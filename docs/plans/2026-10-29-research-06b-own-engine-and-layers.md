# Research 06b — Own engine and editor on libraries, and the layers every route needs

Research agent notes, 2026-10-29. Scope: building JustStage's own engine and editor from libraries
(render libraries, editor UI toolkits, language per layer, scripting and plugin embedding, AI testing),
how the major 3D apps are built, and evidence on the effort. Existing engines as bases are out of scope
(another agent).

**Scope change mid-research (the user, via the coordinator, 2026-10-29):** anything that runs on only one
GPU vendor is out; anything paid-only is out (Qt only under its free open-source terms); free-but-proprietary
parts get normal rows with their terms labelled. Every render library carries a GPU-vendor label.

**How to read the labels.** *page read* = I read the page, README, source file or licence file myself.
*search snippet only* = a search engine's summary; the page itself was not opened (or refused scripted
access). *GitHub API* = GitHub's repository API on 2026-10-29 (stars, last push, latest release or tag,
licence field, contributor and commit counts). Assessment lines are my judgement, not facts.
GPU-vendor labels are **derived from the graphics APIs a library lists** (a conformant D3D12/Vulkan driver
exists for NVIDIA, AMD and Intel; Apple means a native Metal backend) — not from a vendor test matrix,
unless the row says the README names vendors.

The web-search budget for the session ran out part-way; the rest was read from primary pages and
GitHub (see "Couldn't verify / open").

---

## Top findings

1. **No open, cross-vendor rendering library ships CC5-class human rendering.** Filament offers "Approximated
   translucent (subsurface) materials" and no hair or eye model; Wicked Engine's hair is "Hair particle
   systems (grass/vegetation)"; The Forge carries a port of AMD's TressFX strand hair. The one kit that does
   skin (Burley diffusion + single scattering) and strand hair (Chiang BSDF, linear-swept spheres) is NVIDIA's
   RTX Character Rendering — under NVIDIA's proprietary RTX SDK licence, Windows/Vulkan only, no Apple.
   Skin, strand hair and eyes are ours to build on any own-engine route.
   — [Filament README](https://github.com/google/filament), [Filament materials](https://google.github.io/filament/main/materials.html), [Wicked features.txt](https://github.com/turanszkij/WickedEngine/blob/master/features.txt), [The Forge README](https://github.com/ConfettiFX/The-Forge), [RTXCR README + License.txt](https://github.com/NVIDIA-RTX/RTXCR)
2. **macOS narrows the field.** Native Metal: wgpu, bgfx, Filament, The Forge, Wicked, Ogre-Next. Diligent's
   native Metal backend is "Available under commercial license" (so out under the no-paid rule; macOS only via
   MoltenVK). NVRHI/Donut have no Metal. MoltenVK's supported-extension list has no Vulkan ray-tracing
   extensions. — [Diligent README](https://github.com/DiligentGraphics/DiligentEngine), [NVRHI README](https://github.com/NVIDIA-RTX/NVRHI), [MoltenVK runtime guide](https://github.com/KhronosGroup/MoltenVK/blob/main/Docs/MoltenVK_Runtime_UserGuide.md)
3. **Ray tracing on all three APIs is rare.** wgpu's ray query is "EXPERIMENTAL" and Vulkan-only; Wicked lists
   DXR and Vulkan ray tracing plus a GPU path tracer; The Forge ships DXR on Windows and Vulkan ray query on
   Steam Deck; Diligent lists ray tracing on D3D12/Vulkan. — [wgpu features.rs](https://github.com/gfx-rs/wgpu/blob/trunk/wgpu-types/src/features.rs), [Wicked features.txt](https://github.com/turanszkij/WickedEngine/blob/master/features.txt), [The Forge README](https://github.com/ConfettiFX/The-Forge)
4. **Professional DCCs use Qt or their own toolkit.** Maya moved to Qt6/PySide6 (2025); Houdini 21 main builds
   are on Qt 6.5.3; Daz Studio 6 is built on Qt 6.10 Community Edition under LGPL; iClone 8's Python API uses
   Qt 5.15.2/PySide2. Blender, Cinema 4D, Unreal (Slate) and Godot (its own Controls) draw their own UI;
   Omniverse's omni.ui is built on Dear ImGui. — [Maya 2025 API guide](https://blog.autodesk.io/maya-2025-api-update-guide/), [Houdini 21 platforms](https://www.sidefx.com/docs/houdini/news/21/platforms.html), [Daz Studio 6 SDK](https://www.daz3d.com/daz-studio-6-sdk), [IC8 Python API](https://wiki.reallusion.com/IC8_Python_API), [Kit overview](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/kit_overview.html)
5. **Qt's free line:** Qt Base (Core, GUI, Widgets, RHI), Qt Declarative (QML/Quick), Shader Tools, SVG,
   Multimedia, Image Formats, WebEngine, Language Server — LGPL-3 (or GPL-2/3). Qt Quick 3D, Quick 3D Physics,
   Quick Timeline, Graphs, Charts, Data Visualization, Virtual Keyboard, Lottie, HTTP Server, Network Auth —
   **GPL-3 or commercial only**. Insight Tracker and VNC Server — commercial only. — SPDX headers in
   [qt/qtbase](https://github.com/qt/qtbase) etc. (page read), [Qt modules page](https://doc.qt.io/qt-6/qtmodules.html)
6. **Qt Widgets can host our own D3D12/Vulkan/Metal renderer:** QRhiWidget (since Qt 6.7) supports OpenGL,
   Metal, Vulkan, D3D11 and D3D12, and allows "rendering code that directly uses a 3D graphics API" through
   `beginExternal()` / `createFrom()`. — [QRhiWidget, Qt 6.12 docs](https://doc.qt.io/qt-6/qrhiwidget.html)
7. **Dear ImGui is used in shipped 3D tools** — Adobe Substance 3D Modeler, OTOY Sculptron, Nomad Sculpt,
   DreamWorks MoonRay GUI, Remedy Northlight, NVIDIA Omniverse — with MIT node-editor and timeline add-ons, but
   no accessibility and a test engine that is free only for individuals, education and open source.
   — [Software using Dear ImGui (edited 2026-10-27)](https://github.com/ocornut/imgui/wiki/Software-using-dear-imgui), [imgui_test_engine](https://github.com/ocornut/imgui_test_engine)
8. **The most AI-testable UI stacks:** egui's `egui_kittest` drives and asserts the UI through the AccessKit
   accessibility tree; Avalonia.Headless runs without a window, simulates input and captures frames for baseline
   comparison. Neither has a professional DCC behind it (egui's showcase is the Rerun viewer).
   — [egui_kittest README](https://github.com/emilk/egui/tree/main/crates/egui_kittest), [Avalonia headless docs](https://docs.avaloniaui.net/docs/concepts/headless/)
9. **Evidence on how well AI agents write each language is thin and conflicting.** SWE-bench Multilingual (Claude
   3.7 Sonnet): Rust 58%, Java 53%, C/C++ 29% (lowest). Multi-SWE-bench: Java above Rust and C++. SWE-Sharp-Bench:
   C# ~40% vs Python ~70% on SWE-bench Verified with the same setups. All 2025 models; none tests graphics code.
   — [SWE-bench Multilingual](https://www.swebench.com/multilingual.html), [Multi-SWE-bench](https://arxiv.org/pdf/2504.02605), [SWE-Sharp-Bench](https://arxiv.org/abs/2511.02352v2)
10. **C++ is the only language where every key 3D library is native** (OpenUSD, PhysX, Jolt, ufbx, Embree, OIDN,
    OpenVDB, MaterialX, Manifold, meshoptimizer). Rust's USD library is a 151-star project; C# USD bindings are
    Unity's (last push 2024-11, experimental). — GitHub API 2026-10-29
11. **Python is the scripting standard of DCCs** (Blender, Maya, Houdini, Cinema 4D, Omniverse Kit, Cascadeur,
    iClone, Marvelous Designer). nanobind claims ~4× faster compile, ~5× smaller binaries and ~10× lower runtime
    overhead than pybind11 and can target Python's Stable ABI; free-threaded CPython lost its "experimental" tag
    in 3.14. — [nanobind README](https://github.com/wjakob/nanobind), [PEP 779](https://peps.python.org/779)
12. **Sandboxed plugins via WebAssembly are now standardised but unproven in DCCs.** WASI 0.3 (native async in the
    component model) released 2026-06-11; Wasmtime 50 (2026-10-20) embeds from C, C++, Python, .NET, Ruby; Extism
    wraps it for many host languages. No DCC using Wasm plugins was found (Zed, a code editor, does).
    — [WASI 0.3](https://wasi.dev/releases/wasi-p3), [wasmtime README](https://github.com/bytecodealliance/wasmtime), [extism README](https://github.com/extism/extism)
13. **Golden-image render tests on software rasterizers are standard practice:** Filament renders headlessly on
    Mesa's software rasterizers and SwiftShader against goldens; Bevy screenshots examples in CI and compares via
    Pixel Eagle; wgpu compares with NVIDIA's FLIP metric and percentile thresholds; Blender compares renders with
    `oiiotool` thresholds. Windows' WARP runs D3D12 (FL 12_0/12_1) and ray-tracing shader stages on the CPU.
    — [Filament renderdiff](https://github.com/google/filament/tree/main/test/renderdiff), [Bevy example-run.yml](https://github.com/bevyengine/bevy/blob/main/.github/workflows/example-run.yml), [wgpu tests/src/image.rs](https://github.com/gfx-rs/wgpu/blob/trunk/tests/src/image.rs), [Blender render_report.py](https://github.com/blender/blender/blob/main/tests/python/modules/render_report.py), [WARP guide](https://learn.microsoft.com/en-us/windows/win32/direct3darticles/directx-warp)
14. **Control channels exist in every ecosystem:** Bevy Remote Protocol (JSON-RPC 2.0); Blender Lab's official MCP
    server (Blender 5.1+, runs LLM-generated code "without any guards"); an experimental MCP plugin in Unreal 5.8
    (secondary sources); Unity AI's MCP (subscription-gated beta). — [bevy_remote](https://github.com/bevyengine/bevy/blob/main/crates/bevy_remote/src/lib.rs), [blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/)
15. **Effort is years and many hands.** Godot: several years in-house, open since Feb 2014, 3,990 contributors,
    87,441 commits. Bevy: since 2020, 1,706 contributors, still no shipped editor (prototype repo archived
    2026-04). Fyrox: 7 years to 1.0 with ~91 % of commits by one developer. Wicked Engine: 11 years, ~89 % one
    developer. — [Godot README](https://github.com/godotengine/godot), [bevy_editor_prototypes](https://github.com/bevyengine/bevy_editor_prototypes), GitHub API 2026-10-29

---

## Tables

### T1 · Rendering libraries and frameworks

Health = GitHub API 2026-10-29 (stars · last push · latest release or tag). Vendors: N = NVIDIA, A = AMD,
I = Intel, Ap = Apple (native Metal). "RT" = hardware ray tracing.

| Library | Lang | APIs → OS | Vendors | For realistic humans | Health | Licence — commercial use | Status (scope) | Source |
|---|---|---|---|---|---|---|---|---|
| **Filament** (Google) | C++ | Vulkan, OpenGL, WebGPU on Win/Linux/macOS; Metal on macOS; no D3D | N A I Ap | PBR (metallic), "Approximated translucent (subsurface)" model, cloth model; no hair/eye model; no RT; skinning + morphs | 20.7k · 2026-10-29 · v1.79.0 (2026-10-26) | Apache-2.0 — yes — [LICENSE](https://github.com/google/filament/blob/main/LICENSE) | In | README + materials doc, page read |
| **bgfx** | C++ (C API) | D3D11, D3D12, Metal, Vulkan, OpenGL 4.3+, WebGPU (Dawn) on Win/Linux/macOS | N A I Ap | Low-level "bring your own engine": no PBR, SSS, hair or RT built in | 17.6k · 2026-10-29 · no releases (rolling) | BSD-2-Clause — yes — [licence](https://bkaradzic.github.io/bgfx/license.html) | In | README, page read |
| **Diligent Engine** | C++ (C API) | D3D11, D3D12, Vulkan, OpenGL on Windows; Vulkan/GL on Linux; macOS: GL, Vulkan via MoltenVK, Metal **commercial only** | N A I; Ap only via MoltenVK (no RT there) | DiligentFX: glTF PBR renderer, **Hydrogent** (Hydra render delegate for OpenUSD), shadows, SSR, SSAO, TAA, DoF, bloom; RT (D3D12/Vulkan), mesh shaders | 4.5k · 2026-10-16 · v2.5.6 (2024-09-02; API tags newer) | Apache-2.0 — yes (native Metal: paid → out) — [License.txt](https://github.com/DiligentGraphics/DiligentEngine/blob/master/License.txt) | In, minus Metal | README + DiligentFX README, page read |
| **wgpu** | Rust | Vulkan, Metal, D3D12, OpenGL; WebGPU/WebGL2 on wasm | N A I Ap | Plain WebGPU-style API; ray query + RT pipelines EXPERIMENTAL, Vulkan only; mesh shaders Vulkan/Metal | 18.4k · 2026-10-29 · v30.0.1 (2026-08-22) | MIT OR Apache-2.0 — yes — [repo](https://github.com/gfx-rs/wgpu) | In | README + `features.rs`, page read |
| **The Forge** | C++ (C99 rewrite of the run-time underway) | D3D12 on Windows ("Removed Vulkan from Windows Run-Time", 2024), Vulkan on Linux/Steam Deck/Android, Metal on macOS/iOS | N A I Ap | Visibility buffer, hybrid RT GI, DXR + Vulkan ray query; **TressFX-derived strand hair** ported (D3D12/Vulkan/Metal 2) in Material Playground; skinning | 5.7k · 2026-08-27 · v1.63 (2025-03-21) | Apache-2.0 — yes (consoles paid, irrelevant) — [repo](https://github.com/ConfettiFX/The-Forge) | In | README, page read |
| **Wicked Engine** | C++ | DX12 (Windows default), Vulkan (Linux, optional Windows), Metal (Apple) | N A I Ap | PBR + glTF KHR material set (sheen, clearcoat, transmission, anisotropy), DXR/Vulkan RT shadows/AO/reflections, GPU path tracer, DDGI, surfel GI, morph targets, humanoid rig, retargeting, expressions, VRM 0/1, hair particles (grass); comes with an Editor app | 7.3k · 2026-10-29 · v0.72.120 (2026-10-02) | MIT — yes — [repo](https://github.com/turanszkij/WickedEngine) | In (it is a whole engine) | README + features.txt, page read |
| **Ogre-Next** | C++ | D3D11, OpenGL 3.3+, Metal, Vulkan; Win/Linux/macOS (Metal "highly recommended") | N A I Ap | Scene-graph engine with PBS; no RT, hair or SSS listed | 1.4k · 2026-10-26 · v3.0.0 (2024-10-15) | MIT — yes — [repo](https://github.com/OGRECave/ogre-next) | In | README, page read |
| **Magnum** | C++ | OpenGL 2.1–4.6, GLES, WebGL (README lists only the GL family) | N A I (macOS GL only) | Toolkit/middleware; no RT | 5.2k · 2026-10-29 · v2020.06 (2020!) | MIT — yes — [repo](https://github.com/mosra/magnum) | In, weak fit | README, page read |
| **NVRHI + Donut** (NVIDIA) | C++ | D3D11, D3D12, Vulkan 1.3 — Windows and Linux only; **no Metal** | N A I; no Ap | RHI with RT/mesh pipelines; NVIDIA-only extras optional (NVAPI, LSS on Blackwell, SER on Ada); Donut does not maintain RT acceleration structures | NVRHI 2.1k · 2026-10-28 · no releases; Donut 0.5k | MIT — yes — [NVRHI](https://github.com/NVIDIA-RTX/NVRHI) | In, but fails macOS without our own Metal backend | README, page read |
| **nvpro-samples vk_gltf_renderer** (NVIDIA) | C++ + Slang | Vulkan 1.4 RT; Windows/Linux | N A I (Vulkan RT); DLSS-RR and OptiX denoiser parts NVIDIA-only; OIDN vendor-neutral | Reference glTF PBR path tracer + small editor; skinning/morphs on GPU | 0.4k · 2026-10-26 · v2026.11 (2026-10-23) | Apache-2.0 — yes — [repo](https://github.com/nvpro-samples/vk_gltf_renderer) | Reference code only | README, page read |
| **Falcor** (NVIDIA research) | C++/Python | D3D12, Vulkan; Windows, "experimental" Ubuntu 22.04; no Metal | README names NVIDIA GPUs only ("a GPU which supports DirectX Raytracing, such as … GeForce RTX") | Research path-tracing framework | 3.3k · 2026-09-21 · 9.0 (2026-09-21) | BSD-3-Clause (bundled NVIDIA SDKs differ) — yes — [LICENSE.md](https://github.com/NVIDIAGameWorks/Falcor/blob/master/LICENSE.md) | **Out** as a base: NVIDIA-oriented, no Apple | README, page read |
| **RTX Character Rendering (RTXCR)** (NVIDIA) | C++ | Vulkan SDK + Windows SDK (Windows) | README: "RTX 20 series or newer. Radeon RX 7000 Series or newer. Intel Arc" → N A I; no Ap | Skin: Burley diffusion profile + single scattering; hair: Chiang BSDF + far-field model, linear-swept spheres (LSS hardware on newest NVIDIA), path tracer sample with DLSS-RR/NRD | 0.1k · 2026-09-11 · v1.4.1 | **Free, proprietary**: "NVIDIA RTX SDKs LICENSE", non-exclusive, non-sublicensable; source visible on GitHub; redistribution only as the licence allows — [License.txt](https://github.com/NVIDIA-RTX/RTXCR/blob/main/License.txt) | Free-proprietary row; reference for techniques | README + licence head, page read |
| **Vulkan direct + helpers** | C/C++ | Vulkan on Win/Linux; macOS via **MoltenVK** (Vulkan 1.4 subset over Metal; no RT extensions listed) | N A I; Ap via MoltenVK | Everything is ours | volk 1.9k · VMA 3.5k (v3.5.0 2026-10-26) · vk-bootstrap 1.3k · MoltenVK 5.9k (v1.4.2 2026-07-24) | volk MIT, VMA MIT, vk-bootstrap MIT, MoltenVK Apache-2.0 — all yes | In | GitHub API; MoltenVK README/guide page read |
| **Slang** (shader language) | C++ compiler | Compiles one shader source for several APIs (targets not checked here) | — | Used by vk_gltf_renderer | 5.8k · 2026-10-29 · v2026.20 (2026-10-17) | Apache-2.0 WITH LLVM-exception — yes — [LICENSE](https://github.com/shader-slang/slang/blob/master/LICENSE) | In (layer, not a base) | licence page read |

Human-rendering building blocks found (all page read or GitHub API, 2026-10-29):

| Part | What | Health | Licence — commercial use | Source |
|---|---|---|---|---|
| AMD TressFX | Strand hair sim + render (D3D12/Vulkan) | 0.8k · last push **2023-01-26** · v4.1.0 (2020) | MIT — yes | [GPUOpen-Effects/TressFX](https://github.com/GPUOpen-Effects/TressFX) (GitHub API) |
| Jimenez Separable SSS | Screen-space skin SSS (2011 code) | 0.7k · last push 2018 | BSD-style (redistribution clause in README) — yes | [iryoku/separable-sss](https://github.com/iryoku/separable-sss) (README page read) |
| vkhr | "Real-Time Hybrid Hair Rendering using Vulkan" (research) | 0.5k · last push 2024-02 | MIT — yes | [CaffeineViking/vkhr](https://github.com/CaffeineViking/vkhr) (GitHub search API) |
| Unity demo-team hair | Strand authoring/sim/render for Unity | 0.8k · last push 2025-02 | Unity Companion License "for Unity-dependent projects" — not usable outside Unity | [LICENSE.md](https://github.com/Unity-Technologies/com.unity.demoteam.hair) (page read) |

### T2 · Editor UI toolkits

| Toolkit | Lang | Docking | Node editor | Timeline | High-DPI | Accessibility | 3D viewport | Pro 3D apps using it | Health | Licence — commercial use | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Qt Widgets** (Qt 6.12, tag 2026-09-30) | C++ (+ PySide6) | `QDockWidget` (LGPL); Qt-ADS (LGPL-2.1, used by Qt Creator, Qt Design Studio, ezEditor); KDDockWidgets (GPL-2/3 or paid) | QtNodes (BSD-3, 3.7k★) | None built in (Qt Quick Timeline is GPL-only and is a QML keyframe module, not an editor widget) | yes (not measured here) | Qt "does use platform-specific APIs to expose the semantic structure" (Widgets and Quick) | **QRhiWidget** (6.7+): D3D11/D3D12/Vulkan/Metal/GL, native interop | Maya, Houdini, Daz Studio 6, iClone 8 (Python layer), Marvelous Designer (snippet) | qtbase mirror 3.1k · 2026-10-29 · v6.12.0 | LGPL-3 for Base/Declarative etc.; GPL-3-only modules listed in Top finding 5 — conditional (LGPL obligations) | SPDX headers, QRhiWidget + accessibility docs, ADS/QtNodes READMEs — page read |
| **Qt Quick / QML** | QML + C++ | No standard docking in Quick (not found) | — | — | yes | as above | Qt Quick 3D is **GPL-3/commercial only** | iClone's Python samples include QML (snippet) | as above | LGPL-3 (Quick 3D GPL-only) — conditional | SPDX headers page read |
| **PySide6** | Python | as Qt | as Qt | — | — | — | — | Maya 2025+, Houdini Python panels, Cinema 4D (importable since 2024.2) | PyPI 6.11.0 (2026-03-23, snippet) | LGPL-3 — conditional | Maya API guide page read; Houdini/C4D snippets |
| **Dear ImGui** (docking branch) | C++ (C bindings via cimgui/dear_bindings) | docking branch + multi-viewports | imgui-node-editor (MIT, 4.5k★, v0.9.4 2026-10-14), imnodes (MIT, last release 2022) | ImSequencer in ImGuizmo (MIT, 4.1k★, 1.10) | 1.92 (2025-06-25) dynamic fonts; `FontScaleDpi` (snippet) | **none** | trivial (draws into your own pass) | Substance 3D Modeler, Sculptron, Nomad Sculpt, MoonRay GUI, Northlight, Omniverse (omni.ui), O3DE, Filament, The Forge | 76.9k · 2026-10-28 · v1.93.0 (2026-10-14) | MIT — yes. Test Engine: free for individuals, education, open source; paid otherwise — conditional | README + wiki (2026-10-27) page read |
| **egui** | Rust | egui_dock (MIT, 0.6k★), egui_tiles (Rerun, egui_crates repo) | egui-snarl (MIT/Apache, 0.6k★) | none found | yes | **AccessKit** (Windows UIA, macOS NSAccessibility, Linux AT-SPI, iOS, Android adapters) | egui-wgpu / custom 3D examples | Rerun viewer (11.7k★); no DCC found | 31.9k · 2026-10-26 · 0.37.0 (2026-10-15) | MIT OR Apache-2.0 — yes | README, AccessKit README, kittest README page read |
| **Avalonia** | C# / .NET | Dock (MIT, 1.5k★, v12.1.0.13 2026-10-28) | NodeEditor (MIT, 0.3k★, v12.0.0) | none found | yes | screen readers via platform APIs on Windows/macOS/Linux (snippet, Avalonia 12 page) | GPU interop (`ICompositionGpuInterop`, OpenGL) (snippet) | none found among DCCs | 31.7k · 2026-10-29 · 12.1.4 (2026-10-09) | MIT — yes (XPF is a separate paid product) | README page read; headless docs page read |
| **Slint** | Rust/C++/JS/Python + `.slint` markup | none found | none found | none found | yes | not checked | wgpu underlay/overlay via `set_rendering_notifier()`; Bevy example (snippet) | none found | 24.3k · 2026-10-29 · v1.18.1 | GPL-3 **or** free Royalty-free 2.0 (desktop/mobile/web, must show attribution) **or** paid — yes under GPL-3 or royalty-free | LICENSE.md page read |
| **wxWidgets** | C++ | wxAUI (not checked) | — | — | — | native controls | native window handle | none found | 7.3k · 2026-10-27 · v3.3.4 (2026-10-10) | wxWindows Licence (LGPL + exception) — yes (not re-read) | README page read |
| **RmlUi** | C++ (HTML/CSS-like) | — | — | — | — | — | bring-your-own renderer | games | 4.6k · 2026-10-28 · 6.3 | MIT — yes | README page read |
| GTK 4, Flutter desktop | C / Dart | not checked | — | — | — | — | — | — | Flutter 180.6k★ | LGPL-2.1 / BSD-3 | not researched (budget) |
| WPF | C# | — | — | — | — | — | — | — | — | MIT | **Out**: Windows-only |
| NoesisGUI | C++ XAML | — | — | — | — | — | — | — | — | Paid only (Indie €195/project; no free tier) | **Out** — [licensing page](https://www.noesisengine.com/licensing.php), page read |

### T3 · Languages per layer

| Language | Engine core | Editor UI | Plugins / scripting | 3D ecosystem (native) | AI-agent evidence | Source |
|---|---|---|---|---|---|---|
| **C++** | Every pro DCC and every render lib in T1 except wgpu; Blender is 80.8 % C++, Godot 86.8 % | Qt Widgets, Dear ImGui, wxWidgets, RmlUi | C ABI plugins; hosts CPython (pybind11/nanobind), Lua, .NET, wasmtime | OpenUSD 7.6k★ v26.11.1; PhysX (BSD-3) 4.8k★; Jolt (MIT) 11.8k★ v5.6.0; ufbx (MIT or public domain); cgltf/fastgltf (MIT); ozz-animation 3.0k★; meshoptimizer (MIT) 8.7k★; Manifold (Apache) 2.4k★; libigl (MPL-2 + GPL parts); CGAL; Embree/OIDN/OpenVDB/MaterialX (Apache) | SWE-bench Multilingual: C/C++ 28.6 % (lowest of 7 groups); Multi-SWE-bench C++ 3–12 % in visible rows | GitHub API; [SWE-bench Multilingual](https://www.swebench.com/multilingual.html) page read; Multi-SWE-bench snippet |
| **Rust** | wgpu, Bevy (94.6 % Rust), Fyrox | egui, Slint | PyO3 (embed Python), wasmtime (native), Rhai/Lua (not checked) | glam 2.1k★, nalgebra 4.8k★, Rapier 6.0k★, gltf crate (1.0.0 from 2022), **OpenUSD: mxpv/openusd 151★, openusd-rs 37★**, FBX: bevy_ufbx 19★; physx-rs **archived** | SWE-bench Multilingual: Rust 58.1 % (highest); Multi-SWE-bench: Rust 5.9–7.1 % (below Java) | GitHub API + search API; benchmarks above |
| **C# / .NET 10** | Stride (98.9 % C#), Flax (C++ core 47.6 % + C# 46.8 %) | Avalonia | .NET hosting from C++ (hostfxr; one runtime per process) | SharpGLTF (MIT) 0.6k★, BepuPhysics2 (Apache) 3.0k★, JoltPhysicsSharp (MIT) 0.4k★, USD: Unity's usd-unity-sdk (last push 2024-11, 3.0.0-exp.5) | SWE-Sharp-Bench: ~40 % C# vs ~70 % Python (same setups) | GitHub API; SWE-Sharp-Bench snippet; .NET hosting docs page read |
| **Python** | — | PySide6 panels | **The DCC scripting standard** (see T6) | OpenUSD ships Python bindings (not re-checked) | SWE-bench Verified ~70 % (via SWE-Sharp-Bench paper) | T6 sources |
| **Zig** | young | — | — | none checked | none found | ziglang/zig moved to Codeberg ("This repository is not mirrored"); latest GitHub release 0.15.1 (pre-1.0) — GitHub API + README page read |

### T4 · Scripting and plugin embedding

| Option | What it gives | Costs / limits | Who uses it | Health | Licence — commercial use | Source |
|---|---|---|---|---|---|---|
| **CPython + nanobind** (C++) | C++↔Python bindings; Stable-ABI builds | Python's GIL unless free-threaded build; claims ~4× faster compile, ~5× smaller binaries, ~10× lower overhead than pybind11 | IREE etc. (README quotes); DCCs use CPython itself (T6) | 3.8k · 2026-10-20 · v3.1.0 | BSD-3 — yes | [README](https://github.com/wjakob/nanobind), page read |
| **CPython + pybind11** (C++) | The established binding layer | 3.0 (2025-07-10) was an ABI bump; added smart_holder, multi-phase init, subinterpreter support | widely used (not enumerated) | 18.0k · 2026-10-29 · v3.1.0 (2026-08-06) | BSD-3 — yes | [v3.0.0 release notes](https://github.com/pybind/pybind11/releases/tag/v3.0.0), page read |
| **CPython + PyO3** (Rust) | Rust modules for Python, or Python embedded in Rust | Embedding needs a shared-library Python | Rerun (12 % Python), blake3-py | 16.3k · 2026-10-28 · v0.30.1 | MIT OR Apache-2.0 — yes | [README](https://github.com/PyO3/pyo3), page read |
| Free-threaded CPython | No GIL | target ≤10 % slowdown, ≤15–20 % memory growth; stable ABI for it expected in 3.15 | — | PEP 779 Final 2025-06-16 | PSF — yes | [PEP 779](https://peps.python.org/779), search snippet only |
| **Lua 5.5 / LuaJIT + sol2** | Small, fast embedded scripting | sol2 last release 2022 (tag v3.5.0, last push 2025-03); LuaJIT has no releases | Wicked Engine (Lua scripting), RmlUi plugin | Lua mirror 10.4k · v5.5.1 (2026-08-05); LuaJIT 5.8k | MIT (Lua, LuaJIT, sol2) — yes | GitHub API; Wicked features page read |
| **.NET hosting** (hostfxr/nethost) | C# plugins in a C++ host | "Only one runtime can be loaded inside a single process"; framework-dependent deployments only | Maya (.NET 8 since 2025), Godot C# (not re-checked) | dotnet/runtime v10.0.13 (2026-10-13) | MIT — yes | [MS Learn, updated 2026-08-10](https://learn.microsoft.com/en-us/dotnet/core/tutorials/netcore-hosting), page read |
| **Stable C ABI** for native plugins | Native-speed plugins any language can target | We own ABI stability; no sandbox | Godot GDExtension (extensions for an earlier minor version work in later ones, "not vice-versa"); Omniverse Carbonite ("shared libraries with C-style interfaces"); OpenFX (ASWF, BSD-3, v1.5.1 2025-11-20) | godot-cpp 2.8k · 10.0.0-stable (2026-09-15) | MIT / BSD-3 — yes | godot-cpp README, Kit overview — page read |
| **wasmtime** (+ component model, WIT, WASI 0.3) | Sandboxed plugins in any language that compiles to Wasm | No GPU access from inside the sandbox (no checked source for a GPU API); rust toolchain for WASI 0.3 needs nightly in places (snippet) | Zed editor extensions (third-party summary only) | 18.8k · 2026-10-29 · v50.0.0 (2026-10-20) | Apache-2.0 WITH LLVM-exception — yes | README page read; WASI 0.3 snippet |
| **Wasmer** | Alternative Wasm runtime | — | — | 21.2k · v7.5.0 (2026-10-01) | MIT — yes | GitHub API |
| **Extism** | Plugin framework over Wasm; host SDKs for Rust, JS, Go, Java, .NET, Python, PHP, OCaml, Haskell, Elixir, Perl… | an extra layer over the runtime | — | 5.8k · v1.41.0 (2026-10-09) | BSD-3 — yes | README page read |

### T5 · How AI agents can test a 3D app

| Approach | Tool / precedent | What it does | Source (status) |
|---|---|---|---|
| Golden images on CPU rasterizers | **Filament renderdiff** | Headless `gltf_viewer` on Mesa software rasterizers (OpenGL, Vulkan, WebGPU) and on SwiftShader in headless Chromium; separate goldens per platform; JSON test descriptions | [test/renderdiff/README.md](https://github.com/google/filament/tree/main/test/renderdiff) — page read |
| Golden images, perceptual metric | **wgpu** reftests | NVIDIA FLIP error map; tests fail when a chosen percentile exceeds a threshold | [tests/src/image.rs](https://github.com/gfx-rs/wgpu/blob/trunk/tests/src/image.rs) — page read |
| Screenshot CI | **Bevy** | Runs examples with `CI_TESTING_CONFIG`, saves screenshots (macOS runner; Linux under `xvfb-run` with `mesa-vulkan-drivers`), sends them to Pixel Eagle for comparison | [example-run.yml](https://github.com/bevyengine/bevy/blob/main/.github/workflows/example-run.yml) — page read |
| Render regression | **Blender** | `render_report.py` compares renders against reference PNGs with `oiiotool`, fail threshold and fail percent; an update mode rewrites references | [render_report.py](https://github.com/blender/blender/blob/main/tests/python/modules/render_report.py) — page read |
| D3D12 on CPU | **WARP** | Software rasterizer in Windows; D3D12 FL 12_0/12_1 since Win10 1709, FL 12_2 in preview; compiles raytracing shader stages; NuGet DLLs "cannot be redistributed" | [WARP guide, updated 2025-07-24](https://learn.microsoft.com/en-us/windows/win32/direct3darticles/directx-warp) — page read |
| Vulkan on CPU | Mesa lavapipe / llvmpipe; SwiftShader (Apache-2.0, 2.6k★) | used by Filament and Bevy CI above | Filament/Bevy files above; Mesa doc URL 404 |
| UI tests through accessibility | **egui_kittest** | Harness finds widgets by label via AccessKit, clicks, asserts state; snapshot support | [README](https://github.com/emilk/egui/tree/main/crates/egui_kittest) — page read |
| Headless UI + frame capture | **Avalonia.Headless** | No visible window; xUnit/NUnit; simulated keyboard/mouse/drag; Skia frame capture vs baselines | [docs, updated 2026-10-09](https://docs.avaloniaui.net/docs/concepts/headless/) — page read |
| ImGui automation | **Dear ImGui Test Engine** | Runs windowed or headless; screenshots/videos | [README](https://github.com/ocornut/imgui_test_engine) — page read (licence conditional, see T2) |
| Control channel, JSON-RPC | **Bevy Remote Protocol** | `RemotePlugin` + HTTP transport; JSON-RPC 2.0 methods like `world.get_components` to inspect and alter ECS state | [bevy_remote/src/lib.rs](https://github.com/bevyengine/bevy/blob/main/crates/bevy_remote/src/lib.rs) — page read |
| Control channel, MCP | **Blender Lab MCP server** (official) | Natural-language interface to Blender's Python API; needs Blender 5.1+; add-on 1.0.3; warns it executes LLM code "without any guards" | [blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/) — page read |
| | MCP for Blender (community, ex blender-mcp) | 32.7k★, MIT, last push 2026-10-29 | GitHub API |
| | Unreal 5.8 "Unreal MCP" plugin (experimental) | In-editor HTTP server, tool calls run serially on the game thread, no auth | a2a-mcp.org / State of Unreal 2026 — **search snippet only** (Epic page 403) |
| | unreal-mcp (community) | 2.1k★, **last push 2025-04-22**, no licence | GitHub API |
| | Unity AI MCP (official beta) / unity-mcp (CoplayDev, MIT, 15.5k★) | official one needs a Unity AI subscription | gamedev.net 2026-05-11 — search snippet only; GitHub API |
| | godot-mcp (community) | 6.4k★, MIT, last push 2026-04 | GitHub API |
| Deterministic frame output | **Godot Movie Maker** | Non-real-time recording, "perfect frame pacing"; `--write-movie`, `--fixed-fps`, `--quit-after N`; PNG-sequence output | [Godot 4.7 docs](https://docs.godotengine.org/en/stable/tutorials/animation/creating_movies.html) — page read |
| Frame capture/debug | **RenderDoc** | Vulkan, D3D11, D3D12, OpenGL on Windows/Linux; **no Metal** | 11.2k★, MIT, v1.46 (2026-08-31) — README page read |

### T6 · How professional 3D apps are built (public information only)

| App | UI toolkit | Core language | Scripting / plugins | Graphics notes | Source (status) |
|---|---|---|---|---|---|
| **Blender** | Own toolkit; UI layout written in Python (81 `bl_ui` files: headers, menus, panels) | C++ 80.8 %, Python 15 %, C 1.4 % | Embedded CPython (`bpy`), add-ons; C/C++ core | GPU module has `opengl`, `vulkan`, `metal` backends; Vulkan default on Windows (non-ARM) and Linux announced in 5.3 notes | GitHub mirror (API) page read; Vulkan default: developer.blender.org via **search snippet only** (403) |
| **Maya** | Qt 6 (moved from Qt 5 in 2025) | C++ | Python (PySide6), MEL, C++ API, .NET 8 | Viewport 2.0 | [Maya 2025 API guide, 2024-03-26](https://blog.autodesk.io/maya-2025-api-update-guide/) — page read |
| **Houdini 21** | Qt 6.5.3 main builds (Qt 5.15.2 variant); custom PySide6 panels | C++ (HDK) | Python (HOM), VEX, HDK | VFX Reference Platform CY2025 | [platforms page](https://www.sidefx.com/docs/houdini/news/21/platforms.html) page read; PySide6 panels snippet |
| **Cinema 4D** | Own (`GeDialog`); PySide6 importable since 2024.2 but unsupported by Maxon | C++ | Python API = subset of C++ API | — | Maxon developer forum — search snippet only |
| **Godot editor** | Godot's own Control nodes (`editor_node.cpp` includes `scene/gui/...`) | C++ 86.8 % | GDScript, C#, GDExtension (C ABI) | RenderingDevice (not checked) | GitHub page read; developer quote snippet |
| **Unreal editor** | Slate — custom C++ UI framework, "platform agnostic" | C++ | Blueprints, Python editor scripting (not re-checked) | — | Epic Slate overview — search snippet only |
| **Omniverse Kit** (out as a base) | omni.ui "built on top of Dear ImGui", C++ with Python-only API | C++ (Carbonite) | Python extensions; Carbonite C-style plugins | USD + Hydra → RTX | [Kit overview, updated 2026-10-20](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/kit_overview.html) — page read |
| **Cascadeur** | not found | not found | Python 3.8, `csc` module; `call_action` by command ID (being phased out) | — | cascadeur.com help — search snippet only |
| **Marvelous Designer** | not confirmed; API setup needs Qt 5.15.2 path (support thread) | not found | Python API (v10+), no headless mode (support) | Linux version 2025 | developer.marvelousdesigner.com + support — search snippet only |
| **Daz Studio 6** | Qt 6.10 Community Edition, LGPL | C++ SDK | Daz Script (extension of Qt Script, ECMAScript 5.1 — for 4.x) | — | [DS 6 SDK page](https://www.daz3d.com/daz-studio-6-sdk) page read (alpha/beta); Daz Script snippet |
| **iClone 8** | Qt (inferred: Python API is Qt 5.15.2/PySide2; `RLPy.RUi.CreateRDockWidget()` wraps as Qt widget) | not public | Python 3.8 (RLPy), PySide2, QML samples | — | [IC8 Python API (2023-04-10)](https://wiki.reallusion.com/IC8_Python_API) page read; dock-widget snippet |
| **Character Creator 5** | not public | not public | RLPy API in CC5.1 (bug report) | — | Reallusion feedback tracker — search snippet only |
| Wicked Engine Editor | own (engine GUI) | C++/C | Lua | DX12/Vulkan/Metal | README page read |

---

## Facts per question

### Q1 · Rendering libraries

- Filament: "real-time physically based rendering engine for Android, iOS, Linux, macOS, Windows"; backends OpenGL 4.1+, Metal, Vulkan 1.0, WebGPU; "Approximated translucent (subsurface) materials" — https://github.com/google/filament, read 2026-10-29, page read.
- Filament shading models: lit, subsurface, cloth, unlit, specularGlossiness; no hair, strand or eye model ("Eyes"/"Hair" appear only in a reflectance table) — https://google.github.io/filament/main/materials.html, current, page read (first 100k of 152k chars).
- Filament v1.79.0 released 2026-10-26; 20,667 stars; Apache-2.0 — GitHub API 2026-10-29.
- bgfx renderers: Direct3D 11, Direct3D 12, GNM (licensed PS4 devs only), Metal, OpenGL 4.3+, OpenGL ES 3.0+, Vulkan, WebGPU (Dawn Native only); "Bring Your Own Engine/Framework" style; BSD-2 — https://github.com/bkaradzic/bgfx, page read.
- Diligent: D3D11, D3D12, OpenGL/GLES, Vulkan, Metal, WebGPU; macOS Vulkan "requires … MoltenVK"; Metal "Available under commercial license"; supports "Ray-tracing, mesh shaders, tile shaders, bindless resources, variable rate shading"; Apache-2.0 — https://github.com/DiligentGraphics/DiligentEngine, page read.
- DiligentFX: glTF loader, Hydrogent ("an implementation of the Hydra rendering API in Diligent Engine"), shadows, SSR, SSAO, DoF, bloom, epipolar light scattering, TAA, tone mapping — https://github.com/DiligentGraphics/DiligentFX, page read.
- Diligent's last tagged release v2.5.6 is from 2024-09-02; core repo pushed 2026-10-29 — GitHub API.
- wgpu: "runs natively on Vulkan, Metal, D3D12, and OpenGL; and on top of WebGL2 and WebGPU on wasm"; Vulkan on macOS needs MoltenVK — https://github.com/gfx-rs/wgpu, page read.
- wgpu `EXPERIMENTAL_RAY_QUERY`: "THIS IS EXPERIMENTAL … may have major bugs … Supported platforms: Vulkan"; ray-tracing pipelines also experimental — `wgpu-types/src/features.rs` on trunk, page read 2026-10-29.
- The Forge platforms: Windows 10/11 with DirectX 12/DXR; Steam Deck with Vulkan ray query; macOS 11/14 (Intel and Apple silicon); Android; Quest; consoles under paid licence — https://github.com/ConfettiFX/The-Forge, page read.
- The Forge 1.59 (2024-09-06): "Removed Vulkan from Windows Run-time … Concluding that Vulkan is not a good API for PC anymore" — same README, page read.
- The Forge Material Playground: TressFX hair ported; "now runs on PC with DirectX 12 / Vulkan, macOS and iOS with Metal 2 and on the XBOX One" (an older release note kept in README) — page read.
- The Forge's latest release v1.63 is 2025-03-21; last push 2026-08-27 — GitHub API.
- Wicked Engine: "The default renderer is DirectX 12 on Windows, Vulkan on Linux and Metal on Apple systems"; features.txt lists DX12/Vulkan/Metal renderers, real-time ray tracing (DXR and Vulkan), GPU path tracing, DDGI, surfel GI, morph targets, humanoid rig, animation retargeting, expressions, VRM 0.0/1.0 extensions, hair particle systems (grass/vegetation), Lua scripting, physics (rigid/soft body, ragdoll) — https://github.com/turanszkij/WickedEngine (README + features.txt), page read.
- Ogre-Next renderers: Direct3D 11, OpenGL 3.3+, Metal, Vulkan; MIT — https://github.com/OGRECave/ogre-next, page read.
- Magnum graphics APIs listed: OpenGL 2.1–4.6, OpenGL ES, WebGL; last release v2020.06 — README page read; GitHub API.
- NVRHI: "abstraction layer over … Direct3D 11, Direct3D 12, and Vulkan 1.3. It works on Windows and Linux"; supports graphics, compute, ray tracing and meshlet pipelines; LSS listed as "DX12, Blackwell+"; MIT — https://github.com/NVIDIA-RTX/NVRHI, page read.
- Donut: Windows or Linux; "does not provide any ray tracing passes or even maintain acceleration structures"; MIT — https://github.com/NVIDIA-RTX/Donut, page read.
- vk_gltf_renderer: "Open-source Vulkan RTX path tracer and PBR material reference for glTF 2.0" with a scene editor; Windows/Linux; DLSS-RR, OptiX denoiser and OIDN; Apache-2.0; successor of the now-archived vk_raytrace — https://github.com/nvpro-samples/vk_gltf_renderer, page read.
- Falcor: "real-time rendering framework supporting DirectX 12 and Vulkan"; requires "a GPU which supports DirectX Raytracing, such as the NVIDIA Titan V or GeForce RTX"; Linux "experimental"; licence BSD-3 text — https://github.com/NVIDIAGameWorks/Falcor, page read.
- RTXCR: "implements techniques used for rendering realistic human hair and skin"; hair: Chiang BSDF and a far-field model; LSS reduces memory "up to 38%" and improves frame rate "30%" versus polytubes; skin: Burley diffusion profile + single scattering; requirements "RTX 20 series or newer. Radeon RX 7000 Series or newer. Intel Arc Series", Vulkan SDK 1.4.313.2, Windows SDK; licence "NVIDIA RTX SDKs LICENSE" (non-exclusive, non-transferable, no sublicensing) — https://github.com/NVIDIA-RTX/RTXCR, page read.
- MoltenVK: "a layered implementation of Vulkan 1.4" subset over Metal; its runtime guide's supported-extension list contains no `VK_KHR_ray_*` / `VK_KHR_acceleration_structure` entries (grep of the guide) — https://github.com/KhronosGroup/MoltenVK, page read.
- TressFX last push 2023-01-26, last release v4.1.0 (2020) — GitHub API.
- Assessment: for a cross-vendor, Windows+macOS+Linux, free renderer with ray tracing on every OS, **Wicked Engine** and **The Forge** are the only bases found that list D3D12 (or Vulkan) + Metal + hardware RT; Wicked is a whole engine (MIT, very active, one main developer), The Forge is a framework (Apache-2.0, slower release cadence, no Vulkan on Windows). **wgpu** is the strongest cross-vendor RHI if the route is Rust, but its RT is experimental and Vulkan-only (no RT on macOS or D3D12). **Diligent** is the best-structured C++ RHI with an OpenUSD Hydra delegate, but its macOS story under the no-paid rule is MoltenVK without RT. Skin SSS, strand hair and eyes must be written on any base; RTXCR and TressFX are references for the techniques, not drop-ins.

### Q2 · Editor UI toolkits

- Qt 6.12.0 tagged 2026-09-30 (qtbase); Qt 6.11 released March 2026 (Phoronix dated 2026-03-23) — GitHub API; search snippet only.
- SPDX headers on the `dev` branch: qtbase (`qobject.cpp`, `qdockwidget.cpp`, `qrhi.cpp`), qtdeclarative (`qquickitem.cpp`), qtshadertools, qtsvg, qtmultimedia, qtwebengine, qtimageformats, qtlanguageserver = "LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only"; qtquick3d, qtquick3dphysics, qtgraphs, qtcharts, qtdatavis3d, qtquicktimeline, qtvirtualkeyboard, qtlottie, qthttpserver, qtnetworkauth = "LicenseRef-Qt-Commercial OR GPL-3.0-only" — github.com/qt/*, read 2026-10-29, page read (one source file per module).
- Qt Insight Tracker and Qt VNC Server are "Qt Commercial Modules" — https://doc.qt.io/qt-6/qtmodules.html (Qt 6.12 docs), page read.
- QRhiWidget: QWidget for rendering through QRhi, "portable counterpart to QOpenGLWidget"; since Qt 6.7; APIs OpenGL, Metal, Vulkan, D3D11, D3D12; default D3D11 on Windows; one backend per window; native rendering via `QRhiCommandBuffer::beginExternal()` and `QRhiTexture::createFrom()`; device configuration "limited" — https://doc.qt.io/qt-6/qrhiwidget.html (6.12), page read.
- Qt accessibility: "Qt does use platform-specific APIs to expose the semantic structure of your GUI"; covers Widgets and Quick — https://doc.qt.io/qt-6/accessible.html (6.12), page read (the page names no specific platform APIs).
- Qt Advanced Docking System: LGPL-2.1, Qt 6 support, dark mode, native Wayland (5.0), Python bindings; showcase lists Qt Creator, Qt Design Studio, ezEditor, PlotJuggler, Ramses Composer — https://github.com/githubuser0xFFFF/Qt-Advanced-Docking-System, page read; 2.5k★, v5.1.1 2026-08-20 (GitHub API).
- KDDockWidgets: GPL-2.0 or GPL-3.0, commercial from KDAB — LICENSE.txt page read.
- QtNodes (paceholder/nodeeditor): model-view graph editor on QGraphicsScene, dataflow model; BSD-3; 3.7k★; last push 2026-07-31 — README page read; GitHub API.
- Dear ImGui purpose: "content creation tools and visualization / debug tools (as opposed to UI for the average end-user)"; recommends syncing to `master` or `docking` branch — https://github.com/ocornut/imgui, page read.
- Dear ImGui 1.92.0 (2025-06-25) added dynamic fonts; DPI via `style.FontScaleDpi` — search snippet only.
- Dear ImGui Test Engine licence: "free for individuals, educational, open-source" (paid otherwise); can run headless and export screenshots/videos — https://github.com/ocornut/imgui_test_engine, page read.
- egui: immediate-mode Rust GUI; native backend egui-wgpu; "egui can be used to create professional looking applications, like the Rerun Viewer"; accessibility via AccessKit, "enabled by default in eframe" — https://github.com/emilk/egui, page read.
- egui's README states the immediate-mode drawbacks: layout of dynamically sized content is hard, and very large UIs cost CPU each frame — same, page read.
- Dual licences confirmed by the licence files in each repo root: egui, wgpu, PyO3 and egui_crates carry both LICENSE-MIT and LICENSE-APACHE; wasmtime's LICENSE includes the "LLVM Exceptions to the Apache 2.0 License" — GitHub API 2026-10-29, page read.
- AccessKit adapters: Windows (UI Automation), macOS (NSAccessibility), Unix (AT-SPI via zbus), iOS, Android; "suitable for immediate-mode GUI toolkits" — https://github.com/AccessKit/accesskit, page read.
- Avalonia: MIT; Windows, macOS, Linux, iOS, Android, WebAssembly; Avalonia XPF is a separate commercial product — https://github.com/AvaloniaUI/Avalonia, page read.
- Avalonia 12: screen-reader support via platform accessibility APIs on Windows, macOS, Linux, iOS, Android; 12.1.0 adds desktop OpenGL via EGL — search snippet only (avaloniaui.net/avalonia, newreleases.io).
- Slint licences: Royalty-free 2.0 (free for proprietary desktop/mobile/web apps with attribution; not embedded), GPLv3, or commercial; "your own files can stay MIT or Apache-2.0" under GPLv3 — LICENSE.md page read.
- Slint wgpu integration: underlay/overlay via `slint::Window::set_rendering_notifier()` using Slint's device and queue; feature-gated, versioned wgpu modules may change in minor releases; Bevy example exists — search snippet only.
- wxWidgets: "cross-platform C++ framework for writing advanced GUI applications using native controls" — README page read.
- RmlUi: "C++ user interface package based on the HTML and CSS standards", bring your own renderer, Lua plugin, MIT — README page read.
- NoesisGUI: no free tier; Indie €195/project for revenue/funding ≤€100K — https://www.noesisengine.com/licensing.php, page read → out.
- Assessment: for a panel-heavy, node-and-timeline editor that must also be accessible and testable, **Qt Widgets (LGPL-3, C++, with Qt-ADS and QtNodes, QRhiWidget for the viewport)** is the industry pattern (Maya, Houdini, Daz Studio 6) and keeps JustStage MIT if Qt is linked dynamically and the GPL-only modules (Quick 3D, Quick Timeline, Graphs, Charts, HTTP Server…) are avoided. **Dear ImGui** is the fastest to build tools with and is proven in sculpting/modelling tools (Substance 3D Modeler, Sculptron, Nomad), but has no accessibility tree, which removes the cheapest way for AI agents to drive and assert the UI. **egui** has the best AI-test story (kittest over AccessKit) but no DCC precedent and Rust-only. Timeline widgets are build-our-own in every toolkit (only ImSequencer exists, and it is basic).

### Q3 · How existing 3D apps are built

- Blender: first source files 2 January 1994; GPL release 13 October 2002 after a €110,000 crowdfunding; 2.5 UI rewrite work began early 2008; 2.8 (July 2019) "drastically revamped user interface"; "some twenty-eight employees" — https://www.blender.org/about/history/ (undated), page read.
- Blender source language mix: C++ 80.8 %, Python 15 %, C 1.4 % — GitHub API (blender/blender mirror) 2026-10-29.
- Blender's UI headers, menus and panels are Python classes (e.g. `VIEW3D_HT_header(Header)`, `VIEW3D_MT_editor_menus(Menu)`), 81 Python files in `scripts/startup/bl_ui` — GitHub mirror, page read.
- Blender GPU module has `opengl`, `vulkan`, `metal` backend folders — GitHub mirror listing, page read.
- Blender 5.0 kept OpenGL default (Vulkan doesn't offload GPU memory to RAM as OpenGL drivers do); 5.3 notes: "Vulkan backend is now default on Windows (not ARM) and Linux" — Phoronix 2025 / developer.blender.org, search snippet only (developer.blender.org returns 403 to scripted fetch).
- Maya 2025: "Maya has moved from Qt5 and PySide2 to Qt6 and PySide6"; .NET 8 default; VS 2022 17.8.3+ — https://blog.autodesk.io/maya-2025-api-update-guide/ (2024-03-26), page read.
- Houdini 21: "The main Houdini builds are now on Qt 6.5.3. Separate Qt 5.15.2 build are available"; targets VFX Platform CY2025 — https://www.sidefx.com/docs/houdini/news/21/platforms.html, page read.
- Houdini Python Panel pane embeds custom PySide6/PyQt6 UIs; `hou.qt` offers Houdini-styled widgets — sidefx.com docs, search snippet only.
- Cinema 4D: Python API is a subset of the C++ API; PySide6 importable since 2024.2 but Maxon "does not recommend" third-party UI libraries — developers.maxon.net forum, search snippet only.
- Godot: "Before being open sourced in February 2014, Godot had been developed by Juan Linietsky and Ariel Manzur for several years as an in-house engine" — https://github.com/godotengine/godot README, page read.
- Godot's editor is built from engine controls: `editor/editor_node.cpp` includes `scene/gui/control.h`, `menu_bar.h`, `file_dialog.h` etc.; editor folders include `docks`, `inspector`, `animation`, `plugins` — GitHub, page read. A Godot maintainer: "built with Godot's own Control nodes … there's no external toolkit" — Steam forum, search snippet only.
- Unreal: Slate is "a custom UI framework" for tools and in-game UI including the Unreal Editor, render-agnostic, independent of Engine/Editor modules — Epic Slate overview + 2014 DevCon talk, search snippet only.
- Omniverse Kit: "Omni.ui, our UI framework, is built on top of Dear Imgui and written in C++, but exposes only a Python API"; Carbonite is the C++ core SDK; extensions are "versioned packages with a runtime enabled/disabled state"; USD "is the primary Scene Description" — https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/kit_overview.html (updated 2026-10-20), page read.
- Cascadeur: Python 3.8; `csc` module with app, action, dialog and scene managers; `call_action("Scene.Undo")` to be phased out for direct API — cascadeur.com help, search snippet only.
- Marvelous Designer: Python API (version 10 and later), Windows and macOS; support says no headless simulation mode; a support thread needs Qt 5.15.2 on the path for the API module — developer.marvelousdesigner.com + support.marvelousdesigner.com, search snippet only.
- Daz Studio 6.x SDK (alpha/beta): "A separate download and installation of Qt 6.10 is required"; DS 6 "is built using the Qt Community Edition, under the GNU Lesser General Public License (LGPL)"; SDK is C++ — https://www.daz3d.com/daz-studio-6-sdk (© 2026), page read. DS 4.5+ was Qt 4.8; Daz Script 2 extends Qt Script (ECMAScript 5.1) — docs.daz3d.com, search snippet only.
- iClone 8: "iClone 8 adopts Python 3.8 and Qt 5.15.2"; PySide2 must be initialised in scripts — https://wiki.reallusion.com/IC8_Python_API (2023-04-10), page read. `RLPy.RUi.CreateRDockWidget()` dock widgets wrapped for PySide2; QML samples — wiki.reallusion.com / reallusion.com, search snippet only.
- Character Creator 5: a feedback-tracker bug report shows the RLPy API used inside CC5.1 — reallusion.com FeedBackTracker, search snippet only. CC5 shipped August 2025 (cgchannel, search snippet only).
- Assessment: the apps JustStage imitates (CC/iClone) and its references (Maya, Houdini, Daz Studio) are **C++ cores with Qt UIs and an embedded CPython**. The apps with their own toolkit (Blender, C4D, Unreal, Godot) built it over many years; Omniverse shows Dear ImGui can carry a large editor when wrapped (omni.ui) with Python on top.

### Q4 · Language per layer

- SWE-bench Multilingual: 300 tasks, 42 repos, 9 languages; SWE-agent + Claude 3.7 Sonnet: Rust 58.14 %, Java 53.49 %, PHP 48.84 %, Ruby 43.18 %, JS/TS 34.88 %, Go 30.95 %, C/C++ 28.57 %; "Rust having the highest resolution rate and C/C++ the lowest" — https://www.swebench.com/multilingual.html (2025), page read.
- Multi-SWE-bench (ByteDance, arXiv 2504.02605, April 2025): "high-level general-purpose languages (like Python and Java) showing better resolved rates than systems programming languages (Go, Rust) and low-level … (C, C++)"; e.g. Claude 3.7 Sonnet + MSWE-agent Java 23.44 %, Rust 6.69 %, C++ 11.63 % — search snippet only.
- SWE-Sharp-Bench (Microsoft, arXiv 2511.02352, Nov 2025): 150 instances from 17 C# repos; about 40 % resolved vs about 70 % for Python on SWE-bench Verified with the same model-agent setups — search snippet only.
- No benchmark covering Zig or graphics/shader code was found (search budget ran out; see open).
- OpenUSD v26.11.1 (2026-10-21), 7.6k★, "Tomorrow Open Source Technology License 1.0" (Apache 2.0 with a different trademark section) — GitHub API; LICENSE.txt page read.
- Rust USD: mxpv/openusd "Native Rust USD library" 151★ (push 2026-10-29); FloatyMonkey/openusd-rs 37★; AndrejOrsula/pxr_rs 14★ — GitHub search API 2026-10-29.
- C# USD: Unity-Technologies/usd-unity-sdk last push 2024-11-25, release 3.0.0-exp.5 (2023); com.unity.usd-toolkit 47★ (Unity integration) — GitHub API / search API.
- Physics: Jolt v5.6.0 (MIT, 11.8k★); PhysX BSD-3 (4.8k★, release ovphysx-0.7.0 2026-10-15); Rapier (Apache-2.0, 6.0k★); BepuPhysics2 (Apache-2.0, 3.0k★); physx-rs **archived**; JoltPhysicsSharp (MIT, 0.4k★) — GitHub API.
- FBX/glTF: ufbx (MIT or public domain, 1.4k★, tag v0.23.1); cgltf (MIT, 2.0k★); fastgltf (MIT, 0.6k★, v0.9.1 2026-09-27); gltf crate (Rust, last release 1.0.0 2022); SharpGLTF (C#, MIT, v1.0.7 2026-09-12) — GitHub API; ufbx LICENSE page read.
- Mesh processing: meshoptimizer (MIT, v1.3 2026-09-25); Manifold (Apache-2.0, v3.5.4); libigl (both LICENSE.MPL2 and LICENSE.GPL in repo); CGAL (GitHub licence field NOASSERTION) — GitHub API; libigl file listing page read.
- Zig: GitHub repo "Moved to Codeberg … This repository is not mirrored"; last GitHub release 0.15.1 (2025-08-29) — README page read; GitHub API.
- .NET: dotnet/runtime v10.0.13 (2026-10-13) — GitHub API.
- Assessment: **engine core: C++** (every library a CC5-class app needs is native C++ with C++ examples; every reference DCC is C++). **Rust** is credible for core and UI (wgpu, egui, PyO3, wasmtime are first-class) and scores best for AI agents in one benchmark, but USD, FBX and production physics bindings are thin or archived — each would be a bindings project of ours. **C#** has a clean UI story (Avalonia) but the weakest agent evidence of the three and a thin 3D-library base. **Python** is the scripting/plugin layer on any route. Evidence on AI-agent quality per language is too thin and too old (2025 models, generic repos) to decide the core language on its own.

### Q5 · Scripting and plugin embedding

- nanobind: "~4× faster compile time, ~5× smaller binaries, and ~10× lower runtime overheads compared to pybind11"; "can target the Python Stable ABI" — https://github.com/wjakob/nanobind, page read.
- pybind11 3.0.0 (2025-07-10): "includes an ABI bump, the first required bump in many years on Unix … smart-holder branch, multi-phase init and subinterpreter support" — release notes page read.
- PyO3: supports CPython 3.9+, PyPy 7.3, GraalPy 25.4+; "to embed Python in a Rust binary … your Python installation contains a shared library" — README page read.
- PEP 779 accepted (Final, 2025-06-16): free-threaded 3.14 no longer experimental; ≤10 % performance target; Stable ABI for free-threading expected for 3.15 — search snippet only.
- .NET hosting: via `nethost` + `hostfxr`; "Only one runtime can be loaded inside a single process"; hosting APIs "only support framework-dependent deployments" — MS Learn (updated 2026-08-10), page read.
- GDExtension compatibility: "GDExtensions targeting an earlier version of Godot should work in later minor versions, but not vice-versa" — https://github.com/godotengine/godot-cpp, page read.
- Carbonite plugins are "separate shared libraries with C-style interfaces that can be loaded and unloaded" — Kit overview, page read.
- wasmtime embeddings supported by the Bytecode Alliance: C++ (`wasmtime.hh`), Python, .NET, Ruby (plus Rust/C) — README page read.
- WASI 0.3.0 released 2026-06-11: async func, stream<T>, future<T> in the component model; Wasmtime 46.0.0 (2026-06-22) enables it by default — wasi.dev / bytecodealliance.org, search snippet only.
- Extism host SDKs: Rust, JS (Web/Node/Deno/Bun), Elixir, Go, Haskell, Java, .NET, OCaml, Perl, PHP, Python… — README page read.
- Zed editor extensions: Rust → Wasm components run on Wasmtime with WIT interfaces — plushcap.com summary of a zed.dev blog, search snippet only.
- Lua 5.5.1 tagged release 2026-08-05 (lua/lua mirror); Wicked Engine has Lua scripting — GitHub API; features.txt page read.
- Assessment: the industry standard for a DCC's user-facing API is **embedded CPython** (Blender, Maya, Houdini, C4D, Kit, Cascadeur, iClone, MD). For C++ the modern binding is **nanobind** (Stable ABI = one wheel per platform across Python versions); for Rust, **PyO3**. Native plugins need a **stable C ABI** (GDExtension/Carbonite/OpenFX pattern). **Wasm (wasmtime components)** is the only option with a real sandbox, now with async (WASI 0.3), but no DCC precedent was found and it cannot touch the GPU — fits untrusted, data-only plugins (importers, generators, rules), not render or sim plugins. Lua and .NET add a second scripting language without a DCC precedent among the references (Maya's .NET aside).

### Q6 · How AI agents can test a 3D app

- Filament renderdiff: headless renders compared to golden references "mainly useful for continuous integration where GPUs are generally not available"; desktop on Mesa's software rasterizers (opengl, vulkan, webgpu); web in headless Chromium on SwiftShader; goldens per platform; reproducibility pinned by browser build, rasterizer and render size — README page read.
- Bevy CI: examples run with `CI_TESTING_CONFIG`, screenshots saved and sent to Pixel Eagle; Linux job installs `mesa-vulkan-drivers` and runs under `xvfb-run`; "also run when pushed to main to update reference screenshots" — example-run.yml page read.
- wgpu: "The FLIP library generates a per-pixel error map"; tests fail "If the given percentile is greater than the given value" — tests/src/image.rs page read.
- Blender: `render_report.py` "Compare renders or screenshots against reference versions"; uses `oiiotool` with `--fail` and `--failpercent`; update mode rewrites references — page read.
- Godot `tests/` holds doctest unit tests with a `display_server_mock`; no golden-image render suite seen in the folder listing — GitHub page read (absence not proven).
- WARP: "fully conformant software rasterizer"; D3D12 FL 12_0/12_1 since Windows 10 1709, 12_2 in preview; HLSL compiler covers "raytracing shader stages"; NuGet DLLs "cannot be redistributed" — MS Learn (updated 2025-07-24), page read.
- egui_kittest: "Ui testing library for egui, based on kittest (an AccessKit based testing library)"; `harness.get_by_label(...)`, `.click()`, `harness.run()` — README page read.
- Avalonia headless: "runs Avalonia without a visible window, making it ideal for automated testing in CI/CD"; `CaptureRenderedFrame` with the Skia renderer to compare against baselines; simulated input — docs (updated 2026-10-09), page read.
- Bevy Remote Protocol: "allow for remote control of a Bevy app … based on the JSON-RPC 2.0 protocol"; HTTP transport plugin — bevy_remote lib.rs page read.
- Blender Lab MCP server: Blender 5.1+, add-on 1.0.3, executes LLM code "without any guards"; recommends a VM — blender.org/lab/mcp-server, page read.
- Unreal 5.8 experimental MCP plugin: local HTTP/SSE server at 127.0.0.1:8000/mcp, no auth, serial tool calls on the game thread — a2a-mcp.org directory + unrealengine.com news, search snippet only.
- Unity AI MCP open beta (2026-05-11): needs Unity 6, AI Assistant package and a Unity AI trial/subscription — gamedev.net, search snippet only.
- Godot Movie Maker: non-real-time recording with "perfect frame pacing"; `--write-movie`, `--fixed-fps`, `--quit-after`; PNG-sequence output — Godot 4.7 docs page read.
- RenderDoc: Vulkan, D3D11, D3D12, OpenGL, GLES on Windows/Linux/Android; Metal N/A — README page read.
- Assessment (applies to every route): (1) **render goldens** on CPU rasterizers in CI — lavapipe/llvmpipe for Vulkan (Linux), WARP for D3D12 (Windows), with a perceptual metric (FLIP) and per-test thresholds; macOS/Metal has no CPU rasterizer found, so Apple runs need a GPU runner. (2) **a JSON-RPC/MCP control channel** into the command registry (Bevy's BRP is the cleanest precedent; MCP is where Blender, Unreal and Unity are converging). (3) **UI tests through the accessibility tree** (AccessKit/kittest, Avalonia.Headless, Qt's platform accessibility) — Dear ImGui lacks this. (4) **fixed-step deterministic replay** of a command log with frame dumps (Godot Movie Maker pattern). These choices favour toolkits with an accessibility tree and renderers with a Vulkan or D3D12 backend that runs on a CPU rasterizer.

---

## Effort evidence

- **Blender:** first source 1994-01-02; open source 2002; UI rewrite (2.5) began early 2008; 2.8 UI overhaul shipped July 2019; ~28 employees today — blender.org/about/history (page read). GitHub mirror: 166,956 commits on `main`, 1,596 contributors (anonymous included) — GitHub API 2026-10-29.
- **Godot:** "several years as an in-house engine" before open-sourcing in February 2014 (README, page read); 87,441 commits on `master`, 3,990 contributors (anon. incl.), 119k★ — GitHub API.
- **Bevy:** repo created 2020-01-18; 12,509 commits, 1,706 contributors, 49.4k★; latest v0.20.1 (2026-10-28, pre-1.0). Editor: `bevy_editor_prototypes` archived ("Bevy is still actively working on an Editor … Foundational work continues"), last push 2026-04-14 — GitHub API + README page read.
- **Fyrox** ("production-ready … game engine written in Rust with a scene editor"): created 2019-03-30, v1.0.0 2026-03-29; 8,556 commits, of which mrDIMAS 7,805 (~91 %); 99 contributors — GitHub API + README.
- **Wicked Engine** (engine + Editor): created 2015-06-20; 5,216 commits, turanszkij 4,633 (~89 %); 68 contributors — GitHub API.
- **Flax Engine** (C++/C# engine + editor): GitHub since 2020-12; top contributor mafiesto4 10,932 commits; 109 contributors — GitHub API.
- **Omniverse Kit, Unreal, Maya, Houdini:** no public effort figures found.
- **OpenHub cost estimates** (COCOMO) for Blender/Godot: openhub.net refused scripted access (403) — not used.
- Assessment: every editor in this list took **many years** — Godot "several years" in-house plus 12+ years open, with thousands of contributors; Blender's UI rewrite alone ran 2008→2019 through two rewrites; Bevy, with 1,700 contributors and six years, has not shipped an editor. The single-developer engines (Wicked, Fyrox) show one very focused person can reach an engine + editor in 7–11 years, but neither has CC5-level character tools. With AI agents writing every line, line cost falls, but the integration and testing depth (render goldens, UI tests, control channel) becomes the limit — which argues for buying every layer that exists (RHI, physics, USD, UI toolkit, scripting) and writing only the character-specific parts (skin, hair, eyes, morph/rig systems, timeline, the command model).

---

## Overall assessment (judgement only — for the lead to weigh against the existing-engine route)

- **Strongest C++ own-engine stack found:** C++ core + an RHI with native D3D12/Vulkan/Metal and RT (The Forge, or Wicked Engine taken as a whole; Diligent if macOS-on-MoltenVK-without-RT is acceptable) + **Qt Widgets (LGPL-3)** editor with Qt-ADS docking, QtNodes, a QRhiWidget/native-window viewport, our own timeline + **CPython via nanobind** for the user API + a stable C ABI for native plugins + wasmtime for sandboxed data plugins + OpenUSD/ufbx/Jolt/PhysX/ozz from C++ directly. Matches how Maya, Houdini, Daz Studio and iClone are built.
- **Strongest Rust own-engine stack found:** wgpu + egui (egui_dock/egui_tiles, egui-snarl, kittest) + PyO3 + wasmtime. Best AI-testability and safety; weakest 3D ecosystem (USD/FBX/physics bindings would be ours) and no RT on Metal/D3D12 in wgpu yet. PhotoCraft (§11) chose this stack for a 2D app.
- The attack on these: no DCC of CC5's kind ships on Rust or egui; Qt's LGPL means dynamic linking, shipping Qt's source offer and avoiding its GPL-only modules; Dear ImGui would be faster to build but fails the accessibility/AI-test criterion; every route still writes skin, hair and eyes itself.

---

## Couldn't verify / open

- **Web-search budget ran out** mid-research (session-wide limit). Not checked as a result: GTK 4 and Flutter desktop details; Slint docking/accessibility; wxAUI; Qt Test / Squish for UI automation; Rust vs C++ build-time evidence; Mesa lavapipe conformance (docs URL 404); Microsoft Flight Simulator or other DCCs using Wasm plugins; Unreal's Python scripting; Godot C# hosting details.
- **Refused scripted access (403):** developer.blender.org and docs.blender.org (Blender Vulkan default and Python-embedding docs taken from search snippets and the GitHub mirror instead); unrealengine.com news; openhub.net.
- **Search-snippet-only facts** (marked above): Cascadeur, Marvelous Designer, Cinema 4D, Unreal Slate, CC5 RLPy, Unreal 5.8 MCP, Unity MCP, Multi-SWE-bench, SWE-Sharp-Bench, PEP 779, WASI 0.3, Avalonia 12 accessibility, Slint wgpu underlay, Dear ImGui 1.92 DPI.
- **CC5 / iClone UI toolkit** is not public; Qt is inferred from the Python API (Qt 5.15.2/PySide2, dock widgets wrappable as Qt widgets).
- **Cascadeur's and Marvelous Designer's UI toolkits and core language:** no public source found.
- **Diligent's ray tracing on Metal**, The Forge's ray tracing on Metal, and Wicked's Metal RT were not checked per backend.
- **RTXCR fallback** on GPUs without LSS hardware (our RTX 2070 Super) is not stated in the README beyond "RTX 20 series or newer".
- **AI-agent evidence per language** is from 2025 models on generic repos; no 2026 per-language result and no graphics-specific benchmark was found.
- GitHub licence fields marked NOASSERTION (ozz-animation, assimp, CGAL, Magnum, Ogre-Next, mitsuba3, glm) were only read where noted; others need their licence files read before use.
- No public effort figures (team size, years) for Maya, Houdini, Unreal's editor, Omniverse, CC5 or iClone.
