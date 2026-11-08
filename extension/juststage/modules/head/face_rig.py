# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face rig at runtime (`docs/standards/skeleton-and-face.md` §2.3; the job's doc
`docs/plans/2026-11-08-face-rig.md` step 3b): the character's GUI controls - MetaHuman's names, so MetaHuman Animator's
curves key them as they come - live as animatable properties on the character; when they change (an edit, a frame),
OpenRigLogic's RigLogic evaluates the face DNA (`tools/make_face_dna.py`) and its blend-shape outputs set the shape keys
of the same names (our ARKit keys) - the data model's "never hand-made drivers" (`character-data-model.md` §2). The way
Poly Hammer's DNA add-on runs RigLogic in Blender (RESEARCH §14.7): app handlers on frame change and depsgraph update.
Its joint outputs move the face's bones in the character's skeleton (the jaw, `FACIAL_C_Jaw`, which the lower teeth
and tongue ride). Two ways, one runtime: with the rig driving (MARK 1) the controls set the keys and the joints; with
the keys driving (MARK 0 - an ARKit live source writes them, the spec §2.1) each one-to-one key is read back into its
raw control, so the joints still follow (a live jawOpen opens the jaw) - no hand-made drivers either way."""

from __future__ import annotations

import bpy
from bpy.app.handlers import persistent

MARK = "JustStage face rig"  # on a character with the face rig: 1 its controls drive, 0 its ARKit keys drive
TOOL = "python tools/dev.py blender -b --python tools/make_face_dna.py"
_STATE: dict[str, dict] = {}  # character id -> its RigLogic instance and last control values


def _dna():
    """The face DNA's reader and RigLogic, loaded once."""
    if "dna" not in _STATE:
        import dna
        import riglogic

        from ... import paths

        path = paths.generated("rig", "face.dna", tool=TOOL)
        stream = dna.FileStream(str(path), dna.FileStream.AccessMode_Read, dna.FileStream.OpenMode_Binary)
        reader = dna.BinaryStreamReader(stream, dna.DataLayer_All)
        reader.read()
        if not dna.Status.isOk():
            raise RuntimeError(f"reading {path}: {dna.Status.get().message}")
        lows = {}
        for g, f in zip(reader.getGUIToRawInputIndices(), reader.getGUIToRawFromValues(), strict=True):
            lows[g] = min(lows.get(g, 0.0), f)
        channel_raw = dict(zip(reader.getBlendShapeChannelOutputIndices(), reader.getBlendShapeChannelInputIndices(),
                               strict=True))  # fmt: skip
        _STATE["dna"] = {
            "reader": reader, "logic": riglogic.RigLogic(reader),
            "gui": [reader.getGUIControlName(i) for i in range(reader.getGUIControlCount())],
            "low": [lows.get(i, 0.0) for i in range(reader.getGUIControlCount())],
            "channels": [reader.getBlendShapeChannelName(i) for i in range(reader.getBlendShapeChannelCount())],
            "channel_raw": channel_raw, "raw_count": reader.getRawControlCount(),
            "joints": [reader.getJointName(i) for i in range(reader.getJointCount())],
        }  # fmt: skip
    return _STATE["dna"]


def controls() -> list[str]:
    return list(_dna()["gui"])


def attach(character: bpy.types.Object, drive: bool = True) -> int:
    """The face rig on the character: every GUI control a property at 0 (a two-way control -1..1, else 0..1), the
    controls driving its face (`drive`) or its ARKit keys driving and the rig moving the joints after them; returns the
    controls. The teeth's stand-in jaw keys (before the jaw was a joint) go."""
    rig = _dna()
    for name, low in zip(rig["gui"], rig["low"], strict=True):
        if name not in character.keys():
            character[name] = 0.0
        ui = character.id_properties_ui(name)
        ui.update(min=low, max=1.0, soft_min=low, soft_max=1.0, default=0.0)
    character[MARK] = 1 if drive else 0
    _STATE.pop(character.juststage.character_id, None)
    _drop_stand_in(character)
    evaluate(character)
    return len(rig["gui"])


#: the lower teeth's jaw keys and their drivers, made by the stand-in before the jaw was a joint (face_units, until
#: 2026-11-08): a saved character may still have them, and they would move the teeth twice
STAND_IN_KEYS = ("jawOpen", "jawForward", "jawLeft", "jawRight")


def _drop_stand_in(character: bpy.types.Object) -> None:
    from . import parts

    teeth = parts.parts_of(character).get("teeth")
    keys = teeth.data.shape_keys if teeth is not None else None
    if keys is None:
        return
    for name in STAND_IN_KEYS:
        key = keys.key_blocks.get(name)
        if key is not None:
            key.driver_remove("value")
            teeth.shape_key_remove(key)


def evaluate(character: bpy.types.Object) -> dict[str, float]:
    """RigLogic on the character's control values, its outputs into the shape keys; nothing when no control moved.
    Returns the keys it set."""
    import riglogic

    rig = _dna()
    cid = character.juststage.character_id
    state = _STATE.get(cid)
    if state is None:
        state = _STATE[cid] = {"instance": riglogic.RigInstance(rig["logic"]), "last": None}
    keys = character.data.shape_keys.key_blocks if character.data.shape_keys else {}
    drive = bool(character.get(MARK, 1))
    if drive:
        values = [float(character.get(name, 0.0)) for name in rig["gui"]]
    else:  # the keys drive: the one-to-one keys read back into their raw controls
        values = [float(keys[name].value) if name in keys else 0.0 for name in rig["channels"]]
    if (drive, values) == state["last"]:
        return {}
    instance = state["instance"]
    if drive:
        for i, value in enumerate(values):
            instance.setGUIControl(i, value)
        rig["logic"].mapGUIToRawControls(instance)
    else:
        for i in range(rig["raw_count"]):
            instance.setRawControl(i, 0.0)
        for channel, raw in rig["channel_raw"].items():
            instance.setRawControl(raw, values[channel])
    rig["logic"].calculate(instance)
    done = {}
    if drive:
        out = instance.getBlendShapeOutputs()
        for i, name in enumerate(rig["channels"]):
            key = keys.get(name)
            if key is not None and abs(key.value - out[i]) > 1e-6:
                key.value = out[i]
                done[name] = out[i]
    _joints(character, rig, instance.getJointOutputs())
    state["last"] = (drive, values)
    return done


def _joints(character: bpy.types.Object, rig: dict, out) -> None:
    """RigLogic's joint outputs (9 a joint: tx ty tz in cm, rx ry rz in degrees, along the bone's own axes - the DNA's
    convention, `tools/make_face_dna.py`) onto the face bones of the character's skeleton."""
    import math

    try:  # the rig module (the skeleton) may be switched off: then no joints move
        from ..rig import skeleton
    except ImportError:
        return
    arm = skeleton.skeleton_of(character)
    if arm is None:
        return
    for j, name in enumerate(rig["joints"]):
        pb = arm.pose.bones.get(name)
        if pb is None:
            continue
        tx, ty, tz, rx, ry, rz = out[9 * j: 9 * j + 6]
        pb.rotation_mode = "XYZ"
        pb.location = (tx / 100.0, ty / 100.0, tz / 100.0)
        pb.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))


@persistent
def _on_change(*_args) -> None:
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.get(MARK):
            evaluate(obj)


def register() -> None:
    for handlers in (bpy.app.handlers.frame_change_post, bpy.app.handlers.depsgraph_update_post):
        if _on_change not in handlers:
            handlers.append(_on_change)


def unregister() -> None:
    for handlers in (bpy.app.handlers.frame_change_post, bpy.app.handlers.depsgraph_update_post):
        if _on_change in handlers:
            handlers.remove(_on_change)
    _STATE.clear()
