"""Gate step: list the parameters of MetaHuman's baked skin material (names, defaults) - read only."""
import json
import unreal

OUT = r"E:/Dev/3D/just-stage/.dev/gate/out/m_skin_unified_baked.json"
lib = unreal.MaterialEditingLibrary
result = {}
for path in ["/MetaHumanCharacter/Lookdev_UHM/Skin/Materials/M_skin_unified_baked",
             "/MetaHumanCharacter/Lookdev_UHM/Skin/Materials/MI_skin_unified_MH_preset_Baked"]:
    asset = unreal.load_asset(path)
    entry = {"class": asset.get_class().get_name() if asset else None}
    if isinstance(asset, unreal.Material):
        entry["textures"] = {str(n): str(lib.get_material_default_texture_parameter_value(asset, n))
                             for n in lib.get_texture_parameter_names(asset)}
        entry["scalars"] = {str(n): lib.get_material_default_scalar_parameter_value(asset, n)
                            for n in lib.get_scalar_parameter_names(asset)}
        entry["switches"] = {str(n): lib.get_material_default_static_switch_parameter_value(asset, n)
                             for n in lib.get_static_switch_parameter_names(asset)}
        entry["vectors"] = [str(n) for n in lib.get_vector_parameter_names(asset)]
        entry["shading_model"] = str(asset.get_editor_property("shading_model"))
    elif isinstance(asset, unreal.MaterialInstanceConstant):
        entry["parent"] = str(asset.get_editor_property("parent").get_path_name())
        entry["textures"] = {str(p.parameter_info.name): str(p.parameter_value)
                             for p in asset.get_editor_property("texture_parameter_values")}
        entry["scalars"] = {str(p.parameter_info.name): p.parameter_value
                            for p in asset.get_editor_property("scalar_parameter_values")}
    result[path] = entry
json.dump(result, open(OUT, "w"), indent=1, default=str)
unreal.log("GATE dump written: " + OUT)
