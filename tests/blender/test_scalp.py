# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's scalp grooms (modules/hair/scalp.py, rec 11): guides combed over the scalp, filled by Blender's
Interpolate Hair Curves, every strand on the head and coloured by the groom's own melanin."""

import importlib

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

api = importlib.import_module("bl_ext.system.juststage.api")
scalp = importlib.import_module("bl_ext.system.juststage.modules.hair.scalp")


def test_a_combed_groom_covers_the_scalp_and_takes_the_groom_colour():
    made = api.run("juststage.body.create", name="Scalp test", gender=1.0)
    body = bpy.data.objects[made.object]
    try:
        groom = scalp.make(body)
        assert groom.juststage.part == "scalp" and groom.data.surface == body
        depsgraph = bpy.context.evaluated_depsgraph_get()
        curves = groom.evaluated_get(depsgraph).data
        assert len(curves.curves) > 50_000  # filled to density (the guides alone are ~1,500)
        first = np.array([c.first_point_index for c in curves.curves])
        pos = np.empty(len(curves.points) * 3, np.float32)
        curves.attributes["position"].data.foreach_get("vector", pos)
        mw = np.array(groom.matrix_world)
        roots = pos.reshape(-1, 3)[first] @ mw[:3, :3].T + mw[:3, 3]
        mesh = body.evaluated_get(depsgraph).to_mesh()
        try:
            mesh.transform(body.matrix_world)
            tree = BVHTree.FromPolygons([v.co.copy() for v in mesh.vertices], [list(p.vertices) for p in mesh.polygons])
        finally:
            body.evaluated_get(depsgraph).to_mesh_clear()
        sample = roots[:: max(1, len(roots) // 2000)]
        d = np.array([tree.find_nearest(Vector(r))[3] for r in sample])
        assert np.median(d) < 0.001, np.median(d)  # on the body, not on its rest shape 0.8 m below (the first stack)
        assert np.percentile(sample[:, 2], 5) > 1.4  # on the head
        # none on the body: the nape's roots reach ~0.17 m below the median root, strays rooted on the body through the
        # mask's UV bleed lay 0.31 m and more below it (2% of the strands, 2026-11-07)
        low = int((roots[:, 2] < np.median(roots[:, 2]) - 0.25).sum())
        assert low == 0, f"{low} strands rooted below the head"
        melanin = np.empty(len(curves.curves), np.float32)
        curves.attributes["melanin"].data.foreach_get("value", melanin)
        assert abs(np.median(melanin) - scalp.MELANIN) < 0.05 and (melanin < 0.2).mean() > 0.1  # its own, some grey
    finally:
        for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
            bpy.data.objects.remove(obj)
        bpy.data.objects.remove(body)


class _BackField:
    """A constant cut: 30 mm long, tips 5 mm off, every strand combed straight back (+Y)."""

    def length(self, p):
        return 0.03

    def lift(self, p):
        return 0.005

    def direction(self, p):
        return np.array([0.0, 1.0, 0.0])


def test_a_style_with_a_field_grows_its_guides_along_it():
    """A cut measured or designed as a field (scalp.guides' "field", 2026-11-07 late): each guide takes the field's
    length and runs its way - the feasibility test grows our own guides along a reference cut's field."""
    made = api.run("juststage.body.create", name="Scalp field test", gender=1.0)
    body = bpy.data.objects[made.object]
    try:
        style = {**scalp.SHORT_TAPER, "field": _BackField(), "guides": 400}
        found = scalp.guides(body, style)
        assert 300 <= len(found) <= 400
        length = np.array([np.linalg.norm(np.diff(s, axis=0), axis=1).sum() for s in found])
        assert 0.025 < np.median(length) < 0.045, np.median(length)  # 30 mm along the scalp, its lift added
        run = np.array([s[-1] - s[0] for s in found])
        on_top = np.array([s[0][2] for s in found]) > np.median([s[0][2] for s in found])
        assert np.median(run[on_top, 1]) > 0.01  # on top, combed back (+Y)
    finally:
        cid = body.juststage.character_id
        for o in [o for o in bpy.data.objects if o.juststage.part_of == cid]:
            bpy.data.objects.remove(o)
        bpy.data.objects.remove(body)
