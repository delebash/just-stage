# Research 08 — Standards JustStage builds on (2026-10-29)

Research notes for the later standards spec: scene and data model, skeleton, face, command and API layer,
plugin contract, file format and versioning, asset library, target-engine import rules, and importing
existing characters. Clean-room: public specs, docs and behaviour only.

**How to read this.** Each fact is marked **page read** (I fetched the page and read the cited text) or
**search snippet only** (a search-result summary; the page was not opened). The "date" is the date on the
page. Where a page has no date, the doc version it belongs to is given (for example "Unreal 5.8 docs").
Facts and judgement are kept apart: every topic ends with an **Assessment** (my judgement), and each
assessment carries one **Attack** line saying what arguing against it changed.

**Scope change from the user (2026-10-29), applied here:** "omnivers is out it only works on nvidia cards
we dont want restricsions anything that is commercial cost money we dont want either". NVIDIA Omniverse
(Kit commands, extensions, Nucleus) is left out of every comparison. Paid or proprietary apps (Maya,
Houdini, Unreal, Cinema 4D, CC5, Daz) appear only as short references. Open specs and open apps get
the depth.

**Access limits during this session.** docs.blender.org, developer.blender.org and projects.blender.org
refused scripted access (HTTP 403), so I didn't work around them. Blender facts come from search snippets
or from Blender-adjacent repos on GitHub. The session's shared web-search budget ran out partway through,
so the later facts come only from pages I fetched directly. Everything I could not check is listed in
"Couldn't verify / open".

---

## Top findings

1. **OpenUSD is the only open format with layers, composition, variants and skinned characters in one
   model.** The current release is 26.11. AOUSD Core Specification 1.0 (ratified December 2025) makes the
   composition rules, value resolution and USDA/USDC/USDZ normative. It does not cover domain schemas,
   and nothing I read says UsdSkel is included.
   [openusd.org](https://openusd.org/release/index.html),
   [AOUSD blog](https://aousd.org/uncategorized/foundations-of-open-3d-development-introducing-aousd-core-specification-1-0/)
2. **UsdSkel covers skeletons, linear blend skinning and blend shapes with in-betweens, but not
   combination (corrective) shapes or rig behaviour.** JustStage's face rig, correctives, wrinkle maps
   and cloth would need schemas of its own.
   [UsdSkel intro](https://openusd.org/release/api/_usd_skel__intro.html),
   [UsdSkel schemas](https://openusd.org/release/api/_usd_skel__schemas.html)
3. **glTF 2.0 (+Y up, +Z forward, metres) is the exchange format the open engines prefer.** Godot 4.7
   recommends it, and Blender ships Khronos' add-on. Its limits for characters: 4 joints per weight set,
   clients need only guarantee 8 morphed attributes, morph names exist only by convention
   (`extras.targetNames`), and there is no curve/hair extension.
   [glTF 2.0 spec](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html),
   [Godot formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html)
4. **The open humanoid vocabulary already exists and has converged.** VRM 1.0 (55 bones, 15 required),
   Unity's HumanBodyBones (55) and Godot's SkeletonProfileHumanoid (56 with Root) use the same names.
   Unity names the thumb bones differently. VRM 1.0 and Godot agree on a T-pose facing +Z, Y up, metres.
   [VRM humanoid](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/humanoid.md),
   [Unity](https://docs.unity.com/en-us/engine/current/script-reference/unityengine/humanbodybones),
   [Godot](https://docs.godotengine.org/en/stable/classes/class_skeletonprofilehumanoid.html)
5. **The commercial side has converged on Epic's skeleton and face.** CC5 added ten bones so its skeleton
   lines up with UE5/MetaHuman. CC5 characters "share the same skeletal structure and facial controls as
   MetaHumans". Bone counts: CC3+ 108, UE5 Mannequin 89, MetaHuman 342.
   [Reallusion manual](https://manual.reallusion.com/Metahuman-Interoperability/Content/MetaHuman-Interoperability/17-Metahuman-Interoperability/Skeleton-between-CC-and-UE-Characters.htm),
   [CG Channel 2025-08-28](https://www.cgchannel.com/2025/08/reallusion-releases-character-creator-5/)
6. **ARKit's 52 blendshape names are the public, measurable face-interchange set.** Apple publishes
   them, each runs 0.0–1.0, and left/right are the tracked face's own sides. MediaPipe's free Face
   Landmarker (Apache 2.0) outputs `_neutral` plus 51 of ARKit's names, with no `tongueOut`. FACS is the
   anatomical basis, but its manual is paid ($350).
   [Apple](https://developer.apple.com/tutorials/data/documentation/arkit/arfaceanchor/blendshapelocation.json),
   [MediaPipe source](https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/mediapipe/tasks/cc/vision/face_landmarker/face_blendshapes_graph.cc),
   [Paul Ekman Group](https://www.paulekman.com/facial-action-coding-system/)
7. **A proven rich face rig drives the mesh from controls, not raw shapes.** MetaHuman's DNA format has
   descriptor, definition, behaviour and geometry layers. The behaviour layer maps GUI controls → raw
   controls → corrective expressions, joints, blend-shape weights and animated-map (wrinkle) weights.
   [MetaHuman-DNA-Calibration docs/dna.md](https://github.com/EpicGames/MetaHuman-DNA-Calibration/blob/main/docs/dna.md)
8. **The open undo/command systems agree on one shape.** A named command with serializable arguments,
   do and undo on the same instance, groups or macros, and merging for repeated edits: Qt's `id()` and
   `mergeWith()`, Godot's `MERGE_ENDS`. Blender's lesson: an operator without a context-free `execute()`
   "cannot be repeated from a script or macro".
   [Qt 6.12](https://doc.qt.io/qt-6/qundostack.html),
   [Godot UndoRedo](https://docs.godotengine.org/en/stable/classes/class_undoredo.html),
   Blender `bpy.types.Operator` docs (search snippet only)
9. **MCP's current revision is 2026-07-28.** All messages "MUST follow the JSON-RPC 2.0" spec, the
   protocol is stateless (version and capabilities travel in each request's `_meta`), and schemas default
   to JSON Schema 2020-12. Versions are `YYYY-MM-DD`, `server/discover` returns versions and
   capabilities, and deprecated features stay at least 12 months. Today's 3D-app MCP servers mostly
   bridge to the app's scripting: blender-mcp exposes an "execute arbitrary Python" tool over a local
   socket. [MCP base protocol](https://modelcontextprotocol.io/specification/2026-07-28/basic/index.md),
   [MCP versioning](https://modelcontextprotocol.io/docs/learn/versioning), blender-mcp (search snippet only)
10. **Native-binary plugins break across host releases.** Maya gives no binary compatibility between
    releases. Godot 4.1 broke GDExtension binary compatibility, and `.gdextension` files now declare
    `compatibility_minimum` and `compatibility_maximum`. The WebAssembly Component Model gives a typed,
    language-neutral interface (WIT) and capability isolation. WASI 0.3 (native async) shipped
    2026-06-11, and Wasmtime 46+ enables it by default.
    [WASI P3](https://wasi.dev/releases/wasi-p3),
    [Component Model](https://component-model.bytecodealliance.org/design/why-component-model.html),
    [.gdextension](https://docs.godotengine.org/en/stable/engine_details/engine_api/gdextension/gdextension_file.html)
11. **Permissions differ in kind.** Blender's extension manifest declares `files`, `network`,
    `clipboard`, `camera` and `microphone`, each with a short reason; this is disclosure. Extism's
    manifest enforces limits: memory pages, `allowed_hosts` (empty = none) and `allowed_paths` (empty =
    none). [Extism manifest](https://extism.org/docs/concepts/manifest), Blender manual (search snippet only)
12. **Two proven ways keep old files loading.** Blender writes its struct catalogue (SDNA) into every
    file, records writer and minimum-reader versions, ignores unknown data, defaults missing data and runs
    ordered versioning code. Blender 5.0's header change means only 4.5 LTS can read 5.0 files. USD
    versions schemas by family with an `_N` suffix (`SphereLight_2`).
    Blender wiki and 5.0 release notes (search snippet only),
    [USD schema versioning](https://openusd.org/release/wp_schema_versioning.html) (search snippet only)
13. **Blender 5.2 LTS made remote asset libraries plain static HTTP.** A library is JSON listings, preview
    images and one self-contained .blend per asset. No server software is needed, and catalogues are
    UUID-keyed lines in `blender_assets.cats.txt`.
    [code.blender.org 2026-07-22](https://code.blender.org/?p=13361)
14. **Each target engine has its own axes, units and rules.** Unreal 5.8: Z-up, left-handed, X forward,
    cm; FBX 2020.2 importer; pivot at the root bone; triangulated meshes; one animation per FBX. Unity
    6.6: Humanoid needs ≥15 bones and expects a T-pose; 4 weights by default. Godot 4.7: glTF first, FBX
    through ufbx since 4.3, no USD importer listed. So an exporter needs per-target presets.
    [Unreal FBX](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-skeletal-mesh-pipeline-in-unreal-engine),
    [Unity avatar](https://docs.unity.com/en-us/engine/current/manual/assets-and-media/asset-types/models/importing/configuringthe-avatar)
15. **Importing existing characters:** VRM carries its own licence and permission fields inside the file.
    Daz's scene format (DSON) is a published JSON spec, but Daz's EULA bars redistributing content and
    products from which content can be "separately exported". MetaHuman DNA tooling is public, but its
    repo hasn't been updated for UE 5.6 characters.
    [VRM meta](https://raw.githubusercontent.com/vrm-c/vrm-specification/master/specification/VRMC_vrm-1.0/meta.md),
    [DSON](http://docs.daz3d.com/doku.php/public/dson_spec/start), [Daz EULA](https://www.daz3d.com/eula)

---

## 1 · Scene and data model

| Candidate | What it gives a character app | Gaps for characters | Who reads/writes it | Native or interchange in practice | Licence | Source |
|---|---|---|---|---|---|---|
| **OpenUSD 26.11** (+UsdSkel, UsdShade, MaterialX) | Layers, composition, variants, instancing; skeletons, LBS skinning, blend shapes with sparse offsets and in-betweens; BasisCurves for hair; USDA text, USDC binary, USDZ package | No combination (corrective) shapes, no rig behaviour, no wrinkle maps, no cloth schema; Core Spec 1.0 doesn't name UsdSkel | Unreal 5.8 (USD Stage + import, **Beta**), Houdini Solaris; Blender (not verified, docs 403); Godot lists no USD importer | Houdini Solaris builds its scene from USD (short ref, proprietary); the open apps I checked use their own model and USD as interchange | Tomorrow Open Source Technology License 1.0 (modified Apache 2.0) — commercial yes — [LICENSE](https://github.com/PixarAnimationStudios/OpenUSD/blob/release/LICENSE.txt) | [UsdSkel](https://openusd.org/release/api/_usd_skel__intro.html) |
| **glTF 2.0.1** (+KHR extensions) | Compact runtime format; skins, morph targets (POSITION/NORMAL/TANGENT/TEXCOORD/COLOR), TRS and weights animation; PBR materials plus ratified KHR material extensions; KHR_animation_pointer | 4 joints per set (more sets optional for clients); morph names only by convention; clients must guarantee only 8 morphed attributes; no curves/hair; physics only in Review Draft | Godot (recommended), Blender (Khronos add-on), Unreal Interchange (glTF/GLB), Unity (glTFast, not verified) | Interchange/delivery; nobody I checked uses it as an editor's native model | Spec licence not checked | [glTF spec](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) |
| **VRM 1.0** (glTF + VRMC_* extensions) | Humanoid bone map, expressions, look-at, first-person, spring bones, node constraints, MToon toon material, licence metadata in the file | Avatar-focused (toon material, simple spring physics); no PBR skin/hair/cloth specifics | Blender (VRM add-on, MIT/GPL), Unity (UniVRM, not checked), Unreal (VRM4U, per VMC page), three-vrm (not checked) | Interchange for avatars | Spec licence not checked; add-on MIT or GPL-3.0 | [VRM 1.0 README](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/README.md) |
| **FBX** (Autodesk, proprietary) | De-facto DCC→engine path; Unreal 5.8 imports with FBX SDK 2020.2; skin, blend shapes, LOD groups | Closed format; writing it needs Autodesk's SDK (ufbx only reads) | Every engine and DCC | Interchange only | FBX SDK: proprietary, terms not checked; **ufbx** reader: MIT or Unlicense — commercial yes — [ufbx](https://github.com/ufbx/ufbx) | [Unreal FBX](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-skeletal-mesh-pipeline-in-unreal-engine) |
| **MaterialX 1.39.5** (materials only) | Node-graph look-dev, standard node library, OpenPBR Surface; aligned with OpenUSD | Materials only | USD, Unreal Interchange (named), others not checked | Interchange for materials | Apache 2.0 — commercial yes — [materialx.org](https://materialx.org/) | [materialx.org](https://materialx.org/) |

Facts:

- OpenUSD's current release is 26.11 (page title and v26.11 source links). — https://openusd.org/release/index.html — undated; page read 2026-10-29 — **page read**
- The OpenUSD licence is the "Tomorrow Open Source Technology License 1.0", Apache 2.0 with Section 6 (Trademarks) changed. — https://github.com/PixarAnimationStudios/OpenUSD/blob/release/LICENSE.txt — **page read**
- AOUSD Core Specification 1.0 covers the composition algorithm, stage population and value resolution, USDA/USDC/USDZ, grammar and data types, a document data model and a compliance framework. It "does not dictate" domain vocabularies. Core Spec 1.1 is planned for 2026, adding animation-spline parity with OpenUSD v25.08+, variable and path expressions, and compliance-rubric improvements. Physics and Materials specs are named as domain-spec examples. — https://aousd.org/uncategorized/foundations-of-open-3d-development-introducing-aousd-core-specification-1-0/ — page "last updated" 2026-08-11 — **page read**
- The Core Spec 1.0 public release was 2025-12-17. A Linux Foundation release on 2026-03-25 calls it a "landmark ratification". — https://digitalproduction.com/2026/01/05/aousd-releases-openusd-core-specification-1-0/ , https://www.linuxfoundation.org/press/aousd_prmarch2026 — **search snippet only**
- UsdSkel splits a Skeleton (rest state) from a SkelAnimation, so characters share rest state through instancing. It stores animation in a "compact, vectorized encoding" for crowds and uses linear blend skinning. Skinning targets can be any UsdGeomBoundable prim. Sparse layering of joint transforms is not supported; animation blending is only mentioned as a possible future addition. Per the page, UsdSkel does not aim to provide general rigging and execution behaviours as core USD features. — https://openusd.org/release/api/_usd_skel__intro.html — generated 2026-10-20 — **page read**
- UsdSkel BlendShape "Stores an individual blend shape, and optional in-betweens". Offsets can be sparse through `pointIndices`. In-betweens are attributes in the `inbetweens:` namespace with a `weight`, and authoring one at weight 0 or 1 is an error. Interpolation is unbounded. Weights live on SkelAnimation (`blendShapeWeights`, time-sampled) and are mapped to mesh shapes by token names (`skel:blendShapes`, `skel:blendShapeTargets`). The page gives no count limit and no combination shapes. — https://openusd.org/release/api/_usd_skel__schemas.html — Oct 2026 docs — **page read**
- Joints are named with SdfPath-style tokens, and the hierarchy comes from the paths. Skinned prims carry `primvars:skel:geomBindTransform`. — same page — **page read**
- UsdGeomBasisCurves are linear or cubic curves (bezier, bspline, catmullRom) with widths and normals, "often used to render dense aggregate geometry like hair or grass". — https://openusd.org/release/api/class_usd_geom_basis_curves.html — Oct 2026 docs — **page read**
- glTF 2.0.1 is dated 2021-10-11. It uses a right-handed system with +Y up and +Z forward; "The units for all linear distances are meters", and angles are in radians. — https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html — 2021-10-11 — **page read**
- glTF morph targets may carry POSITION, NORMAL, TANGENT, TEXCOORD_n and COLOR_n. Clients "SHOULD support at least three attributes" and at least eight morphed attributes in total, and may reduce larger assets to the eight highest-weighted. "All primitives MUST have the same number of morph targets in the same order." Names are a tool convention in `mesh.extras.targetNames`. — same — **page read**
- glTF skins: "The number of joints that influence one vertex is limited to 4 per set". Clients "MAY support only a single set of up to four weights and joints". Float weights should sum to about 1.0. — same — **page read**
- glTF animation paths are `translation`, `rotation`, `scale` and `weights`; interpolation is `LINEAR`, `STEP` or `CUBICSPLINE`. `extensionsRequired` is a subset of `extensionsUsed`. `asset.version` is required; `minVersion` is optional. — https://raw.githubusercontent.com/KhronosGroup/glTF/main/specification/2.0/Specification.adoc — **page read**
- Ratified KHR extensions include KHR_animation_pointer, the KHR_materials_* family (anisotropy, clearcoat, dispersion, emissive_strength, ior, iridescence, sheen, specular, transmission, volume, variants), KHR_mesh_quantization, KHR_draco_mesh_compression, KHR_texture_basisu, KHR_texture_transform, KHR_xmp_json_ld, KHR_interactivity and KHR_gaussian_splatting. KHR_materials_diffuse_transmission is a Release Candidate. KHR_physics_rigid_bodies and KHR_collision_shapes are Review Drafts, and KHR_materials_subsurface is an Initial Draft. No curves or hair extension is listed. — https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md — **page read**
- VRM 1.0 is the `VRMC_vrm` extension (humanoid, meta, firstPerson, expressions, lookAt) plus VRMC_springBone, VRMC_node_constraint and VRMC_materials_mtoon. Its status is "Complete". — https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/README.md — **page read**
- Unreal 5.8's USD Stage "works natively with your USD data" with live reload, and its supported prims include skeletal meshes, blend shapes and animation. Materials are PreviewSurface, DisplayColor and NVIDIA MDL. The feature is marked **Beta**. — https://dev.epicgames.com/documentation/en-us/unreal-engine/universal-scene-description-in-unreal-engine — Unreal 5.8 docs — **page read**
- Houdini 22.0's Solaris is "based on the Universal Scene Description (USD) framework", and LOP nodes "generate USD describing characters, props, lighting, and rendering". — https://www.sidefx.com/docs/houdini/solaris/index.html — Houdini 22.0 docs — **page read**
- Godot 4.7 imports glTF (recommended), .blend (through Blender), FBX (ufbx), DAE and OBJ. The page doesn't mention USD. — https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html — Godot 4.7 docs — **page read**
- ufbx reads binary and ASCII FBX from version 3000 on: meshes, skinning, blend shapes, animation with layer blending, LOD groups, constraints and embedded textures. It is single-file C, MIT or Unlicense. The README doesn't mention writing FBX. — https://github.com/ufbx/ufbx — **page read**
- MaterialX v1.39.5 was released 2026-05-22. It is Apache 2.0, hosted by ASWF since 2021, and supports OpenPBR Surface since 1.39.0; 1.39.3 improved alignment with OpenUSD. — https://materialx.org/ — **page read**

Assessment:

- **Strongest for the data model: OpenUSD's concepts and file formats, with JustStage's own schemas on
  top.** Concepts: prims addressed by path, typed and applied schemas, layers and composition, variants
  for outfits and morph presets. Formats: USDA for text, USDC for heavy data. JustStage schemas would
  cover what UsdSkel lacks: combination correctives, face controls, wrinkle-map weights, cloth and groom
  settings. Reason: it is the only open spec that does layering, non-destructive overrides, variants
  *and* skinned characters. It now has a normative core spec, and Unreal reads it (Beta).
- **glTF 2.0 + VRM 1.0 as the export and avatar exchange path.** Godot and Blender take it first, and
  VRM brings a humanoid map, expressions and licence metadata.
- **FBX read-only through ufbx** (MIT) for importing legacy assets. An FBX *writer* is a gap: only the
  proprietary Autodesk SDK writes FBX.
- **Attack:** Using the OpenUSD C++ library as the in-memory model ties JustStage to a large C++
  dependency before the stack is chosen. None of the open apps I checked (Blender, Godot) uses USD as its
  live model, and Unreal's USD Stage is still Beta. **Changed:** the rec is now "USD-shaped model, USD and
  glTF as I/O". Whether the OpenUSD library itself is the runtime model is left to the stack research
  (§6), not decided here.

---

## 2 · Skeleton naming and conventions

| Candidate | Bones | Required | Rest pose | Axes / facing / units | Open? | Source |
|---|---|---|---|---|---|---|
| **VRM 1.0 humanoid** | 55: torso 5, head 4 (incl. eyes, jaw), legs 4×2, arms 4×2, fingers 15×2 (thumb Metacarpal/Proximal/Distal) | 15 (hips, spine, head, upper/lower leg + foot ×2, upper/lower arm + hand ×2) | T-pose required | +Z facing (changed from 0.x), Y up, right-handed, metres (glTF) | Open spec (licence not checked) | [humanoid.md](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/humanoid.md), [vrm.dev](https://vrm.dev/en/vrm/vrm_features/) |
| **Godot 4.7 SkeletonProfileHumanoid** | 56 (Root + VRM-style names; thumb Metacarpal/Proximal/Distal) in groups Body, Face, LeftHand, RightHand | Profile for retarget mapping | T-pose | Faces +Z, right-handed Y up; "+Y axis from the parent joint to the child joint"; +X rotation bends like a contracting muscle | Godot MIT (not re-checked) | [class page](https://docs.godotengine.org/en/stable/classes/class_skeletonprofilehumanoid.html), [retargeting](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html) |
| **Unity HumanBodyBones** | 55 (+LastBone); thumb Proximal/Intermediate/Distal | ≥15 bones for a valid Avatar | T-pose "default pose required by Unity animation" | Not verified this session | Proprietary engine; names public | [enum](https://docs.unity.com/en-us/engine/current/script-reference/unityengine/humanbodybones), [avatar](https://docs.unity.com/en-us/engine/current/manual/assets-and-media/asset-types/models/importing/configuringthe-avatar) |
| **UE5 Mannequin / MetaHuman** (short ref) | 89 / 342 | — | Bind poses differ per skeleton (page doesn't say A or T) | Unreal: Z up, X forward, left-handed, cm | Proprietary | [Reallusion manual](https://manual.reallusion.com/Metahuman-Interoperability/Content/MetaHuman-Interoperability/17-Metahuman-Interoperability/Skeleton-between-CC-and-UE-Characters.htm) |
| **CC3+ / CC5** (short ref) | CC3+ 108; CC5 adds 10 spine/head bones to match UE5 | — | "dedicated bind poses" per target | — | Proprietary | same |
| **HumanIK, Mixamo, Rigify** | Not verified this session (Autodesk/Adobe/Blender docs blocked or not reached) | — | — | — | HumanIK proprietary; Rigify GPL (Blender) | — |

Facts:

- The VRM 1.0 humanoid bones and the 15 required ones are as in the table. Finger bones are not required. "Humanoid bones must be unique." Non-humanoid nodes may sit between humanoid bones. Scale "MUST have positive values". — https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/humanoid.md — **page read**
- VRM 1.0 moved to "T-Pose Z+ orientation" (0.x faced the other way) and still requires a T-pose. Its coordinates are right-handed, Y up, metric, and "complies with the glTF specification". — https://vrm.dev/en/vrm/vrm_features/ — © 2026 page — **page read**
- Unity's HumanBodyBones has 55 bones plus `LastBone` (Unity 6000.6). Its thumbs are `LeftThumbProximal/Intermediate/Distal`; VRM 1.0 and Godot use `ThumbMetacarpal/Proximal/Distal`. — Unity enum page, VRM humanoid, Godot class page — **page read** (the three name lists). That Unity's Proximal corresponds to VRM's Metacarpal is my inference, not read.
- Godot's reference pose is a T-pose facing +Z in right-handed Y-up, with no transform on the node itself. "Fix Silhouette" is for A-pose models. "Overwrite Axis" unifies bone rests to the profile and is "the most important option for sharing animations in Godot 4". "Normalize Position Tracks" scales by hips height (`motion_scale`). The BoneMap auto-maps by name pattern. — https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html — Godot 4.7 docs — **page read**
- Unity Humanoid: "at least 15 bones organized in a way that loosely conforms to an actual human skeleton". T-pose is the default required pose ("Character not in T-Pose" → Enforce T-Pose). Automap works from bone connections. — Unity 6000.6 avatar page — **page read**
- Bone counts: CC3+ 108, UE4 Mannequin 68, MetaHuman 342, UE5 Mannequin 89, UEFN 88. CC5 adds ten bones to the spine and head to align with UE5, and each skeleton's bind pose differs in "the shoulders, hands, and fingers". — Reallusion MetaHuman Interoperability manual — undated — **page read**
- Unreal 5.8's IK Retargeter matches retarget chains by "fuzzy string match", needs a pelvis bone set for root motion, and handles A/T differences with an editable Retarget Pose. — https://dev.epicgames.com/documentation/en-us/unreal-engine/ik-rig-animation-retargeting-in-unreal-engine — Unreal 5.8 docs — **page read**
- MetaHuman 5.7 lets a custom mesh be conformed in poses between A-pose and T-pose (5.6 required A-pose). — metahuman.com news, March 2026 — **search snippet only** (the page redirects to a login)
- The VMC protocol (live avatar motion over OSC) names bones by Unity HumanBodyBones. — https://protocol.vmc.info/english — **page read**

Assessment:

- **Strongest: the VRM 1.0 humanoid names as JustStage's canonical humanoid *role map*.** It is an open
  spec, Godot adopted the same names (thumb naming included), and Unity's differ only at the thumb. Use it
  with the shared rest convention: T-pose, facing +Z, Y up, metres, +Y along each bone (Godot's profile
  states that explicitly).
- **JustStage's deform skeleton can have more bones** (twist, face, extra spine) as long as each humanoid
  role maps to one bone.
- **Export presets retarget to UE5/MetaHuman** (where CC5 went) and to Unity/Mixamo naming.
- **Attack:** the commercial ecosystem (UE5, MetaHuman, CC5) uses Epic's names and per-skeleton bind
  poses, not VRM names. A T-pose canonical choice also costs shoulder deformation quality for A-pose
  binds (my inference, not sourced). **Changed:** the canonical standard is the *role map and reference
  pose for retargeting*, not the deform skeleton's naming or its bind pose. The UE5 preset is a first-class
  export target, not an afterthought.

---

## 3 · Face standards

| Candidate | Size | What it is | Open? | Used by | Source |
|---|---|---|---|---|---|
| **ARKit blendshapes** | 52 | Coefficients 0–1: eyes 14, mouth/jaw 27, brows/cheeks/nose 10, tongue 1 | Name list published by Apple | iPhone capture; MediaPipe outputs 52 scores; CC and MetaHuman need a remap (forum) | [Apple](https://developer.apple.com/tutorials/data/documentation/arkit/arfaceanchor/blendshapelocation.json) |
| **MediaPipe Face Landmarker** | 52 scores (`_neutral` + 51 ARKit names, no `tongueOut`) + 478 landmarks | Blendshape model on a webcam face mesh | Apache 2.0 | Webcam capture | [source](https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/mediapipe/tasks/cc/vision/face_landmarker/face_blendshapes_graph.cc) (page read) |
| **FACS** | AU count not on the page read | Anatomical coding of all visible facial movement (Ekman & Friesen 1978, rev. 2002) | Manual sold ($350) | Basis of production face rigs | [Paul Ekman Group](https://www.paulekman.com/facial-action-coding-system/) |
| **MetaHuman DNA / RigLogic** (short ref) | Counts not on page | Layered rig: controls → raw controls → correctives, joints, blendshapes, animated (wrinkle) maps | DNACalib tooling public; licence name not on the page | MetaHuman; CC5 HD profile "compatible" | [dna.md](https://github.com/EpicGames/MetaHuman-DNA-Calibration/blob/main/docs/dna.md) |
| **CC5 facial profiles** (short ref) | Counts not published in pages read | Standard, Extended (CC4), Extended Plus, HD (CC5); corrective and non-linear sliders | Proprietary | CC5 | [CG Channel](https://www.cgchannel.com/2025/08/reallusion-releases-character-creator-5/) |
| **VRM 1.0 expressions** | 18 presets + custom | Emotions 5, visemes aa/ih/ou/ee/oh, blink ×3, lookUp/Down/Left/Right, neutral; binds morphs, material colours, texture transforms | Open spec | VRM apps | [expressions.md](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/expressions.md) |

Facts:

- ARKit lists 52 blend-shape locations. Each is 0.0 (neutral) to 1.0 (maximum), "You can use any subset", and directions are relative to the tracked face. — Apple ARKit docs (JSON) — **page read**
- MediaPipe's Face Landmarker "predicts 52 blendshape scores" alongside 478 3D landmarks. — https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker — **search snippet only**
- MediaPipe's `kBlendshapeNames` (`std::array<…, 52>`) is `_neutral` (index 0; the code comment says to ignore it) followed by 51 names spelled as ARKit spells them. `tongueOut` is absent. The file is Apache 2.0, © 2023 The MediaPipe Authors. — https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/mediapipe/tasks/cc/vision/face_landmarker/face_blendshapes_graph.cc — **page read**
- FACS was first published in 1978 and revised in 2002; it is an "anatomically based system for describing all visually discernible facial movement". The manual (527 + 197 pages) costs $350 and the FACS test $50. — Paul Ekman Group page — undated — **page read**
- MetaHuman DNA layers: Descriptor (metadata), Definition (names of controls, joints, blend shapes, animated maps; LOD mappings; bind pose), Behavior ("map GUI controls to raw control values, compute corrective expressions, joint transforms, blend shape channel weights, and animated map weights"), and Geometry (meshes, skin weights, deltas). Behavior and Geometry are independent, so a rig can run without geometry. — dna.md — **page read**
- The DNA Calibration repo "has not been updated to support MetaHuman characters created in MetaHuman Creator" in UE 5.6, and points to the MetaHuman for Maya plugin. — https://github.com/EpicGames/MetaHuman-DNA-Calibration — **page read**
- CC5 added Extended Plus and HD profiles, with corrective and non-linear sliders. CC5 characters "share the same skeletal structure and facial controls as MetaHumans", and the HD profile is compatible with the MetaHuman facial expression system. — CG Channel 2025-08-28 — **page read**
- CC5's manual describes the HD expression system only qualitatively ("Each expression drives more facial deformations"; an "Expression Constraint System"). — https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/CC5-HD-Characters.htm — **page read**
- A CC5 user on Reallusion's forum asks for an ARKit → CC5 HD remap asset for UE5. — https://discussions.reallusion.com/t/remap-retarget-asset-for-ue5-from-arkit-to-cc5-hd-facial-profile/15988 — **search snippet only**
- VRM 1.0 expressions: the presets are as in the table. `isBinary` thresholds at 0.5. Override modes (`none`, `block`, `blend`) apply to mouth, blink and lookAt. — expressions.md — **page read**

Assessment:

- **Strongest: two layers.**
  - **Interchange and capture layer: the ARKit 52 names, guaranteed on every JustStage face.** They are
    public, already produced by iPhone and free webcam capture (MediaPipe), and the common bridge to
    other rigs.
  - **Internal rig layer: FACS-based shapes plus correctives and wrinkle-map weights, driven by named
    controls through a behaviour layer**, as MetaHuman's DNA does. VRM presets are derived from it on
    export.
- **Attack:** ARKit 52 is too coarse for hero faces; that is why MetaHuman and CC5 HD go beyond it. FACS
  sits behind a paid manual, and the AU *list* being public was not verified. The free webcam source
  (MediaPipe) gives 51 of the 52, without `tongueOut`. **Changed:** ARKit 52 is the guaranteed minimum
  interchange set, not the rig. Importers must accept a subset (MediaPipe's 51, VRM's 18). The FACS AU
  numbering is a reference only until its openness is checked.

---

## 4 · Command and API layer

| Candidate | Command shape | Undo | Scripting / remote | Open? | Source |
|---|---|---|---|---|---|
| **Blender operators + bpy** | `bl_idname`, typed properties as parameters, `poll`, `execute`, `invoke`, `modal`; UI buttons, menus and keymaps call operators | `UNDO` flag: an undo step is made when execute/invoke returns FINISHED | Python `bpy.ops`; `REGISTER` shows it in the info log and the redo panel | GPL app | Blender API docs 4.x/5.x (snippet) |
| **Godot UndoRedo / EditorUndoRedoManager** | `create_action(name, merge_mode…)`, `add_do_method/property`, `add_undo_method/property`, `commit_action(execute)` | Per-scene histories plus a global history; merge modes; version counter | GDScript, C#, GDExtension | MIT | [UndoRedo](https://docs.godotengine.org/en/stable/classes/class_undoredo.html), [EditorUndoRedoManager](https://docs.godotengine.org/en/stable/classes/class_editorundoredomanager.html) |
| **Qt QUndoStack / QUndoCommand** | Command object with `redo()`/`undo()`; `push()` runs redo | `id()` + `mergeWith()` compression; macros; clean state; undo limit; QUndoGroup | C++ / Python bindings | Qt licence not checked | [Qt 6.12](https://doc.qt.io/qt-6/qundostack.html) |
| **PhotoCraft** (our reference) | id, label, menu path, shortcut, params doc, `enabled`, `run`; dispatched by id from UI, CLI, JSON channel and MCP | Not documented in RESEARCH §11 | Same registry for all callers | MIT/Apache-2.0 | RESEARCH.md §11 (*web, 2026-10-29*) |
| **Unreal Remote Control** (short ref) | `PUT /remote/object/call` with `objectPath`, `functionName`, `parameters` | `generateTransaction: true` makes the call undoable | HTTP 30010, WebSocket 30020 (snippet); `/remote/batch`, `/remote/object/describe`, `/remote/search/assets` | Proprietary; **Beta** | [UE 5.8 HTTP ref](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-api-http-reference-for-unreal-engine) |
| **Maya, Houdini HOM** (short ref) | Maya commands (MEL/Python); HOM `hou` module | Not verified this session | Python | Proprietary | — |

Remote protocols:

| Protocol | Fit | Facts | Source |
|---|---|---|---|
| **JSON-RPC 2.0** | Request/response control channel over any transport | 2010-03-26, updated 2013-01-04; "transport agnostic"; notifications (no id), batch, standard error codes −32700…−32603, −32000…−32099 server range | [jsonrpc.org](https://www.jsonrpc.org/specification) (page read) |
| **MCP 2026-07-28** | AI agents calling the app's tools | JSON-RPC 2.0 messages; stateless; JSON Schema 2020-12 for tool schemas; `YYYY-MM-DD` versions; per-request version in `_meta` / `MCP-Protocol-Version`; `server/discover`; deprecations kept ≥12 months | [MCP base](https://modelcontextprotocol.io/specification/2026-07-28/basic/index.md), [versioning](https://modelcontextprotocol.io/docs/learn/versioning) (page read) |
| **OSC 1.0** | Low-latency streams (live mocap, controllers) | 2002-03-26; message = address pattern + type tag string + arguments; transport-independent, usually UDP | [OSC 1.0](https://opensoundcontrol.stanford.edu/spec-1_0.html) (page read) |
| **VMC protocol** (OSC) | Live avatar bones and blendshapes | UDP 39539/39540; `/VMC/Ext/Bone/Pos` with HumanBodyBones names; `/VMC/Ext/Blend/Val` + `/VMC/Ext/Blend/Apply`; MIT; Unity, Unreal, Blender and Godot receivers exist | [VMC](https://protocol.vmc.info/english) (page read) |
| **gRPC, WebSocket, Live Link** | — | Not researched this session (search budget) | — |

Facts:

- Blender `bl_options`: `REGISTER` shows the operator in the info window and supports the redo panel; `UNDO` "pushes an undo event". Operators that modify data should enable UNDO, and an undo step is made when execute or invoke returns FINISHED. Some operators have no `execute()` and "cannot be repeated from a script or macro". — https://docs.blender.org/api/5.0/bpy.types.Operator.html (and 4.x) — **search snippet only** (403 on fetch)
- Godot `MERGE_ENDS` merges with a previous same-name action, keeping the first undo and the last do ("Useful for sequential changes to a single value"). `MERGE_ALL` merges everything of the same name. `get_version()` rises on each commit. — Godot UndoRedo class — Godot 4.7 docs — **page read**
- EditorUndoRedoManager keeps one history per scene plus a global history, inferred from the first object touched; `custom_context` overrides that guess. `commit_action(execute=true)` runs the do-operations at once. — Godot docs — **page read**
- QUndoStack `push()` calls `redo()` and tries `mergeWith()` when ids match. Macros nest and count as one command. `setClean()` marks the saved state. `undoLimit` can only be set on an empty stack. — Qt 6.12.0 docs — **page read**
- Unreal Remote Control (Beta): the routes are as in the table; `generateTransaction` adds a "Remote Call Transaction Wrap" entry to Undo History. — Unreal 5.8 docs — **page read**. Ports 30010 (HTTP) and 30020 (WebSocket) — **search snippet only**.
- MCP's current version is 2026-07-28. Clients may support several versions. An unsupported version returns `UnsupportedProtocolVersionError` with the supported list. — MCP site — **page read**. Protocol-level sessions and the `initialize` handshake were removed in 2026-07-28 — Towards AI write-up — **search snippet only**.
- MCP 2026-07-28 base protocol:
  - "All messages between MCP clients and servers MUST follow the JSON-RPC 2.0 specification"; request ids "MUST NOT be null".
  - Results carry a `resultType` (`complete` / `input_required`).
  - The protocol is "stateless": version and client capabilities travel in each request's `_meta`.
  - Error codes −32020…−32099 are reserved for MCP.
  - Schemas default to JSON Schema 2020-12, and network `$ref`s are not auto-dereferenced.
  - The TypeScript schema is the source of truth.

  — https://modelcontextprotocol.io/specification/2026-07-28/basic/index.md — **page read**
- blender-mcp: a Blender add-on runs a socket server (localhost:9876). The MCP server sends JSON `{type, params}` and gets `{status, result|message}`. It includes a tool that runs arbitrary Python in Blender. — pypi.org/project/blender-mcp and others — **search snippet only**
- Unreal 5.8 ships experimental first-party MCP server support. Third-party guides say the default server has no authentication and should stay on loopback. Community Unreal MCP servers list 400+ tools. — forums.unrealengine.com, strayspark.studio — **search snippet only**
- I found no first-party MCP server from Unity, Autodesk or SideFX (one search; absence is weak evidence). — **search snippet only**

Assessment:

- **Strongest: one command registry, PhotoCraft's shape.** Each command has an id, a typed parameter
  schema (JSON Schema, so MCP tools and docs are generated from it), `enabled`/`poll`, a context-free
  `run(params) → result`, and an undo record. Undo follows Qt/Godot semantics: do and undo on one
  instance, groups and macros, merge ids for drags.
- **Transport: JSON-RPC 2.0 over a local socket or WebSocket**, with HTTP and MCP as thin adapters onto
  the same registry. MCP itself is JSON-RPC 2.0 with JSON Schema 2020-12 tool schemas, so one schema per
  command serves both. OSC/VMC is kept for live streams, which are not commands.
- **Attack:**
  - Blender shows that UI-context operators (invoke/modal) break scripting.
  - "Run arbitrary code" MCP tools (blender-mcp) bypass undo and permissions.
  - Global snapshot undo vs per-command undo is a real trade-off for sculpting-size data. Blender's
    undo internals are not verified here.

  **Changed:** every command must be runnable with explicit parameters and no UI context; interactive
  tools only *fill* parameters. Arbitrary-code execution is not part of the MCP surface by default. The
  undo-storage strategy for large data stays open.

---

## 5 · Plugin contracts

| Candidate | Unit / manifest | Versioning | ABI stability | Permissions | Distribution | Licence | Source |
|---|---|---|---|---|---|---|---|
| **WebAssembly Component Model + WIT** (WASI 0.3) | Component (binary format 0x1000d) with WIT-typed imports and exports | WIT packages; WASI 0.3.0 2026-06-11, 0.3.1 2026-08-11, patches every two months | Language-neutral Canonical ABI; no shared memory between components | Capability by construction: components get only what they import; the graph can be statically analysed | Any (host decides) | Bytecode Alliance projects (licences not checked) | [why CM](https://component-model.bytecodealliance.org/design/why-component-model.html), [WASI P3](https://wasi.dev/releases/wasi-p3) |
| **Extism** | Manifest: wasm sources (+sha256), memory `max_pages`, `allowed_hosts`, `allowed_paths`, `config` | Not checked | Core wasm modules + its own host-function ABI; HTTP "without WASI" | Enforced deny-by-default hosts and paths | Any | BSD-3-Clause | [README](https://github.com/extism/extism), [manifest](https://extism.org/docs/concepts/manifest) |
| **Zed extensions** (precedent) | `extension.toml` (`schema_version = 1`); Rust → `wasm32-wasip2` | `zed_extension_api` crate version vs Zed version | WASM | Not covered on the page | Not covered on the page | Zed licence not checked | [Zed docs](https://zed.dev/docs/extensions/developing-extensions) |
| **Blender extensions** | `blender_manifest.toml`: `schema_version 1.0.0`, id, semver `version`, `blender_version_min` ≥4.2.0, `license` (SPDX list), `type` add-on/theme, platforms | semver + min/max Blender | Python (no binary ABI) | Declared `files`, `network`, `clipboard`, `camera`, `microphone` + ≤64-char reason | extensions.blender.org | GPL host | Blender manual (snippet) |
| **Godot GDExtension** | `.gdextension`: `entry_symbol`, `compatibility_minimum` (4.1+), `compatibility_maximum` (4.3+), `reloadable`, per-platform `[libraries]` | Min/max Godot | C ABI; 4.0→4.1 broke binaries; later minors "should work" (godot-cpp) | None (native code) | Asset Library | MIT | [.gdextension](https://docs.godotengine.org/en/stable/engine_details/engine_api/gdextension/gdextension_file.html) |
| **Unreal .uplugin** (short ref) | JSON: `FileVersion` (required, currently 3), `Version`, `VersionName`, `Modules` [`Name`, `Type`, `LoadingPhase`] | — | C++ modules per engine build | None | Marketplace/Fab | Proprietary | [UE 5.8 plugins](https://dev.epicgames.com/documentation/en-us/unreal-engine/plugins-in-unreal-engine) |
| **Maya plug-ins** (short ref) | — | `MAYA_API_VERSION` | "Maya does not provide binary compatibility for plug-ins between releases" | None | — | Proprietary | Autodesk docs (snippet) |
| **Houdini HDAs** (short ref) | Asset type name `[namespace::]node_name[::version]` | Versions coexist so old scenes keep working | Data assets, not binaries | — | — | Proprietary | SideFX docs (snippet) |
| **Cinema 4D** (short ref) | Globally unique plugin IDs from Maxon's generator | — | — | — | — | Proprietary | Maxon docs (snippet) |

Facts:

- Core wasm functions are limited to integers and floats. Components use rich WIT types with a Canonical ABI. A component "may not export a memory", and the component graph can be statically analysed (for example, to prove business logic has no access to PII). — Component Model docs — undated — **page read**
- WASI 0.3.0 was released 2026-06-11 and 0.3.1 on 2026-08-11. It adds `async func`, `stream<T>` and `future<T>` to the Component Model and removes `wasi:io`. Wasmtime 46+ enables it by default ("first release to implement the final WASI 0.3.0 specification"), and `wasmtime serve` runs 0.2 and 0.3 components side by side. — wasi.dev — **page read**
- Extism host SDKs cover Rust, JS, Elixir, Go, Haskell, Java, .NET, OCaml, Perl, PHP, Python, Ruby, Zig, C and C++; plugin PDKs cover Rust, JS, Python, Go, Haskell, AssemblyScript, .NET, C, C++ and Zig. It is BSD-3-Clause. — Extism README — **page read**
- Extism manifest: `allowed_hosts` "if left empty then no hosts are allowed and if `null` then all hosts are allowed"; `allowed_paths` "if left empty or `null`, then no file access is granted"; memory is capped in 64 KiB pages. — Extism manifest docs — **page read**
- Zed extensions are Rust compiled to `wasm32-wasip2`, with an `extension.toml` at `schema_version = 1`. — Zed docs — **page read**
- Blender manifest: `schema_version` 1.0.0; `license` takes SPDX identifiers; permissions are `files`, `network`, `clipboard`, `camera` and `microphone`, each with a reason of up to 64 characters; `blender_version_min` ≥ 4.2.0. — Blender manual "How to Create Extensions" (4.4–5.x) — **search snippet only**
- `.gdextension`: `compatibility_minimum` needs Godot 4.1+, `compatibility_maximum` needs 4.3+, and `reloadable` works for godot-cpp from 4.2. — Godot 4.7 docs — **page read**. Godot 4.1 "had to break binary compatibility in a big way", and per godot-cpp, extensions "should work in later minor versions, but not vice-versa". — Godot upgrade guide and godot-cpp README — **search snippet only**
- Unreal `.uplugin`: `FileVersion` is the only required field (currently 3); module types are Runtime, Developer, Editor, RuntimeNoCommandlet, EditorNoCommandlet and Program. — Unreal 5.8 docs — **page read**
- Maya: a plug-in built in 8.5 won't load in 2010; 2016 Extension 2 broke binary compatibility with 2016. — Autodesk SDK docs (2009–2018) — **search snippet only**
- Houdini assets are named `[namespace::]node_name[::version]`, and versions let old and new coexist so scenes don't break. — SideFX Houdini 21/22 docs — **search snippet only**
- Cinema 4D plugin IDs must be globally unique, or only one of the clashing plugins loads; IDs come from Maxon's generator. — Maxon Python API docs 2023–2026 — **search snippet only**

Assessment:

- **Strongest for third-party plugins: WebAssembly components with WIT interfaces.** Reasons: typed,
  language-neutral and stable across JustStage releases, which no native ABI here manages (Maya, Godot
  4.1). Permissions are *enforced* by what the host lets a component import, unlike Blender's disclosure
  list. WASI 0.3 is now final, with async.
- **Manifest borrows from Blender and Zed:** id, semver, host min/max version (Godot's pattern), an SPDX
  licence list, and permissions each with a short reason. Plugin *data assets* get Houdini-style
  versioned type names.
- **Attack:**
  - Heavy plugins (simulation, renderers, sculpt brushes) need GPU access and zero-copy mesh access,
    which WASI does not give. Copy cost across the boundary is not measured.
  - Python scripting, the norm in Blender, Maya and Houdini, is not a WASM-first experience (not
    verified here).

  **Changed:** two tiers. (1) Sandboxed WASM components for third-party plugins. (2) Native built-in
  plugins in-process behind a C ABI with declared min/max host versions (GDExtension's pattern). Both
  tiers register commands in the same registry. Python scripting is a client of the command API, not a
  plugin ABI, until the stack research decides otherwise.

---

## 6 · File format design and versioning

| Pattern | How old files keep loading | Text / binary | Project vs asset | Source |
|---|---|---|---|---|
| **Blender .blend + SDNA** | Struct catalogue (DNA) stored in every file; writer version + minimum reader version; unknown data ignored, missing data defaulted; ordered versioning code per subversion; DNA rename table | Binary | One file holds scene and assets; linking between files | Blender wiki, commit 3ec4c2f (snippet) |
| **USD (USDA/USDC/USDZ)** | Schemas versioned per family by `_N` suffix (`SphereLight_2`, version 0 has no suffix); layers stack non-destructively | Text USDA, binary USDC, zip USDZ | Layers and references across files; Ar resolves asset paths | [schema versioning](https://openusd.org/release/wp_schema_versioning.html) (snippet), AOUSD core (page read) |
| **glTF** | `asset.version` + optional `minVersion`; `extensionsUsed` / `extensionsRequired` | JSON + binary buffer (GLB) | Delivery file | glTF spec (page read) |
| **Godot .tscn/.tres** | `format=3` in the header (Godot 4; 2 for Godot 3); deprecated keys ignored (`load_steps` before 4.6); `uid://` ids survive file moves | Text (binary .scn when imported) | Scenes and resources as separate files | [tscn](https://docs.godotengine.org/en/stable/engine_details/file_formats/tscn.html) (page read) |
| **Protocol Buffers rules** | Field numbers never reused; `reserved`; unknown fields preserved on round-trip; adding fields safe | Binary or JSON | — | [protobuf.dev](https://protobuf.dev/programming-guides/proto3/) (page read) |
| **PhotoCraft** | New fields with `#[serde(default)]` | — | — | RESEARCH §11 |
| **Daz DSON** | JSON; assets referenced, not embedded; per-asset addressing; spec 0.6.1.0 | Text | Scene file (.duf) vs asset files | [DSON](http://docs.daz3d.com/doku.php/public/dson_spec/start) (page read) |

Facts:

- Blender stores the DNA struct definitions in each file and builds a catalogue on load, "used to ensure the backward and forward compatibility of the loaded data". Files store the writing version and the minimum version that can open them. On load, unknown data is ignored, missing data gets defaults, and versioning code runs. — Blender wiki "Compatibility Handling", mystery_of_the_blend — **search snippet only**
- A 2019 commit added `blo_do_versions_dna()` so renamed structs and members still map before comparison. — developer.blender.org rB3ec4c2f — **search snippet only**
- Blender 5.0 changed the file header and every block header to support larger buffers. Blender 4.5 LTS can load the new format, but older versions cannot. 4.5 truncates longer data-block names from 5.0 files. When the major version changes, older Blender "will fail opening" and names the minimum version needed. — developer.blender.org 5.0 core release notes, Blender manual "Compatibility" — **search snippet only**
- USD schema versioning: the version is a suffix on the identifier, only major versions exist, the family is the identifier without the suffix, and helpers include `ParseSchemaFamilyAndVersionFromIdentifier`. Which release first shipped it was not found. — openusd.org white paper + API docs — **search snippet only**
- Godot `.tscn`: sections in fixed order (descriptor, ext_resource, sub_resource, node, connection), `ExtResource("id")` / `SubResource("id")`; nodes have `unique_id` from 4.6. Comments are stripped on save. — Godot 4.7 docs — **page read**
- Protobuf: "Field numbers should never be reused"; "Proto3 messages preserve unknown fields". — protobuf.dev — **page read**
- DSON aims for human-readable files, legal sharing "through asset references rather than embedded assets", and per-asset addressing. It replaced the binary .daz format. — DSON intro, spec 0.6.1.0 — **page read**

Assessment:

- **Strongest: a USD-style layered project.** A text project/scene layer (USDA-like, diffable) points
  by reference to binary data files (USDC-like or own chunked binary) for meshes, morph deltas,
  animation and textures.
- **Every file carries** a format version, the writer version, a *minimum reader version* (Blender) and
  a required-features list (glTF's `extensionsRequired`).
- **Readers preserve unknown fields** on save (protobuf); schemas are versioned per family with `_N`
  (USD); upgrades run as ordered, tested migration steps (Blender's versioning code).
- **Assets live by reference, not embedded** (DSON, USD), which also keeps licensed content out of
  project files.
- **Attack:** Blender's method means carrying every old version's code forever, and its 5.0 break shows
  forward compatibility still breaks. A text project file also grows slow on big scenes. **Changed:**
  "minimum reader version" and refusal with a clear message are explicit. Big data is always in binary
  side files, never inline in the text layer.

---

## 7 · The asset library

| Candidate | Storage unit | Organising | Versioning | Sharing | Licence metadata | Source |
|---|---|---|---|---|---|---|
| **Blender asset browser + 5.2 remote libraries** | Asset marked inside a .blend; remote: one self-contained .blend per asset | Catalogues: `{UUID}:{path}:{simple name}` lines in `blender_assets.cats.txt` (`VERSION 1`); the UUID is the identity | Min/max Blender version per asset; listing schema `_v1` | Static HTTP: JSON listings + previews + files, made by `blender -c asset_listing generate`; daily refresh; offline once downloaded | Tags, author and licence fields not verified (docs 403) | [code.blender.org](https://code.blender.org/?p=13361) (page read); catalogues (snippet) |
| **USD Ar asset resolution** | Asset path → resolved path | Resolver plug-ins per URI scheme; contexts per stage | Up to the resolver | Any backend (http, database) behind a resolver | `assetInfo` (not checked) | [Ar](https://openusd.org/release/api/ar_page_front.html) (page read) |
| **Daz DSON content** (short ref) | .duf scene / .dsf asset JSON | URIs to assets | `file_version` (not verified) | Daz store + DIM (not verified) | Daz EULA | [DSON](http://docs.daz3d.com/doku.php/public/dson_spec/start) |
| **VRM meta** (per-asset licence pattern) | — | — | — | — | `licenseUrl`, `avatarPermission`, `commercialUsage`, `allowRedistribution`, `modification`, `creditNotation`, usage flags | [meta.md](https://raw.githubusercontent.com/vrm-c/vrm-specification/master/specification/VRMC_vrm-1.0/meta.md) (page read) |
| **Unreal Content Browser / Fab; CC Smart Gallery** (short ref) | Not researched this session (search budget; paid ecosystems) | — | — | — | — | — |

Facts:

- Blender 5.2 LTS adds remote asset libraries: "No special server software is required; a standard HTTP server is sufficient". Each asset must be self-contained in one .blend, and "Importing any single asset from that file requires downloading the entire file." Listings refresh once a day, and downloaded assets work offline. — code.blender.org, Julian Eisel, 2026-07-22 — **page read**
- The remote listing has a top-level `_asset-library-meta.json` linking a per-schema-version index (`_v1/asset-index.json`), with an OpenAPI schema in Blender's source. — developer.blender.org docs, devtalk 2024 — **search snippet only**
- Blender catalogues: a catalogue is a path, a UUID and a simple name; the UUID is the identity, so renames don't touch asset files. The file is `blender_assets.cats.txt` at the library root, backed up as `…~`. — Blender manual and wiki (3.0+) — **search snippet only**
- USD Ar: `ArResolver` maps asset paths to resolved paths. Resolvers are C++ plug-ins (Python resolvers are not supported), URI schemes are claimed in `plugInfo.json`, `ArResolverContext` makes resolution per stage, and package paths look like `file.usdz[inner.usd]`. — openusd.org Ar docs — **page read**
- VRM meta fields and defaults: `avatarPermission` onlyAuthor; `commercialUsage` personalNonProfit; `allowRedistribution` false; `modification` prohibited; `creditNotation` required; violence/sexual/political/antisocial flags false. — VRM meta.md — **page read**

Assessment:

- **Strongest: Blender's model as the base.**
  - Library = folder; each asset is a self-contained file; catalogues are UUID-keyed text.
  - Remote libraries are static HTTP with versioned JSON listings and previews. It is open and needs
    no paid server, which fits the user's "no paid products" scope.
  - Add USD-style resolver URIs so a project references assets by id rather than path.
  - Add per-asset licence and permission metadata on VRM's pattern, so imported or bought content
    carries its terms.
- **Attack:** whole-file downloads per asset, and no server-side search or versioning of a single asset
  beyond min/max app version. **Changed:** an asset's file holds one asset and its own dependencies, and
  each asset carries an explicit version field (Blender's listing only had app min/max). Whether asset
  versions are immutable is open.

---

## 8 · Import rules of the target engines (what an exporter must satisfy)

| Engine (docs version) | Up / handedness / forward | Units | Preferred character formats | Skeleton rules | Blend shapes | LODs | Materials | Source |
|---|---|---|---|---|---|---|---|---|
| **Unreal 5.8** | Z up, left-handed, X forward, Y right; FBX importer converts (`convert_scene`, Force Front XAxis) | cm (`convert_scene_unit`) | FBX (SDK 2020.2); Interchange names FBX, glTF, GLB, MaterialX; USD Stage (Beta) | Pivot at the root bone; Use T0 As Ref Pose option; bone influence limit set in Project Settings | "Multiple morph targets … in one file"; Import Morph Targets option | LODs aligned, same pivot | Diffuse + normal auto-created; slot order matters; Interchange makes materials or instances | [FBX skeletal](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-skeletal-mesh-pipeline-in-unreal-engine), [Interchange](https://dev.epicgames.com/documentation/en-us/unreal-engine/interchange-import-reference-in-unreal-engine) |
| **Unity 6.6 / 6.3** | Axis conversion baked or put on the root (Bake Axis Conversion); Unity's own axes not verified | 1 unit = 1 m; Scale Factor, Convert Units | FBX (glTFast package for glTF not verified) | Humanoid: ≥15 bones, T-pose; 4 weights default | Import BlendShapes; normals need smoothing groups | Not verified | Not verified | [Avatar](https://docs.unity.com/en-us/engine/current/manual/assets-and-media/asset-types/models/importing/configuringthe-avatar), FBX importer (snippet) |
| **Godot 4.7** | Y up, right-handed; humanoid faces +Z | Metres (glTF) | glTF (recommended), .blend via Blender, FBX via ufbx (4.3+), no USD listed | BoneMap to SkeletonProfileHumanoid at import; Overwrite Axis; Fix Silhouette for A-pose | Export deformation bones only from Blender or shading is wrong | Not verified | glTF materials | [formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html), [retargeting](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html) |
| **Blender 5.x** | glTF add-on converts with "+Y Up"; Blender's own Z-up not page-verified | Not verified | glTF (Khronos add-on), FBX, USD, VRM (add-on) | glTF import: bone-direction heuristics, "Guess Original Bind Pose" | Shape keys with optional normals/tangents; sparse accessors | — | glTF KHR material extensions imported/exported | [glTF-Blender-IO docs](https://raw.githubusercontent.com/KhronosGroup/glTF-Blender-IO/main/docs/blender_docs/scene_gltf2.rst) |

Facts:

- Unreal 5.8's FBX pipeline "uses FBX 2020.2"; "The pivot point of a Skeletal Mesh is always located at the root bone/joint"; meshes "must be triangulated"; "Only a single animation for each Skeletal Mesh can be imported in a single file"; separate parts skinned to one skeleton are "combined when being imported". — Unreal 5.8 docs — **page read**
- Unreal's editor is left-handed, Z up, X forward, Y right. `convert_scene` converts FBX axes, Force Front XAxis makes X the front instead of −Y, and `convert_scene_unit` converts to centimetres. — Epic coordinate-system page and Python API `FbxAssetImportData` — **search snippet only**
- Interchange (5.8) skeletal options: Import Morph Targets, Bone Influence Limit (capped by Project Settings), Use T0 As Ref Pose, Create Physics Asset. Materials import as materials or material instances with automatic parents under `/Interchange/Materials`. — Unreal 5.8 docs — **page read**
- Unity: Scale Factor is a global multiplier, and physics expects 1 unit = 1 m. Bake Axis Conversion writes the correction into mesh and animation data; otherwise it goes on the root Transform. Blend-shape normals require smoothing groups. — Unity 6.3 FBX importer docs — **search snippet only**
- Unity Skin Weights limit influence "to four bones" by default (adjustable). — Unity 6000.6 avatar page — **page read**
- Godot: Blender's built-in COLLADA export "does not work properly for the needs of game engines". FBX2glTF needs the proprietary FBX SDK and is "generally not recommended". .blend import needs Blender 3.0+ installed. — Godot 4.7 docs — **page read**
- Blender's glTF exporter warns that models "may appear incorrectly in many viewers with value different to 4 or 8" bone influences. It exports shape-key normals and tangents optionally, and uses sparse accessors when smaller. Its animation modes are Actions, Active Actions merged, NLA Tracks and Scene. — glTF-Blender-IO docs (GitHub) — **page read**

Assessment:

- **Strongest: one canonical internal convention plus per-target export presets** — the approach CC
  takes with its "Target Tool Preset" (§9).
  - Internal: Y up, right-handed, +Z facing, metres (glTF/VRM/Godot).
  - Unreal preset: Z up, X forward, cm, single root, triangulated, morphs named.
  - Unity preset: T-pose humanoid, ≤4 weights.
  - Godot and Blender preset: glTF 2.0, ≤4 weights per set, `extras.targetNames`, deform bones only.
- **Format per target:** glTF first for Godot, Blender and Unreal Interchange; FBX for Unreal and Unity
  where glTF falls short; USD for Unreal (Beta) and USD pipelines.
- **Attack:** FBX output needs Autodesk's proprietary SDK (ufbx only reads), against the open-only scope.
  Unity's glTF path and Unity's axes were not verified. **Changed:** FBX *export* is marked an open
  question (proprietary-SDK dependency); glTF is the default export.

---

## 9 · Importing existing characters (CC, Daz, MetaHuman, VRM)

| Source | Formats out (public docs) | What survives (from pages read) | Reuse terms (one line, no legal analysis) | Source |
|---|---|---|---|---|
| **Character Creator 5** | FBX (Target Tool Preset), OBJ; USD mentioned (snippet); json sidecar "records the relationships between objects and their textures"; HIK profile | Mesh, character, motion; subdivision levels with multi-level normal maps; textures in categorised folders | Reallusion EULA not read this session | [CC5 Export FBX](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/Export-FBX.htm) |
| **Daz Studio** | DSON (.duf/.dsf, public JSON spec 0.6.1.0); FBX (product pages) | DSON: figures as assets with relationships (details not read) | EULA: 2D renders allowed; games need Game Developer/Interactive licences; no redistribution; no products whose content can be "separately exported, extracted or de-compiled" | [DSON](http://docs.daz3d.com/doku.php/public/dson_spec/start), [EULA](https://www.daz3d.com/eula) |
| **MetaHuman** | DNA (rig + geometry); FBX via Unreal/Bridge; MetaHuman for Maya plugin for 5.6+ | DNA: joints, blend shapes, animated maps, controls, LODs | Snippet: "can be used with any engine or creative software", free under $1M revenue under the UE licence. The DNA tool's own licence (page read) limits MetaHuman characters to where Epic's Content License permits, e.g. Unreal Engine and Twinmotion; the two statements are not reconciled here | [DNA repo](https://github.com/EpicGames/MetaHuman-DNA-Calibration), [its LICENSE](https://raw.githubusercontent.com/EpicGames/MetaHuman-DNA-Calibration/main/LICENSE); licence page behind login (snippet) |
| **VRM** | .vrm = glTF 2.0 + VRMC_* | Humanoid map, expressions, spring bones, MToon, constraints, licence meta | In-file meta fields set the model's terms (VRM Public License 1.0 URL) | [meta.md](https://raw.githubusercontent.com/vrm-c/vrm-specification/master/specification/VRMC_vrm-1.0/meta.md) |

Facts:

- CC5 FBX export has a Target Tool Preset dropdown that changes advanced settings per destination tool. Options are Mesh, Character, Motion or Character with Motion. It writes a json file and a `Multi_Normal` folder, and textures go in categorised subfolders. — CC5 manual — undated — **page read**
- CG Channel says CC5 exports FBX or OBJ, is Windows 10+, and costs $299 perpetual (Deluxe bundle $499). — 2025-08-28 — **page read**
- Reallusion's subdivision-export page says the feature works "via FBX/USD format or Live Link". A CC4 feature request for glTF export is open. — reallusion.com — **search snippet only**
- Daz EULA: content may be used "in the creation and presentation of two-dimensional animations and renderings". Redistribution is barred without DAZ's written consent. It excludes using content in AI systems to auto-generate derivative materials. Selling content separately from a game requires written consent. — daz3d.com/eula — © 2026, undated — **page read**
- MetaHuman 5.6+: the standard UE EULA applies, and MetaHumans "can be used with any engine or creative software". — metahuman.com/license — **search snippet only** (the page redirects to a login)
- In 5.6, conforming relied on vertex order that FBX export from Unreal loses, so round-trips needed DNA-aware plugins. — metahuman.com news (March 2026) — **search snippet only**
- A third-party Blender add-on claims to import MetaHuman DNA (5.0–5.7). — superhivemarket.com — **search snippet only**, not verified
- VRM Add-on for Blender: import and export for "Blender 2.93 to 5.2", MIT or GPL-3.0. — GitHub saturday06/VRM-Addon-for-Blender — **page read**

Assessment:

- **Strongest import paths, in order:**
  1. **VRM and glTF**: open spec, humanoid map and licence in the file.
  2. **FBX via ufbx** for CC and Daz exports, with a per-source retarget profile onto the canonical
     humanoid map, and CC's json sidecar for materials (format not studied).
  3. **DSON** for Daz scenes, which are public JSON.
  4. **MetaHuman DNA** through public DNACalib code, for 5.5-and-older characters only.
- **Attack:** Daz's EULA restricts exportable or redistributable forms, so JustStage-saved projects must
  not embed imported licensed content in a redistributable way. MetaHuman terms are unverified (login
  wall). **Changed:** importers keep a provenance and licence record per imported asset (§7), and projects
  reference imported content rather than embed it (§6). Legal reading stays with the user.

---

## Licences, one line each

- OpenUSD — Tomorrow Open Source Technology License 1.0 (modified Apache 2.0) — commercial: yes — https://github.com/PixarAnimationStudios/OpenUSD/blob/release/LICENSE.txt
- AOUSD Core Specification 1.0 — not stated on the page read — unclear — https://aousd.org/
- glTF 2.0 spec (Khronos) — GitHub reports "Other" (NOASSERTION) for KhronosGroup/glTF; the LICENSE.md path returned 404 — unclear — https://github.com/KhronosGroup/glTF
- VRM 1.0 spec — GitHub detects no licence for vrm-c/vrm-specification (last push 2026-10-02) — unclear — https://github.com/vrm-c/vrm-specification
- VRM Add-on for Blender — MIT or GPL-3.0 — yes — https://github.com/saturday06/VRM-Addon-for-Blender
- VMC protocol — MIT — yes — https://protocol.vmc.info/english
- MaterialX — Apache 2.0 — yes — https://materialx.org/
- ufbx — MIT or Unlicense — yes — https://github.com/ufbx/ufbx
- Autodesk FBX SDK — proprietary; terms not checked — unclear — https://aps.autodesk.com/developer/overview/fbx-sdk
- Extism — BSD-3-Clause — yes — https://github.com/extism/extism
- Wasmtime / WASI / Component Model tooling — not checked — unclear — https://wasi.dev/
- JSON-RPC 2.0 spec — not checked — unclear — https://www.jsonrpc.org/specification
- MCP spec — not checked — unclear — https://modelcontextprotocol.io/
- OSC 1.0 spec — not checked — unclear — https://opensoundcontrol.stanford.edu/spec-1_0.html
- Apple ARKit blendshape list — Apple developer documentation; no licence statement checked — unclear — Apple docs
- MediaPipe (face blendshapes graph source) — Apache 2.0 — yes — https://github.com/google-ai-edge/mediapipe
- FACS manual — sold ($350); not a software licence — conditional (purchase) — https://www.paulekman.com/facial-action-coding-system/
- DSON spec wiki — CC Attribution 3.0 Unported (wiki content) — yes — http://docs.daz3d.com/doku.php/public/dson_spec/start
- Daz content — Daz EULA (restrictions above) — conditional — https://www.daz3d.com/eula
- MetaHuman — UE EULA, free under $1M revenue (snippet) — conditional — https://www.metahuman.com/license
- MetaHuman-DNA-Calibration repo — "MetaHuman DNA Calibration License Agreement" (Epic); MetaHuman characters only where Epic's Content License permits, e.g. with Unreal Engine and Twinmotion — conditional — https://raw.githubusercontent.com/EpicGames/MetaHuman-DNA-Calibration/main/LICENSE (last push 2025-06-20)
- Qt — not checked this session — unclear — https://doc.qt.io/
- Godot — not re-checked this session (MIT per common record) — https://godotengine.org/license
- Blender (and add-ons using its API) — GPL; owned by RESEARCH §9 — https://www.blender.org/about/license/

---

## Couldn't verify / open

- **Blender docs blocked (HTTP 403 on docs.blender.org, developer.blender.org, projects.blender.org).**
  Not verified:
  - operator `poll` semantics;
  - the undo system's internals (global snapshot vs per-step);
  - the manifest permissions text (snippet only);
  - asset metadata fields (tags, author, licence, copyright);
  - USD import of UsdSkel and blend shapes (PR #110912 not read);
  - FBX importer axis and bone-orientation options;
  - the Rigify bone list;
  - Blender's own axis and unit statement.
- **Search budget exhausted midway (shared session limit).** Not researched: gRPC, Live Link, Unity
  glTFast and Unity USD packages, Houdini `hou.undos`, Maya `MPxCommand` undo, HumanIK bone list,
  Mixamo bone names and terms (Adobe page 403), Unreal groom/Alembic spec (page empty), UE5 Mannequin
  bone list, MetaHuman control counts, CC5 HD profile shape count, CC Smart Gallery, Fab, the Reallusion
  content EULA.
- **MCP session removal:** the 2026-07-28 base-protocol page states statelessness (page read); the
  removal of `initialize` is from a secondary write-up only.
- **MetaHuman terms conflict:** the UE 5.6+ "any engine" statement (snippet) vs the DNA Calibration
  licence's Unreal/Twinmotion limit (page read). Not reconciled; the user's call.
- **UsdSkel:** whether blend shapes carry `normalOffsets` (not on the page read); whether AOUSD plans a
  skel/character domain spec (not found).
- **Cloth:** no open interchange standard was found (glTF has only rigid-body and collision drafts;
  UsdPhysics not checked). **Strand hair:** USD BasisCurves exists; Unreal's groom import format was not
  verified.
- **Unity's coordinate system** (left-handed, Y up) was not verified on a page.
- **Exact facing/axis rules for VRM 1.0 bone local axes:** the spec page read doesn't state them.
- **FBX writing:** no open-source FBX writer found or checked. The open-only scope leaves FBX export as
  a user decision.
- **Performance of WASM plugins on large meshes** (copy cost across the component boundary): not measured.
- Omniverse facts gathered before the scope change were dropped, as the user asked.
