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
REACH_M = 1e-4  # an identity moves a vertex when it moves it by over this...
REACH_SHARE = 0.25  # ...and reaches a region when those vertices hold this share of its mask (measured 2026-11-08 on
#                     the filled identities: the head's parts 0.52-1.0, the torso 0.06 - the neck - and arms 0.004)
#: the helpers' key: MakeHuman's helpers (eyeballs, teeth, tongue, joint cubes, ...) carry the eyes, the teeth and the
#: skeleton, and the identities hold none, so each helper vertex moves by the mean of the mixed skin's offsets within
#: FOLLOW_M of it (the face test's rule for its eyeballs, tools/face_test/face_shape.py), or within FOLLOW_REACH times
#: its distance to the skin when that is further (a joint deep in the neck); an island of helpers no wider than
#: RIGID_M (an eyeball, the teeth, a joint cube) moves as one, by its vertices' mean - its shape kept
HELPERS_KEY = "JustStage mix helpers"
FOLLOW_M = 0.020
FOLLOW_REACH = 1.5
FOLLOW_MAX = 200  # a wide neighbourhood thinned evenly to this many skin vertices (its mean kept, the cost bounded)
RIGID_M = 0.030
_FOLLOW: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}  # vertex count -> (rows, cols, weights)
MASK_TOOL = ".dev/venv-tools/Scripts/python -I tools/make_region_masks.py"
IDENTITY_TOOL = ".dev/venv-tools/Scripts/python -I tools/make_identities.py"


@cache
def _regions() -> dict[str, np.ndarray]:
    from ... import paths

    data = np.load(paths.generated("mixer", "regions.npz", tool=MASK_TOOL))
    return {name: data[name] for name in data.files}


def regions() -> list[str]:
    return sorted(_regions())


@cache
def identities() -> tuple[str, ...]:
    """The identity library's names (generated data: fixed for a session - read once)."""
    from ... import paths

    folder = paths.GENERATED / "mixer" / "identities"
    return tuple(sorted(p.stem for p in folder.glob("*.npz"))) if folder.is_dir() else ()


@cache
def reach() -> dict[str, tuple[str, ...]]:
    """Per region, the identities that move it - over REACH_M where its mask is over 0.01 (a head scan reaches no body
    part): the parts the mixer can change today."""
    found = {}
    data = {name: _identity(name) for name in identities()}
    for region, mask in _regions().items():
        found[region] = tuple(
            name
            for name, (index, delta) in data.items()
            if mask[index[np.linalg.norm(delta, axis=1) > REACH_M]].sum() >= REACH_SHARE * mask.sum()
        )
    return found


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
    """The identity's offsets on the character's vertices, split in the region into its proportions and features - on
    the skin alone (the helpers follow the mixed skin: `follow`)."""
    from ...core import makehuman
    from . import base

    n = len(character.data.vertices)
    basis = np.empty(n * 3, np.float32)
    character.data.shape_keys.reference_key.data.foreach_get("co", basis)
    co = basis.reshape(-1, 3).astype(np.float64)
    offsets = np.zeros((n, 3))
    index, delta = base.extend(character, *_identity(identity))
    offsets[index] = delta
    proportions = np.zeros((n, 3))
    mask = _mask_weights(character, region)
    mask[makehuman.BODY_VERTICES : makehuman.HM08_VERTICES] = 0.0  # no helper in the fit, none moved by it
    for weights in sides(co, mask):
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
    """The part's key (made once): the part's offsets, limited to the region's mask."""
    if not character.data.shape_keys:
        character.shape_key_add(name="Basis", from_mix=False)
    keys = character.data.shape_keys
    name = slider_id(identity, region, part)
    key = keys.key_blocks.get(name)
    if key is not None:
        return key
    basis = np.empty(len(character.data.vertices) * 3, np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    offsets = split(character, identity, region)[part]
    key = character.shape_key_add(name=name, from_mix=False)
    key.data.foreach_set("co", (basis.reshape(-1, 3) + offsets).astype(np.float32).ravel())
    key.vertex_group = _mask(character, region).name
    key.slider_min, key.slider_max = 0.0, 1.0
    return key


def set_value(character: bpy.types.Object, identity: str, region: str, part: str, value: float) -> None:
    """One mixer slider: its key at `value` and the character's slider record (the `.blend`'s and the package's), as
    `juststage.body.set_slider` keeps every slider; at 0 both go (keys only for the identities in use - the 11-05
    research's answer to "hundreds of keys (identities x regions)"). No refit - the command does that once."""
    from ... import character as characters

    name = slider_id(identity, region, part)
    keys = character.data.shape_keys
    index = next((i for i, s in enumerate(character.juststage.sliders) if s.id == name), None)
    if value == 0.0:
        if keys and name in keys.key_blocks:
            character.shape_key_remove(keys.key_blocks[name])
        if index is not None:
            character.juststage.sliders.remove(index)
        return
    _key(character, identity, region, part).value = value
    item = character.juststage.sliders[index] if index is not None else None
    if item is None:
        item = character.juststage.sliders.add()
        item.id, item.label, item.group = name, f"{identity} ({region}, {part})", f"mixer/{region}"
    characters.APPLYING["macros"] = True  # its update callback stays quiet
    try:
        item.value = value
    finally:
        characters.APPLYING["macros"] = False


def _follow_weights(character: bpy.types.Object) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Which skin vertices each helper vertex follows, and how much (rows: helper vertices, cols: skin vertices) - on
    the basis, the same for every character of a base version: made once a session."""
    n = len(character.data.vertices)
    if n in _FOLLOW:
        return _FOLLOW[n]
    from mathutils.kdtree import KDTree

    from ...core import makehuman

    skin, end = makehuman.BODY_VERTICES, makehuman.HM08_VERTICES
    basis = np.empty(n * 3, np.float32)
    character.data.shape_keys.reference_key.data.foreach_get("co", basis)
    co = basis.reshape(-1, 3).astype(np.float64)
    kd = KDTree(skin)
    for i in range(skin):
        kd.insert(co[i], i)
    kd.balance()

    def near(point: np.ndarray) -> list[int]:  # the skin around a point, thinned evenly to FOLLOW_MAX
        hits = [i for _co, i, _d in kd.find_range(point, max(FOLLOW_M, FOLLOW_REACH * kd.find(point)[2]))]
        return hits[:: max(1, len(hits) // FOLLOW_MAX)]

    # the helpers' islands (their own edges), each no wider than RIGID_M moved as one
    edges = np.empty(len(character.data.edges) * 2, np.int64)
    character.data.edges.foreach_get("vertices", edges)
    parent = np.arange(end)

    def root(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a, b in edges.reshape(-1, 2):
        if skin <= a < end and skin <= b < end:
            parent[root(a)] = root(b)
    islands: dict[int, list[int]] = {}
    for h in range(skin, end):
        islands.setdefault(root(h), []).append(h)
    rows, cols, weights = [], [], []
    for members in islands.values():
        pts = co[members]
        centre = pts.mean(0)
        shared = near(centre) if np.linalg.norm(pts - centre, axis=1).max() <= RIGID_M else None  # rigid: one row
        for h in members:
            hits = shared if shared is not None else near(co[h])
            rows += [h - skin] * len(hits)
            cols += hits
            weights += [1.0 / len(hits)] * len(hits)
    _FOLLOW[n] = (np.array(rows, np.int64), np.array(cols, np.int64), np.array(weights))
    return _FOLLOW[n]


def follow(character: bpy.types.Object) -> None:
    """The helpers' key on the character's current mix (HELPERS_KEY): each helper vertex moved by the mixed skin around
    it - the skin's offsets the mixer's keys give, as Blender draws them (its mix with them, less its mix without)."""
    from ...core import makehuman
    from . import build

    keys = character.data.shape_keys
    if not keys:
        return
    mixed = [k for k in keys.key_blocks if k.name.startswith(SPACE + ".") and k.value != 0.0 and not k.mute]
    key = keys.key_blocks.get(HELPERS_KEY)
    if not mixed and key is None:
        return
    skin, end = makehuman.BODY_VERTICES, makehuman.HM08_VERTICES
    with_mix = build.shaped_coords(character)[:skin]
    for k in mixed:
        k.mute = True
    try:
        offsets = with_mix - build.shaped_coords(character)[:skin]
    finally:
        for k in mixed:
            k.mute = False
    basis = np.empty(len(character.data.vertices) * 3, np.float32)
    keys.reference_key.data.foreach_get("co", basis)
    basis = basis.reshape(-1, 3)
    rows, cols, weights = _follow_weights(character)
    helpers = np.stack([np.bincount(rows, weights * offsets[cols, a], minlength=end - skin) for a in range(3)], 1)
    if key is None:
        key = character.shape_key_add(name=HELPERS_KEY, from_mix=False)
    out = basis.copy()
    out[skin:end] += helpers.astype(np.float32)
    key.data.foreach_set("co", out.ravel())
    key.value = 1.0


def region_mix(character: bpy.types.Object, region: str, part: str) -> dict[str, float]:
    """The region's identities above 0 in one part and their values (weight x strength), from the character's
    sliders."""
    found = {}
    for item in character.juststage.sliders:
        mixed = parse(item.id) if item.id.startswith(SPACE + ".") else None
        if mixed and mixed[1:] == (region, part) and item.value > 0.0:
            found[mixed[0]] = item.value
    return found
