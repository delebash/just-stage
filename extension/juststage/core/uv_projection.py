# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Projecting pictures taken from cameras back onto a mesh's UV texture — numpy only.

The texture-projection way 3D painting tools and StableGen texture a model: every texel of the UV map gets its 3D point
and normal (the mesh's triangles drawn in UV space), each camera sees that point at a pixel of its picture (Blender's
perspective camera: it looks down its −Z, the sensor width spans the image's width), a view counts only where its depth
picture shows that point and not something in front of it, and views blend weighted by how squarely they see the
surface (the cosine to the power `sharpness`).
"""

from __future__ import annotations

import numpy as np


def raster_uv(uv: np.ndarray, values: list[np.ndarray], size: int) -> tuple[list[np.ndarray], np.ndarray]:
    """Draw triangles in UV space: `uv` (T×3×2, 0–1) and per-corner `values` (each T×3×C) → per-texel values
    (size×size×C, row 0 at v = 1, the way images are stored) interpolated barycentrically, and the covered mask."""
    out = [np.zeros((size, size, v.shape[2]), dtype=np.float32) for v in values]
    mask = np.zeros((size, size), dtype=bool)
    px = uv * size - 0.5  # texel centres at integer coordinates
    for t in range(len(uv)):
        (x0, y0), (x1, y1), (x2, y2) = px[t]
        xmin, xmax = int(np.floor(min(x0, x1, x2))), int(np.ceil(max(x0, x1, x2)))
        ymin, ymax = int(np.floor(min(y0, y1, y2))), int(np.ceil(max(y0, y1, y2)))
        xmin, ymin, xmax, ymax = max(xmin, 0), max(ymin, 0), min(xmax, size - 1), min(ymax, size - 1)
        if xmin > xmax or ymin > ymax:
            continue
        gx, gy = np.meshgrid(np.arange(xmin, xmax + 1), np.arange(ymin, ymax + 1))
        det = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(det) < 1e-12:
            continue
        l0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / det
        l1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / det
        l2 = 1.0 - l0 - l1
        inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not inside.any():
            continue
        rows = size - 1 - gy[inside]  # v up → image rows down
        cols = gx[inside]
        bary = np.stack([l0[inside], l1[inside], l2[inside]], axis=1)
        for o, v in zip(out, values, strict=True):
            o[rows, cols] = bary @ v[t]
        mask[rows, cols] = True
    return out, mask


def project(points: np.ndarray, matrix_world: np.ndarray, lens: float, sensor_width: float, size: int):
    """Blender camera → (column, row) pixel coordinates of each point (row 0 at the top) and its distance from the
    camera; points behind the camera get NaN coordinates."""
    inv = np.linalg.inv(np.asarray(matrix_world, dtype=np.float64))
    cam = (inv @ np.c_[points, np.ones(len(points))].T).T[:, :3]
    focal_px = lens / sensor_width * size
    depth = -cam[:, 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        col = size / 2.0 + focal_px * cam[:, 0] / depth - 0.5
        row = size / 2.0 - focal_px * cam[:, 1] / depth - 0.5
    behind = depth <= 0
    col[behind] = row[behind] = np.nan
    return col, row, np.linalg.norm(cam, axis=1)


def sample(image: np.ndarray, col: np.ndarray, row: np.ndarray) -> np.ndarray:
    """Bilinear samples of an H×W×C image at fractional pixels (clamped to its edge)."""
    h, w = image.shape[:2]
    c = np.clip(np.nan_to_num(col), 0, w - 1.001)
    r = np.clip(np.nan_to_num(row), 0, h - 1.001)
    c0, r0 = c.astype(int), r.astype(int)
    fc, fr = (c - c0)[:, None], (r - r0)[:, None]
    top = image[r0, c0] * (1 - fc) + image[r0, c0 + 1] * fc
    bottom = image[r0 + 1, c0] * (1 - fc) + image[r0 + 1, c0 + 1] * fc
    return top * (1 - fr) + bottom * fr


def view_weights(points, normals, col, row, distance, depth_image, camera_position, sharpness=4.0, tolerance=0.003):
    """How much one view counts at each point: visible in its depth picture (within `tolerance` metres), facing it,
    and the cosine between the surface normal and the direction to the camera to the power `sharpness`."""
    h, w = depth_image.shape[:2]
    inside = (col >= 0) & (col <= w - 1) & (row >= 0) & (row <= h - 1)
    seen = sample(depth_image[..., None] if depth_image.ndim == 2 else depth_image[..., :1], col, row)[:, 0]
    visible = inside & (np.abs(seen - distance) < tolerance)
    to_camera = np.asarray(camera_position) - points
    to_camera /= np.linalg.norm(to_camera, axis=1, keepdims=True)
    facing = np.clip(np.einsum("ij,ij->i", normals, to_camera), 0.0, 1.0)
    return np.where(visible, facing**sharpness, 0.0)
