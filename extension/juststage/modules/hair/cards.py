# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Card hair from free artist packs (Q-HAIR-7, taken 2026-11-10 - `docs/plans/2026-11-08-own-content-proof.md` 19:2x):
the scalp hair's free source that read as real hair at close-up beside HD Aaron (13:1x-13:35, `msahair.png`,
`msalong.png`). MotionStudioArts' hairs made for Character Creator 4 (CC BY 4.0, Sketchfab - ATTRIBUTION.md): ZBrush
FiberMesh cards and a cap (`Sclup`), each with diffuse and opacity maps; fetched by `tools/fetch_data.py` as a manual
source (Sketchfab's download needs a signed-in account).

A pack is fitted to the character's cranium (its cap's top 8 cm to the head's, scale per axis and offset - the trial's
`factors msahair` fit), follows the skin by Surface Deform (Blender's own way for one mesh to ride another's
deformation: https://docs.blender.org/manual/en/5.3/modeling/modifiers/deform/surface_deform.html), and is coloured by
the character's hair colour: the fibre texture kept as detail (divided by its own mean), times Cycles' melanin colour
(`groom.hair_colour`) - a multiply alone could not lighten the short pack's near-black fibres."""

from __future__ import annotations

import bpy
import numpy as np
from mathutils import Matrix

from ... import paths

#: a pack by name: (its folder under data/fetched/msa_hair/ - `fetch_data.py`'s MANUAL_PACKS - the pack zip's own top
#: folder, the OBJ's stem)
PACKS = {
    "msa_short_fuzzy": ("short-fuzzy", "02 Short Hairs Black Fuzzy", "Short Hairs Black Fuzzy"),
    "msa_long_wavy": ("long-wavy", "016 White Long Wavy Hairs", "White Long Wavy Hairs"),
}
PACK_PROP = "juststage_card_pack"  # each card object's pack name (a library file's cards are refitted by it)
CAP_PROP = "juststage_card_cap"  # on the cap (names change when a library file is written: `groom.portable`)
CAP = "Sclup"  # the pack's cap object (the OBJ's group)
FIBRE_STEM = "GoZMesh_Import_Material"  # the fibres' texture stem
TOP_M, SIDE_M = 0.08, 0.12  # the cranium: the top 8 cm, within 12 cm of the head's midline
ROUGHNESS = 0.45  # the trial's (`msahair`)
MOD = "JustStage Surface Deform"
TINT = "JustStage hair colour"  # the RGB node each card material's colour reads


def folder(pack: str):
    sub, inner, _stem = PACKS[pack]
    return paths.FETCHED / "msa_hair" / sub / inner


def _world(obj) -> np.ndarray:
    co = np.empty(len(obj.data.vertices) * 3, np.float32)
    obj.data.vertices.foreach_get("co", co)
    m = np.array(obj.matrix_world)
    return co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]


def _cranium(points: np.ndarray, centre_x: float) -> np.ndarray:
    top = points[:, 2].max()
    return points[(np.abs(points[:, 0] - centre_x) < SIDE_M) & (points[:, 2] > top - TOP_M)]


def _body_points(character) -> np.ndarray:
    dg = bpy.context.evaluated_depsgraph_get()
    ev = character.evaluated_get(dg)
    mesh = ev.to_mesh()
    co = np.empty(len(mesh.vertices) * 3, np.float32)
    mesh.vertices.foreach_get("co", co)
    ev.to_mesh_clear()
    m = np.array(character.matrix_world)
    return co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]


def fit(character, objects: list, cap) -> np.ndarray:
    """Every card object moved so the cap's cranium (its top 8 cm) spans the character's, scaled per axis (the height
    by the breadth's mean - no face on a cap to measure it by); returns the scale."""
    ours = _body_points(character)
    theirs = _world(cap)
    ours_cap = _cranium(ours, float(np.median(ours[ours[:, 2] > ours[:, 2].max() - 0.05, 0])))
    theirs_cap = _cranium(theirs, float(np.median(theirs[:, 0])))
    lo_o, hi_o, lo_t, hi_t = ours_cap.min(0), ours_cap.max(0), theirs_cap.min(0), theirs_cap.max(0)
    scale = (hi_o - lo_o) / np.maximum(hi_t - lo_t, 1e-6)
    scale[2] = float(np.mean(scale[:2]))
    anchor_t = np.array([(lo_t[0] + hi_t[0]) / 2, (lo_t[1] + hi_t[1]) / 2, hi_t[2]])
    anchor_o = np.array([(lo_o[0] + hi_o[0]) / 2, (lo_o[1] + hi_o[1]) / 2, hi_o[2]])
    to_local = np.array(character.matrix_world.inverted())
    for obj in objects:
        w = (_world(obj) - anchor_t) * scale + anchor_o
        obj.parent = character
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = Matrix.Identity(4)
        local = w @ to_local[:3, :3].T + to_local[:3, 3]
        obj.data.vertices.foreach_set("co", local.astype(np.float32).ravel())
        obj.data.update()
    return scale


def _mean_linear(image) -> np.ndarray:
    """The image's mean colour in linear light, from a 64 px copy (Blender gives a colour image's pixels linear)."""
    small = image.copy()
    small.scale(64, 64)
    px = np.empty(64 * 64 * 4, np.float32)
    small.pixels.foreach_get(px)
    bpy.data.images.remove(small)
    rgb = px.reshape(-1, 4)[:, :3]
    return np.maximum(rgb.mean(0), 1e-4)


def _material(name: str, texture_dir, stem: str, ext: str) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED"
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    diffuse = nt.nodes.new("ShaderNodeTexImage")
    diffuse.image = bpy.data.images.load(str(texture_dir / f"{stem}_diffuse.{ext}"), check_existing=True)
    opacity = nt.nodes.new("ShaderNodeTexImage")
    opacity.image = bpy.data.images.load(str(texture_dir / f"{stem}_opacity.{ext}"), check_existing=True)
    opacity.image.colorspace_settings.name = "Non-Color"
    tint = nt.nodes.new("ShaderNodeRGB")
    tint.name = tint.label = TINT
    tint["mean"] = _mean_linear(diffuse.image).tolist()  # the texture's own mean: the colour divides by it
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    nt.links.new(diffuse.outputs["Color"], mix.inputs["A"])
    nt.links.new(tint.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(opacity.outputs["Color"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = ROUGHNESS
    return mat


def set_colour(objects: list, melanin: float, redness: float) -> int:
    """Each card material's colour: Cycles' melanin colour over its texture's own mean; returns how many it set."""
    from .groom import hair_colour

    colour = np.array(hair_colour(melanin, redness))
    n = 0
    for obj in objects:
        for mat in obj.data.materials:
            node = mat.node_tree.nodes.get(TINT) if mat and mat.node_tree else None
            if node is None:
                continue
            node.outputs["Color"].default_value = (*(colour / np.array(node["mean"])).tolist(), 1.0)
            n += 1
        obj["melanin"], obj["redness"] = melanin, redness
    return n


def bind(character, objects: list) -> None:
    """Each card object rides the character's skin (Surface Deform, bound at the fitted rest) - through the body's
    deform cage (`body/cage.py`: one topology at any subdivision level; bound to the body itself the cards flew
    apart at render, where the body's level is higher than the viewport's)."""
    from ..body import cage

    target = cage.get(character)
    bpy.context.view_layer.update()
    for obj in objects:
        mod = obj.modifiers.get(MOD) or obj.modifiers.new(MOD, "SURFACE_DEFORM")
        mod.target = target
        if mod.is_bound:
            with bpy.context.temp_override(object=obj, active_object=obj):
                bpy.ops.object.surfacedeform_bind(modifier=mod.name)  # unbind (the operator toggles)
        with bpy.context.temp_override(object=obj, active_object=obj):
            bpy.ops.object.surfacedeform_bind(modifier=mod.name)


def _tag(character, objects: list, pack: str, part: str = "scalp") -> None:
    for obj in objects:
        if not obj.users_collection:
            for collection in character.users_collection:
                collection.objects.link(obj)
        obj.juststage.part_of = character.juststage.character_id
        obj.juststage.part = part
        obj[PACK_PROP] = pack
        if not obj.name.startswith(f"{character.name}."):
            obj.name = f"{character.name}.{obj.name}"


def make(character, pack: str, melanin: float, redness: float) -> list:
    """The pack on the character: imported, fitted, coloured, bound, tagged as its scalp hair (the old one removed)."""
    from .groom import remove_part

    root = folder(pack)
    stem = PACKS[pack][2]
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=str(root / f"{stem}.obj"), global_scale=0.01, forward_axis="NEGATIVE_Z",
                          up_axis="Y", use_split_groups=True)  # cm, Y up; its `g` groups: the cap and the fibres
    new = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    for obj in [o for o in bpy.data.objects if o not in before and o.type != "MESH"]:
        bpy.data.objects.remove(obj)
    cap = next(o for o in new if o.name.startswith(CAP))
    cap[CAP_PROP] = True
    for obj in new:
        for collection in list(obj.users_collection):
            collection.objects.unlink(obj)
    remove_part(character, "scalp")
    _tag(character, new, pack)
    fit(character, new, cap)
    texture_dir = root / stem
    for obj in new:
        is_cap = obj is cap
        mat = _material(f"JustStage Cards ({obj.name})", texture_dir, CAP if is_cap else FIBRE_STEM,
                        "png" if is_cap else "jpg")
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    set_colour(new, melanin, redness)
    bind(character, new)
    return new


def is_cards(obj) -> bool:
    return obj.type == "MESH" and PACK_PROP in obj


def attach_from_file(character, objects: list) -> object:
    """A library file's cards (fitted to whoever they were saved on) onto this character: refitted by their cap,
    rebound; returns the cap."""
    from .groom import remove_part

    pack = objects[0][PACK_PROP]
    cap = next(o for o in objects if o.get(CAP_PROP))
    remove_part(character, "scalp")
    for obj in objects:
        for mod in list(obj.modifiers):
            if mod.type == "SURFACE_DEFORM":
                obj.modifiers.remove(mod)
        obj.parent = None
    _tag(character, objects, pack)
    fit(character, objects, cap)
    bind(character, objects)
    return cap
