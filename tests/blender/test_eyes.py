# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The eyes (modules/head/eyes.py): MPFB2's procedural iris and white on the iris, pupil and white faces - a smooth
iris instead of GNM's faceted regions - on UVs that run with the 3D radius; the cornea keeps its glass."""

import importlib

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
eyes = importlib.import_module("bl_ext.system.juststage.modules.head.eyes")


@pytest.fixture
def eye():
    made = api.run("juststage.body.create", name="Eye test")
    api.run("juststage.head.add_parts", character=made.character)
    body = bpy.data.objects[made.object]
    yield bpy.data.objects[f"{body.name}.eyeLeft"]
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(body)


def _groups(mat):
    return {n.node_tree.name.split(".")[-1] for n in mat.node_tree.nodes if n.type == "GROUP" and n.node_tree}


def test_the_iris_pupil_and_white_are_mpfb2s_procedural_eye(eye):
    mats = {m.name.split(" (")[0]: m for m in eye.data.materials}
    for name in ("JustStage Iris", "JustStage Pupil", "JustStage Sclera"):
        assert "EnhancedEye" in _groups(mats[name]), name
    cornea = mats["JustStage Cornea"]
    assert "EnhancedEye" not in _groups(cornea)
    assert eyes.gaze(eye)  # still found by the iris' and pupil's materials


def test_the_iris_uvs_run_with_the_3d_radius(eye):
    ids = {i for i, m in enumerate(eye.data.materials) if "Iris" in m.name or "Pupil" in m.name}
    co = np.array([v.co for v in eye.data.vertices])
    centre = (co.min(axis=0) + co.max(axis=0)) / 2
    loops = [(li, vi) for p in eye.data.polygons if p.material_index in ids
             for li, vi in zip(p.loop_indices, p.vertices, strict=True)]  # fmt: skip
    verts = sorted({vi for _li, vi in loops})
    axis = co[verts].mean(axis=0) - centre
    axis /= np.linalg.norm(axis)
    rel = co - centre
    radial = np.linalg.norm(rel - np.outer(rel @ axis, axis), axis=1)
    uv = eye.data.uv_layers[0].data
    rho = np.array([np.hypot(*(np.array(uv[li].uv) - 0.5)) for li, _vi in loops])
    r = np.array([radial[vi] for _li, vi in loops])
    assert np.corrcoef(rho, r)[0, 1] > 0.999  # GNM's own squeezes the pupil into 0-0.05 (0.97 or less)


def _iris_inputs(eye):
    for mat in eye.data.materials:
        for node in mat.node_tree.nodes:
            if node.type == "GROUP" and "IrisMajorColor" in node.inputs:
                yield node.inputs


def test_the_eye_colour_presets_and_custom_colours(eye):
    """CC5's eye colour: a preset sets both eyes; colours given set "custom"; the character keeps them, and eyes
    added again wear them."""
    character = eye.juststage.part_of
    body = next(o for o in bpy.data.objects if o.juststage.character_id == character)
    api.run("juststage.head.set_eye_colour", character=character, preset="blue")
    blue = eyes.PRESETS["blue"][0]
    for inputs in _iris_inputs(eye):
        assert tuple(inputs["IrisMajorColor"].default_value)[:3] == pytest.approx(blue)
    assert body.juststage.eye_preset == "blue" and tuple(body.juststage.iris_colour) == pytest.approx(blue)
    out = api.run("juststage.head.set_eye_colour", character=character, iris=[0.2, 0.1, 0.05], white=[0.6, 0.55, 0.5])
    assert out.eyes == 2 and body.juststage.eye_preset == "custom"
    for inputs in _iris_inputs(eye):
        assert tuple(inputs["EyeWhiteColor"].default_value)[:3] == pytest.approx((0.6, 0.55, 0.5))
    with pytest.raises(api.CommandError):
        api.run("juststage.head.set_eye_colour", character=character, iris=[1.5, 0.0, 0.0])
    # the eyes added again (a new pair) take the character's colours
    for part in [o for o in bpy.data.objects if o.juststage.part_of == character and o.juststage.part == "eyeLeft"]:
        bpy.data.objects.remove(part)
    api.run("juststage.head.add_parts", character=character)
    again = next(o for o in bpy.data.objects if o.juststage.part_of == character and o.juststage.part == "eyeLeft")
    for inputs in _iris_inputs(again):
        assert tuple(inputs["IrisMajorColor"].default_value)[:3] == pytest.approx((0.2, 0.1, 0.05))
