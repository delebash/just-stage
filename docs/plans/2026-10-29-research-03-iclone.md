# Research 03 — iClone 8 and its plugins: complete feature inventory, data model, API

Researched 2026-10-29 by a research agent (Claude Opus 5.5) for JustStage. Clean-room: behaviour and
public docs only; no code, shaders, meshes, morphs or assets were copied. Every fact carries its
source, the source's date and whether the page was read ("page read") or only seen as a search
result ("search snippet only"). Judgement is labelled **Assessment:**.

Method note: the iClone 8 online manual's own table-of-contents data (MadCap Flare TOC, 1,126
pages, build time 2026-08-10, labelled "iClone v. 8.7 Online Manual, 2026 Aug. 07") was downloaded
and rebuilt as text (scratch file
`F:\ClaudeCode\tmp\claude\E--Dev-3D\db107297-0b13-4da2-97d8-83fb9aaa2487\scratchpad\iclone\toc.txt`).
Inventory rows marked "TOC" come from manual page **titles** only; rows marked "page read" were
opened. The session's web-search budget ran out part-way (see "Couldn't verify / open"), so Reddit
was not reached; the rest used direct page fetches.

---

## Top findings

1. **Latest is iClone 8.76, released 2026-10-29 (today); there is no iClone 9 yet.** iClone 9 was
   previewed in March–April 2026 — add bones to any model, custom control rigs, squash and stretch,
   spring dynamics with collision, retargeting — "Development is in early stages", no date.
   ([8.76 post](https://discussions.reallusion.com/t/iclone-8-76-is-now-released-ai-mesh-generator-enhanced-cloth-workflow-improvements-and-bug-fixes/18780), 2026-10-29, page read;
   [2026 preview post](https://discussions.reallusion.com/t/what-to-expect-in-2026-first-glance-at-iclones-upcoming-updates/16776), 2026-03-17, page read;
   [cgchannel roadmap](https://www.cgchannel.com/2026/04/see-reallusions-2026-roadmap-redefining-3d-with-hybrid-ai/), 2026-04-16, page read)
2. **Windows-only, DirectX 11 real-time renderer** with NVIDIA PhysX physics, voxel GI "based on
   NVIDIA VXGI", an Autodesk HumanIK-based control rig and the PopcornFX particle runtime. A path
   tracer ("RTX Render", built on NVIDIA Omniverse rendering tech) has been in open beta since
   2026-07-28, runs beside DX11, needs an RTX 3060 or better, and does not yet render terrain or
   particles. ([manual: System Requirements](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/03-Introducing-the-User-Interface/System_Requirements.htm), undated 8.x page, page read;
   [cgchannel RTX beta](https://www.cgchannel.com/2026/07/try-the-open-beta-of-rtx-render-for-character-creator-and-iclone/), 2026-07-29, page read;
   [cgchannel iClone 8.0](https://www.cgchannel.com/2022/05/reallusion-releases-iclone-8-0/), 2022-05-25, page read)
3. **Data model: one project = one timeline.** Default length 1,800 frames, maximum 54,000; frame
   rate set per project; since iClone 8 the core tick is 6,000 per second; the Python API counts time
   in milliseconds; world axes Z-up, −Y forward, right-handed. "Support for Sequences inside a
   project" is an open user request. ([manual: Time Unit](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/03-Introducing-the-User-Interface/Project_Settings_Time_Unit.htm), page read;
   [wiki: Custom FPS](https://wiki.reallusion.com/IC_8_Python_API:Dealing_With_Custom_FPS), 2022-12-01, page read;
   [wiki: IC8 Python API](https://wiki.reallusion.com/IC8_Python_API), 2023-04-10, page read;
   [FeedBackTracker by votes p.2](https://www.reallusion.com/FeedBackTracker/Product/iClone-8/2?Sort=2), read 2026-10-29)
4. **Timeline model:** nine data types (transform keys, parameter keys, clips, target-switch keys,
   lip-sync keys, voice wave, on/off, transition keys, summary keys) plus IK/FK blend keys; layer keys
   live *inside* clips and move with them; clips speed up, loop, blend, time-warp, break, merge,
   reverse, sample and flatten; project-level tracks carry camera switching, sound, HDR and IBL.
   ([manual: Data Types](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/51-Animation-Timeline-Editing/Data_Types_in_Timeline.htm), page read;
   [manual: Clips and Keys](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/51-Animation-Timeline-Editing/Clips_and_Keys.htm), page read;
   [manual: Project Level Tracks](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/51-Animation-Timeline-Editing/Project_Level_Tracks.htm), page read)
5. **The animation-editing core is layered editing over mocap/library clips:** Edit Motion Layer
   (IK/FK, effectors with blend weight, pin presets, mirror, Pose Mixer), Animation Layers per body
   part with weights, Reach Target, Motion Correction (auto foot/hand prints from ground contact),
   Motion Direction Control, and a built-in Curve Editor that handles transforms and motion-layer
   keys but **not** morphs or facial expressions. ([manual pages, see inventory](#2--feature-inventory)) 
6. **Crowd and game-style animation is a distinct strength:** Motion Director (WASD/gamepad/
   click-to-waypoint control of characters, NPCs on paths/zones/follow, behaviours, MD props) and
   8.4's crowd system (NavMesh, Walkways, Crowd Generator, Actor Groups, Prop Distributor); 8.7 added
   a paid node-graph "Motion Planning" plugin ($299 Indie). ([manual: MD Basic Concepts](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/50-Animation/Motion-Director/Basic-Concepts.htm), page read;
   [manual: 8.4 new features](https://manual.reallusion.com/iClone-8/Content/ENU/8.4/01-Welcome/New-Features-for-iC-8.4.htm), page read;
   [Motion Planning page](https://www.reallusion.com/iclone/motion-planning/), undated, page read)
7. **Mocap is a hub with paid per-device profiles:** Motion LIVE (in iClone since 8.0) takes face,
   body and hand devices at once; the Vicon profile is $1,990 and OptiTrack/Qualisys/Xsens profiles
   cost "over three times" the app; Timecode is a $299 Indie / $1,490 plugin; cloud Video Mocap is a
   free plugin with paid processing ($0.05 per second since 2026-06-08). ([cgchannel 8.53](https://www.cgchannel.com/2025/04/reallusion-releases-iclone-8-53-with-timecode-support), 2025-04-15, page read;
   [Video Mocap 1.03](https://discussions.reallusion.com/t/video-mocap-1-03-is-now-released-per-second-billing-optimized-workflows-and-bug-fixes/17410), 2026-06-01, page read)
8. **Facial animation:** AccuLips (speech-to-text → word alignment → visemes, user dictionary, TTS),
   Face Puppet, Face Key Editor (muscle / expression / morph), viseme and expression tracks, HD Face
   Control, AccuFACE 2 (webcam/video, $299 list). "Animation Layers for Expressions" is a top-voted
   missing feature. ([manual: AccuLips](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/50-Animation/Facial-Animation/Creating-Voice-Script-with-Accurate-Lipsync.htm), page read;
   [AccuFACE page](https://www.reallusion.com/iclone/motion-capture/accuface.html), undated, page read)
9. **The CC↔iClone seam is a recurring pain:** CC "Send Character to iClone" replaces the selected
   character; users report that updating bakes their keyframes and wipes visemes/AccuLips data; some
   prop edits can only be done in CC; motion-import profiles come from CC's Characterization panel.
   ([CC4 manual](https://manual.reallusion.com/Character-Creator-4/Content/ENU/4.0/17_Export/Sending_Character.htm), page read;
   [forum thread 531474](https://forum.reallusion.com/PrintTopic531474.aspx), 2023–2024, page read;
   [manual: Editing Props in CC](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/30-Set/Prop/Editing_Props_in_CC.htm), page read)
10. **Plugin model:** Reallusion lists 20 add-ons — free ones (six Auto Setups, Omniverse, Video Mocap
    plugin, AccuPOSE core, Audio2Face, AI Voice Actors, MetaHuman Live Link) and paid ones (Unreal
    Live Link, PopcornFX, Timecode, Motion Planning, BuildingGen, popVideo, Motion LIVE profiles);
    third parties sell Python plugins on the Reallusion Marketplace. ([plug-in page](https://www.reallusion.com/iclone/plug-in.html), undated, page read;
    [wiki: Marketplace plugins](https://wiki.reallusion.com/IC_Python_API:Uploading_and_Managing_Marketplace_Plugins), 2023-04-10, page read)
11. **Python API:** Python 3.8 + Qt 5.15.2 (PySide2), a subset of the C++ SDK; classes for scene,
    animation (clips, keys, controls, skeleton, face, visemes, morphs, reach, effectors), mocap
    devices, physics/cloth/hair, events, docked UI and TCP/UDP; plugins load from `Bin64\OpenPlugin`
    through `initialize_plugin()`. Users complain of missing docs. ([wiki: IC8 Python API](https://wiki.reallusion.com/IC8_Python_API), 2023-04-10, page read;
    [wiki: IC8 Modules](https://wiki.reallusion.com/IC8_Python_API:Modules), 2026-10-21, page read)
12. **Top user requests/complaints (tracker, by votes):** no way to turn off auto-keying and animated
    properties not visible on the timeline (33 votes), Sony mocopi support (29), export an animated
    rig without mesh (19), change a character's clip size in the timeline (16), apply animation to
    selected bones only (13), expression animation layers (13), Cascadeur bridge / auto-physics (10
    each), undo history lost on save and no autosave (5). ([FeedBackTracker by votes](https://www.reallusion.com/FeedBackTracker/Product/iClone-8?Sort=2), read 2026-10-29, page read)
13. **Praise:** fast character animation and "cinematic iteration", tight CC integration, mocap and
    Motion Director, approachable for beginners and solo creators. ([forum: AI Studio note](https://discussions.reallusion.com/t/a-note-to-our-community-ai-studio-the-future-of-reallusion-3d/17371), 2026-05-29, page read; G2/Renderosity search snippets only)
14. **2026 direction is AI + cloud:** AI Studio (Seedance 2.0, Kling 3.0, Veo 3 …, cloud points)
    became a separate app in 8.75; 8.76 added an AI Mesh Generator (Tripo / Hunyuan image-to-3D) next
    to a quad remesher and high-to-low baking; users push back on cloud-only, accounts and per-use
    fees. ([8.75 post](https://discussions.reallusion.com/t/iclone-8-75-is-now-released-independent-ai-studio-workflow-enhancements-and-bug-fixes/18377), 2026-09-01, page read; 8.76 post; AI Studio note)
15. **Licensing changed in 2026:** free "iClone Personal" (2026-06-23) replaced the trial — full
    editing, 30 exports of 30 s each, renders for personal/social use only; subscriptions $199/yr;
    perpetual $599. ([download page](https://www.reallusion.com/iclone/download.html), undated, page read;
    [magazine](https://magazine.reallusion.com/2026/06/23/reallusion-unlocks-limitless-creation-iclone-personal-debuts-alongside-ai-studio-official-launch/), 2026-06-23, page read;
    [cgchannel licensing](https://www.cgchannel.com/2026/01/reallusion-switches-up-iclone-and-character-creator-licensing/), 2026-01-12, page read)

---

## 1 · Latest version, iClone 9, release notes since 8.0

- Reallusion's release-notes page lists **v8.76 (8.76.5828.1), release date 2026-10-29**, 1.04 GB. — [reallusion.com/iclone/update.html](https://www.reallusion.com/iclone/update.html), 2026-10-29, page read.
- Wikipedia lists 8.7 (8.7.5009.1) as stable, dated 2026-02-12 — now outdated by 8.71–8.76. — [Wikipedia: IClone](https://en.wikipedia.org/wiki/IClone), read 2026-10-29, page read.
- **iClone 9 is not released.** Reallusion's March 2026 post previews it ("Freely add bones", "Custom Control Rigs", "Dynamic Spring and Collision") and says "Development is in early stages"; subscribers will get it "as they roll out". — [forum: What to Expect in 2026](https://discussions.reallusion.com/t/what-to-expect-in-2026-first-glance-at-iclones-upcoming-updates/16776), 2026-03-17, page read.
- The April 2026 roadmap adds "motion retargeting" and "squash and stretch" to the iClone 9 list; timing only "upcoming". — [cgchannel roadmap](https://www.cgchannel.com/2026/04/see-reallusions-2026-roadmap-redefining-3d-with-hybrid-ai/), 2026-04-16 (sponsored by Reallusion), page read.
- A forum user relays that Reallusion said no new iClone version would be announced in 2025; no staff post in that thread. Version history given there: iClone 5 2011, 6 2014, 7 2017, 8 05/2022. — [forum: iClone 9 release date](https://discussions.reallusion.com/t/iclone-9-release-date-potential/15274), 2025-09-06 → 2026-05-19, page read.

Release notes since 8.0 (iClone 8 only; forum "is now released" posts unless noted):

| Version | Date | Main changes | Source |
|---|---|---|---|
| 8.0 | 2022-05-12 | Motion Director; HumanIK-based control rig; End Effector pinning; Pose Mixer; Reach Target offsets and foot/hand prints; Curve Editor built in (was $149); Animation Layer panel; loop/blend options, bi-directional blending; volumetric light, motion blur, lens flare, mirror shader; collections, isolate, merge projects, Hotkey Manager, custom export frame rates; static object type; 3DXchange folded in (FBX import; OBJ/FBX/Alembic/USD export); $599 | [cgchannel](https://www.cgchannel.com/2022/05/reallusion-releases-iclone-8-0/), 2022-05-25, page read |
| 8.1 | not found | Morph animation + Morph Creator (manual pages sit in an `8.1` folder) | [manual TOC](https://manual.reallusion.com/iClone-8/Content/ENU/8.1/50-Animation/Morph-Animation/UI_Intro_for_Morph_Animation.htm), TOC only |
| 8.4 | not found | Crowd sim: NavMesh, Walkway, Crowd Generator, Actor Groups, avoidance; Motion Director crowd animation; Prop Distributor; Video Mocap plugin (first version) | [manual: 8.4 new features](https://manual.reallusion.com/iClone-8/Content/ENU/8.4/01-Welcome/New-Features-for-iC-8.4.htm), page read |
| 8.52 | 2024-12 | AccuPOSE AI posing (Core free from 8.52) | [cgchannel 8.52](https://www.cgchannel.com/2024/12/iclone-8-52-adds-new-ai-assisted-character-posing-system), search snippet only |
| 8.53 | 2025-04-15 | Timecode read/display/burn-in (free); Timecode plugin (paid); Vicon profile | [cgchannel 8.53](https://www.cgchannel.com/2025/04/reallusion-releases-iclone-8-53-with-timecode-support), page read |
| 8.54 | not found | Trial access to 130,000 premium assets | [forum topic title](https://discussions.reallusion.com/t/iclone-8-54-has-arrived-reallusion-unlocks-creative-potential-with-trial-access-to-130-000-premium-assets/14408), title only |
| 8.6 | 2025-08-27 | CC5 HD characters and facial profiles (CC5 required), File > Import MetaHuman Facial Animation (CC5 required), new eye occlusion/tearline shaders, extra SubD level, Facial Parts Strength, UE5-skeleton / Marmoset / UEFN FBX presets, Dynamic Mipmap, non-linear Motion LIVE curves for corrective expressions; smaller project data | [forum 8.6](https://discussions.reallusion.com/t/iclone-8-6-has-arrived-packed-with-cc5-compatibility-updates/15036), page read |
| 8.61 / 8.62 | 2025-09-10 / 2025-09-24–26 | Bug fixes | forum titles + search snippets |
| 8.63 | 2025-10-29 | New cloud Video Mocap (Quickmagic AI engine): full/upper body + fingers, multi-performer by task, auto retargeting, cleanup with Foot Contact / Auto Motion Alignment / Curve Editor / Reach Target | [forum 8.63](https://discussions.reallusion.com/t/iclone-8-63-has-arrived-precise-ai-mocap-from-any-video/15753), page read |
| 8.65 | 2026-01-06 | Subscription licensing, DA points; FBX/Unreal Live Link fixes; AccuPOSE INFINITY perpetual (v1.08) + packs | [forum 8.65](https://discussions.reallusion.com/t/iclone-8-65-is-now-released-enhanced-unreal-workflow-accupose-major-updates-and-bugs-fixes/16297), page read |
| 8.7 | 2026-01-26 (post) / 2026-02-12 (Wikipedia build date) — conflict | Fly Camera (RMB + WASD), Merge Prop (one mesh/material/texture set), mesh rename, Motion Planning plugin, Prompt Control, third-party AI API keys, USD export units cm/m | [forum 8.7](https://discussions.reallusion.com/t/iclone-8-7-is-now-released-new-motion-planning-plugin-for-simulations-fly-camera-and-bug-fixes/16478), page read |
| 8.71 | listed 2026-04-27 | Stability, 8K FBX texture export | forum title only |
| 8.72 | 2026-05-25 | AI Studio support + toolbar, startup Workspace menu | [forum 8.72](https://discussions.reallusion.com/t/iclone-8-72-is-now-released-new-ai-studio-support-workspace-menu-and-bug-fixes/17319), page read |
| 8.73 | listed 2026-07-14 | AI Studio fixes | search snippet only |
| 8.74 | 2026-07-30 | Motion LIVE: AccuFACE 2 compatibility, Expression Curve Settings ("Expression Mapping"), custom neutral; Unify Materials (by Name), Link Identical Texture Maps; FBX SDK 2020; HD content no longer needs CC5 installed | [forum 8.74](https://discussions.reallusion.com/t/iclone-8-74-is-now-released-accuface-2-compatibility-expression-mapping-and-bug-fixes/18056), page read |
| RTX Render beta | 2026-07-28 | Path tracer, separate beta build, free when final | [cgchannel](https://www.cgchannel.com/2026/07/try-the-open-beta-of-rtx-render-for-character-creator-and-iclone/), page read |
| 8.75 | 2026-09-01 | AI Studio moved out to a standalone app; capture to AI Studio from Render panel; workspace selection page removed | [forum 8.75](https://discussions.reallusion.com/t/iclone-8-75-is-now-released-independent-ai-studio-workflow-enhancements-and-bug-fixes/18377), page read |
| 8.76 | 2026-10-29 | AI Mesh Generator (concept image → mesh via Tripo H3.1 / Hunyuan V3.1 / Tripo P2.0; Tripo AI polygon reduction); Cloth Types + "Tuck-in" Cloth Conform with Shrink Wrap and Delta Mush collar smoothing; GLB import; Quad Remesher; High-to-Low Poly Baking; Collapse Sub-Props | [forum 8.76](https://discussions.reallusion.com/t/iclone-8-76-is-now-released-ai-mesh-generator-enhanced-cloth-workflow-improvements-and-bug-fixes/18780), page read |

---

## 2 · Feature inventory

### Source key for the table

| Key | Source | Date | Status |
|---|---|---|---|
| TOC | iClone 8 online manual TOC (titles), `https://manual.reallusion.com/iClone-8/Data/Tocs/New_Type_Grouped.js` | build 2026-08-10 (v8.7 manual) | titles read; pages not opened |
| M:x | iClone 8 manual page `https://manual.reallusion.com/iClone-8/Content/ENU/<x>` | undated; folder = version written for | page read |
| IC | [reallusion.com/iclone](https://www.reallusion.com/iclone/) product page + iClone 7/8 comparison table | undated, current (lists iClone Personal) | page read |
| PI | [reallusion.com/iclone/plug-in.html](https://www.reallusion.com/iclone/plug-in.html) | undated, read 2026-10-29 | page read |
| R8.x | forum release post for version 8.x (links in §1) | as in §1 | page read |
| CG22 | [cgchannel iClone 8.0](https://www.cgchannel.com/2022/05/reallusion-releases-iclone-8-0/) | 2022-05-25 | page read |

Manual page paths used below (prefix `https://manual.reallusion.com/iClone-8/Content/ENU/`):
DT = `8.0/51-Animation-Timeline-Editing/Data_Types_in_Timeline.htm`; PLT = `.../Project_Level_Tracks.htm`;
CK = `.../Clips_and_Keys.htm`; MC = `.../Motion-Correction-for-Sliding-Issues.htm`;
CC = `.../Collect_Clip_Track.htm`; FET = `.../Facial_Expression_Tracks.htm`;
EML = `8.0/50-Animation/Motion-Layer/Introducing_the_Edit_Motion_Layer_Panel.htm`;
ACL = `8.0/50-Animation/Facial-Animation/Creating-Voice-Script-with-Accurate-Lipsync.htm`;
MD = `8.0/50-Animation/Motion-Director/Basic-Concepts.htm`; CE = `8.0/58-Curve-Editor/Supported_Data_for_Curve_Editor.htm`;
IEM = `8.4/50-Animation/Import-External-Motions/Import-External-Motions.htm`; RT = `8.0/83-FBX/Motion_Retargetting.htm`;
SW = `8.0/20-Scene/Camera/Multiple_Camera_Switcher.htm`; CAM = `8.0/20-Scene/Camera/Data_for_Export_and_Import.htm`;
GI = `8.0/20-Scene/GI/GI_UI_Intro.htm`; TER = `8.0/30-Set/Terrain/The_Concept_of_Terrain_System.htm`;
WAT = `8.0/30-Set/Water/3_Types_of_Water.htm`; SKY = `8.0/30-Set/Sky/Using_Dynamic_Sky.htm`;
PAR = `8.0/30-Set/Particle/Structure_of_particle_system.htm`; PHY = `8.0/57-Physics/Dual_Physics_Engines.htm`;
SPR = `8.0/23_Spring/Spring_Settings.htm`; OUT = `8.0/80-Export/General_Export_Settings.htm`;
DOCK = `8.0/03-Introducing-the-User-Interface/Docking_Areas.htm`; TU = `8.0/03-Introducing-the-User-Interface/Project_Settings_Time_Unit.htm`.

### Inventory

| Area | Feature | What it does / how the user works it | Built in or plugin | Source |
|---|---|---|---|---|
| UI | Preview window + dock areas | Central 3D viewport; toolbars dock top/bottom (Project, General, Camera, Physics, Modify, Motion Director, NavMesh, Scatter, GI); panels dock left/right, stacked as tabs or top-down; Timeline docks bottom | Built in | M:DOCK; TOC |
| UI | Panels | Modify panel (per-object parameters), Content Manager (library), Scene Manager (outliner + collections), Project Settings, Visual Settings, Render panel, Preferences | Built in | TOC; M:DOCK |
| UI | Workspaces | Saved layouts: Standard (Ctrl+2), Animation (Ctrl+3), Visual Effect (Ctrl+4), Final Render (Ctrl+5); start-up Workspace menu since 8.72 | Built in | M:DOCK; R8.72 |
| UI | Hotkey Manager, device mapping | Rebind keys; drive tools from gamepads, MIDI boards, Stream Deck, SpaceMouse | Built in | TOC; IC |
| UI | Viewport tools | Shading modes, gizmo, pick + right-click menu, play bar with custom range, mini viewport, minimal mode, real-time smooth, quad/triangle display, Fly Camera (8.7) | Built in | TOC; R8.7 |
| UI | Performance aids | Minimal mode, reduce GPU load, ignore hidden objects, static objects (8.0: "double[s] the rendering speed for static objects"), progressive texture loading, DLSS option | Built in | TOC; CG22; R8.65; R8.6 |
| Project | Project ops | Select, world/local axis, rotation order, align objects/orientations to targets, merge projects, filter effects, replace characters/props, remove animation keeping state, share project with external files | Built in | TOC |
| Project | Project settings | Color management, time unit (frames or time), FPS, total frames (default 1,800, max 54,000), realtime vs by-frame physics stepping, display, global sound, global physics, 2D background, info | Built in | M:TU; TOC |
| Scene | Drag-and-drop set building | Drop content from Content Manager into the viewport; align/snap objects | Built in | TOC |
| Scene | Props | Create from OBJ/FBX (and GLB since 8.76), 3D Blocks, pivots, dummy props as targets for Look At / Reach / Path, duplicate | Built in | TOC; R8.76 |
| Scene | Prop animation | Puppeteer props; Simple vs Advanced mode; animation helpers; key poses + transition curves; IK/FK on boned props; perform lists for props; LiveProps (Smart Props) | Built in | TOC |
| Scene | Prop mesh tools | Merge Prop / Collapse Sub-Props, Unify Materials, Quad Remesher, High-to-Low Poly Baking (8.76); AI Mesh Generator and AI polygon reduction (cloud models, 8.76) | Built in (AI parts use third-party models) | R8.7; R8.74; R8.76 |
| Scene | Edit prop in CC | Merge identical meshes, set spring effects, smooth seams, flip faces, edit perform list, turn prop into character, sculpt — "cannot be done in iClone" | Needs Character Creator | [M: Editing_Props_in_CC](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/30-Set/Prop/Editing_Props_in_CC.htm) |
| Scene | Prop Distributor | Scatter props over NavMesh or Walkways from a distribution pool with range and generation options (8.4) | Built in | TOC; 8.4 page |
| Scene | Terrain | Height-map terrain: LOD, replaceable textures, custom height-map masks, tiled cliffs, extra material detail, physics, Snap/Follow Terrain, custom terrain from props; acts as solid ground; **one terrain per project**; not mouse-selectable | Built in | M:TER; TOC |
| Scene | Water | Three template kinds (video normal map, still image normal with moving UVs, video diffuse + video normal); colour, waves, soft edges, underwater fog, reflection, refraction | Built in | M:WAT; TOC |
| Scene | Sky / Dynamic Sky | Sky templates; Dynamic Sky simulates sun/moon paths, clouds, stars with time-elapse animation; IBL image can sync to sky | Built in | M:SKY; TOC |
| Scene | Plants | Plant trees, grow grass, SpeedTree assets (with wind) | Built in | TOC; M:OUT |
| Scene | 2D background, image layers | 2D backdrop; image layers that can be animated, reordered, combined; effects on/off per layer | Built in | TOC |
| Scene | Path to Mesh | Convert a path into mesh geometry (with listed limits) | Built in | TOC |
| Scene | Video in materials | Video files in texture channels; transparent video | Built in | TOC; IC |
| Scene | popVideo | One-click chroma key for transparent video compositing | Plugin, paid | PI |
| Scene | BuildingGen | Procedural buildings from blueprints | Plugin, paid | PI |
| Scene | Scene management | Scene Manager, custom collections, isolate, fast show/hide, asset filter, modular scenes | Built in | TOC; IC; CG22 |
| Lights | Light types | Directional, spot, point (with shadow), lights with shapes (area, fluorescent, custom/image shape), ambient; IES profiles; SSS lights for characters; light templates; auxiliary light mode; Light Tool single-menu control; intensity multiplier; decay | Built in | TOC; IC |
| Lights | Light animation | Colour and parameter tracks for spot/point; Look At for spotlights; link to targets | Built in | TOC |
| Lights | IBL | Image-based lighting from HDR images; edit image; sync to sky; animated IBL keys (IBL Strength / Transform project tracks); bake IBL for PBR reflections | Built in | TOC; M:PLT |
| Lights | Shadows | Shadow options, PCSS soft shadows, per-light shadow maps, shadow colour, shadow catcher (default project), cast on invisible plane, alpha threshold, shadow casters | Built in | TOC |
| Lights | Volumetric light | Volumetric light shafts | Built in | TOC; CG22 |
| Lights | GI | Voxel GI (VXGI per system-requirements page): ambient colour/strength, keyable bounce strength, voxel cones (max 64), multi-bounce, GI anchors; IBL, glow, self-illumination and particles can contribute; documented leak/flicker issues | Built in | M:GI; TOC |
| Camera | Cameras | Preview vs custom cameras (linear, orbit), orthographic preview, lock view, zoom/focus point, mini viewport | Built in | TOC; M:SW |
| Camera | Real Camera System | Lens, aperture, focal length, angle of view, film back; match a real camera; import/export sensor size, focal length, transform, clip planes, fit resolution; matchmove data import only | Built in | TOC; M:CAM |
| Camera | Depth of field | Focus distance, perfect focus range, blur transitions, bokeh, DOF keys on a DOF track; HQ DOF at render | Built in | TOC; M:OUT |
| Camera | Camera switching | Project > Switcher track: right-click a frame, pick the camera; preview with "Switch" camera | Built in | M:SW; M:PLT |
| Camera | Auto exposure | Histogram-based exposure, EV100 keys | Built in | TOC |
| Camera | Camera on path / look-at | Camera follows a path and looks at targets; offset line of vision | Built in | TOC |
| Visual FX | Post effects | LUT (stackable, animatable), AO (HBAO+), HDR + bloom, fog, motion blur, lens flare (layers, trigger zones, dust), toon shader / sketch, noise, NPR, lens blur, TAA, eye adaptation | Built in | TOC; IC |
| Visual FX | Reflections | Mirror shader, reflective surfaces, water reflection | Built in | TOC; IC |
| Materials | Shading | PBR and traditional shaders; Digital Human shaders (skin, head, eye, teeth/gums, tongue, hair); SSS shader; Smart Hair shader; tessellation + (vector) displacement; UV tiling/offset; linked textures; Material Plus files; material keys (animated materials) | Built in | TOC |
| Materials | Substance | Substance 3D Blocks, Substance material templates and animation, bake textures, Material Modifier (base / RGB mask / colour-ID layers) | Built in | TOC |
| Characters (iClone side) | Character handling | CC characters in Lite vs Edit mode, body proportion and scale, pose offset, ActorCore characters, RLHead from CrazyTalk, expression wrinkles, Smart Hair, layered cloth + conform, HD subdivision levels, Smart Accessories (multi-parent), Cloth Types + Tuck-in conform (8.76) | Built in (full editing in CC) | TOC; R8.6; R8.76 |
| Animation | Timeline | Per-object tracks + project tracks; track list; dope sheet with summary keys; playback range; project start/end markers; insert/delete frames; flags; copy/cut/paste; transition curves between keys; audio mute/solo | Built in | TOC; M:DT; M:PLT |
| Animation | Clip editing | Reset motion pivot, merge, transitions between clips, auto/manual extend, resize, break, Time Warp, remove body-part motion, align to remove sliding, align prop animation, speed and loop, Reset to Zero, sample/flatten keys, reverse, clear | Built in | TOC; M:CK |
| Animation | Edit Motion Layer | IK / FK / Pose Mixer tabs; full-body or body-part selection; effectors with blend weight; move/rotate/full locks; pin presets (feet, hands, toes); mirror; copy/paste pose; motion trails; hand gestures; default pose; keys layered over clips | Built in | M:EML; TOC |
| Animation | HumanIK control rig | On-screen full-body posing rig based on Autodesk HumanIK; End Effector pinning | Built in (third-party solver) | CG22 |
| Animation | Animation Layers | Layers per body part, layer weights, duplicate, merge, sample clip keys into layers | Built in | TOC; CG22 |
| Animation | Reach Target | Hands/feet reach targets; keep pose; lock un-reaching joints; effector dummies; offsets for character–prop and character–character contact | Built in | TOC; CG22 |
| Animation | Motion Correction | Right-click clip → Motion Correction: detects ground contact, creates foot/hand prints, sets Reach/Release keys; threshold, transition, offsets, reach mode; then flatten | Built in | M:MC |
| Animation | Motion Direction Control | Re-aim and align the travel direction of motion clips | Built in | TOC; IC |
| Animation | Blending / looping | Clip transitions, auto root alignment, extended looping, bi-directional blending, transition curve presets | Built in | IC; CG22 |
| Animation | Curve Editor | Graph editor with outliner, tangent types, handles, transition-curve presets, key sampling/optimising; supports transform keys, motion/animation-layer keys, path keys; **not** morph or facial-expression keys ("will be supported in a later update") | Built in since 8.0 (was $149 plugin) | M:CE; TOC; CG22 |
| Animation | Puppeteering | Motion Puppet (slider/mouse control, masks, multi-layer recording, parametric custom motions), Direct Puppet (move/rotate body parts live) → recorded as timeline clips | Built in | TOC |
| Animation | Perform list | Per-character/prop playlist of motions triggered by right-click | Built in | TOC; IC |
| Animation | Look-at | Character looks at camera/targets with weight tracks; camera and spotlight look-at | Built in | TOC |
| Animation | Path animation | Click-drawn or key-converted Bézier paths; project onto terrain; position keys on path, speed variation, offsets (angle, scale), jump between paths | Built in | TOC |
| Animation | Link / Attach | Parent objects over time (Link track) vs permanent attach | Built in | TOC |
| Animation | Morph animation | Morph tracks; Morph Creator to build morph sliders from imported shapes; send/update morph data; bake shape | Built in (8.1) | TOC |
| Animation | Spring effects | Spring bones on actors/props: mass, strength, bounciness per bone chain; Spring track | Built in | M:SPR; TOC |
| Animation | MotionPlus | One file bundling body motion, facial expression, sound, auto-load accessories and baked constraints (path, reach, link, look-at); split groups for editing | Built in | TOC |
| Animation | Collect Clip | Drag a range on the Collect Clip track to merge transform/motion/hand/layer data into a new perform clip or library motion | Built in | M:CC |
| Animation | Retargeting / import | File > Import External Motion: FBX or BVH, Motion Profile (from CC Characterization: bone map, rotations, floor contact, HIK settings), optional source T-pose, sample rate; real-time retargeting across CC characters | Built in (profiles made in CC) | M:IEM; M:RT |
| Animation | Motion Director | Behaviours (iMD files: modes → speeds → perform/mixer motions); player control by keyboard/gamepad/mouse waypoints; NPC modes (path, zone, follow, macro, flock); snap to surface, Lock Feet, avoidance; follow cameras; MD props (actionable, state switch, bi-directional, portable); radial menu; result recorded as timeline clips | Built in | M:MD; TOC; CG22 |
| Animation | Crowd sim | NavMesh generation, Walkways with flow weights, Crowd Generator with actor/accessory pools and tags, randomised materials, random start frames, Actor Groups | Built in (8.4) | TOC; 8.4 page |
| Animation | Motion Planning | Node-graph behaviour scripting for simulations (decision, random, print, composition, parallel nodes), reusable MP Sets | Plugin, paid ($299 / $499 / $1,490) | [MP page](https://www.reallusion.com/iclone/motion-planning/); R8.7 |
| Animation | AccuPOSE | AI-assisted posing; INFINITY pose library (1,400+ poses) | Core free with 8.52+; INFINITY $149 perpetual | PI; [cgchannel 2026-01](https://www.cgchannel.com/2026/01/reallusion-switches-up-iclone-and-character-creator-licensing/) |
| Animation | Motion Link | Real-time link from iClone to Cartoon Animator (2D characters) | Plugin (price not found) | [M: Using Motion Link](https://manual.reallusion.com/iClone-8/Content/ENU/8.7/50-Animation/Motion-Link/Using-Motion-Link.htm) |
| Facial | Facial profiles | Standard/HD/Extended facial profiles; corrective expressions inspection mode | Built in | TOC; R8.6 |
| Facial | AccuLips | Load audio (wav/mp3/m4a/aac/wma) or record or TTS; Generate Text (speech-to-text); fix words; Align text to waveform; Apply → visemes; user dictionary; smoothing, stylising, three levels of viseme strength; only CC characters | Built in | M:ACL; TOC |
| Facial | Talking Style Editor | Adjust talking style of lip-sync | Built in | TOC |
| Facial | Face Puppet | Record facial motion with the mouse: animation modes, strength, control area, solo features, blinking, custom puppet profiles | Built in | TOC |
| Facial | Face Key Editor | Key faces via Muscle, Expression and Modify tabs; layer editing with face keys | Built in | TOC |
| Facial | Tracks | Viseme track (lip-sync clips), Expression track (facial clips; sample to keys), Facial Layer track; smooth/downsample; Facial Parts Strength (8.6) | Built in | M:FET; R8.6 |
| Facial | HD Face Control | Panel of facial controls for HD characters, shown on timeline | Plugin, free | TOC; IC |
| Facial | MetaHuman facial import | File > Import MetaHuman Facial Animation | Built in, needs CC5 | R8.6 |
| Facial | Audio2Face / AI Voice Actors | NVIDIA Audio2Face voice-driven facial animation; AI-voice text-to-lip-sync | Plugins, free | PI |
| Mocap | Motion LIVE | One hub recording body, face and hands from several devices at once onto a character | In iClone since 8.0; device profiles paid | IC; [manual](https://manual.reallusion.com/iClone-8/Content/ENU/8.7/50-Animation/Motion-Live/Motion-Capture-with-Motion-Live.htm) |
| Mocap | Supported gear | Body: Xsens (MVN Awinda/Link), Rokoko Smartsuit Pro, Perception Neuron (V2/Pro), OptiTrack, Qualisys, Vicon. Hands: Rokoko Smartgloves, Neuron, Manus (Xsens gloves), Leap Motion 1. Face: iPhone (LIVE FACE), AccuFACE (webcam/video) | Paid profiles per device | [gears page](https://www.reallusion.com/iclone/motion-capture/gears.html), undated, page read; cgchannel 8.53 |
| Mocap | Expression mapping | Expression curve settings, neutral pose grab, partial/custom neutral, tongue options (8.74) | Built in (Motion LIVE) | R8.74 |
| Mocap | AccuFACE / AccuFACE 2 | AI face tracking from webcam, video or live feed; v2 up to 128 lip morphs, low light, NVIDIA RTX or AMD | Plugin, paid ($299 list) | [AccuFACE page](https://www.reallusion.com/iclone/motion-capture/accuface.html) |
| Mocap | Video Mocap | Upload video → cloud AI → editable body (+fingers) motion; multi-performer as separate tasks; reference video as viewport background | Plugin free; processing $0.05/s | R8.63; Video Mocap 1.03 |
| Mocap | Timecode | Core: read/display/burn-in timecode from MOV/MP4/MKV/WAV/FBX. Plugin: Master Clock in Motion LIVE, snap clips to timecode, timecode in FBX and Unreal Live Link, Tentacle Sync, RED R3D, PeelCapture | Core built in; plugin $299 Indie / $1,490 | cgchannel 8.53; [Timecode page](https://www.reallusion.com/iclone/timecode/) |
| Physics | Engines | NVIDIA PhysX (characters, props, accessories: physics characters, rigid body, soft cloth); legacy Bullet only plays iClone 5 projects | Built in | M:PHY |
| Physics | Rigid bodies | States static/dynamic/kinematic with state keys; mass pivot; boundings; initial motion; link/unlink with state keys; bake to clips | Built in | TOC |
| Physics | Constraints | Hinge, slider, point-to-point, cone twist, spring; limits, breaking, chains, bolts (intermediate dummies) | Built in | TOC |
| Physics | Soft cloth | Weight maps (load/edit), solver frequency, drag, stretch/elasticity/tether, bending, inertia, collision, wind; bake results; character collision shape editor | Built in | TOC |
| Physics | Global settings | Global physics settings; realtime vs by-frame time mode | Built in | TOC; M:TU |
| FX | Native particles | Legacy image-particle emitters (volume, gizmo, link, follow path); on/off keys start/stop emitters | Built in | M:PAR; M:DT |
| FX | PopcornFX | Real-time particle runtime + library; effects authored in the bundled free PopcornFX Editor; lit by and colliding with the scene (see RESEARCH.md §3) | Plugin, paid (price not found) | [PopcornFX page](https://www.reallusion.com/iclone/vfx/popcornfx/), undated, page read; PI |
| Render | Real-time render | DX11 render to image (TGA/PNG with alpha, JPG/BMP) or video (MP4, WMV, AVI); custom size up to 4K; preview/final quality; anti-aliasing; HQ DOF; glow in alpha; noise against banding; range via Mark In/Out; discard simulation warm-up frames | Built in | M:OUT; download page |
| Render | Special output | 360° panorama video, stereo 3D, alpha video, batch rendering, output at viewport size | Built in | TOC; IC |
| Render | RTX Render | Path tracer (beta) built on Omniverse tech: SSS, real-camera DOF, transmission/coat/sheen materials, hair controls, 55 materials, 18 portrait light presets; toggle with DX11 | Built in when final (free); beta build now | cgchannel 2026-07-29 |
| Render | AI Render / AI Studio | AI image/video from 3D previs (Seedance 2.0, Kling 3.0, Veo 3, Flux …) on Reallusion's cloud with points; AI Studio now a standalone app | Cloud service, paid points | magazine 2026-06-23; R8.75 |
| Render | Omniverse | Send project/items as USD to NVIDIA USD Composer; Live Sync (8.3); materials to MDL; camera switch baked to one camera | Plugin (Connector), free | [Omniverse page](https://www.reallusion.com/iclone/nvidia-omniverse/default.html), install guide updated 2026-01-14, page read |
| Audio | Sound | Project Sound track (music/SFX); audio on actors and props; mute/solo audio tracks; global sound settings; record voice; TTS; sound inside MotionPlus | Built in | M:PLT; TOC; [wiki capabilities](https://wiki.reallusion.com/IC_Python_API:Uses_and_Capabilities) |
| Pipeline | Import | OBJ, FBX (mesh, material, motion), Alembic (same vertex count), GLB (8.76), BVH motion, USD (via Omniverse), iClone/CC native files | Built in | IC; M:IEM; R8.76 |
| Pipeline | FBX export | Bone rig, animation, blendshapes; presets UE4/UE5 skeleton, UEFN, Unity, Blender, Maya, 3ds Max, Marmoset; T-pose bind; delete hidden faces/unused morphs; batch export; expressions as morph meshes; 8K textures | Built in | IC; TOC; R8.6; R8.71 |
| Pipeline | Alembic / USD / OBJ export | Alembic with range, sampling, split by material, world space, material mapping; USD for Omniverse (units cm/m since 8.7); static OBJ | Built in | TOC; IC; R8.7 |
| Pipeline | Auto Setup ×6 | One-click character/shader setup in Unreal, Unity, Blender, Maya, 3ds Max, Marmoset Toolbag | Plugins, free | PI |
| Pipeline | Unreal Live Link | Send characters, lights, cameras; stream body/face animation into UE; two-way link and timecode sync (v1.1) | Plugin, paid ("Indie Free/Paid" on IC table) | [Live Link page](https://www.reallusion.com/iclone/live-link/unreal-engine/), undated, page read |
| Pipeline | MetaHuman Live Link | Drive MetaHumans' face, body and voice lip-sync from iClone | Plugin, free | PI |
| Pipeline | Blender Data Link | Two-way characters, poses, motions, lights, cameras between Blender and CC/iClone | Free add-on (GPL-3.0, soupday) | [github.com/soupday/cc_blender_tools](https://github.com/soupday/cc_blender_tools), page read |
| Content | Libraries and stores | Content Manager, Smart Gallery (free), 2,000+ free assets, Content Store, ActorCore/AccuRig, Marketplace, AI smart search | Built in + stores | IC; PI |

Assessment: the inventory is broad but much of the scene side (one height-map terrain per project,
video-texture water, legacy particles, voxel GI) is older real-time tech; the animation side
(layered editing over clips, motion correction, crowd/MD, mocap hub) is where iClone is distinctive.

---

## 3 · CC5 ↔ iClone hand-off (send, update, round trip)

- CC → iClone: **File > Export > Send Character to iClone** or the Project toolbar button. If a character is selected in iClone it is **replaced**; otherwise the new one is **added**; iClone launches if not running. To update, edit in CC and send again — no need to save a file each time. — [CC4 manual: Sending Character](https://manual.reallusion.com/Character-Creator-4/Content/ENU/4.0/17_Export/Sending_Character.htm), undated (CC4), page read.
- iClone → CC: users describe selecting the character, **Edit in Character Creator**, editing, then Send to iClone; a pop-up asks whether to switch to the CC pose, and "No" keeps the iClone animation. — [forum 531474](https://forum.reallusion.com/PrintTopic531474.aspx), posts 2023-01-24 and "2–3 years ago", page read.
- What breaks: the update "bakes any keyframes you've created down"; another user lost viseme and AccuLips data; workarounds are re-importing and pasting tracks back (which can crash). — same thread, page read.
- Some prop work is CC-only (merge meshes, spring effects, seams, flip faces, perform list, prop→character, sculpting). — [iClone manual](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/30-Set/Prop/Editing_Props_in_CC.htm), page read.
- Motion travels back too: **Timeline > Collect Clip > Send Motion to Character Creator** (fixed in 8.76). — [8.76 post](https://discussions.reallusion.com/t/iclone-8-76-is-now-released-ai-mesh-generator-enhanced-cloth-workflow-improvements-and-bug-fixes/18780), page read.
- Motion-import profiles (bone map, HIK settings) are made in CC's Characterization panel. — [iClone manual: Import External Motions](https://manual.reallusion.com/iClone-8/Content/ENU/8.4/50-Animation/Import-External-Motions/Import-External-Motions.htm), page read.
- Generation pairing: CC4 ↔ iClone 8 ("Only same-generation software syncs"). — [kb.reallusion.com](https://kb.reallusion.com/Print53039.aspx), search snippet only.
- CC5 HD characters/facial profiles need iClone 8.6+ and, until 8.74, CC5 installed; 8.74 says "HD Content no longer requires Character Creator 5 to be installed". — [8.6 post](https://discussions.reallusion.com/t/iclone-8-6-has-arrived-packed-with-cc5-compatibility-updates/15036), 2025-08-27; [8.74 post](https://discussions.reallusion.com/t/iclone-8-74-is-now-released-accuface-2-compatibility-expression-mapping-and-bug-fixes/18056), 2026-07-30; both page read.
- CC5 files with subdivision levels, eyelash parts, corrective expressions or HD facial profiles will not open in iClone 8.6 without CC5. — [CC5 FAQ](https://faq.reallusion.com/en/Product/Character-Creator/Character_Creator_5), search snippet only.
- Cross-app user pain: "Updating a model in CC doesn't refresh it in iClone without importing and exporting, which overwrites work." — forum 531474 (paraphrase by fetch tool), page read.

Assessment: the two-app split is itself the source of the worst data-loss reports. A single app
with one document holding character and animation removes the send/update seam; the standard to
set is that character edits never rewrite existing animation keys.

---

## 4 · Plugins — official and third-party

| Plugin | What it does | Built in / plugin | Price | Source |
|---|---|---|---|---|
| Motion LIVE | Multi-device face/body/hand mocap hub | In iClone 8 | Included ($599 perpetual includes it) | IC compare table, page read |
| Motion LIVE gear profiles | One profile per device family | Plugin | Vicon $1,990; OptiTrack/Qualisys/Xsens "over three times" iClone; others paid, prices not found | cgchannel 2025-04-15, page read |
| LIVE FACE | iPhone face capture into Motion LIVE | Plugin/profile | Not found | gears page, page read |
| AccuFACE 2 | AI face tracking (webcam/video/live) | Plugin | $299 list ($224 promo; $199 upgrade) | AccuFACE page, undated, page read |
| Video Mocap | Cloud video-to-motion | Plugin free | $0.05/s processing (from 2026-06-08; was 250 DA points ≈ $2.50 per ≤60 s task) | Video Mocap 1.03 post 2026-06-01; cgchannel 2025-10-31; page read |
| AccuPOSE | AI posing; INFINITY pose library | Core free (8.52+) | INFINITY $149 perpetual (was $99/yr) | cgchannel 2026-01-12, page read |
| Timecode | Master clock, timecode in FBX/Live Link | Plugin | $299 Indie (<$100k/yr) / $1,490 | cgchannel 2025-04-15; Timecode page; page read |
| Motion Planning | Node-graph agent behaviour | Plugin | $299 Indie / $499 combo / $1,490 | MP page, page read |
| BuildingGen | Procedural buildings | Plugin | Paid, price not found | PI, page read |
| PopcornFX | Particle runtime + editor + library | Plugin | Paid, price not found | PI; PopcornFX page |
| popVideo | Chroma-key transparent video | Plugin | Paid, price not found | PI |
| Unreal Live Link | Live transfer/stream to UE | Plugin | Paid; IC table says "Indie Free/Paid" | PI; IC |
| MetaHuman Live Link | Animate MetaHumans | Plugin | Free | PI |
| Omniverse Connector | USD + Live Sync to USD Composer | Plugin | Free | PI; Omniverse page |
| Auto Setup (UE, Unity, Blender, Maya, 3ds Max, Marmoset) | One-click import + shader setup | Plugins | Free | PI |
| Audio2Face | NVIDIA voice-to-face | Plugin | Free | PI |
| AI Voice Actors | AI voice text-to-lip-sync | Plugin | Free | PI |
| Smart Gallery | Content browsing/management | Plugin | Free | IC |
| HD Face Control | HD facial control panel | Plugin | Free | IC; TOC |
| Motion Link | iClone → Cartoon Animator 2D link | Plugin | Not found | manual, page read |
| AI Studio / AI Render | Cloud AI image/video from 3D | Separate app / service | Points; plans Starter/Standard/Pro | magazine 2026-06-23; R8.75 |
| Curve Editor | Graph editor | Built in since 8.0 | Was $149 | CG22 |
| 3DXchange | Old import/export add-on | Discontinued; folded into 8.0 | Was $199 / $499 | CG22; IC |
| Character Creator | Character creation app | Separate app | $299 perpetual; $99/yr | cgchannel 2026-01-12 |
| **Third-party:** CC/iC Blender Tools | Blender import + Data Link round trip | Free add-on (soupday) | Free, GPL-3.0 | GitHub, page read |
| **Third-party:** Marketplace Python plugins | Any developer can list paid/free Python plugins per iClone version | Marketplace | Developer-set | wiki 2023-04-10, page read |

- Personal (free) edition gets only trial versions of Motion Planning, Timecode, BuildingGen, PopcornFX and Unreal Live Link; Video Mocap, AccuPOSE, Auto Setups and Omniverse are free in all editions. — [download page](https://www.reallusion.com/iclone/download.html), undated, page read.
- Bundles: iClone 365 $59/mo or $199/yr; CC 365 $29/mo or $99/yr; Reallusion 3D Suite 365 $129/mo or $599/yr; "Pro" subscriptions include add-ons (not listed). — [cgchannel 2026-01-12](https://www.cgchannel.com/2026/01/reallusion-switches-up-iclone-and-character-creator-licensing/), page read.

### Licences (one line each; no legal analysis)

- iClone 8 perpetual/subscription — Reallusion EULA; commercial use **yes**; the page linked from the download page is https://www.reallusion.com/Content/EULA/EULA.htm.
- Reallusion content (the page above is the "Reallusion Content End User License Agreement", updated 2025-08-01, page read) — Standard License; commercial **conditional**: images and video yes, 3D art derived from content personal-only, export to FBX/OBJ "requires the acquisition of a Standard License", no sublicensing, no AI training, models must stay protected so they "cannot be opened or imported into a publicly available software application"; lapsed one-year plans turn saved files into watermarked trial content.
- iClone Personal — same EULA + Personal limits; commercial use **no** for renders ("personal and social use only"), 30 exports of 30 s; https://www.reallusion.com/iclone/download.html (page read).
- AI Studio outputs — AI Cloud plan terms; commercial **conditional** (Standard/Pro yes, Starter/Free no); https://ai.reallusion.com/plans.html (not opened; terms from magazine 2026-06-23).
- Trial content in any edition — watermarked exports; commercial **no**; download page.
- Motion LIVE profiles, Timecode, Motion Planning — Reallusion EULA, Indie tiers by revenue; commercial **conditional** (tier); product pages.
- ActorCore assets — ActorCore-specific licence page returned empty; commercial **unclear** beyond the Content EULA above; https://actorcore.reallusion.com/license.
- Python samples (github.com/reallusion/iClone) — Reallusion EULA, no open-source licence; commercial **unclear**.
- CC/iC Blender Tools — GPL-3.0; commercial **yes** under GPL terms; https://github.com/soupday/cc_blender_tools.
- PopcornFX Editor — bundled "free" per Reallusion; editor licence not read; commercial **unclear**; https://www.reallusion.com/iclone/vfx/popcornfx/.
- Omniverse Connector — free; NVIDIA Omniverse terms separate; commercial **unclear**.
- Video Mocap outputs — terms not read; commercial **unclear**.

---

## 5 · Data model: scene and animation

- **Project file** `.iProject`; iProject files "remain uncompressed" while mesh/animation data compression was optimised in 8.6. — [8.6 post](https://discussions.reallusion.com/t/iclone-8-6-has-arrived-packed-with-cc5-compatibility-updates/15036), page read.
- **Native asset formats** (import list): iAvatar (character), iCloth, iMotion, rlMotion, iMotionPlus, iAtm (atmosphere), iEffect, iProp; plus iTalk (facial/talk script), iMD (Motion Director behaviour), iPkfx (PopcornFX). — [IC page](https://www.reallusion.com/iclone/), page read; cgchannel 8.53; [manual TOC](https://manual.reallusion.com/iClone-8/Data/Tocs/New_Type_Grouped.js); RLPy release notes (iPkfx).
- Timecode is stored natively in iMotion, iMotionPlus, iTalk and iProject. — [cgchannel 8.53](https://www.cgchannel.com/2025/04/reallusion-releases-iclone-8-53-with-timecode-support), 2025-04-15, page read.
- **MotionPlus** bundles body motion, facial expression, sound, auto-load accessories and baked constraint results (path, reach, link, look-at). — manual TOC titles (MotionPlus, Smart Accessory sections), TOC only.
- **Length and rate:** default 1,800 frames, max 54,000 frames per project; FPS chosen per project from a list; time shown as time or frames. — [manual: Time Unit](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/03-Introducing-the-User-Interface/Project_Settings_Time_Unit.htm), page read.
- **Time base:** iClone 8 raised the core tick from 1,000 to 6,000 per second ("1 tick equals 1/6000 seconds"); `RFps` lists supported rates (e.g. 24, 60, 120); keys are added without an FPS argument in 8. — [wiki: Custom FPS](https://wiki.reallusion.com/IC_8_Python_API:Dealing_With_Custom_FPS), 2022-12-01, page read.
- **Python conventions:** Z-up, −Y forward, right-handed; rotations as quaternion, matrix or Euler radians; scale 1 = 100 %; time 1 = 1 ms. — [wiki: IC8 Python API](https://wiki.reallusion.com/IC8_Python_API), 2023-04-10, page read.
- **One timeline per project:** "Support for Sequences inside a project" is an open request (8 votes, 2023-01-10). — [FeedBackTracker p.2](https://www.reallusion.com/FeedBackTracker/Product/iClone-8/2?Sort=2), page read.
- **Timeline data types:** transform key (props: move/rotate/scale; actors, cameras, lights: move/rotate only), parameter key (light colour/range/beam, camera focal length; interpolated), clip, target-switching key (Look At, Link To), lip-sync key, voice wave, on/off (visibility, emitter start/stop), transition key (Reach, Path, Spring tracks), summary key (dope sheet); IK blend keys (linear path) and FK blend keys (curved). — [manual: Data Types](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/51-Animation-Timeline-Editing/Data_Types_in_Timeline.htm), page read.
- **Clips own their layer keys:** layer keys are "encased in the motion / animation clips", move with the clip and "can not be moved outside the range of the clip"; solid keys = all axes keyed, hollow = some; gesture clips are sub-tracks of the motion clip; Sample blends gesture data into finger tracks, Flatten merges layers into the clip. — [manual: Clips and Keys](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/51-Animation-Timeline-Editing/Clips_and_Keys.htm), page read.
- **Track tree:** project tracks (Project, Switcher, Sound, HDR, IBL Strength, IBL Transform, effect groups); general tracks (Transform, Visible, IBL, GI); actor tracks (Motion with per-bone sub-tracks and Gesture, Motion Layer, Viseme, Expression, Facial Layer); shared private tracks (Collect Clip, Spring, Look-at weight, Look At, Link, Material, Morph); camera (Lens, DOF); lights (Color, Parameter); iProp Animation Layer. — [manual: Project Level Tracks](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/51-Animation-Timeline-Editing/Project_Level_Tracks.htm), page read; TOC titles.
- **Animation layers** exist for body parts with weights, duplicate and merge; **not** for expressions (top request, 13 votes). — TOC; [FeedBackTracker by votes](https://www.reallusion.com/FeedBackTracker/Product/iClone-8?Sort=2), page read.
- Characters are called **actors** on the timeline and in crowd tools ("Actor Private Tracks", "Spawning Actors"). — manual TOC, TOC only.
- Physics results and Motion Director runs are baked into ordinary timeline clips. — TOC ("How to bake animation clips from Physics simulation"); [manual: MD](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/50-Animation/Motion-Director/Basic-Concepts.htm) (recording not described on the page read).

Assessment: the model is "clips with embedded layer keys on per-object tracks, one timeline per
project, fixed tick". For JustStage's standard, the user requests point at: every animated property
visible as a track, auto-key optional, layers for every channel (including face), bone masks on any
clip, and more than one sequence per project.

---

## 6 · Python API

- iClone 8 uses **Python 3.8 and Qt 5.15.2**; PySide2 must be initialised; motion-bone functions such as `GetMotionBones()` were removed in 8. — [wiki: IC8 Python API](https://wiki.reallusion.com/IC8_Python_API), 2023-04-10, page read.
- The Python SDK sits "on top of the iClone C++ SDK" and exposes a subset. — [wiki: Uses and Capabilities](https://wiki.reallusion.com/IC_Python_API:Uses_and_Capabilities), 2020-07-21 (iClone 7 era), page read.
- Module groups: Mathematics, System, Scene, Animation, MotionCapture, Events, UI, Media, Networking. iC8 classes include `RIClip`, `RKey`, `RControl`, `RFloatControl`, `RTransformControl`, `RISkeletonComponent`, `RIHikEffectorComponent`, `RIMorphComponent`, `RIFaceComponent`, `RIVisemeComponent`, `RIReach`, `RIEffector`, `RIMotionDirectorManager`, `RIPhysicsComponent`, `RICloth`, `RIHair`, `RIMocapManager` + body/hand/facial device classes, `ROpenPoseKeyPointParam`, `RICamera` + `RCameraDofData`, `RRealtimeRenderOptions`, `RSaveFileSetting`, `RExportFbxSetting`, `RExportGlbSetting`, `RSaveMotionPlusOption`; events `REventCallback`, `RIEventListener`, timers; UI `RIDialog`, `RIDockWidget`, `RUi`; media `RAudio`, `RAudioRecorder`; network `RTcpClient`, `RUdpClient`. — [wiki: IC8 Modules](https://wiki.reallusion.com/IC8_Python_API:Modules), last modified 2026-10-21, page read.
- Capabilities (iClone 7 list): load iProject/iAvatar/iProp; animate props and play motion clips; FK bone rotation; key morph sliders; audio on objects; materials; cameras and lights; keyboard/mouse/joystick input; TCP/IP messages; event callbacks (load, selection, parameter change, timer); batch render scripts; timeline keys. — wiki 2020-07-21, page read.
- Limits (iClone 7 list, "not exhaustive"): cannot save iClone formats, change render or project settings, manipulate SpeedTree/Substance/constraints/physics/mesh components/preview camera, key lip-sync, attach/detach, or do image processing. **Conflict:** iC8 modules now include `RSaveFileSetting`, `RIPhysicsComponent`, `RIReach` and `RRealtimeRenderOptions`, so parts of this list are likely outdated — not verified per function. — wiki 2020 vs wiki modules 2026-10-21.
- Events added in 7.x: `OnObjectDataChangedWithType`, `OnHierarchyChanged`, `RIGlobal.ObjectModified`; `LoadObject`/`LoadFile` take an undo-recording flag. — [wiki: RLPy Release Notes](https://wiki.reallusion.com/IC_Python_API:RLPy_Release_Notes), 2020-02-20, page read.
- Plugin loading: copy folders into `Bin64\OpenPlugin`, run from the Plugins menu; a plugin needs `initialize_plugin()` or it fails to load. — [github.com/reallusion/iClone](https://github.com/reallusion/iClone), 201 commits, last commit 2025-09-09 "Upload Mocap Sample" (GitHub API), page read; wiki "Your First iClone Python Plugin", search snippet only.
- Official samples: AudioDriven, BatchRenderFolder, Camera_Auto_Focus, Camera_Dolly_Zoom, GroupManager, HandGesturesPuppeteering, JointDrivenMorph, Keyboard, LightRemoteControl, MocapSample, PopcornFX_Sequencer_Demo, Pose_Manager, SampleRequests, SmoothCameraFollow, SpringJoints — under the Reallusion EULA. — GitHub, page read.
- Mocap devices can be added through the Python API ("other gear can be integrated … Motion LIVE provides a Python API"). — [gears page](https://www.reallusion.com/iclone/motion-capture/gears.html), page read.
- Users report missing class docs and iClone 7 samples failing in 8. — [forum: requesting docs](https://discussions.reallusion.com/t/requesting-for-wiki-docs-for-the-python-api-for-classes-without-docs-yet/12628), search snippet only.
- Wikipedia also lists Lua scripting (legacy). — Wikipedia, page read; not verified elsewhere.

Assessment: the API is an embedded in-process Python scripting layer with UI hooks, not an external
service API; outside apps reach iClone through bespoke links (Live Link, Data Link, Omniverse Live
Sync, TCP/UDP from scripts). JustStage's "API other apps connect to" has no direct iClone model to
copy beyond that.

---

## 7 · What iClone is built on; system requirements; platforms

- Real-time playback uses "a 3D game engine for instant on-screen rendering"; DX11 since iClone 6. — [Wikipedia](https://en.wikipedia.org/wiki/IClone), page read.
- DirectX 11 required; real-time GI "based on NVIDIA VXGI". — [manual: System Requirements](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/03-Introducing-the-User-Interface/System_Requirements.htm), undated 8.0 page, page read.
- NVIDIA PhysX for characters, props, cloth; Bullet kept only for iClone 5 projects. — [manual: Dual Physics Engines](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/57-Physics/Dual_Physics_Engines.htm), page read.
- Control rig based on Autodesk HumanIK. — CG22, page read.
- PopcornFX runtime (Persistant Studios), SpeedTree, Substance, HBAO+, DLSS, FBX SDK 2020, Qt 5.15.2 / Python 3.8. — PopcornFX page; TOC; IC; R8.6/R8.76 (DLSS); R8.74 (FBX SDK); IC8 wiki.
- RTX Render is built on NVIDIA Omniverse rendering tech and sits beside DX11. — cgchannel 2026-07-29, page read.
- Video Mocap uses Quickmagic's AI engine; AI Mesh Generator uses Tripo and Hunyuan models. — R8.63; R8.76.
- **Current requirements** (download page): Windows 10/11; min Intel 7th-gen i5, 16 GB RAM, 8 GB VRAM (GTX 10 / RX 5500 XT); recommended 10th-gen i5, 64 GB RAM, 16 GB VRAM (RTX 20 series); 30 GB install + 200 GB DDS cache; subscription needs a continuous connection. **Conflict:** the older manual page lists GTX 900 / 4 GB VRAM / 8 GB RAM. — [download page](https://www.reallusion.com/iclone/download.html), page read; manual page above.
- RTX Render: NVIDIA only, min RTX 3060, recommended RTX 4070 Super. — cgchannel 2026-07-29, page read.
- **Platform: Windows only** (no macOS or Linux). — download page; Wikipedia; cgchannel.

Assessment: the dev machine (RTX 2070 Super 8 GB, 32 GB) meets iClone's current minimum but not RTX
Render's; a cross-platform JustStage cannot lean on DX11, VXGI, PhysX-on-Windows-only or HumanIK.

---

## 8 · What users praise; most common complaints

Praise
- "Its greatest strength is enabling rapid character animation and cinematic iteration" and tight CC integration (JimDHart). — [forum: AI Studio note](https://discussions.reallusion.com/t/a-note-to-our-community-ai-studio-the-future-of-reallusion-3d/17371), 2026-05-29, page read.
- Having tools in one application simplifies workflow (Delphoi_Studio). — same thread, page read.
- Motion Director and Motion Direction Control are upgrade reasons; good for beginners. — Renderosity "iClone 8 Versus 7", search snippet only (site unreachable).
- Interface intuitive; works well with CC. — G2 summary, search snippet only.
- Motion LIVE as one hub for face/body/hands; mocap tools. — IC page, page read; review sites, search snippet only.

Complaints (FeedBackTracker sorted by votes, 1,136 issues; read 2026-10-29)
- Need option to disable auto-keyframing; every animated property should be visible in the Timeline — 33 votes, 2023-05-03.
- Sony mocopi support — 29, 2023-01-12.
- Export animated rig without mesh/textures — 19, 2022-07-04.
- Change the size (length) of a character's clip in the timeline — 16, 2022-06-30.
- Apply animation to selected bones only — 13, 2023-01-20.
- Animation layers for expressions — 13, 2022-06-29.
- iClone ↔ Cascadeur bridge; Cascadeur-style auto-physics — 10 each.
- Updated Curve Editor documentation — 10; morph issues — 9; mini viewport — 9; sequences inside a project — 8; hair/cloth physics to Omniverse — 8; PlantFactory — 7; legacy particle life bugs — 7; rigging essentials — 7; custom animations in Motion Director — 6; "Rendering in iClone Needs to be Improved Badly" — 5 (2026-03-08); FBX export with multiple named animations — 5; undo history removed after save / no autosave — 5.
  — [page 1](https://www.reallusion.com/FeedBackTracker/Product/iClone-8?Sort=2), [page 2](https://www.reallusion.com/FeedBackTracker/Product/iClone-8/2?Sort=2), page read.
- Recent tracker titles: "AccuLips (English): Major overhaul needed", "Iclone 8 needs better landscaping", back-face textures, imported motions no longer importing correctly. — [tracker recent](https://www.reallusion.com/FeedBackTracker/Product/iClone-8/1), page read.
- CC↔iClone updates bake keys and lose visemes/AccuLips data (§3). — forum 531474, page read.
- Cost ("It Costs way too much"), bugs, upgrade "gimmic[k]s". — [forum: iClone 9 thread](https://discussions.reallusion.com/t/iclone-9-release-date-potential/15274), page read.
- AI direction: fear of rising cloud costs, wish for local models (LTX, WAN), objection to mandatory accounts and per-use fees. — AI Studio note thread, 2026-05-29+, page read.
- Crash/hang reports (curve-editor smoothing, Face Puppet recording); post-update viewport slowdowns. — FeedBackTracker and forum, search snippets; 8.63 thread, page read.
- Python API documentation gaps. — forum, search snippet only.
- **Conflict:** a user says AccuLips lacks WAV support, but the manual lists wav as an input format. — AI Studio note thread vs [manual: AccuLips](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/50-Animation/Facial-Animation/Creating-Voice-Script-with-Accurate-Lipsync.htm).

Assessment: complaints cluster on (1) timeline transparency and control (auto-key, hidden animated
properties, bone masks, expression layers, sequences), (2) the CC↔iClone seam, (3) pipeline export
flexibility, (4) cost and paid-per-device mocap, (5) the cloud-AI turn. All five map to JustStage
standards rather than to features.

---

## Couldn't verify / open

- **Web-search budget ran out** mid-research (session limit). Reddit was not reachable (search
  budget gone; a direct fetch of old.reddit.com was refused by the tool, not worked around);
  praise/complaint coverage relies on Reallusion's forum and FeedBackTracker, which skew to engaged
  users. Renderosity (DNS failure) and Software Advice (403) were unreachable.
- Motion LIVE workflow (connect, characterise, calibrate, record, multi-actor) — the mocap manual
  page returned empty; protocols per device (e.g. which use network streaming) not found.
- Prices not found: PopcornFX, popVideo, BuildingGen, Unreal Live Link (current), LIVE FACE,
  Motion Link, most Motion LIVE gear profiles.
- Licence texts not read: the software EULA (only the Content EULA was read), the ActorCore-specific
  licence, the PopcornFX editor licence, Video Mocap output terms.
- Third-party plugins beyond the Blender tools: Marketplace Python plugin titles were not listed.
- Release dates for 8.1–8.5x not found; 8.7's date conflicts (forum post 2026-01-26 vs Wikipedia
  build 2026-02-12).
- Python API: the 2020 limits list versus iC8 classes was not checked function by function; no
  public list of iC8 events found; whether the API can drive the timeline structure (create tracks,
  layers) is unknown.
- Hair physics: iClone 8 has an `RIHair` class and Smart Hair, but how hair simulates (soft cloth
  vs dedicated solver) was not confirmed.
- Native particle parameters and PopcornFX in-iClone editing/keying details beyond RESEARCH.md §3
  were not found on the pages read.
- iClone 9 feature details and dates beyond the March–April 2026 previews — none public.
- The AI Mesh Generator's processing location (cloud vs local) and pricing were not stated in the
  8.76 post.
- Morph Creator, Persona, Smart Accessory and Talking Style Editor pages were seen as TOC titles
  only.
