# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Import / Export module: a character written for a target by a preset (import-export.md §3); importing joins
it (§1)."""

PLUGIN = "io"
NEEDS = ("body",)


def register(api_range: str):
    import bpy

    from ... import api
    from . import export_run, library_add, library_save, operators

    api.register_plugin(PLUGIN, api=api_range, needs=NEEDS, provides=("commands",), builtin=True)
    api.register_command(export_run, PLUGIN)
    api.register_command(library_save, PLUGIN)
    api.register_command(library_add, PLUGIN)
    for cls in operators.CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    import bpy

    from ... import api
    from . import operators

    for cls in reversed(operators.CLASSES):
        bpy.utils.unregister_class(cls)
    api.unregister_plugin(PLUGIN)
