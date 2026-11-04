# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The realism gate's Unreal scene (local comparison only), built in the editor window after tools/gate/unreal_import.py
(a commandlet can't spawn actors: "SpawnActorFromObject. No actor was spawned", measured 2026-11-04):

    UnrealEditor.exe .dev/gate/JustStageGate/JustStageGate.uproject -ExecutePythonScript=tools/gate/unreal_scene.py

One level per light variant (key, rim, sky, stage - each light alone, then all: light adds linearly, so the engines'
light units are matched afterwards on the grey sphere, tools/gate/compare.py), the character, the grey sphere and a
fixed-exposure post-process volume in each; one level sequence per camera (a spawnable cine camera, Blender's lens and
sensor fit); a Movie Render Queue (Epic's offline renderer, rendered by tools/gate/run_unreal.sh) writing linear EXR
- the tone curve off - so every engine goes through the same AgX afterwards. Blender's metres -> Unreal: (x, -y, z) x 100
(checked on the eyes' imported bounds)."""

import json
import math
from pathlib import Path

import unreal

ROOT = Path(r"E:/Dev/3D/just-stage")
GATE = ROOT / ".dev" / "gate"
DEST = "/Game/Gate"
meta = json.loads((GATE / "meta.json").read_text())
tools = unreal.AssetToolsHelpers.get_asset_tools()
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
mel = unreal.MaterialEditingLibrary
SPHERE = ((0.14, -0.13, 1.60), 0.035, 0.18)  # blender_gate.SPHERE
VARIANTS = ("key", "rim", "sky", "stage")
NOMINAL_CANDELA = {"Key light": 400.0, "Rim light": 160.0}  # any fixed value: the scale is read off the sphere


def ue(v):
    return unreal.Vector(v[0] * 100.0, -v[1] * 100.0, v[2] * 100.0)


def look_at(src, dst):
    d = unreal.Vector(dst.x - src.x, dst.y - src.y, dst.z - src.z)
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    return unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw)


def asset(path, cls, factory):
    folder, name = path.rsplit("/", 1)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    return tools.create_asset(name, folder, cls, factory)


# ---- shared assets ----------------------------------------------------------------------------------------------
hdr_path = f"{DEST}/Textures/studio_small_09_2k"
if not unreal.EditorAssetLibrary.does_asset_exist(hdr_path):
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", meta["hdri"]["file"])
    task.set_editor_property("destination_path", f"{DEST}/Textures")
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    tools.import_asset_tasks([task])
cubemap = unreal.load_asset(hdr_path)
unreal.log(f"GATE hdri: {cubemap.get_class().get_name() if cubemap else None}")

grey = asset(f"{DEST}/Materials/M_gate_grey18", unreal.Material, unreal.MaterialFactoryNew())
c = mel.create_material_expression(grey, unreal.MaterialExpressionConstant3Vector, -300, 0)
c.set_editor_property("constant", unreal.LinearColor(SPHERE[2], SPHERE[2], SPHERE[2], 1.0))
r = mel.create_material_expression(grey, unreal.MaterialExpressionConstant, -300, 200)
r.set_editor_property("r", 1.0)
sp = mel.create_material_expression(grey, unreal.MaterialExpressionConstant, -300, 300)
sp.set_editor_property("r", 0.0)
mel.connect_material_property(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
mel.connect_material_property(sp, "", unreal.MaterialProperty.MP_SPECULAR)
mel.recompile_material(grey)
unreal.EditorAssetLibrary.save_loaded_asset(grey)

body = unreal.load_asset(f"{DEST}/Meshes/gate_body")
eyes = [unreal.load_asset(f"{DEST}/Meshes/{n}") for n in ("Average_man_eyeLeft", "Average_man_eyeRight")]
sphere_mesh = unreal.load_asset("/Engine/BasicShapes/Sphere")  # 100 cm across


def build_level(variant):
    path = f"{DEST}/Maps/gate_{variant}"
    world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    for mesh in [body, *eyes]:
        actors.spawn_actor_from_object(mesh, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    sph = actors.spawn_actor_from_object(sphere_mesh, ue(SPHERE[0]), unreal.Rotator(0, 0, 0))
    sph.set_actor_scale3d(unreal.Vector(1, 1, 1) * (SPHERE[1] * 2 * 100.0 / 100.0))
    sph.static_mesh_component.set_material(0, grey)
    for light in meta["lights"]:
        key = "key" if light["name"].startswith("Key") else "rim"
        if variant not in (key, "stage"):
            continue
        loc = ue(light["location"])
        actor = actors.spawn_actor_from_class(unreal.RectLight, loc, look_at(loc, ue(light["target"])))
        comp = actor.get_component_by_class(unreal.RectLightComponent)
        comp.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS)
        comp.set_editor_property("intensity", NOMINAL_CANDELA[light["name"]])
        comp.set_editor_property("source_width", light["size_m"] * 100.0)
        comp.set_editor_property("source_height", light["size_m"] * 100.0)
        comp.set_editor_property("barn_door_angle", 90.0)
        comp.set_editor_property("attenuation_radius", 2000.0)
        comp.set_editor_property("cast_shadows", True)
        actor.set_actor_label(light["name"])
    if variant in ("sky", "stage"):
        sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 200), unreal.Rotator(0, 0, 0))
        comp = sky.get_component_by_class(unreal.SkyLightComponent)
        comp.set_editor_property("source_type", unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
        comp.set_editor_property("cubemap", cubemap)
        comp.set_editor_property("intensity", 1.0)
        comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        sky.set_actor_label("Image light")
    vol = actors.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0))
    vol.set_editor_property("unbound", True)
    pp = vol.get_editor_property("settings")
    for name, value in (("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL), ("auto_exposure_bias", 0.0),
                        ("auto_exposure_apply_physical_camera_exposure", False), ("bloom_intensity", 0.0),
                        ("vignette_intensity", 0.0), ("film_grain_intensity", 0.0), ("scene_fringe_intensity", 0.0),
                        ("lens_flare_intensity", 0.0), ("motion_blur_amount", 0.0),
                        ("local_exposure_highlight_contrast_scale", 1.0),
                        ("local_exposure_shadow_contrast_scale", 1.0)):
        try:
            pp.set_editor_property("override_" + name, True)
            pp.set_editor_property(name, value)
        except Exception as error:  # a setting missing in this version: logged, the rest kept
            unreal.log_warning(f"GATE post-process {name}: {error}")
    vol.set_editor_property("settings", pp)
    unreal.EditorLoadingAndSavingUtils.save_map(world, path)
    unreal.log(f"GATE level {path}")
    return path


def build_sequence(cam_name):
    cam = meta["cameras"][cam_name]
    w, h = meta["resolution"][cam_name]
    path = f"{DEST}/Seq/seq_{cam_name}"
    seq = asset(path, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(24, 1))
    seq.set_playback_start(0)
    seq.set_playback_end(1)
    loc = ue(cam["location"])
    actor = actors.spawn_actor_from_class(unreal.CineCameraActor, loc, look_at(loc, ue(cam["target"])))
    comp = actor.get_cine_camera_component()
    # Blender's sensor fit AUTO: the 36 mm sensor across the image's larger side
    sw, sh = (36.0, 36.0 * h / w) if w >= h else (36.0 * w / h, 36.0)
    comp.set_editor_property("filmback", unreal.CameraFilmbackSettings(sensor_width=sw, sensor_height=sh))
    comp.set_editor_property("current_focal_length", cam["lens"])
    focus = comp.get_editor_property("focus_settings")
    focus.set_editor_property("focus_method", unreal.CameraFocusMethod.DISABLE)
    comp.set_editor_property("focus_settings", focus)
    binding = seq.add_spawnable_from_instance(actor)
    actors.destroy_actor(actor)
    track = seq.add_track(unreal.MovieSceneCameraCutTrack)
    section = track.add_section()
    section.set_range(0, 1)
    section.set_camera_binding_id(seq.get_binding_id(binding))
    unreal.EditorAssetLibrary.save_loaded_asset(seq)
    unreal.log(f"GATE sequence {path}")
    return path


levels = {v: build_level(v) for v in VARIANTS}
unreal.EditorLoadingAndSavingUtils.new_blank_map(False)  # the cameras are spawned and removed in a scratch map
sequences = {c: build_sequence(c) for c in meta["cameras"]}

queue = asset(f"{DEST}/GateQueue", unreal.MoviePipelineQueue, unreal.MoviePipelineQueueFactory())
for cam_name, seq_path in sequences.items():
    w, h = meta["resolution"][cam_name]
    for variant, level_path in levels.items():
        job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        job.set_editor_property("job_name", f"unreal_{cam_name}_{variant}")
        job.set_editor_property("map", unreal.SoftObjectPath(level_path))
        job.set_editor_property("sequence", unreal.SoftObjectPath(seq_path))
        config = job.get_configuration()
        out = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
        out.set_editor_property("output_directory", unreal.DirectoryPath(str(GATE / "renders")))
        out.set_editor_property("output_resolution", unreal.IntPoint(w, h))
        out.set_editor_property("file_name_format", "{job_name}")
        out.set_editor_property("override_existing_output", True)
        config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
        config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_EXR)
        colour = config.find_or_add_setting_by_class(unreal.MoviePipelineColorSetting)
        colour.set_editor_property("disable_tone_curve", True)
        aa = config.find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)
        aa.set_editor_property("spatial_sample_count", 1)
        aa.set_editor_property("temporal_sample_count", 16)
        aa.set_editor_property("engine_warm_up_count", 120)
        aa.set_editor_property("render_warm_up_count", 32)
        aa.set_editor_property("override_anti_aliasing", True)
        aa.set_editor_property("anti_aliasing_method", unreal.AntiAliasingMethod.AAM_NONE)
        game = config.find_or_add_setting_by_class(unreal.MoviePipelineGameOverrideSetting)
        game.set_editor_property("cinematic_quality_settings", True)
        game.set_editor_property("texture_streaming", unreal.MoviePipelineTextureStreamingMethod.DISABLED)
unreal.EditorAssetLibrary.save_loaded_asset(queue)
unreal.log(f"GATE queue {queue.get_path_name()} with {len(queue.get_jobs())} jobs")
unreal.SystemLibrary.quit_editor()  # run in the editor window (actors can't be spawned in a commandlet)
