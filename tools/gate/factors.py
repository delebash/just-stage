# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""One factor at a time on our character at the gate (AGENTS.md: a gap is diagnosed by changing one factor before it
is fixed). Each factor changes the built character, then the gate's own views render with the tag `_f-<factor>`:

    python tools/dev.py blender -b --python tools/gate/factors.py -- --factors relief0,pores0 --views eye,cheek
        [--engine eevee|cycles] [--out DIR]

Factors (the skin's, `modules/skin/maps.py` nodes):
- `relief0`  - the scan's own relief (the skin's normal map) flat: what the scans' mid-scale geometry gives;
- `pores0`   - the pore tile's depth 0;
- `micro0`   - the microrelief's depth 0;
- `colourpores0` - the colour map's detail finer than 1.5 mm blurred out (the pore band of the scan's colour): rec
  17's "colour and relief pores from one source" - how much of the pore band the colour carries, against the relief's
  pores from Ten24's tile;
- `colourflat` - the colour map at its mean over the skin: what the relief alone gives.

`tools/gate/measure.py` then reads every `{engine}_{view}_ours_f-<factor>.png` beside the baseline."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("parts_gate", HERE / "parts_gate.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

PORE_BAND_MM = 1.5  # the colour's detail finer than this is the pore band (measure.py BANDS_MM)


def _maps():
    return importlib.import_module("bl_ext.system.juststage.modules.skin.maps")


def _skin_trees(built: dict):
    seen = set()
    for slot in built["body"].material_slots:
        mat = slot.material
        if mat and mat.node_tree and mat.name not in seen and _maps().NODE + "gain" in mat.node_tree.nodes:
            seen.add(mat.name)
            yield mat.node_tree


def _depth(built: dict, key: str) -> None:
    for nt in _skin_trees(built):
        nt.nodes[_maps().NODE + f"{key}_depth"].inputs[1].default_value = 0.0


def relief0(built: dict) -> None:
    for nt in _skin_trees(built):
        nt.nodes[_maps().NODE + "normal_map"].inputs["Strength"].default_value = 0.0


def pores0(built: dict) -> None:
    _depth(built, "pore")


def micro0(built: dict) -> None:
    _depth(built, "micro")


def _colour_images(built: dict):
    for nt in _skin_trees(built):
        node = nt.nodes[_maps().NODE + "base_color"]
        yield node.image


def _tile_pixels(image, number: int) -> tuple[np.ndarray, object]:
    """One UDIM tile of a tiled image as an array (via a plain image loaded from the tile's file)."""
    path = Path(bpy.path.abspath(image.filepath_raw.replace("<UDIM>", str(number))))
    tile = bpy.data.images.load(str(path), check_existing=False)
    tile.colorspace_settings.name = image.colorspace_settings.name
    w, h = tile.size
    px = np.empty(w * h * 4, np.float32)
    tile.pixels.foreach_get(px)
    return px.reshape(h, w, 4), tile


def _rewrite_colour(built: dict, change) -> None:
    """Each colour tile changed by `change(rgb, mm_per_px) -> rgb` and the skin pointed at the changed copies."""
    maps = _maps()
    out = Path(bpy.app.tempdir) / "gate_factors"
    out.mkdir(parents=True, exist_ok=True)
    for image in _colour_images(built):
        for tile in image.tiles:
            px, plain = _tile_pixels(image, tile.number)
            mm_per_px = maps.MM_PER_UV.get(tile.number, 724.0) / px.shape[0]  # the tile's mean density
            px[..., :3] = change(px[..., :3], mm_per_px)
            plain.pixels.foreach_set(px.ravel())
            plain.filepath_raw = str(out / f"colour.{tile.number}.png")
            plain.file_format = "PNG"
            plain.save()
            bpy.data.images.remove(plain)
        image.filepath = str(out / "colour.<UDIM>.png")
        image.reload()


def colourpores0(built: dict) -> None:
    def blur(rgb, mm_per_px):  # numpy only: Blender's Python has no scipy
        sigma = PORE_BAND_MM / mm_per_px / 2.0
        return np.stack([pg._blur(rgb[..., c], sigma) for c in range(3)], -1)

    _rewrite_colour(built, blur)


def colourflat(built: dict) -> None:
    def flat(rgb, _mm):
        skin = rgb.sum(-1) > 0.02
        mean = rgb[skin].mean(0) if skin.any() else rgb.reshape(-1, 3).mean(0)
        return np.where(skin[..., None], mean, rgb)

    _rewrite_colour(built, flat)


FACTORS = {f.__name__: f for f in (relief0, pores0, micro0, colourpores0, colourflat)}


if __name__ == "__main__":
    import argparse

    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="factors.py --")
    p.add_argument("--factors", required=True)
    p.add_argument("--views", default="eye,cheek,face")
    p.add_argument("--engine", choices=("eevee", "cycles"), default="eevee")
    p.add_argument("--out", type=Path, default=pg.OUT / "factors")
    a = p.parse_args(args)
    out = a.out.resolve()  # absolute: Blender's render path then can't land anywhere else
    for name in a.factors.split(","):
        pg.render("ours", a.engine, out, a.views.split(","), pg.SIZE, pg.CYCLES_SAMPLES, tag=f"_f-{name}",
                  prepare=FACTORS[name])
        for view in a.views.split(","):
            made = out / f"{a.engine}_{view}_ours_f-{name}.png"
            print("WRITTEN" if made.exists() else "MISSING", made, flush=True)
