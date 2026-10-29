# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The dev run: Blender on JustStage's own folders, the way the launcher starts it (docs/standards/plugins.md §5).

    python tools/dev.py setup            # .dev/ folders, links to the add-on and template, pytest for Blender's Python
    python tools/dev.py blender [args]   # Blender with JustStage's folders and the template
    python tools/dev.py test [pytest args]  # the in-Blender tests, headless

`BLENDER_USER_RESOURCES` keeps the dev run's settings apart from any Blender the user has; `BLENDER_SYSTEM_EXTENSIONS`
holds the System repository (Blender uses its `system` folder — measured on 5.3) with `juststage` linked in;
`BLENDER_SYSTEM_SCRIPTS` holds the template under `startup/bl_app_templates_system/`.
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / ".dev"
USER = DEV / "user"
SYSTEM_EXTENSIONS = DEV / "system-extensions"
SYSTEM_SCRIPTS = DEV / "system-scripts"
PYDEPS = DEV / "pydeps"
LINKS = {
    SYSTEM_EXTENSIONS / "system" / "juststage": ROOT / "extension" / "juststage",
    SYSTEM_SCRIPTS / "startup" / "bl_app_templates_system" / "juststage": ROOT / "template" / "juststage",
}
TEST_DEPS = ["pytest==9.1.1"]


def blender_path() -> Path:
    env = os.environ.get("JUSTSTAGE_BLENDER")
    if env:
        return Path(env)
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["juststage"]
    key = "blender_path_" + {"Windows": "windows", "Darwin": "macos"}.get(platform.system(), "linux")
    if key not in config:
        sys.exit(f"set JUSTSTAGE_BLENDER to Blender {config['blender']}'s executable")
    return Path(config[key])


def blender_python(blender: Path) -> Path:
    found = sorted(blender.parent.glob("*/python/bin/python*"))
    found = [p for p in found if p.name in ("python.exe", "python3", "python") or p.name.startswith("python3.")]
    if not found:
        sys.exit(f"no bundled Python next to {blender}")
    return found[0]


def _link(link: Path, target: Path) -> None:
    if link.exists() or link.is_symlink():
        return
    link.parent.mkdir(parents=True, exist_ok=True)
    if platform.system() == "Windows":
        # a directory junction needs no admin rights
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True, capture_output=True)
    else:
        link.symlink_to(target, target_is_directory=True)


def setup() -> None:
    USER.mkdir(parents=True, exist_ok=True)
    for link, target in LINKS.items():
        _link(link, target)
    python = blender_python(blender_path())
    subprocess.run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--quiet",
            "--disable-pip-version-check",
            "--upgrade",
            "--target",
            str(PYDEPS),
            *TEST_DEPS,
        ],
        check=True,
    )
    print(f"ready: {DEV}")


def env() -> dict[str, str]:
    e = dict(os.environ)
    e["BLENDER_USER_RESOURCES"] = str(USER)
    e["BLENDER_SYSTEM_EXTENSIONS"] = str(SYSTEM_EXTENSIONS)
    e["BLENDER_SYSTEM_SCRIPTS"] = str(SYSTEM_SCRIPTS)
    e["JUSTSTAGE_ROOT"] = str(ROOT)
    e["JUSTSTAGE_PYDEPS"] = str(PYDEPS)
    return e


def run_blender(args: list[str]) -> int:
    if not all(link.exists() for link in LINKS):
        setup()
    return subprocess.run([str(blender_path()), *args], env=env()).returncode


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    verb, rest = argv[0], argv[1:]
    if verb == "setup":
        setup()
        return 0
    if verb == "blender":
        return run_blender(["--app-template", "juststage", *rest])
    if verb == "test":
        return run_blender(
            [
                "-b",
                "--factory-startup",
                "--python-exit-code",
                "1",
                "--python",
                str(ROOT / "tests" / "run.py"),
                "--",
                *rest,
            ]
        )
    sys.exit(f"unknown verb {verb!r}; see --help")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
