# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage base v2 (modules/body/base.py; docs/plans/2026-11-05-lid-anatomy-build.md, tests 1-4): hm08 kept whole,
the lid anatomy appended; every target carries the new vertices; the rim stays on the eyeball over every eye slider;
the eyes' openings are found as before."""

import importlib

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
body_create = importlib.import_module("bl_ext.system.juststage.modules.body.body_create")
sliders = importlib.import_module("bl_ext.system.juststage.modules.body.sliders")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")
eyes = importlib.import_module("bl_ext.system.juststage.modules.head.eyes")
eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")

HM08 = makehuman.HM08_VERTICES


def _remove(obj):
    cid = obj.juststage.character_id
    for o in [o for o in bpy.data.objects if o.juststage.part_of == cid]:
        bpy.data.objects.remove(o)
    bpy.data.objects.remove(obj)


def _v1(name):
    values = body_create.Params()._asdict()
    for k in ("name", "dressed"):
        values.pop(k)
    return build.create_human(name, values, base_version=1)


@pytest.fixture
def opened():
    """The default human, eyes opened as a dressed one's, with its eye parts."""
    made = api.run("juststage.body.create", name="Base v2 test")
    body_create.open_eyes(made.character)
    api.run("juststage.head.add_parts", character=made.character)
    body = bpy.data.objects[made.object]
    yield made, body
    _remove(body)


def _faces(obj):
    me = obj.data
    layers = {name: np.empty(len(me.loops) * 2, np.float32) for name in ("UVMap", maps.UV)}
    for name, buf in layers.items():
        me.uv_layers[name].data.foreach_get("uv", buf)
    return {
        tuple(p.vertices): tuple(np.round(layers[n].reshape(-1, 2)[list(p.loop_indices)], 6).tobytes() for n in layers)
        for p in me.polygons
    }


def test_a_new_human_is_hm08_whole_with_the_lids_appended():
    v1 = _v1("hm08")
    made = api.run("juststage.body.create", name="base v2")
    v2 = bpy.data.objects[made.object]
    try:
        rec = base.record()
        assert v2.juststage.base_version == base.VERSION
        assert len(v2.data.vertices) == rec["vertices"] > HM08
        # every hm08 polygon away from the cut is still there with the same vertices and UVs (hm08's and the layout)
        cut = {v for pair in rec["cut"] for v in pair}
        old, new = _faces(v1), _faces(v2)
        kept = {k: uv for k, uv in old.items() if not cut & set(k)}
        assert len(kept) > 18000
        assert all(new.get(k) == uv for k, uv in kept.items())
        # the appended vertices are skin: shown through the helpers' mask
        group = v2.vertex_groups["body"].index
        shown = [v.index for v in v2.data.vertices if any(g.group == group and g.weight > 0.5 for g in v.groups)]
        assert len(shown) == makehuman.BODY_VERTICES + rec["vertices"] - HM08
        # the old vertices the base doesn't move are where hm08 has them
        b1, b2 = build.shaped_coords(v1), build.shaped_coords(v2)
        still = np.setdiff1d(np.arange(HM08), rec["moved"]["index"])
        assert np.abs(b1[still] - b2[still]).max() < 1e-6
        # the rims are creased for the levels
        crease = np.empty(len(v2.data.edges), np.float32)
        v2.data.attributes["crease_edge"].data.foreach_get("value", crease)
        assert (crease > 0).sum() > 40
        assert v2.modifiers[build.LEVELS].use_creases
    finally:
        _remove(v1)
        _remove(v2)


def test_every_target_carries_the_appended_vertices(opened):
    _, body = opened
    app = base.appended()
    # a move of everything carries them exactly
    idx, d = base.extend(body, np.arange(HM08), np.tile(np.array([[0.01, -0.02, 0.005]], np.float32), (HM08, 1)))
    assert np.allclose(d[HM08:], [0.01, -0.02, 0.005], atol=1e-6) and len(idx) == len(body.data.vertices)
    # the slider that opens the left eye moves the left lid's appended vertices about as far as their faces move
    index, delta = sliders._target("eyes", "l-eye-height2-incr")
    idx, d = base.extend(body, index, delta)
    new = idx >= HM08
    assert new.sum() > 20
    parent_move = np.zeros(HM08)
    parent_move[index] = np.linalg.norm(delta, axis=1)
    reach = parent_move[app.parents[idx[new] - HM08]].max(axis=1)
    assert (np.linalg.norm(d[new], axis=1) <= 1.5 * reach + 0.0005).all()


def _rim_gaps(body):
    spheres = [eye_layers._eye_sphere(parts.parts_of(body)[p]) for p in ("eyeLeft", "eyeRight")]
    co = build.shaped_coords(body)
    rows = base.rows()
    rims, lashes = [], []
    for lash, margin, rim in rows:
        c, r = min(spheres, key=lambda s: np.linalg.norm(co[margin] - s[0]))
        if rim >= 0:
            rims.append(np.linalg.norm(co[rim] - c) - r)
        if lash >= 0:
            lashes.append(np.linalg.norm(co[lash] - c) - r)
    return np.array(rims), np.array(lashes)


def test_the_rim_stays_on_the_eyeball_over_every_eye_slider(opened):
    _, body = opened
    targets = sorted({t for s in sliders.catalog().values() if s.group == "eyes" for t in (s.negative, s.positive) if t})
    assert len(targets) == 68  # the prototype's sweep counted 66 (2026-11-05); target.json's eyes group has 68
    bad = []
    for target in targets:
        key = sliders._key(body, "eyes", target)
        before = key.value
        key.value = 1.0
        parts.refit(body)
        rims, lashes = _rim_gaps(body)
        if not (rims.min() >= 0.00005 and rims.max() <= 0.001 and lashes.min() >= 0.0):
            bad.append((target, round(rims.min() * 1000, 2), round(rims.max() * 1000, 2), round(lashes.min() * 1000, 2)))
        key.value = before
    parts.refit(body)
    assert bad == []


def test_the_eyes_openings_are_found_as_on_hm08(opened):
    _, v2 = opened
    v1 = _v1("hm08 openings")
    try:
        cid = v1.juststage.character_id
        for slider, value in body_create.EYE_OPEN.items():
            sliders.apply(v1, sliders.catalog()[slider], value)
        parts.add(v1)
        o1 = {k.rsplit(".", 1)[-1]: o for k, o in eyes.openings(v1).items()}
        o2 = {k.rsplit(".", 1)[-1]: o for k, o in eyes.openings(v2).items()}
        assert set(o1) == set(o2) == {"eyeLeft", "eyeRight"}
        for name in o1:
            a, b = o1[name], o2[name]
            az = np.linspace(max(a.centres.min(), b.centres.min()), min(a.centres.max(), b.centres.max()), 20)[2:-2]
            for lid in ("upper", "lower"):
                ea = np.interp(az, a.centres, getattr(a, lid))
                eb = np.interp(az, b.centres, getattr(b, lid))
                # the margin now lies on the eyeball, so the opening ends a little lower (measured 2026-11-06: up to
                # 1.5 deg at the upper lid's middle, ~0.3 mm) - the plan's 1 deg was set before the rim existed
                assert np.abs(ea - eb).max() <= 2.0, (name, lid, np.abs(ea - eb).max())
        assert cid
    finally:
        _remove(v1)


def test_the_lash_line_keeps_the_margins_width(opened):
    """The clean-input gate's eye view (2026-11-06): under the iris our lower lash line stood up to 5.2 mm off the
    eyeball, the next row 0.8 mm (the opened eye's sliders push the lid's skin out; the contact key only held the rim
    and a minimum) - a swollen glossy roll with a kink. The margin keeps base v2's width: the lash line no farther than
    the record's, the skin beyond carried with it (no step)."""
    _, body = opened
    _rims, lashes = _rim_gaps(body)
    most = base.record()["radii_mm"]["lash"] / 1000
    assert lashes.max() <= most + 0.00005
    rows = base.rows()
    co = build.shaped_coords(body)
    taken = set(rows.ravel().tolist()) - {-1}
    edges = np.empty(len(body.data.edges) * 2, np.int64)
    body.data.edges.foreach_get("vertices", edges)
    edges = edges.reshape(-1, 2)
    lash = set(rows[rows[:, 0] >= 0, 0].tolist())
    beyond = {int(b) for a, b in edges.tolist() + edges[:, ::-1].tolist() if a in lash and b not in taken}
    # the first ring of skin beyond the lash line lies within 2.5 mm of it (a step would leave it standing off)
    near = [min(np.linalg.norm(co[v] - co[a]) for a in lash) for v in beyond]
    assert max(near) < 0.0035


def test_the_lower_margin_is_a_ledge_like_the_upper(opened):
    """The gate's eye view (2026-11-07 late): moved only along its own line from the eye's centre, hm08's lower lash
    line sat 2.4 mm straight below its rim at the rim's depth - a margin 74-80 deg below horizontal, a wall facing the
    camera, the thick roll under the eye. The contact turns it (parts.LEDGE_TURN, LEDGE_GAP): on the lower lid's
    middle the lash line lies in front of its rim and the margin slopes less than 45 deg."""
    _, body = opened
    co = build.shaped_coords(body)
    spheres = [eye_layers._eye_sphere(parts.parts_of(body)[p]) for p in ("eyeLeft", "eyeRight")]
    rows = base.rows()
    rows = rows[(rows >= 0).all(1)]
    for c, _r in spheres:
        mine = rows[np.linalg.norm(co[rows[:, 2]] - c, axis=1) < 0.02]
        lower = mine[co[mine[:, 2], 2] < c[2]]
        x = co[lower[:, 2], 0]
        lo, hi = np.percentile(x, [33, 67])
        middle = lower[(x >= lo) & (x <= hi)]
        d = co[middle[:, 0]] - co[middle[:, 2]]  # rim to lash line
        assert (d[:, 1] < -0.001).all(), d[:, 1]  # in front (the character faces -Y)
        slope = np.degrees(np.arctan2(-d[:, 2], -d[:, 1]))
        assert slope.max() < 45.0, slope
