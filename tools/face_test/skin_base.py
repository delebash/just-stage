# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, a skin base for one character from several scans - not a copy of one scanned person (the user,
2026-11-02: "they cant keep looking like the same character or base, it has to be completelety adjustable like
methuman"). MetaHuman's way (a scanned texture index with wrinkle density, stubble, freckles and moles as controls):

1. `split`: each scan's skin in our layout (scan_bake.py's bake, only where scan_skin.py's mask says skin) taken
   apart in linear light - the fine layer (pores, fine lines: the skin over its 6-texel blur, ~1 mm), the mid layer
   (mottling, redness: the 6-texel blur over the 48-texel one, ~8 mm); its tone (the 48-texel blur) is dropped - each
   character has its own. The scanned person's own marks (moles, blemishes: small dark spots in the mid and fine
   layers) are taken out.
2. `compose`: one character's base as a ratio map around 1 - its pores from ONE scan (the next ones only filling
   where it didn't reach), its blotchiness mixed from 2-3, its regional colour (the broad layer, where `split` had
   scan_skin.py's colour mask and normals) from 2-3, plus its own mottling noise, age (how strong the fine layer
   is), redness, freckles and moles from its seed. The projection (test_face_project.py) multiplies it by the
   character's tone and blends it under the face.

Run (the tool environment): .dev/venv-rdf/Scripts/python -I tools/face_test/skin_base.py split NAME... | compose SEED
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np

DIR = Path("E:/Dev/3D/just-stage/.dev/facetest/scans")
FINE_SIGMA, MID_SIGMA = 6.0, 48.0  # texels of the 4096 HeadTile (~6 texels a mm on the face)
FEATHER = 48.0  # texels (~8 mm): a scan's edge fades in over this - at 6 every hand-over between the partial scans
#               showed as an edge (round 78: a smooth patch beside a stubbly one on the scalp)
#: skin's own range for the layers: colour shifts (a channel off the texel's brightness) and brightness swings beyond
#: these are a scan's leftovers - an ear's red inside, a necklace, a lip's edge (red minus blue to 0.4-0.5 at the 99th
#: percentile in ammamma's and yaro13's mid layers, lps 0.09) - soft-clipped (tanh) to them
HUE_RANGE, LUM_RANGE = 0.08, 0.35
EDGE = 12  # texels (~2 mm on the face): a scan's skin is used this far inside its mask's edge
#: stubble: on a stubbled scan's fine layer the small dark marks (its black top-hat, up to ~1 mm) in the beard and scalp
#: regions are kept by the character's stubble setting; at 0 they go - all but STUBBLE_FLOOR of them (the pores there
#: go with them: a shaved face still shows its follicles). Measured 2026-11-03 (char 12, fine detail = |lum - blur3|):
#: stubble 1 - beard 2.76, scalp 2.40, elsewhere 1.96; stubble 0 at floor 0.3 - beard 1.40, scalp 1.25 (smoother than
#: the rest of the face); 0.55 puts a shaved beard near the face's own 1.95 (the trend between the two)
STUBBLE_KERNEL, STUBBLE_FLOOR = 7, 0.55
#: the broad layer (the face's regional colour above ~8 mm: redder cheeks, nose and ears, the lips, darker round the
#: eyes - the part-by-part gate, 2026-11-05: without it the colour came from the painting, pale and even): the scan's
#: light taken out by a second-order spherical-harmonic fit of its log luminance on our fitted head's normals (the
#: standard low-order lighting model - Ramamoorthi & Hanrahan 2001; a studio's soft light is low-order), fitted at
#: SH_TEXELS, then the layer centred on the scan's own median skin; soft-clipped to skin's range like the others
SH_TEXELS = 512
BROAD_LUM, BROAD_HUE = 0.45, 0.15
#: the low layer's range (log): only a scan's gross leftovers (a shadowed fold, a stray hair) clipped; its holes filled
#: over LOW_FILL texels (~4 mm) of skin round them; its edge fades in over LOW_FEATHER (~2.7 mm) - at FEATHER (8 mm)
#: every feature beside a hole (eyes, brows, lips) faded with it
LOW_RANGE = 0.6  # 1.0 let a collar's edge and a fill's leftovers through as patches (composition 503's neck)
LOW_FILL, LOW_FEATHER = 24.0, 16.0
LOW_NEAR = 0.4  # the share of skin round a texel it needs: holes filled only well inside the skin (0.15 reached edges)
#: HAIR OUT, CC5's way (docs/plans/2026-11-06-inputs-audit.md: CC5's skin colour carries no hair - lashes, brows and
#: stubble are meshes): every scan has its own lashes and stray brow hairs round the eye and brow holes its skin mask
#: leaves (scan_skin.py labels eyes and brows, not the lashes on the lids or the hairs beside the brows) - a band of
#: HAIR_BAND texels (~5 mm) round every hole within EYE_ZONE of an eye's centre is left out of every layer; the holes
#: are then filled with the skin beside them (hair.mirror_fill for the detail, a pull-push for the colour). Near the
#: hairline (HAIRLINE texels, ~6 mm, outside the eye zone) stray strands are found and filled (hair.py, DullRazor).
#: Stubble stays out (a stubble groom, not paint): a stubbled scan is left out of the beard, the clean scans fill it;
#: a man keeps only the faint shaved tint CC5's diffuse has (`beard_shadow`, his stubbled scans' broad colour there).
#: stubble found per texel (the scan list's by-eye tags missed HSR0040's upper lip): in the beard's region, skin whose
#: dark marks (a 7-texel closing over the fine layer, averaged over STUBBLE_AREA texels) run STUBBLE_RATIO x the scan's
#: own clean face's is left out like hair
STUBBLE_RATIO, STUBBLE_AREA = 1.35, 18.0
EYE_ZONE = 0.035  # m
HAIR_BAND, HAIRLINE = 30, 36  # texels
BEARD_SHADOW = 0.35  # a man's default
#: round the eyes the scans' colour carries makeup (liner, mascara, shadow) and the sockets' baked shade - CC5's skin
#: has neither (makeup is its own layer): in the eye zone the colour's darkening is kept to EYE_DARK (log brightness,
#: ~12% - real skin's darker lids and circles) and its grey (makeup's) to skin's own hue, softly
EYE_DARK = 0.12
#: the seam with the body (the design's piece 4: seam-continuous): the head tile's colour detail fades to the plain tone
#: over the neck's last NECK_FADE metres above the UDIM head tile's border (tools/make_udim.py HEAD_Z, 1.28 m on the
#: default body) - the body tiles carry the tone (and their own detail), so the two meet without a step
HEAD_BORDER_Z, NECK_FADE = 1.28, 0.05


def _module(name, path):
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def regions(size=4096):
    """Where stubble grows, as soft masks in our HeadTile layout (cached in scans/regions.npz): the beard (upper lip,
    chin, jaw and the throat) and the scalp (above the hairline, the back and sides above the ears) - from our head's
    own geometry, measured from the eyes. Every identity shares this layout (one topology, one unwrap)."""
    cache = DIR / "regions.npz"
    if cache.exists():
        z = np.load(cache)
        return z["beard"], z["scalp"]
    up = _module("up", "E:/Dev/3D/just-stage/extension/juststage/core/uv_projection.py")
    E = np.load(DIR / "head_export.npz")
    (pts,), covered = up.raster_uv(E["tri_uv"], [E["co"][E["tris"]].astype(np.float32)], size)
    eye = (np.asarray(E["eye_left"]) + np.asarray(E["eye_right"])) / 2
    x, y, z = (pts[..., i] - eye[i] for i in range(3))
    front = 1.0 - _smooth(y, 0.06, 0.09)  # ahead of the ears
    beard = front * _smooth(-z, 0.035, 0.050) * (1.0 - _smooth(-z, 0.19, 0.22)) * (1.0 - _smooth(np.abs(x), 0.07, 0.09))
    scalp = np.maximum(_smooth(z, 0.05, 0.075), _smooth(y, 0.08, 0.11) * _smooth(z, -0.04, -0.01))
    beard, scalp = (np.where(covered, m, 0.0).astype(np.float16) for m in (beard, scalp))
    np.savez_compressed(cache, beard=beard, scalp=scalp)
    return beard, scalp


def eye_zone(size=4096):
    """Texels whose point on our head lies within EYE_ZONE of an eye's centre (lids, brows, the eyes' corners) - from
    our head's own geometry, like `regions` (cached in scans/eye_zone.npz)."""
    cache = DIR / "eye_zone.npz"
    if cache.exists():
        z = np.load(cache)["zone"]
        if z.shape[0] == size:
            return z
    up = _module("up", "E:/Dev/3D/just-stage/extension/juststage/core/uv_projection.py")
    E = np.load(DIR / "head_export.npz")
    (pts,), covered = up.raster_uv(E["tri_uv"], [E["co"][E["tris"]].astype(np.float32)], size)
    zone = np.zeros(pts.shape[:2], bool)
    for eye in (E["eye_left"], E["eye_right"]):
        zone |= np.linalg.norm(pts - np.asarray(eye, np.float32), axis=-1) < EYE_ZONE
    zone &= covered
    np.savez_compressed(cache, zone=zone)
    return zone


def neck_fade(size=4096):
    """1 on the head, falling to 0 at the head tile's border low on the neck (cached in scans/neck_fade.npz)."""
    cache = DIR / "neck_fade.npz"
    if cache.exists():
        z = np.load(cache)["fade"]
        if z.shape[0] == size:
            return z
    up = _module("up", "E:/Dev/3D/just-stage/extension/juststage/core/uv_projection.py")
    E = np.load(DIR / "head_export.npz")
    (pts,), _covered = up.raster_uv(E["tri_uv"], [E["co"][E["tris"]].astype(np.float32)], size)
    fade = _smooth(pts[..., 2], HEAD_BORDER_Z, HEAD_BORDER_Z + NECK_FADE).astype(np.float32)
    np.savez_compressed(cache, fade=fade)
    return fade


def _hair():
    return _module("hair", Path(__file__).with_name("hair.py"))


def _disc(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def smooth_fill(img, have, where):
    """Texels in `where` outside `have` filled from the skin round them, smoothly: a masked blur whose width grows with
    the distance to the nearest skin (4 texels at the edge, doubling outward), the widths blended - no blocks and no
    edge (a colour layer's holes)."""
    out = img.astype(np.float32).copy()
    todo = where & ~have
    if not todo.any() or not have.any():
        return out
    dist = cv2.distanceTransform((~have).astype(np.uint8), cv2.DIST_L2, 5)
    sigmas = [4.0 * 2**k for k in range(9)]  # 4 .. 1024 texels
    t = np.clip(np.log2(np.maximum(dist, 4.0) / 4.0), 0, len(sigmas) - 1)
    lo = np.floor(t).astype(int)
    frac = (t - lo)[..., None]
    acc = np.zeros_like(out)
    for k, sigma in enumerate(sigmas):
        sel = todo & ((lo == k) | (lo + 1 == k))
        if not sel.any():
            continue
        f = masked_blur(img, have, sigma)
        w = np.where((lo == k)[..., None], 1.0 - frac, frac)
        acc[sel] += (w * f)[sel]
    out[todo] = acc[todo]
    return out


def _inside(cover):
    """The head's own area: its coverage and every hole it encloses (eyes, brows, nostrils, mouth) - the outside found
    by a flood from the tile's border."""
    outside = (~cover).astype(np.uint8)
    h, w = outside.shape
    pad = np.pad(outside, 1, constant_values=1)
    mask = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(pad, mask, (0, 0), 2)
    return pad[1:-1, 1:-1] != 2


def _without_stubble(fine, keep):
    """A fine layer with its small dark marks (stubble and pores: closing minus itself, in brightness) lifted where
    `keep` (0-1 per texel) is below 1 - all but STUBBLE_FLOOR of them at 0."""
    luma = np.array([0.2126, 0.7152, 0.0722], np.float32)
    lum = fine @ luma
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (STUBBLE_KERNEL, STUBBLE_KERNEL))
    dark = cv2.morphologyEx(lum, cv2.MORPH_CLOSE, k) - lum  # >= 0 on the dark marks
    return fine + ((1.0 - STUBBLE_FLOOR) * (1.0 - keep) * dark)[..., None]


def linear(srgb):
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


WIDE = 16.0  # texels: masked_blur works on a shrunk copy beyond this


def masked_blur(img, valid, sigma):
    """A blur that only averages valid texels (normalized convolution). Wide ones (sigma over WIDE texels) on a copy
    shrunk so the blur is WIDE there, then grown back - the same smooth result, a kernel thousands of texels wide
    otherwise."""
    w = valid.astype(np.float32)
    if sigma <= WIDE:
        num = cv2.GaussianBlur(img * w[..., None], (0, 0), sigma)
        den = cv2.GaussianBlur(w, (0, 0), sigma)
        return num / np.maximum(den[..., None], 1e-6)
    h, wd = w.shape
    f = sigma / WIDE
    small = (max(1, int(round(wd / f))), max(1, int(round(h / f))))
    num = cv2.GaussianBlur(cv2.resize(img * w[..., None], small, interpolation=cv2.INTER_AREA), (0, 0), WIDE)
    den = cv2.GaussianBlur(cv2.resize(w, small, interpolation=cv2.INTER_AREA), (0, 0), WIDE)
    if num.ndim == 2:
        num = num[..., None]
    out = num / np.maximum(den[..., None], 1e-6)
    return cv2.resize(out, (wd, h), interpolation=cv2.INTER_LINEAR).reshape(h, wd, -1)


def _sh9(n):
    """Real spherical harmonics to order 2 at unit normals (unnormalised: the fit's coefficients absorb the scale)."""
    x, y, z = n[..., 0], n[..., 1], n[..., 2]
    return np.stack([np.ones_like(x), x, y, z, x * y, x * z, y * z, x * x - y * y, 3 * z * z - 1], -1)


def _broad(lin, valid_colour, valid_skin, normals):
    """The scan's colour above MID_SIGMA in log space, its fitted light divided out (luminance only - the colour's
    regional hue stays), centred on its own median skin."""
    luma = np.array([0.2126, 0.7152, 0.0722], np.float32)
    log_b = np.log(np.maximum(masked_blur(lin, valid_colour, MID_SIGMA), 1e-4))
    lum = log_b @ luma
    size = lum.shape[0]
    small = cv2.resize(lum, (SH_TEXELS, SH_TEXELS), interpolation=cv2.INTER_AREA)
    n_small = cv2.resize(normals.astype(np.float32), (SH_TEXELS, SH_TEXELS), interpolation=cv2.INTER_AREA)
    ok = cv2.resize(valid_skin.astype(np.uint8), (SH_TEXELS, SH_TEXELS), interpolation=cv2.INTER_NEAREST) > 0
    length = np.linalg.norm(n_small, axis=-1)
    ok &= length > 0.5
    unit = n_small / np.maximum(length, 1e-6)[..., None]
    basis = _sh9(unit)
    coef, *_ = np.linalg.lstsq(basis[ok], small[ok], rcond=None)
    shading_small = (basis @ coef).astype(np.float32)
    shading = cv2.resize(shading_small, (size, size), interpolation=cv2.INTER_LINEAR)
    broad = log_b - shading[..., None]
    broad -= np.median(broad[valid_skin], axis=0)
    broad[~valid_colour] = 0.0
    lum_b = broad @ luma
    hue = broad - lum_b[..., None]
    broad = (BROAD_LUM * np.tanh(lum_b / BROAD_LUM))[..., None] + BROAD_HUE * np.tanh(hue / BROAD_HUE)
    lit = basis[ok] @ coef
    return broad.astype(np.float32), float(np.std(lit)), float(np.std(small[ok] - lit)), shading


def split(name):
    """The scan's skin as baked into our layout (scan_bake.py: colour + coverage), only where the skin mask
    (scan_skin.py) says skin - the route of `docs/plans/2026-11-02-scan-skin-base.md`."""
    d = DIR / name
    srgb = cv2.imread(str(d / "bake_colour.png"))[..., ::-1].astype(np.float32) / 255.0
    size = srgb.shape[0]
    cover = cv2.imread(str(d / "bake_cover.png"), 0) > 127
    skin = cv2.resize(cv2.imread(str(d / "skin.png"), 0), (size, size), interpolation=cv2.INTER_LINEAR) > 127
    mask = cover  # what this scan reached; the head's whole layout is the union over scans
    # hair out (CC5's way): the band round the eye and brow holes left out; stray strands by the hairline filled
    zone = eye_zone(size)
    holes = zone & ~(skin & cover)
    band = (cv2.dilate(holes.astype(np.uint8), _disc(HAIR_BAND)) > 0) & zone & ~holes
    hairline = (cv2.dilate((cover & ~skin).astype(np.uint8), _disc(HAIRLINE)) > 0) & skin & cover & ~zone
    # the strands: by the hairline, and all over the eye zone - the lashes lie up to ~10 mm across the lids in a
    # photo of open eyes, single strands beyond the band's dense roots
    strands = _hair().mask(srgb, (hairline | zone) & skin & cover)
    srgb = np.clip(_hair().fill(srgb, strands), 0.0, 1.0)
    valid = cover & skin & ~band & (srgb.max(axis=2) > 0.05)
    # pulled in ~2 mm from its edges: the collar's and hairline's shadows sit just inside a skin mask (round 74's dark
    # squiggles low on the neck)
    valid = cv2.erode(valid.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (EDGE * 2 + 1,) * 2)) > 0
    lin = np.maximum(linear(srgb), 1e-4)
    b_fine = masked_blur(lin, valid, FINE_SIGMA)
    b_mid = masked_blur(lin, valid, MID_SIGMA)
    fine = np.log(lin / np.maximum(b_fine, 1e-4))
    mid = np.log(np.maximum(b_fine, 1e-4) / np.maximum(b_mid, 1e-4))
    # stubble, per texel: the beard's skin with far more dark marks than this scan's own clean face
    beard_r, scalp_r = (m.astype(np.float32) for m in regions(size))
    lum_f = fine @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    marks_d = cv2.morphologyEx(lum_f, cv2.MORPH_CLOSE, _disc(STUBBLE_KERNEL // 2)) - lum_f
    dens = masked_blur(marks_d[..., None], valid, STUBBLE_AREA)[..., 0]
    clean = valid & (beard_r < 0.05) & (scalp_r < 0.05) & ~zone
    stubbly = np.zeros_like(valid)
    if clean.sum() > 1000:
        stubbly = (beard_r > 0.3) & valid & (dens > STUBBLE_RATIO * float(np.median(dens[clean])))
        stubbly = cv2.morphologyEx(stubbly.astype(np.uint8), cv2.MORPH_OPEN, _disc(3)) > 0
        stubbly = cv2.dilate(stubbly.astype(np.uint8), _disc(12)) > 0
        valid &= ~stubbly
        fine[stubbly], mid[stubbly] = 0.0, 0.0
    # the scanned person's own marks: spots darker than their surroundings by >30%, ~0.5-6 mm across (at >12% the bald
    # scan's scalp stubble and pores went too - 23% of its texels, a patchwork of blurred holes)
    lum = (mid + fine) @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    spot = cv2.GaussianBlur(lum, (0, 0), 2.0) - cv2.GaussianBlur(lum, (0, 0), 12.0)
    dark = ((spot < -0.30) & valid).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(dark)
    area = stats[:, cv2.CC_STAT_AREA]
    small = np.isin(labels, np.flatnonzero((area >= 10) & (area < 1200) & (np.arange(count) > 0)))
    marks = cv2.dilate(small.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    keep = valid & ~marks
    fine[marks] = 0.0
    mid[marks] = masked_blur(mid, keep, 12.0)[marks]
    fine[~valid], mid[~valid] = 0.0, 0.0
    np.clip(fine, -0.5, 0.12, out=fine)  # the scan's own shine (white specks in a photogrammetry colour map) out
    luma = np.array([0.2126, 0.7152, 0.0722], np.float32)
    for layer in (mid, fine):
        lum = layer @ luma
        hue = layer - lum[..., None]
        layer[...] = (LUM_RANGE * np.tanh(lum / LUM_RANGE))[..., None] + HUE_RANGE * np.tanh(hue / HUE_RANGE)
    extra = {"tone": np.median(lin[valid], axis=0).astype(np.float32)}  # its skin's own colour, linear
    if (d / "colour.png").exists() and (d / "normals.npy").exists():  # scan_skin.py's colour mask and normals
        colour = cv2.resize(cv2.imread(str(d / "colour.png"), 0), (size, size), interpolation=cv2.INTER_LINEAR) > 127
        valid_colour = cover & colour & ~band & ~stubbly & (srgb.max(axis=2) > 0.05)
        valid_colour = cv2.erode(valid_colour.astype(np.uint8),
                                 cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (EDGE * 2 + 1,) * 2)) > 0
        normals = cv2.resize(np.load(d / "normals.npy").astype(np.float32), (size, size),
                             interpolation=cv2.INTER_LINEAR)
        broad, lit, rest, shading = _broad(lin, valid_colour, valid & valid_colour, normals)
        # the low layer: the colour itself above the pores (blurred FINE_SIGMA), its fitted light out, centred on its
        # own skin - lips and regional colour kept whole (a composed skin's colour, `compose`'s "colour": "scans")
        # the scan's non-skin holes (eyes, brows, nostrils, a collar) filled from the skin round them first, so the
        # features' surroundings aren't faded out with the holes (round 502: the face's colour came out at ~30%)
        reach = cv2.erode(cover.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (EDGE * 4 + 1,) * 2)) > 0
        near = cv2.GaussianBlur(valid_colour.astype(np.float32), (0, 0), LOW_FILL) > LOW_NEAR
        valid_low = reach & near
        filled = np.where(valid_colour[..., None], lin, masked_blur(lin, valid_colour, LOW_FILL))
        low = np.log(np.maximum(masked_blur(filled, valid_low, FINE_SIGMA), 1e-4)) - shading[..., None]
        low -= np.median(low[valid & valid_colour], axis=0)
        low[~valid_low] = 0.0
        np.clip(low, -LOW_RANGE, LOW_RANGE, out=low)
        extra.update(broad=broad.astype(np.float16), low=low.astype(np.float16), valid_colour=valid_colour,
                     valid_low=valid_low)
        print(f"{name}: broad layer - the fitted light's spread {lit:.3f} (log luminance), what stays {rest:.3f}")
    np.savez_compressed(d / "layers.npz", fine=fine.astype(np.float16), mid=mid.astype(np.float16), valid=valid,
                        **extra)
    print(f"{name}: hair out - the eye and brow band {band.sum()} texels, {strands.sum()} texels of strands, "
          f"{stubbly.sum()} texels of stubble")
    print(f"{name}: skin on {valid.mean() / mask.mean():.0%} of the texels the scan reached ({valid.mean():.1%} of the "
          f"tile); {count - 1} dark spots, "
          f"{int(small.any() and np.unique(labels[small]).size)} small ones taken out ({marks.sum()} texels); "
          f"fine layer spread {fine[valid].std():.3f}, mid {mid[valid].std():.3f}")


def noise(shape, rng, sigma):
    """Smooth random field, zero mean, unit spread."""
    n = cv2.GaussianBlur(rng.standard_normal(shape).astype(np.float32), (0, 0), sigma)
    return n / max(float(n.std()), 1e-6)


def _feathered(valid):
    """A scan's coverage with its edge faded in over FEATHER texels (inside its own texels only)."""
    v = valid.astype(np.float32)
    return np.clip(cv2.GaussianBlur(v, (0, 0), FEATHER) * 2.0 - 1.0, 0.0, 1.0) * v


#: the scans' own relief (scan_bake.py's bake_normal.png: their surface against our fitted head's, tangent space): its
#: low frequencies above RELIEF_HP texels (~7 mm - the fit's leftover) taken out, kept inside each scan's skin mask
#: (no hair, brows or eyes), faded in over RELIEF_FEATHER
RELIEF_HP, RELIEF_FEATHER = 40.0, 16.0


def _relief(p, layers, shape, keep=None, scans=None, inside=None):
    """A composed skin's mid-scale relief - folds, creases, lines - as tangent-space XY (H x W x 2) from its relief
    scans (`relief_from`, default its colour scans), a weighted mean; None when no scan has one. A stubbled scan only
    as far as `keep` (its stubble's lumps are hair); the holes inside the head (`inside`) filled with the relief
    beside them (hair.mirror_fill)."""
    num, tot = np.zeros((*shape, 2), np.float32), np.zeros(shape, np.float32)
    for n, w in p.get("relief_from", p.get("broad_from", p["mid_from"])).items():
        f = DIR / n / "bake_normal.png"
        if not f.exists():
            continue
        nm = cv2.imread(str(f), cv2.IMREAD_UNCHANGED)[..., [2, 1, 0]].astype(np.float32) / 65535.0
        xy = cv2.resize(nm[..., :2], shape[::-1], interpolation=cv2.INTER_AREA) * 2.0 - 1.0
        valid = layers[n]["valid"]
        hp = xy - masked_blur(np.dstack([xy, np.zeros(shape, np.float32)]), valid, RELIEF_HP)[..., :2]
        v = valid.astype(np.float32)
        a = w * np.clip(cv2.GaussianBlur(v, (0, 0), RELIEF_FEATHER) * 2.0 - 1.0, 0.0, 1.0) * v
        if keep is not None and scans is not None and scans[n]["stubble"]:
            a = a * keep
        num += a[..., None] * hp
        tot += a
    if not tot.any():
        return None
    if inside is None:
        return num / np.maximum(tot, 1e-6)[..., None] * np.clip(tot / 0.5, 0.0, 1.0)[..., None]
    have = tot > 0.25
    return _hair().mirror_fill(num / np.maximum(tot, 1e-6)[..., None], have, inside)


def compose(seed, params=None):
    """One character's base: a ratio map (H x W x 3, ~1) and where the scans covered. The approved way (TASKS "THE
    SCAN ROUTE" (6), MetaHuman's index): the pores and fine lines from ONE scan - averaging several people's pores at a
    texel cancels them (~1/sqrt(n)) - the next scans in this character's order only filling where that one didn't
    reach; the blotchiness (mid layer) mixed from 2-3 scans, scaled back to one scan's strength; the tone is the
    character's own (the projection multiplies it in). Its sex picks the scans first (a woman's pores from women's
    scans; the others only fill where those didn't reach), and its stubble settings (beard, scalp; 0 for a woman)
    decide how much of a stubbled scan's stubble stays."""
    rng = np.random.default_rng(seed)
    scans = _module("scan_list", Path(__file__).with_name("scan_list.py")).SCANS
    names = sorted(f.parent.name for f in DIR.glob("*/layers.npz"))
    sex = (params or {}).get("sex") or str(rng.choice(["m", "f"]))
    own_sex = [str(n) for n in rng.permutation([n for n in names if scans[n]["sex"] == sex])]
    others = [str(n) for n in rng.permutation([n for n in names if scans[n]["sex"] != sex])]
    others.sort(key=lambda n: scans[n]["stubble"])  # a smooth scan fills before a stubbled one
    pool = own_sex if len(own_sex) >= 2 else names
    k = int(min(len(pool), rng.integers(2, 4)))
    mixed = [str(n) for n in rng.choice(pool, k, replace=False)]
    male = sex == "m"
    p = {"sex": sex, "fine_from": own_sex + others,
         "mid_from": dict(zip(mixed, (float(w) for w in rng.dirichlet(np.ones(k))), strict=True)),
         "stubble": 0.0, "scalp_stubble": 0.0,  # stubble is a groom (CC5's Stubble mesh), not paint
         "beard_shadow": BEARD_SHADOW if male else 0.0,
         "age": float(rng.uniform(0.7, 1.3)), "mottle": float(rng.uniform(0.6, 1.2)),
         "redness": float(rng.uniform(0.0, 0.06)), "freckles": float(rng.uniform(0.0, 1.0)),
         "moles": int(rng.integers(2, 12)), **(params or {})}
    if p.get("pores_first"):  # a chosen scan's pores first (a character made to a description), the order kept after it
        p["fine_from"] = [p["pores_first"]] + [n for n in p["fine_from"] if n != p["pores_first"]]
    layers = {n: np.load(DIR / n / "layers.npz") for n in set(p["fine_from"]) | set(p["mid_from"])}
    shape = layers[p["fine_from"][0]]["fine"].shape[:2]
    beard, scalp = (m.astype(np.float32) for m in regions(shape[0]))
    keep = 1.0 - np.clip(beard * (1.0 - p["stubble"]) + scalp * (1.0 - p["scalp_stubble"]), 0.0, 1.0)
    # fine: the first scan over the next, each only where the ones before it left room
    fine, mid_fill, left = np.zeros((*shape, 3), np.float32), np.zeros((*shape, 3), np.float32), np.ones(shape, np.float32)
    for n in p["fine_from"]:
        a = left * _feathered(layers[n]["valid"])
        if scans[n]["stubble"]:
            a = a * keep  # out of the beard and scalp unless the character keeps stubble: a clean scan fills
        if not a.any():
            continue
        f = layers[n]["fine"].astype(np.float32)
        if scans[n]["stubble"] and (p["stubble"] > 0 or p["scalp_stubble"] > 0):
            f = _without_stubble(f, keep)
        fine += a[..., None] * f
        mid_fill += a[..., None] * layers[n]["mid"].astype(np.float32)
        left -= a
    # each texel's detail at full strength where the scans reached it, and the holes inside the head (eyes, brows, the
    # bands left out round them) filled with the skin beside them - pores, not a smooth patch
    got = 1.0 - left
    have = got > 0.5
    inside = _inside(got > 0.05)
    fine = _hair().mirror_fill(fine / np.maximum(got, 1e-6)[..., None], have, inside)
    mid_fill = _hair().mirror_fill(mid_fill / np.maximum(got, 1e-6)[..., None], have, inside)
    cover = inside
    # mid: the chosen scans' weighted sum over sqrt(sum of squared weights) - for unrelated patterns that keeps one
    # scan's strength (a plain mean shrinks it); where none of them reached, the fine order's mid layer
    num, sq, total = np.zeros((*shape, 3), np.float32), np.zeros(shape, np.float32), np.zeros(shape, np.float32)
    for n, w in p["mid_from"].items():
        a = w * _feathered(layers[n]["valid"])
        num += a[..., None] * layers[n]["mid"].astype(np.float32)
        sq += a * a
        total += a
    # the fine order's mid layer joins as one more part wherever the chosen scans fall short - a weight, not a switch
    # (where their coverage ended, the switch drew an edge, round 78)
    b = np.clip(1.0 - total, 0.0, 1.0)
    num += b[..., None] * mid_fill
    sq += b * b
    mid = num / np.sqrt(np.maximum(sq, 1e-8))[..., None]
    # its own mottling, so two characters from the same scans still differ (and texels no scan reached get some)
    own = 0.04 * noise(shape, rng, 10.0)[..., None] * np.array([1.0, 0.9, 0.85], np.float32)
    # broad: the face's regional colour from 2+ scans (the likeness rule, the review brief §10: "broad and mid colour
    # from two or more scans") - a weighted mean, faded out where they don't reach; a stubbled scan's beard area only
    # as far as this character's own stubble
    num_b, tot_b = np.zeros((*shape, 3), np.float32), np.zeros(shape, np.float32)
    for n, w in p.get("broad_from", p["mid_from"]).items():
        if "broad" not in layers[n].files:
            continue
        a = w * _feathered(layers[n]["valid_colour"])
        if scans[n]["stubble"]:
            a *= 1.0 - beard * (1.0 - p["stubble"])
        num_b += a[..., None] * layers[n]["broad"].astype(np.float32)
        tot_b += a
    broad = num_b / np.maximum(tot_b, 1e-6)[..., None] * np.clip(tot_b / 0.5, 0.0, 1.0)[..., None]
    tones = {n: w for n, w in p.get("broad_from", p["mid_from"]).items() if "tone" in layers[n].files}
    if tones and "tone" not in p:  # the scans' own skin colour, blended as their broad layers are (a composed skin's)
        total = sum(tones.values())
        p["tone"] = [float(v) for v in sum(w / total * layers[n]["tone"].astype(np.float64) for n, w in tones.items())]
    if p.get("colour") == "scans":
        # a composed skin with no painting over it: its colour above the pores is its 2-3 scans' own (the low
        # layers, a weighted mean - their lips and regional colour line up on our layout), the pores from one
        num_l, tot_l = np.zeros((*shape, 3), np.float32), np.zeros(shape, np.float32)
        num_s, tot_s = np.zeros((*shape, 3), np.float32), np.zeros(shape, np.float32)  # stubbled scans' beard
        for n, w in p.get("broad_from", p["mid_from"]).items():
            if "valid_low" not in layers[n].files:
                continue
            v = layers[n]["valid_low"].astype(np.float32)
            a = w * np.clip(cv2.GaussianBlur(v, (0, 0), LOW_FEATHER) * 2.0 - 1.0, 0.0, 1.0) * v
            if scans[n]["stubble"]:
                num_s += (a * beard)[..., None] * layers[n]["low"].astype(np.float32)
                tot_s += a * beard
                a = a * keep
            num_l += a[..., None] * layers[n]["low"].astype(np.float32)
            tot_l += a
        have_l = tot_l > 0.25
        low = smooth_fill(num_l / np.maximum(tot_l, 1e-6)[..., None], have_l, inside)  # no edge where scans end
        low[~inside] = 0.0
        # no makeup or baked socket shade round the eyes: darkening there held to EYE_DARK, its hue to the skin's
        zone_w = cv2.GaussianBlur(eye_zone(shape[0]).astype(np.float32), (0, 0), 24.0)
        luma = np.array([0.2126, 0.7152, 0.0722], np.float32)
        lum_l = low @ luma
        lift = np.maximum(-EYE_DARK - lum_l, 0.0) * zone_w
        hue_l = low - lum_l[..., None]
        low = low + lift[..., None] - hue_l * (zone_w * np.clip((-lum_l - EYE_DARK) / EYE_DARK, 0.0, 1.0))[..., None]
        if p.get("beard_shadow", 0.0) > 0 and tot_s.any():
            # CC5's faint shaved tint: the stubbled scans' beard darker than the clean colour there, brightness only,
            # softened (~2 mm) - the stubble itself is a groom
            stub = num_s / np.maximum(tot_s, 1e-6)[..., None]
            luma = np.array([0.2126, 0.7152, 0.0722], np.float32)
            dark = np.minimum((stub - low) @ luma, 0.0) * (tot_s > 0.25)
            tint = cv2.GaussianBlur(dark.astype(np.float32), (0, 0), 12.0) * beard * p["beard_shadow"]
            low += tint[..., None] * np.array([1.0, 1.0, 0.95], np.float32)
        ratio_log = p["age"] * fine + low + 0.5 * own
        relief = _relief(p, layers, shape, keep, scans, inside)
        if relief is not None:
            p["relief_file"] = f"base_char{seed}_relief.npy"
            np.save(DIR / p["relief_file"], relief.astype(np.float16))
    else:
        ratio_log = p["age"] * fine + p["mottle"] * mid + p.get("broad", 1.0) * broad + own
    ratio_log[..., 0] += p["redness"] * noise(shape, rng, 24.0)  # patchy redness
    # freckles (small, many) and moles (few, larger, darker brown), placed by its seed
    spots = np.zeros(shape, np.float32)
    for count, radius, depth in ((int(4000 * p["freckles"]), 2.5, 0.10), (p["moles"], 6.0, 0.45)):
        ys, xs = rng.integers(0, shape[0], count), rng.integers(0, shape[1], count)
        for y, x in zip(ys, xs, strict=True):
            r = float(radius * rng.uniform(0.6, 1.4))
            cv2.circle(spots, (int(x), int(y)), max(1, int(round(r))), float(depth * rng.uniform(0.5, 1.0)), -1)
    spots = cv2.GaussianBlur(spots, (0, 0), 1.0)
    ratio_log -= spots[..., None] * np.array([0.8, 1.0, 1.2], np.float32)  # brown: blue darkest
    # skin keeps skin's hue order: the ratio may not turn a texel greener than it is red, nor bluer than green, by more
    # than 2% (the painting's own guard in test_face_project; walter's scalp came out green and blotchy, 2026-11-03)
    ratio_log[..., 1] = np.minimum(ratio_log[..., 1], ratio_log[..., 0] + 0.02)
    ratio_log[..., 2] = np.minimum(ratio_log[..., 2], ratio_log[..., 1] + 0.02)
    ratio = np.exp(ratio_log).astype(np.float32)
    # a ratio around 1: each channel's mean over what the scans covered set to 1 - the scans' own shading had left it
    # below (round 74's scalp darker and more orange than the face); the character's tone is the projection's
    ratio /= ratio[cover].mean(axis=0)
    return ratio, cover, p


def main(argv):
    if argv[0] == "split":
        for name in argv[1:]:
            split(name)
    elif argv[0] == "compose":  # compose SEED ['{"sex": "f", "fine_from": [...], ...}']
        seed = int(argv[1])
        ratio, cover, p = compose(seed, json.loads(argv[2]) if len(argv) > 2 else None)
        out = np.clip(0.45 * ratio, 0, 1) ** (1 / 2.2)  # a flat mid-skin tone, only to look at it
        cv2.imwrite(str(DIR / f"base_char{seed}.png"), (out[..., ::-1] * 255).astype(np.uint8))
        cv2.imwrite(str(DIR / f"base_char{seed}_small.png"),
                    cv2.resize((out[..., ::-1] * 255).astype(np.uint8), (1024, 1024), interpolation=cv2.INTER_AREA))
        np.save(DIR / f"base_char{seed}.npy", ratio.astype(np.float16))  # for the projection (no OpenCV in Blender)
        np.save(DIR / f"base_char{seed}_cover.npy", cover)
        (DIR / f"base_char{seed}.json").write_text(json.dumps(p, indent=1))
        print(f"char {seed}: {json.dumps(p)}; covered {cover.mean():.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
