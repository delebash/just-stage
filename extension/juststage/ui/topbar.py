# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's top bar while the app template runs: a short, plain set of menus - the user: "the menus dont have to
match exactly just what makes sense, easy and intuitive as blender has a lot of other stuff user may or may not use".
Blender's workspace tabs and its other menus are hidden; Window > "Blender's full interface" brings them back (the
application template "modifying and replacing parts of the user interface" -
https://docs.blender.org/manual/en/5.3/advanced/app_templates.html). Installed by the template, so plain Blender with
the JustStage add-on keeps its own bar."""

from __future__ import annotations

import bpy

#: (menu class, label): Blender's own File, Edit, Render, Window and Help, and JustStage's Character between them
MENUS = (
    ("TOPBAR_MT_file", "File"),
    ("TOPBAR_MT_edit", "Edit"),
    ("TOPBAR_MT_juststage_character", "Character"),
    ("TOPBAR_MT_render", "Render"),
    ("TOPBAR_MT_window", "Window"),
    ("TOPBAR_MT_help", "Help"),
)

_ORIGINAL = {}


def draw_left(self, context):
    if context.window_manager.juststage_full_interface:
        _ORIGINAL["draw_left"](self, context)
        return
    layout = self.layout
    layout.menu("TOPBAR_MT_blender", text="", icon="BLENDER")
    for menu, label in MENUS:
        layout.menu(menu, text=label)


def draw_window_switch(self, context):
    layout = self.layout
    layout.separator()
    layout.prop(context.window_manager, "juststage_full_interface", text="Blender's full interface")


def install() -> None:
    if "draw_left" in _ORIGINAL:
        return
    bpy.types.WindowManager.juststage_full_interface = bpy.props.BoolProperty(
        name="Blender's full interface", description="Show Blender's workspace tabs and all of its menus", default=False
    )
    _ORIGINAL["draw_left"] = bpy.types.TOPBAR_HT_upper_bar.draw_left
    bpy.types.TOPBAR_HT_upper_bar.draw_left = draw_left
    bpy.types.TOPBAR_MT_window.append(draw_window_switch)


def uninstall() -> None:
    if "draw_left" not in _ORIGINAL:
        return
    bpy.types.TOPBAR_MT_window.remove(draw_window_switch)
    bpy.types.TOPBAR_HT_upper_bar.draw_left = _ORIGINAL.pop("draw_left")
    del bpy.types.WindowManager.juststage_full_interface
