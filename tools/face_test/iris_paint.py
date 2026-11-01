# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the iris: a photographic iris for the eye's texture - the research's option from an image model
(`../plans/2026-10-30-research-hair-eyes-teeth.md` §5c, 3: "a flat, centred macro iris ... then unwrap"; MPFB2's
procedural iris read as noise beside the painting's: round 54's close-up). FLUX 3 Image Klein paints a head-on macro
iris (no reference); the pupil is found as the darkest blob near the middle, the iris' rim as the strongest rise in
brightness outward from it; catch-lights are taken out ring by ring; the picture is cropped so the iris' radius is
IRIS_RADIUS of its width (test_face_project.IRIS_TEXTURE_RADIUS) and its brightness scaled to the painting's iris
(linear light, 0.4-0.85 of the radius, its lower half - the upper lies under the lid in the painting); its hue kept
(per channel it went grey-lilac: the painting's iris colour carries its cornea's sheen, which the render adds itself -
the render's own calibration then matches the colour, cornea and all).

Run (the tool environment): .dev/venv-rdf/Scripts/python -I tools/face_test/iris_paint.py SEED [SEED ...]
Writes iris_seed{N}.png (the raw paintings), iris_texture_seed{N}.png (each prepared) and iris_texture.png (the first).
"""

import importlib.util
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("face_paint_cli", str(HERE / "face_paint_cli.py"))
painter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(painter)
DIR = painter.DIR
IRIS_RADIUS = 0.40
SIZE = 1024
LUMA = np.array([0.2126, 0.7152, 0.0722])
PROMPT = (
    "Extreme close-up macro photograph of a human iris, dark brown, seen exactly head-on, perfectly circular and "
    "centred in the frame, the iris filling most of the frame, a round black pupil in its centre, fine radial fibres "
    "and crypts, a darker ring at its outer edge, white of the eye around it. No eyelids, no eyelashes, no "
    "reflections, no highlights, soft even light. Sharp focus, high detail."
)


def linear(bgr):
    c = bgr[..., ::-1].astype(np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb_bgr(rgb):
    c = np.clip(rgb, 0.0, 1.0)
    c = np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)
    return (c[..., ::-1] * 255.0).round().astype(np.uint8)


def find_iris(img):
    """The pupil's centre (the largest dark blob near the middle - the darkest pixels, closed into one: alone they
    split a large pupil into specks, seeds 1-2's first run) and the iris' radius (the strongest rise in the brightness
    profile outward from it, past twice the pupil's radius)."""
    h, w = img.shape[:2]
    lum = cv2.GaussianBlur(img @ LUMA, (0, 0), 3.0)
    dark = (lum < np.percentile(lum, 3)).astype(np.uint8)
    dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    n, labels, stats, cents = cv2.connectedComponentsWithStats(dark)
    near = [i for i in range(1, n) if np.hypot(*(cents[i] - (w / 2, h / 2))) < 0.3 * w]
    k = max(near, key=lambda i: stats[i, cv2.CC_STAT_AREA])
    cx, cy = cents[k]
    pupil = np.sqrt(stats[k, cv2.CC_STAT_AREA] / np.pi)
    yy, xx = np.mgrid[0:h, 0:w]
    rr = np.hypot(xx - cx, yy - cy)
    radii = np.arange(int(2 * pupil), int(min(cx, cy, w - cx, h - cy)) - 2)
    prof = np.array([np.median(lum[(rr >= r) & (rr < r + 1)]) for r in radii])
    rise = np.convolve(np.diff(prof), np.ones(5) / 5, mode="same")
    return cx, cy, pupil, float(radii[int(np.argmax(rise))])


def without_highlights(img, cx, cy, radius):
    """Each ring (1 px wide) inside the iris: pixels brighter than 1.6x its median take the median."""
    out = img.copy()
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    ring = np.hypot(xx - cx, yy - cy).astype(int)
    lum = img @ LUMA
    for r in range(int(radius) + 1):
        m = ring == r
        if m.sum() < 8:
            continue
        med = np.median(img[m], axis=0)
        hot = m & (lum > 1.6 * (med @ LUMA))
        out[hot] = med
    return out


def painting_iris():
    """The painting's iris in the face view (MediaPipe's points, landmarks.json): linear colour at 0.4-0.85 of its
    radius in its lower half, both eyes."""
    img = linear(cv2.imread(str(DIR / "painted_face.png")))
    marks = json.load(open(DIR / "landmarks.json"))["face"]["painted"]
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    picked = []
    for c, ring in ((468, range(469, 473)), (473, range(474, 478))):
        cx, cy = marks[c]
        r = float(np.mean([np.hypot(marks[i][0] - cx, marks[i][1] - cy) for i in ring]))
        rr = np.hypot(xx - cx, yy - cy) / r
        picked.append(img[(rr > 0.4) & (rr < 0.85) & (yy > cy)])
    return np.concatenate(picked).mean(axis=0)


def prepare(raw_path, target):
    img = linear(cv2.imread(str(raw_path)))
    cx, cy, pupil, radius = find_iris(img)
    img = without_highlights(img, cx, cy, radius)
    half = radius / (2 * IRIS_RADIUS)
    m = np.float32([[SIZE / (2 * half), 0, SIZE / 2 - cx * SIZE / (2 * half)],
                    [0, SIZE / (2 * half), SIZE / 2 - cy * SIZE / (2 * half)]])
    tex = cv2.warpAffine(img, m, (SIZE, SIZE), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    rr = np.hypot(xx - SIZE / 2 + 0.5, yy - SIZE / 2 + 0.5) / (IRIS_RADIUS * SIZE)
    band = tex[(rr > 0.4) & (rr < 0.85)].mean(axis=0)
    tex *= (target @ LUMA) / (band @ LUMA)  # brightness only (see above)
    return tex, (cx, cy, pupil, radius, band)


def main(argv) -> int:
    target = painting_iris()
    print(f"the painting's iris (linear, 0.4-0.85 r, lower half): {np.round(target, 3).tolist()}")
    for n, seed in enumerate(int(a) for a in argv):
        raw = DIR / f"iris_seed{seed}.png"
        if not raw.exists():
            painter.paint([], PROMPT, seed, raw)
        tex, (cx, cy, pupil, radius, band) = prepare(raw, target)
        out = srgb_bgr(tex)
        cv2.imwrite(str(DIR / f"iris_texture_seed{seed}.png"), out)
        if n == 0:
            cv2.imwrite(str(DIR / "iris_texture.png"), out)
        print(f"seed {seed}: pupil at ({cx:.0f}, {cy:.0f}) r {pupil:.0f} px, iris r {radius:.0f} px "
              f"(pupil {pupil / radius:.2f} of it); its band {np.round(band, 3).tolist()} -> the painting's brightness")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
