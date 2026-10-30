# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Head module: GNM's scan-based head shapes on hm08 (needs libs/wrap/gnm_to_hm08.py's output)."""

import importlib

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
paths = importlib.import_module("bl_ext.system.juststage.paths")
gnm_space = importlib.import_module("bl_ext.system.juststage.modules.head.gnm_space")

pytestmark = pytest.mark.skipif(not (paths.GENERATED / "gnm").exists(), reason="run libs/wrap/gnm_to_hm08.py")


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Head test")
    yield result, bpy.data.objects[result.object]
    bpy.data.objects.remove(bpy.data.objects[result.object])


def _key(obj):
    keys = obj.data.shape_keys
    co = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    keys.key_blocks[gnm_space.SHAPE_KEY].data.foreach_get("co", co)
    base = np.empty_like(co)
    keys.reference_key.data.foreach_get("co", base)
    return (co - base).reshape(-1, 3)


def test_a_random_scan_based_head(human):
    result, obj = human
    out = api.run("juststage.head.set_identity", character=result.character, seed=7)
    assert out.components == 170
    assert 1.0 < out.max_offset_mm < 40.0  # a different person, not a different species
    offset = _key(obj)
    moved = np.linalg.norm(offset, axis=1) > 1e-6
    assert moved[:13380].any() and not moved[13380:].any()  # the skin of the head only, never the helpers
    assert len(obj.juststage.gnm_identity) == 170


def test_given_coefficients_and_the_operator_door(human):
    result, obj = human
    api.run("juststage.head.set_identity", character=result.character, coefficients=[2.0])
    one = _key(obj).copy()
    status = bpy.ops.juststage.head_set_identity(character=result.character, coefficients=[{"name": "", "value": 2.0}])
    assert status == {"FINISHED"}
    assert np.allclose(_key(obj), one)
    assert obj.juststage.gnm_identity[0].value == pytest.approx(2.0)


def test_too_many_coefficients_are_refused(human):
    result, _ = human
    with pytest.raises(api.CommandError, match="at most 170"):
        api.run("juststage.head.set_identity", character=result.character, coefficients=[0.0] * 171)
