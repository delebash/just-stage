# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The nail bed as detail (build queue item 7; the plan's §5 "Nail shape"): hm08 has no nail outline - 187 of the nail
tile's 245 faces straddle MPFB2's mask (RESEARCH §14.5) - so the plate's shape follows the nail shader's own plate
(`maps._nail_layer`: past the curved cuticle, inside the rounded sides) as a height map in the nail tile's UV,
laid on by Blender's Displace modifier after the levels, on the tile's vertices only: the plate domed across, a
groove where it meets the skin, the fold's skin raised beside it, all faded out at the tile's island edges so no seam
opens. The approved design's route for nail beds ("sculpted shape and detail, not topology"). The amounts are the
gate's (`factors naildisp`, 2026-11-08, sheet `scratchpad/sheet_D15_naildisp.png`: at 1.0 / 0.6 / 0.4 mm it read most
like HD Aaron's plate set into the finger)."""

from __future__ import annotations

import bpy
import numpy as np

DOME_MM, GROOVE_MM, LIP_MM = 1.0, 0.6, 0.4
MODIFIER = "JustStage nail bed"
GROUP = "JustStage nail tile"
IMAGE = "JustStage nail bed height"
FADE_PX = 6  # the height fades to 0 over this many texels in from a tile island's edge (~0.5 mm)
LIP_BLUR_PX = 6.0  # how far the fold's raised skin reaches out from the plate (Gaussian sigma, texels)


def _blur(a: np.ndarray, sigma: float) -> np.ndarray:
    """A Gaussian blur in numpy (separable, edges clamped) - Blender's Python has no OpenCV."""
    r = int(3 * sigma)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    pad = np.pad(a, r, mode="edge")
    rows = np.apply_along_axis(lambda x: np.convolve(x, k, mode="valid"), 1, pad)
    return np.apply_along_axis(lambda x: np.convolve(x, k, mode="valid"), 0, rows)


def _inset(mask: np.ndarray, most: int) -> np.ndarray:
    """Each pixel's distance in from the mask's edge, in whole pixels up to `most` (repeated 4-neighbour erosion)."""
    dist = np.zeros(mask.shape, np.float32)
    cur = mask.copy()
    for step in range(1, most + 1):
        dist[cur] = step
        nxt = cur.copy()
        nxt[1:, :] &= cur[:-1, :]
        nxt[:-1, :] &= cur[1:, :]
        nxt[:, 1:] &= cur[:, :-1]
        nxt[:, :-1] &= cur[:, 1:]
        cur = nxt
    return dist


def height_mm(dome_mm: float = DOME_MM, groove_mm: float = GROOVE_MM, lip_mm: float = LIP_MM) -> np.ndarray:
    """The nail tile's height map in mm (the coordinates map's size, Blender's bottom-up rows)."""
    from . import maps

    img = maps.nail_coords()
    w, h = img.size
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    along, across, inside = px[..., 0], px[..., 1] * 2.0 - 1.0, px[..., 3] > 0.5
    soft = 1.0 / maps.NAIL_EDGE_SOFT
    cut = maps.NAIL_CUTICLE + maps.NAIL_CUTICLE_CURVE * across * across
    plate = np.clip((along - cut) * soft, 0, 1) * np.clip((maps.NAIL_SIDE - np.abs(across)) * soft, 0, 1) * inside
    band = 4.0 * plate * (1.0 - plate)  # 1 on the plate's edge
    near = _blur(plate.astype(np.float32), LIP_BLUR_PX) * (1.0 - plate) * inside
    height = dome_mm * plate * (1.0 - np.clip(across * across, 0, 1)) - groove_mm * band
    height += lip_mm * np.clip(near * 3, 0, 1)
    return height * np.clip(_inset(inside, FADE_PX) / FADE_PX, 0.0, 1.0)


def _image(height: np.ndarray, name: str) -> bpy.types.Image:
    h, w = height.shape
    image = bpy.data.images.get(name) or bpy.data.images.new(name, w, h, float_buffer=True, alpha=False)
    image.colorspace_settings.name = "Non-Color"
    metres = (height / 1000.0).astype(np.float32)
    image.pixels.foreach_set(np.dstack([metres] * 3 + [np.ones_like(metres)]).ravel())
    image.pack()  # saved with the file: it is made, not loaded
    return image


def add(character: bpy.types.Object, dome_mm: float = DOME_MM, groove_mm: float = GROOVE_MM,
        lip_mm: float = LIP_MM, name: str = MODIFIER) -> bpy.types.Modifier:  # fmt: skip
    """The nail bed on the character: its nail tile's vertices displaced along their normals by the height map, after
    the levels (on the subdivided mesh). Again on a character that has it (replaced)."""
    from ..body import build
    from . import maps

    me = character.data
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[maps.UV].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    tile = sorted({v for p in me.polygons if maps.NAIL_TILE_INDEX <= uv[list(p.loop_indices), 0].mean()
                   < maps.NAIL_TILE_INDEX + 1 for v in p.vertices})  # fmt: skip
    vg = character.vertex_groups.get(GROUP) or character.vertex_groups.new(name=GROUP)
    vg.add(tile, 1.0, "REPLACE")
    image = _image(height_mm(dome_mm, groove_mm, lip_mm), IMAGE if name == MODIFIER else f"{IMAGE} ({name})")
    tex = bpy.data.textures.get(image.name) or bpy.data.textures.new(image.name, "IMAGE")
    tex.image, tex.extension, tex.use_interpolation = image, "REPEAT", True  # the tile's UVs run 4..5: repeated
    mod = character.modifiers.get(name) or character.modifiers.new(name, "DISPLACE")
    mod.texture, mod.texture_coords, mod.uv_layer = tex, "UV", maps.UV
    mod.vertex_group, mod.direction, mod.mid_level, mod.strength = vg.name, "NORMAL", 0.0, 1.0
    levels = character.modifiers.find(build.LEVELS)  # -1 without levels: then first
    character.modifiers.move(character.modifiers.find(name), max(levels + 1, 0) if levels < 0 or
                             character.modifiers.find(name) > levels else levels)  # fmt: skip
    return mod
