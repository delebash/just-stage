# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: MIT

"""OpenRigLogic's Python bindings (DNA and RigLogic) built for Blender's own Python, packed as a wheel the extension
ships (docs/standards/README.md §5: "libs/ ... the OpenRigLogic wheel build"; Blender bundles an extension's Python
dependencies as wheels - https://docs.blender.org/manual/en/5.3/advanced/extensions/python_wheels.html).

OpenRigLogic (MIT, https://github.com/EpicGames/OpenRigLogic) has no wheels of its own (RESEARCH §8). Its README's
build: CMake 3.14+, SWIG for the Python wrappers, Python 3 with its development headers. Blender's bundled Python has
no headers, so they come from python.org's NuGet package of the same version.

    python libs/openriglogic/build.py [--jobs N]
    python libs/openriglogic/build.py --install   # the built wheel into extension/juststage/wheels only

Inputs (fetched by hand once, see the working doc): the source at SOURCE, pinned to COMMIT; Python 3.13.13's headers
and import library from the NuGet package `python` 3.13.13 at PY_DEV; SWIG from PyPI's `swig` wheel in the tools venv,
pinned to SWIG_VERSION: RigLogic.i calls SWIG's runtime macro `SWIG_EXPAND_AND_QUOTE_STRING`, which SWIG 4.5 dropped
(its swigrun.swg uses `SWIG_STRINGIFY`) - the wrapper failed with C2065/C3861 under 4.5.1 (2026-11-04); 4.3.1 has it.
Output: dist/openriglogic-<version>-cp313-cp313-win_amd64.whl.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / ".dev"
SOURCE = DEV / "cache" / "src" / "OpenRigLogic"
COMMIT = "ea253d54dbcd005c139816ecc19c96a5dc0939de"  # main, 2026-10-23
BUILD = DEV / "build" / "openriglogic"
PY_DEV = DEV / "build" / "py31313" / "tools"
BLENDER_PYTHON = Path("E:/blender-5.3.0-beta/5.3/python/bin/python.exe")
SWIG = DEV / "venv-tools" / "Scripts" / "swig.exe"
CMAKE = Path(
    "C:/Program Files (x86)/Microsoft Visual Studio/2019/BuildTools/Common7/IDE/CommonExtensions/Microsoft/CMake/CMake"
    "/bin/cmake.exe"
)
DIST = Path(__file__).resolve().parent / "dist"
EXT_WHEELS = Path(__file__).resolve().parents[2] / "extension" / "juststage" / "wheels"  # the manifest's `wheels`
PYTHON_VERSION = "3.13.13"
SWIG_VERSION = "4.3.1"  # `.dev/venv-tools/Scripts/python -m pip install swig==4.3.1`


def run(args: list[str | Path]) -> None:
    print("+", " ".join(map(str, args)), flush=True)
    subprocess.run([str(a) for a in args], check=True)


def version() -> str:
    """OpenRigLogic's version: its CMakeLists sets RL_VERSION and gives the project `VERSION ${RL_VERSION}`."""
    import re

    text = (SOURCE / "CMakeLists.txt").read_text(encoding="utf-8")
    found = re.search(r"set\(RL_VERSION\s+([0-9.]+)\)", text)
    if found is None:
        sys.exit(f"{SOURCE / 'CMakeLists.txt'}: no set(RL_VERSION ...)")
    return found.group(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=2, help="parallel compiles (the machine is shared)")
    args = parser.parse_args()
    swig = subprocess.run([str(SWIG), "-version"], capture_output=True, text=True, check=True).stdout
    if f"SWIG Version {SWIG_VERSION}" not in swig:
        sys.exit(f"{SWIG} is not SWIG {SWIG_VERSION}: pip install swig=={SWIG_VERSION} in the tools venv")
    head = subprocess.run(["git", "-C", str(SOURCE), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
    if head.stdout.strip() != COMMIT:
        sys.exit(f"{SOURCE} is at {head.stdout.strip()}, not {COMMIT}")
    run(
        [
            CMAKE,
            "-S",
            SOURCE,
            "-B",
            BUILD,
            "-G",
            "Visual Studio 16 2019",
            "-A",
            "x64",
            f"-DRL_BUILD_PYTHON_WRAPPER={PYTHON_VERSION}",
            f"-DPython3_EXECUTABLE={BLENDER_PYTHON}",
            f"-DPython3_INCLUDE_DIR={PY_DEV / 'include'}",
            f"-DPython3_LIBRARY={PY_DEV / 'libs' / 'python313.lib'}",
            f"-DSWIG_EXECUTABLE={SWIG}",
            "-DREAD_ONLY_SOURCE_TREE=ON",
        ]
    )
    run([CMAKE, "--build", BUILD, "--config", "Release", "--parallel", str(args.jobs)])

    ver = version()
    stage = BUILD / "wheel"
    shutil.rmtree(stage, ignore_errors=True)
    stage.mkdir(parents=True)
    # SWIG's modules and their compiled halves, at the top level: `import dna`, `import riglogic`, as OpenRigLogic's
    # own examples and tests import them
    found = [p for p in BUILD.rglob("*.pyd") if "Release" in p.parts and "wheel" not in p.parts]
    found += [p for p in BUILD.rglob("*.py") if p.name in ("dna.py", "riglogic.py") and "wheel" not in p.parts]
    for path in found:
        shutil.copy2(path, stage / path.name)
    print("packed:", sorted(p.name for p in stage.iterdir()))
    info = stage / f"openriglogic-{ver}.dist-info"
    info.mkdir()
    (info / "METADATA").write_text(
        f"Metadata-Version: 2.1\nName: openriglogic\nVersion: {ver}\nSummary: OpenRigLogic's DNA and RigLogic Python "
        f"bindings, built for Blender {BLENDER_PYTHON.parts[-4]}'s Python {PYTHON_VERSION}\nLicense: MIT\n",
        encoding="utf-8",
    )
    (info / "WHEEL").write_text(
        "Wheel-Version: 1.0\nGenerator: just-stage libs/openriglogic/build.py\nRoot-Is-Purelib: false\n"
        "Tag: cp313-cp313-win_amd64\n",
        encoding="utf-8",
    )
    shutil.copy2(SOURCE / "LICENSE", info / "LICENSE")
    DIST.mkdir(exist_ok=True)
    run([DEV / "venv-tools" / "Scripts" / "wheel.exe", "pack", stage, "--dest-dir", DIST])
    install()
    return 0


def install() -> Path:
    """The wheel into the extension's `wheels/` folder, which its manifest lists (Blender installs it when the
    extension is enabled); returns its path there."""
    wheels = sorted(DIST.glob("openriglogic-*.whl"))
    if not wheels:
        raise SystemExit(f"no wheel in {DIST}; build it first")
    EXT_WHEELS.mkdir(exist_ok=True)
    target = EXT_WHEELS / wheels[-1].name
    shutil.copy2(wheels[-1], target)
    print(f"INSTALLED {target}", flush=True)
    return target


if __name__ == "__main__":
    if "--install" in sys.argv:  # the built wheel into the extension only (no rebuild)
        install()
        sys.exit(0)
    sys.exit(main())
