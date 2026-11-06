# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""tools/build_skins.py's bakes. The head tile's relief is moved from the face test's UV frames to the UDIM layer's by
a Normal bake on the face test's character - with its shape keys on, Cycles bakes their normal change too (measured
2026-11-06: a plain BSDF baked p50 0.10 / p90 0.31 tilt on man_a's round.blend, flat on the Basis), and every scan
skin carried the face test's face as false shading (the gate: a brown lower face, dark sockets, a hard edge)."""

import importlib.util
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location("build_skins", str(ROOT / "tools" / "build_skins.py"))
build_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_skins)


def _plain(nodes, links, out):
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])


import pytest


@pytest.mark.parametrize("modifier", ["", "MULTIRES"])
def test_a_normal_bake_ignores_the_shape_keys(modifier):
    """A plain surface bakes flat (no relief) whatever shape its keys give it - bare, or with the body's Multires."""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=16, y_subdivisions=16, size=1.0)
    grid = bpy.context.object
    grid.data.polygons.foreach_set("use_smooth", np.ones(len(grid.data.polygons), bool))
    grid.shape_key_add(name="Basis")
    bend = grid.shape_key_add(name="bend")
    for point in bend.data:
        point.co.z = 0.4 * point.co.x**2 + 0.3 * point.co.y  # a curve and a tilt
    bend.value = 1.0
    if modifier:
        grid.modifiers.new("levels", modifier)
    scene = bpy.context.scene
    engine = scene.render.engine
    scene.render.engine = "CYCLES"
    scene.cycles.device, scene.cycles.samples = "CPU", 1
    try:
        for o in bpy.context.selected_objects:
            o.select_set(False)
        bpy.context.view_layer.objects.active = grid
        grid.select_set(True)
        px = build_skins._bake(grid, "NORMAL", _plain, 64)
        covered = px[..., 2] > 0.01
        tilt = np.sqrt(((px[..., :2] * 2.0 - 1.0) ** 2).sum(-1))[covered]
        assert covered.mean() > 0.5
        assert np.percentile(tilt, 99) < 0.02
        assert grid.data.shape_keys.key_blocks["bend"].value == 1.0  # the character as it was
        assert not grid.show_only_shape_key and all(m.show_render for m in grid.modifiers)
    finally:
        scene.render.engine = engine
        bpy.data.objects.remove(grid)


def test_the_border_blend_meets_both_tiles_colours_at_their_border(tmp_path):
    """The design's piece 4: two tiles' colours meet without a step at their border (the gate's chest seam), and a
    place 5 cm or more from a border keeps its own colour."""
    maps = build_skins.maps
    nx, ny = 40, 10  # a 0.4 x 0.1 m strip: its left half on tile 1001, its right half on 1002
    co = [(0.4 * i / nx, 0.1 * j / ny, 0.0) for j in range(ny + 1) for i in range(nx + 1)]
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i)
             for j in range(ny) for i in range(nx)]  # fmt: skip
    me = bpy.data.meshes.new("strip")
    me.from_pydata(co, [], faces)
    uv = []
    for f in faces:
        right = np.mean([co[v][0] for v in f]) > 0.2
        for v in f:
            x, y, _z = co[v]
            u = (x - 0.2) / 0.2 if right else x / 0.2
            uv.append((0.25 + 0.5 * u + (1.0 if right else 0.0), 0.25 + 0.5 * y / 0.1))
    me.uv_layers.new(name=maps.UV).data.foreach_set("uv", np.array(uv, np.float32).ravel())
    strip = bpy.data.objects.new("strip", me)
    bpy.context.scene.collection.objects.link(strip)
    stems = {"base_color": "t.base_color"}
    for number, value in ((1001, 0.6), (1002, 0.4)):
        maps.write_png(tmp_path / f"t.base_color.{number}.png", np.full((256, 256, 3), value, np.float32))
    scene = bpy.context.scene
    engine = scene.render.engine
    scene.render.engine = "CYCLES"
    scene.cycles.device, scene.cycles.samples = "CPU", 1
    try:
        for o in bpy.context.selected_objects:
            o.select_set(False)
        bpy.context.view_layer.objects.active = strip
        strip.select_set(True)
        build_skins._border_blend(strip, tmp_path, stems)
        left = build_skins._read_png(tmp_path / "t.base_color.1001.png")[128, :, 0]
        right = build_skins._read_png(tmp_path / "t.base_color.1002.png")[128, :, 0]
        at_border = left[int(0.745 * 256)], right[int(0.255 * 256)]
        assert abs(at_border[0] - at_border[1]) < 0.02  # was 0.6 against 0.4
        assert 0.4 < at_border[0] < 0.6
        assert left[int(0.3 * 256)] == pytest.approx(0.6, abs=0.01)  # 18 cm away: its own
        assert right[int(0.7 * 256)] == pytest.approx(0.4, abs=0.01)
    finally:
        scene.render.engine = engine
        bpy.data.objects.remove(strip)
