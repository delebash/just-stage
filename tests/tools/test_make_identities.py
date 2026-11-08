# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer's identities (tools/make_identities.py): a scan fit on the face test's export becomes offsets on hm08's
own vertices (the export's first ones), and a fit made against another export is refused, not used. Synthetic data.

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
    report = make_identities.main(out, scans)
    data = np.load(out / "good.npz")
    assert data["index"].tolist() == [5, 7, 13379]
    assert np.allclose(data["delta"], move[:3], atol=1e-6)
    assert not (out / "stale.npz").exists() and report["stale"][0].startswith("refused")
