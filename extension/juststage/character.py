# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The character's own fields on its Blender object (docs/standards/character-data-model.md §0).

Hand-written `bpy.props` (no generator); the USD hook writes them out as the `juststage:` attributes and
`assetInfo` later. `schema_version` versions this group (§6).
"""

import bpy

SCHEMA_VERSION = 1


class JustStageFloat(bpy.types.PropertyGroup):
    """One number in a list — for lists longer than Blender's 32-wide vector properties (a head's 170 GNM
    coefficients; a command's long `list[float]` parameter on its operator)."""

    value: bpy.props.FloatProperty()


class JustStageCharacter(bpy.types.PropertyGroup):
    schema_version: bpy.props.IntProperty(default=SCHEMA_VERSION)
    character_id: bpy.props.StringProperty(description="assetInfo.identifier — a UUID v4 that never changes")
    kind: bpy.props.EnumProperty(
        items=[("NONE", "None", "Not a JustStage character"), ("HUMAN", "Human", ""), ("CREATURE", "Creature", "")],
        default="NONE",
    )
    base_version: bpy.props.IntProperty(default=0)
    gender: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    age: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    muscle: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    weight: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    proportions: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    height: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    cupsize: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    firmness: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    asian: bpy.props.FloatProperty(default=0.33, min=0.0, max=1.0)
    caucasian: bpy.props.FloatProperty(default=0.33, min=0.0, max=1.0)
    african: bpy.props.FloatProperty(default=0.33, min=0.0, max=1.0)
    melanin: bpy.props.FloatProperty(default=0.0104, min=0.0, max=0.5)
    eumelanin: bpy.props.FloatProperty(default=0.6, min=0.0, max=1.0)
    blood: bpy.props.FloatProperty(default=0.016, min=0.001, max=0.2)
    oiliness: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    skin_material: bpy.props.PointerProperty(type=bpy.types.Material, description="this character's skin material")
    gnm_identity: bpy.props.CollectionProperty(type=JustStageFloat, description="GNM head identity coefficients")
    # on a part's object (an eye, the teeth): which part it is (MetaHuman's name) and whose
    part: bpy.props.StringProperty()
    part_of: bpy.props.StringProperty(description="the character's assetInfo identifier")


def register():
    bpy.utils.register_class(JustStageFloat)
    bpy.utils.register_class(JustStageCharacter)
    bpy.types.Object.juststage = bpy.props.PointerProperty(type=JustStageCharacter)


def unregister():
    del bpy.types.Object.juststage
    bpy.utils.unregister_class(JustStageCharacter)
    bpy.utils.unregister_class(JustStageFloat)


def find(character_id: str) -> bpy.types.Object:
    """The object whose `assetInfo` identifier is `character_id`."""
    from .core.commands import CommandError

    for obj in bpy.data.objects:
        if obj.juststage.character_id == character_id:
            return obj
    raise CommandError(f"no character {character_id!r}")
