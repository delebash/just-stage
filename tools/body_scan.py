# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body's skin from a bare-body scan - CC5's way (HD Aaron's body maps: skin variation, areolas, navel, a normal
map with the body's definition; ours were one flat colour and a flat normal - docs/plans/2026-11-06-inputs-audit.md
rows 10, 15). The face's scan route on the torso (tile 1002): the scan placed on our body, our torso wrapped onto it,
its relief and colour baked into our layout, kept as detail layers around 1 (the character's tone multiplies them in),
hair out.

    python tools/dev.py blender -b --python tools/body_scan.py -- export
    .dev/venv-tools/Scripts/python -I tools/body_scan.py fit     (trimesh: the face route's wrap environment)
    python tools/dev.py blender -b --python tools/body_scan.py -- bake
    .dev/venv-rdf/Scripts/python -I tools/body_scan.py post

Source: Artec 3D's "Body scan" (artec3d.com/3d-models/body-scan; its `license.txt`: CC BY 3.0 Unported, "Body scan by
Artec 3D"), a lean athletic man, arms raised - the torso only (the arms are raised: tile 1003 waits for a scan in our
pose). The prototype (2026-11-05, scratchpad torso_*.py) baked against our unwrapped torso: the bake read the two bodies'
difference in shape as relief (blotches and edge stripes); here our torso is wrapped onto the scan first (trimesh's
Amberg non-rigid ICP, as the face route's `scan_fit.py`), so only the scan's own detail is left.
Writes `.dev/facetest/body/` (work files) and `extension/juststage/data/generated/skin/body_1002_relief.png` and
`body_1002_colour.png` with `body_1002.json`."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".dev" / "facetest" / "body"
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "skin"
SCAN = ROOT / ".dev" / "downloads" / "artec_body_scan" / "x" / "3D body scan" / "Dima_body scan.obj"
TILE = 1  # 1002, the torso
SIZE = 2048
RELIEF_HP_MM = 40.0  # the relief kept below this scale (the fit's leftover above it)
COLOUR_HP_MM = 60.0  # the colour's detail around 1: its regional tone above this is the character's
EDGE_FADE = 96.0  # texels (~4 cm) to full strength from the scan's and the tile island's edges


def export() -> None:
    import importlib

    import bpy

    api = importlib.import_module("bl_ext.system.juststage.api")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
    made = api.run("juststage.body.create", name="Body scan", gender=1.0)
    body = bpy.data.objects[made.object]
    co = build.shaped_coords(body)
    skin = makehuman.skin_mask(len(co))
    me = body.data
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers["UDIM"].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    tris, tuv = [], []
    for p in me.polygons:
        vs, ls = list(p.vertices), list(p.loop_indices)
        if not skin[vs].all():
            continue
        for k in range(1, len(vs) - 1):
            tris.append([vs[0], vs[k], vs[k + 1]])
            tuv.append([uv[ls[0]], uv[ls[k]], uv[ls[k + 1]]])
    tris, tuv = np.array(tris), np.array(tuv)
    tile = np.floor(tuv[:, :, 0].mean(1)).astype(int)
    WORK.mkdir(parents=True, exist_ok=True)
    np.savez(WORK / "ours.npz", co=co, tris=tris, tuv=tuv, tile=tile)
    bpy.ops.wm.obj_import(filepath=str(SCAN), forward_axis="Y", up_axis="Z")
    scan = bpy.context.selected_objects[0]
    sv = np.array([v.co for v in scan.data.vertices]) * 0.001
    sv[:, 2] -= sv[:, 2].min()
    sf = np.array([p.vertices[:] for p in scan.data.polygons])
    suv = np.array([scan.data.uv_layers.active.data[li].uv[:] for p in scan.data.polygons for li in p.loop_indices])
    image = next(n.image for m in scan.data.materials for n in m.node_tree.nodes if n.type == "TEX_IMAGE")
    np.savez(WORK / "scan.npz", co=sv, faces=sf, uv=suv.reshape(len(sf), 3, 2), image=bpy.path.abspath(image.filepath))
    print(f"EXPORT ours {len(co)} v, {len(tris)} tris; scan {len(sv)} v, {len(sf)} faces, colour {image.filepath}")


def fit() -> None:
    import trimesh
    from scipy.spatial import cKDTree
    from trimesh import registration

    o, s = np.load(WORK / "ours.npz"), np.load(WORK / "scan.npz", allow_pickle=True)
    co, tris, tile = o["co"], o["tris"], o["tile"]
    sv, sf = s["co"].astype(np.float64), s["faces"]
    torso_tris = tris[tile == TILE]
    tv = np.unique(torso_tris)
    t = co[tv]
    # placed: the scan to our height, centred, its front on our torso's front, then rigid ICP on the torso (the
    # prototype's steps)
    k = co[:, 2].max() / sv[:, 2].max()
    place = np.diag([k, k, k, 1.0])
    sv0 = sv * k
    lo, hi = t.min(0), t.max(0)
    shift = np.zeros(3)
    shift[0] = np.median(t[:, 0]) - np.median(sv0[(sv0[:, 2] > lo[2]) & (sv0[:, 2] < hi[2]), 0])
    zs = np.linspace(lo[2] + 0.08, hi[2] - 0.08, 7)
    fo = [t[np.abs(t[:, 2] - z) < 0.01, 1].min() for z in zs]
    fs = [(sv0 + shift)[(np.abs(sv0[:, 2] - z) < 0.005) & (np.abs(sv0[:, 0] + shift[0] - np.median(t[:, 0])) < 0.12), 1].min()
          for z in zs]  # fmt: skip
    shift[1] = float(np.median(np.array(fo) - np.array(fs)))
    place[:3, 3] = shift
    torso = trimesh.Trimesh(co, torso_tris, process=False)
    near = trimesh.proximity.ProximityQuery(torso)
    rng = np.random.default_rng(0)
    for it in range(3):
        svp = (np.c_[sv, np.ones(len(sv))] @ place.T)[:, :3]
        sample = rng.choice(len(svp), min(120000, len(svp)), replace=False)
        _, dist, _ = near.on_surface(svp[sample])
        crop = svp[sample[dist < (0.04 if it == 0 else 0.02)]]
        m, _moved, cost = registration.icp(crop, t, threshold=1e-6, max_iterations=40, reflection=False, scale=False)
        place = m @ place
        print(f"ICP round {it}: {len(crop)} points, mean {cost * 1000:.1f} mm")
    svp = (np.c_[sv, np.ones(len(sv))] @ place.T)[:, :3]
    _, dv, _ = near.on_surface(svp)
    keep_f = np.all((dv < 0.04)[sf], axis=1)
    target = trimesh.Trimesh(svp, sf, process=False).submesh([np.flatnonzero(keep_f)], append=True)
    idx = -np.ones(len(co), int)
    idx[tv] = np.arange(len(tv))
    source = trimesh.Trimesh(t, idx[torso_tris], process=False)
    # stiff to softer: the body's shape only (its pores and definition stay the scan's, for the bake to read)
    steps = [[0.02, 50, 0.5, 10], [0.02, 20, 0.5, 10], [0.02, 8, 0.5, 10], [0.02, 4, 0.5, 10]]
    fitted = registration.nricp_amberg(source, target, steps=steps, distance_threshold=0.04, use_faces=True,
                                       use_vertex_normals=True)  # fmt: skip
    d, _ = cKDTree(target.vertices).query(fitted)
    print(f"FIT torso {len(tv)} v: to the scan p50 {np.percentile(d, 50) * 1000:.1f} / p90 "
          f"{np.percentile(d, 90) * 1000:.1f} mm; moved p50 {np.percentile(np.linalg.norm(fitted - t, axis=1), 50) * 1000:.1f} mm")
    np.savez(WORK / "fit.npz", place=place, fitted=fitted, torso_v=tv)


def bake() -> None:
    import bpy

    o, s, f = np.load(WORK / "ours.npz"), np.load(WORK / "scan.npz", allow_pickle=True), np.load(WORK / "fit.npz")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device, scene.cycles.samples = "CPU", 4
    co = o["co"].copy()
    co[f["torso_v"]] = f["fitted"]  # our torso wrapped onto the scan: the bake reads only the scan's detail
    tris, tuv, tile = o["tris"], o["tuv"], o["tile"]
    me = bpy.data.meshes.new("ours")
    me.from_pydata(co.tolist(), [], tris.tolist())
    flat = tuv.reshape(-1, 2).copy()
    flat[:, 0] -= TILE
    flat[np.repeat(tile, 3) != TILE] += 10.0
    me.uv_layers.new(name="Tile").data.foreach_set("uv", flat.ravel())
    me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
    ours = bpy.data.objects.new("ours", me)
    scene.collection.objects.link(ours)
    ours.modifiers.new("sub", "SUBSURF").levels = 1
    place = f["place"]
    svp = (np.c_[s["co"], np.ones(len(s["co"]))] @ place.T)[:, :3]
    sm = bpy.data.meshes.new("scan")
    sm.from_pydata(svp.tolist(), [], s["faces"].tolist())
    sm.polygons.foreach_set("use_smooth", np.ones(len(sm.polygons), bool))
    sm.uv_layers.new(name="UV").data.foreach_set("uv", s["uv"].reshape(-1, 2).astype(np.float32).ravel())
    smat = bpy.data.materials.new("scan colour")
    tex = smat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(s["image"]))
    bsdf = next(n for n in smat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    smat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    sm.materials.append(smat)
    scan = bpy.data.objects.new("scan", sm)
    scene.collection.objects.link(scan)
    mat = bpy.data.materials.new("bake")
    node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    mat.node_tree.nodes.active = node
    me.materials.append(mat)
    bpy.ops.object.select_all(action="DESELECT")
    scan.select_set(True)
    ours.select_set(True)
    bpy.context.view_layer.objects.active = ours
    for kind, extra in (("NORMAL", {"normal_space": "TANGENT"}), ("DIFFUSE", {"pass_filter": {"COLOR"}})):
        img = bpy.data.images.new(kind, SIZE, SIZE, alpha=False, float_buffer=True)
        img.colorspace_settings.name = "Non-Color"
        img.generated_color = (0.5, 0.5, 1.0, 1.0) if kind == "NORMAL" else (0.0, 0.0, 0.0, 1.0)
        node.image = img
        bpy.ops.object.bake(type=kind, use_selected_to_active=True, cage_extrusion=0.01, max_ray_distance=0.03,
                            margin=16, use_clear=False, uv_layer="Tile", **extra)  # fmt: skip
        px = np.array(img.pixels[:], np.float32).reshape(SIZE, SIZE, 4)[::-1, :, :3]
        np.save(WORK / f"bake_{kind.lower()}.npy", px)
        print(f"BAKED {kind}")


def post() -> None:
    import cv2

    sys.path.insert(0, str(ROOT / "tools" / "face_test"))
    import hair  # noqa: E402

    o = np.load(WORK / "ours.npz")
    nrm = np.load(WORK / "bake_normal.npy").astype(np.float32)
    col = np.load(WORK / "bake_diffuse.npy").astype(np.float32)
    tuv, tile = o["tuv"], o["tile"]
    cover = np.zeros((SIZE, SIZE), np.uint8)
    for tri in tuv[tile == TILE]:
        pts = np.round(np.c_[(tri[:, 0] - TILE) * SIZE, (1 - tri[:, 1]) * SIZE]).astype(np.int32)
        cv2.fillConvexPoly(cover, pts, 1)
    baked = (np.abs(nrm - [0.5, 0.5, 1.0]).sum(-1) > 1e-4) & (col.max(-1) > 0.02) & (cover > 0)
    baked = cv2.erode(baked.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    # the tile's mm per texel (maps.MM_PER_UV for 1002 over SIZE)
    sys.path.insert(0, str(ROOT / "extension"))
    mm_per_uv = 1100.0  # placeholder replaced below from the add-on's own constant
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("maps_consts", ROOT / "extension" / "juststage" / "modules" /
                                                      "skin" / "maps.py")  # fmt: skip
        src = spec.origin and Path(spec.origin).read_text(encoding="utf-8")
        import re

        m = re.search(r"MM_PER_UV\s*=\s*\{[^}]*1002:\s*([0-9.]+)", src)
        mm_per_uv = float(m.group(1)) if m else mm_per_uv
    except Exception:  # noqa: BLE001
        pass
    px_per_mm = SIZE / mm_per_uv
    w = baked.astype(np.float32)

    def mblur(img, sigma):
        num = cv2.GaussianBlur(img * w[..., None], (0, 0), sigma)
        den = cv2.GaussianBlur(w, (0, 0), sigma)
        return num / np.maximum(den[..., None], 1e-6)

    # relief: the tangent xy over its own wide blur (the fit's leftover out), faded at the island's edge
    xy = nrm[..., :2] * 2 - 1
    hp = (xy - mblur(xy, RELIEF_HP_MM * px_per_mm / 2.0)) * w[..., None]
    # faded out well inside the scan's reach and the tile's own island (its border with the arms' and head's tiles):
    # no step where the detail ends (the gate's torso view showed patches at the shoulders)
    edge = np.clip(np.minimum(cv2.distanceTransform(baked.astype(np.uint8), cv2.DIST_L2, 5),
                              cv2.distanceTransform(cover, cv2.DIST_L2, 5)) / EDGE_FADE, 0, 1)  # fmt: skip
    edge = edge * edge * (3 - 2 * edge)
    hp *= edge[..., None]
    z = np.sqrt(np.clip(1 - (hp**2).sum(-1), 0, 1))
    relief = np.dstack([hp * 0.5 + 0.5, z])
    # colour: hair out, then its detail around 1 (log, over its blur at COLOUR_HP_MM), faded at the edge
    lin = np.maximum(col, 1e-4)
    found = hair.mask(lin, baked)
    lin = np.maximum(hair.fill(lin, found), 1e-4)
    ratio_log = np.log(lin) - np.log(np.maximum(mblur(lin, COLOUR_HP_MM * px_per_mm / 2.0), 1e-4))
    ratio_log = np.clip(ratio_log, -0.5, 0.3) * w[..., None] * edge[..., None]
    ratio = np.exp(ratio_log)
    OUT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / "body_1002_relief.png"), np.round(np.clip(relief[..., ::-1], 0, 1) * 65535).astype(np.uint16))
    cv2.imwrite(str(OUT / "body_1002_colour.png"), np.round(np.clip(ratio[..., ::-1] / 2, 0, 1) * 65535).astype(np.uint16))
    info = {"tile": 1002, "size": SIZE, "source": "Artec 3D, Body scan (artec3d.com/3d-models/body-scan)",
            "licence": "CC BY 3.0 Unported ('Body scan by Artec 3D')", "relief_hp_mm": RELIEF_HP_MM,
            "colour_hp_mm": COLOUR_HP_MM, "colour": "a ratio around 1, stored halved (0.5 = 1)",
            "strands_filled": int(found.sum()), "covered": float(baked.mean())}  # fmt: skip
    (OUT / "body_1002.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(f"POST: relief and colour written; {found.sum()} strand texels filled; tile covered {baked.mean():.1%}")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    {"export": export, "fit": fit, "bake": bake, "post": post}[argv[0]]()
