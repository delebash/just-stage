# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's lashes (modules/hair/lashes.py): real counts along the lids, attached to the body like every groom, so
they land where they were made and follow another character's lids."""

import importlib

import bpy
import numpy as np
import pytest
from mathutils import Vector
from mathutils.bvhtree import BVHTree

api = importlib.import_module("bl_ext.system.juststage.api")
lashes = importlib.import_module("bl_ext.system.juststage.modules.hair.lashes")
eyes = importlib.import_module("bl_ext.system.juststage.modules.head.eyes")


def _human(name, **macros):
    made = api.run("juststage.body.create", name=name, **macros)
    api.run("juststage.head.add_parts", character=made.character)
    return made, bpy.data.objects[made.object]


def _remove(made):
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(bpy.data.objects[made.object])


@pytest.fixture
def woman():
    made, body = _human("Lash test", gender=0.0)
    yield made, body
    _remove(made)


def _evaluated(obj) -> np.ndarray:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    curves = obj.evaluated_get(depsgraph).data
    pos = np.empty(len(curves.points) * 3, np.float32)
    curves.attributes["position"].data.foreach_get("vector", pos)
    pos = pos.reshape(-1, 3)
    return pos @ np.array(obj.matrix_world)[:3, :3].T + np.array(obj.matrix_world)[:3, 3]


def test_lashes_land_where_they_were_made(woman):
    made, body = woman
    openings = eyes.openings(body)
    made_strands, _radii, _melanin, missed = lashes.strands(body, openings)
    groom = lashes.make(body, openings)
    assert missed == 0 and len(made_strands) == 2 * (lashes.UPPER["count"] + lashes.LOWER["count"])
    assert groom.parent == body and groom.data.surface == body and groom.juststage.part == "eyelashes"
    assert groom.juststage.part_of == made.character
    # through rest space and back by Blender's Deform Curves on Surface: within 0.05 mm
    gap = np.linalg.norm(_evaluated(groom) - np.concatenate(made_strands), axis=1)
    assert gap.max() < 0.00005, gap.max()


def test_lashes_follow_another_characters_lids(woman, tmp_path):
    made, body = woman
    lashes.make(body)
    saved = api.run("juststage.library.save", character=made.character, catalog="Hair/Lashes", name="Lashes",
                    licence="CC0-1.0", provenance="JustStage lashes", library=str(tmp_path))  # fmt: skip
    other, other_body = _human("Lash other", gender=1.0, age=0.9, weight=0.8)
    try:
        added = api.run("juststage.library.add", path=saved.path, character=other.character)
        groom = bpy.data.objects[added.object]
        points = _evaluated(groom)
        roots = points[:: lashes.POINTS]
        depsgraph = bpy.context.evaluated_depsgraph_get()
        mesh = other_body.evaluated_get(depsgraph).to_mesh()
        try:
            mesh.transform(other_body.matrix_world)
            tree = BVHTree.FromPolygons([v.co.copy() for v in mesh.vertices], [list(p.vertices) for p in mesh.polygons])
        finally:
            other_body.evaluated_get(depsgraph).to_mesh_clear()
        d = np.array([tree.find_nearest(Vector(r))[3] for r in roots])
        assert np.median(d) < 0.0003 and d.max() < 0.001, (np.median(d), d.max())
        # and at its eyes: every root within 2 cm of an eyeball's centre
        centres = [o.centre for o in eyes.openings(other_body).values()]
        near = np.min([np.linalg.norm(roots - c, axis=1) for c in centres], axis=0)
        assert near.max() < 0.02, near.max()
    finally:
        _remove(other)
