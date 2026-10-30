# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, stage 1 (processor only): the character, seven cameras around its head, a clay picture and a depth
picture from each, the cameras saved.

Run: python tools/dev.py test tools/face_test/test_face_clay.py -k face_clay -s
"""

import importlib
import json
import math
import time

import bpy
from mathutils import Vector

api = importlib.import_module("bl_ext.system.juststage.api")
OUT = "E:/Dev/3D/just-stage/.dev/facetest/"
HEAD = Vector((0.0, -0.06, 1.615))
FACE = Vector((0.0, -0.10, 1.585))  # between the eyes and the nose tip
#: (name, azimuth°, elevation°, distance m, aimed at) — four views round the head, three close on the face
VIEWS = (
    ("front", 0, 0, 0.78, HEAD),
    ("left40", 40, 0, 0.78, HEAD),
    ("right40", -40, 0, 0.78, HEAD),
    ("left90", 90, 0, 0.78, HEAD),
    ("right90", -90, 0, 0.78, HEAD),
    ("above", 0, 28, 0.78, HEAD),
    ("below", 0, -22, 0.78, HEAD),
    ("face", 0, 0, 0.40, FACE),
    ("faceleft30", 30, 0, 0.42, FACE),
    ("faceright30", -30, 0, 0.42, FACE),
)
LENS, SIZE = 85, 1024


def _depth_material():
    mat = bpy.data.materials.new("depth")
    nt = mat.node_tree
    nt.nodes.clear()
    cam = nt.nodes.new("ShaderNodeCameraData")
    em = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    comb = nt.nodes.new("ShaderNodeCombineColor")
    for s in ("Red", "Green", "Blue"):
        nt.links.new(cam.outputs["View Distance"], comb.inputs[s])
    nt.links.new(comb.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def test_face_clay():
    t0 = time.time()
    for name in [o.name for o in bpy.data.objects]:  # the empty scene's cube, light and camera
        bpy.data.objects.remove(bpy.data.objects[name])
    r = api.run("juststage.body.create", name="Face", gender=1.0)
    c = r.character
    api.run("juststage.head.set_identity", character=c, seed=3, strength=0.6)
    api.run("juststage.head.add_parts", character=c)
    api.run("juststage.skin.set_tone", character=c, melanin=0.025)
    api.run("juststage.body.subdivide", character=c, levels=1, viewport_level=1)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "OPTIX"
    scene.render.resolution_x = scene.render.resolution_y = SIZE
    world = bpy.data.worlds.new("clay")
    scene.world = world
    # even light from every side: the clay picture carries shape, not a light direction (Blender 5.x worlds light by
    # their Background node; world.color does nothing there)
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    scene.view_settings.exposure = 0.0
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    cam.data.lens = LENS
    scene.camera = cam
    depth = _depth_material()
    cams = {}
    for name, az, el, dist, target in VIEWS:
        a, e = math.radians(az), math.radians(el)
        offset = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        cam.location = target + offset
        cam.rotation_euler = (-offset).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        cams[name] = {
            "matrix_world": [list(r) for r in cam.matrix_world],
            "lens": LENS,
            "sensor_width": cam.data.sensor_width,
            "size": SIZE,
        }
        scene.view_layers[0].material_override = None
        scene.view_settings.exposure = 0.0
        scene.cycles.samples, scene.cycles.use_denoising = 64, True
        scene.cycles.filter_width = 1.5
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = f"{OUT}clay_{name}.png"
        t = time.time()
        bpy.ops.render.render(write_still=True)
        scene.view_layers[0].material_override = depth
        scene.view_settings.exposure = 0.0
        scene.cycles.samples, scene.cycles.use_denoising = 1, False
        scene.cycles.filter_width = 0.01
        scene.render.image_settings.file_format = "OPEN_EXR"
        scene.render.image_settings.color_depth = "32"
        scene.render.filepath = f"{OUT}depth_{name}.exr"
        bpy.ops.render.render(write_still=True)
        print(f"view {name}: {time.time() - t:.1f}s")
    scene.view_layers[0].material_override = None
    with open(f"{OUT}cameras.json", "w") as f:
        json.dump(cams, f, indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}face.blend", copy=True)
    print(f"stage 1 done in {time.time() - t0:.1f}s")
