# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Calibrate the skin colour model on NIST's measured skin and keep each person's fit as a tone preset.

    .dev/venv-tools/Scripts/python tools/calibrate_skin.py   (after python tools/fetch_data.py)

NIST's "Reference Data Set of Human Skin Reflectance" (Cooksey, Allen & Tsai 2017, doi:10.18434/M38597, public domain)
holds 100 people's directional-hemispherical reflectance, 250–2500 nm. For each candidate epidermal backscatter, the
model's melanin, eumelanin share and blood are fitted to every person's average spectrum over 400–700 nm (SciPy's
least squares); the backscatter with the lowest mean error is the model's constant. Writes
`data/generated/skin/nist_fits.json`: the error per backscatter, and each person's fitted values and colour — real
people's skin, as presets for the skin generator.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extension"))
from juststage.core import skin_optics as so  # noqa: E402

NIST = ROOT / ".dev" / "cache" / "nist" / "1832_Data_JResNIST_skinrefl v3.txt"
OPTICS = ROOT / "extension" / "juststage" / "data" / "fetched" / "optics"
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "skin"
BACKSCATTER_GRID = [round(x, 2) for x in np.arange(0.10, 0.42, 0.02)]


def measured() -> np.ndarray:
    """(wavelengths of the model, people) — each person's average spectrum."""
    with open(NIST, encoding="utf-8", errors="replace", newline="") as f:
        rows = [r for r in csv.reader(f) if r and r[0].strip()[:1].isdigit()]
    data = np.array([[float(c) if c.strip() else np.nan for c in r[:401]] for r in rows])
    nm, average = data[:, 0], data[:, 4::4][:, :100]
    return np.stack([np.interp(so.WAVELENGTHS, nm, average[:, p]) for p in range(average.shape[1])], axis=1)


def main() -> int:
    tables = so.load_tables(OPTICS)
    spectra = measured()
    visible = (so.WAVELENGTHS >= 400) & (so.WAVELENGTHS <= 700)

    def fit(person: int, backscatter: float):
        def residual(p):
            return (so.Skin(*p).reflectance(tables, backscatter) - spectra[:, person])[visible]

        r = least_squares(residual, x0=[0.02, 0.6, 0.015], bounds=([0.0005, 0.0, 0.0005], [0.6, 1.0, 0.3]))
        return r.x, float(np.sqrt(np.mean(r.fun**2)))

    grid = {}
    for b in BACKSCATTER_GRID:
        errors = [fit(p, b)[1] for p in range(spectra.shape[1])]
        grid[b] = {"rmse_mean": float(np.mean(errors)), "rmse_max": float(np.max(errors))}
    best = min(grid, key=lambda b: grid[b]["rmse_mean"])
    people = []
    for p in range(spectra.shape[1]):
        (cm, bm, ch), err = fit(p, best)
        skin = so.Skin(float(cm), float(bm), float(ch))
        people.append(
            {
                "subject": p + 1,
                "melanin": skin.melanin,
                "eumelanin": skin.eumelanin,
                "blood": skin.blood,
                "rmse": err,
                "linear_rgb": skin.linear_rgb(tables),
            }
        )
    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "source": "NIST Reference Data Set of Human Skin Reflectance, doi:10.18434/M38597 (public domain)",
        "range_nm": [400, 700],
        "backscatter_grid": grid,
        "best_backscatter": best,
        "model_constant": so.EPIDERMIS_BACKSCATTER,
        "people": people,
    }
    (OUT / "nist_fits.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"best_backscatter": best, **grid[best], "model_constant": so.EPIDERMIS_BACKSCATTER}, indent=2))
    return 0 if abs(best - so.EPIDERMIS_BACKSCATTER) < 0.011 else 1


if __name__ == "__main__":
    sys.exit(main())
