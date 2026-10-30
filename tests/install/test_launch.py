# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Launching JustStage the launcher's way (docs/standards/plugins.md §5): Blender on JustStage's own folders with
`--app-template juststage` comes up with the template active and the add-on on — on a fresh preferences folder too."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import dev  # noqa: E402

CHECK = (
    "import addon_utils, bpy; "
    "print('LAUNCH', bpy.context.preferences.app_template, addon_utils.check('bl_ext.system.juststage')[1])"
)

pytestmark = pytest.mark.skipif(not dev.blender_path().exists(), reason="Blender isn't installed here")


def _launch(user: Path) -> str:
    env = dev.env()
    env["BLENDER_USER_RESOURCES"] = str(user)
    out = subprocess.run(
        [str(dev.blender_path()), "-b", "--app-template", "juststage", "--python-expr", CHECK],
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    ).stdout
    return next(line for line in out.splitlines() if line.startswith("LAUNCH"))


def test_a_fresh_install_starts_on_the_template_with_the_addon_on(tmp_path):
    user = tmp_path / "user"
    template = user / "scripts" / "startup" / "bl_app_templates_user" / "juststage"
    template.parent.mkdir(parents=True)
    shutil.copytree(ROOT / "template" / "juststage", template)
    assert _launch(user) == "LAUNCH juststage True"
    assert _launch(user) == "LAUNCH juststage True"  # and again, with the preferences that first start left
