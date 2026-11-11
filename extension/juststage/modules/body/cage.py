# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The body's deform cage: what a mesh riding the skin binds to (2026-11-10). The body subdivides by its Multires for
render at a higher level than in the viewport (`build.DEFAULT_LEVELS` 2, `DEFAULT_VIEW_LEVEL` 1), and Blender's Surface
Deform needs its target's topology unchanged after binding
(docs.blender.org/manual/en/5.3/modeling/modifiers/deform/surface_deform.html) - bound to the body, card hair met
another mesh at render and flew apart. The cage is a linked duplicate of the body - the same mesh data, so the same
shape keys (macros, details, the mixer, expressions, the floor) - with the body's deform modifiers (its helper mask,
its skeleton's armature) and no Multires: one topology always, deformed as the body is. Binding to a low cage is the
riggers' usual way (a mesh deform cage); hidden from the viewport and render, and from exports."""

from __future__ import annotations

import bpy

NAME = "JustStage deform cage"
PART = "deform_cage"
SKIP = {"MULTIRES", "SUBSURF"}  # the body's subdivision: the one thing the cage must not have


def of(character: bpy.types.Object) -> bpy.types.Object | None:
    cid = character.juststage.character_id
    return next((o for o in bpy.data.objects if o.juststage.part_of == cid and o.juststage.part == PART), None)


def _copy_modifier(src: bpy.types.Modifier, dst_obj: bpy.types.Object) -> None:
    mod = dst_obj.modifiers.new(src.name, src.type)
    for prop in src.bl_rna.properties:
        if prop.is_readonly or prop.identifier in ("name", "type"):
            continue
        try:
            setattr(mod, prop.identifier, getattr(src, prop.identifier))
        except (AttributeError, TypeError, ValueError):
            pass  # a property that can't be set on a fresh modifier (e.g. a bind state) - left as created


def sync(character: bpy.types.Object, cage: bpy.types.Object) -> None:
    """The cage's modifiers as the body's deform ones, in order, without the subdivision."""
    for mod in list(cage.modifiers):
        cage.modifiers.remove(mod)
    for mod in character.modifiers:
        if mod.type not in SKIP:
            _copy_modifier(mod, cage)


def get(character: bpy.types.Object) -> bpy.types.Object:
    """The character's cage, made the first time, its modifiers synced every time."""
    cage = of(character)
    if cage is None:
        cage = bpy.data.objects.new(f"{character.name}.{NAME}", character.data)  # the body's own mesh data
        for collection in character.users_collection:
            collection.objects.link(cage)
        cage.parent = character.parent
        cage.matrix_world = character.matrix_world
        cage.juststage.part_of = character.juststage.character_id
        cage.juststage.part = PART
        cage.hide_render = True
        cage.display_type = "WIRE"
        cage.hide_set(True)
    sync(character, cage)
    return cage
