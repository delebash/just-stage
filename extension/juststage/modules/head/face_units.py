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


def add(obj: bpy.types.Object) -> list[str]:
    """Every unit the pack has, as a shape key at 0 on `obj` (replacing one of the same name); returns the names."""
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis", from_mix=False)
    basis = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
    obj.data.shape_keys.reference_key.data.foreach_get("co", basis)
    basis = basis.reshape(-1, 3)
    added = []
    for name in ARKIT:
        path = unit_path(name)
        if not path.exists():
            continue
        rows = makehuman.read_target(path)
        co = basis.copy()
        if rows:
            index = np.fromiter((r[0] for r in rows), dtype=np.int64, count=len(rows))
            co[index] += np.array([r[1:] for r in rows], dtype=np.float32) * makehuman.SCALE_TO_METRES
        key = obj.data.shape_keys.key_blocks.get(name) or obj.shape_key_add(name=name, from_mix=False)
        key.data.foreach_set("co", co.ravel())
        key.value = 0.0
        key.slider_min, key.slider_max = 0.0, 1.0
        added.append(name)
    return added
