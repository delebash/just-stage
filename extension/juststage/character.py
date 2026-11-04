# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The character's own fields on its Blender object (docs/standards/character-data-model.md §0).

Hand-written `bpy.props` (no generator); the USD hook writes them out as the `juststage:` attributes and
`assetInfo` later. `schema_version` versions this group (§6).
"""

import bpy

from .modules.head.eyes import IRIS_MAJOR, IRIS_MINOR, PRESETS
from .modules.head.eyes import WHITE as EYE_WHITE

SCHEMA_VERSION = 1
EYE_PRESETS = [("custom", "Custom", "the colours below")] + [
    (key, key.replace("_", " ").capitalize(), f"a {key.replace('_', ' ')} iris") for key in PRESETS
]

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


TONE = ("melanin", "eumelanin", "blood", "oiliness")


def _tone(label: str, default: float, low: float, high: float):
    """A skin-tone slider the Character panel draws: dragging it runs `juststage.skin.set_tone` with the character's
    four tone values (one way per job)."""

    def update(self, context):
        if APPLYING["macros"] or self.kind == "NONE" or not self.character_id:
            return
        from . import api

        values = {name: getattr(self, name) for name in TONE}
        try:
            api.run("juststage.skin.set_tone", character=self.character_id, **values)
        except api.CommandError as e:
            print(f"JustStage: {label}: {e}")

    return bpy.props.FloatProperty(name=label, default=default, min=low, max=high, update=update)


def _eye_update(name: str):
    """The Skin tab's eye colour fields: a preset, or the colours themselves (then "custom") - each runs
    `juststage.head.set_eye_colour` (one way per job)."""

    def update(self, context):
        if APPLYING["macros"] or self.kind == "NONE" or not self.character_id:
            return
        from . import api

        values = (
            {"preset": self.eye_preset}
            if name == "eye_preset" and self.eye_preset != "custom"
            else {
                "preset": "custom",
                "iris": list(self.iris_colour),
                "accent": list(self.iris_accent),
                "white": list(self.eye_white),
            }
        )
        try:
            api.run("juststage.head.set_eye_colour", character=self.character_id, **values)
        except api.CommandError as e:
            print(f"JustStage: eye colour: {e}")

    return update


def _colour(label: str, default, name: str):
    return bpy.props.FloatVectorProperty(
        name=label, subtype="COLOR", size=3, min=0.0, max=1.0, default=default, update=_eye_update(name)
    )


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
    melanin: _tone("Melanin", 0.0104, 0.0, 0.5)
    eumelanin: _tone("Eumelanin share", 0.6, 0.0, 1.0)
    blood: _tone("Blood", 0.016, 0.001, 0.2)
    oiliness: _tone("Oiliness", 0.5, 0.0, 1.0)
    skin_material: bpy.props.PointerProperty(type=bpy.types.Material, description="this character's skin material")
    # the eyes' colour (modules/head/head_set_eye_colour.py; eyes.PRESETS)
    eye_preset: bpy.props.EnumProperty(
        name="Eye colour", items=EYE_PRESETS, default="brown", update=_eye_update("eye_preset")
    )
    iris_colour: _colour("Iris", IRIS_MAJOR, "iris_colour")
    iris_accent: _colour("Iris accent", IRIS_MINOR, "iris_accent")
    eye_white: _colour("Eye white", EYE_WHITE, "eye_white")
    gnm_identity: bpy.props.CollectionProperty(type=JustStageFloat, description="GNM head identity coefficients")
    sliders: bpy.props.CollectionProperty(type=JustStageSlider, description="target.json's detail sliders' values")
    # the asset library's fields (project-files.md §2)
    asset_version: bpy.props.IntProperty(default=1, description="the asset's own version (Blender has none)")
    provenance: bpy.props.StringProperty(description="where the asset came from")
    licence_label: bpy.props.StringProperty(description="its licence, shown and never filtered")
    # on a part's object (an eye, the teeth): which part it is (MetaHuman's name) and whose
    part: bpy.props.StringProperty()
    part_of: bpy.props.StringProperty(description="the character's assetInfo identifier")


class JustStageMaterial(bpy.types.PropertyGroup):
    """A skin material's own record of the tone it was built from (written by modules/skin/material.py), so a skin
    preset in the library carries its values; and the asset library's fields (project-files.md §2)."""

    melanin: bpy.props.FloatProperty(default=0.0104)
    eumelanin: bpy.props.FloatProperty(default=0.6)
    blood: bpy.props.FloatProperty(default=0.016)
    oiliness: bpy.props.FloatProperty(default=0.5)
    is_skin: bpy.props.BoolProperty(description="built by juststage.skin.set_tone")
    # a mapped skin (modules/skin/maps.py): its maps, and the tone they were made at (its colour map's own)
    has_maps: bpy.props.BoolProperty(description="the skin carries maps (modules/skin/maps.py)")
    map_melanin: bpy.props.FloatProperty(default=0.0104)
    map_eumelanin: bpy.props.FloatProperty(default=0.6)
    map_blood: bpy.props.FloatProperty(default=0.016)
    asset_version: bpy.props.IntProperty(default=1, description="the asset's own version (Blender has none)")
    provenance: bpy.props.StringProperty(description="where the asset came from")
    licence_label: bpy.props.StringProperty(description="its licence, shown and never filtered")


def register():
    bpy.utils.register_class(JustStageFloat)
    bpy.utils.register_class(JustStageSlider)
    bpy.utils.register_class(JustStageCharacter)
    bpy.utils.register_class(JustStageMaterial)
    bpy.types.Object.juststage = bpy.props.PointerProperty(type=JustStageCharacter)
    bpy.types.Material.juststage = bpy.props.PointerProperty(type=JustStageMaterial)


def unregister():
    del bpy.types.Material.juststage
    del bpy.types.Object.juststage
    bpy.utils.unregister_class(JustStageMaterial)
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
