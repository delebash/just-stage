# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.library.save` — saved to the asset library as one asset in a catalogue (docs/standards/project-files.md
§2), what is saved picked by the catalogue: Characters the whole character (its parts with it), `Hair/<type>` its groom
of that type (the hair alone, without the body), Skins its skin material (its tone with it). Its rule: no asset
without its provenance and a licence label."""

from typing import NamedTuple


class Params(NamedTuple):
    character: str
    catalog: str = "Characters"
    name: str = ""
    description: str = ""
    licence: str = ""  # e.g. "CC0-1.0" - shown in the Content panel, never filtered (README §4)
    provenance: str = ""  # where it came from: "JustStage body.create", an import's source and its terms
    library: str = ""  # a library folder; "" is the user's JustStage library
    part: str = ""  # Hair/Beards: "beard" or "mustache" when the character has both


#: a hair catalogue → the groom types it holds (character-data-model.md §4)
HAIR = {
    "Hair/Scalp": ("scalp",),
    "Hair/Brows": ("eyebrows",),
    "Hair/Lashes": ("eyelashes",),
    "Hair/Beards": ("beard", "mustache"),
}


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
    folder = Path(params.library) if params.library else library.root()
    meta = {"description": params.description, "licence": params.licence, "tags": ("JustStage",)}
    name = params.name or obj.name
    if params.catalog in HAIR:
        from ..hair import groom

        have = [t for t in HAIR[params.catalog] if groom.of_part(obj, t)]
        if params.part:
            have = [t for t in have if t == params.part]
        if len(have) != 1:
            wanted = " or ".join(HAIR[params.catalog])
            raise CommandError(f"part: {obj.name} has {len(have) or 'no'} {wanted} groom(s); name the one to save")
        copies = groom.portable(obj, have[0], name)
        copies[0].juststage.provenance, copies[0].juststage.licence_label = params.provenance, params.licence
        try:
            target = library.save(copies, params.catalog, name, folder, meta)
        finally:
            groom.remove_copies(copies)
        return Result(path=str(target))
    if params.catalog == "Skins":
        mat = obj.juststage.skin_material
        if mat is None:
            raise CommandError(f"{obj.name} has no skin yet; run juststage.skin.set_tone first")
        mat.juststage.provenance, mat.juststage.licence_label = params.provenance, params.licence
        return Result(path=str(library.save([mat], params.catalog, name, folder, meta)))
    parts = [o for o in bpy.data.objects if o.juststage.part_of == obj.juststage.character_id]
    obj.juststage.provenance = params.provenance
    obj.juststage.licence_label = params.licence
    target = library.save([obj, *parts], params.catalog, name, folder, meta)
    return Result(path=str(target))
