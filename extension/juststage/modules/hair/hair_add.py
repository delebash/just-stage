# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.hair.add` — a groom from MakeHuman's CC0 hair-editor pack (scalp hair, eyebrows, eyelashes, beards,
moustaches) attached to the character the way MPFB2's hair editor attaches it. The colour defaults are Blender's own
Principled Hair BSDF defaults."""

from typing import Literal, NamedTuple

from .styles import DEFAULT, STYLES


class Params(NamedTuple):
    character: str
    style: Literal[tuple(STYLES)] = DEFAULT
    melanin: float = 0.8
    redness: float = 1.0


class Result(NamedTuple):
    groom: str
    groom_type: str
    strands: int


COMMAND = dict(
    id="juststage.hair.add",
    label="Add hair",
    menu="Character > Hair",
    permission="hair",
    undo=True,
    headless=True,
    since="2026-10-29",
)


def main(params: Params) -> Result:
    from ... import character
    from ...core.commands import CommandError
    from . import groom

    for name in ("melanin", "redness"):
        if not 0.0 <= getattr(params, name) <= 1.0:
            raise CommandError(f"{name}: expected 0–1, got {getattr(params, name)}")
    obj = groom.add_style(character.find(params.character), params.style, params.melanin, params.redness)
    return Result(groom=obj.name, groom_type=obj.juststage.part, strands=groom.evaluated_curve_count(obj))
