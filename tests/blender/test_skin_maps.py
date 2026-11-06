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
    maps.build_material(mat, images)  # the pores: the shared tile (maps.pore_relief)
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
    # the body's mottling (below the head tile) on the way to the colour (under the nails' plate)
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    nail = nodes[maps.NODE + "nail_colour"]
    assert next(i for i in nail.inputs if i.identifier == "A_Color").links[0].from_node == nodes[maps.NODE + "mottle"]
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


def _shader_on(mat, target):
    output = next(n for n in mat.node_tree.nodes if n.type == "OUTPUT_MATERIAL" and n.target == target)
    return output, output.inputs["Surface"].links[0].from_node


def _assert_live_twin(mat):
    """The film's skin (Cycles, the export) on the All output; the live view's (EEVEE) on its own output - the same
    inputs from the same sources, its scattering x material.EEVEE_SCATTER."""
    film_out, film = _shader_on(mat, "ALL")
    _live_out, live = _shader_on(mat, "EEVEE")
    assert film.type == live.type == "BSDF_PRINCIPLED" and film != live
    assert film_out.is_active_output and material.principled(mat) == film
    assert sum(n.type == "BSDF_PRINCIPLED" for n in mat.node_tree.nodes) == 2  # synced again, never added again
    assert live.subsurface_method == film.subsurface_method
    scale = film.inputs["Subsurface Scale"].default_value * material.EEVEE_SCATTER
    assert live.inputs["Subsurface Scale"].default_value == pytest.approx(scale)
    for socket, twin in zip(film.inputs, live.inputs, strict=True):
        if socket.name == "Subsurface Scale" or not socket.enabled:
            continue
        if socket.is_linked:
            assert [lk.from_socket for lk in twin.links] == [socket.links[0].from_socket], socket.name
        elif hasattr(socket, "default_value"):
            assert not twin.is_linked, socket.name
            assert np.allclose(np.array(twin.default_value), np.array(socket.default_value)), socket.name


def test_the_live_view_scatters_twice_as_far_as_the_film(human, tmp_path):
    """EEVEE's scattering on our skin is shorter than Cycles' Random Walk: x2 brings its lit pore detail to the
    film's (the realism doc §6a, "Skin scattering alone"); the film keeps the measured radius."""
    made, body = human
    api.run("juststage.skin.set_tone", character=made.character)
    _assert_live_twin(body.juststage.skin_material)
    api.run("juststage.library.add", path=_mapped_skin(tmp_path, melanin=0.12), character=made.character)
    api.run("juststage.skin.set_tone", character=made.character, melanin=0.02)
    mat = body.juststage.skin_material
    _assert_live_twin(mat)  # the maps' links reach both
    detail = importlib.import_module("bl_ext.system.juststage.modules.skin.detail")
    detail.apply(mat, body.name, np.zeros((8, 8)), 20.0, 0.5, {})
    _assert_live_twin(mat)  # and the detail's bump


def _factor(nodes, name, tile_index):
    """The scale the relief layer `name` gets on UDIM tile `tile_index` (0 = 1001), read off its nodes."""
    value = nodes[maps.NODE + f"{name}_scale_1001"].outputs[0].default_value
    for k, number in enumerate(maps.TILES[1:], start=1):
        past = nodes[maps.NODE + f"{name}_past_{number}"].inputs[1].default_value
        step = nodes[maps.NODE + f"{name}_scale_{number}"].inputs[1].default_value
        value += step * (tile_index > past)
    return value


def test_the_relief_layers_keep_one_size_on_every_tile_and_the_microrelief_shades(human, tmp_path):
    made, body = human
    api.run("juststage.library.add", path=_mapped_skin(tmp_path, melanin=0.12), character=made.character)
    nodes = body.juststage.skin_material.node_tree.nodes
    coords = nodes[maps.NODE + "pores"].inputs["Vector"].links[0].from_node
    assert coords.inputs[0].links[0].from_node == nodes[maps.NODE + "uv"]  # the UDIM layer, not hm08's UVMap
    assert nodes[maps.NODE + "pores"].image == maps.pore_relief()[0]  # every skin the one clean tile
    for name, size in (("pore", maps.pore_relief()[1]), ("micro", maps.MICRO_TILE_MM)):
        for k, number in enumerate(maps.TILES):  # hm08's UVMap gave the thigh's pores six times the face's size
            assert _factor(nodes, name, k) == pytest.approx(maps.MM_PER_UV[number] / size)
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    micro = nodes[maps.NODE + "micro_bump"]
    assert nodes[maps.NODE + "nail_raise"].inputs["Normal"].links[0].from_node == micro  # then the nails' edge
    assert micro.inputs["Normal"].links[0].from_node == nodes[maps.NODE + "pore_bump"]
    assert nodes[maps.NODE + "micro"].image.size[0] >= 2048


def test_the_nails_get_a_plate_over_the_skin_on_their_tile(human, tmp_path):
    made, body = human
    api.run("juststage.library.add", path=_mapped_skin(tmp_path, melanin=0.12), character=made.character)
    nodes = body.juststage.skin_material.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    margin = bsdf.inputs["Base Color"].links[0].from_node  # the lid margin's pink, last
    assert margin == nodes[maps.NODE + "margin_colour"]
    mouth = margin.inputs[0].links[0].from_node  # the mouth's lining over the nails' plate
    assert mouth == nodes[maps.NODE + "mouth_colour"]
    lips = next(i for i in mouth.inputs if i.identifier == "A_Color").links[0].from_node  # the lips' vermilion
    assert lips == nodes[maps.NODE + "lips_colour"]
    assert lips.inputs[0].links[0].from_node == nodes[maps.NODE + "nail_groove"]
    rough = bsdf.inputs["Roughness"].links[0].from_node  # the margin's, over the mouth's, the lips', the nails'
    rough = next(i for i in rough.inputs if i.identifier == "A_Float").links[0].from_node
    assert rough == nodes[maps.NODE + "mouth_rough"]
    rough = next(i for i in rough.inputs if i.identifier == "A_Float").links[0].from_node
    assert rough == nodes[maps.NODE + "lips_rough"]
    assert next(i for i in rough.inputs if i.identifier == "A_Float").links[0].from_node == nodes[maps.NODE + "nail_rough"]
    assert bsdf.inputs["Normal"].links[0].from_node == nodes[maps.NODE + "nail_raise"]
    coords = nodes[maps.NODE + "nail_coords"].image  # each nail's own coordinates, made once (make_nail_coords.py)
    alpha = np.empty(coords.size[0] * coords.size[1] * 4, np.float32)
    coords.pixels.foreach_get(alpha)
    assert 0.3 < (alpha[3::4] > 0.5).mean() < 0.9  # the nails fill most of their tile
    assert nodes[maps.NODE + "nail_on_tile"].inputs[1].default_value == maps.NAIL_TILE_INDEX


def test_the_mouths_lining_is_wet_mucosa_on_the_head_tile(human, tmp_path):
    made, body = human
    api.run("juststage.library.add", path=_mapped_skin(tmp_path, melanin=0.12), character=made.character)
    nodes = body.juststage.skin_material.node_tree.nodes
    mask = nodes[maps.NODE + "mouth_mask"].image  # the inner lips and the mouth (make_mouth_mask.py)
    px = np.empty(mask.size[0] * mask.size[1] * 4, np.float32)
    mask.pixels.foreach_get(px)
    assert 0.002 < (px[0::4] > 0.5).mean() < 0.05  # a small part of the head tile
    assert nodes[maps.NODE + "mouth_on_head"].inputs[1].default_value == 0.0  # tile 1001 only


def test_the_lid_margin_is_wet_pink_tissue_on_a_mapped_skin(human, tmp_path):
    """Base v2's margin rows (`js_margin`) tint the skin pink, glossy and wet (maps._margin_layer) - over the colour
    the other layers set, last."""
    made, body = human
    api.run("juststage.library.add", path=_mapped_skin(tmp_path, melanin=0.05), character=made.character)
    nodes = body.juststage.skin_material.node_tree.nodes
    attr = nodes[maps.NODE + "margin_attr"]
    assert attr.attribute_name == "js_margin" and "js_margin" in body.data.attributes
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    assert bsdf.inputs["Base Color"].links[0].from_node == nodes[maps.NODE + "margin_colour"]
    assert bsdf.inputs["Roughness"].links[0].from_node == nodes[maps.NODE + "margin_rough"]


def test_the_relief_layers_keep_one_size_inside_a_tile(human, tmp_path):
    """hm08's UVs are not even inside a tile: the head tile's neck and shoulders span ~1.6x the face's millimetres a UV
    unit (measured 2026-11-06), so one tiling a tile gave them pores 1.6x the face's and a step at the torso's border.
    Each corner carries its place's density (maps.add_texel), the relief layers cross-fade half-octave tilings by it."""
    made, body = human
    api.run("juststage.library.add", path=_mapped_skin(tmp_path, melanin=0.12), character=made.character)
    me = body.data
    attr = me.attributes[maps.TEXEL]
    assert (attr.domain, attr.data_type) == ("CORNER", "FLOAT")
    texel = np.empty(len(me.loops), np.float32)
    attr.data.foreach_get("value", texel)
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[maps.UV].data.foreach_get("uv", uv)
    head = np.floor(uv.reshape(-1, 2)[:, 0]) == 0
    loop_vert = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loop_vert)
    co = np.array([v.co for v in me.vertices])[loop_vert]
    top, front = co[:, 2].max(), co[head, 1].min()
    face = head & (co[:, 1] < front + 0.03) & (co[:, 2] > top - 0.22)  # the face's front, nose to brow
    low = head & (co[:, 2] < top - 0.30)  # the head tile's neck base and shoulders
    assert abs(np.median(texel[face])) < 0.5  # the tile's own tiling: the face it was measured on
    assert np.median(texel[low]) > 0.9  # ~1.6x the face's mm a UV unit: 2 log2(1.6) = 1.36
    nodes = body.juststage.skin_material.node_tree.nodes
    for name in ("pores", "micro"):
        for k in maps.TEXEL_LEVELS:
            level = nodes[maps.NODE + (name if k == 0 else f"{name}_level{k}")]
            assert level.image == nodes[maps.NODE + name].image
        assert nodes[maps.NODE + f"{name}_texel_lo"].inputs[0].links[0].from_node == nodes[maps.NODE + "texel"]
    assert nodes[maps.NODE + "texel"].attribute_name == maps.TEXEL
    assert nodes[maps.NODE + "pore_bump"].inputs["Height"].links[0].from_node == nodes[maps.NODE + "pores_blend"]


def test_the_neck_on_the_head_tile_is_body_skin(human, tmp_path):
    """The head tile reaches down the neck to the chest: its neck took the cheek's roughness (0.48 against the body's
    0.59) and the face's clear coat, the body's mottle stopping at the tile's border - a glossy band ending in a line
    across the chest on dark skin (the clean-input gate, 2026-11-06). The region map makes the neck body skin, and its
    face share (alpha) fades the coat and the mottle across the neck."""
    made, body = human
    api.run("juststage.library.add", path=_mapped_skin(tmp_path, melanin=0.12), character=made.character)
    image = maps.face_regions()
    w, h = image.size
    px = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    me = body.data
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[maps.UV].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    loop_vert = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loop_vert)
    co = np.array([v.co for v in me.vertices])[loop_vert]
    head = uv[:, 0] < 1.0
    top = co[:, 2].max()
    sample = px[(uv[:, 1] * h).astype(int).clip(0, h - 1), (uv[:, 0] * w).astype(int).clip(0, w - 1)]
    neck = head & (co[:, 2] < top - 0.30)
    cheek = head & (co[:, 2] > top - 0.17) & (co[:, 2] < top - 0.12) & (co[:, 1] < co[head, 1].min() + 0.05)
    assert np.median(sample[neck, 1]) == pytest.approx(material.ROUGHNESS, abs=0.02)
    # the face's share in a map of its own: packed in the region map's alpha, the live view divided R, G, B by it -
    # the neck's relief at 2x and more (gate run 8: a coarse patch with a jagged edge on the neck)
    shares = maps.face_share()
    sw, sh = shares.size
    spx = np.empty(sw * sh * 4, np.float32)
    shares.pixels.foreach_get(spx)
    spx = spx.reshape(sh, sw, 4)
    at = spx[(uv[:, 1] * sh).astype(int).clip(0, sh - 1), (uv[:, 0] * sw).astype(int).clip(0, sw - 1), 0]
    assert np.median(at[neck]) < 0.1 and np.median(at[cheek]) > 0.9
    nodes = body.juststage.skin_material.node_tree.nodes
    assert not nodes[maps.NODE + "face_regions"].outputs["Alpha"].is_linked
    assert np.allclose(px[..., 3], 1.0)  # no alpha in the region map
    share = nodes[maps.NODE + "body_share"]
    for name in ("coat", "mottle_on_body"):
        assert nodes[maps.NODE + name].inputs["Factor"].links[0].from_node == share


def test_the_wet_layers_keep_their_coat_and_the_lips_shine(human, tmp_path):
    """The nails', the mouth's and the lips' coat reach the BSDF (the base coat was linked after the nails' and the
    mouth's, replacing both - found 2026-11-06); the lips are smoother and coated (HD Aaron's lower lip shines, ours was
    matte orange: a* 23 / b* 24 against his 30 / 15 at the gate's lips view)."""
    made, body = human
    api.run("juststage.library.add", path=_mapped_skin(tmp_path, melanin=0.12), character=made.character)
    nodes = body.juststage.skin_material.node_tree.nodes
    bsdf = material.principled(body.juststage.skin_material)

    def chain(socket_name):
        names, sock = [], bsdf.inputs[socket_name]
        while sock.is_linked:
            node = sock.links[0].from_node
            names.append(node.name.removeprefix(maps.NODE))
            sock = next((i for i in node.inputs if i.identifier in ("A_Float", "A_Color") and i.is_linked), None)
            if sock is None:
                break
        return names

    coat = chain("Coat Weight")
    for name in ("nail_coat", "mouth_coat", "lips_coat", "coat"):
        assert name in coat, coat
    assert "lips_rough" in chain("Roughness")
    tint = maps.LIP_TINT
    assert tint[1] < tint[2]  # redder, less yellow: blue kept above green


def test_the_nails_have_no_pores(human, tmp_path):
    """The skin's pores and microrelief tiled onto the nails' tile under their coat read as a bumpy plate with white
    specks (gate run 4's nails view; HD Aaron's plates smooth) - nails have none."""
    made, body = human
    api.run("juststage.library.add", path=_mapped_skin(tmp_path, melanin=0.12), character=made.character)
    nodes = body.juststage.skin_material.node_tree.nodes
    for key in ("pore", "micro"):
        factor = nodes[maps.NODE + f"{key}_depth"].inputs[0].links[0].from_node
        assert factor.name == maps.NODE + f"{key}_off_nails", factor.name
