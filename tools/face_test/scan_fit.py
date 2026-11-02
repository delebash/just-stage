# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material, step 5: our head wrapped onto a scan - Wrap's order (point pairs → rigid →
a non-rigid wrap guided by the pairs; `docs/plans/2026-10-30-research-ai-photo-to-head.md` §4). The scan placed on
our head by the pairs (scan_pairs.py) - trimesh's weighted `procrustes` with scale, the worst pairs (beyond 3x the
median residual) dropped and fitted again - then cropped to our head's reach, and our head wrapped onto it with our
standard non-rigid fit (trimesh's Amberg NICP, as libs/wrap/gnm_to_hm08.py) held by the same pairs. Amberg's default
steps let the pairs go in the last step (weight 0); here they keep weight 1 there, so the eyes and lips stay on their
pairs while the surface settles.

Writes scans/NAME/fit.npz: the scan's placement (4x4), our fitted head vertices (head_export.npz's used ones), and
how far each sits from the scan. Run (the tool environment): .dev/venv-tools/Scripts/python -I
tools/face_test/scan_fit.py NAME
"""

import sys
import time
from pathlib import Path

import numpy as np
import trimesh
from trimesh import registration

SCANS = Path("E:/Dev/3D/just-stage/.dev/facetest/scans")
REACH = 0.03  # m: the scan kept within this of our head's bounds (a full body's rest goes)
STEPS = [[0.01, 10, 0.5, 10], [0.02, 5, 0.5, 10], [0.03, 2.5, 0.5, 10], [0.01, 1, 0.0, 10]]  # Amberg's, see above
THRESHOLD = 0.01  # m: farther than this a point finds no match (keeps our scalp off a scan's hair)


def our_head():
    E = np.load(SCANS / "head_export.npz")
    co, tris = E["co"].astype(np.float64), E["tris"]
    used = np.unique(tris)
    remap = -np.ones(len(co), dtype=np.int64)
    remap[used] = np.arange(len(used))
    return trimesh.Trimesh(co[used], remap[tris], process=False), used


def main(name):
    t0 = time.time()
    out = SCANS / name
    P = np.load(out / "pairs.npz")
    a, b, w = P["scan_xyz"].astype(np.float64), P["ours_xyz"].astype(np.float64), P["weight"].astype(np.float64)
    keep = np.ones(len(a), bool)
    for _ in range(3):
        M, _, _ = registration.procrustes(a[keep], b[keep], weights=w[keep], reflection=False, scale=True)
        res = np.linalg.norm(trimesh.transform_points(a, M) - b, axis=1)
        keep = res < 3 * np.median(res[keep])
    scale = np.cbrt(np.linalg.det(M[:3, :3]))
    print(f"{name}: placed by {keep.sum()} of {len(a)} pairs - scale {scale:.4f}, residual median "
          f"{np.median(res[keep]) * 1000:.2f} mm, 90% {np.percentile(res[keep], 90) * 1000:.2f} mm")

    ours, used = our_head()
    src = np.load(out / "src.npz")
    scan_v = trimesh.transform_points(src["co"].astype(np.float64), M)
    lo, hi = ours.bounds[0] - REACH, ours.bounds[1] + REACH
    inside = ((scan_v >= lo) & (scan_v <= hi)).all(1)
    faces = src["tris"][inside[src["tris"]].all(1)]
    scan = trimesh.Trimesh(scan_v, faces, process=False)
    scan.remove_unreferenced_vertices()
    d0 = trimesh.proximity.closest_point(scan, ours.vertices)[1]
    print(f"{name}: scan cropped to {len(scan.faces)} of {len(src['tris'])} triangles; our head to it after placing: "
          f"median {np.median(d0) * 1000:.2f} mm, 90% {np.percentile(d0, 90) * 1000:.2f} mm ({time.time() - t0:.0f}s)")

    # the pairs on our side as points of our surface (triangle + barycentric), the scan's side placed
    pts, gap, tri = trimesh.proximity.closest_point(ours, b[keep])
    bary = trimesh.triangles.points_to_barycentric(ours.triangles[tri], pts)
    print(f"{name}: our pair points off our surface: median {np.median(gap) * 1000:.2f} mm, max {gap.max() * 1000:.2f} mm")
    target = trimesh.transform_points(a[keep], M)
    fitted = registration.nricp_amberg(ours, scan, source_landmarks=(tri, bary), target_positions=target,
                                       steps=STEPS, distance_threshold=THRESHOLD, use_faces=True)
    _, dist, _ = trimesh.proximity.closest_point(scan, fitted)
    land = (fitted[ours.faces[tri]] * bary[:, :, None]).sum(1)
    land_err = np.linalg.norm(land - target, axis=1)
    np.savez(out / "fit.npz", placement=M, fitted=fitted, used=used, dist=dist, scale=scale)
    head = ours.vertices[:, 2] > 1.45  # above our neck - where a bust's scan reaches (the old fit's measure)
    print(f"{name}: after the wrap: our head to the scan median {np.median(dist) * 1000:.2f} mm, 90% "
          f"{np.percentile(dist, 90) * 1000:.2f} mm; above the neck median {np.median(dist[head]) * 1000:.2f} mm, 90% "
          f"{np.percentile(dist[head], 90) * 1000:.2f} mm, beyond 1 cm {np.mean(dist[head] > 0.01):.1%}; pairs median "
          f"{np.median(land_err) * 1000:.2f} mm, 90% {np.percentile(land_err, 90) * 1000:.2f} mm ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main(sys.argv[1])
