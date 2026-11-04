# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The Modify panel (the 3D view's sidebar, JustStage tab) - CC5's Modify panel (the user's screenshots, RESEARCH §1):
a row of icon tabs over what JustStage has - Attribute, Morph, Skin, Material, Hair, Expressions. Sliders run their
commands as they move (character.py). Blender's panel API: https://docs.blender.org/api/5.3/bpy.types.Panel.html;
an enum drawn expanded is Blender's own tab row."""

from __future__ import annotations

import bpy

from .command_operator import character_of

BODY = ("gender", "age", "muscle", "weight", "proportions", "height", "cupsize", "firmness")
RACES = ("asian", "caucasian", "african")
TONE = ("melanin", "eumelanin", "blood", "oiliness")

#: (id, label, icon) - CC5's six Modify tabs (Attribute, Motion, Morph, SkinGen, Material, Expression Wrinkles) as
#: JustStage has them: Motion waits for the rig; Hair is CC5's Content-side job, here beside the rest
TABS = (
    ("ATTRIBUTE", "Attribute", "PROPERTIES"),
    ("MORPH", "Morph", "SHAPEKEY_DATA"),
    ("SKIN", "Skin", "SHADING_TEXTURE"),
    ("MATERIAL", "Material", "MATERIAL"),
    ("HAIR", "Hair", "OUTLINER_OB_CURVES"),
    ("EXPRESSIONS", "Expressions", "USER"),
)

#: the Morph tab's regions - CC5's tree (Body: Full Body … Foot; Head: Full Head … Chin) over target.json's groups
REGIONS = {
    "NECK": ("Neck", ("neck",)),
    "TORSO": ("Torso", ("torso",)),
    "CHEST": ("Chest", ("breast",)),
    "WAIST": ("Waist", ("stomach",)),
    "HIP": ("Hip", ("hip", "pelvis")),
    "GLUTE": ("Glute", ("buttocks",)),
    "ARM": ("Arm", ("arms",)),
    "HAND": ("Hand", ("hands",)),
    "LEG": ("Leg", ("legs",)),
    "FOOT": ("Foot", ("feet",)),
    "GENITALS": ("Genitals", ("genitals",)),
    "HEAD": ("Full Head", ("head",)),
    "FOREHEAD": ("Forehead", ("forehead",)),
    "BROW": ("Brow", ("eyebrows",)),
    "EYE": ("Eye", ("eyes",)),
    "EAR": ("Ear", ("ears",)),
    "CHEEK": ("Cheek", ("cheek",)),
    "NOSE": ("Nose", ("nose",)),
    "MOUTH": ("Mouth", ("mouth",)),
    "CHIN": ("Chin", ("chin",)),
    "ASYM": ("Asymmetry", ("asym",)),
}
BODY_REGIONS = ("NECK", "TORSO", "CHEST", "WAIST", "HIP", "GLUTE", "ARM", "HAND", "LEG", "FOOT", "GENITALS")


def active_character(context):
    """The character the selection belongs to - the body itself or one of its parts - or None."""
    character_id = character_of(context.active_object)
    if not character_id:
        return None
    return next((o for o in bpy.data.objects if o.juststage.character_id == character_id), None)


def visible_sliders(obj, region: str, search: str) -> list:
    """The detail sliders to draw: those whose label holds `search` (any region), else the region's."""
    text = search.strip().lower()
    if text:
        return [item for item in obj.juststage.sliders if text in item.label.lower()]
    groups = REGIONS.get(region, ("", ()))[1]
    return [item for item in obj.juststage.sliders if item.group in groups]


def _parts(obj):
    own = obj.juststage.character_id
    return [o for o in bpy.data.objects if o.juststage.part_of == own]


def _command(layout, operator: str, text: str, icon: str = "NONE"):
    layout.operator(operator, text=text, icon=icon)


class VIEW3D_PT_juststage_modify(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "JustStage"
    bl_label = "Modify"
    bl_order = 0  # first in the JustStage tab

    def draw(self, context):
        layout = self.layout
        obj = active_character(context)
        if obj is None:
            layout.label(text="Select a character, or make one:")
            layout.operator("juststage.body_create", text="New human", icon="ADD")
            return
        wm = context.window_manager
        # text tabs (the user: "i prefer text tabs instead of icons"), three to a row so none is cut off in the sidebar
        tabs = layout.grid_flow(columns=3, even_columns=True, align=True)
        for key, label, _icon in TABS:
            tabs.prop_enum(wm, "juststage_modify_tab", key, text=label)
        tab = wm.juststage_modify_tab
        box = layout.column()
        box.label(text=f"{dict((t[0], t[1]) for t in TABS)[tab]} - {obj.name}")
        getattr(self, f"_draw_{tab.lower()}")(box, obj, wm)

    def _draw_attribute(self, layout, obj, wm):
        col = layout.column(align=True)
        col.prop(obj, "name", text="Character")
        col.label(text=f"Type: {obj.juststage.kind.title()}")
        layout.separator()
        col = layout.column(align=True)
        _command(col, "juststage.body_subdivide", "Subdivide (HD levels)", "MOD_SUBSURF")
        _command(col, "juststage.head_set_identity", "Head shape (scan-based)", "USER")
        _command(col, "juststage.head_add_parts", "Eyes and teeth", "HIDE_OFF")
        _command(col, "juststage.head_add_face_units", "Face units (ARKit 52)", "SHAPEKEY_DATA")
        layout.separator()
        _command(layout, "juststage.export_run", "Export", "EXPORT")

    def _draw_morph(self, layout, obj, wm):
        body = layout.column(align=True)
        body.label(text="Full Body")
        for name in BODY:
            body.prop(obj.juststage, name, slider=True)
        mix = layout.column(align=True)
        mix.label(text="Ethnic mix")
        for name in RACES:
            mix.prop(obj.juststage, name, slider=True)
        layout.separator()
        layout.prop(wm, "juststage_slider_search", text="", icon="VIEWZOOM")
        if not wm.juststage_slider_search.strip():
            grid = layout.grid_flow(columns=3, even_columns=True, align=True)
            for key, (label, _groups) in REGIONS.items():
                grid.prop_enum(wm, "juststage_morph_region", key, text=label)
        found = visible_sliders(obj, wm.juststage_morph_region, wm.juststage_slider_search)
        col = layout.column(align=True)
        for item in found:
            col.prop(item, "value", text=item.label, slider=True)
        if not found:
            col.label(text="No sliders match")

    def _draw_skin(self, layout, obj, wm):
        col = layout.column(align=True)
        for name in TONE:
            col.prop(obj.juststage, name, slider=True)
        layout.separator()
        _command(layout, "juststage.skin_set_tone", "Skin tone (dialog)", "COLOR")
        _command(layout, "juststage.skin_add_detail", "Skin detail (AI)", "TEXTURE")

    def _draw_material(self, layout, obj, wm):
        grid = layout.grid_flow(columns=3, even_columns=False, align=True)
        for head in ("Mesh", "Material", "Shader"):
            grid.label(text=head)
        for part in [obj, *_parts(obj)]:
            for slot in getattr(part, "material_slots", []):
                mat = slot.material
                if mat is None:
                    continue
                shader = next((n.bl_label for n in mat.node_tree.nodes if n.type.startswith("BSDF")), "-")
                grid.label(text=part.name)
                grid.label(text=mat.name)
                grid.label(text=shader)

    def _draw_hair(self, layout, obj, wm):
        grooms = [o for o in _parts(obj) if o.type == "CURVES"]
        for groom in grooms:
            row = layout.row(align=True)
            row.label(text=groom.name, icon="OUTLINER_OB_CURVES")
            row.operator("juststage.hair_set_colour", text="Colour").groom = groom.name
        if not grooms:
            layout.label(text="No hair yet")
        _command(layout, "juststage.hair_add", "Add hair", "ADD")

    def _draw_expressions(self, layout, obj, wm):
        keys = obj.data.shape_keys.key_blocks if obj.data.shape_keys else {}
        from ..modules.head import face_units

        units = [keys[name] for name in face_units.ARKIT if name in keys]
        if not units:
            layout.label(text="No face units yet")
            _command(layout, "juststage.head_add_face_units", "Add face units (ARKit 52)", "ADD")
            return
        col = layout.column(align=True)
        for key in units:
            col.prop(key, "value", text=key.name, slider=True)


_REGION_ITEMS = [(key, label, f"the {label.lower()} sliders") for key, (label, _g) in REGIONS.items()]
CLASSES = (VIEW3D_PT_juststage_modify,)


def register():
    wm = bpy.types.WindowManager
    wm.juststage_modify_tab = bpy.props.EnumProperty(
        name="Modify", items=[(t[0], t[1], t[1], i) for i, t in enumerate(TABS)], default="MORPH"
    )
    wm.juststage_morph_region = bpy.props.EnumProperty(name="Region", items=_REGION_ITEMS, default="NOSE")
    wm.juststage_slider_search = bpy.props.StringProperty(name="Search sliders", options={"TEXTEDIT_UPDATE"})
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    wm = bpy.types.WindowManager
    del wm.juststage_modify_tab, wm.juststage_morph_region, wm.juststage_slider_search
