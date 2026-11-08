# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The smile at the gate in numbers, ours against HD Aaron's (the smile proof; plan §7 "Expression shapes"): each
face's points found by MediaPipe's Face Landmarker (`tools/face_test/landmarks.py`, Apache-2.0) in the neutral face
view and in a smile view. The gate frames `face`, `face_smile` and `face_smile_full` with one camera from the neutral
face's anatomy, 0.30 m wide (parts_gate.view), so a point's move between them is millimetres on the face's plane:
the mouth's corners up and out, the cheeks up, the lower lids up, the eye's opening. Beside them are the Landmarker's
own ARKit scores (how much of a smile, a cheek squint, an eye squint a trained model reads in each picture).

    .dev/venv-tools/Scripts/python -I tools/gate/smile_measure.py DIR [--view face_smile] [--ours-tag _f-...]
        [--overlay]   (--overlay also draws the points used on each picture, to check them by eye)
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import numpy as np

FRAME_M = 0.30  # parts_gate.view: the face views' frame width
#: MediaPipe's face mesh points (the subject's right side first): the mouth's corners, cheeks, lower and upper lids'
#: middles, the lips' middles - checked on the pictures with --overlay
POINTS = {"corner": (61, 291), "cheek": (50, 280), "lower_lid": (145, 374), "upper_lid": (159, 386), "upper_lip": (0,),
          "lower_lip": (17,)}  # fmt: skip
SCORES = ("mouthSmileLeft", "mouthSmileRight", "cheekSquintLeft", "cheekSquintRight", "eyeSquintLeft",
          "eyeSquintRight", "jawOpen", "mouthStretchLeft", "mouthStretchRight")  # fmt: skip


def moves(neutral: np.ndarray, smile: np.ndarray, mm_per_px: float) -> dict[str, float]:
    """Each measure in mm (up and out positive) from two pictures' points (478 x 2, pixels, y down)."""
    d = (smile - neutral) * mm_per_px
    mid = neutral[[33, 133, 362, 263], 0].mean()  # the eyes' corners' middle: the face's midline

    def up(name: str) -> float:
        return float(-d[list(POINTS[name]), 1].mean())

    out = {"corner up": up("corner"), "cheek up": up("cheek"), "lower lid up": up("lower_lid"),
           "upper lip up": up("upper_lip"), "lower lip up": up("lower_lip")}  # fmt: skip
    side = np.sign(neutral[list(POINTS["corner"]), 0] - mid)
    out["corner out"] = float((d[list(POINTS["corner"]), 0] * side).mean())
    lo, hi = list(POINTS["lower_lid"]), list(POINTS["upper_lid"])
    out["eye opening"] = float(((smile[lo, 1] - smile[hi, 1]) - (neutral[lo, 1] - neutral[hi, 1])).mean() * mm_per_px)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("dir", type=Path)
    p.add_argument("--view", default="face_smile")
    p.add_argument("--engine", default="eevee")
    p.add_argument("--ours-tag", default="", help="the smile picture's tag on ours (a factor's, e.g. _f-ictsmilex...)")
    p.add_argument("--overlay", action="store_true")
    a = p.parse_args()
    spec = importlib.util.spec_from_file_location("landmarks", Path(__file__).resolve().parents[1] / "face_test" / "landmarks.py")
    lm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lm)
    import cv2
    from mediapipe.tasks import python as mp_tasks
    from mediapipe.tasks.python import vision

    options = vision.FaceLandmarkerOptions(base_options=mp_tasks.BaseOptions(model_asset_path=str(lm.MODEL)),
                                           num_faces=1, output_face_blendshapes=True)  # fmt: skip
    rows = {}
    with vision.FaceLandmarker.create_from_options(options) as detector:
        for who, tag in (("cc5", ""), ("ours", a.ours_tag)):
            n_path = a.dir / f"{a.engine}_face_{who}.png"
            s_path = a.dir / f"{a.engine}_{a.view}_{who}{tag}.png"
            (n_pts, n_sc), (s_pts, s_sc) = lm.detect(detector, n_path), lm.detect(detector, s_path)
            if n_pts is None or s_pts is None:
                print(f"{who}: no face found in {n_path.name if n_pts is None else s_path.name}")
                continue
            width = cv2.imread(str(s_path)).shape[1]
            m = moves(np.array(n_pts), np.array(s_pts), FRAME_M * 1000 / width)
            rows[who] = (m, s_sc, n_sc)
            if a.overlay:
                for path, pts in ((n_path, n_pts), (s_path, s_pts)):
                    img = cv2.imread(str(path))
                    for k in sum(POINTS.values(), ()):
                        cv2.circle(img, tuple(int(round(c)) for c in pts[k]), 6, (0, 255, 255), 2)
                    cv2.imwrite(str(path.with_name(path.stem + "_points.png")), img)
    if len(rows) < 2:
        return 1
    print(f"{a.view} against neutral, mm on the face's plane (HD Aaron | ours{a.ours_tag} | ours / his)")
    for key in rows["cc5"][0]:
        his, ours = rows["cc5"][0][key], rows["ours"][0][key]
        print(f"  {key:14s} {his:7.2f} | {ours:7.2f} | {ours / his if abs(his) > 0.2 else float('nan'):5.2f}")
    print("the Landmarker's ARKit scores in the smile picture (his | ours; neutral his | ours)")
    for key in SCORES:
        print(f"  {key:18s} {rows['cc5'][1].get(key, 0):.2f} | {rows['ours'][1].get(key, 0):.2f}"
              f"   ({rows['cc5'][2].get(key, 0):.2f} | {rows['ours'][2].get(key, 0):.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
