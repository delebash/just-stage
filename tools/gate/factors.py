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
- `colourflat` - the colour map at its mean over the skin: what the relief alone gives;
- a trial setting `pores*1.15+micro*1.35+relief*2` - each layer's depth scaled everywhere (names keep the `*` and `+`).

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


def _colour_nodes(built: dict):
    for nt in _skin_trees(built):
        yield nt.nodes[_maps().NODE + "base_color"]


def _tile_pixels(image, number: int) -> np.ndarray:
    """One UDIM tile of a tiled image as an array (its own buffer, so a packed image works too)."""
    tile = image.tiles.get(number)
    image.tiles.active = tile
    w, h = image.size
    px = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(px)
    return px.reshape(h, w, 4)


def _rewrite_colour(built: dict, change) -> None:
    """Each colour tile changed by `change(rgb, mm_per_px) -> rgb`, written to new files and loaded as a new tiled
    image the skin then reads - the library's images are packed, so changing a path did nothing (2026-11-07)."""
    maps = _maps()
    out = Path(bpy.app.tempdir) / "gate_factors"
    out.mkdir(parents=True, exist_ok=True)
    for node in _colour_nodes(built):
        image = node.image
        numbers = [t.number for t in image.tiles]
        for number in numbers:
            px = _tile_pixels(image, number)
            mm_per_px = maps.MM_PER_UV.get(number, 724.0) / px.shape[0]  # the tile's mean density
            px[..., :3] = change(px[..., :3], mm_per_px)
            h, w = px.shape[:2]
            plain = bpy.data.images.new(f"factor_{number}", w, h, float_buffer=True)
            plain.colorspace_settings.name = image.colorspace_settings.name
            plain.pixels.foreach_set(px.ravel())
            plain.filepath_raw = str(out / f"colour.{number}.exr")
            plain.file_format = "OPEN_EXR"
            plain.save()
            bpy.data.images.remove(plain)
        new = bpy.data.images.load(str(out / f"colour.{numbers[0]}.exr"), check_existing=False)
        new.source = "TILED"
        new.filepath = str(out / "colour.<UDIM>.exr")
        new.colorspace_settings.name = image.colorspace_settings.name
        new.reload()
        for number in numbers[1:]:
            if new.tiles.get(number) is None:
                new.tiles.new(tile_number=number)
        new.reload()
        node.image = new
        print("COLOUR REWRITTEN", [t.number for t in new.tiles], flush=True)


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


def scaled(spec: str):
    """A trial setting: `pores*1.15`, `micro*1.35`, `relief*2` (the scan relief's normal-map strength), joined by `+` -
    each layer's depth scaled everywhere, to see a change before it is made in the region map."""
    def prepare(built: dict) -> None:
        for part in spec.split("+"):
            key, factor = part.split("*")
            for nt in _skin_trees(built):
                if key in ("pores", "micro"):
                    node = nt.nodes[_maps().NODE + f"{key.rstrip('s')}_depth"]
                    node.inputs[1].default_value *= float(factor)
                elif key == "relief":
                    nt.nodes[_maps().NODE + "normal_map"].inputs["Strength"].default_value *= float(factor)
                else:
                    raise KeyError(key)
    return prepare


def factor(name: str):
    return FACTORS[name] if name in FACTORS else scaled(name)


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
        tag = "_f-" + name.replace("*", "x").replace(".", "p").replace("+", "_")  # a file name Windows takes
        pg.render("ours", a.engine, out, a.views.split(","), pg.SIZE, pg.CYCLES_SAMPLES, tag=tag,
                  prepare=factor(name))
        for view in a.views.split(","):
            made = out / f"{a.engine}_{view}_ours{tag}.png"
            print("WRITTEN" if made.exists() else "MISSING", made, flush=True)
