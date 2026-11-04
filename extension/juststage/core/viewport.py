# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""How a JustStage scene is shown, the way CC5 and MetaHuman show a character (docs/plans/2026-11-03-live-view.md):
Material Preview (EEVEE, real time) to move around; Rendered (Cycles on the card, cleaned by the viewport denoiser) to
stop and look at the film look; F12 the film run, in Cycles. Blender's own settings only:

- the card: Cycles' render devices (https://docs.blender.org/manual/en/5.3/render/cycles/gpu_rendering.html). Blender
  ships with no device chosen, which renders on the processor; the template calls `use_gpu` on first start;
- the viewport denoiser (https://docs.blender.org/manual/en/5.3/render/cycles/render_settings/sampling.html);
- Material Preview in the scene's own lights and world
  (https://docs.blender.org/manual/en/5.3/editors/3dview/display/shading.html). Blender opens a saved Rendered view as
  Solid; Material Preview survives a reload (measured on 5.3, RESEARCH §1);
- EEVEE's ray tracing, which the cornea's refraction needs, and curves drawn as strips with their width instead of
  1-px strands (https://docs.blender.org/manual/en/5.3/render/eevee/render_settings/curves.html).
"""

from __future__ import annotations

import bpy

#: per vendor, its ray-tracing back end before its general one: OptiX (NVIDIA RTX) before CUDA; AMD's HIP, Intel's
#: oneAPI, Apple's Metal
GPU_TYPES = ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL")


def _cycles_prefs():
    return bpy.context.preferences.addons["cycles"].preferences


def use_gpu() -> str:
    """Render Cycles on the card: the first back end of GPU_TYPES with a device, all of its devices on and the
    processor off. Returns the back end, or "NONE" when no card is listed (Cycles then renders on the processor)."""
    prefs = _cycles_prefs()
    prefs.refresh_devices()
    for kind in GPU_TYPES:
        if any(d.type == kind for d in prefs.get_devices_for_type(kind)):
            prefs.compute_device_type = kind
            for device in prefs.devices:
                device.use = device.type == kind
            bpy.context.preferences.is_dirty = True  # saved with the preferences
            return kind
    return "NONE"


def setup_scene(scene: bpy.types.Scene) -> None:
    """F12 renders Cycles (the film run) on the card; Rendered is denoised as it refines; EEVEE (Material Preview)
    ray-traces and draws hair as strips. The scene always asks for the card: which card is the preferences' choice
    (`use_gpu`), and with none chosen Cycles renders on the processor - so a scene saved by a run on factory settings
    still renders on the card where JustStage has picked one."""
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    scene.cycles.use_preview_denoising = True
    scene.cycles.preview_denoiser = "AUTO"  # OptiX's denoiser on an RTX card, Open Image Denoise otherwise
    scene.eevee.use_raytracing = True
    # soft shadows sampled finer than Blender's 1 ray / 6 steps: at those the eye white, half shadowed by the lids under
    # a large soft light, came out in grey blotches (round 79, EEVEE close-up; clean at 4 / 16 - measured 2026-11-03)
    scene.eevee.shadow_ray_count, scene.eevee.shadow_step_count = 4, 16
    scene.render.hair_type = "STRIP"


def show_live(screens, camera: bool = False) -> None:
    """Every 3D view in Material Preview, lit by the scene's own lights and world (not the preview studio light);
    `camera` looks through the scene camera."""
    for screen in screens:
        for area in screen.areas:
            if area.type != "VIEW_3D":
                continue
            view = area.spaces.active
            view.shading.type = "MATERIAL"
            view.shading.use_scene_lights = True
            view.shading.use_scene_world = True
            if camera:
                view.region_3d.view_perspective = "CAMERA"
