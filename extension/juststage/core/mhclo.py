# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-FileCopyrightText: MakeHuman Community (the MHCLO format and MPFB2's fit, `fit_clothes_to_human`)
# SPDX-License-Identifier: GPL-3.0-or-later

"""MakeHuman's MHCLO — how every mesh fitted to the base (clothes, eyes, teeth, hair, proxies) follows it
(the spec's item 3; MPFB2's docs/fileformats/mhclo.md), Blender-free.

Reading follows the documented rules (sections end at a blank line or a non-numeric first word; `material` and
`vertexboneweights…` lines may sit inside the vertex block). The documented reader defects (a one-word `name` and
`author`, the `license` substring test) are not reproduced: names keep the whole line, licences are read as written.
Offsets are stored in MakeHuman's axes (Y up, decimetres) and turned into Blender's, (x, −z, y), on fit — as MPFB2's
`Mhclo.load()` and `fit_clothes_to_human()` do, with each axis scaled by the base's measured `x/y/z_scale` spans.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Mhclo:
    name: str = "imported_cloth"
    uuid: str = ""
    obj_file: str = ""
    material: str = ""
    author: str = "unknown"
    licence: str = "CC0"
    description: str = "no description"
    z_depth: int = 50
    #: (vertex a, vertex b, reference distance in MakeHuman units) per axis, MakeHuman's axes
    x_scale: tuple[int, int, float] | None = None
    y_scale: tuple[int, int, float] | None = None
    z_scale: tuple[int, int, float] | None = None
    #: per asset vertex: base vertex indices (3), weights (3), offset (3, MakeHuman axes and units)
    refs: np.ndarray = field(default_factory=lambda: np.zeros((0, 3), dtype=np.int64))
    weights: np.ndarray = field(default_factory=lambda: np.zeros((0, 3)))
    offsets: np.ndarray = field(default_factory=lambda: np.zeros((0, 3)))
    delete_verts: list[int] = field(default_factory=list)


def _numeric(word: str) -> bool:
    try:
        float(word)
    except ValueError:
        return False
    return True


def parse(text: str) -> Mhclo:
    m = Mhclo()
    refs, weights, offsets = [], [], []
    section = None
    for raw in text.splitlines():
        words = raw.split()
        if not words:
            section = None
            continue
        key = words[0]
        if key == "#":
            if len(words) > 2:
                head = words[1].lower().rstrip(":")
                rest = raw.split(None, 2)[2].strip()
                if head == "author":
                    m.author = rest
                elif head in ("license", "licence"):
                    m.licence = rest
                elif head == "description":
                    m.description = rest
            continue
        if key.startswith("#"):
            continue
        if key == "material":
            m.material = words[1]
            continue
        if key.startswith("vertexboneweights"):
            continue
        if section == "verts":
            if not _numeric(key):
                section = None
                continue
            if len(words) == 1:
                v = int(words[0])
                refs.append((v, v, v))
                weights.append((1.0, 0.0, 0.0))
                offsets.append((0.0, 0.0, 0.0))
            elif len(words) >= 9:
                refs.append(tuple(int(w) for w in words[0:3]))
                weights.append(tuple(float(w) for w in words[3:6]))
                offsets.append(tuple(float(w) for w in words[6:9]))
            else:
                raise ValueError(f"MHCLO vertex line with {len(words)} fields: {raw!r}")
            continue
        if section == "delete":
            if not _numeric(key):
                section = None
                continue
            i = 0
            while i < len(words):
                if i + 2 < len(words) and words[i + 1] == "-":
                    m.delete_verts.extend(range(int(words[i]), int(words[i + 2]) + 1))
                    i += 3
                else:
                    m.delete_verts.append(int(words[i]))
                    i += 1
            continue
        if key == "verts" and len(words) > 1:
            section = "verts"
        elif key == "delete_verts":
            section = "delete"
        elif key == "name":
            m.name = raw.split(None, 1)[1].strip()
        elif key == "uuid":
            m.uuid = words[1]
        elif key == "obj_file":
            m.obj_file = raw.split(None, 1)[1].strip()
        elif key == "z_depth":
            m.z_depth = int(words[1])
        elif key in ("x_scale", "y_scale", "z_scale"):
            setattr(m, key, (int(words[1]), int(words[2]), float(words[3])))
    m.refs = np.array(refs, dtype=np.int64).reshape(-1, 3)
    m.weights = np.array(weights, dtype=np.float64).reshape(-1, 3)
    m.offsets = np.array(offsets, dtype=np.float64).reshape(-1, 3)
    return m


def write(m: Mhclo) -> str:
    """MPFB2's `write_mhclo` layout (its MakeClothes writer)."""
    lines = ["# MHCLO asset for MakeHuman and MPFB, written by JustStage"]
    lines += [f"# author {m.author}", f"# license {m.licence}", f"# description {m.description}"]
    lines += ["basemesh hm08", f"name {m.name}"]
    if m.uuid:
        lines.append(f"uuid {m.uuid}")
    lines.append(f"obj_file {m.obj_file}")
    if m.material:
        lines.append(f"material {m.material}")
    for axis in ("x_scale", "y_scale", "z_scale"):
        ref = getattr(m, axis)
        if ref:
            lines.append(f"{axis} {ref[0]} {ref[1]} {ref[2]:.4f}")
    lines += [f"z_depth {m.z_depth}", "verts 0"]
    for (a, b, c), (wa, wb, wc), (dx, dy, dz) in zip(m.refs, m.weights, m.offsets, strict=True):
        if wa == 1 and wb == 0 and wc == 0 and dx == dy == dz == 0:
            lines.append(f"{a}")
        else:
            lines.append(f"{a} {b} {c} {wa:.4f} {wb:.4f} {wc:.4f} {dx:.4f} {dy:.4f} {dz:.4f}")
    if m.delete_verts:
        lines += ["", "delete_verts", " " + " ".join(str(v) for v in sorted(set(m.delete_verts)))]
    return "\n".join(lines) + "\n"


def _sizes(m: Mhclo, base: np.ndarray, fallback: float) -> tuple[float, float, float]:
    """MPFB2's x/y/z sizes: the base's current span between the reference vertices over the authored span. `base`
    is in Blender's axes, so MakeHuman's y is Blender's z and MakeHuman's z is Blender's y."""
    if not m.x_scale:
        return fallback, fallback, fallback
    x = abs(base[m.x_scale[0], 0] - base[m.x_scale[1], 0]) / m.x_scale[2]
    y = abs(base[m.y_scale[0], 2] - base[m.y_scale[1], 2]) / m.y_scale[2]
    z = abs(base[m.z_scale[0], 1] - base[m.z_scale[1], 1]) / m.z_scale[2]
    return x, y, z


def fit(m: Mhclo, base: np.ndarray, fallback_scale: float = 0.1) -> np.ndarray:
    """Asset vertex positions for a base shape (`base`: N×3, Blender axes and units)."""
    x_size, y_size, z_size = _sizes(m, base, fallback_scale)
    # MakeHuman (x, y, z) → Blender (x, −z, y); each component scaled by its own MakeHuman axis span
    offset = np.stack([m.offsets[:, 0] * x_size, -m.offsets[:, 2] * z_size, m.offsets[:, 1] * y_size], axis=1)
    return (base[m.refs] * m.weights[:, :, None]).sum(axis=1) + offset


def bind(
    asset: np.ndarray,
    base: np.ndarray,
    triangles: np.ndarray,
    scales: tuple[tuple[int, int, float], tuple[int, int, float], tuple[int, int, float]],
    closest,
) -> Mhclo:
    """An MHCLO binding of `asset` vertices (Blender axes) to the nearest of `triangles` on `base` — what MakeClothes
    does. `closest(points) -> (point_on_surface, triangle_index)` is the caller's surface query (trimesh's, or
    Blender's BVH). `scales` are MakeHuman-axis (a, b, span) references measured on `base`."""
    m = Mhclo(x_scale=scales[0], y_scale=scales[1], z_scale=scales[2])
    on, tri = closest(asset)
    corners = triangles[tri]
    a, b, c = (base[corners[:, i]] for i in range(3))
    # barycentric weights of the foot point in its triangle
    v0, v1, v2 = b - a, c - a, on - a
    d00, d01, d11 = (v0 * v0).sum(1), (v0 * v1).sum(1), (v1 * v1).sum(1)
    d20, d21 = (v2 * v0).sum(1), (v2 * v1).sum(1)
    denom = np.where(np.abs(d00 * d11 - d01 * d01) < 1e-20, 1e-20, d00 * d11 - d01 * d01)
    wb = (d11 * d20 - d01 * d21) / denom
    wc = (d00 * d21 - d01 * d20) / denom
    m.refs = corners.astype(np.int64)
    m.weights = np.stack([1.0 - wb - wc, wb, wc], axis=1)
    x_size, y_size, z_size = _sizes(m, base, 0.1)
    rest = asset - on  # Blender axes, Blender units
    # back into MakeHuman's axes and the reference spans: Blender (x, y, z) = (mx·xs, −mz·zs, my·ys)
    m.offsets = np.stack([rest[:, 0] / x_size, rest[:, 2] / y_size, -rest[:, 1] / z_size], axis=1)
    return m
