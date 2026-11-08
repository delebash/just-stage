# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Rig module: the body skeleton (the UE5 skeleton by Epic's names, MPFB2's placement and weights); later the
body correctives (`rig/body.dna`) and the controls."""

PLUGIN = "rig"
NEEDS = ("body",)


def register(api_range: str):
    import bpy

    from ... import api
    from . import operators, rig_add_skeleton

    api.register_plugin(PLUGIN, api=api_range, needs=NEEDS, provides=("commands",), builtin=True)
    api.register_command(rig_add_skeleton, PLUGIN)
    for cls in operators.CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    import bpy

    from ... import api
    from . import operators

    for cls in reversed(operators.CLASSES):
        bpy.utils.unregister_class(cls)
    api.unregister_plugin(PLUGIN)
