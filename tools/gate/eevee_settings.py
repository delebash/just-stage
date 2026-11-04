# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Rec 16's measurements on the gate scene (the review brief §10: "rec 16's EEVEE measurements beside it"): each EEVEE
setting changed alone from today's, rendered on the face camera, measured against Cycles' render of the same scene
(the film render is the live view's oracle - AGENTS.md) on the gate's crops and the grey sphere.

    python tools/dev.py blender -b --python tools/gate/eevee_settings.py        # the card
    python tools/dev.py blender -b --python tools/gate/eevee_settings.py -- report

Blender's own settings only (scene.eevee, its ray-tracing options, the skin material's own inputs); no setting is
kept by this script - the verdict goes to the realism working doc."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / ".dev" / "gate"
OUT = GATE / "eevee16"
sys.path.insert(0, str(Path(__file__).parent))
gate = importlib.import_module("blender_gate")
cmp = importlib.import_module("compare")
startup = importlib.import_module("bl_ext.system.juststage.ui.startup")


def _skin(scene):
    body = next(o for o in scene.objects if o.juststage.character_id and not o.juststage.part_of)
    return next(n for n in body.juststage.skin_material.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def _set(scene, variant):
    e, rt, bsdf = scene.eevee, scene.eevee.ray_tracing_options, _skin(scene)
    if variant == "trace_rough_0.75":
        rt.trace_max_roughness = 0.75
    elif variant == "trace_res_full":
        rt.resolution_scale = "1"
    elif variant == "fast_gi_fine":
        e.fast_gi_resolution, e.fast_gi_ray_count, e.fast_gi_step_count = "1", 4, 16
    elif variant == "indirect_1.2":
        e.indirect_light_intensity = 1.2
    elif variant == "no_sheen":
        bsdf.inputs["Sheen Weight"].default_value = 0.0
    elif variant == "no_coat":
        coat = bsdf.inputs["Coat Weight"]
        tree = bsdf.id_data
        for link in list(coat.links):
            tree.links.remove(link)
        coat.default_value = 0.0
    elif variant == "sss_x1.5":
        bsdf.inputs["Subsurface Scale"].default_value *= 1.5
    elif variant == "samples_128":
        e.taa_render_samples = 128


VARIANTS = ("base", "trace_rough_0.75", "trace_res_full", "fast_gi_fine", "indirect_1.2", "no_sheen", "no_coat",
            "sss_x1.5", "samples_128")


def render() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for variant in VARIANTS:
        bpy.ops.wm.open_mainfile(filepath=str(GATE / "gate_scene.blend"))
        scene = bpy.context.scene
        gate._grey_sphere(scene)
        scene.render.engine = "BLENDER_EEVEE"
        scene.camera = scene.objects["face camera"]
        scene.render.resolution_x, scene.render.resolution_y = gate.RESOLUTION["face"]
        s = scene.render.image_settings
        s.file_format, s.color_depth, s.exr_codec = "OPEN_EXR", "32", "ZIP"
        _set(scene, variant)
        world = scene.world.node_tree.nodes
        lights = [o for o in scene.objects if o.type == "LIGHT"]
        for light_set in ("stage", "sky"):
            for light in lights:
                light.hide_render = light_set == "sky"
            world["image light"].inputs["Strength"].default_value = startup.HDRI_STRENGTH
            scene.render.filepath = str(OUT / f"{variant}_{light_set}.exr")
            import time
            t = time.perf_counter()
            bpy.ops.render.render(write_still=True)
            print(f"GATE16 {variant} {light_set} {time.perf_counter() - t:.1f}s", flush=True)


def report() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(GATE / "gate_scene.blend"))
    centre, radius = cmp._sphere_disc("face", gate.RESOLUTION["face"])
    ref = {v: cmp._load(GATE / "renders" / f"cycles_face_{v}.exr") for v in ("stage", "sky")}
    ref_crops = {c: cmp._numbers(cmp._crop(ref["stage"], f)) for c, f in cmp.CROPS.items()}
    rows = {}
    for variant in VARIANTS:
        stage, sky = (cmp._load(OUT / f"{variant}_{l}.exr") for l in ("stage", "sky"))
        if stage is None:
            continue
        crops = {c: cmp._numbers(cmp._crop(stage, f)) for c, f in cmp.CROPS.items()}
        rows[variant] = {
            "sky_sphere_vs_cycles": cmp._sphere_mean(sky, centre, radius) / cmp._sphere_mean(ref["sky"], centre, radius),
            "crop_mean_err": float(np.mean([abs(np.log(crops[c]["mean"] / ref_crops[c]["mean"])) for c in crops])),
            "crop_detail_err": float(np.mean([abs(np.log(crops[c]["fine_detail"] / ref_crops[c]["fine_detail"]))
                                              for c in crops])),
            "jaw_mean_ratio": crops["jaw_shadow"]["mean"] / ref_crops["jaw_shadow"]["mean"],
            "jaw_detail_ratio": crops["jaw_shadow"]["fine_detail"] / ref_crops["jaw_shadow"]["fine_detail"],
            "under_eye_detail_ratio": crops["under_eye"]["fine_detail"] / ref_crops["under_eye"]["fine_detail"],
        }
    (OUT / "report.json").write_text(json.dumps(rows, indent=1))
    for v, r in rows.items():
        print("GATE16", v.ljust(17), {k: round(x, 3) for k, x in r.items()})


if __name__ == "__main__":
    step = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "render"
    {"render": render, "report": report}[step]()
