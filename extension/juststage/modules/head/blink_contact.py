# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The blink's closing step (the plan's §7 "Per-character" contact, Q-RIG-2 - decided under the go 2026-11-08, build
queue §19.4 item 3): a blink unit closes the upper lid toward the lower, but on our lids it stopped ~2 mm short
(Faceunits' eyeBlink) or ~6 mm short (ICT's scanned blink) and could clip the eyeball. CC5 does the same job with its
"Correct Eyeblink" (the upper lid snapped onto the lower); OmniFaceRig's is "upper-eyelid vertices snapped to lower lid
and locally relaxed". Here, per eye, on the neutral face closed by its blink unit: each upper row of base v2's lid
anatomy (lash line, margin, rim) goes onto the lower row of its kind at the same angle round the eye, the move carried
into four rings of upper-lid skin (RELAX), any lid point inside the eyeball pushed out to EYEBALL_GAP off it - kept as
a corrective shape key driven by the blink's own value (Blender's single-property driver, as the teeth's jaw units
follow the jaw). Made again on every refit and when the face units are added. Measured as the gate's `blinkfix`
trial: gap 1.93 / 2.01 -> 0.15 / 0.18 mm, no clip; on ICT's blink 6.24 / 6.07 -> 0.06 / 0.11; the closed lid reads
like HD Aaron's (sheet `sheet_C9_ictblink.png`)."""

from __future__ import annotations

import bpy
import numpy as np

KEY = "JustStage blink contact {side}"  # the corrective per eye, driven by eyeBlink<side>
SIDES = (("Left", "eyeLeft"), ("Right", "eyeRight"))
RELAX = (0.7, 0.45, 0.25, 0.1)  # the share of the lash line's move each ring of upper-lid skin above it takes
EYEBALL_GAP = 0.0003  # m: a lid point pushed out of the eyeball sits this far off it
NEAR_EYE = 0.025  # m: a lid row belongs to the eye whose centre is within this of its margin
UPPER_SHARE = 0.3  # a row whose margin the blink moves over this share of the most is the upper lid's


def _neutral(character: bpy.types.Object) -> np.ndarray:
    """The face without any expression: every key whose name is an ARKit unit or one of ours here, at 0 for the
    measure (restored after); the sliders, the lids' contact and the lip seal stay. Local space."""
    from ..body import build
    from .face_units import ARKIT

    keys = character.data.shape_keys
    held = {}
    for kb in keys.key_blocks[1:]:
        if kb.name in ARKIT or kb.name.startswith("JustStage blink contact"):
            held[kb.name] = kb.value
            kb.value = 0.0
    try:
        return build.shaped_coords(character)
    finally:
        for name, value in held.items():
            keys.key_blocks[name].value = value


def _lids(rows: np.ndarray, co: np.ndarray, move: np.ndarray, centre: np.ndarray):
    """One eye's (upper, lower) lid rows - the complete rows (lash line, margin and rim all there) near its centre,
    split
    by what the blink does: the upper lid is the one its unit moves (the margin moving over UPPER_SHARE of the most).
    Not by height against the eye's centre, as the gate's trial did: MakeHuman's half-closed default lids put every
    rim below it; nor by the record's order, which is hm08's vertex order, not the ring's."""
    rows = rows[(rows >= 0).all(1)]
    mine = rows[np.linalg.norm(co[rows[:, 1]] - centre, axis=1) < NEAR_EYE]
    if len(mine) < 6:
        return None
    moved = np.linalg.norm(move[mine[:, 1]], axis=1)
    upper = moved > UPPER_SHARE * moved.max()
    if upper.sum() < 3 or (~upper).sum() < 3:
        return None
    return mine[upper], mine[~upper]


def _neighbours(me) -> dict[int, set[int]]:
    edges = np.empty(len(me.edges) * 2, np.int64)
    me.edges.foreach_get("vertices", edges)
    nbr: dict[int, set[int]] = {}
    for a, b in edges.reshape(-1, 2):
        nbr.setdefault(int(a), set()).add(int(b))
        nbr.setdefault(int(b), set()).add(int(a))
    return nbr


def make(character: bpy.types.Object) -> dict[str, tuple[float, float]]:
    """The closing step's corrective for each eye with a blink unit; returns {side: (gap mm, clip mm) after}."""
    from ...core import makehuman
    from ..body import base
    from . import eye_layers, parts

    keys = character.data.shape_keys
    eyes = parts.parts_of(character)
    me = character.data
    if keys is None or len(me.vertices) <= makehuman.HM08_VERTICES:  # base v2's lid rows only
        return {}
    n = len(me.vertices)
    basis = np.empty(n * 3, np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    basis = basis.reshape(-1, 3).astype(np.float64)
    neutral = _neutral(character)
    inv = np.linalg.inv(np.array(character.matrix_world))
    all_rows = base.rows()
    nbr = None
    done = {}
    for side, eye_name in SIDES:
        unit = keys.key_blocks.get(f"eyeBlink{side}")
        if unit is None or eye_name not in eyes:
            continue
        nbr = nbr or _neighbours(me)
        kco = np.empty(n * 3, np.float32)
        unit.data.foreach_get("co", kco)
        closed = neutral + (kco.reshape(-1, 3) - basis)  # the lid closed by the unit, on today's shape
        c_world, r = eye_layers._eye_sphere(eyes[eye_name])
        c = np.asarray(c_world) @ inv[:3, :3].T + inv[:3, 3]
        lids = _lids(all_rows, neutral, kco.reshape(-1, 3) - basis, c)
        if lids is None:
            continue
        up, lo = lids
        mine = np.vstack([up, lo])

        def az(p, c=c):
            return np.arctan2(p[:, 0] - c[0], -(p[:, 1] - c[1]))

        adj = np.zeros_like(closed)
        order = np.argsort(az(neutral[lo[:, 2]]))
        lo_az = az(neutral[lo[order, 2]])
        for col in range(3):  # lash line, margin, rim: each upper row onto the lower row of its kind
            target = closed[lo[order, col]]
            for v, a in zip(up[:, col], az(neutral[up[:, col]]), strict=True):
                p = np.array([np.interp(a, lo_az, target[:, k]) for k in range(3)])
                adj[v] = p - closed[v]
        taken = {int(v) for v in mine.ravel()}
        frontier, seen = {int(v) for v in up[:, 0]}, set(taken)
        for share in RELAX:  # the upper lid's skin follows its lash line
            nxt = {u for v in frontier for u in nbr[v]} - seen
            nxt = {u for u in nxt if neutral[u, 2] > c[2]}
            for u in nxt:
                src = [v for v in nbr[u] if v in frontier]
                adj[u] = share / max(len(src), 1) * sum(adj[v] for v in src) if src else 0.0
            seen |= nxt
            frontier = nxt
        fixed = closed + adj
        lid = np.array(sorted(seen | taken))
        dist = np.linalg.norm(fixed[lid] - c, axis=1)
        inside = dist < r + EYEBALL_GAP
        fixed[lid[inside]] = c + (fixed[lid[inside]] - c) / dist[inside, None] * (r + EYEBALL_GAP)
        name = KEY.format(side=side)
        key = keys.key_blocks.get(name) or character.shape_key_add(name=name, from_mix=False)
        key.data.foreach_set("co", (basis + (fixed - closed)).astype(np.float32).ravel())
        key.slider_min, key.slider_max = 0.0, 1.0
        _drive(key, keys, unit.name)
        mid_up = up[np.argsort(np.abs(az(neutral[up[:, 0]])))[:3], 0]
        mid_lo = lo[np.argsort(np.abs(az(neutral[lo[:, 0]])))[:3], 0]
        gap = float(np.linalg.norm(fixed[mid_up].mean(0) - fixed[mid_lo].mean(0)))
        clip = float(max(0.0, (r - np.linalg.norm(fixed[lid] - c, axis=1)).max()))
        done[side] = (round(gap * 1000, 2), round(clip * 1000, 2))
    me.update()
    return done


#: the corrective eases in as the lid closes (the blink's value cubed: 1 closed, 0.125 half way) - linear, half a blink
#: took half the closing step and shut the eye early (2026-11-08); a simple expression, so Blender runs no Python
EASE = "v * v * v"


def _drive(key: bpy.types.ShapeKey, source: bpy.types.Key, name: str) -> None:
    """`key`'s value follows the blink unit's, eased (EASE)."""
    key.driver_remove("value")
    driver = key.driver_add("value").driver
    driver.type = "SCRIPTED"
    driver.expression = EASE
    var = driver.variables.new()
    var.name = "v"
    var.type = "SINGLE_PROP"
    var.targets[0].id_type = "KEY"
    var.targets[0].id = source
    var.targets[0].data_path = f'key_blocks["{name}"].value'
