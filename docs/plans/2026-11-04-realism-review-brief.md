# Character realism and variety — the full plan, for an independent review (2026-11-04)

> **For the reviewer (Fable):** this is JustStage's plan to make every body part of its characters as real and as
> varied as MetaHuman's and Character Creator 5's, in the real-time view and the film render. Please look for
> **better solutions**: a better method, a better source, a simpler path, a wrong assumption, a missing part, a
> wrong order. Say where you'd do it differently and why, with evidence (a paper, a doc page, a dataset, a
> measurement). §9 lists where the author is least sure. Everything here is verifiable in the repo
> (`E:\Dev\3D\just-stage`); file pointers are given throughout.

## 1 · The app and the bar

JustStage is an open-source (GPL-3.0-or-later extension, MIT libraries) character app built on Blender 5.3 as an
application template plus an extension: CC5's features (character creation, skin, hair, morphs, export) inside
Blender. The user's bar, verbatim (`docs/dev/TASKS.md`, "THE BAR"): *"i told you not to stop until all quality in
eevee mode is as good as metahuman and cc5, that is rule"*; *"if cc5 and metahuman can bee full realism in regular
mode than you should be able to do it to"*; on variety: *"Not accetable, you need to fix quality and we need to do
realistic variety"*; *"we need high quality for every body part"*. The nine parts, as confirmed by the user:

1. Skin: face, body, hands and feet, by ethnicity and age (wrinkles, freckles, moles, age spots, stubble shadow).
2. Hair: scalp styles, lengths, textures (straight to coily) and colours, including grey.
3. Facial hair: beards, moustaches, stubble.
4. Brows and lashes: shapes, density and colour.
5. Body hair.
6. Eyes: iris colour and pattern, sclera (veins, redness, yellowing with age), eye wetness, lid shapes.
7. Mouth: teeth (shape, colour, wear, gaps, alignment), gums and tongue.
8. Nails: finger and toe nails (shape, colour, cuticles).
9. Nipples, lips and ears: their colour and detail.

"Live view" = Blender's EEVEE (Material Preview), what the user works in. "Film" = Cycles (F12). The bar is the live
view, not only the film: CC5 and Unreal (MetaHuman) are real-time too.

## 2 · Constraints

- **Hardware:** one 8 GB NVIDIA card (OptiX), shared with other sessions by message; 32 GB RAM; Windows 11.
- **Software:** Blender 5.3 beta (`E:\blender-5.3.0-beta`); Python in Blender 3.13; numpy, OpenImageIO bundled.
- **Clean-room:** CC5, iClone, Unreal/MetaHuman studied for behaviour and public docs only; never their code or
  content. Published papers and course notes are fine (written in our own code).
- **Licences:** shipped assets must be CC0 / CC-BY / CC-BY-SA / MIT / Apache-like; non-commercial or "personal use"
  material can't ship. A licence is a label on research options, not a filter.
- **Training:** no full-model training (no GPU for it); small LoRAs on an open base that fit 8 GB are allowed; tiny
  special-purpose models are allowed.
- **Standards first:** Blender's own feature or a widely used standard before our own; our own pieces are marked NOT
  STANDARD (the user accepts researched NOT STANDARD pieces).

## 3 · What exists today (built, measured)

**The base:** MakeHuman's hm08 mesh (CC0, ~13k body vertices), MakeHuman macro and detail targets as shape keys,
GNM's scan-based head-shape space (Apache-2.0, 170 identity directions on hm08), SubD 1 shown / 2 rendered by
default (Multires). Eyes, teeth, gums, tongue are GNM's part meshes fitted by MakeHuman's MHCLO.

**Skin (`extension/juststage/modules/skin/`):**
- A chromophore skin model (`core/skin_optics.py`: Donner & Jensen's layers, calibrated on NIST's 100 measured skins;
  melanin, eumelanin share, blood, oiliness) gives tone and the subsurface radii; Principled BSDF with Random Walk
  (Skin) subsurface.
- Mapped skins (`maps.py`, d6711ab): one UDIM layout for every character (`tools/make_udim.py`: 1001 head and neck,
  1002 torso, 1003 arms and hands, 1004 legs and feet, 1005 nails); base colour, tangent normal, roughness, cavity,
  height; recoloured to the character's tone by a per-channel gain (tone colour over the skin's own); a tiled pore
  patch (Lee Perry-Smith scan, CC-BY 3.0) everywhere; the body tiles carry MPFB2's CC0 region masks (areolae, nails,
  genitals) coloured by the tone model, and a ±7% 3D-noise mottle; the clear coat on the face only.
- Where the head maps come from: the "face test" (`tools/face_test/`): 11 CC-BY scans wrapped onto our head
  (RealDenseFace landmark pairs + trimesh's Amberg non-rigid ICP), baked into our layout (Blender's Selected-to-Active
  bake), skin masked by SegFace, split into broad/mid/fine layers and mixed per character (fine layer from one scan,
  mid from 2-3); the face itself painted by an image model (FLUX 3 Image Klein / FLUX.2 klein 4B, local) on the
  character's own clay renders from three views and projected. Four people made so far (Daniel, Amara, Walter, Mei),
  baked into skins (`tools/build_skins.py`); the library's ten characters wear them.
- Known gap: **variety** — a new slider-made character gets Mei's (women) or Daniel's (men) painted face recoloured
  to its tone, so a 70-year-old or a Black character wears a young East Asian face's detail. Body skin below the neck
  is plain colour + mottle + regions (no scanned body).

**Eyes (`modules/head/eyes.py`, `eye_layers.py`):** MPFB2's procedural eye ("EnhancedEye", CC0 node data: iris
fibres, collarette, limbal ring) on GNM's eyeball with UVs re-laid by 3D radius; colour presets (brown measured,
others set by eye, low chroma); ICT-FaceKit's eye occlusion and tearline strips (MIT) moved onto our eye by angle; an
EEVEE-only clear cornea layer (screen-space refraction blotched the iris); the lids kept 0.3 mm in front of the eyeball
by a shape key (`parts.eye_clearance`); jittered 0.1 mm shadows for the lid's shadow on the white.

**Hair (`modules/hair/`):** MakeHuman's CC0 hair-editor pack (13 scalp styles, 2 brows, beards/moustaches, as
Blender hair curves with its node groups), JustStage's own procedural lashes (120 upper / 75 lower, clumped, 12 points),
attached by Blender's Deform Curves on Surface. Cycles: Principled Hair BSDF (Chiang) by per-strand melanin/redness.
EEVEE: a Principled BSDF stand-in — its colour now **fitted to Cycles' look** (358fa72): Chiang's colour formula
exp(-f(β)√σ) is the colour after multiple scattering, near-black as a surface colour, so it read grey; the stand-in
uses exp(-0.637 f(β) √σ) with a floor, fitted over a melanin × redness grid (EEVEE's response linear, slope 1.62);
under the stage light EEVEE now matches Cycles' mean (0.154 / 0.091 / 0.055 vs 0.15 / 0.087 / 0.056); **under an
image light alone it is still 1.4-2.3× darker** (RESEARCH §1 has the step-by-step diagnosis).

**Stage and look:** a key and a rim area light, Poly Haven's CC0 "Studio Small 09" HDRI as the fill at 0.25, a dark
blue-grey backdrop for camera rays, AgX "Medium High Contrast" at -0.3 EV.

**Measured EEVEE facts relevant to the plan:** Blender 5.3 has per-light shading nodes (`ShaderNodeLightAccumulation`,
`LightEvaluation` → Direction, Distance, Factor, Mask; `LightInfo` → Color, Power, Position; `ShadowRaycast`); the
Geometry node's Tangent is the strand tangent on curves. Verified today: Light Accumulation shades hair curves, and
a diffuse term built from `Factor × Mask × Shadow × Color × Power` matches EEVEE's own diffuse on a sphere (0.2027 vs
0.2028).

Tests: 108 Blender tests + 39 unit/install green (`python tools/dev.py test -k "not juststage_ai"`).

## 4 · Assets on hand

| What | Licence | Use |
|---|---|---|
| HSRD-100 (Digital Reality Lab, Hugging Face): 10 people × 10 poses, 112-camera rig, raw 16K scans; **13 poses downloaded** to `.dev/downloads/hsrd100/` (Black men 24 and 64, Black woman 22, Hispanic man 62 and woman 23, Asian man 25 and woman 21, white man 50, white women 60 and 41) | CC BY 4.0 (the cleaned LODs are paid placeholders; the raw scans are real) | head and body skin bases; seen at 1:1: real pores, follicles, even light |
| 11 CC-BY head scans (Sketchfab; mostly white, one elderly South Asian woman, two dark-skinned full bodies, one olive full body) | CC BY | the current skin base |
| Lee Perry-Smith head scan (4K displacement) | CC BY 3.0 | the pore tile |
| MakeHuman hm08 + targets + MPFB2 data (masks, procedural eye, node trees, rigs) | CC0 | the base |
| GNM head model (identity, expressions, 80 unused teeth directions, eyes) | Apache-2.0 | head shapes, parts |
| ICT-FaceKit neutral mesh (occlusion, tearline strips) | MIT | eye layers |
| MakeHuman hair-editor pack (hair.blend; fur.blend inside, not yet extracted) | CC0 | hair, body hair |
| FLUX.2 klein 4B (GGUF, local via stable-diffusion.cpp), FLUX 3 Image Klein | Apache-2.0 / FLUX Kommunity | the face painter |
| SegFace, RealDenseFace, MediaPipe, Sapiens2 (cached) | various (labels) | masks, landmarks, keypoints |
| OpenRigLogic (built today: DNA + RigLogic Python bindings for Blender's Python) | MIT | the face rig (later) |

From the Hugging Face + Zenodo deep search (`2026-11-04-research-hf-assets.md`, samples in `.dev/downloads/hf_samples/`):

| What | Licence | Use |
|---|---|---|
| HUTUBS: 58 real head meshes (TU Berlin; ~200k vertices each, metric, no texture, clean ears, bald-capped, faces smoothed) | CC BY 4.0 | ear shape variety (new rec 15) |
| Poseidon3D: 400 real intraoral scans (200 people; maxilla and mandible, crowns and gums, ~83k v); ProsthoObjects3D ~650 full arches | CC BY 4.0 | teeth and gum shape variety (rec 13) |
| MIO intraoral photos (healthy, gingivitis, periodontitis; 3932 x 1865) | CC BY 4.0 | teeth and gum shading reference (rec 13) |
| Paint3D UVPos ControlNet (SD1.5, paints in UV layout, fits 8 GB); TexDreamer (SMPL-UV text/image-to-texture) | Apache-2.0; CC BY 4.0 | alternatives to the face painter (rec 4) |
| yoso-delight-v0-4 (a delighting model) | Apache-2.0 | candidate for removing light left in scans (rec 3) |
| HairDeck (image -> stylised hair cards with UVs) | Apache-2.0 | its card method only (rec 11); not realistic |

Confirmed gaps (searched on Hugging Face and Zenodo, nothing shippable): eye / iris imagery, realistic hair strands,
UV skin textures, nails, lips, facial and body hair, children's 3D data.

Candidates found, not yet fetched: Sketchfab CC-BY scans (Renderpeople "Mei Posed 001" East Asian woman 8K; 3D
Selfie Scans "Malcolm", "Bryan", "Shelley", "Matt Chua", "Pete", "Ben"; "Hector Navarro Bust" older Latino man; more —
`2026-11-02-research-texture-source.md` §5); MakeHuman CC0 packs `eyebrows01`, `bodyparts04` (nails), `bodyparts05`
(beards), `eyelashes01`; Curly-Cue's code (MIT part, coily hair), Curvature Space Editing code (MIT); Edwards et al.
2016 iris-feature data (Dryad). A Hugging Face + Zenodo deep search is running now.

## 5 · Research already done (read before proposing; please don't repeat)

`docs/dev/RESEARCH.md` §1 (today's facts: EEVEE 5.3 light nodes, the hair diagnosis, skin-variety methods,
SkinGen's inventory, HSRD-100, iris colour searches), and the plan files `docs/plans/2026-10-30-research-*.md` (AI
texturing, photo-to-head, ComfyUI/FLAME, hair-eyes-teeth, skin detail shading, image models),
`2026-11-02-research-texture-source.md` (scan sources and licences), `2026-11-02-scan-skin-base.md` (the scan route),
`2026-11-04-realism.md` (this job's working doc), `2026-11-04-research-hf-assets.md` (the Hugging Face + Zenodo deep
search, its full query log). Texturing.XYZ (CC5's MicroSkin source) was considered: its licence
couldn't be read; comparable vendors forbid raw redistribution and AI training, so buying is not the rec.

## 6 · The plan: 15 recs (14, plus ears from the Hugging Face search; recs 3, 4, 11, 13 updated by it)

Each rec: what, method, why this method, alternatives weighed, the attack and what it changed, the gate (how we'll
know it worked). Standard / NOT STANDARD marked.

### 1 · Live-view hair shading (part 2) — first, half built
- **What:** a real hair model in EEVEE so strands get hair's highlights (the white R highlight shifted toward the
  root, the coloured TRT secondary, the TT glow from behind) and its soft multiple-scattering body.
- **Method:** one swappable node group on the hair material's EEVEE output: Light Accumulation over the scene's lamps;
  L from Light Evaluation, V from the Geometry node's Incoming, T from Geometry Tangent; Marschner's longitudinal
  Gaussians (shift α, width β per lobe) and the azimuthal terms in Karis' published real-time forms (SIGGRAPH 2016
  course: N_R = ¼cos(φ/2)·F; TT and TRT as Gaussians in cos φ with absorption from the base colour); multiple
  scattering as Karis' wrapped Lambert tinted by the base colour, or dual scattering's density fallback (Frostbite
  2019); the world's light as its own term (Light Accumulation covers lamps only); the fitted base colour (done).
- **Why:** the measured gap is the shading model (Cycles rendering our stand-in is as dark as EEVEE); this is the
  model Unreal's real-time hair is built on; 5.3's nodes make it possible.
- **Alternatives:** Blender's own EEVEE hair closure (a WIP pull request, one Kajiya-Kay lobe, "not expected to land in
  its current state") — the standard, not available; Principled with anisotropy along T — no TT/TRT, no scattering;
  hair cards with baked textures — the real-time standard for dense hair, added for dense styles (rec 11).
- **Attack:** the world term double-counts if Principled's diffuse stays in → the model replaces Principled, the world
  term tuned against Cycles under the stage and an image light alone; per-light cost per pixel → measured on a full
  groom; NOT STANDARD (replaced by Blender's closure if it lands).
- **Gate:** visible-hair mean and median within ~10% of Cycles under both lights; highlights where Cycles puts them;
  frame time measured.

### 2 · Head skin bases from HSRD-100 (part 1)
- **What:** ten more people (diverse ethnicity, age 21-64) in the scan-skin mix → 21 scans.
- **Method:** the proven scan route (`tools/face_test/scan_*.py`): Blender import, flat renders, RealDenseFace pairs,
  procrustes + Amberg NICP, Selected-to-Active bake, SegFace skin mask, layer split.
- **Alternatives:** Sketchfab CC-BY heads (more people, mostly phone scans with baked light) — later, where HSRD
  leaves gaps.
- **Attack:** two people wear a hat or hairband in every pose (face and neck only); RealDenseFace needs the card;
  full-body scans have the face small in the atlas (~1,000 px across at 16K — similar texel density to our other
  scans).
- **Gate:** each base seen at 1:1 on our head; no seams; coverage reported.

### 3 · Tone-true variety (part 1) — changed by the second attack
- **What:** a character's skin reads like real skin of its tone (freckles, redness, mottling, sheen).
- **Method:** first pick base scans near the target's tone, ethnicity, sex and age (21 to choose from); then cover
  the remaining tone difference with chromophore maps — each layer inverted per texel to melanin and blood by our own
  skin model (Donner et al. 2008; Aliaga, Hery & Xia 2022), shifted to the target, a residual kept.
- **Why changed:** recolouring a light scan to make a dark-skinned person is weaker — real dark skin differs in sheen
  and pore look too; HSRD-100 gives real scans of those tones.
- **Attack:** light left in a scan reads as pigment (the low band is already dropped); our model is extrapolated past
  NIST's darkest measured skin. Candidate from the HF search: a delighting model (yoso-delight-v0-4, Apache-2.0) run on
  the scans before the inversion - untested.
- **Gate:** a Black, an East Asian, a Hispanic and a white character of two ages each, side by side, read as their
  tone with real-looking detail.

### 4 · Any described person: the face generator in the app (part 1)
- **What:** describe a person (sex, age, ethnicity, features) and get a new face, as CC5 Headshot's AI generator or
  MetaHuman's presets give variety.
- **Method:** the face test's painter as a command: the character's clay renders from three views, FLUX paints the face
  (the hero view first, the others edited from the projected hero), projected and merged over the base chosen in rec 3,
  baked to a mapped skin.
- **Alternatives:** WildCap (CVPR 2026, GPL code; weights' training-data licence unstated, nvdiffrast non-commercial,
  Linux) — a light-stage diffusion prior in its own UV; AvatarTex-style UV LoRA (3DV 2026, no code); DoRA
  (non-commercial). From the HF search: Paint3D's UV-position ControlNet (Apache-2.0, SD1.5, paints directly in a UV
  layout, fits 8 GB) and TexDreamer (CC BY 4.0, SMPL UV). Our route is measured and works; these may beat it on
  reflectance separation or speed - a side-by-side test before choosing.
- **Attack:** ~7 min of card a person; view drift (solved in the face test by three views over a base); the painter's
  licence is a label.
- **Gate:** ten described people, all distinct, none uncanny, in both engines.

### 5 · Age as a slider on any skin (part 1)
- **Method:** age shape from MakeHuman's age macro; age detail by matching the fine layer's per-region multiscale
  statistics to an age group's (Golovinskiy et al. SIGGRAPH 2006: "adjusting the apparent age of faces"), from the old
  scans (yaro13, Ammamma, HSR0023 62, HSR0112 60).
- **Attack:** wrinkles are partly shape (folds) → the age macro carries the shape.

### 6 · SkinGen-style layers (parts 1, 9)
- **What:** CC5's SkinGen inventory in kind (360 skin elements: bases, normal effects, details, blemishes, acquired,
  body hair, nails): freckles, moles, age spots, acne, capillaries, veins, scars, tattoos, stubble shadow; lip lines
  deepening with age; ear translucency; areola glands.
- **Method:** a layer stack in the skin material (blend modes, masks, strength each, Blender nodes); freckles as a
  point process on UV with a size distribution (Schneider, Egger & Vetter 2018), real spots taken from scans.
- **Attack:** procedural blemishes look fake when uniform → distributions from scans, never uniform dots.
- **Substance's role in CC5, and ours:** SkinGen's "dynamic material is powered by Adobe Substance Technology"
  (parametric layers) and CC5 round-trips to Substance Painter for painting. Ours: Blender's shader nodes are the live
  layer engine (EEVEE and Cycles), Blender's bake writes the export maps; painting decals / tattoos / makeup / scars
  at exact places in Blender's Texture Paint, and a UDIM round trip (export tiles, paint, import) for any outside
  painter - ArmorPaint, TextureCraft (storytold, MIT OR Apache-2.0, pure Rust, a Substance-Painter-style layer painter
  with mesh-map baking and an MCP server; created 2026-10-14, in active development) or Substance itself. Tiling
  detail textures (pore tiles per region, freckle and scar patterns) authored in Blender nodes first; Material Maker
  (MIT) or MaterialCraft (storytold, MIT OR Apache-2.0, a Substance-Designer-style node designer; created 2026-11-01)
  only for a generator Blender lacks. Nothing bought. storytold's other craft apps (all pure Rust, weeks old):
  PhotoCraft / LightCraft as outside editors for touching up textures; EffectCraft for compositing renders (the film
  side, later); their craft-anything engine's Study -> Build -> Check loop (every build compared with the original and
  refined) - the method behind our gate. Licences read only for TextureCraft and MaterialCraft (MIT OR Apache-2.0).

### 7 · Body skin (part 1)
- **Method:** HSRD-100 bodies (standing, mostly bare skin) onto our body: correspondences from body keypoints on
  renders (Sapiens2, cached), procrustes + NICP, bake; regional offsets (elbows and knees darker, forearm redness with
  age — PMC11084701, rankings only).
- **Attack:** pose differences (arms, hands); if the wrap fails, regional detail tiles cut from the 16K atlases.

### 8 · Brows and lashes (part 4)
- **Method:** a strand brow generator — one hair per follicle on a shape mask, direction nearly vertical at the head
  turning horizontal toward the tail, thinner at the tail; shapes from MakeHuman's 14 CC0 brows (`eyebrows01`) fitted
  to each face's brow landmarks; lashes get MetaHuman's 7 style parameters.
- **Attack:** those masks read heavy and high on our faces before → fitted to landmarks.

### 9 · Facial hair (part 3)
- **Method:** beards and moustaches as density masks (MakeHuman `bodyparts05`, CC0) with a growth-direction field and
  per-style length; stubble as a skin layer under ~1 mm plus 1-3 mm strands for close-ups.

### 10 · Body hair (part 5)
- **Method:** MakeHuman's `fur.blend` (CC0, 15 regions) with masks by sex and age; per-strand colour variance (also
  for scalp hair — recommended 2026-10-30, never built).

### 11 · Scalp styles (part 2)
- **Method:** our generator on Blender's hair node groups: coily hair by Curly-Cue's method (SIGGRAPH Asia 2024; its
  MIT guides-to-full code), braids by Blender's Braid node group, locs (clumps round a noised tube), buzz cuts, balding
  masks (Norwood / Ludwig stages); grey as a per-strand whiteness share, dye and ombre (MetaHuman's colour controls);
  **hair cards for dense styles in the live view** (CC5's and MetaHuman's real-time path).
- **Alternatives:** image-to-strands AI (DiffLocks and others) — non-commercial or unlicensed weights; asset
  libraries (Code My Crown — no licence; OSAHL — no redistribution) — reference only; HairDeck (Apache-2.0) makes
  stylised cards from an image — its card layout method may help our card baker, not its look. No realistic open
  strand dataset was found on Hugging Face or Zenodo.

### 12 · Eyes (part 6)
- **Method:** on MPFB2's eye: crypts, furrows, pigment spots, Wölfflin nodules, collarette, heterochromia (each eye its
  own colour), arcus with age, drawn by population (Edwards et al. 2016's table; e.g. pigment spots 22% East Asian /
  58% European / 17% South Asian); sclera veins denser at the corners, redness, yellowing with age, melanosis.

### 13 · Mouth (part 7) — changed by the HF search
- **Method:** teeth and gum shapes from real dental scans - Poseidon3D's 400 intraoral scans (CC BY 4.0, 200 people)
  wrapped onto GNM's teeth and gums (as shape targets, so any character can take one), with GNM's 80 teeth identity
  directions for smooth variation between them; per-tooth gaps, wear, gum recession; tooth shade in VITA order
  darkening with age, enamel translucency and gum stippling calibrated on the MIO intraoral photos (CC BY 4.0); gum
  pigmentation from the skin's melanin; tongue papillae and coating.
- **Why changed:** real arches beat a statistical space alone for crowding, wear and gum shape; the photos give real
  shading targets.
- **Attack:** intraoral scans hold crowns and gums, not roots or the hidden tooth (only the visible part matters);
  whether GNM labels teeth individually → checked first; scan orientation and scale vary per case.

### 14 · Nails (part 8)
- **Method:** a layered nail shader on tile 1005 (blood-coloured bed, clear plate, lunula, white free edge, cuticle,
  ridges, yellowing with age); MakeHuman `bodyparts04` (CC0) meshes for long nails.

### 15 · Ears (part 9) — new from the HF search
- **What:** ear shape variety (helix, antihelix, concha, lobe) as real ears vary.
- **Method:** HUTUBS's 58 real head meshes (CC BY 4.0, metric, clean ears): each ear wrapped onto our base's ear
  region (landmarks + NICP, the head route) and stored as ear shape targets; a character's ear blends between them.
- **Attack:** the meshes carry no texture (shape only, which is what's missing); bald caps and smoothed faces are
  outside the ear region; the ear region's seam to the head must stay smooth.

**Children:** no open high-quality scan found (also not on Hugging Face or Zenodo); covered by the generator (rec 4)
and MakeHuman's age shape until one is.

## 7 · Order

**First, the gate (the user approved, 2026-11-04):** how far can EEVEE go? The same character in (1) our live view,
(2) our film render, (3) Unreal 5.8 with MetaHuman's shaders (installed at `F:\Epic\UE_5.8`, used locally for the
comparison only), beside the user's CC5 screenshots, measured, the user judging. If EEVEE can't reach the bar, the
fallbacks: a "Film preview" live mode (Cycles in the viewport with the RTX denoiser) for close-up work, and a live link
to Unreal (CC5 has one) through the planned Unreal plugin. A search for every way to raise EEVEE's live-view quality
(settings, light probes, our own shaders from published real-time skin / eye / hair methods, add-ons, live links) is
running and lands in this brief.

Then: 1 (live hair, half built) → 2 + 3 (bases, tone) → 4 (generator) → 6, 5 (layers, age) → 8-10 (brows, facial and body
hair) → 12-15 (eyes, mouth, nails, ears) → 7 (bodies) → 11 (styles, with cards for dense hair).

## 8 · How each is checked

Renders of the default as the user sees it (EEVEE live view and Cycles), side by side with the previous state, at
face, eye and full-body distances; numeric comparisons against Cycles where the live view should match it; one
test per change; full suites at the end of each batch.

## 9 · Where the author is least sure — please look hardest here

1. **Rec 1:** is a hand-written Marschner node group in EEVEE the best real-time hair route for Blender 5.3, or would
   hair cards (baked from our strands) plus a simpler shader give MetaHuman/CC5 quality sooner? What's the right
   multiple-scattering approximation without deep opacity maps?
2. **Recs 2-4 (variety):** is "scan base + AI-painted face" the best way to get any described person at MetaHuman
   quality, against a parametric approach (a PCA/statistical texture space over many scans, MetaHuman's way of
   blending a scan database), a UV-space diffusion model, or WildCap-style reflectance priors? Is 21 scans enough?
3. **Rec 3:** is per-texel chromophore inversion sound on photogrammetry albedo with baked light?
4. **Rec 7:** the best way to wrap posed full-body scans onto our A-pose body without a rig (we have no body rig yet).
5. **Anything missing** from the nine parts, or a source we haven't found - scans of children above all; open eye /
   iris imagery; realistic strand hair data; nails and lips (none found on Sketchfab, Hugging Face or Zenodo).
7. **Recs 13 and 15:** the best way to turn real scans (intraoral arches, ear meshes) into shape targets on our base's
   parts, and whether that beats a statistical model.
6. **Order:** would a different order reach the bar sooner?
