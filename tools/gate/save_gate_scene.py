# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The gate's man as `parts_gate` builds him today (the library's character, his hair, brows, stubble, the face units)
on the app's stage, saved for the live view's budget (`live_view_budget.py`, checklist row 20) - the 2026-11-04 scene
held an older character and groom.

    python tools/dev.py blender -b --python tools/gate/save_gate_scene.py -- OUT.blend
"""

import importlib.util
import sys
from pathlib import Path

import bpy

spec = importlib.util.spec_from_file_location("parts_gate", Path(__file__).resolve().parent / "parts_gate.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

out = Path(sys.argv[sys.argv.index("--") + 1])
scene, cam = pg._stage()
built = pg.build_ours(scene)
pg.set_expression("ours", built, "neutral")
pg.place(cam, *pg.view("face", pg.anchors("ours", built)))
out.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print("SAVED", out, "objects", len(scene.objects), flush=True)
