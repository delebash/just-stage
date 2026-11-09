# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The composer's edges (tools/face_test/skin_base.py): where the scans' coverage ends, the low colour layer fades to
the flat tone without a step. Run in the tool environment:

    .dev/venv-rdf/Scripts/python -m pytest tests/tools/test_skin_base.py
"""

import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location(
    "skin_base", Path(__file__).resolve().parents[2] / "tools" / "face_test" / "skin_base.py"
)
skin_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skin_base)


def test_the_low_layer_fades_out_where_the_scans_end_without_a_step():
    """623's colour stood 10-33% darker just inside its cover's edge and the cut left a jagged patch (2026-11-09)."""
    n = 2048  # half the head tile's 4096, its cover ~1200 texels across as the scans' (29% of the tile)
    inside = np.zeros((n, n), bool)
    yy, xx = np.mgrid[0:n, 0:n]
    r = np.hypot(yy - 900, xx - 1024)
    inside[r < 600] = True  # a cover with a curved edge
    rng = np.random.default_rng(1)
    layer = np.full((n, n, 3), -0.3, np.float32)  # 26% darker than the tone, as 623's chest
    layer += 0.02 * rng.standard_normal((n, n, 3)).astype(np.float32)  # and some detail
    layer[~inside] = 0.0  # nothing past the cover, as the composed layer (a first version kept half the drop there)
    out = skin_base.faded_out(layer, inside, skin_base.LOW_EDGE_BANDS)
    steps = np.abs(np.diff(out[..., 0], axis=1))
    edge = inside[:, 1:] != inside[:, :-1]
    within = (r[:, 1:] < 450) & ~edge  # the layer's own texel-to-texel change, well inside
    assert np.percentile(steps[edge], 90) <= np.percentile(steps[within], 90)  # no jump at the edge beyond it (0.3)
    deep = r < 250  # 350 texels (~6 cm) inside the edge: the face, far from where the scans end
    assert abs(np.median(out[deep, 0]) + 0.3) < 0.01  # the layer as it was
    far = r > 1000
    assert np.abs(out[far]).max() < 0.01  # well outside, the flat tone


def test_the_pores_colour_fades_in_from_where_the_scans_end():
    """The fine layer x `_feathered(inside)` (2026-11-09: at full strength to the cover's edge the pores' colour drew
    a jagged outline on the Heavy woman's chest): nothing at the edge, nearly all of it two FEATHERs in."""
    n = 1024
    inside = np.zeros((n, n), bool)
    inside[:, : n // 2] = True
    fade = skin_base._feathered(inside)[n // 2]
    edge = n // 2 - 1
    assert fade[edge] < 0.05
    assert fade[edge - int(2 * skin_base.FEATHER)] > 0.9
    assert np.all(np.diff(fade[: n // 2]) <= 1e-6)  # one smooth ramp down to the edge
