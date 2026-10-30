# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fetch the open data JustStage builds on, at pinned versions, checked file by file.

    python tools/fetch_data.py            # fetch what is missing or changed
    python tools/fetch_data.py --check    # verify only

MakeHuman's CC0 assets come from MPFB2's repository at a pinned commit (the spec's item 3: "build on MPFB2's
formats"). Each file is checked against the git blob hash GitHub's tree lists for that commit, so a fetched file is
byte-for-byte the pinned one. Files land in extension/juststage/data/fetched/ (not committed; REUSE.toml labels them).
MakeHuman's CC0 asset packs (zips on its file servers) are checked by the zip's SHA-256, and the files taken from them
by their own. The offline tools' inputs (Google's GNM model for libs/wrap/gnm_to_hm08.py) are checked against their
published SHA-256 and kept in .dev/cache/.
"""

from __future__ import annotations

import fnmatch
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FETCHED = ROOT / "extension" / "juststage" / "data" / "fetched"

SOURCES = {
    "makehuman": {
        "repo": "makehumancommunity/mpfb2",
        "commit": "6ff1eb358f6c1959ced77e79e6dd2406d9a71f49",  # master, 2026-10-29
        "strip": "src/mpfb/data/",
        "licence": "CC0-1.0 (MPFB2's bundled assets — its LICENSE.md, part C)",
        "include": [
            "src/mpfb/data/3dobjs/base.obj",
            "src/mpfb/data/mesh_metadata/*",
            "src/mpfb/data/targets/*.json",
            "src/mpfb/data/targets/**/*.json",
            "src/mpfb/data/targets/**/*.target.gz",
            "src/mpfb/data/rigs/standard/rig.game_engine*.json",
            "src/mpfb/data/rigs/standard/weights.game_engine*.json",
            "src/mpfb/data/expressions/*",
            "src/mpfb/data/uv_layers/*",
        ],
        "extra": {"LICENSE.md": "LICENSE.md"},
    },
}


#: MakeHuman's asset packs (static.makehumancommunity.org/assets/assetpacks.html — the functional packs: "The assets are
#: shared under CC0."), unpacked into MakeHuman's own data layout under extension/juststage/data/fetched/makehuman/.
PACKS = {
    "haireditor": {
        "urls": [  # the pack page's two mirrors
            "https://files2.makehumancommunity.org/functional/haireditor.zip",
            "https://files.makehumancommunity.org/functional/haireditor.zip",
        ],
        "sha256": "e47ade8e58e31c12c1331fe96801059cb1bf0178f064b9bd4a63f343bcecbe72",  # the zip of 2026-10-24
        "files": {
            "hair/haireditor/hair.blend": "8566a128ade918c507fabdca883c49fac7d744fe840b9eb28a98917b5ad3f080",
        },
        "dest": FETCHED / "makehuman",
        "licence": "CC0-1.0 (MakeHuman's hair-editor pack: hair.blend by Tomáš Klecer)",
    },
}


def fetch_pack(name: str, spec: dict, check_only: bool) -> int:
    dest: Path = spec["dest"]
    wanted = {m: h for m, h in spec["files"].items() if not _has(dest / m, h)}
    if not wanted:
        print(f"{name}: present")
        return 0
    if check_only:
        for member in wanted:
            print(f"missing or changed: {dest / member}")
        return len(wanted)
    data = None
    for url in spec["urls"]:
        try:
            data = _get(url, timeout=600)
            break
        except OSError as e:
            print(f"{name}: {url}: {e}")
    if data is None:
        sys.exit(f"{name}: no mirror answered")
    if hashlib.sha256(data).hexdigest() != spec["sha256"]:
        sys.exit(f"{name}: the zip does not match its pinned SHA-256 (the pack changed upstream)")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for member, sha in wanted.items():
            body = z.read(member)
            if hashlib.sha256(body).hexdigest() != sha:
                sys.exit(f"{name}: {member} does not match its pinned SHA-256")
            (dest / member).parent.mkdir(parents=True, exist_ok=True)
            (dest / member).write_bytes(body)
    print(f"{name}: fetched {len(wanted)} file(s)")
    return 0


def _has(path: Path, sha256: str) -> bool:
    return path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == sha256


#: Small published tables the add-on computes from, checked by SHA-256 (extension/juststage/data/fetched/optics/).
TABLES = {
    "hemoglobin": {
        "url": "https://omlc.org/spectra/hemoglobin/summary.html",
        "sha256": "c5b3a312f3c8e135bf69845ba11afa94d92db0a3f784d344d92afcf9dc290c66",
        "dest": FETCHED / "optics" / "prahl_hemoglobin.html",
        "licence": "Scott Prahl, OMLC, 1998 (molar extinction of HbO2 and Hb) — no licence stated; cited",
    },
    "cie_xyz_1931_2deg": {
        "url": "https://files.cie.co.at/Publications-datasets/CIE_xyz_1931_2deg.csv",
        "sha256": "fa663e3535a7e0763a745993a1f0a192eb0275ac46ad2d1befd7626841e713c1",
        "dest": FETCHED / "optics" / "CIE_xyz_1931_2deg.csv",
        "licence": "CIE dataset (CIE 1931 2° colour-matching functions) — no licence stated on its CIE page; cited",
    },
    "cie_d65": {
        "url": "https://files.cie.co.at/Publications-datasets/CIE_std_illum_D65.csv",
        "sha256": "e76f210bffff3d552ef7113025da5f325d5dfec200dd4b878b1a2f3a507032cb",
        "dest": FETCHED / "optics" / "CIE_std_illum_D65.csv",
        "licence": "CIE dataset (CIE standard illuminant D65) — no licence stated on its CIE page; cited",
    },
}

#: Inputs of the offline tools (libs/, tools/), checked by SHA-256 and kept out of the add-on (.dev/cache/).
TOOL_INPUTS = {
    "nist_skin": {
        "url": "https://opendata.nist.gov/1832_Data_JResNIST_skinrefl%20v3.txt",
        "sha256": "ce9aac735d9d83b4b874b98d45f1ebda682cdc0e652f804efe00ab2fce0c25d9",
        "dest": ROOT / ".dev" / "cache" / "nist" / "1832_Data_JResNIST_skinrefl v3.txt",
        "licence": "NIST open data (public domain) — Cooksey, Allen & Tsai 2017, doi:10.18434/M38597",
    },
    "gnm": {
        "url": "https://huggingface.co/google/gnm-v3/resolve/main/v3_0/gnm_head.npz",
        "sha256": "61d78bbfb4ad8e0b38495804a4caef3214d3df00f8c3f68761e63b41ce3747eb",  # v3_0/checksums.sha256
        "dest": ROOT / ".dev" / "cache" / "gnm" / "v3_0" / "gnm_head.npz",
        "licence": "Apache-2.0 (google/gnm-v3)",
    },
}


def fetch_tool_input(name: str, spec: dict, check_only: bool) -> int:
    dest: Path = spec["dest"]
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() == spec["sha256"]:
        print(f"{name}: present")
        return 0
    if check_only:
        print(f"missing or changed: {dest}")
        return 1
    data = _get(spec["url"])
    if hashlib.sha256(data).hexdigest() != spec["sha256"]:
        sys.exit(f"{name}: {spec['url']} does not match its published SHA-256")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print(f"{name}: fetched")
    return 0


def _get(url: str, timeout: int = 60) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "juststage-fetch"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def fetch(name: str, spec: dict, check_only: bool) -> int:
    out = FETCHED / name
    tree = json.loads(_get(f"https://api.github.com/repos/{spec['repo']}/git/trees/{spec['commit']}?recursive=1"))
    if tree.get("truncated"):
        sys.exit(f"{name}: GitHub truncated the tree listing")
    blobs = {b["path"]: b["sha"] for b in tree["tree"] if b["type"] == "blob"}
    wanted = {p: p.removeprefix(spec["strip"]) for p in blobs if _matches(p, spec["include"])}
    wanted.update(spec.get("extra", {}))
    raw = f"https://raw.githubusercontent.com/{spec['repo']}/{spec['commit']}/"
    fetched = bad = 0
    for source, local in sorted(wanted.items()):
        target = out / local
        if target.exists() and _blob_sha(target.read_bytes()) == blobs[source]:
            continue
        if check_only:
            print(f"missing or changed: {target}")
            bad += 1
            continue
        data = _get(raw + source)
        if _blob_sha(data) != blobs[source]:
            sys.exit(f"{name}: {source} does not match its pinned hash")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        fetched += 1
    (out / "SOURCE.json").write_text(
        json.dumps(
            {"repo": spec["repo"], "commit": spec["commit"], "licence": spec["licence"], "files": len(wanted)},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"{name}: {len(wanted)} files, {fetched} fetched, {bad} missing"
        if check_only or fetched
        else f"{name}: {len(wanted)} files, all present"
    )
    return bad


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    bad = sum(fetch(n, s, check_only) for n, s in SOURCES.items())
    bad += sum(fetch_pack(n, s, check_only) for n, s in PACKS.items())
    bad += sum(fetch_tool_input(n, s, check_only) for n, s in {**TABLES, **TOOL_INPUTS}.items())
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
