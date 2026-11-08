# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer's identities (the job's doc `docs/plans/2026-11-08-mixer.md` step 4): each face-test scan fit as offsets
on hm08's vertices, the form MakeHuman's targets take (as `faceunits_ict`), so the mixer applies an identity as a
target. The fits (`tools/face_test/scan_fit.py`) wrapped the face test's exported head
(`.dev/facetest/scans/head_export.npz`: the round scene's body evaluated - helpers masked, subdivided once - 53,514
vertices) onto each scan, its size normalised to our head; Blender's subdivision keeps the original vertices first,
so export vertex i < 13,380 is hm08 vertex i (checked 2026-11-08: export vs hm08 base, index for index, median 46.5 mm
apart against 679 mm shuffled - the character's own shape and a translation-only alignment the rest). An identity's
offset at hm08 vertex i = its fit there minus the export there: the scan's shape against the face test's character.

A fit covers the face and neck down to a cut (one ring of 42 vertices); its offsets stop there by 10-32 mm (measured
2026-11-08), a seam in any mix. So they are carried past the cut by a harmonic fill - each unfitted vertex the mean of
its neighbours (the uniform Laplacian, Botsch & Sorkine's membrane), the fit fixed - fading to nothing where the head's
share of the skeleton (its head and neck bones, `make_region_masks.HEAD`) ends.

LOCAL TEST DATA: the scans' licences (CC BY and others) are read per scan before any identity ships, and a shipped
character is never one scan's face (the likeness rule: >= 2 identities a region, Q-SHAPE-1).

    .dev/venv-tools/Scripts/python -I tools/make_identities.py

Writes `extension/juststage/data/generated/mixer/identities/<scan>.npz` (index, delta in metres); reports per scan
(vertices moved, largest offset mm, largest offset change along an edge mm)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

ROOT = Path(__file__).resolve().parents[1]
SCANS = ROOT / ".dev" / "facetest" / "scans"
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "mixer" / "identities"
BASE = ROOT / "extension" / "juststage" / "data" / "fetched" / "makehuman" / "3dobjs" / "base.obj"
WEIGHTS = ROOT / "extension" / "juststage" / "data" / "generated" / "rigs" / "weights.ue5.json"
BODY_VERTICES = 13380  # core/makehuman.py: hm08's body - the export's first vertices
FLOOR = 1e-6  # m: offsets below this are left out, as a target lists only the vertices it moves
#: a fit made against an older export (the file was written again later) lands its offsets ~23 cm off and on another
#: vertex set (measured 2026-11-08: 11 of the 20 fits) - a fit whose median offset passes this is refused, not used
MEDIAN_MAX = 0.010


def graph() -> tuple[np.ndarray, np.ndarray]:
    """hm08's body edges (the base mesh's faces) and the head's share of each body vertex (the skeleton's head and neck
    weights, as the region masks take it)."""
    spec = importlib.util.spec_from_file_location("make_region_masks", Path(__file__).with_name("make_region_masks.py"))
    masks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(masks)
    edges = set()
    with BASE.open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("f "):
                ids = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
                for a, b in zip(ids, ids[1:] + ids[:1], strict=True):
                    if a < BODY_VERTICES and b < BODY_VERTICES:
                        edges.add((min(a, b), max(a, b)))
    weights = json.loads(WEIGHTS.read_text(encoding="utf-8"))["weights"]
    share = masks._share(weights, masks.HEAD)[:BODY_VERTICES]
    return np.array(sorted(edges), np.int64).reshape(-1, 2), np.clip(share, 0.0, 1.0)


def extend(offsets: np.ndarray, fitted: np.ndarray, edges: np.ndarray, share: np.ndarray) -> np.ndarray:
    """The fit's offsets carried over the unfitted vertices the head's share reaches, by the harmonic fill: each such
    vertex the mean of its neighbours, the fitted ones fixed, those outside the share at nothing."""
    n = len(offsets)
    free = ~fitted & (share > 0.0)
    if not free.any() or not len(edges):
        return offsets
    adjacency = sparse.coo_matrix((np.ones(2 * len(edges)), (np.r_[edges[:, 0], edges[:, 1]],
                                  np.r_[edges[:, 1], edges[:, 0]])), shape=(n, n)).tocsr()  # fmt: skip
    degree = np.asarray(adjacency.sum(1)).ravel()
    index = np.flatnonzero(free)
    lap = (sparse.diags(degree[index] + 1e-9) - adjacency[index][:, index]).tocsc()  # an island alone: nothing
    known = np.where(fitted[:, None], offsets, 0.0)
    rhs = adjacency[index] @ known
    out = offsets.copy()
    out[index] = np.column_stack([spsolve(lap, rhs[:, k]) for k in range(3)])
    return out


def main(out: Path = OUT, scans: Path = SCANS, mesh: tuple[np.ndarray, np.ndarray] | None = None) -> dict:
    edges, share = mesh if mesh is not None else graph()
    export = np.load(scans / "head_export.npz")["co"].astype(np.float64)
    out.mkdir(parents=True, exist_ok=True)
    report = {}
    for fit_path in sorted(scans.glob("*/fit.npz")):
        fit = np.load(fit_path)
        used, fitted = fit["used"], fit["fitted"].astype(np.float64)
        base = used < BODY_VERTICES  # the original vertices: hm08's own
        index = used[base]
        delta = fitted[base] - export[index]
        name = fit_path.parent.name
        median = float(np.median(np.linalg.norm(delta, axis=1)))
        if median > MEDIAN_MAX:
            stale = out / f"{name}.npz"
            if stale.exists():
                stale.unlink()
            report[name] = ("refused: another export", round(median * 1000, 1))
            continue
        offsets = np.zeros((BODY_VERTICES, 3))
        offsets[index] = delta
        mask = np.zeros(BODY_VERTICES, bool)
        mask[index] = True
        offsets = extend(offsets, mask, edges, share)
        size = np.linalg.norm(offsets, axis=1)
        keep = np.flatnonzero(size > FLOOR)
        np.savez(out / f"{name}.npz", index=keep.astype(np.int64), delta=offsets[keep].astype(np.float32),
                 source=f"face-test scan fit {name} (tools/face_test/scan_fit.py), LOCAL")  # fmt: skip
        step = np.abs(size[edges[:, 0]] - size[edges[:, 1]]).max() if len(edges) else 0.0
        report[name] = (len(keep), round(float(size.max()) * 1000, 1), round(float(step) * 1000, 2))
    print(f"IDENTITIES {out}: {len(report)} - {report}", flush=True)
    return report


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
