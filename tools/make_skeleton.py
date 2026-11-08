# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body skeleton's definition and weights (`docs/standards/skeleton-and-face.md` §1.1: Epic's UE5 skeleton by
its own names - Manny's 80 deform bones - plus `breast_l/r`, 82; the plan's §7 "Skeleton" and "Weights"; the job's
doc `docs/plans/2026-11-08-skeleton.md`). Built on MPFB2's CC0 `game_engine_with_breast` rig and weights, whose 55
bones keep MPFB2's own joints, rolls and flags; the 27 bones UE5 adds are placed in MPFB2's own rig format (JSON
v110, its `MEAN` joint strategy: the plain mean of the listed vertices, repeats counted - MPFB2's
`entities/rig.py` `get_best_location_from_strategy` at the fetched commit), at the places measured on Manny
(RESEARCH §14.7, `docs/plans/2026-10-29-spec-evidence/ue5-manny-rest-pose.json`):

- twist bones at the limb's thirds (upper arm and thigh twist_01 at 1/3, _02 at 2/3; forearm and calf twist_01 at
  2/3, _02 at 1/3) - the mean of the two joint cubes' 8 vertices each, listed 2:1 or 1:2;
- `spine_04` / `spine_05` in the game-engine rig's empty joint-spine-1 -> joint-neck stretch, `spine_05` from 5/8 of it
  (Manny 0.62); `neck_02` from half way along neck -> head (Manny 0.51);
- the metacarpals at MPFB2's default rig's own joints and rolls.

Parents are Manny's (measured); `breast_*` stays as MPFB2 has it. Weights: the game-engine weights kept; each added
bone takes a share of its source bone's - the hand's by MPFB2's default weights' wrist : metacarpal shares, a chain's
(the limbs' twists, the upper spine, the neck) by the vertex's place along it, linear between the bones' heads (NOT
STANDARD detail, the job's doc §3); at most 8 influences a vertex (the data model §2); every vertex's weights summing
to 1 (MPFB2's breast weights sit on top of its plain ones).

    .dev/venv-tools/Scripts/python -I tools/make_skeleton.py

Writes `extension/juststage/data/generated/rigs/ue5.json` and `weights.ue5.json` (MPFB2's rig and weights formats),
from the files `python tools/fetch_data.py` fetches."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MAKEHUMAN = ROOT / "extension" / "juststage" / "data" / "fetched" / "makehuman"
RIGS = MAKEHUMAN / "rigs" / "standard"
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "rigs"
HM08_VERTICES = 19158  # core/makehuman.py
SCALE_TO_METRES = 0.1  # core/makehuman.py: MakeHuman's units are decimetres
MAX_INFLUENCES = 8  # character-data-model.md §2: "max 8 influences on the body"
FLOOR = 1e-5  # a share below this is left out, as MPFB2's files list only the vertices a bone moves
SIDES = {"l": "L", "r": "R"}  # ours (Epic's) -> MPFB2's default rig's

#: the limbs' twist bones: (source bone, (twist bone, its head's fraction along the limb) nearest the source's head
#: first) - Manny's, measured (forearm and calf twist_01 nearest the hand and foot)
TWISTS = {
    "upperarm": (("upperarm_twist_01", 1), ("upperarm_twist_02", 2)),
    "lowerarm": (("lowerarm_twist_02", 1), ("lowerarm_twist_01", 2)),
    "thigh": (("thigh_twist_01", 1), ("thigh_twist_02", 2)),
    "calf": (("calf_twist_02", 1), ("calf_twist_01", 2)),
}
SPINE_05_AT = (3, 5)  # spine_05's head: joint-spine-1 x3 and joint-neck x5 -> 5/8 of the way (Manny 0.6205)
NECK_02_AT = (1, 1)  # neck_02's head: half way along joint-neck -> joint-head (Manny 0.5098)
METACARPALS = ("index", "middle", "ring", "pinky")  # MPFB2's default metacarpal1-4, in this order
#: Manny's parents where they differ from the game-engine rig's (the rest of the 80 agree, or are added below)
PARENTS = {"pelvis": "root", "clavicle_l": "spine_05", "clavicle_r": "spine_05", "neck_01": "spine_05",
           "head": "neck_02"}  # fmt: skip


def _vertices(path: Path) -> np.ndarray:
    rows = [line.split()[1:4] for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("v ")]
    return np.array(rows, dtype=np.float64)


def _groups() -> dict[str, list[int]]:
    ranges = json.loads((MAKEHUMAN / "mesh_metadata" / "basemesh_vertex_groups.json").read_text(encoding="utf-8"))
    return {name: [i for a, b in spans for i in range(a, b + 1)] for name, spans in ranges.items()}


def _to_blender(p: np.ndarray) -> list[float]:
    """MakeHuman's OBJ axes (Y up, decimetres) -> MPFB2's `default_position` (Z up, metres)."""
    return [round(float(v), 6) for v in (p[0] * SCALE_TO_METRES, -p[2] * SCALE_TO_METRES, p[1] * SCALE_TO_METRES)]


class Joints:
    """Joint rules (MPFB2's) and where they sit on the base mesh."""

    def __init__(self, co: np.ndarray, groups: dict[str, list[int]]):
        self.co, self.groups = co, groups

    def at(self, spec: dict) -> np.ndarray:
        if spec["strategy"] == "CUBE":
            return self.co[self.groups[spec["cube_name"]]].mean(0)
        if spec["strategy"] in ("MEAN", "VERTEX"):
            return self.co[spec.get("vertex_indices", [spec.get("vertex_index")])].mean(0)
        raise ValueError(f"joint strategy {spec['strategy']} not handled")

    def cube(self, name: str) -> dict:
        return {"cube_name": name, "default_position": _to_blender(self.co[self.groups[name]].mean(0)),
                "strategy": "CUBE"}  # fmt: skip

    def between(self, a: str, b: str, na: int, nb: int) -> dict:
        """The mean of cube `a`'s vertices listed `na` times and cube `b`'s `nb` times: nb / (na + nb) of the way."""
        indices = self.groups[a] * na + self.groups[b] * nb
        if len(self.groups[a]) != len(self.groups[b]):
            raise ValueError(f"{a} and {b} differ in size - a repeated mean would not be {nb}/{na + nb} of the way")
        return {"default_position": _to_blender(self.co[indices].mean(0)), "strategy": "MEAN",
                "vertex_indices": indices}  # fmt: skip


def _bone(base: dict, head: dict, tail: dict, parent: str, roll: float) -> dict:
    return {"head": head, "inherit_scale": base.get("inherit_scale", "FULL"), "parent": parent, "rigify": {},
            "roll": roll, "tail": tail, "use_connect": False, "use_inherit_rotation": True,
            "use_local_location": True}  # fmt: skip


def definition(game: dict, default: dict, joints: Joints) -> dict:
    """The 82 bones in MPFB2's rig format, in the spec's table order."""
    bones = {}
    for name, spec in game.items():
        spec = json.loads(json.dumps(spec))
        name = "root" if name == "Root" else name
        if spec["parent"] == "Root":
            spec["parent"] = "root"
        spec["parent"] = PARENTS.get(name, spec["parent"])
        bones[name] = spec
    # the upper spine: the game-engine rig's spine_03 ends at joint-spine-1 and its neck_01 starts at joint-neck
    up = joints.between("joint-spine-1", "joint-neck", *SPINE_05_AT)
    bones["spine_04"] = _bone(bones["spine_03"], joints.cube("joint-spine-1"), up, "spine_03", 0.0)
    bones["spine_05"] = _bone(bones["spine_03"], up, joints.cube("joint-neck"), "spine_04", 0.0)
    mid = joints.between("joint-neck", "joint-head", *NECK_02_AT)
    neck = bones["neck_01"]
    bones["neck_02"] = _bone(neck, mid, neck["tail"], "neck_01", neck["roll"])
    neck["tail"] = mid
    for side, mpfb in SIDES.items():
        for limb, twists in TWISTS.items():
            src = bones[f"{limb}_{side}"]
            a, b = src["head"]["cube_name"], src["tail"]["cube_name"]
            ends = {0: joints.cube(a), 1: joints.between(a, b, 2, 1), 2: joints.between(a, b, 1, 2), 3: joints.cube(b)}
            for twist, third in twists:
                bones[f"{twist}_{side}"] = _bone(src, ends[third], ends[third + 1], f"{limb}_{side}", src["roll"])
        for k, finger in enumerate(METACARPALS, start=1):
            mc = default[f"metacarpal{k}.{mpfb}"]
            bones[f"{finger}_metacarpal_{side}"] = _bone(mc, mc["head"], mc["tail"], f"hand_{side}", mc["roll"])
            bones[f"{finger}_01_{side}"]["parent"] = f"{finger}_metacarpal_{side}"
    return {name: bones[name] for name in order()}


def order() -> list[str]:
    """The spec's §1.1 table: root and centre, then per side the arm, the hand, the leg, the breast."""
    names = ["root", "pelvis", *(f"spine_0{i}" for i in range(1, 6)), "neck_01", "neck_02", "head"]
    for side in SIDES:
        names += [f"{b}_{side}" for b in ("clavicle", "upperarm", "upperarm_twist_01", "upperarm_twist_02",
                                           "lowerarm", "lowerarm_twist_01", "lowerarm_twist_02", "hand")]  # fmt: skip
        names += [f"thumb_0{i}_{side}" for i in (1, 2, 3)]
        for finger in METACARPALS:
            names += [f"{finger}_metacarpal_{side}", *(f"{finger}_0{i}_{side}" for i in (1, 2, 3))]
        names += [f"{b}_{side}" for b in ("thigh", "thigh_twist_01", "thigh_twist_02", "calf", "calf_twist_01",
                                           "calf_twist_02", "foot", "ball")]  # fmt: skip
    return names + ["breast_l", "breast_r"]


def _table(weights: dict, names: list[str]) -> np.ndarray:
    table = np.zeros((HM08_VERTICES, len(names)))
    for j, name in enumerate(names):
        for i, w in weights.get(name, []):
            table[i, j] = w
    return table


def _along(co: np.ndarray, points: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Each vertex's place along a polyline (arc length to its nearest point) and the places of the polyline's
    points."""
    p = np.asarray(points)
    seg = p[1:] - p[:-1]
    length = np.linalg.norm(seg, axis=1)
    start = np.concatenate([[0.0], np.cumsum(length)])
    best = np.full(len(co), np.inf)
    place = np.zeros(len(co))
    for k in range(len(seg)):
        t = np.clip(((co - p[k]) @ seg[k]) / (length[k] ** 2), 0.0, 1.0)
        d = np.linalg.norm(p[k] + t[:, None] * seg[k] - co, axis=1)
        closer = d < best
        best[closer], place[closer] = d[closer], start[k] + t[closer] * length[k]
    return place, start


def _chain_shares(co: np.ndarray, heads: list[np.ndarray], end: np.ndarray) -> np.ndarray:
    """(vertices, bones): each vertex's share for the chain's bones - linear between the bones' heads, all the first's
    before it, all the last's past the last head."""
    place, at = _along(co, [*heads, end])
    nodes = at[: len(heads)]
    eye = np.eye(len(heads))
    return np.stack([np.interp(place, nodes, eye[j]) for j in range(len(heads))], axis=1)


def weights(rig: dict, game_weights: dict, default_weights: dict, joints: Joints) -> tuple[dict, dict]:
    """The 82 bones' weights (MPFB2's `{bone: [[vertex, weight], ...]}`) and a report."""
    names = list(rig)
    game_names = ["Root" if n == "root" else n for n in names]
    table = _table(game_weights, game_names)  # the game-engine weights; the added bones' columns start empty
    col = {n: j for j, n in enumerate(names)}
    co = joints.co
    total_before = table.sum(1)

    def split(source: str, bones: list[str], shares: np.ndarray) -> None:
        w = table[:, col[source]].copy()
        for k, bone in enumerate(bones):
            table[:, col[bone]] = w * shares[:, k]

    chains = []
    for side, mpfb in SIDES.items():
        for limb, twists in TWISTS.items():
            chains.append([f"{limb}_{side}", *(f"{t}_{side}" for t, _ in twists)])
        hand = f"hand_{side}"
        parts = [f"wrist.{mpfb}", *(f"metacarpal{k}.{mpfb}" for k in range(1, 5))]
        seed = _table(default_weights, parts)
        total = seed.sum(1, keepdims=True)
        shares = np.where(total > 0, seed / np.where(total > 0, total, 1.0), np.eye(5)[0])
        split(hand, [hand, *(f"{f}_metacarpal_{side}" for f in METACARPALS)], shares)
    chains += [["spine_03", "spine_04", "spine_05"], ["neck_01", "neck_02"]]
    for chain in chains:
        heads = [joints.at(rig[b]["head"]) for b in chain]
        end = joints.at(rig[chain[-1]]["tail"])
        split(chain[0], chain, _chain_shares(co, heads, end))
    # at most MAX_INFLUENCES a vertex, the dropped weight given back in proportion
    capped = 0
    for i in np.flatnonzero((table > FLOOR).sum(1) > MAX_INFLUENCES):
        keep = np.argsort(table[i])[::-1][:MAX_INFLUENCES]
        row = np.zeros_like(table[i])
        row[keep] = table[i, keep] * table[i].sum() / table[i, keep].sum()
        table[i] = row
        capped += 1
    table[table < FLOOR] = 0.0
    # every weighted vertex's weights summing to 1 (UsdSkel's and Unreal's skinning take them so): MPFB2's breast
    # weights sit on top of its plain game-engine ones, up to 1.68 a vertex on the chest (831 vertices) - Blender's
    # Armature modifier divides by the total, so the breasts' share was this all along
    total = table.sum(1, keepdims=True)
    over = int((np.abs(total[:, 0] - 1.0) > 1e-3).sum() - (total[:, 0] == 0).sum())
    table = np.where(total > 0, table / np.where(total > 0, total, 1.0), 0.0)
    out = {}
    for j, name in enumerate(names):
        hit = np.flatnonzero(table[:, j])
        if len(hit):
            out[name] = [[int(i), round(float(table[i, j]), 6)] for i in hit]
    report = {"bones weighted": len(out), "capped vertices": capped, "most influences": int((table > 0).sum(1).max()),
              "vertices renormalised": over, "unweighted vertices": int((total_before == 0).sum())}  # fmt: skip
    return out, report


def main(out: Path = OUT) -> dict:
    game = json.loads((RIGS / "rig.game_engine_with_breast.json").read_text(encoding="utf-8"))
    default = json.loads((RIGS / "rig.default.json").read_text(encoding="utf-8"))
    game_w = json.loads((RIGS / "weights.game_engine_with_breast.json").read_text(encoding="utf-8"))
    default_w = json.loads((RIGS / "weights.default.json").read_text(encoding="utf-8"))["weights"]
    joints = Joints(_vertices(MAKEHUMAN / "3dobjs" / "base.obj"), _groups())
    rig = definition(game, default, joints)
    table, report = weights(rig, game_w["weights"], default_w, joints)
    out.mkdir(parents=True, exist_ok=True)
    (out / "ue5.json").write_text(json.dumps(rig, indent=1), encoding="utf-8")
    note = ("JustStage's UE5 skeleton (docs/standards/skeleton-and-face.md 1.1), made by tools/make_skeleton.py from "
            "MPFB2's CC0 game_engine_with_breast and default rigs and weights")  # fmt: skip
    (out / "weights.ue5.json").write_text(json.dumps({
        "copyright": "JustStage contributors; from MPFB2's weights (CC0, MakeHuman / MPFB2 contributors)",
        "description": note, "license": "CC0", "name": "ue5", "version": game_w["version"], "weights": table,
    }), encoding="utf-8")  # fmt: skip
    print(f"SKELETON: {len(rig)} bones -> {out}; {report}", flush=True)
    return report


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
