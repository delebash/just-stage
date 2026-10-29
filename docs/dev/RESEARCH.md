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
Smart Gallery, Transformer, InstaLOD, Auto Setup for Unreal/Unity/Blender, Unreal Live Link. "z-weave",
from the user's list, is Z-Emotion's Z-Weave, a separate clothing design tool (§4); no link to CC found.

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

Added 2026-10-29: Z-Weave (clothing, with cloth simulation); mocap apps — Rokoko Studio, Move.ai,
DeepMotion, Plask; AI-film references for the AI-movie idea — Autodesk Flow Studio (formerly Wonder
Studio), ArtCraft; Blender's own character tools — Rigify, hair curves.

*web, 2026-10-29* — z-emotion.com/z-weave (page summary), plus search-result summaries (businesswire.com
2021-04-01 launch; Pi Europe 2025 exhibitor listings):

- Z-Weave (Z-Emotion) is "3D clothing design tool for fashion designers, game studios and content
  creators": 2D patterns placed and sewn in 3D on a default avatar, with real-time cloth simulation.
- Free tier: DXF/OBJ/FBX import; DXF/OBJ/FBX/glTF/glb export. Pro ($40/month): its own format, animation
  export (FBX+mc, Alembic, USD), fashion grading and colorways. Enterprise: custom.
- Its own formats: rozy (2D patterns with 3D placement, sewing, textures), zbp (body parameters), zpose,
  zcam. Plugins: z-maya (garments and simulation into Maya) and z-unreal (ML-based cloth simulation in
  Unreal).
- Founder Dongsoo Han, a former AMD graphics researcher whose hair simulation work became TressFX.
- No integration with CC, iClone or Reallusion found.

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

Added 2026-10-29: JustStage must be cross-platform — Windows, macOS and Linux (the user) — so each route
is scored on its graphics APIs (DirectX 12, Vulkan, Metal) too. Also: editor UI toolkits (Qt, Dear ImGui,
egui, Avalonia, WPF, Slint); more engine candidates (NVIDIA Omniverse Kit; Wicked Engine and The Forge as
bases for our own engine); how AI agents test a 3D app (a headless mode, image snapshots, a control
channel) — every family app is built by AI, so this is scored for every route; and the licence each route
would force on JustStage (§9).

## 7 · Building blocks

Not researched yet. Skin and hair rendering, blendshapes, cloth and hair simulation, auto-rigging,
photo-to-head, texture generation, video and webcam mocap, lip-sync, motion generation — open models
that fit §1's machine. Added 2026-10-29: sculpting, making and fitting clothes, prop modelling, and FX
(particles).

Leads, not checked: face capture with MediaPipe or ARKit (Live Link Face); lip-sync with NVIDIA
Audio2Face or Rhubarb; video mocap with FreeMoCap, WHAM or GVHMR; motion generation (MoMask); auto-rigging
with UniRig; image-to-3D with Hunyuan3D or TRELLIS; physics with Jolt, PhysX or XPBD cloth; FBX reading
with ufbx.

Added 2026-10-29: a path tracer beside the real-time viewport for final renders; hair grooming tools;
live mocap streams (Live Link, VMC, OSC) and devices (iPhone, Rokoko, Xsens, webcams); open motion and
asset libraries and their licences (CMU mocap, AMASS, LAFAN1, Poly Haven, Mixamo's terms) for a built-in
motion and content library.

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
- Added 2026-10-29: the asset library (how characters, clothes, props and motions are stored, tagged and
  shared — what CC's Smart Gallery and content store do); importing existing characters from CC, Daz,
  MetaHuman and VRM — what's allowed (§9) and how.

## 9 · Legal

Not researched yet. Trademarks — never "Character Creator", "iClone" or "Reallusion" in our names; the
JustStage trademark check (TASKS). Reallusion's EULA on their file formats, their content-store terms,
the licence of every candidate (code and assets apart). Clean-room: behaviour and public docs only
(`AGENTS.md`).

JustStage's own licence (the user, 2026-10-29): open source, MIT preferred, LGPL-type components
acceptable, not limited yet. For each route the research states the licence it would force on JustStage,
including whether Blender treats add-ons that use its Python API as GPL. The family apps checked are MIT
(`just-house-paint/LICENSE`, `justwrite-app/LICENSE` — *code, 2026-10-29*).

The user, 2026-10-29: "dont worry about trademark research or to much on lincese research, i am more
interested in getting the correct app design tools engine ect than leagal stuff" — so round one has no
legal agent; each research doc gives every product, library, model and asset set a one-line licence label,
and the licence a route forces on JustStage is one line in §6 (TASKS).

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

*record, 2026-10-29* — read by this session from the web kit's register (`just-core/docs/dev/RESEARCH.md` §2
"stable-diffusion.cpp video on this PC", §11 "Long server jobs"), its `docs/app-structure.md` (§Q.3 and the jobs
table) and `just-core/docs/plans/2026-10-24-just-direct-feasibility.md` (§A, §D). Pointers, not copies:

- The kit's engines are separate local programs that the kit's Node server installs, starts and books memory
  for: llama-server (llama.cpp), sd-server (stable-diffusion.cpp — image and video as HTTP jobs) and audio.cpp
  (a run of CLI processes for the voice swap) — `runner/runtimes.js` `RUNTIMES` + `runner/runtime_service.js`
  `RuntimeService`. A family app's server also runs headless, on its own launcher (§Q.3). So a non-web app
  can reach the engines in two ways: call a family server over local HTTP, or start the same engine programs
  itself — which would be a second way to do a job the kit already does.
- On §1's 8 GB card, a local video clip (LTX-2.3 22B Q4, 1280×704 × 121 frames) is a 410–419 s job that peaks at
  7.3 GB on the card and 23.3 GB of private RAM, and needs a fresh sd-server per clip — so a live 3D viewport
  and local video generation can't hold the card at the same time; video is a queued job.
- Two apps sharing the card agree on it by Claude messages today; the kit's `EngineBusyError` covers one app
  only (kit register §11, 2026-10-28).
- The JustDirect answer (feasibility §D, 2026-10-24/27): buildable on the kit; images, voice, music, the LLM,
  a 3D stage and the editor run well on this PC; video is a queue, not interactive; "Unreal: no integration" —
  glTF in and out instead, since Unreal beside a video model on one 8 GB card isn't possible.
- ArtCraft's 3D stage — the part of JustDirect that overlaps JustStage — is Three.js 0.171 run locally:
  GLB/glTF, PMX, Gaussian splats, a camera controller, a timeline, snapshots, a posed mannequin guiding the
  final character (feasibility §A). That is a small subset of JustStage's scene and animation workspace.

The assessment of this section (one app or two; JustDirect inside or beside) waits for §2, §3 and §6.

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
search (was: "no trademark search (USPTO, EUIPO) done yet" until 2026-10-29 — the USPTO search is the
next entry):

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

*web, 2026-10-29* — USPTO's trademark search (tmsearch.uspto.gov), queried through the site's own search
service from this session, every class, live and dead; the query was proven first on a known mark (ICLONE:
4 records). A database check, not legal clearance:

- No US application or registration, live or dead, for JUSTSTAGE, JUST STAGE or JUST-STAGE, and none
  starting JUSTSTAG. The only marks holding both words: STAGE IS JUST A NUMBER (live; classes 18, 21, 25,
  35) and THE WORLD IS A STAGE...JUST PRESS PLAY (dead; class 42).
- Nearest spellings (fuzzy match): JUSTSTONE (live, class 9 — MP3 players and recorders; serial 99444663),
  JUSTSTAND (live, classes 41 and 44; Ergotron), JUSTSTART (dead, class 9).
- Live STAGE marks whose goods name 3D, animation, avatar, virtual-production, rendering or character
  software, in classes 9 or 42, all lead with a strong word: UNREAL STAGE (Epic Games; one registration in
  class 9, one in 42), NUKE STAGE (Foundry; 9 and 42), E-STAGE (Materialise; 9, 40, 42), POLYMOTION STAGE
  (Mark Roberts Motion Control; 41, 42), SET STAGE (Set Point; 41, 42).
- EUIPO not searched: its search sites refuse scripted requests, the Chrome extension wasn't connected, and
  the user then dropped the trademark check — "dont worry about trademark research" (TASKS, 2026-10-29).

## 13 · Working method: models and sessions

- Fable 5.1 costs $10 / $50 per million input / output tokens, Opus 5.5 $4 / $20; Fable 5.1 is
  Anthropic's "most capable widely released model, for the most demanding reasoning and long-horizon
  agentic work" — *record, 2026-10-29* (the claude-api skill's model table, cached 2026-10-06).
- Prompt caches are per model, so switching a session's model re-reads its context uncached — *record,
  2026-10-29* (the same skill).
- CLAUDE.md files at and above the working directory load at launch; one in a subdirectory loads when
  Claude reads or edits a file there — *record* (the web kit's register §6, *web, 2026-10-09*).
