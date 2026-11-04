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
