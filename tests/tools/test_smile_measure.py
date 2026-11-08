# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The smile's numbers (tools/gate/smile_measure.py): a point's move between the neutral and the smile pictures,
millimetres on the face's plane, up and out positive. Run in the tool environment:

    .dev/venv-rdf/Scripts/python -m pytest tests/tools/test_smile_measure.py
"""

import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location(
    "smile_measure", Path(__file__).resolve().parents[2] / "tools" / "gate" / "smile_measure.py")
sm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sm)


def _face() -> np.ndarray:
    """478 points, the eyes' corners either side of x 1000 (the midline) and the mouth's corners 200 px out."""
    p = np.full((478, 2), 1000.0)
    p[[33, 133], 0], p[[362, 263], 0] = (800, 900), (1100, 1200)
    p[61, 0], p[291, 0] = 800, 1200
    p[list(sm.POINTS["upper_lid"]), 1], p[list(sm.POINTS["lower_lid"]), 1] = 700, 720
    return p


def test_the_corners_up_and_out_in_millimetres():
    neutral = _face()
    smile = neutral.copy()
    smile[61] += (-10, -20)  # the subject's right corner: out is -x in the picture
    smile[291] += (10, -20)
    m = sm.moves(neutral, smile, 0.5)
    assert m["corner up"] == 10.0  # 20 px up at 0.5 mm a pixel
    assert m["corner out"] == 5.0
    assert m["cheek up"] == 0.0


def test_a_narrowing_eye_reads_as_a_smaller_opening():
    neutral = _face()
    smile = neutral.copy()
    smile[list(sm.POINTS["lower_lid"]), 1] -= 4  # the lower lids up 4 px
    m = sm.moves(neutral, smile, 0.25)
    assert m["lower lid up"] == 1.0
    assert m["eye opening"] == -1.0
