# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Thumbnails for the library's assets (docs/standards/project-files.md §2: "preview >= 256 px"). Each asset is shown
in a fresh scene through `juststage.library.add`, as the Content panel applies it: a character by itself; a groom on
the Average woman (the Average man for beards and moustaches); a skin on the Average woman's face. It is rendered in
EEVEE at 256 px on the card, and the picture is loaded as the asset's custom preview in its own file
(`ed.lib_id_load_custom_preview`), which is saved. Sections after `--`: characters hair skins (all when none). Needs the
card - ask for it first.

    python tools/dev.py blender -b --python tools/library_previews.py -- hair skins
"""

import importlib
import sys

import addon_utils
import bpy
from mathutils import Vector

addon_utils.enable("bl_ext.system.juststage", default_set=True)
api = importlib.import_module("bl_ext.system.juststage.api")
library = importlib.import_module("bl_ext.system.juststage.core.library")
viewport = importlib.import_module("bl_ext.system.juststage.core.viewport")
SIZE = 256
WANTED = set(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else ()) or {"characters", "hair", "skins"}

#: what is shown → (height of the look point from the eyes, the camera's offset from it, lens mm); a character's
#: framing is the head and shoulders, hair and skin closer
FRAMES = {
    "Characters": (-0.1, (0.0, -1.15, 0.05), 60.0),
    "Hair/Scalp": (-0.07, (-0.38, -0.59, 0.07), 60.0),  # three-quarter, head and neck: a ponytail's tail shows
    "Hair/Brows": (0.025, (0.0, -0.40, 0.0), 80.0),
    "Hair/Lashes": (0.0, (-0.05, -0.13, 0.015), 100.0),  # one eye, from a little to its side
    "Hair/Beards": (-0.08, (-0.2, -0.51, 0.0), 70.0),
    "Skins": (-0.03, (0.0, -0.55, 0.0), 70.0),
}
SECTIONS = {"characters": ("Characters",), "hair": ("Hair/Scalp", "Hair/Brows", "Hair/Lashes", "Hair/Beards"),
            "skins": ("Skins",)}  # fmt: skip


def _model(catalog: str) -> str:
    """The library character an asset is shown on."""
    man = catalog == "Hair/Beards"
    return str(library.root() / "Characters" / ("Average man.blend" if man else "Average woman.blend"))


def _eye_centres(character: str) -> list[Vector]:
    """The character's eyeballs' centres (its head parts `eyeLeft`, `eyeRight` - by part, not by name: a brow groom's
    name holds "eye" too), lowest x first."""
    eyes = [o for o in bpy.data.objects if o.juststage.part_of == character and o.juststage.part.startswith("eye")]
    eyes = [o for o in eyes if o.juststage.part in ("eyeLeft", "eyeRight")]
    centres = [o.matrix_world @ (sum((Vector(c) for c in o.bound_box), Vector()) / 8) for o in eyes]
    return sorted(centres, key=lambda c: c.x)


def render(catalog: str, path: str, out) -> None:
    bpy.ops.wm.read_homefile(use_empty=True)
    scene = bpy.context.scene
    viewport.setup_scene(scene)
    if catalog == "Characters":
        shown = api.run("juststage.library.add", path=path)
    else:
        shown = api.run("juststage.library.add", path=_model(catalog))
        api.run("juststage.library.add", path=path, character=shown.character)
    centres = _eye_centres(shown.character)
    # lashes: the eye on the camera's side; everything else: between the eyes
    eye = centres[0] if catalog == "Hair/Lashes" else sum(centres, Vector()) / len(centres)
    rise, offset, lens = FRAMES[catalog]
    # a character's look point at the body's middle line (its framing as before); closer views at the eyes' depth
    look = Vector((eye.x if catalog == "Hair/Lashes" else 0.0, 0.0 if catalog == "Characters" else eye.y, eye.z + rise))
    cam = bpy.data.objects.new("preview camera", bpy.data.cameras.new("preview camera"))
    scene.collection.objects.link(cam)
    cam.location = look + Vector(offset)
    cam.rotation_euler = (look - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    cam.data.clip_start = 0.01  # the lashes' camera is 14 cm from the eye (Blender's 10 cm start cut the face away)
    light = bpy.data.objects.new("preview light", bpy.data.lights.new("preview light", "AREA"))
    # high and to the side, and small: a large light beside the camera filled the corneas (white eyes)
    light.data.energy, light.data.size = 120.0, 0.6
    importlib.import_module("bl_ext.system.juststage.ui.startup").set_fine_shadows(light.data)  # the lids' shadow
    light.location = look + Vector((-0.9, -1.0, 1.1))
    light.rotation_euler = (look - light.location).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(light)
    scene.camera = cam
    scene.render.engine = "BLENDER_EEVEE"
    # lashes are a third of a pixel wide at 256 px: rendered at 1024 and shrunk by Blender, they average into a line
    scene.render.resolution_x = scene.render.resolution_y = SIZE * (4 if catalog == "Hair/Lashes" else 1)
    scene.render.film_transparent = True
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)


def set_preview(path: str, picture) -> None:
    bpy.ops.wm.open_mainfile(filepath=path)
    asset = next(i for i in (*bpy.data.objects, *bpy.data.materials) if i.asset_data is not None)
    with bpy.context.temp_override(id=asset):
        bpy.ops.ed.lib_id_load_custom_preview(filepath=str(picture))
    bpy.context.preferences.filepaths.save_version = 0  # no .blend1 beside each asset
    bpy.ops.wm.save_mainfile()


for section in sorted(WANTED & set(SECTIONS)):
    for catalog in SECTIONS[section]:
        for asset in sorted((library.root() / catalog).glob("*.blend")):
            out = library.root().parent / "previews" / catalog / f"{asset.stem}.png"  # never the system temp on C:
            render(catalog, str(asset), out)
            set_preview(str(asset), out)
            print("PREVIEW", catalog, asset.name, flush=True)
