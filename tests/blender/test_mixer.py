# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer (modules/body/mixer.py, `juststage.body.set_mix`): per region of CC5's part list a weighted blend of
identities at a strength. The masks sum to 1, so one identity at strength 1 in every region is that identity; a
region's mix moves only that region; the mix is kept on the character. Needs the generated masks and identities."""

import importlib
import json

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
mixer = importlib.import_module("bl_ext.system.juststage.modules.body.mixer")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")


@pytest.fixture
def human():
    made = api.run("juststage.body.create", name="Mixer test")
    body = bpy.data.objects[made.object]
    yield made, body
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(body)


def _identity():
    names = mixer.identities()
    assert names, "no identities: run tools/make_identities.py"
    return names[0]


def test_one_identity_in_every_region_is_that_identity(human):
    made, body = human
    name = _identity()
    before = build.shaped_coords(body)
    for region in mixer.regions():
        api.run("juststage.body.set_mix", character=made.character, region=region, identities=name, weights=[1.0])
    moved = build.shaped_coords(body) - before
    index, delta = mixer._identity(name)
    hm = makehuman.HM08_VERTICES
    want = np.zeros((hm, 3))
    want[index] = delta
    assert np.abs(moved[:hm] - want).max() < 1e-4  # the masks sum to 1 (the floor key may shift the body: none here)


def test_a_regions_mix_moves_that_region_alone(human):
    made, body = human
    name = _identity()
    before = build.shaped_coords(body)
    result = api.run("juststage.body.set_mix", character=made.character, region="nose", identities=name,
                     weights=[1.0], strength=0.5)  # fmt: skip
    moved = np.linalg.norm(build.shaped_coords(body) - before, axis=1)[: makehuman.HM08_VERTICES]
    outside = mixer._regions()["nose"] < 1e-6
    assert moved[outside].max() < 1e-6 and moved.max() > 0.0005
    assert body.data.shape_keys.key_blocks[result.key].value == pytest.approx(0.5)
    assert json.loads(body[mixer.STORE])["nose"] == {"identities": [name], "weights": [1.0], "strength": 0.5}


def test_an_unknown_identity_or_region_is_refused_by_name(human):
    made, _ = human
    with pytest.raises(api.CommandError, match="no identity"):
        api.run("juststage.body.set_mix", character=made.character, region="nose", identities="nobody", weights=[1.0])
    with pytest.raises(api.CommandError, match="no region"):
        api.run("juststage.body.set_mix", character=made.character, region="tail", identities=_identity(),
                weights=[1.0])  # fmt: skip
