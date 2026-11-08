# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""ICT-FaceKit's scanned expression shapes as our face units (the plan's §7 "Expression shapes", Q-RIG-1's per-shape
pick, decided under the go 2026-11-08 for the shapes measured: Faceunits' eyeBlink folds the closed lid, ICT's
closes smooth - the gate's sheet `sheet_C9_ictblink.png`; ICT's mouthSmile + cheekSquint lift the corners and cheeks
as HD Aaron's smile does, Faceunits' bends the mouth alone - RESEARCH 14.7). ICT's shape is carried onto our base man through the
smile carry's wrap (eye-rim landmarks, a scaled ICP, Amberg's NICP, a barycentric carry with a harmonic fill -
`tools/gate/smile_transfer.py carry`), then kept as offsets on hm08's vertices, the form MakeHuman's targets take, so
every character applies it as it applies a Faceunits target (`face_units.add`; base v2's appended vertices carried by
`base.extend`). ICT-FaceKit is MIT (its LICENSE; ATTRIBUTION.md).

    1. python tools/dev.py blender -b --python tools/gate/smile_transfer.py -- export
           .dev/gate/smile/ours_average_man.npz
    2. .dev/venv-tools/Scripts/python -I tools/gate/smile_transfer.py carry .dev/gate/smile/ours_average_man.npz
           extension/juststage/data/fetched/ict .dev/gate/smile/ict_units.npz
           eyeBlink_L,eyeBlink_R,mouthSmile_L,mouthSmile_R,cheekSquint_L,cheekSquint_R
       (ICT's files from `python tools/fetch_data.py`)
    3. .dev/venv-tools/Scripts/python -I tools/make_ict_units.py .dev/gate/smile/ict_units.npz

Writes `extension/juststage/data/generated/faceunits_ict/<ARKit name>.npz` (index, delta in metres)."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "faceunits_ict"
HM08_VERTICES = 19158  # core/makehuman.py: hm08's own vertices; base v2's appended ones follow
#: ICT's file names to our ARKit keys (the carry checks each shape's side: _L moves +x, the character's left)
NAMES = {"eyeBlink_L": "eyeBlinkLeft", "eyeBlink_R": "eyeBlinkRight", "mouthSmile_L": "mouthSmileLeft",
         "mouthSmile_R": "mouthSmileRight", "cheekSquint_L": "cheekSquintLeft", "cheekSquint_R": "cheekSquintRight"}
FLOOR = 1e-6  # m: offsets below this are left out, as a target lists only the vertices it moves


def main(carried: Path) -> None:
    data = np.load(carried)
    world = data["world"]
    to_local = np.linalg.inv(world[:3, :3])
    OUT.mkdir(parents=True, exist_ok=True)
    for ict, ours in NAMES.items():
        delta = data[ict].astype(np.float64)[:HM08_VERTICES] @ to_local.T
        index = np.flatnonzero(np.linalg.norm(delta, axis=1) > FLOOR)
        np.savez(OUT / f"{ours}.npz", index=index.astype(np.int64), delta=delta[index].astype(np.float32),
                 source=f"ICT-FaceKit {ict} (da5f95a6), carried by tools/gate/smile_transfer.py")  # fmt: skip
        most = np.linalg.norm(delta, axis=1).max() * 1000
        print(f"UNIT {ours}: {len(index)} vertices, max {most:.1f} mm", flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
