# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.body.set_slider` — one body slider (commands-and-api.md §2's own declaration). The sliders so far are
MakeHuman's macros (`macro.json`: gender, age, muscle, weight, proportions, height, cupsize, firmness) and the three
race mixes, kept summing to 1 the way MakeHuman's EthnicModifier does; target.json's sliders join later."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str  # the character's assetInfo identifier
    slider: str  # a slider id from macro.json (or a race: asian, caucasian, african)
    value: float


class Result(NamedTuple):
    status: str
    value: float


COMMAND = dict(
    id="juststage.body.set_slider",
    label="Set body slider",
    menu="Character > Body",
    permission="body",
    undo=True,
    headless=True,
    since="2026-11-03",
)


def main(params: Params) -> Result:
    from ... import character
    from ...core import makehuman
    from ...core.commands import CommandError
    from . import build

    sliders = (*makehuman.MACROS, *makehuman.RACES)
    if params.slider not in sliders:
        raise CommandError(f"slider: {params.slider!r} is not one of {', '.join(sliders)}")
    if not 0.0 <= params.value <= 1.0:
        raise CommandError(f"value: expected 0.0–1.0, got {params.value}")
    obj = character.find(params.character)
    props = obj.juststage
    values = {k: float(getattr(props, k)) for k in sliders}
    values[params.slider] = float(params.value)
    if params.slider in makehuman.RACES:  # the other two share what is left, in their old proportion
        others = [r for r in makehuman.RACES if r != params.slider]
        rest, total = 1.0 - params.value, sum(values[r] for r in others)
        for r in others:
            values[r] = rest * (values[r] / total if total > 1e-9 else 1.0 / len(others))
    build.apply_macros(obj, values)
    try:  # the head's eyes and teeth ride the body's helpers (head module; absent when it is switched off)
        from ..head import parts
    except ImportError:
        parts = None
    if parts is not None and parts.parts_of(obj):
        parts.refit(obj)
    return Result(status="ok", value=float(params.value))
