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
- The user, 2026-10-29: "my 2070 runs unreal and blend and cc5 and iclone well enough" — *record* (the
  user's word; not measured from this repo).
- The user has Unreal Engine C++ projects on this machine (`E:\Dev\Unreal`: DeformCPlusTest,
  DeformationSystem, FootprintDeformation, GlobalEnvironmentalSystem, UE_GlobalEnvironmentalSystem) —
  *measured (listed), 2026-10-29*. `DeformCPlusTest` is on UE **5.7** (its `.uproject`) and holds the Mannequin
  meshes (§8).
- **Blender 5.3 beta is installed at `E:\blender-5.3.0-beta`** (the user, 2026-10-29; the folder read, not run): its
  bundled Python is 3.13 and `5.3/python/lib/site-packages` holds `pxr` (Usd, UsdSkel, UsdShade, UsdMtlx, UsdMedia,
  UsdPhysics, ExecIr, …) and `MaterialX`; `5.3/datafiles/assets/nodes/procedural_hair_node_assets.blend` ships the
  procedural hair node groups — *measured (listed), 2026-10-29*. (was: "Blender is not installed on this machine … full
  `find`" until 2026-10-29 — that search timed out and C: was searched only five levels deep.)
- **Unreal 5.8 is at `F:\Epic\UE_5.8`** (the user; `Engine\Binaries\Win64\UnrealEditor.exe` present). The registry's
  `HKLM\SOFTWARE\EpicGames\Unreal Engine` still lists 5.7 at `E:\Program Files\Epic Games\UE_5.7` and 5.8 at
  `C:\Program Files\Epic Games\UE_5.8`; neither folder exists — *measured, 2026-10-29*. Its MetaHuman plugin ships DNA
  files: `MetaHumanCoreTechLib\Content\ArchetypeDNA\` (`body_head_combined.dna`, `SKM_Body.dna`, `SKM_Face.dna`) and
  `MetaHumanCharacter\Content\Body\…` (`body_model.dna`, 18 fixed-compatibility bodies) — *measured (listed)*.

## 2 · CC5 and its plugins

Round one done 2026-10-29: [`../plans/2026-10-29-research-02-cc5.md`](../plans/2026-10-29-research-02-cc5.md)
(inventory table, plugins and prices, data model, Python API, praise and complaints; distilled below).
Every feature from Reallusion's own docs and release notes; per feature: keep, improve, drop, or new. The user named (2026-10-29): sculpting at ZBrush's level "or clone", making
clothes (as Marvelous Designer and MetaTailor do), making props, and CC5's pipeline that pushes
characters, scenes and animation to Unreal Engine and other software.

*web (search-result summaries, pages not opened), 2026-10-29:*

- CC sends and receives meshes with ZBrush through the GoZ plugin (provideocoalition.com, CC3 coverage).
- A free MetaTailor plugin for CC (2025) sends a character to MetaTailor in one click and brings it back
  clothed, keeping its own clothing as separate parts (cgchannel.com/2025/04/character-creator-gets-new-metatailor-plugin/).

Leads from the chat — all now rows of round one's inventory: Headshot, SkinGen, Hair Builder, Smart
Gallery, Transformer, InstaLOD, Auto Setup for Unreal/Unity/Blender, Unreal Live Link. "z-weave", from the
user's list, is Z-Emotion's Z-Weave, a separate clothing design tool (§4); no link to CC found (round one
didn't reach it).

*agent, 2026-10-29* — round one's CC5 notes, sources per fact there (page read unless marked):

- Latest is CC 5.2, released 2026-10-29: a cloud AI 3D generator (Tripo / Hunyuan, paid in points), Body
  Wrap (any humanoid mesh becomes a rigged CC base), eight cloth types with tuck-in, a rebuilt skin-weight
  editor, GLB import, Quad Remesher, high-to-low baking. CC5 launched 2025-08-27.
- Over CC4, CC5 added the HD base (two extra subdivision levels, 8K skin, displacement and cavity maps), HD
  morphs, reworked eyes and lashes, the Extended Plus and HD facial profiles, ActorMIXER, and MetaHuman's
  skeleton structure and facial controls (the manual: "same skeleton structure as MetaHuman").
- Windows 10/11 only; minimum 16 GB RAM and 8 GB VRAM; a 30 GB install plus a 200 GB DDS cache.
- One topology family underlies everything: CC3 Base+ at SubD 0/1/2, reduced for LODs with 101 / 54 /
  22-bone templates; bones are `CC_Base_*`, and export can rename them to the UE4/UE5 skeleton.
- Facial profiles: Standard 75 sliders (the ARKit-compatible set), Extended 160, Extended Plus 160 + 26,
  HD 262 + 128 correctives; lip-sync uses 15 visemes.
- CC and iClone share one in-process Python API (RLPy; PySide2 / Qt 5.15; the docs stop at iClone 8.0).
  There is no outside API — a third party built an HTTP + MCP bridge.
- Paid add-ons around a $299 core: ActorMIXER PRO $199, HD Ultimate Morphs $149, Headshot 3 $199;
  subscriptions from $29 a month.
- The pipeline is one free plugin per target: Auto Setup for Unreal (with Control Rig and Live Link, UE
  5.8+), Unity, Blender, Maya, 3ds Max, Marmoset; GoZ for ZBrush; USD.
- AI features run on cloud credits (Tripo, Hunyuan, Google image models; video models in AI Studio);
  FashionGen runs a bundled local ComfyUI.
- Clothing is fit-and-layer (conform, cloth types, tuck-in, auto-hide, weight transfer, PhysX soft
  cloth); garments are designed elsewhere. Sculpting inside CC is light; deep sculpting goes to ZBrush
  (GoZ, the paid Face Tools).
- Rendering is a real-time viewport only (TAA, voxel GI, IBL); whether the Iray path-tracer plugin works
  in CC5 conflicts (the manual vs a staff post).
- Complaints: launch bugs and regressions, paid content the tutorials assume, non-refundable
  subscriptions, no joint-corrective (JCM) system, JCMs lost on FBX export. Praise: HD skin and mesh, the
  number of facial blendshapes, ActorMIXER, an Unreal pipeline that needs no retargeting.
- Open (the notes' §10): Reddit and independent forums not reached (the search cap); vertex counts, the
  full bone list and the UDIM mapping are unpublished; several prices; the EULA and content licences
  (JavaScript-only pages); about 60% of the manual-sourced rows rest on topic titles only.

Second pass done 2026-10-29: [`../plans/2026-10-29-research-02-cc5-pass2.md`](../plans/2026-10-29-research-02-cc5-pass2.md).

*agent, 2026-10-29* — S1's pass 2, sources per fact there:

- Mesh counts reconciled: CC3+ is 17,683 polygons (14,046 for the body); CC5 HD is 70,732 at SubD 1 and 282,928
  at SubD 2 — ×4 per level; "60K" is a dressed character. The Level Table's polygon columns: actorBUILD 20K, LOD1
  7K, LOD2 0.8K (round one's reading of that table was off; the 101 / 54 / 22 bone templates stand). Vertex and
  per-mesh counts are published nowhere.
- Bones: Reallusion gives 100, 101 and 108 for CC3+; a 101-name list taken from Reallusion's GPL Blender add-on
  reduces exactly to the published 54 and 22; CC5 adds "ten bones" in the spine and head, names unpublished.
- UDIM tiles 1001–1006: head, body, arm, leg, nails, eyelash.
- The viewport is DirectX 11 (staff post). The RTX Render path tracer (free open beta since July 2026) needs
  DirectX 12 and NVIDIA RTX. Iray is not supported in CC5 (staff, 2025-04; the manual's menu is out of date).
- Builds: 5.07.1705.1, 5.11.1823.1, 5.12.1925.1 and 5.12.1928.1 (no 5.12 release post), 5.13.2031.1. CC 365 Pro
  costs $33.25 a month billed yearly (~$399). The MetaTailor plugin works with CC5.
- Licence: the CC Base Model clause bars use "in any character generation system" and for AI training — one
  line, no analysis; it bears on importing CC characters (S9).
- Still open: Reddit refused search and fetch, Polycount 403 (not worked around); CC5's Python version (3.8 per
  Reallusion's iClone 8 docs vs 3.10 per a third party); prices for Iray, FashionGen and SkinGen Premium; the 5.2
  build number; the native files' structure (the EULA forbids reverse engineering); no link between Z-Weave and CC.

## 3 · iClone 8 and its plugins

Round one done 2026-10-29: [`../plans/2026-10-29-research-03-iclone.md`](../plans/2026-10-29-research-03-iclone.md)
(about 100 features in 12 areas from the manual's full contents, release notes 8.0–8.76, plugins and
prices, data model and Python API; distilled below). Scene features included (sets, props, terrain and
sky, lights, cameras, particles, physics, timeline, render) as well as characters and animation. FX can come later, but its place goes
into the first design (the user, 2026-10-29).

*web (search-result summaries), 2026-10-29* — reallusion.com/iclone/vfx/popcornfx and 2017 launch coverage:

- PopcornFX has been part of iClone since iClone 7 (2017) and works with iClone's lighting, physics and
  timeline: billboard, ribbon and mesh emitters; particles can light the scene and feed its GI; collisions
  through NVIDIA PhysX; the free PopcornFX Editor is bundled for making effects.

Leads from the chat — confirmed by round one: AccuLips, AccuFACE, Motion LIVE, the Curve Editor, Motion
Director, physics, Live Link; iClone calls characters "actors"; CC and iClone move characters between them
with a send-and-update round trip.

*agent, 2026-10-29* — round one's iClone notes, sources per fact there (page read unless marked):

- Latest is iClone 8.76 (2026-10-29). iClone 9 is only previewed (bones on any model, custom control rigs,
  squash and stretch, springs with collision): "Development is in early stages", no date.
- Windows only: a DirectX 11 renderer, NVIDIA PhysX, voxel GI based on NVIDIA VXGI, an Autodesk HumanIK-based
  control rig, the PopcornFX runtime. An "RTX Render" path tracer, in open beta since 2026-07-28, needs an
  RTX 3060 or better.
- One project is one timeline (default 1,800 frames, maximum 216,000 since 8.3 — was: "maximum 54,000" until
  2026-10-29, from an outdated manual page; the second pass found the 8.3 notes of 2023-06-19); 6,000 ticks a
  second; Z-up, −Y forward, right-handed. "Sequences inside a project" is an open user request.
- The timeline holds nine data types (transform, parameter, clips, target switch, lip-sync, voice, on/off,
  transition, summary) plus IK/FK blend keys; layer keys live inside clips; project tracks carry camera
  switching, sound, HDR and IBL.
- The editing core is layered editing over mocap and library clips: motion layers with IK/FK effectors,
  per-body-part animation layers, Reach Target, Motion Correction (foot and hand contact), Motion
  Direction. The Curve Editor can't edit morph or facial keys.
- Crowds and game-style control: Motion Director (WASD, gamepad, waypoints, NPC behaviours), 8.4's crowd
  system (NavMesh, walkways, crowd generator), a paid node-graph Motion Planning plugin.
- Mocap: Motion LIVE takes face, body and hand devices at once, with paid per-device profiles (Vicon
  $1,990); Timecode is a paid plugin; cloud video mocap is billed per second.
- Face: AccuLips (speech-to-text, word alignment, visemes, TTS), Face Puppet, the Face Key editor, AccuFACE 2
  (webcam and video).
- CC↔iClone: "Send Character to iClone" replaces the character, and users report that an update bakes
  keyframes and wipes lip-sync data.
- Python API: Python 3.8 + Qt 5.15.2 (PySide2), a subset of the C++ SDK; in-process plugins only.
- Top requests by votes (the feedback tracker): turn off auto-keying with every animated property visible
  on the timeline (33), Sony mocopi (29), export an animated rig without its mesh (19), clip size (16),
  animation on selected bones only (13), expression animation layers (13), a Cascadeur bridge (10),
  autosave and undo kept on save (5).
- The 2026 direction is AI and cloud: AI Studio (third-party video models on cloud points) became a separate
  app in 8.75; 8.76 added an AI mesh generator.
- Open: Reddit not reached (the search cap); the Motion LIVE workflow and device protocols; several prices;
  the software EULA and ActorCore licence; whether the Python API can build timeline structure.

Second pass done 2026-10-29: [`../plans/2026-10-29-research-03-iclone-pass2.md`](../plans/2026-10-29-research-03-iclone-pass2.md).

*agent, 2026-10-29* — S2's pass 2, sources per fact there:

- Release history settled: two 8.7 builds (2026-01-26 and 2026-02-12); "8.54" was an announcement (June 2025),
  never a build.
- AI output: Reallusion's AI Service EULA (2026-10-29) grants commercial use on its Starter, Standard and Pro
  plans (Free is for testing); it covers Video Mocap output; Reallusion may train its AI on content set to
  Public.
- Prices, from the price data Reallusion's store page loads: mocap profiles — Xsens, Vicon, OptiTrack, Qualisys
  $1,990 each; Neuron and Rokoko $999; iPhone Live Face $399. Plugins — Unreal Live Link $1,490 (free for indies
  under $100K a year), PopcornFX $267, popVideo $168, BuildingGen $199; Motion Link free.
- Motion LIVE: each device's vendor app streams over the local network to an IP and port iClone listens on
  (Xsens UDP 9763, the iPhone app port 999, AccuFACE 2 its own TCP port); every vendor expects the T-pose to face
  a different axis.
- The AI Mesh Generator runs in Reallusion's cloud, $0.12–$1.60 a mesh in AI points.
- The Python API now covers most of the 2020 "can't do" list (save, undo blocks, viseme keys, re-parenting, mesh
  vertices, render passes) and has 51 events; it can create clips and keys, not tracks or layers.
- Hair is simulated as PhysX soft cloth, not by its own solver.
- The Marketplace lists 60 iClone Python plugins, 45 of them third-party.
- Still open: Reddit (the search tool refuses the site) and Capterra/G2 (403) — not worked around; a few device
  protocol names; ActorCore's own licence page (script-only).

## 4 · Feature references

Round one done 2026-10-29: [`../plans/2026-10-29-research-04-references.md`](../plans/2026-10-29-research-04-references.md)
(20 apps, a section and a summary-table row each; distilled below). Only the parts that overlap CC5 and
iClone. What to study in each (from the chat; round one confirmed Houdini's Solaris, KineFX and Engine,
Cinema 4D's C++ SDK, Cascadeur's two tools and HumanIK retargeting — its "Checks of §4 leads" table):

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

- MetaTailor (Hologress) is a tool that fits third-party garments to humanoid avatars, handling layering
  and skin weights itself; sculpt brushes refine the fit; it exports FBX. 2.0 added clothing physics and an
  asset marketplace; 2.5 took its Unity and UE5 bridge plugins out of beta. (was: "a Unity-based tool"
  until 2026-10-29 — round one found both articles name Unity only as an export and bridge target.)

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

*web, 2026-10-29* — re-checked by this session (GitHub's API):

- MetaHuman's face-rig runtime and rig file format (RigLogic, DNA) are open source as
  `EpicGames/OpenRigLogic`: MIT, created 2026-06-05, last push 2026-10-23, 304 stars. Released with
  MetaHuman 5.8 (June 2026, GamesBeat — *agent*). The licence files inside were not opened.

*agent, 2026-10-29* — round one's references notes, sources per fact there (page read unless marked snippet):

- MetaHuman Creator runs inside the Unreal editor since UE 5.6 (June 2025). Since 5.6 its EULA allows
  MetaHumans in "any engine or creative software"; 5.8 added full-body mesh-to-MetaHuman for any topology
  and the Animator on Linux and macOS.
- Cinema 4D 2026.4+ ships an official MCP server: off by default, local, an access token, and the user picks
  which tool groups an assistant may use — a reference for MCP over JustStage's commands, with permissions.
- Houdini Engine runs Houdini tools inside other apps in-process, out-of-process or on a remote server, with
  plug-ins for Unreal, Unity, Maya and 3ds Max — the reference for "our tools inside other apps". Houdini 22's
  APEX rigs are reusable components that a template moves onto a new character.
- Cascadeur: AutoPosing, AutoPhysics, AI Inbetweening, AI Root Motion and an Unreal Live Link (2026.1,
  snippet); its Python API is thin (Python 3.8, snippet).
- Marvelous Designer converts Character Creator, Daz, Mixamo and MetaHuman avatars itself (2025.0,
  snippet), imports MetaHuman DNA (2025.2, snippet), exports Alembic, FBX, USD and glTF (2026.1).
- Fitting existing clothes (MetaTailor) and making clothes from patterns (Marvelous Designer, Z-Weave) are
  separate jobs.
- ZBrush's stored selection sets (polygroups, masks, polypaint, UVs, morph targets) break when DynaMesh,
  ZRemesher or Sculptris Pro change the topology — the sculpt data-model problem of state tied to one
  topology.
- Maya 2027 built in layered skin weights (ngSkinTools) and shot tools; 2027.1 added OpenTimelineIO
  (snippet).
- HumanIK-style character definitions are the common retargeting interchange: MotionBuilder needs one per
  character (snippet); Rokoko and Flow Studio export HumanIK presets.
- Mocap apps share a feature set: multi-person capture from one video (DeepMotion up to 8 people), cleanup
  filters (root lock, foot lock, knee-pop smoothing), live streaming to many hosts (Rokoko to 8 apps,
  iClone among them).
- Blender's extension format is a .zip plus a TOML manifest: SPDX licence, platforms, bundled Python wheels
  and declared permissions with reasons (files, network, clipboard, camera, microphone); the manual doesn't
  say permissions are enforced.
- Autodesk Flow Studio turns video into 3D scenes (mocap, camera track, clean plate) with Maya, USD, Unreal
  and Blender exports; 2026-08 added a browser 3D editor and a node canvas.
- Daz is still on Genesis 9 (2022); Daz Studio 6 is in preview with an alpha C++ SDK on Qt 6.10; its
  content format DSON (.duf, .dsf) is published JSON (snippet).
- Nomad Sculpt runs a ZBrush-class sculpt loop on phone-class GPUs (snippets).
- Not reached (the session's 200-search budget ran out): 3DCoat, Style3D, Unreal's Control Rig and Sequencer
  as an iClone-timeline reference, Ready Player Me, Avaturn, and several API details — the notes' open list.

Second pass done 2026-10-29: [`../plans/2026-10-29-research-04-references-pass2.md`](../plans/2026-10-29-research-04-references-pass2.md).

*web, 2026-10-29* — re-checked by this session (GitHub's API): OpenRigLogic's `LICENSE` is "MIT License,
Copyright (c) 2026 Epic Games, Inc."; the repo holds code only (`include`, `src`, `python`, `docs`, `tests`,
`examples`, `benchmarks`). Its `TRADEMARKS.md`: the MIT licence "covers code only"; "You may not use … any Marks
as part of your own … product name"; a fork says "[Your Software] is based on OpenRigLogic".

*agent, 2026-10-29* — S3's pass 2, sources per fact there:

- MetaHuman's auto-rigging and texture synthesis run on Epic's servers (Epic's docs list the service hosts);
  nothing in 5.8 does them offline. OpenRigLogic is the C++ DNA and RigLogic libraries with Python bindings — no
  meshes; MetaHuman sample content is on Fab under Fab's licence. The MetaHuman licence pages need an Epic login
  or return 403 — the user's to read.
- Move AI: Vicon's parent bought its assets on 2026-10-09; Move Live is gone; the line is Genesis (real time since
  July 2026, optional fingers, NVIDIA GPU) and Move One. Ready Player Me shut down on 2026-01-31 after Netflix
  bought it; Avaturn still runs.
- Style3D's cloth simulation runs only on NVIDIA (CUDA) on Windows — a labelled reference, not a base.
- Newer versions: Cascadeur 2026.2 (animation layers; AI inbetweening up to 120 frames); Daz Studio 6, released
  2026-06-04 (the former "Daz Studio 2025").
- Unreal's Sequencer and Control Rig have the layer and mixer pieces an iClone-type timeline needs, but recent
  (5.5–5.8) and partly experimental.
- Settled: ArtCraft is dual MIT or Apache-2.0; MetaTailor's free tier is 5 exports a month (v2.6); Houdini 22
  shipped 2026-07-15. Whether MetaTailor is built on Unity: not findable.
- Open: ZBrush GoZ for the 2027 Maya and 3ds Max and Marvelous Designer's Personal-licence terms (blocked pages);
  Mixamo's official skeleton options, Avaturn's terms, Style3D's 2026 prices (not found).

## 5 · Existing bases to build on

Round one done 2026-10-29: [`../plans/2026-10-29-research-05-bases.md`](../plans/2026-10-29-research-05-bases.md)
(26 candidates, a comparison table and a ranked short-list; distilled below). Open human models, character
add-ons and creators, auto-riggers: what each covers, its licence, how healthy it is. Candidates named so far, not a limit: MakeHuman and MPFB2, MB-Lab,
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

*web, 2026-10-29* — re-checked by this session at the source (GitHub's API; MPFB2's `LICENSE.md`; Anny's
`LICENSE` and README):

- MPFB2: code GPLv3; its bundled assets CC0 1.0 — "anyone can do whatever they want with it" — and MakeHuman
  claims nothing over what users make with it. That code/asset split is why GitHub says NOASSERTION.
- Anny (naver/anny): code Apache-2.0; its body data is MPFB2's MakeHuman assets under CC0, its facial
  actions a CC0 face-units pack, plus a "soma" topology from SOMA-X (Apache-2.0); an SMPL-X topology is a
  separate non-commercial download. Created 2025-10-27, last push 2026-10-26, 612 stars.
- Meta's MHR (facebookresearch/MHR): Apache-2.0, last push 2026-10-26, 885 stars. Google's GNM (google/GNM):
  Apache-2.0, created 2026-03-23, last push 2026-10-29, 1,612 stars. NVIDIA's SOMA-X (NVlabs/SOMA-X):
  Apache-2.0, created 2026-03-03, last push 2026-10-09, 847 stars. ICT-FaceKit (USC-ICT/ICT-FaceKit): MIT,
  last push 2020-12-01. MakeHuman 2 (makehumancommunity/makehuman2): last push 2026-10-07, 88 stars.

*agent, 2026-10-29* — round one's bases notes, sources per fact there:

- MPFB2 ships 1,258 morph target files (the agent's count), 52 ARKit face units, 22 + 15 visemes, and 8
  standard rigs plus Rigify, infant to elder; it runs only inside Blender. The notes' rank 1.
- Anny is a PyTorch body model on the MakeHuman mesh (13,718 verts, 13,710 quads, eyes and tongue), with
  163- and 104-bone rigs, up to 267 phenotype parameters and ARKit-named facial actions (v0.6.1,
  2026-09-28) — the MakeHuman data working outside Blender, without its GPL code.
- MHR is scan-trained: 7 LODs (73,639 down to 595 verts), 127 joints, 72 FACS-based expressions, neural
  pose correctives, an FBX per LOD; no eyeballs, mouth interior or textures; 45 identity parameters. The
  notes' rank 2.
- SOMA-X puts MHR, Anny and SMPL on one 77-joint UsdSkel rig (mid LOD 18,056 verts); its fast path is
  NVIDIA Warp (NVIDIA-only), with a PyTorch CPU path at 12.1 ms per mesh.
- GNM Head (Google, 2026) is a scan-based head with eyeballs, teeth, tongue and neck, identities sampled by
  gender and ethnicity; body models are on its roadmap.
- ICT-FaceKit: a light-stage-scanned face with ARKit-named expressions and eye, teeth, gum and eyelash
  geometry; unmaintained since 2020.
- FLAME 2023 Open is CC-BY-4.0; earlier FLAME, SMPL-X, STAR and SUPR carry non-commercial research licences.
- MB-Lab (archived) and CharMorph carry AGPL-3 mesh and morph data; CharMorph also has CC-BY bases; its
  last release was 2025-03.
- MakeHuman 2 is a standalone Python app (PySide6 + OpenGL): AGPL code, CC0 assets, alpha.
- Microsoft Rocketbox (MIT, archived 2022): 115 rigged, textured, low-poly avatars with clothes baked in —
  library content, not a creator base. Blender Studio's Human Base Meshes: CC0 clean quad meshes with
  multires detail and UDIM UVs, no morphs, no rig.
- Open auto-riggers: UniRig (MIT, ≥ 8 GB), SkinTokens/TokenRig (MIT, ≥ 14 GB), Puppeteer and MagicArticulate
  (Apache-2.0), Make-It-Animatable (MIT) — most need CUDA (NVIDIA only). Rigify (GPL-2.0+) is a core
  Blender add-on.
- Out as paid only (the user, 2026-10-29): Human Generator, Auto-Rig Pro. Free but closed: MetaHuman (free
  under the UE EULA below $1M revenue, usable in other engines, no AI training) and VRoid Studio — at most
  something a user imports.
- Gaps: no source compares any open base's realism with CC5 or MetaHuman; mesh quality (edge loops,
  subdivision) is undocumented for every candidate; Mutable, Bevy, Daz, Mixamo and VRoid terms unchecked.

Second pass done 2026-10-29: [`../plans/2026-10-29-research-05-bases-pass2.md`](../plans/2026-10-29-research-05-bases-pass2.md).
The user's bar since 2026-10-29 (TASKS): characters at "the quality of cc5 and metahuman characters or better".

*web, 2026-10-29* — re-checked by this session (GitHub's API and the repo's README):

- `localai-org/skin-tokens.cpp`: Apache-2.0, "A C++23/GGML port of" SkinTokens — "automatic skeleton and
  skin-weight generation on CPU or Vulkan" (Vulkan can be switched off); created 2026-08-28, last push 2026-10-19,
  232 stars. GGML is the library under the web kit's llama.cpp and stable-diffusion.cpp (§10).

*agent, 2026-10-29* — S4's pass 2, sources per fact there:

- Auto-rigging is no longer NVIDIA-only: besides the C++ port above, ONNX and Apple ports of SkinTokens exist
  (the Apple one says it isn't ready); UniRig's skeleton stage runs anywhere through third-party ONNX/WebGPU
  ports, its skin-weight stage stays CUDA-only. Checkpoint licences: UniRig and SkinTokens MIT; Puppeteer,
  MagicArticulate and Make-It-Animatable Apache-2.0. Make-It-Animatable trains on 95 Mixamo characters and 2,453
  Mixamo motions (a non-staff Mixamo FAQ post says no ML training).
- GNM Head: 17,821 vertices, shipped as quads and as triangles, 253 identity and 383 expression parameters, 4
  joints, 7 UDIM tiles; its weights are Apache-2.0.
- MakeHuman's hm08 is all quads, made for subdivision: 14,766 faces; the raw mesh has 19,158 vertices (body
  alone 13,380, including helper geometry in the rest). *Measured 2026-10-29 in MPFB2's `base.obj` (commit 6ff1eb35):
  19,158 vertices, 21,334 UVs, 18,486 faces, all quads, 13,378 of them in the body (vertices 0–13,379); 144 vertex groups
  in `basemesh_vertex_groups.json` (`body` 13,380, `HelperGeometry` 4,778, `JointCubes` 1,000, 125 `joint-*`); 1,258
  `.target.gz` files, 20 of them empty on purpose (the "average" macro targets — the base already is that shape); Blender
  5.3's OBJ importer keeps the vertex order. MakeHuman's units are decimetres (MPFB2's METER scale is 0.1); a target row is
  "index dx dy dz" in Y-up, read as (x, −z, y). The 14,766 above was wrong for the whole mesh.*
- MHR and SOMA-X are triangle meshes as their code evaluates them; SOMA-X's docs admit linear-blend-skinning
  "candy-wrapper" artefacts at the elbow and shoulder.
- Humanizer (Godot) went Unlicense → CC0 (2025-01) → AGPL-3.0 (2025-08); the Godot asset listing shows the CC0
  v2.2.0. Rocketbox: 53 body and 28 facial bones (the agent's count of a Headbox file).
- Unreal's Mutable is production-ready in UE 5.8 (Unreal only). ATLAS was merged into MHR. SMPL's commercial use
  is paid only. The only open (CC0) strand hair found is MakeHuman's hair-editor pack (16 styles MPFB2 lists — was "7": that
  was its scalp list alone; read below, 2026-10-29). LHM is NVIDIA-only and
  depends on non-commercial Sapiens and SMPL-X.
- Still open: no source compares any open base's realism with CC5 or MetaHuman; no source documents edge loops
  for any base; MB-Lab's vertex counts (~18.2k / 18.0k) are the agent's estimate from file sizes.

*web, 2026-10-29* — read by the Opus review of the standards spec (`../plans/2026-10-29-spec-review-opus.md`) at
MPFB2's source (`makehumancommunity/mpfb2`, master, GitHub tree API and raw files) and MakeHuman's asset-pack page:

- MPFB2's data for hm08: `data/targets/target.json` — 23 groups, **234 slider categories**, each with `label`,
  `targets`, `has_left_and_right`, `opposites`; `data/targets/macrodetails/macro.json` — macro targets (gender, age with
  baby/child/young/old parts, muscle, weight, …) and their combinations; `data/rigs/standard/` — rigs `default`,
  `default_no_toes`, `game_engine`, `game_engine_with_breast`, `mixamo`, `mixamo_unity`, `cmu_mb`, `openpose` with
  matching `weights.*.json`, plus Rigify rigs; `data/uv_layers/` (14 alternative UV layers); `data/node_trees/` (skin,
  enhanced skin, procedural eyes).
- `rig.game_engine.json`: **53 bones in UE4-Mannequin names** (`Root`, `pelvis`, `spine_01–03`, `neck_01`, `head`,
  `clavicle_*`, `upperarm_*`, `lowerarm_*`, `hand_*`, `thumb/index/middle/ring/pinky_01–03_*`, `thigh_*`, `calf_*`,
  `foot_*`, `ball_*`). Each bone's head and tail is placed by `"strategy": "CUBE"` with a `cube_name` (e.g.
  `joint-l-foot-1`) — the joint cubes of the helper geometry.
- MHCLO (`docs/fileformats/mhclo.md`): MakeHuman's format for every mesh fitted to the base — "clothes … hair and eyes
  to full body proxy meshes"; per asset vertex an exact base vertex or `<v1> <v2> <v3> <w1> <w2> <w3> <dx> <dy> <dz>`;
  `z_depth` (render/layer order, default 50); `delete_verts` (base vertices hidden when worn); `x/y/z_scale` references;
  author, licence and description header lines.
- MPFB2's `faceservice.py`: `ARKIT_FACEUNITS` (the 52 ARKit names), `MICROSOFT_VISEMES` (22), `META_VISEMES` (15:
  `viseme_aa`, `viseme_CH`, `viseme_DD`, `viseme_E`, `viseme_FF`, `viseme_I`, `viseme_kk`, `viseme_nn`, `viseme_O`,
  `viseme_PP`, `viseme_RR`, `viseme_sil`, `viseme_SS`, `viseme_TH`, `viseme_U`); an expression JSON format keyed by ARKit
  face-unit names (`docs/fileformats/expression.md`). The shapes come from asset packs: MakeHuman's asset-pack page lists
  **Faceunits 01** (ARKit-style), **Visemes 01** (Microsoft) and **Visemes 02** (Meta/Oculus) as CC0 "functional asset
  packs" (static.makehumancommunity.org/assets/assetpacks.html).

*web, 2026-10-29* — re-checked for the user's "is there another better body … i feel you ddint reasearch well" and
"we need to create non human body as well like creatures just like cc5 allows" (Opus re-check of the review):

- A fresh search for free Blender body add-ons finds MPFB2 as the only free, maintained one (its extensions.blender.org
  listing); the others are paid — Transhuman 4 Blender ($100+, sm5.gumroad.com), DanilGOE's "Realistic Male/Female
  Character Creator" bases on Superhive — or are the round-one entries above.
- Creatures: CC5's "Creature" is an imported model with its own skeleton, "no facial controls, nothing swappable",
  animated "only by key-frames or its own embedded motions" (§2, S2 pass 2). Rigify in Blender main ships metarigs
  `Basic` (human, quadruped), `human`, and `Animals/` `bird`, `cat`, `horse`, `shark`, `wolf`
  (projects.blender.org API, `scripts/addons_core/rigify/metarigs`). CharMorph's docs say it is "explicitly designed
  to be modular and support any morphology such as Humanoid, Animal, insect" and name no non-human base. SMAL (the
  research quadruped shape model, learned from 41 animal toys): SMALify's code is MIT (2024-11-02); the SMAL model
  files' own terms were not read. No open, commercially usable creature body with sliders was found.
- The user, verbatim: "these things might be good to look at CharMorph for code features or how to do something just
  to n0ote" — CharMorph (GPL-3.0 code; AGPL-3 / CC-BY body data, §5 above) is a code and method reference: its
  "alternative topology" morph transfer (moving sliders onto another mesh — the fallback-body case), its real-time
  asset fitting, and its any-morphology design (creatures). Study and reuse of code only; its body data is not shipped.
- Fallback bases (the user: "if makehuman doesne work could you Custom / Clean Quad Base Mesh … i want standard if we
  can so we can share with other 3d engines"): Blender Studio's Human Base Meshes v1.4.1 (CC0, 2025-01-20, Blender
  4.2 LTS+; quad topology for subdividing, closed volumes, face sets, UDIM UVs, multires detail on the realistic
  assets; 17 meshes incl. full male and female figures; no morphs, no rig — Blender 3.6 asset-bundle release notes,
  cgchannel 2023-06-28). Reallusion's free CC base (5 rigged models, FBX/OBJ/ZTL, "uniform quads and edge loops",
  150+ facial morphs; reallusion.com free-3d-character-base page) falls under the EULA's CC Base Model clause, which
  bars use "in any character generation system" (§2) — not a base. No source names a cross-app standard human mesh;
  every app has its own (CC, Daz Genesis, MetaHuman, MakeHuman).
- GNM v3.0's model file, read as plain arrays (2026-10-29, `.dev/cache/gnm/v3_0/gnm_head.npz`, SHA-256 matching
  `v3_0/checksums.sha256` on `google/gnm-v3`, Apache-2.0): 17,821 vertices, 17,662 quads, 253 identity directions
  (`head_000`–`head_169`, 3 eyeball, 80 teeth), 383 expressions, 4 joints (`neck`, `head`, `left_eye`, `right_eye`),
  46 vertex groups, components `skin`, `left_eye`, `right_eye`, `upper_teeth_and_gums`, `lower_teeth_and_gums`,
  `tongue`; metres, Y up, facing +Z (eyes at ±30.8 mm, as hm08's eye joint cubes). Wrapped onto hm08: fit mean 0.87 mm,
  p95 2.17 mm; 3,340 head vertices take GNM's full shape, 781 a fade, 338 none (crown, shoulder tops, low neck).
  MPFB2's head span references measured on `base.obj`: x 5399–11998 (14.8 cm), y 791–881 (23.3 cm), z 962–5320
  (19.2 cm), as its MHCLO example uses them. Installing GNM's own package from GitHub was refused by Claude Code's
  permission check ("Code from External"), so no GNM code is run.
- Skin colour from chromophores (R5's physically based melanin and haemoglobin layers), read 2026-10-29: Donner &
  Jensen, "A Spectral BSSRDF for Shading Human Skin", EGSR 2006 (the PDF from graphics.ucsd.edu, §3.3–§3.5): eumelanin
  σa = 6.6×10¹⁰·λ^−3.33 mm⁻¹ (eq. 3), pheomelanin 2.9×10¹⁴·λ^−4.75 (eq. 4), baseline 0.0244 + 8.53·e^−(λ−154)/66.2 (eq. 5),
  epidermis Cm(βm·em + (1−βm)·pm) + (1−Cm)·baseline (eq. 6), dermis Ch(γ·oxy + (1−γ)·deoxy) + (1−Ch)·baseline with
  γ = 0.75 (eq. 7), σs' = 14.74·λ^−0.22 + 2.2×10¹¹·λ^−4 (eq. 8, halved in the dermis), epidermis 0.25 mm, n = 1.4;
  parameter ranges Ch 0.001–0.1, Cm 0–0.5, βm 0–1 (Table 1). Haemoglobin: Prahl's molar extinction (OMLC, 1998,
  250–1000 nm). Colour: CIE 1931 2° and D65 (files.cie.co.at/Publications-datasets/). Calibration data: NIST's
  "Reference Data Set of Human Skin Reflectance" (Cooksey, Allen & Tsai 2017, doi:10.18434/M38597, public domain): 100
  people, R1–R3 and their average, 250–2500 nm. With Kubelka–Munk for both layers the measured spectra are fitted best
  at an epidermal backscatter of 0.22 × KM's 0.75σs': mean RMS 0.0098, worst 0.020 over 400–700 nm (plain KM 0.039;
  an absorbing-only epidermis over-darkens dark skin). Fitted melanin 0.56–5.1% (median 1.0%), blood 0.7–6.3% (median
  1.6%) — the NIST set leans light to medium. The Monk Skin Tone Scale (CC BY 4.0) was looked at as a tone target; its
  page is a script app and no source gave values that could be checked, so it isn't used.
- MetaHuman's face names on disk (`F:\Epic\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCoreTechLib\Content\ArchetypeDNA\SKM_Face.dna`,
  11.2 MB, byte scan 2026-10-29, for the spec's item 10): 373 distinct `FACIAL_[CLR]_*` joint names, among them
  `FACIAL_C_FacialRoot`, `FACIAL_C_Jaw`, `FACIAL_L_Eye`/`FACIAL_R_Eye`, `FACIAL_C_TeethUpper`, `FACIAL_C_TeethLower`,
  `FACIAL_C_Tongue1`–`4`; mesh names `head`, `teeth`, `saliva`, `eyeLeft`, `eyeRight`, `eyeshell`, `eyelashes`,
  `eyeEdge`, `cartilage` (each `<name>_lod0_mesh` at LOD0).
- Reallusion's spine mapping (`soupday/cc_blender_tools` `rigify_mapping_data.py`, read 2026-10-29): Rigify `spine` ↔
  `CC_Base_Hip`, `spine.001` ↔ `CC_Base_Waist`, `spine.002` ↔ `CC_Base_Spine01`, `spine.003` ↔ `CC_Base_Spine02`,
  `spine.004` ↔ `CC_Base_NeckTwist01`, `spine.005` ↔ `CC_Base_NeckTwist02`, `spine.006` ↔ `CC_Base_Head`; its
  `GAME_BASE_BONE_MAPPING` puts `spine.001`–`.003` on UE4's `spine_01`–`spine_03` (UE4 has three spine bones) and splits
  `spine.004`/`.005` 50/50 onto `neck_01`; Rigify's `chest` control sits on `ORG-spine.002` (= `CC_Base_Spine01`). So
  by humanoid role CC's `Waist` is spine, `Spine01` chest, `Spine02` upper chest — UE5 `spine_01`, `spine_03`,
  `spine_05` (the review's first fix had used the UE4 table).
- Rigging and motion services (the user: "did you look at apps like meshy https://www.meshy.ai/features/ai-animation-generator
  could that be useful https://mesh2motion.org/ https://www.mixamo.com/#/"), read 2026-10-29:
  - **Mesh2Motion** (`Mesh2Motion/mesh2motion-app`, 3,622 stars, pushed 2026-10-26; desktop app
    `mesh2motion-desktop`): "Import a 3D Model and automatically assign and export animations … similar to … Mixamo, but
    … more flexible so it can support other model and skeleton types"; "The code and platform are all licensed under the
    very permissive MIT license. The art assets (3d models, rigs, animations) are all licensed under CC0" (README).
    Its site: "Animation rigs for Birds, Dragons, Spiders, Kaiju, Foxes, Horses, Fishes, Snakes, … and Humans"; "Over 170
    animations"; import GLB, GLTF, DAE, FBX; export GLB or FBX; an offline version. A TypeScript/Vite web app.
  - **Meshy**'s animation generator: auto-rigging ("under 30 seconds") plus preset motions ("600+ preset motions"; the
    page also says "100+"); "humanoids, bipeds, quadrupeds, and stylized figures"; FBX and GLB out; a 100-credit free
    tier, "Free-plan models use CC BY 4.0; paid plans unlock a Private license"; a web service with an API. No
    text-to-motion or video capture on that page.
  - **Mixamo** (Adobe's free web service): auto-rig and motion library; terms forbid AI/ML training (§7); no public API
    found; already an import profile (`mixamorig:` names, skeleton §1.4).
- Human Generator, read at its own site (the user: "did you look at https://humgen3d.com/"; round one read only its
  Superhive listing): 100+ body and face adjustments, a face rig with ARKit iPhone capture, particle hairstyles,
  clothes, a pose library, Rigify-compatible rigs, LODs, a batch generator, a Python API, texture baking (home page).
  "The add-on and its Python source code are licensed under the GNU General Public License"; its textures and 3D models
  are under the separate "Human Generator Digital Asset License": no sharing or selling of the assets, customised
  models included, and no sharing of "`.fbx` files of 3D models created with Human Generator" (license FAQ). $68
  personal / $128 commercial, lifetime, one user; the trial has "limited functionality and content" and watermarked
  4K textures (pricing page). Stays out as paid; its body can't be shipped or used as a base; its GPL code is readable.

*measured, 2026-10-29* — hair for step 1.6, on Blender 5.3 beta and MPFB2 `6ff1eb35`:
- **MakeHuman's hair-editor pack** ([haireditor.html](https://static.makehumancommunity.org/assets/assetpacks/haireditor.html),
  *page read*): "This pack contains two blend files ("hair.blend" and "fur.blend"), both by Tomáš Klecer"; the packs
  page's functional section: "The assets are shared under CC0" ([assetpacks.html](https://static.makehumancommunity.org/assets/assetpacks.html)).
  `files2.makehumancommunity.org/functional/haireditor.zip` (mirror `files.`): 18,251,712 bytes, Last-Modified
  2026-10-24, SHA-256 `e47ade8e…cbe72`; `hair.blend` 27,310,677 bytes (`8566a128…f080`), `fur.blend` 19,207,241.
  MPFB2 tells an old pack from the current one by `hair.blend`'s size (`is_hair_pack_outdated`).
- **What `hair.blend` holds** (listed in Blender 5.3): 28 objects. MPFB2's lists (`haireditorpanel/properties/*.json`)
  name 16: scalp `short_hedgehog` (42,504 curves), `hair_to_shoulder`, `short_crown`, `short_cap`, `short_ponnytail`,
  `back_pigtail` (+ a `_brace` hair-tie mesh), `tail_base`, `empty_hair` (0 curves, the template for grooming by hand);
  eyebrows `wild_eyebrow`, `wild_thick_eyebrow`; facial `wild_thick_beard`, `wild_thick_moustache`, `wild_beard`,
  `wild_moustache`; other `basic_lashes_upper`, `basic_lashes_lower`. Not listed: `straight_hair_to_shoulder`,
  `hedgehog`, `basic_short_hair` and `*_cards` meshes. `fur.blend`'s 15 (`fur_assets.json`): full body, hands, forearms,
  arms, chest, back, neck, belly, thighs, lower legs, feet, mane, face, head, inner arms. Every style is a Curves object
  (`surface` empty, `surface_uv_map` "UVMap", a `surface_uv_coordinate` attribute) whose modifiers are the pack's own
  copies of Blender's hair node groups — Surface Deform (one Deform Curves on Surface node) first, then Set Hair Curve
  Profile, Curl, Hair Curves Noise, Frizz, Roll, Clump, and Duplicate, Braid or Attach Hair Curves to Surface in some;
  materials are "Hair shader EEVEE" groups on Principled BSDF. No text blocks, no drivers.
- **How MPFB2 attaches a style** (`apply_hair_operator.py`, `haireditorservices.attach_curves_to_basemesh`): load the
  object (and `<style>_brace`), set the Curves `surface` to the body, parent to it with an identity inverse ("The asset
  was groomed on a character standing at the origin"), and first add Blender's empty hair (`ensure_hair_setup`: "or the
  hair asset wont behave correctly"). Without the body's rest position Surface Deform reports "Evaluated surface
  missing attribute: "rest_position"" and leaves the strands where they were groomed; `Object.add_rest_position_attribute`
  turns it on.
- **The floor:** MPFB2's `create_human(feet_on_ground=True)` lifts the mesh by its lowest body vertex (index < 13,380,
  shape keys mixed) and applies it — 0.8177 m at the default macros. hm08's `base.obj` is centred on the origin, so a
  body left there sits 0.8 m below the styles. Lifted, with rest position on: roots to the skin median 0.1–1.4 mm, 95th
  percentile 0.3–3.8 mm (the beards highest), worst 5.6 mm, over the 15 styles with strands; the same after age 0 (a baby). `tail_base` alone stayed at
  5.5 mm median / 16.6 mm p95 until its Attach Hair Curves to Surface modifier's empty `Surface` input was set to the
  body: 0.3 / 0.8 mm. Blender 5.3's Principled Hair BSDF defaults: Chiang model, Melanin 0.8, Melanin Redness 1.0.
- **Scalp masks tried and dropped** (a procedural groom: Generate Hair Curves inside a mask): MakeHuman's hair helper
  (`helper-hair`, 428 vertices, y 0.201–0.85 m in MakeHuman's axes — it runs to the shoulders for long hair — a median
  15 mm, p90 39 mm, above the skin) and MPFB2's `uv_layers/scalp_solid.json.gz` (its MakeUp "scalp" focus region: 520
  faces, 567 vertices) both reach the forehead: rays along the skin's normals into the helper reach the front midline
  9 mm below the eye's centre, `scalp_solid` from 23 mm above it; the pack's own `short_hedgehog` hairline is 56 mm
  above it (front midline, measured on the attached style).
*web, 2026-10-29* — the eye shells (step 1.5: occlusion and tearline), public docs only:
- **CC5** ([Eye Occlusion](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Eyes/Digital-Human-Eye-Occlusion-Shader.htm),
  *page read*): "The topmost mesh layer for the realistic eyes is the Eye Occlusion, which simulate the shadow cast from
  the eyelids to prevent over-exposure on the eyeballs"; its settings pages are Blur, Shadow 1, Shadow 2 and Vertex
  Offset (not read). [Tear Line](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Eyes/Digital-Human-Tearline-Shader.htm)
  (*page read*): the layer under the occlusion, to "simulate the moisture and the tear reflectivity on the eyeballs and
  the tear ducts"; CC5 changed its UVs because CC4's normal-map tiling was "unevenly distributed". CC4's
  [Tear Line settings](https://manual.reallusion.com/Character-Creator-4/Content/ENU/4.0/15_Digital_Human_Shader/Eyes/Digital-Human-Tearline-Tearline.htm)
  (*page read*): Depth Offset ("adjust the depth of the entire Tear Line mesh"), Detail Amount, Detail Scale U and V (a
  tiling normal detail), Edge Fadeout, Roughness; the sub-section "can be used to offset the Eye Occlusion mesh in
  order to snuggly fit the eyeballs". [New Eye Elements](https://manual.reallusion.com/character-creator-4/Content/ENU/4.0/15_Digital_Human_Shader/Eyes/New-Eye-Elements.htm)
  (*page read*): both "will be changed along with the movement of eye sockets when morphing and performing facial
  animations"; they can be deleted and recreated in CC.
- **MetaHuman:** the face's meshes `eyeshell` and `eyeEdge` (names above); Epic's material set has `EyeShell` and
  `LacrimalFluid` slots (MetaHumanCharacter API, *search snippet only*). A forum user with a custom template mesh
  reports the eyeshell and edge clipping into the eyeball ([forum](https://forums.unrealengine.com/t/eyeshell-and-edge-not-aligning-to-eyeball-with-custom-template-mesh/2764072),
  *search snippet only*).
- Not found: how either vendor shapes the shells (widths, offsets, how they are generated); no Blender-specific
  method. Both are real-time fixes — a shadow and a wet line the rasteriser misses at that scale.
- Lead for the face rig (step 7), contents not yet read: MakeHuman's functional packs also list "Faceunits 01: ARKit
  style face units" and "Visemes 01/02" (Microsoft and Meta/Oculus style), CC0.

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

Out, on the user's word 2026-10-29 (TASKS): NVIDIA Omniverse ("it only works on nvidia cards"), anything that
only comes paid, core parts that run on one GPU vendor only, and Unity (its free tier is far smaller than
Unreal's — below). Unreal is in ("unreal is ok i use it all the time").

*web, 2026-10-29* — unity.com/products/unity-personal and unity.com/products/pricing-updates (pages read; no
page dates shown):

- Unity Personal is free for "individuals and small organizations with less than $200K USD of revenue and funds
  raised", measured over the last 12 months; above it a paid plan is required. The $200K line came with Unity 6
  on 2024-10-17.
- Unity Pro: $2,310 a year per seat (or $210 a month), for $200,001–$24,999,999 of funding or annual revenue
  (since 2025-01-01), after a 5% rise from 2026-01-12; Enterprise above $25M, custom-priced.
- The Runtime Fee was cancelled on 2024-09-12, for Unity 6 and every other version.

*web (search-result summaries), 2026-10-29* — Epic's own licence page refused the fetch (403):

- Unreal is free until a product passes $1,000,000 of gross lifetime revenue, then a 5% royalty
  (developers.meta.com Unreal licence docs, updated April 2026; seeles.ai guide). A seat-based price of $1,850
  a year for non-game work appears in one third-party guide only — unverified; the §6a agent gets Epic's terms.

Round one done 2026-10-29: [`../plans/2026-10-29-research-06a-engine-routes.md`](../plans/2026-10-29-research-06a-engine-routes.md)
(a score table, 10 criteria × every base in scope, and route-and-language pairs) and
[`../plans/2026-10-29-research-06b-own-engine-and-layers.md`](../plans/2026-10-29-research-06b-own-engine-and-layers.md)
(render libraries, UI toolkits, languages, embedding, AI testing, how professional apps are built, effort).
The "to verify" above — MetaHuman Creator in the Unreal editor since 5.6 — is confirmed (below).

*web, 2026-10-29* — re-checked by this session (GitHub's API, O3DE's `LICENSE.txt`, projects.blender.org's API):

- Godot (godotengine/godot): MIT, latest 4.7.2-stable (2026-08-18), 119,262 stars. O3DE: Apache-2.0, or MIT
  at the user's option; latest 2605.0 (2026-05-27); 9,802 stars. Flax: latest 1.13.7012 (2026-10-21), 7,094
  stars. Bforartists: latest v5.2.0 (2026-07-29), 812 stars.
- Blender Lab hosts an MCP server repo, `lab/blender_mcp` on projects.blender.org (created 2026-02-21,
  updated 2026-09-29). Its README didn't load by raw URL; its version and licence come from the agent.

*web, 2026-10-29* — read by the standards-spec session (Gitea API `repos/lab/blender_mcp` and the raw `readme.md`;
the HTML page returns 403 to scripts; excerpt saved in `../plans/2026-10-29-spec-evidence/README.md`):

- `lab/blender_mcp` is Python, 33 stars, 6 releases, 23 open issues; top level `addon/blender_mcp_addon/`, `mcp/blmcp/`
  (with `pyproject.toml` and `manifest.json`), `chat_client/`, `tests/`, `readme_tools.rst`, `readme_local_llm.rst`.
- Its readme: "two components that communicate over a TCP socket: A Blender add-on that runs inside Blender and
  executes requests. An MCP server that runs as a separate process, launched by the MCP client"; data flow
  `MCP Client ⇐ MCP/stdio ⇒ blender-mcp ⇐ TCP socket ⇒ Blender Add-on`; the add-on has preferences for host, port and
  auto-start, configurable polling intervals, client-timeout eviction; "background mode requires requests to complete
  synchronously and rejects deferred results"; tools are one module each, auto-discovered; `_toolcode` modules hold
  code "that runs inside Blender (sent to the add-on for execution)". The lowercase `readme.md` is the file; a
  `README.md` fetch is 404.

*web, 2026-10-29* — Epic's own "Unreal Engine End User License Agreement for Publishing", **version 15**,
downloaded by this session from Epic's CDN (`cdn2.unrealengine.com/…/UnrealEngineEULA_for_Publishing_v15-….pdf`,
147,624 bytes; read as text). It names the store "Marketplace", not Fab, so it predates the current text; the
live EULA and its change log (unrealengine.com) refuse scripted reads (403, not worked around):

- §1(A)(a): the Licensed Technology goes to end users "in object code format only as an inseparable part of a
  Product"; "The Product may not contain any Paid Content Distributed in uncooked source format or any Engine
  Tools."
- §25: "Engine Tools" means "(a) editors and other tools included in the Engine Code; (b) any code and modules
  in either the Developer or Editor folders, including in object code format, whether statically or dynamically
  linked; and (c) other software that may be used to develop standalone products based on the Licensed
  Technology." "Product" means anything made using the Licensed Technology, "regardless of how much or little …
  is used".
- §1(A)(b): Engine Code may go to other Engine Licensees; a public Distribution that includes Engine Tools "must
  take place either through the Marketplace (e.g., for distributing a Product's modding tool or editor to end
  users) or through a fork of Epic's GitHub UnrealEngine Network".
- §1(A): "There is no restriction on your Distribution of a Product … that does not include any Engine Code …
  and does not require any Licensed Technology … to run" ("Unrestricted Products") — e.g. exported files.
- §1(A)(f): an integration of a language other than C++ "must be Distributed free of charge to all Engine
  Licensees, must be available in source code form … and must permit Distribution free of charge, on all
  platforms, in any Product".
- §5: a royalty of 5% of worldwide gross revenue, with "The first $1,000,000 in lifetime gross revenue for each
  Product" exempt.

*web (search-result summaries), 2026-10-29* — Epic's EULA change log, through search snippets only: update 20
merged the Publishing and Creator agreements into one, moved royalties into a Royalty Addendum (adding a 3.5%
rate for "Launch Everywhere with Epic Release"), and put Content under a separate Epic Content License
Agreement; update 21 restricts using MetaHuman characters and animation curves with AI technologies and defines
cloud features. A third-party tracker (conductatlas.com) dates the current EULA 2026-05-05 and quotes the Engine
Tools clause with "the Fab Marketplace". Whether the v15 wording above survives unchanged in the current text is
unverified — the second pass (S5) looks for a readable current copy; otherwise the user reads the live page.

*agent, 2026-10-29* — 06a, sources per fact there:

- Unreal 5.8 (2026-06-17), likely the last 5.x; UE6 previews expected late 2027. The best real-time human
  out of the box (MetaHuman: skin, strand groom, eyes, rig) and the fullest feature set (Sequencer,
  Control Rig, Chaos cloth, hair and flesh, Movie Render Graph, Live Link).
- Epic's EULA, from search snippets only (Epic's pages return 403): "The Product may not contain … any
  Engine Tools" — the editor and its code go only to other Unreal licensees (Fab, the Epic store, a GitHub
  fork). So JustStage on Unreal is either an editor plugin for people who install Unreal (~60–190 GB), or a
  packaged app that rebuilds the authoring tools itself. Pricing (snippets): games pay 5% above $1M per
  product; non-game companies above $1M a year pay $1,850 a seat a year — a model that excludes apps
  licensed to end users that use Unreal at runtime.
- MetaHuman Creator, Mesh to MetaHuman and the Animator moved into the Unreal editor in 5.6 (cgchannel,
  2025-06-04); auto-rigging and texture synthesis run on Epic's cloud; Epic recommends an RTX 3070 / RX 6800
  XT for Creator; the Animator is Windows/DX12 only.
- Godot 4.7 (MIT) is the most "ours" base: its editor is itself a Godot app in C++, LibGodot (since 4.6)
  embeds the engine in another app, glTF saves at runtime, GDExtension takes C++ and Rust. But a realistic
  human is ours to build: subsurface scattering only in Forward+, card hair, no strand hair, no eye shader;
  image tests need a GPU (no RenderingDevice headless).
- Blender 5.2 LTS already has most of CC5 + iClone (sculpting, rigging, animation editors, node-based cloth
  and hair, EEVEE, Cycles, USD/glTF/Alembic/FBX) on every GPU vendor, and is the easiest to drive by AI
  (`-b --python`, `gpu.init()` headless in 5.2, screenshots, an official MCP server). Costs: GPL (published
  add-ons "shared under a GPL compliant license") and Blender's UI framework — an application template reworks
  most of the UI; new editor types or core changes need a fork, as Bforartists is (was: "a reworked UI means a
  fork" until 2026-10-29 — see the *web* entry below).
- O3DE 26.05 (Apache-2.0 / MIT): TressFX strand hair, EMotionFX, motion matching, hardware ray tracing, a Qt +
  Python editor; its macOS editor is experimental, installs take 40–100+ GB, few shipped titles.
- Stride 4.4 (MIT) has the best image-test setup, but its editor is WPF — Windows only. Bevy 0.20 (no editor,
  a breaking release every ~3 months) and Fyrox 1.0 (OpenGL, no GI) are early. Flax charges 4% above $250k a
  quarter; editor redistribution and open-sourcing a Flax app aren't stated.
- Nothing was measured on §1's card; the notes' open list names a per-finalist test (a realistic head with
  strand hair, a skinned body, playback fps).

*web, 2026-10-29* — Blender's UI without a fork, checked by this session at Blender's manual source
(`projects.blender.org/blender/blender-manual`, `manual/advanced/app_templates.rst`) and code
(`github.com/blender/blender`, `scripts/startup/bl_ui/space_view3d.py`):

- Application templates "allow you to define a re-usable configuration that can be selected to replace the
  default configuration"; "people can build their own *applications* on top of Blender that can be easily
  distributed". A template brings its own startup file, themes, add-ons, keymaps and splash; its Python is for
  "Modifying and replacing parts of the user interface" and "Defining new menus, keymaps and tools".
- Blender's headers, menus and panels are Python classes — `space_view3d.py` alone defines 276 — so a template
  can unregister Blender's and register its own.
- Not checked at a source (the lead's knowledge, to confirm in S8): Python can't add a new editor type (space
  type), change the widget toolkit or the window system; it can draw in the viewport (the `gpu` module), add
  gizmos and custom node editors. The user, 2026-10-29: a Blender fork is an allowed route (TASKS).

*web, 2026-10-29* — read at Blender's sources by the standards-spec session (for the spec's USD, plugin and
animation pieces):

- **The USD hook API** (`source/blender/io/usd/intern/usd_hook.cc`, main; the docs example
  `doc/python_api/examples/bpy.types.USDHook.0.py`): a Python `bpy.types.USDHook` subclass may define `on_export(export_context)`
  (before the USD export is saved; the context gives `get_stage()`, `get_depsgraph()`, `get_prim_map()` — exported
  prim paths → Blender IDs), `on_material_export(export_context, bl_material, usd_material)` (`get_stage()`,
  `export_texture(image)`), `on_import(import_context)` (`get_stage()`, `get_prim_map()`),
  `material_import_poll(import_context, usd_material)` and `on_material_import(import_context, bl_material,
  usd_material)` (`get_stage()`, `import_texture(asset_path)`); if a hook's poll returns true the built-in Preview Surface
  and MaterialX importers are skipped for that material. The example calls `bpy.utils.expose_bundled_modules()` ("makes
  the `pxr` module available when running as the `bpy` PIP package") and then `from pxr import Gf, Sdf, Usd, UsdShade`;
  it writes custom layer data and a MaterialX `ND_standard_surface_surfaceshader` network on export and reads it back on
  import. So Blender bundles the USD Python module and gives extensions a documented way to write and read their own USD
  data during its native USD I/O. (docs.blender.org itself still refuses scripted reads — 403.)
- **The extension manifest** (`manual/advanced/extensions/getting_started.rst`, re-read): required `schema_version`,
  `id`, `version`, `name`, `tagline`, `maintainer`, `type`, `blender_version_min`, `license`; optional
  `blender_version_max`, `website`, `copyright`, `tags`, `platforms`, `wheels`; tables `[permissions]`, `[build]`
  (`paths`, `paths_exclude_pattern`), `[asset_library]` (`remote_url`, only for that type), `[build.generated]`
  (reserved). **No field lets an extension depend on another extension**; the page says nothing about extra keys.
- **Slotted Actions** (release notes 4.4, `animation_rigging.md`): "a single Action can animate multiple data-blocks at
  the same time"; a slot is bound to one data-block type; a new Python API for slots, layers, strips and channelbags; the
  old F-Curve/Action-group API is a backward-compatible legacy API working on the first slot.
- **Blender's bone naming page** (`manual/animation/armatures/bones/editing/naming.rst`, read through its rendered
  copy): mirroring and flipping recognise "lower or upper case 'L', 'R', 'left' or 'right'" with the separators `_`,
  `.`, `-` and space ("hand.l to hand.r", "hand_L to hand_R"), as suffix or prefix; a bare `handL` does not work; number
  extensions (`.001`) are removed before mirroring. So Unreal's `thigh_l`/`thigh_r` spelling works with Blender's tools.

*agent, 2026-10-29* — 06b, sources per fact there:

- No open, cross-vendor render library ships CC5-class humans: Filament's subsurface is "approximated",
  Wicked's hair is vegetation, The Forge carries a TressFX port. NVIDIA's RTX Character Rendering does skin
  and strand hair but is proprietary and Windows/Vulkan only. On any own-engine route, skin, strand hair and
  eyes are ours to build.
- macOS narrows the field: native Metal in wgpu, bgfx, Filament, The Forge, Wicked, Ogre-Next; Diligent's
  native Metal backend is commercial (out); MoltenVK has no Vulkan ray-tracing extensions; wgpu's ray
  tracing is experimental and Vulkan-only.
- The apps we copy are C++ cores with Qt UIs and embedded Python (Maya on Qt6/PySide6, Houdini 21 on Qt
  6.5.3, Daz Studio 6 on Qt 6.10 under LGPL, iClone's API on Qt 5.15.2). Blender, Cinema 4D, Unreal (Slate)
  and Godot draw their own UI.
- Qt's free line: Base (Core, GUI, Widgets, RHI) and Declarative (QML/Quick) are LGPL-3; Quick 3D, Quick
  Timeline, Graphs and Charts are GPL-3 or commercial only. QRhiWidget (Qt 6.7+) can host our own D3D12,
  Vulkan or Metal renderer.
- Dear ImGui is in shipped 3D tools (Substance 3D Modeler, Nomad Sculpt, MoonRay's GUI) but has no
  accessibility tree. egui (kittest) and Avalonia (headless) are the most AI-testable UI stacks, with no
  professional DCC behind them.
- C++ is the only language where every key 3D library is native (OpenUSD, PhysX, Jolt, ufbx, Embree, OIDN,
  OpenVDB, MaterialX, Manifold, meshoptimizer). Evidence on how well AI agents write each language is thin
  and conflicting (2025 benchmarks; none on graphics code).
- Python is the DCC scripting standard; nanobind is the lighter binding (Stable ABI). WebAssembly plugins are
  standardised (WASI 0.3, 2026-06-11; Wasmtime; Extism) but no DCC uses them yet.
- AI testing has standard parts: golden-image tests on software rasterizers (Filament on Mesa/SwiftShader,
  Bevy, wgpu with FLIP, Blender with oiiotool; Windows' WARP runs D3D12 including ray-tracing stages), a
  JSON-RPC/MCP control channel, UI tests through accessibility trees.
- Effort: years and many hands (Godot: 3,990 contributors, open since 2014); no public figures for Maya,
  Houdini or Unreal's editor.

Second pass done 2026-10-29: [`../plans/2026-10-29-research-06a-engine-routes-pass2.md`](../plans/2026-10-29-research-06a-engine-routes-pass2.md)
and [`../plans/2026-10-29-research-06b-own-engine-and-layers-pass2.md`](../plans/2026-10-29-research-06b-own-engine-and-layers-pass2.md).

*web, 2026-10-29* — re-checked by this session at the source:

- Epic's merged "Unreal Engine End User License Agreement" with its Royalty Addendum (Epic's CDN,
  `cdn1.epicgames.com/eulatracking-download/unreal_engine/en/v2/r1/…pdf`, fetched by S5, read here as text): "If your
  Product includes Engine Tools, it may only be Distributed pursuant to (C) above" — (C) being other licensees;
  the Engine Tools definition as in v15; North Carolina law, so it predates change-log update 20.
- O3DE's development branch holds `Skin.materialtype` (with `Skin_WrinkleMaps.lua`) and `Eye.materialtype` in
  `Gems/Atom/Feature/Common/Assets/Materials/Types` (GitHub's API).
- The Forge's README: "We switched to Ray Queries for the common Ray Tracing APIs on all the platforms we
  support", with a "Ray Queries on macOS" screenshot from an M2 Mac.

*web, 2026-10-29* — re-checked by this session for the route recs:

- blender.org/about/license: "Blender is released under the GNU General Public License"; blender.org code is "GNU
  GPL Version 2 or later"; Python add-ons, "if published", must be "shared under a GPL compliant license"; "What you
  create with Blender is your sole property." The page doesn't address forks (it links a separate Trademark Policy).
- Open-source Unreal plugins are common practice: GitHub's search finds 303 MIT-licensed repositories tagged
  `unreal-engine-plugin` (e.g. `TriAxis-Games/RealtimeMeshComponent`, 1,764 stars; `20tab/UnrealEnginePython`, MIT,
  2,908 stars). The EULA governs Epic's Engine Code inside them (snippets ≤ 30 lines), not the plugin's own code.

*agent, 2026-10-29* — S5's pass 2, sources per fact there:

- The current Epic EULA, quoted by a third-party tracker (ConductAtlas, the 2026-05-05 text): "If your Product
  includes Engine Tools, you may only Distribute it through either the Fab Marketplace or through a fork of Epic's
  GitHub UnrealEngine Network"; a seat per developer unless "you, together with any entities in your corporate
  group, have generated less than $1,000,000 USD in gross revenue over the last 12 months"; a 3.5% rate; New York
  law; bans on generative-AI training input and on MetaHuman AI databases; cloud-data terms. Still unread at
  Epic: the live text, the seat-purchase terms, the Content License (the user can download them from their Epic
  account's legal history, or read them in a browser).
- Unreal's runtime export is narrow: glTF export works at runtime without material baking; no built-in runtime
  FBX export (the FBX factory needs `UnrealEd`; only paid Fab plugins); USD stages load at runtime, no runtime
  export documented. Unreal's Python is editor-only. Unreal 5.8's MCP is an experimental editor plugin at
  `127.0.0.1:8000/mcp` with no authentication, running tool calls one at a time on the game thread.
- Flax's EULA (2023-10-31, read in full): no Engine Tools in a Product, no sublicensing of the source, and GPL,
  LGPL (except dynamic linking) and CC-BY-SA prohibited — so a Flax-based app can't be fully open source.
- O3DE: the Skin type has subsurface and transmission, dual specular and up to 4 wrinkle layers driven by vertex
  colour; the Eye type has refraction, iris, sclera and limbus. O3DE has no exporter (FBX is its main source
  format; glTF through Assimp is in development).
- Blender: Vulkan becomes the default in 5.3 (in beta until 2026-11-04) on Windows (not ARM) and Linux; no GPU
  skinning upstream (PR #149020 open, unmerged); 5.1 sped up shape-key playback (158.7 vs 39.2 fps in one
  chart). Bforartists 5.2.0 is a full release.
- Godot: Uniform, a commercial 3D sculpt-and-paint app, is built as a Godot 4 C++ module; no official MCP
  server, many community ones. Stride 4.4's editor runs on Linux through Proton/Wine and is being rewritten to be
  cross-platform. Fyrox's master branch has a wgpu backend.
- Open: Unreal's morph-target cap; whether its glTF exporter works in a Shipping build.

*agent, 2026-10-29* — S6's pass 2, sources per fact there:

- Ray tracing on macOS: only The Forge has working ray queries on Metal. Wicked Engine does inline ray tracing
  only on Apple-silicon Macs with macOS 26; Diligent has none (MoltenVK's ray-tracing change is unmerged);
  wgpu's ray tracing is Vulkan-only. Ray queries are the cross-platform path.
- Image tests on all three OSes: Mesa's lavapipe (CPU Vulkan) does Vulkan 1.4 including ray tracing, and wgpu
  runs it in CI on Linux and Windows; Metal has no CPU fallback, but GitHub's `macos-14` runner runs Metal
  (Bevy and wgpu use it).
- An AI agent can drive a Qt app with free tools: Qt's OS accessibility with pywinauto, Appium Mac2,
  QTest/PySide6 and Spix. Squish is paid-only (out).
- WebAssembly plugins in shipped apps (Flight Simulator, Figma, Zed, Helm 4): a real sandbox, but no threads, no
  exceptions, no native libraries, no GPU or UI access.
- Toolkits: GTK 4 is a weak fit (no Vulkan widget; Windows/macOS accessibility is a new build option, off by
  default); Flutter's multi-window and GPU layer are experimental; Slint has no docking; wxAUI docks but is
  accessible only on Windows.
- Corrections to round one: PEP 779 sets 15% speed and 20% memory limits for free-threaded Python, and Stable
  ABI support is undecided; "Cinema 4D on PySide6" came from a user, not Maxon; Marvelous Designer 2026.1 has a
  headless mode.
- Open: no controlled Rust-vs-C++ build-time comparison; no team sizes for Maya, Houdini or Unreal's editor;
  Marvelous Designer's UI toolkit; Cascadeur's core language (a job-ad snippet only).

## 7 · Building blocks

Round one done 2026-10-29: [`../plans/2026-10-29-research-07-building-blocks.md`](../plans/2026-10-29-research-07-building-blocks.md)
(33 job tables; distilled at the end of this section). Skin and hair rendering, blendshapes, cloth and hair simulation, auto-rigging,
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

*web, 2026-10-29* — re-checked by this session (GitHub's API; Jolt's `Docs/ReleaseNotes.md`):

- Jolt Physics (jrouwe/JoltPhysics): MIT, latest v5.6.0 (2026-07-11), 11,831 stars. v5.6.0 "Added a strand
  based hair simulation running on GPU" — guide and render hairs, grid-based hair-to-hair collision, roots
  skinned to the scalp — "still work in progress".
- Cycles (blender/cycles): Apache-2.0, last push 2026-10-26. Momentum (facebookresearch/momentum): MIT,
  v0.1.114 (2026-07-16).

*agent, 2026-10-29* — round one's building-blocks notes, sources per fact there:

- Jolt's GPU work runs on a compute layer with DX12, Vulkan, Metal and CPU back-ends; Jolt also has soft
  bodies (Cosserat rods since 5.4), ragdolls and deterministic simulation.
- Meta's MHR (Apache-2.0) is the one permissive alternative to SMPL (non-commercial; commercial terms through
  Meshcapade). SAM 3D Body outputs MHR from one photo; Momentum adds FK/IK and body-tracking solvers.
- FLAME 2023 Open is CC-BY-4.0; FLAME 2017–2023 are non-commercial.
- MPFB2's CC0 assets include clothes in the MHCLO fitting format, rigs, poses and expressions (§5).
- FBX: ufbx (MIT or public domain) reads it, and Blender 5.x's C++ FBX importer uses it. Writing: ufbx's own
  `ufbx-write` (MIT or Unlicense, "still a work-in-progress" — *web*, its README, 2026-10-29), Assimp's FBX exporter
  (BSD-3, "experimental"), or Autodesk's free closed FBX SDK (was: "there is no writer" in ufbx until 2026-10-29 —
  S8's second pass, §8).
- Cycles builds standalone or as a Hydra render delegate on CPU, CUDA, OptiX, HIP, Metal and oneAPI — the
  embeddable cross-vendor path tracer.
- Webcam face: MediaPipe Face Landmarker (Apache-2.0) — 52 blendshape scores, 478 landmarks. Live mocap
  interchange: the VMC protocol (OSC over UDP; the spec is MIT), spoken by SlimeVR, XR Animator, VSeeFace,
  Waidayo.
- Lip-sync: NVIDIA Audio2Face-3D is open (SDK MIT; models under NVIDIA's Open Model License, commercial use
  allowed) and fits 8 GB, but needs CUDA/TensorRT — NVIDIA only, so an optional part.
- Image-to-3D on 8 GB: Hunyuan3D-2 shape (6 GB; its licence excludes the EU, UK and South Korea), TripoSR (6
  GB, MIT), TripoSG and PartCrafter (≥ 8 GB, MIT). TRELLIS (16 GB) and TRELLIS.2 (24 GB) don't fit.
- Auto-rigging: UniRig (MIT, ≥ 8 GB), SkinTokens/TokenRig (MIT, 14 GB on CUDA); SkinTokens also runs on CPU or
  Vulkan through the GGML port `skin-tokens.cpp` (was: "both CUDA" until 2026-10-29 — §5's second pass).
- Text-to-motion: HY-Motion 1.0 needs 24–26 GB (its licence excludes the EU, UK and South Korea); MoMask, MDM
  and T2M-GPT are MIT/Apache code trained on HumanML3D, which comes from AMASS (non-commercial, and it forbids
  training models for commercial use).
- No open equivalent found for: Marvelous Designer (pattern-and-sew garments), MetaTailor (fitting any
  garment to any body — a packaged one), Cascadeur's physics tools, a ZBrush-class sculpt library (was: "… a
  ZBrush-class sculpt library, a texture baker, an FBX writer; and no cross-vendor GPU garment-cloth library" until
  2026-10-29 — S7's second pass found a garment-cloth solver, a baker and FBX writers, below).
- Open: the VRAM of many models is unstated; GPU-vendor support of most PyTorch models beyond "CUDA"; CMU
  mocap's terms; Blender's dyntopo and hair tools not checked; several licences unresolved.

Second pass done 2026-10-29: [`../plans/2026-10-29-research-07-building-blocks-pass2.md`](../plans/2026-10-29-research-07-building-blocks-pass2.md).

*web, 2026-10-29* — re-checked by this session (GitHub's API; ArmorPaint's `license.md` and README):
`st-tech/ppf-contact-solver` Apache-2.0, last push 2026-10-27, 4,581 stars; `armory3d/armorpaint` source under "The
zlib/libpng License" ("Distributed binaries are paid"), last push 2026-10-29, 5,435 stars; `pwilkin/trellis.cpp`
MIT, last push 2026-10-26, 368 stars; `MengZephyr/LoBoFit` BSD-3-Clause, last push 2026-07-04, 7 stars.

*agent, 2026-10-29* — S7's pass 2, sources per fact there:

- Garment cloth on any GPU: ZOZO's Contact Solver (Apache-2.0) does seam stitching on NVIDIA, AMD, Apple and CPU —
  offline only, and its README says it has never run on real AMD hardware.
- Texture baking: ArmorPaint's source has 14 bake types, including from a high-poly mesh; Unreal's Geometry
  Script also bakes. FBX writing: `ufbx_write` writes skinning, blend shapes and animation (work in progress; §8).
- Garment refit: LoBoFit (BSD-3, SIGGRAPH 2026, a pending-patent notice) and Unreal's Outfit Asset resizing — still
  no packaged open MetaTailor equivalent.
- Not NVIDIA-only after all: TRELLIS.2 runs on ROCm, Vulkan and Metal through trellis.cpp and natively in ComfyUI;
  SkinTokens through skin-tokens.cpp (§5); Audio2Face's weights ship as ONNX, with an Apple MLX port.
- Terms: Cascadeur's free plan is non-commercial and exports .casc only; Mixamo's terms forbid AI/ML training;
  Autodesk's FBX SDK licence allows linking and selling a product but not redistributing the SDK, and its
  open-source clause names GPL and LGPL.
- Hi3D v1.0 needs an NVIDIA GPU of compute capability 8.0+ — not the RTX 2070 Super (7.5).
- Still open: sculpting and Cascadeur-type physics have no embeddable open equivalent; CMU mocap's terms page
  (certificate rejected), the current Mixamo FAQ (403), OptiTrack NatNet's licence (429); VRAM of MagicArticulate,
  Make-It-Animatable, DiffLocks, GENMO; whether mocopi sends VMC; untested — ufbx_write round trips into Maya,
  Unreal or Blender, and most AMD and Apple support (unmerged community PRs or single reports).

**Making our own character assets** — the user's bar since 2026-10-29: the whole human (skin, eyes, lips, mouth,
every kind of hair, nails, deformation) at CC5 and MetaHuman quality or better; reuse if it meets the bar, else build
(TASKS). Second pass S10 done 2026-10-29: [`../plans/2026-10-29-research-10-character-assets.md`](../plans/2026-10-29-research-10-character-assets.md).

*web, 2026-10-29* — re-checked by this session (Hugging Face's model API, `cardData.license`): Z-Image-Turbo
apache-2.0 (2026-01-30), Qwen-Image apache-2.0 (2025-08-18), FLUX.2-klein-4B apache-2.0 (2026-02-24),
HiDream-O1-Image-Dev mit (2026-06-22), none gated; Qwen-Image-2.1 is "other" (its LICENSE is the non-commercial Qwen
Research License, per S10).

*agent, 2026-10-29* — S10's notes, sources per fact there:

- The big datasets exist but don't reach the bar: FFHQ-UV, FaceScape, FaceVerse, RenderMe-360, HairCS (53K) and
  DiffLocks (40K) are almost all non-commercial and mostly 1K, some forbid training a commercial product; no free
  textured head-scan set that allows commercial use was found.
- No released, permissively licensed face UV / PBR texture generator meets the bar (FreeUV non-commercial;
  AvatarMe++ commercialised; MoSAR and USC ICT's generator released nothing). The reusable AI is general: the image
  models above, all run by stable-diffusion.cpp (MIT; CPU, CUDA, Vulkan, Metal, OpenCL, SYCL — the family's image
  engine, §10), which says Z-Image runs "on GPUs with 4GB of VRAM — or even less".
- Every image-to-strand hair model is non-commercial or unlicensed, CUDA-only, tested on A100s.
- Unreal imports USD BasisCurves grooms (a custom GroomAPI schema) and Alembic grooms (schema 1.5). MetaHuman's
  texture set is documented, and its Texture Override takes outside face and body textures.
- Reuse or build, per part — build: the skin generator, eyes (shader and iris), hair groom and card generators,
  wrinkle maps, nails, lips; reuse: OpenRigLogic (face-rig runtime), GNM / ICT teeth and tongue geometry, Dem Bones,
  complementary dynamics and Jolt for deformation, MIT shader references (Galacean, O3DE).
- Open: no source compares any open asset with CC5 or MetaHuman — the bar needs our own side-by-side renders;
  licences unread (FLUX 3 Image Klein and Fibo 2.0 — gated; USC-HairSalon; Teeth3DS); FFHQ-UV's and ATLAS's labels
  conflict; no VRAM measured on 8 GB; MetaHuman's wrinkle-map count and lash type unclear; ~50 facts snippet-only.

## 8 · Standards

Round one done 2026-10-29: [`../plans/2026-10-29-research-08-standards.md`](../plans/2026-10-29-research-08-standards.md)
(nine topics, each with a table, facts and an assessment; distilled at the end of this section). Scene and data model, skeleton naming, face standard, the command and API layer,
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

*web, 2026-10-29* — re-checked by this session (GitHub's API): OpenUSD's latest release is v26.11.1
(2026-10-21); the MCP specification repo's latest release is `2026-07-28`; WASI's latest is v0.3.2
(2026-10-13); MediaPipe is Apache-2.0, v1.2.0 (2026-10-28).

*web, 2026-10-29* — read by the standards-spec session for the spec's USD pieces:

- **UsdShade render contexts** (`class_usd_shade_material.html`, OpenUSD docs): a Material "can host data for any
  number of render targets"; each terminal output (surface, displacement, volume) "can further be qualified by a
  token-valued renderContext"; an empty context is the universal output; "Render context token values is typically
  driven by the rendering backend"; properties are namespaced per context (`outputs:ri:surface`); shaders of a Material
  "live under the Material in namespace"; resolution takes the first context in the caller's list that yields a shader,
  else the universal one. (The mechanism the spec uses for a `juststage` material network beside UsdPreviewSurface and
  MaterialX.)
- **`usd-core` on PyPI**: Pixar's "core USD libraries" for pip, version **26.11** (2026-10-21), licence
  `LicenseRef-TOST-1.0`, Python ≥ 3.11 < 3.15, wheels for Windows x86-64, Linux x86-64/ARM64 (glibc 2.27+), macOS
  10.15+ universal2; no imaging plugins. (The spec's USD library for tests and tools outside Blender.)

*agent, 2026-10-29* — round one's standards notes, sources per fact there:

- OpenUSD is the only open format with layers, composition, variants and skinned characters in one model.
  AOUSD Core Spec 1.0 (December 2025) makes composition and USDA/USDC/USDZ normative, but not the domain
  schemas. UsdSkel covers skeletons, linear blend skinning and blend shapes with in-betweens — not
  corrective combinations, rig behaviour, wrinkle maps or cloth — so JustStage needs schemas of its own.
- glTF 2.0 (+Y up, +Z forward, metres) is the exchange format the open engines prefer (Godot recommends it;
  Blender ships Khronos' add-on). Its limits: 4 joints per weight set, only 8 morphed attributes guaranteed,
  morph names by convention only, no hair extension.
- The open humanoid vocabulary has converged: VRM 1.0 (55 bones, 15 required), Unity's HumanBodyBones (55)
  and Godot's SkeletonProfileHumanoid (56 with root) share names (Unity names the thumbs differently); VRM
  1.0 and Godot agree on a T-pose facing +Z, Y up, metres.
- The commercial side has converged on Epic's skeleton and face: CC5 added ten bones to line up with
  UE5/MetaHuman and shares MetaHuman's facial controls. Bone counts: CC3+ 108, UE5 Mannequin 89, MetaHuman
  342.
- ARKit's 52 blendshape names are the public face-interchange set (0.0–1.0, left and right are the face's
  own sides); MediaPipe outputs 51 of them (no `tongueOut`); FACS's manual is paid. MetaHuman's DNA layers
  controls → raw controls → correctives, joints, blend-shape and wrinkle-map weights — the proven internal
  face design (open under MIT as OpenRigLogic, §4). MetaHuman's terms conflict across sources ("any engine"
  vs the DNA Calibration licence's Unreal/Twinmotion limit).
- Undo and commands: Qt's QUndoStack and Godot's UndoRedo agree — a named command with serializable
  arguments, do and undo on one instance, macros, merging of repeated edits. Blender's lesson: an operator
  without a context-free `execute()` can't be repeated from a script.
- MCP 2026-07-28: JSON-RPC 2.0, stateless (version and capabilities in each request's `_meta`), JSON Schema
  2020-12 tool schemas, date versions, deprecations kept at least 12 months — so one schema per command can
  serve the UI, the CLI, a JSON channel and MCP. Today's 3D-app MCP servers mostly bridge to scripting
  (blender-mcp exposes "execute arbitrary Python").
- Plugins: native binaries break across host releases (Maya; Godot 4.1, whose `.gdextension` now declares a
  compatibility range). WebAssembly components give typed interfaces (WIT) and enforced capabilities
  (Extism: memory, allowed hosts, allowed paths); Blender's manifest permissions are disclosure only. The
  agent's assessment: sandboxed WebAssembly plugins plus native built-ins.
- Old files keep loading two proven ways: Blender writes its struct catalogue (SDNA) into every file with
  writer and minimum-reader versions and runs ordered versioning code (snippets); USD versions schemas by
  family (`SphereLight_2`).
- Blender 5.2 LTS remote asset libraries are plain static HTTP: JSON listings, previews, one .blend per asset.
- Open: Blender's docs refused scripted access (operators, undo internals, asset metadata, USD skeleton import,
  Rigify bones); not reached — gRPC, Live Link, the HumanIK and Mixamo bone lists, the UE5 Mannequin bones,
  MetaHuman's control counts, CC's Smart Gallery, Fab; no open cloth standard found (was: "… and no open FBX
  writer found" until 2026-10-29 — below).

Second pass done 2026-10-29: [`../plans/2026-10-29-research-08-standards-pass2.md`](../plans/2026-10-29-research-08-standards-pass2.md).

*web, 2026-10-29* — re-checked by this session (GitHub's API and the README): `ufbx/ufbx-write` is a "Single
source file FBX exporter", MIT or Unlicense, "still a work-in-progress, and issues/breaking changes are to be
expected"; created 2025-06-22, last push 2026-06-20, 21 stars.

*web, 2026-10-29* — fetched at the source by the standards-spec session for the mapping tables
(`../standards/skeleton-and-face.md`); the Daz files are saved verbatim in `../plans/2026-10-29-spec-evidence/`:

- VRM 1.0 `humanoid.md`: the 55 bone names (torso `hips`, `spine`, `chest`, `upperChest`, `neck`; head `head`,
  `leftEye`, `rightEye`, `jaw`; legs `upperLeg`, `lowerLeg`, `foot`, `toes` per side; arms `shoulder`, `upperArm`,
  `lowerArm`, `hand` per side; fingers `thumbMetacarpal/Proximal/Distal` and `{index,middle,ring,little}
  {Proximal,Intermediate,Distal}` per side); required: `hips`, `spine`, `head`, both `upperLeg`, `lowerLeg`, `foot`,
  `upperArm`, `lowerArm`, `hand`; rules: "Humanoid bones must be unique in VRM", "upperChest can exist only when chest
  exists", scale "MUST have positive values".
- Apple's `ARFaceAnchor.BlendShapeLocation` JSON: the 52 names, grouped left eye 7, right eye 7, mouth and jaw 27,
  brows/cheeks/nose 10, tongue 1 (the list is in the skeleton doc §2.1).
- Daz `DazBridgeUtils/Extras/g9_to_unreal_manny.json` (Apache-2.0): Genesis 9 → UE5 names, including `spine1–4` →
  `spine_01, _02, _03, _05` (no `spine_04`), `neck1/2` → `neck_01/02`, twist bones `*_twist_01/02`, metacarpals, `l_toes`
  → `ball_l`, `l_metatarsal` → `metatarsal_l`, `l_pectoral` → `pectoral_l`, `l_hand_anchor` → `weapon_l`; no calf twists,
  no face bones. `g8_to_unreal.json`: Genesis 8 names (`abdomenLower/Upper`, `chestLower/Upper`, `neckLower/Upper`,
  `lCollar`, `lShldrBend/Twist`, `lForearmBend/Twist`, `lCarpal1–4`, `lThighBend/Twist`, `lShin`, `lFoot`, `lToe`,
  `lPectoral`, fingers `lThumb1–3`, `lIndex1–3`, `lMid1–3`, `lRing1–3`, `lPinky1–3`) → the same UE5 names, one twist per
  segment.

*measured, 2026-10-29* — the UE5 Mannequin bone names, read by a byte scan of the name tables of
`SKM_Manny_Simple.uasset` and `SK_Mannequin.uasset` in the user's UE 5.7 project
(`E:\Dev\Unreal\DeformCPlusTest\Content\Characters\Mannequins\Meshes`; also in `FootprintDeformation`); the lists are
saved in `../plans/2026-10-29-spec-evidence/ue5-mannequin-bones.json`:

- `SKM_Manny_Simple`: exactly **89** names — the count Reallusion publishes for the UE5 Mannequin: `root`, `pelvis`,
  `spine_01`–`spine_05`, `neck_01`, `neck_02`, `head`; per side `clavicle`, `upperarm`, `upperarm_twist_01/02`,
  `lowerarm`, `lowerarm_twist_01/02`, `hand`, `thumb_01–03`, `index/middle/ring/pinky_metacarpal`, `index/middle/ring/
  pinky_01–03`, `thigh`, `thigh_twist_01/02`, `calf`, `calf_twist_01/02`, `foot`, `ball` (80 deform bones), plus the
  helpers `ik_foot_root`, `ik_foot_l/r`, `ik_hand_root`, `ik_hand_gun`, `ik_hand_l/r`, `interaction`, `center_of_mass`.
- `SK_Mannequin` (5.7): **161** names — the 89 plus 72 corrective bones: `*_correctiveRoot_l/r` (thigh, calf, upperarm,
  lowerarm), `*_twistCor_01/02_l/r`, `thigh_fwd/bck/in/out_l/r`, `thigh_fwd_lwr/bck_lwr_l/r`, `calf_knee/kneeBack_l/r`,
  `upperarm_fwd/bck/in/out/bicep/tricep_l/r`, `lowerarm_fwd/bck/in/out_l/r`, `wrist_inner/outer_l/r`, `ankle_fwd/bck_l/r`,
  `clavicle_pec/out/scap_l/r`, `spine_04_latissimus_l/r`, `weapon_l/r`.
- **Neither has `metatarsal_*` or `pectoral_*`** — Daz's bridge adds those on its side. The calf twists exist.

*web and measured, 2026-10-29* — read by the Opus review of the standards spec:

- **DNA carries body correctives.** OpenRigLogic's headers (`include/dna/layers/`): `RBFBehaviorReader.h` (RBF poses
  with joint outputs, blend-shape channel outputs, animated-map outputs, pose scales, pose controls; `RBFBehavior.h`:
  additive and interpolative solvers, quaternion and twist-axis distance methods), `TwistSwingBehaviorReader.h` (twist
  and swing setups: input controls, output joints, blend weights), `JointBehaviorMetadata.h`, `MachineLearnedBehavior.h`;
  matching writers exist. The archetype DNA in the user's UE 5.8 (`body_head_combined.dna`) holds one RBF solver per
  body joint (`calf_l_UERBFSolver`, `clavicle_l_UERBFSolver`, `foot_l_UERBFSolver`, `hand_l_UERBFSolver`,
  `index_l_01_UERBFSolver`, `index_l_01_half_UERBFSolver`, …) and the UE corrective bones — *measured* (names read from
  the file).
- **MetaHuman's face vocabulary** in `SKM_Face.dna` (UE 5.8): about 420 GUI control channels named `CTRL_<C|L|R>_<area>_
  <action>.<tx|ty>` (`CTRL_C_jaw.ty`, `CTRL_L_mouth_cornerPull.ty`, `CTRL_L_brow_lateral.ty`, `CTRL_C_mouth_stickyU.ty`,
  `CTRL_C_tongue_roll.ty`, `CTRL_L_eye_blink.ty`, …), `FACIAL_*` joint names, and part names `head`, `teeth`, `eyeLeft`,
  `eyeRight`, `eyeshell`, `eyelashes`, `eyeEdge` — *measured* (names read from the file).
- **Mapping lookups.** three-vrm's `mixamoVRMRigMap.js` (MIT): `mixamorigSpine` → `spine`, `mixamorigSpine1` → `chest`,
  `mixamorigSpine2` → `upperChest`. Reallusion's Blender tools (`soupday/cc_blender_tools`, `rigify_mapping_data.py`,
  GPL; names only): `CC_Base_Hip` ↔ Rigify `spine`, `CC_Base_Pelvis` ↔ `pelvis`, `CC_Base_Waist` ↔ `spine.001`,
  `CC_Base_Spine01` ↔ `spine.002`, `CC_Base_Spine02` ↔ `spine.003`, `CC_Base_NeckTwist01` ↔ `spine.004`; its game-base
  map: `spine.001` ↔ `spine_01`, `spine.002` ↔ `spine_02`, `spine.003` ↔ `spine_03`, `spine.004/005` ↔ `neck_01`.
- **Materials.** MaterialX `libraries/pbrlib/pbrlib_defs.mtlx`: `ND_chiang_hair_bsdf` ("Chiang hair shading model") and
  `deon_hair_absorption_from_melanin`; `libraries/bxdf/open_pbr_surface.mtlx` inputs include `subsurface_color`,
  `subsurface_radius`, `subsurface_radius_scale`, `subsurface_scatter_anisotropy`, `coat_*`, `fuzz_color`,
  `fuzz_roughness`, `fuzz_weight`, `specular_*`, `transmission_*`, `thin_walled`.
- **Blender's USD I/O** (manual `files/import_export/usd.rst`, main): export writes Custom Properties as USD attributes
  in the `userProperties` namespace by default (a Namespace option changes it); import reads them back (None / User /
  All Custom); mesh attributes export as primvars and "Mesh Attributes — Read USD Primvars as mesh attributes";
  MaterialX networks are written ("supports most of the shader nodes … a few caveats"); displacement exports only in the
  Preview Surface network; Convert Orientation sets forward and up axes. Blender 5.0's Python notes: properties defined
  with `bpy.props` "are no longer stored in the same container as user-defined Custom Properties".
- **EEVEE** (manual `render/eevee/material_settings.rst`): Displacement "Displacement and Bump" moves vertices ("true
  displacement"); "Displacement Only" falls back to it.
- **glTF vendor extensions** (KhronosGroup/glTF `extensions/README.md`): `KHR_` is reserved for Khronos, `EXT_` for
  multi-vendor extensions; vendor extensions carry a vendor prefix (VRM's `VRMC_*`).
- **MCP Python SDK.** PyPI `mcp` latest 2.3.0; the 1.x line's `LATEST_PROTOCOL_VERSION` is `"2025-11-25"` (supported
  2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25); the 2.x line's `mcp_types/version.py` knows `2026-07-28` beside the
  handshake versions. Blender Lab's `blender_mcp` (`mcp/pyproject.toml`, v1.0.2) depends on `mcp[cli]>=1.2.0,<2` and
  declares tools with FastMCP's `@mcp.tool` decorator (`mcp/blmcp/tools/*.py`).
- **Unreal skeletons** (search summaries of Epic's "Skeletons in Unreal Engine" page and Python API `Skeleton` class):
  importing a mesh onto an existing skeleton merges new bones into it; a skeleton's Compatible Skeletons list lets it use
  another skeleton's animation data, one way.

*agent, 2026-10-29* — S8's pass 2, sources per fact there:

- FBX export without Autodesk's SDK: ufbx-write and Assimp's FBX exporter (BSD-style, "experimental") both write
  FBX 7.5 with skins and blend shapes; neither has been tested against Unreal, Unity or Maya.
- MCP: the spec's changelog confirms `initialize` and sessions are removed and `server/discover` is required.
  Unity now ships a first-party MCP server.
- USD and characters: an AOUSD character interest group was chartered 2026-03-02 (it may not publish schemas;
  review March 2027); a cloth-and-hair physics proposal (OpenUSD PR #111) is open; OpenExec added experimental rig
  schemas in 26.08; UsdSkel blend shapes do carry `normalOffsets`.
- Blender, from its manual and code sources: one typed undo stack, general edits as deduplicated snapshots;
  extension permissions are not enforced; no asset versions; the default (ufbx-based) FBX importer dropped the
  axis and bone options.
- Export targets: Unity's and Unreal's axes confirmed on their docs pages; VRM 1.0 defines no bone local axes.
- MetaHuman terms, both readings dated: Epic 2025-06-03, "any engine"; the DNA Calibration licence (Unreal and
  Twinmotion only) dates from 2022 and was never updated — the user decides.
- Open: no primary public UE5 Mannequin bone list (count 89 only); MetaHuman control counts aren't public (LOD0:
  713 joints, 669 blend shapes); refused, not worked around — the Mixamo help page, the Fab EULA, metahuman.com,
  two Epic licence pages; no benchmark of WebAssembly copy cost on large meshes (to measure on our data).

**Pulling in assets from other programs** — a requirement since 2026-10-29 (TASKS). Second pass S9 done
2026-10-29: [`../plans/2026-10-29-research-09-import.md`](../plans/2026-10-29-research-09-import.md) (a table per
source program, the import workflows of CC5, Unreal, Daz and the Blender add-ons, open conversion tools, a USD
survival table, terms lines).

*web, 2026-10-29* — re-checked by this session (GitHub's API): `daz3d/DazBridgeUtils` and `daz3d/DazToUnreal` are
Apache-2.0 (last push 2026-01-01); `daz3d/DazToBlender` shows no single licence ("NOASSERTION").

*agent, 2026-10-29* — S9's notes, sources per fact there:

- Unreal and USD: export is Beta — static and skeletal meshes, animations, levels and sequences, materials baked to
  UsdPreviewSurface; its USD import is the widest of any app checked (blend shapes, grooms, MaterialX, MDL).
  Not found: whether its USD export writes morph targets; any way to export grooms out of Unreal.
- CC5 and Daz don't help through USD: Daz Studio has no USD exporter; CC / iClone write USD only for Omniverse,
  with MDL materials Reallusion says Blender can't read.
- No app's USD carries correctives: Daz's JCMs, MetaHuman's RigLogic, CC's wrinkles and cloth cross only in a
  companion file beside the FBX — Daz's `.dtu`, CC's JSON plus `.fbxkey`, MetaHuman's DNA.
- Daz's bridge code is open (Apache-2.0, above), including Genesis 8/9 bone maps to MetaHuman, Mixamo and UE; the
  Diffeomorphic Blender importer (GPL) reads Daz's native `.duf` files directly.
- Mesh to MetaHuman runs its solve in Epic's cloud. Sketchfab now belongs to KitBash (sale announced 2026-08-10).
- Terms, one line each: Reallusion's content licence allows export to "any other software", but its EULA asks that
  exported models "cannot be opened or imported into a publicly available software application"; with §2's CC
  Base Model clause, importing CC characters into JustStage is a terms question for the user to read.
- Open: the Fab EULA, metahuman.com, VRoid Studio help, Marvelous Designer's format table (refused scripted access);
  CC5's current USD materials, the structure of CC's JSON sidecar, 3ds Max USD import, how plain Daz FBX export
  carries JCMs and hair (not found).

*web, 2026-10-29* — the Opus re-check of its own review recs (the user: "rethink on all your recs again just to make
sure you dont change your mind"), at the sources:

- OpenRigLogic evaluates the body layers, not only stores them: `src/riglogic/rbf/` (`RBFBehaviorEvaluator`,
  `cpu/AdditiveRBFSolver`, …) and `src/riglogic/joints/cpu/twistswing/` (`TwistSwingJointsEvaluator`); Python bindings
  for both libraries: `python/dna/DNA.i`, `python/riglogic/RigLogic.i` (SWIG) with tests (GitHub tree API, HEAD).
- Blender 5.2 LTS builds against MaterialX 1.39.4 and USD 26.03 (`build_files/build_environment/cmake/versions.cmake`,
  `blender-v5.2-release`); the Principled BSDF's MaterialX export creates `open_pbr_surface` on MaterialX newer than
  1.38 (`node_shader_bsdf_principled.cc`, main); Blender 5.3 beta's bundled MaterialX ships
  `libraries/bxdf/open_pbr_surface.mtlx` (on disk).
- Blender 5.2's manual has Remote Asset Libraries (`files/asset_libraries/remote_asset_libraries.rst`, 5.2 branch:
  static `.blend` files + a JSON listing generated by `blender -b -c asset_listing generate`, WebP/PNG previews ≥ 256 px,
  no asset versions) and the hair node groups (`modeling/geometry_nodes/hair/`: Deformation, Generation, Guides, Read,
  Utility, Write) — both are in R1's 5.2 floor.
- glTF `extras`: "Application-specific data" (Khronos schema `extras.schema.json`, "SHOULD be a JSON object").
  Blender's glTF exporter writes custom properties to `extras` ("Include → Custom Properties"); "Unlike glTF extensions,
  custom properties (extras) have no defined namespace, and may be used for any user-specific or application-specific
  purposes" (manual `addons/scene_gltf2.rst`).
- Blender Lab's MCP tools, each a pair: `mcp/blmcp/tools/<tool>.py` — a FastMCP `@mcp.tool` function with typed
  arguments, run in the MCP process — and `<tool>_toolcode.py` — `Params` and `Result` `NamedTuple`s and a `main(params)`
  sent over the socket and run inside Blender (`render_viewport_to_path`, read). 21 tools: blend-file and object
  summaries, screenshots, renders, tab jumps, API/manual search, `execute_blender_code`. No generic operator tool.
- HD morphs in Blender, existing practice: `edolstra/dhdm` (GPL-3.0, 2022) converts Daz `.dhdm` HD morphs to
  "tangent-space displacement maps … that can be used in Blender", with a strength per morph; Daz forum posts on the
  Diffeomorphic importer say the multires modifier "doesn't support morphs other than the base level", so HD morphs go
  in as displacement or normal maps linked in the material (search snippets).

*web, 2026-10-29* — shipping JustStage as its own app on stock Blender (the user: "i want our app to look like a
custom app so user donest have to load plugin it just laucnhe like an app we built even thought it is using blender
core features"), at Blender 5.2's sources:

- Extensions are only `type = "add-on"` or `"theme"` (manual `advanced/extensions/getting_started.rst`, 5.2 branch) —
  an application template can't be published on extensions.blender.org (standards `plugins.md` §5 says it can).
- `--app-template <template>`: "Set the application template (matching the directory name)" (manual
  `advanced/command_line/arguments.rst`, 5.2). Environment variables there: `BLENDER_USER_RESOURCES` ("Replace default
  directory of all user files"), `BLENDER_USER_CONFIG`, `BLENDER_USER_SCRIPTS`, `BLENDER_USER_EXTENSIONS`,
  `BLENDER_SYSTEM_SCRIPTS` ("Directories to add extra scripts"), `BLENDER_SYSTEM_EXTENSIONS` ("Directory for system
  extensions repository"), `BLENDER_SYSTEM_DATAFILES`, `BLENDER_SYSTEM_PYTHON`. A `portable` folder next to the
  executable (inside `Blender.app/Contents/Resources` on macOS) keeps preferences, startup file and extensions there
  (`advanced/blender_directory_layout.rst`, 5.2).
- The main window's title is built in C: `<file> … - Blender <version>` (`wm_window_title_text` in
  `source/blender/windowmanager/intern/wm_window.cc`, 5.2); Python's window-manager API has no title setter (only
  popup and dialog titles, `rna_wm_api.cc`). Hiding "Blender" there and in the window icon takes a code change.
- Blender as a Python module (`bpy`, 5.2.3 on PyPI) "runs without a user interface, like running regular Blender in
  background mode" (`WITH_PYTHON_MODULE` in `CMakeLists.txt`, 5.2) — no viewport or editors to embed.
- The Blender Foundation's 2022 "Blender Apps" proposal (cgchannel, 2022-11-07, "still an early-stage proposal"):
  apps built on application templates, the "fully portable" kind an archive "that include[s] the Blender executable
  itself"; no sign it shipped was found.
- Size: Blender 5.3 beta's folder on this machine is 956 MB.
- Third pass (the user: "since you change your rec should you rethink again?"), at the sources: app templates are found
  in `<BLENDER_SYSTEM_SCRIPTS>/startup/bl_app_templates_system` (`bpy.utils.app_template_paths`, 5.2);
  `blender --command extension install-file [-h] -r REPO [-e] [--no-prefs]` installs and enables a package, system
  repositories "are managed outside of Blender and are considered read-only" (manual
  `advanced/command_line/extension_arguments.rst`, 5.2); Blender 5.2's Python is 3.13.13 (`versions.cmake`);
  OpenRigLogic has no wheels (PyPI `openriglogic`, `riglogic`, `dna-riglogic` 404; no GitHub release assets).
- Blender Lab's MCP server auto-discovers `blmcp/tools` modules with `pkgutil.iter_modules` and calls each
  `register(mcp)` — "they are never un-registered" (`mcp/blmcp/__init__.py`). The MCP SDK 1.x: `FastMCP.add_tool(fn,
  name, title, description, annotations, …)` and `remove_tool(name)` (`src/mcp/server/fastmcp/server.py`);
  `ctx.session.send_tool_list_changed()` for "When your server dynamically adds or removes tools at runtime"
  (`docs/server.md`, "Dynamic Tools" example registering a plugin's tools); tool arguments read with
  `inspect.signature(func, eval_str=True)` (`utilities/func_metadata.py`); a low-level `Server` with `@server.list_tools()`
  returning explicit `inputSchema`s (`docs/low-level-server.md`).
- glTF exporter hooks: `class glTF2ExportUserExtension` with `gather_node_hook(self, gltf2_object, blender_object,
  export_settings)` (KhronosGroup/glTF-Blender-IO `example-addons/example_gltf_exporter_extension`). Blender's FBX
  exporter has no hook code (`scripts/addons_core/io_scene_fbx/export_fbx_bin.py`, 5.2).
- AI features (review item 25): the kit's runtimes (`just-core/packages/core/src/runner/runtimes.js`, read 2026-10-29) —
  `onnx`: kind "vision", "ONNX Runtime", MIT, `inProcess: true`; `audiocpp`: kinds `tts` and `stt`, placements `gpu` and
  `cpu`, models registered into a running server; plus `llamacpp` and `sdcpp`. MediaPipe on PyPI: 1.2.0, Apache 2.0,
  wheels `py3` for win_amd64, win_arm64, macosx_11_0_arm64, manylinux_2_28 x86_64 and aarch64 — no Intel-Mac wheel.
  BlendArMocap (cgtinker, GPL-3.0, pushed 2025-12-01): "Run Mediapipe within Blender to detect pose, hand, face or
  holistic features", dependencies installed from its preferences.
- Mocap (review item 26), from Epic's MetaHuman docs via search: 5.7 release notes — real-time animation "from an
  external camera using Live Link Face on iPad or Android", "60FPS on top end devices"; 5.8 — the experimental
  "MetaHuman Animator Markerless Motion Capture" plugin captures "body, or both body and face performance, from a
  single camera", works with "webcams and supported smartphones", an offline solve, on Fab, body capture Windows-only,
  needs Live Link Hub and Capture Manager; MetaHuman Animator's facial side on Linux and macOS; a batch-processing API
  (dev.epicgames.com MetaHuman 5.7 and 5.8 release notes, "metahuman-animation-from-mono-video-capture"). Blender
  receivers for Live Link Face: `shun126/livelinkface_arkit_receiver` (GPL-3.0, pushed 2026-09-15, 89 stars),
  `nmfisher/blender_livelinkface` (MIT, 2024-03; a paid tier records) — Epic publishes no network format for the app.
  The VMC protocol repo `sh-akira/VirtualMotionCaptureProtocol`: MIT, pushed 2026-10-09. XR Animator
  (`ButzYung/SystemAnimatorOnline`, "AI-based Full Body Motion Capture", pushed 2026-10-17; no licence detected by
  GitHub).
- Extensions importing each other (review item 27): "For add-ons to be bundled as extensions, they must be
  self-contained"; "Bundle other add-ons together. This is recommended if an add-on depends on another add-on"; an
  extension's module name is `bl_ext.{repository_module_name}.<id>` (manual `advanced/extensions/addons.rst`, 5.2).
  The System repository is added as name "System", module "system" (`BKE_preferences_extension_repo_add_default_system`,
  `source/blender/blenkernel/intern/preferences.cc`, 5.2).
- Blender's release rhythm (`blender/blender-developer-docs`, `docs/handbook/release_process/release_cycle.md`,
  `lts.md`): "A new Blender version is targeted to be released every 4 months"; an LTS "will provide bug fixes
  throughout a 2-year time span"; "for non-LTS releases, Blender only has a corrective release if high severity bugs
  are found". 5.3: "currently in **Beta** until November 4, 2026" (`docs/release_notes/5.3/index.md`). 5.3 notes, for
  JustStage: assets — online-library access tokens, extension integration, per-version replacement files
  (`my_asset@b5_3.blend` beside `my_asset.blend`); Alembic — "Arbitrary attributes on meshes, curves, and pointclouds,
  are now exported", curve velocities, subdivision parameters; USD — normals written in Blender's own representation,
  Matrix4d primvars, Gaussian-splat import; sculpt — textures and generic attributes shown on Multires meshes in Sculpt
  Mode; core — projects with project asset libraries and custom splash artwork; Python — read-only undo-stack access,
  `UILayout.label_multiline()`, `gpu.types.GPUStorageBuf`; EEVEE — light-evaluation shader nodes, panoramic cameras.
- AI in Blender 5.3 itself (the user: "doens the beta give us latest ai and more features?"): the 5.3 notes' only AI
  item is Cycles' "new DLSS denoiser … for the viewport" on NVIDIA GPUs (`cycles.md`); no assistant or MCP feature.
  Blender Lab's MCP server is separate from Blender: latest release v1.0.3 (2026-09-11; v1.0.2 2026-09-08, v1.0.0
  2026-04-27, Gitea releases API), and `main` still depends on `mcp[cli]>=1.2.0,<2` (`mcp/pyproject.toml`).
- Re-checked on the installed 5.3 beta (`E:lender-5.3.0-beta`, files read, not run) and the `blender-v5.3-release`
  branches, 2026-10-29 — the 5.2 facts above hold on 5.3, except: extension types "add-on", "asset-library", "theme"
  (manual `getting_started.rst`); USD 26.08, MaterialX 1.39.4, Python 3.13.13 (`versions.cmake`); the main window title
  appends " - <project name>" when a Blender project is active, then " — Blender <version>"
  (`wm_window_title_project_append`, `wm_window.cc`). On disk: `blender.exe`, `blender-launcher.exe`, `python313.dll`;
  system app templates 2D_Animation, Sculpting, Storyboarding, VFX, Video_Editing.
- Measured on the installed 5.3 beta, headless (2026-10-29): with `BLENDER_USER_RESOURCES`, `BLENDER_SYSTEM_EXTENSIONS`
  and `BLENDER_SYSTEM_SCRIPTS` set, the repositories are `blender_org` and `user_default` under the user folder's
  `extensions/`, and **System (`system`, source SYSTEM) at `<BLENDER_SYSTEM_EXTENSIONS>\system`**; an extension placed
  there loads as `bl_ext.system.<id>` (JustStage's foundation tests, `tools/dev.py test`); an app template under
  `<BLENDER_SYSTEM_SCRIPTS>/startup/bl_app_templates_system/` is listed by `bpy.utils.app_template_paths()`; Blender's
  bundled Python 3.13.13 has pip 26.2.2.
- Measured 2026-10-29 on the 5.3 beta: with `BLENDER_SYSTEM_SCRIPTS` set (to a folder holding only an app template),
  Blender prints "ModuleNotFoundError: No module named 'bl_pkg'" and "Extension: unexpected error detecting cache, this
  is a bug!" at start, and an extension add-on saved as enabled in the preferences is not loaded; without that variable
  it loads. An app template's `register()` runs before the extension system is up, so enabling an extension add-on from
  there fails the same way. With `--app-template juststage` and no `userpref.blend` in the template, an add-on saved as
  enabled in the shared preferences was not loaded either. What works (fresh and repeat launches, measured): the
  template under `<BLENDER_USER_RESOURCES>/scripts/startup/bl_app_templates_user/`, enabling the add-on from
  `load_factory_preferences_post` / `load_factory_startup_post` / `load_post` handlers and a one-shot timer — the
  manual's app-template pattern ("You may enable add-ons associated with your template"; defaults "via handler").

*web, 2026-10-29* — NVIDIA Omniverse's standards (the user: "what does omniverse use … for materials and hair and
other things"), from docs.omniverse.nvidia.com, page read:

- Materials: "Materials in Omniverse are supported using MDL, and MaterialX using an MDL backend" (materials page).
  OpenPBR is a material template since Kit 110: "makes use of the reference implementation written in MaterialX …
  translated to MDL using the code generator offered by the MaterialX SDK"; RTX Interactive (path tracing) "supports
  the full OpenPBR Surface model"; Real-Time 2.0 lacks sheen and thin film, and SSS must be switched on (OpenPBR page).
  The MDL SDK is BSD-3-Clause (GitHub API, push 2026-08-31).
- Digital humans: skin is an MDL graph on `OmniSurfaceBase`, eyes several `OmniSurface` materials, hair
  `OmniHairBase` presets (rtx_rt-dh-setup page); OmniHair is "based on Disney's Hair and Fur" model, colour by
  melanin (OmniHair page).
- Geometry: "RTX supports the rendering of basis curves in USD along with the ability to author them"; meshes and
  OpenSubdiv subdivision surfaces; points (geometry page).
- Characters: Audio2Face's blendshape solve exports weights "as a Json file or UsdSkel", with NV 46 and ARKit 51
  templates (character transfer page); its retargeting extension works "only … on a Human rig" (retargeting page).
  PhysX is BSD-3-Clause (GitHub API, push 2026-10-27).

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

*code, 2026-10-29* — read by the standards-spec session in `just-core/packages/core/src` for
`../standards/ai-engines.md` (R14 "name the exact service"):

- `runner/runtimes.js` `RUNTIMES` ids: `llamacpp` (kind llm), `sdcpp`, `onnx`, `audiocpp`. The template server
  (`template/server/src/app.js`) ships with `runtimes: []` — an app turns a runtime on in `installLlm`.
- HTTP routes for runtimes (`llm/runtimes_api.js`): `GET /v1/ai/runtimes`, `GET|POST /v1/ai/runtimes/:id/engine/
  {status,install,update,check,install/cancel}`, `DELETE …/engine`, `PUT …/settings`, `GET …/models`,
  `POST …/models/:modelId/download[/cancel]`, `DELETE …/models/:modelId`. Jobs (`platform/jobs_api.js`): `GET
  /v1/jobs`, `GET /v1/jobs/:id`, `GET /v1/jobs/:id/events`. `POST /v1/ai/run` (`llm/prompts.js`) runs a **chat**
  action. **No kit route runs an image feature over HTTP**: `runImageFeature` (`llm/image_dispatch.js`) is called
  in-process (just-house-paint's `aiphoto_service.js`, `runtime_service.js`, `sdcpp.js`) — the kit gap the spec names.
- `runner/arbiter.js`: "each app process holds its OWN instance (cross-APP arbitration is out of scope, design §7.2)".
- `platform/auth.js`: "OFF by default: an empty token list means no auth (the normal local-loopback case)"; with tokens,
  loopback bypasses auth unless `requireForLoopback`; a proxied request is never the loopback door.
- The image-job route, shipped by the just-core session for JustStage (main `333ac9e3`, 2026-10-29; read in
  `packages/core/src/llm/image_jobs_api.js` and `platform/csrf.js`): `makeImageJobsRouter(jobs, { resultDir })`;
  `POST /v1/ai/image/jobs` `{feature, request: {prompt?, width?, height?, seed?, init?, mask?, refs?}}` (width and height
  64–4096; pictures as base64 PNG) → 202 with the job snapshot; a feature that can't run yet → 409 with its `need`
  (engine-not-installed, model-not-downloaded, engine-cant-run-here, engine-not-on, model-unknown), nothing started;
  progress on `/v1/jobs/:id` and `/events`, cancel by DELETE; `GET /v1/ai/image/jobs/:id/result` → the PNG once ("fetched
  once, then the job is forgotten and its file deleted"; a repeat 410 `result-gone`; 409 `job-running` / `job-<state>`);
  an unfetched picture goes with its job (10 min, the core session's report); PNG only. The CSRF middleware rejects a
  mutating `/v1` request only when an `Origin` header is present and not allowed; resource isolation passes a request
  without `Sec-Fetch-Site` — a non-browser client sends neither.
- Ports (`scripts/check-family.js` `APP_PORTS`): JustWrite 17495, JustVoice 17494, docgen 8742, template 17490,
  just-house-paint 17499. The spec takes **17480** for JustStage's API socket (not in the kit's list; recorded in the
  3D family's table).

The assessment of this section (one app or two; JustDirect inside or beside) waits for §2, §3 and §6.

*read, 2026-10-29* — the kit at just-core `75d3cb01`, for step 1.4 (the engine host):
- `template/server/src/app.js` `llmArgs`: `runtimes: []`, `runtimeModels: []` — "an image app names "sdcpp" and its
  image models' pinned files here, a feature of kind "image" in its catalog with its own preset … The template runs no
  image model". Its runtimes are fixed in code (its only env switches: `FAMILY_TEMPLATE_UI_DIR`,
  `FAMILY_TEMPLATE_ALLOWED_HOSTS`).
- An image feature runs only when the app's stores give it a preset (`featurePresetRef` → an engine preset of kind
  "image" → provider `local-sdcpp` → a `sdcpp` runtime model on disk) — `llm/image_dispatch.js`
  `resolveRuntimeFeature`, `runtimeFeatureReadiness` (needs: `no-image-model`, `engine-not-on`, `engine-not-installed`,
  `model-unknown`, `model-not-downloaded`).
- `scripts/new-app.js` (the generator behind /new-just-app) copies the whole template (app, Electron, server), installs,
  checks and registers the app in `check-family.js` (`APPS`, `APP_PORTS`, `DEV_PORTS`; the registry today: JustWrite
  17495, JustVoice 17494, docgen 8742, template 17490, just-house-paint 17499); no server-only mode.

*read, 2026-10-29* — how JustStage reaches AI engines, re-checked (the user: "maybe blender already has ai tools or
plugins … can webpages run in blender … or just have the ai configuration a sepearte webpage that user clicks from
blender"; "we originally had the kit server code in python"):
- **The kit's Python past:** `llm_runner/` (71 files, 1,317,496 bytes; MIT) — "Detects hardware, manages/recommends GGUF
  models, downloads the right prebuilt llama.cpp … and spawns llama-server"; mounted on FastAPI. llama.cpp only — the
  image, speech and vision runtimes came later, in JavaScript. Deleted in just-core `4619872b` (2026-10-08, "No Python").
- **The kit's engine code today** (just-core `75d3cb01`): `packages/core/src/runner/` 20,610 lines, `llm/` 13,745 —
  hardware detection 1,880, the runtime service 2,193, the lifecycle 4,994, binary choice 1,099. Chat runs over HTTP
  (`POST /v1/ai/run`, `/v1/ai/stream`), images too (`POST /v1/ai/image/jobs`); **speech has no HTTP route** —
  `llm/speech_dispatch.js` (`transcribeFeature`, `withSpeechModel`) is called inside the app only.
- **The template carries the kit's AI screens:** `template/src/boot/familytemplate.js` mounts "the kit's whole UI half in
  one call (installLlmUi …)"; the server serves the built pages when headless (`app-structure.md`: `build:spa` "served
  by the server for headless use"; `server/src/app.js` reads `FAMILY_TEMPLATE_UI_DIR`).
- **Blender opens web pages only in the browser:** `bpy.ops.wm.url_open` ("Open a website in the web browser",
  `5.3/scripts/startup/bl_operators/wm.py:1043`); no web view inside Blender was found.
- **Blender's extension rules** (the extensions platform's moderation guidelines,
  `blender-developer-docs/docs/features/extensions/moderation/guidelines.md`): "Make sure the add-on is self-contained …
  It should not have functionality which is extended by external software. It should not depend on external servers
  (`localhost` is fine)"; no auto-updater; pip dependencies "bundled as wheels or vendorized"; with the `network`
  permission, check `bpy.app.online_access` (manual `addons.rst`). They bind the extensions.blender.org listing;
  JustStage installs through its own installer (plugins.md §5).
- **Blender AI add-ons** (GitHub, 2026-10-29): Dream Textures (8,232 stars, GPL-3.0; PyTorch, "tested with CUDA and Apple
  Silicon GPUs"), Pallaidium (1,552, GPL-3.0; diffusers and ComfyUI; "A CUDA-supported Nvidia card with at least 6-16 GB
  VRAM", Windows, git on PATH), StableGen (996, GPL-3.0; a ComfyUI backend), AI-Render (1,228, MIT; Automatic1111),
  ComfyUI-BlenderAI-node (1,575, GPL-3.0; ComfyUI), mcp-for-blender (32,728, MIT; an outside LLM drives Blender — the
  other direction). None runs llama.cpp, stable-diffusion.cpp or audio.cpp, none bundles its engine.

*measured, 2026-10-29* — JustStage's server (`server/`, the kit at just-core `75d3cb01` then `b41154a7`) on this machine:
- The engine (`sdcpp` build `master-1024-77b72a2`) and FLUX.2 klein 4B (8,749,156,110 bytes, house-paint's pinned
  files) showed installed and on disk at once — the kit's shared cache. A 1024×1024 picture with house-paint's recipe
  (4 steps, guidance 1, euler): 9–13 s; the card's peak 6,060 MiB (`nvidia-smi`, 2 s polls).
- Prompts for a skin close-up: "cheek skin" draws a face (nose, lips); a "grayscale height map" draws grey leather with
  tile seams and lighting baked in; "a flat patch of human skin on the inner forearm … fills the entire frame" gives
  real pores and the crosshatch of skin lines, with the arm's edges, veins and red spots in it — the flat middle 60%,
  high-passed, is the relief kept (`modules/skin/detail.py` PROMPT).
- The image-job route lost the caller's seed (same prompt, seeds 1 and 2 → byte-identical PNGs, sha256
  `344af58836bb…`): `runner/sdcpp.js` `imageJobBody` read only the preset's `params.seed ?? 42`. Fixed in `b41154a7`
  ("the caller's own seed wins over the preset's"); the route takes no `request.params`.
- hm08's UVs: a median 0.57 UV units per metre of skin over the body's faces (10th–90th percentile 0.40–1.10).

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

*web, 2026-10-29* — storytold's repos, read by this session through GitHub's API (`orgs/storytold/repos`), as
evidence for the from-scratch route (TASKS):

- About twenty "Craft" apps, every one "written by scratch in pure Rust" or "an open-source, clean-room
  reimplementation of" a named app, Apache-2.0 on GitHub, nearly all created between 2026-09-30 and 2026-10-14 and
  all pushed 2026-10-29: PhotoCraft (74,735 stars), PdfCraft (18,591), FilmCraft (16,827, a non-linear video
  editor), WordCraft (16,557), LightCraft (15,041), VectorCraft (10,981), EffectCraft (8,139, motion graphics and
  compositing), CADCraft (7,167, AutoCAD-style), GridCraft (6,784), DesignCraft (4,922), DeckCraft (4,406),
  SoundCraft (3,888, a Pro Tools-style app), FigCraft (3,804), AniCraft (61, 2D animation).
- Shared parts: `craft-libs`, `craft-ai-integrations` (an AI layer with egui widgets), `craft-fonts`,
  `craft-i18n`, a launcher, and their own forks of `egui` and `winit`.
- None of them is a real-time 3D character, scene or animation app; ArtCraft's 3D stage is Three.js (§10).

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

The rec list built on this register (2026-10-29): [`../plans/2026-10-29-recs.md`](../plans/2026-10-29-recs.md).

## 13 · Working method: models and sessions

- Fable 5.1 costs $10 / $50 per million input / output tokens, Opus 5.5 $4 / $20; Fable 5.1 is
  Anthropic's "most capable widely released model, for the most demanding reasoning and long-horizon
  agentic work" — *record, 2026-10-29* (the claude-api skill's model table, cached 2026-10-06).
- Prompt caches are per model, so switching a session's model re-reads its context uncached — *record,
  2026-10-29* (the same skill).
- CLAUDE.md files at and above the working directory load at launch; one in a subdirectory loads when
  Claude reads or edits a file there — *record* (the web kit's register §6, *web, 2026-10-09*).
- **The WebSearch cap** — *web, 2026-10-29* (code.claude.com/docs/en/tools-reference.md, "Session search limit";
  env-vars.md), on Claude Code 2.1.312 here (*measured*): "An interactive terminal session has a limit of 200
  WebSearch calls. Searches from the main conversation and from subagents … count against the same limit."
  It refills at about 100 calls an hour (v2.1.290+; `CLAUDE_CODE_WEB_SEARCH_REFILLS_PER_HOUR` sets the rate);
  `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` raises it with no upper bound but can't turn it off (v2.1.212+);
  a new conversation or `/clear` resets the count, unless work that can still spawn subagents survives the
  clear; with `-p` and the Agent SDK it counts per turn. At the cap, searches return a notice to carry on
  with what was gathered. Round one's 8 agents ran it out (each notes file says so).
- The cap is raised: `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` = "2000" in the user settings' `env`
  (`F:\ClaudeCode\config\settings.json`), on the user's word 2026-10-29 (TASKS). It took effect in the running
  session without a restart: a fresh shell saw the variable and WebSearch answered again — *measured,
  2026-10-29*. So the second pass runs as 8 agents in one session (was: one session per area, until
  2026-10-29): [`../plans/2026-10-29-research-second-pass.md`](../plans/2026-10-29-research-second-pass.md).
- WebFetch reads up to 100,000 characters a call and caches 15 minutes; 20 subagents can run at once by
  default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`), with no total limit — *agent, 2026-10-29* (the same docs).
