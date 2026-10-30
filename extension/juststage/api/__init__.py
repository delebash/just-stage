# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.api` — the public, versioned API for built-in modules, outside plugins and Python callers
(docs/standards/plugins.md §3). Outside plugins reach it as `bl_ext.system.juststage.api`.
"""

from __future__ import annotations

import types
from typing import Any

from ..core import commands as _commands
from ..core import registry as _registry

VERSION = _registry.API_VERSION

CommandError = _commands.CommandError
RegistryError = _registry.RegistryError

_REGISTRY = _registry.Registry()


def register_plugin(id: str, api: str, needs=(), provides=(), *, builtin: bool = False) -> _registry.Plugin:
    """Register a plugin (or a built-in module) before its commands; see plugins.md §2."""
    return _REGISTRY.register_plugin(id, api, needs, provides, builtin)


def unregister_plugin(id: str) -> None:
    _REGISTRY.unregister_plugin(id)


def register_command(module: types.ModuleType, plugin: str) -> _commands.Command:
    """Register a command module (`Params`, `Result`, `COMMAND`, `main`) for `plugin`."""
    return _REGISTRY.register_command(module, plugin)


def juststage_version() -> str:
    """The add-on's own version, from its stock manifest."""
    import pathlib
    import tomllib

    manifest = pathlib.Path(__file__).resolve().parents[1] / "blender_manifest.toml"
    return tomllib.loads(manifest.read_text(encoding="utf-8"))["version"]


def plugins() -> list[_registry.Plugin]:
    return list(_REGISTRY.plugins.values())


def commands() -> list[_commands.Command]:
    return list(_REGISTRY.commands.values())


def command(command_id: str) -> _commands.Command:
    return _REGISTRY.command(command_id)


def run(command_id: str, /, **params: Any):
    """Run a command from JSON-shaped parameters and return its `Result`.

    The Python and MCP doors come through here; a data-changing command gets one undo step after it
    (commands-and-api.md §2). The operator door runs the command under Blender's own UNDO flag instead.
    """
    return execute(command(command_id), params, push_undo=True)


def execute(cmd: _commands.Command, values: dict[str, Any], *, push_undo: bool):
    result = cmd.main(_commands.build_params(cmd, values))
    if not isinstance(result, cmd.result_type):
        raise CommandError(f"{cmd.id}: main returned {type(result).__name__}, not its Result")
    if push_undo and cmd.record["undo"]:
        _undo_push(cmd.label)
    return result


def begin(cmd: _commands.Command, values: dict[str, Any]):
    """An AI job command's first half: its `Params` and the job id JustStage's server gave it."""
    if cmd.start is None:
        raise CommandError(f"{cmd.id} isn't a job command")
    params = _commands.build_params(cmd, values)
    return params, cmd.start(params)


def complete(cmd: _commands.Command, params, png: bytes):
    """An AI job command's second half: its picture applied, one undo step after it."""
    result = cmd.finish(params, png)
    if not isinstance(result, cmd.result_type):
        raise CommandError(f"{cmd.id}: finish returned {type(result).__name__}, not its Result")
    if cmd.record["undo"]:
        _undo_push(cmd.label)
    return result


def _undo_push(message: str) -> None:
    try:
        import bpy
    except ImportError:  # plain CPython (unit tests): no undo stack
        return
    if bpy.app.background:  # headless Blender keeps no undo history worth a step
        return
    bpy.ops.ed.undo_push(message=message)


def _registry_for_tests() -> _registry.Registry:
    return _REGISTRY
