# Research — character mixing and the hair pipeline (2026-11-05)

> A research agent on two jobs the design leaves open: **mixing characters** ("actor mixing", not designed yet) and
> **the hair pipeline** for both the live view (EEVEE, 8 GB card) and the film (Cycles), plus **hair colour realism**.
> Only the gaps the coverage map (§0) found were researched. No code written, nothing rendered or measured.
>
> Marks: **[page]** the source's own page or file read (through WebFetch, curl or the GitHub API); **[snippet]** a
> search engine's summary only; **[code]** source code read; **[calc]** my arithmetic on cited numbers;
> **[inferred]** my reasoning from cited facts - a proposal, not a finding. Licence and patents are labels, never
> filters.

## Top findings

1. **CC5's ActorMIXER mixes a dedicated set of morph sliders, per part, and leaves every other slider alone.** CC has
   "three types of morphing sliders, Mixer, HD and General"; "The ActorMIXER only deals with the Mixer Sliders, which
   leaves the HD sliders and General morph sliders influences unchanged" - that split is how it makes "family members"
   (a shared feature on general sliders survives every mix). A character becomes a mixer asset by "Create Mixer
   Assets": "The body and facial features will be separated into different sliders and stored in their respective
   categories" (SubD 0 makes Mixer sliders, SubD 1-2 HD Mixer sliders). Parts: Head, Head Shape, Eyes, Nose, Mouth,
   Chin, Ears, Forehead; Body, Body Ratio, Torso, Arms, Legs. A wheel per category holds "minimum: 3" targets; a green
   blend point dragged among them sets the mix ("the inner circle maintains a stronger influence from the base
   character"). Skins are swapped ("Texture Switch", "Designating Skin"), not blended. PRO adds a CORE library of 44
   scanned heads with 43 skin textures. —
   [Mixer/HD/General sliders](https://manual.reallusion.com/ActorMIXER/Content/ENU/1.0/03-Using-ActorMIXER/Mixer-HD-General-Sliders.htm),
   [Creating Custom Mixer Sliders](https://manual.reallusion.com/ActorMIXER/Content/ENU/1.0/04-Using-ActorMIXER-Pro/Creating-Custom-Mixer-Sliders.htm),
   [Switching Categories](https://manual.reallusion.com/ActorMIXER/Content/ENU/1.0/02-Introducing-the-User-Interface/Switching-Categories.htm),
   [UI for Pro](https://manual.reallusion.com/ActorMIXER/Content/ENU/1.0/02-Introducing-the-User-Interface/User-Interface-Intro-for-Pro.htm),
   [80.lv, Fernández 2025-11-11](https://80.lv/articles/from-sculpt-to-infinite-variations-mastering-cc5-s-hd-character-workflow-and-actormixer),
   [CORE library](https://www.reallusion.com/character-creator/actor-mixer/core-library.html) [page].
2. **MetaHuman Creator blends up to three presets per region, and splits "features" from "proportions".** "Blend
   presets by global body or head regions, or locally"; "You can blend skeletal proportions, shaping, or both". Head
   Blend Space: Both / Feature ("feature/shape-based characteristics") / Proportions ("Only skeletal proportions are
   blended, while maintaining features/shaping"); Body: Shape / Skeleton ("bone lengths") / Both; a Delta strength
   ("the vertex delta"). Its Head Sculpt "finds the closest combination of real human facial features scanned into
   the MetaHuman database". Skin is not blended: a discrete "flipbook" texture index with filters (wrinkles, stubble,
   freckles, moles) and a 2D tone swatch. —
   [Blend tool](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-blend-tool-in-unreal-engine),
   [Head Sculpt](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-head-sculpt-tool-in-unreal-engine),
   [Skin material tools](https://dev.epicgames.com/documentation/metahuman/skin-material-tools) [page].
3. **The data model behind region mixing is published, and partly patented.** Same-topology neutral heads, region
   masks (overlapping), convex per-region weights plus a global blend, regions aligned to the globally blended face "so
   facial feature size and relative positions are preserved", skin blended per frequency layer (bilateral-Gaussian
   hierarchy: pores, wrinkles, freckles) - Soul Machines' patent US11354844B2 (active, claim 1 narrowed to
   muscle-descriptor regions, demographic modifications and eye/teeth/skull assets). Older: Blanz & Vetter's 4 face
   segments blended at the borders (1999, [snippet]); region PCA with continuity constraints, Disney US8922553B1
   (adjusted expiry 2033-08-28). No open implementation found beyond an S&box game's `FaceRegions.cs` (licence
   unread). — [US11354844B2](https://patents.google.com/patent/US11354844B2/en),
   [US8922553B1](https://patents.google.com/patent/US8922553B1/en) [page].
4. **EEVEE draws hair with no sub-pixel coverage.** In Blender's curves shader the Strand shape has zero geometric
   width (`shape.P = pt.P + shape.N * (is_strand ? 0.0f : pt.radius)`), Strip and Cylinder use the true radius; no
   coverage term is in the code read. 5.0 rewrote curve drawing: "a hair/fur system with default settings in 4.5 will
   now render 15 times more geometry in 5.0", added Cylinder and "an internal shadow bias for curves". The EEVEE hair
   closure PR #164595 is still a draft (one Kajiya-Kay lobe, updated 2026-10-02). —
   [`draw_curves_lib.glsl`](https://github.com/blender/blender/blob/main/source/blender/draw/intern/shaders/draw_curves_lib.glsl) [code];
   [5.0 EEVEE notes source](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.0/eevee.md) [page];
   PR #164595 via Gitea API [page].
5. **A shipped 60 fps strand system answers our two open live-view questions.** *Indiana Jones and the Great Circle*
   (SIGGRAPH 2025 Advances): all character grooms and facial hair as strands, no card fallback, ~2 ms; shading
   per vertex, Marschner R/TT/TRT "based on [Karis16] and [Tafuri19]" plus a multiple-scattering approximation;
   **self-shadowing precomputed offline by ray tracing each hair vertex, stored as clamped L1 spherical harmonics of
   the number of scattering events, read for every light** ("Essentially free"; deep opacity maps rejected for
   memory and per-light rasterising; voxel raymarching too soft at 256³); **LOD by a randomised strand order, a prefix
   of the buffer drawn, "scale thickness of each strand accordingly"**; coverage accumulated per pixel and
   reconstructed. The same visibility idea, for environment, direct and GI light: Gerard 2023 (arXiv 2302.06468). —
   [slides PDF](https://www.advances.realtimerendering.com/s2025/content/Strand%20Hair%20in%20IJGC%20-%20Final%20Slides%20(Post-Conference).pdf),
   [Gerard 2023](https://arxiv.org/abs/2302.06468) [page].
6. **Unreal's strands:** rasterised as thin camera-facing strips into MSAA sub-samples ("1 to 8 (set to 4 by
   default)", a per-pixel linked list "up to 32" for cinematics), lit with shadow and transmittance from a voxelised
   density volume or opt-in per-light deep opacity maps, multiple scattering by dual scattering; cards and meshes are
   the fallback "when Strands geometry is not possible". —
   [Groom scalability](https://dev.epicgames.com/documentation/en-us/unreal-engine/groom-scalability-and-performance-with-unreal-engine) [page];
   Unreal's 2020 hair blog [snippet].
7. **CC5's hair is cards with the Smart Hair shader; no "HD hair" product or manual page was found.** Six effect maps
   (AO, Z-depth, Flow, ID, Opacity, Root) plus optional base colour; colour as a Strand Color layer plus Highlight A and
   B layers driven by the Root and ID maps; "CC does not support Unreal's Pixel Depth Offset effect"; "the arrangement
   of the hair cards is the most contributor to the final visual result". The gate's Aaron (`docs/gate/2026-11-05/report.md:39`)
   reads "dense cards with fine flyaways". —
   [CC 3.4 hair wiki](https://wiki.reallusion.com/Content_Dev:CC_3.4_Hair_Creation_Process),
   [CC5 hair textures](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Hair/Textures-3-4.htm),
   [hair colours](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Hair/Hair-Colors-3-4.htm) [page].
8. **Strands → cards has a 2025 published method with code (no licence).** Strands2Cards (Tojo, Hu, Umetani, Li,
   SIGGRAPH Asia 2025): wisp clustering → skinning-aligned textures per wisp in UV → shared textures between similar
   wisps → strips fitted by differentiable rendering of coverage masks; all 342 USC-HairSalon styles in a game engine at
   30 fps on an M3 Pro. Repo `kenji-tojo/strns2cards`: no licence (all rights reserved), Windows 11, PyTorch CUDA 12.4. —
   [project](https://kenji-tojo.github.io/publications/strns2cards) [page]; GitHub API [page].
9. **Hair colour numbers:** pbrt's eumelanin σa (0.419, 0.697, 1.37) per unit concentration; its black, brown and
   blonde examples are concentrations 8, 2 and 0.15 ([page]) - in Cycles' Melanin input about **0.9987, 0.81 and 0.12**
   [calc, eumelanin only]. Chemistry: "Eumelanin contents decrease" from black to blond "with a trace but constant level
   of pheomelanin, except for red hair which contains about equal levels" (Ito & Wakamatsu 2011, abstract) [page].
   MetaHuman's hair controls: Melanin, Redness, Dye, Whiteness ("percentage of gray hairs"), Lightness, Roughness,
   Ombre (Shift, Contrast, Intensity), Highlights (Balance, Intensity, Variation) - no per-strand random control. —
   [pbrt 4ed §9.9](https://pbr-book.org/4ed/Reflection_Models/Scattering_from_Hair),
   [PMID 22077870](https://pubmed.ncbi.nlm.nih.gov/22077870/),
   [hair overrides](https://dev.epicgames.com/documentation/metahuman/hair-overrides) [page].
10. **Nothing shippable beats what we hold for grooms.** New searches found only royalty-free or all-rights-reserved
    freebies, paid packs, and research data (Strands2Cards uses USC-HairSalon, no licence). Real-time strand renderers
    with code: TressFX (MIT), vkhr (MIT), Unity's hair package (Unity Companion License, "Preserve global coverage as
    strands individually transition to subpixel"); hair meshes (Yuksel, SIGGRAPH 2024: 100 × 100k strands in ~2 ms on a
    4090) are "protected by US and Internal patents" with no code. [page] each, §2.5-2.6.

---

## 0 · What we already had (coverage map, read before any search)

| Job | Covered (file:line) | Evidence | Built? |
|---|---|---|---|
| ActorMIXER - what it is | `2026-10-29-research-02-cc5.md:115-116, 197` (six sources, wheel, body with/without bone scale, CORE 40+ heads, PRO $199, v1.1 load times) | CG Channel and the product page [page] | no |
| Mixing - the data model | `2026-11-05-base-mesh-first.md:37, 87-88` ("a character as weights over a library of identities - the same targets, blended. Its exact behaviour from Phase 1's research"); `parity-scorecard.md:28` ("Mix" over slider states and textures) | plan text only | no |
| MetaHuman's blend | `base-mesh-first.md:37` "identity blending from a scan-based preset library" | no source | no |
| EEVEE hair - closures, shapes | `2026-10-30-research-hair-eyes-teeth.md:111-130`; RESEARCH.md:176-191 (Light Accumulation nodes, Cylinder, PR #164595) | manual rst [page], source, measured | stand-in colour fitted (RESEARCH.md:337-349) |
| EEVEE hair - image-light gap | RESEARCH.md:348-349 (1.4-2.3x darker under the HDRI alone) | measured | open |
| Live-view hair model | `2026-11-04-realism-review-brief.md:202-223` (rec 1: Marschner + Karis node group); `:504-505` (bounded two days, then cards); Fable `:138-150, 206-209` | plan | half built |
| Unreal / MetaHuman real-time hair | `2026-11-04-research-eevee-live-view.md:34-38` (Marschner + dual scattering, deep opacity, voxels) | [snip] | - |
| Cards | hair-eyes-teeth `:312-326` (Unreal HCG, Hair Tool, CGHair, 3 small repos, our baker design) | page / API | no |
| Groom sources | hair-eyes-teeth `:416-430`; `2026-11-04-research-gaps.md:189-196, 1792-1829`; brief `:356-358` | page | MakeHuman pack in use |
| Colour model | RESEARCH.md:98-102 (Cycles' melanin σ); hair-eyes-teeth `:93-109` (per-strand variance "never built"; no measured melanin per colour) | source read | per-strand melanin attribute exists |
| Simulation, sims | building-blocks-pass2 `:411-415, 465-468` (Stable Cosserat Rods, hair meshes, TressFX 5) | page | - |

The gaps this pass took: ActorMIXER's and MetaHuman's exact mechanics and data; open implementations; EEVEE's hair
limits in code and notes; how CC5 and production engines render real-time hair; cards from strands since 2025;
2024-2026 real-time strand methods; groom sources; measured colour numbers. Not redone: image-to-strands AI,
simulation, eyes.

---

## 1 · Character mixing

### 1.1 CC5 ActorMIXER (its own manual)

- **What it is:** "ActorMIXER, a Character Creator plugin, provides an intuitive system for mixing and customizing 3D
  digital heads" ([Welcome](https://manual.reallusion.com/ActorMIXER/Content/ENU/1.0/01-Welcome/Welcome.htm)) [page].
- **Three slider kinds** (the table on [Mixer HD General Sliders](https://manual.reallusion.com/ActorMIXER/Content/ENU/1.0/03-Using-ActorMIXER/Mixer-HD-General-Sliders.htm)) [page]:

  | Kind | Made by | Level | ActorMIXER |
  |---|---|---|---|
  | General morph | Morph Slider Editor, Head & Body Morph Sliders | any | "Not affected" |
  | HD morph | same | SubD 1-2 ("Adds details on body parts") | "Not affected" |
  | Mixer | Plugins > ActorMIXER > Create Mixer Assets | SubD 0 | "Affected" |
  | HD Mixer | same | SubD 1-2 (shape + detail) | "Affected" |

  "Sliders marked as Not affected … are thus suitable for generating family members with similar facial features."
- **Making a mixer asset:** set the SubD level, open Create Mixer Assets, tick part checkboxes ("e.g., only the Head
  parts"), Create; "System will dissect the character into different parts controlled by the generated Mixer Sliders";
  each slider is a file ("Find File") [page]. The 80.lv walkthrough: "The system generates gallery items, facial and
  body sliders, and skin materials" [page].
- **Parts (categories):** Character; Head tab - Head, Head Shape, Eyes, Nose, Mouth, Chin, Ears, Forehead; Body tab -
  Body, Body Ratio, Torso (also "Body Shape"), Arms, Legs ([Switching Categories](https://manual.reallusion.com/ActorMIXER/Content/ENU/1.0/02-Introducing-the-User-Interface/Switching-Categories.htm)) [page].
- **How the user drives it:** two modes - Editing ("choosing package, wheel, swapping mixer assets", "Randomizing
  Shapes", "Designating Skin", saving wheels) and Mixing ("can only be used to blend or morph the shape"; "drag the
  green Blend Point near the assets"; Reset centres it) ([Two Modes](https://manual.reallusion.com/ActorMIXER/Content/ENU/1.0/02-Introducing-the-User-Interface/Two-Modes-for-ActorMIXER-Editing-and-Mixing.htm)) [page].
  A wheel layout is "composed of different number of targets (minimum: 3)"; "Randomize Wheel Presets … Fills up the
  targets randomly from all target presets in the same package"; "View Mixer Only (shows only Mixer Sliders on the
  Modify > Morph tab)" - the mix lands in morph slider values ([UI for Pro](https://manual.reallusion.com/ActorMIXER/Content/ENU/1.0/02-Introducing-the-User-Interface/User-Interface-Intro-for-Pro.htm)) [page].
  80.lv: "the inner circle maintains a stronger influence from the base character … the outer circle gives more
  weight to your presets"; mixing works "while the character is posed or has facial expressions applied" [page].
- **Body:** "Reshape the whole body without changing bone scale or adjust scale while preserving the original form";
  "Custom Body Mixers by Ratio, Shape, and Full Body" ([product page](https://www.reallusion.com/character-creator/actor-mixer/default.html)) [page].
- **Skin:** "Generate Skin Materials for effortless texture swapping"; CORE skins "fully blendable with any head
  shape" - i.e. any skin on any shape; nothing says skins blend with each other [page].
- **CORE library:** Asian 10 heads / 10 skins, Caucasian 14 / 14, African 10 / 9, Middle Eastern 10 / 10; 2K and 4K
  ([core library](https://www.reallusion.com/character-creator/actor-mixer/core-library.html)) [page].
- How the wheel turns the dot's position into weights is not published (Couldn't verify).

### 1.2 MetaHuman Creator (Epic's docs)

- **Blend:** "Combine between up to three presets"; "choose one or two to blend with the current MetaHuman
  character, or choose three presets to morph together"; viewport control points, each dragged toward the three slots
  of an "influence circle"; SHIFT starts a global head or body blend; Symmetry; Head Blend Space Both / Feature /
  Proportions; Body Blend Type Shape / Skeleton / Both; Delta ("the strength of the blend … (the vertex delta)"); "New
  Preset" saves the current character as a preset ([Blend tool](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-blend-tool-in-unreal-engine)) [page].
  The control points are not named on the page.
- **Head Sculpt:** markers each with "a limited, specific area" that overlap (two under the brow ridge, four for the
  lids and canthi); "Your changes with the controls are driven by the MetaHuman Creator (MHC) database of real-world
  human scans"; it "finds the closest combination of real human facial features scanned into the MetaHuman
  database"; Global Delta default 1.0 ([Head Sculpt](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-head-sculpt-tool-in-unreal-engine)) [page].
- **Body Params:** "parametric sliders or fixed body types" from "semantic and measurement-based inputs"
  ([Head and Body tools](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-head-and-body-tools-in-unreal-engine)) [page];
  5.6's body is built from "extensive real-world scanned data that you can sculpt and blend between" [snippet; the
  news page returned HTTP 500].
- **Skin:** Face and Body Texture Index ("A flipbook of discrete texture choices"), a Skin Filter by "density of
  wrinkles, stubble, freckles, and moles" ("the best candidate texture is applied automatically"), Skin Tone as a
  swatch position (U/V), Freckles, Accents, Texture Override ([skin material tools](https://dev.epicgames.com/documentation/metahuman/skin-material-tools)) [page].
  Texture synthesis runs as a cloud service [snippet].
- Epic's 2021 preview: the Creator "blends examples in the library in a plausible, data-constrained way" [snippet;
  the blog returned 403].

### 1.3 Other mixers found

- **Soul Machines Digital DNA Blender:** per-region percentage sliders - face, eyes, nose, mouth, head shape; bone
  structure from "Overall Blend" and "Skull shape"; any single non-zero phenotype becomes 100%; guidance "around 3-5
  features … Set one to be dominant"; not real time ("Apply Changes") [snippet, their support wiki].
- **S&box CharacterKit** (`FaceRegions.cs`, `CharacterBaseShape.cs` on sbox.game): per-region head weights and
  per-photo weights written to morph targets, regions without an override inherit the global blend, separate signed
  morph shapes [snippet; source and licence not read].
- **MB-Lab** (GPL/AGPL Blender add-on): parameters interpolated "in real time" by fuzzy logic, an expression mixer - not
  identity mixing [snippet].
- Searched and not found: a Blender, GitHub or open-source tool that mixes head scans by region (queries 6-8, §5).
  This is a gap in the search, not proof none exists.

### 1.4 The data model, from the papers and the patent

- **Soul Machines, US11354844B2** (priority 2018-10-26, granted 2022-06-07, active, anticipated expiry 2039-10-25)
  [page]: neutral shapes "of the same mesh topology and are blendable"; ten or more models across ethnicity, gender,
  age, physique; "Region segmentation is used to separate out different facial regions", regions may overlap; "the
  head model as well as the static region masks are blended together based on the user provided blending weights",
  convex constraints; "the system aligns the region segmentations to the globally blended face model" and merges by
  an objective with region, smoothness and centroid terms, so "the system maintains the size of facial features and
  relative positions"; skin "passed through a hierarchy of bilateral Gaussian filters", each layer (pores, wrinkles,
  freckles) blended separately, base weights summing to 1. Claim 1 (paraphrased by the reader): regions grouped from
  **muscle deformation descriptors**, **demographic prediction modifications** blended at a region mask, the result
  corresponding to an **eyeball, cornea, teeth, tongue or skull asset**.
- **Disney, US8922553B1** (Tena, De la Torre, Matthews; filed 2011-04-19, active, adjusted expiry 2033-08-28) [page]:
  "a spatially local PCA model where the parts are connected with continuity constraints … in the boundaries"; it
  "generalizes better than a holistic model"; a global solve for user manipulation of local control points.
- **Blanz & Vetter 1999:** four face regions fitted independently and blended at the borders; Anbarjafari et al. 2018
  take the three closest database matches per region weighted by inverse error [snippet, arXiv 1801.01089].
- **Blender's standard carrier:** a shape key can be limited to a vertex group - "Limit the active shape key
  deformation to a vertex group" ([shape keys panel](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/animation/shape_keys/shape_keys_panel.rst)) [page].
  So identity × region = a shape key masked by a region's soft vertex group, with no code of ours [inferred].
- PCA spaces (GNM's 253, MHR's 45) are global: mixing their coefficients mixes whole heads, so region mixing has to
  happen on per-vertex deltas with masks [inferred].

### 1.5 What JustStage has to put in a library [inferred]

From our files: ~21 scanned people (HSRD-100's 10, 11 CC BY heads - brief §4), GNM samples, MakeHuman's macro
targets, MHR bodies, users' own characters. CC5's base library is its embedded characters and PRO's 44 heads;
MetaHuman's is Epic's scan database plus the user's presets.

---

## 2 · Hair pipeline

### 2.1 EEVEE's hair, Blender 4.2-5.x

- **Shapes** [code, main 2026-09-09 `fdb5de1a`]: Strand = `half_cylinder_face_count == 0`, no width
  (`is_strand ? 0.0f : pt.radius`); Strip = a ribbon at the true radius; Cylinder = faces around the strand. The
  manual: Strand "a thin strand roughly a pixel wide. Curve diameter parameters are ignored" [page]. EEVEE's curves
  geometry shader passes radius and strand id to shading; no coverage or minimum-width term in either file read
  (`draw_curves_lib.glsl`, `eevee_geom_curves.bsl.hh`) [code]. So a true-width strip thinner than a pixel is hit or
  missed by pixel centres, and only the sample jitter accumulated over EEVEE's samples averages it [inferred].
- **5.0** (source of the release notes) [page]: drawing rewritten, "closer to Cycles 3D curves"; the `resolution`
  attribute now counted - "15 times more geometry", "in the most extreme cases, not display certain dense hair
  system", workaround "the attribute resolution can be manually tuned down"; Cylinder "better intersection in EEVEE";
  "an internal shadow bias for curves to avoid self shadowing artifact". 5.1-5.3 notes: nothing on EEVEE hair (5.3:
  Workbench hair metallic no longer randomised) [page].
- **Shading:** Hair BSDF and Principled Hair BSDF "Not supported" in EEVEE; Curves Info works (its Random uses another
  RNG) ([nodes_support.rst](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/render/eevee/limitations/nodes_support.rst)) [page].
  PR #164595: "WIP: EEVEE: Prototype Hair BSDF and Principled Hair BSDF nodes", draft, open, "isn't expected to land
  in its current state", a "Kajiya-Kay lobe f = (N.H)^alpha" [page, API 2026-11-05].
- **Performance, known issues:** EEVEE Next hair-particle report #114752 - a maintainer: strand steps 10 makes "1024
  vertex per hair strand"; "the main performance hit comes from shadow rendering"; one user 60+ fps (legacy) → 2.5 fps
  [snippet]. #120430: Interpolate Hair Curves on a dense surface slow, "fixed in 4.2" [snippet]. No fps figure for
  50-100k strands on an 8 GB card was found (query 15); ours is unmeasured.
- **New in main:** "Draw: GSplat implementation in EEVEE/Workbench/Overlay", committed 2026-09-16
  (`eevee_geom_gsplat.bsl.hh`); main is 5.4 alpha [code]. Whether our 5.3 beta has it: not checked.

### 2.2 How CC5 and MetaHuman render hair in real time

- **CC5:** cards + Smart Hair shader (§Top 7); Tangent or Flow map ("Both textures ensure the correctness of the
  highlights"); Root map (black roots, white ends) for root/tip colour; ID map for highlight colours; Specular Mask;
  depth used only for compositing [page]. Lashes "Support Smart Hair Shader and multi-layer application" [snippet];
  an "HD Eyebrow set with higher mesh density … powered by the Smart Hair shader" in the free resource pack [snippet].
  Cards made from XGen or Ornatrix grooms in Maya; "make the underlying layers more dense and outer layers more sparse"
  [page]. No source defines "HD hair" (queries 11, 17, 18).
- **Unreal / MetaHuman:** §Top 6 [page]; the 2020 blog: strands "rendered as thin triangle strips facing the
  camera", "a mixture of Deep Opacity Maps and a runtime voxelization", "the dual scattering approximation as an
  estimation for multiple scattering" [snippet]. Ambient occlusion from hair "can have significant cost"; ray-traced
  grooms "costly for memory" [page]. MetaHuman's LOD budget 50,000 strands at LOD0 (hair-eyes-teeth `:77`) [snippet].

### 2.3 A production strand renderer at 60 fps (*Indiana Jones*, SIGGRAPH 2025 Advances) [page, slides + notes]

- Budget ~2 ms; totals 1.64-2.39 ms by console (simulation 0.29-0.49, rasterisation 0.45-0.61, shading 0.26-0.62,
  composition 0.40-0.43); max 32k strands (low) / 65k (high); ≤2,000 segments per 64×64 tile, ≤2 million segments
  a frame.
- **LOD:** "randomizing strands order. Then we can take only a section of strands buffer, scale thickness of each
  strand accordingly and hair shape will still be the same" [Taillandier20].
- **Raster:** software, one lane per segment, per-pixel coverage, 3 depth-ordered layers plus an additive coverage
  layer; total coverage rebuilt as `saturate(x - 0.5*x*saturate(0.5*x))` from the summed coverage x ("a typical strand
  covers only about 20-25% of pixel area").
- **Shading:** per vertex, Marschner without glints, R/TT/TRT from Karis 2016 and Tafuri 2019, a multiple-scattering
  approximation, per-lobe artist scalers. "having good self shadowing on all lights is absolutely critical".
- **Self-shadowing, tried:** deep opacity maps (rejected: memory, rasterise per light); density raymarching per light
  ("Needs high grid resolution (up to 256x256x256)", "High-frequency details are missing"); stochastic probes (~6 ms
  on Series S). **Shipped:** "Trace visibility rays for each hair vertex offline, bake results to a spherical function
  … use for all lights … Essentially free"; L1 SH of the number of scattering events, misses biased to
  `-HAIR_MAX_SCATTER_EVENTS` (5), `visibility = exp(-absorption * numScatterEvents)`; rays also hit the head. Limits:
  "Can't handle strong deformations"; LOD "ghosts" acceptable.
- **Hair on skin:** density raymarch per skin pixel, 6 steps per light, 48³ grid, plus AO, ~0.3 ms; a sculpted proxy
  mesh for shadows on walls.
- Gerard 2023 publishes the visibility-SH idea for "an environment map, direct lighting or a global illumination
  system, without having to render deep opacity maps" [page, abstract].

### 2.4 Cards from strands

| Option | How | Licence / price | Evidence |
|---|---|---|---|
| **Strands2Cards** (SIGGRAPH Asia 2025) | §Top 8 | code public, **no licence**; CUDA | [page] |
| Auto hair-card extraction by differentiable rendering (arXiv 2505.18805) | "making cards for multiple levels of detail remains labor-intensive" | not read | [snippet] |
| Unreal Hair Card Generator | Dataflow: clumps → card geometry → shared textures, per LOD | Unreal EULA | hair-eyes-teeth `:317` |
| Daniel Bystedt's free GN setup | curves → card geometry, Blender 3.6+ | free, licence unread | [snippet] (CG Channel) |
| Simple Hair Cards | curve hair editor + texture maps, Blender 4.2-5.2 | GPL, $14.99 | [snippet] |
| Hair Particle → Card Generator (Orvix) | particles → curve cards | GPL, $4.99 | [snippet] |
| Amr Rezk "Texture Module" | GN scene for card textures (2026-06-16) | free, licence unread | [snippet] |
| FollicleFX | GPU grooming, card generator "in progress"; Windows, CUDA, closed DLL core | $79 founder / free community tier, terms unread | [snippet] |
| HairCS (arXiv 2609.16465) | cards → strands (the reverse) | not read | [snippet] |
| CGHair, Hair Tool 4, PurgatoryMP, hairball | earlier | hair-eyes-teeth `:316-320` | - |

### 2.5 Newer real-time strand methods (2024-2026)

| Method | What | Code / licence | Evidence |
|---|---|---|---|
| IJGC strand hair (MachineGames 2025) | §2.3 | none (talk) | [page] |
| Huang et al., "Real-time Level-of-detail Strand-based Rendering" (EGSR 2025, CGF 44(4)) | clusters swapped for thick strands by projected width, an aggregated scattering model, up to 13× | none found | [snippet] |
| Lipp, Jarabo, Wimmer, Bode, I3D 2026 (arXiv 2607.04230) | deferred software rasterisation of **hair meshes**, strand filtering, far field "at a single sample per pixel", LOD by coverage | none listed | [page] |
| Bhokare … Yuksel, "Real-Time Hair Rendering with Hair Meshes" (SIGGRAPH 2024) | strands generated on the fly by mesh shaders; 100k strands ~1 ms, 13-94 KB a model (8× MSAA, RTX 4090) | no code; "Hair meshes are protected by US and Internal patents" | [page] |
| Unity `com.unity.demoteam.hair` | strands as lines, strips or tubes; "Preserve global coverage as strands individually transition to subpixel"; a volume "scattering probe" | Unity Companion License (Unity-dependent projects only) | [page] README, LICENSE |
| TressFX 4.1 / vkhr | earlier | MIT / MIT | GitHub API [page] |
| Relightable Gaussian Codec Avatars (Meta, CVPR 2024), HairCUP (2025) | Gaussians for captured hair | no code link found | [snippet] |

Gaussian hair stays a capture route (from a person's video), not an authored groom; EEVEE's new splat drawing
(§2.1) would display splats but our grooms are curves [inferred].

### 2.6 Groom sources - anything better than ours?

Searched (queries 28, 29, plus the earlier files): Rudra's "Free Hair Grooms" (three particle styles, "Royalty Free",
no CC licence); VFX Grace's free hair ("All rights reserved for VFX Grace"); paid packs; Blender Studio's Singularity
("licensed under the Creative Commons Attribution 4.0" for its production assets; no groom named) [snippet each].
Nothing beats, for shipping: MakeHuman's pack (CC0), Blender's "Hair Styles" demo (CC BY-SA: curls, box braids, long),
TAU brows (CC BY-SA), OpenGameArt card alphas (CC0) - all already on disk (`.dev/downloads/other_samples/`,
`gaps_2026-11-04/`). Cem Yuksel's grooms are personal/research (`2026-11-04-research-gaps.md:196`). Blender's human
base-mesh bundle has no hair assets (catalogue and thumbnails listed today).

### 2.7 "Is there anything better than…"

- **Blender's hair node groups:** the studio standard is Houdini (MetaHuman's MH Groom tools), XGen, Ornatrix, Yeti
  (hair-eyes-teeth `:440-446`); in Blender, FollicleFX (paid, closed core, Windows/CUDA) and Hair Tool (paid). No open
  Blender groomer better than the built-in nodes was found.
- **Principled Hair BSDF:** it already holds both Chiang 2016 and Huang 2022 (microfacet, elliptical, "Aspect Ratio …
  0.8~1 for Asian hair, 0.65~0.9 for Caucasian hair, 0.5~0.65 for African hair", Reflection / Transmission /
  Secondary Reflection factors) ([hair_principled.rst](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/render/shader_nodes/shader/hair_principled.rst)) [page].
  A Blender Artists user: Huang "makes the hair significantly darker" and can be noisier; a reply: meant for far field
  [snippet]. No newer production hair BSDF turned up (query 26).
- **MakeHuman's hair pack:** better-looking open grooms exist only under CC BY-SA (Blender demo, TAU); nothing CC0.

---

## 3 · Hair colour and shading realism

### 3.1 What makes CG hair read as real (the sources' list)

- **Pigment, not paint:** colour from eumelanin and pheomelanin absorbed inside the fibre; reflection at the cuticle
  is white ("Reflectance at the interface is generally the same for all wavelengths") [page, pbrt].
- **Three lobes:** R (white, shifted by the cuticle tilt, "typically, 2" degrees), TT (backlit glow), TRT (tinted
  second highlight) [page, pbrt; IJGC].
- **Multiple scattering:** light hair needs many bounces - pbrt's blonde at 3 bounces against 50 ("Importance of
  Multiple Scattering in Blonde Hair") [page]; Chiang's colour mapping is the colour after multiple scattering
  (RESEARCH.md:188-189).
- **Self-shadowing:** "absolutely critical" - R and TT are "very bright for most incoming light directions" (IJGC) [page].
- **Strand-to-strand variation:** "Realistic hair should have a minimum of variance between each strand" (Blender
  manual) [page]; V-Ray's guide: root-to-tip change, low-frequency shifts, some lighter strands, restrained [snippet];
  darker roots (Softimage) [snippet]; CC5's ID and Root maps for exactly this [page].
- **Grey, dye, ombre, highlights:** MetaHuman's controls (§Top 9) [page].
- **Shape:** clumps at several levels, tip spread, frizz, flyaways (hair-eyes-teeth `:274-280`); elliptical
  cross-sections and glints (Huang; 3Delight: the glint "is caused by caustics inside hair strands") [page / snippet].

### 3.2 Numbers

- pbrt: σa eumelanin (0.419, 0.697, 1.37), pheomelanin (0.187, 0.4, 1.05); examples σa black (3.35, 5.58, 10.96),
  brown (0.84, 1.39, 2.74), blonde (0.06, 0.10, 0.20) [page].
- Cycles: eumelanin (0.506, 0.841, 1.653), pheomelanin (0.343, 0.733, 1.924); concentration = −ln(max(1 − Melanin,
  0.0001)) [page, manual]. Cycles' eumelanin is pbrt's × 1.207, its pheomelanin pbrt's × 1.83 [calc].
- pbrt's examples in Cycles' Melanin (eumelanin only, Redness 0): black 0.9987, brown 0.809, blonde 0.117 [calc;
  assumes both define σa per the same length - not checked].
- Redness: "a trace but constant level of pheomelanin" except red hair, "about equal levels" (chemical markers, not
  optical units) [page, abstract]. So Redness near 0 for black-brown-blond and ~0.5 for red [inferred]. The manual's
  own ladder (Blonde 0.25 … Black 1) is at Redness 1, i.e. pure pheomelanin [page].

### 3.3 What EEVEE can do of each [inferred unless marked]

| Effect | Cycles | EEVEE today | EEVEE possible |
|---|---|---|---|
| Melanin colour | Principled Hair | fitted stand-in, mean within ~5% per channel under the stage light (RESEARCH.md:346-348, measured) | same |
| Per-strand melanin and roughness variance | Random Color / Random Roughness | none | Curves Info Random in nodes (supported, different RNG [page]) |
| Root-to-tip, grey share, dye, ombre, highlights | via attributes | none | Intercept, Random, attributes in nodes |
| R / TT / TRT lobes, cuticle tilt | yes | none (diffuse fallback) | Light Accumulation node group (rec 1) |
| Multiple scattering | yes | none | Karis wrap term (rec 1); per-vertex baked visibility (§2.3) |
| Self-shadow from all lamps and the world | yes | shadow maps for lamps; world indirect only | baked L1 SH visibility read per lamp direction and against the world's SH |
| Elliptical fibres, glints | Huang | no | no (Huang's microfacet integral is not a node-group job) |
| Sub-pixel strands | path-traced | no coverage term [code] | width ≥ 1 px with alpha = coverage, dithered |
| Flyaways, clumps, frizz | groom | groom | groom |

---

## 4 · Assessment - the best design per job (mine, not a finding)

### 4.1 Mixing

- **Model:** a **library of identities** on the level-0 base, each one a full per-vertex delta stored as a MakeHuman
  target (the spec's format, §1.2) plus its landmark and joint positions and its skin layers; **regions** as soft,
  overlapping vertex groups that sum to 1 per vertex, named after CC5's categories (head shape, eyes, nose, mouth,
  chin, ears, forehead; torso, arms, legs, body ratio); **a character stores** per region a sparse weight list over
  library ids, a blend space per region (both / features / proportions - MetaHuman's), a strength (MetaHuman's Delta),
  and its ordinary sliders, which mixing never touches (CC5's family rule). Evaluated as Σ region mask × Σ weight ×
  identity delta into one "mix" shape key; Blender's per-key vertex group is the standard carrier for a live preview.
- **Proportions vs features:** proportions = the mixed landmark / joint positions; features = each identity's delta
  minus its own proportions, placed at the mixed positions (Soul Machines' alignment, MetaHuman's Feature mode).
- **Skin:** blend the broad and mid bands of the same identities by the face's weights, fine band from one -
  CC5 swaps and MetaHuman picks from a list, so this beats both, and it is the adopted likeness rule (never one scan's
  face) carried out by the tool.
- **Sculpt by database (MetaHuman's Head Sculpt):** a marker drag solves the region's weights by regularised least
  squares over the library - a later step.
- **UI:** the wheel (CC5) and the three-slot circle (MetaHuman) are two pictures of the same weights; numeric weights
  beside them; Randomize from a package.
- **Attack:** *seams* → soft masks summing to 1; *PCA spaces can't mix by region* → mix deltas, not coefficients;
  *21 people is half CC5's 44* → GNM samples and MHR bodies fill, scans give realism; *hundreds of keys
  (identities × regions)* → one baked key, live keys only for the wheel's 3-6 targets; *patents* → masked linear
  blending is 1999 prior art; Soul Machines' claim 1 needs muscle-descriptor regions and demographic modifications we
  don't use; Disney's region PCA with a global solve (to 2033) is near the sculpt step, so that step goes to a
  patent read first (not legal advice). What the attack changed: the sculpt solve moved to "later, after a patent
  read".

### 4.2 Hair

- **Film (Cycles):** strands, Principled Hair (Chiang for close-ups; Huang only where elliptical hair or far views
  show a difference, decided by a render), 3D Curves, per-strand variation - the standard, kept.
- **Live view (EEVEE): strands first, finished the way production strand systems finish them**, in this order:
  1. rec 1's Marschner node group (already half built);
  2. **baked per-vertex self-visibility** (IJGC, Gerard 2023): ray-cast offline from each curve point against the
     groom and the head (Blender's BVH), store L1 SH of scattering-event counts as four point attributes, read per lamp
     in Light Accumulation and against the world's SH (a constant per HDRI) - the published answer to "multiple
     scattering without deep opacity maps" and to the open 1.4-2.3x image-light gap;
  3. **coverage-preserving width:** a Geometry Nodes step sets each strand's width to at least one pixel's footprint
     at the camera's distance and the material's alpha to true width / drawn width (dithered) - Unity's and Unreal's
     sub-pixel answer;
  4. **LOD by random strand subsets** with width × (all / kept) - IJGC's LOD, one attribute and a Delete Geometry.
  Cards come second: our own baker on Strands2Cards' method for far LODs, slow machines and export to CC5, glTF and
  games - not the live view's default.
- **Why strands over cards for the live view:** MetaHuman uses strands at LOD0, IJGC shipped strands everywhere, our
  grooms are strands, and the gate's gap (sparse clumps against "dense cards with fine flyaways") is groom density and
  shading, not the primitive. CC5's own manual: "the arrangement of the hair cards is the most contributor" - cards
  need hand arrangement we don't have.
- **Attack:** *dithered alpha shimmers in motion* → TAA samples (the 64 viewport samples measured) and the width
  floor only where strands are sub-pixel; *frame time unknown on the 2070 Super* → the live-view budget measures 50k
  strands with and without each step before the next; *5.0's 15x geometry* → resolution attribute 1 for live view;
  *baked visibility breaks under strong motion* → IJGC found it acceptable for short and medium hair; re-bake on a
  groom edit; *world SH needs the HDRI's SH* → computed once per world; *NOT STANDARD* → Blender has no hair closure;
  the node group and the bake are ours, replaced if Blender ships one. What the attack changed: the visibility bake
  goes before the coverage work, because the image-light gap is measured and the coverage effect is not.

### 4.3 Colour

Per-strand melanin with a spread (Curves Info Random in EEVEE, Random Color in Cycles); defaults from §3.2 (Redness
near 0 except red hair ~0.5); grey as a per-strand whiteness share, dye, ombre and highlights as MetaHuman names them;
root-to-tip by Intercept; R shifted by a ~2° cuticle tilt. All doable in EEVEE nodes except Huang's glints.

---

## 5 · Queries run and what they returned

Search-mistake check before the first query: (a) no licence in any query; (b) every verdict marked, yes/no quotes
the page; (c/d) plain queries piloted first (1, 2, 10, 11), then narrowed where they returned noise (1 → 3-4; 10 → 12-15);
(e) plain wording first; (f) "better than" asked for the BSDF (26), the grooms (28), the groomers (31); (g) the
coverage map (§0) came from passages read; (h) one pass covered both jobs and the colour model; (i) no launch was
gated; (j) "how do others do it" = CC5, MetaHuman, Soul Machines, IJGC, Unity, Unreal; (k) no API filters used;
(l) no agent results used; (m) picks are in §4 with their queries; (n) `.dev/downloads/` checked for hair before
claiming gaps (§2.6).

| # | WebSearch query | Returned |
|---|---|---|
| 1 | CC5 actor mixer how it works | mostly audio-mixer noise; ActorMIXER page, a tutorial, an 80.lv author page |
| 2 | metahuman creator blend faces how it works | Epic's Blend tool and Head and Body tools pages, press |
| 3 | Character Creator 5 manual ActorMIXER mixer wheel facial features mix region slots | the manual's family-members page, 80.lv article, tips page |
| 4 | manual.reallusion.com ActorMIXER wheel targets blend point skin designate | the manual's UI, Pro UI, Two Modes, Packing Wheels pages |
| 5 | MetaHuman 5.6 texture synthesis skin parametric body how it works scan database | MetaHuman 5.6 news, skin material pages, forum posts |
| 6 | blender addon mix characters faces like actormixer open source | MB-Lab wiki, Poly Hammer DNA add-on, a paid low-poly mixer |
| 7 | region-based face model blend identities per region boundary blending 3D morphable model segments | Tena 2011, Disney and Soul Machines patents, Anbarjafari 2018 |
| 8 | github character face mixer blend multiple head scans per region weights morph targets tool | S&box CharacterKit, MPFB issue 302, CC5 CORE page |
| 9 | Soul Machines Digital DNA blend faces regions how it works | Soul Machines support wiki, the patent |
| 10 | best way to make realistic hair in Blender EEVEE | marketplace listings and a 2.83-era thread - nothing usable |
| 11 | Character Creator 5 HD hair what is it strands cards | marketplace packs, a forum thread; no definition |
| 12 | Reallusion Smart Hair shader how it works hair cards flow map depth anisotropic Character Creator | CC 3.4 hair wiki, CC5 manual hair pages |
| 13 | Unreal Engine groom strands rendering how it works visibility buffer deep opacity maps sub-pixel | Epic's groom scalability doc, the 2020 hair blog |
| 14 | Blender 4.2 EEVEE Next hair curves rendering shadows transparency release notes strands | 4.2 EEVEE shadow notes; nothing on hair |
| 15 | EEVEE hair curves viewport performance slow many strands fps 100k Blender 4 5 | issues #114752, #120430, the 5.0 EEVEE notes |
| 16 | hair cards vs strands realtime quality comparison 2025 which looks better close up | Fab listings, EA Frostbite hair post |
| 17 | "Character Creator 5" hair new features HD hair shader strands 2026 | CC5 launch coverage, Smart Hair Shader manual page |
| 18 | reallusion "HD Hair" CC5 pack | CC5 3D content page (HD Eyebrow set); no "HD Hair" product |
| 19 | generate hair cards from strands groom free tool 2026 Blender open source | FollicleFX, Bystedt's free setup, Simple Hair Cards, Rezk module |
| 20 | Game-Ready Hair in Minutes Yuksel SIGGRAPH 2026 hair cards automatic | Strands2Cards, arXiv 2505.18805, HairCS, hair meshes article, HairDeck; the named talk not found |
| 21 | relightable gaussian hair real-time strands 2025 2026 code github | RGCA (CVPR 2024), HairCUP; no code links |
| 22 | latest techniques realistic hair rendering real time 2025 2026 SIGGRAPH strand hair | Lipp 2026, Huang EGSR 2025, IJGC talk, Roblox interpolation |
| 23 | "Real-time Level-of-detail Strand-based Rendering" Computer Graphics Forum 2025 authors code | authors and project page; no code |
| 24 | eumelanin pheomelanin content human hair black brown blond red measured ratio table | Ito & Wakamatsu 2011, Wikipedia |
| 25 | what makes CG hair look realistic shading per strand color variation flyaways tips | V-Ray guide, 3Delight, Softimage, Maxon docs |
| 26 | better hair shading model than Chiang Principled Hair BSDF Cycles Huang elliptical 2024 2025 hair rendering | Blender API docs, issue #111257, a Blender Artists thread on Huang |
| 27 | real-time hair multiple scattering approximation 2024 2025 paper strand shading without deep opacity maps | Gerard 2023, Zinke 2008, Lipp 2026 |
| 28 | free realistic hair groom download Blender hair curves CC0 CC-BY 2026 | Rudra (royalty free), VFX Grace (all rights reserved), paid packs |
| 29 | Blender Studio character files hair curves groom download license CC-BY Charge Singularity | Singularity's CC BY page; no grooms named |
| 30 | MetaHuman hair material controls melanin redness salt and pepper ombre highlights documentation | Epic's hair overrides page, Convai guide |
| 31 | FollicleFX Blender hair grooming addon community edition license features | the BA announcement (Windows, CUDA, $79) |

Read directly (WebFetch, curl, GitHub and Gitea APIs): Epic's Blend, Head Sculpt, Head and Body, skin material, hair
overrides and groom scalability pages; Reallusion's ActorMIXER product and CORE pages, seven ActorMIXER manual pages,
the 80.lv walkthrough, the CC 3.4 hair wiki, three CC5 hair manual pages; Google Patents US11354844B2 and US8922553B1;
Blender's `draw_curves_lib.glsl`, `eevee_geom_curves.bsl.hh`, `eevee_geom_gsplat.bsl.hh` and their commit logs, the
4.2-5.4 EEVEE release-note sources, three manual rst files, PR #164595; Strands2Cards' page and repo; Yuksel's hair
meshes page; Lipp 2026 (TU Wien, arXiv); Gerard 2023 (arXiv); the IJGC slides (PDF, text extracted with pdftotext);
pbrt 4ed §9.9; PubMed 22077870 (E-utilities); GitHub API for TressFX, vkhr, Unity's hair package. Failed: MetaHuman
5.6 news (HTTP 500), Unreal's 2021 preview blog (403), MetaHuman sneak-peek (login redirect), EGSR 2025 paper page
(403), Blender's 5.0 notes site (403; the source file was read instead).

---

## Couldn't verify

- How CC5 turns the blend point's position into weights; whether its skins ever blend (only swapping is documented).
- MetaHuman's Blend control-point list; Epic's own words on "data-constrained" (snippet only).
- Any "HD hair" in CC5 - no product or manual page by that name was found (queries 11, 17, 18).
- EEVEE frame time for 50-100k strands on the 2070 Super, with or without the steps in §4.2 - nothing rendered here.
- Whether the 5.3 beta contains EEVEE's Gaussian-splat drawing (on main since 2026-09-16).
- The pbrt-to-Cycles melanin conversion's length unit; Ito & Wakamatsu's numbers (abstract only).
- Code for Huang et al. EGSR 2025 and Lipp et al. 2026; the arXiv 2505.18805 and HairCS methods (titles only).
- The licences of S&box CharacterKit, Bystedt's card setup, Rezk's module, FollicleFX's free tier.
- Patent scope: claims paraphrased by a reader tool, not read in full; not legal advice.
- Unity's coverage-preserving LOD mechanism beyond its README line.
