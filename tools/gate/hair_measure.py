# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The scalp hair, ours against HD Aaron's, EEVEE (plan §0; §19.2 item 27: the hair is judged against his, not against
our own Cycles). From `hair_cover.py`'s alpha renders and the gate's own renders of the same views:

- coverage: the hair's silhouette IoU (HairCS's measure; the views are placed from each head's anatomy, so a frame
  shows the same part on both) and each one's hair area as a share of the frame;
- look: CIE L* of the hair (mean, and p95 for its highlights) where the alpha says hair, in the gate's render.

    .dev/venv-tools/Scripts/python -I tools/gate/hair_measure.py DIR [--views hair_back,profile,front]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.color import rgb2lab

SOLID = 0.5  # alpha above this is hair


def _alpha(path: Path, size: int) -> np.ndarray:
    a = Image.open(path).convert("RGBA").resize((size, size), Image.BILINEAR)
    return np.asarray(a, np.float32)[..., 3] / 255.0


def main() -> None:
    p = argparse.ArgumentParser(prog="hair_measure.py")
    p.add_argument("out_dir", type=Path)
    p.add_argument("--views", default="hair_back,profile,front")
    a = p.parse_args()
    for view in a.views.split(","):
        renders = {who: a.out_dir / f"eevee_{view}_{who}.png" for who in ("cc5", "ours")}
        covers = {who: a.out_dir / f"eevee_{view}_{who}_cover.png" for who in ("cc5", "ours")}
        if not all(p.exists() for p in [*renders.values(), *covers.values()]):
            print(f"{view}: missing renders")
            continue
        size = 1024
        hair = {who: _alpha(covers[who], size) > SOLID for who in covers}
        iou = (hair["cc5"] & hair["ours"]).sum() / max((hair["cc5"] | hair["ours"]).sum(), 1)
        line = [f"{view}: coverage IoU {iou:.3f}"]
        for who in ("cc5", "ours"):
            rgb = np.asarray(Image.open(renders[who]).convert("RGB").resize((size, size), Image.BILINEAR),
                             np.float32) / 255.0  # fmt: skip
            lightness = rgb2lab(rgb)[..., 0][hair[who]]
            line.append(f"{who}: area {hair[who].mean():.3f}, L* {lightness.mean():.1f} (p95 {np.percentile(lightness, 95):.1f})")
        print(" | ".join(line))


if __name__ == "__main__":
    main()
