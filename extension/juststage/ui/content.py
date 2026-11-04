# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Content panel (Blender's Asset Browser on JustStage's library): a double-click applies an asset - CC5's way -
and so do its right-click entry and an Apply button in its header, all running `juststage.library.add` (a character
into the scene, hair or a skin onto the selected character). Built as Blender's own Pose Library builds its
double-click (`addons_core/pose_library/keymaps.py`: "Asset Browser Main", DOUBLE_CLICK; `gui.py`: an entry prepended
to `ASSETBROWSER_MT_context_menu`). Only JustStage's catalogues: another library's double-click stays Blender's.

While JustStage's interface is on (ui/topbar.py), the panel's header is JustStage's, as the 3D view's is
(ui/viewport_header.py): the editor switch, search, Apply (or the hint "Double-click to apply") and the display
settings; Blender's five menus (View, Select, Library, Catalog, Asset) come back with "Blender's full interface" - in
the narrow panel they pushed everything after them off the edge.

Dragging an asset into the viewport stays Blender's default (the bare object, `object.add_named`) - Blender has no
call to change an Asset Browser drop."""

from __future__ import annotations

import functools

import bpy

_keymaps: list = []
_ORIGINAL = {}


@functools.cache
def _ours() -> frozenset[str]:
    from ..core import library

    return frozenset(library.catalog_ids().values())


def catalog_of(asset) -> str:
    """The JustStage catalogue path an asset sits in ("" for any other)."""
    from ..core import library

    uid = asset.metadata.catalog_id if asset is not None else ""
    if uid not in _ours():
        return ""
    return next(path for path, value in library.catalog_ids().items() if value == uid)


def label_for(catalog: str) -> str:
    return "Add to scene" if catalog in ("Characters", "Bodies/Presets", "Heads/Presets") else "Apply to character"


def _context_menu(self, context):
    catalog = catalog_of(getattr(context, "asset", None))
    if not catalog:
        return
    layout = self.layout
    layout.operator("juststage.library_add", text=label_for(catalog), icon="IMPORT")
    layout.separator()


def draw_header(self, context):
    space = context.space_data
    if getattr(context.window_manager, "juststage_full_interface", True) or space.browse_mode != "ASSETS":
        _ORIGINAL["draw"](self, context)
        return
    layout = self.layout
    params = space.params
    if space.active_operator is None:
        layout.template_header()
    row = layout.row()
    row.ui_units_x = 6
    row.prop(params, "filter_search", text="", icon="VIEWZOOM")
    catalog = catalog_of(getattr(context, "asset", None))
    if catalog:
        layout.operator("juststage.library_add", text=label_for(catalog), icon="IMPORT")
    else:
        layout.label(text="Double-click to apply")
    layout.separator_spacer()
    layout.prop_with_popover(params, "display_type", panel="ASSETBROWSER_PT_display", text="", icon_only=True)


def install() -> None:
    if "draw" in _ORIGINAL:
        return
    _ORIGINAL["draw"] = bpy.types.FILEBROWSER_HT_header.draw
    bpy.types.FILEBROWSER_HT_header.draw = draw_header


def uninstall() -> None:
    if "draw" in _ORIGINAL:
        bpy.types.FILEBROWSER_HT_header.draw = _ORIGINAL.pop("draw")


def poll_from_content(context) -> bool:
    """`juststage.library_add` in the Content panel: only on JustStage's own assets; elsewhere (a button) always."""
    space = context.space_data
    if space is not None and space.type == "FILE_BROWSER":
        return bool(catalog_of(getattr(context, "asset", None)))
    return True


def register():
    bpy.types.ASSETBROWSER_MT_context_menu.prepend(_context_menu)
    keyconfig = bpy.context.window_manager.keyconfigs.addon
    if keyconfig is None:  # a background run has no window keymaps
        return
    km = keyconfig.keymaps.new(name="Asset Browser Main", space_type="FILE_BROWSER")
    _keymaps.append((km, km.keymap_items.new("juststage.library_add", "LEFTMOUSE", "DOUBLE_CLICK")))


def unregister():
    for km, kmi in _keymaps:
        km.keymap_items.remove(kmi)
    _keymaps.clear()
    bpy.types.ASSETBROWSER_MT_context_menu.remove(_context_menu)
