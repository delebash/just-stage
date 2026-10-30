# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Skin colour from its chromophores — R5's "physically based melanin and haemoglobin layers", Blender-free.

The absorption and scattering are Donner & Jensen's two-layer skin model ("A Spectral BSSRDF for Shading Human Skin",
EGSR 2006, §3.3–§3.5): an epidermis of melanin (eumelanin and pheomelanin, power laws, eq. 3–4) over baseline tissue
(eq. 5), 0.25 mm thick, on a semi-infinite dermis of oxy- and deoxy-haemoglobin at oxygenation 0.75 (eq. 7), with
reduced scattering from eq. 8 (halved in the dermis). Haemoglobin's spectra are Prahl's molar extinction tables
(OMLC, 1998) for whole blood at 150 g/L. Their diffusion step (the multipole) is replaced by Kubelka–Munk for the two
layers, with one calibrated constant: the epidermis's backscatter is EPIDERMIS_BACKSCATTER × Kubelka–Munk's usual
0.75σs'. Fitted to NIST's measured reflectance of 100 people (Cooksey, Allen & Tsai 2017, J. Res. NIST 122:26,
doi:10.18434/M38597, public domain) over 400–700 nm, 0.22 gives a mean RMS error of 0.0098 and a worst of 0.020 in
reflectance (tools/calibrate_skin.py, 2026-10-29); plain Kubelka–Munk (1.0) gives 0.039, and a pure absorbing epidermis
over-darkens. The per-channel subsurface radius comes from the dermis's diffusion length. The spectrum is turned into
linear Rec.709 (Blender's scene-linear) under CIE D65 with the CIE 1931 2° observer.
"""

from __future__ import annotations

import csv
import functools
import math
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

WAVELENGTHS = np.arange(380.0, 781.0, 5.0)  # nm
EPIDERMIS_MM = 0.25
#: calibrated on NIST's 100 measured skins (see the module docstring)
EPIDERMIS_BACKSCATTER = 0.22
OXYGENATION = 0.75
BLOOD_G_PER_L = 150.0
HEMOGLOBIN_G_PER_MOL = 64500.0
#: XYZ → linear sRGB / Rec.709 (IEC 61966-2-1)
XYZ_TO_REC709 = np.array(
    [[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]],
)
#: wavelengths standing for Blender's red, green and blue subsurface channels
RGB_NM = (680.0, 550.0, 450.0)


@dataclass(frozen=True)
class Tables:
    hb_oxy: np.ndarray  # absorption of whole blood, mm⁻¹, on WAVELENGTHS
    hb_deoxy: np.ndarray
    xyz: np.ndarray  # (len, 3)
    d65: np.ndarray


def _interp(nm, values) -> np.ndarray:
    return np.interp(WAVELENGTHS, nm, values)


@functools.cache
def load_tables(folder: Path) -> Tables:
    """Prahl's haemoglobin table and the CIE tables, as fetched by tools/fetch_data.py."""
    rows = re.findall(r"^(\d{3})\t([\d.]+)\t([\d.]+)", (folder / "prahl_hemoglobin.html").read_text("utf-8"), re.M)
    nm = np.array([float(r[0]) for r in rows])
    # molar extinction (cm⁻¹/M) → absorption of whole blood (mm⁻¹): 2.303 · ε · (150 g/L ÷ 64,500 g/mol) ÷ 10
    to_mm = 2.303 * BLOOD_G_PER_L / HEMOGLOBIN_G_PER_MOL / 10.0
    oxy = _interp(nm, [float(r[1]) * to_mm for r in rows])
    deoxy = _interp(nm, [float(r[2]) * to_mm for r in rows])

    def table(name: str, columns: int) -> tuple[np.ndarray, np.ndarray]:
        with open(folder / name, newline="", encoding="utf-8") as f:
            data = np.array([[float(x) for x in row[: columns + 1]] for row in csv.reader(f) if row])
        return data[:, 0], data[:, 1:]

    cmf_nm, cmf = table("CIE_xyz_1931_2deg.csv", 3)
    d65_nm, d65 = table("CIE_std_illum_D65.csv", 1)
    xyz = np.stack([_interp(cmf_nm, cmf[:, i]) for i in range(3)], axis=1)
    return Tables(oxy, deoxy, xyz, _interp(d65_nm, d65[:, 0]))


def eumelanin(nm):
    return 6.6e10 * nm**-3.33  # mm⁻¹, Donner & Jensen eq. 3


def pheomelanin(nm):
    return 2.9e14 * nm**-4.75  # eq. 4


def baseline(nm):
    return 0.0244 + 8.53 * np.exp(-(nm - 154.0) / 66.2)  # eq. 5


def reduced_scattering(nm):
    return 14.74 * nm**-0.22 + 2.2e11 * nm**-4.0  # eq. 8


def _km_coefficients(absorption, scattering):
    # the usual mapping from transport coefficients to Kubelka–Munk's K and S
    return 2.0 * absorption, 0.75 * scattering


def _km_slab(k, s, d):
    """Kubelka–Munk reflectance and transmittance of a slab of thickness d."""
    a = 1.0 + k / s
    b = np.sqrt(a * a - 1.0)
    bsd = b * s * d
    denom = a * np.sinh(bsd) + b * np.cosh(bsd)
    return np.sinh(bsd) / denom, b / denom


def _km_infinite(k, s):
    ratio = k / s
    return 1.0 + ratio - np.sqrt(ratio * ratio + 2.0 * ratio)


@dataclass(frozen=True)
class Skin:
    melanin: float = 0.05  # Cm, the epidermis's melanin volume fraction (0–0.5)
    eumelanin: float = 0.7  # βm, eumelanin's share of it (0–1)
    blood: float = 0.01  # Ch, the dermis's haemoglobin fraction (0.001–0.2)

    def absorption(self, t: Tables) -> tuple[np.ndarray, np.ndarray]:
        nm = WAVELENGTHS
        mel = self.eumelanin * eumelanin(nm) + (1.0 - self.eumelanin) * pheomelanin(nm)
        epidermis = self.melanin * mel + (1.0 - self.melanin) * baseline(nm)  # eq. 6
        hb = OXYGENATION * t.hb_oxy + (1.0 - OXYGENATION) * t.hb_deoxy
        dermis = self.blood * hb + (1.0 - self.blood) * baseline(nm)  # eq. 7
        return epidermis, dermis

    def reflectance(self, t: Tables, backscatter: float = EPIDERMIS_BACKSCATTER) -> np.ndarray:
        """Diffuse spectral reflectance of the two layers (Kubelka–Munk adding)."""
        epidermis, dermis = self.absorption(t)
        scattering = reduced_scattering(WAVELENGTHS)
        k1, s1 = _km_coefficients(epidermis, scattering)
        r1, t1 = _km_slab(k1, s1 * backscatter, EPIDERMIS_MM)
        r2 = _km_infinite(*_km_coefficients(dermis, 0.5 * scattering))
        return r1 + t1 * t1 * r2 / (1.0 - r1 * r2)

    def linear_rgb(self, t: Tables) -> tuple[float, float, float]:
        """The diffuse colour in Blender's scene-linear Rec.709, under D65."""
        r = self.reflectance(t)
        weight = t.d65[:, None] * t.xyz
        xyz = (r[:, None] * weight).sum(axis=0) / weight[:, 1].sum()
        rgb = np.clip(XYZ_TO_REC709 @ xyz, 0.0, 1.0)
        return tuple(float(c) for c in rgb)

    def subsurface_radius_mm(self, t: Tables) -> tuple[float, float, float]:
        """The dermis's diffusion length 1/σ_tr at the red, green and blue wavelengths (mm), σ_tr = √(3σa(σa+σs'))."""
        _, dermis = self.absorption(t)
        scattering = 0.5 * reduced_scattering(WAVELENGTHS)
        out = []
        for nm in RGB_NM:
            a = float(np.interp(nm, WAVELENGTHS, dermis))
            s = float(np.interp(nm, WAVELENGTHS, scattering))
            out.append(1.0 / math.sqrt(3.0 * a * (a + s)))
        return tuple(out)
