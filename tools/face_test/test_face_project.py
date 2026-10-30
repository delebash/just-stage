# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, stages 3 (processor) and 4 (card): the aligned paintings projected onto the head's texture, the render
calibrated to the AI's photo, then rendered next to it from the same cameras.

Detail: each view's ratio painting / clay around 1 (freckles, pores, redness) — a two-band blend (Burt & Adelson's
seam blending): the broad colour from every view that sees a texel (facing weight cos⁴), the fine detail mostly from its
best view (cos¹⁶). The detail is a multiplier on the base colour in the shader, so the tone can change without
rebuilding the texture. Relief: the detail's brightness high-passed, as a bump. Shine: the T-zone shinier, cavities
rougher. Light: Poly Haven's CC0 "Studio Small 09" HDRI.

Calibration against the photo (`aligned_face.png`, the painting warped onto the head): the background grey matched,
the exposure from the skin's brightness, the skin tone (melanin and blood of the calibrated skin model) from its colour,
the iris colour sampled at the eyes.

Run: python tools/dev.py test tools/face_test/test_face_project.py -k face_project -s
"""

import importlib
import json
import time
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

up = importlib.import_module("bl_ext.system.juststage.core.uv_projection")
sd = importlib.import_module("bl_ext.system.juststage.core.skin_detail")
DIR = "E:/Dev/3D/just-stage/.dev/facetest/"
HDRI = "E:/Dev/3D/just-stage/.dev/cache/hdri/studio_small_09_2k.hdr"
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below", "face", "faceleft30", "faceright30")
SIZE = 4096
FADE_FROM, FADE_TO = 1.30, 1.40  # the painting fades in up the neck, so no seam where it ends
ROUGH, ROUGH_TZONE = 0.59, 0.42  # the skin material's (√0.35, Donner & Jensen) and a shinier T-zone
BUMP_STRENGTH, BUMP_DISTANCE = 0.3, 0.0004
RATIO_MAX = 2.5  # the detail texture stores ratio / RATIO_MAX in 8 bits
ROUND = 5  # each round's pictures get their own names (an open picture can't be overwritten)
PORES = "E:/Dev/3D/just-stage/.dev/facetest/pores.png"  # a seamless pore tile from juststage.skin.add_detail
#: skin patches in the "face" view (column, row of their centres, 1024² pictures): forehead, both cheeks, chin
PATCHES = ((512, 170), (330, 540), (700, 540), (512, 900))


def _pixels(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(h, w, 4)[::-1]  # rows top first


def _linear(srgb):
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


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


def _blur(img, sigma):
    pad = int(3 * sigma) + 1
    out = np.empty_like(img)
    for c in range(img.shape[2]):
        out[..., c] = sd.gaussian_blur(np.pad(img[..., c], pad, mode="reflect"), sigma)[pad:-pad, pad:-pad]
    return out


def _patch_colour(img, centres=PATCHES, half=18):
    return np.median(np.concatenate([img[r - half : r + half, c - half : c + half].reshape(-1, 3) for c, r in centres]),
                     axis=0)


def _gpu(scene, samples):
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "OPTIX"
    scene.cycles.device = "GPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True


def _studio_world(scene):
    """The HDRI lights the head; camera rays see a plain grey (matched to the photo's later)."""
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
    return grey


def _render(scene, path, size=1024):
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return _pixels(path)[..., :3]


def test_face_project():
    t0 = time.time()
    bpy.ops.wm.open_mainfile(filepath=DIR + "face.blend")
    body = bpy.data.objects["Face"]
    api = importlib.import_module("bl_ext.system.juststage.api")
    character = body.juststage.character_id
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

    # two-band projection: broad colour softly from every view, fine detail sharply from the best one
    cams = json.load(open(DIR + "cameras.json"))
    low_sum, low_w = np.zeros((len(points), 3)), np.zeros(len(points))
    high_sum, high_w = np.zeros((len(points), 3)), np.zeros(len(points))
    for view in VIEWS:
        cam = cams[view]
        mw = np.array(cam["matrix_world"])
        aligned = Path(f"{DIR}aligned_{view}.png")  # the painting warped onto the clay's face (align_paintings.py)
        painted = _linear(_pixels(str(aligned) if aligned.exists() else f"{DIR}painted_{view}.png")[..., :3])
        clay = _linear(_pixels(f"{DIR}clay_{view}.png")[..., :3])
        depth = _pixels(f"{DIR}depth_{view}.exr")[..., 0]
        ratio_img = painted / np.maximum(clay, 0.01)
        # shapes the mesh doesn't have (an Adam's apple, cheekbones) arrive as broad shading the AI painted: divided out,
        # so only colour and detail smaller than ~40 px travel — a painted shadow must not become a dent
        ratio_img /= _blur(ratio_img, 40.0)
        low_img = _blur(ratio_img, 6.0)
        high_img = ratio_img / np.maximum(low_img, 1e-3)
        col, row, dist = up.project(points, mw, cam["lens"], cam["sensor_width"], cam["size"])
        facing = up.view_weights(points, normals, col, row, dist, depth, mw[:3, 3], sharpness=1.0)
        edge = np.minimum.reduce([col, row, cam["size"] - 1 - col, cam["size"] - 1 - row])
        frame = np.clip(np.nan_to_num(edge) / 80.0, 0.0, 1.0) * (0.78 / np.nan_to_num(dist, nan=1e3)) ** 2
        low = up.sample(low_img, col, row)
        seen = facing * frame > 1e-3
        low /= np.median(low[seen], axis=0)  # only the detail travels: each view's ratio around 1
        soft, sharp = facing**4 * frame, facing**16 * frame
        low_sum += soft[:, None] * low
        low_w += soft
        high_sum += sharp[:, None] * up.sample(high_img, col, row)
        high_w += sharp
        print(f"  {view}: sees {seen.mean():.0%} of the head's texels")
    covered = low_w > 1e-6
    ratio = np.ones((len(points), 3))
    ratio[covered] = low_sum[covered] / low_w[covered, None]
    detail_ok = high_w > 1e-9
    ratio[detail_ok] *= high_sum[detail_ok] / high_w[detail_ok, None]
    ratio = np.clip(ratio, 0.3, RATIO_MAX)
    t = np.clip((points[:, 2] - FADE_FROM) / (FADE_TO - FADE_FROM), 0.0, 1.0)
    fade = (t * t * (3 - 2 * t)) * np.clip(low_w / (0.15 * np.median(low_w[covered])), 0.0, 1.0)
    ratio = 1.0 + (ratio - 1.0) * fade[:, None]

    ratio_map = np.ones((SIZE, SIZE, 3), dtype=np.float32)
    ratio_map[mask] = ratio
    lum = ratio_map @ np.array(sd.LUMA)
    pad = 13
    high = lum - sd.gaussian_blur(np.pad(lum, pad, mode="reflect"), 2.0)[pad:-pad, pad:-pad]  # fine relief only
    high[~mask] = 0.0
    height = np.clip(0.5 + high / (6.0 * high[mask].std()), 0.0, 1.0)
    rough = np.full((SIZE, SIZE), ROUGH, dtype=np.float32)
    tzone = np.exp(-((points[:, 0] / 0.03) ** 2)) * np.clip(-normals[:, 1], 0.0, 1.0)
    rough[mask] = ROUGH + (ROUGH_TZONE - ROUGH) * tzone + 0.15 * (0.5 - height[mask])
    print(f"maps built at {time.time() - t0:.0f}s; covered {covered.mean():.0%} of the head's texels")

    # the material: base colour × detail (a multiplier, so the tone can change), roughness, bump
    mat = body.juststage.skin_material
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    detail_tex = nodes.new("ShaderNodeTexImage")
    detail_tex.image = _image("face detail", ratio_map / RATIO_MAX, "Non-Color")
    base_vec = nodes.new("ShaderNodeCombineXYZ")
    multiply = nodes.new("ShaderNodeVectorMath")
    multiply.operation = "MULTIPLY"
    links.new(detail_tex.outputs["Color"], multiply.inputs[0])
    links.new(base_vec.outputs["Vector"], multiply.inputs[1])
    links.new(multiply.outputs["Vector"], bsdf.inputs["Base Color"])
    rough_tex = nodes.new("ShaderNodeTexImage")
    rough_tex.image = _image("face roughness", rough, "Non-Color")
    links.new(rough_tex.outputs["Color"], bsdf.inputs["Roughness"])
    height_tex = nodes.new("ShaderNodeTexImage")
    height_tex.image = _image("face height", height, "Non-Color")
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = BUMP_STRENGTH
    bump.inputs["Distance"].default_value = BUMP_DISTANCE
    links.new(height_tex.outputs["Color"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    def set_tone(melanin, blood):
        api.run("juststage.skin.set_tone", character=character, melanin=melanin, blood=blood)
        rgb = np.array(bsdf.inputs["Base Color"].default_value[:3]) * RATIO_MAX
        base_vec.inputs["X"].default_value, base_vec.inputs["Y"].default_value, base_vec.inputs["Z"].default_value = rgb

    scene = bpy.context.scene
    grey = _studio_world(scene)
    scene.view_settings.exposure = 0.0
    scene.render.image_settings.file_format = "PNG"
    cam = scene.camera
    cam.matrix_world = Matrix(cams["face"]["matrix_world"])
    photo = _pixels(f"{DIR}aligned_face.png")[..., :3]

    # the photo's light: one large soft light whose direction and size give the render the photo's shading (compared
    # low-passed, so shading and not detail decides), the HDRI kept as a dim fill
    _gpu(scene, 16)
    set_tone(0.012, 0.022)
    lit_strength = scene.world.node_tree.nodes["Background"].inputs["Strength"]
    lit_strength.default_value = 0.3
    key = bpy.data.objects.new("key", bpy.data.lights.new("key", "AREA"))
    key.visible_camera = False
    scene.collection.objects.link(key)
    head_c = np.array([0.0, -0.06, 1.615])
    shade_p = _blur(_linear(photo[::4, ::4]), 6.0) @ np.array(sd.LUMA)
    face_rows, face_cols = slice(30, 230), slice(60, 196)  # the face in the 256² quick renders
    best_light = None
    for az in (-45, -25, -10, 0, 10, 25, 45):
        for el in (5, 25, 45):
            for size in (0.6, 1.6):
                a, e = np.radians(az), np.radians(el)
                pos = head_c + 1.4 * np.array([np.sin(a) * np.cos(e), -np.cos(a) * np.cos(e), np.sin(e)])
                key.location = pos
                key.rotation_euler = (__import__("mathutils").Vector(head_c - pos)).to_track_quat("-Z", "Y").to_euler()
                key.data.size, key.data.energy = size, 60.0
                shade_r = _blur(_linear(_render(scene, f"{DIR}calib.png", 256)), 6.0) @ np.array(sd.LUMA)
                a_, b_ = shade_r[face_rows, face_cols], shade_p[face_rows, face_cols]
                err = np.abs(a_ / a_.mean() - b_ / b_.mean()).mean()
                if best_light is None or err < best_light[0]:
                    best_light = (err, az, el, size, pos)
    _, az, el, size, pos = best_light
    key.location = pos
    key.rotation_euler = (__import__("mathutils").Vector(head_c - pos)).to_track_quat("-Z", "Y").to_euler()
    key.data.size = size
    print(f"the photo's light: azimuth {az}°, elevation {el}°, size {size} m (shading error {best_light[0]:.3f})")

    # calibration (quick renders): background grey, then exposure from the skin's brightness, then the tone's colour
    _gpu(scene, 48)
    for _ in range(2):
        quick = _render(scene, f"{DIR}calib.png", 512)
        bg_r, bg_p = _linear(quick[8:40, 8:40]).mean(), _linear(photo[16:80, 16:80]).mean()
        grey.inputs["Color"].default_value = (*([grey.inputs["Color"].default_value[0] * bg_p / bg_r] * 3), 1.0)
    lum = np.array(sd.LUMA)
    for _ in range(2):
        quick = _render(scene, f"{DIR}calib.png", 512)
        skin_r = _patch_colour(_linear(quick), [(c // 2, r // 2) for c, r in PATCHES], 9) @ lum
        skin_p = _patch_colour(_linear(photo)) @ lum
        scene.view_settings.exposure += float(np.log2(skin_p / skin_r))
    target = _patch_colour(_linear(photo))
    best = None
    for melanin in (0.006, 0.009, 0.012, 0.016, 0.022):
        for blood in (0.010, 0.016, 0.024, 0.034):
            set_tone(melanin, blood)
            got = _patch_colour(_linear(_render(scene, f"{DIR}calib.png", 512)), [(c // 2, r // 2) for c, r in PATCHES], 9)
            err = np.abs(np.log(got / got.mean()) - np.log(target / target.mean())).sum()  # colour, not brightness
            if best is None or err < best[0]:
                best = (err, melanin, blood)
    _, melanin, blood = best
    set_tone(melanin, blood)
    print(f"calibrated at {time.time() - t0:.0f}s: background grey {grey.inputs['Color'].default_value[0]:.3f}, "
          f"exposure {scene.view_settings.exposure:+.2f}, melanin {melanin}, blood {blood}")

    # the iris colour, sampled from the photo where the eyes' fronts are seen
    for eye_name in ("Face.eyeLeft", "Face.eyeRight"):
        eye = bpy.data.objects.get(eye_name)
        if eye is None:
            continue
        v = np.array([x.co for x in eye.data.vertices])
        front = v[np.argmin(v[:, 1])]
        c, r, _d = up.project(front[None], np.array(cams["face"]["matrix_world"]), cams["face"]["lens"],
                              cams["face"]["sensor_width"], 1024)
        yy, xx = np.mgrid[-16:17, -16:17]
        ring = (np.hypot(yy, xx) >= 7) & (np.hypot(yy, xx) <= 13)  # the iris around the pupil, inside the white
        patch = _linear(photo[int(r[0]) - 16 : int(r[0]) + 17, int(c[0]) - 16 : int(c[0]) + 17])
        iris = np.median(patch[ring], axis=0)
        print(f"  {eye_name}: iris colour {iris.round(3).tolist()}")
        for slot in eye.material_slots:
            if slot.material and "Iris" in slot.material.name:
                node = next(n for n in slot.material.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
                node.inputs["Base Color"].default_value = (*np.clip(iris * 1.6, 0, 1), 1.0)

    _gpu(scene, 256)
    for view in ("face", "front", "left40"):
        cam.matrix_world = Matrix(cams[view]["matrix_world"])
        t = time.time()
        render = _render(scene, f"{DIR}round{ROUND}_{view}.png")
        photo_v = _pixels(f"{DIR}painted_{view}.png")[..., :3]  # the AI's own photo, as it painted it
        _image(f"compare{ROUND} {view}", np.concatenate([photo_v, render], axis=1), "sRGB")
        print(f"rendered {view} in {time.time() - t:.1f}s")
