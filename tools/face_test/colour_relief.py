# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face's mid-scale relief - forehead lines, the frown's, crow's feet, the lower lid's creases, the nose-to-mouth
folds - read from a scan's own COLOUR (2026-11-09, the own-content proof's working doc, 18:2x-18:4x).

A photogrammetry scan's mesh is smoothed past its wrinkles, but its colour - its photos projected - still shows them
as shading (HSR0040, 50: deep forehead lines in the colour, none in the mesh). Sapiens2's surface-normal model (Meta,
the Sapiens2 License; RESEARCH 14.9 - a build-time tool, its weights never ship) reads them back as relief: the face
cut upright from the scan's colour on our head tile (`scan_bake.py`'s `bake_colour.png`), its normals' fine part
(slopes under FINE_MM) integrated to a height (Frankot & Chellappa 1988, by FFT), the broad shape over BROAD_MM taken
off, put back on the head tile, kept to the face's skin (the scan's own face labels - its hair, brows and eyes out;
the eye openings, lid margins, lips and nostrils out), small dots (pores, follicles) out by an area
filter (DOTS_MM2), as tangent-space XY. `skin_base._relief` adds it to the scan's own relief.

Writes scans/NAME/colour_relief.npy (H x W x 2 float16, top row first, the head tile) and colour_relief.png (a look),
and caches the model's normals in colour_normals.npy. Run in the tool environment with PyTorch and Sapiens2's code
(the card, ~3.5 GB, ~30 s a scan):

    .dev/venv-rdf/Scripts/python -I tools/face_test/colour_relief.py NAME [NAME ...]
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / ".dev" / "facetest" / "scans"
MASKS = ROOT / "extension" / "juststage" / "data" / "generated" / "skin"
SAPIENS = ROOT / ".dev" / "cache" / "src" / "sapiens2"  # facebookresearch/sapiens2 7e5bae88
CKPT = ROOT / ".dev" / "cache" / "sapiens2" / "sapiens2_1b_normal.safetensors"
CONFIG = SAPIENS / "sapiens/dense/configs/normal/metasim_render_people/sapiens2_1b_normal_metasim_render_people-1024x768.py"
HEAD_TILE = 1001
CROP_H, CROP_W = 1024, 768  # the model's own window (texels of the head tile: ~181 x 136 mm)
FINE_MM, BROAD_MM = 2.0, 4.0  # the slopes' fine part kept; the height's broad part taken off (sap40f, 18:4x)
DOTS_MM2 = 3.0  # pits and bumps smaller than this out (pores, stubble follicles: the scan's colour, not relief)
FACE_HALF_MM, FOREHEAD_MM, CHIN_MM = 68.0, 110.0, 45.0  # the face kept: its half width, above the eyes, below the mouth
HOLE_MARGIN_MM = 2.0  # off the skin mask's holes (a brow's stray hairs)
CROP_DROP_MM = 20.0  # the crop's centre below the eyes' midpoint (the forehead to the hairline in the window; 27
#: cut the upper forehead at 63 mm above the eyes, 19:3x)
EDGE_FADE_MM = (3.0, 10.0)  # the relief fades out from this far inside the crop's edge to this far (no step: a step
#: in the height is a line in the normals - Scan man A's seam down the temple, 19:3x)


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def texels_per_mm(size: int) -> float:
    """The head tile's scale: maps.MM_PER_UV, read from the add-on's source (`body_scan._mm_per_uv`)."""
    return size / _module("body_scan", ROOT / "tools" / "body_scan.py")._mm_per_uv(HEAD_TILE)


def _blobs(name: str, size: int) -> list[np.ndarray]:
    """The layout mask's blobs on the head tile (the eyeballs' own tiles, low in the picture, left out), in texels."""
    m = cv2.imread(str(MASKS / name), cv2.IMREAD_GRAYSCALE) > 20
    n, _lab, st, cen = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    s = m.shape[0]
    return [cen[i] * size / s for i in range(1, n) if cen[i][1] < 0.7 * s and st[i][4] > 20]


def face_frame(size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Our layout's face on the head tile (the same for every scan): the eyes' midpoint, the unit vector up the face
    (from the mouth to the eyes) and the mouth, in texels (x right, y down)."""
    eyes, mouth = _blobs("face_eyes.png", size), _blobs("mouth.png", size)[0]
    mid = (eyes[0] + eyes[1]) / 2
    return mid, (mid - mouth) / np.linalg.norm(mid - mouth), mouth


def crop_axes(up: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The upright crop's right and down on the head tile - a rotation, never a mirror."""
    down = -up
    return np.array([down[1], -down[0]]), down


def fine_height(normals: np.ndarray, mm: float) -> np.ndarray:
    """A height (mm) from normals (x right, y up, z toward the viewer; texels of `mm` a millimetre): only their slopes'
    part under FINE_MM, integrated by Frankot & Chellappa's FFT (mirrored so the edges stay quiet), its part over
    BROAD_MM taken off."""
    nz = np.maximum(normals[..., 2], 0.2)
    p, q = -normals[..., 0] / nz, normals[..., 1] / nz  # dz/dx, dz/dy (y down)
    p = np.clip(p - cv2.GaussianBlur(p, (0, 0), FINE_MM * mm), -0.5, 0.5)
    q = np.clip(q - cv2.GaussianBlur(q, (0, 0), FINE_MM * mm), -0.5, 0.5)
    h, w = p.shape
    big_p = np.block([[p, -p[:, ::-1]], [p[::-1, :], -p[::-1, ::-1]]])
    big_q = np.block([[q, q[:, ::-1]], [-q[::-1, :], -q[::-1, ::-1]]])
    wx, wy = np.meshgrid(np.fft.fftfreq(2 * w) * 2 * np.pi, np.fft.fftfreq(2 * h) * 2 * np.pi)
    den = wx**2 + wy**2
    den[0, 0] = 1.0
    z_hat = (-1j * wx * np.fft.fft2(big_p) - 1j * wy * np.fft.fft2(big_q)) / den
    z_hat[0, 0] = 0.0
    z = np.real(np.fft.ifft2(z_hat))[:h, :w].astype(np.float32)
    return (z - cv2.GaussianBlur(z, (0, 0), BROAD_MM * mm)) / mm


def remove_dots(z_mm: np.ndarray, mm: float, range_mm: float = 0.4) -> np.ndarray:
    """Pits and bumps under DOTS_MM2 out (scikit-image's area closing, then opening) - lines are kept whole."""
    from skimage.morphology import area_closing, area_opening

    q16 = np.clip(32768 + z_mm / (2 * range_mm) * 65535, 0, 65535).astype(np.uint16)
    area = int(DOTS_MM2 * mm * mm)
    q16 = area_opening(area_closing(q16, area), area)
    return (q16.astype(np.float32) - 32768) / 65535 * (2 * range_mm)


def tangent_xy(z_mm: np.ndarray, mm: float) -> np.ndarray:
    """A height (mm, top row first) as tangent-space normal XY: x along U (right), y along V (up the picture)."""
    gx = cv2.Sobel(z_mm, cv2.CV_32F, 1, 0, ksize=3) / 8.0 * mm  # mm of height a mm of skin
    gy = -cv2.Sobel(z_mm, cv2.CV_32F, 0, 1, ksize=3) / 8.0 * mm  # up the picture is +V
    n = np.dstack([-gx, -gy, np.ones_like(gx)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n[..., :2]


def skin_mask(d: Path, size: int, mm: float) -> np.ndarray:
    """The scan's skin for its relief: what it reached (`bake_cover.png`) that its face labels call skin (`skin.png`,
    scan_skin.py: brows, eyes and hair out), HOLE_MARGIN_MM off every hole for the stray hairs at a brow's edge. Not
    `layers.npz`'s `valid`: that leaves a whole band round the eyes and brows (and the stubble) out for the colour -
    the crow's feet and the lower lid's creases are in it (18:5x)."""
    cover = cv2.imread(str(d / "bake_cover.png"), cv2.IMREAD_GRAYSCALE) > 127
    skin = cv2.resize(cv2.imread(str(d / "skin.png"), cv2.IMREAD_GRAYSCALE), (size, size)) > 127
    if cover.shape[0] != size:
        cover = cv2.resize(cover.astype(np.uint8), (size, size), interpolation=cv2.INTER_NEAREST) > 0
    k = int(HOLE_MARGIN_MM * mm) * 2 + 1
    holes = cv2.dilate((~(cover & skin)).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    return cover & skin & (holes == 0)


def edge_fade(bx: np.ndarray, by: np.ndarray, mm: float) -> np.ndarray:
    """0 outside the crop and EDGE_FADE_MM[0] inside its edge, 1 from EDGE_FADE_MM[1] in, smooth between (smoothstep):
    `bx`, `by` a texel's place in the crop."""
    edge = np.minimum(np.minimum(bx, CROP_W - 1 - bx), np.minimum(by, CROP_H - 1 - by)) / mm  # mm inside the crop
    lo, hi = EDGE_FADE_MM
    t = np.clip((edge - lo) / (hi - lo), 0.0, 1.0)
    return (t * t * (3.0 - 2.0 * t)).astype(np.float32)


def keep_mask(valid: np.ndarray, mm: float) -> np.ndarray:
    """Where the colour's relief is kept on the head tile (0-1): the scan's own skin, inside the face, out of the eye
    openings (face_eyes over 250 - over 20 took a 50 mm disc with the crow's feet, 18:4x), the lid margins, the lips and
    the nostrils."""
    size = valid.shape[0]
    mid, up, mouth = face_frame(size)
    right, _down = crop_axes(up)

    def mask(name: str, grow_mm: float, level: int) -> np.ndarray:
        m = cv2.resize(cv2.imread(str(MASKS / name), cv2.IMREAD_GRAYSCALE), (size, size)) > level
        k = max(int(grow_mm * mm) | 1, 1)
        return cv2.dilate(m.astype(np.uint8), np.ones((k, k), np.uint8)) > 0

    away = mask("face_eyes.png", 1.6, 250) | mask("stretched.png", 1.6, 128)
    away |= mask("mouth.png", 4.4, 20) | mask("lips_upper.png", 4.4, 20)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    along = (xx - mid[0]) * up[0] + (yy - mid[1]) * up[1]
    across = np.abs((xx - mid[0]) * right[0] + (yy - mid[1]) * right[1])
    d = float(np.linalg.norm(mid - mouth))
    face = (across < FACE_HALF_MM * mm) & (along > -(d + CHIN_MM * mm)) & (along < FOREHEAD_MM * mm)
    face &= ~((along < -0.55 * d) & (along > -0.85 * d) & (across < 18 * mm))  # the nostrils' rims read as rings
    face = cv2.GaussianBlur(face.astype(np.float32), (0, 0), 8 * mm)
    keep = (valid & ~away).astype(np.float32) * face
    return cv2.GaussianBlur(keep, (0, 0), 3 * mm) * keep


_MODEL = None


def _normals(crop: np.ndarray) -> np.ndarray:
    """Sapiens2's normals of an upright 1024 x 768 picture (x right, y up, z toward the camera)."""
    import torch

    sys.path.insert(0, str(SAPIENS))
    from sapiens.dense.models import NormalEstimator, init_model  # noqa: F401 - registers the estimator

    global _MODEL
    if _MODEL is None:  # loaded once for every scan of the run
        _MODEL = init_model(str(CONFIG), str(CKPT), device="cpu")
        _MODEL.half().cuda()
    model = _MODEL
    data = model.data_preprocessor(model.pipeline(dict(img=crop)))
    inputs = data["inputs"].cuda().half()
    with torch.no_grad():
        n = model(inputs).float()
    n = n / n.norm(dim=1, keepdim=True).clamp_min(1e-8)
    pl, pr, pt, pb = data["data_samples"]["meta"]["padding_size"]
    n = n[:, :, pt : inputs.shape[2] - pb, pl : inputs.shape[3] - pr][0].permute(1, 2, 0).cpu().numpy()
    if n.shape[:2] != (CROP_H, CROP_W):
        n = cv2.resize(n, (CROP_W, CROP_H), interpolation=cv2.INTER_LINEAR)
    return n / np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-8)


def relief(name: str) -> np.ndarray:
    """One scan's colour relief on the head tile (tangent XY), its normals cached."""
    d = DIR / name
    bgr = cv2.imread(str(d / "bake_colour.png"), cv2.IMREAD_UNCHANGED)
    if bgr.dtype == np.uint16:
        bgr = (bgr / 257.0).astype(np.uint8)
    bgr = bgr[..., :3]
    size = bgr.shape[0]
    mm = texels_per_mm(size)
    mid, up, _mouth = face_frame(size)
    right, down = crop_axes(up)
    centre = mid - up * CROP_DROP_MM * mm
    jj, ii = np.meshgrid(np.arange(CROP_W) - CROP_W / 2, np.arange(CROP_H) - CROP_H / 2)
    map_x = (centre[0] + jj * right[0] + ii * down[0]).astype(np.float32)
    map_y = (centre[1] + jj * right[1] + ii * down[1]).astype(np.float32)
    cache = d / "colour_normals.npy"
    if cache.exists():
        n = np.load(cache).astype(np.float32)
    else:
        n = _normals(cv2.remap(bgr, map_x, map_y, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT))
        np.save(cache, n.astype(np.float16))
    z = fine_height(n, mm)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    bx = ((xx - centre[0]) * right[0] + (yy - centre[1]) * right[1] + CROP_W / 2).astype(np.float32)
    by = ((xx - centre[0]) * down[0] + (yy - centre[1]) * down[1] + CROP_H / 2).astype(np.float32)
    inside = edge_fade(bx, by, mm)
    tile_z = cv2.remap(z.astype(np.float32), bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    tile_z = remove_dots(tile_z * keep_mask(skin_mask(d, size, mm), mm) * inside, mm)
    xy = tangent_xy(tile_z, mm)
    np.save(d / "colour_relief.npy", xy.astype(np.float16))
    look = np.clip(0.5 + tile_z / 0.8, 0, 1)
    cv2.imwrite(str(d / "colour_relief.png"), (look * 255).astype(np.uint8))
    print(f"{name}: colour relief p1 {np.percentile(tile_z[tile_z != 0], 1):.3f} mm, p99 "
          f"{np.percentile(tile_z[tile_z != 0], 99):.3f} mm", flush=True)
    return xy


def main(argv: list[str]) -> int:
    for name in argv:
        relief(name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
