# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test: where each aligned painting shows the eyes themselves - so that their white and iris never colour our
lids' skin. Round 79-80's close-ups: a pale band on the lower lid's outer half; the aligned paintings' lower lid lines
sit 4-11 px below ours there (the face view's outer corner +5, faceright30's whole lid +4..+11, MediaPipe's lid
points), so the strip between took the painting's eye white. Photogrammetry and Headshot keep the eyes out of the skin
texture by a face-parsing mask; ours is SegFace, the parser the scan route already runs (scan_skin.py: AAAI 2025, code
and weights MIT, trained on CelebAMask-HQ - non-commercial data, a label), on the aligned painting - the picture the
projection reads, in its camera.

Writes eyes_<view>.png: 255 where the parser calls a pixel an eye (l_eye or r_eye), grown by EYE_GROW px - a pixel on
the lid line is part white. Run (the RealDenseFace environment; processor): .dev/venv-rdf/Scripts/python -I
tools/face_test/parse_paintings.py [VIEW ...]
"""

import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np
import torch

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest")
VIEWS = ("face", "faceleft30", "faceright30")  # the colour views (test_face_project.py COLOUR_VIEWS with a base)
EYE_GROW = 3  # px at 1024: the lid line's own mixed pixels


def _scan_skin():
    spec = importlib.util.spec_from_file_location("scan_skin", str(Path(__file__).with_name("scan_skin.py")))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(views):
    torch.set_num_threads(2)  # the machine is shared
    scan_skin = _scan_skin()
    model = scan_skin.load_segface()
    eyes = [scan_skin.CLASSES.index(c) for c in ("l_eye", "r_eye")]
    for view in views:
        path = DIR / f"aligned_{view}.png"
        if not path.exists():
            print(f"{view}: no aligned painting")
            continue
        rgb = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)
        labels = scan_skin.parse(model, rgb).argmax(-1)
        mask = np.isin(labels, eyes).astype(np.uint8) * 255
        grow = 2 * EYE_GROW + 1
        mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (grow, grow)))
        cv2.imwrite(str(DIR / f"eyes_{view}.png"), mask)
        print(f"{view}: eyes {(mask > 0).mean():.2%} of the picture", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or VIEWS)
