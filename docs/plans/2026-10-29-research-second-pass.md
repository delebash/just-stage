# Research second pass — one session per area, each with its own search budget

Written 2026-10-29 by the round-one session. Round one's 8 agents shared one session's 200 WebSearch calls and
ran out partway (RESEARCH §13), so every notes file has gaps the cap cut. The user: "i dont want to search to be
truncated and give us limited data", then "once you verify how it works if each session has new limit then we
open 1 session per agent" — verified: a new conversation gets a fresh 200 (TASKS).

## How to start a session (the user)

1. Open a terminal at `E:\Dev\3D` and run `claude`. Use Opus 5.5 at xhigh (`/model`, `/effort`) — the approved
   research setup (TASKS, "Model").
2. Paste one line, with that session's number:

   `go: run second-pass session S<N> — read E:\Dev\3D\just-stage\docs\plans\2026-10-29-research-second-pass.md and follow its rules and section S<N>`

The eight sessions don't depend on each other and can run at the same time.

## Rules for every second-pass session

- **Read first:** `just-stage/AGENTS.md`, `docs/dev/README.md`, your area's section of `docs/dev/RESEARCH.md`,
  and your round-one notes file (named in your section). Facts there marked *page read* or *measured*: don't
  re-derive them. Facts marked *search snippet only*: re-check each at its page.
- **Scope, as the user decided 2026-10-29 (TASKS):** NVIDIA Omniverse is out; anything that only comes paid is
  out; core parts (renderer, engine, physics, editor) that run on one GPU vendor only are out, and optional
  parts (AI models, mocap) are labelled with the GPU vendors they run on (NVIDIA / AMD / Intel / Apple); Unity
  is out; Unreal is in; free-but-closed options get normal rows with their terms in plain words. Licences are
  one line each — licence, commercial use (yes / conditional / no / unclear), link — never legal analysis; the
  trademark check is dropped. A licence is a label, never a reason to drop an option.
- **Do the research yourself in this session — no subagents.** The 200-search budget is per conversation and
  shared with subagents; it refills at about 100 calls an hour. Spend searches on discovery; read pages with
  WebFetch, GitHub's API and raw files, Hugging Face's API, arXiv abstract pages and docs source repos.
- **Never work around a block or a bot check** (no spoofed user agents, no archive copies of a page that refused
  you). If a page refuses scripted access, use another source, or list it as blocked.
- **Clean-room:** behaviour and public docs only; never copy code, shaders, meshes, morphs or assets; short quotes
  only.
- **No downloads** of installers, models or datasets. Scratch files only in your session's scratchpad on F:,
  never on C:. Any JavaScript you run is ES modules (`import`, never `require`).
- **Output:** write `docs/plans/2026-10-29-research-<area>-pass2.md` (the name is in your section) in round
  one's format — "Top findings" (at most 15, each with its source), then one heading per gap item with one fact
  per bullet (source URL, the source's date, *page read* / *search snippet only*), "Assessment:" lines kept apart
  from facts, and "Couldn't verify / open" last. Commit **only that file** (if `index.lock` is in use, wait and
  retry; never delete it). Don't edit RESEARCH.md or TASKS.md — the lead distills all eight passes at once, so
  parallel sessions never conflict.
- **Done when** every gap item in your section is answered with a source, or marked "not findable" with what was
  tried. Then tell the user, in under 250 words: your file, the findings that change the picture, what is still
  open.

## S1 · CC5 — round one: `2026-10-29-research-02-cc5.md` → write `2026-10-29-research-02-cc5-pass2.md`

- Praise and complaints from outside Reallusion's own forum: r/Reallusion and other Reddit threads, Polycount,
  CGSociety, ArtStation, YouTube reviews, 80.lv; the Virtual Production Insider review.
- Open the manual pages behind the inventory rows that rest on topic titles only (about 60% of the
  manual-sourced rows) — head and face, morphs, skin, hair, clothing, rigging, mesh tools and the pipeline
  first.
- Exact base-mesh counts per subdivision level (vertices and faces at SubD 0/1/2) and for each separate mesh
  (body, eyes, teeth, tongue, lashes, occlusion, tearline); reconcile the published 13,580 / 17K / 70K / 80K /
  240K+ figures.
- The full bone list and count per part (body, face, twist) beyond "101 / 54 / 22" and `CC_Base_`; the facial
  bone list.
- The UDIM tile → material mapping of CC3+ and CC5 HD.
- Prices: SkinGen Premium, ZBrush Face Tools, Iray, FashionGen, the CC5 Pro annual plan, PRIME, AI points.
- Whether Iray works in CC5 (the manual lists it; a staff post says no); whether the MetaTailor plugin works
  on CC5; CC5's Python and Qt versions; the viewport's graphics API.
- The native file formats (`.ccProject`, `.ccAvatar`, iAvatar): what is public about their structure.
- Whether a 5.12 exists; build numbers of 5.11, 5.13 and 5.2.
- Any link between Z-Weave and CC (the user named it).
- One licence line each for the CC5 EULA and the content licence tiers, if a page serves them as text.

## S2 · iClone — round one: `2026-10-29-research-03-iclone.md` → write `2026-10-29-research-03-iclone-pass2.md`

- Praise and complaints from outside Reallusion's forum and tracker: Reddit, independent forums, reviews.
- The Motion LIVE workflow (connect, characterise, calibrate, record, several actors) and each device's
  protocol (which stream over the network, which use vendor SDKs).
- Prices: PopcornFX, popVideo, BuildingGen, the current Unreal Live Link, LIVE FACE, Motion Link, the mocap
  device profiles.
- Third-party Python plugins on the Reallusion Marketplace (titles and what they add).
- Release dates of 8.1–8.5x; 8.7's date (forum 2026-01-26 vs build 2026-02-12).
- The Python API: the 2020 limits list against the iC8 classes, function by function; a list of iC8 events;
  whether the API can create tracks, layers and clips.
- How hair simulates (soft cloth or its own solver); the native particle parameters; how PopcornFX effects are
  edited and keyed inside iClone.
- The AI Mesh Generator: local or cloud, and its price.
- Morph Creator, Persona, Smart Accessory and Talking Style Editor — open their pages (round one saw titles
  only).
- One licence line each for the software EULA, ActorCore and Video Mocap's output terms, if served as text.

## S3 · Reference apps — round one: `2026-10-29-research-04-references.md` → write `2026-10-29-research-04-references-pass2.md`

- Not researched in round one: 3DCoat (sculpt, retopology, paint), Style3D (cloth), Unreal's Control Rig and
  Sequencer as the reference for an iClone-type timeline, Ready Player Me, Avaturn.
- MetaHuman: whether auto-rigging and texture synthesis run on Epic's servers; the MetaHuman licence text (its
  page needs an Epic login — say so if it stays unreachable); OpenRigLogic's licence files and what the repo
  holds.
- Maya MotionMaker (how it works); Move.ai Move Live (real time) and finger tracking; Rokoko Studio's platforms.
- Cinema 4D's price and Python plugin API; Houdini's HDK ABI rules, its `packages` JSON format and Houdini 22's
  Vellum changes.
- Mixamo: the marker list (groin vs pelvis), its 2026 status, skeleton options.
- Daz: whether "Daz Studio 2025" became Daz Studio 6; how joint-controlled morphs (JCMs) are authored.
- Substance 3D Painter: JavaScript vs Python plugins, price, Linux support. Marvelous Designer: the Personal
  licence's commercial-use terms.
- API facts left out of round one: Maya's Python and C++ APIs, the MotionBuilder SDK, Cinema 4D's Python API,
  Blender's bpy — the shape of each (commands, undo, events, UI hooks).
- Conflicts to settle: ZBrush GoZ targets (2026 vs 2027 hosts), Houdini 22's release date, ArtCraft's licence
  (Apache-2.0 vs MIT-or-Apache), MetaTailor's free export count, and whether MetaTailor is built on Unity.
- Re-check round one's snippet-only facts (Cascadeur 2026.1 among them).

## S4 · Open human bases — round one: `2026-10-29-research-05-bases.md` → write `2026-10-29-research-05-bases-pass2.md`

- Realism against CC5 and MetaHuman: any render comparisons, reviews or user showcases for MPFB2 / MakeHuman,
  Anny, MHR, CharMorph, Rocketbox, GNM.
- Mesh quality: deformation edge loops and subdivision behaviour for the MakeHuman base (hm08), MHR, SOMA-X and
  GNM; MHR's and GNM's face types (quads or triangles); GNM's vertex and expression counts; hm08's raw vertex
  count; MB-Lab's vertex and morph counts (from docs, without downloading its data).
- The licence of the AI checkpoints for UniRig, SkinTokens, Puppeteer and Make-It-Animatable (Hugging Face model
  cards); Make-It-Animatable's Mixamo training data.
- Free-but-closed terms: VRoid Studio's terms of use, Mixamo's FAQ, Daz Studio and Genesis 9 (not researched in
  round one), Blender's Rigify page (use the manual's source repo).
- Not researched in round one: Unreal's Mutable (Customizable Object) plugin, Bevy character creators, open
  strand-hair groom assets, Meshcapade's commercial SMPL terms, ATLAS.
- Conflicts to settle: Humanizer's licence (AGPL-3.0 file vs CC0 listing), Rocketbox's body-bone count (56 vs 53).
- GPU vendors for SOMA-X, UniRig, SkinTokens and LHM (CUDA only, or also ROCm / Metal / CPU).

## S5 · Engine routes — round one: `2026-10-29-research-06a-engine-routes.md` → write `2026-10-29-research-06a-engine-routes-pass2.md`

- Epic's own terms: try Epic pages that serve text (dev.epicgames.com documentation, epicgames.com legal pages).
  Round one's EULA wording ("may not contain … any Engine Tools") and pricing are search snippets only. If every
  Epic page refuses, list it — the user, who uses Unreal daily, reads it.
- Unreal: runtime exporters (glTF, USD, FBX) in a packaged app; morph-target limits; the 5.8 MCP plugin; what a
  packaged Unreal app may include (runtime only vs editor modules).
- Godot: MCP servers and other control channels; products built on Godot that are tools, not games (beyond
  Pixelorama, Material Maker, Dungeondraft).
- Products built on O3DE, Stride, Flax, Fyrox and Bevy (Tiny Glade's use of Bevy).
- Blender: GPU skinning (in 5.x or planned); the Vulkan default (5.1 vs 5.3); whether MIT add-on code counts as
  "GPL compliant" (one line from the FSF list, no analysis).
- O3DE: skin subsurface scattering; its Track View sequencer; export formats. Export from Stride, Fyrox and Bevy;
  Python bindings for Stride and Bevy.
- Flax: its full EULA — editor redistribution, and whether a Flax-based app may be open source.
- Bforartists 5.2.0: pre-release or release.
- Re-check round one's snippet-only facts.

## S6 · Own engine and layers — round one: `2026-10-29-research-06b-own-engine-and-layers.md` → write `2026-10-29-research-06b-own-engine-and-layers-pass2.md`

- UI toolkits not checked: GTK 4 and Flutter desktop for a 3D editor; Slint's docking and accessibility; wxAUI.
- UI test automation for Qt (Qt Test, Squish, accessibility-based drivers) — how an AI agent drives a Qt app.
- Build-time evidence: Rust vs C++ for a large 3D codebase.
- Mesa lavapipe conformance for headless image tests; anything for Metal.
- Ray tracing on Metal per library: Diligent (MoltenVK only — out?), The Forge, Wicked.
- Big apps using WebAssembly plugins (Microsoft Flight Simulator and others) and what they learned.
- Unreal's Python scripting (editor only or runtime); Godot's C# hosting.
- The licence files GitHub marks NOASSERTION: ozz-animation, assimp, CGAL, Magnum, Ogre-Next, mitsuba3, glm.
- The UI toolkits and core languages of Cascadeur and Marvelous Designer; public effort figures (team size,
  years) for Maya, Houdini, Unreal's editor, Blender.
- Re-check round one's snippet-only facts (Cascadeur, Marvelous Designer, Cinema 4D, Slate, RLPy, Unreal 5.8
  MCP, Multi-SWE-bench, SWE-Sharp-Bench, PEP 779, WASI 0.3, Avalonia 12 accessibility, Slint's wgpu underlay,
  Dear ImGui 1.92 DPI).

## S7 · Building blocks — round one: `2026-10-29-research-07-building-blocks.md` → write `2026-10-29-research-07-building-blocks-pass2.md`

- **The jobs with no open option found — search deeper, or confirm none exists:** pattern-and-sew garment
  making (a Marvelous Designer equivalent), fitting any garment to any body (a MetaTailor equivalent), physics
  tools like Cascadeur's, a ZBrush-class sculpt library, a texture baker, an FBX writer, a cross-vendor GPU
  garment-cloth library.
- VRAM needs (model cards, issues, papers) for SAM 3D Body and Objects, Stable3DGen, Step1X-3D, Puppeteer,
  MagicArticulate, Make-It-Animatable, WHAM, GVHMR, NLF, GENMO, MoMask, MDM, T2M-GPT, ChatGarment, DiffLocks.
- GPU vendors for the PyTorch models (AMD ROCm, Apple MPS, DirectML or ONNX ports) — TRELLIS, TRELLIS.2,
  TripoSG, PartCrafter, UniRig, SkinTokens, Audio2Face and the rest.
- CMU mocap's terms; Blender's dynamic topology and hair-curve grooming tools.
- Free-but-closed terms: Autodesk's FBX SDK EULA (including redistribution), Mixamo's terms of use, Live Link
  Face, Rokoko Studio's free tier, Cascadeur's free tier.
- Licences to resolve: the Rokoko Blender plugin (LGPL-3 vs MIT), Rhubarb Lip Sync, XR Animator, CameraHMR,
  DressCode, MotionGPT3, Noitom MocapApi, lightmapper, the VRM spec, CGAL's packages, KTX-Software.
- Algorithms and papers: VBD (Vertex Block Descent), XPBD, Stable Cosserat Rods, PSD/RBF correctives, Jimenez's
  eye rendering — what each gives JustStage and its open implementations.
- Not checked: neural retopology (DeepMesh, BPT, QuadGPT, Meshtron), Hi3D, Sony mocopi and VMC, OptiTrack NatNet
  and Vicon DataStream SDKs, the Live Link plugin's terms, TressFX 5.0, whether Godot's IK is in a stable
  release, MoonRay's GPU back-ends, PhysX's CPU/GPU feature split, OIDN's GPU vendors, Kenney and ambientCG,
  a quantised TRELLIS.2 at 6 GB, Pixal3D's VRAM.

## S8 · Standards — round one: `2026-10-29-research-08-standards.md` → write `2026-10-29-research-08-standards-pass2.md`

- Blender, from the manual's and the code's source repos (docs.blender.org refused scripted access): operator
  `poll` and `execute` rules, the undo system's internals, the extension manifest's permissions text, asset
  metadata fields, USD import of UsdSkel and blend shapes, the FBX importer's axis and bone options, the Rigify
  bone list, Blender's own axes and units.
- Not reached in round one: gRPC and Live Link as remote protocols; Houdini's `hou.undos`; Maya's `MPxCommand`
  undo; the HumanIK and Mixamo bone lists; the UE5 Mannequin bone list; MetaHuman's control counts; CC5's HD
  profile shape count; CC's Smart Gallery; Fab; the Reallusion content EULA (one line).
- MCP: confirm the removal of `initialize` at the spec itself.
- MetaHuman's terms: state both readings ("any engine" vs the DNA Calibration licence's Unreal/Twinmotion limit)
  with their sources — the user decides.
- UsdSkel: whether blend shapes carry `normalOffsets`; any AOUSD plan for a character or skeleton domain spec;
  UsdPhysics for cloth; USD BasisCurves for strand hair and Unreal's groom import format.
- Export-target facts: Unity's coordinate system (Unity is out as a base but stays an export target); VRM 1.0's
  bone local axes.
- Open FBX writers (any); the copy cost of WebAssembly plugins on large meshes (benchmarks or papers).

## After the eight passes (the lead)

One lead session reads the eight pass-2 files, distills them into RESEARCH.md, writes the one complete rec list
(every item researched and argued against, each piece standard with its doc link or NOT STANDARD), and shows it to
the user. Then the fresh Fable session writes the synthesis and the standards spec (TASKS, NEXT).

Not search gaps — these need something else:
- Measuring the route finalists on the RTX 2070 Super (a realistic head with strand hair, a skinned body,
  playback fps) — after the rec list names the finalists.
- Any terms page that refuses every scripted read (Epic's, MetaHuman's) — the user reads it.
