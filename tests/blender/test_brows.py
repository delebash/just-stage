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
    made_strands, _radii, _melanin = brows.rimmed(body)
    groom = brows.make(body)
    assert len(made_strands) == 2 * (brows.COUNT + brows.FINE)  # both brows, coarse and fine hairs, one a follicle
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


def test_brows_have_hd_aarons_grey_hairs_soft_head_and_arched_hairs(man):
    """The clean-input gate's eye view (2026-11-06): our brows a black bar with a brush of upright hairs at the head;
    HD Aaron's dark grey with about a quarter white, sparser at the head, each hair arching toward the tail."""
    _made, body = man
    found, radii, melanin = brows.strands(body, grey_share=0.22)  # a greying man's, as HD Aaron's
    melanin = np.array(melanin)
    coarse = np.arange(len(found)) % (brows.COUNT + brows.FINE) < brows.COUNT
    white = melanin[coarse] < 0.2
    assert 0.1 < white.mean() < 0.35  # white hairs among the coarse ones
    _f, _r, plain = brows.strands(body)
    assert (np.array(plain) > 0.2).all()  # by default none: greying is a character's (gate run 10 - every brow whitish)
    roots = np.array([s[0] for s in found])
    for side in (-1.0, 1.0):
        mine = roots[np.sign(roots[:, 0]) == side]
        lateral = np.abs(mine[:, 0])
        lo, hi = lateral.min(), lateral.max()
        head = (lateral < lo + 0.15 * (hi - lo)).sum()
        body_ = ((lateral > lo + 0.3 * (hi - lo)) & (lateral < lo + 0.45 * (hi - lo))).sum()
        assert head < 0.85 * body_  # the head sparser than the body (the same width of brow)
    # each hair arches: its tip's heading turned toward the tail against its root's - most where it stands up (the head)
    turned, at_head = [], []
    for s in found:
        first, last = s[1] - s[0], s[-1] - s[-2]
        side = np.sign(s[0][0])
        turned.append(side * (last[0] / np.linalg.norm(last) - first[0] / np.linalg.norm(first)))
        mine = roots[np.sign(roots[:, 0]) == side]
        lo, hi = np.abs(mine[:, 0]).min(), np.abs(mine[:, 0]).max()
        at_head.append(abs(s[0][0]) < lo + 0.15 * (hi - lo))
    turned, at_head = np.array(turned), np.array(at_head)
    assert np.mean(turned[at_head]) > 0.15  # outward (toward the tail) by the tip
    assert np.mean(turned) > 0.0  # never away from it
    assert max(r[0] for r in radii) <= 0.00004  # finer than 0.08 mm at the root


def test_brows_are_dark_brown_not_black(man):
    """Near-black brows (0.92) read as a grey bar on a woman and grey smoke at the face view (2026-11-09): every hair's
    melanin a dark brown, with redness."""
    _made, body = man
    _f, _r, melanin = brows.strands(body)
    melanin = np.array(melanin)
    assert 0.7 < np.median(melanin) < 0.88
    assert brows.REDNESS >= 0.25 and brows.FINE_MELANIN < 0.88


@pytest.mark.parametrize("gender", [1.0, 0.0])
def test_the_brows_lower_edge_sits_on_the_rim_out_of_the_blinks_reach(gender):
    """2026-11-08: MakeHuman's region put the roots on the lid's top, which the blink moves 5-12 mm, so the hairs swept
    over the closing lid. On the rim (RIM_RADII eyeball radii above each eye's centre) they stay put."""
    made, body = _human(f"Brow rim {gender}", gender=gender)
    try:
        api.run("juststage.head.add_parts", character=made.character)
        api.run("juststage.head.add_face_units", character=made.character)
        eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
        parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
        found, _r, _m = brows.rimmed(body)
        roots = np.array([s[0] for s in found])
        for name in ("eyeLeft", "eyeRight"):
            centre, radius = eye_layers._eye_sphere(parts.parts_of(body)[name])
            heights = roots[np.sign(roots[:, 0]) == np.sign(centre[0]), 2] - centre[2]
            assert np.percentile(heights, 10) >= brows.RIM_RADII * radius - brows.RIM_TOLERANCE - 1e-4, (name, radius)
        groom = brows.make(body)
        before = _evaluated(groom).reshape(-1, brows.POINTS, 3)  # the hairs kept (a woman's DENSITY_BY_SEX share)
        keys = body.data.shape_keys.key_blocks
        keys["eyeBlinkLeft"].value = keys["eyeBlinkRight"].value = 1.0
        bpy.context.view_layer.update()
        after = _evaluated(groom).reshape(-1, brows.POINTS, 3)  # the same ones (culled by index)
        swept = np.linalg.norm(after[:, -1] - before[:, -1], axis=1) > 0.002
        assert swept.mean() < 0.02, swept.mean()  # the blink leaves the brows: a few hairs at most
    finally:
        _remove(made)


def test_a_womans_brows_are_sparser_and_follow_the_gender_slider():
    """Women's brows sparser (DENSITY_BY_SEX: 0.7 read the most natural on the Average woman, 2026-11-09), culled
    live - a gender drag changes the share kept, nothing regrown."""
    groom = importlib.import_module("bl_ext.system.juststage.modules.hair.groom")
    made, body = _human("Brow density", gender=0.0)
    try:
        obj = brows.make(body)
        total = len(obj.data.curves)
        assert groom.evaluated_curve_count(obj) / total == pytest.approx(brows.DENSITY_BY_SEX[0], abs=0.03)
        api.run("juststage.body.set_slider", character=made.character, slider="gender", value=1.0)
        assert groom.evaluated_curve_count(obj) / total == pytest.approx(1.0, abs=0.01)
        assert len(obj.data.curves) == total  # the same groom, culled - not regrown
        assert obj.modifiers[0].name == brows.DENSITY_MODIFIER  # before the surface deform
    finally:
        _remove(made)


def test_the_brows_thin_toward_their_edges(man):
    """Roots even across the band gave hard edges - a block beside HD Aaron's soft brows (2026-11-09): a bell
    (EDGE_SD). The sampler: none below the band (the lid the blink moves) or past EDGE_ABOVE, the middle third denser
    than an even spread's; each brow: more of its roots near its own middle line than with the even spread (measured
    2026-11-09: 0.49 / 0.45 against 0.43 / 0.42)."""
    rng = np.random.default_rng(0)
    t = np.array([brows._across(rng) for _ in range(20000)])
    assert t.min() >= -1.0 and t.max() <= brows.EDGE_ABOVE
    assert np.mean(np.abs(t) < 1 / 3) > 0.42  # even over [-1, 1]: 0.33
    _made, body = man

    def near_middle(found):
        roots = np.array([s[0] for s in found])
        out = []
        for side in (-1.0, 1.0):
            mine = roots[np.sign(roots[:, 0]) == side]
            lateral = np.abs(mine[:, 0])
            lo_l, hi_l = np.quantile(lateral, [0.25, 0.65])
            part = mine[(lateral > lo_l) & (lateral < hi_l)]
            place = np.clip(np.digitize(np.abs(part[:, 0]), np.linspace(lo_l, hi_l, 9)) - 1, 0, 7)
            off = np.empty(len(part))
            for b in range(8):  # height off the band's own middle at its place (the arch out)
                off[place == b] = part[place == b, 2] - np.median(part[place == b, 2])
            lo, hi = np.quantile(off, [0.02, 0.98])
            out.append(np.mean(np.abs(off - (lo + hi) / 2) < (hi - lo) / 6))
        return np.array(out)

    bell = near_middle(brows.strands(body)[0])
    old = brows.EDGE_SD
    brows.EDGE_SD = None
    try:
        even = near_middle(brows.strands(body)[0])
    finally:
        brows.EDGE_SD = old
    assert (bell > even + 0.02).all(), (bell, even)
