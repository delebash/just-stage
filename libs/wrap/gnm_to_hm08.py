# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: MIT

"""Wrap Google's GNM head shape space onto MakeHuman's hm08 (docs/standards/character-data-model.md §1.2).

    .dev/venv-tools/Scripts/python libs/wrap/gnm_to_hm08.py

Offline, once per GNM or base version. GNM (Apache-2.0) is read as plain arrays from its model file — no GNM code
runs. Steps:

1. Line GNM's template up with hm08's raw base by the eyes (both are Y-up and face +Z; GNM is in metres, hm08 in
   decimetres).
2. Fit GNM's skin onto hm08's head non-rigidly — trimesh's Amberg optimal-step NICP (MIT), the standard method.
3. Find, for each hm08 head vertex, the point on the fitted GNM skin under it (triangle and barycentric weights).
4. Carry each of GNM's 170 head identity directions (one standard deviation each) across through those points,
   faded out down the neck, and write it as a MakeHuman target (`gnm/head_NNN.target.gz`, decimetres, Y-up), the
   format the rest of JustStage reads.

The fit's error (mm) is written to the report — a quality-gate input (R3).
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import trimesh
from trimesh import registration

ROOT = Path(__file__).resolve().parents[2]
MAKEHUMAN = ROOT / "extension" / "juststage" / "data" / "fetched" / "makehuman"
GNM_FILE = ROOT / ".dev" / "cache" / "gnm" / "v3_0" / "gnm_head.npz"
GNM_SHA256 = "61d78bbfb4ad8e0b38495804a4caef3214d3df00f8c3f68761e63b41ce3747eb"  # v3_0/checksums.sha256
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "gnm"

HM08_DM_PER_M = 10.0
BODY_VERTICES = 13380
# the head region, in hm08 metres (Y up): the fade runs from mid-neck (0) to the jaw line (1)
NECK_LOW, NECK_HIGH = 0.55, 0.62
# where hm08 reaches past GNM's skin (the crown, the shoulder tops) it keeps its own shape: full transfer within
# NEAR of the fitted GNM surface, none beyond FAR
NEAR, FAR = 0.005, 0.020


def load_hm08() -> tuple[np.ndarray, np.ndarray, dict[str, list[int]]]:
    obj = (MAKEHUMAN / "3dobjs" / "base.obj").read_text(encoding="utf-8").splitlines()
    vertices = np.array([[float(x) for x in line.split()[1:4]] for line in obj if line.startswith("v ")])
    faces = [[int(c.split("/")[0]) - 1 for c in line.split()[1:]] for line in obj if line.startswith("f ")]
    groups = json.loads((MAKEHUMAN / "mesh_metadata" / "basemesh_vertex_groups.json").read_text(encoding="utf-8"))
    groups = {k: [i for a, b in spans for i in range(a, b + 1)] for k, spans in groups.items()}
    return vertices / HM08_DM_PER_M, np.array(faces), groups


def load_gnm() -> dict[str, np.ndarray]:
    data = GNM_FILE.read_bytes()
    if hashlib.sha256(data).hexdigest() != GNM_SHA256:
        sys.exit(f"{GNM_FILE} does not match GNM v3.0's published SHA-256")
    with np.load(GNM_FILE, allow_pickle=False) as npz:
        return {k: npz[k] for k in npz.files}


def triangles_of(quads: np.ndarray) -> np.ndarray:
    return np.concatenate([quads[:, [0, 1, 2]], quads[:, [0, 2, 3]]])


def head_region(vertices: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, trimesh.Trimesh]:
    """hm08's body vertices above mid-neck, and the body surface they lie on."""
    body_faces = faces[(faces < BODY_VERTICES).all(axis=1)]
    head = np.where((np.arange(len(vertices)) < BODY_VERTICES) & (vertices[:, 1] > NECK_LOW))[0]
    keep = np.isin(body_faces, head).all(axis=1)
    surface = trimesh.Trimesh(vertices, triangles_of(body_faces[keep]), process=False)
    return head, surface


def smoothstep(x: np.ndarray, low: float, high: float) -> np.ndarray:
    t = np.clip((x - low) / (high - low), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def fade(y: np.ndarray, distance: np.ndarray) -> np.ndarray:
    """How much of GNM's shape a vertex takes: up the neck, and only where GNM's skin is under it."""
    return smoothstep(y, NECK_LOW, NECK_HIGH) * (1.0 - smoothstep(distance, NEAR, FAR))


def main() -> int:
    t0 = time.time()
    hm_v, hm_f, hm_groups = load_hm08()
    gnm = load_gnm()

    # 1 · by the eyes: GNM's eye joints onto hm08's eye joint cubes (the CUBE strategy: a cube's mean)
    hm_eyes = np.array([hm_v[hm_groups[g]].mean(0) for g in ("joint-l-eye", "joint-r-eye")])
    names = gnm["joint_names"].tolist()
    gnm_eyes = gnm["template_joint_positions"][[names.index("left_eye"), names.index("right_eye")]]
    scale = np.linalg.norm(hm_eyes[0] - hm_eyes[1]) / np.linalg.norm(gnm_eyes[0] - gnm_eyes[1])
    offset = hm_eyes.mean(0) - scale * gnm_eyes.mean(0)
    template = gnm["template_vertex_positions"] * scale + offset

    # GNM's outer skin only (its eyes, teeth, tongue and mouth interior are parts of their own)
    group_names = gnm["vertex_group_names"].tolist()
    exterior = gnm["vertex_groups"][group_names.index("skin_exterior")] > 0.5
    skin_quads = gnm["quads"][exterior[gnm["quads"]].all(axis=1)]
    used = np.unique(skin_quads)
    remap = -np.ones(len(template), dtype=np.int64)
    remap[used] = np.arange(len(used))
    source = trimesh.Trimesh(template[used], remap[triangles_of(skin_quads)], process=False)

    # 2 · fit GNM's skin onto hm08's head
    head, target_surface = head_region(hm_v, hm_f)
    fitted = registration.nricp_amberg(source, target_surface, distance_threshold=0.03, use_faces=True)
    fitted_mesh = trimesh.Trimesh(fitted, source.faces, process=False)
    fit_mm = trimesh.proximity.closest_point(target_surface, fitted)[1] * 1000.0

    # 3 · each hm08 head vertex → the fitted GNM skin under it
    closest, distance, tri = trimesh.proximity.closest_point(fitted_mesh, hm_v[head])
    bary = trimesh.triangles.points_to_barycentric(fitted_mesh.triangles[tri], closest)
    corners = used[source.faces[tri]]  # GNM vertex indices of each hit triangle

    # 4 · GNM's head identity directions, carried across and faded, as MakeHuman targets
    weight = fade(hm_v[head, 1], distance)[:, None]
    identity = gnm["vertex_identity_basis"]
    identity_names = gnm["identity_names"].tolist()
    head_ids = [i for i, n in enumerate(identity_names) if n.startswith("head_")]
    OUT.mkdir(parents=True, exist_ok=True)
    largest = []
    for i in head_ids:
        delta = (identity[i][corners] * bary[:, :, None]).sum(axis=1) * scale * weight  # metres
        largest.append(float(np.linalg.norm(delta, axis=1).max() * 1000.0))
        rows = "\n".join(
            f"{v} {dx:.6f} {dy:.6f} {dz:.6f}"
            for v, (dx, dy, dz) in zip(head, delta * HM08_DM_PER_M, strict=True)
            if abs(dx) + abs(dy) + abs(dz) > 1e-7
        )
        header = (
            f"# GNM v3.0 identity direction {identity_names[i]} (one standard deviation), wrapped onto MakeHuman hm08\n"
            "# by JustStage's libs/wrap/gnm_to_hm08.py. GNM: Copyright Google, Apache-2.0.\n"
        )
        with gzip.open(OUT / f"{identity_names[i]}.target.gz", "wt", encoding="utf-8") as f:
            f.write(header + rows + "\n")

    report = {
        "gnm": "google/gnm-v3 v3_0/gnm_head.npz",
        "gnm_sha256": GNM_SHA256,
        "makehuman": json.loads((MAKEHUMAN / "SOURCE.json").read_text(encoding="utf-8"))["commit"],
        "eye_scale": float(scale),
        "fit_error_mm": {
            "mean": float(fit_mm.mean()),
            "p95": float(np.percentile(fit_mm, 95)),
            "max": float(fit_mm.max()),
        },
        "transfer_distance_mm": {"mean": float(distance.mean() * 1000), "max": float(distance.max() * 1000)},
        "head_vertices": int(len(head)),
        "full_transfer": int((weight[:, 0] > 0.999).sum()),
        "partial_transfer": int(((weight[:, 0] > 0.001) & (weight[:, 0] <= 0.999)).sum()),
        "no_transfer": int((weight[:, 0] <= 0.001).sum()),
        "near_far_m": [NEAR, FAR],
        "targets": len(head_ids),
        "largest_offset_mm": {"median": float(np.median(largest)), "max": float(max(largest))},
        "neck_fade_m": [NECK_LOW, NECK_HIGH],
        "seconds": round(time.time() - t0, 1),
    }
    (OUT / "REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
