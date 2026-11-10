# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Each nail's own coordinates over its whole fingertip or toe tip, per vertex of the body, for the layered nail
shader (rec 14, the realism brief §6.14; modules/skin/maps.py `NAIL_ATTR`): made once on the default human and kept
as generated data, like the layout itself.

    python tools/dev.py blender -b --python tools/make_nail_coords.py

Per nail - one of the nail tile's islands (UDIM 1005, `tools/make_udim.py`) - its frame: the distal direction from
MakeHuman's joint groups (the nearest digit's tip joint and the joint before it), flattened onto the island's own
normal. Its region: the body's vertices nearer this nail's centre than any other's, facing its way, within GROW x
the island's reach. Per vertex there, `along` (0 at the island's proximal edge - the cuticle line - to 1 at the
fingertip's far end) and `across` (-1 to 1 over the fingertip's own dorsal width: its vertices facing within 60 deg of
the nail's normal); per nail, which digit (thumb 1 to little 5; toes 6 to 10) - the lunula's visibility differs by
digit (the gaps research §3).

2026-11-10 (the own-content proof, `docs/plans/2026-11-08-own-content-proof.md` 13:5x-14:3x): until then the
coordinates filled the tile's island alone, rasterised into its UV square (`nails.png`); the island is a coarse
polygon of hm08's fingertip faces (13 corners), so the plate came out an octagon ~55% of the finger's width where
HD Aaron's spans ~77% and reaches the tip. Over the whole fingertip the shader draws a plate of its own outline.

Writes `extension/juststage/data/generated/skin/nails.npz`: `coords` (vertices x 4, float32: along, (across + 1) / 2,
digit / 10, 1 inside a fingertip's region), `vertices` (the body's vertex count it was made on)."""

from __future__ import annotations

import importlib

import bpy
import numpy as np

api = importlib.import_module("bl_ext.system.juststage.api")
paths = importlib.import_module("bl_ext.system.juststage.paths")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")

NAIL_TILE = 1005
GROW = 2.2  # a fingertip's region: within this many times its island's reach from the island's centre
DORSAL = 0.5  # cos of the angle off the nail's normal that still counts as the fingertip's back (60 deg)
BEHIND_M = 0.004  # the region reaches this far proximal of the island's edge (room for the fold)


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


def vertex_coords(body, grow: float = GROW) -> tuple[np.ndarray, dict]:
    """Per vertex (n, 4): each nail's coordinates over its whole fingertip - along, (across + 1) / 2, digit / 10 and
    1 inside a fingertip's region (0 elsewhere) - and, per digit, (the fingertip's length from the island's edge, its
    dorsal width, the island's length and width (mm), the region's vertices) for the record."""
    me = body.data
    n = len(me.vertices)
    co = np.empty(n * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    nor = np.empty(n * 3)
    me.vertices.foreach_get("normal", nor)
    nor = nor.reshape(-1, 3)
    frames = nails(body)
    centres = np.array([f["centre"] for f in frames])
    nearest = np.argmin(((co[:, None, :] - centres[None]) ** 2).sum(-1), 1)
    out = np.zeros((n, 4), np.float32)
    stats = {}
    for k, f in enumerate(frames):
        c, nrm, dis, sid = f["centre"], f["normal"], f["distal"], f["side"]
        isl = np.array(f["verts"])
        reach = np.linalg.norm(co[isl] - c, axis=1).max()
        a_isl = (co[isl] - c) @ dis
        a0 = a_isl.min()
        rel = co - c
        facing = nor @ nrm
        region = (nearest == k) & (np.linalg.norm(rel, axis=1) < grow * reach) & (facing > 0.0) & (rel @ dis > a0 - BEHIND_M)
        idx = np.flatnonzero(region)
        if len(idx) < 4:
            continue
        al, ac = rel[idx] @ dis, rel[idx] @ sid
        end = al.max()  # the fingertip's far end
        top = facing[idx] > DORSAL  # its dorsal face
        mid = top & (al > a0) & (al < a0 + 0.7 * (end - a0))
        half = np.abs(ac[mid]).max() if mid.any() else np.abs(ac).max()
        out[idx, 0] = (al - a0) / max(end - a0, 1e-6)
        out[idx, 1] = (np.clip(ac / max(half, 1e-6), -1.5, 1.5) + 1.0) / 2.0
        out[idx, 2] = f["digit"] / 10.0
        out[idx, 3] = 1.0
        stats[f["digit"]] = (round(float((end - a0) * 1000), 1), round(float(half * 2000), 1),
                             round(float((a_isl.max() - a0) * 1000), 1),
                             round(float(np.abs((co[isl] - c) @ sid).max() * 2000), 1), len(idx))
    return out, stats


def main() -> None:
    made = api.run("juststage.body.create", name="Nail coords")
    body = bpy.data.objects[made.object]
    coords, stats = vertex_coords(body)
    out = paths.GENERATED / "skin" / "nails.npz"
    np.savez_compressed(out, coords=coords, vertices=np.int64(len(body.data.vertices)))
    print(f"wrote {out}: {len(stats)} digits, {int((coords[:, 3] > 0).sum())} vertices in a fingertip's region")
    for digit, s in sorted(stats.items()):
        print(f"  digit {digit}: fingertip {s[0]} mm x {s[1]} mm, island {s[2]} x {s[3]} mm, {s[4]} vertices")


if __name__ == "__main__":
    main()
