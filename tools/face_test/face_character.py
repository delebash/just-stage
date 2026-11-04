# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test: a whole new character through the face test - the open item "each character's face from its own
painting" (`docs/plans/2026-11-03-open-items.md`). Its body and head from JustStage's own commands (MakeHuman's macros:
sex, age, the African / Asian / Caucasian mix; GNM's scan-based head shape by seed; the skin model's melanin), its face
painted by FLUX 3 from the clay (the hero, then the two 30-degree views from it - the approved structure), the rest of
the head from a skin base of its sex (skin_base.compose), projected and rendered.

The face test works in one folder (.dev/facetest); each character's files are copied into chars/NAME/ when it is
done, and the working files of the character before are copied there and cleared before the next starts (no stale
view leaks in). Run (the tool environment): .dev/venv-tools/Scripts/python -I tools/face_test/face_character.py NAME
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("E:/Dev/3D/just-stage")
TOOLS = ROOT / "tools/face_test"
DIR = ROOT / ".dev/facetest"
CHARS = DIR / "chars"
PY_TOOLS = str(ROOT / ".dev/venv-tools/Scripts/python.exe")
PY_RDF = str(ROOT / ".dev/venv-rdf/Scripts/python.exe")
FACE_VIEWS = ("face", "faceleft30", "faceright30")
#: one character's files in the working folder (the clay stage's, the paintings', the projection's)
PER_CHARACTER = ("clay_*.png", "depth_*.exr", "cameras.json", "face.blend", "head_neutral.npz", "painted_*.png",
                 "aligned_*.png", "aligned_marks.json", "seq_start_*.png", "albedo_*.npy", "albedo_*.png",
                 "nworld_*.npy", "normal_*.npy", "normal_*.png", "landmarks.json", "fit_offsets.npz", "rdf_*.npz",
                 "round.blend", "round.blend1", "face_*.png", "calib.exr", "eyes_*.png")
#: MakeHuman's age macro: 0.5 is 25 years, 1.0 is 90
CHARACTERS = {
    "amara": {"env": {"FACETEST_GENDER": "0.0", "FACETEST_AGE": "0.54", "FACETEST_ETHNIC": "0.9,0.05,0.05",
                      "FACETEST_IDENTITY": "101", "FACETEST_MELANIN": "0.18",
                      "FACETEST_PERSON": "woman in her thirties with dark brown skin and soft feminine features"},
              "base": {"sex": "f", "pores_first": "d3d_african_woman"}, "round": 101},
    "walter": {"env": {"FACETEST_GENDER": "1.0", "FACETEST_AGE": "0.81", "FACETEST_ETHNIC": "0.05,0.05,0.9",
                       "FACETEST_IDENTITY": "202", "FACETEST_IDENTITY_STRENGTH": "0.7", "FACETEST_MELANIN": "0.02",
                       "FACETEST_PERSON": "man in his sixties with light weathered skin, deep wrinkles and short grey "
                                          "stubble on the jaw"},
               "base": {"sex": "m", "pores_first": "yaro13", "stubble": 0.6, "scalp_stubble": 0.15, "age": 1.3},
               "round": 102},
    "mei": {"env": {"FACETEST_GENDER": "0.0", "FACETEST_AGE": "0.49", "FACETEST_ETHNIC": "0.05,0.9,0.05",
                    "FACETEST_IDENTITY": "303", "FACETEST_MELANIN": "0.03",
                    "FACETEST_PERSON": "young East Asian woman in her twenties"},
            "base": {"sex": "f", "pores_first": "portrait_3130", "age": 0.8}, "round": 103},
}


def working_files():
    return sorted({p for pattern in PER_CHARACTER for p in DIR.glob(pattern)})


def keep(name):
    """The working folder's character files copied into chars/NAME/ (and the renders of its round)."""
    dest = CHARS / name
    dest.mkdir(parents=True, exist_ok=True)
    for p in working_files():
        shutil.copy2(p, dest / p.name)
    return dest


def run(label, cmd, env):
    t = time.time()
    done = subprocess.run(cmd, env=env, capture_output=True, text=True, errors="replace")
    tail = [ln for ln in (done.stdout + done.stderr).splitlines() if ln.strip()][-3:]
    print(f"  {label}: {'ok' if done.returncode == 0 else 'FAILED'} ({time.time() - t:.0f}s)", flush=True)
    if done.returncode != 0:
        print("\n".join(f"    {ln[:220]}" for ln in tail))
        raise SystemExit(f"{label} failed")


def main(name):
    spec = CHARACTERS[name]
    current = DIR / "current_char.txt"
    before = current.read_text().strip() if current.exists() else "man_a"  # the face test's first man
    if not (CHARS / before).exists() or before != name:
        print(f"keeping {before}'s working files in {keep(before)}")
    for p in working_files():  # a copy is kept: the new character starts clean
        p.unlink()
    current.write_text(name)
    env = {**os.environ, **spec["env"], "FACETEST_BASE": str(spec["round"]), "FACETEST_ROUND": str(spec["round"])}
    seed = spec["env"]["FACETEST_IDENTITY"]
    t0 = time.time()
    print(f"{name}: {spec['env']['FACETEST_PERSON']}")
    run("clay", [PY_TOOLS, str(ROOT / "tools/dev.py"), "test", str(TOOLS / "test_face_clay.py"), "-k", "face_clay",
                 "-s"], env)
    run("hero painting", [PY_TOOLS, str(TOOLS / "face_paint_cli.py"), seed, "face"], env)
    run("hero aligned", [PY_TOOLS, str(TOOLS / "align_paintings.py"), "face"], env)
    run("30-degree paintings", [PY_RDF, "-I", str(TOOLS / "face_paint_seq.py"), seed, "faceleft30", "faceright30"], env)
    # the aligned paintings' own eyes kept out of the lids' skin (SegFace masks, e2d31e4 - the foreground session)
    run("eye masks", [PY_RDF, "-I", str(TOOLS / "parse_paintings.py"), *FACE_VIEWS], env)
    run("face points", [PY_TOOLS, "-I", str(TOOLS / "landmarks.py")], env)  # the iris band's (test_face_project)
    run("normals", [PY_RDF, "-I", str(TOOLS / "view_normals.py"), *FACE_VIEWS], env)
    run("light removed", [PY_RDF, "-I", str(TOOLS / "delight_views.py"), *FACE_VIEWS], env)
    run("skin base", [PY_RDF, "-I", str(TOOLS / "skin_base.py"), "compose", str(spec["round"]),
                      json.dumps(spec["base"])], env)
    run("projected and rendered", [PY_TOOLS, str(ROOT / "tools/dev.py"), "test", str(TOOLS / "test_face_project.py"),
                                   "-k", "face_project", "-s"], env)
    dest = keep(name)
    for p in DIR.glob(f"*{spec['round']}_*.png"):
        shutil.copy2(p, dest / p.name)
    print(f"{name}: done in {time.time() - t0:.0f}s - {dest}")


if __name__ == "__main__":
    for character in sys.argv[1:]:
        main(character)
