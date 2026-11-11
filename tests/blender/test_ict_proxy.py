# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""ICT-FaceKit's head as a proxy over hm08's (modules/head/ict_proxy.py, Q-BASE-4 - docs/plans/2026-11-10-ict-head.md
§0): it sits on the character's head at any shape - its eye openings on our lids' rims, our brows' roots on its surface
- the body's covered faces stay hidden across a skin change, and it follows a slider made after it was added."""

import importlib

import bpy
import numpy as np
import pytest
from mathutils.bvhtree import BVHTree

api = importlib.import_module("bl_ext.system.juststage.api")
base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
ict_proxy = importlib.import_module("bl_ext.system.juststage.modules.head.ict_proxy")
brows_mod = importlib.import_module("bl_ext.system.juststage.modules.hair.brows")


def _evaluated(obj) -> np.ndarray:
    dg = bpy.context.evaluated_depsgraph_get()
    mesh = obj.evaluated_get(dg).to_mesh()
    co = np.empty(len(mesh.vertices) * 3, np.float32)
    mesh.vertices.foreach_get("co", co)
    obj.evaluated_get(dg).to_mesh_clear()
    m = np.array(obj.matrix_world)
    return co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]


def _rim_edges(body) -> np.ndarray:
    """Our lids' rims as segments at the character's shape, world space: the mesh's edges joining two rim vertices -
    the generator snaps the openings onto these edges, not onto the vertices (`tools/gate/ict_head.py`). The shape
    from `build.shaped_coords` (hm08's numbering, the keys mixed - muted keys left out); not the evaluated cage, whose
    helper mask renumbers the lid cut's vertices (2026-11-10: index 19161 of 13,508)."""
    m = np.array(body.matrix_world)
    co = build.shaped_coords(body) @ m[:3, :3].T + m[:3, 3]
    rims = base.rows()[:, 2]
    rim = set(rims[rims >= 0].tolist())
    return np.array([[co[e.vertices[0]], co[e.vertices[1]]] for e in body.data.edges
                     if e.vertices[0] in rim and e.vertices[1] in rim])


def _off(points: np.ndarray, seg: np.ndarray) -> np.ndarray:
    """Each point's distance to the nearest segment."""
    ab = seg[:, 1] - seg[:, 0]
    t = ((points[:, None, :] - seg[None, :, 0, :]) * ab[None]).sum(2) / np.maximum((ab * ab).sum(1), 1e-12)[None]
    near = seg[None, :, 0, :] + np.clip(t, 0.0, 1.0)[..., None] * ab[None]
    return np.linalg.norm(near - points[:, None, :], axis=2).min(axis=1)


def _eye_openings(head, seg: np.ndarray) -> np.ndarray:
    """The proxy's eye openings' vertices: its border vertices within 10 mm of our rims (its other borders - the neck,
    the mouth - are centimetres away)."""
    count = {}
    for poly in head.data.polygons:
        vs = list(poly.vertices)
        for a, b in zip(vs, vs[1:] + vs[:1], strict=True):
            e = (min(a, b), max(a, b))
            count[e] = count.get(e, 0) + 1
    border = np.array(sorted({v for e, n in count.items() if n == 1 for v in e}))
    pts = _evaluated(head)[border]
    return pts[_off(pts, seg) < 0.01]


def _openings_off(body, head) -> np.ndarray:
    seg = _rim_edges(body)
    return _off(_eye_openings(head, seg), seg)


def _at_basis(body, head) -> np.ndarray:
    """The openings' distance to the rims where the head was placed and bound - every key muted, hm08's basis: the
    placement's own residual (the generator spreads its snap over 1.5 mm and creases the lid after it)."""
    keys = body.data.shape_keys.key_blocks
    was = [k.mute for k in keys]
    for k in keys:
        k.mute = True
    bpy.context.view_layer.update()
    try:
        return _openings_off(body, head)
    finally:
        for k, w in zip(keys, was, strict=True):
            k.mute = w
        bpy.context.view_layer.update()


@pytest.mark.parametrize("macros", [{}, {"gender": 0.0}, {"gender": 1.0}, {"age": 0.0}, {"age": 1.0},
                                    {"weight": 0.0}, {"weight": 1.0}])
def test_the_ict_head_sits_on_the_characters_head_at_any_shape(macros):
    made = api.run("juststage.body.create", name="ICT proxy test", **macros)
    body = bpy.data.objects[made.object]
    head = ict_proxy.add(body)
    placed = np.percentile(_at_basis(body, head), 90)
    assert placed < 0.0015, f"the placement's own residual grew ({placed:.4f})"  # 2026-11-10's generator: ~1.2 mm
    off = np.percentile(_openings_off(body, head), 90)
    assert off < placed + 0.0003, f"{macros}: the eye openings left our rims ({off:.4f}, placed {placed:.4f})"


@pytest.mark.xfail(strict=True, reason="OPEN (2026-11-10 23:4x): with ICT's lids kept 8-15 mm the brows' lower roots "
                   "lie up to ~2 mm under the head (p90 2.1 mm); the 6-10 keep frees them but its lids need ICT's own "
                   "UVs and a skin re-bake - the proxy's build job (docs/plans/2026-11-10-ict-head.md)")
def test_the_brows_roots_lie_on_the_ict_head():
    made = api.run("juststage.body.create", name="ICT proxy brows")
    body = bpy.data.objects[made.object]
    head = ict_proxy.add(body)
    brows = brows_mod.make(body)  # a bare body.create has none (a dressed character grows them - body_create._dress)
    curves = brows.evaluated_get(bpy.context.evaluated_depsgraph_get()).data  # hair: its roots, as test_hair reads them
    pos = np.empty(len(curves.points) * 3, dtype=np.float32)
    curves.attributes["position"].data.foreach_get("vector", pos)
    roots = pos.reshape(-1, 3)[[c.first_point_index for c in curves.curves]]
    roots = roots @ np.array(brows.matrix_world)[:3, :3].T + np.array(brows.matrix_world)[:3, 3]
    head_co = _evaluated(head)
    tree = BVHTree.FromPolygons(head_co.tolist(), [list(p.vertices) for p in head.data.polygons])
    gaps = [tree.find_nearest(r.tolist())[3] for r in roots]
    assert np.percentile(gaps, 90) < 0.001, f"the brows' roots off the head ({np.percentile(gaps, 90):.4f})"


def _mapped_skin(folder):
    """A small mapped skin saved in a library folder (test_skin_maps' helper's way): flat tiles."""
    made = api.run("juststage.body.create", name="Skin source")
    body = bpy.data.objects[made.object]
    api.run("juststage.skin.set_tone", character=made.character, melanin=0.3)  # the skin material is made here
    mat = body.juststage.skin_material
    mat.juststage.map_melanin = 0.3
    images = {}
    for channel in maps.CHANNELS:
        for number in maps.TILES:
            colour = np.broadcast_to({"normal": (0.5, 0.5, 1.0)}.get(channel, (0.5,) * 3), (8, 8, 3))
            maps.write_png(folder / f"test.{channel}.{number}.png", colour)
        images[channel] = maps.tiled_image(folder, f"test.{channel}")
    maps.build_material(mat, images)
    out = api.run("juststage.library.save", character=made.character, catalog="Skins", name="Test mapped",
                  licence="CC0-1.0", provenance="test", library=str(folder / "lib"))  # fmt: skip
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(body)
    return out.path


def test_the_covered_faces_stay_hidden_across_a_skin_change(tmp_path):
    """A library skin swaps into the skin's own slot by name (maps.py); the hidden slot under the head stays."""
    made = api.run("juststage.body.create", name="ICT proxy skin")
    body = bpy.data.objects[made.object]
    ict_proxy.add(body)
    hidden = [p.index for p in body.data.polygons
              if body.data.materials[p.material_index].name == ict_proxy.HIDDEN]
    assert len(hidden) > 1000  # the face and head under it
    api.run("juststage.library.add", path=_mapped_skin(tmp_path), character=made.character)
    assert all(body.data.materials[body.data.polygons[i].material_index].name == ict_proxy.HIDDEN for i in hidden)
    assert ict_proxy.of(body).data.materials[0] == body.juststage.skin_material


def test_the_ict_head_follows_a_slider_moved_after_it(tmp_path):
    made = api.run("juststage.body.create", name="ICT proxy slider")
    body = bpy.data.objects[made.object]
    head = ict_proxy.add(body)
    before = _evaluated(head)
    api.run("juststage.body.set_slider", character=made.character, slider="height", value=1.0)
    bpy.context.view_layer.update()
    assert np.linalg.norm(_evaluated(head) - before, axis=1).max() > 0.002  # it moved with the body
    api.run("juststage.body.set_slider", character=made.character, slider="weight", value=1.0)  # the face reshaped
    bpy.context.view_layer.update()
    off = np.percentile(_openings_off(body, head), 90)
    assert off < np.percentile(_at_basis(body, head), 90) + 0.0003
