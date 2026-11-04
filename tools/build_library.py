# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's starter library, the Content panel's first assets (docs/standards/project-files.md §2: "JustStage's
starter library (... the base bodies, MakeHuman's CC0 styles ...)"), each saved through `juststage.library.save`:

- characters: presets made by JustStage's own commands from MakeHuman's CC0 base and targets;
- hair: MakeHuman's CC0 hair-editor styles (all but `empty_hair`, a blank to groom from), one asset each in its
  `Hair/<type>` catalogue;
- skins: eight tones evenly spaced in lightness (CIE L* 74 down to 25), each melanin found by solving JustStage's own
  skin model (core/skin_optics.py) at the NIST median's eumelanin share and blood.

Sections to build are named after `--` (all when none). Building a section overwrites its files, and with them the
thumbnails tools/library_previews.py set.

    python tools/dev.py blender -b --python tools/build_library.py -- hair skins
"""

import importlib
import sys

import addon_utils
import bpy

addon_utils.enable("bl_ext.system.juststage", default_set=True)
api = importlib.import_module("bl_ext.system.juststage.api")
paths = importlib.import_module("bl_ext.system.juststage.paths")
skin_optics = importlib.import_module("bl_ext.system.juststage.core.skin_optics")
styles = importlib.import_module("bl_ext.system.juststage.modules.hair.styles")
groom = importlib.import_module("bl_ext.system.juststage.modules.hair.groom")
HAIR = importlib.import_module("bl_ext.system.juststage.modules.io.library_save").HAIR

WANTED = set(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else ()) or {"characters", "hair", "skins"}
MAKEHUMAN = "JustStage body.create on MakeHuman's CC0 base and targets (MPFB2 6ff1eb35)"

#: (name, body.create's macros, skin melanin, description)
PRESETS = (
    ("Average woman", {"gender": 0.0}, 0.03, "MakeHuman's average woman"),
    ("Average man", {"gender": 1.0}, 0.03, "MakeHuman's average man"),
    ("Young woman", {"gender": 0.0, "age": 0.35, "weight": 0.4}, 0.012, "A slim young woman"),
    ("Older man", {"gender": 1.0, "age": 0.85, "weight": 0.6}, 0.08, "A man in his sixties"),
    ("Muscular man", {"gender": 1.0, "muscle": 0.9, "weight": 0.6, "height": 0.7}, 0.15, "A tall muscular man"),
    ("Heavy woman", {"gender": 0.0, "weight": 0.9, "age": 0.6}, 0.25, "A heavy-set woman"),
)

#: a groom type → its colour in the library (Cycles' melanin, redness): a medium brown; lashes darker
HAIR_COLOUR = {"eyelashes": (0.85, 0.1)}
BROWN = (0.65, 0.2)  # measured 2026-11-04: medium brown in both engines (0.5 / 0.25 read auburn in Cycles)

#: (name, CIE L*) - eight steps of ~7 in lightness, the range of measured human skin's albedo
TONES = (
    ("Tone 1 - very light", 74.0),
    ("Tone 2 - light", 67.0),
    ("Tone 3 - light medium", 60.0),
    ("Tone 4 - medium", 53.0),
    ("Tone 5 - medium dark", 46.0),
    ("Tone 6 - dark", 39.0),
    ("Tone 7 - very dark", 32.0),
    ("Tone 8 - deep", 25.0),
)
EUMELANIN, BLOOD = 0.6, 0.016  # the skin command's defaults (NIST's median person)
SKIN_SOURCE = "JustStage skin.set_tone (core/skin_optics.py, calibrated on NIST's skin data)"


def _lightness(rgb) -> float:
    """CIE L* of a linear sRGB colour (D65)."""
    y = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    return 116.0 * y ** (1.0 / 3.0) - 16.0 if y > 0.008856 else 903.3 * y


def melanin_for(lightness: float, tables) -> float:
    """The melanin whose skin has that lightness (it falls as melanin rises): bisection over the model's range."""
    low, high = 0.0, 0.5
    for _ in range(40):
        mid = (low + high) / 2
        if _lightness(skin_optics.Skin(mid, EUMELANIN, BLOOD).linear_rgb(tables)) > lightness:
            low = mid
        else:
            high = mid
    return round((low + high) / 2, 5)


def _remove(made) -> None:
    for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
        bpy.data.objects.remove(obj)
    bpy.data.objects.remove(bpy.data.objects[made.object])


if "characters" in WANTED:
    for name, macros, melanin, description in PRESETS:
        made = api.run("juststage.body.create", name=name, **macros)
        api.run("juststage.skin.set_tone", character=made.character, melanin=melanin)
        api.run("juststage.head.add_parts", character=made.character)
        out = api.run("juststage.library.save", character=made.character, catalog="Characters", name=name,
                      description=description, licence="CC0-1.0", provenance=MAKEHUMAN)  # fmt: skip
        print("LIBRARY", out.path, flush=True)

if "hair" in WANTED:
    woman = api.run("juststage.body.create", name="Hair model woman", gender=0.0)
    man = api.run("juststage.body.create", name="Hair model man", gender=1.0)
    for style, (kind, label) in styles.STYLES.items():
        if style == "empty_hair":
            continue
        model = man if kind in ("beard", "mustache") else woman
        melanin, redness = HAIR_COLOUR.get(kind, BROWN)
        api.run("juststage.hair.add", character=model.character, style=style, melanin=melanin, redness=redness)
        catalog = next(c for c, kinds in HAIR.items() if kind in kinds)
        out = api.run("juststage.library.save", character=model.character, catalog=catalog, name=label,
                      description=f"{label} ({kind})", licence="CC0-1.0",
                      provenance="MakeHuman's CC0 hair-editor pack (hair/haireditor/hair.blend, by Tomáš Klecer)",
                      part=kind)  # fmt: skip
        groom.remove_part(bpy.data.objects[model.object], kind)
        print("LIBRARY", out.path, flush=True)
    _remove(woman)
    _remove(man)

if "skins" in WANTED:
    tables = skin_optics.load_tables(paths.FETCHED / "optics")
    model = api.run("juststage.body.create", name="Skin model", gender=0.0)
    for name, lightness in TONES:
        melanin = melanin_for(lightness, tables)
        api.run("juststage.skin.set_tone", character=model.character, melanin=melanin, eumelanin=EUMELANIN, blood=BLOOD)
        out = api.run("juststage.library.save", character=model.character, catalog="Skins", name=name,
                      description=f"Skin of lightness L* {lightness:.0f} (melanin {melanin})", licence="CC0-1.0",
                      provenance=SKIN_SOURCE)  # fmt: skip
        print("LIBRARY", out.path, "melanin", melanin, flush=True)
    _remove(model)
