# JustStage — the standards spec

> **Status: DRAFT, 2026-10-29 — for the user's approval.** AGENTS.md: "The data model, the command API, the plugin
> contract and the file format are specified and approved before any code is written." Nothing here is in force until
> [`../dev/TASKS.md`](../dev/TASKS.md) records the approval verbatim. Written by the Fable session from
> [`../dev/RESEARCH.md`](../dev/RESEARCH.md), [`../dev/TASKS.md`](../dev/TASKS.md) and the approved rec list
> [`../plans/2026-10-29-recs.md`](../plans/2026-10-29-recs.md) (R1–R21, approved 2026-10-29: "go your rec all").
> What JustStage is and why it is built this way: [`../dev/PRD.md`](../dev/PRD.md) and
> [`../dev/ARCHITECTURE.md`](../dev/ARCHITECTURE.md).

## 1 · The documents

| Doc | Covers | Recs |
|---|---|---|
| [`character-data-model.md`](character-data-model.md) | where the data lives (`.blend`, the USD package, the character JSON); the base (hm08, two levels, three shape spaces), morphs and sliders, HD detail, materials and the texture set (CC5's tiles, MetaHuman's slots), hair, clothes, identity and versioning | R4, R5, R7, R8, R17 |
| [`skeleton-and-face.md`](skeleton-and-face.md) | the body skeleton and every mapping table (VRM/Unity/Godot, UE5, HumanIK, Mixamo, Daz G8/G9, CC); the ARKit 52, visemes, the DNA face rig and its control vocabulary; the correctives schema; live capture | R9, R18 |
| [`interchange.md`](interchange.md) | axes and units; the USD package and scenes; glTF + VRM; FBX and Alembic; the companions; formats by job | R17, R11, R12 |
| [`project-files.md`](project-files.md) | what a user saves; the asset library (Blender's, local and remote); versioning so older files keep loading; logging, settings, errors | R6 |
| [`commands-and-api.md`](commands-and-api.md) | one command = one operator with a context-free `execute()` and one JSON Schema; the four doors; the MCP server built from Blender Lab's, with permissions | R19 |
| [`plugins.md`](plugins.md) | in-process plugins as Blender extensions (manifest, API); outside programs through the API; distribution | R19, R2 |
| [`import-export.md`](import-export.md) | the four import steps; CC5, Daz, MetaHuman, VRM, Unreal, MakeHuman, Mixamo rules; export presets; the Unreal plugin's contract and its keep-animation rule; "Send to Unreal as a MetaHuman" | R11, R12, R13 |
| [`animation-and-later-features.md`](animation-and-later-features.md) | clips, layers, timeline, poses, lip-sync, takes, USD animation — defined now; the extension point of every later feature (Animate, Scene, FX, patterns, sculpt extras, props, …) | R13, R6 |
| [`ai-engines.md`](ai-engines.md) | the family engine host named; the client contract; the kit gap; the 8 GB rule; models labelled | R14 |
| [`testing.md`](testing.md) | the rules and levels of tests for AI agents; platforms and CI (manual); fixtures; tools | R16 |
| [`quality-gate.md`](quality-gate.md) | what is built for the gate, the comparison set, the renders, the measurements, the verdict | R3 |
| [`parity-scorecard.md`](parity-scorecard.md) | CC5's inventory as rows with plan, step, status and proof; the floor that only rises | R21 |

## 2 · How a piece is marked

Every piece names the **standard** it follows with its doc link (an official spec, a maintained project's documented
layout, or our own existing code in the web kit), or is marked **NOT STANDARD** with the standard option and the
trade-off beside it. A NOT STANDARD piece waits for the user's word on it **by name** (a blanket go never covers it).
The NOT STANDARD pieces in this spec:

| # | Piece | Where | Standard option | Trade-off |
|---|---|---|---|---|
| N1 | The character JSON schema (correctives, sliders, wrinkle layers, groom settings, fit data, provenance), and its mirror as JustStage USD applied schemas | data model §0, interchange §2.2 | USD only | loses the data that makes a CC5-class character; no standard before 2027 at the earliest |
| N2 | Shipping hm08 without MakeHuman's helper geometry and joint cubes | data model §1.1 | hm08 whole | 5,778 dead vertices per character and morph for a fitting system we don't use; an index map keeps MakeHuman imports |
| N3 | HD morphs as displacement-delta tiles blended by the slider | data model §1.4 | multires sculpt layers only, no slider | texture memory per active HD slider; a bake before export |
| N4 | The face control vocabulary: ARKit 52 plus JustStage's own controls in ARKit's style | skeleton §2.3 | ARKit 52 alone / FACS / MetaHuman's names | mapping tables to MHA and CC5 HD, against every capture source driving the rig |
| N5 | The body correctives schema | skeleton §3 | none exists (Daz `JointLinks`, MetaHuman RBF are vendor-private) | a schema of our own, against collapsing joints |

Everything else is standard: Blender's data-blocks, PropertyGroups, operators, extensions, asset libraries, workspaces,
application templates, Multires, Curves, Cloth, Actions and NLA; OpenUSD/UsdSkel/MaterialX; glTF 2.0 and VRM 1.0; FBX
through ufbx and Blender's exporter; Alembic; OpenRigLogic; ARKit's 52; Meta's visemes; VRM's humanoid roles; JSON
Schema 2020-12; JSON-RPC 2.0; MCP 2026-07-28 on Blender Lab's server; VMC; Unreal's plugin, Live Link and groom
formats; the web kit's runner, jobs, auth and port registry; pytest, Ruff, Blender's render tests; GitHub Actions
(manual); REUSE for licences.

## 3 · One way per job — the 3D family's table

The user's global rule, appended 2026-10-29: "In the 3D family (E:\Dev\3D) the table is the one JustStage's standards
spec creates; until then there is none." Before designing anything in a 3D-family repo, find its job here and use what
it names; a plan names the row. Not here → search JustStage by what the job does; still nothing → it is new, and its
row goes into this table in the same change. **A second way to do a job this table already has is a bug.**
Paths are inside the `juststage` extension unless they say otherwise.

| Job | Use | Never |
|---|---|---|
| **Data** | | |
| The live character | Blender data-blocks + the `juststage` PropertyGroups generated from `schemas/juststage-character.schema.json` | a parallel in-memory model, ad-hoc custom properties |
| A character for another program | `juststage.export.run` preset `package` → the USD character package + companions | a bare `.blend`, a bare FBX |
| JustStage data USD has no schema for | `character.juststage.json` (schema N1) | new USD attributes without a `JustStage*API_N` schema |
| The base mesh and parts | `data/base/` (frozen, `base_version`) | editing the base in place |
| A body or head shape | a slider over shape keys (`body.save_slider`), a shape space for data-driven ranges | a vertex edit of the basis |
| Scan-realistic shape ranges | the `mhr` and `gnm` shape spaces (`data/spaces/`) | a second body model |
| Fine detail | Multires per-level displacement + `displacement` EXR tiles; HD sliders (N3) | normal-map-only detail on the base |
| The texture set | the master set, channels of data model §3.1, UDIM 1001–1006; every target is a bake from it | a second authored set per target |
| A material | the `JustStage *` node groups + the JSON `materials` parameters | a one-off node tree |
| Hair | Blender Curves grooms with the `groom_*` attributes; cards by `hair.bake_cards` | cards authored by hand as the source |
| A garment | a Mesh with the `garment` group (`layer`, `fit`, `hide_mask`, `sim`) | parenting a mesh to the body |
| Clothes following the body | the fit record + `clothes.refit` | Surface Deform / shrinkwrap modifiers left in the file |
| Skin weights | the body's weights by transfer (`rig.transfer_weights`) unless authored | copying weights by hand |
| The skeleton | `js_humanoid` (skeleton §1.1), `DEF` collection, `.L/.R` names | a per-character bone list |
| A bone's name in a target | the mapping tables (`data/skeletons/*.json`) through the export preset | renaming bones in the armature |
| Retargeting an import | `import.characterise` with a profile (`data/profiles/`) | manual bone renaming |
| The face rig | `rig/face.dna` + OpenRigLogic; controls from `data/face/controls.json` (N4) | hand-made drivers on face shape keys |
| Face interchange | the ARKit 52 shape keys (always present), the 15 visemes | a target's names on the shape keys |
| Joint correctives | the `correctives` schema (N5) → generated drivers | hand-made drivers |
| Identity | `character_id` (UUID v4) | the display name as an id |
| Versioning | `schema_version` + `juststage/migrations/v<N>.py`; `base_version` maps; `_N` USD schema families | silent format changes |
| Unknown or plugin data | `extensions[<reverse-DNS>]` | new top-level fields without a schema bump |
| Provenance and licence | the `provenance` records and the library's `licence_label` | an asset with neither |
| **Commands and API** | | |
| An action | a `@command` operator with a context-free `execute()` and a JSON Schema | an operator without a schema; code in a panel's draw |
| Undo | Blender's `UNDO` flag | an undo system of our own |
| A long action | `jobs.start` → a job (modal timer in Blender; the engine host's jobs over HTTP) | blocking the UI |
| Python access | `juststage.api` (typed wrappers from the schemas) | `bpy.ops` strings scattered in callers |
| The command line | `juststage <command> --json` (headless Blender) | per-script argument parsing |
| Remote control | JSON-RPC 2.0 on the add-on socket (17480) | a second socket protocol |
| AI agents | `juststage-mcp` (Blender Lab's server shape; tools generated from the schemas) | hand-written tools |
| Permissions | the API's tool groups, token, loopback rule, Python off by default | a tool that bypasses the registry |
| Live streams | the VMC/OSC receiver and the Unreal plugin's Live Link; `face.capture_start` | frames as commands |
| **Plugins** | | |
| A feature of ours | its own Blender extension depending on `juststage` | a monolith |
| A third-party plugin | a Blender extension with the `[juststage]` manifest table; `js_<name>.*` commands | a Python file dropped in a folder |
| An outside program | the API door | linking Blender |
| **Import and export** | | |
| Reading a file | `import.read` (Blender's ufbx FBX, glTF, USD, Alembic importers; our BVH) | a per-source parser |
| Making a foreign character ours | `import.characterise` → `import.wrap` → `import.materials` | a special path per source |
| Writing for a target | `export.run` with a preset (`data/presets/`) | per-target exporters with their own options |
| FBX out | Blender's exporter behind the preset; ufbx-write once the round trips pass | Autodesk's SDK |
| Grooms to Unreal | Alembic 1.5 attributes (+ USD GroomAPI) | cards unless the target has no strands |
| A character into Unreal | the JustStage Unreal plugin (`ImportCharacter`), re-import in place | a hand FBX import |
| **Engines and jobs** | | |
| An image model | the family engine host over HTTP (`ai-engines.md` §3) | starting sd.cpp from Blender |
| An image feature's model and settings | the host's feature catalog rows (`juststage.*` keys) | a model path in a preference |
| GPU memory beside a job | the 8 GB rule (viewport texture limit, queue) | hoping |
| **Files and settings** | | |
| The working file | `.blend` | a project format of our own |
| The library | Blender asset libraries (local, remote static HTTP), fixed catalogue UUIDs | a database |
| Settings | `AddonPreferences`; per-file in the scene group | JSON files beside the `.blend` |
| The log | `logging` under `juststage` | `print` |
| Errors | `report()` with the command id and field; non-zero exit headless | silent failure |
| Temp files | `bpy.app.tempdir` | the project folder |
| **Quality and tests** | | |
| Looks | golden images (Blender's render-test method) | eyeballing |
| The quality bar | the gate procedure, the user's verdict | a metric alone |
| A command's test | headless, from JSON params | a UI script |
| A format's test | the round trip into its target | "it exported" |
| Parity | the scorecard and its floor | a feature list in prose |
| CI | GitHub Actions on manual dispatch | push or schedule triggers |
| **Docs** | | |
| A decision | `docs/dev/TASKS.md`, verbatim | chat memory |
| A fact | `docs/dev/RESEARCH.md` with how it was checked | a claim in a plan |
| A standard | this folder; a change to a standard lands with its test | a convention in one file's comments |

## 4 · Rules carried from the family

- **Licences are labels, never filters** (the user, JustVoice's way): every model, dataset and asset shows its licence
  and GPU vendors; the user chooses.
- **Nothing builds by itself**: CI runs on `workflow_dispatch` only.
- **Clean-room**: CC5, iClone, MetaHuman and Daz are studied for behaviour and public docs; names never use
  "Character Creator", "iClone" or "Reallusion"; CC's base mesh is never our base.
- **Every change the user can see updates the user docs in the same change**; JustStage's user docs start with the
  first workspace (none exist yet — stated, not hidden).

## 5 · Repo layout the spec implies (for ARCHITECTURE.md; not code yet)

```
just-stage/
  extensions/juststage/            the core extension (GPL-3.0-or-later): blender_manifest.toml, juststage/ (api, commands, schemas, migrations, io, engines), data/
  extensions/juststage_<area>/     body, head, skin, hair, clothes, rig, io, unreal_bridge
  template/                        the Blender application template (splash, startup .blend, workspaces, keymaps, theme)
  libs/                            MIT: the character schema tools, generators, wrap and transfer code, ufbx-write bindings
  unreal/JustStage/                the Unreal plugin (MIT): JustStage.uplugin, Source/, Content/ (master materials)
  mcp/                             juststage-mcp (the outside MCP process)
  tests/                           unit, command, golden, roundtrip, api, versions, data
  docs/standards/                  this spec; docs/dev/, docs/plans/, docs/gate/
  LICENSES/                        REUSE layout: GPL-3.0-or-later, MIT, and the data licences (CC0, Apache-2.0)
```
Standards: [Blender extensions layout](https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html),
[application templates](https://docs.blender.org/manual/en/latest/advanced/app_templates.html),
[Unreal plugins](https://dev.epicgames.com/documentation/en-us/unreal-engine/plugins-in-unreal-engine),
[REUSE](https://reuse.software/spec/) for a repo with more than one licence.
