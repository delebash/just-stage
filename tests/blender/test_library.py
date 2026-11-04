# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The asset library (docs/standards/project-files.md §2): Blender asset libraries, one self-contained `.blend` per
asset in its catalogue's folder, JustStage's fixed catalogue UUIDs, and the rule that an asset without provenance and
a licence label is refused."""

import importlib

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
library = importlib.import_module("bl_ext.system.juststage.core.library")


def test_the_catalogues_are_fixed_and_complete():
    ids = library.catalog_ids()
    for path in ("Characters", "Bodies/Presets", "Heads/Presets", "Skins", "Hair/Scalp", "Clothes", "Motions"):
        assert path in ids
    assert len(set(ids.values())) == len(ids)


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Library test", gender=0.9)
    yield result, bpy.data.objects[result.object]
    bpy.data.objects.remove(bpy.data.objects[result.object])


def test_a_character_saved_as_an_asset(human, tmp_path):
    result, obj = human
    out = api.run(
        "juststage.library.save",
        character=result.character,
        catalog="Characters",
        name="Tall man",
        description="A test character",
        licence="CC0-1.0",
        provenance="JustStage body.create",
        library=str(tmp_path),
    )
    assert out.path.endswith("Characters\\Tall man.blend") or out.path.endswith("Characters/Tall man.blend")
    assert (tmp_path / "blender_assets.cats.txt").exists()
    with bpy.data.libraries.load(out.path, assets_only=True) as (src, _dst):
        assert "Library test" in src.objects


def test_an_asset_without_its_licence_is_refused(human, tmp_path):
    result, _obj = human
    with pytest.raises(api.CommandError, match="licence"):
        api.run("juststage.library.save", character=result.character, catalog="Characters", name="x",
                licence="", provenance="JustStage", library=str(tmp_path))  # fmt: skip
