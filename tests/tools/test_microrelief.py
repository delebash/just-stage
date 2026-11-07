# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The layered microrelief (tools/make_microrelief.py `layered`, 2026-11-07): its slope sits where HD Aaron's micro
normal's does - most at 0.25-0.6 mm (pillowed cells), little finer than 0.1 mm (his 5%; the 11-05 tile's thin walls put
31% there) - and it tiles without a seam. Run in the tool environment:

    .dev/venv-rdf/Scripts/python -m pytest tests/tools/test_microrelief.py
"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location(
    "make_microrelief", Path(__file__).resolve().parents[2] / "tools" / "make_microrelief.py"
)
make_microrelief = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make_microrelief)

TILE_MM, PX = 5.0, 512  # 102 px/mm, as the sweep's tiles


@pytest.fixture(scope="module")
def tile():
    return make_microrelief.layered(TILE_MM, PX, seed=2, angle_deg=35.0)


def _slope_share(h: np.ndarray, lo_mm: float, hi_mm: float) -> float:
    px_mm = h.shape[0] / TILE_MM
    gy, gx = np.gradient(h * px_mm)
    f = np.abs(np.fft.fft2(gx)) ** 2 + np.abs(np.fft.fft2(gy)) ** 2
    fr = np.fft.fftfreq(h.shape[0], 1 / px_mm)
    r = np.hypot(fr[:, None], fr[None, :])
    return float(f[(r > 1 / hi_mm) & (r <= 1 / lo_mm)].sum() / f[r > 0].sum())


def test_the_slope_sits_in_pillowed_cells_not_thin_walls(tile):
    # measured at this density 2026-11-07: 0.04 / 0.42 / 0.38 / 0.15 (0.005-0.1 / -0.25 / -0.6 / -1.5 mm); Aaron's
    # 0.05 / 0.29 / 0.51 / 0.14; the 11-05 tile 0.31 / 0.55 / 0.15 / 0.00 - still more at 0.1-0.25 mm than his
    assert _slope_share(tile, 0.25, 0.6) > 0.35
    assert _slope_share(tile, 0.6, 1.5) > 0.10  # the cells' tilt and lift: none on the 11-05 tile
    assert _slope_share(tile, 0.005, 0.1) < 0.08


def test_it_tiles_without_a_seam(tile):
    step = np.abs(np.diff(tile, axis=1)).mean()
    across = np.abs(tile[:, 0] - tile[:, -1]).mean()
    assert across < 3 * step
    step = np.abs(np.diff(tile, axis=0)).mean()
    assert np.abs(tile[0] - tile[-1]).mean() < 3 * step
