# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.body.create` — a new human on MakeHuman's hm08, shaped by MakeHuman's macro values."""

from typing import NamedTuple


class Params(NamedTuple):
    name: str = "Character"
    gender: float = 0.5
    age: float = 0.5
    muscle: float = 0.5
    weight: float = 0.5
    proportions: float = 0.5
    height: float = 0.5
    cupsize: float = 0.5
    firmness: float = 0.5
    asian: float = 0.33
    caucasian: float = 0.33
    african: float = 0.33


class Result(NamedTuple):
    character: str  # the assetInfo identifier
    object: str
    vertices: int
    visible_vertices: int
    macro_targets: int


COMMAND = dict(
    id="juststage.body.create",
    label="New human",
    menu="Character > New human",
    permission="body",
    undo=True,
    headless=True,
    since="2026-10-29",
)


def main(params: Params) -> Result:
    from ...core.commands import CommandError
    from . import build

    values = params._asdict()
    name = values.pop("name")
    for key, value in values.items():
        if not 0.0 <= value <= 1.0:
            raise CommandError(f"{key}: expected 0.0–1.0, got {value}")
    obj = build.create_human(name, values)
    return Result(
        character=obj.juststage.character_id,
        object=obj.name,
        vertices=len(obj.data.vertices),
        visible_vertices=build.visible_vertex_count(obj),
        macro_targets=sum(1 for k in obj.data.shape_keys.key_blocks if build.is_macro_key(k.name)),
    )
