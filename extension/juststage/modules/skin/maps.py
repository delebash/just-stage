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
#: each UDIM tile's millimetres per UV unit on the default human (measured 2026-11-05: the median polygon's
#: sqrt(3D area / UV area); the head tile by its face, where relief shows): the relief layers keep one real size on
#: every tile. hm08's own `UVMap`, which carried the pores before, spans 1.1 m a unit on the face but 2.1 on the torso
#: and 7.0 on the thigh - the pores were twice and six times their size there
MM_PER_UV = {1001: 724.0, 1002: 851.0, 1003: 753.0, 1004: 1224.0, 1005: 48.0}
PORE_TILE_MM = 56.0  # the pore tile's size on the skin (the Lee Perry-Smith cheek tile, as tuned on the face)
PORE_STRENGTH, PORE_DISTANCE = 0.35, 0.0002
#: the microrelief - the skin's polygon network of fine furrows, finer than the pores (rec 18; the spec's
#: `micro_normal`, character-data-model.md §3.1): tools/make_microrelief.py's generated tile, its size on the skin and
#: its depth as the part-by-part gate picked them (`docs/gate/2026-11-05/report.md`: HD Aaron's cheek's finest band
#: 0.45, ours 0.23 without it, 0.42 with it at 0.03 mm)
MICRO_TOOL = ".dev/venv-tools/Scripts/python -I tools/make_microrelief.py"
MICRO_TILE_MM = 10.0
MICRO_STRENGTH, MICRO_DISTANCE = 1.0, 0.000035
#: the nails (rec 14, the realism brief §6.14: "a layered nail shader on tile 1005"): each nail's own coordinates
#: (`tools/make_nail_coords.py`: along it 0 at the cuticle to 1 at the free edge, across it -1 to 1, its digit); the
#: plate drawn inside them with a curved cuticle edge and rounded sides (the tile's polygons are coarse), over a bed
#: tinted toward blood's red, a lunula as long as its digit's (the gaps research §3: visible on 96% of thumbs, 48% of
#: little fingers; toes but the big one rarely), a white free edge, faint lengthwise ridges; smoother, shinier and
#: coated; raised a little at its edge
NAIL_TOOL = "python tools/dev.py blender -b --python tools/make_nail_coords.py"
NAIL_TILE_INDEX = 4  # 1005
NAIL_CUTICLE, NAIL_CUTICLE_CURVE = 0.08, 0.35  # where the plate starts: along > cuticle + curve * across^2
NAIL_SIDE, NAIL_EDGE_SOFT = 0.8, 0.06  # |across| inside this; the edges' softness (in along / across)
NAIL_FREE_EDGE = (0.92, 0.97)  # along: the free edge - a thin pale rim on a short nail - fades in over this
NAIL_LUNULA_FINGERS = (0.25, 0.03)  # lunula length = first - second * digit (thumb 0.22 ... little 0.10)
NAIL_LUNULA_TOES = (0.06, 0.0)  # the big toe's, the others' (rarely seen)
NAIL_BED, NAIL_BED_SHARE = (0.50, 0.30, 0.27), 0.25  # linear: mixed into the skin's colour
NAIL_LUNULA, NAIL_LUNULA_SHARE = (0.82, 0.72, 0.68), 0.35
NAIL_TIP = (0.80, 0.75, 0.66)
NAIL_GROOVE = 0.45  # how much the fold's groove round the plate darkens it
NAIL_RIDGES = 0.05  # +- share of the colour
NAIL_ROUGHNESS, NAIL_SPECULAR, NAIL_COAT = 0.18, 0.6, 0.5
NAIL_RAISE = 0.0006  # m: the plate over its fold
SPECULAR_FROM_CAVITY = 0.5  # Blender's standard specular level where the cavity map is 1
#: the body's mottling below the head tile (its maps are plain colour there): a seamless 3D noise in the object's own
#: metres, a few centimetres across, +-MOTTLE/2 of the colour - SkinGen's broad "blotch" layer in kind
MOTTLE, MOTTLE_SCALE, MOTTLE_DETAIL = 0.14, 18.0, 4.0
#: the clear coat (the skin's oily sheen) on the face only: over the whole body it read as oiled plastic (Amara's
#: body, Cycles, 2026-11-04); the body keeps a trace
BODY_COAT_WEIGHT = 0.03
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


def micro_relief() -> bpy.types.Image:
    """The generated microrelief tile (MICRO_TOOL), loaded once and shared by every skin."""
    path = paths.generated("skin", "microrelief.png", tool=MICRO_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def nail_coords() -> bpy.types.Image:
    """Each nail's own coordinates on tile 1005 (NAIL_TOOL), loaded once and shared."""
    path = paths.generated("skin", "nails.png", tool=NAIL_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


def _math(nt, name: str, op: str, a, b=None, c=None):
    """A Math node fed by sockets or numbers; returns its output."""
    node = _node(nt, "ShaderNodeMath", name)
    node.operation = op
    for k, value in enumerate((a, b, c)):
        if value is None:
            continue
        if isinstance(value, (int, float)):
            node.inputs[k].default_value = value
        else:
            nt.links.new(value, node.inputs[k])
    return node.outputs["Value"]


def _clamp01(nt, name: str, value, scale: float):
    """min(max(value * scale, 0), 1): a soft edge `1 / scale` wide."""
    scaled = _math(nt, name, "MULTIPLY", value, scale)
    return _math(nt, name + "_c", "MINIMUM", _math(nt, name + "_p", "MAXIMUM", scaled, 0.0), 1.0)


def _mix(nt, name: str, kind: str, factor, a, b):
    """A Mix node (FLOAT or RGBA) of sockets or constants by `factor`; returns its result."""
    node = _node(nt, "ShaderNodeMix", name)
    node.data_type = kind
    suffix = "Float" if kind == "FLOAT" else "Color"
    if isinstance(factor, (int, float)):
        node.inputs["Factor"].default_value = factor
    else:
        nt.links.new(factor, node.inputs["Factor"])
    for ident, value in (("A_" + suffix, a), ("B_" + suffix, b)):
        socket = next(i for i in node.inputs if i.identifier == ident)
        if isinstance(value, tuple):
            socket.default_value = (*value, 1.0)
        elif isinstance(value, (int, float)):
            socket.default_value = value
        else:
            nt.links.new(value, socket)
    return next(o for o in node.outputs if o.identifier == "Result_" + suffix)


def _nail_layer(nt, bsdf, uv, which) -> None:
    """The nail plate over the skin on tile 1005 (the NAIL_* constants): colour, roughness, specular and coat mixed by
    the plate's mask, its edge raised by a bump at the end of the normal chain."""

    def fed(name):
        return bsdf.inputs[name].links[0].from_socket

    shift = _node(nt, "ShaderNodeVectorMath", "nail_uv", (-1800, -1600))
    shift.operation = "SUBTRACT"
    nt.links.new(uv.outputs["UV"], shift.inputs[0])
    shift.inputs[1].default_value = (float(NAIL_TILE_INDEX), 0.0, 0.0)
    coords = _node(nt, "ShaderNodeTexImage", "nail_coords", (-1600, -1600))
    coords.image, coords.interpolation, coords.extension = nail_coords(), "Linear", "CLIP"
    nt.links.new(shift.outputs["Vector"], coords.inputs["Vector"])
    parts = _node(nt, "ShaderNodeSeparateColor", "nail_parts", (-1350, -1600))
    nt.links.new(coords.outputs["Color"], parts.inputs["Color"])
    along = parts.outputs["Red"]
    digit = _math(nt, "nail_digit", "MULTIPLY", parts.outputs["Blue"], 10.0)
    across = _math(nt, "nail_across", "MULTIPLY_ADD", parts.outputs["Green"], 2.0, -1.0)
    across2 = _math(nt, "nail_across2", "MULTIPLY", across, across)
    on_tile = _math(nt, "nail_on_tile", "COMPARE", which.outputs["Value"], float(NAIL_TILE_INDEX), 0.5)
    inside = _math(nt, "nail_inside", "MULTIPLY", coords.outputs["Alpha"], on_tile)
    # the plate: past the curved cuticle edge, inside the rounded sides
    cut = _math(nt, "nail_cut", "MULTIPLY_ADD", across2, NAIL_CUTICLE_CURVE, NAIL_CUTICLE)
    start = _clamp01(nt, "nail_start", _math(nt, "nail_past_cut", "SUBTRACT", along, cut), 1 / NAIL_EDGE_SOFT)
    sides = _clamp01(nt, "nail_sides", _math(nt, "nail_side_room", "SUBTRACT", NAIL_SIDE,
                                             _math(nt, "nail_abs", "ABSOLUTE", across)), 1 / NAIL_EDGE_SOFT)
    plate = _math(nt, "nail_plate", "MULTIPLY", _math(nt, "nail_plate_a", "MULTIPLY", start, sides), inside)
    # the lunula: a half-moon from the cuticle, as long as its digit's
    toes = _math(nt, "nail_toes", "GREATER_THAN", digit, 5.5)
    finger_len = _math(nt, "nail_len_f", "MULTIPLY_ADD", digit, -NAIL_LUNULA_FINGERS[1], NAIL_LUNULA_FINGERS[0])
    big_toe = _math(nt, "nail_big_toe", "COMPARE", digit, 6.0, 0.5)
    toe_len = _mix(nt, "nail_len_t", "FLOAT", big_toe, NAIL_LUNULA_TOES[1], NAIL_LUNULA_TOES[0])
    length = _mix(nt, "nail_len", "FLOAT", toes, finger_len, toe_len)
    round_ = _math(nt, "nail_round", "SQRT", _math(nt, "nail_round_a", "MAXIMUM",
                                                    _math(nt, "nail_round_b", "SUBTRACT", 1.0, across2), 0.0))
    edge = _math(nt, "nail_lunula_edge", "MULTIPLY_ADD", length, round_, cut)
    lunula = _clamp01(nt, "nail_lunula", _math(nt, "nail_lunula_d", "SUBTRACT", edge, along), 1 / 0.04)
    tip = _clamp01(nt, "nail_tip", _math(nt, "nail_tip_d", "SUBTRACT", along, NAIL_FREE_EDGE[0]),
                   1 / (NAIL_FREE_EDGE[1] - NAIL_FREE_EDGE[0]))
    # faint lengthwise ridges: noise stretched along the nail
    ridge_at = _node(nt, "ShaderNodeCombineXYZ", "nail_ridge_at", (-1100, -1900))
    nt.links.new(_math(nt, "nail_ridge_x", "MULTIPLY", across, 30.0), ridge_at.inputs["X"])
    nt.links.new(_math(nt, "nail_ridge_y", "MULTIPLY", along, 2.0), ridge_at.inputs["Y"])
    ridge = _node(nt, "ShaderNodeTexNoise", "nail_ridges", (-900, -1900))
    ridge.inputs["Scale"].default_value, ridge.inputs["Detail"].default_value = 1.0, 2.0
    nt.links.new(ridge_at.outputs["Vector"], ridge.inputs["Vector"])
    shade = _math(nt, "nail_ridge_shade", "MULTIPLY_ADD", ridge.outputs["Fac"], 2 * NAIL_RIDGES, 1.0 - NAIL_RIDGES)
    skin = fed("Base Color")
    bed = _mix(nt, "nail_bed", "RGBA", NAIL_BED_SHARE, skin, NAIL_BED)
    with_lunula = _mix(nt, "nail_with_lunula", "RGBA",
                       _math(nt, "nail_lunula_share", "MULTIPLY", lunula, NAIL_LUNULA_SHARE), bed, NAIL_LUNULA)
    with_tip = _mix(nt, "nail_with_tip", "RGBA", tip, with_lunula, NAIL_TIP)
    ridged = _node(nt, "ShaderNodeVectorMath", "nail_ridged", (-300, -1600))
    ridged.operation = "SCALE"
    nt.links.new(with_tip, ridged.inputs[0])
    nt.links.new(shade, ridged.inputs["Scale"])
    plated = _mix(nt, "nail_colour", "RGBA", plate, skin, ridged.outputs["Vector"])
    # the fold's groove: a darker band where the plate meets the skin (plate x (1 - plate) peaks at its edge)
    band = _math(nt, "nail_band", "MULTIPLY", plate, _math(nt, "nail_band_a", "SUBTRACT", 1.0, plate))
    groove = _node(nt, "ShaderNodeVectorMath", "nail_groove", (-100, -1600))
    groove.operation = "SCALE"
    nt.links.new(plated, groove.inputs[0])
    nt.links.new(_math(nt, "nail_groove_shade", "MULTIPLY_ADD", band, -4 * NAIL_GROOVE, 1.0), groove.inputs["Scale"])
    nt.links.new(groove.outputs["Vector"], bsdf.inputs["Base Color"])
    for name, value, key in (("Roughness", NAIL_ROUGHNESS, "rough"), ("Specular IOR Level", NAIL_SPECULAR, "spec"),
                             ("Coat Weight", NAIL_COAT, "coat")):
        own = fed(name) if bsdf.inputs[name].is_linked else bsdf.inputs[name].default_value
        nt.links.new(_mix(nt, f"nail_{key}", "FLOAT", plate, own, value), bsdf.inputs[name])
    raise_ = _node(nt, "ShaderNodeBump", "nail_raise", (50, -200))
    raise_.inputs["Strength"].default_value, raise_.inputs["Distance"].default_value = 1.0, NAIL_RAISE
    nt.links.new(plate, raise_.inputs["Height"])
    nt.links.new(fed("Normal"), raise_.inputs["Normal"])
    nt.links.new(raise_.outputs["Normal"], bsdf.inputs["Normal"])


def _tiled_coords(nt, name: str, uv, which, tile_mm: float, location):
    """The UDIM layer's coordinates scaled so a tile of `tile_mm` millimetres keeps its size on every UDIM tile:
    x MM_PER_UV[tile] / tile_mm, the factor picked by the tile's index (`which`: floor(u), 0 = 1001)."""
    first = MM_PER_UV[TILES[0]] / tile_mm
    factor = _node(nt, "ShaderNodeValue", f"{name}_scale_1001", (location[0] - 400, location[1]))
    factor.outputs[0].default_value = first
    socket = factor.outputs[0]
    for k, number in enumerate(TILES[1:], start=1):
        step = MM_PER_UV[number] / tile_mm - MM_PER_UV[TILES[k - 1]] / tile_mm
        past = _node(nt, "ShaderNodeMath", f"{name}_past_{number}", (location[0] - 400, location[1] - 60 * k))
        past.operation, past.inputs[1].default_value = "GREATER_THAN", k - 0.5
        nt.links.new(which.outputs["Value"], past.inputs[0])
        add = _node(nt, "ShaderNodeMath", f"{name}_scale_{number}", (location[0] - 200, location[1] - 60 * k))
        add.operation = "MULTIPLY_ADD"
        nt.links.new(past.outputs["Value"], add.inputs[0])
        add.inputs[1].default_value = step
        nt.links.new(socket, add.inputs[2])
        socket = add.outputs["Value"]
    scaled = _node(nt, "ShaderNodeVectorMath", f"{name}_coords", location)
    scaled.operation = "SCALE"
    nt.links.new(uv.outputs["UV"], scaled.inputs[0])
    nt.links.new(socket, scaled.inputs["Scale"])
    return scaled.outputs["Vector"]


def build_material(mat: bpy.types.Material, images: dict[str, bpy.types.Image], pores: bpy.types.Image) -> None:
    """The skin's maps on its Principled BSDF (material.py made the BSDF and its scattering): `images` by channel,
    UDIM tiled; `pores` a tiling height patch."""
    from . import material

    nt = mat.node_tree
    bsdf = material.principled(mat)  # the film's; material.apply syncs the live view's after (sync_live)
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
    for old in ("body_uv", "pore_mapping"):  # the pores' former route on hm08's UVMap (a skin saved before)
        if nt.nodes.get(NODE + old) is not None:
            nt.nodes.remove(nt.nodes[NODE + old])
    # the relief layers on the UDIM layer, each tile scaled by its own millimetres per unit (MM_PER_UV)
    which = _node(nt, "ShaderNodeMath", "tile_index", (-1200, -700))
    which.operation = "FLOOR"
    links.new(tile.outputs["X"], which.inputs[0])
    pore = _node(nt, "ShaderNodeTexImage", "pores", (-1000, -900))
    pore.image = pores
    pore.image.colorspace_settings.name = "Non-Color"
    links.new(_tiled_coords(nt, "pore", uv, which, PORE_TILE_MM, (-1200, -900)), pore.inputs["Vector"])
    bump = _node(nt, "ShaderNodeBump", "pore_bump", (-250, -200))
    bump.inputs["Strength"].default_value, bump.inputs["Distance"].default_value = PORE_STRENGTH, PORE_DISTANCE
    links.new(pore.outputs["Color"], bump.inputs["Height"])
    links.new(fine.outputs["Normal"], bump.inputs["Normal"])
    micro = _node(nt, "ShaderNodeTexImage", "micro", (-1000, -1200))
    micro.image = micro_relief()
    micro.interpolation = "Cubic"
    links.new(_tiled_coords(nt, "micro", uv, which, MICRO_TILE_MM, (-1200, -1200)), micro.inputs["Vector"])
    micro_bump = _node(nt, "ShaderNodeBump", "micro_bump", (-100, -200))
    micro_bump.inputs["Strength"].default_value = MICRO_STRENGTH
    micro_bump.inputs["Distance"].default_value = MICRO_DISTANCE
    links.new(micro.outputs["Color"], micro_bump.inputs["Height"])
    links.new(bump.outputs["Normal"], micro_bump.inputs["Normal"])
    links.new(micro_bump.outputs["Normal"], bsdf.inputs["Normal"])
    _nail_layer(nt, bsdf, uv, which)
    coat = _node(nt, "ShaderNodeMix", "coat", (-450, 500))
    coat.data_type = "FLOAT"
    links.new(body.outputs["Value"], coat.inputs["Factor"])
    next(i for i in coat.inputs if i.identifier == "A_Float").default_value = COAT_WEIGHT
    next(i for i in coat.inputs if i.identifier == "B_Float").default_value = BODY_COAT_WEIGHT
    links.new(next(o for o in coat.outputs if o.identifier == "Result_Float"), bsdf.inputs["Coat Weight"])
    bsdf.inputs["Coat Roughness"].default_value = COAT_ROUGHNESS
    bsdf.inputs["Coat IOR"].default_value = COAT_IOR
    bsdf.inputs["Sheen Weight"].default_value = SHEEN_WEIGHT
    bsdf.inputs["Sheen Roughness"].default_value = SHEEN_ROUGHNESS
    mat.juststage.has_maps = True


def refresh(mat: bpy.types.Material) -> None:
    """A mapped skin's shading set again from this code (its maps kept): a skin or a character from the library wears
    today's settings, not the ones it was saved with."""
    nodes = mat.node_tree.nodes
    images = {c: nodes[NODE + c].image for c in CHANNELS}
    build_material(mat, images, nodes[NODE + "pores"].image)


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
    refresh(mine)
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
