# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""ICT-FaceKit's head placed on hm08's basis once - the proxy every character wears (Q-BASE-4, mine 2026-11-10;
docs/plans/2026-11-10-ict-head.md §0 and step 1's recipe). MakeHuman's own way to use another topology: a proxy fitted
to the base mesh once, which then follows every target (here by Surface Deform, `modules/head/ict_proxy.py`).

    1. python tools/dev.py blender -b --python tools/make_ict_proxy.py -- export     (hm08's basis: every key muted)
    2. .dev/venv-tools/Scripts/python -I tools/make_ict_proxy.py place               (ict_head.place, head6's options)

Writes `extension/juststage/data/generated/ict/head_proxy.npz`: `verts` (ICT's face and head-and-neck, 11,248, on the
basis, the body's object space), `counts` / `flat` (its polygons), `eyes` (ICT's eyeball centres, placed). head6's
options - ICT's lids kept 8-15 mm (the brow stays on our ridge), a 3 mm crease - are the head that read NEAR EQUAL to
HD Aaron's eye (`.dev/gate/parts/2026-11-10icthead`, `head6.png`)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "extension" / "juststage" / "data" / "generated" / "ict"
BASIS = OUT_DIR / "basis_export.npz"  # step 1's output, step 2's input (kept: the proxy's source, re-placeable)
PROXY = OUT_DIR / "head_proxy.npz"
ICT = ROOT / "extension" / "juststage" / "data" / "fetched" / "ict"
CREASE_MM = 3.0  # head6's crease (`crease5_eye.png`: 3 mm read as his)


def export() -> None:
    """A New human's basis - every shape key muted, so the mesh is hm08's raw base, the shape Surface Deform binds
    at - its skin's vertices (object space), triangles and the lids' rims (`base.rows`)."""
    import importlib

    api = importlib.import_module("bl_ext.system.juststage.api")
    base = importlib.import_module("bl_ext.system.juststage.modules.body.base")
    makehuman = importlib.import_module("bl_ext.system.juststage.core.makehuman")
    import bpy

    made = api.run("juststage.body.create", name="ICT proxy basis")
    body = bpy.data.objects[made.object]
    keys = body.data.shape_keys
    co = np.empty(len(body.data.vertices) * 3, np.float32)
    (keys.reference_key.data if keys else body.data.vertices).foreach_get("co", co)
    co = co.reshape(-1, 3).astype(np.float64)
    skin = makehuman.skin_mask(len(co))
    tris = [[p.vertices[0], p.vertices[k], p.vertices[k + 1]] for p in body.data.polygons
            if skin[list(p.vertices)].all() for k in range(1, len(p.vertices) - 1)]  # fmt: skip
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # object space: the proxy is parented to the body and bound there (`ict_proxy.add`)
    np.savez(BASIS, co=co, tris=np.array(tris, np.int64), rows=base.rows(), world=np.eye(4))
    print("EXPORTED the basis:", len(co), "vertices,", len(tris), "skin triangles ->", BASIS, flush=True)


def place() -> None:
    sys.path.insert(0, str(ROOT / "tools" / "gate"))
    import ict_head

    ict_head.place(BASIS, ICT, PROXY, keep_lids=False, crease_mm=CREASE_MM, keep_mm=ict_head.EYE_KEEP_LID_MM)
    print("PROXY", PROXY, flush=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    {"export": export, "place": place}[args[0]]()
