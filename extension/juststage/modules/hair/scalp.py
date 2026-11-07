# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's own scalp grooms (rec 11, the realism brief §6.11; character-data-model.md §4: "Generation: Blender's
own hair node groups"): guide curves combed by a style's flow over the scalp, filled to full density by Blender's
Interpolate Hair Curves, shaped by its Clump, Frizz and Noise groups and Set Hair Curve Profile, each strand coloured
by its own melanin with a grey share. The part-by-part gate (2026-11-05): MakeHuman's styles read as sparse clumps
against HD Aaron's dense hair; its `short_hedgehog` is a 5 mm buzz but its roots sit right (hairline 56 mm above the eye,
RESEARCH "Scalp masks tried and dropped": MakeHuman's and MPFB2's masks reach the forehead) - so its roots give the
scalp, here as the guides' roots and as the interpolation's mask texture in hm08's UVs.

A style (STYLES) is a flow and a length by place: SHORT_COMBED - combed back from the hairline, down at the crown
and the sides, long on top (65 mm) and short at the sides and the nape, lifted a little off the scalp on top. NOT
STANDARD: our guide comb (the standard parts - interpolation, clumps, frizz, profile - are Blender's own groups)."""

from __future__ import annotations

import bpy
import numpy as np

from . import brows, lashes

NAME = "JustStage scalp"
REGION_STYLE = "short_hedgehog"
GUIDES = 1600
POINTS = len(lashes.PROBE)  # place() measures each curve's move on these many points
#: strands per square metre of scalp (an adult has ~100,000 hairs on ~600 cm2: ~1.7M; the live view's budget below it)
DENSITY = 1_300_000.0
INTERPOLATION_GUIDES = 5
RADIUS, PROFILE_SHAPE = 0.00004, 0.3  # m at the root (hair ~80 um across), the taper toward the tip
#: a style: lengths (mm) by how far up the head the root sits (the normal's z: -0.3 nape to 0.7 crown), the lift off
#: the scalp on top and at the sides (mm), the comb's sideways sweep
SHORT_COMBED = {"lengths": ((-0.4, 12.0), (0.0, 24.0), (0.35, 45.0), (0.7, 65.0)), "lift": (14.0, 4.0),
                "sweep": 0.15, "frizz": 0.0008, "noise": 0.0015, "clump": 0.25}  # fmt: skip
#: SHORT_TAPER (2026-11-07, on trial against HD Aaron's "Classic Slick Back" in EEVEE): his hair stands off the scalp
#: p50 / p90 13 / 23 mm on top, 4 / 12 at the sides, 8 / 15 at the back, 7 / 13 at the nape, where short combed's stood
#: 5.5 / 11.7, 2.0 / 5.8, 6.1 / 13.1, 4.7 / 12.4, and hung over the ears (RESEARCH §14.14): more lift on top and at the
#: sides, more again at the front hairline, shorter at the sides (by how far the root faces sideways) and the nape
SHORT_TAPER = {"lengths": ((-0.4, 9.0), (0.0, 18.0), (0.35, 42.0), (0.7, 62.0)), "lift": (24.0, 9.0),
               "sweep": 0.15, "frizz": 0.0008, "noise": 0.0015, "clump": 0.35,
               "side_scale": (0.4, 0.85, 0.55), "front_lift": 1.25, "back_lift": 0.6, "side_down": 0.15}  # fmt: skip
STYLES = {"short combed": SHORT_COMBED, "short taper": SHORT_TAPER}
MASK_SIZE = 1024  # the scalp mask in hm08's UVs, texels
MELANIN, MELANIN_SPREAD, REDNESS = 0.82, 0.06, 0.2
GREY_SHARE, GREY_MELANIN = 0.2, 0.05  # grey: a share of strands nearly without pigment


def _flow(point: np.ndarray, normal: np.ndarray, sweep: float, side: float, side_down: float = 0.6) -> np.ndarray:
    """The comb's direction at a point of the scalp: back (+Y; the character faces -Y) on top, down at the back and the
    sides (`side_down`: how much the sides turn down - combed straight down they part from the top's backward hair
    along a bare line above the ear, 2026-11-07), swept a little to the side the point is on - in the skin's tangent
    plane."""
    back, down = np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, -1.0])
    w = np.clip((normal[1] + 0.1) / 0.6, 0.0, 1.0)  # the crown's back half: down
    d = (1 - w) * back + w * down + side_down * abs(normal[0]) * down + sweep * side * np.array([1.0, 0.0, 0.0])
    d -= (d @ normal) * normal
    return d / max(np.linalg.norm(d), 1e-9)


def guides(body: bpy.types.Object, style: dict, seed: int = 5):
    """The style's guide curves on the body's current shape, world space: (strands, roots' scalp UVs)."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    rng = np.random.default_rng(seed)
    uvs = brows.region_uvs(REGION_STYLE)
    pick = rng.choice(len(uvs), min(GUIDES * 3, len(uvs)), replace=False)
    roots = lashes.surface_points(body, uvs[pick])
    # thin to an even spread: one root per cell of a grid the guides' spacing wide
    area = 0.06  # m2 of scalp, about
    cell = np.sqrt(area / GUIDES)
    _, first = np.unique(np.floor(roots / cell).astype(np.int64), axis=0, return_index=True)
    roots = roots[np.sort(first)][:GUIDES]
    to_local = np.array(body.matrix_world.inverted())
    to_world = np.array(body.matrix_world)
    tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())

    def nearest(p):
        q = to_local[:3, :3] @ p + to_local[:3, 3]
        hit, normal = (np.array(x) for x in tree.find_nearest(Vector(q))[:2])
        n = to_world[:3, :3] @ normal
        return to_world[:3, :3] @ hit + to_world[:3, 3], n / np.linalg.norm(n)

    centre_x = float(np.median(roots[:, 0]))
    out = []
    t = np.linspace(0.0, 1.0, POINTS)
    for root in roots:
        surface, normal = nearest(root)
        heights = np.array([z for z, _ in style["lengths"]])
        length = 0.001 * np.interp(normal[2], heights, [mm for _, mm in style["lengths"]]) * rng.uniform(0.85, 1.15)
        lift = 0.001 * np.interp(abs(normal[0]), [0.2, 0.8], style["lift"])
        if "side_scale" in style:  # shorter where the root faces sideways (a taper over the ears)
            lo, hi, scale = style["side_scale"]
            length *= np.interp(abs(normal[0]), [lo, hi], [1.0, scale])
        if "front_lift" in style:  # more lift where the root faces forward (the hairline's rise)
            lift *= 1.0 + (style["front_lift"] - 1.0) * np.clip((-normal[1] - 0.2) / 0.4, 0.0, 1.0)
        if "back_lift" in style:  # less where it faces back (the back and nape lie closer: his 8 / 7 mm p50)
            lift *= 1.0 + (style["back_lift"] - 1.0) * np.clip((normal[1] - 0.2) / 0.4, 0.0, 1.0)
        side = np.sign(surface[0] - centre_x)
        p = surface.copy()
        strand = [p - 0.0001 * normal]
        jitter = rng.normal(0.0, 0.08, 3)
        for k in range(1, POINTS):
            q, n = nearest(p)
            d = _flow(q, n, style["sweep"], side, style.get("side_down", 0.6)) + jitter
            d -= (d @ n) * n
            d /= max(np.linalg.norm(d), 1e-9)
            step = p + d * length / (POINTS - 1)
            q2, n2 = nearest(step)
            height = 0.0003 + lift * (1 - (1 - t[k]) ** 2)
            p = q2 + n2 * height
            strand.append(p)
        out.append(np.array(strand))
    return out


MASK_RINGS = 2  # the style's root faces grown this many rings over the mesh (the gaps between its roots closed)


def _head_faces(character: bpy.types.Object):
    """The faces above the neck joint (MakeHuman's `joint-neck` cube) on the base shape - the same faces on every
    character - with every face's UV polygon (hm08's, in mask texels) and its vertices."""
    from . import groom

    me = character.data
    co = np.empty(len(me.vertices) * 3, np.float32)
    me.vertices.foreach_get("co", co)  # the base shape
    co = co.reshape(-1, 3)
    neck = character.vertex_groups["joint-neck"].index
    cube = [v.index for v in me.vertices if any(g.group == neck and g.weight > 0.5 for g in v.groups)]
    neck_z = float(co[cube, 2].mean())
    uv = me.uv_layers[groom.SURFACE_UV].data
    loop_uv = np.empty(len(uv) * 2, np.float32)
    uv.foreach_get("uv", loop_uv)
    loop_uv = loop_uv.reshape(-1, 2) * MASK_SIZE
    faces = {}
    for poly in me.polygons:
        verts = list(poly.vertices)
        if co[verts, 2].mean() > neck_z:
            faces[poly.index] = (loop_uv[poly.loop_start:poly.loop_start + poly.loop_total], verts)
    return faces


def _scalp_faces(character: bpy.types.Object) -> dict[int, float]:
    """The style's scalp as faces, each with its mask value: the head's faces (`_head_faces`) holding a root of the
    style's region, grown MASK_RINGS rings across the mesh - 1 inside, 0.5 on the outermost ring (a soft hairline). In
    faces, not in UV space: a mask closed and blurred over the UVs fell to nothing along the head island's own seams and
    left a bare line above the ear, the crown to the nape (2026-11-07); and 2% of the strands rooted on the body,
    whose islands border the head's (2,030 of 102,137, from the upper back to 0.42 m above the floor)."""
    head = _head_faces(character)
    ids = np.full((MASK_SIZE, MASK_SIZE), -1, np.int32)
    for index, (pts, _) in head.items():
        _fill_polygon(ids, pts, index)
    uvs = brows.region_uvs(REGION_STYLE)
    ij = np.clip((uvs * MASK_SIZE).astype(int), 0, MASK_SIZE - 1)
    found = ids[ij[:, 1], ij[:, 0]]
    chosen = {int(f): 1.0 for f in np.unique(found[found >= 0])}
    by_vertex: dict[int, list[int]] = {}
    for index, (_, verts) in head.items():
        for v in verts:
            by_vertex.setdefault(v, []).append(index)
    for ring in range(MASK_RINGS):
        grown = {f for index in chosen for v in head[index][1] for f in by_vertex[v]} - set(chosen)
        value = 0.5 if ring == MASK_RINGS - 1 else 1.0
        chosen.update({f: value for f in grown})
    return chosen


def _fill_polygon(grid: np.ndarray, pts: np.ndarray, value: float = 1.0) -> None:
    """A UV polygon (texel units, x = u, y = v) filled into `grid` with `value` as a fan of triangles: every texel
    whose centre lies inside, and the texels of its corners and centre (a face smaller than a texel still marks one) -
    numpy only, Blender's Python has no imaging library."""
    size = grid.shape[0]
    for p in np.vstack([pts, pts.mean(0)]):
        grid[min(int(p[1]), size - 1), min(int(p[0]), size - 1)] = value
    for k in range(1, len(pts) - 1):
        a, b, c = pts[0], pts[k], pts[k + 1]
        x0, x1 = max(int(np.floor(min(a[0], b[0], c[0]))), 0), min(int(np.ceil(max(a[0], b[0], c[0]))), size - 1)
        y0, y1 = max(int(np.floor(min(a[1], b[1], c[1]))), 0), min(int(np.ceil(max(a[1], b[1], c[1]))), size - 1)
        if x1 < x0 or y1 < y0:
            continue
        yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1] + 0.5

        def side(p, q):
            return (q[0] - p[0]) * (yy - p[1]) - (q[1] - p[1]) * (xx - p[0])

        s1, s2, s3 = side(a, b), side(b, c), side(c, a)
        inside = ((s1 >= 0) & (s2 >= 0) & (s3 >= 0)) | ((s1 <= 0) & (s2 <= 0) & (s3 <= 0))
        grid[y0:y1 + 1, x0:x1 + 1][inside] = value


def scalp_mask(character: bpy.types.Object | None = None) -> bpy.types.Image:
    """The scalp in hm08's UVs as an image - the style's region chosen in faces (`_scalp_faces`) and filled into its
    UV polygons: the interpolation's mask texture, sampled by the strands' surface UVs. Made once, from the first
    character it is asked for (the faces are the topology's: the same on every character)."""
    name = "JustStage scalp mask"
    image = bpy.data.images.get(name)
    if image is not None:
        return image
    if character is None:
        raise ValueError("the scalp mask is made from a character the first time")
    head = _head_faces(character)
    grid = np.zeros((MASK_SIZE, MASK_SIZE), np.float32)
    for index, value in sorted(_scalp_faces(character).items(), key=lambda kv: kv[1]):  # 1 painted over 0.5
        _fill_polygon(grid, head[index][0], value)
    image = bpy.data.images.new(name, MASK_SIZE, MASK_SIZE, alpha=False, float_buffer=True)
    image.colorspace_settings.name = "Non-Color"
    image.pixels.foreach_set(np.dstack([grid, grid, grid, np.ones_like(grid)]).ravel())
    image.pack()
    return image


def _hair_group(name: str) -> bpy.types.NodeTree:
    """One of Blender's own hair node groups (`datafiles/assets/nodes/procedural_hair_node_assets.blend`)."""
    import glob
    import os

    group = bpy.data.node_groups.get(name)
    if group is not None:
        return group
    root = os.path.dirname(bpy.app.binary_path)
    path = glob.glob(os.path.join(root, "*", "datafiles", "assets", "nodes", "procedural_hair_node_assets.blend"))[0]
    with bpy.data.libraries.load(path, link=False) as (_src, dst):
        dst.node_groups = [name]
    return dst.node_groups[0]


def _fill_group(seed: int, character: bpy.types.Object) -> bpy.types.NodeTree:
    """Blender's Interpolate Hair Curves with its inputs held in a group of ours - the scalp mask image among them."""
    return _chain("JustStage scalp fill", [("Interpolate Hair Curves", {
        "Density": DENSITY, "Interpolation Guides": INTERPOLATION_GUIDES, "Mask Texture": scalp_mask(character),
        "Seed": seed})])


def _chain(name: str, steps: list) -> bpy.types.NodeTree:
    """A group of ours running Blender's hair groups in order, each with its inputs set on its node (`steps`: (group
    name, {input: value})) - a modifier can't take every socket type through its properties."""
    group = bpy.data.node_groups.get(name)
    if group is not None:
        return group
    group = bpy.data.node_groups.new(name, "GeometryNodeTree")
    group.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    group.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    inp, out = group.nodes.new("NodeGroupInput"), group.nodes.new("NodeGroupOutput")
    socket = inp.outputs[0]
    for k, (hair_group, values) in enumerate(steps):
        node = group.nodes.new("GeometryNodeGroup")
        node.node_tree = _hair_group(hair_group)
        node.location = (200 * (k + 1), 0)
        for key, value in values.items():
            node.inputs[key].default_value = value
        group.links.new(socket, node.inputs["Geometry"])
        socket = node.outputs[0]
    group.links.new(socket, out.inputs[0])
    return group


def _shape_group(spec: dict, seed: int) -> bpy.types.NodeTree:
    """The strands' shape after the fill: Blender's Clump, Frizz and Noise groups, then Set Hair Curve Profile."""
    return _chain("JustStage scalp shape", [
        ("Clump Hair Curves", {"Factor": spec["clump"], "Shape": 0.5}),
        ("Frizz Hair Curves", {"Distance": spec["frizz"], "Seed": seed}),
        ("Hair Curves Noise", {"Distance": spec["noise"], "Scale": 40.0, "Seed": seed}),
        ("Set Hair Curve Profile", {"Radius": RADIUS, "Shape": PROFILE_SHAPE}),
    ])


def _colour_group() -> bpy.types.NodeTree:
    """Each strand's own melanin (a spread round the groom's, a grey share nearly without pigment) and redness, as
    curve attributes the hair material reads - the interpolated strands get theirs here."""
    name = "JustStage strand colour"
    group = bpy.data.node_groups.get(name)
    if group is not None:
        return group
    group = bpy.data.node_groups.new(name, "GeometryNodeTree")
    io = group.interface
    io.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    for label, default in (("Melanin", MELANIN), ("Spread", MELANIN_SPREAD), ("Grey Share", GREY_SHARE),
                           ("Grey Melanin", GREY_MELANIN), ("Redness", REDNESS)):
        io.new_socket(label, in_out="INPUT", socket_type="NodeSocketFloat").default_value = default
    io.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n, links = group.nodes, group.links
    inp, out = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    # the groom's own colour where its curves carry one (juststage.hair.set_colour writes `melanin` and `redness`; the
    # interpolated strands take their guides'), else the group's inputs
    base, redness = (n.new("GeometryNodeInputNamedAttribute") for _ in range(2))
    for node, attr in ((base, "melanin"), (redness, "redness")):
        node.data_type = "FLOAT"
        node.inputs["Name"].default_value = attr
    own = n.new("GeometryNodeSwitch")
    own.input_type = "FLOAT"
    links.new(base.outputs["Exists"], own.inputs["Switch"])
    links.new(inp.outputs["Melanin"], own.inputs["False"])
    links.new(base.outputs["Attribute"], own.inputs["True"])
    own_red = n.new("GeometryNodeSwitch")
    own_red.input_type = "FLOAT"
    links.new(redness.outputs["Exists"], own_red.inputs["Switch"])
    links.new(inp.outputs["Redness"], own_red.inputs["False"])
    links.new(redness.outputs["Attribute"], own_red.inputs["True"])
    spread = n.new("FunctionNodeRandomValue")
    spread.data_type = "FLOAT"
    spread.inputs["Seed"].default_value = 3
    low = n.new("ShaderNodeMath")
    low.operation = "SUBTRACT"
    links.new(own.outputs[0], low.inputs[0])
    links.new(inp.outputs["Spread"], low.inputs[1])
    high = n.new("ShaderNodeMath")
    links.new(own.outputs[0], high.inputs[0])
    links.new(inp.outputs["Spread"], high.inputs[1])
    links.new(low.outputs[0], spread.inputs["Min"])  # 5.3 shows the active type's sockets only
    links.new(high.outputs[0], spread.inputs["Max"])
    grey = n.new("FunctionNodeRandomValue")
    grey.data_type = "BOOLEAN"
    grey.inputs["Seed"].default_value = 9
    links.new(inp.outputs["Grey Share"], grey.inputs["Probability"])
    pick = n.new("GeometryNodeSwitch")
    pick.input_type = "FLOAT"
    links.new(grey.outputs["Value"], pick.inputs["Switch"])
    links.new(spread.outputs["Value"], pick.inputs["False"])
    links.new(inp.outputs["Grey Melanin"], pick.inputs["True"])
    store = n.new("GeometryNodeStoreNamedAttribute")
    store.data_type, store.domain = "FLOAT", "CURVE"
    store.inputs["Name"].default_value = "melanin"
    links.new(inp.outputs["Geometry"], store.inputs["Geometry"])
    links.new(pick.outputs[0], store.inputs["Value"])
    red = n.new("GeometryNodeStoreNamedAttribute")
    red.data_type, red.domain = "FLOAT", "CURVE"
    red.inputs["Name"].default_value = "redness"
    links.new(store.outputs["Geometry"], red.inputs["Geometry"])
    links.new(own_red.outputs[0], red.inputs["Value"])
    links.new(red.outputs["Geometry"], out.inputs["Geometry"])
    return group


def make(character: bpy.types.Object, style: str = "short combed", seed: int = 5) -> bpy.types.Object:
    """The style's groom on the character, replacing its scalp hair (part "scalp")."""
    from . import groom

    spec = STYLES[style]
    groom._check_surface(character)
    found = guides(character, spec, seed)
    rest, uvs = lashes.to_rest(character, found)
    curves = bpy.data.hair_curves.new(NAME)
    curves.add_curves([POINTS] * len(rest))
    curves.position_data.foreach_set("vector", rest.astype(np.float32).ravel())
    curves.attributes.new("surface_uv_coordinate", "FLOAT2", "CURVE").data.foreach_set(
        "vector", uvs.astype(np.float32).ravel())
    curves.surface_uv_map = groom.SURFACE_UV
    for attr, value in (("melanin", MELANIN), ("redness", REDNESS)):  # the groom's colour (hair.set_colour's)
        curves.attributes.new(attr, "FLOAT", "CURVE").data.foreach_set("value", np.full(len(rest), value, np.float32))
    obj = bpy.data.objects.new(NAME, curves)
    obj.modifiers.new("Surface Deform", "NODES").node_group = lashes._deform_group()
    groom.remove_part(character, "scalp")
    groom._attach(character, [obj], "scalp")
    to_local = np.array(character.matrix_world.inverted())
    wanted = np.array(found) @ to_local[:3, :3].T + to_local[:3, 3]
    miss = lashes.place(obj, rest[:, 0], wanted)
    # the fill and the shaping work in rest space (Interpolate Hair Curves on the resting surface; a body's rest shape
    # is MakeHuman's basis, ~0.8 m below its floor key - first in the stack, they put the strands there), then Deform
    # Curves on Surface carries every strand onto the body: it goes last
    obj.modifiers.new("Interpolate Hair Curves", "NODES").node_group = _fill_group(seed, character)
    obj.modifiers.new("Shape", "NODES").node_group = _shape_group(spec, seed)
    obj.modifiers.new("Strand colour", "NODES").node_group = _colour_group()
    obj.modifiers.move(0, len(obj.modifiers) - 1)
    curves.materials.append(groom.hair_material(f"JustStage Hair ({obj.name})"))
    print(f"scalp: {len(rest)} guides, {POINTS} points each, within {miss * 1000:.4f} mm; "
          f"{groom.evaluated_curve_count(obj)} strands")
    return obj
