# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Base v1 -> v2: an hm08 character gets base v2's lid anatomy (modules/body/base.py `upgrade`: the cut, every shape
key's new vertices placed by their faces), its grooms are put back exactly where they were drawn (the cut changes the
faces under the lashes - their surface deform would carry them wrong; hair/lashes.py `keep_in_place`), and its parts
are refitted (the contact key). JustStage's own lashes are made again on the new lid (their roots belong on its lash
line, which the cut made; carried, they would swing with the reshaped margin - up to 5 mm at the tips, measured)."""

from __future__ import annotations

import bpy
import numpy as np


def needed(body: bpy.types.Object) -> bool:
    from ..core.makehuman import HM08_VERTICES
    from ..modules.body import base

    return body.juststage.base_version < base.VERSION and len(body.data.vertices) == HM08_VERTICES


def migrate(body: bpy.types.Object) -> None:
    from ..modules.body import base
    from ..modules.hair import lashes

    cid = body.juststage.character_id
    grooms = [o for o in bpy.data.objects if o.type == "CURVES" and o.data.surface == body]
    bpy.context.view_layer.update()
    before = {o.name: lashes.evaluated_points(o) for o in grooms}
    base.upgrade(body)
    bpy.context.view_layer.update()
    for o in grooms:
        now = lashes.evaluated_points(o)
        if len(now) == len(before[o.name]) and np.abs(now - before[o.name]).max() > 1e-5:
            miss = lashes.keep_in_place(o, before[o.name])
            print(f"JustStage: {o.name} put back where it was drawn (within {miss * 1000:.4f} mm)")
    if any(o.juststage.part_of == cid and o.juststage.part in ("eyeLeft", "eyeRight") for o in bpy.data.objects):
        from ..modules.head import parts

        parts.refit(body)
        if any(o.name.removeprefix(f"{body.name}.").startswith(lashes.NAME) for o in grooms):
            lashes.make(body)  # replaces the part
