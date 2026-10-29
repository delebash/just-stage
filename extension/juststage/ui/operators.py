# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The core's operators — one per core command, mirroring its `Params`."""

import bpy

from .command_operator import CommandOperator


class JUSTSTAGE_OT_api_status(CommandOperator, bpy.types.Operator):
    """Which JustStage, API and Blender this is, and which plugins are on"""

    bl_idname = "juststage.api_status"
    bl_label = "JustStage status"
    bl_options = {"REGISTER"}
    command_id = "juststage.api.status"


CLASSES = (JUSTSTAGE_OT_api_status,)
