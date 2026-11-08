# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.body.set_slider` — one body slider (commands-and-api.md §2's own declaration): MakeHuman's macros
(`macro.json`: gender, age, muscle, weight, proportions, height, cupsize, firmness), the three race mixes (kept summing
to 1 the way MakeHuman's EthnicModifier does) and target.json's detail sliders (`<group>/<category>`, sliders.py)."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str  # the character's assetInfo identifier
    slider: str  # a slider id from macro.json (or a race: asian, caucasian, african) or target.json (`nose/...`)
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
    from . import sliders as detail

    sliders = (*makehuman.MACROS, *makehuman.RACES)
    found = detail.catalog().get(params.slider)
    if params.slider not in sliders and found is None:
        raise CommandError(f"slider: {params.slider!r} is not a macro ({', '.join(sliders)}) nor a target.json slider")
    low = found.low if found else 0.0
    if not low <= params.value <= 1.0:
        raise CommandError(f"value: expected {low:.1f}–1.0, got {params.value}")
    obj = character.find(params.character)
    if found is not None:
        detail.apply(obj, found, float(params.value))
        item = next((s for s in obj.juststage.sliders if s.id == found.id), None)
        if item is None:
            item = obj.juststage.sliders.add()
            item.id, item.label, item.group = found.id, found.label, found.group
        if abs(item.value - params.value) > 1e-9:
            character.APPLYING["macros"] = True  # its update callback stays quiet
            try:
                item.value = float(params.value)
            finally:
                character.APPLYING["macros"] = False
        build.keep_on_floor(obj)
        _refit(obj)
        return Result(status="ok", value=float(params.value))
    props = obj.juststage
    values = {k: float(getattr(props, k)) for k in sliders}
    values[params.slider] = float(params.value)
    if params.slider in makehuman.RACES:  # the other two share what is left, in their old proportion
        others = [r for r in makehuman.RACES if r != params.slider]
        rest, total = 1.0 - params.value, sum(values[r] for r in others)
        for r in others:
            values[r] = rest * (values[r] / total if total > 1e-9 else 1.0 / len(others))
    build.apply_macros(obj, values)
    build.keep_on_floor(obj)
    _refit(obj)
    return Result(status="ok", value=float(params.value))


def _refit(obj) -> None:
    from . import build

    build.refit_riders(obj)  # the head's eyes and teeth ride the body's helpers, the skeleton its joint cubes
