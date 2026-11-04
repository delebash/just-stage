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


def save(objects: list, catalog: str, name: str, folder: Path, meta: dict) -> Path:
    """`objects` (the asset first) written as one `.blend` in `<folder>/<catalog>/<name>.blend`, the first marked as an
    asset in that catalogue with Blender's metadata fields."""
    uid = catalog_ids()[catalog]
    prepare(folder)
    asset = objects[0]
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
    bpy.data.libraries.write(str(target), set(objects), path_remap="RELATIVE_ALL", compress=True)
    asset.asset_clear()  # the scene's own copy stays a plain object
    return target


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
        if obj.asset_data is not None:
            obj.asset_clear()
        if obj.juststage.part_of == old:
            obj.juststage.part_of = new
    body.juststage.character_id = new
    return body
