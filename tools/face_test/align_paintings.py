# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, between stages 2 and 3: each painted view warped so its face sits exactly on the clay view's — the AI
moves the face a little as it paints (its eyes lower, its mouth shifted), which projected back gives doubled eyes.

MediaPipe's Face Landmarker (Apache-2.0) finds the same 478 face points in the clay view and in the painting; a
thin-plate-spline warp (SciPy's RBFInterpolator) carries the painting's points onto the clay's, the picture's border
pinned so the warp stays on the face. Views where either face isn't found keep their painting.

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


def landmarks(detector, path: Path) -> np.ndarray | None:
    result = detector.detect(mp.Image.create_from_file(str(path)))
    if not result.face_landmarks:
        return None
    h, w = cv2.imread(str(path)).shape[:2]
    return np.array([(p.x * w, p.y * h) for p in result.face_landmarks[0]])


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
            before = np.linalg.norm(clay_pts - painted_pts, axis=1)
            aligned = warp(cv2.imread(str(painted_path)), clay_pts, painted_pts)
            cv2.imwrite(str(out), aligned)
            again = landmarks(detector, out)
            after = np.linalg.norm(clay_pts - again, axis=1) if again is not None else np.array([np.nan])
            print(
                f"{view}: the AI moved the face {before.mean():.1f} px on average (worst {before.max():.0f}); "
                f"after the warp {np.nanmean(after):.1f} px"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
