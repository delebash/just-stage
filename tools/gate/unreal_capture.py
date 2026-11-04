# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The realism gate's editor-viewport captures (the card), for the MetaHuman benchmark: MetaHuman's editor actor is
editor-only (Movie Render Queue's play-in-editor session leaves it out - its render came back without it, measured
2026-11-04) and a game-ready build needs MetaHuman's cloud auto-rigging ("Character is not rigged") - the user's
account, not used. So both characters are captured the same way, from the editor's own viewport:

    UnrealEditor.exe .dev/gate/JustStageGate/JustStageGate.uproject -ExecCmds="py tools/gate/unreal_capture.py"

For each light alone (key, rim, sky) and each character (ours: gate_<light>; MetaHuman's: gate_mh_<light>, its actor
re-spawned and aligned as in tools/gate/unreal_metahuman.py), a cine camera at the face camera's place, the editor's
high-resolution screenshot with HDR (linear EXR) after the view settles. Written as
`.dev/gate/renders/{ue_ours|ue_mh}_face_{light}.exr`; our character's capture also checks the path against the render
queue's (the same scene, two capture routes)."""

import json
import math
import shutil
from pathlib import Path

import unreal

ROOT = Path(r"E:/Dev/3D/just-stage")
GATE = ROOT / ".dev" / "gate"
DEST = "/Game/Gate"
meta = json.loads((GATE / "meta.json").read_text())
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
level_lib = unreal.EditorLoadingAndSavingUtils
SETTLE_S = 6.0  # Lumen and the virtual shadow maps settle in the live viewport
SHOTS = [("ue_ours", f"gate_{light}", light) for light in ("key", "rim", "sky")] + \
        [("ue_mh", f"gate_mh_{light}", light) for light in ("key", "rim", "sky")]
character = unreal.load_asset(f"{DEST}/MH/MH_benchmark")
bounds = json.loads((GATE / "out" / "unreal_bounds.json").read_text())


def log(msg):
    unreal.log("GATE CAP " + msg)


def ue(v):
    return unreal.Vector(v[0] * 100.0, -v[1] * 100.0, v[2] * 100.0)


def look_at(src, dst):
    d = unreal.Vector(dst.x - src.x, dst.y - src.y, dst.z - src.z)
    return unreal.Rotator(roll=0.0, pitch=math.degrees(math.atan2(d.z, math.hypot(d.x, d.y))),
                          yaw=math.degrees(math.atan2(d.y, d.x)))


def _centre(b):
    return unreal.Vector(*[(lo + hi) / 2 for lo, hi in zip(b["min"], b["max"])])


OUR_LEFT, OUR_RIGHT = _centre(bounds["Average_man_eyeLeft"]), _centre(bounds["Average_man_eyeRight"])


def _eyes(actor):
    for comp in actor.get_components_by_class(unreal.SkeletalMeshComponent):
        if comp.does_socket_exist("FACIAL_L_Eye") and comp.does_socket_exist("FACIAL_R_Eye"):
            return comp.get_socket_location("FACIAL_L_Eye"), comp.get_socket_location("FACIAL_R_Eye")
    return None


def _align(actor):
    eyes = _eyes(actor)
    if eyes is None:
        return False
    left, right = eyes
    ours = math.atan2(OUR_LEFT.y - OUR_RIGHT.y, OUR_LEFT.x - OUR_RIGHT.x)
    theirs = math.atan2(left.y - right.y, left.x - right.x)
    rot = actor.get_actor_rotation()
    actor.set_actor_rotation(unreal.Rotator(roll=rot.roll, pitch=rot.pitch, yaw=rot.yaw + math.degrees(ours - theirs)),
                             False)
    left, right = _eyes(actor)
    loc = actor.get_actor_location()
    actor.set_actor_location(unreal.Vector(loc.x + (OUR_LEFT.x + OUR_RIGHT.x - left.x - right.x) / 2,
                                           loc.y + (OUR_LEFT.y + OUR_RIGHT.y - left.y - right.y) / 2,
                                           loc.z + (OUR_LEFT.z + OUR_RIGHT.z - left.z - right.z) / 2), False, False)
    return True


def _camera():
    cam = meta["cameras"]["face"]
    w, h = meta["resolution"]["face"]
    loc = ue(cam["location"])
    actor = actors.spawn_actor_from_class(unreal.CineCameraActor, loc, look_at(loc, ue(cam["target"])))
    comp = actor.get_cine_camera_component()
    comp.set_editor_property("filmback", unreal.CameraFilmbackSettings(sensor_width=36.0, sensor_height=36.0 * h / w))
    comp.set_editor_property("current_focal_length", cam["lens"])
    focus = comp.get_editor_property("focus_settings")
    focus.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE)
    comp.set_editor_property("focus_settings", focus)
    return actor


state = {"i": -1, "t": 0.0, "phase": "load", "task": None, "handle": None, "camera": None, "file": None}
OUT = GATE / "renders"


def _start(i):
    tag, level, light = SHOTS[i]
    level_lib.load_map(f"{DEST}/Maps/{level}")
    if tag == "ue_mh":
        for actor in actors.get_all_level_actors():
            if "MetaHuman" in actor.get_class().get_name():
                actors.destroy_actor(actor)
        mh = sub.spawn_meta_human_actor(character, True)
        log(f"{level}: MetaHuman aligned {_align(mh)}")
    state["camera"] = _camera()
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
        state["camera"].get_actor_location(), state["camera"].get_actor_rotation())
    state["file"] = f"{tag}_face_{light}"


def _tick(dt):
    state["t"] += dt
    if state["phase"] == "load":
        state["i"] += 1
        if state["i"] >= len(SHOTS):
            unreal.unregister_slate_post_tick_callback(state["handle"])
            sub.remove_object_to_edit(character)
            log("done")
            unreal.SystemLibrary.quit_editor()
            return
        _start(state["i"])
        state["phase"], state["t"] = "settle", 0.0
    elif state["phase"] == "settle" and state["t"] > SETTLE_S:
        w, h = meta["resolution"]["face"]
        state["task"] = unreal.AutomationLibrary.take_high_res_screenshot(
            w, h, f"{state['file']}.exr", state["camera"], False, True)
        state["phase"], state["t"] = "shoot", 0.0
    elif state["phase"] == "shoot" and (state["task"] is None or state["task"].is_task_done()) and state["t"] > 2.0:
        shots = Path(unreal.Paths.project_saved_dir()) / "Screenshots"
        found = sorted(shots.rglob(f"{state['file']}*.exr"), key=lambda p: p.stat().st_mtime)
        if found:
            shutil.copy(found[-1], OUT / f"{state['file']}.exr")
            log(f"captured {state['file']} <- {found[-1]}")
        else:
            log(f"no EXR for {state['file']} under {shots}: {[p.name for p in shots.rglob('*')][-6:]}")
        state["phase"] = "load"


if not sub.try_add_object_to_edit(character):
    log("could not open the MetaHuman for edit")
state["handle"] = unreal.register_slate_post_tick_callback(_tick)
