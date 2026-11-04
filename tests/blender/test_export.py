# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.export.run` with the `package` preset: the USD character package (import-export.md §3,
character-data-model.md §0) - Blender's USD exporter plus JustStage's fields on the root prim."""

import importlib

import bpy
import pytest
from pxr import Usd, UsdShade, UsdSkel

api = importlib.import_module("bl_ext.system.juststage.api")


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Export test")
    obj = bpy.data.objects[result.object]
    yield result, obj
    bpy.data.objects.remove(obj)


def test_the_package_carries_the_character_and_its_fields(human, tmp_path):
    result, obj = human
    api.run("juststage.skin.set_tone", character=result.character)
    obj.juststage.gender = 0.9  # a slider away from its default
    out = api.run("juststage.export.run", character=result.character, folder=str(tmp_path / "pkg"))
    stage = Usd.Stage.Open(out.path)
    root = stage.GetPrimAtPath("/Character")
    assert root and stage.GetDefaultPrim() == root
    model = Usd.ModelAPI(root)
    assert model.GetAssetIdentifier().path == obj.juststage.character_id
    assert model.GetAssetName() == obj.name
    assert root.GetAttribute("juststage:formatVersion").Get() == 1
    assert root.GetAttribute("juststage:kind").Get() == "human"
    assert root.GetAttribute("juststage:baseVersion").Get() == obj.juststage.base_version
    ids = list(root.GetAttribute("juststage:sliderIds").Get())
    values = list(root.GetAttribute("juststage:sliderValues").Get())
    assert ids == ["macrodetails/Gender"] and values == pytest.approx([0.9])
    prims = list(stage.Traverse())
    assert any(p.IsA(UsdSkel.BlendShape) for p in prims)  # the shape keys
    assert any(p.IsA(UsdShade.Material) for p in prims)  # the skin material


def test_an_unknown_preset_is_refused(human, tmp_path):
    result, _ = human
    with pytest.raises(api.CommandError, match="no preset"):
        api.run("juststage.export.run", character=result.character, folder=str(tmp_path), preset="nowhere")
