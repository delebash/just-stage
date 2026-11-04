#!/usr/bin/env bash
# The realism gate's Unreal steps (the card): the scene in the editor window, then Movie Render Queue's command-line
# render of the saved queue (https://dev.epicgames.com/documentation/en-us/unreal-engine/using-command-line-rendering-
# with-move-render-queue-in-unreal-engine). The import (tools/gate/unreal_import.py) runs before, as a commandlet.
set -euo pipefail
UE="/f/Epic/UE_5.8/Engine/Binaries/Win64"
PROJECT="E:/Dev/3D/just-stage/.dev/gate/JustStageGate/JustStageGate.uproject"
LOGS="E:/Dev/3D/just-stage/.dev/gate/out"
"$UE/UnrealEditor.exe" "$PROJECT" -ExecutePythonScript="E:/Dev/3D/just-stage/tools/gate/unreal_scene.py" \
  -unattended -nosplash -nop4 -log -abslog="$LOGS/unreal_scene_gui.log"
"$UE/UnrealEditor-Cmd.exe" "$PROJECT" /Game/Gate/Maps/gate_stage -game -MoviePipelineConfig=/Game/Gate/GateQueue \
  -windowed -resx=1280 -resy=720 -unattended -nosplash -nop4 -RenderOffscreen -log -stdout \
  -abslog="$LOGS/unreal_render.log"
