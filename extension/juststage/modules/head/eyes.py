# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""An eye's opening between its lids, found by what shows (moved from the face test's `face_shape.py`, which re-exports
it): rays out from just under the eyeball's surface; the eyeball shows where no skin crosses close outside it. The
lashes (modules/hair/lashes.py) root along it; the face test's occlusion shell and tearline follow it too."""

from __future__ import annotations

import collections

import bpy
import numpy as np

Opening = collections.namedtuple("Opening", "centre radius centres upper lower outer inner")


def direction(az, el):
    """Unit vectors for azimuths (degrees toward +x from straight ahead, -y) and elevations about an eye."""
    ar, er = np.radians(az), np.radians(el)
    return np.c_[np.sin(ar) * np.cos(er), -np.cos(ar) * np.cos(er), np.sin(er)]


def angles(points, centre):
    """Each point's azimuth and elevation about an eye's centre, and its distance from it."""
    rel = points - centre
    return (np.degrees(np.arctan2(rel[:, 0], -rel[:, 1])),
            np.degrees(np.arctan2(rel[:, 2], np.hypot(rel[:, 0], rel[:, 1]))), np.linalg.norm(rel, axis=1))  # fmt: skip


def world_points(obj):
    m = np.array(obj.matrix_world)
    return np.array([v.co for v in obj.data.vertices]) @ m[:3, :3].T + m[:3, 3]


def gaze(eye):
    """Where an eye looks: the azimuth and elevation of its iris and pupil's middle."""
    points = world_points(eye)
    ids = {
        i
        for i, sl in enumerate(eye.material_slots)
        if sl.material and ("Iris" in sl.material.name or "Pupil" in sl.material.name)
    }
    iris = sorted({v for p in eye.data.polygons if p.material_index in ids for v in p.vertices})
    az, el, _ = angles(points[iris].mean(axis=0, keepdims=True), (points.min(axis=0) + points.max(axis=0)) / 2)
    return float(az[0]), float(el[0])


def eye_opening(eye_points, verts, polys, seed, inside, reach):
    """An eye's opening by what shows: rays out from `inside` under the eyeball's surface on a 1 x 0.5 deg grid; the
    eyeball shows where no skin crosses within `reach` outside it; the opening is the shown patch around `seed` (the
    gaze's azimuth and elevation). Not a search for skin touching the eyeball: the skin is watertight - it folds into
    the socket - so that search also finds the socket and the lids' backs; it put our opening at +-2..7 deg where it
    really runs from -4 to -30 deg at the iris (rays, 2026-10-31). Returns the eyeball's centre and radius, the
    opening's azimuths with its upper and lower edge at each, and the outer and inner corners' azimuths."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    centre = (eye_points.min(axis=0) + eye_points.max(axis=0)) / 2
    radius = float((eye_points.max(axis=0) - eye_points.min(axis=0))[[0, 2]].mean() / 2)
    tree = BVHTree.FromPolygons([Vector(v) for v in verts], polys)
    azs, els = np.arange(-80.0, 80.5, 1.0), np.arange(-50.0, 50.25, 0.5)
    shown = np.zeros((len(azs), len(els)), bool)
    for i, a in enumerate(azs):
        for k, d in enumerate(direction(np.full(len(els), a), els)):
            shown[i, k] = tree.ray_cast(Vector(centre + (radius - inside) * d), Vector(d), inside + reach)[0] is None
    # from the shown cell nearest the gaze: the lid's edge stands 1-1.5 mm off the eyeball, so a ray straight out
    # through the iris' middle can meet it while the camera still sees the iris' middle below it (round 51's lids)
    ai, ek = np.meshgrid(azs, els, indexing="ij")
    gap = np.where(shown, np.hypot(ai - seed[0], ek - seed[1]), np.inf)
    i0, k0 = np.unravel_index(int(np.argmin(gap)), gap.shape)
    assert gap[i0, k0] < 15.0, f"nothing shows within 15 deg of the gaze ({seed[0]:.1f}, {seed[1]:.1f} deg)"
    patch, todo = np.zeros_like(shown), [(i0, k0)]
    while todo:
        i, k = todo.pop()
        if 0 <= i < len(azs) and 0 <= k < len(els) and shown[i, k] and not patch[i, k]:
            patch[i, k] = True
            todo += [(i + 1, k), (i - 1, k), (i, k + 1), (i, k - 1)]
    cols = np.flatnonzero(patch.any(axis=1))
    centres = azs[cols]
    upper = np.array([els[patch[i]].max() for i in cols])
    lower = np.array([els[patch[i]].min() for i in cols])
    outer, inner = (centres.max(), centres.min()) if centre[0] > 0 else (centres.min(), centres.max())  # nose at x 0
    return Opening(centre, radius, centres, upper, lower, outer, inner)


def skin_polygons(body: bpy.types.Object) -> list[list[int]]:
    """The body's own polygons (not its helpers')."""
    from ...core.makehuman import BODY_VERTICES

    return [list(p.vertices) for p in body.data.polygons if max(p.vertices) < BODY_VERTICES]


def openings(body: bpy.types.Object) -> dict[str, Opening]:
    """Both eyes' openings on the character's current shape (its eye parts `eyeLeft`, `eyeRight`), by eye object."""
    from ...core.makehuman import BODY_VERTICES
    from ..body import build
    from . import parts

    skin = build.shaped_coords(body)[:BODY_VERTICES].astype(np.float64)
    polys = skin_polygons(body)
    found = {}
    for part in ("eyeLeft", "eyeRight"):
        eye = parts.parts_of(body).get(part)
        if eye is None:
            from ...core.commands import CommandError

            raise CommandError(f"{body.name} has no {part}; run juststage.head.add_parts first")
        found[eye.name] = eye_opening(world_points(eye), skin, polys, gaze(eye), 0.003, 0.008)
    return found
