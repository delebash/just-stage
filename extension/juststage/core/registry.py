# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The plugin and command registry (docs/standards/plugins.md §2–§3), Blender-free.

Built-in modules and outside plugins register the same way: `register_plugin(id, api, needs, provides)`, then their
commands. A plugin outside the API range, or one whose `needs` aren't on, is refused with the reason named.
"""

from __future__ import annotations

import types
from dataclasses import dataclass, field

from . import commands as _commands
from . import versions

#: The public plugin API's version (semver); a breaking change bumps the major (plugins.md §3).
API_VERSION = "1.0.0"


class RegistryError(RuntimeError):
    """A registration was refused; the message says why."""


@dataclass
class Plugin:
    id: str
    api: str
    needs: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()
    builtin: bool = False
    commands: list[str] = field(default_factory=list)


class Registry:
    def __init__(self, api_version: str = API_VERSION):
        self.api_version = api_version
        self.plugins: dict[str, Plugin] = {}
        self.commands: dict[str, _commands.Command] = {}

    # plugins -----------------------------------------------------------------------------------------------------

    def register_plugin(
        self,
        id: str,
        api: str,
        needs: tuple[str, ...] | list[str] = (),
        provides: tuple[str, ...] | list[str] = (),
        builtin: bool = False,
    ) -> Plugin:
        if id in self.plugins:
            raise RegistryError(f"plugin {id!r} is already registered")
        try:
            fits = versions.satisfies(self.api_version, api)
        except ValueError as e:
            raise RegistryError(f"plugin {id!r}: its api range {api!r} is malformed ({e})") from e
        if not fits:
            raise RegistryError(f"plugin {id!r} needs JustStage API {api}; this is {self.api_version}")
        missing = [n for n in needs if n not in self.plugins]
        if missing:
            raise RegistryError(f"plugin {id!r} needs {', '.join(missing)}, which is not on")
        plugin = Plugin(id, api, tuple(needs), tuple(provides), builtin)
        self.plugins[id] = plugin
        return plugin

    def needed_by(self, id: str) -> list[str]:
        """The plugins that need `id` — switched off with it, after the user is asked (plugins.md §2)."""
        return [p.id for p in self.plugins.values() if id in p.needs]

    def unregister_plugin(self, id: str) -> None:
        if id not in self.plugins:
            return
        blocked = self.needed_by(id)
        if blocked:
            raise RegistryError(f"plugin {id!r} is needed by {', '.join(blocked)}; switch those off first")
        for command_id in self.plugins[id].commands:
            self.commands.pop(command_id, None)
        del self.plugins[id]

    # commands ----------------------------------------------------------------------------------------------------

    def register_command(self, module: types.ModuleType, plugin: str) -> _commands.Command:
        if plugin not in self.plugins:
            raise RegistryError(f"command module {module.__name__}: plugin {plugin!r} is not registered")
        command = _commands.load(module)
        if command.id in self.commands:
            raise RegistryError(f"command {command.id!r} is already registered")
        self.commands[command.id] = command
        self.plugins[plugin].commands.append(command.id)
        return command

    def command(self, command_id: str) -> _commands.Command:
        try:
            return self.commands[command_id]
        except KeyError:
            raise RegistryError(f"no command {command_id!r}") from None
