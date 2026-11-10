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
- **How long, how thick:** LENGTH mm (about a week's growth - HD Aaron's Stubble, measured), +-30%; RADIUS at the
  root, cut blunt (TIP).
Attached as the lashes are (lashes.py: rest shape, surface UVs, Deform Curves on Surface, placed exactly)."""

from __future__ import annotations

import bpy
import numpy as np

from . import lashes

NAME = "JustStage stubble"
#: 2026-11-06, against HD Aaron's Stubble at the gate's mouth and cheek views: denser, shorter, finer, curved, a third
#: of the hairs grey (the first pass - 60 a cm2, 1.5 mm, straight black - read as scattered black lines over the cheeks)
#: 2026-11-08, judged by eye at full resolution beside HD Aaron (`.dev/gate/parts/2026-11-08q`, the user's bar): at 160
#: our stubble read as a dense dark mat over the lower face, his short and sparse; at 100 it reads close to his
#: 2026-11-10, one factor at a time beside him (`.dev/gate/parts/2026-11-10stubble`, `stubble5.png`): with the patches
#: of 11-09 (PATCHY 0.8) 220 at the shipped 25% grey reads like his coverage, not a mat; 50% grey alone only lightened
#: it (the grey share is a character's age)
DENSITY = 220.0  # hairs a cm2
#: 2026-11-06, the clean-input gate's cheek view: HD Aaron's Stubble hairs 2.4-4.2 mm, lying close along the skin,
#: a third of them white - ours (1 mm, rising 45 degrees, grey at melanin 0.25) read as scattered dots, no white
#: Gate run 10's lips view: ours thick (0.1 mm), sparse-looking, every way - each strand stood out (chin share >8 L*
#: darker 0.173 against his 0.061); his finer, denser, flowing one way, reading as a texture
LENGTH = 2.8  # mm
RADIUS, TIP = 0.00003, 0.7  # m at the root; a cut hair's blunt end
RISE = 22.0  # degrees off the skin at the root
CURL = 12.0  # degrees the hair turns along its length (each its own way)
GREY_SHARE, GREY_MELANIN = 0.25, 0.12  # the grey ones (run 7: a third at 0.04 read as a white beard; his mostly dark)
#: GREY_SHARE is the share at HD Aaron's age (~40: MakeHuman's age macro ~0.615 - 0.5 is 25, 1.0 is 90), scaled by
#: the character's age: none at 25, x2.8 at 90 (2026-11-10: a fixed quarter read as a pale fuzz on the dark-skinned
#: 25-year-old Muscular man; with none his stubble read dark and natural - `.dev/gate/parts/2026-11-10ship3`)
GREY_BY_AGE = ((0.5, 0.615, 1.0), (0.0, 1.0, 2.8))
NECKLINE = (0.155, 0.7, 0.03)  # m below the eyes under the chin; its rise a metre back; from this far behind them
GROWTH = np.array([0.0, 0.5, -1.0])  # down and back (-Y is the face's front)
FLARE = 0.25  # the cheeks' outward share
SPREAD = 10.0  # degrees
CAVITY = 0.02  # m
LIPS_AT = 0.4
MELANIN, REDNESS, MELANIN_SPREAD = 0.9, 0.15, 0.05
#: beards grow unevenly: the density x (1 - PATCHY + PATCHY x a smooth noise of PATCH_MM cells) - at an even density
#: ours read as a uniform mat beside HD Aaron's patchy stubble; at 0.8 (DENSITY kept) the chin's middle thins and the
#: jaw stays dense, as his (2026-11-09, `.dev/gate/parts/2026-11-09stubble`, by eye at the chin and face views)
PATCHY, PATCH_MM = 0.8, 25.0
POINTS = lashes.POINTS


def _smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _patches(p: np.ndarray, seed: int, cell_mm: float = PATCH_MM) -> np.ndarray:
    """A smooth value noise in 0-1 at points `p` (m): lattice values hashed from the cell and `seed`, blended
    trilinearly with a smoothstep - patches about `cell_mm` across."""
    g = p / (cell_mm / 1000.0)
    i = np.floor(g).astype(np.int64)
    f = g - i
    f = f * f * (3.0 - 2.0 * f)

    def lattice(ix, iy, iz):
        n = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
        n &= 0xFFFFFFFF
        n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
        return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0

    out = np.zeros(len(p))
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out += w * lattice(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz)
    return out


def _neckline(rel: np.ndarray) -> np.ndarray:
    """1 above the beard's neckline, 0 below (HD Aaron's: none down the throat - run 7 of the clean-input gate had
    ours to the collarbones): NECKLINE[0] below the eyes under the chin, rising by NECKLINE[1] a metre back."""
    cut = -NECKLINE[0] + NECKLINE[1] * np.clip(rel[:, 1] - NECKLINE[2], 0.0, None)
    return _smooth(rel[:, 2] - cut, 0.002, 0.014)


def beard_weight(rel: np.ndarray, mouth: np.ndarray | None = None) -> np.ndarray:
    """The beard's soft region at points relative to the eyes' midpoint (m, the character's axes): skin_base.regions'
    formula, and - with the mouth's centre (relative too) - stubble's own: the upper lip up to the nose, the chin, the
    jaw and the cheeks below the mouth's level, to a neckline under the jaw (HD Aaron's: his cheeks above are clean)."""
    x, y, z = rel[:, 0], rel[:, 1], rel[:, 2]
    front = 1.0 - _smooth(y, 0.06, 0.09)
    w = front * _smooth(-z, 0.035, 0.050) * (1.0 - _smooth(np.abs(x), 0.07, 0.09))
    w = w * _neckline(rel)
    if mouth is not None:
        side = _smooth(np.abs(x - mouth[0]), 0.018, 0.035)  # 0 over the lip, 1 out on the cheeks
        top = mouth[2] + 0.017 * (1.0 - side) - 0.004 * side  # the moustache's top, the cheeks' at the mouth's level
        w = w * (1.0 - _smooth(z - top, -0.004, 0.006))
    return w


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


def grey_share(body: bpy.types.Object) -> float:
    """The share of grey hairs for the character's age (GREY_SHARE x GREY_BY_AGE)."""
    return float(GREY_SHARE * np.interp(body.juststage.age, *GREY_BY_AGE))


def strands(body: bpy.types.Object, seed: int = 5, density: float = DENSITY, length_mm: float = LENGTH,
            grey: float | None = None):
    """The stubble's hairs on the body's current shape, world space: (strands, radii, melanin per strand); `grey` the
    grey share (by default the character's age's, `grey_share`)."""
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
    lips = _lips_per_vertex(body)
    lp = co[(lips > LIPS_AT)]
    weight = beard_weight(co - mid, (lp.mean(axis=0) - mid) if len(lp) else None)
    weight *= 1.0 - np.clip((lips - 0.2) / 0.3, 0.0, 1.0)
    if len(lp):
        top = lp[:, 2].max()
        nose = (np.abs(co[:, 0] - mid[0]) < 0.022) & (co[:, 2] > top + 0.013)
        weight[nose] = 0.0
    tris, _loops = lashes._triangles(body)
    a, b, c = co[tris[:, 0]], co[tris[:, 1]], co[tris[:, 2]]
    cross = np.cross(b - a, c - a)
    area = 0.5 * np.linalg.norm(cross, axis=1)
    normal = cross / np.maximum(2.0 * area, 1e-12)[:, None]
    w_max = weight[tris].max(axis=1)  # sampled at each triangle's most, kept by each root's own weight below
    count = rng.poisson(density * 1e4 * area * w_max)
    which = np.repeat(np.arange(len(tris)), count)
    r1, r2 = rng.uniform(size=len(which)), rng.uniform(size=len(which))
    s = np.sqrt(r1)
    bary = np.stack([1 - s, s * (1 - r2), s * r2], axis=1)
    roots = bary[:, :1] * a[which] + bary[:, 1:2] * b[which] + bary[:, 2:] * c[which]
    own = (bary * weight[tris[which]]).sum(axis=1) * _neckline(roots - mid)  # a big neck triangle across the line
    if PATCHY > 0:
        own *= 1.0 - PATCHY + PATCHY * _smooth(_patches(roots - mid, seed), 0.3, 0.7)  # contrast: patches, not haze
    kept = rng.uniform(size=len(roots)) < own / np.maximum(w_max[which], 1e-9)
    roots, which = roots[kept], which[kept]
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
    lengths = 0.001 * length_mm * rng.uniform(0.6, 1.4, len(roots))
    curl = np.radians(rng.normal(0.0, CURL, len(roots)))[:, None] * t[None, :]  # each its own way along it
    side_dir = np.cross(n, flat)
    heading = np.cos(curl)[..., None] * flat[:, None, :] + np.sin(curl)[..., None] * side_dir[:, None, :]
    d = np.cos(rise)[None, :, None] * heading + np.sin(rise)[None, :, None] * n[:, None, :]
    steps = np.concatenate([np.zeros((len(roots), 1, 3)), d[:, :-1] * (lengths / (POINTS - 1))[:, None, None]], axis=1)
    found_strands = roots[:, None, :] - 0.00005 * n[:, None, :] + np.cumsum(steps, axis=1)
    radii = [RADIUS * np.interp(t, [0.0, 1.0], [1.0, TIP])] * len(roots)
    grey = rng.uniform(size=len(roots)) < (grey_share(body) if grey is None else grey)
    melanin = list(np.clip(np.where(grey, GREY_MELANIN, MELANIN) + rng.normal(0.0, MELANIN_SPREAD, len(roots)), 0.0, 1.0))
    return list(found_strands), radii, melanin


def make(character: bpy.types.Object, seed: int = 5, density: float = DENSITY, length_mm: float = LENGTH,
         grey: float | None = None):
    """JustStage's stubble on the character, replacing its beard (part "beard")."""
    from . import groom

    groom._check_surface(character)
    found, radii, melanin = strands(character, seed, density, length_mm, grey)
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
