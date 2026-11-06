# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Migrations (extension/juststage/migrations/): a character saved on base v1 (hm08 as MakeHuman ships it) comes in as
base v2 with its grooms where they were drawn and its sliders unchanged (docs/plans/2026-11-05-lid-anatomy-build.md,
test 5)."""

import importlib

import bpy
import numpy as np

api = importlib.import_module("bl_ext.system.juststage.api")
base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
body_create = importlib.import_module("bl_ext.system.juststage.modules.body.body_create")
lashes = importlib.import_module("bl_ext.system.juststage.modules.hair.lashes")
brows = importlib.import_module("bl_ext.system.juststage.modules.hair.brows")
parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
sliders = importlib.import_module("bl_ext.system.juststage.modules.body.sliders")
makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")


def _world(obj):
    m = np.array(obj.matrix_world)
    return lashes.evaluated_points(obj) @ m[:3, :3].T + m[:3, 3]


def test_a_v1_character_comes_in_as_v2_with_its_grooms_in_place(tmp_path):
    values = body_create.Params()._asdict()
    for k in ("name", "dressed"):
        values.pop(k)
    values["gender"] = 1.0
    old = build.create_human("Old man", values, base_version=1)
    cid = old.juststage.character_id
    for slider, value in body_create.EYE_OPEN.items():
        sliders.apply(old, sliders.catalog()[slider], value)
    old.juststage.sliders[0].value = 0.0
    parts.add(old)
    lash = lashes.make(old)
    brow = brows.make(old)
    bpy.context.view_layer.update()
    lash_before, brow_before = _world(lash), _world(brow)
    keys_before = {k.name: k.value for k in old.data.shape_keys.key_blocks}
    out = api.run("juststage.library.save", character=cid, catalog="Characters", name="Old man", licence="CC0-1.0",
                  provenance="test", library=str(tmp_path / "lib"))  # fmt: skip
    for o in [o for o in bpy.data.objects if o.juststage.part_of == cid]:
        bpy.data.objects.remove(o)
    bpy.data.objects.remove(old)
    added = api.run("juststage.library.add", path=out.path)
    body = bpy.data.objects[added.object]
    try:
        assert body.juststage.base_version == base.VERSION
        assert len(body.data.vertices) == base.record()["vertices"]
        keys = {k.name: k.value for k in body.data.shape_keys.key_blocks}
        assert all(keys.get(n) == v for n, v in keys_before.items())  # its sliders unchanged
        assert base.CONTACT in keys
        new_grooms = {o.juststage.part: o for o in bpy.data.objects
                      if o.juststage.part_of == added.character and o.type == "CURVES"}  # fmt: skip
        assert new_grooms["eyelashes"].data.surface == body
        moved = np.linalg.norm(_world(new_grooms["eyebrows"]) - brow_before, axis=1)
        assert moved.max() < 0.0002, moved.max()  # the brows where they were drawn
        lash = new_grooms["eyelashes"]  # ours, made again on the new lid's lash line
        assert lash.name.endswith(lashes.NAME) and abs(len(_world(lash)) - len(lash_before)) < 0.2 * len(lash_before)
    finally:
        for o in [o for o in bpy.data.objects if o.juststage.part_of == added.character]:
            bpy.data.objects.remove(o)
        bpy.data.objects.remove(body)
