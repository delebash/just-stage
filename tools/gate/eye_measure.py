# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The eye against HD Aaron's at the gate's eye view, EEVEE (plan §0; the eye proof): one aligned structure, not a
texture - so a crop centred on each pupil, scaled so the two irises are the same size, compared whole by DISTS (Ding
et al. 2020, piq) - a ranking of trials only: there is no second sample of his eye, and his crop moved 6% of an iris
radius (0.02) is the same pixels, not a floor - and the white's colour.

    .dev/venv-rdf/Scripts/python -I tools/gate/eye_measure.py DIR [TAG ...]

Reads `eevee_eye_cc5.png` and `eevee_eye_ours{TAG}.png`."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
import piq
import torch
from PIL import Image
from skimage.color import rgb2lab

CROP = (3.2, 1.9)  # half the crop's width and height in iris radii: both lids, the corners, the lid margins
SIZE = (512, 304)


def find_eye(rgb: np.ndarray) -> tuple[float, float, float]:
    """The pupil's centre (x, y) and the iris's radius, px: the largest very dark blob in the middle of the frame, then
    rays left and right of it to where the white begins (the lids cut the iris above and below)."""
    lightness = rgb2lab(rgb)[..., 0]
    h, w = lightness.shape
    middle = np.zeros_like(lightness, bool)
    middle[int(0.3 * h):int(0.8 * h), int(0.2 * w):int(0.8 * w)] = True
    n, _, stats, centres = cv2.connectedComponentsWithStats(((lightness < 12) & middle).astype(np.uint8))
    k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    cx, cy = centres[k]
    pupil = np.sqrt(stats[k, cv2.CC_STAT_AREA] / np.pi)
    radii = []
    for angle in np.linspace(-0.6, 0.6, 9):
        for side in (-1, 1):
            for r in range(int(pupil) + 3, int(6 * pupil)):
                y, x = int(cy + r * np.sin(angle)), int(cx + side * r * np.cos(angle))
                if not (0 <= y < h and 0 <= x < w):
                    break
                if lightness[y, x] > 62:
                    radii.append(r)
                    break
    return float(cx), float(cy), float(np.median(radii))


def crop(rgb: np.ndarray, eye: tuple[float, float, float], shift: tuple[float, float] = (0.0, 0.0)) -> torch.Tensor:
    cx, cy, r = eye
    cx, cy = cx + shift[0] * r, cy + shift[1] * r
    box = (int(cx - CROP[0] * r), int(cy - CROP[1] * r), int(cx + CROP[0] * r), int(cy + CROP[1] * r))
    cut = Image.fromarray((rgb * 255).astype(np.uint8)).crop(box).resize(SIZE, Image.LANCZOS)
    return torch.from_numpy(np.asarray(cut, np.float32)[None] / 255.0).permute(0, 3, 1, 2)


def white(rgb: np.ndarray, eye: tuple[float, float, float]) -> tuple[float, float, float]:
    """The white's mean L* a* b*: light pixels beside the iris, within the opening's band."""
    cx, cy, r = eye
    lab = rgb2lab(rgb)
    h, w = lab.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    band = (np.abs(yy - cy) < 0.5 * r) & (np.abs(xx - cx) > 1.15 * r) & (np.abs(xx - cx) < 2.6 * r)
    chroma = np.hypot(lab[..., 1], lab[..., 2])
    sel = band & (lab[..., 0] > 55) & (chroma < 14)  # near-neutral: the white, not the skin beside it
    return tuple(float(lab[..., c][sel].mean()) for c in range(3))


def main() -> None:
    p = argparse.ArgumentParser(prog="eye_measure.py")
    p.add_argument("out_dir", type=Path)
    p.add_argument("tags", nargs="*")
    a = p.parse_args()
    metric = piq.DISTS(reduction="none")

    def load(path: Path) -> np.ndarray:
        return np.asarray(Image.open(path).convert("RGB"), np.float32) / 255.0

    his = load(a.out_dir / "eevee_eye_cc5.png")
    his_eye = find_eye(his)
    ref = crop(his, his_eye)
    with torch.no_grad():
        floor = [float(metric(crop(his, his_eye, s), ref)) for s in ((0.06, 0), (-0.06, 0), (0, 0.06), (0, -0.06))]
    hw = white(his, his_eye)
    print(f"eye: Aaron's iris r {his_eye[2]:.0f} px; his crop moved against itself {np.mean(floor):.4f}; "
          f"his white L*a*b* {hw[0]:.1f} {hw[1]:.1f} {hw[2]:.1f}")
    for tag in [""] + a.tags:
        path = a.out_dir / f"eevee_eye_ours{tag}.png"
        if not path.exists():
            continue
        ours = load(path)
        eye = find_eye(ours)
        with torch.no_grad():
            d = float(metric(crop(ours, eye), ref))
        ow = white(ours, eye)
        print(f"  ours{tag}: DISTS {d:.4f}; white {ow[0]:.1f} {ow[1]:.1f} {ow[2]:.1f}; iris r {eye[2]:.0f} px")


if __name__ == "__main__":
    main()
