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
    assert result.controls == 174 and result.channels == 41
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
