# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test: the head's shape for the whole test - the lips closed, the lids brought to the iris and the painted
person's shape (flame_fit.py), as shape keys. Applied before the clay and depth pictures (test_face_clay.py), so the
paintings are aligned to, and projected onto, the same surface (round 43: the clay's open mouth stretched the
painting's closed lips into a pale band between them).
"""

import importlib

import bpy
import numpy as np

#: the lid key's turn at each lid's edge (degrees; + closes, - opens), set so the clay's real lid edges - its eye
#: opening segmented from its colours - meet the painting's lid lines (MediaPipe on the painting), column by column,
#: unwarped (round 51's lid_fit). Not MediaPipe on the clay: its lid contour there is a learned guess (it read a
#: near-shut clay eye as matching), nor an iris-radius ruler fitted to the clay's colours (it under-read the iris by
#: a quarter). At 5 / 1.6 the front view's clay opening was ~2.5 mm short of the painting's (upper lid 3-5 px low,
#: lower 5 px high at 0.88 px a degree): our neutral eye is the smaller one, so the key opens it. At 1 / -4.4 the
#: front view's lids sit 0.7-2.1 px from the painting's; the close view's opening heights within ~3 px (its lids both
#: 13-22 px higher - the AI's drift there, which the landmark warp takes out). But MediaPipe's lid lines on the
#: painting run along the outer edges of its thick lid margins (the lower one ~6 px below where the eyeball stops
#: showing, close view) and on our thin-margined render at the edge itself, so matching them opened our eye too far:
#: round 65 against the unwarped close painting, read by eye at 4x from the line through MediaPipe's corners (in eye
#: widths, both eyes): upper lid 0.26-0.28 above it against the painting's 0.23-0.25, lower 0.06-0.09 below against
#: 0.02-0.05 - the opening ~26% taller, white under the iris. Closed by 4.7 / 7 px at ~1.7 px a degree (the front
#: view's 0.88, the close camera 1.95x nearer): 3.7 / -0.3 (round 66, 2026-11-02). Round 69 the same way: the upper
#: lids 0.235 / 0.258 (matched), the lower still 0.074 / 0.065 below; the key moves the lower edge a degree a degree
#: (eye_opening at the iris: -34 / -30 / -26 deg at -4.4 / -0.3 / +4), ~1.1 px a degree here - +4.5.
UPPER_LID, LOWER_LID = 3.7, 4.5


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


# the eye opening and its helpers are the app's (modules/head/eyes.py: the lashes root along it), re-exported here for
# this test's callers (the lid key below, the occlusion shell, the tearline)
_eyes = importlib.import_module("bl_ext.system.juststage.modules.head.eyes")
Opening, direction, angles, world_points = _eyes.Opening, _eyes.direction, _eyes.angles, _eyes.world_points
gaze, eye_opening, skin_polygons = _eyes.gaze, _eyes.eye_opening, _eyes.skin_polygons


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
        o = eye_opening(world_points(eye), skin, polys, gaze(eye), 0.0001, 0.02)
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
