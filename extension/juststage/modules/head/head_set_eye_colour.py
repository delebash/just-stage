# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.head.set_eye_colour` — both eyes' colour (CC5's eye colour, MetaHuman's iris presets): a preset
(eyes.PRESETS), or `custom` with the iris, its darker accent and the white given; on MPFB2's procedural eye
(modules/head/eyes.py). The character keeps the colours (its Skin tab shows them), and eyes added again get them."""

from typing import Literal, NamedTuple

from .eyes import IRIS_MAJOR, IRIS_MINOR, PRESETS, WHITE

PRESET_NAMES = ("custom", *PRESETS)


class Params(NamedTuple):
    character: str
    preset: Literal[PRESET_NAMES] = "custom"
    iris: list[float] = list(IRIS_MAJOR)  # linear RGB, used when preset is "custom"
    accent: list[float] = list(IRIS_MINOR)
    white: list[float] = list(WHITE)


class Result(NamedTuple):
    eyes: int
    iris: list[float]
    accent: list[float]


COMMAND = dict(
    id="juststage.head.set_eye_colour",
    label="Eye colour",
    menu="Character > Head",
    permission="head",
    undo=True,
    headless=True,
    since="2026-11-04",
)


def main(params: Params) -> Result:
    from ... import character
    from ...core.commands import CommandError
    from . import eyes, parts

    for name in ("iris", "accent", "white"):
        value = getattr(params, name)
        if len(value) != 3 or not all(0.0 <= c <= 1.0 for c in value):
            raise CommandError(f"{name}: expected three linear values 0-1, got {list(value)}")
    obj = character.find(params.character)
    iris, accent = (params.iris, params.accent) if params.preset == "custom" else PRESETS[params.preset]
    found = [e for p, e in parts.parts_of(obj).items() if p in ("eyeLeft", "eyeRight")]
    if not found:
        raise CommandError(f"{obj.name} has no eyes; run juststage.head.add_parts first")
    done = sum(eyes.set_colour(eye, iris, accent, params.white) for eye in found)
    props = obj.juststage
    character.APPLYING["macros"] = True  # the Skin tab's eye fields stay quiet while their values are written
    try:
        props.eye_preset = params.preset
        props.iris_colour, props.iris_accent, props.eye_white = tuple(iris), tuple(accent), tuple(params.white)
    finally:
        character.APPLYING["macros"] = False
    return Result(eyes=len(found) if done else 0, iris=list(iris), accent=list(accent))
