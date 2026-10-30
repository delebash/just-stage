# The character data model

> **Status: APPROVED recs, written 2026-10-29.** The review's recs 1–27 were approved by the user ("i agree with your
> recs"; then "your rec on all 1-6 as long as you think on it again and make sure you dont change your mind go" —
> [`../dev/TASKS.md`](../dev/TASKS.md)); this document is rewritten to them from Fable's draft
> ([`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md), items cited as "item N").
> Facts: [`../dev/RESEARCH.md`](../dev/RESEARCH.md) (§ numbers). Each piece names its standard, or is marked
> **NOT STANDARD** with the user's approval beside it. Blender facts are checked on the installed Blender 5.3.

## 0 · Where the data lives

A character has three forms, each with one job ([`README.md`](README.md) §3):

| Form | Job | Standard |
|---|---|---|
| **Blender data in a `.blend`** | the live character while the user works, and the asset-library copy | Blender's data model — Mesh, Shape Keys, Armature, Curves, Material, Image — plus JustStage's fields in hand-written `bpy.props` `PropertyGroup`s ([PropertyGroup](https://docs.blender.org/api/5.3/bpy.types.PropertyGroup.html)) |
| **The character package** (a folder: `character.usda` root layer, `.usdc` side layers, `textures/`, `grooms/`, `garments/*.mhclo`, `rig/face.dna`, `rig/body.dna`) | the portable character: export, import, the Unreal plugin, JustDirect, archives | OpenUSD (UsdSkel, UsdShade with MaterialX, UsdGeomBasisCurves, UsdGeomSubset, UsdMedia, `assetInfo`, `customData`), Epic's DNA for the rigs ([UsdSkel](https://openusd.org/release/api/_usd_skel__intro.html), [OpenRigLogic](https://github.com/EpicGames/OpenRigLogic)) |
| **The FBX sidecar** (`<name>.juststage.json`, beside FBX exports only) | the few JustStage fields FBX can't hold — CC5's (FBX + JSON + `.fbxkey`), Daz's (FBX + `.dtu`) and MetaHuman's (FBX + `.dna`) pattern (§8, S9) | JSON; glTF needs no sidecar — its `extras` slot carries the same fields (item 11) |

**No JustStage USD schemas** (item 6). After the existing formats took their jobs — the DNA for correctives (§2),
MakeHuman's formats for sliders and clothes (§1.3, §5), MaterialX for materials (§3), Blender's hair nodes for grooms
(§4) — only a handful of fields have no standard home. They are plain USD attributes in the `juststage:` namespace,
the way Blender's own exporter writes custom properties (its `userProperties` namespace — manual `usd.rst`), written
from the `PropertyGroup`s by Blender's USD hook API (`bpy.types.USDHook.on_export`/`on_import` — §8; Blender 5.0+ keeps
`bpy.props` values apart from custom properties, so the native custom-property export doesn't see them, hence the hook).
Readers that don't know them ignore them; JustStage and the Unreal plugin validate them.

**NOT STANDARD (N1) — APPROVED 2026-10-29** ("your rec on all 1-6 … go", TASKS): the names of these attributes. No
standard defines them (AOUSD's character group has published nothing; the cloth-and-hair physics proposal, OpenUSD PR
#111, is open — §8). The complete list:

| Attribute | On | Type | What it holds |
|---|---|---|---|
| `juststage:formatVersion` | `/Character` | int | the version of this attribute set (§6) |
| `juststage:kind` | `/Character` | token `human` \| `creature` | the two kinds of character (§1.0) |
| `juststage:baseVersion` | `/Character` | int | the frozen base mesh's version (§1.1) |
| `juststage:skeletonVersion` | `/Character` | int | the skeleton's version ([`skeleton-and-face.md`](skeleton-and-face.md) §1) |
| `juststage:sliderIds` | `/Character` | token[] | the slider ids whose values differ from default |
| `juststage:sliderValues` | `/Character` | float[] | their values, parallel to `sliderIds` (MakeHuman's MHM "modifier" values, §1.3) |
| `juststage:faceRig` | `/Character` | asset | `rig/face.dna` |
| `juststage:bodyRig` | `/Character` | asset | `rig/body.dna` |
| `juststage:layer` | a garment mesh | int | its layer order, outermost highest (MHCLO's `z_depth`) |
| `juststage:tuckUnder` | a garment mesh | relationship | the garments it goes under |
| `juststage:fit` | a garment mesh | asset | its `.mhclo` fit file (§5) |
| `juststage:cloth:mass`, `:stiffness`, `:damping`, `:collisionDistance`, `:pinGroup` | a garment mesh | float / token | its cloth settings (§5) |
| `juststage:audio` | a take | relationship | the take's `UsdMediaSpatialAudio` ([`animation-and-later-features.md`](animation-and-later-features.md)) |

Plus one `UsdGeomSubset` family name, `juststage:hide` (body faces hidden under a garment, §5), and one `customData`
key, `juststage` (provenance, §6). The character's id, display name and version are USD's own `assetInfo`
(`identifier`, `name`, `version`). glTF carries the same fields under `extras.juststage`; FBX in the sidecar.

## 1 · The base human

**R4, decided:** MakeHuman's hm08 topology is subdivision level 0; two Catmull-Clark levels sit on it with displacement
on top (CC5 HD's method); three shape spaces are wrapped onto it.

### 1.0 Two kinds of character (item 22)

- **Human** — the hm08 base, the UE5 skeleton, the ARKit 52 face and the DNA face rig; everything in this document.
  Humanoid creatures (orcs, elves, aliens) are humans with sculpted sliders, so they keep the rig, face and clothes.
- **Creature** — any mesh with its own skeleton and its own face shapes (CC5's "Creature": "its own skeleton, no facial
  controls, nothing swappable" — §2): rigged from **Mesh2Motion's CC0 creature rigs** — birds, dragons, spiders, kaiju,
  foxes, horses, fish, snakes, each with its own CC0 animations (item 28; MIT code, "The art assets (3d models, rigs,
  animations) are all licensed under CC0" — §5) — or Rigify's creature metarigs (basic quadruped, bird, cat, horse,
  shark, wolf — on disk in Blender 5.3), weighted with Blender's automatic weights, shaped by sculpting (Blender Studio's
  CC0 base meshes are starting points in the library — §1.1), its expressions plain shape keys. USD, glTF and FBX carry any skeleton; the Unreal plugin makes a skeleton asset per creature. Built in
  step 4 beside the human rig (R21 as changed). No open creature body with sliders exists (§5), so a creature starts
  from a sculpt or an import, as in CC5.

### 1.1 The base mesh (`js_base_body`, version 1)

| Fact | Value | Source |
|---|---|---|
| Topology | hm08: all quads, "completely triangles free", poles ≤ 5 edges, made for subdivision | §5 |
| Dots (vertices), level 0 | 19,158 in the whole mesh: 13,380 in the `body` group (the skin) and 5,778 in the helper geometry and joint cubes | §5 |
| Faces, level 0 | 18,486 quads in the whole mesh (no triangles), 13,378 of them in the body — measured in MPFB2's `base.obj` at the pinned commit (was: "14,766 for the whole mesh" until 2026-10-29) | §5 |
| Licence | CC0 1.0 (MPFB2's assets) — the base, the 1,258 targets; MakeHuman's hair-editor pack — the 16 styles MPFB2 lists | §5 |
| Levels | 0 (editing, shape keys, skinning), 1 and 2 (Catmull-Clark through Blender's Multires modifier, which stores per-level displacement; 5.3 shows textures and attributes while sculpting on it) | [Multiresolution](https://docs.blender.org/manual/en/5.3/modeling/modifiers/generate/multiresolution.html), §8 |
| Expected counts | ×4 faces per level (CC5 HD: 70,732 at SubD 1, 282,928 at SubD 2 from 17,683) | §2 |

Rules:

- **hm08 ships whole, helpers and joint cubes included** (item 2; N2 withdrawn). The helpers (tights, skirt, hair,
  genital) are what MakeHuman's clothes fit to, and the joint cubes are what every MPFB2 rig places its joints from
  (`"strategy": "CUBE"`, §5) — so they are how joints and clothes follow the body when sliders change it. MPFB2's own
  workflow: the helpers are **hidden while editing** (a mask) and **deleted at export** (§5). Standard: MakeHuman's.
- **The body's topology is frozen** once the gate (R3) passes on it. A change bumps `baseVersion` and ships a vertex
  map from the old base (`data/base/maps/v<old>-to-v<new>.json`), so every morph, texture and garment still loads.
- **Parts** are separate meshes, each with its own base version: `eye.L/R` (eyeball with cornea bulge), `cornea.L/R`,
  `occlusion.L/R` (the eye shell), `tearline.L/R`, `teeth_upper`, `teeth_lower` (with gums), `tongue`, `eyelash.L/R`
  (card lashes; strand lashes are a groom). hm08's own eyes (72 vertices) and teeth (68) are too coarse for the bar, so
  eyes, occlusion, tearline and lashes are built (R5); teeth, gums and tongue come from GNM or ICT geometry under their
  licences (GNM Apache-2.0, ICT MIT — §5, §7). Parts are fitted to the body as MakeHuman fits its eyes — by MHCLO
  (MakeHuman's format covers "clothes … hair and eyes", §5). Part names follow MetaHuman's face-part names where one
  exists (item 10, [`skeleton-and-face.md`](skeleton-and-face.md) §2.3).
- **Units and axes inside Blender:** metres, Z up, −Y front, standing on the floor (the body's lowest vertex at
  z = 0 — MPFB2's `feet_on_ground`). Interchange converts ([`interchange.md`](interchange.md) §1).
- **Rest pose:** A-pose (arms about 45° down), facing −Y. MetaHuman conforming required A-pose in 5.6 and takes A to T
  since 5.7 (§8); A-pose binds keep shoulder deformation. Exports that need a T-pose re-pose through the retarget pose,
  never the bind pose ([`skeleton-and-face.md`](skeleton-and-face.md) §1.4).
- **Fallback base** (item 23): if the gate fails on topology, Blender Studio's Human Base Meshes (CC0; quads made for
  subdividing, realistic bodies, UDIM UVs; no sliders, no rig — §5) take hm08's place, with MakeHuman's CC0 sliders moved
  onto them by wrapping (CharMorph's "alternative topology" transfer is the code reference — §5) and the clothes refitted.
- **Sculpting starting points** (item 28): Blender Studio's Human Base Meshes (17 meshes — full figures, heads, hands,
  feet, jaws, eyeballs, realistic and stylised) ship in the starter library for one-off characters and creatures that
  don't need sliders ([`project-files.md`](project-files.md) §2).

### 1.2 Shape spaces

A **shape space** is a set of shape keys on the level-0 body plus how sliders weight them. Three ship (R4), **all in
MakeHuman's own target format** (item 3): each shape is a `.target.gz` file — "a morph target (shape key) for the
MakeHuman base mesh … Only vertices that differ from the base mesh are included" ([`target.md`](https://github.com/makehumancommunity/mpfb2/blob/master/docs/fileformats/target.md)).

| Space | Source | Shapes | Licence | Role |
|---|---|---|---|---|
| `makehuman` | MPFB2's 1,258 targets (macro: gender, age, muscle, weight, height, proportions; plus region detail) | the targets as shipped; MakeHuman's macro blending from `macro.json` | CC0 | range: infant to elder, all body types |
| `mhr` | Meta's MHR identity space (45 parameters, trained on 7,110 body scans), wrapped onto hm08 through SOMA-X's MHR↔Anny bridge (Anny outputs the MakeHuman topology) | one target per identity component; MHR's neural pose correctives are not part of identity | Apache-2.0 | scan-realistic bodies |
| `gnm` | Google's GNM head: 253 identity components (170 head, 3 eyeball, 80 teeth) | one target per component on the head region and the eye and teeth parts (`.ptarget.gz` for parts) | Apache-2.0 | scan-realistic heads, eyes and teeth |

Rules: a wrap is computed **offline** (deformation transfer, the standard technique — §8 S9) and shipped as targets
under `data/targets/<space>/`, versioned with the base. The wrap's error (max and mean distance in mm) is recorded — a
gate input (R3).

### 1.3 Morphs and sliders

- A **morph** is a relative shape key on a level-0 mesh ([Shape Keys](https://docs.blender.org/manual/en/5.3/animation/shape_keys/index.html)),
  loaded from a target file; names are `<space>.<name>` (`makehuman.nose-width-incr`, `gnm.identity.017`,
  `user.jaw-square`). Shape keys with the same name on the body and its parts move together.
- **Slider definitions are app data, not character data** (item 3): MakeHuman's `data/targets/target.json` (23 groups,
  234 slider categories, each with `label`, `targets`, `has_left_and_right`, `opposites`) and
  `data/targets/macrodetails/macro.json` (macro targets and their combinations), the format extended with groups for the
  `mhr`, `gnm` and `user` spaces ([target metadata](https://github.com/makehumancommunity/mpfb2/blob/master/docs/fileformats/target_metadata.md)).
  The UI's anatomy groups, favourites, search and mirror pairs follow CC5's observable UI (§2) on those definitions.
- **A character stores only its slider values** — `juststage:sliderIds` / `juststage:sliderValues` in the package, the
  `PropertyGroup` in the `.blend`, MakeHuman's MHM `modifier` lines on MHM export
  ([`mhm.md`](https://github.com/makehumancommunity/mpfb2/blob/master/docs/fileformats/mhm.md)); the resulting live
  weights go out as `UsdSkelAnimation.blendShapeWeights`, as USD defines.
- **Custom morphs:** sculpt on level 0 → "Save as slider" (R7) writes a target file and a `target.json` entry in the
  `user` space; or from an OBJ with the base's vertex count (CC5's Morph Slider Editor, Daz's Morph Loader Pro — §2, S9).
- **Baking:** "Bake sliders into the base" collapses shape keys into the basis; the character keeps the list baked.

### 1.4 HD detail

CC5's HD morphs activate at higher subdivision levels and each level loads its own normal and displacement maps (§2).
JustStage's equivalent:

- **Sculpted detail** lives in the Multires modifier's per-level displacement (Blender's own storage).
- **Authored or generated detail** lives in **displacement maps** (`displacement` channel, OpenEXR 32-bit float, UDIM,
  per level — §3.1).
- An **HD slider** has one tangent-space displacement map (EXR, UDIM, authored at level 2, lower levels filtered from
  it), which the slider fades in — in the material's displacement input (EEVEE's "Displacement and Bump", true
  displacement in Cycles — §8). Its low-frequency part is an ordinary level-0 target in the same slider. Blender's
  multires can't hold sliders above level 0 (Daz-to-Blender users' finding — §8), and the existing Blender practice for
  Daz's HD morphs is the same map-per-morph (`edolstra/dhdm`, GPL-3.0, a strength per morph — §8).
- **Export bakes** the faded result into one displacement map per level for programs that read displacement, and into
  normal maps for Unreal and game engines (CC5's per-level normal and displacement maps, §2); Blender's MaterialX export
  doesn't carry displacement (§8).
- **Expression wrinkles** are not HD sliders: they are the DNA's animated maps, blended by the face rig (RigLogic's
  `animatedmaps`, OpenRigLogic — §8), built in step 4.
- **NOT STANDARD (N3) — APPROVED 2026-10-29** ("your rec on all 1-6 … go", TASKS): only the live fade by the slider is
  ours; the maps are the standard carrier. Trade-off: texture memory per active HD slider on the 8 GB card — measured at
  the gate; baking when the slider is released keeps one map live.

## 2 · Rig, face rig and correctives

Defined in [`skeleton-and-face.md`](skeleton-and-face.md). In the data model:

| Piece | In the `.blend` | In the package | Standard |
|---|---|---|---|
| Skeleton | one Armature, deform bones in a `DEF` bone collection, the UE5 skeleton's own names; placed from the joint cubes (MPFB2's `CUBE` strategy) as sliders change the body | `UsdSkelSkeleton` + `UsdSkelBindingAPI` on each skinned mesh | UsdSkel; MPFB2's rig JSON v110 ([`rig.md`](https://github.com/makehumancommunity/mpfb2/blob/master/docs/fileformats/rig.md)) |
| Skin weights | vertex groups named after bones, from MPFB2's `weights.game_engine.json` extended for UE5's added bones; max 8 influences on the body; export caps to 4 where a target needs it | `primvars:skel:jointIndices/jointWeights` | UsdSkel |
| Face rig | `rig/face.dna` evaluated by OpenRigLogic's Python bindings; its outputs drive shape keys, face bones and the animated wrinkle maps; the ARKit 52 shapes exist as plain shape keys too | `rig/face.dna` (`juststage:faceRig`) | Epic's DNA, OpenRigLogic (MIT) |
| Body correctives | `rig/body.dna`: RigLogic's RBF and twist-swing layers (the shapes they turn on are shape keys; the joints they move are corrective bones), evaluated by OpenRigLogic in Blender — never hand-made drivers | `rig/body.dna` (`juststage:bodyRig`) | Epic's DNA (item 1; N5 replaced) |

## 3 · Materials and texture sets

### 3.1 The master texture set

One master set per character; every target (CC5's tiles, MetaHuman's override slots, glTF, Unreal materials) is a
**bake from the master**, never a second authored set (S10 §5).

**UV layout and tiles.** The body shares one UDIM layout, CC5-compatible in tile assignment (§2 pass 2):

| Tile | Region | Max resolution |
|---|---|---|
| 1001 | head and neck | 8192 |
| 1002 | torso | 8192 |
| 1003 | arms and hands | 8192 |
| 1004 | legs and feet | 8192 |
| 1005 | nails | 2048 |
| 1006 | eyelash cards | 2048 |

Parts have their own 0–1 UVs and materials (`eye.L/R`, `cornea.L/R`, `occlusion.L/R`, `tearline.L/R`, `teeth_upper`,
`teeth_lower`, `tongue`). The layout is JustStage's own unwrap of hm08 (MPFB2 ships 14 alternative UV layers — §5 —
the gate picks one or ours); only the tile *assignment* follows CC5's public layout. Standard:
[UDIM](https://docs.blender.org/manual/en/5.3/modeling/meshes/uv/workflows/udims.html).

**Channels** (file naming `<character>.<channel>.<tile>.<ext>`; sRGB for colour, Non-Color for data, linear EXR for
float — Blender's OpenColorIO config):

| Channel | Format | Notes |
|---|---|---|
| `base_color` | PNG/WebP 8-bit sRGB (TIFF 16-bit master) | albedo without lighting |
| `normal` | 16-bit, tangent space, OpenGL +Y (glTF's convention) | export flips Y for DirectX targets |
| `roughness` | 8-bit linear | |
| `specular` | 8-bit linear (F0 scalar) | MetaHuman packs S/R/M/F; CC5 separates — both baked from this |
| `cavity` | 8-bit linear | micro-occlusion |
| `scatter` | 8-bit linear | subsurface weight mask |
| `displacement` | EXR 32-bit float, per level 1 and 2 | HD detail (§1.4) |
| `micro_normal` | 16-bit tileable + tiling scalar | CC5 defaults: body 42, face 20 (§7 S10) |
| `wrinkle.<i>.normal`, `wrinkle.<i>.color`, `wrinkle.<i>.mask` | 16-bit / 8-bit | the DNA's animated maps (§1.4) |
| `redness` | 8-bit linear | blood-flow mask for expression redness |
| `makeup.<layer>` | 8-bit sRGB + alpha | SkinGen-style layers kept separately, toggled and re-baked |

Eye, teeth and tongue channels: `base_color`, `normal`, `roughness`, `scatter`. Hair cards: `base_color` (with
alpha), `normal`, `flow`, `id`, `root`, 2048 max.

**Resolution budget (the 8 GB rule):** 8K masters live on disk; the viewport never loads them whole. One 8K RGBA
8-bit tile is 268 MB uncompressed; six tiles of five channels at 8K is about 8 GB — the whole card. So the working
resolution is 2K per tile by default (≈ 0.5 GB for the body) and 4K on request; 8K is used by Cycles and by final
bakes. MetaHuman itself ships 2K "UE Optimized" and bakes "up to 8K" for Cine (S10 §4a). The gate measures VRAM at 2K,
4K and 8K ([`quality-gate.md`](quality-gate.md) §4).

**Generation and provenance:** every generated texture records its generator preset, model, seed and prompt in the
`juststage` `customData` of its texture-reader prim (§6); every imported texture its origin and licence label. A
texture with no record is a build error ([`testing.md`](testing.md)).

### 3.2 Material model (item 4)

- **In Blender** materials are built on Principled BSDF and Principled Hair BSDF — skin with Random Walk subsurface,
  coat, sheen for vellus fuzz, micro normal and the wrinkle maps; eyes with a transmissive cornea. Principled BSDF is
  based on OpenPBR, so these map onto it directly. Standard: [Principled BSDF](https://docs.blender.org/manual/en/5.3/render/shader_nodes/shader/principled.html),
  [Principled Hair BSDF](https://docs.blender.org/manual/en/5.3/render/shader_nodes/shader/hair_principled.html).
- **In USD** each material is written by **Blender's own USD exporter**: `UsdPreviewSurface` (every reader) plus a
  MaterialX network — the Principled BSDF's MaterialX export creates `open_pbr_surface` (OpenPBR Surface) on MaterialX
  newer than 1.38, and Blender 5.3 builds against MaterialX 1.39.4 (§8); OpenPBR covers subsurface (colour, radius,
  scale, anisotropy), coat, fuzz, specular and transmission. Hair uses MaterialX's `chiang_hair_bsdf` with
  `deon_hair_absorption_from_melanin` (melanin-based colour — §8). Unreal 5.8 imports MaterialX OpenPBR (§8, S9); the
  Unreal plugin maps the OpenPBR values onto its own skin, eye and hair materials. **No `juststage` render context.**
- **Generator inputs** (melanin, haemoglobin, age, pores, iris pattern seed, …) belong to the generator preset that
  made the textures (recorded in provenance), not to the material.
- **Test items for the gate** (the attack on this choice): how much of Principled's subsurface and coat survives
  Blender's MaterialX export, and whether OpenPBR → Unreal reaches the bar ([`quality-gate.md`](quality-gate.md)).
- **glTF:** PBR metallic-roughness with `KHR_materials_specular`, `KHR_materials_sheen` (cloth) and
  `KHR_materials_ior`. Standard: [MaterialX](https://materialx.org/), [OpenPBR](https://academysoftwarefoundation.github.io/OpenPBR/),
  [glTF 2.0](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html).

## 4 · Hair (item 5)

- **Storage:** Blender Curves objects attached to the body or a part ([Curves](https://docs.blender.org/manual/en/5.3/modeling/curves/index.html)).
- **Generation:** Blender's own hair node groups, shipped in `datafiles/assets/nodes/procedural_hair_node_assets.blend`
  (on disk in 5.3; the manual's Hair Nodes: Deformation, Generation, Guides, Read, Utility, Write — Generate,
  Interpolate and Duplicate Hair Curves; Clump, Curl, Braid; Frizz, Noise, Roll, Rotate, Shrinkwrap, Smooth, Straighten,
  Trim, …) as modifiers on the Curves object. **A groom's settings are those node groups' inputs**, saved in the
  `.blend` and the library asset — no groom schema of ours.
- **Styles:** MakeHuman's CC0 hair-editor pack (`hair/haireditor/hair.blend`, by Tomáš Klecer) — the 16 styles MPFB2's
  hair editor lists (scalp, eyebrows, beards, moustaches, eyelashes) — attached as MPFB2 attaches them: the body as the
  Curves surface, an identity parent; each style carries its own copies of Blender's hair node groups, Surface Deform
  (Deform Curves on Surface) first, which follows the body's shape keys through Blender's rest position.
- **Groom types:** `scalp`, `eyebrows`, `eyelashes`, `beard`, `mustache`, `body`, `vellus` — MetaHuman's public groom
  types plus body hair (S10 §4a), a property of the Curves object.
- **Per-curve attributes** named after Unreal's groom schema so export is a copy: `groom_root_uv`, `groom_guide`,
  `groom_group_id`, `groom_id`, `groom_color`, `groom_width` (metres inside, cm on export), plus `melanin`, `redness`.
- **Simulation:** Blender's hair simulation nodes now; Jolt strand hair when it ships inside the extension (R5).
- **LOD:** strands → cards (`hair.bake_cards`) → mesh.
- **Interchange:** USD `UsdGeomBasisCurves` with Epic's `GroomAPI` and the `groom_*` primvars (the baked curves —
  generator settings don't travel, as in studios: S10); Alembic at `groom_version 1.5` for Unreal — Blender 5.3 exports
  "Arbitrary attributes on meshes, curves, and pointclouds" to Alembic (§8), so no exporter of ours; cards for CC5 and
  glTF ([`interchange.md`](interchange.md) §4). Standard: [BasisCurves](https://openusd.org/release/api/class_usd_geom_basis_curves.html),
  [Alembic for grooms](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-alembic-for-grooms-in-unreal-engine).

## 5 · Clothes (item 3)

- **The fit format is MakeHuman's MHCLO** ([`mhclo.md`](https://github.com/makehumancommunity/mpfb2/blob/master/docs/fileformats/mhclo.md)):
  per garment vertex either an exact base vertex or three base vertices with three weights and an x/y/z offset;
  `z_depth` (layer order); `delete_verts` (body faces hidden when worn); `x/y/z_scale` references; author, licence and
  description header lines — the format MakeHuman uses for "clothes … hair and eyes". Garments fit to the helper
  geometry (§1.1), which is why the helpers stay.
- **Refit** when the body changes: MHCLO's binding, with LoBoFit (BSD-3, a pending-patent notice — §7) on top where the
  binding isn't enough (R8).
- **In the package** a garment is a Mesh with `juststage:layer`, `juststage:tuckUnder` (a relationship to the garments it
  goes under), `juststage:fit` (its `.mhclo`, in `garments/`) and `juststage:cloth:*` (§0); the body faces hidden under
  it are a `UsdGeomSubset` (family `juststage:hide`, element type face) — USD's standard carrier for a set of faces; in
  Blender a boolean face attribute `hide.<garment>`. MHCLO lacks tuck-under relations and cloth settings — the two
  fields that are ours.
- **Skin weights** come from the body by transfer (Robust Skin Weights Transfer, MIT — S9 §3) unless authored.
- **Simulation:** Blender's Cloth modifier in the app ([Cloth](https://docs.blender.org/manual/en/5.3/physics/cloth/index.html));
  the cloth settings map to Unreal's Chaos cloth where they can, through the plugin.
- **Making from patterns** (R8, step 8) comes later ([`animation-and-later-features.md`](animation-and-later-features.md) §2).

## 6 · Identity, versioning and provenance

- **Identity:** USD's `assetInfo.identifier` on `/Character` is the character's id — a UUID v4 (RFC 9562) that never
  changes across edits, exports and re-imports; the Unreal plugin's keep-animation rule keys on it
  ([`import-export.md`](import-export.md) §5.3). `assetInfo.name` and `assetInfo.version` are the display name and the
  character's own version.
- **Versions:** `juststage:formatVersion` versions the attribute set of §0; the `PropertyGroup`s carry
  `schema_version`; migrations are ordered Python steps (`juststage/migrations/`) run on `load_post` and on package
  import — Blender's versioning-code pattern (§8). A file whose `formatVersion` is newer than the app knows is refused
  with the needed version named (Blender's "minimum reader" rule, §8). The DNA files carry their own versions.
- **Plugin and later-feature data** goes in attributes under the plugin's own namespace (`<plugin id>:`) or in
  `customData` under a reverse-DNS key — both preserved by every USD reader and by JustStage's load and save
  (protobuf's rule, §8).
- **Provenance** is the `juststage` `customData` key on the prim it describes — `{origin, licence, url, tool, model,
  seed, date}` on each imported or generated mesh, texture reader, groom and garment (VRM's in-file licence fields,
  §8). The export commands write it; the importers create it. Licences are labels, never filters
  ([`README.md`](README.md) §4).
