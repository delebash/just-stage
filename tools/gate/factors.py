# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""One factor at a time on our character at the gate (AGENTS.md: a gap is diagnosed by changing one factor before it
is fixed). Each factor changes the built character, then the gate's own views render with the tag `_f-<factor>`:

    python tools/dev.py blender -b --python tools/gate/factors.py -- --factors relief0,pores0 --views eye,cheek
        [--engine eevee|cycles] [--out DIR]

Factors (the skin's, `modules/skin/maps.py` nodes):
- `relief0`  - the scan's own relief (the skin's normal map) flat: what the scans' mid-scale geometry gives;
- `pores0`   - the pore tile's depth 0;
- `micro0`   - the microrelief's depth 0;
- `colourpores0` - the colour map's detail finer than 1.5 mm blurred out (the pore band of the scan's colour): rec
  17's "colour and relief pores from one source" - how much of the pore band the colour carries, against the relief's
  pores from Ten24's tile;
- `colourflat` - the colour map at its mean over the skin: what the relief alone gives;
- a trial setting `pores*1.15+micro*1.35+relief*2` - each layer's depth scaled everywhere (names keep the `*` and `+`).

`tools/gate/measure.py` then reads every `{engine}_{view}_ours_f-<factor>.png` beside the baseline."""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("parts_gate", HERE / "parts_gate.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

PORE_BAND_MM = 1.5  # the colour's detail finer than this is the pore band (measure.py BANDS_MM)


def _maps():
    return importlib.import_module("bl_ext.system.juststage.modules.skin.maps")


def _skin_trees(built: dict):
    seen = set()
    for slot in built["body"].material_slots:
        mat = slot.material
        if mat and mat.node_tree and mat.name not in seen and _maps().NODE + "gain" in mat.node_tree.nodes:
            seen.add(mat.name)
            yield mat.node_tree


def _depth(built: dict, key: str) -> None:
    for nt in _skin_trees(built):
        nt.nodes[_maps().NODE + f"{key}_depth"].inputs[1].default_value = 0.0


def relief0(built: dict) -> None:
    for nt in _skin_trees(built):
        nt.nodes[_maps().NODE + "normal_map"].inputs["Strength"].default_value = 0.0


def pores0(built: dict) -> None:
    _depth(built, "pore")


def micro0(built: dict) -> None:
    _depth(built, "micro")


def _colour_nodes(built: dict):
    for nt in _skin_trees(built):
        yield nt.nodes[_maps().NODE + "base_color"]


def _first_tile(image) -> np.ndarray:
    """The first UDIM tile (1001, the head) as an array - the only tile `image.pixels` reads (measured 2026-11-07)."""
    w, h = image.size
    px = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(px)
    return px.reshape(h, w, 4)


def _tile_uv(nt, number: int):
    """The skin's UDIM UVs moved so tile `number` reads as 0-1, and a factor that is 1 on that tile only."""
    maps = _maps()
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = maps.UV
    shift = nt.nodes.new("ShaderNodeVectorMath")
    shift.operation = "SUBTRACT"
    shift.inputs[1].default_value = (number - 1001, 0.0, 0.0)
    nt.links.new(uv.outputs["UV"], shift.inputs[0])
    tile = nt.nodes[maps.NODE + "tile_index"].outputs["Value"]
    on = nt.nodes.new("ShaderNodeMath")
    on.operation, on.inputs[1].default_value, on.inputs[2].default_value = "COMPARE", number - 1001, 0.5
    nt.links.new(tile, on.inputs[0])
    return shift.outputs["Vector"], on.outputs["Value"]


def _plain(px: np.ndarray, name: str, colorspace: str):
    """An image from `px` (h x w x 4, the values a source image's `pixels` gave). Colour (sRGB) goes in an 8-bit image:
    Blender reads a float image's values as linear whatever its colour space says, so sRGB values put in one rendered
    the skin washed out (`redmottle`, 2026-11-08 - and the earlier colour factors `colourflat`, `colourpores0` with
    it); data (Non-Color) stays float, used as it is."""
    h, w = px.shape[:2]
    img = bpy.data.images.new(name, w, h, float_buffer=colorspace == "Non-Color")
    img.colorspace_settings.name = colorspace
    img.pixels.foreach_set(px.astype(np.float32).ravel())
    img.pack()
    return img


def _rewrite_colour(built: dict, change) -> None:
    """The head tile's colour changed by `change(rgb, mm_per_px) -> rgb`, shown over that tile only (the face views'
    factors; other tiles keep the skin's own)."""
    maps = _maps()
    for nt in _skin_trees(built):
        node = nt.nodes[maps.NODE + "base_color"]
        px = _first_tile(node.image)
        px[..., :3] = change(px[..., :3], maps.MM_PER_UV.get(1001, 724.0) / px.shape[0])
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = _plain(px, "factor_colour_1001", node.image.colorspace_settings.name)
        vec, on = _tile_uv(nt, 1001)
        nt.links.new(vec, tex.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(on, mix.inputs["Factor"])
        for link in list(node.outputs["Color"].links):
            nt.links.new(mix.outputs["Result"], link.to_socket)
        nt.links.new(node.outputs["Color"], mix.inputs["A"])
        nt.links.new(tex.outputs["Color"], mix.inputs["B"])
        print("COLOUR REWRITTEN on the head tile", flush=True)


def colourpores0(built: dict) -> None:
    def blur(rgb, mm_per_px):  # numpy only: Blender's Python has no scipy
        sigma = PORE_BAND_MM / mm_per_px / 2.0
        return np.stack([pg._blur(rgb[..., c], sigma) for c in range(3)], -1)

    _rewrite_colour(built, blur)


def colourflat(built: dict) -> None:
    def flat(rgb, _mm):
        skin = rgb.sum(-1) > 0.02
        mean = rgb[skin].mean(0) if skin.any() else rgb.reshape(-1, 3).mean(0)
        return np.where(skin[..., None], mean, rgb)

    _rewrite_colour(built, flat)


def redmottle(built: dict, k: float) -> None:
    """The colour's red variation at 0.5-5 mm scaled by `k` on the head tile: redness (red less the mean of green and
    blue) band-passed between 0.5 and 5 mm, (k - 1) of it added to the red channel. Measured on the gate's cheek
    patches (2026-11-07 late): ours matches his brightness detail at every scale but varies in red 18% less at
    0.5-2 mm and 29% less at 2-5 mm (his blotches and fine veins) - where the cheek's excess sits."""
    def change(rgb, mm_per_px):
        red = rgb[..., 0] - 0.5 * (rgb[..., 1] + rgb[..., 2])
        band = _fft_blur(red, 0.5 / mm_per_px / 2.0) - _fft_blur(red, 5.0 / mm_per_px / 2.0)
        out = rgb.copy()
        out[..., 0] = np.clip(rgb[..., 0] + (k - 1.0) * band, 0.0, 1.0)
        return out

    _rewrite_colour(built, change)


def handspart(built: dict, strength: float = 1.0, colour: bool = False) -> None:
    """A body part's donor relief (`tools/body_scan.py texture`: `body_1003_hands_*`) over the skin's own on the arm
    tile, by its weight, in the shader - nothing rebuilt before the part is measured. `strength` scales its tilt;
    `colour` multiplies in its colour detail by the same weight."""
    maps = _maps()
    folder = Path(maps.paths.GENERATED) / "skin"

    def tex(nt, name, vec):
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images.load(str(folder / name), check_existing=True)
        node.image.colorspace_settings.name = "Non-Color"
        node.extension = "CLIP"
        nt.links.new(vec, node.inputs["Vector"])
        return node.outputs["Color"]

    for nt in _skin_trees(built):
        vec, on = _tile_uv(nt, 1003)
        weight = nt.nodes.new("ShaderNodeMath")
        weight.operation = "MULTIPLY"
        nt.links.new(nt.nodes.new("ShaderNodeSeparateColor").outputs[0], weight.inputs[0])
        sep = weight.inputs[0].links[0].from_node
        nt.links.new(tex(nt, "body_1003_hands_weight.png", vec), sep.inputs["Color"])
        nt.links.new(on, weight.inputs[1])
        scaled = nt.nodes.new("ShaderNodeVectorMath")  # (part - 0.5) * strength + 0.5
        scaled.operation = "MULTIPLY_ADD"
        nt.links.new(tex(nt, "body_1003_hands_relief.png", vec), scaled.inputs[0])
        scaled.inputs[1].default_value = (strength, strength, 1.0)
        scaled.inputs[2].default_value = (0.5 - 0.5 * strength, 0.5 - 0.5 * strength, 0.0)
        normal = nt.nodes[maps.NODE + "normal"]
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(weight.outputs["Value"], mix.inputs["Factor"])
        for link in list(normal.outputs["Color"].links):
            nt.links.new(mix.outputs["Result"], link.to_socket)
        nt.links.new(normal.outputs["Color"], mix.inputs["A"])
        nt.links.new(scaled.outputs["Vector"], mix.inputs["B"])
        if colour:  # x (1 - w + ratio * w), the ratio stored halved
            base = nt.nodes[maps.NODE + "base_color"]
            ratio = nt.nodes.new("ShaderNodeVectorMath")
            ratio.operation = "MULTIPLY"
            nt.links.new(tex(nt, "body_1003_hands_colour.png", vec), ratio.inputs[0])
            ratio.inputs[1].default_value = (2.0, 2.0, 2.0)
            gain = nt.nodes.new("ShaderNodeMix")
            gain.data_type = "RGBA"
            nt.links.new(weight.outputs["Value"], gain.inputs["Factor"])
            gain.inputs["A"].default_value = (1.0, 1.0, 1.0, 1.0)
            nt.links.new(ratio.outputs["Vector"], gain.inputs["B"])
            times = nt.nodes.new("ShaderNodeVectorMath")
            times.operation = "MULTIPLY"
            for link in list(base.outputs["Color"].links):
                nt.links.new(times.outputs["Vector"], link.to_socket)
            nt.links.new(base.outputs["Color"], times.inputs[0])
            nt.links.new(gain.outputs["Result"], times.inputs[1])
        print("HANDS PART in the shader, strength", strength, "colour", colour, flush=True)


def _margin_value(built: dict, key: str, value) -> None:
    for nt in _skin_trees(built):
        node = nt.nodes[_maps().NODE + f"margin_{key}"]
        sock = next(i for i in node.inputs if i.identifier == ("B_Color" if node.data_type == "RGBA" else "B_Float"))
        sock.default_value = value


def margindry(built: dict) -> None:
    """The lid margin's wet shine off: its roughness and coat the skin's own (0.5, 0.12) - the eye proof's first
    factor for the swollen glossy lower rim (plan §19.1 item 6)."""
    _margin_value(built, "rough", 0.5)
    _margin_value(built, "coat", 0.12)


def margintint0(built: dict) -> None:
    """The lid margin's pink tint off (the skin's colour there)."""
    _margin_value(built, "tint", (1.0, 1.0, 1.0, 1.0))


def _hide_part(built: dict, part: str) -> None:
    n = 0
    for obj in bpy.data.objects:
        if obj.juststage.part == part:
            obj.hide_render = True
            n += 1
    print("HIDDEN", part, n, flush=True)


def nohair(built: dict) -> None:
    """The scalp hair hidden: what the scalp's own skin shows under it."""
    _hide_part(built, "scalp")


def tear0(built: dict) -> None:
    """The tearline (ICT's ring, the wet film along the lid margins) hidden."""
    _hide_part(built, "eyeEdge")


def occl0(built: dict) -> None:
    """The occlusion film (ICT's strip, the lids' shadow on the white) hidden."""
    _hide_part(built, "eyeshell")


FACTORS = {f.__name__: f for f in (relief0, pores0, micro0, colourpores0, colourflat, handspart, margindry,
                                   margintint0, tear0, occl0, nohair)}


#: the shine trials: a key -> the Principled input it scales on both of the skin's BSDFs (the film's and the live view's)
SHINE = {"rough": "Roughness", "spec": "Specular IOR Level", "coat": "Coat Weight", "coatrough": "Coat Roughness",
         "sss": "Subsurface Scale"}  # sss: how far the light scatters (HD Aaron's radius is wider than ours)


def _scale_input(nt, socket: str, k: float) -> None:
    """`socket` on every Principled BSDF of the tree times `k`: a linked one through a multiply node, clamped to 0-1."""
    for bsdf in [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]:
        s = bsdf.inputs[socket]
        if not s.is_linked:
            s.default_value = s.default_value * k if socket == "Subsurface Scale" else min(s.default_value * k, 1.0)
            continue
        times = nt.nodes.new("ShaderNodeMath")
        times.operation, times.use_clamp = "MULTIPLY", True
        nt.links.new(s.links[0].from_socket, times.inputs[0])
        times.inputs[1].default_value = k
        nt.links.new(times.outputs[0], s)


def roughvar(built: dict, k: float) -> None:
    """The skin's roughness varied by its own relief: x (1 - k (h - 0.5)) with h the pore and microrelief heights' sum
    about 0.5 - rougher in the cavities, as CC5's cavity map does (HD Aaron's roughness varies 0.62-0.70 over the cheek,
    ours is flat in a region, 0.474-0.479; the plan's §10 "cavity into roughness in pores", TO BUILD)."""
    maps = _maps()
    for nt in _skin_trees(built):
        h = nt.nodes.new("ShaderNodeMath")
        h.operation = "ADD"
        nt.links.new(nt.nodes[maps.NODE + "pores_blend"].outputs[0], h.inputs[0])
        nt.links.new(nt.nodes[maps.NODE + "micro_blend"].outputs[0], h.inputs[1])
        gain = nt.nodes.new("ShaderNodeMath")  # 1 - k (h - 1) = (1 + k) - k h
        gain.operation = "MULTIPLY_ADD"
        nt.links.new(h.outputs[0], gain.inputs[0])
        gain.inputs[1].default_value, gain.inputs[2].default_value = -k, 1.0 + k
        for bsdf in [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]:
            s = bsdf.inputs["Roughness"]
            times = nt.nodes.new("ShaderNodeMath")
            times.operation, times.use_clamp = "MULTIPLY", True
            if s.is_linked:
                nt.links.new(s.links[0].from_socket, times.inputs[0])
            else:
                times.inputs[0].default_value = s.default_value
            nt.links.new(gain.outputs[0], times.inputs[1])
            nt.links.new(times.outputs[0], s)
    print("ROUGHNESS VARIED by the relief, k", k, flush=True)


def scaled(spec: str):
    """A trial setting: `pores*1.15`, `micro*1.35`, `relief*2` (the scan relief's normal-map strength), `rough*0.75`,
    `spec*1.5`, `coat*3`, `coatrough*0.5`, `sss*2` (`SHINE`), `roughvar*0.3` (`roughvar`), `poresize*1.25` (the pore
    tile k times as big on the skin: its tiling scale, `maps._tiled_coords`' `pore_scale_*` values, / k), joined by
    `+` - each changed everywhere on the skin, to see a change before it is made."""
    def prepare(built: dict) -> None:
        for part in spec.split("+"):
            key, factor = part.split("*")
            if key == "roughvar":  # adds nodes once per tree
                roughvar(built, float(factor))
                continue
            for nt in _skin_trees(built):
                if key in ("pores", "micro"):
                    node = nt.nodes[_maps().NODE + f"{key.rstrip('s')}_depth"]
                    node.inputs[1].default_value *= float(factor)
                elif key == "poresize":  # the first tile's scale and every later tile's step, all / k
                    for node in nt.nodes:
                        if node.name == _maps().NODE + "pore_scale_1001":
                            node.outputs[0].default_value /= float(factor)
                        elif node.name.startswith(_maps().NODE + "pore_scale_"):
                            node.inputs[1].default_value /= float(factor)
                elif key == "relief":
                    nt.nodes[_maps().NODE + "normal_map"].inputs["Strength"].default_value *= float(factor)
                elif key in SHINE:
                    _scale_input(nt, SHINE[key], float(factor))
                else:
                    raise KeyError(key)
    return prepare


def _fft_blur(a: np.ndarray, sigma: float) -> np.ndarray:
    """A Gaussian blur by FFT (numpy only - Blender's Python has no scipy), wrapping at the edges."""
    h, w = a.shape
    fy, fx = np.fft.fftfreq(h)[:, None], np.fft.fftfreq(w)[None, :]
    return np.real(np.fft.ifft2(np.fft.fft2(a) * np.exp(-2 * (np.pi * sigma) ** 2 * (fx**2 + fy**2))))


def reliefband(built: dict, k: float, below_mm: float = 7.0) -> None:
    """The scans' own relief on the head tile with its detail finer than `below_mm` scaled by `k` (its form kept):
    the cheek's folds below HD Aaron's while x2 on the whole relief pushed the form past his (2026-11-07)."""
    maps = _maps()
    for nt in _skin_trees(built):
        node = nt.nodes[maps.NODE + "normal"]
        px = _first_tile(node.image)
        sigma = below_mm * px.shape[0] / maps.MM_PER_UV[1001] / 2.0
        xy = px[..., :2] * 2 - 1
        for c in range(2):
            xy[..., c] = xy[..., c] + (k - 1) * (xy[..., c] - _fft_blur(xy[..., c], sigma))
        z = np.sqrt(np.clip(1 - (xy**2).sum(-1), 0, 1))
        px[..., :3] = np.dstack([xy * 0.5 + 0.5, z])
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = _plain(px, "factor_normal_1001", "Non-Color")
        vec, on = _tile_uv(nt, 1001)
        nt.links.new(vec, tex.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(on, mix.inputs["Factor"])
        for link in list(node.outputs["Color"].links):
            nt.links.new(mix.outputs["Result"], link.to_socket)
        nt.links.new(node.outputs["Color"], mix.inputs["A"])
        nt.links.new(tex.outputs["Color"], mix.inputs["B"])
        print("RELIEF BAND x", k, "below", below_mm, "mm on the head tile", flush=True)


def _hair_trees():
    for mat in bpy.data.materials:  # not the gate's kept originals (fake users: `parts_gate.render` variants)
        if mat.node_tree and not mat.use_fake_user and mat.node_tree.nodes.get("js_hair.world_mean") is not None:
            yield mat.node_tree


def hairambient(built: dict, k: float) -> None:
    """The live-view hair model's image-light ambient (`hair_shading.AMBIENT` x the world's mean) scaled by `k`."""
    for nt in _hair_trees():
        nt.nodes["js_hair.world_mean"].outputs[0].default_value *= k
    print("HAIR AMBIENT x", k, flush=True)


def hairthrough(built: dict, share: float) -> None:
    """The share of the light the hair's body gets in its own shadow (`hair_shading.BODY_LIGHT_THROUGH`) set to
    `share`: the soft shadow's ADD (share) and SCALE (1 - share) nodes."""
    n = 0
    for nt in _hair_trees():
        for node in nt.nodes:
            if node.type == "VECT_MATH" and node.operation == "ADD" and node.inputs[0].is_linked:
                src = node.inputs[0].links[0].from_node
                if src.type == "VECT_MATH" and src.operation == "SCALE" and not node.inputs[1].is_linked:
                    if abs(src.inputs["Scale"].default_value + node.inputs[1].default_value[0] - 1.0) < 1e-4:
                        node.inputs[1].default_value = (share,) * 3
                        src.inputs["Scale"].default_value = 1.0 - share
                        n += 1
    print("HAIR LIGHT THROUGH", share, "on", n, "nodes", flush=True)


def hairdensity(built: dict, per_m2: float) -> None:
    """The scalp fill's density (`scalp.DENSITY`, 1.3M strands a m2 - 130 a cm2 - against the real ~223, Barman 1965;
    the plan's §14 "Density: TO SET") set on the fill group's Interpolate Hair Curves - our hair's mean L* stays above
    HD Aaron's whatever the shading (the scalp showing through, the guess)."""
    group = bpy.data.node_groups.get("JustStage scalp fill")
    node = next(n for n in group.nodes if n.type == "GROUP" and n.node_tree and n.node_tree.name.startswith("Interpolate"))
    node.inputs["Density"].default_value = per_m2
    for obj in bpy.data.objects:
        if obj.type == "CURVES":
            obj.data.update_tag()
    bpy.context.view_layer.update()
    print("HAIR DENSITY", per_m2, flush=True)


def hairclump(built: dict, factor: float) -> None:
    """The scalp shape group's Clump Hair Curves factor set (a node group - run --alone): whether the clumps' partings
    are the hair's fixed bare lines (not the mask, the comb, island parting, highlights or light-through, 2026-11-07)."""
    group = bpy.data.node_groups.get("JustStage scalp shape")
    node = next(n for n in group.nodes if n.type == "GROUP" and n.node_tree and n.node_tree.name.startswith("Clump"))
    node.inputs["Factor"].default_value = factor
    for obj in bpy.data.objects:
        if obj.type == "CURVES":
            obj.data.update_tag()
    bpy.context.view_layer.update()
    print("HAIR CLUMP", factor, flush=True)


def hairgrey(built: dict, share: float) -> None:
    """The scalp grooms' share of near-unpigmented strands (`scalp.GREY_SHARE`) set inside the strand colour group: its
    random pick's Probability unhooked from the group's "Grey Share" input and set (Blender 5.3 refuses a modifier's
    input set as an ID property) - HD Aaron's highlights (p95 60 at the back) come from light strands among dark."""
    group = bpy.data.node_groups.get("JustStage strand colour")
    pick = next(n for n in group.nodes if n.type == "RANDOM_VALUE" and n.data_type == "BOOLEAN")
    socket = pick.inputs["Probability"]
    for link in list(socket.links):
        group.links.remove(link)
    socket.default_value = share
    for obj in bpy.data.objects:
        if obj.type == "CURVES":
            obj.data.update_tag()
    bpy.context.view_layer.update()
    print("HAIR GREY", share, flush=True)


def hairmelanin(built: dict, melanin: float) -> None:
    """Every scalp groom's own colour set to `melanin` (its `melanin` curve attribute; the strands take their guides')
    - darker roots for HD Aaron's L* 20 at the back (ours 25)."""
    n = 0
    for obj in bpy.data.objects:
        if obj.type == "CURVES" and obj.juststage.part == "scalp" and "melanin" in obj.data.attributes:
            attr = obj.data.attributes["melanin"]
            attr.data.foreach_set("value", np.full(len(attr.data), melanin, np.float32))
            obj.data.update_tag()
            n += 1
    print("HAIR MELANIN", melanin, "on", n, "grooms", flush=True)


def hairtip(built: dict, k: float) -> None:
    """Each strand lighter toward its tip: its melanin x (1 - k t²), t the Hair Info's Intercept (0 at the root, 1 at
    the tip) - the plan's carried "root-to-tip by Intercept" (RR rec 7); HD Aaron's hair is dark at the roots (back
    L* 20) with light tips (highlights p95 60), ours even (25 / 43), and the hair model's shares only trade the two."""
    n = 0
    for nt in _hair_trees():
        attr = next((x for x in nt.nodes if x.type == "ATTRIBUTE" and x.attribute_name == "melanin"), None)
        if attr is None:
            continue
        info = nt.nodes.new("ShaderNodeHairInfo")
        sq = nt.nodes.new("ShaderNodeMath")
        sq.operation = "POWER"
        nt.links.new(info.outputs["Intercept"], sq.inputs[0])
        sq.inputs[1].default_value = 2.0
        gain = nt.nodes.new("ShaderNodeMath")  # 1 - k t²
        gain.operation = "MULTIPLY_ADD"
        nt.links.new(sq.outputs[0], gain.inputs[0])
        gain.inputs[1].default_value, gain.inputs[2].default_value = -k, 1.0
        times = nt.nodes.new("ShaderNodeMath")
        times.operation = "MULTIPLY"
        for link in list(attr.outputs["Fac"].links):
            nt.links.new(times.outputs[0], link.to_socket)
        nt.links.new(attr.outputs["Fac"], times.inputs[0])
        nt.links.new(gain.outputs[0], times.inputs[1])
        n += 1
    print("HAIR TIPS lighter, k", k, "on", n, "materials", flush=True)


def hairmodel(built: dict, diffuse: float, glossy: float, ambient: float) -> None:
    """The live-view hair model's shares set (`hair_shading.DIFFUSE`, `GLOSSY`, `AMBIENT`) and every groom's material
    built again with them (`groom.hair_material`) - calibrating against Cycles on more than one view."""
    hs = importlib.import_module("bl_ext.system.juststage.modules.hair.hair_shading")
    groom = importlib.import_module("bl_ext.system.juststage.modules.hair.groom")
    hs.DIFFUSE, hs.GLOSSY, hs.AMBIENT = diffuse, glossy, ambient
    remade = {}
    for obj in bpy.data.objects:
        if obj.type != "CURVES":
            continue
        for slot in obj.material_slots:
            mat = slot.material
            if mat and mat.node_tree and mat.node_tree.nodes.get("js_hair.world_mean") is not None:
                if mat.name not in remade:
                    remade[mat.name] = groom.hair_material(mat.name + " f")
                slot.material = remade[mat.name]
    print("HAIR MODEL diffuse", diffuse, "glossy", glossy, "ambient", ambient, "on", len(remade), "materials", flush=True)


MICRO_TRIALS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "micro"


def microtile(built: dict, stem: str) -> None:
    """The microrelief tile swapped for a candidate (`.dev/gate/micro/<stem>.png`, the same 10 mm size) on every skin's
    microrelief image nodes - the face skin's pattern against HD Aaron's micro normal (plan §0, 2026-11-07)."""
    image = bpy.data.images.load(str(MICRO_TRIALS / f"{stem}.png"), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    n = 0
    for nt in _skin_trees(built):
        for node in nt.nodes:
            if node.type == "TEX_IMAGE" and node.image and node.image.name.startswith("microrelief"):
                node.image = image
                n += 1
    if not n:
        raise RuntimeError("no microrelief image node found on the skin")
    print("MICRO TILE", stem, "on", n, "nodes", flush=True)


PORE_TRIALS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "pores"


def poretile(built: dict, stem: str) -> None:
    """The pore tile swapped for a candidate (`.dev/gate/pores/<stem>.png` with its `.json` size in mm) on every skin,
    its tiling scale set to the candidate's own size (`pore_scale_*` x old / new mm): the pores' pattern alone changed
    - the cheek's excess sits at the pores' scale and their size and depth are already at their best (2026-11-07
    late). `aaron_cheek`: HD Aaron's own head normals on the upper cheek, a LOCAL TEST of whether his pattern closes
    the gap."""
    maps = _maps()
    image = bpy.data.images.load(str(PORE_TRIALS / f"{stem}.png"), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    new_mm = float(json.loads((PORE_TRIALS / f"{stem}.json").read_text(encoding="utf-8"))["size_mm"])
    _, old_mm = maps.pore_relief()
    n = 0
    for nt in _skin_trees(built):
        for node in nt.nodes:
            if node.type == "TEX_IMAGE" and node.image and node.image.name.startswith("pores"):
                node.image = image
                n += 1
            elif node.name == maps.NODE + "pore_scale_1001":
                node.outputs[0].default_value *= old_mm / new_mm
            elif node.name.startswith(maps.NODE + "pore_scale_"):
                node.inputs[1].default_value *= old_mm / new_mm
    if not n:
        raise RuntimeError("no pore image node found on the skin")
    print("PORE TILE", stem, f"{new_mm:.1f} mm (was {old_mm:.1f}) on", n, "nodes", flush=True)


#: the eye-open sliders (body_create.EYE_OPEN) one at a time - the lower lid's thick roll at the eye view; shape keys,
#: so these run alone (`--alone`: a build each - the trials' material reset doesn't undo a shape)
EYE_SLIDERS = {"eyebag": "bag-decr-incr", "eyeheight2": "height2-decr-incr", "eyefold": "eyefold-concave-convex",
               "eyefoldup": "eyefold-down-up", "eyeheight1": "height1-decr-incr",
               "eyetrans": "trans-down-up"}  # eyetrans*-1: the eye 2.9 mm down (with browup*1's 7.1 mm: his brow height)


def lashcap(built: dict, mm: float) -> None:
    """The lid margin narrower: the lash line's most off the eyeball (base v2's 2.6 mm, `parts.eyelid_contact`) capped
    at `mm`, the contact made again - the lower lid's thick roll (plan §19.1 item 6: the margin's width against the
    real ~2 mm and HD Aaron's 1.0-2.3 mm ledge; the films, shine and eye sliders didn't move it, 2026-11-07). A shape:
    run with --alone."""
    base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    original = base.record  # it reads its file on every call: the call patched, not its result

    def capped() -> dict:
        rec = original()
        rec["radii_mm"]["lash"] = mm
        return rec

    base.record = capped
    try:
        rows = parts.eyelid_contact(built["body"])
    finally:
        base.record = original
    bpy.context.view_layer.update()
    print("LASH CAP", mm, "mm on", rows, "rows", flush=True)


def lidcarry(built: dict, *shares: float) -> None:
    """The lid contact's carry (`parts.CARRY`, 0.6 / 0.25: each lash-line move carried into the next two rings of lid
    skin) set to `shares` (one a ring), the contact made again - the lash line pulled in while the skin past the second
    ring stays out leaves a step: the lower lid's roll. A shape: --alone."""
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    kept = parts.CARRY
    parts.CARRY = tuple(shares)
    try:
        rows = parts.eyelid_contact(built["body"])
    finally:
        parts.CARRY = kept
    bpy.context.view_layer.update()
    print("LID CARRY", shares, "on", rows, "rows", flush=True)


def lidsmooth(built: dict, rings: int, iterations: int) -> None:
    """The lower lid's skin past its lash line relaxed (Laplacian smoothing, the lash line and the outermost ring held):
    `rings` rings of lid skin below the lower lash line, `iterations` passes, on the shaped character (every key
    mixed), the change added to the contact key (base.CONTACT) - the lower lid's thick roll is its skin bulging between
    the lash line the contact pulls onto the eyeball and the skin beyond that the eye-open sliders pushed out (no film,
    shine, slider, margin width or carry setting removed it, 2026-11-07). A shape: --alone."""
    base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    body = built["body"]
    me = body.data
    shaped = build.shaped_coords(body)
    rows = base.rows()
    edges = np.empty(len(me.edges) * 2, np.int64)
    me.edges.foreach_get("vertices", edges)
    edges = edges.reshape(-1, 2)
    nbr: dict[int, set[int]] = {}
    for a, b in edges:
        nbr.setdefault(int(a), set()).add(int(b))
        nbr.setdefault(int(b), set()).add(int(a))
    lash = rows[:, 0][rows[:, 0] >= 0]
    lid = set(int(v) for v in rows[rows >= 0])
    lower = [int(v) for v in lash if shaped[v, 2] < np.median(shaped[lash, 2])]  # the lash line's lower half
    top = shaped[lower, 2].max() + 0.001
    ring_sets, seen, frontier = [], set(lid), set(lower)
    for _ in range(rings + 1):
        nxt = {u for v in frontier for u in nbr[v]} - seen
        nxt = {u for u in nxt if shaped[u, 2] < top}  # the lid's skin below the lash line, not the eye's opening
        ring_sets.append(nxt)
        seen |= nxt
        frontier = nxt
    free = sorted(set().union(*ring_sets[:-1]))  # the last ring held
    co = shaped.copy()
    for _ in range(iterations):
        new = co.copy()
        for v in free:
            new[v] = co[list(nbr[v])].mean(0)
        co = new
    delta = (co - shaped).astype(np.float32)
    key = me.shape_keys.key_blocks[base.CONTACT]
    kco = np.empty(len(me.vertices) * 3, np.float32)
    key.data.foreach_get("co", kco)
    key.data.foreach_set("co", (kco.reshape(-1, 3) + delta / max(key.value, 1e-6)).ravel())
    me.update()
    bpy.context.view_layer.update()
    moved = np.linalg.norm(delta, axis=1)
    print("LID SMOOTH", rings, "rings,", iterations, "passes,", len(free), "vertices, most moved",
          round(float(moved.max()) * 1000, 2), "mm", flush=True)


def blinkfix(built: dict) -> None:
    """The blink's deciding test (checklist row 10): can our lids close cleanly? Known broken: a 2 mm gap and a
    0.7-1.1 mm clip into the eyeball (plan §7 "Per-character"). The plan's named method (OmniFaceRig's: "upper-eyelid
    vertices snapped to lower lid and locally relaxed"): in each eyeBlink key every upper row (lash line, margin, rim)
    closes onto the lower row of its kind at the same angle round the eye; the move carried into four rings of upper
    lid skin (0.7, 0.45, 0.25, 0.1); any lid point left inside the eyeball pushed out to 0.3 mm off it. Prints the gap
    and the clip before and after. A shape: --alone."""
    base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
    body = built["body"]
    me = body.data
    n = len(me.vertices)
    blocks = me.shape_keys.key_blocks
    shaped = build.shaped_coords(body)
    basis = np.empty(n * 3, np.float32)
    blocks[0].data.foreach_get("co", basis)
    basis = basis.reshape(-1, 3).astype(np.float64)
    mw = np.array(body.matrix_world)
    inv = np.linalg.inv(mw)
    spheres = {name: eye_layers._eye_sphere(o) for name, o in parts.parts_of(body).items() if name in ("eyeLeft", "eyeRight")}
    rows = base.rows()
    rows = rows[(rows >= 0).all(1)]
    edges = np.empty(len(me.edges) * 2, np.int64)
    me.edges.foreach_get("vertices", edges)
    edges = edges.reshape(-1, 2)
    nbr: dict[int, set[int]] = {}
    for a, b in edges:
        nbr.setdefault(int(a), set()).add(int(b))
        nbr.setdefault(int(b), set()).add(int(a))

    def to_local(p):
        return p @ inv[:3, :3].T + inv[:3, 3]

    for key_name, eye_name in (("eyeBlinkLeft", "eyeLeft"), ("eyeBlinkRight", "eyeRight")):
        key = blocks[key_name]
        kco = np.empty(n * 3, np.float32)
        key.data.foreach_get("co", kco)
        kco = kco.reshape(-1, 3).astype(np.float64)
        closed = shaped + (kco - basis)  # the closed lid on the current shape (local)
        c_w, r = spheres[eye_name]
        c = to_local(c_w)
        mine = rows[np.linalg.norm(shaped[rows[:, 2]] - c, axis=1) < 0.025]
        up, lo = mine[shaped[mine[:, 2], 2] > c[2]], mine[shaped[mine[:, 2], 2] <= c[2]]
        if len(up) < 3 or len(lo) < 3:
            continue

        def az(p):
            return np.arctan2(p[:, 0] - c[0], -(p[:, 1] - c[1]))

        def gap_and_clip(state):
            mid_up = up[np.argsort(np.abs(az(shaped[up[:, 0]])))[:3], 0]
            mid_lo = lo[np.argsort(np.abs(az(shaped[lo[:, 0]])))[:3], 0]
            gap = float(np.linalg.norm(state[mid_up].mean(0) - state[mid_lo].mean(0)))
            lid_v = np.array(sorted({int(v) for v in up.ravel()}))
            clip = float(max(0.0, (r - np.linalg.norm(state[lid_v] - c, axis=1)).max()))
            return gap * 1000, clip * 1000

        before = gap_and_clip(closed)
        adj = np.zeros_like(closed)
        order = np.argsort(az(shaped[lo[:, 2]]))
        lo_az = az(shaped[lo[order, 2]])
        for col in range(3):  # lash line, margin, rim: each upper row onto the lower row of its kind
            tgt = closed[lo[order, col]]
            for v, a in zip(up[:, col], az(shaped[up[:, col]]), strict=True):
                p = np.array([np.interp(a, lo_az, tgt[:, k]) for k in range(3)])
                adj[v] = p - closed[v]
        taken = set(int(v) for v in mine.ravel())
        ring_of_lash = {int(v): adj[v] for v in up[:, 0]}
        frontier, seen = set(ring_of_lash), set(taken)
        for share in (0.7, 0.45, 0.25, 0.1):  # the upper lid's skin follows its lash line
            nxt = {u for v in frontier for u in nbr[v]} - seen
            nxt = {u for u in nxt if shaped[u, 2] > c[2]}
            for u in nxt:
                src = [v for v in nbr[u] if v in frontier]
                adj[u] = share / max(len(src), 1) * sum(adj[v] for v in src) if src else 0.0
            seen |= nxt
            frontier = nxt
        fixed = closed + adj
        lid_v = np.array(sorted(seen | taken))
        dist = np.linalg.norm(fixed[lid_v] - c, axis=1)
        inside = dist < r + 0.0003
        fixed[lid_v[inside]] = c + (fixed[lid_v[inside]] - c) / dist[inside, None] * (r + 0.0003)
        after = gap_and_clip(fixed)
        key.data.foreach_set("co", (basis + (fixed - shaped)).astype(np.float32).ravel())
        print("BLINK FIX", key_name, f"gap {before[0]:.2f} -> {after[0]:.2f} mm, clip {before[1]:.2f} -> {after[1]:.2f} mm",
              flush=True)
    me.update()
    bpy.context.view_layer.update()


def rigsmooth(built: dict, iterations: int) -> None:
    """Checklist row 17's corrective, tried: the gate's body rig (`body_rig.build`, as the posed views build it) with
    Blender's Corrective Smooth modifier after the Armature (delta mush - the standard cheap joint corrective; the
    plan's own is body.dna's RBF, Q-RIG-7), bound at rest; `iterations` 0 leaves the plain rig (the factor's control).
    The posed views (`pose_*`) then render through it. A new rig: --alone."""
    spec = importlib.util.spec_from_file_location("body_rig", HERE / "body_rig.py")
    body_rig = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(body_rig)
    body = built["body"]
    arm = body_rig.build(body)
    built["rig"], built["rig_start"] = arm, {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}
    if iterations:
        mod = body.modifiers.new("Corrective Smooth", "CORRECTIVE_SMOOTH")
        body.modifiers.move(len(body.modifiers) - 1, 1)  # right after the Armature
        mod.iterations, mod.factor, mod.smooth_type, mod.rest_source = iterations, 0.5, "LENGTH_WEIGHTED", "BIND"
        mod.use_pin_boundary = True
        with bpy.context.temp_override(object=body, active_object=body):
            bpy.ops.object.correctivesmooth_bind(modifier=mod.name)
        bpy.context.view_layer.update()
        print("RIG SMOOTH", iterations, "iterations, bound:", mod.is_bind, flush=True)
    else:
        print("RIG SMOOTH 0: the plain rig", flush=True)


def teethcolour(built: dict, r: float, g: float, b: float) -> None:
    """Item 5's teeth (row 4: ours read too white beside HD Aaron's ivory; his enamel's texture median, linear, upper
    (0.43, 0.35, 0.30), lower (0.60, 0.48, 0.42) against our base (0.80, 0.75, 0.65)): our enamel's base colour set to
    (r, g, b) linear, the gum-line-to-edge ramp (part_materials.TOOTH_RATIOS) kept in proportion."""
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    pm = importlib.import_module("bl_ext.system.juststage.modules.head.part_materials")
    teeth = parts.parts_of(built["body"])["teeth"]
    old = pm.REGIONS["teeth"][0]
    scale = (r / old[0], g / old[1], b / old[2])
    done = 0
    for slot in teeth.material_slots:
        mat = slot.material
        if not mat or not mat.name.startswith("JustStage Teeth"):
            continue
        for node in mat.node_tree.nodes:
            if node.type == "VALTORGB":
                for el in node.color_ramp.elements:
                    el.color = (*(c * s for c, s in zip(el.color[:3], scale, strict=True)), 1.0)
                done += 1
    print("TEETH COLOUR", (r, g, b), "on", done, "ramps", flush=True)


def eyescale(built: dict, k: float, pivot: str = "centre") -> None:
    """Build queue item 5 (row 5: our eyeball 14.5-14.8 mm in radius on three characters, HD Aaron's 13.2 - his at his
    own size in our sockets read as his eye): both eye parts scaled by `k` about their own centres - or, `pivot`
    "front", about the cornea's front (the eye's most forward vertex), as `aaroneyes*own` set his eyeball: scaled
    about the centre, the lids followed the eyeball in and the opening shrank (2026-11-08) - then refit's eye steps
    again: the clearance, the lids' contact (the rims back onto the smaller eyeball), the eye films, and the blink's
    closing step. A shape: --alone."""
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
    base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
    blink_contact = importlib.import_module("bl_ext.system.juststage.modules.head.blink_contact")
    body = built["body"]
    eyes = parts.parts_of(body)
    before = {}
    for name in ("eyeLeft", "eyeRight"):
        obj = eyes[name]
        centre, radius = eye_layers._eye_sphere(obj)
        before[name] = radius
        inv = np.linalg.inv(np.array(obj.matrix_world))
        c = np.asarray(centre) @ inv[:3, :3].T + inv[:3, 3]
        co = np.empty(len(obj.data.vertices) * 3)
        obj.data.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        if pivot == "front":  # the cornea's front: the most forward vertex in world space (the face looks down -y)
            world = co @ np.array(obj.matrix_world)[:3, :3].T + np.array(obj.matrix_world)[:3, 3]
            c = co[int(np.argmin(world[:, 1]))]
        co = c + (co - c) * k
        obj.data.vertices.foreach_set("co", co.ravel())
        obj.data.update()
    keys = body.data.shape_keys
    if keys and base.CONTACT in keys.key_blocks:
        keys.key_blocks[base.CONTACT].value = 0.0
    parts.eye_clearance(body)
    parts.eyelid_contact(body)
    eye_layers.refit(body)
    blink_contact.make(body)
    bpy.context.view_layer.update()
    after = {n: eye_layers._eye_sphere(eyes[n])[1] for n in before}
    print("EYE SCALE", k, {n: (round(before[n] * 1000, 2), round(after[n] * 1000, 2)) for n in before}, "mm", flush=True)


def browlift(built: dict, mm: float) -> None:
    """Checklist row 12's fix, tried: our brows grown again (`brows.make`) with their band lifted `mm` before the hairs
    are rooted on the skin - our roots sit 0-12.5 mm above the eye's centre (median 8.5), on the lid the blink moves
    9.8-12 mm; his 13.7-28.5 (median 17.5), where his blink moves skin ~1 mm (2026-11-08). Do lifted brows read as
    his, and stay put in the blink? A new groom: --alone."""
    brows = importlib.import_module("bl_ext.system.juststage.modules.hair.brows")
    lashes = brows.lashes
    points = lashes.surface_points
    lashes.surface_points = lambda body, uvs: points(body, uvs) + np.array([0.0, 0.0, mm / 1000.0])
    try:
        made = brows.make(built["body"])
    finally:
        lashes.surface_points = points
    alive = []
    for o in built["objects"]:  # the old brows were removed: the gate reads this list for its anchors
        try:
            o.name
        except ReferenceError:
            continue
        alive.append(o)
    built["objects"] = [*alive, made]
    bpy.context.view_layer.update()
    print("BROW LIFT", mm, "mm", flush=True)


def setkey(built: dict, name: str, value: float) -> None:
    """One of the body's shape keys set and held (one the gate's expressions don't name, so they leave it): row 3's
    seal test - hm08's neutral leaves a see-through slit 0.3-0.9 mm wide across the mouth's middle (rays from the
    front to the front teeth's depth, 2026-11-08); Faceunits' own mouthClose at 0.1 closes it everywhere, at 0.3 too.
    (A snap of nearest lip-edge pairs across the slit, tried first, left 0.15-0.75 mm: the pairs it found weren't the
    slit's.) A shape: --alone."""
    built["body"].data.shape_keys.key_blocks[name].value = value
    bpy.context.view_layer.update()
    print("KEY", name, value, flush=True)


def lidcrease(built: dict, ring: int, mm: float) -> None:
    """The eye's deciding test (checklist row 6): can our lid's mesh hold HD Aaron's upper-lid crease? The ring of upper
    lid skin `ring` rings above the upper lash line pushed `mm` toward its eye's centre, the rings either side half as
    far, as a shape key of its own - a fold where his is (~8-10 mm above his lash line at mid-lid; the ring's height
    is printed). A shape: --alone."""
    base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
    body = built["body"]
    me = body.data
    shaped = build.shaped_coords(body)
    rows = base.rows()
    edges = np.empty(len(me.edges) * 2, np.int64)
    me.edges.foreach_get("vertices", edges)
    edges = edges.reshape(-1, 2)
    nbr: dict[int, set[int]] = {}
    for a, b in edges:
        nbr.setdefault(int(a), set()).add(int(b))
        nbr.setdefault(int(b), set()).add(int(a))
    lash = rows[:, 0][rows[:, 0] >= 0]
    lid = set(int(v) for v in rows[rows >= 0])
    upper = [int(v) for v in lash if shaped[v, 2] > np.median(shaped[lash, 2])]
    floor = shaped[upper, 2].min() - 0.001
    rings, seen, frontier = [], set(lid), set(upper)
    for _ in range(ring + 1):
        nxt = {u for v in frontier for u in nbr[v]} - seen
        nxt = {u for u in nxt if shaped[u, 2] > floor}  # the lid's skin above the lash line
        rings.append(nxt)
        seen |= nxt
        frontier = nxt
    spheres = [eye_layers._eye_sphere(o) for n, o in parts.parts_of(body).items() if n in ("eyeLeft", "eyeRight")]
    mw = np.array(body.matrix_world)
    to_local = np.linalg.inv(mw[:3, :3])
    delta = np.zeros_like(shaped)
    for idx, share in ((ring - 2, 0.5), (ring - 1, 1.0), (ring, 0.5)):
        if idx < 0:
            continue
        for v in rings[idx]:
            world = mw[:3, :3] @ shaped[v] + mw[:3, 3]
            c, _r = min(spheres, key=lambda s: np.linalg.norm(world - s[0]))
            d = (c - world) / np.linalg.norm(c - world)
            delta[v] = to_local @ (d * share * mm / 1000)
    basis = np.empty(len(me.vertices) * 3, np.float32)
    me.shape_keys.reference_key.data.foreach_get("co", basis)
    key = body.shape_key_add(name="lid crease", from_mix=False)
    key.data.foreach_set("co", (basis.reshape(-1, 3) + delta).astype(np.float32).ravel())
    key.value = 1.0
    me.update()
    bpy.context.view_layer.update()
    lash_z = shaped[upper, 2].mean()
    height = np.mean([shaped[v, 2] for v in rings[ring - 1]]) - lash_z
    print("LID CREASE: ring", ring, f"{height * 1000:.1f} mm above the lash line, {len(rings[ring - 1])} vertices,",
          mm, "mm in", flush=True)


def lidledge(built: dict, k: float, gap_mm: float) -> None:
    """The lower lid's margin turned from a wall into a ledge. Measured on the gate's man (2026-11-07 late): the lower
    lash line sits 2.4 mm straight below the rim at its depth (74-80 deg below horizontal - a wall facing the camera,
    the thick roll), the upper one 2.2 mm in front of its rim and level (5-7 deg - a ledge). The contact
    (`parts.eyelid_contact`) moves each row only along its own line from the eye's centre, so it can't turn the margin.
    Here each lower lash vertex goes onto the line `k` of the way from its own toward its rim's (1 = straight out from
    the rim), `gap_mm` off the eyeball; the middle row midway; the move carried into the skin below (`parts._carry`,
    CARRY) and added to the contact key. A shape: --alone."""
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
    body = built["body"]
    me = body.data
    co = build.shaped_coords(body)
    spheres = [eye_layers._eye_sphere(o) for n, o in parts.parts_of(body).items() if n in ("eyeLeft", "eyeRight")]
    rows = base.rows()
    push = np.zeros_like(co)

    def unit(v: np.ndarray) -> np.ndarray:
        return v / np.linalg.norm(v)

    turned = []
    for lash, margin, rim in rows:
        if lash < 0 or rim < 0:
            continue
        c, r = min(spheres, key=lambda s: np.linalg.norm(co[margin] - s[0]))
        if co[rim][2] >= c[2]:  # the upper lid: a ledge already
            continue
        d_rim, d_lash = unit(co[rim] - c), unit(co[lash] - c)
        d = unit((1 - k) * d_lash + k * d_rim)
        push[lash] = c + d * (r + gap_mm / 1000) - co[lash]
        push[margin] = c + unit(d + d_rim) * (r + (gap_mm / 1000 + parts.RIM_GAP) / 2) - co[margin]
        turned.append(float(np.linalg.norm(push[lash])))
    parts._carry(body, rows, push)
    key = me.shape_keys.key_blocks[base.CONTACT]
    kco = np.empty(len(me.vertices) * 3, np.float32)
    key.data.foreach_get("co", kco)
    key.data.foreach_set("co", (kco.reshape(-1, 3) + push / max(key.value, 1e-6)).astype(np.float32).ravel())
    me.update()
    bpy.context.view_layer.update()
    print("LID LEDGE", k, gap_mm, "mm:", len(turned), "lower lash vertices moved, most",
          round(max(turned, default=0.0) * 1000, 2), "mm", flush=True)


def browup(built: dict, value: float) -> None:
    """The brow raised by MakeHuman's own slider (`eyebrows/eyebrows-trans-down-up`, positive up): our brow sits low,
    almost on the upper lid, where HD Aaron has ~15 mm of lid and a crease (the eye view, 2026-11-08) - the lid space
    the eye's look needs, made by a slider we ship. A shape: --alone."""
    sliders = importlib.import_module("bl_ext.system.juststage.modules.body.sliders")
    sliders.apply(built["body"], sliders.catalog()["eyebrows/eyebrows-trans-down-up"], value)
    bpy.context.view_layer.update()
    print("BROW UP", value, flush=True)


def eye_slider(built: dict, key: str, value: float) -> None:
    sliders = importlib.import_module("bl_ext.system.juststage.modules.body.sliders")
    catalog = sliders.catalog()
    for side in ("l", "r"):
        sliders.apply(built["body"], catalog[f"eyes/{side}-eye-{EYE_SLIDERS[key]}"], value)
    bpy.context.view_layer.update()
    if key == "eyetrans":  # the socket moves: the eyeballs and films follow it (the lid sliders leave them be)
        importlib.import_module("bl_ext.system.juststage.modules.head.parts").refit(built["body"])
        bpy.context.view_layer.update()
    print("EYE SLIDER", key, value, flush=True)


HAIR_TRIALS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "hair"


def _transplant(built: dict, stem: str, tile: int, material: str, near_m: float = 1.0) -> None:
    """THE TRANSPLANT (a LOCAL TEST - nothing of his ships): HD Aaron's own head material on our head, rendered our
    way. His head wrapped onto ours (`groom_transfer.py skin`, `.dev/gate/hair/<stem>.npz`); each corner of our
    head tile's faces reads his texture coordinate at its nearest point on his wrapped head, into a layer named as his
    material reads it; his material (appended from the gate's .blend) then goes on those faces with every texture
    lookup pointed at that layer. If our head reaches his look in his own skin, our head and renderer carry CC5's
    skin and what is left is content; if not, the gap is ours to find in the head or the render (the user,
    2026-11-07: "if anyone cant meet quality we stop"). Shared by `aaronskin` (his head on our head tile) and
    `aaronbody` (his body skin on a region of another tile): our faces on UDIM tile `tile` within `near_m` metres of
    his carried skin take his `material`."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    maps = _maps()
    data = np.load(HAIR_TRIALS / f"{stem}.npz")
    src, stris, stuv, layer_name = data["co"].astype(np.float64), data["tris"], data["tuv"], str(data["uv_name"])
    tree = BVHTree.FromPolygons([Vector(v) for v in src], [list(t) for t in stris])
    body = built["body"]
    me = body.data
    mw = np.array(body.matrix_world)
    # our face moved toward his (`aaronshape`): each corner reads his texture where its vertex sat before the move, on
    # the wrap (the texture moves with our skin; regions moved or not alike)
    shape = me.shape_keys.key_blocks.get("aaron shape") if me.shape_keys else None
    kept = shape.value if shape else 0.0
    if shape:
        shape.value = 0.0
    co = build.shaped_coords(body) @ mw[:3, :3].T + mw[:3, 3]
    if shape:
        shape.value = kept
    udim = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[maps.UV].data.foreach_get("uv", udim)
    udim = udim.reshape(-1, 2)
    loop_v = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loop_v)
    out_uv = np.zeros((len(me.loops), 2), np.float32)
    if layer_name in me.uv_layers:  # a transplant before this one (head, then body): keep its corners
        me.uv_layers[layer_name].data.foreach_get("uv", out_uv.ravel())
    head_polys = []
    for p in me.polygons:
        ls = list(p.loop_indices)
        if not (tile - 1001 <= udim[ls, 0].mean() < tile - 1000):  # the tile asked for
            continue
        found = [tree.find_nearest(Vector(co[loop_v[li]])) for li in ls]
        if any(f[0] is None or f[3] > near_m for f in found):  # off his carried skin
            continue
        head_polys.append(p.index)
        for li, (hit, _n, ti, _d) in zip(ls, found, strict=True):
            a, b, c = src[stris[ti]]
            v0, v1, v2 = b - a, c - a, np.array(hit) - a
            d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1
            den = d00 * d11 - d01 * d01
            w1 = (d11 * d20 - d01 * d21) / den if den else 0.0
            w2 = (d00 * d21 - d01 * d20) / den if den else 0.0
            out_uv[li] = (1 - w1 - w2) * stuv[ti, 0] + w1 * stuv[ti, 1] + w2 * stuv[ti, 2]
    layer = me.uv_layers.get(layer_name) or me.uv_layers.new(name=layer_name, do_init=False)
    layer.data.foreach_set("uv", out_uv.ravel())
    with bpy.data.libraries.load(str(pg.CC5_BLEND["eevee"]), link=False) as (lib_src, dst):
        dst.materials = [material]
    mat = dst.materials[0]
    lib_dir = pg.CC5_BLEND["eevee"].parent
    for img in bpy.data.images:  # appended images: their paths made absolute against his file's folder
        if img.filepath.startswith("//") and not Path(bpy.path.abspath(img.filepath)).exists():
            img.filepath = str(lib_dir / img.filepath[2:])

    def point_at_layer(nt, seen):
        if nt in seen:
            return
        seen.add(nt)
        for node in list(nt.nodes):
            if node.type == "UVMAP":
                node.uv_map = layer_name
            elif node.type == "TEX_IMAGE" and not node.inputs["Vector"].is_linked:
                uvn = nt.nodes.new("ShaderNodeUVMap")
                uvn.uv_map = layer_name
                nt.links.new(uvn.outputs["UV"], node.inputs["Vector"])
            elif node.type == "GROUP" and node.node_tree:
                point_at_layer(node.node_tree, seen)

    point_at_layer(mat.node_tree, set())
    body.data.materials.append(mat)
    slot = len(body.data.materials) - 1
    idx = np.empty(len(me.polygons), np.int64)
    me.polygons.foreach_get("material_index", idx)
    idx[head_polys] = slot
    me.polygons.foreach_set("material_index", idx)
    me.update()
    loaded = sum(1 for i in bpy.data.images if i.has_data or (i.filepath and Path(bpy.path.abspath(i.filepath)).exists()))
    print("AARON SKIN on", len(head_polys), f"of our faces on tile {tile}; his material", mat.name, "; images found",
          loaded, flush=True)


def aaronskin(built: dict, stem: str = "aaron_skin_on_ours") -> None:
    """THE TRANSPLANT for the face: his head material on our head tile (`_transplant`)."""
    _transplant(built, stem, 1001, "Std_Skin_Head")


def aaronwrinkles(built: dict, expression: str) -> None:
    """Checklist row 13's deciding test (a LOCAL TEST, after `aaronskin`): HD Aaron's own wrinkle maps on our face in
    our smile. His head material's wrinkle shader (CC Blender Tools' rl_wrinkle_shader) is fed by 46 drivers on his
    body's keys; in his scene his smile (the gate's: Mouth_Corner_Pull_L/R 1) gives 12 of its inputs 0.6-1.0
    (`.dev/gate/hair/aaron_wrinkles.json`, read 2026-11-08 by evaluating each driver's expression). Here the appended
    copy's drivers are dropped and those inputs set: with our smile (`ictsmile`, the smile views) do his crow's feet
    and smile lines read on our face as on his?"""
    import json

    values = json.loads((HAIR_TRIALS / "aaron_wrinkles.json").read_text())[expression]
    mats = [s.material for s in built["body"].material_slots if s.material and s.material.name.startswith("Std_Skin_Head")]
    for mat in mats:
        nt = mat.node_tree
        nt.animation_data_clear()
        for key, value in values.items():
            node, idx = key.rsplit("|", 1)
            nt.nodes[node].inputs[int(idx)].default_value = value
    print("AARON WRINKLES", expression, "on", [m.name for m in mats], sum(abs(v) > 1e-4 for v in values.values()),
          "inputs on", flush=True)


def aaronbody(built: dict, stem: str = "aaron_torso") -> None:
    """THE TRANSPLANT for the body (checklist row 14, a LOCAL TEST): his body skin (`groom_transfer.py region`) on our
    body tile's faces within 1 cm of it (`_transplant`)."""
    data = np.load(HAIR_TRIALS / f"{stem}.npz")
    tile = int(data["tile"]) if "tile" in data.files else 1002
    _transplant(built, stem, tile, str(data["material"]), near_m=0.01)


def guidefile(built: dict, stem: str) -> None:
    """An authored groom's strands (`tools/gate/groom_transfer.py`, `.dev/gate/hair/<stem>.npz` - USC-HairSalon's or
    HD Aaron's own cards, LOCAL TESTS ONLY) as our scalp's guides: `scalp.make` with its own fill, shape and colour, so only the guides differ
    from the gate's man - does our render reach HD Aaron's hair once the cut is an authored one? Each strand resampled
    to the guides' POINTS evenly along its length. A new groom: --alone."""
    scalp = importlib.import_module("bl_ext.system.juststage.modules.hair.scalp")
    data = np.load(HAIR_TRIALS / f"{stem}.npz")
    strands = np.split(data["points"].astype(np.float64), np.cumsum(data["counts"])[:-1])
    t = np.linspace(0.0, 1.0, scalp.POINTS)

    def resample(s: np.ndarray) -> np.ndarray:
        along = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(s, axis=0), axis=1))]
        return np.stack([np.interp(t, along / along[-1], s[:, k]) for k in range(3)], axis=1)

    found = [resample(s) for s in strands if len(s) > 1 and np.linalg.norm(s[-1] - s[0]) > 0.002]
    body = built["body"]
    kept = scalp.guides
    scalp.guides = lambda character, style, seed=5: found
    try:
        groom = scalp.make(body, "short taper")
    finally:
        scalp.guides = kept
    pg.colour_scalp(groom)
    cid = body.juststage.character_id
    built["objects"] = [o for o in bpy.context.scene.objects if cid in (o.juststage.character_id, o.juststage.part_of)]
    print("GUIDE FILE", stem, len(found), "guides", flush=True)


def aaronshape(built: dict, stem: str = "aaron_skin_on_ours", region: str = "") -> None:
    """THE SHAPE TRANSPLANT for the eye region (a LOCAL TEST): our head moved onto HD Aaron's own face shape, on our own
    topology - each skin vertex of our head to its point on his surface (the wrap's correspondence:
    `groom_transfer.py skin`'s `placed`), fading out down the neck; our helper points (the eye sockets' fitting
    guides) moved as their nearest skin; then the parts refitted (eyes, the lid contact, the films). With `aaronskin`
    the eye view asks: can our lids, shaped as his, give his eye? `region` "lower": only the face below the eyes and
    above the jaw, at the front, faded over 15 mm - his cheeks and smile-line fold on our mesh (the lids, where the
    transplant tears, untouched): with `ictsmile` the smile's deciding test (checklist row 9). "upper": his brow and
    the fold under it above our eyes (`_upper_region`, row 5a). A shape: --alone."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.kdtree import KDTree

    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
    data = np.load(HAIR_TRIALS / f"{stem}.npz")
    wrapped, placed, tris = data["co"].astype(np.float64), data["placed"].astype(np.float64), data["all_tris"]
    tree = BVHTree.FromPolygons([Vector(v) for v in wrapped], [list(t) for t in tris])
    body = built["body"]
    me = body.data
    mw = np.array(body.matrix_world)
    co = build.shaped_coords(body) @ mw[:3, :3].T + mw[:3, 3]
    skin = makehuman.skin_mask(len(co))
    top = co[skin, 2].max()
    head = co[:, 2] > top - 0.30
    delta = np.zeros_like(co)
    found = np.zeros(len(co), bool)
    for v in np.flatnonzero(head & skin):
        hit, _n, ti, dist = tree.find_nearest(Vector(co[v]))
        if hit is None or dist > 0.01:
            continue
        found[v] = True
        a, b, c = wrapped[tris[ti]]
        v0, v1, v2 = b - a, c - a, np.array(hit) - a
        d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1
        den = d00 * d11 - d01 * d01
        w1 = (d11 * d20 - d01 * d21) / den if den else 0.0
        w2 = (d00 * d21 - d01 * d20) / den if den else 0.0
        his = (1 - w1 - w2) * placed[tris[ti][0]] + w1 * placed[tris[ti][1]] + w2 * placed[tris[ti][2]]
        delta[v] = his - co[v]
    fade = np.clip((co[:, 2] - (top - 0.27)) / 0.05, 0.0, 1.0)  # none at the neck's base, full above the jaw
    if region == "lower":  # below the eyes, above the jaw, the front: the cheeks and the smile line
        a = pg.anchors("ours", built)
        pupils, mouth = np.array(a["pupils"]), np.array(a["mouth"])
        band = np.minimum(np.clip(((pupils[2] - 0.015) - co[:, 2]) / 0.015, 0, 1),
                          np.clip((co[:, 2] - (mouth[2] - 0.045)) / 0.015, 0, 1))
        front = np.clip(((pupils[1] + 0.03) - co[:, 1]) / 0.015, 0, 1) * np.clip((0.075 - np.abs(co[:, 0])) / 0.015, 0, 1)
        fade = fade * band * front
    if region == "upper":  # above the lid's margin: his brow ridge and the fold under it, set round OUR eyes
        fade = fade * _upper_region(built, co, delta, found, placed, tris)
    delta *= fade[:, None]
    moved = np.flatnonzero(head & skin & (np.linalg.norm(delta, axis=1) > 0))
    kd = KDTree(len(moved))
    for i, v in enumerate(moved):
        kd.insert(co[v], i)
    kd.balance()
    for v in np.flatnonzero(head & ~skin):  # the helpers (the eye sockets' fitting guides) move as their nearest skin
        found = kd.find_n(co[v], 6)
        w = np.array([1.0 / max(d, 1e-4) for _, _, d in found])
        delta[v] = (delta[moved[[i for _, i, _ in found]]] * w[:, None]).sum(0) / w.sum() * fade[v]  # the region too
    local = delta @ np.linalg.inv(mw[:3, :3]).T
    keys = me.shape_keys
    basis = np.empty(len(me.vertices) * 3, np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    key = body.shape_key_add(name="aaron shape", from_mix=False)
    key.data.foreach_set("co", (basis.reshape(-1, 3) + local).astype(np.float32).ravel())
    key.value = 1.0
    me.update()
    parts.refit(body)
    bpy.context.view_layer.update()
    size = np.linalg.norm(delta[head & skin], axis=1)
    print("AARON SHAPE:", len(moved), "skin vertices moved, p50 / p90 / max", np.percentile(size, [50, 90]).round(4) * 1000,
          round(float(size.max()) * 1000, 1), "mm; parts refitted", flush=True)


def _upper_region(built: dict, co: np.ndarray, delta: np.ndarray, found: np.ndarray, placed: np.ndarray,
                  tris: np.ndarray) -> np.ndarray:
    """`aaronshape`'s "upper" region (checklist row 5a): the skin from 6 mm above each eye's centre (the lid's margin
    stays, where the full transplant tore) to the forehead, full from 12 mm, given HIS depth there - each of our
    vertices moved front-to-back onto his surface (the brow ridge and the fold under it are a height field seen from
    the front; the wrap's own correspondence flattened his fold onto our flat lid, measured 2026-11-08). His surface is
    first set on our eyes: his eyes' centres (his eye mesh's Std_Eye_L / R faces, through the wrap's alignment) onto
    ours across and up, his cornea's front onto ours in depth. Replaces `delta` in the region; returns its weights."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    st_spec = importlib.util.spec_from_file_location("smile_transfer", HERE / "smile_transfer.py")
    st = importlib.util.module_from_spec(st_spec)
    st_spec.loader.exec_module(st)
    src = np.load(HAIR_TRIALS / "aaron_skin_src.npz")["co"].astype(np.float64)
    original = src[src[:, 2] > src[:, 2].max() - 0.30]  # groom_transfer.head_region's vertices, in its order
    align = st._similarity(original, placed)
    with bpy.data.libraries.load(str(pg.CC5_BLEND["eevee"]), link=False) as (_src, dst):
        dst.objects = ["CC_Base_Eye"]
    eye = dst.objects[0]
    bpy.context.scene.collection.objects.link(eye)
    bpy.context.view_layer.update()
    ours = parts.parts_of(built["body"])
    shift = {}
    for side, name in (("L", "eyeLeft"), ("R", "eyeRight")):
        pts = st._apply(align, pg._faces_of(eye, (f"Std_Eye_{side}",))[f"Std_Eye_{side}"])
        his_c, his_front = (pts.min(0) + pts.max(0)) / 2, pts[:, 1].min()
        mine_pts = pg._world(ours[name], evaluated=False)
        mine_c = np.array(eye_layers._eye_sphere(ours[name])[0])
        across, up = mine_c[0] - his_c[0], mine_c[2] - his_c[2]
        shift[np.sign(mine_c[0])] = np.array([across, mine_pts[:, 1].min() - his_front, up])
        eye_z, eye_y = mine_c[2], mine_c[1]
    bpy.data.objects.remove(eye)
    built["aaron_shift"] = shift  # aaroncards*shaped sets his cards the same way
    left_of = np.clip(0.5 + placed[:, 0] / 0.02, 0.0, 1.0)[:, None]  # blended across the nose's bridge
    his = placed + left_of * shift[1.0] + (1.0 - left_of) * shift[-1.0]
    tree = BVHTree.FromPolygons([Vector(v) for v in his], [list(t) for t in tris])
    band = np.clip((co[:, 2] - (eye_z + 0.006)) / 0.006, 0, 1) * np.clip(((eye_z + 0.050) - co[:, 2]) / 0.015, 0, 1)
    front = np.clip(((eye_y + 0.01) - co[:, 1]) / 0.01, 0, 1) * np.clip((0.075 - np.abs(co[:, 0])) / 0.015, 0, 1)
    weight = band * front
    hits = 0
    for v in np.flatnonzero((weight > 0) & found):
        start = Vector((co[v, 0], co[v, 1] - 0.05, co[v, 2]))  # from 5 cm in front, back along the depth
        hit, _n, _i, dist = tree.ray_cast(start, Vector((0.0, 1.0, 0.0)), 0.08)
        delta[v] = (0.0, hit[1] - co[v, 1], 0.0) if hit is not None else (0.0, 0.0, 0.0)
        hits += hit is not None
    print("AARON SHAPE upper: his eyes onto ours by", {k: np.round(v * 1000, 1).tolist() for k, v in shift.items()},
          "mm (across, depth, up);", hits, "vertices given his depth", flush=True)
    return weight


def aaronteeth(built: dict) -> None:
    """THE TRANSPLANT for the mouth (a LOCAL TEST): HD Aaron's own teeth, gums and tongue (appended from the gate's
    .blend) in our mouth - matched to ours at the front teeth (`parts_gate._front_teeth`) and scaled to our teeth's
    width; his lower teeth and tongue given our teeth's jaw keys (the same rigid motions) so they ride our jaw in
    every mouth view; ours hidden. With `aaronskin` (his lips) the mouth views ask: does our mouth carry CC5's? A new set of objects: --alone."""
    from mathutils import Matrix

    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    body = built["body"]
    ours = parts.parts_of(body)["teeth"]
    with bpy.data.libraries.load(str(pg.CC5_BLEND["eevee"]), link=False) as (_src, dst):
        dst.objects = ["CC_Base_Teeth", "CC_Base_Tongue"]
    for obj in dst.objects:
        bpy.context.scene.collection.objects.link(obj)
        for m in list(obj.modifiers):
            obj.modifiers.remove(m)
        if obj.data.shape_keys:
            obj.shape_key_clear()
    bpy.context.view_layer.update()  # their world matrices are read only after the scene has them (stale before)
    for obj in dst.objects:
        world = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = world
    bpy.context.view_layer.update()
    lib_dir = pg.CC5_BLEND["eevee"].parent
    for img in bpy.data.images:
        if img.filepath.startswith("//") and not Path(bpy.path.abspath(img.filepath)).exists():
            img.filepath = str(lib_dir / img.filepath[2:])
    our_pts = pg._world(ours, evaluated=False)
    his_teeth = next(o for o in dst.objects if o.name.startswith("CC_Base_Teeth"))
    his_pts = pg._world(his_teeth, evaluated=False)
    scale = 1.0  # his teeth at their own size: our teeth part's width holds its tongue and gums (x1.19 pushed his
    # lower teeth out through our lip, 2026-11-08)
    a, b = np.array(pg._front_teeth(his_pts)), np.array(pg._front_teeth(our_pts))
    move = Matrix.Translation(b) @ Matrix.Scale(scale, 4) @ Matrix.Translation(-a)
    for obj in dst.objects:
        obj.matrix_world = move @ obj.matrix_world
    bpy.context.view_layer.update()
    # his lower teeth and tongue ride our jaw joint (`FACIAL_C_Jaw`, the face rig's - since 2026-11-08 the jaw is a
    # joint, not keys on our teeth), the rest of his teeth our head bone - skinned as ours are (`skeleton.attach`)
    skeleton = importlib.import_module("bl_ext.system.juststage.modules.rig.skeleton")
    arm = skeleton.skeleton_of(built["body"])
    made = []
    for obj in dst.objects:
        me = obj.data
        if obj.name.startswith("CC_Base_Teeth"):
            names = [s.material.name if s.material else "" for s in obj.material_slots]
            lower = np.zeros(len(me.vertices), bool)
            for p in me.polygons:
                if names[p.material_index].startswith("Std_Lower_Teeth"):
                    lower[list(p.vertices)] = True
        else:
            lower = np.ones(len(me.vertices), bool)
        for group, rows in ((skeleton.JAW, lower), (skeleton.HEAD, ~lower)):
            if rows.any():
                vg = obj.vertex_groups.get(group) or obj.vertex_groups.new(name=group)
                vg.add(np.flatnonzero(rows).tolist(), 1.0, "REPLACE")
        mod = obj.modifiers.new("JustStage skeleton", "ARMATURE")
        mod.object = arm
        obj.modifiers.move(len(obj.modifiers) - 1, 0)
        made.append(obj.name)
    built["keyed"] = [*built["keyed"], *dst.objects]
    ours.hide_render = True
    print("AARON TEETH: scale", round(scale, 3), "front teeth moved", round(float(np.linalg.norm(b - a)) * 1000, 1),
          "mm; riding our jaw and head bones:", sorted(made), flush=True)


def aaroncards(built: dict, stem: str = "aaron_skin_pinned", shaped: bool = False) -> None:
    """THE TRANSPLANT for brows, lashes and stubble (checklist rows 6-7, a LOCAL TEST): HD Aaron's own card meshes
    (Brows, Eyelash_Up, Eyelash_Low, Stubble, appended from the gate's .blend) carried onto our face by the head wrap
    with the eye rims pinned (`groom_transfer.py skin ... aaron_eyes.npz`): his alignment, then each card vertex moved as
    its nearest head vertices moved in the wrap; bound to our body by Surface Deform so they ride blinks and
    expressions; ours hidden. Does our face carry CC5's brows, lashes and stubble? A new set of objects: --alone."""
    from mathutils import Matrix
    from mathutils.kdtree import KDTree

    st_spec = importlib.util.spec_from_file_location("smile_transfer", HERE / "smile_transfer.py")
    st = importlib.util.module_from_spec(st_spec)
    st_spec.loader.exec_module(st)
    data = np.load(HAIR_TRIALS / f"{stem}.npz")
    placed, wrapped = data["placed"].astype(np.float64), data["co"].astype(np.float64)
    src = np.load(HAIR_TRIALS / "aaron_skin_src.npz")["co"].astype(np.float64)
    original = src[src[:, 2] > src[:, 2].max() - 0.30]  # groom_transfer.head_region's vertices, in its order
    align = st._similarity(original, placed)  # his alignment onto our head (wrap_head's scaled ICP)
    move = wrapped - placed
    kd = KDTree(len(placed))
    for i, p in enumerate(placed):
        kd.insert(p, i)
    kd.balance()
    body = built["body"]
    with bpy.data.libraries.load(str(pg.CC5_BLEND["eevee"]), link=False) as (_src, dst):
        # shaped: his brows only - his lashes and stubble sit on skin `aaronshape*upper` leaves ours
        dst.objects = ["Brows"] if shaped else ["Brows", "Eyelash_Up", "Eyelash_Low", "Stubble"]
    lib_dir = pg.CC5_BLEND["eevee"].parent
    for img in bpy.data.images:
        if img.filepath.startswith("//") and not Path(bpy.path.abspath(img.filepath)).exists():
            img.filepath = str(lib_dir / img.filepath[2:])
    for obj in dst.objects:
        bpy.context.scene.collection.objects.link(obj)
        for m in list(obj.modifiers):
            obj.modifiers.remove(m)
        if obj.data.shape_keys:
            obj.shape_key_clear()
    bpy.context.view_layer.update()  # world matrices read only after the scene has them (stale before)
    for obj in dst.objects:
        mw = np.array(obj.matrix_world)
        co = np.empty(len(obj.data.vertices) * 3)
        obj.data.vertices.foreach_get("co", co)
        world = st._apply(align, co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3])
        if shaped:  # on `aaronshape*upper`'s face: his cards set on our eyes as his surface there was, no wrap move
            shift = built["aaron_shift"]
            left = np.clip(0.5 + world[:, 0] / 0.02, 0.0, 1.0)[:, None]
            world = world + left * shift[1.0] + (1.0 - left) * shift[-1.0]
        for i, p in enumerate(() if shaped else world):
            found = kd.find_n(p, 4)
            w = np.array([1.0 / max(d, 1e-5) for _, _, d in found])
            world[i] = p + (move[[j for _, j, _ in found]] * w[:, None]).sum(0) / w.sum()
        obj.parent = None
        obj.matrix_world = Matrix.Identity(4)
        obj.data.vertices.foreach_set("co", world.ravel())
        obj.data.update()
    bpy.context.view_layer.update()
    # static on the neutral face: a Surface Deform bound to the body broke them into shards (the body renders through
    # its helper mask, so the bound and the rendered target differ) - the blink view can't show them
    cid = body.juststage.character_id
    replaced = ("eyebrows",) if shaped else ("eyebrows", "eyelashes", "beard")
    for o in bpy.context.scene.objects:
        if o.juststage.part_of == cid and o.juststage.part in replaced:
            o.hide_render = True
    print("AARON CARDS:", [o.name for o in dst.objects], "placed, static", "(shaped face)" * shaped, flush=True)


def aaroneyes(built: dict, own: bool = False) -> None:
    """THE TRANSPLANT for the eyes (a LOCAL TEST): HD Aaron's own eyeballs, eye occlusion and tearline (appended from
    the gate's .blend) in our sockets - each of his eyes moved and scaled onto ours (his eyeball's centre and radius
    onto our eye part's, `eye_layers._eye_sphere`), our eyes and films hidden. With `aaronskin` the eye view then asks:
    do our lids carry CC5's eye? A new set of objects: --alone."""
    eye_layers = importlib.import_module("bl_ext.system.juststage.modules.head.eye_layers")
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    body = built["body"]
    ours = parts.parts_of(body)
    target = {side: eye_layers._eye_sphere(ours[name]) for side, name in (("L", "eyeLeft"), ("R", "eyeRight"))}
    with bpy.data.libraries.load(str(pg.CC5_BLEND["eevee"]), link=False) as (_src, dst):
        dst.objects = ["CC_Base_Eye", "CC_Base_EyeOcclusion", "CC_Base_TearLine"]
    for obj in dst.objects:  # in the scene, his armature's modifiers and keys off: his rest shape
        bpy.context.scene.collection.objects.link(obj)
        for m in list(obj.modifiers):
            obj.modifiers.remove(m)
        if obj.data.shape_keys:
            obj.shape_key_clear()
    bpy.context.view_layer.update()
    eye = next(o for o in dst.objects if o.name.startswith("CC_Base_Eye") and "Occlusion" not in o.name)
    his = {}
    shift_own = {}
    for side in ("L", "R"):  # his eyeballs from their own faces (Std_Eye_L / Std_Eye_R), as parts_gate.anchors reads them
        pts = pg._faces_of(eye, (f"Std_Eye_{side}",))[f"Std_Eye_{side}"]
        his[side] = ((pts.min(0) + pts.max(0)) / 2, float((pts.max(0) - pts.min(0))[[0, 2]].mean() / 2))
        oc = np.asarray(target[side][0])
        front = pg._world(ours["eyeLeft" if side == "L" else "eyeRight"], evaluated=False)[:, 1].min()
        shift_own[side] = np.array([oc[0] - his[side][0][0], front - pts[:, 1].min(), oc[2] - his[side][0][2]])
    lib_dir = pg.CC5_BLEND["eevee"].parent
    for img in bpy.data.images:
        if img.filepath.startswith("//") and not Path(bpy.path.abspath(img.filepath)).exists():
            img.filepath = str(lib_dir / img.filepath[2:])
    for obj in dst.objects:
        mw = np.array(obj.matrix_world)
        obj.parent = None
        co = np.empty(len(obj.data.vertices) * 3)
        obj.data.vertices.foreach_get("co", co)
        world = co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
        side_of = np.where(world[:, 0] > (his["L"][0][0] + his["R"][0][0]) / 2,
                           "L" if his["L"][0][0] > his["R"][0][0] else "R",
                           "R" if his["L"][0][0] > his["R"][0][0] else "L")  # fmt: skip
        moved = world.copy()
        for side in ("L", "R"):
            sel = side_of == side
            (hc, hr), (oc, orad) = his[side], target[side]
            if own:  # his size kept (x1.12 onto ours voided the first try): his cornea's front onto ours, centred across
                moved[sel] = world[sel] + shift_own[side]
            else:
                moved[sel] = oc + (world[sel] - hc) * (orad / hr)
        obj.matrix_world = __import__("mathutils").Matrix.Identity(4)
        obj.data.vertices.foreach_set("co", moved.astype(np.float64).ravel())
        obj.data.update()
    for name in ("eyeLeft", "eyeRight"):
        ours[name].hide_render = True
    for o in bpy.context.scene.objects:
        if o.juststage.part_of == body.juststage.character_id and o.juststage.part in ("eyeshell", "eyeEdge"):
            o.hide_render = True
    print("AARON EYES: his radius", round(his["L"][1] * 1000, 2), "mm", "kept, his cornea's front on ours" if own else
          f"onto ours {round(target['L'][1] * 1000, 2)} mm", flush=True)


class _HairField:
    """A cut measured as a field (`tools/gate/hair_field.py`): length and tip stand-off by the nearest roots' median,
    direction by the nearest field points' mean."""

    def __init__(self, path: Path):
        from mathutils.kdtree import KDTree

        d = np.load(path)
        self.tan, self.length_v, self.lift_v = d["tan"], d["length"], d["lift"]
        if "profile" in d.files:  # the stand-off at a quarter, half and the whole of the length
            self.profile_v = d["profile"]
            self.profile = lambda p: tuple(np.median(self.profile_v[self._near_roots(p)], axis=0))
        self.points = KDTree(len(d["pos"]))
        for i, p in enumerate(d["pos"]):
            self.points.insert(p, i)
        self.points.balance()
        self.roots = KDTree(len(d["roots"]))
        for i, p in enumerate(d["roots"]):
            self.roots.insert(p, i)
        self.roots.balance()

    def _near_roots(self, p):
        return [i for _, i, _ in self.roots.find_n(p, 8)]

    def length(self, p):
        return float(np.median(self.length_v[self._near_roots(p)]))

    def lift(self, p):
        return float(np.median(self.lift_v[self._near_roots(p)]))

    def direction(self, p):
        found = self.points.find_n(p, 6)
        w = np.array([1.0 / max(dist, 1e-4) for _, _, dist in found])
        return (self.tan[[i for _, i, _ in found]] * w[:, None]).sum(0) / w.sum()


def fieldcut(built: dict, stem: str, guides: int = 3000) -> None:
    """The scalp hair's feasibility, part 2: OUR generator grows its own guides from its own roots along a cut measured
    as a field (`.dev/gate/hair/<stem>.npz`, `tools/gate/hair_field.py` - HD Aaron's cut on our head, a LOCAL TEST),
    then our own fill, shape and colour (`scalp.make`). Does our generator make an artist's cut? A new groom: --alone."""
    scalp = importlib.import_module("bl_ext.system.juststage.modules.hair.scalp")
    name = "field test"
    scalp.STYLES[name] = {**scalp.SHORT_TAPER, "field": _HairField(HAIR_TRIALS / f"{stem}.npz"), "guides": guides}
    try:
        groom = scalp.make(built["body"], name)
    finally:
        scalp.STYLES.pop(name, None)
    pg.colour_scalp(groom)
    cid = built["body"].juststage.character_id
    built["objects"] = [o for o in bpy.context.scene.objects if cid in (o.juststage.character_id, o.juststage.part_of)]
    print("FIELD CUT", stem, guides, "guides", flush=True)


SMILE_TRIALS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "smile"


def aaronsmile(built: dict, stem: str = "aaron_skin_pinned") -> None:
    """Checklist row 9's deciding test (a LOCAL TEST): HD Aaron's own smile shape (Mouth_Corner_Pull_L / _R, the
    gate's smile; `.dev/gate/hair/aaron_smile.npz`, his world offsets in his mesh's order) carried onto our head
    through the head wrap - each of our head's skin vertices takes his offset at its point on his wrapped face
    (barycentric), turned and scaled by the wrap's alignment, full within 2 mm of it and none past 6 mm - written into
    our mouthSmileLeft / Right by side; our cheekSquint keys emptied, so `smile_full` is his smile alone. ICT's scanned
    smile left his deep smile line out (sheet `scratchpad/sheet_C16_smileline.png`): does his own shape bring it?"""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
    st_spec = importlib.util.spec_from_file_location("smile_transfer", HERE / "smile_transfer.py")
    st = importlib.util.module_from_spec(st_spec)
    st_spec.loader.exec_module(st)
    data = np.load(HAIR_TRIALS / f"{stem}.npz")
    wrapped, placed, tris = data["co"].astype(np.float64), data["placed"].astype(np.float64), data["all_tris"]
    src = np.load(HAIR_TRIALS / "aaron_skin_src.npz")["co"].astype(np.float64)
    head_idx = np.flatnonzero(src[:, 2] > src[:, 2].max() - 0.30)  # groom_transfer.head_region's vertices, in order
    align = st._similarity(src[head_idx], placed)
    lin = align[:3, :3]  # his offsets into our frame: the wrap's rotation and scale
    smile = np.load(HAIR_TRIALS / "aaron_smile.npz")
    tree = BVHTree.FromPolygons([Vector(v) for v in wrapped], [list(f) for f in tris])
    body = built["body"]
    me = body.data
    mw = np.array(body.matrix_world)
    co = build.shaped_coords(body) @ mw[:3, :3].T + mw[:3, 3]
    skin = makehuman.skin_mask(len(co))
    head = skin & (co[:, 2] > co[skin, 2].max() - 0.30)
    deltas = {side: np.zeros_like(co) for side in ("L", "R")}
    for v in np.flatnonzero(head):
        hit, _n, ti, dist = tree.find_nearest(Vector(co[v]))
        if hit is None or dist > 0.006:
            continue
        a, b, c = wrapped[tris[ti]]
        v0, v1, v2 = b - a, c - a, np.array(hit) - a
        d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1
        den = d00 * d11 - d01 * d01
        w1 = (d11 * d20 - d01 * d21) / den if den else 0.0
        w2 = (d00 * d21 - d01 * d20) / den if den else 0.0
        bary = np.array([1 - w1 - w2, w1, w2])
        fade = float(np.clip((0.006 - dist) / 0.004, 0.0, 1.0))
        his_v = head_idx[tris[ti]]
        for side in ("L", "R"):
            deltas[side][v] = (bary @ smile[side][his_v].astype(np.float64)) @ lin.T * fade
    blocks = me.shape_keys.key_blocks
    to_local = np.linalg.inv(mw[:3, :3])
    n = len(me.vertices)
    ref = np.empty(n * 3, np.float32)
    blocks[0].data.foreach_get("co", ref)
    ref = ref.reshape(-1, 3)
    for side in ("L", "R"):
        d = deltas[side]
        size = np.linalg.norm(d, axis=1)
        x = float((co[:, 0] * size).sum() / max(size.sum(), 1e-12))
        key = blocks["mouthSmileLeft" if x > 0 else "mouthSmileRight"]  # our Left is the character's left, +x
        key.data.foreach_set("co", (ref + d @ to_local.T).astype(np.float32).ravel())
        print("AARON SMILE", side, "->", key.name, "max", round(float(size.max()) * 1000, 1), "mm, side x",
              round(x * 100, 2), "cm", flush=True)
    for name in ("cheekSquintLeft", "cheekSquintRight"):  # his corner pull raises the cheeks itself
        blocks[name].data.foreach_set("co", ref.ravel())
    me.update()
    bpy.context.view_layer.update()


def ictsmile(built: dict, stem: str, mouth: float = 1.0, cheek: float = 1.0) -> None:
    """ICT-FaceKit's smile shapes carried onto our head (`tools/gate/smile_transfer.py`, `.dev/gate/smile/<stem>.npz`)
    written into our ARKit keys of the same names (mouthSmile, cheekSquint, eyeSquint), each side to the key that
    moves the same side - the gate's face_smile / face_smile_full views then show ICT's scanned smile on our head
    against HD Aaron's (the smile proof, plan §7 "Expression shapes"). `mouth`, `cheek`: the carried mouthSmile's and
    cheekSquint's offsets scaled (his smile line and cheek mass are shape, not wrinkle maps - 2026-11-07). A shape:
    --alone."""
    deltas = np.load(SMILE_TRIALS / f"{stem}.npz")
    body = built["body"]
    me = body.data
    blocks = me.shape_keys.key_blocks
    n = len(me.vertices)
    to_local = np.linalg.inv(np.array(body.matrix_world)[:3, :3])

    def side(d: np.ndarray, at: np.ndarray) -> float:
        """Where a shape moves the skin: the moved vertices' mean x, weighted by how far each moves."""
        size = np.linalg.norm(d, axis=1)
        return float((at[:, 0] * size).sum())

    shapes = sorted({k[:-2] for k in deltas.files if k.endswith(("_L", "_R"))})  # the smile's three, or a blink
    for shape in shapes:
        ours = {}
        for long in ("Left", "Right"):
            key = blocks[f"{shape}{long}"]
            kco, ref = np.empty(n * 3, np.float32), np.empty(n * 3, np.float32)
            key.data.foreach_get("co", kco)
            key.relative_key.data.foreach_get("co", ref)
            ref = ref.reshape(-1, 3)
            ours[long] = (key, ref, side(kco.reshape(-1, 3) - ref, ref))
        for short in ("_L", "_R"):
            d = deltas[f"{shape}{short}"].astype(np.float64)
            if len(d) != n:
                raise RuntimeError(f"{stem}: {len(d)} vertices carried, the body has {n} - export him again")
            d = d @ to_local.T * {"mouthSmile": mouth, "cheekSquint": cheek}.get(shape, 1.0)
            same = [k for k, (_, ref, s) in ours.items() if np.sign(s) == np.sign(side(d, ref))]
            key, ref, _ = ours[same[0] if len(same) == 1 else ("Left" if short == "_L" else "Right")]
            key.data.foreach_set("co", (ref + d).astype(np.float32).ravel())
            print("ICT SMILE", f"{shape}{short}", "->", key.name, "max",
                  round(float(np.linalg.norm(d, axis=1).max()) * 1000, 1), "mm", flush=True)
    for single in sorted(k for k in deltas.files if k in blocks.keys()):  # one-key shapes (jawOpen, mouthFunnel ...)
        key = blocks[single]
        ref = np.empty(n * 3, np.float32)
        key.relative_key.data.foreach_get("co", ref)
        d = deltas[single].astype(np.float64)
        if len(d) != n:
            raise RuntimeError(f"{stem}: {len(d)} vertices carried, the body has {n} - export him again")
        d = d @ to_local.T
        key.data.foreach_set("co", (ref.reshape(-1, 3) + d).astype(np.float32).ravel())
        print("ICT SHAPE", single, "->", key.name, "max", round(float(np.linalg.norm(d, axis=1).max()) * 1000, 1), "mm",
              flush=True)
    me.update()
    bpy.context.view_layer.update()


SCALED_KEYS = {"pores", "micro", "relief", "roughvar", "poresize", *SHINE}


#: sRGB: HD Aaron's nail texture's median over his nail faces (Std_Nails_Diffuse, 3,576 faces, measured 2026-11-08 -
#: a local reading), the plate; the lunula and the free edge paler, as a nail's are (ours: a pale plate, a white tip)
NAIL_PLATE, NAIL_LUNULA, NAIL_EDGE = (0.545, 0.349, 0.267), (0.70, 0.55, 0.50), (0.74, 0.64, 0.55)
NAIL_LUNULA_TO, NAIL_EDGE_FROM = 0.22, 0.88  # shares of each nail's length, from its base


def _nail_pieces(built: dict) -> tuple[np.ndarray, set[int], list[dict]]:
    """Our nails: (every vertex in world space, the nail tile's vertices, one dict per nail - a connected piece of the
    tile, 1005 - with its vertices, centre, outward normal, base-to-tip `axis` and each vertex's `along`, 0 at its base
    and 1 at its tip). The axis runs from the skin within 30 mm of the nail (the finger's end, which lies behind it)
    toward the nail, flattened onto it."""
    from mathutils.kdtree import KDTree

    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    maps = _maps()
    body = built["body"]
    me = body.data
    mw = np.array(body.matrix_world)
    co = build.shaped_coords(body) @ mw[:3, :3].T + mw[:3, 3]
    udim = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[maps.UV].data.foreach_get("uv", udim)
    udim = udim.reshape(-1, 2)
    parent = np.arange(len(co))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    nail_v, normals = set(), {}
    for poly in me.polygons:
        ls = list(poly.loop_indices)
        if not (4.0 <= udim[ls, 0].mean() < 5.0):
            continue
        vs = list(poly.vertices)
        nail_v.update(vs)
        a, b, c = co[vs[0]], co[vs[1]], co[vs[2]]
        n = np.cross(b - a, c - a)
        for v in vs:
            normals[v] = normals.get(v, 0) + n
        for v in vs[1:]:
            ra, rb = root(vs[0]), root(v)
            if ra != rb:
                parent[rb] = ra
    groups = {}
    for v in sorted(nail_v):
        groups.setdefault(root(v), []).append(v)
    skin = importlib.import_module("bl_ext.system.juststage.core.makehuman").skin_mask(len(co))
    others = np.flatnonzero(skin & ~np.isin(np.arange(len(co)), np.array(sorted(nail_v))))
    kd = KDTree(len(others))
    for i, v in enumerate(others):
        kd.insert(co[v], i)
    kd.balance()
    pieces = []
    for vs in groups.values():
        vs = np.array(vs)
        c = co[vs].mean(0)
        n = sum(normals[v] for v in vs)
        n = n / np.linalg.norm(n)
        near = [others[i] for _, i, _ in kd.find_range(c, 0.03)]
        axis = c - co[near].mean(0)
        axis -= (axis @ n) * n
        axis /= np.linalg.norm(axis)
        s = (co[vs] - c) @ axis
        pieces.append({"vertices": vs, "centre": c, "normal": n, "axis": axis,
                       "along": (s - s.min()) / max(s.max() - s.min(), 1e-6)})  # fmt: skip
    return co, nail_v, pieces


def _nail_along(built: dict) -> int:
    """Each nail given `nail_along` - 0 at its base, 1 at its tip - along its finger (`_nail_pieces`). Returns the
    pieces found."""
    me = built["body"].data
    co, _, pieces = _nail_pieces(built)
    along = np.zeros(len(co), np.float32)
    for piece in pieces:
        along[piece["vertices"]] = piece["along"]
    attr = me.attributes.get("nail_along") or me.attributes.new("nail_along", "FLOAT", "POINT")
    attr.data.foreach_set("value", along)
    return len(pieces)


def naildisp(built: dict, dome_mm: float, groove_mm: float, lip_mm: float) -> None:
    """Item 7, the nail bed as detail on the shader's own plate outline (hm08 has no nail outline - RESEARCH 14.5):
    the product's nail bed (`modules/skin/nail_bed.py`, which this trial chose at 1.0 / 0.6 / 0.4 mm on 2026-11-08)
    set to other amounts - the plate's dome, the groove at its edge, the fold's lip. A shape: --alone."""
    nail_bed = importlib.import_module("bl_ext.system.juststage.modules.skin.nail_bed")
    mod = nail_bed.add(built["body"], dome_mm, groove_mm, lip_mm)
    print("NAIL DISP", dome_mm, groove_mm, lip_mm, [m.name for m in built["body"].modifiers], mod.name, flush=True)


def nailshine(built: dict, coat: float, specular: float, roughness: float) -> None:
    """Item 7, one factor: our nail plate reads milky white where HD Aaron's is barely lighter than his skin, and its
    colour along the nail (`nailmat`) changed little - so its shine: the plate's coat, specular level and roughness
    (`maps.NAIL_COAT`, `NAIL_SPECULAR`, `NAIL_ROUGHNESS`; 0.5 / 0.6 / 0.18 until this trial set them to 0 / 0.3 / 0.55)
    set on the shader's nail mixes."""
    maps = _maps()
    done = 0
    for nt in _skin_trees(built):
        for key, value in (("coat", coat), ("spec", specular), ("rough", roughness)):
            node = nt.nodes.get(maps.NODE + f"nail_{key}")
            if node is None:
                continue
            socket = next(i for i in node.inputs if i.identifier == "B_Float")
            socket.default_value = value
            done += 1
    print("NAIL SHINE", coat, specular, roughness, done, "mixes", flush=True)


def nailluna(built: dict, share: float) -> None:
    """Item 7, one factor: with the plate matte (`nailshine`), our lunula's crescent still reads white beside HD
    Aaron's faint one - its share of the pale lunula colour (`maps.NAIL_LUNULA_SHARE`, 0.35) set on the shader's mix."""
    maps = _maps()
    done = 0
    for nt in _skin_trees(built):
        node = nt.nodes.get(maps.NODE + "nail_lunula_share")
        if node is not None:
            node.inputs[1].default_value = share
            done += 1
    print("NAIL LUNULA", share, done, "trees", flush=True)


def mouthnoshadow(built: dict) -> None:
    """Item 5's inner mouth, narrowed: the body casting no shadow lit our tongue (`bodynoshadow`) - is it the mouth's
    own inner skin? Where our mouth-lining mask is (`maps._mouth_layer`'s `mouth_in`: the mask on the head's tile), the
    skin turns transparent to shadow rays (Blender's Light Path "Is Shadow Ray", the material's transparent shadows),
    the rest of the body casting as before."""
    maps = _maps()
    done = 0
    for nt in _skin_trees(built):
        inside = nt.nodes.get(maps.NODE + "mouth_in")
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
        surface = out.inputs["Surface"].links[0].from_socket
        path = nt.nodes.new("ShaderNodeLightPath")
        clear = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        both = nt.nodes.new("ShaderNodeMath")
        both.operation = "MULTIPLY"
        nt.links.new(path.outputs["Is Shadow Ray"], both.inputs[0])
        nt.links.new(inside.outputs["Value"], both.inputs[1])
        nt.links.new(both.outputs["Value"], mix.inputs["Fac"])
        nt.links.new(surface, mix.inputs[1])
        nt.links.new(clear.outputs["BSDF"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
        done += 1
    for slot in built["body"].material_slots:
        if slot.material:
            slot.material.use_transparent_shadow = True
    print("MOUTH NO SHADOW on", done, "skin materials", flush=True)


def _no_shadow_faces(built: dict, faces, label: str) -> None:
    """The body's `faces` transparent to shadow rays (the Light Path's "Is Shadow Ray" on a face attribute; the
    material's transparent shadows), the rest casting as before - a diagnostic of which skin shadows the mouth."""
    body = built["body"]
    me = body.data
    mask = np.zeros(len(me.polygons), np.float32)
    mask[list(faces)] = 1.0
    attr = me.attributes.get("js_noshadow") or me.attributes.new("js_noshadow", "FLOAT", "FACE")
    attr.data.foreach_set("value", mask)
    done = 0
    for nt in _skin_trees(built):
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
        surface = out.inputs["Surface"].links[0].from_socket
        path, get = nt.nodes.new("ShaderNodeLightPath"), nt.nodes.new("ShaderNodeAttribute")
        get.attribute_name = "js_noshadow"
        clear, mix = nt.nodes.new("ShaderNodeBsdfTransparent"), nt.nodes.new("ShaderNodeMixShader")
        both = nt.nodes.new("ShaderNodeMath")
        both.operation = "MULTIPLY"
        nt.links.new(path.outputs["Is Shadow Ray"], both.inputs[0])
        nt.links.new(get.outputs["Fac"], both.inputs[1])
        nt.links.new(both.outputs["Value"], mix.inputs["Fac"])
        nt.links.new(surface, mix.inputs[1])
        nt.links.new(clear.outputs["BSDF"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
        done += 1
    for slot in body.material_slots:
        if slot.material:
            slot.material.use_transparent_shadow = True
    print("NO SHADOW", label, int(mask.sum()), "faces on", done, "skin materials", flush=True)


def allnoshadow(built: dict) -> None:
    """The check on the method itself: every face of the body transparent to shadow rays by the material - if the tongue
    stays dark here while `bodynoshadow` (the object's own shadow switch) lit it, EEVEE doesn't take the material's
    shadow-ray transparency and the narrowed trials (mouth lining, head tile, cavity) say nothing."""
    _no_shadow_faces(built, range(len(built["body"].data.polygons)), "every face")


def headnoshadow(built: dict) -> None:
    """Item 5's inner mouth, narrowed again: the head's tile (UDIM 1001) casts no shadow - is the tongue's shadow from
    the head at all (the mouth lining alone was not it, `mouthnoshadow`)?"""
    me = built["body"].data
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[_maps().UV].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    faces = [p.index for p in me.polygons if uv[list(p.loop_indices), 0].mean() < 1.0]
    _no_shadow_faces(built, faces, "head tile")


def cavitynoshadow(built: dict) -> None:
    """...and only the faces inside the mouth: behind the front teeth's front and within the mouth's width and height
    (the teeth part's box widened 5 mm) - hm08's mouth interior, which no vertex group names."""
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    body = built["body"]
    teeth = pg._world(parts.parts_of(body)["teeth"], evaluated=False)
    lo, hi = teeth.min(0) - 0.005, teeth.max(0) + 0.005
    front = float(teeth[:, 1].min())
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    mw = np.array(body.matrix_world)
    co = build.shaped_coords(body) @ mw[:3, :3].T + mw[:3, 3]  # our shape lives in its keys
    faces = []
    for p in body.data.polygons:
        c = co[list(p.vertices)].mean(0)
        if c[1] > front and (lo[0] < c[0] < hi[0]) and (lo[2] < c[2] < hi[2]):
            faces.append(p.index)
    _no_shadow_faces(built, faces, "mouth cavity")


def bodynoshadow(built: dict) -> None:
    """Item 5's inner mouth, one factor: our tongue is in view (`tongueglow`) yet black-red whatever its material
    (`tonguess`, `tonguegrad` - no change) - is it the body's own mouth (hm08's inner mouth skin) shadowing it? The
    body casts no shadow (a diagnostic only: the whole body)."""
    built["body"].visible_shadow = False
    print("BODY NO SHADOW", built["body"].name, flush=True)


def _tongue(built: dict):
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    pm = importlib.import_module("bl_ext.system.juststage.modules.head.part_materials")
    teeth = parts.parts_of(built["body"])["teeth"]
    slot = [r for r, _ in pm.PART_REGIONS["teeth"]].index("tongue")
    mat = teeth.material_slots[slot].material.copy()
    teeth.material_slots[slot].material = mat
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    return teeth, parts.groups("teeth")["tongue"], mat, bsdf


def tonguess(built: dict, weight: float) -> None:
    """Item 5's inner mouth, one factor: our tongue's subsurface weight (1.0 built) - does it darken our tongue
    where his (CC5's rl_tongue_shader, his diffuse darker than ours) reads pink?"""
    _teeth, _idx, mat, bsdf = _tongue(built)
    bsdf.inputs["Subsurface Weight"].default_value = weight
    print("TONGUE SSS", weight, mat.name, flush=True)


def tonguegrad(built: dict, front: float, rear: float) -> None:
    """Item 5's inner mouth, one factor: HD Aaron's tongue shader (CC Blender Tools' rl_tongue_shader) scales his
    tongue's colour from `Front AO` 1.318 at its tip to `Rear AO` 0.195 at its root along a gradient map - the cavity
    lit by hand. Ours the same: the base colour times front..rear along the tongue (its tip the most forward point)."""
    teeth, idx, mat, bsdf = _tongue(built)
    me = teeth.data
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3) @ np.array(teeth.matrix_world)[:3, :3].T
    y = co[idx, 1]  # the face looks down -y: the tip is the smallest y
    t = np.zeros(len(co), np.float32)
    t[idx] = (y.max() - y) / max(y.max() - y.min(), 1e-6)  # 1 at the tip, 0 at the root
    attr = me.attributes.get("js_tongue_t") or me.attributes.new("js_tongue_t", "FLOAT", "POINT")
    attr.data.foreach_set("value", t)
    nt = mat.node_tree
    get = nt.nodes.new("ShaderNodeAttribute")
    get.attribute_name = "js_tongue_t"
    scale = nt.nodes.new("ShaderNodeMapRange")
    scale.inputs["To Min"].default_value, scale.inputs["To Max"].default_value = rear, front
    nt.links.new(get.outputs["Fac"], scale.inputs["Value"])
    mul = nt.nodes.new("ShaderNodeVectorMath")
    mul.operation = "SCALE"
    base = bsdf.inputs["Base Color"]
    if base.is_linked:
        nt.links.new(base.links[0].from_socket, mul.inputs[0])
    else:
        mul.inputs[0].default_value = base.default_value[:3]
    nt.links.new(scale.outputs["Result"], mul.inputs["Scale"])
    nt.links.new(mul.outputs["Vector"], base)
    print("TONGUE GRAD", front, rear, len(idx), "vertices", flush=True)


def tongueglow(built: dict) -> None:
    """A diagnostic for item 5's inner mouth (ours reads dark with no tongue where his pink tongue shows; ours sits like
    his - RESEARCH 14.5): our tongue drawn flat green, unlit - is it in view at all (then the gap is its lighting and
    shading), or hidden (then its place or the lips)?"""
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    pm = importlib.import_module("bl_ext.system.juststage.modules.head.part_materials")
    teeth = parts.parts_of(built["body"])["teeth"]
    slot = [r for r, _ in pm.PART_REGIONS["teeth"]].index("tongue")
    mat = teeth.material_slots[slot].material.copy()
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    glow = nt.nodes.new("ShaderNodeEmission")
    glow.inputs["Color"].default_value = (0.0, 1.0, 0.0, 1.0)
    glow.inputs["Strength"].default_value = 1.0
    nt.links.new(glow.outputs["Emission"], out.inputs["Surface"])
    teeth.material_slots[slot].material = mat
    print("TONGUE GLOW", teeth.name, mat.name, flush=True)


NAIL_FREE = 0.85  # along: past this a nail's border is its free edge (no groove, no fold over it)


def nailshape(built: dict, dome_mm: float, groove_mm: float, lip_mm: float) -> None:
    """Build queue item 7 (row 16: ours a flat plate in a rectangular window with a hard step; his a curved plate
    tucked under a cuticle fold, the skin rolling over its sides). The approved design (2026-11-05): nail beds are
    sculpted shape and detail - a loop only where shape can't (Q-BASE-3). Shape alone, on our existing faces, along
    each nail's outward normal: the plate domed across (`dome_mm` on its middle line, 0 at its sides), its border sunk
    into a groove (`groove_mm`; not at the free edge), the skin's first ring round it raised into a fold's lip
    (`lip_mm`). A shape key at 1. A shape: --alone."""
    body = built["body"]
    me = body.data
    co, nail_v, pieces = _nail_pieces(built)
    maps = _maps()
    udim = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[maps.UV].data.foreach_get("uv", udim)
    udim = udim.reshape(-1, 2)
    in_skin = set()
    for poly in me.polygons:
        if not 4.0 <= udim[list(poly.loop_indices), 0].mean() < 5.0:
            in_skin.update(poly.vertices)
    edges = np.empty(len(me.edges) * 2, np.int64)
    me.edges.foreach_get("vertices", edges)
    nbr = {}
    for a, b in edges.reshape(-1, 2):
        nbr.setdefault(int(a), set()).add(int(b))
        nbr.setdefault(int(b), set()).add(int(a))
    offset = np.zeros_like(co)
    counts = {"border": 0, "ring": 0, "plate": 0}
    for piece in pieces:
        vs, n, c, axis = piece["vertices"], piece["normal"], piece["centre"], piece["axis"]
        side = np.cross(n, axis)
        across = (co[vs] - c) @ side
        across = across / max(np.abs(across).max(), 1e-6)
        along = dict(zip(vs.tolist(), piece["along"].tolist(), strict=True))
        for v, a in zip(vs.tolist(), across.tolist(), strict=True):
            if v in in_skin:  # the border, shared with the finger's skin
                if along[v] < NAIL_FREE:
                    offset[v] -= groove_mm / 1000 * n
                    counts["border"] += 1
                    for u in nbr[v] - nail_v:
                        offset[u] = lip_mm / 1000 * n
                        counts["ring"] += 1
            else:
                offset[v] += dome_mm / 1000 * (1.0 - a * a) * n
                counts["plate"] += 1
    keys = me.shape_keys
    if keys is None:
        body.shape_key_add(name="Basis", from_mix=False)
        keys = me.shape_keys
    basis = np.empty(len(me.vertices) * 3, np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    local = offset @ np.linalg.inv(np.array(body.matrix_world)[:3, :3]).T
    key = body.shape_key_add(name="JustStage nail shape trial", from_mix=False)
    key.data.foreach_set("co", (basis.reshape(-1, 3) + local).astype(np.float32).ravel())
    key.value = 1.0
    me.update()
    print("NAIL SHAPE", dome_mm, groove_mm, lip_mm, len(pieces), "nails", counts, flush=True)


def aaronnailgeo(built: dict, stem: str = "aaron_nails") -> None:
    """Checklist row 16's deciding test, the geometry (a LOCAL TEST): his own five nail pieces - plate, cuticle fold
    and the skin round them, as his mesh has them - set on our right hand's nails (`groom_transfer.py nailfit`'s aligned
    `placed`, not its wrap) with his UVs and his nail material; our nail faces made transparent under them. His
    material on our flat plates read as crumpled skin (11-08 night); does his nail's shape on our finger read as his?"""
    data = np.load(HAIR_TRIALS / f"{stem}.npz")
    co, tris, tuv, layer_name = data["placed"].astype(np.float64), data["tris"], data["tuv"], str(data["uv_name"])
    me = bpy.data.meshes.new("Aaron nails (geometry)")
    me.from_pydata([tuple(v) for v in co], [], [tuple(int(i) for i in f) for f in tris])
    me.update()
    uv = me.uv_layers.new(name=layer_name)
    uv.data.foreach_set("uv", tuv.reshape(-1, 2).astype(np.float32).ravel())
    obj = bpy.data.objects.new("Aaron nails (geometry)", me)
    bpy.context.scene.collection.objects.link(obj)
    me.shade_smooth()
    with bpy.data.libraries.load(str(pg.CC5_BLEND["eevee"]), link=False) as (_src, dst):
        dst.materials = [str(data["material"])]
    mat = dst.materials[0]
    lib_dir = pg.CC5_BLEND["eevee"].parent
    for img in bpy.data.images:
        if img.filepath.startswith("//") and not Path(bpy.path.abspath(img.filepath)).exists():
            img.filepath = str(lib_dir / img.filepath[2:])

    def point_at_layer(nt, seen):
        if nt in seen:
            return
        seen.add(nt)
        for node in list(nt.nodes):
            if node.type == "UVMAP":
                node.uv_map = layer_name
            elif node.type == "TEX_IMAGE" and not node.inputs["Vector"].is_linked:
                uvn = nt.nodes.new("ShaderNodeUVMap")
                uvn.uv_map = layer_name
                nt.links.new(uvn.outputs["UV"], node.inputs["Vector"])
            elif node.type == "GROUP" and node.node_tree:
                point_at_layer(node.node_tree, seen)

    point_at_layer(mat.node_tree, set())
    me.materials.append(mat)
    # our nail faces (tile 1005) see-through under his
    body = built["body"]
    hidden = bpy.data.materials.new("nail hidden (trial)")
    hidden.use_nodes = True
    nt = hidden.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(nt.nodes.new("ShaderNodeBsdfTransparent").outputs[0], out.inputs["Surface"])
    body.data.materials.append(hidden)
    slot = len(body.data.materials) - 1
    maps = _maps()
    udim = np.empty(len(body.data.loops) * 2, np.float32)
    body.data.uv_layers[maps.UV].data.foreach_get("uv", udim)
    udim = udim.reshape(-1, 2)
    idx = np.empty(len(body.data.polygons), np.int64)
    body.data.polygons.foreach_get("material_index", idx)
    n = 0
    for poly in body.data.polygons:
        if 4.0 <= udim[list(poly.loop_indices), 0].mean() < 5.0:
            idx[poly.index] = slot
            n += 1
    body.data.polygons.foreach_set("material_index", idx)
    body.data.update()
    print("AARON NAIL GEOMETRY:", len(tris), "of his triangles on our hand;", n, "of our nail faces see-through", flush=True)


def nailmat(built: dict) -> None:
    """Checklist row 16 (the nails' transplants were void - his nail piece holds the fingertip's skin): our nails' own
    colour laid along each nail (`_nail_along`) - a paler lunula at the base, his plate's colour, a subtle free edge -
    on the nail tile only, our skin shader otherwise as it is. Does our nail, so coloured, read as his? (What is left
    would be the cuticle fold - geometry, Q-BASE-3's loops.)"""
    def lin(c):
        c = np.asarray(c)
        return tuple(np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)) + (1.0,)

    pieces = _nail_along(built)
    maps = _maps()
    for nt in _skin_trees(built):
        node = nt.nodes[maps.NODE + "base_color"]
        attr = nt.nodes.new("ShaderNodeAttribute")
        attr.attribute_name = "nail_along"
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        els = ramp.color_ramp.elements
        els[0].position, els[0].color = 0.0, lin(NAIL_LUNULA)
        els[1].position, els[1].color = 1.0, lin(NAIL_EDGE)
        for pos, col in ((NAIL_LUNULA_TO, NAIL_PLATE), (NAIL_EDGE_FROM, NAIL_PLATE)):
            e = els.new(pos)
            e.color = lin(col)
        nt.links.new(attr.outputs["Fac"], ramp.inputs["Fac"])
        _vec, on = _tile_uv(nt, 1005)
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(on, mix.inputs["Factor"])
        for link in list(node.outputs["Color"].links):
            nt.links.new(mix.outputs["Result"], link.to_socket)
        nt.links.new(node.outputs["Color"], mix.inputs["A"])
        nt.links.new(ramp.outputs["Color"], mix.inputs["B"])
    print("NAIL MATERIAL on", pieces, "nails", flush=True)


def factor(name: str):
    if name in FACTORS:
        return FACTORS[name]
    parts = name.split("+")
    if len(parts) > 1 and parts[0].split("*")[0] not in SCALED_KEYS:  # a chain of named factors: hairmelanin*1+hairtip*0.8
        steps = [factor(part) for part in parts]

        def chained(built: dict) -> None:
            for step in steps:
                step(built)
        return chained
    if name.startswith("hairclump"):  # hairclump*0 (the Clump group's factor)
        return lambda built: hairclump(built, float(name.split("*")[1]))
    if name.startswith("hairgrey"):  # hairgrey*0.2 (a share)
        return lambda built: hairgrey(built, float(name.split("*")[1]))
    if name.startswith("hairdensity"):  # hairdensity*2200000 (strands a m2)
        return lambda built: hairdensity(built, float(name.split("*")[1]))
    if name.startswith("hairmelanin"):  # hairmelanin*1.0
        return lambda built: hairmelanin(built, float(name.split("*")[1]))
    if name.startswith("lidsmooth"):  # lidsmooth*4*10 (rings, passes)
        _, rings, passes = name.split("*")
        return lambda built: lidsmooth(built, int(rings), int(passes))
    if name.startswith("fieldcut"):  # fieldcut*field_aaron[*3000] (the field's stem, the guides)
        stem, *n = name.split("*")[1:]
        return lambda built: fieldcut(built, stem, *(int(x) for x in n))
    if name.startswith("aaronshape"):  # aaronshape[*lower] (our head moved onto his face shape; "lower": below the eyes)
        region = name.split("*", 1)[1] if "*" in name else ""
        return lambda built: aaronshape(built, "aaron_skin_pinned", region)
    if name == "aaronsmile":  # his own smile shape carried onto our head (into mouthSmile; cheekSquint emptied)
        return aaronsmile
    if name.startswith("ictkeys*"):  # ictkeys*ict_blink_average_man: any carried ICT shapes into our keys of their names
        return lambda built: ictsmile(built, name.split("*")[1])
    if name.startswith("aaronwrinkles*"):  # aaronwrinkles*smile (after aaronskin: his wrinkle maps as his smile sets them)
        return lambda built: aaronwrinkles(built, name.split("*")[1])
    if name.startswith("teethcolour*"):  # teethcolour*0.52*0.42*0.36 (our enamel's base colour, linear)
        _k, r, g, b = name.split("*")
        return lambda built: teethcolour(built, float(r), float(g), float(b))
    if name.startswith("eyescale*"):  # eyescale*0.89 (both eyeballs scaled about their centres, the lids refitted);
        _k, k, *pivot = name.split("*")  # eyescale*0.89*front: about the cornea's front
        return lambda built: eyescale(built, float(k), *pivot)
    if name.startswith("rigsmooth*"):  # rigsmooth*10 (the body rig with Corrective Smooth; *0 the plain rig)
        return lambda built: rigsmooth(built, int(name.split("*")[1]))
    if name.startswith("naildisp*"):  # naildisp*0.6*0.4*0.3 (mm: dome, groove, lip - on the plate's own outline)
        _k, dome, groove, lip = name.split("*")
        return lambda built: naildisp(built, float(dome), float(groove), float(lip))
    if name == "mouthnoshadow":  # the mouth's inner skin casts no shadow (does it darken the tongue?)
        return mouthnoshadow
    if name == "allnoshadow":  # every face by the material route (does the route work in EEVEE?)
        return allnoshadow
    if name in ("headnoshadow", "cavitynoshadow"):  # the head's tile / the mouth's interior casts no shadow
        return {"headnoshadow": headnoshadow, "cavitynoshadow": cavitynoshadow}[name]
    if name == "bodynoshadow":  # the body casts no shadow (does its mouth shadow the tongue?)
        return bodynoshadow
    if name.startswith("nailluna*"):  # nailluna*0.12 (the lunula's share of its pale colour)
        return lambda built: nailluna(built, float(name.split("*")[1]))
    if name.startswith("nailshine*"):  # nailshine*0.1*0.4*0.4 (the nail plate's coat, specular level, roughness)
        _k, coat, spec, rough = name.split("*")
        return lambda built: nailshine(built, float(coat), float(spec), float(rough))
    if name.startswith("tonguess*"):  # tonguess*0 (our tongue's subsurface weight)
        return lambda built: tonguess(built, float(name.split("*")[1]))
    if name.startswith("tonguegrad*"):  # tonguegrad*1.318*0.195 (his shader's Front AO / Rear AO along our tongue)
        _k, front, rear = name.split("*")
        return lambda built: tonguegrad(built, float(front), float(rear))
    if name == "tongueglow":  # our tongue flat green: in view or hidden (item 5's inner mouth)
        return tongueglow
    if name.startswith("nailshape*"):  # nailshape*0.5*0.5*0.25 (mm: the plate's dome, the border's groove, the fold's lip)
        _k, dome, groove, lip = name.split("*")
        return lambda built: nailshape(built, float(dome), float(groove), float(lip))
    if name.startswith("browlift*"):  # browlift*9 (the brows grown again, their band lifted 9 mm)
        return lambda built: browlift(built, float(name.split("*")[1]))
    if name.startswith("setkey*"):  # setkey*mouthClose*0.1 (a body shape key held at a value)
        _k, key, value = name.split("*")
        return lambda built: setkey(built, key, float(value))
    if name == "aaronnailgeo":  # his nail pieces (plate, fold, skin round them) on our right hand's nails
        return aaronnailgeo
    if name == "nailmat":  # our nails coloured along their length (lunula, his plate colour, a subtle free edge)
        return nailmat
    if name == "aaronteeth":  # his teeth, gums and tongue in our mouth, riding our jaw
        return aaronteeth
    if name == "aaroncards":  # his brow, lash and stubble cards on our face, riding it
        return aaroncards
    if name == "aaroncards*shaped":  # his cards on aaronshape*upper's face (after it in the same trial)
        return lambda built: aaroncards(built, shaped=True)
    if name == "aaroneyes":  # his eyeballs and eye films in our sockets
        return aaroneyes
    if name == "aaroneyes*own":  # at his own size, his cornea's front on ours
        return lambda built: aaroneyes(built, own=True)
    if name.startswith("aaronbody"):  # aaronbody[*aaron_hand] (his body skin on our torso, or the carried region)
        stem = name.split("*", 1)[1] if "*" in name else "aaron_torso"
        return lambda built: aaronbody(built, stem)
    if name.startswith("aaronskin"):  # aaronskin[*stem] (the transplant: his head material on our head; a stem for
        # another character's wrap, e.g. aaronskin*aaron_skin_on_woman)
        return lambda built: aaronskin(built, name.split("*", 1)[1]) if "*" in name else aaronskin(built)
    if name.startswith("guidefile"):  # guidefile*aaron_cards (the carried strands' file stem)
        return lambda built: guidefile(built, name.split("*", 1)[1])
    if name.startswith("browup"):  # browup*1 (the brow slider, up)
        return lambda built: browup(built, float(name.split("*")[1]))
    if name == "blinkfix":  # the blink closed onto the lower lid (row 10)
        return blinkfix
    if name.startswith("lidcrease"):  # lidcrease*3*1.5 (the ring above the lash line, mm inward)
        _, r, mm = name.split("*")
        return lambda built: lidcrease(built, int(r), float(mm))
    if name.startswith("lidledge"):  # lidledge*1*2.3 (the share toward the rim's line, the lash line's gap in mm)
        _, k, gap = name.split("*")
        return lambda built: lidledge(built, float(k), float(gap))
    if name.startswith("ictsmile"):  # ictsmile*ict_average_man[*mouth*cheek] (the deltas' file stem, their scales)
        stem, *scales = name.split("*")[1:]
        return lambda built: ictsmile(built, stem, *(float(x) for x in scales))
    if name.startswith("lidcarry"):  # lidcarry*0.85*0.7*0.55 (a share a ring)
        shares = [float(x) for x in name.split("*")[1:]]
        return lambda built: lidcarry(built, *shares)
    if name.startswith("lashcap"):  # lashcap*1.6 (mm)
        return lambda built: lashcap(built, float(name.split("*")[1]))
    if name.split("*")[0] in EYE_SLIDERS:  # eyebag*0 (the slider's value, both eyes)
        key, value = name.split("*")
        return lambda built: eye_slider(built, key, float(value))
    if name.startswith("redmottle"):  # redmottle*1.3 (the red variation at 0.5-5 mm scaled)
        return lambda built: redmottle(built, float(name.split("*")[1]))
    if name.startswith("poretile"):  # poretile*aaron_cheek (the candidate tile's stem)
        return lambda built: poretile(built, name.split("*", 1)[1])
    if name.startswith("microtile"):  # microtile*v2b, microtile*v2b+micro*1.5 (then the depth scaled)
        stem, _, rest = name.split("*", 1)[1].partition("+")
        after = scaled(rest) if rest else None

        def prepare(built: dict) -> None:
            microtile(built, stem)
            if after:
                after(built)
        return prepare
    if name.startswith("hairmodel"):  # hairmodel*0.4*1.0*0.45 (diffuse, glossy, ambient)
        d, g, amb = (float(x) for x in name.split("*")[1:4])
        return lambda built: hairmodel(built, d, g, amb)
    if name.startswith("hairtip"):  # hairtip*0.4 (tips' melanin 1 - k)
        return lambda built: hairtip(built, float(name.split("*")[1]))
    if name.startswith("hairambient"):  # hairambient*0.45
        return lambda built: hairambient(built, float(name.split("*")[1]))
    if name.startswith("hairthrough"):  # hairthrough*0.15 (the share, not a scale)
        return lambda built: hairthrough(built, float(name.split("*")[1]))
    if name.startswith("reliefband"):  # reliefband*2
        return lambda built: reliefband(built, float(name.split("*")[1]))
    if name.startswith("handspart"):  # handspart*1.5, handspartc*1.5 (with the donor's colour)
        k = float(name.split("*")[1]) if "*" in name else 1.0
        return lambda built: handspart(built, k, colour=name.startswith("handspartc"))
    return scaled(name)


if __name__ == "__main__":
    import argparse

    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="factors.py --")
    p.add_argument("--factors", required=True)
    p.add_argument("--views", default="eye,cheek,face")
    p.add_argument("--engine", choices=("eevee", "cycles"), default="eevee")
    p.add_argument("--out", type=Path, default=pg.OUT / "factors")
    p.add_argument("--lights", choices=("stage", "world"), default="stage")
    p.add_argument("--scalp", default="library", help='our scalp: library, generated, "generated:<style>"')
    p.add_argument("--alone", action="store_true", help="a build for each factor (shape changes: eyebag*0 ...)")
    p.add_argument("--character", default="", help="another library character for ours (parts_gate's --character)")
    a = p.parse_args(args)
    out = a.out.resolve()  # absolute: Blender's render path then can't land anywhere else
    names = a.factors.split(",")
    tags = ["_f-" + n.replace("*", "x").replace(".", "p").replace("+", "_") + ("_world" if a.lights == "world" else "")
            for n in names]  # fmt: skip
    if a.alone:  # a build each (a factor that changes the shape)
        for t, n in zip(tags, names, strict=True):
            pg.render("ours", a.engine, out, a.views.split(","), pg.SIZE, pg.CYCLES_SAMPLES, tag=t, prepare=factor(n),
                      lights=a.lights, scalp=a.scalp, character=a.character)
    else:  # built once, the materials set back before each factor (parts_gate.render's variants)
        pg.render("ours", a.engine, out, a.views.split(","), pg.SIZE, pg.CYCLES_SAMPLES, lights=a.lights,
                  scalp=a.scalp, character=a.character, variants=[(t, factor(n)) for t, n in zip(tags, names, strict=True)])
    for tag in tags:
        for view in a.views.split(","):
            made = out / f"{a.engine}_{view}_ours{tag}.png"
            print("WRITTEN" if made.exists() else "MISSING", made, flush=True)
