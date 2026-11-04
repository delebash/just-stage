# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The character's own fields on its Blender object (docs/standards/character-data-model.md §0).

Hand-written `bpy.props` (no generator); the USD hook writes them out as the `juststage:` attributes and
`assetInfo` later. `schema_version` versions this group (§6).
"""

import bpy

SCHEMA_VERSION = 1

#: True while `body.build.apply_macros` writes the sliders' values: their update callbacks then stay quiet
APPLYING = {"macros": False}


def _slider(name: str, label: str, default: float):
    """A body slider the Body panel draws: dragging it runs `juststage.body.set_slider` (one way per job: the same
    command the API and MCP doors run)."""

    def update(self, context):
        if APPLYING["macros"] or self.kind == "NONE" or not self.character_id:
            return
        from . import api

        try:
            api.run("juststage.body.set_slider", character=self.character_id, slider=name, value=getattr(self, name))
        except api.CommandError as e:
            print(f"JustStage: {label}: {e}")

    return bpy.props.FloatProperty(name=label, default=default, min=0.0, max=1.0, update=update)


class JustStageFloat(bpy.types.PropertyGroup):
    """One number in a list — for lists longer than Blender's 32-wide vector properties (a head's 170 GNM
    coefficients; a command's long `list[float]` parameter on its operator)."""

    value: bpy.props.FloatProperty()


def _detail_update(self, context):
    if APPLYING["macros"]:
        return
    owner = self.id_data.juststage
    if not owner.character_id:
        return
    from . import api

    try:
        api.run("juststage.body.set_slider", character=owner.character_id, slider=self.id, value=self.value)
    except api.CommandError as e:
        print(f"JustStage: {self.id}: {e}")


class JustStageSlider(bpy.types.PropertyGroup):
    """One of target.json's detail sliders on a character (modules/body/sliders.py): its id and value; dragging it
    runs `juststage.body.set_slider`."""

    id: bpy.props.StringProperty()
    label: bpy.props.StringProperty()
    group: bpy.props.StringProperty()
    value: bpy.props.FloatProperty(name="Value", default=0.0, min=-1.0, max=1.0, update=_detail_update)


class JustStageCharacter(bpy.types.PropertyGroup):
    schema_version: bpy.props.IntProperty(default=SCHEMA_VERSION)
    character_id: bpy.props.StringProperty(description="assetInfo.identifier — a UUID v4 that never changes")
    kind: bpy.props.EnumProperty(
        items=[("NONE", "None", "Not a JustStage character"), ("HUMAN", "Human", ""), ("CREATURE", "Creature", "")],
        default="NONE",
    )
    base_version: bpy.props.IntProperty(default=0)
    gender: _slider("gender", "Gender", 0.5)
    age: _slider("age", "Age", 0.5)
    muscle: _slider("muscle", "Muscle", 0.5)
    weight: _slider("weight", "Weight", 0.5)
    proportions: _slider("proportions", "Proportions", 0.5)
    height: _slider("height", "Height", 0.5)
    cupsize: _slider("cupsize", "Cup size", 0.5)
    firmness: _slider("firmness", "Firmness", 0.5)
    asian: _slider("asian", "Asian", 0.33)
    caucasian: _slider("caucasian", "Caucasian", 0.33)
    african: _slider("african", "African", 0.33)
    melanin: bpy.props.FloatProperty(default=0.0104, min=0.0, max=0.5)
    eumelanin: bpy.props.FloatProperty(default=0.6, min=0.0, max=1.0)
    blood: bpy.props.FloatProperty(default=0.016, min=0.001, max=0.2)
    oiliness: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0)
    skin_material: bpy.props.PointerProperty(type=bpy.types.Material, description="this character's skin material")
    gnm_identity: bpy.props.CollectionProperty(type=JustStageFloat, description="GNM head identity coefficients")
    sliders: bpy.props.CollectionProperty(type=JustStageSlider, description="target.json's detail sliders' values")
    # on a part's object (an eye, the teeth): which part it is (MetaHuman's name) and whose
    part: bpy.props.StringProperty()
    part_of: bpy.props.StringProperty(description="the character's assetInfo identifier")


def register():
    bpy.utils.register_class(JustStageFloat)
    bpy.utils.register_class(JustStageSlider)
    bpy.utils.register_class(JustStageCharacter)
    bpy.types.Object.juststage = bpy.props.PointerProperty(type=JustStageCharacter)


def unregister():
    del bpy.types.Object.juststage
    bpy.utils.unregister_class(JustStageCharacter)
    bpy.utils.unregister_class(JustStageSlider)
    bpy.utils.unregister_class(JustStageFloat)


def find(character_id: str) -> bpy.types.Object:
    """The object whose `assetInfo` identifier is `character_id`."""
    from .core.commands import CommandError

    for obj in bpy.data.objects:
        if obj.juststage.character_id == character_id:
            return obj
    raise CommandError(f"no character {character_id!r}")
