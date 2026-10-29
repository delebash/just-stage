# Research 04, pass 2: reference apps (section S3 of the second-pass plan)

Researched 2026-10-29 for RESEARCH.md §4. This pass fills the gaps that round one
([`2026-10-29-research-04-references.md`](2026-10-29-research-04-references.md)) left when it ran out of searches.
Clean-room: behaviour and public docs only; short quotes only. No files were downloaded. About 80 WebSearch
calls were used.

Every fact has a label. **[page read]**: the page was opened and read. **[snippet]**: from a search-result
snippet only. **[measured]**: pulled from this machine (GitHub's API or raw files, 2026-10-29). Each fact also
gives its source URL and the source's date ("undated" when the page shows none). Lines starting
"Assessment:" are my judgement, not facts.

## Top findings

1. **MetaHuman Creator still needs Epic's servers to rig and texture a character.** Epic's docs: "MetaHuman
   Creator in Unreal Engine uses cloud services for auto rigging and texture synthesis". They list two
   epicgames.com service hosts and an S3 bucket to allow
   ([Epic docs](https://dev.epicgames.com/documentation/metahuman/getting-started-with-metahuman-creator-in-unreal-engine), undated, UE 5.6 links, page read).
   The 5.8 release notes add no offline auto-rig
   ([5.8 notes](https://dev.epicgames.com/documentation/metahuman/metahuman-5-8-release-notes-in-unreal-engine), 2026, page read).
2. **OpenRigLogic's licence file is MIT, and the repo holds only libraries.** LICENSE is "MIT License,
   Copyright (c) 2026 Epic Games, Inc."
   ([raw](https://raw.githubusercontent.com/EpicGames/OpenRigLogic/main/LICENSE), measured). The repo
   contains the C++ DNA library (reads and writes DNA, binary and JSON), RigLogic (joints, blend shapes,
   animated maps, RBF, PSD-net, ML), SWIG Python bindings, docs and tests. It has no meshes or assets: sample
   assets and the Faceboard Control Rig are on Fab under the Fab Standard License. TRADEMARKS.md bars the
   Epic names from product names
   ([README](https://raw.githubusercontent.com/EpicGames/OpenRigLogic/main/README.md), measured).
3. **Move AI no longer exists as a company.** Oxford Metrics (Vicon's parent) bought its assets on
   2026-10-09 for £525,000
   ([ResultSense](https://www.resultsense.com/news/2026-10-09-oxford-metrics-vicon-move-ai-assets/), 2026-10-09, page read).
   Move Live and Move Pro are gone from the docs. The current products are Genesis (on-premise, 6–12
   cameras, up to 8 actors, NVIDIA GPU) and Move One (single camera). Genesis Live (real time) launched in
   v1.1.1 on 2026-07-16 with optional finger tracking
   ([Genesis release notes](https://docs.move.ai/knowledge/genesis-release-notes), page read).
4. **Unreal's timeline tools fill most of an iClone-type animator's needs, but the key pieces are new.**
   Sequencer has shots, sub-sequences and takes, with priority by "Hierarchical Bias". Control Rig tracks
   can be layered (additive). Animation layers arrived in 5.5, and Selection Sets and a unified Constraint
   window in 5.7. 5.8 adds Anim Mixer in Sequencer (experimental), Direct Mesh Controls (experimental),
   Control Rig Dynamics (experimental) and Control Rig Physics (beta). Take Recorder records Live Link,
   mocap and audio into sequences (sources in the Unreal section).
5. **Ready Player Me shut down on 2026-01-31** after Netflix bought it (announced 2025-12-19)
   ([PocketGamer.biz](http://www.pocketgamer.biz/netflix-acquires-avatar-creation-platform-ready-player-me/), 2025-12-22, page read).
   Avaturn is still running. It makes an avatar from a selfie, with a Mixamo-compatible rig, ARKit
   blendshapes and visemes. Its Pro plan is $800/month for 1,000 avatars
   ([avaturn.me](https://avaturn.me/), page read; [pricing](https://avaturn.me/pricing), page read).
6. **3DCoat 2026 puts the whole sculpt-to-texture chain in one app, with a scripting layer that mirrors its
   C++ API.** The chain: voxel and surface sculpting, retopology (manual or AutoPo), UV, paint, and new GPU
   node texturing compiled into shaders. Its Python API is "almost 1:1" with the C++17 Core API
   ([3DCoat docs](https://3dcoat.com/documentation/?p=2379), 2022-09-23, page read). It runs on Windows,
   Ubuntu and macOS, and costs €379 perpetual for an individual
   ([CG Channel](https://www.cgchannel.com/2026/07/pilgway-releases-3dcoat-2026-and-3dcoattextura-2026/), 2026-07-23, page read).
7. **Style3D's cloth simulation is NVIDIA-only and Windows-only.** The help center says it "uses the
   NVIDIA CUBDA [CUDA] architecture … you can only use the NVIDIA GPU", and "Style3D only supports windows"
   ([help.style3d.com](https://help.style3d.com/cloud/en/9f52/e95c/c38e/520f), 2024-11-22, page read).
   CG Channel says the same of Atelier and the Unreal Simulator
   ([CG Channel](https://www.cgchannel.com/2024/08/tools-to-watch-in-fall-2024-style3d-atelier-and-simulator/), 2024-08-28, page read).
8. **Cascadeur is now at 2026.2** (2026-08-06). It adds additive animation layers (alpha), easing, "Motion
   Generation" (the renamed Root Motion), custom Python UI in PySide/QML, Python stubs and BVH import. The
   paid tiers are rent-to-own
   ([CG Channel](https://www.cgchannel.com/2026/08/nekki-releases-cascadeur-2026-2-with-animation-layers/), page read).
   AI Inbetweening now allows up to 120 frames between keys
   ([help](https://cascadeur.com/help/category/278), page read).
9. **Maya MotionMaker runs on the CPU, on the user's machine, and was trained only on Autodesk's own
   mocap.** It is an autoregressive next-pose predictor whose output is baked to keys on its own animation
   layer ([Autodesk blog](https://blogs.autodesk.com/media-and-entertainment/2025/10/15/ai-powered-motionmaker-for-animation-your-top-questions-answered/), 2025-10-15, page read).
   Maya 2027.2 lets users train models on their own data, locally
   ([Digital Production](https://digitalproduction.com/2026/07/24/maya-2027-2-trains-motionmaker/), 2026-07-24, page read).
10. **Autodesk's 2027 apps share one stack.** Maya, 3ds Max and MotionBuilder 2027 all use Python 3.13.3,
    PySide/Qt 6.8.3, C++20 and VS 2022
    ([Autodesk VFX platform alignment](https://aps.autodesk.com/developer/overview/me-vfx-platform-alignment), undated, page read).
11. **Cinema 4D is rental-only at $109/month or $839/year.** Its 2026.4 MCP server records "every action it
    takes" in the undo stack and runs only in the full version
    ([CG Channel](https://www.cgchannel.com/2026/09/maxon-releases-cinema-4d-2026-4-with-a-new-mcp-server/), 2026-09-30, page read).
    C4D embeds Python 3.11.4 and has about 18 plugin hook types
    ([Maxon Python manual](https://developers.maxon.net/docs/py/2026_0_0/manuals/manual_py_in_c4d.html), page read).
12. **Houdini 22 shipped on 2026-07-15 as build 22.0.368.** It dropped the OpenGL renderer for a Vulkan
    viewport and needs Windows 11 or Apple silicon
    ([Digital Production](https://digitalproduction.com/2026/07/16/houdini-22-how-right-were-we/), 2026-07-16, page read).
    Its Vellum changes are only two hair-solver items
    ([H22 Vellum](https://www.sidefx.com/docs/houdini/news/22/vellum.html), page read). Houdini packages are
    a documented JSON format
    ([packages ref](https://www.sidefx.com/docs/houdini/ref/plugins.html), page read).
13. **Daz Studio 6 shipped on 2026-06-04, free.** The forum thread that carried the "Daz Studio 2025" alpha
    builds (6.25.2025.x) since April 2025 is now titled "Daz Studio 6 Beta"
    ([Daz forum](https://www.daz3d.com/forums/discussion/728111), page read). DS 6 brings Qt 6, Iray
    2025.0.3, ES2016 scripting and an AI chat, and retires 3Delight
    ([Daz tech highlights](https://hpcl.daz3d.com/blog/daz-studio-6-technical-highlights), page read).
14. **Substance 3D Painter keeps two plugin APIs.** JavaScript + QML gets "no new features" since 2020, but
    its API was still bumped to 1.1.20 in 12.0. Python (3.13 in 12.0) plugins live in `python/plugins`
    ([12.0 notes](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/release-notes/version-12-0), 2026-03-09, page read).
    Linux is official (RHEL 8/9, plus Ubuntu 22.04 for the Steam edition)
    ([system requirements](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/getting-started/system-requirements), 2026-10-19, page read).
15. **Conflicts from round one, settled.** ArtCraft is dual MIT **or** Apache-2.0: it ships both licence
    files, and GitHub's SPDX field shows only one
    ([NOTICE](https://raw.githubusercontent.com/storytold/artcraft/main/NOTICE), measured). MetaTailor's free
    tier is 5 FBX exports a month; the app is now at v2.6
    ([pricing](https://www.metatailor.com/pricing), page read). Houdini 22's date is 2026-07-15. ZBrush GoZ
    is unsettled, and whether MetaTailor is built on Unity is not findable (see Conflicts).

---

## 3DCoat (Pilgway): sculpt, retopology, UV, paint

- Three products: 3DCoat 2026, 3DCoatTextura 2026 (texturing only, cheaper), and free 3DCoatPrint. 3DCoatPrint
  has voxel modelling, with exports "reduced to … 40K triangles"
  ([3dcoat.com news](https://3dcoat.com/news/article/3dcoat-2026-officially-released/), undated, page read;
  [pilgway.com/licensing/2](https://pilgway.com/licensing/2), undated, page read).
- Stable build 2026.11, called "production-ready". Public beta from 2026-06-01; builds from February 2026
  ([CG Channel](https://www.cgchannel.com/2026/07/pilgway-releases-3dcoat-2026-and-3dcoattextura-2026/), 2026-07-23, page read).
- New Node System: non-destructive GPU node texturing that previews while sculpting. Node graphs are
  "compiled into shaders" and written in NGL, "Pilgway's own GLSL-based language". It ships as two
  executables, a GPU build and a legacy CPU build (same, page read).
- Also new: 30 PBR channels, a Splitter tool, reworked parametric hybrid modelling, asset trees in the
  Retopology and Modeling rooms, LWO3 import and better GLB export (same, page read).
- Sculpt room:
  - **Voxel mode** is for blocking out. It is "memory, and processor intensive", and resolution goes up
    with Res+.
  - **Surface mode** is polygonal, with dynamic subdivision in the brushes. It is the only mode that stores
    Sculpt Layers.
  - Users switch modes at any time, but voxel volumes have no layers
    ([3DCoat docs, Sculpt](https://3dcoat.com/documentation/?p=2256), 2022-09-19, page read).
- Retopology: Auto Retopo or manual. "Conform Retopo Mesh" keeps the retopo mesh in step with sculpt edits,
  but only for Pose, Transform and Move edits (same, page read).
- AutoPo can send its result to the Retopo room, or to Paint (Ptex, micro-vertex or per-pixel) with UV seams
  and maps made automatically ([3DCoat docs](https://3dcoat.com/documentation/?p=2611), snippet).
- Platforms: Windows 7+, Ubuntu 20.04+, macOS 10.13+ (CG Channel 2026-07-23, page read).
- Prices for individuals:
  - perpetual node-locked €379;
  - subscription €20.80/month or €169.85/year;
  - rent-to-own, 11 × €41.60.
  Studio perpetual is €539 node-locked or €579 floating. Textura's individual perpetual is €159 (was €119)
  (same, page read).
- A perpetual licence includes "12 months of free program updates". The individual licence "provides for
  commercial use of the assets created" and stays the person's, not the company's
  ([pilgway.com/licensing/2](https://pilgway.com/licensing/2), page read).
- After the 30-day trial, the program drops to a "Free Learning mode" that lasts indefinitely
  ([3dcoat.com news](https://3dcoat.com/news/article/3dcoat-2026-officially-released/), page read). Whether
  that mode allows commercial use is not stated.
- Scripting has three routes:
  - **Python**, embedded and "intended to trigger UI commands, operate over the scene, and create new tools".
    It is "much slower than C++".
  - **Core API**, "a compliable C++17 program", built only with Visual Studio.
  - **AngelScript**, "deprecated" and not working on Apple silicon.
  ([3DCoat docs](https://3dcoat.com/documentation/?p=2379), 2022-09-23, page read). The embedded Python is
  3.8.10 (3DCoat docs via search, snippet).
- Assessment: 3DCoat is the reference for "rooms" that hand one asset along the chain (block, sculpt,
  retopo, UV, paint). Its Python layer that mirrors the C++ API one-to-one fits JustStage's plan of one
  command API for every language.
- Licence: Pilgway EULA, proprietary. Commercial use: yes (individual licence). [pilgway.com/licensing](https://pilgway.com/licensing/2)

## Style3D (Zhejiang Lingdi / Linctex): cloth

- **Atelier** sews 2D pattern pieces and drapes them on an avatar, with "fast GPU-based simulation". It also
  has Auto Rig and Auto Quad Remesh, and an online library of 4,000 garments, trims, fabrics and avatars. It
  imports OBJ and FBX and exports OBJ, FBX, Alembic and USD
  ([CG Channel](https://www.cgchannel.com/2024/08/tools-to-watch-in-fall-2024-style3d-atelier-and-simulator/), 2024-08-28, page read).
- **Simulator** is an Unreal plugin for real-time garment simulation or "extremely compact" caches. It takes
  Style3D SMD files, or FBX garments from 3ds Max, Maya or Blender after some preparation (same, page read).
- The Simulator's supported Unreal versions disagree between sources: UE 4.27+ (CG Channel 2024, page read),
  "UE 5.0~5.4" (Fab listing, snippet), and UE 5.0+ (Style3D blog, snippet).
- Platforms: Windows 10+. "GPU simulation requires a compatible NVIDIA GPU"; macOS and Linux are not
  mentioned (CG Channel 2024, page read).
- The help center, covering Style3D Studio and Fabric: "Style3D only supports windows". The software "uses
  the NVIDIA CUBDA [CUDA] architecture", so "you can only use the NVIDIA GPU". Minimum RTX 2060 and 16 GB RAM
  ([help.style3d.com](https://help.style3d.com/cloud/en/9f52/e95c/c38e/520f), 2024-11-22, page read).
- Prices in 2024, rental only:
  - Atelier $35/month or $248/year for individuals, $1,299/year for studios;
  - Simulator $248/year for individuals, $1,499/year for studios
  (CG Channel 2024, page read). No 2026 price list was found; Style3D's own blog posts give conflicting
  figures ($40, $99 or $180 a month; snippet).
- Free version: 80.lv says "Atelier has a free version"
  ([80.lv](https://80.lv/articles/this-new-garment-modeling-software-has-released-free-version), 2024-07-02, page read).
  A commenter there and a 2024 Patreon review call it a trial, or limited to non-commercial use and
  low-resolution export (snippet).
- Research: GarmageNet (ACM TOG, SIGGRAPH Asia 2025) links 2D patterns to 3D garment shapes and can start a
  simulation from them (Style3D press release, 2026-08-31, snippet). Style3D Studio V9.3 came out in May 2026
  (third-party directory, snippet).
- Assessment: the simulation core is CUDA-only, so under the 2026-10-29 scope rule Style3D is only a
  reference, labelled NVIDIA-only. Its garment features (auto rig, auto quad remesh, compact caches for UE)
  are the bar for game-ready garments.
- Licence: Style3D terms (not read). Commercial use: unclear on the free version; paid plans not read.
  [style3d.com](https://www.style3d.com/)

## Unreal Engine: Control Rig and Sequencer as the reference for an iClone-type timeline

- Sequencer has two parts. The Level Sequence **asset** holds "tracks, cameras, keyframes, and animations".
  The Level Sequence **actor** in the level binds that data to the level. A Camera Cuts track picks the
  camera
  ([UE 5.8 docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-sequencer-movie-tool-overview), page read).
- Shots, sub-sequences and takes:
  - a Shots track holds shots, each its own Level Sequence asset, shown in the parent as a sub-sequence
    section;
  - takes are alternate copies of a shot, and the active take is starred;
  - priority comes from "Hierarchical Bias": the root is 0, sub-sequences default to 100, and the higher
    bias wins when two sources drive one actor
  ([UE docs, shots and takes](https://dev.epicgames.com/documentation/en-us/unreal-engine/sequences-shots-and-takes-in-unreal-engine), page read).
- Bindings: "possessable" binds an actor already in the level; "spawnable" exists only while the sequence
  plays (UE 4.26/4.27 API docs, [Blueprint Sequence API](https://docs.unrealengine.com/4.26/en-US/BlueprintAPI/Sequence/), snippet). The 5.8 page
  on this topic rendered empty.
- Control Rig is "a set of in-engine tools for rigging and animating characters". Users build controls,
  bones and nulls, with Modular Rigging for speed. It runs in Sequencer, and also in Blueprints and Animation
  Blueprints
  ([UE 5.8 docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/control-rig-in-unreal-engine), page read).
- Animating with Control Rig in Sequencer
  ([UE 5.8 docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/animating-with-control-rig-in-unreal-engine), page read):
  - a Control Rig track lists the rig's controls, and pressing S keys a control;
  - several rigs can be animated at once;
  - **Layered** Control Rig tracks need a working Backwards Solve graph. They let users layer edits on
    animation sequences "without the need to bake";
  - layered tracks evaluate in descending Order (starting at 100), and their weight can be keyed.
- Animation layers arrived in UE 5.5: additive or override, keyable weight, mute and lock. They work on
  skeletal meshes and Control Rigs
  ([Versluis](https://www.versluis.com/2026/06/how-to-use-animation-layers-in-unreal-engine/), 2026-06-08, page read).
- UE 5.7 animation
  ([CG Channel](https://www.cgchannel.com/2025/11/unreal-engine-5-7-five-key-features-for-cg-artists/), 2025-11-12, page read):
  - Selection Sets and a unified Constraint window;
  - the Skeletal Mesh Editor moves between bones, weights and blendshape sculpting without switching tools;
  - an experimental Morph Target Viewer, and a Control Rig Dependency View;
  - IK Retargeter gains Crotch Height and a Floor Constraint;
  - experimental Spatially Aware Retargeting reduces self-collision.
- UE 5.8 animation
  ([CG Channel](https://www.cgchannel.com/2026/06/see-5-key-features-for-cg-artists-in-unreal-engine-5-8/), 2026-06-17, page read):
  - Direct Mesh Controls (experimental): pose by "pulling body parts around directly", in the viewport and
    Sequencer;
  - Control Rig Dynamics (experimental): a particle solver for secondary motion, claimed "5x" faster than
    Chaos Cloth and Flesh;
  - Control Rig Physics (beta);
  - blendshape authoring and corrective sculpting on shots;
  - animation mixing in Sequencer (experimental);
  - Chaos Cloth round-trips assets with Marvelous Designer.
- Anim Mixer is "the experimental Anim Mixer plugin for Unreal Engine 5.8". It mixes and layers animation
  sources in Sequencer with looping, blending and root motion, through UAF and Animation Blueprints
  ([UE forums tutorial](https://forums.unrealengine.com/t/tutorial-animation-mixer-in-sequencer-intro/2731468), 2026-06-25, page read).
- Take Recorder "records gameplay animation, live performances, and other sources" into Level Sequences:
  actor properties, Live Link subjects, mocap systems and microphone audio. Takes are non-destructive, with
  slates and auto-lock
  ([UE 5.8 docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/take-recorder-in-unreal-engine), page read).
- Assessment, how this maps onto iClone:
  - Level Sequence ≈ the project timeline;
  - Control Rig track plus layered tracks ≈ key editing over a motion layer;
  - anim layers and Anim Mixer ≈ motion clips with blending;
  - Take Recorder ≈ Motion LIVE recording;
  - shots and takes ≈ multi-shot editing.

  The layer and mixer pieces are only 5.5–5.8 old and partly experimental, so Unreal shows the shape a
  timeline can take rather than a settled design.

## Ready Player Me

- Netflix agreed to buy Ready Player Me. TechCrunch first reported it on 2025-12-19, and PocketGamer
  reported it on 2025-12-22.
  About 20 staff moved to Netflix; of the founders, only the CTO. Services "shut down … on January 31st,
  2026", PlayerZero included
  ([PocketGamer.biz](http://www.pocketgamer.biz/netflix-acquires-avatar-creation-platform-ready-player-me/), page read).
- The hosted creator, PlayerZero and the public API went offline. GLBs exported earlier still work, but
  nothing served from RPM's servers does
  ([Avatar SDK blog](https://avatarsdk.com/blog/2026/08/31/avatar-platforms-2026-whos-alive-whos-gone/), 2026-08-31, page read; written by a competitor).
- Union Avatars has been offline since July 2026; Spatial announced its closure in July 2026 (same, page read).
- Assessment: a hosted avatar service can vanish with its API. JustStage's character data should never
  depend on one.

## Avaturn

- Avaturn calls itself "a realistic avatar creator and an avatar system for games, apps and metaverses".
  Users can change body shape, clothes, accessories, hairstyles, shoes and glasses. Output is GLB, with guides
  for converting to FBX and VRM and for using Mixamo animations
  ([docs](https://docs.avaturn.me/docs/what-is-avaturn/), undated, page read).
- Avatars are made from a selfie by generative AI. The body has a standard humanoid rig "compatible with
  Mixamo animations", with ARKit blendshapes and visemes. SDKs and plugins exist for Web, Unity, Unreal, iOS
  and Android ([avaturn.me](https://avaturn.me/), © 2025, page read).
- Pricing: the free integration has "no limits on the number of avatars created or number of exports"
  (docs, page read). Pro is $800/month for up to 1,000 avatars, then $0.15 each, with the API, SDK, custom
  garments and branding. Enterprise adds full body scans and custom terms
  ([pricing](https://avaturn.me/pricing), page read).
- Avatar SDK, a competitor, says Avaturn is "the same company as in3D" (blog 2026-08-31, page read).
  avaturn.me shows only "© Avaturn", so this is not confirmed.
- Licence: Avaturn terms (the terms page returned 404). Commercial use: unclear.

## MetaHuman: cloud services, licence text, OpenRigLogic

**Cloud services**
- "MetaHuman Creator in Unreal Engine uses cloud services for auto rigging and texture synthesis". Hosts to
  allow: `mh-texture-synthesis-service.eeeb.live.use1a.on.epicgames.com`,
  `mh-uemhc-autorig-service.eeeb.live.use1a.on.epicgames.com`, `s3.us-east-1.amazonaws.com`. The page does
  not mention an Epic login
  ([Epic docs](https://dev.epicgames.com/documentation/metahuman/getting-started-with-metahuman-creator-in-unreal-engine), undated, page read).
- The editor API has `FMetaHumanCharacterEditorCloudRequests`, "Struct holding requests to the MetaHuman
  Cloud Services". It holds an auto-rig request and high-resolution face and body texture requests
  ([UE API](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/MetaHumanCharacterEditor/FMetaHumanCharacterEditorCloudRe-), page read).
- 5.8 release notes ([page](https://dev.epicgames.com/documentation/metahuman/metahuman-5-8-release-notes-in-unreal-engine), page read):
  - degenerate-triangle detection "before autorigging";
  - an updated Texture Synthesis model;
  - MetaHuman Animator body capture uses an "offline solve", and Animator runs on Linux and macOS;
  - Mesh to MetaHuman converts "any human character mesh with arbitrary topology";
  - Python `GetFaceModelCoefficients` and `SetFaceModelCoefficients`;
  - DCC Export gains a DNA Export control and SMRF textures.
- A 5.8 user reports that "Full Rig" stalls at "75% / RUNNING" and then fails with "Server Error". This
  happened in 4 of 4 tries; no Epic reply was visible
  ([UE forum](https://forums.unrealengine.com/t/ue-5-8-metahuman-character-full-rig-remains-running-and-times-out-after-300-seconds/2739214), 2026-07-29, page read).
- Press since 5.6: "Cloud services still shoulder autorigging and texture synthesis"
  ([Digital Production](https://digitalproduction.com/2025/06/05/metahumans-graduate-ready-for-unity-godot-and-the-fab-cash-register/), 2025-06-05, page read).
  CG Channel says the tools "can't run entirely locally"
  ([CG Channel](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/), 2025-06-04, page read).
- Assessment: making a new MetaHuman needs Epic's online service and an Epic-hosted job. Only using one
  (evaluating the rig with OpenRigLogic) is local and open.

**Licence text: unreachable for scripted reads (the user reads it)**
- `metahuman.com/license` redirects to the Epic login (302 to epicgames.com/id). It was not followed.
  `unrealengine.com/eula/mhc` returned 403. Both tried 2026-10-29.
- A search snippet of metahuman.com/license reads: MetaHuman is "included in the standard Unreal Engine
  license", free under $1M revenue, "can be used with any engine or creative software". The legacy
  MetaHuman Creator EULA applies to UE 5.5 and earlier; from 5.6 the UE EULA applies (snippet).
- CG Channel's summary, 2025-06-04 (page read):
  - free under $1M a year;
  - characters and clothing may be sold on marketplaces;
  - a seat licence ($1,850/year) above $1M;
  - MetaHumans are "non-engine products", so no 5% royalty in Unity or Godot;
  - usable in "workflows that incorporate artificial intelligence technology", but not to train or enhance
    AI models.
- Digital Production (2025-06-05, page read): "feeding MetaHumans back into training data is off-limits";
  Fab pays sellers 88%.
- An open forum question asks whether shipping MetaHuman Animator's runtime models falls under Fab EULA
  §5(b) "Engine Tools". No Epic answer
  ([UE forum](https://forums.unrealengine.com/t/licensing-question-shipping-metahuman-animator-markerless-motion-capture-runtime-models-in-a-steam-game/2839692), snippet).

**OpenRigLogic: what the repo holds**
- `EpicGames/OpenRigLogic`: created 2026-06-05, last push 2026-10-23, 304 stars. Licence MIT. Branches:
  `main` ("Experimental"), `5.8` ("Production-Ready"), `gh-pages` and `gh-pages-source`
  ([GitHub API](https://api.github.com/repos/EpicGames/OpenRigLogic), measured).
- LICENSE is the standard MIT text, "Copyright (c) 2026 Epic Games, Inc."
  ([raw](https://raw.githubusercontent.com/EpicGames/OpenRigLogic/main/LICENSE), measured). Source headers
  still say "Copyright Epic Games, Inc. All Rights Reserved." (e.g. `include/riglogic/RigLogic.h`, measured).
- README (measured):
  - **DNA Library**: reads and writes MetaHuman DNA files;
  - **RigLogic**: "realtime evaluation of the MetaHuman rig";
  - both are C++ with Python bindings, built with CMake 3.14+ and C++11+;
  - SWIG and Python only for the bindings; GoogleTest and Google Benchmark optional;
  - platforms: "console platforms and mobile devices in addition to Windows, Linux, and macOS".
- README: sample assets and the "MetaHuman Faceboard Control Rig" are "acquired separately" on Fab under the
  Fab Standard License. A DCC export package holds a head DNA, a body DNA and textures; "Groom and clothing
  information is not currently part of this package" (measured).
- The tree has 799 entries (measured):
  - DNA: binary and JSON stream readers and writers (`include/dna/JSONStreamReader.h`);
  - RigLogic modules: joints (BPCM, quaternions, twist-swing, ML), blendshapes, animated maps, conditional
    table, controls, RBF, PSD-net, machine-learned behaviour;
  - helpers: `terse` (binary and JSON archives), `trio` (streams), `pma` (memory);
  - SWIG `.i` files under `python/`;
  - a design doc with algorithm notes (`docs/design/`).

  No mesh or texture data.
- TRADEMARKS.md: the MIT licence "covers code only". A fork may not use the Marks in its own product name,
  and must "choose your own name" and attribute ("[Your Software] is based on OpenRigLogic")
  ([raw](https://raw.githubusercontent.com/EpicGames/OpenRigLogic/main/TRADEMARKS.md), measured).
- GOVERNANCE.md: "OpenRigLogic is MIT-licensed and Epic does not intend to change that". Licence changes get
  at least 2 weeks of public notice
  ([raw](https://raw.githubusercontent.com/EpicGames/OpenRigLogic/main/GOVERNANCE.md), measured).
- The 5.8 notes call the MetaHuman Devkit "fully open source, starting with the OpenRigLogic repository"
  (5.8 notes, page read).
- Also seen: a Blender add-on, MetaWrap, "converts sculpts, 3D scans, or AI characters into Unreal Engine
  MetaHumans" ([CG Channel tag page](https://www.cgchannel.com/tag/claude-desktop/), 2026-10-29, teaser only, page read).
- Assessment: JustStage may read and write DNA and evaluate the rig under MIT. It may not name anything
  "MetaHuman" or "RigLogic", and it must get no rig content from the Fab samples.

## Maya MotionMaker: how it works

- MotionMaker "uses machine learning to train on a motion dataset" and predicts the next pose from the
  character's current position and trajectory. It looks at the previous second of animation
  ([Autodesk blog](https://blogs.autodesk.com/media-and-entertainment/2025/10/15/ai-powered-motionmaker-for-animation-your-top-questions-answered/), 2025-10-15, page read).
- It runs locally: "generated using only your machine's CPU", and "nothing goes out of your machine" (same).
- Training data: only Autodesk's own mocap, about 30 minutes each of two dogs and about an hour each of a male
  and a female actor. "Autodesk owns the data but is making the trained models freely available" (same).
- Output is baked keyframes, optionally on their own animation layer, which regenerates without touching
  hand-keyed layers. Bipeds can walk or run forward, sideways and back, and jump; canines can jump, sit and
  lie down (same).
- The stock characters come with HumanIK characterisation. HIK is not required: any retargeter can move the
  motion onto another rig (same).
- An Autodesk research blog traces the roots to University of Edinburgh work from 2017–18
  ([Autodesk blog](https://blogs.autodesk.com/media-and-entertainment/2025/06/04/meet-motionmaker/), 2025-06-04, snippet).
- Maya 2027.2, "Bring Your Own Data":
  - users train models on their own mocap or keyframes, "local to the user's machine";
  - the source data is prepared against a standard character definition, with frame ranges tagged by action
    style;
  - Maya 2027 added horses (`adsk_equine`);
  - there is a `motionMaker` command for generating and for exporting training data
  ([Digital Production](https://digitalproduction.com/2026/07/24/maya-2027-2-trains-motionmaker/), 2026-07-24, page read).
- 2027.1: MotionMaker workflow fixes (frame ranges on clips, shortcuts), and OpenTimelineIO in Sequencer
  ([CG Channel](https://www.cgchannel.com/2026/05/autodesk-releases-maya-2027-1/), 2026-05-21, page read).
- Assessment: MotionMaker is the reference for path-driven locomotion generation that runs on the CPU from a
  small, owned dataset. It is not a large cloud model.

## Move AI: Move Live (real time) and finger tracking

- Oxford Metrics, Vicon's parent, bought "the technology and team" of Move AI Ltd on 2026-10-09: £525,000 in
  cash, about £725,000 with costs. Patents, staff and customers moved to Vicon; no product roadmap was given
  ([ResultSense](https://www.resultsense.com/news/2026-10-09-oxford-metrics-vicon-move-ai-assets/), page read).
  Move AI's 2025 revenue was £1.1M, unaudited (RNS via aggregators, snippet).
- Move Live at launch: up to 2 actors, 4–8 machine-vision cameras, latency "around 100ms". It ran on an
  on-premise Ubuntu 20.04 server (96 GB RAM and an RTX A6000 recommended), streamed over gRPC to an Unreal
  Live Link plugin, and was subscription-only
  ([CG Channel](https://www.cgchannel.com/2024/06/move-ai-launches-aaa-quality-real-time-mocap-solution-move-live/), 2024-06-27, page read).
- In 2026 the docs list only Genesis and Move One; the Move Live and release-notes pages return 404
  ([docs.move.ai/knowledge](https://docs.move.ai/knowledge), page read).
- Genesis: "the first enterprise-grade, markerless motion capture system from MOVE". 6–12 Z-Cams, up to 8
  actors, up to 240 fps (FHD), capture volumes 4×4 m to 16×16 m. It runs on "readily available Nvidia GPUs"
  ([Genesis overview](https://docs.move.ai/knowledge/genesis-overview), © 2026, page read). The docs split it
  into Genesis Live (real-time calibration, mocap, streaming to UE) and Genesis Post (offline)
  ([Genesis index](https://docs.move.ai/knowledge/genesis), page read).
- Genesis release notes ([page](https://docs.move.ai/knowledge/genesis-release-notes), page read):
  - **v1.1.1 (2026-07-16):** launches Genesis Live; finger tracking "can be toggled on or off"; a
    smoothing-versus-latency filter (0–5); m3 model in beta;
  - **v1.1.3 (2026-08-06):** the Performance model tracks more keypoints, "including fingers", in Genesis
    Live; Ubuntu 24.04 only from then on;
  - **v1.0.30 (2026-06-17):** retargeting to SOMA and Unitree G1 rigs.
- Genesis outputs: FBX, BVH, GLB, USDZ and .blend (raw and retargeted), C3D, JSON with skeleton and rotations,
  and preview MP4s ([output formats](https://docs.move.ai/knowledge/genesis-output-formats), page read).
- The old Move Live release notes (v2.5.44, 2025-12-18) introduced Gen 2 tracking: wrists on by default,
  fingers optional, best in volumes up to 8×8 m (search snippet of docs.move.ai; the page now 404s).
- Move One pricing: Starter $18 (60 credits), Standard $48 (180), Plus $225 (240), Advanced $490 (700). s1
  costs 1 credit per person-second and s2 costs 2. Free users get a one-time 30 credits and 30-second videos
  ([Move One pricing](https://docs.move.ai/knowledge/move-one-pricing), © 2026, page read). This **replaces**
  round one's snippet figures of 6 and 12 credits a second.
- Licence: Move AI (now Vicon) terms. Commercial use: unclear. GPU: NVIDIA only (Genesis).

## Rokoko Studio: platforms

- System requirements:
  - Windows 10 64-bit, an Intel i5 (Ivy Bridge) or AMD A10 7850k, 8 GB RAM, a DX10 GPU;
  - macOS Big Sur with an Apple M1;
  - Linux is not listed
  ([rokoko.com/studio/beta](https://www.rokoko.com/studio/beta), undated, page read).
- Rokoko's support article says Studio is "only officially supported on Apple-silicon Mac's"; Intel Macs
  are not supported (search snippet; [support.rokoko.com](https://support.rokoko.com/hc/en-us/articles/4418023603345)
  returned 403).

## Cinema 4D: price and Python plugin API

- 2027.0 came out on 2026-10-14. It adds object scattering, LiquidFX, a Scene Nodes field and effector,
  and CAD import; no character features. It needs Windows 11 or macOS 15+. Rental only: **$109/month or
  $839/year**
  ([CG Channel](https://www.cgchannel.com/2026/10/maxon-releases-cinema-4d-2027-0/), 2026-10-15, page read).
- 2026.4's MCP server:
  - "runs locally"; local-network use needs a separate opt-in;
  - "turned off by default";
  - "every action it takes appears in the undo stack";
  - official clients are Claude Desktop and ChatGPT Desktop; LM Studio also works;
  - full Cinema 4D only (not Lite, Team Render or the command line);
  - 2026.4 ran on Windows 10+ and macOS 14+
  ([CG Channel](https://www.cgchannel.com/2026/09/maxon-releases-cinema-4d-2026-4-with-a-new-mcp-server/), 2026-09-30, page read).
- MCP preferences: "Copy Config" puts the server details and an "authentication key" on the clipboard. The
  client may ask for permissions "once per project". Python execution depends on the MCP Server's Security
  settings
  ([Maxon help 2027](https://help.maxon.net/c4d/2027/en-us/Content/html/MCPADAPTERPREFS-MCPADAPTERPREFS_GROUP_CLIENTS.html.md), page read).
- Python: embedded **3.11.4** on Windows and macOS, "based on a vanilla CPython interpreter" but not
  interchangeable with it. Scripts run in the Script Manager; plugins are `.pyp` files loaded at boot
  ([Python manual](https://developers.maxon.net/docs/py/2026_0_0/manuals/manual_py_in_c4d.html), 2026.0, page read).
- Plugin hooks (same, page read):
  - CommandData: a button that "runs a piece of code", often with a GeDialog;
  - ObjectData: generators and deformers;
  - TagData, ShaderData, ToolData, MessageData ("core message stream");
  - SceneLoaderData and SceneSaverData, BitmapLoader and Saver;
  - SculptBrushToolData, PreferenceData, NodeData, FalloffData (deprecated).

  GUIs are defined in resource "markup files".
- Modules: `c4d`, `c4d.plugins` ("plugin hooks"), `c4d.gui`, `c4d.documents`, `c4d.modules`, `maxon` and
  `mxutils` ([Python SDK index](https://developers.maxon.net/docs/py/2026_0_0/index.html), page read).
- Undo and events, from a Maxon SDK specialist: `EndUndo` "will set the current state of doc to be the final
  state of the undo handling". `EventAdd` puts "an update event on the core event stack". Both must run on
  the main thread ([Maxon dev forum](https://developers.maxon.net/forum/post/63371), undated, page read).
  Each `StartUndo`/`EndUndo` pair is one undo step (forum, snippet).
- C++ SDK: CMake is mandatory ("You must build plugins for 2026 with a CMake based build system"), and the
  Project Tool was removed in 2025.3. The SDK targets C++20, though most C++20 features are not yet supported.
  Breaking the build rules can give "binary incompatible" plugins
  ([C++ migration](https://developers.maxon.net/docs/cpp/2026_0_0/manual_migrating_to_2026.html), page read).

## Houdini: HDK ABI rules, packages JSON, Houdini 22's Vellum, release date

- HDK ABI: it "can change from time to time, requiring plugins to be recompiled". `HDK_API_VERSION` (in
  `UT_HDKVersion.h`, since 15.5.500) is "updated to the last Houdini version that an ABI incompatible change
  was made". It is a packed `%02d%02d%04d` integer, "typically updated on every major release and only
  occasionally on X.Y releases". Adding functions does not change it. The build number in `SYS_Version.h`
  rises with "every Houdini build"
  ([HDK compatibility](https://www.sidefx.com/docs/hdk/_h_d_k__intro__compatibility.html), page read).
- HDK build: other build systems should use "the same compiler settings as hcustom" (`hcustom --cflags` and
  `--ldflags`). Plugins must not link their own allocators (e.g. `tbbmalloc_proxy`), or "conflicts and
  crashes can occur"
  ([HDK compiling](https://www.sidefx.com/docs/hdk/_h_d_k__intro__compiling.html), page read).
- Packages are `.json` files ([packages ref](https://www.sidefx.com/docs/houdini/ref/plugins.html), page read):
  - **Scanned from:** `$HOUDINI_USER_PREF_DIR/packages`, `$HSITE/houdiniX.Y/packages`,
    `$HOUDINI_PACKAGE_DIR` and `$HFS/packages`, alphabetically, with no subfolders.
  - **Keys:** `hpath` (prepend, append or replace), `env`, `enable` (bool or expression),
    `load_package_once`, `process_order`, `package_path`, `requires` (stops on a missing dependency),
    `recommends` (warns), `preload_libraries`, `show`. `path` is deprecated.
  - **Variables:** `${VAR-DEFAULT}` gives a default; `$HOUDINI_PACKAGE_PATH` is relative to the package.
  - **Conditional keys:** expressions on `houdini_version`, `houdini_os`, `houdini_python` and
    `houdini_platform_build`.
  - **Debugging:** set `HOUDINI_PACKAGE_VERBOSE`.
- Houdini 22's Vellum changes are only two: a "Quasistatic" solve for hair Bend/Twist constraints (stronger
  bend resistance, notably on branched hair), and Angular Damping on the Vellum Solver
  ([H22 Vellum](https://www.sidefx.com/docs/houdini/news/22/vellum.html), page read).
- Release: build 22.0.368, about three weeks after the June keynote. Houdini 22 "drops the OpenGL renderer"
  for a Vulkan viewport (GPU subdivision, volumetric fog). Windows support starts at 11, and macOS needs Apple
  silicon. Qt 5 builds are dropped, and a Linux Arm preview lacks FBX
  ([Digital Production](https://digitalproduction.com/2026/07/16/houdini-22-how-right-were-we/), 2026-07-16, page read).
- 80.lv, dated **2026-07-15**, says SideFX "has officially released Houdini 22"
  ([80.lv](https://80.lv/articles/houdini-22-is-out-now-bringing-native-gaussian-splats-new-ui-and-more), page read).
  CG Channel posted on 2026-07-16 (round one, page read). Settled: **2026-07-15**. The German roundup dated
  2026-07-21 is a later report.
- H21 (2025-08-27): KineFX became "Production-ready for all riggers and animators". The Autorig Builder drops
  rig components onto a viewport schematic and maps them to joints automatically. APEX, KineFX's graph
  framework, dates from 20.0
  ([CG Channel](https://www.cgchannel.com/2025/08/sidefx-just-released-houdini-21-check-out-its-5-key-features/), page read).
- Indie costs **$299 for 1 year or $449 for 2 years**. It is for entities with gross revenue up to $100K a
  year and under $1M in funding over 24 months. Up to 3 Indie and 3 Engine Indie licences, one artist on one
  machine at a time. Not allowed in the same pipeline as commercial Houdini
  ([Houdini Indie](https://www.sidefx.com/products/houdini-indie/), page read).
- Apprentice is free and "must be used on Non-commercial projects". Renders are watermarked outside `.picnc`
  and capped at 1920×1080; no third-party renderers; its assets do not work with Houdini Engine; a 30-day
  licence that renews online
  ([Apprentice](https://www.sidefx.com/products/houdini-apprentice/), page read).
- Houdini Engine for Unity and Unreal is free for commercial customers (up to 10 per studio). It "should only
  open HDA files", with no GUI, no Maya or Max plug-in and no batch. Indie customers get up to 3 Engine Indie
  licences; Apprentice users get none
  ([SideFX FAQ](https://www.sidefx.com/faq/question/houdini-engine-plugin-free-for-unity-and-unreal/), page read).

## Mixamo: markers, 2026 status, skeleton options

- Markers: "chin, wrists, elbows, knees, and groin", with symmetry on or off
  ([Monaverse docs](https://docs.monaverse.com/vrm-avatars/rigging-an-avatar), undated, page read).
  Overdare calls the last one "pelvis"
  ([Overdare docs](https://docs.overdare.com/manual/studio-manual/asset-and-resource-creation/using-mixamo-to-create-studio-animations), undated, page read).
  A vendor guide says to put "the groin at the hip joint center" (Tripo blog, snippet). Settled: one marker
  at the hip centre. Mixamo's own UI label could not be read (it needs an Adobe login), but three of four
  sources call it "groin".
- Skeleton options:
  - users describe a "standard 65-joint skeleton" and "3 chain Fingers" and "2 chain Fingers" variants
    ([Adobe community](https://community.adobe.com/t5/mixamo-discussions/the-skeleton-has-1-finger-on-each-hand-although-i-want-all-fingers/td-p/12029210), 2021-05-11, page read);
  - another user set "skeleton LOD to no fingers"
    ([Adobe community](https://community.adobe.com/t5/mixamo-discussions/auto-rigging-part-doesn-t-work/td-p/11758306), 2021-01, snippet);
  - no official list of the Skeleton LOD options was found.
- Status in 2026:
  - Adobe's Mixamo status was "up", with "0 outages in the last 30 days" as of 2026-10-29
    ([IncidentHub](https://incidenthub.cloud/status/adobe/creative-cloud-mixamo), page read; an aggregator
    reading Adobe's status page);
  - a multi-day outage began 2025-06-16. A support agent reportedly said "Mixamo is not supported anymore",
    and no Adobe staff reply was visible. A user reported it "down today" on 2026-04-23
    ([Adobe community](https://community.adobe.com/t5/mixamo-discussions/mixamo-down/m-p/15377556), from 2025-06-18, page read);
  - IsDown logged an outage of about an hour on 2026-07-24 (snippet);
  - no official 2026 statement from Adobe was found.
- Terms:
  - Adobe's helpx Mixamo FAQ returned 403 (blocked, not worked around);
  - a 2022 community post by a non-staff member ("TylerG 3D") says the only thing users may not do is
    "distribute the raw character and animation files", and that Mixamo content can't be used for "training
    machine-learning models"
    ([Adobe community](https://community.adobe.com/questions-696/mixamo-faq-licensing-royalties-ownership-eula-and-tos-589400), 2022-09-29, page read).
    Not an official source.

## Daz Studio: version 6, and how JCMs are authored

- "Daz Studio 6 is available now": the press release dated 2026-06-04 (paid placement via GlobeNewswire).
  Features: faster loading, background texture loading, content organisation, viewport work, strand-hair
  editing, newer NVIDIA GPUs, adaptive displacement, and "Victoria AI Chat"
  ([press release copy](https://pr.davisjournal.com/article/DAZ-3D-Launches-Daz-Studio-6-the-Next-Generation-of-Its-Flagship-3D-Creation-Platform/6a21ab39e80eb70d15dfa3cc), page read).
- Daz's own page: "Free to download and try", installed through DIM
  ([daz3d.com/introducing-studio-6](https://delorean.daz3d.com/introducing-studio-6), undated, page read).
- Technical highlights ([Daz blog](https://hpcl.daz3d.com/blog/daz-studio-6-technical-highlights), undated, page read):
  - "migration to the Qt6 framework", an updated viewport architecture, a rebuilt DrawStyle system;
  - Iray 2025.0.3; 3Delight "retired"; Blackwell (RTX 50) support;
  - scripting moves from ECMAScript 5.1 to ES2016;
  - the AI chat needs an internet connection.
- Name: the forum thread that began in April 2025 with the "Daz Studio 2025" alpha builds (6.25.2025.x, the
  last on 2025-12-19) is now titled "Daz Studio 6 Beta" (6.26.2026.x builds). Staff: "Older plugins do not
  work at all". Windows needs NVIDIA driver R570; macOS x86 needs SSSE3. The stable 4.x line continued with
  4.24.0.4 (2025-12-29)
  ([Daz forum](https://www.daz3d.com/forums/discussion/728111), page read). No sentence that says "renamed"
  was found.
- Assessment: "Daz Studio 2025" was the working name of Daz Studio 6. Evidence: the same thread, the same
  6.25 version line, and the same feature set.
- JCM authoring, the forum method:
  1. pose the joint to the target angle and set the corrective morph to 100%;
  2. in Edit Mode on the Parameters tab, use "Show in Property Hierarchy";
  3. drag the joint's rotation onto the morph's "1st Stage Controller";
  4. apply ERC Freeze so the morph blends in instead of snapping
  ([Versluis](https://www.versluis.com/2021/08/jcms/), 2021-08, page read).
- ERC means "Extended Remote Control". An older method uses ERC Freeze alone to link a pose to morph values
  ([Daz forum](https://www.daz3d.com/forums/discussion/comment/69208/), snippet). A morph sculpted on a posed
  figure elsewhere is loaded through Morph Loader Pro with "Reverse Deformations" so the pose is taken out
  (Daz forum threads, snippet).
- DSON file types: `.dsf` is the "DSON Support File" (called "Daz Scene Format" before 4.5) and `.duf` the
  "DSON User File". Daz Script 2 uses `.dsa` (ASCII), `.dsb` (binary) and `.dse` (encrypted); Daz Script 1
  (`.ds`) is deprecated
  ([Daz docs](https://docs.daz3d.com/public/software/dazstudio/4/referenceguide/tech_articles/file_extensions/start), page read).
  The DSON spec is version 0.6.1.0, "simple to parse due to its JSON syntax"
  ([DSON spec](http://docs.daz3d.com/public/dson_spec/start), page read).

## Substance 3D Painter: JavaScript vs Python plugins, price, Linux

- The plugins page still says plugins "are wrote in Javascript and can be combined with the QML language"
  ([plugins](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/features/plugins/plugins), 2026-10-08, page read).
- When Python arrived in 2020.1: "The old JavaScript API will remain in the software, but no new features will
  be added to it". No "deprecated" wording
  ([CG Channel](https://www.cgchannel.com/?p=114219), 2020-04-23, page read).
- 12.0 (2026-03-09): "JavaScript API" to 1.1.20, Python to 3.13, Qt to 6.8.6
  ([12.0 notes](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/release-notes/version-12-0), page read).
- 10.1 (2024-09): the Qt 6 move affected both plugin kinds. JavaScript plugins were moved to a subfolder and
  must be copied back by hand ([10.1 notes](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/release-notes/old-versions/version-10-1), snippet).
- Python plugins:
  - "plugins" is the JavaScript folder; Python plugins go under `python/plugins`;
  - `start_plugin()` adds UI, and `close_plugin()` removes it with `delete_ui_element`;
  - the tutorial still imports PySide2
  ([tutorial](https://experienceleague.adobe.com/en/docs/substance-3d-dev/painter-python/tutorials/create-a-python-plugin), 2026-07-09, page read).
- Python API 0.3.5 modules: project, layerstack, export, baking, event, ui, resource, js, textureset and more
  ([API overview](https://experienceleague.adobe.com/en/docs/substance-3d-dev/painter-python/api/api-overview), 2026-09-17, page read).
  12.1 widened the geometry-mask API
  ([12.1 notes](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/release-notes/version-12-1), 2026-06-22, page read).
- Price: Substance 3D Texturing $24.99/month or $249.99/year; Collection $59.99/month or $599.99/year;
  perpetual $199.99 on Steam
  ([CG Channel](https://www.cgchannel.com/2026/10/adobe-releases-substance-3d-painter-12-2/), 2026-10-25, page read).
- Platforms, official ([system requirements](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/getting-started/system-requirements), 2026-10-19, page read):
  - Windows 11 64-bit (23H2–24H2);
  - macOS 15 minimum;
  - Linux: "Enterprise: RHEL 8 and RHEL 9", plus Ubuntu 22.04 for the Steam edition.
- GPUs, from the same page:
  - NVIDIA from RTX 2060 Super;
  - AMD from RX 5700 XT;
  - Intel on Windows only ("Linux is unsupported");
  - Apple from M1;
  - 8 GB VRAM minimum.

  CG Channel's 12.2 article gives Linux as RHEL 8.6/9.2+ and Ubuntu 22.04+ (page read).
- Steam users report Painter 2026 failing on Ubuntu 22.04/24.04, Debian 12 and Fedora 43 for missing
  libraries ([Steam forum](https://steamcommunity.com/app/4329260/discussions/0/796712966523263676/), snippet).

## Marvelous Designer: the Personal licence's commercial terms

- The pricing page:
  - Personal is "For independent designers and creators who make digital garments", $23.3/month billed
    annually (≈$280/year);
  - Indie is "For small studios and agencies with up to 5 users", price on application;
  - Enterprise Team is $2,000/seat/year ($2,300 with Linux); Enterprise Single is $199/seat/month;
  - no commercial-use wording on any plan
  ([marvelousdesigner.com/pricing](https://www.marvelousdesigner.com/pricing), page read).
- The support article "What is the difference between Personal and Enterprise License"
  ([support.marvelousdesigner.com](https://support.marvelousdesigner.com/hc/en-us/articles/47358297616153-What-is-the-difference-between-Personal-and-Enterprise-License)
  returned 403). Search snippet: "freelancers are allowed to use personal licenses, but all other companies
  (studios, game companies, research companies, etc.) must purchase enterprise licenses". If a company buys
  Personal licences, access "may be restricted or terminated without prior notice".
- Indie eligibility differs by source:
  - the pricing page says "up to 5 users";
  - CG Channel says "at least two staff and under $500,000/year in earnings"
    ([CG Channel](https://www.cgchannel.com/?p=175258), 2026-04-20, page read);
  - Digital Production: a revenue threshold "specified by CLO", and the licence is not "a learning or
    non-commercial edition"
    ([Digital Production](https://digitalproduction.com/2026/01/28/marvelous-designer-adds-indie-pricing-quietly), 2026-01-12, page read).
- Licence: CLO EULA, proprietary. Commercial use: conditional. Personal covers freelancers' commercial work;
  companies need Enterprise or Indie (from the snippet; the page itself was blocked).

## API shapes: Maya, MotionBuilder, Cinema 4D, Blender

**Maya (Python `maya.cmds` and OpenMaya API 2.0; C++ API)**
- `MPxCommand` is the "Base class for user commands" and "the proxy class for creating MEL commands through
  the API":
  - `doIt` sets up class data and calls `redoIt`;
  - `redoIt` "should do the actual work … based on the internal class data only";
  - `undoIt` reverses it;
  - `isUndoable` (default false) decides whether Maya keeps the instance for its undo manager;
  - syntax goes through `MArgDatabase` and `MArgParser`; registration through `MFnPlugin::registerCommand()`
  ([MPxCommand ref](https://help.autodesk.com/cloudhelp/2018/ENU/Maya-SDK/cpp_ref/class_m_px_command.html), 2018 docs, page read).
- Events: `MEventMessage.addEventCallback` returns an id. Event names come from `getEventNames` or
  `scriptJob -listEvents`, and removal is through `MMessage.removeCallback`. "All callbacks that are
  registered by a plug-in must be removed by that plug-in when it is unloaded", or Maya hits a fatal error
  ([Maya 2026 API ref](https://help.autodesk.com/cloudhelp/2026/ENU/MAYA-API-REF/py_ref/class_open_maya_1_1_m_event_message.html), page read).
- UI: Maya moved "from Qt5 and PySide2 to Qt6 and PySide6" in 2025; VS 2022 17.8.3+, Xcode 14.3+, CMake
  3.27.3+ ([Autodesk blog](https://blog.autodesk.io/maya-2025-api-update-guide/), 2024-03-26, page read).
- Maya, 3ds Max and MotionBuilder 2027: Python 3.13.3, PySide and Qt 6.8.3, C++20, VS 2022, gcc 14.2 on
  Linux, FBX "2020.latest". Maya 2026 used Python 3.11.9 and PySide 6.5.3
  ([alignment page](https://aps.autodesk.com/developer/overview/me-vfx-platform-alignment), undated, page read).

**MotionBuilder (Python `pyfbsdk`; C++ Open Reality SDK)**
- `FBSystem` "Provides access to the underlying system, and the MotionBuilder scene". Events:
  - `OnUIIdle`, for light work about once every few frames;
  - `OnVideoFrameRendering`;
  - `OnConnectionNotify`, `OnConnectionDataNotify`, `OnConnectionStateNotify`, `OnConnectionKeyingNotify`
  ([Open Reality ref 2026](https://help.autodesk.com/cloudhelp/2026/ENU/MOBU-CPP-API-REF/class_f_b_system.html), page read).
- Undo: `FBUndoManager`. "All undo/redo related functions should only be called inside UI event callback".
  `TransactionBegin` and `TransactionEnd` are paired around `TransactionAddModelTRS`,
  `TransactionAddProperty` and `TransactionAddObjectDestroy`; also `Undo`, `Redo`, `Clear`. Events:
  OnUndo, OnUndoCompleted, OnRedo, OnRedoCompleted
  ([Python ref 2026](https://help.autodesk.com/cloudhelp/2026/ENU/MOBU-PYTHON-API-REF/classpyfbsdk_1_1_f_b_undo_manager.html), page read).
- Mocap pipeline: "A Marker set links optical motion data to the Actor asset". The markers should load "in
  a T-stance facing the positive Z-axis". The Actor then becomes the motion source of a characterised
  (HumanIK) character
  ([MotionBuilder help 2026](https://help.autodesk.com/cloudhelp/2026/ENU/MotionBuilder-Character-Animation/files/Character-Animation/Actor-assets/Marker-sets/GUID-BA14C51F-20A1-4305-9273-E44022B8D389.html), page read).
- HumanIK is a "full-body inverse kinematics (IK) solver and retargeter". Each character needs an HIK
  definition, made and locked in the Definition tab. Source and target must both be HIK characters
  ([MotionBuilder help 2026](https://help.autodesk.com/cloudhelp/2026/ENU/MotionBuilder-Character-Animation/files/Character-Animation/GUID-5911BFC8-0DB4-4F59-B3DB-F02C65DBBCE6.html), page read).

**Cinema 4D**: see its section above (plugin hooks, `StartUndo`/`EndUndo`, `EventAdd`, `GeDialog`
resources, Python 3.11.4).

**Blender (bpy)**: from the source repo, because docs.blender.org refuses scripted reads.
- Integration is through registered classes (`bpy.types.Panel`, `Menu`, `Operator`), with
  `bpy.utils.register_class`. Add-ons need `register()` and `unregister()` "so it's possible to toggle add-ons
  and reload scripts while Blender runs". Operators are called as `bpy.ops.<cat>.<name>()`
  ([info_overview.rst](https://projects.blender.org/blender/blender/raw/branch/main/doc/python_api/rst/info_overview.rst), main, measured).
- Operator limits: they "can't pass data such as objects, meshes or materials" (they use the context). The
  return value is only success or cancel. `poll()` failures say little, except where
  `poll_message_set` is used
  ([info_gotchas_operators.rst](https://projects.blender.org/blender/blender/raw/branch/main/doc/python_api/rst/info_gotchas_operators.rst), measured).
- Undo: "Any operator modifying Blender data should enable the 'UNDO' option". Returning `{'CANCELLED'}`
  makes no undo step. Without UNDO the stack may be corrupted, "even … data corruption and crashes". For
  complex cases there is a manual `bpy.ops.ed.undo_push`
  ([bpy.types.Operator.1.py](https://projects.blender.org/blender/blender/raw/branch/main/doc/python_api/examples/bpy.types.Operator.1.py), measured).
- Events:
  - **handlers**: `bpy.app.handlers.frame_change_pre.append(fn)` and similar
    ([bpy.app.handlers.0.py](https://projects.blender.org/blender/blender/raw/branch/main/doc/python_api/examples/bpy.app.handlers.0.py), measured);
  - **msgbus**: subscriptions to RNA property changes. They fire for API and UI edits, not for viewport
    moves or animation. Callbacks wait until operators finish; "Changes done from msgbus callbacks are not
    included in related undo steps"
    ([bpy.msgbus.1.py](https://projects.blender.org/blender/blender/raw/branch/main/doc/python_api/examples/bpy.msgbus.1.py), measured).
  - Timers (`bpy.app.timers`) also exist (example files listed, measured).
- Blender 5.2 animation release notes ([source](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.2/animation_rigging.md), measured):
  - Copy Constraints in Ctrl+L;
  - Auto IK with non-connected parents;
  - `action.select_by_type`, and Duplicate and Rename for bones;
  - "Only Insert Available" on by default;
  - in-betweens in Object Mode, and playback loop modes.

  This **confirms** round one's snippet.
- Assessment: the four undo models differ:
  - Maya: command objects (do/undo/redo);
  - MotionBuilder: transactions inside UI callbacks;
  - Cinema 4D: document undo groups plus a queued redraw event;
  - Blender: the operator flag plus snapshot undo.

  Maya's command object is the closest to "every edit is a command", which JustStage's API plan needs.

## Conflicts from round one, settled

| Conflict | Result |
|---|---|
| ZBrush GoZ targets (2026 vs 2027 hosts) | **Not fully settled.** Maxon's What's New: 2026.2.1 GoZ sends to "Maya 2026 and 3DS Max 2026" ([maxon.net](https://www.maxon.net/en/zbrush/new), page read). Maxon's GoZ list: 3ds Max 2016–2026 and Maya 2015–2026 ([interoperability](https://www.maxon.net/zbrush/features/interoperability), page read). Maxon's 2026.2.1 release notes (2026-06-17): "GoZ for Autodesk Max and Maya 2027 versions" ([support.maxon.net](https://support.maxon.net/hc/en-us/articles/15780513877788-ZBrush-2025-0-1-Release-Notes), 403, snippet). Assessment: the release notes are the most specific and probably right; the marketing pages lag. The GoZ list names no Blender. |
| Houdini 22 release date | **2026-07-15.** 80.lv's article of that date says it is out (page read); build 22.0.368 (Digital Production, page read); CG Channel posted 07-16; the 07-21 roundup is later. |
| ArtCraft licence | **Dual MIT OR Apache-2.0.** The repo has `LICENSE-MIT` and `LICENSE-APACHE`. The README says "dual-licensed under MIT or Apache-2.0, at your option", and so does NOTICE. GitHub's SPDX field reports only Apache-2.0 (measured). NOTICE: the ArtCraft name and logos are excluded, some files are third-party (ammo.js zlib, Font Awesome CC BY 4.0, OFL fonts), and some third-party files are "not licensed" by the repo (measured). |
| MetaTailor's free export count | **5 FBX exports a month** ([metatailor.com/pricing](https://www.metatailor.com/pricing), page read). It was 10 in 2024-10. Pro is $35/month or $336/year with a "Limited Commercial License"; Enterprise $50/month or $500/year. The site now shows **v2.6** ([metatailor.com](https://www.metatailor.com/), page read). The FAQ: "not available for Mac users" ([FAQ](https://www.metatailor.com/faq), page read). Digital Production: Windows-only, fitting by a "proprietary adaptive mesh approach", bridges on Pro only (2026-02-05, page read). |
| Is MetaTailor built on Unity? | **Not findable.** Neither metatailor.com (home, FAQ, pricing), CG Channel, Digital Production nor search results name the app's engine. Unity appears only as a bridge-plugin target. A search for Unity runtime files in MetaTailor found nothing. Checking an install was ruled out (no downloads). |

## Round one's snippet-only facts, re-checked

| Round-one fact (snippet) | Now |
|---|---|
| Cascadeur 2026.1: AI Root Motion, penetration cleaning, AutoPhysics constraints, UE Live Link 5.5–5.7, Filament | **Confirmed** ([Digital Production](https://digitalproduction.com/2026/04/09/cascadeur-2026-1-adds-unreal-live-link-filament-rendering-and-ai-root-motion/), page read; [Cascadeur blog](https://cascadeur.com/blog/view/cascadeur-2026-1-new-renderer-ue-live-link), page read). Root Motion is a diffusion model that takes "motion signatures from reference animation"; Live Link was funded by an Epic MegaGrant (blog). **Superseded** by 2026.2, 2026-08-06 (CG Channel, page read). |
| Cascadeur Python 3.8, `csc`, managers; `call_action` to be removed | Python 3.8, `csc`, Action/Scene/Dialog managers **confirmed**. Commands are files with `command_name()` and `run(scene)`; "Every change is recorded in the command history" and can be undone ([help](https://cascadeur.com/help/tools/animation_tools/python_scripting_in_cascadeur), page read). The `call_action` removal and "mainly rig generation" remain **unverified** (not on that page). 2026.2 adds PySide/QML custom UI and stubs ([blog](https://cascadeur.com/blog/view/cascadeur-2026-2-animation-layers-easing-new-languages), page read). |
| AI Inbetweening 88-frame limit (2025.1) | 88 was 2025.1 (release-notes snippet; CG Channel said 89, snippet). **Now 120**: "The distance between 2 nearest keyframes should not be longer than 120 frames" ([help](https://cascadeur.com/help/category/278), page read). |
| Cascadeur 2025.3: inbetweening in Timeline Interpolation; quadruped AutoPosing and Quick Rigging | **Confirmed**, labelled Alpha. 2025.3 also had a Filament preview for Windows only ([blog](https://cascadeur.com/blog/view/cascadeur-2025-3-new-inbetweening-quadrupeds), page read). |
| Cascadeur platforms and prices | Windows 10+, Ubuntu 20.04+, macOS 13.3+. Free is "not licensed for commercial use" and saves only .casc. Indie $19/month or $96/year (under $100k); Pro $49/month or $396/year. **New:** paid tiers become perpetual after one year (rent-to-own) (CG Channel 2026-08-06, page read). |
| MD 2025.0 auto-conversion of Daz, Mixamo, CC and MetaHuman | **Confirmed**: these convert "automatically when their joint naming matches", others map by hand. Also keyframing, IK joint mapping, Auto Convert to Motion (FBX to MTN), experimental fur. $39/month or $280/year Personal; Windows 10+ and macOS 12+ ([CG Channel](https://www.cgchannel.com/2025/04/clo-virtual-fashion-releases-marvelous-designer-2025-0/), 2025-04-30, page read). |
| MD 2025.2: MetaHuman DNA import, pleats, patterns to trims, EveryWear FBX | **Confirmed** ([Digital Production](https://digitalproduction.com/2025/11/18/marvelous-designer-2025-2-metahumans-pleats-keyframes/), page read). Keyable fabric properties added. "GPU soft-body" is **not** in that article. |
| MD 2026.0: 3D Pencil, Lacing, Toon Shader, glTF, Template-Based Rigging | **Confirmed**, released 2026-04-20. glTF and VRM avatar import; the "experimental Rig Template system" adds joints to wide garments; blendshapes on imported avatars ([CG Channel](https://www.cgchannel.com/?p=175258), page read). |
| MD Python API and .py plug-ins | **Confirmed**. Modules EXPORT_API, IMPORT_API, FABRIC_API, PATTERN_API, UTILITY_API ([list](https://developer.marvelousdesigner.com/list.html), page read, partly). `.py` plug-ins are registered in the Plug-in Manager on Windows and macOS ([register](https://developer.marvelousdesigner.com/register.html), page read). Changelog: `.py` plug-ins and built-in pip in 2025.1.107; `RunAnimationRecording` in 2025.0.157; a `gui_api` (dialogs, docks) documented in 2026.1 docs but "not in the current 2026.1 release yet" ([changelog](https://developer.marvelousdesigner.com/changelog.html), undated, page read). |
| MD Linux, with its Python API | **Confirmed**: due 2025-09-30, RHEL 9 and Rocky 9. The Python API does batch import and export and controls simulation parameters ([Digital Production](https://digitalproduction.com/2025/09/30/marvelous-designer-finally-sews-itself-into-linux/), page read). |
| MetaTailor 2.5 one-click bridges | **Confirmed** for Unreal, Unity and CC4/CC5, Pro only ([Digital Production](https://digitalproduction.com/2026/02/05/metatailor-adds-engine-bridges-and-less-fbx-fatigue/), page read). |
| Houdini H21 Autorig Builder; Engine free for UE/Unity; Indie $299; Apprentice non-commercial | All **confirmed** (Houdini section, page read). |
| C4D 2027.0 from 2026-10-14, no character tools | **Confirmed** (CG Channel 2026-10-15, page read). |
| C4D MCP undo and logging | Undo **confirmed**: "every action it takes appears in the undo stack" (CG Channel, page read). Logging **not confirmed** (only Creative Bloq's snippet). |
| C4D C++: CMake, C++20, "binary incompatible" | **Confirmed** (C++ migration page, page read). The compiler list (VS 2022, Xcode, GCC/Ninja) is not on that page. |
| Maya 2027.1 OTIO | **Confirmed**: Sequencer supports OTIO (CG Channel 2026-05-21, page read). Import or export not stated. |
| HumanIK definitions | **Confirmed** (MotionBuilder help 2026, page read). |
| MotionBuilder Actor-to-Character mapping | **Confirmed** from Autodesk's own help; it replaces the third-party MocapOnline source. |
| Daz "Daz Studio 2025" alpha; 3Delight phased out | **Resolved**: DS 2025 became DS 6, and 3Delight is "retired" (Daz section, page read). |
| Daz DSON `.duf` / `.dsf` | **Confirmed** (Daz docs, page read). "Pure data, no scripting" is still forum-only (snippet). |
| MetaHuman 5.7 (Creator on Linux and macOS; Python and Blueprint API) | **Confirmed** by CG Channel 2025-11-12 (page read). metahuman.com's 5.7 page redirects to the Epic login; dev.epicgames.com's 5.7 notes rendered only a 5.8 title. |
| MetaHuman licence summary (CG Channel 2025-06-04) | **Confirmed** (page read); see the MetaHuman section. |
| ZBrush 2026.1 retopology brush; iPad photogrammetry | **Confirmed**: a manual Retopo brush; iPad photogrammetry needs an A14 or later ([CG Channel](https://www.cgchannel.com/2025/12/maxon-releases-zbrush-2026-1-and-zbrush-for-ipad-2026-1/), 2025-12-04, page read). A "Smooth Retopology Brush" is **not** in the article. |
| Substance 12.1 and 12.0 notes | **Confirmed**: 12.1 (2026-06-22) automatic rebaking, skew-correction painting, OpenPBR 1.1 as the default; 12.0 (2026-03-09) Warp to Geometry, Flatten (both pages read). |
| Substance price and Linux (GG.deals) | **Replaced** by CG Channel 2026-10-25 and Adobe's requirements page (both page read). |
| Mixamo FAQ, markers, status | Mixamo section. helpx is still 403. |
| Move.ai credit prices (6 and 12 credits a second) | **Out of date**: now 1 and 2 credits a second (Move One pricing, page read). |
| DeepMotion SayMotion | **Confirmed**: open beta from 2024-03-20; v1.5 2024-06-29; FBX, GLB and BVH export; inpainting ([CG Channel](https://www.cgchannel.com/?p=156294), page read). |
| Flow Studio pricing | **Partly confirmed**: a free tier at SIGGRAPH 2025, Lite cut "from $20 to $10", a new Standard tier ([Autodesk news](https://adsknews.autodesk.com/en/?p=53687), 2025-08-12, page read). The credit costs and the free tier's watermark are still from the aggregator only. |
| Blender 5.2 animation and rigging notes | **Confirmed** from the developer-docs source repo (measured). |
| Nomad Sculpt desktop: $35 for 2 computers | **Confirmed**: "one-time purchase", about $35 for one key for 2 computers; Windows, macOS, iOS and Android ([nomadsculpt.com](https://nomadsculpt.com/), page read). |

---

## Couldn't verify / open

- **MetaHuman licence text**: `metahuman.com/license` redirects to the Epic login, and
  `unrealengine.com/eula/mhc` returns 403. Neither was worked around. **The user reads these.** Only the
  snippet and the press summaries above are in hand.
- **MetaHuman offline auto-rig**: nothing in 5.8 shows one. Whether an Epic account or entitlement gates the
  cloud jobs is not stated by Epic (one forum user suspects it).
- **Is MetaTailor built on Unity?** Not findable. Tried: metatailor.com home, FAQ and pricing; CG Channel and
  Digital Production; searches for Unity runtime traces. Installing was not allowed.
- **ZBrush GoZ 2027 hosts**: rests on a release-notes snippet (support.maxon.net, 403). Maxon's marketing
  pages still say 2026.
- **Mixamo**: there is no official Skeleton LOD list (helpx 403; the app needs an Adobe login). There is no
  official 2026 statement on Mixamo's status.
- **Marvelous Designer Personal**: the commercial-use wording comes from a snippet of a 403 support page.
  The Indie revenue threshold is not published, and sources disagree on team size (up to 5 users vs at least
  2 staff and under $500k).
- **Style3D**: no 2026 price list (the pricing page 404s; blog figures conflict); free-tier terms unclear;
  Simulator's supported UE versions conflict (4.27+ / 5.0–5.4 / 5.0+).
- **Avaturn**: its terms page returned 404, so licence and commercial terms for avatars are unknown. The
  in3D link rests on a competitor's claim.
- **Move AI**: the old Move Live pages are gone (404). What Vicon will keep of Genesis and Move One is
  unannounced. Whether Genesis's finger tracking runs in real time at full quality is not stated beyond
  "Genesis Live" in the notes.
- **Rokoko**: Apple-silicon-only rests on a snippet (support page 403).
- **Cascadeur**: the `call_action` removal and "the API is mainly for rig generation" still rest on round
  one's snippets.
- **Cinema 4D**: whether the MCP server logs actions locally is unconfirmed; the C++ compiler list is not on
  the migration page.
- **Substance 3D Painter**: whether JavaScript plugins will ever be formally deprecated (Adobe only says "no
  new features"); the Python plugin tutorial still shows PySide2 against Qt 6.8.6.
- **3DCoat**: whether Free Learning mode allows commercial use; whether the Python version is still 3.8.10
  in 2026.
- **Daz**: there is no single sentence from Daz that says "Daz Studio 2025 was renamed Daz Studio 6"; it is
  inferred from the thread and the version line.
