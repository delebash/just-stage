# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test: the head's shape for the whole test - the lips closed and the lids brought to the iris, as shape keys.
Applied before the clay and depth pictures (test_face_clay.py), so the paintings are aligned to, and projected onto,
the same surface (round 43: the clay's open mouth stretched the painting's closed lips into a pale band between them).
"""

import importlib

import bpy
import numpy as np


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


def lower_lids(body, upper=14.0, lower=5.0):
    """The lids closer to the iris, as a shape key: our neutral eyes show white above and below the iris (a stare, or
    eyes rolled up); a relaxed eye — and the AI's painting — has the upper lid over the iris' top and the lower lid at its
    bottom. Lid skin over each eyeball turns about the eyeball's left-right axis (as a lid closes, so it can't pass
    through the eye): the upper lid down, the lower lid up, most at each lid's edge (found per 10° slice across the eye),
    none 35° away from it."""
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    co = build.shaped_coords(body).astype(np.float64)
    key = body.shape_key_add(name="lids closer", from_mix=False)
    moved = 0
    for name in ("Face.eyeLeft", "Face.eyeRight"):
        eye = bpy.data.objects[name]
        ev = np.array([v.co for v in eye.data.vertices]) @ np.array(eye.matrix_world)[:3, :3].T + np.array(eye.matrix_world)[:3, 3]
        centre = (ev.min(axis=0) + ev.max(axis=0)) / 2
        radius = float((ev.max(axis=0) - ev.min(axis=0))[[0, 2]].mean() / 2)
        rel = co - centre
        dist = np.linalg.norm(rel, axis=1)
        az = np.degrees(np.arctan2(rel[:, 0], -rel[:, 1]))
        el = np.degrees(np.arctan2(rel[:, 2], np.hypot(rel[:, 0], rel[:, 1])))
        near = (dist > radius * 0.9) & (dist < radius + 0.012) & (rel[:, 1] < 0) & (np.abs(az) < 45)
        touching = near & (dist < radius + 0.004)
        ang = np.zeros(len(co))
        edges = []
        for a0 in range(-40, 40, 10):
            in_bin = (az >= a0) & (az < a0 + 10)
            up_edge = el[touching & in_bin & (el > 3)]
            lo_edge = el[touching & in_bin & (el < -3)]
            fade = max(0.0, 1.0 - (abs(a0 + 5) - 25) / 15) if abs(a0 + 5) > 25 else 1.0  # less toward the corners
            if up_edge.size:
                m = float(up_edge.min())
                w = np.clip(1.0 - (el - m) / 35.0, 0.0, 1.0) * (el >= m - 2.0)
                ang += np.where(in_bin & near, np.radians(upper) * w * fade, 0.0)
                edges.append(round(m, 1))
            if lo_edge.size:
                m = float(lo_edge.max())
                w = np.clip(1.0 - (m - el) / 35.0, 0.0, 1.0) * (el <= m + 2.0)
                ang -= np.where(in_bin & near, np.radians(lower) * w * fade, 0.0)
        y, z = rel[:, 1], rel[:, 2]
        new_y = y * np.cos(ang) - z * np.sin(ang)
        new_z = y * np.sin(ang) + z * np.cos(ang)
        for i in np.flatnonzero(ang != 0):
            key.data[i].co.y += float(new_y[i] - y[i])
            key.data[i].co.z += float(new_z[i] - z[i])
        moved += int((ang != 0).sum())
        print(f"  {name}: upper lid edges {edges}°")
    key.value = 1.0
    print(f"lids closer: {moved} vertices (upper {upper}°, lower {lower}° at the edges)")
