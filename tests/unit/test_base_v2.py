# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage base v2's appended vertices (docs/plans/2026-11-05-lid-anatomy-build.md): the skin set, and an appended
vertex carried by every target through its birth face's frame (Blender's Surface Deform method)."""

import numpy as np

from juststage.core import makehuman


def test_the_skin_is_hm08s_body_and_everything_appended():
    mask = makehuman.skin_mask(makehuman.HM08_VERTICES + 5)
    assert mask[: makehuman.BODY_VERTICES].all()
    assert not mask[makehuman.BODY_VERTICES : makehuman.HM08_VERTICES].any()  # the helpers and joint cubes
    assert mask[makehuman.HM08_VERTICES :].all()
    assert len(makehuman.skin_indices(makehuman.HM08_VERTICES)) == makehuman.BODY_VERTICES


def _setup(rng):
    old = rng.normal(size=(40, 3))
    parents = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 9]])
    t = np.array([0.5, 0.3, 0.5])
    wanted = rng.normal(size=(3, 3)) * 0.2 + old[parents[:, 0]]
    app = makehuman.Appended.measure(old, parents, t, wanted)
    return old, app, wanted


def test_an_appended_vertex_sits_where_it_was_measured():
    old, app, wanted = _setup(np.random.default_rng(1))
    assert np.allclose(makehuman.place_appended(old, app), wanted)


def test_it_follows_a_turn_a_move_and_a_scale_of_its_face():
    rng = np.random.default_rng(2)
    old, app, wanted = _setup(rng)
    q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    q *= np.sign(np.linalg.det(q))  # a rotation
    moved = 1.3 * old @ q.T + np.array([0.1, -0.2, 0.3])
    assert np.allclose(makehuman.place_appended(moved, app), 1.3 * wanted @ q.T + np.array([0.1, -0.2, 0.3]))


def test_a_target_reaches_the_appended_vertices():
    rng = np.random.default_rng(3)
    old, app, wanted = _setup(rng)
    index = np.array([0, 1, 2, 30])
    delta = rng.normal(size=(4, 3)) * 0.01
    idx, d = makehuman.extend_offsets(index, delta, old, app)
    assert list(idx[:4]) == [0, 1, 2, 30] and np.allclose(d[:4], delta)
    # appended vertex 0 (born on vertices 0, 1, 2) moves; 1 and 2 (their faces untouched) are left out
    assert list(idx[4:]) == [len(old)]
    moved = old.copy()
    moved[index] += delta
    assert np.allclose(d[4], makehuman.place_appended(moved, app)[0] - wanted[0])


def test_an_untouched_target_adds_nothing():
    old, app, _ = _setup(np.random.default_rng(4))
    idx, d = makehuman.extend_offsets(np.array([20]), np.array([[0.0, 0.01, 0.0]]), old, app)
    assert list(idx) == [20]
