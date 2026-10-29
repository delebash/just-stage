# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The JustStage application template (docs/standards/plugins.md §5).

Blender runs `register()` when the launcher starts it with `--app-template juststage`; the template switches the
JustStage add-on on from Blender's System repository. Its splash, startup file, workspaces, theme and keymaps join it
as the workspaces are built.
"""

ADDON = "bl_ext.system.juststage"


def register():
    import addon_utils

    addon_utils.enable(ADDON, default_set=True, persistent=True)


def unregister():
    import addon_utils

    addon_utils.disable(ADDON, default_set=False)
