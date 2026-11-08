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
    h, w = px.shape[:2]
    img = bpy.data.images.new(name, w, h, float_buffer=True)
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


#: the eye-open sliders (body_create.EYE_OPEN) one at a time - the lower lid's thick roll at the eye view; shape keys,
#: so these run alone (`--alone`: a build each - the trials' material reset doesn't undo a shape)
EYE_SLIDERS = {"eyebag": "bag-decr-incr", "eyeheight2": "height2-decr-incr", "eyefold": "eyefold-concave-convex",
               "eyefoldup": "eyefold-down-up", "eyeheight1": "height1-decr-incr"}


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


def eye_slider(built: dict, key: str, value: float) -> None:
    sliders = importlib.import_module("bl_ext.system.juststage.modules.body.sliders")
    catalog = sliders.catalog()
    for side in ("l", "r"):
        sliders.apply(built["body"], catalog[f"eyes/{side}-eye-{EYE_SLIDERS[key]}"], value)
    bpy.context.view_layer.update()
    print("EYE SLIDER", key, value, flush=True)


SMILE_TRIALS = Path(__file__).resolve().parents[2] / ".dev" / "gate" / "smile"


def ictsmile(built: dict, stem: str) -> None:
    """ICT-FaceKit's smile shapes carried onto our head (`tools/gate/smile_transfer.py`, `.dev/gate/smile/<stem>.npz`)
    written into our ARKit keys of the same names (mouthSmile, cheekSquint, eyeSquint), each side to the key that
    moves the same side - the gate's face_smile / face_smile_full views then show ICT's scanned smile on our head
    against HD Aaron's (the smile proof, plan §7 "Expression shapes"). A shape: --alone."""
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

    for shape in ("mouthSmile", "cheekSquint", "eyeSquint"):
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
            d = d @ to_local.T
            same = [k for k, (_, ref, s) in ours.items() if np.sign(s) == np.sign(side(d, ref))]
            key, ref, _ = ours[same[0] if len(same) == 1 else ("Left" if short == "_L" else "Right")]
            key.data.foreach_set("co", (ref + d).astype(np.float32).ravel())
            print("ICT SMILE", f"{shape}{short}", "->", key.name, "max",
                  round(float(np.linalg.norm(d, axis=1).max()) * 1000, 1), "mm", flush=True)
    me.update()
    bpy.context.view_layer.update()


SCALED_KEYS = {"pores", "micro", "relief", "roughvar", "poresize", *SHINE}


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
    if name.startswith("lidledge"):  # lidledge*1*2.3 (the share toward the rim's line, the lash line's gap in mm)
        _, k, gap = name.split("*")
        return lambda built: lidledge(built, float(k), float(gap))
    if name.startswith("ictsmile"):  # ictsmile*ict_average_man (the carried deltas' file stem)
        return lambda built: ictsmile(built, name.split("*", 1)[1])
    if name.startswith("lidcarry"):  # lidcarry*0.85*0.7*0.55 (a share a ring)
        shares = [float(x) for x in name.split("*")[1:]]
        return lambda built: lidcarry(built, *shares)
    if name.startswith("lashcap"):  # lashcap*1.6 (mm)
        return lambda built: lashcap(built, float(name.split("*")[1]))
    if name.split("*")[0] in EYE_SLIDERS:  # eyebag*0 (the slider's value, both eyes)
        key, value = name.split("*")
        return lambda built: eye_slider(built, key, float(value))
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
    a = p.parse_args(args)
    out = a.out.resolve()  # absolute: Blender's render path then can't land anywhere else
    names = a.factors.split(",")
    tags = ["_f-" + n.replace("*", "x").replace(".", "p").replace("+", "_") + ("_world" if a.lights == "world" else "")
            for n in names]  # fmt: skip
    if a.alone:  # a build each (a factor that changes the shape)
        for t, n in zip(tags, names, strict=True):
            pg.render("ours", a.engine, out, a.views.split(","), pg.SIZE, pg.CYCLES_SAMPLES, tag=t, prepare=factor(n),
                      lights=a.lights, scalp=a.scalp)
    else:  # built once, the materials set back before each factor (parts_gate.render's variants)
        pg.render("ours", a.engine, out, a.views.split(","), pg.SIZE, pg.CYCLES_SAMPLES, lights=a.lights,
                  scalp=a.scalp, variants=[(t, factor(n)) for t, n in zip(tags, names, strict=True)])
    for tag in tags:
        for view in a.views.split(","):
            made = out / f"{a.engine}_{view}_ours{tag}.png"
            print("WRITTEN" if made.exists() else "MISSING", made, flush=True)
