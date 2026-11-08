# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face's 52 ARKit shape keys, from MakeHuman's CC0 "Faceunits 01" (Mika Suominen; made for hm08, so no transfer -
RESEARCH ~1798) - the face interchange of docs/standards/skeleton-and-face.md §2.1 and the job table's "Face
interchange" row: shape keys by Apple's names (https://developer.apple.com/documentation/arkit/arfaceanchor/
blendshapelocation), not a target's names. Each key is the character's basis plus the unit's offsets, at 0; the face
rig (rig/face.dna through OpenRigLogic, §2.3) drives them."""

from __future__ import annotations

import bpy
import numpy as np

from ... import paths
from ...core import makehuman

#: ARKit's 52, in skeleton-and-face.md §2.1's order: the eyes, mouth and jaw, brows, cheeks and nose, tongue
ARKIT = (
    "eyeBlinkLeft", "eyeLookDownLeft", "eyeLookInLeft", "eyeLookOutLeft", "eyeLookUpLeft", "eyeSquintLeft",
    "eyeWideLeft", "eyeBlinkRight", "eyeLookDownRight", "eyeLookInRight", "eyeLookOutRight", "eyeLookUpRight",
    "eyeSquintRight", "eyeWideRight", "jawForward", "jawLeft", "jawRight", "jawOpen", "mouthClose", "mouthFunnel",
    "mouthPucker", "mouthLeft", "mouthRight", "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight",
    "mouthDimpleLeft", "mouthDimpleRight", "mouthStretchLeft", "mouthStretchRight", "mouthRollLower", "mouthRollUpper",
    "mouthShrugLower", "mouthShrugUpper", "mouthPressLeft", "mouthPressRight", "mouthLowerDownLeft",
    "mouthLowerDownRight", "mouthUpperUpLeft", "mouthUpperUpRight", "browDownLeft", "browDownRight", "browInnerUp",
    "browOuterUpLeft", "browOuterUpRight", "cheekPuff", "cheekSquintLeft", "cheekSquintRight", "noseSneerLeft",
    "noseSneerRight", "tongueOut",
)  # fmt: skip


def unit_path(name: str):
    return paths.makehuman("targets", "faceunits", f"{name}.target")


#: units taken from ICT-FaceKit's scanned shapes instead of Faceunits (Q-RIG-1's per-shape pick, 2026-11-08;
#: `tools/make_ict_units.py`): the closed lid - Faceunits' eyeBlink folds the skin above the lashes, ICT's closes
#: smooth; the smile - ICT's mouthSmile + cheekSquint lift the corners and the cheeks as HD Aaron's do (MediaPipe's
#: Face Landmarker scores the smile 0.83 / 0.84 against his 0.86 / 0.85; Faceunits' 0.72 / 0.79, the mouth alone
#: bent - RESEARCH 14.7)
ICT_UNITS = ("eyeBlinkLeft", "eyeBlinkRight", "mouthSmileLeft", "mouthSmileRight", "cheekSquintLeft",
             "cheekSquintRight")  # fmt: skip


def _offsets(name: str) -> tuple[np.ndarray, np.ndarray] | None:
    """A unit's hm08 (indices, offsets in metres): ICT's carried shape for ICT_UNITS, else Faceunits' target; None
    where the pack has none."""
    if name in ICT_UNITS:
        data = np.load(paths.generated("faceunits_ict", f"{name}.npz", tool="tools/make_ict_units.py"))
        return data["index"].astype(np.int64), data["delta"].astype(np.float32)
    path = unit_path(name)
    if not path.exists():
        return None
    rows = makehuman.read_target(path)
    if not rows:
        return np.zeros(0, np.int64), np.zeros((0, 3), np.float32)
    index = np.fromiter((r[0] for r in rows), dtype=np.int64, count=len(rows))
    return index, np.array([r[1:] for r in rows], dtype=np.float32) * makehuman.SCALE_TO_METRES


def add(obj: bpy.types.Object) -> list[str]:
    """Every unit the pack has, as a shape key at 0 on `obj` (replacing one of the same name); returns the names."""
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis", from_mix=False)
    basis = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    obj.data.shape_keys.reference_key.data.foreach_get("co", basis)
    basis = basis.reshape(-1, 3)
    added = []
    from ..body import base

    for name in ARKIT:
        found = _offsets(name)
        if found is None:
            continue
        co = basis.copy()
        if len(found[0]):
            index, delta = base.extend(obj, *found)
            co[index] += delta
        key = obj.data.shape_keys.key_blocks.get(name) or obj.shape_key_add(name=name, from_mix=False)
        key.data.foreach_set("co", co.ravel())
        key.value = 0.0
        key.slider_min, key.slider_max = 0.0, 1.0
        added.append(name)
    return added


#: the units that move the jaw bone. The lower teeth, their gums and the tongue ride it rigidly, as MetaHuman's ride
#: `FACIAL_C_Jaw` and CC5's ride `CC_Base_JawRoot` (CC Blender Tools' drivers); without this the skin opened and the
#: teeth stayed (the part-by-part gate, 2026-11-05)
JAW_UNITS = ("jawOpen", "jawForward", "jawLeft", "jawRight")
#: the teeth part's groups that ride the jaw (`teeth.groups.json`, tools/bind_parts.py)
JAW_GROUPS = ("lower_teeth_and_gums", "tongue")
#: the jaw's hinge: MakeHuman's jaw bone runs from the `mouth` joint (its head, the pivot) to the `jaw` joint (the chin)
HINGE_JOINT = "joint-mouth"
#: the chin: the skin a jaw unit moves by at least this share of its largest move - bone under thin skin, so it moves
#: with the jaw; the lips and cheeks stretch instead
CHIN_SHARE = 0.8


def _jaw_motion(name: str, shaped: np.ndarray, offsets: np.ndarray, hinge: np.ndarray):
    """The jaw's rigid motion under one unit, read off the chin: jawOpen turns about the jaw joint's left-right axis
    (the angle each chin point turns about it, weighted by how far it moves); the others move as the chin does."""
    moved = np.linalg.norm(offsets, axis=1)
    chin = moved >= CHIN_SHARE * moved.max()
    if name != "jawOpen":
        shift = offsets[chin].mean(0)
        return lambda points: points + shift
    a = shaped[chin] - hinge
    b = a + offsets[chin]
    turn = np.arctan2(a[:, 1] * b[:, 2] - a[:, 2] * b[:, 1], a[:, 1] * b[:, 1] + a[:, 2] * b[:, 2])
    angle = float((turn * moved[chin]).sum() / moved[chin].sum())
    c, s = np.cos(angle), np.sin(angle)
    rotation = np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])
    return lambda points: hinge + (points - hinge) @ rotation.T


def add_to_teeth(body: bpy.types.Object, teeth: bpy.types.Object) -> list[str]:
    """The jaw units on the teeth part (replacing any of the same name), from the body's own units - so they follow
    every face the units were added to. Both meshes share the body's space (the parts are fitted in it, parented
    to it - parts.py). Returns the names added."""
    from ..body import build

    keys = body.data.shape_keys
    if keys is None or not any(name in keys.key_blocks for name in JAW_UNITS):
        return []
    shaped = build.shaped_coords(body)
    joint = body.vertex_groups.get(HINGE_JOINT)
    if joint is None:
        return []
    weights = np.zeros(len(body.data.vertices))
    for v in body.data.vertices:
        for g in v.groups:
            if g.group == joint.index:
                weights[v.index] = g.weight
    hinge = shaped[weights > 0.5].mean(0)
    from . import parts

    sets = parts.groups("teeth")
    rides = np.zeros(len(teeth.data.vertices), dtype=bool)
    for name in JAW_GROUPS:
        rides[sets.get(name, [])] = True
    if not rides.any():
        return []
    if not teeth.data.shape_keys:
        teeth.shape_key_add(name="Basis", from_mix=False)
    base = np.empty(len(teeth.data.vertices) * 3, dtype=np.float32)
    teeth.data.shape_keys.reference_key.data.foreach_get("co", base)
    base = base.reshape(-1, 3).astype(np.float64)
    reference = np.empty(len(body.data.vertices) * 3, dtype=np.float32)
    keys.reference_key.data.foreach_get("co", reference)
    added = []
    for name in JAW_UNITS:
        unit = keys.key_blocks.get(name)
        if unit is None:
            continue
        co = np.empty(len(body.data.vertices) * 3, dtype=np.float32)
        unit.data.foreach_get("co", co)
        offsets = (co - reference).reshape(-1, 3).astype(np.float64)
        if not offsets.any():
            continue
        move = _jaw_motion(name, shaped, offsets, hinge)
        posed = base.copy()
        posed[rides] = move(base[rides])
        key = teeth.data.shape_keys.key_blocks.get(name) or teeth.shape_key_add(name=name, from_mix=False)
        key.data.foreach_set("co", posed.astype(np.float32).ravel())
        key.value = 0.0
        key.slider_min, key.slider_max = 0.0, 1.0
        _follow(key, keys, name)
        added.append(name)
    return added


def _follow(key: bpy.types.ShapeKey, source: bpy.types.Key, name: str) -> None:
    """`key`'s value driven by the body's key of the same name (Blender's single-property driver - no Python runs)."""
    key.driver_remove("value")
    driver = key.driver_add("value").driver
    driver.type = "AVERAGE"
    var = driver.variables.new()
    var.type = "SINGLE_PROP"
    var.targets[0].id_type = "KEY"
    var.targets[0].id = source
    var.targets[0].data_path = f'key_blocks["{name}"].value'
