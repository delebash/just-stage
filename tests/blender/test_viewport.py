# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""How a character is shown (docs/plans/2026-11-03-live-view.md): Cycles on the card, Material Preview (EEVEE) to move
around, Rendered (Cycles on the card with the viewport denoiser) to stop and look, F12 the film run - and the EEVEE
settings the materials carry for the live view."""

import importlib

import bpy
import pytest

api = importlib.import_module("bl_ext.system.juststage.api")
viewport = importlib.import_module("bl_ext.system.juststage.core.viewport")
part_materials = importlib.import_module("bl_ext.system.juststage.modules.head.part_materials")
groom = importlib.import_module("bl_ext.system.juststage.modules.hair.groom")


def _cycles_prefs():
    return bpy.context.preferences.addons["cycles"].preferences


def test_use_gpu_picks_the_card_when_one_is_listed():
    prefs = _cycles_prefs()
    prefs.refresh_devices()
    listed = {d.type for d in prefs.devices if d.type != "CPU"}
    chosen = viewport.use_gpu()
    if not listed:
        assert chosen == "NONE"
        return
    assert chosen in listed
    assert prefs.compute_device_type == chosen
    used = [d for d in prefs.devices if d.use]
    assert used and all(d.type == chosen for d in used)


def test_the_scene_renders_on_the_card_with_the_viewport_denoiser():
    scene = bpy.context.scene
    viewport.setup_scene(scene)
    assert scene.render.engine == "CYCLES"  # F12 is the film run
    assert scene.cycles.device == "GPU"  # the preferences pick the card; none picked renders on the processor
    assert scene.cycles.use_preview_denoising
    assert scene.eevee.use_raytracing  # the cornea's refraction in Material Preview
    assert (scene.eevee.shadow_ray_count, scene.eevee.shadow_step_count) == (4, 16)  # no blotched eye whites
    assert scene.render.hair_type == "STRIP"  # strands with their width, not 1-px lines


def test_the_live_view_is_material_preview_in_the_scene_light():
    viewport.show_live(bpy.data.screens)
    views = [a.spaces.active for s in bpy.data.screens for a in s.areas if a.type == "VIEW_3D"]
    assert views
    for view in views:
        assert view.shading.type == "MATERIAL"
        assert view.shading.use_scene_lights and view.shading.use_scene_world


@pytest.fixture
def human():
    result = api.run("juststage.body.create", name="Live view test")
    yield result, bpy.data.objects[result.object]
    bpy.data.objects.remove(bpy.data.objects[result.object])


def test_skin_and_cornea_carry_their_eevee_settings(human):
    result, obj = human
    skin = obj.data.materials[api.run("juststage.skin.set_tone", character=result.character).material]
    assert skin.use_thickness_from_shadow
    cornea = part_materials._material("cornea", "test")
    try:
        assert cornea.use_raytrace_refraction
    finally:
        bpy.data.materials.remove(cornea)


def test_hair_keeps_principled_hair_for_cycles_and_gets_an_eevee_stand_in():
    mat = groom.hair_material("live view hair")
    try:
        outputs = {n.target: n for n in mat.node_tree.nodes if n.type == "OUTPUT_MATERIAL"}
        assert set(outputs) == {"ALL", "EEVEE"}
        assert outputs["ALL"].inputs["Surface"].links[0].from_node.type == "BSDF_HAIR_PRINCIPLED"
        assert outputs["EEVEE"].inputs["Surface"].links[0].from_node.type == "BSDF_PRINCIPLED"
    finally:
        bpy.data.materials.remove(mat)


def test_the_stand_in_colour_follows_cycles_melanin():
    white = groom.hair_colour(0.0, 0.0)
    assert white == pytest.approx((1.0, 1.0, 1.0))
    black = groom.hair_colour(0.98, 0.1)
    assert max(black) < 0.05
    ginger = groom.hair_colour(0.5, 1.0)
    assert ginger[0] > ginger[1] > ginger[2]  # pheomelanin absorbs blue most
    brown = groom.hair_colour(0.6, 0.2)
    assert brown[0] > brown[1] > brown[2] and max(brown) < max(ginger)
