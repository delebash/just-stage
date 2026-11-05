# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The CC5 benchmark's Blender side (TASKS "FABLE ON THE PLAN", item 3; CC5 is the standard): CC5 is driven through
its MCP bridge (memory `cc5-control`), our character is rendered here the same way.

    python tools/dev.py blender -b --python tools/gate/cc5_bench.py -- sphere
        an 18% grey sphere as FBX for CC5 (`.dev/gate/cc5/grey_sphere.fbx`): the image light's direction and strength
        read off it in both apps, as the gate's sphere does between EEVEE and Cycles
Local tests may use CC5's content (the user, 2026-11-05: AGENTS.md clean-room) - e.g. a CC5 character in our stage
(`render --cc5-blend`); nothing of it ships or enters our data."""

from __future__ import annotations

import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".dev" / "gate" / "cc5"
SPHERE_RADIUS_M = 0.10
GREY = 0.18  # linear, the gate's sphere
SPHERE_IN_SCENE_M = 0.035  # the gate sphere's radius


def sphere() -> Path:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=SPHERE_RADIUS_M)
    obj = bpy.context.active_object
    obj.name = "JustStage grey sphere"
    bpy.ops.object.shade_smooth()
    mat = bpy.data.materials.new("grey 18")
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (GREY, GREY, GREY, 1.0)
    bsdf.inputs["Roughness"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    obj.data.materials.append(mat)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "grey_sphere.fbx"
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, global_scale=1.0, apply_unit_scale=True)
    return path


def render(out: Path, engine: str, lens: float, camera, target, world_rotation_deg: float, lights: bool, size: int,
           sphere_at=None, mirror_lights: bool = False, exposure: float | None = None, pupils=None,
           world_strength: float | None = None, cc5_blend: Path | None = None, our_skin: bool = False,
           view_transform: str | None = None) -> Path:
    """The gate scene (`.dev/gate/gate_scene.blend`: Daniel, the stage) rendered for the comparison with CC5: today's
    live-view skin synced first (the scene predates it), the key and rim on or off, the image light turned about Z
    by `world_rotation_deg`, a square frame through a camera at `camera` looking at `target` (metres, Blender's Z up)."""
    import importlib
    import math

    from mathutils import Vector

    scene = bpy.context.scene
    material = importlib.import_module("bl_ext.system.juststage.modules.skin.material")
    body = next(o for o in scene.objects if o.juststage.character_id and not o.juststage.part_of)
    material.sync_live(body.juststage.skin_material)
    if cc5_blend is not None:  # Blender resolves a bare relative path from C:\ (seen 2026-11-05)
        swap_in_cc5_character(cc5_blend if cc5_blend.is_absolute() else ROOT / cc5_blend, our_skin)
    if view_transform is not None:  # e.g. "Khronos PBR Neutral" against our AgX look
        scene.view_settings.view_transform = view_transform
    STAGE_TARGET = Vector((0.0, 0.0, 1.35))  # the key's and rim's aim (`.dev/gate/meta.json` lights)
    for obj in scene.objects:
        if obj.type == "LIGHT":
            obj.hide_render = not lights
            if mirror_lights:  # the stage's lights to the other side (x -> -x), aimed again at the stage's target
                obj.location.x = -obj.location.x
                obj.rotation_euler = (STAGE_TARGET - obj.location).to_track_quat("-Z", "Y").to_euler()
    if exposure is not None:
        scene.view_settings.exposure = exposure
    nodes, links = scene.world.node_tree.nodes, scene.world.node_tree.links
    env = next(n for n in nodes if n.type == "TEX_ENVIRONMENT")
    mapping = next((n for n in nodes if n.type == "MAPPING"), None)
    if mapping is None:
        coords, mapping = nodes.new("ShaderNodeTexCoord"), nodes.new("ShaderNodeMapping")
        links.new(coords.outputs["Generated"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    mapping.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(world_rotation_deg))
    if world_strength is not None:  # the image light's Background (the one the environment texture feeds)
        light = next(lk.to_node for lk in env.outputs["Color"].links if lk.to_node.type == "BACKGROUND")
        light.inputs["Strength"].default_value = world_strength
    if sphere_at is not None:
        bpy.ops.import_scene.fbx(filepath=str(OUT / "grey_sphere.fbx"))
        ball = bpy.context.selected_objects[0]
        ball.location = Vector(sphere_at)
        ball.scale = (SPHERE_IN_SCENE_M / SPHERE_RADIUS_M,) * 3  # as in CC5 (scaled to 3.5 cm there too)
    cam = scene.objects["face camera"]
    cam.data.sensor_fit, cam.data.sensor_width = "HORIZONTAL", 36.0  # pupil_camera's model
    if pupils is not None:
        camera, target = pupil_camera(pupils, size, lens)
    cam.location = Vector(camera)
    cam.rotation_euler = (Vector(target) - Vector(camera)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    scene.camera = cam
    scene.render.engine = {"eevee": "BLENDER_EEVEE", "cycles": "CYCLES"}[engine]
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    # the scene's own look (AgX, as the live view shows it): the gate scene was saved with the map writer's
    # "Standard" override (blender_gate.py _write), which clipped the first run's PNGs (found 2026-11-05)
    scene.render.image_settings.color_management = "FOLLOW_SCENE"
    out = out if out.is_absolute() else ROOT / out  # Blender resolves a bare relative path from C:\ (seen 2026-11-05)
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    return out


def _pupil(points):
    """An eyeball's pupil: its centre pushed to its front (the character faces -Y)."""
    from mathutils import Vector

    centre = sum(points, Vector()) / len(points)
    return Vector((centre.x, min(p.y for p in points), centre.z))


def _pupils() -> list:
    """The visible character's two pupils: ours (`<name>.eyeLeft` / `.eyeRight`), or an imported CC5 character's (the
    faces of its `Std_Eye_L` / `Std_Eye_R` materials)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eyes: dict[str, list] = {}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        mesh = obj.evaluated_get(depsgraph).data
        if obj.name.endswith((".eyeLeft", ".eyeRight")):
            eyes[obj.name] = [obj.matrix_world @ v.co for v in mesh.vertices]
            continue
        names = [slot.material.name if slot.material else "" for slot in obj.material_slots]
        for poly in mesh.polygons:
            name = names[poly.material_index] if poly.material_index < len(names) else ""
            if name.startswith(("Std_Eye_L", "Std_Eye_R")):
                eyes.setdefault(name[:9], []).extend(obj.matrix_world @ mesh.vertices[i].co for i in poly.vertices)
    return [_pupil(points) for points in eyes.values()]


def pupil_camera(pixels: tuple[float, float, float, float], size: int, lens: float, sensor_mm: float = 36.0):
    """A level camera (looking along +Y, as CC5's front view) that puts the character's pupils on `pixels` (image-left
    x, y, image-right x, y, rows from the top) of a `size`-square frame - so our render frames the face as a CC5 capture
    does without reading CC5's camera (its sensor model isn't exposed)."""
    from mathutils import Vector

    left, right = sorted(_pupils(), key=lambda p: p.x)  # the camera looks along +Y: image right is +X
    x1, y1, x2, y2 = pixels
    depth = lens / sensor_mm * size * (right.x - left.x) / (x2 - x1)
    per_px = depth * sensor_mm / (lens * size)  # metres a pixel at the pupils' depth
    mid = (left + right) / 2
    camera = Vector((mid.x - ((x1 + x2) / 2 - size / 2) * per_px, mid.y - depth,
                     mid.z - (size / 2 - (y1 + y2) / 2) * per_px))
    return camera, camera + Vector((0.0, 1.0, 0.0))


#: our skin BSDF's values put on a CC5 character's skin (`--our-skin`): everything but its maps
SKIN_INPUTS = ("Roughness", "IOR", "Subsurface Weight", "Subsurface Radius", "Subsurface Scale", "Subsurface IOR",
               "Subsurface Anisotropy", "Specular IOR Level", "Specular Tint", "Coat Weight", "Coat Roughness",
               "Coat IOR", "Sheen Weight", "Sheen Roughness", "Sheen Tint")


def swap_in_cc5_character(blend: Path, our_skin: bool) -> None:
    """A CC5 character in place of ours - a LOCAL TEST ONLY (AGENTS.md clean-room: nothing of it ships or enters our
    data). `blend`: the character as Reallusion's CC Blender Tools imported it from CC5's Blender Pipeline export
    (its materials rebuilt from the export's JSON - CC5's own route into Blender; built for EEVEE or Cycles, so the
    file matches the engine). Ours hidden, its meshes and armature appended. `our_skin`: its skin materials replaced
    by a Principled BSDF on our skin's values (scattering, specular, coat, sheen) and our live-view twin, fed only its
    colour and normal maps (`<blend dir>/<name>.fbm/Std_Skin_*_Diffuse / _Normal`) - so against the plain run the
    shader is the one factor that changes."""
    import importlib

    scene = bpy.context.scene
    material = importlib.import_module("bl_ext.system.juststage.modules.skin.material")
    body = next(o for o in scene.objects if o.juststage.character_id and not o.juststage.part_of)
    ours = material.principled(body.juststage.skin_material)
    for obj in scene.objects:
        if obj.juststage.character_id or obj.juststage.part_of:
            obj.hide_render = obj.hide_viewport = True
    with bpy.data.libraries.load(str(blend), link=False) as (src, dst):
        dst.objects = list(src.objects)
    imported = [o for o in dst.objects if o is not None and o.type in {"MESH", "ARMATURE"} and o.name != "Cube"]
    for obj in imported:
        scene.collection.objects.link(obj)
    for obj in dst.objects:  # the source file's own camera, light and cube stay out
        if obj is not None and obj not in imported:
            bpy.data.objects.remove(obj)
    print("CC5 character:", sorted(o.name for o in imported))
    if not our_skin:
        return
    maps = next(blend.parent.glob("*.fbm"))
    done = {}
    for obj in imported:
        for slot in getattr(obj, "material_slots", ()):
            name = slot.material.name if slot.material else ""
            if not name.startswith("Std_Skin_"):
                continue
            if name not in done:
                mat = bpy.data.materials.new(f"{name} (our skin)")
                nodes, links = mat.node_tree.nodes, mat.node_tree.links
                bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
                colour = nodes.new("ShaderNodeTexImage")
                colour.image = bpy.data.images.load(str(maps / f"{name}_Diffuse.jpg"))
                normal_map = nodes.new("ShaderNodeTexImage")
                normal_map.image = bpy.data.images.load(str(maps / f"{name}_Normal.jpg"))
                normal_map.image.colorspace_settings.name = "Non-Color"
                normal = nodes.new("ShaderNodeNormalMap")
                links.new(colour.outputs["Color"], bsdf.inputs["Base Color"])
                links.new(normal_map.outputs["Color"], normal.inputs["Color"])
                links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
                bsdf.subsurface_method = ours.subsurface_method
                for key in SKIN_INPUTS:
                    if not ours.inputs[key].is_linked:
                        bsdf.inputs[key].default_value = ours.inputs[key].default_value
                material.sync_live(mat)
                done[name] = mat
            slot.material = done[name]
    print("CC5 skin on our values:", sorted(done))


def sphere_light(png: Path, centre: tuple[float, float], radius: float) -> dict:
    """The grey sphere's light, read the same way off any app's display image (CC5's viewport gives no linear data):
    direction - the first moment of the disc's luminance (length = how directional, angle in the image, 0 = right,
    90 = up); contrast - its 95th over 5th percentile; the five brightness bands' means, dark to lit."""
    import numpy as np

    img = bpy.data.images.load(str(png), check_existing=False)
    w, h = img.size
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    rgb = px.reshape(h, w, 4)[::-1, :, :3]  # Blender's rows run bottom-up
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
    yy, xx = np.mgrid[0:h, 0:w]
    dx, dy = (xx - centre[0]) / radius, (centre[1] - yy) / radius
    inside = np.hypot(dx, dy) < 0.95
    weight = lum[inside] / lum[inside].sum()
    mx, my = float((dx[inside] * weight).sum()), float((dy[inside] * weight).sum())
    values = lum[inside]
    qs = np.quantile(values, [0, 0.2, 0.4, 0.6, 0.8, 1.0])
    return {
        "direction": round(float(np.hypot(mx, my)), 3),
        "angle_deg": round(float(np.degrees(np.arctan2(my, mx))), 1),
        "contrast_p95_p5": round(float(np.quantile(values, 0.95) / max(np.quantile(values, 0.05), 1e-4)), 2),
        "bands": [round(float(values[(values >= qs[i]) & (values <= qs[i + 1])].mean()), 4) for i in range(5)],
    }


def _vec(text: str) -> tuple[float, float, float]:
    x, y, z = (float(v) for v in text.split(","))
    return x, y, z


if __name__ == "__main__":
    import argparse

    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if args[:1] == ["sphere"]:
        print("wrote", sphere())
    elif args[:1] == ["render"]:
        p = argparse.ArgumentParser(prog="cc5_bench.py -- render")
        p.add_argument("--out", type=Path, required=True)
        p.add_argument("--engine", choices=("eevee", "cycles"), default="eevee")
        p.add_argument("--lens", type=float, default=85.0)
        p.add_argument("--camera", type=_vec, default=(-0.22, -0.88, 1.66))
        p.add_argument("--target", type=_vec, default=(0.0, -0.128, 1.593))  # the gate's face camera (meta.json)
        p.add_argument("--world-rotation", type=float, default=0.0)
        p.add_argument("--lights", choices=("on", "off"), default="on")
        p.add_argument("--size", type=int, default=1440)
        p.add_argument("--sphere-at", type=_vec, default=None)
        p.add_argument("--mirror-lights", action="store_true")
        p.add_argument("--exposure", type=float, default=None)
        p.add_argument("--pupils", type=lambda t: tuple(float(v) for v in t.split(",")), default=None,
                       help="x1,y1,x2,y2: frame so the pupils land on these pixels (overrides --camera / --target)")
        p.add_argument("--world-strength", type=float, default=None)
        p.add_argument("--cc5-blend", type=Path, default=None,
                       help="a CC5 character as CC Blender Tools imported it, in place of ours (local test)")
        p.add_argument("--our-skin", action="store_true", help="with --cc5-blend: its maps on our skin shader")
        p.add_argument("--view-transform", default=None)
        a = p.parse_args(args[1:])
        print("wrote", render(a.out, a.engine, a.lens, a.camera, a.target, a.world_rotation, a.lights == "on",
                              a.size, a.sphere_at, a.mirror_lights, a.exposure, a.pupils, a.world_strength,
                              a.cc5_blend, a.our_skin, a.view_transform))  # fmt: skip
    elif args[:1] == ["sphere-light"]:  # -- sphere-light PNG CX CY RADIUS (pixels, rows from the top)
        import json

        print("SPHERE", json.dumps(sphere_light(Path(args[1]), (float(args[2]), float(args[3])), float(args[4]))))
