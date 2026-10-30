# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, stages 3 (processor) and 4 (card): the painted views projected onto the head's texture, then the head
rendered next to the AI's own photos from the same cameras.

Colour: only what the AI changed against the clay view (their ratio), so the clay's light cancels and the calibrated
skin colour stays on average; close views count more (more of their pixels land on the face). Relief: the painted
skin's fine detail (a high-pass of its brightness) as a bump. Shine: the forehead and nose less rough than the cheeks
(skin's T-zone), cavities rougher. Light: Poly Haven's CC0 "Studio Small 09" HDRI, the background a plain grey like the
photos'.

Run: python tools/dev.py test tools/face_test/test_face_project.py -k face_project -s
"""

import importlib
import json
import time

import bpy
import numpy as np

up = importlib.import_module("bl_ext.system.juststage.core.uv_projection")
sd = importlib.import_module("bl_ext.system.juststage.core.skin_detail")
DIR = "E:/Dev/3D/just-stage/.dev/facetest/"
HDRI = "E:/Dev/3D/just-stage/.dev/cache/hdri/studio_small_09_2k.hdr"
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below", "face", "faceleft30", "faceright30")
SIZE = 4096
FADE_FROM, FADE_TO = 1.30, 1.40  # the painting fades in up the neck, so no seam where it ends
ROUGH, ROUGH_TZONE = 0.59, 0.42  # the skin material's (√0.35, Donner & Jensen) and a shinier T-zone
BUMP_STRENGTH, BUMP_DISTANCE = 0.35, 0.0006


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


def _image(name, rgb, colorspace):
    h, w = rgb.shape[:2]
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = rgb if rgb.ndim == 3 else rgb[..., None]
    image = bpy.data.images.new(name, w, h, alpha=False)
    image.colorspace_settings.name = colorspace
    image.pixels.foreach_set(rgba[::-1].ravel())
    image.filepath_raw = DIR + name.replace(" ", "_") + ".png"
    image.file_format = "PNG"
    image.save()
    return image


def _gpu(scene):
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "OPTIX"
    scene.cycles.device = "GPU"
    scene.cycles.samples = 256
    scene.cycles.use_denoising = True


def _studio_world(scene):
    """The HDRI lights the head; camera rays see plain grey, like the photos' background."""
    world = bpy.data.worlds.new("studio")
    scene.world = world
    nt = world.node_tree
    nt.nodes.clear()
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(HDRI)
    lit = nt.nodes.new("ShaderNodeBackground")
    grey = nt.nodes.new("ShaderNodeBackground")
    grey.inputs["Color"].default_value = (0.18, 0.18, 0.18, 1.0)
    path = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(env.outputs["Color"], lit.inputs["Color"])
    nt.links.new(path.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(lit.outputs["Background"], mix.inputs[1])
    nt.links.new(grey.outputs["Background"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])


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
        mw = np.array(cam["matrix_world"])
        painted = _linear(_pixels(f"{DIR}painted_{view}.png")[..., :3])
        clay = _linear(_pixels(f"{DIR}clay_{view}.png")[..., :3])
        depth = _pixels(f"{DIR}depth_{view}.exr")[..., 0]
        col, row, dist = up.project(points, mw, cam["lens"], cam["sensor_width"], cam["size"])
        w = up.view_weights(points, normals, col, row, dist, depth, mw[:3, 3])
        edge = np.minimum.reduce([col, row, cam["size"] - 1 - col, cam["size"] - 1 - row])
        w *= np.clip(np.nan_to_num(edge) / 80.0, 0.0, 1.0)  # fade out toward the picture's frame
        w *= (0.78 / np.nan_to_num(dist, nan=1e3)) ** 4  # close views count more: more of their pixels per texel
        r = up.sample(painted / np.maximum(clay, 0.01), col, row)
        seen = w > 1e-3
        r /= np.median(r[seen], axis=0)  # each view's overall brightness matched before blending
        accum += w[:, None] * r
        wsum += w
        print(f"  {view}: sees {seen.mean():.0%} of the head's texels")
    covered = wsum > 1e-6
    ratio = np.ones((len(points), 3))
    ratio[covered] = accum[covered] / wsum[covered, None]
    ratio /= np.median(ratio[covered], axis=0)  # the AI's changes around the calibrated colour, not its exposure
    ratio = np.clip(ratio, 0.3, 2.5)
    t = np.clip((points[:, 2] - FADE_FROM) / (FADE_TO - FADE_FROM), 0.0, 1.0)
    fade = (t * t * (3 - 2 * t)) * np.clip(wsum / (0.15 * np.median(wsum[covered])), 0.0, 1.0)
    ratio = 1.0 + (ratio - 1.0) * fade[:, None]

    mat = body.juststage.skin_material
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    base = np.array(bsdf.inputs["Base Color"].default_value[:3])
    albedo = np.tile(base, (SIZE, SIZE, 1)).astype(np.float32)
    albedo[mask] = np.clip(base * ratio, 0.0, 1.0)
    # relief: the painted skin's fine detail — its brightness high-passed in texture space, dark is low
    lum = albedo @ np.array(sd.LUMA)
    pad = 13
    high = lum - sd.gaussian_blur(np.pad(lum, pad, mode="reflect"), 4.0)[pad:-pad, pad:-pad]
    high[~mask] = 0.0
    height = np.clip(0.5 + high / (6.0 * high[mask].std()), 0.0, 1.0)
    # shine: the T-zone (the forehead and the nose, near the middle and facing forward) shinier, cavities rougher
    rough = np.full((SIZE, SIZE), ROUGH, dtype=np.float32)
    tzone = np.exp(-((points[:, 0] / 0.03) ** 2)) * np.clip(-normals[:, 1], 0.0, 1.0)
    rough[mask] = ROUGH + (ROUGH_TZONE - ROUGH) * tzone + 0.15 * (0.5 - height[mask])
    print(f"maps built at {time.time() - t0:.0f}s; covered {covered.mean():.0%} of the head's texels")

    color_img = _image("face albedo", _srgb(albedo), "sRGB")
    height_img = _image("face height", height, "Non-Color")
    rough_img = _image("face roughness", rough, "Non-Color")
    for image, socket, x in ((color_img, "Base Color", 300), (rough_img, "Roughness", 0)):
        tex = nodes.new("ShaderNodeTexImage")
        tex.image, tex.location = image, (-650, x)
        links.new(tex.outputs["Color"], bsdf.inputs[socket])
    tex = nodes.new("ShaderNodeTexImage")
    tex.image, tex.location = height_img, (-650, -300)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = BUMP_STRENGTH
    bump.inputs["Distance"].default_value = BUMP_DISTANCE
    links.new(tex.outputs["Color"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    scene = bpy.context.scene
    _gpu(scene)
    _studio_world(scene)
    scene.view_settings.exposure = 0.0
    scene.render.resolution_x = scene.render.resolution_y = 1024
    scene.render.image_settings.file_format = "PNG"
    cam = scene.camera
    for view in ("face", "front", "left40"):
        cam.matrix_world = __import__("mathutils").Matrix(cams[view]["matrix_world"])
        scene.render.filepath = f"{DIR}round2_{view}.png"
        t = time.time()
        bpy.ops.render.render(write_still=True)
        render = _pixels(f"{DIR}round2_{view}.png")[..., :3]
        photo = _pixels(f"{DIR}painted_{view}.png")[..., :3]
        side = np.concatenate([photo, render], axis=1)  # the AI's photo left, our 3D head right
        _image(f"compare {view}", side, "sRGB")
        print(f"rendered {view} in {time.time() - t:.1f}s")
