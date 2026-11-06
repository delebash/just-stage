# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body's skin from a bare-body scan - CC5's way (HD Aaron's body maps: skin variation, areolas, navel, a normal
map with the body's definition; ours were one flat colour and a flat normal - docs/plans/2026-11-06-inputs-audit.md
rows 10, 15). The face's scan route on the body: the scan placed on our body, our part wrapped onto it, its relief and
colour baked into our layout, kept as detail layers around 1 (the character's tone multiplies them in), hair out.

    python tools/dev.py blender -b --python tools/body_scan.py -- export [SOURCE]
    .dev/venv-tools/Scripts/python -I tools/body_scan.py fit [SOURCE]     (trimesh: the face route's wrap environment)
    python tools/dev.py blender -b --python tools/body_scan.py -- bake [SOURCE]
    .dev/venv-rdf/Scripts/python -I tools/body_scan.py post [SOURCE]

SOURCE (SOURCES):
- `artec` (default): the torso (tile 1002) from Artec 3D's "Body scan" (artec3d.com/3d-models/body-scan; its
  `license.txt`: CC BY 3.0 Unported, "Body scan by Artec 3D"), a lean athletic man, arms raised. The prototype
  (2026-11-05, scratchpad torso_*.py) baked against our unwrapped torso: the bake read the two bodies' difference in
  shape as relief; here our torso is wrapped onto the scan first (trimesh's Amberg non-rigid ICP, as the face route's
  `scan_fit.py`), so only the scan's own detail is left.
- `hsr0042`: the arms with the hands and the legs with the feet (tiles 1003, 1004) from HSRD-100's HSR0042-Body-045
  (CC BY 4.0, Digital Reality Lab; bare but for swim trunks and a cap, barefoot, near A-pose) - the gate's hand and
  foot views (2026-11-06): ours flat beside HD Aaron's veins, tendons and knuckle creases. Its arms hang ~20 deg out
  against our ~45: each limb is turned about its shoulder or hip to the scan (searched), its segments then aligned
  rigidly and blended at the joints, then wrapped (fit_limbs). The swim trunks are left out by their colour.
Writes `.dev/facetest/body/[SOURCE]/` (work files) and `extension/juststage/data/generated/skin/body_<tile>_relief.png`,
`body_<tile>_colour.png` with `body_<tile>.json`."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WORK_ROOT = ROOT / ".dev" / "facetest" / "body"
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "skin"
SCAN = ROOT / ".dev" / "downloads" / "artec_body_scan" / "x" / "3D body scan" / "Dima_body scan.obj"
#: each source: its scan, the scale to metres, the UDIM tiles (index past 1001) it gives, its fit, its credit
SOURCES = {
    "artec": {"scan": SCAN, "scale": 0.001, "tiles": (1,), "fit": "torso", "work": WORK_ROOT,
              "source": "Artec 3D, Body scan (artec3d.com/3d-models/body-scan)",
              "licence": "CC BY 3.0 Unported ('Body scan by Artec 3D')"},
    "hsr0042": {"scan": ROOT / ".dev" / "downloads" / "hsrd100" / "HSR0042-Body-045" / "x" / "HSR0042-Body-045_LOD0.obj",
                "image": ROOT / ".dev" / "downloads" / "hsrd100" / "HSR0042-Body-045" / "x" / "HSR0042-Body-045_LOD0_u0_v0_diffuse.png",
                "scale": 1.0, "tiles": (2, 3), "fit": "limbs", "work": WORK_ROOT / "hsr0042",
                "source": "HSRD-100, HSR0042-Body-045 (huggingface.co/datasets/digitalrealitylab/HSRD-100)",
                "licence": "CC BY 4.0 (Digital Reality Lab)"},
}  # fmt: skip
SIZE = 2048
RELIEF_HP_MM = 40.0  # the relief kept below this scale (the fit's leftover above it)
COLOUR_HP_MM = 60.0  # the colour's detail around 1: its regional tone above this is the character's
EDGE_FADE = 96.0  # texels (~4 cm) to full strength from the scan's and the tile island's edges
#: the limbs' joints (MakeHuman's joint helpers, each a vertex group of the body): per side, the arm's and the leg's
ARM = ("shoulder", "elbow", "hand", "finger-3-4")
LEG = ("upper-leg", "knee", "ankle", "toe-3-3")
TRUNK = ("pelvis", "neck", "head")
#: each joint's swing in the pose search (degrees each way): shoulder / elbow / wrist, hip / knee / ankle
SWING = {"arm": (70.0, 45.0, 30.0), "leg": (35.0, 35.0, 20.0)}
FLOOR = 0.006  # m: the scan's points below this (its floor sheet) are left out of the pose search
#: the fit's gap (m) up to which a texel takes the scan's detail fully, and past which none (limbs: hands, forearms and
#: feet lie within 3-10 mm after the wrap; upper arms, thighs and shins 9-16 mm, p90 30-56 - 2026-11-06)
FIT_GAP = (0.006, 0.012)
#: a fabric texel (the swim trunks, black): darker than this and greyer than this saturation
FABRIC_VALUE, FABRIC_SATURATION = 0.10, 0.25


def export(src: str = "artec") -> None:
    import importlib

    import bpy

    spec = SOURCES[src]
    work = spec["work"]
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
    joints = {}
    for g in body.vertex_groups:
        if g.name.startswith("joint-"):
            idx = [v.index for v in me.vertices if any(e.group == g.index for e in v.groups)]
            if idx:
                joints[g.name] = co[idx].mean(axis=0)
    work.mkdir(parents=True, exist_ok=True)
    np.savez(work / "ours.npz", co=co, tris=tris, tuv=tuv, tile=tile,
             joint_names=np.array(list(joints)), joint_co=np.array(list(joints.values())))  # fmt: skip
    bpy.ops.wm.obj_import(filepath=str(spec["scan"]), forward_axis="Y", up_axis="Z")
    scan = bpy.context.selected_objects[0]
    sm = scan.data
    sv = np.empty(len(sm.vertices) * 3, np.float64)
    sm.vertices.foreach_get("co", sv)
    sv = sv.reshape(-1, 3) * spec["scale"]
    sv[:, 2] -= sv[:, 2].min()
    sm.calc_loop_triangles()
    sf = np.empty(len(sm.loop_triangles) * 3, np.int64)
    sm.loop_triangles.foreach_get("vertices", sf)
    sl = np.empty(len(sm.loop_triangles) * 3, np.int64)
    sm.loop_triangles.foreach_get("loops", sl)
    suv = np.empty(len(sm.loops) * 2, np.float32)
    sm.uv_layers.active.data.foreach_get("uv", suv)
    suv = suv.reshape(-1, 2)[sl].reshape(-1, 3, 2)
    if "image" in spec:  # the download has no .mtl: the colour map beside the OBJ
        image_path = str(spec["image"])
    else:
        image = next(n.image for m in sm.materials for n in m.node_tree.nodes if n.type == "TEX_IMAGE")
        image_path = bpy.path.abspath(image.filepath)
    np.savez(work / "scan.npz", co=sv, faces=sf.reshape(-1, 3), uv=suv, image=image_path)
    print(f"EXPORT {src}: ours {len(co)} v, {len(tris)} tris, {len(joints)} joints; scan {len(sv)} v, {len(sf) // 3} "
          f"faces, colour {image_path}")


def _place_rigid(co, part_tris, sv, sf):
    """The scan to our height, centred on `part_tris`' vertices, its front on theirs, then rigid ICP on them (the
    torso's prototype steps). Returns the 4x4 placement."""
    import trimesh
    from trimesh import registration

    pv = np.unique(part_tris)
    t = co[pv]
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
    part = trimesh.Trimesh(co, part_tris, process=False)
    near = trimesh.proximity.ProximityQuery(part)
    rng = np.random.default_rng(0)
    for it in range(3):
        svp = (np.c_[sv, np.ones(len(sv))] @ place.T)[:, :3]
        sample = rng.choice(len(svp), min(120000, len(svp)), replace=False)
        _, dist, _ = near.on_surface(svp[sample])
        crop = svp[sample[dist < (0.04 if it == 0 else 0.02)]]
        m, _moved, cost = registration.icp(crop, t, threshold=1e-6, max_iterations=40, reflection=False, scale=False)
        place = m @ place
        print(f"ICP round {it}: {len(crop)} points, mean {cost * 1000:.1f} mm")
    return place


def _wrap(source_co, source_tris, target_v, target_f, label: str):
    """Our part wrapped onto the scan's surface near it: stiff to softer (the body's shape only - its pores and
    definition stay the scan's, for the bake to read)."""
    import trimesh
    from scipy.spatial import cKDTree
    from trimesh import registration

    near = trimesh.proximity.ProximityQuery(trimesh.Trimesh(source_co, source_tris, process=False))
    _, dv, _ = near.on_surface(target_v)
    keep_f = np.all((dv < 0.04)[target_f], axis=1)
    target = trimesh.Trimesh(target_v, target_f, process=False).submesh([np.flatnonzero(keep_f)], append=True)
    source = trimesh.Trimesh(source_co, source_tris, process=False)
    steps = [[0.02, 50, 0.5, 10], [0.02, 20, 0.5, 10], [0.02, 8, 0.5, 10], [0.02, 4, 0.5, 10]]
    fitted = registration.nricp_amberg(source, target, steps=steps, distance_threshold=0.04, use_faces=True,
                                       use_vertex_normals=True)  # fmt: skip
    d, _ = cKDTree(target.vertices).query(fitted)
    print(f"FIT {label} {len(source_co)} v: to the scan p50 {np.percentile(d, 50) * 1000:.1f} / p90 "
          f"{np.percentile(d, 90) * 1000:.1f} mm; moved p50 "
          f"{np.percentile(np.linalg.norm(fitted - source_co, axis=1), 50) * 1000:.1f} mm")
    return fitted


def fit(src: str = "artec") -> None:
    spec = SOURCES[src]
    work = spec["work"]
    o, s = np.load(work / "ours.npz"), np.load(work / "scan.npz", allow_pickle=True)
    if spec["fit"] == "limbs":
        return fit_limbs(src, o, s)
    co, tris, tile = o["co"], o["tris"], o["tile"]
    sv, sf = s["co"].astype(np.float64), s["faces"]
    torso_tris = tris[tile == spec["tiles"][0]]
    tv = np.unique(torso_tris)
    place = _place_rigid(co, torso_tris, sv, sf)
    svp = (np.c_[sv, np.ones(len(sv))] @ place.T)[:, :3]
    idx = -np.ones(len(co), int)
    idx[tv] = np.arange(len(tv))
    fitted = _wrap(co[tv], idx[torso_tris], svp, sf, "torso")
    np.savez(work / "fit.npz", place=place, fitted=fitted, moved_v=tv)


def _segment_labels(co, verts, chains):
    """Each vertex's nearest bone segment (point-to-segment distance) among `chains` (lists of joint points): (labels
    as (chain, segment) indices, the distance, the share t along its segment)."""
    best = np.full(len(verts), np.inf)
    lab = np.zeros((len(verts), 2), int)
    tt = np.zeros(len(verts))
    p = co[verts]
    for ci, chain in enumerate(chains):
        for si in range(len(chain) - 1):
            a, b = chain[si], chain[si + 1]
            ab = b - a
            t = np.clip(((p - a) @ ab) / max(ab @ ab, 1e-12), 0.0, 1.0)
            d = np.linalg.norm(p - (a + t[:, None] * ab), axis=1)
            better = d < best
            best[better], tt[better] = d[better], t[better]
            lab[better] = (ci, si)
    return lab, best, tt


def _rotation(axis, angle):
    axis = axis / np.linalg.norm(axis)
    k = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(angle) * k + (1 - np.cos(angle)) * (k @ k)


def fit_limbs(src: str, o, s) -> None:
    """Our arms and legs onto the scan's: placed rigidly by the torso, then each limb posed down its chain - at each
    joint (shoulder or hip, elbow or knee, wrist or ankle) everything below it turned by two angles (about the body's
    front-to-back and side-to-side axes) to lie closest to the scan, searched coarse then fine, blended into the joint
    over the first fifth of its segment - then all four wrapped. (Our A-pose bends the forearm 19 cm forward; the
    scan's arm hangs straight down: a turn at the shoulder alone left them 8 cm apart.)"""
    from scipy.spatial import cKDTree

    spec = SOURCES[src]
    work = spec["work"]
    co, tris, tile = o["co"].astype(np.float64), o["tris"], o["tile"]
    joints = dict(zip(o["joint_names"].tolist(), o["joint_co"], strict=True))
    sv, sf = s["co"].astype(np.float64), s["faces"]
    torso_tris = tris[tile == 1]
    place = _place_rigid(co, torso_tris, sv, sf)
    svp = (np.c_[sv, np.ones(len(sv))] @ place.T)[:, :3]
    tree = cKDTree(svp[svp[:, 2] > FLOOR])  # the scan's floor sheet out (it drew the feet onto it)
    limb_tris = tris[np.isin(tile, spec["tiles"])]
    lv = np.unique(limb_tris)
    trunk = [joints[f"joint-{n}"] for n in TRUNK]
    chains = [trunk]
    for side in ("l", "r"):
        chains.append([joints["joint-neck"], joints[f"joint-{side}-shoulder"]])
        chains.append([joints[f"joint-{side}-{n}"] for n in ARM])
        chains.append([joints["joint-pelvis"], joints[f"joint-{side}-upper-leg"]])
        chains.append([joints[f"joint-{side}-{n}"] for n in LEG])
    lab, _dist, tt = _segment_labels(co, lv, chains)
    posed = co.copy()
    pts = co[lv].copy()
    axes = (np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.0, 0.0]))  # front-to-back, side-to-side
    limbs = [(2, "l-arm"), (4, "l-leg"), (6, "r-arm"), (8, "r-leg")]
    rng = np.random.default_rng(1)
    for chain_i, name in limbs:
        chain = [c.copy() for c in chains[chain_i]]
        spans = SWING[name[2:]]
        mine = lab[:, 0] == chain_i
        for k in range(len(chain) - 1):
            below = mine & (lab[:, 1] >= k)
            # the joint's own segment blends in over its first fifth; the segments past it move whole
            w = np.where(lab[:, 1] > k, 1.0, np.clip(tt / 0.2, 0.0, 1.0)) * below
            w = w * w * (3 - 2 * w)
            # each segment below the joint weighs the same (the hand's 1,577 vertices outweighed the upper arm's 172)
            groups = []
            for seg in range(k, len(chain) - 1):
                on = np.flatnonzero(mine & (lab[:, 1] == seg) & ((seg > k) | (tt > 0.3)))
                if len(on) >= 20:
                    groups.append(rng.choice(on, min(300, len(on)), replace=False))
            if not groups:
                continue
            root = chain[k]

            def turned(a, b, root=root):
                return _rotation(axes[1], np.radians(b)) @ _rotation(axes[0], np.radians(a))

            best = (np.inf, 0.0, 0.0)
            for span, step in ((spans[k], 5.0), (6.0, 1.0)):  # coarse within the joint's swing, then fine
                ca, cb = best[1], best[2]
                for a in np.arange(ca - span, ca + span + 0.1, step):
                    for b in np.arange(cb - span, cb + span + 0.1, step):
                        if max(abs(a), abs(b)) > spans[k] + 1e-6:
                            continue
                        r = turned(a, b)
                        score = float(np.mean([np.median(tree.query((pts[g] - root) @ r.T + root)[0]) for g in groups]))
                        if score < best[0]:
                            best = (score, a, b)
            r = turned(best[1], best[2])
            moved = (pts - root) @ r.T + root
            pts = pts * (1 - w[:, None]) + moved * w[:, None]
            for j in range(k + 1, len(chain)):
                chain[j] = (chain[j] - root) @ r.T + root
            print(f"POSE {name} joint {k}: {best[1]:+.0f} / {best[2]:+.0f} deg, median gap {best[0] * 1000:.1f} mm")
    posed[lv] = pts
    idx = -np.ones(len(co), int)
    idx[lv] = np.arange(len(lv))
    fitted = _wrap(posed[lv], idx[limb_tris], svp, sf, "limbs")
    np.savez(work / "fit.npz", place=place, fitted=fitted, moved_v=lv, posed=posed[lv])


def bake(src: str = "artec") -> None:
    import bpy

    spec = SOURCES[src]
    work = spec["work"]
    o, s, f = np.load(work / "ours.npz"), np.load(work / "scan.npz", allow_pickle=True), np.load(work / "fit.npz")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device, scene.cycles.samples = "CPU", 4
    co = o["co"].copy()
    moved = f["moved_v"] if "moved_v" in f.files else f["torso_v"]
    co[moved] = f["fitted"]  # our part wrapped onto the scan: the bake reads only the scan's detail
    tris, tuv, tile = o["tris"], o["tuv"], o["tile"]
    me = bpy.data.meshes.new("ours")
    me.from_pydata(co.tolist(), [], tris.tolist())
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
    # each of our vertices' gap to the scan after the wrap: the post step takes the scan's detail only where it is small
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    scan_tree = BVHTree.FromPolygons(svp.tolist(), s["faces"].tolist())
    gap = np.array([(Vector(p) - scan_tree.find_nearest(Vector(p))[0]).length if scan_tree.find_nearest(Vector(p))[0]
                    is not None else 1.0 for p in co], np.float32)  # fmt: skip
    me.attributes.new("fitgap", "FLOAT", "POINT").data.foreach_set("value", gap)
    mat = bpy.data.materials.new("bake")
    node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    mat.node_tree.nodes.active = node
    me.materials.append(mat)
    gap_mat = bpy.data.materials.new("gap")
    gnt = gap_mat.node_tree
    gnt.nodes.clear()
    g_out = gnt.nodes.new("ShaderNodeOutputMaterial")
    g_attr = gnt.nodes.new("ShaderNodeAttribute")
    g_attr.attribute_name = "fitgap"
    g_emit = gnt.nodes.new("ShaderNodeEmission")
    gnt.links.new(g_attr.outputs["Fac"], g_emit.inputs["Color"])
    gnt.links.new(g_emit.outputs["Emission"], g_out.inputs["Surface"])
    g_node = gnt.nodes.new("ShaderNodeTexImage")
    gnt.nodes.active = g_node
    for number in spec["tiles"]:
        flat = tuv.reshape(-1, 2).copy()
        flat[:, 0] -= number
        flat[np.repeat(tile, 3) != number] += 10.0
        layer = me.uv_layers.get("Tile") or me.uv_layers.new(name="Tile")
        layer.data.foreach_set("uv", flat.ravel())
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
            np.save(work / f"bake_{kind.lower()}_{1001 + number}.npy", px)
            print(f"BAKED {kind} {1001 + number}")
        if spec["fit"] == "limbs":  # the fit's gap on this tile (our own surface's attribute, emitted)
            img = bpy.data.images.new("GAP", SIZE, SIZE, alpha=False, float_buffer=True)
            img.colorspace_settings.name = "Non-Color"
            g_node.image = img
            me.materials[0] = gap_mat
            bpy.ops.object.select_all(action="DESELECT")
            ours.select_set(True)
            bpy.context.view_layer.objects.active = ours
            bpy.ops.object.bake(type="EMIT", margin=16, use_clear=True, uv_layer="Tile")
            px = np.array(img.pixels[:], np.float32).reshape(SIZE, SIZE, 4)[::-1, :, 0]
            np.save(work / f"bake_fitgap_{1001 + number}.npy", px)
            me.materials[0] = mat
            print(f"BAKED GAP {1001 + number}")


def _mm_per_uv(tile_number: int) -> float:
    """maps.MM_PER_UV for the tile, read from the add-on's source (this runs outside Blender)."""
    import re

    src = (ROOT / "extension" / "juststage" / "modules" / "skin" / "maps.py").read_text(encoding="utf-8")
    m = re.search(r"MM_PER_UV\s*=\s*\{([^}]*)\}", src)
    table = dict(re.findall(r"(\d{4}):\s*([0-9.]+)", m.group(1)))
    return float(table[str(tile_number)])


def post(src: str = "artec") -> None:
    import cv2

    sys.path.insert(0, str(ROOT / "tools" / "face_test"))
    import hair  # noqa: E402

    spec = SOURCES[src]
    work = spec["work"]
    o = np.load(work / "ours.npz")
    tuv, tile = o["tuv"], o["tile"]
    for number in spec["tiles"]:
        name = 1001 + number
        legacy = work / "bake_normal.npy"  # the torso's work files before sources (2026-11-06)
        nrm_path = work / f"bake_normal_{name}.npy"
        nrm = np.load(nrm_path if nrm_path.exists() else legacy).astype(np.float32)
        col_path = work / f"bake_diffuse_{name}.npy"
        col = np.load(col_path if col_path.exists() else work / "bake_diffuse.npy").astype(np.float32)
        cover = np.zeros((SIZE, SIZE), np.uint8)
        for tri in tuv[tile == number]:
            pts = np.round(np.c_[(tri[:, 0] - number) * SIZE, (1 - tri[:, 1]) * SIZE]).astype(np.int32)
            cv2.fillConvexPoly(cover, pts, 1)
        baked = (np.abs(nrm - [0.5, 0.5, 1.0]).sum(-1) > 1e-4) & (col.max(-1) > 0.02) & (cover > 0)
        hsv = cv2.cvtColor(np.clip(col, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
        fabric = (hsv[..., 2] < FABRIC_VALUE) & (hsv[..., 1] < FABRIC_SATURATION)
        fabric = cv2.dilate(fabric.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0  # the trunks out, their edge too
        baked &= ~fabric
        baked = cv2.erode(baked.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        px_per_mm = SIZE / _mm_per_uv(name)
        w = baked.astype(np.float32)
        gap_path = work / f"bake_fitgap_{name}.npy"
        if gap_path.exists():  # where our wrapped surface lies off the scan, its detail would land displaced: faded out
            gap = np.load(gap_path).astype(np.float32)
            close = 1.0 - np.clip((gap - FIT_GAP[0]) / (FIT_GAP[1] - FIT_GAP[0]), 0.0, 1.0)
            w = w * close * close * (3 - 2 * close)
            baked = baked & (close > 0.0)

        def mblur(img, sigma, w=w):
            num = cv2.GaussianBlur(img * w[..., None], (0, 0), sigma)
            den = cv2.GaussianBlur(w, (0, 0), sigma)
            return num / np.maximum(den[..., None], 1e-6)

        # relief: the tangent xy over its own wide blur (the fit's leftover out), faded at the island's edge
        xy = nrm[..., :2] * 2 - 1
        hp = (xy - mblur(xy, RELIEF_HP_MM * px_per_mm / 2.0)) * w[..., None]
        # faded out well inside the scan's reach and the tile's own island: no step where the detail ends
        edge = np.clip(np.minimum(cv2.distanceTransform(baked.astype(np.uint8), cv2.DIST_L2, 5),
                                  cv2.distanceTransform(cover, cv2.DIST_L2, 5)) / EDGE_FADE, 0, 1)  # fmt: skip
        edge = edge * edge * (3 - 2 * edge)
        hp *= edge[..., None]
        debris = hair.relief_debris(hp, 0.3, 8).astype(np.float32)  # rings and arcs at the scan's holes and edges
        hp *= (1.0 - np.clip(cv2.GaussianBlur(debris, (0, 0), 2.0) * 1.5, 0.0, 1.0))[..., None]
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
        cv2.imwrite(str(OUT / f"body_{name}_relief.png"),
                    np.round(np.clip(relief[..., ::-1], 0, 1) * 65535).astype(np.uint16))  # fmt: skip
        cv2.imwrite(str(OUT / f"body_{name}_colour.png"),
                    np.round(np.clip(ratio[..., ::-1] / 2, 0, 1) * 65535).astype(np.uint16))  # fmt: skip
        info = {"tile": name, "size": SIZE, "source": spec["source"], "licence": spec["licence"],
                "relief_hp_mm": RELIEF_HP_MM, "colour_hp_mm": COLOUR_HP_MM,
                "colour": "a ratio around 1, stored halved (0.5 = 1)", "strands_filled": int(found.sum()),
                "fabric_out": int(fabric.sum()), "covered": float(baked.mean())}  # fmt: skip
        (OUT / f"body_{name}.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
        print(f"POST {name}: relief and colour written; {found.sum()} strand texels filled; {fabric.sum()} fabric "
              f"texels out; tile covered {baked.mean():.1%}")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    {"export": export, "fit": fit, "bake": bake, "post": post}[argv[0]](*(argv[1:2] or ["artec"]))
