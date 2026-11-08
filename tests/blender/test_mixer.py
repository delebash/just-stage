# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer (modules/body/mixer.py, `juststage.body.set_mix`): per region of CC5's part list a weighted blend of
identities at a strength in one of MetaHuman's Blend Types, kept as the character's slider values
(`scans.<identity>.<region>.<part>`, character-data-model.md §1.3). The masks sum to 1 and the two parts to the
identity, so one identity at strength 1 in every region is that identity; a region's mix moves only that region; the
features keep the region's place (their sum is nothing), the proportions are a similarity; the wheel's weights are
normalised; `set_slider` on the mixer's ids is the same shape. Needs the generated masks and identities."""

import importlib

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
mixer = importlib.import_module("bl_ext.system.juststage.modules.body.mixer")
body_set_mix = importlib.import_module("bl_ext.system.juststage.modules.body.body_set_mix")
base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
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


def _mix(made, region, names, weights, **kw):
    return api.run("juststage.body.set_mix", character=made.character, region=region, identities=", ".join(names),
                   weights=weights, **kw)  # fmt: skip


def test_the_modes_are_metahumans_and_the_parts_its_two_layers():
    assert body_set_mix.MODES == ("both", *mixer.PARTS)


def test_one_identity_in_every_region_is_that_identity(human):
    made, body = human
    (name,) = _identities()
    before = build.shaped_coords(body)
    for region in mixer.regions():
        _mix(made, region, [name], [1.0])
    moved = build.shaped_coords(body) - before
    index, delta = mixer._identity(name)
    hm = makehuman.HM08_VERTICES
    want = np.zeros((hm, 3))
    want[index] = delta
    assert np.abs(moved[:hm] - want).max() < 1e-4  # the masks sum to 1, the parts to the identity


def test_a_regions_mix_moves_that_region_alone_and_is_kept_as_sliders(human):
    made, body = human
    (name,) = _identities()
    before = build.shaped_coords(body)
    result = _mix(made, "nose", [name], [1.0], strength=0.5)
    moved = np.linalg.norm(build.shaped_coords(body) - before, axis=1)[: makehuman.HM08_VERTICES]
    outside = mixer._regions()["nose"] < 1e-6
    assert moved[outside].max() < 1e-6 and moved.max() > 0.0005
    ids = [mixer.slider_id(name, "nose", part) for part in mixer.PARTS]
    assert result.sliders == ids
    assert [body.data.shape_keys.key_blocks[i].value for i in ids] == pytest.approx([0.5, 0.5])
    assert _sliders(body) == dict.fromkeys(ids, pytest.approx(0.5))
    package_ids, values = usd_hooks.sliders(body.juststage)  # the package's sliderIds / sliderValues
    assert [values[package_ids.index(i)] for i in ids] == pytest.approx([0.5, 0.5])


def test_features_keep_the_regions_place_proportions_are_a_similarity_and_both_sum_to_the_identity(human):
    made, body = human
    (name,) = _identities()
    before = build.shaped_coords(body)
    _mix(made, "nose", [name], [1.0], mode="features")
    features = build.shaped_coords(body) - before
    mask = mixer._mask_weights(body, "nose")
    inside = mask > 0.0
    assert np.abs(features[inside].sum(0)).max() < 1e-4  # no shift: the fit's residual sums to nothing
    assert np.abs(features[~inside]).max() < 1e-6
    _mix(made, "nose", [name], [1.0], mode="proportions")  # the features stay
    both = build.shaped_coords(body) - before
    proportions = both - features
    core = mask > 0.5  # an affine fit of the proportions over the mask's core, on the basis they were fitted on: exact
    basis = np.empty(len(body.data.vertices) * 3, np.float32)
    body.data.shape_keys.reference_key.data.foreach_get("co", basis)
    co = basis.reshape(-1, 3)[core].astype(np.float64)
    lhs = np.hstack([co, np.ones((len(co), 1))])
    fit, *_ = np.linalg.lstsq(lhs, proportions[core] / mask[core, None], rcond=None)
    assert np.abs(lhs @ fit - proportions[core] / mask[core, None]).max() < 2e-5
    assert np.abs(proportions[core]).max() > 0.0005
    offsets = np.zeros_like(both)
    index, delta = base.extend(body, *mixer._identity(name))
    offsets[index] = delta
    assert np.abs(both - mask[:, None] * offsets).max() < 1e-5  # features + proportions = the identity, masked


def test_the_wheels_weights_are_normalised_and_a_new_mix_replaces_the_last(human):
    made, body = human
    first, second = _identities(2)
    _mix(made, "chin", [first, second], [3.0, 1.0], strength=0.8)
    a = [mixer.slider_id(first, "chin", part) for part in mixer.PARTS]
    b = [mixer.slider_id(second, "chin", part) for part in mixer.PARTS]
    assert _sliders(body) == {**dict.fromkeys(a, pytest.approx(0.6)), **dict.fromkeys(b, pytest.approx(0.2))}
    _mix(made, "chin", [second], [1.0], strength=0.8, mode="features")  # proportions untouched
    assert _sliders(body) == {a[0]: pytest.approx(0.0), a[1]: pytest.approx(0.6), b[0]: pytest.approx(0.8),
                              b[1]: pytest.approx(0.2)}  # fmt: skip
    assert mixer.region_mix(body, "chin", "features") == {second: pytest.approx(0.8)}


def test_set_slider_on_the_mixers_ids_is_the_same_shape(human):
    made, body = human
    (name,) = _identities()
    before = build.shaped_coords(body)
    ids = [mixer.slider_id(name, "mouth", part) for part in mixer.PARTS]
    for slider in ids:
        api.run("juststage.body.set_slider", character=made.character, slider=slider, value=0.7)
    by_slider = build.shaped_coords(body) - before
    for slider in ids:
        api.run("juststage.body.set_slider", character=made.character, slider=slider, value=0.0)
    assert np.abs(build.shaped_coords(body) - before).max() < 1e-6
    _mix(made, "mouth", [name], [1.0], strength=0.7)
    assert np.abs((build.shaped_coords(body) - before) - by_slider).max() < 1e-6


def test_an_unknown_identity_region_mode_or_value_is_refused_by_name(human):
    made, _ = human
    (name,) = _identities()
    with pytest.raises(api.CommandError, match="no identity"):
        _mix(made, "nose", ["nobody"], [1.0])
    with pytest.raises(api.CommandError, match="no region"):
        _mix(made, "tail", [name], [1.0])
    with pytest.raises(api.CommandError, match="weights"):
        _mix(made, "nose", [name], [0.0])
    with pytest.raises(api.CommandError, match="mode"):
        _mix(made, "nose", [name], [1.0], mode="volume")
    with pytest.raises(api.CommandError, match="mixer one"):
        api.run("juststage.body.set_slider", character=made.character, slider="scans.nobody.nose.features", value=0.5)
    with pytest.raises(api.CommandError, match="value"):
        api.run("juststage.body.set_slider", character=made.character,
                slider=mixer.slider_id(name, "nose", "features"), value=-0.5)  # fmt: skip
