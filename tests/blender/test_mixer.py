# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer (modules/body/mixer.py, `juststage.body.set_mix`): per region of CC5's part list a weighted blend of
identities at a strength, kept as the character's slider values (`scans.<identity>.<region>`, character-data-model.md
§1.3). The masks sum to 1, so one identity at strength 1 in every region is that identity; a region's mix moves only
that region; the wheel's weights are normalised; `set_slider` on a mixer id is the same shape. Needs the generated
masks and identities."""

import importlib

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
mixer = importlib.import_module("bl_ext.system.juststage.modules.body.mixer")
build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
usd_hooks = importlib.import_module("bl_ext.system.juststage.core.usd_hooks")


@pytest.fixture
def human():
    made = api.run("juststage.body.create", name="Mixer test")
    body = bpy.data.objects[made.object]
    yield made, body
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(body)


def _identities(n=1):
    names = mixer.identities()
    assert len(names) >= n, "too few identities: run tools/make_identities.py"
    return names[:n]


def _sliders(body):
    return {item.id: item.value for item in body.juststage.sliders if item.id.startswith(mixer.SPACE + ".")}


def test_one_identity_in_every_region_is_that_identity(human):
    made, body = human
    (name,) = _identities()
    before = build.shaped_coords(body)
    for region in mixer.regions():
        api.run("juststage.body.set_mix", character=made.character, region=region, identities=name, weights=[1.0])
    moved = build.shaped_coords(body) - before
    index, delta = mixer._identity(name)
    hm = makehuman.HM08_VERTICES
    want = np.zeros((hm, 3))
    want[index] = delta
    assert np.abs(moved[:hm] - want).max() < 1e-4  # the masks sum to 1 (the floor key may shift the body: none here)


def test_a_regions_mix_moves_that_region_alone_and_is_kept_as_sliders(human):
    made, body = human
    (name,) = _identities()
    before = build.shaped_coords(body)
    result = api.run("juststage.body.set_mix", character=made.character, region="nose", identities=name,
                     weights=[1.0], strength=0.5)  # fmt: skip
    moved = np.linalg.norm(build.shaped_coords(body) - before, axis=1)[: makehuman.HM08_VERTICES]
    outside = mixer._regions()["nose"] < 1e-6
    assert moved[outside].max() < 1e-6 and moved.max() > 0.0005
    slider = mixer.slider_id(name, "nose")
    assert result.sliders == [slider]
    assert body.data.shape_keys.key_blocks[slider].value == pytest.approx(0.5)
    assert _sliders(body) == {slider: pytest.approx(0.5)}
    ids, values = usd_hooks.sliders(body.juststage)  # the package's sliderIds / sliderValues
    assert values[ids.index(slider)] == pytest.approx(0.5)


def test_the_wheels_weights_are_normalised_and_a_new_mix_replaces_the_last(human):
    made, body = human
    first, second = _identities(2)
    api.run("juststage.body.set_mix", character=made.character, region="chin", identities=f"{first}, {second}",
            weights=[3.0, 1.0], strength=0.8)  # fmt: skip
    a, b = mixer.slider_id(first, "chin"), mixer.slider_id(second, "chin")
    assert _sliders(body) == {a: pytest.approx(0.6), b: pytest.approx(0.2)}
    api.run("juststage.body.set_mix", character=made.character, region="chin", identities=second, weights=[1.0],
            strength=0.8)  # fmt: skip
    assert _sliders(body) == {a: pytest.approx(0.0), b: pytest.approx(0.8)}
    assert mixer.region_mix(body, "chin") == {second: pytest.approx(0.8)}


def test_set_slider_on_a_mixer_id_is_the_same_shape(human):
    made, body = human
    (name,) = _identities()
    before = build.shaped_coords(body)
    api.run("juststage.body.set_slider", character=made.character, slider=mixer.slider_id(name, "mouth"), value=0.7)
    by_slider = build.shaped_coords(body) - before
    api.run("juststage.body.set_slider", character=made.character, slider=mixer.slider_id(name, "mouth"), value=0.0)
    assert np.abs(build.shaped_coords(body) - before).max() < 1e-6
    api.run("juststage.body.set_mix", character=made.character, region="mouth", identities=name, weights=[1.0],
            strength=0.7)  # fmt: skip
    assert np.abs((build.shaped_coords(body) - before) - by_slider).max() < 1e-6


def test_an_unknown_identity_region_or_value_is_refused_by_name(human):
    made, _ = human
    (name,) = _identities()
    with pytest.raises(api.CommandError, match="no identity"):
        api.run("juststage.body.set_mix", character=made.character, region="nose", identities="nobody", weights=[1.0])
    with pytest.raises(api.CommandError, match="no region"):
        api.run("juststage.body.set_mix", character=made.character, region="tail", identities=name, weights=[1.0])
    with pytest.raises(api.CommandError, match="weights"):
        api.run("juststage.body.set_mix", character=made.character, region="nose", identities=name, weights=[0.0])
    with pytest.raises(api.CommandError, match="mixer one"):
        api.run("juststage.body.set_slider", character=made.character, slider="scans.nobody.nose", value=0.5)
    with pytest.raises(api.CommandError, match="value"):
        api.run("juststage.body.set_slider", character=made.character, slider=mixer.slider_id(name, "nose"), value=-0.5)
