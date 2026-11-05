# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The skin material: Blender's Principled BSDF with Random Walk (Skin) subsurface (character-data-model.md §3.2), its
colour and scattering depths from the chromophore model calibrated on NIST's measured skin (core/skin_optics.py)."""

from __future__ import annotations

import math

import bpy

from ... import paths
from ...core import skin_optics

NAME = "JustStage Skin"
IOR = 1.4  # Donner & Jensen §3.5
#: their Beckmann RMS slope (σ = 0.35) as Blender's roughness, whose GGX α is roughness²
ROUGHNESS = math.sqrt(0.35)
MM_TO_M = 0.001
#: the live view's scattering against the film's: EEVEE's on our skin is shorter than Cycles' Random Walk - its lit
#: pores came out 2-3% sharper and its shadowed ones 21-28% harsher; x2 brings the lit to the film's (0.97-1.00) and the
#: shadowed to 1.15-1.16, above x2 the lit pores blur past Cycles' (the realism doc §6a, "Skin scattering alone")
EEVEE_SCATTER = 2.0
#: the live view's own copy of the skin's BSDF and its output (EEVEE reads an EEVEE-target output over an All one -
#: Blender's Material Output "Target"; the eyes' and the hair's live-view stand-ins are built the same way)
LIVE_BSDF, LIVE_OUTPUT = "juststage.live.bsdf", "juststage.live.output"


def principled(mat: bpy.types.Material) -> bpy.types.ShaderNodeBsdfPrincipled:
    """The skin's BSDF - the film's (Cycles, the export); every map and value goes on it, `sync_live` copies them."""
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED" and n.name != LIVE_BSDF)


def sync_live(mat: bpy.types.Material) -> None:
    """The live view's BSDF made the film's again - its every input from the same source or value - with its
    scattering x EEVEE_SCATTER, on an output only EEVEE reads. Run after anything changes the film's BSDF."""
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    film = principled(mat)
    film_out = next(lk.to_node for lk in film.outputs["BSDF"].links if lk.to_node.type == "OUTPUT_MATERIAL")
    film_out.target = "ALL"
    film_out.is_active_output = True
    live = nodes.get(LIVE_BSDF) or nodes.new("ShaderNodeBsdfPrincipled")
    live.name = live.label = LIVE_BSDF
    live.location = (film.location.x, film.location.y - 750)
    live.subsurface_method, live.distribution = film.subsurface_method, film.distribution
    live_out = nodes.get(LIVE_OUTPUT) or nodes.new("ShaderNodeOutputMaterial")
    live_out.name = live_out.label = LIVE_OUTPUT
    live_out.target = "EEVEE"
    live_out.location = (film_out.location.x, film_out.location.y - 750)
    for source, twin in ((film, live), (film_out, live_out)):
        for socket, mirror in zip(source.inputs, twin.inputs, strict=True):  # the same node type: the same sockets
            for link in list(mirror.links):
                links.remove(link)
            if socket.is_linked:
                if socket.links[0].from_node != film:
                    links.new(socket.links[0].from_socket, mirror)
            elif hasattr(socket, "default_value"):
                mirror.default_value = socket.default_value
    links.new(live.outputs["BSDF"], live_out.inputs["Surface"])
    live.inputs["Subsurface Scale"].default_value = film.inputs["Subsurface Scale"].default_value * EEVEE_SCATTER
    film_out.is_active_output = True


def apply(obj: bpy.types.Object, skin: skin_optics.Skin, oiliness: float) -> bpy.types.Material:
    tables = skin_optics.load_tables(paths.FETCHED / "optics")
    rgb = skin.linear_rgb(tables)
    radius = skin.subsurface_radius_mm(tables)
    mat = obj.juststage.skin_material
    if mat is None:  # each character has its own, held by pointer (names get ".001" suffixes)
        mat = bpy.data.materials.new(NAME)
        if mat.node_tree is None:  # Blender 5.x makes node materials already; `use_nodes` goes in 6.0
            mat.use_nodes = True
        obj.data.materials.append(mat)
        obj.juststage.skin_material = mat
    bsdf = principled(mat)
    bsdf.subsurface_method = "RANDOM_WALK_SKIN"
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Subsurface Weight"].default_value = 1.0
    bsdf.inputs["Subsurface Radius"].default_value = radius
    bsdf.inputs["Subsurface Scale"].default_value = MM_TO_M  # the radius is in millimetres
    bsdf.inputs["IOR"].default_value = IOR
    bsdf.inputs["Roughness"].default_value = ROUGHNESS
    bsdf.inputs["Specular IOR Level"].default_value = oiliness  # 0.5 is Blender's standard; the paper's ρs scales it
    # EEVEE (the live view) has no Random Walk: its scattering reads the thickness, refined from the shadow maps so
    # ears and nostrils glow (manual render/eevee/material_settings; Cycles ignores both settings)
    mat.thickness_mode = "SPHERE"
    mat.use_thickness_from_shadow = True
    record = mat.juststage  # the material says what it was built from: a skin preset in the library carries it
    record.melanin, record.eumelanin, record.blood = skin.melanin, skin.eumelanin, skin.blood
    record.oiliness, record.is_skin = oiliness, True
    if record.has_maps:  # a mapped skin (maps.py): its colour map recoloured to this tone
        from . import maps

        maps.set_gain(mat, rgb)
    sync_live(mat)
    return mat
