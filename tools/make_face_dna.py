# SPDX-FileCopyrightText: 2026 JustStage contributors
# SPDX-License-Identifier: GPL-3.0-or-later

"""The face rig's DNA (`docs/standards/skeleton-and-face.md` §2.3; the job's doc `docs/plans/2026-11-08-face-rig.md`
step 3): MetaHuman's control names - the user's item 10, names only - with every value ours, written by OpenRigLogic's
own writer (MIT; the extension's wheel). From the user's MetaHuman archetype (`SKM_Face.dna` in their Unreal install,
read per machine, as Manny's places were) it takes the 174 GUI control names, the 251 `CTRL_expressions.*` raw control
names and each GUI control's direction (which raw control its positive and negative halves move - an interface
convention, recorded in RESEARCH §14.7); nothing else. Ours: the GUI -> raw ramps (a half 0..1 -> its raw control
0..1), the raw -> blend-shape channel links (CHANNELS: an expression to the ARKit key of ours it names one-to-one) and
the joints (next increment: the jaw).

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


def write(path: Path, gui: list[str], raw: list[str], links: list[tuple[str, str, int]]) -> dict:
    channels = sorted(set(CHANNELS.values()))
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
    w.setJointIndices(0, [0])
    w.setLODJointMapping(0, 0)
    w.setJointHierarchy([0])
    w.setNeutralJointTranslations([[0.0, 0.0, 0.0]])
    w.setNeutralJointRotations([[0.0, 0.0, 0.0]])
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
    w.setJointRowCount(9)
    w.setJointColumnCount(len(raw))
    # raw -> channel, one input each
    ci = {n: i for i, n in enumerate(channels)}
    pairs = [(ri[EXPRESSION + e], ci[c]) for e, c in sorted(CHANNELS.items()) if EXPRESSION + e in ri]
    w.setBlendShapeChannelLODs([len(pairs)])
    w.setBlendShapeChannelInputIndices([i for i, _ in pairs])
    w.setBlendShapeChannelOutputIndices([o for _, o in pairs])
    w.write()
    if not dna.Status.isOk():
        raise RuntimeError(f"writing {path}: {dna.Status.get().message}")
    missing = sorted(e for e in CHANNELS if EXPRESSION + e not in ri)
    return {"gui": len(gui), "raw": len(raw), "gui_to_raw": len(rows), "channels": len(channels),
            "linked": len(pairs), "names_missing": missing}  # fmt: skip


def main(argv: list[str]) -> dict:
    source = Path(argv[0]) if argv else ARCHETYPE
    gui, raw, links = archetype(source)
    report = write(OUT, gui, raw, links)
    print(f"FACE DNA {OUT}: {report}", flush=True)
    return report


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
