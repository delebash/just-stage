# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Modify panel (docs/plans/2026-11-03-cc5-window.md §3 step 1): CC5's icon tabs over what JustStage already has;
the Morph tab's regions (CC5's tree, the user's screenshots) cover every target.json group, and its search finds
sliders across them."""

import importlib

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
panel = importlib.import_module("bl_ext.system.juststage.ui.character_panel")
sliders = importlib.import_module("bl_ext.system.juststage.modules.body.sliders")


def test_the_tabs_are_cc5s():
    assert [t[0] for t in panel.TABS] == ["ATTRIBUTE", "MORPH", "SKIN", "MATERIAL", "HAIR", "EXPRESSIONS"]
    assert hasattr(bpy.types, "VIEW3D_PT_juststage_modify")


def test_every_slider_group_has_one_region():
    placed = [g for _label, groups in panel.REGIONS.values() for g in groups]
    assert len(placed) == len(set(placed))  # none twice
    assert set(sliders.groups()) <= set(placed)  # none left out


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Modify test")
    yield result, bpy.data.objects[result.object]
    bpy.data.objects.remove(bpy.data.objects[result.object])


def test_a_region_shows_its_sliders_and_search_crosses_regions(human):
    _result, obj = human
    nose = panel.visible_sliders(obj, "NOSE", "")
    assert nose and all(item.group == "nose" for item in nose)
    found = panel.visible_sliders(obj, "NOSE", "width")
    assert found and all("width" in item.label.lower() for item in found)
    assert {item.group for item in found} - {"nose"}  # the search isn't held to the region


theme = importlib.import_module("bl_ext.system.juststage.ui.theme")


def test_the_theme_is_dark_with_one_accent():
    theme.apply(bpy.context.preferences)
    t = bpy.context.preferences.themes[0]
    ui = t.user_interface
    assert tuple(ui.wcol_numslider.item)[:3] == pytest.approx(theme.ACCENT, abs=0.005)  # the slider's fill
    assert tuple(ui.wcol_radio.inner_sel)[:3] == pytest.approx(theme.ACCENT, abs=0.005)  # the selected tab
    assert max(tuple(ui.panel_header)[:3]) < 0.2  # quiet panel titles, not colour bars
    assert max(tuple(ui.panel_back)[:3]) < 0.2  # near-black panels
    assert t.view_3d.space.gradients.background_type == "LINEAR"  # CC5's blue-grey viewport


def test_slider_names_read_as_words():
    assert sliders.pretty("nose", "nose-nostrils-angle-down-up") == "Nostrils angle (down / up)"
    assert sliders.pretty("nose", "nose-point-width-decr-incr") == "Point width (− / +)"
    assert sliders.pretty("chin", "chin-triangle") == "Triangle"
    assert sliders.catalog()["arms/l-lowerarm-scale-depth-decr-incr"].label == "Lowerarm depth (− / +), left"
    assert sliders.pretty("nose", "nose-trans-backward-forward") == "Move (backward / forward)"
    assert sliders.pretty("nose", "nose-scale-vert-decr-incr") == "Height (− / +)"
