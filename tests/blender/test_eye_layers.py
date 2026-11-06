# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The eye occlusion and tearline (modules/head/eye_layers.py): ICT-FaceKit's strips over both eyeballs, between the
lids, with the head's other parts; they follow the eyes when the body changes."""

import importlib

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
eyes = importlib.import_module("bl_ext.system.juststage.modules.head.eyes")
parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")


@pytest.fixture
def human():
    made = api.run("juststage.body.create", name="Eye layer test", gender=0.0)
    api.run("juststage.head.add_parts", character=made.character)
    body = bpy.data.objects[made.object]
    yield made, body
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(body)


def _gap_to_eyeball(layer, eye_objs):
    """Each layer vertex's height off its own eyeball's sphere (m)."""
    points = eyes.world_points(layer)
    which = np.zeros(len(points), np.int32)
    layer.data.attributes["js_eye"].data.foreach_get("value", which)
    gaps = np.zeros(len(points))
    for k, eye in enumerate(eye_objs):
        centre, radius = eye_layers._eye_sphere(eye)
        gaps[which == k] = np.linalg.norm(points[which == k] - centre, axis=1) - radius
    return gaps


def test_both_layers_come_with_the_eyes(human):
    made, body = human
    layers = eye_layers.layers_of(body)
    assert set(layers) == {"eyeshell", "eyeEdge"}
    eye_objs = [parts.parts_of(body)[p] for p in ("eyeLeft", "eyeRight")]
    for part, obj in layers.items():
        assert obj.parent == body and obj.juststage.part_of == made.character
        assert not obj.visible_shadow  # films: they cast nothing
        which = np.zeros(len(obj.data.vertices), np.int32)
        obj.data.attributes["js_eye"].data.foreach_get("value", which)
        assert set(which.tolist()) == {0, 1}  # both eyes in one object (MetaHuman's way)
        gaps = _gap_to_eyeball(obj, eye_objs)
        assert gaps.min() > 0.00005 and gaps.max() < 0.003, (part, gaps.min(), gaps.max())
    # the occlusion sits 0.4 mm off the eyeball and spans the opening between the lids
    assert np.allclose(_gap_to_eyeball(layers["eyeshell"], eye_objs), eye_layers.OCCLUSION_LIFT, atol=2e-6)


def test_they_follow_the_eyes_when_the_body_changes(human):
    made, body = human
    api.run("juststage.body.set_slider", character=made.character, slider="height", value=1.0)
    eye_objs = [parts.parts_of(body)[p] for p in ("eyeLeft", "eyeRight")]
    gaps = _gap_to_eyeball(eye_layers.layers_of(body)["eyeshell"], eye_objs)
    assert np.allclose(gaps, eye_layers.OCCLUSION_LIFT, atol=2e-6)


def test_they_follow_the_lids_when_the_eyes_open(human):
    """A slider that changes the lids' opening (the dressed human's EYE_OPEN) moves the films to the new lids: the
    occlusion spans the opening as it is now, not the one it was made on (the gate, 2026-11-05: made on the closed
    library eye, it sat as a lens in the middle of the opened one, its lid-edge darkening inside the opening)."""
    made, body = human
    body_create = importlib.import_module("bl_ext.system.juststage.modules.body.body_create")
    body_create.open_eyes(made.character)
    eye_objs = [parts.parts_of(body)[p] for p in ("eyeLeft", "eyeRight")]
    found = eyes.openings(body)
    shell = eye_layers.layers_of(body)["eyeshell"]
    values = {}
    for name in ("js_eye", "js_el"):
        buf = np.zeros(len(shell.data.vertices), np.int32 if name == "js_eye" else np.float32)
        shell.data.attributes[name].data.foreach_get("value", buf)
        values[name] = buf
    for k, eye in enumerate(eye_objs):
        _, _, wanted, _, _ = eye_layers.occlusion_shape(found[eye.name])
        assert np.allclose(values["js_el"][values["js_eye"] == k], wanted, atol=0.05), eye.name
    assert np.allclose(_gap_to_eyeball(shell, eye_objs), eye_layers.OCCLUSION_LIFT, atol=2e-6)
