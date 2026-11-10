# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer's identities (tools/make_identities.py): a scan fit on the face test's export becomes offsets on hm08's
own vertices (the export's first ones), a fit made against another export is refused, not used, and the harmonic fill
carries a fit's offsets past its cut, fading where the head's share ends. Synthetic data.

    .dev/venv-tools/Scripts/python -m pytest tests/tools/test_make_identities.py
"""

import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("make_identities", ROOT / "tools" / "make_identities.py")
make_identities = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make_identities)


def test_a_fit_becomes_hm08_offsets_and_a_stale_one_is_refused(tmp_path):
    scans, out = tmp_path / "scans", tmp_path / "out"
    rng = np.random.default_rng(0)
    export = rng.normal(size=(20000, 3)).astype(np.float32)
    (scans / "good").mkdir(parents=True)
    (scans / "stale").mkdir()
    np.savez(scans / "head_export.npz", co=export)
    used = np.array([5, 7, 13379, 13380, 19999])  # the last two are subdivision vertices, not hm08's
    move = np.array([[0.002, 0, 0], [0, 0.003, 0], [0, 0, -0.001], [0.5, 0, 0], [0.5, 0, 0]])
    np.savez(scans / "good" / "fit.npz", used=used, fitted=export[used] + move)
    np.savez(scans / "stale" / "fit.npz", used=used, fitted=export[used] + 0.2)  # ~20 cm off: another export
    no_mesh = (np.zeros((0, 2), np.int64), np.zeros(make_identities.BODY_VERTICES))  # no fill
    report = make_identities.main(out, scans, no_mesh, (set(), np.ones(make_identities.BODY_VERTICES)))
    data = np.load(out / "good.npz")
    assert data["index"].tolist() == [5, 7, 13379]
    assert np.allclose(data["delta"], move[:3], atol=1e-6)
    assert not (out / "stale.npz").exists() and report["stale"][0].startswith("refused")


def test_the_fill_carries_the_fit_past_its_cut_and_fades_where_the_heads_share_ends():
    # a chain 0-1-2-3-4-5-6: 0 and 1 fitted (1 cm), 2-5 not, 6 outside the head's share
    edges = np.array([[i, i + 1] for i in range(6)])
    offsets = np.zeros((7, 3))
    offsets[:2, 0] = 0.01
    fitted = np.array([True, True, False, False, False, False, False])
    share = np.array([1.0, 1.0, 1.0, 0.8, 0.5, 0.2, 0.0])
    out = make_identities.extend(offsets, fitted, edges, share)
    assert np.allclose(out[:, 0], [0.01, 0.01, 0.008, 0.006, 0.004, 0.002, 0.0], atol=1e-9)  # a straight ramp: harmonic
    assert np.allclose(out[:, 1:], 0.0)


def test_a_shape_only_scans_identity_is_its_ears_alone(tmp_path):
    """HUTUBS's heads (smoothed faces, bald caps) are in the mixer for their ears (Q-EAR-1): their offsets outside the
    ears region are dropped, so picking one for a nose or a head shape moves nothing."""
    scans, out = tmp_path / "scans", tmp_path / "out"
    export = np.zeros((20000, 3), np.float32)
    (scans / "hutubs_pp1").mkdir(parents=True)
    np.savez(scans / "head_export.npz", co=export)
    used = np.array([10, 20, 30])
    np.savez(scans / "hutubs_pp1" / "fit.npz", used=used, fitted=export[used] + 0.003)
    ears = np.zeros(make_identities.BODY_VERTICES)
    ears[20], ears[30] = 1.0, 0.5  # vertex 10 is not on the ears
    no_mesh = (np.zeros((0, 2), np.int64), np.zeros(make_identities.BODY_VERTICES))
    make_identities.main(out, scans, no_mesh, ({"hutubs_pp1"}, ears))
    data = np.load(out / "hutubs_pp1.npz")
    assert data["index"].tolist() == [20, 30]
    assert np.allclose(data["delta"], [[0.003] * 3, [0.0015] * 3], atol=1e-6)
    assert "ears only" in str(data["source"])
