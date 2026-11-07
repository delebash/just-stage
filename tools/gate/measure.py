# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The gate's measures on its renders (the plan's §2: m2 detail, m3 colour, the repeatability band), outside Blender:

    .dev/venv-tools/Scripts/python -I tools/gate/measure.py OUT_DIR [--engine eevee|cycles]

For every view both characters were rendered in (`{engine}_{view}_{who}.png`, `tools/gate/parts_gate.py render`), each
window of that view (WINDOWS: fractions of the frame - the views are placed from each character's own anatomy, so a
fraction lands on the same part of both):

- **colour** - mean CIE L*, a*, b* of the window's skin (scikit-image's `rgb2lab`, sRGB D65), as the image shows it
  through the app's look.
- **detail by scale** - the window's L* power spectrum, radially averaged (the standard surface-texture measure, ISO
  25178-2's power spectral density), summed over bands of real size (BANDS_MM, from the view's frame width) and given
  as an RMS in L* units - comparable with the earlier band standard deviations, but in millimetres on the skin, not
  pixels, so every view and every character reads the same scale. A band whose finest wavelength is under two pixels
  is not resolved and reads None, as is one whose finest wavelength doesn't fit twice in the window.
- **ridges** - long lines at the mid scale (veins, tendons, creases; ~1.5-8 mm wide) apart from speckle: the mean of
  Frangi et al.'s 1998 vesselness (scikit-image's `frangi`) over the window, dark ridges (creases, veins) and light
  ones (tendons) apart.
- **repeatability** - each measure again with the window moved by JITTER of the frame in a 3 x 3 grid: its spread
  ((max - min) / |mean|). "Equal" at the gate is within this band (Q-GATE-1); over 15% the window straddles a feature
  and is moved (the skin itself varies 8-9% on the cheek at 1.5% of the frame - 2026-11-07).

The scale comes from `frames.json`, which `parts_gate.py render` writes beside the renders (each view's frame
width at its target). Writes `measures_<engine>.json` beside the renders and `windows_<view>.png`, each render with its windows outlined - looked at
before any number is used."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from skimage.color import rgb2lab
from skimage.filters import frangi

#: windows by view: name -> (row0, row1, col0, col1) as fractions of the frame. The eye view's forehead strip and the
#: cheek view's centre are the proof log's (2026-11-05); the rest the central skin of their view
WINDOWS = {
    "eye": {"forehead": (0.02, 0.17, 0.30, 0.75)},  # above both brows (HD Aaron's sit lower in the frame)
    "cheek": {"cheek": (0.15, 0.48, 0.25, 0.58)},  # above the stubble (its lower edge caught hairs when moved)
    "face": {"face": (0.30, 0.70, 0.30, 0.70)},
    "torso": {"chest": (0.25, 0.55, 0.30, 0.70)},
    "hand": {"back of hand": (0.58, 0.80, 0.33, 0.58)},  # below the knuckles (the fingers point up the frame)
    "foot": {"top of foot": (0.30, 0.60, 0.35, 0.65)},
}
#: detail bands by real size on the skin (wavelength, mm): microrelief, pores, folds and fine lines, form (muscles,
#: tendons) - the plan's §9 scales
BANDS_MM = {"micro": (0.06, 0.3), "pore": (0.3, 1.5), "fold": (1.5, 7.0), "form": (7.0, 30.0)}
RIDGE_WIDTH_MM = (1.5, 8.0)
#: Frangi's contrast scale, fixed (scikit-image's default is half the image's own strongest Hessian, which scores pure
#: speckle like a crease and two images on different scales); on L* / 100: a 15 L* deep 2 mm crease reads ~0.026,
#: speckle of 3 L* 0 (measured 2026-11-07)
RIDGE_GAMMA = 1e-4
RIDGE_MIN_SIGMA_PX = 3.0
JITTER = 0.015  # ~1 mm on the face views: the anchors' own placement error, not a walk into other skin
SKIN_L = 12.0  # the stage's dark backdrop left out


def lab(rgb: np.ndarray) -> np.ndarray:
    """CIE L*a*b* of display sRGB values in 0-1."""
    return rgb2lab(np.clip(rgb, 0.0, 1.0))


def form_removed(lum: np.ndarray) -> np.ndarray:
    """The window less its form: a least-squares quadratic surface in x and y (ISO 25178-2's F-operator, done before
    a surface's power spectrum) - the face's curvature shading out, which otherwise swamps the bands and swings when
    the window moves."""
    h, w = lum.shape
    y, x = np.mgrid[0:h, 0:w]
    x, y = x / w - 0.5, y / h - 0.5
    basis = np.stack([np.ones_like(x), x, y, x * x, x * y, y * y], -1).reshape(-1, 6)
    coef, *_ = np.linalg.lstsq(basis, lum.ravel(), rcond=None)
    return lum - (basis @ coef).reshape(h, w)


def band_rms(lum: np.ndarray, mm_per_px: float) -> dict[str, float | None]:
    """The window's L* detail per band of real size: the radially averaged power spectrum of the window less its form
    (Hann-windowed, its energy restored), summed over each band's frequencies, as an RMS in L* units."""
    h, w = lum.shape
    x = form_removed(lum)
    hann = np.outer(np.hanning(h), np.hanning(w))
    power = np.abs(np.fft.fft2(x * hann)) ** 2 / (h * w) ** 2 / np.mean(hann**2)
    fy, fx = np.fft.fftfreq(h)[:, None], np.fft.fftfreq(w)[None, :]
    f = np.hypot(fy, fx)  # cycles per pixel
    with np.errstate(divide="ignore"):
        wavelength_mm = np.where(f > 0, mm_per_px / f, np.inf)
    out = {}
    window_mm = min(h, w) * mm_per_px
    for name, (lo, hi) in BANDS_MM.items():
        if lo < 2 * mm_per_px or window_mm < 2 * lo:  # finer than two pixels, or not twice inside the window
            out[name] = None
            continue
        sel = (wavelength_mm >= lo) & (wavelength_mm < hi)
        out[name] = round(float(np.sqrt(power[sel].sum())), 3)
    return out


def ridges(lum: np.ndarray, mm_per_px: float) -> dict[str, float | None]:
    """Mean Frangi vesselness at the mid scale, dark and light ridges apart (L* scaled to 0-1 first)."""
    lo, hi = (w / 2 / mm_per_px for w in RIDGE_WIDTH_MM)  # sigma ~ the half width, in pixels
    if lo < 1.0:
        return {"dark": None, "light": None}
    step = max(1, int(lo / RIDGE_MIN_SIGMA_PX))  # the filter needs only ~3 px at its finest scale: block-mean first
    if step > 1:
        h, w = (lum.shape[0] // step) * step, (lum.shape[1] // step) * step
        lum = lum[:h, :w].reshape(h // step, step, w // step, step).mean((1, 3))
        lo, hi = lo / step, hi / step
    sigmas = np.geomspace(lo, hi, 5)
    img = lum / 100.0
    gamma = RIDGE_GAMMA * step**2  # second derivatives in pixels grow by step^2 when the pixels do
    return {key: round(float(frangi(img, sigmas=sigmas, gamma=gamma, black_ridges=black).mean()), 5)
            for key, black in (("dark", True), ("light", False))}


def window_measures(rgb: np.ndarray, box: tuple[float, float, float, float], mm_per_px: float) -> dict:
    h, w = rgb.shape[:2]
    r0, r1, c0, c1 = int(box[0] * h), int(box[1] * h), int(box[2] * w), int(box[3] * w)
    cut = lab(rgb[r0:r1, c0:c1])
    lum = cut[..., 0]
    skin = lum > SKIN_L
    cover = float(skin.mean())
    if cover < 0.9:
        return {"cover": round(cover, 3)}  # backdrop or hair in the window: no numbers
    return {"cover": round(cover, 3),
            "lab": [round(float(cut[..., i][skin].mean()), 2) for i in range(3)],
            "bands": band_rms(lum, mm_per_px), "ridges": ridges(lum, mm_per_px)}  # fmt: skip


def _flat(m: dict, prefix: str = "") -> dict[str, float]:
    out = {}
    for k, v in m.items():
        if isinstance(v, dict):
            out.update(_flat(v, f"{prefix}{k}."))
        elif isinstance(v, list):
            out.update({f"{prefix}{k}.{i}": x for i, x in enumerate(v)})
        elif isinstance(v, (int, float)) and k != "cover":
            out[prefix + k] = v
    return out


def repeatability(rgb: np.ndarray, box, mm_per_px: float) -> dict[str, float]:
    """Each measure's spread with the window moved by JITTER of the frame (3 x 3 positions)."""
    runs = []
    for dr in (-JITTER, 0.0, JITTER):
        for dc in (-JITTER, 0.0, JITTER):
            moved = (box[0] + dr, box[1] + dr, box[2] + dc, box[3] + dc)
            if min(moved) < 0 or max(moved) > 1:
                continue
            m = window_measures(rgb, moved, mm_per_px)
            if "lab" in m:
                runs.append(_flat(m))
    if len(runs) < 2:
        return {}
    spread = {}
    for k in runs[0]:
        vals = np.array([r[k] for r in runs if r.get(k) is not None], float)
        if len(vals) == len(runs) and abs(vals.mean()) > 1e-9:
            spread[k] = round(float((vals.max() - vals.min()) / abs(vals.mean())), 3)
    return spread


def read(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), np.float64) / 255.0


def outline(path: Path, boxes: dict, out: Path) -> None:
    img = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    for name, (r0, r1, c0, c1) in boxes.items():
        draw.rectangle([c0 * w, r0 * h, c1 * w, r1 * h], outline=(255, 0, 255), width=max(2, w // 400))
        draw.text((c0 * w + 6, r0 * h + 6), name, fill=(255, 0, 255))
    img.save(out)


def measure_dir(out_dir: Path, engine: str) -> dict:
    report = {}
    frames_path = out_dir / "frames.json"  # written by parts_gate.py render: each render's frame width
    frames = json.loads(frames_path.read_text()) if frames_path.exists() else {}
    pattern = re.compile(rf"^{engine}_(?P<view>.+?)_(?P<who>(?:ours|cc5)(?:_f-\w+)?)\.png$")  # factors.py's tags
    for path in sorted(out_dir.glob(f"{engine}_*.png")):
        m = pattern.match(path.name)
        if not m or m["view"] not in WINDOWS:
            continue
        view, who = m["view"], m["who"]
        frame = frames.get(path.stem)
        if frame is None:
            print("no frame width for", path.name, "- rendered before frames.json; skipped")
            continue
        rgb = read(path)
        mm_per_px = frame["width_m"] * 1000.0 / rgb.shape[1]
        outline(path, WINDOWS[view], out_dir / f"windows_{engine}_{view}_{who}.png")
        for name, box in WINDOWS[view].items():
            entry = window_measures(rgb, box, mm_per_px)
            entry["repeatability"] = repeatability(rgb, box, mm_per_px)
            entry["mm_per_px"] = round(mm_per_px, 4)
            report.setdefault(f"{engine}_{view}", {}).setdefault(name, {})[who] = entry
    return report


def main() -> None:
    p = argparse.ArgumentParser(prog="measure.py")
    p.add_argument("out_dir", type=Path)
    p.add_argument("--engine", choices=("eevee", "cycles"), default="eevee")
    args = p.parse_args()
    report = measure_dir(args.out_dir, args.engine)
    (args.out_dir / f"measures_{args.engine}.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
