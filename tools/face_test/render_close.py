# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Face test: the finished round scene (round.blend) rendered from the close "face" camera at a larger size - is the
4096 head tile, with the shader's tiling pore detail, sharp enough for a 2K close-up, or does it need the 8K face
(open item (a), `docs/plans/2026-11-03-open-items.md`: the whole head at 8192 needs more than ~19 GB)? Writes
close_<size>.png beside the round's own 1024-px render.

Run: blender -b --factory-startup --python tools/face_test/render_close.py -- [SIZE]   (default 2048; the card)
"""

import json
import sys

import bpy
from mathutils import Matrix

DIR = "E:/Dev/3D/just-stage/.dev/facetest/"


def main(argv):
    size = int(argv[0]) if argv else 2048
    bpy.ops.wm.open_mainfile(filepath=DIR + "round.blend")
    scene = bpy.context.scene
    cam = json.load(open(DIR + "cameras.json"))["face"]
    scene.camera.matrix_world = Matrix(cam["matrix_world"])
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = DIR + f"close_{size}.png"
    bpy.ops.render.render(write_still=True)
    print(f"rendered the face camera at {size} px: {scene.render.filepath}")


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
