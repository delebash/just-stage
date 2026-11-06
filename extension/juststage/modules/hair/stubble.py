# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's stubble: short hairs over the beard, as geometry - CC5's way (HD Aaron's `Stubble` is a hair mesh over
a faint shaved tint in his skin; docs/plans/2026-11-06-inputs-audit.md row 4: ours had the scans' stubble painted in).
The approved method (the realism review's rec 9, 2026-11-04): a density over the beard's region with a growth
direction, a length per style; 1-3 mm strands. The faint shaved tint stays in the skin (tools/face_test/skin_base.py
`beard_shadow`), the hairs are these.

- **Where:** the beard's region measured from the eyes on the character's own shape - the skin composer's (`skin_base
  .regions`: ahead of the ears, from 3.5-5 cm below the eyes' level down the throat to 19-22 cm, within 7-9 cm of the
  middle, soft-edged) - less the lips (MakeHuman's CC0 lips mask, `mpfb_lips.jpg`) and the nose; a root whose outward
  ray meets the body again within CAVITY is inside the mouth or a nostril and is dropped.
- **How many:** DENSITY a square centimetre over the region (snippet-level figures for beard density, to be checked
  against scan photos - rec 9's attack), each triangle's share by its area and its mean weight.
- **Which way:** down and back over the face and neck (GROWTH: under the chin that is toward the throat), flaring
  out over the cheeks (FLARE), each hair SPREAD degrees its own; leaving the skin at RISE, lying to half that at the tip.
- **How long, how thick:** LENGTH mm (two or three days' growth), +-30%; RADIUS at the root, cut blunt (TIP).
Attached as the lashes are (lashes.py: rest shape, surface UVs, Deform Curves on Surface, placed exactly)."""

from __future__ import annotations

import bpy
import numpy as np

from . import lashes

NAME = "JustStage stubble"
DENSITY = 60.0  # hairs a cm2
LENGTH = 1.5  # mm
RADIUS, TIP = 0.00006, 0.75  # m at the root (beard hair ~0.12 mm across); a cut hair's blunt end
RISE = 35.0  # degrees off the skin at the root
GROWTH = np.array([0.0, 0.5, -1.0])  # down and back (-Y is the face's front)
FLARE = 0.25  # the cheeks' outward share
SPREAD = 20.0  # degrees
CAVITY = 0.02  # m
LIPS_AT = 0.4
MELANIN, REDNESS, MELANIN_SPREAD = 0.9, 0.15, 0.05
POINTS = lashes.POINTS


def _smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def beard_weight(rel: np.ndarray) -> np.ndarray:
    """The beard's soft region at points relative to the eyes' midpoint (m, the character's axes) - skin_base.regions'
    formula."""
    x, y, z = rel[:, 0], rel[:, 1], rel[:, 2]
    front = 1.0 - _smooth(y, 0.06, 0.09)
    return front * _smooth(-z, 0.035, 0.050) * (1.0 - _smooth(-z, 0.19, 0.22)) * (1.0 - _smooth(np.abs(x), 0.07, 0.09))


def _lips_per_vertex(body: bpy.types.Object) -> np.ndarray:
    """MakeHuman's lips mask on hm08's own UVs, per vertex (the largest over its corners)."""
    from ... import paths
    from .groom import SURFACE_UV

    image = bpy.data.images.load(str(paths.makehuman("textures", "mpfb_lips.jpg")), check_existing=True)
    w, h = image.size
    px = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(px)
    grey = px.reshape(h, w, 4)[..., 0]
    me = body.data
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[SURFACE_UV].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    value = grey[np.clip((uv[:, 1] * h).astype(int), 0, h - 1), np.clip((uv[:, 0] * w).astype(int), 0, w - 1)]
    verts = np.empty(len(me.loops), np.int32)
    me.loops.foreach_get("vertex_index", verts)
    out = np.zeros(len(me.vertices), np.float32)
    np.maximum.at(out, verts, value)
    return out


def lip_points(body: bpy.types.Object) -> np.ndarray:
    """The lips' points on the character's current shape, world space."""
    from ...core.makehuman import skin_mask
    from ..body import build

    co = build.shaped_coords(body)
    lips = (_lips_per_vertex(body) > LIPS_AT) & skin_mask(len(co))
    m = np.array(body.matrix_world)
    return co[lips] @ m[:3, :3].T + m[:3, 3]


def strands(body: bpy.types.Object, seed: int = 5, density: float = DENSITY, length_mm: float = LENGTH):
    """The stubble's hairs on the body's current shape, world space: (strands, radii, melanin per strand)."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    from ..body import build
    from ..head import eye_layers, parts

    rng = np.random.default_rng(seed)
    m = np.array(body.matrix_world)
    to_local = np.array(body.matrix_world.inverted())
    co = build.shaped_coords(body) @ m[:3, :3].T + m[:3, 3]
    found = parts.parts_of(body)
    if not {"eyeLeft", "eyeRight"} <= set(found):
        from ...core.commands import CommandError

        raise CommandError(f"{body.name} has no eyes to measure the beard from; run juststage.head.add_parts first")
    mid = np.mean([eye_layers._eye_sphere(found[p])[0] for p in ("eyeLeft", "eyeRight")], axis=0)
    weight = beard_weight(co - mid)
    lips = _lips_per_vertex(body)
    weight *= 1.0 - np.clip((lips - 0.2) / 0.3, 0.0, 1.0)
    lp = co[(lips > LIPS_AT)]
    if len(lp):
        top = lp[:, 2].max()
        nose = (np.abs(co[:, 0] - mid[0]) < 0.022) & (co[:, 2] > top + 0.013)
        weight[nose] = 0.0
    tris, _loops = lashes._triangles(body)
    a, b, c = co[tris[:, 0]], co[tris[:, 1]], co[tris[:, 2]]
    cross = np.cross(b - a, c - a)
    area = 0.5 * np.linalg.norm(cross, axis=1)
    normal = cross / np.maximum(2.0 * area, 1e-12)[:, None]
    w_tri = weight[tris].mean(axis=1)
    count = rng.poisson(density * 1e4 * area * w_tri)
    which = np.repeat(np.arange(len(tris)), count)
    r1, r2 = rng.uniform(size=len(which)), rng.uniform(size=len(which))
    s = np.sqrt(r1)
    roots = (1 - s)[:, None] * a[which] + (s * (1 - r2))[:, None] * b[which] + (s * r2)[:, None] * c[which]
    n = normal[which]
    tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    keep = np.ones(len(roots), bool)
    for k, (p, nk) in enumerate(zip(roots, n, strict=True)):  # inside the mouth or a nostril: the body again outward
        q = to_local[:3, :3] @ (p + 0.0005 * nk) + to_local[:3, 3]
        hit = tree.ray_cast(Vector(q), Vector(to_local[:3, :3] @ nk), CAVITY)
        keep[k] = hit[0] is None
    roots, n = roots[keep], n[keep]
    # onto the skin as it is drawn (the levels smooth the base mesh in by up to ~1 mm): the nearest point and its
    # normal on the evaluated body, as the lashes and brows find theirs
    to_world = np.array(body.matrix_world)
    for k, p in enumerate(roots):
        hit, nk = tree.find_nearest(Vector(to_local[:3, :3] @ p + to_local[:3, 3]))[:2]
        roots[k] = to_world[:3, :3] @ np.array(hit) + to_world[:3, 3]
        nw = to_world[:3, :3] @ np.array(nk)
        n[k] = nw / np.linalg.norm(nw)
    side = np.sign(roots[:, 0] - mid[0])[:, None] * np.array([1.0, 0.0, 0.0])
    g = GROWTH / np.linalg.norm(GROWTH) + FLARE * side
    flat = g - (g * n).sum(1, keepdims=True) * n
    flat /= np.maximum(np.linalg.norm(flat, axis=1, keepdims=True), 1e-9)
    turn = np.radians(rng.normal(0.0, SPREAD, len(roots)))[:, None]
    flat = np.cos(turn) * flat + np.sin(turn) * np.cross(n, flat)
    t = np.linspace(0.0, 1.0, POINTS)
    rise = np.radians(RISE) * (1.0 - 0.5 * t)  # lying to half its rise at the tip
    lengths = 0.001 * length_mm * rng.uniform(0.7, 1.3, len(roots))
    d = np.cos(rise)[None, :, None] * flat[:, None, :] + np.sin(rise)[None, :, None] * n[:, None, :]
    steps = np.concatenate([np.zeros((len(roots), 1, 3)), d[:, :-1] * (lengths / (POINTS - 1))[:, None, None]], axis=1)
    found_strands = roots[:, None, :] - 0.00005 * n[:, None, :] + np.cumsum(steps, axis=1)
    radii = [RADIUS * np.interp(t, [0.0, 1.0], [1.0, TIP])] * len(roots)
    melanin = list(np.clip(MELANIN + rng.normal(0.0, MELANIN_SPREAD, len(roots)), 0.0, 1.0))
    return list(found_strands), radii, melanin


def make(character: bpy.types.Object, seed: int = 5, density: float = DENSITY, length_mm: float = LENGTH):
    """JustStage's stubble on the character, replacing its beard (part "beard")."""
    from . import groom

    groom._check_surface(character)
    found, radii, melanin = strands(character, seed, density, length_mm)
    rest, uvs = lashes.to_rest(character, found)
    curves = bpy.data.hair_curves.new(NAME)
    curves.add_curves([POINTS] * len(rest))
    curves.position_data.foreach_set("vector", rest.astype(np.float32).ravel())
    curves.attributes.new("radius", "FLOAT", "POINT").data.foreach_set(
        "value", np.concatenate(radii).astype(np.float32))
    curves.attributes.new("melanin", "FLOAT", "CURVE").data.foreach_set("value", np.array(melanin, np.float32))
    curves.attributes.new("redness", "FLOAT", "CURVE").data.foreach_set(
        "value", np.full(len(rest), REDNESS, np.float32))
    curves.attributes.new("surface_uv_coordinate", "FLOAT2", "CURVE").data.foreach_set(
        "vector", uvs.astype(np.float32).ravel())
    curves.surface_uv_map = groom.SURFACE_UV
    obj = bpy.data.objects.new(NAME, curves)
    obj.modifiers.new("Surface Deform", "NODES").node_group = lashes._deform_group()
    groom.remove_part(character, "beard")
    groom._attach(character, [obj], "beard")
    curves.materials.append(groom.hair_material(f"JustStage Hair ({obj.name})"))
    to_local = np.array(character.matrix_world.inverted())
    wanted = np.array(found) @ to_local[:3, :3].T + to_local[:3, 3]
    miss = lashes.place(obj, rest[:, 0], wanted)
    print(f"stubble: {len(rest)} hairs, {POINTS} points each, within {miss * 1000:.4f} mm")
    return obj
