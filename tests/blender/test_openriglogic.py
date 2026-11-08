# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""OpenRigLogic's bindings (MIT) ship as the extension's wheel (the manifest's `wheels`; `libs/openriglogic/build.py`):
inside Blender `dna` and `riglogic` import, and a DNA written with its own writer reads back (its `demo.py`'s calls) -
the face rig's ground (docs/plans/2026-11-08-face-rig.md step 1)."""

import importlib


def test_dna_and_riglogic_import_and_a_dna_round_trips(tmp_path):
    dna = importlib.import_module("dna")
    importlib.import_module("riglogic")
    path = str(tmp_path / "face.dna")
    stream = dna.FileStream(path, dna.FileStream.AccessMode_Write, dna.FileStream.OpenMode_Binary)
    writer = dna.BinaryStreamWriter(stream)
    writer.setName("JustStage test")
    writer.setLODCount(1)
    writer.setJointName(0, "FACIAL_C_FacialRoot")
    writer.setJointName(1, "FACIAL_C_Jaw")
    writer.write()
    assert dna.Status.isOk(), dna.Status.get().message
    stream = dna.FileStream(path, dna.FileStream.AccessMode_Read, dna.FileStream.OpenMode_Binary)
    reader = dna.BinaryStreamReader(stream, dna.DataLayer_All)
    reader.read()
    assert dna.Status.isOk(), dna.Status.get().message
    assert reader.getName() == "JustStage test"
    assert [reader.getJointName(i) for i in range(reader.getJointCount())] == ["FACIAL_C_FacialRoot", "FACIAL_C_Jaw"]
