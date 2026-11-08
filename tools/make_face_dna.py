# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face rig's DNA (`docs/standards/skeleton-and-face.md` §2.3; the job's doc `docs/plans/2026-11-08-face-rig.md`
step 3): MetaHuman's control names - the user's item 10, names only - with every value ours, written by OpenRigLogic's
own writer (MIT; the extension's wheel). From the user's MetaHuman archetype (`SKM_Face.dna` in their Unreal install,
read per machine, as Manny's places were) it takes the 174 GUI control names, the 251 `CTRL_expressions.*` raw control
names and each GUI control's direction (which raw control its positive and negative halves move - an interface
convention, recorded in RESEARCH §14.7); nothing else. Ours: the GUI -> raw ramps (a half 0..1 -> its raw control
0..1), the raw -> blend-shape channel links (CHANNELS: an expression to the ARKit key of ours it names one-to-one) and
the joints - the jaw (`FACIAL_C_Jaw`, the skeleton's face bone) turned and shifted by the jaw expressions by the
amounts our own jaw units move it, measured here on the average man as the teeth's stand-in keys read them (the chin's
turn about the mouth joint for jawOpen, the chin's shift for the others), in DNA units (cm, degrees) along the bone's
own axes.

    python tools/dev.py blender -b --python tools/make_face_dna.py -- [path to SKM_Face.dna]

Writes `extension/juststage/data/generated/rig/face.dna`."""

from __future__ import annotations

import sys
from pathlib import Path

import dna

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "extension" / "juststage" / "data" / "generated" / "rig" / "face.dna"
ARCHETYPE = Path("F:/Epic/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/Content/ArchetypeDNA/SKM_Face.dna")
EXPRESSION = "CTRL_expressions."

#: MetaHuman's expression -> our ARKit key, where the one names the other (ours: `face_units.ARKIT`). MetaHuman's L / R
#: and ARKit's Left / Right are the face's own sides; a look "Left" turns the left eye out and the right eye in.
_SIDED = {
    "browDown{s}": "browDown{S}", "browRaiseOuter{s}": "browOuterUp{S}", "eyeBlink{s}": "eyeBlink{S}",
    "eyeWiden{s}": "eyeWide{S}", "eyeSquintInner{s}": "eyeSquint{S}", "eyeCheekRaise{s}": "cheekSquint{S}",
    "eyeLookUp{s}": "eyeLookUp{S}", "eyeLookDown{s}": "eyeLookDown{S}", "noseWrinkle{s}": "noseSneer{S}",
    "mouthUpperLipRaise{s}": "mouthUpperUp{S}", "mouthLowerLipDepress{s}": "mouthLowerDown{S}",
    "mouthCornerPull{s}": "mouthSmile{S}", "mouthStretch{s}": "mouthStretch{S}", "mouthDimple{s}": "mouthDimple{S}",
    "mouthCornerDepress{s}": "mouthFrown{S}",
}  # fmt: skip
CHANNELS = {k.format(s=s): v.format(S=S) for k, v in _SIDED.items() for s, S in (("L", "Left"), ("R", "Right"))}
CHANNELS.update({
    "eyeLookLeftL": "eyeLookOutLeft", "eyeLookRightL": "eyeLookInLeft",
    "eyeLookLeftR": "eyeLookInRight", "eyeLookRightR": "eyeLookOutRight",
    "mouthLeft": "mouthLeft", "mouthRight": "mouthRight", "jawOpen": "jawOpen", "jawLeft": "jawLeft",
    "jawRight": "jawRight", "jawFwd": "jawForward", "tongueOut": "tongueOut",
})  # fmt: skip


#: the jaw's expressions -> our units whose chin motion the jaw takes (MetaHuman's `jawFwd` is our `jawForward`)
JAW_UNITS = {"jawOpen": "jawOpen", "jawLeft": "jawLeft", "jawRight": "jawRight", "jawFwd": "jawForward"}
CHIN_SHARE = 0.8  # the chin: the skin a jaw unit moves by at least this share of its largest move (bone under skin)
JAW = "FACIAL_C_Jaw"


def jaw_motions() -> dict[str, list[float]]:
    """Each jaw expression's motion of `FACIAL_C_Jaw` - (tx, ty, tz) cm and (rx, ry, rz) degrees along the bone's own
    axes - read off our units' chin on the average man (a character made here and removed)."""
    import importlib

    import bpy
    import numpy as np

    api = importlib.import_module("bl_ext.system.juststage.api")
    build = importlib.import_module("bl_ext.system.juststage.modules.body.build")
    face_units = importlib.import_module("bl_ext.system.juststage.modules.head.face_units")
    made = api.run("juststage.body.create", name="Face DNA measure")
    try:
        body = bpy.data.objects[made.object]
        face_units.add(body)  # the units alone - the command would attach the face rig this file makes
        arm = bpy.data.objects[api.run("juststage.rig.add_skeleton", character=made.character).object]
        bone = arm.data.bones[JAW]
        rest = np.array(bone.matrix_local)[:3, :3]  # the bone's axes in the armature's (= the body's) space
        if np.abs(rest[:, 0] - (1.0, 0.0, 0.0)).max() > 1e-3:
            raise RuntimeError(f"{JAW}'s X axis {rest[:, 0]} is not the face's left-right axis")
        hinge = np.array(bone.head_local)
        shaped = build.shaped_coords(body)
        keys = body.data.shape_keys
        basis = np.empty(len(body.data.vertices) * 3, np.float32)
        keys.reference_key.data.foreach_get("co", basis)
        out = {}
        for expression, unit in JAW_UNITS.items():
            co = np.empty(len(body.data.vertices) * 3, np.float32)
            keys.key_blocks[unit].data.foreach_get("co", co)
            offsets = (co - basis).reshape(-1, 3).astype(np.float64)
            moved = np.linalg.norm(offsets, axis=1)
            chin = moved >= CHIN_SHARE * moved.max()
            if expression == "jawOpen":  # a turn about the left-right axis through the hinge
                a = shaped[chin] - hinge
                b = a + offsets[chin]
                turn = np.arctan2(a[:, 1] * b[:, 2] - a[:, 2] * b[:, 1], a[:, 1] * b[:, 1] + a[:, 2] * b[:, 2])
                angle = float((turn * moved[chin]).sum() / moved[chin].sum())
                out[expression] = [0.0, 0.0, 0.0, float(np.degrees(angle)), 0.0, 0.0]
            else:  # the chin's shift, in the bone's axes
                shift = rest.T @ offsets[chin].mean(0) * 100.0
                out[expression] = [*map(float, shift), 0.0, 0.0, 0.0]
        return out
    finally:
        for obj in [o for o in bpy.data.objects if o.juststage.part_of == made.character]:
            bpy.data.objects.remove(obj)
        bpy.data.objects.remove(bpy.data.objects[made.object])


def _splits() -> dict[str, str]:
    """MetaHuman's finer expressions -> our split channels (`face_rig.SPLIT_EXPRESSIONS`: the shapes and the DNA share
    one table)."""
    import importlib

    return importlib.import_module("bl_ext.system.juststage.modules.head.face_rig").SPLIT_EXPRESSIONS


def _read(path: Path, layer):
    stream = dna.FileStream(str(path), dna.FileStream.AccessMode_Read, dna.FileStream.OpenMode_Binary)
    reader = dna.BinaryStreamReader(stream, layer)
    reader.read()
    if not dna.Status.isOk():
        raise RuntimeError(f"reading {path}: {dna.Status.get().message}")
    return reader


def archetype(path: Path) -> tuple[list[str], list[str], list[tuple[str, str, int]]]:
    """(GUI names, expression raw names, (GUI, raw expression, direction +1 / -1) per GUI -> raw entry) - names and
    directions only."""
    r = _read(path, dna.DataLayer_Behavior)
    gui = [r.getGUIControlName(i) for i in range(r.getGUIControlCount())]
    raw = [r.getRawControlName(i) for i in range(r.getRawControlCount())]
    links = []
    fr, to = r.getGUIToRawFromValues(), r.getGUIToRawToValues()
    for k, (g, o) in enumerate(zip(r.getGUIToRawInputIndices(), r.getGUIToRawOutputIndices(), strict=True)):
        if raw[o].startswith(EXPRESSION):
            links.append((gui[g], raw[o], 1 if max(fr[k], to[k]) > 0 else -1))
    return gui, [n for n in raw if n.startswith(EXPRESSION)], sorted(set(links))


def write(path: Path, gui: list[str], raw: list[str], links: list[tuple[str, str, int]],
          jaw: dict[str, list[float]]) -> dict:
    table = {**CHANNELS, **_splits()}  # expression -> channel: one-to-one onto our units, or a part of one
    channels = sorted(set(table.values()))
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = dna.FileStream(str(path), dna.FileStream.AccessMode_Write, dna.FileStream.OpenMode_Binary)
    w = dna.BinaryStreamWriter(stream)
    w.setName("JustStage face")
    w.setLODCount(1)
    w.setDBMaxLOD(0)
    for i, name in enumerate(gui):
        w.setGUIControlName(i, name)
    for i, name in enumerate(raw):
        w.setRawControlName(i, name)
    w.setJointName(0, "FACIAL_C_FacialRoot")
    w.setJointName(1, JAW)
    w.setJointIndices(0, [0, 1])
    w.setLODJointMapping(0, 0)
    w.setJointHierarchy([0, 0])
    w.setNeutralJointTranslations([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])  # outputs are the joints' moves from rest
    w.setNeutralJointRotations([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    for i, name in enumerate(channels):
        w.setBlendShapeChannelName(i, name)
    w.setBlendShapeChannelIndices(0, list(range(len(channels))))
    w.setLODBlendShapeChannelMapping(0, 0)
    # GUI -> raw: each half of a control a plain ramp onto its expression (ours: 0..1 -> 0..1, -1..0 -> 1..0)
    gi = {n: i for i, n in enumerate(gui)}
    ri = {n: i for i, n in enumerate(raw)}
    rows = [(gi[g], ri[o], (0.0, 1.0, 1.0) if d > 0 else (-1.0, 0.0, -1.0)) for g, o, d in links]
    w.setGUIToRawInputIndices([g for g, _, _ in rows])
    w.setGUIToRawOutputIndices([o for _, o, _ in rows])
    w.setGUIToRawFromValues([v[0] for _, _, v in rows])
    w.setGUIToRawToValues([v[1] for _, _, v in rows])
    w.setGUIToRawSlopeValues([v[2] for _, _, v in rows])
    w.setGUIToRawCutValues([0.0] * len(rows))
    w.setPSDCount(0)
    w.setJointRowCount(9 * 2)  # 9 attributes a joint: tx ty tz rx ry rz sx sy sz
    w.setJointColumnCount(len(raw))
    # the jaw: one group, the jaw expressions in, the jaw's moved attributes out (row-major: outputs x inputs)
    inputs = [ri[EXPRESSION + e] for e in jaw]
    attributes = sorted({a for move in jaw.values() for a, v in enumerate(move) if abs(v) > 1e-9})
    w.setJointGroupJointIndices(0, [1])
    w.setJointGroupInputIndices(0, inputs)
    w.setJointGroupOutputIndices(0, [9 * 1 + a for a in attributes])
    w.setJointGroupValues(0, [jaw[e][a] for a in attributes for e in jaw])
    w.setJointGroupLODs(0, [len(attributes)])
    # raw -> channel, one input each
    ci = {n: i for i, n in enumerate(channels)}
    pairs = [(ri[EXPRESSION + e], ci[c]) for e, c in sorted(table.items()) if EXPRESSION + e in ri]
    w.setBlendShapeChannelLODs([len(pairs)])
    w.setBlendShapeChannelInputIndices([i for i, _ in pairs])
    w.setBlendShapeChannelOutputIndices([o for _, o in pairs])
    w.write()
    if not dna.Status.isOk():
        raise RuntimeError(f"writing {path}: {dna.Status.get().message}")
    missing = sorted(e for e in table if EXPRESSION + e not in ri)
    return {"gui": len(gui), "raw": len(raw), "gui_to_raw": len(rows), "channels": len(channels),
            "linked": len(pairs), "names_missing": missing,
            "jaw": {e: [round(v, 3) for v in m] for e, m in jaw.items()}}  # fmt: skip


def main(argv: list[str]) -> dict:
    source = Path(argv[0]) if argv else ARCHETYPE
    gui, raw, links = archetype(source)
    report = write(OUT, gui, raw, links, jaw_motions())
    print(f"FACE DNA {OUT}: {report}", flush=True)
    return report


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
