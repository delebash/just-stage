# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The neutral lip seal (modules/head/lip_seal.py): hm08's neutral leaves a see-through slit between the lips; every
refit closes it with the smallest share of Faceunits' mouthClose, so a new character's mouth is sealed and still
opens."""

import importlib

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
lip_seal = importlib.import_module("bl_ext.system.juststage.modules.head.lip_seal")


CHARACTERS = [{"gender": 1.0}, {"gender": 0.0, "age": 0.2}, {"gender": 1.0, "age": 0.9, "weight": 0.8}]


@pytest.mark.parametrize("macros", CHARACTERS)
def test_a_new_characters_lips_are_sealed_and_still_open(macros):
    made = api.run("juststage.body.create", name="Seal test", **macros)
    body = bpy.data.objects[made.object]
    try:
        api.run("juststage.head.add_parts", character=made.character)
        parts.refit(body)
        key = body.data.shape_keys.key_blocks[lip_seal.SEAL]
        assert key.value == 1.0
        assert lip_seal.drawn_slit_mm(body) == 0.0  # sealed where it is drawn (the subdivided mesh)
        key.value = 0.0
        bpy.context.view_layer.update()
        assert lip_seal.drawn_slit_mm(body) > 0.0  # hm08's own slit, which the seal closes (the measure sees it)
        key.value = 1.0
        api.run("juststage.head.add_face_units", character=made.character)
        body.data.shape_keys.key_blocks["jawOpen"].value = 1.0
        bpy.context.view_layer.update()
        # the jaw still opens the mouth from the sealed lips - wider than hm08's own slit (0.6-0.9 mm); the measure's
        # window reaches only 4 mm below the front teeth, so an open mouth reads 1.8-3 mm there, not its full height
        assert lip_seal.drawn_slit_mm(body) > 1.0
        assert key.value == 0.0  # the seal is the neutral's: gone with the jaw open (it held the lips ~5 mm closed)
    finally:
        for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
            bpy.data.objects.remove(obj)
        bpy.data.objects.remove(body)
