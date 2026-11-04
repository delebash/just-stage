# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The realism gate's comparison (CPU): every engine's linear EXR through the same look, side by side, with numbers.

    python tools/dev.py blender -b --python tools/gate/compare.py

Light units differ between Blender and Unreal, and light adds linearly: each light was rendered alone in each engine
with an 18% grey sphere beside the head (tools/gate/blender_gate.py SPHERE), so each Unreal light's scale is Cycles'
sphere over Unreal's sphere, and Unreal's stage is the sum of its scaled single-light renders. Blender's own stage
render is checked against the sum of its singles (linearity). Every image then goes through JustStage's look (AgX,
its contrast look, its exposure - core/viewport.py). Crops (cheek, nose, forehead) at 1:1, with their mean luminance,
their fine-detail energy (the standard deviation of a 2-px high-pass) and their highlight share (pixels above twice
the crop's median)."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / ".dev" / "gate"
RENDERS = GATE / "renders"
SHEETS = GATE / "sheets"
sys.path.insert(0, str(Path(__file__).parent))
gate = importlib.import_module("blender_gate")
viewport = importlib.import_module("bl_ext.system.juststage.core.viewport")
LIGHTS = ("key", "rim", "sky")
#: unreal_mh: the MetaHuman benchmark by the render queue (left empty: its actor is editor-only); ue_ours / ue_mh: both
#: characters captured from the editor's viewport (tools/gate/unreal_capture.py) - ue_ours against unreal checks that
#: capture route
ENGINES = ("eevee", "cycles", "unreal", "ue_ours", "ue_mh")
LUMA = np.array([0.2126, 0.7152, 0.0722])
#: crops on the face camera, as fractions of the frame (x, y from the top-left, size): picked on Cycles' face render
CROPS = {"cheek": (0.40, 0.58, 0.12), "nose": (0.50, 0.50, 0.08), "forehead": (0.48, 0.31, 0.10),
         # the shadowed side: where EEVEE and Cycles part (the face sheet, 2026-11-04)
         "under_eye": (0.43, 0.47, 0.07), "jaw_shadow": (0.58, 0.69, 0.08)}


def _load(path: Path) -> np.ndarray | None:
    if not path.exists():
        return None
    image = bpy.data.images.load(str(path), check_existing=False)
    w, h = image.size
    px = np.empty(w * h * 4, np.float32)
    image.pixels.foreach_get(px)
    bpy.data.images.remove(image)
    return px.reshape(h, w, 4)[::-1, :, :3].copy()


def _sphere_disc(cam_name: str, size) -> tuple[np.ndarray, np.ndarray]:
    """The grey sphere's centre and radius in pixels on `cam_name`'s camera (top-left origin)."""
    scene = bpy.context.scene
    cam = scene.objects[f"{cam_name} camera"]
    scene.render.resolution_x, scene.render.resolution_y = size
    centre = Vector(gate.SPHERE[0])
    edge = centre + cam.matrix_world.to_3x3() @ Vector((gate.SPHERE[1], 0.0, 0.0))
    pc, pe = (world_to_camera_view(scene, cam, p) for p in (centre, edge))
    w, h = size
    c = np.array([pc.x * w, (1 - pc.y) * h])
    return c, np.hypot((pe.x - pc.x) * w, (pe.y - pc.y) * h)


def _sphere_mean(img: np.ndarray, centre, radius) -> float:
    """The sphere's lit side: the mean of its brightest fifth (a light from behind - the rim - lights only a crescent
    the camera sees at the edge; the inner disc read noise there, measured 2026-11-04)."""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    lum = img[np.hypot(xx - centre[0], yy - centre[1]) < 0.95 * radius] @ LUMA
    return float(lum[lum >= np.quantile(lum, 0.8)].mean())


def _tonemap(img: np.ndarray, out: Path) -> np.ndarray:
    """Through JustStage's look (core/viewport.py: AgX, its look, its exposure) by Blender's own colour management."""
    scene = bpy.context.scene
    h, w = img.shape[:2]
    image = bpy.data.images.new(out.stem, w, h, float_buffer=True)
    image.pixels.foreach_set(np.ascontiguousarray(np.dstack([img, np.ones((h, w))])[::-1], np.float32).ravel())
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = viewport.LOOK
    scene.view_settings.exposure = viewport.EXPOSURE
    s = scene.render.image_settings
    s.file_format, s.color_mode, s.color_depth, s.color_management = "PNG", "RGB", "8", "FOLLOW_SCENE"
    image.save_render(str(out), scene=scene)
    bpy.data.images.remove(image)
    shown = bpy.data.images.load(str(out), check_existing=False)
    px = np.empty(w * h * 4, np.float32)
    shown.pixels.foreach_get(px)
    bpy.data.images.remove(shown)
    return px.reshape(h, w, 4)[::-1, :, :3].copy()


def _crop(img, frac):
    h, w = img.shape[:2]
    x, y, s = frac
    side = int(s * w)
    x0, y0 = int(x * w - side / 2), int(y * h - side / 2)
    return img[y0:y0 + side, x0:x0 + side]


def _numbers(linear_crop) -> dict:
    lum = linear_crop @ LUMA
    k = 2
    pad = np.pad(lum, k, mode="edge")
    blur = sum(pad[k + dy:k + dy + lum.shape[0], k + dx:k + dx + lum.shape[1]]
               for dy in range(-k, k + 1) for dx in range(-k, k + 1)) / (2 * k + 1) ** 2
    return {"mean": float(lum.mean()), "fine_detail": float((lum - blur).std() / max(lum.mean(), 1e-6)),
            "highlight_share": float((lum > 2 * np.median(lum)).mean())}


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(GATE / "gate_scene.blend"))
    meta = json.loads((GATE / "meta.json").read_text())
    SHEETS.mkdir(parents=True, exist_ok=True)
    report = {"scale": {}, "linearity": {}, "crops": {}}
    for cam_name, size in meta["resolution"].items():
        centre, radius = _sphere_disc(cam_name, size)
        singles = {e: {v: _load(RENDERS / f"{e}_{cam_name}_{v}.exr") for v in (*LIGHTS, "stage")} for e in ENGINES}
        ref = singles["cycles"]
        stage = {}
        for engine in ENGINES:
            got = singles[engine]
            if any(got[v] is None for v in LIGHTS):
                continue
            scales = {}
            for v in LIGHTS:
                scales[v] = (_sphere_mean(ref[v], centre, radius) / _sphere_mean(got[v], centre, radius)
                             if ref[v] is not None else 1.0)
            report["scale"][f"{engine}_{cam_name}"] = scales
            summed = sum(scales[v] * got[v] for v in LIGHTS)
            if got["stage"] is not None and engine != "unreal":
                report["linearity"][f"{engine}_{cam_name}"] = (_sphere_mean(got["stage"], centre, radius) /
                                                               _sphere_mean(summed, centre, radius))
            # Blender's engines keep their own units (scale ~1 to Cycles, reported); Unreal is brought to Cycles'
            stage[engine] = summed if engine.startswith(("unreal", "ue_")) else (
                got["stage"] if got["stage"] is not None else summed)
        shown = {e: _tonemap(img, SHEETS / f"{e}_{cam_name}.png") for e, img in stage.items()}
        engines = [e for e in ENGINES if e in shown]
        if engines:
            sheet = np.concatenate([shown[e] for e in engines], 1)
            _tonemap_write(sheet, SHEETS / f"sheet_{cam_name}.png")
        if cam_name == "face":
            for name, frac in CROPS.items():
                report["crops"][name] = {e: _numbers(_crop(stage[e], frac)) for e in engines}
                row = np.concatenate([_crop(shown[e], frac) for e in engines], 1)
                _tonemap_write(row, SHEETS / f"crop_{name}.png")
    (SHEETS / "report.json").write_text(json.dumps(report, indent=1))
    print("GATE compared:", json.dumps(report))


def _tonemap_write(display: np.ndarray, out: Path) -> None:
    """An already tone-mapped picture written as it is (display values, no transform)."""
    h, w = display.shape[:2]
    image = bpy.data.images.new(out.stem, w, h)
    image.colorspace_settings.name = "Non-Color"
    image.pixels.foreach_set(np.ascontiguousarray(np.dstack([display, np.ones((h, w))])[::-1], np.float32).ravel())
    image.filepath_raw = str(out)
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)


if __name__ == "__main__":
    main()
