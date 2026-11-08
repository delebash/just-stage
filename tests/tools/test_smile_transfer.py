# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The smile carry's pieces (tools/gate/smile_transfer.py): the similarity that starts the alignment, the openings
found as boundary loops, the landmarks picked round an opening. Run in the tool environment:

    .dev/venv-rdf/Scripts/python -m pytest tests/tools/test_smile_transfer.py
"""

import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location(
    "smile_transfer", Path(__file__).resolve().parents[2] / "tools" / "gate" / "smile_transfer.py")
st = importlib.util.module_from_spec(spec)
spec.loader.exec_module(st)


def test_the_similarity_recovers_a_known_turn_scale_and_shift():
    rng = np.random.default_rng(0)
    src = rng.normal(0, 0.05, (40, 3))
    a = np.radians(20)
    turn = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    dst = 0.95 * src @ turn.T + [0.01, -0.14, 1.6]
    m = st._similarity(src, dst)
    assert np.allclose(st._apply(m, src), dst, atol=1e-9)
    assert abs(np.cbrt(np.linalg.det(m[:3, :3])) - 0.95) < 1e-9


def _grid_with_hole(n: int = 12) -> np.ndarray:
    """A flat n x n grid of quads (as triangles) in the x-z plane with its 2 x 2 centre quads left out."""
    tris = []
    for i in range(n):
        for j in range(n):
            if n // 2 - 1 <= i <= n // 2 and n // 2 - 1 <= j <= n // 2:
                continue
            a, b, c, d = i * (n + 1) + j, i * (n + 1) + j + 1, (i + 1) * (n + 1) + j + 1, (i + 1) * (n + 1) + j
            tris += [[a, b, c], [a, c, d]]
    return np.array(tris)


def test_the_openings_are_the_meshs_boundary_loops():
    loops = sorted(st._boundary_loops(_grid_with_hole()), key=len)
    assert [len(lp) for lp in loops] == [8, 48]  # the hole's ring of 8 edges, the outer border's 4 x 12


def test_the_landmarks_go_round_the_opening_at_even_angles():
    ang = np.linspace(0, 2 * np.pi, 90, endpoint=False)
    ring = np.c_[np.cos(ang), np.zeros_like(ang), np.sin(ang)] * 0.012
    picked = st._round(ring, np.zeros(3), 6)
    got = np.sort(np.degrees(np.arctan2(ring[picked, 2], ring[picked, 0])) % 360)
    assert np.allclose(got, [0, 60, 120, 180, 240, 300], atol=2.1)
