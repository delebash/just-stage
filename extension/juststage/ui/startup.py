# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""How JustStage starts (docs/plans/2026-11-03-cc5-window.md §3 step 5), called by the application template: a new
file is a stage - Blender's default cube gone, its camera framing a standing person, its light kept (without them F12
and the lit live view would be black); the Properties editor becomes the Content panel (Blender's Asset Browser); the
3D view's sidebar opens on JustStage's Modify panel. Blender's own settings only:
https://docs.blender.org/api/5.3/bpy.types.Region.html#bpy.types.Region.active_panel_category ("categories are generated
at runtime, so list may be empty at initialization, before any drawing took place" - hence the retries)."""

from __future__ import annotations

import bpy
from mathutils import Vector

CATEGORY = "JustStage"
#: the camera on a new stage: 4.2 m in front at chest height, a 50 mm lens - a whole standing person in frame
CAMERA_AT, CAMERA_LOOKS_AT, LENS = Vector((0.0, -4.2, 1.0)), Vector((0.0, 0.0, 0.92)), 50.0


def new_stage(scene) -> None:
    """Blender's default cube out; its camera aimed at where a JustStage character stands."""
    cube = bpy.data.objects.get("Cube")
    if cube is not None and cube.type == "MESH" and len(cube.data.vertices) == 8:
        bpy.data.objects.remove(cube)
    cam = scene.camera
    if cam is not None:
        cam.location = CAMERA_AT
        cam.rotation_euler = (CAMERA_LOOKS_AT - CAMERA_AT).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = LENS


def content_panel(screens) -> None:
    """Every Properties editor becomes the Content panel: Blender's Asset Browser."""
    for screen in screens:
        for area in screen.areas:
            if area.type == "PROPERTIES":
                area.type = "FILE_BROWSER"
                area.ui_type = "ASSETS"


def open_sidebar(retries: int = 15) -> None:
    """The 3D views' sidebars open, on the JustStage tab, once they have drawn their tabs."""
    left = [retries]

    def attempt():
        done = True
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type != "VIEW_3D":
                    continue
                area.spaces.active.show_region_ui = True
                region = next((r for r in area.regions if r.type == "UI"), None)
                if region is None:
                    continue
                try:
                    region.active_panel_category = CATEGORY
                except TypeError:  # not drawn yet: its tabs don't exist
                    done = False
                area.tag_redraw()
        left[0] -= 1
        return None if done or left[0] <= 0 else 0.2

    bpy.app.timers.register(attempt, first_interval=0.1)
