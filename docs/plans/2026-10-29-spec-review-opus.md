# Review of the Fable session's standards spec, PRD and ARCHITECTURE (2026-10-29, Opus 5.5)

The user, verbatim: "fable messed up on the standards by trying to roll its on json file for characters and a bunch of
other non standard hand rolled stuff when openusd handled it, i dont trust fables synthesis so can you revoiew all of
fables work". Scope: `docs/standards/` (13 files), `docs/dev/PRD.md`, `docs/dev/ARCHITECTURE.md`, Fable's RESEARCH and
TASKS entries, its evidence folder and its memory edits. Nothing in the spec is changed by this review. **Recs 1–27 APPROVED 2026-10-29** ("i agree with your recs",
TASKS); the spec rewrite waits for the word go, and N1, N3, the command registrar, item 10 and item 15 wait for the
user's word by name. Every fact below was checked at its source or on this machine on 2026-10-29 (RESEARCH §1, §5, §6,
§8 carry them).

Passes run, each from a new angle: (1) standard-first per piece; (2) every factual claim; (3) against the approved
recs R1–R21 and the user's decisions; (4) how the pieces interact; (5) attacks on this review's own recs; (6) the
untouched neighbours (TASKS, RESEARCH, memory, evidence files). A seventh pass over the list found nothing new.

## What holds

- The Daz evidence files are byte-equal to Daz's source (`g9_to_unreal_manny.json`, `g8_to_unreal.json`).
- The UE5 Mannequin lists hold: a second scan of `SK_Mannequin.uasset` finds no side-suffixed bone outside Fable's
  161, and `SKM_Manny_Simple` has the published 89.
- VRM's 55 roles, Apple's 52 names, Blender's bone-naming rule, the USD hook API, slotted Actions, UsdShade render
  contexts, `usd-core`, the kit-code facts and EEVEE's true displacement ("Displacement and Bump") are correct.
- The skeleton's names (UE5 verbatim), ARKit 52 as the guaranteed set, DNA + OpenRigLogic for the face, one extension
  with modules, MCP as the only remote door and pytest as the only runner are right.

## Findings, most severe first

Each: the fact and its source → the rec → the attack on the rec → what the attack changed.

### 1 · Body correctives already have an open standard: the DNA format (N5's premise was false)

- **Fact.** OpenRigLogic (MIT, the library the spec already uses for the face) defines DNA behaviour layers for body
  correctives: `include/dna/layers/RBFBehaviorReader.h` (RBF poses → joint outputs, blend-shape channels, animated
  maps; solver types additive/interpolative; quaternion and twist-axis distances) and `TwistSwingBehaviorReader.h`
  (twist and swing setups → output joints with blend weights). MetaHuman's archetype DNA in the user's UE 5.8
  (`F:\Epic\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCoreTechLib\Content\ArchetypeDNA\body_head_combined.dna`)
  holds one RBF solver per joint (`calf_l_UERBFSolver`, `clavicle_l_UERBFSolver`, `index_l_01_UERBFSolver`, …) and
  the UE corrective bones. Fable wrote "none exists" and invented `JustStageCorrectiveAPI`; the user approved N5 ("5
  ok") on that premise.
- **Rec.** Body correctives live in a body DNA file (`rig/body.dna`) beside the face DNA — MetaHuman's own split (head
  and body are separate DNA files, RESEARCH §7) — evaluated by OpenRigLogic in Blender and by Unreal's RigLogic plugin.
  `JustStageCorrectiveAPI` and the N5 schema go.
- **Attack.** (a) Blender has no RigLogic evaluator, so the extension drives bones and shape keys from OpenRigLogic's
  Python bindings — the face needs exactly that already. (b) glTF and FBX can't carry DNA — bake, as before. (c)
  Authoring RBF poses needs DNA writing — OpenRigLogic ships `RBFBehaviorWriter` and `TwistSwingBehaviorWriter`. (d)
  In Unreal, RigLogic evaluates a body DNA natively, which is simpler than the plugin building Control Rig nodes.
- **Changed.** Nothing; a NOT STANDARD piece disappears.

### 2 · hm08's helper geometry and joint cubes are how joints and clothes follow the body (N2's premise was false)

- **Fact.** Every MPFB2 rig places its joints from the joint cubes: `rig.game_engine.json` bones carry
  `"strategy": "CUBE", "cube_name": "joint-l-foot-1"` for head and tail. MHCLO garments fit to helper vertices
  (RESEARCH §5: deleting helpers "stops most clothes fitting"). MPFB2 masks helpers while editing and deletes them at
  export (its "Delete helpers" operation; export options `mask_modifiers`). The spec has **no** rule for moving joints
  when sliders change the body; the joint cubes are that rule. Fable called the 5,778 vertices "dead".
- **Rec.** Keep helpers and joint cubes while editing, masked; delete them at export — MPFB2's own workflow. Joint
  placement = MPFB2's `CUBE` strategy (the mean of a joint cube's vertices, which every morph moves). N2 is withdrawn.
- **Attack.** Memory and time per morph with 19,158 instead of 13,380 vertices — MakeHuman and MPFB2 carry it on
  ordinary machines; the gate measures it. A joint regressor (SMPL's method) avoids helpers but is new work and new
  data. Anny dropped helpers, but Anny has its own rig and no garment system.
- **Changed.** Nothing.

### 3 · MPFB2 already has the formats for this base: sliders, character state, garments, face units, visemes, rig, weights

R4 adopted MakeHuman's hm08 and its CC0 targets. MPFB2 (GPL-3.0 code, CC0 assets — reusable inside our GPL extension,
R2/R11) is the maintained MakeHuman for Blender (push 2026-10-24) and already defines, for exactly this mesh:

| Job | MPFB2's existing format (read 2026-10-29) | What Fable invented instead |
|---|---|---|
| Slider definitions | `data/targets/target.json`: 23 groups, 234 slider categories, each with `label`, `targets`, `has_left_and_right`, `opposites`; `data/targets/macrodetails/macro.json`: macro targets (gender, age, muscle, weight, …) with ranges and combinations | `JustStageSliderAPI` per character |
| A character's slider state | MakeHuman's `.mhm` modifier values; in USD the shape weights are `UsdSkelAnimation.blendShapeWeights` | slider prims inside every package |
| Garment fit | MHCLO (`docs/fileformats/mhclo.md`): per vertex 3 base vertices + 3 weights + xyz offset, or an exact match; `z_depth` (layer order); `delete_verts` (body faces hidden); `x/y/z_scale`; author and licence header; used for clothes, eyes, hair and proxies | `fitTriangle`/`fitBary`/`fitOffset` primvars, `layer`, a `juststage:hide` GeomSubset |
| ARKit 52 on hm08 | "Faceunits 01" pack, CC0 ("Functional asset packs", static.makehumancommunity.org); MPFB2's `faceservice.py` `ARKIT_FACEUNITS` (52) | "the gate's rig-generation work" |
| Visemes | "Visemes 02" (Meta/Oculus 15: `viseme_aa … viseme_U`) and "Visemes 01" (Microsoft 22), both CC0 | Meta's names from a search snippet |
| Expressions | MPFB2's expression JSON: `format_version`, `name`, `face_units` keyed by ARKit names, licence fields | — |
| A UE-named rig with weights | `rig.game_engine.json` (53 bones in UE4-Mannequin names: `pelvis`, `spine_01–03`, `neck_01`, `clavicle_l`, `upperarm_l`, `lowerarm_l`, `hand_l`, fingers `_01–_03`, `thigh_l`, `calf_l`, `foot_l`, `ball_l`) + `weights.game_engine.json`; also `game_engine_with_breast` | no source for body skin weights at all |

- **Rec.** JustStage's body, head and garment layer is built on MPFB2's data formats and, where code helps, its GPL
  services: sliders from `target.json`/`macro.json` (the same format extended for the MHR, GNM and user spaces);
  character state as shape weights (USD) and MHM-style modifier values; garments as MHCLO (LoBoFit, R8, refits on top);
  the CC0 face-unit and viseme packs as the first ARKit 52 and visemes; the `game_engine` rig and weights as the start of
  the UE5 skeleton, extended by the 27 bones UE5 adds (`spine_04/05`, `neck_02`, twists, metacarpals) with their own
  joint-cube rules and weights.
- **Attack.** MPFB2's formats are MakeHuman's, not an industry standard — but they are the existing format for the
  data R4 chose; a new format for the same data is the second way the rules forbid. MHCLO lacks tuck-under relations and
  cloth settings — two small fields remain ours (§6 below). The CC0 face units may not reach the bar — the gate (R3)
  judges, and improved shapes replace them under the same names. The game_engine rig is UE4-era — extending it is less
  work than authoring 80 bones and their weights from nothing.
- **Changed.** Sliders: the per-character slider prims were dropped once it was clear definitions are app data and only
  values belong to a character.

### 4 · Materials: OpenPBR and MaterialX cover skin, eyes and hair; the `juststage` shader network is hand-rolled

- **Fact.** MaterialX's OpenPBR Surface has subsurface (colour, radius, scale, anisotropy), coat, fuzz (for vellus),
  specular and transmission (cornea); `pbrlib` has `chiang_hair_bsdf` and `deon_hair_absorption_from_melanin`
  (melanin-based hair colour). Blender's USD exporter writes MaterialX networks itself (manual `usd.rst`); Unreal 5.8
  imports MaterialX OpenPBR into Substrate (RESEARCH §8, S9). Fable added a third network with `info:id =
  "juststage:skin"`, a shader no program knows.
- **Rec.** Materials export through Blender's own USD exporter as UsdPreviewSurface + MaterialX (OpenPBR for skin,
  eyes, teeth, cloth; Chiang hair with the melanin node for hair). The generator inputs (melanin, haemoglobin, age,
  pores) belong to the generator preset that made the textures, not to the material. No `juststage` render context.
- **Attack.** Whether Blender's MaterialX export carries Principled's subsurface and coat fully is not tested here
  (the manual lists caveats; displacement is not exported to MaterialX). Whether OpenPBR → Substrate reaches
  MetaHuman-grade skin in Unreal is unknown — the plugin maps the OpenPBR values onto its own skin material either way,
  and the gate judges. Both are test items for step 1, not reasons to invent a format.
- **Changed.** Two test items added to the gate.

### 5 · Grooms: Blender's own hair node groups are the generator; `JustStageGroomAPI` duplicates them

- **Fact.** Blender 5.3 ships `datafiles/assets/nodes/procedural_hair_node_assets.blend` (on disk at
  `E:\blender-5.3.0-beta`); the manual lists them: Generate, Interpolate, Duplicate Hair Curves; Clump, Curl, Braid
  Hair Curves, Create Guide Index Map; Blend, Displace, Frizz, Noise, Roll, Rotate, Shrinkwrap, Smooth, Straighten,
  Trim Hair Curves. Fable's groom schema stored "guide count, interpolation, clumping, noise, length maps".
- **Rec.** A groom is a Curves object with Blender's hair node-group modifiers; its settings are their inputs in the
  `.blend` and the library asset. USD carries the baked curves with Epic's `GroomAPI` and the `groom_*` primvars;
  Alembic 1.5 for Unreal, as the spec says.
- **Attack.** Generator settings then don't travel in USD — that is industry practice (studios bake; RESEARCH S10), and
  JustStage-to-JustStage transfer uses the library `.blend`. **Changed:** nothing.

### 6 · With 1–5, N1's USD schemas are no longer needed

What remains of Fable's applied-schema families after 1–5: a character id and versions, the HD-morph map link, a
garment's tuck-under list and cloth settings, a lip-sync take's audio and phonemes.

- **Rec.** No JustStage applied API schemas and no `usdGenSchema`. Character id, name and version go in USD's native
  `assetInfo`; the rest are a handful of custom attributes and relationships in the `juststage:` namespace (the way
  Blender's own exporter writes custom properties — `userProperties` by default, namespace configurable, `usd.rst`),
  written from the extension's PropertyGroups by the USD hook; lip-sync audio as `UsdMediaSpatialAudio` (Blender's
  bundled `pxr` has `UsdMedia`). N1 shrinks to "the names of about ten `juststage:` attributes".
- **Attack.** Untyped attributes aren't validated by other readers — those readers ignore them anyway; JustStage and
  the Unreal plugin validate. Applied schemas would give `HasAPI()` and docs — worth it only with many fields, which
  1–5 removed. Blender 5.0 stores `bpy.props` values apart from custom properties (5.0 Python notes), so the native
  custom-property export doesn't see PropertyGroups — hence the hook, which the spec already has.
- **Changed.** The hook stays; schema generation goes.

### 7 · Commands: the schema source should be the typed Python function, as in the MCP server we build on

- **Fact.** Blender Lab's MCP server declares each tool as a FastMCP function (`@mcp.tool(...)` in
  `mcp/blmcp/tools/get_objects_summary.py`), and the MCP SDK derives the JSON Schema from its type hints; it depends on
  `mcp[cli]>=1.2.0,<2`. Blender's own gotcha page says scripts should prefer API functions to operators (operators
  return only success/cancel). Fable made hand-written schema files the source, generated operator properties from them,
  and returned results through a scene property (`last_result`).
- **Rec.** One source per command: a typed Python function in `juststage.api`. FastMCP derives the tool and its JSON
  Schema from it; the operator wraps it for the UI and the keymap; Python callers call the function and get its return
  value. R19 holds: one operator and one JSON Schema per command, the same command at every door.
- **Attack.** Operator properties then duplicate the function's arguments — generated from the signature by a small
  helper, or written once per command; both beat a third source. **Changed:** nothing.

### 8 · R19 can't hold both "built from Blender Lab's server" and "the 2026-07-28 spec" today

- **Fact.** The MCP Python SDK 1.x line's `LATEST_PROTOCOL_VERSION` is `2025-11-25` (with the `initialize`
  handshake); `2026-07-28` (stateless) arrives in SDK 2.x (2.3.0 lists both). Blender Lab pins `<2`.
- **Rec.** Use Blender Lab's server as it is (2025-11-25) and move to 2026-07-28 when it moves; offer the SDK-2 bump
  upstream. The spec's "stateless, `server/discover`" lines become "per Blender Lab's SDK".
- **Attack.** R19's text names 2026-07-28 — this changes an approved rec, so it waits for the user's word. Patching the
  pin ourselves now is the other option; it forks a dependency for a protocol no client needs yet. **Changed:**
  marked as an R19 change.

### 9 · Two mapping-table columns are wrong

- **Mixamo.** three-vrm's map (MIT): `mixamorigSpine` → spine, `Spine1` → chest, `Spine2` → upperChest. With the spec's
  role map (spine_01 = spine, spine_03 = chest, spine_05 = upperChest) Mixamo `Spine1` ↔ `spine_03` and `Spine2` ↔
  `spine_05`; the table has them at `spine_02` and `spine_03`.
- **CC3+/CC4.** Reallusion's GPL Blender tools (`rigify_mapping_data.py`, names only): `CC_Base_Waist` ↔ Rigify
  `spine.001` ↔ UE `spine_01`; `Spine01` ↔ `spine.002` ↔ `spine_02`; `Spine02` ↔ `spine.003` ↔ `spine_03`;
  `NeckTwist01` ↔ `neck_01`. The table maps `Spine01` → `spine_01` and `Spine02` → `spine_02` and leaves `Waist` out.
- **Rec.** Fix both columns from these sources. **Attack:** none; they are lookups.

### 10 · MetaHuman's face control names and joint names are on this machine (new fact under the approved N4)

- **Fact.** `SKM_Face.dna` in the user's UE 5.8 holds about 420 GUI control channels (`CTRL_C_jaw`,
  `CTRL_L_mouth_cornerPull`, `CTRL_L_brow_lateral`, `CTRL_C_mouth_stickyU`, `CTRL_C_tongue_roll`, …), `FACIAL_*`
  joints, and part names `head`, `teeth`, `eyeLeft`, `eyeRight`, `eyeshell`, `eyelashes`, `eyeEdge`. Fable's reason for
  inventing our own control names ("Epic's content, not public as a list") was wrong; the user approved N4 on ARKit's
  merit, which stands.
- **Rec.** Keep ARKit 52 as the guaranteed interchange set (N4) and name the DNA rig's GUI controls, face joints and
  face parts with MetaHuman's names, so MetaHuman Animator curves and MetaHuman tools drive a JustStage face with no
  mapping table. Only the names are taken; every shape, joint position and weight stays ours.
- **Attack.** AGENTS.md's clean-room rule: "Never copy their code, shaders, base meshes, morphs, content or assets."
  Reading names out of Epic's DNA files is reading their content. Counter: the UE5 bone names the user accepted came out
  of `SK_Mannequin.uasset` the same way; names are the interface a pipeline must speak, like the `groom_*` attributes.
  **Changed:** this is the user's call against their own clean-room rule, not mine; the rec is shown with that conflict
  named.

### 11 · glTF carries vendor data in a vendor extension, not a sidecar

- **Fact.** Khronos' extension registry: vendor extensions use a registered vendor prefix (VRM's `VRMC_*` is one);
  `EXT_` for multi-vendor, `KHR_` for ratified. The spec writes a `.juststage.json` beside glTF.
- **Rec.** Inside glTF, JustStage data is a vendor extension under a prefix registered with Khronos (a pull request
  to the registry); the sidecar stays for FBX only (CC5, Daz, MetaHuman pattern). **Attack:** a registry PR is a small
  outward step — it waits for the user's word when the exporter is built. **Changed:** nothing.

### 12 · Unreal: share Epic's animations through compatible skeletons

- **Fact.** Unreal skeletons have a "Compatible Skeletons" list that lets one skeleton use another's animation data,
  one way (Epic's Python API `Skeleton` class; the Skeletons page); importing onto an existing skeleton merges new bones
  into it. The spec builds `SK_JustStage_<version>` with no link to Epic's skeletons, so Epic, Fab and MetaHuman body
  animations would need retargeting despite identical bone names.
- **Rec.** The plugin keeps its own skeleton asset (so the user's `SK_Mannequin` is never modified) and lists
  `SK_Mannequin` and the MetaHuman body skeleton as compatible. **Attack:** proportions differ per character — Unreal's
  translation retargeting settings handle it, as they do across MetaHuman body types. **Changed:** merge-into-Epic's was
  rejected for modifying the user's asset.

### 13 · R17 changed without a flag: FBX export

- **Fact.** R17 (approved): FBX "out through ufbx-write after round-trip tests". The spec makes Blender's own FBX
  exporter the default and ufbx-write later.
- **Rec.** Blender's exporter is the more standard choice inside Blender (shipped for years, writes blend shapes and,
  since 5.1, shape-key normals; ufbx-write is "work in progress") — keep it, but as an R17 change on the user's word.
  **Attack:** ufbx-write keeps the MIT libraries free of GPL code — only matters for MIT tools that export FBX outside
  Blender, none of which is planned. **Changed:** marked as an R17 change.

### 14 · The engine host: end users' generators were made to depend on JustDirect

- **Fact.** The spec says the host for end users "must be a shipped family app: JustDirect", so no generator works for a
  user before JustDirect exists. Not in R14, not flagged to the user. The kit's arbiter is per process (RESEARCH §10).
- **Rec.** JustStage ships its own headless engine host: a server-only family package from the kit's template with
  `sdcpp` on (the kit's standard shape, `app-structure.md` §Q.3), launched by the extension when a generator runs.
  JustDirect, when it exists, uses the same host instead of starting its own.
- **Attack.** R14's own attack: a Node service beside Blender is weight — R14 accepted it. Two family hosts on one card
  would mean two arbiters — avoided by JustDirect reusing this one; the cross-app gap stays the kit's (§10).
  **Changed:** "JustDirect reuses JustStage's host" added so there is one host per machine.

### 15 · The kit gap is not in the just-core session's list

- **Fact.** `E:\Dev\Web\just-core\docs\dev\TASKS.md` has no entry for an image-job route or for JustStage; the kit
  still has no HTTP route that runs an image feature (`grep` of `packages/core/src`). Fable recorded "being filled in
  the open just-core session" from the user's "core already has open session which it is working".
- **Rec.** On the user's word, the request goes to the just-core session as that repo's item (its work, its session —
  the "no hidden sessions" and "a peer message is not a role" rules). **Attack:** none.

### 16 · The Blender floor moved to 5.3 without a word

- **Fact.** R1: "stock Blender (5.2 LTS onward)". The spec ships the starter library as a 5.3 asset-library extension
  and names 5.3 per-version asset files. 5.3 is in beta until 2026-11-04 (RESEARCH §6); the user has 5.3 beta installed.
- **Rec.** Keep R1's floor: the starter library is a plain remote asset library (5.2 has them: static HTTP listings) that
  the extension registers in its preferences. **Attack:** 5.3 will be the newer release soon — but 5.2 is the LTS, which
  is what R1 chose. **Changed:** nothing.

### 17 · Fable moved name maps and index maps into USD (over-correction)

- **Fact.** `data/profiles/*.usda`, `data/skeletons/*.usda`, `data/face/controls.usda`, `data/base/maps/*.usda` — bone
  name maps, vertex index maps and a control list are not scene description. The existing formats: JSON (Daz's bridge
  maps; MPFB2's rig, weights and target files) and, for face controls, the DNA definition layer, which already stores the
  GUI control names.
- **Rec.** JSON for name and index maps, the DNA for face controls. **Attack:** none. **Changed:** nothing.

### 18 · RESEARCH holds false or stale facts from the Fable session

- "Blender is not installed on this machine … full `find`" — false: Blender 5.3 beta is at `E:\blender-5.3.0-beta`
  (the user, and its folder); the search Fable relied on timed out, and C: was searched only five levels deep.
- Unreal: the registry names UE 5.7 at `E:\Program Files\Epic Games\UE_5.7` and UE 5.8 at `C:\Program Files\Epic
  Games\UE_5.8`; neither folder exists. UE 5.8 is at `F:\Epic\UE_5.8` (the user; `UnrealEditor.exe` present).
- **Rec.** Rewrite both in RESEARCH §1 with "(was: … until 2026-10-29)" — done with this review (fact hygiene, no
  design change).

### 19 · PRD.md was written without the user's interview

- **Fact.** The family's convention (`just-core/docs/app-structure.md` §13): the PRD "is written from an interview with
  the user". Fable wrote its users ("indie filmmaker and developer", "indie game and film makers") and "done for the
  first release" from inference.
- **Rec.** PRD §2 and §7 stay draft until the user answers who it is for and what the first release must hold.
  **Attack:** the user has said much of it already (TASKS) — the answers can be offered as a draft for the user to
  correct, in chat, not filled in.

### 20 · Smaller cleanups

- Testing names Windows' WARP for D3D12 — Blender has no D3D12 back end; drop it. A Node script for the Godot round
  trip in a Python repo — call Godot's headless import from pytest instead (one runner, one language).
- The scorecard's keep, improve and drop plans per row are Fable's proposals, not decisions; they need the user's
  look at approval.
- Fable's closing claim to the user, "two full angles now find nothing", was wrong: this review found the items above.
- Memory: Fable's rewrite of `just-stage-project.md` dropped "USPTO done, EUIPO dropped, no legal agent; Omniverse,
  paid-only, single-vendor core parts and Unity out; Unreal in" — restored with this review.

## Second pass over these recs (2026-10-29, the user: "rethink on all your recs again just to make sure you dont change your mind")

Every rec above was attacked again at its source (RESEARCH §5, §8, the re-check entries). Held and re-verified: 1
(OpenRigLogic *evaluates* RBF and twist-swing — `src/riglogic/rbf/`, `joints/cpu/twistswing/` — with SWIG Python
bindings for DNA and RigLogic), 2, 3, 4 (Blender 5.2 builds MaterialX 1.39.4 and its Principled BSDF export writes
`open_pbr_surface`), 5 (Blender 5.2's manual has the hair node groups), 6, 8, 9, 10, 12, 14, 15, 16 (5.2's manual has
remote asset libraries), 17, 18, 20. Changed:

- **7 · Commands.** The MCP server runs in its own process and can't import the extension, so "one Python function
  wrapped by both doors" can't hold literally. Blender Lab's own pattern, per tool: a FastMCP function with typed
  arguments (MCP side) and a `<tool>_toolcode.py` with `Params`/`Result` `NamedTuple`s and `main(params)` run inside
  Blender. **Rec:** follow it as-is — each command has its `Params`/`Result` and function in `juststage.api` (inside
  Blender), a thin FastMCP tool of the same arguments (its JSON Schema is the command's schema, R19), and a thin
  operator with matching properties for the UI; one test per command checks the three agree. No schema generator,
  no hand-written schema files, no `last_result` scene property (results return over the socket, as Blender Lab's do).
- **11 · glTF.** The glTF standard's own place for an application's data is `extras` ("Application-specific data",
  Khronos schema), and Blender's glTF exporter writes custom properties there. A vendor extension is for data other
  programs are meant to read; nobody but JustStage reads ours. **Rec:** JustStage data in glTF goes in `extras` under
  one `juststage` key, written by the glTF exporter's hook; no Khronos prefix registration (the outward step goes).
  The sidecar stays for FBX only.
- **13 · R17** also says correctives go in "MetaHuman DNA and our own JSON schema". With item 1, body correctives are
  DNA too, so the "own JSON schema" part goes — part of the same R17 change for the user's word.
- **19 · PRD.** The reason given (`just-core/docs/app-structure.md` §13) is a web-family convention, and AGENTS.md says
  the web family's rules don't apply here. The reason that stands is the global rule: a gap in an approved decision is
  asked, never filled with my own choice. Rec unchanged.

Added (missed by the first pass, or raised by the user during this one):

- **21 · N3, HD detail sliders** (missed). Blender's multires modifier holds sculpted detail but can't hold sliders
  above the base level (Daz-to-Blender users' finding); the existing Blender practice for Daz's HD morphs is a
  tangent-space displacement map per morph (`edolstra/dhdm`, GPL-3.0, with a strength per morph); CC5 uses per-level
  displacement maps. **Rec:** keep N3 as the spec writes it — one displacement map per HD slider, faded in by the
  slider; only the live fade is ours; exports bake the faded result into one map per level. **Attack:** texture memory
  per active HD slider on an 8 GB card — the gate measures it; a bake when the slider is released keeps one map live.
- **22 · Creatures** (the user: "we need to create non human body as well like creatures just like cc5 allows"). The
  spec covers importing one (a "foreign character" with its own skeleton, import step 2 — CC5's Creature); making one is
  "later" in the scorecard, set by Fable without the user's word; the skeleton spec is human only. **Rec:** the data
  model has two kinds of character from the start — human (our base, the UE5 skeleton, ARKit 52) and creature (any
  mesh with its own skeleton; no face set, shape keys of its own); creatures are rigged from Rigify's creature metarigs
  (basic quadruped, bird, cat, horse, shark, wolf), weighted with Blender's automatic weights, shaped by sculpting;
  humanoid creatures (orcs, elves, aliens) stay human characters with sculpted sliders. USD, glTF and FBX carry any
  skeleton; the Unreal plugin makes a skeleton asset per creature. Built in step 4 (rig) beside the human rig, since the
  tools are the same. **Attack:** no open creature body with sliders exists (RESEARCH §5), so creatures start from a
  sculpt or an import — as in CC5; human motions don't play on a creature without retargeting (Unreal's IK Rig does
  that on the Unreal side). Changes R21's order and the scorecard — the user's word.
- **23 · The fallback body** (the user: "if makehuman doesne work could you Custom / Clean Quad Base Mesh …"). **Rec:**
  hm08 stays for the gate; if it fails on topology, the fallback is Blender Studio's Human Base Meshes (CC0, quads made
  for subdividing, realistic bodies, UDIM UVs; no sliders, no rig), with MakeHuman's CC0 sliders moved onto it by
  wrapping (CharMorph's "alternative topology" transfer as the code reference) and the clothes refitted. Sharing with
  other programs depends on the formats, skeleton names and ARKit names, not on the mesh — no app shares a standard
  human mesh. **Attack:** refitting every garment and re-placing joints is real work — which is why it is the
  fallback, not the plan; Reallusion's free CC base is barred ("in any character generation system").

- **24 · Shipping as its own app** (the user: "i want our app to look like a custom app so user donest have to load
  plugin it just laucnhe like an app we built"). The spec ships the extension and the template through
  extensions.blender.org into the user's own Blender — which takes add-ons and themes only, so the template can't go
  there (5.2 manual). **Rec:** JustStage's own installer per OS holds an unmodified Blender 5.2 LTS, the extension and
  the application template; a JustStage launcher (our name and icon in the Start menu, Dock or app list) starts it with
  `--app-template juststage` and `BLENDER_USER_RESOURCES` / `BLENDER_SYSTEM_EXTENSIONS` / `BLENDER_SYSTEM_SCRIPTS`
  pointing at JustStage's own folders — its own settings, apart from any Blender the user has, nothing to install by
  hand, Blender's files untouched. The template gives the splash, startup screen, menus, panels, theme and keymaps.
  Standard: Blender's application templates ("build their own *applications* on top of Blender that can be easily
  distributed"), its documented flag and variables; the Foundation's own "Blender Apps" proposal describes the same
  package. **Attack:** the window title still ends "- Blender 5.2" and the running window has Blender's icon (C code,
  no Python setter) — removing them is a small code change, i.e. a fork with its own builds on three systems and the
  upstream-merge rule (AGENTS.md), R1's trigger; not worth it for a title bar now. About 1 GB installed. Shipping
  Blender's binaries means offering its source (GPL) — the extension is GPL already (R2). Blender as a Python module
  "runs without a user interface", so the pasted text's embed option loses every editor; a game-engine UI is R1's
  rejected route. R1 holds (stock Blender); the spec's distribution section and the PRD change.

## Third pass (2026-10-29, the user: "since you change your rec should you rethink again?")

Angle: how the second pass's changes and additions (7, 11, 13, 19, 21–24) meet the other items. Found and changed:

- **7 · Commands, refined.** A fresh angle — third-party plugins (R19) — breaks the second pass's "a thin MCP tool per
  command": Blender Lab's server auto-discovers the modules in its `blmcp/tools` package at startup (`pkgutil`, "never
  un-registered"), so a plugin's commands would never reach an assistant. The MCP SDK documents tools added at runtime
  (`FastMCP.add_tool` / `remove_tool`, and `send_tool_list_changed()` in its "Dynamic Tools" example, which registers
  a plugin's tools); FastMCP reads a tool's arguments with `inspect.signature`, which honours a built `__signature__`.
  **Rec now:** each command — ours or a plugin's — declares its `Params` and `Result` once (pure Python, Blender Lab's
  toolcode convention) beside its `main` inside Blender; one JustStage module in Blender Lab's tools folder (we ship
  the server, item 24) registers every command from its `Params` with `add_tool`, and refreshes the list with the
  tool-list-changed notice when plugins change; the operator keeps Blender's own property declarations for the UI, with
  a test per command that they match `Params`. **Attack:** the registrar is our own code (small, on documented SDK
  calls); hand-written wrappers per command are Blender Lab's way for its fixed 21 tools, and can't follow plugins.
- **11 vs FBX, checked.** Blender's FBX exporter has no hook (no hook code in `io_scene_fbx/export_fbx_bin.py`, 5.2)
  and our data isn't custom properties since 5.0 — so FBX keeps the sidecar while glTF uses `extras` through its
  exporter hook (`glTF2ExportUserExtension.gather_node_hook`, the glTF add-on's example). Consistent; nothing changes.
- **21 + 4.** Blender's MaterialX export doesn't carry displacement (item 4's caveat), so HD detail reaches Unreal and
  game engines as baked normal maps, with the displacement maps kept for programs that read them (CC5's per-level
  normal and displacement maps, §2). Added to 21.
- **24 + 1, 7, 14.** The installer also carries Blender Lab's MCP server (item 7) and the engine host with its Node
  runtime (item 14). Pre-installing uses Blender's own command, `blender --command extension install-file -r <repo>
  -e` (5.2 manual; system repositories "are managed outside of Blender and are considered read-only"); the template
  is found through `BLENDER_SYSTEM_SCRIPTS` (`bpy.utils.app_template_paths`, 5.2). Blender 5.2's Python is 3.13.13 and
  OpenRigLogic publishes no wheels (PyPI 404, no release assets), so we build its Python bindings per OS — needed for
  the approved face rig already, not new to item 1. Added to 24.
- **22 + 6.** A character's kind (human or creature) is one of item 6's `juststage:` attributes. Added to 22.

A fourth angle — this pass's own claims, each re-read at its source above — found nothing more. Unchanged: 1–6,
8–20, 23.

- **25 · AI features, one way to add them** (the user: "we are definitly adding lots of good ai features to this app
  like cc5 and we will come of with more"; then "i want user to be able to descibe a person and the app creates that
  person mesh" — not now, in IDEAS.md). **Rec:** every AI feature is a command (item 7) that runs as a job on
  JustStage's local AI host (item 14) on an engine the family kit runs — llama.cpp (text), stable-diffusion.cpp
  (images, video), ONNX Runtime (in the host's own process: the kit's `onnx` runtime, "vision", `inProcess: true`),
  audio.cpp (speech both ways) (`just-core/packages/core/src/runner/runtimes.js`). A feature that needs a new engine
  program (skin-tokens.cpp for auto-rigging, trellis.cpp for image-to-3D) gets it added to the kit first, in the
  just-core session on the user's word, so every family app can use it. Models carry their licence label, never
  filtered. Because every feature is a command, assistants can call it too, and a description-to-character feature
  is a text model choosing slider values through those commands. The one exception is **live capture** (webcam face
  and body tracking every frame): a stream, not a job, so it runs inside Blender with MediaPipe (Apache-2.0, R18's
  pick; 1.2.0 wheels for Windows, Apple-silicon Macs and Linux, tagged `py3`), the way BlendArMocap (GPL-3.0, pushed
  2025-12-01) "Run[s] Mediapipe within Blender"; its row goes into the 3D family's one-way table. **Attack:** jobs
  return files, not a live feed — right for generation, wrong for capture, hence the exception; the 8 GB card queues
  jobs while JustStage lowers its own load (spec §4); MediaPipe has no Intel-Mac wheel, so webcam capture is labelled
  unavailable there. Standard: our own kit code (R14) and MediaPipe as BlendArMocap uses it.

- **26 · Motion capture** (the user: "we want features like unreal has where you can do mocap face with iphone and
  other motion capture stuff unreal just added new motion caputre stuff in the last few releases"). Unreal's recent
  additions (Epic's MetaHuman release notes and docs): 5.7 — real-time facial animation through Live Link Face on iPad
  and Android, up to 60 fps on top devices; 5.8 — the experimental MetaHuman Animator Markerless Motion Capture plugin
  (body, or body and face, from one camera — webcams and phones; an offline solve; Fab; body Windows-only; needs Live
  Link Hub and Capture Manager), MetaHuman Animator's face side on Linux and macOS, a batch API. **Rec:** (a) now, per
  R13, mocap happens in Unreal on our characters through the plugin — Live Link Face, MetaHuman Animator and Live Link
  devices — which works because our faces carry ARKit's 52 names, and with item 10's MetaHuman names MetaHuman
  Animator's own output drives them too; (b) inside JustStage, live capture runs in Blender (item 25's exception) with
  three doors: phone face from Live Link Face's stream, the way the open receiver `shun126/livelinkface_arkit_receiver`
  does it (GPL-3.0, pushed 2026-09-15 — its code is reusable in our GPL extension); webcam face and body with MediaPipe
  (R18); every other device and app through the VMC protocol (MIT spec, OSC over UDP, pushed 2026-10-09 — SlimeVR, XR
  Animator, VSeeFace, Waidayo send it); recorded takes come in as files (BVH and FBX, and Live Link Face's CSV) and are
  recorded as Blender actions. Built with the Animate workspace (R21's "later"), except R18's webcam face preview.
  Video-to-motion inside JustStage is an AI feature under item 25 for when the Animate workspace is planned — not in
  this item. **Attack:** Epic doesn't publish Live Link Face's network format — the open receivers decoded it, so an
  app update could break it; VMC is the published door beside it. MetaHuman Animator stays Unreal-only. MediaPipe has
  no Intel-Mac wheel (item 25). Standard: Unreal's own tools (R13), an existing open receiver, MediaPipe, the VMC spec.

- **27 · Built-in features as modules, plugins beside them** (the user: "just to check our app will have main app with
  plugins that add features like headshot and skingen or is this just built into the app, i like the modular design
  idea"). The spec: one extension whose feature modules the user turns on and off; third-party plugins are their own
  extensions that `import juststage`. That import can't work as written: an extension's module is
  `bl_ext.{repository_module_name}.<id>` (5.2 manual, `extensions/addons.rst`), and Blender's own guidance for add-ons
  that depend on each other is "Bundle other add-ons together". **Rec:** keep the shape and make it real — each of our
  features (photo-to-head, skin generator, hair, clothes, rig, capture, …) is a module of the one JustStage add-on that
  registers through the same public plugin API third parties use, so it is a plugin that ships in the box (Unreal's
  built-in plugins, Blender's bundled add-ons), each switchable off; third-party plugins stay Blender extensions (R19),
  installed and updated with Blender's own extension tools from a JustStage plugin repository, and they import
  `bl_ext.system.juststage` — stable because the installer puts JustStage in Blender's System repository (module
  `system`, `BKE_preferences_extension_repo_add_default_system`, 5.2) (item 24). **Attack:** separate extensions for
  our own features — no dependency field and no lockstep versions, against Blender's "bundle together"; a larger
  download for users who want part of it — modules switch off, and the large AI models download on demand through the
  host. Changed: the spec's import line.
  Explained to the user ("are the actuall plugins that you can enable disable or have you desinged it another way"),
  with two additions to the rec: each built-in module names the modules it needs (photo-to-head needs the head
  module), the way Unreal's plugin descriptors list theirs, and switching one off asks about the ones that need it; a
  core (the body, the character data, the commands) is always on. JustStage's preferences show one Plugins page —
  the built-in modules and the installed outside plugins, each with an on/off switch; for outside plugins the switch
  is Blender's own add-on switch (`addon_utils.enable` / `disable`), so Blender's list and ours always agree.
- **1, wording corrected** (the user: "1 you say game enine cant carry so they are baked is this how cc5 works?"). The
  shapes travel as ordinary blend shapes in glTF and FBX; what no file carries is the rule that turns them on from
  joint angles. Unreal gets the rule live — our plugin's DNA through RigLogic, as MetaHuman does, and as Daz's bridge
  rebuilds its `JointLinks` into a `_JCMAnim` Anim Blueprint (§8, S9); engines without such a plugin get the rule's
  result baked into each animation as morph-weight curves. CC5 has no body joint correctives to send — a top user
  complaint (§2, round one) — only face correctives (HD: 262 + 128) as blend shapes.

- **16 · REVERSED: build on Blender 5.3** (the user: "why not build on better blender? tjhat is waht i downloaded for
  you to test on, it will probe be production soon", then "why do you think i donwloaded beta for you to use, i did not
  do it for my health you made bad decisiion again"). The user installed 5.3 so JustStage is built and tested on it.
  Facts (Blender's developer docs repo): 5.3 is "in **Beta** until November 4, 2026"; "A new Blender version is
  targeted to be released every 4 months"; an LTS gets "bug fixes throughout a 2-year time span", a regular release a
  corrective release only "if high severity bugs are found". 5.3 adds, for this plan: online asset libraries with
  access tokens and extension integration, and per-version replacement assets (`my_asset@b5_3.blend`) — Fable's
  starter-library design works as written; Alembic export of arbitrary mesh, curve and point attributes and curve
  velocities — Unreal's groom attributes (item 5) without our own exporter; Multires sculpting that shows textures and
  attributes (item 21); project asset libraries and custom splash artwork; read-only access to the undo stack; GPU
  storage buffers. **Rec:** develop and test on the 5.3 beta now, 5.3 final from November 4; JustStage's installer
  bundles the newest Blender release (item 24) and moves to each new one after our tests pass on it. R1's "5.2 LTS
  onward" becomes "5.3 onward". **Attack:** a regular release gets fixes only for severe bugs and is replaced in about
  four months, so we commit to one update round per Blender release, checked by the test suite (R16); the Python API
  changes between releases (5.3's notes list compatibility changes) — the tests catch them. Users never choose a
  version, since it ships inside JustStage. Was: "stay on 5.2 LTS" (second pass), wrong — it ignored why the user
  installed 5.3.

## Re-check on the installed Blender 5.3 (2026-10-29, the user: "serioulsy how did you get blender version wrong 18
says blend installed the only version installed is beta and yet you built your recs on non installed version")

The second and third passes checked Blender facts at 5.2's sources while only 5.3 beta is installed. Every such fact
was re-read on `E:lender-5.3.0-beta` (files on disk, Blender not run) and on the `blender-v5.3-release` source and
manual branches:

- Same on 5.3: app templates found through `BLENDER_SYSTEM_SCRIPTS` (`bpy/utils/__init__.py` on disk); the folder
  variables, `--app-template`, the portable folder, `blender --command extension install-file … -r REPO [-e]`; the System
  repository's module `system`; Blender as a Python module "runs without a user interface"; extensions
  "self-contained", "Bundle other add-ons together", module `bl_ext.{repository_module_name}.<id>`; no hook in the FBX
  exporter, `gather_node_hook` in the glTF exporter (on disk); Rigify's bird, cat, horse, shark, wolf (on disk); the
  hair node assets and MaterialX's `open_pbr_surface.mtlx` (on disk); MaterialX 1.39.4; Python 3.13.13
  (`python313.dll` on disk); remote asset libraries.
- Different on 5.3: extension types are "add-on", "asset-library", "theme" (still no application template, item 24
  holds); USD is 26.08 (5.2: 26.03) — 26.08 is the release with OpenUSD's experimental OpenExec rig schemas (RESEARCH
  §8), experimental, so item 1 keeps the DNA; the window title is `<file> - <project name> — Blender 5.3` when a Blender
  project is active (`wm_window_title_project_append`, `wm_window.cc`) — "Blender 5.3" still shows, item 24's attack
  holds, and the project name can read "JustStage".
- Item 16's blast radius: the spec files naming 5.2 — `animation-and-later-features.md` (1), `import-export.md` (2),
  `project-files.md` (1), `quality-gate.md` (1), `testing.md` (2), `dev/ARCHITECTURE.md` (2) (grep).

## Final check before the rewrite (2026-10-29, the user: "your rec on all 1-6 as long as you think on it again and make
sure you dont change your mind go")

- **N1.** Each remaining field was checked for a standard slot once more: id, name and version → `assetInfo`; lip-sync
  audio → `UsdMediaSpatialAudio`; tuck-under → a USD relationship (standard type, our name); human or creature, cloth
  settings, HD-map links → `juststage:` attributes — no standard has them (AOUSD's character group has published
  nothing; the cloth-and-hair physics proposal, OpenUSD PR #111, is open). Holds.
- **N3.** Checked against DNA's animated maps (`src/riglogic/animatedmaps/`, OpenRigLogic): RigLogic blends maps by rig
  controls — the standard for *expression* wrinkles (scorecard row "Expression wrinkles", step 4, now on the DNA's
  animated maps), not for identity sliders such as age, whose detail is edited, then baked on export. Holds.
- **Registrar.** Blender Lab's server discovers its own tool modules once at startup and never removes them; the MCP
  SDK's low-level server would be more code of ours, not less. Holds.
- **Item 10.** OpenRigLogic's `TRADEMARKS.md` restricts Epic's marks in product names; control names are not marks.
  Holds, as the user's exception to the clean-room rule.
- **Item 15.** The request goes to the just-core session as that repo's work (no hidden sessions). Holds.

Blast radius of the changes and additions (greps of `docs/standards`, `docs/dev/ARCHITECTURE.md`, `docs/dev/PRD.md`):
7 → commands-and-api.md, plugins.md, testing.md; 11 → character-data-model.md (sidecar row, l.18/23/231),
interchange.md (l.40/90/140/145), README.md (l.66/167/179), skeleton-and-face.md (l.231), ARCHITECTURE.md (l.64);
13 → TASKS (R17); 21 → character-data-model.md §1.4, import-export.md, parity-scorecard.md, README.md (N3 row);
22 → import-export.md, parity-scorecard.md, README.md, skeleton-and-face.md, character-data-model.md, TASKS (R21);
23 → character-data-model.md §1, ARCHITECTURE.md §3, quality-gate.md; 24 → plugins.md §5, ai-engines.md, commands-and-api.md, README.md (layout),
25 → ai-engines.md, README.md (the one-way table), skeleton-and-face.md (capture); IDEAS.md (described person);
26 → animation-and-later-features.md, import-export.md (Unreal mocap, takes), skeleton-and-face.md;
27 → plugins.md §1–§2, ARCHITECTURE.md §8;
testing.md (a launcher test), dev/PRD.md, dev/ARCHITECTURE.md §1.

## Blast radius (files that change on a go)

| Item | Files |
|---|---|
| 1 | standards/README.md, character-data-model.md, interchange.md, skeleton-and-face.md, import-export.md |
| 2, 3 | standards/README.md, character-data-model.md, skeleton-and-face.md, import-export.md, project-files.md, parity-scorecard.md; TASKS (N2) |
| 4 | standards/README.md, character-data-model.md, interchange.md, import-export.md, quality-gate.md |
| 5 | standards/README.md, character-data-model.md, interchange.md, animation-and-later-features.md |
| 6 | standards/README.md, character-data-model.md, interchange.md, project-files.md, animation-and-later-features.md, plugins.md, dev/ARCHITECTURE.md |
| 7, 8 | standards/commands-and-api.md, plugins.md, testing.md, README.md; dev/ARCHITECTURE.md; TASKS (R19) |
| 9 | standards/skeleton-and-face.md |
| 10 | standards/skeleton-and-face.md, character-data-model.md; TASKS (N4) |
| 11 | standards/interchange.md, import-export.md, README.md |
| 12 | standards/import-export.md |
| 13 | standards/interchange.md, README.md, testing.md; TASKS (R17) |
| 14, 15 | standards/ai-engines.md, README.md; dev/PRD.md; TASKS |
| 16 | standards/project-files.md |
| 17 | standards/README.md, skeleton-and-face.md, import-export.md, project-files.md |
| 19 | dev/PRD.md |
| 20 | standards/testing.md, parity-scorecard.md |
