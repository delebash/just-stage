# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The sclera's veins (modules/head/eyes.py `shade`; the realism review's rec 12, approved: procedural veins, "grown
from seeds by our own rules, deeper = bluer and blurrier" - RESEARCH, the two eye patents: no eyeball model fitted over
a database or a scan, no iris synthesised from image patches, so outside every claim's full set of elements). HD
Aaron's eye view shows fine red vessels on a warm white and pink corners; ours was a flat white (the clean-input gate,
2026-11-06).

    .dev/venv-rdf/Scripts/python -I tools/make_sclera.py

A polar map, as the iris's: columns the angle round the eye (0 at the UV's +u, counter-clockwise), rows the distance
from the eye's centre in limbus radii, R0 (the limbus) at the top to R1 at the bottom. Each texel a colour multiplier
on the white (1 = none). Superficial (conjunctival) vessels: TRUNKS grown in from the fornix (R1) toward the limbus,
wavy, branching, thinning, gone before it; seeded densest at the corners (the CCLRU grading scales: bulbar redness
higher nasally and temporally than above and below - RESEARCH, the gaps file §2); red. Deep (episcleral) vessels:
fewer, wider, straighter, bluish, blurred. A faint pink at the corners. Writes
`extension/juststage/data/generated/eyes/sclera.png` (8-bit, data) and `sclera.json`."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "eyes"
W, H = 4096, 1024
#: limbus radii of the eye's UV radius (it runs with the projected 3D radius): the map's top and bottom rows - the
#: white seen in an opened eye reaches ~1.7 (2026-11-06: at R1 3 with a fade over 0.7 every visible vessel was faint)
R0, R1 = 1.0, 2.0
LIMBUS_MM = 5.9  # the limbus's radius (an adult's ~11.8 mm visible iris)
STEP_MM = 0.12
#: superficial vessels: trunks, root width range (mm), wander per step (deg), branch chance per step, tint
TRUNKS, TRUNK_WIDTH, WANDER, BRANCH, SUPER_TINT, SUPER_ALPHA = 14, (0.03, 0.06), 22.0, 0.03, (0.8, 0.36, 0.36), 0.55
#: deep vessels: fewer, wider, straighter, bluish, blurred (mm)
DEEP, DEEP_WIDTH, DEEP_WANDER, DEEP_TINT, DEEP_ALPHA, DEEP_BLUR = 6, (0.08, 0.14), 6.0, (0.7, 0.64, 0.78), 0.3, 0.05
MIN_WIDTH = 0.011  # mm: thinner than this, a vessel ends (the mean conjunctival vessel: 18.8 um - RESEARCH)
CORNER_PINK = (1.0, 0.976, 0.972)  # the white's faint pink at the corners, far from the limbus


def radius_of_rows(h: int = H) -> np.ndarray:
    """Each row's distance from the eye's centre in limbus radii (texel centres)."""
    return R0 + (np.arange(h) + 0.5) / h * (R1 - R0)


def _px(theta: float, r: float) -> tuple[float, float]:
    return theta / (2 * np.pi) * W, (r - R0) / (R1 - R0) * H


def _grow(rng, canvas, n, width, wander, branch, seed_weight) -> None:
    """`n` trunks from R1 inward, drawn into `canvas` (alpha, 0-255) - each a wavy walk toward the limbus that
    branches, narrows with each branch and with nearness to it, and ends when thinner than MIN_WIDTH."""
    mm_px = (R1 - R0) * LIMBUS_MM / H  # one row in mm
    thetas = np.linspace(0, 2 * np.pi, 3600, endpoint=False)
    p = seed_weight(thetas)
    starts = rng.choice(thetas, size=n, p=p / p.sum())
    stack = [(float(t + rng.normal(0, 0.01)), R1, rng.uniform(*width), np.pi + rng.normal(0, 0.3)) for t in starts]
    while stack:
        theta, r, w, heading = stack.pop()  # heading: direction in the (tangential, radial) plane; pi = straight in
        for _ in range(4000):
            heading += np.radians(rng.normal(0.0, wander))
            heading += 0.05 * (np.pi - heading)  # drawn loosely inward
            dt_mm, dr_mm = STEP_MM * np.sin(heading), STEP_MM * np.cos(heading)
            r2 = r + dr_mm / LIMBUS_MM
            theta2 = theta + dt_mm / (r * LIMBUS_MM)
            near = np.clip((r2 - R0 - 0.03) / 0.25, 0.0, 1.0)  # narrowing over the last ~1.5 mm before the limbus
            shown = w * (0.2 + 0.8 * near)
            if shown < MIN_WIDTH or r2 < R0 + 0.03 or r2 > R1 + 0.05:
                break
            alpha = int(255 * np.clip(shown / 0.05, 0.35, 1.0))
            thick = max(1, int(round(shown / mm_px)))
            (x0, y0), (x1, y1) = _px(theta % (2 * np.pi), r), _px(theta2 % (2 * np.pi), r2)
            if abs(x1 - x0) < W / 2:
                for shift in (-W, 0, W):  # wrapped round the angle's seam
                    cv2.line(canvas, (int(x0 + shift), int(y0)), (int(x1 + shift), int(y1)), alpha, thick, cv2.LINE_AA)
            theta, r = theta2, r2
            w *= 0.993
            if rng.uniform() < branch:
                side = rng.choice([-1.0, 1.0])
                stack.append((theta, r, w * 0.7, heading + side * np.radians(rng.uniform(25, 60))))
                w *= 0.85


def veins(seed: int = 1) -> np.ndarray:
    """The map: H x W x 3 colour multipliers on the white (1 = the plain white)."""
    rng = np.random.default_rng(seed)
    corners = lambda t: 0.1 + np.abs(np.cos(t)) ** 2  # noqa: E731
    superficial = np.zeros((H, W), np.uint8)
    _grow(rng, superficial, TRUNKS, TRUNK_WIDTH, WANDER, BRANCH, corners)
    deep = np.zeros((H, W), np.uint8)
    _grow(rng, deep, DEEP, DEEP_WIDTH, DEEP_WANDER, BRANCH / 3, corners)
    blur = DEEP_BLUR / ((R1 - R0) * LIMBUS_MM / H)
    deep_a = cv2.GaussianBlur(deep.astype(np.float32) / 255, (0, 0), blur) * DEEP_ALPHA
    super_a = superficial.astype(np.float32) / 255 * SUPER_ALPHA
    m = np.ones((H, W, 3), np.float32)
    m *= 1.0 - deep_a[..., None] * (1.0 - np.array(DEEP_TINT, np.float32))
    m *= 1.0 - super_a[..., None] * (1.0 - np.array(SUPER_TINT, np.float32))
    theta = (np.arange(W) + 0.5) / W * 2 * np.pi
    r = radius_of_rows()
    pink = (np.abs(np.cos(theta))[None, :] ** 2) * np.clip((r[:, None] - 1.3) / 0.6, 0.0, 1.0)
    m *= 1.0 - pink[..., None] * (1.0 - np.array(CORNER_PINK, np.float32))
    return np.clip(m, 0.0, 1.0)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    m = veins()
    cv2.imwrite(str(OUT / "sclera.png"), (m[..., ::-1] * 255 + 0.5).astype(np.uint8))
    (OUT / "sclera.json").write_text(json.dumps({"r0": R0, "r1": R1, "limbus_mm": LIMBUS_MM}), encoding="utf-8")
    print("sclera.png", m.shape, "vessel share 1.1-2.0:", round(float((m.min(axis=2) < 0.97).mean()), 4))


if __name__ == "__main__":
    main()
