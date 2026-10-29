# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.body.subdivide` — levels 1 and 2 on the base (CC5 HD's method; character-data-model.md §1.1).

Blender's Multires modifier holds the levels and their sculpted displacement. It goes first in the stack, before the
helper mask, so its levels sit on the unchanged base topology.
"""

from typing import NamedTuple


class Params(NamedTuple):
    character: str
    levels: int = 2
    viewport_level: int = 2


class Result(NamedTuple):
    levels: int
    viewport_level: int
    visible_faces: int


COMMAND = dict(
    id="juststage.body.subdivide",
    label="Subdivide (HD levels)",
    menu="Character > Body",
    permission="body",
    undo=True,
    headless=True,
    since="2026-10-29",
)

MAX_LEVELS = 2


def main(params: Params) -> Result:
    from ... import character
    from ...core.commands import CommandError
    from . import build

    if not 0 <= params.levels <= MAX_LEVELS:
        raise CommandError(f"levels: expected 0–{MAX_LEVELS}, got {params.levels}")
    if not 0 <= params.viewport_level <= params.levels:
        raise CommandError(f"viewport_level: expected 0–{params.levels}, got {params.viewport_level}")
    obj = character.find(params.character)
    build.set_levels(obj, params.levels, params.viewport_level)
    return Result(
        levels=params.levels, viewport_level=params.viewport_level, visible_faces=build.visible_face_count(obj)
    )
