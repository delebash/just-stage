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

import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest")
MODEL = Path("E:/Dev/3D/just-stage/.dev/cache/mediapipe/face_landmarker.task")
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below", "face", "faceleft30", "faceright30")


def points(detector, path: Path, size: int = 1024):
    result = detector.detect(mp.Image.create_from_file(str(path)))
    if not result.face_landmarks:
        return None
    return [[p.x * size - 0.5, p.y * size - 0.5] for p in result.face_landmarks[0]]


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
