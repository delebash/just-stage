# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's stubble (modules/hair/stubble.py) - CC5's way: stubble is hair geometry (HD Aaron's `Stubble` mesh),
never paint (docs/plans/2026-11-06-inputs-audit.md row 4)."""

import importlib

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
stubble = importlib.import_module("bl_ext.system.juststage.modules.hair.stubble")
groom = importlib.import_module("bl_ext.system.juststage.modules.hair.groom")
parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")


@pytest.fixture
def man():
    made = api.run("juststage.body.create", name="Stubble test", gender=1.0)
    api.run("juststage.head.add_parts", character=made.character)
    body = bpy.data.objects[made.object]
    yield made, body
    for o in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(o)
    bpy.data.objects.remove(body)


def _world_points(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    curves = obj.evaluated_get(depsgraph).data
    pos = np.empty(len(curves.points) * 3, np.float32)
    curves.attributes["position"].data.foreach_get("vector", pos)
    pos = pos.reshape(len(curves.curves), -1, 3)
    m = np.array(obj.matrix_world)
    return pos @ m[:3, :3].T + m[:3, 3]


def test_stubble_is_short_hair_on_the_beard_not_on_the_lips_or_nose(man):
    made, body = man
    obj = stubble.make(body)
    assert obj in groom.of_part(body, "beard")
    pts = _world_points(obj)
    n = len(pts)
    assert 4000 < n < 40000  # ~60 a cm2 over the beard's ~150-300 cm2
    length = np.linalg.norm(np.diff(pts, axis=1), axis=2).sum(axis=1) * 1000
    assert 2.5 < np.median(length) < 4.5  # mm: HD Aaron's Stubble at the gate's cheek view, 2.4-4.2 (2026-11-06)
    roots = pts[:, 0]
    eyes = [eye_layers._eye_sphere(parts.parts_of(body)[p])[0] for p in ("eyeLeft", "eyeRight")]
    mid = (eyes[0] + eyes[1]) / 2
    rel = roots - mid
    assert (rel[:, 2] < -0.025).all()  # all below the eyes' level by the cheekbones
    # a neckline as HD Aaron's: none down the throat (run 7 had them to the collarbones) - under the chin no lower than
    # 15.5 cm below the eyes, rising toward the jaw's angle behind it
    assert (rel[:, 2] > -0.155 + 0.7 * np.clip(rel[:, 1] - 0.03, 0.0, None) - 0.003).all()
    lips = stubble.lip_points(body)
    near_lips = np.linalg.norm(roots[:, None] - lips[None, ::20], axis=2).min(axis=1) < 0.0015
    assert near_lips.mean() < 0.01  # none on the lips
    # every root on the skin
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    inv = np.array(body.matrix_world.inverted())
    gaps = [tree.find_nearest(Vector(inv[:3, :3] @ r + inv[:3, 3]))[3] for r in roots[::50]]
    assert max(gaps) < 0.0003


def test_stubble_grows_in_patches_not_an_even_mat(man):
    """An even density read as a uniform mat beside HD Aaron's patchy stubble (2026-11-09): with PATCHY the hairs per
    2 cm cell, over the same cells of an even run (the beard region's own fall-off cancels), vary well beyond what two
    even runs with different seeds differ by (chance)."""
    _made, body = man

    def cells(patchy, seed):
        old = stubble.PATCHY
        stubble.PATCHY = patchy
        try:
            roots = np.array([s[0] for s in stubble.strands(body, seed=seed)[0]])
        finally:
            stubble.PATCHY = old
        keys, counts = np.unique(np.floor(roots[:, [0, 2]] / 0.02).astype(int), axis=0, return_counts=True)
        return {tuple(k): c for k, c in zip(keys, counts, strict=True)}

    even, other, patchy = cells(0.0, 5), cells(0.0, 6), cells(stubble.PATCHY, 5)
    full = [k for k, c in even.items() if c >= 30]  # cells well inside the beard

    def spread(run):
        ratio = np.array([run.get(k, 0) / even[k] for k in full])
        return ratio.std()

    assert stubble.PATCHY > 0 and len(full) > 20
    assert spread(patchy) > 2.0 * spread(other), (spread(patchy), spread(other))
