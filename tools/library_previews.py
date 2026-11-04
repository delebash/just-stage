# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Thumbnails for the library's character assets (docs/standards/project-files.md §2: "preview >= 256 px"): each
asset file opened, its character rendered head and shoulders in EEVEE at 256 px on the card, the picture loaded as the
asset's custom preview (Blender's `ed.lib_id_load_custom_preview`), the file saved. Needs the card - ask for it first.

    python tools/dev.py blender -b --python tools/library_previews.py
"""

import importlib

import addon_utils
import bpy
from mathutils import Vector

addon_utils.enable("bl_ext.system.juststage", default_set=True)
library = importlib.import_module("bl_ext.system.juststage.core.library")
SIZE = 256

for path in sorted((library.root() / "Characters").glob("*.blend")):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    asset = next(o for o in bpy.data.objects if o.asset_data is not None)
    scene = bpy.context.scene
    if scene.objects.get(asset.name) is None:
        scene.collection.objects.link(asset)
    for o in bpy.data.objects:
        if o.juststage.part_of == asset.juststage.character_id and scene.objects.get(o.name) is None:
            scene.collection.objects.link(o)
    top = max((asset.matrix_world @ Vector(c)).z for c in asset.bound_box)
    look = Vector((0.0, 0.0, top - 0.22))
    cam = bpy.data.objects.new("preview camera", bpy.data.cameras.new("preview camera"))
    scene.collection.objects.link(cam)
    cam.location = look + Vector((0.0, -1.15, 0.05))
    cam.rotation_euler = (look - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 60.0
    sun = bpy.data.objects.new("preview light", bpy.data.lights.new("preview light", "AREA"))
    sun.data.energy, sun.data.size = 120.0, 1.5
    sun.location = look + Vector((-0.8, -1.2, 0.8))
    sun.rotation_euler = (look - sun.location).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun)
    scene.camera = cam
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = SIZE
    scene.render.film_transparent = True
    out = library.root().parent / "previews" / f"{path.stem}.png"  # beside the library (never the system temp on C:)
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    with bpy.context.temp_override(id=asset):
        bpy.ops.ed.lib_id_load_custom_preview(filepath=str(out))
    for helper in (cam, sun):
        bpy.data.objects.remove(helper)
    bpy.ops.wm.save_mainfile()
    print("PREVIEW", path.name, flush=True)
