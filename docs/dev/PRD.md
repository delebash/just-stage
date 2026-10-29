# JustStage — what the app is for (PRD)

> **Status: DRAFT, 2026-10-29 — for the user's approval**, with the standards spec
> ([`../standards/README.md`](../standards/README.md)). The synthesis of the research
> ([`RESEARCH.md`](RESEARCH.md)) and the approved recs ([`../plans/2026-10-29-recs.md`](../plans/2026-10-29-recs.md)).
> The family's PRD convention: who uses it, its features and how each is proven, the outside data and services, what
> is out of scope. Why it is built this way: [`ARCHITECTURE.md`](ARCHITECTURE.md).

## 1 · In one paragraph

**JustStage — characters, scenes, animation.** A free, open-source 3D character creator — what Character Creator 5
and its plugins do — that makes whole humans at CC5 and MetaHuman quality or better, pulls in characters from CC5,
Daz, MetaHuman, VRM and Unreal, and sends set-up characters to Unreal in one click. It runs as its own application on
top of stock Blender (an application template plus one extension with feature modules), on Windows, macOS and Linux, on any GPU vendor, with
an API every program and AI agent can call. Scenes and animation (iClone's side) come later in the same app; until
then Unreal, reached through JustStage's own plugin, and Blender's animation tools stand in. Every feature is built by
AI agents against written standards, with a measured quality gate before the features and a parity scorecard whose
floor only rises.

## 2 · Who it is for

| User | What they come for | What they must get |
|---|---|---|
| The user (indie filmmaker and developer; Unreal, Blender, CC5 and iClone on an RTX 2070 Super, 8 GB) | CC5's results without CC5's prices, Windows-only install, cloud credits and content lock-in; characters that go to Unreal with no retargeting | the quality bar, the Unreal pipeline, import of what they already own |
| Indie game and film makers on Unreal, Unity or Godot | rigged, textured humans with faces that take iPhone, webcam or MetaHuman Animator capture | glTF/VRM/FBX/USD out, ARKit-compatible faces, free licences shown |
| Blender artists | a character creator inside Blender that sculpts, grooms and clothes with Blender's own tools | the template's workspaces, Blender's data-blocks underneath |
| Pipeline developers and AI agents | a scriptable, remote-controllable app | one command = one JSON Schema; Python, CLI, JSON-RPC, MCP |
| JustDirect (the family's AI-film app, planned) | characters, scenes and render passes | the API and the USD package |

## 3 · Hard requirements (the user's words, TASKS)

- Quality: "the quality of cc5 and metahuman characters or better" for "all of the character realism hair the whole
  human", "like teeth lips" — **pass/fail**, judged at the quality gate.
- "pull in assest from other programs just like cc5 and unreal engine and daz studio" — importing is a requirement;
  "it will be ok to import cc model if unreal can do it we can".
- "the best of the best … if none of the existing stuff meets the quality bar … then we need to do are own" — reuse if
  it meets the bar, else build.
- "an api that user can connect to", "with plugin cpabalilty", "define standards for everything we do before we write
  code".
- Cross-platform: Windows, macOS, Linux. Open source: MIT preferred, LGPL-type components acceptable (the extension
  is GPL-3.0-or-later because Blender requires it — R2; libraries and the Unreal plugin are MIT).
- Out: Omniverse, paid-only products, single-vendor core parts, Unity as a base. In: Unreal; a Blender fork if ever
  needed.
- Features named: sculpting at ZBrush's level, making clothes, making props, the pipeline out to Unreal and other
  software, FX later — "we need to be able to add them in the orginal design".
- Headshot: "i definelty want headshot" — photo-to-head is step 3.

## 4 · Features and how each is proven

The scope now is the character creator (R21's order); each row names its proof (a test level of
[`../standards/testing.md`](../standards/testing.md) or the gate).

| # | Feature (workspace) | What the user does | Proof |
|---|---|---|---|
| 1 | **The quality gate** | sees one JustStage head beside a CC5 HD head and a MetaHuman in EEVEE, Cycles and Unreal, and judges it | [`quality-gate.md`](../standards/quality-gate.md): the report with the verdict |
| 2 | **Body** | shapes a body with sliders (MakeHuman's range, MHR's scan-based bodies), mixes characters, saves presets | slider and shape-space tests; golden images |
| 2 | **Head & Face** | shapes a head (GNM's scan-based heads), eyes, teeth, tongue; previews expressions | the same; the gate |
| 2 | **Skin & Materials** | generates skin (tone, age, pores, wrinkles, freckles, makeup layers) at up to 8K, eyes, lips, nails; edits layers; bakes | generator tests; golden images; the gate |
| 2 | **Hair** | generates and grooms scalp hair, brows, lashes, beards, body hair as strands; bakes cards | groom tests; golden images; the gate |
| 3 | **Photo-to-head / photo-to-body** (Headshot) | one or more photos → a head on our base with a completed texture; a photo → a body shape | fit-error tests; a compare sheet like the gate's |
| 4 | **Rig & Expressions** | gets a skeleton, a face rig with the ARKit 52 and the HD-class controls, correctives; auto-rigs an imported humanoid; poses; captures from webcam or iPhone | rig tests; capture tests; round trips |
| 5 | **Clothes** | fits garments (conform, layers, tuck-in, hide-under, weights), simulates, re-fits when the body changes | fit and refit tests; golden images |
| 6 | **Import / Export** | imports from CC5, Daz, MetaHuman, VRM, Unreal, MakeHuman, Mixamo, any humanoid; exports to Unreal (the plugin, keep-animation), glTF/VRM, FBX, USD, CC5, Unity, Godot, Maya | round-trip tests per preset; the plugin's Automation tests |
| 7 | **Sculpt extras** | sculpts morphs and HD detail; saves sculpts as sliders | command tests |
| 8 | **Making clothes from patterns** | sews 2D patterns into garments and simulates | tests when built |
| — | **The API** (every step) | drives all of the above from Python, the command line, JSON-RPC and MCP, with permissions | API contract tests |
| — | **The asset library** | stores characters, garments, grooms, presets with licence labels; browses remote libraries | library tests |
| later | **Animate**, **Scene**, **FX**, props, crowds, mocap devices | iClone's side | rows reserved in the scorecard; data defined now |

## 5 · Outside data, accounts and paid services

| Thing | Status | Where it shows |
|---|---|---|
| Open bases and data: MakeHuman hm08 and targets (CC0), MHR and SOMA-X (Apache-2.0), GNM (Apache-2.0), ICT-FaceKit (MIT), OpenRigLogic (MIT) | reused under their licences, labelled | provenance on every asset |
| Open image models: Z-Image-Turbo, Qwen-Image, FLUX.2 klein 4B (Apache-2.0), HiDream-O1 (MIT) | run locally by the family engine host; labelled | the generators' model picker |
| The family engine host (a web-kit server) | local, free | the AI preferences |
| Epic: Unreal Engine, MetaHuman, Fab | the user's Epic account; Epic's terms; "Send to Unreal as a MetaHuman" uses Epic's cloud and is optional | the plugin; a labelled button |
| The user's own CC5, Daz, MetaHuman exports | imported under their terms, kept out of shared libraries where terms require | import dialogs show the label |
| No accounts, no cloud credits, no store of JustStage's own | — | — |

## 6 · Out of scope (now)

- iClone's side as a built workspace (animation timeline, scene editing, FX) — later, same app (R6, R13).
- Our own engine, our own renderer, our own sculpt core (R1, R7, R15).
- A Blender fork (R1: only on a named trigger).
- Training on non-commercial scan datasets; buying scans (R5).
- A content store, cloud services, accounts.
- Video generation and the AI-film flow — JustDirect's job, linked by the API (R20, IDEAS).
- Legal clearance of names and terms beyond the USPTO database check (RESEARCH §12; the user's word).

## 7 · What "done" means for the first release

The gate passed; Body, Head & Face, Skin & Materials, Hair, Photo-to-head, Rig & Expressions, Clothes fitting and
Import / Export with the Unreal plugin at `done` on the scorecard with their proofs; the API's contract tests green on
Windows, macOS and Linux CI; user docs for each workspace; the extension on extensions.blender.org and the plugin on
GitHub — and the family's rule: a release only when nothing is open.
