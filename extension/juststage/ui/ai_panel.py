# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The AI panel (the 3D view's sidebar, JustStage tab): JustStage's server — running or not, Start; each AI feature with
its model; the running jobs with their progress and Cancel; the latest outcomes. (A link to the kit's AI settings pages
in the browser joins when the server serves them — TASKS step 1.4.)"""

from __future__ import annotations

import bpy

from .. import engines, paths  # noqa: F401 — engines for the operators below
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

        character = _character_id(context)
        for feature, label, operator in FEATURES:
            box = layout.box()
            box.label(text=label)
            model = ai_jobs.STATUS["models"].get(feature)
            if model:
                box.label(text=f"Model: {model}")
            col = box.column()
            col.enabled = bool(character)  # a second job waits on the server behind the first
            props = col.operator(operator, text=f"Make {label.lower()}" if character else "Select a character")
            if character:
                props.character = character

        for job_id, entry in ai_jobs.JOBS.items():
            row = layout.row(align=True)
            row.progress(factor=entry["progress"], type="BAR", text=f"{entry['label']} {entry['progress']:.0%}")
            row.operator(JUSTSTAGE_OT_ai_cancel.bl_idname, text="", icon="X").job_id = job_id
        for text in ai_jobs.MESSAGES[-3:]:
            layout.label(text=text)


CLASSES = (JUSTSTAGE_OT_ai_server_start, JUSTSTAGE_OT_ai_cancel, VIEW3D_PT_juststage_ai)
