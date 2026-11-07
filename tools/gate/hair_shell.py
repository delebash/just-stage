# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""How far the scalp hair stands off the scalp, by region - the groom's volume against HD Aaron's (plan §0; RESEARCH
§14.14: his p50 / p90 13 / 23 mm on top, ours 5.5 / 11.7 with "short combed"). Each hair point's distance to the
body's surface (his card vertices, our evaluated strand points), in head-centred regions: top, back, sides, nape.

    python tools/dev.py blender -b --python tools/gate/hair_shell.py -- --who ours [--scalp "generated:short taper"]
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("parts_gate", HERE / "parts_gate.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)
hc_spec = importlib.util.spec_from_file_location("hair_cover", HERE / "hair_cover.py")
hc = importlib.util.module_from_spec(hc_spec)
hc_spec.loader.exec_module(hc)

SAMPLE = 60_000
NEAR = 0.2  # m from the hair's median: farther points are strays (the 2% on the body, fixed 2026-11-07)


def shell(who: str, scalp: str) -> None:
    scene, _cam = pg._stage()
    built = pg.build_ours(scene, scalp=scalp) if who == "ours" else pg.build_cc5(scene, "eevee")
    body = built["body"]
    dg = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(body, dg)
    to_body = body.matrix_world.inverted()
    scale = body.matrix_world.to_scale()[0]
    hair = next(o for o in bpy.data.objects if o.type in ("MESH", "CURVES") and hc._is_scalp(o) and o != body)
    ev = hair.evaluated_get(dg)
    if hair.type == "CURVES":
        pos = np.empty(len(ev.data.points) * 3, np.float32)
        ev.data.attributes["position"].data.foreach_get("vector", pos)
    else:
        me = ev.to_mesh()
        pos = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get("co", pos)
    pos = pos.reshape(-1, 3) @ np.array(hair.matrix_world)[:3, :3].T + np.array(hair.matrix_world)[:3, 3]
    sel = pos[np.random.default_rng(0).choice(len(pos), min(SAMPLE, len(pos)), replace=False)]
    c = np.median(sel, 0)
    near = np.linalg.norm(sel - c, axis=1) < NEAR
    sel = sel[near]
    d = np.array([tree.find_nearest(to_body @ Vector(p))[3] for p in sel]) * scale * 1000.0
    rel = sel - c
    top = rel[:, 2] > 0.04
    back = (rel[:, 1] > 0.03) & ~top
    side = (np.abs(rel[:, 0]) > 0.05) & ~top & ~back
    nape = (rel[:, 2] < -0.04) & (rel[:, 1] > 0.0)
    print(f"SHELL {who} {scalp if who == 'ours' else ''}: {hair.name}, strays {int((~near).sum())} of {len(near)}")
    for name, m in (("top", top), ("sides", side), ("back", back), ("nape", nape)):
        if m.any():
            print(f"SHELL   {name:6s} p50 {np.percentile(d[m], 50):5.1f}  p90 {np.percentile(d[m], 90):5.1f} mm")


if __name__ == "__main__":
    import argparse

    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="hair_shell.py --")
    p.add_argument("--who", choices=("ours", "cc5"), required=True)
    p.add_argument("--scalp", default="library")
    a = p.parse_args(args)
    shell(a.who, a.scalp)
