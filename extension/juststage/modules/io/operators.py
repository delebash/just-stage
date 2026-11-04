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


class JUSTSTAGE_OT_library_save(CommandOperator, bpy.types.Operator):
    """Save the character to the asset library, in a catalogue, with its licence and where it came from"""

    bl_idname = "juststage.library_save"
    bl_label = "Save to library"
    bl_options = {"REGISTER"}
    command_id = "juststage.library.save"

    character: bpy.props.StringProperty(name="Character")
    catalog: bpy.props.StringProperty(name="Catalogue", default="Characters")
    name: bpy.props.StringProperty(name="Name", default="")
    description: bpy.props.StringProperty(name="Description", default="")
    licence: bpy.props.StringProperty(name="Licence", default="")
    provenance: bpy.props.StringProperty(name="Provenance", default="")
    library: bpy.props.StringProperty(name="Library", default="", subtype="DIR_PATH")


class JUSTSTAGE_OT_library_add(CommandOperator, bpy.types.Operator):
    """Add this character from the library, as a character of its own"""

    bl_idname = "juststage.library_add"
    bl_label = "Add from library"
    bl_options = {"REGISTER", "UNDO"}
    command_id = "juststage.library.add"

    path: bpy.props.StringProperty(name="Asset file", subtype="FILE_PATH")


CLASSES = (JUSTSTAGE_OT_export_run, JUSTSTAGE_OT_library_save, JUSTSTAGE_OT_library_add)
