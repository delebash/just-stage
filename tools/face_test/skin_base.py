# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, a skin base for one character from several scans - not a copy of one scanned person (the user,
2026-11-02: "they cant keep looking like the same character or base, it has to be completelety adjustable like
methuman"). MetaHuman's way (a scanned texture index with wrinkle density, stubble, freckles and moles as controls):

1. `split`: each scan's skin in our layout (scan_bake.py's bake, only where scan_skin.py's mask says skin) taken
   apart in linear light - the fine layer (pores, fine lines: the skin over its 6-texel blur, ~1 mm), the mid layer
   (mottling, redness: the 6-texel blur over the 48-texel one, ~8 mm); its tone (the 48-texel blur) is dropped - each
   character has its own. The scanned person's own marks (moles, blemishes: small dark spots in the mid and fine
   layers) are taken out.
2. `compose`: one character's base as a ratio map around 1 - its pores from ONE scan (the next ones only filling
   where it didn't reach), its blotchiness mixed from 2-3, plus its own mottling noise, age (how strong the fine layer
   is), redness, freckles and moles from its seed. The projection (test_face_project.py) multiplies it by the
   character's tone and blends it under the face.

Run (the tool environment): .dev/venv-rdf/Scripts/python -I tools/face_test/skin_base.py split NAME... | compose SEED
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest/scans")
FINE_SIGMA, MID_SIGMA = 6.0, 48.0  # texels of the 4096 HeadTile (~6 texels a mm on the face)
FEATHER = 48.0  # texels (~8 mm): a scan's edge fades in over this - at 6 every hand-over between the partial scans
#               showed as an edge (round 78: a smooth patch beside a stubbly one on the scalp)
#: skin's own range for the layers: colour shifts (a channel off the texel's brightness) and brightness swings beyond
#: these are a scan's leftovers - an ear's red inside, a necklace, a lip's edge (red minus blue to 0.4-0.5 at the 99th
#: percentile in ammamma's and yaro13's mid layers, lps 0.09) - soft-clipped (tanh) to them
HUE_RANGE, LUM_RANGE = 0.08, 0.35
EDGE = 12  # texels (~2 mm on the face): a scan's skin is used this far inside its mask's edge
#: stubble: on a stubbled scan's fine layer the small dark marks (its black top-hat, up to ~1 mm) in the beard and scalp
#: regions are kept by the character's stubble setting; at 0 they go - all but STUBBLE_FLOOR of them (the pores there
#: go with them: a shaved face still shows its follicles). Measured 2026-11-03 (char 12, fine detail = |lum - blur3|):
#: stubble 1 - beard 2.76, scalp 2.40, elsewhere 1.96; stubble 0 at floor 0.3 - beard 1.40, scalp 1.25 (smoother than
#: the rest of the face); 0.55 puts a shaved beard near the face's own 1.95 (the trend between the two)
STUBBLE_KERNEL, STUBBLE_FLOOR = 7, 0.55


def _module(name, path):
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def regions(size=4096):
    """Where stubble grows, as soft masks in our HeadTile layout (cached in scans/regions.npz): the beard (upper lip,
    chin, jaw and the throat) and the scalp (above the hairline, the back and sides above the ears) - from our head's
    own geometry, measured from the eyes. Every identity shares this layout (one topology, one unwrap)."""
    cache = DIR / "regions.npz"
    if cache.exists():
        z = np.load(cache)
        return z["beard"], z["scalp"]
    up = _module("up", "E:/Dev/3D/just-stage/extension/juststage/core/uv_projection.py")
    E = np.load(DIR / "head_export.npz")
    (pts,), covered = up.raster_uv(E["tri_uv"], [E["co"][E["tris"]].astype(np.float32)], size)
    eye = (np.asarray(E["eye_left"]) + np.asarray(E["eye_right"])) / 2
    x, y, z = (pts[..., i] - eye[i] for i in range(3))
    front = 1.0 - _smooth(y, 0.06, 0.09)  # ahead of the ears
    beard = front * _smooth(-z, 0.035, 0.050) * (1.0 - _smooth(-z, 0.19, 0.22)) * (1.0 - _smooth(np.abs(x), 0.07, 0.09))
    scalp = np.maximum(_smooth(z, 0.05, 0.075), _smooth(y, 0.08, 0.11) * _smooth(z, -0.04, -0.01))
    beard, scalp = (np.where(covered, m, 0.0).astype(np.float16) for m in (beard, scalp))
    np.savez_compressed(cache, beard=beard, scalp=scalp)
    return beard, scalp


def _without_stubble(fine, keep):
    """A fine layer with its small dark marks (stubble and pores: closing minus itself, in brightness) lifted where
    `keep` (0-1 per texel) is below 1 - all but STUBBLE_FLOOR of them at 0."""
    luma = np.array([0.2126, 0.7152, 0.0722], np.float32)
    lum = fine @ luma
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (STUBBLE_KERNEL, STUBBLE_KERNEL))
    dark = cv2.morphologyEx(lum, cv2.MORPH_CLOSE, k) - lum  # >= 0 on the dark marks
    return fine + ((1.0 - STUBBLE_FLOOR) * (1.0 - keep) * dark)[..., None]


def linear(srgb):
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


def masked_blur(img, valid, sigma):
    """A blur that only averages valid texels (normalized convolution)."""
    w = valid.astype(np.float32)
    num = cv2.GaussianBlur(img * w[..., None], (0, 0), sigma)
    den = cv2.GaussianBlur(w, (0, 0), sigma)
    return num / np.maximum(den[..., None], 1e-6)


def split(name):
    """The scan's skin as baked into our layout (scan_bake.py: colour + coverage), only where the skin mask
    (scan_skin.py) says skin - the route of `docs/plans/2026-11-02-scan-skin-base.md`."""
    d = DIR / name
    srgb = cv2.imread(str(d / "bake_colour.png"))[..., ::-1].astype(np.float32) / 255.0
    size = srgb.shape[0]
    cover = cv2.imread(str(d / "bake_cover.png"), 0) > 127
    skin = cv2.resize(cv2.imread(str(d / "skin.png"), 0), (size, size), interpolation=cv2.INTER_LINEAR) > 127
    mask = cover  # what this scan reached; the head's whole layout is the union over scans
    valid = cover & skin & (srgb.max(axis=2) > 0.05)
    # pulled in ~2 mm from its edges: the collar's and hairline's shadows sit just inside a skin mask (round 74's dark
    # squiggles low on the neck)
    valid = cv2.erode(valid.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (EDGE * 2 + 1,) * 2)) > 0
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
    luma = np.array([0.2126, 0.7152, 0.0722], np.float32)
    for layer in (mid, fine):
        lum = layer @ luma
        hue = layer - lum[..., None]
        layer[...] = (LUM_RANGE * np.tanh(lum / LUM_RANGE))[..., None] + HUE_RANGE * np.tanh(hue / HUE_RANGE)
    np.savez_compressed(d / "layers.npz", fine=fine.astype(np.float16), mid=mid.astype(np.float16), valid=valid)
    print(f"{name}: skin on {valid.mean() / mask.mean():.0%} of the texels the scan reached ({valid.mean():.1%} of the "
          f"tile); {count - 1} dark spots, "
          f"{int(small.any() and np.unique(labels[small]).size)} small ones taken out ({marks.sum()} texels); "
          f"fine layer spread {fine[valid].std():.3f}, mid {mid[valid].std():.3f}")


def noise(shape, rng, sigma):
    """Smooth random field, zero mean, unit spread."""
    n = cv2.GaussianBlur(rng.standard_normal(shape).astype(np.float32), (0, 0), sigma)
    return n / max(float(n.std()), 1e-6)


def _feathered(valid):
    """A scan's coverage with its edge faded in over FEATHER texels (inside its own texels only)."""
    v = valid.astype(np.float32)
    return np.clip(cv2.GaussianBlur(v, (0, 0), FEATHER) * 2.0 - 1.0, 0.0, 1.0) * v


def compose(seed, params=None):
    """One character's base: a ratio map (H x W x 3, ~1) and where the scans covered. The approved way (TASKS "THE
    SCAN ROUTE" (6), MetaHuman's index): the pores and fine lines from ONE scan - averaging several people's pores at a
    texel cancels them (~1/sqrt(n)) - the next scans in this character's order only filling where that one didn't
    reach; the blotchiness (mid layer) mixed from 2-3 scans, scaled back to one scan's strength; the tone is the
    character's own (the projection multiplies it in). Its sex picks the scans first (a woman's pores from women's
    scans; the others only fill where those didn't reach), and its stubble settings (beard, scalp; 0 for a woman)
    decide how much of a stubbled scan's stubble stays."""
    rng = np.random.default_rng(seed)
    scans = _module("scan_list", Path(__file__).with_name("scan_list.py")).SCANS
    names = sorted(f.parent.name for f in DIR.glob("*/layers.npz"))
    sex = (params or {}).get("sex") or str(rng.choice(["m", "f"]))
    own_sex = [str(n) for n in rng.permutation([n for n in names if scans[n]["sex"] == sex])]
    others = [str(n) for n in rng.permutation([n for n in names if scans[n]["sex"] != sex])]
    others.sort(key=lambda n: scans[n]["stubble"])  # a smooth scan fills before a stubbled one
    pool = own_sex if len(own_sex) >= 2 else names
    k = int(min(len(pool), rng.integers(2, 4)))
    mixed = [str(n) for n in rng.choice(pool, k, replace=False)]
    male = sex == "m"
    p = {"sex": sex, "fine_from": own_sex + others,
         "mid_from": dict(zip(mixed, (float(w) for w in rng.dirichlet(np.ones(k))), strict=True)),
         "stubble": float(rng.uniform(0.0, 1.0)) if male else 0.0,
         "scalp_stubble": float(rng.uniform(0.0, 1.0)) if male else 0.0,
         "age": float(rng.uniform(0.7, 1.3)), "mottle": float(rng.uniform(0.6, 1.2)),
         "redness": float(rng.uniform(0.0, 0.06)), "freckles": float(rng.uniform(0.0, 1.0)),
         "moles": int(rng.integers(2, 12)), **(params or {})}
    if p.get("pores_first"):  # a chosen scan's pores first (a character made to a description), the order kept after it
        p["fine_from"] = [p["pores_first"]] + [n for n in p["fine_from"] if n != p["pores_first"]]
    layers = {n: np.load(DIR / n / "layers.npz") for n in set(p["fine_from"]) | set(p["mid_from"])}
    shape = layers[p["fine_from"][0]]["fine"].shape[:2]
    beard, scalp = (m.astype(np.float32) for m in regions(shape[0]))
    keep = 1.0 - np.clip(beard * (1.0 - p["stubble"]) + scalp * (1.0 - p["scalp_stubble"]), 0.0, 1.0)
    # fine: the first scan over the next, each only where the ones before it left room
    fine, mid_fill, left = np.zeros((*shape, 3), np.float32), np.zeros((*shape, 3), np.float32), np.ones(shape, np.float32)
    for n in p["fine_from"]:
        a = left * _feathered(layers[n]["valid"])
        if not a.any():
            continue
        f = layers[n]["fine"].astype(np.float32)
        if scans[n]["stubble"]:
            f = _without_stubble(f, keep)
        fine += a[..., None] * f
        mid_fill += a[..., None] * layers[n]["mid"].astype(np.float32)
        left -= a
    cover = left < 0.5
    # mid: the chosen scans' weighted sum over sqrt(sum of squared weights) - for unrelated patterns that keeps one
    # scan's strength (a plain mean shrinks it); where none of them reached, the fine order's mid layer
    num, sq, total = np.zeros((*shape, 3), np.float32), np.zeros(shape, np.float32), np.zeros(shape, np.float32)
    for n, w in p["mid_from"].items():
        a = w * _feathered(layers[n]["valid"])
        num += a[..., None] * layers[n]["mid"].astype(np.float32)
        sq += a * a
        total += a
    # the fine order's mid layer joins as one more part wherever the chosen scans fall short - a weight, not a switch
    # (where their coverage ended, the switch drew an edge, round 78)
    b = np.clip(1.0 - total, 0.0, 1.0)
    num += b[..., None] * mid_fill
    sq += b * b
    mid = num / np.sqrt(np.maximum(sq, 1e-8))[..., None]
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
    # a ratio around 1: each channel's mean over what the scans covered set to 1 - the scans' own shading had left it
    # below (round 74's scalp darker and more orange than the face); the character's tone is the projection's
    ratio /= ratio[cover].mean(axis=0)
    return ratio, cover, p


def main(argv):
    if argv[0] == "split":
        for name in argv[1:]:
            split(name)
    elif argv[0] == "compose":  # compose SEED ['{"sex": "f", "fine_from": [...], ...}']
        seed = int(argv[1])
        ratio, cover, p = compose(seed, json.loads(argv[2]) if len(argv) > 2 else None)
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
