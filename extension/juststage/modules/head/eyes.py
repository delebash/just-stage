# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""An eye's opening between its lids, found by what shows (moved from the face test's `face_shape.py`, which re-exports
it): rays out from just under the eyeball's surface; the eyeball shows where no skin crosses close outside it. The
lashes (modules/hair/lashes.py) root along it; the face test's occlusion shell and tearline follow it too."""

from __future__ import annotations

import collections

import json

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
    """The body's own polygons (not its helpers'): hm08's body and base v2's appended lid anatomy."""
    from ...core.makehuman import skin_mask

    skin = skin_mask(len(body.data.vertices))
    return [list(p.vertices) for p in body.data.polygons if skin[list(p.vertices)].all()]


def openings(body: bpy.types.Object) -> dict[str, Opening]:
    """Both eyes' openings on the character's current shape (its eye parts `eyeLeft`, `eyeRight`), by eye object."""
    from ..body import build
    from . import parts

    skin = build.shaped_coords(body).astype(np.float64)  # every vertex: the skin's polygons index it
    polys = skin_polygons(body)
    found = {}
    for part in ("eyeLeft", "eyeRight"):
        eye = parts.parts_of(body).get(part)
        if eye is None:
            from ...core.commands import CommandError

            raise CommandError(f"{body.name} has no {part}; run juststage.head.add_parts first")
        found[eye.name] = eye_opening(world_points(eye), skin, polys, gaze(eye), 0.003, 0.008)
    return found


#: MPFB2's procedural eye ("EnhancedEye", CC0 data at its pinned commit - tools/fetch_data.py), the face test's way
EYE_TREE = ("node_trees", "procedural_eyes.json")
#: a brown eye: the face test's round 70 matched a painted dark-brown iris at (0.047, 0.023, 0.016) linear overall -
#: the fibres' lighter and darker halves around it (MakeHuman's own "brown" texture reads red-orange: 0.08, 0.007, 0)
IRIS_MAJOR, IRIS_MINOR = (0.06, 0.03, 0.02), (0.03, 0.014, 0.010)
IRIS_SIZE = 0.371  # the iris' radius over the eyeball's on the eye's UVs (round 70's match: 0.371)
PUPIL_SHARE = 0.22  # MPFB2's black pupil disc, of the iris' radius (the face test's)
#: the white: the face test's sclera brightness (~0.55 luminance, its eye calibration) - its starting (0.68, 0.60, 0.54)
#: read paper-white under the stage's portrait light in both engines (live view and film, 2026-11-04)
WHITE = (0.61, 0.535, 0.475)
#: the face test's settings for MPFB2's eye (rounds 33-38): a glossy iris and its clear coat mirrored the studio, its
#: bump glittered under the catch light, its outer layer mirrored the studio from the side
SETTINGS = {"InnerLayerRoughness": 0.35, "IrisBumpStrength": 0.1, "OuterLayerIOR": 1.15, "Clearcoat": 0.0}
UV_EYE_RADIUS = 0.46  # GNM's eyeball on its UV map, centred at (0.5, 0.5) (measured 2026-10-30)
#: eye colours (CC5's eye colour, MetaHuman's iris presets): (iris, its darker accent), linear. Brown is the measured
#: one above; the rest are set by eye, kept low in chroma - no measured iris colours were found (RESEARCH §1, the
#: searches of 2026-11-04), and a saturated iris is what reads fake (MPFB2's own default blue is 0.18 / 0.49 / 0.91)
PRESETS = {
    "brown": (IRIS_MAJOR, IRIS_MINOR),
    "dark_brown": ((0.035, 0.018, 0.012), (0.018, 0.009, 0.006)),
    "amber": ((0.10, 0.055, 0.02), (0.05, 0.025, 0.010)),
    "hazel": ((0.07, 0.055, 0.025), (0.035, 0.022, 0.012)),
    "green": ((0.055, 0.075, 0.04), (0.025, 0.035, 0.02)),
    "grey": ((0.09, 0.10, 0.10), (0.045, 0.05, 0.055)),
    "blue": ((0.07, 0.11, 0.16), (0.03, 0.05, 0.08)),
    "light_blue": ((0.12, 0.18, 0.24), (0.06, 0.09, 0.13)),
}


def set_colour(eye, iris, accent, white) -> int:
    """An eye's iris, its accent (the fibres' darker half and, a little darker, the limbal ring) and its white, on
    each of its EnhancedEye nodes (the iris, pupil and white materials); returns how many it set."""
    done = 0
    for slot in eye.material_slots:
        mat = slot.material
        if mat is None or mat.node_tree is None:
            continue
        nodes = mat.node_tree.nodes
        if NODE + "iris" in nodes:  # the photo iris: its tint and its white (the structure carries the accent's role)
            nodes[NODE + "iris"].outputs[0].default_value = (*iris, 1.0)
            nodes[NODE + "white"].outputs[0].default_value = (*white, 1.0)
            done += 1
            continue
        for node in mat.node_tree.nodes:
            if node.type != "GROUP" or "IrisMajorColor" not in node.inputs:
                continue
            node.inputs["IrisMajorColor"].default_value = (*iris, 1.0)
            node.inputs["IrisMinorColor"].default_value = (*accent, 1.0)
            node.inputs["IrisSection4Color"].default_value = (*(0.9 * c for c in accent), 1.0)  # a soft limbal ring
            node.inputs["EyeWhiteColor"].default_value = (*white, 1.0)
            done += 1
    return done


def _iris_loops(eye, ids=None):
    names = [sl.material.name if sl.material else "" for sl in eye.material_slots]
    ids = ids or {i for i, n in enumerate(names) if "Iris" in n or "Pupil" in n}
    return [(li, vi) for p in eye.data.polygons if p.material_index in ids
            for li, vi in zip(p.loop_indices, p.vertices, strict=True)]  # fmt: skip


def linear_iris_uvs(eye, ids=None):
    """The iris' and pupil's UVs laid out by their 3D radius, each loop's angle kept, out to the limbus where the
    sclera's begin: GNM's eye squeezes its 2.7 mm pupil disc into UV radius 0-0.05 and its iris (2.55-5.5 mm) into
    0.05-0.185 (measured 2026-11-01), so MPFB2's rings landed warped - a dilated, ringed eye (the face test's round
    61). In the eye's own space (a rigid matrix changes no radius). `ids`: the iris' and pupil's material indices,
    when their slots no longer say so. Returns the UV and 3D radii at the limbus."""
    co = np.array([v.co for v in eye.data.vertices])
    centre = (co.min(axis=0) + co.max(axis=0)) / 2
    loops = _iris_loops(eye, ids)
    verts = sorted({vi for _li, vi in loops})
    axis = co[verts].mean(axis=0) - centre
    axis /= np.linalg.norm(axis)
    rel = co - centre
    radial = np.linalg.norm(rel - np.outer(rel @ axis, axis), axis=1)
    uv = eye.data.uv_layers[0].data
    rho_max = max(float(np.hypot(*(np.array(uv[li].uv) - 0.5))) for li, _vi in loops)
    r_max = float(radial[verts].max())
    for li, vi in loops:
        u, v = uv[li].uv
        angle = np.arctan2(v - 0.5, u - 0.5)
        rho = rho_max * radial[vi] / r_max
        uv[li].uv = (0.5 + rho * np.cos(angle), 0.5 + rho * np.sin(angle))
    return rho_max, r_max


#: the photo iris (tools/make_iris.py: a photographed iris's lightness structure, tinted by the character's iris colour)
#: and its settings, measured equal to HD Aaron's eye at the gate's eye view on one character and holding on five
#: (2026-11-05, RESUME (4b)/(4c)): the pupil 0.45 of the iris's radius (his 0.49), the limbus's soft edge LIMBUS of the
#: radius, the white x WHITE_GAIN (warmer: red x 1.05), no specular of its own (the cornea's shell carries the gloss -
#: at 0.5 a grey haze sat on the pupil)
IRIS_TOOL = ".dev/venv-rdf/Scripts/python -I tools/make_iris.py"
PUPIL, LIMBUS, IRIS_PAST = 0.45, 0.06, 1.04
WHITE_GAIN = (0.71 * 1.05, 0.71, 0.71)
EYE_ROUGHNESS = 0.4
NODE = "js_eye."


def _iris_image():
    from ... import paths

    image = bpy.data.images.load(str(paths.generated("eyes", "iris.png", tool=IRIS_TOOL)), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image


#: the sclera's veins (rec 12, tools/make_sclera.py): a polar map of colour multipliers on the white - columns the
#: angle, rows R0 to R1 limbus radii from the eye's centre
SCLERA_TOOL = ".dev/venv-rdf/Scripts/python -I tools/make_sclera.py"


def _sclera_image():
    from ... import paths

    path = paths.generated("eyes", "sclera.png", tool=SCLERA_TOOL)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "Non-Color"
    return image, json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))


def _photo_tree(mat, uv_name: str, limbus_uv: float) -> None:
    """One eye material as the photo iris, the pupil and the white by the radius on the eye's UVs (the same tree on
    the iris, pupil and white materials - each keeps its name: the gaze and the face test find the iris by them)."""
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")

    def math(op, a, b=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                nt.links.new(x, n.inputs[i])
        return n.outputs[0]

    def ramp(x, lo, hi, clamp=True):
        n = nt.nodes.new("ShaderNodeMapRange")
        n.interpolation_type, n.clamp = "SMOOTHSTEP", clamp
        nt.links.new(x, n.inputs["Value"])
        n.inputs["From Min"].default_value, n.inputs["From Max"].default_value = lo, hi
        return n.outputs["Result"]

    def mix(f, a, b):
        n = nt.nodes.new("ShaderNodeMix")
        n.data_type = "RGBA"
        nt.links.new(f, n.inputs["Factor"])
        for ident, v in (("A_Color", a), ("B_Color", b)):
            sock = next(i for i in n.inputs if i.identifier == ident)
            if isinstance(v, tuple):
                sock.default_value = (*v, 1.0)
            else:
                nt.links.new(v, sock)
        return next(o for o in n.outputs if o.identifier == "Result_Color")

    def rgb(name, value):
        n = nt.nodes.new("ShaderNodeRGB")
        n.name = NODE + name
        n.outputs[0].default_value = (*value, 1.0)
        return n.outputs[0]

    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = uv_name
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs[0])
    du, dv = math("SUBTRACT", sep.outputs["X"], 0.5), math("SUBTRACT", sep.outputs["Y"], 0.5)
    d = math("SQRT", math("ADD", math("MULTIPLY", du, du), math("MULTIPLY", dv, dv)))
    angle = math("ADD", math("DIVIDE", math("ARCTAN2", dv, du), 2 * np.pi), 0.5)
    pupil = limbus_uv * PUPIL
    t = nt.nodes.new("ShaderNodeMapRange")
    t.clamp = True
    nt.links.new(d, t.inputs["Value"])
    t.inputs["From Min"].default_value, t.inputs["From Max"].default_value = pupil * 1.02, limbus_uv * IRIS_PAST
    coords = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(angle, coords.inputs["X"])
    nt.links.new(math("SUBTRACT", 1.0, t.outputs["Result"]), coords.inputs["Y"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.name = NODE + "iris_structure"
    tex.image, tex.extension, tex.interpolation = _iris_image(), "EXTEND", "Cubic"
    nt.links.new(coords.outputs[0], tex.inputs["Vector"])
    tint = nt.nodes.new("ShaderNodeVectorMath")
    tint.operation = "MULTIPLY"
    nt.links.new(tex.outputs["Color"], tint.inputs[0])
    nt.links.new(rgb("iris", IRIS_MAJOR), tint.inputs[1])
    iris = nt.nodes.new("ShaderNodeVectorMath")
    iris.operation, iris.inputs[3].default_value = "SCALE", 2.0  # the structure is stored halved (0.5 = its mean)
    nt.links.new(tint.outputs["Vector"], iris.inputs[0])
    col = mix(ramp(d, pupil * 0.94, pupil * 1.04), (0.0, 0.0, 0.0), iris.outputs["Vector"])
    white = nt.nodes.new("ShaderNodeVectorMath")
    white.operation = "MULTIPLY"
    nt.links.new(rgb("white", WHITE), white.inputs[0])
    white.inputs[1].default_value = WHITE_GAIN
    sclera_image, polar = _sclera_image()
    rows = nt.nodes.new("ShaderNodeMapRange")  # the radius in limbus radii -> the map's rows (R0 at its top)
    rows.clamp = True
    nt.links.new(d, rows.inputs["Value"])
    rows.inputs["From Min"].default_value = limbus_uv * polar["r0"]
    rows.inputs["From Max"].default_value = limbus_uv * polar["r1"]
    rows.inputs["To Min"].default_value, rows.inputs["To Max"].default_value = 1.0, 0.0
    at = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(angle, at.inputs["X"])
    nt.links.new(rows.outputs["Result"], at.inputs["Y"])
    veins = nt.nodes.new("ShaderNodeTexImage")
    veins.name = NODE + "sclera"
    veins.image, veins.extension, veins.interpolation = sclera_image, "EXTEND", "Cubic"
    nt.links.new(at.outputs[0], veins.inputs["Vector"])
    veined = nt.nodes.new("ShaderNodeVectorMath")
    veined.name, veined.operation = NODE + "white_veined", "MULTIPLY"
    nt.links.new(white.outputs["Vector"], veined.inputs[0])
    nt.links.new(veins.outputs["Color"], veined.inputs[1])
    col = mix(ramp(d, limbus_uv * (1 - LIMBUS / 2), limbus_uv * (1 + LIMBUS)), col, veined.outputs["Vector"])
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = EYE_ROUGHNESS
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    nt.links.new(bsdf.outputs[0], out.inputs["Surface"])


def shade(eye) -> None:
    """The photo iris on the eye's iris, pupil and white (_photo_tree), its UVs laid out by the 3D radius first
    (linear_iris_uvs); the cornea keeps its own (modules/head/part_materials.py)."""
    limbus_uv, _r = linear_iris_uvs(eye)
    for slot in eye.material_slots:
        mat = slot.material
        if mat is None or not any(r in mat.name for r in ("Iris", "Pupil", "Sclera")):
            continue
        _photo_tree(mat, eye.data.uv_layers[0].name, limbus_uv)