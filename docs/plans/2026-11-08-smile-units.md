# ICT's scanned smile as our smile units (build queue §19.4 item 6, Q-RIG-1's per-shape pick) — read this FIRST after any compaction

The job: the smile shapes (§18a row 9: "a scanned set strong in the cheek (Q-RIG-1's scoring) or shapes authored to
his fold"). The user's rule (2026-11-08): "if you can you will continue with the rest of the features of the app".
Mine under the go, logged in the plan's §19.3.

## Where it stands

- 2026-11-08: ICT-FaceKit's `mouthSmile_L/R` and `cheekSquint_L/R` fetched at the pinned commit (byte-identical to
  the 11-07 download), carried with the blink in one run (`.dev/gate/smile/carry_units.log`: wrap p50 0.53 / p90 2.21
  mm; mouthSmile 15.0 mm, cheekSquint 5.9 mm, each on its side; the blink's carry unchanged to the bit), written as
  units (`tools/make_ict_units.py`), `face_units.ICT_UNITS` widened, the face test widened, ATTRIBUTION widened.
  Rendering the smile views ours / his (`scratchpad/batch_F.sh` -> `.dev/gate/parts/2026-11-08smile`). Unverified.

## The pick and why

- Evidence (RESEARCH §14.7, 2026-11-07): MediaPipe's Face Landmarker scores the full smile ours-with-ICT 0.83 / 0.84,
  ours-with-Faceunits 0.72 / 0.79, his 0.86 / 0.85; corners up ICT 11.4 mm (0.91 of his); by eye ICT lifts the corners
  and the cheeks as his do, Faceunits bends the mouth alone. Not picked: `eyeSquint` (never measured alone - stays
  Faceunits').
- Attack: (A) Q-RIG-1 asks for scoring every set against D3DFACS's AU scans and Aaron - this is the per-shape pick on
  the shapes measured, as the blink was (§19.4); the harness stays open. (B) Our lips stay full in either set, and his
  smile line is his face's shape (row 9) - neither set gives it; ICT is the nearer. (C) ICT narrows the eye 1.5 mm in
  the full smile against his 0.4 (cheekSquint) - a Duchenne smile narrows the eye; the render decides. (D) Licence: MIT,
  its row widened. Nothing new in a further pass.

## Next

- Look at `2026-11-08smile` against his and the 07all Faceunits renders; measure with `tools/gate/smile_measure.py`;
  then the library rebuild (its characters carry face units only when the gate adds them - check), the suites.
