# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The rig module's operators — each mirroring its command's `Params`."""

import bpy

from ...ui.command_operator import CommandOperator


class JUSTSTAGE_OT_rig_add_skeleton(CommandOperator, bpy.types.Operator):
    """The body skeleton (UE5's bones by Epic's names), placed on the character and bound"""

    bl_idname = "juststage.rig_add_skeleton"
    bl_label = "Skeleton (UE5)"
    bl_options = {"REGISTER", "UNDO"}
    command_id = "juststage.rig.add_skeleton"

    character: bpy.props.StringProperty(name="Character")


CLASSES = (JUSTSTAGE_OT_rig_add_skeleton,)
