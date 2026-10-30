# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.head.add_parts` — the head's eyes and teeth (with gums and tongue), fitted to the character; running it
again refits them to the character's current shape."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str


class Result(NamedTuple):
    added: list[str]
    parts: list[str]


COMMAND = dict(
    id="juststage.head.add_parts",
    label="Eyes and teeth",
    menu="Character > Head",
    permission="head",
    undo=True,
    headless=True,
    since="2026-10-29",
)


def main(params: Params) -> Result:
    from ... import character
    from . import parts

    obj = character.find(params.character)
    added = parts.add(obj)
    return Result(added=added, parts=sorted(parts.parts_of(obj)))
