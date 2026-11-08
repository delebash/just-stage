# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body skeleton's definition and weights (tools/make_skeleton.py): the spec's 82 bones with Manny's parents, the
added joints where Manny has them, MPFB2's own joints and weights kept. Needs MPFB2's fetched files
(`python tools/fetch_data.py`). Run in the tool environment:

    .dev/venv-tools/Scripts/python -m pytest tests/tools/test_make_skeleton.py
"""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("make_skeleton", ROOT / "tools" / "make_skeleton.py")
make_skeleton = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make_skeleton)
MANNY = ROOT / "docs" / "plans" / "2026-10-29-spec-evidence" / "ue5-manny-rest-pose.json"


@pytest.fixture(scope="module")
def made(tmp_path_factory):
    out = tmp_path_factory.mktemp("rigs")
    report = make_skeleton.main(out)
    rig = json.loads((out / "ue5.json").read_text(encoding="utf-8"))
    weights = json.loads((out / "weights.ue5.json").read_text(encoding="utf-8"))["weights"]
    joints = make_skeleton.Joints(make_skeleton._vertices(make_skeleton.MAKEHUMAN / "3dobjs" / "base.obj"),
                                  make_skeleton._groups())  # fmt: skip
    return rig, weights, joints, report


def test_the_bones_are_mannys_80_and_the_two_breasts_with_his_parents(made):
    rig = made[0]
    manny = json.loads(MANNY.read_text(encoding="utf-8"))
    deform = [n for n in manny if not n.startswith(("ik_", "interaction", "center_of_mass"))]
    assert len(deform) == 80
    assert set(rig) == set(deform) | {"breast_l", "breast_r"}
    for name in deform:
        assert (rig[name]["parent"] or None) == manny[name]["parent"], name


def _fraction(joints, rig, bone, limb):
    a, b = joints.at(rig[limb]["head"]), joints.at(rig[limb]["tail"])
    p = joints.at(rig[bone]["head"])
    return float((p - a) @ (b - a) / ((b - a) @ (b - a))), float(np.linalg.norm(np.cross(p - a, b - a)))


@pytest.mark.parametrize("side", ["l", "r"])
def test_the_twist_bones_sit_at_the_limbs_thirds_as_on_manny(made, side):
    rig, _, joints, _ = made
    expected = {"upperarm": {"upperarm_twist_01": 1 / 3, "upperarm_twist_02": 2 / 3},
                "lowerarm": {"lowerarm_twist_01": 2 / 3, "lowerarm_twist_02": 1 / 3},
                "thigh": {"thigh_twist_01": 1 / 3, "thigh_twist_02": 2 / 3},
                "calf": {"calf_twist_01": 2 / 3, "calf_twist_02": 1 / 3}}  # fmt: skip
    for limb, twists in expected.items():
        for twist, at in twists.items():
            t, off = _fraction(joints, rig, f"{twist}_{side}", f"{limb}_{side}")
            assert t == pytest.approx(at, abs=1e-9) and off < 1e-9, (twist, t)
            assert rig[f"{twist}_{side}"]["parent"] == f"{limb}_{side}"


def test_the_upper_spine_and_the_neck_split_where_manny_splits_them(made):
    rig, _, joints, _ = made
    spine_1, neck, head = (joints.co[joints.groups[c]].mean(0) for c in ("joint-spine-1", "joint-neck", "joint-head"))
    s5 = joints.at(rig["spine_05"]["head"])
    assert (s5 - spine_1) @ (neck - spine_1) / ((neck - spine_1) @ (neck - spine_1)) == pytest.approx(5 / 8)
    assert joints.at(rig["neck_02"]["head"]) == pytest.approx((neck + head) / 2)
    assert np.allclose(joints.at(rig["spine_04"]["head"]), spine_1)
    assert np.allclose(joints.at(rig["neck_01"]["tail"]), joints.at(rig["neck_02"]["head"]))


def test_mpfb2s_own_bones_keep_their_joints_and_rolls(made):
    rig = made[0]
    game = json.loads((make_skeleton.RIGS / "rig.game_engine_with_breast.json").read_text(encoding="utf-8"))
    for name, spec_ in game.items():
        ours = rig["root" if name == "Root" else name]
        assert ours["head"] == spec_["head"] and ours["roll"] == spec_["roll"], name
        if name != "neck_01":  # its tail moves to neck_02's head
            assert ours["tail"] == spec_["tail"], name


def test_each_vertex_sums_to_one_within_eight_influences_and_a_split_keeps_its_source(made):
    rig, weights, _, report = made
    game = json.loads((make_skeleton.RIGS / "weights.game_engine_with_breast.json").read_text(encoding="utf-8"))
    n = make_skeleton.HM08_VERTICES
    table = {b: np.zeros(n) for b in weights}
    for b, rows in weights.items():
        for i, w in rows:
            table[b][i] = w
    total = sum(table.values())
    count = sum((t > 0).astype(int) for t in table.values())
    assert np.abs(total - 1.0).max() < 1e-4  # rounding to 6 places, the dropped shares below 1e-5
    assert count.max() <= make_skeleton.MAX_INFLUENCES
    source = {b: np.zeros(n) for b in game["weights"]}
    for b, rows in game["weights"].items():
        for i, w in rows:
            source[b][int(i)] = w
    plain = (source["breast_l"] == 0) & (source["breast_r"] == 0) & (count < make_skeleton.MAX_INFLUENCES)
    chain = table["upperarm_l"] + table["upperarm_twist_01_l"] + table["upperarm_twist_02_l"]
    assert np.abs(chain - source["upperarm_l"])[plain].max() < 1e-4  # the twists share the upper arm's own weight
    hand = table["hand_l"] + sum(table[f"{f}_metacarpal_l"] for f in make_skeleton.METACARPALS)
    assert np.abs(hand - source["hand_l"])[plain].max() < 1e-4
    added = set(rig) - {"root" if k == "Root" else k for k in game["weights"]}
    assert len(added) == 27 and all(weights.get(b) for b in added), sorted(b for b in added if not weights.get(b))
