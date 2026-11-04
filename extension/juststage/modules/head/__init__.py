# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Head & Face module: scan-based head shapes (GNM's space on hm08), the ARKit face units, later the face rig."""

PLUGIN = "head"
NEEDS = ("body",)


def register(api_range: str):
    import bpy

    from ... import api
    from . import head_add_face_units, head_add_parts, head_set_eye_colour, head_set_identity, operators

    api.register_plugin(PLUGIN, api=api_range, needs=NEEDS, provides=("commands",), builtin=True)
    api.register_command(head_set_identity, PLUGIN)
    api.register_command(head_add_parts, PLUGIN)
    api.register_command(head_add_face_units, PLUGIN)
    api.register_command(head_set_eye_colour, PLUGIN)
    for cls in operators.CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    import bpy

    from ... import api
    from . import operators

    for cls in reversed(operators.CLASSES):
        bpy.utils.unregister_class(cls)
    api.unregister_plugin(PLUGIN)
