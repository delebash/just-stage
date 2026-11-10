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
    add_blink_props(obj)
    add_smile_props(obj)
    return added


#: each eye's blink key and the object property that carries its value to the skin's shader (modules/skin/maps.py's
#: closed lid): an Attribute node of type Object reads it, so a skin shared by characters needs no retargeting
BLINK_PROPS = (("eyeBlinkLeft", "js_blink_l"), ("eyeBlinkRight", "js_blink_r"))
#: each side's smile - the larger of its mouth-corner and cheek-squint keys - as an object property the skin's crow's
#: feet read (modules/skin/maps.py `_smile_wrinkles`; 2026-11-10: HD Aaron's smile folds the eyes' outer corners, ours
#: didn't). A unit's own value drives the map - not mesh tension (the plan's §3 rule 8: US 12,062,140 claim 17)
SMILE_PROPS = (("js_smile_l", ("mouthSmileLeft", "cheekSquintLeft")),
               ("js_smile_r", ("mouthSmileRight", "cheekSquintRight")))  # fmt: skip


def add_blink_props(obj: bpy.types.Object) -> None:
    """Each blink key's value as an object property (`BLINK_PROPS`), through a non-scripted driver (no Python in the
    file); nothing for a character without the keys, nothing twice."""
    keys = obj.data.shape_keys
    for key, prop in BLINK_PROPS:
        if keys is None or key not in keys.key_blocks:
            continue
        if obj.animation_data and obj.animation_data.drivers.find(f'["{prop}"]'):
            continue
        obj[prop] = 0.0
        driver = obj.driver_add(f'["{prop}"]').driver
        driver.type = "AVERAGE"
        var = driver.variables.new()
        var.type = "SINGLE_PROP"
        var.targets[0].id_type = "KEY"
        var.targets[0].id = keys
        var.targets[0].data_path = f'key_blocks["{key}"].value'


def add_smile_props(obj: bpy.types.Object) -> None:
    """Each side's smile (`SMILE_PROPS`) as an object property: a non-scripted MAX driver over its keys; nothing for a
    character without them, nothing twice."""
    keys = obj.data.shape_keys
    for prop, names in SMILE_PROPS:
        if keys is None or not all(n in keys.key_blocks for n in names):
            continue
        if obj.animation_data and obj.animation_data.drivers.find(f'["{prop}"]'):
            continue
        obj[prop] = 0.0
        driver = obj.driver_add(f'["{prop}"]').driver
        driver.type = "MAX"
        for name in names:
            var = driver.variables.new()
            var.type = "SINGLE_PROP"
            var.targets[0].id_type = "KEY"
            var.targets[0].id = keys
            var.targets[0].data_path = f'key_blocks["{name}"].value'
