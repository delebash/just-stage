# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Mixer panel (the 3D view's sidebar, JustStage tab, under Modify) - CC5's ActorMIXER over our identities: its
parts (CC5's manual, "Switching Categories": Head Shape, Eyes, Nose, Mouth, Chin, Ears, Forehead; Torso, Arms, Legs),
each target identity's share of the part (CC5's wheel: what the targets don't take stays the character's own - the
manual, "the inner circle maintains a stronger influence from the base character"), MetaHuman's Blend Type and its
strength (the shares' sum). The panel keeps no state of its own: every slider reads and writes the character's mixer
sliders (Blender's property get / set), through `juststage.body.set_mix` - one way per job (modules/body/mixer.py).
The wheel's picture is not drawn (a panel can't host one); its numbers are. Blender's panel API:
https://docs.blender.org/api/5.3/bpy.types.Panel.html; get / set properties:
https://docs.blender.org/api/5.3/bpy.props.html#getter-setter-example."""

from __future__ import annotations

import re

import bpy

from .character_panel import active_character

#: CC5's mixer parts in its order, the Head tab then the Body tab, with its names
PARTS = (
    ("head shape", "Head Shape"),
    ("eyes", "Eyes"),
    ("nose", "Nose"),
    ("mouth", "Mouth"),
    ("chin", "Chin"),
    ("ears", "Ears"),
    ("forehead", "Forehead"),
    ("torso", "Torso"),
    ("arms", "Arms"),
    ("legs", "Legs"),
)
HEAD = tuple(key for key, _label in PARTS[:7])  # CC5's Head tab, its first seven parts; the rest its Body tab
MODES = (
    ("both", "Both", "The part's shape, place, turn and size"),
    ("features", "Features", "The part's shape; its place, turn and size kept"),
    ("proportions", "Proportions", "The part's place, turn and size; its shape kept"),
)
_REGISTERED: list[str] = []  # the per-identity properties this module added


def _mixer():
    from ..modules.body import mixer

    return mixer


def prop_name(identity: str) -> str:
    """The window manager property drawing one identity's share."""
    return "juststage_mix_" + re.sub(r"\W", "_", identity)


def shares(context, part: str | None = None) -> dict[str, float]:
    """The active character's shares in the chosen part: the features' (or, in Proportions, the proportions')."""
    obj = active_character(context)
    if obj is None:
        return {}
    wm = context.window_manager
    part = part or ("proportions" if wm.juststage_mix_mode == "proportions" else "features")
    return _mixer().region_mix(obj, wm.juststage_mix_region, part)


def _run(context, values: dict[str, float]) -> None:
    """The part's mix as `values` (each identity's share), through the command."""
    from .. import api

    obj = active_character(context)
    if obj is None:
        return
    wm = context.window_manager
    keep = {name: value for name, value in values.items() if value > 1e-6}
    try:
        api.run("juststage.body.set_mix", character=obj.juststage.character_id, region=wm.juststage_mix_region,
                identities=", ".join(keep), weights=list(keep.values()), strength=min(1.0, sum(keep.values())),
                mode=wm.juststage_mix_mode)  # fmt: skip
    except api.CommandError as e:
        print(f"JustStage: mixer: {e}")


def _share(identity: str):
    def get(_wm):
        return shares(bpy.context).get(identity, 0.0)

    def set(_wm, value):
        values = shares(bpy.context)
        others = sum(v for name, v in values.items() if name != identity)
        values[identity] = min(value, max(0.0, 1.0 - others))  # the shares sum to 1 at most: the rest, the character
        _run(bpy.context, values)

    return bpy.props.FloatProperty(name=identity, min=0.0, max=1.0, get=get, set=set,
                                   description=f"{identity}'s share of the part")  # fmt: skip


def _get_strength(_wm):
    return min(1.0, sum(shares(bpy.context).values()))


def _set_strength(_wm, value):
    values = shares(bpy.context)
    total = sum(values.values())
    if total > 0.0:  # every share scaled: the targets' balance kept
        _run(bpy.context, {name: v * value / total for name, v in values.items()})


class VIEW3D_PT_juststage_mixer(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "JustStage"
    bl_label = "Mixer"
    bl_order = 1  # under Modify

    @classmethod
    def poll(cls, context):
        return active_character(context) is not None

    def draw(self, context):
        layout = self.layout
        from ..core.commands import CommandError

        mixer = _mixer()
        wm = context.window_manager
        if not mixer.identities():
            layout.label(text="No identities yet")
            return
        try:
            reach = mixer.reach()
        except CommandError as e:  # the masks not generated: the tool to run
            layout.label(text=str(e), icon="ERROR")
            return
        for group, keys in (("Head", HEAD), ("Body", None)):  # CC5's Head tab, then its Body tab
            found = [(key, label) for key, label in _parts() if (key in keys if keys else key not in HEAD)]
            if not found:
                continue
            layout.label(text=group)
            grid = layout.grid_flow(row_major=True, columns=3, even_columns=True, align=True)
            for key, label in found:
                cell = grid.row(align=True)
                cell.enabled = bool(reach.get(key))
                cell.prop_enum(wm, "juststage_mix_region", key, text=label)
        layout.prop(wm, "juststage_mix_mode", expand=True)
        reached = reach.get(wm.juststage_mix_region, ())
        if not reached:
            layout.label(text="No identity reaches this part yet")
            return
        layout.prop(wm, "juststage_mix_strength", text="Strength", slider=True)
        col = layout.column(align=True)
        for name in reached:
            col.prop(wm, prop_name(name), text=name, slider=True)
        if wm.juststage_mix_mode == "both" and shares(context, "features") != shares(context, "proportions"):
            layout.label(text="Features and proportions differ here", icon="INFO")
        op = layout.operator("juststage.body_set_mix", text="Reset this part")
        op.character = active_character(context).juststage.character_id
        op.region = wm.juststage_mix_region
        op.mode = wm.juststage_mix_mode


def _parts() -> list[tuple[str, str]]:
    """CC5's parts the mask file has, in CC5's order; any other region after them under its own name (none when the
    masks aren't generated - the panel then names the tool)."""
    from ..core.commands import CommandError

    try:
        have = _mixer().regions()
    except CommandError:
        return []
    known = [(key, label) for key, label in PARTS if key in have]
    return known + [(key, key.title()) for key in have if key not in dict(PARTS)]


_REGION_ITEMS: list[tuple[str, str, str]] = []  # kept referenced while registered (Blender's dynamic-enum rule)
CLASSES = (VIEW3D_PT_juststage_mixer,)


def register():
    wm = bpy.types.WindowManager
    _REGION_ITEMS[:] = [(key, label, f"the mixer's {label.lower()}") for key, label in _parts()] or [
        ("none", "None", "the mixer's masks aren't generated")
    ]
    default = "nose" if any(k == "nose" for k, *_ in _REGION_ITEMS) else _REGION_ITEMS[0][0]
    wm.juststage_mix_region = bpy.props.EnumProperty(name="Part", items=_REGION_ITEMS, default=default)
    wm.juststage_mix_mode = bpy.props.EnumProperty(name="Blend type", items=MODES, default="both")
    wm.juststage_mix_strength = bpy.props.FloatProperty(
        name="Strength", min=0.0, max=1.0, get=_get_strength, set=_set_strength, description="The targets' shares' sum"
    )
    for name in _mixer().identities():
        setattr(wm, prop_name(name), _share(name))
        _REGISTERED.append(prop_name(name))
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    wm = bpy.types.WindowManager
    for name in _REGISTERED:
        delattr(wm, name)
    _REGISTERED.clear()
    del wm.juststage_mix_region, wm.juststage_mix_mode, wm.juststage_mix_strength
