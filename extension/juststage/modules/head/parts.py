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
    cid = character.juststage.character_id
    return {o.juststage.part: o for o in bpy.data.objects if o.juststage.part_of == cid and o.juststage.part}


def refit(character: bpy.types.Object) -> None:
    """Move every part to the character's current shape."""
    base = build.shaped_coords(character)
    for part, obj in parts_of(character).items():
        co = mhclo.fit(_binding(part), base).astype(np.float32)
        obj.data.vertices.foreach_set("co", co.ravel())
        obj.data.update()


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
    refit(character)
    return added
