# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the paintings' relief: Sapiens2's surface normals (Meta, the Sapiens2 License; the human normal model
our research ranked first, measured 2026-10-30 at 8.5–12.7° from our mesh's broad shape against DAViD's 9.6–15.9°)
for each aligned painting, in camera space (x right, y up, z toward the camera), saved as normal_<view>.npy.

A 1024² picture runs as two 1024×768 windows at the model's own resolution, blended where they overlap.

Run (the tool environment with PyTorch and Sapiens2's code):
  .dev/venv-rdf/Scripts/python -I tools/face_test/view_normals.py [VIEW ...]
"""

import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest")
REPO = Path("E:/Dev/3D/just-stage/.dev/cache/src/sapiens2")  # facebookresearch/sapiens2 7e5bae88
CKPT = Path("E:/Dev/3D/just-stage/.dev/cache/sapiens2/sapiens2_1b_normal.safetensors")
CONFIG = REPO / "sapiens/dense/configs/normal/metasim_render_people/sapiens2_1b_normal_metasim_render_people-1024x768.py"
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below", "face", "faceleft30", "faceright30")
WIDTH = 768

sys.path.insert(0, str(REPO))
from sapiens.dense.models import NormalEstimator, init_model  # noqa: E402, F401 — registers the estimator


def estimate(model, img):
    h, w = img.shape[:2]
    acc, wsum = np.zeros((h, w, 3), np.float32), np.zeros((h, w, 1), np.float32)
    for x0 in (0, w - WIDTH):
        data = model.data_preprocessor(model.pipeline(dict(img=img[:, x0 : x0 + WIDTH])))
        inputs = data["inputs"].cuda().half()
        with torch.no_grad():
            n = model(inputs).float()
        n = n / n.norm(dim=1, keepdim=True).clamp_min(1e-8)
        pl, pr, pt, pb = data["data_samples"]["meta"]["padding_size"]
        n = n[:, :, pt : inputs.shape[2] - pb, pl : inputs.shape[3] - pr][0].permute(1, 2, 0).cpu().numpy()
        if n.shape[:2] != (h, WIDTH):
            n = cv2.resize(n, (WIDTH, h), interpolation=cv2.INTER_LINEAR)
        ramp = np.clip(np.minimum(np.arange(WIDTH), WIDTH - 1 - np.arange(WIDTH)) / 128.0, 0.0, 1.0)
        ramp[: 128 if x0 == 0 else 0] = 1.0
        if x0:
            ramp[-128:] = 1.0
        acc[:, x0 : x0 + WIDTH] += n * ramp[None, :, None]
        wsum[:, x0 : x0 + WIDTH] += ramp[None, :, None]
    n = acc / np.maximum(wsum, 1e-6)
    return n / np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-8)


def main() -> int:
    model = init_model(str(CONFIG), str(CKPT), device="cpu")
    model.half().cuda()
    for view in sys.argv[1:] or VIEWS:
        src = DIR / f"aligned_{view}.png"
        src = src if src.exists() else DIR / f"painted_{view}.png"
        t = time.time()
        n = estimate(model, cv2.imread(str(src)))
        np.save(DIR / f"normal_{view}.npy", n.astype(np.float16))
        cv2.imwrite(str(DIR / f"normal_{view}.png"), ((n * 0.5 + 0.5)[..., ::-1] * 255).clip(0, 255).astype(np.uint8))
        print(f"{view}: {src.name}, {time.time() - t:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
