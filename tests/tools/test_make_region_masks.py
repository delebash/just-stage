# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer's region masks (tools/make_region_masks.py): CC5's parts as soft weights over hm08 summing to 1 at every
vertex - so a mix of one identity at strength 1 is that identity - the face's regions inside the head, the body's
parts the skeleton's own. Needs the fetched targets and the generated skeleton weights. Run in the tool environment:

    .dev/venv-tools/Scripts/python -m pytest tests/tools/test_make_region_masks.py
"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("make_region_masks", ROOT / "tools" / "make_region_masks.py")
make_region_masks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make_region_masks)


@pytest.fixture(scope="module")
def regions(tmp_path_factory):
    out = tmp_path_factory.mktemp("mixer") / "regions.npz"
    make_region_masks.main(out)
    data = np.load(out)
    return {k: data[k] for k in data.files}


def test_cc5s_parts_each_have_a_region(regions):
    assert set(regions) == {*make_region_masks.FACE, *make_region_masks.BODY, "head shape"}
    for name, w in regions.items():
        assert (w > 0.5).sum() > 100, name


def test_the_regions_sum_to_one_at_every_vertex(regions):
    total = sum(regions.values())
    assert np.abs(total - 1.0).max() < 1e-4


def test_the_face_regions_stay_on_the_head(regions):
    head = regions["head shape"] + sum(regions[k] for k in make_region_masks.FACE)
    for name in make_region_masks.FACE:
        inside = regions[name] > 0.01
        assert (head[inside] > 0.99 * regions[name][inside]).all(), name  # a face region is part of the head's share
    assert regions["nose"][regions["legs"] > 0.5].max() == 0.0
