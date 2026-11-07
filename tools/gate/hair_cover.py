# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The scalp hair alone, its coverage as alpha - the plan's §14 groom measure (HairCS's silhouette IoU), ours and HD
Aaron's alike (his hair is cards with alpha, ours strands): every object but the scalp hair hidden from the render,
the film transparent, so a pixel's alpha is how much hair covers it. EEVEE, the gate's views (plan §0, 2026-11-07).

    python tools/dev.py blender -b --python tools/gate/hair_cover.py -- --who cc5 --views hair_back,profile,front
        --out DIR

Writes `eevee_{view}_{who}_cover.png` (RGBA); the IoU is read beside the gate's own renders."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("parts_gate", HERE / "parts_gate.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)

#: his scalp hair's objects (CC5's export: "Classic Slick Back" cards) and ours (a Curves groom named by scalp.NAME)
SCALP_WORDS = ("scalp", "slick", "hair")
NOT_SCALP = ("brow", "lash", "beard", "stubble", "body", "eye", "teeth", "tongue")


def _is_scalp(obj) -> bool:
    name = obj.name.lower()
    return any(w in name for w in SCALP_WORDS) and not any(w in name for w in NOT_SCALP)


def only_hair(built: dict) -> None:
    kept = []
    for obj in bpy.data.objects:
        if obj.type in ("MESH", "CURVES") and not _is_scalp(obj):
            obj.hide_render = True
        elif obj.type in ("MESH", "CURVES"):
            kept.append(obj.name)
    scene = bpy.context.scene
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = "RGBA"
    print("HAIR ONLY:", kept, flush=True)
    if not kept:
        raise RuntimeError("no scalp hair object found")


if __name__ == "__main__":
    import argparse

    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="hair_cover.py --")
    p.add_argument("--who", choices=("ours", "cc5"), required=True)
    p.add_argument("--views", default="hair_back,profile,front")
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(args)
    pg.render(a.who, "eevee", a.out.resolve(), a.views.split(","), 1024, 1, tag="_cover", prepare=only_hair)
