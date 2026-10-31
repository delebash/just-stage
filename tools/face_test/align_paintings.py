# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, between stages 2 and 3: each painted view warped so its face sits exactly on the clay view's — the AI
moves the face a little as it paints (its eyes lower, its mouth shifted), which projected back gives doubled eyes.

Anchored only on what is real on the clay: MediaPipe's Face Landmarker (Apache-2.0) is reliable on the paintings,
but on a clay render - no brows, no colour - it guesses: between two clays that differ by a degree or two of lid its
brows moved 9-11 px, its nose 5.5 px (the nose unchanged), its eye rings 6 px and its lid contour read a near-shut eye
as matching the painting; only its lips held (1.3 px; round 51, 2026-10-31). So the painting's lid lines (its eye
rings) go onto the clay's eye openings - segmented from the clay's colours, each lid point moved straight up or down
onto the opening's edge - and the painting's outer lips onto the clay's; a thin-plate-spline warp (SciPy's
RBFInterpolator) carries them, the picture's border pinned, everything between interpolated (the flow step,
flow_views.py, refines between the views). Views where a face or an eye isn't found keep what they can.

Run (the tool environment, .dev/venv-tools): .dev/venv-tools/Scripts/python tools/face_test/align_paintings.py
"""

import sys
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision
from scipy.interpolate import RBFInterpolator

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest")
MODEL = Path("E:/Dev/3D/just-stage/.dev/cache/mediapipe/face_landmarker.task")
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below", "face", "faceleft30", "faceright30")
GRID = 64  # the warp is solved on a coarse grid and smoothly scaled up to the full picture
#: MediaPipe's inner lip ring, left out of the warp: the head's lips are closed (face_shape.py), so there is no inner
#: edge to find on the clay - the detector guesses one at the crease, and the warp pulled the painting's lips apart
INNER_LIPS = (78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191)
#: MediaPipe's outer lip ring (its published lips set without the inner ring)
OUTER_LIPS = tuple(sorted({p for c in vision.FaceLandmarksConnections.FACE_LANDMARKS_LIPS for p in (c.start, c.end)}
                          - set(INNER_LIPS)))
#: MediaPipe's eye rings, outer corner to inner corner: upper lid, lower lid (its published eye sets, ordered)
EYE_RINGS = (((33, 246, 161, 160, 159, 158, 157, 173, 133), (33, 7, 163, 144, 145, 153, 154, 155, 133)),
             ((263, 466, 388, 387, 386, 385, 384, 398, 362), (263, 249, 390, 373, 374, 380, 381, 382, 362)))
SKIN_DISTANCE = 45  # colour distance from the clay's skin (8-bit RGB) that counts as eye


def landmarks(detector, path: Path) -> np.ndarray | None:
    result = detector.detect(mp.Image.create_from_file(str(path)))
    if not result.face_landmarks:
        return None
    h, w = cv2.imread(str(path)).shape[:2]
    return np.array([(p.x * w, p.y * h) for p in result.face_landmarks[0]])


def clay_eye_points(clay: np.ndarray, painted_pts: np.ndarray):
    """For each of the painting's lid points (its eye rings without the corners), the clay's: straight up or down at
    the same column, on the top (upper lid) or bottom edge of the clay's eye opening - its pixels not skin-coloured,
    the region nearest the painted eye. Only vertical, and no corners: MediaPipe's corners sit at the canthi, past
    the inner corner's pink tissue, while the clay's opening ends where the eyeball stops showing - matched, they
    squashed the painted eye sideways (round 51). Returns (painting points, clay points) for the eyes found."""
    h, w = clay.shape[:2]
    skin = np.median(clay[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4].reshape(-1, 3).astype(float), axis=0)
    eye_px = (np.linalg.norm(clay.astype(float) - skin, axis=2) > SKIN_DISTANCE).astype(np.uint8)
    _count, labels = cv2.connectedComponents(eye_px)
    ys, xs = np.nonzero(labels > 0)
    src, dst = [], []
    for upper, lower in EYE_RINGS:
        cx, cy = painted_pts[list(upper) + list(lower)].mean(axis=0)
        if not len(xs):
            continue
        near = np.argmin((xs - cx) ** 2 + (ys - cy) ** 2)
        if (xs[near] - cx) ** 2 + (ys[near] - cy) ** 2 > 40**2:  # no opening near the painted eye: hidden from here
            continue
        region = labels == labels[ys[near], xs[near]]
        if region.sum() > 0.02 * h * w:  # not an eye: the background or the face's outline
            continue
        for ids, top in ((upper, True), (lower, False)):
            for i in ids[1:-1]:
                x = int(round(painted_pts[i, 0]))
                rows = np.flatnonzero(region[:, x]) if 0 <= x < w else []
                if len(rows):
                    src.append([painted_pts[i, 0], rows.min() if top else rows.max()])
                    dst.append(painted_pts[i])
    return np.array(dst).reshape(-1, 2), np.array(src).reshape(-1, 2)


def warp(painted: np.ndarray, clay_pts: np.ndarray, painted_pts: np.ndarray) -> np.ndarray:
    """The painting resampled so its points land on the clay's: each output pixel looks up where it was painted."""
    h, w = painted.shape[:2]
    edge = np.linspace(0, 1, 9)[:-1]
    border = np.concatenate(
        [
            np.c_[edge * w, np.zeros(8)],
            np.c_[np.full(8, w), edge * h],
            np.c_[w - edge * w, np.full(8, h)],
            np.c_[np.zeros(8), h - edge * h],
        ]
    )
    src = np.vstack([clay_pts, border])
    dst = np.vstack([painted_pts, border])
    rbf = RBFInterpolator(src, dst, kernel="thin_plate_spline", smoothing=0.3)  # tight: the lips need it
    gy, gx = np.mgrid[0 : h : complex(GRID), 0 : w : complex(GRID)]
    coarse = rbf(np.c_[gx.ravel(), gy.ravel()]).reshape(GRID, GRID, 2).astype(np.float32)
    full = cv2.resize(coarse, (w, h), interpolation=cv2.INTER_CUBIC)
    return cv2.remap(painted, full[..., 0], full[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def main() -> int:
    options = vision.FaceLandmarkerOptions(base_options=mp_tasks.BaseOptions(model_asset_path=str(MODEL)), num_faces=1)
    with vision.FaceLandmarker.create_from_options(options) as detector:
        for view in VIEWS:
            clay_path, painted_path = DIR / f"clay_{view}.png", DIR / f"painted_{view}.png"
            out = DIR / f"aligned_{view}.png"
            clay_pts, painted_pts = landmarks(detector, clay_path), landmarks(detector, painted_path)
            if clay_pts is None or painted_pts is None:
                out.unlink(missing_ok=True)
                print(f"{view}: face not found in {'the clay view' if clay_pts is None else 'the painting'} — kept")
                continue
            painted_eyes, clay_eyes = clay_eye_points(cv2.imread(str(clay_path)), painted_pts)
            lips = list(OUTER_LIPS)
            src = np.vstack([clay_eyes, clay_pts[lips]])
            dst = np.vstack([painted_eyes, painted_pts[lips]])
            moved = np.linalg.norm(src - dst, axis=1)
            cv2.imwrite(str(out), warp(cv2.imread(str(painted_path)), src, dst))
            print(
                f"{view}: the AI moved the lids {moved[: len(clay_eyes)].mean():.1f} px on average "
                f"(worst {moved[: len(clay_eyes)].max():.0f}, {len(clay_eyes)} points), the lips "
                f"{moved[len(clay_eyes):].mean():.1f} px - warped onto the clay's"
                if len(clay_eyes) else f"{view}: no eye opening found; the lips moved {moved.mean():.1f} px - warped"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
