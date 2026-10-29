# The parity scorecard — CC5's inventory, with a floor that only rises

> **Status: APPROVED recs, written 2026-10-29** (the review's items 1–5, 10, 20–22, 25, 26 — TASKS; review file
> [`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md)). **The Plan column's keep,
> improve and drop entries are proposals for the user's look** (item 20), not decisions. R21: "The scorecard is CC5's
> inventory (§2), with a floor that only rises." Rows come from RESEARCH §2's feature inventory
> ([`../plans/2026-10-29-research-02-cc5.md`](../plans/2026-10-29-research-02-cc5.md) §2). Method: PhotoCraft's parity
> scorecard (RESEARCH §11) — the floor is the count of `done` rows, kept in `scorecard.json`, raised and never lowered;
> a test fails any change that lowers it ([`testing.md`](testing.md) §2).

Columns: **Plan** = keep (do what CC5 does), improve (do it better, how), new (ours, no CC5 row), drop (not built,
why), later (after R21's listed steps). **Step** = R21's step. **Status** = none · partial · done. **Proof** = the test
or gate report that makes it `done`. iClone's rows come when the Animate workspace is scheduled (R13); the "later"
rows below hold their place.

## Base bodies and morphs

| CC5 feature | Plan | Step | Status | Proof |
|---|---|---|---|---|
| Base generations (CC3+, HD, Game Base, LODs) | keep as one base with levels 0–2 and LOD variants; improve: one topology, no generation conversions | 2 | none | gate; `base_*` tests |
| HD base (SubD 0/1/2 with per-level maps) | keep (Multires + displacement) | 2 | none | gate |
| Convert between generations | drop — one base; import wraps instead | — | — | — |
| Neutral bases and templates | keep (library presets) | 2 | none | library tests |
| Morph sliders (anatomy groups, favourites, search, −200..200) | keep; improve: three shape spaces incl. scan-based MHR and GNM | 2 | none | slider tests |
| HD morphs (paid pack in CC5) | keep, free; HD sliders as displacement maps faded by the slider (N3) | 2 | none | golden images |
| Custom morph sliders (OBJ/sculpt → slider) | keep | 2 | none | `body.save_slider` test |
| Bake morph results | keep | 2 | none | test |
| ActorMIXER (blend up to six characters) | keep as "Mix" (blend slider states and textures); improve: any number of sources | 2 | none | test |
| Bone adjust / proportion | keep (bone-scale sliders) | 4 | none | test |

## Head and face

| CC5 feature | Plan | Step | Status | Proof |
|---|---|---|---|---|
| Headshot 3 image mode (photo → head, texture, body matching) | keep, free, local (GNM/FLAME fit + image models) | 3 | none | gate-style compare |
| Headshot mesh mode (scan/sculpt → rigged head) | keep (wrap) | 3 | none | wrap tests |
| Headshot AI image generator (cloud) | improve: local image models through the family engine | 3 | none | engine tests |
| Edit Facial panel (muscle drag, presets, FACS) | keep (control panel on the face rig) | 4 | none | UI test |
| Facial Profile Editor (edit each shape, batch update) | keep | 4 | none | test |
| Facial profiles Standard/Extended/Extended+/HD | improve: one DNA face rig by MetaHuman's control names, the ARKit 52 guaranteed | 4 | none | rig tests |
| Expression wrinkles | keep (the DNA's animated maps, driven by RigLogic) | 4 | none | golden images |
| MetaHuman interop (same skeleton/controls; mesh → MetaHuman; MHA import) | keep via the plugin; MHA curves drive our faces directly (the same control names) | 6 | none | round trip |

## Skin and materials

| CC5 feature | Plan | Step | Status | Proof |
|---|---|---|---|---|
| SkinGen layer stack (blend modes, masks, bake; free cap 15 layers) | keep, no cap | 2 | none | test |
| SkinGen Premium (custom images, dynamic tools) | keep, free | 2 | none | test |
| Digital Human shader family (skin, head, eye, occlusion, tearline, teeth, tongue, hair) | keep: Principled-based materials, exported as OpenPBR through MaterialX | 2 | none | gate |
| HD skin maps (8K, redness, cavity, EXR displacement, per-level normals) | keep | 2 | none | gate |
| Material tools (unify, merge, batch, tiling) | keep | 6 | none | test |
| Dynamic Appearance Editor (Substance-based) | improve: procedural node groups + image models; no Substance | 7 | none | test |
| Substance Painter round trip | keep (UDIM export/import of textures) | 6 | none | round trip |

## Eyes, teeth, tongue, hair

| CC5 feature | Plan | Step | Status | Proof |
|---|---|---|---|---|
| HD eyes (pupil depth, tearline, ducts, occlusion) | keep | 2 | none | gate |
| HD teeth and tongue, shaders, teeth position tool | keep | 2 | none | gate |
| Eyelash system (layers, templates, morphs) | keep; improve: strand lashes too | 2 | none | gate |
| Smart Hair cards (elements, groups, styles; ombré, ID maps) | keep cards as a bake; improve: strand grooms first | 2 | none | gate |
| Facial hair conform | keep (grooms bound to the face) | 2 | none | test |
| Hair authoring / import (card meshes, binding presets) | keep | 2 | none | test |
| Hair physics (spring, soft cloth) | keep (Blender hair sim; Jolt later) | 5 | none | test |
| MetaHuman groom on CC (Unreal) | keep via the plugin's groom binding | 6 | none | round trip |

## Clothes and props

| CC5 feature | Plan | Step | Status | Proof |
|---|---|---|---|---|
| Conform (full/partial, rigid detail, shrink wrap, tuck-in) | keep (MakeHuman's MHCLO fit, refit on body change) | 5 | none | test |
| Layering / cloth types, reorder, tuck-in preserve outer | keep (MHCLO `z_depth`, `juststage:tuckUnder`) | 5 | none | test |
| Hide body under cloth | keep | 5 | none | test |
| Transfer skin weights (presets, picker, vertex mode) | keep (robust transfer) | 5 | none | test |
| Skin-weight editor | keep (Blender weight paint + our tools) | 5 | none | test |
| Cloth appearance editor | improve: node groups + image models | 7 | none | test |
| FashionGen (AI cloth textures) | keep via the family engine | 7 | none | test |
| Cloth physics (PhysX soft cloth) | keep (Blender cloth; Chaos on export) | 5 | none | test |
| Marvelous Designer route | keep (FBX/OBJ/USD avatar out) | 6 | none | round trip |
| MetaTailor plugin | improve: fitting built in | 5 | none | test |
| Mix-dress across generations; replace character keeping outfit | keep (one base makes it trivial) | 5 | none | test |
| Props and accessories (pivots, attach, merge, spring) | keep | later | none | — |

## AI generation, rigging and import

| CC5 feature | Plan | Step | Status | Proof |
|---|---|---|---|---|
| AI 3D Generator (cloud, points) | improve: local image-to-3D through the engine where a model fits 8 GB (TripoSR MIT) | later | none | — |
| AI Studio (3D → images/video) | drop here — JustDirect's job (R20) | — | — | — |
| CC Wrap / Body Wrap (any humanoid → CC base) | keep (import wrap) | 6 | none | wrap tests |
| AccuRIG (auto-rig a static humanoid) | keep (skin-tokens.cpp, Rigify) | 4 | none | test |
| Characterization (bone-skinned import, profiles for Mixamo, HIK, Biped, Blender, UE4) | keep (profiles: Mixamo, HIK, UE5, VRM, Daz, CC, MPFB2) | 6 | none | import tests |
| Transformer (Daz → CC) | keep (Daz import, bridges and `.duf`) | 6 | none | import tests |
| Creatures | improve: human and creature kinds from the start; creature rigs and animations from Mesh2Motion (CC0) and Rigify's metarigs, automatic weights, sculpted shapes (items 22, 28) | 4 | none | test |
| Spring bones | keep | 5 | none | test |

## Poses and animation (CC5's own)

| CC5 feature | Plan | Step | Status | Proof |
|---|---|---|---|---|
| Edit Pose (IK/FK, lock, gestures, mirror) | keep (Blender pose mode + Rigify) | 4 | none | test |
| Motions (apply, import FBX/BVH, player, turntable) | keep | 4 | none | test |
| Face keys / puppet / mocap (iPhone, MHA) | keep: in Unreal now through the plugin (Live Link Face, MetaHuman Animator, Live Link devices — R13); in JustStage the webcam face preview at step 4 (R18), then MediaPipe, the Live Link Face stream and VMC with the Animate workspace (item 26) | 1, 4, later | none | test |
| Video mocap (cloud) | in Unreal now: MetaHuman Animator's Markerless Motion Capture (5.8, experimental; body Windows-only); in JustStage later, as an AI feature on the engine host (item 25) | later | none | — |

## Mesh tools and rendering

| CC5 feature | Plan | Step | Status | Proof |
|---|---|---|---|---|
| Edit Mesh (selection tools, delta mush, sculpt brushes) | keep (Blender edit and sculpt modes) | 7 | none | — |
| Subdivision / OpenSubdiv | keep | 2 | none | gate |
| Quad Remesher (trial-capped) | keep (Blender's remesh; Quad Remesher is paid) | 7 | none | test |
| High-to-low baking | keep (Blender bake) | 6 | none | test |
| InstaLOD optimisation | keep (Blender decimate + our LOD command) | 6 | none | test |
| Character levels / LOD (bone templates 101/54/22) | keep (LOD variants 0–3) | 4 | none | test |
| Real-time viewport (TAA, GI, DOF, LUT…) | keep (EEVEE) | 1 | none | gate |
| Image / video render | keep (Blender render) | 1 | none | test |
| Iray (paid; not in CC5) | improve: Cycles, free | 1 | none | gate |

## Pipeline, content, UI

| CC5 feature | Plan | Step | Status | Proof |
|---|---|---|---|---|
| FBX export (presets, UE skeleton, UDIM, LOD) | keep | 6 | none | round trips |
| Other formats (OBJ, USD, BVH, Alembic, GLB) | keep; improve: USD package, glTF, VRM first-class | 6 | none | round trips |
| GoZ (ZBrush) | improve: sculpt inside the app (R7); OBJ round trip for ZBrush users | 7 | none | test |
| ZBrush Face Tools (paid) | keep: sculpt expressions in app | 7 | none | test |
| Auto Setup family (Unreal, Unity, Blender, Maya, Max, Marmoset) | keep: the Unreal plugin; presets for the rest | 1, 6 | none | round trips |
| Omniverse connector | drop (out of scope by the user's word) | — | — | — |
| Send to iClone | later: the Animate workspace, or Unreal | later | none | — |
| Blender DataLink | drop — we are inside Blender | — | — | — |
| Content Manager / Smart Gallery / stores | keep as the asset library (local + remote); improve: licence labels on every asset; no store | 2 | none | library tests |
| UI layout (menus, toolbars, dockable panels) | keep: the application template's workspaces (R6) | 1 | none | UI tests |

## Floor

`scorecard.json`: `{ "floor": 0, "rows": N }` — the floor rises when a row turns `done` with its proof linked; a
pull request that lowers `done` below the floor fails the scorecard test.
