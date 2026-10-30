# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Bind GNM's part meshes to hm08's helpers with MakeHuman's MHCLO — what MakeClothes does for an asset.

    .dev/venv-tools/Scripts/python tools/bind_parts.py     (after libs/wrap/gnm_to_hm08.py)

Each part (`data/generated/gnm/parts/<part>.obj`, MakeHuman's axes and decimetres) is bound vertex by vertex to the
nearest triangle of the hm08 helper groups `parts.json` names (the eye helpers for an eye; the teeth and tongue
helpers for the teeth), with the head's span references (MPFB2's: x 5399–11998, y 791–881, z 962–5320 — measured on
base.obj as the head's width, height and depth). The `.mhclo` lands beside the part.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "extension"))
from juststage.core import makehuman, mhclo  # noqa: E402

MAKEHUMAN = ROOT / "extension" / "juststage" / "data" / "fetched" / "makehuman"
PARTS = ROOT / "extension" / "juststage" / "data" / "generated" / "gnm" / "parts"
HEAD_SPANS = {"x": (5399, 11998), "y": (791, 881), "z": (962, 5320)}


def read_obj(path: Path) -> tuple[np.ndarray, np.ndarray]:
    lines = path.read_text(encoding="utf-8").splitlines()
    v = np.array([[float(x) for x in line.split()[1:4]] for line in lines if line.startswith("v ")])
    f = [[int(c.split("/")[0]) - 1 for c in line.split()[1:]] for line in lines if line.startswith("f ")]
    return v, np.array(f, dtype=np.int64)


def to_blender(mh_dm: np.ndarray) -> np.ndarray:
    """MakeHuman (x, y, z) decimetres → Blender (x, −z, y) metres."""
    return np.stack([mh_dm[:, 0], -mh_dm[:, 2], mh_dm[:, 1]], axis=1) * makehuman.SCALE_TO_METRES


def triangles(quads: np.ndarray) -> np.ndarray:
    return np.concatenate([quads[:, [0, 1, 2]], quads[:, [0, 2, 3]]])


def main() -> int:
    base_mh, base_faces = read_obj(MAKEHUMAN / "3dobjs" / "base.obj")
    base = to_blender(base_mh)
    groups = makehuman.vertex_groups(MAKEHUMAN / "mesh_metadata" / "basemesh_vertex_groups.json")
    scales = tuple(
        (a, b, float(abs(base_mh[a, axis] - base_mh[b, axis])))
        for (a, b), axis in zip(HEAD_SPANS.values(), (0, 1, 2), strict=True)
    )
    meta = json.loads((PARTS / "parts.json").read_text(encoding="utf-8"))
    report = {}
    for part, info in meta.items():
        helper = np.zeros(len(base), dtype=bool)
        for group in info["bind_to"]:
            helper[groups[group]] = True
        tris = triangles(base_faces[helper[base_faces].all(axis=1)])
        surface = trimesh.Trimesh(base, tris, process=False)

        def closest(points, surface=surface):
            on, _, tri = trimesh.proximity.closest_point(surface, points)
            return on, tri

        asset_mh, _ = read_obj(PARTS / info["obj"])
        asset = to_blender(asset_mh)
        m = mhclo.bind(asset, base, tris, scales, closest)
        m.name, m.obj_file = part, info["obj"]
        m.author, m.licence = "JustStage, from Google's GNM v3.0", "Apache-2.0"
        m.description = f"GNM v3.0 {', '.join(info['gnm_components'])}, bound to hm08's {', '.join(info['bind_to'])}"
        (PARTS / f"{part}.mhclo").write_text(mhclo.write(m), encoding="utf-8")
        error = np.abs(mhclo.fit(mhclo.parse(mhclo.write(m)), base) - asset).max() * 1000.0
        report[part] = {"vertices": int(len(asset)), "round_trip_error_mm": round(float(error), 4)}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
