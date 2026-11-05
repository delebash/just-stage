# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The CC5 benchmark's Blender side (TASKS "FABLE ON THE PLAN", item 3; CC5 is the standard): CC5 is driven through
its MCP bridge (memory `cc5-control`), our character is rendered here the same way.

    python tools/dev.py blender -b --python tools/gate/cc5_bench.py -- sphere
        an 18% grey sphere as FBX for CC5 (`.dev/gate/cc5/grey_sphere.fbx`): the image light's direction and strength
        read off it in both apps, as the gate's sphere does between EEVEE and Cycles
Nothing of CC5's is exported, baked or copied: CC5's side is its own viewport renders only (clean-room)."""

from __future__ import annotations

import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".dev" / "gate" / "cc5"
SPHERE_RADIUS_M = 0.10
GREY = 0.18  # linear, the gate's sphere


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
           sphere_at=None) -> Path:
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
    for obj in scene.objects:
        if obj.type == "LIGHT":
            obj.hide_render = not lights
    nodes, links = scene.world.node_tree.nodes, scene.world.node_tree.links
    env = next(n for n in nodes if n.type == "TEX_ENVIRONMENT")
    mapping = next((n for n in nodes if n.type == "MAPPING"), None)
    if mapping is None:
        coords, mapping = nodes.new("ShaderNodeTexCoord"), nodes.new("ShaderNodeMapping")
        links.new(coords.outputs["Generated"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    mapping.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(world_rotation_deg))
    if sphere_at is not None:
        bpy.ops.import_scene.fbx(filepath=str(OUT / "grey_sphere.fbx"))
        bpy.context.selected_objects[0].location = Vector(sphere_at)
    cam = scene.objects["face camera"]
    cam.location = Vector(camera)
    cam.rotation_euler = (Vector(target) - Vector(camera)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    scene.camera = cam
    scene.render.engine = {"eevee": "BLENDER_EEVEE", "cycles": "CYCLES"}[engine]
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    return out


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
        a = p.parse_args(args[1:])
        print("wrote", render(a.out, a.engine, a.lens, a.camera, a.target, a.world_rotation, a.lights == "on",
                              a.size, a.sphere_at))  # fmt: skip
    elif args[:1] == ["sphere-light"]:  # -- sphere-light PNG CX CY RADIUS (pixels, rows from the top)
        import json

        print("SPHERE", json.dumps(sphere_light(Path(args[1]), (float(args[2]), float(args[3])), float(args[4]))))
