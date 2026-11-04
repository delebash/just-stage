# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's fields in a USD character package (docs/standards/character-data-model.md §0): the approved `juststage:`
attributes (N1) and USD's own `assetInfo`, written on the package's root prim by Blender's USD hook API
(https://docs.blender.org/api/5.3/bpy.types.USDHook.html) - Blender 5.0+ keeps `bpy.props` values apart from custom
properties, so its own custom-property export doesn't see them."""

from __future__ import annotations

import bpy

from . import makehuman

#: the attribute set's version (character-data-model.md §6)
FORMAT_VERSION = 1
#: the slider fields the package records - the ids `juststage.body.set_slider` takes (one id per slider in the command,
#: the panel and the package; MakeHuman's MHM names are the MHM export's, character-data-model.md §1.3)
MACRO_SLIDERS = (*makehuman.MACROS, *makehuman.RACES)


def sliders(props) -> tuple[list[str], list[float]]:
    """The slider ids whose values differ from default, and their values (character-data-model.md §0): the macros,
    the race mix and target.json's detail sliders."""
    defaults = makehuman.default_macros()
    ids, values = [], []
    for field in MACRO_SLIDERS:
        value = float(getattr(props, field))
        default = defaults["race"][field] if field in makehuman.RACES else defaults[field]
        if abs(value - default) > 1e-6:
            ids.append(field)
            values.append(value)
    for item in props.sliders:
        if abs(item.value) > 1e-6:
            ids.append(item.id)
            values.append(float(item.value))
    return ids, values


def write_character(stage, prim_path: str, obj: bpy.types.Object) -> None:
    """The character's fields on its root prim."""
    from pxr import Sdf, Usd, Vt

    prim = stage.GetPrimAtPath(prim_path)
    props = obj.juststage
    model = Usd.ModelAPI(prim)
    model.SetAssetIdentifier(Sdf.AssetPath(props.character_id))
    model.SetAssetName(obj.name)
    model.SetAssetVersion(str(props.schema_version))
    prim.CreateAttribute("juststage:formatVersion", Sdf.ValueTypeNames.Int).Set(FORMAT_VERSION)
    prim.CreateAttribute("juststage:kind", Sdf.ValueTypeNames.Token).Set(props.kind.lower())
    prim.CreateAttribute("juststage:baseVersion", Sdf.ValueTypeNames.Int).Set(props.base_version)
    ids, values = sliders(props)
    prim.CreateAttribute("juststage:sliderIds", Sdf.ValueTypeNames.TokenArray).Set(Vt.TokenArray(ids))
    prim.CreateAttribute("juststage:sliderValues", Sdf.ValueTypeNames.FloatArray).Set(Vt.FloatArray(values))
    prim.SetCustomDataByKey("juststage", {"exporter": "JustStage", "blender": bpy.app.version_string})


class JustStageUSDHook(bpy.types.USDHook):
    """JustStage's fields on the character package's root prim"""

    bl_idname = "juststage"
    bl_label = "JustStage"

    @staticmethod
    def on_export(export_context):
        stage = export_context.get_stage()
        root = stage.GetDefaultPrim()
        if not root:
            return True
        characters = [
            o for o in bpy.data.objects if o.select_get() and o.juststage.character_id and o.juststage.kind != "NONE"
        ]
        if len(characters) == 1:  # one package, one character (juststage.export.run selects it and its parts)
            write_character(stage, str(root.GetPath()), characters[0])
        return True


CLASSES = (JustStageUSDHook,)
