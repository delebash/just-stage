# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The eye's iris structure (modules/head/eyes.py `shade`): a photographed iris unwrapped to polar coordinates and kept
as its lightness structure alone, so the character's iris colour tints it - one photo, every colour (CC5's eye: an iris
texture; ours measured equal to HD Aaron's iris at the gate's eye view, 2026-11-05: L* 24.6 / C 14.8 vs 27.2 / 11.3,
detail bands 1.9/3.5/4.2 vs 1.1/2.6/3.9 - RESUME (4b)).

    .dev/venv-rdf/Scripts/python -I tools/make_iris.py

Source: "Green iris" by Lizapopova143 (Wikimedia Commons, 2019-07-15, 5,315 x 3,838), its file page: "This file is
licensed under the Creative Commons Attribution 4.0 International license" (RESEARCH, the eye part by part). The iris
disc and the pupil found by brightness; unwrapped (columns: the angle, 0-2 pi; rows: the pupil's edge at the top to 4%
past the limbus at the bottom); its linear lightness over its mean, to the power STRUCTURE (the gate's 0.7: the photo's
own contrast read harsh), stored at half (0.5 = the mean) in 16-bit grey. Writes
`extension/juststage/data/generated/eyes/iris.png` and `iris.json`."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".dev" / "downloads" / "other_samples" / "commons_green_iris" / "Green_iris.jpg"
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "eyes"
W, H = 2048, 512
STRUCTURE = 0.7
LIMBUS_PAST = 1.04  # the unwrap runs 4% past the limbus


def main() -> None:
    a = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float64) / 255
    lum = a @ [0.2126, 0.7152, 0.0722]
    small = lum[::4, ::4]
    disk = ndimage.binary_fill_holes(ndimage.binary_opening(small > 0.06, iterations=3))
    lab, n = ndimage.label(disk)
    disk = lab == (np.argmax(ndimage.sum(disk, lab, range(1, n + 1))) + 1)
    ys, xs = np.nonzero(disk)
    cy, cx = ys.mean() * 4, xs.mean() * 4
    r_iris = np.sqrt(disk.sum() / np.pi) * 4
    yy, xx = np.mgrid[: small.shape[0], : small.shape[1]]
    pupil = ndimage.binary_opening(small < 0.04, iterations=2) & (np.hypot(yy - cy / 4, xx - cx / 4) < r_iris / 4 * 0.6)
    r_pupil = np.sqrt(pupil.sum() / np.pi) * 4
    th = np.linspace(0, 2 * np.pi, W, endpoint=False)
    rr = np.linspace(r_pupil * 1.02, r_iris * LIMBUS_PAST, H)
    x = cx + rr[:, None] * np.cos(th)[None, :]
    y = cy + rr[:, None] * np.sin(th)[None, :]
    polar = np.stack([ndimage.map_coordinates(a[..., c], [y, x], order=1) for c in range(3)], -1)
    lin = np.where(polar <= 0.04045, polar / 12.92, ((polar + 0.055) / 1.055) ** 2.4)
    light = lin @ [0.2126, 0.7152, 0.0722]
    inside = slice(0, int(H * 0.96))
    rel = (light / max(light[inside].mean(), 1e-6)) ** STRUCTURE
    rel /= rel[inside].mean()
    OUT.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.round(np.clip(rel / 2.0, 0, 1) * 65535).astype(np.uint16)).save(OUT / "iris.png")
    info = {"source": "Green iris, Wikimedia Commons (commons.wikimedia.org/wiki/File:Green_iris.jpg)",
            "author": "Lizapopova143", "licence": "CC BY 4.0", "pupil_px": float(r_pupil), "iris_px": float(r_iris),
            "rows": "the pupil's edge (top) to 4% past the limbus (bottom)", "columns": "angle 0-2 pi",
            "values": "linear lightness over its mean, ^0.7, halved (0.5 = the mean)"}  # fmt: skip
    (OUT / "iris.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(f"iris {r_iris:.0f} px, pupil {r_pupil:.0f} px (share {r_pupil / r_iris:.2f}); wrote {OUT / 'iris.png'}")


if __name__ == "__main__":
    main()
