# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The gate's measures (tools/gate/measure.py): detail lands in the band of its real size, ridges read as ridges,
and a window's numbers are steady when it moves a little. Run in the tool environment:

    .dev/venv-tools/Scripts/python -m pytest tests/tools/test_measure.py
"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location(
    "measure", Path(__file__).resolve().parents[2] / "tools" / "gate" / "measure.py"
)
measure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure)

MM_PER_PX = 0.03  # the cheek view: 60 mm over 2048 px


def _grating(wavelength_mm: float, amplitude: float, n: int = 512, scale: float = MM_PER_PX) -> np.ndarray:
    x = np.arange(n) * scale
    return 50.0 + amplitude * np.sin(2 * np.pi * x / wavelength_mm)[None, :].repeat(n, 0)


@pytest.mark.parametrize(("wavelength", "band", "scale"),
                         [(0.15, "micro", MM_PER_PX), (0.8, "pore", MM_PER_PX), (3.0, "fold", MM_PER_PX),
                          (12.0, "form", 0.12)])  # fmt: skip
def test_detail_lands_in_the_band_of_its_real_size(wavelength, band, scale):
    bands = measure.band_rms(_grating(wavelength, 4.0, scale=scale), scale)
    assert bands[band] == pytest.approx(4.0 / np.sqrt(2), rel=0.1)  # a sine's RMS
    assert all(v < 0.3 for k, v in bands.items() if k != band and v is not None)


def test_a_band_finer_than_two_pixels_is_not_resolved():
    bands = measure.band_rms(_grating(3.0, 4.0), 0.27)  # the torso view: 560 mm over 2048 px
    assert bands["micro"] is None and bands["pore"] is None and bands["fold"] is not None


def test_a_crease_reads_as_a_dark_ridge_and_speckle_does_not():
    rng = np.random.default_rng(1)
    n = 400
    speckle = 60.0 + rng.normal(0, 3, (n, n))
    crease = speckle.copy()
    cols = np.arange(n) * MM_PER_PX
    crease -= 15.0 * np.exp(-0.5 * ((cols - 6.0) / 0.8) ** 2)[None, :]  # a 2 mm wide dark line down the middle
    flat, line = measure.ridges(speckle, MM_PER_PX), measure.ridges(crease, MM_PER_PX)
    assert line["dark"] > 0.01 and flat["dark"] < 0.001
    assert line["dark"] > line["light"]


def test_a_windows_numbers_are_steady_when_it_moves():
    rng = np.random.default_rng(2)
    n = 600
    lum = 55.0 + rng.normal(0, 2, (n, n))  # an even texture
    rgb = np.repeat(((lum + 16) / 116) ** 3, 3).reshape(n, n, 3)  # its L* back to linear grey
    rgb = np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * rgb ** (1 / 2.4) - 0.055)  # and to display sRGB
    spread = measure.repeatability(rgb, (0.3, 0.7, 0.3, 0.7), MM_PER_PX)
    assert spread and spread["lab.0"] < 0.01 and spread["bands.pore"] < 0.05


def test_the_backdrop_in_a_window_gives_no_numbers():
    rgb = np.zeros((200, 200, 3))
    rgb[:, 100:] = 0.6
    assert set(measure.window_measures(rgb, (0.0, 1.0, 0.0, 1.0), MM_PER_PX)) == {"cover"}


def test_a_band_longer_than_half_the_window_is_not_resolved():
    bands = measure.band_rms(_grating(12.0, 4.0, n=300), MM_PER_PX)  # a 9 mm window
    assert bands["form"] is None and bands["fold"] is not None
