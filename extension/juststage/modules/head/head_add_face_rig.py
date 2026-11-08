# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.head.add_face_rig` — the face rig on: MetaHuman's GUI controls as the character's animatable properties,
RigLogic driving the face's shape keys from them (needs the face units)."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str


class Result(NamedTuple):
    controls: int
    channels: int


COMMAND = dict(
    id="juststage.head.add_face_rig",
    label="Face rig (MetaHuman controls)",
    menu="Character > Head",
    permission="head",
    undo=True,
    headless=True,
    since="2026-11-08",
)


def main(params: Params) -> Result:
    from ... import character
    from ...core.commands import CommandError
    from . import face_rig, face_units

    obj = character.find(params.character)
    keys = obj.data.shape_keys.key_blocks if obj.data.shape_keys else {}
    if not any(name in keys for name in face_units.ARKIT):
        raise CommandError(f"{obj.name} has no face units; run juststage.head.add_face_units first")
    count = face_rig.attach(obj)
    return Result(controls=count, channels=sum(1 for name in face_rig._dna()["channels"] if name in keys))
