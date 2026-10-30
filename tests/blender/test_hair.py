# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Hair module: MakeHuman's CC0 hair styles, attached to the body the way MPFB2's hair editor attaches them."""

import importlib

import bpy
import numpy as np
import pytest
from mathutils import Vector
from mathutils.bvhtree import BVHTree

api = importlib.import_module("bl_ext.system.juststage.api")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
groom = importlib.import_module("bl_ext.system.juststage.modules.hair.groom")
styles = importlib.import_module("bl_ext.system.juststage.modules.hair.styles")
makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
paths = importlib.import_module("bl_ext.system.juststage.paths")


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Hair test")
    yield result, bpy.data.objects[result.object]
    for obj in list(bpy.data.objects[result.object].children):
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(bpy.data.objects[result.object])


def _root_to_skin(hair, body):
    """Each strand root's distance to the body's skin (the evaluated, masked body), in metres."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    curves = hair.evaluated_get(depsgraph).data
    pos = np.empty(len(curves.points) * 3, dtype=np.float32)
    curves.attributes["position"].data.foreach_get("vector", pos)
    roots = pos.reshape(-1, 3)[[c.first_point_index for c in curves.curves]]
    roots = (np.array(hair.matrix_world) @ np.c_[roots, np.ones(len(roots))].T).T[:, :3]
    evaluated = body.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.transform(body.matrix_world)
        tree = BVHTree.FromPolygons([v.co.copy() for v in mesh.vertices], [list(p.vertices) for p in mesh.polygons])
    finally:
        evaluated.to_mesh_clear()
    return np.array([tree.find_nearest(Vector(r))[3] for r in roots[:: max(1, len(roots) // 2000)]])


def test_every_style_is_in_the_pack():
    with bpy.data.libraries.load(str(paths.makehuman(*groom.PACK))) as (src, _):
        names = set(src.objects)
    assert set(styles.STYLES) <= names


def test_every_style_roots_on_the_skin(human):
    result, body = human
    for style, (kind, _) in styles.STYLES.items():
        out = api.run("juststage.hair.add", character=result.character, style=style)
        hair = bpy.data.objects[out.groom]
        assert out.groom_type == kind == hair.juststage.part
        assert hair.parent == body and hair.data.surface == body
        assert hair.juststage.part_of == body.juststage.character_id
        if style == "empty_hair":  # MPFB2's template for grooming by hand
            assert out.strands == 0
            continue
        assert out.strands > 0
        d = _root_to_skin(hair, body)
        # measured on hm08 2026-10-29: medians 0.1–1.4 mm, the 95th percentile at most 3.8 mm (the beards)
        assert np.median(d) < 0.002 and np.percentile(d, 95) < 0.005, (style, np.median(d), np.percentile(d, 95))


def test_hair_follows_the_body_shape(human):
    result, body = human
    out = api.run("juststage.hair.add", character=result.character, style="short_hedgehog")
    hair = bpy.data.objects[out.groom]
    now = {k: getattr(body.juststage, k) for k in (*makehuman.MACROS, *makehuman.RACES)}
    build.apply_macros(body, {**now, "age": 0.0})  # a baby's head is another size and place
    d = _root_to_skin(hair, body)
    assert np.median(d) < 0.002 and np.percentile(d, 95) < 0.005


def test_hair_colour_is_melanin_per_strand(human):
    result, _ = human
    out = api.run("juststage.hair.add", character=result.character, style="short_cap", melanin=0.3, redness=0.6)
    hair = bpy.data.objects[out.groom]
    evaluated = hair.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    for name, value in (("melanin", 0.3), ("redness", 0.6)):
        values = np.empty(len(evaluated.curves), dtype=np.float32)
        evaluated.attributes[name].data.foreach_get("value", values)
        assert np.allclose(values, value)  # it reaches the strands the style's node groups make
    (material,) = hair.data.materials
    nodes = material.node_tree.nodes
    (bsdf,) = [n for n in nodes if n.type == "BSDF_HAIR_PRINCIPLED"]
    assert bsdf.parametrization == "MELANIN"
    assert {n.attribute_name for n in nodes if n.type == "ATTRIBUTE"} == {"melanin", "redness"}
    assert "short_cap" not in bpy.data.materials  # the style's own material is dropped


def test_an_unknown_style_is_refused(human):
    result, _ = human
    with pytest.raises(api.CommandError):
        api.run("juststage.hair.add", character=result.character, style="mohawk")
