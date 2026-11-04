# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The 3D view's header in JustStage's interface (docs/plans/2026-11-03-cc5-window.md §3 step 4): camera Home / Frame,
the view list, Preview (Clay / Skin / Film) and MetaHuman's framing presets (Face, Body, Hands, Feet)."""

import importlib

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
header = importlib.import_module("bl_ext.system.juststage.ui.viewport_header")


def test_install_swaps_the_header_and_uninstall_restores_it():
    original = bpy.types.VIEW3D_HT_header.draw
    header.install()
    try:
        assert bpy.types.VIEW3D_HT_header.draw is header.draw
    finally:
        header.uninstall()
    assert bpy.types.VIEW3D_HT_header.draw is original


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Header test")
    yield bpy.data.objects[result.object]
    bpy.data.objects.remove(bpy.data.objects[result.object])


def test_the_framings_sit_where_their_parts_are(human):
    boxes = {t: header.frame_box(human, t) for t in ("FACE", "BODY", "HANDS", "FEET")}
    face, body, feet = boxes["FACE"], boxes["BODY"], boxes["FEET"]
    assert face[0].z > body[0].z > feet[0].z  # the face high, the feet low
    assert face[1] < body[1] and feet[1] < body[1]  # close-ups are smaller than the whole body
    assert bpy.ops.juststage.view_frame.idname() == "JUSTSTAGE_OT_view_frame"
