# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The library's six scan skins rebuilt from their compositions, hair out (docs/plans/2026-11-06-inputs-audit.md):
every scan split again (tools/face_test/skin_base.py split - the eye and brow band, strands, stubble out), the six
compositions made again with their recorded scans and stubble off (a man keeps the faint shaved tint), then each baked
into the library (tools/build_skins.py --composed). The compositions' records before this rebuild are kept in
`.dev/backup/compositions_2026-11-06/`.

    python tools/rebuild_scan_skins.py [split] [compose] [build]     (all three by default)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANS = ROOT / ".dev" / "facetest" / "scans"
RECORDS = ROOT / ".dev" / "backup" / "compositions_2026-11-06"
VENV = ROOT / ".dev" / "venv-rdf" / "Scripts" / "python.exe"
SKINS = {611: "Scan man A", 612: "Scan man B", 613: "Scan man C", 621: "Scan woman A", 622: "Scan woman B",
         623: "Scan woman C"}  # fmt: skip
BEARD_SHADOW = 0.35


def run(cmd: list[str]) -> None:
    print(">", " ".join(cmd[-6:]), flush=True)
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    keep = [line for line in (out.stdout + out.stderr).splitlines()
            if any(k in line for k in ("hair out", "covered", "Result(", "Error", "Traceback"))]  # fmt: skip
    print("\n".join(keep), flush=True)
    if out.returncode:
        raise SystemExit(out.returncode)


def main(steps: set[str]) -> None:
    if "split" in steps:
        names = sorted(p.parent.name for p in SCANS.glob("*/layers.npz"))
        run([str(VENV), "-I", "tools/face_test/skin_base.py", "split", *names])
    if "compose" in steps:
        for seed in SKINS:
            p = json.loads((RECORDS / f"base_char{seed}.json").read_text())
            p.pop("relief_file", None)
            p.update(stubble=0.0, scalp_stubble=0.0, beard_shadow=BEARD_SHADOW if p["sex"] == "m" else 0.0)
            run([str(VENV), "-I", "tools/face_test/skin_base.py", "compose", str(seed), json.dumps(p)])
    if "build" in steps:
        for seed, name in SKINS.items():
            if ONLY and seed not in ONLY:
                continue
            run([sys.executable, "tools/dev.py", "blender", "-b", "--python-exit-code", "1", "--python",
                 "tools/build_skins.py", "--", "--composed", str(seed), "man_a", "-", name])  # fmt: skip


ONLY = {int(a) for a in sys.argv[1:] if a.isdigit()}  # seeds to build (all when none named)

if __name__ == "__main__":
    main({a for a in sys.argv[1:] if not a.isdigit()} or {"split", "compose", "build"})
