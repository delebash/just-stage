# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The blink's closing step (modules/head/blink_contact.py): with the face units added, each eye gets a corrective that
snaps the closed upper lid onto the lower, eased in by its blink - the lids meet, nothing clips the eyeball, and half a
blink is still half open."""

import importlib

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
blink_contact = importlib.import_module("bl_ext.system.juststage.modules.head.blink_contact")
create = importlib.import_module("bl_ext.system.juststage.modules.body.body_create")

CHARACTERS = [{"gender": 1.0}, {"gender": 0.0, "age": 0.2}, {"gender": 1.0, "age": 0.9, "weight": 0.8}]


@pytest.mark.parametrize("macros", CHARACTERS)
def test_the_blink_closes_onto_the_lower_lid_without_clipping(macros):
    made = api.run("juststage.body.create", name="Blink test", **macros)
    body = bpy.data.objects[made.object]
    try:
        create.open_eyes(made.character)  # as the app's New human does
        api.run("juststage.head.add_parts", character=made.character)
        api.run("juststage.head.add_face_units", character=made.character)
        keys = body.data.shape_keys.key_blocks
        for side in ("Left", "Right"):
            assert blink_contact.KEY.format(side=side) in keys
        result = blink_contact.make(body)
        for side, (gap_mm, clip_mm) in result.items():
            assert gap_mm < 1.0, (side, gap_mm)  # the lash lines meet (Faceunits alone: ~2 mm apart)
            assert clip_mm == 0.0, (side, clip_mm)
        keys["eyeBlinkLeft"].value = 0.5
        bpy.context.view_layer.update()
        assert abs(keys[blink_contact.KEY.format(side="Left")].value - 0.125) < 1e-3  # eased in near closure
        keys["eyeBlinkLeft"].value = 1.0
        bpy.context.view_layer.update()
        assert keys[blink_contact.KEY.format(side="Left")].value == pytest.approx(1.0)
    finally:
        for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
            bpy.data.objects.remove(obj)
        bpy.data.objects.remove(body)
