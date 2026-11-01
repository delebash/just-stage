# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, stage 2 with FLUX 3 Image Klein (measured 2026-10-30: it holds our head 2–5× closer than FLUX.2 klein):
each clay view repainted as a photograph by stable-diffusion.cpp's `sd-cli`, the view as its one reference. The model
isn't a row on JustStage's server yet, so this runs the engine directly — the same flags the server would pass.

Run: python tools/face_test/face_paint_cli.py SEED [VIEW ...]
"""

import subprocess
import sys
import time
from pathlib import Path

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest")
CACHE = Path("E:/Dev/Web/justwrite-app/data/ai-cache")
JD = Path("E:/Dev/Web/test-just-direct/ai-cache/hf")
ENGINE = CACHE / "sdcpp/master-1024-77b72a2/cuda12/sd-cli.exe"
MODEL = JD / "models--leejet--flux-3-image-klein-GGUF/snapshots/1c2ad2f9b9247ccca6506a23bdb033fdb0873321/flux3-image-klein-Q8_0.gguf"
LLM = JD / "models--Qwen--Qwen3-VL-4B-Instruct-GGUF/snapshots/1cd86afb9a95c410a6038ab3b40d8b578c892266/Qwen3VL-4B-Instruct-Q8_0.gguf"
VAE = CACHE / "hf/models--black-forest-labs--FLUX.2-klein-4B/snapshots/e7b7dc27f91deacad38e78976d1f2b499d76a294/vae/diffusion_pytorch_model.safetensors"
PROMPT = (
    "Turn this 3D render into a real photograph of the same completely bald man: exactly the same head shape, face, "
    "pose, camera angle and framing. Smooth bald scalp with no hair and no stubble. Natural human skin with visible "
    "pores, fine lines, slight redness on the nose and cheeks, faint freckles, realistic lips and eyelids, mouth closed. "
    "Soft even studio light from every side, no shadows, plain grey background. Sharp focus, high detail, professional "
    "portrait photo."
)
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below", "face", "faceleft30", "faceright30")



def paint(refs, prompt, seed, out):
    """One FLUX 3 Image Klein edit: the reference pictures (the first is the one edited), the prompt, the seed."""
    subprocess.run(
        [str(ENGINE), "--diffusion-model", str(MODEL), "--vae", str(VAE), "--llm", str(LLM),
         *[a for r in refs for a in ("-r", str(r))], "-p", prompt, "--cfg-scale", "1", "--steps", "16",
         "--sampling-method", "euler", "-W", "1024", "-H", "1024", "-s", str(seed), "--offload-to-cpu", "-o", str(out)],
        check=True, capture_output=True,
    )


def main(argv) -> int:
    seed = int(argv[0])
    for view in argv[1:] or VIEWS:
        t = time.time()
        paint([DIR / f"clay_{view}.png"], PROMPT, seed, DIR / f"painted_{view}.png")
        print(f"{view}: {time.time() - t:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
