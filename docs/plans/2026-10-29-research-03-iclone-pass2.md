# Research 03, second pass — iClone 8: the gaps round one left open

Researched 2026-10-29 by a second-pass research agent (Claude Opus 5.5) for JustStage, section S2 of
[`2026-10-29-research-second-pass.md`](2026-10-29-research-second-pass.md). Round one:
[`2026-10-29-research-03-iclone.md`](2026-10-29-research-03-iclone.md). Clean-room: behaviour and public docs
only; nothing copied but short quotes. Every fact carries its source, the source's date and whether the page
was read ("page read") or only seen as a search result ("search snippet only"). Judgement is labelled
**Assessment:** and kept apart from facts.

Method note: about 40 web searches were used. Most facts come from pages read directly — the manuals' own
MadCap table-of-contents data, Reallusion's official version-history data file, the public JSON endpoints that
Reallusion's own store and Marketplace pages call (store prices, Marketplace search), the wiki's MediaWiki API
and the forum's Discourse JSON. No downloads of installers, models or datasets; scratch files are in
`F:\ClaudeCode\tmp\claude\E--Dev-3D\db107297-0b13-4da2-97d8-83fb9aaa2487\scratchpad\pass2-s2\`. Blocked and not
worked around: Reddit (the search tool refuses the domain), Capterra, G2 and GetApp (HTTP 403).

---

## Top findings

1. **Every iClone 8 build now has an official date.** Reallusion's version-history data file lists 8.0
   (2022-05-12) through 8.76 (2026-10-29). The 8.7 conflict is settled: there were two 8.7 builds,
   8.7.4923.1 on 2026-01-26 and 8.7.5009.1 on 2026-02-12. No 8.54 build exists; "8.54" was a 2025-06-26
   announcement about AI Smart Search and trial access to content.
   ([version history](https://www.reallusion.com/iclone/iclone-version-history.html), read 2026-10-29, page read;
   [forum 8.54 topic](https://discussions.reallusion.com/t/14408), 2025-06-26, page read)
2. **Correction to round one: the maximum project length is 216,000 frames, not 54,000.** 8.3 (2023-06-19):
   "Maximum project duration is lengthened from 54 to 216 thousand frames." The manual's Time Unit page is
   out of date. ([version history](https://www.reallusion.com/iclone/iclone-version-history.html), page read)
3. **Current list prices, from Reallusion's own store data (2026-10-29):** Unreal Live Link $1,490 (free for
   indies under $100K a year who own iClone 8), iPhone Live Face $399, Perception Neuron profile $999, Rokoko
   full-body profile (hands included) $999, Xsens / Vicon / OptiTrack / Qualisys profiles $1,990 each,
   PopcornFX 3-in-1 $267, popVideo 3 Suite $168 (legacy, no 4K), BuildingGen $199. A 40–50 % sale was running.
   Motion Link is free for iClone buyers.
   ([store price API behind the pricing page](https://www.reallusion.com/plan-and-pricing/individual/perpetual/perception-neuron-3049), read 2026-10-29, page read;
   [Indie page](https://www.reallusion.com/iclone/live-link/unreal-engine/indie.html), undated, page read)
4. **How Motion LIVE works:** each capture device runs its vendor's own app. That app streams to an IP:port
   on the local network, and the Motion LIVE panel in iClone receives the stream. Inside Motion LIVE the user
   adds gear to a Gear List (saved as JSON), assigns Face / Body / Hand gear to each character, maps several
   actors from the vendor app's actor list, sets TCFPS (timecode FPS) to keep timing in sync, then clicks
   Preview and Record and presses Space to run them. Face capture has New / Blend / Replace modes; body
   capture can be recorded one body part at a time.
   ([Motion LIVE manual](https://manual.reallusion.com/Motion_LIVE_Plugin/Content/Motion_LIVE/1/Workflow_for_Motion_Live.htm), build 2026-07-30, page read)
5. **Device protocols:** Xsens MVN uses its Network Streamer over **UDP, port 9763**. The LIVE FACE iPhone app
   connects over Wi-Fi, USB or Ethernet on **port 999**. AccuFACE 2 runs its own **TCP** server port. Rokoko
   Studio sends body and hands on separate ports. OptiTrack Motive uses its data-streaming pane. Qualisys QTM
   uses "Real-Time Output" on a fixed port. Vicon Shogun Live uses its DataStream port. Perception Neuron goes
   through the Axis Neuron app, and Leap Motion through its local control panel. Each vendor expects the
   T-pose to face a different axis; iClone faces −Y.
   ([device pages](https://manual.reallusion.com/Motion_LIVE_Plugin/Content/Motion_LIVE/1/Xsens_for_iClone.htm), page read)
6. **The AI Mesh Generator runs in Reallusion's cloud and costs AI Points.** The rate is 1 USD = 100 points,
   and a mesh costs 12–160 points ($0.12–$1.60), depending on the model (Hunyuan 3.1 Pro, Tripo H3.1, Tripo
   P2.0) and options. Plans: Free $0 with 500 points, Starter $11 a month, Standard $35, Pro $95.
   ([AI Cloud plans](https://ai.reallusion.com/plans.html), read 2026-10-29, page read)
7. **Correction to round one on AI output rights:** the AI Service EULA (dated 2026-10-29) grants commercial
   use on **Starter, Standard and Pro**; Free is "for testing and evaluation purposes only". Round one had
   Starter as non-commercial. The same EULA covers Video Mocap output, and it lets Reallusion train its AI on
   content set to "Public".
   ([AI Service EULA](https://www.reallusion.com/Content/EULA/AI-Service.htm), 2026-10-29, page read)
8. **Software EULA (dated 2026-05-25):** with a perpetual or active subscription licence, the user may sell
   images and video. Models and animations may be distributed only when embedded in games, apps or 3D prints.
   CC avatars' topology and rigs stay Reallusion's property, and AI training on them is barred.
   ([Software EULA](https://www.reallusion.com/Content/EULA/AP/EULA_AP.htm), 2026-05-25, page read)
9. **The Python API now does most of what the 2020 "can't" list ruled out:** save files and projects, undo and
   redo with named action blocks (`BeginAction` / `EndAction`), set render options and project length, key
   visemes, re-parent and link objects, key IK reach targets, edit soft-cloth physics, read and write mesh
   vertices, and switch cameras. Still not exposed: SpeedTree, Substance materials, preferences, an FPS setter,
   rigid-body settings and springs. ([IC8 class pages](https://wiki.reallusion.com/IC8_Python_API:Modules), last edited 2026-10-21, page read;
   [2020 limits](https://wiki.reallusion.com/IC_Python_API:Uses_and_Capabilities), 2020-07-22, page read)
10. **Python can create and edit clips, not tracks or layers.** It can add, break, merge, mirror, sample,
    flatten and delete clips (body, face and viseme), and add, move or remove keys on any control. There is no
    AddTrack or AddLayer; layer keys are reached through a clip's "Layer" control. The API has 51 event
    callbacks, including `OnUndoRedoDone`, `OnObjectDataChangedWithType` and `OnCurrentTimeChanged`.
    ([RISkeletonComponent](https://wiki.reallusion.com/IC8_Python_API:RLPy_RISkeletonComponent),
    [REventCallback](https://wiki.reallusion.com/IC8_Python_API:RLPy_REventCallback), 2026-10-21, page read)
11. **The Marketplace lists 60 iClone Python plugins.** 15 are Reallusion's own (all free except one); the
    other 45 come from third parties and are priced in DA points (100 points = $1). Examples: an ElevenLabs voice-over
    generator, a "Kimodo" motion generator, Dollars markerless mocap (free), face-animation importers, a visual
    morph controller, a plugin manager, and builders for buildings, stairs, roads and debris.
    ([Marketplace search API](https://marketplace.reallusion.com/), read 2026-10-29, page read)
12. **Hair simulates as PhysX soft cloth.** It is the same physics component as cloth, with weight maps and
    "Hair" presets, and no separate solver. Native particles are billboard-sprite emitters. PopcornFX effects
    are made in the PopcornFX Editor and imported; inside iClone every exposed attribute gets its own timeline
    track with keys, and attributes not exposed in the Editor can't be reached.
    ([manual: Soft Cloth for Characters](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/57-Physics/Soft_Cloth_for_Characters.htm), page read;
    [PopcornFX technology page](https://www.reallusion.com/iclone/vfx/popcornfx/technology.html), page read;
    [forum tips](https://forum.reallusion.com/PrintTopic351131.aspx), about 2017, page read)
13. **Opinion outside Reallusion's own channels is split.** Reallusion's TrustScore on Trustpilot is 1.7 / 5
    from 60 reviews (support, pricing, licensing, stability, an unintuitive UI). Daz, Blender Artists and
    Unreal forum users praise fast animation, IK and lip-sync but cite "hidden costs", add-on prices, weak
    rendering and the work needed to animate well.
    ([Trustpilot](https://ie.trustpilot.com/review/reallusion.com), read 2026-10-29, page read;
    [Daz forum](https://www.daz3d.com/forums/discussion/567936/iclone-8-and-cc4-anyone), 2022, page read)
14. **The four tools round one saw only as titles:**
    - Persona is an AML (Action XML) file of idles, keyboard movement behaviours and perform actions.
    - Smart Accessory (8.5) gives accessories several parent bones with stored offsets, several materials,
      and auto-loading with MotionPlus.
    - The Talking Style Editor scales each viseme's strength (default 100).
    - Morph Creator works as a round trip: export the base mesh as OBJ, sculpt targets in another tool,
      import them as sliders, then send or update the result in iClone.

    ([manual pages](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/10-Avatar/Persona.htm), page read)
15. **ActorCore assets fall under the Content EULA**, which names ActorCore among "Reallusion's Stores". The
    ActorCore licence pages are script-only. A staff post says games need a free "Mass Distribution License".
    ([Content EULA](https://www.reallusion.com/Content/EULA/EULA.htm), updated 2025-08-01, page read; staff
    post via search snippet only)

---

## 1 · Praise and complaints outside Reallusion's forum and tracker

**Reddit:** the search tool refuses reddit.com ("not accessible to our user agent"), and round one found the
same for direct fetches. Not worked around, so no Reddit data.

**Review aggregators**
- Capterra: 4.4 / 5 from 10 reviews. Pros: "easy to use. No steep learning curve", drag-and-drop FBX/OBJ.
  Cons: "So super expensive for beginners", weak simulation and character behaviour, the Unreal Live Link
  "showed so much promise but delivered very little", no Maya-style facial control, "nickel and dime you".
  — [capterra.com reviews](https://www.capterra.com/p/237893/iClone/reviews/), reviews dated about 2022–2023,
  search snippet only (the page returns 403).
- Software Advice: 4.4 / 5 from 10 reviews (ease of use 4.6, support 4.2, features 4.6). —
  [softwareadvice.com.au](https://www.softwareadvice.com.au/software/328914/iclone), search snippet only.
- G2: 4.8 / 5 from 13 reviews; G2 names Blender as the top alternative. —
  [G2 alternatives](https://www.g2.com/products/iclone/competitors/alternatives/mid-market), search snippet
  only (the page returns 403).
- Trustpilot (company-wide, not iClone only): TrustScore 1.7, 60 reviews, mostly 1-star, 2022–2026. Themes:
  - support ("Great software, absolutely useless support", 2025-12-09);
  - price ("Unbelievably exaggerated prices for the software alone", 2026-03-12);
  - stability ("The most unstable 'mainstream' software I've ever used", 2025-12-03);
  - licensing ("The licensing is the worst in the business", CC4, 2025-08-12);
  - usability ("the interface is just a nightmare", 2026-08-31; "Absolutely not intuitive", iClone and CC5,
    updated 2026-05-12);
  - billing ("they take money yearly with no warning", 2026-09-05);
  - one 5-star review: "Quality software isnt cheap" (2026-06-17).

  — [ie.trustpilot.com](https://ie.trustpilot.com/review/reallusion.com), read 2026-10-29, page read.

**Independent forums**
- Daz 3D forum, "iClone 8 and CC4 anyone?", May–July 2022:
  - Praise: "iClone's posing/anim toolset and physics toolset is obviously better than DAZ's"; "I can put
    together a scene in iClone within minutes"; "iClone itself on the otherhand is easy to use".
  - Complaints: price ("it got real expensive, real quick", "too expensive"); deformation ("their characters
    deform horribly compared to G8s"); value for Blender or UE5 users ("it offers nothing we dont already
    have"); launch bugs ("many teething problems").

  — [daz3d.com thread 567936](https://www.daz3d.com/forums/discussion/567936/iclone-8-and-cc4-anyone), page read.
- Daz 3D forum, other threads (2022–2023): the render engine and VFX make iClone "a non starter as delivery
  output platform"; "the UI is so bad"; geografts unsupported; DAZ figures lose JCM and MCM correctives in
  iClone. — [Daz forum search results](https://www.daz3d.com/forums/discussion/566906/), search snippet only.
- Blender Artists, 2021-07/08:
  - Cost: "The cost factor is a major drawback"; "a minimum of $400 USD" to start.
  - "Reallusion is just an expensive Blender add-on for the artistically challenged".
  - Praise: lip-sync and iClone's IK.

  — [blenderartists.org thread 1319006](https://blenderartists.org/t/reallusion-iclone-character-creator-headshot-etc/1319006), page read.
- Unreal Engine forums, "DAZ Studio vs Iclone. The lesser evil?", 2018–2020: "Iclone gets expensive real fast
  due to hidden costs"; "it does have a lot of good things going for it"; "a lot of hidden costs they
  conveniently don't tell you about upfront" (2020-12-17). —
  [forums.unrealengine.com 109259](https://forums.unrealengine.com/t/daz-studio-vs-iclone-the-lesser-evil/109259), page read.
- Unreal Engine forums, UE5.1 pipeline thread, 2022-12 to 2025-04: creating characters "seems fine" but
  "trying to get it to animate properly takes a LOT of work … still seems unfinished" (2023-05-01); the
  original poster later moved to Maya + Advanced Skeleton. —
  [forums.unrealengine.com 734808](https://forums.unrealengine.com/t/ue5-1-animation-pipeline-metahuman-or-real-illusion-cc4-characters-for-iclone-livelink/734808), page read.
- Unreal Engine forums, "Iclone to Unreal", 2020-01 to 2020-04:
  - Pros: faster animation tuning.
  - Cons: paid add-ons for the curve editor and 3DXchange (both since folded into iClone 8); Live Link
    animation can't be baked in Unreal (staff: record it with Take Recorder); physics doesn't transfer.
  - A user: "buying another software just to export bought fbx models is kind of overkill".

  — [forums.unrealengine.com 136700](https://forums.unrealengine.com/t/iclone-to-unreal/136700), page read.

**Video reviews:** titles only. Examples: "Iclone 8 is a broken piece of crap" (King of Iclone), "iClone 8
Released … First Impressions", "iClone is Now FREE! iClone 8 Personal Explained". —
[YouTube search](https://www.youtube.com/watch?v=kumR-bPQ0jc), dates not shown, search snippet only.

**Press:** CG Channel says iClone Personal "can be used on commercial projects" but is limited to "30 lifetime
exports to other 3D applications", and its native and RTX renders are licensed for personal use only. —
[cgchannel](https://www.cgchannel.com/?p=176884), 2026-06-24, page read. Digital Production's piece is
labelled an advertorial: renders are "personal and social use only". —
[digitalproduction.com](https://digitalproduction.com/2026/06/25/iclone-personal-is-free-now/), 2026-06-25,
page read.

Assessment: outside opinion matches round one's tracker themes and adds three: lock-in cost ("hidden costs",
paid per-device profiles), render quality not good enough for final output, and figures from other ecosystems
(Daz) deforming badly once imported. Praise is steady too: fast animation, lip-sync, IK and mocap.

---

## 2 · Motion LIVE: workflow and device protocols

Source: the separate Motion LIVE plugin manual (MadCap; HelpSystem build time 2026-07-30). Prefix
`https://manual.reallusion.com/Motion_LIVE_Plugin/Content/Motion_LIVE/`. Pages are undated; all were page read.
The iClone manual's own Motion LIVE page only links here.

**Data path**
- "Capturing Devices" → "Plug-ins (standalone)" (the vendor's app) → "Motion LIVE plug-in in iClone" → the
  virtual character. — `1/Workflow_for_Motion_Live.htm`.

**Connect**
- Plugins > Motion LIVE > Motion LIVE. Under Gear List, click "+" in the Face, Body or Hand row and pick a
  device. It appears with a hollow green circle; clicking the circle connects it, and the circle turns solid.
  — `1/Workflow_for_Motion_Live_Body.htm`.
- The Connection field takes "the IP and Port where the gear software is installed" if the gear runs on
  another PC on the intranet. The Actors column shows how many actors the gear detects. — `1/UI_Intro_for_Motion_Live.htm`.
- Gear lists save to and load from `*.json`, to share setups across PCs on a LAN. — `1/Saving_and_Loading_Server_List.htm`.
- Profiles: download the purchased profile installer from the member account, then install the vendor's own
  software (Faceware Realtime, Axis Neuron, Leap Motion). — `1/Getting_Gear_Profiles.htm`.

**Characterise, calibrate, orient**
- Calibration happens in the vendor app, for example Axis Neuron's four-pose calibration. — `1/Perception_Neuron_for_iClone.htm`.
- T-pose facing per vendor: iClone faces −Y; Vicon uses its default; OptiTrack +Z; Xsens +X; Perception
  Neuron +Z; Rokoko +Z. — `1.1/Setting-T-Pose-Direction.htm`.
- The manual recommends turning off Foot Contact before body capture. — `1/Workflow_for_Motion_Live_Body.htm`.
- Facial neutral pose: "Set Zero Pose" (LIVE FACE), grab neutral, grab neutral per part, custom neutral
  (AccuFACE 2), and Faceware neutral calibration. — `1/Workflow_for_Motion_Live_Face_iPhoneX.htm`,
  `1/Calibrating_Neutral_Expression.htm`, TOC titles.
- Character position: Mocap Data Location (align to the real actors' positions), iClone Specified Location,
  or Aligning to Source. — `1/Characters_Orientations_and_Positions.htm`, `1/Mocap_Data_Location.htm`.

**Record**
- In the Character List, assign a device per Face / Body / Hand column. Click Preview, then Space; click
  Record, then Space. — `1/Workflow_for_Motion_Live_Body.htm`.
- Options: auto-save MotionPlus after recording, with timecode; "Remote Trigger" port; Start with Motion
  Director; Full-Frame Recording (timecode) "regardless of system performance"; Timecode settings appear if
  that plugin is installed. — `1/UI_Intro_for_Motion_Live.htm`.
- Face capture modes: New, Blend and Replace. — `1/Animation-Modes.htm`.
- Body capture can be done per body part (multi-layer), with Full Body or Upper Body modes. — `1/Multi_Layer_Capturing_Body.htm`.
- FPS sync: enter the device's timecode FPS (TCFPS) and match the project FPS, or keys land between frames. — `1.1/Synchronizing-FPS-for-Mocapping.htm`.

**Several actors**
- One gear can drive several characters; several gears can drive one character; several gears can drive
  several characters. — `1/Multi_Gears_Controlling_Multi_Characters.htm` and siblings (TOC).
- For multi-actor gear (for example Vicon / Shogun), click the device icon in a character's Body cell and pick
  that performer from the sub-menu. — `1.1/Multi-Characters-Motion-Capturing.htm`.

**Device protocols (each from its "Device Settings" page)**

| Device | Vendor app | How data reaches iClone | Source page |
|---|---|---|---|
| Xsens (Awinda, Link) | MVN Animate Pro ("Must") | Network Streamer: host IP, **port 9763, protocol UDP**, "Position + Orientation (Euler)" | `1/Xsens_for_iClone.htm` |
| Rokoko Smartsuit Pro | Rokoko Studio ("Must") | Older: Settings > Network Settings, "Forward Data" IP and port. v1.19: Live Stream, iClone tile, one port for hands and one for the body | `1/Rokoko_for_iClone.htm`, `1/Rokoko-119-for-iClone.htm` |
| OptiTrack | Motive | Live mode, View > Data Streaming Pane; same IP:Port in the Gear List; FPS set in both | `1/OptiTrack_for_iClone.htm` |
| Qualisys | Qualisys Track Manager | Play > "Play with Real-Time Output"; "the IP : Port is fixed and can not be edit"; iClone 7.4+ | `1/Qualisys_for_iClone.htm` |
| Vicon | Shogun Live (VST 3.6 / 3.7 skeletons) | DataStream section, Live/Offline port; IP of the local machine; TCFPS; "Only iClone 8.5 and Motion LIVE 1.1 supports Vicon" | `1.1/Vicon-for-iClone.htm` |
| Perception Neuron (V2, Pro) | Axis Neuron (Noitom) | Vendor app connects to the suits; the page names no port | `1/Perception_Neuron_for_iClone.htm` |
| Leap Motion | Leap Motion Control Panel | Local vendor service on the same PC; no network settings on the page | `1/Leap_Motion_for_iClone.htm` |
| iPhone (LIVE FACE) | LIVE FACE app | Same network over Wi-Fi, hotspot, USB tethering or Ethernet; type the phone's IP, "leave the port number '999'"; USB recommended | `1/Connecting_to_LIVE_Face.htm`, `1/Workflow_for_Motion_Live_Face_iPhoneX.htm` |
| AccuFACE 2 | AccuFACE 2 app (webcam or video) | IP shown in the app; "Set Server TCP Port" | `AccuFACE-2/Connecting-AccuFACE-and-iClone.htm` |
| Faceware | Faceware Realtime for iClone | Standalone vendor app | `1/Workflow_for_Motion_Live_Face.htm` |

- Other gear can be added through the Python API. `RIMocapManager` offers AddBodyDevice, AddFacialDevice,
  AddHandDevice, Start and Stop; `RIBodyDevice` offers ProcessData and SetTPoseData. —
  [RIMocapManager](https://wiki.reallusion.com/IC8_Python_API:RLPy_RIMocapManager),
  [RIBodyDevice](https://wiki.reallusion.com/IC8_Python_API:RLPy_RIBodyDevice), 2026-10-21, page read.
- Full-Frame Recording (timecode) first supported LIVE FACE iPhone, AccuFACE, Xsens, Rokoko and Rokoko Smart
  Gloves (8.33, 2023-11-06), then Perception Neuron (2023-11-16). —
  [version history](https://www.reallusion.com/iclone/iclone-version-history.html), page read.

Assessment: Motion LIVE is a hub of per-vendor network receivers, not one protocol. Each profile wraps one
vendor's own stream. An open equivalent would speak the open or vendor-documented streams directly (VMC,
Xsens UDP, Rokoko's JSON forward, OptiTrack NatNet, Vicon DataStream, the QTM RT protocol). JustStage would
need one shared T-pose and axis normaliser, because every vendor faces a different way.

---

## 3 · Prices

All rows below come from the JSON price endpoint (`api.reallusion.com/onlinestore/v1/products/prices`) that
Reallusion's own pricing page calls, matched to product names from that page's data. They were read
2026-10-29 (page read). "List" is the regular price; "sale" is the promotion running that day.

| Product | List (USD) | Sale on 2026-10-29 | Note |
|---|---|---|---|
| iClone 8 (perpetual) | 599 | not read | ContentID `BIC8001…` |
| Unreal LiveLink | 1,490 | 894 | Free for indies: under USD 100,000 a year, owners of "the full version of iClone 8", one licence per user or organisation, schools excluded — [indie page](https://www.reallusion.com/iclone/live-link/unreal-engine/indie.html), undated, page read |
| iPhone Live Face | 399 | 239.40 | Motion LIVE face profile |
| Perception Neuron profile | 999 | 599.40 | |
| Rokoko Full-Body profile (hand profile included) | 999 | 599.40 | |
| Xsens profile | 1,990 | 995 | |
| Vicon profile | 1,990 | 995 | |
| OptiTrack profile | 1,990 | 995 | |
| Qualisys profile | 1,990 | 995 | |
| AccuFACE 2 | 299 | 179.40 | |
| AccuFACE 2 + Ultra Head Sampler | 448 | 268.80 | |
| AccuPOSE INFINITY | 149 | 89.40 | |
| Timecode (Indie) / Timecode | 299 / 1,490 | 179.40 / 894 | |
| Motion Planning (Indie) / Core Bundle (Indie) / full | 299 / 499 / 1,490 | 179.40 / 299.40 / 894 | |
| BuildingGen | 199 | 119.40 | Launch MSRP was also $199 — [cgchannel](https://www.cgchannel.com/2024/04/reallusion-releases-buildinggen-for-iclone/), 2024-04-18, search snippet only |
| PopcornFX 3-in-1 | 267 | 133.50 | "PopcornFX Plugin, PopcornFX Library 40, PopcornFX Particle Sequencer"; the 2017 launch price was $179 — [ProVideo Coalition](https://www.provideocoalition.com/iclone-popcornfx-now-offer-realtime-vfx-3d-platform/), 2017, search snippet only |
| popVideo 3 Suite (+ Super VFX 200) | 168 | 84 | "This is a legacy product and does not support 4K resolution" |

- Motion Link: "Motion Link Plugin … *Free for iClone purchase users"; the Motion Link Profile is "*Free for
  Motion LIVE 2D purchase users"; installed from Reallusion Hub; Windows only. —
  [Motion Link page](https://www.reallusion.com/cartoon-animator/motion-link), undated, page read.
- The store's add-on list on 2026-10-29 offers no Faceware, Leap Motion, Manus or glove-only profile. —
  [pricing page](https://www.reallusion.com/plan-and-pricing/individual/perpetual/perception-neuron-3049), page read.
- Older figures, for history: a Faceware profile at "RRP $1590, Presale Price $990" (2022 forum post);
  Perception Neuron profile $999 (2018); Motion LIVE hand bundle from $249 and full-body bundle from $2,000
  at the 2018 launch. — [ProVideo Coalition 2018](https://www.provideocoalition.com/reallusion-introduces-motion-live-a-full-body-motion-capture-solution/),
  [forum](https://forum.reallusion.com/PrintTopic513516.aspx), search snippet only.
- The product pages themselves render prices with script, so a plain page read shows none. —
  [plug-in page](https://www.reallusion.com/iclone/plug-in.html), page read.

Assessment: a full professional mocap setup on iClone costs $1,990 per optical or inertial vendor profile, on
top of the $599 app; even consumer suits need a $999 profile. The per-device paywall is the single largest
cost in the iClone pipeline.

---

## 4 · Third-party Python plugins on the Reallusion Marketplace

Source: the Marketplace search endpoint (`api.reallusion.com/Marketplace20/v1/Content/OpenSearch`, filter
CategoryID "ic", CatalogLevel1 "Plug-in") that marketplace.reallusion.com calls; read 2026-10-29, page read.
**60 iClone plug-in listings.** Prices are in DA points; "DA Points and AI Points have a 1:1 exchange value"
and "1 USD = 100 AI Points" ([AI plans](https://ai.reallusion.com/plans.html), page read), so 1,000 points =
$10. "ver" is the supported iClone version range as listed (793 = 7.93, 874 = 8.74).

Third-party, one line each (author · points · versions):
- BB EZ Lighting Wizard, BB EZ Prop Controller, BB EZ MultiMAT Tweeker, BB EZ CAM Controller — Bigboss · 1,950 each · 7.93–8.00 (one 7.70–8.00).
- Building Creator, Light Pipes Controller, Ceiling Fan Creator, Chair Builder (free), Image Rotator (free), Candle Python Script (free) — Data Juggler · 0–700 · 7.7–7.9.
- CC UV Master Editor (8.74), Visual Morph Controller (8.72) — José Tijerín · 1,200 each.
- RM3D Texture Text Generator (390), RM3D GLB Importer (100), RM3D Kimodo Motion Generator (1,080; 8.65–8.72), RM3D Advanced Math Primitives Generator (510), RM3D Field Generator (1,080) — remark3dcz · 8.40–8.72.
- ElevenLabs Voiceover Generator — CyberMerch · 1,500 · 8.72.
- TaskNotes (2,495), Plugin Manager (999) — jlittle · 7.90–8.00.
- Debris Generator (500), Ex-Static (750), ShakyCam Plus (750), Building Blocks (1,000), MIDI Piano Player (free), Stair Builder (free), MIDI Drummer (free) — G-Tools · 7.7–8.00.
- BonesPositionScanner (8.41), PropToCharacter AttachPlus 1.1 (8.60) — OldFatherThames2 · 100 each.
- AnimCutter Iclone8 — olegTOB · 1,000 · 8.70.
- Boids — pine · free · 7.90.
- iGroup RL (999), UV-Bone Mapper – Eyes (free), iText RL (1,990) — 3DEA · 7.5–7.7.
- Midi Controller — Alex Kuo · free · 7.50.
- Spring Joints Plus iC8 — Lex3D · free · 8.52.
- Blend Camera — Morlochi · 500 · 8.30.
- PRO Face Animation Importer (5,000), LITE Face Animation Importer (free) — Virtual Filmer · 8.40.
- Motion Trigger 2.1 — ZongYe · 1,500 · 7.8–8.00.
- Dollars MoCap iClone8 Plugin (markerless mocap) — SunnyView Tech · free · 8.00–8.72.
- CONTINUITY SCRIPT GENERATOR — glaunay · 1,000 · 8.50.
- Road Builder — RLin · free · 7.93.
- Camera Fly Through — kyo · free · 7.50.
- HEAT Tools — HEAT · free · 8.30.

Reallusion's own Marketplace plugins (all free except one): NVIDIA Audio2Face for iClone 8, Light Remote
Control, Smooth Camera Follow 2.0, Hand Gestures Puppeteering 2.0, Pose Manager, Camera Auto-Focus, Batch
Render Folder, Audio Driven, Joint Driven Morph, Group Manager, Omniverse Audio2Face (Beta, iClone 7), Camera
Dolly Zoom, Spring Joints, Musical Keyboard, and the PopcornFX Particle Sequencer (850 points).

- Install: download from the Marketplace plugin inventory, picking the build for your version; unzip into
  `Bin64\OpenPlugin`; or use Script > Load Python on `main.py`. —
  [kb.reallusion.com](https://kb.reallusion.com/ExportPDF53202.aspx), search snippet only.
- A plugin is a folder holding `main.py` with `initialize_plugin()` ("If this functions do not exist in the
  file, the plugin will fail to load"). — [wiki: Your First iClone Python Plugin](https://wiki.reallusion.com/IC_Python_API:Your_First_iClone_Python_Plugin), page read (re-checks round one's snippet).
- A third-party developer (Data_Juggler): "I stopped building IClone Plugins because they broke everything in
  IClone 8". — [forum topic 12628](https://discussions.reallusion.com/t/12628), 2024-11-26, page read.

Assessment: the plugin market is small (60 listings over seven years) and mostly utilities: lighting,
cameras, builders, MIDI, voice. Many listings stop at iClone 7.9 or 8.0, which matches the developer's
complaint above that the 8.0 API change broke plugins. The only plugin in the list that is a separate AI
service is ElevenLabs voice-over.

---

## 5 · Release dates 8.0–8.76

Source: Reallusion's version-history data file, which `update.html` loads, at
[iclone-version-history.html](https://www.reallusion.com/iclone/iclone-version-history.html); read 2026-10-29,
page read. One line per build, with the headline from its notes.

| Build | Date | Headline (from the notes) |
|---|---|---|
| 8.0 | 2022-05-12 | Grand launch |
| 8.01 / 8.02 | 2022-06-01 / 2022-07-20 | — |
| 8.1 | 2022-09-29 | Motion Director Snap to Surface; subdivision export (FBX, OBJ, USD); Morph Animator "Bake Shape"; Motion LIVE facial mocap inside Motion Director; hair needs Physics on for soft-body intercollision |
| 8.11 / 8.12 | 2022-10-17 / 2022-11-17 | Fixes / Smart Content Manager |
| 8.2 (8.2.1421.1) | 2023-02-23 | Look-at realism, Expression Wrinkles, deferred texture loading |
| 8.21 / 8.22 / 8.23 | 2023-03-16 / 04-13 / 05-23 | Fixes; FBX export writes a JSON for Auto Setup |
| 8.3 (8.3.1815.1) | 2023-06-19 | **Maximum project duration 54K → 216K frames**; MD trigger paging |
| 8.31 | 2023-08-02 | Omniverse Connector 8.3 Live Sync (official) |
| 8.32 | 2023-10-16 | ZBrush Face Tools 1.0 compatibility |
| 8.33 | 2023-11-06 and 2023-11-16 | AccuFACE 1.0; Motion LIVE Full-Frame Recording (timecode) |
| 8.4 | 2023-12-06 and 2024-01-09 | Crowd simulation |
| 8.41 | 2024-04-17 | BuildingGen 1.0; path → mesh; EXR image render; FBX expressions as pure morphs |
| 8.42 | 2024-06-19 | BuildingGen optimisation, Prop Distribution Z offset |
| 8.5 | 2024-09-05, 2024-09-06, 2024-10-04 | Prop Interaction (five MD Prop templates) and Smart Accessory |
| 8.51 | 2024-11-04 | AI Smart Search across stores |
| 8.52 | 2024-11-28 and 2024-12-10 | AccuPOSE; curve filters (Butterworth, Peak Removal …); Motion Trail; non-destructive Break |
| 8.53 | 2025-04-14 and 2025-04-21 | Timecode, Vicon |
| (8.54) | 2025-06-26 | Not a build: a forum announcement of AI Smart Search and trial access to 130,000 assets — [forum 14408](https://discussions.reallusion.com/t/14408), page read |
| 8.6 | 2025-08-27 | CC5 compatibility |
| 8.61 / 8.62 | 2025-09-09 / 2025-09-24 | Fixes |
| 8.63 | 2025-10-29 and 2025-12-04 | Video Mocap |
| 8.65 | 2026-01-06 | Subscription licensing |
| 8.7 | **2026-01-26 (8.7.4923.1) and 2026-02-12 (8.7.5009.1)** | Motion Planning, Fly Camera. Settles round one's conflict: the forum post marks the first build, Wikipedia the second |
| 8.71 | 2026-04-27 and 2026-05-06 | Stability, 8K textures |
| 8.72 | 2026-05-25 | AI Studio support |
| 8.73 | 2026-06-23 and 2026-07-13 | AI Studio fixes |
| 8.74 | 2026-07-29 | AccuFACE 2, expression mapping (round one had the forum post's 07-30) |
| 8.75 | 2026-09-01 | AI Studio becomes a separate app |
| 8.76 | 2026-10-29 | AI Mesh Generator, Cloth Types, GLB import, Quad Remesher, high-to-low baking |

- Release cadence before iClone 8: 7.0 came out on 2017-06-20 and 7.93 last on 2021-11-15. — same file, page read.

---

## 6 · Python API: the 2020 limits against iC8, the events, tracks / layers / clips

Sources: the wiki's IC8 class pages, read as wikitext through the MediaWiki API (165 IC8 pages; the class pages
checked were last edited 2026-10-21), and the 2020 "Uses and Capabilities" page (last edited 2020-07-22). All
page read. Prefix `https://wiki.reallusion.com/IC8_Python_API:RLPy_`.

**2020 limits, item by item, against the iC8 functions**

| 2020 limit ("can not … with Python") | iC8 status | iC8 functions found |
|---|---|---|
| SpeedTrees | Still absent | No SpeedTree class among the 165 pages |
| Substance materials | Mostly absent | `RFileIO.LoadSubstancePainterTextures` only (loads Painter textures) |
| Texture images | Now possible | `RIMaterialComponent.LoadImageToTexture`, `SetImage`, `GetImage`, `LoadShaderTexture`, `RemoveMaterialTexture`; `RIImage.LoadFile` / `SaveFile` / `SetImageData` / `GetQImage` |
| Constraints: path, spring, look-at, physics | Partly | Path: `RIObject.FollowPath` / `ReleasePath`. Link: `LinkTo` / `UnLink` / `RemoveLinkKey`. Look-at: `RILookAtComponent.AddLookAtKey`. Reach: `RIReach`, `RIHikEffectorComponent.AddReachKey`. Spring: no class found |
| Physics (soft and rigid) | Soft only | `RIPhysicsComponent`: `SetActivatePhysicsEnable`, `SetObjectGravityEnable`, `Set/GetSoftPhysXProperty`, `SetSoftPhysXCollisionValue`, soft-cloth weight-map get/set/save. No rigid-body parameters found. `RGlobal.SetPhysicsSimulationLoop` |
| IK end-effectors | Now possible | `RIHikEffectorComponent`: `AddReachKey`, `SetPosition`, `SetLock`, `SetActive`, `SetBodyWeight`, `Solve`; `RISkeletonComponent.GetEffector`, `BakeFkToIk` |
| Mesh components (vertices, edges, faces) | Partly | `RIMesh`: `GetVertices`, `SetWorldVertices`, `GetFace`, `DeleteFaces`, selection get/set, `ReplaceMesh`. `RMeshTool`: `RunBasicRepair`, `RunFixNonManifoldPoly`, `Uvatlas`, `BakeTexture`, `ProjectToHighPoly`, transient mesh previews |
| Preview camera | Now possible | `RScene.GetCurrentCamera` / `SetCurrentCamera`, `AddSwitchCameraKey`; `RICamera.SetWorldView`, `SetCameraLocation`, DOF and focal-length keys |
| Saving iClone formats | Now possible | `RFileIO.SaveFile` (with `RSaveFileSetting`), `SaveProject`, `LoadProject`; also `ExportFbxFile` / `ExportGlbFile` / `ExportObjFile` / `ExportUsdFile` / `ExportBvhFile` / `ExportGoZFile` |
| Pixel operations, image processing | Partly | `RIImage` gives raw image data and a Qt `QImage`, so processing is done in Python; no built-in filters |
| Render parameters (project settings) | Mostly possible | `RGlobal.SetRealtimeRenderOptions`, `SetRenderExportParameter`, `SetRenderExportType`, `SetProjectLength`, `SetStartTime` / `SetEndTime`, preview range; render calls for image, sequence, video and audio, **plus depth, normal, Canny and OpenPose-keypoint passes**. No FPS setter (`GetFps` only) |
| Facial lip-sync keying | Now possible | `RIVisemeComponent`: `AddVisemeKey`, `AddVisemesClip`, `AddVisemesClipWithData`, `LoadVocal`, `TextToSpeech`, `TextToVisemeData`, `ChangeTalkingStyle`, `RemoveVisemesKey`. `RIFaceComponent`: `AddClip`, `AddExpressionKeys`, `ImportExpression` |
| Preference settings | Still absent | No preferences class or setter found |
| Attach / detach (parent-child) | Now possible | `RIObject.SetParent`, `LinkTo`, `UnLink`; `RIProp.SetLinkOffsetKey`; `RIAvatar.LoadAccessoryWithTransferSkinWeight` |
| Align motion / character root | Partly | `RIObject.AlignTo`; `RIAvatar.AutoAdjustFootHeight`; no motion-root-alignment call found |
| Modelling operations | Partly | See mesh row; plus `RIProp.MakeSubProp`, `RIAvatarShapingComponent.CreateSlider` / `SetShapingMorphWeight` |

**Undo and structure**
- `RGlobal.BeginAction(strAction, bBlockRecordUndo=False)` and `EndAction()` mark an undo/redo boundary;
  `RGlobal.Undo()` and `Redo()` exist; `REventCallback.OnUndoRedoDone` fires afterwards. — `RGlobal`, `REventCallback`.
- `RIMotionDirectorManager` has `BeginCommand` / `EmbedCommand` / `EndCommand`, `Start` / `Stop`. — `RIMotionDirectorManager`.
- `RIAvatar.DoCharacterization`, `LoadHikProfile`, `SaveHikProfile`, `SwitchSubdivMeshLevel`. — `RIAvatar`.
- UI hooks: `RUi.AddMenu`, `AddContextMenu`, `AddHotKey`, `CreateRDockWidget`, `CreateRDialog`, progress
  dialogs, viewport labels, plus `CallLuaFunction` / `LoadLuaUI`. The Lua calls confirm Wikipedia's legacy-Lua
  line, which round one could not verify. — `RUi`.

**Clips, tracks, layers**
- Body clips: `RISkeletonComponent.AddClip(kTime)` creates a clip; also `BreakClip`, `DeleteClip`,
  `MergeClips`, `MirrorClip`, `SampleMotionClip`, `FlattenMotionClip`. — `RISkeletonComponent`.
- Face and viseme clips: `RIFaceComponent.AddClip` / `BreakClip` / `DeleteClip`; `RIVisemeComponent.AddVisemesClip` / `RemoveVisemesClip`. — those pages.
- Clip properties: `RIClip` length, speed, loop count, transitions (type, strength, range), timecode data,
  clip↔scene time conversion. `GetControl("Layer", bone)` returns the clip's motion-layer control: "At the
  present, only 'Layer' is supported as the clip key". — `RIClip`.
- Keys on any control: `RControl.AddKey`, `RemoveKey`, `MoveKey`, `MoveAllKey`, `ClearKeys`,
  `SetKeyTransition`; `RFloatControl.OptimizeKeys`; morph keys through `RIMorphComponent.AddKey`; material
  keys through `RIMaterialComponent.Add*Key`; PopcornFX attribute keys through `RIPopcornFXObject.AddAttributeKey`. — those pages.
- **No `AddTrack` or `AddLayer` function exists on any of the 50 class pages checked.** Tracks appear from the
  data, and animation layers are reached only through a clip's "Layer" control.

**The 51 event callbacks on `REventCallback`** (2026-10-21):
- Application: OnAPInitialized, OnAPLayoutChanged, OnAPLayoutRestored, OnBeforeCloseAP, OnDialogModeChanged.
- Files: OnBeforeLoadFile / OnBeforeLoadFileWithPath, OnAfterFileLoaded / OnAfterFileLoadedWithPath,
  OnFileLoaded / OnFileLoadedWithPath, OnFileLoadFail, OnBeforeSaveFile, OnFileSaved.
- Scene: OnHierarchyChanged, OnObjectAdded, OnObjectAboutToBeDeleted, OnObjectDeleted,
  OnObjectSelectionChanged, OnObjectDataChanged, OnObjectDataChangedWithType, OnProjectDataChanged,
  OnPickedGeometryChanged, OnCurrentCameraChanged.
- Time and playback: OnCurrentTimeChanged, OnPlayed, OnStopped, OnSceneUpdated, OnTimerUpdated, OnUndoRedoDone.
- Content: OnContentBrowserSelected, OnCurrentLibraryChanged, OnSmartGalleryInitialized, OnInstallStarted /
  Progress / Finished / Error, OnUninstallStarted / Progress / Finished, OnImageAsyncLoadStart / AllDone.
- Account: OnMemberLoginStatusChanged, OnRefreshAccountPoints, OnRefreshDAPoints, OnUpdateDAPoints.
- Services: OnCommandReceived, OnLuaEvent, OnOmniLiveChanged, OnQuickMagicWebSocketNotified,
  OnServiceWebSocketNotified.

Registration goes through `RIEventListener.RegisterCallback` / `UnregisterCallback`. — `REventCallback`, `RIEventListener`.

- Users' documentation complaint, re-checked at the page: in 2024-11 the `RSaveFileSetting` page was empty;
  staff filled it within a week; animagic: "complete and updated documentation is lacking". —
  [forum 12628](https://discussions.reallusion.com/t/12628), 2024-11-25 to 2025-01-06, page read.

Assessment: by 2026 the API is a broad in-process scripting layer: file I/O, undo boundaries, clips, keys,
visemes, mesh vertices, render passes and mocap devices. Its structural gaps are telling for JustStage's
command API: tracks and layers can't be created as first-class objects, there are no project FPS or
preference setters, and there is no event for a single key change. JustStage's command set should make
tracks, layers and sequences addressable objects, each with its own undoable commands and change events.

---

## 7 · Hair simulation, native particles, PopcornFX inside iClone

**Hair**
- "Each iClone standard character contains one or more soft cloth objects. These objects can be the hair,
  cloth, or any sort of accessories." The hair is edited through Modify > Physics > Edit Weight Map, plus the
  Property, Collision and Wind sections. —
  [manual: Soft Cloth for Characters](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/57-Physics/Soft_Cloth_for_Characters.htm), undated, page read.
- Soft-cloth presets come in two groups, "Cloth and Hair. The Hair presets are suitable for characters with
  hair for generating soft hair animations." Soft Cloth simulation must be switched on in the toolbar, and
  "By Frame" time mode is advised. —
  [manual: The Soft Cloth Simulation](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/57-Physics/The_Basics_of_Soft_Body_Simulation.htm), page read.
- The Python `RIHair` exposes `GetPhysicsComponent` (the same `RIPhysicsComponent` as cloth),
  `GetHairType`, `ConvertToHair` and `ConvertToFaceHair`. — [RIHair](https://wiki.reallusion.com/IC8_Python_API:RLPy_RIHair), 2026-10-21, page read.
- 8.1 (2022-09-29): "Physics will need to be enabled for the hair to intercept soft-body intercollisions". —
  [version history](https://www.reallusion.com/iclone/iclone-version-history.html), page read.
- Bone-based hair or props can also use Spring effects (mass, strength, bounciness per chain), as round one
  noted from the manual's Spring Settings page.

Assessment: hair is mesh cards simulated by PhysX soft cloth with a weight map. There is no strand solver
and no dedicated hair solver. iClone 9's preview of "Dynamic Spring and Collision" (round one) suggests
springs are where Reallusion is improving.

**Native (legacy) particles** — manual pages in `8.0/30-Set/Particle/`, undated, page read:
- Structure: emitter, particles, and an optional parent node; an invisible cube ("Volume of Emitters") holds
  the emitters; a gizmo locates the set and can be linked, attached or sent along a path. —
  [Structure](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/30-Set/Particle/Structure_of_particle_system.htm).
- Emitter parameters:
  - Emit On / Off keys on the timeline;
  - Quota (maximum alive) and Emit Rate (per second);
  - Emit Volume (XYZ) and Position;
  - Direction as Longitude (−180–180) and Latitude (−90–90);
  - Spread (0–180) and Diagonal (0–180), described as a pyramid;
  - Velocity (0–99,999), Direction Randomness (0–359) and Random Seed;
  - Attach to any node.

  — [Adjusting Emitters](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/30-Set/Particle/Adjusting_emitters.htm).
- Particle parameters:
  - Diffuse texture with an Opacity map;
  - Blend Mode: Alpha, Addition or Subtraction;
  - four particle keys over a particle's life, each holding colour, opacity and size, with a Size Multiplier;
  - start and end colour, opacity and size (0–99,999);
  - Initial Angle and min/max Angular Velocity;
  - Softness Strength (blends where particles meet geometry);
  - Orientation: Face Cam, Vertical or Horizontal;
  - Life in frames (min/max, up to 99,999);
  - Force Gravity XYZ (accelerating) and Wind XYZ (constant).

  — [Adjusting Particles](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/30-Set/Particle/Adjusting_particles.htm).
- Python `RIParticle` has only `GetEmit` / `SetEmit`. — [RIParticle](https://wiki.reallusion.com/IC8_Python_API:RLPy_RIParticle), page read.

**PopcornFX inside iClone**
- Renderers are billboard, ribbon and mesh. Particles can light the scene (GI) and support HDR bloom. PhysX
  collisions are one-way (bounce or accumulate) and two-way (push physics objects).
- "Create brand new particle behaviors using the powerful script-based PopcornFX Editor … Directly load
  PopcornFX into iClone via the PopcornFX Plug-in."
- "All Attributes have their own timeline tracks. Users can set keys for each attribute. Effects are grouped
  for easy track management."
- Custom effects save with their attribute values and sampler data (mesh, texture, sound), can be attached to
  objects and saved with props and characters. "PopcornFX particles are not supported in Iray Render."

  — [technology page](https://www.reallusion.com/iclone/vfx/popcornfx/technology.html), undated (2017 era), page read.
- UI mapping: PopcornFX "Particle Attributes" become the iClone PopcornFX Attributes; the "Sample Attribute"
  becomes the iClone Emitter; the "Layer List" becomes the iClone Particle List.
- Attributes not exposed in the Editor can't be reached; turbulence is script-only; curve editing "no
  support"; "Path sampling is not yet a feature of iClone".
- `.pkfx` files don't package their sources, so iClone records their locations; missing `.pkmm` meshes are
  fixed in the Editor.
- PopcornFX is Y-up and iClone Z-up; a Z-up sample is provided but "not applicable to all scenarios".

  — [forum: PopcornFX into iClone – Tips & Notes](https://forum.reallusion.com/PrintTopic351131.aspx), Grace (RL), about 2017, page read.
- Mesh sampler: Modify > PopcornFX > Emitter > Sampler List; text samplers take typed text. —
  [forum 351143](https://forum.reallusion.com/PrintTopic351143.aspx), search snippet only.
- Python `RIPopcornFXObject`: `AddAttributeKey`, attribute count, name and value, `SetEmit`, emit keys,
  `SetLoop` / `SetLoopInterval`, `SetMeshSamplerTarget`, `GetSamplerList`. —
  [RIPopcornFXObject](https://wiki.reallusion.com/IC8_Python_API:RLPy_RIPopcornFXObject), 2026-10-21, page read.

Assessment: iClone keeps effect authoring outside, in the PopcornFX Editor, and only exposes and keys
attributes on its own timeline. For JustStage that is two layers: an effect graph, edited in its own editor
or imported, and "exposed parameters become timeline tracks". The second part is the standard to copy into
our data model.

---

## 8 · The AI Mesh Generator: local or cloud, and its price

- 8.76 adds Concept Design (single-view images for mesh generation), Mesh Generation (1 to 4 reference images
  → mesh with "Tripo H3.1 and Hunyuan V3.1 for high-poly detail, and Tripo P2.0 for clean low-poly
  topology") and AI Polygon Reduction (Tripo). The post states no host or price. —
  [8.76 post](https://discussions.reallusion.com/t/iclone-8-76-is-now-released-ai-mesh-generator-enhanced-cloth-workflow-improvements-and-bug-fixes/18780),
  2026-10-29, page read (no replies yet);
  [version history](https://www.reallusion.com/iclone/iclone-version-history.html), page read.
- The AI Cloud plans page lists "AI Mesh Design / per image" and "AI Mesh Gen / per mesh" under the AI Points
  services. "AI Points are the universal credits for all Reallusion cloud-based AI generation services …
  across AI Studio, Headshot Image Generation, Video Mocap". 1 USD = 100 AI Points. —
  [ai.reallusion.com/plans.html](https://ai.reallusion.com/plans.html), read 2026-10-29, page read.
- Point costs from that page:
  - Concept image (GPT Image 2.0): 18 points per image.
  - Hunyuan 3.1 Pro (1.5M / 500K / 10K faces): 45 mesh only; 90 with PBR texture; 57 with decimate (two
    meshes); 102 with decimate and texture.
  - Tripo H3.1: 24 mesh; 48 with texture; 36 with decimate; 60 with decimate and texture; 12 for a "Mesh +
    Decimate" row (listed twice with different prices).
  - Tripo P2.0 (25K / 5K / 1K faces, or manual 25K–50): 120 mesh; 160 with texture.
  - Two meshes can run at once on any plan.
- Plans: FREE $0 with 500 points one-off; STARTER $11 a month for 1,100; STANDARD $35 for 3,500; PRO $95 for
  9,500 (plus bonus points on paid plans). — same page.

Assessment: the AI Mesh Generator is a cloud service; nothing points to local running. Tripo H3.1, Tripo P2.0
and Hunyuan 3.1 Pro are offered as hosted models. A mesh costs $0.12–$1.60. JustStage's equivalent would sit
behind a model choice, local open checkpoints or the user's own API key, never a points wallet.

---

## 9 · Morph Creator, Persona, Smart Accessory, Talking Style Editor

All manual pages undated, page read; prefix `https://manual.reallusion.com/iClone-8/Content/ENU/`.

**Persona** (`8.0/10-Avatar/Persona.htm`)
- "The characteristics given to the actor so that the actor can animate in a unique style", stored in an AML
  (Action XML) file.
- A Persona holds several idles, keyboard movement behaviours and perform actions. Several behaviour sets
  (walk, run, custom fly) are switched with the Behavior Mode Switch (hotkeys X / Z).
- Applied from Content Manager > Animation > Persona; it replaces the Perform and Move entries.
- Right-click > Persona > Export Persona, edit the file, and re-apply it to the same or another actor.
  Templates are for G3 and G5 characters, and older actors need a Persona before they can move.

**Smart Accessory (8.5)** (`8.5/18-Accessory/Smart-Accessory/…`)
- It lets crowds spawn "each with different accessories" and links mocap motions to prop animations (for
  example skateboarding); MD performances for held objects. — `Smart-Accessory.htm`.
- Multiple parents: before 8.5 an accessory was bound to one fixed parent bone. Now Modify lists the possible
  parent bones, and the Parent Bone Settings panel adds bones (for example `CC_Base_L_Hand`) with
  per-bone Move / Rotate offsets saved with the item. Dropping the item with the right mouse button opens
  Attachment Options to choose the bone. — `Setting-Multiple-Parents-for-Accessories.htm`.
- Multiple materials: right-click > Edit Relation > Material tab adds MaterialPlus files, so MotionPlus and
  Crowd Generator can apply different materials. — `Setting-Multiple-Materials-for-Accessories.htm`.
- MotionPlus with auto-load accessories: select a collection range, Add MotionPlus to Library, and the
  MotionPlus Options panel picks which character and accessory animations to include. Each accessory keeps a
  "reference path" in a virtual directory, so applying the MotionPlus to another character loads the
  accessory too. Statuses flag a missing real path. — `Creating-MotionPlus-with-Smart-Accessories.htm`.

**Talking Style Editor** (`8.0/50-Animation/Facial-Animation/Using-Talking-Style-Editor.htm`)
- Opened by right-clicking a voice clip on the Viseme track (F3 opens the timeline). It needs voice scripts
  with visemes.
- A Preset Name list applies a style; per-phoneme strength sliders (for example "Ah", default 100, set to 150)
  scale that viseme across the whole clip. Python: `RIVisemeComponent.ChangeTalkingStyle`.

**Morph Creator / Morph Animator** (`8.0/50-Animation/Morph_Animation/…`, `8.1/…`)
- Opened from Modify for a prop, accessory or avatar. Workflow: export base meshes from Morph Creator as OBJ
  (all or selected, with a coordinate space chosen for the target tool); edit targets in another 3D tool;
  import (embedded morph targets are offered on load); create sliders; Send to iClone. —
  `Creating_Custom_Morph_Sliders_with_Morph_Creator.htm`, `Creating_Morph_Sliders.htm`.
- Limit: "Morph target shapes do not take into account bone transformations", so targets made from a
  re-boned avatar come out wrong (for example around the eyes). — `Creating_Morph_Sliders.htm`.
- Morph Editor: Send and Replace to iClone, Update Morph to iClone, Add / Replace / Bake / Delete sliders,
  Show Child, Reset. Deleting or updating morphs on already animated objects "will create animation errors".
  — `UI_Intro_for_Morph_Creator_Morph_Editor.htm`, `Editing_Morph_Sliders.htm`.
- Send replaces the selected iAvatar in iClone; link sliders keep, lose or split their links depending on full
  or partial updates. — `Sending_and_Updating_Morph_Data.htm`.
- The Morph Animator panel in iClone: Mesh List, Morph List, Show Child, Default Key (keys every slider at 0)
  and Bake Shape ("initialize the values of all morph sliders while the current shape … maintains", 8.1). —
  `8.1/50-Animation/Morph-Animation/UI_Intro_for_Morph_Animation.htm`.

Assessment: Persona and Smart Accessory are data-driven behaviour and attachment presets: a character carries
its behaviours, and an accessory carries its allowed parents, offsets and materials. JustStage's asset format
should hold both as data on the asset. Morph Creator's "targets ignore bone transforms" limit and its
"don't update morphs on animated objects" warning are exactly the kind of seam our one-document model should
not have.

---

## 10 · Licence lines (one each, no legal analysis)

- **iClone software (Reallusion Software EULA, 2026-05-25)** — commercial use **yes** with a perpetual or
  active subscription licence: sell images and videos; models and animations only "embedded within games,
  applications, interactive projects, or in 3D print format"; CC avatars' topology and rigs stay Reallusion's,
  and AI training on them is barred; Education licence non-commercial. —
  [EULA_AP.htm](https://www.reallusion.com/Content/EULA/AP/EULA_AP.htm), page read.
- **iClone Personal (free)** — commercial use **conditional**: the tool may be used on commercial projects,
  but renders are personal and social use only, and 3D export stops after 30 exports. The 2026-05-25 software
  EULA text has no Personal clause. —
  [download page](https://www.reallusion.com/iclone/download.html), page read (round one);
  [cgchannel](https://www.cgchannel.com/?p=176884), 2026-06-24, page read.
- **ActorCore assets** — governed by the Content EULA (updated 2025-08-01), which names ActorCore among
  "Reallusion's Stores". Commercial use **conditional**: imagery yes; games and interactive use under the
  Standard License; 3D art derived from content personal-only; export from iContent "requires the acquisition
  of a Standard License". —
  [Content EULA](https://www.reallusion.com/Content/EULA/EULA.htm), page read. Staff: commercial video "without
  any restrictions"; games need a free "Mass Distribution License" —
  [forum 493214](https://forum.reallusion.com/PrintTopic493214.aspx), about 2022, search snippet only. The
  ActorCore licence and FAQ pages are script-only (3 KB shells) and could not be read.
- **Video Mocap output (and all AI Service output)** — Reallusion AI Service EULA (2026-10-29), which names
  "AI video mocap". Commercial use **conditional** on the plan "at the time of generation": Free plan "testing
  and evaluation purposes only"; Starter, Standard and Pro "Commercial use granted". Content set "Public" may
  be used by Reallusion for promotion and "AI Improvement" (training). —
  [AI-Service.htm](https://www.reallusion.com/Content/EULA/AI-Service.htm), page read.

---

## Round-one snippet-only facts, re-checked at their pages

- 8.52 AccuPOSE (2024-12, cgchannel snippet) → confirmed: 8.52 2024-11-28, "AI-assisted natural posing
  technology, AccuPOSE". — version history, page read.
- 8.61 / 8.62 / 8.71 / 8.73 dates (snippets and titles) → confirmed with official dates; 8.61 is 2025-09-09,
  not round one's 09-10. — version history, page read.
- "Only same-generation software syncs" → confirmed: "No. Only the same generation software can be synced
  together … CC4 can transfer character to iClone 8"; iClone 8 reads iClone 7 projects. —
  [kb.reallusion.com 53039](https://kb.reallusion.com/Print53039.aspx), about 2022, page read.
- CC5 files not opening in iClone 8.6 without CC5 → confirmed on the FAQ: "Files containing CC5-specific
  elements cannot be opened in iClone 8.6 (or above) unless CC5 is installed … subdivision levels, eyelash
  components, corrective expressions, and HD facial profiles". —
  [CC5 FAQ](https://faq.reallusion.com/en/Product/Character-Creator/Character_Creator_5), page read.
  **Conflict:** the 8.74 notes (2026-07-29) say "HD Content no longer requires Character Creator 5 to be
  installed"; the FAQ may be older than 8.74.
- Python documentation complaints (snippet) → confirmed. — [forum 12628](https://discussions.reallusion.com/t/12628), page read.
- "Your First iClone Python Plugin" (snippet) → confirmed (§4).
- Wikipedia's legacy Lua scripting → corroborated by `RUi.CallLuaFunction` / `LoadLuaUI` and
  `REventCallback.OnLuaEvent` in the iC8 API (§6), and the manual's "Using Lights with Lua Script" page title (TOC).
- Round one's "max 54,000 frames" (manual page) → superseded: 216,000 since 8.3 (Top finding 2).
- Round one's AI Studio output line ("Starter no") → corrected: Starter is commercial (§10).

---

## Couldn't verify / open

- **Reddit:** blocked. The search tool refuses reddit.com, and round one found direct fetches refused. Not
  worked around.
- **Capterra, G2, GetApp review pages:** HTTP 403; only search snippets used. Renderosity was not retried
  (DNS failure in round one).
- **YouTube reviews:** titles only; no transcripts read.
- **Protocol names Reallusion's pages don't state:** whether Perception Neuron's link is Axis Neuron's BVH
  broadcast (TCP or UDP), the transport for Rokoko and OptiTrack (NatNet is Motive's usual protocol), and
  QTM's fixed port number. The device pages give only "IP:Port".
- **Prices not in the current store:** Faceware, Leap Motion, Manus and glove-only profiles are not sold in the
  2026-10-29 add-on list. Whether they were withdrawn or are sold elsewhere is not stated.
- **AI Mesh Generator:** the page lists no point cost for "AI Polygon Reduction (Tripo)", and the Tripo H3.1
  "Mesh + Decimate" row appears twice with different prices (36 and 12 points).
- **ActorCore licence and FAQ text:** script-only pages; the "Mass Distribution License" terms rest on a
  staff-post snippet.
- **Python:** no rigid-body, spring, SpeedTree, preferences or FPS setter found among the 50 class pages read.
  The 115 other IC8 class pages were not opened one by one, so a setter elsewhere is possible but unlikely (no
  page title suggests one).
- **Hair:** no page says whether CC5 HD hair or Hair Builder hair uses anything beyond PhysX soft cloth and
  spring bones.
- **iClone 9:** nothing beyond round one's March–April 2026 previews.
