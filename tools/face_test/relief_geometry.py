# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, the paintings' relief as geometry (research rec 5, "true displacement ... relief from pictures"): the
heights that give our surface the normals the paintings show - the hooded fold over the lid, the brow ridge, the lips'
volume - so they cast shadows and turn edges, not only shade.

Nehab et al., "Efficiently combining positions and normals for precise 3D geometry" (SIGGRAPH 2005): positions held
near where they are while every tangent - the step to a neighbour - is made perpendicular to the target normal; one
sparse linear least-squares solve. Here on the UV texel grid (each texel a surface point, its neighbours in the same UV
island its neighbours on the surface), each point moving only along the mesh normal, so the unknown is one height per
texel - a displacement map in the same layout as the colour and normal maps. Plain numpy (Blender's Python has
no SciPy).
"""

import numpy as np


def _cgls(rows, cols, vals, rhs, n, iterations=600, tol=1e-8):
    """Conjugate gradients on the least-squares normal equations (CGLS, Hestenes & Stiefel), the sparse matrix kept as
    its (row, column, value) triplets - plain numpy, so it runs in Blender's own Python (no SciPy there)."""
    m = len(rhs)

    def mul(x):
        return np.bincount(rows, vals * x[cols], minlength=m)

    def mul_t(y):
        return np.bincount(cols, vals * y[rows], minlength=n)

    x = np.zeros(n)
    r = rhs.copy()
    s = mul_t(r)
    p = s.copy()
    gamma = s @ s
    start = gamma
    for _ in range(iterations):
        q = mul(p)
        alpha = gamma / (q @ q)
        x += alpha * p
        r -= alpha * q
        s = mul_t(r)
        new = s @ s
        if new < tol * tol * start:
            break
        p = s + (new / gamma) * p
        gamma = new
    return x


def heights(points, mesh_normals, target_normals, mask, hold=0.02, max_step=None):
    """Heights along `mesh_normals` (metres) per masked texel.

    points, mesh_normals, target_normals: (H, W, 3) maps, valid where `mask`; `hold` weighs each height toward 0
    against the normal terms (Nehab's lambda, per texel); neighbours farther apart than `max_step` (a UV seam's two
    sides) are not tied.
    """
    h, w = mask.shape
    index = -np.ones((h, w), np.int64)
    index[mask] = np.arange(int(mask.sum()))
    n_unknown = int(mask.sum())
    rows, cols, vals, rhs = [], [], [], []
    row = 0
    spacing = []
    for dy, dx in ((0, 1), (1, 0)):
        a = mask[: h - dy, : w - dx] & mask[dy:, dx:]
        ia, ib = index[: h - dy, : w - dx][a], index[dy:, dx:][a]
        pa, pb = points[: h - dy, : w - dx][a], points[dy:, dx:][a]
        step = np.linalg.norm(pb - pa, axis=1)
        spacing.append(step)
        keep = step < (max_step if max_step is not None else np.inf)
        ia, ib, pa, pb = ia[keep], ib[keep], pa[keep], pb[keep]
        na, nb = mesh_normals[: h - dy, : w - dx][a][keep], mesh_normals[dy:, dx:][a][keep]
        for t in (target_normals[: h - dy, : w - dx][a][keep], target_normals[dy:, dx:][a][keep]):
            # (pb + hb nb - pa - ha na) . t = 0  ->  hb (nb.t) - ha (na.t) = -(pb - pa).t
            k = len(ia)
            r = np.arange(row, row + k)
            rows += [r, r]
            cols += [ib, ia]
            vals += [(nb * t).sum(1), -(na * t).sum(1)]
            rhs.append(-((pb - pa) * t).sum(1))
            row += k
    scale = float(np.median(np.concatenate(spacing)))  # normal terms in metres of step: the hold in the same units
    r = np.arange(row, row + n_unknown)
    rows.append(r)
    cols.append(np.arange(n_unknown))
    vals.append(np.full(n_unknown, hold * scale))
    rhs.append(np.zeros(n_unknown))
    row += n_unknown
    solved = _cgls(np.concatenate(rows), np.concatenate(cols), np.concatenate(vals), np.concatenate(rhs), n_unknown)
    out = np.zeros((h, w))
    out[mask] = solved
    return out
