# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.body.set_mix` — one region of the mixer (CC5's part list: head shape, forehead, eyes, nose, mouth, chin,
ears, torso, arms, legs): a weighted blend of identities in that region at a strength; ordinary sliders untouched."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str
    region: str
    identities: str = ""  # comma-separated names (the command API's lists hold numbers - core/commands.py)
    weights: list[float] = []
    strength: float = 1.0


class Result(NamedTuple):
    key: str
    region: str
    identities: list[str]


COMMAND = dict(
    id="juststage.body.set_mix",
    label="Mix identities (a region)",
    menu="Character > Body",
    permission="body",
    undo=True,
    headless=True,
    since="2026-11-08",
)


def main(params: Params) -> Result:
    from ... import character
    from ...core.commands import CommandError
    from . import build, mixer

    obj = character.find(params.character)
    if not 0.0 <= params.strength <= 1.0:
        raise CommandError(f"strength: expected 0.0-1.0, got {params.strength}")
    names = [n.strip() for n in params.identities.split(",") if n.strip()]
    unknown = [n for n in names if n not in mixer.identities()]
    if unknown:
        raise CommandError(f"no identity {', '.join(unknown)}; the identities: {', '.join(mixer.identities())}")
    try:
        key = mixer.set_mix(obj, params.region, names, list(params.weights), params.strength)
    except ValueError as exc:
        raise CommandError(str(exc)) from exc
    build.keep_on_floor(obj)
    build.refit_riders(obj)  # the head's parts and the skeleton follow the new shape, as after a slider
    return Result(key=key.name, region=params.region, identities=names)
