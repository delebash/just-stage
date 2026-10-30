# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the light taken out of each painting — the scan studios' way: shape goes to the normal map, colour
without light to the albedo. No model; our mesh and the paintings' own normals carry it (the realism recs, rec 3's
"no-model way first").

Per view:
1. Relief: Sapiens2's normals (view_normals.py) keep only what is smaller than ~15 mm — the broad shape is our mesh's
   (from the view's depth picture), so the estimator's broad errors can't bend the head; the eye bags, lids and
   wrinkles the AI painted stay. Saved in world space as nworld_<view>.npy.
2. Light: the painting's brightness fitted as albedo × (a₀ + a·n) — a first-order spherical-harmonic light over these
   normals — times our mesh's own occlusion (the clay picture, lit evenly, shows only where light can't reach). The
   painting divided by that is its albedo, albedo_<view>.npy (linear RGB).

Run (the tool environment): .dev/venv-rdf/Scripts/python -I tools/face_test/delight_views.py [VIEW ...]
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np
import OpenEXR

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest")
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below", "face", "faceleft30", "faceright30")
DETAIL_MM = 15.0  # relief smaller than this comes from the painting, larger from our mesh
LUMA = np.array([0.2126, 0.7152, 0.0722])


def linear(srgb):
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


def depth(view):
    with OpenEXR.File(str(DIR / f"depth_{view}.exr")) as exr:
        ch = exr.channels()
        px = (ch.get("RGB", ch.get("RGBA")) or next(iter(ch.values()))).pixels
    return (px[..., 0] if px.ndim == 3 else px).astype(np.float64)


def mesh_normals(dist, cam):
    """Camera-space normals of our mesh (x right, y up, z toward the camera) and the pixels it covers."""
    size = cam["size"]
    f = cam["lens"] / cam["sensor_width"] * size
    jj, ii = np.meshgrid(np.arange(size), np.arange(size))
    ray = np.stack([(jj + 0.5 - size / 2) / f, -(ii + 0.5 - size / 2) / f, -np.ones_like(jj, float)], axis=2)
    ray /= np.linalg.norm(ray, axis=2, keepdims=True)
    p = ray * dist[..., None]
    n = np.cross(np.gradient(p, axis=0), np.gradient(p, axis=1))
    n /= np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-12)
    n[n[..., 2] < 0] *= -1
    covered = dist < 0.999  # the background reads 1.0 (the clay world's white) in the view-distance picture
    return n, covered


def masked_blur(a, mask, sigma):
    """A blur that ignores pixels outside the mask (normalised convolution)."""
    m = mask.astype(np.float32)
    num = cv2.GaussianBlur((a * m[..., None]).astype(np.float32), (0, 0), sigma)
    den = cv2.GaussianBlur(m, (0, 0), sigma)
    return num / np.maximum(den[..., None], 1e-6)


def unit(a):
    return a / np.maximum(np.linalg.norm(a, axis=2, keepdims=True), 1e-8)


def main() -> int:
    cams = json.load(open(DIR / "cameras.json"))
    for view in sys.argv[1:] or VIEWS:
        cam = cams[view]
        src = DIR / f"aligned_{view}.png"
        src = src if src.exists() else DIR / f"painted_{view}.png"
        painted = linear(cv2.imread(str(src))[..., ::-1].astype(np.float64) / 255.0)
        clay = linear(cv2.imread(str(DIR / f"clay_{view}.png"))[..., ::-1].astype(np.float64) / 255.0)
        dist = depth(view)
        n_mesh, covered = mesh_normals(dist, cam)
        inner = cv2.erode(covered.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        n_ai = np.load(DIR / f"normal_{view}.npy").astype(np.float64)

        # 1. relief: the painting's small shapes on our mesh's broad shape
        mm_per_px = np.median(dist[covered]) * cam["sensor_width"] / cam["lens"] / cam["size"] * 1000.0
        sigma = DETAIL_MM / mm_per_px
        n_rel = unit(n_ai - masked_blur(n_ai, inner, sigma) + masked_blur(n_mesh, inner, sigma))
        n_rel[~covered] = n_mesh[~covered]
        rot = np.array(cam["matrix_world"])[:3, :3]
        np.save(DIR / f"nworld_{view}.npy", (n_rel @ rot.T).astype(np.float16))

        # 2. light: occlusion from the evenly lit clay, a first-order light fitted over the skin, both divided out
        clay_l = clay @ LUMA
        occlusion = np.clip(clay_l / np.median(clay_l[inner]), 0.2, 1.2)
        lum = (painted @ LUMA) / occlusion
        skin = inner & (lum > np.percentile(lum[inner], 15)) & (lum < np.percentile(lum[inner], 97))  # no eyes, brows
        A = np.concatenate([np.ones((skin.sum(), 1)), n_rel[skin]], axis=1)
        y, w = lum[skin], np.ones(skin.sum())
        for _ in range(5):  # robust: freckles and lips shouldn't pull the light
            coef = np.linalg.lstsq(A * w[:, None], y * w, rcond=None)[0]
            r = y - A @ coef
            w = 1.0 / np.maximum(np.abs(r) / (1.4826 * np.median(np.abs(r)) + 1e-9), 1.0)
        shade = np.concatenate([np.ones(dist.shape + (1,)), n_rel], axis=2) @ coef
        shade = np.maximum(shade, 0.25 * np.median(shade[inner])) * occlusion
        albedo = painted / shade[..., None]
        albedo[~covered] = 0.0
        np.save(DIR / f"albedo_{view}.npy", albedo.astype(np.float16))
        vis = albedo / np.percentile(albedo[inner], 99)
        vis = np.where(vis <= 0.0031308, vis * 12.92, 1.055 * np.clip(vis, 0, None) ** (1 / 2.4) - 0.055)
        cv2.imwrite(str(DIR / f"albedo_{view}.png"), (vis[..., ::-1] * 255).clip(0, 255).astype(np.uint8))
        print(f"{view}: {mm_per_px:.2f} mm a pixel, relief below {sigma:.0f} px; light a₀ {coef[0]:.3f}, "
              f"a {np.round(coef[1:], 3).tolist()}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
