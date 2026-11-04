# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""JustStage's own look - CC5's calm dark window (the user's screenshots, RESEARCH §1), not its colours (the user: "do
enough so it doenst look exactly like cc5 but it needs to be intuitive and easy to use"): near-black greys, quiet dark
panel titles, one teal accent only on what is selected or being dragged, a blue-grey gradient behind the character.
Blender's own theme settings
(https://docs.blender.org/manual/en/5.3/editors/preferences/themes.html), set by the application template on first
start (template/juststage/__init__.py) - the user can change or reset them in Preferences like any theme."""

from __future__ import annotations

#: JustStage's accent - teal, apart from CC5's lime and Blender's blue - on selected tabs and buttons and slider fills
ACCENT = (0.16, 0.66, 0.72)
INK = (0.03, 0.05, 0.06)  # text on the accent
HEADER = (0.17, 0.17, 0.17)  # panel titles
TEXT = (0.86, 0.86, 0.86)
BACK = (0.11, 0.11, 0.11)  # panels
WIDGET = (0.20, 0.20, 0.20)  # buttons and fields
FIELD = (0.15, 0.15, 0.15)  # number and text fields
VIEW_TOP, VIEW_BOTTOM = (0.33, 0.37, 0.43), (0.13, 0.15, 0.18)  # the viewport's gradient


def _set(owner, name, rgb):
    """A theme colour of 3 or 4 components from an RGB triple (alpha left as it was)."""
    current = getattr(owner, name)
    setattr(owner, name, (*rgb, current[3]) if len(current) == 4 else rgb)


def apply(preferences) -> None:
    theme = preferences.themes[0]
    ui = theme.user_interface
    for name in ("wcol_regular", "wcol_tool", "wcol_toolbar_item", "wcol_radio", "wcol_toggle", "wcol_option",
                 "wcol_box", "wcol_menu", "wcol_pulldown", "wcol_tab", "wcol_list_item", "wcol_menu_item",
                 "wcol_pie_menu", "wcol_scroll", "wcol_progress"):  # fmt: skip
        w = getattr(ui, name)
        _set(w, "inner", WIDGET)
        _set(w, "inner_sel", ACCENT)
        _set(w, "text", TEXT)
        _set(w, "text_sel", INK)
    for name in ("wcol_num", "wcol_numslider", "wcol_text"):
        w = getattr(ui, name)
        _set(w, "inner", FIELD)
        _set(w, "inner_sel", (0.25, 0.25, 0.25))
        _set(w, "text", TEXT)
        _set(w, "text_sel", TEXT)
    _set(ui.wcol_numslider, "item", ACCENT)  # the slider's fill
    _set(ui.wcol_menu_back, "inner", BACK)
    _set(ui.wcol_tooltip, "inner", BACK)
    _set(ui, "panel_header", HEADER)
    _set(ui, "panel_title", TEXT)
    _set(ui, "panel_back", BACK)
    _set(ui, "panel_sub_back", (0.09, 0.09, 0.09))
    _set(ui, "panel_text", TEXT)
    grad = theme.view_3d.space.gradients
    grad.background_type = "LINEAR"
    _set(grad, "high_gradient", VIEW_TOP)
    _set(grad, "gradient", VIEW_BOTTOM)
    preferences.is_dirty = True  # saved with the preferences
