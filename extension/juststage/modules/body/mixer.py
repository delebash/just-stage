# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer (the approved design `docs/plans/2026-11-05-character-design.md` §5; the job's doc
`docs/plans/2026-11-08-mixer.md`): per region of CC5's part list, a weighted blend of whole identities - "a library of
identities ...; soft, overlapping region masks (CC5's part list); per region up to N identities with weights (CC5's
wheel) ... and a strength (MetaHuman's); ordinary sliders stay outside the mix (CC5's rule)". NOT STANDARD, approved
by name 2026-11-05; the patents' claims read for it (RESEARCH §14.3, not legal advice: no global constrained solve,
no demographic predictions in the mix). Each region's mask is a vertex group (`data/generated/mixer/regions.npz`,
`tools/make_region_masks.py`); each identity in it a shape key of its own - its offsets (MakeHuman target form,
`data/generated/mixer/identities/`, `tools/make_identities.py`) limited to the mask by the key's own vertex group
(Blender's standard carrier). The mix is slider values in the `scans` space (character-data-model.md §1.3: "a
character stores only its slider values"; morphs named `<space>.<name>`): slider and key `scans.<identity>.<region>`,
its value the identity's weight (the wheel's, summing to 1) times the region's strength - so the `.blend` and the
package carry a mix as they carry every slider, and a character rebuilt from its slider values gets it back. The masks
sum to 1, so one identity at 1 in every region is that identity."""

from __future__ import annotations

from functools import cache

import bpy
import numpy as np

GROUP = "JustStage region {}"
SPACE = "scans"
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


def slider_id(identity: str, region: str) -> str:
    """The slider (and its key) of one identity in one region."""
    return f"{SPACE}.{identity}.{region}"


def parse(slider: str) -> tuple[str, str] | None:
    """A mixer slider id's (identity, region), or None when it is not one."""
    space, _, rest = slider.partition(".")
    identity, _, region = rest.rpartition(".")
    if space != SPACE or region not in _regions() or identity not in identities():
        return None
    return identity, region


def _key(character: bpy.types.Object, identity: str, region: str) -> bpy.types.ShapeKey:
    """The identity's key in the region (made once): its offsets, limited to the region's mask."""
    from . import base

    if not character.data.shape_keys:
        character.shape_key_add(name="Basis", from_mix=False)
    keys = character.data.shape_keys
    name = slider_id(identity, region)
    key = keys.key_blocks.get(name)
    if key is not None:
        return key
    basis = np.empty(len(character.data.vertices) * 3, np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    co = basis.reshape(-1, 3).astype(np.float64)
    index, delta = base.extend(character, *_identity(identity))
    co[index] += delta
    key = character.shape_key_add(name=name, from_mix=False)
    key.data.foreach_set("co", co.astype(np.float32).ravel())
    key.vertex_group = _mask(character, region).name
    key.slider_min, key.slider_max = 0.0, 1.0
    return key


def set_value(character: bpy.types.Object, identity: str, region: str, value: float) -> None:
    """One mixer slider: its key at `value` and the character's slider record (the `.blend`'s and the package's), as
    `juststage.body.set_slider` keeps every slider. No refit - the command does that once."""
    from ... import character as characters

    name = slider_id(identity, region)
    keys = character.data.shape_keys
    if value > 0.0 or (keys and name in keys.key_blocks):
        _key(character, identity, region).value = value
    item = next((s for s in character.juststage.sliders if s.id == name), None)
    if item is None:
        if value == 0.0:
            return
        item = character.juststage.sliders.add()
        item.id, item.label, item.group = name, f"{identity} ({region})", f"mixer/{region}"
    characters.APPLYING["macros"] = True  # its update callback stays quiet
    try:
        item.value = value
    finally:
        characters.APPLYING["macros"] = False


def region_mix(character: bpy.types.Object, region: str) -> dict[str, float]:
    """The region's identities above 0 and their values (weight x strength), read from the character's sliders."""
    found = {}
    for item in character.juststage.sliders:
        mixed = parse(item.id) if item.id.startswith(SPACE + ".") else None
        if mixed and mixed[1] == region and item.value > 0.0:
            found[mixed[0]] = item.value
    return found
