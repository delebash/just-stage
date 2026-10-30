# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""MHCLO: the documented reading rules, a write/read round trip, and binding then fitting reproducing the asset."""

import numpy as np
import pytest
from juststage.core import mhclo

DOC_EXAMPLE = """# MHCLO asset for MakeHuman and MPFB
# author: John Doe
# license: CC0
basemesh hm08
name shirt
uuid 59985471-ab08-479f-a32d-2d88411714ef
obj_file shirt.obj
material shirt.mhmat
tag casual
tag shirt
x_scale 5399 11998 1.4340
y_scale 791 881 2.4098
z_scale 962 5320 2.0001
z_depth 50
max_pole 4
verts 0
1234
5678 5679 5680 0.5000 0.3000 0.2000 0.0100 -0.0050 0.0020
delete_verts
 100 - 150 200 - 250
"""


def test_the_documented_example():
    m = mhclo.parse(DOC_EXAMPLE)
    assert (m.name, m.obj_file, m.material, m.z_depth) == ("shirt", "shirt.obj", "shirt.mhmat", 50)
    assert m.author == "John Doe"  # the whole name, not the documented one-word defect
    assert m.x_scale == (5399, 11998, 1.4340)
    assert m.refs.tolist() == [[1234, 1234, 1234], [5678, 5679, 5680]]
    assert m.weights[1].tolist() == [0.5, 0.3, 0.2]
    assert m.offsets[1].tolist() == pytest.approx([0.01, -0.005, 0.002])
    # the docs: a delete_verts line right after the last vertex line "is swallowed as the terminator of the vertex
    # block and the delete section never starts" — and their example is written that way
    assert m.delete_verts == []


WITH_BLANK = DOC_EXAMPLE.replace("0.0020\ndelete_verts", "0.0020\n\ndelete_verts")


def test_delete_verts_after_a_blank_line():
    assert mhclo.parse(WITH_BLANK).delete_verts == list(range(100, 151)) + list(range(200, 251))


def test_round_trip():
    m = mhclo.parse(WITH_BLANK)
    again = mhclo.parse(mhclo.write(m))
    assert again.refs.tolist() == m.refs.tolist()
    assert np.allclose(again.offsets, m.offsets, atol=1e-4)
    assert again.delete_verts == m.delete_verts


def test_bind_then_fit_gives_the_asset_back_and_follows_the_base():
    rng = np.random.default_rng(0)
    base = rng.uniform(-1, 1, (60, 3))
    triangles = np.array([[i, i + 1, i + 2] for i in range(0, 57, 3)])
    asset = base[triangles[:, 0]] * 0.6 + base[triangles[:, 1]] * 0.4 + np.array([0.0, 0.01, 0.02])

    def closest(points):  # the plane-projected foot point on each asset vertex's own triangle, for the test
        tri = np.arange(len(points))
        a, b, c = (base[triangles[tri, i]] for i in range(3))
        n = np.cross(b - a, c - a)
        n /= np.linalg.norm(n, axis=1, keepdims=True)
        foot = points - ((points - a) * n).sum(1, keepdims=True) * n
        return foot, tri

    scales = (
        (0, 1, abs(base[0, 0] - base[1, 0])),
        (2, 3, abs(base[2, 2] - base[3, 2])),
        (4, 5, abs(base[4, 1] - base[5, 1])),
    )
    m = mhclo.bind(asset, base, triangles, scales, closest)
    assert np.allclose(mhclo.fit(m, base), asset, atol=1e-9)
    moved = base + np.array([0.3, -0.2, 0.1])  # a translated base carries the asset along unchanged in shape
    assert np.allclose(mhclo.fit(m, moved), asset + np.array([0.3, -0.2, 0.1]), atol=1e-9)
