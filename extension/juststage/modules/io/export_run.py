# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.export.run` — a character written for a target by a preset (docs/standards/import-export.md §3: "One
command, `juststage.export.run`, with a preset (`data/presets/<target>.json`)"). First preset: `package`, the USD
character package - Blender's own USD exporter for the meshes, shape keys, armatures, hair curves, materials
(UsdPreviewSurface and MaterialX) and textures; JustStage's fields from core/usd_hooks.py."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str
    folder: str
    preset: str = "package"


class Result(NamedTuple):
    path: str
    objects: int
    files: int


COMMAND = dict(
    id="juststage.export.run",
    label="Export",
    menu="Character > Export",
    permission="files",
    undo=False,
    headless=True,
    since="2026-11-03",
)


def main(params: Params) -> Result:
    import json
    from pathlib import Path

    import bpy

    from ... import character, paths
    from ...core.commands import CommandError

    preset_path = paths.DATA / "presets" / f"{params.preset}.json"
    if not preset_path.exists():
        raise CommandError(f"preset: no preset {params.preset!r}")
    preset = json.loads(preset_path.read_text(encoding="utf-8"))
    if preset["format"] != "usd":
        raise CommandError(f"preset {params.preset!r}: format {preset['format']!r} is not built yet")
    obj = character.find(params.character)
    from ..body import cage

    members = [obj] + [o for o in bpy.data.objects
                       if o.juststage.part_of == obj.juststage.character_id and o.juststage.part != cage.PART]
    folder = Path(params.folder)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / preset["root_layer"]
    view_layer = bpy.context.view_layer
    was_selected = [o for o in view_layer.objects if o.select_get()]
    was_active = view_layer.objects.active
    try:
        for o in was_selected:
            o.select_set(False)
        for o in members:
            o.select_set(True)
        view_layer.objects.active = obj
        bpy.ops.wm.usd_export(filepath=str(target), **preset["usd_export"])
    finally:
        for o in members:
            o.select_set(False)
        for o in was_selected:
            o.select_set(True)
        view_layer.objects.active = was_active
    files = sum(1 for p in folder.rglob("*") if p.is_file())
    return Result(path=str(target), objects=len(members), files=files)
