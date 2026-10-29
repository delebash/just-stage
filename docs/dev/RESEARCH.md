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
improve, drop, or new.

## 3 · iClone 8 and its plugins

Not researched yet. Scene features included (sets, props, terrain and sky, lights, cameras, particles,
physics, timeline, render) as well as characters and animation.

## 4 · Feature references

Not researched yet. Houdini, Cinema 4D, Cascadeur, Maya, MotionBuilder, Daz Studio, MetaHuman Creator,
ZBrush, Marvelous Designer, Substance 3D Painter, Mixamo — only the parts that overlap CC5 and iClone.

## 5 · Existing bases to build on

Not researched yet. Open human models, character add-ons and creators, auto-riggers: what each covers,
its licence, how healthy it is.

## 6 · Routes: engine and editor layers, languages

Not researched yet. A game engine, Blender, our own engine on rendering libraries, or a mix; the
language per layer (engine core, editor UI, scripting and plugin API), nothing ruled out.

## 7 · Building blocks

Not researched yet. Skin and hair rendering, blendshapes, cloth and hair simulation, auto-rigging,
photo-to-head, texture generation, video and webcam mocap, lip-sync, motion generation — open models
that fit §1's machine.

## 8 · Standards

Not researched yet. Scene and data model, skeleton naming, face standard, the command and API layer,
the plugin contract and sandbox, our own file format and its versions; the import rules of Unreal,
Unity, Godot and Blender.

## 9 · Legal

Not researched yet. Trademarks, Reallusion's EULA on their file formats, their content-store terms,
the licence of every candidate.

## 10 · Fit: the web kit's engines, JustDirect, one app or two

Not researched yet. The shared web stack's facts (llama.cpp, stable-diffusion.cpp, audio.cpp, the
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
