# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material, step 3: MediaPipe's Face Landmarker (Apache-2.0) only for what it does
reliably - finding a face: which of a scan's 12 turns (scan_views.py) shows it most squarely (the nose tip centred
between the outer eye corners), and the face box RealDenseFace crops by (flame_fit.py's way: the points' box). Its
fine points are not used as pairs (on clay its brows moved 9-11 px between near-identical renders, TASKS 2026-10-31);
RealDenseFace's dense points are (scan_pairs.py). `ours` does the same for our head's side: round N's renders.

Run (the tool environment): .dev/venv-tools/Scripts/python -I tools/face_test/scan_marks.py NAME | ours
"""

import json
import re
import sys
from pathlib import Path

import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

FACETEST = Path("E:/Dev/3D/just-stage/.dev/facetest")
SCANS = FACETEST / "scans"
MODEL = Path("E:/Dev/3D/just-stage/.dev/cache/mediapipe/face_landmarker.task")
OURS_VIEWS = ("face", "front")  # our head's front views: the close one carries the most pixels per millimetre
NOSE_TIP, EYE_OUT_R, EYE_OUT_L = 1, 33, 263


def detect(detector, path: Path):
    """MediaPipe's 478 points in pixels (pixel centres at whole numbers), or None."""
    image = mp.Image.create_from_file(str(path))
    result = detector.detect(image)
    if not result.face_landmarks:
        return None
    w, h = image.width, image.height
    return [[p.x * w - 0.5, p.y * h - 0.5] for p in result.face_landmarks[0]]


def squareness(pts):
    """How far the nose tip sits off the middle of the outer eye corners, as a share of the eyes' span (0 = square)."""
    (xr, _), (xl, _), (xn, _) = pts[EYE_OUT_R], pts[EYE_OUT_L], pts[NOSE_TIP]
    return abs(xn - (xr + xl) / 2) / max(abs(xl - xr), 1e-6)


def main(argv):
    options = vision.FaceLandmarkerOptions(base_options=mp_tasks.BaseOptions(model_asset_path=str(MODEL)), num_faces=1)
    with vision.FaceLandmarker.create_from_options(options) as detector:
        if argv[0] == "ours":
            rounds = [int(m.group(1)) for p in FACETEST.glob("round*_face.png") if (m := re.match(r"round(\d+)_", p.name))]
            n = max(rounds)
            found = {}
            for view in OURS_VIEWS:
                path = FACETEST / f"round{n}_{view}.png"
                pts = detect(detector, path)
                if pts is None:
                    raise SystemExit(f"no face found in {path}")
                found[view] = {"image": str(path), "points": pts, "squareness": squareness(pts)}
                print(f"ours {view} (round {n}): squareness {squareness(pts):.3f}")
            (SCANS / "ours_marks.json").write_text(json.dumps({"round": n, "views": found}))
            return 0
        out = SCANS / argv[0]
        if len(argv) > 1 and argv[1] == "face":  # the zoomed square-on render (scan_views.py NAME face)
            marks = json.loads((out / "marks.json").read_text())
            pts = detect(detector, out / "view_face.png")
            if pts is None:
                raise SystemExit(f"{argv[0]}: no face in view_face.png")
            marks["face"] = {"points": pts, "squareness": squareness(pts)}
            (out / "marks.json").write_text(json.dumps(marks))
            print(f"{argv[0]} view_face: squareness {squareness(pts):.3f}")
            return 0
        views = {}
        for path in sorted(out.glob("view_turn*.png")):
            pts = detect(detector, path)
            views[path.stem] = None if pts is None else {"points": pts, "squareness": squareness(pts)}
            print(f"{argv[0]} {path.stem}: " + ("no face" if pts is None else f"squareness {squareness(pts):.3f}"))
        best = min((v for v in views if views[v]), key=lambda v: views[v]["squareness"], default=None)
        if best is None:
            raise SystemExit(f"{argv[0]}: no face in any turn")
        (out / "marks.json").write_text(json.dumps({"best": best, "views": views}))
        print(f"{argv[0]}: best {best}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
