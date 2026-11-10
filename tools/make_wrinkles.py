# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face's mid-scale wrinkles as a height map on the head's UDIM tile - our own (2026-11-08, the own-content proof:
HD Aaron's skin on our head reads real with its relief and plastic without it, and no free scan we have gives lines
at his strength - two HSRD-100 heads, a 60-year-old's, Lee Perry-Smith's; `docs/plans/2026-11-08-own-content-proof.md`).
NOT STANDARD (the standard - sculpted or scanned wrinkle maps - none free): each wrinkle a curve placed from the face's
own landmarks (the pupils, the nose's tip, the mouth), carried onto the skin by a ray from the front, drawn as a groove
of a Gaussian profile in the head tile's UVs - forehead lines, the frown's lines, crow's feet, the lower lid's crease,
the nose-to-mouth fold.

    python tools/dev.py blender -b --python tools/make_wrinkles.py -- --out DIR

Writes `DIR/wrinkles.png` (16-bit grey, 1 flat, lower in a groove; its depth at 1.0 is DEPTH_M)."""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

import bpy
import numpy as np

api = importlib.import_module("bl_ext.system.juststage.api")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")

SIZE = 4096  # the head tile at ~5.7 px / mm (MM_PER_UV 724 for tile 1001)
HEAD_TILE = 1001
DEPTH_M = 0.0004  # a groove of depth 1.0, metres (the bump's distance)
STEP = 0.0002  # m between a curve's samples (well under the narrowest groove's width)


def _curves(pupils: np.ndarray, nose: np.ndarray, mouth_z: float, rng, only: str = "") -> list[tuple[np.ndarray, float, float]]:
    """(points (n, 2) in x, z metres; depth; sigma metres) for each wrinkle, from the landmarks."""
    pz = float(pupils[:, 1].mean())
    out = []

    def wobble(n, amp):
        return np.cumsum(rng.normal(0.0, amp / 6.0, n))  # a slow random walk

    for dz, half, depth in ((0.034, 0.040, 1.0), (0.046, 0.044, 0.9), (0.058, 0.036, 0.7)):  # the forehead's lines
        xs = np.linspace(-half, half, 80)
        zs = pz + dz + 0.005 * (1.0 - (xs / 0.05) ** 2) + wobble(80, 0.0012)
        out.append((np.stack([xs, zs], -1), depth, 0.0007))
    for sx in (-1.0, 1.0):
        x0 = sx * 0.0065  # the frown's lines between the brows
        zs = np.linspace(pz + 0.010, pz + 0.028, 30)
        out.append((np.stack([x0 + sx * 0.002 * (zs - pz - 0.010) / 0.018, zs], -1), 0.7, 0.0006))
    for eye in pupils:
        px = float(eye[0])
        sx = np.sign(px)
        corner = np.array([px + sx * 0.016, pz + 0.001])
        for ang, length in ((-30.0, 0.013), (-8.0, 0.016), (15.0, 0.012)):  # crow's feet, out from the corner
            a = np.radians(ang)
            d = np.array([sx * np.cos(a), np.sin(a)])
            t = np.linspace(0.004, 0.004 + length, 40)[:, None]
            out.append((corner + t * d + np.c_[np.zeros(40), wobble(40, 0.0006)], 0.7, 0.0005, "crows"))
        xs = np.linspace(px - sx * 0.010, px + sx * 0.014, 50)  # the lower lid's crease
        zs = pz - 0.012 + 0.003 * ((xs - px) / 0.012) ** 2
        out.append((np.stack([xs, zs], -1), 0.5, 0.0008))
        t = np.linspace(0.0, 1.0, 60)  # the nose-to-mouth fold: from beside the nose's wing to past the mouth's corner
        start, end = np.array([sx * 0.017, nose[1] - 0.004]), np.array([sx * 0.031, mouth_z - 0.008])
        bow = np.array([sx * 0.004, 0.0]) * np.sin(np.pi * t)[:, None]
        out.append((start + (end - start) * t[:, None] + bow, 1.2, 0.002))
    # `only`: one kind of line (the crow's feet for the smile's own layer, 2026-11-10); the rest carry no tag
    return [c[:3] for c in out if not only or (len(c) > 3 and c[3] == only)]


def main() -> None:
    p = argparse.ArgumentParser(prog="make_wrinkles.py --")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--only", default="", help="one kind of line: crows")
    a = p.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    from mathutils import Vector, geometry
    from mathutils.bvhtree import BVHTree

    made = api.run("juststage.body.create", name="Wrinkles")
    api.run("juststage.head.add_parts", character=made.character)
    body = bpy.data.objects[made.object]
    co = build.shaped_coords(body)
    found = parts.parts_of(body)
    eyes = [np.array([v.co for v in found[k].data.vertices]) for k in ("eyeLeft", "eyeRight")]
    pupils = np.array([[e[:, 0].mean(), e[:, 2].mean()] for e in eyes])  # x, z
    teeth = np.array([v.co for v in found["teeth"].data.vertices])
    mouth_z = float(teeth[teeth[:, 1] < teeth[:, 1].min() + 0.004][:, 2].mean())
    mid = (np.abs(co[:, 0]) < 0.008) & (co[:, 2] < pupils[:, 1].mean()) & (co[:, 2] > mouth_z + 0.01)
    tip = co[mid][np.argmin(co[mid][:, 1])]
    nose = np.array([0.0, float(tip[2])])
    me = body.data
    me.calc_loop_triangles()
    uv = me.uv_layers[maps.UV].data
    # only the head tile's skin: hm08's helpers (joint cubes, the hair, tights and skirt proxies) lie in front of the face
    # too and took the rays (the first map, 20:50: 86 of ~3,000 samples on the skin)
    tris = [t for t in me.loop_triangles if all(HEAD_TILE - 1001 <= uv[i].uv.x < HEAD_TILE - 1000 for i in t.loops)]
    bvh = BVHTree.FromPolygons([Vector(c) for c in co], [t.vertices for t in tris])
    rng = np.random.default_rng(a.seed)
    px_per_m = SIZE / (maps.MM_PER_UV.get(HEAD_TILE, 724.0) / 1000.0)  # one texel ~ MM_PER_UV / SIZE mm on the head
    height = np.zeros((SIZE, SIZE), np.float32)
    drawn = 0
    for points, depth, sigma in _curves(pupils, nose, mouth_z, rng, a.only):
        # resample evenly along the curve, then carry each sample onto the skin by a ray from the front
        seg = np.linalg.norm(np.diff(points, axis=0), axis=1)
        s = np.concatenate([[0.0], np.cumsum(seg)])
        n = max(int(s[-1] / STEP), 2)
        t = np.linspace(0.0, s[-1], n)
        pts = np.stack([np.interp(t, s, points[:, 0]), np.interp(t, s, points[:, 1])], -1)
        fade = np.sin(np.pi * np.linspace(0.0, 1.0, n)) ** 0.5  # the ends fade out
        for (x, z), f in zip(pts, fade, strict=True):
            hit, _, index, _ = bvh.ray_cast(Vector((x, -1.0, z)), Vector((0.0, 1.0, 0.0)))
            if hit is None:
                continue
            tri = tris[index]
            corners = [Vector(co[v]) for v in tri.vertices]
            uvs = [Vector((uv[i].uv.x - (HEAD_TILE - 1001), uv[i].uv.y, 0.0)) for i in tri.loops]
            u = geometry.barycentric_transform(hit, *corners, *uvs)
            if not (0.0 <= u.x <= 1.0 and 0.0 <= u.y <= 1.0):
                continue
            r = sigma * px_per_m  # the groove's width in texels
            cx, cy = u.x * SIZE - 0.5, u.y * SIZE - 0.5
            k = int(np.ceil(3 * r)) + 1
            x0, y0 = int(cx) - k, int(cy) - k
            xs, ys = np.meshgrid(np.arange(x0, x0 + 2 * k + 1), np.arange(y0, y0 + 2 * k + 1))
            ok = (xs >= 0) & (xs < SIZE) & (ys >= 0) & (ys < SIZE)
            g = np.exp(-((xs - cx) ** 2 + (ys - cy) ** 2) / (2 * r * r)) * depth * f
            g *= STEP * px_per_m / (np.sqrt(2 * np.pi) * r)  # the splats along the line sum to one groove's depth
            height[ys[ok], xs[ok]] += g[ok]
            drawn += 1
    height = np.clip(height, 0.0, 1.5) / 1.5
    image = np.repeat((1.0 - height)[..., None], 3, axis=2)
    a.out.mkdir(parents=True, exist_ok=True)
    maps.write_png(a.out / "wrinkles.png", image, depth="16")
    print(f"wrote {a.out / 'wrinkles.png'}: {drawn} samples on the skin; deepest {height.max():.2f}", flush=True)


main()
