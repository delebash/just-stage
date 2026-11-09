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


def test_upper_lashes_fan_without_spikes_or_tight_clumps(woman):
    """The clean-input gate's eye view (2026-11-06): our upper lashes read as spiky clumps with a few standing straight up
    - HD Aaron's a fringe of single lashes curving up and out. Few rise past 60 degrees root to tip, and a clump's tips
    stay most of their roots' spacing apart."""
    made, body = woman
    importlib.import_module("bl_ext.system.juststage.modules.body.body_create").open_eyes(made.character)
    found, _radii, _melanin, _missed = lashes.strands(body, eyes.openings(body))
    per_eye = lashes.UPPER["count"] + lashes.LOWER["count"]
    upper = [s for k, s in enumerate(found) if k % per_eye < lashes.UPPER["count"]]
    d = np.array([s[-1] - s[0] for s in upper])
    rise = np.degrees(np.arcsin(d[:, 2] / np.linalg.norm(d, axis=1)))
    assert (rise > 60).mean() < 0.03, (rise > 60).mean()
    roots = np.array([s[0] for s in upper])
    tips = np.array([s[-1] for s in upper])
    gaps_root = np.linalg.norm(np.diff(roots, axis=0), axis=1)
    gaps_tip = np.linalg.norm(np.diff(tips, axis=0), axis=1)
    keep = gaps_root < 0.002  # neighbours along one lid
    assert np.median(gaps_tip[keep]) > 0.75 * np.median(gaps_root[keep]), (np.median(gaps_tip[keep]), np.median(gaps_root[keep]))


def test_the_upper_lashes_curve_smoothly_out_of_the_lid(woman):
    """No kinked wire: a lash that runs into its lid is turned whole, not bent at every joint (2026-11-08: joints up to
    180 deg, 68% of the lashes over 20 - against a smooth curl's ~5 deg a joint). Measured after: 3% on the New human,
    7.5% on this woman - the target (under 5%) is open (the own-content proof's working doc); this guards the gain."""
    _made, body = woman
    made_strands, _radii, _melanin, _missed = lashes.strands(body, eyes.openings(body))
    per = lashes.UPPER["count"] + lashes.LOWER["count"]
    upper = [s for e in range(len(made_strands) // per) for s in made_strands[e * per:e * per + lashes.UPPER["count"]]]
    sharpest = []
    for s in upper:
        seg = np.diff(np.asarray(s), axis=0)
        seg /= np.linalg.norm(seg, axis=1, keepdims=True)
        sharpest.append(np.degrees(np.arccos(np.clip((seg[1:] * seg[:-1]).sum(1), -1.0, 1.0))).max())
    sharpest = np.array(sharpest)
    assert np.percentile(sharpest, 90) < 15.0, np.percentile(sharpest, 90)
    assert (sharpest > 20.0).mean() < 0.10, (sharpest > 20.0).mean()
