# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Where the add-on's data lives."""

from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
FETCHED = DATA / "fetched"
MAKEHUMAN = FETCHED / "makehuman"


def makehuman(*parts: str) -> Path:
    """A path under MakeHuman's fetched CC0 data; refuses with the fix named when the data isn't there."""
    path = MAKEHUMAN.joinpath(*parts)
    if not path.exists():
        from .core.commands import CommandError

        raise CommandError(f"MakeHuman's data is missing ({path.name}); run: python tools/fetch_data.py")
    return path
