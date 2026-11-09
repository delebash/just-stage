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
#: per brow (real brows: hundreds of hairs each; 600 read sparse beside HD Aaron's). 800 -> 1200 on 2026-11-08 (with
#: FINE 1400 -> 2000 at FINE_MELANIN 0.8 -> 0.92), judged by eye beside him at the face and eye views
#: (`.dev/gate/parts/2026-11-08layers`): a layer diagnostic (his cards on our face) made our brows the eyes' main fault -
#: grey, thin, floating; grown denser and darker they read as real brows
COUNT = 1200
HEAD_ANGLE, BODY_ANGLE, TAIL_ANGLE, BODY_AT = 70.0, 22.0, 8.0, 0.35  # degrees off the brow's line, toward up
CONVERGE = 14.0  # degrees: the upper rows down, the lower up
SPREAD = 7.0  # degrees of each hair's own randomness
RISE = 18.0  # degrees off the skin at the root, lying down to ~0 at the tip
LENGTH = (5.0, 8.0, 6.0)  # mm at the head, the body and the tail; each +- 20%
RADIUS, TIP = 0.000035, 0.15  # m at the root (~0.07 mm across: 0.09 read as a brush beside HD Aaron's); the tip's share
JITTER = 0.0002  # m: each root's own offset
WIDEN = 1.25  # the band's half-height over the region roots' (their 85th percentile)
TAIL_DENSITY = 0.35  # the tail's density as a share of the body's
#: the roots' spread across the band's height, a bell of EDGE_SD half-heights - densest along the middle, thinning to
#: the edges, a few strays above (to EDGE_ABOVE), none below the band (the lid the blink moves). Even (None) gave hard
#: upper and lower edges, a block beside HD Aaron's soft brows; 0.55 soft, 0.4 a thin line (2026-11-09,
#: `.dev/gate/parts/2026-11-09browedge`, the gate's man and the Average woman)
EDGE_SD, EDGE_ABOVE = 0.55, 1.25
#: 2026-11-06, the clean-input gate's eye view: ours a black bar with a brush of upright hairs at its head, each hair
#: straight; HD Aaron's dark grey with about a quarter white, sparser at the head, each hair arching toward the tail
HEAD_DENSITY, HEAD_TO = 0.45, 0.2  # the head's density as a share of the body's, rising to it by HEAD_TO
BEND = 30.0  # degrees a hair standing square to the brow's line turns toward the tail along its length (x sin)
#: the share of the coarse hairs that are white - a character's own (greying): none by default (gate run 10: a fifth
#: on everyone made every brow whitish); HD Aaron's about a fifth
GREY_SHARE, GREY_MELANIN = 0.0, 0.05
#: a dark brown, not black: at 0.92 / 0.12 (tuned 11-08 beside HD Aaron, a dark-haired man) a woman's brows read as a
#: grey-black bar at the eye view and grey smoke at the face view - black hairs thinner than a pixel averaged with the
#: skin (2026-11-09, `.dev/gate/parts/2026-11-09browcol`; on him brown is no worse)
MELANIN, REDNESS, MELANIN_SPREAD = 0.8, 0.3, 0.05
#: the brow's soft body under the coarse hairs (CC5's brows lay a soft base layer under their hair cards; MetaHuman's
#: strand brows hold fine short hairs among the coarse ones): FINE hairs a brow, at FINE_LENGTH x the coarse ones'
#: length, FINE_RADIUS thick, lighter - with the painted brows gone from the skins (2026-11-06) the 800 coarse hairs
#: alone read thin beside HD Aaron's
FINE, FINE_LENGTH, FINE_RADIUS, FINE_MELANIN = 2000, 0.5, 0.000022, 0.8
POINTS = len(lashes.PROBE)  # place() measures each curve's move on these many points
#: women's brows sparser than men's - the share of the hairs kept by the gender macro (2026-11-09,
#: `.dev/gate/parts/2026-11-09browcol`: 0.7 read the most natural on the Average woman, skin between the hairs; 1.0 is
#: HD Aaron's density), culled live by DENSITY_GROUP: a gender drag must not regrow the brows (refit_lashes' 1.84 s a
#: step stalled the slider)
DENSITY_BY_SEX = (0.7, 1.0)
DENSITY_GROUP, DENSITY_MODIFIER = "JustStage Brow Density", "Density"
#: the band's lower edge (its roots' 10th percentile) at least this many eyeball radii above the eye's centre - about
#: the orbital rim, where a man's brow lies (RESEARCH 14.13 "Where a brow sits"). MakeHuman's region put our roots
#: 6-12.5 mm up (median 8.5) on the lid's top, which the blink moves 5-12 mm, so the hairs swept over the closing lid;
#: HD Aaron's brow starts 13.7 mm above a 13.2 mm eye (1.04 radii). Measured 2026-11-08 on the default man: lifted to
#: the rule (~9 mm) his roots sit 15-22 mm up and the blink moves 4 of 4,400 hairs (1,817 before)
RIM_RADII, RIM_TOLERANCE = 1.0, 0.0005  # m: a band within half a millimetre of the rule is left


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


def strands(body: bpy.types.Object, seed: int = 11, grey_share: float = GREY_SHARE, lift: dict | None = None):
    """Both brows' hairs on the body's current shape, in world space: (strands, radii, melanin per strand). `lift`:
    metres to raise each side's band ({-1.0: right, 1.0: left}) before the hairs are rooted on the skin."""
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
        roots = region[np.sign(region[:, 0]) == side] + np.array([0.0, 0.0, (lift or {}).get(side, 0.0)])
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
        density = np.where(s_all < 0.6, 1.0, 1.0 - (1.0 - TAIL_DENSITY) * (s_all - 0.6) / 0.4)
        density *= np.interp(s_all, [0.0, HEAD_TO], [HEAD_DENSITY, 1.0])
        keep = rng.uniform(0.0, 1.0, len(s_all)) < density
        s_all = s_all[keep][: COUNT + FINE]
        for k_hair, s0 in enumerate(s_all):
            fine = k_hair >= COUNT  # the soft body's hairs after the coarse ones
            b0 = min(int(s0 * 8), 7)
            t0 = rng.uniform(-1.0, 1.0) if EDGE_SD is None else _across(rng)
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
            sideways = np.cross(normal, flat)
            toward_tail = 1.0 if sideways @ u > 0 else -1.0  # turning by +angle moves the heading toward the tail
            turn = (curl + toward_tail * np.radians(BEND) * max(np.sin(a), 0.0)) * t_points  # never past the line
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
            own = FINE_MELANIN if fine else (GREY_MELANIN if rng.uniform() < grey_share else MELANIN)
            melanin.append(float(np.clip(own + rng.normal(0.0, MELANIN_SPREAD), 0.0, 1.0)))
    return found, radii, melanin


def rim_lift(character: bpy.types.Object, found: list) -> dict:
    """Per side, how far the band must rise so its roots' 10th percentile sits RIM_RADII eyeball radii above that
    side's eye centre (the eye parts' spheres); empty when both already do."""
    from ..head import eye_layers, parts

    eyes = parts.parts_of(character)
    roots = np.array([s[0] for s in found])
    lift = {}
    for name in ("eyeLeft", "eyeRight"):
        if name not in eyes:
            continue
        centre, radius = eye_layers._eye_sphere(eyes[name])
        side = float(np.sign(centre[0]))
        heights = roots[np.sign(roots[:, 0]) == side, 2] - centre[2]
        if len(heights):
            short = RIM_RADII * radius - float(np.percentile(heights, 10))
            if short > 0:
                lift[side] = short
    return lift


def rimmed(character: bpy.types.Object, seed: int = 11, grey_share: float = GREY_SHARE):
    """`strands` with each band lifted onto the rim (RIM_RADII): grown, measured, grown again - up to three times, as
    rooting on the skin's curve can land a little short. What `make` places."""
    found, radii, melanin = strands(character, seed, grey_share)
    total: dict = {}
    for _ in range(3):
        lift = {side: dz for side, dz in rim_lift(character, found).items() if dz > RIM_TOLERANCE}
        if not lift:
            break
        for side, dz in lift.items():
            total[side] = total.get(side, 0.0) + dz
        found, radii, melanin = strands(character, seed, grey_share, total)
    return found, radii, melanin


def _across(rng) -> float:
    """A root's place across the band (half-heights from its middle): a bell of EDGE_SD, redrawn past the band's lower
    edge or EDGE_ABOVE."""
    while True:
        t = rng.normal(0.0, EDGE_SD)
        if -1.0 <= t <= EDGE_ABOVE:
            return t


def make(character: bpy.types.Object, seed: int = 11, grey_share: float = GREY_SHARE) -> bpy.types.Object:
    """JustStage's brows on the character, replacing its brows: one groom for both (part "eyebrows")."""
    from . import groom

    groom._check_surface(character)
    found, radii, melanin = rimmed(character, seed, grey_share)
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
    set_density(character)
    print(f"brows: {len(rest)} hairs, {POINTS} points each, within {miss * 1000:.4f} mm")
    return obj


def _density_group() -> bpy.types.NodeTree:
    """A random share of the curves deleted - Geometry Nodes' Delete Geometry by a Random Value per curve (its index the
    ID, so the same hairs go at every share): the input "Kept" is the share left."""
    group = bpy.data.node_groups.get(DENSITY_GROUP)
    if group is not None:
        return group
    group = bpy.data.node_groups.new(DENSITY_GROUP, "GeometryNodeTree")
    group.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    kept = group.interface.new_socket("Kept", in_out="INPUT", socket_type="NodeSocketFloat")
    kept.default_value, kept.min_value, kept.max_value = 1.0, 0.0, 1.0
    group.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    nodes, links = group.nodes, group.links
    inp, out = nodes.new("NodeGroupInput"), nodes.new("NodeGroupOutput")
    drop = nodes.new("ShaderNodeMath")
    drop.operation = "SUBTRACT"
    drop.inputs[0].default_value = 1.0
    links.new(inp.outputs["Kept"], drop.inputs[1])
    pick = nodes.new("FunctionNodeRandomValue")
    pick.data_type = "BOOLEAN"
    pick.inputs["Seed"].default_value = 17
    links.new(drop.outputs[0], pick.inputs["Probability"])
    delete = nodes.new("GeometryNodeDeleteGeometry")
    delete.domain = "CURVE"
    links.new(inp.outputs["Geometry"], delete.inputs["Geometry"])
    links.new(next(o for o in pick.outputs if o.type == "BOOLEAN"), delete.inputs["Selection"])
    links.new(delete.outputs["Geometry"], out.inputs[0])
    return group


def set_density(character: bpy.types.Object) -> None:
    """The character's brows thinned to its sex's share (DENSITY_BY_SEX by the gender macro) - on growing, on a gender
    drag (body.set_slider) and on a library groom put on it."""
    kept = float(np.interp(character.juststage.gender, (0.0, 1.0), DENSITY_BY_SEX))
    for obj in bpy.data.objects:
        if obj.juststage.part_of != character.juststage.character_id or obj.juststage.part != "eyebrows":
            continue
        mod = obj.modifiers.get(DENSITY_MODIFIER)
        if mod is None:
            mod = obj.modifiers.new(DENSITY_MODIFIER, "NODES")
            mod.node_group = _density_group()
            obj.modifiers.move(len(obj.modifiers) - 1, 0)  # before the surface deform: fewer curves to carry
        socket = next(i for i in mod.node_group.interface.items_tree if getattr(i, "name", "") == "Kept")
        getattr(mod.properties.inputs, socket.identifier).value = kept  # Blender 5.x's modifier inputs (groom.py)
        obj.update_tag()
