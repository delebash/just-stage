# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.head.add_face_units` — the face's 52 ARKit shape keys (MakeHuman's CC0 Faceunits 01), at 0."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str


class Result(NamedTuple):
    units: int
    missing: list[str]


COMMAND = dict(
    id="juststage.head.add_face_units",
    label="Face units (ARKit 52)",
    menu="Character > Head",
    permission="head",
    undo=True,
    headless=True,
    since="2026-11-03",
)


def main(params: Params) -> Result:
    from ... import character
    from . import face_units

    obj = character.find(params.character)
    added = face_units.add(obj)
    _jaw(obj)  # the lower teeth and tongue ride the jaw joint, which the face rig moves after the jaw units
    from . import blink_contact, lip_seal

    blink_contact.make(obj)  # the blink's closing step (the lids snapped and relaxed onto each other)
    lip_seal.drive(obj)  # the neutral's seal fades as the jaw opens
    return Result(units=len(added), missing=[n for n in face_units.ARKIT if n not in added])


def _jaw(obj) -> None:
    """The face rig on the character with its ARKit keys driving (the spec §2.1: live sources write the keys), so the
    jaw joint - and the teeth on it - follows jawOpen and the other jaw units; the skeleton added first when the
    character has none (the rig module's command)."""
    from ... import api
    from . import face_rig

    try:
        from ..rig import skeleton
    except ImportError:
        skeleton = None
    if skeleton is not None and skeleton.skeleton_of(obj) is None and "juststage.rig.add_skeleton" in {
            c.record["id"] for c in api.commands()}:  # fmt: skip
        api.run("juststage.rig.add_skeleton", character=obj.juststage.character_id)
    face_rig.attach(obj, drive=bool(obj.get(face_rig.MARK, 0)))
