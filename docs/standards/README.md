# JustStage — the standards spec

> **Status: APPROVED recs, written 2026-10-29.** AGENTS.md: "The data model, the command API, the plugin contract and
> the file format are specified and approved before any code is written." The approvals, verbatim in
> [`../dev/TASKS.md`](../dev/TASKS.md): the rec list R1–R21 ("go your rec all"); the Opus review's recs 1–27 ("i agree
> with your recs"); and the go on the rewrite and five named items ("your rec on all 1-6 as long as you think on it again
> and make sure you dont change your mind go"). The first draft was the Fable session's; this version is rewritten to
> the review ([`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md), its items cited as
> "item N") — §6 lists what changed. Facts: [`../dev/RESEARCH.md`](../dev/RESEARCH.md); Blender facts are checked on the
> installed Blender 5.3. What JustStage is and why: [`../dev/PRD.md`](../dev/PRD.md),
> [`../dev/ARCHITECTURE.md`](../dev/ARCHITECTURE.md).

## 1 · The documents

| Doc | Covers | Recs |
|---|---|---|
| [`character-data-model.md`](character-data-model.md) | where the data lives (`.blend`, the USD package, the FBX sidecar); the dozen `juststage:` attributes; human and creature; the base (hm08 whole, two levels, three shape spaces in MakeHuman's target format); sliders from MakeHuman's `target.json`; HD detail; materials (OpenPBR through Blender's exporter) and the texture set; hair (Blender's hair nodes); clothes (MHCLO); identity and versioning | R4, R5, R7, R8, R17 |
| [`skeleton-and-face.md`](skeleton-and-face.md) | the UE5 skeleton by its own names, built on MPFB2's UE-named rig and joint cubes; every name table; ARKit 52, visemes, the DNA face rig by MetaHuman's names; body correctives in a body DNA; live capture | R9, R18 |
| [`interchange.md`](interchange.md) | axes and units; the USD package and scenes; glTF + VRM with `extras`; FBX (Blender's exporter) and its sidecar; Alembic; formats by job | R17, R11, R12 |
| [`project-files.md`](project-files.md) | what a user saves; the asset library (Blender 5.3's, local and remote, an asset-library extension); versioning; logging, settings, errors | R6 |
| [`commands-and-api.md`](commands-and-api.md) | one declaration per command (`Params`, `Result`, `main`), the operator, the four doors; Blender Lab's MCP server with the command registrar; permissions | R19 |
| [`plugins.md`](plugins.md) | one add-on with built-in modules on the public plugin API; outside plugins; outside programs; distribution as JustStage's own app | R19, R2, R1 |
| [`import-export.md`](import-export.md) | the four import steps; CC5, Daz, MetaHuman, VRM, Unreal, MakeHuman, Mixamo rules; export presets; the Unreal plugin's contract, compatible skeletons and the keep-animation rule; mocap in Unreal | R11, R12, R13 |
| [`animation-and-later-features.md`](animation-and-later-features.md) | clips, layers, timeline, poses, lip-sync, takes, USD animation — defined now; the extension point of every later feature | R13, R6 |
| [`ai-engines.md`](ai-engines.md) | one way to add an AI feature; JustStage's own engine host from the kit's template; the client contract; the kit gap (requested); the 8 GB rule; models labelled | R14 |
| [`testing.md`](testing.md) | the rules and levels of tests for AI agents; one runner; platforms and CI (manual); fixtures; tools | R16 |
| [`quality-gate.md`](quality-gate.md) | what is built for the gate, the comparison set, the renders, the measurements, the verdict | R3 |
| [`parity-scorecard.md`](parity-scorecard.md) | CC5's inventory as rows with plan (proposals), step, status and proof; the floor that only rises | R21 |

## 2 · How a piece is marked

Every piece names the **standard** it follows with its doc link (an official spec, a maintained project's documented
format or code, or our own existing code in the web kit), or is marked **NOT STANDARD** with the standard option and the
trade-off beside it. A NOT STANDARD piece waits for the user's word on it **by name** (a blanket go never covers it).

| # | Piece | Where | Standard option | Trade-off | State |
|---|---|---|---|---|---|
| N1 | The names of the dozen `juststage:` attributes, the `juststage:hide` subset family and the `juststage` `customData` key | data model §0 | none — AOUSD's character group has published nothing; the cloth-and-hair physics proposal is open | names of our own to version, against characters whose sliders, kind, rigs and garments have nowhere to go | **approved 2026-10-29** ("your rec on all 1-6 … go") |
| N2 | ~~Shipping hm08 without its helpers and joint cubes~~ | — | — | — | **withdrawn** (item 2): hm08 ships whole, MakeHuman's way |
| N3 | The live fade of an HD slider's displacement map by the slider | data model §1.4 | a baked level-2 mesh per slider (214,000 offsets each), or ZBrush-style layers (Blender can't hold sliders above multires level 0) | texture memory per active HD slider, measured at the gate | **approved 2026-10-29** ("your rec on all 1-6 … go") |
| N4 | The face controls: ARKit 52 for interchange, the DNA rig by MetaHuman's control, joint and part names | skeleton §2.3 | ARKit 52 alone | none for interchange; MetaHuman's names are an exception to AGENTS.md's clean-room rule, names only | **approved 2026-10-29** ("4 fine …"; item 10: "your rec on all 1-6 … go") |
| N5 | ~~Body corrective fields of our own~~ | — | — | — | **replaced** (item 1): the DNA's RBF and twist-swing layers, a standard |
| N6 | The command registrar — the module that puts every command, ours and plugins', on the MCP tool list at runtime | commands §4 | Blender Lab's hand-written wrapper per tool | our own small module on the MCP SDK's documented calls; the wrappers can't follow plugins | **approved 2026-10-29** ("your rec on all 1-6 … go") |

Everything else is standard: Blender 5.3's data-blocks, PropertyGroups, operators, application templates, the USD hook
API, the glTF exporter's user extensions, asset libraries and asset-library extensions, workspaces, Multires, Curves
and the hair node groups, Cloth, slotted Actions and NLA, Rigify; MakeHuman's formats (targets, `target.json`,
`macro.json`, MHM, MHCLO, rig and weights JSON, expressions) and its CC0 data; Epic's DNA and OpenRigLogic; OpenUSD,
UsdSkel, UsdShade with MaterialX and OpenPBR, BasisCurves with Epic's GroomAPI, GeomSubsets, UsdMedia, `assetInfo`,
`customData`; glTF 2.0 with `extras` and VRM 1.0; FBX through ufbx in and Blender's exporter out; Alembic; the UE5
skeleton's names; ARKit's 52; Meta's and Microsoft's visemes; VRM's humanoid roles; MCP 2025-11-25 on Blender Lab's
server; MediaPipe; VMC; Unreal's plugin, Live Link, compatible skeletons and groom formats; the web kit's runner, jobs,
auth and port registry; pytest, Ruff, Blender's render tests; GitHub Actions (manual); REUSE for licences.

## 3 · One way per job — the 3D family's table

The user's global rule, appended 2026-10-29: "In the 3D family (E:\Dev\3D) the table is the one JustStage's standards
spec creates; until then there is none." Before designing anything in a 3D-family repo, find its job here and use what
it names; a plan names the row. Not here → search JustStage by what the job does; still nothing → it is new, and its
row goes into this table in the same change. **A second way to do a job this table already has is a bug.**
Paths are inside the `juststage` add-on unless they say otherwise.

| Job | Use | Never |
|---|---|---|
| **The app** | | |
| Shipping JustStage | one installer per OS: an unmodified Blender (the newest release, 5.3 now), the add-on, the template, Blender Lab's MCP add-on and server, the engine host ([`plugins.md`](plugins.md) §5) | asking users to install Blender and an add-on; a Blender fork for branding |
| Starting JustStage | the launcher: `--app-template juststage` + `BLENDER_USER_RESOURCES`, `BLENDER_SYSTEM_EXTENSIONS`, `BLENDER_SYSTEM_SCRIPTS` pointing at JustStage's folders | changing the user's own Blender settings |
| Which Blender | the newest release, moved to after the suite passes on it (R1 as changed: 5.3 onward) | building on a version that isn't installed here |
| **Data** | | |
| The live character | Blender data-blocks + hand-written `juststage` PropertyGroups | a parallel in-memory model; ad-hoc custom properties |
| A character for another program | `juststage.export.run` preset `package` → the USD package + `face.dna`, `body.dna`, the MHCLO files | a bare `.blend`, a bare FBX |
| JustStage fields no standard defines | the dozen `juststage:` attributes (N1) in USD, `extras.juststage` in glTF, the sidecar beside FBX | USD schemas of our own; a JSON beside USD or glTF |
| Writing and reading those fields | Blender's USD hook API; the glTF exporter's user-extension hooks | post-processing exported files; a second exporter |
| The kind of character | `juststage:kind` — `human` (the base, the UE5 skeleton, the DNA face) or `creature` (its own mesh and skeleton) | a creature forced onto the human skeleton |
| The base mesh | hm08 whole, helpers and joint cubes kept and masked, deleted at export (`data/base/`, frozen, `baseVersion`) | deleting the helpers; editing the base in place |
| A fallback base | Blender Studio's Human Base Meshes with MakeHuman's sliders wrapped on (only if the gate fails on topology) | a second base beside hm08 |
| A body or head shape | a MakeHuman target (`.target.gz`) in a shape space, driven by a slider | a vertex edit of the basis |
| Slider definitions | MakeHuman's `target.json` / `macro.json`, extended with our space groups | slider records inside characters |
| A character's slider values | `juststage:sliderIds` / `:sliderValues`; MHM `modifier` lines on MHM export | — |
| Scan-realistic ranges | the `mhr` and `gnm` shape spaces as MakeHuman targets (`data/targets/<space>/`) | a second body model |
| Fine detail | Multires per-level displacement + `displacement` EXR tiles; HD sliders (N3); baked normal maps for engines | normal-map-only detail on the base |
| The texture set | the master set, channels of data model §3.1, UDIM 1001–1006, 8K on disk, 2K/4K working resolution; every target is a bake from it | a second authored set per target; 8K in the viewport |
| A material | Principled BSDF / Principled Hair BSDF in Blender; in USD what Blender's exporter writes — UsdPreviewSurface + MaterialX `open_pbr_surface` (`chiang_hair_bsdf` for hair) | a shader network of our own; MDL |
| A generator's inputs (melanin, age, pores, …) | the generator preset, recorded in provenance | parameters stored on the material |
| Hair | Blender Curves with Blender's hair node groups; their inputs are the groom's settings; `groom_*` attributes; cards by `hair.bake_cards` | a groom schema of our own; cards as the source |
| A garment's fit | MakeHuman's MHCLO (`garments/*.mhclo`), refit on body change (LoBoFit on top) | fit arrays of our own |
| Garment layering | MHCLO `z_depth` / `juststage:layer`; `juststage:tuckUnder` | parenting a mesh to the body |
| Faces hidden under a garment | MHCLO `delete_verts`; a `UsdGeomSubset` (family `juststage:hide`) | a vertex-list blob |
| Skin weights | MPFB2's weights extended for UE5's bones; garments by transfer (`rig.transfer_weights`) | copying weights by hand |
| The skeleton | the UE5 skeleton by its own names in MPFB2's rig JSON v110 (`data/rigs/ue5.json`), joints placed by the `CUBE` strategy | a per-character bone list; our own spellings |
| A creature's skeleton | Mesh2Motion's CC0 creature rigs or Rigify's creature metarigs, Blender's automatic weights | the human skeleton bent to fit |
| Starter motions and sculpting bases | Mesh2Motion's CC0 animations (human ones retargeted onto the UE5 skeleton); Blender Studio's CC0 base meshes — both in the starter library | motions or bases of unknown licence |
| A bone's name in another program | the name tables (`data/skeletons/<source>.json`) through the export preset | renaming bones in the armature |
| Retargeting an import | `import.characterise` with a profile (`data/profiles/<source>.json`) | manual bone renaming |
| The face rig | `rig/face.dna` + OpenRigLogic, by MetaHuman's names (N4) | hand-made drivers on face shape keys |
| Face interchange | the ARKit 52 shape keys (MakeHuman's CC0 face units first), the 15 visemes | a target's names on the shape keys |
| Expression wrinkles | the DNA's animated maps | wrinkle drivers of our own |
| Joint correctives | `rig/body.dna`: the DNA's RBF and twist-swing layers, evaluated by OpenRigLogic | hand-made drivers; a corrective format of our own |
| Name and index maps | JSON files (`data/skeletons/`, `data/profiles/`, `data/base/maps/`) | scene-description files for lookup tables |
| Identity | `assetInfo.identifier` (UUID v4) | the display name as an id |
| Versioning | `juststage:formatVersion` + `schema_version` on the PropertyGroups + `juststage/migrations/v<N>.py`; `baseVersion` maps | silent format changes |
| Plugin or later-feature data | the plugin's own attribute namespace, or `customData` under a reverse-DNS key | new fields in the `juststage:` namespace |
| Provenance and licence | the `juststage` `customData` key on each asset prim; `assetInfo`; the library's licence label | an asset with neither |
| **Commands and API** | | |
| An action | a command module (`Params`, `Result`, `COMMAND`, `main`) + its operator, with a test that they match | an operator without a declaration; code in a panel's draw |
| Undo | Blender's `UNDO` flag; `ed.undo_push` after API calls | an undo system of our own |
| A long action | `jobs.start` → a job (modal timer in Blender; the engine host's jobs over HTTP) | blocking the UI |
| Python access | `juststage.api.run(...)` on `bl_ext.system.juststage` | `bpy.ops` strings scattered in callers |
| The command line | `juststage-cli` / `blender -b … --python-expr` with `--json` | per-script argument parsing |
| Remote control and AI agents | Blender Lab's `blender_mcp` as it is, MCP 2025-11-25, stdio or Streamable HTTP on 17480 | a second remote protocol; a fork of Blender Lab's server |
| JustStage's MCP tools | the command registrar in Blender Lab's tools folder (N6): every command from its `Params`, `add_tool` / `remove_tool`, the tool-list-changed notice | hand-written tool wrappers per command |
| Permissions | the API's tool groups, token, loopback rule, Python off by default | a tool that bypasses the groups |
| Live streams | MediaPipe in Blender, the Live Link Face stream receiver, VMC; the Unreal plugin's Live Link | frames as commands |
| **Plugins** | | |
| A feature of ours | a built-in module of the `juststage` add-on, registered through the public plugin API with its `needs`, switched on the Plugins page | a separate extension for our own features |
| A third-party plugin | its own Blender extension that imports `bl_ext.system.juststage` and calls `register_plugin` | `import juststage`; a custom manifest table |
| Switching plugins | the Plugins page (built-in modules + outside plugins; Blender's add-on switch underneath) | two lists that can disagree |
| An outside program | the MCP door | linking Blender |
| **Import and export** | | |
| Reading a file | `import.read` (Blender's ufbx FBX, glTF, USD, Alembic importers; our BVH) | a per-source parser |
| Making a foreign character ours | `import.characterise` → `import.wrap` → `import.materials` | a special path per source |
| Writing for a target | `export.run` with a preset (`data/presets/`) | per-target exporters with their own options |
| FBX out | Blender's exporter behind the preset (R17 as changed) | Autodesk's SDK |
| Grooms to Unreal | Alembic 1.5 attributes from Blender's exporter (+ USD GroomAPI) | cards unless the target has no strands |
| A character into Unreal | the JustStage Unreal plugin (`ImportCharacter`), its skeleton compatible with Epic's, re-import in place | a hand FBX import; modifying the user's `SK_Mannequin` |
| Mocap now | Unreal through the plugin: Live Link Face, MetaHuman Animator, Live Link devices (R13) | — |
| **Engines and jobs** | | |
| An AI feature | a command that runs as a job on JustStage's engine host, on an engine the kit runs; a new engine goes into the kit first | an engine started from Blender; an app's own engine code |
| An image feature's model and settings | the host's feature-catalog rows (`juststage.*` keys) | a model path in a preference |
| GPU memory beside a job | the 8 GB rule (working resolution, queue) | hoping |
| **Files and settings** | | |
| The working file | `.blend` | a project format of our own |
| The library | Blender asset libraries (local, remote static HTTP, the 5.3 asset-library extension), fixed catalogue UUIDs | a database |
| Settings | `AddonPreferences` in JustStage's own user folder; per-file in the scene group | JSON files beside the `.blend` |
| The log | `logging` under `juststage` | `print` |
| Errors | `report()` with the command id and field; non-zero exit headless | silent failure |
| Temp files | `bpy.app.tempdir` | the project folder |
| **Quality and tests** | | |
| Looks | golden images (Blender's render-test method) | eyeballing |
| The quality bar | the gate procedure, the user's verdict | a metric alone |
| A test, anywhere | pytest — plain CPython for Blender-free modules, `pytest.main()` inside Blender's Python for the rest; round trips driven from pytest | a second runner |
| A format's test | the round trip into its target | "it exported" |
| Parity | the scorecard and its floor | a feature list in prose |
| CI | GitHub Actions on manual dispatch | push or schedule triggers |
| **Docs** | | |
| A decision | `docs/dev/TASKS.md`, verbatim | chat memory |
| A fact | `docs/dev/RESEARCH.md` with how it was checked | a claim in a plan |
| A standard | this folder; a change to a standard lands with its test | a convention in one file's comments |

## 4 · Rules carried from the family

- **Licences are labels, never filters** (the user, JustVoice's way; extended 2026-10-29: a feature is never gated on
  a terms reading either): every model, dataset, asset and import shows its licence and GPU vendors; the user chooses.
- **Nothing builds by itself**: CI runs on `workflow_dispatch` only.
- **Clean-room**: CC5, iClone, MetaHuman and Daz are studied for behaviour and public docs; names never use
  "Character Creator", "iClone" or "Reallusion"; CC's base mesh is never our base. Bone names and file-format
  conventions are public interfaces, not content. **One exception, the user's** (item 10, approved 2026-10-29):
  MetaHuman's face control, face-joint and face-part names on our DNA face rig — names only.
- **Every change the user can see updates the user docs in the same change**; JustStage's user docs start with the
  first workspace (none exist yet — stated, not hidden).

## 5 · Repo layout the spec implies (for ARCHITECTURE.md; not code yet)

```
just-stage/
  extension/juststage/             the one add-on (GPL-3.0-or-later): blender_manifest.toml; juststage/ — core (api,
                                   commands, character fields, usd_hooks, gltf_hooks, migrations) and modules/<body|
                                   head_face|photo_to_head|skin|eyes|hair|clothes|rig|creature|capture|io|unreal_bridge|ai>;
                                   data/ (base, targets + target.json + macro.json, rigs, skeletons, profiles, presets, assets)
  template/juststage/              the Blender application template (splash, startup .blend, workspaces, keymaps, theme)
  mcp/juststage_commands.py        the command registrar, installed into Blender Lab's blmcp/tools/
  host/                            JustStage's engine host, a server-only family package from the kit's template
  installer/                       the per-OS installer and the launcher
  libs/                            MIT: generators, wrap and transfer code, the OpenRigLogic wheel build
  unreal/JustStage/                the Unreal plugin (MIT): JustStage.uplugin, Source/, Content/ (master materials)
  tests/                           unit, command, golden, roundtrip, api, install, versions, data
  docs/standards/                  this spec; docs/dev/, docs/plans/, docs/gate/
  LICENSES/                        REUSE layout: GPL-3.0-or-later, MIT, and the data licences (CC0, Apache-2.0)
```
Standards: [Blender extensions layout](https://docs.blender.org/manual/en/5.3/advanced/extensions/getting_started.html),
[application templates](https://docs.blender.org/manual/en/5.3/advanced/app_templates.html),
[Unreal plugins](https://dev.epicgames.com/documentation/en-us/unreal-engine/plugins-in-unreal-engine),
[REUSE](https://reuse.software/spec/) for a repo with more than one licence.

## 6 · What the Opus review changed (2026-10-29)

Each line: what Fable's draft had → what replaced it, with the review item.

1. Body corrective fields of our own (`JustStageCorrectiveAPI`, N5) → `rig/body.dna`, the DNA's RBF and twist-swing
   layers, evaluated by OpenRigLogic in Blender and by RigLogic in Unreal (item 1).
2. hm08 without its helpers and joint cubes (N2) → hm08 whole, helpers masked while editing and deleted at export;
   joints placed by MPFB2's `CUBE` strategy (item 2).
3. Slider prims, fit primvars and a face-unit plan of our own → MakeHuman's formats: targets, `target.json`,
   `macro.json`, MHM, MHCLO, rig and weights JSON, the CC0 face-unit and viseme packs, expressions (item 3).
4. A `juststage` shader network and render context → Blender's own MaterialX export, OpenPBR and Chiang hair (item 4).
5. `JustStageGroomAPI` → Blender's hair node groups; baked curves with Epic's GroomAPI in USD (item 5).
6. Nine applied-schema families, `schema.usda`, `usdGenSchema` and generated PropertyGroups → a dozen `juststage:`
   attributes (N1) written by the USD hook from hand-written PropertyGroups (item 6).
7. Hand-written JSON Schema files as the command source and a `last_result` scene property → Blender Lab's
   `Params`/`Result` convention, the operator mirroring it under test, results over the socket, the command registrar
   (N6) (items 7, third pass).
8. MCP 2026-07-28 → 2025-11-25, Blender Lab's server as it is (item 8; R19 as changed).
9. The Mixamo and CC name columns → fixed by humanoid role: `spine_01`/`spine_03`/`spine_05` (item 9; the CC column
   corrected again while rewriting — Reallusion's table the review cited was UE4's three-bone spine).
10. Face controls of our own → MetaHuman's names on the DNA rig, ARKit 52 for interchange (item 10).
11. A glTF sidecar → glTF's `extras` through the exporter's hook; the sidecar for FBX only (item 11).
12. A JustStage skeleton with no link to Epic's → compatible skeletons in Unreal (item 12).
13. FBX out through ufbx-write (R17) → Blender's exporter, made a silent R17 change by the draft, now approved (item 13).
14. Generators waiting for JustDirect → JustStage's own engine host from the kit's template (item 14).
15. "Kit gap being filled" → requested of the just-core session (item 15).
16. A 5.2 LTS base with 5.3 features → Blender 5.3 onward, the version installed here (item 16, reversed; R1 as changed).
17. USD files for name maps, index maps and the control list → JSON, and the DNA for controls (item 17).
18. False facts (Blender and Unreal "not installed") → corrected in RESEARCH §1 (item 18).
19. A PRD written without the user's interview → its users and first-release sections stay draft (item 19).
20. WARP/D3D12, a Node script for Godot, the scorecard's plans as decisions → dropped, pytest, proposals (item 20).
21. HD morphs (N3) → kept and approved; baked normal maps for engines; expression wrinkles as the DNA's animated maps
    (item 21).
22. Creatures "later" → human and creature kinds from the start, built in step 4 (item 22; R21 as changed).
23. — → a named fallback base (item 23).
24. Installing into the user's Blender from extensions.blender.org (where an application template can't go) →
    JustStage's own installer and launcher on an unmodified Blender (item 24).
25. — → one way to add an AI feature, live capture as the one exception (item 25).
26. — → motion capture in Unreal now, live capture doors in JustStage later (item 26).
27. `import juststage` (which can't work) and modules toggled in preferences → built-in modules on the public plugin
    API with `needs`, one Plugins page, `bl_ext.system.juststage` (item 27).
28. — → Mesh2Motion's CC0 creature rigs and animations, its human animations retargeted, and Blender Studio's CC0 base
    meshes as sculpting starting points, in the starter library (item 28; the user: "you have go on adding those
    things").
