# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face's relief read from a scan's colour (tools/face_test/colour_relief.py) and its place in the composer
(skin_base._colour_relief): a known groove's normals give back its depth, the tangent XY points the way the bake's
does, dots go and lines stay, and each texel's lines come from one scan - the heaviest. Run in the tool environment:

    .dev/venv-rdf/Scripts/python -m pytest tests/tools/test_colour_relief.py
"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / "face_test" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


colour_relief = _load("colour_relief")
skin_base = _load("skin_base")
MM = 4096 / 724.0  # texels a mm on the head tile


def _normals_of(z):
    """Normals (x right, y up, z out) of a height on a grid of MM texels a mm (rows top first)."""
    dz_dx = np.gradient(z, axis=1) * MM
    dz_dy_up = -np.gradient(z, axis=0) * MM
    n = np.dstack([-dz_dx, -dz_dy_up, np.ones_like(z)])
    return (n / np.linalg.norm(n, axis=2, keepdims=True)).astype(np.float32)


def test_a_grooves_normals_give_back_its_depth():
    h, w = 400, 300
    x = (np.arange(w) - w / 2) / MM
    groove = -0.3 * np.exp(-(x**2) / (2 * 0.5**2))  # 0.3 mm deep, ~1 mm wide
    z = np.tile(groove, (h, 1)).astype(np.float32)
    got = colour_relief.fine_height(_normals_of(z), MM)
    middle = got[h // 2]
    floor = middle[w // 2]
    assert -0.36 < floor < -0.2, floor  # its depth, within the fine cut's loss
    assert abs(middle[10]) < 0.05 and abs(middle[-10]) < 0.05  # flat skin stays flat


def test_the_tangent_xy_points_as_the_bake_s_does():
    h, w = 64, 64
    ramp_right = np.tile(np.arange(w) / MM * 0.1, (h, 1)).astype(np.float32)  # rises 0.1 mm a mm to the right
    xy = colour_relief.tangent_xy(ramp_right, MM)
    assert xy[32, 32, 0] == pytest.approx(-0.1 / np.sqrt(1.01), abs=0.005)
    assert abs(xy[32, 32, 1]) < 1e-4
    ramp_up = ramp_right.T[::-1].copy()  # rises up the picture (+V)
    xy = colour_relief.tangent_xy(ramp_up, MM)
    assert xy[32, 32, 1] == pytest.approx(-0.1 / np.sqrt(1.01), abs=0.005)


def test_dots_go_and_lines_stay():
    z = np.zeros((300, 300), np.float32)
    yy, xx = np.mgrid[0:300, 0:300]
    z[(yy - 60) ** 2 + (xx - 60) ** 2 < (0.4 * MM) ** 2] = -0.2  # a pit ~0.5 mm2 (a follicle)
    z[200:206, 40:260] = -0.2  # a crease ~39 mm long, 1 mm wide
    got = colour_relief.remove_dots(z, MM)
    assert abs(got[60, 60]) < 0.01
    assert got[203, 150] < -0.15


def test_each_texels_lines_come_from_the_heaviest_scan(tmp_path, monkeypatch):
    shape = (64, 64)
    for name, value in (("heavy", 0.05), ("light", -0.05)):
        (tmp_path / name).mkdir()
        xy = np.zeros((*shape, 2), np.float32)
        xy[..., 0] = value
        if name == "heavy":
            xy[:, 40:] = 0.0  # its colour gave nothing on the right
        np.save(tmp_path / name / "colour_relief.npy", xy.astype(np.float16))
    monkeypatch.setattr(skin_base, "DIR", tmp_path)
    monkeypatch.setattr(skin_base, "RELIEF_FEATHER", 1.0)
    got = skin_base._colour_relief({"light": 0.3, "heavy": 0.7}, shape)
    assert got[32, 10, 0] == pytest.approx(0.05 * skin_base.COLOUR_RELIEF, abs=0.002)  # the heavy one's, not a mean
    assert got[32, 60, 0] == pytest.approx(-0.05 * skin_base.COLOUR_RELIEF, abs=0.002)  # the next where it didn't reach
