# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The groom carry's pieces (tools/gate/groom_transfer.py): USC-HairSalon's .data read, its axes turned to Blender's,
a hair card turned into strands rooted at the scalp's end. Run in the tool environment:

    .dev/venv-rdf/Scripts/python -m pytest tests/tools/test_groom_transfer.py
"""

import importlib.util
import struct
import zipfile
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location(
    "groom_transfer", Path(__file__).resolve().parents[2] / "tools" / "gate" / "groom_transfer.py")
gt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gt)


def test_a_style_reads_its_strands_and_leaves_out_the_empty_roots(tmp_path):
    strand = np.array([[0.0, 1.8, 0.0], [0.0, 1.81, -0.01], [0.0, 1.82, -0.02]], np.float32)
    data = struct.pack("<i", 2) + struct.pack("<i", 3) + strand.tobytes() + struct.pack("<i", 1) + np.zeros(3, np.float32).tobytes()
    archive = tmp_path / "hairstyles.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("hairstyles/strands00007.data", data)
    found = gt.read_style(archive, "00007")
    assert len(found) == 1
    assert np.allclose(found[0], strand)


def test_usc_axes_turn_to_blenders():
    # y up and the face toward +z -> z up and the face toward -y
    assert np.allclose(gt.to_blender(np.array([[0.1, 1.8, 0.05]])), [[0.1, -0.05, 1.8]])


def test_a_card_gives_three_strands_from_the_scalp_out():
    # a card of 2 x 5 vertices running up from z 0 (the scalp at z -0.01) to z 0.04, its texture's v along it
    rows = np.arange(5)
    co = np.array([[x, 0.0, 0.01 * r] for r in rows for x in (0.0, 0.004)])
    uv = np.array([[u, 1.0 - 0.2 * r] for r in rows for u in (0.1, 0.2)])  # v falls toward the tip: order by distance
    tris = []
    for r in range(4):
        a, b, c, d = 2 * r, 2 * r + 1, 2 * r + 3, 2 * r + 2
        tris += [[a, b, c], [a, c, d]]
    scalp = np.array([[0.002, 0.0, -0.01]])
    strands = gt.card_strands(co, np.array(tris), uv, scalp)
    assert len(strands) == 3
    for s in strands:
        assert len(s) == 5
        assert s[0][2] < s[-1][2]  # rooted at the scalp's end
