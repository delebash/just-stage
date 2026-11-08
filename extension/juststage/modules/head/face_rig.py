# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face rig at runtime (`docs/standards/skeleton-and-face.md` §2.3; the job's doc
`docs/plans/2026-11-08-face-rig.md` step 3b): the character's GUI controls - MetaHuman's names, so MetaHuman Animator's
curves key them as they come - live as animatable properties on the character; when they change (an edit, a frame),
OpenRigLogic's RigLogic evaluates the face DNA (`tools/make_face_dna.py`) and its blend-shape outputs set the shape keys
of the same names (our ARKit keys) - the data model's "never hand-made drivers" (`character-data-model.md` §2). The way
Poly Hammer's DNA add-on runs RigLogic in Blender (RESEARCH §14.7): app handlers on frame change and depsgraph update.
While the rig is on, it owns those keys; an ARKit live source drives them with the rig off."""

from __future__ import annotations

import bpy
from bpy.app.handlers import persistent

MARK = "JustStage face rig"  # a custom property on a character whose face rig is on (its value: 1)
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
        _STATE["dna"] = {
            "reader": reader, "logic": riglogic.RigLogic(reader),
            "gui": [reader.getGUIControlName(i) for i in range(reader.getGUIControlCount())],
            "low": [lows.get(i, 0.0) for i in range(reader.getGUIControlCount())],
            "channels": [reader.getBlendShapeChannelName(i) for i in range(reader.getBlendShapeChannelCount())],
        }  # fmt: skip
    return _STATE["dna"]


def controls() -> list[str]:
    return list(_dna()["gui"])


def attach(character: bpy.types.Object) -> int:
    """The face rig on: every GUI control a property on the character at 0 (a two-way control -1..1, else 0..1);
    returns the controls."""
    rig = _dna()
    for name, low in zip(rig["gui"], rig["low"], strict=True):
        if name not in character.keys():
            character[name] = 0.0
        ui = character.id_properties_ui(name)
        ui.update(min=low, max=1.0, soft_min=low, soft_max=1.0, default=0.0)
    character[MARK] = 1
    _STATE.pop(character.juststage.character_id, None)
    evaluate(character)
    return len(rig["gui"])


def evaluate(character: bpy.types.Object) -> dict[str, float]:
    """RigLogic on the character's control values, its outputs into the shape keys; nothing when no control moved.
    Returns the keys it set."""
    import riglogic

    rig = _dna()
    cid = character.juststage.character_id
    state = _STATE.get(cid)
    if state is None:
        state = _STATE[cid] = {"instance": riglogic.RigInstance(rig["logic"]), "last": None}
    values = [float(character.get(name, 0.0)) for name in rig["gui"]]
    if values == state["last"]:
        return {}
    instance = state["instance"]
    for i, value in enumerate(values):
        instance.setGUIControl(i, value)
    rig["logic"].mapGUIToRawControls(instance)
    rig["logic"].calculate(instance)
    out = instance.getBlendShapeOutputs()
    keys = character.data.shape_keys.key_blocks if character.data.shape_keys else {}
    done = {}
    for i, name in enumerate(rig["channels"]):
        key = keys.get(name)
        if key is not None and abs(key.value - out[i]) > 1e-6:
            key.value = out[i]
            done[name] = out[i]
    state["last"] = values
    return done


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
