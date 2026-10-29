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
| **The character package** (a folder: `character.usda` root layer, binary `.usdc` side layers, `textures/`, `grooms/`, `rig/`, `character.juststage.json`) | the portable character: export, import, the Unreal plugin, JustDirect, archives | OpenUSD with UsdSkel, UsdShade, UsdGeomBasisCurves, plus JustStage applied API schemas; companions for what USD lacks (R17, §8) | [UsdSkel](https://openusd.org/release/api/_usd_skel__intro.html), [UsdShade](https://openusd.org/release/api/usd_shade_page_front.html) |
| **The character JSON** (`character.juststage.json`, one JSON Schema 2020-12) | everything USD has no schema for: slider definitions, shape-space maps, correctives, wrinkle layers, groom settings, garment fit data, provenance and licence; also the source of the `PropertyGroup` classes | JSON Schema 2020-12 (the schema language MCP tools use too, §8) | [json-schema.org](https://json-schema.org/draft/2020-12) |

The `PropertyGroup` classes are **generated at registration from the JSON Schema** (one source; `bpy.props` fields per
schema property), so the `.blend` form and the JSON form never drift. Mesh, shape-key, bone, curve, image and material
data stay in Blender's own blocks and in USD; the JSON carries references by name, never geometry.

**NOT STANDARD — the character JSON schema itself.** No open standard carries correctives, slider definitions,
wrinkle layers or garment fit data (§8: UsdSkel has none; the AOUSD character group may not publish normative schemas
before 2027; no app's USD carries correctives). Standard option: USD only — loses correctives today (S9). Trade-off:
one schema of our own to maintain and version, against losing the data that makes a CC5-class character a character.
Where a standard appears (AOUSD CMI, OpenExec rigs), the JSON field moves into a USD schema and the JSON field is
deprecated with a migration.

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
  with its own method (R8) and rigs with its own skeleton (§2 of this doc). A fixed index map
  (`data/base/hm08-index-map.json`, 19,158 → 13,380 + parts) lets the importer read MakeHuman targets, `.mhclo` clothes
  and MPFB2 rigs. **NOT STANDARD** against MakeHuman's convention of keeping helpers: the standard option is to ship
  hm08 whole; the trade-off is 5,778 dead vertices in every character and every morph for a fitting system we don't
  use. Waits for the user's word.
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
"morph transfer"), checked in as data (`data/spaces/<space>/`), and versioned with the base. The wrap's error is
measured and recorded (max and mean vertex distance in mm) — a gate input (R3). Sliders over a space are ordinary
sliders (§1.3) whose `shape_keys` list the space's keys.

### 1.3 Morphs and sliders

- A **morph** is a relative shape key on a level-0 mesh (Blender's own: [Shape Keys](https://docs.blender.org/manual/en/latest/animation/shape_keys/index.html)).
  Names are `<space>.<name>` (e.g. `makehuman.nose-width-incr`, `gnm.identity.017`, `user.jaw-square`). Shape keys on
  the body and on parts with the same name move together.
- A **slider** is a JSON record (schema `slider`) the UI shows:
  `id`, `label`, `group` (an anatomy path such as `head/nose`), `type` (`macro`, `detail`, `scan`, `hd`, `expression`,
  `corrective`), `min`, `max` (default −1..1; the UI may extrapolate to the Blender shape-key limit, −10..10),
  `default`, `mirror` (the paired slider id), `shape_keys` (list of `{name, weight}` or a named function for non-linear
  maps), `hd` (optional: displacement deltas per level, §1.4), `source` (`{origin, licence, url}`).
  Standard: the slider record follows CC5's observable grouping (anatomy groups, favourites, search, mirror pairs —
  §2) and Blender's shape-key value model; the record format is ours (covered by the character JSON's NOT STANDARD
  mark).
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
- An **HD morph** is a slider whose `hd` field names displacement-delta EXR tiles per level; the slider weight blends
  them (shader-side in EEVEE through the material's displacement input, true displacement in Cycles). Its
  low-frequency part is an ordinary level-0 shape key in the same slider.
  **NOT STANDARD** — no open app defines HD morphs; the standard option is sculpt layers only (Blender's multires,
  no slider); trade-off: a blend of displacement maps costs texture memory per active HD slider and must be baked
  before export (a bake step exists anyway for every target). Waits for the user's word.

## 2 · Rig, face rig and correctives

Defined in [`skeleton-and-face.md`](skeleton-and-face.md). In the data model they are:

| Piece | Storage in `.blend` | Storage in the package | Standard |
|---|---|---|---|
| Skeleton | one Armature, deform bones in a `DEF` bone collection, Blender `.L`/`.R` names | `UsdSkelSkeleton` + `UsdSkelBindingAPI` on each skinned mesh | [Armatures](https://docs.blender.org/manual/en/latest/animation/armatures/index.html), UsdSkel |
| Skin weights | vertex groups named after bones; max 8 influences per vertex on the body (MetaHuman LOD0 uses 12 on the head, 8 on the body — §8 pass 2); export presets cap to 4 where a target needs it | `primvars:skel:jointIndices/jointWeights` | UsdSkel |
| Face rig | a DNA file (`rig/face.dna`) evaluated by OpenRigLogic; its outputs drive shape keys, face bones and wrinkle layers; the ARKit 52 shapes exist as plain shape keys too | `rig/face.dna` + the JSON's `face` section | OpenRigLogic (MIT) — [repo](https://github.com/EpicGames/OpenRigLogic) |
| Body correctives | drivers on shape keys and on corrective bones, generated from the JSON's `correctives` list; never hand-made drivers | JSON `correctives` (schema in [`skeleton-and-face.md`](skeleton-and-face.md) §3) | ours (NOT STANDARD, see that doc) |

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

**Generation and provenance:** every generated texture records its generator, model, seed and prompt in the JSON
`provenance` list; every imported texture records its origin and licence label. A texture with no record is a build
error (the test in [`testing.md`](testing.md)).

### 3.2 Material model

- In Blender: one node group per material kind — `JustStage Skin`, `JustStage Eye`, `JustStage Cornea`,
  `JustStage Occlusion`, `JustStage Tearline`, `JustStage Teeth`, `JustStage Tongue`, `JustStage Hair`,
  `JustStage Cloth` — built on Principled BSDF (skin: subsurface Random Walk, dual specular through a second
  coat/layer, micro normal, wrinkle layers) and Principled Hair BSDF (melanin model — §7 S10). Standard: Blender's
  shader nodes ([Principled BSDF](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html),
  [Principled Hair BSDF](https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/hair_principled.html)).
- **Parameters** (the JSON `materials` section) are the inputs of those groups: skin tone (melanin, haemoglobin,
  the physically based layers of R5), roughness scale, specular scale, SSS radius and scale, micro-normal tiling and
  strength, wrinkle layer weights; eye: iris pattern seed, iris colours, limbal ring size/softness/colour, pupil size,
  cornea bulge, sclera tint and vascularity, wetness (MetaHuman's public eye-tool list is the behaviour reference —
  S10 §4a); teeth: plaque, gum colour; hair: melanin, redness, tint, roughness, random colour.
- Interchange: USD `UsdPreviewSurface` always, plus MaterialX OpenPBR Surface for USD and Unreal (Unreal imports
  MaterialX OpenPBR — S9 §4); glTF PBR metallic-roughness with `KHR_materials_specular`, `KHR_materials_sheen`
  (cloth) and `KHR_materials_ior`; the skin, eye and hair parameters travel in the JSON and are rebuilt by the Unreal
  plugin on Unreal's shaders ([`import-export.md`](import-export.md) §5). Standard: [MaterialX](https://materialx.org/),
  [glTF 2.0](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html).

## 4 · Hair

- **Storage:** Blender Curves (hair curves) objects attached to the body or a part (Blender's own:
  [Curves](https://docs.blender.org/manual/en/latest/modeling/curves/index.html), grooming with Curves Sculpt).
- **Groom types** (`groom.type`): `scalp`, `eyebrows`, `eyelashes`, `beard`, `mustache`, `body`, `vellus` — MetaHuman's
  public groom types plus body hair (S10 §4a).
- **Per-curve attributes** (named after Unreal's groom schema so export is a copy, not a mapping — §8 pass 2):
  `groom_root_uv` (float2), `groom_guide` (bool), `groom_group_id` (int), `groom_id` (int), `groom_color` (float3),
  `groom_width` (float, per point; metres internally, cm on export), plus JustStage's `melanin`, `redness`, `clump_id`.
- **Per-groom settings** (JSON `grooms[]`): type, binding surface and UV set, generator parameters (guide count,
  interpolation, clumping, noise, length maps), simulation settings (Jolt strand hair when it ships inside the
  extension; Blender's hair simulation nodes meanwhile), LOD policy (`strands` → `cards` → `mesh`, with the card bake's
  outputs and card count), licence and provenance.
- **Interchange:** USD `UsdGeomBasisCurves` with Epic's `GroomAPI` applied and the `groom_*` primvars; Alembic with
  the `groom_*` attributes at `groom_version 1.5` for Unreal's reliable path; card meshes for CC5 and glTF
  ([`interchange.md`](interchange.md) §4). Standard: [BasisCurves](https://openusd.org/release/api/class_usd_geom_basis_curves.html),
  [Alembic for grooms](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-alembic-for-grooms-in-unreal-engine).

## 5 · Clothes

- A **garment** is a Mesh object with a `juststage.garment` group: `layer` (integer draw/tuck order, outermost
  highest — MPFB2's `z_depth` pattern, §5), `kind` (free text tag), `fit` (§5.1), `hide_mask` (the body faces hidden
  under it: a boolean face attribute on the body named `hide.<garment>`), `weights` (`transferred` | `authored`),
  `sim` (a subset of Blender's Cloth modifier settings: mass, stiffness, damping, collision distance, pinning group),
  `tuck` (list of garment ids this one goes under), `materials`, `provenance`.
- **5.1 Fit data (R8):** per garment vertex, a binding to the base body in the rest pose: `triangle` index,
  barycentric weights and signed `offset` along the body normal, recorded against `base_version`. When the body's
  shape changes (sliders, scan spaces, imports), the garment refits from the binding (LoBoFit's method, BSD-3 with a
  pending-patent notice — §7 pass 2; the method is an implementation detail behind the binding record). Standard
  for the *behaviour*: CC5's conform model (conform, layers, tuck-in, hide-under, weight transfer — §2); Blender's
  Surface Deform is the behaviour reference for binding (§8 S9).
- **Skin weights** come from the body by transfer (Robust Skin Weights Transfer, MIT — S9 §3) unless authored.
- **Simulation:** Blender's Cloth modifier in the app (standard: [Cloth](https://docs.blender.org/manual/en/latest/physics/cloth/index.html));
  the garment's `sim` record is what gets exported to Unreal's Chaos cloth config by the plugin where it maps.
- **Making from patterns** (R8, step 8) adds `pattern` (2D pieces, seams) to the garment record later: the field is
  reserved now ([`animation-and-later-features.md`](animation-and-later-features.md) §2).

## 6 · Identity, versioning and provenance

- Every character has a `character_id` (UUID v4) that never changes across edits, exports and re-imports; the Unreal
  plugin's keep-animation rule keys on it ([`import-export.md`](import-export.md) §5.3). Standard: UUID (RFC 9562).
- `schema_version` (integer) on the JSON and on every `juststage` PropertyGroup; migrations are ordered Python steps
  (`juststage/migrations/`) run on load and on package import — Blender's versioning-code pattern (§8). A file with a
  newer `schema_version` than the app knows is refused with the version named ("minimum reader", Blender's rule, §8).
- Unknown JSON fields are preserved on save (protobuf's rule, §8) in `extensions`, keyed by a reverse-DNS namespace
  (`org.juststage.fx`, `com.example.plugin`), so plugins and later features store data without a schema change
  ([`animation-and-later-features.md`](animation-and-later-features.md) §3).
- `provenance`: a list of `{what, origin, licence, url, tool, model, seed, date}` records — one per imported or
  generated asset (VRM's in-file licence pattern, §8). The export commands copy it into the package; the importers
  create it. Licences are labels, never filters ([`README.md`](README.md) §4).
