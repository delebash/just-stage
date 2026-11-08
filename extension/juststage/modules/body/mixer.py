# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The mixer (the approved design `docs/plans/2026-11-05-character-design.md` §5; the job's doc
`docs/plans/2026-11-08-mixer.md`): per region of CC5's part list, a weighted blend of whole identities - "a library of
identities ...; soft, overlapping region masks (CC5's part list); per region up to N identities with weights (CC5's
wheel), a features / proportions mode and a strength (MetaHuman's); ordinary sliders stay outside the mix (CC5's
rule)". NOT STANDARD, approved by name 2026-11-05; the patents' claims read for it (RESEARCH §14.3, not legal advice:
no per-region linear models solved together, no demographic predictions in the mix).

Each region's mask is a vertex group (`data/generated/mixer/regions.npz`, `tools/make_region_masks.py`). An identity's
offsets (MakeHuman target form, `data/generated/mixer/identities/`, `tools/make_identities.py`) split per region into
MetaHuman's two layers (its Blend Type, read in its source - RESEARCH §14.6): **proportions**, the region's place, turn
and size - a similarity (shift, small turn, uniform scale) fitted to the offsets over the mask by weighted least
squares, one a side for a region off the midline (eyes, ears, arms, legs) - and **features**, the rest (the offsets
minus the proportions). The two sum to the identity's offsets exactly, so "both" is the plain blend; mixing one
identity's features with another's proportions is linear (the features are not turned by the other's turn: about
0.4 mm at the measured turns, the job's doc).

The mix is slider values in the `scans` space (character-data-model.md §1.3: "a character stores only its slider
values"; morphs named `<space>.<name>`): slider and key `scans.<identity>.<region>.<part>`, each key limited to the
region's mask by its own vertex group (Blender's standard carrier), its value the identity's weight (the wheel's,
summing to 1) times the region's strength - so the `.blend` and the package carry a mix as they carry every slider,
and a character rebuilt from its slider values gets it back. The masks sum to 1, so one identity at 1 in every region
and both parts is that identity."""

from __future__ import annotations

from functools import cache

import bpy
import numpy as np

GROUP = "JustStage region {}"
SPACE = "scans"
PARTS = ("features", "proportions")  # MetaHuman's two layers; with "both" they are body_set_mix.MODES
#: a region whose mask puts less than this share of its weight within MIDLINE_M of the midline is two-sided: its
#: proportions are fitted a side at a time (MetaHuman's patches are a side each; measured 2026-11-08: eyes 0.0005,
#: ears 0, arms 0, legs 0.007 against forehead 0.21, nose 0.21, mouth 0.18, chin 0.11, torso 0.09, head shape 0.07)
SIDED_SHARE = 0.01
MIDLINE_M = 0.005
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


def _weights(character: bpy.types.Object, region: str) -> np.ndarray:
    """The region's mask on the character's vertices: hm08's weights, base v2's appended vertices their nearest body
    vertex's."""
    from ...core import makehuman
    from . import build

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
    return weights


def _mask(character: bpy.types.Object, region: str) -> bpy.types.VertexGroup:
    """The region's vertex group on the character (made once from `_weights`)."""
    name = GROUP.format(region)
    vg = character.vertex_groups.get(name)
    if vg is not None:
        return vg
    weights = _weights(character, region)
    vg = character.vertex_groups.new(name=name)
    hit = np.flatnonzero(weights > 1e-4)
    for w in np.unique(np.round(weights[hit], 4)):
        vg.add(hit[np.round(weights[hit], 4) == w].tolist(), float(w), "REPLACE")
    return vg


def _mask_weights(character: bpy.types.Object, region: str) -> np.ndarray:
    """The region's vertex group as the key draws it (its stored, rounded weights)."""
    vg = _mask(character, region)
    out = np.zeros(len(character.data.vertices))
    for v in character.data.vertices:
        for g in v.groups:
            if g.group == vg.index:
                out[v.index] = g.weight
    return out


def similarity(co: np.ndarray, offsets: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """The similarity (shift t, small turn w, uniform scale s - linearised: t + s (p - c) + w x (p - c), c the weighted
    centre) that best fits `offsets` at `co` by weighted least squares, evaluated at every point of `co`. Its residual
    is orthogonal to it: fitted again to `offsets` minus it, the fit is zero."""
    keep = weights > 0.0
    c = (weights[keep, None] * co[keep]).sum(0) / weights[keep].sum()
    r = co - c
    basis = np.zeros((len(co), 3, 7))
    basis[:, :, :3] = np.eye(3)
    basis[:, :, 3] = r
    basis[:, 0, 5], basis[:, 0, 6] = r[:, 2], -r[:, 1]  # w x r, the turn's three columns
    basis[:, 1, 4], basis[:, 1, 6] = -r[:, 2], r[:, 0]
    basis[:, 2, 4], basis[:, 2, 5] = r[:, 1], -r[:, 0]
    root = np.sqrt(weights[keep])[:, None, None]
    x, *_ = np.linalg.lstsq((basis[keep] * root).reshape(-1, 7), (offsets[keep] * root[:, :, 0]).ravel(), rcond=None)
    return basis @ x


def sides(co: np.ndarray, weights: np.ndarray) -> list[np.ndarray]:
    """The mask once, or a side at a time for a region off the midline (SIDED_SHARE)."""
    near = weights[np.abs(co[:, 0]) < MIDLINE_M].sum()
    if near >= SIDED_SHARE * weights.sum():
        return [weights]
    return [weights * (co[:, 0] > 0.0), weights * (co[:, 0] < 0.0)]


def split(character: bpy.types.Object, identity: str, region: str) -> dict[str, np.ndarray]:
    """The identity's offsets on the character's vertices, split in the region into its proportions and features."""
    from . import base

    n = len(character.data.vertices)
    basis = np.empty(n * 3, np.float32)
    character.data.shape_keys.reference_key.data.foreach_get("co", basis)
    co = basis.reshape(-1, 3).astype(np.float64)
    offsets = np.zeros((n, 3))
    index, delta = base.extend(character, *_identity(identity))
    offsets[index] = delta
    proportions = np.zeros((n, 3))
    for weights in sides(co, _mask_weights(character, region)):
        if weights.sum() > 0.0:
            proportions += (weights > 0.0)[:, None] * similarity(co, offsets, weights)
    return {"proportions": proportions, "features": offsets - proportions}


def slider_id(identity: str, region: str, part: str) -> str:
    """The slider (and its key) of one part of one identity in one region."""
    return f"{SPACE}.{identity}.{region}.{part}"


def parse(slider: str) -> tuple[str, str, str] | None:
    """A mixer slider id's (identity, region, part), or None when it is not one."""
    space, _, rest = slider.partition(".")
    if space != SPACE or rest.count(".") < 2:
        return None
    identity, region, part = rest.rsplit(".", 2)
    if part not in PARTS or region not in _regions() or identity not in identities():
        return None
    return identity, region, part


def _key(character: bpy.types.Object, identity: str, region: str, part: str) -> bpy.types.ShapeKey:
    """The part's key (made once, its sibling with it): the part's offsets, limited to the region's mask."""
    if not character.data.shape_keys:
        character.shape_key_add(name="Basis", from_mix=False)
    keys = character.data.shape_keys
    key = keys.key_blocks.get(slider_id(identity, region, part))
    if key is not None:
        return key
    basis = np.empty(len(character.data.vertices) * 3, np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    for name, offsets in split(character, identity, region).items():
        made = keys.key_blocks.get(slider_id(identity, region, name))
        if made is None:
            made = character.shape_key_add(name=slider_id(identity, region, name), from_mix=False)
            made.data.foreach_set("co", (basis.reshape(-1, 3) + offsets).astype(np.float32).ravel())
            made.vertex_group = _mask(character, region).name
            made.slider_min, made.slider_max = 0.0, 1.0
            made.value = 0.0
    return keys.key_blocks[slider_id(identity, region, part)]


def set_value(character: bpy.types.Object, identity: str, region: str, part: str, value: float) -> None:
    """One mixer slider: its key at `value` and the character's slider record (the `.blend`'s and the package's), as
    `juststage.body.set_slider` keeps every slider. No refit - the command does that once."""
    from ... import character as characters

    name = slider_id(identity, region, part)
    keys = character.data.shape_keys
    if value > 0.0 or (keys and name in keys.key_blocks):
        _key(character, identity, region, part).value = value
    item = next((s for s in character.juststage.sliders if s.id == name), None)
    if item is None:
        if value == 0.0:
            return
        item = character.juststage.sliders.add()
        item.id, item.label, item.group = name, f"{identity} ({region}, {part})", f"mixer/{region}"
    characters.APPLYING["macros"] = True  # its update callback stays quiet
    try:
        item.value = value
    finally:
        characters.APPLYING["macros"] = False


def region_mix(character: bpy.types.Object, region: str, part: str) -> dict[str, float]:
    """The region's identities above 0 in one part and their values (weight x strength), from the character's
    sliders."""
    found = {}
    for item in character.juststage.sliders:
        mixed = parse(item.id) if item.id.startswith(SPACE + ".") else None
        if mixed and mixed[1:] == (region, part) and item.value > 0.0:
            found[mixed[0]] = item.value
    return found
