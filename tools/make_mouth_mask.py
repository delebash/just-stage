# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mouth's lining on the body's head tile (UDIM 1001): the inner lips and the mouth's skin, which no scan or
painting covers (people are scanned with their mouths closed) - so an open mouth showed a pale rim of skin inside the
lips (the part-by-part gate, 2026-11-05: "a pale gap inside the corner"). Made once on the default human, like the
layout; modules/skin/maps.py colours it as wet mucosa.

    python tools/dev.py blender -b --python tools/make_mouth_mask.py

The lining: the body's vertices behind the lips' front, within the mouth's width and height round the front teeth,
facing into the mouth; softened over their neighbours. Writes `extension/juststage/data/generated/skin/mouth.png`
(8-bit grey, 2048², the head tile's UV square)."""

from __future__ import annotations

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
    weight = (near & behind & facing).astype(np.float32)
    # softened over the neighbours (two rounds of averaging along the edges)
    edges = np.array([e.vertices for e in me.edges])
    for _ in range(2):
        acc, cnt = weight.copy(), np.ones_like(weight)
        np.add.at(acc, edges[:, 0], weight[edges[:, 1]])
        np.add.at(acc, edges[:, 1], weight[edges[:, 0]])
        np.add.at(cnt, edges[:, 0], 1)
        np.add.at(cnt, edges[:, 1], 1)
        weight = np.maximum(weight, acc / cnt)
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
    out = paths.GENERATED / "skin" / "mouth.png"
    maps.write_png(out, np.repeat(image[..., None], 3, axis=2))  # Blender's rows bottom first, as write_png expects
    print(f"wrote {out}: {int((weight > 0.5).sum())} lining vertices, {count} polygons, "
          f"{(image > 0.5).mean():.2%} of the head tile")


main()
