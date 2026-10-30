# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The UI door of a command (docs/standards/commands-and-api.md §2).

Each command has a thin operator whose `bpy.props` mirror its `Params` in Blender's own declaration style; its
`execute()` builds `Params` from them and runs the command. `mirror_mismatches` is what the per-command test checks.
"""

from __future__ import annotations

import bpy

from .. import api
from ..character import JustStageFloat
from ..core.commands import Command, FieldSpec

_KIND_OF_PROPERTY = {
    bpy.props.StringProperty: "str",
    bpy.props.IntProperty: "int",
    bpy.props.FloatProperty: "float",
    bpy.props.BoolProperty: "bool",
    bpy.props.EnumProperty: "choice",
    bpy.props.FloatVectorProperty: "list:float",
    bpy.props.IntVectorProperty: "list:int",
    bpy.props.BoolVectorProperty: "list:bool",
}


class CommandOperator:
    """Mixin for a command's operator: set `command_id`, declare the mirrored properties.

    A `list[float]` field is a `FloatVectorProperty` when it is short (Blender caps those at 32), or a
    `CollectionProperty(type=JustStageFloat)` when it isn't (Blender's own way to pass a list to an operator).
    """

    command_id: str = ""

    def execute(self, context):
        cmd = api.command(self.command_id)
        values = {f.name: _plain(getattr(self, f.name)) for f in cmd.fields}
        if cmd.start is not None and not bpy.app.background:  # an AI job: started now, followed by ai_jobs
            from . import ai_jobs

            try:
                params, job_id = api.begin(cmd, values)
            except (api.CommandError, api.RegistryError) as e:
                self.report({"ERROR"}, f"{cmd.id}: {e}")
                return {"CANCELLED"}
            ai_jobs.track(cmd, params, job_id)
            self.report({"INFO"}, f"{cmd.label}: started on JustStage's AI server")
            return {"FINISHED"}
        try:
            api.execute(cmd, values, push_undo=False)  # the operator's own UNDO flag makes the step
        except (api.CommandError, api.RegistryError) as e:
            self.report({"ERROR"}, f"{cmd.id}: {e}")
            return {"CANCELLED"}
        return {"FINISHED"}


def _plain(value):
    if isinstance(value, bpy.types.bpy_prop_collection):  # a long list: a collection of JustStageFloat items
        return [item.value for item in value]
    # bpy vector properties come back as bpy_prop_array
    return list(value) if hasattr(value, "__len__") and not isinstance(value, str) else value


def _kind(prop) -> str:
    if prop.function is bpy.props.CollectionProperty:
        return "list:float" if prop.keywords.get("type") is JustStageFloat else "collection"
    return _KIND_OF_PROPERTY.get(prop.function, repr(prop.function))


def _expected(spec: FieldSpec) -> str:
    return f"list:{spec.item}" if spec.kind == "list" else spec.kind


def mirror_mismatches(cmd: Command, operator_class: type) -> list[str]:
    """What differs between a command's `Params` and its operator's properties (empty when they match)."""
    problems = []
    if getattr(operator_class, "command_id", None) != cmd.id:
        problems.append(f"command_id is {getattr(operator_class, 'command_id', None)!r}, not {cmd.id!r}")
    if getattr(operator_class, "bl_idname", None) != cmd.operator_idname:
        problems.append(f"bl_idname is {getattr(operator_class, 'bl_idname', None)!r}, not {cmd.operator_idname!r}")
    wants_undo = bool(cmd.record["undo"])
    has_undo = "UNDO" in getattr(operator_class, "bl_options", set())
    if wants_undo != has_undo:
        problems.append(f"UNDO in bl_options is {has_undo}, the command's undo is {wants_undo}")
    props = {
        name: value
        for name, value in getattr(operator_class, "__annotations__", {}).items()
        if hasattr(value, "function") and hasattr(value, "keywords")
    }
    for spec in cmd.fields:
        prop = props.pop(spec.name, None)
        if prop is None:
            problems.append(f"no property for field {spec.name!r}")
            continue
        kind = _kind(prop)
        if kind != _expected(spec):
            problems.append(f"{spec.name}: property kind {kind}, field kind {_expected(spec)}")
        if spec.kind == "choice":
            items = tuple(item[0] for item in prop.keywords.get("items", ()))
            if items != spec.choices:
                problems.append(f"{spec.name}: enum items {items}, choices {spec.choices}")
        default = prop.keywords.get("default", None)
        if spec.required:
            continue
        if spec.kind == "list" and prop.function is bpy.props.CollectionProperty:
            if list(spec.default) != []:
                problems.append(f"{spec.name}: a collection starts empty; the field's default must be []")
            continue
        if spec.kind == "list":
            default = list(default) if default is not None else None
            if default != list(spec.default):
                problems.append(f"{spec.name}: default {default!r}, field default {spec.default!r}")
        elif default != spec.default:
            problems.append(f"{spec.name}: default {default!r}, field default {spec.default!r}")
    problems.extend(f"extra property {name!r} with no field" for name in props)
    return problems
