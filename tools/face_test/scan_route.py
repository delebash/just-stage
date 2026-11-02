# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test: the whole scan route for one or more scans (`docs/plans/2026-11-02-scan-skin-base.md` §6), each step in
the environment it needs - Blender for import, views and the bake; the tool environment (trimesh, MediaPipe) for the
marks and the fit; the RealDenseFace environment (PyTorch) for the pairs, the skin mask and the layers. Stops a scan
at its first failed step and goes on to the next scan. Run: .dev/venv-tools/Scripts/python -I
tools/face_test/scan_route.py NAME [NAME ...]
"""

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("E:/Dev/3D/just-stage")
TOOLS = ROOT / "tools/face_test"
BLENDER = "E:/blender-5.3.0-beta/blender.exe"
PY_TOOLS = str(ROOT / ".dev/venv-tools/Scripts/python.exe")
PY_RDF = str(ROOT / ".dev/venv-rdf/Scripts/python.exe")


def blender(script, *args):
    return [BLENDER, "-b", "--factory-startup", "--python", str(TOOLS / script), "--", *args]


def steps(name):
    return [
        ("convert", blender("scan_convert.py", name)),
        ("sphere views", blender("scan_views.py", name, "sphere")),
        ("upright", [PY_TOOLS, "-I", str(TOOLS / "scan_orient.py"), name]),
        ("views", blender("scan_views.py", name)),
        ("marks", [PY_TOOLS, "-I", str(TOOLS / "scan_marks.py"), name]),
        ("face view", blender("scan_views.py", name, "face")),
        ("face marks", [PY_TOOLS, "-I", str(TOOLS / "scan_marks.py"), name, "face"]),
        ("pairs", [PY_RDF, "-I", str(TOOLS / "scan_pairs.py"), name]),
        ("fit", [PY_TOOLS, "-I", str(TOOLS / "scan_fit.py"), name]),
        ("bake", blender("scan_bake.py", name)),
        ("skin", [PY_RDF, "-I", str(TOOLS / "scan_skin.py"), name]),
        ("layers", [PY_RDF, "-I", str(TOOLS / "skin_base.py"), "split", name]),
    ]


def main(names):
    failed = []
    for name in names:
        t0 = time.time()
        for label, cmd in steps(name):
            t = time.time()
            run = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
            lines = [ln for ln in (run.stdout + run.stderr).splitlines()
                     if ln.startswith(name) or "Error" in ln or "Traceback" in ln or ln.startswith("baked")]
            for ln in lines[-4:]:
                print(f"  {ln[:240]}")
            ok = run.returncode == 0 and not any("Traceback" in ln for ln in lines)
            if not ok and label == "marks" and "no face in any turn" in run.stdout + run.stderr:
                # a wide full body (spread arms) framed whole: its face too small - the turns again, framed on the head
                print(f"{name}: no face in the turns - framing on the head", flush=True)
                subprocess.run(blender("scan_views.py", name, "body"), capture_output=True, text=True)
                run = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
                ok = run.returncode == 0
                for ln in [x for x in (run.stdout + run.stderr).splitlines() if x.startswith(name)][-2:]:
                    print(f"  {ln[:240]}")
            print(f"{name}: {label} {'ok' if ok else 'FAILED'} ({time.time() - t:.0f}s)", flush=True)
            if not ok:
                print("\n".join((run.stdout + run.stderr).splitlines()[-12:]))
                failed.append(f"{name} ({label})")
                break
        print(f"{name}: done in {time.time() - t0:.0f}s", flush=True)
    print("failed: " + (", ".join(failed) if failed else "none"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
