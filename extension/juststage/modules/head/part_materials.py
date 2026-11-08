# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The head parts' materials, one per region GNM marks (character-data-model.md §3.2: Principled BSDF throughout).

Measured constants: the cornea's refractive index 1.376 and enamel's 1.63 (ocular and dental optics' standard values).
The colours, roughness and scattering depths below are starting values for the quality gate to judge (R3), not
measurements; the eye and mouth generators (R5) replace the colours with textures.
"""

from __future__ import annotations

import bpy
import numpy as np

# region → (base colour, linear Rec.709), roughness, subsurface weight, subsurface radius (mm), IOR, transmission
REGIONS = {
    "cornea": ((1.0, 1.0, 1.0), 0.0, 0.0, (0.0, 0.0, 0.0), 1.376, 1.0),
    "sclera": ((0.80, 0.76, 0.71), 0.30, 0.3, (1.0, 0.6, 0.4), 1.40, 0.0),
    "iris": ((0.12, 0.06, 0.03), 0.40, 0.0, (0.0, 0.0, 0.0), 1.40, 0.0),
    "pupil": ((0.005, 0.005, 0.005), 0.30, 0.0, (0.0, 0.0, 0.0), 1.40, 0.0),
    # the enamel: HD Aaron's texture median over his enamel faces (linear) upper (0.43, 0.35, 0.30), lower (0.60, 0.48,
    # 0.42) - ours between them read ivory as his do (2026-11-08, `factors teethcolour`; (0.80, 0.75, 0.65) read white)
    "teeth": ((0.52, 0.42, 0.36), 0.25, 0.2, (0.5, 0.4, 0.3), 1.63, 0.0),
    "gums": ((0.55, 0.15, 0.15), 0.35, 1.0, (1.0, 0.3, 0.2), 1.40, 0.0),
    "tongue": ((0.50, 0.12, 0.12), 0.50, 1.0, (1.0, 0.3, 0.2), 1.40, 0.0),
}
# a part's faces: the first region whose GNM group holds every corner of the face wins
PART_REGIONS = {
    "eyeLeft": [("cornea", "eye_exteriors"), ("pupil", "pupils"), ("iris", "irises"), ("sclera", "scleras")],
    "eyeRight": [("cornea", "eye_exteriors"), ("pupil", "pupils"), ("iris", "irises"), ("sclera", "scleras")],
    "teeth": [("tongue", "tongue"), ("gums", "gums"), ("teeth", "teeth")],
}


def _material(region: str, owner: str) -> bpy.types.Material:
    colour, roughness, sss, radius, ior, transmission = REGIONS[region]
    mat = bpy.data.materials.new(f"JustStage {region.title()} ({owner})")
    if mat.node_tree is None:
        mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*colour, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["IOR"].default_value = ior
    bsdf.inputs["Transmission Weight"].default_value = transmission
    if transmission:
        _eevee_clear(mat, ior, roughness)
    if sss:
        bsdf.subsurface_method = "RANDOM_WALK"
        bsdf.inputs["Subsurface Weight"].default_value = sss
        bsdf.inputs["Subsurface Radius"].default_value = radius
        bsdf.inputs["Subsurface Scale"].default_value = 0.001  # millimetres
    return mat


#: the EEVEE cornea's gloss: a little softer than the glass's 0 so its highlight has a body at viewing distance
CLEAR_ROUGHNESS = 0.02


def _eevee_clear(mat: bpy.types.Material, ior: float, roughness: float) -> None:
    """A clear part (the cornea) for EEVEE: what's behind seen through without refraction, a gloss on top by Fresnel
    at its IOR, blended - on an output only EEVEE reads (as the hair's stand-in: the Material Output's Target).
    EEVEE's refraction is traced in screen space ("See Raytracing limitations", manual render/eevee): in a close-up it
    painted the lid and the light as blotches on the iris (2026-11-04). Real-time engines draw the cornea this way
    and fake its lens in the iris (MetaHuman's eye shader); Cycles and the USD export keep the glass on the All
    output."""
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    fresnel = nodes.new("ShaderNodeFresnel")
    fresnel.inputs["IOR"].default_value = ior
    see_through = nodes.new("ShaderNodeBsdfTransparent")
    gloss = nodes.new("ShaderNodeBsdfGlossy")
    gloss.inputs["Roughness"].default_value = max(roughness, CLEAR_ROUGHNESS)
    mix = nodes.new("ShaderNodeMixShader")
    links.new(fresnel.outputs["Fac"], mix.inputs["Fac"])
    links.new(see_through.outputs["BSDF"], mix.inputs[1])
    links.new(gloss.outputs["BSDF"], mix.inputs[2])
    output = nodes.new("ShaderNodeOutputMaterial")
    output.target = "EEVEE"
    links.new(mix.outputs["Shader"], output.inputs["Surface"])
    main = next(n for n in nodes if n.type == "OUTPUT_MATERIAL" and n is not output)
    main.target = "ALL"
    main.is_active_output = True
    mat.surface_render_method = "BLENDED"  # EEVEE's own setting; Cycles ignores it
    mat.use_raytrace_refraction = False


#: the teeth and gums as the MIO intraoral photo shows them (CC BY 4.0; rec 13: "enamel translucency and gum stippling
#: calibrated on the MIO intraoral photos"): enamel yellower at the gum line and greyer-bluer, more translucent at the
#: biting edge, by its ratios to the crown's middle (sampled 2026-11-06: cervical x(1.04, 1.00, 0.93), incisal x(0.85,
#: 0.87, 1.04)); faint mottling; wet (a thin coat: MetaHuman's saliva film); the gums stippled and wet. CC5 gives its
#: teeth colour and normal maps - ours shade the same features from each tooth's height above the gum line
TOOTH_T = "js_tooth_t"  # 0 at the gum line, 1 at the biting edge (per vertex: its distance to the nearest gum)
TOOTH_RATIOS = ((0.0, (1.04, 1.00, 0.93)), (0.45, (1.0, 1.0, 1.0)), (1.0, (0.85, 0.87, 1.04)))
TOOTH_MOTTLE, WET_COAT, WET_ROUGHNESS = 0.05, 0.5, 0.08
GUM_STIPPLE = 0.00008  # m: the stippling's bump


def tooth_heights(obj: bpy.types.Object, groups: dict[str, list[int]]) -> None:
    """Each tooth vertex's height above the gum line (TOOTH_T), from its distance to the nearest gum vertex over the
    teeth's longest such distance."""
    from mathutils import Vector
    from mathutils.kdtree import KDTree

    co = np.array([v.co for v in obj.data.vertices])
    gums = groups.get("gums", [])
    t = np.zeros(len(co), np.float32)
    if gums:
        tree = KDTree(len(gums))
        for i in gums:
            tree.insert(Vector(co[i]), i)
        tree.balance()
        teeth = np.array(groups["teeth"])
        d = np.array([tree.find(Vector(co[i]))[2] for i in teeth])
        t[teeth] = np.clip(d / max(float(np.quantile(d, 0.98)), 1e-9), 0.0, 1.0)
    attr = obj.data.attributes.get(TOOTH_T) or obj.data.attributes.new(TOOTH_T, "FLOAT", "POINT")
    attr.data.foreach_set("value", t)


def _teeth_shading(mat: bpy.types.Material) -> None:
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    base = tuple(bsdf.inputs["Base Color"].default_value)[:3]
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = TOOTH_T
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    while len(els) < len(TOOTH_RATIOS):
        els.new(0.5)
    for el, (pos, ratio) in zip(els, TOOTH_RATIOS, strict=True):
        el.position = pos
        el.color = (*(b * r for b, r in zip(base, ratio, strict=True)), 1.0)
    nt.links.new(attr.outputs["Fac"], ramp.inputs["Fac"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 400.0  # ~2.5 mm spots on the tooth
    mottle = nt.nodes.new("ShaderNodeMapRange")
    mottle.inputs["To Min"].default_value, mottle.inputs["To Max"].default_value = 1 - TOOTH_MOTTLE, 1 + TOOTH_MOTTLE
    nt.links.new(noise.outputs["Fac"], mottle.inputs["Value"])
    mul = nt.nodes.new("ShaderNodeVectorMath")
    mul.operation = "SCALE"
    nt.links.new(ramp.outputs["Color"], mul.inputs[0])
    nt.links.new(mottle.outputs["Result"], mul.inputs["Scale"])
    nt.links.new(mul.outputs["Vector"], bsdf.inputs["Base Color"])
    bsdf.inputs["Coat Weight"].default_value = WET_COAT
    bsdf.inputs["Coat Roughness"].default_value = WET_ROUGHNESS


def _gum_shading(mat: bpy.types.Material) -> None:
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3000.0  # fine stippling
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Distance"].default_value = GUM_STIPPLE
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Coat Weight"].default_value = WET_COAT
    bsdf.inputs["Coat Roughness"].default_value = WET_ROUGHNESS


def assign(obj: bpy.types.Object, part: str, groups: dict[str, list[int]]) -> dict[str, int]:
    """Give each face of a part the material of its region; returns faces per region."""
    regions = PART_REGIONS[part]
    member = {g: np.zeros(len(obj.data.vertices), dtype=bool) for _, g in regions}
    for _, g in regions:
        member[g][groups[g]] = True
    obj.data.materials.clear()
    slots = {}
    for region, _ in regions:
        slots[region] = len(obj.data.materials)
        mat = _material(region, obj.name)
        if region == "teeth":
            _teeth_shading(mat)
        elif region in ("gums", "tongue"):
            _gum_shading(mat)  # wet, stippled (the tongue's papillae read the same at the gate's distance)
        obj.data.materials.append(mat)
    if part == "teeth":
        tooth_heights(obj, groups)
    counts = dict.fromkeys(slots, 0)
    fallback = regions[-1][0]
    indices = []
    for poly in obj.data.polygons:
        corners = list(poly.vertices)
        region = next((r for r, g in regions if member[g][corners].all()), fallback)
        indices.append(slots[region])
        counts[region] += 1
    obj.data.polygons.foreach_set("material_index", indices)
    return counts
