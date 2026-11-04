# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's top bar (docs/plans/2026-11-03-cc5-window.md §3 step 3): a short, plain menu set while the app template
runs - Blender's workspace tabs and extra menus hidden, its full interface one switch away (Window menu)."""

import importlib

import bpy
from mathutils import Vector

topbar = importlib.import_module("bl_ext.system.juststage.ui.topbar")


def test_install_swaps_the_top_bar_and_uninstall_restores_it():
    original = bpy.types.TOPBAR_HT_upper_bar.draw_left
    topbar.install()
    try:
        assert bpy.types.TOPBAR_HT_upper_bar.draw_left is topbar.draw_left
        assert hasattr(bpy.types.WindowManager, "juststage_full_interface")
        assert topbar.draw_window_switch in bpy.types.TOPBAR_MT_window._dyn_ui_initialize()
    finally:
        topbar.uninstall()
    assert bpy.types.TOPBAR_HT_upper_bar.draw_left is original


def test_the_menus_are_few_and_plain():
    assert [label for _menu, label in topbar.MENUS] == ["File", "Edit", "Character", "Render", "Window", "Help"]
    for menu, _label in topbar.MENUS:
        assert hasattr(bpy.types, menu), menu


startup = importlib.import_module("bl_ext.system.juststage.ui.startup")


def test_a_new_file_is_a_stage():
    scene = bpy.context.scene
    if "Cube" not in bpy.data.objects:  # Blender's factory start has it; an earlier test may have removed it
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.active_object.name = "Cube"
    startup.new_stage(scene)
    assert "Cube" not in bpy.data.objects
    assert scene.camera is not None and scene.camera.data.lens == startup.LENS
    lights = {o.name: o for o in scene.objects if o.type == "LIGHT"}
    # three-point studio lighting in front of the character (Blender's one light stood behind it: the face was dark)
    assert {"Key light", "Fill light", "Rim light"} <= set(lights) and "Light" not in lights
    assert lights["Key light"].location.y < 0 and lights["Fill light"].location.y < 0  # in front (it faces -Y)
    assert lights["Rim light"].location.y > 0
    assert lights["Key light"].data.energy > lights["Fill light"].data.energy
    for name in ("Key light", "Fill light", "Rim light"):  # fine jittered shadows: the lid's on the eye white
        assert lights[name].data.use_shadow_jitter and lights[name].data.shadow_maximum_resolution <= 0.0001
    for light in lights.values():  # each aimed at the head and chest
        aim = light.rotation_euler.to_quaternion() @ Vector((0.0, 0.0, -1.0))
        to_body = (Vector((0.0, 0.0, 1.35)) - light.location).normalized()
        assert aim.dot(to_body) > 0.99, light.name


def test_the_stage_view_hides_the_lights_outlines():
    screen = bpy.data.screens["Layout"]
    startup.stage_view([screen])
    views = [a.spaces.active for a in screen.areas if a.type == "VIEW_3D"]
    assert views and not any(v.overlay.show_extras for v in views)


def test_the_properties_editor_becomes_the_content_panel():
    screen = bpy.data.screens["Layout"]
    startup.content_panel([screen])
    assert not [a for a in screen.areas if a.type == "PROPERTIES"]
    assert [a for a in screen.areas if a.type == "FILE_BROWSER" and a.ui_type == "ASSETS"]
