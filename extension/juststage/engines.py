# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's side of its AI server (docs/standards/ai-engines.md §3).

JustStage's server (`server/`: the web kit's template server, copied, with the image engine on) listens on
127.0.0.1:17481; this module finds it, starts it when it isn't running, and runs image jobs on it over the kit's
routes — submit
(`POST /v1/ai/image/jobs`), progress (`GET /v1/jobs/:id`), cancel (`DELETE /v1/jobs/:id`), the picture once
(`GET /v1/ai/image/jobs/:id/result`). Python's standard library only.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PORT = 17481  # server/src/version.js DEFAULT_PORT
BASE = f"http://127.0.0.1:{PORT}"
START_SECONDS = 60


class EngineError(Exception):
    """The AI server refused or failed — its own words, and what it needs first when it says (`need`)."""

    def __init__(self, message: str, need: str = ""):
        super().__init__(message)
        self.need = need


def _call(method: str, path: str, body: dict | None = None, timeout: float = 30.0) -> tuple[bytes, str]:
    data = json.dumps(body).encode() if body is not None else None
    headers = {"content-type": "application/json"}
    request = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(), response.headers.get("content-type", "")
    except urllib.error.HTTPError as e:  # the kit's problem+json: title, detail, need
        try:
            problem = json.loads(e.read())
        except ValueError:
            problem = {}
        words = problem.get("detail") or problem.get("title") or str(e)
        raise EngineError(f"JustStage's server: {words}", problem.get("need", "")) from None


def _json(method: str, path: str, body: dict | None = None) -> dict:
    return json.loads(_call(method, path, body)[0])


def health() -> dict | None:
    """The server's health, or None when nothing answers on its port."""
    try:
        return _json("GET", "/v1/health")
    except (OSError, EngineError):
        return None


def server_dir() -> Path:
    """Where JustStage's server's code is: `JUSTSTAGE_SERVER_DIR`, else `server/` in the checkout (`JUSTSTAGE_ROOT`)."""
    for key, sub in (("JUSTSTAGE_SERVER_DIR", ""), ("JUSTSTAGE_ROOT", "server")):
        if os.environ.get(key):
            path = Path(os.environ[key]) / sub
            if (path / "src" / "serve.js").exists():
                return path
    raise EngineError("JustStage's server isn't on this computer (no server/src/serve.js)")


def ensure_running(data_dir: Path) -> dict:
    """The server's health — started first when it isn't running, its data in `data_dir`."""
    found = health()
    if found is not None:
        return found
    node = os.environ.get("JUSTSTAGE_NODE") or shutil.which("node")
    if not node:
        raise EngineError("JustStage's server needs Node, and none was found")
    data_dir.mkdir(parents=True, exist_ok=True)
    flags = 0
    if sys.platform == "win32":  # it outlives the Blender that started it, without a console window
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    with open(data_dir / "serve.log", "ab") as log:
        subprocess.Popen(
            [node, str(Path("src") / "serve.js"), "serve"],
            cwd=server_dir(),
            env={**os.environ, "JUST_STAGE_DATA_DIR": str(data_dir)},
            stdout=log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            creationflags=flags,
            start_new_session=sys.platform != "win32",
        )
    deadline = time.monotonic() + START_SECONDS
    while time.monotonic() < deadline:
        found = health()
        if found is not None:
            return found
        time.sleep(0.5)
    raise EngineError(f"JustStage's server didn't start within {START_SECONDS} s (its log: {data_dir / 'serve.log'})")


def feature_model(feature: str) -> str:
    """The model a feature runs with — its preset's, as the server's routing has it."""
    preset_id = _json("GET", "/v1/ai/preset-assignments").get("features", {}).get(feature, "")
    for row in _json("GET", "/v1/ai/engine-presets?kind=image").get("presets", []):
        if row.get("id") == preset_id:
            return row.get("model", "")
    return ""


def submit_image(feature: str, prompt: str, width: int, height: int, seed: int) -> dict:
    """Start an image job; the job's snapshot. Refused at once (EngineError with `need`) when it can't run yet."""
    request = {"prompt": prompt, "width": width, "height": height, "seed": seed}
    return _json("POST", "/v1/ai/image/jobs", {"feature": feature, "request": request})


def job(job_id: str) -> dict:
    return _json("GET", f"/v1/jobs/{job_id}")


def cancel(job_id: str) -> None:
    _call("DELETE", f"/v1/jobs/{job_id}")


def result(job_id: str) -> bytes:
    """The finished picture (PNG) — once: the server forgets it after."""
    return _call("GET", f"/v1/ai/image/jobs/{job_id}/result", timeout=120.0)[0]


def run_image(feature: str, prompt: str, width: int, height: int, seed: int, timeout: float = 900.0) -> bytes:
    """Submit, wait, fetch — the headless way (the UI follows the job itself)."""
    snapshot = submit_image(feature, prompt, width, height, seed)
    deadline = time.monotonic() + timeout
    while snapshot["state"] not in ("done", "error", "cancelled"):
        if time.monotonic() > deadline:
            cancel(snapshot["id"])
            raise EngineError(f"{feature} took longer than {timeout:.0f} s and was cancelled")
        time.sleep(0.5)
        snapshot = job(snapshot["id"])
    if snapshot["state"] != "done":
        error = snapshot.get("error") or {}
        raise EngineError(f"{feature}: {error.get('message', snapshot['state']) if isinstance(error, dict) else error}")
    return result(snapshot["id"])
