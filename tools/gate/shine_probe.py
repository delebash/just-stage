# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""What the skin's BSDF gets at each pixel - its Roughness or Specular IOR Level - rendered as plain emission at the
gate's views, for ours and HD Aaron alike (a diagnostic: the face's shine against his, plan §0, 2026-11-07; his
shader computes them from maps, cavity, Fresnel and region inputs, so the values are read, not traced).

    python tools/dev.py blender -b --python tools/gate/shine_probe.py -- --who cc5 --input Roughness --views cheek,eye
        --out DIR

Writes `eevee_{view}_{who}_{Input}.png` through the Standard view (sRGB-encoded: decode to linear for the value),
512 px; read inside `measure.WINDOWS`."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("parts_gate", HERE / "parts_gate.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)


def _skin(mat) -> bool:
    nt = mat.node_tree
    return bool(nt) and ("juststage.maps.gain" in nt.nodes or "Skin_Head" in mat.name or "Skin_Body" in mat.name
                         or "Skin_Arm" in mat.name or "Skin_Leg" in mat.name)


def emit(socket_name: str):
    def prepare(built: dict) -> None:
        scene = bpy.context.scene
        n = 0
        for mat in bpy.data.materials:
            if not _skin(mat):
                continue
            nt = mat.node_tree
            for bsdf in [x for x in nt.nodes if x.type == "BSDF_PRINCIPLED"]:
                s = bsdf.inputs[socket_name]
                em = nt.nodes.new("ShaderNodeEmission")
                if s.is_linked:
                    nt.links.new(s.links[0].from_socket, em.inputs["Color"])
                else:
                    em.inputs["Color"].default_value = (s.default_value,) * 3 + (1.0,)
                for link in list(bsdf.outputs[0].links):  # wherever this BSDF went (film or live output), emit
                    nt.links.new(em.outputs[0], link.to_socket)
                n += 1
        for obj in bpy.data.objects:  # strands and cards hidden: the skin alone
            if obj.type == "CURVES" or any(k in obj.name for k in ("Brow", "Lash", "Hair", "Beard")):
                obj.hide_render = True
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        scene.view_settings.exposure = 0.0
        print("EMIT", socket_name, "on", n, "BSDFs", flush=True)
    return prepare


if __name__ == "__main__":
    import argparse

    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="shine_probe.py --")
    p.add_argument("--who", choices=("ours", "cc5"), required=True)
    p.add_argument("--input", default="Roughness")
    p.add_argument("--views", default="cheek,eye")
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(args)
    out = a.out.resolve()
    tag = "_" + a.input.replace(" ", "")
    pg.render(a.who, "eevee", out, a.views.split(","), 512, 1, tag=tag, prepare=emit(a.input))
