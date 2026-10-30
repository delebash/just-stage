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


@persistent
def _on_load(_=None):
    _ensure_addon()


def _on_timer():
    _ensure_addon()
    return None  # one shot


_HANDLERS = (
    bpy.app.handlers.load_factory_preferences_post,
    bpy.app.handlers.load_factory_startup_post,
    bpy.app.handlers.load_post,
)


def register():
    for handlers in _HANDLERS:
        if _on_load not in handlers:
            handlers.append(_on_load)
    bpy.app.timers.register(_on_timer, first_interval=0.0, persistent=True)


def unregister():
    for handlers in _HANDLERS:
        if _on_load in handlers:
            handlers.remove(_on_load)
