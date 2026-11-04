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
PORES = ROOT / ".dev" / "facetest" / "pores_lps.png"  # the Lee Perry-Smith scan's cheek tile (RESEARCH §10)
OUT = ROOT / ".dev" / "skins"  # the baked tiles before they are packed
NAMES = {"man_a": "Daniel", "amara": "Amara", "walter": "Walter", "mei": "Mei"}
#: each character's melanin as the face test made it (face_character.py's FACETEST_MELANIN; the first man the clay's
#: default) - its stored colour map is brought to that tone's brightness: the face test levelled every map to one light
#: skin and made dark people dark by the scene's exposure (test_face_project.py's calibration), fine for its renders,
#: wrong for a skin
MELANIN = {"man_a": 0.025, "amara": 0.18, "walter": 0.02, "mei": 0.03}
LUMA = np.array([0.2126, 0.7152, 0.0722])  # Rec.709
SIZE, BODY_SIZE = 4096, 256
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


def _bake_uv(body) -> None:
    """A UV layer for baking tile 1001 as a plain 0-1 image: the head's loops where the UDIM layer has them, the rest
    pushed off the image."""
    me = body.data
    uv, tile = maps.layout()
    loop_tile = np.repeat(tile, 4)  # hm08 is all quads
    flat = uv.copy()
    flat[loop_tile != 1001] += 5.0
    layer = me.uv_layers.get("bake") or me.uv_layers.new(name="bake")
    layer.data.foreach_set("uv", flat.ravel())
    me.uv_layers.active = layer
    for other in me.uv_layers:
        other.active_render = other.name == "bake"


def _bake(body, kind: str, build) -> np.ndarray:
    """One bake into a fresh 4096² float image through a temporary material made by `build(nodes, links, out)`."""
    mat = bpy.data.materials.new("bake")
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    build(nt.nodes, nt.links, out)
    target = bpy.data.images.new("bake target", SIZE, SIZE, alpha=False, float_buffer=True)
    target.colorspace_settings.name = "Non-Color"
    node = nt.nodes.new("ShaderNodeTexImage")
    node.image = target
    nt.nodes.active = node
    slots = body.data.materials
    saved = list(slots)
    slots.clear()
    slots.append(mat)
    try:
        bpy.ops.object.bake(type=kind, normal_space="TANGENT", margin=MARGIN, margin_type="EXTEND", use_clear=True)
        return _pixels(target)[..., :3].copy()
    finally:
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


def build(key: str) -> Path:
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
    name = NAMES[key]
    out = OUT / key
    out.mkdir(parents=True, exist_ok=True)
    stems = {c: f"{name} skin.{c}" for c in maps.CHANNELS}
    albedo = _source("albedo", folder)
    corner = _pixels(albedo)[-1, -1, :3]  # the face test's reserved corner (0.995, 0.995): the plain body skin
    props = body.juststage
    props.melanin = MELANIN[key]
    tables = skin_optics.load_tables(paths.FETCHED / "optics")
    tone = skin_optics.Skin(props.melanin, props.eumelanin, props.blood).linear_rgb(tables)
    hue = _face_test_gain(body)
    for channel in ("base_color", "roughness", "cavity", "height"):
        source = albedo if channel == "base_color" else _source(channel, folder)
        baked = _bake(body, "EMIT", _emission_of(source))
        if channel == "base_color":  # the face test's hue; our tone model's brightness at this melanin
            linear = _decode(baked) * hue
            skin = linear[linear.sum(axis=2) > 0.01]
            scale = float(np.array(tone) @ LUMA) / float(np.median(skin @ LUMA))
            baked = _encode(linear * scale)
            corner = _encode(_decode(corner) * hue * scale)
            print(f"{name}: colour x{scale:.3f} to melanin {props.melanin}'s brightness")
        maps.write_png(out / f"{stems[channel]}.1001.png", baked, "8" if channel != "height" else "16")
        fill = corner if channel == "base_color" else np.full(3, FLAT[channel], np.float32)
        for number in maps.TILES[1:]:
            maps.write_png(
                out / f"{stems[channel]}.{number}.png", np.broadcast_to(fill, (BODY_SIZE, BODY_SIZE, 3)), "8"
            )
        print(f"{name}: {channel} baked")
    baked = _bake(body, "NORMAL", _normals_of(_source("normal", folder), _source("painted", folder)))
    maps.write_png(out / f"{stems['normal']}.1001.png", baked, "16")
    for number in maps.TILES[1:]:
        maps.write_png(
            out / f"{stems['normal']}.{number}.png", np.broadcast_to((0.5, 0.5, 1.0), (BODY_SIZE, BODY_SIZE, 3)), "16"
        )
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
    pores = bpy.data.images.load(str(PORES), check_existing=False)
    pores.pack()
    maps.build_material(mat, {c: maps.tiled_image(out, s) for c, s in stems.items()}, pores)
    maps.set_gain(mat, tuple(skin.linear_rgb(tables)))
    if old is not None:
        props.skin_material = mat
    result = api.run("juststage.library.save", character=props.character_id, catalog="Skins", name=f"{name} skin",
                     provenance=PROVENANCE, licence=LICENCE)  # fmt: skip
    print(f"{name}: {result}")
    return result


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    for key in argv or list(NAMES):
        build(key)


main()
