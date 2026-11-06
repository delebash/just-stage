# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The eye's two thin layers over the eyeball, as CC5 and MetaHuman stack them (RESEARCH §5; the research's
`2026-10-30-research-hair-eyes-teeth.md` §5): the eye occlusion - "the shadow cast from the eyelids", a tinted film over
the eyeball between the lids - and the tearline, the wet strip where the lids meet the eye. Moved from the face test
(`tools/face_test/test_face_project.py`, rec 6 of `docs/plans/2026-10-31-audit-eyes.md` §6), which calls these now.

Both are ICT-FaceKit's own strips (MIT, fetched by tools/fetch_data.py: its neutral mesh's left eye occlusion and
lacrimal fluid, topology and UVs kept), moved onto our eye across our lid opening (eyes.openings). One object per layer
holds both eyes, named as MetaHuman's face names them: `eyeshell` (the occlusion) and `eyeEdge` (the tearline). Each
vertex keeps its angles about its eye and its height off the eyeball, so a body change that moves or resizes the eyes
refits them at once (`refit`), the lids' outline found again.
"""

from __future__ import annotations

import collections
import functools

import bpy
import numpy as np

from ... import paths

ICT_MESH = ("ict", "generic_neutral_mesh.obj")
#: its README's index table (left side): the face's vertices, the left eyeball's vertices, the polygons of the left eye
#: occlusion and of the left lacrimal fluid
ICT_SKIN, ICT_EYE, ICT_OCCLUSION, ICT_TEAR = (0, 9409), (21451, 23021), (25048, 25176), (24692, 24855)
ICT_SKIN_POLYGONS = 9230  # its face's polygons
#: the occlusion's darkening per side, CC5's documented model (Eye Occlusion Shadow 1: a range and strength for the top,
#: bottom, inner and outer, each with an edge fade): (range in UV, strength) - the face test's values (round 49 on)
OCCLUSION = {"top": (0.30, 0.15), "bottom": (0.20, 0.15), "inner": (0.20, 0.30), "outer": (0.15, 0.15)}
OCCLUSION_COLOUR = (0.33, 0.09, 0.05)  # CC5's Shadow 2 example #54170E, a dark red-brown
EEVEE_OCCLUSION_GAIN = 2.5  # the live view's darker film (its lids' shadow is weaker than Cycles')
OCCLUSION_LIFT = 0.0004  # off the eyeball (ICT's sits a median 0.5 mm off)
OCCLUSION_UNDER_LIDS = 3.0  # degrees under each lid
TEAR_ROUGHNESS = 0.3  # CC5's Tear Line examples: 0.25 and 0.45
#: the film fades in over this share of the strip from its edge on the eyeball (CC5's Edge Fadeout); 0.25 left a grey
#: band lying on the eyeball (gate run 9; HD Aaron's a thin wet line at the lid)
TEAR_FADE = 0.6
TEAR_IOR = 1.336  # water
LAYERS = {"eyeshell": "occlusion", "eyeEdge": "tearline"}
#: each vertex's place about its eye (point attributes): which eye, azimuth and elevation (degrees), height off it (m)
ATTRS = ("js_eye", "js_az", "js_el", "js_off")


@functools.cache
def _ict():
    """ICT-FaceKit's neutral mesh: positions in Blender's axes (ICT's are y up, z forward, in centimetres - its eye
    centres are 6.19 apart), UVs, and faces as (vertex, uv) pairs."""
    v, vt, faces = [], [], []
    with open(paths.FETCHED.joinpath(*ICT_MESH), encoding="utf-8") as f:
        for line in f:
            if line.startswith("v "):
                v.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("vt "):
                vt.append([float(x) for x in line.split()[1:3]])
            elif line.startswith("f "):
                faces.append([tuple(int(t) - 1 for t in c.split("/")[:2]) for c in line.split()[1:]])
    v = np.array(v)
    return np.c_[v[:, 0], -v[:, 2], v[:, 1]], np.array(vt), faces


def _ict_part(first, end):
    """One of ICT's pieces by its polygon range: faces in its own vertex numbers, positions, per-vertex UVs."""
    v, vt, faces = _ict()
    part = faces[first:end]
    order = sorted({c[0] for f in part for c in f})
    local = {g: k for k, g in enumerate(order)}
    uv = np.zeros((len(order), 2))
    for f in part:
        for g, t in f:
            uv[local[g]] = vt[t]
    return [[local[c[0]] for c in f] for f in part], v[order], uv


@functools.cache
def _ict_opening():
    """ICT's own left eye opening (its units, cm), which the tearline's angles are read against."""
    from . import eyes

    v, _, faces = _ict()
    polys = [[c[0] for c in f] for f in faces[:ICT_SKIN_POLYGONS]]
    return eyes.eye_opening(v[slice(*ICT_EYE)], v[slice(*ICT_SKIN)], polys, (0.0, 0.0), 0.3, 0.8)


def occlusion_shape(o) -> tuple[list, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """ICT's sheet over our eyeball across our lid opening `o`: u from the outer corner to the inner, v from the lower
    lid's edge to the upper's, `OCCLUSION_UNDER_LIDS` under each lid, `OCCLUSION_LIFT` off the eyeball. Returns faces,
    the vertices' azimuths, elevations and heights off the eyeball, and their UVs."""
    faces, _, uv = _ict_part(*ICT_OCCLUSION)
    widen = 4.0 * np.sign(o.inner - o.outer)
    a_outer, a_inner = o.outer - widen, o.inner + widen
    a = a_outer + uv[:, 0] * (a_inner - a_outer)
    lo_e = np.interp(a, o.centres, o.lower) - OCCLUSION_UNDER_LIDS
    up_e = np.interp(a, o.centres, o.upper) + OCCLUSION_UNDER_LIDS
    e = lo_e + uv[:, 1] * (up_e - lo_e)
    return faces, a, e, np.full(len(a), OCCLUSION_LIFT), uv


def tearline_shape(o, skin: np.ndarray) -> tuple[list, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """ICT's lacrimal-fluid strip, a ring from the eyeball at the lid margins (its edge there a median 0.3 mm off the
    eyeball) to under both lids (its other edge 1.6 mm off), moved onto our eye: each vertex keeps its angle past ICT's
    lid edge on its side, at the same share of the way from the outer corner to the inner, and its height off the
    eyeball scaled to ours - but stays under our lid's skin (`skin`, the body's points) where that is lower. Returns
    faces, azimuths, elevations, heights off the eyeball, and each vertex's share from its rim on the eyeball (0) to
    its rim under the lids (1), which the film fades in by."""
    from . import eyes

    faces, ict_points, _ = _ict_part(*ICT_TEAR)
    i = _ict_opening()
    az, el, dist = eyes.angles(ict_points, i.centre)
    off = (dist - i.radius) * o.radius / i.radius
    a = o.outer + (az - i.outer) / (i.inner - i.outer) * (o.inner - o.outer)
    upper_side = el > (np.interp(az, i.centres, i.upper) + np.interp(az, i.centres, i.lower)) / 2
    i_edge = np.where(upper_side, np.interp(az, i.centres, i.upper), np.interp(az, i.centres, i.lower))
    o_edge = np.where(upper_side, np.interp(a, o.centres, o.upper), np.interp(a, o.centres, o.lower))
    e = o_edge + (el - i_edge)
    t_dir = eyes.direction(a, e)
    # under our lid: no higher than the skin within 3 deg of it, less 0.2 mm
    s_az, s_el, s_dist = eyes.angles(skin, o.centre)
    near_eye = (s_dist < o.radius + 0.005) & (skin[:, 1] < o.centre[1])
    s_dir, s_off = eyes.direction(s_az[near_eye], s_el[near_eye]), s_dist[near_eye] - o.radius
    close = np.degrees(np.arccos(np.clip(t_dir @ s_dir.T, -1.0, 1.0))) < 3.0
    ceiling = np.where(close, s_off[None, :], np.inf).min(axis=1) - 0.0002
    off = np.maximum(np.minimum(off, ceiling), 0.0001)
    # the strip's share from its rim on the eyeball (0) to its rim under the lids (1), in steps along its edges
    count = collections.Counter(tuple(sorted((f[k], f[k - 1]))) for f in faces for k in range(len(f)))
    links, rim = collections.defaultdict(set), collections.defaultdict(set)
    for (p, q), n in count.items():
        for graph in (links, rim) if n == 1 else (links,):
            graph[p].add(q)
            graph[q].add(p)
    loops, seen = [], set()
    for start in rim:
        if start not in seen:
            loop, todo = set(), [start]
            while todo:
                p = todo.pop()
                if p not in loop:
                    loop.add(p)
                    todo.extend(rim[p])
            seen |= loop
            loops.append(loop)
    if len(loops) != 2:
        raise ValueError(f"ICT's tear strip should have two rims, found {len(loops)}")
    on_eye, under_lid = sorted(loops, key=lambda lp: np.median(dist[list(lp)]))

    def steps(sources):
        d, front = dict.fromkeys(sources, 0), list(sources)
        while front:
            nxt = []
            for p in front:
                for q in links[p]:
                    if q not in d:
                        d[q] = d[p] + 1
                        nxt.append(q)
            front = nxt
        return np.array([d[k] for k in range(len(ict_points))], dtype=float)

    near = steps(on_eye)
    return faces, a, e, off, near / (near + steps(under_lid))


def _eye_sphere(eye: bpy.types.Object) -> tuple[np.ndarray, float]:
    """An eye's centre and radius from its current points (eyes.eye_opening's measure)."""
    from . import eyes

    points = eyes.world_points(eye)
    lo, hi = points.min(axis=0), points.max(axis=0)
    return (lo + hi) / 2, float((hi - lo)[[0, 2]].mean() / 2)


def _place(mesh: bpy.types.Mesh, spheres: list) -> None:
    """Each vertex at its angles about its eye and its height off that eyeball."""
    from . import eyes

    n = len(mesh.vertices)
    values = {}
    for name in ATTRS:
        buf = np.zeros(n, dtype=np.float32 if name != "js_eye" else np.int32)
        mesh.attributes[name].data.foreach_get("value", buf)
        values[name] = buf
    points = np.zeros((n, 3))
    for k, (centre, radius) in enumerate(spheres):
        on = values["js_eye"] == k
        points[on] = centre + (radius + values["js_off"][on, None]) * eyes.direction(
            values["js_az"][on], values["js_el"][on]
        )
    mesh.vertices.foreach_set("co", points.astype(np.float32).ravel())
    mesh.update()


def _occlusion_material(name: str) -> bpy.types.Material:
    """CC5's documented occlusion: per-side ranges with a soft edge, a tinted transparent film that only darkens what is
    behind it and casts nothing (the lids' own shadow is traced)."""
    mat = bpy.data.materials.new(name)
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    film = nt.nodes.new("ShaderNodeBsdfTransparent")
    coords = nt.nodes.new("ShaderNodeUVMap")
    coords.uv_map = "UVMap"
    split = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coords.outputs["UV"], split.inputs["Vector"])
    darkness = None
    for side, (span, strength) in OCCLUSION.items():
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.interpolation_type = "SMOOTHSTEP"
        axis = split.outputs["Y" if side in ("top", "bottom") else "X"]
        near_one = side in ("top", "inner")  # u runs outer (0) to inner (1); v lower (0) to upper (1)
        ramp.inputs["From Min"].default_value = 1.0 - span if near_one else span
        ramp.inputs["From Max"].default_value = 1.0 if near_one else 0.0
        ramp.inputs["To Max"].default_value = strength
        nt.links.new(axis, ramp.inputs["Value"])
        if darkness is None:
            darkness = ramp.outputs["Result"]
        else:
            both = nt.nodes.new("ShaderNodeMath")
            both.operation = "MAXIMUM"
            nt.links.new(darkness, both.inputs[0])
            nt.links.new(ramp.outputs["Result"], both.inputs[1])
            darkness = both.outputs["Value"]
    # Cycles traces the lids' own soft shadow on the white, EEVEE's shadow maps draw only a hard sliver of it (the eyes'
    # working doc, 2026-11-04): the live view gets the same ranges, darker, through its own output
    out.target = "CYCLES"
    eevee_out = nt.nodes.new("ShaderNodeOutputMaterial")
    eevee_out.target = "EEVEE"
    gain = nt.nodes.new("ShaderNodeMath")
    gain.operation, gain.use_clamp = "MULTIPLY", True
    gain.inputs[1].default_value = EEVEE_OCCLUSION_GAIN
    nt.links.new(darkness, gain.inputs[0])
    for amount, output in ((darkness, out), (gain.outputs["Value"], eevee_out)):
        tint = nt.nodes.new("ShaderNodeMix")
        tint.data_type = "RGBA"
        nt.links.new(amount, tint.inputs["Factor"])
        next(i for i in tint.inputs if i.identifier == "A_Color").default_value = (1.0, 1.0, 1.0, 1.0)
        next(i for i in tint.inputs if i.identifier == "B_Color").default_value = (*OCCLUSION_COLOUR, 1.0)
        layer = film if output is out else nt.nodes.new("ShaderNodeBsdfTransparent")
        nt.links.new(next(o for o in tint.outputs if o.identifier == "Result_Color"), layer.inputs["Color"])
        nt.links.new(layer.outputs["BSDF"], output.inputs["Surface"])
    mat.surface_render_method = "BLENDED"  # EEVEE: a sorted see-through film, not dithered noise
    return mat


def _tearline_material(name: str) -> bpy.types.Material:
    """A tear film: water's Fresnel reflection over a transparent film, CC5's example roughness, faded in from its edge
    on the eyeball (CC5's Edge Fadeout)."""
    mat = bpy.data.materials.new(name)
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "share"
    fade = nt.nodes.new("ShaderNodeMapRange")
    fade.interpolation_type = "SMOOTHSTEP"
    fade.inputs["From Max"].default_value = TEAR_FADE
    nt.links.new(attr.outputs["Fac"], fade.inputs["Value"])
    fresnel = nt.nodes.new("ShaderNodeFresnel")
    fresnel.inputs["IOR"].default_value = TEAR_IOR
    wet = nt.nodes.new("ShaderNodeMath")
    wet.operation = "MULTIPLY"
    nt.links.new(fresnel.outputs["Fac"], wet.inputs[0])
    nt.links.new(fade.outputs["Result"], wet.inputs[1])
    gloss = nt.nodes.new("ShaderNodeBsdfGlossy")
    gloss.inputs["Roughness"].default_value = TEAR_ROUGHNESS
    nt.links.new(wet.outputs["Value"], gloss.inputs["Color"])  # the reflection's strength: water's Fresnel, faded in
    # the film adds its gloss over the eye seen through it: as a mix by Fresnel it put the dark stage's reflection in
    # the eyeball's place at grazing angles - a dark grey outline round the opening (the clean-input gate, 2026-11-06,
    # gone with the film hidden; HD Aaron's a light wet line)
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(nt.nodes.new("ShaderNodeBsdfTransparent").outputs["BSDF"], add.inputs[0])
    nt.links.new(gloss.outputs["BSDF"], add.inputs[1])
    nt.links.new(add.outputs["Shader"], out.inputs["Surface"])
    mat.surface_render_method = "BLENDED"
    return mat


def layers_of(character: bpy.types.Object) -> dict[str, bpy.types.Object]:
    cid = character.juststage.character_id
    return {o.juststage.part: o for o in bpy.data.objects if o.juststage.part_of == cid and o.juststage.part in LAYERS}


def _eyes(character: bpy.types.Object) -> list[bpy.types.Object]:
    from . import parts

    found = parts.parts_of(character)
    return [found[p] for p in ("eyeLeft", "eyeRight") if p in found]


def _shapes(kind: str, found: list, skin: np.ndarray) -> tuple[list, dict, list]:
    """One layer's strips over both eyes, from their openings `found` (in the eyes' order) and the body's points `skin`:
    faces, the ATTRS columns per eye, and per eye the occlusion's UVs or the tearline's share from its rim."""
    all_faces, cols, extra = [], {name: [] for name in ATTRS}, []
    for k, o in enumerate(found):
        faces, a, e, off, more = occlusion_shape(o) if kind == "occlusion" else tearline_shape(o, skin)
        base = sum(len(c) for c in cols["js_az"])
        all_faces += [[base + i for i in f] for f in faces]
        cols["js_eye"].append(np.full(len(a), k))
        cols["js_az"].append(a)
        cols["js_el"].append(e)
        cols["js_off"].append(off)
        extra.append(more)
    return all_faces, cols, extra


def add(character: bpy.types.Object, openings: dict | None = None) -> dict[str, bpy.types.Object]:
    """Both layers on the character's eyes, replacing any it has; their shape from its lids as they are now."""
    from ...core.makehuman import skin_indices
    from ..body import build
    from . import eyes

    eye_objs = _eyes(character)
    if len(eye_objs) != 2:
        from ...core.commands import CommandError

        raise CommandError(f"{character.name} has no eyes; run juststage.head.add_parts first")
    found = openings or eyes.openings(character)
    co = build.shaped_coords(character)
    skin = co[skin_indices(len(co))].astype(np.float64)
    for old in layers_of(character).values():
        bpy.data.objects.remove(old)
    made = {}
    for part, kind in LAYERS.items():
        all_faces, cols, extra = _shapes(kind, [found[eye.name] for eye in eye_objs], skin)
        n = sum(len(c) for c in cols["js_az"])
        mesh = bpy.data.meshes.new(part)
        mesh.from_pydata(np.zeros((n, 3)).tolist(), [], all_faces)
        for name in ATTRS:
            kind_ = "INT" if name == "js_eye" else "FLOAT"
            mesh.attributes.new(name, kind_, "POINT").data.foreach_set("value", np.concatenate(cols[name]))
        _place(mesh, [_eye_sphere(eye) for eye in eye_objs])
        if kind == "occlusion":
            uv = np.concatenate(extra)
            layer = mesh.uv_layers.new(name="UVMap")
            layer.data.foreach_set("uv", uv[[lp.vertex_index for lp in mesh.loops]].ravel())
        else:
            mesh.attributes.new("share", "FLOAT", "POINT").data.foreach_set("value", np.concatenate(extra))
            centres = np.array([_eye_sphere(eye)[0] for eye in eye_objs])
            eye_of = np.concatenate(cols["js_eye"])
            outward = [
                (np.array(p.center) - centres[eye_of[p.vertices[0]]]) @ np.array(p.normal) for p in mesh.polygons
            ]
            if np.median(outward) < 0:  # ICT's strip faces the eyeball once moved: turned to face away again
                mesh.flip_normals()
        mesh.shade_smooth()
        obj = bpy.data.objects.new(f"{character.name}.{part}", mesh)
        for collection in character.users_collection:
            collection.objects.link(obj)
        obj.parent = character
        obj.visible_shadow = obj.visible_diffuse = obj.visible_volume_scatter = False
        obj.juststage.part = part
        obj.juststage.part_of = character.juststage.character_id
        material = _occlusion_material if kind == "occlusion" else _tearline_material
        mesh.materials.append(material(f"JustStage {kind.title()} ({obj.name})"))
        made[part] = obj
    return made


def refit(character: bpy.types.Object) -> None:
    """The layers onto the eyes where they are now and across the lids' opening as it is now (a body change moved or
    resized the eyes, or opened or narrowed the lids - the dressed human's EYE_OPEN): the same strips, their angles
    found again."""
    from ...core.makehuman import skin_indices
    from ..body import build
    from . import eyes

    layers = layers_of(character)
    eye_objs = _eyes(character)
    if not layers or len(eye_objs) != 2:
        return
    found = eyes.openings(character)
    co = build.shaped_coords(character)
    skin = co[skin_indices(len(co))].astype(np.float64)
    spheres = [_eye_sphere(eye) for eye in eye_objs]
    for part, obj in layers.items():
        _, cols, extra = _shapes(LAYERS[part], [found[eye.name] for eye in eye_objs], skin)
        for name in ("js_az", "js_el", "js_off"):
            obj.data.attributes[name].data.foreach_set("value", np.concatenate(cols[name]).astype(np.float32))
        if LAYERS[part] == "tearline":
            obj.data.attributes["share"].data.foreach_set("value", np.concatenate(extra).astype(np.float32))
        _place(obj.data, spheres)
