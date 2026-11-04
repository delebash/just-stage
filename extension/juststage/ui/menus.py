# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The top bar's Character menu, built from the commands' `menu` paths at draw time (commands-and-api.md §1: the
registry's "id, label, menu path" - PhotoCraft's shape; §3: menus call the operator), so a plugin's commands appear
beside ours. Blender's own menu API: https://docs.blender.org/api/5.3/bpy.types.Menu.html."""

from __future__ import annotations

import bpy

from .. import api

#: groups in the order a character is made (New human first); a plugin's new group goes after them
ORDER = ("New human", "Body", "Head", "Skin", "Hair", "Clothes", "Rig", "Export")


def menu_groups(top: str) -> list[tuple[str, list]]:
    """The commands under `top` ("Character > Head" → group "Head"), grouped and ordered."""
    groups: dict[str, list] = {}
    for cmd in api.commands():
        path = [p.strip() for p in cmd.record.get("menu", "").split(">")]
        if path[0] != top:
            continue
        groups.setdefault(path[1] if len(path) > 1 else cmd.label, []).append(cmd)

    def rank(name):
        return (ORDER.index(name), "") if name in ORDER else (len(ORDER), name)

    return [(name, sorted(groups[name], key=lambda c: c.label)) for name in sorted(groups, key=rank)]


class TOPBAR_MT_juststage_character(bpy.types.Menu):
    """Make and change a character"""

    bl_idname = "TOPBAR_MT_juststage_character"
    bl_label = "Character"

    def draw(self, context):
        layout = self.layout
        for i, (group, cmds) in enumerate(menu_groups("Character")):
            if i:
                layout.separator()
            if len(cmds) > 1 or cmds[0].label != group:
                layout.label(text=group)
            for cmd in cmds:
                layout.operator(cmd.operator_idname, text=cmd.label)


def draw_topbar(self, context):
    self.layout.menu(TOPBAR_MT_juststage_character.bl_idname)


CLASSES = (TOPBAR_MT_juststage_character,)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_topbar)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_topbar)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
