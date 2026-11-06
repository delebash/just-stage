# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The library's mapped skins from the face test's characters (`.dev/facetest/chars/<name>/`: a scan skin base under
the character's own painted face, rounds 74-101; the realism working doc, `docs/plans/2026-11-04-realism.md` rec 4).

    python tools/dev.py blender -b --python tools/build_skins.py -- [name ...]

Each character's round scene holds its head maps in its own head tile (the face test's `HeadTile`); they are baked into
the body's UDIM layout's head tile (1001, `tools/make_udim.py`) by Blender's own bake on the processor
(https://docs.blender.org/manual/en/5.3/render/cycles/baking.html): colour, roughness, cavity and height copied
(emission bakes, data kept as data), the face test's object-space normals baked to tangent space (a Normal bake of the
same normal set-up). The other tiles take the character's plain body skin (the face test's reserved corner), its skin
roughness, a flat normal. Written as `<library>/Skins/<Name> skin.blend` through `juststage.library.save`, the images
packed, the tone the maps were made at kept on the material (`map_*`, modules/skin/maps.py).
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from pathlib import Path

import bpy
import numpy as np

api = importlib.import_module("bl_ext.system.juststage.api")
library = importlib.import_module("bl_ext.system.juststage.core.library")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")
material = importlib.import_module("bl_ext.system.juststage.modules.skin.material")
skin_optics = importlib.import_module("bl_ext.system.juststage.core.skin_optics")
paths = importlib.import_module("bl_ext.system.juststage.paths")

ROOT = Path(__file__).resolve().parents[1]
CHARS = ROOT / ".dev" / "facetest" / "chars"
OUT = ROOT / ".dev" / "skins"  # the baked tiles before they are packed
NAMES = {"man_a": "Daniel", "amara": "Amara", "walter": "Walter", "mei": "Mei"}
#: each character's melanin as the face test made it (face_character.py's FACETEST_MELANIN; the first man the clay's
#: default) - its stored colour map is brought to that tone's brightness: the face test levelled every map to one light
#: skin and made dark people dark by the scene's exposure (test_face_project.py's calibration), fine for its renders,
#: wrong for a skin
MELANIN = {"man_a": 0.025, "amara": 0.18, "walter": 0.02, "mei": 0.03}
LUMA = np.array([0.2126, 0.7152, 0.0722])  # Rec.709
SIZE, BODY_SIZE, FLAT_SIZE = 4096, 1024, 256
#: the body's coloured regions (MPFB2's CC0 masks on hm08's UVs, fetched): each one's tone over the skin's own, by the
#: chromophore model - (melanin factor, melanin added, blood factor); nails also shinier (roughness)
REGIONS = {
    "areolae": (2.0, 0.01, 1.6),
    "nails": (0.4, 0.0, 1.8),
    "genitals": (1.6, 0.005, 1.5),
}
NAIL_ROUGHNESS = 0.3
MASK_BLUR = 2  # texels at 1024: soft edges
MARGIN = 16
FLAT = {"roughness": material.ROUGHNESS, "cavity": 1.0, "height": 0.5}
PROVENANCE = (
    "JustStage face test (tools/face_test): a scan skin base from CC BY scans on Sketchfab (their authors listed in "
    "docs/plans/2026-11-02-research-texture-source.md) under a face painted by FLUX 3 Image Klein on the character's "
    "own clay; pores from the Lee Perry-Smith 'Infinite' head scan (CC BY 3.0, via three.js)"
)
LICENCE = "CC-BY-4.0 (scans) / CC-BY-3.0 (pores); painted with FLUX 3 Image Klein (FLUX Kommunity licence)"


def _pixels(image) -> np.ndarray:
    w, h = image.size
    buf = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(buf)
    return buf.reshape(h, w, 4)


def _bake_uv(body, number: int = 1001) -> None:
    """A UV layer for baking one tile as a plain 0-1 image: that tile's loops where the UDIM layer has them, the rest
    pushed off the image."""
    me = body.data
    uv = np.empty(len(me.loops) * 2, np.float32)  # the body's own UDIM layer (hm08's or base v2's loops)
    me.uv_layers[maps.UV].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    loop_tile = 1001 + np.floor(uv[:, 0]).astype(int)
    flat = uv - np.array([number - 1001, 0.0], np.float32)
    flat[loop_tile != number] += 5.0
    layer = me.uv_layers.get("bake") or me.uv_layers.new(name="bake")
    layer.data.foreach_set("uv", flat.ravel())
    me.uv_layers.active = layer
    for other in me.uv_layers:
        other.active_render = other.name == "bake"


def _bake(body, kind: str, build, size: int = 4096) -> np.ndarray:
    """One bake into a fresh float image through a temporary material made by `build(nodes, links, out)`."""
    mat = bpy.data.materials.new("bake")
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    build(nt.nodes, nt.links, out)
    target = bpy.data.images.new("bake target", size, size, alpha=False, float_buffer=True)
    target.colorspace_settings.name = "Non-Color"
    node = nt.nodes.new("ShaderNodeTexImage")
    node.image = target
    nt.nodes.active = node
    slots = body.data.materials
    saved = list(slots)
    slots.clear()
    slots.append(mat)
    # A Normal bake on the Basis, modifiers off: Cycles' tangent frames stay on the Basis while the shading normal
    # follows the shape keys, so with the face test's keys on it baked their normal change into every head tile
    # (measured 2026-11-06: p50 0.10 / p90 0.31 tilt from a plain BSDF; RESEARCH "The head tile's false shading")
    shape = (body.show_only_shape_key, body.active_shape_key_index)
    shown = [m.show_render for m in body.modifiers]
    if kind == "NORMAL":
        body.show_only_shape_key, body.active_shape_key_index = True, 0
        for m in body.modifiers:
            m.show_render = False
    try:
        bpy.ops.object.bake(type=kind, normal_space="TANGENT", margin=MARGIN, margin_type="EXTEND", use_clear=True)
        return _pixels(target)[..., :3].copy()
    finally:
        body.show_only_shape_key, body.active_shape_key_index = shape
        for m, show in zip(body.modifiers, shown, strict=True):
            m.show_render = show
        slots.clear()
        for m in saved:
            slots.append(m)
        bpy.data.materials.remove(mat)
        bpy.data.images.remove(target)


def _decode(srgb: np.ndarray) -> np.ndarray:
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


def _encode(linear: np.ndarray) -> np.ndarray:
    linear = np.clip(linear, 0.0, 1.0)
    return np.where(linear <= 0.0031308, linear * 12.92, 1.055 * linear ** (1 / 2.4) - 0.055)


def _face_test_gain(body) -> np.ndarray:
    """The face test's colour gain: the Vector Math node its calibration set on the way to the skin's Base Color."""
    nt = body.data.materials[0].node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    node = bsdf.inputs["Base Color"].links[0].from_node
    return np.array(node.inputs[1].default_value[:3])


def _source(name: str, folder: Path) -> bpy.types.Image:
    image = bpy.data.images.load(str(folder / f"face_{name}.png"), check_existing=False)
    image.colorspace_settings.name = "Non-Color"  # copied as stored (colour stays sRGB-encoded)
    return image


def _emission_of(image):
    def build(nodes, links, out):
        uv = nodes.new("ShaderNodeUVMap")
        uv.uv_map = "HeadTile"
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = image
        emit = nodes.new("ShaderNodeEmission")
        links.new(uv.outputs["UV"], tex.inputs["Vector"])
        links.new(tex.outputs["Color"], emit.inputs["Color"])
        links.new(emit.outputs["Emission"], out.inputs["Surface"])

    return build


def _normals_of(normal, painted):
    """The face test's normal set-up: its object-space map where painted, the surface's own normal elsewhere."""

    def build(nodes, links, out):
        uv = nodes.new("ShaderNodeUVMap")
        uv.uv_map = "HeadTile"
        tex, mask = nodes.new("ShaderNodeTexImage"), nodes.new("ShaderNodeTexImage")
        tex.image, mask.image = normal, painted
        tex.interpolation = "Cubic"
        for t in (tex, mask):
            links.new(uv.outputs["UV"], t.inputs["Vector"])
        nmap = nodes.new("ShaderNodeNormalMap")
        nmap.space = "OBJECT"
        links.new(tex.outputs["Color"], nmap.inputs["Color"])
        mix = nodes.new("ShaderNodeMix")
        mix.data_type = "VECTOR"
        links.new(mask.outputs["Color"], mix.inputs["Factor"])
        links.new(
            nodes.new("ShaderNodeNewGeometry").outputs["Normal"],
            next(i for i in mix.inputs if i.identifier == "A_Vector"),
        )
        links.new(nmap.outputs["Normal"], next(i for i in mix.inputs if i.identifier == "B_Vector"))
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(next(o for o in mix.outputs if o.identifier == "Result_Vector"), bsdf.inputs["Normal"])
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    return build


def _tangent_normals_of(image):
    """A tangent-space normal map in the HeadTile layout as the shading normal - baked (Normal, tangent) into the
    bake's own layout: the relief moves from one UV layout's tangent frames to the other's."""

    def build(nodes, links, out):
        uv = nodes.new("ShaderNodeUVMap")
        uv.uv_map = "HeadTile"
        tex = nodes.new("ShaderNodeTexImage")
        tex.image, tex.interpolation = image, "Cubic"
        links.new(uv.outputs["UV"], tex.inputs["Vector"])
        nmap = nodes.new("ShaderNodeNormalMap")
        nmap.space, nmap.uv_map = "TANGENT", "HeadTile"
        links.new(tex.outputs["Color"], nmap.inputs["Color"])
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    return build


def _masks_of():
    """MPFB2's region masks as emission: red the areolae, green the finger and toe nails, blue the genitals with half
    the crotch."""
    images = {}
    for name in ("aureolae", "fingernails", "toenails", "genitals", "crotch"):
        image = bpy.data.images.load(str(paths.makehuman("textures", f"mpfb_{name}.jpg")), check_existing=True)
        image.colorspace_settings.name = "Non-Color"
        images[name] = image

    def build(nodes, links, out):
        uv = nodes.new("ShaderNodeUVMap")
        uv.uv_map = "UVMap"
        tex = {}
        for name, image in images.items():
            tex[name] = nodes.new("ShaderNodeTexImage")
            tex[name].image = image
            links.new(uv.outputs["UV"], tex[name].inputs["Vector"])
        nails = nodes.new("ShaderNodeMath")
        nails.operation = "MAXIMUM"
        links.new(tex["fingernails"].outputs["Color"], nails.inputs[0])
        links.new(tex["toenails"].outputs["Color"], nails.inputs[1])
        half = nodes.new("ShaderNodeMath")
        half.operation, half.inputs[1].default_value = "MULTIPLY", 0.5
        links.new(tex["crotch"].outputs["Color"], half.inputs[0])
        lower = nodes.new("ShaderNodeMath")
        lower.operation = "MAXIMUM"
        links.new(tex["genitals"].outputs["Color"], lower.inputs[0])
        links.new(half.outputs["Value"], lower.inputs[1])
        rgb = nodes.new("ShaderNodeCombineColor")
        links.new(tex["aureolae"].outputs["Color"], rgb.inputs["Red"])
        links.new(nails.outputs["Value"], rgb.inputs["Green"])
        links.new(lower.outputs["Value"], rgb.inputs["Blue"])
        emit = nodes.new("ShaderNodeEmission")
        links.new(rgb.outputs["Color"], emit.inputs["Color"])
        links.new(emit.outputs["Emission"], out.inputs["Surface"])

    return build


def _blur(mask: np.ndarray, px: int) -> np.ndarray:
    for axis in (0, 1):
        mask = sum(np.roll(mask, k, axis=axis) for k in range(-px, px + 1)) / (2 * px + 1)
    return mask


BODY_SCAN_SIZE = 2048


def _body_scan() -> dict | None:
    """The torso's detail from a bare-body scan (tools/body_scan.py: Artec's, CC BY 3.0) - its colour ratio around 1
    and its relief, rows bottom first as Blender's pixels; None when not made."""
    folder = paths.GENERATED / "skin"
    if not (folder / "body_1002_relief.png").exists():
        return None
    import OpenImageIO as oiio

    def read(name):
        buf = oiio.ImageBuf(str(folder / name))
        return np.asarray(buf.get_pixels(oiio.FLOAT), np.float32)[::-1, :, :3]

    colour = read("body_1002_colour.png") * 2.0
    return {"ratio": colour, "cover": np.abs(colour - 1.0).max(-1) > 1e-3, "relief": read("body_1002_relief.png")}


def _body_tiles(body, out: Path, stems: dict, body_srgb: np.ndarray, props, tables, scan: dict | None = None) -> None:
    """Tiles 1002-1005: the plain body skin with its coloured regions (areolae, nails, genitals) by the tone model,
    the nails shinier; the other channels flat. `scan` (_body_scan, a man's skin): the torso's colour detail and
    relief from a bare-body scan on 1002 - CC5's body maps carry real skin and definition (inputs audit row 10); its
    own areolas there in place of MakeHuman's mask."""
    own = np.array(skin_optics.Skin(props.melanin, props.eumelanin, props.blood).linear_rgb(tables))
    ratio = {}
    for region, (factor, added, blood) in REGIONS.items():
        skin = skin_optics.Skin(props.melanin * factor + added, props.eumelanin, props.blood * blood)
        ratio[region] = np.array(skin.linear_rgb(tables)) / own
    base = _decode(body_srgb)
    for number in maps.TILES[1:]:
        _bake_uv(body, number)
        with_scan = scan is not None and number == 1002
        masks = _bake(body, "EMIT", _masks_of(), BODY_SCAN_SIZE if with_scan else BODY_SIZE)
        colour = np.broadcast_to(base, masks.shape).copy()
        for k, region in enumerate(("areolae", "nails", "genitals")):
            m = _blur(np.clip(masks[..., k], 0.0, 1.0), MASK_BLUR)[..., None]
            if with_scan and region == "areolae":
                m = m * (1.0 - scan["cover"][..., None])  # the scan's own areolas there
            colour *= 1.0 + m * (ratio[region] - 1.0)
        if with_scan:
            colour *= scan["ratio"]
        maps.write_png(out / f"{stems['base_color']}.{number}.png", _encode(colour))
        nails = _blur(np.clip(masks[..., 1], 0.0, 1.0), MASK_BLUR)
        rough = FLAT["roughness"] + nails * (NAIL_ROUGHNESS - FLAT["roughness"])
        maps.write_png(out / f"{stems['roughness']}.{number}.png", np.repeat(rough[..., None], 3, axis=2))
        for channel in ("cavity", "height"):
            flat = np.broadcast_to(np.full(3, FLAT[channel], np.float32), (FLAT_SIZE, FLAT_SIZE, 3))
            maps.write_png(out / f"{stems[channel]}.{number}.png", flat, "8")
        normal = scan["relief"] if with_scan else np.broadcast_to((0.5, 0.5, 1.0), (FLAT_SIZE, FLAT_SIZE, 3))
        maps.write_png(out / f"{stems['normal']}.{number}.png", normal, "16")
    _bake_uv(body, 1001)


def _border_colour(body, head_srgb: np.ndarray) -> np.ndarray | None:
    """The head tile's own colour along its border with the body's tiles (the mean over the head tile's polygons that
    share an edge with another tile's, sRGB) - the body tiles take it, so the two meet without a step (the design's
    piece 4: seam-continuous; the clean-input gate showed a colour seam across the chest and patches at the shoulders)."""
    me = body.data
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[maps.UV].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    tiles = np.array([1001 + int(np.floor(uv[list(p.loop_indices), 0].mean())) for p in me.polygons])
    owner: dict = {}
    for p in me.polygons:
        for key in p.edge_keys:
            owner.setdefault(key, set()).add(int(tiles[p.index]))
    h, w = head_srgb.shape[:2]
    mask = np.zeros((h, w), bool)
    for p in me.polygons:
        if tiles[p.index] != 1001 or not any(len(owner[k]) > 1 for k in p.edge_keys):
            continue
        for li in p.loop_indices:  # the border polygons' corners (rows bottom first, as Blender's pixels)
            u, v = uv[li]
            x, y = min(int(u * w), w - 1), min(int(v * h), h - 1)
            mask[max(y - 3, 0) : y + 4, max(x - 3, 0) : x + 4] = True
    colour = head_srgb[mask]
    colour = colour[colour.max(axis=1) > 0.02]
    return np.median(colour, axis=0) if len(colour) > 50 else None


def _module_scan_list():
    """tools/face_test/scan_list.py (its scans and their credits)."""
    spec = importlib.util.spec_from_file_location("scan_list", str(ROOT / "tools" / "face_test" / "scan_list.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _melanin_for(linear_rgb: np.ndarray, props, tables) -> float:
    """The melanin whose skin (at the character's eumelanin and blood) is as light as `linear_rgb` (luminance;
    bisection - lightness falls as melanin rises; tools/build_library.py's melanin_for by luminance)."""
    target = float(np.asarray(linear_rgb) @ LUMA)
    low, high = 0.0, 0.5
    for _ in range(40):
        mid = (low + high) / 2
        lum = float(np.array(skin_optics.Skin(mid, props.eumelanin, props.blood).linear_rgb(tables)) @ LUMA)
        low, high = (mid, high) if lum > target else (low, mid)
    return round((low + high) / 2, 5)


def _fill(colour: np.ndarray, cover: np.ndarray) -> np.ndarray:
    """Texels the scan didn't reach filled from their surroundings (pull-push: averages of the covered ones down a
    pyramid, pushed back up), so the bake's edges have no black seam."""
    levels = [(colour * cover[..., None], cover)]
    while levels[-1][1].shape[0] > 4:
        c, w = levels[-1]
        h2, w2 = c.shape[0] // 2, c.shape[1] // 2
        c = c[: h2 * 2, : w2 * 2].reshape(h2, 2, w2, 2, 3).sum((1, 3))
        w = w[: h2 * 2, : w2 * 2].reshape(h2, 2, w2, 2).sum((1, 3))
        levels.append((c, w))
    c, w = levels[-1]
    filled = c / np.maximum(w, 1e-6)[..., None]
    for c, w in reversed(levels[:-1]):
        up = np.repeat(np.repeat(filled, 2, 0), 2, 1)[: c.shape[0], : c.shape[1]]
        own = c / np.maximum(w, 1e-6)[..., None]
        filled = np.where((w > 0)[..., None], own, up)
    return filled


def build(key: str, colour: Path | None = None, name: str | None = None, library: str | None = None,
          composed: int | None = None) -> Path:
    """`colour`: a HeadTile colour map in place of the character's painted face - a scan's own bake
    (`.dev/facetest/scans/<scan>/bake_colour.png`, its `bake_cover.png` beside it), kept as the scan shows it, the head
    tile's other channels flat - a local test of scan colour against the painting (the part-by-part gate); `name` and
    `library` then name the skin and keep it out of the user's library. `composed`: a composition's seed instead
    (`tools/face_test/skin_base.py compose SEED`: `scans/base_char<SEED>.npy`, its ratio around 1 in HeadTile, and its
    `.json` with the scans' blended tone) - the colour is that tone times the ratio, all from scans, no painting."""
    folder = CHARS / key
    bpy.ops.wm.open_mainfile(filepath=str(folder / "round.blend"))
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 1
    scene.render.threads_mode, scene.render.threads = "FIXED", 6
    body = next(o for o in bpy.data.objects if o.juststage.kind == "HUMAN")
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    maps.add_layout(body)
    _bake_uv(body)
    name = name or NAMES[key]
    out = OUT / (key if colour is None and composed is None else name.replace(" ", "_"))  # a test never over Daniel's
    out.mkdir(parents=True, exist_ok=True)
    stems = {c: f"{name} skin.{c}" for c in maps.CHANNELS}
    albedo = _source("albedo", folder)
    corner = _pixels(albedo)[-1, -1, :3]  # the face test's reserved corner (0.995, 0.995): the plain body skin
    props = body.juststage
    props.melanin = MELANIN[key]
    tables = skin_optics.load_tables(paths.FETCHED / "optics")
    tone = skin_optics.Skin(props.melanin, props.eumelanin, props.blood).linear_rgb(tables)
    hue = _face_test_gain(body)
    if composed is not None:
        scans_dir = ROOT / ".dev" / "facetest" / "scans"
        ratio = np.load(scans_dir / f"base_char{composed}.npy").astype(np.float32)[::-1]  # Blender's rows bottom-up
        params = json.loads((scans_dir / f"base_char{composed}.json").read_text())
        tone = np.array(params["tone"], np.float32)
        props.melanin = _melanin_for(tone, props, tables)  # the scattering and the tone record at the scans' own tone
        filled = _encode(np.clip(ratio * tone, 0.0, 1.0))
        corner = _encode(tone)
        albedo = bpy.data.images.new("composed colour", filled.shape[1], filled.shape[0])
        albedo.colorspace_settings.name = "Non-Color"
        albedo.pixels.foreach_set(np.dstack([filled, np.ones(filled.shape[:2])]).astype(np.float32).ravel())
        hue = np.ones(3)
        colour = scans_dir / f"base_char{composed}.npy"  # the flat-channel path below
    elif colour is not None:
        scan_image = bpy.data.images.load(str(colour), check_existing=False)
        cover_image = bpy.data.images.load(str(colour.with_name("bake_cover.png")), check_existing=False)
        for image in (scan_image, cover_image):
            image.colorspace_settings.name = "Non-Color"  # as stored
        scan, cover = _pixels(scan_image)[..., :3], _pixels(cover_image)[..., 0]
        covered = cover > 0.5
        filled = _fill(scan, covered.astype(np.float32))
        corner = np.median(scan[covered], axis=0)  # the scan's own skin for the body tiles
        albedo = bpy.data.images.new("scan colour", filled.shape[1], filled.shape[0])
        albedo.colorspace_settings.name = "Non-Color"
        albedo.pixels.foreach_set(np.dstack([filled, np.ones(filled.shape[:2])]).astype(np.float32).ravel())
        hue = np.ones(3)
    for channel in ("base_color", "roughness", "cavity", "height"):
        if composed is not None and channel == "roughness":  # the face's regions' shine (make_face_regions.py)
            regions = bpy.data.images.load(str(paths.GENERATED / "skin" / "face_regions.png"), check_existing=False)
            regions.colorspace_settings.name = "Non-Color"
            rough = _pixels(regions)[..., 1]
            maps.write_png(out / f"{stems[channel]}.1001.png", np.repeat(rough[..., None], 3, axis=2))
            continue
        if colour is not None and channel != "base_color":
            flat = np.broadcast_to(np.full(3, FLAT[channel], np.float32), (FLAT_SIZE, FLAT_SIZE, 3))
            maps.write_png(out / f"{stems[channel]}.1001.png", flat, "8" if channel != "height" else "16")
            continue
        source = albedo if channel == "base_color" else _source(channel, folder)
        baked = _bake(body, "EMIT", _emission_of(source))
        if channel == "base_color" and colour is not None:
            pass  # the scan's colour as it is
        elif channel == "base_color":  # the face test's hue; our tone model's brightness at this melanin
            linear = _decode(baked) * hue
            skin = linear[linear.sum(axis=2) > 0.01]
            scale = float(np.array(tone) @ LUMA) / float(np.median(skin @ LUMA))
            baked = _encode(linear * scale)
            corner = _encode(_decode(corner) * hue * scale)
            print(f"{name}: colour x{scale:.3f} to melanin {props.melanin}'s brightness")
        maps.write_png(out / f"{stems[channel]}.1001.png", baked, "8" if channel != "height" else "16")
        print(f"{name}: {channel} baked")
    if colour is None:
        baked = _bake(body, "NORMAL", _normals_of(_source("normal", folder), _source("painted", folder)))
    elif composed is not None and params.get("relief_file"):  # the scans' own folds and lines (skin_base._relief)
        xy = np.load(ROOT / ".dev" / "facetest" / "scans" / params["relief_file"]).astype(np.float32)[::-1]
        z = np.sqrt(np.clip(1.0 - (xy ** 2).sum(-1), 0.0, 1.0))
        relief = bpy.data.images.new("scan relief", xy.shape[1], xy.shape[0], alpha=False, float_buffer=True)
        relief.colorspace_settings.name = "Non-Color"
        relief.pixels.foreach_set(np.dstack([xy * 0.5 + 0.5, z, np.ones_like(z)]).astype(np.float32).ravel())
        baked = _bake(body, "NORMAL", _tangent_normals_of(relief))
        print(f"{name}: the scans' relief baked to the head tile")
    else:
        baked = np.broadcast_to(np.array((0.5, 0.5, 1.0), np.float32), (FLAT_SIZE, FLAT_SIZE, 3))
    maps.write_png(out / f"{stems['normal']}.1001.png", baked, "16")
    head_image = bpy.data.images.load(str(out / f"{stems['base_color']}.1001.png"), check_existing=False)
    head_image.colorspace_settings.name = "Non-Color"  # as stored (sRGB-encoded), like `corner`
    head = _pixels(head_image)[..., :3]
    border = _border_colour(body, head)
    if border is not None:
        print(f"{name}: the body's colour from the head tile's border {np.round(border, 3)} (was {np.round(corner, 3)})")
        corner = border
    man = composed is not None and params.get("sex") == "m"  # one man's torso: men's skins only (design piece 8)
    _body_tiles(body, out, stems, corner, props, tables, _body_scan() if man else None)
    print(f"{name}: normal baked to tangent space")
    for layer in body.data.uv_layers:
        layer.active_render = layer.name == "UVMap"
    body.data.uv_layers.remove(body.data.uv_layers["bake"])
    # the skin material: the chromophore model's scattering (material.py), the maps on it, at the character's tone
    old = props.skin_material
    props.skin_material = None
    skin = skin_optics.Skin(props.melanin, props.eumelanin, props.blood)
    mat = material.apply(body, skin, props.oiliness)
    record = mat.juststage
    record.map_melanin, record.map_eumelanin, record.map_blood = props.melanin, props.eumelanin, props.blood
    maps.build_material(mat, {c: maps.tiled_image(out, s) for c, s in stems.items()})  # the shared clean pore tile
    maps.set_gain(mat, tuple(skin.linear_rgb(tables)))
    if old is not None:
        props.skin_material = mat
    extra = {"library": library} if library else {}
    provenance, licence = PROVENANCE, LICENCE
    if composed is not None:  # colour from scans only: their credits, no painting
        scans = _module_scan_list().SCANS
        used = list(params["mid_from"]) + [params["fine_from"][0]]
        credits = "; ".join(dict.fromkeys(scans[n]["credit"] for n in used))
        provenance = (f"JustStage composed skin (tools/face_test/skin_base.py compose {composed}: colour from "
                      f"{', '.join(params['mid_from'])}, pores from {params['fine_from'][0]}); scans: {credits}")
        licence = "CC-BY-4.0 (scans) / CC-BY-3.0 (Lee Perry-Smith's scan, where used)"
    result = api.run("juststage.library.save", character=props.character_id, catalog="Skins", name=f"{name} skin",
                     provenance=provenance, licence=licence, **extra)  # fmt: skip
    print(f"{name}: {result}")
    return result


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if argv[:1] == ["--composed"]:  # -- --composed SEED KEY LIBRARY [NAME]: a scan composition ("-": the user's library)
        seed, key, lib = argv[1:4]
        name = argv[4] if len(argv) > 4 else f"Composed {seed}"
        build(key, None, name, None if lib == "-" else lib, composed=int(seed))
        return
    if argv[:1] == ["--scan"]:  # -- --scan SCAN KEY LIBRARY: a scan's colour on KEY's character (a local test)
        scan, key, lib = argv[1:4]
        build(key, ROOT / ".dev" / "facetest" / "scans" / scan / "bake_colour.png", f"Scan {scan}", lib)
        return
    for key in argv or list(NAMES):
        build(key)


if __name__ == "__main__":
    main()
