# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Rec 18's contenders (`docs/plans/2026-11-04-realism-review-brief.md` §6.18, the order in §10): pore-scale relief
from each source as a tileable height tile with its real size, for the pore slot of the skin (`modules/skin/maps.py`
`pores`). Local measurement only - nothing here ships.

    .dev/venv-rdf/Scripts/python -I tools/gate/relief_tiles.py ten24      # Ten24's finest normals -> height
    .dev/venv-rdf/Scripts/python -I tools/gate/relief_tiles.py photo NAME X Y SIZE PX_PER_MM   # Marigold normals
    .dev/venv-rdf/Scripts/python -I tools/gate/relief_tiles.py lps        # today's tile, copied for the sheet

A normal map becomes height by Frankot & Chellappa's integration (1988; the FFT least-squares surface from a gradient
field - the standard way), then a high-pass keeps the pore and fine-line scale (features under HIGH_PASS_MM), and a
Moisan's periodic component makes it tile. Out: `.dev/gate/relief/<name>.png` (16-bit grey) + `<name>.json`
(its size in mm and where it came from)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None  # the scans' 16K atlases (our own downloads, 268M pixels) trip Pillow's bomb check

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".dev" / "gate" / "relief"
TEN24 = ROOT / ".dev" / "downloads" / "ten24_sample" / "x" / "OBJ Package"
#: Ten24's upper cheek on its 8K maps (between ear and nose, under the eye, clear of stubble - seen 2026-11-05) and its
#: density there: eye to mouth ~300 texels ~ 65 mm
TEN24_CHEEK = (5830, 6580, 180)
TEN24_PX_PER_MM = 4.6
HIGH_PASS_MM = 1.5  # pores and fine lines; 3 mm left the integration's 2-3 mm blobs on top (seen 2026-11-05)
LPS = ROOT / ".dev" / "facetest" / "pores_lps.png"
LPS_TILE_MM = 56.0  # the shipped tile's size on the skin (modules/skin/maps.py)


def _ffmpeg_crop(path: Path, x: int, y: int, size: int) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"crop={size}:{size}:{x}:{y}",
                          "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.uint16).reshape(size, size, 3).astype(np.float64) / 65535.0


def height_from_normals(normal_rgb: np.ndarray, flatten_px: float | None = None) -> np.ndarray:
    """Frankot-Chellappa: the surface whose gradient best fits the normals' (p = -nx/nz, q = -ny/nz), in Fourier space;
    rows run down the image, so y flips (a tangent-space map's green points up)."""
    n = normal_rgb * 2.0 - 1.0
    nz = np.clip(n[..., 2], 0.2, None)
    p0, q0 = -n[..., 0] / nz, n[..., 1] / nz
    if flatten_px:  # the slopes' local mean out first: a photo looked at on a slant (or curved) leans all its normals
        p0 = p0 - ndimage.gaussian_filter(p0, flatten_px, mode="reflect")  # one way - integrated whole, that lean is a
        q0 = q0 - ndimage.gaussian_filter(q0, flatten_px, mode="reflect")  # ramp far taller than the pores
    # mirrored to 2h x 2w so the field repeats cleanly (the height mirrored is even, its x-slope odd in x, its y-slope
    # odd in y) - without it the FFT's wrap-around put blobs on the edges (seen 2026-11-05 on a photo)
    p = np.block([[p0, -p0[:, ::-1]], [p0[::-1, :], -p0[::-1, ::-1]]])
    q = np.block([[q0, q0[:, ::-1]], [-q0[::-1, :], -q0[::-1, ::-1]]])
    h, w = p.shape
    wx = np.fft.fftfreq(w) * 2 * np.pi
    wy = np.fft.fftfreq(h) * 2 * np.pi
    u, v = np.meshgrid(wx, wy)
    denom = u**2 + v**2
    denom[0, 0] = 1.0
    z = (-1j * u * np.fft.fft2(p) - 1j * v * np.fft.fft2(q)) / denom
    z[0, 0] = 0.0
    return np.real(np.fft.ifft2(z))  # the mirrored 2h x 2w height: fine_tile filters it whole, then keeps a quarter


def periodic(u: np.ndarray) -> np.ndarray:
    """Moisan's periodic component ("Periodic plus smooth image decomposition", J. Math. Imaging Vis. 2011): `u` minus
    the smooth image that carries its edges' mismatch, so it tiles without a seam and without blending two copies."""
    h, w = u.shape
    v = np.zeros_like(u)
    v[0, :] += u[-1, :] - u[0, :]
    v[-1, :] += u[0, :] - u[-1, :]
    v[:, 0] += u[:, -1] - u[:, 0]
    v[:, -1] += u[:, 0] - u[:, -1]
    denom = 2 * np.cos(2 * np.pi * np.arange(w) / w)[None, :] + 2 * np.cos(2 * np.pi * np.arange(h) / h)[:, None] - 4
    denom[0, 0] = 1.0
    smooth = np.fft.fft2(v) / denom
    smooth[0, 0] = 0.0
    return u - np.real(np.fft.ifft2(smooth))


def fine_tile(height: np.ndarray, px_per_mm: float) -> np.ndarray:
    """The pore and fine-line band (under HIGH_PASS_MM), a 5% margin trimmed (an estimator's edges are its weakest),
    made to tile (Moisan), 0-1 around 0.5."""
    # the high-pass on the mirrored height (it repeats, continuous at its edges: no edge residue from a photo's slope)
    fine = height - ndimage.gaussian_filter(height, HIGH_PASS_MM * px_per_mm / 2.0, mode="wrap")
    fine = fine[: fine.shape[0] // 2, : fine.shape[1] // 2]
    m = int(0.05 * min(fine.shape))
    fine = fine[m:-m, m:-m]
    side = min(fine.shape)
    tiled = periodic(fine[:side, :side])
    tiled = (tiled - tiled.mean()) / (4.0 * tiled.std() + 1e-12)  # +-2 sigma in 0-1
    return np.clip(tiled + 0.5, 0.0, 1.0)


def _write(name: str, tile: np.ndarray, size_mm: float, source: dict) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.png"
    Image.fromarray(np.round(tile * 65535).astype(np.uint16)).save(path)
    (OUT / f"{name}.json").write_text(json.dumps({"size_mm": size_mm, "px": tile.shape[0], **source}, indent=1))
    print(f"{name}: {tile.shape[0]} px = {size_mm:.1f} mm -> {path}")
    return path


def ten24() -> Path:
    x, y, size = TEN24_CHEEK
    normals = _ffmpeg_crop(TEN24 / "Normal Maps" / "Level_01_Normal.PSD", x, y, size)
    tile = fine_tile(height_from_normals(normals, HIGH_PASS_MM * TEN24_PX_PER_MM / 2.0), TEN24_PX_PER_MM)
    return _write("ten24", tile, tile.shape[0] / TEN24_PX_PER_MM,
                  {"source": "Ten24 sample scan, Level_01_Normal.PSD (8K), upper cheek", "crop": [x, y, size],
                   "licence": "Ten24: 'use this scan as you wish ... credit' (page saved 2026-11-04)"})


def lps() -> Path:
    img = np.asarray(Image.open(LPS).convert("I;16") if Image.open(LPS).mode.startswith("I") else
                     Image.open(LPS).convert("L"), dtype=np.float64)
    tile = img / img.max()
    return _write("lps", tile, LPS_TILE_MM, {"source": "today's pore tile (Lee Perry-Smith 'Infinite' scan)",
                                             "licence": "CC BY 3.0"})


#: Marigold's weights in the repo's own cache (never C:), and its trained resolution ("any larger input image should be
#: resized to make the longer side 768 pixels" - its model card)
HF_HOME = ROOT / ".dev" / "cache" / "hf"
MARIGOLD = "prs-eth/marigold-normals-v1-1"


def marigold_normals(rgb: np.ndarray, processing_resolution: int = 768) -> np.ndarray:
    """Marigold's normals (diffusers `MarigoldNormalsPipeline`, its weights only - no remote code) as a 0-1 tangent
    normal map, x right, y up, z toward the camera."""
    import os

    os.environ.setdefault("HF_HOME", str(HF_HOME))
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    import torch
    from diffusers import MarigoldNormalsPipeline

    pipe = MarigoldNormalsPipeline.from_pretrained(MARIGOLD, torch_dtype=torch.float16).to("cuda")
    out = pipe(Image.fromarray((rgb * 255).astype(np.uint8)), processing_resolution=processing_resolution,
               ensemble_size=4, output_type="np")
    normals = np.asarray(out.prediction[0], dtype=np.float64)  # -1..1, x right, y up, z to the camera
    print(f"marigold: peak card {torch.cuda.max_memory_allocated() / 2**20:.0f} MiB")
    return normals * 0.5 + 0.5


def photo(name: str, path: str, x: int, y: int, size: int, px_per_mm: float, note: str) -> Path:
    """A photo's crop -> Marigold normals -> the same height and band as the scans (`px_per_mm` from the photo's own
    features: say how in `note`)."""
    img = Image.open(path).convert("RGB").crop((x, y, x + size, y + size))
    rgb = np.asarray(img, dtype=np.float64) / 255.0
    OUT.mkdir(parents=True, exist_ok=True)
    cached = OUT / f"{name}_normals.npy"  # Marigold's answer kept (float), so a change below doesn't rerun it
    if cached.exists():
        normals = np.load(cached)
    else:
        normals = marigold_normals(rgb)
        np.save(cached, normals)
    Image.fromarray((normals * 255).astype(np.uint8)).save(OUT / f"{name}_normals.png")
    tile = fine_tile(height_from_normals(normals, HIGH_PASS_MM * px_per_mm / 2.0), px_per_mm)
    return _write(name, tile, tile.shape[0] / px_per_mm, {"source": str(Path(path).name), "crop": [x, y, size],
                                                 "px_per_mm": px_per_mm, "scale_from": note,
                                                 "normals": f"{MARIGOLD} (OpenRAIL++, local test only)"})


if __name__ == "__main__":
    if sys.argv[1] == "photo":
        name, path, x, y, size, ppm, note = sys.argv[2:9]
        photo(name, path, int(x), int(y), int(size), float(ppm), note)
    else:
        {"ten24": ten24, "lps": lps}[sys.argv[1]]()
