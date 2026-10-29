# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""`juststage.api.status` — which JustStage, API and Blender this is, and which plugins are on."""

from typing import NamedTuple


class Params(NamedTuple):
    pass


class Result(NamedTuple):
    juststage: str
    api: str
    blender: str
    plugins: list[str]


COMMAND = dict(
    id="juststage.api.status",
    label="JustStage status",
    permission="read",
    undo=False,
    headless=True,
    since="2026-10-29",
)


def main(params: Params) -> Result:
    from .. import api

    try:
        import bpy

        blender = bpy.app.version_string
    except ImportError:
        blender = ""
    return Result(
        juststage=api.juststage_version(),
        api=api.VERSION,
        blender=blender,
        plugins=sorted(p.id for p in api.plugins()),
    )
