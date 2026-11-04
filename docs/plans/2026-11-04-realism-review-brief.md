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
- **Licences:** a licence is a label, never a filter (the user's rule). Every source gets routes, from its clause
  read at the source (`2026-11-04-research-licences-redo.md`): SHIP (in our download, modified), FETCH (each user gets
  it from the source), IMPORT (the user's own purchase, read by our importer), TRAIN (machine learning allowed - only
  if we pick a small LoRA; our texture work is not training), REFERENCE. An open-source download lets anyone open the
  files, so most store and royalty-free licences give IMPORT, not SHIP (Fab bars GPL and exporting tools; 3D Scan
  Store bars character makers and open source; Texturing.XYZ bars open source and any AI use). Pexels, Unsplash and
  Pixabay ship as textures made from the photos (creative work, picked by hand - their terms ban bots and ML
  collection); BlenderKit's royalty-free ships as a base for our own maps, never its raw files (the user's call).
  (Corrected 2026-11-04: an earlier draft filtered to CC / MIT-like only.)
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
  is plain colour + mottle + regions - though 13 HSRD-100 full bodies (16K), three Sketchfab CC-BY full bodies (8K)
  and Ten24's sample body (16K) are on hand, unused below the neck (rec 7).
- **Already tried and measured - AI repainting** (TASKS, 2026-10-29 to 11-02, ~100 rounds): FLUX repainted our clay
  views as photos with pore prompts ("visible pores, fine lines, slight redness", even light) and projected them. It
  gives the faces real colour (freckles, redness, creases, lip colour) and stays the face layer. Its measured limits:
  each painting invents its own fine detail (aligning views by DIS / RAFT optical flow made two of three held-out views
  worse, rounds 52-54); ten views read as ten different men; painted shadows read as dents; FLUX 3 at 2K paints real
  pores (fine detail 6.96 vs 2.92) but the head tile's 6.0 texels/mm caps it; the paintings' pores and the scanned
  pore tile looked alike at portrait distance (rounds 27-29), and "the photo's pores catch highlights ours don't". So
  pores come from one scan, and 2D skin enhancers (Wink, Claid, Enhancor - closed cloud repaints) would hit the same
  limits: not a route.

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

From the other-sites search (`2026-11-04-research-other-sites.md`: Wikimedia Commons, Flickr, Kaggle, GitHub,
Smithsonian, Europeana, OpenGameArt, itch.io, texture sites, Blender's demo files, and the user's Pexels, Unsplash,
Nexus Mods, ShareTextures, BlenderKit; samples in `.dev/downloads/other_samples/`):

| What | Licence | Use |
|---|---|---|
| Real iris macro photos: Commons' "Close-up photographs of 1 human eye" (462 files, 158 at 2000 px+), e.g. Lizapopova143 (studio cut-outs, iris 3,417 px across), Thomas Tolkien (5906²), Osmo Lundell, Mattis2412, Kamil Saitov (whole eyes with lids), CC0 brown / amber eyes, central heterochromia, children's eyes; brown, hazel, amber, green, blue, grey | CC BY / CC BY-SA / CC0 (per file) | real iris textures (rec 12) |
| Blender's demo "Hair Styles" (Daniel Bystedt): Geometry Nodes grooms - tight curls 22,418 strands, box braids 18,535, long 11,193, brows, lashes | CC BY-SA | library styles and the generator's techniques (rec 11) |
| OpenGameArt "Hair Alphas For Days": 85 rendered hair-card alphas, 2048² | CC0 | hair cards (rec 11) |
| Commons CC0 stubble series (two days, a week, greying; 4032 x 3024) | CC0 | the stubble layer's reference (rec 9) |
| Smithsonian life masks (Lincoln, Washington) | CC0 | face-shape references only |

Not shippable, checked at the source: Foot3D's 118 scanned feet (its request form: "strictly for non-commercial
research purposes", CC BY-NC 4.0; only its code is MIT); Nexus Mods 13537 (built from Cyberpunk's assets);
ShareTextures ("No asset redistribution ... in plugins").

From the redo of the filtered search (`2026-11-04-research-licences-redo.md`, `2026-11-04-research-redo-sources.md`;
stock photo sites, royalty-free marketplaces, scan and texture stores, Flickr 7 / 8, Hugging Face's "other" licence,
Japanese, Chinese and Korean sites):

| What | Licence / price | Routes | Use |
|---|---|---|---|
| Ten24 sample scan: full body + head, 16K colour (head 9.7, face 7.6-11, body 7.9 texels/mm, measured), six normal levels; a light-skinned adult man; downloaded to `.dev/downloads/ten24_sample/` | "use this scan as you wish for both commercial and personal projects", credit | SHIP with credit | body detail layers (recs 7, 17), the relief test (rec 18) |
| Renderpeople's own Sketchfab uploads (Mei Posed 001 East Asian woman 8K, Carla, Eric, Nathan, Dennis, Sophia, Claudia) | CC BY 4.0 (by the `renderpeople` account, API) - their shop terms cover shop files only | SHIP with credit | head and body bases |
| Pexels / Unsplash / Pixabay close-ups (skin by tone and age, freckles, moles, palms, hair, eyes); one sharp at 1:1 (Pexels 7479965, dark skin, follicles), most soft | own licences; no bots, no ML collection | SHIP as derived patches | small detail patches, references |
| BlenderKit royalty-free skins and CC0 sculpt brushes (micro-veins, fine wrinkles, milia) | RF: no re-sale "in the same form" | SHIP as a base | detail layers (rec 6) |
| deep3dstudio raw head scans: 16K cross- + parallel-polarised, Asian and European 60s-70s, African 20s-30s | $12.99 each; "For non-AI use only"; RenderHub bars making the asset accessible | IMPORT | user-supplied bases (better than HSRD for older faces) |
| KhitrovArt coily / afro grooms (Fab), PixelHair afro / 4C (Blender), khaloui coily styles (Superhive) | $13-170; Fab Standard / RF | IMPORT | users' own hair imports |
| Daniel Bauer "Eye Textures @ 8K": photographed sclera, vessels, maps | $50; licence text unread | IMPORT likely | sclera reference |
| 3D.sk (4,000 people, ages 0-71+, cross-polarised photo sets), Ten24 SP-6M (7,400+ people, 16K), HumanScanRepository | subscriptions / contract; ML by separate plan | TRAIN, IMPORT, REFERENCE | only if a small LoRA is ever picked |
| Texturing.XYZ, 3D Scan Store, Triplegangers, Fab, CGTrader, TurboSquid, Sketchfab Store | bar open source, character makers or end-user access | IMPORT at most (3D Scan Store: REFERENCE only) | - |

Flickr licences 7 and 8 and Hugging Face's "other" licence held nothing usable. Gaps that stay: children (3D.sk's
clothed photo references only), nails (scans reconstruct them poorly), sharp sclera veins, older Black faces (70+).

Confirmed gaps (searched on Sketchfab, Hugging Face, Zenodo and the sites above, nothing shippable at the bar):
realistic hair strands beyond the Blender demo (coily scans, beards), UV skin textures, nails and lips (references
only), children's 3D data.

Candidates found, not yet fetched: Sketchfab CC-BY scans (Renderpeople "Mei Posed 001" East Asian woman 8K; 3D
Selfie Scans "Malcolm", "Bryan", "Shelley", "Matt Chua", "Pete", "Ben"; "Hector Navarro Bust" older Latino man; more —
`2026-11-02-research-texture-source.md` §5); MakeHuman CC0 packs `eyebrows01`, `bodyparts04` (nails), `bodyparts05`
(beards), `eyelashes01`; Curly-Cue's code (MIT part, coily hair), Curvature Space Editing code (MIT); Edwards et al.
2016 iris-feature data (Dryad).

## 5 · Research already done (read before proposing; please don't repeat)

`docs/dev/RESEARCH.md` §1 (today's facts: EEVEE 5.3 light nodes, the hair diagnosis, skin-variety methods,
SkinGen's inventory, HSRD-100, iris colour searches), and the plan files `docs/plans/2026-10-30-research-*.md` (AI
texturing, photo-to-head, ComfyUI/FLAME, hair-eyes-teeth, skin detail shading, image models),
`2026-11-02-research-texture-source.md` (scan sources and licences), `2026-11-02-scan-skin-base.md` (the scan route),
`2026-11-04-realism.md` (this job's working doc), `2026-11-04-research-hf-assets.md` (the Hugging Face + Zenodo deep
search, its full query log), `2026-11-04-research-other-sites.md` (Commons, Flickr, Kaggle, GitHub, museums, the
user's sites), `2026-11-04-research-eevee-live-view.md` (every way to raise EEVEE's live view),
`2026-11-04-research-licences-redo.md` and `2026-11-04-research-redo-sources.md` (the redo of the filtered search).
Texturing.XYZ (CC5's MicroSkin source): its licence, read, bars releasing its textures or derivatives "under an Open
Source License" and any AI use - IMPORT only, so buying it for the app is not the rec.

## 6 · The plan: 18 recs (ears from the Hugging Face search, the EEVEE pass from the EEVEE search, 17 and 18 from the redo; recs 1, 3, 4, 7, 9, 11, 12, 13 updated by the searches)

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
- **Changed by the EEVEE search:** EEVEE treats world light as indirect (Cycles as direct), so the image-light gap
  (1.4-2.3x) is the world's share - an explicit world multiple-scatter term in the model; also Blender 5.0's Cylinder
  strand shape and 64 viewport samples for thin strands, measured.
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
  licence is a label; the painting gives colour only - fine relief and pores come from rec 17's shared layers (each
  painting invents its own fine detail, measured - §3).
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
- **Changed by the redo:** more bodies to draw on - Ten24's sample (16K, body 7.9 texels/mm measured, SHIP with
  credit), Renderpeople's CC BY Sketchfab bodies; the regional tiles feed rec 17 either way, so body detail does not
  wait on the wrap.

### 17 · One quality for every character (parts 1, 9) — new from the redo
- **What:** every character - library or slider-made, any tone or age - reaches the same skin quality; no character
  sharper or blotchier than another because of its source.
- **Method:** (a) all skins are already baked into one layout at one density (head tile 4096, face 6.0 texels/mm;
  body tiles 1024), so a 16K source cannot make one character sharper; (b) the fine relief (pores, micro-wrinkles,
  follicles) is a shared set of layers per region (forehead, cheek, nose, chin, lips, neck, torso, arms, hands, legs,
  feet) and age band, several variants each, cut from the best scans (HSRD-100's 16K heads and bodies, Ten24's 16K
  body, the Lee Perry-Smith tile) and offset per character; each character's colour and broad features from recs 3-6;
  (c) a build check: each character's fine-band energy per region (the face test's difference-of-Gaussian bands,
  `tools/face_test/flow_views.py`) and its left-in light measured against the best character; below a floor, the
  build fails and that source gives colour only.
- **Why:** CC5's SkinGen puts the same MicroSkin detail (Texturing.XYZ scans) on every character; MetaHuman selects
  scanned detail maps from a library; our measured limit is the tile, not the source.
- **Attack:** one pore set for all reads cloned -> per region, age and sex, several variants, randomised placement;
  a floor tuned to the best character could fail every phone scan -> they keep giving colour only, which is the
  point; the body tiles at 1024 cap body detail -> the shared tiling layers carry it at render time, not the baked tile.
- **Gate:** four characters of different tones and ages side by side at 1:1 on cheek, nose, hand and forearm: the same
  detail sharpness, measured within ~10% band energy.

### 18 · Relief and shine at pore scale — the test never run (part 1) — new from the redo
- **What:** the open part of "plastic": how the skin's surface catches light, not its colour (rounds 27-29: "the
  photo's pores catch highlights ours don't").
- **Method:** one close-up scene (cheek and nose, a light moving across, EEVEE and Cycles), four relief sources side by
  side: HSRD-100 16K crops, Ten24 16K crops, the Lee Perry-Smith tile, and relief estimated from a sharp photo
  (Pexels 7479965) by StableNormal / Marigold normals (Apache-2.0; RESEARCH: "none tested at pore scale"); with and
  without per-pore shine (roughness and specular darkened in the pores from the cavity map).
- **Why:** it decides rec 17's source; the AI colour route is already measured (§3), this part never was.
- **Alternatives:** Disney's graph-based micro-wrinkles (SGP 2023, training-free) as a fifth contender.
- **Attack:** photo relief from oily, specular light may be wrong at pore scale -> that's what the test measures;
  each source's scale set from its measured texel density.
- **Gate:** the user picks from the side-by-side; the numbers (band energy, highlight breakup under the moving light)
  beside it.

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
- **Changed by the other-sites search:** Blender's own "Hair Styles" demo (CC BY-SA) has a real tight-curl groom and
  box braids in Geometry Nodes - as library styles (share-alike label) and as the generator's starting technique, ahead
  of writing coils from scratch; OpenGameArt's 85 CC0 hair-card alphas for the live-view cards.

### 12 · Eyes (part 6) — changed by the other-sites search
- **Changed:** real iris photos exist under open licences (Commons and Flickr, CC BY / BY-SA / CC0, up to ~6K, all
  the common colours, heterochromia). So: a library of real irises - each photo unwrapped to polar coordinates,
  delit, its catch light removed, into MPFB2's iris layout - with the procedural features below for variety between
  them and for features a photo lacks. Attack: CC BY-SA photos make the derived iris textures share-alike (a licence
  label per iris); photo grain at 1:1; ethnicity rarely stated.
- **Changed by the EEVEE search:** our iris has no lens depth. The real-time standard (Jimenez GDC 2013, Unreal's
  Eye model, Unity HDRP's Eye, Animal Logic 2024) is parallax refraction: the view ray refracted at the cornea (IOR
  1.376), intersected with the iris plane at its measured depth, the iris UV offset, the limbus darkened at grazing
  angles; plus an iris caustic per light (Unity's "Eye Cinematic With Caustic") through Light Accumulation; a catch
  light on the cornea and tearline by light linking (EEVEE since 4.3). On the EEVEE-only output (Cycles refracts for
  real). Attack: parallax breaks past ~70°; the iris depth measured on GNM's eye first. NOT STANDARD in Blender.
- **Method (procedural part):** on MPFB2's eye: crypts, furrows, pigment spots, Wölfflin nodules, collarette, heterochromia (each eye its
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
- **Changed by the EEVEE search:** a mouth-interior darkening (CC5's teeth shader has "Rear AO") - a front-to-back
  gradient by distance behind the lips on teeth, gums and tongue, on the EEVEE-only output, following the jaw.
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

### 16 · The EEVEE live-view pass — new from the EEVEE search (`2026-11-04-research-eevee-live-view.md`)
- **What:** EEVEE's own settings and Blender-standard features we never used, each measured alone against Cycles.
- **Settings:** our skin's roughness (0.59) is above EEVEE's ray-tracing threshold (`trace_max_roughness`, factory
  0.5), so the skin's specular is never ray-traced -> threshold 0.7-1.0; ray-tracing and Fast GI resolution 1/2 -> full;
  viewport samples 16 -> 64 (capped: the card is shared); anisotropic filtering 2x -> 16x; overscan on.
- **Occlusion of the world light:** a volume probe around the character baked for visibility only (the world stays
  live) - shades under the chin, in the mouth, in the ears, between the lips (EEVEE treats world light as indirect).
  After rec 1 (it would darken the hair further today).
- **Skin calibration:** EEVEE's subsurface is screen-space Burley (Golubev 2018) - Unreal's screen-space mode's class,
  no new algorithm needed - so its energy is fitted against Cycles, as the hair colour was; the specular as two lobes
  (Unreal's 0.75x / 1.3x roughness, mixed 0.85) within EEVEE's three closure bins (SSS + two reflection lobes stays
  noise-free; a fourth closure goes stochastic).
- **Attack:** earlier trials found full-resolution Fast GI "changed little"; tracing rough skin can add noise; more
  samples keep the shared card busy while idle -> each change measured alone, samples capped.

**The gate's fallbacks, with facts from the same search:** Cycles in the viewport with DLSS Ray Reconstruction
(Blender 5.3: 1 sample a frame, reused and upscaled; no specular motion vectors; needs NVIDIA driver 620+ by the
release notes / 590+ by the PR - this machine has 610.88 - and the DLSS library, which the 5.3 beta doesn't ship; its
licence unread). An Unreal live view through Epic's "Send to Unreal" (MIT; Unreal's own remote execution) or our
planned plugin - weeks of work; the user works in Blender, so it stays the plugin's job.

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

Then: 16's settings (cheap, measured) and 1 (live hair, half built) → 18 (the relief and shine test - it picks the
detail source) → 2 + 3 (bases, tone) → 17 + 7 (shared detail layers incl. the body tiles; the body wrap) → 4
(generator) → 6, 5 (layers, age) → 12 (eyes, incl. parallax) → 8-10 (brows, facial and body hair) → 13-15 (mouth,
nails, ears) → 16's probe volume → 11 (styles, with cards for dense hair). (Changed by the redo: 7 moved up beside 17
- every character shows plain body skin today, and the bodies are on hand.)

**Superseded 2026-11-04 by §10** (the review adopted): the gate first, then the half it points to, then 18 → 2 +
delighting → 3 → 17 + 7 (skeleton first) → 12 → 1 → 4 → 6, 5 → 8-10 → 13-15 → the import command → 16's probe → 11.

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
8. **Rec 17:** do real pores differ enough by ethnicity and sex (not only by region and age) that shared layers need
   those axes too? (Not researched.) And is a per-region band-energy floor the right quality check?
9. **IMPORT route:** the best paid sources (deep3dstudio's polarised older heads, coily grooms, photographed sclera)
   allow a user's own purchase, not shipping - is an importer for user-bought scans worth building early?

## 10 · Adopted from the review (2026-11-04, the user: "your rec on all go")

From `2026-11-04-realism-review-fable.md` (Fable's 12 findings) and Opus's rethink appended to it. Where a rec above
says otherwise, this section wins.

- **The gate (§7)** runs first, before any build, with rec 16's EEVEE measurements beside it. Our character's baked
  maps on an instance of MetaHuman's `M_skin_unified_baked` (`Basecolor Baked`, `Normal Baked`, `SRMF Baked`,
  `Scatter Baked`), its micro-detail slot fed our own pore tile, region strengths uniform; a flat grey-map render first
  to prove nothing region-masked leaks; the same stage (and an HDRI-only shot), the same camera; renders captured
  linear and tone-mapped by the same AgX in Blender. Beside it EEVEE and Cycles; the MetaHuman preset as the
  benchmark, inside Unreal only (MetaHuman's maps never leave Unreal - clean-room). The verdict picks the half: our
  maps on MetaHuman's material still plastic → the maps first (18, 2, 3, 17); close to MetaHuman → EEVEE's shading
  first (16, 1, the fallbacks).
- **A live-view budget:** today's character measured in Material Preview (Blender's `wm.redraw_timer`, fps and VRAM,
  `quality-gate.md:43`), the target set from that; every rec's gate reports its ms and MB.
- **Rec 3:** the base picked by tone, sex and age from the 21; the broad layer's colour moved to the target by
  colour-statistics transfer (Reinhard et al. 2001); chromophore inversion off the critical path (its own experiment,
  gated on NIST's measured skins).
- **Delighting** (new step with rec 2): broad and mid bands only, the fine band kept; candidates yoso-delight-v0-4,
  Marigold IID, OpenDelight; measured by the light gradient and shine hotspots (forehead, nose) before and after -
  skipped where both are small.
- **Likeness:** a shipped character is never one scan's face (shape from GNM's space or the generator; broad and mid
  colour from two or more scans; fine from one); written into the spec; a recognition test (library renders against
  renders of each source scan at the same camera) when whole-face sources enter.
- **Rec 17** is the spec's `micro_normal` channel (16-bit tileable + tiling scalar; CC5's defaults body 42, face 20),
  exported as such; its floor measured on relief (height / normal) and roughness, colour judged per tone; colour fine
  detail and relief pores from the same source (today they come from two people: one scan's colour, the Lee
  Perry-Smith relief). Body tiles 2K (the spec's default) when body detail lands; library skins backed up before
  every rebuild.
- **Rec 7:** the spec's skeleton built first (UE5 bone names from MPFB2's joint cubes, `weights.game_engine.json` -
  `character-data-model.md:170-171`), posed to each scan's pose from keypoints, wrapped in the matched pose (one
  texture transfer); a body-model fit (MHR) only as the fallback.
- **Import (with rec 2 and rec 11):** "Import a scan" and "Import a groom" as commands on the existing route; a no-AI
  mode for sources whose licence bars AI software (Texturing.XYZ; deep3dstudio's "For non-AI use only"): manual
  landmarks, classical wrap, no learned masks or delighting.
- **Rec 1** bounded: two days to its 10% gate under both lights, then hair cards take the live view (strands for
  close-ups and the film); moved after the eyes.
- **Rec 16:** the closure count measured first (SSS, GGX, coat, sheen - possibly four); if noisy, the coat folded
  into the main specular before the fuzz goes (MetaHuman keeps region peach fuzz).
- **Smaller:** Poseidon3D is a "challenging cases" set - its arches are the extremes, GNM's directions the normal
  space; the Hair Styles demo's BY-SA version decides whether its grooms ship inside the GPL extension; children are a
  hole in the bar; lid shape and mouth corners named as shape items under recs 12 and 13.
