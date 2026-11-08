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


def test_the_blink_and_smile_units_are_icts_scanned_shapes(human):
    """2026-11-08 (Q-RIG-1's per-shape pick): Faceunits' eyeBlink folded the closed lid's skin and its smile bent the
    mouth alone; ICT-FaceKit's scanned blink and smile, carried onto our base (`tools/make_ict_units.py`), close the
    lid smooth and lift the cheeks - those keys are ICT's, each on its own side."""
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


def _evaluated(obj) -> np.ndarray:
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    try:
        co = np.empty(len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", co)
        return co.reshape(-1, 3)
    finally:
        ev.to_mesh_clear()


def test_the_lower_teeth_and_tongue_ride_the_jaw_joint_and_survive_a_refit(human):
    """The jaw is a joint (`FACIAL_C_Jaw`, the face rig job's step 3c): the lower teeth, gums and tongue ride it; with
    the face units the face rig runs with the keys driving, so the body's jawOpen key turns the jaw and the teeth drop
    (the gate, 2026-11-05: they stayed); the upper teeth stay with the skull; again after a refit."""
    result, obj = human
    api.run("juststage.head.add_parts", character=result.character)
    api.run("juststage.head.add_face_units", character=result.character)
    teeth = next(o for o in bpy.data.objects if o.juststage.part_of == result.character and o.juststage.part == "teeth")
    assert teeth.data.shape_keys is None or "jawOpen" not in teeth.data.shape_keys.key_blocks  # no stand-in keys
    lower = _teeth_rows(teeth, "lower_teeth_and_gums") | _teeth_rows(teeth, "tongue")
    upper = _teeth_rows(teeth, "upper_teeth_and_gums")
    for refit in (False, True):
        if refit:
            api.run("juststage.head.add_parts", character=result.character)  # a refit: the jaw re-placed too
        rest = _evaluated(teeth)
        obj.data.shape_keys.key_blocks["jawOpen"].value = 1.0
        bpy.context.view_layer.update()  # the face rig's handler turns the jaw after the key
        opened = _evaluated(teeth)
        obj.data.shape_keys.key_blocks["jawOpen"].value = 0.0
        bpy.context.view_layer.update()
        moved = opened - rest
        assert moved[lower, 2].mean() < -0.008, refit  # the lower teeth drop with the chin
        assert np.abs(moved[upper]).max() < 1e-5, refit  # the upper teeth stay
        assert np.abs(_evaluated(teeth) - rest).max() < 1e-5, refit  # and come back


def test_jaw_open_drops_the_chin_and_runs_again_in_place(human):
    result, obj = human
    api.run("juststage.head.add_face_units", character=result.character)
    moved = _offsets(obj, "jawOpen")
    largest = np.linalg.norm(moved, axis=1).argmax()
    assert moved[largest, 2] < -0.01  # the chin's point drops more than a centimetre
    count = len(obj.data.shape_keys.key_blocks)
    assert bpy.ops.juststage.head_add_face_units(character=result.character) == {"FINISHED"}
    assert len(obj.data.shape_keys.key_blocks) == count  # replaced, not added twice
