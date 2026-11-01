# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, stage 2 in sequence - one person across the views (rec 1's second half, my call under the user's go on
2026-10-30: "one face across views from painting each next view on a render of the paint already projected"; the
research's "sequential context": TEXTure, StableGen's "Generate Sequentially"). Painted one at a time from each
view's clay, FLUX 3 invented a different man in each (round 53: the front a narrow light-skinned face, the close view
an East Asian man with eye bags, the 40-degree view a third), and the projection blended them.

The close "face" painting is the hero (the test's photo). For each next view, in order of overlap:
1. what is painted so far, re-projected into its camera through our mesh (each aligned painting by its depth picture,
   flow_views.View; blended by facing), the clay where nothing is painted yet, the seam feathered;
2. FLUX 3 Image Klein (face_paint_cli.paint) edits that picture alone - the person comes from its painted part (with
   the hero as a second reference, round 54's first try, the model painted the hero's front view instead of the
   30-degree one: the lips 180 px off);
3. the new painting aligned to the clay (align_paintings.py, in MediaPipe's environment) before the next view uses it.

Run (the tool environment with OpenEXR): .dev/venv-rdf/Scripts/python -I tools/face_test/face_paint_seq.py SEED [VIEW ...]
"""

import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, str(HERE / f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fv = _load("flow_views")
painter = _load("face_paint_cli")
DIR = fv.DIR
TOOLS_PYTHON = Path("E:/Dev/3D/just-stage/.dev/venv-tools/Scripts/python.exe")  # MediaPipe's environment
HERO = "face"
ORDER = ("faceleft30", "faceright30", "front", "left40", "right40", "above", "below", "left90", "right90")
FEATHER = 12  # px: the painted part fades into the clay over this, inside its own border
PROMPT = (
    "Make image 1 a real photograph. Keep its head shape, pose, camera angle and framing exactly, and keep every part "
    "that is already a photograph; the rest is the same man: the same face, skin tone, eyes, brows, nose and lips. "
    "Completely bald, smooth scalp with no hair and no stubble, mouth closed. Natural skin with visible "
    "pores and fine lines. Soft even studio light from every side, no shadows, plain grey background. Sharp focus, "
    "high detail, professional portrait photo."
)


def srgb(path):
    return cv2.imread(str(path))[..., ::-1].astype(np.float32) / 255.0


def composite(view, done, views):
    """What is painted so far, seen from `view`'s camera, over its clay."""
    target = views[view]
    num = np.zeros(target.albedo.shape, np.float32)
    den = np.zeros(target.albedo.shape[:2], np.float32)
    for name in done:
        col, row, w = views[name].seen_from(target)
        src = DIR / f"aligned_{name}.png"
        src = src if src.exists() else DIR / f"painted_{name}.png"  # as delight_views: no face found, not aligned
        num += cv2.remap(srgb(src), col, row, cv2.INTER_LINEAR) * w[..., None]
        den += w
    painted = num / np.maximum(den[..., None], 1e-6)
    hard = np.clip(den / 0.2, 0.0, 1.0).astype(np.float32)
    inside = cv2.erode(hard, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4 * FEATHER + 1,) * 2))
    alpha = cv2.GaussianBlur(inside, (0, 0), FEATHER)
    clay = srgb(DIR / f"clay_{view}.png")
    out = alpha[..., None] * painted + (1.0 - alpha[..., None]) * clay
    return (np.clip(out, 0.0, 1.0)[..., ::-1] * 255.0).round().astype(np.uint8), float(alpha[target.covered].mean())


def main(argv) -> int:
    seed, todo = int(argv[0]), argv[1:] or list(ORDER)
    cams = json.load(open(DIR / "cameras.json"))
    views = {name: fv.View(name, cams[name]) for name in fv.VIEWS}
    done = [HERO] + list(ORDER[:ORDER.index(todo[0])])  # a resumed run: the views before its first are painted
    for view in todo:
        t = time.time()
        picture, share = composite(view, done, views)
        start = DIR / f"seq_start_{view}.png"
        cv2.imwrite(str(start), picture)
        painter.paint([start], PROMPT, seed, DIR / f"painted_{view}.png")
        subprocess.run([str(TOOLS_PYTHON), str(HERE / "align_paintings.py"), view], check=True)
        done.append(view)
        print(f"{view}: {share:.0%} of it painted already; repainted and aligned in {time.time() - t:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
