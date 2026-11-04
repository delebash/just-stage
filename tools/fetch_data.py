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
            "src/mpfb/data/node_trees/procedural_eyes.json",  # its procedural eye ("EnhancedEye", modules/head/eyes.py)
            "src/mpfb/data/textures/mpfb_*.jpg",  # its region masks on hm08's UVs: lips, areolae, nails, ... (skin)
        ],
        "extra": {"LICENSE.md": "LICENSE.md"},
    },
    "ict": {
        "repo": "USC-ICT/ICT-FaceKit",
        "commit": "da5f95a607f5e6b37755b38d3385d7f2853732e5",  # master, 2020-12-01 (its last push)
        "strip": "FaceXModel/",
        "licence": "MIT (ICT-FaceKit's LICENSE)",
        # its neutral face: the eye occlusion and lacrimal-fluid strips the app's eye layers are made from
        "include": ["FaceXModel/generic_neutral_mesh.obj"],
        "extra": {"LICENSE": "LICENSE"},
    },
}


#: MakeHuman's asset packs (static.makehumancommunity.org/assets/assetpacks.html — the functional packs: "The assets are
#: shared under CC0."), unpacked into MakeHuman's own data layout under extension/juststage/data/fetched/makehuman/.
FU = "targets/faceunits/"  # Faceunits 01's folder inside its zip
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
    "faceunits01": {
        "urls": [  # the functional packs' two mirrors (RESEARCH ~1798: "faceunits01.zip" 257,821 bytes)
            "https://files2.makehumancommunity.org/functional/faceunits01.zip",
            "https://files.makehumancommunity.org/functional/faceunits01.zip",
        ],
        "sha256": "d113107bd7eb59f3af4df6fc0ec29bfcc593f496d0b336aec14f086a80ce7146",  # the zip of 2026-11-03
        "files": {
            "packs/faceunits01.json": "fd647a088691ddd9193ce9600df3377bb9ccf69c2904f0a7773a3c246d234c18",
            FU + "browDownLeft.target": "095b8e45fc918aa17f845ea6490561644e10d83d3a5aa42790488a6806b2ccf1",
            FU + "browDownRight.target": "f092d3c8446b9e1bdf523b039465796e629b6cf9e20ac3f8fb853f98e890f105",
            FU + "browInnerUp.target": "84c8be8c1cade46a51486786244c1a80dfbf6e1915bf1f5a72b74ef8eb951f6d",
            FU + "browOuterUpLeft.target": "9821d5a8279c0ba8751d4595e0333ef5d1a041fad6d85ffffdae7b5044908fa0",
            FU + "browOuterUpRight.target": "770fd5cb608adbeb778e17ab39e085f9472191d65056cebe0df5f3e4d6cab364",
            FU + "cheekPuff.target": "fb99e2ab7e923be84cf2387a10d198d410b6b4135a14d58a1111b55edd624894",
            FU + "cheekSquintLeft.target": "2ec68e1aca9ecd24019db58af53d7998f10e4964dda2729fd0f319597f734d75",
            FU + "cheekSquintRight.target": "7daf855b7d23d2b95ae4e75ed0994b4951d8d9ec6d82a9a6aec8742df033bdbc",
            FU + "eyeBlinkLeft.target": "53d35e0a8357140d4e37277a674f211bdaf97be011b61cfcdff618f0bfea0ec8",
            FU + "eyeBlinkRight.target": "00d159a70fad650b336eb6f739a1a6a47f916da4331ef9848fb0eef989ca5cc5",
            FU + "eyeLookDownLeft.target": "df824a8a46447e95bc465b198ea9e49f10db8429c94531568dfbc512811f3f07",
            FU + "eyeLookDownRight.target": "568da82dd1a31eb5eb6a46025d56dbf13e6e9a9cb7950f0546111af0781d3f4c",
            FU + "eyeLookInLeft.target": "d0774cb36def532a3be8576fc62cc23ad10bcc6f668365fcf387fe52a83155a0",
            FU + "eyeLookInRight.target": "de9123797cbca735fa2d12853723dc1eb88d9ad435033465b713dc5e64511a28",
            FU + "eyeLookOutLeft.target": "9dd01ff6424676eb3abd4cfcd13ecfa3ffe87ea4feb8eeb252fd06aeb441be1e",
            FU + "eyeLookOutRight.target": "c25852238d3833d9f8977d7fac66942f810e4a24b0c90f584894d3c76c626ae7",
            FU + "eyeLookUpLeft.target": "3c8b3e2ac2bb82561f72deb94bb3d58e3876675cd3b87262967df812bcd6acb9",
            FU + "eyeLookUpRight.target": "4b91cf96e42c527179e8b7f60f0c69ae9d3dec0abe4ce475ceca0c95f8cd9cc0",
            FU + "eyeSquintLeft.target": "4f7298dec327d91f53fe9525bf07ef17cf02776c4228da8baaef4b19079fd311",
            FU + "eyeSquintRight.target": "f8563d6a34269f97110b1b0513b79bf98153125a7d179135f1ef206d0b0f2504",
            FU + "eyeWideLeft.target": "40c1f1ba32e511609828e1da2280158db4e515fa0294892c08b4a6a863f08fab",
            FU + "eyeWideRight.target": "be06515fd73d078639871d33ae4770a61bee41ffacd06d619913319054832839",
            FU + "jawForward.target": "c87b4893f82e6908601cb766e5362d0534a73310f1c072ea4041ad2f1cc9d39e",
            FU + "jawLeft.target": "21cf8350d2310e237ac0cf941a1928f67589c9166d71ae254d3a0d1079f25426",
            FU + "jawOpen.target": "2439e703e434f999b58a1d26cffdb6b2fd5f30941b8ff19cac70b75392d4de6f",
            FU + "jawRight.target": "8473c887d979b98b4d5f37f034028a246d03131d6350ce76a338951f99dd5794",
            FU + "mouthClose.target": "965135637c90019c9f91ddd7540405124da7274b3a5b6b6a2201fa97956773f5",
            FU + "mouthDimpleLeft.target": "8d36c4877b39adffefd0f29ec19e9aae56ab3fe69733bf569b9c8c5c900062f7",
            FU + "mouthDimpleRight.target": "3aa3934cc294b9c6666ab9f6034b569ea9cc111cf7342aa7442918f33fc82ab0",
            FU + "mouthFrownLeft.target": "39d0c7cc1305ac62bdf989522f00f1b820ade8e1762a738f7398926bf6f91cd4",
            FU + "mouthFrownRight.target": "a14b45427d3f78ddb8a05604b6c353bddcda49376588097809797c4a51714767",
            FU + "mouthFunnel.target": "b273e870938c798357b314dac22f388b4030d9f4b782fd2179991c9f7831d32a",
            FU + "mouthLeft.target": "0a90cd34d70f1b858d029189ed00a134566053a92d78e681b75c46027ed9deeb",
            FU + "mouthLowerDownLeft.target": "493600ee77f3c8f06113d49e7b6d9cda75fb1fe9dfd9df602e7f90f55b5477eb",
            FU + "mouthLowerDownRight.target": "08be0c2158339981e6bf9533666c734cf030c08fa7bed2a931aa965d01aaff44",
            FU + "mouthPressLeft.target": "00613a25981f172decf2f95f0871dda1cb775bfcba65088e9e0978b441ca5b5a",
            FU + "mouthPressRight.target": "27d1cf1610d2565be0fb99e1ff2e96dc8e58531e05309a69f961a638fa1a39a2",
            FU + "mouthPucker.target": "3d90b495088fac29e5db4022842860d0b0f10f875e201670d559e37db4da67ae",
            FU + "mouthRight.target": "170b71c2fe038248e7edd50e417dda4096f3cf620fec75a0f5b66b4c04edd69f",
            FU + "mouthRollLower.target": "69cff9c045c3c461eee4be855883c2f1b79ddb645ca7bf499c35a95b3adbb055",
            FU + "mouthRollUpper.target": "c5965de076f01d5b227d28d233be58e40180ed63a302fb9869e74ab6f93d1fb7",
            FU + "mouthShrugLower.target": "0948e2b311179b563692c24d64435e1770bb9e6c60bd8df63ca284d349a57739",
            FU + "mouthShrugUpper.target": "2991fcd27cf7ca215e222d30c31a23c79c6ee744a59501e336ea063a280b5b47",
            FU + "mouthSmileLeft.target": "11cabf2fa6f9664c4d0b9f8f0cadaf4b2a1a9625b72c7593262465ce8d4cb9a2",
            FU + "mouthSmileRight.target": "70578981892db13c02512455583c2f9743683d5c571c1e2624b09638cf37bedd",
            FU + "mouthStretchLeft.target": "0b3622bfc1d922c9d686523800babd217e06d865338cb979485c2b22efd63c4d",
            FU + "mouthStretchRight.target": "b866286fc0b607b07c6191c36c458c6f197ad19ce26c66218b8df37c1a283b38",
            FU + "mouthUpperUpLeft.target": "db4e4f0d22b5488c139a6a6434e0ba1599e30211fbd577796b071a409a19b075",
            FU + "mouthUpperUpRight.target": "5919a0772f665cb275097e0d291d3e7a9269ee2ffd3a4340e8f1c3093b78e6c4",
            FU + "noseSneerLeft.target": "c205f9972e41f5147525b74d543b7617e51bba80dbfe601456711cb2f265b9c8",
            FU + "noseSneerRight.target": "51039beca77f3ccaf505645ec9db19438b96102ddd3fba6cbd72ec9280dee685",
            FU + "tongueOut.target": "d153f31b458c309671cab9222652d60d238218561695dfc8b3678ab3e8482e19",
        },
        "dest": FETCHED / "makehuman",
        "licence": "CC0-1.0 (MakeHuman's Faceunits 01: 52 ARKit face units for hm08 by Mika Suominen)",
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
