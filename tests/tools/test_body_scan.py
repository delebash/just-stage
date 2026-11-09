# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body scan route's helpers (tools/body_scan.py): the wrap's move smoothed keeps its broad shape and drops its
small-scale following of the scan (a foot's tendons stay for the bake), and a foot's vertices reach its toes on its
own side only. Run in the tool environment:

    .dev/venv-tools/Scripts/python -m pytest tests/tools/test_body_scan.py
"""

import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location(
    "body_scan", Path(__file__).resolve().parents[2] / "tools" / "body_scan.py"
)
body_scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(body_scan)


def _grid(n: int = 20, step: float = 0.008):
    """A flat n x n grid of vertices `step` m apart (a foot's top at hm08's spacing) and its triangles."""
    ys, xs = np.mgrid[0:n, 0:n]
    co = np.c_[xs.ravel() * step, ys.ravel() * step, np.zeros(n * n)]
    i = (ys[:-1, :-1] * n + xs[:-1, :-1]).ravel()
    tris = np.r_[np.c_[i, i + 1, i + n], np.c_[i + 1, i + n + 1, i + n]]
    return co, tris


def test_the_smoothed_move_keeps_the_broad_shape_and_drops_the_ridges():
    rest, tris = _grid()
    n = int(np.sqrt(len(rest)))
    ridges = np.where((np.arange(len(rest)) % n) % 2 == 0, 0.0015, -0.0015)  # +-1.5 mm alternating: tendon-scale
    co = rest.copy()
    co[:, 2] += 0.005 + ridges  # a 5 mm broad move plus the ridges the soft wrap followed
    moved = np.arange(len(rest))
    out = body_scan._smooth_move(rest, co, moved, tris, 10)
    lift = out[:, 2] - rest[:, 2]
    inner = (np.arange(len(rest)) % n > 2) & (np.arange(len(rest)) % n < n - 3)
    assert abs(np.mean(lift[inner]) - 0.005) < 0.0005  # the broad move kept
    assert np.std(lift[inner]) < 0.3 * np.std(ridges)  # the ridges mostly gone


def test_the_smoothed_move_leaves_unmoved_vertices_alone():
    rest, tris = _grid(6)
    co = rest + np.array([0.0, 0.0, 0.004])
    moved = np.arange(18)  # the first three rows only
    out = body_scan._smooth_move(rest, co, moved, tris, 5)
    assert np.allclose(out[18:], co[18:])


def test_a_debris_hole_takes_the_slope_round_it_not_a_flat_disc():
    n = 200
    hp = np.zeros((n, n, 2), np.float32)
    hp[..., 0] = 0.15  # a chest's broad slope
    yy, xx = np.mgrid[0:n, 0:n]
    ring = np.abs(np.hypot(yy - 100, xx - 100) - 10) < 1.5  # a ring at a scan's hole, far steeper
    hp[ring, 0] = 0.9
    out = body_scan._debris_filled(hp, 0.3)
    inside = np.hypot(yy - 100, xx - 100) < 14
    assert np.abs(out[inside, 0] - 0.15).max() < 0.05  # the slope carried in, the ring gone
    assert np.allclose(out[np.hypot(yy - 100, xx - 100) > 40], hp[np.hypot(yy - 100, xx - 100) > 40])


def test_a_foot_reaches_its_toes_on_its_own_side_only():
    ankle_r, ankle_l = np.array([-0.198, -0.015, 0.071]), np.array([0.198, -0.015, 0.071])
    co = np.array([
        [-0.198, -0.226, 0.009],  # the right big toe's tip, 0.21 m before the ankle (cut at the old 0.16 m reach)
        [-0.150, -0.100, 0.030],  # the right foot's top
        [0.150, -0.100, 0.030],   # the left foot's top
        [-0.198, -0.015, 0.200],  # the right shin, above the ankle
    ])  # fmt: skip
    o = {"joint_names": np.array(["joint-r-ankle", "joint-l-ankle"]), "joint_co": np.array([ankle_r, ankle_l]),
         "co": co}  # fmt: skip
    right = body_scan._foot_vertices(o, "r")
    assert right.tolist() == [True, True, False, False]
    assert body_scan._foot_vertices(o, "l").tolist() == [False, False, True, False]


def test_a_named_mark_takes_the_skin_round_it_level_and_texture():
    """A scanned person's own mark (Artec's man's scar, 2026-11-09) filled from the skin round it: its level, and texture
    copied from beside it - not a smooth disc, not a Telea star."""
    rng = np.random.default_rng(3)
    px_per_mm, n = 2.4, 300
    img = (0.5 + 0.05 * rng.normal(size=(n, n, 1))).astype(np.float32)
    yy, xx = np.mgrid[0:n, 0:n]
    mark = (yy - 150) ** 2 + (xx - 150) ** 2 < (10 * px_per_mm) ** 2
    img[mark] -= 0.3  # a dark dent
    out = body_scan._patched(img, mark, np.ones((n, n), bool), px_per_mm)
    inside, around = out[mark, 0], img[~mark, 0]
    assert abs(inside.mean() - around.mean()) < 0.02  # the skin's level
    assert inside.std() > 0.5 * around.std()  # its texture, not a flat fill
