# JustStage — what the app is for (PRD)

> **Status: rewritten 2026-10-29 to the approved recs** (R1–R21 and the Opus review's 1–28 — [`TASKS.md`](TASKS.md);
> the standards spec: [`../standards/README.md`](../standards/README.md)). **§2 (who it is for) and §7 (what "done"
> means for the first release) were the Fable session's guess; §2 and §7 are now the user's answers (2026-10-29)** (review
> item 19 — a gap in an approved decision is asked, never filled with our own choice). Why it is built this way:
> [`ARCHITECTURE.md`](ARCHITECTURE.md).

## 1 · In one paragraph

**JustStage — characters, scenes, animation.** A free, open-source 3D character creator — what Character Creator 5
and its plugins do — that makes whole humans at CC5 and MetaHuman quality or better, pulls in characters from CC5,
Daz, MetaHuman, VRM and Unreal, and sends set-up characters to Unreal in one click. Creatures too, not only humans.
It installs and opens as its own app — an unmodified Blender inside, JustStage's add-on, screens and AI host on top —
on Windows, macOS and Linux, on any GPU vendor, with an API every program and AI agent can call, and with its features
built as plugins that switch on and off. AI features run locally through the family's engines. Scenes and animation (iClone's side) come later in the same app; until
then Unreal, reached through JustStage's own plugin, and Blender's animation tools stand in. Every feature is built by
AI agents against written standards, with a measured quality gate before the features and a parity scorecard whose
floor only rises.

## 2 · Who it is for — the user's answer, 2026-10-29

The user, verbatim: "as with all my apps they are for anyone to use open source on any computer crossplatform and any
grpahics". So JustStage is for **anyone**: free and open source, on Windows, macOS and Linux, on any graphics card —
NVIDIA, AMD, Intel or Apple. Every core part runs on every vendor; a part that runs on one vendor only (NVIDIA's
Audio2Face, UniRig's weight stage) is an optional plugin with its vendor shown, and a part missing on one platform (the
webcam capture library on Intel Macs) is labelled there, never hidden.

What anyone must get, from the requirements below: characters at the quality bar; import of what they already own;
export into the engine or program they use (Unreal through the plugin, Unity, Godot, Blender, Maya and others); an API
for scripts and AI assistants; licences shown on everything.

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
- Creatures: "we need to create non human body as well like creatures just like cc5 allows" — human and creature
  kinds from the start, built in step 4.
- AI: "we are definitly adding lots of good ai features to this app like cc5 and we will come of with more"; "i want
  user to be able to descibe a person and the app creates that person mesh" (not now — IDEAS.md).
- Its own app: "i want our app to look like a custom app so user donest have to load plugin it just laucnhe like an
  app we built even thought it is using blender core features".
- Modular: "i like the modular design idea"; "our bundle of plugins for features should not be seperate donwloads".
- Mocap: "we want features like unreal has where you can do mocap face with iphone and other motion capture stuff" —
  in Unreal now through the plugin; in JustStage with the Animate workspace.
- Blender: the user installed Blender 5.3 so JustStage is built and tested on it.

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
| 4 | **Rig & Expressions** | gets the UE5 skeleton placed from the body, a DNA face rig by MetaHuman's control names with the ARKit 52, body correctives in a body DNA; auto-rigs an imported humanoid; poses; previews expressions from the webcam | rig tests; capture tests; round trips |
| 4 | **Creatures** | makes a non-human character: imports or sculpts a mesh, rigs it from Mesh2Motion's or Rigify's creature rigs, plays CC0 creature animations | rig tests; golden images |
| 5 | **Clothes** | fits garments (conform, layers, tuck-in, hide-under, weights), simulates, re-fits when the body changes | fit and refit tests; golden images |
| 6 | **Import / Export** | imports from CC5, Daz, MetaHuman, VRM, Unreal, MakeHuman, Mixamo, any humanoid; exports to Unreal (the plugin, keep-animation), glTF/VRM, FBX, USD, CC5, Unity, Godot, Maya | round-trip tests per preset; the plugin's Automation tests |
| 7 | **Sculpt extras** | sculpts morphs and HD detail; saves sculpts as sliders | command tests |
| 8 | **Making clothes from patterns** | sews 2D patterns into garments and simulates | tests when built |
| — | **The API** (every step) | drives all of the above from Python, the command line and MCP, with permissions; plugins' commands appear for assistants automatically | API contract tests |
| — | **The app** (every step) | installs JustStage and opens it from its own icon; switches features and plugins on and off on one Plugins page | install and launcher tests |
| — | **Motion capture in Unreal** (from step 1) | drives JustStage characters in Unreal with Live Link Face, MetaHuman Animator and Live Link devices | the plugin's Automation tests |
| — | **The asset library** | stores characters, garments, grooms, presets with licence labels; browses remote libraries | library tests |
| later | **Animate** (with live capture in JustStage: webcam, Live Link Face, VMC), **Scene**, **FX**, props, crowds, describe-a-person | iClone's side and the AI ideas | rows reserved in the scorecard; data defined now |

## 5 · Outside data, accounts and paid services

| Thing | Status | Where it shows |
|---|---|---|
| Blender 5.3 (GPL), shipped unmodified inside the installer | its source offered, as the GPL asks | About |
| Open bases and data: MakeHuman hm08, targets, face-unit and viseme packs (CC0), MHR and SOMA-X (Apache-2.0), GNM (Apache-2.0), ICT-FaceKit (MIT), OpenRigLogic (MIT), Blender Studio's Human Base Meshes (CC0), Mesh2Motion's rigs and animations (CC0) | reused under their licences, labelled | provenance on every asset |
| Open image models: Z-Image-Turbo, Qwen-Image, FLUX.2 klein 4B (Apache-2.0), HiDream-O1 (MIT) | run locally by JustStage's engine host; labelled | the generators' model picker |
| JustStage's engine host (a server-only package from the web kit's template), shipped in the installer | local, free; JustDirect shares it later | the AI page |
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

## 7 · What "done" means for the first release — the user's word, 2026-10-29

The user, verbatim: "i agree go code it" (on the rec shown in chat — TASKS). The first release is **R21's steps 1–6**:
the passed quality gate; Body, Head & Face, Skin & Materials (with makeup layers), eyes, Hair (with beards and
mustaches); Photo-to-head and photo-to-body; Rig & Expressions with Creatures; Clothes fitting; Import / Export with the
full Unreal plugin (motion capture through Unreal with it) — each at `done` on the scorecard with its proof; the
installer and launcher on Windows, macOS and Linux; the Plugins page; the API with its contract tests green on all three
OSes' CI; user docs for each workspace; JustStage's installers and the Unreal plugin on GitHub — and the family's rule:
a release only when nothing is open. After it: sculpt extras (step 7), clothes from patterns (step 8), then Animate
with JustStage's own live capture, Scene, FX and describe-a-person.
