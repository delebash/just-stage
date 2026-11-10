# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The lips' mask with a soft border: MPFB2's CC0 lips mask (`data/fetched/makehuman/textures/mpfb_lips.jpg`, on
hm08's own UVs) blurred by a Gaussian of SIGMA_PX texels - 2026-11-10 (the own-content proof, `lipsoft` 10 beside
HD Aaron): every lip setting kept a crisp drawn outline where his lip fades into the skin; with the border softened the
lip reads as his, no outline (`docs/plans/2026-11-08-own-content-proof.md`, 10:1x / 10:27).

    .dev/venv-tools/Scripts/python -I tools/make_lips_soft.py

Writes `extension/juststage/data/generated/skin/lips_soft.png` (8-bit grey, the mask's own size)."""

from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "extension" / "juststage" / "data" / "fetched" / "makehuman" / "textures" / "mpfb_lips.jpg"
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "skin" / "lips_soft.png"
#: texels at the mask's 2048 px: the trial's three-pass box of radius 10 has a spread of ~10.5 texels
SIGMA_PX = 10.5


def soft(mask: np.ndarray, sigma: float = SIGMA_PX) -> np.ndarray:
    """The mask (0-1, H x W) blurred; its total kept (a blur moves weight outward, it doesn't add any)."""
    return ndimage.gaussian_filter(mask.astype(np.float32), sigma, mode="nearest")


def main() -> None:
    mask = np.asarray(Image.open(SOURCE).convert("L"), np.float32) / 255.0
    out = soft(mask)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.round(np.clip(out, 0.0, 1.0) * 255).astype(np.uint8)).save(OUT)
    print("wrote", OUT, out.shape, "sigma", SIGMA_PX)


if __name__ == "__main__":
    main()
