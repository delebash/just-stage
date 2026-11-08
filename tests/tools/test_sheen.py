# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face's sheen reader (tools/gate/sheen.py): a Blender-named multilayer EXR with known specular and diffuse light
reads back their share, and a scattered glint reads a wider spread than an even sheen. Synthetic data.

    .dev/venv-tools/Scripts/python -m pytest tests/tools/test_sheen.py
"""

import importlib.util
from pathlib import Path

import numpy as np
import OpenEXR

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("sheen", ROOT / "tools" / "gate" / "sheen.py")
sheen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sheen)


def _exr(path: Path, gloss: np.ndarray, diffuse: np.ndarray) -> None:
    channels = {}
    for name, value in (("GlossDir", gloss), ("DiffDir", diffuse)):
        for c in "RGB":
            channels[f"ViewLayer.{name}.{c}"] = value.astype(np.float32)
    with OpenEXR.File({"compression": OpenEXR.ZIP_COMPRESSION, "type": OpenEXR.scanlineimage}, channels) as f:
        f.write(str(path))


def test_the_share_and_the_spread_read_back(tmp_path):
    even = np.full((40, 40), 0.25)
    glint = np.zeros((40, 40))
    glint[::10, ::10] = 25.0  # the same mean, gathered in 16 pixels of 1,600
    diffuse = np.full((40, 40), 0.75)
    _exr(tmp_path / "even.exr", even, diffuse)
    _exr(tmp_path / "glint.exr", glint, diffuse)
    whole = (0.0, 1.0, 0.0, 1.0)
    a = sheen.measure(sheen.passes(tmp_path / "even.exr"), whole)
    b = sheen.measure(sheen.passes(tmp_path / "glint.exr"), whole)
    assert a["sheen share"] == b["sheen share"] == 0.25  # luminance weights sum to 1: grey light reads as it is
    assert a["sheen spread"] == 0.0 and b["sheen spread"] > 9.0  # 1 pixel in 100 at 100x the mean: sqrt(99)
