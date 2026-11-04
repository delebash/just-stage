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

import math

import bpy
import numpy as np
from mathutils import Matrix

from ... import paths
from .styles import STYLES

PACK = ("hair", "haireditor", "hair.blend")
SURFACE_UV = "UVMap"  # hm08's own UV map, the one the styles' roots are placed by


#: Cycles' melanin colours (`intern/cycles/kernel/closure/bsdf_util.h`, RESEARCH §1)
EUMELANIN = (0.506, 0.841, 1.653)
PHEOMELANIN = (0.343, 0.733, 1.924)


def _roughness_scale(beta: float) -> float:
    """Cycles' `bsdf_principled_hair_albedo_roughness_scale`."""
    return (((((0.245 * beta) + 5.574) * beta - 10.73) * beta + 2.532) * beta - 0.215) * beta + 5.969


def hair_colour(melanin: float, redness: float, roughness: float = 0.3) -> tuple[float, float, float]:
    """The colour Cycles' Principled Hair gives a strand of this melanin: its absorption σ from the two pigments, and
    Cycles' own colour-to-σ mapping, σ = (ln colour / s(roughness))², turned round (0.3 is its radial roughness)."""
    m = -math.log(max(1.0 - melanin, 1e-4))
    s = _roughness_scale(roughness)
    sigma = [m * (1.0 - redness) * e + m * redness * p for e, p in zip(EUMELANIN, PHEOMELANIN, strict=True)]
    return tuple(math.exp(-math.sqrt(x) * s) for x in sigma)


def _eevee_stand_in(nodes, links, melanin, redness, roughness: float):
    """EEVEE has no hair shader ("Principled Hair BSDF — Not supported", manual render/eevee/limitations): a Principled
    BSDF in `hair_colour`'s colour, per strand, on an output only EEVEE reads - the Material Output's Target (Blender
    prefers the exact target over All); Cycles and the USD export keep Principled Hair on the All output."""

    def op(operation, a, b=None, c=None):
        node = nodes.new("ShaderNodeMath")
        node.operation = operation
        for i, value in enumerate((a, b, c)):
            if value is None:
                continue
            if isinstance(value, float):
                node.inputs[i].default_value = value
            else:
                links.new(value, node.inputs[i])
        return node.outputs[0]

    m = op("MULTIPLY", op("LOGARITHM", op("MAXIMUM", op("SUBTRACT", 1.0, melanin), 1e-4), math.e), -1.0)
    eu, pheo = op("MULTIPLY", m, op("SUBTRACT", 1.0, redness)), op("MULTIPLY", m, redness)
    s = _roughness_scale(roughness)
    colour = nodes.new("ShaderNodeCombineColor")
    for channel, e, p in zip(("Red", "Green", "Blue"), EUMELANIN, PHEOMELANIN, strict=True):
        sigma = op("MULTIPLY_ADD", pheo, p, op("MULTIPLY", eu, e))
        links.new(op("EXPONENT", op("MULTIPLY", op("SQRT", sigma), -s)), colour.inputs[channel])
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.4
    links.new(colour.outputs["Color"], bsdf.inputs["Base Color"])
    output = nodes.new("ShaderNodeOutputMaterial")
    output.target = "EEVEE"
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])


def hair_material(name: str) -> bpy.types.Material:
    """Principled Hair BSDF (Chiang) coloured by melanin, read per strand from the `melanin` and `redness` curve
    attributes (Blender's melanin parametrisation — character-data-model.md §3, §4), and its EEVEE stand-in."""
    mat = bpy.data.materials.new(name)
    if mat.node_tree is None:
        mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    for node in list(nodes):
        if node.type == "BSDF_PRINCIPLED":
            nodes.remove(node)
    hair = nodes.new("ShaderNodeBsdfHairPrincipled")
    hair.parametrization = "MELANIN"
    read = {}
    for socket, attribute in (("Melanin", "melanin"), ("Melanin Redness", "redness")):
        node = nodes.new("ShaderNodeAttribute")
        node.attribute_type = "GEOMETRY"
        node.attribute_name = attribute
        links.new(node.outputs["Fac"], hair.inputs[socket])
        read[attribute] = node.outputs["Fac"]
    output = next(n for n in nodes if n.type == "OUTPUT_MATERIAL")
    output.target = "ALL"
    links.new(hair.outputs[0], output.inputs["Surface"])
    _eevee_stand_in(nodes, links, read["melanin"], read["redness"], hair.inputs["Radial Roughness"].default_value)
    output.is_active_output = True
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
