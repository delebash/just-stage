# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""A skin photo's fine relief as a seamless height map — the skin detail's maths, numpy only.

The way texture artists make a micro-detail map from a skin photo: keep the flat middle of the frame, drop the colour
(luminance), drop the large shading and tone changes (a high-pass: the photo minus its Gaussian blur, so pores and the
crosshatch of skin lines remain — dark is low), then make it tile: the photo blended with itself shifted by half, the
shifted copy at the edges (GIMP's Tile Seamless), its weights normalised so the blend keeps the relief's contrast.
"""

from __future__ import annotations

import numpy as np

#: Rec. 709 luminance weights (linear-light coefficients, applied to the 8-bit values as is — relief, not colour)
LUMA = (0.2126, 0.7152, 0.0722)


def gaussian_blur(img: np.ndarray, sigma: float) -> np.ndarray:
    """A Gaussian blur through the FFT; its edges wrap (relief() pads by mirroring first)."""
    h, w = img.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    kernel = np.exp(-2.0 * (np.pi * sigma) ** 2 * (fx**2 + fy**2))
    return np.real(np.fft.ifft2(np.fft.fft2(img) * kernel))


def relief(rgb: np.ndarray, crop: float = 0.6, sigma_px: float = 12.0) -> np.ndarray:
    """The zero-mean fine relief of the middle `crop` of an RGB photo (H×W×3, any range)."""
    h, w = rgb.shape[:2]
    ch, cw = int(h * crop), int(w * crop)
    y0, x0 = (h - ch) // 2, (w - cw) // 2
    lum = np.tensordot(rgb[y0 : y0 + ch, x0 : x0 + cw, :3].astype(np.float64), LUMA, axes=([2], [0]))
    pad = int(3 * sigma_px) + 1  # mirrored, so the blur never mixes one edge's tone into the other's
    blurred = gaussian_blur(np.pad(lum, pad, mode="reflect"), sigma_px)[pad:-pad, pad:-pad]
    high = lum - blurred
    return high - high.mean()


def make_seamless(high: np.ndarray) -> np.ndarray:
    """Blend a zero-mean relief with itself shifted by half: the original in the middle, the shifted copy (whose edges
    meet across the wrap) at the edges; dividing by √(w² + (1 − w)²) keeps the relief's contrast through the blend."""
    h, w = high.shape
    shifted = np.roll(high, (h // 2, w // 2), axis=(0, 1))
    wy = 1.0 - np.abs(np.linspace(-1.0, 1.0, h))
    wx = 1.0 - np.abs(np.linspace(-1.0, 1.0, w))
    weight = np.outer(wy, wx)
    return (weight * high + (1.0 - weight) * shifted) / np.sqrt(weight**2 + (1.0 - weight) ** 2)


def height_map(rgb: np.ndarray, crop: float = 0.6, sigma_px: float = 12.0, spread: float = 3.0) -> np.ndarray:
    """A seamless height map in 0–1 (0.5 is the skin's surface) from a skin photo; ±`spread` standard deviations of the
    relief fill the range."""
    tile = make_seamless(relief(rgb, crop, sigma_px))
    return np.clip(0.5 + tile / (2.0 * spread * tile.std()), 0.0, 1.0).astype(np.float32)


def wrap_ratio(img: np.ndarray) -> float:
    """How well an image tiles: the mean step across its wrap-around seam over the mean step between neighbours inside
    (about 1 for a seamless image, well above 1 for one that isn't)."""
    inside = np.abs(np.diff(img, axis=1)).mean() + np.abs(np.diff(img, axis=0)).mean()
    seam = np.abs(img[:, 0] - img[:, -1]).mean() + np.abs(img[0, :] - img[-1, :]).mean()
    return float(seam / inside)
