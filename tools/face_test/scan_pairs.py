# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material, step 4: point pairs between a scan's face and ours - Wrap's point pairs,
found the way MetaHuman From Mesh finds markers (on a render), with the dense detector our research ranked first
(RealDenseFace, `docs/plans/2026-10-30-research-ai-photo-to-head.md` §2.1; measured here, RESEARCH.md). The same
network reads the scan's square-on render (scan_views.py, scan_marks.py) and our head's round renders, so its own
leanings cancel in the pairs (flame_fit.py's reasoning). Each of FLAME's 5,023 points in its face, nose, lips,
eye-region and forehead masks becomes a 3D pair: the scan's side through its position picture, ours through the round
cameras and the clay depth pictures of the same views; weighted by both sides' certainty (variances add).

Run (the RealDenseFace environment; processor, the card stays free): .dev/venv-rdf/Scripts/python -I
tools/face_test/scan_pairs.py NAME   (scan_marks.py NAME and scan_marks.py ours first)
"""

import importlib.util
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np


def _module(name):
    spec = importlib.util.spec_from_file_location(name, str(Path(__file__).with_name(f"{name}.py")))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


flame_fit = _module("flame_fit")  # RealDenseFace's reading, FLAME's masks
flow_views = _module("flow_views")  # the depth pictures' reader

FACETEST = Path("E:/Dev/3D/just-stage/.dev/facetest")
SCANS = FACETEST / "scans"
EDGE = 6.0  # pixels' footprints: a pixel whose 3x3 neighbours' points spread wider sits on an edge or a hole
AGREE = 0.003  # m: our two views' points for one FLAME vertex farther apart than this are dropped


def on_surface(points, px, footprint):
    """3D points under picture positions (nearest pixel), and whether each is trustworthy (inside, not on an edge:
    its neighbours within EDGE pixels' footprints, `footprint` = metres a pixel spans there)."""
    h, w = points.shape[:2]
    c = np.clip(np.round(px).astype(int), 1, [w - 2, h - 2])
    xyz = points[c[:, 1], c[:, 0], :3]
    ok = np.isfinite(xyz).all(1)
    spread = np.zeros(len(px))
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            n = points[c[:, 1] + dy, c[:, 0] + dx, :3]
            spread = np.maximum(spread, np.nan_to_num(np.linalg.norm(n - xyz, axis=1), nan=1.0))
    inside = (px[:, 0] >= 0) & (px[:, 0] <= w - 1) & (px[:, 1] >= 0) & (px[:, 1] <= h - 1)
    return xyz, ok & inside & (spread < EDGE * footprint)


def depth_points(view, cams):
    """Our head's 3D point under every pixel of a round view - flow_views.View's way: the camera's ray through the
    pixel's centre times the clay depth picture's distance along it; the background (1.0 there) left out."""
    cam = cams[view]
    dist = flow_views.depth(view)
    size, mw = cam["size"], np.array(cam["matrix_world"], dtype=np.float64)
    f = cam["lens"] / cam["sensor_width"] * size
    jj, ii = np.meshgrid(np.arange(size), np.arange(size))
    ray = np.stack([(jj + 0.5 - size / 2) / f, -(ii + 0.5 - size / 2) / f, -np.ones_like(jj, float)], axis=2)
    ray /= np.linalg.norm(ray, axis=2, keepdims=True)
    world = (ray * dist[..., None]) @ mw[:3, :3].T + mw[:3, 3]
    world[dist >= 0.999] = np.nan
    return world


def draw(img, px, keep, path):
    out = np.ascontiguousarray(img[..., ::-1]).copy()
    for (x, y), k in zip(px[::7], keep[::7], strict=True):
        cv2.circle(out, (int(round(x)), int(round(y))), 1, (0, 255, 0) if k else (0, 0, 255), -1)
    cv2.imwrite(str(path), out)


def main(argv):
    name = argv[0]
    out = SCANS / name
    masks = flame_fit.load_pickle(flame_fit.FLAME_MASKS)
    region = np.unique(np.concatenate([np.asarray(masks[k], np.int64) for k in flame_fit.FACE_PARTS]))
    rdf = flame_fit.load_rdf("cpu")

    marks = json.loads((out / "marks.json").read_text())
    label = "face" if "face" in marks else marks["best"].replace("view_", "")  # the zoomed square-on render first
    points = marks["face"]["points"] if "face" in marks else marks["views"][marks["best"]]["points"]
    cam = json.loads((out / "views.json").read_text())["cams"][label]
    rgba = cv2.imread(str(out / f"view_{label}.png"), cv2.IMREAD_UNCHANGED)[..., [2, 1, 0, 3]].astype(np.float32) / 255
    img = rgba[..., :3] * rgba[..., 3:] + 0.5 * (1 - rgba[..., 3:])  # over mid grey, as a photo's backdrop
    img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    px_s, lv_s, _ = flame_fit.rdf_points(rdf, img, points)
    scan_xyz, ok_s = on_surface(np.load(out / f"pos_{label}.npy"), px_s, cam["ortho_scale"] / cam["size"])
    draw(img, px_s, ok_s, out / "pairs_scan.png")

    ours = json.loads((SCANS / "ours_marks.json").read_text())
    cams = json.loads((FACETEST / "cameras.json").read_text())
    acc, wsum, views_xyz = np.zeros((5023, 3)), np.zeros(5023), []
    lv_o = np.full(5023, 3.0)
    for view, v in ours["views"].items():
        img_o = cv2.imread(v["image"])[..., ::-1]
        px_o, lv, _ = flame_fit.rdf_points(rdf, img_o, v["points"])
        world = depth_points(view, cams)
        f = cams[view]["lens"] / cams[view]["sensor_width"] * cams[view]["size"]
        reach = np.linalg.norm(world - np.asarray(cams[view]["matrix_world"])[:3, 3], axis=2)
        xyz, ok = on_surface(world, px_o, np.nanmedian(reach) / f)
        draw(img_o, px_o, ok, SCANS / f"pairs_ours_{view}.png")
        w = np.where(ok, np.exp(-lv), 0.0)
        acc += np.nan_to_num(xyz) * w[:, None]
        wsum += w
        lv_o = np.minimum(lv_o, np.where(ok, lv, 3.0))
        views_xyz.append(np.where(ok[:, None], xyz, np.nan))
    ours_xyz = acc / np.maximum(wsum, 1e-12)[:, None]
    both = np.isfinite(views_xyz[0]).all(1) & np.isfinite(views_xyz[1]).all(1)
    apart = np.where(both, np.linalg.norm(np.nan_to_num(views_xyz[0] - views_xyz[1]), axis=1), 0.0)
    ok_o = (wsum > 0) & (apart < AGREE)

    keep = np.zeros(5023, bool)
    keep[region] = True
    keep &= ok_s & ok_o
    weight = 1.0 / (np.exp(lv_s) + np.exp(lv_o))
    idx = np.flatnonzero(keep)
    np.savez(out / "pairs.npz", flame_idx=idx, scan_xyz=scan_xyz[idx], ours_xyz=ours_xyz[idx], weight=weight[idx])
    print(f"{name}: {len(idx)} pairs of {len(region)} face points (scan side usable {ok_s[region].mean():.0%}, ours "
          f"{ok_o[region].mean():.0%}; our two views apart median {np.median(apart[both & keep]) * 1000:.2f} mm); "
          f"log variance median scan {np.median(lv_s[idx]):.2f}, ours {np.median(lv_o[idx]):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
