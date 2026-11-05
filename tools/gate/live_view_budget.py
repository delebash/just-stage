# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The live view's budget (the review brief §10: "today's character measured in Material Preview (Blender's
`wm.redraw_timer`, fps and VRAM) ... every rec's gate reports its ms and MB"): the gate scene's character in the app's
live view (Material Preview, the scene's lights and world - core/viewport.py `show_live`), through the face camera,
in Blender's window (a redraw needs one):

    python tools/dev.py blender .dev/gate/gate_scene.blend --python tools/gate/live_view_budget.py

Per case (hair hidden as in the gate; hair shown): ms per redraw over 30 redraws after 10 to warm up, and the card's
memory in use (`nvidia-smi`). Written to `.dev/gate/out/live_view_budget.json`; Blender quits when done."""

import json
import subprocess
import time
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".dev" / "gate" / "out" / "live_view_budget.json"
WARM, RUNS = 10, 30


def _vram_mb() -> int:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, check=False).stdout.strip().splitlines()
    return int(out[0]) if out else -1


def _view3d():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                return window, area
    return None, None


def _measure(window, area) -> dict:
    """Each redraw after a 0.1 mm camera nudge, so EEVEE renders afresh as while orbiting or dragging a slider (a
    still view converges and then only re-displays - measured 2026-11-04: 4.8 ms, hair shown no slower)."""
    cam = bpy.context.scene.camera

    def redraws(n):
        with bpy.context.temp_override(window=window, area=area):
            for i in range(n):
                cam.location.x += 0.0001 if i % 2 else -0.0001
                bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)

    redraws(WARM)
    t = time.perf_counter()
    redraws(RUNS)
    ms = (time.perf_counter() - t) * 1000 / RUNS
    return {"ms_per_fresh_frame": round(ms, 1), "fps": round(1000 / ms, 1), "vram_mb": _vram_mb()}


def _run():
    from bl_ext.system.juststage.core import viewport

    window, area = _view3d()
    if area is None:
        print("BUDGET no 3D view", flush=True)
        bpy.ops.wm.quit_blender()
        return None
    viewport.show_live([window.screen], camera=True)
    region = next(r for r in area.regions if r.type == "WINDOW")
    result = {"view_px": [region.width, region.height]}
    scene = bpy.context.scene
    result["hair_hidden"] = _measure(window, area)
    for obj in scene.objects:  # the gate hid hair and lashes in both engines (blender_gate.py prepare)
        if obj.hide_viewport and obj.type in ("CURVES", "MESH") and obj.parent is not None:
            obj.hide_viewport = False
    result["hair_shown"] = _measure(window, area)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1))
    print("BUDGET", json.dumps(result), flush=True)
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(_run, first_interval=8.0)  # the window and the extension's startup draw first
