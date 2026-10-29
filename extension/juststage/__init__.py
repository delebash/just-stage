# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage, the Blender add-on (standards: docs/standards/plugins.md).

Nothing here imports `bpy` at module level, so the Blender-free parts (`core`) import on plain CPython for the unit
tests (docs/standards/testing.md §2).
"""


def register():
    from . import addon

    addon.register()


def unregister():
    from . import addon

    addon.unregister()
