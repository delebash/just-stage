# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The gate's posing (tools/gate/body_rig.py, the plan's §18a row 17) on the product's skeleton: a limb aimed in
world space points where the gate's poses say, and the forearm twist turns each twist bone by its weights' place.
The skeleton itself is test_skeleton's."""

import importlib
import importlib.util
from pathlib import Path

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
_spec = importlib.util.spec_from_file_location("body_rig", Path(__file__).parents[2] / "tools" / "gate" / "body_rig.py")
body_rig = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(body_rig)


@pytest.fixture
def rigged():
    made = api.run("juststage.body.create", name="Rig test", gender=1.0)
    api.run("juststage.head.add_parts", character=made.character)
    body = bpy.data.objects[made.object]
    arm = body_rig.build(body)
    yield body, arm
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(body)


def test_the_gate_poses_the_products_skeleton(rigged):
    body, arm = rigged
    assert len(arm.data.bones) == 82 and arm.juststage.part == "skeleton"
    assert body_rig.build(body) == arm  # the one it has, not a second


def test_a_bone_turned_in_world_space_points_where_it_was_aimed(rigged):
    _body, arm = rigged
    want = np.array([0.0, -0.94, 0.34]) / np.linalg.norm([0.0, -0.94, 0.34])
    u = body_rig.direction(arm, "lowerarm_r")
    axis = np.cross(u, want)
    body_rig.turn(arm, "lowerarm_r", axis / np.linalg.norm(axis), np.degrees(np.arccos(u @ want)))
    assert np.allclose(body_rig.direction(arm, "lowerarm_r"), want, atol=1e-3)
    # ours: the bone's tail is on the next joint, so the limb points the same way (the gate aims limbs, joint to joint)
    assert np.allclose(body_rig.limb(arm, body_rig.ROLES["ours"], "lowerarm"), want, atol=1e-3)
    body_rig.rest(arm)
    assert np.allclose(body_rig.direction(arm, "lowerarm_r"), u, atol=1e-6)


def test_the_forearm_twist_turns_each_twist_bone_by_its_place(rigged):
    body, arm = rigged
    roles = body_rig.ROLES["ours"]
    wrist = np.array(body_rig.joint(arm, "hand_r"))
    fingers = np.array(body_rig.joint(arm, "thumb_02_r"))
    shares = body_rig.twist(arm, body, roles, 90.0)
    near, far = shares[roles["twist_near"]], shares[roles["twist_far"]]
    assert 0.2 < near < 0.5 < far < 0.95, shares  # ours at the thirds: their weights round 1/3 and 2/3 of the way
    assert np.allclose(np.array(body_rig.joint(arm, "hand_r")), wrist, atol=1e-6)  # about the forearm: the wrist stays
    assert np.linalg.norm(np.array(body_rig.joint(arm, "thumb_02_r")) - fingers) > 0.01  # and the hand turns
    body_rig.rest(arm)
