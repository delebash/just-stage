# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The realism gate's Blender side (the review brief §10, `docs/plans/2026-11-04-realism-review-brief.md`): one library
character with today's shipped skin, the same content handed to Unreal, renders to compare. Local comparison only.

    python tools/dev.py blender -b --python tools/gate/blender_gate.py -- prepare   # CPU: scene, maps, FBX, meta
    python tools/dev.py blender -b --python tools/gate/blender_gate.py -- render    # the card: EEVEE + Cycles EXRs

Content held identical in both engines (the one factor changed is the shading): the shipped skin's maps, its tone gain
baked into the colour, the fine height map folded into the normal map (Blender's Bump node maths: n' = (-d*dH/dx,
-d*dH/dy, 1) mixed by its strength, whiteout-blended onto the normal map), the pores as a tiling micro normal at the
shipped tile size (~5.6 cm); the body's 3D-noise mottle switched off (Unreal gets no 3D noise); hair hidden in both
(the skin is what this gate isolates). Blender keeps the shipped material otherwise (coat, sheen, the pore bump).
Renders are linear EXR; tools/gate/tonemap.py puts every engine's EXR through the same AgX look."""

from __future__ import annotations

import importlib
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".dev" / "gate"
CONTENT = OUT / "content"
RENDERS = OUT / "renders"
CHARACTER = "Average man"  # the library's man wears Daniel's skin (tools/build_library.py)
SKIN_MAPS = ROOT / ".dev" / "skins" / "man_a"
SKIN_STEM = "Daniel skin"
PORES = ROOT / "extension" / "juststage" / "data" / "generated" / "skin" / "pores.png"  # the shared clean tile (maps.pore_relief)
PORE_TILE_MM = json.loads(PORES.with_suffix(".json").read_text(encoding="utf-8"))["size_mm"]
#: Unreal's Specular is F0 / 0.08; ours: IOR 1.4 (F0 0.0278) scaled by Specular IOR Level x 2, the level = cavity x 0.5
UNREAL_SPECULAR_PER_CAVITY = ((1.4 - 1) / (1.4 + 1)) ** 2 / 0.08
SCATTER = 0.5  # MetaHuman's preset scatter distance base (its MI): Unreal's profile does the scattering
#: the face camera: an 85 mm portrait 0.9 m off the face, a little to the key's side; the stage camera is startup.py's
FACE_CAMERA = (Vector((-0.22, -0.88, 1.66)), 85.0)
RESOLUTION = {"face": (2048, 2048), "stage": (1080, 1920)}

api = importlib.import_module("bl_ext.system.juststage.api")
library = importlib.import_module("bl_ext.system.juststage.core.library")
viewport = importlib.import_module("bl_ext.system.juststage.core.viewport")
startup = importlib.import_module("bl_ext.system.juststage.ui.startup")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")


# ---- images -------------------------------------------------------------------------------------------------------

def _read(path: Path) -> np.ndarray:
    """A PNG as float RGBA (0-1, as stored - no colour conversion), top row first."""
    image = bpy.data.images.load(str(path), check_existing=False)
    image.colorspace_settings.name = "Non-Color"
    w, h = image.size
    px = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(px)
    bpy.data.images.remove(image)
    return px.reshape(h, w, 4)[::-1].copy()


def _write(path: Path, rgba: np.ndarray, depth: str = "8") -> None:
    h, w = rgba.shape[:2]
    image = bpy.data.images.new(path.stem, w, h, alpha=True, float_buffer=depth == "16")
    image.colorspace_settings.name = "Non-Color"
    image.pixels.foreach_set(np.ascontiguousarray(rgba[::-1], np.float32).ravel())
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    scene = bpy.context.scene
    settings = scene.render.image_settings
    settings.file_format, settings.color_mode, settings.color_depth = "PNG", "RGBA", depth
    settings.color_management = "OVERRIDE"
    settings.view_settings.view_transform = "Standard"
    settings.linear_colorspace_settings.name = "Non-Color"
    image.save_render(str(path), scene=scene)
    bpy.data.images.remove(image)


def _fit(channel: np.ndarray, size: int) -> np.ndarray:
    """A square channel brought to `size` (the maps' sizes are powers of two: an integer ratio, nearest up)."""
    if channel.shape[0] == size:
        return channel
    k = size // channel.shape[0]
    return np.kron(channel, np.ones((k, k), channel.dtype)) if k >= 1 else channel[:: -k or 1, :: -k or 1]


def _decode(srgb):
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


def _encode(linear):
    linear = np.clip(linear, 0.0, 1.0)
    return np.where(linear <= 0.0031308, linear * 12.92, 1.055 * linear ** (1 / 2.4) - 0.055)


def _bump_normal(height: np.ndarray, texel_m: float, distance: float, strength: float) -> np.ndarray:
    """Blender's Bump node in tangent space: n' = (-d*dH/dx, -d*dH/dy, 1), mixed with flat by `strength` (rows run
    down the image: +v is up, so the row gradient is negated)."""
    gy, gx = np.gradient(height.astype(np.float64), texel_m)
    bumped = np.stack([-distance * gx, distance * gy, np.ones_like(height)], -1)
    bumped /= np.linalg.norm(bumped, axis=-1, keepdims=True)
    mixed = (1 - strength) * np.array([0.0, 0.0, 1.0]) + strength * bumped
    return mixed / np.linalg.norm(mixed, axis=-1, keepdims=True)


def _whiteout(base: np.ndarray, detail: np.ndarray) -> np.ndarray:
    out = np.concatenate([base[..., :2] + detail[..., :2], (base[..., 2] * detail[..., 2])[..., None]], -1)
    return out / np.linalg.norm(out, axis=-1, keepdims=True)


# ---- the scene ----------------------------------------------------------------------------------------------------

def _scene():
    bpy.ops.wm.read_homefile(use_empty=True)
    scene = bpy.context.scene
    viewport.setup_scene(scene)
    cam = bpy.data.objects.new("stage camera", bpy.data.cameras.new("stage camera"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    startup.new_stage(scene)
    shown = api.run("juststage.library.add", path=str(library.root() / "Characters" / f"{CHARACTER}.blend"))
    objects = [o for o in scene.objects if o.juststage.part_of == shown.character or
               o.juststage.character_id == shown.character]
    body = next(o for o in objects if o.juststage.character_id == shown.character and not o.juststage.part_of)
    face = bpy.data.objects.new("face camera", bpy.data.cameras.new("face camera"))
    scene.collection.objects.link(face)
    eyes = [o for o in objects if o.juststage.part in ("eyeLeft", "eyeRight")]
    look = sum((o.matrix_world @ (sum((Vector(c) for c in o.bound_box), Vector()) / 8) for o in eyes), Vector()) / 2
    look.z -= 0.03  # between the eyes and the nose tip
    face.location = FACE_CAMERA[0]
    face.rotation_euler = (look - face.location).to_track_quat("-Z", "Y").to_euler()
    face.data.lens = FACE_CAMERA[1]
    face.data.clip_start = 0.01
    for obj in objects:  # the skin is what this gate compares: hair and lashes out in both engines
        if obj.type == "CURVES":
            obj.hide_render = obj.hide_viewport = True
    skin = body.juststage.skin_material
    swing = skin.node_tree.nodes[maps.NODE + "mottle_swing"]
    swing.inputs["To Min"].default_value = swing.inputs["To Max"].default_value = 1.0  # no 3D noise in Unreal
    return scene, body, objects, face, look


def _tile_scale(body) -> dict[int, float]:
    """Each UDIM tile's millimetres per UV unit on the body (its rest mesh: 3D area over UV area, per tile)."""
    mesh = body.data
    uv = mesh.uv_layers[maps.UV].data
    sums: dict[int, list[float]] = {}
    for poly in mesh.polygons:
        corners = [uv[i].uv for i in poly.loop_indices]
        u = sum(c.x for c in corners) / len(corners)
        v = sum(c.y for c in corners) / len(corners)
        tile = 1001 + int(math.floor(u)) + 10 * int(math.floor(v))
        area_uv = 0.0
        for k in range(1, len(corners) - 1):
            a, b, c = corners[0], corners[k], corners[k + 1]
            area_uv += abs((b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)) / 2
        s = sums.setdefault(tile, [0.0, 0.0])
        s[0] += poly.area
        s[1] += area_uv
    return {t: 1000.0 * math.sqrt(a / uv_a) for t, (a, uv_a) in sums.items() if uv_a > 0}


def prepare() -> None:
    scene, body, objects, face, look = _scene()
    CONTENT.mkdir(parents=True, exist_ok=True)
    skin = body.juststage.skin_material
    gain = np.array(skin.node_tree.nodes[maps.NODE + "gain"].inputs[1].default_value[:3])
    scale = _tile_scale(body)
    meta = {"character": CHARACTER, "skin": SKIN_STEM, "gain": gain.tolist(), "mm_per_uv": scale, "tiles": {}}
    for tile in maps.TILES:
        base = _read(SKIN_MAPS / f"{SKIN_STEM}.base_color.{tile}.png")
        h, w = base.shape[:2]
        colour = _encode(_decode(base[..., :3]) * gain)
        _write(CONTENT / f"base_tile{tile - 1000}.png", np.concatenate([colour, np.ones((h, w, 1))], -1))
        normal = _read(SKIN_MAPS / f"{SKIN_STEM}.normal.{tile}.png")[..., :3] * 2 - 1
        height = _fit(_read(SKIN_MAPS / f"{SKIN_STEM}.height.{tile}.png")[..., 0], normal.shape[0])
        nh, nw = normal.shape[:2]
        texel_m = scale[tile] / nw / 1000.0
        fine = _bump_normal(height, texel_m, maps.HEIGHT_DISTANCE, maps.HEIGHT_STRENGTH)
        combined = _whiteout(normal / np.linalg.norm(normal, axis=-1, keepdims=True), fine)
        _write(CONTENT / f"normal_tile{tile - 1000}.png", np.concatenate([combined * 0.5 + 0.5, np.ones((nh, nw, 1))], -1), "16")
        rough = _read(SKIN_MAPS / f"{SKIN_STEM}.roughness.{tile}.png")[..., 0]
        cavity = _read(SKIN_MAPS / f"{SKIN_STEM}.cavity.{tile}.png")[..., 0]
        size = max(rough.shape[0], cavity.shape[0])
        rough, cavity = _fit(rough, size), _fit(cavity, size)
        srmf = np.stack([cavity * UNREAL_SPECULAR_PER_CAVITY, rough, np.zeros_like(rough), np.zeros_like(rough)], -1)
        _write(CONTENT / f"srmf_tile{tile - 1000}.png", srmf)
        _write(CONTENT / f"scatter_tile{tile - 1000}.png", np.full((16, 16, 4), [SCATTER, SCATTER, SCATTER, 1.0]))
        meta["tiles"][tile] = {"size": max(w, nw, size), "micro_tiling": scale[tile] / PORE_TILE_MM,
                               "sizes": {"base": w, "normal": nw, "srmf": size}}
    pores = _read(PORES)[..., 0]
    micro = _bump_normal(pores, PORE_TILE_MM / 1000.0 / pores.shape[1], maps.PORE_DISTANCE, maps.PORE_STRENGTH)
    _write(CONTENT / "micro_normal.png", np.concatenate([micro * 0.5 + 0.5, np.ones((*pores.shape, 1))], -1), "16")
    low = pores - pores.mean()
    _write(CONTENT / "micro_cavity.png", np.dstack([np.clip(1 + low * 2, 0, 1)] * 3 + [np.ones_like(pores)]))
    _write(CONTENT / "white.png", np.ones((16, 16, 4)))
    # the eyes for Unreal: each eye's look baked as plain colour (a placeholder - the eyes are not this gate's subject)
    meta["eyes"] = []
    for eye in (o for o in objects if o.juststage.part in ("eyeLeft", "eyeRight")):
        meta["eyes"].append(eye.name)
    # the stage, in Blender's metres (tools/gate/unreal_setup.py converts to Unreal's axes and centimetres)
    lights = []
    for name, _location, power, size in startup.LIGHTS:
        obj = scene.objects[name]
        lights.append({"name": name, "location": list(obj.location), "target": list(startup.LIGHTS_LOOK_AT),
                       "power_w": power, "size_m": size})
    meta["lights"] = lights
    meta["hdri"] = {"file": str(Path(bpy.data.worlds[startup.WORLD].node_tree.nodes["Environment Texture"].image
                                     .filepath_from_user()).resolve()), "strength": startup.HDRI_STRENGTH}
    meta["cameras"] = {
        "stage": {"location": list(startup.CAMERA_AT), "target": list(startup.CAMERA_LOOKS_AT), "lens": startup.LENS},
        "face": {"location": list(face.location), "target": list(look), "lens": FACE_CAMERA[1]},
    }
    meta["resolution"] = RESOLUTION
    # the mesh for Unreal: the body at the shown subdivision with one material slot per UDIM tile, the eyes
    bpy.ops.object.select_all(action="DESELECT")
    export = body.copy()
    export.data = body.data.copy()
    scene.collection.objects.link(export)
    export.name = "gate_body"
    for mod in export.modifiers:  # the renders (F12, both engines) use the render level: Unreal gets the same
        if mod.type == "MULTIRES":
            mod.levels = mod.render_levels
    meta["subdivision"] = next((m.render_levels for m in export.modifiers if m.type == "MULTIRES"), 0)
    mesh = export.data
    mesh.materials.clear()
    for tile in maps.TILES:
        mesh.materials.append(bpy.data.materials.new(f"tile_{tile}"))
    uv = mesh.uv_layers[maps.UV].data
    for poly in mesh.polygons:
        corners = [uv[i].uv for i in poly.loop_indices]
        u = sum(c.x for c in corners) / len(corners)
        poly.material_index = min(int(math.floor(u)), len(maps.TILES) - 1)
    # Unreal reads the first UV layer as UV0: the body's first is MakeHuman's own `UVMap`, which sampled our UDIM maps
    # at the wrong places (black where it met the tiles' empty space - measured 2026-11-04); the export keeps UDIM alone
    for layer in [layer for layer in mesh.uv_layers if layer.name != maps.UV]:
        mesh.uv_layers.remove(layer)
    mesh.uv_layers.active = mesh.uv_layers[maps.UV]
    mesh.uv_layers[maps.UV].active_render = True
    export.select_set(True)
    for eye in (o for o in objects if o.juststage.part in ("eyeLeft", "eyeRight")):
        eye.select_set(True)
    bpy.context.view_layer.objects.active = export
    bpy.ops.export_scene.fbx(filepath=str(OUT / "gate_body.fbx"), use_selection=True, use_mesh_modifiers=True,
                             mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False, axis_forward="-Z",
                             axis_up="Y", apply_scale_options="FBX_SCALE_UNITS")
    bpy.data.objects.remove(export)
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "gate_scene.blend"))
    print("GATE prepared:", OUT)


#: the 18% grey calibration sphere beside the head (both engines): light adds linearly, so each light is rendered
#: alone and its scale between the engines read off this sphere (tools/gate/compare.py)
SPHERE = (Vector((0.14, -0.13, 1.60)), 0.035, 0.18)
#: the light variants: each light alone, then the whole stage (the sum, rendered as a check of the linearity)
VARIANTS = ("key", "rim", "sky", "stage")


def _grey_sphere(scene) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=SPHERE[1], location=SPHERE[0])
    sphere = bpy.context.active_object
    sphere.name = "grey sphere"
    bpy.ops.object.shade_smooth()
    mat = bpy.data.materials.new("grey 18")
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (SPHERE[2], SPHERE[2], SPHERE[2], 1.0)
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    sphere.data.materials.append(mat)
    return sphere


def render() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(OUT / "gate_scene.blend"))
    scene = bpy.context.scene
    _grey_sphere(scene)
    RENDERS.mkdir(parents=True, exist_ok=True)
    settings = scene.render.image_settings
    settings.file_format, settings.color_depth, settings.exr_codec = "OPEN_EXR", "32", "ZIP"
    scene.render.film_transparent = False
    world = scene.world.node_tree.nodes
    lights = {o.name: o for o in scene.objects if o.type == "LIGHT"}
    engines = sys.argv[sys.argv.index("--") + 2:] if len(sys.argv) > sys.argv.index("--") + 2 else ["eevee", "cycles"]
    for tag in engines:
        scene.render.engine = "BLENDER_EEVEE" if tag == "eevee" else "CYCLES"
        if tag == "cycles":
            scene.cycles.device, scene.cycles.samples, scene.cycles.use_denoising = "GPU", 512, True
        for cam_name, size in RESOLUTION.items():
            scene.camera = scene.objects[f"{cam_name} camera"]
            scene.render.resolution_x, scene.render.resolution_y = size
            for variant in VARIANTS:
                lights["Key light"].hide_render = variant not in ("key", "stage")
                lights["Rim light"].hide_render = variant not in ("rim", "stage")
                world["image light"].inputs["Strength"].default_value = (
                    startup.HDRI_STRENGTH if variant in ("sky", "stage") else 0.0)
                scene.render.filepath = str(RENDERS / f"{tag}_{cam_name}_{variant}.exr")
                bpy.ops.render.render(write_still=True)
                print("GATE rendered", scene.render.filepath, flush=True)


def eyes() -> None:
    """The eyes' placeholder colours for Unreal, read from the eye shader's own settings (MPFB2's EnhancedEye: its
    white, its iris colours): the eyes are not this gate's subject - flat colours keep the face readable. (A Cycles
    colour bake of the procedural eye came out black: the colour sits inside the group's procedural tree.)"""
    bpy.ops.wm.open_mainfile(filepath=str(OUT / "gate_scene.blend"))
    meta = json.loads((OUT / "meta.json").read_text())
    eye = next(o for o in bpy.data.objects if o.juststage.part == "eyeLeft")
    node = next(n for slot in eye.material_slots if slot.material for n in slot.material.node_tree.nodes
                if n.type == "GROUP" and "IrisMajorColor" in n.inputs)
    major = list(node.inputs["IrisMajorColor"].default_value[:3])
    minor = list(node.inputs["IrisMinorColor"].default_value[:3])
    meta["eye_colours"] = {"Sclera": list(node.inputs["EyeWhiteColor"].default_value[:3]),
                           "Iris": [(a + b) / 2 for a, b in zip(major, minor)], "Pupil": [0.01, 0.01, 0.01]}
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1))
    print("GATE eye colours", meta["eye_colours"], flush=True)


if __name__ == "__main__":
    step = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "prepare"
    {"prepare": prepare, "render": render, "eyes": eyes}[step]()
