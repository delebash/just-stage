# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.library.add` — an asset from the library (docs/standards/project-files.md §2), by what its file holds:
a character comes into the scene as a character of its own (the Modify panel's "Start from" buttons); a groom goes onto
`character`, replacing its groom of the same type (CC5's way: applied hair replaces the hair); a skin preset sets
`character`'s tone, and a mapped skin (modules/skin/maps.py) puts its maps on it too. The Content panel's double-click
and its Apply entry run it (ui/content.py)."""

from typing import NamedTuple


class Params(NamedTuple):
    path: str  # the asset's .blend (core/library.py `characters()`, or the Content panel's asset)
    character: str = ""  # who a groom or a skin preset is applied to


class Result(NamedTuple):
    character: str
    object: str


COMMAND = dict(
    id="juststage.library.add",
    label="Add from library",
    menu="Character > New human",
    permission="files",
    undo=True,
    headless=True,
    since="2026-11-04",
)


def main(params: Params) -> Result:
    from pathlib import Path

    import bpy

    from ... import character
    from ...core import library
    from ...core.commands import CommandError

    if not Path(params.path).is_file():
        raise CommandError(f"path: no asset file at {params.path!r}")
    held = library.kind(params.path)
    if held == "character":
        body = library.add(params.path, bpy.context.scene)
        return Result(character=body.juststage.character_id, object=body.name)
    if not held:
        raise CommandError(f"path: {params.path!r} holds no JustStage character, groom or skin")
    if not params.character:
        raise CommandError(f"character: a {held} is applied to a character - select one first")
    obj = character.find(params.character)
    if held == "groom":
        from ..hair import groom

        return Result(character=params.character, object=groom.add_from_file(obj, params.path).name)
    from ..skin import maps, skin_set_tone

    mapped = library.skin_material(params.path)
    if mapped is not None:  # a mapped skin: its maps on the character (a copy of its own), then its tone
        maps.apply(obj, mapped)
        bpy.data.materials.remove(mapped)
    skin_set_tone.main(skin_set_tone.Params(character=params.character, **library.skin_tone(params.path)))
    return Result(character=params.character, object=obj.name)
