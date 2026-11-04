# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the shape fit's first half: the same 478 face points (MediaPipe's Face Landmarker, Apache-2.0) found in
every clay view and every painting, saved as pixel coordinates (pixel centres at whole numbers, as
core/uv_projection.py counts them) to landmarks.json for test_face_fit.py.

Run (the tool environment): .dev/venv-tools/Scripts/python tools/face_test/landmarks.py
"""

import json
import sys
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest")
MODEL = Path("E:/Dev/3D/just-stage/.dev/cache/mediapipe/face_landmarker.task")
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below", "face", "faceleft30", "faceright30")


def points(detector, path: Path):
    """MediaPipe's 478 points in the picture's own pixels; None if there's no picture (a view a character's face test
    doesn't paint) or no face in it."""
    if not path.exists():
        return None
    img = cv2.imread(str(path))
    h, w = img.shape[:2]
    for pad in (0, w // 8):  # again with a margin when no face is found (align_paintings.landmarks: the close view)
        x = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_REPLICATE) if pad else img
        result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(x[..., ::-1])))
        if result.face_landmarks:
            return [[p.x * (w + 2 * pad) - pad - 0.5, p.y * (h + 2 * pad) - pad - 0.5] for p in result.face_landmarks[0]]
    return None


def main() -> int:
    options = vision.FaceLandmarkerOptions(base_options=mp_tasks.BaseOptions(model_asset_path=str(MODEL)), num_faces=1)
    found = {}
    with vision.FaceLandmarker.create_from_options(options) as detector:
        for view in VIEWS:
            clay, painted = points(detector, DIR / f"clay_{view}.png"), points(detector, DIR / f"painted_{view}.png")
            if clay and painted:
                found[view] = {"clay": clay, "painted": painted}
            print(f"{view}: {'both found' if clay and painted else 'skipped'}")
    (DIR / "landmarks.json").write_text(json.dumps(found), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
