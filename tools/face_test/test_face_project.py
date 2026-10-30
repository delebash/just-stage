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
import itertools
import json
import os
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
COAT_WEIGHT, COAT_ROUGHNESS, SHEEN_WEIGHT = 0.12, 0.3, 0.1  # the oil lobe and the fine hair (research rec 5)
BUMP_STRENGTH, BUMP_DISTANCE = 0.15, 0.0004  # pores only: the normal map carries the larger relief
ROUND = 18  # each round's pictures get their own names (an open picture can't be overwritten)
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


def _render_linear(scene, path, size=512):
    """A quick render as scene-linear light (EXR: no view transform, no exposure, no clipping) — what calibration
    compares, so a channel that saturates in an 8-bit picture can't steer it."""
    fmt = scene.render.image_settings.file_format
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    scene.render.image_settings.file_format = fmt
    scene.render.image_settings.color_depth = "8"  # back to 8-bit PNG (16-bit PNGs load as linear)
    return _pixels(path)[..., :3]


def _lower_lids(body, degrees=9.0):
    """The upper lids lowered a little, as a shape key: our head's neutral eyes show the whole iris (a stare); a relaxed
    eye — and the AI's painting — has the upper lid over the iris' top. Lid skin over each eyeball turns down about the
    eyeball's horizontal axis (as a lid closes, so it can't pass through the eye): most at the lid's edge, none 35° above."""
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    co = build.shaped_coords(body).astype(np.float64)
    key = body.shape_key_add(name="lids lowered", from_mix=False)
    moved = 0
    for name in ("Face.eyeLeft", "Face.eyeRight"):
        eye = bpy.data.objects[name]
        ev = np.array([v.co for v in eye.data.vertices]) @ np.array(eye.matrix_world)[:3, :3].T + np.array(eye.matrix_world)[:3, 3]
        centre = (ev.min(axis=0) + ev.max(axis=0)) / 2
        radius = float((ev.max(axis=0) - ev.min(axis=0))[[0, 2]].mean() / 2)
        rel = co - centre
        dist = np.linalg.norm(rel, axis=1)
        az = np.degrees(np.arctan2(rel[:, 0], -rel[:, 1]))
        el = np.degrees(np.arctan2(rel[:, 2], np.hypot(rel[:, 0], rel[:, 1])))
        near = (dist > radius * 0.9) & (dist < radius + 0.012) & (rel[:, 1] < 0) & (np.abs(az) < 45)
        lid = near & (el > 0) & (dist < radius + 0.004)
        margin = float(np.min(el[lid])) if lid.any() else 15.0
        weight = np.clip(1.0 - (el - margin) / 35.0, 0.0, 1.0) * (el >= margin - 2.0) * near
        weight *= np.clip(1.0 - (np.abs(az) - 30.0) / 15.0, 0.0, 1.0)  # fading toward the corners
        ang = np.radians(degrees) * weight  # down on the front (-y) side: about the eye's left-right axis (world x)
        y, z = rel[:, 1], rel[:, 2]
        new_y = y * np.cos(ang) - z * np.sin(ang)
        new_z = y * np.sin(ang) + z * np.cos(ang)
        for i in np.flatnonzero(weight > 0):
            key.data[i].co.y += float(new_y[i] - y[i])
            key.data[i].co.z += float(new_z[i] - z[i])
        moved += int((weight > 0).sum())
        print(f"  {name}: lid edge at {margin:.1f}° above the eye's centre")
    key.value = 1.0
    print(f"lids lowered: {moved} vertices, {degrees}° at the edge")


def _close_mouth(body):
    """The lips closed as a shape key: our head's neutral mouth is a slit ~0.9 mm tall at its middle (measured by rays
    from the face camera; teeth behind it), the AI paints it closed. Upper lip down, lower lip up, most at the slit,
    fading out by ~4 mm and toward the corners (±24 mm)."""
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    co = build.shaped_coords(body).astype(np.float64)
    x, y, z = co[:, 0], co[:, 1], co[:, 2]
    z_mid = 1.5484  # where the lips meet, middle and corners (measured)
    half = np.clip(1.0 - (x / 0.024) ** 2, 0.0, 1.0)
    gap = 0.0016 * half
    near = (np.abs(x) < 0.027) & (y < -0.138) & (np.abs(z - z_mid) < 0.012)
    shift = (gap / 2 + 0.0003 * half) * np.exp(-(((z - z_mid) / 0.005) ** 2)) * near
    key = body.shape_key_add(name="mouth closed", from_mix=False)  # the basis plus this offset only
    dz = np.where(z > z_mid, -shift, shift)
    for i in np.flatnonzero(near):
        key.data[i].co.z += dz[i]
    key.value = 1.0
    print(f"mouth closed: {near.sum()} vertices, at most {shift.max() * 1000:.2f} mm")


def test_face_project():
    t0 = time.time()
    bpy.ops.wm.open_mainfile(filepath=DIR + "face.blend")
    body = bpy.data.objects["Face"]
    _close_mouth(body)
    _lower_lids(body)
    api = importlib.import_module("bl_ext.system.juststage.api")
    character = body.juststage.character_id
    # brows and lashes as strands (the hair module's MakeHuman CC0 grooms), dark brown: Principled Hair melanin
    for style, melanin, redness in (('basic_lashes_upper', 0.9, 0.2),):
        api.run('juststage.hair.add', character=character, style=style, melanin=melanin, redness=redness)
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

    # each view's albedo and relief (delight_views.py), two-band (Burt & Adelson): the broad part from every view that
    # sees a texel (cos⁴), the fine part from its best view (cos¹⁶); each view's brightness levelled to the others where
    # they overlap (a global gain per view — the simplest form of Waechter et al.'s seam levelling), the front the anchor
    cams = json.load(open(DIR + "cameras.json"))

    def view_samples(view, idx):
        cam = cams[view]
        mw = np.array(cam["matrix_world"])
        depth = _pixels(f"{DIR}depth_{view}.exr")[..., 0]
        col, row, dist = up.project(points[idx], mw, cam["lens"], cam["sensor_width"], cam["size"])
        facing = up.view_weights(points[idx], normals[idx], col, row, dist, depth, mw[:3, 3], sharpness=1.0)
        edge = np.minimum.reduce([col, row, cam["size"] - 1 - col, cam["size"] - 1 - row])
        frame = np.clip(np.nan_to_num(edge) / 80.0, 0.0, 1.0) * (0.78 / np.nan_to_num(dist, nan=1e3)) ** 2
        return facing * frame, col, row

    lum = np.array(sd.LUMA)
    sub = np.arange(0, len(points), 16)
    looks = {}
    for view in VIEWS:
        w, col, row = view_samples(view, sub)
        looks[view] = (w, up.sample(_blur(np.load(f"{DIR}albedo_{view}.npy").astype(np.float32), 6.0), col, row) @ lum)
    gains = dict.fromkeys(VIEWS, 1.0)
    for _ in range(4):
        num = sum(w * gains[v] * l for v, (w, l) in looks.items())
        den = sum(w for w, _l in looks.values())
        mean = num / np.maximum(den, 1e-9)
        for v, (w, l) in looks.items():
            sel = (w > 0.05) & (l > 1e-4) & (den > 1e-6)
            gains[v] = float(np.median(mean[sel] / l[sel])) if sel.sum() > 100 else gains[v]
        anchor = gains["front"]
        gains = {v: g / anchor for v, g in gains.items()}
    print("  view gains: " + ", ".join(f"{v} {g:.2f}" for v, g in gains.items()))

    every = np.arange(len(points))
    low_sum, low_w = np.zeros((len(points), 3)), np.zeros(len(points))
    high_best, high_w = np.ones((len(points), 3)), np.zeros(len(points))
    nlow_sum, nhigh_best = np.zeros((len(points), 3)), np.zeros((len(points), 3))
    for view in VIEWS:
        w, col, row = view_samples(view, every)
        albedo = np.load(f"{DIR}albedo_{view}.npy").astype(np.float32) * gains[view]
        nworld = np.load(f"{DIR}nworld_{view}.npy").astype(np.float32)
        low_img, nlow_img = _blur(albedo, 6.0), _blur(nworld, 6.0)
        low, nlow = up.sample(low_img, col, row), up.sample(nlow_img, col, row)
        soft, sharp = w**4, w**16
        low_sum += soft[:, None] * low
        nlow_sum += soft[:, None] * nlow
        low_w += soft
        better = sharp > high_w  # the fine band from the single best view: no blur from views that disagree by pixels
        high_best[better] = (up.sample(albedo, col, row) / np.maximum(low, 1e-4))[better]
        nhigh_best[better] = (up.sample(nworld, col, row) - nlow)[better]
        high_w[better] = sharp[better]
        print(f"  {view}: sees {(w > 1e-3).mean():.0%} of the head's texels")
    covered = low_w > 1e-6
    albedo = np.zeros((len(points), 3))
    albedo[covered] = low_sum[covered] / low_w[covered, None]
    nrm = normals.copy()
    nrm[covered] = nlow_sum[covered] / low_w[covered, None]
    detail_ok = high_w > 1e-9
    albedo[detail_ok] *= np.clip(high_best[detail_ok], 0.3, 3.0)
    nrm[detail_ok] += nhigh_best[detail_ok]
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    t = np.clip((points[:, 2] - FADE_FROM) / (FADE_TO - FADE_FROM), 0.0, 1.0)
    fade = (t * t * (3 - 2 * t)) * np.clip(low_w / (0.15 * np.median(low_w[covered])), 0.0, 1.0)
    face_zone = covered & (points[:, 2] > 1.5) & (fade > 0.9)
    fallback = np.median(albedo[face_zone], axis=0)
    albedo = fallback + (albedo - fallback) * fade[:, None]
    nrm = normals + (nrm - normals) * fade[:, None]
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    print(f"maps built at {time.time() - t0:.0f}s; covered {covered.mean():.0%} of the head's texels")

    mat = body.juststage.skin_material
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    api.run("juststage.skin.set_tone", character=character, melanin=0.012, blood=0.022)
    target = float(np.array(bsdf.inputs["Base Color"].default_value[:3]) @ lum)
    scale = target / float(np.median(albedo[face_zone] @ lum))  # the skin model's brightness, the AI's colour
    albedo *= scale
    print(f"albedo scaled to the skin model's luminance {target:.3f}")

    albedo_map = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    albedo_map[...] = fallback * scale
    albedo_map[mask] = albedo
    srgb = np.clip(albedo_map, 0.0, 1.0)
    srgb = np.where(srgb <= 0.0031308, srgb * 12.92, 1.055 * srgb ** (1 / 2.4) - 0.055)
    albedo_tex = nodes.new("ShaderNodeTexImage")
    albedo_tex.image = _image("face albedo", srgb, "sRGB")
    gain = nodes.new("ShaderNodeVectorMath")
    gain.operation = "MULTIPLY"
    gain.inputs[1].default_value = (1.0, 1.0, 1.0)
    links.new(albedo_tex.outputs["Color"], gain.inputs[0])
    links.new(gain.outputs["Vector"], bsdf.inputs["Base Color"])

    rot_inv = np.array(body.matrix_world.to_3x3().inverted())
    nrm_map = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    nrm_map[..., 2] = 1.0
    nrm_map[mask] = nrm @ rot_inv.T
    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = _image("face normal", nrm_map * 0.5 + 0.5, "Non-Color")
    normal_tex.interpolation = "Cubic"
    nmap = nodes.new("ShaderNodeNormalMap")
    nmap.space = "OBJECT"
    links.new(normal_tex.outputs["Color"], nmap.inputs["Color"])

    lum_map = albedo_map @ lum
    pad = 13
    high = np.log(np.maximum(lum_map, 1e-4))
    high = high - sd.gaussian_blur(np.pad(high, pad, mode="reflect"), 2.0)[pad:-pad, pad:-pad]  # pores, fine lines
    high[~mask] = 0.0
    height = np.clip(0.5 + high / (6.0 * high[mask].std()), 0.0, 1.0)
    rough = np.full((SIZE, SIZE), ROUGH, dtype=np.float32)
    tzone = np.exp(-((points[:, 0] / 0.03) ** 2)) * np.clip(-normals[:, 1], 0.0, 1.0)
    rough[mask] = ROUGH + (ROUGH_TZONE - ROUGH) * tzone + 0.15 * (0.5 - height[mask])
    cavity = np.clip(1.0 - 2.5 * np.maximum(0.0, 0.5 - height), 0.2, 1.0)
    rough += 0.2 * (1.0 - cavity)
    cavity_tex = nodes.new("ShaderNodeTexImage")
    cavity_tex.image = _image("face cavity", cavity, "Non-Color")
    spec = nodes.new("ShaderNodeMath")
    spec.operation = "MULTIPLY"
    spec.inputs[1].default_value = 0.5
    links.new(cavity_tex.outputs["Color"], spec.inputs[0])
    links.new(spec.outputs["Value"], bsdf.inputs["Specular IOR Level"])
    bsdf.inputs["Coat Weight"].default_value = COAT_WEIGHT
    bsdf.inputs["Coat Roughness"].default_value = COAT_ROUGHNESS
    bsdf.inputs["Coat IOR"].default_value = 1.45
    bsdf.inputs["Sheen Weight"].default_value = SHEEN_WEIGHT
    bsdf.inputs["Sheen Roughness"].default_value = 0.4
    rough_tex = nodes.new("ShaderNodeTexImage")
    rough_tex.image = _image("face roughness", rough, "Non-Color")
    links.new(rough_tex.outputs["Color"], bsdf.inputs["Roughness"])
    height_tex = nodes.new("ShaderNodeTexImage")
    height_tex.image = _image("face height", height, "Non-Color")
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = BUMP_STRENGTH
    bump.inputs["Distance"].default_value = BUMP_DISTANCE
    links.new(height_tex.outputs["Color"], bump.inputs["Height"])
    links.new(nmap.outputs["Normal"], bump.inputs["Normal"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    def set_tone(melanin, blood):  # the light fit's quick renders: the skin model's scattering; the colour is the map's
        api.run("juststage.skin.set_tone", character=character, melanin=melanin, blood=blood)
        links.new(gain.outputs["Vector"], bsdf.inputs["Base Color"])

    scene = bpy.context.scene
    grey = _studio_world(scene)
    scene.view_settings.exposure = 0.0
    scene.view_settings.view_transform = "Standard"  # the photo's plain sRGB
    scene.view_settings.look = "None"
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
    for fill, az, el, size in itertools.product((0.3, 1.0, 3.0), (-45, -25, -10, 0, 10, 25, 45), (5, 25, 45), (1.6, 3.0)):
                lit_strength.default_value = fill  # the studio's fill: the photo is lit evenly from every side
                a, e = np.radians(az), np.radians(el)
                pos = head_c + 1.4 * np.array([np.sin(a) * np.cos(e), -np.cos(a) * np.cos(e), np.sin(e)])
                key.location = pos
                key.rotation_euler = (__import__("mathutils").Vector(head_c - pos)).to_track_quat("-Z", "Y").to_euler()
                key.data.size, key.data.energy = size, 60.0
                shade_r = _blur(_render_linear(scene, f"{DIR}calib.exr", 256), 6.0) @ np.array(sd.LUMA)
                a_, b_ = shade_r[face_rows, face_cols], shade_p[face_rows, face_cols]
                err = np.abs(a_ / a_.mean() - b_ / b_.mean()).mean()
                if best_light is None or err < best_light[0]:
                    best_light = (err, az, el, size, pos, fill)
    _, az, el, size, pos, fill = best_light
    lit_strength.default_value = fill
    key.location = pos
    key.rotation_euler = (__import__("mathutils").Vector(head_c - pos)).to_track_quat("-Z", "Y").to_euler()
    key.data.size = size
    print(f"the photo's light: azimuth {az}°, elevation {el}°, size {size} m, fill {fill} (shading error {best_light[0]:.3f})")

    # calibration (quick renders): exposure from the skin's brightness, the skin's colour (light scattered through skin
    # comes out redder than its albedo; a per-channel gain on the albedo brings it to the photo's), then the background
    _gpu(scene, 48)
    lum = np.array(sd.LUMA)
    target_rgb = _patch_colour(_linear(photo))
    halves = [(c // 2, r // 2) for c, r in PATCHES]
    for _ in range(3):
        got = _patch_colour(_render_linear(scene, f"{DIR}calib.exr"), halves, 9)  # before exposure
        hue = (target_rgb / (target_rgb @ lum)) / (got / (got @ lum))
        g = np.array(gain.inputs[1].default_value) * hue
        gain.inputs[1].default_value = tuple(g / (g @ lum))
    got = _patch_colour(_render_linear(scene, f"{DIR}calib.exr"), halves, 9)
    scene.view_settings.exposure = float(np.log2((target_rgb @ lum) / (got @ lum)))
    bg_lin = _render_linear(scene, f"{DIR}calib.exr")[8:40, 8:40].mean() * 2.0 ** scene.view_settings.exposure
    bg_p = _linear(photo[16:80, 16:80]).mean()
    grey.inputs["Color"].default_value = (*([grey.inputs["Color"].default_value[0] * bg_p / bg_lin] * 3), 1.0)
    print(f"colour gain {np.round(gain.inputs[1].default_value, 3).tolist()}; photo skin {np.round(target_rgb, 3).tolist()}, render skin (linear, before exposure) {np.round(got, 3).tolist()}")
    melanin, blood = 0.012, 0.022
    print(f"calibrated at {time.time() - t0:.0f}s: background grey {grey.inputs['Color'].default_value[0]:.3f}, "
          f"exposure {scene.view_settings.exposure:+.2f}, melanin {melanin}, blood {blood}")

    # the eyes: iris, pupil and white painted from the views that see them, projected onto each eyeball's own UVs (the
    # cornea, a clear shell in front, stays clear); the painting's catch-lights clipped so the cornea's own shine isn't
    # doubled; the white's brightness set to a sclera's (~0.55)
    eye_views = ("face", "faceleft30", "faceright30", "front", "left40", "right40")
    eye_paintings = {}
    for view in eye_views:
        aligned = Path(f"{DIR}aligned_{view}.png")
        eye_paintings[view] = (_linear(_pixels(str(aligned) if aligned.exists() else f"{DIR}painted_{view}.png")[..., :3]),
                               _pixels(f"{DIR}depth_{view}.exr")[..., 0])
    for eye_name in ("Face.eyeLeft", "Face.eyeRight"):
        eye = bpy.data.objects.get(eye_name)
        if eye is None:
            continue
        me = eye.data
        me.calc_loop_triangles()
        ntri = len(me.loop_triangles)
        e_loops, e_verts = np.empty(ntri * 3, np.int64), np.empty(ntri * 3, np.int64)
        e_mat = np.empty(ntri, np.int64)
        me.loop_triangles.foreach_get("loops", e_loops)
        me.loop_triangles.foreach_get("vertices", e_verts)
        me.loop_triangles.foreach_get("material_index", e_mat)
        e_loops, e_verts = e_loops.reshape(-1, 3), e_verts.reshape(-1, 3)
        mw_eye = np.array(eye.matrix_world)
        e_co = np.array([v.co for v in me.vertices]) @ mw_eye[:3, :3].T + mw_eye[:3, 3]
        e_vn = np.array([v.normal for v in me.vertices]) @ mw_eye[:3, :3].T
        e_uv = np.empty(len(me.loops) * 2, np.float32)
        me.uv_layers[0].data.foreach_get("uv", e_uv)
        e_uv = e_uv.reshape(-1, 2)
        names = [slot.material.name if slot.material else "" for slot in eye.material_slots]
        painted_parts = np.array(["Cornea" not in names[m] for m in e_mat])
        e_mid = np.repeat(e_mat[painted_parts][:, None, None], 3, axis=1).astype(np.float32)
        (e_pos, e_nrm, e_id), e_mask = up.raster_uv(
            e_uv[e_loops[painted_parts]], [e_co[e_verts[painted_parts]], e_vn[e_verts[painted_parts]], e_mid], 1024)
        e_pts = e_pos[e_mask].astype(np.float64)
        e_n = e_nrm[e_mask].astype(np.float64)
        e_n /= np.linalg.norm(e_n, axis=1, keepdims=True) + 1e-12
        acc, wsum = np.zeros((len(e_pts), 3)), np.zeros(len(e_pts))
        for view in eye_views:
            cam_v = cams[view]
            mw = np.array(cam_v["matrix_world"])
            painting, depth = eye_paintings[view]
            col, row, dist = up.project(e_pts, mw, cam_v["lens"], cam_v["sensor_width"], cam_v["size"])
            w = up.view_weights(e_pts, e_n, col, row, dist, depth, mw[:3, 3], sharpness=8.0, tolerance=0.006)
            w = w * (0.78 / np.nan_to_num(dist, nan=1e3)) ** 2
            acc += w[:, None] * up.sample(painting, col, row)
            wsum += w
        seen = wsum > 1e-6
        colour = np.zeros((len(e_pts), 3))
        colour[seen] = acc[seen] / wsum[seen, None]
        lum_e = colour @ lum
        sat = (colour.max(axis=1) - colour.min(axis=1)) / np.maximum(colour.max(axis=1), 1e-6)
        texel_ids = np.round(e_id[e_mask][:, 0]).astype(int)
        sclera_ids = [i for i, n in enumerate(names) if "Sclera" in n]
        white = seen & np.isin(texel_ids, sclera_ids) & (sat < 0.35) & (lum_e > np.percentile(lum_e[seen], 50))
        colour *= 0.38 / max(float(np.median(lum_e[white])), 1e-6)
        iris_ids = [i for i, n in enumerate(names) if "Iris" in n or "Pupil" in n]
        disk_v = np.isin(np.repeat(e_mat, 3), iris_ids)
        disk_pts = e_co[e_verts.ravel()[disk_v]]
        centre = disk_pts.mean(axis=0)
        normal = np.linalg.svd(disk_pts - centre)[2][2]
        normal *= -np.sign(normal[1]) or 1.0  # facing forward (-y)
        ex = np.array([1.0, 0.0, 0.0]) - normal[0] * normal
        ex /= np.linalg.norm(ex)
        ez = np.cross(normal, ex) * -1.0
        ez *= np.sign(ez[2]) or 1.0
        radius3d = np.max(np.linalg.norm((disk_pts - centre) - np.outer((disk_pts - centre) @ normal, normal), axis=1))
        on_disk = np.isin(np.round(e_id[e_mask][:, 0]).astype(int), iris_ids)
        on_disk_all = on_disk
        rel = e_pts[on_disk] - centre
        u, v = rel @ ex, rel @ ez
        rr, th = np.hypot(u, v) / radius3d, np.arctan2(v, u)
        band = np.arctan2(np.sin(th), np.abs(np.cos(th))) / 3.0  # every angle into a ±30° band, mirrored
        face_paint = _linear(_pixels(f"{DIR}painted_face.png")[..., :3])
        sides = []
        for side in (1.0, -1.0):  # the band on the iris' right, then its left, in the painting
            t_side = band if side > 0 else np.pi - band
            sides.append(t_side)
        marks = json.load(open(DIR + "landmarks.json"))["face"]["painted"]
        c_i, ring = (468, range(469, 473)) if "Right" in eye_name else (473, range(474, 478))
        cx, cy = marks[c_i]
        r_img = float(np.mean([np.hypot(marks[i][0] - cx, marks[i][1] - cy) for i in ring]))
        darkness = [float(np.median(up.sample(face_paint, cx + rr * r_img * np.cos(t), cy - rr * r_img * np.sin(t)) @ lum))
                    for t in sides]
        th = sides[int(np.argmin(darkness))]
        r_in = 0.88 * r_img  # MediaPipe's iris edge sits a little outside the iris; beyond it is the white
        limbal = 1.0 - 0.55 * np.clip((rr - 0.82) / 0.18, 0.0, 1.0) ** 1.5  # the dark ring at every iris' edge
        colour[on_disk] = limbal[:, None] * up.sample(face_paint, cx + rr * r_in * np.cos(th), cy - rr * r_in * np.sin(th)) * (
            0.38 / max(float(np.median((acc[seen] / wsum[seen, None])[white[seen]] @ lum)), 1e-6))
        lum_e = colour @ lum
        cap = 1.15 * float(np.percentile(lum_e[seen], 90))
        colour[seen & (lum_e > cap)] *= (cap / lum_e[seen & (lum_e > cap)])[:, None]  # catch-lights out
        skin_on_white = np.isin(texel_ids, sclera_ids) & ~on_disk_all & (~seen | (sat >= 0.35))
        colour[skin_on_white] = np.median(colour[white], axis=0)
        colour[~seen] = np.median(colour[white], axis=0)
        e_map = np.zeros((1024, 1024, 3), np.float32)
        e_map[...] = np.median(colour[white], axis=0)
        e_map[e_mask] = colour
        seen_map = np.zeros((1024, 1024), np.float32)
        seen_map[e_mask] = (wsum > 0.05 * np.median(wsum[seen])).astype(np.float32)
        seen_map[e_mask] = np.where(on_disk_all, 1.0, seen_map[e_mask])  # the iris counts as open (under the cornea)
        pad = 40
        edge = sd.gaussian_blur(np.pad(seen_map, pad, mode="edge"), 12.0)[pad:-pad, pad:-pad]
        contact = 0.45 + 0.55 * np.clip((edge - 0.35) / 0.5, 0.0, 1.0)
        e_map *= contact[..., None]
        e_srgb = np.clip(e_map, 0.0, 1.0)
        e_srgb = np.where(e_srgb <= 0.0031308, e_srgb * 12.92, 1.055 * e_srgb ** (1 / 2.4) - 0.055)
        e_img = _image(f"{eye_name} paint", e_srgb, "sRGB")
        for slot in eye.material_slots:
            if slot.material and "Cornea" in slot.material.name:
                # the cornea clear (as a shell it greyed the eye — measured 2026-10-30); the wet shine is on the iris
                # and the white below
                c_nt = slot.material.node_tree
                c_out = next(n for n in c_nt.nodes if n.type == "OUTPUT_MATERIAL")
                c_clear = c_nt.nodes.new("ShaderNodeBsdfTransparent")
                c_nt.links.new(c_clear.outputs["BSDF"], c_out.inputs["Surface"])
        for slot in eye.material_slots:
            if slot.material and "Cornea" not in slot.material.name:
                e_nodes = slot.material.node_tree.nodes
                e_tex = e_nodes.new("ShaderNodeTexImage")
                e_tex.image = e_img
                e_bsdf = next(n for n in e_nodes if n.type == "BSDF_PRINCIPLED")
                e_gain = e_nodes.new("ShaderNodeVectorMath")
                e_gain.operation = "MULTIPLY"
                e_gain.inputs[1].default_value = gain.inputs[1].default_value  # the skin's calibrated colour gain
                slot.material.node_tree.links.new(e_tex.outputs["Color"], e_gain.inputs[0])
                slot.material.node_tree.links.new(e_gain.outputs["Vector"], e_bsdf.inputs["Base Color"])
                e_bsdf.inputs["Roughness"].default_value = 0.4 if "Iris" in slot.material.name else 0.25
                e_bsdf.inputs["Coat Weight"].default_value = 0.3 if "Iris" in slot.material.name else 0.0
                e_bsdf.inputs["Coat Roughness"].default_value = 0.03
        print(f"  {eye_name}: {seen.mean():.0%} of its painted texels seen; white {np.median(colour[white], axis=0).round(3).tolist()}")

    bpy.ops.wm.save_as_mainfile(filepath=f"{DIR}round.blend", copy=True)  # the finished scene, for quick trials
    _gpu(scene, 256)
    for view in ("face", "front", "left40"):
        cam.matrix_world = Matrix(cams[view]["matrix_world"])
        t = time.time()
        render = _render(scene, f"{DIR}round{ROUND}_{view}.png")
        photo_v = _pixels(f"{DIR}painted_{view}.png")[..., :3]  # the AI's own photo, as it painted it
        _image(f"compare{ROUND} {view}", np.concatenate([photo_v, render], axis=1), "sRGB")
        print(f"rendered {view} in {time.time() - t:.1f}s")
