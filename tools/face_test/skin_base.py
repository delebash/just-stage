# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, a skin base for one character from several scans - not a copy of one scanned person (the user,
2026-11-02: "they cant keep looking like the same character or base, it has to be completelety adjustable like
methuman"). MetaHuman's way (a scanned texture index with wrinkle density, stubble, freckles and moles as controls):

1. `split`: each scan's skin in our layout (scan_base.py) taken apart in linear light - the fine layer (pores, fine
   lines: the skin over its 6-texel blur, ~1 mm), the mid layer (mottling, redness: the 6-texel blur over the 48-texel
   one, ~8 mm); its tone (the 48-texel blur) is dropped - each character has its own. The scanned person's own marks
   (moles, blemishes: small dark spots in the mid and fine layers) are taken out. Kept only where the scan reached our
   surface (within 4 mm).
2. `compose`: one character's base as a ratio map around 1 - its mid and fine layers mixed from the scans with its
   own weights, plus its own mottling noise, age (how strong the fine layer is), redness, freckles and moles from its
   seed. The projection (test_face_project.py) multiplies it by the character's tone and blends it under the face.

Run (the tool environment): .dev/venv-rdf/Scripts/python -I tools/face_test/skin_base.py split NAME... | compose SEED
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest/scans")
FINE_SIGMA, MID_SIGMA = 6.0, 48.0  # texels of the 4096 HeadTile (~6 texels a mm on the face)
REACH = 0.004  # m: texels farther than this from the scan didn't get its skin (the chest, the ears' folds)


def linear(srgb):
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


def masked_blur(img, valid, sigma):
    """A blur that only averages valid texels (normalized convolution)."""
    w = valid.astype(np.float32)
    num = cv2.GaussianBlur(img * w[..., None], (0, 0), sigma)
    den = cv2.GaussianBlur(w, (0, 0), sigma)
    return num / np.maximum(den[..., None], 1e-6)


def split(name):
    srgb = cv2.imread(str(DIR / f"base_{name}.png"))[..., ::-1].astype(np.float32) / 255.0
    gap = np.load(DIR / f"base_{name}_gap.npy").astype(np.float32)
    mask = cv2.imread(str(DIR / "base_mask.png"), 0) > 0
    valid = mask & (gap < REACH) & (srgb.max(axis=2) > 0.05)
    lin = np.maximum(linear(srgb), 1e-4)
    b_fine = masked_blur(lin, valid, FINE_SIGMA)
    b_mid = masked_blur(lin, valid, MID_SIGMA)
    fine = np.log(lin / np.maximum(b_fine, 1e-4))
    mid = np.log(np.maximum(b_fine, 1e-4) / np.maximum(b_mid, 1e-4))
    # the scanned person's own marks: spots darker than their surroundings by >30%, ~0.5-6 mm across (at >12% the bald
    # scan's scalp stubble and pores went too - 23% of its texels, a patchwork of blurred holes)
    lum = (mid + fine) @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    spot = cv2.GaussianBlur(lum, (0, 0), 2.0) - cv2.GaussianBlur(lum, (0, 0), 12.0)
    dark = ((spot < -0.30) & valid).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(dark)
    area = stats[:, cv2.CC_STAT_AREA]
    small = np.isin(labels, np.flatnonzero((area >= 10) & (area < 1200) & (np.arange(count) > 0)))
    marks = cv2.dilate(small.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    keep = valid & ~marks
    fine[marks] = 0.0
    mid[marks] = masked_blur(mid, keep, 12.0)[marks]
    fine[~valid], mid[~valid] = 0.0, 0.0
    np.clip(fine, -0.5, 0.12, out=fine)  # the scan's own shine (white specks in a photogrammetry colour map) out
    np.savez_compressed(DIR / f"layers_{name}.npz", fine=fine.astype(np.float16), mid=mid.astype(np.float16),
                        valid=valid)
    print(f"{name}: {valid.mean() / mask.mean():.0%} of the head's texels from the scan; {count - 1} dark spots, "
          f"{int(small.any() and np.unique(labels[small]).size)} small ones taken out ({marks.sum()} texels); "
          f"fine layer spread {fine[valid].std():.3f}, mid {mid[valid].std():.3f}")


def noise(shape, rng, sigma):
    """Smooth random field, zero mean, unit spread."""
    n = cv2.GaussianBlur(rng.standard_normal(shape).astype(np.float32), (0, 0), sigma)
    return n / max(float(n.std()), 1e-6)


def compose(seed, params=None):
    """One character's base: a ratio map (H x W x 3, ~1) and where the scans covered."""
    rng = np.random.default_rng(seed)
    p = {"scans": None, "age": float(rng.uniform(0.7, 1.3)), "mottle": float(rng.uniform(0.6, 1.2)),
         "redness": float(rng.uniform(0.0, 0.06)), "freckles": float(rng.uniform(0.0, 1.0)),
         "moles": int(rng.integers(2, 12)), **(params or {})}
    names = sorted(f.stem[len("layers_"):] for f in DIR.glob("layers_*.npz"))
    weights = p["scans"] or {n: float(w) for n, w in zip(names, rng.dirichlet(np.ones(len(names))), strict=True)}
    fine = mid = cover = None
    for n, w in weights.items():
        z = np.load(DIR / f"layers_{n}.npz")
        v = z["valid"].astype(np.float32)[..., None] * w
        f, m = z["fine"].astype(np.float32) * v, z["mid"].astype(np.float32) * v
        fine, mid, cover = (f, m, v) if fine is None else (fine + f, mid + m, cover + v)
    fine, mid = fine / np.maximum(cover, 1e-6), mid / np.maximum(cover, 1e-6)
    shape = fine.shape[:2]
    # its own mottling, so two characters from the same scans still differ (and texels no scan reached get some)
    own = 0.04 * noise(shape, rng, 10.0)[..., None] * np.array([1.0, 0.9, 0.85], np.float32)
    ratio_log = p["age"] * fine + p["mottle"] * mid + own
    ratio_log[..., 0] += p["redness"] * noise(shape, rng, 24.0)  # patchy redness
    # freckles (small, many) and moles (few, larger, darker brown), placed by its seed
    spots = np.zeros(shape, np.float32)
    for count, radius, depth in ((int(4000 * p["freckles"]), 2.5, 0.10), (p["moles"], 6.0, 0.45)):
        ys, xs = rng.integers(0, shape[0], count), rng.integers(0, shape[1], count)
        for y, x in zip(ys, xs, strict=True):
            r = float(radius * rng.uniform(0.6, 1.4))
            cv2.circle(spots, (int(x), int(y)), max(1, int(round(r))), float(depth * rng.uniform(0.5, 1.0)), -1)
    spots = cv2.GaussianBlur(spots, (0, 0), 1.0)
    ratio_log -= spots[..., None] * np.array([0.8, 1.0, 1.2], np.float32)  # brown: blue darkest
    ratio = np.exp(ratio_log).astype(np.float32)
    return ratio, cover[..., 0] > 0, {**p, "scans": weights}


def main(argv):
    if argv[0] == "split":
        for name in argv[1:]:
            split(name)
    elif argv[0] == "compose":
        seed = int(argv[1])
        ratio, cover, p = compose(seed)
        out = np.clip(0.45 * ratio, 0, 1) ** (1 / 2.2)  # a flat mid-skin tone, only to look at it
        cv2.imwrite(str(DIR / f"base_char{seed}.png"), (out[..., ::-1] * 255).astype(np.uint8))
        cv2.imwrite(str(DIR / f"base_char{seed}_small.png"),
                    cv2.resize((out[..., ::-1] * 255).astype(np.uint8), (1024, 1024), interpolation=cv2.INTER_AREA))
        np.save(DIR / f"base_char{seed}.npy", ratio.astype(np.float16))  # for the projection (no OpenCV in Blender)
        np.save(DIR / f"base_char{seed}_cover.npy", cover)
        print(f"char {seed}: {json.dumps(p)}; covered {cover.mean():.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
