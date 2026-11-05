# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The skin's microrelief as a tileable height tile, generated - rec 18's graph-based contender (the realism brief
§6.18; the method ranked first in `docs/plans/2026-10-30-research-skin-detail-shading.md` §2.2): Weiss, Moulin,
Chandran, Zoss, Gotardo, Bradley, "Graph-based synthesis for skin micro wrinkles", SGP 2023 - pores are a graph's
nodes, furrows run along its edges, deeper where an edge follows the skin's line direction, and the graph is drawn
into a height map with a furrow profile and a pore profile. Here the furrows are the walls of the nodes' Voronoi cells
(the plateaus between the lines, domed), stretched along the line direction; pores sit on wall junctions. NOT STANDARD: our own code of a published method (no code
was released); the user's standing word on researched methods (2026-10-17).

Why: the part-by-part gate (`docs/gate/2026-11-05/report.md`) measured that the finest band of HD Aaron's cheek - half
of it missing on ours - is his micro-normal, a tile of domed polygonal cells about 0.2 mm across with fine furrows.

    .dev/venv-tools/Scripts/python -I tools/make_microrelief.py [OUT.png] [--tile-mm 10] [--px 2048] [--seed 2]
        [--spacing-mm 0.3] [--pore-spacing-mm 0.8] [--angle-deg 35]

Out (by default the skin's, `extension/juststage/data/generated/skin/microrelief.png`, read by modules/skin/maps.py):
a 16-bit grey PNG (1 = highest) and `OUT.json` with its size in millimetres and the parameters. The defaults are the
ones the gate picked (2026-11-05: on our cheek with the pore tile kept, the finest band 0.42 against HD Aaron's 0.45,
the pore band 0.92 against 0.97 - `docs/gate/2026-11-05/report.md`); 2048 px keeps 205 px/mm, six times the closest
gate view's 34, at a quarter of 4096's memory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

OUT = Path(__file__).resolve().parents[1] / "extension" / "juststage" / "data" / "generated" / "skin" / "microrelief.png"
#: furrow depths and widths (relative height; millimetres): primary furrows follow the line direction, secondary
#: ones cross them shallower and narrower - the skin's two orders of lines
PRIMARY_DEPTH, SECONDARY_DEPTH = 0.55, 0.28
PRIMARY_WIDTH_MM, SECONDARY_WIDTH_MM = 0.016, 0.010
#: how far the cells rise between the furrows (relative), and the final smoothing (pixels)
DOME = 0.35
SMOOTH_PX = 1.5
#: pores: pits at a sparser subset of the nodes, radius in mm (a range) and depth (relative)
PORE_RADIUS_MM, PORE_DEPTH = (0.025, 0.055), 1.0
NOISE, NOISE_PX = 0.02, 6.0


def poisson_disk(spacing: float, rng: np.random.Generator, tries: int = 30) -> np.ndarray:
    """Bridson's Poisson-disk sampling on the unit torus (wrap-around distance), `spacing` in tile units."""
    cell = spacing / np.sqrt(2)
    n = int(np.ceil(1 / cell))
    grid = -np.ones((n, n), dtype=np.int64)
    points = [rng.random(2)]
    grid[tuple((points[0] / (1 / n)).astype(int) % n)] = 0
    active = [0]
    while active:
        i = active[rng.integers(len(active))]
        found = False
        for _ in range(tries):
            r = spacing * (1 + rng.random())
            a = rng.random() * 2 * np.pi
            p = (points[i] + r * np.array([np.cos(a), np.sin(a)])) % 1.0
            gx, gy = (p * n).astype(int) % n
            ok = True
            for dx in (-2, -1, 0, 1, 2):
                for dy in (-2, -1, 0, 1, 2):
                    j = grid[(gx + dx) % n, (gy + dy) % n]
                    if j >= 0:
                        d = np.abs(points[j] - p)
                        d = np.minimum(d, 1 - d)
                        if d @ d < spacing * spacing:
                            ok = False
                            break
                if not ok:
                    break
            if ok:
                points.append(p)
                grid[gx, gy] = len(points) - 1
                active.append(len(points) - 1)
                found = True
                break
        if not found:
            active.remove(i)
    return np.array(points)


def _wrap_edt(mask: np.ndarray, pad: int):
    """The distance to the nearest True pixel and its index, on the torus (the tile wrapped by `pad` on every side)."""
    padded = np.pad(mask, pad, mode="wrap")
    dist, (iy, ix) = ndimage.distance_transform_edt(~padded, return_indices=True)
    inner = (slice(pad, -pad), slice(pad, -pad))
    return dist[inner], (iy[inner] - pad) % mask.shape[0], (ix[inner] - pad) % mask.shape[1]


def make(tile_mm: float, px: int, seed: int, spacing_mm: float, pore_spacing_mm: float, angle_deg: float,
         stretch: float = 1.35) -> np.ndarray:
    """The height tile (0-1). Nodes by Poisson disk in a frame stretched along the line direction; their Voronoi cells
    are the plateaus (the Delaunay graph's dual: Weiss et al.'s furrow edges join the nodes, so its faces are the
    cells), domed; the cell walls are the furrows, deeper where they run along the line direction; pores sit on
    junctions of the walls."""
    rng = np.random.default_rng(seed)
    pad = px // 8
    theta = np.radians(angle_deg)
    u = np.array([np.cos(theta), np.sin(theta)])
    # the nodes, then each pixel's nearest node by distance measured in the stretched frame (cells longer along u)
    nodes = poisson_disk(spacing_mm / tile_mm, rng)
    seeds = np.zeros((px, px), dtype=bool)
    ij = (nodes * px).astype(int) % px
    seeds[ij[:, 1], ij[:, 0]] = True
    if stretch != 1.0:  # an anisotropic Voronoi: sample the pixel grid in the stretched frame
        yy, xx = np.mgrid[0:px, 0:px].astype(np.float32) / px
        along = xx * u[0] + yy * u[1]
        across = -xx * u[1] + yy * u[0]
        coords = np.stack([along / stretch, across], -1)
        node_c = np.stack([nodes @ u / stretch, nodes @ np.array([-u[1], u[0]])], -1)
        from scipy.spatial import cKDTree

        offsets = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        copies = np.concatenate([nodes + np.array(o) for o in offsets])
        copies_c = np.stack([copies @ u / stretch, copies @ np.array([-u[1], u[0]])], -1)
        to_node, nearest = cKDTree(copies_c).query(coords.reshape(-1, 2))
        label = (nearest % len(nodes)).reshape(px, px).astype(np.int32)
        to_node = to_node.reshape(px, px) * tile_mm
        del yy, xx, along, across, coords, node_c
    else:
        to_node, iy, ix = _wrap_edt(seeds, pad)
        to_node = to_node / px * tile_mm
        lookup = -np.ones((px, px), dtype=np.int32)
        lookup[ij[:, 1], ij[:, 0]] = np.arange(len(nodes))
        label = lookup[iy, ix]
    # the walls: where a pixel's cell differs from its right or lower neighbour; how much each runs along u
    right = label != np.roll(label, -1, 1)
    down = label != np.roll(label, -1, 0)
    wall = right | down
    other = np.where(right, np.roll(label, -1, 1), np.roll(label, -1, 0))
    gap = nodes[other] - nodes[label]
    gap -= np.round(gap)  # the torus
    gap /= np.linalg.norm(gap, axis=-1, keepdims=True) + 1e-12
    # a wall runs across the line joining its two nodes: along u when that line is across u
    runs_along = np.abs(gap @ np.array([-u[1], u[0]]))
    depth_px = np.where(runs_along > 0.7, PRIMARY_DEPTH, SECONDARY_DEPTH)
    width_px = np.where(runs_along > 0.7, PRIMARY_WIDTH_MM, SECONDARY_WIDTH_MM)
    pair_noise = rng.uniform(0.6, 1.0, len(nodes))
    depth_px = depth_px * pair_noise[np.minimum(label, other)]
    dist, iy, ix = _wrap_edt(wall, pad)
    d_mm = dist / px * tile_mm
    depth, width = depth_px[iy, ix], width_px[iy, ix]
    # the plateau: rounded by where a pixel sits between its cell's wall (0) and its centre (0.5)
    place = np.clip(d_mm / (d_mm + to_node + 1e-9), 0.0, 0.5) * 2
    height = DOME * (1 - (1 - place) ** 2) - depth * np.exp(-((d_mm / width) ** 2))
    # pores: at wall junctions (three cells meet) near a sparser Poisson set
    junction = right & down & (np.roll(label, -1, 1) != np.roll(label, -1, 0))
    jy, jx = np.nonzero(junction)
    wanted = poisson_disk(pore_spacing_mm / tile_mm, rng)
    from scipy.spatial import cKDTree

    jpos = np.stack([jx, jy], -1) / px
    _, pick = cKDTree(np.concatenate([jpos + np.array(o) for o in [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]])
                      ).query(wanted)
    centres = jpos[pick % len(jpos)]
    for centre, radius in zip(centres, rng.uniform(*PORE_RADIUS_MM, len(centres)), strict=True):
        r_px = int(radius * 3 / tile_mm * px) + 2
        cx, cy = (centre * px).astype(int)
        ys = np.arange(cy - r_px, cy + r_px + 1) % px
        xs = np.arange(cx - r_px, cx + r_px + 1) % px
        dy = (ys[:, None] / px - centre[1] + 0.5) % 1.0 - 0.5
        dx = (xs[None, :] / px - centre[0] + 0.5) % 1.0 - 0.5
        r_mm = np.hypot(dx, dy) * tile_mm
        height[np.ix_(ys, xs)] -= PORE_DEPTH * np.exp(-((r_mm / radius) ** 2)) * rng.uniform(0.6, 1.0)
    noise = ndimage.gaussian_filter(rng.standard_normal((px, px)), NOISE_PX, mode="wrap")
    height += NOISE * noise / noise.std()
    height = ndimage.gaussian_filter(height, SMOOTH_PX, mode="wrap")  # the walls' pixel steps out
    return (height - height.min()) / (height.max() - height.min())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path, nargs="?", default=OUT)
    p.add_argument("--tile-mm", type=float, default=10.0)
    p.add_argument("--px", type=int, default=2048)
    p.add_argument("--seed", type=int, default=2)
    p.add_argument("--spacing-mm", type=float, default=0.3)
    p.add_argument("--pore-spacing-mm", type=float, default=0.8)
    p.add_argument("--angle-deg", type=float, default=35.0)
    a = p.parse_args()
    height = make(a.tile_mm, a.px, a.seed, a.spacing_mm, a.pore_spacing_mm, a.angle_deg)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((height * 65535).astype(np.uint16)).save(a.out)
    meta = {"size_mm": a.tile_mm, "px": a.px, "seed": a.seed, "spacing_mm": a.spacing_mm,
            "pore_spacing_mm": a.pore_spacing_mm, "angle_deg": a.angle_deg,
            "method": "graph-based microrelief after Weiss et al., SGP 2023 (our code)"}
    a.out.with_suffix(".json").write_text(json.dumps(meta, indent=1))
    print("wrote", a.out, height.shape)


if __name__ == "__main__":
    main()
