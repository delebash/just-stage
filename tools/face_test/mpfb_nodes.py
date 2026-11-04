# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""MPFB2's node-tree JSON into Blender materials: the app's (core/node_trees.py), re-exported for the face test."""

import importlib

build_material = importlib.import_module("bl_ext.system.juststage.core.node_trees").build_material
