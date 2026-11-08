# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body skeleton (modules/rig/skeleton.py, `juststage.rig.add_skeleton`): the spec's 82 bones in `DEF`, every
skin vertex weighted, the joints inside the body at the sliders' extremes and following a slider, a forearm twist
spread along the twist bones, the head's parts riding the head bone."""

import importlib
import math

import bpy
import numpy as np
import pytest
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

api = importlib.import_module("bl_ext.system.juststage.api")
skeleton = importlib.import_module("bl_ext.system.juststage.modules.rig.skeleton")
makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")


def _make(name="Skeleton test", **macros):
    made = api.run("juststage.body.create", name=name, **macros)
    api.run("juststage.head.add_parts", character=made.character)
    result = api.run("juststage.rig.add_skeleton", character=made.character)
    return made, bpy.data.objects[made.object], bpy.data.objects[result.object], result


def _remove(made):
    body = bpy.data.objects[made.object]
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(body)


def _rest(arm):
    for pb in arm.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


def _evaluated(obj) -> np.ndarray:
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    try:
        co = np.empty(len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", co)
        return co.reshape(-1, 3) @ np.array(obj.matrix_world)[:3, :3].T + np.array(obj.matrix_world)[:3, 3]
    finally:
        ev.to_mesh_clear()


@pytest.fixture(scope="module")
def man():
    made, body, arm, result = _make()
    yield made, body, arm, result
    _remove(made)


def test_the_skeleton_is_the_specs_82_in_def_with_every_skin_vertex_weighted(man):
    made, body, arm, result = man
    rig = skeleton.definition()
    face = set(skeleton.FACE_BONES)  # the face's joints mirrored in (the jaw, which the lower teeth ride)
    assert len(rig) == 82 and result.bones == 82 + len(face)
    assert {b.name for b in arm.data.bones} == set(rig) | face
    deform = arm.data.collections[skeleton.COLLECTION]
    assert {b.name for b in deform.bones} == set(rig) | face
    for b in arm.data.bones:
        parent = skeleton.FACE_BONES[b.name][2] if b.name in face else rig[b.name]["parent"]
        assert (b.parent.name if b.parent else "") == parent, b.name
    jaw = arm.data.bones[skeleton.JAW]
    assert abs(jaw.x_axis.x - 1.0) < 1e-3  # it opens about the face's left-right axis (the DNA's rx)
    assert body.modifiers[0].type == "ARMATURE" and body.modifiers[0].object == arm
    names = {vg.index: vg.name for vg in body.vertex_groups if vg.name in rig}
    skin = makehuman.skin_indices(len(body.data.vertices))
    for i in skin:
        groups = [g for g in body.data.vertices[i].groups if g.group in names and g.weight > 0]
        assert 0 < len(groups) <= 8, i
        assert abs(sum(g.weight for g in groups) - 1.0) < 1e-3, i
    for part in ("eyeLeft", "eyeRight", "teeth"):
        obj = next(o for o in skeleton.riders(body) if o.juststage.part == part)
        assert obj.modifiers[0].type == "ARMATURE" and obj.vertex_groups.get(skeleton.HEAD) is not None


EXTREMES = [{"gender": 0.0, "weight": 0.0, "height": 0.0}, {"gender": 1.0, "weight": 1.0, "muscle": 1.0, "height": 1.0},
            {"gender": 0.0, "age": 0.0}, {"gender": 1.0, "age": 1.0, "proportions": 1.0}]  # fmt: skip


#: a joint may sit this close outside the skin: MPFB2's own toe joint (`joint-l-foot-1`, the ball's head) lies 0.4 mm
#: below the sole of MakeHuman's age-0 foot (2026-11-08) - a pivot at the skin, harmless; a misplaced joint is cm off
SKIN_MM = 1.0


@pytest.mark.parametrize("macros", EXTREMES)
def test_every_joint_is_inside_the_body_at_the_sliders_extremes(macros):
    made, body, arm, _ = _make(name="Skeleton extremes", **macros)
    try:
        co = build.shaped_coords(body)
        faces = [list(p.vertices) for p in body.data.polygons
                 if all(v < makehuman.BODY_VERTICES for v in p.vertices)]  # fmt: skip
        tree = BVHTree.FromPolygons([Vector(c) for c in co], faces)
        outside = []
        for b in arm.data.bones:
            if b.name == "root":  # on the floor, by the spec
                continue
            p = Vector(b.head_local)
            hit, normal, _, _ = tree.find_nearest(p)
            if (p - hit).dot(normal) > SKIN_MM / 1000:
                outside.append((b.name, round((p - hit).length * 1000, 1)))
        assert not outside, outside
    finally:
        _remove(made)


def test_the_joints_follow_a_slider(man):
    made, body, arm, _ = man
    before = arm.data.bones["hand_l"].head_local.copy()
    api.run("juststage.body.set_slider", character=made.character, slider="height", value=0.9)
    try:
        where = skeleton.joints(body)
        assert (arm.data.bones["hand_l"].head_local - where["hand_l"][0]).length < 1e-5
        assert (arm.data.bones["hand_l"].head_local - before).length > 0.01  # a taller man's hand sits elsewhere
    finally:
        api.run("juststage.body.set_slider", character=made.character, slider="height", value=0.5)


def _turn(arm, bone, degrees):
    """`bone` turned about its own length (Y) by `degrees`."""
    pb = arm.pose.bones[bone]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = (0.0, math.radians(degrees), 0.0)


def test_a_forearm_twist_spreads_along_the_twist_bones(man):
    made, body, arm, _ = man
    _rest(arm)
    rest = _evaluated(body)
    elbow, wrist = (np.array(arm.matrix_world @ arm.data.bones[b].head_local) for b in ("lowerarm_l", "hand_l"))
    # the hand turned 90 deg and the twist bones by their place (as body.dna's twist layer will turn them)
    _turn(arm, "hand_l", 90)
    _turn(arm, "lowerarm_twist_01_l", 60)
    _turn(arm, "lowerarm_twist_02_l", 30)
    bpy.context.view_layer.update()
    try:
        posed = _evaluated(body)
        axis = (wrist - elbow) / np.linalg.norm(wrist - elbow)
        t = (rest - elbow) @ axis / np.linalg.norm(wrist - elbow)
        radial = rest - elbow - np.outer((rest - elbow) @ axis, axis)
        near = np.linalg.norm(radial, axis=1) < 0.06
        moved = posed - rest

        def turn(lo, hi):
            ring = near & (t > lo) & (t < hi)
            r, m = radial[ring], moved[ring]
            return float(np.median(np.linalg.norm(m, axis=1) / np.maximum(np.linalg.norm(r, axis=1), 1e-6)))

        low, high = turn(0.1, 0.25), turn(0.75, 0.9)
        assert high > 2 * low > 0.0, (low, high)  # the skin twists more toward the wrist, smoothly from the elbow
    finally:
        _rest(arm)


def test_the_heads_parts_ride_the_head_bone(man):
    made, body, arm, _ = man
    _rest(arm)
    eye = next(o for o in skeleton.riders(body) if o.juststage.part == "eyeLeft")
    rest = _evaluated(eye).mean(0)
    pb = arm.pose.bones["head"]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = (math.radians(25), 0.0, 0.0)
    bpy.context.view_layer.update()
    try:
        moved = _evaluated(eye).mean(0)
        expect = arm.matrix_world @ pb.matrix @ arm.data.bones["head"].matrix_local.inverted() @ \
            arm.matrix_world.inverted() @ Vector(rest)  # fmt: skip
        assert np.linalg.norm(moved - np.array(expect)) < 1e-4
        assert np.linalg.norm(moved - rest) > 0.005
    finally:
        _rest(arm)
