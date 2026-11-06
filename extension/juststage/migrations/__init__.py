# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Ordered migration steps (character-data-model.md §6: Blender's versioning-code pattern) - run on every file load
(`load_post`) and when a library asset comes in (core/library.py `add`), so a character saved by an older JustStage
works in this one."""

from __future__ import annotations

import bpy
from bpy.app.handlers import persistent

from . import v2_base


def run(objects) -> list[str]:
    """Every step a character among `objects` still needs; returns the names of the characters it changed."""
    changed = []
    for obj in list(objects):
        if obj.type != "MESH" or obj.juststage.kind != "HUMAN" or obj.juststage.part_of:
            continue
        if v2_base.needed(obj):
            v2_base.migrate(obj)
            changed.append(obj.name)
        elif v2_base.is_v2(obj):
            v2_base.remark(obj)  # the lid's marks (creases, the margin's and caruncle's shares) as this code sets them
    return changed


@persistent
def _on_load(_filepath) -> None:
    changed = run(bpy.data.objects)
    if changed:
        print(f"JustStage: {', '.join(changed)} brought to base v2 (modules/body/base.py)")


def register() -> None:
    if _on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load)


def unregister() -> None:
    if _on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load)
