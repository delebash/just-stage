# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The quality gate part by part (`docs/standards/quality-gate.md` §3, §5; the bar: CC5's HD Aaron, TASKS "HD AARON IS
THE BAR"): our character and CC5's, each alone on the app's stage, through the same cameras, so only the content
differs. A LOCAL TEST: CC5's character comes from the user's own export and nothing of it ships (AGENTS.md clean-room).

    python tools/dev.py blender -b --python tools/gate/parts_gate.py -- render --who ours --engine eevee
    python tools/dev.py blender -b --python tools/gate/parts_gate.py -- render --who cc5 --engine cycles
    python tools/dev.py blender -b --python tools/gate/parts_gate.py -- sheet

`ours`: built the app's way - the library's Daniel, a scalp style and brows from the hair library, the face's ARKit 52
(`juststage.head.add_face_units`); nothing hidden. `cc5`: HD Aaron as Reallusion's CC Blender Tools imported CC5's
Blender Pipeline export (hair and stubble on), its EEVEE or Cycles build to match the engine.

Every camera is placed from anatomy measured on each character (pupils, the front teeth, the ear, the right hand's and
foot's joints - MakeHuman's joint groups on ours, CC5's bones on Aaron), never from fixed coordinates, so a view frames
the same part on both. The character faces -Y; the key light is on its right (-X), so one-sided views take that side.
The four expressions by ARKit's names on ours and by CC5's own on Aaron, mapped as CC Blender Tools maps them
(`facerig_data.py`, CC5's HD profile: jawOpen -> Jaw_Open, mouthSmileLeft -> Mouth_Corner_Pull_L, browInnerUp ->
Brow_Raise_In_L + _R)."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".dev" / "gate" / "parts"
CC5_DIR = ROOT / ".dev" / "gate" / "cc5_aaron_blender"
CC5_BLEND = {"eevee": CC5_DIR / "aaron_hair_eevee.blend", "cycles": CC5_DIR / "aaron_hair_cycles.blend"}
#: the library's Average man in the Scan man A skin (2026-11-06: Daniel's skin is a face-test AI painting with painted
#: lashes - docs/plans/2026-11-06-inputs-audit.md); recs 11, 8 for the scalp and brows; stubble as hair (build_ours)
OURS = {"character": "Average man", "scalp": "JustStage short combed", "brows": "JustStage brows"}
#: our man's scalp hair as dark as HD Aaron's (2026-11-06: the library style's brown 0.82 with a fifth grey measured
#: L* 42 at the face view against his 22) - his hair's colour, so the hair's shading and structure are what differ;
#: through the app's own juststage.hair.set_colour, the gate's man only (character="" )
SCALP_COLOUR = {"melanin": 0.96, "redness": 0.6}
#: and his little grey (the style's fifth grey strands made it L* 41; a twentieth: 28 at melanin 0.93) - the scalp
#: groom's "Strand colour" modifier input (Blender 5.3: mod.properties.inputs.<identifier>.value)
SCALP_GREY = 0.05
BROW_GREY = 0.2  # his brows: about a fifth of the coarse hairs white (gate run 5's eye view)
LENS = 85.0  # quality-gate.md §3
SENSOR = 36.0
SIZE = 2048
CYCLES_SAMPLES = 256  # quality-gate.md §3: "Cycles (256 samples, OIDN)"
JAW = 0.5  # half open: teeth, gums and tongue in view on both

#: the expressions, by who: shape key -> value (CC Blender Tools' drivers move Aaron's jaw, teeth and tongue bones from
#: his body's keys)
EXPRESSIONS = {
    "neutral": {"ours": {}, "cc5": {}},
    "jawOpen": {"ours": {"jawOpen": JAW}, "cc5": {"Jaw_Open": JAW}},
    "smile": {"ours": {"mouthSmileLeft": 1.0, "mouthSmileRight": 1.0},
              "cc5": {"Mouth_Corner_Pull_L": 1.0, "Mouth_Corner_Pull_R": 1.0}},
    "browInnerUp": {"ours": {"browInnerUp": 1.0}, "cc5": {"Brow_Raise_In_L": 1.0, "Brow_Raise_In_R": 1.0}},
}  # fmt: skip

#: the parts each view shows (quality-gate.md §5's list plus the user's 2026-11-05 "all body parts", toenails too)
VIEWS = {
    "front": ("overall, skin, scalp hair", "neutral"),
    "three_quarter": ("overall, scalp hair, ears", "neutral"),
    "profile": ("overall, scalp hair, ears, lips", "neutral"),
    "face": ("skin, brows, lashes, facial hair", "neutral"),
    "hair_back": ("scalp hair", "neutral"),
    "eye": ("eyes, lashes, brows", "neutral"),
    "lips": ("lips, facial hair", "neutral"),
    "lip_corner": ("lips, skin", "neutral"),
    "cheek": ("skin", "neutral"),
    "ear": ("ears", "neutral"),
    "torso": ("body skin, nipples", "neutral"),
    "hand": ("hands, nails", "neutral"),
    "nails": ("nails", "neutral"),
    "foot": ("feet, toenails", "neutral"),
    "toenails": ("toenails", "neutral"),
    "full": ("overall, body", "neutral"),
    "face_jawOpen": ("expression, teeth", "jawOpen"),
    "mouth_jawOpen": ("teeth and gums, tongue", "jawOpen"),
    "face_smile": ("expression", "smile"),
    "mouth_smile": ("teeth and gums, lips", "smile"),
    "face_browInnerUp": ("expression, brows", "browInnerUp"),
}


# ---- the characters ------------------------------------------------------------------------------------------------

def _stage():
    """An empty scene with the app's settings and stage (core/viewport.py, ui/startup.py), as a new file gets."""
    viewport = importlib.import_module("bl_ext.system.juststage.core.viewport")
    startup = importlib.import_module("bl_ext.system.juststage.ui.startup")
    bpy.ops.wm.read_homefile(use_empty=True)
    scene = bpy.context.scene
    viewport.setup_scene(scene)
    cam = bpy.data.objects.new("gate camera", bpy.data.cameras.new("gate camera"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    startup.new_stage(scene)
    cam.data.sensor_fit, cam.data.sensor_width, cam.data.lens = "HORIZONTAL", SENSOR, LENS
    cam.data.clip_start, cam.data.clip_end = 0.01, 100.0
    return scene, cam


def build_ours(scene, skin: str = "", brows: str = "library", character: str = "", scalp: str = "library",
               stubble: str = "generated") -> dict:
    """The library's man the app's way, with the hair library's scalp style and brows and the face's ARKit 52;
    `skin` (a library skin's .blend) put on him as the Content panel does."""
    api = importlib.import_module("bl_ext.system.juststage.api")
    library = importlib.import_module("bl_ext.system.juststage.core.library")
    root = library.root()
    shown = api.run("juststage.library.add", path=str(root / "Characters" / f"{character or OURS['character']}.blend"))
    if scalp == "generated":  # JustStage's own (modules/hair/scalp.py, rec 11)
        importlib.import_module("bl_ext.system.juststage.modules.hair.scalp").make(
            next(o for o in scene.objects if o.juststage.character_id == shown.character and not o.juststage.part_of))
    else:
        api.run("juststage.library.add", path=str(root / "Hair" / "Scalp" / f"{OURS['scalp']}.blend"),
                character=shown.character)
    if not character:
        for o in list(scene.objects):
            if o.juststage.part_of == shown.character and o.juststage.part == "scalp":
                api.run("juststage.hair.set_colour", groom=o.name, **SCALP_COLOUR)
                mod = o.modifiers.get("Strand colour")
                if mod is not None:
                    ident = next(i.identifier for i in mod.node_group.interface.items_tree
                                 if getattr(i, "in_out", "") == "INPUT" and i.name == "Grey Share")
                    getattr(mod.properties.inputs, ident).value = SCALP_GREY
    if brows == "generated" or not character:  # JustStage's own (modules/hair/brows.py, rec 8); the gate's man greying
        importlib.import_module("bl_ext.system.juststage.modules.hair.brows").make(
            next(o for o in scene.objects if o.juststage.character_id == shown.character and not o.juststage.part_of),
            grey_share=BROW_GREY if not character else 0.0)
    else:
        api.run("juststage.library.add", path=str(root / "Hair" / "Brows" / f"{OURS['brows']}.blend"),
                character=shown.character)
    create = importlib.import_module("bl_ext.system.juststage.modules.body.body_create")
    create.open_eyes(shown.character)  # as a dressed human (the library's characters predate EYE_OPEN)
    api.run("juststage.head.add_face_units", character=shown.character)
    if stubble == "generated":  # HD Aaron wears CC5's Stubble mesh: ours its hairs (modules/hair/stubble.py)
        body0 = next(o for o in scene.objects if o.juststage.character_id == shown.character and not o.juststage.part_of)
        if body0.juststage.gender > 0.5:  # a man's
            importlib.import_module("bl_ext.system.juststage.modules.hair.stubble").make(body0)
    if skin:
        api.run("juststage.library.add", path=skin, character=shown.character)
    objects = [o for o in scene.objects if shown.character in (o.juststage.character_id, o.juststage.part_of)]
    body = next(o for o in objects if not o.juststage.part_of)
    return {"body": body, "objects": objects, "keyed": [body]}


def build_cc5(scene, engine: str, inputs: dict[str, float] | None = None) -> dict:
    """HD Aaron from CC Blender Tools' import, appended with his armature, materials and drivers. `inputs`: values set
    on his skin shaders' group inputs (e.g. "Micro Normal Strength": 0) - one factor at a time, to see what his look
    owes to each map."""
    with bpy.data.libraries.load(str(CC5_BLEND[engine]), link=False) as (src, dst):
        dst.objects = list(src.objects)
    kept = [o for o in dst.objects if o is not None and o.type in {"MESH", "ARMATURE"} and o.name != "Cube"]
    for obj in kept:
        scene.collection.objects.link(obj)
    for obj in dst.objects:  # the import's own camera, light and cube stay out
        if obj is not None and obj not in kept:
            bpy.data.objects.remove(obj)
    body = next(o for o in kept if o.name == "CC_Base_Body")
    for slot in body.material_slots:
        for node in slot.material.node_tree.nodes if slot.material and inputs else ():
            if node.type == "GROUP" and node.node_tree.name.startswith(("rl_head_shader", "rl_skin_shader")):
                for name, value in inputs.items():
                    if name in node.inputs:
                        node.inputs[name].default_value = value
    keyed = [o for o in kept if o.type == "MESH" and o.data.shape_keys]
    return {"body": body, "objects": kept, "keyed": keyed, "armature": next(o for o in kept if o.type == "ARMATURE")}


def set_expression(who: str, built: dict, name: str) -> None:
    values = EXPRESSIONS[name][who]
    every = {k for expr in EXPRESSIONS.values() for k in expr[who]}
    for obj in built["keyed"]:
        blocks = obj.data.shape_keys.key_blocks
        for key in every:
            if key in blocks:
                blocks[key].value = values.get(key, 0.0)
    bpy.context.view_layer.update()


# ---- anatomy -------------------------------------------------------------------------------------------------------

def _world(obj, evaluated: bool = True) -> np.ndarray:
    """An object's vertices in world space (evaluated: shape keys, modifiers, the armature)."""
    if evaluated:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        mesh = obj.evaluated_get(depsgraph).data
    else:
        mesh = obj.data
    co = np.empty(len(mesh.vertices) * 3, np.float64)
    mesh.vertices.foreach_get("co", co)
    m = np.array(obj.matrix_world)
    return co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]


def _pupil(points: np.ndarray) -> Vector:
    """An eyeball's pupil: its centre pushed to its front (the character faces -Y)."""
    centre = points.mean(0)
    return Vector((centre[0], points[:, 1].min(), centre[2]))


def _faces_of(obj, prefixes: tuple[str, ...]) -> dict[str, np.ndarray]:
    """World vertices of the faces whose material name starts with each prefix."""
    co = _world(obj)
    names = [slot.material.name if slot.material else "" for slot in obj.material_slots]
    found: dict[str, list[int]] = {}
    for poly in obj.data.polygons:
        name = names[poly.material_index] if poly.material_index < len(names) else ""
        for prefix in prefixes:
            if name.startswith(prefix):
                found.setdefault(prefix, []).extend(poly.vertices)
    return {k: co[sorted(set(v))] for k, v in found.items()}


def _front_teeth(points: np.ndarray) -> Vector:
    """The mouth's centre: the front teeth's front (within 4 mm of the foremost point), mid-height."""
    front = points[points[:, 1] < points[:, 1].min() + 0.004]
    return Vector((points[:, 0].mean(), front[:, 1].mean(), front[:, 2].mean()))


def _ear(body_points: np.ndarray, pupil: Vector) -> Vector:
    """The right ear: the head's most lateral skin behind and level with the eye, a centimetre in from its rim."""
    p = body_points
    box = p[(p[:, 2] > pupil.z - 0.06) & (p[:, 2] < pupil.z + 0.01) & (p[:, 1] > pupil.y + 0.04)
            & (p[:, 1] < pupil.y + 0.16) & (p[:, 0] < pupil.x)]
    rim = box[np.argsort(box[:, 0])[:40]]
    return Vector((rim[:, 0].mean() + 0.01, rim[:, 1].mean(), rim[:, 2].mean()))


def _joints(body) -> dict[str, Vector]:
    """MakeHuman's joint groups on our body (the mean of each group's vertices, the shape keys as they stand)."""
    mesh = body.data
    n = len(mesh.vertices)
    blocks = mesh.shape_keys.key_blocks
    co = np.empty(n * 3)
    blocks[0].data.foreach_get("co", co)
    total = co.copy()
    for kb in blocks[1:]:
        if kb.mute or kb.value == 0:
            continue
        d, ref = np.empty(n * 3), np.empty(n * 3)
        kb.data.foreach_get("co", d)
        kb.relative_key.data.foreach_get("co", ref)
        total += kb.value * (d - ref)
    m = np.array(body.matrix_world)
    co = total.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]
    names = {g.index: g.name for g in body.vertex_groups}
    groups: dict[str, list[int]] = {}
    for v in mesh.vertices:
        for g in v.groups:
            name = names.get(g.group, "")
            if name.startswith("joint-") and g.weight > 0.5:
                groups.setdefault(name, []).append(v.index)
    return {k: Vector(co[v].mean(0)) for k, v in groups.items()}


def anchors(who: str, built: dict) -> dict[str, Vector]:
    """The points every camera is placed from: pupils, mouth, ear, the right hand (wrist, index and little-finger
    knuckles, middle fingertip) and foot (ankle, ball, big toe's end), each measured on the character."""
    if who == "ours":
        eyes = [_world(o) for o in built["objects"] if o.juststage.part in ("eyeLeft", "eyeRight")]
        teeth = _world(next(o for o in built["objects"] if o.juststage.part == "teeth"))
        j = _joints(built["body"])
        hand = (j["joint-r-hand"], j["joint-r-finger-2-1"], j["joint-r-finger-5-1"], j["joint-r-finger-3-4"])
        foot = (j["joint-r-ankle"], j["joint-r-toe-3-1"], j["joint-r-toe-1-3"])
    else:
        eye_obj = next(o for o in built["objects"] if o.name == "CC_Base_Eye")
        eyes = list(_faces_of(eye_obj, ("Std_Eye_L", "Std_Eye_R")).values())
        teeth = _world(next(o for o in built["objects"] if o.name == "CC_Base_Teeth"))
        arm = built["armature"]

        def bone(name: str, end: str = "head") -> Vector:
            b = arm.data.bones[name]
            return arm.matrix_world @ (b.head_local if end == "head" else b.tail_local)

        hand = (bone("CC_Base_R_Hand"), bone("CC_Base_R_Index1"), bone("CC_Base_R_Pinky1"), bone("CC_Base_R_Mid3", "tail"))
        foot = (bone("CC_Base_R_Foot"), bone("CC_Base_R_ToeBase"), bone("CC_Base_R_BigToe1", "tail"))
    pupils = sorted((_pupil(e) for e in eyes), key=lambda p: p.x)  # image right is +X: [right eye, left eye]
    right_pupil = pupils[0]
    out = {"pupil_r": right_pupil, "pupil_l": pupils[1], "pupils": (pupils[0] + pupils[1]) / 2,
           "mouth": _front_teeth(teeth), "ear_r": _ear(_world(built["body"]), right_pupil)}
    out.update(zip(("wrist", "index1", "pinky1", "middle_tip"), hand))
    out.update(zip(("ankle", "ball", "big_toe"), foot))
    return out


# ---- the views -----------------------------------------------------------------------------------------------------

def _v(x: float, y: float, z: float) -> Vector:
    return Vector((x, y, z))


def view(name: str, a: dict[str, Vector]):
    """(target, direction from the target to the camera, up, frame width in metres) for one view."""
    m, z = a["pupils"], _v(0, 0, 1)
    face, front34 = 0.30, _v(-0.7071, -0.7071, 0)
    if name == "front":
        return m + _v(0, 0, -0.12), _v(0, -1, 0), z, 0.56
    if name == "three_quarter":
        return m + _v(0, 0.04, -0.12), front34, z, 0.56
    if name == "profile":
        return m + _v(0, 0.07, -0.12), _v(-1, 0, 0), z, 0.56
    if name.startswith("face"):
        return m + _v(0, 0, -0.035), _v(0, -1, 0), z, face
    if name == "hair_back":
        return m + _v(0, 0.08, 0.03), _v(-0.5, 0.85, 0.25), z, 0.34
    if name == "eye":
        return a["pupil_r"] + _v(0, 0, 0.004), _v(-0.17, -0.985, 0), z, 0.075
    if name in ("lips", "mouth_jawOpen", "mouth_smile"):
        return a["mouth"] + _v(0, 0, -0.008), _v(0, -1, 0.08), z, 0.09
    if name == "lip_corner":
        return a["mouth"] + _v(-0.022, 0, -0.006), _v(-0.42, -0.906, 0), z, 0.05
    if name == "cheek":
        return a["pupil_r"] + _v(-0.008, 0, -0.045), _v(-0.34, -0.94, 0), z, 0.06
    if name == "ear":
        return a["ear_r"], _v(-1, 0, 0), z, 0.10
    if name == "torso":
        return _v(m.x, m.y, m.z - 0.42), _v(0, -1, 0), z, 0.56
    if name == "full":
        return _v(m.x, m.y, m.z / 2 + 0.05), _v(0, -1, 0), z, 2.0
    if name in ("hand", "nails"):
        along = (a["middle_tip"] - a["wrist"]).normalized()
        across = (a["index1"] - a["pinky1"]).normalized()
        back = along.cross(across).normalized()  # the right hand's back (CC5's palm-down A-pose: up and out)
        if name == "hand":
            return a["wrist"].lerp(a["middle_tip"], 0.55), back, along, 0.24
        return a["middle_tip"] - along * 0.012, (back * 0.85 + along * 0.5).normalized(), along, 0.06
    if name in ("foot", "toenails"):
        forward = a["ball"] - a["ankle"]
        forward = _v(forward.x, forward.y, 0).normalized()
        if name == "foot":
            return a["ankle"].lerp(a["ball"], 0.75), (forward * 0.75 + z * 0.66).normalized(), z, 0.24
        return a["big_toe"], (forward * 0.6 + z * 0.8).normalized(), z, 0.06
    raise KeyError(name)


def place(cam, target: Vector, direction: Vector, up: Vector, width: float) -> None:
    """The camera `width * lens / sensor` from `target` along `direction`, looking at it, `up` up in the frame."""
    distance = width * LENS / SENSOR
    forward = -direction.normalized()
    up = (up - forward * up.dot(forward)).normalized()
    right = forward.cross(up)
    rotation = Matrix((right, up, -forward)).transposed()
    cam.matrix_world = Matrix.Translation(target - forward * distance) @ rotation.to_4x4()


# ---- render --------------------------------------------------------------------------------------------------------

def render(who: str, engine: str, out_dir: Path, names: list[str], size: int, samples: int,
           cc5_inputs: dict[str, float] | None = None, tag: str = "", skin: str = "", brows: str = "library",
           character: str = "", scalp: str = "library", prepare=None, lights: str = "stage",
           variants: list[tuple[str, object]] | None = None) -> None:
    """`prepare(built)`, if given, changes the built character before any render - one factor at a time
    (`tools/gate/factors.py`). `variants` [(tag, prepare)]: the character built once, and before each variant every
    object's materials set back to fresh copies of the built ones (a variant may change only its materials' trees and
    load images - one that changes anything else runs alone) - a trial in about a minute instead of a rebuild's six."""
    scene, cam = _stage()
    built = build_ours(scene, skin, brows, character, scalp) if who == "ours" else build_cc5(scene, engine, cc5_inputs)
    if variants:
        slots = [(obj, i, s.material) for obj in scene.objects for i, s in enumerate(obj.material_slots) if s.material]
        pristine = {m.name: m.copy() for m in {m for _, _, m in slots}}
        for m in pristine.values():
            m.use_fake_user = True
        for vtag, vprepare in variants:
            for obj, i, m in slots:
                obj.material_slots[i].material = pristine[m.name].copy()
            vprepare(built)
            _render_views(who, engine, out_dir, names, size, samples, vtag, built, scene, cam, lights)
        return
    if prepare is not None:
        prepare(built)
    _render_views(who, engine, out_dir, names, size, samples, tag, built, scene, cam, lights)


def _render_views(who, engine, out_dir, names, size, samples, tag, built, scene, cam, lights) -> None:
    if lights == "world":  # the image light alone (rec 1's bound: hair within 10% of Cycles under both lights)
        for obj in scene.objects:
            if obj.type == "LIGHT":
                obj.hide_render = True
    set_expression(who, built, "neutral")
    a = anchors(who, built)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"anchors_{who}.json").write_text(json.dumps({k: [round(c, 5) for c in v] for k, v in a.items()},
                                                            indent=1))
    scene.render.engine = {"eevee": "BLENDER_EEVEE", "cycles": "CYCLES"}[engine]
    if engine == "cycles":
        scene.cycles.device, scene.cycles.samples, scene.cycles.use_denoising = "GPU", samples, True
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    settings = scene.render.image_settings
    settings.file_format, settings.color_depth = "PNG", "8"
    settings.color_mode = "RGBA" if scene.render.film_transparent else "RGB"  # transparent: hair_cover.py's alpha
    settings.color_management = "FOLLOW_SCENE"  # the app's look (AgX), as the live view shows it
    current = "neutral"
    frames_path = out_dir / "frames.json"  # each render's frame width at its target (tools/gate/measure.py's scale)
    frames = json.loads(frames_path.read_text()) if frames_path.exists() else {}
    for name in names:
        expression = VIEWS[name][1]
        if expression != current:
            set_expression(who, built, expression)
            current = expression
        placed = view(name, a)
        place(cam, *placed)
        stem = f"{engine}_{name}_{who}{tag}"
        scene.render.filepath = str(out_dir / f"{stem}.png")
        bpy.ops.render.render(write_still=True)
        frames[stem] = {"width_m": placed[3], "size": size}
        frames_path.write_text(json.dumps(frames, indent=1))
        print("RENDERED", scene.render.filepath, flush=True)


# ---- sheets and numbers --------------------------------------------------------------------------------------------

def _read(path: Path) -> np.ndarray:
    img = bpy.data.images.load(str(path), check_existing=False)
    w, h = img.size
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(h, w, 4)[::-1, :, :3].copy()  # display values 0-1, top row first


def _lab_l(rgb: np.ndarray) -> np.ndarray:
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    y = lin @ np.array([0.2126, 0.7152, 0.0722])
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


def _blur(a: np.ndarray, sigma: float) -> np.ndarray:
    r = int(3 * sigma + 0.5)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    a = np.apply_along_axis(lambda row: np.convolve(np.pad(row, r, mode="edge"), k, "valid"), 1, a)
    return np.apply_along_axis(lambda col: np.convolve(np.pad(col, r, mode="edge"), k, "valid"), 0, a)


def numbers(rgb: np.ndarray) -> dict:
    """The central half of the frame, the stage's dark backdrop left out (L* above 12): mean L*, and fine detail - the
    standard deviation of L* above a 1-px Gaussian (the measure of realism §6c), at 1024 px so both sides match."""
    h, w = rgb.shape[:2]
    if w != 1024:
        step = w // 1024
        rgb = rgb[: h // step * step, : w // step * step].reshape(h // step, step, w // step, step, 3).mean((1, 3))
        h, w = rgb.shape[:2]
    lum = _lab_l(rgb)
    win = lum[h // 4: 3 * h // 4, w // 4: 3 * w // 4]
    fine = win - _blur(win, 1.0)
    mask = win > 12
    if mask.sum() < 100:
        return {"L": None, "fine": None, "cover": round(float(mask.mean()), 3)}
    return {"L": round(float(win[mask].mean()), 1), "fine": round(float(fine[mask].std()), 3),
            "cover": round(float(mask.mean()), 3)}


def sheet(out_dir: Path) -> None:
    """Each view and engine: ours left, CC5's right (1024 px each), and the numbers beside them in `numbers.json`."""
    sheets = out_dir / "sheets"
    sheets.mkdir(parents=True, exist_ok=True)
    report = {}
    for engine in ("eevee", "cycles"):
        for name in VIEWS:
            pair = [out_dir / f"{engine}_{name}_{who}.png" for who in ("ours", "cc5")]
            if not all(p.exists() for p in pair):
                continue
            imgs = [_read(p) for p in pair]
            report[f"{engine}_{name}"] = {"parts": VIEWS[name][0], "ours": numbers(imgs[0]), "cc5": numbers(imgs[1])}
            small = []
            for img in imgs:
                step = max(1, img.shape[1] // 1024)
                h, w = img.shape[0] // step * step, img.shape[1] // step * step
                small.append(img[:h, :w].reshape(h // step, step, w // step, step, 3).mean((1, 3)))
            gap = np.ones((small[0].shape[0], 8, 3))
            both = np.concatenate([small[0], gap, small[1]], 1)
            img = bpy.data.images.new(f"{engine}_{name}", both.shape[1], both.shape[0])
            img.pixels.foreach_set(np.dstack([both[::-1], np.ones(both.shape[:2])]).astype(np.float32).ravel())
            img.filepath_raw = str(sheets / f"{engine}_{name}.png")
            img.file_format = "PNG"
            img.save()
            bpy.data.images.remove(img)
    (out_dir / "numbers.json").write_text(json.dumps(report, indent=1))
    print("SHEETS", len(report))


if __name__ == "__main__":
    import argparse

    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="parts_gate.py --")
    p.add_argument("command", choices=("render", "sheet"))
    p.add_argument("--who", choices=("ours", "cc5"))
    p.add_argument("--engine", choices=("eevee", "cycles"), default="eevee")
    p.add_argument("--out", type=Path, default=OUT / "2026-11-05")
    p.add_argument("--views", default=",".join(VIEWS))
    p.add_argument("--size", type=int, default=SIZE)
    p.add_argument("--samples", type=int, default=CYCLES_SAMPLES)
    p.add_argument("--cc5-inputs", default="", help='"Name=value;Name=value" on his skin shaders (a diagnostic)')
    p.add_argument("--tag", default="", help="appended to the file names (a diagnostic's variant)")
    p.add_argument("--skin", default="", help="a library skin (.blend) on ours, as the Content panel applies it")
    p.add_argument("--brows", choices=("library", "generated"), default="library")
    p.add_argument("--character", default="", help="another library character for ours")
    p.add_argument("--scalp", choices=("library", "generated"), default="library")
    p.add_argument("--lights", choices=("stage", "world"), default="stage", help="world: the image light alone")
    a = p.parse_args(args)
    out = a.out if a.out.is_absolute() else ROOT / a.out  # Blender resolves a bare relative path from C:\
    if a.command == "render":
        inputs = {k.strip(): float(v) for k, v in (pair.split("=") for pair in a.cc5_inputs.split(";") if pair)}
        render(a.who, a.engine, out, a.views.split(","), a.size, a.samples, inputs, a.tag, a.skin, a.brows, a.character,
               a.scalp, lights=a.lights)
    else:
        sheet(out)
