# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's own lashes: strands at real counts, rooted along the lids' edge and attached to the body like every
groom (moved from the face test's `_strand_lashes`, rec 7 approved 2026-10-30: "brows and lashes at real counts (lashes
90-160 upper)"; `docs/plans/2026-10-30-research-hair-eyes-teeth.md`: 90-160 upper in 5-6 rows, 75-80 lower in 3-4, per
eye, 10+ points each for the curl). MetaHuman's way - strand grooms - as Blender hair curves:
- roots on the lid's front skin just past the opening's edge (modules/head/eyes.py), found by rays from in front, in a
  band just past the edge (the rows), none by the inner corner;
- each lash leaves the lid at the measured angle off straight ahead and curls away from the eye, fanned as measured
  from the front (FAN), longest just outside the middle, clumped in fours;
- attached as Blender attaches hair: the body as the Curves' surface, each strand's root UV, and Deform Curves on
  Surface carrying the strands from the surface's rest shape to its current one - so they follow the lid on any
  character, and through its shape keys. Made on one character, they are moved into rest space by each root
  triangle's frame, then placed exactly through the node itself: each curve's rigid move is measured on a probe shape
  and inverted (Kabsch). The library's "JustStage lashes" asset is built this way (tools/build_library.py), and the
  face test makes its lashes with it."""

from __future__ import annotations

import bpy
import numpy as np

#: per eye and lid: count, length at the longest and at the corners (mm), the angle off straight ahead at the root seen
#: from the side (+ away from the eye: up for the upper lid), the curl to the tip (degrees), how far past the opening's
#: edge the roots sit (degrees), the root radius (m). Counts: StatPearls' 90-160 upper, 75-80 lower. Angles and lengths
#: measured on 50 Japanese adults from the side (oatext.com, "A study of normal eyelashes in Japanese individuals"):
#: upper 61 deg from vertical in men (women 72), 7.3 mm, 60% straight in men; lower 90 deg (straight ahead; women 100),
#: 5.0 mm, all curly. The paper doesn't say which way its vertical points; its remark that the lower lashes "grow in
#: the upward direction against gravity" (women's 100 above straight ahead) fits only a vertical pointing down - so the
#: men's upper lashes leave the lid ~29 deg BELOW straight ahead (women's ~18), down and forward over the top of the
#: eyeball, a dark band at the margin. The face test's rounds 57-65 read it the other way (rise 0 to +15): a fringe of
#: spikes standing above the lid. Lengths 0.65 / 0.55 of the study's: at full length round 79's 4096-px close-up drew
#: long spikes across the iris and out past the outer corner, where its painting shows a fine short lash line.
#: 2026-11-06: 180 upper at 0.08 mm, melanin 1.0 - the approved design's piece 3 ("measured to make a lash line",
#: proof (4), 2026-11-05) - never put in the code until the clean-input gate showed the lash line thin
UPPER = {"count": 180, "long": 7.0, "short": 3.8, "rise": 0.0, "curl": 50.0, "band": (0.2, 1.0), "radius": 0.00008,
         "melanin": 1.0}  # fmt: skip
LOWER = {"count": 80, "long": 3.8, "short": 1.8, "rise": 5.0, "curl": 25.0, "band": (0.2, 0.8), "radius": 0.000025,
         "melanin": 0.6}  # fmt: skip  # lower lashes are finer and lighter
#: Changed 2026-11-05 (the part-by-part gate): with the eyes opened to an adult's 9 mm (body_create.EYE_OPEN) the
#: lashes read as a dark line along the lid, seen end-on - HD Aaron's and photographed men's sweep up into a fringe. The
#: study's 61 deg "from vertical" read the other way (vertical up: ~29 deg ABOVE straight ahead) fits that: here they
#: leave the lid straight ahead and curl 50 deg up, ~25 deg up on average; the study's full lengths less ~5% (7.0 /
#: 3.8 mm); upper 150, lower 80 (inside StatPearls' counts). The narrow lid that made long lashes cross the iris
#: (round 79) is gone. Compared: `.dev/gate/parts/eyes/eevee_eye_ours_lash_{base,long,curl}.png` against Aaron's.
CLUMP, CLUMP_PULL = 4, 0.5  # real lashes group: neighbours' tips pulled halfway together, more toward the tip
#: the fan seen from the front: (share of the way from the inner corner to the outer, the lash's angle from the line
#: through the corners toward the outer one, degrees) - measured on the lower lid of Korean adults (Korea University,
#: "Changes in the horizontal angular direction of lower eyelashes with age": medial 137, central 72, lateral 25);
#: the upper lid mirrored, no measurement found
FAN = ((1 / 6, 137.0), (0.5, 72.0), (5 / 6, 25.0))
FACE_FORWARD = np.array([0.0, -1.0, 0.0])  # a JustStage character faces -Y
POINTS = 12  # the research: 10+ points each for the curl (the pack's lashes have 5)
TIP = 0.12  # the tip's radius as a share of the root's (0.25 read as blunt spikes at 4096 px)
REDNESS = 0.25  # with melanin 0.95, near black-brown
NAME = "JustStage lashes"
DEFORM = "JustStage Surface Deform"


def clump(strands: list, start: int) -> None:
    """Lashes from `start` on, in groups of CLUMP neighbours, each pulled toward its group's mean shape - by nothing at
    the root, CLUMP_PULL at the tip (squared along the lash)."""
    t = np.linspace(0.0, 1.0, POINTS)[:, None] ** 2
    for g in range(start, len(strands), CLUMP):
        group = strands[g : g + CLUMP]
        centre = np.mean(group, axis=0)
        for i, strand in enumerate(group):
            strands[g + i] = strand + (centre - strand) * t * CLUMP_PULL


#: on base v2, how far into the lid (degrees about the eye) the lashes' rows reach from the lash line
LASH_ROWS = 1.2
#: m: a lash's root is looked for this far off the eyeball at most - the lid it grows from is the skin nearest the eye
ROOT_REACH = 0.008


def _lash_line(body: bpy.types.Object, o, side: float):
    """Base v2's lash line on one lid of one eye (modules/body/base.py's rows): (azimuths, elevations) about the eye,
    sorted - None on hm08 itself."""
    from ..body import base, build
    from ..head.eyes import angles

    if body.juststage.base_version < base.VERSION:
        return None
    rows = base.rows()
    lash = rows[rows[:, 0] >= 0, 0]
    m = np.array(body.matrix_world)
    pts = build.shaped_coords(body)[lash] @ m[:3, :3].T + m[:3, 3]
    pts = pts[np.linalg.norm(pts - o.centre, axis=1) < o.radius + 0.008]  # this eye's
    az, el, _d = angles(pts, o.centre)
    mid = np.interp(az, o.centres, (o.upper + o.lower) / 2)
    keep = el > mid if side > 0 else el < mid
    if keep.sum() < 4:
        return None
    order = np.argsort(az[keep])
    return az[keep][order], el[keep][order]


def strands(body: bpy.types.Object, openings: dict, seed: int = 7):
    """Both eyes' lashes on the body's current shape, in world space: (strands, radii, melanin per strand, roots that
    found no lid)."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    from ..head.eyes import direction

    rng = np.random.default_rng(seed)
    to_local = np.array(body.matrix_world.inverted())
    to_world = np.array(body.matrix_world)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(body, depsgraph)  # its local space
    found, radii, melanin, missed = [], [], [], 0
    for eye_name, o in openings.items():
        # the eye whole, or with its cornea split off (the face test splits it)
        eyes = [bpy.data.objects[n] for n in (eye_name, f"{eye_name} cornea") if n in bpy.data.objects]
        eye_trees = [(BVHTree.FromObject(e, depsgraph), np.array(e.matrix_world.inverted()),
                      np.array(e.matrix_world), 0.0002) for e in eyes]  # fmt: skip
        corner_az = np.array([o.inner, o.outer])
        corner_el = np.interp(corner_az, o.centres, (o.upper + o.lower) / 2)
        corners = o.centre + o.radius * direction(corner_az, corner_el)
        lateral = corners[1] - corners[0]  # along the line through the corners, toward the outer one
        lateral -= (lateral @ FACE_FORWARD) * FACE_FORWARD
        lateral /= np.linalg.norm(lateral)
        up = np.cross(lateral, FACE_FORWARD)
        up *= np.sign(up[2])
        for spec, side in ((UPPER, 1.0), (LOWER, -1.0)):
            n = spec["count"]
            block = len(found)  # this lid's lashes, in order along it (f is sorted): the clumps are neighbours
            f = np.sort(rng.uniform(0.06, 0.97, n))  # the share of the way from the inner corner to the outer
            az = o.inner + f * (o.outer - o.inner)
            el = np.interp(az, o.centres, o.upper if side > 0 else o.lower) + side * rng.uniform(*spec["band"], n)
            line = _lash_line(body, o, side)
            if line is not None:  # base v2: the lashes grow from its lash line (the margin's front edge), in rows
                el = np.interp(az, *line) + side * rng.uniform(0.0, LASH_ROWS, n)
            for k in range(n):
                # from in front onto the lid; this close to its edge a ray can slip past the margin - then a little
                # further onto the lid, up to 3 deg
                for extra in (0.0, 0.5, 1.0, 2.0, 3.0):
                    el_k = el[k] + side * extra
                    d_k = direction(az[k : k + 1], np.array([el_k]))[0]
                    # from ROOT_REACH off the eyeball (the lash line sits ~2.3 mm off), ending 5 mm inside it: from
                    # 20 mm out a ray at the inner corner started inside the nose and rooted a lash there (the
                    # lower lid's ledge, test_lashes 2026-11-08: 33.5 mm from the eye)
                    start = o.centre + d_k * (o.radius + ROOT_REACH)
                    s_local = to_local[:3, :3] @ start + to_local[:3, 3]
                    hit = tree.ray_cast(Vector(s_local), Vector(to_local[:3, :3] @ -d_k), ROOT_REACH + 0.005)
                    if hit[0] is not None:
                        break
                if hit[0] is None:
                    missed += 1
                    continue
                el[k] = el_k
                normal = to_world[:3, :3] @ np.array(hit[1])
                root = to_world[:3, :3] @ np.array(hit[0]) + to_world[:3, 3] - 0.0001 * normal / np.linalg.norm(normal)
                fan = np.radians(np.interp(f[k], *zip(*FAN, strict=True)) + rng.normal(0.0, 8.0))
                shape = np.sin(np.pi * f[k] ** 1.3)
                length = 0.001 * rng.uniform(0.85, 1.1) * (spec["short"] + (spec["long"] - spec["short"]) * shape)
                t = np.linspace(0.0, 1.0, POINTS)
                theta = np.radians(spec["rise"] + rng.normal(0.0, 5.0))
                theta = theta + np.radians(spec["curl"] + rng.normal(0.0, 10.0)) * t**1.5
                # seen from the side, theta off straight ahead, away from the opening when positive (up for the upper
                # lid) and toward it when negative (a drooping lash); seen from the front, fanned (FAN) - the
                # sideways part always toward its own corner, so an outer lash that droops still points outward
                d = (np.cos(theta)[:, None] * FACE_FORWARD + (side * np.sin(theta) * np.sin(fan))[:, None] * up
                     + (np.abs(np.sin(theta)) * np.cos(fan))[:, None] * lateral)  # fmt: skip
                d /= np.linalg.norm(d, axis=1, keepdims=True)
                steps = np.vstack([np.zeros(3), d[:-1] * length / (POINTS - 1)])
                strand = root + np.cumsum(steps, axis=0)
                for i in range(1, POINTS):  # out of the skin (a groom's collision pass): by the nose
                    for bvh, local, world, gap in [(tree, to_local, to_world, 0.0001), *eye_trees]:
                        # and off the eye: a drooping lash meets the cornea
                        q = local[:3, :3] @ strand[i] + local[:3, 3]
                        near, n_near = (np.array(x) for x in bvh.find_nearest(Vector(q))[:2])
                        if (q - near) @ n_near < gap:
                            moved = near + gap * n_near - q
                            strand[i:] += world[:3, :3] @ moved  # the rest of the lash follows
                found.append(strand)
                radii.append(spec["radius"] * np.interp(t, [0.0, 1.0], [1.0, TIP]))
                melanin.append(spec["melanin"])
            clump(found, block)
    return found, radii, melanin, missed


def _triangles(body: bpy.types.Object) -> tuple[np.ndarray, np.ndarray]:
    """The body's own polygons as triangles (fans, as Blender splits them): their vertex and loop indices."""
    from ...core.makehuman import skin_mask

    skin = skin_mask(len(body.data.vertices))
    tris, loops = [], []
    for p in body.data.polygons:
        v, lo = list(p.vertices), list(p.loop_indices)
        if not skin[v].all():  # a helper's polygon
            continue
        for i in range(1, len(v) - 1):
            tris.append((v[0], v[i], v[i + 1]))
            loops.append((lo[0], lo[i], lo[i + 1]))
    return np.array(tris), np.array(loops)


def _frames(co: np.ndarray, tris: np.ndarray) -> np.ndarray:
    """Each triangle's frame (columns: its first edge, the normal's cross with it, its normal) - as Deform Curves on
    Surface turns a strand with its triangle."""
    a, b, c = co[tris[:, 0]], co[tris[:, 1]], co[tris[:, 2]]
    x = b - a
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    n = np.cross(b - a, c - a)
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    y = np.cross(n, x)
    return np.stack([x, y, n], axis=2)


def to_rest(body: bpy.types.Object, world_strands: list) -> tuple[np.ndarray, np.ndarray]:
    """Strands made on the body's current shape (world space) moved to its rest shape (the basis: what Blender's
    `rest_position` holds), in the body's own space, and each root's surface UV."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    from ..body import build

    tris, loops = _triangles(body)
    now = build.shaped_coords(body)
    keys = body.data.shape_keys
    rest = np.empty(len(body.data.vertices) * 3, np.float32)
    (keys.reference_key.data if keys else body.data.vertices).foreach_get("co", rest)
    rest = rest.reshape(-1, 3).astype(np.float64)
    uv = np.empty(len(body.data.loops) * 2, np.float32)
    body.data.uv_layers[_surface_uv()].data.foreach_get("uv", uv)
    uv = uv.reshape(-1, 2)
    tree = BVHTree.FromPolygons([Vector(v) for v in now], tris.tolist())
    to_local = np.array(body.matrix_world.inverted())
    f_now, f_rest = _frames(now, tris), _frames(rest, tris)
    out, uvs = [], []
    for strand in world_strands:
        local = strand @ to_local[:3, :3].T + to_local[:3, 3]
        hit, _normal, tri, _dist = tree.find_nearest(Vector(local[0]))
        a, b, c = now[tris[tri]]
        w = _barycentric(np.array(hit), a, b, c)
        origin_now = w @ now[tris[tri]]
        origin_rest = w @ rest[tris[tri]]
        turn = f_rest[tri] @ f_now[tri].T
        out.append((local - origin_now) @ turn.T + origin_rest)
        uvs.append(w @ uv[loops[tri]])
    return np.array(out), np.array(uvs)


def surface_points(body: bpy.types.Object, uvs: np.ndarray) -> np.ndarray:
    """Surface UVs (hm08's map, the grooms' surface UVs) to points on the body's current shape, in world space - each
    UV's triangle found among its nearest triangle centres in UV (Blender's k-d tree), its barycentric weights taken to
    the shaped vertices. UVs that fall in no triangle are left out."""
    from mathutils import Vector
    from mathutils.kdtree import KDTree

    from ..body import build

    tris, loops = _triangles(body)
    uv = np.empty(len(body.data.loops) * 2, np.float32)
    body.data.uv_layers[_surface_uv()].data.foreach_get("uv", uv)
    tri_uv = uv.reshape(-1, 2).astype(np.float64)[loops]  # (n, 3, 2)
    centres = tri_uv.mean(1)
    tree = KDTree(len(centres))
    for i, c in enumerate(centres):
        tree.insert((c[0], c[1], 0.0), i)
    tree.balance()
    now = build.shaped_coords(body)
    mw = np.array(body.matrix_world)
    out = []
    for q in uvs:
        for _co, k, _d in tree.find_n(Vector((q[0], q[1], 0.0)), 16):
            a, b, c = tri_uv[k]
            m = np.array([[b[0] - a[0], c[0] - a[0]], [b[1] - a[1], c[1] - a[1]]])
            if abs(np.linalg.det(m)) < 1e-14:
                continue
            s, t = np.linalg.solve(m, q - a)
            if s >= -1e-6 and t >= -1e-6 and s + t <= 1 + 1e-6:
                p = now[tris[k]].T @ np.array([1 - s - t, s, t])
                out.append(mw[:3, :3] @ p + mw[:3, 3])
                break
    return np.array(out)


def _barycentric(p, a, b, c) -> np.ndarray:
    v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1
    den = d00 * d11 - d01 * d01
    v = (d11 * d20 - d01 * d21) / den
    w = (d00 * d21 - d01 * d20) / den
    return np.array([1.0 - v - w, v, w])


def _surface_uv() -> str:
    from .groom import SURFACE_UV

    return SURFACE_UV


#: a probe for the node's move of each curve: twelve points spread over a millimetre around its root (not on a line)
PROBE = 0.001 * np.array(
    [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [0, 1, 1],
     [1, 0, 1], [-1, 0, 0], [0, -1, 0], [0, 0, -1], [1, 1, 1], [-1, -1, 0]], dtype=np.float64
)  # fmt: skip


def _evaluated_local(obj: bpy.types.Object) -> np.ndarray:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    curves = obj.evaluated_get(depsgraph).data
    pos = np.empty(len(curves.points) * 3, np.float32)
    curves.attributes["position"].data.foreach_get("vector", pos)
    return pos.reshape(len(curves.curves), POINTS, 3).astype(np.float64)


def _set_positions(obj: bpy.types.Object, positions: np.ndarray) -> None:
    obj.data.position_data.foreach_set("vector", positions.astype(np.float32).ravel())
    obj.data.update_tag()


def _rigid(source: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per curve, the rotation and shift that best take `source` (n, k, 3) to `target` (Kabsch): target = R @ p + t."""
    sc, tc = source.mean(axis=1, keepdims=True), target.mean(axis=1, keepdims=True)
    h = np.einsum("nki,nkj->nij", source - sc, target - tc)
    u, _s, vt = np.linalg.svd(h)
    d = np.sign(np.linalg.det(np.einsum("nij,njk->nik", vt.transpose(0, 2, 1), u.transpose(0, 2, 1))))
    fix = np.eye(3)[None].repeat(len(h), axis=0)
    fix[:, 2, 2] = d
    r = np.einsum("nij,njk,nkl->nil", vt.transpose(0, 2, 1), fix, u.transpose(0, 2, 1))
    t = tc[:, 0] - np.einsum("nij,nj->ni", r, sc[:, 0])
    return r, t


def place(obj: bpy.types.Object, rest_roots: np.ndarray, wanted: np.ndarray) -> float:
    """Each strand's rest positions set so that Deform Curves on Surface puts it at `wanted` (the curves object's
    space): the node's move of each curve - rigid, whatever the points - measured on PROBE and inverted. Returns the
    largest miss left (m)."""
    probe = rest_roots[:, None, :] + PROBE[None]
    _set_positions(obj, probe)
    r, t = _rigid(probe, _evaluated_local(obj))
    rest = np.einsum("nji,nkj->nki", r, wanted - t[:, None, :])  # p = R^T (q - t)
    _set_positions(obj, rest)
    return float(np.linalg.norm(_evaluated_local(obj) - wanted, axis=2).max())


def _deform_group() -> bpy.types.NodeTree:
    """Blender's Deform Curves on Surface in a node group (as the hair pack's styles carry it)."""
    group = bpy.data.node_groups.get(DEFORM)
    if group is not None:
        return group
    group = bpy.data.node_groups.new(DEFORM, "GeometryNodeTree")
    group.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    group.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    inp, out = group.nodes.new("NodeGroupInput"), group.nodes.new("NodeGroupOutput")
    deform = group.nodes.new("GeometryNodeDeformCurvesOnSurface")
    group.links.new(inp.outputs[0], deform.inputs["Curves"])
    group.links.new(deform.outputs["Curves"], out.inputs[0])
    return group


def make(character: bpy.types.Object, openings: dict | None = None, seed: int = 7) -> bpy.types.Object:
    """JustStage's lashes on the character, replacing its lashes: one groom for both eyes' lids (part "eyelashes")."""
    from ..head import eyes
    from . import groom

    groom._check_surface(character)
    found, radii, melanin, missed = strands(character, openings or eyes.openings(character), seed)
    rest, uvs = to_rest(character, found)
    curves = bpy.data.hair_curves.new(NAME)
    curves.add_curves([POINTS] * len(rest))
    curves.position_data.foreach_set("vector", rest.astype(np.float32).ravel())
    radius = np.concatenate(radii).astype(np.float32)
    curves.attributes.new("radius", "FLOAT", "POINT").data.foreach_set("value", radius)
    # the hair material (groom.py: Principled Hair by each strand's melanin, and its EEVEE stand-in)
    curves.attributes.new("melanin", "FLOAT", "CURVE").data.foreach_set("value", np.array(melanin, dtype=np.float32))
    curves.attributes.new("redness", "FLOAT", "CURVE").data.foreach_set(
        "value", np.full(len(rest), REDNESS, dtype=np.float32)
    )
    curves.attributes.new("surface_uv_coordinate", "FLOAT2", "CURVE").data.foreach_set(
        "vector", uvs.astype(np.float32).ravel()
    )
    curves.surface_uv_map = groom.SURFACE_UV
    obj = bpy.data.objects.new(NAME, curves)
    obj.modifiers.new("Surface Deform", "NODES").node_group = _deform_group()
    groom.remove_part(character, "eyelashes")
    groom._attach(character, [obj], "eyelashes")
    curves.materials.append(groom.hair_material(f"JustStage Hair ({obj.name})"))
    to_local = np.array(character.matrix_world.inverted())
    wanted = np.array(found) @ to_local[:3, :3].T + to_local[:3, 3]
    miss = place(obj, rest[:, 0], wanted)
    print(f"lashes: {len(rest)} strands ({missed} roots missed), {POINTS} points each, within {miss * 1000:.4f} mm")
    return obj


def evaluated_points(obj: bpy.types.Object) -> np.ndarray:
    """Every point of a groom as drawn (its modifiers applied), the groom's own space, flat (points x 3)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    curves = obj.evaluated_get(depsgraph).data
    pos = np.empty(len(curves.points) * 3, np.float32)
    curves.attributes["position"].data.foreach_get("vector", pos)
    return pos.reshape(-1, 3).astype(np.float64)


def keep_in_place(obj: bpy.types.Object, wanted: np.ndarray) -> float:
    """Any groom's rest positions set so that its surface deform draws every point at `wanted` (flat, the groom's
    space) - `place` for curves of any point count: each curve's move measured on PROBE's first points and inverted
    (curves with fewer than three points left as they are). Returns the largest miss left (m) - after a change to the
    surface under the groom (base v2's cut: modules/body/base.py) it is put back where it was drawn."""
    curves = obj.data
    offs = np.empty(len(curves.curves) + 1, np.int32)
    curves.curve_offset_data.foreach_get("value", offs)
    counts = np.diff(offs)
    rest = np.empty(len(curves.points) * 3, np.float32)
    curves.position_data.foreach_get("vector", rest)
    rest = rest.reshape(-1, 3).astype(np.float64)
    roots = rest[offs[:-1]]
    k_of_point = np.arange(len(rest)) - np.repeat(offs[:-1], counts)
    probe = np.repeat(roots, counts, axis=0) + PROBE[np.minimum(k_of_point, len(PROBE) - 1)]
    _set_positions(obj, probe)
    moved = evaluated_points(obj)
    out = rest.copy()
    for k in np.unique(counts):
        if k < 3:
            continue
        which = np.flatnonzero(counts == k)
        idx = offs[which][:, None] + np.arange(k)[None, :]
        r, t = _rigid(probe[idx], moved[idx])
        out[idx] = np.einsum("nji,nkj->nki", r, wanted[idx] - t[:, None, :])
    _set_positions(obj, out)
    return float(np.linalg.norm(evaluated_points(obj) - wanted, axis=1).max())
