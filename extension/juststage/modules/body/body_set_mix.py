# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.body.set_mix` — one region of the mixer (CC5's part list: head shape, forehead, eyes, nose, mouth, chin,
ears, torso, arms, legs): a weighted blend of identities in that region at a strength - CC5's wheel - in one of
MetaHuman's Blend Types: "both", "features" (the region's shape, its place, turn and size kept) or "proportions" (its
place, turn and size, its shape kept) - mixer.py. It sets the region's mixer sliders of the mode's parts
(`scans.<identity>.<region>.<part>` = weight / sum of weights x strength; the region's other identities in those parts
to 0, the other part untouched), the values `juststage.body.set_slider` takes one at a time; no identities clears
the mode's parts in the region (CC5's Reset: the character's own shape there); ordinary sliders untouched."""

from typing import Literal, NamedTuple

MODES = ("both", "features", "proportions")  # MetaHuman's Blend Type (EBlendOptions); mixer.PARTS the last two


class Params(NamedTuple):
    character: str
    region: str
    identities: str = ""  # comma-separated names (the command API's lists hold numbers - core/commands.py)
    weights: list[float] = []
    strength: float = 1.0
    mode: Literal[MODES] = "both"


class Result(NamedTuple):
    region: str
    sliders: list[str]  # the region's mixer sliders now above 0


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
    if params.region not in mixer.regions():
        raise CommandError(f"no region {params.region!r}; the regions: {', '.join(mixer.regions())}")
    names = [n.strip() for n in params.identities.split(",") if n.strip()]
    unknown = [n for n in names if n not in mixer.identities()]
    if unknown:
        raise CommandError(f"no identity {', '.join(unknown)}; the identities: {', '.join(mixer.identities())}")
    if len(names) != len(params.weights) or len(set(names)) != len(names):
        raise CommandError("weights: one a named identity, each identity once")
    if names and (any(w < 0.0 for w in params.weights) or sum(params.weights) <= 0.0):
        raise CommandError("weights: none below 0, their sum above 0")
    total = sum(params.weights) or 1.0  # no identities: the part cleared
    parts = mixer.PARTS if params.mode == "both" else (params.mode,)
    now = []
    for part in parts:
        values = dict.fromkeys(mixer.region_mix(obj, params.region, part), 0.0)  # the part's last mix out
        values.update({n: w / total * params.strength for n, w in zip(names, params.weights, strict=True)})
        for name, value in values.items():
            mixer.set_value(obj, name, params.region, part, value)
        now += [mixer.slider_id(n, params.region, part) for n, v in values.items() if v > 0.0]
    mixer.follow(obj)  # the helpers (the eyes', teeth's and skeleton's carriers) with the mixed skin
    build.keep_on_floor(obj)
    build.refit_riders(obj)  # the head's parts and the skeleton follow the new shape, as after a slider
    return Result(region=params.region, sliders=now)
