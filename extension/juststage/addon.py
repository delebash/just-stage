# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Registration with Blender: the core (always on) first, then the built-in modules through the public plugin API."""

import bpy

from . import api, character
from .commands import api_status
from .modules import body, head, skin
from .ui import operators

CORE = "core"
_CORE_COMMANDS = (api_status,)
#: Built-in modules in dependency order; each registers through the same `register_plugin` outside plugins use.
MODULES = (body, head, skin)


def _api_range() -> str:
    major = int(api.VERSION.split(".")[0])
    return f">={major}.0,<{major + 1}"


def register():
    character.register()
    api.register_plugin(CORE, api=_api_range(), builtin=True)
    for module in _CORE_COMMANDS:
        api.register_command(module, CORE)
    for cls in operators.CLASSES:
        bpy.utils.register_class(cls)
    for module in MODULES:
        module.register(_api_range())


def unregister():
    for module in reversed(MODULES):
        module.unregister()
    for cls in reversed(operators.CLASSES):
        bpy.utils.unregister_class(cls)
    for plugin in reversed(api.plugins()):
        api.unregister_plugin(plugin.id)
    character.unregister()
