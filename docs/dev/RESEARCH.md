# Research register — what we already know, and where the proof is (just-stage)

**Read the section for your subject before researching anything.** An agent's brief carries that
section and the line *"don't re-derive these; re-check one only if the source it cites changed after
its date"*. New facts land here in the same change; a research doc with no entry here is not done.
A fact about a part of the character goes into §14.N - the plan's §N (the index below); nothing is appended at
the end any more.

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
[13 · Working method: models and sessions](#13--working-method-models-and-sessions) ·
[14 · The character, part by part](#14--the-character-part-by-part)

**The index - the plan's sections and their facts** (14.N = the plan's §N; the plan is the method, this
file the proof):

| Plan § | Topic | Facts here | Detail docs |
|---|---|---|---|
| §1 | The bar: CC5's HD Aaron, MetaHuman as a reference | [14.1](#141--the-bar-cc5s-hd-aaron-metahuman-as-a-reference) | `2026-11-04-realism.md` §6c; `2026-11-04-realism-review-brief.md` §1 |
| §2 | The gate: views, measures, runs | [14.2](#142--the-gate-views-measures-runs) | `../standards/quality-gate.md`; `../gate/2026-11-05/report.md`, `../gate/2026-11-06/report.md` |
| §3 | Assets, sources, licences, patents | [14.3](#143--assets-sources-licences-patents) | `2026-11-04-research-gaps.md`; `-research-licences-redo.md`; `-research-other-sites.md` |
| §4 | Base mesh, topology, UVs | [14.4](#144--base-mesh-topology-uvs) | `2026-11-05-research-base-mesh.md`, `-base-mesh-2.md`; `2026-11-05-character-design.md` |
| §5 | Mouth, nails, ears | [14.5](#145--mouth-nails-ears) | `2026-10-30-research-hair-eyes-teeth.md`; `2026-11-05-character-design.md` |
| §6 | Shape spaces, sliders, mixing | [14.6](#146--shape-spaces-sliders-mixing) | `2026-10-29-research-05-bases*.md`; `2026-11-05-research-mixing-hair.md` |
| §7 | Face rig, expressions, body rig, capture | [14.7](#147--face-rig-expressions-body-rig-capture) | `2026-11-05-research-face-animation.md`; `2026-10-31-audit-face-edits.md` |
| §8 | Skin colour: scans, the scan route, delighting, hair out, the AI painting route (retired) | [14.8](#148--skin-colour-scans-the-scan-route-delighting-hair-out-the-ai-painting-route-retired) | `2026-11-02-research-texture-source.md`; `2026-11-02-scan-skin-base.md`; `2026-10-30-research-ai-*` |
| §9 | Skin relief: mid-scale, pores, microrelief, regions | [14.9](#149--skin-relief-mid-scale-pores-microrelief-regions) | `2026-10-30-research-skin-detail-shading.md`; `2026-11-04-realism.md` §5 |
| §10 | Skin shading: scattering, specular, roughness, the tone model | [14.10](#1410--skin-shading-scattering-specular-roughness-the-tone-model) | `2026-10-30-research-skin-detail-shading.md` |
| §11 | Body skin and fitting a scan | [14.11](#1411--body-skin-and-fitting-a-scan) | `2026-11-04-realism-review-fable.md` F7; `2026-11-06-inputs-audit.md` |
| §12 | Eyes | [14.12](#1412--eyes) | `2026-10-31-audit-eyes.md`; `2026-11-04-app-eyes.md` |
| §13 | Lids, lashes, brows, facial and body hair | [14.13](#1413--lids-lashes-brows-facial-and-body-hair) | `2026-11-04-app-lashes.md`; `2026-11-05-lid-anatomy-build.md` |
| §14 | Scalp hair | [14.14](#1414--scalp-hair) | `2026-11-05-research-mixing-hair.md`; `2026-10-30-research-hair-eyes-teeth.md` |
| §15 | The live view against the film | [14.15](#1415--the-live-view-against-the-film) | `2026-11-04-research-eevee-live-view.md`; `2026-11-03-live-view.md` |
| §16 | The app | §6, §7, §8, §10 | `../standards/`; `2026-10-29-research-06a*`, `-08-standards*` |

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
- **JustStage's own Blender settings render Cycles on the processor** — `compute_device_type` is `NONE` in
  `.dev/user/config` (Blender's factory value); the card is listed (CUDA and OptiX, RTX 2070 Super) but never chosen. The
  face-test scripts pick OptiX per run (`test_face_project.py:170-174`, `test_face_clay.py:83-88`), so only a window
  opened by hand renders on the processor — *measured, 2026-11-03*.
- **Blender 5.3 opens a saved Rendered view as Solid; Material Preview survives** — a copy saved with every 3D view on
  Rendered read back Solid (saved from the GUI and from a background run alike); Material Preview in an EEVEE scene read
  back Material Preview. The Material Output's Target is `ALL` / `EEVEE` / `CYCLES` — *measured, 2026-11-03*.
- **Applying an asset from Blender's Asset Browser** (Blender 5.3's own Pose Library, read 2026-11-04 at
  `5.3/scripts/addons_core/pose_library/`): a keymap item on "Asset Browser Main" (FILE_BROWSER), LEFTMOUSE
  DOUBLE_CLICK, runs an operator that reads `context.asset` (an `AssetRepresentation`: `name`, `id_type`,
  `full_library_path`, `metadata.catalog_id`, `local_id`, ...); its menu entry is prepended to
  `ASSETBROWSER_MT_context_menu`. A failed poll lets the double-click through to Blender. Dragging an object asset
  into the 3D view runs `object.add_named` (the bare object), and Blender has no call to change that drop (operators
  listed). `temp_override(area=…, region=…, asset=rep)` with a representation from `context.selected_assets` drives
  the operator like a double-click. A changed `params.catalog_id` filters the listing only after the next redraw.
  *Measured, 2026-11-04.*
- **Blender drops user-less data-blocks when a file is saved again.** `bpy.data.libraries.write` writes the given
  data-blocks with no users when they're in no scene, so a re-save (`open_mainfile` + `save_mainfile`, as a thumbnail
  step does) emptied JustStage's hair and skin files. `write(..., fake_user=True)` keeps them. An append
  (`libraries.load`, linked or not) clears fake users, so the flag can't be seen that way, only by opening the file.
  *Measured, 2026-11-04.*


*measured, 2026-10-29* — the face test (`tools/face_test/`):
- Blender 5.x worlds light through their Background node; `World.color` changes nothing in a render — the first clay
  views were nearly black. A white Background at strength 1 gives the even light the clay views need.

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
- **The CC5 MCP bridge in use (2026-11-04, the user's pick):** `mackatwentytsuru/cc5-mcp-server` (MIT, © Yuki
  Tsuruoka; README read; cloned and built at `E:\Dev\3D\cc5\cc5-mcp-server`): a Node MCP server (stdio) talking HTTP to
  a Python plugin inside CC5 on `127.0.0.1:5101` (localhost only); 100 tools, among them `set_camera_focal_length`,
  `frame_camera`, `get_lights` / `set_light_multiplier`, `set_ibl` (loads an HDRI), `render_viewport` (PNG),
  `capture_viewport`, `skingen_layer`, `list_presets`, `load_asset`; `exec_python` is refused unless CC5 starts with
  `CC5_ALLOW_EXEC=1` (left off). Its `install-plugin.ps1` hard-codes `C:\Program Files\Reallusion\Character Creator 5`;
  this machine's CC5 is at `F:\Reallusion\Character Creator 5`, so the plugin went to C: unused - copied to
  `F:\...\Bin64\OpenPlugin\CC5_MCP_Bridge` (identical files). Claude Code: `claude mcp add cc5 --scope local` (this
  project). The RLPy file itself: `F:\Reallusion\Character Creator 5\Bin64\RLPy.py` (24,247 lines; `RICamera`,
  `RILight`, `LoadIBLImage`, `RGlobal.RenderImage`).
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

- **CC5's and MetaHuman Creator's screens** (read 2026-11-03, searches "Character Creator 5 user interface overview
  Content Manager Modify panel Scene Manager layout manual", "MetaHuman Creator Unreal Engine 5.7 user interface panels
  …", "Character Creator 5 camera navigation mouse controls …"): CC5's manual (Main Menu > Window) - preset layouts:
  Standard (Ctrl+2: the Content Manager and all toolbars), Fine Tuning (Ctrl+5: the Modify panel on the right), others
  stacking Modify and Content Manager on the left or leaving only the camera view; the Content Manager applies
  templates; Scene Manager (F5) lists every object; Modify (F6). CC5's Camera Toolbar page: pan, Orbit (C), a view
  list Front / Right / Top / Left / Bottom / Back / Face / All. CC5's mouse bindings were not found for 5 (a CC4 forum
  post: Alt + right mouse orbits) - a gap in these searches. Epic's "Navigating MetaHuman Creator in Unreal Engine"
  (page read): a toolbox column on the left - Presets, Import, Head and Body, Materials, Hair and Clothing, Export,
  Assembly - each opening a tool palette with the tool's properties below; the viewport's own toolbar: Preview Material
  (Topology / Skin / Clay), Environment Lighting (Studio, Red Lantern, Moonlight, Tungsten, custom), Camera framing
  (Face, Body, Far, Hands, Feet; 35 / 50 / 100 mm), LOD0-7, Rendering Quality (Medium / High / Epic), View Mode; an
  Animation Bar once rigged; Preview Scene Details hiding grooms and clothing; panels rearrangeable.
- **CC5's window, from the user's own screenshots** (2026-11-03, CC5 trial, 14 pictures in the user's
  `Pictures/Screenshots 1/cc5`): menus File, Edit, Create, Character, Modify, Mesh, Render, View, Window, Plugins,
  Script, Help; View: Pan X, Zoom Z, Orbit C, Home, Center, Camera View; Window: Workspace, Tool Bar, Bone Manager F3,
  Content Manager F4, Scene Manager F5, Modify F6, Visual Settings F7, Facial Profile Editor F8, Animation Player F9,
  Packager Ctrl+F4, Cloth Layer Settings; Render: Preview F10, Render Video, Render Image, AI Image / Video Render;
  Create: Create Character, AccuRIG, Generate Head from Photo, Wrap into CC5 HD Actor, Transformer, bakes, Morph Slider
  Editor, Head & Body Morph Sliders, Prop, Accessory, Cloth/Hair/Acc, Animation, Light, AI Mesh; Plugins: Auto Setup,
  Headshot 3, Smart Search, Omniverse, ActorMIXER. Two toolbar rows (file, transform and camera tools, quality "High",
  light toggle, Animation Player, Turntable; Conform, Modify, Morph, Transform, Create Character, ActorMixer, AI Studio,
  AI Mesh, online content search) and a Headshot row. LEFT: the Content panel (green title) - category icons in two
  rows, Template / Custom tabs, a breadcrumb (All > Actor > Character), Item / Pack, search, sort, a thumbnail grid,
  a folder tree, Apply / Save / Overwrite; vertical side tabs Content, Scene, AI Mesh Generator, Visual. CENTRE: the
  viewport (blue-grey gradient, "SubD 1" label), the Animation Player bar under it. RIGHT: the Modify panel (green
  title), six icon tabs - Attribute (name, type, eye element, contact, corrective expressions, auto-blink, SubD
  viewport / render, load CC3+ / CC5 HD neutral bases, ActorMixer, convert to game base), Motion (edit pose, import
  animation, edit facial, HIK T-pose, facial profile editor), Morph (a checkbox tree Actor > Body: Full Body,
  Shoulder, Arm, Hand, Chest, Back, Waist, Hip, Glute, Leg, Foot, Pose Corrective, Base Morph; Head: Full Head, Skull,
  Forehead, Brow, Eye, Ear, Cheek, Nose, Mouth, Jaw, Chin; a search box, the sliders beside the tree, Bake / Reset),
  SkinGen (Skin / Makeup / Outfits), Material (a mesh / material / shader-type table, texture settings), Expression
  Wrinkles (a head map of regions); a side tab Cloth Layer Settings. Look: near-black greys, lime-green titles and
  highlights.

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
- **Epic's licences read at source (2026-11-04, in the user's Chrome - Epic answers WebFetch with 403):**
  - State of Unreal 2025 post: "We've updated the Unreal Engine EULA so MetaHuman characters and animation can be
    used in any engine, such as Unity or Godot, as well as creative software like Maya, Houdini, and Blender".
  - UE EULA §4(a)(i): asset files "such as character models and animations ... that you developed using Engine Code.
    Such asset files remain Non-Engine Products even if included in Products that use or rely on other video game
    engines. Please note that certain assets that we make available under separate agreements are available for use
    only with Unreal Engine." Seats are waived for "indie developers (those making less than $1,000,000 a year)".
  - UE EULA and the Epic Content License, "Non-Compatible Licenses": you "may not combine Licensed Content with code
    or content that is licensed under ... GNU General Public License (GPL), Lesser GPL (LGPL) (unless you are merely
    dynamically linking a shared library), or Creative Commons Attribution-ShareAlike License." -> JustStage (GPL)
    can't ship or be built on MetaHuman content.
  - UE EULA, Engine Tools: "If your Product includes Engine Tools, you may only Distribute it through either the Fab
    Marketplace or through a fork of Epic's GitHub UnrealEngine Network" -> an add-on to MetaHuman Creator can't be
    our open-source app.
  - Content License, MetaHuman Content Addendum: "MetaHuman Content that you acquire may only be used and shared as
    UE-Only Content"; Epic "exclusively owns ... MetaHuman Creator and Rig Logic, including as embodied in MetaHuman
    Content". This conflicts with the State of Unreal post; Epic's FAQ that might settle it needs a login.
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


*agent, 2026-10-30* — every JustStage function surveyed for what is new since 2026-10-29, plus Blender 5.0–5.3 (notes,
tables ranked by quality, training buckets, apps and how they work, every search logged:
[`../plans/2026-10-30-research-all-functions.md`](../plans/2026-10-30-research-all-functions.md); facts to re-check
before the rec list):
- Motion: NVIDIA's stack on SOMA (the body layer in §5) — GEM-X (video → body, hands, world-space motion; NVIDIA Open
  Model License), Kimodo (text and keyframes → motion, 282M parameters, 700 h of mocap; its card says "ready for
  commercial use"; under 3 GB with the text encoder on the CPU), MotionBricks (real-time motion from keyframes), SOMA
  Retargeter — each ported to C++/GGML by `localai-org` (Apache-2.0). Any-skeleton motion: UniMate (code MIT, weights
  CC-BY-NC-4.0), MoCapAnything V2, TopX (paper only).
- Rigging: SkinTokens still the best released; Armature, a new free AI rigging app (under $100k revenue) exporting USD;
  Rigel3D and AniGen (generate a mesh already rigged) — papers without code.
- Clothing: NGL-Prompter — sewing patterns from one image with a stock vision-language model and GarmentCode, no
  fine-tuning (code not found).
- Image to 3D: Pixal3D (MIT), SUPRA-Tex (MIT, relightable textures); Meshy T2's repo has no licence; Hunyuan3D 3.x
  looks API-only.
- Faces: no released model makes a full ARKit-52 set for any head; the training-free route is transferring the shapes
  from a CC0/MIT template (MPFB2 Faceunits, ICT-FaceKit); NFR has MIT code, its weights' licence unstated.
- Blender: 5.2 experimental XPBD cloth and hair dynamics; 5.3 EEVEE Material Lighting nodes, Gaussian splats,
  world-space animation copy/paste, Vulkan the default.
- LoRA on 8 GB (trainers' documented minimums): a vision-language model up to ~11B by QLoRA (Unsloth); FLUX.2 klein-4B
  borderline at ~8 GB in int8; Z-Image (10–12 GB) and Qwen-Image (24 GB) don't fit; no trainer documents LoRA for 3D or
  motion models.
- Not verified: AccuRIG, Cascadeur and Mixamo internals; GEM-X's VRAM; MetaHuman 5.8's notes; nothing run here.

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
- Re-checked on the installed 5.3 beta (`E:\blender-5.3.0-beta`, files read, not run) and the `blender-v5.3-release`
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

- **Blender 5.3's USD exporter** (`bpy.ops.wm.usd_export`, listed 2026-11-03): `root_prim_path`, `selected_objects_only`,
  `export_shapekeys`, `export_armatures`, `export_hair`, `export_materials`, `generate_materialx_network`,
  `generate_preview_surface`, `export_textures_mode`, `relative_paths`, `export_custom_properties`,
  `custom_properties_namespace`, `convert_orientation`, … ; `bpy.types.USDHook` is there for our attributes.
- **Blender Lab's MCP, read in its source** (*code read, 2026-11-06*, `projects.blender.org/lab/blender_mcp` `main`
  `dbbf836` = tag v1.0.3's code; `.dev/audit/2026-11-06/research/R4.md` Q1, the exec and CORS lines re-read by me): the
  Blender add-on runs any Python a request of type "execute" carries (`addon/blender_mcp_addon/mcp_to_blender_server.py`
  L245-253, `exec(code, namespace)` inside a `WeakSandboxForLLM`; L322-332) - no token, no allow-list; every tool, named
  ones too, works by sending Python. **26 tools, not 21** (L1709 above): two run Python - `execute_blender_code` and
  `execute_blender_code_for_cli` (its own background Blender). `blmcp --transport http`: stateless Streamable HTTP on `/`,
  `enable_dns_rebinding_protection=False` (L86), CORS `allow_origins=["*"]` (L97). FastMCP 1.x's token auth is constructor
  arguments `blmcp` doesn't pass; no documented per-call hook. No release on MCP SDK 2.x (`mcp[cli]>=1.2.0,<2`; PRs #43,
  #47 open). The add-on opens its socket only with Allow Online Access on (`__init__.py` L34-38, "a grey area"; issue #45
  open). So "the Python tool off" in the permission table (`standards/commands-and-api.md` L105) can't close the door by
  hiding the tool - the plan's Q-APP-3.
- **Allow Online Access and localhost** (*doc read + measured, 2026-11-06*, R4 Q2): off blocks nothing - the manual:
  "Blender cannot prevent third-party add-ons from violating this rule"; a loopback socket round trip worked in 5.3 with
  it off; the extension guidelines' "`localhost` is fine" stands.
- **Live Link** (*doc read*, R4 Q3): Unreal 5.8's "Live Link Plugin Development" names a source plugin
  (`ULiveLinkSourceFactory` + `ILiveLinkSource`) - "the recommended approach for anyone that already has there own
  streaming protocol" - or Message Bus (the sender links Unreal's core libraries; Epic's Maya / MotionBuilder way). No
  Epic page names VMC.
- **VRM add-on on 5.3** (*measured*, R4 Q4): 4.10.4 (2026-11-04) declares `blender_version_max = "5.3.0"`, exclusive
  (`blender_ext.py` L2643): 5.3 refuses it ("This Blender version (5.3.0) must be less than the maximum version (5.3.0)").
  The range in R08 L492 / R09 L250 is 4.2.0 up to, not including, 5.3.0.
- **Installers** (*build code read*, R4 Q5): Blender - CPack WiX `.msi` + zip (signtool via Azure), a hardened-runtime
  DMG notarised (`notarytool`) and stapled, `.tar.xz` + Snap / Steam / Store; Bforartists - Inno Setup `.exe` + zip,
  DMG / zip, `.tar.xz` / AppImage / `.deb`. Labels: WiX 7's binaries carry a maintenance fee at US$10,000+ revenue;
  Inno Setup asks commercial users to buy ("not strictly required"); Velopack MIT.

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

## 14 · The character, part by part

Subsection 14.N holds the facts behind the plan's section N (`../plans/2026-11-06-the-plan.md`); within one,
entries stand in the order they were found. Moved here 2026-11-07 from §1, §5, §10 and the deep read's list
(nothing deleted; a provenance line is copied above each bullet that left its group).

### 14.1 · The bar: CC5's HD Aaron, MetaHuman as a reference

- **CC5's default character, seen** (the user's three screenshots of HD Aaron in CC5's live view, 2026-11-04; kept out
  of the repo): SubD 1; scanned skin maps - pores, redness on the nose and cheeks, stubble, eye bags, neck creases; wet
  eyes with a pink caruncle and lower lid rim and a shadow under the upper lid; a dark blue-grey stage, a strong key
  with soft image light. Against it ours was one flat skin colour, no brows, faceted outlines, a bright flat eye white.
  The gaps and the recs: `docs/plans/2026-11-04-realism.md`.
- **MetaHuman's character API in Unreal 5.8's Python** (listed headless 2026-11-04, `.dev/gate/out/mh_api.log`): 242
  `MetaHuman*` names, among them `MetaHumanCharacterFactoryNew` (a character asset), `MetaHumanCharacterEditorSubsystem`
  (`try_add_object_to_edit`, `commit_skin_settings` / `commit_face_state` / `commit_eyes_settings` /
  `commit_makeup_settings`, `request_texture_sources`, `assemble_for_preview`, `build_meta_human`,
  `spawn_meta_human_actor`, `import_from_template`, `conform_to_target_meshes`), `MetaHumanCharacterExportBlueprintLibrary`
  (`export_dcc`, `export_dna`, `export_materials`). So the gate's preset benchmark can be scripted; whether texture
  requests need Epic's cloud (and a login) is not yet known.
  Answered 2026-11-04 (the API's own docstrings, `.dev/gate/out/mh_doc.log`): `commit_skin_settings` synthesizes
  preview textures locally and "will also discard any high resolution textures"; `request_texture_sources` is
  "Request high resolution textures" (Epic's cloud, `desired_texture_sources_resolutions`); `build_meta_human` stops
  at "Character is not rigged" without the cloud auto-rig. A face DNA does ship:
  `Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/Content/ArchetypeDNA/SKM_Face.dna` (not tried with
  `import_from_face_dna`). The MetaHuman benchmark was then dropped - CC5 is the standard (TASKS).
- **CC5's side of the gate, its limits** (*measured, 2026-11-04 / 05*; moved here from RESUME.md 2026-11-07):
  memory `cc5-control` (first call `check_cc5_connection`; `exec_python` off; the trial's dialogs are
  the user's to click). Limits measured: captures are 600 x 600 whatever is asked; the trial logo covers 27-73% of
  the width and 44-55% of the height - parts are framed above or below it; FBX / OBJ / ABC exports are counted (30 in
  the trial; 2 used: 10:41 mine, 12:06 the user's). HD Aaron's export (CC5's Blender Pipeline plugin, "Export FBX",
  Selected Models, SubD 1, every box off) and its CC Blender Tools import: `.dev/gate/cc5_aaron_blender/`
  (`aaron_cctools_eevee.blend`, `aaron_cctools_cycles.blend`). Hair on disk for the gate: `Classic Slick Back.rlHair`,
  `Stubble.rlHair`, HD brows (`F:\Reallusion Content\Reallusion Templates\Hair\Group\`).

### 14.2 · The gate: views, measures, runs

- **The stage's light, trials** (Cycles, the library's Average woman, 2026-11-04): three area lights (key 300 W, fill
  100 W, rim 120 W) under AgX base contrast read flat and pale; Poly Haven's Studio Small 09 as the fill at 0.5 flattened
  it again; at 0.25, no fill light, AgX "Medium High Contrast" and -0.3 EV the face had shape. AgX's looks in 5.3
  include "AgX - Medium High Contrast" (set and rendered).
- **The gate's first run (2026-11-04, measured; `../plans/2026-11-04-realism.md` §6a):** EEVEE 5.3's world light on a
  plain 18% grey sphere's lit side is 17-19% weaker than Cycles' (key 1.006, rim 0.84-0.91); on the face, lit skin
  agrees across EEVEE, Cycles and Unreal (MetaHuman's baked skin material on our maps), shadows part (EEVEE's jaw shadow
  15% darker and 28% harsher than Cycles'). Unreal 5.8 facts: commandlets can't spawn actors; `-ExecutePythonScript`
  quits the editor after the script; `name.1001.png` / `name_1001.png` import as a UDIM virtual texture; UV0 is the
  first UV layer.
- **Clean skins and the first clean-input gate** (*measured, 2026-11-06*, `../gate/2026-11-06/report.md`,
  `../plans/2026-11-06-inputs-audit.md`): hair comes out of scan photos by region, not by strands alone - DullRazor's
  line closings (Lee et al. 1997) catch single strands and stray hairs but neither the dense lash band round an eye
  nor stubble (dots) and they also catch fine creases; so a ~5 mm band round the eye and brow holes is dropped, strands
  are found in the eye zone and by the hairline, stubble is found per texel (dark-mark density >1.35x the scan's own
  clean face) - the scan list's by-eye stubble tags were wrong (HSR0040's upper lip; LPS's whole beard 911k texels),
  and holes are filled with mirrored real skin, the colour by a smooth multi-width fill. Women's scans carry eye makeup
  (liner, mascara, shadow): darkening round the eyes held to 12%. The pore tile: Ten24's sample scan (its page: "Feel
  free to use this scan as you wish for both commercial and personal projects. All we ask is that you provide us with a
  credit") - its Level_01 relief normals on a clean upper cheek, 33 mm, Moisan-tiled; the LPS tile it replaces carried
  his beard's streaks (his whole lower face is stubble, `lambertian.jpg`); LPS's forehead has no hair but deep
  wrinkles and scan streaks. With the new tile the pore depth that matches HD Aaron's upper cheek is 0.15 mm
  (bands 1.135 / 0.884 vs 1.154 / 0.894; 0.3 mm gave 1.74 / 1.31), the microrelief 0.015 mm (fine 0.63 vs 0.51). The
  torso: Artec's scan wrapped (our torso onto it, NICP, p50 2.2 / p90 4.6 mm) then baked - the prototype's rigid
  placement read the two bodies' difference as relief. The eye's recess measured the scans' way on base v2: upper
  -2.9 mm (man) / -2.2 mm (woman) against the real -2.86 - no move needed. Found unapplied in code while fixing: the
  design's lash settings (180 upper, 0.08 mm, melanin 1.0), the caruncle (proof 4c), the photo iris (harness only).
- **Data in an image's alpha, the live view, and other gate findings** (*measured, 2026-11-06*, gate runs 7-8,
  scratchpad `factors.py` with its `show-<node>` mode - a node's value rendered as emission): a region map with a data
  channel in its alpha (`face_regions.png` RGBA, the image's alpha mode Channel Packed) read right through
  `image.pixels` (R 0.125 on the neck) but the live view's pore depth there came out 2x and more - R, G, B divided by
  an alpha of 0; a separate greyscale map fixed it (`face_share.png`). The skin builder's read of the same map
  (`image.pixels` of an 8-bit RGBA PNG) divided too: the head tile's neck roughness came out up to 1.0 (255) - the
  dark characters' neck patch in gate run 9. Rule: no data in alpha, anywhere. Also
  measured: the skin's scattering halved changes neither side of the face (our shadow side L* 50.7 either way against
  HD Aaron's 36.4 - his face's form, not our material); our upper lashes rise 12 deg median root to tip (p90 22, none
  past 60 - the "spikes" at the eye view are the longest middle lashes seen end-on); the live view's tearline (a
  Fresnel mix of transparent and glossy) drew a dark outline round the opening on a dark stage (hidden: gone; Cycles
  not checked) - an additive film keeps the eye seen through it.
- **Measuring skin detail** (*R1 Q6*): no published skin-specific measure. Better than our band standard deviation:
  DISTS (MIT; built for textures that don't align pixel for pixel), the radially averaged power spectrum, ISO 25178
  band-limited roughness on the relief maps (light-free); for mid-scale form a multi-scale ridge filter (Frangi 1998) at
  ~1.5-8 mm - it separates long ridges (veins, tendons, creases) from speckle, why run 11's "fine" rose while the hand
  read flatter.
- **The proof log of 2026-11-05 / 06** (*measured*; moved here from RESUME.md 2026-11-07, where it was kept until
  then; `.dev/gate/parts/proof*/`; bands then = L* standard deviations of a Gaussian band-pass in pixels at 1024,
  fine / pore / fold - not comparable with `tools/gate/measure.py`'s bands in mm). Entries (1), (1b), (4b), (4c) and
  the brows / lashes judgments were measured on skins with painted hair - VOID ("Painted hair in our inputs", §14.8):
  - (1) face skin, one character (Average man, composed 632 = HSR0040 + LPS colour and relief): cheek 0.42/0.97/0.72 vs
  Aaron 0.45/0.96/0.79 = EQUAL; forehead 0.96/0.91/0.57 vs 1.73/1.74/0.92, by eye close (his glossier). Made by: pore
  relief 1.0 / 0.3 mm + per-pore shine, region factors (`tools/make_face_regions.py`: forehead pores x2, micro x5),
  the scans' geometry relief (`scan_bake.py NAME normal`, `skin_base._relief`). Scan colour alone = 0.40 pore band
  (Aaron without normals: 0.40) - pores are relief. NEXT: the same on 4 characters (scan relief bakes for hsr0027
  0028 0015 0042 0081 0102), then step (2) body relief. Seen: at face distance the gap is now shape (MakeHuman
  proportions, HSR0040's heavy bags), tone, hair - not texture.
  - (1b) face skin on 6 characters (library men and women, light to dark, the six "Scan" skins with relief,
  `.dev/gate/parts/proof_chars/`): cheek pore band 0.97-2.18 (Aaron 0.96) - HOLDS for any character; forehead men
  55-70% of Aaron's, dark woman equal, young women lower (smoother, as real). Defect: a scar-like mark on Scan woman
  B's cheek (HSR0028's). NEW RISK found: face SHAPE - MakeHuman's faces read generic and puffy round the eyes beside
  Aaron's; testing a real face shape (a scan's fit in our topology) on the same skin next.
  - (1c) face shape: HSR0040's real face (his fit in our topology as a shape key, `.dev/gate/parts/proof_shape/`) on the
  same skin reads no more like Aaron than MakeHuman's - shape is NOT the main gap. Tone is: melanin 0.07 overshoots
  (face L* 40 vs Aaron 48.5; a*/b* match), ~0.045 should match - a per-character choice. Sheen (roughness x0.8): no
  visible change. THE EYES are now the main face-distance gap (`.dev/gate/parts/proof_eyes/`): ours meet the eyeball
  at a sharp lid edge with no margin, no pink wet rim, lashes thin, white flat, pupil small; Aaron's lids have a thick
  wet pink margin wrapping the eyeball, lashes on it, a larger pupil, a lighter iris. Pupil 0.38 / white x0.85 /
  today's lashes: barely visible change (the pupil may be GNM's pupil-disc geometry - check). NEXT: the eye region
  (step 4 moved up): lid margin (geometry thickness + a wet pink rim by MPFB2's `mpfb_eyelids` mask?), tearline,
  pupil, iris; then the library characters rebuilt with today's lashes, brows, eyes open, scan skins.
  - (4) eyes, measured (`.dev/gate/parts/proof_eyes/`, scratchpad `eye_exp3.py`): our white L* 80 vs Aaron's ~48-60 -
  his sits in the lids' shadow (CC5's occlusion); ours uniform. Our occlusion film (eyeshell) darkens nothing in EEVEE
  (hidden or not: same) - a fault to fix first. The pupil is GNM's 2.7 mm pupil-disc geometry (the shader's
  PupilSize 0.082 -> 0.15 changed nothing). Cornea reflection x0.3: no change. Lashes: radius 0.08 mm, 180 upper,
  melanin 1.0 give a visible lash line at face distance (adopt). Amber iris overshot to yellow.
  FOUND: the occlusion film (eyeshell, rendered solid red: `proof_eyes/eevee_eye_ours_shellred.png`) does not fit the
  opened eye - a lens in the middle of the opening, strips under the upper lid and above the lower one uncovered, so
  its lid-edge darkening lands inside the opening. FIXED in code: `eye_layers.refit` finds the lids again (test
  `test_they_follow_the_lids_when_the_eyes_open`).
  - (4b) eyes on one character (Average man, Scan man A skin; scratchpad harness `eye_photo.py`, options per factor;
  `.dev/gate/parts/proof_eyes/`, crops beside Aaron's eye view; measures: white L* inside the opening found by a red
  film render, iris annulus Lab, a vertical L*a*b* profile under the iris). Each against Aaron:
  white x0.71 (warm R x1.05) L* 67.5 vs 68.3 = EQUAL; a polar-unwrapped iris PHOTO (`.dev/downloads/other_samples/
  commons_green_iris`, recoloured by its lightness to albedo 0.053/0.030/0.021, structure ^0.7) L* 24.6 C 14.8 vs
  27.2 / 11.3, detail bands 1.9/3.5/4.2 vs 1.1/2.6/3.9 = EQUAL (its light collarette ring is this photo's; brown photos
  are content); the iris' own specular 0 (the cornea shell glosses - at 0.5 a grey haze sat on the pupil); pupil 0.45
  of the iris vs his 0.49 (a parameter; the procedural eye's PupilSize did nothing); the lid MARGIN: our lower lid's
  edge stands up to 3.3 mm off the eyeball (a dark crevice, L* 21) - sealing the one vertex ring onto the eyeball left
  a 4-8 px band (MakeHuman's lid has no margin geometry); the TEARLINE strip (ICT's ring, eyeEdge) shaded as wet pink
  tissue (0.50/0.22/0.20, roughness 0.15, coat 0.6) gives a 32 px band L* 60-72 a* 12-18 vs his ~36 px L* 65-72 a*
  10-19 = EQUAL. Thick lashes (radius 0.08 mm, 180 upper, melanin 1.0) make the lash line. Not done: caruncle (a
  geometry mask at the inner corner barely shows), veins (invisible at face distance). Shape: MakeHuman's own sliders
  (bag -1, eyefold concave -0.7 / up 0.6, height1 +0.6) open the eye (9.7 -> 10.7 mm at the iris, iris covered 12.8 ->
  9.7 deg) - a per-character choice. Seen at face distance and NOT eye parts: our skin round the eyes reads rougher
  and far paler and less red than his (lid L* 80 a* 5 vs 60 a* 19) - recheck the skin proof (1) there.
  - (4c) the same settings on four library characters (own skins, no tuning; `proof_eyes/*multiphotolashocctearpink*`):
  iris, white, pupil hold; the pink tearline strip DISPROVED as made - it outlines the whole opening (a drawn pink ring,
  worst on dark skin). Pink on the lower lid's part only, fading at the corners, the upper part the clear tear film
  (`*multi2*lowonly*`, five characters): a wet waterline on all five, no ring; darkened by the character's own melanin
  (x(1 - 0.7 min(m/0.25, 1)) toward 0.20/0.08/0.06 - conjunctival melanosis; `*multi3*`). The strip's inner end as the
  caruncle: hidden under the corner skin (failed). The caruncle as the corner skin painted wet pink (0.45/0.18/0.16,
  geometry mask past the inner corner, scratchpad `lid_margin_mask.py mode=caruncle`): shows, as on Aaron. Seen: our
  default opening shows white below the iris (scleral show - a stare), Aaron's lower lid meets the iris: shape, per
  character. Final run of every piece on five characters: `*final*`. EYES: equal by measure at face distance on one
  character, the pieces hold on five; at close-up still below (flat white without veins or soft shading; the photo is a
  hazel eye recoloured - a light collarette ring; brown photos are content). Adoption into code waits for the user's go
  (the list in the session report, 2026-11-05).
  - (2) body, started (`.dev/gate/parts/proof_body/`; RESEARCH "Body relief and muscle definition"): MakeHuman's muscle
  gives bulk, not definition (Muscular man vs Aaron); a texture-tile seam across the chest and arms on two characters
  (to diagnose); no bare athletic torso among our downloads (HSRD bodies clothed but HSR0042-Body-045; deep3dstudio's
  athletic man in a tank top; Ten24 in a sweater). Triplegangers' free full-body sample (the user's link): athletic, in
  underwear, CC BY-NC-ND - a LOCAL test source only, behind a registration the user must do.
  - (2b) the user's links, the user: "i want you to download all these ones i am giving you yes downloade dthem":
  Artec 3D "Body scan" DOWNLOADED (`.dev/downloads/artec_body_scan/`, 60.5 MB; its `license.txt`: CC BY 3.0 Unported,
  "Body scan by Artec 3D"; 765k triangles, 8K colour, no normal map; a lean athletic man, arms raised). Triplegangers
  needs the user's registration; Digital Reality Lab's form (name, email, company, use) mails the link to the user.
  Measured (scratchpad `scan_torso2.py`, the torso framed as Aaron's; bands fine/pore/fold/form at 1024 px, form =
  12-48 px = the muscles): ours 0.31/0.18/0.38/2.27, Muscular man 2.00/0.88/0.53/2.76, the Artec scan as scanned
  0.27/0.40/0.71/3.12, Aaron 0.86/0.67/1.23/4.34 - the scan carries real definition (72% of Aaron's form band; his
  is a sculpted glossier physique), its fine/pore come from our layers. The chest SEAM (`proof_body/*nonormal*`,
  `*flatcolour*`): COLOUR - the head tile's painted colour ends at the upper chest against the torso tile's, plus
  a dark line from the colour map's unpadded island edge; normals cut: no change. NEXT: fit the Artec torso to our
  body and bake its relief into our UVs (the face route on the torso), apply to two body types, measure; the seam
  fix (pad the islands, blend the head tile into the torso tile at the border).

### 14.3 · Assets, sources, licences, patents

- **Texturing.XYZ's licence** (2026-11-04): not reached - searches "Texturing.XYZ license terms redistribution AI
  training open source" and "texturing.xyz EULA 'license' personal indie studio redistribute textures" returned other
  vendors' terms (no raw redistribution, embedding in finished media only, AI training by separate permission:
  aiTextured, Cubebrush, a Gumroad seller, CGTrader's 2026-05-15 change); `texturing.xyz/pages/licenses` 404;
  `texturing.xyz/policies/terms-of-service` covers the shop, not the textures. A gap: only Texturing.XYZ can say.
  **READ 2026-11-04 (the redo):** the licence is `texturing.xyz/pages/terms-of-service` ("Terms & conditions /
  Licensing", updated 2026-08-29): §7 bars releasing Materials "or derivative products under an Open Source License"
  and any use "with artificial intelligence, machine-learning ... systems or software" without written authorisation -
  a user's own purchase, imported, is the only route (`../plans/2026-11-04-research-licences-redo.md`, with every
  other licence the CC-only filter had cut: Pexels, Unsplash, Pixabay, BlenderKit, Superhive, Fab, CGTrader,
  Sketchfab Store, HumanScanRepository, Renderpeople, Triplegangers, Ten24's commercial-use sample scan).

*web, 2026-10-29* — the eye shells (step 1.5: occlusion and tearline), public docs only:
- **The gaps search (2026-11-04, the session "just-stage asset search", `../plans/2026-11-04-research-gaps.md`; its
  query logs checked - no licence filter; three slips logged in its §0):**
  - Older people of colour at 16K exist, all paid (IMPORT, none SHIP): 3D.sk raw heads - Black men 62-66 (six),
    Black women 62, 63, 70; Arab people 61-72 (five, two women); Indian 61-62 (four) - ages read per scan page (3D.sk's
    age filter undercounts); HumanScanRepository HSR0274 Hispanic F 67, HSR0172 African M 63 (EUR 35 a pose, model
    releases stated, a custom SHIP licence invited); Triplegangers Bertha Horan Hispanic F 76 ($49.99; SHIP "with
    written consent"). No scan labelled Southeast Asian, Indigenous or Pacific Islander anywhere searched.
  - Photos for calibration and patches: Pexels 8265216 (elderly Indonesian man, 4000 x 6000, sharp pores), 14684597;
    nappy.co (CC0) is closing "in the next few months". **Fetched 2026-11-05** (the asset search session, by hand
    from nappy's own search pages; `.dev/downloads/nappy_2026-11-05/`, 27 photos, 67 MB, `SOURCES.md` with each
    page URL, uploader, pixels, what it shows and the search terms): nappy.co/license re-read that day - "All photos
    posted on Nappy are licensed under the Creative Commons Zero (CC0) license"; DON'T "Resell our photos without
    significant modification", "Repost our photos on other stock websites"; AI and model releases not mentioned.
    Best for colour: Nigeria Art Market x3 (6720 x 4480, an older man's face and hands), MetaLab's hands (6720 x
    4480, a grey-bearded man), the walker (7000 x 4836, older feet and hand), "Grandpa" x11 (2560 x 1707), an older
    Latina woman (2048 px). Black-and-white close-ups (four) give relief and wrinkles, not colour. Two files
    uploaded by the account `pixabay` are REFERENCE until nappy's CC0 over Pixabay-origin photos is read.
  - Sclera: no shippable sharp macro; keep procedural veins (rec 12) - Bérard et al.'s published recipe is in patent
    US10217265 (Disney / ETH, listed active to 2036); calibration numbers (CCLRU redness by region,
    vessel 18.8 um, melanosis 92.5% in Black people, pinguecula 73% over 60) in its §2.
  - Renderpeople "Fabienne & Percy 001" (mother and child, `.dev/downloads/scans/rp_fabienne/`; Sketchfab uid
    8c9bfd4fb8a444b3a42a4fc31935a2fb, uploaded by the studio's own account `renderpeople` 2020-05-12, "CC
    Attribution" by/4.0, tags incl. "kids", "child", "noai" [API, read 2026-11-05]): **both people used like any CC
    BY scan** - credited in `ATTRIBUTION.md`, inputs to our own maps, the likeness rule (never one scan's face
    shipped) as for every scan, no AI training on Renderpeople uploads (the "noai" tag, also on Carla and Mei [API];
    Sketchfab: "the tag may not be enforceable outside of the Sketchfab platform" for CC models - we follow it
    anyway). CC BY 4.0 §2(b)(1) leaves personality rights unlicensed for anyone [page]. (The user, 2026-11-05: "go" -
    replaces "the child is never used"; TASKS "FABIENNE & PERCY: THE CHILD USED LIKE ANY CC BY SCAN".)
    **Measured 2026-11-05** (Blender, the 200k FBX's UVs on the 8K diffuse, per-island texel density = sqrt(UV px² /
    surface mm²)): one merged mesh, one uniform density - the child's face 3.98 texels/mm, his neck and ear 4.0, his
    hand 3.98, the mother's face 3.99 (0.25 mm a texel; his face island ~900 px across). Below our face tile (6.0) and
    Ten24's face (7.6-11): pores (0.1-0.3 mm) sit at or under one texel, so it is **not a pore source**; it is a
    source for a child's skin colour and its variation across the face (a medium-brown, school-age boy - the age my
    estimate from the render, not stated), and for head and face proportions (his body is posed, legs wrapped round
    her, so limb lengths only in part). The 2026-11-02 windows ("only shoes and hair") missed his face, ears, neck
    and hand - they are in the atlas (upper right). The texture has lighting baked in, so delighting first, as for
    every scan.
  - **The two patents' claims, read 2026-11-05 (not legal advice; the claims as Google Patents prints them [page],
    the user's go "your rec all"):** US10217265B2 "Methods and systems of generating a parametric eye model" (ETH
    Zurich, Disney; Active, expiry 2036-10-26): 21 claims, three independent (1 method, 9 system, 16 stored
    instructions), each requiring ALL of - eye data "from an eye model database"; an eyeball model built by
    "iteratively establishing correspondences among the plurality of eyes" (rigid alignment, fitting by "identifying a
    limbus ... in one or more input images", non-rigid deformation, update); an iris model by "sampling a plurality of
    patches from the plurality of eyes and merging the plurality of patches into a high-resolution synthesized
    texture ... constrained by the iris control map". The veins ("grown from seed points in directions and by amounts
    controlled by one or more vein recipes") are claimed only as additions to that (claims 2, 10, 17).
    US10217275B2 "Methods and systems of performing eye reconstruction using a parametric model" (same family, Active,
    expires 2036-11-09): 11 claims, three independent (1, 6, 11), each requiring input "a three-dimensional face scan
    ... from a multi-view scanner", an eyeball model fitted to it, an iris control map from "a proxy iris centered on a
    pupil ... texture information ... from at least one of the one or more input images", and "rendering the vein
    network onto a sclera backplate determined from the one or more images". **Our design rule:** our procedural
    veins (rec 12) never form part of a method that fits an eyeball model over an eye database or to a scan AND
    synthesises the iris from patches or a control map taken from images; scan import (HSRD, the 3D.sk heads) keeps
    our own eyes, never one reconstructed from the scan's eye pixels. Veins grown from seeds by our own rules,
    deeper = bluer and blurrier, are then outside every claim's full set of elements. Query: WebSearch
    `patent "vein network" sclera "seed points" "vein recipes" Disney ETH continuation` (found the sibling); claims
    extracted from the two pages' `itemprop="claims"` sections.
  - Nails: no texture pack; keep the layered shader (rec 14); plate transmittance per wavelength, melanonychia by
    ancestry and age, lunula visibility by finger, ridges 85% over 60 - its §3; a CC0 hand-and-nail set of 250 people
    aged 18-95 (Yakimov 2024, figshare).
  - Children: measured skin (cheek pores x14 from 3-7 y to 19-23 y; furrow depth; melanin rising to adolescence) and
    eye numbers (the eyeball and iris must not scale with the head); CC5 has no child base or child skin; **Anny**
    (NAVER, Apache-2.0 code, CC0 data) calibrates MPFB2's age targets to WHO growth standards - better than our
    four-anchor blend; FaceBase's per-age head norms tables are open.
  - Better than ours: TAU "Procedural Human Hair" brows (CC BY-SA; compare before rec 8); Thunk3D ear scans on
    Sketchfab (CC BY, geometry). Corrects `2026-10-30-research-hair-eyes-teeth.md` §7: Cem Yuksel's grooms are
    "for your personal or research projects".

*agent, 2026-10-30* — what makes rendered skin read as a photo: relief, pores, shading, light, upscaling, eyes (notes,
ranked by quality, training buckets, apps, every search logged:
[`../plans/2026-10-30-research-skin-detail-shading.md`](../plans/2026-10-30-research-skin-detail-shading.md); facts to
re-check before the rec list; nothing run on skin here):
- Open for the user: whether CC Blender Tools (GPL-3, ships Reallusion texture files) is a clean-room reference;
  whether to train a small FLUX.2 klein-4B LoRA (SimpleTuner: ~8 GB at int8 — skin training data is the blocker).
- **HSRD-100's licence, read at its source** (*page read, 2026-11-06*: the Hugging Face API
  `huggingface.co/api/datasets/digitalrealitylab/HSRD-100` and the card's `README.md`, last modified 2025-09-18):
  `cardData.license` "cc-by-4.0"; the card's "## License": "This dataset is licensed under Creative Commons
  Attribution 4.0 International (CC BY 4.0)", "Commercial use allowed", "Modification allowed", "Distribution allowed",
  "Attribution required", "No additional restrictions"; "Consent: All participants provided informed consent for data
  collection" (consent for collection - personality rights are not licensed: the likeness rule stands). Each pose's
  `pose_meta.json` says `"license": "Commercial"` with `"price_commercial": "70"`, `"price_personal": "35"` - the
  maker's store listing of the same scan, not the grant on the files we downloaded from the dataset; the dataset's
  grant is CC BY 4.0 (ATTRIBUTION.md's row stands). Queries: none - two direct reads.
- **Patents near what we ship or plan - claims read at Google Patents** (*page read, 2026-11-06*; the agent's R2 Q1,
  the claims below re-read by me from each page's raw HTML; **not legal advice**):
  - **US 2024/0346733 A1** (Disney, "Graph simulation for facial micro features with dynamic animation", pending in
    the US; R2: granted AU2024202285B2 and GB2633151B, to 2044 - those claims unread). Claim 1: "sampling, from a
    three-dimensional (3D) representation of a facial structure, a plurality of nodes, wherein each node ... represents
    a pore ...; generating one or more edges connecting a node ... to one or more different nodes ..., wherein each edge
    ... represents a candidate wrinkle ...; generating ... a graph ...; calculating, for each edge ..., an edge weight
    ...; and generating a wrinkle graph". Our `tools/make_microrelief.py` (shipped tile): nodes by Poisson disk on a
    flat 2D tile, not sampled from a 3D face; the furrows are the walls of the nodes' Voronoi cells; pores sit on wall
    junctions, not at the nodes - it lacks claim 1's first element as written. Its docstring describes it as Weiss et
    al.'s method ("pores are a graph's nodes") - to reword to what it does.
  - **US 12,651,397 B2** (Disney, "Graph simulation for facial micro features via pre-computed displacement texture
    maps" - the EG 2024 orientation-bin method; R2: granted, to 2044-04-06). Claim 1: a wrinkle graph of pores and
    wrinkles on a 3D face; wrinkles "assign[ed] ... to one of a plurality of bins" by a wrinkle characteristic;
    "pre-computed displacement texture maps" per bin; "a per-frame displacement texture map"; "modifying an animation
    frame". The design's "wrinkle content generated per character by the published orientation-bin method" (design
    L145-147) reads onto it - that route is out. The paper's CC BY licence grants no patent rights (CC BY 4.0 §2(b)(2)).
  - **US 12,062,140 B2** (Microsoft; inventors Baltrusaitis, Hewitt, Wood, Raman - the authors of the tension paper our
    design cites; to 2043). Claim 1: a tension map per vertex, compressed / expanded wrinkle textures "formed by
    aggregating maps of the first face with different expressions using the tension map", applied "according to the
    tension map", rendered. Claim 17 (no render step): "computing a weighted combination of the maps to produce a
    compressed wrinkle texture, wherein the weights ... are negative weights from the tension map" (and expanded from
    positive), "storing" them. Design rule: tension may set the DNA's animated-map weights offline; never build
    wrinkle textures as tension-weighted combinations of expression maps. Raman's MIT add-on carries no patent grant.
    US 12,555,324 (same family, to 2042) and US 8,217,955 (per-pixel stress shader perturbing normals, to 2030): R2.
  - **US 9,269,185 B2** (Sony, "System and method for procedural CG eye meniscus", active, expires 2033-08-24). Claim
    16: "A meniscus plug-in ... comprising: an input module to receive a computer-generated model; an analysis module to
    automatically determine at least one feature of the module in which a liquid component may exhibit a meniscus; and a
    meniscus module to procedurally modify the model or procedurally add to the model to cause a meniscus to appear."
    Our tearline (ICT's ring placed to the lids' opening found automatically, `head/eye_layers.py`) reads close to it.
    Design-around to weigh: the tearline as a fixed part bound to base v2's known margin rows (an MHCLO-style binding, as
    the teeth) - no automatic search for where a meniscus forms. A question for the user (and counsel if wanted).
  - **US 9,336,622** (Sony): claims only a gaze rig with a fixed visual-axis offset of 2-15 deg (R2) - our lid
    darkening is outside; a future look-at rig avoids that offset until 2034.
  - **US 8,922,553 B1** (to 2033-08-28) needs a solve across per-region linear models with continuity constraints;
    **US 11,354,844 B2** (to 2039-10-25) needs masks from muscle action units + "demographic prediction modifications"
    + a modified eyeball / cornea / teeth / tongue / skull asset together (R2) - the approved mixer (a weighted blend of
    whole identities per mask) holds none of the first and not all of the second's elements as R2 reads them.
- **Licences read at their sources** (*page read, 2026-11-06*, R2 Q2-Q5): CC BY 4.0 credit: creator, notices, a link,
  a change notice, the licence URI, "in any reasonable manner" (a linked credits page is CC's own example); CC BY 3.0:
  the licence URI with every copy, the title, a credit "at least as prominent" as others; BY-SA -> GPLv3 is one-way, BY-SA
  4.0 only, "must specify version 3 of the GPL", source form provided, for content "melded with code". REUSE 3.3: every
  `LicenseRef-*` needs `LICENSES/LicenseRef-<id>.txt` (`LicenseRef-cited-data` has none); Ten24's grant needs its own id
  with the text verbatim. Blender 5.3 manifest: `license` and `copyright` take several entries; **extensions.blender.org's
  Terms (1.2): assets inside an extension "must be licensed as Public Domain (CC0)"** - our extension (CC BY, Apache,
  MIT, Ten24 data) can't be listed there; self-hosting a third-party repository is the documented route. Blender's
  "Hair Styles" demo: "CC-BY-SA", no version. SONICOM: no licence file (the paper says MIT, the page "for research
  purposes") - stays REFERENCE. Yakimov 2024 nails: CC0 (figshare API). Curly-Cue: the guides-to-full Python step MIT,
  the switchback generator GPL-3.0-or-later. Artec "Top of hand": "Creative Commons license v4", credit "Top of hand by
  Artec 3D" (the archive's `license.txt` unread). Blender Studio's Human Base Meshes: CC0 (page, README, 25 asset
  records) - but the .blend also carries "The Rain Rig is released under the Creative Commons Attribution 4.0 license"
  and two stylized meshes are "Based on" the CC BY Rain and Snow rigs. Epic's "Send to Unreal" add-on is MIT and ships
  no Unreal plugin; Reallusion's Unreal Auto Setup licence unread.

### 14.4 · Base mesh, topology, UVs

- **The body's UDIM layout** (`tools/make_udim.py` on the default human, hm08's own islands packed per region by
  Blender's packer, measured 2026-11-04): 1001 head and neck 4,934 polygons (everything above 1.28 m), 1002 torso
  1,146, 1003 arms and hands 5,743, 1004 legs and feet 1,310, 1005 nails 245 (MPFB2's CC0 nail masks). hm08 is all
  quads (73,944 loops, 18,486 polygons with the helpers).
- **The base mesh** (2026-11-05, `../plans/2026-11-05-research-base-mesh.md`): hm08 has no lid-margin or caruncle geometry (one ring at the lid edge, measured); Blender Studio's CC0 Human Base Meshes (v1.4.1, downloaded) model both - a 2-3 loop lid margin turning toward the eyeball and a dense inner-corner pocket (rendered); MakeHuman's standard route to another topology is its proxy system (`.mhclo` -> `.proxy`, refit on slider change) [page].

*measured, 2026-10-29* — JustStage's server (`server/`, the kit at just-core `75d3cb01` then `b41154a7`) on this machine:
- hm08's UVs: a median 0.57 UV units per metre of skin over the body's faces (10th–90th percentile 0.40–1.10).

*leads from the user, 2026-10-29, not checked* — cloud face generators as fallbacks for the face test's pictures
(the user: "Canva AI Face Generator: … for commercial projects, provided you follow their AI Product Terms"; "Adobe
Firefly: … trained on licensed and public domain content"; "EaseMate AI: … text-to-image or image-to-image … free
credits"). Their terms, image-to-image control and APIs are unread; the face test runs on the local model first.
- hm08's head (the body's faces above the neck joint, 4,242 faces) holds 21.1% of the UV square — about 1,880 px a
  side at 4096², 3,760 at 8192² — *measured 2026-10-29*.

### 14.5 · Mouth, nails, ears

*web + measured, 2026-10-31* - the face's neutral: lips and lids (`../plans/2026-10-31-audit-face-edits.md`, 18 searches,
every one logged; key claims page-read):
- MakeHuman's CC0 identity mouth targets (in our repo, `extension/juststage/data/fetched/makehuman/targets/mouth/`)
  thin and narrow the lips without moving the seam (`mouth-scale-horiz-decr` narrows 2.9 mm on average, the lip-height
  targets change the seam by under 0.6 mm); the eye-height targets move the lids only 0.75-1.3 mm.

*measured, 2026-10-31* - eye openings, ICT's tear strip and flow between the paintings (face test rounds 50-51):
- *measured, 2026-11-02*: the lips' seam - the clay's contact line (its darkest row in the evenly lit render) against
  MediaPipe's inner lip points on each painting: the clay's sits 3.6-9.9 px lower in every view that sees it (close
  view 6.8, front 4.2 - about 1.3-1.7 mm). The outer lips with the painting brought into the clay's frame (a
  similarity on eye corners and nose): in the close view that fit errs 11.6 px (MediaPipe on the clay misreads the
  corners and nose), in the front view 3.0 px - there the painting's mouth is as wide (158.8 against 156.1 px) and
  as high at the top, its corners ~10 px lower and its lower edge ~5 px lower: a thinner upper lip, a taller lower
  one, the corners turned down (MakeHuman's upperlip-height-decr, lowerlip-height-incr, angles-down).
- **Mouth** (*page read*, R3 Q5): no automatic lip-seal tool or method found; MetaHuman requires sealed neutral lips
  and names no tool (edit the mesh, Update Vertices). Dental scans onto a template: per-tooth labels, a rigid fit of
  each template tooth, a Laplacian deformation of the crown, the template's roots kept (RMS < 0.096 mm); Teeth3DS stores
  per-vertex tooth labels in JSON; Poseidon3D's label format is not stated on its page.

### 14.6 · Shape spaces, sliders, mixing

- **MakeHuman's MHM names for the macro sliders** (`makehuman/data/modifiers/modeling_modifiers.json`, MakeHuman's
  repo, read 2026-11-03): `macrodetails/Gender`, `/Age`, `/African`, `/Asian`, `/Caucasian`;
  `macrodetails-universal/Muscle`, `/Weight`; `macrodetails-height/Height`; `macrodetails-proportions/BodyProportions`;
  `breast/BreastSize`, `/BreastFirmness` - the ids `juststage:sliderIds` carries (character-data-model §0, §1.3).
- **GNM's wrap onto hm08: max error 29.19 mm** (*file, 2026-11-06*, `data/generated/gnm/REPORT.json`; S3) beside the
  mean 0.87 / p95 2.17 mm recorded above; transfer distance mean 4.49 / max 72.9 mm.

### 14.7 · Face rig, expressions, body rig, capture

- **OpenRigLogic and SWIG's version** (measured 2026-11-04): at ea253d5 its `python/riglogic/RigLogic.i` calls SWIG's
  runtime macro `SWIG_EXPAND_AND_QUOTE_STRING(PYDNA_SWIG_TYPE_TABLE)`. SWIG 4.5.1's `swigrun.swg` no longer defines it
  (`SWIG_TYPE_TABLE_NAME` is `SWIG_STRINGIFY(SWIG_TYPE_TABLE)` there), so MSVC failed on the generated wrapper (C2065
  `py3dna_13_5_2`, C3861); PyPI's `swig` 4.3.1 still defines it (`SWIG_QUOTE_STRING`). The C++ libraries and benchmarks
  compiled under 4.5.1.

*web, 2026-10-29* — re-checked for the user's "is there another better body … i feel you ddint reasearch well" and
"we need to create non human body as well like creatures just like cc5 allows" (Opus re-check of the review):
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

*web, 2026-10-29* — the eye shells (step 1.5: occlusion and tearline), public docs only:
- Lead for the face rig (step 7), contents not yet read: MakeHuman's functional packs also list "Faceunits 01: ARKit
  style face units" and "Visemes 01/02" (Microsoft and Meta/Oculus style), CC0.

*web, 2026-10-31* - anything new from Apple for face capture? (the user: "is apple iphone have anthing new since ai
boom"). Queries: "WWDC 2026 ARKit face tracking new features" (only a visionOS 27 ARKit summary - Vision Pro, no face
tracking named - and 2017-2021 material); "iPhone face capture 2026 MetaHuman Animator Live Link Face update depth";
"Apple Vision framework face landmarks 2026 new API iOS 26 face tracking blendshapes" (`FaceObservation.Landmarks2D`
from iOS 18; one forum report of iOS 26 landmark coordinates outside [0,1]); "iPhone 17 TrueDepth camera face tracking
improvements ARKit blendshapes 2025 2026" (nothing specific); developer.apple.com "ARKit iOS 26 what's new face tracking
ARFaceAnchor" (ARFaceAnchor: 52 blend shapes, 60 updates a second, gaze since ARKit 2, multiple faces, ARKit 5's better
accuracy - no iOS 26 change found); Epic's sites "MetaHuman Animator monocular video webcam Android audio driven
animation release notes":
- Apple: no new face-capture API found for iOS 26 / WWDC 2026 - ARKit's face tracking (TrueDepth, 52 blend shapes) is
  as it was; a search gap, not proof.
- Epic, since 2025: MetaHuman 5.6 - MetaHuman Animator in real time from mono cameras (most webcams, many phones,
  Android through Live Link) and from audio alone (with the speaker's emotion and plausible head movement); 5.7 notes -
  its mode on iOS devices without TrueDepth; 5.8 - Live Link Face for Android (take recording, RTSP streaming), RTSP on
  iOS too, a new real-time audio-driven model, single-camera body capture (Fab plugin, Windows, offline, experimental).
  Device advice in Epic's docs: iPhone 12 or newer, 16 / 16 Pro recommended.

*web + measured, 2026-10-31* - the face's neutral: lips and lids (`../plans/2026-10-31-audit-face-edits.md`, 18 searches,
every one logged; key claims page-read):
- MetaHuman's neutral is sealed: "In the neutral pose the lips should be completely sealed, without gaps and without
  intersections"; "Expressions are stored and treated as differences from the Neutral Pose"; for likeness scans a
  "relaxed face with the teeth touching, but not clenched" (Neutral Pose; Expressions for Likeness Calibration - page read).
- MetaHuman's lids turn about the eye: rotate `FACIAL_[L|R]_EyelidUpperA` joints and check the lids keep "a sectional
  contour of the eyeball" (Skin Weights - page read); "The eyelid shell and folds shouldn't intersect".
- ARKit's `mouthClose` is jaw-relative ("closing of the lips without relation to the position of the jaw", Apple - page
  read). Measured on hm08: Faceunits `mouthClose` at 1 lowers the upper lip 2-7 mm and lifts lower lip and chin ~27 mm;
  `eyeBlinkLeft` at 0.2 sinks the upper lid ~0.7 mm further into the eyeball (1.1 mm at 0.5) - the flattening
  MetaHuman warns about.
- MakeHuman's Faceunits 01 (Mika Suominen): 52 targets with ARKit's names, every metadata entry "license": "CC0";
  `faceunits01.zip` 257,821 bytes, sha256 d113107b…, from files2.makehumancommunity.org/functional/; not in our system
  asset pack nor in MPFB2's repo (MPFB2 loads it when installed); byte-identical to naver/anny's copy. Same topology as
  hm08: no transfer needed.
- ICT-FaceKit (MIT, push 2020-12-01): 57 expression OBJs (ARKit names without tongueOut, split L/R, plus cheekRaiser,
  PupilDilate), 100 identity modes, eye occlusion, lacrimal fluid and lash meshes; FACS map in its README (AU45 ->
  eyeBlink, AU7 -> eyeSquint, AU24 -> mouthPress, AU28 -> mouthRoll).
- Transfer tools: Blender's Surface Deform (built in); ShapeKeyWrap, ShapeKeyTransferBlender, mesh-expression-retargeter
  (GPL-3); `vasiliskatr/deformation_transfer_ARkit_blendshapes` (MIT, Sumner & Popovic 2004) and its example-based
  facial rigging repo (MIT); ARKitBlendshapeHelper and arkit-blendshape-tool have no licence.
- GNM keeps its zero expression neutral on purpose (a mean expression "would result in a face with slightly closed eyes
  and a slightly opened mouth"); its fit solves identity, per-region expression, pose and camera against ~600 dense
  landmarks with a self-intersection penalty (arXiv 2607.23687, page read).
- **Blinks** (*page read*, R3 Q4): OmniFaceRig's rest of the page says only "upper-eyelid vertices snapped to lower lid
  and locally relaxed" - no vertex set, weights or iterations: the details are ours. CC5's manual: Transformer >
  Character > "Correct Eyeblink" snaps the upper lid onto the lower. MetaHuman moves the lids by joints (EyelidUpperA/B,
  EyelidLowerA/B); expressions are joint animation with per-vertex corrective shapes at LOD0 only.

### 14.8 · Skin colour: scans, the scan route, delighting, hair out, the AI painting route (retired)

- **The face test's colour maps** (`.dev/facetest/chars/<name>/face_albedo.png`, measured 2026-11-04): all four
  people's maps share one brightness (median ~0.54 / 0.31 / 0.22 linear) - `test_face_project.py` scales every map to
  the skin model's luminance at melanin 0.012, then a per-channel gain normalised to luminance 1, and makes a dark
  person dark through the scene's exposure (Amara -2.59 EV). A skin taken from them needs its own brightness.
- **Skin variety methods not yet in our files** (the same agent, 2026-11-04): chromophore-space mixing - each scan
  layer inverted per texel to melanin and blood maps by our own skin model, characters made by shifting them, a
  residual kept (Donner et al. 2008; Aliaga, Hery & Xia 2022 arXiv 2201.10695; Aliaga et al. EGSR 2023; no code
  found); age and person variety from per-region multiscale detail statistics (Golovinskiy et al. SIGGRAPH 2006, page
  read: "adjusting the apparent age of faces"); parametric freckles as a point process on UV (Schneider, Egger &
  Vetter FG 2018, snippet); skin-optics ageing (Iglesias-Guitian et al. EG 2015, no wrinkles); WildCap (CVPR 2026, GPL-3,
  weights' data licence not stated, nvdiffrast non-commercial, Linux) and DoRA (non-commercial); AvatarTex (3DV 2026, a
  FLUX UV LoRA, snippet). Body sites (PMC11084701, 53 Korean women, rankings only): elbows then knees darkest and most
  melanin and erythema; forearm redness rises with age.
- **CC5's SkinGen, its inventory** (reallusion.com/character-creator/skingen.html, page read 2026-11-04, the user's
  link): a layer stack ("dynamic skin effects layer stack", per-layer sliders, 4 blend modes - normal, multiply, overlay,
  soft-light; free version capped at 15 layers; "up to 4K real-time editing for each body material"). Skin elements
  90 free / 270 premium / 360: skin base 42; normal effects (muscle, sinew, fat crease, vascular, skin noise, skin
  details) 86; skin details (decal, coloration, capillary, roughness) 61; blemish (acne, freckle, mole, suntan) 38;
  acquired (liquid, scale, scar, tattoo) 39; body hair and scalp (scalp, beard, body hair) 55; nails 29 + nail presets
  10. Makeup elements 79 / 281 / 360. "SkinGen is embedded with MicroSkin textures licensed from TexturingXYZ"; "powered
  by Adobe Substance Technology". The digital-human page (page read): "Authentic Human Skin" (skin, hair and nail
  materials from 3D scans, adjustable by age), "Intricate Wrinkles" (high-res scans, a real-time wrinkle shader), the
  Digital Human Shader (SSS, micro normal) for skin, eyes, teeth, hair; HD Ultimate Morphs 172; "40+ scanned assets".
- **Painted hair in our inputs - the measurements on them are void** (*checked 2026-11-06*, after the user: "why are
  our lashes paintedt on cc5 lashes and beards are not painted on"). **CC5 paints no hair** (HD Aaron's files on disk,
  `.dev/gate/cc5_aaron_blender/hd_aaron.fbm/`, `aron_with_hair.fbm/`): lashes a mesh (`Std_Eyelash` colour and
  opacity - cards), brows a mesh (`Brows_Base`, `Brows_Color`, `Brows_Hair`), stubble a mesh (`Beard_Transparency`);
  his head colour map `Std_Skin_Head_Diffuse.jpg` has no lashes and no brows, only a faint grey shaved tint on the jaw
  and lip under the stubble mesh. **Ours:** Daniel's head colour (`.dev/skins/man_a/Daniel skin.base_color.1001.png`,
  from the face test's AI-painted face, rounds 74-101 - `tools/build_skins.py`) has the lashes painted along both lids
  and stray brow hairs; Scan man A's (HSRD scan photos) his stubble; Scan man A's normal map (the scan's geometry
  baked) shows lumpy rows at the hairline and the beard's edge [seen, to confirm per region]; the pore tile on every
  character (`.dev/facetest/pores_lps.png`, the Lee Perry-Smith scan's cheek) shows seams at its quarter lines and
  elongated streaks like stubble [seen, to confirm against the scan]. Our strand lashes and brows (`hair/lashes.py`,
  `brows.py`) are there but 0.1 mm thick and sub-pixel at face distance in EEVEE (no minimum width) - the painted
  ones are what shows. No step ever removed hair from a skin; nothing approved painting it. **Void until re-measured on
  clean inputs:** the face-skin proof (cheek pore band "equal on six characters"), the brows and lashes judgments, the
  lower-lid wet margin and caruncle, the lid band (28-50 px), every face-distance comparison with Aaron (he wears his
  Stubble mesh, ours none). **Stand:** iris, white and pupil (measured inside the opening), the geometry (lid
  anatomy, slider sweep, recess), the gate's tooling, the live view's calibration (111-117% of Cycles: L280's ratios are 113 / 117 / 111% - was: "113-117%" until 2026-11-07).

*leads from the user, 2026-10-29, not checked* — cloud face generators as fallbacks for the face test's pictures
(the user: "Canva AI Face Generator: … for commercial projects, provided you follow their AI Product Terms"; "Adobe
Firefly: … trained on licensed and public domain content"; "EaseMate AI: … text-to-image or image-to-image … free
credits"). Their terms, image-to-image control and APIs are unread; the face test runs on the local model first.

*measured, 2026-10-29* — the face test (`tools/face_test/`):
- FLUX.2 klein on stable-diffusion.cpp ignores a starting picture sent as `init` alone at the preset's strength 1
  (seven views came back byte-identical); sent as `init` and `refs` (house-paint's `aiphoto/edit.js`: "the photo is
  both init and reference image") it repaints each view in its pose and framing — the front view's eyes within ~2 px
  of the clay's. Seven 1024² views: 22 s for the first (the model loading), then ~22 s each queued (219 s in all).
- Projection: 36,046 head triangles rasterised to 4,037,726 texels of a 4096² UV in 4 s (numpy); seven views reach
  69% of the head's texels (the back of the head has no view); the painted/clay ratio's 5th–95th percentile
  0.55–2.2 after each view's brightness is matched.
- A projection seam appears where one view's picture frame ends; fading each view's weight over its last 80 px
  removes the hard line (a soft band stays on the shoulders).
- MetaHuman: "The MetaHuman database of real-world scan data has been significantly expanded to offer more variation
  in character mesh shapes and textures … retain more authentic realism, such as blemishes"
  ([MetaHuman 5.6](https://metahuman.com/news/metahuman-leaves-early-access-with-a-feature-packed-new-release),
  *search snippet*); the skin panel picks from a "Face Texture Index" of scanned textures
  ([skin material tools](https://dev.epicgames.com/documentation/metahuman/skin-material-tools), *search snippet*).

*agent, 2026-10-30* — what makes rendered skin read as a photo: relief, pores, shading, light, upscaling, eyes (notes,
ranked by quality, training buckets, apps, every search logged:
[`../plans/2026-10-30-research-skin-detail-shading.md`](../plans/2026-10-30-research-skin-detail-shading.md); facts to
re-check before the rec list; nothing run on skin here):
- Taking the light out: OpenDelight (SIGGRAPH 2026, face-specific; code GPL-3, weights' licence not stated), Marigold IID
  (OpenRAIL++).
- Upscaling: SeedVR2 (Apache; its README: 8 GB works with GGUF Q4) the strongest; SUPIR non-commercial; Real-ESRGAN and
  MoSR run inside stable-diffusion.cpp.

*agent, 2026-10-30* — AI texturing of our own mesh, the methods (notes, ranked by quality — the papers' own claims, no
independent comparison exists — training buckets, apps, every search logged:
[`../plans/2026-10-30-research-ai-texturing.md`](../plans/2026-10-30-research-ai-texturing.md); facts to re-check
before the rec list):
- The drift fix that needs no training: before projecting a view, warp it onto a render of the paint already on the
  mesh where they overlap (ConsistenTex, ECCV 2024, no code), face landmarks as the backstop for eyes, nose and lips.
- Painting all views of a given mesh: Hunyuan3D-Paint 2.1 is the reference others compare to (21 GB; its licence
  doesn't apply in the EU, UK or South Korea); 2026 methods claiming better — LumiTex, NaTex, UniTEX, TRELLIS.2, MatLat
  — mostly on non-commercial bases, 24 GB+, or unreleased. Runs here today: MV-Adapter, an ONNX conversion of its SD2.1
  image+mesh model (2026-10-29; CPU, CUDA, WebGPU; weights Apache, the SD2.1 base OpenRAIL++) — 512 px per view, so base
  colour only.
- Reference + depth per view on our engine: an Apache LoRA for FLUX.2 klein (`refcontrol`) keeps a reference picture's
  identity while following a depth map; runs on stable-diffusion.cpp; trained on klein base, not the 4B we run;
  untested.
- Removing baked light: Marigold V2 albedo (2026; code and weights Apache; a LoRA on Qwen-Image-Edit-2509; 17 GB in
  PyTorch; stable-diffusion.cpp untested); the no-model way first — fit the light from the mesh's known normals and
  divide it out, with a baked crease-shadow map.
- Seams: one view per mesh face, colours levelled across seams, then blended (Waechter et al. 2014, `mvs-texturing`,
  BSD-3).
- Face UV generators: OMGTex (CVPR 2026, MIT code, on non-commercial FLUX.1-dev) the best released; TOPOS describes
  our target exactly, no code.
- Small training on 8 GB: an SDXL LoRA fits (kohya: "8GB GPU memory (10GB recommended)"); a FLUX.2 klein 4B LoRA is
  borderline (SimpleTuner: ~8 GB at int8, 16 GB recommended).
- Open for the user: whether OpenRAIL weights (SD2.1, Marigold IID) are acceptable. Nothing measured this session.

*agent, 2026-10-30* — photo to a 3D head on our base, the research the user asked for (notes, every search logged:
[`../plans/2026-10-30-research-ai-photo-to-head.md`](../plans/2026-10-30-research-ai-photo-to-head.md); facts to be
re-checked before the rec list):
- Best single-photo shape method found: **RealDenseFace** (arXiv 2608.09238, code 2026-08) — first on the NeRSemble
  single-photo leaderboard (1.610 mm mean surface error; Pixel3DMM 1.659, SMIRK 2.276): a network predicts, per face
  pixel, the head-surface point it shows plus depth, then Gauss–Newton fits the face model to those thousands of
  matches. Code MIT, weights' card MIT; its training data includes Ava-256 (CC BY-NC); the solver is CUDA-only (to
  rewrite in NumPy); ONNX export untested; VRAM on 8 GB unmeasured.
- Why the face test's fit failed: only identity was free (camera, pose, expression fixed, so identity absorbed every
  mismatch); the AI's views disagree 5–40 px; MediaPipe's jaw and outline points slide with the view but were tied
  to fixed vertices; sparse points don't pin depth; the prior was swamped. GNM's report solves identity, expression,
  pose and camera together; Google says it will release the dense landmarks it fits to.
- To our head: wrap FLAME 2023 Open (CC-BY-4.0) onto GNM once with the existing wrap tool; each fit then becomes a
  linear 3D projection onto GNM's space.
- Feed-forward avatars: MeshLAM (CVPR 2026, textured mesh) — no code; LAM, GAGAvatar, FaceLift, CAP4D, Arc2Avatar —
  Gaussian splats, not meshes. Pro apps (MetaHuman From Mesh, Headshot Mesh mode) first make a 3D surface from the
  photo, then fit their template to it; Headshot 3's photo mode is reported weak on shape.
- Not verified: the FLAME file RealDenseFace needs, its VRAM, Wrap's and KeenTools' docs (connection errors), whether
  stable-diffusion.cpp runs Qwen-Image-Edit 2511.

*web, 2026-10-30* — Meshy's image-to-3D, read at the guide the user linked
([meshy.ai/tutorials/image-to-3d-model-complete-guide](https://www.meshy.ai/tutorials/image-to-3d-model-complete-guide),
*page read*; the user: "i gave you meshy … but you never even looked at what it does or how it works"):
- One photo (≥ 1024 px, plain background, even light, front or ¾) plus an optional material prompt → a "white model"
  (geometry, ~1–2 min; "multi-view synthesis" — "Generate Multi-view" predicts the sides, back and ¾ views first) →
  remesh → texturing: "UV unwrapping, multi-view diffusion, back-projection, and super-resolution" (~1–6 min) → PBR
  maps when on: base colour, normal, metallic, roughness. **Retexture** "reruns only the texture pass" on an existing
  mesh with a new prompt — the job JustStage needs on its own head. Characters: A- or T-pose; auto-rigging separate;
  "hair and fur work better with Text-to-3D than with a photo". Exports GLB, FBX, OBJ, USDZ, STL; models Meshy 7/6/6 Lite
  (closed, cloud). Nothing on faces specifically.
- So the professional texturing pipeline is the family the face test built by hand (views → back-projection), with
  what it lacked: the views made TOGETHER by a multi-view diffusion model (so they agree — no drift), super-resolution,
  and PBR maps estimated from the result.

*web, 2026-10-30* — texturing a given mesh from AI images, the latest open methods (the user: "did you search for
latest techniques for all of our app functions?", after pasting TRELLIS.2, Meshy/Tripo, BumpMesh and multi-view
diffusion re-texturing). Checked against: commercial use, 8 GB, any graphics card:
- **Multi-view diffusion painting a given mesh** (all views at once, guided by the mesh's own geometry, so the views
  agree and stay on the mesh — the drift the face test fights): MV-Adapter (`huanngzh/MV-Adapter`, Apache-2.0 code,
  1.3k ★, last push 2025-06-26; "geometry-conditioned adapters with low VRAM requirements (<10G)" on SD2.1, ~14 GB for
  SDXL; its texture pipeline needs NVIDIA's CV-CUDA) — README read; Hunyuan3D-Paint 2.1 (PBR maps: albedo, metallic,
  roughness; "21GB for texture generation"; the Tencent Hunyuan 3D 2.1 Community License, whose territory excludes the
  EU, UK and South Korea — *one third-party blog, the licence file not read*); MaterialMVP and TEXGen (no licence on
  GitHub); MVPainter (Alibaba AMAP — the repo name searched wasn't found).
- **A photo split into colour, roughness and shading** (so painted shadows don't become colour or dents): Marigold IID
  (`prs-eth/Marigold`, code Apache-2.0, last push 2026-09-06; the IID weights "CreativeML Open RAIL++-M", SD2-based —
  appearance: albedo, roughness, metallicity; lighting: albedo, diffuse shading, residual) — model card read.
- **Relief from a photo:** StableNormal (`Stable-X/StableNormal`, Apache-2.0 code, last push 2025-08-02), Marigold
  Normals. Weights read 2026-11-05 [page]: `prs-eth/marigold-normals-v1-1` - "License: openrail++" ("CreativeML Open
  RAIL++-M"), "fine-tuned from the `stable-diffusion-2`", 0.9B, F32, `MarigoldNormalsPipeline` in diffusers, "any
  larger input image should be resized to make the longer side 768 pixels" (so pore-scale use means 768-px crops);
  `Stable-X/stable-normal-v0-1` - metadata "apache-2.0", README empty. For rec 18's test (local measurement) the
  licence is a label; shipping anything made with the OpenRAIL weights waits on the user's open question above.
- **Photo to textured 3D head:** no open, permissive, photoreal tool found (KeenTools is a commercial service; CRM is MIT
  but general objects; a CVPR 2026 feed-forward animatable textured-mesh head — code and licence not found).
- All of the above run in PyTorch, mostly CUDA-only: the family's engine (stable-diffusion.cpp) runs none of them as
  they are. TRELLIS.2 is MIT (12.5k ★) but needs ~24 GB (§7).

*measured + web, 2026-10-30* — the image model that paints each view (the realism recs' first step, and the user's
questions on FLUX 3 and Krea 2:
[`../plans/2026-10-30-research-image-models.md`](../plans/2026-10-30-research-image-models.md), every search logged):
- **refcontrol on our engine, measured** (stable-diffusion.cpp master-1024-77b72a2 CUDA, RTX 2070 Super 8 GB): image 1
  our head's depth at the left40 view (rendered in Blender; nearest 0.5th percentile to 0.22 m behind it, near = light),
  image 2 the approved painted front, prompt `<lora:flux2_klein_4b_refcontrol_depth:1.0> refcontrol`, 1024², seed 1,
  `--offload-to-cpu`. On FLUX.2 klein 4B distilled (4 steps, CFG 1): 44 s; a photoreal picture of the same person
  turned to our head's pose; its face points (MediaPipe) sit 11.3 px from the clay view's (median 12.1, worst 30)
  against 14.5 px (median 14.7, worst 33) for the painting without depth — 22% closer. On klein base 4B Q8_0 (the
  model it was trained on, `leejet/FLUX.2-klein-base-4B-GGUF`, 28 steps, CFG 4): 468 s, 12.7 px — no gain.
- FLUX 3 Image Klein (2026-10-15, 5.6B; FLUX Kommunity licence, free under US$5M revenue — secondary source): one model
  for text-to-image, editing with up to 10 references and layout boxes; **no depth, pose or structure input** in its
  README; needs its 9B prompt upsampler; testers call it "a strong editor and a weak generator of people". No depth
  LoRA for it found. Failed to load on this card in stable-diffusion.cpp without a `--max-vram` budget (just-core
  RESEARCH, 2026-10-27).
- **FLUX 3 Image Klein measured** (Q8_0, Qwen3-VL-4B, 16 steps, the clay view as its one reference, ~99 s a view,
  card peak 7,165 MiB with `--offload-to-cpu` alone): 6.2 px on left40 (seed 2: 7.2), 12.7 and 7.9 px on the close face
  views where FLUX.2 klein drifts 39 and 44 px; front 5.6 (FLUX.2 4.5). Photoreal skin. With the front photo as a
  second reference it drew the front's pose (177 px) — one face across views comes from painting each next view on a
  render of the paint already projected.
- **RealDenseFace's network measured** (code `LinzhouLi/RealDenseFace` 4dbdf1de, MIT; weights from its HF repo, sha256
  checked; PyTorch 2.6.0+cu124 in `.dev/venv-rdf`; one 512² picture, no FLAME, no solver): ViT-B 224.5M parameters —
  1,098 MiB allocated, 104 ms (fp32), 1,394 MiB, 54 ms (fp16 autocast); ViT-S 67.8M — 481 MiB, 54 ms / 600 MiB, 33 ms;
  the whole card's peak 1,995 MiB with the desktop's 588. All keys load; four 512² maps out (2-channel UV correspondence
  and three 1-channel maps). Its `flame_assets.npz` holds FLAME's UVs and faces only (5,023 vertex UVs, 9,976 faces) —
  the mesh itself is `flame2023.pkl`, whose download page shows only a sign-in form (flame.is.tue.mpg.de, 2026-10-30).
- **FLAME files, downloaded by the user and checked 2026-10-31** (`.dev/cache/flame/`, git-ignored; zips' sha256:
  FLAME2023Open a6b4c3dc…, mediapipe_landmark_embedding 9b7f96d4…, FLAME_masks c196afeb…). `flame2023_Open.pkl` — its
  readme: "available under a Creative Commons Attribution 4.0 International License", cite the FLAME paper in
  publications — references only numpy and scipy's `csc_matrix` (read with `pickletools`, loaded by an allow-list
  unpickler; no chumpy): `v_template` 5,023×3, `f` 9,976 triangles, `shapedirs` 5,023×3×400 (its
  `supr_expression_metadata`: the last 100 are expressions, from the SUPR head, male — so 300 identity), `posedirs` 36,
  5 joints (`J_regressor`, `kintree_table`), linear blend skinning. The masks (`FLAME_masks.pkl`, 14 regions: face,
  lips, nose, eye regions, eyeballs, ears, scalp, neck, forehead, boundary) index the Open head and sit where they should
  on it (lips' centre front-low, eyeballs ±0.032 m, ears ±0.076 m). The Mediapipe embedding: 105 MediaPipe points as
  barycentric coordinates in FLAME triangles. The download page also offers, by the user's choice downloaded too:
  FLAME 2023 academic (`flame2023.pkl`, `flame2023_no_jaw.pkl`), the FLAME 2020 Blender add-on, the texture space
  (1.2 GB) — all non-commercial, for testing only; and D3DFACS registrations (`d3dfacs_alignments.zip`, 5,225,133,752
  bytes, sha256 9b3b2255…, public link, the page's data licence; 47,384 PLY frames in FLAME topology, a folder per person and per FACS action-unit combination such as
  `1+2+5`, 8.9 GB unpacked - kept zipped) for testing the face rig. Its other datasets (FaMoS, CoMA, VOCASET, LYHM)
  link to their own sites with their own sign-ups. The page notes: RingNet needs FLAME 2019; DECA, EMOCA and GIF need
  FLAME 2020; a converter maps FLAME 2023 academic expressions to the Open model's (not tested on older versions).
  The page's code list: a TensorFlow fitting framework (sample FLAME; fit to 2D landmarks, 3D landmarks or registered
  meshes; sample the texture space; VOCA templates), a Chumpy one (fit to scans), BFM-to-FLAME (convert Basel Face
  Model colours and meshes), a PyTorch photometric fitting framework (fit FLAME to an image with a differentiable
  renderer), PyTorch FLAME (load FLAME, landmarks embedded in its surface), RingNet, DECA, EMOCA, VOCA (speech-driven
  animation of a FLAME template from audio), GIF (StyleGAN2 conditioned on FLAME renders), and the FLAME-Universe list
  (github.com/TimoBolkart/FLAME-Universe). Datasets by sign-up on their own sites, for testing later: FaMoS
  (tempeh.is.tue.mpg.de; 95 subjects x 28 dynamic expressions, 600K frames) for the face rig, VOCASET
  (voca.is.tue.mpg.de; 12 subjects x 40 speech sequences with audio) for lip-sync; CoMA (coma.is.tue.mpg.de; 12 subjects,
  12 extreme expressions); LYHM (York Headspace; 1,216 neutral scans) - licences not read.
  Their download pages, read signed in (2026-10-31): FaMoS - FLAME registrations in 7 7z volumes (6 x 10.7 GB +
  3.2 GB, all needed to extract, 108 GB extracted), plus TEMPEH's training images and scans (~400 GB); CoMA - registered
  data 2.4 GB (`files.is.tue.mpg.de/tbolkart/COMA/COMA_data.zip`, public link - downloaded to `.dev/cache/flame/coma/`),
  raw textured scans 29-50 GB a subject; VOCA - audio 71 MB, sentences 17 KB, raw scans 142-224 GB a subject, registered /
  unposed / unposed-cleaned data 15 GB each, template meshes 2 MB, the trained VOCA model 12 MB, its training data 8 GB.
  VOCA's training data holds `data_verts.npy`, `raw_audio_fixed.pkl`, `templates.pkl`, `subj_seq_to_idx.pkl` (VOCA's
  `config_parser.py`: `./training_data/...`) - the four files FaceFormer's README asks for, so the package speech-driven
  methods read. Links on `download.is.tue.mpg.de` need the site's sign-in (without it they return a web page); links on
  `files.is.tue.mpg.de` are public. FLAME_PyTorch (`soubhiksanyal/FLAME_PyTorch` 5a85f60; GitHub says MIT, its file
  header claims MPG rights needing a licence agreement) runs FLAME through smplx's `lbs`: joints from the shaped mesh,
  pose correctives from (R - I) of the four non-root joints in order, transforms about each joint's rest place - the same
  steps as our `flame_fit.Flame`. The photometric fitting repository (`HavenFeng/photometric_optimization`) is MIT.
- **The FLAME fit, measured 2026-10-31** (face test): RealDenseFace reads our clay renders as well as the paintings
  (its 105 MediaPipe-embedded points 6-8 px from MediaPipe's on the head views, 12-14 px close); FLAME 2023 Open fits
  the clay views' predictions to 2-4 px, the paintings' to 3-5 px (12 px on the close front view). The paintings'
  non-rigid difference from our clay, by MediaPipe (rigid shift removed): 4-7 px on the head views, 7-14 px close -
  1-2 mm, no more than the two detectors disagree; the fitted change didn't follow it. A whole-head model fit doesn't
  resolve this head's remaining differences; they are mid-scale forms.

*web, 2026-10-31* - is MediaPipe the right tool for aligning the paintings? (the user: "from my searches it is not the
best and is old, are you sure you should be using it?"). Queries: "best face landmark detection model 2026 more
accurate than mediapipe" -> no 2026 landmark model benchmarked against MediaPipe on 300W/WFLW found; one comparison
table (detection: RetinaFace 0.95 at ~1 FPS vs MediaPipe 0.94 at 36 FPS; MediaPipe's landmark stage 0.88 +/- 0.15); a
surgical-setting study (arXiv 2507.18248): lighting and head pose are the known weak points; SCRFD's weights
non-commercial; "dense face alignment correspondence model open source 2026 dense landmarks" -> only older dense
methods (PIFA 2017, DenseReg 2017, 2DASL 2019); "align generated face image to 3D render dense correspondence warp
texture projection" -> Yu et al. ICCV 2017 (a learned per-pixel flow plus a matchability mask between a photo and a
rendered 3D face model), a 3D spatial transformer network (learned TPS + camera), landmark warp then dense optical
flow refinement, morphable-model correspondence by projection and TPS. Not found: a source on aligning AI-generated
images to renders specifically. RealDenseFace (2026; first on the NeRSemble single-view board; already measured here)
is the modern form of Yu et al.'s idea: dense per-pixel correspondence to a head model.
- The user's pasted search answer (2026-10-31, a Google AI answer on video face mocap for Unreal), checked: RealDenseFace
  first on NeRSemble's single-view board, dense UV correspondence + relative depth, fitted to FLAME, real time - matches
  its README and code read here (its README: "80+ FPS" online; the answer's "84+ FPS on an RTX 4090" and "CVPR 2026" not
  verified - only arXiv 2608.09238 seen); labels the answer omits: code MIT, weights trained on Ava-256 (CC BY-NC), its
  code expects the academic FLAME 2023 file, its solver is CUDA-only. NeuFace is a method for 3D face pseudo-labels on
  videos (TMLR 2024, ICLR 2025 poster; FLAME through DECA) - code and licence not found (arXiv 2310.03205); DECA and
  EMOCA need FLAME 2020 (non-commercial). Other FLAME video trackers found: philgras/video-head-tracker (CC BY-NC 3.0),
  Pixel3DMM (CC BY-NC 4.0). Search note: our search tool's extended query "is there a better face point model than
  mediapipe 2026 RealDenseFace vs MediaPipe face tracking alternatives" returned only SDK vendors' pages (Banuba,
  visage|SDK 151 points, OpenSeeFace) and not RealDenseFace - named-candidate, leaderboard and GitHub/arXiv/Hugging
  Face searches find what plain queries miss here.

*web, 2026-10-31* - the standard fix for misaligned projected pictures. Queries: "Floating Textures Eisemann optical
flow multi-view texture projection misalignment" -> Eisemann et al., Floating Textures (Computer Graphics Forum 27(2)
409-418, Eurographics 2008 best student paper, doi 10.1111/j.1467-8659.2008.01138.x): projective texturing from several
views with imprecise geometry or cameras gives blur and ghosting; it computes optical flow between the projected
textures and warps them to agree; Dellepiane et al. (IEEE TVCG 2012, "Flow-based local optimization for image-to-geometry
projection"): flow between overlapping images fixes the local misregistration that shows as ghosting or as jumps where
one camera's part meets another's; "multi-view texture mapping misaligned images optical flow correction latest method
2025 2026" -> Volino et al. (BMVC 2014): surface-based optical flow between views for multi-layer texture video; no
2025-2026 method found (a search gap; newer work may sit under neural textures or Gaussian splatting).

*measured, 2026-10-31* - eye openings, ICT's tear strip and flow between the paintings (face test rounds 50-51):
- MediaPipe's Face Landmarker on a clay render (no brows, flat colour) guesses: between two clay renders a degree or
  two of lid apart, its brow points moved 9-11 px (median), nose 5.5 px (max 13.8; the nose unchanged), eye rings 6
  px, face oval 3.1 px, lips 1.3 px (face view, 1024 px); its lid contour read a near-shut clay eye as matching an
  open painted one. On a clay, measure the lids from its colours (the eye opening is what isn't skin-coloured); keep
  MediaPipe for the paintings, where its lid lines and iris (radius 36.7 px in the face view, against our geometry's
  5.83 mm iris = 36.4 px) hold. A circle fitted to the clay's coloured iris under-read it (26-29 px).
- Flow between the AI's paintings (Floating Textures, OpenCV DIS on the light-free colours, judged on held-out views):
  at pore scale (difference of Gaussians 1.5-4 px) the paintings don't correspond at all - correlation 0.03-0.14 -
  each view invents its own pores, and the close view its own brows, eye bags and moles; at feature scale (3-16 px)
  flow from a quarter resolution raises agreement on two of three held-out views (face 0.411 -> 0.445, front 0.554 ->
  0.568 at 6-16 px) without blurring. But in a full round (52) it hurt: raw DIS flows between views 20-37 px at the
  median (p90 up to 83 px), the mean at its 15 px cap over half the face, pores -20%, the eye bags flattened. With a
  forward-backward check (Sundaram, Brox & Keutzer, ECCV 2010: |w + w'|^2 < 0.01 (|w|^2 + |w'|^2) + 0.5) the features
  (lids, lip line) stay near zero but smooth skin keeps 15 px patches - DIS's aperture problem on low-texture skin
  whose shading differs between paintings. Bilinear resampling alone costs pore-scale detail; Lanczos keeps it.
  Re-judged 2026-10-31 on the paintings made in sequence (one person): agreement without flow rose (face view 0.514,
  front 0.748 at 6-16 px; the front's pore band 0.366); DIS and RAFT (torchvision `raft_large` C_T_SKHT_V2, BSD-3,
  weights from download.pytorch.org, 20.1 MB) both raise the front and lower the face and the 40-degree view - a
  learned flow doesn't change the verdict.
- Painting the views in sequence with FLUX 3 Image Klein (sd-cli edit mode, measured 2026-10-31): given two pictures
  - the re-projected composite first, the hero painting second - it painted the hero's own front view into the
  30-degree view (lips 180 px off); given the composite alone it keeps the pose (lids 1.8-5.4 px, lips 4-12.5 px) and
  carries the painted part's person into the rest of the head, 100 s a view on the 8 GB card. Over nine views in a
  chain the skin tone drifts darker and more orange.
- TEXTure's trimap (Richardson et al. 2023, read 2026-11-02 at ar5iv.labs.arxiv.org/html/2302.01721; searches
  "TEXTure trimap keep refine generate z-normals ..."): a meta-texture keeps, per texel, the face normal's z
  component it was painted from; a region painted before is "refine" when "the current view provides a better
  colorization angle", otherwise "keep" (frozen); "generate" where unpainted. Refine regions are repainted with a
  checkerboard mask over the first 25 sampling steps; the paper gives no threshold.
- *measured, 2026-11-02 (round 65's paintings)*: under that rule (the current view's cosine 0.2 better than the best
  earlier view's), 0-23% of each view's painted part would be repainted (the profiles most); it would not have kept
  left40's grey scalp out of left90's start - left40 supplies 84% of left90's scalp there and is kept. The profiles'
  scalp blotches (grey-green on left90, dark smudges on right90) are FLUX's own, where that painted grey meets the
  clay. The paintings' backdrop inside our mesh's outline (head painted smaller than the mesh at the scalp): 0.1-4.6%
  of each view's head pixels, nearly all weighted under 0.05 by facing - not the bright streak on the 40-degree
  view's forehead edge (that render clips to white there; the coat lobe at grazing is the next suspect).
- *measured, 2026-11-02*: MediaPipe's iris centre on the close painting sits 9.4-11.9 px (1024 px) below the circle
  through the iris' edges (row chords where the white starts, least-squares circle, Kasa 1976), 4-6 px on the front
  painting: the hooded lid hides the iris' top and MediaPipe takes the middle of what shows. On our renders, whose
  lids cover less, the two agree within ~4 px. The circles: the painting's 30.8-31.0 px round, ours 29.7-30.2.
- *measured, 2026-11-02*: MediaPipe's lid lines on the close painting run along the outer edges of its thick lid
  margins - the lower one at 311 px where the eyeball stops showing at ~305 (by eye at 4x) - while on our render
  (thin margins) they sit at the edge (315-319 against ~318). In eye widths from the line through MediaPipe's corners
  (by eye at 4x, unwarped painting): the painting's upper lid 0.23 / 0.25 above it, lower 0.05 / 0.02 below, iris
  centre 0.17 / 0.20 above; round 65's 0.26 / 0.28, 0.09 / 0.06, 0.13 / 0.16. Colour segmentation and gradient
  searches for the lid edges failed here (the nose shadow, eye-bag creases).
- *2026-11-02, the skin's source* (`../plans/2026-11-02-research-texture-source.md`): Headshot 3 textures from ONE
  photo plus "a skin-base preset by age and facial hair" merged by blend masks (ai-texturing §6) - we paint ten AI
  views instead. MakeHuman's CC0 skins (Skins 02, downloaded, measured): 2048² whole-body maps in our UV layout, the
  face ~250 px across, painted with shading baked in - not a base. Free scanned heads: Digital Emily 2 is non-commercial; Ten24's sample allows commercial use with credit - "Feel free to use this scan as you wish for both commercial and personal projects. All we ask is that you provide us with a credit wherever it's used" (its page saved 2026-11-04; §14 "The hand donor") (was: "Free scanned heads (Ten24, Digital Emily 2) are
  non-commercial" until 2026-11-07); the Lee Perry-Smith scan stays the one CC-BY head. Nano Banana Pro: ~$0.24 a 4K picture on Google's
  API; Google "won't claim ownership" of outputs and bars using the service "to develop models that compete". SkinGen:
  a skin base under masked layers (blend modes, normal and micro-normal strengths, region tools). Histogram-preserving
  blending (Heitz & Neyret 2018) tiles skin swatches; pores need their own layer. Claude makes no images.
  The scans downloaded and checked, and the method for each step of carrying a scan's skin onto our head (with the
  research each pick rests on): `../plans/2026-11-02-scan-skin-base.md`.
- *2026-11-02, the scan route measured on scan02* (`tools/face_test/scan_*.py`; run log in the working doc §7):
  RealDenseFace on the CPU reads a 1024² picture in a few seconds - 1,511 pairs on a zoomed square-on render
  (~0.25 mm a pixel; the whole-bust render at 1.4 mm a pixel gave 48 usable); our two round views put the same FLAME
  point within 0.53 mm (median). Pairs → `procrustes` → `nricp_amberg` held by the pairs: above the neck 0.9-1.0 mm
  from the scan (the eye-aligned fit without pairs: 1.2), 44 s, 460 MB. Blender's Selected-to-Active bake of the
  scan's colour onto HeadTile at 4096²: 6 s on the CPU. SegFace ConvNeXt-512 on the CPU: 13 views in under a minute,
  2.2 GB; it labels flat-lit scan renders cleanly from the front and calls part of a bald crown "hair" from a side
  turn. A file can break its format's UV convention: scan02's glTF stores V upward (21.5% of skin triangles on black
  read the spec's way, 0.6% flipped).

*from the JustDirect research session, 2026-10-31, not verified here* - a lead for the alignment test: Facepoints
(`myned-ai/facepoints`) - 620 points on the GNM mesh with a per-point error estimate; self-reported accuracy, 0
downloads, CC BY-NC, weak on profiles (their notes: `E:\Dev\Web\just-core\docs\plans\2026-10-31-just-direct-
research-mocap-notes\face-landmarks-juststage.md`). Also suggested there: SEA-RAFT for the flow step, flow rejection,
a limbus ellipse fit for the iris, the crop box from the mesh projected through the known camera. Not on disk here:
Sapiens2 pose weights (only `sapiens2_1b_normal`), RealDenseFace's face-box weights.
- Krea 2 Raw / Turbo (2026-06-22, 12B; Krea 2 Community License, free under US$1M revenue — search snippet):
  text-to-image only; runs in stable-diffusion.cpp; add-ons for identity (V2 non-commercial) and pose (Apache), a
  depth ControlNet card unread; no reference + depth add-on found.

*agent, 2026-10-30* — ComfyUI nodes, FLAME-Universe, the apps that turn photos into head textures, and alternatives
to FLAME (the user: "did we reall check all confy ui stuff to see if somehwone doesnt already havea a really good
working method alreayd?"; notes, 41 searches logged: [`../plans/2026-10-30-research-comfyui-flame.md`](../plans/2026-10-30-research-comfyui-flame.md)):
- `BD_FlameFit` (the BrainDead FaceWrap pack; `pyproject.toml` MIT, no LICENSE file): our pipeline's shape — landmarks,
  fit, per-view projection bake, angle-weighted blend, Qwen fill, transfer to CC5 / MetaHuman UVs — but weaker: FLAME
  shape refitted per view from zero, 105 sparse MediaPipe points, a simplified camera (~3–4 px per landmark, its docs);
  no delighting, normal maps or lashes.
- Most promising (each argued in the notes): UltraTex (SIGGRAPH Asia 2026; paints 6–10 views of a mesh together up to
  2048², albedo + metal/rough, keeps our UVs; low-VRAM ComfyUI build 6.8 GB at 1536 per its author; code and LoRA MIT,
  on FLUX.2 klein base 9B, non-commercial; objects only shown, needs Triton); Hunyuan3D-2's delight model (an
  InstructPix2Pix SD model, `Hy3DDelightImage`; Tencent community licence, not EU/UK/KR); inverse rendering on our known
  mesh (NextFace GPL-3, GTAvatar's UV-space method — our code from the methods); HeadCraft (FLAME + StyleGAN2 UV
  displacement; code MIT, weights' licence unstated, trained on NPHM); FFHQ-UV (50K+ evenly lit 1024² face UVs, the HF
  dataset MIT) as a colour prior; the commercial apps' layering — projected colour for the low and mid frequencies,
  scanned normal and cavity detail on top (MetaHuman: albedo from a scan-trained model, normal/cavity from a library;
  Headshot 3: projection over its base skin, AI delighting, two normal layers).
- Alternatives to FLAME: none shown better than GNM on a shared benchmark; detail comes as a displacement layer on a
  base model (HeadCraft; FaceScape's 4K displacements, non-commercial; HRN Apache-2.0; DECA / EMOCA 256², non-commercial).
  NPHM and Gaussian / NeRF avatars give no riggable mesh; SMPL-X's head is FLAME.
- Not found (a search gap, not proof): a ComfyUI face-delighting node to true albedo, a pore/wrinkle displacement node,
  a face-UV generator for a given layout, a photometric FLAME fitter; Civitai / OpenArt pages never came back.

*measured + web, 2026-10-30* — eyes, lashes and pore sources for the face test (rounds 19–27, `docs/dev/TASKS.md`):
- Painted views must be aligned to, and depth-tested against, renders of the same surface they are projected onto: the
  face test's clay views had the head's open mouth while the paintings closed it, and the 478-point landmark warp
  stretched the painted lips open again (round 43).
- **Hair out of scan colour** (*R1 Q1*): no studio publishes an automatic tool - avoid at capture, smooth geometry
  (ZBrush), paint out by hand. Detection better than DullRazor: Koehoorn, Sobiecki, Rauber, Jalba and Telea 2016 (training-free; code linked, licence unstated) and a learned mask - Ollamberganov et al. 2025's SegFormer-based pipeline, Dice 0.967 against SegFormer alone 0.932 and DullRazor 0.781 on dermoscopy images (HAM10000), no code link, no open hair-segmentation weights checked [page]
  (was: "Telea et al. 2016" and "learned SegFormer masks (Dice 0.967 vs DullRazor's 0.781 on skin-lesion images)" until 2026-11-07). Learned fills
  (LaMa, Apache-2.0) smooth fine texture - a fill from the same scan keeps pores. Makeup-removal models work on
  low-resolution photos only: picking makeup-free scans is the fix.
- **Delighting** (*R1 Q2*): Unity's De-Lighting Tool (MIT, 2020) rebuilds the light from the surface with bent
  normals, AO weighing near against overall light - it handles crease shading the SH fit can't; it needs a bent-normal
  bake Blender 5.3 lacks (we would compute it). HSRD-100 ships each pose's 112 source photos and RealityCapture cameras
  (CC BY) - multi-view specular separation (Su et al. 2022) is possible. MAGINet (2025-12): too low resolution.
- **A face-recognition model for the likeness test** (*API + snippet, 2026-11-06*; query "best open source face
  recognition model 2026 face similarity"): the strongest open recogniser is InsightFace's ArcFace (its weights a
  non-commercial label [snippet: a 2026 playbook, fullstackcv.github.io/playbook/face]); `timesler/facenet-pytorch` is
  MIT (GitHub API, last push 2025-09-16; its pretrained weights' terms unread); no recogniser with both a commercial
  licence and ArcFace-class accuracy was found. The likeness test is a build-time check - nothing of it ships - so the
  weights' licence is a label: ArcFace for accuracy, facenet-pytorch as the MIT fallback.

### 14.9 · Skin relief: mid-scale, pores, microrelief, regions

- **MPFB2's region masks** (CC0, `src/mpfb/data/textures/mpfb_*.jpg` at 6ff1eb35, 2048², hm08's UVs): aureolae,
  crotch, ears, eyelids, face, fingernails, genitals, inside-mouth, lips, toenails - crisp white shapes. Its v2
  procedural skin (`entities/nodemodel/v2`, GPL-3 code) builds on its own services and would need MPFB2 installed and
  run; a trial run in an isolated Blender was refused by Claude Code's permission check as code from outside.
- **The head tile's false shading - Cycles' Normal bake and shape keys** (*measured, 2026-11-06*, scratchpad
  `factors.py`, `bake_probe.py`, `keys_probe.py`; test `tests/blender/test_build_skins.py`): the gate's face (run 5)
  showed a brown lower face with a hard edge on one cheek and dark sockets. One factor at a time on the face view: a flat
  colour map - unchanged; a flat normal map - gone (the face clean, the sockets far lighter). The scan skins' head
  normal (`build_skins.py`: the composed relief moved from the face test's `HeadTile` frames to the UDIM layer's by a
  Normal bake on man_a's `round.blend`) held low-frequency tilt (after a 40-texel blur p50 0.13 / p90 0.31) the
  composed relief does not (p50 0.00). A plain BSDF, no normal map, baked the same tilt: Cycles' tangent frames stay on
  the Basis while the shading normal follows the shape keys - each key that reshapes the face adds it in proportion
  (MakeHuman's ethnic keys moving up to 0.19 m: p90 0.11-0.12 each; `gnm.identity` 0.11; keys of a few mm: 0.002);
  Basis only, modifiers off: p99 0.011. Every scan skin carried the face test character's face as shading. Fixed:
  `build_skins._bake` bakes normals on the Basis with modifiers off. A bare shape-keyed grid reproduces it (p99 0.43);
  a Subsurf modifier hides it (re-evaluated frames). `scan_bake.py` is not affected: it bakes onto the fitted head
  built as a plain mesh (no shape keys).

*agent, 2026-10-30* — what makes rendered skin read as a photo: relief, pores, shading, light, upscaling, eyes (notes,
ranked by quality, training buckets, apps, every search logged:
[`../plans/2026-10-30-research-skin-detail-shading.md`](../plans/2026-10-30-research-skin-detail-shading.md); facts to
re-check before the rec list; nothing run on skin here):
- Relief from images: Sapiens2 normals (human-specific; no non-commercial clause; bans deepfakes), StableNormal
  (Apache), Marigold / E2E-FT, MoGe-2 (MIT, official ONNX) — none tested at pore scale.
- Pores, all training-free: Disney's graph-based micro-wrinkles (SGP 2023), example tiles from the CC-BY 3.0 Lee
  Perry-Smith scan, Blender Studio's tension-map wrinkles.
- Blender 5.3: multires bakes normals, displacement and vector displacement; adaptive subdivision is no longer
  experimental. EEVEE has no Random Walk, IOR or anisotropy for skin scattering — Cycles for the final render.
- BumpMesh (CNC Kitchen, AGPL) pushes brightness as height for 3D printing — the same as ours, not a skin fix.

*web, 2026-10-31* - relief from pictures into geometry (queries: "latest techniques recover 3D face geometry detail
from normal maps normal integration 2026" -> SuperNormal (multi-view normal integration, arXiv 2312.04803),
discontinuity-aware normal integration (ICCV 2025), anisotropic screen-space meshing (CVPR 2025), feature-preserving
decimation for normal integration, Cao et al. inverse plane fitting (CVPR 2021), Ma et al. 2008 gradient-illumination
face normals refining geometry, Wang et al. 3DV 2013 template registration to normal maps, Bouafif et al. 2020 face
normals integrated by weighted least squares; "mesh refinement from normal map open source combine positions and
normals" -> `normal-position-combination` (PyPI 0.0.3, MIT, a binding of Nehab et al. SIGGRAPH 2005's C++), Berkiten et
al. 3DV 2014 (Nehab's linear method combines high-frequency normals with low-frequency positions; Poisson
reconstruction smooths when their resolutions differ), CraftsMan3D (normal-map refiner by differentiable rendering);
"best open source monocular face depth geometry estimation 2026 sapiens2 pointmap MoGe" -> MoGe / MoGe-2 (MIT code;
metric pointmaps, depth, normals, FOV; general, not face-specific), Sapiens2 pointmap 0.4B-5B (human-centric; licence
tagged "other"), no face-specific comparison found):
- For a mesh whose broad shape is right and whose normals carry the detail - our head with the paintings' projected
  normal map - Nehab et al.'s method is the standard: vertex positions solved so the surface's tangents are
  perpendicular to the target normals, held near the original positions; one sparse linear solve.

*from the JustDirect research session, 2026-10-31, not verified here* - a lead for the alignment test: Facepoints
(`myned-ai/facepoints`) - 620 points on the GNM mesh with a per-point error estimate; self-reported accuracy, 0
downloads, CC BY-NC, weak on profiles (their notes: `E:\Dev\Web\just-core\docs\plans\2026-10-31-just-direct-
research-mocap-notes\face-landmarks-juststage.md`). Also suggested there: SEA-RAFT for the flow step, flow rejection,
a limbus ellipse fit for the iris, the crop box from the mesh projected through the known camera. Not on disk here:
Sapiens2 pose weights (only `sapiens2_1b_normal`), RealDenseFace's face-box weights.
- **Normals from the paintings, measured** (the relief the AI painted — eye bags, lids, wrinkles — for a normal map):
  Sapiens2 1B normal (`facebook/sapiens2-normal-1b`, the Sapiens2 License; code `facebookresearch/sapiens2` 7e5bae88 in
  `.dev/venv-rdf`, PyTorch 2.7.1+cu126; fp16, two 1024×768 windows per 1024² picture): 1.4 s a view, 3,557 MiB peak.
  DAViD ViT-L (`normal-model-vitl16_384.onnx`, MIT, ONNX Runtime 1.31 on the CPU — its CUDA provider didn't load): 1.6 s
  a view at 512². Against our mesh's own normals (from the views' depth pictures, the face's inner part, 6 px blur):
  Sapiens2 8.5–12.7° mean (left40 8.5, front 9.1, faceleft30 10.4, face 12.7); DAViD 9.6–15.9°; a flat card 31–34°. Both
  agree with the mesh along the forehead within ~0.1 per axis. Sapiens2 kept. (The first comparison counted the clay
  world's background, which the view-distance picture stores as 1.0, as head — fixed.)

*measured + web, 2026-10-30* — eyes, lashes and pore sources for the face test (rounds 19–27, `docs/dev/TASKS.md`):
- Scanned pores: three.js ships the Lee Perry-Smith head scan (`examples/models/gltf/LeePerrySmith/`: a 4096²
  displacement JPEG, a 1024² tangent normal, 1024² colour and specular; "Infinite, 3D Head Scan by Lee Perry-Smith is
  licensed under a Creative Commons Attribution 3.0 Unported License … always mention where you got them from"). Its
  high-passed displacement shows pores and fine lines (with 8×8 JPEG blocks — blurred σ 0.8 first); a 512² seamless
  cheek tile made (`.dev/facetest/pores_lps.png`) for the pore comparison.
- **The face's relief against HD Aaron, one factor at a time** (*measured, 2026-11-07*, `../gate/2026-11-07/report.md`;
  `tools/gate/measure.py` bands in mm, `tools/gate/factors.py`): on the cheek in EEVEE the pore tile makes the pore band
  (off: 1.49 -> 0.53) and a quarter of the folds, the microrelief the micro band (off: 0.48 -> 0.17), the scans' own
  mid-scale relief only ~9% of the folds, the colour ~20% of the folds and ~40% of the form. Microrelief acts as
  roughness on the larger bands (the forehead's x5: off, its pore and fold bands rise 20-30%); at x3 on the cheek it
  reads as regular crackle-glaze cells. Pores x1.15 and microrelief x1.35 on every head region bring the cheek within
  Aaron's bands (micro 0.93, pores 0.92, form 0.90) with the forehead equal; the cheek's folds stay below (0.76). Ten24's
  8K maps resolve ~4.4-4.6 texels / mm - too coarse for real pores (0.1-0.25 mm): the "pore tile" carries 1-2 mm bumps.
- **HD Aaron's skin per engine** (*file read, 2026-11-07*, local test): CC Blender Tools' Cycles build against its
  EEVEE build - Normal Strength 1.25 / 1.0, Micro Normal Strength 0.396 / 0.317, Roughness Power 0.75 / 0.56,
  Subsurface Scale 1.0 / 1.43. His detail reads ~1.6x stronger in Cycles; ours the same in both engines.

### 14.10 · Skin shading: scattering, specular, roughness, the tone model

- **Skin lightness by melanin** (`core/skin_optics.py`, eumelanin 0.6, blood 0.016; CIE L* of the albedo):
  - melanin 0.003 gives L* 75.6, 0.01 gives 69.0, 0.03 gives 54.7;
  - melanin 0.06 gives 41.0, 0.1 gives 30.8, 0.13 gives 26.3;
  - melanin 0.25 gives 17.6, 0.5 gives 10.9.

  The library's eight tones solve L* 74 down to 25 in steps of 7: melanin 0.00457, 0.01239, 0.02164, 0.03288,
  0.04705, 0.06597, 0.09366, 0.14102. *Computed, 2026-11-04.*
- **MetaHuman's skin materials, read from the installed plugin** (Unreal 5.8, `Engine/Plugins/MetaHuman/
  MetaHumanCharacter/Content/Lookdev_UHM/Skin/Materials/`, 2026-11-04, names read from the `.uasset` files; nothing
  copied): presets use `MI_skin_unified_MH_preset_Baked` on parent `M_skin_unified` with region masks
  `T_region_face_A-D` / `T_region_body_A-D` (hundreds of per-region basecolor / normal / fuzz parameters, animated
  wrinkle maps cm1-3 / wm1-3, "a fake peachfuzz effect adjustable through regions"); `M_skin_unified_baked` takes
  plain baked inputs - `Basecolor Baked`, `Normal Baked`, `SRMF Baked` (specular / roughness / metal / fuzz packed),
  `Scatter Baked` - plus `Micro Skin Details` (tiling micro normal and cavity, `T_SkinMicro3_N` / `_CAV`) with
  `Micro MaskA-D` strengths; subsurface profile `SSP_skin_unified`. For the gate: our maps on the baked variant.

*web, 2026-10-29* — re-checked for the user's "is there another better body … i feel you ddint reasearch well" and
"we need to create non human body as well like creatures just like cc5 allows" (Opus re-check of the review):
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

*agent, 2026-10-30* — what makes rendered skin read as a photo: relief, pores, shading, light, upscaling, eyes (notes,
ranked by quality, training buckets, apps, every search logged:
[`../plans/2026-10-30-research-skin-detail-shading.md`](../plans/2026-10-30-research-skin-detail-shading.md); facts to
re-check before the rec list; nothing run on skin here):
- Why ours looks waxy: `modules/skin/material.py` has one roughness (≈0.59) everywhere — no cavity map, no second
  specular lobe, no sheen; `modules/skin/detail.py` turns brightness into bump, which no professional pipeline does —
  they take the light out of the colour first, and pores come from scanned or generated height.
- **Blender 5.2's Random Walk radius** (*source read*, R1 Q7): from 5.2 plain Random Walk reads Subsurface Radius as the
  mean free path (1/σt) - the same value scatters 4π ≈ 12.6x farther than in "Legacy" mode; Random Walk (Skin) is
  unchanged (its radius the diffuse mean free path 1/σtr - our skin's, `skin_optics.py`). Our sclera, teeth, gums and
  tongue use plain Random Walk (`head/part_materials.py`) - their radii to re-check.
- **Weyrich et al. 2006** (*figure read*, R1 Q7: values read off Figure 15's vector paths - no table published): Torrance-
  Sparrow m / ρs - nose 0.234 / 0.304, cheeks 0.271 / 0.234, forehead 0.270 / 0.272, chin 0.289 / 0.228, lips 0.285 /
  0.289; measured diffuse mean free path 1.82 / 1.02 / 0.65 mm (R / G / B) - a target for our radius.
- **HD Aaron's cavity map does not follow his normal map** (*measured, 2026-11-07*, local test, scratchpad
  `aaron_cavity_fit.py`): `Std_Skin_Head_Cavitymap.jpg` (2048², mean 0.83) against the Frankot-Chellappa height of his
  `Std_Skin_Head_NBMap.jpg`, high-passed at 2-32 px: correlation <= 0.15 with either green convention. His cavity is
  not derived from that normal map alone (CC5 likely bakes it from the HD sculpt). So "cavity from our relief" can't be
  calibrated to his map this way; whether a cavity map is needed at all is left to the face proof's highlight measure.

### 14.11 · Body skin and fitting a scan

- **Anny (NAVER), read 2026-11-05** (github.com/naver/anny README [page], the user's link): "a free, open-source, differentiable human body mesh model" in PyTorch, infants to elders, "based on the tremendous work of the MakeHuman community"; licences: code Apache-2.0, `data/mpfb2` and `data/faceunits01` CC0 1.0, `data/soma` Apache-2.0, `smplx` non-commercial; topologies `anny` (default, triangulated, unattached vertices removed), `anny-quads`, `anny-full`, **`makehuman` ("unedited quad MakeHuman mesh")**, `smplx`, `smpl`, `soma`; rig 104 bones by default, 163 with `rig="makehuman"`; phenotype parameters in [0, 1], local changes in [-1, 1], facial actions from MakeHuman's Face Units (CC0). The README names no scan / keypoint / image fitting and doesn't say how ages are calibrated. Use for us: a differentiable copy of our base (if `makehuman` matches hm08's vertex order - to check) to fit our body's shape and pose to any scan by gradient descent (the Artec body fit that failed rigidly); the SOMA bridge for MHR shapes and SOMA-X correctives.
- **Limbs from a bare-body scan - fitting our body's pose** (*measured, 2026-11-06*, `tools/body_scan.py hsr0042`,
  HSRD-100's HSR0042-Body-045: bare but for trunks and cap, barefoot, near A-pose, 500k vertices, a floor sheet under
  the feet): our default A-pose bends the forearm 19 cm forward (elbow y -0.016 to wrist y -0.207) where the scan's
  arm hangs straight; a turn at the shoulder alone left the arms 8 cm off; a joint-by-joint two-angle search (each
  segment weighed the same - the hand's 1,577 vertices had outweighed the upper arm's 172; each joint's swing limited -
  the floor sheet had drawn the feet 73 deg round) then Amberg's non-rigid ICP: hands 3 / 8 mm (p50 / p90), forearms
  5-6 / 12-17, feet 9-10 / 17-19, upper arms 13-16 / 39-42, thighs 9-12 / 35-56, shins 14-15 / 30. The bake takes the
  scan's detail only where the wrapped surface lies within 6-12 mm (the fit's gap baked per tile). **Then Anny**
  (`pip install anny` 0.6.2 into venv-rdf, Apache-2.0 code, CC0 MakeHuman data): `Anny(rig="makehuman",
  topology="makehuman")` is the unedited quad mesh - 19,158 vertices, 13,742 quads, hm08's order (head within 6 mm
  index for index after a rigid fit; its default `anny` topology is the triangulated, trimmed one - not used); 163
  bones; phenotype gender, age, muscle, weight, height, proportions. Its README names no scan fitting: ours by gradient
  descent (bones' turns, the phenotype, a placement; a robust two-way nearest-point loss, 400 Adam steps, GPU) then
  the wrap: upper arms 3 / 7-8 mm, forearms 2-3 / 7-8, hands 2-3 / 6-8, thighs 3-4 / 9, shins 6-8 / 20-22, feet 5 / 13-16
  - every segment better. (The fit ended at gender 0.08 - male, right for this man: Anny's gender runs 0 male, 1 female (`anny/models/model_data.py` `gender=["male", "female"]`, anchors 0..1 in `phenotype.py`), the reverse of MakeHuman's 1 = male; `fit_anny` starts it at logit 4.0 commented "a man" (`tools/body_scan.py` L234) - 0.98, female in Anny - and its loss has no phenotype term, so that is an inverted start value, not a prior (was: "a shape-space quirk" until 2026-11-07); only the surface matters
  here.) Anny is a fitting tool in the scan pipeline only: the shipped mesh stays hm08 + base v2.
  Queries (2026-11-06, after the user asked whether Anny was researched against MakeHuman): "best way to fit a
  parametric human body model to a 3D body scan 2026" - older SCAPE / SMPL pipelines (joint-anchored fitting,
  BODYFITR, learned registration to SMPL+D), no 2026 consensus [snippets]; "Anny body model NAVER fit to 3D scan
  accuracy compared SMPL-X MHR" - the Anny paper (arXiv 2511.03589) via summaries: ~2.4 mm mean point-to-mesh error on
  adult scans (3DBodyTex), 2.0 vs SMPL-X 3.2 mm on children's, SMPL-X better on high-BMI skin folds, no MHR comparison
  [snippets - to read at the source before a plan rests on them]; "how do studios wrap a 3D scan to a base mesh
  topology R3DS Wrap alternative open source" - R3DS Wrap, Wrap for Blender ($49), TopoWrap: corresponding points,
  then a non-rigid fit, then clean-up; no open tool found [snippets]. Verdict: Anny + non-rigid ICP is the open form
  of the studio method on our own topology; MHR via SOMA-X (Apache-2.0) is the one to try if heavy bodies' folds
  come out wrong.
- **Body relief and muscle definition** (*measured + web, 2026-11-05*, proof step 2, `.dev/gate/parts/proof_body/`):
  MakeHuman's muscle macro (our Muscular man, 0.9) gives bulk, not definition - no abs or separation beside HD Aaron's
  torso; the same horizontal chest seam and arm bands show on Average and Muscular man (a texture-tile defect, not
  diagnosed yet). Bare torsos we hold: of HSRD-100's 13 downloaded poses only HSR0042-Body-045 (swim trunks; an
  average-build older man) - the rest wear shirts, dresses, hoodies (their `pose_meta.json`); the plan's "HSRD-100
  bodies ... mostly bare" was wrong. deep3dstudio's "Athletic African man walking 223" (CC BY, 8K tangent normal map)
  wears a tank top - bare arms show real definition; Ten24's sample wears a sweater. Web (queries, standard mode): "best
  way to add realistic muscle definition to a 3D character body skin normal map 2026" - listings and texture packs:
  the industry way is sculpted detail baked to normal + cavity maps (MetaHuman custom bodies, VRChat muscle packs);
  "free 3D scan shirtless male body full body photogrammetry download" - Ten24 (clothed), 3D Scan Store (paid; its
  terms bar character makers - licences-redo file); "textured 3D human body scan dataset minimal clothing underwear
  high resolution" - 3D.sk underwear scans (RenderHub listing: no commercial use), 3DBodyTex (close-fitting clothing,
  terms unread), CAPE / BUFF (textured raw scans on request, terms unread); "sketchfab shirtless man full body scan
  downloadable CC attribution" - Scanlab "human man scan *mbody" and "cdkc/cdbc a pose reference male scan" (licences
  and clothing unread), Heges app scan (CC BY, raw STL); "is there anything better than MakeHuman for realistic body
  shape and muscle detail open source 2026" - aggregator pages only (MakeHuman + sculpting; Ara 3D Gen, MIT, unread).
  **Triplegangers' free samples** (the user's link, triplegangers.com/blog/technology/free-scan-samples, read in Chrome
  2026-11-05 [page]): a face, a full body and a hand; the body an athletic man in underwear, BACS pose, mesh with clear
  pectoral and abdominal definition [seen]; "All free samples below are licensed under a Creative Commons
  Attribution-NonCommercial-NoDerivatives 4.0 International License" ... "You may not use the material for commercial
  purposes. If you remix, transform, or build upon the material, you may not distribute the modified material";
  download after registering (Google Drive, .7z). LOCAL TEST only - never shipped, nothing derived from it ships.
  **Artec 3D "Body scan"** (the user's link, artec3d.com/3d-models/body-scan, read in Chrome 2026-11-05 [page]): a
  young athletic man in shorts, bare torso, arms raised in a muscle flex (scanned with Artec Leo, 10 min, processed in
  Artec Studio) [seen]; its Free download tab: "Under Creative Commons license v4, attribution to Artec 3D and a link
  back to our website is all you need to use this 3D model for free" - the link goes to
  creativecommons.org/licenses/by/4.0 (CC BY 4.0); credit "Body scan by Artec 3D"; one OBJ archive, 57.73 MB, a direct
  CDN link (no account). SHIP with credit - the first bare athletic torso we can ship from. Downloaded 2026-11-05
  (`.dev/downloads/artec_body_scan/`); its own `license.txt` says CC BY 3.0 Unported ("This 3D model by Artec Group inc.
  ... is licensed under the Creative Commons Attribution 3.0 Unported License") - the file's grant; the page says v4.
  **Digital Reality Lab samples** (the user's link, digitalrealitylab.com/sample-model, 2026-11-05 [page]): full body
  A-pose (3.5 GB raw / 480 MB rig-ready, 16K), heads raw / clean / PBR (separate eyes, 16K PBR), facial expressions
  (1.6 GB), hand, clothing, a rigged female; "The sample models are free for personal and commercial use with credit
  mentioned on any social media" [page, found in Chrome]; "we do not allow resale or free distribution on other
  websites" [WebFetch summary - unread in the page itself]; /legal and /faq hold no licence text. A form (name, email,
  company, job, use) mails the link - the user's to fill. Shipping derived maps: UNREAD (whether a baked map in our
  repo is "free distribution on other websites") - ask them in writing before anything ships.
  **3D.sk free samples** (the user's link, static.3d.sk/photos/freeSample, read in Chrome 2026-11-05 [page]): Dale
  Base Body Scan (a bodybuilder, A-pose, 57.89 MB), Adelle Sabelle Standing Clean Body Scan, Alison Clean A Pose Scan
  (clothed), Bshara Henry Head Scan, Vinna Reed head premade texture, Lenny groom scan, photo sets (Darren in underwear,
  poses, expressions). Their Content Commercial License Agreement (3d.sk/page/commercialterms [page]): "you may not use
  the Content in products for resale, license or other distribution, unless the original Content has been
  fundamentally modified ... and where the primary value ... is not recognizable as the Content nor is the Content
  capable of being downloaded, extracted or accessed by a third party as a stand-alone file" - a relief map in our
  open repo is a stand-alone file: LOCAL TEST only. The download link (`/photos/download?id=969125` for Dale) is
  bot-protected (curl: 403) and a browser click saves to Chrome's download folder - the user downloads it. 3D.sk's ArtStation post "FREE 3D Scan | Retopo Hands & Premade Head Textures" (the user's link [page]): its only free item is Adelle Sabelle's cleaned raw body scan (the same sample); the hands and head textures it shows are paid products.
  **CGTrader free characters** (the user's 16 links, 2026-11-05; four read in Chrome [page]): "Matt" and "Amber Free
  High-Poly" (Martinthedark-, rigged game characters; FBX / BLEND / Unity / Unreal), "Realistic Male Full Body Sculpt"
  (daniartist, 171 reviews), "Head Parts Anatomy" (Avanar) - each "License (no AI) ... Free for personal and commercial
  use"; CGTrader's terms (§21A, read 2026-11-04, `../plans/2026-11-04-research-licences-redo.md`): "strictly limited to
  Incorporated Product", in software "prevent the end user from gaining access to the Product" - LOCAL REFERENCE only,
  never shipped; downloads need the user's CGTrader login. Most useful as references: the full-body sculpt (body
  definition), Head Parts Anatomy (lid and mouth anatomy); the stylised or game ones (knight, centaur, bunny girl, monkey
  king, cool girl, Asian girl PBR) add nothing for realism (titles; pages unread).
- **Anny ships a fitter for registered meshes and MPFB2's rigs** (*code read, 2026-11-06*, `.dev/venv-rdf` anny
  0.6.2): `anny_inverter.py` L35-44 `AnnyInverter` - "Estimate Anny parameters fitting a target mesh", pose "via
  joint-wise rigid registration", phenotype "via finite-difference Jacobian optimization", input `[batch_size, V, 3]`
  (vertices already in Anny's topology - i.e. after our wrap); `keypoints.py` (keypoint regressors);
  `models/model_data.py` L223-231 its rigs are MPFB2's files - `"makehuman": ("rig.default.json",
  "weights.default.json")` (163 bones), `"game_engine": ("rig.game_engine.json", "weights.game_engine.json")` (53
  bones, root `Root`) - joints by MPFB2's `CUBE` strategy (`models/full_model.py` L243-255). So `Anny(rig="game_engine",
  topology="makehuman")` is our mesh with the MPFB2 base of the spec's skeleton (`character-data-model.md` §2: "placed
  from the joint cubes (MPFB2's `CUBE` strategy)", weights "from MPFB2's `weights.game_engine.json`"). Earlier line
  L352 ("Its README names no scan fitting") is true of the README only. The package also holds `anthropometry.py`,
  `shape_distribution.py`, `face_segmentation.py` (not read).
- **The hand donor was on our disk** (*seen, 2026-11-06*; `.dev/audit/2026-11-06/research/R1.md` Q3, checked by me on a
  crop of `.dev/downloads/ten24_sample/x/OBJ Package/Normal Maps/Level_01_Normal.PSD`, 8192² - not 16K - x 5100-7000,
  y 200-2900): Ten24's sample has bare hands; its normal map shows the extensor tendons fanning to the knuckles, veins on
  the back of the hand, knuckle and finger creases, palm creases and wrist skin lines (the forearm's colour carries hair;
  the cuff is a sweater). Licence: "Feel free to use this scan as you wish for both commercial and personal projects. All
  we ask is that you provide us with a credit wherever it's used" (the page saved 2026-11-04). Its feet are in shoes. So
  run 11's flat hands have a donor in hand: our hand fitted to Ten24's mesh and its relief baked onto our hand tiles.
  Feet: Thunk3D's "Leg-foot" (Sketchfab, "CC Attribution" [API], 2.97M faces, geometry only) is the one detailed bare
  foot found; more hands: Arkify "Pencil Hand Pack" (3 female + 3 male, Artec Space Spider, CC Attribution [API]),
  Thunk3D hands - their detail unseen until downloaded.
- **HSR0042 is a 24-year-old, 179 cm, 112 kg African man** (*page read, 2026-11-06*, HSRD-100's
  `manifest/persons.jsonl`: `{"person_id": "HSR0042", "age": "24", "sex": "Male", "ethnicity": "African", "height_cm":
  "179", "weight": "112", ...}`) - L371-372 above ("an average-build older man") is wrong; L355's "a heavy man" is right.
  HSR0040 (Scan man A's and B's main colour scan): 50, Caucasian, 180 cm, 92 kg.
- **Bare bodies of women, heavier, older, darker** (*page read, R1 Q4*): none found fully bare under terms that let us
  ship. On disk or in HSRD-100 (CC BY): poses with bare arms or legs - women 22, 23, 41, 60; men 50 and 62 (~90 kg)
  (HSR0015-069/-070, HSR0112-078, HSR0040-074, HSR0023-071, HSR0042-043 - not downloaded); `d3d_bodysuit_woman` (CC BY, on
  disk): a dark-skinned, heavier woman with bare arms, legs and feet. Renderbot (a one-year site licence), store
  "Standard" licences, editorial-only and NC sources fail; Sketchfab's Store has closed.
- **Anny paper, v3** (*page read*, arXiv 2511.03589): no scan-fitting method is described; adults fit at 2.5 mm against
  SMPL-X 1.9 and ATLAS 1.8 (head and hands excluded); children 2.0 vs SMPL-X 3.2 on three scans; "SMPL-X better captures
  fine skin-fold details of high-BMI bodies compared with Anny"; no MHR comparison. L360's 2.4 mm is v1's figure.
- **Ten24's hands carried in texture space** (*measured, 2026-11-07*, `tools/body_scan.py texture ten24`): baking its
  Level_01 normal map through the 100k decimated mesh gave blotches (the map is relative to the coarse level-1 mesh: the
  medium shape counts twice). Taken instead in the map's own texture space - its tilt high-passed at 8 mm inside each
  UV island, its hair strands (found in its colour) filled, anti-aliased to our 2.7 texels / mm, carried through the
  fit's nearest point and turned from its tangent frame into ours - it gives palm creases, extensor tendons, knuckle and
  finger creases. Ten24's hands sit at x 5160-7947, y 256-4207 of its 8K maps, ~4.4 texels / mm. Two traps: Blender's OBJ
  importer keeps a Y-up file's axis turn in the object, not the mesh; an ffmpeg crop box past the image's edge comes
  back shifted (here ~900 texels). On the gate's back-of-hand window: form 0.71 -> 0.95 and ridges 0.29 -> 0.47 of
  Aaron's in EEVEE (Cycles 0.53 -> 0.70, 0.21 -> 0.35) - still below his sculpted veins.

### 14.12 · Eyes

- **EEVEE's eye white and the lids' shadow** (Blender 5.3, a close eye, one 120 W area light 0.6 m wide, measured
  2026-11-04):
  - The lid stands about a millimetre off the eyeball. The light's `shadow_maximum_resolution` defaults to 1 mm.
  - At 0.1 mm without `use_shadow_jitter` the white stays flat. Jittered, the upper lid's shadow shows.
  - Render time was the same at every limit: 0.56 s for a close eye at 512 px and 64 samples, 0.44 s for a full body
    at 1280 x 720.
  - In 5.3 the setting is `shadow_maximum_resolution`; `shadow_resolution_scale` no longer exists.
  - The viewport jitters only with `scene.eevee.use_shadow_jitter_viewport`.
- **The eye part by part against HD Aaron** (*measured, 2026-11-05*, proof step 4, `.dev/gate/parts/proof_eyes/`,
  RESUME (4b)): a cut-out iris photo, unwrapped to polar coordinates and sampled on our eye's linear iris UVs (pupil
  edge to 4% past the limbus), measures equal to his iris (L* 24.6 / C 14.8 vs 27.2 / 11.3) with more detail; the
  iris surface itself must not be specular (0.5 at roughness 0.4 laid a grey haze over the pupil - the cornea shell
  carries the gloss, the real iris sits in index-matched fluid). Source on disk: `Green_iris.jpg` (Wikimedia Commons,
  Lizapopova143, 2019-07-15, 5,315 x 3,838) - its file page [page, read 2026-11-05]: "This file is licensed under the
  Creative Commons Attribution 4.0 International license." MakeHuman's lid has no margin geometry: its lower lid's
  edge stands up to 3.3 mm off the eyeball (a dark crevice in the render); moving that one vertex ring onto the eyeball
  leaves a 4-8 px band against his ~36 px. ICT's tearline strip shaded as wet pink tissue gives the band on the
  Average man (32 px, the same colour) but on four other library characters it outlines the whole opening, upper lid
  included - a drawn pink ring (his upper margin hides under the lashes).
- **Iris colour values** (searched 2026-11-04, for the eye colour presets). Queries and what they returned:
  1. "measured iris colour CIELAB values blue green hazel brown eyes" - Edwards et al. 2012 (Am J Phys Anthropol,
     CIELAB from a 256 x 256 patch at the iris' 9:00 meridian), Herrera Ramírez et al. 2009 (UPC, brown / blue / green
     groups by camera), a Korean study, a 1984 Psychonomic paper - methods; no numbers on the pages reached.
  2. "realistic iris colors for 3D eye shader presets blue green hazel" - product pages (Daz Macro Eyes presets, an
     Unreal eye pack, Blender's Eye Designer: 12 colour sets) without values; a paper on blue as stroma scattering and
     hazel as melanin over it.
  3. "Edwards 2012 'quantitative measures of iris color' CIELAB ..." - the same paper's design; PMC6456006 (a South
     Asian GWAS, 2019) reports only GWAS statistics, its camera set-up (D55, f/19, ISO 200).
  4. "'Digital quantification of human eye color' Liu 2010 ..." - PLoS Genetics 2010: hue and saturation from photos,
     the categories overlapping; values not reached.
  5. "'Iris pigmentation as a quantitative trait' Edwards 2016 ..." and "iris color physics melanin stroma Rayleigh
     scattering model ..." - the 2016 paper and qualitative physics only.
  A gap in the search, not "none exist": the papers hold the numbers; their full texts weren't reached (an ARRO copy
  failed its certificate). MPFB2's own eye default is a saturated blue (0.18, 0.49, 0.91; `eye_settings.default.json`).
- **EEVEE and the occlusion film** (2026-11-04): ICT's sheet sits a median 0.57 mm off our eyeball (16 of 152 vertices
  up to 0.2 mm under it, by the cornea); EEVEE draws it (seen as flat red) as a blended surface, but at the face test's
  strengths (tuned in Cycles, where the lids cast real shadows) its darkening barely shows.

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

*agent, 2026-10-30* — hair, eyes and teeth (notes, ranked by quality, training buckets, apps, every search logged:
[`../plans/2026-10-30-research-hair-eyes-teeth.md`](../plans/2026-10-30-research-hair-eyes-teeth.md); facts to re-check
before the rec list; measured in Blender 5.3 and read in our code):
- Eyes: a layered stack with the iris ~3.6 mm behind the cornea (Navarro's optics); a procedural iris, or an SDXL LoRA
  (kohya: 8 GB at the edge). Teeth: per-part shaders on our GNM teeth.

*agent, 2026-10-30* — what makes rendered skin read as a photo: relief, pores, shading, light, upscaling, eyes (notes,
ranked by quality, training buckets, apps, every search logged:
[`../plans/2026-10-30-research-skin-detail-shading.md`](../plans/2026-10-30-research-skin-detail-shading.md); facts to
re-check before the rec list; nothing run on skin here):
- Eyes: ICT-FaceKit (MIT) ships eye occlusion, tearline and eye-corner meshes; the cornea in Cycles by MNEE shadow
  caustics or a shadow-ray trick.

*web + measured, 2026-10-31* - the eye's occlusion and tear line, shaded and fitted (`../plans/2026-10-31-audit-eyes.md`,
27 searches logged; CC5's pages read one by one):
- CC5's Eye Occlusion is set, not computed: a UV-space mask with its own range, contrast and edge fade for the upper
  lid, lower lid, inner and outer corner (Shadow 1, default strength 0.312), a second colour layer (Shadow 2), a Blur
  ("simulating the shadows from the eyelids"; "Inner Blur Contrast" places "the dark crevice between the eyeball and the
  tear duct") and a Vertex Offset ("to snuggly fit the eyeballs"; Depth Offset 0.500). Its Tear Line: depth offset
  0.050, detail normal tiling, edge fadeout, roughness 0.25-0.45, opacity 0.04-0.2 (the manual's examples).
- UE 4.27 Photorealistic Character: a translucent sheet over the eye, `MI_Eye_Occlusion_Bust`, its border fitted to the
  open lid, UVs filling 0-1; the Eye shading model's Ambient Occlusion input is the soft lid / caruncle shadow.
  MetaHuman's DNA Calibration scripts (Epic's licence, study only): `eyeshell`, `eyeEdge`, `cartilage` (inner corner),
  `saliva` and `eyelashesShadow` meshes, each skinned to the face joints.
- Film: Weta (Gollum) added "an extra amount of shadowing from the eyelids" and the meniscus, driven by curves on the
  lid edges; Sony US 9336622: the band between pupil and upper lid at 40-60% of the eye's shading, "a combination of
  shadows from the brow, eyelashes, and upper lid"; Sony US 9269185: a procedural meniscus ribbon from the socket loop,
  thicker at the bottom. Unity's The Heretic: an anisotropic spherical Gaussian fitted to four lid markers. The real
  lower tear meniscus is ~0.20 +/- 0.05 mm high.
- ICT-FaceKit (MIT) per eye: eye occlusion 152 v, lacrimal fluid 204 v, eye blend 24 v, with UVs, no shader or texture,
  no caruncle mesh. Measured: the shells live inside every expression shape (a blink moves the occlusion up to 9.6 mm,
  the eyeball not at all); the occlusion sits a median 0.5 mm off its eyeball (fitted sphere 15.8 mm) and covers the
  27 x 11 mm opening. CC5's shells carry their own Eye_Blink / Eye_Wide / Eye_Squint shapes (Reallusion staff).
- Blender: Shrinkwrap "Nearest Surface Point" with an offset "Outside Surface" keeps a layer off another surface; the
  manual: the AO node gives no valid result on a shadow-caustics caster or receiver - AO and MNEE can't be combined.
- Not found (a search gap): an open occlusion or tearline shader; a CC0 sclera texture with veins; an open caruncle.

*measured, 2026-10-31* - eye openings, ICT's tear strip and flow between the paintings (face test rounds 50-51):
- Our head's skin is watertight around the eyes (no boundary edges among its 13,380 vertices' polygons): the lids fold
  into the socket, so "skin within a few mm of the eyeball" also finds the socket lining and the lids' backs. The
  opening is what shows: rays out from 3 mm under the eyeball's surface, skin within 8 mm outside it, on a 1 x 0.5 deg
  grid, the shown patch around the gaze. Ours (eyeball radius 14.8 mm by a sphere fit; the iris disc 23.2 deg in
  radius, its middle at az +-4.7, el -6.5 deg): at the iris -30 .. -2 deg before the lid key; the lid's edge stands
  1.0-1.5 mm off the eyeball. ICT-FaceKit's left eye (radius 15.2 mm): az -24 .. 44 deg, lids +13 / -22 deg at the
  middle.
- ICT-FaceKit's lacrimal fluid (left: polygons 24692-24854, 204 vertices, all quads): a ring with two rims - 36
  vertices on the eyeball at the lid margins (a median 0.3 mm off it, -0.2..1.4), 46 under the lids (1.6 mm, 0.9..3.3)
  - about 3-4 rows across; its UVs sit in tile u 4-5, both u and v running along the eye (corr with azimuth -0.90 and
  0.87). Its inner rim lies 1.5-2.5 deg inside ICT's lid edge, so 1-2.5 deg of it shows below the upper lid and above
  the lower.

*measured + web, 2026-10-30* — eyes, lashes and pore sources for the face test (rounds 19–27, `docs/dev/TASKS.md`):
- MPFB2's procedural eye (`src/mpfb/data/node_trees/procedural_eyes.json` at 6ff1eb35, CC0 data; 14 node groups,
  "EnhancedEye") built by `tools/face_test/mpfb_nodes.py` works on GNM's eye: one eye per UV map centred at (0.5, 0.5),
  eyeball UV radius 0.46, iris 0.40 of it (measured: iris UVs 0.315–0.685, pupil 0.45–0.55). Its distance node sums two
  eyes' centres — the second must be moved off the map. Trials: a refracting or Fresnel-shell cornea greyed the eye;
  a glossy iris and the shader's 0.4 clear coat mirrored the grey studio; the paintings' eye colours on our lids'
  undersides read as a shiny strip.
- **GNM's eye part as stored** (*measured, 2026-11-06*, `extension/juststage/data/generated/gnm/parts/eyeLeft.obj`,
  hm08's decimetre units): sclera sphere radius 0.141 (14.1 mm), the cornea's apex 0.0299 in front of the iris's mean
  plane (2.99 mm) and 0.0326 in front of the pupil's - before the MHCLO fit scales the part to our head; the fitted
  eye's depth is unmeasured. The `eye_exteriors` shell covers the whole ball (to 178 deg from the axis), so the
  "cornea" material also glosses the white.
- **Lower tear meniscus** (*page read*, R3): ages 19-31 AS-OCT 0.21 ± 0.06, Keratograph 0.20 ± 0.05 mm (PMC11809819, CC
  BY); ages 10-78: 0.34 ± 0.07 mm (0.11-0.61), ~0.002 mm a year (0.29 at 10-20 to 0.40 at 61-80), no sex difference
  (Frontiers Med 2022, CC BY).
- **Iris colour data** (*page read*, R3 Q1): Edwards' Dryad data (doi:10.5061/dryad.0kt87, CC0) holds iris surface
  features only, no colour - drop it from the download list; Edwards 2012's tables paywalled; the only open numbers
  reached: Korean dark-brown irises L* ~22, a* ~22, b* ~29 (CC BY-NC). No open per-category table found.

### 14.13 · Lids, lashes, brows, facial and body hair

- **MakeHuman's pack lashes** (`basic_lashes_upper`, attached to our Average woman): 99 strands for both eyes, radius
  0.05 mm (median; max 0.1 mm), standing 8-9 mm in front of the eyes. At 256 px over 7 cm (0.28 mm a pixel) EEVEE's
  true-width strips are a third of a pixel and vanish; at 1024 px a few strands show at the outer corner.
  *Measured, 2026-11-04.*

*web + measured, 2026-10-31* - the face's neutral: lips and lids (`../plans/2026-10-31-audit-face-edits.md`, 18 searches,
every one logged; key claims page-read):
- Lead: MakeHuman's packs page lists "Eyebrows 01 - A set of high-res eyebrows by Mindfront" under CC0 mesh assets (not in
  our local pack).

*measured, 2026-10-31* - eye openings, ICT's tear strip and flow between the paintings (face test rounds 50-51):
- Eyelash angles, measured (searched 2026-10-31: "human eyelash curvature angle upper lash lift angle measurement
  study" - a Korean cilia-angle table, the SNU Asian/Caucasian curl-up and lift-up study (Na et al., BJD 2006: Asian
  lashes lower lift-up and curl-up angles, fewer, thicker; numbers not in the snippets, the page didn't load), a
  cadaver root angle 75 +/- 11 deg to the skin; "Asian Caucasian eyelash lift-up angle curl-up angle degrees lateral
  photograph"; "upper eyelash angle to horizontal degrees Asian downward lashes eyelid margin inclination"; "how to
  groom realistic eyelashes 3D strands direction curl tips Blender MetaHuman" - only Fab groom listings: 182-270
  curves, ~19 points each). Page read, oatext.com "A study of normal eyelashes in Japanese individuals" (50 adults,
  lateral photographs, primary gaze; angle between the lash root and the vertical): upper 61.4 +/- 13.7 deg men,
  71.8 +/- 13.5 women; lower 90.0 +/- 10.1 / 99.8 +/- 10.8; upper length 7.33 / 7.47 mm, lower 4.98 / 5.56; upper
  lashes curly in 40% of men, 76% of women, the lower all curly. Page read, Korea University "Changes in the horizontal
  angular direction of lower eyelashes with age in Korean patients" (frontal photographs, tangential to the line
  through the canthi): adults medial 137.1 +/- 13.8, central 71.8 +/- 14.5, lateral 25.3 +/- 9.3 deg. No frontal
  measurement of the upper lid's fan was found - a gap in these searches.
- The study's angle reference, re-read 2026-11-02 (search: "\"A study of normal eyelashes in Japanese individuals\"
  oatext angle vertical"; the page fetched): "The angle was defined as the angle between the root of the eyelashes and
  the vertical line shown in Figure 2" - the text doesn't say which way that vertical points (the figure wasn't
  readable). Its discussion: the lower lashes "grow in the upward direction against gravity" - which fits only a
  vertical pointing down (lower 90 deg straight ahead, women's 100 above it); so men's upper lashes leave the lid ~29
  deg below straight ahead (women's ~18). The close 30-degree painting shows them that way (hanging over the eyeball).

*measured + web, 2026-10-30* — eyes, lashes and pore sources for the face test (rounds 19–27, `docs/dev/TASKS.md`):
- MPFB2's lash groom (hair-editor pack "basic_lashes_upper") on our GNM-shaped head: 99 strands, 3.7 mm, roots at the
  eye's middle height (z 1.616–1.623 against the eye centre 1.623) — they hang across the eye. GNM has no lash geometry.
  MakeHuman's system assets (`makehuman_system_assets_cc0.zip`, 280,737,770 bytes, sha256 b542127a8e25…; each asset file
  "explicitly released as CC0 in september 2020") carry lash cards `eyelashes01`–`04` (.obj + .mhclo to hm08 + RGBA
  .png) and brow cards; `eyelashes02` fitted by our `core/mhclo.fit`: 250 vertices, 184 cards, z 1.611–1.628, in front
  of the cornea — on the lids.
- MakeHuman's own material files for these cards (`eyelashes01.mhmat`, `eyebrow012.mhmat`, read 2026-10-31):
  "specularColor 0 0 0", "transparent True", "backfaceCull False", "castShadows False", "receiveShadows True", the
  card's PNG as `diffuseTexture` (its RGB near black; the hair is in its alpha). A Principled BSDF left at its default
  specular and casting shadows renders a brow card as a grey film (face test round 43). Brow sets' coverage (alpha >
  0.05 share of the 512² map): 006 0.040, 007 0.050, 011 0.078, 001 0.106 … 012 0.161, 009 0.322.
- **Lid margin, measured** (*page read, 2026-11-06*; R3 Q2; the first re-read by me via Europe PMC's full text):
  "the LMT was defined as the distance from the posterior lash line to the MCJ at the center eyelid, directly above or
  below the center of the subject's pupil"; 56 normal adults: **upper 1.36 ± 0.25 mm, lower 1.0 ± 0.23 mm**, both rising
  with age (Ophthalmol Ther 2021, PMC8770731, CC BY-NC). Lower lid by OCT / Keratograph 0.90 ± 0.20 / 0.86 ± 0.16 mm
  (Wang et al., Graefes 2023, CC BY). The MCJ (line of Marx) "0.2-0.3 mm wide" (Knop et al. 2011). The whole margin
  "Nearly flat, 2 mm wide" [snippet]. Base v2 places the lash row - the margin's front edge (`hair/lashes.py` L132) - 2.6 mm off the eyeball (`tools/make_base_v2.py` LASH / MARGIN / RIM = 2.6 / 1.3 / 0.25): a whole margin of ~2.35 mm against the real whole margin's ~2 mm [snippet], ~1.2x; the LMT runs from the posterior lash line, a part of the margin, so it is no target for the front row's place
  (was: "above every measured value: a measured target for the lid band" until 2026-11-07).
- **Lashes** (*page read*, R3 Q3): the oatext study's Figure 2 seen - the vertical points down from the root, so upper
  lashes leave the lid ~29 deg (men) / 18 deg (women) below straight ahead (L2385 above stands; our code sweeps them up
  to match Aaron - a choice to state). Central density 12-15 upper lashes per 2 mm of lid. Shaft 77.8 x 63.9 µm across, elliptical (synchrotron CT; ~71 µm round) - our lashes' 0.08 mm is their radius (`hair/lashes.py` `UPPER["radius"]`, the Curves' `radius` attribute): 0.16 mm across, ~2x the real
  (was: "our 0.08 mm fits" until 2026-11-07). No frontal fan study found (again). Kerbiriou's data (InterDigital, 56
  people): access by e-mail, evaluation only, no commercial use, no redistribution - blocked. MetaHuman's "7" lash
  styles are its style list (None + six presets); its other controls are colour (melanin, redness, lightness,
  roughness, salt-and-pepper, dye) - rec 8's "7 style parameters" was wrong.
- **The lid margin's whole width - no source found; the measured spans are partial** (*page read, 2026-11-07*):
  Wang et al. (Graefes 2023, PMC10368556, CC BY 4.0): "the LLMT was defined as the distance from the posterior lash
  line to the anterior edge of the tear meniscus"; "it was difficult to measure the full thickness of lid margin
  including the mucosa"; normals 0.90 ± 0.20 mm (OCT) / 0.86 ± 0.16 (K5M). So the 1.0 / 1.36 mm above (posterior lash
  line -> MCJ) leave out the lash rows in front and the mucosa behind: the whole margin, lash row to eyeball, is wider.
  Searched: "eyelid margin width 2 mm anatomy anterior posterior lid border" (only a SlideShare outline gives "2mm in
  width" - unverified), Knop's lid-margin overview (erich-knop.squarespace.com, read: no dimensions), BCSC's eyelid
  page (ophthalmologyreview.org, read: none), "eyelid margin total thickness OCT normal subjects mm anterior lid margin
  to posterior lid margin" (partial spans only). A gap in the search, not proof none exists. So base v2's 2.6 mm is
  not shown too wide by these numbers (the plan's Q-BASE-5, 2026-11-06, read them as the whole margin - corrected).

### 14.14 · Scalp hair

- **Cycles' hair colour from melanin** (source read 2026-11-03: `intern/cycles/kernel/svm/closure.h`,
  `kernel/closure/bsdf_util.h` on GitHub's mirror): concentration m = −ln(max(1 − melanin, 0.0001)); eumelanin
  m·(1 − redness), pheomelanin m·redness; σ = eu·(0.506, 0.841, 1.653) + pheo·(0.343, 0.733, 1.924); a colour's σ is
  (ln colour / s(β))² with s(β) = ((((0.245β + 5.574)β − 10.73)β + 2.532)β − 0.215)β + 5.969 (β the radial roughness) -
  so the colour a melanin gives is exp(−√σ · s(β)), what EEVEE's Principled BSDF stand-in for Principled Hair needs.
- **Hair colour, EEVEE stand-in against Cycles** (`Hair to shoulder` on the Average woman, the three-quarter
  thumbnail view, 64 samples): the mean hair colour in sRGB for melanin / redness 0.5 / 0.25 was 87,63,46 in EEVEE
  against 101,71,51 in Cycles; for 0.65 / 0.2, 70,53,45 against 82,59,48; for 0.75 / 0.2, 61,49,44 against 71,54,47.
  EEVEE is ~10-15% darker with the same hue. Cycles turns 0.5 / 0.25 auburn on a sparse style (light through it).
  *Measured, 2026-11-04.*
- **Grooms between characters** (Blender 5.3's Deform Curves on Surface; measured 2026-11-04):
  - The node moves each curve rigidly from its root's triangle in the surface's rest position (the base mesh before
    shape keys) to the same UV point on the evaluated surface. A strand's points don't change the move, so it can be
    measured on a probe shape and inverted exactly.
  - Its turn isn't the plain triangle frame (first edge, normal): that frame missed by up to 1.9 mm at a lash tip.
  - With each character's base mesh lifted by its own `feet_on_ground` amount (0.817743 m at the default macros,
    0.820291 at height 1, 0.819702 for a tall muscular man), grooms landed off by the difference: MakeHuman's pack
    roots, median on the skin, were hedgehog 0.84 mm and pack lashes 1.88 mm on a tall character (0.07 / 0.31 on the
    default). With one lift for every base mesh: 0.08 / 0.28.
- **The live view's hair against the film's** (the library's "Hair to shoulder" on the Average woman, Standard view,
  measured 2026-11-04). First, a mask of what the hair changes (it took in the skin the hair shadows) showed Cycles
  1.17x EEVEE - misleading. Then the VISIBLE hair only (the hair as white emission, the rest held out): Cycles'
  Principled Hair (0.15, 0.087, 0.056) against EEVEE's stand-in (0.068, 0.05, 0.044), grey; Cycles rendering the
  stand-in's own BSDF just as dark (0.058, 0.043, 0.038) - so the gap is the stand-in's model, not EEVEE; EEVEE's
  ray tracing / Fast GI change little; the hair's self-shadow matters in both. The cause: the stand-in used Chiang's
  colour formula exp(-f(beta) sqrt(sigma)) as a plain surface colour - near-black for brown hair (0.016, 0.005,
  0.001), the strand's colour inside a multiple-scattering model, not a surface albedo. Fitted on a grid (melanin
  0.2-0.97 x redness 0.1-1; EEVEE's response linear in the colour, slope 1.62 everywhere): the matching colour is
  exp(-k sqrt(sigma)) with k ~3.75 (vs 5.89) within ~5%, near-black hair floored ~0.008. Built: the stand-in at k =
  0.637 f(beta) with that floor - under the stage's light EEVEE (0.154, 0.091, 0.055) against Cycles (0.15, 0.087,
  0.056). Under the image light alone EEVEE is still 2.3 / 1.8 / 1.4x darker: its ambient light on hair falls short of
  Cycles' scattering - open (the shading model, not the colour).

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

*agent, 2026-10-30* — hair, eyes and teeth (notes, ranked by quality, training buckets, apps, every search logged:
[`../plans/2026-10-30-research-hair-eyes-teeth.md`](../plans/2026-10-30-research-hair-eyes-teeth.md); facts to re-check
before the rec list; measured in Blender 5.3 and read in our code):
- Why ours looks fake: the hair defaults (melanin 0.8, redness 1.0) are Blender's own — by the manual's formula all red
  pigment, no brown-black — and every strand has the same value; Principled Hair BSDF is "Cycles Only" (EEVEE's default
  hair draws each strand ~1 px wide); scalp counts 10K–42K (MetaHuman's real-time level); each brow guide copied into a
  ~19-strand tuft (the clumps); lashes ~50 upper and 33 lower per eye at 5 points (real lids 90–160 and 75–80); flat
  iris, sclera and teeth; no occlusion, tearline or caruncle meshes.
- Image to strands: DiffLocks, Im2Haircut, TANGLED, Perm (MIT), HairStep — training we can't do, or non-commercial or
  unlicensed weights. Text to strands without training: Digital Salon (MIT; CLIP search over a captioned groom library,
  then live editing). Facial hair from multi-view capture: Wispy to Voluminous (training-free, no code yet).
- Training-free: Blender's hair node groups used properly, and DiffLocks' published Blender recipe (75 guide sets × 110
  random parameters) — a CC0 groom library of our own; hair cards by Unreal's generator or our own baker.
- Open: no measured melanin table per hair colour; VRAM unknown for the hair AI methods; no fix rendered.
- **Hair colour in Cycles** (*code read*; R3 Q6, the coefficients re-read by me in Blender 5.3's
  `intern/cycles/kernel/closure/bsdf_util.h` L430-431): eumelanin (0.506, 0.841, 1.653), pheomelanin (0.343, 0.733,
  1.924) - pbrt's (0.419, 0.697, 1.37) / (0.187, 0.4, 1.05) x 1.207 / x 1.833; the 0-1 input maps by
  `-log(1 - m)`. pbrt's *text*: eumelanin "roughly 8, 1.3, and 0.3" for black, brown, blonde (the "8, 2, 0.15" in our
  mixing-hair research are its figure's examples). In Cycles' Melanin input (redness 0): black 0.9987, **brown 0.659
  (we had 0.81), blonde 0.220 (we had 0.12)** [calc, re-done by me]. Measured single-fibre absorption (Bashkatov 2006)
  is ~50x below rendering values - not a default source.
- **Hair densities** (*page read*, R3 Q6-Q7): scalp terminal 223 / cm² (175-300; Barman 1965) - African 149, Asian 175,
  Caucasian 226, Hispanic 178 - these by ethnicity are Table 6 of Alsharif & AlGhamdi 2022 (CCID 15:2737, CC BY-NC 3.0, citing Birnbaum 2018 and Maymone 2021; R3 Q6), not Barman (was: credited to Barman 1965 with the 223 until 2026-11-07); Szabo's 980 counts all follicles. Beard shaft 125.6 ± 10.9 µm (Tolgyesi 1983); beard
  densities reached run to ~120 / cm² (ours 160). Forearm 39 ± 12 follicles / cm². Brow shaft 54 µm (men), 47 (women);
  no measured hairs-per-brow count found (a full transplanted brow ~200 follicles; ours 2,200 a brow). Strands2Cards'
  paper unread (over the fetch limit). Groom comparison: HairCS's silhouette IoU (coverage), tangent and depth images,
  volume Chamfer (clumping). MetaHuman binds brows by a Groom Binding through shared UVs (optional RBF); CC's brows and
  beards carry skin weights and follow the head's morphs.

### 14.15 · The live view against the film

- **Round 79 in EEVEE**: 10.7 s for one 1024² still on the 2070 Super, shader compile included; the maps carry over
  (pores, stubble, redness); every part's output is Target `ALL` with nothing on Thickness, the cornea has no raytraced
  refraction, `scene.eevee.use_raytracing` is off and the lashes draw as 1-px `STRAND` curves — the EEVEE tuning of
  RESEARCH skin (`../plans/2026-10-30-research-skin-detail-shading.md:349-358, 495-500`) and hair
  (`../plans/2026-10-30-research-hair-eyes-teeth.md:111-122`) was never built — *measured, 2026-11-03*.
- **EEVEE 5.3 can shade per light in nodes** (a research agent's finding 2026-11-04 - manual rst, PR #161429 merged
  2026-09-02, task #139341, PR #164595; verified on our 5.3 beta by listing the nodes, measured): `ShaderNodeLightAccumulation`
  (inputs LightIndex, Diffuse Light / Color, Glossy Light / Color, Transmission Light / Color, Weight - its input tree
  evaluated once per scene light and summed), `ShaderNodeLightEvaluation` (LightIndex, Position, Normal, Roughness ->
  Factor, Mask, Direction, Distance), `ShaderNodeLightInfo` (Color, Power, Position), `ShaderNodeShadowRaycast`
  (LightIndex, Position, Softness -> Color), `ShaderNodeRaycast`. The Geometry node's Tangent output is the strand's
  tangent on curves (source `node_geometry`: `sd.curve_T`); Hair Info's "Tangent Normal" is the view-facing normal.
  **Units, measured 2026-11-06** (scratchpad `lightacc_test.py`: two spheres under one area light, linear EXR): Light
  Accumulation's output is the sum over lights of Light x Color, as radiance; with Diffuse Light = Light Evaluation's
  Factor (Normal = the surface normal) x Light Info's Color x Power and Diffuse Color = the albedo, it equals a
  Principled diffuse surface within 2% (0.385 / 0.313 / 0.242 vs 0.377 / 0.312 / 0.246) - Factor carries the cosine,
  the falloff and the 1/pi, not the power. Its LightIndex and Weight inputs are hidden (implicit per light).
  Light Accumulation covers light objects only (the world needs its own term). So a Marschner-family hair model (R,
  TT, TRT lobes from L, V, T; Karis SIGGRAPH 2016 for Unreal, Tafuri 2019 for Frostbite; multiple scattering as
  Karis' wrapped term or dual scattering's density fallback) can be written in EEVEE nodes. Also: Blender 5.0 added a
  Cylinder curve shape (STRAND / STRIP / CYLINDER in 5.3); EEVEE's Principled Hair falls back to a diffuse closure of
  its Color socket; WIP PR #164595 (an EEVEE hair closure, one Kajiya-Kay lobe) "not expected to land in its current
  state". Chiang's colour mapping is "a precomputed fit of absorption coefficients to scattered hair color" (pbrt) -
  the colour after multiple scattering, so near-black as a single-bounce colour; per fibre for brown hair (melanin 0.65,
  redness 0.2): A (0.016, 0.004, 0.000), R 0.075 white, TT (0.34, 0.17, 0.03), TRT (0.009, 0.003, 0.000) (computed from
  Cycles' absorption).
- **EEVEE 5.3 against Cycles on the gate's face, one setting at a time (2026-11-04, measured):** `indirect_light_intensity`
  1.2 brings the world light on a grey sphere from 0.836 to 1.002 of Cycles' and the jaw shadow from 0.855 to 0.947;
  the skin's subsurface radius x1.5 cuts the shadow-detail error from 0.103 to 0.075; `trace_max_roughness` 0.75,
  full-resolution tracing, finer Fast GI and 128 samples change nothing; dropping sheen or coat makes the match worse.
  **Corrected the same evening:** the sphere's five brightness bands (dark to lit), EEVEE over Cycles under the image
  light alone: 1.262, 1.294, 1.224, 0.973, 0.836 - EEVEE's world light is flat, not weak; x1.2 gives 1.524 ... 1.002
  (the dark side ~50% too bright), so x1.2 is dropped. EEVEE's world sun extraction is on at Blender's defaults
  (`world.sun_threshold` 10, `sun_angle` 0.0092 rad, `use_sun_shadow` on, `probe_resolution` 1024) and Studio Small
  09 peaks at 541 (135 after our 0.25 strength), so its softbox cores become one sharp sun - the next one-factor sweep.
  **Later the same night (measured, the realism doc §6a):** under the full stage the sphere matches Cycles exactly, so
  the sweep was dropped; the jaw's 15% darkness is EEVEE's shading of the 1.5 m key light at grazing angles (~60%; a
  0.5 m key gives 0.950; no EEVEE shadow setting closes it) plus off-screen bounce (~40%). A light-probe volume
  (`LightProbeVolume`: `capture_indirect` on and `capture_world` off by default; `bpy.ops.object.lightprobe_cache_bake`
  works headless, 3.5-6.7 s) - coarse with the world captured helps a little, fine (24 x 20 x 36) darkens the world.
  Skin scattering x2 keeps lit detail within 3% of Cycles and cuts shadow harshness 1.28 -> 1.16.
- **The live view's fine detail against the film render** (*measured, 2026-11-05*, rec 1; `.dev/gate/parts/proof_eevee/`, bands fine/pore/fold on the gate's cheek view): HD Aaron (CC Blender Tools' material) in EEVEE keeps 58% / 64% / 70% of his Cycles detail; one factor at a time: skin scattering off 0.609 fine (+36%), film filter 0.75 px +7%, anisotropic 16x and 256 samples no change, cubic textures lower - EEVEE's screen-space scattering blurs his normal-map detail. **Our skin with its live-view calibration (`skin/material.py` EEVEE_SCATTER 2.0) is not affected:** Cycles 0.484 / 1.297 / 1.055 against EEVEE 0.546 / 1.512 / 1.169 (113-117%); scattering x1.0 and x0.5 sharpen further (0.715, 0.849 fine). The live view matches the film render on our content; the earlier 80-87% was Aaron's uncalibrated material.
- **GPU frame time** (*source read*, R4 Q6): `--profile-gpu` writes `profile.json` (Trace Event Format) with real GPU
  timestamps on the OpenGL backend only (`gl_debug.cc`, `glQueryCounter(GL_TIMESTAMP)`); on Vulkan / Metal CPU time
  only. 5.3's default here is Vulkan (measured) - so `--gpu-backend opengl --profile-gpu`. `wm.redraw_timer` is wall
  clock; `--debug-gpu` adds labels only.
