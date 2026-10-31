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

import collections
import functools
import importlib
import importlib.util
import itertools
import json
import os
import time
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

up = importlib.import_module("bl_ext.system.juststage.core.uv_projection")
_spec = importlib.util.spec_from_file_location("mpfb_nodes", str(Path(__file__).with_name("mpfb_nodes.py")))
mpfb_nodes = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mpfb_nodes)
_spec = importlib.util.spec_from_file_location("face_shape", str(Path(__file__).with_name("face_shape.py")))
face_shape = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(face_shape)
_spec = importlib.util.spec_from_file_location("relief_geometry", str(Path(__file__).with_name("relief_geometry.py")))
relief_geometry = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(relief_geometry)
MPFB_EYES = "E:/Dev/3D/just-stage/.dev/cache/mpfb2_nodes/procedural_eyes.json"  # mpfb2 6ff1eb35 data/node_trees
sd = importlib.import_module("bl_ext.system.juststage.core.skin_detail")
DIR = "E:/Dev/3D/just-stage/.dev/facetest/"
HDRI = "E:/Dev/3D/just-stage/.dev/cache/hdri/studio_small_09_2k.hdr"
VIEWS = ("front", "left40", "right40", "left90", "right90", "above", "below", "face", "faceleft30", "faceright30")
SIZE = 4096
FADE_FROM, FADE_TO = 1.30, 1.40  # the painting fades in up the neck, so no seam where it ends
ROUGH, ROUGH_TZONE = 0.59, 0.42  # the skin material's (√0.35, Donner & Jensen) and a shinier T-zone
PORE_TILES = 20.0  # tiles per UV unit: the face is 1.13 m a UV unit (measured, median of 17,331 triangles), the tile ~5.6 cm
COAT_WEIGHT, COAT_ROUGHNESS, SHEEN_WEIGHT = 0.12, 0.3, 0.1  # the oil lobe and the fine hair (research rec 5)
BUMP_STRENGTH, BUMP_DISTANCE = 0.15, 0.0004  # pores only: the normal map carries the larger relief
ROUND = int(os.environ.get("FACETEST_ROUND", 49))  # each round's pictures get their own names (an open picture can't be overwritten)
FLOW = os.environ.get("FACETEST_FLOW", "0") == "1"  # flow_views.py's nudged paintings (the approved alignment rec)
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


def _view_map(kind, view):
    """A view's light-free colours (kind "albedo") or world normals ("nworld"): flow_views.py's nudged ones with
    FACETEST_FLOW=1 - which must be newer than the light removal they came from."""
    plain = Path(f"{DIR}{kind}_{view}.npy")
    if not FLOW:
        return np.load(plain).astype(np.float32)
    flowed = Path(f"{DIR}flowed_{kind}_{view}.npy")
    assert flowed.exists() and flowed.stat().st_mtime >= plain.stat().st_mtime, f"run flow_views.py first ({flowed.name})"
    return np.load(flowed).astype(np.float32)


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


ICT_MESH = "E:/Dev/3D/just-stage/.dev/cache/ict/generic_neutral_mesh.obj"  # USC-ICT/ICT-FaceKit FaceXModel, MIT
#: its README's index table (left side): the face's vertices, the left eyeball's vertices, the polygons of the left eye
#: occlusion and of the left lacrimal fluid
ICT_SKIN, ICT_EYE, ICT_OCCLUSION, ICT_TEAR = (0, 9409), (21451, 23021), (25048, 25176), (24692, 24855)
ICT_SKIN_POLYGONS = 9230  # its face's polygons
#: the occlusion's darkening per side, CC5's documented model (Eye Occlusion Shadow 1: a range and strength for the top,
#: bottom, inner and outer, each with an edge fade): (range in UV, strength) - starting values, to be calibrated on the
#: white's brightness profile against the painting
# measured before the shell (round 48, face view, linear, the white beside the iris): just under the upper lashes ours
# 0.125 vs the painting's 0.191 (already darker - the lashes), mid-white 0.283 vs 0.252, low 0.194 vs 0.185 - so a light top
OCCLUSION = {"top": (0.30, 0.15), "bottom": (0.20, 0.15), "inner": (0.20, 0.30), "outer": (0.15, 0.15)}
OCCLUSION_COLOUR = (0.33, 0.09, 0.05)  # CC5's Shadow 2 example #54170E, a dark red-brown
TEAR_ROUGHNESS = 0.3  # CC5's Tear Line examples: 0.25 and 0.45
TEAR_FADE = 0.25  # the film fades in over this share of the strip from its edge on the eyeball (CC5's Edge Fadeout)


@functools.cache
def _ict():
    """ICT-FaceKit's neutral mesh: positions in Blender's axes (ICT's are y up, z forward, in centimetres - its eye
    centres are 6.19 apart), UVs, and faces as (vertex, uv) pairs."""
    v, vt, faces = [], [], []
    with open(ICT_MESH, encoding="utf-8") as f:
        for line in f:
            if line.startswith("v "):
                v.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("vt "):
                vt.append([float(x) for x in line.split()[1:3]])
            elif line.startswith("f "):
                faces.append([tuple(int(t) - 1 for t in c.split("/")[:2]) for c in line.split()[1:]])
    v = np.array(v)
    return np.c_[v[:, 0], -v[:, 2], v[:, 1]], np.array(vt), faces


def _ict_part(first, end):
    """One of ICT's pieces by its polygon range: faces in its own vertex numbers, positions, per-vertex UVs."""
    v, vt, faces = _ict()
    part = faces[first:end]
    order = sorted({c[0] for f in part for c in f})
    local = {g: k for k, g in enumerate(order)}
    uv = np.zeros((len(order), 2))
    for f in part:
        for g, t in f:
            uv[local[g]] = vt[t]
    return [[local[c[0]] for c in f] for f in part], v[order], uv


def _occlusion_shell(o, name):
    """Rec 6's eye occlusion (docs/plans/2026-10-31-audit-eyes.md section 6): ICT's sheet, its topology and UVs kept,
    placed over our own eyeball across our lid opening - u from the outer corner to the inner, v from the lower lid's
    edge to the upper's, 3-4 degrees under each lid, 0.4 mm off the eyeball (ICT's sits a median 0.5 mm off). Shaded as
    CC5 documents: per-side ranges, a soft edge, a tinted transparent film that only darkens what is behind it and
    casts nothing (Cycles traces the lids' own shadow)."""
    faces, _, uv = _ict_part(*ICT_OCCLUSION)
    widen = 4.0 * np.sign(o.inner - o.outer)
    a_outer, a_inner = o.outer - widen, o.inner + widen
    a = a_outer + uv[:, 0] * (a_inner - a_outer)
    lo_e = np.interp(a, o.centres, o.lower) - 3.0
    up_e = np.interp(a, o.centres, o.upper) + 3.0
    e = lo_e + uv[:, 1] * (up_e - lo_e)
    points = o.centre + (o.radius + 0.0004) * face_shape.direction(a, e)
    mesh = bpy.data.meshes.new(f"{name} occlusion")
    mesh.from_pydata(points.tolist(), [], faces)
    layer = mesh.uv_layers.new(name="UVMap")
    layer.data.foreach_set("uv", np.array([uv[mesh.loops[k].vertex_index] for k in range(len(mesh.loops))]).ravel())
    obj = bpy.data.objects.new(f"{name} occlusion", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.visible_shadow = obj.visible_diffuse = obj.visible_volume_scatter = False
    mat = bpy.data.materials.new(f"{name} occlusion")
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    film = nt.nodes.new("ShaderNodeBsdfTransparent")
    coords = nt.nodes.new("ShaderNodeUVMap")
    split = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coords.outputs["UV"], split.inputs["Vector"])
    darkness = None
    for side, (span, strength) in OCCLUSION.items():
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.interpolation_type = "SMOOTHSTEP"
        axis = split.outputs["Y" if side in ("top", "bottom") else "X"]
        near_one = side in ("top", "inner")  # u runs outer (0) to inner (1); v lower (0) to upper (1)
        ramp.inputs["From Min"].default_value = 1.0 - span if near_one else span
        ramp.inputs["From Max"].default_value = 1.0 if near_one else 0.0
        ramp.inputs["To Max"].default_value = strength
        nt.links.new(axis, ramp.inputs["Value"])
        if darkness is None:
            darkness = ramp.outputs["Result"]
        else:
            both = nt.nodes.new("ShaderNodeMath")
            both.operation = "MAXIMUM"
            nt.links.new(darkness, both.inputs[0])
            nt.links.new(ramp.outputs["Result"], both.inputs[1])
            darkness = both.outputs["Value"]
    tint = nt.nodes.new("ShaderNodeMix")
    tint.data_type = "RGBA"
    nt.links.new(darkness, tint.inputs["Factor"])
    next(i for i in tint.inputs if i.identifier == "A_Color").default_value = (1.0, 1.0, 1.0, 1.0)
    next(i for i in tint.inputs if i.identifier == "B_Color").default_value = (*OCCLUSION_COLOUR, 1.0)
    nt.links.new(next(o for o in tint.outputs if o.identifier == "Result_Color"), film.inputs["Color"])
    nt.links.new(film.outputs["BSDF"], out.inputs["Surface"])
    mesh.materials.append(mat)
    print(f"  {name} occlusion: {len(points)} vertices over an opening of {abs(a_inner - a_outer):.0f} deg, "
          f"lids {o.lower.max():.1f} .. {o.upper.min():.1f} deg")
    return obj


def _tearline(o, skin, name):
    """Rec 6's tearline (docs/plans/2026-10-31-audit-eyes.md section 6, item 3): ICT's lacrimal-fluid strip, a ring from
    the eyeball at the lid margins (its edge there a median 0.3 mm off the eyeball) to under both lids (its other edge
    1.6 mm off), moved onto our eye. Each vertex keeps its angle past ICT's lid edge on its side, at the same share of
    the way from the outer corner to the inner, and its height off the eyeball scaled to ours - but stays under our
    lid's skin where that is lower. Shaded as a tear film: water's Fresnel reflection (IOR 1.336) over a transparent
    film, CC5's example roughness, faded in from its edge on the eyeball (CC5's Edge Fadeout); seen by the camera and
    by reflections only, so it casts nothing."""
    faces, ict_points, _ = _ict_part(*ICT_TEAR)
    ict_v = _ict()[0]
    ict_polys = [[c[0] for c in f] for f in _ict()[2][:ICT_SKIN_POLYGONS]]
    i = face_shape.eye_opening(ict_v[slice(*ICT_EYE)], ict_v[slice(*ICT_SKIN)], ict_polys, (0.0, 0.0), 0.3, 0.8)  # cm
    az, el, dist = face_shape.angles(ict_points, i.centre)
    off = (dist - i.radius) * o.radius / i.radius
    a = o.outer + (az - i.outer) / (i.inner - i.outer) * (o.inner - o.outer)
    upper_side = el > (np.interp(az, i.centres, i.upper) + np.interp(az, i.centres, i.lower)) / 2
    i_edge = np.where(upper_side, np.interp(az, i.centres, i.upper), np.interp(az, i.centres, i.lower))
    o_edge = np.where(upper_side, np.interp(a, o.centres, o.upper), np.interp(a, o.centres, o.lower))
    t_dir = face_shape.direction(a, o_edge + (el - i_edge))
    # under our lid: no higher than the skin within 3 deg of it, less 0.2 mm
    s_az, s_el, s_dist = face_shape.angles(skin, o.centre)
    near_eye = (s_dist < o.radius + 0.005) & (skin[:, 1] < o.centre[1])
    s_dir, s_off = face_shape.direction(s_az[near_eye], s_el[near_eye]), s_dist[near_eye] - o.radius
    close = np.degrees(np.arccos(np.clip(t_dir @ s_dir.T, -1.0, 1.0))) < 3.0
    ceiling = np.where(close, s_off[None, :], np.inf).min(axis=1) - 0.0002
    lowered = int((off > ceiling).sum())
    off = np.maximum(np.minimum(off, ceiling), 0.0001)
    points = o.centre + (o.radius + off)[:, None] * t_dir
    # the strip's share from its rim on the eyeball (0) to its rim under the lids (1), in steps along its edges
    count = collections.Counter(tuple(sorted((f[k], f[k - 1]))) for f in faces for k in range(len(f)))
    links, rim = collections.defaultdict(set), collections.defaultdict(set)
    for (p, q), n in count.items():
        for graph in (links, rim) if n == 1 else (links,):
            graph[p].add(q)
            graph[q].add(p)
    loops, seen = [], set()
    for start in rim:
        if start not in seen:
            loop, todo = set(), [start]
            while todo:
                p = todo.pop()
                if p not in loop:
                    loop.add(p)
                    todo.extend(rim[p])
            seen |= loop
            loops.append(loop)
    assert len(loops) == 2, f"ICT's tear strip should have two rims, found {len(loops)}"
    on_eye, under_lid = sorted(loops, key=lambda lp: np.median(dist[list(lp)]))

    def steps(sources):
        d, front = dict.fromkeys(sources, 0), list(sources)
        while front:
            nxt = []
            for p in front:
                for q in links[p]:
                    if q not in d:
                        d[q] = d[p] + 1
                        nxt.append(q)
            front = nxt
        return np.array([d[k] for k in range(len(points))], dtype=float)

    near = steps(on_eye)
    share = near / (near + steps(under_lid))
    mesh = bpy.data.meshes.new(f"{name} tearline")
    mesh.from_pydata(points.tolist(), [], faces)
    mesh.attributes.new("share", "FLOAT", "POINT").data.foreach_set("value", share)
    mesh.update()
    outward = np.array([(np.array(p.center) - o.centre) @ np.array(p.normal) for p in mesh.polygons])
    if np.median(outward) < 0:  # mirrored onto the right eye: facing away from the eyeball again
        mesh.flip_normals()
    obj = bpy.data.objects.new(f"{name} tearline", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.visible_shadow = obj.visible_diffuse = obj.visible_volume_scatter = False
    mat = bpy.data.materials.new(f"{name} tearline")
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "share"
    fade = nt.nodes.new("ShaderNodeMapRange")
    fade.interpolation_type = "SMOOTHSTEP"
    fade.inputs["From Max"].default_value = TEAR_FADE
    nt.links.new(attr.outputs["Fac"], fade.inputs["Value"])
    fresnel = nt.nodes.new("ShaderNodeFresnel")
    fresnel.inputs["IOR"].default_value = 1.336
    wet = nt.nodes.new("ShaderNodeMath")
    wet.operation = "MULTIPLY"
    nt.links.new(fresnel.outputs["Fac"], wet.inputs[0])
    nt.links.new(fade.outputs["Result"], wet.inputs[1])
    gloss = nt.nodes.new("ShaderNodeBsdfGlossy")
    gloss.inputs["Roughness"].default_value = TEAR_ROUGHNESS
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(wet.outputs["Value"], mix.inputs["Fac"])
    nt.links.new(nt.nodes.new("ShaderNodeBsdfTransparent").outputs["BSDF"], mix.inputs[1])
    nt.links.new(gloss.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    mesh.materials.append(mat)
    print(f"  {name} tearline: {len(points)} vertices, {off.min() * 1000:.2f}-{off.max() * 1000:.2f} mm off the eyeball, "
          f"{lowered} kept under the lid")
    return obj


LASH_PACK = "E:/Dev/3D/just-stage/.dev/cache/mh_packs/makehuman_system_assets_cc0.zip"  # sha256 b542127a…, CC0


def _add_lashes(body, style="eyelashes01", kind="eyelashes", shorten=0.6, colour=(0.012, 0.009, 0.008), lower=False):
    """MakeHuman's lash cards (its CC0 system assets: a strip mesh, an MHCLO binding to hm08, a lash texture with
    transparency) fitted to our head by MHCLO — MakeHuman's own way, and the card lashes CC5 and MetaHuman use. Fitted
    after the lid keys, so they sit on the lids as shaped."""
    import zipfile

    mhclo = importlib.import_module("bl_ext.system.juststage.core.mhclo")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    pack = zipfile.ZipFile(LASH_PACK)
    folder = f"{kind}/{style}/{style}"
    binding = mhclo.parse(pack.read(folder + ".mhclo").decode("utf-8", "replace"))
    co = mhclo.fit(binding, build.shaped_coords(body))
    uvs, faces = [], []
    for line in pack.read(folder + ".obj").decode("utf-8", "replace").splitlines():
        if line.startswith("vt "):
            uvs.append([float(x) for x in line.split()[1:3]])
        elif line.startswith("f "):
            faces.append([tuple(int(x) - 1 if x else -1 for x in (c.split("/") + [""])[:2]) for c in line.split()[1:]])
    skin = build.shaped_coords(body)[:13380]  # the body's own vertices, not its helpers
    near = np.array([skin[np.argmin(np.linalg.norm(skin - v, axis=1))] for v in co])
    co = near + (co - near) * shorten
    if not lower:  # eyelashes01's texture holds two upper strips (its top half) and two lower ones (bottom right): a card
        # is a lower lash when its UV centre lies there (the root-height rule dropped most upper cards too - round 45)
        centre = [np.mean([uvs[c[1]] for c in face], axis=0) for face in faces]
        down = [v < 0.41 or u > 0.74 for u, v in centre]
        faces = [face for face, d in zip(faces, down) if not d]
        print(f"{kind}: {sum(down)} lower cards dropped")
    mesh = bpy.data.meshes.new(f"{body.name} {style}")
    mesh.from_pydata(co.tolist(), [], [[c[0] for c in f] for f in faces])
    layer = mesh.uv_layers.new(name="UVMap")
    flat = [uvs[c[1]] for f in faces for c in f]
    for loop, uv in zip(layer.data, flat):
        loop.uv = uv
    obj = bpy.data.objects.new(f"{body.name} {style}", mesh)
    bpy.context.scene.collection.objects.link(obj)
    tex_path = DIR + f"{style}.png"
    Path(tex_path).write_bytes(pack.read(folder + ".png"))
    mat = bpy.data.materials.new(f"{body.name} {style}")
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(tex_path)
    bsdf.inputs["Base Color"].default_value = (*colour, 1.0)  # dark brown-black hair
    bsdf.inputs["Roughness"].default_value = 0.45
    bsdf.inputs["Specular IOR Level"].default_value = 0.0  # the asset's .mhmat: specularColor 0 0 0
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    mesh.materials.append(mat)
    obj.visible_shadow = False  # the asset's .mhmat: castShadows False
    print(f"{kind}: {style}, {len(co)} vertices, {len(faces)} cards, {shorten:.0%} length")


LASHES = os.environ.get("FACETEST_LASHES", "cards")  # rec 7's strands at real counts, or "cards" (MakeHuman's)
#: per eye and lid: count, length at the longest and at the corners (mm), the angle off the eyeball at the root and the
#: curl to the tip (degrees). Counts: StatPearls' 90-160 upper, 75-80 lower; lengths and curl starting values
LASH_UPPER = {"count": 120, "long": 10.0, "short": 6.0, "rise": 15.0, "curl": 60.0}
LASH_LOWER = {"count": 75, "long": 6.0, "short": 3.5, "rise": 10.0, "curl": 25.0}
LASH_POINTS = 12  # the research: 10+ points each for the curl (the pack's lashes have 5)
LASH_RADIUS = (0.00005, 0.000012)  # at the root and the tip (m): 0.1 mm thick at the root
LASH_MELANIN, LASH_REDNESS = 0.95, 0.25  # near black-brown


def _strand_lashes(body, openings, seed=7):
    """Rec 7's lashes at real counts (approved 2026-10-30: "brows and lashes at real counts (lashes 90-160 upper)";
    `../plans/2026-10-30-research-hair-eyes-teeth.md`: 90-160 upper in 5-6 rows, 75-80 lower in 3-4, per eye, 10+ points
    each for the curl). MetaHuman's way - strand grooms - as Blender hair curves: roots on the lid's front skin just past
    the opening's edge (face_shape.eye_opening), found by rays from in front onto the subdivided surface the camera
    sees, in a band 0.5-2 deg wide (the rows), none by the inner corner; each lash grows out from the eyeball and curls
    away from the eye, longest just outside the middle, the outer ones leaning outward; Principled Hair BSDF by melanin,
    rendered as 3D curves."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    rng = np.random.default_rng(seed)
    to_local = np.array(body.matrix_world.inverted())
    to_world = np.array(body.matrix_world)
    tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())  # its local space
    strands, missed = [], 0
    for o in openings.values():
        outward = np.sign(o.outer - o.inner)
        for spec, side in ((LASH_UPPER, 1.0), (LASH_LOWER, -1.0)):
            n = spec["count"]
            f = np.sort(rng.uniform(0.06, 0.97, n))  # the share of the way from the inner corner to the outer
            az = o.inner + f * (o.outer - o.inner)
            el = np.interp(az, o.centres, o.upper if side > 0 else o.lower) + side * rng.uniform(0.5, 2.0, n)
            dirs = face_shape.direction(az, el)
            for k in range(n):
                start = o.centre + dirs[k] * (o.radius + 0.02)
                s_local = to_local[:3, :3] @ start + to_local[:3, 3]
                hit = tree.ray_cast(Vector(s_local), Vector(to_local[:3, :3] @ -dirs[k]), 0.025)
                if hit[0] is None:
                    missed += 1
                    continue
                normal = to_world[:3, :3] @ np.array(hit[1])
                root = to_world[:3, :3] @ np.array(hit[0]) + to_world[:3, 3] - 0.0001 * normal / np.linalg.norm(normal)
                radial = (root - o.centre) / np.linalg.norm(root - o.centre)
                away = (face_shape.direction(az[k:k + 1], el[k:k + 1] + side)[0] - dirs[k])  # up for the upper lid
                away -= (away @ radial) * radial
                away /= np.linalg.norm(away)
                along = face_shape.direction(az[k:k + 1] + outward, el[k:k + 1])[0] - dirs[k]  # toward the outer corner
                along -= (along @ radial) * radial
                along /= np.linalg.norm(along)
                length = 0.001 * rng.uniform(0.85, 1.1) * (spec["short"] + (spec["long"] - spec["short"]) * np.sin(np.pi * f[k] ** 1.3))
                t = np.linspace(0.0, 1.0, LASH_POINTS)
                theta = np.radians(spec["rise"] + rng.normal(0.0, 5.0)) + np.radians(spec["curl"] + rng.normal(0.0, 10.0)) * t ** 1.5
                d = np.cos(theta)[:, None] * radial + np.sin(theta)[:, None] * away + 0.3 * (f[k] - 0.5) * along
                d /= np.linalg.norm(d, axis=1, keepdims=True)
                steps = np.vstack([np.zeros(3), d[:-1] * length / (LASH_POINTS - 1)])
                strands.append(root + np.cumsum(steps, axis=0))
    curves = bpy.data.hair_curves.new(f"{body.name} lashes")
    curves.add_curves([LASH_POINTS] * len(strands))
    curves.position_data.foreach_set("vector", np.concatenate(strands).astype(np.float32).ravel())
    t = np.tile(np.linspace(0.0, 1.0, LASH_POINTS), len(strands))
    curves.attributes.new("radius", "FLOAT", "POINT").data.foreach_set("value", np.interp(t, [0.0, 1.0], LASH_RADIUS).astype(np.float32))
    obj = bpy.data.objects.new(f"{body.name} lashes", curves)
    bpy.context.scene.collection.objects.link(obj)
    mat = bpy.data.materials.new(f"{body.name} lashes")
    nt = mat.node_tree
    nt.nodes.clear()
    hair = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
    hair.parametrization = "MELANIN"
    hair.inputs["Melanin"].default_value = LASH_MELANIN
    hair.inputs["Melanin Redness"].default_value = LASH_REDNESS
    nt.links.new(hair.outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs["Surface"])
    curves.materials.append(mat)
    bpy.context.scene.cycles_curves.shape = "THICK"  # 3D curves for close-ups (the research)
    print(f"lashes: {len(strands)} strands ({missed} roots missed), {LASH_POINTS} points each")
    return obj

def _pad(img, mask, px=16):
    """Each UV island grown outward by `px` texels with its own edge values (a bake's "margin"): filtering at UV seams
    otherwise blends in the fill outside the islands — the pale line on the neck's seam."""
    out = img.astype(np.float32).copy()
    known = mask.copy()
    for _ in range(px):
        grow = np.zeros(out.shape, np.float32)
        count = np.zeros(mask.shape, np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            shifted_known = np.roll(known, (dy, dx), axis=(0, 1))
            shifted = np.roll(out, (dy, dx), axis=(0, 1))
            grow += shifted * (shifted_known[..., None] if out.ndim == 3 else shifted_known)
            count += shifted_known
        new = (~known) & (count > 0)
        out[new] = (grow[new] / (count[new][:, None] if out.ndim == 3 else count[new]))
        known |= new
    return out



def _head_tile(body):
    """The head's own texture tile (the standards spec's UDIM 1001, `docs/standards/character-data-model.md` "UV
    layout and tiles"): hm08's UV islands of everything painted (above FADE_FROM) packed by Blender's own packer into a
    0-1 square of their own. On the body's shared map the face had 3.8 texels/mm against the close painting's ~7.5;
    packed it gets 6.0 (measured 2026-10-31; prioritising the face island gains nothing - it already holds 3,028 of
    the head's 4,018 polygons). Polygons below sit on one reserved corner (the plain skin colour)."""
    me = body.data
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    src = me.uv_layers["UVMap"]
    uv = np.empty(len(me.loops) * 2, np.float32)
    src.data.foreach_get("uv", uv)
    me.uv_layers.new(name="HeadTile").data.foreach_set("uv", uv)
    pick = np.array([co[list(p.vertices)][:, 2].max() > FADE_FROM - 0.02 and max(p.vertices) < 13380 for p in me.polygons])
    chosen = set(int(v) for p, k in zip(me.polygons, pick) if k for v in p.vertices)
    for v in me.vertices:
        v.select = v.index in chosen
    for e in me.edges:
        e.select = all(v in chosen for v in e.vertices)
    for p, k in zip(me.polygons, pick):
        p.select = bool(k)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    me.uv_layers.active = me.uv_layers["HeadTile"]
    bpy.context.scene.tool_settings.mesh_select_mode = (False, False, True)
    bpy.context.scene.tool_settings.use_uv_select_sync = False
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(udim_source="CLOSEST_UDIM", rotate=True, scale=True, margin=0.002)
    bpy.ops.object.mode_set(mode="OBJECT")
    tile = me.uv_layers["HeadTile"]
    packed = np.empty(len(me.loops) * 2, np.float32)
    tile.data.foreach_get("uv", packed)
    packed = packed.reshape(-1, 2) * 0.985  # the corner beyond 0.985 stays free
    loop_pick = np.zeros(len(me.loops), bool)
    for p, k in zip(me.polygons, pick):
        if k:
            loop_pick[list(p.loop_indices)] = True
    packed[~loop_pick] = 0.995  # everything else on the reserved corner
    tile.data.foreach_set("uv", packed.ravel())
    me.uv_layers.active = src
    src.active_render = True  # the pore tile and anything else on plain UV coordinates keep hm08's layout
    print(f"head tile: {int(pick.sum())} polygons packed into their own map")


def test_face_project():
    t0 = time.time()
    bpy.ops.wm.open_mainfile(filepath=DIR + "face.blend")
    body = bpy.data.objects["Face"]
    # each eye's opening, once, from the untouched eye (its iris marks the gaze; later its materials are replaced and
    # its cornea split off, which moves its bounding box): for the lashes, the occlusion and the tearline
    skin = importlib.import_module("bl_ext.system.juststage.modules.body.build").shaped_coords(body)[:13380].astype(np.float64)
    polys = face_shape.skin_polygons(body)
    openings = {}
    for eye_name in ("Face.eyeLeft", "Face.eyeRight"):
        eye = bpy.data.objects[eye_name]
        openings[eye_name] = face_shape.eye_opening(face_shape.world_points(eye), skin, polys, face_shape.gaze(eye), 0.003, 0.008)
    _strand_lashes(body, openings) if LASHES == "strands" else _add_lashes(body)
    _head_tile(body)
    # brows: the painted ones in the skin - MakeHuman's brow cards (010, 011, 012, masked or not) all sat higher and more
    # arched than the painting's and doubled them; without cards the painted brows read as hair (round 43 trials)
    api = importlib.import_module("bl_ext.system.juststage.api")
    character = body.juststage.character_id
    # brows and lashes as strands (the hair module's MakeHuman CC0 grooms), dark brown: Principled Hair melanin
    for style, melanin, redness in ():  # lashes off until the groom curls: its strands hung across the eyes
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
    mesh.uv_layers["HeadTile"].data.foreach_get("uv", uvs)  # the head's own tile (_head_tile)
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
        # away from the view's silhouettes: pixels on an outline are part background (the pale ear rims and neck streak)
        # ...and its depth jumps (a jaw in front of the neck: pixels on that edge blend both — the neck's pale line)
        near = np.where(depth < 0.999, depth, 1.0).astype(np.float32)
        hi, lo = near.copy(), near.copy()
        for dy in (-2, -1, 0, 1, 2):
            for dx in (-2, -1, 0, 1, 2):
                shifted = np.roll(near, (dy, dx), axis=(0, 1))
                hi, lo = np.maximum(hi, shifted), np.minimum(lo, shifted)
        smooth_here = ((depth < 0.999) & (hi - lo < 0.01)).astype(np.float32)
        inside = _blur(smooth_here[..., None], 4.0)
        clear_of_edge = up.sample(np.clip((inside - 0.5) / 0.45, 0.0, 1.0), col, row)[:, 0]
        return facing * frame * clear_of_edge, col, row

    lum = np.array(sd.LUMA)
    sub = np.arange(0, len(points), 16)
    looks = {}
    for view in VIEWS:
        w, col, row = view_samples(view, sub)
        looks[view] = (w, up.sample(_blur(_view_map("albedo", view), 6.0), col, row) @ lum)
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
        albedo = _view_map("albedo", view) * gains[view]
        nworld = _view_map("nworld", view)
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
    eye_gap = np.full(len(points), 1.0)
    facing_eye = np.zeros(len(points), dtype=bool)
    for eye_name in ("Face.eyeLeft", "Face.eyeRight"):
        eye = bpy.data.objects[eye_name]
        ev = np.array([v.co for v in eye.data.vertices]) @ np.array(eye.matrix_world)[:3, :3].T + np.array(eye.matrix_world)[:3, 3]
        e_centre = (ev.min(axis=0) + ev.max(axis=0)) / 2
        e_radius = float(np.median(np.linalg.norm(ev - e_centre, axis=1)))
        to_eye = e_centre - points
        gap_here = np.linalg.norm(to_eye, axis=1) - e_radius
        eye_gap = np.minimum(eye_gap, gap_here)
        inward = (normals * to_eye).sum(axis=1) / (np.linalg.norm(to_eye, axis=1) + 1e-9) > 0.2
        facing_eye |= inward & (gap_here < 0.0012)
    rim = facing_eye
    near_rim = (eye_gap >= 0.003) & (eye_gap < 0.007) & covered
    if near_rim.any():
        albedo[rim] = np.median(albedo[near_rim], axis=0) * np.array([0.9, 0.78, 0.78])
        nrm[rim] = normals[rim]
    print(f"  lid rim: {rim.sum()} texels take the rim's colour")
    # the lips' contact takes the painting's own colours: the clay views now have the closed lips (face_shape.py), so no
    # view sees teeth or a gap there (round 44: the flat colour that replaced them read as a strip under the upper lip)
    t = np.clip((points[:, 2] - FADE_FROM) / (FADE_TO - FADE_FROM), 0.0, 1.0)
    fade = (t * t * (3 - 2 * t)) * np.clip(low_w / (0.4 * np.median(low_w[covered])), 0.0, 1.0) ** 2  # grazing-only texels fade to the skin's median
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
    albedo_map = _pad(albedo_map, mask)
    srgb = np.clip(albedo_map, 0.0, 1.0)
    srgb = np.where(srgb <= 0.0031308, srgb * 12.92, 1.055 * srgb ** (1 / 2.4) - 0.055)
    head_uv = nodes.new("ShaderNodeUVMap")
    head_uv.uv_map = "HeadTile"
    albedo_tex = nodes.new("ShaderNodeTexImage")
    albedo_tex.image = _image("face albedo", srgb, "sRGB")
    links.new(head_uv.outputs["UV"], albedo_tex.inputs["Vector"])
    gain = nodes.new("ShaderNodeVectorMath")
    gain.operation = "MULTIPLY"
    gain.inputs[1].default_value = (1.0, 1.0, 1.0)
    links.new(albedo_tex.outputs["Color"], gain.inputs[0])
    links.new(gain.outputs["Vector"], bsdf.inputs["Base Color"])

    rot_inv = np.array(body.matrix_world.to_3x3().inverted())
    nrm_map = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    nrm_map[..., 2] = 1.0
    nrm_map[mask] = nrm @ rot_inv.T
    nrm_map = _pad(nrm_map, mask)
    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = _image("face normal", nrm_map * 0.5 + 0.5, "Non-Color")
    normal_tex.interpolation = "Cubic"
    links.new(head_uv.outputs["UV"], normal_tex.inputs["Vector"])
    nmap = nodes.new("ShaderNodeNormalMap")
    nmap.space = "OBJECT"
    links.new(normal_tex.outputs["Color"], nmap.inputs["Color"])
    # outside the painted area the map holds only its fill: the surface's own normal there (the fill's flat "up" normal
    # shaded the neck below the paint wrongly)
    painted_tex = nodes.new("ShaderNodeTexImage")
    painted_tex.image = _image("face painted", _pad(mask.astype(np.float32), mask), "Non-Color")
    links.new(head_uv.outputs["UV"], painted_tex.inputs["Vector"])
    normal_mix = nodes.new("ShaderNodeMix")
    normal_mix.data_type = "VECTOR"
    geometry = nodes.new("ShaderNodeNewGeometry")
    links.new(painted_tex.outputs["Color"], normal_mix.inputs["Factor"])
    links.new(geometry.outputs["Normal"], next(i for i in normal_mix.inputs if i.identifier == "A_Vector"))
    links.new(nmap.outputs["Normal"], next(i for i in normal_mix.inputs if i.identifier == "B_Vector"))
    shading_normal = next(o for o in normal_mix.outputs if o.identifier == "Result_Vector")
    # off by default: round 48 measured no gain - the paintings' normals (Sapiens2) carry no hooded fold over the lid
    # (raw vs ours ~5 deg apart; neither shows it), and the displacement tore the lips' contact and spiked the ears
    if os.environ.get("RELIEF_GEOMETRY", "0") == "1":
        # the paintings' relief as geometry (relief_geometry.py, Nehab et al. 2005): heights along the mesh normal that
        # give the surface the paintings' normals - the lid's fold, the brow ridge, the lips - so they cast shadows and
        # turn edges, not only shade (rec 5); solved at half the maps' resolution (0.55 mm texels); none at the eyes'
        # rims (the lids stay on the eyeballs) or the lips' contact (the mouth stays closed)
        t_relief = time.time()
        target_map = np.zeros((SIZE, SIZE, 3), np.float32)
        target_map[mask] = nrm
        mesh_map = np.zeros((SIZE, SIZE, 3), np.float32)
        mesh_map[mask] = normals
        keep = np.clip((eye_gap - 0.0015) / 0.004, 0.0, 1.0)
        keep *= 1.0 - np.exp(-(((points[:, 2] - 1.5484) / 0.0025) ** 2)) * (np.abs(points[:, 0]) < 0.03)
        keep_map = np.zeros((SIZE, SIZE), np.float32)
        keep_map[mask] = keep
        half = mask[::2, ::2]
        lift = relief_geometry.heights(pos_map[::2, ::2].astype(np.float64), mesh_map[::2, ::2].astype(np.float64),
                                       target_map[::2, ::2].astype(np.float64), half,
                                       max_step=0.003) * keep_map[::2, ::2]
        lift = np.repeat(np.repeat(lift, 2, axis=0), 2, axis=1)
        lift[~mask] = 0.0
        lift = _pad(lift, mask)
        print(f"relief as geometry: heights {np.percentile(lift[mask], 1) * 1000:+.2f} to {np.percentile(lift[mask], 99) * 1000:+.2f} mm "
              f"(1st-99th percentile), {time.time() - t_relief:.0f}s")
        disp_img = bpy.data.images.new("face displacement", SIZE, SIZE, alpha=False, float_buffer=True)
        disp_img.colorspace_settings.name = "Non-Color"
        rgba = np.ones((SIZE, SIZE, 4), dtype=np.float32)
        rgba[..., :3] = lift[..., None]
        disp_img.pixels.foreach_set(rgba[::-1].ravel())
        disp_img.filepath_raw = DIR + "face_displacement.exr"
        disp_img.file_format = "OPEN_EXR"
        disp_img.save()
        disp_tex = nodes.new("ShaderNodeTexImage")
        disp_tex.image = disp_img
        disp_tex.interpolation = "Cubic"
        links.new(head_uv.outputs["UV"], disp_tex.inputs["Vector"])
        disp = nodes.new("ShaderNodeDisplacement")
        disp.space = "OBJECT"
        disp.inputs["Midlevel"].default_value = 0.0
        disp.inputs["Scale"].default_value = 1.0
        links.new(disp_tex.outputs["Color"], disp.inputs["Height"])
        out_node = next(n for n in nodes if n.type == "OUTPUT_MATERIAL")
        links.new(disp.outputs["Displacement"], out_node.inputs["Displacement"])
        mat.displacement_method = "DISPLACEMENT"  # the object-space normal map already gives the shading normal
        subsurf = next((m for m in body.modifiers if m.type == "SUBSURF"), None) or body.modifiers.new("Subdivision", "SUBSURF")
        subsurf.use_adaptive_subdivision = True  # Blender 5.3: diced to the pixel at render
        subsurf.adaptive_space = "PIXEL"
        subsurf.adaptive_pixel_size = 1.0

    lum_map = albedo_map @ lum
    pad = 13
    high = np.log(np.maximum(lum_map, 1e-4))
    high = high - sd.gaussian_blur(np.pad(high, pad, mode="reflect"), 2.0)[pad:-pad, pad:-pad]  # pores, fine lines
    high[~mask] = 0.0
    height = np.clip(0.5 + high / (6.0 * high[mask].std()), 0.0, 1.0)
    height = _pad(height, mask)
    rough = np.full((SIZE, SIZE), ROUGH, dtype=np.float32)
    tzone = np.exp(-((points[:, 0] / 0.03) ** 2)) * np.clip(-normals[:, 1], 0.0, 1.0)
    rough[mask] = ROUGH + (ROUGH_TZONE - ROUGH) * tzone + 0.15 * (0.5 - height[mask])
    cavity = np.clip(1.0 - 2.5 * np.maximum(0.0, 0.5 - height), 0.2, 1.0)
    rough += 0.2 * (1.0 - cavity)
    cavity_tex = nodes.new("ShaderNodeTexImage")
    cavity_tex.image = _image("face cavity", cavity, "Non-Color")
    links.new(head_uv.outputs["UV"], cavity_tex.inputs["Vector"])
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
    links.new(head_uv.outputs["UV"], rough_tex.inputs["Vector"])
    links.new(rough_tex.outputs["Color"], bsdf.inputs["Roughness"])
    height_tex = nodes.new("ShaderNodeTexImage")
    height_tex.image = _image("face height", height, "Non-Color")
    links.new(head_uv.outputs["UV"], height_tex.inputs["Vector"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = BUMP_STRENGTH
    bump.inputs["Distance"].default_value = BUMP_DISTANCE
    links.new(height_tex.outputs["Color"], bump.inputs["Height"])
    links.new(shading_normal, bump.inputs["Normal"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    # pores, the approaches side by side (the user: "so we test all approaches"): PORE_SOURCE=paint (the paintings'
    # own fine relief, above), scan (the Lee Perry-Smith scan's cheek tile, CC-BY 3.0, at its real size ~7.5 cm), both
    source = os.environ.get("PORE_SOURCE", "both")  # 2026-10-30: both read richest
    if source in ("scan", "both"):
        if source == "scan":
            bump.inputs["Strength"].default_value = 0.0
        tile = nodes.new("ShaderNodeTexImage")
        tile.image = bpy.data.images.load(DIR + "pores_lps.png")
        tile.image.colorspace_settings.name = "Non-Color"
        coords, mapping = nodes.new("ShaderNodeTexCoord"), nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (PORE_TILES, PORE_TILES, 1.0)
        links.new(coords.outputs["UV"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], tile.inputs["Vector"])
        scan_bump = nodes.new("ShaderNodeBump")
        scan_bump.inputs["Strength"].default_value = 0.35
        scan_bump.inputs["Distance"].default_value = 0.0002
        links.new(tile.outputs["Color"], scan_bump.inputs["Height"])
        links.new(bump.outputs["Normal"], scan_bump.inputs["Normal"])
        links.new(scan_bump.outputs["Normal"], bsdf.inputs["Normal"])
    print(f"pores from: {source}")

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
    catch = bpy.data.objects.new("catch", bpy.data.lights.new("catch", "AREA"))
    catch.visible_camera = False
    scene.collection.objects.link(catch)
    cam_pos = np.array(cams["face"]["matrix_world"])[:3, 3]
    catch.location = cam_pos + np.array([0.0, 0.0, 0.25])
    catch.rotation_euler = (__import__("mathutils").Vector(head_c - catch.location)).to_track_quat("-Z", "Y").to_euler()
    catch.data.size, catch.data.energy = 0.12, 15.0
    catch.visible_diffuse = catch.visible_transmission = catch.visible_volume_scatter = False  # reflections only
    receivers = bpy.data.collections.new("catch light receivers")  # light linking (Blender 4.0+): the eyes only -
    for eye_name in ("Face.eyeLeft", "Face.eyeRight"):  # on the skin it read as oil (round 35)
        receivers.objects.link(bpy.data.objects[eye_name])
    catch.light_linking.receiver_collection = receivers
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
        # MPFB2's EnhancedEye: a procedural iris (fibres, crypts, limbal ring) and white, on our eye's polar UVs (one
        # eye per map, centred, eyeball radius 0.46, iris 0.40 of it — measured); its colours from the painted iris
        iris_rr = rr[(rr > 0.3) & (rr < 0.8)]
        disk_col = colour[on_disk][(rr > 0.3) & (rr < 0.8)] if iris_rr.size else colour[on_disk]
        disk_lum = disk_col @ lum
        major = np.median(disk_col[disk_lum >= np.median(disk_lum)], axis=0) * 1.15
        minor = np.median(disk_col[disk_lum < np.median(disk_lum)], axis=0)
        e_mat = bpy.data.materials.new(f"JustStage eye ({eye_name})")
        made = mpfb_nodes.build_material(MPFB_EYES, e_mat, f"mpfb_eye.{eye_name}.")
        cc = bpy.data.node_groups[f"mpfb_eye.{eye_name}.CenterCoordinates"]
        combs = sorted((n for n in cc.nodes if n.type == "COMBXYZ"), key=lambda n: n.name)
        combs[0].inputs["X"].default_value, combs[0].inputs["Y"].default_value = 0.5, 0.5
        combs[1].inputs["X"].default_value, combs[1].inputs["Y"].default_value = 5.0, 5.0  # one eye per map
        next(n for n in cc.nodes if n.type == "VALUE").outputs[0].default_value = 0.46
        eye_in = made["EnhancedEye"].inputs
        eye_in["IrisToEyeWhiteRelation"].default_value = 0.40
        eye_in["PupilSize"].default_value = 0.16
        # calibrated like the skin (2026-10-30, round 27 against the painting, linear light measured at MediaPipe's iris
        # and lid points): our iris read greyer and lighter, our white cooler and darker than the painting's
        iris_gain = np.array([1.0, 0.78, 0.82])
        eye_in["IrisMajorColor"].default_value = (*np.clip(major * 1.8 * iris_gain, 0, 1), 1.0)  # lit head-on in the painting
        eye_in["IrisMinorColor"].default_value = (*np.clip(minor * 1.8 * iris_gain, 0, 1), 1.0)
        eye_in["IrisSection4Color"].default_value = (*np.clip(minor * 0.9, 0, 1), 1.0)  # a softer limbal ring
        eye_in["InnerLayerRoughness"].default_value = 0.35  # a glossy iris mirrored the grey studio
        eye_in["IrisBumpStrength"].default_value = 0.1  # 0.3 glittered under the catch light (round 36)
        eye_in["OuterLayerIOR"].default_value = 1.15  # its outer layer mirrored the grey studio from the side (round 37);
        # its alpha 0 turned the whole eye black (round 38) - a lower IOR keeps the layer, with a fifth of the shine
        # the white beside the iris (MediaPipe's iris edge × 1.25–1.6 toward each corner, linear): the painting's
        # (0.230, 0.165, 0.138) against round 27's (0.122, 0.106, 0.098) — (0.50, 0.45, 0.42) × (1.89, 1.56, 1.41)
        # round 46, measured at the white's outer side (7x7 spots beside each iris, where the painting's white is clean -
        # its inner corners are dark red tissue, which made a whole-white median read as matching): painting/ours
        # (0.240, 0.205, 0.186) / (0.333, 0.241, 0.202) = (0.72, 0.85, 0.92) on (0.94, 0.70, 0.59)
        eye_in["EyeWhiteColor"].default_value = (0.68, 0.60, 0.54, 1.0)
        eye_in["Clearcoat"].default_value = 0.0  # its coat mirrored the grey studio over the iris
        if os.environ.get("EYE_STYLE", "mpfb") == "mh":  # rounds 30–31: its brown read red-orange; MPFB2 kept
            import zipfile

            mh_path = DIR + "mh_brown_eye.png"
            if not Path(mh_path).exists():
                Path(mh_path).write_bytes(zipfile.ZipFile(LASH_PACK).read("eyes/materials/brown_eye.png"))
            mh = _linear(_pixels(mh_path)[..., :3])
            yy, xx = np.mgrid[0:1024, 0:1024]
            u, v = (xx + 0.5) / 1024, 1.0 - (yy + 0.5) / 1024
            k = 0.285 / 0.46
            mu, mv = 0.705 + (u - 0.5) * k, 0.7 + (v - 0.5) * k
            h_mh, w_mh = mh.shape[:2]
            baked = up.sample(mh, (mu * w_mh - 0.5).ravel(), ((1 - mv) * h_mh - 0.5).ravel()).reshape(1024, 1024, 3)
            r_uv = np.hypot(u - 0.5, v - 0.5)
            iris_px = (r_uv < 0.17) & (r_uv > 0.06)
            # MakeHuman's iris keeps its own colour (a per-channel tint blew its near-zero blue up 8× — round 30); only
            # its brightness becomes the painted iris' (×1.6: the painting lights the iris head-on — round 26)
            tint = float(major @ lum) * 1.6 / max(float(np.median(baked[iris_px] @ lum)), 1e-4)
            iris_all = r_uv < 0.185
            baked[iris_all] *= tint
            b_srgb = np.clip(baked, 0.0, 1.0)
            b_srgb = np.where(b_srgb <= 0.0031308, b_srgb * 12.92, 1.055 * b_srgb ** (1 / 2.4) - 0.055)
            e_mat = bpy.data.materials.new(f"JustStage eye ({eye_name}, MakeHuman texture)")
            e_bsdf = next(n for n in e_mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            e_tex = e_mat.node_tree.nodes.new("ShaderNodeTexImage")
            e_tex.image = _image(f"{eye_name} mh", b_srgb, "sRGB")
            e_mat.node_tree.links.new(e_tex.outputs["Color"], e_bsdf.inputs["Base Color"])
            e_bsdf.inputs["Roughness"].default_value = 0.35
            e_bsdf.inputs["Subsurface Weight"].default_value = 0.1
        for slot in eye.material_slots:
            if slot.material and "Cornea" not in slot.material.name:
                slot.material = e_mat
            elif slot.material:  # the cornea: clear, with half a Fresnel reflection — the catch-light, no grey veil
                c_nt = slot.material.node_tree
                c_out = next(n for n in c_nt.nodes if n.type == "OUTPUT_MATERIAL")
                c_mix, c_fres, c_half = (c_nt.nodes.new(t) for t in ("ShaderNodeMixShader", "ShaderNodeFresnel", "ShaderNodeMath"))
                c_fres.inputs["IOR"].default_value = 1.376
                c_half.operation, c_half.inputs[1].default_value = "MULTIPLY", 0.3
                c_gloss = c_nt.nodes.new("ShaderNodeBsdfGlossy")
                c_gloss.inputs["Roughness"].default_value = 0.02
                c_nt.links.new(c_fres.outputs["Fac"], c_half.inputs[0])
                c_nt.links.new(c_half.outputs["Value"], c_mix.inputs["Fac"])
                c_nt.links.new(c_nt.nodes.new("ShaderNodeBsdfTransparent").outputs["BSDF"], c_mix.inputs[1])
                c_nt.links.new(c_gloss.outputs["BSDF"], c_mix.inputs[2])
                c_nt.links.new(c_mix.outputs["Shader"], c_out.inputs["Surface"])
        # the cornea as its own object, unseen by shadow and diffuse rays: the white's ambient occlusion then sees only the
        # lids (with the shell in the eye's object it turned the white black - round 45 trials); the catch light still
        # reaches it (light linking)
        cornea_ids = [i for i, sl in enumerate(eye.material_slots) if sl.material and "Cornea" in sl.material.name]
        shell = eye.copy()
        shell.data, shell.name = eye.data.copy(), f"{eye_name} cornea"
        scene.collection.objects.link(shell)
        for obj, keep in ((eye, False), (shell, True)):
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if (f.material_index in cornea_ids) != keep], context="FACES")
            bm.to_mesh(obj.data)
            bm.free()
        shell.visible_shadow = shell.visible_diffuse = False
        receivers.objects.link(shell)
        _occlusion_shell(openings[eye_name], eye_name)
        receivers.objects.link(_tearline(openings[eye_name], skin, eye_name))  # its wet shine catches the eye light
        colour = np.zeros((1, 3)) + major  # for the print below
        white = np.array([True])
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
