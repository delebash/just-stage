# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Building a human on hm08 inside Blender — MPFB2's way (the spec's items 2 and 3).

The mesh comes in through Blender's own OBJ importer with the whole hm08 (helpers and joint cubes kept), MPFB2's vertex
groups from its metadata, the helpers masked while editing (a Mask modifier showing the `body` group), and the macro
targets as shape keys weighted by MakeHuman's macro blending.
"""

from __future__ import annotations

import functools
import json
import uuid

import bpy
import numpy as np
from mathutils import Matrix

from ... import paths
from ...core import makehuman

MACRO_PREFIX = "makehuman."
HELPER_MASK = "JustStage helpers"
LEVELS = "JustStage levels"
BASE_VERSION = 1


def _import_base(name: str) -> bpy.types.Object:
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(
        filepath=str(paths.makehuman("3dobjs", "base.obj")), use_split_objects=False, use_split_groups=False
    )
    new = set(bpy.data.objects) - before
    if len(new) != 1:
        raise RuntimeError(f"the OBJ import made {len(new)} objects, not 1")
    obj = new.pop()
    # bake the importer's axis turn into the mesh, then MakeHuman's decimetres into metres (MPFB2's METER scale)
    obj.data.transform(Matrix.Scale(makehuman.SCALE_TO_METRES, 4) @ obj.matrix_basis)
    obj.matrix_basis = Matrix.Identity(4)
    obj.name = obj.data.name = name
    obj.data.shade_smooth()
    return obj


def _add_vertex_groups(obj: bpy.types.Object) -> None:
    for group, indices in makehuman.vertex_groups(
        paths.makehuman("mesh_metadata", "basemesh_vertex_groups.json")
    ).items():
        obj.vertex_groups.new(name=group).add(indices, 1.0, "REPLACE")


def _mask_helpers(obj: bpy.types.Object) -> None:
    mask = obj.modifiers.new(HELPER_MASK, "MASK")
    mask.vertex_group = "body"


@functools.cache
def _target_offsets(target: str) -> tuple[np.ndarray, np.ndarray]:
    """A target's vertex indices and offsets in metres, read once (a slider drag rebuilds the macro stack each step)."""
    rows = makehuman.read_target(paths.makehuman("targets", f"{target}.target.gz"))
    index = np.fromiter((r[0] for r in rows), dtype=np.int64, count=len(rows))
    delta = np.array([r[1:] for r in rows], dtype=np.float32).reshape(-1, 3) * makehuman.SCALE_TO_METRES
    return index, delta


def _add_target(obj: bpy.types.Object, target: str, weight: float, basis: np.ndarray) -> None:
    index, delta = _target_offsets(target)
    co = basis.copy()
    if len(index):  # MakeHuman's "average" macro targets are empty on purpose: the base already is that shape
        co[index] += delta
    key = obj.shape_key_add(name=MACRO_PREFIX + makehuman.target_shapekey_name(target), from_mix=False)
    key.data.foreach_set("co", co.ravel())
    key.value = weight


def is_macro_key(name: str) -> bool:
    """A shape key made by `apply_macros`: a macrodetails target, or a breast target (cup size and firmness)."""
    return name.startswith(MACRO_PREFIX + "$md-") or (
        name.startswith(MACRO_PREFIX) and "cup-" in name and "$fi" in name
    )


def apply_macros(obj: bpy.types.Object, values: dict) -> int:
    """Replace the macro shape keys with the stack for `values`; returns how many there are."""
    keys = obj.data.shape_keys
    if keys:
        for key in [k for k in keys.key_blocks if is_macro_key(k.name)]:
            obj.shape_key_remove(key)
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis", from_mix=False)
    basis = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    obj.data.shape_keys.reference_key.data.foreach_get("co", basis)
    basis = basis.reshape(-1, 3)
    config = json.loads(paths.makehuman("targets", "macrodetails", "macro.json").read_text(encoding="utf-8"))
    macro_values = {k: values[k] for k in makehuman.MACROS}
    macro_values["race"] = {race: values[race] for race in makehuman.RACES}
    stack = makehuman.macro_target_stack(config, macro_values)
    for target, weight in stack:
        _add_target(obj, target, weight, basis)
    from ... import character

    character.APPLYING["macros"] = True  # the sliders' own update callbacks stay quiet while their values are written
    try:
        for key, value in values.items():
            setattr(obj.juststage, key, value)
    finally:
        character.APPLYING["macros"] = False
    return len(stack)


def create_human(name: str, values: dict) -> bpy.types.Object:
    obj = _import_base(name)
    _add_vertex_groups(obj)
    _mask_helpers(obj)
    props = obj.juststage
    props.character_id = str(uuid.uuid4())
    props.kind = "HUMAN"
    props.base_version = BASE_VERSION
    apply_macros(obj, values)
    from . import sliders

    sliders.add_items(obj)
    stand_on_floor(obj)
    return obj


#: the lift every base mesh gets: MPFB2's `feet_on_ground` at the default macros (measured 2026-11-04: 0.817743 m;
#: RESEARCH §5: 0.8177), the body MakeHuman's hair styles were groomed on. One for all: Blender's hair attachment
#: measures from the base mesh (its rest position), so each character lifted by its own amount (0-2.5 mm apart,
#: measured) put a groom made on one character that far off another's skin
BASE_LIFT = 0.817743
FLOOR = "JustStage floor"  # the shape key with this shape's own lift on top


def stand_on_floor(obj: bpy.types.Object) -> float:
    """MPFB2's `feet_on_ground` (its default) in two parts: a new character's base mesh, shape keys too, lifted by
    BASE_LIFT; this shape's own few millimetres in the FLOOR shape key, so the shaped body's lowest vertex is at
    z = 0 - the floor every character tool stands on. Again after a shape change (body.set_slider). Returns the whole
    lift."""
    keys = obj.data.shape_keys
    key = keys.key_blocks.get(FLOOR) if keys else None
    if key is None:  # a new character: its base mesh still centred on the origin, as hm08 comes
        obj.data.transform(Matrix.Translation((0.0, 0.0, BASE_LIFT)), shape_keys=True)
        if not obj.data.shape_keys:
            obj.shape_key_add(name="Basis", from_mix=False)
        key = obj.shape_key_add(name=FLOOR, from_mix=False)
    key.value = 0.0
    own = -float(shaped_coords(obj)[: makehuman.BODY_VERTICES, 2].min())
    co = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    obj.data.shape_keys.reference_key.data.foreach_get("co", co)
    co = co.reshape(-1, 3)
    co[:, 2] += own
    key.data.foreach_set("co", co.ravel())
    key.value = 1.0
    return BASE_LIFT + own


def keep_on_floor(obj: bpy.types.Object) -> None:
    """After a shape change: the feet back on the floor - for characters with the floor key (made since 2026-11-04;
    older ones keep the lift in their base mesh, as they were made)."""
    keys = obj.data.shape_keys
    if keys is not None and keys.key_blocks.get(FLOOR) is not None:
        stand_on_floor(obj)


def visible_vertex_count(obj: bpy.types.Object) -> int:
    """Vertices left after the modifiers (the helper mask) — what the user sees."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return len(mesh.vertices)
    finally:
        evaluated.to_mesh_clear()


def set_levels(obj: bpy.types.Object, levels: int, viewport_level: int) -> None:
    """The Multires levels (Catmull-Clark), first in the modifier stack so they sit on the unchanged base."""
    mod = obj.modifiers.get(LEVELS)
    if mod is None:
        mod = obj.modifiers.new(LEVELS, "MULTIRES")
        obj.modifiers.move(obj.modifiers.find(LEVELS), 0)
    with bpy.context.temp_override(object=obj, active_object=obj):
        while mod.total_levels < levels:
            bpy.ops.object.multires_subdivide(modifier=LEVELS, mode="CATMULL_CLARK")
        if mod.total_levels > levels:
            mod.levels = mod.sculpt_levels = levels
            bpy.ops.object.multires_higher_levels_delete(modifier=LEVELS)
    mod.render_levels = levels
    mod.levels = mod.sculpt_levels = viewport_level


def visible_face_count(obj: bpy.types.Object) -> int:
    """Faces left after the modifiers, at the viewport level — what the user sees."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return len(mesh.polygons)
    finally:
        evaluated.to_mesh_clear()


def shaped_coords(obj: bpy.types.Object) -> np.ndarray:
    """Every vertex's position with the shape keys mixed in and no modifiers — the helpers and joint cubes too, which
    the mask hides from view. What MHCLO fits to (MPFB2 fits to the shaped base)."""
    n = len(obj.data.vertices)
    keys = obj.data.shape_keys
    if not keys:
        co = np.empty(n * 3, dtype=np.float64)
        obj.data.vertices.foreach_get("co", co)
        return co.reshape(-1, 3)
    basis = np.empty(n * 3, dtype=np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    basis = basis.reshape(-1, 3).astype(np.float64)
    mix = basis.copy()
    co = np.empty(n * 3, dtype=np.float32)
    for key in keys.key_blocks[1:]:
        if key.mute or key.value == 0.0:
            continue
        key.data.foreach_get("co", co)
        mix += (co.reshape(-1, 3) - basis) * key.value
    return mix
