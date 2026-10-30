# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The skin colour model: it reproduces NIST's measured skin (tools/calibrate_skin.py's fits) and behaves the way
Donner & Jensen's figures 3 and 4 show — more melanin goes from light to dark skin, more blood from pale to pink."""

import csv
import json
from pathlib import Path

import numpy as np
import pytest

from juststage.core import skin_optics

ROOT = Path(__file__).resolve().parents[2]
OPTICS = ROOT / "extension" / "juststage" / "data" / "fetched" / "optics"
FITS = ROOT / "extension" / "juststage" / "data" / "generated" / "skin" / "nist_fits.json"
NIST = ROOT / ".dev" / "cache" / "nist" / "1832_Data_JResNIST_skinrefl v3.txt"
pytestmark = pytest.mark.skipif(not (OPTICS / "prahl_hemoglobin.html").exists(), reason="run tools/fetch_data.py")


@pytest.fixture(scope="module")
def tables():
    return skin_optics.load_tables(OPTICS)


def luminance(rgb):
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


@pytest.mark.skipif(not (FITS.exists() and NIST.exists()), reason="run tools/calibrate_skin.py")
def test_it_reproduces_measured_skin(tables):
    fits = json.loads(FITS.read_text(encoding="utf-8"))
    assert fits["best_backscatter"] == pytest.approx(skin_optics.EPIDERMIS_BACKSCATTER, abs=0.011)
    with open(NIST, encoding="utf-8", errors="replace", newline="") as f:
        rows = np.array(
            [
                [float(c) if c.strip() else np.nan for c in r[:401]]
                for r in csv.reader(f)
                if r and r[0].strip()[:1].isdigit()
            ]
        )
    visible = (skin_optics.WAVELENGTHS >= 400) & (skin_optics.WAVELENGTHS <= 700)
    for person in fits["people"][::10]:
        measured = np.interp(skin_optics.WAVELENGTHS, rows[:, 0], rows[:, 4 * person["subject"]])
        skin = skin_optics.Skin(person["melanin"], person["eumelanin"], person["blood"])
        error = np.sqrt(np.mean((skin.reflectance(tables) - measured)[visible] ** 2))
        assert error < 0.025, person["subject"]


def test_light_skin_is_warm_and_bright(tables):
    # about the median of NIST's 100 people
    r, g, b = skin_optics.Skin(melanin=0.0104, eumelanin=0.6, blood=0.016).linear_rgb(tables)
    assert r > g > b
    assert 0.2 < luminance((r, g, b)) < 0.7


def test_more_melanin_is_darker(tables):
    lum = [
        luminance(skin_optics.Skin(melanin=c, eumelanin=0.7, blood=0.005).linear_rgb(tables))
        for c in (0.001, 0.01, 0.05, 0.1, 0.2, 0.5)
    ]
    assert lum == sorted(lum, reverse=True)
    assert lum[0] > 4 * lum[-1]


def test_more_blood_is_pinker(tables):
    def redness(ch):
        r, g, _ = skin_optics.Skin(melanin=0.01, eumelanin=0.5, blood=ch).linear_rgb(tables)
        return r / g

    assert redness(0.1) > redness(0.01) > redness(0.001)


def test_red_light_travels_furthest(tables):
    r, g, b = skin_optics.Skin().subsurface_radius_mm(tables)
    assert r > g > b > 0
    assert 0.3 < r < 10.0
