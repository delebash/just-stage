# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.body.create` — a new human on MakeHuman's hm08, shaped by MakeHuman's macro values; `dressed`, as CC5's
New gives one (the realism working doc, `docs/plans/2026-11-04-realism.md`): its eyes and teeth with their occlusion
and tearline, JustStage's lashes, and a mapped skin from the library (DEFAULT_SKIN, by sex) in its own tone."""

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
    dressed: bool = False  # the panel's New human: eyes, teeth, lashes and a skin too


class Result(NamedTuple):
    character: str  # the assetInfo identifier
    object: str
    vertices: int
    visible_vertices: int
    macro_targets: int
    skin: str  # the mapped skin it wears ("" when bare, or when the library has none)


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
    dressed = values.pop("dressed")
    for key, value in values.items():
        if not 0.0 <= value <= 1.0:
            raise CommandError(f"{key}: expected 0.0–1.0, got {value}")
    obj = build.create_human(name, values)
    skin = _dress(obj) if dressed else ""
    return Result(
        character=obj.juststage.character_id,
        object=obj.name,
        vertices=len(obj.data.vertices),
        visible_vertices=build.visible_vertex_count(obj),
        macro_targets=sum(1 for k in obj.data.shape_keys.key_blocks if build.is_macro_key(k.name)),
        skin=skin,
    )


#: a new human's skin by sex (tools/build_skins.py's people): the women Mei's, the men Daniel's
DEFAULT_SKIN = {"female": "Mei skin", "male": "Daniel skin"}


def _dress(obj) -> str:
    from ... import api
    from ...core import library
    from ..hair import lashes

    cid = obj.juststage.character_id
    api.run("juststage.head.add_parts", character=cid)
    lashes.make(obj)
    name = DEFAULT_SKIN["female" if obj.juststage.gender < 0.5 else "male"]
    path = library.root() / "Skins" / f"{name}.blend"
    if not path.is_file():
        print(f"JustStage: {name} is not in the library - the skin stays the tone alone (tools/build_skins.py)")
        return ""
    tone = {k: getattr(obj.juststage, k) for k in ("melanin", "eumelanin", "blood", "oiliness")}
    api.run("juststage.library.add", path=str(path), character=cid)
    api.run("juststage.skin.set_tone", character=cid, **tone)  # its own tone, the skin's detail
    return name
