# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The skin's pore tile (the material's pore relief, `modules/skin/maps.py` `pore_relief`), from a clean scanned cheek
- CC5's way: a tiling micro-detail with no hair (its micro normal; docs/plans/2026-11-06-inputs-audit.md row 9: our
former tile, the Lee Perry-Smith scan's cheek, carried his stubble's streaks and seams).

    .dev/venv-rdf/Scripts/python -I tools/face_test/pore_tile.py [ten24 | SCAN ...]

The default, `ten24`: Ten24's scanned relief normals on a clean upper cheek (below). Or for each scan named (e.g. the
women's HSRD scans - no stubble): the cheek found on our head's own geometry (below and
beside each eye), the largest square of the scan's baked skin there with no strand in it (hair.py), its pores as height
(the high-passed log brightness - a pore is a shadowed pit), made to tile by Moisan's periodic component (as
tools/gate/relief_tiles.py). The scan whose square is largest wins; written to
`extension/juststage/data/generated/skin/pores.png` (16-bit grey, 0.5 = the surface) and `pores.json` (its size in mm,
source, licence)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SCANS = ROOT / ".dev" / "facetest" / "scans"
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "skin"
PX_PER_MM = 6.0  # the HeadTile bake's density on the face (skin_base.py: ~6 texels a mm)
HIGH_PASS_MM = 1.5  # pores and fine lines (relief_tiles.py's band)
MIN_SIDE = 96  # texels (16 mm): a smaller clean square is no tile
DEFAULT = ("hsr0027", "hsr0028", "hsr0015", "hsr0102", "hsr0112", "hsr0161")


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hair = _module("hair", Path(__file__).with_name("hair.py"))
skin_base = _module("skin_base", Path(__file__).with_name("skin_base.py"))
scan_list = _module("scan_list", Path(__file__).with_name("scan_list.py"))


def periodic(u: np.ndarray) -> np.ndarray:
    """Moisan's periodic component (tools/gate/relief_tiles.py's): tiles without a seam."""
    h, w = u.shape
    v = np.zeros_like(u)
    v[0, :] += u[-1, :] - u[0, :]
    v[-1, :] += u[0, :] - u[-1, :]
    v[:, 0] += u[:, -1] - u[:, 0]
    v[:, -1] += u[:, 0] - u[:, -1]
    denom = 2 * np.cos(2 * np.pi * np.arange(w) / w)[None, :] + 2 * np.cos(2 * np.pi * np.arange(h) / h)[:, None] - 4
    denom[0, 0] = 1.0
    smooth = np.fft.fft2(v) / denom
    smooth[0, 0] = 0.0
    return u - np.real(np.fft.ifft2(smooth))


def cheeks(size: int) -> np.ndarray:
    """Texels on our head's cheeks: 20-45 mm below an eye's centre, within 15 mm of its column, at the front."""
    up = _module("up", ROOT / "extension" / "juststage" / "core" / "uv_projection.py")
    e = np.load(SCANS / "head_export.npz")
    (pts,), covered = up.raster_uv(e["tri_uv"], [e["co"][e["tris"]].astype(np.float32)], size)
    zone = np.zeros(pts.shape[:2], bool)
    for eye in (e["eye_left"], e["eye_right"]):
        d = pts - np.asarray(eye, np.float32)
        zone |= (np.abs(d[..., 0]) < 0.015) & (d[..., 2] < -0.020) & (d[..., 2] > -0.045) & (d[..., 1] < 0.02)
    return zone & covered


def largest_square(ok: np.ndarray) -> tuple[int, int, int]:
    """(y, x, side) of the largest all-True square (the classic dynamic programme)."""
    h, w = ok.shape
    best = (0, 0, 0)
    prev = np.zeros(w + 1, np.int32)
    for y in range(h):
        cur = np.zeros(w + 1, np.int32)
        row = ok[y]
        for x in np.flatnonzero(row):
            cur[x + 1] = min(prev[x], prev[x + 1], cur[x]) + 1
            if cur[x + 1] > best[2]:
                best = (y - cur[x + 1] + 1, x - cur[x + 1] + 1, int(cur[x + 1]))
        prev = cur
    return best


def tile_for(name: str, zone_cache: dict) -> tuple[np.ndarray, dict] | None:
    d = SCANS / name
    srgb = cv2.imread(str(d / "bake_colour.png"))[..., ::-1].astype(np.float32) / 255.0
    size = srgb.shape[0]
    if size not in zone_cache:
        zone_cache[size] = cheeks(size)
    cover = cv2.imread(str(d / "bake_cover.png"), 0) > 127
    skin = cv2.resize(cv2.imread(str(d / "skin.png"), 0), (size, size), interpolation=cv2.INTER_LINEAR) > 127
    ok = zone_cache[size] & cover & skin
    ok &= ~(cv2.dilate(hair.mask(srgb, ok).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)  # no strand near it
    ys, xs = np.nonzero(ok)
    if not len(ys):
        return None
    y0, x0 = ys.min(), xs.min()
    sub = ok[y0 : ys.max() + 1, x0 : xs.max() + 1]
    y, x, side = largest_square(sub)
    if side < MIN_SIDE:
        print(f"{name}: the largest clean cheek square is {side} texels - too small")
        return None
    y, x = y + y0, x + x0
    lum = np.maximum(skin_base.linear(srgb[y : y + side, x : x + side]) @ hair.LUMA, 1e-4)
    log = np.log(lum).astype(np.float32)
    hp = log - cv2.GaussianBlur(log, (0, 0), HIGH_PASS_MM * PX_PER_MM / 2.0, borderType=cv2.BORDER_REFLECT)
    t = periodic(hp.astype(np.float64))
    t = (t - t.mean()) / (4.0 * t.std() + 1e-12)
    tile = np.clip(t + 0.5, 0.0, 1.0)
    info = {"size_mm": side / PX_PER_MM, "px": side, "scan": name, "crop_headtile": [int(x), int(y), side],
            "source": scan_list.SCANS[name]["credit"], "method": "high-passed log brightness (pores as pits), Moisan's "
            "periodic component; tools/face_test/pore_tile.py", "strands_in_crop": 0}  # fmt: skip
    print(f"{name}: a clean cheek square of {side} texels ({side / PX_PER_MM:.0f} mm) at {x},{y}; spread {hp.std():.4f}")
    return tile, info


#: Ten24's crops (x, y, side on Level_01's 8K), by place. The upper cheek (2026-11-06): between the lid's creases and
#: the stubble, no strand in its colour (a crop 25 texels higher kept the lower lid's creases as streaks, lower ones
#: reach the stubble). The forehead (the shipped one since 2026-11-08): measured against HD Aaron (DISTS excess over
#: his own, `tools/gate/factors.py poretile*ten24_forehead`, 2026-11-08) better or equal everywhere - forehead 0.0359
#: -> 0.0286, nose 0.0785 -> 0.0737, torso 0.0493 -> 0.0310, hand and cheek within noise; the same size (154 px)
TEN24_CROPS = {"forehead": (6110, 6220, 170), "upper cheek": (5820, 6615, 170)}
TEN24_PLACE = "forehead"


def main(names) -> int:
    if names == ["ten24"]:
        tile, info = ten24(*TEN24_CROPS[TEN24_PLACE], place=TEN24_PLACE)
        return _write(tile, info)
    cache: dict = {}
    found = [r for r in (tile_for(n, cache) for n in names) if r is not None]
    if not found:
        print("no scan has a clean cheek square")
        return 1
    return _write(*max(found, key=lambda r: r[1]["px"]))


def _write(tile, info) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / "pores.png"), np.round(tile * 65535).astype(np.uint16))
    (OUT / "pores.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(f"wrote {OUT / 'pores.png'} from {info['scan']} ({info['size_mm']:.0f} mm)")
    return 0




#: Ten24's sample scan (ten24.info/sample-scan: "Feel free to use this scan as you wish for both commercial and personal
#: projects. All we ask is that you provide us with a credit wherever it's used" - the page as downloaded:
#: .dev/downloads/ten24_sample/sample-scan-page-2026-11-04.html): its finest relief normals (Level_01, 8K) on the upper
#: cheek - a scanned pore network (rec 18's contenders, docs/plans/2026-11-04-realism.md: "a clean pore-scale
#: network"), relief as relief (the women's colour crops above give pores as shading, 20 mm at most).
TEN24 = ROOT / ".dev" / "downloads" / "ten24_sample" / "x" / "OBJ Package"
TEN24_PX_PER_MM = 4.6  # its density on the face (relief_tiles.py: eye to mouth ~300 texels ~ 65 mm)


def ten24(x: int, y: int, side: int, place: str = "upper cheek") -> tuple[np.ndarray, dict] | None:
    relief = _module("relief_tiles", ROOT / "tools" / "gate" / "relief_tiles.py")
    colour = relief._ffmpeg_crop(TEN24 / "Colour Maps" / "JPG" / "Colour_8k.jpg", x, y, side)
    strands = int(hair.mask(colour.astype(np.float32)).sum())  # hair in the colour over the same texels
    normals = relief._ffmpeg_crop(TEN24 / "Normal Maps" / "Level_01_Normal.PSD", x, y, side)
    height = relief.height_from_normals(normals, HIGH_PASS_MM * TEN24_PX_PER_MM / 2.0)
    tile = relief.fine_tile(height, TEN24_PX_PER_MM)
    info = {"size_mm": tile.shape[0] / TEN24_PX_PER_MM, "px": tile.shape[0], "scan": "ten24",
            "crop_level01_8k": [x, y, side], "strands_in_colour_crop": strands,
            "source": f"Ten24 sample scan (ten24.info/sample-scan), Level_01_Normal.PSD, {place}",
            "licence": "Ten24: free for commercial and personal projects with a credit (page saved 2026-11-04)",
            "method": "Frankot-Chellappa height from the normals, 1.5 mm high-pass, Moisan's periodic component"}
    print(f"ten24 at {x},{y} ({side}): {strands} strand texels in the colour")
    return tile, info


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["ten24"]))
