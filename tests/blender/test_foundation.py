# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The foundation inside Blender: the add-on loads from the System repository, a command runs through the Python
door and the operator door, and every command's operator mirrors its Params."""

import importlib
import os

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
command_operator = importlib.import_module("bl_ext.system.juststage.ui.command_operator")


def _operator_classes():
    found, todo = {}, list(command_operator.CommandOperator.__subclasses__())
    while todo:
        cls = todo.pop()
        todo.extend(cls.__subclasses__())
        if cls.command_id:
            found[cls.command_id] = cls
    return found


def test_status_through_the_python_door():
    result = api.run("juststage.api.status")
    assert result.api == api.VERSION
    assert result.juststage == "0.1.0"
    assert result.blender.startswith("5.3")
    assert "core" in result.plugins


def test_status_through_the_operator_door():
    assert bpy.ops.juststage.api_status() == {"FINISHED"}


def test_unknown_parameter_is_refused_by_name():
    with pytest.raises(api.CommandError, match="unknown parameters"):
        api.run("juststage.api.status", colour="red")


@pytest.mark.parametrize("command_id", [c.id for c in api.commands()])
def test_operator_mirrors_params(command_id):
    cmd = api.command(command_id)
    classes = _operator_classes()
    assert command_id in classes, f"no operator for {command_id}"
    assert command_operator.mirror_mismatches(cmd, classes[command_id]) == []


def test_the_template_is_found_in_juststages_own_user_folder():
    found = [p for p in bpy.utils.app_template_paths() if os.path.isdir(os.path.join(p, "juststage"))]
    assert found, list(bpy.utils.app_template_paths())


def test_the_addon_sits_in_the_system_repository():
    repo = next(r for r in bpy.context.preferences.extensions.repos if r.module == "system")
    assert repo.source == "SYSTEM"
    assert os.path.isdir(os.path.join(repo.directory, "juststage"))
