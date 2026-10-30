# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.skin.set_tone` — the skin's colour from its chromophores: melanin (and how much of it is
eumelanin), blood, and oiliness. The defaults are about the median of NIST's 100 measured people."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str
    melanin: float = 0.0104
    eumelanin: float = 0.6
    blood: float = 0.016
    oiliness: float = 0.5


class Result(NamedTuple):
    material: str
    linear_rgb: list[float]
    subsurface_radius_mm: list[float]


COMMAND = dict(
    id="juststage.skin.set_tone",
    label="Skin tone",
    menu="Character > Skin",
    permission="skin",
    undo=True,
    headless=True,
    since="2026-10-29",
)

RANGES = {"melanin": (0.0, 0.5), "eumelanin": (0.0, 1.0), "blood": (0.001, 0.2), "oiliness": (0.0, 1.0)}


def main(params: Params) -> Result:
    from ... import character, paths
    from ...core import skin_optics
    from ...core.commands import CommandError
    from . import material

    for name, (low, high) in RANGES.items():
        value = getattr(params, name)
        if not low <= value <= high:
            raise CommandError(f"{name}: expected {low}–{high}, got {value}")
    obj = character.find(params.character)
    skin = skin_optics.Skin(params.melanin, params.eumelanin, params.blood)
    mat = material.apply(obj, skin, params.oiliness)
    props = obj.juststage
    props.melanin = params.melanin
    props.eumelanin = params.eumelanin
    props.blood = params.blood
    props.oiliness = params.oiliness
    tables = skin_optics.load_tables(paths.FETCHED / "optics")
    return Result(
        material=mat.name,
        linear_rgb=list(skin.linear_rgb(tables)),
        subsurface_radius_mm=list(skin.subsurface_radius_mm(tables)),
    )
