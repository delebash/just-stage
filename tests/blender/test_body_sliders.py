# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.body.set_slider` (commands-and-api.md §2's own example): a macro slider of macro.json - or a race, the
three kept summing to 1 as MakeHuman does - changes the body, and the head's parts follow."""

import importlib
import time

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Slider test")
    yield result, bpy.data.objects[result.object]
    for obj in list(bpy.data.objects):
        if obj.juststage.part_of == result.character or obj.name == result.object:
            bpy.data.objects.remove(obj)


def test_a_macro_slider_reshapes_the_body(human):
    result, obj = human
    before = build.shaped_coords(obj).copy()
    t = time.perf_counter()
    out = api.run("juststage.body.set_slider", character=result.character, slider="weight", value=0.9)
    took = time.perf_counter() - t
    print(f"set_slider weight: {took:.2f} s")
    assert out.status == "ok" and out.value == pytest.approx(0.9)
    assert obj.juststage.weight == pytest.approx(0.9)
    moved = np.linalg.norm(build.shaped_coords(obj) - before, axis=1)
    assert moved.max() > 0.01  # a heavier body: centimetres somewhere


def test_a_race_keeps_the_three_summing_to_one(human):
    result, obj = human
    api.run("juststage.body.set_slider", character=result.character, slider="african", value=0.7)
    props = obj.juststage
    assert props.african == pytest.approx(0.7)
    assert props.asian + props.caucasian + props.african == pytest.approx(1.0, abs=1e-4)
    assert props.asian == pytest.approx(props.caucasian, abs=1e-4)  # the other two share the rest


def test_the_heads_parts_follow_the_body(human):
    result, obj = human
    api.run("juststage.head.add_parts", character=result.character)
    eye = next(o for o in bpy.data.objects if o.juststage.part_of == result.character and "eyeLeft" in o.name)
    before = np.array([v.co for v in eye.data.vertices])
    api.run("juststage.body.set_slider", character=result.character, slider="height", value=1.0)
    assert np.linalg.norm(np.array([v.co for v in eye.data.vertices]) - before, axis=1).mean() > 0.005


def test_dragging_the_characters_own_slider_reshapes_it(human):
    result, obj = human
    before = build.shaped_coords(obj).copy()
    obj.juststage.muscle = 0.95  # what the Body panel's slider does
    assert np.linalg.norm(build.shaped_coords(obj) - before, axis=1).max() > 0.005
    obj.juststage.asian = 0.8  # a race through the panel keeps the three at 1
    props = obj.juststage
    assert props.asian + props.caucasian + props.african == pytest.approx(1.0, abs=1e-4)


sliders = importlib.import_module("bl_ext.system.juststage.modules.body.sliders")


def test_the_catalogue_is_target_jsons():
    found = sliders.catalog()
    assert len(found) == 300  # 234 categories, 66 of them twice (left and right)
    assert found["arms/l-lowerarm-scale-depth-decr-incr"].negative == "l-lowerarm-scale-depth-decr"
    assert found["chin/chin-triangle"].low == 0.0  # one target: 0..1


def test_a_detail_slider_weights_its_two_targets(human):
    result, obj = human
    assert len(obj.juststage.sliders) == 300  # every slider at 0, ready for the panel...
    detail_keys = [
        k for k in obj.data.shape_keys.key_blocks if k.name.startswith("makehuman.") and not build.is_macro_key(k.name)
    ]
    assert not detail_keys  # ...with no keys yet
    sid = "nose/nose-nostrils-angle-down-up"
    api.run("juststage.body.set_slider", character=result.character, slider=sid, value=0.8)
    keys = obj.data.shape_keys.key_blocks
    assert keys["makehuman.nose-nostrils-angle-up"].value == pytest.approx(0.8)
    assert "makehuman.nose-nostrils-angle-down" not in keys  # never used: no key
    next(s for s in obj.juststage.sliders if s.id == sid).value = -0.5  # the panel's slider
    assert keys["makehuman.nose-nostrils-angle-up"].value == 0.0
    assert keys["makehuman.nose-nostrils-angle-down"].value == pytest.approx(0.5)
    with pytest.raises(api.CommandError, match="0.0"):
        api.run("juststage.body.set_slider", character=result.character, slider="chin/chin-triangle", value=-0.5)


def test_an_unknown_slider_and_a_bad_value_are_refused(human):
    result, _ = human
    with pytest.raises(api.CommandError, match="slider"):
        api.run("juststage.body.set_slider", character=result.character, slider="wings", value=0.5)
    with pytest.raises(api.CommandError, match="0.0"):
        api.run("juststage.body.set_slider", character=result.character, slider="age", value=1.5)
