# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.library.save` — a character (and its parts) saved to the asset library as one asset in a catalogue
(docs/standards/project-files.md §2). Its rule: no asset without its provenance and a licence label."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str
    catalog: str = "Characters"
    name: str = ""
    description: str = ""
    licence: str = ""  # e.g. "CC0-1.0" - shown in the Content panel, never filtered (README §4)
    provenance: str = ""  # where it came from: "JustStage body.create", an import's source and its terms
    library: str = ""  # a library folder; "" is the user's JustStage library


class Result(NamedTuple):
    path: str


COMMAND = dict(
    id="juststage.library.save",
    label="Save to library",
    menu="Character > Export",
    permission="files",
    undo=False,
    headless=True,
    since="2026-11-04",
)


def main(params: Params) -> Result:
    from pathlib import Path

    import bpy

    from ... import character
    from ...core import library
    from ...core.commands import CommandError

    for field in ("licence", "provenance"):
        if not getattr(params, field).strip():
            raise CommandError(f"{field}: an asset needs its {field} (project-files.md §2)")
    if params.catalog not in library.catalog_ids():
        raise CommandError(f"catalog: {params.catalog!r} is not one of JustStage's catalogues")
    obj = character.find(params.character)
    parts = [o for o in bpy.data.objects if o.juststage.part_of == obj.juststage.character_id]
    folder = Path(params.library) if params.library else library.root()
    meta = {"description": params.description, "licence": params.licence, "tags": ("JustStage",)}
    obj.juststage.provenance = params.provenance
    obj.juststage.licence_label = params.licence
    target = library.save([obj, *parts], params.catalog, params.name or obj.name, folder, meta)
    return Result(path=str(target))
