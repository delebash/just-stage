# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.head.add_face_units` — the face's 52 ARKit shape keys (MakeHuman's CC0 Faceunits 01), at 0."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str


class Result(NamedTuple):
    units: int
    missing: list[str]


COMMAND = dict(
    id="juststage.head.add_face_units",
    label="Face units (ARKit 52)",
    menu="Character > Head",
    permission="head",
    undo=True,
    headless=True,
    since="2026-11-03",
)


def main(params: Params) -> Result:
    from ... import character
    from . import face_units

    obj = character.find(params.character)
    added = face_units.add(obj)
    return Result(units=len(added), missing=[n for n in face_units.ARKIT if n not in added])
