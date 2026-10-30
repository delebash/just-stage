# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The AI jobs the UI started, followed by a Blender timer (`bpy.app.timers` — it runs on Blender's main thread, where
`bpy` is safe): their progress for the AI panel, Cancel, and their picture applied through the command's `finish` when
the job is done. Headless runs never come here — there the command's `main` waits.

Also the panel's view of JustStage's server (running or not, each feature's model), refreshed by a one-shot timer at
most every few seconds, so drawing the panel never waits on the network."""

from __future__ import annotations

import time

import bpy

from .. import api, engines

INTERVAL_S = 0.5
STATUS_EVERY_S = 3.0

#: job id → {"command", "params", "label", "progress", "state"}
JOBS: dict[str, dict] = {}
#: the latest outcomes, newest last, for the panel
MESSAGES: list[str] = []
STATUS: dict = {"checked": 0.0, "server": None, "models": {}, "pending": False}


def _say(text: str) -> None:
    MESSAGES.append(text)
    del MESSAGES[:-5]


def track(cmd, params, job_id: str) -> None:
    JOBS[job_id] = {"command": cmd, "params": params, "label": cmd.label, "progress": 0.0, "state": "running"}
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=INTERVAL_S)


def cancel(job_id: str) -> None:
    try:
        engines.cancel(job_id)
    except (OSError, engines.EngineError):
        pass  # gone already: the next poll says how it ended
    if job_id in JOBS:
        JOBS[job_id]["state"] = "cancelling"


def poll_once() -> bool:
    """Follow every tracked job one step; True while any is still running."""
    for job_id, entry in list(JOBS.items()):
        try:
            snapshot = engines.job(job_id)
        except (OSError, engines.EngineError) as e:
            _say(f"{entry['label']}: {e}")
            del JOBS[job_id]
            continue
        entry["progress"] = float(snapshot.get("progress") or 0.0)
        state = snapshot["state"]
        if state == "running":
            continue
        del JOBS[job_id]
        if state != "done":
            _say(f"{entry['label']}: {'cancelled' if state == 'cancelled' else engines.failure(snapshot)}")
            continue
        try:
            api.complete(entry["command"], entry["params"], engines.result(job_id))
            _say(f"{entry['label']}: done")
        except (OSError, engines.EngineError, api.CommandError) as e:
            _say(f"{entry['label']}: {e}")
    return bool(JOBS)


def _tick():
    busy = poll_once()
    _redraw()
    return INTERVAL_S if busy else None


def refresh_status_later(features: tuple[str, ...]) -> None:
    """Ask for the server's status in a moment, if the last answer is old — never in the panel's draw itself."""
    if STATUS["pending"] or time.monotonic() - STATUS["checked"] < STATUS_EVERY_S:
        return
    STATUS["pending"] = True

    def refresh():
        server = engines.health()
        models = {}
        if server is not None:
            for feature in features:
                try:
                    models[feature] = engines.feature_model(feature)
                except (OSError, engines.EngineError):
                    models[feature] = ""
        STATUS.update(checked=time.monotonic(), server=server, models=models, pending=False)
        _redraw()
        return None

    bpy.app.timers.register(refresh, first_interval=0.0)


def _redraw() -> None:
    wm = bpy.context.window_manager
    for window in wm.windows if wm else ():
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


def stop() -> None:
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    JOBS.clear()
