# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The UI door's menus (commands-and-api.md §3: "panels, menus and keymaps call the operator"): the top bar's
Character menu built from every command's `menu` path, and a command opened from it working on the selected
character."""

import importlib

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
menus = importlib.import_module("bl_ext.system.juststage.ui.menus")
command_operator = importlib.import_module("bl_ext.system.juststage.ui.command_operator")


def test_every_character_command_is_in_the_menu():
    groups = menus.menu_groups("Character")
    listed = {cmd.id for _group, cmds in groups for cmd in cmds}
    wanted = {c.id for c in api.commands() if c.record.get("menu", "").split(" > ")[0] == "Character"}
    assert listed == wanted and wanted
    names = [group for group, _ in groups]
    assert names[0] == "New human"  # the first thing to do comes first
    assert {"Body", "Head", "Skin", "Hair", "Export"} <= set(names)


def test_the_menu_is_in_the_top_bar():
    assert hasattr(bpy.types, menus.TOPBAR_MT_juststage_character.__name__)
    assert menus.draw_topbar in bpy.types.TOPBAR_MT_editor_menus._dyn_ui_initialize()


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Menu test")
    yield result, bpy.data.objects[result.object]
    for obj in list(bpy.data.objects):
        if obj.juststage.part_of == result.character or obj.name == result.object:
            bpy.data.objects.remove(obj)


def test_a_command_works_on_the_selected_character_or_its_part(human):
    result, obj = human
    assert command_operator.character_of(obj) == result.character
    api.run("juststage.head.add_parts", character=result.character)
    part = next(o for o in bpy.data.objects if o.juststage.part_of == result.character)
    assert command_operator.character_of(part) == result.character
    assert command_operator.character_of(None) == ""
