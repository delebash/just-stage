# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body rig's deciding test (the plan's §18a row 17, a LOCAL TEST in the gate): MPFB2's CC0 game-engine skeleton
(`rig.game_engine.json`, 53 bones) and its weights (`weights.game_engine.json`) on our character, the way MPFB2's
rig service places them (https://github.com/makehumancommunity/mpfb2, `src/mpfb/services/rigservice.py` at the
fetched commit: each joint the mean of its MakeHuman joint cube's vertices on the shaped body - the `CUBE` strategy -
or of listed vertices - `MEAN`; each bone's roll and parent from the file; the weights as vertex groups and an
Armature modifier first in the stack). Base v2's appended lid vertices, which hm08's weights don't list, take their
nearest hm08 vertex's weights. Then both men posed alike - each bone turned in world space from its own rest - for
the gate's posed views (`parts_gate.POSES`): do our mesh and weights pose like CC5's HD Aaron, as exported to Blender
(his 90 deform bones with twist and share bones, no body correctives)? The plan's skeleton (§7 "Skeleton": the 82 of
UE5 plus breasts) and its correctives (body.dna) are Q-RIG-6 / Q-RIG-7; this is the base they build on."""

from __future__ import annotations

import importlib
import json

import bpy
import numpy as np
from mathutils import Matrix, Vector

RIG, WEIGHTS = "rig.game_engine.json", "weights.game_engine.json"
NAME = "JustStage gate rig"
#: the gate's bone roles in each rig (ours MPFB2's game-engine names, his CC5's) - the right side, as the gate's views
ROLES = {
    "ours": {"upperarm": "upperarm_r", "lowerarm": "lowerarm_r", "hand": "hand_r", "thigh": "thigh_r",
             "calf": "calf_r", "foot": "foot_r", "spine": "spine_02"},
    "cc5": {"upperarm": "CC_Base_R_Upperarm", "lowerarm": "CC_Base_R_Forearm", "hand": "CC_Base_R_Hand",
            "thigh": "CC_Base_R_Thigh", "calf": "CC_Base_R_Calf", "foot": "CC_Base_R_Foot", "spine": "CC_Base_Spine02"},
}  # fmt: skip
#: a limb's direction is joint to joint - its bone's head to the next joint's: a CC5 bone's tail, set on FBX import by
#: convention, doesn't lie along the limb (aimed by head-to-tail, his forearm, calf and thigh barely turned,
#: 2026-11-08); MPFB2's tails sit on the next joint, so ours is unchanged
NEXT = {"upperarm": "lowerarm", "lowerarm": "hand", "thigh": "calf", "calf": "foot"}


def _ext(name: str):
    return importlib.import_module(f"bl_ext.system.juststage.{name}")


def build(body: bpy.types.Object) -> bpy.types.Object:
    """The game-engine rig on `body`'s current shape, its weights bound; returns the armature object."""
    paths, makehuman = _ext("paths"), _ext("core.makehuman")
    build_mod = _ext("modules.body.build")
    rig = json.loads(paths.makehuman("rigs", "standard", RIG).read_text())
    weights = json.loads(paths.makehuman("rigs", "standard", WEIGHTS).read_text())["weights"]
    groups = makehuman.vertex_groups(paths.makehuman("mesh_metadata", "basemesh_vertex_groups.json"))
    co = build_mod.shaped_coords(body)  # the body's own space

    def joint(spec: dict) -> Vector:
        if spec["strategy"] == "CUBE":
            return Vector(co[list(groups[spec["cube_name"]])].mean(0))
        if spec["strategy"] == "MEAN":
            return Vector(co[spec["vertex_indices"]].mean(0))
        raise ValueError(f"joint strategy {spec['strategy']} not handled")

    data = bpy.data.armatures.new(NAME)
    arm = bpy.data.objects.new(NAME, data)
    bpy.context.scene.collection.objects.link(arm)
    arm.matrix_world = body.matrix_world.copy()
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for name, spec in rig.items():
        eb = data.edit_bones.new(name)
        eb.head, eb.tail = joint(spec["head"]), joint(spec["tail"])
        eb.roll = spec["roll"]
    for name, spec in rig.items():
        eb = data.edit_bones[name]
        if spec["parent"]:
            eb.parent = data.edit_bones[spec["parent"]]
            eb.use_connect = bool(spec.get("use_connect", False))
        eb.use_inherit_rotation = spec.get("use_inherit_rotation", True)
        eb.use_local_location = spec.get("use_local_location", True)
    bpy.ops.object.mode_set(mode="OBJECT")
    for name in rig:
        data.bones[name].inherit_scale = rig[name].get("inherit_scale", "FULL")
    # the weights: hm08's vertices from the file, base v2's appended ones from their nearest hm08 vertex
    n, hm = len(body.data.vertices), makehuman.HM08_VERTICES
    table = np.zeros((n, len(rig)), np.float32)
    names = list(rig)
    for j, name in enumerate(names):
        for i, w in weights.get(name, []):
            if i < hm:
                table[i, j] = w
    if n > hm:
        from mathutils.kdtree import KDTree

        kd = KDTree(hm)
        for i in range(hm):
            kd.insert(co[i], i)
        kd.balance()
        for i in range(hm, n):
            table[i] = table[kd.find(co[i])[1]]
    for j, name in enumerate(names):
        vg = body.vertex_groups.get(name) or body.vertex_groups.new(name=name)
        hit = np.flatnonzero(table[:, j] > 0)
        for w in np.unique(table[hit, j]):  # one call per distinct weight
            vg.add(hit[table[hit, j] == w].tolist(), float(w), "REPLACE")
    mod = body.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    body.modifiers.move(len(body.modifiers) - 1, 0)  # first: the mask and the rest act on the posed body
    for part in [o for o in bpy.context.scene.objects if o.juststage.part_of == body.juststage.character_id
                 and o.type == "MESH"]:  # the eyes, teeth and tongue ride the head
        world = part.matrix_world.copy()
        part.parent, part.parent_type, part.parent_bone = arm, "BONE", "head"
        part.matrix_world = world
    bpy.context.view_layer.update()
    total = table[:hm].sum(1)
    print(f"BODY RIG: {len(rig)} bones; weights per vertex sum p1 {np.percentile(total, 1):.3f} / median "
          f"{np.median(total):.3f}; {n - hm} appended vertices given their nearest's", flush=True)
    return arm


def rest(arm: bpy.types.Object) -> None:
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


def turn(arm: bpy.types.Object, bone: str, axis, degrees: float) -> None:
    """`bone` turned `degrees` about a world `axis` through its head (its children follow)."""
    pb = arm.pose.bones[bone]
    to_arm = arm.matrix_world.inverted()
    head = pb.head.copy()  # armature space
    a = (to_arm.to_3x3() @ Vector(axis)).normalized()
    r = Matrix.Translation(head) @ Matrix.Rotation(np.radians(degrees), 4, a) @ Matrix.Translation(-head)
    pb.matrix = r @ pb.matrix
    bpy.context.view_layer.update()


def direction(arm: bpy.types.Object, bone: str) -> np.ndarray:
    """A posed bone's world direction, head to tail."""
    pb = arm.pose.bones[bone]
    d = arm.matrix_world.to_3x3() @ (pb.tail - pb.head)
    return np.array(d.normalized())


def limb(arm: bpy.types.Object, roles: dict, role: str) -> np.ndarray:
    """A posed limb's world direction, joint to joint (`NEXT`); a role with no next joint, its bone's head to tail."""
    if role not in NEXT:
        return direction(arm, roles[role])
    d = np.array(joint(arm, roles[NEXT[role]]) - joint(arm, roles[role]))
    return d / np.linalg.norm(d)


def joint(arm: bpy.types.Object, bone: str) -> Vector:
    """A posed bone's head in world space."""
    return arm.matrix_world @ arm.pose.bones[bone].head
