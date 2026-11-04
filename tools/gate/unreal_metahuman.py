# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The realism gate's benchmark (the brief §6 step 2): a MetaHuman of MetaHuman's own making under the gate's stage, in
the editor window (local comparison only - nothing of MetaHuman's leaves the gate project; clean-room: its renders
are looked at, never its maps taken out):

    UnrealEditor.exe .dev/gate/JustStageGate/JustStageGate.uproject -ExecCmds="py tools/gate/unreal_metahuman.py"

A MetaHuman Character asset (MetaHuman's factory: its default head), opened for edit (MetaHuman's local texture
synthesis), its preview assembled, its editor actor spawned in a copy of each gate level with our character's actors
removed, framed by a face camera at the same lens and distance as ours, aimed at its own eyes; then rendered by
tools/gate/unreal_render.py with GATE_MAPS=mh (same queue settings). Writes the MetaHuman's head position to
`.dev/gate/out/mh_head.json` for the camera."""

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

head = None
for variant in VARIANTS:
    world = level_lib.load_map(f"{DEST}/Maps/gate_{variant}")
    for actor in actors.get_all_level_actors():
        if isinstance(actor, unreal.StaticMeshActor):
            mesh = actor.static_mesh_component.static_mesh
            if mesh and mesh.get_name() in ("gate_body", "Average_man_eyeLeft", "Average_man_eyeRight"):
                actors.destroy_actor(actor)
    mh = sub.spawn_meta_human_actor(character, False)
    origin, extent = mh.get_actor_bounds(False)
    top = origin.z + extent.z
    head = {"top_cm": top, "centre": [origin.x, origin.y, origin.z], "extent": [extent.x, extent.y, extent.z]}
    level_lib.save_map(world, f"{DEST}/Maps/gate_mh_{variant}")
    log(f"level gate_mh_{variant}: bounds origin {origin} extent {extent}")
(GATE / "out" / "mh_head.json").write_text(json.dumps(head, indent=1))
sub.remove_object_to_edit(character)
log("done")
unreal.SystemLibrary.quit_editor()
