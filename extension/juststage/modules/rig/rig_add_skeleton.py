# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.rig.add_skeleton` — the body skeleton (UE5's 80 deform bones by Epic's names, plus the breasts) placed
on the character's shape, its weights bound, the head's parts riding the head bone."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str


class Result(NamedTuple):
    object: str
    bones: int
    weighted_vertices: int
    riders: list[str]


COMMAND = dict(
    id="juststage.rig.add_skeleton",
    label="Skeleton (UE5)",
    menu="Character > Rig",
    permission="rig",
    undo=True,
    headless=True,
    since="2026-11-08",
)


def main(params: Params) -> Result:
    from ... import character
    from . import skeleton

    obj = character.find(params.character)
    arm = skeleton.add(obj)
    bones = {vg.index for vg in obj.vertex_groups if vg.name in skeleton.definition()}
    weighted = sum(1 for v in obj.data.vertices if any(g.group in bones and g.weight > 0 for g in v.groups))
    return Result(object=arm.name, bones=len(arm.data.bones), weighted_vertices=weighted,
                  riders=[o.name for o in skeleton.riders(obj)])  # fmt: skip
