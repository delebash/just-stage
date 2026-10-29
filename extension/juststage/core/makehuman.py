# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-FileCopyrightText: MakeHuman Community (MPFB2's TargetService, the macro stack below)
# SPDX-License-Identifier: GPL-3.0-or-later

"""MakeHuman's own formats for the hm08 base (the spec's item 3), Blender-free.

- `vertex_groups`: MPFB2's `mesh_metadata/basemesh_vertex_groups.json` — group name → inclusive index ranges.
- `read_target`: a `.target` / `.target.gz` file — "index dx dy dz" lines in MakeHuman's Y-up space, turned into
  Blender's Z-up the way MPFB2 does (x, −z, y).
- `macro_components` and `macro_target_stack`: MakeHuman's macro blending — how the gender, age, muscle, weight,
  proportions, height, cup-size and firmness values pick and weight the `macrodetails` targets. The rules are in
  MPFB2's `macro.json` (the parts) and in code (the combinations — its docs: "The same five combinations are hardcoded
  in `TargetService.calculate_target_stack_from_macro_info_dict()`"); this is a port of that function, so a JustStage
  body matches an MPFB2 body with the same values.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

#: MakeHuman's base is in decimetres; MPFB2's "METER" scale.
SCALE_TO_METRES = 0.1

MACROS = ("gender", "age", "muscle", "weight", "proportions", "height", "cupsize", "firmness")
RACES = ("asian", "caucasian", "african")


#: MPFB2's `_SHAPEKEY_ENCODING`: Blender caps a shape key's name at 63 bytes and MakeHuman's names run longer, so
#: MPFB2 shortens them this way, in this order ("female" before "male"); JustStage uses the same names.
SHAPEKEY_ENCODING = (
    ("macrodetail", "$md"),
    ("female", "$fe"),
    ("male", "$ma"),
    ("caucasian", "$ca"),
    ("asian", "$as"),
    ("african", "$af"),
    ("average", "$av"),
    ("weight", "$wg"),
    ("height", "$hg"),
    ("muscle", "$mu"),
    ("proportions", "$pr"),
    ("firmness", "$fi"),
    ("ideal", "$id"),
    ("uncommon", "$un"),
    ("young", "$yn"),
    ("child", "$ch"),
)
#: Blender's limit for a shape key's name (MAX_NAME − 1).
MAX_NAME = 63


def encode_name(name: str) -> str:
    for long, short in SHAPEKEY_ENCODING:
        name = name.replace(long, short)
    return name


def target_shapekey_name(target: str) -> str:
    """MPFB2's `filename_to_shapekey_name` for a target path under `targets/` (without `.target.gz`)."""
    base = target.rsplit("/", 1)[-1]
    if target.startswith("macrodetails/"):
        return encode_name("macrodetail-" + base)
    return encode_name(base) if len(base) > 60 else base


def default_macros() -> dict:
    """MPFB2's `get_default_macro_info_dict()`."""
    values = {name: 0.5 for name in MACROS}
    values["race"] = {"asian": 0.33, "caucasian": 0.33, "african": 0.33}
    return values


def vertex_groups(path: Path) -> dict[str, list[int]]:
    """Group name → sorted vertex indices, from MPFB2's inclusive ranges."""
    ranges = json.loads(Path(path).read_text(encoding="utf-8"))
    return {name: [i for a, b in spans for i in range(a, b + 1)] for name, spans in ranges.items()}


def read_target(path: Path) -> list[tuple[int, float, float, float]]:
    """A target's (index, dx, dy, dz) rows in Blender's axes, MakeHuman's units (decimetres)."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        rows = []
        for line in f:
            line = line.strip()
            if not line or line[0] in '#"':
                continue
            parts = line.split()
            rows.append((int(parts[0]), float(parts[1]), -float(parts[3]), float(parts[2])))
    return rows


def macro_components(macro_config: dict, name: str, value: float) -> list[tuple[str, float]]:
    """MPFB2's `_interpolate_macro_components`: the (target part, weight) pairs one macro value selects."""
    components = []
    for part in macro_config["macrotargets"][name]["parts"]:
        lowest, highest = part["lowest"], part["highest"]
        if lowest < value < highest:  # both bounds exclusive, as MPFB2 reads them
            position_pct = (value - lowest) / (highest - lowest)
            if part["low"]:
                components.append((part["low"], round(1 - position_pct, 4)))
            if part["high"]:
                components.append((part["high"], round(position_pct, 4)))
    return components


def macro_target_stack(macro_config: dict, values: dict | None = None, cutoff: float = 0.01) -> list[tuple[str, float]]:
    """MPFB2's `calculate_target_stack_from_macro_info_dict`: the macro targets and weights for a set of values."""
    values = values or default_macros()
    c = {name: macro_components(macro_config, name, values[name]) for name in MACROS}
    targets: list[tuple[str, float]] = []

    for race, race_weight in values["race"].items():
        if race_weight > 0.0001:
            for age, aw in c["age"]:
                for gender, gw in c["gender"]:
                    if gender != "universal":
                        weight = race_weight * gw * aw
                        if weight > cutoff:
                            targets.append((f"macrodetails/{race}-{gender}-{age}", weight))

    for gender, gw in c["gender"]:
        for age, aw in c["age"]:
            for muscle, mw in c["muscle"]:
                for wt, ww in c["weight"]:
                    weight = gw * aw * mw * ww
                    if weight > cutoff:
                        targets.append((f"macrodetails/universal-{gender}-{age}-{muscle}-{wt}", weight))

    for gender, gw in c["gender"]:
        for age, aw in c["age"]:
            for muscle, mw in c["muscle"]:
                for wt, ww in c["weight"]:
                    for height, hw in c["height"]:
                        weight = gw * aw * mw * ww * hw
                        if weight > cutoff:
                            targets.append((f"macrodetails/height/{gender}-{age}-{muscle}-{wt}-{height}", weight))

    for gender, _gw in c["gender"]:
        if gender != "female":  # there are no male complementary breast targets
            continue
        for age, aw in c["age"]:
            for muscle, mw in c["muscle"]:
                for wt, ww in c["weight"]:
                    for cup, cw in c["cupsize"]:
                        for firm, fw in c["firmness"]:
                            name = f"breast/{gender}-{age}-{muscle}-{wt}-{cup}-{firm}"
                            weight = aw * mw * ww * cw * fw
                            if weight > cutoff and not (
                                "averagecup-averagefirmness" in name or "_baby_" in name or "-baby-" in name
                            ):
                                targets.append((name, weight))

    for gender, gw in c["gender"]:
        for age, aw in c["age"]:
            for muscle, mw in c["muscle"]:
                for wt, ww in c["weight"]:
                    for proportions, pw in c["proportions"]:
                        name = f"macrodetails/proportions/{gender}-{age}-{muscle}-{wt}-{proportions}"
                        weight = gw * aw * mw * ww * pw
                        if weight > cutoff and not ("-baby-" in name or "_baby_" in name):
                            targets.append((name, weight))

    return targets
