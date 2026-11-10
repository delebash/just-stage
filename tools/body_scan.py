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
  foot views (2026-11-06): ours flat beside HD Aaron's veins, tendons and knuckle creases. Fitted through Anny
  (fit_anny: its pose and body sliders by gradient descent, then the wrap) - run its fit in `.dev/venv-rdf` (torch,
  anny). The swim trunks are left out by their colour; the scan's detail is taken only where the fit lies close.
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
TEN24 = ROOT / ".dev" / "downloads" / "ten24_sample" / "x" / "OBJ Package"
#: each source: its scan, the scale to metres, the UDIM tiles (index past 1001) it gives, its fit, its credit
SOURCES = {
    "artec": {"scan": SCAN, "scale": 0.001, "tiles": (1,), "fit": "torso", "work": WORK_ROOT, "debris_limit": 0.8,
              # the scanned man's own marks out (the composition's rule): his appendectomy scar - a curved dent on the
              # lower right abdomen, 8 cm right of and 4 cm below our navel on every man (2026-11-09, the torso view;
              # found in the relief at this texel, top-first rows): (x, y) on tile 1002 at SIZE, radius mm
              "marks_out": [((318, 712), 20.0)],  # 20 mm: the scar runs ~3 cm (14 left its end)
              "source": "Artec 3D, Body scan (artec3d.com/3d-models/body-scan)",
              "licence": "CC BY 3.0 Unported ('Body scan by Artec 3D')"},
    "hsr0042": {"scan": ROOT / ".dev" / "downloads" / "hsrd100" / "HSR0042-Body-045" / "x" / "HSR0042-Body-045_LOD0.obj",
                "image": ROOT / ".dev" / "downloads" / "hsrd100" / "HSR0042-Body-045" / "x" / "HSR0042-Body-045_LOD0_u0_v0_diffuse.png",
                "scale": 1.0, "tiles": (2, 3), "fit": "anny", "work": WORK_ROOT / "hsr0042",
                # no colour detail: his dense leg hair, filled, left speckle and polygon cells - brown patches with
                # edges on every man's thighs at the full view; with the colour neutral they're gone (2026-11-10,
                # `men_legs_colour.png`); the hands keep Ten24's own colour (the "hands" part)
                "no_colour": True,
                # the legs' relief under 6 mm only: at 40 the fit's leftover drew lumps on the thighs (the relief-only
                # render, `men_legs_layers.png`); the arms keep 40 (their veins, no lumps seen)
                "relief_hp_mm": {1004: 6.0},
                "source": "HSRD-100, HSR0042-Body-045 (huggingface.co/datasets/digitalrealitylab/HSRD-100)",
                "licence": "CC BY 4.0 (Digital Reality Lab)"},
    "ten24": {"scan": TEN24 / "OBJ" / "Decimated" / "Ten24_Sample_100k.OBJ", "image": TEN24 / "Colour Maps" / "JPG" / "Colour_8k.jpg",
              "normal": TEN24 / "Normal Maps" / "Level_01_Normal.PSD", "axes": ("NEGATIVE_Z", "Y"),
              "scale": 1.0, "tiles": (2,), "fit": "anny", "part": "hands", "work": WORK_ROOT / "ten24",
              "edge_fade": 24.0,
              # only detail under 12 mm: its Level_01 map holds everything between its coarse level-1 surface and the
              # scan, so on the 100k mesh the medium shape counted twice (blotches, 2026-11-07); tendons, veins and
              # creases are all narrower
              "relief_hp_mm": 12.0,
              # the part's tilt x1.5: at x1 the back of the hand's ridges read 0.47 of HD Aaron's, at x1.5 with the
              # colour 0.74-0.80 and its form within his band (1.24, band 29%) - factors.py, 2026-11-07
              "strength": 1.5,  # texels (~9 mm): a finger is ~160 texels round on this tile - 96 would fade it out
              "source": "Ten24, the free sample scan (3dscanstore.com - the page saved 2026-11-04)",
              "licence": "Ten24's grant: 'Feel free to use this scan as you wish for both commercial and personal projects. "
                         "All we ask is that you provide us with a credit wherever it's used'"},
    # the feet (2026-11-08, the own-content proof: ours smooth plastic beside HD Aaron's tendons and veins; no detailed
    # donor until this): Thunk3D's "Leg-foot", a left leg and foot, geometry only (the original STL, millimetres, lying
    # on its side) - placed by our left foot (mirrored on our right), our feet wrapped onto it, their relief baked as a
    # part onto both tiles a foot lies on (1003 holds most of its faces, 1004 the heel's strip, measured 2026-11-08);
    # the wrap's move smoothed first (a soft wrap follows the tendons and the bake reads them flat), the debris limit
    # past a tendon's slope, no fade at the islands' seams
    "thunk3d_foot": {"scan": ROOT / ".dev" / "downloads" / "sketchfab_leg_foot_2026-11-08" / "foot" / "left_foot_02.stl",
                     "scale": 0.001, "tiles": (2, 3), "fit": "foot", "part": "feet", "geometry_only": True,
                     "work": WORK_ROOT / "thunk3d_foot", "edge_fade": 24.0, "relief_hp_mm": 25.0, "fit_smooth": 10,
                     "debris_limit": 0.8, "island_fade": False,
                     "source": "Thunk3D, 'Leg-foot' (sketchfab.com/3d-models/leg-foot-37e2802a104141b982e15eda21d425ec, by "
                               "Diana Liu: 'Leg-foot scan by Thunk3D Fisher's 3D scanner')",
                     "licence": "CC Attribution (Sketchfab's CC BY 4.0): 'Author must be credited. Commercial use is allowed'"},
    # the women's torso (the plan's Q-BODY-3, 2026-11-10): Blender Studio's CC0 realistic_body_female at its top
    # Multires level (tools/export_bs_female.py) - a sculpt, not a scan: geometry only; our body exported as a woman;
    # its relief written beside the men's as `body_1002_female_*` (build_skins gives it to women's skins)
    # the women's limbs (the plan's Q-BODY-3 option "the HSRD bare limbs", 2026-11-10): HSR0015-Body-087 - a woman of
    # 23 in a sports bra, shorts (black: the fabric test drops them) and sneakers, arms crossed; as HSR0042 for the men
    "hsr0015": {"scan": ROOT / ".dev" / "downloads" / "hsrd100" / "HSR0015-Body-087" / "x" / "HSR0015-Body-087_LOD0.obj",
                "image": ROOT / ".dev" / "downloads" / "hsrd100" / "HSR0015-Body-087" / "x" / "HSR0015-Body-087_LOD0_u0_v0_diffuse.png",
                "scale": 1.0, "tiles": (2, 3), "fit": "anny", "gender": 0.0, "stem": "female",
                # only detail under 6 mm: the fit's leftover (her limbs' wrap p90 14.8 mm) drew broad dark streaks on
                # her thighs at 40 and 5-15 mm diagonal ones at 15 (2026-11-10, `row_h15_full`, `legs_layers.png`,
                # `cuts_shade.png`: one factor - the relief, not the colour)
                "relief_hp_mm": 6.0,
                # her sneakers took 29% of tile 1003's relief as "foot skin" (2026-11-10 05:0x); her hands sit under
                # her crossed arms
                "leave_out": ("feet", "hands"),
                # her own mark: an oval dent ~12 x 30 mm on the front of the right thigh by the groin (a pit at the
                # full view in every woman, 2026-11-10 `legs_lo6.png`; found at this texel of tile 1004, `pit_1004.png`)
                "marks_out": [((985, 845), 22.0, 1004)],
                "work": WORK_ROOT / "hsr0015",
                "source": "HSRD-100, HSR0015-Body-087 (huggingface.co/datasets/digitalrealitylab/HSRD-100)",
                "licence": "CC BY 4.0 (Digital Reality Lab)"},
    "bs_female": {"scan": WORK_ROOT / "bs_female" / "bs_female_top.obj", "scale": 1.0, "tiles": (1,), "fit": "torso",
                  "geometry_only": True, "gender": 0.0, "stem": "female", "work": WORK_ROOT / "bs_female",
                  # only detail under 15 mm: at 40 the sculpt's breast shape against ours left crescents under the
                  # breasts (a shape difference, not skin definition - 2026-11-10)
                  "relief_hp_mm": 15.0, "debris_limit": 0.8,
                  # two marks at the island's side edge, ~2x the nipples' slope - where the sculpt's armpit and hip
                  # don't meet ours (a one-sided line low on a slim woman's abdomen, 2026-11-10): out, as Artec's scar
                  "marks_out": [((1201, 313), 25.0), ((1032, 1822), 25.0)],
                  "source": "Blender Studio, Human Base Meshes bundle v1.4.1 (studio.blender.org), GEO-body_female_realistic",
                  "licence": "CC0-1.0"},
}  # fmt: skip
SIZE = 2048
RELIEF_HP_MM = 40.0  # the relief kept below this scale (the fit's leftover above it)
COLOUR_HP_MM = 60.0  # the colour's detail around 1: its regional tone above this is the character's
EDGE_FADE = 96.0  # texels (~4 cm) to full strength from the scan's and the tile island's edges
FLOOR = 0.006  # m: the scan's points below this (its floor sheet) are left out of the fit
#: the Anny fit: scan points used, steps, the robust distance's scale (m), the pose's pull back to rest
ANNY_SCAN_POINTS, ANNY_STEPS, ANNY_ROBUST, ANNY_POSE_REG = 60000, 400, 0.02, 1e-4
#: the fit's gap (m) up to which a texel takes the scan's detail fully, and past which none (limbs: hands, forearms and
#: feet lie within 3-10 mm after the wrap; upper arms, thighs and shins 9-16 mm, p90 30-56 - 2026-11-06)
FIT_GAP = (0.006, 0.012)
#: a fabric texel (the swim trunks, black): darker than this and greyer than this saturation
FABRIC_VALUE, FABRIC_SATURATION = 0.15, 0.25  # linear; HSR0042: skin S p50 0.71, the trunks under 0.2


def export(src: str = "artec") -> None:
    import importlib

    import bpy

    spec = SOURCES[src]
    work = spec["work"]
    api = importlib.import_module("bl_ext.system.juststage.api")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
    made = api.run("juststage.body.create", name="Body scan", gender=spec.get("gender", 1.0))
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
    forward, up = spec.get("axes", ("Y", "Z"))  # Ten24's OBJ is Y-up, facing +Z
    if spec["scan"].suffix.lower() == ".stl":  # geometry only (the placement turns it)
        bpy.ops.wm.stl_import(filepath=str(spec["scan"]))
    else:
        bpy.ops.wm.obj_import(filepath=str(spec["scan"]), forward_axis=forward, up_axis=up)
    scan = bpy.context.selected_objects[0]
    sm = scan.data
    sv = np.empty(len(sm.vertices) * 3, np.float64)
    sm.vertices.foreach_get("co", sv)
    sv = sv.reshape(-1, 3)
    mw = np.array(scan.matrix_world)  # the importer puts its axis turn in the object, not the mesh (Ten24's Y-up OBJ)
    sv = (sv @ mw[:3, :3].T + mw[:3, 3]) * spec["scale"]
    sv[:, 2] -= sv[:, 2].min()
    sm.calc_loop_triangles()
    sf = np.empty(len(sm.loop_triangles) * 3, np.int64)
    sm.loop_triangles.foreach_get("vertices", sf)
    if spec.get("geometry_only"):  # no UVs, no colour: the bake reads its surface alone
        np.savez(work / "scan.npz", co=sv, faces=sf.reshape(-1, 3), uv=np.zeros((len(sf) // 3, 3, 2), np.float32),
                 image="")  # fmt: skip
        print(f"EXPORT {src}: ours {len(co)} v, {len(tris)} tris, {len(joints)} joints; scan {len(sv)} v, "
              f"{len(sf) // 3} faces, geometry only")
        return
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
    # in chunks: one query over a whole scan built a 150M-pair candidate array (3.3 GB, 2026-11-07)
    dv = np.concatenate([near.on_surface(target_v[i:i + 4000])[1] for i in range(0, len(target_v), 4000)])
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
    if spec["fit"] == "anny":
        return fit_anny(src, o, s)
    if spec["fit"] == "foot":
        return fit_foot(src, o, s)
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


def _foot_vertices(o, side: str = "l") -> np.ndarray:
    """Our vertices of one foot: below its ankle joint plus 1 cm (a fade lands on the ankle), on its side of the body,
    within FOOT_REACH of the ankle (0.16 m until 2026-11-08 cut off the forefoot and toes - the default man's reach
    to 0.211 m)."""
    names = [str(n) for n in o["joint_names"]]
    jc = dict(zip(names, o["joint_co"], strict=True))
    co = o["co"]
    ankle = jc[f"joint-{side}-ankle"]
    return ((co[:, 2] < ankle[2] + 0.01) & (np.sign(co[:, 0]) == np.sign(ankle[0]))
            & (np.linalg.norm(co[:, :2] - ankle[:2], axis=1) < FOOT_REACH))  # fmt: skip


FOOT_REACH = 0.3  # m from the ankle joint: past any foot's toes (the other foot is out by its side)


def fit_foot(src: str, o, s) -> None:
    """A lone leg-and-foot scan onto our left foot (Thunk3D's lies on its side, in no body's frame): its long axis
    (the leg, by PCA) stood up with the foot - the wider end - at the bottom, the foot's reach from the leg turned to
    ours (-Y, the character faces -Y), its sole on our sole and its heel under our ankle; then rigid ICP on our foot,
    then our foot wrapped onto it (`_wrap`, as the limbs). Both feet: the scan (a left foot) on our left, mirrored on
    our right."""
    spec = SOURCES[src]
    work = spec["work"]
    out = {}
    for side in ("l", "r"):  # the scan is a left foot; mirrored (x), it is a right one
        sv = s["co"].astype(np.float64) * (np.array([1.0, 1.0, 1.0]) if side == "l" else np.array([-1.0, 1.0, 1.0]))
        sf = s["faces"] if side == "l" else s["faces"][:, ::-1]
        place, fitted, fv = _place_foot(o, sv, sf, side)
        out[f"place_{side}"], out[f"fitted_{side}"], out[f"moved_{side}"] = place, fitted, fv
    np.savez(work / "fit.npz", place=out["place_l"], fitted=np.concatenate([out["fitted_l"], out["fitted_r"]]),
             moved_v=np.concatenate([out["moved_l"], out["moved_r"]]), place_r=out["place_r"])  # fmt: skip


def _place_foot(o, sv, sf, side: str):
    """One foot: the scan placed on our `side` foot and our foot wrapped onto it - (placement, fitted, our vertices)."""
    import trimesh
    from trimesh import registration

    co, tris = o["co"].astype(np.float64), o["tris"]
    on_foot = _foot_vertices(o, side)
    foot_tris = tris[on_foot[tris].all(axis=1)]
    fv = np.unique(foot_tris)
    ours = co[fv]
    rng = np.random.default_rng(0)
    pts = sv[rng.choice(len(sv), min(200000, len(sv)), replace=False)]
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    axis = vt[0]
    along = (pts - c) @ axis
    lo, hi = along < np.percentile(along, 15), along > np.percentile(along, 85)

    def spread(m):
        q = pts[m] - c
        q = q - np.outer(q @ axis, axis)
        return np.linalg.norm(q - q.mean(0), axis=1).mean()

    if spread(hi) > spread(lo):  # the foot (the wider end) at the bottom
        axis = -axis
        along = -along
        lo, hi = hi, lo
    up = -axis  # the leg runs up from the foot
    bottom = pts[lo]
    reach = (bottom - c) - np.outer((bottom - c) @ up, up)
    fwd_s = reach.mean(0)
    fwd_s = fwd_s - (fwd_s @ up) * up
    fwd_s /= np.linalg.norm(fwd_s)
    side_s = np.cross(fwd_s, up)
    rot_scan = np.stack([side_s, fwd_s, up])  # rows: the scan's (side, forward, up)
    fwd_o, up_o = np.array([0.0, -1.0, 0.0]), np.array([0.0, 0.0, 1.0])
    rot_ours = np.stack([np.cross(fwd_o, up_o), fwd_o, up_o])
    r = rot_ours.T @ rot_scan  # scan frame -> ours
    turned = (sv - c) @ r.T
    # translate: its sole on ours, its foot's middle on ours (x, y of the lowest 3 cm)
    sole_s, sole_o = turned[:, 2].min(), ours[:, 2].min()
    low_s = turned[turned[:, 2] < sole_s + 0.03]
    low_o = ours[ours[:, 2] < sole_o + 0.03]
    t = np.array([np.median(low_o[:, 0]) - np.median(low_s[:, 0]), np.median(low_o[:, 1]) - np.median(low_s[:, 1]),
                  sole_o - sole_s])  # fmt: skip
    place = np.eye(4)
    place[:3, :3] = r
    place[:3, 3] = -r @ c + t
    part = trimesh.Trimesh(co, foot_tris, process=False)
    near = trimesh.proximity.ProximityQuery(part)
    for it in range(3):
        svp = (np.c_[sv, np.ones(len(sv))] @ place.T)[:, :3]
        sample = rng.choice(len(svp), min(120000, len(svp)), replace=False)
        _, dist, _ = near.on_surface(svp[sample])
        crop = svp[sample[dist < (0.03 if it == 0 else 0.015)]]
        m, _moved, cost = registration.icp(crop, ours, threshold=1e-6, max_iterations=40, reflection=False, scale=False)
        place = m @ place
        print(f"FOOT ICP round {it}: {len(crop)} points, mean {cost * 1000:.1f} mm", flush=True)
    svp = (np.c_[sv, np.ones(len(sv))] @ place.T)[:, :3]
    idx = -np.ones(len(co), int)
    idx[fv] = np.arange(len(fv))
    fitted = _wrap(co[fv], idx[foot_tris], svp, sf, f"foot {side}")
    return place, fitted, fv


def fit_anny(src: str, o, s) -> None:
    """Our body onto the scan through Anny (NAVER's differentiable MakeHuman: the same 19,158 vertices in hm08's order
    - its head within 6 mm of ours index for index after a rigid fit, 2026-11-06): its 163 bones' turns, its six body
    sliders and a global placement fitted by gradient descent to a robust two-way nearest-point distance between our
    skin and the scan (the matches renewed every step), then the non-rigid wrap of the arms and legs. (A hand-made
    joint-by-joint pose search before it left the upper arms, thighs and shins 13-16 mm off - pose without shape.)"""
    import os

    os.environ.setdefault("WARP_CACHE_PATH", str(ROOT / ".dev" / "cache" / "warp"))
    import anny
    import roma
    import torch
    from scipy.spatial import cKDTree

    spec = SOURCES[src]
    work = spec["work"]
    co, tris, tile = o["co"].astype(np.float64), o["tris"], o["tile"]
    n_hm08 = 19158
    sv, sf = s["co"].astype(np.float64), s["faces"]
    torso_tris = tris[tile == 1]
    place = _place_rigid(co, torso_tris, sv, sf)  # the scan into our frame (scale to our height, the torso on ours)
    svp = (np.c_[sv, np.ones(len(sv))] @ place.T)[:, :3]
    target = svp[svp[:, 2] > FLOOR]
    rng = np.random.default_rng(0)
    target = target[rng.choice(len(target), min(ANNY_SCAN_POINTS, len(target)), replace=False)]
    skin = np.unique(tris)
    skin = skin[skin < n_hm08]
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = anny.Anny(rig="makehuman", topology="makehuman").to(device=dev, dtype=torch.float32)
    labels = list(model.phenotype_labels)
    rot = torch.zeros(model.bone_count, 3, device=dev, requires_grad=True)
    pheno = torch.zeros(len(labels), device=dev, requires_grad=True)  # logits: 0.5 at the start
    with torch.no_grad():
        # the start's sex the source's (a logit: +4 a man, -4 a woman - the fit frees it after)
        pheno[labels.index("gender")] = 4.0 if SOURCES[src].get("gender", 1.0) >= 0.5 else -4.0
    shift = torch.zeros(3, device=dev, requires_grad=True)
    tgt = torch.tensor(target, dtype=torch.float32, device=dev)
    tgt_tree = cKDTree(target)
    skin_t = torch.tensor(skin, device=dev)
    eye = torch.eye(4, device=dev)

    def body():
        pose = eye.repeat(1, model.bone_count, 1, 1).clone()
        pose[0, :, :3, :3] = roma.rotvec_to_rotmat(rot)
        ph = {k: torch.sigmoid(pheno[i])[None] for i, k in enumerate(labels)}
        v = model(pose_parameters=pose, phenotype_kwargs=ph)["vertices"][0]
        return v, ph

    with torch.no_grad():  # Anny's frame (centred) onto ours: its skin's centre and its feet on the scan's
        v0, _ = body()
        sk = v0[skin_t].cpu().numpy()
        start = np.array([target[:, 0].mean() - sk[:, 0].mean(), target[:, 1].mean() - sk[:, 1].mean(),
                          target[:, 2].min() - sk[:, 2].min()])  # fmt: skip
        shift[:] = torch.tensor(start, dtype=torch.float32, device=dev)
    opt = torch.optim.Adam([{"params": [rot], "lr": 0.01}, {"params": [pheno], "lr": 0.05},
                            {"params": [shift], "lr": 0.003}])  # fmt: skip
    sigma2 = ANNY_ROBUST**2
    for it in range(ANNY_STEPS):
        opt.zero_grad()
        v, _ph = body()
        ours = v[skin_t] + shift
        on = ours.detach().cpu().numpy()
        _, near = tgt_tree.query(on)  # ours -> the scan
        _, back = cKDTree(on).query(target)  # the scan -> ours
        d1 = ((ours - tgt[torch.tensor(near, device=dev)]) ** 2).sum(-1)
        d2 = ((tgt - ours[torch.tensor(back, device=dev)]) ** 2).sum(-1)
        loss = (d1 / (d1 + sigma2)).mean() + (d2 / (d2 + sigma2)).mean() + ANNY_POSE_REG * (rot**2).sum()
        loss.backward()
        opt.step()
        if it % 50 == 0 or it == ANNY_STEPS - 1:
            print(f"ANNY step {it}: loss {loss.item():.4f}, ours->scan p50 {np.sqrt(d1.detach().median().item()) * 1000:.1f} mm",
                  flush=True)  # fmt: skip
    with torch.no_grad():
        v, ph = body()
        fitted_all = (v + shift).cpu().numpy().astype(np.float64)
    print("ANNY body:", {k: round(float(x.item()), 2) for k, x in ph.items()})
    posed = co.copy()
    posed[:n_hm08] = fitted_all  # base v2's appended lid vertices stay where they were (not on these tiles)
    limb_tris = tris[np.isin(tile, spec["tiles"])]
    if spec.get("part") == "hands":  # only the hands are wrapped and baked (Ten24's arms are in a sweater)
        limb_tris = limb_tris[_hand_vertices(o)[limb_tris].all(axis=1)]
    lv = np.unique(limb_tris)
    d, _ = tgt_tree.query(posed[lv])
    print(f"ANNY limbs: to the scan p50 {np.median(d) * 1000:.1f} / p90 {np.percentile(d, 90) * 1000:.1f} mm")
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
    if spec.get("fit_smooth"):  # the wrap's move smoothed: a soft wrap on a small part follows its tendons and
        co = _smooth_move(o["co"], co, moved, tris, spec["fit_smooth"])  # veins, and the bake then reads them flat
    me = bpy.data.meshes.new("ours")
    me.from_pydata(co.tolist(), [], tris.tolist())
    me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), bool))
    ours = bpy.data.objects.new("ours", me)
    scene.collection.objects.link(ours)
    ours.modifiers.new("sub", "SUBSURF").levels = 1
    place = f["place"]
    svp = (np.c_[s["co"], np.ones(len(s["co"]))] @ place.T)[:, :3]
    faces, suv = s["faces"], s["uv"]
    if "place_r" in f.files:  # a lone foot placed on both feet: the right one is the scan mirrored (fit_foot)
        mirrored = s["co"] * np.array([-1.0, 1.0, 1.0])
        svp_r = (np.c_[mirrored, np.ones(len(mirrored))] @ f["place_r"].T)[:, :3]
        faces = np.concatenate([faces, faces[:, ::-1] + len(svp)])
        suv = np.concatenate([suv, suv[:, ::-1]])
        svp = np.concatenate([svp, svp_r])
    sm = bpy.data.meshes.new("scan")
    sm.from_pydata(svp.tolist(), [], faces.tolist())
    sm.polygons.foreach_set("use_smooth", np.ones(len(sm.polygons), bool))
    sm.uv_layers.new(name="UV").data.foreach_set("uv", suv.reshape(-1, 2).astype(np.float32).ravel())
    smat = bpy.data.materials.new("scan colour")
    bsdf = next(n for n in smat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    if not spec.get("geometry_only"):
        tex = smat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(str(s["image"]))
        smat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if "normal" in spec:  # the scan's detail is in its normal map (Ten24's 100k mesh + 8K map): the bake reads it there
        ntex = smat.node_tree.nodes.new("ShaderNodeTexImage")
        ntex.image = bpy.data.images.load(str(spec["normal"]))
        ntex.image.colorspace_settings.name = "Non-Color"
        nmap = smat.node_tree.nodes.new("ShaderNodeNormalMap")
        nmap.space, nmap.uv_map = "TANGENT", "UV"
        smat.node_tree.links.new(ntex.outputs["Color"], nmap.inputs["Color"])
        smat.node_tree.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    sm.materials.append(smat)
    scan = bpy.data.objects.new("scan", sm)
    scene.collection.objects.link(scan)
    # each of our vertices' gap to the scan after the wrap: the post step takes the scan's detail only where it is small
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    scan_tree = BVHTree.FromPolygons(svp.tolist(), faces.tolist())
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
        kinds = (("NORMAL", {"normal_space": "TANGENT"}), ("DIFFUSE", {"pass_filter": {"COLOR"}}))
        for kind, extra in kinds[:1] if spec.get("geometry_only") else kinds:
            img = bpy.data.images.new(kind, SIZE, SIZE, alpha=False, float_buffer=True)
            img.colorspace_settings.name = "Non-Color"
            img.generated_color = (0.5, 0.5, 1.0, 1.0) if kind == "NORMAL" else (0.0, 0.0, 0.0, 1.0)
            node.image = img
            bpy.ops.object.bake(type=kind, use_selected_to_active=True, cage_extrusion=0.01, max_ray_distance=0.03,
                                margin=16, use_clear=False, uv_layer="Tile", **extra)  # fmt: skip
            px = np.array(img.pixels[:], np.float32).reshape(SIZE, SIZE, 4)[::-1, :, :3]
            np.save(work / f"bake_{kind.lower()}_{1001 + number}.npy", px)
            print(f"BAKED {kind} {1001 + number}")
        if spec["fit"] in ("anny", "foot"):  # the fit's gap on this tile (our own surface's attribute, emitted)
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


def _smooth_move(rest: np.ndarray, co: np.ndarray, moved: np.ndarray, tris: np.ndarray, steps: int) -> np.ndarray:
    """`co` with each moved vertex's move (co - rest) averaged with its moved neighbours' `steps` times (Laplacian,
    half a step each): the wrap's broad shape kept, its small-scale following of the scan taken out."""
    on = np.zeros(len(co), bool)
    on[moved] = True
    edges = np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    edges = edges[on[edges].all(axis=1)]
    move = co - rest
    for _ in range(steps):
        total = np.zeros_like(move)
        count = np.zeros(len(co))
        for a, b in ((0, 1), (1, 0)):
            np.add.at(total, edges[:, a], move[edges[:, b]])
            np.add.at(count, edges[:, a], 1.0)
        mean = total / np.maximum(count, 1.0)[:, None]
        move[moved] = np.where(count[moved, None] > 0, 0.5 * move[moved] + 0.5 * mean[moved], move[moved])
    out = co.copy()
    out[moved] = rest[moved] + move[moved]
    return out


def _mm_per_uv(tile_number: int) -> float:
    """maps.MM_PER_UV for the tile, read from the add-on's source (this runs outside Blender)."""
    import re

    src = (ROOT / "extension" / "juststage" / "modules" / "skin" / "maps.py").read_text(encoding="utf-8")
    m = re.search(r"MM_PER_UV\s*=\s*\{([^}]*)\}", src)
    table = dict(re.findall(r"(\d{4}):\s*([0-9.]+)", m.group(1)))
    return float(table[str(tile_number)])


def _hand_vertices(o) -> np.ndarray:
    """Our vertices on the hands: past each wrist joint along the forearm (elbow -> wrist), from 1 cm before the wrist
    so a fade lands on the wrist itself."""
    names = [str(n) for n in o["joint_names"]]
    jc = dict(zip(names, o["joint_co"], strict=True))
    co = o["co"]
    on_hand = np.zeros(len(co), bool)
    for side in ("l", "r"):
        elbow, wrist = jc[f"joint-{side}-elbow"], jc[f"joint-{side}-hand"]
        axis = (wrist - elbow) / np.linalg.norm(wrist - elbow)
        along = (co - wrist) @ axis
        near = np.linalg.norm(co - wrist, axis=1) < 0.25
        on_hand |= near & (along > -0.01)
    return on_hand


def _hand_cover(o, number: int) -> np.ndarray:
    """The texels of tile `number` on our hands (_hand_vertices)."""
    return _cover(o, number, _hand_vertices(o))


def _left_out(o, number: int, parts) -> np.ndarray:
    """The texels of tile `number` on the parts a source leaves out (its `leave_out`: "hands", "feet") - where its
    person shows no bare skin (HSR0015's sneakers; her hands tucked under her crossed arms)."""
    on = np.zeros(len(o["co"]), bool)
    for part in parts:
        if part == "hands":
            on |= _hand_vertices(o)
        elif part == "feet":
            on |= _foot_vertices(o, "l") | _foot_vertices(o, "r")
        else:
            raise ValueError(f"no part {part!r} to leave out")
    return _cover(o, number, on) > 0


def _cover(o, number: int, on_part: np.ndarray) -> np.ndarray:
    """The texels of tile `number` on the faces whose vertices are all in `on_part`."""
    import cv2

    tris, tuv, tile = o["tris"], o["tuv"], o["tile"]
    cover = np.zeros((SIZE, SIZE), np.uint8)
    sel = (tile == number) & on_part[tris].all(axis=1)
    for tri in tuv[sel]:
        pts = np.round(np.c_[(tri[:, 0] - number) * SIZE, (1 - tri[:, 1]) * SIZE]).astype(np.int32)
        cv2.fillConvexPoly(cover, pts, 1)
    return cover


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
        if spec.get("geometry_only"):  # no colour: a flat grey - the colour ratio comes out 1 (the skin's own colour kept)
            col = np.full((SIZE, SIZE, 3), 0.5, np.float32)
        else:
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
        if spec.get("part") == "hands":  # only the hands (Ten24's forearms carry hair and a sweater's cuff)
            baked &= _hand_cover(o, number) > 0
        if spec.get("part") == "feet":  # only the feet the scan was placed on
            baked &= _cover(o, number, _foot_vertices(o, "l") | _foot_vertices(o, "r")) > 0
        if spec.get("leave_out"):  # parts with no bare skin on the scan: no detail there (the edge fade lands before them)
            baked &= ~_left_out(o, number, spec["leave_out"])
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
        cut_mm = _relief_cut(spec, name)
        hp = (xy - mblur(xy, cut_mm * px_per_mm / 2.0)) * w[..., None]
        # faded out well inside the scan's reach and the tile's own island: no step where the detail ends
        # (a part laid over its tile's main relief takes no fade at the island's own edge: across a UV seam the
        # other side carries the same part, and a seam down a foot's top faded its tendons out)
        if spec.get("island_fade", True):
            reach = np.minimum(cv2.distanceTransform(baked.astype(np.uint8), cv2.DIST_L2, 5),
                               cv2.distanceTransform(cover, cv2.DIST_L2, 5))
        else:  # the distance to the island's texels the part leaves out (the ankle's cut), not to its seams
            reach = cv2.distanceTransform(np.where((cover > 0) & ~baked, 0, 1).astype(np.uint8), cv2.DIST_L2, 5)
        edge = np.clip(reach / spec.get("edge_fade", EDGE_FADE), 0, 1)
        edge = edge * edge * (3 - 2 * edge)
        hp *= edge[..., None]
        hp = _debris_filled(hp, spec.get("debris_limit", 0.3))
        marked = _marks(spec, px_per_mm, name)
        if marked is not None:  # filled from the skin round them, relief and colour alike
            hp = _patched(hp, marked, baked, px_per_mm)
        z = np.sqrt(np.clip(1 - (hp**2).sum(-1), 0, 1))
        relief = np.dstack([hp * 0.5 + 0.5, z])
        # colour: hair out, then its detail around 1 (log, over its blur at COLOUR_HP_MM), faded at the edge
        lin = np.maximum(col, 1e-4)
        found = hair.mask(lin, baked)
        lin = np.maximum(hair.fill(lin, found), 1e-4)
        marks = hair.spots(lin, baked, px_per_mm)  # the person's small red spots out (2026-11-07, the torso's gap)
        lin = np.maximum(hair.unred(lin, marks, baked, px_per_mm), 1e-4)  # their redness only: a fill left stains
        if marked is not None:
            lin = np.exp(_patched(np.log(lin), marked, baked, px_per_mm))
        ratio_log = np.log(lin) - np.log(np.maximum(mblur(lin, COLOUR_HP_MM * px_per_mm / 2.0), 1e-4))
        ratio_log = np.clip(ratio_log, -0.5, 0.3) * w[..., None] * edge[..., None]
        ratio = np.exp(ratio_log)
        if spec.get("no_colour"):  # the colour detail left out: the skin's own colour there (a ratio of 1)
            ratio = np.ones_like(ratio)
        OUT.mkdir(parents=True, exist_ok=True)
        stem = f"body_{name}" + (f"_{spec['stem']}" if "stem" in spec else "")  # a sex's own source (women's torso)
        stem += f"_{spec['part']}" if "part" in spec else ""  # a part beside the tile's main source
        cv2.imwrite(str(OUT / f"{stem}_relief.png"),
                    np.round(np.clip(relief[..., ::-1], 0, 1) * 65535).astype(np.uint16))  # fmt: skip
        if "part" in spec:  # its weight (the edge and fit fades): where build_skins takes this part over the main one
            cv2.imwrite(str(OUT / f"{stem}_weight.png"), np.round(np.clip(w * edge, 0, 1) * 65535).astype(np.uint16))
        if "part" in spec and spec.get("geometry_only"):  # no colour of its own: the tile's main colour stays
            (OUT / f"{stem}_colour.png").unlink(missing_ok=True)
        else:
            cv2.imwrite(str(OUT / f"{stem}_colour.png"),
                        np.round(np.clip(ratio[..., ::-1] / 2, 0, 1) * 65535).astype(np.uint16))  # fmt: skip
        info = {"tile": name, "size": SIZE, "source": spec["source"], "licence": spec["licence"],
                "relief_hp_mm": cut_mm, "colour_hp_mm": COLOUR_HP_MM,
                "colour": "none (no_colour)" if spec.get("no_colour") else "a ratio around 1, stored halved (0.5 = 1)",
                "strands_filled": int(found.sum()),
                "fabric_out": int(fabric.sum()), "spots_filled": int(marks.sum()), "covered": float(baked.mean())}  # fmt: skip
        (OUT / f"{stem}.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
        wrote = "relief" if "part" in spec and spec.get("geometry_only") else "relief and colour"
        print(f"POST {name}: {wrote} written; {found.sum()} strand texels, {marks.sum()} spot texels unreddened; {fabric.sum()} fabric "
              f"texels out; tile covered {baked.mean():.1%}")


def _relief_cut(spec: dict, tile: int) -> float:
    """The scale (mm) under which a source's relief is kept on `tile`: its `relief_hp_mm` - one number, or one per
    tile number ({1004: 6.0}: the legs cut finer than the arms) - else RELIEF_HP_MM."""
    cut = spec.get("relief_hp_mm", RELIEF_HP_MM)
    return float(cut.get(tile, RELIEF_HP_MM) if isinstance(cut, dict) else cut)


def _marks(spec: dict, px_per_mm: float, tile: int | None = None) -> np.ndarray | None:
    """The source's own named marks (`marks_out`: texel and radius in mm, and the tile number when the source covers
    more than one - (x, y), mm[, tile]) as a mask on `tile`, None without any there."""
    import cv2

    marks = [m for m in spec.get("marks_out", ()) if len(m) == 2 or tile is None or m[2] == tile]
    if not marks:
        return None
    mask = np.zeros((SIZE, SIZE), np.uint8)
    for (x, y), radius_mm, *_tile in marks:
        cv2.circle(mask, (int(x), int(y)), max(1, int(round(radius_mm * px_per_mm))), 1, -1)
    return mask.astype(bool)


MARK_FINE_MM, MARK_FADE_MM = 12.0, 3.0  # a mark's fill: the skin's texture finer than this from beside it, its level
# from round it, faded in over this (3 mm and 1 mm left a smoother disc with a rim)


def _patched(img: np.ndarray, mask: np.ndarray, valid: np.ndarray, px_per_mm: float) -> np.ndarray:
    """`img` (H x W x C) inside `mask` made from the skin round it: its level a blur of what lies round each mark (the
    mark left out), its texture finer than MARK_FINE_MM copied from the nearest whole patch beside the mark - a Telea
    fill drew a star of flat wedges across a 3 cm mark (2026-11-09) - faded in over MARK_FADE_MM."""
    import cv2

    count, labels = cv2.connectedComponents(mask.astype(np.uint8))
    around = (valid & ~mask).astype(np.float32)
    fine = img - cv2.GaussianBlur(img, (0, 0), MARK_FINE_MM * px_per_mm / 2.0).reshape(img.shape)
    out = img.copy()
    for i in range(1, count):
        one = labels == i
        ys, xs = np.nonzero(one)
        sigma = max(np.ptp(ys), np.ptp(xs)) / 2.0
        level = cv2.GaussianBlur(img * around[..., None], (0, 0), sigma).reshape(img.shape) / np.maximum(
            cv2.GaussianBlur(around, (0, 0), sigma), 1e-6)[..., None]  # fmt: skip
        fade = MARK_FADE_MM * px_per_mm  # the fade runs outward: grown by twice it first, so the mark itself is all 1
        grown = cv2.dilate(one.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(4 * fade) + 1,) * 2))
        soft = np.clip(cv2.GaussianBlur(grown.astype(np.float32), (0, 0), fade), 0.0, 1.0)
        ys, xs = np.nonzero(soft > 1e-3)
        mark_r = sigma  # the mark's own half-width
        reach = int(max(np.ptp(ys), np.ptp(xs)) / 2.0 + mark_r) + 2  # the copied area clear of the mark itself
        copied = np.zeros((len(ys), img.shape[2]), img.dtype)  # no whole patch beside it: no texture (not its own)
        for dy, dx in ((0, reach), (0, -reach), (reach, 0), (-reach, 0), (reach, reach), (-reach, -reach),
                       (reach, -reach), (-reach, reach)):  # fmt: skip
            sy, sx = ys + dy, xs + dx
            if (sy.min() >= 0 and sx.min() >= 0 and sy.max() < len(valid) and sx.max() < valid.shape[1]
                    and valid[sy, sx].all() and not mask[sy, sx].any()):  # fmt: skip
                copied = fine[sy, sx]
                break
        w = soft[ys, xs][:, None]
        out[ys, xs] = img[ys, xs] * (1.0 - w) + (level[ys, xs] + copied) * w
    return out


def _debris_filled(hp: np.ndarray, limit: float) -> np.ndarray:
    """A relief's (tangent XY, high-passed) debris - rings and arcs at the scan's holes and edges, steeper than `limit`
    (a foot's tendons and veins, a nipple, are steeper than a face's folds: `debris_limit` per source) - filled from
    the relief round it. Flattened, as until 2026-11-08, each hole shaded as an oval patch on a sloped chest (the
    torso's "blotch by the sternum") and took the nipples' bumps away."""
    import cv2

    sys.path.insert(0, str(ROOT / "tools" / "face_test"))
    import hair  # noqa: E402

    debris = hair.relief_debris(hp, limit, 8)
    soft = np.clip(cv2.GaussianBlur(debris.astype(np.float32), (0, 0), 2.0) * 1.5, 0.0, 1.0)[..., None]
    return hp * (1.0 - soft) + hair.fill(hp, debris) * soft


HAND_HP_MM = 8.0  # the hands' detail kept from the donor's map: tendons, veins, creases (all narrower)
DONOR_SKIN_VALUE, DONOR_SKIN_MARGIN_MM = 0.3, 3.0  # a donor texel is skin above this sRGB value, this far from fabric


def texture(src: str = "ten24") -> None:
    """A part's relief and colour from its donor's maps in their own texture space - the pore tile's method
    (`tools/gate/relief_tiles.py`), for a donor whose detail lives in a normal map made for another surface (Ten24's
    Level_01 map is relative to its coarse level-1 mesh: baked through its 100k mesh the medium shape counted twice,
    2026-11-07). The map's tilt is high-passed at HAND_HP_MM inside the donor's own islands (its medium shape out);
    each of our hand texels takes the tilt and colour at the nearest point of the donor's surface (after the fit), the
    tilt turned from the donor's tangent frame into ours - no integration to height (Frankot-Chellappa ran across the
    islands' seams and left stripes, 2026-11-07). Writes the same part files as `post`."""
    import subprocess

    import cv2
    import trimesh
    from scipy.spatial import cKDTree

    sys.path.insert(0, str(ROOT / "tools" / "gate"))

    spec = SOURCES[src]
    work = spec["work"]
    o, s, f = np.load(work / "ours.npz"), np.load(work / "scan.npz", allow_pickle=True), np.load(work / "fit.npz")
    co = o["co"].astype(np.float64)
    co[f["moved_v"]] = f["fitted"]  # our hands on the donor's surface
    place = f["place"]
    sv = (np.c_[s["co"], np.ones(len(s["co"]))] @ place.T)[:, :3]
    sf, suv = s["faces"], s["uv"]  # uv per triangle corner
    # the donor's hand triangles and their box in its 8K maps
    d, _ = cKDTree(co[_hand_vertices(o)]).query(sv[sf].mean(1))
    keep = d < 0.015
    tri_uv = suv[keep]
    big = 8192
    # the box inside the map (a square past its edge came back shifted by ffmpeg - the normals read ~900 texels off
    # the colour and the UVs: the stripes of 2026-11-07)
    x0, x1 = max(int(tri_uv[..., 0].min() * big) - 8, 0), min(int(tri_uv[..., 0].max() * big) + 8, big)
    y0, y1 = max(int((1 - tri_uv[..., 1].max()) * big) - 8, 0), min(int((1 - tri_uv[..., 1].min()) * big) + 8, big)
    cw, ch = x1 - x0, y1 - y0
    tv = sv[sf[keep]]
    area3d = np.linalg.norm(np.cross(tv[:, 1] - tv[:, 0], tv[:, 2] - tv[:, 0]), axis=1).sum() / 2 * 1e6  # mm2
    tuvp = tri_uv * big
    e1, e2 = tuvp[:, 1] - tuvp[:, 0], tuvp[:, 2] - tuvp[:, 0]
    area_uv = np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]).sum() / 2  # NumPy 2 has no 2D cross
    donor_px_per_mm = float(np.sqrt(area_uv / area3d))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(spec["normal"]), "-vf", f"crop={cw}:{ch}:{x0}:{y0}",
                          "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"], check=True, capture_output=True).stdout
    normals = np.frombuffer(raw, np.uint16).reshape(ch, cw, 3).astype(np.float32) / 65535.0
    sigma = HAND_HP_MM * donor_px_per_mm / 2.0
    island = np.zeros((ch, cw), np.uint8)  # the donor's hand triangles in the crop: blur stays inside them
    for tri in tuvp:
        cv2.fillConvexPoly(island, np.round(np.c_[tri[:, 0] - x0, big - tri[:, 1] - y0]).astype(np.int32), 1)
    inside = island.astype(np.float32)
    dxy = normals[..., :2].astype(np.float32) * 2 - 1
    # hair out: the backs of Ten24's hands are hairy and its normal map carries the strands as parallel stripes
    # (2026-11-07) - the strands found in its colour (dark on light skin; tools/face_test/hair.py, the scan colour's
    # way) and the tilt filled under them; tendons and veins are 13-22 of its texels wide and stay
    sys.path.insert(0, str(ROOT / "tools" / "face_test"))
    import hair  # noqa: E402

    rgb = cv2.imread(str(spec["image"]), cv2.IMREAD_COLOR)[y0:y1, x0:x1, ::-1].astype(np.float32) / 255
    strands = hair.mask(rgb, island > 0)
    dxy = hair.fill(np.dstack([dxy * 0.5 + 0.5, np.zeros(dxy.shape[:2], np.float32)]), strands)[..., :2] * 2 - 1
    print(f"TEXTURE donor hair: {strands.sum()} strand texels filled ({strands[island > 0].mean():.1%} of the hands)")
    num = cv2.GaussianBlur(dxy * inside[..., None], (0, 0), sigma)
    den = cv2.GaussianBlur(inside, (0, 0), sigma)[..., None]
    dxy = (dxy - num / np.maximum(den, 1e-6)) * inside[..., None]  # the tilt under HAND_HP_MM, its medium shape out
    # anti-aliased to our texels before resampling: the palms' fine ridges (~0.5 mm) folded into stripes at our
    # coarser 2.7 px / mm (2026-11-07)
    ours_px_per_mm = SIZE / _mm_per_uv(1001 + spec["tiles"][0])
    if donor_px_per_mm > ours_px_per_mm:
        dxy = cv2.GaussianBlur(dxy, (0, 0), 0.6 * donor_px_per_mm / ours_px_per_mm)
    colour = rgb
    lin = np.where(colour <= 0.04045, colour / 12.92, ((colour + 0.055) / 1.055) ** 2.4).astype(np.float32)
    # the donor's skin only: Ten24's black knit sweater meets the wrists (its ribbing came through as stripes,
    # 2026-11-07) - skin is light (sRGB value > DONOR_SKIN_VALUE), kept DONOR_SKIN_MARGIN_MM in from the fabric
    value = colour.max(-1)
    skin_ok = cv2.erode((value > DONOR_SKIN_VALUE).astype(np.uint8),
                        np.ones((2 * int(DONOR_SKIN_MARGIN_MM * donor_px_per_mm) + 1,) * 2, np.uint8)).astype(np.float32)
    blur = cv2.GaussianBlur(lin, (0, 0), COLOUR_HP_MM * donor_px_per_mm / 2.0)
    log_ratio = np.log(np.maximum(lin, 1e-4)) - np.log(np.maximum(blur, 1e-4))
    print(f"TEXTURE donor: {keep.sum()} hand triangles, map box {x0},{y0} {cw} x {ch}, {donor_px_per_mm:.2f} px/mm")
    # our hand texels on the tile: each texel's 3D point and its triangle's scale (mm per texel)
    number = spec["tiles"][0]
    tris, tuv, tile = o["tris"], o["tuv"], o["tile"]
    on_hand = _hand_vertices(o)
    sel = np.flatnonzero((tile == number) & on_hand[tris].all(axis=1))
    tri_id = np.full((SIZE, SIZE), -1, np.int64)
    pos = np.zeros((SIZE, SIZE, 3), np.float64)
    mm_tex = np.zeros((SIZE, SIZE), np.float32)
    have = np.zeros((SIZE, SIZE), bool)
    for t in sel:
        xs, ys = (tuv[t][:, 0] - number) * SIZE, (1 - tuv[t][:, 1]) * SIZE
        bx0, bx1 = int(np.floor(xs.min())), int(np.ceil(xs.max()))
        by0, by1 = int(np.floor(ys.min())), int(np.ceil(ys.max()))
        gx, gy = np.meshgrid(np.arange(bx0, bx1 + 1) + 0.5, np.arange(by0, by1 + 1) + 0.5)
        m = np.array([[xs[1] - xs[0], xs[2] - xs[0]], [ys[1] - ys[0], ys[2] - ys[0]]])
        if abs(np.linalg.det(m)) < 1e-9:
            continue
        b = np.einsum("ij,jkl->ikl", np.linalg.inv(m), np.stack([gx - xs[0], gy - ys[0]]))
        w = np.stack([1 - b[0] - b[1], b[0], b[1]])
        inside = (w >= -1e-4).all(0)
        if not inside.any():
            continue
        p3 = np.einsum("kij,kc->ijc", w, co[tris[t]])
        e3 = np.linalg.norm(np.cross(co[tris[t][1]] - co[tris[t][0]], co[tris[t][2]] - co[tris[t][0]])) / 2 * 1e6
        e2 = abs(np.linalg.det(m)) / 2
        iy, ix = (gy[inside] - 0.5).astype(int), (gx[inside] - 0.5).astype(int)
        ok = (iy >= 0) & (iy < SIZE) & (ix >= 0) & (ix < SIZE)
        pos[iy[ok], ix[ok]] = p3[inside][ok]
        mm_tex[iy[ok], ix[ok]] = np.sqrt(e3 / max(e2, 1e-9))
        tri_id[iy[ok], ix[ok]] = t
        have[iy[ok], ix[ok]] = True
    pts = pos[have]
    donor = trimesh.Trimesh(sv, sf[keep], process=False)
    near = trimesh.proximity.ProximityQuery(donor)
    closest, dist, tid = [], [], []
    for i in range(0, len(pts), 20000):
        c, dd, t = near.on_surface(pts[i:i + 20000])
        closest.append(c)
        dist.append(dd)
        tid.append(t)
    closest, dist, tid = np.concatenate(closest), np.concatenate(dist), np.concatenate(tid)
    bary = trimesh.triangles.points_to_barycentric(donor.triangles[tid], closest)
    duv = np.einsum("ij,ijk->ik", bary, tri_uv[tid])
    mapx = (duv[:, 0] * big - x0).astype(np.float32).reshape(-1, 1)
    mapy = ((1 - duv[:, 1]) * big - y0).astype(np.float32).reshape(-1, 1)

    def sample(img):  # remap takes at most 32767 rows: the points laid out as a 2D grid
        n, cols = len(mapx), 1024
        rows = -(-n // cols)
        gx = np.zeros(rows * cols, np.float32)
        gy = np.zeros(rows * cols, np.float32)
        gx[:n], gy[:n] = mapx[:, 0], mapy[:, 0]
        out = cv2.remap(img.astype(np.float32), gx.reshape(rows, cols), gy.reshape(rows, cols), cv2.INTER_LINEAR)
        return out.reshape(rows * cols, -1)[:n]

    def frames(p3, uv):
        """Each triangle's tangent (along u) and bitangent (along v), unit, in 3D (the standard tangent basis)."""
        e1, e2 = p3[:, 1] - p3[:, 0], p3[:, 2] - p3[:, 0]
        d1, d2 = uv[:, 1] - uv[:, 0], uv[:, 2] - uv[:, 0]
        r = 1.0 / np.where(np.abs(d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]) < 1e-12, 1e-12,
                           d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1])[:, None]  # fmt: skip
        t = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) * r
        b = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) * r
        n = np.cross(e1, e2)
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        t -= n * (t * n).sum(1, keepdims=True)
        t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-12)
        b -= n * (b * n).sum(1, keepdims=True) + t * (b * t).sum(1, keepdims=True)
        b /= np.maximum(np.linalg.norm(b, axis=1, keepdims=True), 1e-12)
        return t, b

    dt, db = frames(sv[sf[keep]], tri_uv)  # the donor's frames (its map's green is +v, as the pore tile reads it)
    ot, ob = frames(co[tris], tuv)  # ours
    tilt = sample(dxy)  # the donor's tilt at each of our texels, in its frame
    p3 = tilt[:, :1] * dt[tid] + tilt[:, 1:2] * db[tid]  # in 3D
    mine = tri_id[have]
    xy_have = np.c_[(p3 * ot[mine]).sum(1), (p3 * ob[mine]).sum(1)]  # in our frame
    ratio_log = np.zeros((SIZE, SIZE, 3), np.float32)
    ratio_log[have] = sample(log_ratio)
    gap = np.full((SIZE, SIZE), 1.0, np.float32)
    gap[have] = dist
    on_skin = np.zeros((SIZE, SIZE), np.float32)
    on_skin[have] = sample(skin_ok)[:, 0]
    print(f"TEXTURE ours: {have.sum()} hand texels, gap p50 {np.median(dist) * 1000:.1f} / p90 "
          f"{np.percentile(dist, 90) * 1000:.1f} mm")
    xy = np.zeros((SIZE, SIZE, 2), np.float32)
    xy[have] = xy_have
    close = 1.0 - np.clip((gap - FIT_GAP[0]) / (FIT_GAP[1] - FIT_GAP[0]), 0.0, 1.0)
    w = have.astype(np.float32) * close * close * (3 - 2 * close) * on_skin
    edge = np.clip(cv2.distanceTransform((have & (on_skin > 0.5)).astype(np.uint8), cv2.DIST_L2, 5)
                   / spec.get("edge_fade", EDGE_FADE), 0, 1)  # fmt: skip
    w *= edge * edge * (3 - 2 * edge)
    xy *= w[..., None] * spec.get("strength", 1.0)
    z = np.sqrt(np.clip(1 - (xy**2).sum(-1), 0, 1))
    relief = np.dstack([xy * 0.5 + 0.5, z])
    ratio = np.exp(np.clip(ratio_log, -0.5, 0.3) * w[..., None])
    name = 1001 + number
    stem = f"body_{name}_{spec['part']}"
    OUT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / f"{stem}_relief.png"), np.round(np.clip(relief[..., ::-1], 0, 1) * 65535).astype(np.uint16))
    cv2.imwrite(str(OUT / f"{stem}_weight.png"), np.round(np.clip(w, 0, 1) * 65535).astype(np.uint16))
    cv2.imwrite(str(OUT / f"{stem}_colour.png"),
                np.round(np.clip(ratio[..., ::-1] / 2, 0, 1) * 65535).astype(np.uint16))  # fmt: skip
    info = {"tile": name, "size": SIZE, "source": spec["source"], "licence": spec["licence"], "method": "texture space",
            "hand_hp_mm": HAND_HP_MM, "donor_px_per_mm": round(donor_px_per_mm, 2),
            "gap_mm_p50_p90": [round(float(np.median(dist)) * 1000, 1), round(float(np.percentile(dist, 90)) * 1000, 1)]}
    (OUT / f"{stem}.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    slope = np.linalg.norm(xy[have], axis=-1)
    print(f"TEXTURE {stem}: written; slope p50 {np.median(slope):.3f} / p99 {np.percentile(slope, 99):.3f}")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    stages = {"export": export, "fit": fit, "bake": bake, "post": post, "texture": texture}
    stages[argv[0]](*(argv[1:2] or ["artec"]))
