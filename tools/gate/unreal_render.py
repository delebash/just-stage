# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The realism gate's Unreal render, in the editor window (the card), after tools/gate/unreal_scene.py built the levels
and sequences:

    UnrealEditor.exe .dev/gate/JustStageGate/JustStageGate.uproject -ExecutePythonScript=tools/gate/unreal_render.py

Movie Render Queue (Epic's offline renderer) through the editor's queue subsystem and its play-in-editor executor (a
saved queue asset needs a factory Python doesn't expose - measured 2026-11-04): one job per camera and light variant,
linear EXR with the tone curve off, 16 temporal samples after warm-up frames (Lumen settles), texture streaming off;
the editor quits when the queue is done."""

import json
import os
from pathlib import Path

import unreal

ROOT = Path(r"E:/Dev/3D/just-stage")
GATE = ROOT / ".dev" / "gate"
DEST = "/Game/Gate"
VARIANTS = ("key", "rim", "sky", "stage")
meta = json.loads((GATE / "meta.json").read_text())


def _set(obj, name, value):
    try:
        obj.set_editor_property(name, value)
    except Exception as error:  # a setting this version lacks: logged, the job kept
        unreal.log_warning(f"GATE setting {type(obj).__name__}.{name}: {error}")


subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
queue = subsystem.get_queue()
queue.delete_all_jobs()
ONLY = os.environ.get("GATE_ONLY", "")  # e.g. "face_sky": one job, for a diagnosis
for cam_name in meta["cameras"]:
    w, h = meta["resolution"][cam_name]
    for variant in VARIANTS:
        if ONLY and f"{cam_name}_{variant}" != ONLY:
            continue
        job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        job.set_editor_property("job_name", f"unreal_{cam_name}_{variant}" + os.environ.get("GATE_TAG", ""))
        job.set_editor_property("map", unreal.SoftObjectPath(f"{DEST}/Maps/gate_{variant}"))
        job.set_editor_property("sequence", unreal.SoftObjectPath(f"{DEST}/Seq/seq_{cam_name}"))
        config = job.get_configuration()
        for cls in (unreal.MoviePipelineImageSequenceOutput_JPG, unreal.MoviePipelineImageSequenceOutput_PNG,
                    unreal.MoviePipelineImageSequenceOutput_BMP):
            found = config.find_setting_by_class(cls)
            if found is not None:
                config.remove_setting(found)
        out = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
        _set(out, "output_directory", unreal.DirectoryPath(str(GATE / "renders")))
        _set(out, "output_resolution", unreal.IntPoint(w, h))
        _set(out, "file_name_format", "{job_name}")
        _set(out, "override_existing_output", True)
        config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
        config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_EXR)
        colour = config.find_or_add_setting_by_class(unreal.MoviePipelineColorSetting)
        _set(colour, "disable_tone_curve", True)
        aa = config.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
        _set(aa, "spatial_sample_count", 1)
        _set(aa, "temporal_sample_count", 16)
        _set(aa, "engine_warm_up_count", 120)
        _set(aa, "render_warm_up_count", 32)
        _set(aa, "override_anti_aliasing", True)
        _set(aa, "anti_aliasing_method", unreal.AntiAliasingMethod.AAM_NONE)
        game = config.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting)
        _set(game, "cinematic_quality_settings", True)
        _set(game, "texture_streaming", unreal.MoviePipelineTextureStreamingMethod.DISABLED)
unreal.log(f"GATE queue: {len(queue.get_jobs())} jobs")

EXECUTOR = unreal.MoviePipelinePIEExecutor()


def _finished(executor, success):
    unreal.log(f"GATE render finished, success={success}")
    unreal.SystemLibrary.quit_editor()


EXECUTOR.on_executor_finished_delegate.add_callable(_finished)
#: started from a startup script, play-in-editor ended at once ("PIE Ended while Movie Pipeline was still active",
#: measured 2026-11-04): the queue starts once the editor has ticked for a while
START_AFTER_S = 20.0
_state = {"t": 0.0, "handle": None}


def _tick(dt):
    _state["t"] += dt
    if _state["t"] < START_AFTER_S:
        return
    unreal.unregister_slate_post_tick_callback(_state["handle"])
    unreal.log("GATE render starting")
    subsystem.render_queue_with_executor_instance(EXECUTOR)


_state["handle"] = unreal.register_slate_post_tick_callback(_tick)
