# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The neutral lip seal (the plan's §5 "Neutral lip seal", rec 17; build queue §19.4 item 2): hm08's neutral leaves a
see-through slit between the lips - 0.3-0.9 mm wide across the mouth's middle on the default man (rays from the front
to the front teeth's depth, 2026-11-08) - where HD Aaron's, like MetaHuman's required neutral, is sealed. The seal is
the smallest share of MakeHuman's own CC0 Faceunits `mouthClose` target that closes it (0.1 closed the default man's
at every point; the share is measured per character, as the lids' contact is), in a shape key of its own held at 1, made
again on every refit (`parts.refit`) - so the jaw and mouth keys open the mouth from the sealed lips. Standard pieces:
the seal is one of the face's own units, not a new shape; the measure is a ray test."""

from __future__ import annotations

import bpy
import numpy as np

from ... import paths
from ...core import makehuman

SEAL = "JustStage lip seal"  # the refit shape key that closes the neutral's slit
STEPS = (0.0, 0.05, 0.1, 0.15, 0.2, 0.3)  # shares of mouthClose tried, smallest first
ACROSS_MM, ACROSS_STEP_MM = 18.0, 6.0  # the measure's columns across the mouth's middle
DOWN_MM, UP_MM, STEP_MM = 4.0, 6.0, 0.2  # each column's rays, round the front teeth's height (a slit under 0.2 mm
# reads closed; the default man's was 0.3-0.9)
NEAR_M = 0.04  # the measure's surface: the polygons within this of the mouth (a slider drag refits every step)
#: the render draws the body subdivided (its Multires "levels"), which rounds the lips' edges back: measured 2026-11-08,
#: the coarse mesh closed at 0.05 on a man, a young woman and an old heavy man, the drawn one at 0.05, 0.15 and 0.05 -
#: so the coarse share plus this closes all three where it is drawn (a drawn measure needs a depsgraph update, ~0.4 s,
#: each slider step)
DRAWN_MARGIN = 0.1


def _mouth(character: bpy.types.Object) -> np.ndarray | None:
    """The front teeth's front (world): the depth a ray passes when it went between the lips."""
    from . import parts

    teeth = parts.parts_of(character).get("teeth")
    if teeth is None:
        return None
    mw = np.array(teeth.matrix_world)
    co = np.empty(len(teeth.data.vertices) * 3)
    teeth.data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
    front = co[co[:, 1] < co[:, 1].min() + 0.002]  # the incisors' fronts (the character faces -Y)
    return np.array([float(np.median(front[:, 0])), float(co[:, 1].min()), float(np.median(front[:, 2]))])


def _world(character: bpy.types.Object) -> np.ndarray:
    """The character's vertices with its shape keys mixed by their values (world) - what the mouth looks like: no
    modifier moves it (the helper mask only hides). No depsgraph update: one re-evaluates every groom (~183,000 scalp
    strands), ~0.4 s, and a slider drag refits at every step."""
    from ..body import build

    mw = np.array(character.matrix_world)
    return build.shaped_coords(character) @ mw[:3, :3].T + mw[:3, 3]


def slit_mm(character: bpy.types.Object, mouth: np.ndarray | None = None, co: np.ndarray | None = None) -> float:
    """The widest see-through gap between the lips over the mouth's middle (mm): per column, the height of the rays
    from the front that reach the front teeth's depth. `co`: the vertices to measure (world; default the shape now)."""

    mouth = _mouth(character) if mouth is None else mouth
    if mouth is None:
        return 0.0
    co = _world(character) if co is None else co
    return _rays(mouth, co, _mouth_polygons(character, co, mouth))


def _rays(mouth: np.ndarray, co: np.ndarray, polys: list) -> float:
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    if mouth is None:
        return 0.0
    near = np.linalg.norm(co - mouth, axis=1) < NEAR_M
    tree = BVHTree.FromPolygons([Vector(v) for v in co], [p for p in polys if near[p[0]]])
    widest = 0.0
    zs = np.arange(mouth[2] - DOWN_MM / 1000, mouth[2] + UP_MM / 1000, STEP_MM / 1000)
    for dx in np.arange(-ACROSS_MM, ACROSS_MM + 1e-6, ACROSS_STEP_MM) / 1000:
        through = 0
        for z in zs:
            hit = tree.ray_cast(Vector((mouth[0] + dx, mouth[1] - 0.06, z)), Vector((0.0, 1.0, 0.0)), 0.2)
            if hit[0] is None or hit[0][1] > mouth[1]:
                through += 1
        widest = max(widest, through * STEP_MM)
    return widest


def _mouth_polygons(character: bpy.types.Object, co: np.ndarray, mouth: np.ndarray) -> list:
    """The skin's polygons (not the helpers') with a corner within NEAR_M of the mouth."""
    me = character.data
    skin = makehuman.skin_mask(len(me.vertices))
    near = (np.linalg.norm(co - mouth, axis=1) < NEAR_M) & skin
    starts = np.empty(len(me.polygons), np.int64)
    totals = np.empty(len(me.polygons), np.int64)
    me.polygons.foreach_get("loop_start", starts)
    me.polygons.foreach_get("loop_total", totals)
    loops = np.empty(len(me.loops), np.int64)
    me.loops.foreach_get("vertex_index", loops)
    return [loops[s : s + n].tolist() for s, n in zip(starts, totals, strict=True)
            if near[loops[s]] and skin[loops[s : s + n]].all()]  # fmt: skip


def seal(character: bpy.types.Object) -> float:
    """The neutral's slit closed: the smallest STEPS share of mouthClose that leaves no see-through gap, in the SEAL
    key at 1; returns the share (0 when the lips already meet, or there are no teeth to measure against)."""
    keys = character.data.shape_keys
    if keys is None:
        return 0.0
    mouth = _mouth(character)
    key = keys.key_blocks.get(SEAL) or character.shape_key_add(name=SEAL, from_mix=False)
    key.value = 0.0
    key.slider_min, key.slider_max = 0.0, 1.0
    basis = np.empty(len(character.data.vertices) * 3, np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    basis = basis.reshape(-1, 3)
    key.data.foreach_set("co", basis.ravel())
    if mouth is None:
        return 0.0
    from ..body import base

    rows = makehuman.read_target(paths.makehuman("targets", "faceunits", "mouthClose.target"))
    index = np.fromiter((r[0] for r in rows), dtype=np.int64, count=len(rows))
    delta = np.array([r[1:] for r in rows], dtype=np.float32) * makehuman.SCALE_TO_METRES
    index, delta = base.extend(character, index, delta)
    rot = np.array(character.matrix_world)[:3, :3]
    unsealed = _world(character)
    chosen = STEPS[-1]
    for share in STEPS:
        co = unsealed.copy()
        co[index] += share * (delta @ rot.T)
        if slit_mm(character, mouth, co) == 0.0:
            chosen = min(share + DRAWN_MARGIN, STEPS[-1]) if share > 0.0 else 0.0
            break
    sealed = basis.copy()
    sealed[index] += chosen * delta
    key.data.foreach_set("co", sealed.ravel())
    key.value = 1.0
    drive(character)
    character.data.update()
    return chosen


#: the seal is the neutral's: it fades as the jaw opens, gone by a quarter of jawOpen - held at 1 it pulled the lips
#: ~5 mm together in every expression (mouthClose moves them up to 36 mm), so an open mouth hid the teeth (2026-11-08)
FADE = "max(0.0, 1.0 - 4.0 * j)"


def drive(character: bpy.types.Object) -> None:
    """The SEAL key's value from the jaw (FADE), once the face units are there; held at 1 until then."""
    keys = character.data.shape_keys
    if keys is None or SEAL not in keys.key_blocks or "jawOpen" not in keys.key_blocks:
        return
    key = keys.key_blocks[SEAL]
    key.driver_remove("value")
    driver = key.driver_add("value").driver
    driver.type = "SCRIPTED"
    driver.expression = FADE
    var = driver.variables.new()
    var.name = "j"
    var.type = "SINGLE_PROP"
    var.targets[0].id_type = "KEY"
    var.targets[0].id = keys
    var.targets[0].data_path = 'key_blocks["jawOpen"].value'


def drawn_slit_mm(character: bpy.types.Object) -> float:
    """The slit where it is drawn - the evaluated, subdivided mesh (tests and diagnostics; a depsgraph update)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = character.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mw = np.array(evaluated.matrix_world)
        co = np.empty(len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
        polys = [list(p.vertices) for p in mesh.polygons]
    finally:
        evaluated.to_mesh_clear()
    return _rays(_mouth(character), co, polys)
