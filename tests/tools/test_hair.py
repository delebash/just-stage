# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Hair out of a skin image (tools/face_test/hair.py) - CC5's way: hair is geometry, a skin's colour has none
(docs/plans/2026-11-06-inputs-audit.md). Run in the tool environment:

    .dev/venv-rdf/Scripts/python -m pytest tests/tools/test_hair.py
"""

import importlib.util
from pathlib import Path

import cv2
import numpy as np

spec = importlib.util.spec_from_file_location(
    "hair", Path(__file__).resolve().parents[2] / "tools" / "face_test" / "hair.py"
)
hair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hair)


def _skin(rng, size=256):
    """A skin-like image: a warm tone with pores (small round dark dots) and mottling."""
    img = np.full((size, size, 3), (0.62, 0.45, 0.38), np.float32)
    img *= (1.0 + 0.05 * cv2.GaussianBlur(rng.standard_normal((size, size)).astype(np.float32), (0, 0), 8.0))[..., None]
    for _ in range(400):
        y, x = rng.integers(4, size - 4, 2)
        cv2.circle(img, (int(x), int(y)), 1, (0.50, 0.35, 0.29), -1)
    return img


def test_hairs_are_found_and_pores_are_not():
    rng = np.random.default_rng(1)
    img = _skin(rng)
    truth = np.zeros(img.shape[:2], np.uint8)
    for k in range(12):  # dark hairs, 1 texel wide, any angle, 8-40 texels long
        a = rng.uniform(0, np.pi)
        x0, y0 = rng.integers(40, 216, 2)
        n = rng.integers(8, 40)
        x1, y1 = int(x0 + n * np.cos(a)), int(y0 + n * np.sin(a))
        cv2.line(img, (int(x0), int(y0)), (x1, y1), (0.18, 0.12, 0.10), 1, cv2.LINE_AA)  # soft, as a scan shows a hair
        cv2.line(truth, (int(x0), int(y0)), (x1, y1), 1, 1)
    cv2.line(img, (20, 230), (120, 200), (0.85, 0.82, 0.78), 1, cv2.LINE_AA)  # a white hair
    cv2.line(truth, (20, 230), (120, 200), 1, 1)
    mask = hair.mask(img)
    found = (mask & truth.astype(bool)).sum() / truth.sum()
    assert found > 0.85, found
    pores = (img.mean(axis=2) < 0.42) & ~cv2.dilate(truth, np.ones((5, 5), np.uint8)).astype(bool)
    assert (mask & pores).sum() / max(pores.sum(), 1) < 0.1  # the pores stay


def test_cleaning_leaves_skin_where_hair_was():
    rng = np.random.default_rng(2)
    clean = _skin(rng)
    img = clean.copy()
    for y in range(60, 200, 9):  # a brow's worth of hairs
        cv2.line(img, (60, y), (190, y + 25), (0.15, 0.10, 0.08), 1, cv2.LINE_AA)
    out, mask = hair.clean(img)
    hairy = mask.astype(bool)
    assert hairy.sum() > 500
    before = np.abs(img - clean)[hairy].mean()
    after = np.abs(out - clean)[hairy].mean()
    assert after < 0.25 * before, (before, after)
    assert np.abs(out - img)[~cv2.dilate(mask, np.ones((7, 7), np.uint8)).astype(bool)].max() < 1e-6  # nothing else


def test_a_hole_in_the_pores_is_filled_with_pores():
    rng = np.random.default_rng(3)
    fine = cv2.GaussianBlur(rng.standard_normal((200, 200)).astype(np.float32), (0, 0), 1.0)[..., None].repeat(3, 2)
    have = np.ones((200, 200), bool)
    cv2.ellipse(have.view(np.uint8), (100, 100), (40, 12), 20, 0, 360, 0, -1)  # a brow-shaped hole
    hole = ~have
    out = hair.mirror_fill(np.where(have[..., None], fine, 0.0), have, np.ones_like(have))
    assert np.allclose(out[have], fine[have])
    inside, outside = out[hole].std(), fine[have].std()
    assert 0.8 * outside < inside < 1.2 * outside  # pores at their own strength, not a smooth patch


skin_base_spec = importlib.util.spec_from_file_location(
    "skin_base", Path(__file__).resolve().parents[2] / "tools" / "face_test" / "skin_base.py"
)
skin_base = importlib.util.module_from_spec(skin_base_spec)
skin_base_spec.loader.exec_module(skin_base)


def test_a_colour_hole_fills_smoothly_without_blocks():
    y, x = np.mgrid[0:256, 0:256].astype(np.float32)
    img = np.dstack([x / 256, y / 256, 0.5 + 0 * x])
    have = np.ones((256, 256), bool)
    cv2.circle(have.view(np.uint8), (128, 128), 60, 0, -1)
    out = skin_base.smooth_fill(img, have, np.ones_like(have))
    assert np.allclose(out[have], img[have])
    step = np.abs(np.diff(out[..., 0], axis=1))[~have[:, 1:]].max()
    assert step < 0.02  # no block edges (a gradient of 1/256 a texel)


def test_the_heads_inside_holds_its_enclosed_holes():
    cover = np.zeros((100, 100), bool)
    cover[10:90, 10:90] = True
    cover[40:60, 40:60] = False  # an eye
    inside = skin_base._inside(cover)
    assert inside[50, 50] and inside[20, 20] and not inside[5, 5]


def test_a_wide_hole_in_a_relief_fades_to_flat_not_streaks():
    """A relief (tangent XY, 0 = flat) with a hole wider than the skin round it: the mirror can't reach, and the old
    fallback (the edge's own texel) streaked the scan's edge across the hole - wedges of constant tilt on the face
    (the gate, 2026-11-06). With `neutral`, the fill carries the skin's detail in from the edge and fades to it."""
    rng = np.random.default_rng(3)
    size = 256
    relief = (0.15 * rng.standard_normal((size, size, 2))).astype(np.float32)
    relief[:, :, :] = cv2.GaussianBlur(relief, (0, 0), 1.0)
    relief[:, 100:104] = 0.6  # the scan's edge: a strong rim just outside the hole
    have = np.zeros((size, size), bool)
    have[:, :104] = True  # skin on the left only; the hole is 152 texels wide
    where = ~have
    filled = hair.mirror_fill(relief, have, where, neutral=0.0, depth=(24, 24))
    deep = filled[:, 104 + 60 :]
    assert np.abs(deep).max() == 0.0  # flat deep in the hole, no streak
    near = filled[:, 104 : 104 + 20]
    assert np.abs(near).mean() > 0.03  # the skin's detail carried in near the edge
    old = hair.mirror_fill(relief, have, where)
    assert np.abs(old[:, 104 + 60 :]).mean() > 0.1  # the old fill streaked the edge (kept for colour)


def test_relief_debris_is_found_and_folds_are_kept():
    """A scan's relief carries debris - rings round its holes (nostrils), arcs at its edges - far steeper than skin's
    folds (gate run 7: gashes on the Average woman's temple and cheek; her head relief's p99.5 0.5 against folds under
    0.25). The mask covers the debris and a few texels round it, not the folds."""
    size = 256
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    relief = np.zeros((size, size, 2), np.float32)
    relief[..., 1] = 0.12 * np.sin(xx / 9.0)  # folds: gentle, everywhere
    ring = np.abs(np.hypot(xx - 180, yy - 80) - 12) < 1.5
    relief[ring, 0] = 0.7  # a nostril's ring
    mask = hair.relief_debris(relief, limit=0.3, grow=4)
    assert mask[ring].all()
    assert mask[np.abs(np.hypot(xx - 180, yy - 80) - 12) < 5].mean() > 0.9  # and round it
    assert mask[:, :120].mean() == 0.0  # the folds kept


def test_small_red_spots_are_found_and_a_mole_is_left():
    """The person's small red spots out of a body scan's colour (`hair.spots`, 2026-11-07: Artec's torso showed 15x
    HD Aaron's count): small blobs redder than the skin round them are found; a larger mole and the pores are not."""
    rng = np.random.default_rng(3)
    img = _skin(rng)
    px_per_mm = 4.0  # a ~1 mm spot is 4 texels across
    dots = [(int(y), int(x)) for y, x in rng.integers(20, 236, (30, 2))]
    for y, x in dots:
        cv2.circle(img, (x, y), 2, (0.66, 0.36, 0.33), -1)  # redder than the skin: R up, G down
    cv2.circle(img, (128, 128), 12, (0.40, 0.25, 0.20), -1)  # a mole: larger, darker brown
    found = hair.spots(img, np.ones(img.shape[:2], bool), px_per_mm)
    hit = np.mean([found[y, x] for y, x in dots])
    assert hit > 0.8, hit
    assert not found[124:133, 124:133].any()  # the mole kept
    assert found.mean() < 0.05  # not the skin


def test_unred_takes_a_spots_redness_and_keeps_its_lightness():
    """`hair.unred`: a red spot brought to its surroundings' log R/G, its green and blue (its lightness) kept - a fill
    left stains where spots cluster (2026-11-07)."""
    rng = np.random.default_rng(4)
    img = _skin(rng)
    cv2.circle(img, (64, 64), 2, (0.66, 0.36, 0.33), -1)
    where = np.zeros(img.shape[:2], bool)
    where[60:69, 60:69] = True
    out = hair.unred(img, where, np.ones(img.shape[:2], bool), 4.0)
    skin_ratio = np.median(img[..., 0] / img[..., 1])
    assert abs(out[64, 64, 0] / out[64, 64, 1] - skin_ratio) < 0.05 * skin_ratio
    assert np.allclose(out[..., 1:], img[..., 1:])  # green and blue untouched
    assert np.allclose(out[~where], img[~where])  # the rest untouched
