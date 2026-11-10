# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The women's torso relief's donor (the plan's Q-BODY-3: "First Blender Studio's CC0 `realistic_body_female` ...
looked at in Blender" - 2026-11-10: its top Multires level carries the sternum, the rib cage's hints, the navel and
the abdomen's soft forms; its base level none): Blender Studio's Human Base Meshes bundle (CC0) -
`GEO-body_female_realistic` - evaluated at its top Multires level and written as an OBJ (metres, Z up) for
`tools/body_scan.py bs_female` to fit and bake as it does Artec's torso for the men.

    python tools/dev.py blender -b --factory-startup --python tools/export_bs_female.py

Writes `.dev/facetest/body/bs_female/bs_female_top.obj`."""

from __future__ import annotations

from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = (ROOT / ".dev" / "downloads" / "blender_human_base_meshes" / "x" / "human-base-meshes-bundle-v1.4.1"
          / "human_base_meshes_bundle.blend")  # fmt: skip
NAME = "GEO-body_female_realistic"
OUT = ROOT / ".dev" / "facetest" / "body" / "bs_female" / "bs_female_top.obj"


def main() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(BUNDLE), link=False) as (src, dst):
        dst.objects = [NAME]
    body = dst.objects[0]
    bpy.context.scene.collection.objects.link(body)
    for mod in body.modifiers:
        if mod.type == "MULTIRES":
            mod.levels = mod.render_levels = mod.sculpt_levels = mod.total_levels
        else:
            mod.show_viewport = mod.show_render = False  # the sculpt alone (no armature or other deform)
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.obj_export(filepath=str(OUT), export_selected_objects=True, apply_modifiers=True,
                          export_uv=False, export_normals=False, export_materials=False,
                          forward_axis="Y", up_axis="Z")  # fmt: skip
    print(f"wrote {OUT}: {NAME} at Multires level {max(m.total_levels for m in body.modifiers if m.type == 'MULTIRES')}")


main()
