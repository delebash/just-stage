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

LOCAL TEST DATA: the scans' licences (CC BY and others) are read per scan before any identity ships, and a shipped
character is never one scan's face (the likeness rule: >= 2 identities a region, Q-SHAPE-1).

    .dev/venv-tools/Scripts/python -I tools/make_identities.py

Writes `extension/juststage/data/generated/mixer/identities/<scan>.npz` (index, delta in metres)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCANS = ROOT / ".dev" / "facetest" / "scans"
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "mixer" / "identities"
BODY_VERTICES = 13380  # core/makehuman.py: hm08's body - the export's first vertices
FLOOR = 1e-6  # m: offsets below this are left out, as a target lists only the vertices it moves
#: a fit made against an older export (the file was written again later) lands its offsets ~23 cm off and on another
#: vertex set (measured 2026-11-08: 11 of the 20 fits) - a fit whose median offset passes this is refused, not used
MEDIAN_MAX = 0.010


def main(out: Path = OUT, scans: Path = SCANS) -> dict:
    export = np.load(scans / "head_export.npz")["co"].astype(np.float64)
    out.mkdir(parents=True, exist_ok=True)
    report = {}
    for fit_path in sorted(scans.glob("*/fit.npz")):
        fit = np.load(fit_path)
        used, fitted = fit["used"], fit["fitted"].astype(np.float64)
        base = used < BODY_VERTICES  # the original vertices: hm08's own
        index = used[base]
        delta = fitted[base] - export[index]
        keep = np.linalg.norm(delta, axis=1) > FLOOR
        name = fit_path.parent.name
        median = float(np.median(np.linalg.norm(delta, axis=1)))
        if median > MEDIAN_MAX:
            stale = out / f"{name}.npz"
            if stale.exists():
                stale.unlink()
            report[name] = ("refused: another export", round(median * 1000, 1))
            continue
        np.savez(out / f"{name}.npz", index=index[keep].astype(np.int64), delta=delta[keep].astype(np.float32),
                 source=f"face-test scan fit {name} (tools/face_test/scan_fit.py), LOCAL")  # fmt: skip
        report[name] = (int(keep.sum()), round(float(np.linalg.norm(delta, axis=1).max()) * 1000, 1))
    print(f"IDENTITIES {out}: {len(report)} - {report}", flush=True)
    return report


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
