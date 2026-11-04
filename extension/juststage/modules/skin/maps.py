# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""A skin's maps (docs/standards/character-data-model.md: the body's one UDIM layout, 1001 head and neck … 1005 nails;
the channels `base_color`, `normal` - tangent space, OpenGL - `roughness`, `cavity`, and a fine `height`), as CC5's
skins carry scanned colour and relief (the realism working doc, `docs/plans/2026-11-04-realism.md`).

Every character has the layout (`add_layout`, made once by `tools/make_udim.py`), so a skin's maps fit any of them.
A skin is a material: Principled BSDF with Random Walk (Skin) subsurface from the chromophore model (material.py), the
maps on its inputs, and the tone it was made at (`juststage.map_*`). The character's own tone recolours it by a
per-channel gain - its tone's colour over the skin's own (core/skin_optics.py) - so the Skin tab's sliders keep working
on a mapped skin. Pores everywhere from a tiled scan patch on hm08's own UVs (the face test's, ~5.6 cm a tile).
Images: Blender's UDIM tiled images (https://docs.blender.org/manual/en/5.3/modeling/meshes/uv/workflows/udims.html).
"""

from __future__ import annotations

import bpy
import numpy as np

from ... import paths

LAYOUT_TOOL = "python tools/dev.py blender -b --python tools/make_udim.py"
UV = "UDIM"
CHANNELS = ("base_color", "normal", "roughness", "cavity", "height")
COLOUR_SPACE = {"base_color": "sRGB"}  # the rest are data
TILES = (1001, 1002, 1003, 1004, 1005)
#: the face test's skin shading (tools/face_test/test_face_project.py, rounds 40-79)
COAT_WEIGHT, COAT_ROUGHNESS, COAT_IOR, SHEEN_WEIGHT, SHEEN_ROUGHNESS = 0.12, 0.44, 1.45, 0.1, 0.4
HEIGHT_STRENGTH, HEIGHT_DISTANCE = 0.15, 0.0004  # the painting's own fine relief (the normal map carries the larger)
PORE_TILES = 20.0  # tiles per hm08 UV unit: the face is 1.13 m a UV unit (measured), the tile ~5.6 cm
PORE_STRENGTH, PORE_DISTANCE = 0.35, 0.0002
SPECULAR_FROM_CAVITY = 0.5  # Blender's standard specular level where the cavity map is 1
#: the body's mottling below the head tile (its maps are plain colour there): a seamless 3D noise in the object's own
#: metres, a few centimetres across, +-MOTTLE/2 of the colour - SkinGen's broad "blotch" layer in kind
MOTTLE, MOTTLE_SCALE, MOTTLE_DETAIL = 0.10, 18.0, 4.0
NODE = "juststage.maps."  # this module's nodes are named with it


def layout() -> tuple[np.ndarray, np.ndarray]:
    data = np.load(paths.generated("skin", "udim.npz", tool=LAYOUT_TOOL))
    return data["uv"], data["tile"]


def add_layout(obj: bpy.types.Object) -> None:
    """The body's UDIM layer (each loop's place in its tile), beside hm08's own `UVMap`."""
    me = obj.data
    if UV in me.uv_layers:
        return
    uv, _tile = layout()
    if len(uv) != len(me.loops):
        raise ValueError(f"{obj.name}: {len(me.loops)} loops, the layout has {len(uv)} (not hm08?)")
    active = me.uv_layers.active
    me.uv_layers.new(name=UV).data.foreach_set("uv", uv.ravel())
    if active is not None:
        me.uv_layers.active = active  # hm08's own map stays the one the tools edit
    for layer in me.uv_layers:
        layer.active_render = layer.name == "UVMap"


def write_png(path, rgb: np.ndarray, depth: str = "8") -> None:
    """A PNG of the values as given - no colour transform: colour stays sRGB-encoded, data stays data - by OpenImageIO
    (Blender's own copy); `rgb` rows bottom first as Blender's pixels, PNG's top first."""
    import OpenImageIO as oiio

    h, w = rgb.shape[:2]
    spec = oiio.ImageSpec(w, h, 3, oiio.UINT8 if depth == "8" else oiio.UINT16)
    out = oiio.ImageOutput.create(str(path))
    out.open(str(path), spec)
    out.write_image(np.ascontiguousarray(np.clip(rgb[::-1], 0.0, 1.0), dtype=np.float32))
    out.close()


def tiled_image(folder, stem: str) -> bpy.types.Image:
    """`<folder>/<stem>.<tile>.png` for every tile as one UDIM image, packed into the .blend."""
    from pathlib import Path

    folder = Path(folder)
    image = bpy.data.images.load(str(folder / f"{stem}.1001.png"), check_existing=False)
    image.source = "TILED"
    image.filepath = str(folder / f"{stem}.<UDIM>.png")
    for number in TILES[1:]:
        image.tiles.new(tile_number=number)
    image.reload()
    image.name = stem
    image.pack()
    return image


def _node(nt, kind: str, name: str, location=(0, 0)):
    node = nt.nodes.get(NODE + name) or nt.nodes.new(kind)
    node.name = node.label = NODE + name
    node.location = location
    return node


def build_material(mat: bpy.types.Material, images: dict[str, bpy.types.Image], pores: bpy.types.Image) -> None:
    """The skin's maps on its Principled BSDF (material.py made the BSDF and its scattering): `images` by channel,
    UDIM tiled; `pores` a tiling height patch."""
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    links = nt.links
    uv = _node(nt, "ShaderNodeUVMap", "uv", (-1400, 0))
    uv.uv_map = UV
    tex = {}
    for k, channel in enumerate(CHANNELS):
        node = _node(nt, "ShaderNodeTexImage", channel, (-1100, 300 - 280 * k))
        node.image = images[channel]
        node.image.colorspace_settings.name = COLOUR_SPACE.get(channel, "Non-Color")
        node.interpolation = "Cubic" if channel in ("normal", "height") else "Linear"
        links.new(uv.outputs["UV"], node.inputs["Vector"])
        tex[channel] = node
    gain = _node(nt, "ShaderNodeVectorMath", "gain", (-750, 300))
    gain.operation = "MULTIPLY"
    gain.inputs[1].default_value = (1.0, 1.0, 1.0)
    links.new(tex["base_color"].outputs["Color"], gain.inputs[0])
    # the body's mottling: where the UDIM layer's u is past the head tile (u >= 1)
    place = _node(nt, "ShaderNodeTexCoord", "place", (-1400, 600))
    noise = _node(nt, "ShaderNodeTexNoise", "mottle_noise", (-1200, 600))
    noise.inputs["Scale"].default_value, noise.inputs["Detail"].default_value = MOTTLE_SCALE, MOTTLE_DETAIL
    links.new(place.outputs["Object"], noise.inputs["Vector"])
    tile = _node(nt, "ShaderNodeSeparateXYZ", "tile", (-1200, 420))
    links.new(uv.outputs["UV"], tile.inputs["Vector"])
    body = _node(nt, "ShaderNodeMath", "body", (-1000, 420))
    body.operation, body.inputs[1].default_value = "GREATER_THAN", 0.999
    links.new(tile.outputs["X"], body.inputs[0])
    swing = _node(nt, "ShaderNodeMapRange", "mottle_swing", (-1000, 600))
    swing.inputs["To Min"].default_value, swing.inputs["To Max"].default_value = 1.0 - MOTTLE / 2, 1.0 + MOTTLE / 2
    links.new(noise.outputs["Fac"], swing.inputs["Value"])
    on_body = _node(nt, "ShaderNodeMix", "mottle_on_body", (-800, 600))
    on_body.data_type = "FLOAT"
    links.new(body.outputs["Value"], on_body.inputs["Factor"])
    next(i for i in on_body.inputs if i.identifier == "A_Float").default_value = 1.0
    links.new(swing.outputs["Result"], next(i for i in on_body.inputs if i.identifier == "B_Float"))
    mottle = _node(nt, "ShaderNodeVectorMath", "mottle", (-600, 300))
    mottle.operation = "SCALE"
    links.new(gain.outputs["Vector"], mottle.inputs[0])
    links.new(next(o for o in on_body.outputs if o.identifier == "Result_Float"), mottle.inputs["Scale"])
    links.new(mottle.outputs["Vector"], bsdf.inputs["Base Color"])
    normal = _node(nt, "ShaderNodeNormalMap", "normal_map", (-750, 20))
    normal.space, normal.uv_map = "TANGENT", UV
    links.new(tex["normal"].outputs["Color"], normal.inputs["Color"])
    links.new(tex["roughness"].outputs["Color"], bsdf.inputs["Roughness"])
    spec = _node(nt, "ShaderNodeMath", "specular", (-750, -300))
    spec.operation, spec.inputs[1].default_value = "MULTIPLY", SPECULAR_FROM_CAVITY
    links.new(tex["cavity"].outputs["Color"], spec.inputs[0])
    links.new(spec.outputs["Value"], bsdf.inputs["Specular IOR Level"])
    fine = _node(nt, "ShaderNodeBump", "height_bump", (-450, -100))
    fine.inputs["Strength"].default_value, fine.inputs["Distance"].default_value = HEIGHT_STRENGTH, HEIGHT_DISTANCE
    links.new(tex["height"].outputs["Color"], fine.inputs["Height"])
    links.new(normal.outputs["Normal"], fine.inputs["Normal"])
    body_uv = _node(nt, "ShaderNodeUVMap", "body_uv", (-1400, -900))
    body_uv.uv_map = "UVMap"
    mapping = _node(nt, "ShaderNodeMapping", "pore_mapping", (-1200, -900))
    mapping.inputs["Scale"].default_value = (PORE_TILES, PORE_TILES, 1.0)
    links.new(body_uv.outputs["UV"], mapping.inputs["Vector"])
    pore = _node(nt, "ShaderNodeTexImage", "pores", (-1000, -900))
    pore.image = pores
    pore.image.colorspace_settings.name = "Non-Color"
    links.new(mapping.outputs["Vector"], pore.inputs["Vector"])
    bump = _node(nt, "ShaderNodeBump", "pore_bump", (-250, -200))
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = PORE_STRENGTH, PORE_DISTANCE
    links.new(pore.outputs["Color"], bump.inputs["Height"])
    links.new(fine.outputs["Normal"], bump.inputs["Normal"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Coat Weight"].default_value = COAT_WEIGHT
    bsdf.inputs["Coat Roughness"].default_value = COAT_ROUGHNESS
    bsdf.inputs["Coat IOR"].default_value = COAT_IOR
    bsdf.inputs["Sheen Weight"].default_value = SHEEN_WEIGHT
    bsdf.inputs["Sheen Roughness"].default_value = SHEEN_ROUGHNESS
    mat.juststage.has_maps = True


def set_gain(mat: bpy.types.Material, rgb: tuple[float, float, float]) -> None:
    """The character's tone over the skin's own: `rgb` is the tone's linear colour (skin_optics)."""
    from ...core import skin_optics

    record = mat.juststage
    tables = skin_optics.load_tables(paths.FETCHED / "optics")
    own = skin_optics.Skin(record.map_melanin, record.map_eumelanin, record.map_blood).linear_rgb(tables)
    gain = tuple(float(t / o) for t, o in zip(rgb, own, strict=True))
    mat.node_tree.nodes[NODE + "gain"].inputs[1].default_value = gain


def apply(character: bpy.types.Object, skin: bpy.types.Material) -> bpy.types.Material:
    """A mapped skin on the character: a copy of `skin` (each character its own), in the place of its skin material,
    in the character's own tone."""
    from . import skin_set_tone

    add_layout(character)
    old = character.juststage.skin_material
    mine = skin.copy()
    mine.name = f"JustStage Skin ({character.name})"
    mine.use_fake_user = False
    slots = character.data.materials
    if old is not None and old.name in slots:
        slots[slots.find(old.name)] = mine
    else:
        slots.append(mine)
    character.juststage.skin_material = mine
    if old is not None and old.users == 0:
        bpy.data.materials.remove(old)
    props = character.juststage
    skin_set_tone.main(
        skin_set_tone.Params(props.character_id, props.melanin, props.eumelanin, props.blood, props.oiliness)
    )
    return mine
