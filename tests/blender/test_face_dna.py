# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face rig's DNA (tools/make_face_dna.py): MetaHuman's control names, our values - RigLogic evaluates it: a GUI
control moves its expression's channel, a two-way control's halves move their own (the directions read from the
user's archetype). Needs the generated `data/generated/rig/face.dna`."""

import importlib

import pytest

paths = importlib.import_module("bl_ext.system.juststage.paths")


@pytest.fixture(scope="module")
def rig():
    dna = importlib.import_module("dna")
    riglogic = importlib.import_module("riglogic")
    path = paths.generated("rig", "face.dna", tool="python tools/dev.py blender -b --python tools/make_face_dna.py")
    stream = dna.FileStream(str(path), dna.FileStream.AccessMode_Read, dna.FileStream.OpenMode_Binary)
    reader = dna.BinaryStreamReader(stream, dna.DataLayer_All)
    reader.read()
    assert dna.Status.isOk(), dna.Status.get().message
    logic = riglogic.RigLogic(reader)
    return reader, logic


def _evaluate(reader, logic, gui: dict[str, float]) -> dict[str, float]:
    riglogic = importlib.import_module("riglogic")
    instance = riglogic.RigInstance(logic)
    names = [reader.getGUIControlName(i) for i in range(reader.getGUIControlCount())]
    for name, value in gui.items():
        instance.setGUIControl(names.index(name), value)
    logic.mapGUIToRawControls(instance)
    logic.calculate(instance)
    out = instance.getBlendShapeOutputs()
    return {reader.getBlendShapeChannelName(i): out[i] for i in range(reader.getBlendShapeChannelCount())}


def test_the_dna_has_metahumans_controls_and_our_channels(rig):
    reader, _logic = rig
    assert reader.getGUIControlCount() == 174 and reader.getRawControlCount() == 251
    channels = {reader.getBlendShapeChannelName(i) for i in range(reader.getBlendShapeChannelCount())}
    assert {"browDownLeft", "mouthSmileRight", "jawOpen", "eyeLookOutLeft"} <= channels


@pytest.mark.parametrize(("gui", "channel"), [
    ({"CTRL_L_brow_down.ty": 1.0}, "browDownLeft"),
    ({"CTRL_R_mouth_cornerPull.ty": 1.0}, "mouthSmileRight"),
    ({"CTRL_C_jaw.ty": 1.0}, "jawOpen"),
    ({"CTRL_L_eye.tx": 1.0}, "eyeLookOutLeft"),  # a look to the face's left turns its left eye out
    ({"CTRL_L_eye.tx": -1.0}, "eyeLookInLeft"),
])  # fmt: skip
def test_a_control_moves_its_channel_alone(rig, gui, channel):
    reader, logic = rig
    out = _evaluate(reader, logic, gui)
    assert out[channel] == pytest.approx(1.0)
    assert sum(v for k, v in out.items() if k != channel) == pytest.approx(0.0)
