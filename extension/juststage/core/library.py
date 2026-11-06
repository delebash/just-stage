# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's asset library (docs/standards/project-files.md §2): Blender 5.3's asset libraries
(https://docs.blender.org/manual/en/5.3/files/asset_libraries/index.html) - `<library>/blender_assets.cats.txt`,
`<library>/<catalogue path>/<asset>.blend`, one self-contained file per asset written with
`bpy.data.libraries.write`; the catalogue UUIDs fixed in data/library/catalogs.txt so every install shares them."""

from __future__ import annotations

import shutil
from pathlib import Path

import bpy

from .. import paths

CATALOGS = paths.DATA / "library" / "catalogs.txt"
NAME = "JustStage"


def catalog_ids() -> dict[str, str]:
    """Catalogue path → UUID."""
    found = {}
    for line in CATALOGS.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or line.startswith("VERSION"):
            continue
        uid, path, _simple = line.split(":", 2)
        found[path] = uid
    return found


def root() -> Path:
    """The user's JustStage library folder."""
    return paths.user_dir("library")


def prepare(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CATALOGS, folder / "blender_assets.cats.txt")


def register_library(preferences, folder: Path | None = None) -> None:
    """The JustStage library in Blender's preferences (once), so the Content panel lists it."""
    folder = folder or root()
    prepare(folder)
    libraries = preferences.filepaths.asset_libraries
    if not any(lib.name == NAME for lib in libraries):
        lib = libraries.new(name=NAME, directory=str(folder))
        lib.import_method = "APPEND"
    preferences.is_dirty = True


def save(ids: list, catalog: str, name: str, folder: Path, meta: dict) -> Path:
    """`ids` (the asset first: a character's body, a groom, a skin material) written as one `.blend` in
    `<folder>/<catalog>/<name>.blend`, the first marked as an asset in that catalogue with Blender's metadata fields and
    shown in the Content panel as `name` (Blender lists an asset by its data-block's name)."""
    uid = catalog_ids()[catalog]
    prepare(folder)
    asset = ids[0]
    own_name = asset.name
    asset.name = name
    try:
        asset.asset_mark()
        data = asset.asset_data
        data.catalog_id = uid
        data.description = meta.get("description", "")
        data.author = meta.get("author", "JustStage")
        data.license = meta["licence"]
        for tag in meta.get("tags", ()):
            data.tags.new(tag, skip_if_exists=True)
        target = folder / catalog / f"{name}.blend"
        target.parent.mkdir(parents=True, exist_ok=True)
        # fake users: the written data-blocks are in no scene there, and Blender drops user-less data-blocks when that
        # file is saved again (a thumbnail set) - `add` clears them in the scene
        bpy.data.libraries.write(str(target), set(ids), path_remap="RELATIVE_ALL", fake_user=True, compress=True)
    finally:
        asset.asset_clear()  # the scene's own copy stays a plain data-block, under its own name
        asset.name = own_name
    return target


def kind(path: str) -> str:
    """What a library file holds - "character", "groom" or "skin" - read in Blender's temporary data, so nothing
    comes into the scene; "" when it is none of JustStage's."""
    with bpy.types.BlendData.temp_data() as temp:
        with temp.libraries.load(path, assets_only=True) as (src, dst):
            dst.objects = list(src.objects)
            dst.materials = list(src.materials)
        for obj in dst.objects:
            if obj is None:
                continue
            if obj.juststage.character_id and not obj.juststage.part_of:
                return "character"
            if obj.type == "CURVES" and obj.juststage.part:
                return "groom"
        if any(mat is not None and mat.juststage.is_skin for mat in dst.materials):
            return "skin"
    return ""


def skin_tone(path: str) -> dict:
    """A skin preset's tone values, read without keeping its material."""
    with bpy.types.BlendData.temp_data() as temp:
        with temp.libraries.load(path, assets_only=True) as (src, dst):
            dst.materials = list(src.materials)
        mat = next(m for m in dst.materials if m is not None and m.juststage.is_skin)
        record = mat.juststage
        return {name: getattr(record, name) for name in ("melanin", "eumelanin", "blood", "oiliness")}


def skin_material(path: str) -> bpy.types.Material | None:
    """A skin preset's material appended, when it carries maps (modules/skin/maps.py); None for a tone-only preset."""
    with bpy.types.BlendData.temp_data() as temp:
        with temp.libraries.load(path, assets_only=True) as (src, dst):
            dst.materials = list(src.materials)
        if not any(m is not None and m.juststage.is_skin and m.juststage.has_maps for m in dst.materials):
            return None
    with bpy.data.libraries.load(path, link=False, assets_only=True) as (src, dst):
        dst.materials = list(src.materials)
    mat = next(m for m in dst.materials if m is not None and m.juststage.has_maps)
    for node in mat.node_tree.nodes:
        image = getattr(node, "image", None)
        if image is not None:
            image.use_fake_user = False  # in use now (save wrote them with one)
    mat.use_fake_user = False
    if mat.asset_data is not None:
        mat.asset_clear()
    return mat


def characters(folder: Path | None = None) -> list[dict]:
    """The library's characters: their names and files, by name."""
    base = (folder or root()) / "Characters"
    return [{"name": p.stem, "path": str(p)} for p in sorted(base.glob("*.blend"))]


def add(path: str, scene) -> bpy.types.Object:
    """An asset file's objects appended into `scene`; the character gets an identifier of its own (its parts point to
    it), so two characters from one preset are two characters."""
    import uuid

    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = list(src.objects)
    objects = [o for o in dst.objects if o is not None]
    body = next(o for o in objects if o.juststage.character_id and not o.juststage.part_of)
    old, new = body.juststage.character_id, str(uuid.uuid4())
    for obj in objects:
        scene.collection.objects.link(obj)
        obj.use_fake_user = False  # in the scene now (save wrote it with one)
        if obj.asset_data is not None:
            obj.asset_clear()
        if obj.juststage.part_of == old:
            obj.juststage.part_of = new
    body.juststage.character_id = new
    from .. import migrations

    bpy.context.view_layer.update()
    if migrations.run([body]):  # a character saved by an older JustStage (base v1: hm08 without the lid anatomy)
        objects = [body, *(o for o in bpy.data.objects if o.juststage.part_of == new)]  # its grooms may be new ones
    if any(o.juststage.part in ("eyeLeft", "eyeRight") for o in objects):  # today's fit: the eyes' lid clearance
        from ..modules.head import parts

        bpy.context.view_layer.update()
        parts.refit(body)
    skin = body.juststage.skin_material
    if skin is not None and skin.juststage.has_maps:  # today's shading on its maps (modules/skin/maps.py)
        from ..modules.skin import maps, skin_set_tone

        maps.refresh(skin)
        props = body.juststage
        skin_set_tone.main(skin_set_tone.Params(new, props.melanin, props.eumelanin, props.blood, props.oiliness))
    return body
