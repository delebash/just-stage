# The character data model

> **Status: DRAFT, 2026-10-29 — for the user's approval. Nothing here is in force until TASKS.md records the approval
> verbatim.** Part of the standards spec ([`README.md`](README.md)). Facts come from
> [`../dev/RESEARCH.md`](../dev/RESEARCH.md) (§ numbers below) and the approved recs
> ([`../plans/2026-10-29-recs.md`](../plans/2026-10-29-recs.md), R numbers). Each piece names the standard it
> follows, or is marked **NOT STANDARD** with the standard option and the trade-off; a NOT STANDARD piece waits for the
> user's word on it by name.

## 0 · Where the data lives

A JustStage character exists in three forms, each with one job (the kit rule "one way per job", [`README.md`](README.md) §3):

| Form | Job | Standard | Link |
|---|---|---|---|
| **Blender data-blocks in a `.blend`** | the live, editable character while the user works, and the asset-library copy | Blender's own data model: Mesh, Shape Keys, Armature, Curves (hair), Material, Image; JustStage's own fields as a registered `PropertyGroup` named `juststage` on each data-block | [bpy.types.PropertyGroup](https://docs.blender.org/api/current/bpy.types.PropertyGroup.html), [Asset libraries](https://docs.blender.org/manual/en/latest/files/asset_libraries/index.html) |
| **The character package** (a folder: `character.usda` root layer, binary `.usdc` side layers, `textures/`, `grooms/`, `rig/face.dna`) | the portable character: export, import, the Unreal plugin, JustDirect, archives | OpenUSD with UsdSkel, UsdShade (render contexts), UsdGeomBasisCurves, UsdGeomSubset, primvars, `assetInfo`; **JustStage applied API schemas** for what the core schemas lack (R17, §8); the DNA face rig beside it | [UsdSkel](https://openusd.org/release/api/_usd_skel__intro.html), [UsdShade](https://openusd.org/release/api/usd_shade_page_front.html), [applied API schemas](https://openusd.org/release/api/_usd__page__generating_schemas.html) |
| **The sidecar** (`<name>.juststage.json`, written only beside FBX and glTF exports) | carries the JustStage schema data into formats that cannot hold it — the pattern CC5 (FBX + JSON + `.fbxkey`), Daz (FBX + `.dtu`) and MetaHuman (FBX + `.dna`) use (S9) | generated from `schema.usda`; JSON Schema 2020-12 | — |

**One source: `schema.usda`.** JustStage's own data is defined once, as USD applied API schemas in `schema.usda`
(USD's own way to extend USD; `usdGenSchema` generates the C++/Python classes — the mechanism Epic uses for
`GroomAPI`/`GroomBindingAPI`, S9 §4). From that file the build generates the Blender `PropertyGroup` classes (`bpy.props`
fields per attribute), the sidecar's JSON Schema, and the reference docs. Blender writes and reads the schemas through
its own **USD hook API** (`bpy.types.USDHook`: `on_export` gets the `pxr` stage and prim map, `on_material_export` the
USD material, `on_import`/`on_material_import` the reverse — Blender's source `io/usd/intern/usd_hook.cc` and its docs
example, read 2026-10-29; Blender's bundled `pxr` module is what the example imports), so a JustStage character is a
single USD package any USD reader opens: the standard parts are read everywhere, the applied schemas by JustStage, the
Unreal plugin and JustDirect, and ignored (not lost) elsewhere, by USD's design.

**NOT STANDARD (N1) — the content of JustStage's applied schemas.** The *mechanism* is standard; the *fields* are ours
because no industry schema defines correctives drivers, slider definitions, groom generator settings, garment layering
or HD morphs (§8: UsdSkel "does not aim to provide general rigging and execution behaviours"; the AOUSD character
interest group cannot publish normative schemas; no app's USD carries correctives — S9). Standard option: wait for
AOUSD. Trade-off: fields of our own to version (`_N` families), against shipping characters whose joints collapse and
whose sliders have no names. When AOUSD publishes, a converter maps our families onto theirs.

Schema families (version 1): `JustStageCharacterAPI` (ids, base/skeleton/face versions), `JustStageSliderAPI` (slider
definitions), `JustStageShapeSpaceAPI` (a space's parameter map), `JustStageHDMorphAPI`, `JustStageCorrectiveAPI`
([`skeleton-and-face.md`](skeleton-and-face.md) §3), `JustStageGroomAPI`, `JustStageGarmentAPI`, `JustStageLipsyncAPI`,
`JustStageTakeAPI` ([`animation-and-later-features.md`](animation-and-later-features.md)). Materials carry their JustStage
parameters as a UsdShade network under the `juststage` render context (§3.2), provenance lives in USD's native
`assetInfo` and `customData` (§6), per-vertex data in primvars, face sets in `UsdGeomSubset`s, references between prims
as USD relationships — never as JSON blobs.

## 1 · The base human

**R4, decided:** MakeHuman's hm08 topology is subdivision level 0; two Catmull-Clark levels sit on it with displacement
on top (CC5 HD's method); three shape spaces are wrapped onto it.

### 1.1 The base mesh (`js_base_body`, version 1)

| Fact | Value | Source |
|---|---|---|
| Topology | hm08 body: all quads, "completely triangles free", poles ≤ 5 edges, made for subdivision | §5 (MakeHuman's topology page, pass 2) |
| Vertices, level 0 | hm08's `body` group, vertices 0–13,379 (13,380); the raw MakeHuman mesh with helpers and joint cubes is 19,158 | §5 |
| Faces, level 0 | 14,766 for the whole hm08 mesh; the body-only count is fixed when the base is built (step 2) and written here | §5 |
| Licence | CC0 1.0 (MPFB2's assets) — the base, the 1,258 targets, the 7 hair styles | §5 |
| Levels | 0 (edit, shape keys, skinning), 1 and 2 (Catmull-Clark through Blender's Multires modifier, which stores per-level displacement) | [Multiresolution modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/multiresolution.html) |
| Expected counts | ×4 faces per level (CC5 HD: 70,732 at SubD 1, 282,928 at SubD 2 from 17,683; ours scales the same way from the body count) | §2 |

Rules:

- **Helpers and joint cubes are not part of the shipped base.** MakeHuman's helper geometry (tights, skirt, hair,
  genital) and its 125 joint cubes exist for MakeHuman's own fitting (`.mhclo`) and rigging; JustStage fits clothes
  with its own method (R8) and rigs with the UE5 skeleton (§2 of this doc). A fixed index map
  (`data/base/hm08-index-map.json`, 19,158 → 13,380 + parts) lets the importer read MakeHuman targets, `.mhclo` clothes
  and MPFB2 rigs. Precedent: Anny, the bridge MHR reaches us through, already works on a 13,718-vertex MakeHuman mesh
  (body, eyes, tongue — §5), not the 19,158-vertex raw mesh. **NOT STANDARD (N2)** against MakeHuman's own convention of
  keeping helpers: the standard option is to ship hm08 whole; the trade-off is 5,778 dead vertices in every character
  and every morph for a fitting system we don't use. Waits for the user's word.
- **The body's topology is frozen** once the gate (R3) passes on it. Any change bumps `base_version` (integer) and
  ships a vertex map from the old base, so every morph, texture and garment made for version 1 still loads.
- **Parts** are separate meshes, each with its own base version: `eye.L`, `eye.R` (eyeball with cornea bulge),
  `cornea.L`, `cornea.R`, `occlusion.L`, `occlusion.R` (eye occlusion shell, CC5's and MetaHuman's "eye shell"),
  `tearline.L`, `tearline.R`, `teeth_upper`, `teeth_lower` (teeth with gums), `tongue`, `eyelash.L`, `eyelash.R` (card
  lashes; strand lashes are a groom). hm08's own eyes (72 vertices) and teeth (68) are too coarse for the bar, so the
  parts are JustStage's: eyes, occlusion, tearline and lashes built (R5); teeth, gums and tongue from GNM or ICT
  geometry under their licences (GNM Apache-2.0, ICT MIT — §5, §7), re-topologised to quads if needed. Part meshes
  are frozen and versioned like the body.
- **Units and axes inside Blender:** metres, Z up, −Y front (Blender's own; §8 pass 2). Interchange converts
  ([`interchange.md`](interchange.md) §1).
- **Rest pose:** A-pose (arms about 45° down), facing −Y. Reason: MetaHuman conforming required A-pose in 5.6 and takes
  A to T since 5.7 (§8), and A-pose binds keep shoulder deformation (the standards note's attack on T-pose). VRM and
  Unity need a T-pose: the export presets re-pose through the retarget pose, never the bind pose
  ([`skeleton-and-face.md`](skeleton-and-face.md) §1.4).

### 1.2 Shape spaces

A **shape space** is a set of shape keys on the level-0 body plus a map from the space's parameters to shape-key
weights. Three ship (R4):

| Space | Source | Parameters → shape keys | Licence | Role |
|---|---|---|---|---|
| `makehuman` | MPFB2's 1,258 targets (macro: gender, age, muscle, weight, height, proportions, ethnic mix; plus per-region detail targets) | one target = one shape key; MakeHuman's macro blending (its weighted combination of macro targets) reimplemented in Python/NumPy from its public behaviour | CC0 | range: infant to elder, all body types |
| `mhr` | Meta's MHR identity space (45 identity parameters, scan-trained on 7,110 bodies); wrapped onto hm08 through SOMA-X's existing MHR↔Anny bridge (Anny outputs the MakeHuman topology) | each identity component = one shape key (a linear basis), weights = the component values; MHR's neural pose correctives are *not* baked into identity | Apache-2.0 (MHR, SOMA-X, Anny) | scan-realistic bodies |
| `gnm` | Google's GNM head: 253 identity components (170 head, 3 eyeball, 80 teeth) | each component = one shape key on the head region (and on the eye and teeth parts); typical range −3..+3 | Apache-2.0 | scan-realistic heads, eyes and teeth |

Rules: a wrap is computed **offline** (deformation transfer: the space's mesh → hm08, the standard technique, §8 S9's
"morph transfer") and shipped as a **USD layer of `UsdSkelBlendShape` prims** (`data/spaces/<space>.usdc`, the standard
carrier for a shape basis), with the parameter map as `JustStageShapeSpaceAPI` attributes on the layer's root prim;
versioned with the base. The wrap's error is measured and recorded (max and mean vertex distance in mm) — a gate input
(R3). Sliders over a space are ordinary sliders (§1.3) whose `shape_keys` list the space's keys.

### 1.3 Morphs and sliders

- A **morph** is a relative shape key on a level-0 mesh (Blender's own: [Shape Keys](https://docs.blender.org/manual/en/latest/animation/shape_keys/index.html)).
  Names are `<space>.<name>` (e.g. `makehuman.nose-width-incr`, `gnm.identity.017`, `user.jaw-square`). Shape keys on
  the body and on parts with the same name move together.
- A **slider** is a prim under `/Character/Sliders/<id>` with `JustStageSliderAPI` applied: `label`, `group` (an
  anatomy path such as `head/nose`), `type` (`macro`, `detail`, `scan`, `hd`, `expression`, `corrective`), `min`,
  `max` (default −1..1; the UI may extrapolate to Blender's shape-key limit, −10..10), `default`, a `mirror`
  relationship to the paired slider, `shapeKeys` (names) and `shapeWeights` (floats, or a `curve` for non-linear maps),
  an `hd` relationship to its HD map prim (§1.4), and `assetInfo`/`customData` for origin and licence. Its **value** is a
  plain float attribute (`juststage:value`), and the live weights go out through `UsdSkelAnimation.blendShapeWeights`
  as USD defines. Standard: the grouping follows CC5's observable UI (anatomy groups, favourites, search, mirror pairs —
  §2) and Blender's shape-key value model; the definition fields are N1's.
- **Custom morphs:** sculpt on level 0 → "Save as slider" (R7) writes a shape key and a slider record; from an OBJ
  with the base's vertex count (CC5's Morph Slider Editor and Daz's Morph Loader Pro behaviour, §2, S9).
- **Baking:** "Bake sliders into the base" collapses shape keys into the basis (Blender's "Apply as Shape"/"Join as
  shapes" behaviour); the record keeps the list that was baked.

### 1.4 HD detail

CC5's HD morphs activate at higher subdivision levels and each level loads its own normal and displacement maps (§2).
JustStage's equivalent:

- **Level detail** lives in the Multires modifier's per-level displacement (Blender's own storage) for sculpted
  detail, and in **displacement maps** for authored or generated detail: `displacement` channel, OpenEXR 32-bit
  float, UDIM, one per level ([`#3`](#3--materials-and-texture-sets)).
- An **HD morph** is a slider whose `hd` relationship points at one displacement-delta map (EXR 32-bit float, UDIM
  tiles, authored at the level-2 resolution; lower levels are derived by filtering, never authored twice); the slider
  weight blends the active maps (shader-side in EEVEE through the material's displacement input, true displacement in
  Cycles). Its low-frequency part is an ordinary level-0 shape key in the same slider. The map is the industry's
  carrier for sculpted detail (ZBrush, Mari, Substance, Unreal and CC5's own per-level EXR displacement — §2).
  **NOT STANDARD (N3)** — only the *blend by slider* is ours; the alternatives are ZBrush-style layers (per-vertex
  offsets at the top level with an intensity slider), which Blender cannot key on multires without a fork, or a baked
  level-2 mesh with shape keys (214,000 offsets per slider, and no more multires sculpting). Trade-off: texture memory
  per active HD slider (measured at the gate), and a bake before export (a bake step exists anyway for every target).
  Waits for the user's word.

## 2 · Rig, face rig and correctives

Defined in [`skeleton-and-face.md`](skeleton-and-face.md). In the data model they are:

| Piece | Storage in `.blend` | Storage in the package | Standard |
|---|---|---|---|
| Skeleton | one Armature, deform bones in a `DEF` bone collection, the UE5 skeleton's own names (`thigh_l`; Blender's mirror tools accept the `_l`/`_r` suffix — its naming page, read 2026-10-29) | `UsdSkelSkeleton` + `UsdSkelBindingAPI` on each skinned mesh | [Armatures](https://docs.blender.org/manual/en/latest/animation/armatures/index.html), UsdSkel |
| Skin weights | vertex groups named after bones; max 8 influences per vertex on the body (MetaHuman LOD0 uses 12 on the head, 8 on the body — §8 pass 2); export presets cap to 4 where a target needs it | `primvars:skel:jointIndices/jointWeights` | UsdSkel |
| Face rig | a DNA file (`rig/face.dna`) evaluated by OpenRigLogic; its outputs drive shape keys, face bones and wrinkle layers; the ARKit 52 shapes exist as plain shape keys too | `rig/face.dna` + `JustStageCharacterAPI` attributes naming it and its control-vocabulary version | OpenRigLogic (MIT) — [repo](https://github.com/EpicGames/OpenRigLogic) |
| Body correctives | drivers on shape keys and on corrective bones, generated from the corrective prims; never hand-made drivers | `/Character/Rig/Correctives/<id>` prims with `JustStageCorrectiveAPI` ([`skeleton-and-face.md`](skeleton-and-face.md) §3) | N5: our fields on USD's applied-schema mechanism |

## 3 · Materials and texture sets

### 3.1 The master texture set

One master set per character; every target (CC5's tiles, MetaHuman's override slots, glTF, Unreal materials) is a
**bake from the master**, never a second authored set (S10 §5).

**UV layout and tiles.** The body shares one UDIM layout, CC5-compatible in tile assignment (§2 pass 2: U-ranges
0–1 head, 1–2 body, 2–3 arms, 3–4 legs, 4–5 nails, 5–6 eyelash):

| Tile | Region | Max resolution |
|---|---|---|
| 1001 | head and neck | 8192 |
| 1002 | torso | 8192 |
| 1003 | arms and hands | 8192 |
| 1004 | legs and feet | 8192 |
| 1005 | nails | 2048 |
| 1006 | eyelash cards | 2048 |

Parts have their own 0–1 UVs and materials: `eye.L`, `eye.R` (sclera + iris), `cornea.L/R`, `occlusion.L/R`,
`tearline.L/R`, `teeth_upper`, `teeth_lower` (gums included), `tongue` (CC5's own split: `Std_Eye`, `Std_Cornea`,
`Std_Eye_Occlusion`, `Std_Tearline`, `Std_Upper_Teeth`, `Std_Lower_Teeth`, `Std_Tongue` — §2 pass 2; GNM uses seven
tiles for the same parts — §5 pass 2). The layout is JustStage's own unwrap of hm08 (hm08's UVs are MakeHuman's
single-tile layout); only the tile *assignment* follows CC5's public layout. Standard: UDIM
([Blender UDIM](https://docs.blender.org/manual/en/latest/modeling/meshes/uv/workflows/udims.html)).

**Channels** (file naming `<character>.<channel>.<tile>.<ext>`; colour management: sRGB for colour, Non-Color for
data, linear EXR for float — Blender's OpenColorIO config):

| Channel | Format | Notes |
|---|---|---|
| `base_color` | PNG/WebP 8-bit sRGB (TIFF 16-bit master) | albedo without lighting |
| `normal` | 16-bit, tangent space, OpenGL +Y (glTF's convention) | export flips Y for DirectX targets |
| `roughness` | 8-bit linear | |
| `specular` | 8-bit linear (F0 scalar) | MetaHuman packs S/R/M/F; CC5 separates — both baked from this |
| `cavity` | 8-bit linear | micro-occlusion; CC5 "cavity", MetaHuman "cavity" |
| `scatter` | 8-bit linear | subsurface weight mask (MetaHuman "Scatter") |
| `displacement` | EXR 32-bit float, per level 1 and 2 | HD detail (§1.4) |
| `micro_normal` | 16-bit tileable + `micro_normal_tiling` scalar | CC5 defaults: body 42, face 20 (§7 S10) |
| `wrinkle.<i>.normal`, `wrinkle.<i>.color`, `wrinkle.<i>.mask` | 16-bit / 8-bit | up to 4 wrinkle layers (O3DE's skin type: up to 4 wrinkle layers — §6 pass 2), each driven by a face-rig output |
| `redness` | 8-bit linear | blood-flow mask for expression redness (CC5 ships five redness maps; MetaHuman animated colour deltas — §2, S10) |
| `makeup.<layer>` | 8-bit sRGB + alpha | SkinGen-style layers kept separately so they can be toggled and re-baked |

Eye, teeth and tongue channels: `base_color`, `normal`, `roughness`, `scatter`, plus the parameter set in §3.2.
Hair cards: `base_color` (with alpha), `normal`, `flow`, `id`, `root` (CC5's root and ID maps — §2), 2048 max.

**Resolution budget (the 8 GB rule):** 8K masters live on disk; the viewport never loads them whole. One 8K RGBA
8-bit tile is 268 MB uncompressed; six tiles of five channels at 8K is about 8 GB — the whole card. So: the master
set is stored at up to 8K; JustStage's **working resolution** is 2K per tile by default (≈ 0.5 GB for the body) and 4K
on request (Blender's *Texture Limit* preference and the file's own derived sizes); 8K is used by Cycles (out-of-core
on CPU) and by final bakes. MetaHuman itself ships 2K "UE Optimized" and bakes "up to 8K" for Cine (S10 §4a). The gate
measures VRAM at 2K, 4K and 8K on the RTX 2070 Super ([`quality-gate.md`](quality-gate.md) §4).

**Generation and provenance:** every generated texture records its generator, model, seed and prompt in USD's
`customData` on its texture-reader prim (§6); every imported texture records its origin and licence label the same
way. A texture with no record is a build error (the test in [`testing.md`](testing.md)).

### 3.2 Material model

- In Blender: one node group per material kind — `JustStage Skin`, `JustStage Eye`, `JustStage Cornea`,
  `JustStage Occlusion`, `JustStage Tearline`, `JustStage Teeth`, `JustStage Tongue`, `JustStage Hair`,
  `JustStage Cloth` — built on Principled BSDF (skin: subsurface Random Walk, dual specular through a second
  coat/layer, micro normal, wrinkle layers) and Principled Hair BSDF (melanin model — §7 S10). Standard: Blender's
  shader nodes ([Principled BSDF](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html),
  [Principled Hair BSDF](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/hair_principled.html)).
- **Parameters** are the inputs of those groups: skin tone (melanin, haemoglobin, the physically based layers of
  R5), roughness scale, specular scale, SSS radius and scale, micro-normal tiling and strength, wrinkle layer weights;
  eye: iris pattern seed, iris colours, limbal ring size/softness/colour, pupil size, cornea bulge, sclera tint and
  vascularity, wetness (MetaHuman's public eye-tool list is the behaviour reference — S10 §4a); teeth: plaque, gum
  colour; hair: melanin, redness, tint, roughness, random colour.
- **In USD** a material is one `UsdShade.Material` with three networks, USD's own multi-renderer design ("can host
  data for any number of render targets", each terminal "qualified by a token-valued renderContext" — the
  UsdShadeMaterial docs, read 2026-10-29): the universal `UsdPreviewSurface` (every reader), MaterialX OpenPBR Surface
  under the `mtlx` context (USD pipelines, Unreal — S9 §4), and JustStage's own shader network under the `juststage`
  context (`outputs:juststage:surface` → a `Shader` with `info:id = "juststage:skin"` and the parameters above as inputs).
  Blender writes the second and third through `on_material_export` and reads them back through `material_import_poll`
  / `on_material_import` (the USD hook API). The Unreal plugin rebuilds the `juststage` network on Unreal's shaders
  ([`import-export.md`](import-export.md) §5).
- glTF: PBR metallic-roughness with `KHR_materials_specular`, `KHR_materials_sheen` (cloth) and `KHR_materials_ior`;
  the skin, eye and hair parameters ride in the sidecar. Standard: [MaterialX](https://materialx.org/),
  [glTF 2.0](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html).

## 4 · Hair

- **Storage:** Blender Curves (hair curves) objects attached to the body or a part (Blender's own:
  [Curves](https://docs.blender.org/manual/en/latest/modeling/curves/index.html), grooming with Curves Sculpt).
- **Groom types** (`groom.type`): `scalp`, `eyebrows`, `eyelashes`, `beard`, `mustache`, `body`, `vellus` — MetaHuman's
  public groom types plus body hair (S10 §4a).
- **Per-curve attributes** (named after Unreal's groom schema so export is a copy, not a mapping — §8 pass 2):
  `groom_root_uv` (float2), `groom_guide` (bool), `groom_group_id` (int), `groom_id` (int), `groom_color` (float3),
  `groom_width` (float, per point; metres internally, cm on export), plus JustStage's `melanin`, `redness`, `clump_id`.
- **Per-groom settings** (`JustStageGroomAPI` on the curves prim): type, a binding relationship to the surface mesh and
  its UV set, generator parameters (guide count, interpolation, clumping, noise, length maps), simulation settings
  (Jolt strand hair when it ships inside the extension; Blender's hair simulation nodes meanwhile), LOD policy
  (`strands` → `cards` → `mesh`, with the card bake's outputs and card count); licence and provenance in `customData`.
- **Interchange:** USD `UsdGeomBasisCurves` with Epic's `GroomAPI` applied and the `groom_*` primvars; Alembic with
  the `groom_*` attributes at `groom_version 1.5` for Unreal's reliable path; card meshes for CC5 and glTF
  ([`interchange.md`](interchange.md) §4). Standard: [BasisCurves](https://openusd.org/release/api/class_usd_geom_basis_curves.html),
  [Alembic for grooms](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-alembic-for-grooms-in-unreal-engine).

## 5 · Clothes

- A **garment** is a Mesh with `JustStageGarmentAPI` applied: `layer` (integer draw/tuck order, outermost highest —
  MPFB2's `z_depth` pattern, §5), `kind` (free text tag), the fit primvars (§5.1), `weights` (`transferred` |
  `authored`), `sim` (a subset of Blender's Cloth modifier settings: mass, stiffness, damping, collision distance,
  pinning group), a `tuckUnder` **relationship** to the garments it goes under, and `customData` provenance. The body
  faces hidden under it are a **`UsdGeomSubset`** on the body mesh (family `juststage:hide`, element type face; in
  Blender a boolean face attribute `hide.<garment>`) — USD's standard carrier for a set of faces.
- **5.1 Fit data (R8):** per garment vertex, a binding to the base body in the rest pose, stored as **primvars**
  (vertex interpolation, USD's carrier for per-vertex data): `primvars:juststage:fitTriangle` (int), `fitBary`
  (float3), `fitOffset` (float, signed along the body normal), recorded against `baseVersion`. When the body's shape
  changes (sliders, scan spaces, imports), the garment refits from the binding (LoBoFit's method, BSD-3 with a
  pending-patent notice — §7 pass 2; the method is an implementation detail behind the primvars). Standard for the
  *behaviour*: CC5's conform model (conform, layers, tuck-in, hide-under, weight transfer — §2); Blender's Surface
  Deform is the behaviour reference for binding (§8 S9).
- **Skin weights** come from the body by transfer (Robust Skin Weights Transfer, MIT — S9 §3) unless authored.
- **Simulation:** Blender's Cloth modifier in the app (standard: [Cloth](https://docs.blender.org/manual/en/latest/physics/cloth/index.html));
  the garment's `sim` record is what gets exported to Unreal's Chaos cloth config by the plugin where it maps.
- **Making from patterns** (R8, step 8) adds a `JustStagePatternAPI` (2D pieces, seams) later; the family name is
  reserved now ([`animation-and-later-features.md`](animation-and-later-features.md) §2).

## 6 · Identity, versioning and provenance

- Every character has a `characterId` (UUID v4, `JustStageCharacterAPI`) that never changes across edits, exports and
  re-imports; the Unreal plugin's keep-animation rule keys on it ([`import-export.md`](import-export.md) §5.3).
  Standard: UUID (RFC 9562).
- **Versions:** USD schema families carry theirs in the name (`JustStageSliderAPI_1` → `_2`; version 0 has no suffix —
  USD's rule, §8); the generated `PropertyGroup`s carry `schema_version`; migrations are ordered Python steps
  (`juststage/migrations/`) run on `load_post` and on package import — Blender's versioning-code pattern (§8). A file
  with a newer family than the app knows is refused with the version named ("minimum reader", Blender's rule, §8).
- **Plugin and later-feature data** is the plugin's own applied schema (its `schema.usda`, its family names) or, for
  small records, `customData` under a reverse-DNS key (`org.juststage.fx`, `com.example.plugin`) — both preserved by
  every USD reader and by JustStage's own load/save (protobuf's rule, §8) ([`animation-and-later-features.md`](animation-and-later-features.md) §3).
- **Provenance** is USD's native metadata: `assetInfo` on the character prim (`name`, `version`, `identifier`) and
  `customData["juststage"]` on the prim it describes — `{origin, licence, url, tool, model, seed, date}` on each
  imported or generated mesh, texture reader, groom and garment (VRM's in-file licence pattern for the fields, §8).
  The export commands write it; the importers create it. Licences are labels, never filters
  ([`README.md`](README.md) §4).
