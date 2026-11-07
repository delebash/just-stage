# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face's regions on the body's head tile (UDIM 1001): how strong the skin's relief is and how shiny it is, region
by region - as CC5 masks its micro detail by region (HD Aaron's `MicroNMask`). Made once on the default human, like
the layout; modules/skin/maps.py scales the pore and microrelief depth by it, tools/build_skins.py takes a composed
skin's roughness from it. Why (the part-by-part gate, 2026-11-05): one pore depth for the whole face matched HD Aaron's
cheek (pore band 0.99 against 0.96) and left his forehead at a third (0.65 against 1.74); doubling it everywhere took
the forehead to 0.98 and the cheek past his to 1.68.

    python tools/dev.py blender -b --python tools/make_face_regions.py

Regions by place on the default human (it faces -Y; from the pupils, the front teeth and the face's front): the
forehead above the brows, the nose, the chin, round the eyes; elsewhere the cheek's values. Softened over the mesh's
neighbours. Writes `extension/juststage/data/generated/skin/face_regions.png`: 8-bit RGB, 2048², R the relief factor /
RELIEF_SCALE, G the roughness, B the microrelief factor / RELIEF_SCALE; and `face_share.png`, the face's share (0 on the
neck)."""

from __future__ import annotations

import importlib

import bpy
import numpy as np

api = importlib.import_module("bl_ext.system.juststage.api")
paths = importlib.import_module("bl_ext.system.juststage.paths")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")
material = importlib.import_module("bl_ext.system.juststage.modules.skin.material")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")

SIZE = 2048
HEAD_TILE = 1001
RELIEF_SCALE = 8.0  # R = factor / RELIEF_SCALE
#: (relief factor, roughness) by region; "cheek" everywhere else on the head tile
#: (pore relief factor, microrelief factor, roughness) by region. The forehead's extra detail is fine (the
#: microrelief): its pore tile at x5 read craggy at the face's distance, HD Aaron's forehead clean there (2026-11-05)
#: 2026-11-07, the first clean baseline measured with the standard bands (docs/gate/2026-11-07/report.md): the cheek
#: below HD Aaron (micro 0.75, pores 0.86) - pores x1.15 and microrelief x1.35 on every region bring it to 0.93 / 0.92
#: (within his own bands) and keep the forehead equal (0.96 / 0.85); microrelief x3 read as crackle-glaze cells and
#: flattened the larger bumps. 2026-11-07 evening (plan §0, EEVEE, `dists.py --patches` - the texture's excess over
#: HD Aaron's own patch-to-patch): the forehead's microrelief x5 read as a crisp honeycomb against his soft forehead,
#: where his MicroNMask is 1 over the whole face; at x1 (his mask's level) with roughness 0.36 -> 0.50 (his is 0.66;
#: ours at 0.66 made the cheek too even) the forehead's excess 0.099 -> 0.021 (the layered tile on both). The nose
#: (a close view of its own, `parts_gate` "nose"): its pores x2 and microrelief x3 read as deep pits against his smooth
#: nose - microrelief x1 (his mask) and pores x0.6 bring its excess 0.171 -> 0.053
SCALE = (1.15, 1.35)
REGIONS = {k: (v[0] * SCALE[0], v[1] * SCALE[1], v[2]) for k, v in {
    "forehead": (2.0, 1.0, 0.50), "nose": (0.6, 1.0, 0.35), "chin": (1.5, 1.6, 0.45), "eyes": (0.6, 0.6, 0.50),
    "cheek": (1.0, 1.0, 0.48)}.items()}  # fmt: skip
#: the head tile's neck, down to the chest, is body skin (2026-11-06: as "cheek" it took the face's roughness and the
#: face's coat - a glossy band ending in a line across the chest on dark skin): the body tiles' values, and a face
#: share of 0 (1 elsewhere, `face_share.png`), softened like the rest - modules/skin/maps.py fades the clear coat and
#: the body's mottle by it
NECK_BELOW = 0.065  # m below the mouth: the chin's underside and down
SOFTEN = 4  # passes over the mesh's neighbours


def main() -> None:
    made = api.run("juststage.body.create", name="Face regions")
    api.run("juststage.head.add_parts", character=made.character)
    body = bpy.data.objects[made.object]
    co = build.shaped_coords(body)
    found = parts.parts_of(body)
    eyes = [np.array([v.co for v in found[k].data.vertices]) for k in ("eyeLeft", "eyeRight")]
    pupils = np.array([[e[:, 0].mean(), e[:, 1].min(), e[:, 2].mean()] for e in eyes])
    pupil_z, pupil_y = pupils[:, 2].mean(), pupils[:, 1].mean()
    teeth = np.array([v.co for v in found["teeth"].data.vertices])
    mouth_z = teeth[teeth[:, 1] < teeth[:, 1].min() + 0.004][:, 2].mean()
    x, y, z = co[:, 0], co[:, 1], co[:, 2]
    front = y < pupil_y + 0.03  # the face's front, not the sides of the head
    region = np.full(len(co), "cheek", dtype=object)
    region[front & (z > pupil_z + 0.022) & (z < pupil_z + 0.09) & (np.abs(x) < 0.065)] = "forehead"
    region[front & (np.abs(x) < 0.02) & (z < pupil_z - 0.004) & (z > mouth_z + 0.014) & (y < pupil_y - 0.006)] = "nose"
    region[front & (np.abs(x) < 0.03) & (z < mouth_z - 0.016) & (z > mouth_z - 0.06)] = "chin"
    near_eye = np.min(np.linalg.norm(co[:, None, :] - pupils[None, :, :], axis=2), axis=1) < 0.017
    region[front & near_eye] = "eyes"
    region[z < mouth_z - NECK_BELOW] = "neck"
    table = {**{k: (*v, 1.0) for k, v in REGIONS.items()}, "neck": (1.0, 1.0, material.ROUGHNESS, 0.0)}
    values = np.array([table[r] for r in region], np.float32)
    me = body.data
    edges = np.array([e.vertices for e in me.edges])
    for _ in range(SOFTEN):  # softened over the neighbours
        acc, cnt = values.copy(), np.ones(len(values), np.float32)
        np.add.at(acc, edges[:, 0], values[edges[:, 1]])
        np.add.at(acc, edges[:, 1], values[edges[:, 0]])
        np.add.at(cnt, edges[:, 0], 1)
        np.add.at(cnt, edges[:, 1], 1)
        values = acc / cnt[:, None]
    uv_layer = me.uv_layers[maps.UV].data
    image = np.zeros((SIZE, SIZE, 4), np.float32)
    image[..., 0], image[..., 2] = (REGIONS["cheek"][k] / RELIEF_SCALE for k in (0, 1))
    image[..., 1] = REGIONS["cheek"][2]
    image[..., 3] = 1.0
    for p in me.polygons:
        uvs = np.array([[uv_layer[i].uv.x - (HEAD_TILE - 1001), uv_layer[i].uv.y] for i in p.loop_indices])
        if not ((uvs >= 0) & (uvs <= 1)).all():
            continue
        vv = values[list(p.vertices)]
        for k in range(1, len(uvs) - 1):
            tri, val = uvs[[0, k, k + 1]] * SIZE - 0.5, vv[[0, k, k + 1]]
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
            inside = (w > -0.02).all(1)
            v = w[inside] @ val
            rows, cols = q[inside, 1].astype(int), q[inside, 0].astype(int)
            image[rows, cols, 0] = v[:, 0] / RELIEF_SCALE
            image[rows, cols, 2] = v[:, 1] / RELIEF_SCALE
            image[rows, cols, 1] = v[:, 2]
            image[rows, cols, 3] = v[:, 3]
    out = paths.GENERATED / "skin" / "face_regions.png"
    maps.write_png(out, image[..., :3])
    # the face's share in a map of its own (packed in the region map's alpha, the live view divided R, G, B by it)
    maps.write_png(out.with_name("face_share.png"), np.repeat(image[..., 3:4], 3, axis=2))
    counts = {r: int((region == r).sum()) for r in table}
    print(f"wrote {out}: vertices by region {counts}")


main()
