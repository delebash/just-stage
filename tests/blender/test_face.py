# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face's ARKit 52 shape keys from MakeHuman's CC0 Faceunits 01 (skeleton-and-face.md §2.1)."""

import importlib
import json

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
paths = importlib.import_module("bl_ext.system.juststage.paths")
face_units = importlib.import_module("bl_ext.system.juststage.modules.head.face_units")

pytestmark = pytest.mark.skipif(
    not face_units.unit_path("jawOpen").exists(), reason="run tools/fetch_data.py (Faceunits 01)"
)


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Face test")
    yield result, bpy.data.objects[result.object]
    bpy.data.objects.remove(bpy.data.objects[result.object])


def _offsets(obj, name):
    keys = obj.data.shape_keys
    co, base = (np.empty(len(obj.data.vertices) * 3, dtype=np.float32) for _ in range(2))
    keys.key_blocks[name].data.foreach_get("co", co)
    keys.reference_key.data.foreach_get("co", base)
    return (co - base).reshape(-1, 3)


def test_the_pack_holds_arkits_52():
    pack = json.loads(paths.makehuman("packs", "faceunits01.json").read_text(encoding="utf-8"))
    assert sorted(pack) == sorted(face_units.ARKIT)
    assert len(face_units.ARKIT) == 52
    assert {entry["license"] for entry in pack.values()} == {"CC0"}


def test_a_character_gets_the_52_keys_at_rest(human):
    result, obj = human
    out = api.run("juststage.head.add_face_units", character=result.character)
    assert out.units == 52 and out.missing == []
    keys = obj.data.shape_keys.key_blocks
    assert all(keys[name].value == 0.0 for name in face_units.ARKIT)


def test_the_blink_units_are_icts_scanned_blink(human):
    """2026-11-08 (Q-RIG-1's per-shape pick): Faceunits' eyeBlink folded the closed lid's skin; ICT-FaceKit's scanned
    blink, carried onto our base (`tools/make_ict_units.py`), closes it smooth - the two blink keys are ICT's."""
    result, obj = human
    api.run("juststage.head.add_face_units", character=result.character)
    for name in face_units.ICT_UNITS:
        data = np.load(paths.generated("faceunits_ict", f"{name}.npz", tool="tools/make_ict_units.py"))
        moved = _offsets(obj, name)
        assert np.allclose(moved[data["index"]], data["delta"], atol=1e-6), name
        side = float(obj.data.vertices[int(data["index"][np.argmax(np.linalg.norm(data["delta"], axis=1))])].co.x)
        assert np.sign(side) == (1.0 if name.endswith("Left") else -1.0), (name, side)  # Left is the character's +x


def _teeth_rows(teeth, group_name):
    rows = np.zeros(len(teeth.data.vertices), dtype=bool)
    rows[importlib.import_module("bl_ext.system.juststage.modules.head.parts").groups("teeth")[group_name]] = True
    return rows


def test_the_lower_teeth_and_tongue_ride_jaw_open_and_survive_a_refit(human):
    result, obj = human
    api.run("juststage.head.add_parts", character=result.character)
    api.run("juststage.head.add_face_units", character=result.character)
    teeth = next(o for o in bpy.data.objects if o.juststage.part_of == result.character and o.juststage.part == "teeth")
    lower = _teeth_rows(teeth, "lower_teeth_and_gums") | _teeth_rows(teeth, "tongue")
    upper = _teeth_rows(teeth, "upper_teeth_and_gums")
    moved = _offsets(teeth, "jawOpen")
    assert moved[lower, 2].mean() < -0.008  # the lower teeth drop with the chin (the gate: they stayed, 2026-11-05)
    assert np.abs(moved[upper]).max() < 1e-6  # the upper teeth stay with the skull
    obj.data.shape_keys.key_blocks["jawOpen"].value = 1.0  # the teeth's key follows the body's (a driver)
    bpy.context.view_layer.update()
    assert teeth.data.shape_keys.key_blocks["jawOpen"].value == pytest.approx(1.0)
    obj.data.shape_keys.key_blocks["jawOpen"].value = 0.0
    api.run("juststage.head.add_parts", character=result.character)  # a refit rebuilds them on the new fit
    assert _offsets(teeth, "jawOpen")[lower, 2].mean() < -0.008


def test_jaw_open_drops_the_chin_and_runs_again_in_place(human):
    result, obj = human
    api.run("juststage.head.add_face_units", character=result.character)
    moved = _offsets(obj, "jawOpen")
    largest = np.linalg.norm(moved, axis=1).argmax()
    assert moved[largest, 2] < -0.01  # the chin's point drops more than a centimetre
    count = len(obj.data.shape_keys.key_blocks)
    assert bpy.ops.juststage.head_add_face_units(character=result.character) == {"FINISHED"}
    assert len(obj.data.shape_keys.key_blocks) == count  # replaced, not added twice
