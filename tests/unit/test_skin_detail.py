# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The skin detail's maths: a photo's fine relief kept, its shading dropped, the result tiling without a seam."""

import numpy as np

from juststage.core import skin_detail


def _photo(seed=0, n=512):
    """A stand-in skin photo: fine noise (the pores) over a strong left-to-right shading and a colour cast."""
    rng = np.random.default_rng(seed)
    fine = skin_detail.gaussian_blur(rng.standard_normal((n, n)), 1.5)
    shading = np.linspace(0.3, 0.9, n)[None, :] * np.ones((n, 1))
    lum = shading + 0.05 * fine / fine.std()
    return np.stack([lum * 1.1, lum, lum * 0.8], axis=2), fine


def test_the_relief_keeps_the_fine_detail_and_drops_the_shading():
    photo, fine = _photo()
    high = skin_detail.relief(photo, crop=1.0, sigma_px=12.0)
    assert abs(high.mean()) < 1e-9
    assert np.corrcoef(high.ravel(), fine.ravel())[0, 1] > 0.9  # the pores survive, the gradient doesn't
    assert np.abs(np.polyfit(np.arange(high.shape[1]), high.mean(axis=0), 1)[0]) < 1e-5


def test_the_height_map_tiles_and_fills_its_range():
    photo, _ = _photo(1)
    before = skin_detail.relief(photo)
    height = skin_detail.height_map(photo)
    assert skin_detail.wrap_ratio(before) > 2.0  # a crop of a photo doesn't tile (2.9 here)
    assert skin_detail.wrap_ratio(height) < 1.5
    assert height.dtype == np.float32 and 0.0 <= height.min() and height.max() <= 1.0
    assert abs(float(height.mean()) - 0.5) < 0.02
    assert 0.1 < float(height.std()) < 0.25  # ±3 standard deviations fill the range


def test_the_blend_keeps_the_contrast():
    rng = np.random.default_rng(2)
    noise = skin_detail.gaussian_blur(rng.standard_normal((256, 256)), 1.0)
    tile = skin_detail.make_seamless(noise - noise.mean())
    bands = tile.reshape(8, 32, 256).std(axis=(1, 2))  # eight bands of rows, edge to middle and back
    assert bands.min() > 0.85 * bands.max()  # no washed-out band where the two copies meet
