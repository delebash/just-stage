# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Hair module: grooms from MakeHuman's CC0 hair styles — Blender hair curves shaped by Blender's hair
node groups (the spec's item 5)."""

PLUGIN = "hair"
NEEDS = ("head",)


def register(api_range: str):
    import bpy

    from ... import api
    from . import hair_add, operators

    api.register_plugin(PLUGIN, api=api_range, needs=NEEDS, provides=("commands",), builtin=True)
    api.register_command(hair_add, PLUGIN)
    for cls in operators.CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    import bpy

    from ... import api
    from . import operators

    for cls in reversed(operators.CLASSES):
        bpy.utils.unregister_class(cls)
    api.unregister_plugin(PLUGIN)
