# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Character panel (the 3D view's sidebar, JustStage tab): the selected character's body sliders - dragging one
runs `juststage.body.set_slider` (character.py `_slider`) - and its make-and-change commands, the Character menu's
(ui/menus.py) in a panel. Blender's panel API: https://docs.blender.org/api/5.3/bpy.types.Panel.html."""

from __future__ import annotations

import bpy

from ..modules.body import sliders
from .command_operator import character_of
from .menus import menu_groups

BODY = ("gender", "age", "muscle", "weight", "proportions", "height", "cupsize", "firmness")
RACES = ("asian", "caucasian", "african")


def active_character(context):
    """The character the selection belongs to - the body itself or one of its parts - or None."""
    character_id = character_of(context.active_object)
    if not character_id:
        return None
    return next((o for o in bpy.data.objects if o.juststage.character_id == character_id), None)


class VIEW3D_PT_juststage_character(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "JustStage"
    bl_label = "Character"

    def draw(self, context):
        layout = self.layout
        obj = active_character(context)
        if obj is None:
            layout.label(text="Select a character, or make one:")
            layout.operator("juststage.body_create", text="New human", icon="ADD")
            return
        layout.label(text=obj.name, icon="OUTLINER_OB_ARMATURE")
        body = layout.column(align=True)
        body.label(text="Body")
        for name in BODY:
            body.prop(obj.juststage, name, slider=True)
        mix = layout.column(align=True)
        mix.label(text="Ethnic mix")
        for name in RACES:
            mix.prop(obj.juststage, name, slider=True)
        detail = layout.column(align=True)
        detail.label(text="Details")
        wm = context.window_manager
        detail.prop(wm, "juststage_slider_group", text="")
        for item in obj.juststage.sliders:
            if item.group == wm.juststage_slider_group:
                detail.prop(item, "value", text=item.label, slider=True)
        for group, cmds in menu_groups("Character"):
            if group in ("New human", "Body"):
                continue
            box = layout.column(align=True)
            box.label(text=group)
            for cmd in cmds:
                box.operator(cmd.operator_idname, text=cmd.label)


_GROUP_ITEMS: list[tuple[str, str, str]] = []  # kept here: Blender needs Python to hold an enum callback's strings


def _groups(self, context):
    if not _GROUP_ITEMS:
        _GROUP_ITEMS.extend((g, g.title(), f"target.json's {g} sliders") for g in sliders.groups())
    return _GROUP_ITEMS


CLASSES = (VIEW3D_PT_juststage_character,)


def register():
    bpy.types.WindowManager.juststage_slider_group = bpy.props.EnumProperty(name="Slider group", items=_groups)
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    del bpy.types.WindowManager.juststage_slider_group
