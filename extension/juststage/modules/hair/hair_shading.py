# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The live view's hair model (the realism review's rec 1, approved 2026-11-04; "half built: the lobes not written"
until 2026-11-06): EEVEE has no hair shader ("Principled Hair BSDF - Not supported", manual render/eevee/limitations)
and our stand-in was a plain Principled surface - hair with no highlight bands, read flat beside HD Aaron's cards.

Karis' real-time form of Marschner's model (SIGGRAPH 2016 course "Physically Based Hair Shading in Unreal", the model
Unreal's real-time hair is built on): three lobes - R (the white highlight, shifted toward the root), TT (through the
hair, from behind), TRT (the coloured secondary, shifted toward the tip) - each a longitudinal Gaussian M_p(theta_h)
(shift ALPHA_p, width BETA_p from the roughness) times Karis' azimuthal terms N_p(phi) with absorption from the hair's
colour; per scene light through EEVEE 5.3's Light Accumulation node (its units measured 2026-11-06: Light Evaluation's
Factor x Light Info's Color x Power = a diffuse surface's light within 2% - RESEARCH, EEVEE per-light nodes); the
multiple-scattered body as Kajiya-Kay's diffuse in the hair's colour; the image light (which Light Accumulation leaves
out) as a constant ambient of the world's mean, darkened toward the roots (the strands under the others).

NOT STANDARD (in the review: "replaced by Blender's closure if it lands"): Blender's own EEVEE hair closure (PR #164595,
one Kajiya-Kay lobe) "not expected to land in its current state"."""

from __future__ import annotations

import math

import bpy

ETA = 1.55  # hair's refractive index
F0 = ((ETA - 1) / (ETA + 1)) ** 2
SHIFT = 0.035  # rad: Karis' cuticle tilt; R at -2 x, TT at +1 x, TRT at +4 x
ROUGHNESS = 0.3  # the longitudinal roughness (Cycles' Principled Hair default)
#: calibrated against Cycles' Principled Hair on the gate's front view (the scalp's window, 2026-11-06, 6e43562): with
#: the lobes' width as Cycles maps its roughness and the body's shadow softened, body 0.4 / lobes 1.0 put the scalp's
#: mean at 0.112 against Cycles' 0.121 (within the gate's 10%)
DIFFUSE = 0.4  # the multiple-scattered body's share
GLOSSY = 1.0  # the lobes' share
BODY_LIGHT_THROUGH = 0.5  # the share of the light the body gets in the strands' own shadow
#: the image light's ambient, x the world's mean radiance (WORLD_MEAN, set from the stage's world): x0.45 puts the back of
#: the hair under the image light alone at 1.02x Cycles (was 2.2x at 1.0 - the gate, 2026-11-07); the stage light's
#: front-to-back mismatch (0.77x / 2.05x) is the model's angular error, not this term
AMBIENT = 0.45
ROOT_AO = 0.35  # the ambient at the root (the strands above shade it), rising to 1 at the tip
NODE = "js_hair."


def _math(nt, op, a, b=None, c=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    for i, x in enumerate((a, b, c)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            n.inputs[i].default_value = x
        else:
            nt.links.new(x, n.inputs[i])
    return n.outputs[0]


def _vec(nt, op, a, b=None, scale=None):
    n = nt.nodes.new("ShaderNodeVectorMath")
    n.operation = op
    for i, x in enumerate((a, b)):
        if x is None:
            continue
        if isinstance(x, tuple):
            n.inputs[i].default_value = x
        else:
            nt.links.new(x, n.inputs[i])
    if scale is not None:
        if isinstance(scale, (int, float)):
            n.inputs["Scale"].default_value = scale
        else:
            nt.links.new(scale, n.inputs["Scale"])
    return n.outputs["Value"] if op in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else n.outputs["Vector"]


def _gauss(nt, x, mean, width):
    d = _math(nt, "SUBTRACT", x, mean)
    return _math(nt, "MULTIPLY", _math(nt, "EXPONENT", _math(nt, "DIVIDE", _math(nt, "MULTIPLY", d, d), -2 * width * width)),
                 1.0 / (math.sqrt(2 * math.pi) * width))  # fmt: skip


def _fresnel(nt, cos):
    """Schlick's Fresnel at hair's F0."""
    one_minus = _math(nt, "SUBTRACT", 1.0, _math(nt, "MAXIMUM", cos, 0.0))
    p5 = _math(nt, "POWER", one_minus, 5.0)
    return _math(nt, "MULTIPLY_ADD", p5, 1 - F0, F0)


def _pow_colour(nt, colour, exponent):
    """colour ** exponent per channel (absorption)."""
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(colour, sep.inputs["Color"])
    comb = nt.nodes.new("ShaderNodeCombineColor")
    for ch in ("Red", "Green", "Blue"):
        nt.links.new(_math(nt, "POWER", _math(nt, "MAXIMUM", sep.outputs[ch], 1e-4), exponent), comb.inputs[ch])
    return comb.outputs["Color"]


def build(nt, colour, roughness: float = ROUGHNESS, world_mean: float = 0.0, sheen: float = 1.0):
    """The hair model's closure in `nt` for strands of `colour` (a socket: the strand's own colour - groom.py's fitted
    stand-in), its lobes' light x `sheen` (a groom's own - the brows', `brows.SHEEN`); returns its Shader output."""
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    T, V, P = geo.outputs["Tangent"], geo.outputs["Incoming"], geo.outputs["Position"]
    ev0 = nt.nodes.new("ShaderNodeLightEvaluation")
    nt.links.new(P, ev0.inputs["Position"])
    nt.links.new(geo.outputs["Normal"], ev0.inputs["Normal"])
    L = ev0.outputs["Direction"]
    ev1 = nt.nodes.new("ShaderNodeLightEvaluation")  # the light's own strength, no cosine: its normal toward it
    nt.links.new(P, ev1.inputs["Position"])
    nt.links.new(L, ev1.inputs["Normal"])
    info = nt.nodes.new("ShaderNodeLightInfo")
    # the light at the strand: its strength x its colour and power x its shadow (Light Evaluation's Mask - without it
    # every strand was lit, brows under the brow ridge and hair under hair alike)
    strength = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", ev1.outputs["Factor"], info.outputs["Power"]), ev1.outputs["Mask"])
    shadow = nt.nodes.new("ShaderNodeShadowRaycast")  # the light's shadow at the strand (the head's, other hair's)
    nt.links.new(P, shadow.inputs["Position"])
    unshadowed = _vec(nt, "SCALE", info.outputs["Color"], scale=strength)
    light = _vec(nt, "MULTIPLY", unshadowed, shadow.outputs["Color"])  # the lobes: the surface's, fully shadowed
    # the body: multiple scattering carries light under the top strands - its shadow softened (hair isn't opaque:
    # the raycast's full shadow put the scalp at half of Cycles')
    soft = _vec(nt, "ADD", _vec(nt, "SCALE", shadow.outputs["Color"], scale=1.0 - BODY_LIGHT_THROUGH), (BODY_LIGHT_THROUGH,) * 3)
    body_light = _vec(nt, "MULTIPLY", unshadowed, soft)
    # clamped: a strand along the light or the view would put a dot product a hair past 1 and asin's NaN on screen
    sin_i = _math(nt, "MAXIMUM", _math(nt, "MINIMUM", _vec(nt, "DOT_PRODUCT", L, T), 0.9999), -0.9999)
    sin_r = _math(nt, "MAXIMUM", _math(nt, "MINIMUM", _vec(nt, "DOT_PRODUCT", V, T), 0.9999), -0.9999)
    th_i, th_r = _math(nt, "ARCSINE", sin_i), _math(nt, "ARCSINE", sin_r)
    th_h = _math(nt, "MULTIPLY", _math(nt, "ADD", th_i, th_r), 0.5)
    cos_d = _math(nt, "MAXIMUM", _math(nt, "COSINE", _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", th_i, th_r), 0.5)), 0.05)
    lp = _vec(nt, "NORMALIZE", _vec(nt, "SUBTRACT", L, _vec(nt, "SCALE", T, scale=sin_i)))
    vp = _vec(nt, "NORMALIZE", _vec(nt, "SUBTRACT", V, _vec(nt, "SCALE", T, scale=sin_r)))
    cos_phi = _vec(nt, "DOT_PRODUCT", lp, vp)
    cos_half = _math(nt, "SQRT", _math(nt, "MAXIMUM", _math(nt, "MULTIPLY_ADD", cos_phi, 0.5, 0.5), 0.0))
    # the lobes' longitudinal width as Cycles' Principled Hair maps its roughness (Chiang et al. 2016:
    # v = (0.726 b + 0.812 b^2 + 3.7 b^20)^2, the deviation its root) - Karis' b^2 (0.09 rad at 0.3) made the R
    # highlight 3x too narrow and too bright (the gate's front view: white hair beside Cycles' brown, 2026-11-06)
    width = 0.726 * roughness + 0.812 * roughness**2 + 3.7 * roughness**20
    m_r = _gauss(nt, th_h, -2 * SHIFT, width)
    m_tt = _gauss(nt, th_h, SHIFT, width / 2)
    m_trt = _gauss(nt, th_h, 4 * SHIFT, 2 * width)
    # R: 1/4 cos(phi/2) F(eta, sqrt(1/2 + 1/2 L.V))
    ldv = _vec(nt, "DOT_PRODUCT", L, V)
    f_r = _fresnel(nt, _math(nt, "SQRT", _math(nt, "MAXIMUM", _math(nt, "MULTIPLY_ADD", ldv, 0.5, 0.5), 0.0)))
    n_r = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", cos_half, 0.25), f_r)
    # TT: h = (1 + a (0.6 - 0.8 cos phi)) cos(phi/2), a = 1/eta; T = C^(sqrt(1 - h^2 a^2) / (2 cos_d)); D = exp(-3.65 cos phi - 3.98)
    a = 1.0 / ETA
    h = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY_ADD", _math(nt, "MULTIPLY_ADD", cos_phi, -0.8, 0.6), a, 1.0), cos_half)
    root = _math(nt, "SQRT", _math(nt, "MAXIMUM", _math(nt, "SUBTRACT", 1.0, _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", h, h), a * a)), 0.0))
    t_tt = _pow_colour(nt, colour, _math(nt, "DIVIDE", root, _math(nt, "MULTIPLY", cos_d, 2.0)))
    f_tt = _fresnel(nt, _math(nt, "MULTIPLY", cos_d, _math(nt, "SQRT", _math(nt, "MAXIMUM", _math(nt, "SUBTRACT", 1.0, _math(nt, "MULTIPLY", h, h)), 0.0))))
    d_tt = _math(nt, "EXPONENT", _math(nt, "MULTIPLY_ADD", cos_phi, -3.65, -3.98))
    w_tt = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", _math(nt, "POWER", _math(nt, "SUBTRACT", 1.0, f_tt), 2.0), d_tt), m_tt)
    # TRT: T = C^(0.8 / cos_d); f = F(eta, cos_d / 2); D = exp(17 cos phi - 16.78); N = (1 - f)^2 f T^2 D
    t_trt = _pow_colour(nt, colour, _math(nt, "DIVIDE", 1.6, cos_d))  # T^2
    f_trt = _fresnel(nt, _math(nt, "MULTIPLY", cos_d, 0.5))
    d_trt = _math(nt, "EXPONENT", _math(nt, "MULTIPLY_ADD", cos_phi, 17.0, -16.78))
    w_trt = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", _math(nt, "POWER", _math(nt, "SUBTRACT", 1.0, f_trt), 2.0), f_trt), d_trt), m_trt)
    spec = _vec(nt, "ADD", _vec(nt, "SCALE", t_tt, scale=w_tt), _vec(nt, "SCALE", t_trt, scale=w_trt))
    r_term = _math(nt, "MULTIPLY", m_r, n_r)
    spec = _vec(nt, "ADD", spec, _vec(nt, "SCALE", (1.0, 1.0, 1.0), scale=r_term))
    fiber_cos = _math(nt, "SQRT", _math(nt, "MAXIMUM", _math(nt, "SUBTRACT", 1.0, _math(nt, "MULTIPLY", sin_i, sin_i)), 0.0))
    lobes = _math(nt, "MULTIPLY", fiber_cos, math.pi * GLOSSY * sheen)  # the lobes' share x the groom's sheen
    glossy = _vec(nt, "MULTIPLY", light, _vec(nt, "SCALE", spec, scale=lobes))
    acc = nt.nodes.new("ShaderNodeLightAccumulation")
    acc.name = NODE + "lights"
    nt.links.new(glossy, acc.inputs["Glossy Light"])
    acc.inputs["Glossy Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    # the body: Kajiya-Kay's diffuse (sin of the angle to the strand) in the hair's colour
    nt.links.new(_vec(nt, "SCALE", body_light, scale=_math(nt, "MULTIPLY", fiber_cos, DIFFUSE)), acc.inputs["Diffuse Light"])
    nt.links.new(colour, acc.inputs["Diffuse Color"])
    # the image light: the world's mean radiance in the hair's colour, darker toward the roots
    info_h = nt.nodes.new("ShaderNodeHairInfo")
    ao = _math(nt, "MULTIPLY_ADD", _math(nt, "POWER", info_h.outputs["Intercept"], 0.5), 1 - ROOT_AO, ROOT_AO)
    world = nt.nodes.new("ShaderNodeValue")
    world.name = NODE + "world_mean"
    world.outputs[0].default_value = world_mean * AMBIENT
    amb = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(colour, amb.inputs["Color"])
    nt.links.new(_math(nt, "MULTIPLY", ao, world.outputs[0]), amb.inputs["Strength"])
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(acc.outputs["Shader"], add.inputs[0])
    nt.links.new(amb.outputs["Emission"], add.inputs[1])
    return add.outputs["Shader"]


def world_mean(scene) -> float:
    """The scene world's mean radiance (luminance): its colour, or its environment image's mean x its strength."""
    world = scene.world
    if world is None or world.node_tree is None:
        return 0.0
    nodes = world.node_tree.nodes
    bgs = [n for n in nodes if n.type == "BACKGROUND"]
    lit = [n for n in bgs if n.inputs["Color"].is_linked and n.inputs["Color"].links[0].from_node.type == "TEX_ENVIRONMENT"]
    bg = (lit or bgs or [None])[0]  # the image light (the stage's world also has a camera-only backdrop)
    if bg is None:
        return 0.0
    strength = bg.inputs["Strength"].default_value
    if bg.inputs["Color"].is_linked and bg.inputs["Color"].links[0].from_node.type == "TEX_ENVIRONMENT":
        image = bg.inputs["Color"].links[0].from_node.image
        import numpy as np

        w, h = image.size
        px = np.empty(w * h * 4, np.float32)
        image.pixels.foreach_get(px)
        px = px.reshape(h, w, 4)[..., :3]
        lat = np.cos(np.linspace(-np.pi / 2, np.pi / 2, h))[:, None]  # the rows' solid angles
        lum = (px @ np.array([0.2126, 0.7152, 0.0722], np.float32)) * lat
        return float(lum.sum() / (lat.sum() * w)) * strength
    c = bg.inputs["Color"].default_value
    return float(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) * strength


def sync_world(scene) -> int:
    """Every hair material's image-light term set to the scene's world now (after the stage changes its world)."""
    mean = world_mean(scene)
    done = 0
    for mat in bpy.data.materials:
        node = mat.node_tree.nodes.get(NODE + "world_mean") if mat.node_tree else None
        if node is not None:
            node.outputs[0].default_value = mean * AMBIENT
            done += 1
    return done
