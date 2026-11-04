# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The 3D view's header while JustStage's interface is on (ui/topbar.py; Window > "Blender's full interface" brings
Blender's back): camera Home and Frame and a view list (CC5's camera toolbar, the user's screenshots); Preview Clay /
Skin / Film - Blender's Solid, Material Preview and Rendered under plain names (MetaHuman Creator's Preview Material);
MetaHuman's framing presets Face, Body, Hands, Feet. Blender's overlay and shading popovers stay at the right.
Blender's header API: https://docs.blender.org/api/5.3/bpy.types.Header.html."""

from __future__ import annotations

import bpy
from mathutils import Euler, Vector

#: (key, label, the share of the body's height its box takes, the height of the box's middle as a share, from the floor)
FRAMES = (
    ("FACE", "Face", 0.15, 0.92),
    ("BODY", "Body", 1.0, 0.5),
    ("HANDS", "Hands", 0.25, 0.48),
    ("FEET", "Feet", 0.15, 0.06),
)
PREVIEWS = (("SOLID", "Clay"), ("MATERIAL", "Skin"), ("RENDERED", "Film"))
VIEWS = (("FRONT", "Front"), ("BACK", "Back"), ("LEFT", "Left"), ("RIGHT", "Right"), ("TOP", "Top"))

_ORIGINAL = {}


def frame_box(obj, target: str) -> tuple[Vector, float]:
    """Where a framing looks (its box's middle) and how big the box is (metres), from the character's bounds."""
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    low = Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    high = Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    height = high.z - low.z
    _key, _label, share, middle = next(f for f in FRAMES if f[0] == target)
    centre = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z + middle * height))
    size = share * height if target != "HANDS" else max(share * height, high.x - low.x)
    return centre, size


class JUSTSTAGE_OT_view_frame(bpy.types.Operator):
    """Look at the selected character's face, whole body, hands or feet, from the front"""

    bl_idname = "juststage.view_frame"
    bl_label = "Frame"
    target: bpy.props.EnumProperty(items=[(k, label, "") for k, label, _s, _m in FRAMES], default="BODY")

    def execute(self, context):
        from .character_panel import active_character

        obj = active_character(context) or context.active_object
        rv3d = context.region_data
        if obj is None or rv3d is None:
            self.report({"WARNING"}, "Select a character in a 3D view")
            return {"CANCELLED"}
        centre, size = frame_box(obj, self.target)
        rv3d.view_perspective = "PERSP"
        rv3d.view_rotation = Euler((1.5708, 0.0, 0.0)).to_quaternion()  # from the front
        rv3d.view_location = centre
        rv3d.view_distance = size * 2.2
        return {"FINISHED"}


def draw(self, context):
    if getattr(context.window_manager, "juststage_full_interface", True):
        _ORIGINAL["draw"](self, context)
        return
    layout = self.layout
    space = context.space_data
    row = layout.row(align=True)
    row.operator("view3d.view_all", text="Home", icon="HOME").center = True
    row.operator("view3d.view_selected", text="Frame", icon="ZOOM_SELECTED")
    sub = layout.row(align=True)
    for key, label in VIEWS:
        sub.operator("view3d.view_axis", text=label).type = key
    layout.separator_spacer()
    row = layout.row(align=True)
    for key, label in PREVIEWS:
        row.prop_enum(space.shading, "type", key, text=label)
    row = layout.row(align=True)
    for key, label, _s, _m in FRAMES:
        row.operator("juststage.view_frame", text=label).target = key
    layout.separator_spacer()
    layout.popover("VIEW3D_PT_overlay", text="", icon="OVERLAY")
    layout.popover("VIEW3D_PT_shading", text="", icon="SHADING_TEXTURE")


CLASSES = (JUSTSTAGE_OT_view_frame,)


def install() -> None:
    if "draw" in _ORIGINAL:
        return
    _ORIGINAL["draw"] = bpy.types.VIEW3D_HT_header.draw
    bpy.types.VIEW3D_HT_header.draw = draw


def uninstall() -> None:
    if "draw" in _ORIGINAL:
        bpy.types.VIEW3D_HT_header.draw = _ORIGINAL.pop("draw")
