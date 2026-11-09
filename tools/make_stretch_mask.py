# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The lids' margins where the default human's resting shape stretches them against the body's UV layout (the basis),
on the head tile - the eyelid contact (base.CONTACT, always on) pulls them 2-10x (measured 2026-11-09), so every
map read through the UVs - the scans' colour, the pores, the relief - drew streaks across the lower lid's ledge at the
eye view. The band is always seen and always stretched, and a real margin is smooth wet tissue, so inside the mask
modules/skin/maps.py cuts the relief layers and tools/face_test/skin_base.py smooths the composed colour.

    python tools/dev.py blender -b --python tools/make_stretch_mask.py [-- --out DIR]

Each vertex's stretch is the largest area ratio (rest shape - every key at its value, no armature - over the basis) of
the faces round it; the mask rises from STRETCH_FROM to STRETCH_FULL on the lids' margins only (base v2's
`js_margin` and one ring round it - elsewhere the shape keys stretch other skin too: 31 regions over the head tile,
measured 2026-11-09), softened over the neighbours. Writes
`stretched.png` (8-bit grey, 2048², the head tile's UV square) into the generated skin folder.
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
base = importlib.import_module("bl_ext.system.juststage.modules.body.base")

_spec = importlib.util.spec_from_file_location("make_mouth_mask", Path(__file__).with_name("make_mouth_mask.py"))
mouth = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mouth)  # its _raster: per-vertex weights into the head tile's UV square

STRETCH_FROM, STRETCH_FULL = 2.0, 3.0  # face area, the rest shape over the basis


def _out_dir() -> Path:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return Path(args[args.index("--out") + 1]) if "--out" in args else paths.GENERATED / "skin"


def _area(co: np.ndarray, faces: list[tuple[int, ...]]) -> np.ndarray:
    out = np.empty(len(faces))
    for k, f in enumerate(faces):
        v = co[list(f)]
        out[k] = sum(0.5 * np.linalg.norm(np.cross(v[i] - v[0], v[i + 1] - v[0])) for i in range(1, len(v) - 1))
    return out


def stretch(body: bpy.types.Object) -> np.ndarray:
    """Each vertex's resting stretch: the largest rest / basis area ratio of its faces (1 where nothing moves)."""
    for mod in body.modifiers:
        mod.show_viewport = False  # the shape keys alone (the armature's pose and the levels aside)
    bpy.context.view_layer.update()
    ev = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    n = len(body.data.vertices)
    rest = np.empty(n * 3, np.float32)
    me.vertices.foreach_get("co", rest)
    ev.to_mesh_clear()
    basis = np.empty(n * 3, np.float32)
    body.data.shape_keys.key_blocks[0].data.foreach_get("co", basis)
    faces = [tuple(p.vertices) for p in body.data.polygons]
    ratio = _area(rest.reshape(-1, 3), faces) / np.maximum(_area(basis.reshape(-1, 3), faces), 1e-12)
    out = np.ones(n)
    for f, r in zip(faces, ratio, strict=True):
        idx = list(f)
        out[idx] = np.maximum(out[idx], r)
    return out


def main() -> None:
    # eyes opened and the eye parts added - the contact on - but no mapped skin: its shader reads this tool's mask
    made = api.run("juststage.body.create", name="Stretch mask")
    importlib.import_module("bl_ext.system.juststage.modules.body.body_create").open_eyes(made.character)
    api.run("juststage.head.add_parts", character=made.character)
    body = bpy.data.objects[made.object]
    s = stretch(body)
    t = np.clip((s - STRETCH_FROM) / (STRETCH_FULL - STRETCH_FROM), 0.0, 1.0)
    weight = (t * t * (3 - 2 * t)).astype(np.float32)
    edges = np.array([e.vertices for e in body.data.edges])
    margin = np.zeros(len(weight), np.float32)
    body.data.attributes[base.MARGIN_ATTR].data.foreach_get("value", margin)
    near = margin > 0.01
    near[edges[near[edges[:, 0]], 1]] = True  # and one ring round the margin
    near[edges[near[edges[:, 1]], 0]] = True
    weight *= near
    for _ in range(2):  # softened over the neighbours, as the mouth's lining
        acc, cnt = weight.copy(), np.ones_like(weight)
        np.add.at(acc, edges[:, 0], weight[edges[:, 1]])
        np.add.at(acc, edges[:, 1], weight[edges[:, 0]])
        np.add.at(cnt, edges[:, 0], 1)
        np.add.at(cnt, edges[:, 1], 1)
        weight = np.maximum(weight, acc / cnt)
    image, count = mouth._raster(body.data, weight)
    folder = _out_dir()
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / "stretched.png"
    maps.write_png(out, np.repeat(image[..., None], 3, axis=2))
    print(f"wrote {out}: {int((weight > 0.5).sum())} stretched vertices (most {s.max():.2f}x), {count} polygons, "
          f"{(image > 0.5).mean():.3%} of the head tile")


if __name__ == "__main__":
    main()
