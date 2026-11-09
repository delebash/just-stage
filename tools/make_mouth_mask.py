# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mouth's lining on the body's head tile (UDIM 1001): the inner lips and the mouth's skin, which no scan or
painting covers (people are scanned with their mouths closed) - so an open mouth showed a pale rim of skin inside the
lips (the part-by-part gate, 2026-11-05: "a pale gap inside the corner"). Made once on the default human, like the
layout; modules/skin/maps.py colours it as wet mucosa.

    python tools/dev.py blender -b --python tools/make_mouth_mask.py

The lining: the body's vertices behind the lips' front, within the mouth's width and height round the front teeth,
facing into the mouth - out of the corners' outer crease (CORNER_FADE: there the lining's red glowed through the
scattering at close-up, 2026-11-09), the deeper lining inside the cheeks kept; softened over their neighbours.
`-- --out DIR` writes a trial's masks there instead (tools/gate/factors.py `mouthmask*<name>`). Writes `extension/juststage/data/generated/skin/mouth.png`
(8-bit grey, 2048², the head tile's UV square).

The seam: the band of the lips in front of the lining, by each vertex's distance along the surface (Dijkstra over the
mesh's edges) from it - 1 at the lining, 0 at SEAM_MM - where real lips darken to a deep red into the closed mouth's
line (HD Aaron's, the own-content proof 2026-11-08; ours one flat pink). Writes `mouth_seam.png` beside it; maps.py
darkens the lips by it (LIP_SEAM_TINT).

The upper lip: the lips (MakeHuman's mask on hm08's own UVs, per vertex) on the upper side of the mouth's slit in the
head tile's UVs (the lining's long, thin hole runs between the two lips; the upper side is the one whose lips sit
higher) - faded over UPPER_SOFT_UV. Writes `lips_upper.png`;
maps.py tints it deeper red (LIP_UPPER_TINT: real upper lips, HD Aaron's among them, are a deeper red than the lower;
ours were one pink)."""

from __future__ import annotations

import heapq
import importlib

import bpy
import numpy as np

api = importlib.import_module("bl_ext.system.juststage.api")
paths = importlib.import_module("bl_ext.system.juststage.paths")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")

SIZE = 2048
HEAD_TILE = 1001
BEHIND = 0.002  # m behind the lips' frontmost point: the lining starts here
HALF_WIDTH, HALF_HEIGHT = 0.032, 0.022  # m round the front teeth's centre
DEPTH = 0.05  # m behind the lips' front: the lining ends (the throat)
#: m: the lining fades out over this before the lips' corners - BEHIND is measured from the mouth's front at its middle,
#: so at the corners (the mouth curving back) the outer crease, facing in, counted as lining: a red glow at each corner
#: at close-up, lit through by the scattering (2026-11-09)
CORNER_FADE = 0.004
UPPER_SOFT_UV = 0.002  # the upper lip's mask fades in over this across the slit (head-tile UV units, ~1.4 mm)
SEAM_MM = 10.0  # the lips' darkening reaches this far in front of the lining (4 mm stayed on the lips' inner side)


def _out_dir():
    """`-- --out DIR`: a trial's variant written there (tools/gate/factors.py `mouthmask*<name>` swaps it in); none:
    the shipped folder."""
    import sys
    from pathlib import Path

    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return Path(args[args.index("--out") + 1]) if "--out" in args else paths.GENERATED / "skin"


def main() -> None:
    made = api.run("juststage.body.create", name="Mouth mask")
    api.run("juststage.head.add_parts", character=made.character)
    body = bpy.data.objects[made.object]
    co = build.shaped_coords(body)
    teeth = parts.parts_of(body)["teeth"]
    tco = np.array([v.co for v in teeth.data.vertices])  # the body's space (parts.py)
    front = tco[tco[:, 1] < tco[:, 1].min() + 0.004]
    centre = np.array([tco[:, 0].mean(), front[:, 1].mean(), front[:, 2].mean()])
    me = body.data
    normals = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("normal", normals)
    normals = normals.reshape(-1, 3)
    near = (np.abs(co[:, 0] - centre[0]) < HALF_WIDTH) & (np.abs(co[:, 2] - centre[2]) < HALF_HEIGHT)
    lips_front = co[near, 1].min()  # the character faces -Y
    behind = (co[:, 1] > lips_front + BEHIND) & (co[:, 1] < lips_front + DEPTH)
    to_centre = centre - co
    to_centre /= np.linalg.norm(to_centre, axis=1, keepdims=True)
    facing = np.einsum("ij,ij->i", normals, to_centre) > 0.2
    lining = near & behind & facing
    stubble = importlib.import_module("bl_ext.system.juststage.modules.hair.stubble")
    lips = stubble._lips_per_vertex(body)
    # the corner's outer crease out, the mouth's inside kept (the lining inside the cheeks shows when it opens): near
    # the lips' corners, only what lies within 1-3 mm of the corner's own depth fades
    side = np.abs(co[:, 0] - centre[0])
    reach = side[lips > 0.3].max()  # the lips' corners, out from the middle
    corner_y = np.median(co[(lips > 0.3) & (side > reach - 0.002), 1])  # the corners' depth (the character faces -Y)
    at_corner = np.clip((side - (reach - CORNER_FADE)) / CORNER_FADE + 0.5, 0.0, 1.0)
    shallow = np.clip((corner_y + 0.003 - co[:, 1]) / 0.002, 0.0, 1.0)  # 1 at the corner's depth, 0 from 3 mm deeper
    keep = 1.0 - at_corner * shallow
    weight = (lining * keep * keep * (3 - 2 * keep)).astype(np.float32)
    lining = weight > 0.5
    # softened over the neighbours (two rounds of averaging along the edges)
    edges = np.array([e.vertices for e in me.edges])
    for _ in range(2):
        acc, cnt = weight.copy(), np.ones_like(weight)
        np.add.at(acc, edges[:, 0], weight[edges[:, 1]])
        np.add.at(acc, edges[:, 1], weight[edges[:, 0]])
        np.add.at(cnt, edges[:, 0], 1)
        np.add.at(cnt, edges[:, 1], 1)
        weight = np.maximum(weight, acc / cnt)
    image, count = _raster(me, weight)
    folder = _out_dir()
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / "mouth.png"
    maps.write_png(out, np.repeat(image[..., None], 3, axis=2))  # Blender's rows bottom first, as write_png expects
    print(f"wrote {out}: {int((weight > 0.5).sum())} lining vertices, {count} polygons, "
          f"{(image > 0.5).mean():.2%} of the head tile")
    seam = np.clip(1.0 - _distance_from(co, edges, lining) / (SEAM_MM / 1000.0), 0.0, 1.0) ** 2
    image, count = _raster(me, seam.astype(np.float32))
    out = folder / "mouth_seam.png"
    maps.write_png(out, np.repeat(image[..., None], 3, axis=2))
    print(f"wrote {out}: {int(((seam > 0) & ~lining).sum())} vertices in front of the lining, {count} polygons")
    # which lip: the side of the mouth's slit in the head tile's UVs - the lining's hole, long and thin, runs between
    # the two lips there (by height alone the lower lip's top, rolled up to the line, came out upper)
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[maps.UV].data.foreach_get("uv", uv)
    loop_v = np.empty(len(me.loops), np.int32)
    me.loops.foreach_get("vertex_index", loop_v)
    vuv = np.zeros((len(co), 2))
    np.add.at(vuv, loop_v, uv.reshape(-1, 2))
    vuv /= np.maximum(np.bincount(loop_v, minlength=len(co)), 1)[:, None]
    lip = (lips > 0.3) & ~lining
    lips_uv = np.median(vuv[lip], axis=0)  # the lining round the lips on the face, not the mouth's own island
    face = lining & (np.linalg.norm(vuv - lips_uv, axis=1) < 0.03)
    centre = vuv[face].mean(axis=0)
    axis = np.linalg.svd(vuv[face] - centre, full_matrices=False)[2][0]  # the slit's long direction
    side = (vuv - centre) @ np.array([-axis[1], axis[0]])  # signed distance across it (UV units)
    upper_sign = 1.0 if co[lip & (side > 0), 2].mean() > co[lip & (side < 0), 2].mean() else -1.0
    across = side * upper_sign / UPPER_SOFT_UV
    upper = (np.clip((lips - 0.2) / 0.3, 0.0, 1.0) * np.clip(across * 0.5 + 0.5, 0.0, 1.0) * ~lining).astype(np.float32)
    print(f"lips: {int(lip.sum())} vertices; upper {int((lip & (side * upper_sign > 0)).sum())} (mean z "
          f"{co[lip & (side * upper_sign > 0), 2].mean():.4f}), lower {int((lip & (side * upper_sign < 0)).sum())} "
          f"(mean z {co[lip & (side * upper_sign < 0), 2].mean():.4f})")
    image, count = _raster(me, upper)
    out = folder / "lips_upper.png"
    maps.write_png(out, np.repeat(image[..., None], 3, axis=2))
    print(f"wrote {out}: {int((upper > 0.5).sum())} upper-lip vertices, {count} polygons")


def _distance_from(co: np.ndarray, edges: np.ndarray, sources: np.ndarray) -> np.ndarray:
    """Each vertex's distance (m) along the mesh's edges from the nearest of `sources` (Dijkstra; inf if unreached)."""
    length = np.linalg.norm(co[edges[:, 0]] - co[edges[:, 1]], axis=1)
    near = [[] for _ in range(len(co))]
    for (a, b), d in zip(edges.tolist(), length.tolist(), strict=True):
        near[a].append((b, d))
        near[b].append((a, d))
    dist = np.full(len(co), np.inf)
    dist[sources] = 0.0
    heap = [(0.0, int(v)) for v in np.flatnonzero(sources)]
    while heap:
        d, v = heapq.heappop(heap)
        if d > dist[v] or d > 0.05:  # a few cm is all the band needs
            continue
        for u, w in near[v]:
            if d + w < dist[u]:
                dist[u] = d + w
                heapq.heappush(heap, (d + w, u))
    return dist


def _raster(me, weight: np.ndarray) -> tuple[np.ndarray, int]:
    """Per-vertex `weight` drawn into the head tile's UV square (SIZE², rows bottom first), the highest where faces
    overlap, and the polygons drawn."""
    uv_layer = me.uv_layers[maps.UV].data
    image = np.zeros((SIZE, SIZE), np.float32)
    count = 0
    for p in me.polygons:
        vw = weight[list(p.vertices)]
        if vw.max() <= 0:
            continue
        uvs = np.array([[uv_layer[i].uv.x - (HEAD_TILE - 1001), uv_layer[i].uv.y] for i in p.loop_indices])
        if not ((uvs >= 0) & (uvs <= 1)).all():
            continue
        count += 1
        for k in range(1, len(uvs) - 1):
            tri, val = uvs[[0, k, k + 1]] * SIZE - 0.5, vw[[0, k, k + 1]]
            lo, hi = np.floor(tri.min(0)).astype(int), np.ceil(tri.max(0)).astype(int)
            xs, ys = np.meshgrid(np.arange(max(lo[0], 0), min(hi[0], SIZE - 1) + 1),
                                 np.arange(max(lo[1], 0), min(hi[1], SIZE - 1) + 1))
            q = np.stack([xs.ravel(), ys.ravel()], -1).astype(np.float64)
            a, b, c = tri
            m = np.array([[b[0] - a[0], c[0] - a[0]], [b[1] - a[1], c[1] - a[1]]])
            if abs(np.linalg.det(m)) < 1e-12:
                continue
            st = (q - a) @ np.linalg.inv(m).T
            w = np.stack([1 - st[:, 0] - st[:, 1], st[:, 0], st[:, 1]], -1)
            inside = (w > -0.05).all(1)
            image[q[inside, 1].astype(int), q[inside, 0].astype(int)] = np.maximum(
                image[q[inside, 1].astype(int), q[inside, 0].astype(int)], w[inside] @ val)
    return image, count


if __name__ == "__main__":  # imported by make_stretch_mask.py for _raster
    main()
