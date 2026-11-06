# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body's UDIM layout (docs/standards/character-data-model.md, "UV layout and tiles": 1001 head and neck, 1002
torso, 1003 arms and hands, 1004 legs and feet, 1005 nails - CC5's tile assignment), made once on the default human
and kept as generated data, so every character gets the same layout and a skin's maps fit any of them.

    python tools/dev.py blender -b --python tools/make_udim.py

Each tile holds hm08's own UV islands of its region (the `UVMap` unwrap, cut where a region ends), packed by Blender's
own island packer (https://docs.blender.org/manual/en/5.3/modeling/meshes/editing/uv.html#pack-islands) into that tile.
The head tile is the face test's `_head_tile` (tools/face_test/test_face_project.py): everything above 1.28 m on the
default body - the face, scalp, ears, neck and the top of the shoulders - packed alone, which gave the face 6.0
texels/mm at 4096 against 3.8 on the shared map (measured 2026-10-31). Regions by each polygon's place on the default
body: the head as above; the arms beyond the shoulders (|x| > ARM_X); the legs below the crotch (z < LEG_Z); the nails
where MPFB2's CC0 nail masks (fetched) are bright; the torso the rest.

Writes `extension/juststage/data/generated/skin/udim.npz`: `uv` (each loop's UV, tile offsets included) and `tile`
(each polygon's tile, 1001-1005), for the body's polygons; the helpers' polygons sit on 1002's spare corner.
"""

from __future__ import annotations

import importlib

import bpy
import numpy as np

api = importlib.import_module("bl_ext.system.juststage.api")
paths = importlib.import_module("bl_ext.system.juststage.paths")
makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")

HEAD_Z = 1.30 - 0.02  # the face test's FADE_FROM less its 2 cm: the painting fades in up the neck from 1.30 m
ARM_X = 0.20  # beyond the shoulder's joint on the default body (its shoulders at |x| ~0.18)
LEG_Z = 0.84  # the crotch on the default body
NAIL_LEVEL = 0.5  # MPFB2's nail masks: white on the nails
MARGIN = 0.002  # the packer's margin (the face test's)
SHRINK = 0.985  # each tile's packing stays inside 0-0.985; the corner beyond is spare
SPARE = 0.995  # where polygons of no region sit (the helpers), in tile 1002


def _mask(name: str) -> np.ndarray:
    image = bpy.data.images.load(str(paths.makehuman("textures", name)))
    w, h = image.size
    pixels = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(pixels)
    bpy.data.images.remove(image)
    return pixels.reshape(h, w, 4)[..., 0]


def _regions(obj) -> np.ndarray:
    me = obj.data
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers["UVMap"].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    nails = np.maximum(_mask("mpfb_fingernails.jpg"), _mask("mpfb_toenails.jpg"))
    h, w = nails.shape
    tile = np.zeros(len(me.polygons), np.int32)
    for p in me.polygons:
        verts = list(p.vertices)
        if max(verts) >= makehuman.BODY_VERTICES:
            continue  # a helper: no region
        pts = co[verts]
        loops = list(p.loop_indices)
        u, v = uv[loops].mean(axis=0)
        if nails[min(int(v * h), h - 1), min(int(u * w), w - 1)] > NAIL_LEVEL:
            tile[p.index] = 1005
        elif pts[:, 2].max() > HEAD_Z:
            tile[p.index] = 1001
        elif np.abs(pts[:, 0]).mean() > ARM_X:
            tile[p.index] = 1003
        elif pts[:, 2].mean() < LEG_Z:
            tile[p.index] = 1004
        else:
            tile[p.index] = 1002
    return tile


def _pack(obj, chosen: np.ndarray) -> np.ndarray:
    """The chosen polygons' islands (of UVMap, cut where the choice ends) packed into 0-1 by Blender's packer."""
    me = obj.data
    src = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers["UVMap"].data.foreach_get("uv", src)
    work = me.uv_layers.new(name="pack")
    work.data.foreach_set("uv", src)
    verts = {int(v) for p in me.polygons if chosen[p.index] for v in p.vertices}
    for v in me.vertices:
        v.select = v.index in verts
    for e in me.edges:
        e.select = all(v in verts for v in e.vertices)
    for p in me.polygons:
        p.select = bool(chosen[p.index])
    me.uv_layers.active = work
    scene = bpy.context.scene
    scene.tool_settings.mesh_select_mode = (False, False, True)
    scene.tool_settings.use_uv_select_sync = False
    with bpy.context.temp_override(active_object=obj, object=obj):
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.uv.select_all(action="SELECT")
        bpy.ops.uv.pack_islands(udim_source="CLOSEST_UDIM", rotate=True, scale=True, margin=MARGIN)
        bpy.ops.object.mode_set(mode="OBJECT")
    packed = np.empty(len(me.loops) * 2, np.float32)
    work = me.uv_layers["pack"]  # edit mode rebuilt the layers: the old reference is gone
    work.data.foreach_get("uv", packed)
    me.uv_layers.remove(work)
    return packed.reshape(-1, 2)


def main() -> None:
    # on hm08 itself (base v1): the layout is per hm08 loop; base v2's new faces take their old faces' place in it
    # (modules/body/base.py), so every skin painted in it stays valid
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    create = importlib.import_module("bl_ext.system.juststage.modules.body.body_create")
    defaults = create.Params()._asdict()
    for k in ("name", "dressed"):
        defaults.pop(k)
    obj = build.create_human("UDIM layout", defaults, base_version=1)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    tile = _regions(obj)
    me = obj.data
    loop_poly = np.empty(len(me.loops), np.int32)
    for p in me.polygons:
        loop_poly[list(p.loop_indices)] = p.index
    uv = np.full((len(me.loops), 2), SPARE, np.float32) + np.array([1.0, 0.0], np.float32)  # helpers: 1002's corner
    for number in (1001, 1002, 1003, 1004, 1005):
        chosen = tile == number
        packed = _pack(obj, chosen) * SHRINK
        on = chosen[loop_poly]
        uv[on] = packed[on] + np.array([number - 1001, 0.0], np.float32)
        print(f"tile {number}: {int(chosen.sum())} polygons")
    out = paths.GENERATED / "skin"
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "udim.npz", uv=uv, tile=tile)
    print(f"wrote {out / 'udim.npz'}: {len(uv)} loops, {len(tile)} polygons")


main()
