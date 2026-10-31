# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""MPFB2's node-tree JSON (`src/mpfb/data/node_trees/*.json`, CC0 data — its LICENSE.md part C) built into Blender
materials: groups with their sockets, nodes with their values and operations, links by socket name or index. Used by
the face test for MPFB2's procedural eye ("EnhancedEye") and skin.
"""

import json

import bpy


def _set_input(node, key, value):
    sockets = node.inputs
    sock = sockets[int(key)] if str(key).isdigit() else sockets.get(key)
    if sock is None or not hasattr(sock, "default_value"):
        return
    try:
        sock.default_value = value
    except (TypeError, ValueError):
        pass


def _fill(tree, nodes, links, build_group):
    made = {}
    for name, spec in nodes.items():
        if spec["type"] == "NodeGroupInput":
            node = next((n for n in tree.nodes if n.type == "GROUP_INPUT"), None) or tree.nodes.new("NodeGroupInput")
        elif spec["type"] == "NodeGroupOutput":
            node = next((n for n in tree.nodes if n.type == "GROUP_OUTPUT"), None) or tree.nodes.new("NodeGroupOutput")
        elif spec["type"] == "ShaderNodeOutputMaterial":
            node = next((n for n in tree.nodes if n.type == "OUTPUT_MATERIAL"), None) or tree.nodes.new(spec["type"])
        else:
            node = tree.nodes.new(spec["type"])
        node.name, node.label = name, spec.get("label", "")
        node.location = spec.get("location", (0, 0))
        if spec["type"] == "ShaderNodeGroup":
            node.node_tree = build_group(spec["group_name"])
        for attr in ("operation", "use_clamp", "blend_type", "data_type", "distribution", "subsurface_method"):
            if attr in spec and hasattr(node, attr):
                setattr(node, attr, spec[attr])
        if spec["type"] == "ShaderNodeValue" and "value" in spec:
            node.outputs[0].default_value = spec["value"]
        if spec["type"] != "NodeGroupOutput":
            for key, value in spec.get("values", {}).items():
                _set_input(node, key, value)
        made[name] = node
    for link in links:
        a, b = made.get(link["from_node"]), made.get(link["to_node"])
        if a is None or b is None:
            continue
        fs, ts = link["from_socket"], link["to_socket"]
        out = a.outputs[int(fs)] if str(fs).isdigit() else a.outputs.get(fs)
        inp = b.inputs[int(ts)] if str(ts).isdigit() else b.inputs.get(ts)
        if out is not None and inp is not None:
            tree.links.new(out, inp)
    return made


def build_material(path, material, prefix):
    """Replace `material`'s nodes with the JSON's tree; the groups are made once per `prefix` (e.g. "mpfb_eye.")."""
    data = json.load(open(path, encoding="utf-8"))

    def build_group(name):
        full = prefix + name
        if full in bpy.data.node_groups:
            return bpy.data.node_groups[full]
        spec = data["groups"][name]
        tree = bpy.data.node_groups.new(full, "ShaderNodeTree")
        for sock, s in spec["inputs"].items():
            item = tree.interface.new_socket(sock, in_out="INPUT", socket_type=s["type"] if isinstance(s, dict) else s)
            if isinstance(s, dict) and "value" in s and hasattr(item, "default_value"):
                try:
                    item.default_value = s["value"]
                except (TypeError, ValueError):
                    pass
        for sock, s in spec["outputs"].items():
            tree.interface.new_socket(sock, in_out="OUTPUT", socket_type=s["type"] if isinstance(s, dict) else s)
        _fill(tree, spec["nodes"], spec["links"], build_group)
        return tree

    nt = material.node_tree
    nt.nodes.clear()
    nt.nodes.new("ShaderNodeOutputMaterial").name = "Material Output"
    return _fill(nt, data["nodes"], data["links"], build_group)
