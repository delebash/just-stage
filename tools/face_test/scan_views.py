# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material, step 2: pictures of a scan for finding its face - MetaHuman From Mesh's
way (markers found on a near-flat render of the textured mesh, unlit for albedo-textured meshes; `docs/plans/
2026-10-30-research-ai-photo-to-head.md` §4). The scan (scan_convert.py's arrays) lit by nothing but its own colour
(emission), seen by an orthographic camera from 12 turns about the vertical, framed on the head (the top ~16% of a
full body). Per view a colour picture and a position picture - the clay script's depth-override pattern
(test_face_clay.py: emission of a value, 1 sample, filter 0.01, a 32-bit EXR), here the world position - saved as
.npy for the steps outside Blender. Processor only (Cycles CPU, 8 threads).

With `face` (after scan_marks.py NAME): the square-on turn again, framed on the face MediaPipe found (its box 1.9x
wide), for RealDenseFace's points at ~0.25 mm a pixel instead of the whole bust's ~1.4 mm (MetaHuman From Mesh
promotes one frontal frame the same way).

Run: blender -b --factory-startup --python tools/face_test/scan_views.py -- NAME [face]
"""

import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

_spec = importlib.util.spec_from_file_location("scan_list", str(Path(__file__).with_name("scan_list.py")))
scan_list = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scan_list)

SIZE = 1024
TURNS = 12
FULL_BODY = 2.2  # height over width beyond which the scan is a full body (a bust is ~1-1.5)
HEAD_SHARE = 0.16  # of a full body's height: the head and a little neck


def build_mesh(name, src, scan):
    """The scan as one Blender mesh: vertices, triangles, corner UVs, a material per scan material."""
    co, tris, tri_uv, tri_mat = src["co"], src["tris"], src["tri_uv"], src["tri_mat"]
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(co))
    me.vertices.foreach_set("co", co.astype(np.float32).ravel())
    me.loops.add(tris.size)
    me.loops.foreach_set("vertex_index", tris.astype(np.int32).ravel())
    me.polygons.add(len(tris))
    me.polygons.foreach_set("loop_start", np.arange(0, tris.size, 3, dtype=np.int32))
    me.update()
    uv = me.uv_layers.new(name="UV")
    uv.data.foreach_set("uv", tri_uv.astype(np.float32).ravel())
    for m in json.loads(str(src["materials"])):
        me.materials.append(emission_material(m["name"], scan_list.texture_for(scan, m["name"])))
    me.polygons.foreach_set("material_index", tri_mat.astype(np.int32))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def emission_material(name, texture):
    """The surface shows its colour map as it is - no light, no shading (or flat grey without one)."""
    mat = bpy.data.materials.new(name)
    nt = mat.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if texture:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(texture, check_existing=True)
        nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    else:
        em.inputs["Color"].default_value = (0.2, 0.2, 0.2, 1.0)
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def position_material():
    mat = bpy.data.materials.new("position")
    nt = mat.node_tree
    nt.nodes.clear()
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    em = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(geo.outputs["Position"], em.inputs["Color"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def main(argv):
    name = argv[0]
    out = Path(scan_list.OUT) / name
    src = np.load(out / "src.npz")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    build_mesh(name, src, scan_list.SCANS[name])
    co = src["co"]
    lo, hi = co.min(0), co.max(0)
    height, width = hi[2] - lo[2], max(hi[0] - lo[0], hi[1] - lo[1])
    full_body = height > FULL_BODY * width
    frame = HEAD_SHARE * height if full_body else height
    top = co[co[:, 2] > hi[2] - frame]
    centre = Vector(((top[:, 0].min() + top[:, 0].max()) / 2, (top[:, 1].min() + top[:, 1].max()) / 2,
                     hi[2] - frame / 2))
    reach = float(np.hypot(top[:, 0] - centre.x, top[:, 1] - centre.y).max())
    span = float(max(frame, 2 * reach) * 1.08)

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.render.threads_mode, scene.render.threads = "FIXED", 8
    scene.render.resolution_x = scene.render.resolution_y = SIZE
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    scene.world = bpy.data.worlds.new("none")
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    cam.data.type, cam.data.ortho_scale = "ORTHO", span
    cam.data.clip_start, cam.data.clip_end = 0.001, 10 * (reach + span)
    scene.camera = cam
    pos_mat = position_material()
    cams = {}
    t0 = time.time()
    shots = [(f"turn{k:02d}", 2 * math.pi * k / TURNS, centre, span) for k in range(TURNS)]
    if len(argv) > 1 and argv[1] == "face":
        marks = json.loads((out / "marks.json").read_text())
        best = marks["best"].replace("view_", "")
        pts = np.asarray(marks["views"][marks["best"]]["points"])
        pos = np.load(out / f"pos_{best}.npy")
        old = json.loads((out / "views.json").read_text())["cams"][best]
        per_px = old["ortho_scale"] / SIZE
        (x0, y0), (x1, y1) = pts.min(0), pts.max(0)
        mid = pos[int(round((y0 + y1) / 2)), int(round((x0 + x1) / 2)), :3]  # the face's middle (the nose's side)
        M = np.asarray(old["matrix_world"])
        right, up = M[:3, 0], M[:3, 1]
        # the box's centre in the picture plane, through the old camera: its offset from the picture's centre
        dx, dy = ((x0 + x1) / 2 + 0.5 - SIZE / 2) * per_px, -((y0 + y1) / 2 + 0.5 - SIZE / 2) * per_px
        face_centre = Vector(M[:3, 3] + right * dx + up * dy)
        face_centre += Vector(M[:3, 2]) * float(np.dot(M[:3, 3] - mid, M[:3, 2])) * -1.0  # onto the face's depth
        shots = [("face", math.radians(old["turn_deg"]), face_centre, float(max(x1 - x0, y1 - y0) * per_px * 1.9))]
    for label, a, aim, frame_span in shots:
        cam.data.ortho_scale = frame_span
        offset = Vector((math.sin(a), -math.cos(a), 0.0)) * (reach + span) * 2
        cam.location = aim + offset
        cam.rotation_euler = (-offset).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        cams[label] = {"matrix_world": [list(r) for r in cam.matrix_world], "ortho_scale": frame_span, "size": SIZE,
                       "turn_deg": math.degrees(a)}
        scene.view_layers[0].material_override = None
        scene.cycles.samples, scene.cycles.use_denoising, scene.cycles.filter_width = 16, False, 1.5
        scene.render.image_settings.file_format, scene.render.image_settings.color_mode = "PNG", "RGBA"
        scene.render.image_settings.color_depth = "8"
        scene.render.filepath = str(out / f"view_{label}.png")
        bpy.ops.render.render(write_still=True)
        scene.view_layers[0].material_override = pos_mat
        scene.cycles.samples, scene.cycles.filter_width = 1, 0.01
        scene.render.image_settings.file_format = "OPEN_EXR"
        scene.render.image_settings.color_depth = "32"
        exr = out / f"pos_{label}.exr"
        scene.render.filepath = str(exr)
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(str(exr))
        px = np.empty(SIZE * SIZE * 4, np.float32)
        img.pixels.foreach_get(px)
        bpy.data.images.remove(img)
        np.save(out / f"pos_{label}.npy", np.flipud(px.reshape(SIZE, SIZE, 4)))  # row 0 at the top, as the PNG
        exr.unlink()
        print(f"{label}: {time.time() - t0:.0f}s")
    views = out / "views.json"
    data = json.loads(views.read_text()) if views.exists() and len(shots) == 1 else {}
    data.update({"full_body": bool(full_body), "centre": [float(c) for c in centre], "span": span})
    data.setdefault("cams", {}).update(cams)
    views.write_text(json.dumps(data, indent=1))
    print(f"{name}: {len(shots)} views, {'full body' if full_body else 'bust'}, span {span:.3f} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:])
