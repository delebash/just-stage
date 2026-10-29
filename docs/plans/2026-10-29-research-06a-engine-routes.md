# Research 06a — building JustStage on an existing engine or 3D app

Research agent notes, 2026-10-29. Clean-room: public docs, release notes, licence texts and repo files
only. Every fact carries its source, the source's date, and how it was read: **page read** (fetched and
read), **search snippet only** (seen in a search-result summary, page not opened), **repo file read** or
**GitHub API** (fetched from github.com / api.github.com on 2026-10-29). Judgement is labelled
**Assessment:**.

Scope changes during the run (the coordinator, relaying the user, 2026-10-29):
- NVIDIA Omniverse Kit is **out**: it runs only on NVIDIA cards. No row or evidence here.
- Products that only come paid are out.
- Unity is **out**: "out — free tier far smaller than Unreal's" (the user, 2026-10-29). One row only, no
  evidence section.
- Unreal Engine and Flax stay full candidates, with their terms stated.
- Each candidate gets a label for the GPU vendors it runs on.

The session's web-search budget ran out part way through. After that, only direct page fetches and
GitHub's API were used. Gaps that caused are listed in the last section.

---

## Top findings

1. **Unreal 5.8 (2026-06-17) is "most likely" the last 5.x. The first UE6 previews are expected "late
   2027ish"**, so any Unreal route meets a major-version move early on.
   [gamefromscratch, 2026-06-17, page read](https://gamefromscratch.com/unreal-engine-5-8-released/)
2. **Verified (RESEARCH §6 "to verify"): MetaHuman Creator, Mesh to MetaHuman and MetaHuman Animator
   moved into the Unreal editor in 5.6.** That work is "enhanced by cloud services that deliver
   autorigging and texture synthesis", and Creator is an editor plugin.
   [cgchannel, 2025-06-04, page read](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/)
3. **Epic's EULA (search snippets): "The Product may not contain … any Engine Tools".** Engine Tools
   means the editor and the code in the Developer and Editor folders. They may be released publicly only
   to licensees, through the Marketplace (now Fab) or a fork of Epic's GitHub. A JustStage on Unreal is
   therefore either a packaged runtime app that rebuilds the authoring tools itself, or an editor plugin
   or mod kit for people who install Unreal.
   [Epic EULA, search snippet only](https://www.unrealengine.com/en-US/eula/unreal)
4. **Unreal pricing (Epic blog, March 2024 with a note dated 2026-05-27; search snippet only):**
   - Games pay 5% of gross revenue above $1M per product.
   - Non-game companies above $1M a year pay $1,850 per seat per year. That seat model excludes
     companies that create "applications that are licensed to third-party end users and rely on Unreal
     Engine code at runtime".
   - Use is free under $1M a year.
   [Epic blog](https://www.unrealengine.com/blog/we-are-updating-unreal-engine-twinmotion-and-realitycapture-pricing-in-late-april)
5. **MetaHuman Creator's recommended spec is above our machine.** Epic recommends an RTX 3070 or
   RX 6800 XT with 8 GB, 32 GB RAM and 16 cores. MetaHuman Animator is Windows-only (DirectX 12).
   [Epic MetaHuman docs, search snippet only](https://dev.epicgames.com/documentation/metahuman/hardware-requirements)
6. **Flax charges a 4% royalty on earnings above $250,000 per calendar quarter.** Its source is on
   GitHub under the Flax EULA, and the README invites people to "use the modified source in Flax-based
   games". Whether the editor may be redistributed, or a Flax app released as open source, was not found.
   [flaxengine.com/licensing, page read](https://flaxengine.com/licensing/) ·
   [FlaxEngine README, repo file read](https://github.com/FlaxEngine/FlaxEngine)
7. **Godot 4.7 (MIT) is the most "ours" base:**
   - The editor "is drawn using Godot's renderer and UI system" and is "fully written in C++".
   - LibGodot (since 4.6) embeds the engine in another app.
   - glTF can be saved at runtime.

   [Godot docs 4.7, page read](https://docs.godotengine.org/en/stable/engine_details/editor/introduction_to_editor_development.html) ·
   [Godot 4.6 release, page read](https://godotengine.org/releases/4.6/)
8. **In Godot, a realistic human is mostly ours to build:**
   - Subsurface scattering is "only available in the Forward+ renderer".
   - Hair is shaded as cards, using anisotropy and alpha hash.
   - There is no strand hair and no eye shader.

   Skinning and blend shapes already run in a GPU compute shader.
   [Godot StandardMaterial3D docs 4.7, page read](https://docs.godotengine.org/en/stable/tutorials/3d/standard_material_3d.html) ·
   [skeleton.glsl, repo file read](https://github.com/godotengine/godot/blob/master/servers/rendering/renderer_rd/shaders/skeleton.glsl)
9. **Blender already covers most of the CC5 + iClone feature list.** It has sculpting, rigging,
   animation editors, cloth and hair physics (node-based, new in 5.2 LTS), the EEVEE real-time renderer,
   the Cycles path tracer, and USD/glTF/Alembic export. It runs on every GPU vendor.
   [Blender 5.2 release page, 2026-07-14, page read](https://www.blender.org/download/releases/5-2/)
10. **Blender's licence: published add-on scripts must be "shared under a GPL compliant license"**, and
    Blender itself is "GPL Version 2 or later". The UI is Blender's own, so a deeply reworked UI means a
    fork, as Bforartists does (5.2.0, 2026-07-29).
    [blender.org/about/license, undated, page read](https://www.blender.org/about/license/) ·
    [Bforartists, GitHub API](https://github.com/Bforartists/Bforartists)
11. **Blender is the easiest base for AI agents to drive.** It has `-b/--background`, `--python`,
    `--python-expr`, `--render-frame` and `--app-template`. 5.2 adds `gpu.init()` for background mode
    and `Window.screenshot`. An official Blender Lab MCP server (v1.0.0, 2026-04-27, GPL-3.0+) exists.
    [creator_args.cc, repo file read](https://github.com/blender/blender/blob/main/source/creator/creator_args.cc) ·
    [strayspark blog, 2026, page read (third-party)](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026)
12. **O3DE 26.05 has the strongest out-of-the-box character stack among the permissive engines.** It is
    licensed Apache-2.0, or MIT at your option. It has AMD TressFX strand hair, NVIDIA Cloth, EMotionFX,
    motion matching, hardware ray tracing and a Python + Qt editor. Against that, the macOS editor is
    "Experimental", installs take 40 GB to 100+ GB, and there are few shipped titles.
    [O3DE LICENSE.txt, repo file read](https://github.com/o3de/o3de/blob/development/LICENSE.txt) ·
    [O3DE requirements, page read](https://docs.o3de.org/docs/welcome-guide/requirements/)
13. **Stride 4.4 (MIT, C#) has the best-built image-test setup** (GPU gold images, editor screenshot
    tests). But "WPF is the only supported view layer" for its editor, so the editor is Windows-only.
    [stride docs/editor/projects.md, repo file read](https://github.com/stride3d/stride/blob/master/docs/editor/projects.md)
14. **Bevy and Fyrox are early bases.** Bevy 0.20 (2026-10-08) has no editor yet and says it is "still in
    the early stages", with a breaking release about every 3 months. Fyrox 1.0 (2026-03-29) runs on
    OpenGL with no global illumination, from a team with "little to no funding".
    [bevy.org 0.20, page read](https://bevy.org/news/bevy-0-20/) ·
    [Bevy README, repo file read](https://github.com/bevyengine/bevy) ·
    [fyrox.rs 1.0, page read](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/)
15. **Official MCP control channels for AI agents now exist for Unreal (5.8, experimental plugin) and
    Blender (Blender Lab).** None was found for Godot, O3DE, Stride, Bevy or Fyrox (search budget ran out
    before Godot was checked). Bevy has its own JSON-RPC Remote Protocol.
    [gamefromscratch 5.8, page read](https://gamefromscratch.com/unreal-engine-5-8-released/) ·
    [docs.rs bevy_remote, search snippet only](https://docs.rs/bevy_remote)

---

## Score table

Scale (**Assessment:** the scores are my judgement from the evidence below):

- **3** — strong, or there out of the box.
- **2** — workable with moderate building.
- **1** — weak, or a large build or constraint.
- **0** — a blocker.

Source keys such as [U5] point to the evidence bullets.

### Criteria 1–5

| Candidate | 1 Realistic human, real time | 2 Own editor and layout | 3 Terms | 4 Language per layer · Python / native API | 5 Export to UE · Unity · Godot · Blender |
|---|---|---|---|---|---|
| **Unreal Engine 5.8** | **3** — MetaHuman (skin, strand groom, eyes, rig) inside the editor; cloud autorig and texture synthesis [U5][U7] | **1** — a packaged app with its own UI is possible (Cine Tracer). The authoring tools are Engine Tools, and a Product may not contain them. Editor builds go only to licensees, via Fab, the Epic store or a GitHub fork [U8][U10][U11] | **1** — free under $1M; 5% royalty above $1M per product; no Engine Tools or engine source to the public [U8][U9] | **2** — C++ core and Slate editor, Blueprint. Built-in Python is editor-only; a third-party runtime Python plugin exists. C++ plugins: yes [U13] | **2** — **Assessment:** export runs from the editor; a runtime exporter is ours to write (not verified this round) |
| **Unity 6** | out — free tier far smaller than Unreal's (the user, 2026-10-29) | — | — | — | — |
| **Flax 1.13** | **1** — a Subsurface shading model, blend shapes, 65,535 bones; no hair model found [F7] | **1** — C# editor, source on GitHub; editor redistribution not stated [F2][F3] | **1** — 4% over $250k a quarter; Flax EULA; open-source app not stated [F1][F2] | **1** — C++ core, C# editor and scripting; no Python found [F3] | **?** — not verified |
| **Godot 4.7** | **1** — SSS in Forward+ only; card hair (anisotropy, alpha hash); no strand hair or eye shader; GPU compute skinning and blend shapes [G5][G6] | **3** — the editor is a Godot app in C++; MIT fork allowed; LibGodot embedding; shipped tools: Pixelorama, Material Maker, Dungeondraft; fork Redot [G2][G4][G13][G14] | **3** — MIT; we choose JustStage's licence; no royalties; editor redistribution free [G1] | **2** — C++ core and editor; GDScript, C#; GDExtension C++ (godot-cpp, MIT) and Rust (gdext, MPL-2.0); Python only through community py4godot [G12] | **2** — glTF save at runtime is built in; FBX is load-only [G7] |
| **O3DE 26.05** | **2** — AtomTressFX strand hair (Marschner), EMotionFX with morph targets, hardware RT; skin SSS not found [O5][O6][O7] | **2** — Qt editor, Python 3 and QtForPython extensions; permissive fork; no shipped non-game tool found [O5][O6] | **3** — Apache-2.0, or MIT at our option [O2] | **2** — C++ core, Qt/C++ editor, Lua and Script Canvas, Python 3 for the editor; C++ Gems [O5][O6] | **1** — FBX import; export not verified |
| **Stride 4.4** | **1** — SSS with a "Skin" profile; no hair found [S5] | **1** — custom asset editors possible, but the editor is WPF, so Windows-only [S4] | **3** — MIT; contributors sign the .NET Foundation CLA [S1] | **2** — all C#/.NET; Python and native-plugin story not verified | **?** — not verified |
| **Bevy 0.20** | **0** — no SSS or hair; morph targets; the Solari path tracer is experimental [B4][B5] | **2** — no host editor at all, so the whole UI is ours to build [B3] | **3** — MIT or Apache-2.0 [B1] | **2** — Rust throughout; Rust plugins; Python not verified | **1** — glTF is its scene format; export not found [B3] |
| **Fyrox 1.0** | **0** — OpenGL PBR, no GI [Y3] | **2** — native Rust editor (FyroxEd); MIT fork [Y2] | **3** — MIT [Y1] | **1** — Rust only | **?** — not verified |
| **Blender 5.2 (add-on / app template)** | **2** — EEVEE SSS, strand hair curves, shape keys, Cycles; deformation is CPU-bound for heavy rigs [L8][L9] | **1** — panels, workspaces and app templates, inside Blender's UI framework [L6] | **1** — GPL: published add-on scripts must use a GPL-compliant licence; no fees [L1] | **2** — C/C++ core and UI; Python (bpy) is the API; no C++ plugin SDK (**Assessment**, not sourced) | **3** — USD, glTF, Alembic and FBX export built in [L3] |
| **Blender fork (Bforartists, UPBGE, others)** | **2** — as Blender; UPBGE reports GPU skinning in master [L8] | **2** — any UI change; Bforartists reworks the UI [L10] | **1** — GPL for the whole app [L1] | **2** — as Blender, plus our own C/C++ in-tree | **3** — as Blender |
| **Wicked Engine (other)** | **?** — features beyond the README not verified | **2** — has a "standalone 3D editor"; MIT [W1] | **3** — MIT [W1] | **1** — C++ and Lua scripting; no Python [W1] | **?** |
| **Panda3D (other)** | **0** — no character rendering features found | **1** — no editor [P1] | **3** — Modified BSD [P1] | **3** — Python and C++ first-class [P1] | **?** |

### Criteria 6–10 and GPU vendors

| Candidate | 6 Editor OS · graphics APIs | GPU vendors (editor / runtime) | 7 RTX 2070 Super 8 GB | 8 CC5 + iClone features free | 9 AI agents build and test | 10 Health |
|---|---|---|---|---|---|---|
| **Unreal Engine 5.8** | **2** — editor on Windows 10+, macOS 14+, RHEL/Rocky 8+; MetaHuman Animator is Windows/DX12 only [U5][U7] | NVIDIA, AMD, Intel, Apple (MetaHuman Animator: Windows only) | **2** — editor recommends 8 GB VRAM and 32 GB RAM; MetaHuman Creator recommends an RTX 3070 [U7][U17] | **3** — Sequencer, Control Rig (physics in Sequencer), Chaos Cloth, Hair and Flesh, MegaLights, Movie Render Graph, Live Link Hub, MetaHuman (editor only) [U2][U3] | **2** — automation and screenshot tests, Remote Control HTTP/WebSocket, MCP plugin (experimental); ~190 GiB source install, builds take hours [U14][U15][U16] | **3** — Epic, two releases a year; UE6 previews late 2027 [U1][U4] |
| **Unity 6** | out (the user, 2026-10-29) | — | — | — | — | — |
| **Flax 1.13** | **2** — editor builds on Windows, Linux and Mac; Vulkan; D3D on Windows [F3] | NVIDIA, AMD, Intel; Apple through the Vulkan SDK [F3] | **?** — no data | **1** — DDGI, jiggle physics [F5] | **1** — nothing found on headless runs or tests | **1** — 7.1k stars; 1.13 on 2026-10-21 [F4] |
| **Godot 4.7** | **3** — Windows, macOS and Linux; Vulkan, D3D12 (default for new Windows projects), Metal (4.4+), OpenGL [G2][G10][G11] | NVIDIA, AMD, Intel, Apple [G10] | **2** — Forward+ recommends a GTX 1050 or RX 460, so the 2070 Super is far above; heavy human content not measured [G10] | **1** — AnimationTree, IK (4.6), Jolt, soft bodies, GPU particles, area lights; no strand hair, path tracer, sculpting or sequencer [G2][G3] | **3** — `--headless`, `--script`, `--write-movie`, `--test`; but RenderingDevice is not available headless, so image tests need a GPU [G8][G9] | **3** — 119k stars, two feature releases a year; breaking changes come with migration guides [G1][G2] |
| **O3DE 26.05** | **1** — Windows and Ubuntu 22.04; macOS "Experimental"; DX12 or Vulkan [O3][O4] | NVIDIA, AMD, Intel; Apple experimental [O3] | **2** — minimum 2 GB VRAM; build needs 16–32 GB RAM and ~2 GB per thread [O3] | **2** — EMotionFX, motion matching, PhysX 5, NvCloth, TressFX, ray tracing, experimental particles [O4][O5][O6] | **1** — Python editor bindings, ScriptAutomation and RemoteTools Gems; 40–100+ GB; 1 TB SSD recommended [O3][O6] | **1** — 9.8k stars, two releases a year, few shipped titles [O1][O8] |
| **Stride 4.4** | **1** — editor Windows-only (WPF); runtime Windows and Linux (Vulkan/OpenGL); D3D11/12 [S4][S7] | Editor: NVIDIA, AMD, Intel (Windows); Apple not verified | **?** — no data | **1** — Bepu physics (4.3); rest not verified [S3] | **2** — gold-image GPU tests, editor screenshot tests, WARP software renderer, CLI [S6] | **1** — 7.9k stars; 4.4.1 on 2026-10-17 [S2] |
| **Bevy 0.20** | **3** — no editor; runtime on Vulkan, Metal and D3D12 through wgpu (Metal named in the 0.19/0.20 posts) [B4][B5] | NVIDIA, AMD, Intel, Apple | **?** — no data | **0** — very little: no timeline, cloth or hair | **2** — the BRP JSON-RPC control channel; Rust tests; Rust compile times; a breaking API every ~3 months [B2][B6] | **2** — 49k stars, very active, pre-1.0 [B1][B2] |
| **Fyrox 1.0** | **2** — Windows, Linux and macOS through OpenGL only [Y2][Y3] | NVIDIA, AMD, Intel, Apple (OpenGL) | **?** — no data | **1** — animation state machine and editor; no GI [Y2][Y3] | **1** — export CLI; no test tooling found [Y2] | **1** — 9.6k stars; little or no funding [Y1][Y2] |
| **Blender 5.2 (add-on / app template)** | **3** — Windows, macOS and Linux; OpenGL, Vulkan, Metal; Cycles on CUDA, OptiX, HIP, oneAPI, Metal [L5] | NVIDIA, AMD, Intel, Apple [L5] | **2** — **Assessment:** EEVEE fits 8 GB; dense skinned characters hit the CPU [L8] | **3** — sculpting, modelling, rigging, animation editors, XPBD cloth and hair, Cycles, EEVEE, Geometry Nodes, video editor [L3] | **3** — `-b --python`, `gpu.init()` in background, `Window.screenshot`, a test suite, an official MCP server [L3][L6][L7] | **3** — 3–4 releases a year, LTS for two years; bpy breaks a little each release [L2][L3] |
| **Blender fork** | **3** — as Blender (Bforartists Mac builds "coming soon") [L10] | NVIDIA, AMD, Intel, Apple | **2** | **3** | **3** — **Assessment:** as Blender, plus rebasing every Blender release | **2** — Bforartists has 812 stars and tracks Blender [L10] |
| **Wicked Engine (other)** | **3** — Windows, Linux, macOS; DX12, Vulkan, Metal [W1] | NVIDIA, AMD, Intel, Apple | **?** | **?** | **?** | **2** — 7.3k stars; v0.72.120 on 2026-10-02 [W1] |
| **Panda3D (other)** | **?** — OpenGL (not verified) | **?** | **?** | **0** | **2** — **Assessment:** Python-first, so scriptable | **1** — latest stable 1.10.16 on 2025-12-25; 1.11 only in preview [P1] |

### Route and language pairs (Assessment)

| Route | Engine core | Editor UI | Scripting / user API | Native plugin API | Fit |
|---|---|---|---|---|---|
| **Unreal: editor plugin or mod kit for Unreal users** | C++ (Epic's) | Slate, inside the Unreal editor | Python (editor) + Blueprint | C++ | Best human and feature set. Users must install Unreal (~60–190 GB), and the app lives inside Unreal's editor. |
| **Unreal: packaged runtime app** | C++ | UMG/Slate of our own | ours (runtime Python only through a third-party plugin) | C++ | Our own UI, but every authoring tool (Sequencer editing, rig editing, MetaHuman Creator) is rebuilt by us. |
| **Godot: custom editor build or LibGodot** | C++ (MIT) | Godot UI nodes (C++ / GDScript) | GDScript, C#, community Python | C++ (GDExtension), Rust (gdext) | Best "our own app, any licence". The realistic-human rendering and every CC/iClone tool are ours to build. |
| **Blender add-on + app template** | C/C++ (GPL) | Blender's UI, through Python panels | Python (bpy) | none (fork needed) | Most features already there; GPL; Blender's look and feel. |
| **Blender fork** | C/C++ (GPL) | Blender's UI toolkit, changed freely | Python | in-tree C/C++ | Full control; GPL; rebase on every Blender release. |
| **O3DE** | C++ (Apache/MIT) | Qt (C++ / PySide) | Python, Lua | C++ Gems | Good character pieces and licence; weak macOS support, large, a small ecosystem. |

---

## Evidence by candidate

### Unreal Engine (latest 5.8)

- **[U1]** 5.8 was released 2026-06-17 at State of Unreal. It is "most likely going to be the final
  release of Unreal Engine 5.x", and the first UE6 previews are expected "late 2027ish".
  [gamefromscratch.com, 2026-06-17, page read](https://gamefromscratch.com/unreal-engine-5-8-released/)
- **[U2]** 5.8 features:
  - MegaLights "now fully production-ready", and Lumen Lite.
  - An experimental "Unreal MCP Server Plugin" connecting LLMs to projects.
  - MetaHuman Crowds, full-body Mesh to MetaHuman, and single-camera MetaHuman Animator.
  - Control Rig Physics (Beta) "directly inside the sequencer".
  - Chaos Hair, Flesh and Cloth updates, and Substrate NPR shading.

  [same page, page read](https://gamefromscratch.com/unreal-engine-5-8-released/)
- **[U3]** In 5.8, MegaLights, Audio Insights, Live Link Hub, Iris and Movie Render Graph left
  experimental status.
  [wnhub / 80.lv / guru3d coverage, 2026-06, search snippet only](https://80.lv/articles/unreal-engine-5-8-is-out-today-with-big-optimization-improvements-and-mesh-terrain)
- **[U4]** 5.7 (November 2025) brought production-ready PCG, an in-editor AI assistant and deeper
  MetaHuman integration.
  [unrealengine.com news, 2025-11, search snippet only](https://www.unrealengine.com/news/unreal-engine-5-7-is-now-available)
- **[U5]** MetaHuman Creator, Mesh to MetaHuman and MetaHuman Animator "are now integrated into Unreal
  Engine 5.6":
  - The workflow is "enhanced by cloud services that deliver autorigging and texture synthesis".
  - Bodies are now parametric (height, chest, waist, leg length).
  - "The Unreal Editor is compatible with Windows 10+, macOS 14.0+ and RHEL/Rocky Linux 8+."

  [cgchannel.com, 2025-06-04, page read](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/)
- **[U6]** MetaHuman licence: free "with under $1 million/year in revenue"; above that, Unreal seat
  licences are needed. MetaHumans may be used in Unity, Godot and other engines without the 5% cut, and
  may be sold. [same cgchannel page, page read]. The metahuman.com/license page redirects to an Epic
  login and was not read.
- **[U7]** As of 5.7:
  - The MetaHuman Creator plugin works "in Editor on Windows, Mac, and Linux".
  - Creating Identity and Performance assets is disabled on Mac and Linux, because some MetaHuman
    Animator features are limited to DirectX 12; MetaHuman Animator is "Only Supported on Windows".
  - Recommended spec: 16 cores, 32 GB RAM, and an RTX 3070, RX 6800 XT or M2 Ultra with 8 GB VRAM.

  [dev.epicgames.com MetaHuman hardware requirements, UE 5.7 docs, search snippet only (the fetched page had no body text)](https://dev.epicgames.com/documentation/metahuman/hardware-requirements)
- **[U8]** Terms: the EULA and FAQ (all search snippets; Epic's EULA page and FAQ answered 403 to
  scripted fetches, so they were not read):
  - "Engine Tools" means "(a) editors and other tools included in the Engine Code; (b) any code and
    modules in either the Developer or Editor folders".
  - "The Product may not contain any Paid Content Distributed in uncooked source format or any Engine
    Tools."
  - Engine Code may go only "to an Engine Licensee who has rights … to the same Version".
  - "Any public Distribution … which includes Engine Tools … must take place either through the
    Marketplace (e.g., for distributing a Product's modding tool or editor to end users) or through a
    fork of Epic's GitHub UnrealEngine Network".
  - Epic FAQ: "The only parts of the Unreal Engine you can't release to the general public are the
    source code and tools or modifications to them."

  [unrealengine.com/en-US/eula/unreal](https://www.unrealengine.com/en-US/eula/unreal) and
  [Epic FAQ](https://www.unrealengine.com/en-US/faq)
- **[U9]** Pricing, from Epic's blog of March 2024 (with an update note dated 2026-05-27; search snippet
  only, the page answered 403):
  - Games pay "a 5% royalty on products that exceed $1 million in lifetime gross revenue"; Epic Games
    Store revenue is exempt.
  - Non-game use is $1,850 per seat per year. It applies only to a company with over $1M annual gross
    revenue that "does not create games, and does not create applications that are licensed to
    third-party end users and rely on Unreal Engine code at runtime".
  - Unreal is free for "students, educators, hobbyists, and companies generating less than $1 million in
    annual gross revenue".
  - Plug-in makers "can continue to use the software for free".

  [Epic blog](https://www.unrealengine.com/blog/we-are-updating-unreal-engine-twinmotion-and-realitycapture-pricing-in-late-april)
- **[U10]** Editor builds already reach the public as game mod kits:
  - ARK Dev Kit, a modified Unreal 4 editor obtained through the Epic launcher, about 500 GB.
  - GROUND BRANCH Mod Kit, an "extended version of the Unreal Engine 4 editor" on the Epic Games Store,
    40–60 GB.

  [ark.wiki.gg, search snippet only](https://ark.wiki.gg/wiki/Modding) ·
  [store.epicgames.com, search snippet only](https://store.epicgames.com/p/ground-branch-mod-kit)
- **[U11]** Cine Tracer is an Unreal-based cinematography simulator by Matt Workman, sold on Steam since
  2019. Cine Tracer 2 was "built from scratch in Unreal Engine 5"; its Steam page notes no updates for
  over two years.
  [cgchannel, 2019-07-18, search snippet only](https://www.cgchannel.com/2019/07/check-out-ue4-based-cinematography-simulator-cine-tracer) ·
  [Epic spotlight, 2019-07-17, search snippet only](https://www.unrealengine.com/spotlights/cine-tracer-delivers-easy-to-use-realistic-cinematography-simulation)
- **[U12]** Twinmotion is Epic's own product "built on Unreal Engine technology", with a simplified
  interface. [bimekspert.ee comparison PDF, 2023, search snippet only](https://bimekspert.ee/twinmotion/tm-vs-ue-2023-v2.pdf)
- **[U13]** "Unreal only supports python in the editor and not in runtime" (a forum reply). A
  third-party open-source plugin, UnrealPython, embeds CPython at runtime for UE 5.7 and 5.8.
  [forum.convai.com, search snippet only](https://forum.convai.com/t/python-commands-in-packaged-game/1862) ·
  [forums.unrealengine.com, 2026, search snippet only](https://forums.unrealengine.com/t/open-source-unrealpython-runtime-python-integration-for-unreal-engine-5/2731632)
- **[U14]** Remote Control runs a web server inside the engine (HTTP and WebSocket; WebSocket port
  30020). It is disabled in packaged builds and `-game` unless started with
  `-RCWebControlEnable -RCWebInterfaceEnable`.
  [dev.epicgames.com, search snippet only](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-for-unreal-engine)
- **[U15]** The Screenshot Comparison tool and the Screenshot Functional Test actor exist; the actor's
  "Disable Noisy Rendering Features" turns off anti-aliasing, motion blur and similar effects.
  [dev.epicgames.com, search snippet only](https://dev.epicgames.com/documentation/en-us/unreal-engine/screenshot-comparison-tool-in-unreal-engine)
- **[U16]** Install and build cost:
  - A source build of UE 5.4 installs to about 190 GiB and needs 340+ GiB to build; the precompiled
    package is about 63 GB (Arch wiki).
  - A UE 5.6.1 build takes "a couple of hours to overnight" (UMBC course notes).

  [wiki.archlinux.org, search snippet only](https://wiki.archlinux.org/title/Unreal_Engine_5) ·
  [userpages.cs.umbc.edu, search snippet only](https://userpages.cs.umbc.edu/olano/class/438-25-8/assn6a)
- **[U17]** Epic's hardware page recommends 8 GB or more of graphics RAM and 32 GB of system RAM.
  [dev.epicgames.com, search snippet only](https://dev.epicgames.com/documentation/unreal-engine/hardware-and-software-specifications-for-unreal-engine)
- **[U18]** The user already has Unreal C++ projects on this machine (RESEARCH §1, measured 2026-10-29).
- **Real products:** Twinmotion (Epic); Cine Tracer and Cine Tracer 2; ARK Dev Kit and GROUND BRANCH Mod
  Kit (an editor shipped to the public through Epic's store); MetaHuman Creator itself (an editor
  plugin).
- **Assessment:**
  - Of all the bases, Unreal gives the most of CC5 and iClone, but mostly as editor tooling.
  - The EULA lines in [U8] decide how JustStage could ship on Unreal:
    - as a plugin or mod-kit-style editor for people who install Unreal; or
    - as a runtime app whose authoring tools we write ourselves.
  - Our own code can carry any licence we pick. The engine and editor cannot be redistributed under it.

### Unity 6

Out — free tier far smaller than Unreal's (the user, 2026-10-29). No evidence section, by instruction.

### Flax Engine (latest 1.13)

- **[F1]** Terms on flaxengine.com/licensing (undated, page read):
  - "pay a 4% royalty on earnings exceeding $250,000 (per calendar quarter)".
  - "Use full source code", and "all Editor source code" is usable for free.
  - A custom licence that "reduces or eliminates royalty in favor of flat-fee, per-seat licensing" is
    available on request.

  [flaxengine.com/licensing](https://flaxengine.com/licensing/) ·
  [custom licensing, search snippet only](https://flaxengine.com/custom-licensing)
- **[F2]** LICENSE.md says: "Use of the Flax, provided source code and binary files is governed by the
  terms of the Flax Engine End User License Agreement". GitHub reports the licence as NOASSERTION.
  [LICENSE.md, repo file read 2026-10-29](https://github.com/FlaxEngine/FlaxEngine/blob/master/LICENSE.md)
- **[F3]** README:
  - "written in C++ and C#".
  - The repo "contains full source code of the Flax Engine (excluding NDA-protected platforms
    support)".
  - "Anyone is welcome to contribute or use the modified source in Flax-based games."
  - Build steps cover the Editor on Windows (Win64), Linux and Mac; the Vulkan SDK is required on Linux
    and Mac.

  [README, repo file read 2026-10-29](https://github.com/FlaxEngine/FlaxEngine)
- **[F4]** Latest release 1.13.7012, published 2026-10-21; 7,094 stars.
  [GitHub API, 2026-10-29](https://github.com/FlaxEngine/FlaxEngine)
- **[F5]** 1.12 added DDGI, jiggle physics and experimental web support through WebGPU.
  [gamefromscratch, search snippet only](https://gamefromscratch.com/flax-engine-1-12-released/)
- **[F6]** The 1.7 notes say the EULA was loosened; "the ability to revoke or terminate the license was
  removed". [docs.flaxengine.com 1.7 notes, search snippet only](https://docs.flaxengine.com/manual/release-notes/1_7/index.html)
- **[F7]** Character rendering:
  - A Subsurface shading model "intended to be used by materials like skin, jade, wax or foliage".
  - Blend shapes have been imported since 0.7; 1.10 supports 65,535 bones in skinned meshes.
  - No built-in hair shading model was found; an undated forum thread asks for one.

  [Flax docs shading models](https://docs.flaxengine.com/manual/graphics/materials/shading-models/index.html) ·
  [forum](https://forum.flaxengine.com/t/realistic-human-shaders/1496) · all search snippets only.
- **Real products:** none found (search budget ran out).
- **Terms not found:** whether the Flax Editor may be redistributed; whether a Flax-based app may be
  published as open source (the README wording is "Flax-based games"). The full EULA text was not read.

### Godot (latest 4.7.2)

- **[G1]** MIT; 119,262 stars; latest tag 4.7.2-stable, published 2026-08-18.
  [GitHub API, 2026-10-29](https://github.com/godotengine/godot). 4.7 stable came out on 2026-06-19
  [cinevva / wnhub, search snippet only](https://app.cinevva.com/hi/news/2026-06-19-godot-4-7-released).
- **[G2]** Godot 4.6 (announced 2026-01-26):
  - "We're introducing the core IKModifier3D class built on the revamped SkeletonModifier3D", with
    TwoBoneIK3D, SplineIK3D, FABRIK3D, CCDIK3D and JacobianIK3D.
  - Docks can move between sides and most can float.
  - LibGodot lets you "embed the engine in your own applications and control its startup and loop" on
    Linux, Windows and macOS.
  - Jolt is the default 3D physics; Direct3D 12 is the default for new Windows projects.

  [godotengine.org/releases/4.6, page read](https://godotengine.org/releases/4.6/)
- **[G3]** 4.7 added HDR output (Windows, macOS, iOS, visionOS, Wayland), AreaLight3D, and the Godot
  Asset Store in beta. [wnhub / cinevva, 2026-06, search snippet only](https://wnhub.io/news/engines/item-51174)
  (the godotengine.org 4.7 page returned HTTP 520).
- **[G4]** "The Godot editor is drawn using Godot's renderer and UI system." "The editor is fully written
  in C++." Editor plugins are made in GDScript.
  [docs 4.7, page read](https://docs.godotengine.org/en/stable/engine_details/editor/introduction_to_editor_development.html)
- **[G5]** Material features for characters:
  - Subsurface scattering: "only available in the Forward+ renderer, not the Mobile or Compatibility
    renderers".
  - "Anisotropy is commonly used with hair"; "Alpha Hash is suited for realistic-looking hair"; Lambert
    Wrap gives "cheap subsurface scattering".
  - No content on eye shading.

  [docs 4.7 StandardMaterial3D, page read](https://docs.godotengine.org/en/stable/tutorials/3d/standard_material_3d.html)
- **[G6]** `servers/rendering/renderer_rd/shaders/skeleton.glsl` is a `#[compute]` shader that reads
  `blend_shape_weights` and `bone_transforms`: skinning and blend shapes run on the GPU in the
  Forward+ and Mobile renderers.
  [repo file read 2026-10-29](https://github.com/godotengine/godot/blob/master/servers/rendering/renderer_rd/shaders/skeleton.glsl)
- **[G7]** "Godot has first-class support for glTF 2.0, both in the editor and exported projects":
  `GLTFDocument.write_to_filesystem()` saves .gltf or .glb. "Since Godot 4.3, FBX scenes can also be
  loaded (but not saved) at runtime."
  [docs 4.7, page read](https://docs.godotengine.org/en/stable/tutorials/io/runtime_file_loading_and_saving.html)
- **[G8]** Command line:
  - `--headless` ("--display-driver headless --audio-driver Dummy").
  - `--script`, `--write-movie <file>`, and `--export-release`.
  - `--test` "requires compiling the engine with tests=yes".
  - `--quit-after`.

  [docs 4.7 command line, page read](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)
- **[G9]** RenderingDevice "is not available when running in headless mode or when using the
  Compatibility rendering method".
  [docs 4.3 RenderingDevice, search snippet only](https://docs.godotengine.org/en/4.2/classes/class_renderingdevice.html)
- **[G10]** System requirements:
  - Editor: Windows 10, macOS 10.15 (Forward+/Mobile), Linux released after 2018.
  - Forward+: minimum Vulkan 1.0 integrated graphics; recommended Vulkan 1.2 dedicated graphics (GTX
    1050, RX 460).
  - Exported projects also run on Metal 3 (macOS) and Direct3D 12 at feature level 12_0.
  - Example GPUs come from Intel, AMD and NVIDIA.

  [docs 4.7, page read](https://docs.godotengine.org/en/stable/about/system_requirements.html)
- **[G11]** 4.4 added a native Metal back end (Apple Silicon; Intel Macs use MoltenVK). 4.3 added
  Direct3D 12, which needs the separate dxil.dll.
  [godotengine.org 4.4 dev 1 / 4.3 dev 1, search snippet only](https://godotengine.org/article/dev-snapshot-godot-4-4-dev-1/)
- **[G12]** Language bindings:
  - godot-cpp, "C++ bindings for the Godot script API": MIT, 2,750 stars, pushed 2026-10-26.
  - godot-rust/gdext, "Rust bindings for Godot 4": MPL-2.0, 5,337 stars, pushed 2026-10-25.

  [GitHub API, 2026-10-29](https://github.com/godot-rust/gdext). For Python, py4godot (MIT; Windows,
  Linux, macOS arm64; "under active development") and godot-python-extension ("not production ready")
  exist. [store.godotengine.org, search snippet only](https://store.godotengine.org/asset/niklas-zimmer/py4godot/)
- **[G13]** Non-game apps on Godot: the Godot editor, Material Maker, Pixelorama (MIT) and Dungeondraft.
  [gamefromscratch, search snippet only](https://gamefromscratch.com/godot-developed-non-game-applications/)
- **[G14]** Redot, a Godot fork: MIT, 6,169 stars, redot-26.3-stable on 2026-10-15.
  [GitHub API, 2026-10-29](https://github.com/Redot-Engine/redot-engine)
- **Real products:** Pixelorama, Material Maker, Dungeondraft (apps); the Godot editor itself; the Redot
  fork.
- **Assessment:**
  - Godot is the cleanest base for "one app of our own, on our own licence".
  - CC5-level realism needs work in the engine itself: skin profiles, strand hair, eye shading and
    wrinkle maps, all through the C++ module or GDExtension rendering hooks.
  - So do the CC5 and iClone tools: sequencer, sculpting, cloth.

### O3DE (latest 26.05)

- **[O1]** Release 2605.0 was published 2026-05-27; 9,802 stars.
  [GitHub API, 2026-10-29](https://github.com/o3de/o3de)
- **[O2]** "The default license for Open 3D Engine is the Apache License, Version 2.0 … you may elect at
  your option to use the Open 3D Engine under the MIT License."
  [LICENSE.txt, repo file read 2026-10-29](https://github.com/o3de/o3de/blob/development/LICENSE.txt)
- **[O3]** System requirements:
  - Windows 10 20H2+. Linux: "The primary Linux distribution for using the O3DE Editor is Ubuntu 22.04
    LTS". macOS: "Experimental" (Big Sur, Intel x86_64).
  - GPU: DX12 or Vulkan, 2 GB VRAM, Shader Model 6.2 (6.3 for ray tracing).
  - Disk: 40 GB with the installer, 100+ GB depending on the project; an SSD with 1 TB free is
    recommended.
  - RAM: 16 GB minimum, 32 GB recommended; about 2 GB per build thread.

  [docs.o3de.org requirements, page read](https://docs.o3de.org/docs/welcome-guide/requirements/)
- **[O4]** 26.05 notes:
  - An experimental Open Particle System.
  - A GUI for creating C++ components; CMake bundled.
  - PhysX 5 is the default, and PhysX 4 is deprecated.
  - The Windows settings tab offers DirectX 12 or Vulkan; macOS appears only in build fixes.

  [docs.o3de.org 26.05 release notes, page read](https://docs.o3de.org/docs/release-notes/2605-0-release-notes/)
- **[O5]** Features page:
  - AMD TressFX: "Create hair and fur using guide hairs and grooming data".
  - NVIDIA Cloth: "Create clothing and fabrics that realistically react to animated entities".
  - "Real time, hardware accelerated ray tracing".
  - Lua and Script Canvas scripting.
  - "The O3DE Editor and tools offer extension support through Python 3"; "the Qt UX library used by
    the O3DE editor".

  [docs.o3de.org features, page read](https://docs.o3de.org/docs/welcome-guide/features-intro/)
- **[O6]** Gems in the repo: AtomTressFX, EMotionFX, MotionMatching, NvCloth, PhysX, OpenParticleSystem,
  EditorPythonBindings, QtForPython, PythonAssetBuilder, RemoteTools, ScriptAutomation, ScriptCanvas.
  [GitHub API Gems listing, development branch, 2026-10-29](https://github.com/o3de/o3de/tree/development/Gems)
- **[O7]** AtomTressFX "enhances the open source TressFX 4.1 by AMD and includes a more advanced handling
  of lighting using the Marschner lighting model". The Atom skinned-mesh options include
  `m_applyMorphTargets`.
  [docs.o3de.org AtomTressFX, search snippet only](https://docs.o3de.org/docs/user-guide/gems/reference/rendering/amd/atom-tressfx/)
- **[O8]** "Made with O3DE" lists State of Matter (PC, July 2024), plus MadWorld, Awaken Guardian and
  Reverb, all with no release date.
  [docs.o3de.org, search snippet only](https://docs.o3de.org/docs/learning-guide/made-with-o3de/)
- **[O9]** The Open 3D Foundation (Linux Foundation) began in 2021 from Amazon Lumberyard. Its undated
  members page names AWS, Robotec.AI, Epic Games, Microsoft and OPPO.
  [opensourceforu 2021 / o3d.foundation, search snippet only](https://www.opensourceforu.com/2021/07/linux-foundation-to-form-new-open-3d-foundation/)
- **Real products:** State of Matter (game). No non-game tool built on O3DE was found.
- **Assessment:**
  - O3DE has the most character pieces among the permissive engines: strand hair, cloth, motion
    matching, and a Qt/Python editor.
  - Against it: weak macOS support, a heavy install and build, a small ecosystem, and no proof of a
    shipped creation tool.

### Stride (latest 4.4.1)

- **[S1]** README:
  - "Stride is an open-source C# game engine designed for realistic rendering and VR", with the Game
    Studio editor and a CLI that runs "no editor required".
  - "Stride is covered by the MIT License"; contributors sign the .NET Foundation CLA.

  [README, repo file read 2026-10-29](https://github.com/stride3d/stride)
- **[S2]** releases/4.4.1 was published 2026-10-17; 7,931 stars.
  [GitHub API, 2026-10-29](https://github.com/stride3d/stride)
- **[S3]** Releases:
  - 4.4 rewrote the SDSL shader compiler, added NativeAOT and improved the Vulkan and D3D12 back ends;
    D3D12 needs Enhanced Barriers.
  - 4.3 (2025-11-14) brought .NET 10, Bepu Physics and Vulkan compute.

  [gamedev.net / Wikipedia, search snippet only](https://gamedev.net/news/6338-stride-releases440-released/)
- **[S4]** "WPF is the only supported view layer, but ViewModels are written to be platform-agnostic."
  Custom asset editors are a ViewModel plus a WPF view.
  [docs/editor/projects.md and custom-editor.md, repo files read 2026-10-29](https://github.com/stride3d/stride/tree/master/docs/editor)
  An Avalonia editor exists only as an "Experimental prototype".
  [doc.stride3d.net 4.3 community resources, search snippet only](https://doc.stride3d.net/4.3/en/community-resources/engine.html)
- **[S5]** Subsurface scattering offers a "Skin" scattering profile and kernel (Falloff, Strength).
  [doc.stride3d.net 4.0–4.3, search snippet only](https://doc.stride3d.net/4.0/jp/Manual/graphics/materials/subsurface-scattering.html)
- **[S6]** Tests:
  - "Gold images of the GPU tests, compared pixel by pixel".
  - "Game Studio screenshot tests"; WARP and software renderers.
  - Linux runs through WSL2.

  [tests/README.md, repo file read 2026-10-29](https://github.com/stride3d/stride/blob/master/tests/README.md)
- **[S7]** CI builds a Windows runtime and a "Linux Vulkan/OpenGL" runtime.
  [README, repo file read](https://github.com/stride3d/stride)
- **Real products:** none found (search budget ran out).
- **Assessment:** the test design is a good model, but the Windows-only editor fails the cross-platform
  need.

### Bevy (latest 0.20.1)

- **[B1]** v0.20.1 was published 2026-10-28; 49,357 stars. Licence: "dual-licensed under either: MIT
  … Apache License, Version 2.0".
  [GitHub API and README, 2026-10-29](https://github.com/bevyengine/bevy)
- **[B2]** "Bevy is still in the early stages of development. Important features are missing." A
  breaking release comes "approximately once every 3 months". [README, repo file read](https://github.com/bevyengine/bevy)
- **[B3]** Bevy 0.20 (posted 2026-10-08) describes "essential components of a Bevy scene editor", not
  "the editor itself"; a remote inspector is future work. In 0.19 (2026-06-19), BSN "will also be used
  to build the upcoming Bevy Editor".
  [bevy.org 0.20, page read](https://bevy.org/news/bevy-0-20/) · [bevy.org 0.19, page read](https://bevy.org/news/bevy-0-19/)
- **[B4]** Solari, "Bevy's realtime pathtraced renderer", runs on macOS through Metal in 0.20, with
  DLSS-RR 4.5. [bevy.org 0.20, page read](https://bevy.org/news/bevy-0-20/)
- **[B5]** In 0.19, morph-target meshes render in batches ("almost 2x speedup"); rectangular area lights
  use LTC but "don't cast shadows yet"; contact shadows were added. Nothing on SSS, skin or hair.
  [bevy.org 0.19, page read](https://bevy.org/news/bevy-0-19/)
- **[B6]** The Bevy Remote Protocol is JSON-RPC 2.0 over `RemoteHttpPlugin`. The community crate
  bevy_brp_extras adds screenshots and key input for agents.
  [docs.rs bevy_remote / bevy_brp_mcp, search snippet only](https://docs.rs/bevy_remote)
- **Real products:** not verified (search budget ran out before checking Tiny Glade).
- **Assessment:** Bevy is a code-first engine with no editor and almost none of the CC or iClone list;
  for us it is close to "build our own".

### Fyrox (latest 1.0.0)

- **[Y1]** v1.0.0 was published 2026-03-29; MIT; 9,634 stars.
  [GitHub API, 2026-10-29](https://github.com/FyroxEngine/Fyrox)
- **[Y2]** Fyrox 1.0:
  - Released "after 7 years in development".
  - The team is "quite small with little to no funding".
  - It targets PC (Windows, Linux, macOS), WebAssembly and Android.
  - It has a native editor with a project manager, an export CLI, and an animation blending state
    machine editor.

  [fyrox.rs blog 1.0.0, page read](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/)
- **[Y3]** Rendering:
  - The graphics layer is OpenGL (the fyrox-graphics-gl crate).
  - 1.0 isolated OpenGL in its own crate "to transition to modern GAPIs" later.
  - The release candidate notes the renderer "still lacks any global illumination … most likely for
    Fyrox 2.0".

  [docs.rs fyrox-graphics-gl / fyrox.rs RC blog, search snippet only](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0-rc-1/)
- **Real products:** none found.

### Blender (latest 5.2 LTS) — as an add-on, app template or fork

- **[L1]** Licence:
  - "The source code we develop at blender.org is default being licensed as GNU GPL Version 2 or
    later."
  - "The GNU GPL license therefore requires that such scripts (if published) are being shared under a
    GPL compliant license."
  - "What you create with Blender is your sole property." "You can distribute changed versions of
    Blender."

  [blender.org/about/license, undated, page read](https://www.blender.org/about/license/)
- **[L2]** 5.2 LTS was "Released July 14th, 2026", "Supported until July 2028".
  [blender.org/download/releases/5-2, page read](https://www.blender.org/download/releases/5-2/)
- **[L3]** 5.2 highlights [same page, page read]:
  - Cloth: "Quickly add a cloth-like behaviour to any mesh with a new node-based modifier".
  - "Hair physics work similarly to cloth", on a new XPBD Solver node.
  - EEVEE is "2x" faster in instance-heavy scenes.
  - Python: `gpu.init()` for background mode and `Window.screenshot`; Geometry Nodes modifier inputs
    moved to RNA properties ("Scripts … require updates").
  - Export: USD colour spaces, glTF point clouds and meshopt, Alembic camera import.
- **[L4]** Blender 5.0 was released 2025-11-18 and 5.1 on 2026-03-17.
  [devtalk.blender.org / strayspark, search snippet only](https://devtalk.blender.org/t/24-november-2025/43379)
- **[L5]** GPU and render back ends in the source:
  - GPU back ends `opengl`, `vulkan` and `metal` (plus `dummy`); `--gpu-backend` "Valid options:
    'vulkan', 'metal', 'opengl'".
  - Cycles devices `cpu`, `cuda`, `optix`, `hip`, `hiprt`, `oneapi`, `metal`.

  [blender source, GitHub API and creator_args.cc, read 2026-10-29](https://github.com/blender/blender).
  Whether Vulkan is the default is unclear: it was planned for 5.1, and one October 2026 article says
  5.3. [phoronix 2025-10 / xenospectrum 2026-10, search snippet only](https://www.phoronix.com/news/Blender-5.1-Vulkan-Default)
- **[L6]** Command-line arguments include `-b/--background`, `--python`, `--python-expr`,
  `-f/--render-frame`, `--app-template` and `-X/--factory-startup`. `tests/python/` holds test scripts
  such as `bl_animation_armature.py` and `bl_alembic_io_test.py`.
  [creator_args.cc and tests/python, repo files read 2026-10-29](https://github.com/blender/blender/blob/main/source/creator/creator_args.cc)
- **[L7]** MCP servers:
  - The official Blender Lab MCP server is v1.0.0 (2026-04-27): GPL-3.0-or-later, needs Blender 5.1+,
    has 26 tools (code execution, screenshots, API-doc search), and runs model code "without any
    guards".
  - The community blender-mcp (MIT, ~29.3k stars) was renamed "MCP for Blender" on 2026-09-16.

  [strayspark.studio, 2026, page read (third-party blog)](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026)
- **[L8]** "armature deforming a mesh is a cpu intensive process" (a Blender bug-tracker comment).
  UPBGE forum posts say "GPU skinning is already available in current UPBGE master".
  [developer.blender.org T86478 / blenderartists, search snippet only](https://developer.blender.org/T86478)
- **[L9]** EEVEE Next has a subsurface scattering port and the hair and curves work (merged PRs, 2023),
  with later issues about hair shadows and performance.
  [projects.blender.org #107407, #109833, search snippet only](https://projects.blender.org/blender/blender/pulls/109833)
- **[L10]** Bforartists: "a fork of the popular 3D software Blender, with the goal to improve the UI".
  v5.2.0 was published 2026-07-29 (GitHub marks it pre-release); 812 stars; licence in COPYING. Its
  download page says it is based on Blender 5.2.0 and 5.3 alpha, with "Mac builds coming soon".
  [GitHub API, 2026-10-29](https://github.com/Bforartists/Bforartists) ·
  [bforartists.de, search snippet only](https://www.bforartists.de/download)
- **[L11]** Other Blender-based open projects:
  - UPBGE, "the best integrated game engine in Blender": v0.50 on 2026-01-04, 1,850 stars.
  - Armory3D, "3D Engine with Blender Integration": zlib, 26.02 on 2026-02-16, 3,359 stars.

  [GitHub API, 2026-10-29](https://github.com/UPBGE/upbge) · [armory3d](https://github.com/armory3d/armory)
- **Real products:** Bforartists (UI fork), UPBGE (game-engine fork), Armory3D (engine using Blender as
  its editor), and Blender's own MCP server.
- **Assessment:**
  - Blender wins on feature coverage (criterion 8), export and AI testability.
  - It loses on licence (GPL for anything shipped with it) and on owning the UI.
  - Real-time playback of heavy skinned characters is CPU-bound; this was not measured on this machine.
  - An add-on plus app template keeps Blender's look. A fork gives full control, at the cost of
    rebasing every Blender release.

### Other open bases found

- **[W1] Wicked Engine**:
  - "open-source 3D engine with modern graphics. Use this as a C++ framework …, a standalone 3D
    editor, LUA scripting".
  - Builds on Windows, Linux, Mac OS and iOS. "The default renderer is DirectX 12 on Windows, Vulkan on
    Linux and Metal on Apple systems."
  - MIT; v0.72.120 on 2026-10-02; 7,327 stars.

  [README and GitHub API, read 2026-10-29](https://github.com/turanszkij/WickedEngine). Its own
  engine-library role belongs to the other agent's brief; it is listed here as an engine with an editor.
- **[P1] Panda3D**: "Powerful, mature open-source cross-platform game engine for Python and C++,
  developed by Disney and CMU". Latest stable v1.10.16 on 2025-12-25; 5,262 stars; 1.11 only as preview
  builds; Modified BSD licence.
  [GitHub API, 2026-10-29](https://github.com/panda3d/panda3d) ·
  [nuget preview, search snippet only](https://www.nuget.org/packages/panda3d.tools/)
- **Redot**: a Godot fork, see [G14].

---

## Couldn't verify / open

- **Epic's own terms pages refuse scripted access.** unrealengine.com/eula, /license, /faq and the
  pricing blog all returned HTTP 403, so no workaround was tried. The current EULA wording ([U8]) and
  pricing ([U9]) come from search snippets only. A human should read the live EULA (Engine Tools,
  Distribution, royalty sections) and the pricing page before the route decision. The one Epic CDN PDF
  fetched (2021-01-28) could not be read as text.
- **The MetaHuman licence page** (metahuman.com/license) needs an Epic login; its terms come from
  cgchannel's 2025-06-04 report.
- **The full Flax EULA text was not read:** editor redistribution and open-source publishing of a Flax
  app are unknown.
- **The web-search budget ran out** before these were checked:
  - Godot MCP servers; Tiny Glade's use of Bevy.
  - Products built on Stride, Flax and Fyrox.
  - Blender's real-time skinning on the GPU (no Blender source found either way).
  - Unreal's runtime exporters (glTF, USD, FBX) and its morph-target limits.
  - Python bindings for Stride and Bevy.
  - O3DE skin SSS and its sequencer (Track View).
  - Export from O3DE, Stride, Fyrox and Bevy.
- **Performance on the RTX 2070 Super** is unmeasured for every candidate; only vendor spec pages were
  read. A measured test per finalist (one realistic head with strand hair, a skinned body, playback fps)
  is the open step.
- **Blender's licence for MIT add-on code:** whether MIT counts as "GPL compliant" is not checked here
  (the FSF list was not fetched). The user did not ask for legal analysis.
- **Blender's Vulkan default:** sources conflict (5.1 was planned; one October 2026 article says 5.3).
- **Bforartists 5.2.0** is labelled pre-release on GitHub but called a release on its site.
- **Unity facts gathered before it went out** were not written up (by instruction). If it comes back,
  re-run: its plans page says Personal is "For gaming and entertainment applications only", and HDRP
  gets "no new features".
