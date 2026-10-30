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
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.subsurface_method = "RANDOM_WALK_SKIN"
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Subsurface Weight"].default_value = 1.0
    bsdf.inputs["Subsurface Radius"].default_value = radius
    bsdf.inputs["Subsurface Scale"].default_value = MM_TO_M  # the radius is in millimetres
    bsdf.inputs["IOR"].default_value = IOR
    bsdf.inputs["Roughness"].default_value = ROUGHNESS
    bsdf.inputs["Specular IOR Level"].default_value = oiliness  # 0.5 is Blender's standard; the paper's ρs scales it
    return mat
