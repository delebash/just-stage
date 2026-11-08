# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face rig at runtime (modules/head/face_rig.py, `juststage.head.add_face_rig`): MetaHuman's controls on the
character drive its face's shape keys through RigLogic - set by hand, or keyed and played."""

import importlib

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
face_rig = importlib.import_module("bl_ext.system.juststage.modules.head.face_rig")


@pytest.fixture
def rigged():
    made = api.run("juststage.body.create", name="Face rig test", gender=1.0)
    api.run("juststage.head.add_face_units", character=made.character)
    result = api.run("juststage.head.add_face_rig", character=made.character)
    body = bpy.data.objects[made.object]
    yield body, result
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(body)


def test_the_controls_sit_on_the_character_and_drive_its_keys(rigged):
    body, result = rigged
    split = len(face_rig.SPLIT_EXPRESSIONS)  # MetaHuman's finer expressions as parts of our units (step 3d)
    assert result.controls == 174 and result.channels == 41 + split
    keys = body.data.shape_keys.key_blocks
    assert body["CTRL_L_brow_down.ty"] == 0.0
    assert body.id_properties_ui("CTRL_L_eye.tx").as_dict()["min"] == -1.0  # a two-way control
    body["CTRL_L_brow_down.ty"] = 0.7
    body["CTRL_C_jaw.ty"] = 0.4
    set_keys = face_rig.evaluate(body)
    assert keys["browDownLeft"].value == pytest.approx(0.7) and keys["jawOpen"].value == pytest.approx(0.4)
    assert set(set_keys) == {"browDownLeft", "jawOpen"}
    assert face_rig.evaluate(body) == {}  # nothing moved: nothing set
    body["CTRL_L_brow_down.ty"] = 0.0
    face_rig.evaluate(body)
    assert keys["browDownLeft"].value == pytest.approx(0.0)


def test_a_keyed_control_plays_through_the_rig(rigged):
    body, _ = rigged
    scene = bpy.context.scene
    body["CTRL_R_mouth_cornerPull.ty"] = 0.0
    body.keyframe_insert('["CTRL_R_mouth_cornerPull.ty"]', frame=1)
    body["CTRL_R_mouth_cornerPull.ty"] = 1.0
    body.keyframe_insert('["CTRL_R_mouth_cornerPull.ty"]', frame=11)
    scene.frame_set(11)  # the frame-change handler evaluates the rig
    assert body.data.shape_keys.key_blocks["mouthSmileRight"].value == pytest.approx(1.0)
    scene.frame_set(1)
    assert body.data.shape_keys.key_blocks["mouthSmileRight"].value == pytest.approx(0.0)
    body.animation_data_clear()


def test_the_finer_expressions_are_parts_that_sum_to_their_unit(rigged):
    """MetaHuman's purse by quadrant, its inner brow by side: each a part of our unit - the parts sum to the unit, the
    left part moves the face's left (+x), the upper part the upper lip (not what the jaw carries)."""
    import numpy as np

    body, _ = rigged
    keys = body.data.shape_keys.key_blocks
    n = len(body.data.vertices)

    def offsets(name):
        co, basis = np.empty(n * 3), np.empty(n * 3)
        keys[name].data.foreach_get("co", co)
        body.data.shape_keys.reference_key.data.foreach_get("co", basis)
        return (co - basis).reshape(-1, 3)

    whole = offsets("mouthPucker")
    parts = sum(offsets(f"mouthPucker_{q}") for q in ("UL", "UR", "DL", "DR"))
    assert np.abs(parts - whole).max() < 1e-6
    left = np.linalg.norm(offsets("browInnerUp_L"), axis=1)
    x = np.array([v.co.x for v in body.data.vertices])
    assert x[np.argmax(left)] > 0
    upper, jaw = np.linalg.norm(offsets("mouthPucker_UL") + offsets("mouthPucker_UR"), axis=1), np.linalg.norm(
        offsets("jawOpen"), axis=1)
    assert jaw[np.argmax(upper)] < 0.5 * jaw.max()  # the upper part's most moved skin is skin the jaw doesn't carry
    body["CTRL_L_mouth_purseU.ty"] = 1.0
    face_rig.evaluate(body)
    assert keys["mouthPucker_UL"].value == pytest.approx(1.0) and keys["mouthPucker_DL"].value == pytest.approx(0.0)
