# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Texture structure against HD Aaron: DISTS (Ding et al., "Image Quality Assessment: Unifying Structure and Texture
Similarity", TPAMI 2020 - made for textures that don't align pixel for pixel; piq's implementation, Apache-2.0) between
each of our windows and his, beside his own noise floor. The plan's §2 m2: "DISTS only if the bands and the eye
disagree" - on the cheek they did (2026-11-07: three bands equal, by eye soft bumps against his crisp network).

    .dev/venv-rdf/Scripts/python -I tools/gate/dists.py OUT_DIR [--engine eevee] [--views cheek,eye] [TAG ...]

Per view's window (`measure.WINDOWS`): DISTS(ours[+TAG], Aaron) over a 3 x 3 grid of the window moved 1.5% of the frame,
cut and resized to 256 px - and DISTS(Aaron, Aaron moved) as the floor. 0 is identical texture; lower is closer. `--tone`: our crops' channel means set to his first (structure only)."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import numpy as np
import piq
import torch
from PIL import Image

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("measure", HERE / "measure.py")
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)

SIZE = 256


def crops(path: Path, box: tuple[float, float, float, float]) -> torch.Tensor:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    out = []
    for dr in (-measure.JITTER, 0.0, measure.JITTER):
        for dc in (-measure.JITTER, 0.0, measure.JITTER):
            r0, r1, c0, c1 = box[0] + dr, box[1] + dr, box[2] + dc, box[3] + dc
            if min(r0, c0) < 0 or max(r1, c1) > 1:
                continue
            cut = img.crop((int(c0 * w), int(r0 * h), int(c1 * w), int(r1 * h))).resize((SIZE, SIZE), Image.LANCZOS)
            out.append(np.asarray(cut, np.float32) / 255.0)
    return torch.from_numpy(np.stack(out)).permute(0, 3, 1, 2)


def main() -> None:
    p = argparse.ArgumentParser(prog="dists.py")
    p.add_argument("out_dir", type=Path)
    p.add_argument("tags", nargs="*", help="factor tags beside ours, e.g. _f-reliefbandx2")
    p.add_argument("--engine", default="eevee")
    p.add_argument("--views", default="cheek,eye")
    p.add_argument("--tone", action="store_true", help="each crop's channel means set to Aaron's first: structure only")
    a = p.parse_args()
    metric = piq.DISTS(reduction="none")
    for view in a.views.split(","):
        for name, box in measure.WINDOWS[view].items():
            ref = crops(a.out_dir / f"{a.engine}_{view}_cc5.png", box)
            centre = ref[len(ref) // 2:len(ref) // 2 + 1].repeat(len(ref), 1, 1, 1)
            with torch.no_grad():
                floor = metric(ref, centre)
            floor = floor[torch.arange(len(ref)) != len(ref) // 2]  # not the centre against itself
            print(f"{view} / {name}: Aaron against himself moved {floor.mean():.4f} (max {floor.max():.4f})")
            for tag in [""] + a.tags:
                path = a.out_dir / f"{a.engine}_{view}_ours{tag}.png"
                if not path.exists():
                    print(f"  ours{tag}: missing")
                    continue
                ours = crops(path, box)
                n = min(len(ours), len(ref))
                if a.tone:  # our tone moved onto his: what is left is texture, not colour
                    ours = (ours * (ref.mean((2, 3), keepdim=True)[:len(ours)] / ours.mean((2, 3), keepdim=True))).clamp(0, 1)
                with torch.no_grad():
                    d = metric(ours[:n], ref[:n])
                print(f"  ours{tag or ''}: {d.mean():.4f} (spread {d.min():.4f}-{d.max():.4f})")


if __name__ == "__main__":
    main()
