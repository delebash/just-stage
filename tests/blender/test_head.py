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
    moved = np.flatnonzero(np.linalg.norm(offset, axis=1) > 1e-6)
    assert (moved < 13380).any()  # the head's skin
    head_helpers = set()
    for group in (
        "helper-l-eye",
        "helper-r-eye",
        "helper-upper-teeth",
        "helper-lower-teeth",
        "helper-tongue",
        "helper-l-eyelashes-1",
        "helper-l-eyelashes-2",
        "helper-r-eyelashes-1",
        "helper-r-eyelashes-2",
        "helper-hair",
    ):
        vg = obj.vertex_groups[group].index
        head_helpers |= {v.index for v in obj.data.vertices if any(g.group == vg for g in v.groups)}
    stray = [v for v in moved if v >= 13380 and v not in head_helpers]
    assert stray == []  # the head's helpers follow it (what eyes and teeth fit to); joint cubes and the rest don't
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


def _centre(obj):
    """The bounding-box centre — an eyeball's centre (its mean point sits forward: GNM's cornea and iris are dense)."""
    co = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    obj.data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    return (co.min(axis=0) + co.max(axis=0)) / 2


def test_eyes_and_teeth_fit_in_the_head_and_follow_it(human):
    result, obj = human
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    out = api.run("juststage.head.add_parts", character=result.character)
    assert sorted(out.added) == sorted(out.parts) == ["eyeLeft", "eyeRight", "teeth"]
    parts = {o.juststage.part: o for o in obj.children}
    shaped = build.shaped_coords(obj)
    for side, cube in (("eyeLeft", "joint-l-eye"), ("eyeRight", "joint-r-eye")):
        vg = obj.vertex_groups[cube].index
        idx = [v.index for v in obj.data.vertices if any(g.group == vg for g in v.groups)]
        assert np.linalg.norm(_centre(parts[side]) - shaped[idx].mean(axis=0)) < 0.004  # in its socket, ±4 mm
    before = {k: _centre(p).copy() for k, p in parts.items()}
    api.run("juststage.head.set_identity", character=result.character, seed=5, strength=2.0)
    moved = [np.linalg.norm(_centre(parts[k]) - before[k]) for k in before]
    assert max(moved) > 0.0005  # the parts followed the new head
    again = api.run("juststage.head.add_parts", character=result.character)
    assert again.added == [] and len(obj.children) == 3  # running it again refits, never duplicates
