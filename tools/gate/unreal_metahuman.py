# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The realism gate's benchmark (the brief §6 step 2): a MetaHuman of MetaHuman's own making under the gate's stage, in
the editor window (local comparison only - nothing of MetaHuman's leaves the gate project; clean-room: its renders
are looked at, never its maps taken out):

    UnrealEditor.exe .dev/gate/JustStageGate/JustStageGate.uproject -ExecCmds="py tools/gate/unreal_metahuman.py"

A MetaHuman Character asset (MetaHuman's factory: its default head), opened for edit (MetaHuman's local texture
synthesis), its preview assembled, its editor actor spawned in a copy of each gate level with our character's actors
removed, the MetaHuman turned and moved so its eyes (its face rig's eye bones) sit where ours do - the same camera,
lights and grey sphere then frame it; rendered by tools/gate/unreal_render.py with GATE_MAPS=mh (same queue settings).
Writes the aligned eyes to `.dev/gate/out/mh_head.json`."""

import json
import math
from pathlib import Path

import unreal

ROOT = Path(r"E:/Dev/3D/just-stage")
GATE = ROOT / ".dev" / "gate"
DEST = "/Game/Gate"
VARIANTS = ("key", "rim", "sky", "stage")
meta = json.loads((GATE / "meta.json").read_text())
tools = unreal.AssetToolsHelpers.get_asset_tools()
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
level_lib = unreal.EditorLoadingAndSavingUtils


def log(msg):
    unreal.log("GATE MH " + msg)


path = f"{DEST}/MH/MH_benchmark"
if unreal.EditorAssetLibrary.does_asset_exist(path):
    character = unreal.load_asset(path)
else:
    character = tools.create_asset("MH_benchmark", f"{DEST}/MH", unreal.MetaHumanCharacter,
                                   unreal.MetaHumanCharacterFactoryNew())
log(f"character {character}")
if not sub.try_add_object_to_edit(character):
    log("could not open the character for edit")
    unreal.SystemLibrary.quit_editor()
skin = character.get_editor_property("skin_settings")
sub.commit_skin_settings(character, skin)  # its own default skin: synthesizes its textures locally
sub.assemble_for_preview(character)
unreal.EditorAssetLibrary.save_loaded_asset(character)

bounds = json.loads((GATE / "out" / "unreal_bounds.json").read_text())


def _centre(b):
    return unreal.Vector(*[(lo + hi) / 2 for lo, hi in zip(b["min"], b["max"])])


OUR_LEFT, OUR_RIGHT = _centre(bounds["Average_man_eyeLeft"]), _centre(bounds["Average_man_eyeRight"])


def _eyes(actor):
    """The MetaHuman's eyes from its face rig's eye bones (MetaHuman's DNA joint names)."""
    for comp in actor.get_components_by_class(unreal.SkeletalMeshComponent):
        if comp.does_socket_exist("FACIAL_L_Eye") and comp.does_socket_exist("FACIAL_R_Eye"):
            return comp.get_socket_location("FACIAL_L_Eye"), comp.get_socket_location("FACIAL_R_Eye")
    return None


def _align(actor):
    """Turned and moved so its eyes sit where our character's do (the same camera, lights and sphere frame it)."""
    eyes = _eyes(actor)
    if eyes is None:
        log("no eye bones found - not aligned")
        return None
    left, right = eyes
    ours = math.atan2(OUR_LEFT.y - OUR_RIGHT.y, OUR_LEFT.x - OUR_RIGHT.x)
    theirs = math.atan2(left.y - right.y, left.x - right.x)
    rot = actor.get_actor_rotation()
    actor.set_actor_rotation(unreal.Rotator(roll=rot.roll, pitch=rot.pitch,
                                            yaw=rot.yaw + math.degrees(ours - theirs)), False)
    left, right = _eyes(actor)
    mid = unreal.Vector((left.x + right.x) / 2, (left.y + right.y) / 2, (left.z + right.z) / 2)
    target = unreal.Vector((OUR_LEFT.x + OUR_RIGHT.x) / 2, (OUR_LEFT.y + OUR_RIGHT.y) / 2,
                           (OUR_LEFT.z + OUR_RIGHT.z) / 2)
    loc = actor.get_actor_location()
    actor.set_actor_location(unreal.Vector(loc.x + target.x - mid.x, loc.y + target.y - mid.y,
                                           loc.z + target.z - mid.z), False, False)
    left, right = _eyes(actor)
    return {"left": [left.x, left.y, left.z], "right": [right.x, right.y, right.z],
            "ours_left": [OUR_LEFT.x, OUR_LEFT.y, OUR_LEFT.z], "ours_right": [OUR_RIGHT.x, OUR_RIGHT.y, OUR_RIGHT.z]}


head = None
for variant in VARIANTS:
    world = level_lib.load_map(f"{DEST}/Maps/gate_{variant}")
    for actor in actors.get_all_level_actors():
        if isinstance(actor, unreal.StaticMeshActor):
            mesh = actor.static_mesh_component.static_mesh
            if mesh and mesh.get_name() in ("gate_body", "Average_man_eyeLeft", "Average_man_eyeRight"):
                actors.destroy_actor(actor)
    mh = sub.spawn_meta_human_actor(character, False)
    head = _align(mh)
    level_lib.save_map(world, f"{DEST}/Maps/gate_mh_{variant}")
    log(f"level gate_mh_{variant}: eyes {head}")
(GATE / "out" / "mh_head.json").write_text(json.dumps(head, indent=1))
sub.remove_object_to_edit(character)
log("done")
unreal.SystemLibrary.quit_editor()
