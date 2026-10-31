# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test: the head's shape for the whole test - the lips closed, the lids brought to the iris and the painted
person's shape (flame_fit.py), as shape keys. Applied before the clay and depth pictures (test_face_clay.py), so the
paintings are aligned to, and projected onto, the same surface (round 43: the clay's open mouth stretched the
painting's closed lips into a pale band between them).
"""

import collections
import importlib

import bpy
import numpy as np

#: the lid key's turn at each lid's edge (degrees; + closes, - opens), set so the clay's real lid edges - its eye
#: opening segmented from its colours - meet the painting's lid lines (MediaPipe on the painting), column by column,
#: unwarped (round 51's lid_fit). Not MediaPipe on the clay: its lid contour there is a learned guess (it read a
#: near-shut clay eye as matching), nor an iris-radius ruler fitted to the clay's colours (it under-read the iris by
#: a quarter). At 5 / 1.6 the front view's clay opening was ~2.5 mm short of the painting's (upper lid 3-5 px low,
#: lower 5 px high at 0.88 px a degree): our neutral eye is the smaller one, so the key opens it
UPPER_LID, LOWER_LID = 1.0, -4.4


def close_mouth(body):
    """The lips closed as a shape key: our head's neutral mouth is a slit ~0.9 mm tall at its middle (measured by rays
    from the face camera; teeth behind it), the AI paints it closed. Upper lip down, lower lip up, most at the slit,
    fading out by ~4 mm and toward the corners (±24 mm)."""
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    co = build.shaped_coords(body).astype(np.float64)
    x, y, z = co[:, 0], co[:, 1], co[:, 2]
    z_mid = 1.5484  # where the lips meet, middle and corners (measured)
    half = np.clip(1.0 - (x / 0.024) ** 2, 0.0, 1.0)
    gap = 0.0016 * half
    near = (np.abs(x) < 0.027) & (y < -0.138) & (np.abs(z - z_mid) < 0.012)
    around = (np.abs(x) < 0.036) & (y < -0.12) & (np.abs(z - z_mid) < 0.02)  # the thinning's and narrowing's reach
    shift = (gap / 2 + 0.0004 * half) * np.exp(-(((z - z_mid) / 0.005) ** 2)) * near
    shift += 0.21 * np.abs(z - z_mid) * np.exp(-(((z - z_mid) / 0.012) ** 4)) * half * around  # thinner lips
    key = body.shape_key_add(name="mouth closed", from_mix=False)  # the basis plus this offset only
    dz = np.where(z > z_mid, -shift, shift)
    dx = -0.06 * x * np.clip((0.036 - np.abs(x)) / 0.010, 0.0, 1.0) * np.exp(-(((z - z_mid) / 0.008) ** 2)) * around
    for i in np.flatnonzero(near | around):
        key.data[i].co.z += dz[i]
        key.data[i].co.x += dx[i]
    key.value = 1.0
    print(f"mouth closed: {(near | around).sum()} vertices, at most {shift.max() * 1000:.2f} mm down/up, "
          f"{np.abs(dx).max() * 1000:.2f} mm in")


Opening = collections.namedtuple("Opening", "centre radius centres upper lower outer inner")


def direction(az, el):
    """Unit vectors for azimuths (degrees toward +x from straight ahead, -y) and elevations about an eye."""
    ar, er = np.radians(az), np.radians(el)
    return np.c_[np.sin(ar) * np.cos(er), -np.cos(ar) * np.cos(er), np.sin(er)]


def angles(points, centre):
    """Each point's azimuth and elevation about an eye's centre, and its distance from it."""
    rel = points - centre
    return (np.degrees(np.arctan2(rel[:, 0], -rel[:, 1])),
            np.degrees(np.arctan2(rel[:, 2], np.hypot(rel[:, 0], rel[:, 1]))), np.linalg.norm(rel, axis=1))


def world_points(obj):
    m = np.array(obj.matrix_world)
    return np.array([v.co for v in obj.data.vertices]) @ m[:3, :3].T + m[:3, 3]


def gaze(eye):
    """Where an eye looks: the azimuth and elevation of its iris and pupil's middle."""
    points = world_points(eye)
    ids = {i for i, sl in enumerate(eye.material_slots) if sl.material and ("Iris" in sl.material.name or "Pupil" in sl.material.name)}
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


def skin_polygons(body, skin_count=13380):
    """The body's own polygons (not its helpers')."""
    return [list(p.vertices) for p in body.data.polygons if max(p.vertices) < skin_count]


def lower_lids(body, upper=UPPER_LID, lower=LOWER_LID):
    """The lids moved to the painting's lid lines, as a shape key ("lids closer"; + closes, - opens). Lid skin over
    each eyeball turns about the eyeball's left-right axis (as a lid closes, so it can't pass through the eye -
    MetaHuman's lid joints keep the eyeball's contour the same way): the upper lid by `upper` degrees, the lower by
    `lower`, most at the lid's edge - the opening's edge (eye_opening) - none 35 deg away from it, fading over the
    last 15 deg toward each corner."""
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    co = build.shaped_coords(body).astype(np.float64)
    skin = co[:13380]
    polys = skin_polygons(body)
    key = body.shape_key_add(name="lids closer", from_mix=False)
    moved = 0
    for name in ("Face.eyeLeft", "Face.eyeRight"):
        eye = bpy.data.objects[name]
        o = eye_opening(world_points(eye), skin, polys, gaze(eye), 0.003, 0.008)
        az, el, dist = angles(co, o.centre)
        lo_az, hi_az = o.centres.min(), o.centres.max()
        near = (dist > o.radius * 0.9) & (dist < o.radius + 0.012) & (co[:, 1] < o.centre[1]) & (az >= lo_az) & (az <= hi_az)
        fade = np.clip(np.minimum(az - lo_az, hi_az - az) / 15.0, 0.0, 1.0)
        up_edge, lo_edge = np.interp(az, o.centres, o.upper), np.interp(az, o.centres, o.lower)
        w_up = np.clip(1.0 - (el - up_edge) / 35.0, 0.0, 1.0) * (el >= up_edge - 1.0)
        w_lo = np.clip(1.0 - (lo_edge - el) / 35.0, 0.0, 1.0) * (el <= lo_edge + 1.0)
        ang = np.where(near, np.radians(upper) * w_up * fade - np.radians(lower) * w_lo * fade, 0.0)
        rel = co - o.centre
        y, z = rel[:, 1], rel[:, 2]
        new_y = y * np.cos(ang) - z * np.sin(ang)
        new_z = y * np.sin(ang) + z * np.cos(ang)
        for i in np.flatnonzero(ang != 0):
            key.data[i].co.y += float(new_y[i] - y[i])
            key.data[i].co.z += float(new_z[i] - z[i])
        moved += int((ang != 0).sum())
        mid = int(np.argmin(np.abs(o.centres - gaze(eye)[0])))
        print(f"  {name}: opening {abs(o.inner - o.outer):.0f} deg wide, at the iris {o.lower[mid]:.1f} .. {o.upper[mid]:.1f} deg")
    key.value = 1.0
    print(f"lids closer: {moved} vertices (upper {upper} deg, lower {lower} deg at the edges)")


def export_neutral(body, path):
    """Our head before any of these shape keys (vertices and triangles, world = object space here), for flame_fit.py's
    fit to our own surface."""
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    co = build.shaped_coords(body).astype(np.float64)
    tris = [(p.vertices[0], p.vertices[i], p.vertices[i + 1]) for p in body.data.polygons for i in range(1, len(p.vertices) - 1)]
    np.savez(path, co=co, faces=np.asarray(tris, np.int64))
    print(f"neutral head: {len(co)} vertices, {len(tris)} triangles -> {path}")


def apply_fit(body, path):
    """The painted person's shape (flame_fit.py's offsets, from the neutral head) as one more additive shape key; each
    eyeball moves with the face around it. Nothing when there is no fit yet."""
    from pathlib import Path

    from mathutils import Vector

    if not Path(path).exists():
        print("painted person: no fit yet")
        return
    fit = np.load(path)
    offsets = fit["offsets"].astype(np.float64)
    key = body.shape_key_add(name="painted person", from_mix=False)
    for i in np.flatnonzero(np.linalg.norm(offsets, axis=1) > 1e-6):
        key.data[i].co += Vector(offsets[i])
    key.value = 1.0
    # each eyeball moves with the lid skin around it (within 20 mm of its centre): FLAME's own eyeballs are fitted by
    # neither fit (both use the face's skin), and their offset - 2 mm inward and up - pushed the whites out at the
    # inner corners (the first fitted clay views)
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    co = build.shaped_coords(body).astype(np.float64)[:13380]
    for name in ("Face.eyeLeft", "Face.eyeRight"):
        eye = bpy.data.objects[name]
        m = np.array(eye.matrix_world)
        ev = np.array([v.co for v in eye.data.vertices]) @ m[:3, :3].T + m[:3, 3]
        centre = (ev.min(axis=0) + ev.max(axis=0)) / 2
        around = np.linalg.norm(co - centre, axis=1) < 0.020
        move = offsets[:13380][around].mean(axis=0)
        eye.matrix_world.translation += Vector(move)
        print(f"  {name}: moved {np.round(move * 1000, 2).tolist()} mm with {int(around.sum())} lid vertices")
    moved = np.linalg.norm(offsets, axis=1)
    print(f"painted person: {int((moved > 0.0005).sum())} vertices over 0.5 mm, at most {moved.max() * 1000:.1f} mm")
