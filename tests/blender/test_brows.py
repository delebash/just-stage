# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's brows (modules/hair/brows.py, rec 8): one hair per follicle over each brow's band, flowing upward at
its head and along it by its tail, attached to the body like every groom."""

import importlib

import bpy
import numpy as np
import pytest
from mathutils import Vector
from mathutils.bvhtree import BVHTree

api = importlib.import_module("bl_ext.system.juststage.api")
brows = importlib.import_module("bl_ext.system.juststage.modules.hair.brows")


def _human(name, **macros):
    made = api.run("juststage.body.create", name=name, **macros)
    return made, bpy.data.objects[made.object]


def _remove(made):
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(bpy.data.objects[made.object])


@pytest.fixture
def man():
    made, body = _human("Brow test", gender=1.0)
    yield made, body
    _remove(made)


def _evaluated(obj) -> np.ndarray:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    curves = obj.evaluated_get(depsgraph).data
    pos = np.empty(len(curves.points) * 3, np.float32)
    curves.attributes["position"].data.foreach_get("vector", pos)
    pos = pos.reshape(-1, 3)
    return pos @ np.array(obj.matrix_world)[:3, :3].T + np.array(obj.matrix_world)[:3, 3]


def test_brows_are_single_hairs_flowing_from_head_to_tail(man):
    made, body = man
    made_strands, _radii, _melanin = brows.strands(body)
    groom = brows.make(body)
    assert len(made_strands) == 2 * brows.COUNT  # both brows, one hair per follicle (no duplicated tufts)
    assert groom.parent == body and groom.data.surface == body and groom.juststage.part == "eyebrows"
    gap = np.linalg.norm(_evaluated(groom) - np.concatenate(made_strands), axis=1)
    assert gap.max() < 0.00005, gap.max()  # through rest space and back: where they were made
    strands = np.array(made_strands)
    roots, tips = strands[:, 0], strands[:, -1]
    for side in (-1.0, 1.0):
        on = np.sign(roots[:, 0]) == side
        lateral = np.abs(roots[on, 0])
        heading = tips[on] - roots[on]
        rising = heading[:, 2] / np.linalg.norm(heading, axis=1)
        head, tail = lateral < np.quantile(lateral, 0.15), lateral > np.quantile(lateral, 0.85)
        assert rising[head].mean() > rising[tail].mean() + 0.3  # upward at the head, along the brow at the tail


def test_brows_follow_another_characters_face(man, tmp_path):
    made, body = man
    brows.make(body)
    saved = api.run("juststage.library.save", character=made.character, catalog="Hair/Brows", name="Brows",
                    licence="CC0-1.0", provenance="JustStage brows", library=str(tmp_path))  # fmt: skip
    other, other_body = _human("Brow other", gender=0.0, age=0.9, weight=0.8)
    try:
        added = api.run("juststage.library.add", path=saved.path, character=other.character)
        roots = _evaluated(bpy.data.objects[added.object])[:: brows.POINTS]
        depsgraph = bpy.context.evaluated_depsgraph_get()
        mesh = other_body.evaluated_get(depsgraph).to_mesh()
        try:
            mesh.transform(other_body.matrix_world)
            tree = BVHTree.FromPolygons([v.co.copy() for v in mesh.vertices], [list(p.vertices) for p in mesh.polygons])
        finally:
            other_body.evaluated_get(depsgraph).to_mesh_clear()
        d = np.array([tree.find_nearest(Vector(r))[3] for r in roots])
        assert np.median(d) < 0.0003 and d.max() < 0.001, (np.median(d), d.max())
    finally:
        _remove(other)
