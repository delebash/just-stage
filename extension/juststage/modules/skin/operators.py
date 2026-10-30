# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The skin module's operators — each mirroring its command's `Params`."""

import bpy

from ...ui.command_operator import CommandOperator


class JUSTSTAGE_OT_skin_set_tone(CommandOperator, bpy.types.Operator):
    """The skin's colour from melanin, blood and oiliness"""

    bl_idname = "juststage.skin_set_tone"
    bl_label = "Skin tone"
    bl_options = {"REGISTER", "UNDO"}
    command_id = "juststage.skin.set_tone"

    character: bpy.props.StringProperty(name="Character")
    melanin: bpy.props.FloatProperty(name="Melanin", default=0.0104, min=0.0, max=0.5)
    eumelanin: bpy.props.FloatProperty(name="Eumelanin share", default=0.6, min=0.0, max=1.0)
    blood: bpy.props.FloatProperty(name="Blood", default=0.016, min=0.001, max=0.2)
    oiliness: bpy.props.FloatProperty(name="Oiliness", default=0.5, min=0.0, max=1.0)


class JUSTSTAGE_OT_skin_add_detail(CommandOperator, bpy.types.Operator):
    """The skin's fine detail, drawn by JustStage AI"""

    bl_idname = "juststage.skin_add_detail"
    bl_label = "Skin detail (AI)"
    bl_options = {"REGISTER", "UNDO"}
    command_id = "juststage.skin.add_detail"

    character: bpy.props.StringProperty(name="Character")
    seed: bpy.props.IntProperty(name="Seed", default=1)
    size_mm: bpy.props.FloatProperty(name="Tile size (mm)", default=20.0, min=1.0, max=200.0)
    strength: bpy.props.FloatProperty(name="Strength", default=0.5, min=0.0, max=2.0)


CLASSES = (JUSTSTAGE_OT_skin_set_tone, JUSTSTAGE_OT_skin_add_detail)
