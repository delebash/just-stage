# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Skin module: the skin material from the calibrated chromophore model, later the generated texture layers."""

PLUGIN = "skin"
NEEDS = ("body",)


def register(api_range: str):
    import bpy

    from ... import api
    from . import operators, skin_set_tone

    api.register_plugin(PLUGIN, api=api_range, needs=NEEDS, provides=("commands",), builtin=True)
    api.register_command(skin_set_tone, PLUGIN)
    for cls in operators.CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    import bpy

    from ... import api
    from . import operators

    for cls in reversed(operators.CLASSES):
        bpy.utils.unregister_class(cls)
    api.unregister_plugin(PLUGIN)
