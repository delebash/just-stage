# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""A groom: one of MakeHuman's CC0 hair-editor styles (`hair/haireditor/hair.blend`, by Tomáš Klecer), attached to the
character the way MPFB2's hair editor attaches it (`apply_hair_operator.py`, `attach_curves_to_basemesh`): a Curves
object whose surface is the body, parented with an identity inverse because the style was groomed on a body standing
at the origin. Its strands are shaped by the Blender hair node groups the style carries — a groom's settings are those
node groups' inputs (character-data-model.md §4). The first of them, Surface Deform (Blender's Deform Curves on
Surface), makes the strands follow the body's shape keys, which needs the body's rest position.
"""

from __future__ import annotations

import bpy
import numpy as np
from mathutils import Matrix

from ... import paths
from .styles import STYLES

PACK = ("hair", "haireditor", "hair.blend")
SURFACE_UV = "UVMap"  # hm08's own UV map, the one the styles' roots are placed by


def hair_material(name: str) -> bpy.types.Material:
    """Principled Hair BSDF (Chiang) coloured by melanin, read per strand from the `melanin` and `redness` curve
    attributes (Blender's melanin parametrisation — character-data-model.md §3, §4)."""
    mat = bpy.data.materials.new(name)
    if mat.node_tree is None:
        mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    for node in list(nodes):
        if node.type == "BSDF_PRINCIPLED":
            nodes.remove(node)
    hair = nodes.new("ShaderNodeBsdfHairPrincipled")
    hair.parametrization = "MELANIN"
    for socket, attribute in (("Melanin", "melanin"), ("Melanin Redness", "redness")):
        node = nodes.new("ShaderNodeAttribute")
        node.attribute_type = "GEOMETRY"
        node.attribute_name = attribute
        links.new(node.outputs["Fac"], hair.inputs[socket])
    output = next(n for n in nodes if n.type == "OUTPUT_MATERIAL")
    links.new(hair.outputs[0], output.inputs["Surface"])
    return mat


def _set_colour(curves: bpy.types.Curves, melanin: float, redness: float) -> None:
    for name, value in (("melanin", melanin), ("redness", redness)):
        attribute = curves.attributes.get(name) or curves.attributes.new(name, "FLOAT", "CURVE")
        attribute.data.foreach_set("value", np.full(len(curves.curves), value, dtype=np.float32))


def _drop_unused(materials: list[bpy.types.Material]) -> None:
    """The style's own materials, once replaced, and the node groups only they used."""
    for mat in materials:
        if mat is None or mat.users:
            continue
        groups = [n.node_tree for n in mat.node_tree.nodes if n.type == "GROUP"] if mat.node_tree else []
        bpy.data.materials.remove(mat)
        for group in groups:
            if group is not None and group.users == 0:
                bpy.data.node_groups.remove(group)


def _point_surface_inputs(groom: bpy.types.Object, character: bpy.types.Object) -> None:
    """A style's empty `Surface` object inputs (Attach Hair Curves to Surface, in `tail_base`) — they named the body it
    was groomed on, which the pack doesn't carry — now name this character, as the Curves surface does. Without it
    `tail_base`'s roots float 5 mm off the skin (median, measured 2026-10-29); with it 0.3 mm."""
    for mod in groom.modifiers:
        if mod.type != "NODES" or mod.node_group is None:
            continue
        for item in mod.node_group.interface.items_tree:
            if (item.item_type, item.in_out, item.socket_type, item.name) == (
                "SOCKET",
                "INPUT",
                "NodeSocketObject",
                "Surface",
            ):
                prop = getattr(mod.properties.inputs, item.identifier)  # Blender 5.x's modifier inputs
                if prop.value is None:
                    prop.value = character


def add_style(character: bpy.types.Object, style: str, melanin: float, redness: float) -> bpy.types.Object:
    from ...core.commands import CommandError

    if SURFACE_UV not in character.data.uv_layers:
        raise CommandError(f"{character.name} has no {SURFACE_UV!r} UV map (hm08's own), which the styles root by")
    character.add_rest_position_attribute = True
    with bpy.data.libraries.load(str(paths.makehuman(*PACK)), link=False) as (src, dst):
        missing = style not in src.objects
        dst.objects = [] if missing else [n for n in (style, f"{style}_brace") if n in src.objects]
    if missing:
        raise CommandError(f"the hair pack has no style {style!r}; run: python tools/fetch_data.py")
    groom = dst.objects[0]
    for obj in dst.objects:  # the style, and the hair tie (`_brace`) one style has
        for collection in character.users_collection:
            collection.objects.link(obj)
        obj.parent = character
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.juststage.part_of = character.juststage.character_id
        obj.name = f"{character.name}.{obj.name}"
    groom.data.surface = character
    _point_surface_inputs(groom, character)
    groom.juststage.part = STYLES[style][0]
    old = list(groom.data.materials)
    groom.data.materials.clear()
    groom.data.materials.append(hair_material(f"JustStage Hair ({groom.name})"))
    _drop_unused(old)
    _set_colour(groom.data, melanin, redness)
    return groom


def evaluated_curve_count(obj: bpy.types.Object) -> int:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    return len(obj.evaluated_get(depsgraph).data.curves)
