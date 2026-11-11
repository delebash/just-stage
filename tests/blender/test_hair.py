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


cards = importlib.import_module("bl_ext.system.juststage.modules.hair.cards")


def _skin_top(body) -> float:
    """The evaluated skin's top (the helpers masked, the shape keys applied) - what the cards fit to; the mesh's own
    vertices hold MakeHuman's helper geometry over the scalp and no shape (the 21:57 run's first measure)."""
    dg = bpy.context.evaluated_depsgraph_get()
    mesh = body.evaluated_get(dg).to_mesh()
    top = max((body.matrix_world @ v.co).z for v in mesh.vertices)
    body.evaluated_get(dg).to_mesh_clear()
    return top


def test_a_card_hair_fits_the_cranium_rides_the_skin_and_takes_the_hair_colour(human):
    """Q-HAIR-7 (2026-11-10): MotionStudioArts' short pack on a new human - its cap's top on the head's (within 5 mm),
    bound by Surface Deform, tagged as the scalp; its colour Cycles' melanin colour over the texture's own mean."""
    made, body = human
    objects = cards.make(body, "msa_short_fuzzy", 0.8, 0.3)
    assert all(o.juststage.part == "scalp" and o.juststage.part_of == made.character for o in objects)
    assert all(o.modifiers[cards.MOD].is_bound for o in objects)
    cap = next(o for o in objects if o.get(cards.CAP_PROP))
    head_top = _skin_top(body)
    cap_top = max((cap.matrix_world @ v.co).z for v in cap.data.vertices)
    assert abs(cap_top - head_top) < 0.005
    node = cap.data.materials[0].node_tree.nodes[cards.TINT]
    want = np.array(groom.hair_colour(0.8, 0.3)) / np.array(node["mean"])
    assert np.allclose(node.outputs["Color"].default_value[:3], want, rtol=1e-4)
    api.run("juststage.hair.set_colour", groom=cap.name, melanin=0.3, redness=0.6)
    want = np.array(groom.hair_colour(0.3, 0.6)) / np.array(node["mean"])
    assert np.allclose(node.outputs["Color"].default_value[:3], want, rtol=1e-4)


def test_a_card_hair_stays_put_at_the_bodys_render_level(human):
    """The body subdivides higher for render than in the viewport; bound to the body itself the cards flew apart at
    render (2026-11-10's roll-out). Bound through the cage, the same evaluated cards at the viewport's and the
    render's level."""
    made, body = human
    objects = cards.make(body, "msa_short_fuzzy", 0.8, 0.3)
    cap = next(o for o in objects if o.get(cards.CAP_PROP))

    def evaluated():
        dg = bpy.context.evaluated_depsgraph_get()
        mesh = cap.evaluated_get(dg).to_mesh()
        co = np.array([cap.matrix_world @ v.co for v in mesh.vertices])
        cap.evaluated_get(dg).to_mesh_clear()
        return co

    before = evaluated()
    levels = next(m for m in body.modifiers if m.type in ("MULTIRES", "SUBSURF"))
    view = levels.levels
    levels.levels = levels.render_levels
    try:
        bpy.context.view_layer.update()
        after = evaluated()
    finally:
        levels.levels = view
    assert levels.render_levels != view  # the test means something only while the two levels differ
    assert np.abs(after - before).max() < 0.001
    # ...and it FOLLOWS the body (were the hidden cage not evaluated, the cards would sit still and pass the above) -
    # by height, which lifts the whole head (weight barely moves the cranium: 0.5 mm at 1.0, 2026-11-10's end run)
    api.run("juststage.body.set_slider", character=made.character, slider="height", value=1.0)
    bpy.context.view_layer.update()
    assert np.abs(evaluated() - before).max() > 0.002


def test_a_library_card_hair_refits_onto_another_character(human, tmp_path):
    """A card hair saved to the library and added to a heavier, older character lands on that cranium and binds."""
    made, body = human
    cards.make(body, "msa_short_fuzzy", 0.8, 0.3)
    out = api.run("juststage.library.save", character=made.character, catalog="Hair/Scalp", name="Card test",
                  description="test", licence="CC-BY-4.0", provenance="test", part="scalp", library=str(tmp_path))
    other = api.run("juststage.body.create", name="Card other", weight=0.9, age=0.8)
    other_body = bpy.data.objects[other.object]
    api.run("juststage.library.add", path=out.path, character=other.character)
    pieces = [o for o in bpy.data.objects if o.juststage.part_of == other.character and o.juststage.part == "scalp"]
    assert pieces and all(cards.is_cards(o) and o.modifiers[cards.MOD].is_bound for o in pieces)
    cap = next(o for o in pieces if o.get(cards.CAP_PROP))
    head_top = _skin_top(other_body)
    assert abs(max((cap.matrix_world @ v.co).z for v in cap.data.vertices) - head_top) < 0.005


def test_an_unknown_style_is_refused(human):
    result, _ = human
    with pytest.raises(api.CommandError):
        api.run("juststage.hair.add", character=result.character, style="mohawk")


def test_a_grooms_colour_changes_in_place(human):
    result, _body = human
    out = api.run("juststage.hair.add", character=result.character)
    hair = bpy.data.objects[out.groom]
    changed = api.run("juststage.hair.set_colour", groom=out.groom, melanin=0.3, redness=0.6)
    assert changed.strands == len(hair.data.curves)
    for name, want in (("melanin", 0.3), ("redness", 0.6)):
        values = np.empty(len(hair.data.curves), dtype=np.float32)
        hair.data.attributes[name].data.foreach_get("value", values)
        assert np.allclose(values, want)
    with pytest.raises(api.CommandError, match="groom"):
        api.run("juststage.hair.set_colour", groom="no such groom", melanin=0.3, redness=0.6)


def test_a_slider_moves_with_hair_on(human):
    """A groom is a part of the character too (part "scalp"), but not one of the head's fitted parts: moving a body
    slider refits the eyes and teeth and leaves the groom to its own surface deform."""
    result, body = human
    api.run("juststage.head.add_parts", character=result.character)
    api.run("juststage.hair.add", character=result.character, style="short_hedgehog")
    api.run("juststage.body.set_slider", character=result.character, slider="height", value=0.8)
    assert "scalp" not in api.run("juststage.head.add_parts", character=result.character).parts
