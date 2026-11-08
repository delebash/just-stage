# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The scalp hair's feasibility, part 2 (plan §0; the user, 2026-11-07: "can't you make a bunch of your own high
quality hair ... use cc5 metahuman as reference"): can OUR generator make an artist's cut? A reference cut on our head
(`groom_transfer.py` - HD Aaron's own, a local test) is measured as a smoothed field: at points over the scalp, the way
the hair runs (each strand's direction averaged over FIELD_MM), and per root the strand's length and how far its tip
stands off the skin. Our generator then grows its own strands from its own roots along that field (`factors fieldcut`)
- the reference's strands themselves are never used, only these smoothed measures (as the skin was matched to his
statistics, not his pixels).

    .dev/venv-tools/Scripts/python -I tools/gate/hair_field.py OURS.npz STRANDS.npz FIELD.npz
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

FIELD_MM = 15.0  # the field's smoothing radius: a region's flow, not a card's
SAMPLES = 12000  # field points kept


def measure(ours_npz: Path, strands_npz: Path, out: Path) -> None:
    import trimesh
    from scipy.spatial import cKDTree

    o, s = np.load(ours_npz), np.load(strands_npz)
    co, tris = o["co"], o["tris"]
    top = co[:, 2].max()
    head = co[:, 2] > top - 0.30
    skin = trimesh.Trimesh(co, tris[head[tris].all(1)], process=False)
    strands = np.split(s["points"].astype(np.float64), np.cumsum(s["counts"])[:-1])
    strands = [x for x in strands if len(x) > 1]
    pos = np.concatenate([(x[1:] + x[:-1]) / 2 for x in strands])
    tan = np.concatenate([np.diff(x, axis=0) for x in strands])
    tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-12)
    rng = np.random.default_rng(0)
    keep = rng.choice(len(pos), min(SAMPLES, len(pos)), replace=False)
    tree = cKDTree(pos)
    radius = FIELD_MM / 1000
    smooth = np.array([tan[tree.query_ball_point(p, radius)].mean(0) for p in pos[keep]])
    smooth /= np.maximum(np.linalg.norm(smooth, axis=1, keepdims=True), 1e-12)
    roots = np.array([x[0] for x in strands])
    length = np.array([np.linalg.norm(np.diff(x, axis=0), axis=1).sum() for x in strands])
    tip_off = trimesh.proximity.closest_point(skin, np.array([x[-1] for x in strands]))[1]
    rt = cKDTree(roots)
    # per root, the neighbourhood's median (a region's length and stand-off, not one card's)
    near = [rt.query_ball_point(r, radius) for r in roots]
    length_s = np.array([np.median(length[n]) for n in near])
    lift_s = np.array([np.median(tip_off[n]) for n in near])
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, pos=pos[keep].astype(np.float32), tan=smooth.astype(np.float32), roots=roots.astype(np.float32),
             length=length_s.astype(np.float32), lift=lift_s.astype(np.float32), radius_mm=FIELD_MM)  # fmt: skip
    print(f"FIELD: {len(keep)} points, {len(roots)} roots; length p10/50/90 "
          f"{np.percentile(length_s, [10, 50, 90]).round(3) * 1000} mm; tip stand-off p10/50/90 "
          f"{np.percentile(lift_s, [10, 50, 90]).round(4) * 1000} mm", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    measure(Path(a[0]), Path(a[1]), Path(a[2]))
