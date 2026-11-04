# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body's detail sliders from MakeHuman's `targets/target.json` (character-data-model.md §1.3: slider definitions
are app data; 23 groups, 234 categories with `has_left_and_right` and `opposites`). A slider's id is
`<group>/<category>` - `<group>/l-<category>` and `r-` for a category with left and right; its value runs -1..1 (the
negative target below 0, the positive above) or 0..1 for a category with one target. Each target is a relative shape
key `makehuman.<target>` (§1.3's `<space>.<name>`), made the first time it is used."""

from __future__ import annotations

import functools
import json
from typing import NamedTuple

import bpy
import numpy as np

from ... import paths
from ...core import makehuman

PREFIX = "makehuman."


class Slider(NamedTuple):
    id: str
    group: str
    label: str
    negative: str  # target name, "" for a one-way slider
    positive: str
    low: float  # -1.0, or 0.0 for a one-way slider


@functools.cache
def catalog() -> dict[str, Slider]:
    data = json.loads(paths.makehuman("targets", "target.json").read_text(encoding="utf-8"))
    found = {}
    for group, spec in data.items():
        for cat in spec["categories"]:
            name, label = cat["name"], cat.get("label", cat["name"])
            opp = cat.get("opposites")
            if not opp:  # one target, 0..1
                found[f"{group}/{name}"] = Slider(f"{group}/{name}", group, label, "", cat["targets"][0], 0.0)
            elif cat.get("has_left_and_right"):
                for side, key in (("l", "left"), ("r", "right")):
                    sid = f"{group}/{side}-{name}"
                    neg, pos = opp[f"negative-{key}"], opp[f"positive-{key}"]
                    found[sid] = Slider(sid, group, f"{label} ({key})", neg, pos, -1.0)
            else:
                sid = f"{group}/{name}"
                found[sid] = Slider(sid, group, label, opp["negative-unsided"], opp["positive-unsided"], -1.0)
    return found


def groups() -> list[str]:
    return sorted({s.group for s in catalog().values()})


@functools.cache
def _target(group: str, target: str) -> tuple[np.ndarray, np.ndarray]:
    rows = makehuman.read_target(paths.makehuman("targets", group, f"{target}.target.gz"))
    index = np.fromiter((r[0] for r in rows), dtype=np.int64, count=len(rows))
    delta = np.array([r[1:] for r in rows], dtype=np.float32).reshape(-1, 3) * makehuman.SCALE_TO_METRES
    return index, delta


def _key(obj: bpy.types.Object, group: str, target: str) -> bpy.types.ShapeKey:
    keys = obj.data.shape_keys
    key = keys.key_blocks.get(PREFIX + target)
    if key is None:
        basis = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
        keys.reference_key.data.foreach_get("co", basis)
        basis = basis.reshape(-1, 3)
        index, delta = _target(group, target)
        basis[index] += delta
        key = obj.shape_key_add(name=PREFIX + target, from_mix=False)
        key.data.foreach_set("co", basis.ravel())
        key.slider_min, key.slider_max = 0.0, 1.0
    return key


def apply(obj: bpy.types.Object, slider: Slider, value: float) -> None:
    """The slider's targets weighted by `value`: the negative one by -value below 0, the positive by value above. A
    target at 0 gets no shape key until it is used (a new character would otherwise carry 400-odd empty keys)."""
    for target, weight in ((slider.negative, max(0.0, -value)), (slider.positive, max(0.0, value))):
        if not target:
            continue
        key = obj.data.shape_keys.key_blocks.get(PREFIX + target)
        if key is None and weight == 0.0:
            continue
        (key or _key(obj, slider.group, target)).value = weight


def add_items(obj: bpy.types.Object) -> None:
    """Every detail slider on the character at 0 (data only, no shape keys) - what the Body panel draws."""
    have = {s.id for s in obj.juststage.sliders}
    for slider in catalog().values():
        if slider.id not in have:
            item = obj.juststage.sliders.add()
            item.id, item.label, item.group = slider.id, slider.label, slider.group
