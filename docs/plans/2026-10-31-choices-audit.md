# The face pipeline's choices, audited (2026-10-31)

The user, 2026-10-31: "do we need to again re-eavalute all your choices in tools and methods … how do we fix this?",
then "go" on the audit (`../dev/TASKS.md`, ALIGNMENT AND THE AUDIT). One row per job the face test does. **Chosen by**
names the logged research that picked the tool (a `RESEARCH.md` line or a plan file) — or **NOT RESEARCHED** when the
tool was picked without a search for that job (a quick test pick, carried forward). Every NOT RESEARCHED row is
researched the user's way — plain searches, "X vs Y", "alternatives to X", the job's leaderboard, named candidates on
GitHub / arXiv / Hugging Face, the code read, measured here — before more is built on it.

**Corrected 2026-10-31, the same day:** the first version of this table marked nine jobs NOT RESEARCHED after a grep of
`RESEARCH.md` for the tools' names only. The plan files (`2026-10-29-research-*`, `2026-10-30-research-*`) cover nearly
all of them. The failure is not missing research: the research was not read, or not followed, when the face test's
tools were picked. The rows now say which, and the research agents first extract and apply what those files found,
searching only for real gaps.

The app's own stack (Blender, OpenRigLogic, USD, the standards spec) came out of the 2026-10-29 research passes and the
approved rec list; its "one way per job" table (`../standards/README.md`) gets the same check as a second pass.

| # | Job | Tool / method now | Chosen by | Measured here | Status |
|---|-----|-------------------|-----------|---------------|--------|
| 1 | Head base and identity | GNM identity on MakeHuman hm08 | research 05 (bases), RESEARCH §5 | wrap error in the report | researched |
| 2 | Painting each view as a photo | FLUX 3 Image Klein (sd-cli) | `2026-10-30-research-image-models.md` | drift 6–13 px vs FLUX.2's 14–44 | researched |
| 3 | Aligning each painting to its view (coarse) | MediaPipe 478 points, thin-plate spline | research exists, not consulted when picked (RESEARCH: "face landmarks as the backstop"; `2026-10-30-research-ai-photo-to-head.md` rates MediaPipe "weak as the only shape signal") | 3.7–10.1 px after warp; no face found on the profile views | test approved: vs RealDenseFace 5,023 points, leave-one-out judge |
| 4 | Aligning (local) | none | Floating Textures / Dellepiane (RESEARCH, 2026-10-31) | — | approved, to build |
| 5 | Surface normals from the paintings | Sapiens2 1B normal | RESEARCH (normals measured) | 8.5–12.7° from our mesh vs DAViD's 9.6–15.9° | researched |
| 6 | Taking the light out of each painting | own constrained light fit + clay occlusion | realism rec 3 ("the no-model way leads"; Marigold V2 fallback) | shading error 0.12 | researched (method) |
| 7 | Blending views onto the UV map | two-band blend, per-view global gains | realism rec 2 (Waechter et al. 2014) | — | researched; only the global gains of Waechter's levelling built |
| 8 | UV island margins | 16-texel padding | standard bake practice | removed seam-fill bleed | standard, no search logged (low risk) |
| 9 | Skin material | Principled BSDF, Random Walk SSS, Donner & Jensen chromophores | RESEARCH (skin optics, NIST calibration) | mean RMS 0.0098 on NIST skins | researched |
| 10 | Skin detail shading | cavity → specular, coat 0.12, sheen 0.1 | realism rec 5, `2026-10-30-research-skin-detail-shading.md` | — | researched |
| 11 | Pores | paintings' own + Lee Perry-Smith scan tile | realism rec 5; compared rounds 27–29 | alike at portrait distance | researched |
| 12 | Eye shader | MPFB2 EnhancedEye | RESEARCH (MPFB2 nodes), after the user's push | eye shape within a few % of the painting | researched; rec 6's ICT-FaceKit occlusion, tearline, caruncle not built |
| 13 | Eye white shading near the lids | Cycles AO node, cornea split off | research exists — NOT FOLLOWED: rec 6 and `2026-10-30-research-hair-eyes-teeth.md` name an eye occlusion mesh (ICT-FaceKit); I used an AO node | brightest tenth 0.258 vs painting 0.248 | to research (MetaHuman's eye occlusion is rec 6) |
| 14 | Catch light in the eyes | small area light, light-linked to the eyes | research exists (`2026-10-30-research-skin-detail-shading.md`) — whether followed: being checked | — | to research |
| 15 | Lashes | MakeHuman CC0 cards, lower set dropped | RESEARCH (MakeHuman system assets) | 96 upper cards | researched (cards); count vs rec 7 to check |
| 16 | Brows | the paintings' own, in the skin (cards dropped) | research exists — NOT FOLLOWED: rec 7 and `2026-10-30-research-hair-eyes-teeth.md` (brows as hair at real counts); round 43 trials chose the painted brows | — | to research (deviates from rec 7) |
| 17 | Closing the mouth | own shape key | research exists (CC5 research 02, references 04, `2026-10-30-research-all-functions.md`, `../standards/skeleton-and-face.md`: expressions from a rig) — NOT FOLLOWED: own shape key | seam 0.003 vs painting 0.004 | to research (an expression rig's way) |
| 18 | Bringing the lids to the iris | own shape key, per 10° slice | research exists (same files: lids from the rig's expressions) — NOT FOLLOWED: own shape key | opening/width 0.340 vs 0.339 | to research |
| 19 | Matching the render's tone and exposure to the painting | own linear-EXR gain fit | research exists (`2026-10-30-research-skin-detail-shading.md`, `-hair-eyes-teeth.md`, `-comfyui-flame.md`) — whether followed: being checked | — | to research |
| 20 | Matching the render's light to the painting's | own grid fit (fill, azimuth, elevation, size) | research exists (`2026-10-30-research-ai-texturing.md`, `-skin-detail-shading.md`, `-all-functions.md`, `-comfyui-flame.md`) — whether followed: being checked | shading error 0.12 | to research (light estimation from a portrait) |
| 21 | Face shape from the paintings | RealDenseFace + FLAME 2023 Open | realism rec 4 | fits 2–5 px; change not applied (agreement −0.06…+0.57) | researched; measured; set aside |
| 22 | Relief as geometry | Nehab et al. 2005 on the texel grid | RESEARCH (2026-10-31) | synthetic: 0.006 mm RMS | researched; round 48 |
| 23 | Rendering displacement | Blender 5.3 adaptive subdivision | realism rec 5 | — | researched |
| 24 | Iris points (eye colour sampling) | MediaPipe iris (468–477) | research exists (`2026-10-30-research-hair-eyes-teeth.md`, `-ai-photo-to-head.md`) — whether followed: being checked | — | to research |
| 25 | Measuring (lips, eyes, drift) | MediaPipe, RealDenseFace beside it | research exists (`2026-10-30-research-ai-photo-to-head.md`: dense landmarks) — whether followed: being checked | the two disagree 5–8 px | to research |
| 26 | Sharper skin textures | not built (SeedVR2 planned) | realism rec 8 | — | researched, not built |

## Verified 2026-10-31 — what the earlier research actually says, read passage by passage

| # | Job | Earlier research (file : lines, evidence) | Followed? | Gap left |
|---|-----|--------------------------------------------|-----------|----------|
| 3 | Aligning paintings | `2026-10-30-research-ai-texturing.md` §0.3 (~88–108): rec (3) "optical-flow / landmark alignment of each view to the already-painted texture before projecting", landmarks "the backstop for eyes, nose, lips" | **NO** — only the landmark warp was built | none: build the flow step (approved today) |
| 7 | Blending views | same rec (4): "graph-cut view choice + seam leveling + Poisson blend in UV" | **partly** — per-view global gains only | none: build (4) |
| 13 | Eye white near the lids | `2026-10-30-research-hair-eyes-teeth.md` §5a (~332–356): CC5 / MetaHuman layer stack — Eye Occlusion "for the shadow cast from the eyelids", Tearline, caruncle (CC5 manual, page read); ICT-FaceKit meshes (MIT, API); iris ~3.6 mm deep (Navarro, page read); realism rec 6 | **NO** — an AO node instead; the iris flat on the eyeball | how the layers are shaded and fitted (agent) |
| 14 | Catch light | `2026-10-30-research-skin-detail-shading.md` §4 (~403–432): "The key's shape must show as a catchlight in the cornea" (from snippets and reasoning); MNEE shadow caustics through the cornea (manual, page read) | **NO** — a separate light linked to the eyes; no MNEE | verify the snippets; pros' practice (agent) |
| 16 | Brows | `…hair-eyes-teeth.md` §3 step 8 (~287): one snippet-level line; CC5 research: brows follow face vertices | thin research; we use the painted brows | placing and fitting brows to a face or photo (agent) |
| 17, 18 | Mouth closed, lids relaxed | `2026-10-30-research-all-functions.md` (~244–258): rank 1 deformation transfer (Sumner & Popović 2004) of the 52 ARKit shapes from MPFB2 Faceunits 01 (CC0) or ICT-FaceKit (MIT) — [prior]/[known] marks; `2026-10-29-research-02-cc5.md` (~446–482): CC5's expression system (page read) | **NO** — own shape keys | verify the [prior] claims; apply the shapes to our job (agent) |
| 19 | Tone and exposure match | `…skin-detail-shading.md` §4: Blender 5.3 view transforms and working spaces (measured) | n/a | matching a render to a reference (agent) |
| 20 | The painting's light for our render | only the reverse job (delighting, `…ai-texturing.md` §0.3); portrait setups (snippets) | n/a | full research (agent) |
| 24 | Iris points | not covered (iris textures only) | n/a | full research (agent) |
| 25 | Measuring | `2026-10-30-research-ai-photo-to-head.md` (~51–52, §2.3): MediaPipe "fine for eyes and mouth, weak as the only shape signal"; GNM's dense detector unreleased | partly | benchmark-ranked landmark models (agent) |

The finding: the main failure was not research but execution — four researched recommendations (flow alignment, seam
levelling, the eye layer stack, expression transfer) were not built, and hand-made stand-ins took their place.

## What research is worth doing — the attack (2026-10-31)

The user: "think adversily on what you are researching and why and what we have already done". Per job: is the gap
research, and does it change the result?

- **13 eye occlusion and tearline** — research kept (how the layers are shaded and fitted; the stack itself is
  researched): the eyes are the largest CG tell left.
- **14 catch light** — dropped: the research already says the key's own reflection is the catch light; a trial tests it.
- **16 brows placement** — parked: the painted brows read as hair at portrait distance (round 43); 3D brows matter in
  profile views. Open for later.
- **17, 18 mouth and lids** — no method research: the researched rec (deformation transfer of the 52 ARKit shapes) is
  to be built; only its data is checked (MPFB2 Faceunits 01, ICT-FaceKit's shapes).
- **19 tone match** — dropped: the calibration matches the painting (measured).
- **20 the painting's light for our render** — parked: a real gap, but it serves lighting scenes later, not this test.
  Open for later.
- **24 iris points** — dropped: MediaPipe's iris points did the job (the eye colours calibrated to the painting).
- **25 measuring** — dropped: MediaPipe with RealDenseFace beside it is enough for a ruler.

The light-and-measuring agent was stopped after 19 searches; its partial notes were not written to a file.

**Order of work from here:** round 48 (the relief as geometry) → the alignment (flow on top of the coarse warp; the
coarse warp decided by the leave-one-out test) → seams (one view per region, levelled, blended) → the eye layer stack
(rec 6) → the mouth and lids by expression transfer.
