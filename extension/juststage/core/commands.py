# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The command declaration (docs/standards/commands-and-api.md §2), Blender-free.

A command is a module with `Params` and `Result` (NamedTuples), a `COMMAND` record and `main(params) -> Result` —
Blender Lab's tool convention. This module loads such a module, describes its parameters (for the operator mirror and
the MCP registrar), and turns JSON-shaped values into a checked `Params`.
"""

from __future__ import annotations

import types
import typing
from dataclasses import dataclass, field
from typing import Any, Literal, get_args, get_origin

#: The JSON types a `Params` field may use; `list[...]` of the numeric and bool ones, and `Literal[...]` of strings.
SCALARS = (str, int, float, bool)
LIST_ITEMS = (int, float, bool)
RECORD_KEYS = {"id", "label", "menu", "permission", "undo", "headless", "since", "deprecated"}

_MISSING = object()


class CommandError(ValueError):
    """A command's declaration or a call's parameters are wrong; the message names the field."""


@dataclass(frozen=True)
class FieldSpec:
    """One `Params` field, described in JSON terms."""

    name: str
    kind: str  # "str" | "int" | "float" | "bool" | "choice" | "list"
    default: Any = _MISSING
    choices: tuple[str, ...] = ()
    item: str = ""  # the item kind of a "list"

    @property
    def required(self) -> bool:
        return self.default is _MISSING


@dataclass(frozen=True)
class Command:
    id: str
    module: types.ModuleType
    params_type: type
    result_type: type
    record: dict
    main: typing.Callable
    fields: tuple[FieldSpec, ...] = field(default=())
    #: an AI job command's two halves (commands-and-api.md §2): `start(params) -> job id` submits the job to
    #: JustStage's server, `finish(params, png) -> Result` applies its picture — the UI runs them around a Blender
    #: timer, so Blender never waits; `main` still runs the whole command for scripts and headless runs
    start: typing.Callable | None = None
    finish: typing.Callable | None = None

    @property
    def label(self) -> str:
        return self.record["label"]

    @property
    def operator_idname(self) -> str:
        """`juststage.body.set_slider` → `juststage.body_set_slider` (Blender's `category.name` rule)."""
        return operator_idname(self.id)


def operator_idname(command_id: str) -> str:
    head, _, rest = command_id.partition(".")
    return f"{head}.{rest.replace('.', '_')}"


def _is_namedtuple(t: object) -> bool:
    return isinstance(t, type) and issubclass(t, tuple) and hasattr(t, "_fields")


def _kind(name: str, hint: Any) -> tuple[str, tuple[str, ...], str]:
    if hint in SCALARS:
        return hint.__name__, (), ""
    origin = get_origin(hint)
    if origin is Literal:
        choices = get_args(hint)
        if not choices or not all(isinstance(c, str) for c in choices):
            raise CommandError(f"field {name!r}: Literal choices must be strings")
        return "choice", tuple(choices), ""
    if origin is list:
        (item,) = get_args(hint) or (None,)
        if item not in LIST_ITEMS:
            raise CommandError(f"field {name!r}: a list holds int, float or bool, not {item!r}")
        return "list", (), item.__name__
    raise CommandError(f"field {name!r}: type {hint!r} is not a JSON type a command may take")


def describe(params_type: type) -> tuple[FieldSpec, ...]:
    """Describe a `Params` NamedTuple's fields; raises `CommandError` for a type a command may not take."""
    if not _is_namedtuple(params_type):
        raise CommandError("Params must be a NamedTuple")
    hints = typing.get_type_hints(params_type)
    defaults = params_type._field_defaults
    specs = []
    for name in params_type._fields:
        kind, choices, item = _kind(name, hints[name])
        default = defaults.get(name, _MISSING)
        if kind == "choice" and default is not _MISSING and default not in choices:
            raise CommandError(f"field {name!r}: default {default!r} is not one of {choices}")
        specs.append(FieldSpec(name, kind, default, choices, item))
    return tuple(specs)


def load(module: types.ModuleType) -> Command:
    """Check a command module and return its `Command`."""
    for attr in ("Params", "Result", "COMMAND", "main"):
        if not hasattr(module, attr):
            raise CommandError(f"{module.__name__}: a command module needs {attr}")
    record = dict(module.COMMAND)
    unknown = set(record) - RECORD_KEYS
    if unknown:
        raise CommandError(f"{module.__name__}: unknown COMMAND keys {sorted(unknown)}")
    for key in ("id", "label"):
        if not isinstance(record.get(key), str) or not record[key]:
            raise CommandError(f"{module.__name__}: COMMAND needs a {key!r} string")
    if not record["id"].count(".") >= 2:
        raise CommandError(f"{module.__name__}: a command id is '<namespace>.<area>.<verb>', not {record['id']!r}")
    record.setdefault("undo", False)
    record.setdefault("headless", True)
    record.setdefault("permission", record["id"].split(".")[1])
    if not _is_namedtuple(module.Result):
        raise CommandError(f"{module.__name__}: Result must be a NamedTuple")
    start, finish = getattr(module, "start", None), getattr(module, "finish", None)
    if (start is None) != (finish is None):
        raise CommandError(f"{module.__name__}: a job command has both start and finish")
    return Command(
        id=record["id"],
        module=module,
        params_type=module.Params,
        result_type=module.Result,
        record=record,
        main=module.main,
        fields=describe(module.Params),
        start=start,
        finish=finish,
    )


def _check(spec: FieldSpec, value: Any) -> Any:
    def bad(expected: str) -> CommandError:
        return CommandError(f"{spec.name}: expected {expected}, got {value!r}")

    if spec.kind == "bool":
        if not isinstance(value, bool):
            raise bad("true or false")
        return value
    if spec.kind == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise bad("an integer")
        return value
    if spec.kind == "float":
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise bad("a number")
        return float(value)
    if spec.kind == "str":
        if not isinstance(value, str):
            raise bad("a string")
        return value
    if spec.kind == "choice":
        if value not in spec.choices:
            raise bad("one of " + ", ".join(spec.choices))
        return value
    if spec.kind == "list":
        if not isinstance(value, list | tuple):
            raise bad(f"a list of {spec.item}")
        item_spec = FieldSpec(spec.name, spec.item)
        return [_check(item_spec, v) for v in value]
    raise bad(spec.kind)  # unreachable for a described field


def build_params(command: Command, values: dict[str, Any]) -> Any:
    """JSON-shaped values → a checked `Params`; unknown and missing fields are refused by name."""
    unknown = set(values) - {f.name for f in command.fields}
    if unknown:
        raise CommandError(f"{command.id}: unknown parameters {sorted(unknown)}")
    kwargs = {}
    for spec in command.fields:
        if spec.name in values:
            kwargs[spec.name] = _check(spec, values[spec.name])
        elif spec.required:
            raise CommandError(f"{command.id}: missing parameter {spec.name!r}")
    return command.params_type(**kwargs)


def to_json(value: Any) -> Any:
    """A `Result` (or anything in it) → plain JSON-shaped data."""
    if _is_namedtuple(type(value)):
        return {k: to_json(v) for k, v in value._asdict().items()}
    if isinstance(value, list | tuple):
        return [to_json(v) for v in value]
    if isinstance(value, dict):
        return {str(k): to_json(v) for k, v in value.items()}
    return value
