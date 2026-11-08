# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The gate's body rig (tools/gate/body_rig.py, the plan's §18a row 17): MPFB2's game-engine skeleton and weights on a
character - every joint inside the body, every vertex fully weighted, and a bone aimed where the gate's poses say."""

import importlib
import importlib.util
from pathlib import Path

import bpy
import numpy as np
import pytest
from mathutils.bvhtree import BVHTree

api = importlib.import_module("bl_ext.system.juststage.api")
makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
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
    bpy.data.objects.remove(arm)
    bpy.data.objects.remove(body)


def test_the_game_engine_rig_sits_inside_the_body_and_weighs_every_vertex(rigged):
    body, arm = rigged
    assert len(arm.data.bones) == 53
    assert body.modifiers[0].type == "ARMATURE" and body.modifiers[0].object == arm
    names = {b.name for b in arm.data.bones}
    total = np.zeros(len(body.data.vertices))
    for v in body.data.vertices:
        total[v.index] = sum(g.weight for g in v.groups if body.vertex_groups[g.group].name in names)
    assert np.abs(total - 1.0).max() < 1e-3, np.abs(total - 1.0).max()  # base v2's appended vertices too
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = body.evaluated_get(depsgraph).to_mesh()
    try:
        mesh.transform(body.matrix_world)
        tree = BVHTree.FromPolygons([v.co.copy() for v in mesh.vertices], [list(p.vertices) for p in mesh.polygons])
    finally:
        body.evaluated_get(depsgraph).to_mesh_clear()
    for bone in ("upperarm_r", "lowerarm_r", "hand_r", "thigh_r", "calf_r", "foot_r", "spine_02", "head"):
        # inside: a ray from the joint hits the skin both ways along x (a joint outside the body misses one side)
        c = body_rig.joint(arm, bone)
        hits = [tree.ray_cast(c, d, 1.0)[0] is not None for d in ((1, 0, 0), (-1, 0, 0))]
        assert all(hits), (bone, tuple(c))


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
