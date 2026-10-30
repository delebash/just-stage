# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, stage 3 (processor) and 4 (card): the painted views projected onto the head's texture — only what the AI
changed against the clay view (their ratio), so the clay's light cancels and the calibrated skin colour stays on
average — then portraits rendered beside the unpainted head.

Run: python tools/dev.py test tools/face_test/test_face_project.py -k face_project -s
"""

import importlib
import json
import time

import bpy
import numpy as np
from mathutils import Vector

up = importlib.import_module("bl_ext.system.juststage.core.uv_projection")
DIR = "E:/Dev/3D/just-stage/.dev/facetest/"
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below")
SIZE = 4096
NECK_Z = 1.41  # the neck joint's height on this body (measured)
FADE_FROM, FADE_TO = 1.30, 1.40  # the painting fades in up the neck, so no seam where it ends


def _pixels(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(h, w, 4)[::-1]  # rows top first


def _linear(srgb):
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


def _srgb(lin):
    lin = np.clip(lin, 0.0, 1.0)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)


def _gpu(scene):
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = kind
            prefs.get_devices()
            if any(d.type == kind for d in prefs.devices):
                for d in prefs.devices:
                    d.use = d.type == kind
                break
        except TypeError:
            continue
    scene.cycles.device = "GPU"
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True


def _aim(obj, loc, target):
    obj.location = loc
    obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def test_face_project():
    t0 = time.time()
    bpy.ops.wm.open_mainfile(filepath=DIR + "face.blend")
    body = bpy.data.objects["Face"]
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    nt = len(mesh.loop_triangles)
    loops = np.empty(nt * 3, dtype=np.int64)
    verts = np.empty(nt * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("loops", loops)
    mesh.loop_triangles.foreach_get("vertices", verts)
    loops, verts = loops.reshape(-1, 3), verts.reshape(-1, 3)
    co = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    vn = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertex_normals.foreach_get("vector", vn)
    vn = vn.reshape(-1, 3)
    uvs = np.empty(len(mesh.loops) * 2, dtype=np.float32)
    mesh.uv_layers["UVMap"].data.foreach_get("uv", uvs)
    uvs = uvs.reshape(-1, 2)
    ev.to_mesh_clear()
    head = (co[verts][:, :, 2] > FADE_FROM).all(axis=1)
    (pos_map, nrm_map), mask = up.raster_uv(uvs[loops[head]], [co[verts[head]], vn[verts[head]]], SIZE)
    points = pos_map[mask].astype(np.float64)
    normals = nrm_map[mask].astype(np.float64)
    normals /= np.linalg.norm(normals, axis=1, keepdims=True) + 1e-12
    print(f"\nrasterised {head.sum()} head triangles → {mask.sum()} texels in {time.time() - t0:.0f}s")
    cams = json.load(open(DIR + "cameras.json"))
    accum = np.zeros((len(points), 3))
    wsum = np.zeros(len(points))
    for view in VIEWS:
        cam = cams[view]
        painted = _linear(_pixels(f"{DIR}painted_{view}.png")[..., :3])
        clay = _linear(_pixels(f"{DIR}clay_{view}.png")[..., :3])
        depth = _pixels(f"{DIR}depth_{view}.exr")[..., 0]
        ratio = painted / np.maximum(clay, 0.01)
        col, row, dist = up.project(
            points, np.array(cam["matrix_world"]), cam["lens"], cam["sensor_width"], cam["size"]
        )
        w = up.view_weights(points, normals, col, row, dist, depth, np.array(cam["matrix_world"])[:3, 3])
        edge = np.minimum.reduce([col, row, cam["size"] - 1 - col, cam["size"] - 1 - row])
        w *= np.clip(np.nan_to_num(edge) / 80.0, 0.0, 1.0)  # fade out toward the picture's frame: no seam where it ends
        r = up.sample(ratio, col, row)
        seen = w > 0.05
        r /= np.median(r[seen], axis=0)  # each view's overall brightness matched before blending
        accum += w[:, None] * r
        wsum += w
        print(f"  {view}: sees {(w > 0).mean():.0%} of the head's texels")
    covered = wsum > 1e-6
    ratio = np.ones((len(points), 3))
    ratio[covered] = accum[covered] / wsum[covered, None]
    ratio /= np.median(ratio[covered], axis=0)  # the AI's changes around the calibrated colour, not its exposure
    ratio = np.clip(ratio, 0.3, 2.5)
    # fade to the plain skin where the views barely reach (the back of the head) and down the neck
    t = np.clip((points[:, 2] - FADE_FROM) / (FADE_TO - FADE_FROM), 0.0, 1.0)
    fade = (t * t * (3 - 2 * t)) * np.clip(wsum / 0.15, 0.0, 1.0)
    ratio = 1.0 + (ratio - 1.0) * fade[:, None]
    spread = np.percentile(ratio[covered], [5, 50, 95], axis=0).round(2).tolist()
    print(f"covered {covered.mean():.0%} of the head's texels; ratio p5/p50/p95 {spread}")
    mat = body.juststage.skin_material
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    base = np.array(bsdf.inputs["Base Color"].default_value[:3])
    albedo = np.tile(base, (SIZE, SIZE, 1)).astype(np.float32)
    albedo[mask] = np.clip(base * ratio, 0.0, 1.0)
    rgba = np.ones((SIZE, SIZE, 4), dtype=np.float32)
    rgba[..., :3] = _srgb(albedo)
    image = bpy.data.images.new("Face painted albedo", SIZE, SIZE, alpha=False)
    image.colorspace_settings.name = "sRGB"
    image.pixels.foreach_set(rgba[::-1].ravel())
    image.filepath_raw = DIR + "albedo_painted.png"
    image.file_format = "PNG"
    image.save()
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.location = (-650, 300)
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    print(f"stage 3 done at {time.time() - t0:.0f}s")

    # stage 4: portraits, painted and not
    api = importlib.import_module("bl_ext.system.juststage.api")
    c = body.juststage.character_id
    for style in ("short_hedgehog", "wild_eyebrow", "basic_lashes_upper", "basic_lashes_lower"):
        api.run("juststage.hair.add", character=c, style=style, melanin=0.75, redness=0.15)
    scene = bpy.context.scene
    _gpu(scene)
    scene.view_settings.exposure = 0.0
    background = scene.world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (0.03, 0.03, 0.035, 1.0)
    head = (0.0, -0.06, 1.615)
    for name, energy, size, loc in (
        ("key", 40, 0.6, (0.55, -0.75, 1.85)),
        ("fill", 10, 1.0, (-0.8, -0.6, 1.6)),
        ("rim", 25, 0.4, (-0.3, 0.7, 1.9)),
    ):
        light = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA"))
        light.data.energy, light.data.size = energy, size
        light.visible_camera = False
        scene.collection.objects.link(light)
        _aim(light, loc, head)
    cam = scene.camera
    scene.render.resolution_x = scene.render.resolution_y = 1000
    scene.render.image_settings.file_format = "PNG"
    for shot, loc in (("front", (0.0, -1.0, 1.62)), ("34", (0.6, -0.8, 1.64))):
        _aim(cam, loc, head)
        for label, linked in (("painted", True), ("plain", False)):
            if linked and not tex.outputs["Color"].links:
                mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            if not linked:
                for link in list(tex.outputs["Color"].links):
                    mat.node_tree.links.remove(link)
            scene.render.filepath = f"{DIR}render_{shot}_{label}.png"
            t = time.time()
            bpy.ops.render.render(write_still=True)
            print(f"rendered {shot} {label} in {time.time() - t:.1f}s")
