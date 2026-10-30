# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The AI panel (the 3D view's sidebar, JustStage tab): JustStage's server — running or not, Start, and a link to its
AI settings pages in the browser (engines, models, which model each feature uses); each AI feature with its model; the
running jobs with their progress and Cancel; the latest outcomes."""

from __future__ import annotations

import bpy

from .. import engines, paths
from . import ai_jobs

#: the AI features the panel offers: (feature key, label, the command's operator)
FEATURES = (("juststage.skin_detail", "Skin detail", "juststage.skin_add_detail"),)


class JUSTSTAGE_OT_ai_server_start(bpy.types.Operator):
    """Start JustStage's server, which runs the AI models"""

    bl_idname = "juststage.ai_server_start"
    bl_label = "Start the AI server"

    def execute(self, context):
        try:
            found = engines.ensure_running(paths.user_dir("server"))
        except (OSError, engines.EngineError) as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        ai_jobs.STATUS.update(checked=0.0)
        self.report({"INFO"}, f"{found.get('product', 'JustStage')} {found.get('version', '')} is running")
        return {"FINISHED"}


class JUSTSTAGE_OT_ai_cancel(bpy.types.Operator):
    """Stop this AI job"""

    bl_idname = "juststage.ai_cancel"
    bl_label = "Cancel"
    bl_options = {"INTERNAL"}

    job_id: bpy.props.StringProperty()

    def execute(self, context):
        ai_jobs.cancel(self.job_id)
        return {"FINISHED"}


def _character_id(context) -> str:
    obj = context.active_object
    while obj is not None and obj.juststage.kind == "NONE":
        obj = obj.parent
    return obj.juststage.character_id if obj is not None else ""


class VIEW3D_PT_juststage_ai(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "JustStage"
    bl_label = "AI"

    def draw(self, context):
        layout = self.layout
        ai_jobs.refresh_status_later(tuple(f for f, _, _ in FEATURES))
        server = ai_jobs.STATUS["server"]
        row = layout.row()
        if server is None:
            row.label(text="AI server: not running", icon="CANCEL")
            row.operator(JUSTSTAGE_OT_ai_server_start.bl_idname, text="Start")
        else:
            row.label(text=f"AI server: {server.get('product', '')} {server.get('version', '')}", icon="CHECKMARK")
        layout.operator("wm.url_open", text="AI settings", icon="URL").url = engines.BASE

        character = _character_id(context)
        for feature, label, operator in FEATURES:
            box = layout.box()
            box.label(text=label)
            model = ai_jobs.STATUS["models"].get(feature)
            if model:
                box.label(text=f"Model: {model}")
            col = box.column()
            col.enabled = bool(character) and not ai_jobs.JOBS  # the card runs one AI job at a time
            text = f"Make {label.lower()}" if character else "Select a character"
            props = col.operator(operator, text=text if not ai_jobs.JOBS else "Waiting for the running job")
            if character:
                props.character = character

        for job_id, entry in ai_jobs.JOBS.items():
            row = layout.row(align=True)
            row.progress(factor=entry["progress"], type="BAR", text=f"{entry['label']} {entry['progress']:.0%}")
            row.operator(JUSTSTAGE_OT_ai_cancel.bl_idname, text="", icon="X").job_id = job_id
        for text in ai_jobs.MESSAGES[-3:]:
            layout.label(text=text)


CLASSES = (JUSTSTAGE_OT_ai_server_start, JUSTSTAGE_OT_ai_cancel, VIEW3D_PT_juststage_ai)
