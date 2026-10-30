# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""MakeHuman's formats and macro blending, against MPFB2's documented behaviour (docs/fileformats/target_metadata.md)
and the fetched data (python tools/fetch_data.py)."""

import json
from pathlib import Path

import pytest

from juststage.core import makehuman

DATA = Path(__file__).resolve().parents[2] / "extension" / "juststage" / "data" / "fetched" / "makehuman"
needs_data = pytest.mark.skipif(not (DATA / "3dobjs" / "base.obj").exists(), reason="run tools/fetch_data.py")


@pytest.fixture(scope="module")
def macro_config():
    return json.loads((DATA / "targets" / "macrodetails" / "macro.json").read_text(encoding="utf-8"))


@needs_data
def test_gender_extremes_never_reach_one(macro_config):
    # the docs: "At gender 0.0 the components are female 0.9902 and male 0.0098, not female 1.0"
    assert makehuman.macro_components(macro_config, "gender", 0.0) == [("female", 0.9902), ("male", 0.0098)]


@needs_data
def test_average_height_and_proportions_add_nothing(macro_config):
    # the docs: "any value in [0.49, 0.51] — including the slider midpoint 0.5 — produces no height target at all"
    assert makehuman.macro_components(macro_config, "height", 0.5) == []
    assert makehuman.macro_components(macro_config, "proportions", 0.5) == []


@needs_data
def test_default_stack(macro_config):
    stack = dict(makehuman.macro_target_stack(macro_config))
    assert not any("height/" in name or "proportions/" in name for name in stack)
    # gender 0.5 → female and male each 0.5; age 0.5 → young (≈1); averages for muscle and weight
    assert stack["macrodetails/universal-female-young-averagemuscle-averageweight"] == pytest.approx(0.5, abs=1e-3)
    assert stack["macrodetails/universal-male-young-averagemuscle-averageweight"] == pytest.approx(0.5, abs=1e-3)
    assert stack["macrodetails/caucasian-female-young"] == pytest.approx(0.165, abs=1e-3)
    assert not any("averagecup-averagefirmness" in name for name in stack)


@needs_data
def test_every_default_target_exists(macro_config):
    for name, _ in makehuman.macro_target_stack(macro_config):
        assert (DATA / "targets" / f"{name}.target.gz").exists(), name


@needs_data
def test_base_mesh_groups():
    groups = makehuman.vertex_groups(DATA / "mesh_metadata" / "basemesh_vertex_groups.json")
    assert len(groups["body"]) == 13380
    assert len(groups["HelperGeometry"]) == 4778
    assert len(groups["JointCubes"]) == 1000
    assert sum(1 for name in groups if name.startswith("joint-")) == 125


@needs_data
def test_a_target_reads_in_blender_axes():
    # the macro targets for the average body are empty on purpose; a muscular one moves vertices
    rows = makehuman.read_target(
        DATA / "targets" / "macrodetails" / "universal-male-young-maxmuscle-averageweight.target.gz"
    )
    assert rows and all(isinstance(i, int) and 0 <= i < 19158 for i, *_ in rows)


@needs_data
def test_average_macro_targets_are_empty_on_purpose():
    assert (
        makehuman.read_target(
            DATA / "targets" / "macrodetails" / "universal-female-young-averagemuscle-averageweight.target.gz"
        )
        == []
    )


def test_shapekey_names_are_mpfb2s_and_fit_blender():
    assert makehuman.target_shapekey_name("macrodetails/universal-female-young-averagemuscle-averageweight") == (
        "$md-universal-$fe-$yn-$av$mu-$av$wg"
    )


@needs_data
def test_every_macro_name_fits_and_is_unique(macro_config):
    values = makehuman.default_macros()
    names = set()
    for gender in (0.0, 0.5, 1.0):
        for age in (0.0, 0.3, 0.5, 1.0):
            for height in (0.0, 1.0):
                stack = makehuman.macro_target_stack(
                    macro_config, {**values, "gender": gender, "age": age, "height": height}
                )
                for target, _ in stack:
                    name = makehuman.target_shapekey_name(target)
                    assert len(("makehuman." + name).encode()) <= makehuman.MAX_NAME, name
                    names.add((name, target))
    assert len({n for n, _ in names}) == len({t for _, t in names})
