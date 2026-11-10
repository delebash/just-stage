# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The lips' soft mask (tools/make_lips_soft.py): MPFB2's hard-edged lips mask blurred so the lip fades into the skin
(2026-11-10: a crisp drawn outline beside HD Aaron's). Run in the tool environment:

    .dev/venv-tools/Scripts/python -m pytest tests/tools/test_make_lips_soft.py
"""

import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location(
    "make_lips_soft", Path(__file__).resolve().parents[2] / "tools" / "make_lips_soft.py"
)
mls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mls)


def test_a_hard_edge_becomes_a_ramp_and_keeps_its_weight():
    mask = np.zeros((200, 200), np.float32)
    mask[60:140, 40:160] = 1.0  # a hard-edged lip
    out = mls.soft(mask)
    row = out[100]
    assert abs(out.sum() - mask.sum()) / mask.sum() < 0.01  # weight moved, not added
    ramp = np.count_nonzero((row > 0.05) & (row < 0.95))
    assert ramp >= 2 * 2 * mls.SIGMA_PX  # each side fades over several sigma, not one texel
    assert row[100] > 0.99 and row[5] < 0.01  # the middle stays lip, far skin stays skin
