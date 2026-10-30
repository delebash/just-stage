# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The hair styles JustStage offers: MPFB2's hair-editor lists (`src/mpfb/ui/haireditorpanel/properties/` —
`hair_assets.json`, `eyebrow_assets.json`, `facial_assets.json`, `other_assets.json` at the pinned commit), each style
an object in MakeHuman's CC0 hair-editor pack (`hair/haireditor/hair.blend`), with its groom type
(character-data-model.md §4) and MPFB2's label."""

#: style → (groom type, label)
STYLES = {
    "short_hedgehog": ("scalp", "Short hedgehog"),
    "hair_to_shoulder": ("scalp", "Hair to shoulder"),
    "short_crown": ("scalp", "Hair crown"),
    "short_cap": ("scalp", "Short hair cap"),
    "short_ponnytail": ("scalp", "Short ponytail"),
    "back_pigtail": ("scalp", "Back pigtail"),
    "tail_base": ("scalp", "Tail base"),
    "empty_hair": ("scalp", "Empty hair"),
    "wild_eyebrow": ("eyebrows", "Wild eyebrow"),
    "wild_thick_eyebrow": ("eyebrows", "Wild thick eyebrow"),
    "wild_thick_beard": ("beard", "Wild thick beard"),
    "wild_thick_moustache": ("mustache", "Wild thick moustache"),
    "wild_beard": ("beard", "Wild beard"),
    "wild_moustache": ("mustache", "Wild moustache"),
    "basic_lashes_upper": ("eyelashes", "Basic upper lashes"),
    "basic_lashes_lower": ("eyelashes", "Basic lower lashes"),
}
DEFAULT = "short_hedgehog"  # MPFB2's default hair
