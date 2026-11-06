# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""How JustStage starts (docs/plans/2026-11-03-cc5-window.md §3 step 5), called by the application template: a new
file is a stage - Blender's default cube gone, its camera framing a standing person, Blender's one point light (it
stands behind where the character stands: the face came out dark) replaced by a portrait light - the research's
technique (`docs/plans/2026-10-30-research-skin-detail-shading.md` §4): one large soft key at 30-45 degrees, a rim
behind (the scattering at the ears and nostrils), the fill from a studio image light - over a dark stage, as CC5's view
(the realism working doc, `docs/plans/2026-11-04-realism.md` rec 3); the
Properties editor becomes the Content panel (Blender's Asset Browser); the
3D view's sidebar opens on JustStage's Modify panel. Blender's own settings only:
https://docs.blender.org/api/5.3/bpy.types.Region.html#bpy.types.Region.active_panel_category ("categories are generated
at runtime, so list may be empty at initialization, before any drawing took place" - hence the retries)."""

from __future__ import annotations

import bpy
from mathutils import Vector

CATEGORY = "JustStage"
#: the camera on a new stage: 4.2 m in front at chest height, a 50 mm lens - a whole standing person in frame
CAMERA_AT, CAMERA_LOOKS_AT, LENS = Vector((0.0, -4.2, 1.0)), Vector((0.0, 0.0, 0.92)), 50.0
#: where the lights aim: a standing person's chest-to-head
LIGHTS_LOOK_AT = Vector((0.0, 0.0, 1.35))
#: (name, location, power in watts, size in metres): the key 45 degrees to the camera's left and 35 up, 3 m off; the
#: rim behind and above (the character faces -Y). No fill light: the image light fills (an area fill at a third of the
#: key left the face flat and pale - trials 2026-11-04, `light_sheet*.png` in the realism working doc)
LIGHTS = (
    ("Key light", Vector((-1.74, -1.74, 3.07)), 300.0, 1.5),
    ("Rim light", Vector((-1.0, 2.2, 3.0)), 120.0, 1.0),  # 250 W turned the hair's edge white in the live view
)
#: the image light (Poly Haven's CC0 "Studio Small 09", fetched by tools/fetch_data.py) at a quarter: a soft fill
#: (at a half it flattened the face again); the camera sees a dark blue-grey stage instead (Blender's Light Path
#: "Is Camera Ray"), as CC5's view
HDRI = ("hdri", "studio_small_09_2k.hdr")
HDRI_STRENGTH = 0.25
BACKDROP = (0.018, 0.022, 0.03)
WORLD = "JustStage stage"


#: the finest shadow texel (m): the lid stands about a millimetre off the eyeball, Blender's 1 mm can't resolve its
#: shadow; EEVEE's virtual shadow maps refine only where the view needs it (0.56 s for a close eye either way, measured)
SHADOW_TEXEL = 0.0001


def set_fine_shadows(light) -> None:
    """Jittered soft shadows down to SHADOW_TEXEL: the lids' contact shadow on the eye white (measured 2026-11-04)."""
    light.use_shadow_jitter = True
    light.shadow_maximum_resolution = SHADOW_TEXEL


def new_stage(scene) -> None:
    """Blender's default cube and point light out; its camera aimed at where a JustStage character stands, studio
    lights on it."""
    cube = bpy.data.objects.get("Cube")
    if cube is not None and cube.type == "MESH" and len(cube.data.vertices) == 8:
        bpy.data.objects.remove(cube)
    light = bpy.data.objects.get("Light")
    if light is not None and light.type == "LIGHT" and light.data.type == "POINT":  # Blender's factory light
        bpy.data.objects.remove(light)
    for name, location, power, size in LIGHTS:
        if scene.objects.get(name) is not None:
            continue
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.size = power, size
        set_fine_shadows(data)
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (LIGHTS_LOOK_AT - location).to_track_quat("-Z", "Y").to_euler()
    stage_world(scene)
    cam = scene.camera
    if cam is not None:
        cam.location = CAMERA_AT
        cam.rotation_euler = (CAMERA_LOOKS_AT - CAMERA_AT).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = LENS


def stage_world(scene) -> bpy.types.World:
    """The stage's world: the studio image lights the character, camera rays see the dark stage."""
    from .. import paths

    world = bpy.data.worlds.get(WORLD) or bpy.data.worlds.new(WORLD)
    scene.world = world
    nt = world.node_tree
    nt.nodes.clear()
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(paths.FETCHED.joinpath(*HDRI)), check_existing=True)
    lit, stage = nt.nodes.new("ShaderNodeBackground"), nt.nodes.new("ShaderNodeBackground")
    lit.name, stage.name = "image light", "stage"
    lit.inputs["Strength"].default_value = HDRI_STRENGTH
    stage.inputs["Color"].default_value = (*BACKDROP, 1.0)
    path, mix, out = (nt.nodes.new(t) for t in ("ShaderNodeLightPath", "ShaderNodeMixShader", "ShaderNodeOutputWorld"))
    nt.links.new(env.outputs["Color"], lit.inputs["Color"])
    nt.links.new(path.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(lit.outputs["Background"], mix.inputs[1])
    nt.links.new(stage.outputs["Background"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    from ..modules.hair import hair_shading

    hair_shading.sync_world(scene)  # the live view's hair: its image-light term from this world
    return world


def stage_view(screens) -> None:
    """The 3D views show the character, not the stage's workings: Blender's "extras" overlay (the lights' and
    camera's outlines and their direction lines) off, as CC5's and MetaHuman's viewports show none. The lights stay in
    the Scene list; the overlay popover brings the outlines back."""
    for screen in screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.overlay.show_extras = False


def content_panel(screens) -> None:
    """Every Properties editor becomes the Content panel: Blender's Asset Browser."""
    for screen in screens:
        for area in screen.areas:
            if area.type == "PROPERTIES":
                area.type = "FILE_BROWSER"
                area.ui_type = "ASSETS"
            if area.type == "FILE_BROWSER" and area.ui_type == "ASSETS":
                params = getattr(area.spaces.active, "params", None)  # none until the browser has drawn once
                if params is not None and hasattr(params, "asset_library_reference"):
                    try:
                        params.asset_library_reference = "JustStage"  # core/library.py's NAME
                    except TypeError:  # the library isn't registered in these preferences
                        pass


def open_sidebar(retries: int = 15) -> None:
    """The 3D views' sidebars open, on the JustStage tab, once they have drawn their tabs."""
    left = [retries]

    def attempt():
        done = True
        wm = bpy.context.window_manager
        full = getattr(wm, "juststage_full_interface", True)
        for window in wm.windows:
            for area in window.screen.areas:
                if area.type == "FILE_BROWSER" and area.ui_type == "ASSETS":  # the Content panel on JustStage's library
                    params = getattr(area.spaces.active, "params", None)
                    if params is None:
                        done = False  # not drawn yet
                    elif getattr(params, "asset_library_reference", "JustStage") != "JustStage":
                        try:
                            params.asset_library_reference = "JustStage"
                        except TypeError:  # the library isn't registered in these preferences
                            pass
                    continue
                if area.type != "VIEW_3D":
                    continue
                space = area.spaces.active
                space.show_region_ui = True
                space.show_region_toolbar = space.show_region_tool_header = full  # Blender's tools (topbar.py)
                region = next((r for r in area.regions if r.type == "UI"), None)
                if region is None:
                    continue
                try:
                    region.active_panel_category = CATEGORY
                except (TypeError, AttributeError):  # not drawn yet: no tabs, and the setting is read-only until then
                    done = False
                area.tag_redraw()
        left[0] -= 1
        return None if done or left[0] <= 0 else 0.2

    bpy.app.timers.register(attempt, first_interval=0.1)
