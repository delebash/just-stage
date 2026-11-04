# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The realism gate's Unreal import (local comparison only; nothing of MetaHuman's leaves the gate project). Run as a
commandlet without the card:

    UnrealEditor-Cmd.exe .dev/gate/JustStageGate/JustStageGate.uproject -run=pythonscript
        -script=tools/gate/unreal_import.py -nullrhi -unattended

Imports tools/gate/blender_gate.py's FBX and content maps, makes one instance of MetaHuman's baked skin material per
UDIM tile (`M_skin_unified_baked`: "Use Baked Material" and "Use Micro Skin Details" on, our maps in its baked and
micro slots, the micro masks uniform), a plain placeholder material for the eyes, and writes the imported bounds for
the axis check (`.dev/gate/out/unreal_bounds.json`)."""

import json
from pathlib import Path

import unreal

ROOT = Path(r"E:/Dev/3D/just-stage")
GATE = ROOT / ".dev" / "gate"
CONTENT = GATE / "content"
DEST = "/Game/Gate"
PARENT = "/MetaHumanCharacter/Lookdev_UHM/Skin/Materials/M_skin_unified_baked"
TILES = (1001, 1002, 1003, 1004, 1005)

tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
meta = json.loads((GATE / "meta.json").read_text())


def _import(files, destination, options=None):
    tasks = []
    for f in files:
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", str(f))
        task.set_editor_property("destination_path", destination)
        task.set_editor_property("automated", True)
        task.set_editor_property("replace_existing", True)
        task.set_editor_property("save", True)
        if options is not None:
            task.set_editor_property("options", options)
        tasks.append(task)
    tools.import_asset_tasks(tasks)
    return [p for t in tasks for p in t.get_editor_property("imported_object_paths")]


def _texture(path, srgb, compression, flip_green=False):
    tex = unreal.load_asset(path)
    tex.set_editor_property("srgb", srgb)
    tex.set_editor_property("compression_settings", compression)
    tex.set_editor_property("flip_green_channel", flip_green)
    unreal.EditorAssetLibrary.save_loaded_asset(tex)
    return tex


# ---- textures ---------------------------------------------------------------------------------------------------
textures = {}
for tile in TILES:
    for kind in ("base", "normal", "srmf", "scatter"):
        textures[(kind, tile)] = _import([CONTENT / f"{kind}.{tile}.png"], f"{DEST}/Textures")[0]
for name in ("micro_normal", "micro_cavity", "white"):
    textures[name] = _import([CONTENT / f"{name}.png"], f"{DEST}/Textures")[0]
TC = unreal.TextureCompressionSettings
for tile in TILES:
    _texture(textures[("base", tile)], True, TC.TC_DEFAULT)
    _texture(textures[("normal", tile)], False, TC.TC_NORMALMAP, flip_green=True)  # ours OpenGL, Unreal DirectX
    _texture(textures[("srmf", tile)], False, TC.TC_MASKS)
    _texture(textures[("scatter", tile)], False, TC.TC_MASKS)
_texture(textures["micro_normal"], False, TC.TC_NORMALMAP, flip_green=True)
_texture(textures["micro_cavity"], False, TC.TC_MASKS)
_texture(textures["white"], False, TC.TC_MASKS)

# ---- the skin's material instances, one per tile ----------------------------------------------------------------
parent = unreal.load_asset(PARENT)
instances = {}
for tile in TILES:
    name = f"MI_gate_skin_{tile}"
    path = f"{DEST}/Materials/{name}"
    mi = unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else tools.create_asset(
        name, f"{DEST}/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, parent)
    for switch, on in (("Use Baked Material", True), ("Use Micro Skin Details", True), ("Use Virtual Texture", False),
                       ("Use Animated Maps", False)):
        mel.set_material_instance_static_switch_parameter_value(mi, switch, on)
    for param, key in (("Basecolor Baked", ("base", tile)), ("Normal Baked", ("normal", tile)),
                       ("SRMF Baked", ("srmf", tile)), ("Scatter Baked", ("scatter", tile)),
                       ("Micro Skin Details Normal", "micro_normal"), ("Micro Skin Details Cavity", "micro_cavity"),
                       ("Micro Skin Details Mask", "white")):
        mel.set_material_instance_texture_parameter_value(mi, param, unreal.load_asset(textures[key]))
    info = meta["tiles"][str(tile)]
    for param, value in (("UDIM", float(tile)), ("Texture Size", float(info["size"])),
                         ("Micro Skin Tiling", float(info["micro_tiling"])), ("Micro MaskA Strength", 1.0),
                         ("Micro MaskB Strength", 1.0), ("Micro MaskC Strength", 1.0), ("Micro MaskD Strength", 1.0)):
        mel.set_material_instance_scalar_parameter_value(mi, param, value)
    mel.update_material_instance(mi)
    unreal.EditorAssetLibrary.save_loaded_asset(mi)
    instances[tile] = mi

# ---- the eyes' placeholder: flat colours from the eye shader's own settings (blender_gate.py eyes), cornea hidden --
def _param_material(path, masked=False):
    folder, name = path.rsplit("/", 1)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    mat = tools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
    colour = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -400, 0)
    colour.set_editor_property("parameter_name", "Colour")
    rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 200)
    rough.set_editor_property("r", 0.06)
    mel.connect_material_property(colour, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    if masked:
        mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
        zero = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 400)
        zero.set_editor_property("r", 0.0)
        mel.connect_material_property(zero, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat


eye_base = _param_material(f"{DEST}/Materials/M_gate_eye_placeholder")
cornea = _param_material(f"{DEST}/Materials/M_gate_cornea_hidden", masked=True)
eye_mats = {"Cornea": cornea}
for part, rgb in meta.get("eye_colours", {}).items():
    name = f"MI_gate_eye_{part}"
    path = f"{DEST}/Materials/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    mi = tools.create_asset(name, f"{DEST}/Materials", unreal.MaterialInstanceConstant,
                            unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, eye_base)
    mel.set_material_instance_vector_parameter_value(mi, "Colour", unreal.LinearColor(*rgb, 1.0))
    unreal.EditorAssetLibrary.save_loaded_asset(mi)
    eye_mats[part] = mi

# ---- the mesh ---------------------------------------------------------------------------------------------------
ui = unreal.FbxImportUI()
ui.set_editor_property("import_mesh", True)
ui.set_editor_property("import_as_skeletal", False)
ui.set_editor_property("import_materials", False)
ui.set_editor_property("import_textures", False)
ui.set_editor_property("import_animations", False)
ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
smd = ui.get_editor_property("static_mesh_import_data")
smd.set_editor_property("combine_meshes", False)
smd.set_editor_property("generate_lightmap_u_vs", False)
smd.set_editor_property("auto_generate_collision", False)
smd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
smd.set_editor_property("transform_vertex_to_absolute", True)
meshes = _import([GATE / "gate_body.fbx"], f"{DEST}/Meshes", ui)
bounds = {}
for eye_path in (f"{DEST}/Meshes/Average_man_eyeLeft", f"{DEST}/Meshes/Average_man_eyeRight"):
    if eye_path not in meshes and unreal.EditorAssetLibrary.does_asset_exist(eye_path):
        meshes.append(eye_path)  # imported by an earlier run of this script, still to get today's materials
for path in meshes:
    asset = unreal.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        continue
    box = asset.get_bounding_box()
    bounds[asset.get_name()] = {"min": [box.min.x, box.min.y, box.min.z], "max": [box.max.x, box.max.y, box.max.z],
                                "slots": [str(m.get_editor_property("material_slot_name"))
                                          for m in asset.get_editor_property("static_materials")]}
    if asset.get_name().startswith("gate_body"):
        for k, m in enumerate(asset.get_editor_property("static_materials")):
            slot = str(m.get_editor_property("material_slot_name"))
            tile = next((t for t in TILES if str(t) in slot), None)
            if tile is not None:
                asset.set_material(k, instances[tile])
    else:
        for k, m in enumerate(asset.get_editor_property("static_materials")):
            slot = str(m.get_editor_property("material_slot_name"))
            part = next((p for p in eye_mats if p in slot), None)
            asset.set_material(k, eye_mats.get(part, eye_base))
    unreal.EditorAssetLibrary.save_loaded_asset(asset)
(GATE / "out" / "unreal_bounds.json").write_text(json.dumps(bounds, indent=1))
unreal.log("GATE imported: " + ", ".join(bounds))
