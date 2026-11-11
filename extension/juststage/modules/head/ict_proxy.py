# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""ICT-FaceKit's head (MIT) as a proxy over the character's hm08 head (Q-BASE-4, mine 2026-11-10 -
docs/plans/2026-11-10-ict-head.md §0): the eye's lid and the ear's concha need topology hm08 doesn't have; on ICT's
head the eye read NEAR EQUAL to HD Aaron's and the ear CLOSE. MakeHuman's own way to wear another topology - a proxy
placed once on the base mesh (`tools/make_ict_proxy.py`) that then follows every target:

- the head's mesh from `data/generated/ict/head_proxy.npz`, parented to the body;
- our UDIM UVs carried onto it by Blender's Data Transfer (nearest face, interpolated), so every skin fits it as is;
- the character's skin material; the body's faces under it in a hidden slot (transparent, its shadow too) - not
  deleted: every groom is bound to the body's surface;
- Surface Deform bound - through the body's deform cage (one topology at any subdivision level) - with the body's
  shape keys muted (hm08's raw basis, where the proxy was placed), then the keys restored - the macros, details,
  mixer, floor lift and expressions carry it
  (docs.blender.org/manual/en/5.3/modeling/modifiers/deform/surface_deform.html)."""

from __future__ import annotations

import bpy
import numpy as np

from ... import paths

NAME = "JustStage ICT head"
PART = "ict_head"  # the proxy's part tag (one per character)
DATA = ("ict", "head_proxy.npz")
TOOL = "python tools/dev.py blender -b --python tools/make_ict_proxy.py -- export, then make_ict_proxy.py place"
HIDE_MM = 4.0  # the body's faces with every vertex this near the proxy go into the hidden slot
HIDDEN = "JustStage hidden under the ICT head"
MOD = "JustStage Surface Deform"


def _data() -> dict:
    path = paths.generated(*DATA, tool=TOOL)
    with np.load(path) as d:
        return {k: d[k] for k in d.files}


def _mesh(data: dict) -> bpy.types.Mesh:
    counts, flat = data["counts"], data["flat"]
    starts = np.r_[0, np.cumsum(counts)[:-1]]
    polys = [flat[s:s + c].tolist() for s, c in zip(starts, counts, strict=True)]
    me = bpy.data.meshes.new(NAME)
    me.from_pydata(data["verts"].tolist(), [], polys)
    me.validate()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    return me


def _uv_missing(head: bpy.types.Object) -> bool:
    from ..skin import maps

    return maps.UV not in head.data.uv_layers


def _uvs_from_body(head: bpy.types.Object, body: bpy.types.Object) -> None:
    """Our UDIM layer onto the head by Blender's Data Transfer (nearest face, interpolated), applied. `body`: the
    body's cage at the basis (the caller mutes the keys)."""
    from ..skin import maps

    head.data.uv_layers.new(name=maps.UV)
    active = body.data.uv_layers.active
    body.data.uv_layers.active = body.data.uv_layers[maps.UV]
    mod = head.modifiers.new("uv from the body", "DATA_TRANSFER")
    mod.object = body
    mod.use_loop_data = True
    mod.data_types_loops = {"UV"}
    mod.loop_mapping = "POLYINTERP_NEAREST"
    mod.layers_uv_select_src = maps.UV
    dst = [i.identifier for i in mod.bl_rna.properties["layers_uv_select_dst"].enum_items]
    mod.layers_uv_select_dst = "NAME" if "NAME" in dst else dst[0]
    with bpy.context.temp_override(object=head, active_object=head):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    body.data.uv_layers.active = active


def _hidden_material() -> bpy.types.Material:
    mat = bpy.data.materials.get(HIDDEN)
    if mat is None:
        mat = bpy.data.materials.new(HIDDEN)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(nt.nodes.new("ShaderNodeBsdfTransparent").outputs["BSDF"], out.inputs["Surface"])
        if hasattr(mat, "use_transparent_shadow"):
            mat.use_transparent_shadow = True
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "DITHERED"
    return mat


def _hide_covered(body: bpy.types.Object, verts: np.ndarray) -> int:
    """The body's faces whose every vertex lies within HIDE_MM of the proxy (basis space) -> the hidden slot."""
    from mathutils import kdtree

    co = np.empty(len(body.data.vertices) * 3, np.float32)
    keys = body.data.shape_keys
    (keys.reference_key.data if keys else body.data.vertices).foreach_get("co", co)
    co = co.reshape(-1, 3)
    tree = kdtree.KDTree(len(verts))
    for i, p in enumerate(verts):
        tree.insert(p.tolist(), i)
    tree.balance()
    near = np.array([tree.find(p.tolist())[2] < HIDE_MM / 1000.0 for p in co])
    mats = body.data.materials
    if HIDDEN not in [m.name for m in mats if m]:
        mats.append(_hidden_material())
    slot = [m.name if m else "" for m in mats].index(HIDDEN)
    n = 0
    for poly in body.data.polygons:
        if near[list(poly.vertices)].all():
            poly.material_index = slot
            n += 1
    return n


def _bind_at_basis(head: bpy.types.Object, body: bpy.types.Object) -> None:
    """Our UDIM UVs carried onto the head, then Surface Deform to the body's deform cage (`body/cage.py`: one topology
    at any subdivision level - bound to the body itself a rider flies apart at render, 2026-11-10) - both with every
    shape key muted: hm08's basis, where the proxy was placed. (The UVs carried from the shaped body put the nose bridge
    and the ear on the wrong faces, 2026-11-10 23:1x.)"""
    from ..body import cage

    target = cage.get(body)
    keys = body.data.shape_keys
    muted = [(k, k.mute) for k in keys.key_blocks] if keys else []
    for k, _ in muted:
        k.mute = True
    try:
        bpy.context.view_layer.update()
        if _uv_missing(head):
            _uvs_from_body(head, target)  # from the cage at the basis: the body's own faces, no subdivision
        mod = head.modifiers.get(MOD) or head.modifiers.new(MOD, "SURFACE_DEFORM")
        mod.target = target
        with bpy.context.temp_override(object=head, active_object=head):
            if mod.is_bound:
                bpy.ops.object.surfacedeform_bind(modifier=mod.name)  # the operator toggles: unbind first
            bpy.ops.object.surfacedeform_bind(modifier=mod.name)
        bpy.context.view_layer.update()  # the operator only asks: the bind is made at this evaluation - at the basis
    finally:
        for k, was in muted:
            k.mute = was
        bpy.context.view_layer.update()
    if not mod.is_bound:  # Surface Deform fails silently (an invalid target: the cage's docstring)
        raise RuntimeError(f"the ICT head did not bind to {target.name}")


def add(character: bpy.types.Object) -> bpy.types.Object:
    """The ICT head on the character (its old one replaced)."""
    remove(character)
    data = _data()
    head = bpy.data.objects.new(f"{character.name}.{NAME}", _mesh(data))
    for collection in character.users_collection:
        collection.objects.link(head)
    head.parent = character
    head.juststage.part_of = character.juststage.character_id
    head.juststage.part = PART
    head.data.materials.append(character.juststage.skin_material)
    hidden = _hide_covered(character, data["verts"])
    _bind_at_basis(head, character)  # our UVs carried and the bind made where the proxy was placed
    print(f"ICT HEAD on {character.name}: {len(head.data.vertices)} vertices, {hidden} body faces hidden", flush=True)
    return head


def of(character: bpy.types.Object) -> bpy.types.Object | None:
    cid = character.juststage.character_id
    return next((o for o in bpy.data.objects if o.juststage.part_of == cid and o.juststage.part == PART), None)


def remove(character: bpy.types.Object) -> None:
    old = of(character)
    if old is not None:
        mesh = old.data
        bpy.data.objects.remove(old)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for poly in character.data.polygons:  # the hidden faces back on the skin's slot
        if poly.material_index and character.data.materials[poly.material_index] and \
                character.data.materials[poly.material_index].name == HIDDEN:
            poly.material_index = 0
