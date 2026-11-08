# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body skeleton on a character (`docs/standards/skeleton-and-face.md` §1, `character-data-model.md` §2
"Skeleton" and "Skin weights"): the UE5 skeleton by its own names - Manny's 80 deform bones and `breast_l/r` - from
`data/generated/rigs/ue5.json` and `weights.ue5.json` (`tools/make_skeleton.py`, from MPFB2's CC0 rigs and
weights). Placed the way MPFB2's rig service places a rig (https://github.com/makehumancommunity/mpfb2,
`entities/rig.py` at the fetched commit: each joint the mean of its joint cube's vertices - `CUBE` - or of listed
vertices - `MEAN` - on the shaped body; roll, parent and flags from the file), again after every shape change
(`refit`), so the skeleton follows the sliders. Deform bones in the `DEF` bone collection; the weights as vertex
groups named after the bones, base v2's appended lid vertices taking their nearest body vertex's; an Armature
modifier first in the body's stack (linear blend skinning, as Unreal's). The armature is a part of the character -
a child of the body, as its other parts are (the body is the character's object: the panels, the library and the
grooms all hang on it). The head's rigid parts (eyes, teeth, their films) ride the `head` bone through an Armature
modifier of their own, all their vertices weighted to it - skinned to the skeleton, as a game engine takes them.
The twist bones have no constraints: twist-swing is `rig/body.dna`'s layer (the data model §2, "never hand-made
drivers")."""

from __future__ import annotations

import json
from functools import cache

import bpy
import numpy as np
from mathutils import Matrix, Vector

PART = "skeleton"
COLLECTION = "DEF"  # skeleton-and-face.md §1.1: "every deform bone is in the `DEF` bone collection"
MODIFIER = "JustStage skeleton"
HEAD = "head"  # the bone the head's rigid parts ride
TOOL = "tools/make_skeleton.py"
#: a part deformed by the body's own surface (a groom, a garment) follows the body, not the head bone
FOLLOWS_BODY = {"SURFACE_DEFORM", "MESH_DEFORM", "SHRINKWRAP"}


@cache
def definition() -> dict:
    from ... import paths

    return json.loads(paths.generated("rigs", "ue5.json", tool=TOOL).read_text(encoding="utf-8"))


@cache
def _weights() -> dict:
    from ... import paths

    return json.loads(paths.generated("rigs", "weights.ue5.json", tool=TOOL).read_text(encoding="utf-8"))["weights"]


def skeleton_of(character: bpy.types.Object) -> bpy.types.Object | None:
    cid = character.juststage.character_id
    return next((o for o in bpy.data.objects if o.type == "ARMATURE" and o.juststage.part_of == cid
                 and o.juststage.part == PART), None)  # fmt: skip


def add(character: bpy.types.Object) -> bpy.types.Object:
    """The skeleton on `character`'s current shape, its weights bound and the head's parts riding it; again on a
    character that has one (placed and bound afresh). Returns the armature object."""
    arm = skeleton_of(character)
    if arm is None:
        data = bpy.data.armatures.new(PART)
        arm = bpy.data.objects.new(f"{character.name}.{PART}", data)
        for collection in character.users_collection:
            collection.objects.link(arm)
        arm.parent = character
        arm.matrix_parent_inverse = Matrix.Identity(4)  # the armature's space is the body's
        arm.juststage.part = PART
        arm.juststage.part_of = character.juststage.character_id
    place(character, arm)
    bind(character, arm)
    attach(character, arm)
    return arm


def refit(character: bpy.types.Object) -> None:
    """After a shape change: the joints on the new shape and the head's parts riding the head bone (a part added
    since). Nothing without a skeleton."""
    arm = skeleton_of(character)
    if arm is not None:
        place(character, arm)
        attach(character, arm)


def joints(character: bpy.types.Object) -> dict[str, tuple[Vector, Vector]]:
    """Each bone's (head, tail) on the character's shaped body, in its own space (MPFB2's strategies)."""
    from ... import paths
    from ..body import build

    co = build.shaped_coords(character)
    groups = _cubes(str(paths.makehuman("mesh_metadata", "basemesh_vertex_groups.json")))

    def at(spec: dict) -> Vector:
        if spec["strategy"] == "CUBE":
            return Vector(co[groups[spec["cube_name"]]].mean(0))
        if spec["strategy"] == "MEAN":
            return Vector(co[spec["vertex_indices"]].mean(0))
        if spec["strategy"] == "VERTEX":
            return Vector(co[spec["vertex_index"]])
        raise ValueError(f"joint strategy {spec['strategy']} not handled")

    return {name: (at(spec["head"]), at(spec["tail"])) for name, spec in definition().items()}


@cache
def _cubes(path: str) -> dict[str, list[int]]:
    from pathlib import Path

    from ...core import makehuman

    return makehuman.vertex_groups(Path(path))


def place(character: bpy.types.Object, arm: bpy.types.Object) -> None:
    """The bones on the character's current shape - MPFB2's placement, in edit mode (Blender's only door to a
    bone's rest)."""
    rig = definition()
    where = joints(character)
    data = arm.data
    view_layer = bpy.context.view_layer
    active = view_layer.objects.active
    if active is not None and active.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    hidden = arm.hide_get()
    arm.hide_set(False)
    view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    try:
        bones = data.edit_bones
        for name, spec in rig.items():
            eb = bones.get(name) or bones.new(name)
            eb.head, eb.tail = where[name]
            eb.roll = spec["roll"]
        for name, spec in rig.items():
            eb = bones[name]
            eb.parent = bones[spec["parent"]] if spec["parent"] else None
            eb.use_connect = bool(spec.get("use_connect", False))
            eb.use_inherit_rotation = spec.get("use_inherit_rotation", True)
            eb.use_local_location = spec.get("use_local_location", True)
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")
        view_layer.objects.active = active
        arm.hide_set(hidden)
    collection = data.collections.get(COLLECTION) or data.collections.new(COLLECTION)
    for name, spec in rig.items():
        bone = data.bones[name]
        bone.inherit_scale = spec.get("inherit_scale", "FULL")
        bone.use_deform = True
        collection.assign(bone)


def bind(character: bpy.types.Object, arm: bpy.types.Object) -> int:
    """The weights as vertex groups (replacing any of the bones' names) and the Armature modifier first in the
    stack; returns the vertices weighted."""
    from ...core import makehuman
    from ..body import build

    rig = definition()
    weights = _weights()
    names = list(rig)
    n, hm = len(character.data.vertices), makehuman.HM08_VERTICES
    table = np.zeros((n, len(names)), np.float32)
    for j, name in enumerate(names):
        rows = np.asarray(weights.get(name, []), dtype=np.float64).reshape(-1, 2)
        index = rows[:, 0].astype(np.int64)
        keep = index < min(n, hm)
        table[index[keep], j] = rows[keep, 1]
    if n > hm:  # base v2's appended lid vertices: their nearest body vertex's weights
        from mathutils.kdtree import KDTree

        co = build.shaped_coords(character)
        body = makehuman.BODY_VERTICES
        kd = KDTree(body)
        for i in range(body):
            kd.insert(co[i], i)
        kd.balance()
        for i in range(hm, n):
            table[i] = table[kd.find(co[i])[1]]
    for name in names:
        old = character.vertex_groups.get(name)
        if old is not None:
            character.vertex_groups.remove(old)
    for j, name in enumerate(names):
        hit = np.flatnonzero(table[:, j] > 0)
        if not len(hit):
            continue
        vg = character.vertex_groups.new(name=name)
        for w in np.unique(table[hit, j]):  # one call per distinct weight
            vg.add(hit[table[hit, j] == w].tolist(), float(w), "REPLACE")
    _modifier(character, arm)
    return int((table.sum(1) > 0).sum())


def _modifier(obj: bpy.types.Object, arm: bpy.types.Object) -> None:
    mod = obj.modifiers.get(MODIFIER) or obj.modifiers.new(MODIFIER, "ARMATURE")
    mod.object = arm
    mod.use_vertex_groups = True
    mod.use_bone_envelopes = False
    mod.use_deform_preserve_volume = False  # linear blend skinning, as Unreal deforms
    if obj.modifiers.find(MODIFIER) != 0:  # first: the levels, the mask and the rest act on the posed body
        obj.modifiers.move(obj.modifiers.find(MODIFIER), 0)


def riders(character: bpy.types.Object) -> list[bpy.types.Object]:
    """The character's rigid mesh parts - the eyes, teeth and their films; not a groom or anything bound to the
    body's surface."""
    cid = character.juststage.character_id
    return [o for o in bpy.data.objects if o.type == "MESH" and o.juststage.part_of == cid
            and not any(m.type in FOLLOWS_BODY for m in o.modifiers)]  # fmt: skip


def attach(character: bpy.types.Object, arm: bpy.types.Object) -> list[str]:
    """Each rigid part skinned whole to the `head` bone; returns their names."""
    done = []
    for part in riders(character):
        vg = part.vertex_groups.get(HEAD) or part.vertex_groups.new(name=HEAD)
        vg.add(list(range(len(part.data.vertices))), 1.0, "REPLACE")
        _modifier(part, arm)
        done.append(part.name)
    return done
