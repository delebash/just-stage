# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage base v2's record (extension/juststage/modules/body/base.py): hm08's lid anatomy, measured once on
MakeHuman's own base mesh (MPFB2's `base.obj`, CC0) with GNM's eyes fitted to it, and kept as generated data.

    python tools/dev.py blender -b --python tools/make_base_v2.py

1. The lid ring per eye: the closed loop of edges between skin faces facing away from the eyeball and socket faces
   facing it (normal-to-eye dot threshold 0), the longest single cycle kept (docs/plans/2026-11-05-research-base-mesh.md
   §7: 40 and 38 edges on the library's man).
2. The cut: every edge crossing the ring (one end on it) cut once by Blender's subdivide - the new vertices appended.
3. The rows: each ring vertex with its two new neighbours - the farther from the eyeball the lash line, the nearer the
   rim - placed along their own lines from the eye's centre at LASH / MARGIN / RIM mm off the eyeball.
4. The record: the cut's vertex pairs; each appended vertex's birth (its edge's ends, a third vertex of the face) and its
   offset in that face's frame; the ring vertices' moves; the rows; the topology's hash.

Writes `extension/juststage/data/generated/base/v2.json`.
"""

from __future__ import annotations

import importlib
import json

import bmesh
import bpy
import numpy as np
from mathutils import Vector

paths = importlib.import_module("bl_ext.system.juststage.paths")
makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
mhclo = importlib.import_module("bl_ext.system.juststage.core.mhclo")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
eyes = importlib.import_module("bl_ext.system.juststage.modules.head.eyes")

LASH, MARGIN, RIM = 2.6, 1.3, 0.25  # mm off the eyeball (the prototype's, measured against HD Aaron's band)
#: the caruncle: the skin within CARUNCLE m of each eye's inner corner (the ring's vertex nearest the nose), wet pink
#: like the margin (design piece 3; proof 4c, 2026-11-05: "the corner skin painted wet pink ... shows, as on Aaron")
CARUNCLE = 0.0028
HM08 = makehuman.HM08_VERTICES


def coords(me) -> np.ndarray:
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", co)
    return co.reshape(-1, 3).astype(np.float64)


def spheres(co: np.ndarray) -> list[tuple[np.ndarray, float]]:
    """GNM's eyes fitted to this shape (their MHCLO binding), as eye_layers._eye_sphere measures a fitted eye."""
    found = []
    for part in ("eyeLeft", "eyeRight"):
        pts = mhclo.fit(parts._binding(part), co)
        lo, hi = pts.min(axis=0), pts.max(axis=0)
        found.append(((lo + hi) / 2, float((hi - lo)[[0, 2]].mean() / 2)))
    return found


def _prune(es: set, ev: dict) -> tuple[set, dict]:
    es = set(es)
    while True:
        deg: dict = {}
        for e in es:
            for v in ev[e]:
                deg[v] = deg.get(v, 0) + 1
        dead = {e for e in es if any(deg[v] == 1 for v in ev[e])}
        if not dead:
            return es, deg
        es -= dead


def _longest_cycle(edges, ev) -> set:
    es, deg = _prune(edges, ev)
    branch = [v for v, d in deg.items() if d > 2]
    if not branch:
        return es
    best, best_n = es, -1
    for e in sorted(e for e in es if any(v in branch for v in ev[e])):
        es2, deg2 = _prune(es - {e}, ev)
        if es2 and all(d == 2 for d in deg2.values()) and len(es2) > best_n:
            best, best_n = es2, len(es2)
    return best


def rings(me, co: np.ndarray, eye_spheres) -> tuple[list[set], dict]:
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    ev = {e.index: tuple(v.index for v in e.verts) for e in bm.edges}
    found = []
    for c, r in eye_spheres:
        side = {}
        for f in bm.faces:
            vi = [v.index for v in f.verts]
            if max(vi) >= makehuman.BODY_VERTICES:
                continue
            fc = co[vi].mean(0)
            if np.linalg.norm(fc - c) > r + 0.006 or fc[1] > c[1] + 0.004:
                continue
            p = [Vector(co[i]) for i in vi]
            n = Vector((0, 0, 0))
            for i in range(len(p)):
                n += p[i].cross(p[(i + 1) % len(p)])
            to = (c - fc) / np.linalg.norm(c - fc)
            side[f.index] = 1 if np.array(n.normalized()) @ to > 0.0 else -1
        edges = [e.index for e in bm.edges if len(e.link_faces) == 2 and all(f.index in side for f in e.link_faces)
                 and side[e.link_faces[0].index] != side[e.link_faces[1].index]]  # fmt: skip
        found.append(_longest_cycle(edges, ev))
    bm.free()
    return found, ev


def crossing_pairs(me, ring_edges: list[set], ev: dict) -> list[tuple[int, int]]:
    """Every edge of the faces along the rings with one end on a ring - as vertex pairs, in edge order."""
    ring_verts = {v for es in ring_edges for e in es for v in ev[e]}
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.edges.ensure_lookup_table()
    cross = set()
    for es in ring_edges:
        for ei in es:
            for f in bm.edges[ei].link_faces:
                for e in f.edges:
                    a, b = (v.index for v in e.verts)
                    if (a in ring_verts) != (b in ring_verts):
                        cross.add(e.index)
    pairs = [tuple(ev[i]) for i in sorted(cross)]
    bm.free()
    return pairs


def births(me_v1, pairs, after: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Each appended vertex's edge (found by where the cut put it: its edge's middle) and a third vertex of a face on
    that edge (the lowest-numbered face; its vertex after the edge's second end)."""
    co = coords(me_v1)
    mids = np.array([(co[a] + co[b]) / 2 for a, b in pairs])
    faces_of: dict = {}
    for p in me_v1.polygons:
        vs = list(p.vertices)
        for k in range(len(vs)):
            faces_of.setdefault(frozenset((vs[k], vs[(k + 1) % len(vs)])), []).append(vs)
    parents = []
    for v in after[HM08:]:
        k = int(np.argmin(np.linalg.norm(mids - v, axis=1)))
        if np.linalg.norm(mids[k] - v) > 1e-7:
            raise RuntimeError(f"an appended vertex is not on a cut edge's middle ({np.linalg.norm(mids[k] - v)})")
        a, b = pairs[k]
        face = faces_of[frozenset((a, b))][0]
        third = next(x for x in face[face.index(b) :] + face[: face.index(b)] if x not in (a, b))
        parents.append((a, b, third))
    return np.array(parents, dtype=np.int64), np.full(len(parents), 0.5)


def open_probe():
    """The default human with its eyes opened as a dressed one's (body_create.EYE_OPEN) and GNM's eyes fitted: the
    lids as characters wear them, where the ring between lid skin and socket is found (on MakeHuman's own, nearly
    closed lids it runs into the corners' folds - 50 and 52 edges, 62 of 100 ring vertices with a clean row)."""
    create = importlib.import_module("bl_ext.system.juststage.modules.body.body_create")
    sliders = importlib.import_module("bl_ext.system.juststage.modules.body.sliders")
    values = create.Params()._asdict()
    for k in ("name", "dressed"):
        values.pop(k)
    probe = build.create_human("ring probe", values, base_version=1)  # hm08 itself: the ring is found on it
    for slider, value in create.EYE_OPEN.items():
        sliders.apply(probe, sliders.catalog()[slider], value)
    parts.add(probe)
    eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
    found = parts.parts_of(probe)
    return probe, build.shaped_coords(probe), [eye_layers._eye_sphere(found[p]) for p in ("eyeLeft", "eyeRight")]


def main() -> None:
    probe, shaped, open_spheres = open_probe()
    ring_edges, ev = rings(probe.data, shaped, open_spheres)
    print("RINGS", [len(r) for r in ring_edges], flush=True)
    pairs = crossing_pairs(probe.data, ring_edges, ev)
    obj = build._import_base("JustStage base v2 source")
    me = obj.data
    v1 = me.copy()  # the untouched hm08, for the births
    co = coords(me)
    eye_spheres = spheres(co)
    base.cut(me, pairs)
    after = coords(me)
    parents, t = births(v1, pairs, after)
    n = len(me.vertices)
    nbrs: dict = {}
    for e in me.edges:
        a, b = e.vertices
        nbrs.setdefault(a, []).append(b)
        nbrs.setdefault(b, []).append(a)
    ring_verts = sorted({v for es in ring_edges for e in es for v in ev[e]})
    target = after.copy()
    out_rows = []
    odd = []
    for i in ring_verts:
        new = [j for j in nbrs[i] if j >= HM08]
        c, r = min(eye_spheres, key=lambda s: np.linalg.norm(after[i] - s[0]))
        off = {j: np.linalg.norm(after[j] - c) - r for j in [i, *new]}
        if len(new) == 2:
            lash, rim = sorted(new, key=lambda j: off[j], reverse=True)
        elif len(new) == 1:  # a corner, where the ring turns through one face: one side only
            odd.append((i, 1))
            lash, rim = (new[0], -1) if off[new[0]] > off[i] else (-1, new[0])
        else:
            odd.append((i, 0))
            continue
        for j, mm in ((lash, LASH), (i, MARGIN), (rim, RIM)):
            if j < 0:
                continue
            d = (after[j] - c) / np.linalg.norm(after[j] - c)
            target[j] = c + d * (r + mm / 1000)
        out_rows.append((lash, i, rim))
    old_target = target[:HM08]
    moved = np.flatnonzero(np.linalg.norm(old_target - after[:HM08], axis=1) > 0)
    app = makehuman.Appended.measure(old_target, parents, t, target[HM08:])
    check = makehuman.place_appended(old_target, app)
    print("RING VERTICES", len(ring_verts), "WITHOUT A CLEAN ROW", odd, flush=True)
    print("APPENDED", n - HM08, "ROWS", len(out_rows), "MOVED", len(moved),
          "CHECK mm", float(np.abs(check - target[HM08:]).max() * 1000), flush=True)  # fmt: skip
    caruncle = []
    for c, _r in eye_spheres:
        mine = [i for i in ring_verts if np.linalg.norm(target[i] - c) < 0.02]
        corner = min(mine, key=lambda i: abs(target[i][0]))  # nearest the nose (x 0)
        near = np.flatnonzero(np.linalg.norm(target[:HM08] - target[corner], axis=1) < CARUNCLE)
        inside = np.abs(target[near, 0]) >= abs(target[corner][0]) - 0.0003  # in the opening, not on the nose's side
        caruncle += [int(i) for i in near[inside] if i < makehuman.BODY_VERTICES]
    print("CARUNCLE", len(caruncle), flush=True)
    record = {
        "baseVersion": base.VERSION,
        "from": "MPFB2 base.obj (hm08, CC0) + tools/make_base_v2.py",
        "radii_mm": {"lash": LASH, "margin": MARGIN, "rim": RIM},
        "cut": [list(map(int, p)) for p in pairs],
        "appended": {"parents": parents.tolist(), "t": t.tolist(), "local": app.local.tolist()},
        "moved": {"index": moved.tolist(), "delta": (old_target[moved] - after[moved]).tolist()},
        "rows": [list(map(int, r)) for r in out_rows],
        "caruncle": caruncle,
        "topology": base.topology_hash(me),
        "vertices": n,
    }
    folder = paths.GENERATED / "base"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "v2.json").write_text(json.dumps(record), encoding="utf-8")
    print("WROTE", folder / "v2.json", n, "vertices", flush=True)
    bpy.data.meshes.remove(v1)


main()
