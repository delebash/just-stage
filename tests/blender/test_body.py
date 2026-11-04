# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Body module: a human on the whole hm08, helpers masked, macro targets as shape keys, joints following
the body."""

import importlib
import uuid

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Test human")
    obj = bpy.data.objects[result.object]
    yield result, obj
    bpy.data.objects.remove(obj)


def _shaped_coords(obj):
    """Every vertex's position with the shape keys mixed in and no modifiers — the joint cubes included, though the
    helper mask hides them from view."""
    keys = obj.data.shape_keys.key_blocks
    n = len(obj.data.vertices)
    basis = np.empty(n * 3, dtype=np.float32)
    keys[0].data.foreach_get("co", basis)
    basis = basis.reshape(-1, 3)
    mix = basis.copy()
    for key in keys[1:]:
        co = np.empty(n * 3, dtype=np.float32)
        key.data.foreach_get("co", co)
        mix += (co.reshape(-1, 3) - basis) * key.value
    return mix


def _group_mean(obj, group):
    """The mean of a vertex group's shaped positions — MPFB2's CUBE strategy for placing a joint."""
    vg = obj.vertex_groups[group].index
    indices = [v.index for v in obj.data.vertices if any(g.group == vg for g in v.groups)]
    return _shaped_coords(obj)[indices].mean(axis=0)


def test_the_whole_hm08_is_kept_and_the_helpers_masked(human):
    result, obj = human
    assert result.vertices == 19158  # helpers and joint cubes kept (item 2)
    assert obj.modifiers[build.HELPER_MASK].vertex_group == "body"
    assert len(obj.vertex_groups) == 144  # MPFB2's groups: body, helpers, joint cubes, sides


def test_a_new_human_is_smooth_as_cc5s_default(human):
    """CC5's default shows "SubD 1": the HD levels made (2), the live view at one, the film at both."""
    result, obj = human
    levels = obj.modifiers[build.LEVELS]
    assert obj.modifiers[0] == levels  # first, before the helper mask
    assert (levels.total_levels, levels.levels, levels.render_levels) == (2, 1, 2)
    assert build.visible_face_count(obj) == 13378 * 4  # the body's quads once subdivided; the helpers stay masked


def test_the_character_has_its_fields(human):
    result, obj = human
    assert uuid.UUID(result.character).version == 4
    assert obj.juststage.kind == "HUMAN"
    assert obj.juststage.base_version == build.BASE_VERSION


def test_macro_targets_are_weighted_shape_keys(human):
    result, obj = human
    keys = obj.data.shape_keys.key_blocks
    assert result.macro_targets == sum(1 for k in keys if build.is_macro_key(k.name)) > 0
    assert all(len(k.name.encode()) <= 63 for k in keys)
    name = build.makehuman.target_shapekey_name("macrodetails/universal-female-young-averagemuscle-averageweight")
    universal = keys[build.MACRO_PREFIX + name]
    assert universal.value == pytest.approx(0.5, abs=1e-3)


def test_a_standing_adult_in_metres_z_up(human):
    _, obj = human
    co = _shaped_coords(obj)[:13380]  # the body group is vertices 0–13,379
    height = co[:, 2].max() - co[:, 2].min()
    assert 1.4 < height < 2.0  # an adult, in metres, standing along Z
    assert co[:, 2].min() == pytest.approx(0.0, abs=1e-5)  # on the floor (MPFB2's feet_on_ground)


def test_joint_cubes_follow_the_body(human):
    _, obj = human
    before = _group_mean(obj, "joint-l-knee")
    build.apply_macros(
        obj,
        {
            **{k: getattr(obj.juststage, k) for k in build.makehuman.MACROS},
            **{r: getattr(obj.juststage, r) for r in build.makehuman.RACES},
            "height": 1.0,
        },
    )
    after = _group_mean(obj, "joint-l-knee")
    assert np.linalg.norm(after - before) > 0.005  # the knee's joint cube moved with the taller body


def test_bad_macro_value_is_refused():
    with pytest.raises(api.CommandError, match="gender: expected 0.0–1.0"):
        api.run("juststage.body.create", gender=1.5)


def test_operator_door_creates_a_human():
    before = set(bpy.data.objects)
    assert bpy.ops.juststage.body_create(name="Operator human") == {"FINISHED"}
    new = set(bpy.data.objects) - before
    assert len(new) == 1
    bpy.data.objects.remove(new.pop())


def test_two_hd_levels_on_the_body_only(human):
    result, obj = human
    out = api.run("juststage.body.subdivide", character=result.character, levels=2, viewport_level=2)
    assert obj.modifiers[0].name == build.LEVELS  # first, before the helper mask
    assert obj.modifiers[0].total_levels == 2
    assert out.visible_faces == 13378 * 16  # the body's quads, ×4 per level; the helpers stay masked


def test_levels_can_go_down(human):
    result, obj = human
    api.run("juststage.body.subdivide", character=result.character, levels=2, viewport_level=1)
    out = api.run("juststage.body.subdivide", character=result.character, levels=1, viewport_level=1)
    assert obj.modifiers[build.LEVELS].total_levels == 1
    assert out.visible_faces == 13378 * 4


def _basis(obj):
    co = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    obj.data.shape_keys.reference_key.data.foreach_get("co", co)
    return co.reshape(-1, 3)


def test_every_character_shares_one_rest_shape_and_stands_on_the_floor():
    """Blender's hair attachment measures from the base mesh (its rest position): one lift for every base mesh, so a
    groom made on one character fits another; each shape's own few millimetres in the floor shape key, so the feet
    stay on the floor - after a height change too."""
    made = [api.run("juststage.body.create", name=f"Floor {i}", **m) for i, m in enumerate(({}, {"height": 1.0}))]
    objs = [bpy.data.objects[m.object] for m in made]
    try:
        assert np.abs(_basis(objs[0]) - _basis(objs[1])).max() < 1e-6
        assert all(build.FLOOR in o.data.shape_keys.key_blocks for o in objs)
        for o in objs:
            assert build.shaped_coords(o)[:13380, 2].min() == pytest.approx(0.0, abs=1e-5)
        api.run("juststage.body.set_slider", character=made[0].character, slider="height", value=0.0)
        assert build.shaped_coords(objs[0])[:13380, 2].min() == pytest.approx(0.0, abs=1e-5)
        assert np.abs(_basis(objs[0]) - _basis(objs[1])).max() < 1e-6
    finally:
        for o in objs:
            bpy.data.objects.remove(o)
