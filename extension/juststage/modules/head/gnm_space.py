# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""GNM's head shape space on hm08 (character-data-model.md §1.2): 170 identity directions as MakeHuman targets,
made offline by `libs/wrap/gnm_to_hm08.py`. A head's identity is 170 coefficients (standard deviations); the
character carries one combined shape key for it, rebuilt when the coefficients change.
"""

from __future__ import annotations

import functools

import bpy
import numpy as np

from ... import paths
from ...core import makehuman

TOOL = ".dev/venv-tools/Scripts/python libs/wrap/gnm_to_hm08.py"
SHAPE_KEY = "gnm.identity"


@functools.cache
def directions() -> tuple[np.ndarray, np.ndarray]:
    """(vertex indices, directions[component, vertex, xyz] in Blender metres), loaded once."""
    folder = paths.generated("gnm", tool=TOOL)
    files = sorted(folder.glob("head_*.target.gz"))
    if not files:
        raise FileNotFoundError(f"no GNM targets in {folder}; run {TOOL}")
    rows = [makehuman.read_target(f) for f in files]
    index = np.array(sorted({r[0] for target in rows for r in target}), dtype=np.int64)
    where = {v: i for i, v in enumerate(index)}
    basis = np.zeros((len(files), len(index), 3), dtype=np.float32)
    for c, target in enumerate(rows):
        for v, dx, dy, dz in target:
            basis[c, where[v]] = (dx, dy, dz)
    return index, basis * makehuman.SCALE_TO_METRES


def components() -> int:
    return directions()[1].shape[0]


def set_identity(obj: bpy.types.Object, coefficients: np.ndarray) -> float:
    """Put a GNM identity on the character's head; returns the largest vertex offset in millimetres."""
    index, basis = directions()
    offset = np.tensordot(coefficients.astype(np.float32), basis, axes=1)  # (vertices, 3)
    keys = obj.data.shape_keys
    co = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    keys.reference_key.data.foreach_get("co", co)
    co = co.reshape(-1, 3)
    co[index] += offset
    key = keys.key_blocks.get(SHAPE_KEY) or obj.shape_key_add(name=SHAPE_KEY, from_mix=False)
    key.data.foreach_set("co", co.ravel())
    key.value = 1.0
    obj.juststage.gnm_identity.clear()
    for value in coefficients:
        obj.juststage.gnm_identity.add().value = float(value)
    return float(np.linalg.norm(offset, axis=1).max() * 1000.0)
