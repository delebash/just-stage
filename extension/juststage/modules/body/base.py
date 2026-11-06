# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage base v2: hm08 whole, with the lid anatomy it lacks appended after its 19,158 vertices
(docs/plans/2026-11-05-character-design.md piece 1, approved 2026-11-05; the code plan
docs/plans/2026-11-05-lid-anatomy-build.md, approved 2026-11-06).

hm08's lid edge is one ring of vertices standing off the eyeball (measured: up to 3.3 mm, a dark crevice); real lids
and HD Aaron's have a margin - a lash line, the margin's flat, a rim on the eyeball. Base v2 cuts one loop each side of
that ring (Blender's own subdivide: every old index, UV, vertex group and shape key kept, the new ones interpolated)
and shapes the three rows against the eyeball: lash line 2.6 mm, margin 1.3 mm, rim 0.25 mm off it (the prototype's
measured band, 28-50 px against Aaron's 26-63 px).

`upgrade` turns any hm08 character into base v2 - a new one (`build.create_human`, after its UDIM layout, so the new
faces share their old faces' place in every skin's maps) and a saved one (`migrations`): the cut, then every shape
key's appended vertices placed by their birth faces (`makehuman.Appended`, Blender's Surface Deform method) and the
base's own moves added. `extend` carries every target loaded later onto the appended vertices.

NOT STANDARD (approved 2026-11-05: "yes non standard is approved if you cant find any other way"): appending to
MakeHuman's base; the standard alternatives, MakeHuman's proxy or another base, lose exactly at the lids. The record of
the cut and the shaping is made once by `tools/make_base_v2.py` (`data/generated/base/v2.json`), frozen by a hash of
the resulting topology."""

from __future__ import annotations

import functools
import hashlib
import json

import bpy
import numpy as np

from ... import paths
from ...core import makehuman

VERSION = 2
TOOL = "python tools/dev.py blender -b --python tools/make_base_v2.py"
CREASE = 0.6  # both rims' edge crease: they stay crisp under Catmull-Clark (the prototype's)
MARGIN_ATTR = "js_margin"  # the margin's share per vertex - its wet pink in the skin material
CONTACT = "JustStage eyelid contact"  # the refit shape key that keeps the rim on the eyeball (head/parts.py)


@functools.cache
def record() -> dict:
    """`data/generated/base/v2.json`: the cut (hm08 vertex pairs), the appended vertices' births and offsets, hm08
    vertices the base moves, the lid rows and the topology's hash."""
    return json.loads(paths.generated("base", "v2.json", tool=TOOL).read_text(encoding="utf-8"))


@functools.cache
def appended() -> makehuman.Appended:
    a = record()["appended"]
    return makehuman.Appended(
        np.array(a["parents"], dtype=np.int64), np.array(a["t"], dtype=np.float64), np.array(a["local"], np.float64)
    )


def rows() -> np.ndarray:
    """The lid's rows: (lash line, margin, rim) vertex indices, one row per vertex of hm08's old lid ring; -1 where a
    corner row has no lash line or no rim (the ring turns through one face there)."""
    return np.array(record()["rows"], dtype=np.int64)


def topology_hash(mesh: bpy.types.Mesh) -> str:
    corners = np.empty(len(mesh.loops), np.int32)
    mesh.loops.foreach_get("vertex_index", corners)
    sizes = np.empty(len(mesh.polygons), np.int32)
    mesh.polygons.foreach_get("loop_total", sizes)
    return hashlib.sha256(corners.tobytes() + sizes.tobytes()).hexdigest()


def cut(mesh: bpy.types.Mesh, pairs) -> None:
    """One cut through each hm08 edge in `pairs` (vertex index pairs), as Blender's subdivide makes it - the new
    vertices appended, every layer (UVs, vertex groups, shape keys, attributes) interpolated onto them."""
    import bmesh

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    edges = []
    for a, b in pairs:
        edge = bm.edges.get((bm.verts[a], bm.verts[b]))
        if edge is None:
            bm.free()
            raise ValueError(f"no edge {a}-{b}: not hm08's topology")
        edges.append(edge)
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def _key_arrays(mesh: bpy.types.Mesh) -> list:
    keys = mesh.shape_keys
    return list(keys.key_blocks) if keys else []


def place(co: np.ndarray) -> np.ndarray:
    """A whole shape (n x 3, n = hm08's + the appended) in base v2's way from its hm08 part: the base's moves added to
    hm08's vertices, the appended vertices placed by their faces."""
    rec = record()
    co = co.astype(np.float64).copy()
    moved = rec["moved"]
    co[np.array(moved["index"], dtype=np.int64)] += np.array(moved["delta"], dtype=np.float64)
    co[makehuman.HM08_VERTICES :] = makehuman.place_appended(co[: makehuman.HM08_VERTICES], appended())
    return co


def upgrade(obj: bpy.types.Object) -> bool:
    """An hm08 character (base v1) made base v2 in place - the cut, every shape key and the basis placed, the rims
    creased and the margin marked. Returns False when it is base v2 already."""
    me = obj.data
    if obj.juststage.base_version >= VERSION:
        return False
    if len(me.vertices) != makehuman.HM08_VERTICES:
        raise ValueError(f"{obj.name}: {len(me.vertices)} vertices, not hm08's {makehuman.HM08_VERTICES}")
    rec = record()
    from ..skin import maps

    maps.add_layout(obj)  # the UDIM layout is per hm08 loop: on before the cut, so the new faces take their place in it
    levels = _drop_levels(obj)
    cut(me, rec["cut"])
    if topology_hash(me) != rec["topology"]:
        raise RuntimeError(f"{obj.name}: the cut made another topology than base v2's record ({TOOL} again?)")
    n = len(me.vertices)
    buf = np.empty(n * 3, np.float32)
    blocks = _key_arrays(me)
    for block in blocks or [None]:
        data = block.data if block is not None else me.vertices
        data.foreach_get("co", buf)
        data.foreach_set("co", place(buf.reshape(-1, 3)).astype(np.float32).ravel())
    mark(me)
    me.update()
    obj.juststage.base_version = VERSION
    if levels:
        from . import build

        build.set_levels(obj, *levels)
    return True


def mark(me: bpy.types.Mesh) -> None:
    """Both rims creased (the lash line's row and the rim's row), the margin's share in `js_margin`."""
    r = rows()
    lash, rim = set(r[:, 0].tolist()) - {-1}, set(r[:, 2].tolist()) - {-1}
    edges = np.empty(len(me.edges) * 2, np.int32)
    me.edges.foreach_get("vertices", edges)
    edges = edges.reshape(-1, 2)
    on = np.array([(a in lash and b in lash) or (a in rim and b in rim) for a, b in edges.tolist()])
    crease = me.attributes.get("crease_edge") or me.attributes.new("crease_edge", "FLOAT", "EDGE")
    crease.data.foreach_set("value", np.where(on, CREASE, 0.0).astype(np.float32))
    share = np.zeros(len(me.vertices), np.float32)
    share[r[:, 1]] = 1.0
    share[r[r[:, 2] >= 0, 2]] = 1.0
    share[r[r[:, 0] >= 0, 0]] = 0.35  # the lash line: the margin's pink fades into the lid's skin across it
    share[record().get("caruncle", [])] = 1.0  # the inner corner's wet pink tissue
    attr = me.attributes.get(MARGIN_ATTR) or me.attributes.new(MARGIN_ATTR, "FLOAT", "POINT")
    attr.data.foreach_set("value", share)


def _drop_levels(obj: bpy.types.Object) -> tuple[int, int] | None:
    """The Multires levels taken off before the topology changes (its per-corner data is tied to the old corners),
    to be made again on the new mesh; None when there were none."""
    from . import build

    mod = obj.modifiers.get(build.LEVELS)
    if mod is None:
        return None
    levels = (mod.render_levels, mod.levels)
    obj.modifiers.remove(mod)
    return levels


def extend(obj: bpy.types.Object, index: np.ndarray, delta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """A target's hm08 (indices, offsets in metres) for this character: on base v2 also its appended vertices,
    carried by their faces from the character's rest shape."""
    if len(obj.data.vertices) <= makehuman.HM08_VERTICES:
        return index, delta
    rest = np.empty(len(obj.data.vertices) * 3, np.float32)
    keys = obj.data.shape_keys
    (keys.reference_key.data if keys else obj.data.vertices).foreach_get("co", rest)
    rest = rest.reshape(-1, 3)[: makehuman.HM08_VERTICES]
    return makehuman.extend_offsets(index, delta, rest, appended())
