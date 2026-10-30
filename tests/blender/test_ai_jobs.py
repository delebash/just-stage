# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The UI's AI jobs on the real JustStage server: a job command in two halves (started, then applied when its picture is
ready), followed step by step as the panel's timer does, and cancelled. Headless Blender runs no timers, so the test
steps the follower itself."""

import importlib
import time

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
ai_jobs = importlib.import_module("bl_ext.system.juststage.ui.ai_jobs")


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="AI jobs test")
    api.run("juststage.skin.set_tone", character=result.character)
    yield result, bpy.data.objects[result.object]
    ai_jobs.stop()
    bpy.data.objects.remove(bpy.data.objects[result.object])


def _follow(timeout=180.0):
    deadline = time.monotonic() + timeout
    seen = []
    while ai_jobs.poll_once():
        seen.extend(entry["progress"] for entry in ai_jobs.JOBS.values())
        assert time.monotonic() < deadline, "the job never ended"
        time.sleep(0.25)
    return seen


def test_a_job_command_starts_then_applies_its_picture(human):
    result, obj = human
    cmd = api.command("juststage.skin.add_detail")
    assert cmd.start is not None and cmd.finish is not None
    params, job_id = api.begin(cmd, {"character": result.character, "seed": 3})
    ai_jobs.track(cmd, params, job_id)
    assert ai_jobs.JOBS[job_id]["state"] == "running"
    seen = _follow()
    assert job_id not in ai_jobs.JOBS
    assert ai_jobs.MESSAGES[-1] == "Skin detail (AI): done"
    assert all(0.0 <= p <= 1.0 for p in seen)
    image = bpy.data.images[f"{obj.name} skin detail"]
    assert image["juststage_seed"] == 3


def test_a_cancelled_job_applies_nothing(human):
    result, obj = human
    cmd = api.command("juststage.skin.add_detail")
    images = {i.name for i in bpy.data.images}
    params, job_id = api.begin(cmd, {"character": result.character, "seed": 4})
    ai_jobs.track(cmd, params, job_id)
    ai_jobs.cancel(job_id)
    _follow()
    assert ai_jobs.MESSAGES[-1] == "Skin detail (AI): cancelled"
    assert {i.name for i in bpy.data.images} == images  # no picture applied


def test_the_ai_panel_is_registered():
    assert hasattr(bpy.types, "VIEW3D_PT_juststage_ai")
    assert bpy.ops.juststage.ai_server_start.poll()


def test_a_second_job_waits_behind_the_first(human):
    result, obj = human
    cmd = api.command("juststage.skin.add_detail")
    for seed in (5, 6):
        params, job_id = api.begin(cmd, {"character": result.character, "seed": seed})
        ai_jobs.track(cmd, params, job_id)
    _follow()
    assert ai_jobs.MESSAGES[-2:] == ["Skin detail (AI): done", "Skin detail (AI): done"]
    assert bpy.data.images[f"{obj.name} skin detail"]["juststage_seed"] in (5, 6)
