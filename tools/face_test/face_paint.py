# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test, stage 2 (the card): each clay view repainted as a photograph by JustStage's server
(`juststage.face_paint`, FLUX.2 klein editing from the view). python face_paint.py SEED [VIEW ...]

Run (JustStage's server up): python tools/face_test/face_paint.py SEED [VIEW ...]
"""

import base64
import json
import sys
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:17481"
DIR = Path("E:/Dev/3D/just-stage/.dev/facetest")
PROMPT = (
    "Turn this 3D render into a real photograph of the same bald man: exactly the same head shape, face, pose, "
    "camera angle and framing. Natural human skin with visible pores, fine lines, slight redness on the nose and "
    "cheeks, faint freckles, realistic lips and eyelids, shaved head. Soft even studio light from every side, no "
    "shadows, plain grey "
    "background. Sharp focus, high detail, professional portrait photo."
)


def call(method, path, body=None, timeout=600):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


seed = int(sys.argv[1])
views = sys.argv[2:] or [
    "front",
    "left40",
    "right40",
    "left90",
    "right90",
    "above",
    "below",
    "face",
    "faceleft30",
    "faceright30",
]
jobs = {}
for view in views:
    init = base64.b64encode((DIR / f"clay_{view}.png").read_bytes()).decode()
    # the view is both the starting picture and the reference FLUX.2 [klein] edits from (house-paint's aiphoto/edit.js)
    request = {"prompt": PROMPT, "width": 1024, "height": 1024, "seed": seed, "init": init, "refs": [init]}
    jobs[view] = json.loads(call("POST", "/v1/ai/image/jobs", {"feature": "juststage.face_paint", "request": request}))[
        "id"
    ]
t0 = time.time()
for view, job_id in jobs.items():  # the server queues them; each waits for the one before
    while (state := json.loads(call("GET", f"/v1/jobs/{job_id}")))["state"] == "running":
        time.sleep(1)
    if state["state"] != "done":
        sys.exit(f"{view}: {state['state']} {state.get('error')}")
    (DIR / f"painted_{view}.png").write_bytes(call("GET", f"/v1/ai/image/jobs/{job_id}/result"))
    print(f"{view}: done at {time.time() - t0:.0f}s")
