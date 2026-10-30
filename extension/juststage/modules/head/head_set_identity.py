# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.head.set_identity` — a scan-based head shape from GNM's space: given coefficients, or a random
person drawn from it (GNM's identity directions are standard deviations, so a draw is a normal sample)."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str
    seed: int = 0
    strength: float = 1.0
    coefficients: list[float] = []


class Result(NamedTuple):
    components: int
    max_offset_mm: float


COMMAND = dict(
    id="juststage.head.set_identity",
    label="Head shape (scan-based)",
    menu="Character > Head",
    permission="head",
    undo=True,
    headless=True,
    since="2026-10-29",
)


def main(params: Params) -> Result:
    import numpy as np

    from ... import character
    from ...core.commands import CommandError
    from . import gnm_space

    obj = character.find(params.character)
    n = gnm_space.components()
    if params.coefficients:
        if len(params.coefficients) > n:
            raise CommandError(f"coefficients: at most {n}, got {len(params.coefficients)}")
        values = np.zeros(n, dtype=np.float32)
        values[: len(params.coefficients)] = params.coefficients
    else:
        values = np.random.default_rng(params.seed).standard_normal(n).astype(np.float32)
    values *= params.strength
    largest = gnm_space.set_identity(obj, values)
    from . import parts

    if parts.parts_of(obj):
        parts.refit(obj)
    return Result(components=n, max_offset_mm=largest)
