# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The JustStage application template (docs/standards/plugins.md §5).

The template switches the JustStage add-on on itself — the manual: "You may enable add-ons associated with your
template", changing defaults "via handler" (`load_factory_preferences_post`, `load_factory_startup_post`). A template's
`register()` runs before Blender's extension system is up (measured on 5.3: enabling from `register()` fails with "No
module named 'bl_pkg'"), so the handlers, and a one-shot timer for an interactive start, do it once Blender is ready.
The splash, startup file, workspaces, theme and keymaps join this template as the workspaces are built.
"""

import bpy
from bpy.app.handlers import persistent

ADDON = "bl_ext.system.juststage"


def _ensure_addon():
    import addon_utils

    if not addon_utils.check(ADDON)[1]:
        addon_utils.enable(ADDON, default_set=True, persistent=True)


def _viewport():
    import importlib

    return importlib.import_module(ADDON + ".core.viewport")


def _ui(name):
    import importlib

    return importlib.import_module(ADDON + ".ui." + name)


def _topbar():
    _ui("topbar").install()  # JustStage's short top bar (Window brings Blender's back)
    _ui("startup").open_sidebar()  # the 3D view's sidebar on JustStage's Modify panel


@persistent
def _on_load(_=None):
    _ensure_addon()
    _topbar()


@persistent
def _on_factory_preferences(_=None):
    """First start (or preferences reset): Cycles on the card (not Blender's factory "None"); JustStage's look."""
    _ensure_addon()
    _viewport().use_gpu()
    _ui("theme").apply(bpy.context.preferences)
    bpy.context.preferences.view.show_splash = False  # Blender's splash; File > Open Recent keeps the recent files


@persistent
def _on_factory_startup(_=None):
    """A new file: F12 renders the film look on the card; the 3D view is the live view in the scene's light."""
    _ensure_addon()
    viewport = _viewport()
    viewport.setup_scene(bpy.context.scene)
    viewport.show_live(bpy.data.screens)
    startup = _ui("startup")
    startup.new_stage(bpy.context.scene)  # Blender's cube out, the camera on a standing person
    startup.content_panel(bpy.data.screens)  # the Properties editor becomes the Content panel (Asset Browser)


def _on_timer():
    _ensure_addon()
    _topbar()
    return None  # one shot


_HANDLERS = (
    (bpy.app.handlers.load_factory_preferences_post, _on_factory_preferences),
    (bpy.app.handlers.load_factory_startup_post, _on_factory_startup),
    (bpy.app.handlers.load_post, _on_load),
)


def register():
    for handlers, handler in _HANDLERS:
        if handler not in handlers:
            handlers.append(handler)
    bpy.app.timers.register(_on_timer, first_interval=0.0, persistent=True)


def unregister():
    for handlers, handler in _HANDLERS:
        if handler in handlers:
            handlers.remove(handler)
