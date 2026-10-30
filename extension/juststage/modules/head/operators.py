# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The head module's operators — each mirroring its command's `Params`."""

import bpy

from ...character import JustStageFloat
from ...ui.command_operator import CommandOperator


class JUSTSTAGE_OT_head_set_identity(CommandOperator, bpy.types.Operator):
    """A scan-based head shape from GNM's space"""

    bl_idname = "juststage.head_set_identity"
    bl_label = "Head shape (scan-based)"
    bl_options = {"REGISTER", "UNDO"}
    command_id = "juststage.head.set_identity"

    character: bpy.props.StringProperty(name="Character")
    seed: bpy.props.IntProperty(name="Seed", default=0)
    strength: bpy.props.FloatProperty(name="Strength", default=1.0, min=0.0, soft_max=2.0)
    coefficients: bpy.props.CollectionProperty(name="Coefficients", type=JustStageFloat)


class JUSTSTAGE_OT_head_add_parts(CommandOperator, bpy.types.Operator):
    """The head's eyes and teeth, fitted to the character"""

    bl_idname = "juststage.head_add_parts"
    bl_label = "Eyes and teeth"
    bl_options = {"REGISTER", "UNDO"}
    command_id = "juststage.head.add_parts"

    character: bpy.props.StringProperty(name="Character")


CLASSES = (JUSTSTAGE_OT_head_set_identity, JUSTSTAGE_OT_head_add_parts)
