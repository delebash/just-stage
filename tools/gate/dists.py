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
    # the body (2026-11-07, looked at on both): the back of the hand (~12 mm patches), the chest and upper belly clear
    # of the nipples and the navel (~45 mm), the top of the foot (~14 mm)
    "hand": _grid([0.60, 0.65, 0.70, 0.75], [0.36, 0.41, 0.46, 0.51], 0.05),
    "torso": _grid([0.20, 0.28, 0.45, 0.53, 0.61, 0.69], [0.36, 0.44, 0.52], 0.08),
    "foot": _grid([0.30, 0.36, 0.42, 0.48, 0.54], [0.42, 0.48, 0.54], 0.06),
    # the nose's side and back (~3.6 mm patches), clear of its edge on ours (the chin view is under stubble on both)
    "nose": _grid([0.12, 0.18, 0.24, 0.30, 0.36, 0.42, 0.48], [0.26, 0.32, 0.38, 0.44], 0.06),
    # the forehead's own view (2026-11-07 late, looked at on both, ours with the scalp hidden - `factors nohair`):
    # ~7 mm patches, clear of his frown line between the brows
    "forehead": _grid([0.15, 0.27, 0.39, 0.51, 0.63], [0.10, 0.22, 0.34, 0.46, 0.58, 0.70], 0.12),
}
PERMUTATIONS = 2000
#: DISTS' six layers (piq: the input, then VGG16's five stages; a 256 px patch: 256, 256, 128, 64, 32, 16 px maps)
LAYER_NAMES = ("0 pixels (colour, tone)", "1 VGG stage 1 (finest edges)", "2 VGG stage 2", "3 VGG stage 3",
               "4 VGG stage 4", "5 VGG stage 5 (coarsest)")


def patch(path: Path, box: tuple[float, float, float, float]) -> torch.Tensor:
    img = Image.open(path).convert("RGB")
    w, h = img.size
    r0, r1, c0, c1 = box
    cut = img.crop((int(c0 * w), int(r0 * h), int(c1 * w), int(r1 * h))).resize((SIZE, SIZE), Image.LANCZOS)
    return torch.from_numpy(np.asarray(cut, np.float32)[None] / 255.0).permute(0, 3, 1, 2)


def _features(metric, patches_: list[torch.Tensor]) -> list[list[torch.Tensor]]:
    """Each patch's DISTS features once (its VGG maps and the input itself, `piq.DISTS.get_features`)."""
    with torch.no_grad():
        return [metric.get_features(x) for x in patches_]


def _matrix(metric, fa: list[list[torch.Tensor]], fb: list[list[torch.Tensor]], by_layer: bool = False) -> np.ndarray:
    """DISTS between every patch of `fa` and every patch of `fb` from their cached features - piq's own formula
    (`DISTS.compute_distance`, `ContentLoss.forward`'s weights; 1 - the weighted sum): per layer and channel the means'
    similarity (2 mx my + c) / (mx^2 + my^2 + c) and the covariance's (2 cov + c) / (vx + vy + c), every pair's
    covariance from one matrix product per layer instead of VGG once per pair. `by_layer`: each layer's share of the
    distance (its weights' sum less its weighted terms; layers x n x m) - they add up to the distance."""
    eps = 1e-6
    n_layers = len(fa[0])
    loss = torch.zeros(len(fa), len(fb), dtype=torch.float64)
    shares = []
    with torch.no_grad():
        for layer in range(n_layers):
            x = torch.cat([f[layer] for f in fa]).flatten(2).double()  # n, C, P
            y = torch.cat([f[layer] for f in fb]).flatten(2).double()
            mx, my = x.mean(2), y.mean(2)  # n, C
            vx, vy = x.var(2, unbiased=False), y.var(2, unbiased=False)
            exy = torch.einsum("icp,jcp->ijc", x, y) / x.shape[2]
            cov = exy - mx[:, None, :] * my[None, :, :]
            structure = (2 * mx[:, None, :] * my[None, :, :] + eps) / (mx[:, None, :] ** 2 + my[None, :, :] ** 2 + eps)
            texture = (2 * cov + eps) / (vx[:, None, :] + vy[None, :, :] + eps)
            ws = metric.weights[layer].flatten().double()
            wt = metric.weights[n_layers + layer].flatten().double()
            part = (structure * ws).sum(2) + (texture * wt).sum(2)
            loss += part
            shares.append((ws.sum() + wt.sum() - part).numpy())
    return np.stack(shares) if by_layer else (1 - loss).numpy()


def _energy(pooled: np.ndarray, first: np.ndarray) -> float:
    """Half the energy statistic (Székely & Rizzo 2004) of a pooled distance matrix split by `first` (a bool mask):
    the mean distance across the two groups less the mean of their within-group distances."""
    a, b = first, ~first
    off = ~np.eye(len(pooled), dtype=bool)
    within = (pooled[np.ix_(a, a)][off[np.ix_(a, a)]].mean() + pooled[np.ix_(b, b)][off[np.ix_(b, b)]].mean()) / 2
    return float(pooled[np.ix_(a, b)].mean() - within)


def _flatten(patches_: list[torch.Tensor], to: torch.Tensor) -> list[torch.Tensor]:
    """Each patch's channel means set to `to` (1, 3, 1, 1): the light's level on that patch out - the two faces' shapes
    put each patch under a different light; what stays is the texture."""
    return [(x * to / x.mean((2, 3), keepdim=True)).clamp(0, 1) for x in patches_]


def patches(out_dir: Path, engine: str, views: list[str], tags: list[str], tone: bool = False,
            flat: bool = False, by_layer: bool = False) -> None:
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
        level = torch.cat(his).mean((0, 2, 3), keepdim=True)
        if flat:
            his = _flatten(his, level)
        f_his = _features(metric, his)
        hh = _matrix(metric, f_his, f_his)
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
            if flat:
                ours = _flatten(ours, level)
            f_ours = _features(metric, ours)
            oh, oo = _matrix(metric, f_ours, f_his), _matrix(metric, f_ours, f_ours)
            pooled = np.block([[hh, oh.T], [oh, oo]])
            first = np.arange(2 * n) < n
            excess = _energy(pooled, first)
            null = np.array([_energy(pooled, rng.permutation(first)) for _ in range(PERMUTATIONS)])
            p = float((null >= excess).mean())
            print(f"  ours{tag}: against his {oh.mean():.4f}, ours against ours {oo[off].mean():.4f} -> excess "
                  f"{excess:.4f} (by chance {null.mean():.4f} +- {null.std():.4f}; p {p:.3f})")
            if by_layer:  # the excess split by VGG layer (they add up): at which scale ours differs from his
                hl, ol, ool = (_matrix(metric, fa, fb, by_layer=True) for fa, fb in
                               ((f_his, f_his), (f_ours, f_his), (f_ours, f_ours)))
                for k, name in enumerate(LAYER_NAMES):
                    part = _energy(np.block([[hl[k], ol[k].T], [ol[k], ool[k]]]), first)
                    print(f"    {name:28s} {part:+.4f} ({part / excess:4.0%})" if excess else f"    {name} {part:+.4f}")


def main() -> None:
    p = argparse.ArgumentParser(prog="dists.py")
    p.add_argument("out_dir", type=Path)
    p.add_argument("tags", nargs="*", help="factor tags beside ours, e.g. _f-reliefbandx2")
    p.add_argument("--engine", default="eevee")
    p.add_argument("--views", default="cheek,eye")
    p.add_argument("--tone", action="store_true", help="each crop's channel means set to Aaron's first: structure only")
    p.add_argument("--patches", action="store_true", help="two samples of skin (`patches`): the excess over his own")
    p.add_argument("--flat", action="store_true", help="--patches: each patch's light level out (`_flatten`)")
    p.add_argument("--by-layer", action="store_true", help="--patches: the excess split by DISTS' layers")
    a = p.parse_args()
    if a.patches:
        patches(a.out_dir, a.engine, a.views.split(","), a.tags, a.tone, a.flat, a.by_layer)
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
