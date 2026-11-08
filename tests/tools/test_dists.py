# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The gate's texture measure as two samples of skin (tools/gate/dists.py --patches): the energy excess - half
Székely & Rizzo's energy statistic over a pooled distance matrix - is ~0 for two samples of one texture and grows with
the difference; the 1.5%-jitter floor it replaced compared the same pixels (2026-11-07). Run in the tool environment:

    .dev/venv-rdf/Scripts/python -m pytest tests/tools/test_dists.py
"""

import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location("dists", Path(__file__).resolve().parents[2] / "tools" / "gate" / "dists.py")
dists = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dists)


def _pooled(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Euclidean distances between every pair of points of a and b pooled (a first)."""
    x = np.vstack([a, b])
    return np.linalg.norm(x[:, None] - x[None], axis=-1)


def test_the_excess_is_near_zero_for_one_texture_and_grows_with_the_difference():
    rng = np.random.default_rng(0)
    first = np.arange(48) < 24
    same = _energy_of(rng.normal(0, 1, (24, 8)), rng.normal(0, 1, (24, 8)), first)
    near = _energy_of(rng.normal(0, 1, (24, 8)), rng.normal(0.3, 1, (24, 8)), first)
    far = _energy_of(rng.normal(0, 1, (24, 8)), rng.normal(1.5, 1, (24, 8)), first)
    assert abs(same) < 0.1
    assert same < near < far


def test_the_permutation_band_holds_the_same_texture_and_rejects_another():
    rng = np.random.default_rng(1)
    first = np.arange(48) < 24
    for shift, expect_p in ((0.0, "high"), (1.5, "low")):
        pooled = _pooled(rng.normal(0, 1, (24, 8)), rng.normal(shift, 1, (24, 8)))
        excess = dists._energy(pooled, first)
        null = np.array([dists._energy(pooled, rng.permutation(first)) for _ in range(500)])
        p = (null >= excess).mean()
        assert (p > 0.05) if expect_p == "high" else (p < 0.01)


def test_the_layers_shares_add_up_to_the_distance():
    import piq
    import torch

    metric = piq.DISTS(reduction="none")
    gen = torch.Generator().manual_seed(2)
    a = dists._features(metric, [torch.rand(1, 3, 96, 96, generator=gen) for _ in range(3)])
    b = dists._features(metric, [torch.rand(1, 3, 96, 96, generator=gen) * 0.5 for _ in range(2)])
    whole = dists._matrix(metric, a, b)
    shares = dists._matrix(metric, a, b, by_layer=True)
    assert shares.shape == (len(dists.LAYER_NAMES), 3, 2)
    assert np.allclose(shares.sum(0), whole, atol=1e-9)


def _energy_of(a, b, first):
    return dists._energy(_pooled(a, b), first)
