# Audit — the face test's own edits: closing the mouth (17), the lids (18), brows (16) — 2026-10-31

Rows 16–18 of [`2026-10-31-choices-audit.md`](2026-10-31-choices-audit.md) were picked without research. This file
first extracts what our earlier research already says, then verifies it, then gives one rec per job.

Course corrections from the coordinator while this ran, in order:
1. "the earlier research already covered your jobs. Do not redo it": extract first, then search only real gaps.
2. Re-verify snippet-only findings by reading the page. Treat thin coverage as a gap. 40 searches at most.
3. Plan: 17/18 are covered (deformation transfer of the ARKit 52 ranked first). Verify the [prior]/[known] claims.
   The gap is using those shapes for our job. 16 is thin.
4. **Scope cut:** job 16 (brows) dropped and parked ("our painted brows work at portrait views"). No new method
   research for 17/18. Verify only: (1) Faceunits 01 — that it exists, has the 52 shapes and is CC0; (2) ICT-FaceKit's
   expression data; (3) Blender tools for deformation or ARKit shape transfer. Searches 1–16 below ran before
   corrections 1–4 arrived. They are kept and marked.

Evidence labels: **page read** (the page itself), **API** (GitHub API: file, tree or licence), **snippet** (search
summary only), **measured** (computed here on our files; the scripts are listed under Searches), **file** (our repo).

---

## 0 · What our research already says (extracted, with file:line)

| # | Finding | Where | Its evidence there |
|---|---|---|---|
| E1 | Expressions for any head: rank 1 is deformation transfer (Sumner & Popović 2004) of the ARKit 52 from a template that has them (MPFB2 *Faceunits 01*, CC0; ICT-FaceKit, MIT). Rank 2 NFR, rank 4 example-based facial rigging (Li et al. 2010). Technique: wrap by NICP, per-triangle gradients, one sparse solve per shape, hand-masked lids and lips | `2026-10-30-research-all-functions.md:243-264` | [prior]/[known]; NFR [page] |
| E2 | The guaranteed face set is ARKit 52. **The first set is MakeHuman's CC0 "Faceunits 01"** (hm08), via MPFB2's `faceservice.py`. Better shapes replace them under the same names if the gate judges them below the bar | `docs/standards/skeleton-and-face.md:165-181`; `quality-gate.md:56-57` | approved spec |
| E3 | MPFB2's FaceService loads the 52 ARKit face units (`faceunits01` pack) as shape keys | `2026-10-29-research-05-bases.md:104`; `RESEARCH.md:429-434` | page read |
| E4 | Anny ships `data/faceunits01` under CC0 | `2026-10-29-research-05-bases.md:124` | page read |
| E5 | "Lead … contents not yet read: Faceunits 01" | `RESEARCH.md:573-574` | — |
| E6 | ICT-FaceKit: ARKit-named expressions, `_L`/`_R`, browInnerUp and cheekPuff split per side. MIT, unmaintained since 2020 | `2026-10-29-research-05-bases.md:36,76,160`; `RESEARCH.md:358` | page read |
| E7 | No open tool turns a neutral mesh into ARKit 52 automatically. TopoRig is academic-only; RigAnyFace and OmniFaceRig have no code; `digitalp/arkit-blendshape-tool` copies by nearest neighbour | `2026-10-29-research-10-character-assets.md:79-82,431-434,491-500` | page read / snippet |
| E8 | CC5 faces are bone-, morph- or hybrid-driven. Slider categories include EyeBlink, Eyelid, MouthBase, MouthSticky, Jaw. HD is 262 + 128 correctives. Mouth-open is one morph that also drives the teeth and tongue | `2026-10-29-research-02-cc5.md:445-482`; `-cc5-pass2.md:236-262` | page read |
| E9 | MetaHuman's face: about 420 GUI controls (`CTRL_L_eye_blink.ty`, `CTRL_C_mouth_stickyU.ty` …); DNA layers controls → joints / blend shapes / wrinkle maps | `RESEARCH.md:1033-1036,1108-1112` | measured (names from the user's UE 5.8 file) |
| E10 | Later step: expressions transferred from MPFB2's Faceunits or ICT-FaceKit (no model) | `2026-10-30-realism-recs.md:63-64` | — |
| E11 | Lips: sticky lips simulated (Barrielle et al. 2019); visemes | `2026-10-29-research-10-character-assets.md:413-421` | snippet |
| E12 | Maya Bifrost 3.0 has "an eye module for eyelid deformation"; MetaHuman 5.8 has procedural blinks | `2026-10-29-research-04-references.md:265,370` | page read |
| E13 | A photoreal MakeHuman example "needed … a custom eyelid target" | `2026-10-29-research-05-bases-pass2.md:88-90` | page read |
| E14 | Brows: MetaHuman brows are a groom (strands, cards or meshes per LOD). CC5 brows are card hair (HairGroup), with conform regions, plus a SkinGen brow-makeup layer. Advice "individual hairs on a painted density mask" | `2026-10-30-research-hair-eyes-teeth.md:83-87,287,440`; `-research-10-character-assets.md:557-559`; `-research-02-cc5.md:206,217`; `-cc5-pass2.md:326-333` | page read; line 287 **snippet** |
| E15 | MakeHuman brow cards on our head: grey film until the `.mhmat` rules applied; then higher and more arched than the painting's brows, doubling them | `RESEARCH.md:1814-1820`; `TASKS.md` round 43 | measured |

**Not in our research before today** (grep of `RESEARCH.md`, `docs/plans/*`, `docs/standards/*` for `EyelidUpper`,
`lip seal`, `sealed`, `AU45`, `AU43`, `neutral pose`, `mouthClose` semantics). Nothing on:
- MetaHuman's rules for the neutral;
- how its lids move;
- what `mouthClose` means;
- Faceunits 01's actual contents;
- ICT-FaceKit's file list;
- Blender transfer tools.

---

## 1 · Verification (the coordinator's three questions)

### 1.1 Faceunits 01 — it exists, it has the 52 ARKit shapes, it is CC0

- **Not in our local packs.** `.dev/cache/mh_packs/makehuman_system_assets_cc0.zip` has 517 entries: `skins`,
  `clothes`, `teeth`, `eyelashes`, `hair`, `tongue`, `packs`, `proxymeshes`, `eyebrows`, `eyes`. No face units,
  ARKit or visemes — *measured* (zipfile listing).
- **Not in MPFB2's repo.** `makehumancommunity/mpfb2` holds `docs/services/faceservice.md` and MakeHuman's older
  expression units (`src/mpfb/data/targets/expression/units/{african,asian,caucasian}/eye-left-closure`, `-slit`,
  `mouth-compression` …), but no faceunits targets. The doc says `load_targets(..., load_arkit_faceunits=False)` "Load
  the 52 ARKit face unit targets", needs the pack installed (`is_faceunits01_installed`), and loads through
  `TargetService.bulk_load_targets`. Those are MakeHuman's additive targets, so they work on any slider mix of the
  base — *API*.
- **The pack page:** "Faceunits 01 — ARKit style face units". The functional packs section says "The assets are
  shared under CC0" — *page read*
  ([assetpacks.html](https://static.makehumancommunity.org/assets/assetpacks.html)). Its own page names the
  contributor Mika Suominen, says "can be used standalone as common targets", gives 0.2 MB, and has no licence line.
  Downloads: `https://files2.makehumancommunity.org/functional/faceunits01.zip` (mirror `files.`) — *page read*
  ([faceunits01.html](https://static.makehumancommunity.org/assets/assetpacks/faceunits01.html)).
- **The zip itself** (257,821 bytes, sha256 `d113107bd7eb59f3…`, in the scratchpad, not extracted into the repo):
  - 52 `targets/faceunits/*.target` and `packs/faceunits01.json`;
  - every one of the 52 metadata entries says `"license": "CC0"`, `"author": "Mika Suominen"` and
    `"description": "Autogenerated ARKit faceunit"`;
  - its `mouthClose.target` is byte-identical to Anny's copy
    (`naver/anny/src/anny/data/faceunits01/targets/faceunits/`, 52 files);
  - Anny's README: "Face Units asset pack by Mika Suominen, licensed under the CC0 1.0 Universal License"
    — *measured* + *API*.
- **The names are exactly ARKit's 52** (browDownLeft … tongueOut, matching `skeleton-and-face.md:170-174`) — *API*.
- **Our head is hm08, so these targets apply directly: no deformation transfer is needed.** E1's rank-1 transfer is
  only for a template on another topology (ICT, FLAME).

### 1.2 ICT-FaceKit's expression data — *API* (repo, README, tree, LICENSE)

- `USC-ICT/ICT-FaceKit`: **MIT** (LICENSE: "Copyright (c) 2020 USC Institute for Creative Technologies"), last push
  2020-12-01, 773 stars.
- **57 expression OBJs** in `FaceXModel/`:
  - the ARKit names without `tongueOut`, `_L`/`_R` suffixed, with `browInnerUp` and `cheekPuff` split per side (53);
  - plus `cheekRaiser_L/R` and `PupilDilate_L/R`.
- `mouthClose.obj` is among the 57. The model also has 100 identity PCA modes (`identity000–099.obj`) and
  `generic_neutral_mesh.obj`.
- Topology: 26,719 vertices in all; face 9,409.
- Separate meshes: mouth socket, eye sockets, gums and tongue, teeth (32 teeth), eyeballs, lacrimal fluid, eye
  blend, eye occlusion, eyelash strips.
- README's FACS table: AU45 Blink → `eyeBlink_L + _R`; AU5 → `eyeWide`; AU7 Lid tightener → `eyeSquint`;
  AU24 Lip pressor → `mouthPress`; AU28 Lip suck → `mouthRollLower + mouthRollUpper`; AU27 → `jawOpen`. AU43 is not
  in the table.
- "expression shapes and naming convention are subject to change" (README, via search 8 — *snippet*).
- Another topology than hm08, so ICT needs E1's wrap + transfer. Our `libs/wrap/gnm_to_hm08.py` already runs
  trimesh's Amberg NICP — *file*.

### 1.3 Blender tools for shape-key / ARKit transfer — *API* (GitHub repo records, READMEs)

| Tool | How it works | Licence | Last push · stars | Fits us? |
|---|---|---|---|---|
| Blender **Surface Deform** modifier (built in) | binds one mesh to another surface's deformation; a shape key comes from applying it. Target must have no edges with >2 faces, no concave faces, no doubles, no faces with collinear edges; "the further a mesh deviates from the target mesh surface, the more likely … artifacts" | GPL (Blender) | manual source read (projects.blender.org; docs.blender.org returned 403) | the standard built-in way between topologies; positions, not deformation gradients |
| Blender **New from Objects** (`object.join_shapes`) | "Add the vertex positions of selected objects as new shape keys" (same vertex count) | GPL (Blender) | manual source read | same topology only |
| `MykytaPetrenko/ShapeKeyWrap` | Surface Deform under the hood; optional Corrective Smooth; binds values by name | GPL-3.0 | 2026-09-04 · 117 | maintained |
| `fblah/ShapeKeyTransferBlender` | overlap both meshes at the origin; radius of source influence | GPL-3.0 | 2025-11-16 · 196 | built for 2.93 (search 17, *snippet*) |
| `Vidyut/mesh-expression-retargeter` | landmark pairs → transfer map → native shape keys. With MPFB, can project a shape onto MPFB's 52 ARKit face units and save an MPFB expression | GPL-3.0 | 2026-10-22 · 3 | new, tiny; README read |
| `knhcr/TransferAllShapeKeysViaSurfaceDeform` | script, all keys via Surface Deform | GPL-3.0 | 2021-05-10 · 4 | old |
| `vasiliskatr/deformation_transfer_ARkit_blendshapes` | **Sumner & Popović 2004 implemented** (numpy, scipy, numba), demonstrated making ARKit shapes for ICT's face; NICP done in commercial Wrap3D | **MIT** | 2022-01-14 · 70 | the method E1 names, MIT. Our wrap can stand in for Wrap3D |
| `vasiliskatr/example_based_facial_rigging_ARkit_blendshapes` | Li et al. 2010 (EBFR); "All input data must share the same topology" | **MIT** | 2022-01-16 · 43 | for refining shapes from example poses |
| `elijah-atkins/ARKitBlendshapeHelper` | you sculpt the 52 poses on frames; it bakes them | **no licence** | 2025-08-04 · 96 | not a transfer |
| `digitalp/arkit-blendshape-tool` | GLB → GLB, nearest-neighbour KD-tree | **no licence** | 2026-04-07 · 1 | not usable (no licence) |
| Shape Key Gen (Superhive) | generates the 52 on a rigged character | paid | — (search 18, *snippet*) | reference only |

---

## 2 · Job 17 — closing the mouth (and thinning / narrowing the lips)

### 2.1 How the pros do it

| Finding | Evidence | Already in our research |
|---|---|---|
| **MetaHuman: the neutral itself is sealed.** "In the neutral pose the lips should be completely sealed, without gaps and without intersections." "Teeth should be flush with the lips with no intersections". Figure: "Closing a parted Lip Seal." | page read ([Neutral Pose](https://dev.epicgames.com/documentation/en-us/metahuman/neutral-pose)) | **no** |
| MetaHuman: "Expressions are stored and treated as differences from the Neutral Pose". Edits are made in the Expression Editor's Neutral Pose mode, on LOD0, by moving vertices in the scene or transferring them from a reference mesh | page read (same; [Neutral Pose Editing](https://dev.epicgames.com/documentation/metahuman/neutral-pose-editing?lang=en-US); search 11 *snippet*) | **no** |
| MetaHuman's neutral for likeness scans: "Relaxed face with the teeth touching, but not clenched" | page read ([Expressions for Likeness Calibration](https://dev.epicgames.com/documentation/en-us/metahuman/expressions-for-likeness-calibration)) | **no** |
| MetaHuman's lip controls are performance controls. `mouthLipsTogether*` "can not be used independently — but only with jaw open". `mouthLipsPress` "Presses … lips together without pushing up the chin boss". `mouthSticky*` simulate sticking "in combination with some amount of 'jaw open' (max 25%)" | mouthStickyUC page read; the rest search 10 *snippet* | partly (names, E9) |
| **ARKit `mouthClose` is jaw-relative:** "closing of the lips without relation to the position of the jaw … some values … can produce unrealistic facial expressions unless other coefficients are also set". Apple's figure pairs it with `jawOpen` = 1 | page read ([Apple](https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation/mouthclose)) | **no** (name only) |
| CC5: lip and lid shape through Facial Profile morph sliders (EyeBlink, Eyelid, MouthBase …); identity through head morph sliders; the neutral is reset with Load Neutral Base | page read (E8); slider names search 14 *snippet* | yes (E8) |
| GNM keeps its zero expression neutral on purpose. A mean-expression template "would result in a face with slightly closed eyes and a slightly opened mouth". Its fit solves identity, expression (per region: left eye, right eye, lower face), pose and camera together against ~600 dense landmarks, with priors and a self-intersection penalty | page read ([arXiv 2607.23687](https://arxiv.org/html/2607.23687v1), first 100k of 130k characters) | partly (`RESEARCH.md:1589`, solve only) |
| Expression transfer methods (deformation transfer, EBFR, NFR, Disney's Neural Facial Deformation Transfer EG 2025). An EG 2018 study: EBFR better overall, "certain lip poses were not improved" | search 3–4 *snippet* | yes (E1), except Disney NFDT and the 2018 study |

### 2.2 Measured here — what the CC0 shapes do on hm08 (`base.obj`, mm, weight 1)

- **Faceunits `mouthClose` is not a closing shape on a closed jaw.** It lowers the upper lip 2–7 mm and raises the
  lower lip and chin ~27 mm. The seam gap changes −34 mm at the middle, against `jawOpen` +34 mm. It undoes jawOpen,
  as Apple's definition says. Closing our 0.9 mm slit with it (w ≈ 0.026) would also lift the chin ~0.7 mm.
- Faceunits `mouthPressLeft`: −1.3 mm at the seam's middle, −0.7 at 6 mm out. `mouthRollUpper` / `mouthRollLower`:
  −2.8 / −3.2 mm. These are AU24 (lip pressor) and AU28 (lip suck) per ICT's table: tension, not a relaxed neutral.
- **MakeHuman's identity mouth targets keep the seam where it is:**

  | Target | Seam change (mm) | Effect |
  |---|---|---|
  | `mouth-scale-vert-decr` | −0.1 / −0.3 | thins |
  | `mouth-upperlip-height-decr` | −0.3 / −0.6 | thins |
  | `mouth-lowerlip-height-decr` | +0.6 / +0.5 | thins |
  | `mouth-scale-horiz-decr` | 0.0 | narrows by 2.9 mm on average, up to 6.2 mm |

  They are artist-sculpted CC0 identity sliders that thin and narrow the lips without touching the seal. All
  44 mouth targets are already in our repo (`extension/juststage/data/fetched/makehuman/targets/mouth/`, from
  MPFB2 6ff1eb35) — *file*.
- hm08's base seam: 0.24 mm at the middle, 0.53 mm at 6 mm out. Our GNM-shaped head: ~0.9 mm (`face_shape.py`'s
  measurement), so the slit comes with the identity.

### 2.3 What we do now, compared

`face_shape.close_mouth` is one hand-made shape key:
- Gaussian falloffs move the upper lip down and the lower lip up (gap 1.6 mm + 0.4 mm overlap at the middle);
- in the same key, the lips get 21% thinner and the mouth 6% narrower;
- tuned by MediaPipe against the painting. Seam 0.003 vs the painting's 0.004; upper lip 0.086 vs 0.080; lower
  0.128 vs 0.122 (`TASKS.md` rounds 44–45).

Against the pros:
- **Sealing as a neutral fix, not an expression: right** (MetaHuman's rule).
- **Mixing identity into the same key: wrong.** Thinning and narrowing are identity (CC5 and MakeHuman sliders,
  MetaHuman neutral editing), and we already have the CC0 sliders for them.
- It lives in the face test, so the app's own heads keep the slit.

Status: NOT STANDARD (our own falloffs).

### 2.4 Rec 17

**Split the edit along MetaHuman's line:**
- **Lip thickness and mouth width** become values of MakeHuman's CC0 identity sliders already in our repo
  (`mouth-upperlip-height`, `mouth-lowerlip-height`, `mouth-scale-horiz`, `mouth-scale-vert`). The values are solved
  by linear least squares against the painting's outer-lip MediaPipe points: the standard landmark fit of a linear
  basis, as in GNM's report §4.2.
- **The seal** stays a neutral-pose step that only closes the seam (and opens any overlap). It moves from the face
  test into the head module, with a "lips sealed, no intersections" check from MetaHuman's neutral rule.
- No Faceunits shape and no transfer for this job.

*Attack.*
- (a) Does it break a decision? `skeleton-and-face.md` §2.1 makes Faceunits the expression set. Untouched: the
  neutral is not an expression ("differences from the Neutral Pose").
- (b) Simpler standard option, `mouthClose` at a small value? Measured: jaw-relative; it lifts the chin with the lip.
  Apple warns about it. Rejected.
- (c) `mouthPress` / roll? AU24/AU28 are tense, and MetaHuman's neutral is "relaxed". Rejected.
- (d) Deformation transfer (E1's rank 1)? Not needed: same topology (§1.1).
- (e) Cost: the targets are in the repo; the solve is ~30 lines beside `flame_fit.py`.
- (f) Could the sliders' sculpts match the painting worse than the tuned Gaussian? Possibly. Measure on the same
  MediaPipe numbers (upper, lower, width, seam) first. Keep the old key if the sliders lose, and write down why.
- (g) Edge: identities whose lips intersect at rest. The seal step must also open overlaps ("without
  intersections").
- (h) The seal step is still our code: **NOT STANDARD**. The standard is MetaHuman's Neutral Pose editing, a manual
  Unreal tool. No automated open seal tool was searched for (scope cut), so that is a search gap, not "none exists".

What the attack changed: dropped `mouthClose` and transfer (measured), and added the overlap case.

---

## 3 · Job 18 — bringing the lids to the iris

### 3.1 How the pros do it

| Finding | Evidence | Already in our research |
|---|---|---|
| **MetaHuman turns eyelid joints about the eye.** "start by rotating `FACIAL_[L|R]_EyelidUpperA` joints (through the blink controls on the rig)"; check "whether the eyelids are being flattened (not preserving a sectional contour of the eyeball)"; "keep an eye on the volume of the eyelid" | page read ([Skin Weights](https://dev.epicgames.com/documentation/en-us/metahuman/skin-weights)) | **no** |
| MetaHuman `eyeBlinkL`: "Left side of FACS AU45 'blink' … can be used for FACS AU43 'eye closure' also". `eyeWiden` is AU5. `eyeLidPress` and `eyeUpperLidUp` are tweakers on top | eyeBlinkL page read; the rest search 9 *snippet* | partly (names, E9) |
| MetaHuman's neutral: "The eyelid shell and folds shouldn't intersect, nor be too thin"; "shouldn't intersect with the other EyeMeshes at all". Mesh to MetaHuman input "must have open eyes and visible separation between the eye and eyelid" | page read (Neutral Pose; [From Mesh](https://dev.epicgames.com/documentation/en-us/metahuman/from-mesh)) | **no** |
| ICT / ARKit / Faceunits: the lid is a linear `eyeBlink` (AU45), `eyeSquint` (AU7), `eyeWide` (AU5) | API (ICT README) | yes (E6), not the AU table |
| Riggers: linear shape-key blinks cut through the eyeball mid-blink, so lids are rotated about the eye's centre, with shape keys as correctives | search 12 *snippet* (forum threads) | **no** — supported by the measurement below |
| CC5: Eye_Blink, Eyelid sliders; CC3's "Fix Blink" snaps the upper lid onto the lower | search 14 *snippet* | partly (E8 categories) |
| GNM places eyeballs by hand for "higher fidelity of the eyeball-eyelid contact" and adjusts its identity basis to keep contact; its eye-region expressions are statistical (100 per eye) | page read (GNM report §3.5–3.6) + measured (`gnm_head.npz` names) | partly (`RESEARCH.md:392,463` counts only) |

### 3.2 Measured here

- **Faceunits `eyeBlinkLeft` on hm08**, measured against a sphere fitted to `helper-l-eye` (radius 13.8 mm; crude,
  because the cornea bulges). The 144 upper-lid vertices that move more than 2 mm sit deepest at:

  | Weight | Deepest point (mm, against the sphere) |
  |---|---|
  | 0 | −0.87 |
  | 0.2 | −1.54 |
  | 0.5 | −1.95 |
  | 1 | −1.33 |

  The linear path sinks the lid a further ~0.7 mm into the eye at the partial value our job needs, and ~1.1 mm at
  half blink. This is the flattening MetaHuman's skin-weights page warns about.
- **MakeHuman's identity eye targets are too small for this.** `l-eye-height1-decr` moves the upper lid 0.75 mm on
  average (1.93 at most); `height2/3-decr` raise the lower lid 1.0–1.3 mm. Our upper lid needs ~2.9 mm at its edge
  (14° on a ~12 mm eye), beyond the sliders' range.

### 3.3 What we do now, compared

`face_shape.lower_lids` rotates the lid skin about each eyeball's left-right axis: upper 14° and lower 5° at the
edge, fading over 35°, found per 10° slice. Opening/width 0.340 vs the painting's 0.339. That is MetaHuman's principle
(lids turned about the eye, keeping its contour), done as a shape key in NumPy instead of joints and skin weights.
It is closer to the pro rig than a partial linear `eyeBlink` would be (§3.2).

Status: NOT STANDARD as code, standard as method.

### 3.4 Rec 18

**Keep the rotation about each eyeball.** It is the rig's way: MetaHuman turns its upper-lid joints so the lid keeps
the eyeball's contour. Move it from the face test into the head module as the neutral's lid step, with a
no-intersection check (MetaHuman's neutral rule). Retire it when the DNA rig's eyelid joints exist; until then it is
the only lid mechanism. Do not use Faceunits' `eyeBlink` at a partial value.

*Attack.*
- (a) Simpler standard option, `eyeBlink` ≈ 0.2? Measured: it sinks ~0.7 mm into the eye. Rejected for the neutral;
  it stays the blink expression on the rig.
- (b) Identity eye-height sliders? Too small a range (measured). Rejected.
- (c) GNM's eye-region expression fit, carried through our wrap? It is the model's own statistical way. But the
  wrap's error (mean 0.87 mm, p95 2.17 mm, `RESEARCH.md:465`) is larger than the sub-millimetre lid contact. GNM
  itself places eyeballs by hand for that contact. Later, not now.
- (d) One way per job: once the rig exists, a second lid mechanism would be a bug. Hence "retire".
- (e) NOT STANDARD as code; the standard (joints and skin weights) needs the rig we don't have yet.
- (f) Is the stare identity or expression? MetaHuman's neutral is "relaxed", so the relaxed lid belongs to the
  neutral, which is where the rec puts it.

What the attack changed: rejected `eyeBlink` and the eye-height sliders (both measured), and added the retire rule.

---

## 4 · Job 16 — brows (parked by the coordinator's scope cut)

Not researched. What exists:
- E14: one snippet-level line, `hair-eyes-teeth.md:287` — "individual hairs on a painted density mask, flowing
  along the brow" — not re-verified;
- E15: the measured card trials.

One page read on the way (§1.1): MakeHuman's packs page lists **"Eyebrows 01 — A set of high-res eyebrows by
Mindfront"** under "Mesh assets shared under CC0". It is not in our local `makehuman_system_assets_cc0.zip`, which has
the older `eyebrow001–012` cards. A lead for when brows are reopened.

Open gaps, logged for that day:
- placing brows from a photo;
- cards vs strands at portrait distance;
- MetaHuman's and CC5's brow fitting.

---

## 5 · Facts for `RESEARCH.md` (pending: this agent may edit only this file)

§1.1–§1.3, §2.1 rows marked "no", §2.2, §3.1 rows marked "no", §3.2, and the Eyebrows 01 lead.

---

## 6 · Searches — every query and read, in order

WebSearch (18 in all; 1–16 ran before the coordinator's corrections, so some repeat covered ground, marked *covered*):

| # | Query (domains) | Why | Returned |
|---|---|---|---|
| 1 | how to close the mouth on a neutral 3D head blendshape lips closed | job 17, plain | Unity Live Capture and ARKit enums, Apple `mouthClose`, Android XR, Meta Movement SDK (LIPS_TOWARD), Animaze manual, a Google patent |
| 2 | ARKit mouthClose vs jawOpen blendshape how lips close | job 17, X vs Y | Unity ARKit enums, Apple `mouthClose`, a Reallusion forum thread on jawOpen + mouthClose, a Reallusion feedback-tracker jaw issue |
| 3 | deformation transfer vs example-based facial rigging blendshapes for a new head | job 17, X vs Y (*covered*: all-functions:250-253) | OmniFaceRig arXiv 2606.08043, Disney Neural Facial Deformation Transfer (EG 2025), EG 2018 EBFR study, TU Dortmund VRST 2022 supplement, a SIGGRAPH Asia example-based sculpting entry |
| 4 | alternatives to deformation transfer for facial expression blendshapes 2025 2026 | job 17, alternatives (*covered* in part) | Disney NFDT, landmark-guided DT (ICCVW 2019), online-modelling patents; nothing from 2026 |
| 5 | OmniFaceRig inner-mouth-aware face rigging code (github, arxiv, hf) | named candidate (*covered*: character-assets:431) | arXiv pages, the project-page repo and fork, TopoRig arXiv 2609.15746; no code |
| 6 | MetaHuman neutral pose lips closed mouth sticky lips control (dev.epicgames.com, forums) | job 17, vendor docs | MetaHuman standards pages `mouthSticky*` (10 pages) |
| 7 | fit blendshape expression weights to face landmarks from a photo closed mouth 3DMM expression fitting | job 17, method | Salazar et al. arXiv 1202.1444, a Surrey thesis (linear fit to 2D landmarks), a caricature-expression paper |
| 8 | ICT-FaceKit expression blendshapes ARKit (github) | named candidate | USC-ICT repo and its Blender script, QtMeshEditor issue #889, `vasiliskatr` EBFR repo, aniface-demo, makehuman.js, BlendCap, HACK-Model |
| 9 | MetaHuman standards eyeBlink upper eyelid curve lids follow eyes (dev.epicgames.com) | job 18, vendor docs | `eyeBlinkL/R`, `eyeLidPressL/R`, `eyeWidenL/R`, `eyeUpperLidUpL`, `eyeFaceScrunchL/R`, the Skin Weights page |
| 10 | MetaHuman lips together mouthLipsTogether control lip press neutral (dev.epicgames.com) | job 17, vendor docs | `mouthLipsTogether{UL,DL,UR}`, `mouthLipsPressL/R`, `mouthPress{DL,UL,UR}`, the MHA curve index, Expressions for Likeness Calibration |
| 11 | MetaHuman neutral pose conform template mouth closed eyelids custom character Expression Editor (dev.epicgames.com) | job 17/18, vendor docs | Neutral Pose, Neutral Pose Editing, initial head DNA, From Mesh, Workflow/UX overviews, From Video, DNA rig definition, From Template Mesh |
| 12 | eyelid rig rotate around eyeball center blink shape key vs bones lid slides over eye | job 18, X vs Y | Blender Artists threads (bone blink, oversized eye, eyelid rotation ruins shape, pivot), Renderosity threads |
| 13 | FACS AU43 AU45 AU7 eyelid blendshapes upper lid lower lid relaxed eye rig | job 18, plain | garagefarm blog, ICCV 2025 AU-Blendshape supplement, rmpy facial-rig docs, Gnomon FACS photogrammetry article (4 mirrors) |
| 14 | Character Creator morph sliders eyelid upper lid height lip thickness mouth close neutral (manual.reallusion.com) | job 17/18, vendor docs | CC5 Slider Table for Facial Profiles, CC4 Adjusting Facial Features, Setting Lips Shape Data, ExPlus blend shapes, wrinkles, CC3 Fixing Blinking Issues, Muscles Movement Data, Refining Expressions, external-character morphs |
| 15 | Headshot photo to head lips closed eyes open expression neutral Character Creator (manual.reallusion.com) | job 17, vendor docs | Headshot 1/2 pages (body types, Morph 1000+, mesh-mode guides and requirements), Face Template, Adjusting Facial Features, Base Mesh Projection, Edit Facial UI, nasolabial folds |
| 16 | Google GNM head model expression basis eye region lower face fitting landmarks (github, arxiv, research.google) | job 17/18, our own model | GNM report arXiv 2607.23687, a MediaPipe→GNM correspondence gist, FaceFrame (iOS), gnm-maya, VRFaceTracking PR, threejs-talking-avatar, cape-jones PR |
| 17 | Blender add-on deformation transfer shape keys between different topology meshes (github) | verification 3 | ShapeKeyTransferBlender, ShapeKeyWrap (+ README, releases), mesh-expression-retargeter, shapekey_inference, TransferAllShapeKeysViaSurfaceDeform, Duplicate-and-mirror, BlenderRoundTrip, BlenderShapeKeyTools |
| 18 | transfer ARKit 52 blendshapes from one head to another head Blender free addon | verification 3 | ARKitBlendshapeHelper, BlenderNation listings, a Blender Artists thread, a Gumroad item, Shape Key Gen (paid), digitalp/arkit-blendshape-tool |

Pages read (WebFetch):
- MetaHuman `mouthStickyUC`;
- Expressions for Likeness Calibration;
- `eyeBlinkL`;
- Skin Weights;
- Neutral Pose (twice, verbatim quotes);
- From Mesh;
- Neutral Pose Editing (no lip or eyelid text);
- GNM report HTML (first 100k of 130k characters);
- MakeHuman `assetpacks.html` and `faceunits01.html`;
- Apple `mouthClose` (.md);
- docs.blender.org shape-keys panel and Surface Deform: **403**. Both read from the manual's source on
  projects.blender.org (`shape_keys_panel.rst`, `surface_deform.rst`) by curl.

GitHub API:
- `google/GNM`: repo, README, `gnm/shape/README.md`, `semantic_sampler.py` (20 expression labels: SURPRISE … WINK_LEFT,
  LIPS_ROLL_IN …);
- `naver/anny`: tree, README;
- `makehumancommunity/mpfb2`: tree, `docs/services/faceservice.md`;
- `USC-ICT/ICT-FaceKit`: repo, README, tree, LICENSE;
- records of the 9 tool repos in §1.3, and READMEs of `mesh-expression-retargeter`, `ShapeKeyWrap` and both
  `vasiliskatr` repos.

Downloads (data only, in the scratchpad, never run):
- 7 Faceunits targets from Anny's raw files;
- `faceunits01.zip`;
- two Blender manual `.rst` files.

Measurements (Python, `-I`, on our files; scripts in
`F:\ClaudeCode\tmp\claude\E--Dev-3D\4dbbd99d-b204-4ed4-aa13-96f0c5684206\scratchpad\`):
- `gnm_keys.py` and `gnm_expr.py`: the arrays and the 383 expression and 46 group names of `.dev/cache/gnm/v3_0/gnm_head.npz`
  — `left_eye_region_000–099`, `right_eye_region_000–099`, `lower_face_region_000–149`, `tongue_mean`, `tongue_000–030`,
  `pupils_000`;
- `gnm_lips.py`: GNM template midline upper/lower lip vertex distance 0.52 mm (rough: by vertex groups);
- `targets_measure.py`, `lips_mid.py` and `seam.py`: Faceunits and MakeHuman targets on `base.obj` (§2.2);
- `blink.py`: `eyeBlinkLeft` clearance (§3.2).
