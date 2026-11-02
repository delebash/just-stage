# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material, step 1b: a scan stood upright, facing our way (Z up, face to -Y). Some
scans arrive lying down or tilted (rudavin flat, female_wnmb ~60 degrees, 2026-11-02), and the views turn about the
vertical only. MediaPipe's Face Landmarker looks at the scan from 26 directions (scan_views.py NAME sphere), each picture
also turned a quarter, half and three quarters (the roll is unknown); the picture with an upright, square-on face wins;
its points in 3D (the position picture) give the head's axes - eye corner to eye corner its left-right, chin to the top of
the forehead its up - and the scan is turned to match ours. An upright scan comes out unchanged (the turn ~identity).

Rewrites scans/NAME/src.npz (vertices turned) and writes orient.json (the turn, which picture). Run (the tool
environment): .dev/venv-tools/Scripts/python -I tools/face_test/scan_orient.py NAME
"""

import json
import sys
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

SCANS = Path("E:/Dev/3D/just-stage/.dev/facetest/scans")
MODEL = Path("E:/Dev/3D/just-stage/.dev/cache/mediapipe/face_landmarker.task")
RIGHT_EYE, LEFT_EYE = (33, 133), (263, 362)  # the subject's right / left eye corners (outer, inner)
FOREHEAD, CHIN, NOSE_TIP = 10, 152, 1
UPRIGHT = 25.0  # degrees: the eye line's tilt allowed in an "upright" picture


def detect(detector, rgb):
    result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    if not result.face_landmarks:
        return None
    h, w = rgb.shape[:2]
    return np.array([[p.x * w - 0.5, p.y * h - 0.5] for p in result.face_landmarks[0]])


def unturn(pts, k, size):
    """Points found in np.rot90(picture, k) back in the picture's own pixels."""
    x, y = pts[:, 0], pts[:, 1]
    s = size - 1
    if k == 0:
        return pts
    if k == 1:
        return np.c_[s - y, x]
    if k == 2:
        return np.c_[s - x, s - y]
    return np.c_[y, s - x]


def main(name):
    out = SCANS / name
    views = json.loads((out / "views.json").read_text())["cams"]
    options = vision.FaceLandmarkerOptions(base_options=mp_tasks.BaseOptions(model_asset_path=str(MODEL)), num_faces=1)
    best = None
    with vision.FaceLandmarker.create_from_options(options) as detector:
        for label in sorted(v for v in views if v.startswith("sphere")):
            rgba = cv2.imread(str(out / f"view_{label}.png"), cv2.IMREAD_UNCHANGED)[..., [2, 1, 0, 3]].astype(np.float32)
            a = rgba[..., 3:] / 255.0
            rgb = (rgba[..., :3] * a + 128.0 * (1 - a)).astype(np.uint8)
            for k in range(4):
                pts = detect(detector, np.rot90(rgb, k))
                if pts is None:
                    continue
                r, l = pts[list(RIGHT_EYE)].mean(0), pts[list(LEFT_EYE)].mean(0)
                tilt = np.degrees(np.arctan2(l[1] - r[1], l[0] - r[0]))
                span = float(np.linalg.norm(l - r))
                upright = abs(tilt) < UPRIGHT and pts[FOREHEAD, 1] < pts[CHIN, 1] and span > 20
                square = abs(pts[NOSE_TIP, 0] - (r[0] + l[0]) / 2) / max(span, 1e-6)
                if upright and (best is None or square < best[0]):
                    best = (square, label, k, unturn(pts, k, rgb.shape[0]))
    if best is None:
        raise SystemExit(f"{name}: no upright face in any of the 26 directions")
    square, label, k, pts = best
    pos = np.load(out / f"pos_{label}.npy")

    def at(ids):
        c = np.clip(np.round(pts[list(ids)]).astype(int), 0, pos.shape[0] - 1)
        p = pos[c[:, 1], c[:, 0]]
        if (p[:, 3] < 0.5).any():
            raise SystemExit(f"{name}: a face point fell off the scan in {label}")
        return p[:, :3].mean(0)

    x = at(LEFT_EYE) - at(RIGHT_EYE)  # the subject's left: our +X
    x /= np.linalg.norm(x)
    z = at([FOREHEAD]) - at([CHIN])
    z -= x * (z @ x)
    z /= np.linalg.norm(z)
    y = np.cross(z, x)  # the back of the head: our +Y (the face looks to -Y)
    R = np.stack([x, y, z])
    src = dict(np.load(out / "src.npz"))
    # MediaPipe can lay an upright face over an upside-down one (rudavin's half-turned picture, 2026-11-02): chin and
    # forehead swap, and left and right with them - the head comes out turned half round the line of sight. A head
    # always reaches farther below its eyes (chin, neck, shoulders) than above them (the crown): if not, turn it back
    eyes = (at(LEFT_EYE) + at(RIGHT_EYE)) / 2 @ R.T
    zs = src["co"].astype(np.float64) @ R[2]
    flipped = zs.max() - eyes[2] > eyes[2] - zs.min()
    if flipped:
        R = np.diag([-1.0, 1.0, -1.0]) @ R
    src = dict(np.load(out / "src.npz"))
    src["co"] = (src["co"].astype(np.float64) @ R.T).astype(np.float32)
    np.savez(out / "src.npz", **src)
    prev = out / "orient.json"
    total = R @ np.asarray(json.loads(prev.read_text())["total"]) if prev.exists() else R
    angle = float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1.0, 1.0))))
    prev.write_text(json.dumps({"turn": R.tolist(), "total": total.tolist(), "picture": label, "roll_quarters": k,
                                "squareness": square, "angle_deg": angle, "flipped_back": bool(flipped)}))
    print(f"{name}: upright from {label} (roll {k * 90} deg, squareness {square:.3f}{', turned back half round' if flipped else ''}); "
          f"turned {angle:.1f} deg")


if __name__ == "__main__":
    main(sys.argv[1])
