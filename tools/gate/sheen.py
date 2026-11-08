# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face's shine apart from its colour, ours against HD Aaron (the user's plan of 2026-11-08, "OUR ASSETS TO HD
AARON": face skin first, its sheen; working doc `docs/plans/2026-11-08-own-content-proof.md`). Reads the linear
multilayer EXRs `parts_gate.py render --passes glossy_direct,glossy_indirect,diffuse_direct,diffuse_indirect` writes
beside its PNGs and gives, per window of skin:

- **sheen share** - the specular light's share of all the light the skin sends back: specular / (specular + diffuse),
  luminance means over the window (Rec. 709 weights) - independent of the skin's tone;
- **sheen spread** - the specular light's standard deviation over its mean (its coefficient of variation): a broad
  even sheen reads near 0, scattered glints high;
- **specular level** - the specular light's mean against the window's total, both linear.

    .dev/venv-tools/Scripts/python -I tools/gate/sheen.py OUT_DIR [--engine eevee] [--views face,cheek,eye] [TAG ...]

Writes `sheen_<engine>.json` and `sheen_<view>_<who><tag>.png` (the specular pass, tone-mapped, its windows outlined -
looked at before any number is used)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import OpenEXR
from PIL import Image, ImageDraw

#: windows of skin (top, bottom, left, right as fractions of the frame); the views are placed from each character's own
#: anatomy, so a fraction lands on the same part of both. The close views' as `measure.WINDOWS`; the face view's set
#: by eye on the 2026-11-08 renders (forehead above the brows, each cheek below the eye and beside the nose, the nose's
#: bridge) and checked on the outlined images
WINDOWS = {
    "face": {
        "forehead": (0.20, 0.28, 0.40, 0.60),
        "cheek L": (0.50, 0.58, 0.30, 0.40),
        "cheek R": (0.50, 0.58, 0.60, 0.70),
        "nose bridge": (0.40, 0.50, 0.47, 0.53),
    },  # fmt: skip
    "eye": {"forehead": (0.02, 0.17, 0.30, 0.75)},
    "cheek": {"cheek": (0.15, 0.48, 0.25, 0.58)},
    "forehead": {"forehead": (0.40, 0.80, 0.20, 0.80)},
}
LUMA = np.array([0.2126, 0.7152, 0.0722])
SPECULAR = ("GlossDir", "GlossInd")
DIFFUSE = ("DiffDir", "DiffInd")


def passes(path: Path) -> dict[str, np.ndarray]:
    """Each pass's luminance (H x W) from a Blender multilayer EXR (channels `<layer>.<pass>.<R|G|B>`)."""
    with OpenEXR.File(str(path), separate_channels=True) as f:
        channels = f.channels()
        found: dict[str, dict[str, np.ndarray]] = {}
        for name, channel in channels.items():
            parts = name.split(".")
            if len(parts) >= 2 and parts[-1] in "RGB":
                found.setdefault(parts[-2], {})[parts[-1]] = np.asarray(channel.pixels, np.float64)
    return {p: sum(LUMA[i] * c[k] for i, k in enumerate("RGB")) for p, c in found.items() if set("RGB") <= set(c)}


def measure(lum: dict[str, np.ndarray], box: tuple[float, float, float, float]) -> dict:
    h, w = next(iter(lum.values())).shape
    r0, r1, c0, c1 = int(box[0] * h), int(box[1] * h), int(box[2] * w), int(box[3] * w)
    spec = sum(lum[p][r0:r1, c0:c1] for p in SPECULAR if p in lum)
    diff = sum(lum[p][r0:r1, c0:c1] for p in DIFFUSE if p in lum)
    s, d = float(np.mean(spec)), float(np.mean(diff))
    spread = float(np.std(spec)) / max(s, 1e-9)
    return {
        "sheen share": round(s / max(s + d, 1e-9), 4),
        "sheen spread": round(spread, 3),
        "specular": round(s, 5),
        "diffuse": round(d, 5),
    }


def picture(lum: dict[str, np.ndarray], boxes: dict, path: Path) -> None:
    spec = sum(lum[p] for p in SPECULAR if p in lum)
    top = np.percentile(spec, 99.5) or 1.0
    img = Image.fromarray((np.clip(spec / top, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)).convert("RGB")
    draw = ImageDraw.Draw(img)
    for label, (top_, bottom, left, right) in boxes.items():
        box = (int(left * img.width), int(top_ * img.height), int(right * img.width), int(bottom * img.height))
        draw.rectangle(box, outline=(255, 200, 0), width=4)
        draw.text((box[0] + 6, box[1] + 6), label, fill=(255, 200, 0))
    img.save(path)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("out_dir", type=Path)
    p.add_argument("tags", nargs="*", help="tags beside ours, e.g. _new")
    p.add_argument("--engine", default="eevee")
    p.add_argument("--views", default="face,cheek,eye")
    a = p.parse_args()
    report = {}
    for view in a.views.split(","):
        for who in ["cc5", "ours", *(f"ours{t}" for t in a.tags)]:
            path = a.out_dir / f"{a.engine}_{view}_{who}.exr"
            if not path.exists():
                print("MISSING", path)
                continue
            lum = passes(path)
            if not any(k in lum for k in SPECULAR):
                print("NO SPECULAR PASS in", path, sorted(lum))
                continue
            report[f"{view} {who}"] = {name: measure(lum, box) for name, box in WINDOWS[view].items()}
            picture(lum, WINDOWS[view], a.out_dir / f"sheen_{view}_{who}.png")
            print(view, who, json.dumps(report[f"{view} {who}"]), flush=True)
    (a.out_dir / f"sheen_{a.engine}.json").write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
