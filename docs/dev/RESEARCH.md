# Research register — what we already know, and where the proof is (just-stage)

**Read the section for your subject before researching anything.** An agent's brief carries that
section and the line *"don't re-derive these; re-check one only if the source it cites changed after
its date"*. New facts land here in the same change; a research doc with no entry here is not done.

How an entry reads: one fact per bullet, then *how it was checked and when*, then where the proof is.
A fact that turns out wrong is **rewritten**, ending "(was: … until <date>)" — never left standing
beside its correction.

Labels: **measured** — run on this machine · **web** — checked against the upstream page by the
session that recorded it · **agent** — found on the web by a research agent and not re-checked by
the session that recorded it · **record** — carried from another register or note.

Subjects: [1 · The machine](#1--the-machine) ·
[2 · CC5 and its plugins](#2--cc5-and-its-plugins) ·
[3 · iClone 8 and its plugins](#3--iclone-8-and-its-plugins) ·
[4 · Feature references](#4--feature-references) ·
[5 · Existing bases to build on](#5--existing-bases-to-build-on) ·
[6 · Routes: engine and editor layers, languages](#6--routes-engine-and-editor-layers-languages) ·
[7 · Building blocks](#7--building-blocks) ·
[8 · Standards](#8--standards) ·
[9 · Legal](#9--legal) ·
[10 · Fit: the web kit's engines, JustDirect, one app or two](#10--fit-the-web-kits-engines-justdirect-one-app-or-two) ·
[11 · PhotoCraft, the setup we looked at](#11--photocraft-the-setup-we-looked-at) ·
[12 · The name](#12--the-name) ·
[13 · Working method: models and sessions](#13--working-method-models-and-sessions)

## 1 · The machine

- GPU RTX 2070 Super with 8 GB, 32 GB RAM — *record, 2026-10-24* (the JustDirect memory note); not
  measured from this repo yet.
- The user has Unreal Engine C++ projects on this machine (`E:\Dev\Unreal`: DeformCPlusTest,
  DeformationSystem, FootprintDeformation, GlobalEnvironmentalSystem, UE_GlobalEnvironmentalSystem) —
  *measured (listed), 2026-10-29*.

## 2 · CC5 and its plugins

Not researched yet. Every feature from Reallusion's own docs and release notes; per feature: keep,
improve, drop, or new. The user named (2026-10-29): sculpting at ZBrush's level "or clone", making
clothes (as Marvelous Designer and MetaTailor do), making props, and CC5's pipeline that pushes
characters, scenes and animation to Unreal Engine and other software.

*web (search-result summaries, pages not opened), 2026-10-29:*

- CC sends and receives meshes with ZBrush through the GoZ plugin (provideocoalition.com, CC3 coverage).
- A free MetaTailor plugin for CC (2025) sends a character to MetaTailor in one click and brings it back
  clothed, keeping its own clothing as separate parts (cgchannel.com/2025/04/character-creator-gets-new-metatailor-plugin/).

Leads from the chat, not checked — names to confirm in the inventory: Headshot, SkinGen, Hair Builder,
Smart Gallery, Transformer, InstaLOD, Auto Setup for Unreal/Unity/Blender, Unreal Live Link. Unknown:
"z-weave" (the user's word) — nothing found under that name; closest are GoZ and R3DS ZWrap; asked the user.

## 3 · iClone 8 and its plugins

Not researched yet. Scene features included (sets, props, terrain and sky, lights, cameras, particles,
physics, timeline, render) as well as characters and animation. FX can come later, but its place goes
into the first design (the user, 2026-10-29).

*web (search-result summaries), 2026-10-29* — reallusion.com/iclone/vfx/popcornfx and 2017 launch coverage:

- PopcornFX has been part of iClone since iClone 7 (2017) and works with iClone's lighting, physics and
  timeline: billboard, ribbon and mesh emitters; particles can light the scene and feed its GI; collisions
  through NVIDIA PhysX; the free PopcornFX Editor is bundled for making effects.

Leads from the chat, not checked: AccuLips, AccuFace, Motion LIVE, the Curve Editor, Motion Director,
physics, Live Link; iClone calls characters "actors"; CC and iClone move characters between them with a
send-and-update round trip.

## 4 · Feature references

Not researched yet. Only the parts that overlap CC5 and iClone. What to study in each (from the chat,
not checked):

- Houdini — node-based procedural design and native USD (Solaris); KineFX for rigging and animation,
  Vellum for cloth and hair; Python + C++ SDK; Houdini Engine runs Houdini tools inside Unreal, Unity and
  other hosts — the pattern for "our API and tools usable from other apps".
- Cinema 4D — the approachable interface; a clean Python + C++ plugin SDK.
- Cascadeur — AI-assisted posing (AutoPosing) and physics-correct animation (AutoPhysics): the main
  source for "improve or add" on the animation side.
- Maya and MotionBuilder — rigging, retargeting and mocap cleanup; HumanIK naming as a skeleton
  candidate.
- Daz Studio and MetaHuman Creator (direct competitors), ZBrush (sculpting, HD morphs), Marvelous
  Designer (making and simulating clothing), Substance 3D Painter (texturing), Mixamo (auto-rigging, a
  motion library), MetaTailor (fitting clothes to any humanoid; added 2026-10-29).

*web (search-result summaries), 2026-10-29* — cgchannel.com, MetaTailor 2.0 (2024-10) and 2.5 (2026-02):

- MetaTailor (Hologress) is a Unity-based tool that fits third-party garments to humanoid avatars,
  handling layering and skin weights itself; sculpt brushes refine the fit; it exports FBX. 2.0 added
  clothing physics and an asset marketplace; 2.5 took its Unity and UE5 bridge plugins out of beta.

## 5 · Existing bases to build on

Not researched yet. Open human models, character add-ons and creators, auto-riggers: what each covers,
its licence, how healthy it is. Candidates named so far, not a limit: MakeHuman and MPFB2, MB-Lab,
CharMorph, Human Generator, Anny, VRoid Studio, Auto-Rig Pro, Rigify, UniRig — the research finds the rest.

*web, 2026-10-29* — GitHub's API (`repos/<name>` and `releases/latest`) and the projects' pages:

- MPFB2 (makehumancommunity/mpfb2), MakeHuman's Blender add-on: last push 2026-10-24, latest release
  v2.0.18 on 2026-10-11, 671 stars — the active one of these four.
- MakeHuman, the standalone app (makehumancommunity/makehuman): last push 2024-08-19, latest release
  v1.3.0 on 2024-05-15, 1,621 stars.
- MB-Lab (animate1978/MB-Lab), the community continuation of ManuelBastioniLAB after its developer stopped:
  **archived** (last push 2024-07-21), latest release 1_8_1 on 2024-06-08, 2,030 stars. Its page lists
  phenotypes, age, mass, tone, body measures, face rig, expressions, poses and BVH files.
- blendercharacterproject.org is CharMorph (Upliner/CharMorph), "100% Free & Open Source": last push
  2025-05-29, latest release v0.4.0-3 on 2025-03-27, 576 stars.
- GitHub reports no single licence for any of the four ("NOASSERTION") — read each repo's licence files
  for code and assets separately.

## 6 · Routes: engine and editor layers, languages

Not researched yet. A game engine, Blender, our own engine on rendering libraries, or a mix; the
language per layer (engine core, editor UI, scripting and plugin API), nothing ruled out. CC and iClone
are each an engine (renderer, scene, skeletal animation, physics, asset pipeline — the layer of Unreal,
Unity, Godot) with an editor on top (tools, panels, undo, timeline, file format, plugins — the layer of
the Unreal and Godot editors, and of Blender).

Candidates from the chat, not checked:

- Game engines: Unreal, Unity, Godot (its editor is itself a Godot app), O3DE, Bevy and Fyrox (Rust),
  Stride (all C#, MIT), Flax (C++ core with C# scripting; source published, royalties).
- Blender as an add-on or a fork (Bforartists is an existing fork with a reworked interface).
- Our own engine on rendering libraries: Filament, bgfx, Diligent, wgpu.
- A mix: our own editor with borrowed parts — Jolt or PhysX for physics, ozz for animation; a .NET
  editor UI on Avalonia or WPF.
- To verify: since Unreal 5.6, MetaHuman Creator runs inside the Unreal editor beside Sequencer and
  Control Rig — the closest existing "CC + iClone in one editor"; and what Epic's and Unity's terms
  allow when shipping an editor built on them.

Each route is scored on: a CC5-quality human in real time (skin, strand hair, eyes, wrinkles); our own
editor and layout on it; a licence that lets us ship our own free app (Epic's and Unity's terms on editor
tools, GPL for Blender); a Python and C++/Rust API and plugins; clean export into Unreal, Unity, Godot and
Blender; performance on §1's machine; how much of the CC5 and iClone feature list it gives for free. The
route and the language mostly decide each other, so they are compared as pairs.

## 7 · Building blocks

Not researched yet. Skin and hair rendering, blendshapes, cloth and hair simulation, auto-rigging,
photo-to-head, texture generation, video and webcam mocap, lip-sync, motion generation — open models
that fit §1's machine. Added 2026-10-29: sculpting, making and fitting clothes, prop modelling, and FX
(particles).

Leads, not checked: face capture with MediaPipe or ARKit (Live Link Face); lip-sync with NVIDIA
Audio2Face or Rhubarb; video mocap with FreeMoCap, WHAM or GVHMR; motion generation (MoMask); auto-rigging
with UniRig; image-to-3D with Hunyuan3D or TRELLIS; physics with Jolt, PhysX or XPBD cloth; FBX reading
with ufbx.

## 8 · Standards

Not researched yet. Scene and data model, skeleton naming, face standard, the command and API layer,
the plugin contract and sandbox, our own file format and its versions; the import rules of Unreal,
Unity, Godot and Blender.

Candidates from the chat, not checked:

- Scene and data model: OpenUSD (with UsdSkel), glTF 2.0 + VRM, FBX import.
- Skeleton naming: HumanIK, VRM humanoid, Unity Humanoid, the Unreal/MetaHuman skeleton, Rigify. Face:
  ARKit's 52 blendshapes, FACS.
- Everything is a command (§11): one registry that the UI, a CLI, a JSON control channel, an HTTP API and
  an MCP server all call — the user API by construction, the same for characters, scenes, animation and
  plugins.
- Plugins: a sandbox (PhotoCraft uses WebAssembly) and/or a Python API like Blender's, Maya's and
  Houdini's. Every feature beyond the core ships as a built-in plugin, so the plugin API is proven on our
  own features and a character-only user doesn't load the rest.
- Later features — FX and others — get their extension points in the first design (the user,
  2026-10-29).
- The file format adds fields so older files still load (§11).
- A parity scorecard against CC5 and iClone, feature by feature, with a floor that only rises (§11).
- The jobs table ("one way per job"): the standards spec creates it (TASKS).

## 9 · Legal

Not researched yet. Trademarks — never "Character Creator", "iClone" or "Reallusion" in our names; the
JustStage trademark check (TASKS). Reallusion's EULA on their file formats, their content-store terms,
the licence of every candidate (code and assets apart). Clean-room: behaviour and public docs only
(`AGENTS.md`).

## 10 · Fit: the web kit's engines, JustDirect, one app or two

Not researched yet. Questions from the chat:

- JustDirect inside JustStage (a workspace or built-in plugin) or beside it, using JustStage's
  characters and scenes through the API: how much of JustDirect is the 3D stage; how a non-web app
  reaches the web kit's engines (call the kit as a service, or a 3D-family engine layer — engine
  handling inside an app is NOT STANDARD in the web family); a 3D viewport and image or video models
  sharing 8 GB of GPU memory.
- One app or two: the user leans to one app that feels like two distinct apps; one shared scene with a
  workspace per job is how every engine editor and Blender work.
- The AI-movie thought (IDEAS.md): maybe JustStage needs only character creation, props, scenes and
  camera management, and AI makes the movie.

The shared web stack's facts (llama.cpp, stable-diffusion.cpp, audio.cpp, the
memory arbiter) are in `E:\Dev\Web\just-core\docs\dev\RESEARCH.md` — read them there, don't copy them.

## 11 · PhotoCraft, the setup we looked at

*web, 2026-10-29* — github.com/storytold/photocraft, its README and `AGENTS.md`, read through a page
summary:

- An image editor written in Rust: a Cargo workspace of 24 crates, egui/eframe on wgpu, the same code
  built to WebAssembly for the browser; dual-licensed MIT or Apache-2.0; early alpha.
- Its own words: a "clean-room reimplementation of Adobe Photoshop", "implemented from public specs and
  observed behaviour only"; `AGENTS.md`: "Never copy their code, shaders, profiles or assets."
- No orchestrator: `AGENTS.md` and `docs/` are read first, golden rules apply, "Every change comes with
  tests", and a parity scorecard has a floor that is raised and never lowered.
- Everything is a command: each has an id, label, menu path, shortcut, params doc, `enabled` and `run`,
  and is dispatched by id from the UI, the CLI, a JSON control channel and an MCP server.
- Plugins: "sandboxed WebAssembly plug-ins" — no further design detail.
- Parallel agents each use their own build directory and edit only files they own; a new command goes
  in a new `<area>_cmds.rs` module.
- It forbids webview UIs: "Never add Tauri (or any webview/JS UI framework)".
- Its file format adds new fields with `#[serde(default)]` so older files still load.

## 12 · The name

*web, 2026-10-29* — search-engine checks, npm (`registry.npmjs.org/<name>`) and GitHub's repository
search; **no trademark search (USPTO, EUIPO) done yet**:

- `just-stage`: no product named JustStage; npm free; 22 GitHub repos carry the name. "Stage" is a
  real-time 3D rendering and collaboration platform on Unreal Engine 5 by Trapdoor Creative
  (blog.cadsoftwaredirect.com/?p=9009).
- `just-animate`: taken on npm (an MIT JS animation library, last pushed 2019) and a WordPress plugin;
  23 GitHub repos.
- `just-character-animation`: no product; npm free; 0 GitHub repos.
- `just-actor` npm free, 3 repos · `just-troupe` npm free, 0 repos ("Troupe" is a JetBlue trip-planning
  app) · `just-scene` npm free, 9 · `just-figure` npm free, 12 · `just-puppet` npm free, 5 ·
  `just-motion` taken on npm, 20 repos, plus the `just_motion` Flutter library · `just-act` npm free,
  219 repos.
- JustCast is an active podcast hosting service (podnews.net/directory/company/justcast).
- Galatea is Inkitt's "Galatea: Books & Audiobooks" app, about 256K App Store reviews
  (apps.apple.com/app/id1380362212); Sinew turned up no 3D product.

## 13 · Working method: models and sessions

- Fable 5.1 costs $10 / $50 per million input / output tokens, Opus 5.5 $4 / $20; Fable 5.1 is
  Anthropic's "most capable widely released model, for the most demanding reasoning and long-horizon
  agentic work" — *record, 2026-10-29* (the claude-api skill's model table, cached 2026-10-06).
- Prompt caches are per model, so switching a session's model re-reads its context uncached — *record,
  2026-10-29* (the same skill).
- CLAUDE.md files at and above the working directory load at launch; one in a subdirectory loads when
  Claude reads or edits a file there — *record* (the web kit's register §6, *web, 2026-10-09*).
