# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body module's operators — each mirroring its command's `Params`."""

import bpy

from ...ui.command_operator import CommandOperator


def _macro(name: str, default: float = 0.5):
    return bpy.props.FloatProperty(name=name, default=default, min=0.0, max=1.0)


class JUSTSTAGE_OT_body_create(CommandOperator, bpy.types.Operator):
    """A new human on MakeHuman's base, shaped by its macro values"""

    bl_idname = "juststage.body_create"
    bl_label = "New human"
    bl_options = {"REGISTER", "UNDO"}
    command_id = "juststage.body.create"

    name: bpy.props.StringProperty(name="Name", default="Character")
    gender: _macro("Gender")
    age: _macro("Age")
    muscle: _macro("Muscle")
    weight: _macro("Weight")
    proportions: _macro("Proportions")
    height: _macro("Height")
    cupsize: _macro("Cup size")
    firmness: _macro("Firmness")
    asian: _macro("Asian", 0.33)
    caucasian: _macro("Caucasian", 0.33)
    african: _macro("African", 0.33)


CLASSES = (JUSTSTAGE_OT_body_create,)
