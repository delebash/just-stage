# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the skin base's raw material, step 6: the scan's skin onto our head's texture layout by Blender's bake,
"Selected to Active" - "how a texture made on another topology (… a scan) moves onto hm08's UVs once the two heads
are aligned" (`docs/plans/2026-10-30-research-ai-texturing.md` §, Cycles manual `render/cycles/baking`). Active: our
head wrapped onto the scan (scan_fit.py) with its HeadTile UVs; selected: the scan placed on our head, showing its
own colour (emission). Rays start 5 mm outside our surface and reach 10 mm inward, so they find the scan's surface
within ±5 mm of ours; what they miss (our neck below a bust, the mouth's inside) stays empty. A second bake with
the scan all white gives that coverage.

Writes scans/NAME/bake_colour.png and bake_cover.png (4096², HeadTile). Processor only (Cycles CPU, 8 threads).
Run: blender -b --factory-startup --python tools/face_test/scan_bake.py -- NAME [normal]
(`normal`: the scan's relief as a tangent-space normal map, bake_normal.png - bake_normal below.)
"""

import importlib.util
import json
import sys
import time
from pathlib import Path

import bpy
import numpy as np


def _module(name):
    spec = importlib.util.spec_from_file_location(name, str(Path(__file__).with_name(f"{name}.py")))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scan_list = _module("scan_list")
scan_views = _module("scan_views")  # build_mesh, emission_material: one way to make a scan a Blender mesh

SIZE = 4096
EXTRUSION, RAY = 0.005, 0.010  # m


def target_image(name):
    img = bpy.data.images.new(name, SIZE, SIZE, alpha=False, float_buffer=False)
    img.generated_color = (0.0, 0.0, 0.0, 1.0)
    return img


def our_mesh(fitted, tris, tri_uv, image):
    """Our fitted head with its HeadTile UVs and a material whose active node is the bake's image."""
    src = {"co": fitted, "tris": tris, "tri_uv": tri_uv, "tri_mat": np.zeros(len(tris), np.int32),
           "materials": json.dumps([])}
    ob = scan_views.build_mesh("ours", src, {"textures": {}})
    mat = bpy.data.materials.new("bake_target")
    node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = image
    mat.node_tree.nodes.active = node
    ob.data.materials.append(mat)
    return ob, node


def bake(scene, ours, scan, filepath):
    bpy.ops.object.select_all(action="DESELECT")
    scan.select_set(True)
    ours.select_set(True)
    bpy.context.view_layer.objects.active = ours
    t = time.time()
    bpy.ops.object.bake(type="EMIT", use_selected_to_active=True, cage_extrusion=EXTRUSION, max_ray_distance=RAY,
                        margin=0, use_clear=False)
    print(f"baked {Path(filepath).name} ({time.time() - t:.0f}s)")


def bake_normal(scene, ours, scan, node, path):
    """The scan's surface relief against our fitted head's, in our head's tangent space (HeadTile): Blender's Normal
    bake, Selected to Active, the same reach as the colour's; our head shaded smooth so its own facets don't bake in.
    16-bit PNG, (0.5, 0.5, 1) where flat. Its low frequencies (the fit's leftover) are taken out after
    (skin_base.split) - what stays is the scan's folds, creases and lines."""
    for poly in ours.data.polygons:
        poly.use_smooth = True
    for poly in scan.data.polygons:
        poly.use_smooth = True
    image = bpy.data.images.new(path.stem, SIZE, SIZE, alpha=False, float_buffer=True)
    image.colorspace_settings.name = "Non-Color"
    image.generated_color = (0.5, 0.5, 1.0, 1.0)
    node.image = image
    bpy.ops.object.select_all(action="DESELECT")
    scan.select_set(True)
    ours.select_set(True)
    bpy.context.view_layer.objects.active = ours
    t = time.time()
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT", use_selected_to_active=True, cage_extrusion=EXTRUSION,
                        max_ray_distance=RAY, margin=0, use_clear=False)
    image.filepath_raw, image.file_format = str(path), "PNG"
    scene.render.image_settings.color_depth = "16"
    image.save_render(str(path), scene=scene)
    print(f"baked {path.name} ({time.time() - t:.0f}s)")


def main(argv):
    name = argv[0]
    out = Path(scan_list.OUT) / name
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.render.threads_mode, scene.render.threads = "FIXED", 8
    scene.cycles.samples = 4
    scene.view_settings.view_transform = "Standard"

    E = np.load(scan_list.reference(name))
    F = np.load(out / "fit.npz")
    used = F["used"]
    remap = -np.ones(len(E["co"]), dtype=np.int64)
    remap[used] = np.arange(len(used))
    colour = target_image(f"{name}_colour")
    ours, node = our_mesh(F["fitted"], remap[E["tris"]], E["tri_uv"], colour)

    src = dict(np.load(out / "src.npz"))
    M = F["placement"]
    src["co"] = src["co"].astype(np.float64) @ M[:3, :3].T + M[:3, 3]
    scan = scan_views.build_mesh(name, src, scan_list.SCANS[name])

    if argv[1:2] == ["normal"]:  # the scan's own relief as a tangent-space normal map on our fitted head
        bake_normal(scene, ours, scan, node, out / "bake_normal.png")
        return
    t0 = time.time()
    bake(scene, ours, scan, out / "bake_colour.png")
    colour.filepath_raw, colour.file_format = str(out / "bake_colour.png"), "PNG"
    colour.save()

    white = scan_views.emission_material("white", None)
    white.node_tree.nodes["Emission"].inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    for i in range(len(scan.data.materials)):
        scan.data.materials[i] = white
    cover = target_image(f"{name}_cover")
    node.image = cover
    bake(scene, ours, scan, out / "bake_cover.png")
    cover.filepath_raw, cover.file_format = str(out / "bake_cover.png"), "PNG"
    cover.save()
    px = np.empty(SIZE * SIZE * 4, np.float32)
    cover.pixels.foreach_get(px)
    print(f"{name}: covered {np.mean(px[0::4] > 0.5):.1%} of the 4096² tile ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:])
