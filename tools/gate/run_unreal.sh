#!/usr/bin/env bash
# The realism gate's Unreal steps (the card): the scene in the editor window (tools/gate/unreal_scene.py), then Movie
# Render Queue in the editor - its queue subsystem and play-in-editor executor (tools/gate/unreal_render.py). The import
# (tools/gate/unreal_import.py) runs before, as a commandlet without the card.
set -euo pipefail
UE="/f/Epic/UE_5.8/Engine/Binaries/Win64"
PROJECT="E:/Dev/3D/just-stage/.dev/gate/JustStageGate/JustStageGate.uproject"
LOGS="E:/Dev/3D/just-stage/.dev/gate/out"
step="${1:-all}"
if [[ "$step" == "all" || "$step" == "scene" ]]; then
  "$UE/UnrealEditor.exe" "$PROJECT" -ExecutePythonScript="E:/Dev/3D/just-stage/tools/gate/unreal_scene.py" \
    -unattended -nosplash -nop4 -log -abslog="$LOGS/unreal_scene_gui.log"
fi
if [[ "$step" == "all" || "$step" == "render" ]]; then
  # -ExecutePythonScript closes the editor once the script returns ("Cmd: QUIT_EDITOR" right after, measured
  # 2026-11-04) - before the queue's callbacks run; the console's `py` command at start-up keeps it open until the
  # script itself quits
  "$UE/UnrealEditor.exe" "$PROJECT" -ExecCmds="py E:/Dev/3D/just-stage/tools/gate/unreal_render.py" \
    -unattended -nosplash -nop4 -log -abslog="$LOGS/unreal_render.log"
fi
