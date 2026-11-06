# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's own brows: one hair per follicle (rec 8, the realism brief §6.8) - the industry's way for brows (XGen
and Daz SBH: individually placed hairs on a region with a growth-direction flow, `docs/plans/2026-10-30-research-hair-
eyes-teeth.md` 287), not MakeHuman's `wild_eyebrow`, whose 44 guides duplicated into ~19-strand tufts read as clumps
(the same research, 83-87; the part-by-part gate 2026-11-05: "thick clumped strands against fine single hairs").
NOT STANDARD: our own generator (TAU's CC BY-SA brow generator sits behind a pay-what-you-want form - not fetched).

- **Where:** each brow's region from `wild_eyebrow`'s roots (MakeHuman's CC0 pack) by their hm08 UVs, mapped onto the
  character's current shape - its line and its height along it only; the roots are spread evenly over that band
  (round the pack's own roots they came out in its tufts), denser in the body than the tail.
- **Which way:** off the brow's line (head to tail) by HEAD_ANGLE at its head, turning to TAIL_ANGLE by BODY_AT and
  on; the upper rows turned down and the lower up toward the middle (CONVERGE: a brow's herringbone); each hair
  leaving the skin at RISE and lying down along its length.
- **How long, how thick:** LENGTH (mm) at the head, body and tail; RADIUS at the root tapering to TIP.
Attached as the lashes are (lashes.py: rest shape, surface UVs, Deform Curves on Surface, placed exactly)."""

from __future__ import annotations

import bpy
import numpy as np

from . import lashes

NAME = "JustStage brows"
STYLE = "wild_eyebrow"  # its roots give the region
COUNT = 800  # per brow (real brows: hundreds of hairs each; 600 read sparse beside HD Aaron's)
HEAD_ANGLE, BODY_ANGLE, TAIL_ANGLE, BODY_AT = 70.0, 22.0, 8.0, 0.35  # degrees off the brow's line, toward up
CONVERGE = 14.0  # degrees: the upper rows down, the lower up
SPREAD = 7.0  # degrees of each hair's own randomness
RISE = 18.0  # degrees off the skin at the root, lying down to ~0 at the tip
LENGTH = (5.0, 8.0, 6.0)  # mm at the head, the body and the tail; each +- 20%
RADIUS, TIP = 0.000045, 0.15  # m at the root (brow hairs are coarse: ~0.09 mm across); the tip's share
JITTER = 0.0002  # m: each root's own offset
WIDEN = 1.25  # the band's half-height over the region roots' (their 85th percentile)
TAIL_DENSITY = 0.35  # the tail's density as a share of the body's
MELANIN, REDNESS, MELANIN_SPREAD = 0.92, 0.12, 0.05
#: the brow's soft body under the coarse hairs (CC5's brows lay a soft base layer under their hair cards; MetaHuman's
#: strand brows hold fine short hairs among the coarse ones): FINE hairs a brow, at FINE_LENGTH x the coarse ones'
#: length, FINE_RADIUS thick, lighter - with the painted brows gone from the skins (2026-11-06) the 800 coarse hairs
#: alone read thin beside HD Aaron's
FINE, FINE_LENGTH, FINE_RADIUS, FINE_MELANIN = 1400, 0.5, 0.000022, 0.8
POINTS = len(lashes.PROBE)  # place() measures each curve's move on these many points


def region_uvs(style: str = STYLE) -> np.ndarray:
    """A pack style's root UVs on hm08's own map (the pack's surface UVs): `wild_eyebrow`'s by default."""
    from ... import paths
    from .groom import PACK

    with bpy.data.libraries.load(str(paths.makehuman(*PACK)), link=False) as (src, dst):
        dst.objects = [style] if style in src.objects else []
    if not dst.objects:
        from ...core.commands import CommandError

        raise CommandError(f"the hair pack has no {style!r}; run: python tools/fetch_data.py")
    obj = dst.objects[0]
    data = obj.data.attributes["surface_uv_coordinate"].data
    uv = np.empty(len(data) * 2, np.float32)
    data.foreach_get("vector", uv)
    curves = obj.data
    bpy.data.objects.remove(obj)
    bpy.data.hair_curves.remove(curves)
    return uv.reshape(-1, 2).astype(np.float64)


def strands(body: bpy.types.Object, seed: int = 11):
    """Both brows' hairs on the body's current shape, in world space: (strands, radii, melanin per strand)."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    rng = np.random.default_rng(seed)
    region = lashes.surface_points(body, region_uvs())
    to_local = np.array(body.matrix_world.inverted())
    to_world = np.array(body.matrix_world)
    tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())  # its local space

    def nearest(p):
        q = to_local[:3, :3] @ p + to_local[:3, 3]
        hit, normal = (np.array(x) for x in tree.find_nearest(Vector(q))[:2])
        n = to_world[:3, :3] @ normal
        return to_world[:3, :3] @ hit + to_world[:3, 3], n / np.linalg.norm(n)

    found, radii, melanin = [], [], []
    t_points = np.linspace(0.0, 1.0, POINTS)
    for side in (-1.0, 1.0):  # the character's right (-X), left
        roots = region[np.sign(region[:, 0]) == side]
        if len(roots) < 10:
            continue
        lateral = np.abs(roots[:, 0])
        head = roots[lateral <= np.quantile(lateral, 0.1)].mean(0)
        tail = roots[lateral >= np.quantile(lateral, 0.9)].mean(0)
        axis = tail - head
        span = np.linalg.norm(axis)
        axis /= span
        s_of = np.clip((roots - head) @ axis / span, 0.0, 1.0)
        # the brow's middle line and half-height by place along it (its height across the line, upward)
        up_world = np.array([0.0, 0.0, 1.0])
        across = up_world - (up_world @ axis) * axis
        across /= np.linalg.norm(across)
        bins = np.minimum((s_of * 8).astype(int), 7)
        middle = np.array([np.median(((roots - head) @ across)[bins == b]) if (bins == b).any() else 0.0
                           for b in range(8)])
        half = np.array([np.quantile(np.abs((roots - head) @ across - middle[b])[bins == b], 0.85)
                         if (bins == b).sum() > 3 else 0.004 for b in range(8)])
        # roots spread evenly over the brow's band (MakeHuman's roots sit in tufts): s along it, denser in the body,
        # t across its height at that place
        s_all = rng.uniform(0.0, 1.0, (COUNT + FINE) * 3)
        keep = rng.uniform(0.0, 1.0, len(s_all)) < np.where(s_all < 0.6, 1.0,
                                                            1.0 - (1.0 - TAIL_DENSITY) * (s_all - 0.6) / 0.4)
        s_all = s_all[keep][: COUNT + FINE]
        for k_hair, s0 in enumerate(s_all):
            fine = k_hair >= COUNT  # the soft body's hairs after the coarse ones
            b0 = min(int(s0 * 8), 7)
            t0 = rng.uniform(-1.0, 1.0)
            place = head + s0 * span * axis + (np.interp(s0, (np.arange(8) + 0.5) / 8, middle)
                                               + t0 * WIDEN * np.interp(s0, (np.arange(8) + 0.5) / 8, half)) * across
            root, normal = nearest(place + rng.normal(0.0, JITTER, 3))
            s = float(np.clip((root - head) @ axis / span, 0.0, 1.0))
            b = min(int(s * 8), 7)
            t = float(np.clip(((root - head) @ across - middle[b]) / max(half[b], 1e-4), -1.0, 1.0))
            u = axis - (axis @ normal) * normal
            u /= np.linalg.norm(u)
            v = np.cross(normal, u)
            v *= np.sign(v @ up_world) or 1.0
            angle = np.interp(s, [0.0, BODY_AT, 1.0], [HEAD_ANGLE, BODY_ANGLE, TAIL_ANGLE])
            angle += -CONVERGE * t + rng.normal(0.0, SPREAD)
            a = np.radians(angle)
            flat = np.cos(a) * u + np.sin(a) * v
            curl = np.radians(rng.normal(0.0, 8.0))
            rise = np.radians(RISE) * (1.0 - t_points) ** 1.5
            turn = curl * t_points
            sideways = np.cross(normal, flat)
            heading = np.cos(turn)[:, None] * flat + np.sin(turn)[:, None] * sideways
            d = np.cos(rise)[:, None] * heading + np.sin(rise)[:, None] * normal
            length = 0.001 * np.interp(s, [0.0, 0.4, 1.0], LENGTH) * rng.uniform(0.8, 1.2) * (FINE_LENGTH if fine else 1.0)
            steps = np.vstack([np.zeros(3), d[:-1] * length / (POINTS - 1)])
            strand = root - 0.0001 * normal + np.cumsum(steps, axis=0)
            for i in range(1, POINTS):  # off the skin (a groom's collision pass)
                q = to_local[:3, :3] @ strand[i] + to_local[:3, 3]
                near, n_near = (np.array(x) for x in tree.find_nearest(Vector(q))[:2])
                if (q - near) @ n_near < 0.00008:
                    strand[i:] += to_world[:3, :3] @ (near + 0.00008 * n_near - q)
            found.append(strand)
            radii.append((FINE_RADIUS if fine else RADIUS) * np.interp(t_points, [0.0, 1.0], [1.0, TIP]))
            melanin.append(float(np.clip((FINE_MELANIN if fine else MELANIN) + rng.normal(0.0, MELANIN_SPREAD), 0.0, 1.0)))
    return found, radii, melanin


def make(character: bpy.types.Object, seed: int = 11) -> bpy.types.Object:
    """JustStage's brows on the character, replacing its brows: one groom for both (part "eyebrows")."""
    from . import groom

    groom._check_surface(character)
    found, radii, melanin = strands(character, seed)
    rest, uvs = lashes.to_rest(character, found)
    curves = bpy.data.hair_curves.new(NAME)
    curves.add_curves([POINTS] * len(rest))
    curves.position_data.foreach_set("vector", rest.astype(np.float32).ravel())
    curves.attributes.new("radius", "FLOAT", "POINT").data.foreach_set(
        "value", np.concatenate(radii).astype(np.float32))
    curves.attributes.new("melanin", "FLOAT", "CURVE").data.foreach_set("value", np.array(melanin, np.float32))
    curves.attributes.new("redness", "FLOAT", "CURVE").data.foreach_set(
        "value", np.full(len(rest), REDNESS, np.float32))
    curves.attributes.new("surface_uv_coordinate", "FLOAT2", "CURVE").data.foreach_set(
        "vector", uvs.astype(np.float32).ravel())
    curves.surface_uv_map = groom.SURFACE_UV
    obj = bpy.data.objects.new(NAME, curves)
    obj.modifiers.new("Surface Deform", "NODES").node_group = lashes._deform_group()
    groom.remove_part(character, "eyebrows")
    groom._attach(character, [obj], "eyebrows")
    curves.materials.append(groom.hair_material(f"JustStage Hair ({obj.name})"))
    to_local = np.array(character.matrix_world.inverted())
    wanted = np.array(found) @ to_local[:3, :3].T + to_local[:3, 3]
    miss = lashes.place(obj, rest[:, 0], wanted)
    print(f"brows: {len(rest)} hairs, {POINTS} points each, within {miss * 1000:.4f} mm")
    return obj
