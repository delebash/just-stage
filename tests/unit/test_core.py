# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Blender-free core: the command declaration, parameter checks, the registry's refusals, version ranges."""

import types
from typing import Literal, NamedTuple

import pytest
from juststage.core import commands, registry, versions


def make_command(params, *, id="juststage.test.do", undo=False, result=None):
    class Result(NamedTuple):
        ok: bool

    module = types.ModuleType("fake_command")
    module.Params = params
    module.Result = result or Result
    module.COMMAND = dict(id=id, label="Do", undo=undo)
    module.main = lambda p: module.Result(True)
    return module


class Shape(NamedTuple):
    character: str
    value: float
    steps: int = 3
    mirror: bool = False
    side: Literal["left", "right", "both"] = "both"
    weights: list[float] = [0.0, 1.0]


def test_fields_are_described():
    cmd = commands.load(make_command(Shape))
    kinds = {f.name: (f.kind, f.required) for f in cmd.fields}
    assert kinds == {
        "character": ("str", True),
        "value": ("float", True),
        "steps": ("int", False),
        "mirror": ("bool", False),
        "side": ("choice", False),
        "weights": ("list", False),
    }
    assert cmd.operator_idname == "juststage.test_do"


def test_params_are_checked_and_converted():
    cmd = commands.load(make_command(Shape))
    p = commands.build_params(cmd, {"character": "eve", "value": 1, "side": "left", "weights": [1, 2]})
    assert p.value == 1.0 and isinstance(p.value, float)
    assert p.weights == [1.0, 2.0]
    assert p.steps == 3


@pytest.mark.parametrize(
    "values, message",
    [
        ({"value": 1.0}, "missing parameter 'character'"),
        ({"character": "eve", "value": "big"}, "value: expected a number"),
        ({"character": "eve", "value": True}, "value: expected a number"),
        ({"character": "eve", "value": 1.0, "steps": 2.5}, "steps: expected an integer"),
        ({"character": "eve", "value": 1.0, "side": "up"}, "side: expected one of left, right, both"),
        ({"character": "eve", "value": 1.0, "colour": "red"}, "unknown parameters"),
    ],
)
def test_bad_params_are_refused_by_name(values, message):
    cmd = commands.load(make_command(Shape))
    with pytest.raises(commands.CommandError, match=message):
        commands.build_params(cmd, values)


def test_a_type_json_cant_carry_is_refused():
    class Bad(NamedTuple):
        names: list[str]

    with pytest.raises(commands.CommandError, match="a list holds int, float or bool"):
        commands.load(make_command(Bad))


def test_a_malformed_command_id_is_refused():
    with pytest.raises(commands.CommandError, match="namespace"):
        commands.load(make_command(Shape, id="juststage.do"))


def test_result_to_json():
    class Inner(NamedTuple):
        x: int

    class Outer(NamedTuple):
        name: str
        inner: Inner
        items: list[Inner]

    assert commands.to_json(Outer("a", Inner(1), [Inner(2)])) == {"name": "a", "inner": {"x": 1}, "items": [{"x": 2}]}


@pytest.mark.parametrize(
    "version, spec, fits",
    [("1.0.0", ">=1.0,<2", True), ("2.0.0", ">=1.0,<2", False), ("1.4.2", ">1.4", True), ("1.4", "==1.4.0", True)],
)
def test_version_ranges(version, spec, fits):
    assert versions.satisfies(version, spec) is fits


def test_registry_refusals():
    reg = registry.Registry("1.2.0")
    reg.register_plugin("core", ">=1.0,<2", builtin=True)
    with pytest.raises(registry.RegistryError, match="needs JustStage API >=2.0"):
        reg.register_plugin("future", ">=2.0")
    with pytest.raises(registry.RegistryError, match="needs head, which is not on"):
        reg.register_plugin("photo_to_head", ">=1.0,<2", needs=["head"])
    reg.register_plugin("head", ">=1.0,<2", needs=["core"])
    reg.register_plugin("photo_to_head", ">=1.0,<2", needs=["head"])
    assert reg.needed_by("head") == ["photo_to_head"]
    with pytest.raises(registry.RegistryError, match="needed by photo_to_head"):
        reg.unregister_plugin("head")
    reg.register_command(make_command(Shape), "head")
    with pytest.raises(registry.RegistryError, match="already registered"):
        reg.register_command(make_command(Shape), "head")
    reg.unregister_plugin("photo_to_head")
    reg.unregister_plugin("head")
    assert "juststage.test.do" not in reg.commands
