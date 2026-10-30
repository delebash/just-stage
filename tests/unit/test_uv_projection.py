# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Texture projection's maths: triangles drawn in UV space, Blender's camera, depth-tested and facing-weighted views."""

import numpy as np

from juststage.core import uv_projection as up


def _look_at(eye, target):
    """A Blender camera's world matrix looking from `eye` at `target` (its −Z forward, +Y up)."""
    eye, target = np.asarray(eye, float), np.asarray(target, float)
    back = eye - target
    back /= np.linalg.norm(back)
    right = np.cross([0, 0, 1], back)
    right /= np.linalg.norm(right)
    up_ = np.cross(back, right)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = right, up_, back, eye
    return m


def test_a_triangle_fills_its_texels_with_interpolated_values():
    uv = np.array([[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]])
    pos = np.array([[[0, 0, 0], [1, 0, 0], [0, 1, 0]]], dtype=float)
    (p,), mask = up.raster_uv(uv, [pos], 64)
    assert 0.45 < mask.mean() < 0.55  # half the square
    row, col = 63 - 10, 20  # texel at u ≈ 20.5/64, v ≈ 10.5/64
    assert np.allclose(p[row, col], [(col + 0.5) / 64, (10 + 0.5) / 64, 0], atol=1e-6)


def test_the_camera_sees_its_target_at_the_middle():
    m = _look_at([0, -1, 0], [0, 0, 0])
    col, row, dist = up.project(np.array([[0.0, 0.0, 0.0], [0.1, 0.0, 0.0], [0.0, 0.0, 0.1]]), m, 50, 36, 1000)
    assert np.allclose([col[0], row[0], dist[0]], [499.5, 499.5, 1.0])
    assert col[1] > col[0]  # +X is to the right
    assert row[2] < row[0]  # +Z is up, so a smaller row
    assert np.isclose(col[1] - col[0], 50 / 36 * 1000 * 0.1, rtol=1e-6)


def test_a_hidden_or_turned_away_point_gets_no_weight():
    m = _look_at([0, -1, 0], [0, 0, 0])
    points = np.array([[0.0, 0.0, 0.0], [0.0, 0.05, 0.0], [0.0, 0.0, 0.0]])
    normals = np.array([[0.0, -1.0, 0.0], [0.0, -1.0, 0.0], [0.0, 1.0, 0.0]])  # facing, facing, turned away
    col, row, dist = up.project(points, m, 50, 36, 100)
    depth = np.full((100, 100), 1.0)  # the depth picture sees a surface 1 m away: point 2 (1.05 m) is behind it
    w = up.view_weights(points, normals, col, row, dist, depth, [0, -1, 0])
    assert w[0] == 1.0 and w[1] == 0.0 and w[2] == 0.0
