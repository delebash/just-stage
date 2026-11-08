# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Mixer panel (ui/mixer_panel.py): CC5's parts in its order, each identity's share of the part read from and
written to the character's mixer sliders through `juststage.body.set_mix` (no state of its own), the shares capped at
1 together (the rest stays the character's), the strength scaling them all, the Blend Type choosing the part, Reset
clearing it, and the body's parts closed while no identity reaches them."""

import importlib

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
mixer = importlib.import_module("bl_ext.system.juststage.modules.body.mixer")
panel = importlib.import_module("bl_ext.system.juststage.ui.mixer_panel")


@pytest.fixture
def human():
    made = api.run("juststage.body.create", name="Mixer panel test")
    body = bpy.data.objects[made.object]
    bpy.context.view_layer.objects.active = body
    wm = bpy.context.window_manager
    wm.juststage_mix_region, wm.juststage_mix_mode = "nose", "both"
    yield made, body, wm
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(body)


def _values(body, part):
    return {item.id: item.value for item in body.juststage.sliders if item.id.endswith(f".nose.{part}")}


def test_the_parts_are_cc5s_in_its_order_and_every_identity_has_a_share():
    assert hasattr(bpy.types, "VIEW3D_PT_juststage_mixer")
    keys = [key for key, _label in panel._parts()]
    assert keys == [key for key, _label in panel.PARTS if key in mixer.regions()]
    assert set(keys) == set(mixer.regions())
    for name in mixer.identities():
        assert hasattr(bpy.context.window_manager, panel.prop_name(name))


def test_a_share_writes_the_characters_sliders_and_reads_them_back(human):
    _made, body, wm = human
    first, second = mixer.identities()[:2]
    setattr(wm, panel.prop_name(first), 0.4)
    assert getattr(wm, panel.prop_name(first)) == pytest.approx(0.4)
    for part in mixer.PARTS:  # Both: both parts
        assert _values(body, part) == {mixer.slider_id(first, "nose", part): pytest.approx(0.4)}
    setattr(wm, panel.prop_name(second), 0.8)  # capped: the shares sum to 1 at most
    assert getattr(wm, panel.prop_name(second)) == pytest.approx(0.6)
    assert wm.juststage_mix_strength == pytest.approx(1.0)
    wm.juststage_mix_strength = 0.5  # every share scaled, the balance kept
    assert getattr(wm, panel.prop_name(first)) == pytest.approx(0.2)
    assert getattr(wm, panel.prop_name(second)) == pytest.approx(0.3)


def test_the_blend_type_chooses_the_part_and_reset_clears_it(human):
    made, body, wm = human
    (first,) = mixer.identities()[:1]
    setattr(wm, panel.prop_name(first), 0.5)
    wm.juststage_mix_mode = "features"
    setattr(wm, panel.prop_name(first), 0.0)
    assert _values(body, "features") == {}
    assert _values(body, "proportions") == {mixer.slider_id(first, "nose", "proportions"): pytest.approx(0.5)}
    bpy.ops.juststage.body_set_mix(character=made.character, region="nose", mode="both")  # the panel's Reset
    assert _values(body, "proportions") == {}


def test_the_body_parts_are_closed_while_no_identity_reaches_them():
    reach = mixer.reach()
    assert reach["nose"] and reach["eyes"]  # the identities are head scans
    assert all(not reach[part] for part in ("torso", "arms", "legs"))
