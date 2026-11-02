# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material: a scanned head's skin carried onto our head's texture layout (HeadTile) -
Headshot's structure (the face from the character's painting, the rest from a skin base; `docs/plans/2026-11-02-
research-texture-source.md`). The scan lined up (by its eye meshes when it has them, else by the skull's breadth and
the crown, both facings tried), refined by ICP with scale, our head wrapped onto its surface (trimesh's Amberg NICP,
as libs/wrap/gnm_to_hm08.py does), then each texel of ours takes the colour of the scan's surface under it; how far
each texel sat from the scan is kept (where the wrap didn't reach - the chest, the ears' folds - the base isn't used).

The scans (CC BY - credit them wherever their skin is used):
- "Head scan 02 (Optimized PBR)" by Cratera Games, scan by yaro.pro -
  sketchfab.com/3d-models/2f1978b43032415c8fdf911c7acfb1a4
- "Infinite, 3D Head Scan" by Lee Perry-Smith, CC BY 3.0, based on a work at www.triplegangers.com (Sketchfab upload
  "Head (Lee Perry Smith)" by Paul) - sketchfab.com/3d-models/4d07eb2030db4406bc7eee971d1d3a97
- "Marcus - Free 3D Head Sample Model Scan" by Digital Reality Lab -
  sketchfab.com/3d-models/1aef740047ba4214998f068355a5f034

Needs `scans/head_export.npz` (the round scene's head, HeadTile UVs and eyes; written by test_face_export_head.py
from round.blend). Run (the tool environment with trimesh): .dev/venv-tools/Scripts/python -I
tools/face_test/scan_base.py NAME   (scan02, lps, marcus)"""

import importlib.util
import sys
import time

import cv2
import numpy as np
import trimesh
from trimesh import registration

T = "E:/Dev/3D/just-stage/.dev/facetest/scans/"
S = "E:/Dev/3D/just-stage/.dev/downloads/scans/"
SIZE = 4096
spec = importlib.util.spec_from_file_location("up", "E:/Dev/3D/just-stage/extension/juststage/core/uv_projection.py")
up = importlib.util.module_from_spec(spec)
spec.loader.exec_module(up)
R_YUP = np.array([[1.0, 0, 0], [0, 0, -1.0], [0, 1.0, 0]])  # Y-up, face +Z -> ours Z-up, face -Y
R_TURN = np.diag([-1.0, -1.0, 1.0])  # the other facing (a half turn about the vertical)


def load_scan(name):
    """(skin mesh in its own frame, eye centres in that frame or None, texture path, whether V counts up the image)
    - trimesh hands glTF UVs over already in image-row order (flipped, 22% of scan02's vertices landed on the
    texture's black; unflipped 0.7%) and OBJ UVs with v up"""
    if name == "scan02":
        sc = trimesh.load(S + "head_scan_02/x/source/scene_optimized.gltf", force="scene")

        def node(n):
            tf, g = sc.graph[n]
            m = sc.geometry[g].copy()
            m.apply_transform(tf)
            return m

        eyes = np.array([node(n).bounds.mean(0) for n in ("head_02_eye_L", "head_02_eye_R")])
        return node("head_02_skin"), eyes, S + "head_scan_02/x/textures/head_scan_02_photogammetry_diffuse_3.png", False
    if name == "lps":
        return (
            trimesh.load(S + "lee_perry_smith/x/src7z/head.obj", force="mesh", process=False),
            None,
            S + "lee_perry_smith/x/src7z/lambertian.jpg",
            True,
        )
    if name == "marcus":
        return (
            trimesh.load(S + "marcus/x/src/Marcus_01_250k.obj", force="mesh", process=False),
            None,
            S + "marcus/x/textures/Marcus_01_250k.png",
            True,
        )
    raise SystemExit(f"unknown scan {name}")


def breadth(v, up_axis_values, top, depth):
    """The head's widest left-right span in the band between `depth` below the crown and the crown."""
    band = v[(up_axis_values > top - depth) & (up_axis_values < top - 0.25 * depth)]
    return float(np.ptp(band[:, 0]))


def main(name):
    t0 = time.time()
    E = np.load(T + "head_export.npz")  # the round scene's head (see the docstring)
    co, tris, tri_uv = E["co"].astype(np.float64), E["tris"], E["tri_uv"]
    used = np.unique(tris)
    remap = -np.ones(len(co), dtype=np.int64)
    remap[used] = np.arange(len(used))
    ours = trimesh.Trimesh(co[used], remap[tris], process=False)
    eyes_o = np.array([E["eye_left"], E["eye_right"]], dtype=np.float64)
    top_o = ours.vertices[:, 2].max()
    upper_o = ours.vertices[ours.vertices[:, 2] > 1.45]

    skin, eyes_s, tex_path, v_up = load_scan(name)
    candidates = []
    for turn in (np.eye(3),) if eyes_s is not None else (np.eye(3), R_TURN):
        Rm = turn @ R_YUP
        v = skin.vertices @ Rm.T
        if eyes_s is not None:
            e = eyes_s @ Rm.T
            scale = np.linalg.norm(eyes_o[0] - eyes_o[1]) / np.linalg.norm(e[0] - e[1])
            offset = eyes_o.mean(0) - scale * e.mean(0)
        else:  # the skull above the ears: its breadth and the crown
            h_o = top_o - eyes_o[:, 2].mean()  # crown to eyes, ~0.116 m
            vt = v[:, 2].max()
            span = np.ptp(v[:, 2])
            scale = breadth(upper_o, upper_o[:, 2], top_o, h_o) / breadth(
                v, v[:, 2], vt, h_o / (top_o - 1.45) * span * 0.25
            )
            v_s = v * scale
            offset = np.array(
                [
                    eyes_o[:, 0].mean() - np.median(v_s[:, 0]),
                    upper_o[:, 1].mean() - v_s[v_s[:, 2] > v_s[:, 2].max() - 0.25, 1].mean(),
                    top_o - v_s[:, 2].max(),
                ]
            )
        v = v * scale + offset
        head_s = v[v[:, 2] > 1.45]
        if len(head_s) > 20000:  # ICP on a subsample: all of Marcus' 250k points ran 30+ min without one result
            head_s = head_s[np.random.default_rng(0).choice(len(head_s), 20000, replace=False)]
        m, _moved, cost = registration.icp(
            head_s, ours, max_iterations=50, threshold=1e-7, scale=True, reflection=False
        )
        candidates.append((cost, trimesh.transform_points(v, m), scale))
        print(f"{name}: facing {len(candidates)}: ICP cost {cost * 1e6:.1f} mm^2 (scale {scale:.4f})")
    cost, scan_v, _ = min(candidates, key=lambda c: c[0])
    scan = trimesh.Trimesh(scan_v, skin.faces, process=False)
    d0 = trimesh.proximity.closest_point(scan, ours.vertices[ours.vertices[:, 2] > 1.45])[1] * 1000
    print(
        f"{name}: after the rigid fit: median {np.median(d0):.1f} mm, 90% {np.percentile(d0, 90):.1f} mm "
        f"({time.time() - t0:.0f}s)"
    )

    fitted = registration.nricp_amberg(ours, scan, distance_threshold=0.02, use_faces=True)
    closest, dist, tri = trimesh.proximity.closest_point(scan, fitted)
    print(
        f"{name}: after the wrap: median {np.median(dist) * 1000:.2f} mm, 90% {np.percentile(dist, 90) * 1000:.2f} mm "
        f"({time.time() - t0:.0f}s)"
    )
    np.save(T + f"fitted_on_{name}.npy", fitted)

    bary = trimesh.triangles.points_to_barycentric(scan.triangles[tri], closest)
    suv = np.asarray(skin.visual.uv)
    corner_uv = (suv[skin.faces[tri]] * bary[:, :, None]).sum(1)[remap[tris]]
    seam = np.ptp(corner_uv, axis=1).max(axis=1) > 0.03
    (uv_map, pos_map), mask = up.raster_uv(
        tri_uv, [corner_uv.astype(np.float32), fitted[remap[tris]].astype(np.float32)], SIZE
    )
    (_s,), seam_mask = up.raster_uv(tri_uv[seam], [np.ones((seam.sum(), 3, 1), np.float32)], SIZE)
    redo = seam_mask & mask
    c2, d2, t2 = trimesh.proximity.closest_point(scan, pos_map[redo].astype(np.float64))
    b2 = trimesh.triangles.points_to_barycentric(scan.triangles[t2], c2)
    uv_map[redo] = (suv[skin.faces[t2]] * b2[:, :, None]).sum(1)
    # how far each texel's point sat from the scan: far means the wrap didn't reach (ears' folds, the mouth's inside)
    gap = np.zeros((SIZE, SIZE), np.float32)
    (gap_map,), _ = up.raster_uv(tri_uv, [dist[remap[tris]][..., None].astype(np.float32)], SIZE)
    gap[mask] = gap_map[mask][:, 0]
    gap[redo] = d2
    print(f"{name}: {seam.sum()} seam triangles, {redo.sum()} texels looked up one by one ({time.time() - t0:.0f}s)")

    tex = cv2.imread(tex_path)[..., :3]
    h, w = tex.shape[:2]
    mx = (uv_map[..., 0] * w - 0.5).astype(np.float32)
    my = (((1.0 - uv_map[..., 1]) if v_up else uv_map[..., 1]) * h - 0.5).astype(np.float32)
    base = cv2.remap(tex, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    base[~mask] = 0
    cv2.imwrite(T + f"base_{name}.png", base)
    np.save(T + f"base_{name}_gap.npy", gap.astype(np.float16))
    cv2.imwrite(T + "base_mask.png", (mask * 255).astype(np.uint8))
    cv2.imwrite(T + f"base_{name}_small.png", cv2.resize(base, (1024, 1024), interpolation=cv2.INTER_AREA))
    print(f"{name}: base map written ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main(sys.argv[1])
