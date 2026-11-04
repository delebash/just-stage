# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Mapped skins (modules/skin/maps.py): every character has the body's UDIM layout, a skin's maps go onto any
character from the library, and the tone sliders recolour a mapped skin."""

import importlib

import bpy
import numpy as np
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
library = importlib.import_module("bl_ext.system.juststage.core.library")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")
material = importlib.import_module("bl_ext.system.juststage.modules.skin.material")
skin_optics = importlib.import_module("bl_ext.system.juststage.core.skin_optics")
paths = importlib.import_module("bl_ext.system.juststage.paths")


@pytest.fixture
def human():
    made = api.run("juststage.body.create", name="Map test")
    yield made, bpy.data.objects[made.object]
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(bpy.data.objects[made.object])


def test_every_character_has_the_udim_layout(human):
    _made, body = human
    layer = body.data.uv_layers[maps.UV]
    uv = np.empty(len(body.data.loops) * 2, np.float32)
    layer.data.foreach_get("uv", uv)
    tiles = 1001 + np.floor(uv.reshape(-1, 2)[:, 0]).astype(int)
    assert set(tiles.tolist()) == set(maps.TILES)  # head and neck, torso, arms, legs, nails
    assert body.data.uv_layers["UVMap"].active_render  # hm08's own unwrap stays the render one


def _mapped_skin(folder, melanin):
    """A small mapped skin saved in a library folder: flat tiles, the skin's own tone `melanin`."""
    made = api.run("juststage.body.create", name="Skin source")
    body = bpy.data.objects[made.object]
    api.run("juststage.skin.set_tone", character=made.character, melanin=melanin)
    mat = body.juststage.skin_material
    mat.juststage.map_melanin = melanin
    fill = {"base_color": (0.6, 0.45, 0.4), "normal": (0.5, 0.5, 1.0), "roughness": (0.6,) * 3}
    images = {}
    for channel in maps.CHANNELS:
        for number in maps.TILES:
            colour = np.broadcast_to(fill.get(channel, (0.5,) * 3), (8, 8, 3))
            maps.write_png(folder / f"test.{channel}.{number}.png", colour)
        images[channel] = maps.tiled_image(folder, f"test.{channel}")
    maps.write_png(folder / "pores.png", np.full((8, 8, 3), 0.5))
    pores = bpy.data.images.load(str(folder / "pores.png"))
    pores.pack()
    maps.build_material(mat, images, pores)
    out = api.run("juststage.library.save", character=made.character, catalog="Skins", name="Test mapped",
                  licence="CC0-1.0", provenance="test", library=str(folder / "lib"))  # fmt: skip
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(body)
    return out.path


def test_a_mapped_skin_goes_onto_any_character_in_its_own_tone(human, tmp_path):
    made, body = human
    path = _mapped_skin(tmp_path, melanin=0.12)
    assert library.kind(path) == "skin"
    api.run("juststage.library.add", path=path, character=made.character)
    mat = body.juststage.skin_material
    assert mat.juststage.has_maps and mat.name in body.data.materials
    nodes = mat.node_tree.nodes
    assert nodes[maps.NODE + "uv"].uv_map == maps.UV
    assert nodes[maps.NODE + "base_color"].image.source == "TILED"
    # the body's mottling (below the head tile) on the way to the colour
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    assert bsdf.inputs["Base Color"].links[0].from_node == nodes[maps.NODE + "mottle"]
    assert body.juststage.melanin == pytest.approx(0.12)  # the skin's own tone came with it
    gain = np.array(nodes[maps.NODE + "gain"].inputs[1].default_value)
    assert np.allclose(gain, 1.0, atol=1e-4)  # at its own tone, the map as made


def test_the_tone_sliders_recolour_a_mapped_skin(human, tmp_path):
    made, body = human
    api.run("juststage.library.add", path=_mapped_skin(tmp_path, melanin=0.12), character=made.character)
    api.run("juststage.skin.set_tone", character=made.character, melanin=0.02)
    mat = body.juststage.skin_material
    tables = skin_optics.load_tables(paths.FETCHED / "optics")
    want = np.array(skin_optics.Skin(0.02, 0.6, 0.016).linear_rgb(tables)) / np.array(
        skin_optics.Skin(0.12, 0.6, 0.016).linear_rgb(tables)
    )
    assert np.allclose(mat.node_tree.nodes[maps.NODE + "gain"].inputs[1].default_value, want, rtol=1e-4)
    assert (want > 1.0).all()  # lighter than the map's own tone
