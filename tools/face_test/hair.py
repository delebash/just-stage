# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Hair out of a skin image - CC5's way: hair is geometry (lash cards, brow layers, a stubble shell), a skin's colour
and relief carry none (HD Aaron's head diffuse: no lashes, no brows; docs/plans/2026-11-06-inputs-audit.md). A scan's
photo carries the person's lashes, brow hairs, stray hairs and stubble; this finds the strands and fills them from the
skin round them.

The method is DullRazor's (Lee et al., "DullRazor: a software approach to hair removal from images", Computers in
Biology and Medicine 27(6), 1997 - the standard hair removal of dermoscopy): a greyscale closing with line-shaped
structuring elements at several angles. A strand along angle a survives the closing whose line lies along it and is
filled by the others; a pore (round, smaller than the line) is filled at every angle. So the strand measure is the
spread of the closings' fill over the angles - high on strands, ~0 on pores and on flat skin - in log brightness (a
ratio, the same at every tone); light strands (grey and white hairs) the same with openings. The strands found are
filled from their surroundings by OpenCV's inpainting (Telea 2004), as DullRazor fills them by interpolation.
"""

from __future__ import annotations

import cv2
import numpy as np

LENGTH = 7  # texels: the line elements' length - a strand longer than this, thinner than it (~1.2 mm at 6 texels/mm; pores are 1-2 texels across)
ANGLES = 12
DARK, LIGHT = 0.10, 0.10  # the strand measure's threshold, log brightness (a strand ~10% darker / lighter than skin)
MIN_AREA = 6  # texels: smaller finds are noise
GROW = 1  # texels: the mask grown round each strand (its soft edge)
RADIUS = 4  # texels: the inpainting's reach
SOFTEN = 0.7  # texels

LUMA = np.array([0.2126, 0.7152, 0.0722], np.float32)


def _lines(length: int, angles: int) -> list[np.ndarray]:
    """Line elements through the centre, point-symmetric about it (OpenCV's closing and opening apply one kernel
    unreflected - a lopsided line shifts them, and pores then read as strands)."""
    kernels = []
    c = length // 2
    for k in range(angles):
        a = np.pi * k / angles
        se = np.zeros((length, length), np.uint8)
        se[c, c] = 1
        for t in range(1, c + 1):
            dx, dy = int(np.floor(t * np.cos(a) + 0.5)), int(np.floor(t * np.sin(a) + 0.5))
            se[c + dy, c + dx] = se[c - dy, c - dx] = 1
        kernels.append(se)
    return kernels


def measure(log_lum: np.ndarray, length: int = LENGTH, angles: int = ANGLES) -> tuple[np.ndarray, np.ndarray]:
    """Per texel: how strand-like a dark feature is there, and a light one (log brightness)."""
    log_lum = cv2.GaussianBlur(log_lum, (0, 0), SOFTEN)  # a strand's staircase smoothed so a straight element fits
    fill_dark, fill_light = [], []
    for se in _lines(length, angles):
        fill_dark.append(cv2.morphologyEx(log_lum, cv2.MORPH_CLOSE, se) - log_lum)
        fill_light.append(log_lum - cv2.morphologyEx(log_lum, cv2.MORPH_OPEN, se))
    d, light = np.stack(fill_dark), np.stack(fill_light)
    return d.max(0) - d.min(0), light.max(0) - light.min(0)


def mask(colour: np.ndarray, valid: np.ndarray | None = None, dark: float = DARK, light: float = LIGHT) -> np.ndarray:
    """The strands in a colour image (H x W x 3, linear or display - any monotonic brightness) as a boolean mask."""
    lum = np.maximum(colour.astype(np.float32) @ LUMA, 1e-4)
    m_dark, m_light = measure(np.log(lum))
    found = ((m_dark > dark) | (m_light > light)).astype(np.uint8)
    if valid is not None:
        found &= valid.astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(found, connectivity=8)
    keep = np.flatnonzero(stats[:, cv2.CC_STAT_AREA] >= MIN_AREA)
    keep = keep[keep > 0]
    found = np.isin(labels, keep).astype(np.uint8)
    if GROW:
        found = cv2.dilate(found, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * GROW + 1,) * 2))
    return found.astype(bool)


def fill(colour: np.ndarray, where: np.ndarray, radius: int = RADIUS) -> np.ndarray:
    """`where` filled from the texels round it (Telea's inpainting, each channel at 16 bits)."""
    out = colour.astype(np.float32).copy()
    m = where.astype(np.uint8)
    if not m.any():
        return out
    for c in range(out.shape[2]):
        ch = out[..., c]
        lo, hi = float(ch.min()), float(ch.max())
        scale = 65535.0 / max(hi - lo, 1e-9)
        q = np.round((ch - lo) * scale).astype(np.uint16)
        filled = cv2.inpaint(q, m, radius, cv2.INPAINT_TELEA).astype(np.float32) / scale + lo
        out[..., c] = np.where(where, filled, ch)
    return out


SPOT_RED = 0.06  # log(R/G) above its 1.5 mm surroundings: a red spot (a texel ~6% redder than the skin round it)
SPOT_SPAN_MM, SPOT_RADIUS_MM = 1.5, 1.2  # the surroundings' blur; the largest spot taken (a mole or a vessel is larger)


def spots(colour: np.ndarray, valid: np.ndarray, px_per_mm: float) -> np.ndarray:
    """Small red spots in a scan's colour (H x W x 3, linear) - the person's marks out, as the composition's rule has
    it (docs/plans/2026-11-06-the-plan.md §8): HD Aaron's torso shows 274 such spots where ours showed 4,240 (Artec's
    scan; EEVEE, 2026-11-07), and painted out of the render the torso's texture excess fell 0.052 -> 0.030. A boolean
    mask: texels redder than their surroundings (log R/G over its blur) in blobs no wider than SPOT_RADIUS_MM."""
    lin = np.maximum(colour.astype(np.float32), 1e-4)
    red = np.log(lin[..., 0] / lin[..., 1])
    w = valid.astype(np.float32)
    sigma = max(SPOT_SPAN_MM * px_per_mm, 1.0)
    bg = cv2.GaussianBlur(red * w, (0, 0), sigma) / np.maximum(cv2.GaussianBlur(w, (0, 0), sigma), 1e-6)
    found = ((red - bg) > SPOT_RED) & valid.astype(bool)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(found.astype(np.uint8), connectivity=8)
    largest = max(int(np.pi * (SPOT_RADIUS_MM * px_per_mm) ** 2), 1)
    keep = np.flatnonzero(stats[:, cv2.CC_STAT_AREA] <= largest)
    keep = keep[keep > 0]
    found = np.isin(labels, keep).astype(np.uint8)
    return cv2.dilate(found, np.ones((3, 3), np.uint8)).astype(bool)


def unred(colour: np.ndarray, where: np.ndarray, valid: np.ndarray, px_per_mm: float) -> np.ndarray:
    """`where` (the spots) brought to the redness of the skin round it - its red channel scaled so its log R/G is its
    surroundings' (the spots left out of the blur) - its lightness and texture kept. Filling the spots instead (Telea,
    as the strands) left round stains where they cluster: their masks merge and the fill paints a flat blob (the torso,
    2026-11-07)."""
    lin = np.maximum(colour.astype(np.float32), 1e-4).copy()
    red = np.log(lin[..., 0] / lin[..., 1])
    w = (valid.astype(bool) & ~where).astype(np.float32)
    sigma = max(SPOT_SPAN_MM * px_per_mm, 1.0)
    bg = cv2.GaussianBlur(red * w, (0, 0), sigma) / np.maximum(cv2.GaussianBlur(w, (0, 0), sigma), 1e-6)
    lin[..., 0] = np.where(where, lin[..., 1] * np.exp(bg), lin[..., 0])
    return lin


def clean(colour: np.ndarray, valid: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """The image with its strands filled, and the strands' mask (uint8)."""
    found = mask(colour, valid)
    return fill(colour, found), found.astype(np.uint8)


def mirror_fill(layer: np.ndarray, have: np.ndarray, where: np.ndarray, neutral: float | None = None,
                depth: tuple[float, float] = (24.0, 24.0)) -> np.ndarray:  # fmt: skip
    """A detail layer's holes (`where`, outside `have`) filled with the skin beside them, mirrored across the hole's
    edge - each hole texel takes the texel as far outside the edge as it is inside (reflection padding), so pores and
    fine lines carry on into it at their own size instead of a blur's smooth patch (the brows' and lash bands' holes:
    every scan has hair there). Where the mirror lands in another hole, the edge's own texel is taken - or, with
    `neutral` (a relief's 0: flat), the fill fades to `neutral` from `depth[0]` texels into the hole over `depth[1]` and
    is `neutral` where the mirror fails: a wide hole's edge texel streaked across it made wedges of constant tilt."""
    out = layer.astype(np.float32).copy()
    todo = where & ~have
    if not todo.any() or not have.any():
        return out
    src = np.where(have, 0, 1).astype(np.uint8)
    dist, labels = cv2.distanceTransformWithLabels(src, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    edge = np.argwhere(src == 0)  # label k is the k-th zero texel in raster order (OpenCV's numbering)
    ys, xs = np.nonzero(todo)
    q = edge[labels[ys, xs] - 1]
    my, mx = 2 * q[:, 0] - ys, 2 * q[:, 1] - xs
    h, w = have.shape
    inside = (my >= 0) & (my < h) & (mx >= 0) & (mx < w)
    ok = np.zeros(len(ys), bool)
    ok[inside] = have[my[inside], mx[inside]]
    sy, sx = np.where(ok, my, q[:, 0]), np.where(ok, mx, q[:, 1])
    if neutral is None:
        out[ys, xs] = layer[sy, sx]
        return out
    fade = np.clip(1.0 - (dist[ys, xs] - depth[0]) / depth[1], 0.0, 1.0) * ok
    fade = fade.reshape(-1, *([1] * (layer.ndim - 2)))
    out[ys, xs] = neutral + fade * (layer[sy, sx] - neutral)
    return out


def relief_debris(relief: np.ndarray, limit: float = 0.3, grow: int = 6) -> np.ndarray:
    """Where a scan's relief (tangent XY, high-passed) is debris: steeper than `limit` - rings round the scan's holes
    (nostrils, eyes), arcs and spikes at its edges; skin's folds stay well under it (gate run 7, the Average woman's
    gashes: her head relief's p99.5 0.5, its folds under 0.25) - and `grow` texels round it (their slopes' feet).
    A bool mask; the composer drops the scan there, another scan or the flat fill takes the place."""
    steep = (np.sqrt((relief.astype(np.float32) ** 2).sum(-1)) > limit).astype(np.uint8)
    if grow > 0:
        steep = cv2.dilate(steep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
    return steep.astype(bool)
