# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the shape fit: the head's GNM identity solved so its face points land where the AI painted them — the
way a photo-to-head tool (CC5's Headshot) makes the 3D head that person.

Each face point found in a clay view (landmarks.json) is a ray from that camera onto the head: the mesh vertex nearest
where it hits is that point's vertex (the most common across views). The 170 identity values (GNM's directions, each one
standard deviation) are then solved by Gauss-Newton so those vertices project onto the painted points in every view at
once, with a prior that keeps the face a likely one (‖c‖² weighted against the detector's ~4 px noise). The result goes
to fit.json, which the clay stage reads.

Run: python tools/dev.py test tools/face_test/test_face_fit.py -k face_fit -s
"""

import importlib
import json
from collections import Counter

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
gnm = importlib.import_module("bl_ext.system.juststage.modules.head.gnm_space")
DIR = "E:/Dev/3D/just-stage/.dev/facetest/"
NOISE_PX = 4.0  # the landmark detector's own wobble on these pictures (measured: aligned views stay ~4 px off)
PRIOR = 1.0  # weight of ‖c‖² (the identity in standard deviations) against the pixel residuals / NOISE_PX


def _camera(cam):
    m = np.array(cam["matrix_world"])
    return m[:3, :3], m[:3, 3], cam["lens"] / cam["sensor_width"] * cam["size"], cam["size"]


def _project(P, R, C, f, size):
    """Points → pixel (col, row) with pixel centres at whole numbers, and the 2×3 Jacobians per point."""
    p = (P - C) @ R  # camera space: Rᵀ(P − C)
    d = -p[:, 2]
    col = size / 2 + f * p[:, 0] / d - 0.5
    row = size / 2 - f * p[:, 1] / d - 0.5
    J = np.zeros((len(P), 2, 3))
    J[:, 0, 0], J[:, 0, 2] = f / d, f * p[:, 0] / d**2
    J[:, 1, 1], J[:, 1, 2] = -f / d, -f * p[:, 1] / d**2
    return np.stack([col, row], axis=1), J @ R.T  # chain rule: ∂p/∂P = Rᵀ


def test_face_fit():
    bpy.ops.wm.open_mainfile(filepath=DIR + "face.blend")
    body = bpy.data.objects["Face"]
    co = build.shaped_coords(body)
    polys = [list(p.vertices) for p in body.data.polygons if all(v < 13380 for v in p.vertices)]
    tree = BVHTree.FromPolygons([Vector(c) for c in co], polys)
    marks = json.load(open(DIR + "landmarks.json"))
    cams = json.load(open(DIR + "cameras.json"))
    index, basis = gnm.directions()
    where = {v: i for i, v in enumerate(index)}

    votes = [Counter() for _ in range(478)]
    for view, found in marks.items():
        R, C, f, size = _camera(cams[view])
        for i, (col, row) in enumerate(found["clay"]):
            ray = R @ np.array([(col + 0.5 - size / 2) / f, -(row + 0.5 - size / 2) / f, -1.0])
            hit, _n, face, _d = tree.ray_cast(Vector(C), Vector(ray / np.linalg.norm(ray)))
            if hit is not None:
                verts = polys[face]
                votes[i][min(verts, key=lambda v: (Vector(co[v]) - hit).length)] += 1
    mapping = {i: v.most_common(1)[0][0] for i, v in enumerate(votes) if v and v.most_common(1)[0][0] in where}
    print(f"\n{len(mapping)} of 478 face points map onto the head's GNM vertices")

    c0 = np.array([x.value for x in body.juststage.gnm_identity], dtype=np.float64)
    c = c0.copy()
    lm = np.array(sorted(mapping))
    vid = np.array([mapping[i] for i in lm])
    rows = np.array([where[v] for v in vid])
    B = basis[:, rows, :].astype(np.float64)  # (components, points, 3)
    P0 = co[vid] - np.tensordot(c0, B, axes=1)  # the points without any identity

    def residuals(c):
        P = P0 + np.tensordot(c, B, axes=1)
        res, jac = [], []
        for view, found in marks.items():
            uv, J = _project(P, *_camera(cams[view]))
            target = np.array(found["painted"])[lm]
            res.append((target - uv).ravel() / NOISE_PX)
            jac.append(np.einsum("pij,kpj->pik", J, B).reshape(-1, len(c)) / NOISE_PX)
        return np.concatenate(res), np.vstack(jac)

    r, _ = residuals(c)
    print(f"before: mean {np.abs(r).mean() * NOISE_PX:.1f} px from the painted points")
    for _ in range(8):
        r, J = residuals(c)
        A = J.T @ J + PRIOR * np.eye(len(c))
        step = np.linalg.solve(A, J.T @ r - PRIOR * c)
        c += step
        if np.abs(step).max() < 1e-3:
            break
    r, _ = residuals(c)
    print(f"after: mean {np.abs(r).mean() * NOISE_PX:.1f} px; identity values moved {np.abs(c - c0).max():.2f} sd at most")
    json.dump({"coefficients": c.tolist()}, open(DIR + "fit.json", "w"))
