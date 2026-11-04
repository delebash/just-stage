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


def _binding(part: str) -> mhclo.Mhclo:
    return mhclo.parse(paths.generated("gnm", "parts", f"{part}.mhclo", tool=TOOL).read_text(encoding="utf-8"))


def parts_of(character: bpy.types.Object) -> dict[str, bpy.types.Object]:
    """The character's fitted head parts (eyes, teeth, ...) - not its grooms, which carry a part too ("scalp") but
    follow the body by their own surface deform."""
    cid = character.juststage.character_id
    fitted = catalog()
    return {o.juststage.part: o for o in bpy.data.objects if o.juststage.part_of == cid and o.juststage.part in fitted}


def refit(character: bpy.types.Object) -> None:
    """Move every part to the character's current shape."""
    base = build.shaped_coords(character)
    for part, obj in parts_of(character).items():
        co = mhclo.fit(_binding(part), base).astype(np.float32)
        obj.data.vertices.foreach_set("co", co.ravel())
        obj.data.update()
    from . import eye_layers

    eye_layers.refit(character)  # the occlusion and tearline ride the eyes


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
        groups = json.loads((_folder() / f"{part}.groups.json").read_text(encoding="utf-8"))
        part_materials.assign(obj, part, groups)
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
