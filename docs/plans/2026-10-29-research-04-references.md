# Research 04 — feature references: how other apps do the jobs CC5 and iClone do (overlap only)

Researched 2026-10-29 for RESEARCH.md §4. Clean-room: behaviour and public docs only; short quotes only.

Labels on every fact: **[page read]** — the page was opened and read · **[snippet]** — search-result
snippet only, page not opened · **[measured]** — run from this machine (GitHub API, 2026-10-29).
Every fact carries its source URL and the source's date ("undated" when the page shows none).
"Assessment:" lines are my judgement, not facts.

The session-wide web-search budget ran out near the end (200 searches shared by every agent), so a few
items rest on snippets; they are listed under "Couldn't verify / open".

## Top findings

1. **MetaHuman's face-rig runtime and file format are now MIT.** With MetaHuman 5.8, Epic released
   RigLogic and DNA as open source under MIT, as OpenRigLogic
   ([GamesBeat, 2026-06-17](https://gamesbeat.com/epic-games-launches-metahuman-5-8-to-create-real-time-game-character-crowds/), page read).
   `EpicGames/OpenRigLogic`: created 2026-06-05, last push 2026-10-23, licence MIT, 304 stars
   ([GitHub API](https://api.github.com/repos/EpicGames/OpenRigLogic), measured).
2. **MetaHuman Creator has run inside the Unreal editor since UE 5.6** (out of early access, June 2025).
   It now covers bodies, mesh-to-MetaHuman, and capture from video, webcam and audio. Since 5.6 the EULA
   allows MetaHumans in "any engine or creative software"
   ([80.lv, 2025-06-04](https://80.lv/articles/explore-new-metahuman-features-in-unreal-engine-5-6), page read).
   5.8 added full-body mesh-to-MetaHuman for any topology, and Animator on Linux and macOS
   ([GamesBeat, 2026-06-17](https://gamesbeat.com/epic-games-launches-metahuman-5-8-to-create-real-time-game-character-crowds/), page read).
3. **Cinema 4D ships an official MCP server** (2026.4+, free). It is off by default and runs locally,
   with a separate opt-in for network use. It needs an access token, the user picks which tool groups an
   assistant may use, and Python execution can be controlled
   ([AEC Magazine, 2026-09-30](https://aecmag.com/visualisation/maxon-automates-cinema-4d-with-mcp-server/), page read).
   This is a proven reference for JustStage's planned MCP-over-commands with permissions.
4. **Houdini Engine is the model for "our tools inside other apps".** HAPI sessions run in-process,
   out-of-process, or on a remote server (HARS), with SessionSync
   ([HAPI docs, Engine 9.0](https://www.sidefx.com/docs/hengine/), page read, contents page only). H22
   ships plug-ins for UE 5.7/5.8, Unity 6.3/6.5, Maya 2027 and 3ds Max 2027
   ([H22 Engine notes, 2026-07](https://www.sidefx.com/docs/houdini/news/22/engine.html), page read).
5. **Houdini 22's KineFX/APEX treats rigs as reusable components.** Prebuilt rig templates move a whole
   rig onto a new character. It also adds Set Driven Keys, a 2D character picker, Motion Mixer nested
   clips, a "Retarget to Rig" recipe, and blend-shape sliders in 3D or screen space
   ([H22 KineFX notes, 2026-07](https://www.sidefx.com/docs/houdini/news/22/kinefx.html), page read).
6. **Cascadeur is the animation "improve or add" list:** AutoPosing, AutoPhysics, AI Inbetweening,
   AI Root Motion (style transfer from existing clips) and an Unreal Live Link (2026.1)
   ([Digital Production, 2026-04-09](https://digitalproduction.com/2026/04/09/cascadeur-2026-1-adds-unreal-live-link-filament-rendering-and-ai-root-motion/), snippet).
   Its Python API is thin: Python 3.8, aimed at rig generation, with `call_action` to be removed
   ([Cascadeur help](https://cascadeur.com/help/tools/animation_tools/python_scripting_in_cascadeur), undated, snippet).
7. **Marvelous Designer converts other apps' avatars automatically:** Daz, Mixamo, Character Creator
   and MetaHuman rigs (2025.0)
   ([MD support, 2025](https://support.marvelousdesigner.com/hc/en-us/articles/47358120307353-Marvelous-Designer-2025-0-2025-1-New-Feature-List), snippet).
   It imports MetaHuman DNA (2025.2)
   ([Digital Production, 2025-11-18](https://digitalproduction.com/2025/11/18/marvelous-designer-2025-2-metahumans-pleats-keyframes/), snippet).
   It exports Alembic, FBX, USD and glTF, and records avatar blendshape animation (2026.1)
   ([CG Channel, 2026-08-24](https://www.cgchannel.com/2026/08/clo-virtual-fashion-releases-marvelous-designer-2026-1/), page read).
8. **Fitting clothes and making clothes are separate jobs.** MetaTailor auto-fits "any 3D wearable" to
   any biped, layering and skin-weighting it. It has one-click Unity/UE5 bridges, plus an existing
   Character Creator plugin
   ([CG Channel, 2026-02-02](https://www.cgchannel.com/2026/02/metatailor-2-5-is-out-with-new-bridge-plugins-to-unity-and-ue5/), page read).
   Marvelous Designer and Z-Weave are pattern-and-sew tools (§4 of RESEARCH.md).
9. **ZBrush 2027 adds per-SubTool Selection Sets** (stored polygroups, masks, polypaint, UVs and morph
   targets) and a UV Editor ([CG Channel, 2026-10-15](https://www.cgchannel.com/?p=179326), page read).
   DynaMesh, ZRemesher and Sculptris Pro change topology and "break existing sets"
   ([Maxon help](https://help.maxon.net/zbr/en-us/Content/html/user-guide/selection-sets/selection-sets.html), undated, page read).
   That is the core sculpt data-model problem: stored states tied to one topology.
10. **Maya 2027 built in ngSkinTools** (layered, non-destructive skin weights) and added shot tools to
    Sequencer. MotionMaker, its generative locomotion, now covers horses
    ([CG Channel, 2026-03-25](https://www.cgchannel.com/?p=174872), page read). Maya 2027.1 added
    OpenTimelineIO ([CG Channel tag page](https://www.cgchannel.com/tag/maya-2027-1/), 2026-05, snippet).
11. **HumanIK-style character definitions are the interchange for retargeting.** Each MotionBuilder
    character needs an HIK character definition before retargeting
    ([Autodesk help 2026](https://help.autodesk.com/cloudhelp/2026/ENU/MotionBuilder-Character-Animation/files/Character-Animation/GUID-5911BFC8-0DB4-4F59-B3DB-F02C65DBBCE6.html), snippet).
    Rokoko exports "Human IK and Mixamo" skeleton presets
    ([Rokoko Studio page](https://www.rokoko.com/products/studio), undated, page read). Flow Studio added
    HumanIK to its Maya export on 2026-07-17
    ([Flow Studio release notes](https://help.wonderdynamics.com/release-notes/), page read).
12. **Mocap apps meet on a common feature set:** multi-person capture from one video (DeepMotion up to 8
    people), cleanup filters (root lock, foot lock, knee-pop smoothing), live streaming to many hosts
    (Rokoko to 8 apps including iClone), and a command API
    ([DeepMotion](https://www.deepmotion.com/animate-3d), undated, page read;
    [Rokoko](https://www.rokoko.com/products/studio), undated, page read).
13. **Blender's extension manifest is a simple, proven plugin contract.** It is a .zip plus a TOML
    manifest with SPDX licence, platforms, bundled Python wheels, and declared permissions (files,
    network, clipboard, camera, microphone), each with a reason. The manual does not say that permissions
    are enforced
    ([manual source, blender-manual main](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/advanced/extensions/getting_started.rst), current, page read).
14. **AI-film references blend a 3D stage with generation.** Flow Studio turns video into 3D scenes
    (mocap, camera track, clean plate; Maya, USD, Unreal and Blender exports). In August 2026 it added a
    browser 3D Editor and a node-based Canvas
    ([release notes](https://help.wonderdynamics.com/release-notes/), page read). ArtCraft (Rust, 37.6k
    stars) poses mannequins and blocks 3D scenes before image or video generation
    ([GitHub](https://github.com/storytold/artcraft), page read; API measured).
15. **Daz is still on Genesis 9 (2022)**, with Daz Studio 4.24 stable and Daz Studio 6 in preview
    ([Wikipedia](https://en.wikipedia.org/wiki/Daz_Studio), page read). Its DS 6 C++ SDK is still
    "Alpha" on Qt 6.10 ([Daz](https://www.daz3d.com/daz-studio-6-sdk), undated, page read). Its content
    format (DSON: .duf and .dsf) is published JSON
    ([DSON spec](https://docs.daz3d.com/public/dson_spec/start), snippet).

---

## Houdini (SideFX) — KineFX, APEX, Vellum, Solaris, Houdini Engine

Current version: **Houdini 22**, released 2026-07-15/16 (22.0.368)
([CG Channel, 2026-07-16](https://www.cgchannel.com/?p=177317), page read;
[Wikipedia](https://en.wikipedia.org/wiki/Houdini_(software)), snippet). No Houdini 21.5 was found; CG
Channel expected one before H22 shipped ([CG Channel, 2026-06-08](https://www.cgchannel.com/2026/06/sneak-peek-houdini-22/), snippet).

**Better at**
- KineFX was declared production-ready in H21 (Aug 2025). H21 added the Autorig Builder: place rig
  components on a viewport schematic and joints map automatically
  ([CG Channel, 2025-08-27](https://www.cgchannel.com/2025/08/sidefx-just-released-houdini-21-check-out-its-5-key-features/), snippet).
- H22 rig templates: "Prebuilt rig templates" transfer full rigs onto a character, while components
  can still be customised. Rig inversion (skeleton animation to rig controls) gives "more stable
  results" ([H22 KineFX](https://www.sidefx.com/docs/houdini/news/22/kinefx.html), 2026-07, page read).
- H22 Set Driven Keys component, and a character picker that lays out a 2D button grid for selecting
  controls (same page, page read).
- H22 Motion Mixer: nested clips, and a clip can become an override animation layer. Biped Setup and
  Biped Retarget SOPs, plus an "APEX Retarget to Rig" recipe (same page, page read).
- H22 animate state: cached animation, secondary motion, constraint and full-body IK tools (same page,
  page read).
- H22 ragdoll: wind, air resistance and turbulence forces, plus an "Impact Threshold" that turns a hit
  object into a ragdoll (same page, page read).
- Face: Blend shape component 3.0 has 3D or screen-space sliders, plus patch sliders driven by a NURBS
  surface (same page, page read).
- H22 grooming: Guide Deform SOP deforms static grooms with simulated guides ("much faster and captures
  guides more accurately"); Guide Reduce, Guide Utility (snap to skin, Vellum-ready attributes); Shot
  Sculpt for guides plus skin ([H22 hair](https://www.sidefx.com/docs/houdini/news/22/feathers.html),
  2026-07, page read).
- CFX: an improved muscle system that simulates "realistic skin and tissue deformation"
  ([H21 what's new](https://www.sidefx.com/products/whats-new-in-h21/), undated, page read). H22 adds
  faster muscle simulation, plus stress attributes and sliding constraints for soft tissue
  ([CG Channel, 2026-07-16](https://www.cgchannel.com/?p=177317), page read).
- Solaris (USD): Shot Builder, live rendering, and Karma on Hydra 2 with Gaussian splats (H21)
  ([H21 what's new](https://www.sidefx.com/products/whats-new-in-h21/), page read).

**Worth adding (no CC5 / iClone counterpart)**
- Assessment: rig templates plus a component-based autorig (one rig recipe applied to many characters,
  with any joint naming), a 2D character picker, Set Driven Keys, and ragdoll-on-impact are the pieces
  that map onto an iClone-type animator.

**API model**
- Houdini Engine (HAPI): the docs cover in-process, out-of-process and HARS (remote server) sessions,
  multithreading, SessionSync, PDG and licensing. Functions carry the `HAPI_` prefix
  ([HAPI docs](https://www.sidefx.com/docs/hengine/), Engine 9.0, page read, contents page only).
- H22 HAPI: SOP camera input and output, and COP (image) HDAs. The Unreal plug-in supports UE 5.7/5.8
  on Windows and Linux, and 5.6 on macOS; it has a "Bake to Asset" mode and a public API
  (`InstantiatePreset`). Unity 6.3/6.5, Maya 2027 and 3ds Max 2027 are supported
  ([H22 Engine](https://www.sidefx.com/docs/houdini/news/22/engine.html), page read).
- A free "Houdini Engine for Unity/Unreal" licence exists. It is limited to HDA files and to commercial
  customers; Indie covers both engines
  ([SideFX FAQ](https://www.sidefx.com/faq/question/houdini-engine-plugin-free-for-unity-and-unreal/), undated, snippet).
- The H22 notes list "VEX, OpenCL, and HOM scripting" and "Houdini Engine, APIs, and plug-ins" as areas
  ([H22 index](https://www.sidefx.com/docs/houdini/news/22/index.html), page read). HOM is the Python
  object model. The C++ HDK was not re-checked this session (see open items).
- Assessment: the distribution unit is the HDA, a node network with a parameter interface that any host
  (Engine) can cook. JustStage's equivalent would be "a command or plugin package callable headless from
  other apps".

**Formats**: USD-native Solaris (page read, H21 page). Others not re-checked this session.

**Platforms / price / licence**
- Windows 11, macOS 11+ and Linux. FX costs $4,495 node-locked or $6,995 floating; Core $1,995 or
  $2,995; Indie is rental-only; Apprentice is free and educational
  ([CG Channel, 2026-07-16](https://www.cgchannel.com/?p=177317), page read).
- Indie is $299/year, for revenue under $100K
  ([Shade, 2026](https://shade.inc/blog/sidefx-houdini-pricing-2026-fx-core-indie-license-costs), snippet).
  Apprentice is non-commercial and watermarked
  ([SideFX forum](https://www.sidefx.com/forum/topic/50431/), undated, snippet).
- Licence: SideFX EULA, proprietary. Commercial use: conditional (FX/Core yes; Indie under $100K; Apprentice
  no). [sidefx.com/get/buy](https://www.sidefx.com/get/buy/)

## Cinema 4D (Maxon) — approachability, character tools, SDK, MCP

Current version: **2027.0**, available from 2026-10-14
([Digital Production, 2026-10-14](https://digitalproduction.com/2026/10/14/maxon-2027-scatter-liquid-fx-zbrush-redshift-autograph), snippet).
2027.0's headline features are scattering and Liquid FX; no new character tools were found (same, snippet).

**Better at**
- Character Component: TDs pack rig objects or hierarchies into reusable components and templates
  for artists ([Maxon character page](https://www.maxon.net/cinema-4d/features/character-animation), undated, page read).
- Character Solver: Character Definitions retarget animation "regardless of joint orientation" (same,
  page read).
- Pose Morph tag: slider blends between poses, expressions and corrective morphs, including
  joint-rotation poses; two Character Object presets for joint-based faces (same, page read).
- CMotion: parametric cyclic motion (walk cycles) tuned with function curves; Cappuccino records
  "mouse movement as position data" (same, page read).

**Worth adding**
- MCP server (2026.4+, Windows and macOS, free): off by default; local, with a separate opt-in for
  network; an access token; user-chosen tool groups; control over Python execution. Results are native
  scene data the artist can "inspect, refine or undo". Officially supported clients are Claude Desktop
  and ChatGPT Desktop; others are untested
  ([AEC Magazine, 2026-09-30](https://aecmag.com/visualisation/maxon-automates-cinema-4d-with-mcp-server/), page read).
- The help for 2027 has MCP adapter preference pages
  ([Maxon help 2027](https://help.maxon.net/c4d/2027/en-us/Content/html/MCPADAPTERPREFS-MCPADAPTERPREFS_GROUP_CLIENTS.html.md), snippet).
  Changes are grouped in undo and logged locally
  ([Creative Bloq](https://www.creativebloq.com/ai/you-can-now-use-chatgpt-and-claude-to-speed-up-3d-art-in-cinema-4d), 2026, snippet).
- Assessment: Character Component templates (the TD builds, the artist uses) are a good split for
  JustStage's rig presets.

**API model**
- C++ SDK: CMake has been mandatory since 2025.3 (the Project Tool was removed); C++20; VS 2022, Xcode
  or GCC/Ninja. Plugins must match the Cinema 4D version, or they may be "binary incompatible"
  ([Maxon developer docs 2026](https://developers.maxon.net/docs/cpp/2026_0_0/manual_migrating_to_2026.html), snippet).
- The Python plugin API was not re-checked this session (open).

**Platforms / price / licence**: Windows and macOS (MCP article, page read). Price not retrieved (open).
Licence: Maxon EULA, proprietary. Commercial use: yes (paid). [maxon.net](https://www.maxon.net/cinema-4d)

## Cascadeur (Nekki) — AI-assisted posing and physics

Current version: **2026.1**, released about 2026-04-09
([Cascadeur blog](https://cascadeur.com/blog/view/cascadeur-2026-1-new-renderer-ue-live-link), snippet).

**Better at**
- 2025.1 AI Inbetweening generates motion between two poses, including loops; the limit is 88 frames
  between keys ([RenderU, 2025-04](https://renderu.com/en/news/post/26607), snippet). It was trained mostly on
  locomotion ([80.lv](https://80.lv/articles/cascadeur-2025-1-can-auto-generate-motion-between-poses), 2025-04, snippet).
- 2025.1 AutoPhysics keeps the original pose better, and the Physics Corrector gained a strength
  slider. Ragdolls interact with props, with convex and kinematic colliders (RenderU and the Cascadeur
  blog, 2025-04, snippet).
- 2025.3: inbetweening moved into Timeline Interpolation; quadruped AutoPosing and Quick Rigging
  arrived in alpha ([Cascadeur blog](https://cascadeur.com/blog/view/cascadeur-2025-3-new-inbetweening-quadrupeds), 2025, snippet).
- 2026.1 AI Root Motion generates between key poses, optionally using existing animations as a style
  reference. 2026.1 also has Collision Penetration Cleaning, constraints in AutoPhysics, and better
  quadruped AutoPosing
  ([Digital Production, 2026-04-09](https://digitalproduction.com/2026/04/09/cascadeur-2026-1-adds-unreal-live-link-filament-rendering-and-ai-root-motion/), snippet).
- 2026.1 Unreal Live Link (UE 5.5–5.7) for paid subscriptions, funded by an Epic MegaGrant. 2026.1 also
  completed the move of rendering to Filament (same, snippet).

**Worth adding**
- Assessment: physics-correctness as an editing aid (AutoPhysics as a corrector on keyed animation,
  not a simulation that replaces it), AI inbetweening on the timeline, and penetration cleaning are absent
  from the CC5/iClone leads list in RESEARCH.md §3.

**API model**
- Python 3.8 with a `csc` module; the app module's Action_manager calls Commands-menu actions, alongside
  Scene_manager and Dialog_manager. The help article is "intended primarily for running scripts", and
  `call_action` will be removed gradually
  ([Cascadeur help](https://cascadeur.com/help/tools/animation_tools/python_scripting_in_cascadeur), undated, snippet;
  [API reference](https://cascadeur.com/python-api), snippet).
- The API focuses "mainly on rig generation and rigging tool implementation"
  ([Cascadeur help](https://cascadeur.com/help/category/215), snippet).

**Formats**: CASC, FBX, DAE, USD, glTF exports on paid tiers; the free tier exports only CASC
([plans](https://cascadeur.com/plans), current, page read). glTF/GLB import arrived in 2025.1
([GameFromScratch](https://gamefromscratch.com/cascadeur-2025-1-released/), 2025-04, snippet).

**Platforms / price / licence**
- Windows 10 (1809+) and 11; Ubuntu 20.04+ only; macOS 13.3+ on Apple silicon only (no Intel); a mobile
  app ([plans](https://cascadeur.com/plans), page read).
- Free: non-commercial, with a 300-frame and 120-joint limit. Indie: $19/month or $96/year, revenue under
  $100k. Pro: $49/month or $396/year, adding retargeting, environment interaction, scene linking and
  quadruped AutoPosing. Teams: per seat (same, page read).
- Licence: Cascadeur EULA, proprietary. Commercial use: conditional (Free no; Indie under $100k; Pro yes).
  [cascadeur.com/plans](https://cascadeur.com/plans)

## Maya and MotionBuilder (Autodesk) — rigging, HumanIK, retargeting, mocap cleanup, shots

Current versions: **Maya 2027** (2026-03-25), 2027.1 (May 2026); **MotionBuilder 2027** (2026-03-26).

**Better at**
- Maya 2027 builds in ngSkinTools: layer-based, non-destructive skin weights with masking and mirroring
  ([CG Channel, 2026-03-25](https://www.cgchannel.com/?p=174872), page read).
- Maya MotionMaker (generative animation, added in 2026.1) now covers horses, besides humans and wolf-like
  dogs, for layout and previs (same, page read).
- Maya Sequencer: trim or time-scale shots by dragging their edges; a Playblast menu; shot colours,
  labels and thumbnails (same, page read).
- Bifrost 3.0 rigging: an eye module for eyelid deformation; a rod solver for secondary motion on chains
  (same, page read).
- USD for Maya: Component Creator and Variant Manager (same, page read).
- Maya 2027.1 supports OpenTimelineIO
  ([CG Channel tag](https://www.cgchannel.com/tag/maya-2027-1/), 2026-05, snippet).
- HumanIK: a full-body IK solver and retargeter; each character needs an HIK character definition,
  made in the Character Controls Definition tab
  ([Autodesk help 2026](https://help.autodesk.com/cloudhelp/2026/ENU/MotionBuilder-Character-Animation/files/Character-Animation/GUID-5911BFC8-0DB4-4F59-B3DB-F02C65DBBCE6.html), snippet).
- MotionBuilder maps raw capture (BVH or a live stream) to an Actor, then to a Character
  ([MocapOnline blog](https://mocaponline.com/blogs/mocap-news/motionbuilder-motion-capture-guide), undated, snippet; third party).
- MotionBuilder 2027: quaternion converters for Relation constraints; the viewer splits into 2–4 panes;
  device recording uses the scene frame rate, while the Story Tool still uses 30 fps
  ([CG Channel, 2026-03-26](https://www.cgchannel.com/?p=174959), page read).

**Worth adding**
- Assessment: layered skin weights, a HumanIK-style character definition as the one retargeting
  contract, shot trimming on a sequencer, and OTIO export for edits.

**API model**: not re-checked this session (open). Known but unverified here: Maya Python (cmds and
OpenMaya), the Maya C++ API, and MotionBuilder's Python (pyfbsdk) and C++ Open Reality SDK.

**Formats**: USD for Maya (page read above); OTIO (snippet). FBX not re-checked.

**Platforms / price / licence**
- Maya: Windows 11, RHEL/Rocky 8.10/9.7, macOS 14+. $255/month or $2,010/year; Maya Indie $330/year;
  Maya Creative from $3/day ([CG Channel](https://www.cgchannel.com/?p=174872), page read).
- MotionBuilder: Windows 11, RHEL/Rocky 8.10/9.7 (no macOS); $2,300/year
  ([CG Channel](https://www.cgchannel.com/?p=174959), page read).
- Licence: Autodesk Terms of Use, proprietary. Commercial use: yes (Indie conditional).
  [autodesk.com/products/maya](https://www.autodesk.com/products/maya)

## Daz Studio (Daz 3D) — figures, morphs, Genesis, content ecosystem

Current versions: stable **4.24.0.3** (2025-04-29); preview **6.25.2025.22607** (2025-08-14)
([Wikipedia](https://en.wikipedia.org/wiki/Daz_Studio), page read). The "Daz Studio 2025" alpha has been
on the Public Build channel since 2025-04-21; no final release was found
([Daz blog](https://forum.daz3d.com/blog/daz-studio-2025-alpha-release), 2025-04, snippet). A
"DAZ STUDIO 6 ANNOUNCED" headline exists from June 2026 ([yespress](https://yespress.io/daz-3d), snippet).

**Better at**
- Genesis 9 (October 2022) is one unified base figure for masculine and feminine shapes, for
  "Blendability of cross-gender shapes", so clothing, hair and add-ons fit across shapes. It also has
  asymmetry morphs, doubled mesh density, separate eye and mouth geometry, 8K HD materials, "Enhanced
  FACS", real-world measurements, and a Proportions System
  ([Introducing Genesis 9](https://free.downloads-cache.daz3d.com/introducing-genesis-9), content 2022, page read).
- Genesis lineage: Genesis (2011) made figures as morphs from a common base mesh; Genesis 2 split male
  and female; Genesis 3 moved to dual-quaternion weight maps
  ([Wikipedia](https://en.wikipedia.org/wiki/Daz_Studio), page read).
- dForce cloth (wind, gravity, collisions) has been free since October 2017 (same, page read).
- Third-party HD morph tools sculpt in Blender and export .dsf and .dhdm files that Daz Studio loads
  ([RenderHub](https://www.renderhub.com/intenzo/hd-morph-plugin-for-genesis-9), undated, snippet).
- A later DS 2025 alpha added Geometry Sculptor, for Daz Premier members only. 3Delight is being phased
  out because its licence ends
  ([Daz blog](https://forum.daz3d.com/blog/daz-studio-2025-alpha-updates), 2025, snippet).

**Worth adding**
- Assessment: one unified base figure is what lets a content ecosystem scale (every garment and morph
  fits every shape). JustStage's base-figure decision is also a content-compatibility decision.

**API model**
- The DS 6 SDK is a "free C++ software development platform" on Qt 6.10, which is installed separately
  (Qt under LGPL). It is labelled both "Beta" and "Alpha … NOT the Production Release", and its API may
  change. Plugins are 64-bit Windows and macOS. Daz assigns serial-number prefixes, builds installers
  and smoke-tests them; plugins install through DazCentral, DIM or manually
  ([Daz](https://www.daz3d.com/daz-studio-6-sdk), undated, © 2026, page read).
- The DS 4.5+ SDK adds "interfaces, scene components, render engines, file I/O"
  ([Daz](https://www.daz3d.com/daz-studio-4-5-sdk), snippet).
- Daz Script 2 (.dsa, .dsb, .dse) is current; Daz Script 1 is deprecated
  ([Daz docs](https://docs.daz3d.com/public/software/dazstudio/4/referenceguide/tech_articles/file_extensions/start), snippet).
  A third-party "DazScript Server" exposes Daz Script over HTTP (search result, snippet).

**Formats**: DSON spec 0.6.1.0 is JSON-based; .duf is a user file and .dsf a support file; both are pure
data with no scripting ([DSON spec](https://docs.daz3d.com/public/dson_spec/start), snippet;
[Daz forum](https://www.daz3d.com/forums/discussion/comment/604443), snippet).

**Platforms / price / licence**: Windows and macOS; freeware
([Wikipedia](https://en.wikipedia.org/wiki/Daz_Studio), page read). Licence: Daz EULA, proprietary
freeware; content carries its own licences. Commercial use: unclear (content licences not checked).
[daz3d.com](https://www.daz3d.com/)

No Genesis 10 announcement was found; recent store listings are Genesis 8.1 and 9 (RenderHub, 2026,
snippet).

## MetaHuman (Epic) — in-editor Creator, bodies, mesh-to-MetaHuman, capture

**Since which version**: MetaHuman Creator has been embedded in the Unreal editor since **UE 5.6**
(June 2025), leaving early access; Creator, Mesh to MetaHuman and Animator are integrated into 5.6
([CG Channel, 2025-06-04](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/), snippet;
[80.lv, 2025-06-04](https://80.lv/articles/explore-new-metahuman-features-in-unreal-engine-5-6), page read).
Current: **MetaHuman 5.8** (announced 2026-06-17 at Unreal Fest)
([GamesBeat](https://gamesbeat.com/epic-games-launches-metahuman-5-8-to-create-real-time-game-character-crowds/), page read).

**Better at**
- 5.6 parametric body: sculpt and blend body shapes (height, chest, waist, leg length) from scan data.
  The Outfit Asset combines garments that "adapt automatically to different body shapes"
  ([80.lv](https://80.lv/articles/explore-new-metahuman-features-in-unreal-engine-5-6), page read).
- 5.6 Animator: real-time animation from mono cameras (webcams, phones), and animation generated from
  audio that "accounts for emotion" (same, page read).
- 5.7 (2025-11-12): Creator on Linux and macOS; pose-agnostic body conforming; Python and Blueprint API;
  procedural grooming; scriptable creation operations
  ([MetaHuman 5.7](https://www.metahuman.com/releases/metahuman-5-7-is-now-available), snippet; the release-notes page did not render).
- 5.8: Mesh to MetaHuman handles full bodies and meshes of any topology; unbaked textures and materials
  export for editing; Lumen previews of custom lighting
  ([GamesBeat, 2026-06-17](https://gamesbeat.com/epic-games-launches-metahuman-5-8-to-create-real-time-game-character-crowds/), page read).
- 5.8 Animator: full-body capture from one off-actor camera (Experimental, Meshcapade, a Windows plugin on
  Fab); real-time procedural blinks and emotion from audio; Live Link Face streams video; Animator runs
  on Linux and macOS (same, page read).
- 5.8 Collections (Experimental): crowds of modular parts (head, body, hair, clothing) that switch
  between full actors and instanced skinned meshes by distance (same, page read).

**Worth adding**
- Assessment: mesh-to-character for any topology (bring your own scan or sculpt), audio-to-face with
  emotion, and single-camera body capture are the three MetaHuman jobs that overlap CC5's Headshot and
  iClone's AccuFace/AccuLips leads.
- Assessment: RigLogic and DNA under MIT make a documented, open face-rig evaluation format a candidate for
  JustStage's face standard. Read the repo's licence files before relying on that (RESEARCH.md §9).

**API model**
- 5.7 added Python and Blueprint API support (snippet above). Free MetaHuman plugins for Maya and Houdini
  were released with 5.6 ([CG Channel](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/), snippet).
- 5.6 gave "full access to the source code of the MetaHuman Creator tool" (Epic news, quoted in a
  [search result](https://metahuman.com/news/metahuman-leaves-early-access-with-a-feature-packed-new-release), snippet; the page needs an Epic login).
- `EpicGames/OpenRigLogic`: MIT, created 2026-06-05, last push 2026-10-23
  ([GitHub API](https://api.github.com/repos/EpicGames/OpenRigLogic), measured).
  `EpicGames/MetaHuman-DNA-Calibration`: licence NOASSERTION, last push 2025-06-20 (measured).

**Formats**: DNA (rig) files; Unreal assets. Exporting to DCCs goes through the Maya and Houdini plugins
(snippets above).

**Platforms / price / licence**
- Creator on Windows, Linux and macOS since 5.7; Animator on Linux and macOS since 5.8 (above). The
  body-capture plugin is Windows-only (GamesBeat, page read).
- Licence: Unreal Engine EULA; MetaHumans are "non-engine products", usable in Unity, Godot and DCCs
  without the 5% royalty, and can be sold on marketplaces. Free under $1M a year in revenue; a seat licence
  above that. Not to be used to train or enhance AI models
  ([CG Channel, 2025-06-04](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/), snippet).
  Commercial use: conditional. RigLogic and DNA: MIT, so yes.
  [unrealengine.com/eula](https://www.unrealengine.com/eula)

## ZBrush (Maxon) — sculpting, retopology, layers, morphs, polypaint, iPad

Current version: **ZBrush 2027.0** and **ZBrush for iPad 2027.0**, released about 2026-10-14
([CG Channel, 2026-10-15](https://www.cgchannel.com/?p=179326), page read).

**Better at**
- Long-standing core, confirmed by the 2027 help: subdivision levels, morph targets, polypaint, and the
  topology tools DynaMesh, ZRemesher and Sculptris Pro, which "break existing sets"
  ([Selection Sets help](https://help.maxon.net/zbr/en-us/Content/html/user-guide/selection-sets/selection-sets.html), undated, page read).
- 2027.0 Selection Sets: each SubTool stores several versions of its polygroups, masks, polypaint, UVs
  and morph targets, kept in its rows, with update, switch and copy/paste. The Morph brush blends a stored
  morph target with the current mesh (same, page read).
- 2027.0 UV Editor, built on Cinema 4D's UV tech: three auto-unwrap modes including Unwrap by Polygroup;
  UDIM; trim sheets. Users can bake the current 3D Layer
  ([CG Channel, 2026-10-15](https://www.cgchannel.com/?p=179326), page read).
- 2026.1: a Retopology Brush and Smooth Retopology Brush on desktop and iPad; photogrammetry from the
  iPad camera
  ([CG Channel, 2025-12-04](https://www.cgchannel.com/2025/12/maxon-releases-zbrush-2026-1-and-zbrush-for-ipad-2026-1/), snippet).
- 2026.2 has a one-click Substance Painter bridge; 2026.2.1 runs natively on Windows on Arm, with GoZ
  to Maya and 3ds Max ([Maxon what's new](https://www.maxon.net/en/zbrush/new), undated, page read). Sources
  disagree on the Maya/Max versions (2026 on Maxon's page, 2027 on ZBrushCentral, snippet).
- iPad 2027.0 adds Spotlight (image-based sculpting and painting) and 3D Layers (non-destructive sculpt,
  polypaint and masks, plus blend shapes for poses) ([Maxon](https://www.maxon.net/en/zbrush/new), page read).

**Worth adding**
- Assessment: the two data-model lessons for JustStage's sculpt standard are (a) multi-resolution
  subdivision levels with detail layers, and (b) stored masks, groups, paint and morph states per mesh
  that are invalidated, not silently corrupted, when topology changes.

**API model**
- 2026.0 added Python scripting, "a more pipeline-friendly alternative to … ZScript", for automating
  tasks, customising the UI and modifying tools
  ([CG Channel, 2025-09-10](https://www.cgchannel.com/?p=170024), page read). How Python plugins are
  packaged is not documented in that source. GoZ is the round-trip bridge to other apps (Maxon page, page read).

**Formats**: ZTL and ZPR (native; Selection Sets help, page read); STL, VRML and 3MF from the 3D Print Hub
(CG Channel 2025-09-10, page read).

**Platforms / price / licence**: desktop on Windows 11 and macOS 15+; iPadOS 17+ with an A12 or later.
Desktop is rental-only at $49/month or $399/year, including the iPad app; iPad alone is free with paid
features at $9.99/month or $89.99/year ([CG Channel, 2026-10-15](https://www.cgchannel.com/?p=179326), page read).
Licence: Maxon EULA, proprietary. Commercial use: yes (subscription). [maxon.net/zbrush](https://www.maxon.net/en/zbrush)

## Marvelous Designer (CLO Virtual Fashion) — patterns, sewing, simulation, fitting, export

Current version: **2026.1** (August 2026)
([CG Channel, 2026-08-24](https://www.cgchannel.com/2026/08/clo-virtual-fashion-releases-marvelous-designer-2026-1/), page read).

**Better at**
- 2025.0: keyframe animation of avatar joints, fabric and wind; IK joint mapping; Auto Convert to Motion.
  Daz, Mixamo, Character Creator and MetaHuman characters "with compatible bone structures" convert
  automatically; experimental fur; a modular garment library
  ([MD support](https://support.marvelousdesigner.com/hc/en-us/articles/47358120307353-Marvelous-Designer-2025-0-2025-1-New-Feature-List), 2025, snippet).
- 2025.1: off-avatar 3D pen drawing flattened into 2D pieces; soft-body simulation for custom avatars and
  props; AI Pose Generator (beta); Pattern Drafter (beta); topology kept during Auto Fitting (same, snippet).
- 2025.2: direct MetaHuman DNA import; patterns to trims; a pleat tool; EveryWear export with FBX;
  GPU soft-body
  ([Digital Production, 2025-11-18](https://digitalproduction.com/2025/11/18/marvelous-designer-2025-2-metahumans-pleats-keyframes/), snippet).
- 2026.0 (2026-04-20): 3D Pencil and Lacing tools; Toon Shader; glTF; Template-Based Rigging (beta),
  which adds bones to garments automatically
  ([CG Channel tag](https://www.cgchannel.com/tag/rig-template/), snippet).
- 2026.1: Brush Pinching (paint folds and wrinkles); a pinching simulation override; a Seamline Rip tool
  (experimental, tears along seams with fraying); recording of blendshape value changes for avatars;
  customisable toolbars and Global Search; Metal GPU simulation on Apple silicon
  ([CG Channel, 2026-08-24](https://www.cgchannel.com/2026/08/clo-virtual-fashion-releases-marvelous-designer-2026-1/), page read).

**Worth adding**
- Assessment: automatic avatar conversion from CC/Daz/Mixamo/MetaHuman is the bar for JustStage's
  importers. Garment auto-rigging and "fit keeps topology" are what a clothing workflow needs for game
  export.

**API model**
- Python Script API with a Script-menu editor. Python (.py) plug-ins are registered in the Plug-in
  Manager and appear in a Plugin tab, on Windows and macOS
  ([developer.marvelousdesigner.com](https://developer.marvelousdesigner.com/python.html), undated, snippet).
- The Linux release (2025-09-30) included the Python API: batch import/export and simulation parameters
  ([Digital Production, 2025-09-30](https://digitalproduction.com/2025/09/30/marvelous-designer-finally-sews-itself-into-linux/), snippet; vendor claims).
- A vendor reply in CLO's community forum says more advanced API features are "to be added in the future";
  a user said the API mostly covered import and export
  ([CLO forum](https://support.clo3d.com/hc/en-us/community/posts/360001305087-Python-enabled-stitching), older, snippet).

**Formats**: exports Alembic, FBX, USD, OBJ sequences, Maya cache, PC2 and MDD; camera import and export
in FBX and glTF/GLB ([CG Channel, 2026-08-24](https://www.cgchannel.com/2026/08/clo-virtual-fashion-releases-marvelous-designer-2026-1/), page read).

**Platforms / price / licence**: Windows 11; macOS 14+; RHEL/Rocky 9.5+ (Linux edition). Rental-only:
Personal $39/month or $280/year; Enterprise $199/month or $2,000/year ($2,300/year including Linux); Indie
for studios of two or more under $500k (price undisclosed) (same, page read). Licence: CLO EULA,
proprietary. Commercial use: unclear (the terms of each tier were not read).
[marvelousdesigner.com](https://www.marvelousdesigner.com/)

## MetaTailor (Hologress) — fitting existing clothes to any humanoid

Current version: **2.5** (2026-02-02)
([CG Channel](https://www.cgchannel.com/2026/02/metatailor-2-5-is-out-with-new-bridge-plugins-to-unity-and-ue5/), page read).

**Better at**
- It imports "any 3D wearable" and auto-fits it to any bipedal character, layering and skin-weighting the
  outfit. Sculpt brushes refine the result; accessories such as weapons attach (same, page read).
- 2.0 (2024-10-03): real-time cloth physics for straps and loose parts, with paintable weights blending
  physics and skinning; "assemblies" of clothing; an in-app asset library
  ([CG Channel](https://www.cgchannel.com/2024/10/metatailor-2-0), page read).
- 2.5: Unity and UE5 Bridge plugins out of beta (paid Pro only), joining the existing Character Creator
  plugin. Digital Production describes a one-click round trip with Unreal, Unity and CC4/CC5
  ([Digital Production, 2026-02-05](https://digitalproduction.com/2026/02/05/metatailor-adds-engine-bridges-and-less-fbx-fatigue/), snippet).

**Worth adding**: Assessment: "drop in a store-bought garment and it fits, layers and skins itself" is
a job JustStage must do apart from pattern-based clothing.

**API model**: none documented in these sources; the bridges are the integration surface (open).

**Formats**: FBX export (both CG Channel pages, page read).

**Platforms / price / licence**: Windows only. Rental-only: free with base features and 5 FBX exports a
month; Pro $35/month or $336/year (2026-02, page read; the free-export count was 10 in 2024-10). Licence:
Hologress terms. Commercial use: unclear. [metatailor.app](https://www.metatailor.app/)

## Z-Weave (Z-Emotion)

Already in RESEARCH.md §4 (web, 2026-10-29); not re-derived. Re-read
[z-emotion.com/z-weave](https://www.z-emotion.com/z-weave) (undated, © 2026, page read): the page names no
platforms, no API or SDK, and no specific avatar sources (only DXF/OBJ/FBX import and a "default
avatar"). Grading and colorways sit on Pro and Enterprise; grading across avatars is not described.
Licence: Z-Emotion terms. Commercial use: unclear. Platforms: not stated (open).

## Substance 3D Painter (Adobe) — smart materials, layers, baking

Current version: **12.2** (2026-10-21)
([release notes](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/release-notes/version-12-2), page read).

**Better at**
- 12.2: cage painting for baking (paint per-pixel cage offsets on top of the global distance); a reworked
  Polygon Fill with loop selection and blend modes; Texture Set highlighting; order-independent
  transparency in the viewport; bakers 3.23.0 (same, page read).
- 12.1 (2026-06-22): automatic rebaking; skew-correction painting on the mesh; OpenPBR support
  ([release notes 12.1](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/release-notes/version-12-1), snippet).
- 12.0 (2026-03-09): Warp to Geometry (decals follow curvature and topology); a Flatten action in the layer
  stack ([release notes 12.0](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/release-notes/version-12-0), snippet).

**Worth adding**: Assessment: the layer stack with procedural "smart" materials, masks driven by baked
maps, and automatic rebaking when the mesh changes is the texturing workflow to match. Smart materials
and the layer model were not re-read this session.

**API model**
- Plugins "are wrote in Javascript and can be combined with the QML language"
  ([plugins page](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/features/plugins/plugins), updated 2026-10-08, page read).
- A separate Python API exists. Its changelog shows `substance_painter.js.evaluate()` since 0.2.3
  (Painter 7.4) ([Python API changelog](https://helpx.adobe.com/substance-3d-painter-python/api/changelog.html), snippet).
  A JavaScript deprecation claim is forum-only ([tech-artists.org](https://www.tech-artists.org/t/substance-painter-python-api/16176), snippet).
  Not confirmed.

**Formats**: USD export (12.2 fixes, page read). Others not re-checked.

**Platforms / price / licence**: Steam perpetual $199.99, with feature updates until March 2026; the
latest version comes through the Substance 3D Indie subscription; Linux (Ubuntu 22.04.1+) appears in the
system requirements ([GG.deals](https://gg.deals/application/substance-3d-painter-2026/), retailer, snippet).
Licence: Adobe General Terms, proprietary. Commercial use: yes.
[adobe.com/products/substance3d](https://www.adobe.com/products/substance3d.html)

## Mixamo (Adobe) — the auto-rig flow and a motion library

**Better at**
- Characters and animations are royalty-free "for personal, commercial, and non-profit projects",
  including films and games. The auto-rigger is for bipedal humanoids only, in a neutral pose, with
  distinguishable head, body, arms and legs
  ([Adobe Mixamo FAQ](https://helpx.adobe.com/au/creative-cloud/faq/mixamo-faq.html), snippet; helpx returned 403 to scripted access).
- The flow: upload, then place markers on chin, wrists, elbows, knees and groin, then it rigs to a choice
  of skeletons ([Reallusion forum](https://forum.reallusion.com/PrintTopic284483.aspx), snippet). Another
  guide names the hip marker "pelvis"
  ([Overdare docs](https://docs.overdare.com/manual/studio-manual/asset-and-resource-creation/using-mixamo-to-create-studio-animations), snippet).
- An older Adobe community post says raw character and animation files may not be redistributed
  ([Adobe community, 2022](https://community.adobe.com/questions-696/mixamo-faq-licensing-royalties-ownership-eula-and-tos-589400), snippet).

**Status**: "maintenance mode", with no shutdown date; a multi-day outage in June 2025; Adobe's Blender
add-on stopped working with Blender 4.0
([Cinevva guide](https://app.cinevva.com/guides/free-character-animations-rigging), 2026, snippet; vendor of a competing tool).

**Worth adding**: Assessment: a "five clicks to a rig" flow (place a few landmarks, then auto-skin)
is the bar for JustStage's auto-rig. Mixamo itself is not a dependency to build on.

**API model**: none public found (open). **Formats**: FBX upload and download (not re-checked).
**Price / licence**: free with an Adobe ID; Adobe terms; commercial use yes (royalty-free).

## Mocap apps

### Rokoko Studio
- Retargeting onto custom characters; live streaming to Unreal, Unity, Blender, iClone, MotionBuilder,
  Maya, Houdini and Cinema 4D (Plus or Pro); "Advanced command API" and UDP trigger messages (Pro)
  ([Rokoko Studio](https://www.rokoko.com/products/studio), undated, page read).
- Devices: Smartsuit Pro II, Smartgloves, Face Capture. Filters: root locking, foot locking, elevation
  tracking, knee-pop smoothing (same, page read).
- Exports FBX (all plans), BVH and CSV, with skeleton presets including "Human IK and Mixamo" (same,
  page read).
- Plans (annual price per month): Starter free (30 s of Vision AI video a month); Basic $10 (600 s);
  Plus $20 (3,000 s); Pro $50 (15,000 s); Enterprise from $100 (same, page read). Platforms: not stated on
  that page (open). Licence: Rokoko terms. Commercial use: yes on paid plans, unclear on free.
- API model: a command API plus UDP triggers on Pro (above). Assessment: this is the "remote-control a
  mocap app" pattern.

### Move.ai
- Markerless capture since 2019; claims the first multi-camera systems; pricing by contact
  ([move.ai](https://www.move.ai/), undated, page read).
- Move One (single camera) has a free plan with credits: s1 costs 6 credits a second, s2 12. The Move Pro
  (multi-camera, multi-person) trial is $995 for 30 days
  ([docs.move.ai pricing](https://docs.move.ai/knowledge/pricing), snippet).
- Pay-as-you-go API rates per second (s1 $0.012, s2 $0.024, m2 $0.043 per camera)
  ([FitGap](https://us.fitgap.com/products/move-ai), third party, snippet).
- Licence: Move.ai terms. Commercial use: unclear. Platforms: cloud plus capture apps (not verified).

### DeepMotion (Animate 3D, SayMotion)
- Up to 8 people from one video; face and hand tracking; physics simulation; foot locking and
  hand-to-ground contact; smoothing. Custom characters from FBX, GLB or VRM; automatic retargeting; a
  "Rotoscope Pose Editor" (patent-pending)
  ([Animate 3D](https://www.deepmotion.com/animate-3d), undated, page read).
- Exports FBX, BVH, GLB and MP4. The Animate 3D API and a Real-Time SDK are available through sales;
  browser-based (same, page read).
- SayMotion (text to animation) launched as an open beta in 2024
  ([CG Channel](https://www.cgchannel.com/?p=156294), 2024, snippet).
- Licence: DeepMotion terms. Commercial use: unclear. Price: not shown on the page (open).

### Plask
- Free: 15 s of mocap a day. Standard: $18/month (annual), 10 min a month. Pro: $50/month (annual),
  1 h a month. All plans: full body and hands, multi-person capture, FBX/GLB/BVH export, real-time
  collaboration, auto camera and lighting. API: a footer link only
  ([plask.ai/pricing](https://plask.ai/pricing), © 2026, page read).
- Licence: Plask terms. Commercial use: unclear.

Assessment (mocap): JustStage needs a capture-input standard (live stream in, recorded clip in), a cleanup
filter set (root and foot lock, smoothing, penetration fixes), and HumanIK/Mixamo-style skeleton presets
for export, whatever capture model it uses.

## AI-film references

### Autodesk Flow Studio (formerly Wonder Studio)
Release notes ([help.wonderdynamics.com](https://help.wonderdynamics.com/release-notes/), latest entry
2026-10-28, page read):
- 2024-10-30: Video to 3D Scene, with motion prediction for occluded actors. 2024-01-22: camera tracking.
  2023-12-04: USD export. 2023-12-18: Maya scene export. 2024-02-12: Unreal scene export.
- 2023-11-08: character validation add-ons for Maya and Blender. 2025-06-30: AI mocap exports MetaHuman body
  animation to Unreal. 2025-02-12: Clean Plate and Camera Track as standalone tools.
- 2026-04-16: rigging in the Asset Generator; GLB download. 2026-05-14: a Static Camera mocap mode.
  2026-06-25: Character LoRA training. 2026-07-17: Maya scene export adds HumanIK, pelvis controls and
  per-shot control groups.
- 2026-08-04: a browser 3D Editor (characters, animation, cameras, worlds) and Canvas, a node-based
  image and video workspace across many outside models. 2026-10-19: object keyframing in the 3D Editor;
  image-to-3D with Trellis 2.0.
- Pricing: a freemium tier was added and Lite cut to $10 (Autodesk, Aug 2025)
  ([Autodesk news](https://adsknews.autodesk.com/en/?p=53687), snippet). Tiers Free / Lite $10 /
  Standard $45 / Pro $95 / Enterprise; mocap costs 10 credits a second, live action 20
  ([usagepricing.com](https://usagepricing.com/blueprint/activity/wonder-dynamics-2026-08-04-launch), aggregator, snippet).
- Licence: Autodesk terms. Commercial use: conditional (the free tier is watermarked, 720p, per the aggregator).
- Assessment: Flow Studio's whole pipeline (video in; actor replaced by a rigged character; camera,
  mocap and clean plate out as an editable DCC scene) is the reference for JustStage-plus-JustDirect.

### ArtCraft (storytold)
- "The IDE for artists": compose in 2D, stage scenes in 3D, pick models. Character posing and camera
  before generating; identity transfer guided by a posed mannequin; scene blocking with kitbashing; 3D
  image compositing; image to 3D mesh. A catalog of 62 models (image, video, audio, mesh, world/splat).
  Stable releases for Windows and macOS; Linux builds from source. Dual MIT or Apache-2.0
  ([README](https://github.com/storytold/artcraft), current, page read).
- `storytold/artcraft`: Rust; GitHub reports Apache-2.0; 37,579 stars; release v0.41.0 on 2026-09-26; last
  push 2026-10-28 ([GitHub API](https://api.github.com/repos/storytold/artcraft), measured). The org also
  holds `bevy-mocap` and `storyteller-bevy` (names only, measured).
- Licence: MIT or Apache-2.0. Commercial use: yes.
- Assessment: ArtCraft's 3D is a staging aid for generation, not a character or animation tool. It
  overlaps JustStage only on posing, blocking and camera.

## Blender — Rigify, hair curves, shape keys, extensions

Current version: **Blender 5.2 LTS**, released 2026-07-14, supported to July 2028
([release notes source](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.2/index.md), page read).
docs.blender.org and developer.blender.org returned 403 to scripted access, so the official source repos
were read instead.

**Better at**
- 5.2: online asset libraries browsed and downloaded inside Blender; an experimental Geometry Nodes
  physics framework for hair and cloth on an XPBD solver; a scene-project sculpt brush
  ([GameFromScratch](https://gamefromscratch.com/blender-5-2-lts-released/), 2026-07, page read).
- 5.2 animation and rigging: Copy Constraints in Ctrl+L; Auto IK reverse with non-connected parents;
  select keys by type; Duplicate and Rename for bones (no ".001"); "Only Insert Available" on by default
  ([dev notes](https://developer.blender.org/docs/release_notes/5.2/animation_rigging/), snippet).
- Rigify: "Automatic rigging from building-block components", support "OFFICIAL", in
  `scripts/addons_core/` of Blender's main repo
  ([source](https://projects.blender.org/blender/blender/raw/branch/main/scripts/addons_core/rigify/__init__.py), page read).
  Assessment: that path means it ships with Blender as a core add-on.
- Hair Nodes (curves): bundled node-group categories for Deformation, Generation, Guides, Utility, Read
  and Write ([manual source](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/modeling/geometry_nodes/hair/index.rst), page read).

**Worth adding**: Assessment: building-block rigs (Rigify) plus node-based hair (guides, generation,
deformation) are open references whose behaviour JustStage can study, and whose files it can import.

**API model**
- An extension is a .zip with a TOML manifest: `license` as an SPDX list, optional `platforms`
  (windows-x64/arm64, macos-x64/arm64, linux-x64), bundled Python `wheels`, and optional `[permissions]`
  (files, network, clipboard, camera, microphone), each with a short reason. `blender_version_min` is
  4.2.0 or later. Enforcement is not described
  ([manual source](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/advanced/extensions/getting_started.rst), page read).
- Python API (bpy): standard, not re-checked this session.

**Formats / platforms / licence**: USD, glTF and FBX I/O, and Windows/macOS/Linux, not re-checked this
session. Licence: GNU GPL. Commercial use: yes. Whether add-ons count as GPL is RESEARCH.md §9's question.
[blender.org/about/license](https://www.blender.org/about/license/)

## Other apps found doing one of these jobs well

- **Nomad Sculpt** (mobile sculpting): iOS and Android apps; a desktop licence at $35 one-time for 2
  computers ([softwares.com](https://www.softwares.com/compare/nomad-sculpt-vs-zbrush), read 2026-10-12, snippet).
  A native desktop beta for Windows and macOS came out in 2025 (same source, snippet). Clay, flatten and
  smooth brushes, trim booleans, and vertex painting of colour, roughness and metalness (app listing,
  snippet). Licence: proprietary, unclear. Assessment: proof that a ZBrush-class sculpt loop runs on
  phone-class GPUs.
- Not researched for lack of search budget: 3DCoat (sculpt plus retopology plus paint), Style3D (cloth),
  and Unreal Engine's own animation authoring (Control Rig, Sequencer), which is the closest match to
  iClone's timeline. Listed under open items.

---

## Checks of RESEARCH.md §4 leads (those "from the chat, not checked")

| Lead | Result |
|---|---|
| Houdini: Solaris native USD; KineFX; Vellum cloth and hair; Python + C++ SDK; Engine in UE/Unity/other hosts | **Confirmed**, apart from Vellum and C++: Solaris and USD (H21 page, page read); KineFX/APEX (H22 notes, page read); Engine plug-ins for UE, Unity, Maya and Max (H22 Engine, page read); HOM named (page read). Vellum-specific changes and the C++ HDK were **not re-checked**. |
| Cinema 4D: approachable UI; clean Python + C++ SDK | C++ SDK **confirmed** (CMake, C++20; snippet). Python **not re-checked**. "Approachable" is opinion, not checkable. **New**: official MCP server (page read). |
| Cascadeur: AutoPosing and AutoPhysics as the main animation source | **Confirmed**, plus AI Inbetweening, Root Motion and Live Link (snippets; plans page read). |
| Maya/MotionBuilder: rigging, retargeting, mocap cleanup; HumanIK naming as a candidate | HumanIK character definitions and retargeting **confirmed** (snippet). Rokoko and Flow Studio export HumanIK presets (page read). HumanIK *naming* specifics not checked. |
| MetaHuman Creator runs in the Unreal editor since 5.6 (§6 "to verify") | **Confirmed**: since UE 5.6, June 2025 (80.lv page read; CG Channel snippet). |
| MetaTailor is a Unity-based tool (§4 web entry) | **Not confirmed**: neither CG Channel article (page read) says it is built on Unity; both name Unity only as an export and bridge target. The rest of the entry holds: physics and marketplace in 2.0, bridges out of beta in 2.5. |

---

## Summary table

| App | Overlapping job | Where it beats CC5 / iClone (facts above) | API language and model | Platforms | Price / licence | Source |
|---|---|---|---|---|---|---|
| Houdini 22 | rigging, animation, groom, muscles, USD scene | rig templates and transfer, Set Driven Keys, picker, Motion Mixer layers, ragdoll on impact, guide-deformed grooms | Python (HOM), VEX; HDAs; Houdini Engine C API (HAPI: in-process, out-of-process, remote) in UE/Unity/Maya/Max | Win, macOS, Linux | FX $4,495, Core $1,995, Indie ~$299/yr, Apprentice free; SideFX EULA, conditional | [H22 KineFX](https://www.sidefx.com/docs/houdini/news/22/kinefx.html), [CG Channel](https://www.cgchannel.com/?p=177317) |
| Cinema 4D 2027 | character rigs, retarget, scene | Character Component templates, Character Solver retarget, Pose Morph; **official MCP server** with permissions | C++20 SDK (CMake, version-matched), Python; MCP | Win, macOS | not retrieved; Maxon EULA, yes | [Maxon](https://www.maxon.net/cinema-4d/features/character-animation), [AEC](https://aecmag.com/visualisation/maxon-automates-cinema-4d-with-mcp-server/) |
| Cascadeur 2026.1 | posing, keyframe animation, physics | AutoPosing, AutoPhysics, AI inbetweening, AI root motion, penetration cleanup, UE Live Link | Python 3.8 `csc` (thin, rig-focused) | Win, Ubuntu, macOS ARM, mobile | Free (non-commercial) / $96/yr Indie / $396/yr Pro; conditional | [plans](https://cascadeur.com/plans) |
| Maya 2027 | rigging, skinning, shots | layered skin weights, MotionMaker, Sequencer shot tools, OTIO | Python, C++ (not re-checked) | Win, Linux, macOS | $2,010/yr; Indie $330/yr; yes | [CG Channel](https://www.cgchannel.com/?p=174872) |
| MotionBuilder 2027 | mocap cleanup, retargeting | HumanIK definition and retarget, Actor-to-Character, multi-pane viewer | Python, C++ SDK (not re-checked) | Win, Linux | $2,300/yr; yes | [CG Channel](https://www.cgchannel.com/?p=174959) |
| Daz Studio 4.24 / 6 preview | figures, morphs, content | unified Genesis 9 figure, asymmetry, FACS; open JSON (DSON) content | C++/Qt 6.10 SDK (alpha), Daz Script 2 | Win, macOS | freeware; Daz EULA, unclear (content) | [Wikipedia](https://en.wikipedia.org/wiki/Daz_Studio), [SDK](https://www.daz3d.com/daz-studio-6-sdk) |
| MetaHuman 5.8 | heads, bodies, face rig, capture | any-topology mesh-to-character, audio-to-face with emotion, single-camera body capture, crowds | Python + Blueprint (5.7); RigLogic/DNA MIT; Maya/Houdini plugins | Win, Linux, macOS | free under $1M revenue; UE EULA, conditional; no AI training | [GamesBeat](https://gamesbeat.com/epic-games-launches-metahuman-5-8-to-create-real-time-game-character-crowds/) |
| ZBrush 2027 | sculpt, retopo, morphs, paint | subdivision levels, DynaMesh, ZRemesher, Selection Sets, retopo brush, UV editor, iPad 3D Layers | Python (2026.0), ZScript, GoZ | Win, macOS, iPad | $399/yr; iPad $89.99/yr; yes | [CG Channel](https://www.cgchannel.com/?p=179326) |
| Marvelous Designer 2026.1 | making clothes | pattern, sew and simulate; auto avatar conversion (CC, Daz, Mixamo, MetaHuman); garment rigging; pinch and rip | Python script API and .py plug-ins | Win, macOS, Linux | $280/yr Personal; CLO EULA, unclear | [CG Channel](https://www.cgchannel.com/2026/08/clo-virtual-fashion-releases-marvelous-designer-2026-1/) |
| MetaTailor 2.5 | fitting clothes | auto-fit any wearable to any biped with layering and skin weights; physics; engine bridges | none documented; bridges | Win | free (5 exports) / $336/yr Pro; unclear | [CG Channel](https://www.cgchannel.com/2026/02/metatailor-2-5-is-out-with-new-bridge-plugins-to-unity-and-ue5/) |
| Z-Weave | making clothes | pattern and sew with real-time simulation; glTF on the free tier (§4) | z-maya and z-unreal plugins (§4); no API stated | not stated | free / $40/mo Pro (§4); unclear | [z-emotion](https://www.z-emotion.com/z-weave) |
| Substance 3D Painter 12.2 | skin and prop texturing | smart materials and layers, bake cage painting, auto rebake, OpenPBR | JavaScript + QML plugins; Python API | Win, macOS, Linux | $199.99 Steam or Indie subscription; yes | [12.2 notes](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/release-notes/version-12-2) |
| Mixamo | auto-rig, motion library | landmark auto-rig in a few clicks; royalty-free motions | none public | web | free; Adobe terms, yes | [FAQ](https://helpx.adobe.com/au/creative-cloud/faq/mixamo-faq.html) |
| Rokoko Studio | mocap, live stream | streams to 8 hosts incl. iClone; cleanup filters; HumanIK/Mixamo presets | command API + UDP triggers (Pro) | not stated | free to $50/mo; yes on paid | [Rokoko](https://www.rokoko.com/products/studio) |
| Move.ai | markerless mocap | multi-camera, multi-person markerless | pay-per-second API | cloud and apps | credits; unclear | [docs](https://docs.move.ai/knowledge/pricing) |
| DeepMotion | video mocap, text to motion | 8 people from one video, physics filter, rotoscope pose editor | API and real-time SDK via sales | browser | freemium; unclear | [Animate 3D](https://www.deepmotion.com/animate-3d) |
| Plask | video mocap | multi-person, hands, collaborative browser editor | API (link only) | browser | free / $18 / $50 per month; unclear | [pricing](https://plask.ai/pricing) |
| Flow Studio | video to animated 3D scene | replaces actors with CG characters; camera track; clean plate; Maya, USD, Unreal and Blender export; 3D Editor + Canvas | web app; Maya/Blender validation add-ons | browser | Free / $10 / $45 / $95; conditional | [release notes](https://help.wonderdynamics.com/release-notes/) |
| ArtCraft 0.41 | 3D staging for AI film | mannequin posing and scene blocking feeding image and video models | open source (Rust) | Win, macOS (Linux from source) | free; MIT or Apache-2.0, yes | [GitHub](https://github.com/storytold/artcraft) |
| Blender 5.2 LTS | rigging, hair, shape keys, plugins | Rigify building blocks, hair node groups, XPBD node physics, online asset libraries | Python (bpy); extensions = zip + TOML manifest with declared permissions | Win, macOS, Linux | free; GPL, yes | [manifest](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/advanced/extensions/getting_started.rst) |
| Nomad Sculpt | sculpting on tablet and phone | mobile-class sculpt with vertex PBR paint | not found | iOS, Android, desktop beta | ~$35 desktop; unclear | [softwares.com](https://www.softwares.com/compare/nomad-sculpt-vs-zbrush) |

---

## Couldn't verify / open

- **Search budget ran out** (200 searches shared by every agent in this session). These were not reached:
  Maya MotionMaker internals; Move.ai Move Live (real-time) and finger tracking; Rokoko Studio platforms;
  Cinema 4D price and Python plugin API; Houdini HDK (C++) ABI rules and the `packages` JSON format;
  Houdini Vellum H22 changes (vellum.html not opened).
- **Blocked to scripted access, not worked around**: docs.blender.org and developer.blender.org (403;
  the official source repos on projects.blender.org were read instead), helpx.adobe.com (403), metahuman.com news
  (Epic login), and unrealengine.com news (403). The MetaHuman 5.6, 5.7 and 5.8 release-notes pages on
  dev.epicgames.com rendered without content.
- **MetaHuman**: whether autorigging and texture synthesis run on Epic's servers (one Medium blog claim,
  unverified). The exact MetaHuman EULA text was not read (only CG Channel's summary). The licence files
  inside OpenRigLogic were not opened (only GitHub's SPDX "MIT").
- **Mixamo**: the marker list differs between sources (groin vs pelvis); no official 2026 status
  statement; skeleton LOD options not found; Adobe's FAQ "last updated 2021" claim not verified.
- **Daz**: whether "Daz Studio 2025" became "Daz Studio 6" (the version string 6.25.2025 suggests so, but
  no official statement was read); how JCM (joint-controlled) morphs are authored; content licence terms.
- **Substance Painter**: whether JavaScript plugins are deprecated in favour of Python (forum claim only);
  official subscription price; whether Linux is officially supported or only listed on Steam.
- **Marvelous Designer**: commercial-use terms of the Personal licence.
- **Unverified API facts left out of the sections**: Maya Python/C++, the MotionBuilder SDK, Houdini's HDK,
  C4D Python, and Blender's bpy are well known but were not re-checked this session.
- **Not researched**: 3DCoat, Style3D, Unreal Engine's Control Rig and Sequencer as an iClone-timeline
  reference, Ready Player Me and Avaturn (named by DeepMotion as character sources).
- **Conflicts noted**: ZBrush GoZ targets (Maya/Max 2026 on Maxon's page vs 2027 on ZBrushCentral);
  Houdini 22's release date (2026-07-15 on Wikipedia, 2026-07-16 on CG Channel, 2026-07-21 in a German
  roundup); ArtCraft's licence (GitHub SPDX Apache-2.0, README says MIT or Apache-2.0); MetaTailor's free
  exports (10 a month in 2024, 5 in 2026).
- RESEARCH.md §4 still needs these facts entered. Per the brief, this agent did not edit RESEARCH.md.
