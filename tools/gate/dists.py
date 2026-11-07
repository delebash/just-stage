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


def _grid(rows: list[float], cols: list[float], size: float) -> list[tuple[float, float, float, float]]:
    return [(r, r + size, c, c + size) for r in rows for c in cols]


#: --patches: a grid of patches per view (fractions of the frame: rows, columns), every one skin on both renders -
#: looked at on the renders 2026-11-07 (the cheek's rows below 0.54 take stubble, the forehead's first column the
#: hairline): the cheek 24 patches of ~7 mm, the forehead 24 of ~4.5 mm
PATCHES = {
    "cheek": _grid([0.06, 0.18, 0.30, 0.42], [0.10, 0.22, 0.34, 0.46, 0.58, 0.70], 0.12),
    "eye": _grid([0.00, 0.06, 0.12], [0.16, 0.26, 0.36, 0.46, 0.56, 0.66, 0.76, 0.86], 0.06),
}
PERMUTATIONS = 2000


def patch(path: Path, box: tuple[float, float, float, float]) -> torch.Tensor:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    r0, r1, c0, c1 = box
    cut = img.crop((int(c0 * w), int(r0 * h), int(c1 * w), int(r1 * h))).resize((SIZE, SIZE), Image.LANCZOS)
    return torch.from_numpy(np.asarray(cut, np.float32)[None] / 255.0).permute(0, 3, 1, 2)


def _matrix(metric, a: list[torch.Tensor], b: list[torch.Tensor], chunk: int = 32) -> np.ndarray:
    """DISTS between every patch of `a` and every patch of `b`, batched."""
    pairs = [(i, j) for i in range(len(a)) for j in range(len(b))]
    out = np.zeros((len(a), len(b)))
    with torch.no_grad():
        for k in range(0, len(pairs), chunk):
            part = pairs[k:k + chunk]
            d = metric(torch.cat([a[i] for i, _ in part]), torch.cat([b[j] for _, j in part]))
            for (i, j), v in zip(part, d.tolist(), strict=True):
                out[i, j] = v
    return out


def _energy(pooled: np.ndarray, first: np.ndarray) -> float:
    """Half the energy statistic (Székely & Rizzo 2004) of a pooled distance matrix split by `first` (a bool mask):
    the mean distance across the two groups less the mean of their within-group distances."""
    a, b = first, ~first
    off = ~np.eye(len(pooled), dtype=bool)
    within = (pooled[np.ix_(a, a)][off[np.ix_(a, a)]].mean() + pooled[np.ix_(b, b)][off[np.ix_(b, b)]].mean()) / 2
    return float(pooled[np.ix_(a, b)].mean() - within)


def patches(out_dir: Path, engine: str, views: list[str], tags: list[str], tone: bool = False) -> None:
    """The texture measured as two samples of skin, not one window against itself moved: Aaron's patches against each
    other (how much his own skin differs from place to place), ours against his, ours against ours. The excess - the
    mean ours-against-his less the two within-means' average (half Székely & Rizzo's energy statistic) - is ~0 when
    ours is the same texture as his; its p-value is the share of random relabellings of the pooled patches that give
    an excess as large (the energy test's permutation test): p > 0.05 - ours can't be told from his at this sample.
    The 1.5%-jitter floor (the default mode) only says how a window's measure moves: two different patches of his own
    cheek differ ~3x that (2026-11-07)."""
    metric = piq.DISTS(reduction="none")
    rng = np.random.default_rng(0)
    for view in views:
        boxes = PATCHES[view]
        n = len(boxes)
        his = [patch(out_dir / f"{engine}_{view}_cc5.png", b) for b in boxes]
        hh = _matrix(metric, his, his)
        off = ~np.eye(n, dtype=bool)
        print(f"{view}: {n} patches; Aaron's against each other {hh[off].mean():.4f}")
        for tag in [""] + tags:
            path = out_dir / f"{engine}_{view}_ours{tag}.png"
            if not path.exists():
                continue
            ours = [patch(path, b) for b in boxes]
            if tone:  # our skin's colour set to his (each channel's mean over all patches): the texture alone
                gain = torch.cat(his).mean((0, 2, 3), keepdim=True) / torch.cat(ours).mean((0, 2, 3), keepdim=True)
                ours = [(o * gain).clamp(0, 1) for o in ours]
            oh, oo = _matrix(metric, ours, his), _matrix(metric, ours, ours)
            pooled = np.block([[hh, oh.T], [oh, oo]])
            first = np.arange(2 * n) < n
            excess = _energy(pooled, first)
            null = np.array([_energy(pooled, rng.permutation(first)) for _ in range(PERMUTATIONS)])
            p = float((null >= excess).mean())
            print(f"  ours{tag}: against his {oh.mean():.4f}, ours against ours {oo[off].mean():.4f} -> excess "
                  f"{excess:.4f} (by chance {null.mean():.4f} +- {null.std():.4f}; p {p:.3f})")


def main() -> None:
    p = argparse.ArgumentParser(prog="dists.py")
    p.add_argument("out_dir", type=Path)
    p.add_argument("tags", nargs="*", help="factor tags beside ours, e.g. _f-reliefbandx2")
    p.add_argument("--engine", default="eevee")
    p.add_argument("--views", default="cheek,eye")
    p.add_argument("--tone", action="store_true", help="each crop's channel means set to Aaron's first: structure only")
    p.add_argument("--patches", action="store_true", help="two samples of skin (`patches`): the excess over his own")
    a = p.parse_args()
    if a.patches:
        patches(a.out_dir, a.engine, a.views.split(","), a.tags, a.tone)
        return
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
