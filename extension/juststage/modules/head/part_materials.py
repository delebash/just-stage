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
    "teeth": ((0.80, 0.75, 0.65), 0.25, 0.2, (0.5, 0.4, 0.3), 1.63, 0.0),
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
    if sss:
        bsdf.subsurface_method = "RANDOM_WALK"
        bsdf.inputs["Subsurface Weight"].default_value = sss
        bsdf.inputs["Subsurface Radius"].default_value = radius
        bsdf.inputs["Subsurface Scale"].default_value = 0.001  # millimetres
    return mat


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
        obj.data.materials.append(_material(region, obj.name))
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
