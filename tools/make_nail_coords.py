# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Each nail's own coordinates on the body's nail tile (UDIM 1005, `tools/make_udim.py`), for the layered nail shader
(rec 14, the realism brief §6.14; modules/skin/maps.py): made once on the default human and kept as generated data,
like the layout itself.

    python tools/dev.py blender -b --python tools/make_nail_coords.py

Per nail (a connected island of the tile's polygons): its distal direction from MakeHuman's joint groups - the
nearest digit's tip joint and the joint before it - and its own normal; per vertex, `along` (0 at the cuticle, 1 at
the free edge) and `across` (-1 to 1); per nail, which digit (thumb 1 to little 5; toes 6 to 10) - the lunula's
visibility differs by digit (the gaps research §3). Rasterised into the tile's UV square.

Writes `extension/juststage/data/generated/skin/nails.png`: 16-bit RGBA, 1024², R along, G (across + 1) / 2, B digit / 10,
A inside a nail."""

from __future__ import annotations

import importlib

import bpy
import numpy as np

api = importlib.import_module("bl_ext.system.juststage.api")
paths = importlib.import_module("bl_ext.system.juststage.paths")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")

SIZE = 1024
NAIL_TILE = 1005


def _joints(body) -> dict[str, np.ndarray]:
    co = np.empty(len(body.data.vertices) * 3)
    body.data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    names = {g.index: g.name for g in body.vertex_groups}
    groups: dict[str, list[int]] = {}
    for v in body.data.vertices:
        for g in v.groups:
            name = names.get(g.group, "")
            if name.startswith("joint-") and ("finger" in name or "toe" in name) and g.weight > 0.5:
                groups.setdefault(name, []).append(v.index)
    return {k: co[v].mean(0) for k, v in groups.items()}


def _tips(joints: dict[str, np.ndarray]) -> list[tuple[int, np.ndarray, np.ndarray]]:
    """(digit, tip, the joint before it) for every finger and toe: the last joint of each chain."""
    out = []
    for side in ("l", "r"):
        for kind, base in (("finger", 0), ("toe", 5)):
            for digit in range(1, 6):
                chain = sorted((k for k in joints if k.startswith(f"joint-{side}-{kind}-{digit}-")),
                               key=lambda k: int(k.rsplit("-", 1)[1]))
                if len(chain) >= 2:
                    out.append((base + digit, joints[chain[-1]], joints[chain[-2]]))
    return out


def _raster(uv: np.ndarray, values: np.ndarray, image: np.ndarray, tris: np.ndarray) -> None:
    """Each triangle's corner values (n, 4) interpolated over its texels (barycentric), into `image` (SIZE, SIZE, 4)."""
    for tri in tris:
        p = uv[tri] * SIZE - 0.5
        lo = np.floor(p.min(0)).astype(int)
        hi = np.ceil(p.max(0)).astype(int)
        xs, ys = np.meshgrid(np.arange(max(lo[0], 0), min(hi[0], SIZE - 1) + 1),
                             np.arange(max(lo[1], 0), min(hi[1], SIZE - 1) + 1))
        q = np.stack([xs.ravel(), ys.ravel()], -1).astype(np.float64)
        a, b, c = p
        m = np.array([[b[0] - a[0], c[0] - a[0]], [b[1] - a[1], c[1] - a[1]]])
        if abs(np.linalg.det(m)) < 1e-12:
            continue
        st = (q - a) @ np.linalg.inv(m).T
        w = np.stack([1 - st[:, 0] - st[:, 1], st[:, 0], st[:, 1]], -1)
        inside = (w > -0.02).all(1)
        if not inside.any():
            continue
        vals = w[inside] @ values[tri]
        image[q[inside, 1].astype(int), q[inside, 0].astype(int)] = vals


def nails(body) -> list[dict]:
    """Each nail of the body's nail tile: its island's polygons and vertices, its digit and its frame - the centre, the
    normal, the distal direction (to the nearest digit's tip joint, flattened onto the nail) and the side."""
    me = body.data
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    layer = me.uv_layers[maps.UV].data
    tips = _tips(_joints(body))
    # the tile's polygons, grouped into islands by shared vertices
    polys = [p for p in me.polygons if 1001 + int(np.floor(np.mean([layer[i].uv.x for i in p.loop_indices]))) == NAIL_TILE]
    parent = {}

    def find(v):
        while parent.setdefault(v, v) != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    for p in polys:
        vs = list(p.vertices)
        for v in vs[1:]:
            parent[find(v)] = find(vs[0])
    islands: dict[int, list] = {}
    for p in polys:
        islands.setdefault(find(p.vertices[0]), []).append(p)
    out = []
    for members in islands.values():
        verts = sorted({v for p in members for v in p.vertices})
        centre = co[verts].mean(0)
        normal = np.mean([np.array(p.normal) for p in members], 0)
        normal /= np.linalg.norm(normal)
        digit, tip, before = min(tips, key=lambda t: np.linalg.norm(t[1] - centre))
        distal = tip - before
        distal -= normal * (distal @ normal)
        distal /= np.linalg.norm(distal)
        out.append({"polygons": members, "verts": verts, "digit": digit, "centre": centre, "normal": normal,
                    "distal": distal, "side": np.cross(normal, distal)})
    return out


def main() -> None:
    made = api.run("juststage.body.create", name="Nail coords")
    body = bpy.data.objects[made.object]
    me = body.data
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    layer = me.uv_layers[maps.UV].data
    found = nails(body)
    image = np.zeros((SIZE, SIZE, 4), np.float32)
    for nail in found:
        members, verts, digit = nail["polygons"], nail["verts"], nail["digit"]
        centre, distal, side = nail["centre"], nail["distal"], nail["side"]
        along = (co[verts] - centre) @ distal
        across = (co[verts] - centre) @ side
        a = {v: (x - along.min()) / max(along.max() - along.min(), 1e-6) for v, x in zip(verts, along, strict=True)}
        half = max(np.abs(across).max(), 1e-6)
        c = {v: x / half for v, x in zip(verts, across, strict=True)}
        for p in members:
            loops = list(p.loop_indices)
            uv = np.array([[layer[i].uv.x - (NAIL_TILE - 1001), layer[i].uv.y] for i in loops])
            values = np.array([[a[v], (c[v] + 1) / 2, digit / 10, 1.0] for v in p.vertices], np.float32)
            for k in range(1, len(loops) - 1):  # a fan of triangles
                _raster(uv, values, image, np.array([[0, k, k + 1]]))
    import OpenImageIO as oiio

    out = paths.GENERATED / "skin" / "nails.png"
    spec = oiio.ImageSpec(SIZE, SIZE, 4, oiio.UINT16)
    writer = oiio.ImageOutput.create(str(out))
    writer.open(str(out), spec)
    writer.write_image(np.ascontiguousarray(image[::-1]))  # PNG rows top first; UV v up
    writer.close()
    print(f"wrote {out}: {len(found)} nails, {(image[..., 3] > 0).mean():.1%} of the tile")


if __name__ == "__main__":
    main()
