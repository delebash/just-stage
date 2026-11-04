# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The asset library (docs/standards/project-files.md §2): Blender asset libraries, one self-contained `.blend` per
asset in its catalogue's folder, JustStage's fixed catalogue UUIDs, and the rule that an asset without provenance and
a licence label is refused."""

import importlib
import subprocess

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
        assert list(src.objects) == ["Tall man"]  # listed by the name it was saved as
    assert obj.name == "Library test"  # the scene's character keeps its own


def test_an_asset_without_its_licence_is_refused(human, tmp_path):
    result, _obj = human
    with pytest.raises(api.CommandError, match="licence"):
        api.run("juststage.library.save", character=result.character, catalog="Characters", name="x",
                licence="", provenance="JustStage", library=str(tmp_path))  # fmt: skip


def test_a_library_character_comes_into_the_scene(human, tmp_path):
    result, obj = human
    saved = api.run("juststage.library.save", character=result.character, catalog="Characters", name="Preset",
                    licence="CC0-1.0", provenance="JustStage", library=str(tmp_path))  # fmt: skip
    before = {o.name for o in bpy.data.objects}
    added = api.run("juststage.library.add", path=saved.path)
    new = {o.name for o in bpy.data.objects} - before
    try:
        assert added.object in new
        assert bpy.data.objects[added.object].juststage.character_id == added.character
        assert added.character != obj.juststage.character_id  # its own character, not the saved one's
        assert [p["name"] for p in library.characters(tmp_path)] == ["Preset"]
    finally:
        for name in new:
            bpy.data.objects.remove(bpy.data.objects[name])


@pytest.fixture
def other():
    result = api.run("juststage.body.create", name="Library other")
    yield result, bpy.data.objects[result.object]
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == result.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(bpy.data.objects[result.object])


def test_a_groom_saved_and_applied_to_another_character(human, other, tmp_path):
    """Hair/<type> saves the character's groom of that type without the body; applying it replaces the other
    character's groom of that type (CC5's way) and attaches it as `juststage.hair.add` does."""
    result, obj = human
    api.run("juststage.hair.add", character=result.character, style="back_pigtail")
    saved = api.run("juststage.library.save", character=result.character, catalog="Hair/Scalp", name="Pigtail",
                    licence="CC0-1.0", provenance="MakeHuman hair pack", library=str(tmp_path))  # fmt: skip
    with bpy.data.libraries.load(saved.path, assets_only=True) as (src, _dst):
        assert list(src.objects) == ["Pigtail"]
    with bpy.data.libraries.load(saved.path) as (src, _dst):
        assert obj.name not in src.objects and len(src.objects) == 2  # the groom and its hair tie, no body
    assert obj.children and all(o.parent == obj for o in obj.children)  # the saved character keeps its own
    with pytest.raises(api.CommandError, match="character"):
        api.run("juststage.library.add", path=saved.path)
    o_result, o_obj = other
    api.run("juststage.hair.add", character=o_result.character, style="short_hedgehog")
    added = api.run("juststage.library.add", path=saved.path, character=o_result.character)
    scalp = [o for o in bpy.data.objects if o.juststage.part_of == o_result.character and o.juststage.part == "scalp"]
    groom = bpy.data.objects[added.object]
    assert groom in scalp and len(scalp) == 2 and all(o.parent == o_obj for o in scalp)  # the hedgehog replaced
    assert groom.type == "CURVES" and groom.data.surface == o_obj
    assert added.character == o_result.character


def test_a_skin_preset_saved_and_applied(human, other, tmp_path):
    result, obj = human
    api.run("juststage.skin.set_tone", character=result.character, melanin=0.2, blood=0.03)
    saved = api.run("juststage.library.save", character=result.character, catalog="Skins", name="Deep",
                    licence="CC0-1.0", provenance="JustStage skin.set_tone", library=str(tmp_path))  # fmt: skip
    with bpy.data.libraries.load(saved.path, assets_only=True) as (src, _dst):
        assert list(src.materials) == ["Deep"] and not list(src.objects)
    o_result, o_obj = other
    api.run("juststage.library.add", path=saved.path, character=o_result.character)
    assert (o_obj.juststage.melanin, o_obj.juststage.blood) == pytest.approx((0.2, 0.03))
    assert o_obj.juststage.skin_material.juststage.melanin == pytest.approx(0.2)
    assert "Deep" not in bpy.data.materials  # the preset is read, not kept beside the character's own skin


def test_a_saved_asset_survives_its_file_being_saved_again(human, other, tmp_path):
    """Assets are written with no users (they're in no scene): Blender drops such data-blocks when the file is saved
    again (the thumbnail step does), unless they carry a fake user. An asset brought into a scene drops it again."""
    result, _obj = human
    api.run("juststage.hair.add", character=result.character, style="back_pigtail")
    saved = api.run("juststage.library.save", character=result.character, catalog="Hair/Scalp", name="Kept",
                    licence="CC0-1.0", provenance="MakeHuman hair pack", library=str(tmp_path))  # fmt: skip
    resave = "import bpy, sys; bpy.ops.wm.open_mainfile(filepath=sys.argv[-1]); bpy.ops.wm.save_mainfile()"
    subprocess.run([bpy.app.binary_path, "-b", "--factory-startup", "--python-expr", resave, "--", saved.path],
                   check=True, capture_output=True, timeout=120)  # fmt: skip
    with bpy.data.libraries.load(saved.path, assets_only=True) as (src, _dst):
        assert list(src.objects) == ["Kept"]
    with bpy.data.libraries.load(saved.path) as (src, _dst):
        assert len(src.objects) == 2  # the groom and its hair tie
    o_result, _o_obj = other
    added = api.run("juststage.library.add", path=saved.path, character=o_result.character)
    assert not any(o.use_fake_user for o in bpy.data.objects if o.juststage.part_of == o_result.character)
    assert bpy.data.objects[added.object].users_collection
