# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The import / export module's operators — each mirroring its command's `Params`."""

import bpy

from ...ui.command_operator import CommandOperator


class JUSTSTAGE_OT_export_run(CommandOperator, bpy.types.Operator):
    """Write the character for a target, by a preset (first: the USD character package)"""

    bl_idname = "juststage.export_run"
    bl_label = "Export"
    bl_options = {"REGISTER"}
    command_id = "juststage.export.run"

    character: bpy.props.StringProperty(name="Character")
    folder: bpy.props.StringProperty(name="Folder", subtype="DIR_PATH")
    preset: bpy.props.StringProperty(name="Preset", default="package")


CLASSES = (JUSTSTAGE_OT_export_run,)
