# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.hair.set_colour` — a groom's colour by melanin and its redness (Blender's melanin parametrisation,
character-data-model.md §4): every strand's `melanin` and `redness` attributes, which its material reads in Cycles
and in its EEVEE stand-in alike (groom.py)."""

from typing import NamedTuple


class Params(NamedTuple):
    groom: str  # the groom object's name (juststage.hair.add's `groom`)
    melanin: float = 0.8
    redness: float = 1.0


class Result(NamedTuple):
    strands: int


COMMAND = dict(
    id="juststage.hair.set_colour",
    label="Hair colour",
    menu="Character > Hair",
    permission="hair",
    undo=True,
    headless=True,
    since="2026-11-03",
)


def main(params: Params) -> Result:
    import bpy

    from ...core.commands import CommandError
    from . import groom

    for name in ("melanin", "redness"):
        if not 0.0 <= getattr(params, name) <= 1.0:
            raise CommandError(f"{name}: expected 0–1, got {getattr(params, name)}")
    from . import cards

    obj = bpy.data.objects.get(params.groom)
    if obj is not None and cards.is_cards(obj) and obj.juststage.part_of:  # card hair: its whole set's colour
        pieces = [o for o in bpy.data.objects
                  if o.juststage.part_of == obj.juststage.part_of and o.juststage.part == obj.juststage.part]
        cards.set_colour(pieces, params.melanin, params.redness)
        return Result(strands=sum(len(o.data.polygons) for o in pieces))
    if obj is None or obj.type != "CURVES" or not obj.juststage.part_of:
        raise CommandError(f"groom: no JustStage groom named {params.groom!r}")
    groom._set_colour(obj.data, params.melanin, params.redness)
    obj.data.update_tag()
    return Result(strands=len(obj.data.curves))
