# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Registration with Blender: the core (always on) first, then the built-in modules through the public plugin API."""

import bpy

from . import api, character, migrations
from .commands import api_status
from .core import usd_hooks
from .modules import body, hair, head, io, rig, skin
from .ui import ai_jobs, ai_panel, character_panel, content, menus, operators, viewport_header

CORE = "core"
_CORE_COMMANDS = (api_status,)
#: Built-in modules in dependency order; each registers through the same `register_plugin` outside plugins use.
MODULES = (body, head, rig, skin, hair, io)


def _api_range() -> str:
    major = int(api.VERSION.split(".")[0])
    return f">={major}.0,<{major + 1}"


def register():
    character.register()
    api.register_plugin(CORE, api=_api_range(), builtin=True)
    for module in _CORE_COMMANDS:
        api.register_command(module, CORE)
    for cls in (*operators.CLASSES, *ai_panel.CLASSES, *viewport_header.CLASSES, *usd_hooks.CLASSES):
        bpy.utils.register_class(cls)
    for module in MODULES:
        module.register(_api_range())
    menus.register()
    character_panel.register()
    content.register()
    migrations.register()


def unregister():
    migrations.unregister()
    content.unregister()
    character_panel.unregister()
    menus.unregister()
    for module in reversed(MODULES):
        module.unregister()
    ai_jobs.stop()
    for cls in reversed((*operators.CLASSES, *ai_panel.CLASSES, *viewport_header.CLASSES, *usd_hooks.CLASSES)):
        bpy.utils.unregister_class(cls)
    for plugin in reversed(api.plugins()):
        api.unregister_plugin(plugin.id)
    character.unregister()
