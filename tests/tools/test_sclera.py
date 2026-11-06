# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The sclera's veins (tools/make_sclera.py, rec 12): grown from seeds by our own rules, deeper ones bluer and
blurrier, more at the corners than above and below (the CCLRU redness grades by region), thinning toward the limbus.
Run in the tool environment:

    .dev/venv-rdf/Scripts/python -m pytest tests/tools/test_sclera.py
"""

import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location(
    "make_sclera", Path(__file__).resolve().parents[2] / "tools" / "make_sclera.py"
)
make_sclera = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make_sclera)


def _band(m, lo, hi):
    """Rows of the polar map between `lo` and `hi` limbus radii."""
    r = make_sclera.radius_of_rows(m.shape[0])
    return m[(r >= lo) & (r < hi)]


def test_veins_cover_the_white_lightly_more_at_the_corners():
    m = make_sclera.veins(seed=1)
    assert m.shape == (make_sclera.H, make_sclera.W, 3)
    assert m.min() >= 0.0 and m.max() <= 1.0001
    vessel = m.min(axis=2) < 0.97
    seen = _band(vessel, 1.1, 2.0)
    assert 0.02 < seen.mean() < 0.15  # a white with veins, not a red eye
    angle = (np.arange(make_sclera.W) + 0.5) / make_sclera.W * 2 * np.pi
    corners = np.abs(np.cos(angle)) > np.cos(np.radians(30))
    above_below = np.abs(np.sin(angle)) > np.cos(np.radians(30))
    assert seen[:, corners].mean() > 1.5 * seen[:, above_below].mean()
    assert _band(vessel, 1.0, 1.04).mean() < 0.02  # thinning out before the limbus


def test_deep_vessels_are_bluer_and_superficial_ones_redder():
    m = make_sclera.veins(seed=1)
    dark = m.min(axis=2) < 0.95  # deep vessels are faint (x0.91 at their darkest)
    red = dark & (m[..., 0] > m[..., 2] + 0.05)
    blue = dark & (m[..., 2] > m[..., 0] + 0.02)
    assert red.sum() > 0 and blue.sum() > 0
    assert red.sum() > blue.sum()  # the superficial net is most of what shows
