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
import math
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


def _skin_materials(built: dict):
    """The skin materials of `_skin_trees`, with the product's own film BSDF (`skin.material.principled`) - a trial
    that rewires that BSDF calls `skin.material.sync_live` after, or EEVEE (the live view's own copy) never sees it
    (2026-11-08: `eyedark` and `liplines` changed the film's alone - void in EEVEE)."""
    mod = importlib.import_module("bl_ext.system.juststage.modules.skin.material")
    seen = set()
    for slot in built["body"].material_slots:
        mat = slot.material
        if mat and mat.node_tree and mat.name not in seen and _maps().NODE + "gain" in mat.node_tree.nodes:
            seen.add(mat.name)
            yield mat, mod.principled(mat), mod


def _depth(built: dict, key: str) -> None:
    for nt in _skin_trees(built):
        nt.nodes[_maps().NODE + f"{key}_depth"].inputs[1].default_value = 0.0


def relief0(built: dict) -> None:
    for nt in _skin_trees(built):
        cut = nt.nodes.get(_maps().NODE + "relief_off_stretched")  # the strength's own number since 2026-11-09
        if cut is not None:
            cut.inputs[0].default_value = 0.0
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


def regioncontrast(built: dict, k: float) -> None:
    """The head tile colour's regional variation (5-60 mm: redder cheeks, nose and ears, darker lids) scaled by `k` in
    log space - our composed skins average 2-3 scanned people's regional colour (`skin_base.compose`, "colour": "scans"),
    which washes their zones out; the layer diagnostic (19:0x) showed HD Aaron's skin colour on our head takes much of
    the doll look away. The composition's own content, boosted - a trial of the amount before the compose changes."""
    def change(rgb, mm_per_px):
        log = np.log(np.clip(rgb, 1e-4, 1.0))
        band = np.stack([_fft_blur(log[..., c], 5.0 / mm_per_px / 2.0) - _fft_blur(log[..., c], 60.0 / mm_per_px / 2.0)
                         for c in range(3)], -1)  # fmt: skip
        skin = rgb.sum(-1) > 0.02
        out = np.exp(log + (k - 1.0) * band)
        return np.where(skin[..., None], np.clip(out, 0.0, 1.0), rgb)

    _rewrite_colour(built, change)
    print("REGION CONTRAST x", k, flush=True)


def handspart(built: dict, strength: float = 1.0, colour: bool = False, tile: int = 1003,
              part: str = "hands") -> None:
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
        vec, on = _tile_uv(nt, tile)
        weight = nt.nodes.new("ShaderNodeMath")
        weight.operation = "MULTIPLY"
        nt.links.new(nt.nodes.new("ShaderNodeSeparateColor").outputs[0], weight.inputs[0])
        sep = weight.inputs[0].links[0].from_node
        nt.links.new(tex(nt, f"body_{tile}_{part}_weight.png", vec), sep.inputs["Color"])
        nt.links.new(on, weight.inputs[1])
        scaled = nt.nodes.new("ShaderNodeVectorMath")  # (part - 0.5) * strength + 0.5
        scaled.operation = "MULTIPLY_ADD"
        nt.links.new(tex(nt, f"body_{tile}_{part}_relief.png", vec), scaled.inputs[0])
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
            nt.links.new(tex(nt, f"body_{tile}_{part}_colour.png", vec), ratio.inputs[0])
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
                elif key == "relief":  # the strength's own number (relief_off_stretched's) since 2026-11-09
                    cut = nt.nodes.get(_maps().NODE + "relief_off_stretched")
                    target = cut.inputs[0] if cut is not None else nt.nodes[_maps().NODE + "normal_map"].inputs["Strength"]
                    target.default_value *= float(factor)
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


def cavitynet(built: dict, stem: str, strength: float) -> None:
    """A crease-net cavity tile into the skin's roughness, CC5's way (HD Aaron's `rl_head_shader` in
    `aaron_hair_eevee.blend`, read 2026-11-10): the roughness mixed toward 1 by (1 - cavity) x (1 - Fresnel(IOR 1.5,
    the bumped normal)) x strength (his Cavity Strength 0.823) - his forehead's crisp crackle net is his cavity map
    acting on the shine (his head normal is near flat there). The tile (`.dev/gate/micro/<stem>.png`, 10 mm, 1 = no
    cavity) on the microrelief's own coordinates; the film's BSDF rewired, then the live view's synced."""
    maps = _maps()
    image = bpy.data.images.load(str(MICRO_TRIALS / f"{stem}.png"), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    for mat, film, mod in _skin_materials(built):
        nt = mat.node_tree
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image, tex.interpolation = image, "Cubic"
        nt.links.new(nt.nodes[maps.NODE + "micro_coords"].outputs["Vector"], tex.inputs["Vector"])
        fresnel = nt.nodes.new("ShaderNodeFresnel")
        fresnel.inputs["IOR"].default_value = 1.5
        if film.inputs["Normal"].is_linked:
            nt.links.new(film.inputs["Normal"].links[0].from_socket, fresnel.inputs["Normal"])
        open_ = nt.nodes.new("ShaderNodeMath")  # 1 - cavity
        open_.operation = "SUBTRACT"
        open_.inputs[0].default_value = 1.0
        nt.links.new(tex.outputs["Color"], open_.inputs[1])
        facing = nt.nodes.new("ShaderNodeMath")  # 1 - Fresnel
        facing.operation = "SUBTRACT"
        facing.inputs[0].default_value = 1.0
        nt.links.new(fresnel.outputs["Fac"], facing.inputs[1])
        both = nt.nodes.new("ShaderNodeMath")
        both.operation = "MULTIPLY"
        nt.links.new(open_.outputs[0], both.inputs[0])
        nt.links.new(facing.outputs[0], both.inputs[1])
        share = nt.nodes.new("ShaderNodeMath")
        share.operation, share.use_clamp = "MULTIPLY", True
        nt.links.new(both.outputs[0], share.inputs[0])
        share.inputs[1].default_value = strength
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "FLOAT"
        nt.links.new(share.outputs[0], mix.inputs["Factor"])
        rough = film.inputs["Roughness"]
        a_in = next(i for i in mix.inputs if i.identifier == "A_Float")
        if rough.is_linked:
            nt.links.new(rough.links[0].from_socket, a_in)
        else:
            a_in.default_value = rough.default_value
        next(i for i in mix.inputs if i.identifier == "B_Float").default_value = 1.0
        nt.links.new(next(o for o in mix.outputs if o.identifier == "Result_Float"), rough)
        mod.sync_live(mat)
    print("CAVITY NET", stem, "strength", strength, flush=True)


def lipsoft(built: dict, px: float) -> None:
    """The lips' border softened: MPFB2's lips mask (`mpfb_lips.jpg` on hm08's UVs, the lip layer's share) blurred by a
    three-pass box of `px` texels (~a Gaussian) - 2026-11-10: every lip setting kept a uniform pink with a crisp drawn
    outline where HD Aaron's lip fades into the skin (`lips6.png`)."""
    nodes = [n for nt in _skin_trees(built) for n in nt.nodes if n.name.endswith("lips_mask")]
    if not nodes:
        raise RuntimeError("no lips mask node")
    src = nodes[0].image
    w, h = src.size
    a = np.empty(w * h * 4, np.float32)
    src.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)
    r = max(1, int(round(px)))

    def box(x, axis):
        c = np.cumsum(np.pad(x, [(r + 1, r) if k == axis else (0, 0) for k in range(x.ndim)], mode="edge"), axis=axis)
        hi = np.take(c, range(2 * r + 1, c.shape[axis]), axis=axis)
        lo = np.take(c, range(0, c.shape[axis] - 2 * r - 1), axis=axis)
        return (hi - lo) / (2 * r + 1)

    for _ in range(3):
        a[..., :3] = box(box(a[..., :3], 0), 1)
    soft = bpy.data.images.new(f"lips mask soft {px}", w, h, alpha=True, float_buffer=True)
    soft.colorspace_settings.name = "Non-Color"
    soft.pixels.foreach_set(a.ravel())
    for n in nodes:
        n.image = soft
    print("LIPS SOFT", px, "texels on", len(nodes), "nodes, mask", w, "x", h, flush=True)


def browthick(built: dict, k: float, melanin: float | None = None) -> None:
    """Our strand brows' radius x `k` (and the coarse hairs' melanin, given): his brows read as crisp dark hairs, ours
    a hazy grey bar - count, fine hairs, grey share and melanin were tried (`browtrial`, 11-08/09); the root radius was
    tuned too (`brows.RADIUS` 0.035 mm: 0.09 mm across read as a brush) - this scales the whole strand (2026-11-10)."""
    n = 0
    for o in bpy.data.objects:
        if o.juststage.part == "eyebrows" and o.type == "CURVES":
            radius = o.data.attributes.get("radius")
            if radius is None:
                continue
            vals = np.empty(len(radius.data), np.float32)
            radius.data.foreach_get("value", vals)
            radius.data.foreach_set("value", vals * k)
            if melanin is not None:
                for mat in o.data.materials:
                    for node in (mat.node_tree.nodes if mat and mat.node_tree else []):
                        sock = node.inputs.get("Melanin") if hasattr(node, "inputs") else None
                        if sock is not None and not sock.is_linked:
                            sock.default_value = melanin
            o.data.update_tag()
            n += 1
            print("BROW THICK x", k, "radius p50 before", float(np.median(vals)) * 1000, "mm", flush=True)
    if not n:
        raise RuntimeError("no brow curves with a radius")


MH_BROWS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "mhbrows"  # MakeHuman's CC0 pack, unpacked
MH_BROW_COLOUR = (0.045, 0.032, 0.024, 1.0)  # a dark brown (the texture's RGB is near black: the hair is its alpha)


def mhbrow(built: dict, number: str) -> None:
    """MakeHuman's CC0 brow cards (`eyebrow<number>` from makehuman_system_assets_cc0.zip, unpacked to
    .dev/gate/mhbrows): CC5's brows are cards (Brows_Hair_Transparency); ours strands, a hazy bar in the live view;
    Polytricity's long-hair strips on brow cards read as smudges (11-09). Fitted by our own MHCLO fit
    (`core.mhclo.fit` on the body's shaped coordinates, as the head parts are), shaded as MakeHuman's .mhmat has them
    (near-black, the hair in the alpha, no specular, no shadow); our strand brows hidden."""
    mhclo = importlib.import_module("bl_ext.system.juststage.core.mhclo")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    folder = MH_BROWS / f"eyebrow{number}"
    m = mhclo.parse((folder / f"eyebrow{number}.mhclo").read_text(encoding="utf-8"))
    body = built["body"]
    co = mhclo.fit(m, build.shaped_coords(body))
    verts, uvs, faces = [], [], []
    for line in (folder / f"eyebrow{number}.obj").read_text(encoding="utf-8").splitlines():
        bits = line.split()
        if not bits:
            continue
        if bits[0] == "vt":
            uvs.append((float(bits[1]), float(bits[2])))
        elif bits[0] == "f":
            faces.append([tuple(int(x) - 1 if x else -1 for x in (b.split("/") + [""])[:2]) for b in bits[1:]])
    me = bpy.data.meshes.new(f"mh brows {number}")
    me.from_pydata(co.tolist(), [], [[v for v, _t in f] for f in faces])
    uv = me.uv_layers.new(name="UVMap")
    k = 0
    for f in faces:
        for _v, t in f:
            uv.data[k].uv = uvs[t] if t >= 0 else (0.0, 0.0)
            k += 1
    obj = bpy.data.objects.new(f"mh brows {number}", me)
    for coll in body.users_collection:
        coll.objects.link(obj)
    obj.matrix_world = body.matrix_world
    mat = bpy.data.materials.new(f"mh brows {number}")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(folder / f"eyebrow{number}.png"), check_existing=True)
    bsdf.inputs["Base Color"].default_value = MH_BROW_COLOUR
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.7
    if hasattr(mat, "use_transparent_shadow"):
        mat.use_transparent_shadow = True
    me.materials.append(mat)
    obj.visible_shadow = False
    hidden = 0
    for o in bpy.data.objects:
        if o.juststage.part == "eyebrows":  # groom._attach's tag for brows
            o.hide_render = True
            hidden += 1
    print("MH BROWS", number, len(co), "vertices,", len(faces), "cards; strand brows hidden:", hidden, flush=True)


ICT_TRIALS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "ict"
ICT_HIDE_MM = 12.0  # our head's skin hidden where ICT's head lies this close over it


def icthead(built: dict, stem: str) -> None:
    """The eye's and the ear's proof on a free head (`tools/gate/ict_head.py`, a trial - Q-BASE-4 stays the user's for
    the product): ICT-FaceKit's head placed on our man (`.dev/gate/ict/<stem>.npz`, world positions), given our UDIM
    UVs by Blender's Data Transfer from the body (nearest face, interpolated - Blender's own way to copy UVs between
    meshes) and our skin material; our head's skin under it made transparent (a material slot of its own), so the
    lashes, brows and eye parts stay bound to the body's surface as they are."""
    import bmesh  # noqa: F401
    from mathutils import kdtree

    maps = _maps()
    body = built["body"]
    data = np.load(ICT_TRIALS / f"{stem}.npz")
    verts, counts, flat = data["verts"], data["counts"], data["flat"]
    starts = np.r_[0, np.cumsum(counts)[:-1]]
    polys = [flat[s:s + c].tolist() for s, c in zip(starts, counts, strict=True)]
    me = bpy.data.meshes.new("ICT head")
    me.from_pydata(verts.tolist(), [], polys)
    me.validate()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.uv_layers.new(name=maps.UV)
    head = bpy.data.objects.new("ICT head", me)
    for coll in body.users_collection:
        coll.objects.link(head)
    active = body.data.uv_layers.active
    body.data.uv_layers.active = body.data.uv_layers[maps.UV]
    mod = head.modifiers.new("uv from ours", "DATA_TRANSFER")
    mod.object = body
    mod.use_loop_data = True
    mod.data_types_loops = {"UV"}
    mod.loop_mapping = "POLYINTERP_NEAREST"
    mod.layers_uv_select_src = maps.UV  # the source layer by name (its enum lists ALL and the layers' names)
    dst_items = [i.identifier for i in mod.bl_rna.properties["layers_uv_select_dst"].enum_items]
    mod.layers_uv_select_dst = "NAME" if "NAME" in dst_items else dst_items[0]  # the same name on ICT's mesh
    deps = bpy.context.evaluated_depsgraph_get()
    deps.update()
    baked = bpy.data.meshes.new_from_object(head.evaluated_get(deps))
    head.modifiers.remove(mod)
    head.data = baked
    body.data.uv_layers.active = active
    head.data.materials.clear()
    head.data.materials.append(body.juststage.skin_material)
    # our head's skin under ICT's: transparent, its own slot (the body's topology kept for everything bound to it)
    hide = bpy.data.materials.new("ICT trial hidden skin")
    hide.use_nodes = True
    nt = hide.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(nt.nodes.new("ShaderNodeBsdfTransparent").outputs["BSDF"], out.inputs["Surface"])
    if hasattr(hide, "use_transparent_shadow"):
        hide.use_transparent_shadow = True
    body_eval = body.evaluated_get(deps)
    bme = body_eval.to_mesh()
    world = np.array(body.matrix_world)
    co = np.array([world[:3, :3] @ np.array(v.co) + world[:3, 3] for v in bme.vertices])
    body_eval.to_mesh_clear()
    tree = kdtree.KDTree(len(verts))
    for i, p in enumerate(verts):
        tree.insert(p.tolist(), i)
    tree.balance()
    near = np.array([tree.find(p.tolist())[2] < ICT_HIDE_MM / 1000.0 for p in co])
    uv = np.empty(len(body.data.loops) * 2, np.float32)
    body.data.uv_layers[maps.UV].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    loop_vert = np.empty(len(body.data.loops), np.int64)
    body.data.loops.foreach_get("vertex_index", loop_vert)
    body.data.materials.append(hide)
    slot = len(body.data.materials) - 1
    n = 0
    for poly in body.data.polygons:
        loops = range(poly.loop_start, poly.loop_start + poly.loop_total)
        if all(uv[k, 0] < 1.0 for k in loops) and all(near[loop_vert[k]] for k in loops):
            poly.material_index = slot
            n += 1
    print("ICT HEAD", stem, len(verts), "vertices; our head's faces hidden under it:", n, flush=True)
    if "eyes" in data.files:  # head3: our eyes moved into ICT's sockets (its lids kept whole), per side
        _eyes_to(body, np.asarray(data["eyes"], np.float64))


EYE_PARTS = ("eyeLeft", "eyeRight", "eyeshell", "eyeEdge")


def _eyes_to(body, centres: np.ndarray) -> None:
    """Our eye parts (the eyeballs and their films) translated per side so each eyeball's centre lands on `centres`
    (world, one a side by x's sign) - every vertex by its own side's shift, every shape key alike."""
    cid = body.juststage.part_of or body.juststage.character_id
    objs = [o for o in bpy.data.objects if o.juststage.part in EYE_PARTS and o.type == "MESH"
            and (o.juststage.part_of == cid or not cid)]  # fmt: skip

    def world_co(o):
        m = np.array(o.matrix_world)
        co = np.empty(len(o.data.vertices) * 3, np.float32)
        o.data.vertices.foreach_get("co", co)
        return co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]

    balls = [o for o in objs if o.juststage.part in ("eyeLeft", "eyeRight")]
    ours = {np.sign(world_co(o)[:, 0].mean()): world_co(o).mean(0) for o in balls}
    shift = {np.sign(c[0]): c - ours[np.sign(c[0])] for c in centres if np.sign(c[0]) in ours}
    for o in objs:
        inv = np.linalg.inv(np.array(o.matrix_world))[:3, :3]
        side = np.sign(world_co(o)[:, 0])
        d_world = np.array([shift.get(s, np.zeros(3)) for s in side])
        d_local = d_world @ inv.T
        blocks = list(o.data.shape_keys.key_blocks) if o.data.shape_keys else []
        for target in [o.data.vertices] + [kb.data for kb in blocks]:
            co = np.empty(len(target) * 3, np.float32)
            target.foreach_get("co", co)
            target.foreach_set("co", (co.reshape(-1, 3) + d_local).astype(np.float32).ravel())
        o.data.update()
    print("EYES MOVED to ICT's sockets:", {int(k): np.round(v * 1000, 1).tolist() for k, v in shift.items()}, "mm",
          [o.name for o in objs], flush=True)


def bodycoat(built: dict, weight: float) -> None:
    """The body's coat weight (`maps.BODY_COAT_WEIGHT`, 0.03 - the coat mix's B, the face's A kept): HD Aaron's body
    coat ~0.10 (RESEARCH 14.10), tried 11-07 with our coat on a smooth normal (not the lever); since 2026-11-10 the coat
    shines off the relief - his foot's and hand's wet sheen against our matte. One node feeds both BSDFs."""
    n = 0
    for nt in _skin_trees(built):
        node = nt.nodes.get(_maps().NODE + "coat")
        if node is not None:
            next(i for i in node.inputs if i.identifier == "B_Float").default_value = weight
            n += 1
    if not n:
        raise RuntimeError("no coat mix on the skin")
    print("BODY COAT", weight, "on", n, "skins", flush=True)


def coatnormal(built: dict) -> None:
    """The coat lobe on the skin's bumped normal - HD Aaron's head BSDF takes the same normal for both lobes (CC
    Blender Tools' `rl_head_shader` feeds Normal and Coat Normal from one output, read 2026-11-10); ours leaves Coat
    Normal unlinked, so our sharper oil lobe sees a smooth surface and can't glint on the relief's bumps (his forehead's
    pinpoint glints, `cav_fh4.png`). The film BSDF rewired, the live view's synced."""
    n = 0
    for mat, film, mod in _skin_materials(built):
        if film.inputs["Normal"].is_linked:
            mat.node_tree.links.new(film.inputs["Normal"].links[0].from_socket, film.inputs["Coat Normal"])
            mod.sync_live(mat)
            n += 1
    if not n:
        raise RuntimeError("no skin BSDF with a linked normal")
    print("COAT NORMAL linked on", n, "skins", flush=True)


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


REGION_TRIALS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "regions"


def regions(built: dict, stem: str) -> None:
    """The face's region map swapped for a variant (`.dev/gate/regions/<stem>/face_regions.png`, made by
    `tools/make_face_regions.py -- --out ... --pores forehead=1.2`): one region's relief depth changed, the rest as
    shipped (2026-11-08: round 1's `pores*0.6` helped the forehead and hurt the cheek - the forehead alone)."""
    maps = _maps()
    image = bpy.data.images.load(str(REGION_TRIALS / stem / "face_regions.png"), check_existing=False)
    image.colorspace_settings.name = "Non-Color"
    n = 0
    for nt in _skin_trees(built):
        node = nt.nodes.get(maps.NODE + "face_regions")
        if node is not None:
            node.image = image
            n += 1
    if not n:
        raise RuntimeError("no region map node found on the skin")
    print("REGIONS", stem, "on", n, "skins", flush=True)


#: the eye-open sliders (body_create.EYE_OPEN) one at a time - the lower lid's thick roll at the eye view; shape keys,
#: so these run alone (`--alone`: a build each - the trials' material reset doesn't undo a shape)
EYE_SLIDERS = {"eyebag": "bag-decr-incr", "eyeheight2": "height2-decr-incr", "eyefold": "eyefold-concave-convex",
               "eyefoldup": "eyefold-down-up", "eyeheight1": "height1-decr-incr",
               "eyetrans": "trans-down-up"}  # eyetrans*-1: the eye 2.9 mm down (with browup*1's 7.1 mm: his brow height)


def lashtrial(built: dict, radius_mm: float, count: float) -> None:
    """The lashes grown again with the lower lashes' root radius (`lashes.LOWER["radius"]`, 0.025 mm) and count an eye
    (80) set - 2026-11-09, ours far fainter than HD Aaron's dark lower fan. A new groom: --alone."""
    lashes = importlib.import_module("bl_ext.system.juststage.modules.hair.lashes")
    old = dict(lashes.LOWER)
    lashes.LOWER.update(radius=radius_mm / 1000.0, count=int(count))
    try:
        lashes.make(built["body"])
    finally:
        lashes.LOWER.clear()
        lashes.LOWER.update(old)
    cid = built["body"].juststage.character_id
    built["objects"] = [o for o in bpy.context.scene.objects if cid in (o.juststage.character_id, o.juststage.part_of)]
    print("LASHES lower radius", radius_mm, "mm, count", int(count), flush=True)


def lashup(built: dict, rise: float, curl: float, long_mm: float | None = None, radius_mm: float | None = None,
           tries: float | None = None) -> None:
    """The upper lashes grown again with their rise (`lashes.UPPER["rise"]`, 0 deg) and curl (50 deg) set - 2026-11-10
    at full size: ours hang down over the iris as a dark curtain with a few spikes standing at the centre, his leave
    the margin and curl up and out. A new groom: --alone."""
    lashes = importlib.import_module("bl_ext.system.juststage.modules.hair.lashes")
    old = dict(lashes.UPPER)
    old_tries = lashes.CLEAR_TRIES
    if tries is not None:  # the whole-lash turns before the joint bends (`lashes.CLEAR_TRIES`, 12): 0 - bends alone
        lashes.CLEAR_TRIES = int(tries)
    lashes.UPPER.update(rise=rise, curl=curl)
    if long_mm is not None:  # the longest (centre) lash; the short ones scaled with it
        lashes.UPPER.update(long=long_mm, short=old["short"] * long_mm / old["long"])
    if radius_mm is not None:
        lashes.UPPER.update(radius=radius_mm / 1000.0)
    try:
        lashes.make(built["body"])
    finally:
        lashes.UPPER.clear()
        lashes.UPPER.update(old)
        lashes.CLEAR_TRIES = old_tries
    cid = built["body"].juststage.character_id
    built["objects"] = [o for o in bpy.context.scene.objects if cid in (o.juststage.character_id, o.juststage.part_of)]
    print("LASHES upper rise", rise, "curl", curl, "long", long_mm, "radius", radius_mm, "tries", tries, flush=True)


def lashlower(built: dict, melanin: float) -> None:
    """The lower lashes' melanin (`lashes.LOWER["melanin"]`, 0.6) set on the groom's own curve attribute - 2026-11-09,
    they read golden-orange on the Heavy woman's dark skin beside her near-black upper lashes; HD Aaron's dark brown.
    The lower lashes found once by their melanin and kept (each variant sets its value on the same strands)."""
    lashes = importlib.import_module("bl_ext.system.juststage.modules.hair.lashes")
    n = 0
    for obj in bpy.data.objects:
        if obj.type != "CURVES" or obj.juststage.part != "eyelashes":
            continue
        attr = obj.data.attributes["melanin"]
        values = np.empty(len(attr.data), np.float32)
        attr.data.foreach_get("value", values)
        lower = built.setdefault("lower_lashes", {}).setdefault(obj.name, np.isclose(values, lashes.LOWER["melanin"]))
        values[lower] = melanin
        attr.data.foreach_set("value", values)
        obj.data.update_tag()
        n += int(lower.sum())
    print("LOWER LASHES melanin", melanin, "on", n, "strands", flush=True)


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


def aaronflat(built: dict) -> None:
    """After `aaronskin` (a LOCAL TEST, a diagnostic): his transplanted head material with its relief off - every group
    input whose name holds "Normal Strength" (CC Blender Tools' skin group: Normal Strength, Micro Normal Strength...)
    set to 0 - so his colour alone is on our head. 19:5x: his whole skin took much of the doll look away, our regional
    colour boosted did little - is his gain the colour or the relief (his forehead lines, folds)?"""
    n = 0
    for slot in built["body"].material_slots:
        mat = slot.material
        if not (mat and mat.node_tree and mat.name.startswith("Std_Skin_Head")):
            continue
        for node in mat.node_tree.nodes:
            for socket in getattr(node, "inputs", []):
                if "Normal Strength" in socket.name and hasattr(socket, "default_value") and not socket.is_linked:
                    socket.default_value = 0.0
                    n += 1
    print("AARON FLAT: his relief off -", n, "inputs at 0", flush=True)


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


#: the scalp's style trials (2026-11-08, the own-content proof's step 1: our "short taper" reads as a grey helmet - a
#: bowl outline, a hard straight fringe line): (style overrides on SHORT_TAPER, MASK_RINGS or None). "base" regrows the
#: style unchanged - each trial's one-change baseline (the library's groom is a stored asset, not this regrow)
SCALP_PRESETS = {
    "base": ({}, None),
    "sides": ({"lift": (24.0, 4.0), "side_scale": (0.4, 0.85, 0.35)}, None),  # flatter, shorter sides: no bowl
    "hairline": ({}, 1),  # the scalp grown one ring past the hedgehog's roots, not two: a higher, softer hairline
    "hairline0": ({}, 0),  # the hedgehog's roots alone (56 mm above the eye): round 1 showed ours ~30 mm, a wig's edge
}


def scalpstyle(built: dict, preset: str) -> None:
    """Our scalp regrown with one style change (SCALP_PRESETS), the library's groom hidden - a new groom: --alone."""
    scalp = importlib.import_module("bl_ext.system.juststage.modules.hair.scalp")
    over, rings = SCALP_PRESETS[preset]
    _hide_part(built, "scalp")
    old_rings, name = scalp.MASK_RINGS, f"style trial {preset}"
    if rings is not None:
        # the mask is made once per file and the fill group's image node points at it: write the new rings' mask INTO
        # that image (2026-11-08 15:54: removing it left the node empty - hair grew over the whole body, 3.5M strands,
        # 30 GB, stopped by the RAM guard)
        scalp.MASK_RINGS = rings
        old = bpy.data.images.get("JustStage scalp mask")
        if old is not None:
            old.name = "JustStage scalp mask (old)"
        new = scalp.scalp_mask(built["body"])
        if old is not None:
            old.pixels.foreach_set(np.array(new.pixels[:], np.float32))
            old.pack()
            bpy.data.images.remove(new)
            old.name = "JustStage scalp mask"
    scalp.STYLES[name] = {**scalp.SHORT_TAPER, **over}
    try:
        groom = scalp.make(built["body"], name)
    finally:
        scalp.STYLES.pop(name, None)
        scalp.MASK_RINGS = old_rings
    pg.colour_scalp(groom)
    cid = built["body"].juststage.character_id
    built["objects"] = [o for o in bpy.context.scene.objects if cid in (o.juststage.character_id, o.juststage.part_of)]
    print("SCALP STYLE", preset, over, "rings", rings if rings is not None else old_rings, flush=True)


def _skin_node_inputs(built: dict, node_name: str):
    """Every skin material's node `maps.NODE + node_name` (one per skin tree)."""
    maps = _maps()
    return [nt.nodes[maps.NODE + node_name] for nt in _skin_trees(built) if maps.NODE + node_name in nt.nodes]


def lipshine(built: dict, rough: float, coat: float) -> None:
    """The lips' roughness and coat (`maps.LIP_ROUGHNESS`, `LIP_COAT`; 0.4 / 0.2 since 2026-11-09 midday,
    0.6 / 0.05 that morning, 0.33 / 0.3 before) - step 1's fault: a broad plastic sheen over our lips where his show a small wet highlight on a matte lip;
    2026-11-09 the lines' wet glints at extreme close-up."""
    n = 0
    for key, value in (("lips_rough", rough), ("lips_coat", coat)):
        for node in _skin_node_inputs(built, key):
            next(i for i in node.inputs if i.identifier == "B_Float").default_value = value
            n += 1
    print("LIP SHINE rough", rough, "coat", coat, "on", n, "nodes", flush=True)


def liptint(built: dict, r: float, g: float, b: float) -> None:
    """The lips' tint over the skin (`maps.LIP_TINT` (1.0, 0.56, 0.90)) - step 1's fault: one flat saturated pink."""
    nodes = _skin_node_inputs(built, "lips_tint")
    for node in nodes:
        next(i for i in node.inputs if i.identifier == "B_Color").default_value = (r, g, b, 1.0)
    print("LIP TINT", (r, g, b), "on", len(nodes), "nodes", flush=True)


def lipseam(built: dict, k: float) -> None:
    """The lips' darkening toward the mouth's line (`maps.LIP_SEAM_STRENGTH` 1.0, by `mouth_seam.png`) at `k`."""
    nodes = _skin_node_inputs(built, "lips_seam_share")
    for node in nodes:
        node.inputs[1].default_value = k
    print("LIP SEAM", k, "on", len(nodes), "nodes", flush=True)


def upperlip(built: dict, r: float, g: float, b: float) -> None:
    """The upper lip deeper red than the lower (HD Aaron's; ours one pink on both, 2026-11-09): the base colour x (r, g,
    b) on the lips' share above the mouth's line (world height over the gate's mouth anchor, -0.5 to +2 mm) - a trial
    on a still render; the product would need a mask in UV that follows the lips."""
    maps = _maps()
    mouth_z = pg.anchors("ours", built)["mouth"][2]
    n = 0
    for mat, bsdf, mod in _skin_materials(built):
        nt = mat.node_tree
        share = nt.nodes.get(maps.NODE + "lips_share")
        if share is None or not bsdf.inputs["Base Color"].is_linked:
            continue
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Position"], sep.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.clamp = True
        nt.links.new(sep.outputs["Z"], ramp.inputs["Value"])
        ramp.inputs["From Min"].default_value, ramp.inputs["From Max"].default_value = mouth_z - 0.0005, mouth_z + 0.002
        upper = nt.nodes.new("ShaderNodeMath")
        upper.operation = "MULTIPLY"
        nt.links.new(ramp.outputs["Result"], upper.inputs[0])
        nt.links.new(share.outputs["Value"], upper.inputs[1])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(upper.outputs["Value"], mix.inputs["Factor"])
        next(i for i in mix.inputs if i.identifier == "A_Color").default_value = (1.0, 1.0, 1.0, 1.0)
        next(i for i in mix.inputs if i.identifier == "B_Color").default_value = (r, g, b, 1.0)
        times = nt.nodes.new("ShaderNodeVectorMath")
        times.operation = "MULTIPLY"
        nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, times.inputs[0])
        nt.links.new(next(o for o in mix.outputs if o.identifier == "Result_Color"), times.inputs[1])
        nt.links.new(times.outputs["Vector"], bsdf.inputs["Base Color"])
        mod.sync_live(mat)
        n += 1
    print("UPPER LIP", (r, g, b), "at mouth z", round(mouth_z, 4), "on", n, "skins", flush=True)


def lipcrease(built: dict, sharp: float, period: float, depth_mm: float, distortion: float, detail: float) -> None:
    """The lip lines as thin creases on a smooth lip: the wave's 0-1 raised to `sharp` (a plateau with a narrow valley
    each period), its period (mm), depth (mm), distortion and detail set - 2026-11-09, the sine ripple at distortion 8 /
    detail 3 read as an even worm-like crinkle, crepe paper, beside HD Aaron's few irregular furrows."""
    maps = _maps()
    n = 0
    for nt in _skin_trees(built):
        wave, varied = nt.nodes.get(maps.NODE + "lips_wave"), nt.nodes.get(maps.NODE + "lips_varied")
        if wave is None or varied is None:
            continue
        wave.inputs["Scale"].default_value = maps.LIP_MM_PER_V / period
        wave.inputs["Distortion"].default_value, wave.inputs["Detail"].default_value = distortion, detail
        crease = nt.nodes.get(maps.NODE + "lips_crease")  # the product's own since 2026-11-09 (maps.LIP_CREASE)
        if crease is None:
            crease = nt.nodes.new("ShaderNodeMath")
            crease.operation = "POWER"
            nt.links.new(wave.outputs["Fac"], crease.inputs[0])
            nt.links.new(crease.outputs[0], varied.inputs[0])
        crease.inputs[1].default_value = sharp
        nt.nodes[maps.NODE + "lips_lines"].inputs["Distance"].default_value = depth_mm / 1000.0
        n += 1
    print("LIP CREASE", sharp, period, depth_mm, distortion, detail, "on", n, flush=True)


def lipset(built: dict, period: float, depth: float, distortion: float, vary: float) -> None:
    """The product's lip lines (`maps.LIP_LINES` (1.3, 0.0004, 4.0, 0.8)) set on its own nodes - at full resolution they
    read as a dense even rib, corduroy, beside HD Aaron's sparse irregular creases on a smooth lip (2026-11-08)."""
    maps = _maps()
    n = 0
    for nt in _skin_trees(built):
        nodes = nt.nodes
        if maps.NODE + "lips_wave" not in nodes:
            continue
        nodes[maps.NODE + "lips_wave"].inputs["Scale"].default_value = maps.LIP_MM_PER_V / period
        nodes[maps.NODE + "lips_wave"].inputs["Distortion"].default_value = distortion
        nodes[maps.NODE + "lips_lines"].inputs["Distance"].default_value = depth
        gain = nodes[maps.NODE + "lips_gain"]
        gain.inputs[1].default_value, gain.inputs[2].default_value = vary, 1.0 - vary
        n += 1
    print("LIP SET", (period, depth, distortion, vary), "on", n, "trees", flush=True)


def browedge(built: dict, sd: float) -> None:
    """Our brows grown again with their roots in a bell across the band (`brows.EDGE_SD`; 0 = today's even spread):
    2026-11-09, ours a block with hard edges beside HD Aaron's soft brows. A new groom: --alone."""
    brows = importlib.import_module("bl_ext.system.juststage.modules.hair.brows")
    old = brows.EDGE_SD
    brows.EDGE_SD = sd or None
    try:
        brows.make(built["body"], grey_share=pg.BROW_GREY if built["body"].juststage.gender > 0.5 else 0.0)
    finally:
        brows.EDGE_SD = old
    cid = built["body"].juststage.character_id
    built["objects"] = [o for o in bpy.context.scene.objects if cid in (o.juststage.character_id, o.juststage.part_of)]
    print("BROW EDGE", sd, flush=True)


MASK_TRIALS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "masks"


VF_BUSTS = Path(__file__).resolve().parents[2] / ".dev" / "downloads" / "vincent_hair_2026-11-09" / "m01_busts.blend"


def vfhair(built: dict, bust: str, textured: bool = False, alpha: str = "") -> None:
    """An artist's free cut on our head (2026-11-09): VincentFreelance's "FREE Male Fashion Hair collection 01" (CC BY
    4.0, Sketchfab 2735370f...; split per bust into `.dev/downloads/.../m01_busts.blend`: vf_hair_<bust>, vf_head_<bust>)
    - its source head's cranium (the top 8 cm) fitted to ours by scale per axis and offset, the cards moved with it,
    any card point inside our skin pushed 1 mm out; our scalp groom hidden. The cards plain (a first look at the shape:
    the creator's strand textures are not free). A shape: --alone."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    body = built["body"]
    with bpy.data.libraries.load(str(VF_BUSTS), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in (f"vf_hair_{bust}", f"vf_head_{bust}")]
    hair, head = (next(o for o in dst.objects if o.name.startswith(k)) for k in ("vf_hair", "vf_head"))
    scene = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    mesh = ev.to_mesh()
    ours = np.array([body.matrix_world @ v.co for v in mesh.vertices])
    ev.to_mesh_clear()
    theirs = np.array([head.matrix_world @ v.co for v in head.data.vertices])

    def cap(points, centre_x):
        top = points[:, 2].max()
        near = np.abs(points[:, 0] - centre_x) < 0.12
        return points[near & (points[:, 2] > top - 0.08)]

    ours_cap = cap(ours, float(np.median(ours[ours[:, 2] > ours[:, 2].max() - 0.05, 0])))
    theirs_cap = cap(theirs, float(np.median(theirs[:, 0])))
    lo_o, hi_o, lo_t, hi_t = ours_cap.min(0), ours_cap.max(0), theirs_cap.min(0), theirs_cap.max(0)
    sx, sy = (hi_o[0] - lo_o[0]) / (hi_t[0] - lo_t[0]), (hi_o[1] - lo_o[1]) / (hi_t[1] - lo_t[1])

    def nose_tip(points):  # the head's most forward point (the character faces -Y), the head only
        head_pts = points[points[:, 2] > points[:, 2].max() - 0.25]
        return head_pts[np.argmin(head_pts[:, 1])]

    nose_o, nose_t = nose_tip(ours), nose_tip(theirs)
    sz = (hi_o[2] - nose_o[2]) / (hi_t[2] - nose_t[2])  # the face's height: the cut's hairline lands on ours
    scale = np.array([sx, sy, sz])
    anchor_t = np.array([(lo_t[0] + hi_t[0]) / 2, (lo_t[1] + hi_t[1]) / 2, hi_t[2]])
    anchor_o = np.array([(lo_o[0] + hi_o[0]) / 2, (lo_o[1] + hi_o[1]) / 2, hi_o[2]])
    # the source bust's brow cards out (in front, 2.5-6.5 cm above its nose tip, near the face's middle)
    import bmesh

    hp = np.array([hair.matrix_world @ v.co for v in hair.data.vertices])
    ed = np.array([e.vertices for e in hair.data.edges])
    lab = np.arange(len(hp))
    while True:
        mn = np.minimum(lab[ed[:, 0]], lab[ed[:, 1]])
        new = lab.copy()
        np.minimum.at(new, ed[:, 0], mn)
        np.minimum.at(new, ed[:, 1], mn)
        new = new[new]
        if np.array_equal(new, lab):
            break
        lab = new
    _parts, part_of, counts = np.unique(lab, return_inverse=True, return_counts=True)
    cent = np.zeros((len(counts), 3))
    np.add.at(cent, part_of, hp)
    cent /= counts[:, None]
    mid_x = float(np.median(theirs[theirs[:, 2] > hi_t[2] - 0.05, 0]))
    brow = ((cent[:, 1] < nose_t[1] + 0.04) & (cent[:, 2] > nose_t[2] + 0.025) & (cent[:, 2] < nose_t[2] + 0.065)
            & (np.abs(cent[:, 0] - mid_x) < 0.07))  # fmt: skip
    drop = brow[part_of]
    bm = bmesh.new()
    bm.from_mesh(hair.data)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if drop[v.index]], context="VERTS")
    bm.to_mesh(hair.data)
    bm.free()
    pts = np.array([hair.matrix_world @ v.co for v in hair.data.vertices])
    pts = (pts - anchor_t) * scale + anchor_o
    tree = BVHTree.FromObject(body, dg)
    inv = np.array(body.matrix_world.inverted())
    fwd = np.array(body.matrix_world)
    pushed = 0
    for i, p in enumerate(pts):
        q = inv[:3, :3] @ p + inv[:3, 3]
        near, normal = (np.array(x) for x in tree.find_nearest(Vector(q))[:2])
        if (q - near) @ normal < 0.001:
            q = near + 0.001 * normal
            pts[i] = fwd[:3, :3] @ q + fwd[:3, 3]
            pushed += 1
    hair.matrix_world = Matrix_identity()
    hair.data.vertices.foreach_set("co", pts.astype(np.float32).ravel())
    hair.data.update()
    scene.collection.objects.link(hair)
    bpy.data.objects.remove(head)
    for o in bpy.data.objects:  # our scalp groom out of the way
        if o.juststage.part == "scalp":
            o.hide_render = True
    hair.data.materials.clear()
    if textured or alpha:
        _vf_card_material(hair, anchor_o - np.array([0.0, 0.0, 0.09]), alpha)  # appends the cards' and the cap's
    else:
        mat = bpy.data.materials.new("vf plain")
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.045, 0.03, 0.022, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.45
        hair.data.materials.append(mat)
    built.setdefault("objects", []).append(hair)
    print("VF HAIR", bust, "scale", np.round(scale, 3), len(pts), "points,", pushed, "pushed out of the skin,",
          int(brow.sum()), "brow cards dropped", flush=True)


HAIR_ATLAS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "hair_atlas"
ATLAS_STRIPS, ATLAS_STRIP_MM, ATLAS_LENGTH_MM, ATLAS_PX_PER_MM = 8, 16.0, 64.0, 16.0


def _groom_arrays(groom) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """The evaluated groom's points (world), curve offsets, point radii and float curve attributes (melanin ...)."""
    cd = groom.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    pos = np.empty(len(cd.points) * 3, np.float32)
    cd.attributes["position"].data.foreach_get("vector", pos)
    mw = np.array(groom.matrix_world)
    pos = pos.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
    offs = np.empty(len(cd.curves) + 1, np.int64)
    cd.curve_offset_data.foreach_get("value", offs)
    rad = np.full(len(cd.points), 0.00004, np.float32)
    if "radius" in cd.attributes:
        cd.attributes["radius"].data.foreach_get("value", rad)
    attrs = {}
    for a in cd.attributes:
        if a.domain == "CURVE" and a.data_type == "FLOAT" and not a.name.startswith("."):
            v = np.empty(len(cd.curves), np.float32)
            a.data.foreach_get("value", v)
            attrs[a.name] = v
    return pos, offs, rad, attrs


def _bake_strips(groom, out: Path) -> Path:
    """Card textures from our OWN strands - the way Unreal's groom-to-cards generator and Strands2Cards make them:
    ATLAS_STRIPS clumps of the evaluated groom (the strands rooted within half a strip of a seed root), each turned
    into its own frame (along its mean root-to-tip, across in the scalp's tangent plane, depth off the scalp), laid side
    by side flat, roots at the top, and rendered from above in Cycles with the groom's own material (Principled Hair)
    under an even white world: colour and coverage (alpha) in one RGBA picture, ATLAS_PX_PER_MM."""
    pos, offs, rad, attrs = _groom_arrays(groom)
    roots = pos[offs[:-1]]
    tips = pos[offs[1:] - 1]
    length = np.linalg.norm(tips - roots, axis=1)
    centre = np.array([np.median(pos[:, 0]), np.median(pos[:, 1]), pos[:, 2].max() - 0.09])
    rng = np.random.default_rng(11)
    long_ = np.where(length > np.percentile(length, 60))[0]  # seeds among the longer strands: a strip shows a length
    w, half = ATLAS_STRIP_MM / 1000.0, ATLAS_STRIP_MM / 2000.0
    pts, rads, sizes, picked = [], [], [], []
    for k, s in enumerate(rng.choice(long_, ATLAS_STRIPS, replace=False)):
        near = np.where(np.linalg.norm(roots - roots[s], axis=1) < half)[0]
        axis = (tips[near] - roots[near]).mean(0)
        axis /= np.linalg.norm(axis)
        nrm = roots[s] - centre
        across = np.cross(axis, nrm)
        across /= np.linalg.norm(across)
        nrm = np.cross(across, axis)
        for j in near:
            p = pos[offs[j]:offs[j + 1]] - roots[s]
            x, y, z = p @ across, p @ axis, p @ nrm
            if np.abs(x).max() > half * 0.95:
                continue
            pts.append(np.stack([x + (k + 0.5) * w - ATLAS_STRIPS * w / 2, -y, z], 1))
            rads.append(rad[offs[j]:offs[j + 1]])
            sizes.append(len(p))
            picked.append(j)
    curves = bpy.data.hair_curves.new("atlas strands")
    curves.add_curves(sizes)
    curves.position_data.foreach_set("vector", np.concatenate(pts).astype(np.float32).ravel())
    r = curves.attributes.get("radius") or curves.attributes.new("radius", "FLOAT", "POINT")
    r.data.foreach_set("value", np.concatenate(rads).astype(np.float32))
    for name, v in attrs.items():
        a = curves.attributes.get(name) or curves.attributes.new(name, "FLOAT", "CURVE")
        a.data.foreach_set("value", v[np.array(picked)].astype(np.float32))
    for m in groom.data.materials:
        curves.materials.append(m)
    scene = bpy.data.scenes.new("hair atlas")
    obj = bpy.data.objects.new("atlas strands", curves)
    scene.collection.objects.link(obj)
    cam_data = bpy.data.cameras.new("atlas camera")
    cam_data.type = "ORTHO"
    W, L = ATLAS_STRIPS * w, ATLAS_LENGTH_MM / 1000.0
    cam_data.ortho_scale = max(W, L)
    cam = bpy.data.objects.new("atlas camera", cam_data)
    cam.location = (0.0, -L / 2, 0.2)
    scene.collection.objects.link(cam)
    scene.camera = cam
    world = bpy.data.worlds.new("atlas white")
    world.color = (1.0, 1.0, 1.0)
    if world.node_tree is not None:
        bg = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
        if bg is not None:
            bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
            bg.inputs["Strength"].default_value = 1.0
    scene.world = world
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 128
    scene.cycles.device = "GPU" if bpy.context.scene.cycles.device == "GPU" else "CPU"
    scene.render.film_transparent = True
    scene.render.resolution_x = int(round(W * 1000 * ATLAS_PX_PER_MM))
    scene.render.resolution_y = int(round(L * 1000 * ATLAS_PX_PER_MM))
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "Standard"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "16"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "colour.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True, scene=scene.name)
    print("ATLAS", len(sizes), "strands in", ATLAS_STRIPS, "strips ->", path, flush=True)
    bpy.data.scenes.remove(scene)
    return path


POLY_HAIR = Path(__file__).resolve().parents[2] / ".dev" / "downloads" / "polytricity_hair_2026-11-09" / "x"
#: Polytricity's "Hair Cards_FBX" (Sketchfab ad1ac6f1..., CC BY 4.0, made with HairStrand Designer): 11 strips on one
#: 4K sheet, each (u0, u1, v0, v1) as its FBX maps them (read 2026-11-09), roots at the top (v1: the RGB mask's green);
#: 0-5 dense, 6-10 sparse fly-aways
POLY_STRIPS = ((0.0, 0.1225, 0.0, 1.0), (0.1225, 0.2130, 0.0, 1.0), (0.2130, 0.2998, 0.0, 1.0), (0.2998, 0.3854, 0.0, 1.0),
               (0.3854, 0.4734, 0.0, 1.0), (0.4734, 0.5609, 0.0, 1.0), (0.5609, 0.6483, 0.3678, 1.0),
               (0.6483, 0.7388, 0.4663, 1.0), (0.7388, 0.8275, 0.4411, 1.0), (0.8275, 0.9087, 0.4996, 1.0),
               (0.9087, 1.0, 0.1935, 0.9663))  # fmt: skip


def _poly_card_material(melanin: float, redness: float) -> bpy.types.Material:
    """The cards with an artist's strand textures (POLY_HAIR) and OUR hair model (`hair_shading.build`, along the card's
    V on the "poly" UV map): coverage from the strips' mask; colour the strands' own melanin stand-in x the strips' tone
    (the RGB mask's red), darker at the root (green), lighter at the tip (blue), x their occlusion (AO)."""
    groom = importlib.import_module("bl_ext.system.juststage.modules.hair.groom")
    hs = importlib.import_module("bl_ext.system.juststage.modules.hair.hair_shading")
    m = -math.log(max(1.0 - melanin, 1e-4))
    eu, pheo = m * (1.0 - redness), m * redness
    s = groom._roughness_scale(hs.ROUGHNESS) * groom.LIVE_EXPONENT
    stand_in = [max(math.exp(-math.sqrt(pheo * p + eu * e) * s), groom.LIVE_FLOOR)
                for e, p in zip(groom.EUMELANIN, groom.PHEOMELANIN, strict=True)]
    mat = bpy.data.materials.new("vf cards (Polytricity strands, our model)")
    nt = mat.node_tree
    for node in [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]:
        nt.nodes.remove(node)
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "poly"

    def tex(name):
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images.load(str(POLY_HAIR / "textures" / f"HSD_Skecthfab_{name}.png"), check_existing=True)
        node.image.colorspace_settings.name = "Non-Color"
        node.interpolation = "Cubic"
        nt.links.new(uv.outputs["UV"], node.inputs["Vector"])
        return node

    def math_node(op, a, b, c=None):
        node = nt.nodes.new("ShaderNodeMath")
        node.operation = op
        for i, value in enumerate((a, b, c)):
            if value is None:
                continue
            if isinstance(value, float):
                node.inputs[i].default_value = value
            else:
                nt.links.new(value, node.inputs[i])
        return node.outputs[0]

    mask, rgb, ao = tex("Mask"), tex("RGBMask"), tex("AO")
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(rgb.outputs["Color"], sep.inputs["Color"])
    # tone 0.75-1.25, root x0.7, tip x1.25, occlusion x(0.35-1)
    gain = math_node("MULTIPLY_ADD", sep.outputs["Red"], 0.5, 0.75)
    gain = math_node("MULTIPLY", gain, math_node("MULTIPLY_ADD", sep.outputs["Green"], -0.3, 1.0))
    gain = math_node("MULTIPLY", gain, math_node("MULTIPLY_ADD", sep.outputs["Blue"], 0.25, 1.0))
    ao_bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(ao.outputs["Color"], ao_bw.inputs["Color"])
    gain = math_node("MULTIPLY", gain, math_node("MULTIPLY_ADD", ao_bw.outputs["Val"], 0.65, 0.35))
    colour = nt.nodes.new("ShaderNodeVectorMath")
    colour.operation = "SCALE"
    colour.inputs[0].default_value = stand_in
    nt.links.new(gain, colour.inputs["Scale"])
    shader = hs.build(nt, colour.outputs["Vector"], world_mean=hs.world_mean(bpy.context.scene))
    tan_u = nt.nodes.new("ShaderNodeTangent")
    tan_u.direction_type, tan_u.uv_map = "UV_MAP", "poly"
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    along = nt.nodes.new("ShaderNodeVectorMath")
    along.operation = "CROSS_PRODUCT"
    nt.links.new(geo.outputs["Normal"], along.inputs[0])
    nt.links.new(tan_u.outputs["Tangent"], along.inputs[1])
    unit = nt.nodes.new("ShaderNodeVectorMath")
    unit.operation = "NORMALIZE"
    nt.links.new(along.outputs["Vector"], unit.inputs[0])
    intercept = math_node("SUBTRACT", 1.0, sep.outputs["Green"])  # 0 at the root
    for node in list(nt.nodes):
        if node.type == "NEW_GEOMETRY" and node is not geo:
            for link in list(node.outputs["Tangent"].links):
                nt.links.new(unit.outputs["Vector"], link.to_socket)
        if node.type == "HAIR_INFO":
            for link in list(node.outputs["Intercept"].links):
                nt.links.new(intercept, link.to_socket)
    clear = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mask.outputs["Color"], mix.inputs["Fac"])
    nt.links.new(clear.outputs[0], mix.inputs[1])
    nt.links.new(shader, mix.inputs[2])
    nt.links.new(mix.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL").inputs["Surface"])
    mat.surface_render_method = "DITHERED"
    return mat


def _cap_material(hair, cap_mode: str, melanin: float, redness: float, fade_mm: float = 15.0) -> bpy.types.Material:
    """The cut's base cap (its largest loose part, material slot 1): "off" - transparent; "fade" - the hair's dark
    under-colour, fading out over `fade_mm` from the cap's own edge (its open border), so the hairline and the nape end
    in skin, not in a painted band (21:0x: the cap showed as a solid band across our lower forehead and the nape)."""
    import bmesh

    mat = bpy.data.materials.new(f"vf cap ({cap_mode})")
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    bsdf = nt.nodes.get("Principled BSDF")
    clear = nt.nodes.new("ShaderNodeBsdfTransparent")
    if cap_mode == "off":
        nt.links.new(clear.outputs[0], out.inputs["Surface"])
        mat.surface_render_method = "DITHERED"
        return mat
    me = hair.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    cap = {f.index for f in bm.faces if f.material_index == 1}
    cap_verts = {v.index for i in cap for v in bm.faces[i].verts}
    border = {v.index for e in bm.edges if e.is_boundary for v in e.verts if v.index in cap_verts}
    dist = np.full(len(bm.verts), np.inf)
    import heapq

    heap = [(0.0, i) for i in border]
    for i in border:
        dist[i] = 0.0
    while heap:  # the distance along the cap from its edge (Dijkstra over its edges)
        d, i = heapq.heappop(heap)
        if d > dist[i]:
            continue
        v = bm.verts[i]
        for e in v.link_edges:
            o = e.other_vert(v)
            if o.index not in cap_verts:
                continue
            nd = d + e.calc_length()
            if nd < dist[o.index]:
                dist[o.index] = nd
                heapq.heappush(heap, (nd, o.index))
    bm.free()
    inside = np.clip(np.where(np.isfinite(dist), dist, 1.0) / (fade_mm / 1000.0), 0.0, 1.0).astype(np.float32)
    attr = me.attributes.get("vf_cap_in") or me.attributes.new("vf_cap_in", "FLOAT", "POINT")
    attr.data.foreach_set("value", inside)
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "vf_cap_in"
    groom = importlib.import_module("bl_ext.system.juststage.modules.hair.groom")
    hs = importlib.import_module("bl_ext.system.juststage.modules.hair.hair_shading")
    m = -math.log(max(1.0 - melanin, 1e-4))
    eu, pheo = m * (1.0 - redness), m * redness
    sc = groom._roughness_scale(hs.ROUGHNESS) * groom.LIVE_EXPONENT
    under = [0.5 * max(math.exp(-math.sqrt(pheo * p + eu * e) * sc), groom.LIVE_FLOOR)
             for e, p in zip(groom.EUMELANIN, groom.PHEOMELANIN, strict=True)]
    bsdf.inputs["Base Color"].default_value = (*under, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6
    if cap_mode == "strands":  # short hair on the cap: stretched noise down the head, our hair model along it
        coords = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (2600.0, 2600.0, 160.0)  # ~0.4 mm across, ~6 mm along, per metre
        nt.links.new(coords.outputs["Object"], mapping.inputs["Vector"])
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value, noise.inputs["Detail"].default_value = 1.0, 2.0
        nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        cut = nt.nodes.new("ShaderNodeMapRange")
        cut.inputs["From Min"].default_value, cut.inputs["From Max"].default_value = 0.42, 0.56  # denser
        nt.links.new(noise.outputs["Fac"], cut.inputs["Value"])
        shade = nt.nodes.new("ShaderNodeVectorMath")
        shade.operation = "SCALE"
        shade.inputs[0].default_value = [1.2 * c for c in under]  # darker than the top (under is half its colour)
        # darker toward the cap's own edge and in the gaps: the cut's under-hair, not ginger fuzz on skin
        nt.links.new(_mul(nt, _mul(nt, noise.outputs["Fac"], 1.2), at.outputs["Fac"]), shade.inputs["Scale"])
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        down = nt.nodes.new("ShaderNodeVectorMath")  # the head's down laid onto the surface: d - (d.n) n
        down.operation = "PROJECT"
        down.inputs[0].default_value = (0.0, 0.0, -1.0)
        nt.links.new(geo.outputs["Normal"], down.inputs[1])
        along = nt.nodes.new("ShaderNodeVectorMath")
        along.operation = "SUBTRACT"
        along.inputs[0].default_value = (0.0, 0.0, -1.0)
        nt.links.new(down.outputs["Vector"], along.inputs[1])
        unit = nt.nodes.new("ShaderNodeVectorMath")
        unit.operation = "NORMALIZE"
        nt.links.new(along.outputs["Vector"], unit.inputs[0])
        hair_shader = hs.build(nt, shade.outputs["Vector"], world_mean=hs.world_mean(bpy.context.scene))
        for node in list(nt.nodes):
            if node.type == "NEW_GEOMETRY" and node is not geo:
                for link in list(node.outputs["Tangent"].links):
                    nt.links.new(unit.outputs["Vector"], link.to_socket)
            if node.type == "HAIR_INFO":
                for link in list(node.outputs["Intercept"].links):
                    nt.links.new(noise.outputs["Fac"], link.to_socket)
        # not across the forehead: the cap's front (its normal facing forward, -Y) out - the face's hairline is the
        # cards' (22:5x: a pale band of fuzz across the forehead)
        front = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Normal"], front.inputs[0])
        not_front = nt.nodes.new("ShaderNodeMapRange")
        not_front.inputs["From Min"].default_value, not_front.inputs["From Max"].default_value = -0.75, -0.35
        nt.links.new(front.outputs["Y"], not_front.inputs["Value"])
        cover = _mul(nt, _mul(nt, cut.outputs["Result"], at.outputs["Fac"]), not_front.outputs["Result"])
        # the gaps: the dark under-colour (the scalp seen through clipped hair), fading with the cap - not bare skin
        # (22:53: skin between the strands read orange at the nape)
        gaps = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(_mul(nt, _mul(nt, at.outputs["Fac"], not_front.outputs["Result"]), 0.75), gaps.inputs["Fac"])
        nt.links.new(clear.outputs[0], gaps.inputs[1])
        nt.links.new(bsdf.outputs["BSDF"], gaps.inputs[2])
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(cover, mix.inputs["Fac"])
        nt.links.new(gaps.outputs[0], mix.inputs[1])
        nt.links.new(hair_shader, mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        mat.surface_render_method = "DITHERED"
        print("VF CAP strands, fading", fade_mm, "mm,", len(border), "edge points", flush=True)
        return mat
    ramp = nt.nodes.new("ShaderNodeMath")
    ramp.operation = "POWER"
    nt.links.new(at.outputs["Fac"], ramp.inputs[0])
    ramp.inputs[1].default_value = 1.5
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(ramp.outputs[0], mix.inputs["Fac"])
    nt.links.new(clear.outputs[0], mix.inputs[1])
    nt.links.new(bsdf.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "DITHERED"
    print("VF CAP fade", fade_mm, "mm,", len(border), "edge points", flush=True)
    return mat


def _cap_footprint_uvs(hair, body, front: float = -0.2) -> np.ndarray:
    """The cut's base cap (slot 1) on our skin, as hm08 UVs read the way the groom reads them back
    (`lashes.surface_points`: the base mesh's skin triangles - MakeHuman's helpers out - on the shaped coordinates,
    hm08's UVMap): each cap vertex's nearest skin triangle, its UV by barycentric weights - kept where the skin there
    doesn't face forward (the triangle normal's y over `front`: the sides, the back, the nape), so no short hair lands
    on the forehead. (From the evaluated mesh's UVs the roots landed on the chest and the arm, 2026-11-09.)"""
    from mathutils import Vector, geometry
    from mathutils.bvhtree import BVHTree

    lashes = importlib.import_module("bl_ext.system.juststage.modules.hair.lashes")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    groom = importlib.import_module("bl_ext.system.juststage.modules.hair.groom")
    tris, loops = lashes._triangles(body)
    uv = np.empty(len(body.data.loops) * 2, np.float32)
    body.data.uv_layers[groom.SURFACE_UV].data.foreach_get("uv", uv)
    tri_uv = uv.reshape(-1, 2)[loops]
    mw = np.array(body.matrix_world)
    now = build.shaped_coords(body) @ mw[:3, :3].T + mw[:3, 3]
    tree = BVHTree.FromPolygons([Vector(c) for c in now], [tuple(t) for t in tris])
    me = hair.data
    cap_v = sorted({v for poly in me.polygons if poly.material_index == 1 for v in poly.vertices})
    out = []
    for i in cap_v:
        p = hair.matrix_world @ me.vertices[i].co
        hit, normal, index, _d = tree.find_nearest(p)
        if hit is None or normal.normalized().y < front:
            continue
        a, b, c = (Vector(now[j]) for j in tris[index])
        ua, ub, uc = (Vector((*tri_uv[index][k], 0.0)) for k in range(3))
        w = geometry.barycentric_transform(hit, a, b, c, ua, ub, uc)
        out.append((w.x, w.y))
    print("VF CAP FOOTPRINT", len(out), "of", len(cap_v), "cap points as roots (off the front)", flush=True)
    return np.array(out, np.float64).reshape(-1, 2)


def browpoly(built: dict, width_mm: float = 1.6, gap_mm: float = 0.9, tips: float = 0.5) -> None:
    """The brows as cards (CC5's way: its brows are cards with a strand texture) along our own brow strands: strands
    picked so no two roots lie within `gap_mm`, each a ribbon `width_mm` wide lying on the skin, mapped onto a dense
    Polytricity strip's lower `tips` share (the fine, separated ends - a brow hair is ~10 mm), in our hair model at the
    brows' own melanin; the strand brows hidden. --alone."""
    brows = importlib.import_module("bl_ext.system.juststage.modules.hair.brows")
    groom = next(o for o in bpy.data.objects if o.type == "CURVES" and o.juststage.part == "eyebrows"
                 and o.juststage.part_of == built["body"].juststage.character_id)
    pos, offs, _rad, attrs = _groom_arrays(groom)
    roots = pos[offs[:-1]]
    rng = np.random.default_rng(13)
    gap = gap_mm / 1000.0
    cells: dict = {}
    picked = []
    for k in rng.permutation(len(roots)):
        c = tuple((roots[k] // gap).astype(int))
        near = [j for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
                for j in cells.get((c[0] + dx, c[1] + dy, c[2] + dz), ())]
        if any(np.linalg.norm(roots[k] - roots[j]) < gap for j in near):
            continue
        cells.setdefault(c, []).append(k)
        picked.append(k)
    centre = np.median(roots, axis=0) + np.array([0.0, 0.08, 0.0])  # ~8 cm behind the brows (the face looks -Y)
    verts, faces, uvs = [], [], []
    for k in picked:
        q = pos[offs[k]:offs[k + 1]]
        if len(q) < 3:
            continue
        tan = np.gradient(q, axis=0)
        tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-9)
        side = np.cross(tan, q - centre)
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-9)
        n = len(q)
        half = side * (width_mm / 2000.0) * np.linspace(1.0, 0.5, n)[:, None]
        strip = rng.integers(0, 6)
        u0, u1, v0, v1 = POLY_STRIPS[strip]
        x0 = u0 + rng.uniform(0.1, 0.6) * (u1 - u0)
        du = 0.3 * (u1 - u0)
        base = len(verts)
        for i in range(n):
            verts.append(q[i] - half[i])
            verts.append(q[i] + half[i])
            v = v0 + tips * (v1 - v0) * (1.0 - i / (n - 1))  # the strip's lower share, root to tip down it
            uvs.append((x0, v))
            uvs.append((x0 + du, v))
        for i in range(n - 1):
            a = base + 2 * i
            faces.append((a, a + 1, a + 3, a + 2))
    me = bpy.data.meshes.new("brow cards")
    me.from_pydata([tuple(v) for v in verts], [], faces)
    layer = me.uv_layers.new(name="poly")
    loop_v = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loop_v)
    layer.data.foreach_set("uv", np.array(uvs, np.float32)[loop_v].ravel())
    obj = bpy.data.objects.new("brow cards", me)
    bpy.context.scene.collection.objects.link(obj)
    melanin = float(np.median(attrs["melanin"])) if "melanin" in attrs else brows.MELANIN
    redness = float(np.median(attrs["redness"])) if "redness" in attrs else brows.REDNESS
    me.materials.append(_poly_card_material(melanin, redness))
    groom.hide_render = True
    built.setdefault("objects", []).append(obj)
    print("BROW CARDS", len(faces), "quads on", len(picked), "of", len(roots), "strands,", width_mm, "mm, melanin",
          round(melanin, 3), flush=True)


def vfpoly(built: dict, bust: str, fly: float = 0.2, cap_mode: str = "") -> None:
    """The free cut's own cards (VincentFreelance, CC BY 4.0 - an artist's layout, its textures not free) with an
    artist's free strand textures (Polytricity's "Hair Cards_FBX", CC BY 4.0 - 4K strips: mask, root / tip / tone, AO)
    and our hair model: each card a random strip at its own length along the strip (`vf_t`, root at the strip's top) and
    across it (`vf_s`), `fly` of them a sparse fly-away strip. The two free halves of a card groom together. --alone."""
    vfhair(built, bust, textured=True)
    hair = next(o for o in bpy.data.objects if o.name.startswith(f"vf_hair_{bust}"))
    me = hair.data
    n = len(me.vertices)
    t, s, part = np.empty(n, np.float32), np.empty(n, np.float32), np.empty(n, np.int32)
    me.attributes["vf_t"].data.foreach_get("value", t)
    me.attributes["vf_s"].data.foreach_get("value", s)
    me.attributes["vf_part"].data.foreach_get("value", part)
    rng = np.random.default_rng(9)
    parts = int(part.max()) + 1
    dense = rng.integers(0, 6, parts)
    sparse = rng.integers(6, 11, parts)
    strip = np.where(rng.random(parts) < fly, sparse, dense)[part]
    rect = np.array(POLY_STRIPS, np.float32)[strip]
    margin = 0.06
    across = margin + (s * 0.5 + 0.5) * (1.0 - 2 * margin)
    u = rect[:, 0] + across * (rect[:, 1] - rect[:, 0])
    v = rect[:, 3] - np.clip(t, 0.0, 1.0) * (rect[:, 3] - rect[:, 2])
    layer = me.uv_layers.get("poly") or me.uv_layers.new(name="poly")
    loop_v = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loop_v)
    layer.data.foreach_set("uv", np.stack([u, v], 1)[loop_v].astype(np.float32).ravel())
    me.materials[0] = _poly_card_material(pg.SCALP_COLOUR["melanin"], pg.SCALP_COLOUR["redness"])
    if cap_mode and len(me.materials) > 1:
        me.materials[1] = _cap_material(hair, "off" if cap_mode in ("buzz", "capbuzz") else cap_mode, pg.SCALP_COLOUR["melanin"],
                                        pg.SCALP_COLOUR["redness"])
    if cap_mode in ("buzz", "capbuzz"):  # the short sides and nape: our own short strands under the cards
        scalp = importlib.import_module("bl_ext.system.juststage.modules.hair.scalp")
        scalp.STYLES["trial buzz"] = {"lengths": ((-0.4, 5.0), (0.0, 6.0), (0.35, 8.0), (0.7, 10.0)), "lift": (1.0, 0.5),
                                      "sweep": 0.1, "frizz": 0.0004, "noise": 0.0008, "clump": 0.05,
                                      "flow_down": 0.35, "side_down": 0.4}  # fmt: skip
        brows = importlib.import_module("bl_ext.system.juststage.modules.hair.brows")
        old_region = brows.region_uvs
        if cap_mode == "capbuzz":  # roots: MakeHuman's region + the cap's footprint off the front
            extra = _cap_footprint_uvs(hair, built["body"])
            brows.region_uvs = lambda style=brows.STYLE, _o=old_region, _e=extra: np.concatenate([_o(style), _e])
            # the scalp mask is made once and the fill group (cached by name) holds it: removing it left the fill
            # unmasked - strands over the whole body (21:3x, 22:1x, 22:3x). Made again from these roots and its pixels
            # written into the image the group holds.
            mask = bpy.data.images.get("JustStage scalp mask")
            if mask is not None:
                mask.name = "JustStage scalp mask (held)"
                fresh = scalp.scalp_mask(built["body"])
                px = np.empty(len(fresh.pixels), np.float32)
                fresh.pixels.foreach_get(px)
                mask.pixels.foreach_set(px)
                mask.pack()
                bpy.data.images.remove(fresh)
                mask.name = "JustStage scalp mask"
                print("VF CAP MASK made again: covered", round(float((px[0::4] > 0.25).mean()), 4), flush=True)
        try:
            buzz = scalp.make(built["body"], "trial buzz")  # replaces the character's scalp groom (removed)
        finally:
            brows.region_uvs = old_region
        pg.colour_scalp(buzz)
        buzz.hide_render = False

        def alive(o):
            try:
                return bool(o.name)
            except ReferenceError:
                return False

        built["objects"] = [o for o in built.get("objects", []) if alive(o)] + [buzz]
    print("VF POLY", bust, parts, "cards on Polytricity's strips,", f"{fly:.0%} fly-aways, cap", cap_mode or "as cut",
          flush=True)


def vfbake(built: dict, bust: str, count: int = 6000, width_mm: float = 7.0) -> None:
    """Hair cards along our own strands (`vfguides`: grown from the free cut's cards) carrying a texture baked from
    those same strands (`_bake_strips`) - the plan's Cards row ("our own baker on Strands2Cards' published method"),
    tried 2026-11-09 after the CC0 sheets read scaly. Each card a random strip of the atlas at true scale (its width a
    `width_mm` slice of the strip's ATLAS_STRIP_MM, its length the strand's own arc length), colour and coverage from
    the atlas; the strand groom hidden. A new groom: --alone."""
    vfguides(built, bust)
    groom = next(o for o in bpy.data.objects if o.juststage.part == "scalp" and o.type == "CURVES")
    atlas = _bake_strips(groom, HAIR_ATLAS / bust)
    pos, offs, _rad, _a = _groom_arrays(groom)
    rng = np.random.default_rng(3)
    pick = rng.choice(len(offs) - 1, min(count, len(offs) - 1), replace=False)
    centre = np.array([np.median(pos[:, 0]), np.median(pos[:, 1]), pos[:, 2].max() - 0.09])
    du = width_mm / (ATLAS_STRIPS * ATLAS_STRIP_MM)
    verts, faces, uvs = [], [], []
    for k in pick:
        p = pos[offs[k]:offs[k + 1]]
        if len(p) < 3:
            continue
        tan = np.gradient(p, axis=0)
        tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-9)
        side = np.cross(tan, p - centre)
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-9)
        n = len(p)
        half = side * (width_mm / 2000.0) * np.linspace(1.0, 0.55, n)[:, None]
        s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]) * 1000.0
        strip = rng.integers(ATLAS_STRIPS)
        x0 = (strip + rng.uniform(0.05, 0.95 - width_mm / ATLAS_STRIP_MM)) / ATLAS_STRIPS
        base = len(verts)
        for i in range(n):
            verts.append(p[i] - half[i])
            verts.append(p[i] + half[i])
            v = max(1.0 - s[i] / ATLAS_LENGTH_MM, 0.0)  # the atlas's roots at its top, at true length
            uvs.append((x0, v))
            uvs.append((x0 + du, v))
        for i in range(n - 1):
            a = base + 2 * i
            faces.append((a, a + 1, a + 3, a + 2))
    me = bpy.data.meshes.new("baked cards")
    me.from_pydata([tuple(v) for v in verts], [], faces)
    uv_layer = me.uv_layers.new(name="UVMap")
    loop_v = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loop_v)
    uv_layer.data.foreach_set("uv", np.array(uvs, np.float32)[loop_v].ravel())
    obj = bpy.data.objects.new("baked cards", me)
    bpy.context.scene.collection.objects.link(obj)
    mat = bpy.data.materials.new("baked cards")
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(atlas), check_existing=False)
    img.interpolation = "Cubic"
    nt.links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(img.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.42
    mat.surface_render_method = "DITHERED"
    me.materials.append(mat)
    groom.hide_render = True
    built.setdefault("objects", []).append(obj)
    print("VF BAKED CARDS", len(faces), "quads on", len(pick), "strands,", width_mm, "mm", flush=True)


def _hair_card_material(atlas: bpy.types.Image, mean_lum: float, melanin: float, redness: float) -> bpy.types.Material:
    """A card material with OUR hair model - the strands' live-view shading (`hair_shading.build`: Marschner's lobes
    per light, the body, the image light), its strand direction the card's V (the atlas's root-to-tip), its colour
    the strands' own stand-in (groom.py's melanin model) times the atlas's strand-to-strand brightness, its coverage
    the atlas's alpha. The flat Principled cards (round 1) lit each card as one sheet - the scales."""
    groom = importlib.import_module("bl_ext.system.juststage.modules.hair.groom")
    hs = importlib.import_module("bl_ext.system.juststage.modules.hair.hair_shading")
    m = -math.log(max(1.0 - melanin, 1e-4))
    eu, pheo = m * (1.0 - redness), m * redness
    s = groom._roughness_scale(hs.ROUGHNESS) * groom.LIVE_EXPONENT
    stand_in = [max(math.exp(-math.sqrt(pheo * p + eu * e) * s), groom.LIVE_FLOOR)
                for e, p in zip(groom.EUMELANIN, groom.PHEOMELANIN, strict=True)]
    mat = bpy.data.materials.new("hair cards (our model)")
    nt = mat.node_tree
    for node in [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"]:
        nt.nodes.remove(node)
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = atlas  # read as stored (Non-Color), as its mean was
    img.interpolation = "Cubic"
    # the atlas's strand-to-strand brightness, around 1 where it has hair
    lum = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(img.outputs["Color"], lum.inputs["Color"])
    vary = nt.nodes.new("ShaderNodeMath")
    vary.operation = "MULTIPLY"
    nt.links.new(lum.outputs["Val"], vary.inputs[0])
    vary.inputs[1].default_value = 1.0 / max(mean_lum, 1e-3)
    colour = nt.nodes.new("ShaderNodeVectorMath")
    colour.operation = "SCALE"
    colour.inputs[0].default_value = stand_in
    nt.links.new(vary.outputs[0], colour.inputs["Scale"])
    shader = hs.build(nt, colour.outputs["Vector"], world_mean=hs.world_mean(bpy.context.scene))
    # the strand's direction on a card: along its V (cross of the normal and the UV map's U tangent)
    tan_u = nt.nodes.new("ShaderNodeTangent")
    tan_u.direction_type, tan_u.uv_map = "UV_MAP", "UVMap"
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    along = nt.nodes.new("ShaderNodeVectorMath")
    along.operation = "CROSS_PRODUCT"
    nt.links.new(geo.outputs["Normal"], along.inputs[0])
    nt.links.new(tan_u.outputs["Tangent"], along.inputs[1])
    unit = nt.nodes.new("ShaderNodeVectorMath")
    unit.operation = "NORMALIZE"
    nt.links.new(along.outputs["Vector"], unit.inputs[0])
    # root to tip on the card: 1 - V (the atlas's roots at its top), x2 (a strip is 64 mm, our strands ~32)
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "UVMap"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs[0])
    tip = nt.nodes.new("ShaderNodeMath")
    tip.operation, tip.use_clamp = "MULTIPLY_ADD", True
    nt.links.new(sep.outputs["Y"], tip.inputs[0])
    tip.inputs[1].default_value, tip.inputs[2].default_value = -2.0, 2.0
    for node in list(nt.nodes):
        if node.type == "NEW_GEOMETRY" and node is not geo:
            for link in list(node.outputs["Tangent"].links):
                nt.links.new(unit.outputs["Vector"], link.to_socket)
        if node.type == "HAIR_INFO":
            for link in list(node.outputs["Intercept"].links):
                nt.links.new(tip.outputs[0], link.to_socket)
    clear = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(img.outputs["Alpha"], mix.inputs["Fac"])
    nt.links.new(clear.outputs[0], mix.inputs[1])
    nt.links.new(shader, mix.inputs[2])
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    mat.surface_render_method = "DITHERED"
    return mat


def vfbake2(built: dict, bust: str, card_mm: float = 12.0, spacing: float = 0.5) -> None:
    """Round 2 of the cards textured from our own strands (`vfbake`: scales): fewer, wider cards - one a clump,
    `card_mm` wide, their roots at least `spacing` x card_mm apart (the way an artist lays a card per clump) - each a
    strip of the atlas at true scale, shaded with our hair model along the card (`_hair_card_material`). --alone."""
    vfguides(built, bust)
    groom = next(o for o in bpy.data.objects if o.juststage.part == "scalp" and o.type == "CURVES")
    atlas = bpy.data.images.load(str(_bake_strips(groom, HAIR_ATLAS / bust)), check_existing=False)
    atlas.colorspace_settings.name = "Non-Color"
    px = np.empty(atlas.size[0] * atlas.size[1] * 4, np.float32)
    atlas.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    mean_lum = float((px[px[:, 3] > 0.5, :3] @ np.array([0.2126, 0.7152, 0.0722], np.float32)).mean())
    pos, offs, _rad, attrs = _groom_arrays(groom)
    roots = pos[offs[:-1]]
    rng = np.random.default_rng(5)
    gap = spacing * card_mm / 1000.0
    cells: dict = {}
    picked = []
    for k in rng.permutation(len(roots)):  # roots spread: none closer than `gap` to one taken (a dart throw on a grid)
        c = tuple((roots[k] // gap).astype(int))
        near = [j for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
                for j in cells.get((c[0] + dx, c[1] + dy, c[2] + dz), ())]
        if any(np.linalg.norm(roots[k] - roots[j]) < gap for j in near):
            continue
        cells.setdefault(c, []).append(k)
        picked.append(k)
    centre = np.array([np.median(pos[:, 0]), np.median(pos[:, 1]), pos[:, 2].max() - 0.09])
    du = card_mm / (ATLAS_STRIPS * ATLAS_STRIP_MM)
    verts, faces, uvs = [], [], []
    for k in picked:
        p = pos[offs[k]:offs[k + 1]]
        if len(p) < 3:
            continue
        tan = np.gradient(p, axis=0)
        tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-9)
        side = np.cross(tan, p - centre)
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-9)
        n = len(p)
        half = side * (card_mm / 2000.0) * np.linspace(1.0, 0.6, n)[:, None]
        s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]) * 1000.0
        strip = rng.integers(ATLAS_STRIPS)
        x0 = (strip + rng.uniform(0.02, max(0.03, 0.98 - card_mm / ATLAS_STRIP_MM))) / ATLAS_STRIPS
        base = len(verts)
        for i in range(n):
            verts.append(p[i] - half[i])
            verts.append(p[i] + half[i])
            v = max(1.0 - s[i] / ATLAS_LENGTH_MM, 0.0)
            uvs.append((x0, v))
            uvs.append((x0 + du, v))
        for i in range(n - 1):
            a = base + 2 * i
            faces.append((a, a + 1, a + 3, a + 2))
    me = bpy.data.meshes.new("clump cards")
    me.from_pydata([tuple(v) for v in verts], [], faces)
    uv_layer = me.uv_layers.new(name="UVMap")
    loop_v = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loop_v)
    uv_layer.data.foreach_set("uv", np.array(uvs, np.float32)[loop_v].ravel())
    obj = bpy.data.objects.new("clump cards", me)
    bpy.context.scene.collection.objects.link(obj)
    melanin = float(np.median(attrs["melanin"])) if "melanin" in attrs else pg.SCALP_COLOUR["melanin"]
    redness = float(np.median(attrs["redness"])) if "redness" in attrs else pg.SCALP_COLOUR["redness"]
    me.materials.append(_hair_card_material(atlas, mean_lum, melanin, redness))
    groom.hide_render = True
    built.setdefault("objects", []).append(obj)
    print("VF CLUMP CARDS", len(faces), "quads on", len(picked), "cards,", card_mm, "mm, melanin", round(melanin, 3),
          flush=True)


def vfcards(built: dict, bust: str, count: int = 6000, width_mm: float = 7.0, sheet: str = "hair02") -> None:
    """Hair cards the way CC5 and MetaHuman make them - flat strips carrying a strand texture - built along our own
    strands (`vfguides`: grown from the free cut's cards, so the artist's shape): `count` of the groom's strands each a
    ribbon `width_mm` wide, turned to lie on the head, its UV across the strip and along it, the strip a narrow random
    slice of a CC0 strand sheet (OpenGameArt "Hair Alphas For Days", `sheet`: roots at its top); the strand groom
    hidden. Q-HAIR-7's approved live-view route with its gap filled (the cut ours, the alphas CC0). A new groom: --alone."""
    vfguides(built, bust)
    groom = next(o for o in bpy.data.objects if o.juststage.part == "scalp" and o.type == "CURVES")
    dg = bpy.context.evaluated_depsgraph_get()
    cd = groom.evaluated_get(dg).data
    pos = np.empty(len(cd.points) * 3, np.float32)
    cd.attributes["position"].data.foreach_get("vector", pos)
    pos = pos.reshape(-1, 3)
    offs = np.empty(len(cd.curves) + 1, np.int64)
    cd.curve_offset_data.foreach_get("value", offs)
    mw = np.array(groom.matrix_world)
    pos = pos @ mw[:3, :3].T + mw[:3, 3]
    rng = np.random.default_rng(3)
    pick = rng.choice(len(offs) - 1, min(count, len(offs) - 1), replace=False)
    centre = np.array([np.median(pos[:, 0]), np.median(pos[:, 1]), pos[:, 2].max() - 0.09])
    verts, faces, uvs, quad_uv = [], [], [], []
    for k in pick:
        p = pos[offs[k]:offs[k + 1]]
        if len(p) < 3:
            continue
        tan = np.gradient(p, axis=0)
        tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-9)
        radial = p - centre
        side = np.cross(tan, radial)
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-9)
        n = len(p)
        taper = np.linspace(1.0, 0.55, n)[:, None]
        half = side * (width_mm / 2000.0) * taper
        base = len(verts)
        x0 = rng.uniform(0.12, 0.62)  # the strip's slice of the sheet
        for i in range(n):
            verts.append(p[i] - half[i])
            verts.append(p[i] + half[i])
            v = 1.0 - 0.72 * i / (n - 1)  # the sheet's roots at its top
            uvs.append((x0, v))
            uvs.append((x0 + 0.16, v))
        for i in range(n - 1):
            a = base + 2 * i
            faces.append((a, a + 1, a + 3, a + 2))
    me = bpy.data.meshes.new("vf cards")
    me.from_pydata([tuple(v) for v in verts], [], faces)
    uv_layer = me.uv_layers.new(name="UVMap")
    loop_v = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loop_v)
    uv_arr = np.array(uvs, np.float32)[loop_v]
    uv_layer.data.foreach_set("uv", uv_arr.ravel())
    obj = bpy.data.objects.new("vf cards", me)
    bpy.context.scene.collection.objects.link(obj)
    mat = bpy.data.materials.new("vf cards")
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(OGA_ALPHAS / f"{sheet}.png"), check_existing=True)
    nt.links.new(img.outputs["Alpha"], bsdf.inputs["Alpha"])
    shade = nt.nodes.new("ShaderNodeMix")  # the sheet's own strand brightness into a brown, darker in its gaps
    shade.data_type = "RGBA"
    nt.links.new(img.outputs["Color"], shade.inputs["Factor"])
    next(i for i in shade.inputs if i.identifier == "A_Color").default_value = (0.018, 0.012, 0.009, 1.0)
    next(i for i in shade.inputs if i.identifier == "B_Color").default_value = (0.085, 0.06, 0.042, 1.0)
    nt.links.new(next(o for o in shade.outputs if o.identifier == "Result_Color"), bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.42
    mat.surface_render_method = "DITHERED"
    me.materials.append(mat)
    groom.hide_render = True
    built.setdefault("objects", []).append(obj)
    print("VF CARDS (ours)", len(faces), "quads on", len(pick), "strands,", width_mm, "mm,", sheet, flush=True)


def vfguides(built: dict, bust: str, fill_gap: float = 0.012) -> None:
    """Our scalp groom (`scalp.make`, Blender's Interpolate Hair Curves and shaping) grown from the free cut's cards as
    its guide curves (2026-11-09): the cut fitted as `vfhair` does, each card (not its base cap) a guide - its points
    ordered root (the end nearer the head's centre) to tip, resampled to the groom's point count, its root seated on
    our skin - so the strands take the artist's shape: the cards' look (sculpted, glossy without the creator's
    textures) out, our strands' look in. A new groom: --alone."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    scalp = importlib.import_module("bl_ext.system.juststage.modules.hair.scalp")
    vfhair(built, bust)  # the fitted cut, linked (plain), our scalp groom hidden
    hair = next(o for o in bpy.data.objects if o.name.startswith(f"vf_hair_{bust}"))
    body = built["body"]
    co = np.array([hair.matrix_world @ v.co for v in hair.data.vertices])
    ed = np.array([e.vertices for e in hair.data.edges])
    lab = np.arange(len(co))
    while True:
        mn = np.minimum(lab[ed[:, 0]], lab[ed[:, 1]])
        new = lab.copy()
        np.minimum.at(new, ed[:, 0], mn)
        np.minimum.at(new, ed[:, 1], mn)
        new = new[new]
        if np.array_equal(new, lab):
            break
        lab = new
    labels, counts = np.unique(lab, return_counts=True)
    cap = labels[np.argmax(counts)]
    dg = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(body, dg)
    inv, fwd = np.array(body.matrix_world.inverted()), np.array(body.matrix_world)
    top = co[:, 2].max()
    centre = np.array([np.median(co[:, 0]), np.median(co[:, 1]), top - 0.09])
    n_pts = scalp.POINTS
    out = []
    for label, count in zip(labels, counts, strict=True):
        if label == cap or count < 4:
            continue
        pts = co[lab == label]
        c = pts.mean(0)
        _u, _sv, vt = np.linalg.svd(pts - c, full_matrices=False)
        t = (pts - c) @ vt[0]
        if np.linalg.norm(pts[np.argmax(t)] - centre) < np.linalg.norm(pts[np.argmin(t)] - centre):
            t = -t
        edges_t = np.linspace(t.min(), t.max(), n_pts + 1)
        line = []
        for k in range(n_pts):
            sel = (t >= edges_t[k]) & (t <= edges_t[k + 1])
            line.append(pts[sel].mean(0) if sel.any() else c + vt[0] * (edges_t[k] + edges_t[k + 1]) / 2)
        line = np.array(line)
        q = inv[:3, :3] @ line[0] + inv[:3, 3]  # the root seated on our skin, the curve moved with it
        near = np.array(tree.find_nearest(Vector(q))[0])
        line += (fwd[:3, :3] @ near + fwd[:3, 3]) - line[0]
        out.append(line)
    bpy.data.objects.remove(hair)
    # the sides and the nape - the cut's cap covered them, no card does - from our own style's guides: each kept
    # where no card root lies within FILL_GAP
    own = scalp.guides(body, scalp.STYLES["short taper"], 5)
    card_roots = np.array([g[0] for g in out])
    kept = [g for g in own if np.min(np.linalg.norm(card_roots - g[0], axis=1)) > fill_gap]
    out = out + kept
    print("VF GUIDES", len(card_roots), "from cards +", len(kept), "of our own", len(own), "where no card is near",
          flush=True)
    old = scalp.guides
    scalp.guides = lambda *_a, **_k: out
    try:
        groom = scalp.make(body, "short taper")
    finally:
        scalp.guides = old
    pg.colour_scalp(groom)
    groom.hide_render = False
    cid = body.juststage.character_id
    built["objects"] = [o for o in bpy.context.scene.objects if cid in (o.juststage.character_id, o.juststage.part_of)]
    print("VF GUIDES", bust, len(out), "guides from the cut's cards", flush=True)


def _vf_card_material(hair, head_centre, alpha_name: str = "") -> bpy.types.Material:
    """Each card's own length (vf_t, 0 at the root) and width (vf_s) as attributes, and a card material from them: strands
    along the card (a stretched noise), alpha-cut, faded at the tip and the edges; brown, darker at the root."""
    me = hair.data
    n = len(me.vertices)
    co = np.empty(n * 3, np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    ed = np.empty(len(me.edges) * 2, np.int64)
    me.edges.foreach_get("vertices", ed)
    ed = ed.reshape(-1, 2)
    lab = np.arange(n)
    while True:  # each card a loose part (label propagation with pointer jumping)
        m = np.minimum(lab[ed[:, 0]], lab[ed[:, 1]])
        new = lab.copy()
        np.minimum.at(new, ed[:, 0], m)
        np.minimum.at(new, ed[:, 1], m)
        new = new[new]
        if np.array_equal(new, lab):
            break
        lab = new
    t = np.zeros(n, np.float32)
    w = np.zeros(n, np.float32)
    for part in np.unique(lab):
        idx = np.where(lab == part)[0]
        if len(idx) < 3:  # a stray point or edge: no card
            continue
        pts = co[idx]
        c = pts.mean(0)
        _u, _sv, vt = np.linalg.svd(pts - c, full_matrices=False)
        along, across = (pts - c) @ vt[0], (pts - c) @ vt[1]
        if np.linalg.norm(pts[np.argmax(along)] - head_centre) < np.linalg.norm(pts[np.argmin(along)] - head_centre):
            along = -along  # the root (the end nearer the head) at 0
        span = max(along.max() - along.min(), 1e-6)
        t[idx] = (along - along.min()) / span
        half = max(np.abs(across).max(), 1e-6)
        w[idx] = across / half
    for name, values in (("vf_t", t), ("vf_s", w)):
        attr = me.attributes.get(name) or me.attributes.new(name, "FLOAT", "POINT")
        attr.data.foreach_set("value", values)
    part = me.attributes.get("vf_part") or me.attributes.new("vf_part", "INT", "POINT")  # each card's loose part
    part.data.foreach_set("value", np.unique(lab, return_inverse=True)[1].astype(np.int32))
    mat = bpy.data.materials.new("vf hair (cards)")
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes.get("Principled BSDF")
    at_t, at_s = (nodes.new("ShaderNodeAttribute") for _ in range(2))
    at_t.attribute_name, at_s.attribute_name = "vf_t", "vf_s"
    vec = nodes.new("ShaderNodeCombineXYZ")  # strands: fine across the card, long along it
    links.new(_mul(nt, at_s.outputs["Fac"], 18.0), vec.inputs["X"])
    links.new(_mul(nt, at_t.outputs["Fac"], 0.6), vec.inputs["Y"])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value, noise.inputs["Detail"].default_value = 1.0, 3.0
    links.new(vec.outputs["Vector"], noise.inputs["Vector"])
    strands = nodes.new("ShaderNodeMapRange")
    strands.inputs["From Min"].default_value, strands.inputs["From Max"].default_value = 0.42, 0.56
    links.new(noise.outputs["Fac"], strands.inputs["Value"])
    tip = nodes.new("ShaderNodeMapRange")  # 1 to 0.7 of the length, fading to 0 at the tip
    tip.inputs["From Min"].default_value, tip.inputs["From Max"].default_value = 1.0, 0.7
    links.new(at_t.outputs["Fac"], tip.inputs["Value"])
    edge_abs = nodes.new("ShaderNodeMath")
    edge_abs.operation = "ABSOLUTE"
    links.new(at_s.outputs["Fac"], edge_abs.inputs[0])
    edge = nodes.new("ShaderNodeMapRange")
    edge.inputs["From Min"].default_value, edge.inputs["From Max"].default_value = 1.0, 0.75
    links.new(edge_abs.outputs[0], edge.inputs["Value"])
    alpha = _mul(nt, _mul(nt, strands.outputs["Result"], tip.outputs["Result"]), edge.outputs["Result"])
    if alpha_name:  # a CC0 strand sheet instead: across the card its lit width, along it root (top) to tip
        img = nodes.new("ShaderNodeTexImage")
        img.image = bpy.data.images.load(str(OGA_ALPHAS / f"{alpha_name}.png"), check_existing=True)
        uv = nodes.new("ShaderNodeCombineXYZ")
        across01 = nodes.new("ShaderNodeMapRange")
        across01.inputs["From Min"].default_value, across01.inputs["From Max"].default_value = -1.0, 1.0
        across01.inputs["To Min"].default_value, across01.inputs["To Max"].default_value = 0.10, 0.78
        links.new(at_s.outputs["Fac"], across01.inputs["Value"])
        along01 = nodes.new("ShaderNodeMapRange")
        along01.inputs["To Min"].default_value, along01.inputs["To Max"].default_value = 0.98, 0.28
        links.new(at_t.outputs["Fac"], along01.inputs["Value"])
        links.new(across01.outputs["Result"], uv.inputs["X"])
        links.new(along01.outputs["Result"], uv.inputs["Y"])
        links.new(uv.outputs["Vector"], img.inputs["Vector"])
        alpha = img.outputs["Alpha"]
    links.new(alpha, bsdf.inputs["Alpha"])
    ramp = nodes.new("ShaderNodeMix")  # darker at the root, lighter to the tip
    ramp.data_type = "RGBA"
    links.new(at_t.outputs["Fac"], ramp.inputs["Factor"])
    next(i for i in ramp.inputs if i.identifier == "A_Color").default_value = (0.025, 0.016, 0.011, 1.0)
    next(i for i in ramp.inputs if i.identifier == "B_Color").default_value = (0.075, 0.052, 0.036, 1.0)
    links.new(next(o for o in ramp.outputs if o.identifier == "Result_Color"), bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.38
    mat.surface_render_method = "DITHERED"
    # the base cap - the largest part, a shell over the cranium - is no card: darkened skin under the cards (a
    # second material on its faces), so it reads as the scalp seen through the hair, not a band
    sizes = np.bincount(np.searchsorted(np.unique(lab), lab))
    cap_label = np.unique(lab)[np.argmax(sizes)]
    cap_mat = bpy.data.materials.new("vf hair (cap)")
    cap_bsdf = cap_mat.node_tree.nodes.get("Principled BSDF")
    cap_bsdf.inputs["Base Color"].default_value = (0.05, 0.032, 0.024, 1.0)
    cap_bsdf.inputs["Roughness"].default_value = 0.7
    me.materials.append(mat)
    me.materials.append(cap_mat)
    poly_v = np.empty(len(me.polygons), np.int64)
    me.polygons.foreach_get("loop_start", poly_v)
    loop_v = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loop_v)
    on_cap = (lab[loop_v[poly_v]] == cap_label).astype(np.int32)
    me.polygons.foreach_set("material_index", on_cap)
    print("VF CARDS", len(np.unique(lab)), "cards; the cap", int(sizes.max()), "verts,", int(on_cap.sum()), "faces", flush=True)
    return mat


OGA_ALPHAS = Path(__file__).resolve().parents[2] / ".dev" / "downloads" / "other_samples" / "oga_hair_alphas" / "x"


def _mul(nt, a, b):
    m = nt.nodes.new("ShaderNodeMath")
    m.operation = "MULTIPLY"
    for k, v in enumerate((a, b)):
        if isinstance(v, float):
            m.inputs[k].default_value = v
        else:
            nt.links.new(v, m.inputs[k])
    return m.outputs[0]


def Matrix_identity():
    from mathutils import Matrix

    return Matrix.Identity(4)


def lidblink(built: dict, stem: str, closed: float = 0.0, blur: int = 8, cell_mm: float = 0.35) -> None:
    """The relief layers (pores, microrelief, the scans' relief) faded inside each eye's blink stretch
    (`.dev/gate/masks/<stem>.png`: the left eye's red, the right's green - tools/make_lid_mask.py) by that eye's own blink
    key, through drivers - MetaHuman's and CC5's expression-driven detail: the open eye unchanged, the closing lid's
    stretched detail gone (2026-11-09: a mask applied always made the open lid smooth and glossy)."""
    maps = _maps()
    body = built["body"]
    keys = body.data.shape_keys
    image = bpy.data.images.load(str(MASK_TRIALS / f"{stem}.png"), check_existing=False)
    image.colorspace_settings.name = "Non-Color"
    n = 0
    for mat, _bsdf, mod in _skin_materials(built):
        nt = mat.node_tree
        nodes, links = nt.nodes, nt.links
        tex = nodes.new("ShaderNodeTexImage")
        tex.image, tex.extension = image, "CLIP"
        links.new(nodes[maps.NODE + "uv"].outputs["UV"], tex.inputs["Vector"])
        sep = nodes.new("ShaderNodeSeparateColor")
        links.new(tex.outputs["Color"], sep.inputs["Color"])
        total = None
        for channel, key in (("Red", "eyeBlinkLeft"), ("Green", "eyeBlinkRight")):
            value = nodes.new("ShaderNodeValue")
            value.name = f"lidblink_{key}"
            fc = value.outputs[0].driver_add("default_value")
            fc.driver.type = "AVERAGE"
            var = fc.driver.variables.new()
            var.type = "SINGLE_PROP"
            var.targets[0].id_type = "KEY"
            var.targets[0].id = keys
            var.targets[0].data_path = f'key_blocks["{key}"].value'
            m = nodes.new("ShaderNodeMath")
            m.operation = "MULTIPLY"
            links.new(sep.outputs[channel], m.inputs[0])
            links.new(value.outputs[0], m.inputs[1])
            if total is None:
                total = m.outputs[0]
            else:
                a = nodes.new("ShaderNodeMath")
                a.operation = "ADD"
                links.new(total, a.inputs[0])
                links.new(m.outputs[0], a.inputs[1])
                total = a.outputs[0]
        on_head = nodes.new("ShaderNodeMath")
        on_head.operation = "MULTIPLY"
        links.new(total, on_head.inputs[0])
        links.new(nodes[maps.NODE + "mouth_on_head"].outputs["Value"], on_head.inputs[1])
        keep = nodes.new("ShaderNodeMath")
        keep.operation, keep.use_clamp = "SUBTRACT", True
        keep.inputs[0].default_value = 1.0
        links.new(on_head.outputs[0], keep.inputs[1])
        for key in ("pore", "micro"):
            depth = nodes[maps.NODE + f"{key}_depth"]
            src = depth.inputs[0].links[0].from_socket
            cut = nodes.new("ShaderNodeMath")
            cut.operation = "MULTIPLY"
            links.new(src, cut.inputs[0])
            links.new(keep.outputs[0], cut.inputs[1])
            links.new(cut.outputs[0], depth.inputs[0])
        relief = nodes[maps.NODE + "relief_off_stretched"]
        links.new(keep.outputs[0], relief.inputs[0])  # its number was 1: the scans' relief x keep
        if closed:
            _lid_closed_detail(nt, on_head.outputs[0], closed, blur, cell_mm)
        mod.sync_live(mat)
        n += 1
    bpy.context.view_layer.update()
    print("LID BLINK", stem, "on", n, "skins", "+ closed-lid colour and object-space relief" if closed else "", flush=True)


def _blurred_copy(image: bpy.types.Image, factor: int = 8) -> bpy.types.Image:
    """A 1/`factor`-size copy of an image (block means), sampled Linear: a soft blur of it at no extra cost."""
    w, h = image.size
    px = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    small = px[: h - h % factor, : w - w % factor].reshape(h // factor, factor, w // factor, factor, 4).mean((1, 3))
    out = bpy.data.images.new(image.name + " (blurred)", w // factor, h // factor, alpha=True, float_buffer=False)
    out.colorspace_settings.name = image.colorspace_settings.name
    out.pixels.foreach_set(small.astype(np.float32).ravel())
    out.pack()
    return out


def _lid_closed_detail(nt, share, depth_mm: float, blur: int = 8, cell_mm: float = 0.35) -> None:
    """The closed lid's skin: its colour faded toward a blurred copy (the stretched streaks out) and a fine pore-like
    relief in object space (Voronoi pits ~0.35 mm, `depth_mm` deep) added, both by `share` (blink x the lid mask)."""
    nodes, links = nt.nodes, nt.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    base_link = bsdf.inputs["Base Color"].links[0]
    colour_tex = next((n for n in nodes if n.type == "TEX_IMAGE" and n.image and "base_color" in n.image.name), None)
    if colour_tex is not None:
        soft_tex = nodes.new("ShaderNodeTexImage")
        soft_tex.image, soft_tex.interpolation = _blurred_copy(colour_tex.image, blur), "Linear"
        soft_tex.extension = "EXTEND"
        if colour_tex.inputs["Vector"].is_linked:
            links.new(colour_tex.inputs["Vector"].links[0].from_socket, soft_tex.inputs["Vector"])
        # the blurred colour carried through the same tone chain: the ratio blurred / sharp on the final colour
        ratio = nodes.new("ShaderNodeVectorMath")
        ratio.operation = "DIVIDE"
        links.new(soft_tex.outputs["Color"], ratio.inputs[0])
        links.new(colour_tex.outputs["Color"], ratio.inputs[1])
        clamp = nodes.new("ShaderNodeVectorMath")
        clamp.operation = "MINIMUM"
        links.new(ratio.outputs["Vector"], clamp.inputs[0])
        clamp.inputs[1].default_value = (3.0, 3.0, 3.0)
        soft = nodes.new("ShaderNodeVectorMath")
        soft.operation = "MULTIPLY"
        links.new(base_link.from_socket, soft.inputs[0])
        links.new(clamp.outputs["Vector"], soft.inputs[1])
        mix = nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        links.new(share, mix.inputs["Factor"])
        links.new(base_link.from_socket, next(i for i in mix.inputs if i.identifier == "A_Color"))
        links.new(soft.outputs["Vector"], next(i for i in mix.inputs if i.identifier == "B_Color"))
        # the eyes' surround tint (maps.EYE_SURROUND_TINT, x0.6) lifted off the closed lid: a closed lid's skin reads
        # lighter than the open eye's surround (HD Aaron's), and darkened it read as a brown sheet (00:4x)
        tint = _maps().EYE_SURROUND_TINT
        lift = nodes.new("ShaderNodeMix")
        lift.data_type = "RGBA"
        links.new(share, lift.inputs["Factor"])
        next(i for i in lift.inputs if i.identifier == "A_Color").default_value = (1.0, 1.0, 1.0, 1.0)
        next(i for i in lift.inputs if i.identifier == "B_Color").default_value = (*(1.0 / c for c in tint), 1.0)
        lifted = nodes.new("ShaderNodeVectorMath")
        lifted.operation = "MULTIPLY"
        links.new(next(o for o in mix.outputs if o.identifier == "Result_Color"), lifted.inputs[0])
        links.new(next(o for o in lift.outputs if o.identifier == "Result_Color"), lifted.inputs[1])
        links.new(lifted.outputs["Vector"], bsdf.inputs["Base Color"])
    coords = nodes.new("ShaderNodeTexCoord")
    vor = nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "F1"
    vor.inputs["Scale"].default_value = 1000.0 / cell_mm  # cells `cell_mm` across in object space (metres)
    links.new(coords.outputs["Object"], vor.inputs["Vector"])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value, noise.inputs["Detail"].default_value = 1000.0 / 1.2, 3.0
    links.new(coords.outputs["Object"], noise.inputs["Vector"])
    height = nodes.new("ShaderNodeMath")
    height.operation = "MULTIPLY_ADD"
    links.new(vor.outputs["Distance"], height.inputs[0])
    height.inputs[1].default_value = 1.0
    links.new(noise.outputs["Fac"], height.inputs[2])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 1.0
    dist = nodes.new("ShaderNodeMath")
    dist.operation = "MULTIPLY"
    links.new(share, dist.inputs[0])
    dist.inputs[1].default_value = depth_mm / 1000.0
    links.new(dist.outputs[0], bump.inputs["Distance"])
    links.new(height.outputs[0], bump.inputs["Height"])
    if bsdf.inputs["Normal"].is_linked:
        links.new(bsdf.inputs["Normal"].links[0].from_socket, bump.inputs["Normal"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def maskshow(built: dict, stem: str) -> None:
    """A head-tile mask (`.dev/gate/masks/<stem>.png`) painted red over the skin's colour - where a mask lands on the face
    (2026-11-09: the lids' stretch mask)."""
    maps = _maps()
    image = bpy.data.images.load(str(MASK_TRIALS / f"{stem}.png"), check_existing=False)
    image.colorspace_settings.name = "Non-Color"
    n = 0
    for mat, bsdf, mod in _skin_materials(built):
        nt = mat.node_tree
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image, tex.extension = image, "CLIP"
        nt.links.new(nt.nodes[maps.NODE + "uv"].outputs["UV"], tex.inputs["Vector"])
        on_head = nt.nodes[maps.NODE + "mouth_on_head"].outputs["Value"]
        share = nt.nodes.new("ShaderNodeMath")
        share.operation = "MULTIPLY"
        nt.links.new(tex.outputs["Color"], share.inputs[0])
        nt.links.new(on_head, share.inputs[1])
        red = nt.nodes.new("ShaderNodeMix")
        red.data_type = "RGBA"
        nt.links.new(share.outputs[0], red.inputs["Factor"])
        nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, next(i for i in red.inputs if i.identifier == "A_Color"))
        next(i for i in red.inputs if i.identifier == "B_Color").default_value = (0.8, 0.0, 0.0, 1.0)
        nt.links.new(next(o for o in red.outputs if o.identifier == "Result_Color"), bsdf.inputs["Base Color"])
        mod.sync_live(mat)
        n += 1
    print("MASK SHOWN", stem, "on", n, flush=True)


def tearfade(built: dict, start: float) -> None:
    """The tear film faded out toward its rim under the lids too (from share `start` to 0 at 1), not only in from its
    rim on the eyeball (`eye_layers.TEAR_FADE`): 2026-11-09, its lid-side edge showed as a white fleck on the lower
    lid's ledge (the ledge turn moved the lid out; 24-27 film vertices 1-2.3 mm off the eyeball)."""
    n = 0
    for obj in bpy.data.objects:
        if obj.juststage.part != "eyeEdge":
            continue
        for slot in obj.material_slots:
            nt = slot.material.node_tree
            attr = next(x for x in nt.nodes if x.type == "ATTRIBUTE" and x.attribute_name == "share")
            wet = next(x for x in nt.nodes if x.type == "MATH" and x.operation == "MULTIPLY")
            out_fade = nt.nodes.new("ShaderNodeMapRange")
            out_fade.interpolation_type = "SMOOTHSTEP"
            out_fade.inputs["From Min"].default_value, out_fade.inputs["From Max"].default_value = 1.0, start
            nt.links.new(attr.outputs["Fac"], out_fade.inputs["Value"])
            both = nt.nodes.new("ShaderNodeMath")
            both.operation = "MULTIPLY"
            nt.links.new(wet.outputs["Value"], both.inputs[0])
            nt.links.new(out_fade.outputs["Result"], both.inputs[1])
            gloss = next(x for x in nt.nodes if x.type == "BSDF_GLOSSY")
            nt.links.new(both.outputs["Value"], gloss.inputs["Color"])
            n += 1
    print("TEAR FADE from", start, "on", n, "materials", flush=True)


def marginrelief(built: dict, kept: float) -> None:
    """The lid margin's relief (pores, microrelief, the scans' relief) x `kept` by base v2's `js_margin` (the shader's
    margin_attr): 2026-11-09, the lower margin a wide band of stretched, streaky skin texture at the eye view - real
    margins are smooth wet tissue. Material-only: each depth factor and the normal map's strength scaled there."""
    maps = _maps()
    n = 0
    for nt in _skin_trees(built):
        nodes, links = nt.nodes, nt.links
        attr = nodes.get(maps.NODE + "margin_attr")
        if attr is None:
            continue
        keep = nodes.new("ShaderNodeMath")
        keep.operation = "MULTIPLY_ADD"  # 1 - (1 - kept) * margin
        links.new(attr.outputs["Fac"], keep.inputs[0])
        keep.inputs[1].default_value, keep.inputs[2].default_value = -(1.0 - kept), 1.0
        for key in ("pore", "micro"):
            depth = nodes[maps.NODE + f"{key}_depth"]
            src = depth.inputs[0].links[0].from_socket
            cut = nodes.new("ShaderNodeMath")
            cut.operation = "MULTIPLY"
            links.new(src, cut.inputs[0])
            links.new(keep.outputs[0], cut.inputs[1])
            links.new(cut.outputs[0], depth.inputs[0])
        strength = nodes[maps.NODE + "normal_map"].inputs["Strength"]
        cut = nodes.new("ShaderNodeMath")
        cut.operation = "MULTIPLY"
        cut.inputs[0].default_value = strength.default_value
        links.new(keep.outputs[0], cut.inputs[1])
        links.new(cut.outputs[0], strength)
        n += 1
    print("MARGIN RELIEF kept", kept, "on", n, "trees", flush=True)


def toeplate(built: dict, length: float, side: float) -> None:
    """The toes' nail plate shorter and narrower (`maps.TOE_PLATE_LENGTH`, `TOE_PLATE_SIDE`) in the shader and the nail
    bed's shape together - 2026-11-09, the fingers' plate covered the toe's whole tip. A shape: --alone."""
    maps = _maps()
    nail_bed = importlib.import_module("bl_ext.system.juststage.modules.skin.nail_bed")
    n = 0
    for nt in _skin_trees(built):
        for key, value in (("nail_plate_length", length), ("nail_plate_side", side)):
            node = nt.nodes.get(maps.NODE + key)
            if node is not None:
                next(i for i in node.inputs if i.identifier == "B_Float").default_value = value
                n += 1
    old = maps.TOE_PLATE_LENGTH, maps.TOE_PLATE_SIDE
    maps.TOE_PLATE_LENGTH, maps.TOE_PLATE_SIDE = length, side
    try:
        nail_bed.add(built["body"])
    finally:
        maps.TOE_PLATE_LENGTH, maps.TOE_PLATE_SIDE = old
    print("TOE PLATE", length, side, "on", n, "nodes", flush=True)


def nailgroove(built: dict, k: float) -> None:
    """The nail plate's border darkening (`maps.NAIL_GROOVE`, 0.15 since 2026-11-09, 0.45 before) set to k - the toenails read as stickers
    with a dark outline beside HD Aaron's."""
    maps = _maps()
    nodes = [nt.nodes[maps.NODE + "nail_groove_shade"] for nt in _skin_trees(built) if maps.NODE + "nail_groove_shade" in nt.nodes]
    for node in nodes:
        node.inputs[1].default_value = -4 * k
    print("NAIL GROOVE", k, "on", len(nodes), "nodes", flush=True)


def nailbed(built: dict, share: float) -> None:
    """The nail bed colour's share in the plate (`maps.NAIL_BED_SHARE`, 0.25) - 2026-11-09, the toenails pale beside his
    skin-toned ones."""
    maps = _maps()
    nodes = [nt.nodes[maps.NODE + "nail_bed"] for nt in _skin_trees(built) if maps.NODE + "nail_bed" in nt.nodes]
    for node in nodes:
        node.inputs["Factor"].default_value = share
    print("NAIL BED", share, "on", len(nodes), "nodes", flush=True)


def eartintset(built: dict, r: float, g: float, b: float) -> None:
    """The shipped ear layer's tint (`maps.EAR_TINT`) set to (r, g, b) - (1, 1, 1) turns it off: 2026-11-09, the
    Muscular man's ear glowed orange-red beside his dark skin."""
    nodes = _skin_node_inputs(built, "ears_tint")
    for node in nodes:
        next(i for i in node.inputs if i.identifier == "B_Color").default_value = (r, g, b, 1.0)
    print("EAR TINT", (r, g, b), "on", len(nodes), "nodes", flush=True)


def scatter(built: dict, k: float) -> None:
    """The live view's scattering distance x k (the EEVEE BSDF's Subsurface Scale) - a diagnostic of how much of a
    part's glow is light through it (2026-11-09: the Muscular man's orange-red ear)."""
    material = importlib.import_module("bl_ext.system.juststage.modules.skin.material")
    n = 0
    for mat, _bsdf, _mod in _skin_materials(built):
        live = mat.node_tree.nodes.get(material.LIVE_BSDF)
        if live is not None:
            live.inputs["Subsurface Scale"].default_value *= k
            n += 1
    print("SCATTER x", k, "on", n, "materials", flush=True)


def skintone(built: dict, melanin: float) -> None:
    """The character's skin tone set to `melanin` through the product's own command (`juststage.skin.set_tone`), its
    eumelanin share, blood and oiliness kept: 2026-11-09, the Heavy woman's preset melanin 0.25 sits at L* 17.6 - past
    NIST's darkest measured skin (L* 43) and the library's darkest tone (L* 25), where the model's colour greys."""
    body = built["body"]
    props = body.juststage
    api = importlib.import_module("bl_ext.system.juststage.api")
    made = api.run("juststage.skin.set_tone", character=props.character_id, melanin=melanin, eumelanin=props.eumelanin,
                   blood=props.blood, oiliness=props.oiliness)  # fmt: skip
    print("SKIN TONE melanin", melanin, "linear", [round(c, 4) for c in made.linear_rgb], flush=True)


MOUTH_TRIALS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "mouthmasks"


def mouthmask(built: dict, stem: str) -> None:
    """The mouth's lining and seam masks swapped for a variant (`.dev/gate/mouthmasks/<stem>/`, made by
    `tools/make_mouth_mask.py -- --out ...`): 2026-11-09, the lining faded out of the mouth's corner crease (a red glow
    at each corner at close-up)."""
    maps = _maps()
    n = 0
    for nt in _skin_trees(built):
        for node_name, file in (("mouth_mask", "mouth.png"), ("lips_seam_mask", "mouth_seam.png")):
            node = nt.nodes.get(maps.NODE + node_name)
            if node is not None:
                node.image = bpy.data.images.load(str(MOUTH_TRIALS / stem / file), check_existing=False)
                node.image.colorspace_settings.name = "Non-Color"
                n += 1
    print("MOUTH MASK", stem, "on", n, "nodes", flush=True)


def eyetint(built: dict, r: float, g: float, b: float) -> None:
    """The eyes' surround tint (`maps.EYE_SURROUND_TINT` (0.60, 0.54, 0.51)) set on its node - on darker skins the
    surround reads bruised grey (2026-11-09, the characters' check); 1,1,1 = the layer off."""
    nodes = _skin_node_inputs(built, "eyes_tint")
    for node in nodes:
        next(i for i in node.inputs if i.identifier == "B_Color").default_value = (r, g, b, 1.0)
    print("EYE TINT", (r, g, b), "on", len(nodes), "nodes", flush=True)


def margintint(built: dict, r: float, g: float, b: float) -> None:
    """The lid margin's tint over the skin (`maps.MARGIN_TINT` (0.86, 0.62, 0.62)) - our margin reads as a thick
    orange-pink rim round the eye beside HD Aaron's thin wet line (2026-11-08)."""
    nodes = _skin_node_inputs(built, "margin_tint")
    for node in nodes:
        next(i for i in node.inputs if i.identifier == "B_Color").default_value = (r, g, b, 1.0)
    print("MARGIN TINT", (r, g, b), "on", len(nodes), "nodes", flush=True)


def eyewhite(built: dict, k: float) -> None:
    """The eyes' white colour (`eyes.WHITE`) scaled by k - step 1's fault: the white reads too bright and bluish."""
    eyes = importlib.import_module("bl_ext.system.juststage.modules.head.eyes")
    n = 0
    for mat in bpy.data.materials:
        if mat.node_tree is None:
            continue
        node = mat.node_tree.nodes.get(eyes.NODE + "white")
        if node is not None:
            node.outputs[0].default_value = (*(k * c for c in eyes.WHITE), 1.0)
            n += 1
        for g in (x for x in mat.node_tree.nodes if x.type == "GROUP" and "EyeWhiteColor" in x.inputs):
            g.inputs["EyeWhiteColor"].default_value = (*(k * c for c in eyes.WHITE), 1.0)
            n += 1
    print("EYE WHITE x", k, "on", n, "nodes", flush=True)


def stubblepatch(built: dict, patchy: float, density: float) -> None:
    """Our stubble regrown patchy (`stubble.PATCHY`, 0 shipped: an even density read as a uniform mat beside HD Aaron's
    patchy stubble, 2026-11-09) at a density (hairs a cm2, 100 shipped - patches lower the mean, so it is given too).
    A new groom: --alone."""
    stubble = importlib.import_module("bl_ext.system.juststage.modules.hair.stubble")
    old = stubble.PATCHY
    stubble.PATCHY = patchy
    try:
        stubble.make(built["body"], density=density)
    finally:
        stubble.PATCHY = old
    cid = built["body"].juststage.character_id
    built["objects"] = [o for o in bpy.context.scene.objects if cid in (o.juststage.character_id, o.juststage.part_of)]
    print("STUBBLE PATCHY", patchy, "density", density, flush=True)


def stubbletrial(built: dict, density: float, grey: float, length: float) -> None:
    """Our stubble regrown (`stubble.make`) at a density (hairs a cm2, 160 shipped), grey share (0.25) and length (mm,
    2.8) - step 1's fault: a dense dark mat over the lower face against his short, sparse, greying stubble. A new groom:
    --alone."""
    stubble = importlib.import_module("bl_ext.system.juststage.modules.hair.stubble")
    old = stubble.GREY_SHARE
    stubble.GREY_SHARE = grey
    try:
        stubble.make(built["body"], density=density, length_mm=length)
    finally:
        stubble.GREY_SHARE = old
    cid = built["body"].juststage.character_id
    built["objects"] = [o for o in bpy.context.scene.objects if cid in (o.juststage.character_id, o.juststage.part_of)]
    print("STUBBLE", density, "a cm2, grey", grey, "length", length, flush=True)


#: the face's shape by our own sliders (2026-11-08, step 1's fault: a broad, flat, puffy face with small squinting
#: eyes reads as a doll; his bone structure): presets of (slider id, value), each a character setting we ship
FACE_PRESETS = {
    "lean": [("head/head-fat-decr-incr", -0.5), ("cheek/l-cheek-volume-decr-incr", -0.5),
             ("cheek/r-cheek-volume-decr-incr", -0.5), ("cheek/l-cheek-bones-decr-incr", 0.5),
             ("cheek/r-cheek-bones-decr-incr", 0.5)],
    "brow": [("eyebrows/eyebrows-trans-down-up", 1.0), ("eyes/l-eye-height2-decr-incr", 0.4),
             ("eyes/r-eye-height2-decr-incr", 0.4)],
}
FACE_PRESETS["leanbrow"] = FACE_PRESETS["lean"] + FACE_PRESETS["brow"]
#: round 2 (15:52: "lean" and "brow" at half strength moved the face too little to read differently): full strength,
#: the eyes opened by the lid sliders and the brow ridge brought forward
FACE_PRESETS["strong"] = [("head/head-fat-decr-incr", -1.0), ("cheek/l-cheek-volume-decr-incr", -1.0),
                          ("cheek/r-cheek-volume-decr-incr", -1.0), ("cheek/l-cheek-bones-decr-incr", 1.0),
                          ("cheek/r-cheek-bones-decr-incr", 1.0), ("eyebrows/eyebrows-trans-down-up", 1.0),
                          ("eyebrows/eyebrows-trans-backward-forward", 1.0), ("eyes/l-eye-height2-decr-incr", 1.0),
                          ("eyes/r-eye-height2-decr-incr", 1.0)]  # fmt: skip
#: the ears (step 1: ours small and smooth beside his) - larger, the rim and the flap out a little
FACE_PRESETS["ears"] = [("ears/l-ear-scale-decr-incr", 0.4), ("ears/r-ear-scale-decr-incr", 0.4),
                        ("ears/l-ear-flap-decr-incr", 0.3), ("ears/r-ear-flap-decr-incr", 0.3)]  # fmt: skip
#: the lips (step 1 / the quick round: ours a puffy round tube, his flatter with a defined border and a cupid's bow)
FACE_PRESETS["lipthin"] = [("mouth/mouth-upperlip-volume-decr-incr", -0.6), ("mouth/mouth-lowerlip-volume-decr-incr", -0.4),
                           ("mouth/mouth-cupidsbow-decr-incr", 0.5)]  # fmt: skip


def eyedark(built: dict, k: float) -> None:
    """The skin round the eyes darker and a little redder - his lids and under-eyes read darker and reddish-brown, ours
    the cheek's flat colour (15:51, `row_face_eye.png`). The face's "eyes" region (`make_face_regions.py`: within 17 mm
    of a pupil) is the only one whose region map has both pores < 0.1 and microrelief < 0.13 (R, B / 8); the base
    colour there x (k, k^1.6... as an RGB tint: k, k x 0.9, k x 0.85 for the red-brown), the map's own softened edge."""
    maps = _maps()
    tint = (k, k * 0.9, k * 0.85)
    n = 0
    for mat, bsdf, mod in _skin_materials(built):
        nt = mat.node_tree
        split = nt.nodes.get(maps.NODE + "face_regions_split")
        if split is None or not bsdf.inputs["Base Color"].is_linked:
            continue
        # a fade, not a cut (17:3x: LESS_THAN drew a hard ring round the eye): the microrelief channel is 0.101 in the
        # eyes region and 0.169 on the cheek, nose and forehead around it (chin 0.27), softened over the mesh by the
        # map's own passes - its ramp from 0.168 down to 0.105 is the mask
        # times the pores' channel's ramp (eyes 0.086, the nose too, the neck 0.125, cheek 0.144): the neck's microrelief
        # (0.125) sits inside the first ramp, its pores keep it out
        ramps = []
        for out, lo, hi in (("Blue", 0.168, 0.105), ("Red", 0.13, 0.09)):
            ramp = nt.nodes.new("ShaderNodeMapRange")
            ramp.clamp = True
            nt.links.new(split.outputs[out], ramp.inputs["Value"])
            ramp.inputs["From Min"].default_value, ramp.inputs["From Max"].default_value = lo, hi
            ramp.inputs["To Min"].default_value, ramp.inputs["To Max"].default_value = 0.0, 1.0
            ramps.append(ramp)
        mask = nt.nodes.new("ShaderNodeMath")
        mask.operation = "MULTIPLY"
        nt.links.new(ramps[0].outputs["Result"], mask.inputs[0])
        nt.links.new(ramps[1].outputs["Result"], mask.inputs[1])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(mask.outputs[0], mix.inputs["Factor"])
        next(i for i in mix.inputs if i.identifier == "A_Color").default_value = (1.0, 1.0, 1.0, 1.0)
        next(i for i in mix.inputs if i.identifier == "B_Color").default_value = (*tint, 1.0)
        times = nt.nodes.new("ShaderNodeVectorMath")
        times.operation = "MULTIPLY"
        nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, times.inputs[0])
        nt.links.new(next(o for o in mix.outputs if o.identifier == "Result_Color"), times.inputs[1])
        nt.links.new(times.outputs["Vector"], bsdf.inputs["Base Color"])
        mod.sync_live(mat)  # the live view's own BSDF takes the same inputs
        n += 1
    print("EYE DARK tint", tint, "on", n, "skins (film and live)", flush=True)


WRINKLE_TRIALS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "wrinkles"


def wrinkles(built: dict, stem: str, strength: float = 1.0) -> None:
    """Our own wrinkle layer (`tools/make_wrinkles.py`: forehead lines, the frown's, crow's feet, the lower lid's crease,
    the nose-to-mouth fold - grooves drawn in the head tile's UVs from the face's landmarks) as a bump at the end of the
    skin's normal chain, sampled through the region map's own head-tile coordinates; its depth x `strength`. 20:4x: no
    free scan gives wrinkles at HD Aaron's strength, and his relief is what makes his skin read real on our head."""
    maps = _maps()
    img = bpy.data.images.load(str(WRINKLE_TRIALS / stem / "wrinkles.png"), check_existing=False)
    img.colorspace_settings.name = "Non-Color"
    n = 0
    for mat, bsdf, mod in _skin_materials(built):
        nt = mat.node_tree
        regions = nt.nodes.get(maps.NODE + "face_regions")
        if regions is None or not regions.inputs["Vector"].is_linked:
            continue
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image, tex.interpolation, tex.extension = img, "Cubic", "EXTEND"
        nt.links.new(regions.inputs["Vector"].links[0].from_socket, tex.inputs["Vector"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 1.0
        bump.inputs["Distance"].default_value = 0.0004 * strength  # make_wrinkles.DEPTH_M
        nt.links.new(tex.outputs["Color"], bump.inputs["Height"])
        if bsdf.inputs["Normal"].is_linked:
            nt.links.new(bsdf.inputs["Normal"].links[0].from_socket, bump.inputs["Normal"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        mod.sync_live(mat)
        n += 1
    print("WRINKLES", stem, "x", strength, "on", n, "skins (film and live)", flush=True)


def aoshade(built: dict, strength: float, distance_mm: float = 15.0) -> None:
    """The skin darkened in its creases by Blender's Ambient Occlusion shader node (EEVEE's horizon scan, Cycles' AO) -
    the plan's §10 "Cavity: TO BUILD (flat 1.0 on every composed skin today)" and CC5's own AO map. 2026-11-08: with the
    face's shape changed (sliders, two real scans' shapes) ours still reads as a doll at the face view, where his face
    is dark in every crease - the eye sockets, beside the nose, under the lip; ours lit flat. Base colour x mix(1, AO,
    strength); `distance_mm` the occlusion's reach."""
    n = 0
    for mat, bsdf, mod in _skin_materials(built):
        nt = mat.node_tree
        if not bsdf.inputs["Base Color"].is_linked:
            continue
        ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
        ao.inputs["Distance"].default_value = distance_mm / 1000.0
        ao.samples = 16
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "FLOAT"
        mix.inputs["Factor"].default_value = strength
        next(i for i in mix.inputs if i.identifier == "A_Float").default_value = 1.0
        nt.links.new(ao.outputs["AO"], next(i for i in mix.inputs if i.identifier == "B_Float"))
        times = nt.nodes.new("ShaderNodeVectorMath")
        times.operation = "SCALE"
        nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, times.inputs[0])
        nt.links.new(next(o for o in mix.outputs if o.identifier == "Result_Float"), times.inputs["Scale"])
        nt.links.new(times.outputs["Vector"], bsdf.inputs["Base Color"])
        mod.sync_live(mat)
        n += 1
    print("AO SHADE strength", strength, "reach", distance_mm, "mm on", n, "skins (film and live)", flush=True)


def browtrial(built: dict, count: float, fine: float, fine_melanin: float, grey: float, melanin: float | None = None,
              redness: float | None = None) -> None:
    """Our brows grown again (`brows.make`) with the coarse hairs' COUNT, the FINE hairs' count and melanin, and the
    grey share set - 19:1x: the layer diagnostic made our brows the eyes' main fault (his dark, dense, low; ours grey,
    thin), and the hair model's shares darkened the scalp but hardly the brows: their own settings are the lever (a
    fifth white in the gate, 1,400 lighter fine hairs at melanin 0.8). Optionally the coarse hairs' MELANIN and the
    brows' REDNESS (2026-11-09: near-black brows read as a grey smudge on the Average woman and the Older man). A new
    groom: --alone."""
    brows = importlib.import_module("bl_ext.system.juststage.modules.hair.brows")
    old = brows.COUNT, brows.FINE, brows.FINE_MELANIN, brows.MELANIN, brows.REDNESS
    brows.COUNT, brows.FINE, brows.FINE_MELANIN = int(count), int(fine), fine_melanin
    if melanin is not None:
        brows.MELANIN = melanin
    if redness is not None:
        brows.REDNESS = redness
    try:
        brows.make(built["body"], grey_share=grey)
    finally:
        brows.COUNT, brows.FINE, brows.FINE_MELANIN, brows.MELANIN, brows.REDNESS = old
    cid = built["body"].juststage.character_id
    built["objects"] = [o for o in bpy.context.scene.objects if cid in (o.juststage.character_id, o.juststage.part_of)]
    print("BROWS", int(count), "coarse,", int(fine), "fine at", fine_melanin, "grey", grey, flush=True)


MH_BODY_NORMAL = Path(__file__).resolve().parents[2] / ".dev" / "downloads" / "mh_skins02" / "x" / "skins" / \
    "mindfront_skin_male_african_middleage" / "skin_male_african_middleage_NRM.png"  # CC0 (MINDFRONT, MakeHuman's skins02)


def mhbody(built: dict, strength: float) -> None:
    """The body's definition (step 1's fault: our torso flat and smooth, his defined - the plan's §11 Q-BODY-1, a
    definition layer on a strength slider): MakeHuman's CC0 community skin normal map (MINDFRONT's "skin male african
    middleage", on our disk from skins02 - sculpted muscle definition in hm08's own UVs) on the body tiles - its normal
    (hm08's "UVMap") added to ours as a world-space detail, n = normalize(ours + s (mh - geometry)), the head tile left
    as ours (tile index 0)."""
    maps = _maps()
    img = bpy.data.images.load(str(MH_BODY_NORMAL), check_existing=True)
    img.colorspace_settings.name = "Non-Color"
    n = 0
    for mat, bsdf, mod in _skin_materials(built):
        nt = mat.node_tree
        fine = nt.nodes.get(maps.NODE + "height_bump")
        ours_map = nt.nodes.get(maps.NODE + "normal_map")
        which = nt.nodes.get(maps.NODE + "tile_index")
        if fine is None or ours_map is None or which is None:
            continue
        uv = nt.nodes.new("ShaderNodeUVMap")
        uv.uv_map = "UVMap"
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
        mh = nt.nodes.new("ShaderNodeNormalMap")
        mh.space, mh.uv_map = "TANGENT", "UVMap"
        nt.links.new(tex.outputs["Color"], mh.inputs["Color"])
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        diff = nt.nodes.new("ShaderNodeVectorMath")
        diff.operation = "SUBTRACT"
        nt.links.new(mh.outputs["Normal"], diff.inputs[0])
        nt.links.new(geo.outputs["Normal"], diff.inputs[1])
        body = nt.nodes.new("ShaderNodeMath")  # 1 on the body tiles, 0 on the head's
        body.operation = "GREATER_THAN"
        nt.links.new(which.outputs[0], body.inputs[0])
        body.inputs[1].default_value = 0.5
        amount = nt.nodes.new("ShaderNodeMath")
        amount.operation = "MULTIPLY"
        nt.links.new(body.outputs[0], amount.inputs[0])
        amount.inputs[1].default_value = strength
        scaled = nt.nodes.new("ShaderNodeVectorMath")
        scaled.operation = "SCALE"
        nt.links.new(diff.outputs["Vector"], scaled.inputs[0])
        nt.links.new(amount.outputs[0], scaled.inputs["Scale"])
        added = nt.nodes.new("ShaderNodeVectorMath")
        added.operation = "ADD"
        nt.links.new(ours_map.outputs["Normal"], added.inputs[0])
        nt.links.new(scaled.outputs["Vector"], added.inputs[1])
        unit = nt.nodes.new("ShaderNodeVectorMath")
        unit.operation = "NORMALIZE"
        nt.links.new(added.outputs["Vector"], unit.inputs[0])
        nt.links.new(unit.outputs["Vector"], fine.inputs["Normal"])
        mod.sync_live(mat)
        n += 1
    print("MH BODY NORMAL strength", strength, "on", n, "skins (film and live)", flush=True)


def eartint(built: dict, r: float, g: float, b: float) -> None:
    """The ears' colour x (r, g, b) by MPFB2's CC0 ears mask (`mpfb_ears.jpg`, hm08's own UVs - as the lips' vermilion
    by `mpfb_lips.jpg`): step 1's ear fault - ours pale, his red and translucent (the plan's §5: "a map on MPFB2's CC0
    ears mask only if the ear view shows a gap")."""
    paths = importlib.import_module("bl_ext.system.juststage.paths")
    img = bpy.data.images.load(str(paths.makehuman("textures", "mpfb_ears.jpg")), check_existing=True)
    img.colorspace_settings.name = "Non-Color"
    n = 0
    for mat, bsdf, mod in _skin_materials(built):
        nt = mat.node_tree
        if not bsdf.inputs["Base Color"].is_linked:
            continue
        uv = nt.nodes.new("ShaderNodeUVMap")
        uv.uv_map = "UVMap"
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        nt.links.new(uv.outputs["UV"], tex.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        nt.links.new(tex.outputs["Color"], mix.inputs["Factor"])
        next(i for i in mix.inputs if i.identifier == "A_Color").default_value = (1.0, 1.0, 1.0, 1.0)
        next(i for i in mix.inputs if i.identifier == "B_Color").default_value = (r, g, b, 1.0)
        mul = nt.nodes.new("ShaderNodeVectorMath")
        mul.operation = "MULTIPLY"
        nt.links.new(bsdf.inputs["Base Color"].links[0].from_socket, mul.inputs[0])
        nt.links.new(next(o for o in mix.outputs if o.identifier == "Result_Color"), mul.inputs[1])
        nt.links.new(mul.outputs["Vector"], bsdf.inputs["Base Color"])
        mod.sync_live(mat)
        n += 1
    print("EAR TINT", (r, g, b), "on", n, "skins (film and live)", flush=True)


def regiontint(built: dict, k: float = 1.0) -> None:
    """Regional colour in our skin (18:59, the layer diagnostic: HD Aaron's skin on our head took the doll look away -
    redder nose and cheeks, darker reddish lids and under-eyes; ours one flat peach): by the region map's smooth ramps,
    the eyes' surround x (0.78, 0.66, 0.62) and the nose x (1.0, 0.86, 0.86), `k` scaling how far from 1."""
    maps = _maps()
    # 19:25: (0.78, 0.66, 0.62) x2 read as orange eye shadow on our peach base - his lids darker brown-red; less orange
    tints = {"eyes": (0.80, 0.72, 0.72), "nose": (1.0, 0.88, 0.88)}
    n = 0
    for mat, bsdf, mod in _skin_materials(built):
        nt = mat.node_tree
        split = nt.nodes.get(maps.NODE + "face_regions_split")
        if split is None or not bsdf.inputs["Base Color"].is_linked:
            continue

        def ramp(out, lo, hi):
            r = nt.nodes.new("ShaderNodeMapRange")
            r.clamp = True
            nt.links.new(split.outputs[out], r.inputs["Value"])
            r.inputs["From Min"].default_value, r.inputs["From Max"].default_value = lo, hi
            return r.outputs["Result"]

        def times(a, b):
            m = nt.nodes.new("ShaderNodeMath")
            m.operation = "MULTIPLY"
            nt.links.new(a, m.inputs[0])
            nt.links.new(b, m.inputs[1])
            return m.outputs[0]

        low_pores = ramp("Red", 0.13, 0.09)  # eyes and nose 0.086; neck 0.125, cheek 0.144 out
        masks = {"eyes": times(low_pores, ramp("Blue", 0.168, 0.105)),  # micro 0.101 round the eyes
                 "nose": times(low_pores, times(ramp("Blue", 0.13, 0.16), ramp("Blue", 0.22, 0.19)))}  # 0.169
        colour = bsdf.inputs["Base Color"].links[0].from_socket
        for key, mask in masks.items():
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            nt.links.new(mask, mix.inputs["Factor"])
            next(i for i in mix.inputs if i.identifier == "A_Color").default_value = (1.0, 1.0, 1.0, 1.0)
            next(i for i in mix.inputs if i.identifier == "B_Color").default_value = (
                *(1.0 - k * (1.0 - c) for c in tints[key]), 1.0)
            mul = nt.nodes.new("ShaderNodeVectorMath")
            mul.operation = "MULTIPLY"
            nt.links.new(colour, mul.inputs[0])
            nt.links.new(next(o for o in mix.outputs if o.identifier == "Result_Color"), mul.inputs[1])
            colour = mul.outputs["Vector"]
        nt.links.new(colour, bsdf.inputs["Base Color"])
        mod.sync_live(mat)
        n += 1
    print("REGION TINT k", k, tints, "on", n, "skins (film and live)", flush=True)


def liplines(built: dict, period_mm: float = 1.2, depth_mm: float = 0.25, distortion: float = 6.0,
             vary: float = 0.0) -> None:
    """Vertical lip lines made in the shader (our own asset, the user's "making your own assets"; no free scan resolves
    them - Ten24's lips are ~220 texels across): Blender's Wave Texture in bands across the lips (the object's X, a
    line every `period_mm`, its distortion by noise for irregular furrows), masked by the lips' share, as a bump on top of
    the skin's relief - step 1's fault: our lips read as smooth rubber, his show fine vertical lines."""
    maps = _maps()
    n = 0
    for mat, bsdf, mod in _skin_materials(built):
        nt = mat.node_tree
        share = nt.nodes.get(maps.NODE + "lips_share")
        if share is None:
            continue
        coord = nt.nodes.new("ShaderNodeNewGeometry")  # world position in metres (the object's own units may not be)
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type, wave.bands_direction, wave.wave_profile = "BANDS", "X", "SIN"
        wave.inputs["Scale"].default_value = 1000.0 / period_mm
        wave.inputs["Distortion"].default_value = distortion  # 6 read as a dense crinkle (16:59); his lines fewer, upright
        wave.inputs["Detail"].default_value = 3.0
        wave.inputs["Detail Scale"].default_value = 1.5
        nt.links.new(coord.outputs["Position"], wave.inputs["Vector"])
        lines = wave.outputs["Fac"]
        if vary > 0:  # irregular lines (17:3x: an even wave read as a comb): each line's strength varied by a noise
            # of ~4 mm cells, so some furrows are deep, some fade - as his
            noise = nt.nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = 1000.0 / 4.0
            noise.inputs["Detail"].default_value = 2.0
            nt.links.new(coord.outputs["Position"], noise.inputs["Vector"])
            gain = nt.nodes.new("ShaderNodeMath")
            gain.operation = "MULTIPLY_ADD"  # 1 - vary + vary * noise
            nt.links.new(noise.outputs["Fac"], gain.inputs[0])
            gain.inputs[1].default_value, gain.inputs[2].default_value = vary, 1.0 - vary
            varied = nt.nodes.new("ShaderNodeMath")
            varied.operation = "MULTIPLY"
            nt.links.new(lines, varied.inputs[0])
            nt.links.new(gain.outputs[0], varied.inputs[1])
            lines = varied.outputs[0]
        height = nt.nodes.new("ShaderNodeMath")
        height.operation = "MULTIPLY"
        nt.links.new(lines, height.inputs[0])
        nt.links.new(share.outputs[0], height.inputs[1])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Distance"].default_value = depth_mm / 1000.0
        bump.inputs["Strength"].default_value = 1.0
        nt.links.new(height.outputs[0], bump.inputs["Height"])
        if bsdf.inputs["Normal"].is_linked:
            nt.links.new(bsdf.inputs["Normal"].links[0].from_socket, bump.inputs["Normal"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        mod.sync_live(mat)  # the live view's own BSDF takes the same inputs
        n += 1
    print("LIP LINES every", period_mm, "mm, depth", depth_mm, "mm on", n, "skins (film and live)", flush=True)


def faceshape(built: dict, presets: str) -> None:
    """The face's shape set by one or more FACE_PRESETS ("lean", "lean&brow"), the eyes, teeth and films refitted.
    A shape: --alone."""
    sliders = importlib.import_module("bl_ext.system.juststage.modules.body.sliders")
    catalog = sliders.catalog()
    done = []
    for preset in presets.split("&"):
        for key, value in FACE_PRESETS[preset]:
            if key not in catalog:
                print("FACE SLIDER MISSING", key, flush=True)
                continue
            sliders.apply(built["body"], catalog[key], value)
            done.append((key, value))
    bpy.context.view_layer.update()
    importlib.import_module("bl_ext.system.juststage.modules.head.parts").refit(built["body"])
    bpy.context.view_layer.update()
    print("FACE SHAPE", presets, done, flush=True)


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


def mouthlining(built: dict, r: float, g: float, b: float) -> None:
    """Item 5's inner mouth, one factor: both tongues see none of the stage's lights (RESEARCH 14.5), so what lights
    his is bounce or his material; ours sits in a mouth lined dark red (`maps.MOUTH_COLOUR` (0.42, 0.11, 0.11)) - the
    lining's colour (linear) set lighter on the shader's mix."""
    maps = _maps()
    done = 0
    for nt in _skin_trees(built):
        node = nt.nodes.get(maps.NODE + "mouth_colour")
        if node is not None:
            next(i for i in node.inputs if i.identifier == "B_Color").default_value = (r, g, b, 1.0)
            done += 1
    print("MOUTH LINING", (r, g, b), done, "trees", flush=True)


def _cavity_faces(built: dict) -> list[int]:
    """The body's faces inside the mouth: behind the front teeth's front, within the teeth part's box widened 5 mm."""
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    body = built["body"]
    teeth = pg._world(parts.parts_of(body)["teeth"], evaluated=False)
    lo, hi = teeth.min(0) - 0.005, teeth.max(0) + 0.005
    front = float(teeth[:, 1].min())
    mw = np.array(body.matrix_world)
    co = build.shaped_coords(body) @ mw[:3, :3].T + mw[:3, 3]
    return [p.index for p in body.data.polygons
            if (c := co[list(p.vertices)].mean(0))[1] > front and lo[0] < c[0] < hi[0] and lo[2] < c[2] < hi[2]]


def shadowsplit(built: dict, region: str) -> None:
    """Which skin shadows our tongue, by objects (EEVEE ignores a material's shadow-ray transparency - `allnoshadow`):
    the body casts no shadow; a copy of it, unseen by the camera, casts it instead - without `region`'s faces ("cavity":
    inside the mouth; "head": the head's tile). The visible body, its grooms and its rig stay as they are."""
    import bmesh

    body = built["body"]
    if region == "cavity":
        drop = set(_cavity_faces(built))
    else:
        me = body.data
        uv = np.empty(len(me.loops) * 2, np.float32)
        me.uv_layers[_maps().UV].data.foreach_get("uv", uv)
        uv = uv.reshape(-1, 2)
        drop = {p.index for p in me.polygons if uv[list(p.loop_indices), 0].mean() < 1.0}
    proxy = body.copy()
    proxy.data = body.data.copy()
    proxy.name = f"{body.name} (shadow, without the {region})"
    for collection in body.users_collection:
        collection.objects.link(proxy)
    bm = bmesh.new()
    bm.from_mesh(proxy.data)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in sorted(drop)], context="FACES_ONLY")
    bm.to_mesh(proxy.data)
    bm.free()
    proxy.juststage.character_id = ""  # not the character: `character.find` and the face rig's handler pass it by
    if "JustStage face rig" in proxy.keys():  # (its keys are set with the body's - built["keyed"]; the jaw is the
        del proxy["JustStage face rig"]  # same armature)
    proxy.visible_camera = proxy.visible_diffuse = proxy.visible_glossy = False
    proxy.visible_transmission = proxy.visible_volume_scatter = False
    body.visible_shadow = False
    built["keyed"] = [*built["keyed"], proxy]
    print("SHADOW SPLIT", region, len(drop), "faces left out of the caster", flush=True)


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


def tonguedown(built: dict, down_mm: float, back_mm: float = 0.0) -> None:
    """The tongue moved down (and back) in the open mouth - 2026-11-10 `tongueglow`: our tongue fills the whole opening
    up to the upper lip (the "dark void" is its top in shadow); his sits low behind the lower teeth. Its vertices
    (the teeth part's `tongue` group) moved in the teeth object's own axes, every shape key alike. A shape: --alone."""
    parts = importlib.import_module("bl_ext.system.juststage.modules.head.parts")
    teeth = parts.parts_of(built["body"])["teeth"]
    idx = np.asarray(parts.groups("teeth")["tongue"], np.int64)
    inv = np.linalg.inv(np.array(teeth.matrix_world))[:3, :3]
    d = inv @ np.array([0.0, back_mm / 1000.0, -down_mm / 1000.0])  # world: -z down, +y back (the face looks down -y)
    blocks = list(teeth.data.shape_keys.key_blocks) if teeth.data.shape_keys else []
    for target in [teeth.data.vertices] + [kb.data for kb in blocks]:
        co = np.empty(len(target) * 3, np.float32)
        target.foreach_get("co", co)
        co = co.reshape(-1, 3)
        co[idx] += d
        target.foreach_set("co", co.ravel())
    teeth.data.update()
    print("TONGUE DOWN", down_mm, "mm, back", back_mm, "mm,", len(idx), "vertices", flush=True)


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


def mix(built: dict, first: str, second: str = "", strength: float = 1.0) -> None:
    """The mixer on our character (`juststage.body.set_mix`, the product's command): `first` in every part, or - with
    `second` - the two alternating part by part (head shape, nose, mouth and ears the first's; forehead, eyes and chin
    the second's), the most part borders a face can have: do the borders, the neck and the riders (eyes, teeth) hold in
    a render? Identities by index into the library (`mixer.identities()`) or name. A shape: --alone."""
    api = importlib.import_module("bl_ext.system.juststage.api")
    mixer = importlib.import_module("bl_ext.system.juststage.modules.body.mixer")
    names = mixer.identities()

    def pick(token: str) -> str:
        return names[int(token)] if token.isdigit() else token

    body = built["body"]
    a, b = pick(first), pick(second) if second else ""
    takes = {"head shape": a, "nose": a, "mouth": a, "ears": a, "forehead": b or a, "eyes": b or a, "chin": b or a}
    for region, name in takes.items():
        api.run("juststage.body.set_mix", character=body.juststage.character_id, region=region, identities=name,
                weights=[1.0], strength=strength)  # fmt: skip
    bpy.context.view_layer.update()
    print("MIX", {r: n for r, n in takes.items()}, "strength", strength, flush=True)


def earmix(built: dict, name: str, strength: float = 1.0) -> None:
    """One identity's ears alone (the mixer's "ears" region, `juststage.body.set_mix`) - Q-EAR-1's feasibility: a
    real ear (HUTUBS) on our head, its concha against hm08's shallow dish (2026-11-10). A shape: --alone."""
    api = importlib.import_module("bl_ext.system.juststage.api")
    body = built["body"]
    api.run("juststage.body.set_mix", character=body.juststage.character_id, region="ears", identities=name,
            weights=[1.0], strength=strength)  # fmt: skip
    bpy.context.view_layer.update()
    print("EAR MIX", name, "strength", strength, flush=True)


def exprset(built: dict, expression: str, key: str, value: float) -> None:
    """One key of one of the gate's expressions for ours, set in the gate's own table (`parts_gate.EXPRESSIONS`): a
    view sets its expression after a factor runs, so `setkey` on an expression view is overwritten (2026-11-10: the
    "aa" trial came out three times alike). The table stays changed for the run's later variants - put it last."""
    pg.EXPRESSIONS[expression]["ours"][key] = value
    print("EXPRESSION", expression, key, "=", value, flush=True)


def factor(name: str):
    if name in FACTORS:
        return FACTORS[name]
    if name.startswith("lashup*") and "+" not in name:  # lashup*15*80 (the upper lashes' rise and curl, degrees) - --alone
        return lambda built: lashup(built, *(float(x) for x in name.split("*")[1:6]))
    if name.startswith("lipsoft*") and "+" not in name:  # lipsoft*4 (the lips mask blurred, texels)
        return lambda built: lipsoft(built, float(name.split("*", 1)[1]))
    if name.startswith("browthick*") and "+" not in name:  # browthick*2 or browthick*2*0.95 (radius x k, the coarse hairs' melanin)
        bits = [float(x) for x in name.split("*")[1:]]
        return lambda built: browthick(built, bits[0], bits[1] if len(bits) > 1 else None)
    if name.startswith("mhbrow*") and "+" not in name:  # mhbrow*012 (MakeHuman's CC0 brow card set)
        return lambda built: mhbrow(built, name.split("*", 1)[1])
    if name.startswith("icthead*") and "+" not in name:  # icthead*head1 (ICT-FaceKit's head placed by tools/gate/ict_head.py)
        return lambda built: icthead(built, name.split("*", 1)[1])
    if name.startswith("bodycoat*") and "+" not in name:  # bodycoat*0.1 (the body's coat weight)
        return lambda built: bodycoat(built, float(name.split("*", 1)[1]))
    if name == "coatnormal":  # the coat lobe on the bumped normal (defined below FACTORS)
        return coatnormal
    if name.startswith("cavitynet*") and "+" not in name:  # cavitynet*cavnet_a*0.823 (a tile under .dev/gate/micro, the strength)
        _c, stem, strength = name.split("*")
        return lambda built: cavitynet(built, stem, float(strength))
    if name.startswith("regions*"):  # regions*fh1p2 (a region-map variant's folder under .dev/gate/regions)
        return lambda built: regions(built, name.split("*", 1)[1])
    if name.startswith("exprset*") and "+" not in name:  # exprset*talk_aa*jawOpen*0.8 (a gate expression's key)
        _e, expression, key, value = name.split("*")
        return lambda built: exprset(built, expression, key, float(value))
    if name.startswith("earmix*"):  # earmix*hutubs_pp1[*1.0] (one identity's ears alone) - --alone
        bits = name.split("*")
        return lambda built: earmix(built, bits[1], *(float(bits[2]),) if len(bits) > 2 else ())
    if name.startswith("mix*"):  # mix*0, mix*0*3, mix*0*3*0.7 (identities by index or name, the strength)
        first, *rest = name.split("*")[1:]
        second = rest[0] if rest else ""
        strength = float(rest[1]) if len(rest) > 1 else 1.0
        return lambda built: mix(built, first, second, strength)
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
    if name.startswith("browtrial*"):  # browtrial*1200*2000*0.92*0[*0.8*0.25] (coarse, fine, fine melanin, grey[,
        return lambda built: browtrial(built, *(float(x) for x in name.split("*")[1:7]))  # melanin, redness]) - --alone
    if name.startswith("mhbody*"):  # mhbody*1.0 (MakeHuman's CC0 body normal on the body tiles, its strength)
        return lambda built: mhbody(built, float(name.split("*")[1]))
    if name.startswith("eartint*"):  # eartint*1.0*0.78*0.76 (the ears' colour multiplier)
        return lambda built: eartint(built, *(float(x) for x in name.split("*")[1:4]))
    if name.startswith("regiontint"):  # regiontint, regiontint*1.5 (how far from 1)
        return lambda built: regiontint(built, *(float(x) for x in name.split("*")[1:2]))
    if name.startswith("wrinkles*"):  # wrinkles*w1[*1.5] (the map's folder under .dev/gate/wrinkles, its strength)
        stem, *k = name.split("*")[1:]
        return lambda built: wrinkles(built, stem, *(float(x) for x in k))
    if name.startswith("aoshade*"):  # aoshade*0.6[*15] (strength, reach in mm)
        return lambda built: aoshade(built, *(float(x) for x in name.split("*")[1:3]))
    if name.startswith("eyedark*"):  # eyedark*0.8 (the tint's level round the eyes)
        return lambda built: eyedark(built, float(name.split("*")[1]))
    if name.startswith("liplines"):  # liplines, liplines*1.2*0.25[*6] (period, depth in mm, distortion)
        return lambda built: liplines(built, *(float(x) for x in name.split("*")[1:5]))
    if name.startswith("faceshape*"):  # faceshape*lean, faceshape*lean&brow (FACE_PRESETS) - --alone
        return lambda built: faceshape(built, name.split("*", 1)[1])
    if name.startswith("lipshine*"):  # lipshine*0.5*0.1 (roughness, coat)
        return lambda built: lipshine(built, *(float(x) for x in name.split("*")[1:3]))
    if name.startswith("liptint*"):  # liptint*0.9*0.55*0.6 (linear RGB)
        return lambda built: liptint(built, *(float(x) for x in name.split("*")[1:4]))
    if name.startswith("stubblepatch*"):  # stubblepatch*0.8*140 (patchy share, density a cm2) - --alone
        return lambda built: stubblepatch(built, *(float(x) for x in name.split("*")[1:3]))
    if name.startswith("upperlip*"):  # upperlip*0.8*0.6*0.62 (linear RGB, x the colour on the upper lip)
        return lambda built: upperlip(built, *(float(x) for x in name.split("*")[1:4]))
    if name.startswith("lipseam*"):  # lipseam*1.5 (maps.LIP_SEAM_STRENGTH's place; 0 = none)
        return lambda built: lipseam(built, float(name.split("*")[1]))
    if name.startswith("lipcrease*"):  # lipcrease*0.2*1.8*0.15*3*1 (sharpness, period mm, depth mm, distortion, detail)
        return lambda built: lipcrease(built, *(float(x) for x in name.split("*")[1:6]))
    if name.startswith("lipset*"):  # lipset*1.8*0.0002*6*0.95 (maps.LIP_LINES' place: period mm, depth m, distortion,
        return lambda built: lipset(built, *(float(x) for x in name.split("*")[1:5]))  # vary)
    if name.startswith("hide*"):  # hide*eyebrows (a groom's part: eyebrows, eyelashes, scalp, beard)
        return lambda built: _hide_part(built, name.split("*", 1)[1])
    if name.startswith("browedge*"):  # browedge*0.55 (the roots' bell across the brow; 0 today's even) - --alone
        return lambda built: browedge(built, float(name.split("*")[1]))
    if name.startswith("browpoly"):  # browpoly[*1.6*0.9*0.5] (brow cards on Polytricity's strips) - --alone
        bits = [float(b) for b in name.split("*")[1:]]
        return lambda built: browpoly(built, *bits)
    if name.startswith("vfpoly*"):  # vfpoly*B4[*0.2] (the free cut's cards, Polytricity's free strands) - --alone
        bits = name.split("*")
        return lambda built: vfpoly(built, bits[1], *(float(bits[2]),) if len(bits) > 2 else (),
                                    *(bits[3],) if len(bits) > 3 else ())
    if name.startswith("vfbake2*"):  # vfbake2*B4[*12*0.5] (clump cards, our hair model, our strands' atlas) - --alone
        bits = name.split("*")
        return lambda built: vfbake2(built, bits[1], *(float(bits[2]),) if len(bits) > 2 else (),
                                     *(float(bits[3]),) if len(bits) > 3 else ())
    if name.startswith("vfbake*"):  # vfbake*B4[*6000*7] (cards along our strands, textured from our strands) - --alone
        bits = name.split("*")
        return lambda built: vfbake(built, bits[1], *(int(bits[2]),) if len(bits) > 2 else (),
                                    *(float(bits[3]),) if len(bits) > 3 else ())
    if name.startswith("vfcards*"):  # vfcards*B4[*6000*7*hair02] (cards along our strands, a CC0 sheet) - --alone
        bits = name.split("*")
        return lambda built: vfcards(built, bits[1], *(int(bits[2]),) if len(bits) > 2 else (),
                                     *(float(bits[3]),) if len(bits) > 3 else (), *(bits[4],) if len(bits) > 4 else ())
    if name.startswith("vfguides*"):  # vfguides*B4 (our strands grown from the free cut's cards) - --alone
        bits = name.split("*")
        return lambda built: vfguides(built, bits[1], *(float(bits[2]) / 1000.0,) if len(bits) > 2 else ())
    if name.startswith("vfhair*"):  # vfhair*B4[*tex] (a bust of VincentFreelance's male collection 01) - --alone
        bits = name.split("*")
        return lambda built: vfhair(built, bits[1], textured=len(bits) > 2 and bits[2] == "tex",
                                    alpha=f"hair{bits[2][3:]}" if len(bits) > 2 and bits[2].startswith("oga") else "")
    if name.startswith("lidblink*"):  # lidblink*lid_blink[*0.04] (the relief faded by each eye's blink; with a depth in
        bits = name.split("*")  # mm: the closed lid's colour blurred and an object-space relief that deep added)
        return lambda built: lidblink(built, bits[1], *(float(bits[2]),) if len(bits) > 2 else (),
                                      *(int(bits[3]),) if len(bits) > 3 else (), *(float(bits[4]),) if len(bits) > 4 else ())
    if name.startswith("maskshow*"):  # maskshow*stretched (a head-tile mask under .dev/gate/masks painted red)
        return lambda built: maskshow(built, name.split("*", 1)[1])
    if name.startswith("tearfade*"):  # tearfade*0.7 (the film fades out from this share to its lid-side rim)
        return lambda built: tearfade(built, float(name.split("*")[1]))
    if name.startswith("marginrelief*"):  # marginrelief*0 (the lid margin's relief kept: 0 none)
        return lambda built: marginrelief(built, float(name.split("*")[1]))
    if name.startswith("toeplate*"):  # toeplate*0.6*0.65 (the toes' plate length share and half-width) - --alone
        _k, length, side = name.split("*")
        return lambda built: toeplate(built, float(length), float(side))
    if name.startswith("nailgroove*"):  # nailgroove*0.2 (the plate's border darkening)
        return lambda built: nailgroove(built, float(name.split("*")[1]))
    if name.startswith("nailbed*"):  # nailbed*0.1 (the bed colour's share in the plate)
        return lambda built: nailbed(built, float(name.split("*")[1]))
    if name.startswith("eartintset*"):  # eartintset*1*1*1 (the shipped ear tint; 1, 1, 1 off)
        return lambda built: eartintset(built, *(float(x) for x in name.split("*")[1:4]))
    if name.startswith("scatter*"):  # scatter*0.3 (the live view's scattering distance x k)
        return lambda built: scatter(built, float(name.split("*")[1]))
    if name.startswith("skintone*"):  # skintone*0.1 (melanin)
        return lambda built: skintone(built, float(name.split("*", 1)[1]))
    if name.startswith("mouthmask*"):  # mouthmask*corner (a variant folder under .dev/gate/mouthmasks)
        return lambda built: mouthmask(built, name.split("*", 1)[1])
    if name.startswith("eyetint*"):  # eyetint*1*1*1 (maps.EYE_SURROUND_TINT's place; 1,1,1 = off)
        return lambda built: eyetint(built, *(float(x) for x in name.split("*")[1:4]))
    if name.startswith("margintint*"):  # margintint*1*1*1 (maps.MARGIN_TINT's place, linear RGB; 1,1,1 = the skin's)
        return lambda built: margintint(built, *(float(x) for x in name.split("*")[1:4]))
    if name.startswith("eyewhite*"):  # eyewhite*0.85
        return lambda built: eyewhite(built, float(name.split("*")[1]))
    if name.startswith("stubbletrial*"):  # stubbletrial*90*0.4*2.8 (a cm2, grey share, mm) - --alone
        return lambda built: stubbletrial(built, *(float(x) for x in name.split("*")[1:4]))
    if name.startswith("scalpstyle"):  # scalpstyle*sides (SCALP_PRESETS)
        return lambda built: scalpstyle(built, name.split("*", 1)[1])
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
    if name.startswith("mouthlining*"):  # mouthlining*0.6*0.25*0.25 (the inner mouth's lining colour, linear)
        _k, r, g, b = name.split("*")
        return lambda built: mouthlining(built, float(r), float(g), float(b))
    if name.startswith("shadowsplit*"):  # shadowsplit*cavity / *head (a shadow-only copy without those faces)
        return lambda built: shadowsplit(built, name.split("*")[1])
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
    if name.startswith("tonguedown*") and "+" not in name:  # tonguedown*6[*3] (mm down, mm back) - --alone
        return lambda built: tonguedown(built, *(float(x) for x in name.split("*")[1:3]))
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
    if name == "aaronflat":  # after aaronskin: his relief off, his colour alone
        return aaronflat
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
    if name.startswith("lashtrial*"):  # lashtrial*0.04*110 (the lower lashes' root radius in mm, count an eye) - --alone
        _k, radius, count = name.split("*")
        return lambda built: lashtrial(built, float(radius), float(count))
    if name.startswith("lashlower*"):  # lashlower*0.9 (the lower lashes' melanin)
        return lambda built: lashlower(built, float(name.split("*")[1]))
    if name.startswith("lashcap"):  # lashcap*1.6 (mm)
        return lambda built: lashcap(built, float(name.split("*")[1]))
    if name.split("*")[0] in EYE_SLIDERS:  # eyebag*0 (the slider's value, both eyes)
        key, value = name.split("*")
        return lambda built: eye_slider(built, key, float(value))
    if name.startswith("regioncontrast*"):  # regioncontrast*1.6 (the colour's 5-60 mm variation scaled)
        return lambda built: regioncontrast(built, float(name.split("*")[1]))
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
    if name.startswith("feetpart"):  # feetpart*1.0 (body_scan.py thunk3d_foot: body_100{3,4}_feet_* - the foot's
        k = float(name.split("*")[1]) if "*" in name else 1.0  # faces lie on both tiles, most of them on 1003)
        return lambda built: [handspart(built, k, tile=t, part="feet") for t in (1003, 1004)]
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
    p.add_argument("--passes", default="", help="view-layer passes into an EXR beside each PNG (parts_gate's --passes)")
    p.add_argument("--clay", action="store_true", help="every skin one grey, every hair hidden (parts_gate's --clay)")
    a = p.parse_args(args)
    pg.PASSES = tuple(x for x in a.passes.split(",") if x)
    pg.CLAY = a.clay
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
