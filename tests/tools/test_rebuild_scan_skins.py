# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""A recorded composition put right by the composer's own rule (tools/rebuild_scan_skins.py `own_sex_first`): the
pores' fill order with the character's own sex first, the mid layer from its own sex only. Run in the tool environment:

    .dev/venv-rdf/Scripts/python -m pytest tests/tools/test_rebuild_scan_skins.py
"""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "rebuild_scan_skins", Path(__file__).resolve().parents[2] / "tools" / "rebuild_scan_skins.py"
)
rebuild = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rebuild)

SEXES = {"m1": "m", "m2": "m", "f1": "f", "f2": "f"}


def test_a_mans_skin_drops_a_woman_from_its_mid_layer_and_fills_with_men_first():
    p = {"sex": "m", "fine_from": ["m1", "f1", "m2", "f2"], "mid_from": {"m1": 0.65, "f1": 0.35}}
    got = rebuild.own_sex_first(p, SEXES)
    assert got["fine_from"] == ["m1", "m2", "f1", "f2"]
    assert got["mid_from"] == {"m1": pytest.approx(1.0)}
    assert p["mid_from"] == {"m1": 0.65, "f1": 0.35}  # the record itself untouched


def test_a_composition_already_right_is_unchanged():
    p = {"sex": "f", "fine_from": ["f1", "f2", "m1"], "mid_from": {"f1": 0.6, "f2": 0.4}}
    assert rebuild.own_sex_first(p, SEXES) == p
