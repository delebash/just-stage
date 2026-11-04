# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's starter library, the Content panel's first characters (docs/standards/project-files.md §2: "JustStage's
starter library (... the base bodies ...)"): presets made by JustStage's own commands from MakeHuman's CC0 base and
targets, so their licence is CC0 and their provenance ours. Saved through `juststage.library.save`, one asset each.

    python tools/dev.py blender -b --python tools/build_library.py
"""

import importlib

import addon_utils

addon_utils.enable("bl_ext.system.juststage", default_set=True)
api = importlib.import_module("bl_ext.system.juststage.api")

#: (name, body.create's macros, skin melanin, description)
PRESETS = (
    ("Average woman", {"gender": 0.0}, 0.03, "MakeHuman's average woman"),
    ("Average man", {"gender": 1.0}, 0.03, "MakeHuman's average man"),
    ("Young woman", {"gender": 0.0, "age": 0.35, "weight": 0.4}, 0.012, "A slim young woman"),
    ("Older man", {"gender": 1.0, "age": 0.85, "weight": 0.6}, 0.08, "A man in his sixties"),
    ("Muscular man", {"gender": 1.0, "muscle": 0.9, "weight": 0.6, "height": 0.7}, 0.15, "A tall muscular man"),
    ("Heavy woman", {"gender": 0.0, "weight": 0.9, "age": 0.6}, 0.25, "A heavy-set woman"),
)

for name, macros, melanin, description in PRESETS:
    made = api.run("juststage.body.create", name=name, **macros)
    api.run("juststage.skin.set_tone", character=made.character, melanin=melanin)
    api.run("juststage.head.add_parts", character=made.character)
    out = api.run(
        "juststage.library.save",
        character=made.character,
        catalog="Characters",
        name=name,
        description=description,
        licence="CC0-1.0",
        provenance="JustStage body.create on MakeHuman's CC0 base and targets (MPFB2 6ff1eb35)",
    )
    print("LIBRARY", out.path, flush=True)
