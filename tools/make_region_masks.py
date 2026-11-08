# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer's region masks (the approved design: "soft, overlapping region masks (CC5's part list)"; the job's doc
`docs/plans/2026-11-08-mixer.md` step 3): soft weights over hm08's vertices, summing to 1 at every vertex, for CC5's
parts - head shape, forehead, eyes, nose, mouth, chin, ears, torso, arms, legs ("body ratio" is a whole-body weight,
no mask). From data we already have, nothing painted by hand:

- the body's parts are the skeleton's own weights summed per part (`data/generated/rigs/weights.ue5.json`,
  tools/make_skeleton.py) - a soft partition summing to 1;
- the face's regions, inside the head's share (the `head` and `neck_*` weights), are MakeHuman's own CC0 face targets
  by region folder: how far a region's targets move each vertex (the largest move, over the region's 90th percentile,
  capped at 1), normalised where regions overlap; what the face regions leave of the head is the head shape. Measured
  2026-11-08: face folders are local (forehead 658 ... eyes 1,552 vertices moved), body folders global (breast moves
  every vertex) - so the body takes the skeleton's parts.

    .dev/venv-tools/Scripts/python -I tools/make_region_masks.py

Writes `extension/juststage/data/generated/mixer/regions.npz`: one float32 array per region (19,158 values)."""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "extension" / "juststage" / "data" / "fetched" / "makehuman" / "targets"
WEIGHTS = ROOT / "extension" / "juststage" / "data" / "generated" / "rigs" / "weights.ue5.json"
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "mixer" / "regions.npz"
HM08_VERTICES = 19158  # core/makehuman.py
MOVE_MM = 0.5  # a target moves a vertex when it moves it over this
#: CC5's face parts -> MakeHuman's target folders (its brows belong to the forehead, its cheeks to the head shape)
FACE = {"forehead": ("forehead", "eyebrows"), "eyes": ("eyes",), "nose": ("nose",), "mouth": ("mouth",),
        "chin": ("chin",), "ears": ("ears",)}  # fmt: skip
#: CC5's body parts -> the skeleton's bones (by prefix); the head's share is what the face regions divide
BODY = {"torso": ("root", "pelvis", "spine_", "clavicle_", "breast_"),
        "arms": ("upperarm", "lowerarm", "hand_", "thumb_", "index_", "middle_", "ring_", "pinky_"),
        "legs": ("thigh", "calf", "foot_", "ball_")}  # fmt: skip
HEAD = ("head", "neck_")


def _moved(folder: str) -> np.ndarray:
    """The largest move (mm) any target under `folder` gives each hm08 vertex."""
    out = np.zeros(HM08_VERTICES)
    for path in sorted((TARGETS / folder).rglob("*.target.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line[0] in '#"':
                    continue
                i, dx, dy, dz = line.split()[:4]
                d = (float(dx) ** 2 + float(dy) ** 2 + float(dz) ** 2) ** 0.5 * 100.0  # decimetres -> mm
                out[int(i)] = max(out[int(i)], d)
    return out


def _share(weights: dict, prefixes: tuple[str, ...]) -> np.ndarray:
    out = np.zeros(HM08_VERTICES)
    for bone, rows in weights.items():
        if bone.startswith(prefixes):
            for i, w in rows:
                out[int(i)] += w
    return out


def main(out: Path = OUT) -> dict:
    weights = json.loads(WEIGHTS.read_text(encoding="utf-8"))["weights"]
    head = _share(weights, HEAD)
    regions = {name: _share(weights, prefixes) for name, prefixes in BODY.items()}
    raw = {}
    for name, folders in FACE.items():
        moved = np.maximum.reduce([_moved(f) for f in folders])
        scale = np.percentile(moved[moved > MOVE_MM], 90) if (moved > MOVE_MM).any() else 1.0
        raw[name] = np.clip(moved / scale, 0.0, 1.0) * (moved > MOVE_MM)
    total = sum(raw.values())
    over = np.maximum(total, 1.0)
    for name, w in raw.items():
        regions[name] = head * w / over
    regions["head shape"] = head * (1.0 - np.minimum(total, 1.0))
    total_all = sum(regions.values())
    weighted = total_all > 0
    report = {name: int((w > 0.01).sum()) for name, w in regions.items()}
    report["sum max error"] = float(np.abs(total_all[weighted] - 1.0).max())
    report["unweighted vertices"] = int((~weighted).sum())  # the helpers MPFB2's weights leave out
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, **{k: v.astype(np.float32) for k, v in regions.items()})
    print(f"REGIONS {out}: {report}", flush=True)
    return report


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
