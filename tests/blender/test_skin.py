# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Skin module: the skin material from the calibrated chromophore model."""

import importlib

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Skin test")
    yield result, bpy.data.objects[result.object]
    bpy.data.objects.remove(bpy.data.objects[result.object])


def _bsdf(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def test_the_skin_material_carries_the_model(human):
    result, obj = human
    out = api.run("juststage.skin.set_tone", character=result.character)
    bsdf = _bsdf(obj.data.materials[out.material])
    assert bsdf.subsurface_method == "RANDOM_WALK_SKIN"
    assert tuple(bsdf.inputs["Base Color"].default_value)[:3] == pytest.approx(tuple(out.linear_rgb), abs=1e-6)
    r, g, b = bsdf.inputs["Subsurface Radius"].default_value
    assert r > g > b
    assert bsdf.inputs["IOR"].default_value == pytest.approx(1.4)


def test_darker_skin_and_the_operator_door(human):
    result, obj = human
    light = api.run("juststage.skin.set_tone", character=result.character).linear_rgb
    assert bpy.ops.juststage.skin_set_tone(character=result.character, melanin=0.2) == {"FINISHED"}
    assert sum(_bsdf(obj.data.materials[0]).inputs["Base Color"].default_value[:3]) < sum(light)
    assert len(obj.data.materials) == 1  # set again, not added again
    assert obj.juststage.melanin == pytest.approx(0.2)


def test_out_of_range_is_refused(human):
    result, _ = human
    with pytest.raises(api.CommandError, match="blood: expected"):
        api.run("juststage.skin.set_tone", character=result.character, blood=0.5)
