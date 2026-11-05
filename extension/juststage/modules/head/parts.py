# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The head's parts — GNM's eyes and teeth (with gums and tongue), fitted to the character by MakeHuman's MHCLO
(character-data-model.md §1.1: "Parts are fitted to the body as MakeHuman fits its eyes — by MHCLO"). Made offline by
`libs/wrap/gnm_to_hm08.py` and `tools/bind_parts.py`; names are MetaHuman's (`eyeLeft`, `eyeRight`, `teeth`).
"""

from __future__ import annotations

import json

import bpy
import numpy as np
from mathutils import Matrix

from ... import paths
from ...core import mhclo
from ..body import build
from . import part_materials

TOOL = ".dev/venv-tools/Scripts/python libs/wrap/gnm_to_hm08.py, then tools/bind_parts.py"


def _folder():
    return paths.generated("gnm", "parts", tool=TOOL)


def catalog() -> dict:
    return json.loads((_folder() / "parts.json").read_text(encoding="utf-8"))


def groups(part: str) -> dict[str, list[int]]:
    """A part's named vertex sets (`<part>.groups.json`, by tools/bind_parts.py), e.g. the teeth's
    `lower_teeth_and_gums`."""
    return json.loads((_folder() / f"{part}.groups.json").read_text(encoding="utf-8"))


def _binding(part: str) -> mhclo.Mhclo:
    return mhclo.parse(paths.generated("gnm", "parts", f"{part}.mhclo", tool=TOOL).read_text(encoding="utf-8"))


def parts_of(character: bpy.types.Object) -> dict[str, bpy.types.Object]:
    """The character's fitted head parts (eyes, teeth, ...) - not its grooms, which carry a part too ("scalp") but
    follow the body by their own surface deform."""
    cid = character.juststage.character_id
    fitted = catalog()
    return {o.juststage.part: o for o in bpy.data.objects if o.juststage.part_of == cid and o.juststage.part in fitted}


#: the shape key that keeps the lids' skin in front of the eyeballs (eye_clearance)
CLEARANCE = "JustStage eye clearance"
LID_GAP = 0.0003  # the outer lid skin's least gap over the eyeball


def eye_clearance(character: bpy.types.Object) -> int:
    """The lids' outer skin kept LID_GAP in front of the eyeballs: a shape can push lid skin inside an eye (the face
    test's Walter: 8 vertices an eye up to 0.95 mm in, the white showing through his upper lid - 2026-11-04). Outward-
    facing skin in front of the eye's centre and inside its sphere moves out along the eye's radius, its neighbours
    half as far; in a shape key of its own, made again on every refit. The socket's folded skin (it faces the eye) is
    left alone. Returns how many vertices moved."""
    from ...core.makehuman import BODY_VERTICES
    from . import eye_layers

    keys = character.data.shape_keys
    key = keys.key_blocks.get(CLEARANCE) if keys else None
    if key is not None:
        key.value = 0.0
    skin = build.shaped_coords(character)[:BODY_VERTICES]
    normals = np.empty(len(character.data.vertices) * 3, np.float32)
    character.data.vertex_normals.foreach_get("vector", normals)
    normals = normals.reshape(-1, 3)[:BODY_VERTICES]
    push = np.zeros_like(skin)
    for part, eye in parts_of(character).items():
        if part not in ("eyeLeft", "eyeRight"):
            continue
        centre, radius = eye_layers._eye_sphere(eye)
        rel = skin - centre
        dist = np.linalg.norm(rel, axis=1)
        along = rel / np.maximum(dist, 1e-9)[:, None]
        poke = (dist < radius + LID_GAP) & (dist > radius - 0.006) & (skin[:, 1] < centre[1])
        poke &= np.einsum("ij,ij->i", normals, along) > 0.3
        push[poke] += (radius + LID_GAP - dist[poke])[:, None] * along[poke]
    moved = np.flatnonzero(np.abs(push).sum(axis=1) > 0)
    if not len(moved):
        return 0
    ring = np.zeros_like(push)
    count = np.zeros(len(push))
    edges = np.empty(len(character.data.edges) * 2, np.int32)
    character.data.edges.foreach_get("vertices", edges)
    edges = edges.reshape(-1, 2)
    edges = edges[(edges < BODY_VERTICES).all(axis=1)]
    for a, b in ((edges[:, 0], edges[:, 1]), (edges[:, 1], edges[:, 0])):
        np.add.at(ring, a, push[b])
        np.add.at(count, a, 1.0)
    ring = 0.5 * ring / np.maximum(count, 1.0)[:, None]
    push = np.where(np.abs(push).sum(axis=1, keepdims=True) > 0, push, ring)
    if key is None:
        if not character.data.shape_keys:
            character.shape_key_add(name="Basis", from_mix=False)
        key = character.shape_key_add(name=CLEARANCE, from_mix=False)
    co = np.empty(len(character.data.vertices) * 3, np.float32)
    character.data.shape_keys.reference_key.data.foreach_get("co", co)
    co = co.reshape(-1, 3)
    co[:BODY_VERTICES] += push.astype(np.float32)
    key.data.foreach_set("co", co.ravel())
    key.value = 1.0
    return int(len(moved))


def refit(character: bpy.types.Object) -> None:
    """Move every part to the character's current shape."""
    base = build.shaped_coords(character)
    for part, obj in parts_of(character).items():
        if part == "teeth" and obj.data.shape_keys:  # its jaw units: rebuilt below on the new fit
            obj.shape_key_clear()
        co = mhclo.fit(_binding(part), base).astype(np.float32)
        obj.data.vertices.foreach_set("co", co.ravel())
        obj.data.update()
    from . import eye_layers, face_units

    eye_clearance(character)
    eye_layers.refit(character)  # the occlusion and tearline ride the eyes
    teeth = parts_of(character).get("teeth")
    if teeth is not None:
        face_units.add_to_teeth(character, teeth)


def add(character: bpy.types.Object) -> list[str]:
    """Add the parts the character doesn't have yet, fitted to its shape; returns their names."""
    existing = parts_of(character)
    added = []
    for part, info in catalog().items():
        if part in existing:
            continue
        before = set(bpy.data.objects)
        bpy.ops.wm.obj_import(filepath=str(_folder() / info["obj"]), use_split_objects=False, use_split_groups=False)
        obj = (set(bpy.data.objects) - before).pop()
        obj.matrix_basis = Matrix.Identity(4)  # the fit below gives final positions in Blender's axes
        obj.name = f"{character.name}.{part}"
        obj.data.name = part
        obj.data.shade_smooth()
        obj.parent = character
        obj.juststage.part = part
        obj.juststage.part_of = character.juststage.character_id
        part_materials.assign(obj, part, groups(part))
        added.append(part)
    # the importer's own 90-degree turn stays in each new part's world matrix until the scene updates (the next import
    # updated the one before it, so only a part imported last - an eye added again alone - kept it; 2026-11-04)
    bpy.context.view_layer.update()
    refit(character)
    from . import eyes

    props = character.juststage
    for part in added:
        if part in ("eyeLeft", "eyeRight"):  # the procedural iris and white (MPFB2's), on UVs by the 3D radius
            eye = parts_of(character)[part]
            eyes.shade(eye)
            eyes.set_colour(eye, props.iris_colour, props.iris_accent, props.eye_white)  # the character's own
    if {"eyeLeft", "eyeRight"} & set(added):  # CC5's and MetaHuman's two films over the eyeball
        from . import eye_layers

        eye_layers.add(character)
    return added
