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

import importlib.util
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


def own_sex_first(p: dict, sexes: dict[str, str]) -> dict:
    """A recorded composition put right by the composer's own rule (skin_base.compose: the character's own sex first)
    against today's scan list: the pores' fill order with the character's own sex first (stable), and the mid layer
    from scans of its sex only, its weights renormalised - a scan's tag fixed after the record was made (HSR0081, a
    woman tagged "m" until 2026-11-09) would otherwise keep a woman's blotchiness in a man's skin."""
    sex = p["sex"]
    out = dict(p)
    fine = list(p["fine_from"])
    out["fine_from"] = [n for n in fine if sexes[n] == sex] + [n for n in fine if sexes[n] != sex]
    mid = {n: w for n, w in p["mid_from"].items() if sexes[n] == sex}
    if mid and len(mid) < len(p["mid_from"]):
        total = sum(mid.values())
        out["mid_from"] = {n: w / total for n, w in mid.items()}
    return out


def _sexes() -> dict[str, str]:
    spec = importlib.util.spec_from_file_location("scan_list", ROOT / "tools" / "face_test" / "scan_list.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {n: s["sex"] for n, s in module.SCANS.items()}


def main(steps: set[str]) -> None:
    if "split" in steps:
        names = sorted(p.parent.name for p in SCANS.glob("*/layers.npz"))
        run([str(VENV), "-I", "tools/face_test/skin_base.py", "split", *names])
    if "compose" in steps:
        sexes = _sexes()
        for seed in SKINS:
            p = own_sex_first(json.loads((RECORDS / f"base_char{seed}.json").read_text()), sexes)
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
