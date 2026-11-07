# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Our microrelief tile against HD Aaron's micro normal, in texture space - no render, seconds a try (the plan's §0
loop for the face skin; the gap measured 2026-11-07: DISTS 0.185 on the cheek against his own 0.06 floor, and no
strength of ours moved it - the pattern differs, not the amount).

Both tiles are turned into slopes at the same real size (`PX_PER_MM`), their slope RMS set equal (the pattern, not the
strength - the render sets that), and lit by the same raking light from four sides (a Lambert shade, 35 deg above the
skin). Then per light: DISTS (Ding et al. 2020, piq) of 3 x 3 crops of ours against his, beside his own floor (his
crops against his crops moved), and the slope's power by band of real size.

    .dev/venv-rdf/Scripts/python -I tools/gate/micro_compare.py AARON_MICRO_N.png AARON_MM OURS.png OURS_MM [--sheet OUT.png]

AARON_MM: the millimetres one repeat of his tile spans on his head (10.56: his head's 528 mm a UV unit / the shader's
tiling 50, measured on `aaron_hair_eevee.blend` 2026-11-07). OURS: a 16-bit height PNG (`tools/make_microrelief.py`)."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import piq
import torch
from PIL import Image
from scipy import ndimage

PX_PER_MM = 50.0  # the comparison's density: above the closest gate view's 34 px/mm
CROP_MM = 5.0
SIZE = 256
LIGHT_ELEVATION_DEG = 35.0
BANDS_MM = ((0.04, 0.1), (0.1, 0.25), (0.25, 0.6), (0.6, 1.5), (1.5, 4.0))


def slopes_from_normal(path: Path, tile_mm: float) -> np.ndarray:
    """His tangent-space normal map as slopes (dh/dx, dh/dy) at PX_PER_MM."""
    n = np.asarray(Image.open(path).convert("RGB"), np.float32) / 255.0 * 2.0 - 1.0
    nz = np.maximum(n[..., 2], 0.2)
    s = np.stack([-n[..., 0] / nz, n[..., 1] / nz], -1)  # OpenGL green up: the sign only turns the light round
    return _resample(s, n.shape[0] / tile_mm)


def slopes_from_height(path: Path, tile_mm: float) -> np.ndarray:
    h = np.asarray(Image.open(path), np.float32)
    h = h / (65535.0 if h.max() > 255 else 255.0)
    if h.ndim == 3:
        h = h[..., 0]
    px_mm = h.shape[0] / tile_mm
    gy, gx = np.gradient(h * px_mm)  # height units per mm; the scale goes with the RMS normalisation
    return _resample(np.stack([gx, gy], -1), px_mm)


def _resample(s: np.ndarray, px_mm: float) -> np.ndarray:
    k = PX_PER_MM / px_mm
    if k < 1:  # anti-aliased: a Gaussian at the new pixel's size first (wrapped - the tiles tile)
        s = np.stack([ndimage.gaussian_filter(s[..., c], 0.5 / k, mode="wrap") for c in range(2)], -1)
    out = np.stack([ndimage.zoom(s[..., c], k, order=1, mode="grid-wrap") for c in range(2)], -1)
    return out / np.sqrt((out ** 2).sum(-1).mean())  # slope RMS 1: the pattern only


def shade(s: np.ndarray, azimuth_deg: float, rms: float = 0.3) -> np.ndarray:
    """Lambert under a raking light, the slope RMS set to `rms` (a skin's micro tilt)."""
    e, a = np.radians(LIGHT_ELEVATION_DEG), np.radians(azimuth_deg)
    light = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    n = np.concatenate([-s * rms, np.ones(s.shape[:2] + (1,), np.float32)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.clip(n @ light, 0.0, 1.0)


def crops(img: np.ndarray, shift: int = 0) -> torch.Tensor:
    n = int(CROP_MM * PX_PER_MM)
    h, w = img.shape
    out = []
    for i in range(3):
        for j in range(3):
            y, x = (i * h // 3 + shift) % (h - n), (j * w // 3 + shift) % (w - n)
            c = Image.fromarray((img[y:y + n, x:x + n] * 255).astype(np.uint8)).resize((SIZE, SIZE), Image.LANCZOS)
            out.append(np.asarray(c, np.float32) / 255.0)
    t = torch.from_numpy(np.stack(out))[:, None].repeat(1, 3, 1, 1)
    return t


def band_power(s: np.ndarray) -> list[float]:
    """The slope field's power per band of real size (share of the total), radially averaged."""
    f = (np.abs(np.fft.fft2(s[..., 0])) ** 2 + np.abs(np.fft.fft2(s[..., 1])) ** 2)
    fy = np.fft.fftfreq(s.shape[0], 1 / PX_PER_MM)
    fx = np.fft.fftfreq(s.shape[1], 1 / PX_PER_MM)
    r = np.hypot(fy[:, None], fx[None, :])  # cycles per mm
    total = f[r > 0].sum()
    return [float(f[(r > 1 / hi) & (r <= 1 / lo)].sum() / total) for lo, hi in BANDS_MM]


def main() -> None:
    p = argparse.ArgumentParser(prog="micro_compare.py")
    p.add_argument("aaron", type=Path)
    p.add_argument("aaron_mm", type=float)
    p.add_argument("ours", type=Path)
    p.add_argument("ours_mm", type=float)
    p.add_argument("--sheet", type=Path)
    a = p.parse_args()
    his, ours = slopes_from_normal(a.aaron, a.aaron_mm), slopes_from_height(a.ours, a.ours_mm)
    metric = piq.DISTS(reduction="none")
    floors, dists = [], []
    for az in (0, 90, 180, 270):
        hs, os_ = shade(his, az), shade(ours, az)
        with torch.no_grad():
            floors.append(float(metric(crops(hs), crops(hs, shift=int(0.7 * PX_PER_MM))).mean()))
            dists.append(float(metric(crops(os_), crops(hs)).mean()))
    print(f"DISTS ours against Aaron {np.mean(dists):.4f} (per light {' '.join(f'{d:.3f}' for d in dists)}); "
          f"his floor {np.mean(floors):.4f}")
    names = " ".join(f"{lo}-{hi}" for lo, hi in BANDS_MM)
    print(f"slope power share by band (mm {names}):")
    print("  Aaron", " ".join(f"{v:.3f}" for v in band_power(his)))
    print("  ours ", " ".join(f"{v:.3f}" for v in band_power(ours)))
    if a.sheet:
        n = int(4.0 * PX_PER_MM)
        tiles = [shade(his, 45)[:n, :n], shade(ours, 45)[:n, :n]]
        sheet = np.concatenate([tiles[0], np.ones((n, 6)), tiles[1]], 1)
        Image.fromarray((sheet * 255).astype(np.uint8)).resize((2 * 600 + 18, 600)).save(a.sheet)
        print("sheet", a.sheet)


if __name__ == "__main__":
    main()
