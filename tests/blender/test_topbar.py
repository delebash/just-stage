# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's top bar (docs/plans/2026-11-03-cc5-window.md §3 step 3): a short, plain menu set while the app template
runs - Blender's workspace tabs and extra menus hidden, its full interface one switch away (Window menu)."""

import importlib

import bpy

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
    assert any(o.type == "LIGHT" for o in scene.objects)  # kept: F12 and the lit live view need it


def test_the_properties_editor_becomes_the_content_panel():
    screen = bpy.data.screens["Layout"]
    startup.content_panel([screen])
    assert not [a for a in screen.areas if a.type == "PROPERTIES"]
    assert [a for a in screen.areas if a.type == "FILE_BROWSER" and a.ui_type == "ASSETS"]
