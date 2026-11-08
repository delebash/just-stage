# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer (the approved design `docs/plans/2026-11-05-character-design.md` §5; the job's doc
`docs/plans/2026-11-08-mixer.md`): per region of CC5's part list, a weighted blend of whole identities - "a library of
identities ...; soft, overlapping region masks (CC5's part list); per region up to N identities with weights (CC5's
wheel) ... and a strength (MetaHuman's); ordinary sliders stay outside the mix (CC5's rule)". NOT STANDARD, approved
by name 2026-11-05; the patents' claims read for it (RESEARCH §14.3, not legal advice: no global constrained solve,
no demographic predictions in the mix). Each region's mask is a vertex group (`data/generated/mixer/regions.npz`,
`tools/make_region_masks.py`); its mix a shape key of its own - the identities' offsets (MakeHuman target form,
`data/generated/mixer/identities/`, `tools/make_identities.py`) weighted and summed - limited to the mask by the key's
own vertex group (Blender's standard carrier), its value the strength. The masks sum to 1, so one identity at strength
1 in every region is that identity."""

from __future__ import annotations

import json
from functools import cache

import bpy
import numpy as np

GROUP = "JustStage region {}"
KEY = "JustStage mix {}"
STORE = "JustStage mix"  # the character's mix: {region: {"identities": [...], "weights": [...], "strength": s}}
MASK_TOOL = ".dev/venv-tools/Scripts/python -I tools/make_region_masks.py"
IDENTITY_TOOL = ".dev/venv-tools/Scripts/python -I tools/make_identities.py"


@cache
def _regions() -> dict[str, np.ndarray]:
    from ... import paths

    data = np.load(paths.generated("mixer", "regions.npz", tool=MASK_TOOL))
    return {name: data[name] for name in data.files}


def regions() -> list[str]:
    return sorted(_regions())


def identities() -> list[str]:
    from ... import paths

    folder = paths.GENERATED / "mixer" / "identities"
    return sorted(p.stem for p in folder.glob("*.npz")) if folder.is_dir() else []


def _identity(name: str) -> tuple[np.ndarray, np.ndarray]:
    from ... import paths

    data = np.load(paths.generated("mixer", "identities", f"{name}.npz", tool=IDENTITY_TOOL))
    return data["index"].astype(np.int64), data["delta"].astype(np.float64)


def _mask(character: bpy.types.Object, region: str) -> bpy.types.VertexGroup:
    """The region's vertex group on the character: hm08's weights, base v2's appended vertices their nearest body
    vertex's."""
    from ...core import makehuman
    from . import build

    name = GROUP.format(region)
    vg = character.vertex_groups.get(name)
    if vg is not None:
        return vg
    weights = np.zeros(len(character.data.vertices))
    weights[: makehuman.HM08_VERTICES] = _regions()[region]
    if len(weights) > makehuman.HM08_VERTICES:
        from mathutils.kdtree import KDTree

        co = build.shaped_coords(character)
        kd = KDTree(makehuman.BODY_VERTICES)
        for i in range(makehuman.BODY_VERTICES):
            kd.insert(co[i], i)
        kd.balance()
        for i in range(makehuman.HM08_VERTICES, len(weights)):
            weights[i] = weights[kd.find(co[i])[1]]
    vg = character.vertex_groups.new(name=name)
    hit = np.flatnonzero(weights > 1e-4)
    for w in np.unique(np.round(weights[hit], 4)):
        vg.add(hit[np.round(weights[hit], 4) == w].tolist(), float(w), "REPLACE")
    return vg


def set_mix(character: bpy.types.Object, region: str, names: list[str], weights: list[float],
            strength: float = 1.0) -> bpy.types.ShapeKey:  # fmt: skip
    """The region's mix on the character (replacing its last): the identities' offsets weighted and summed, as a key
    limited to the region's mask, at `strength`; kept on the character (STORE)."""
    from . import base

    if region not in _regions():
        raise ValueError(f"no region {region!r}; the regions: {', '.join(regions())}")
    if len(names) != len(weights):
        raise ValueError("one weight an identity")
    if not character.data.shape_keys:
        character.shape_key_add(name="Basis", from_mix=False)
    keys = character.data.shape_keys
    n = len(character.data.vertices)
    basis = np.empty(n * 3, np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    co = basis.reshape(-1, 3).astype(np.float64)
    for name, weight in zip(names, weights, strict=True):
        index, delta = base.extend(character, *_identity(name))
        co[index] += weight * delta
    key = keys.key_blocks.get(KEY.format(region)) or character.shape_key_add(name=KEY.format(region), from_mix=False)
    key.data.foreach_set("co", co.astype(np.float32).ravel())
    key.vertex_group = _mask(character, region).name
    key.slider_min, key.slider_max = 0.0, 1.0
    key.value = strength
    mix = json.loads(character.get(STORE, "{}"))
    mix[region] = {"identities": list(names), "weights": [float(w) for w in weights], "strength": float(strength)}
    character[STORE] = json.dumps(mix)
    return key
