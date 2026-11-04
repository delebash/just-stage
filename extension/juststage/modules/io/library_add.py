# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.library.add` — a character from the asset library into the scene, as a character of its own
(docs/standards/project-files.md §2) - the Modify panel's "Start from" buttons."""

from typing import NamedTuple


class Params(NamedTuple):
    path: str  # the asset's .blend (core/library.py `characters()`)


class Result(NamedTuple):
    character: str
    object: str


COMMAND = dict(
    id="juststage.library.add",
    label="Add from library",
    menu="Character > New human",
    permission="files",
    undo=True,
    headless=True,
    since="2026-11-04",
)


def main(params: Params) -> Result:
    from pathlib import Path

    import bpy

    from ...core import library
    from ...core.commands import CommandError

    if not Path(params.path).is_file():
        raise CommandError(f"path: no asset file at {params.path!r}")
    body = library.add(params.path, bpy.context.scene)
    return Result(character=body.juststage.character_id, object=body.name)
