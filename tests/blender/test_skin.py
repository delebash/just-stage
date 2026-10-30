# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Skin module: the skin material from the calibrated chromophore model, and its fine detail from JustStage AI."""

import importlib

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
skin_detail = importlib.import_module("bl_ext.system.juststage.core.skin_detail")
detail = importlib.import_module("bl_ext.system.juststage.modules.skin.detail")


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


def test_skin_detail_from_juststage_ai(human):
    """The real server: JustStage AI started if it isn't running, FLUX.2 klein drawing the close-up on this card."""
    result, obj = human
    with pytest.raises(api.CommandError):  # the detail goes on the skin material, which set_tone makes
        api.run("juststage.skin.add_detail", character=result.character)
    api.run("juststage.skin.set_tone", character=result.character)
    out = api.run("juststage.skin.add_detail", character=result.character, size_mm=20.0, strength=0.5)
    image = bpy.data.images[out.image]
    assert out.model == "flux2-klein-4b"
    assert image.packed_file is not None and image.colorspace_settings.name == "Non-Color"
    assert image["juststage_feature"] == "juststage.skin_detail" and image["juststage_model"] == out.model
    w, h = image.size
    px = np.empty(w * h * 4, dtype=np.float32)
    image.pixels.foreach_get(px)
    height = px.reshape(h, w, 4)[..., 0].copy()
    assert skin_detail.wrap_ratio(height) < 1.5  # it tiles
    nodes = obj.juststage.skin_material.node_tree.nodes
    bump = nodes["juststage.detail.bump"]
    assert _bsdf(obj.juststage.skin_material).inputs["Normal"].links[0].from_node == bump
    scale = nodes["juststage.detail.mapping"].inputs["Scale"].default_value[0]
    assert scale == pytest.approx(1.0 / (detail.UV_PER_M * 0.020))
    again = api.run("juststage.skin.add_detail", character=result.character, seed=2, size_mm=10.0)
    assert again.image == out.image  # a second run replaces the detail, it doesn't stack another
    image.pixels.foreach_get(px)
    assert not np.allclose(px.reshape(h, w, 4)[..., 0], height)  # another seed, another skin
    assert sum(1 for n in nodes if n.name.startswith("juststage.detail.")) == 4
