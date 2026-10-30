# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The skin's fine detail: a seamless height map made from a generated skin close-up (core/skin_detail.py), packed in
the .blend with where it came from, tiled over the body's UVs at its real size and fed to the skin's Principled BSDF
through Blender's Bump node."""

from __future__ import annotations

import bpy
import numpy as np

from ... import paths
from ...core import skin_detail

#: hm08's UV units per metre of skin — the median over the body's faces, measured 2026-10-29 (10th–90th percentile
#: 0.40–1.10: the tile's real size holds where the UVs are average, smaller where they are denser)
UV_PER_M = 0.57
BUMP_DISTANCE_M = 0.0001  # the height map's full range as 0.1 mm of relief; the command's strength scales it
NODES = ("juststage.detail.coords", "juststage.detail.mapping", "juststage.detail.image", "juststage.detail.bump")
PROMPT = (
    "macro texture photograph of a flat patch of human skin on the inner forearm, the skin fills the entire frame edge "
    "to edge, evenly spaced fine pores and the natural crosshatch of skin lines, flat even diffuse lighting, "
    "photographed straight on, uniform tone, material scan for 3D texturing"
)


def photo_pixels(png: bytes) -> np.ndarray:
    """An RGB array (rows top first) from PNG bytes, read by Blender's own image loader."""
    path = paths.user_dir("cache") / "skin_detail_source.png"
    path.write_bytes(png)
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        w, h = image.size
        px = np.empty(w * h * 4, dtype=np.float32)
        image.pixels.foreach_get(px)
        return px.reshape(h, w, 4)[::-1, :, :3]  # Blender's rows run bottom first
    finally:
        bpy.data.images.remove(image)
        path.unlink(missing_ok=True)


def _height_image(name: str, height: np.ndarray, provenance: dict) -> bpy.types.Image:
    h, w = height.shape
    image = bpy.data.images.get(name)
    if image is not None and tuple(image.size) != (w, h):
        bpy.data.images.remove(image)
        image = None
    if image is None:
        image = bpy.data.images.new(name, w, h, alpha=False, is_data=True)
    image.colorspace_settings.name = "Non-Color"
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = height[::-1, :, None]
    image.pixels.foreach_set(rgba.ravel())
    image.pack()
    for key, value in provenance.items():  # where it came from (character-data-model.md §3.1)
        image[f"juststage_{key}"] = value
    return image


def apply(
    material: bpy.types.Material,
    character_name: str,
    height: np.ndarray,
    size_mm: float,
    strength: float,
    provenance: dict,
) -> bpy.types.Image:
    image = _height_image(f"{character_name} skin detail", height, provenance)
    nodes, links = material.node_tree.nodes, material.node_tree.links
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    coords, mapping, tex, bump = (nodes.get(n) for n in NODES)
    if coords is None:
        coords = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        tex = nodes.new("ShaderNodeTexImage")
        bump = nodes.new("ShaderNodeBump")
        for node, name, x in zip((coords, mapping, tex, bump), NODES, (-1100, -900, -650, -350), strict=True):
            node.name, node.label, node.location = name, name.rsplit(".", 1)[1].title(), (x, -500)
        links.new(coords.outputs["UV"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        links.new(tex.outputs["Color"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    tex.image = image
    tex.interpolation = "Cubic"
    tiles = 1.0 / (UV_PER_M * size_mm / 1000.0)
    mapping.inputs["Scale"].default_value = (tiles, tiles, 1.0)
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = BUMP_DISTANCE_M
    return image


def height_from_png(png: bytes) -> np.ndarray:
    return skin_detail.height_map(photo_pixels(png))
