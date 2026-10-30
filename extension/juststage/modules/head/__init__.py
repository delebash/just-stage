# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Head & Face module: scan-based head shapes (GNM's space on hm08), later the face rig and expressions."""

PLUGIN = "head"
NEEDS = ("body",)


def register(api_range: str):
    import bpy

    from ... import api
    from . import head_set_identity, operators

    api.register_plugin(PLUGIN, api=api_range, needs=NEEDS, provides=("commands",), builtin=True)
    api.register_command(head_set_identity, PLUGIN)
    for cls in operators.CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    import bpy

    from ... import api
    from . import operators

    for cls in reversed(operators.CLASSES):
        bpy.utils.unregister_class(cls)
    api.unregister_plugin(PLUGIN)
