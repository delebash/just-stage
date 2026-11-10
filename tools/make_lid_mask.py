# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The upper lids' blink stretch on the body's head tile (UDIM 1001), each eye apart: the skin the blink opens out over
the closed eye - its faces 2.4-5x top to bottom (measured 2026-11-09) - where every map read through the UVs drew
vertical streaks over the closed lid beside HD Aaron's plain lid. The left eye's in the red channel, the right eye's in
the green, so modules/skin/maps.py's closed lid (`_closed_lid_share`) works there by each eye's own blink
(eyeBlinkLeft / eyeBlinkRight) - only while it closes: the open eye unchanged (a mask applied always made the open lid
smooth and glossy - 2026-11-09 11:18). Made once on the default human with its face units, like the mouth's masks.

    python tools/dev.py blender -b --python tools/make_lid_mask.py [-- --out DIR]

Each vertex's stretch is the largest area ratio (that eye's blink at 1 over the basis) of the faces round it; the mask
rises from STRETCH_FROM to STRETCH_FULL, softened over the neighbours. Writes `lid_blink.png` (8-bit RGB, 2048², the
head tile's UV square) into the generated skin folder.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

import bpy
import numpy as np

api = importlib.import_module("bl_ext.system.juststage.api")
paths = importlib.import_module("bl_ext.system.juststage.paths")
maps = importlib.import_module("bl_ext.system.juststage.modules.skin.maps")

_spec = importlib.util.spec_from_file_location("make_mouth_mask", Path(__file__).with_name("make_mouth_mask.py"))
mouth = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mouth)  # its _raster: per-vertex weights into the head tile's UV square

STRETCH_FROM, STRETCH_FULL = 1.3, 2.0  # face area, the blink over the basis
#: the character's left eye's key first (its +X side), the right's second - the mask's red and green channels
BLINKS = ("eyeBlinkLeft", "eyeBlinkRight")


def _out_dir() -> Path:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return Path(args[args.index("--out") + 1]) if "--out" in args else paths.GENERATED / "skin"


def _area(co: np.ndarray, faces: list[tuple[int, ...]]) -> np.ndarray:
    out = np.empty(len(faces))
    for k, f in enumerate(faces):
        v = co[list(f)]
        out[k] = sum(0.5 * np.linalg.norm(np.cross(v[i] - v[0], v[i + 1] - v[0])) for i in range(1, len(v) - 1))
    return out


def stretch(body: bpy.types.Object, key: str) -> np.ndarray:
    """Each vertex's stretch under one blink key: the largest key / basis area ratio of its faces (1 where none)."""
    keys = body.data.shape_keys.key_blocks
    n = len(body.data.vertices)
    basis = np.empty(n * 3, np.float32)
    keys[0].data.foreach_get("co", basis)
    closed = np.empty(n * 3, np.float32)
    keys[key].data.foreach_get("co", closed)  # the basis plus the unit's offsets
    faces = [tuple(p.vertices) for p in body.data.polygons]
    ratio = _area(closed.reshape(-1, 3), faces) / np.maximum(_area(basis.reshape(-1, 3), faces), 1e-12)
    out = np.ones(n)
    for f, r in zip(faces, ratio, strict=True):
        idx = list(f)
        out[idx] = np.maximum(out[idx], r)
    return out


def weight(body: bpy.types.Object, key: str) -> np.ndarray:
    t = np.clip((stretch(body, key) - STRETCH_FROM) / (STRETCH_FULL - STRETCH_FROM), 0.0, 1.0)
    w = (t * t * (3 - 2 * t)).astype(np.float32)
    edges = np.array([e.vertices for e in body.data.edges])
    for _ in range(2):  # softened over the neighbours, as the mouth's lining
        acc, cnt = w.copy(), np.ones_like(w)
        np.add.at(acc, edges[:, 0], w[edges[:, 1]])
        np.add.at(acc, edges[:, 1], w[edges[:, 0]])
        np.add.at(cnt, edges[:, 0], 1)
        np.add.at(cnt, edges[:, 1], 1)
        w = np.maximum(w, acc / cnt)
    return w


def main() -> None:
    made = api.run("juststage.body.create", name="Lid mask")
    api.run("juststage.head.add_parts", character=made.character)
    api.run("juststage.head.add_face_units", character=made.character)
    body = bpy.data.objects[made.object]
    channels = []
    for key in BLINKS:
        image, count = mouth._raster(body.data, weight(body, key))
        channels.append(image)
        print(f"{key}: {count} polygons, {(image > 0.5).mean():.3%} of the head tile")
    rgb = np.stack([channels[0], channels[1], np.zeros_like(channels[0])], axis=2)
    folder = _out_dir()
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / "lid_blink.png"
    maps.write_png(out, rgb)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
