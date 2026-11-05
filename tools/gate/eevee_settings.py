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
from mathutils import Vector

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
    elif variant.startswith("both_sss_"):  # the two that helped, together: indirect x1.2 and an SSS scale sweep
        e.indirect_light_intensity = 1.2
        bsdf.inputs["Subsurface Scale"].default_value *= float(variant.split("_")[-1])
    # World sun extraction (Blender's tooltip: "If non-zero, the maximum value for world contribution that will be
    # recorded inside the world light probe. The excess contribution is converted to a sun light"); today 10, and Studio
    # Small 09 peaks at 135 after its strength - x1.2 was dropped (the sphere's bands, the realism doc §6a)
    elif variant.startswith("sun_thr_"):
        scene.world.sun_threshold = float(variant.split("_")[-1])
    elif variant.startswith("sun_angle_"):
        scene.world.sun_angle = np.radians(float(variant.split("_")[-1]))
    elif variant == "sun_no_shadow":
        scene.world.use_sun_shadow = False
    elif variant.startswith("sss_x"):  # skin scattering alone (x2.5 was measured with x1.2 - void)
        bsdf.inputs["Subsurface Scale"].default_value *= float(variant[len("sss_x"):])
    elif variant.startswith(("probe_fine_sss_", "probe_fine_world_sss_")):  # the two causes' fixes together
        _probe_volume(scene, capture_world="_world_" in variant, resolution=(24, 20, 36))
        bsdf.inputs["Subsurface Scale"].default_value *= float(variant.split("_")[-1])
    elif variant.startswith("probe_volume"):
        _probe_volume(scene, capture_world=variant.endswith("_world"),
                      resolution=(24, 20, 36) if "_fine" in variant else (12, 10, 18))


def _probe_volume(scene, capture_world: bool, resolution=(12, 10, 18)) -> None:
    """A light-probe volume around the head and torso, baked (Blender's own way to add bounce and occlusion to EEVEE:
    the jaw shadow's suspect is the missing bounce from the chest and neck - the realism doc §6a). Blender's defaults
    (`capture_indirect` on, `capture_world` off: the world as visibility only) unless `capture_world`."""
    body = next(o for o in scene.objects if o.juststage.character_id and not o.juststage.part_of)
    corners = np.array([body.matrix_world @ Vector(c) for c in body.bound_box])
    top, centre = corners[:, 2].max(), corners.mean(axis=0)
    data = bpy.data.lightprobes.new("bounce", "VOLUME")
    data.resolution_x, data.resolution_y, data.resolution_z = resolution  # 12 x 10 x 18 (~5 cm) was too coarse
    data.capture_world = capture_world
    probe = bpy.data.objects.new("bounce", data)
    scene.collection.objects.link(probe)
    probe.location = (centre[0], centre[1], top - 0.36)  # head and shoulders down to mid-chest
    probe.scale = (0.32, 0.26, 0.40)  # the volume spans -1..1 in its own space
    for obj in scene.objects:
        obj.select_set(False)
    probe.select_set(True)
    bpy.context.view_layer.objects.active = probe
    import time
    t = time.perf_counter()
    bpy.ops.object.lightprobe_cache_bake(subset="ACTIVE")
    print(f"GATE16 probe bake {time.perf_counter() - t:.1f}s capture_world={capture_world}", flush=True)


VARIANTS = ("base", "trace_rough_0.75", "trace_res_full", "fast_gi_fine", "indirect_1.2", "no_sheen", "no_coat",
            "sss_x1.5", "samples_128", "both_sss_1.5", "both_sss_2.0", "both_sss_2.5",
            "sun_thr_0", "sun_thr_5", "sun_thr_2", "sun_thr_1", "sun_angle_10", "sun_angle_30", "sun_no_shadow",
            "sss_x2", "sss_x2.5", "sss_x3", "probe_volume", "probe_volume_world", "probe_volume_fine",
            "probe_fine_sss_2.5", "probe_fine_sss_3", "probe_volume_fine_world", "probe_fine_world_sss_3")
#: `-- render <names...>` renders only those (the first round's are on disk)


def render() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    args = sys.argv[sys.argv.index("--") + 2:] if "--" in sys.argv else []
    for variant in args or VARIANTS:
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


def _sphere_bands(img, centre, radius) -> list[float]:
    """The grey sphere's mean in five brightness bands, dark to lit (the lit side alone hid a flat world light -
    measured 2026-11-04: x1.2 matched the lit fifth and left the dark side ~50% too bright)."""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    lum = img[np.hypot(xx - centre[0], yy - centre[1]) < 0.95 * radius] @ cmp.LUMA
    qs = np.quantile(lum, [0, .2, .4, .6, .8, 1.0])
    return [float(lum[(lum >= qs[i]) & (lum <= qs[i + 1])].mean()) for i in range(5)]


def report() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(GATE / "gate_scene.blend"))
    centre, radius = cmp._sphere_disc("face", gate.RESOLUTION["face"])
    ref = {v: cmp._load(GATE / "renders" / f"cycles_face_{v}.exr") for v in ("stage", "sky")}
    ref_bands = _sphere_bands(ref["sky"], centre, radius)
    ref_crops = {c: cmp._numbers(cmp._crop(ref["stage"], f)) for c, f in cmp.CROPS.items()}
    rows = {}
    for variant in VARIANTS:
        stage, sky = (cmp._load(OUT / f"{variant}_{l}.exr") for l in ("stage", "sky"))
        if stage is None:
            continue
        crops = {c: cmp._numbers(cmp._crop(stage, f)) for c, f in cmp.CROPS.items()}
        bands = [b / r for b, r in zip(_sphere_bands(sky, centre, radius), ref_bands)]
        rows[variant] = {
            "sky_sphere_vs_cycles": cmp._sphere_mean(sky, centre, radius) / cmp._sphere_mean(ref["sky"], centre, radius),
            "sky_bands_vs_cycles": bands,
            "sky_bands_err": float(np.mean([abs(np.log(b)) for b in bands])),
            "crop_mean_err": float(np.mean([abs(np.log(crops[c]["mean"] / ref_crops[c]["mean"])) for c in crops])),
            "crop_detail_err": float(np.mean([abs(np.log(crops[c]["fine_detail"] / ref_crops[c]["fine_detail"]))
                                              for c in crops])),
            "jaw_mean_ratio": crops["jaw_shadow"]["mean"] / ref_crops["jaw_shadow"]["mean"],
            "jaw_detail_ratio": crops["jaw_shadow"]["fine_detail"] / ref_crops["jaw_shadow"]["fine_detail"],
            "under_eye_detail_ratio": crops["under_eye"]["fine_detail"] / ref_crops["under_eye"]["fine_detail"],
        }
    (OUT / "report.json").write_text(json.dumps(rows, indent=1))
    for v, r in rows.items():
        print("GATE16", v.ljust(17), {k: [round(y, 3) for y in x] if isinstance(x, list) else round(x, 3)
                                      for k, x in r.items()})


if __name__ == "__main__":
    step = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "render"
    {"render": render, "report": report}[step]()
