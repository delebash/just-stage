# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Content panel's apply (ui/content.py): only JustStage's catalogues answer a double-click, with a label by
catalogue; the welcome's buttons (outside the Asset Browser) always run."""

import importlib
from types import SimpleNamespace

import bpy

content = importlib.import_module("bl_ext.system.juststage.ui.content")
library = importlib.import_module("bl_ext.system.juststage.core.library")


def _asset(uid):
    return SimpleNamespace(metadata=SimpleNamespace(catalog_id=uid))


def _context(space_type, asset):
    return SimpleNamespace(space_data=SimpleNamespace(type=space_type), asset=asset)


def test_only_juststage_catalogues_apply():
    ids = library.catalog_ids()
    assert content.catalog_of(_asset(ids["Hair/Scalp"])) == "Hair/Scalp"
    assert content.catalog_of(_asset("00000000-0000-0000-0000-000000000000")) == ""
    assert content.catalog_of(None) == ""
    assert content.poll_from_content(_context("FILE_BROWSER", _asset(ids["Skins"])))
    assert not content.poll_from_content(_context("FILE_BROWSER", _asset("not ours")))
    assert not content.poll_from_content(_context("FILE_BROWSER", None))
    assert content.poll_from_content(_context("VIEW_3D", None))  # the welcome's "Start from" buttons


def test_labels_by_catalogue():
    assert content.label_for("Characters") == "Add to scene"
    assert content.label_for("Hair/Beards") == content.label_for("Skins") == "Apply to character"


def test_the_entry_is_in_blenders_context_menu():
    assert content._context_menu in bpy.types.ASSETBROWSER_MT_context_menu._dyn_ui_initialize()


def test_the_header_before_the_browser_has_drawn_falls_back_to_blenders():
    """The Asset Browser's `params` are None until it has drawn once (ui/startup.py `content_panel`); the header then
    draws Blender's own instead of handing None to `prop` (the error seen 2026-11-04 opening a saved scene)."""
    calls = []
    layout = SimpleNamespace(template_header=lambda: calls.append("template_header"),
                             row=lambda: SimpleNamespace(prop=lambda data, *a, **k: calls.append(("prop", data))))
    stub = SimpleNamespace(layout=layout)
    context = SimpleNamespace(window_manager=SimpleNamespace(juststage_full_interface=False),
                              space_data=SimpleNamespace(browse_mode="ASSETS", params=None, active_operator=None))
    saved = dict(content._ORIGINAL)
    content._ORIGINAL["draw"] = lambda self, ctx: calls.append("blenders")
    try:
        content.draw_header(stub, context)
    finally:
        content._ORIGINAL.clear()
        content._ORIGINAL.update(saved)
    assert calls == ["blenders"]


def test_the_header_is_installed_with_juststages_interface():
    """The template installs it with the top bar (ui/topbar.py); uninstalling gives Blender's back."""
    blenders = bpy.types.FILEBROWSER_HT_header.draw
    content.install()
    try:
        assert bpy.types.FILEBROWSER_HT_header.draw is content.draw_header
    finally:
        content.uninstall()
    assert bpy.types.FILEBROWSER_HT_header.draw is blenders
