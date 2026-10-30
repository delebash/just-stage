# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The hair module's operators — each mirroring its command's `Params`."""

import bpy

from ...ui.command_operator import CommandOperator
from .styles import DEFAULT, STYLES


class JUSTSTAGE_OT_hair_add(CommandOperator, bpy.types.Operator):
    """A groom from MakeHuman's hair styles: scalp hair, eyebrows, eyelashes, beards, moustaches"""

    bl_idname = "juststage.hair_add"
    bl_label = "Add hair"
    bl_options = {"REGISTER", "UNDO"}
    command_id = "juststage.hair.add"

    character: bpy.props.StringProperty(name="Character")
    style: bpy.props.EnumProperty(
        name="Style",
        items=[(name, label, f"{label} ({kind})") for name, (kind, label) in STYLES.items()],
        default=DEFAULT,
    )
    melanin: bpy.props.FloatProperty(name="Melanin", default=0.8, min=0.0, max=1.0)
    redness: bpy.props.FloatProperty(name="Redness", default=1.0, min=0.0, max=1.0)


CLASSES = (JUSTSTAGE_OT_hair_add,)
