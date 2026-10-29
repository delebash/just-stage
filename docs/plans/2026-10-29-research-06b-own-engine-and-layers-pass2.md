# Research 06b, pass 2 — Own engine and layers: the gaps round one left open

Research agent notes, 2026-10-29. Second pass for section S6 of
[`2026-10-29-research-second-pass.md`](2026-10-29-research-second-pass.md); round one is
[`2026-10-29-research-06b-own-engine-and-layers.md`](2026-10-29-research-06b-own-engine-and-layers.md). Scope rules as
there (Omniverse, Unity and paid-only parts out; core parts must run on more than one GPU vendor; licences one line
each; clean-room).

**How to read the labels.** *page read* = I read the page myself. *source read* = I read the file in the project's
repository (GitHub's signed API or the project's own GitLab raw URL) on 2026-10-29. *GitHub API* = repository
metadata on 2026-10-29 (stars, last push, latest release, licence field). *search snippet only* = a search
engine's summary; the page itself was not opened, or it refused scripted access. "Assessment:" lines are my
judgement and are kept apart from the facts. About 60 web searches were used; the rest was read from pages and
sources.

---

## Top findings

1. **Hardware ray tracing on Metal, per library:** The Forge does it (ray queries on macOS through
   `MetalRaytracing.mm`; its README shows the ray-query test on an M2 Mac). Wicked Engine's Metal backend is Metal 4
   only, builds acceleration structures and sets its `RAYTRACING` capability when the device supports it, but
   ray-tracing *pipelines* (`CreateRaytracingPipelineState`, `DispatchRays`) are `// TODO` — inline ray queries
   only. Metal 4 needs "Mac with Apple silicon" and "macOS Tahoe 26 or later". Diligent's native Metal backend is
   still "Available under commercial license", and its free macOS path (MoltenVK) has no ray tracing: MoltenVK's
   ray-tracing support is an open, opt-in work-in-progress pull request (#2771). wgpu's ray query is still
   "Supported platforms: Vulkan" only. — [Forge README + MetalRaytracing.mm](https://github.com/ConfettiFX/The-Forge),
   [Wicked wiGraphicsDevice_Metal.cpp](https://github.com/turanszkij/WickedEngine/blob/master/WickedEngine/wiGraphicsDevice_Metal.cpp),
   [Apple: Metal support](https://support.apple.com/102894), [Diligent README](https://github.com/DiligentGraphics/DiligentEngine),
   [MoltenVK PR #2771](https://github.com/KhronosGroup/MoltenVK/pull/2771), [wgpu features.rs](https://github.com/gfx-rs/wgpu/blob/trunk/wgpu-types/src/features.rs)
2. **Headless render tests work on all three OSes.** Mesa's lavapipe (CPU Vulkan) on `main` exposes Vulkan 1.4
   with `VK_KHR_acceleration_structure`, `VK_KHR_ray_query` and `VK_KHR_ray_tracing_pipeline`; Khronos formally
   recognised it as a Vulkan 1.3 implementation in July 2022, and it reports conformance version 1.3.1.1. wgpu's
   CI runs its GPU tests on lavapipe (Mesa 26.1.3) on **both Linux and Windows**, plus WARP on Windows. Metal has
   no software fallback (CircleCI, 2026-05-14), but GitHub's standard `macos-14` runner does run Metal: Bevy's
   `run-examples-macos-metal` screenshot job and wgpu's "Mac aarch64" tests use it.
   — [lvp_device.c](https://gitlab.freedesktop.org/mesa/mesa/-/blob/main/src/gallium/frontends/lavapipe/lvp_device.c),
   [Phoronix 2022-07-20](https://www.phoronix.com/news/Lavapipe-Vulkan-1.3-Official), [wgpu ci.yml](https://github.com/gfx-rs/wgpu/blob/trunk/.github/workflows/ci.yml),
   [Bevy example-run.yml](https://github.com/bevyengine/bevy/blob/main/.github/workflows/example-run.yml),
   [CircleCI support](https://support.circleci.com/hc/en-us/articles/360052160592-Tests-Fail-With-Error-There-is-no-available-Metal-device-on-this-system)
3. **How an AI agent drives a Qt app, all free:** Qt's own accessibility backends are in qtbase (Windows UI
   Automation, macOS NSAccessibility, Linux AT-SPI), so out-of-process drivers work: pywinauto (`backend="uia"`,
   BSD-3), Appium Mac2 driver (XCTest, Apache-2.0), AT-SPI on Linux. In-process: QTest event simulation and
   `-platform offscreen` ("only fully supported on X11"); PySide6 exposes `QTest` and `QSignalSpy` to Python;
   pytest-qt (MIT). Embedded remote control: Spix (MIT; Qt Quick and, Qt 6 only, Qt Widgets; HTTP RPC; screenshots).
   Squish is subscription-only (out). — [qtbase](https://github.com/qt/qtbase/tree/dev/src/plugins/platforms/windows/uiautomation),
   [Qt Test overview 6.12](https://doc.qt.io/qt-6/qtest-overview.html), [Spix](https://github.com/faaxm/spix), [pywinauto](https://github.com/pywinauto/pywinauto)
4. **Unreal 5.8's MCP server, now from Epic's page:** experimental; HTTP + SSE at `127.0.0.1:8000/mcp`; "no
   authentication layer"; tool calls run "on the game thread serially"; toolsets in C++ or Python (most shipped ones
   are Python); cooked and shipping builds *can* host an MCP server, but the toolset registry is editor-only.
   Unreal's Python is editor-only ("you cannot currently use it as a gameplay scripting language"), Python 3.11.8.
   — [Unreal MCP in Unreal Editor (5.8)](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor?lang=en-US),
   [Scripting the Unreal Editor Using Python (5.8)](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)
5. **WebAssembly plugins in big apps:** Microsoft Flight Simulator replaced DLL add-ons with Wasm "to provide both
   security and portability" (compiled ahead of time; each module single-threaded; no C++ exceptions, C++ threads or
   Windows API; read-only access to its own package). Developers' complaints: no libraries, no exceptions, no files
   outside the package; Asobo says multithreading "has proven technically hard". Figma moved its plugin sandbox to
   QuickJS compiled to Wasm in 2019 after sandbox escapes in the Realms shim ("somewhat slower … intrinsically more
   secure"). Zed uses Wasm components with WIT and a versioned API, but extensions can't add UI panels. Helm 4 ships
   Extism (Wasm) plugins beside subprocess plugins. No 3D content-creation app with Wasm plugins was found.
   — [MSFS 2024 WebAssembly](https://docs.flightsimulator.com/msfs2024/retail/programming-apis/wasm/webassembly/index.md),
   [MSFS dev forum, 2024-11](https://devsupport.flightsimulator.com/t/dll-vs-wasm-modules/10658),
   [Figma update 2019-10-02](https://madebyevan.com/figma/an-update-on-plugin-security/), [Zed blog 2024-10-21](https://zed.dev/blog/zed-decoded-extensions),
   [Helm go.mod](https://github.com/helm/helm/blob/main/go.mod)
6. **GPU from inside a Wasm plugin is not standard yet:** `wasi:webgpu` (wasi-gfx) is a Phase 2 proposal.
   WASI 0.3.0 (native async) is confirmed released 2026-06-11; Wasmtime 46 (2026-06-22) enables it by default.
   — [wasi-gfx README](https://github.com/WebAssembly/wasi-gfx), [WASI 0.3](https://wasi.dev/releases/wasi-p3)
7. **Flutter desktop for a 3D editor:** multi-window is still experimental ("Do not use windowing APIs in
   production"; main channel plus a feature flag; issue #30701 open); Flutter GPU is "in an early preview state and
   does not guarantee API stability"; Impeller became the default on Windows, macOS and Linux in 3.47 (backends:
   Metal, Vulkan, GLES — no D3D). Precedent: Flutter Scene (MIT, 1.0k★, by the author of Flutter GPU) has a desktop
   scene editor with an MCP server, "in active development". Docking comes only from small third-party packages.
   — [Flutter _window.dart](https://github.com/flutter/flutter/blob/master/packages/flutter/lib/src/widgets/_window.dart),
   [Flutter-GPU.md](https://github.com/flutter/flutter/blob/master/docs/engine/impeller/Flutter-GPU.md),
   [Impeller docs (3.47)](https://docs.flutter.dev/perf/impeller), [flutter_scene](https://github.com/bdero/flutter_scene)
8. **GTK 4 for a 3D editor:** no Vulkan widget (`GtkGLArea` is OpenGL only); the GTK maintainer's advice is to
   render offscreen and hand GTK a dmabuf-backed `GdkTexture` (dmabuf is Linux). Accessibility on Windows and macOS
   exists only through the AccessKit backend added in 4.18, and on GTK `main` (4.25.0) that build option still
   defaults to `disabled`. Docking comes from libpanel (LGPL-3, built for GNOME Builder). The only 3D tools on GTK
   found are old (K-3D, Kudu, gSculpt). — [GtkGLArea 4.24](https://docs.gtk.org/gtk4/class.GLArea.html),
   [GNOME Discourse 2025-06-17](https://discourse.gnome.org/t/python-creating-vulkan-surface-on-gtk-paned/29429),
   [GTK blog 2025-05-12](https://blog.gtk.org/2025/05/12/an-accessibility-update/), [GTK meson.options](https://gitlab.gnome.org/GNOME/gtk/-/blob/main/meson.options)
9. **Slint:** AccessKit accessibility is on by default (Cargo `default` includes `accessibility`); there is no
   docking widget (issue "Docking widgets" #1723, open since 2022-10-10); the wgpu underlay is real but sits behind
   `unstable-wgpu-29/30` flags that "may be removed or changed in future minor releases".
   — [slint Cargo.toml + lib.rs](https://github.com/slint-ui/slint/tree/master/api/rs/slint), [issue #1723](https://github.com/slint-ui/slint/issues/1723)
10. **wxWidgets:** wxAUI docks panes to the four edges or centre, floats them, and saves and restores layouts as
    "perspectives"; `wxAccessible` (for custom controls) is Windows-only (MSAA). A shipped 3D app on wxWidgets:
    PrusaSlicer (AGPL-3.0, 9.4k★) with an OpenGL viewport. — [wxAuiManager 3.2.13](https://docs.wxwidgets.org/stable/classwx_aui_manager.html),
    [wxAccessible](https://docs.wxwidgets.org/stable/classwx_accessible.html), [PrusaSlicer deps](https://github.com/prusa3d/PrusaSlicer/tree/master/deps)
11. **Build time, Rust vs C++:** no controlled comparison of large codebases exists that I could find. Rust's own
    2025 survey (3,700+ answers): average satisfaction 6/10; 55% wait more than 10 s for a rebuild after a small
    change; 45% of people who left Rust name compile times. Rust's 2026 roadmap says CI clean builds take "30+
    minutes" for medium-sized projects. A small ported benchmark (9.3k lines) found Rust's build time growing much
    faster than C++'s as the source grew. — [Rust survey results 2025-09-10](https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results),
    [Rust 2026 fast-builds roadmap](https://goals.rust-lang.org/2026/roadmap-fast-builds.html), [Shape of Code 2023-01-29](https://shape-of-code.com/2023/01/29/a-comparison-of-c-and-rust-compiler-performance/)
12. **Code-quality evidence on Rust vs C++ (Google, Android, 2025-11-13):** Rust changes have a "~4x lower" rollback
    rate than C++, spend about 25% less time in code review, and need about 20% fewer revisions; memory-safety bugs
    run about 0.2 per million lines in Rust against roughly 1,000 in C/C++. This concerns human teams, not AI
    agents. — [Google blog](https://blog.google/security/rust-in-android-move-fast-fix-things/)
13. **The seven NOASSERTION licences, read:** ozz-animation MIT; assimp BSD-3-Clause (its test models are an
    exception); CGAL GPL-3+ or LGPL-3+ per file (commercial licence from GeometryFactory); Magnum MIT; Ogre-Next MIT;
    mitsuba3 BSD-3-Clause plus an "Enhancements" grant-back clause; glm "Happy Bunny" or MIT. — licence files, source read
14. **Corrections to round one's snippet-only facts:** PEP 779 sets a 15% "hard performance target" and a 20% memory
    target, and the Stable ABI stays an open question — round one's "≤10%, ≤15–20%, Stable ABI in 3.15" was wrong.
    The Cinema 4D "PySide6 importable since 2024.2" claim comes from a user, not Maxon staff. Marvelous Designer's
    2026.1 changelog mentions a headless mode, which contradicts the older support answer "no headless".
    — [PEP 779](https://peps.python.org/pep-0779/), [Maxon forum](https://developers.maxon.net/forum/post/75688), [MD changelog](https://developer.marvelousdesigner.com/changelog.html)
15. **How the reference apps are built, and the effort:** Cascadeur's GUI was converted to Qt's QML in 2020, with
    Python 3.8 scripting; Marvelous Designer's toolkit isn't public (staff said Qt 5, snippet only); Maya 1.0
    (February 1998) was built on four earlier codebases and has used a Qt UI since Maya 2011. No public team sizes
    exist for Maya, Houdini or Unreal's editor. Blender's Development Fund takes in $326,118 a month from 7,611
    individual and 46 corporate members, and Blender paid developers €2.15M in 2024.
    — [Game World Observer 2020-07-29](https://gameworldobserver.com/2020/07/29/nekki-launches-cascadeur-open-beta),
    [Wikipedia: Autodesk Maya](https://en.wikipedia.org/wiki/Autodesk_Maya), [fund.blender.org](https://fund.blender.org/),
    [CGPress 2025-09-16](https://cgpress.org/archives/blender-foundation-reports-higher-donations-but-warns-of-low-reserves-in-2024-annual-report.html)

---

## G1 · UI toolkits not checked in round one: GTK 4, Flutter desktop, Slint docking and accessibility, wxAUI

### GTK 4

- `GtkGLArea` "Allows drawing with OpenGL"; OpenGL ES is a deprecated option (since 4.12); Vulkan isn't mentioned —
  https://docs.gtk.org/gtk4/class.GLArea.html (GTK 4.24.1 docs, gi-docgen 2026.1), page read.
- GTK accessibility docs list "AT-SPI on Linux/BSD", "NSAccessibility on macOS", "Active Accessibility on
  Windows", plus a test backend for GTK's own CI — https://docs.gtk.org/gtk4/section-accessibility.html (4.24.1),
  page read.
- "We merged the AccessKit a11y backend in GTK 4.18. For the very first time, GTK applications can be accessible on
  Windows and macOS"; enabled by the build option `-Daccesskit=enabled` plus `GTK_A11Y=accesskit`; Linux still
  defaults to AT-SPI; "the first rust dependency in GTK" — https://blog.gtk.org/2025/05/12/an-accessibility-update/
  (2025-05-12), page read.
- GTK `main` (version 4.25.0): `option('accesskit', type: 'feature', value: 'disabled', …)` —
  https://gitlab.gnome.org/GNOME/gtk/-/raw/main/meson.options and meson.build, source read.
- An October 2024 forum post (before 4.18): "There's currently no accessibility support on Windows and macOS" —
  discourse.gnome.org, search snippet only.
- No Vulkan widget in GTK: GTK's maintainer Emmanuele Bassi, 2019-12-06: "you don't have access to the Vulkan
  pipeline from outside GTK itself" — https://discourse.gnome.org/t/gtk4-gsk-vulkan-for-drawing-area-kotlin/2293,
  page read.
- His advice, 2025-06-17: "create an offscreen buffer, render to it, and then extract the backing buffer", wrapped
  as a dmabuf `GdkTexture` and drawn with `GtkSnapshot` in a custom widget; "look at how `GtkGLArea` is implemented"
  — https://discourse.gnome.org/t/python-creating-vulkan-surface-on-gtk-paned/29429, page read.
- An openSUSE Hack Week project prototyped a "GtkVulkanArea"; no sign it was adopted upstream —
  hackweek.opensuse.org, search snippet only.
- libpanel: "helps you create IDE-like applications using GTK 4 and libadwaita … panels, docks, columns and grids of
  pages … focus around GNOME Builder and Drafting" — https://gitlab.gnome.org/GNOME/libpanel README, source read;
  LGPL-3 (COPYING head read); 1.10.4 packaged by Arch in February 2026 — archlinux.org, search snippet only.
- 3D tools found on GTK: K-3D (gtkmm, 2006 mailing-list post), Kudu Animator (GTK+ and OpenGL), gSculpt — all old
  projects; no current 3D content-creation app on GTK 4 found — sourceforge / lists.gnome.org, search snippet only.
- Licence: GTK is LGPL-2.1-or-later (round one, not re-read) — commercial use: conditional (LGPL).
- Assessment: GTK 4 is a weak fit — no native 3D viewport path outside Linux (dmabuf), accessibility outside Linux
  is opt-in at build time and new, and no current 3D app uses it.

### Flutter desktop

- Flutter's windowing source, on both the `master` and `stable` branches: "Windowing APIs are currently experimental.
  Do not use windowing APIs in production applications or plugins published to pub.dev. To try … Switch to Flutter's
  main release channel. Turn on the windowing feature flag." — https://github.com/flutter/flutter/blob/master/packages/flutter/lib/src/widgets/_window.dart,
  source read (stable branch at `flutter-3.47-candidate.0`, commit 2026-10-23).
- Issue #30701 "Support multiple windows for desktop shells": open, 149 comments, updated 2026-09-05 — GitHub API.
- A third-party blog (2026-08) says stable Flutter has no public multi-window API and suggests the
  `desktop_multi_window` plugin (separate engines and isolates) — startdebugging.net, search snippet only.
- Impeller "available and enabled by default as of Flutter 3.47" on macOS, Linux and Windows; "In a future release,
  the ability to opt out of using Impeller will be removed" — https://docs.flutter.dev/perf/impeller (3.47), page read.
- Impeller's backend folders are `gles`, `metal`, `vulkan` (no D3D) — flutter/flutter `engine/src/flutter/impeller/renderer/backend`, GitHub API.
- Flutter GPU: "in an early preview state and does not guarantee API stability"; requires Impeller; shader building
  "relies on the experimental Dart 'Native Assets' feature"; "switching to the master channel is strongly
  recommended" — https://github.com/flutter/flutter/blob/master/docs/engine/impeller/Flutter-GPU.md, source read.
- Flutter Scene: "A complete 3D game engine for Flutter, built on Flutter GPU" with "a desktop scene editor with an
  MCP server for agent-driven editing"; the editor stack (headless command core, Flutter UI, MCP tools) is "In active
  development"; macOS, Windows, Linux supported (Windows/Linux releases need Flutter 3.47.1); visual tests on Argos;
  MIT; 1,006★; created 2024-02-01; top contributor bdero 1,875 commits, next 18 —
  https://github.com/bdero/flutter_scene README, source read; GitHub API.
- Native textures on Windows: the embedder's texture registrar accepts a DXGI shared handle or a D3D11 `Texture2D`
  as a GPU surface — flutter engine `flutter_texture_registrar.h`, search snippet only.
- Desktop screen readers named in Flutter's docs: Narrator/NVDA (Windows), VoiceOver (macOS), Orca (Linux); no
  per-platform limits stated — https://docs.flutter.dev/ui/accessibility/assistive-technologies (updated 2026-09-29), page read.
- Docking: `dock_panel` 0.1.1 (dock tabs left/right/top/bottom, saved layouts) and `fl_panel` 1.1.0 (its docs list
  floating panels and multi-window hosting as not built yet) — pub.dev, search snippet only.
- Licence: Flutter BSD-3-Clause (round one) — commercial use: yes.
- Assessment: Flutter can host a 3D view and has a live agent-driven 3D editor precedent, but floating panels need
  multi-window, which is experimental, and its own GPU layer is an early preview. A pro editor on it today means
  building docking and taking pre-release pieces.

### Slint

- Default Cargo features include `"accessibility"` — "expose the tree of UI elements to OS provided accessibility
  APIs to support screen readers" — https://github.com/slint-ui/slint/blob/master/api/rs/slint/Cargo.toml, source read.
- Its winit backend's `accessibility` feature pulls in `accesskit` 0.25 and `accesskit_winit` 0.34 (AT-SPI through
  zbus on Linux); a backend file `accesskit.rs` exists — internal/backends/winit/Cargo.toml, source read.
- Older docs (2022) routed accessibility through Qt's code; Slint 1.6 (2024-05-13) added accessibility actions —
  slint.dev blog, search snippet only (superseded by the source above).
- Docking: no dock widget among the std widgets (`internal/compiler/widgets/common`: combobox, tabwidget, menus,
  listview… no dock) — source read. Issue #1723 "Docking widgets" is open since 2022-10-10 — GitHub API.
- wgpu integration: use the same `wgpu::Device` and `Queue` as Slint; render an underlay or overlay through
  `Window::set_rendering_notifier()`, or show your own `wgpu::Texture` as a `slint::Image`; modules `wgpu_29` (for
  "bevy 0.19") and `wgpu_30` are "behind a feature flag and may be removed or changed in future minor releases" —
  https://github.com/slint-ui/slint/blob/master/api/rs/slint/lib.rs (1.19 in development), source read.
- Latest release v1.18.1, 2026-09-21 — GitHub API.
- Licence: GPL-3 or Royalty-free 2.0 or paid (round one) — commercial use: yes under the royalty-free licence (with attribution).
- Assessment: Slint's accessibility is now as good as egui's (both AccessKit), but docking would be ours to build.

### wxWidgets / wxAUI

- wxAUI: frame management to "open, move, and hide controls" and save configurations as perspectives; native
  floating frames; toolbars with chevrons and user customisation — https://docs.wxwidgets.org/stable/overview_aui.html (3.2.13), page read.
- `wxAuiManager`: panes dock Top, Bottom, Left, Right or Center, in rows and layers; `wxAUI_MGR_ALLOW_FLOATING`
  floats a pane into a `wxMiniFrame`; `SavePerspective()` / `LoadPerspective()` save the layout as a string; new docks
  limited to 1/3 of the window by default — https://docs.wxwidgets.org/stable/classwx_aui_manager.html (3.2.13), page read.
- `wxAccessible` is "only available for the wxMSW port" and "only Microsoft Active Accessibility is supported" —
  https://docs.wxwidgets.org/stable/classwx_accessible.html (3.2.13), page read. Native controls carry each OS's own
  accessibility (inference from "native controls"; not tested).
- PrusaSlicer's dependency list includes wxWidgets, GLEW, GLFW, OpenVDB, CGAL, OCCT; AGPL-3.0, 9,445★, last push
  2026-09-21 — https://github.com/prusa3d/PrusaSlicer/tree/master/deps, GitHub API.
- Licence: wxWindows Licence (LGPL with exception, round one) — commercial use: yes.
- Assessment: wxAUI covers docking and saved layouts; a 3D viewport is proven (PrusaSlicer, OpenGL). Weak points:
  custom widgets are accessible only on Windows, and no character or animation tool uses it.

## G2 · UI test automation for Qt — how an AI agent drives a Qt app

- Qt's platform accessibility code in qtbase: `src/plugins/platforms/windows/uiautomation/qwindowsuiaaccessibility.cpp`
  (UI Automation), `src/plugins/platforms/cocoa/qcocoaaccessibility.mm` (NSAccessibility),
  `src/gui/accessible/linux/atspiadaptor.cpp` (AT-SPI) — https://github.com/qt/qtbase, source read.
- Qt Test: "functionality for mouse and keyboard simulation"; data-driven tests; benchmarks; `-vs` traces signals;
  "By using the 'offscreen' platform plugin (-platform offscreen) it's possible to have tests that use QWidget or
  QWindow run without showing anything on the screen. Currently the offscreen platform plugin is only fully supported
  on X11." — https://doc.qt.io/qt-6/qtest-overview.html (Qt 6.12), page read.
- Keyboard focus can fail under `offscreen` (a 2019 forum report) — forum.qt.io, search snippet only.
- PySide6 exposes `QTest`, `QSignalSpy`, `QAbstractItemModelTester` and `QTouchEventSequence` to Python —
  https://github.com/pyside/pyside-setup `sources/pyside6/PySide6/QtTest/typesystem_test.xml`, source read.
- pytest-qt: MIT, 456★, last push 2026-10-27 — GitHub API.
- Spix: "UI test automation library for QtQuick/QML/QtWidgets Apps"; control "via c++ code, or through an http RPC
  interface"; `Spix::QtWidgets` is "Qt6 only" and off by default; needs AnyRPC; actions include mouse, text entry,
  property reads, screenshots — https://github.com/faaxm/spix README, source read; MIT, 275★, last push 2026-08-19 — GitHub API.
- KDAB wrote about Spix for GUI automation in February 2026 — planet.kde.org, search snippet only.
- pywinauto: "Win32 API (backend='win32') … MS UI Automation (backend='uia')"; BSD-3; 6,308★; last release 0.6.9
  (2025-01-06), last push 2026-10-28 — https://github.com/pywinauto/pywinauto README, source read; GitHub API.
- FlaUI (.NET UI Automation): MIT, 3,187★, last push 2026-08-13 — GitHub API.
- Appium Mac2 driver: "automating macOS applications using Apple's XCTest framework"; Apache-2.0; 189★; last push
  2026-10-29 — https://github.com/appium/appium-mac2-driver, source read; GitHub API.
- GammaRay ("poke around in a Qt-application and also … manipulate the application"): GPL-2.0-or-later or
  commercial from KDAB; 1,923★ — README source read; GitHub API. It is a separate tool injected at run time, not
  linked into the app.
- Cisco's QtWebDriver (WebDriver for Qt): 200★, last push 2022-07-06, no licence field — GitHub API.
- Squish: subscription licences only since Squish 7.0 — qt.io blog, search snippet only; price not public, a
  reseller lists $1,190/year per floating execution licence — techjockey, search snippet only; free trial only.
  → **Out** (paid only).
- The Qt Company's own MCP offering is a hosted documentation server (`qt-docs-mcp.qt.io/mcp`, tools
  `qt_documentation_search` / `_read`) — https://doc.qt.io/agentictools/mcp/, page read. A Qt Creator MCP server for
  controlling the IDE exists in Qt Creator 20 snapshot docs — search snippet only. Neither drives a running app.
- Community MCP bridges into Qt apps: qtPilot (MIT, 5★, "Qt Mcp server that mimics the Claude Code Chrome api"),
  QtMcpEmbedded (Apache-2.0, 3★), dcc-mcp Qt action/inspector skills (MIT, 0–1★) — GitHub API.
- Assessment: an agent can drive a Qt Widgets app with free, standard parts — through the OS accessibility tree
  (pywinauto, AT-SPI, Appium Mac2) from outside, or QTest/PySide6/pytest-qt from inside — but none is as tidy as
  egui_kittest. The precedent most apps converge on (Unreal, Blender, Flutter Scene) is a command-level MCP or
  JSON-RPC channel inside the app; on Qt that would be ours (Spix is the closest library).

## G3 · Build-time evidence: Rust vs C++ for a large 3D codebase

- Rust compiler performance survey 2025: over 3,700 responses; average satisfaction 6/10 (mode 7); 55% wait more than
  10 s for a rebuild of their most frustrating project; about 45% of people no longer using Rust name compile times;
  in large workspaces, changing one crate rebuilds its dependents, which can "dramatically increase the latency of
  rebuilds in large (or deep) workspaces"; LLD becomes the default linker on x86_64 Linux —
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results (2025-09-10), page read.
- Rust 2026 fast-builds roadmap: CI clean builds "30+ minutes" for medium projects; the frontend is largely
  single-threaded; plans: Cranelift and TPDE debug backends, parallel frontend, "Relink-Don't-Rebuild" (target 5–10×
  faster rebuilds), crate slicing (1.4×–30× in experiments) — https://goals.rust-lang.org/2026/roadmap-fast-builds.html, page read.
- Feldera: about 100k lines of generated Rust took 1,617.77 s to build; split into about 1,106 crates it took
  150.24 s, on a 64-core machine — https://www.feldera.com/blog/cutting-down-rust-compile-times-from-30-to-2-minutes-with-one-thousand-crates (2025-04-15), page read.
- strager's port (9.3k lines of C++ → 9.5k lines of Rust), analysed by Derek Jones: at 1× source Rust 0.98 vs C++
  1.03; at 32× copies Rust 6.90 vs C++ 2.45 — "the size factor for Rust is growing quadratically, while it is much
  closer to linear for C++"; small sample, caveats stated — https://shape-of-code.com/2023/01/29/a-comparison-of-c-and-rust-compiler-performance/ (2023-01-29), page read.
- Bevy's `dynamic_linking` feature "speeds up incremental builds considerably"; not for release builds — bevy.org
  setup guide, search snippet only (no measured seconds found).
- C++: ISO C++ developer survey 2023 — build times a "major pain point" for 43%, second after library management
  (47%) — JetBrains summary, search snippet only (the JetBrains page returned 403; the isocpp PDF had no text layer).
- C++: Unreal Engine 5 full rebuild "40 minutes" on a Ryzen 5950X with 64 GB (forum user); UE4 clean builds 2–3 h on
  older workstations — forums.unrealengine.com, search snippet only.
- C++: Godot full build ~13–15 minutes typical on Godot 4.5 in Phoronix's test suite (76–3,722 s range) —
  openbenchmarking.org, search snippet only (the page returned 403).
- Code-quality data, not build time: Android (2025-11-13) — Rust rollback rate "~4x lower than C++" for medium and
  large changes, ~25% less review time, ~20% fewer revisions; 0.2 memory-safety vulnerabilities per MLOC in Rust vs
  "closer to 1,000" in C/C++ — https://blog.google/security/rust-in-android-move-fast-fix-things/, page read.
- Not found: a controlled clean-and-incremental build comparison of large Rust vs C++ codebases, or any for 3D
  engines.
- Assessment: both languages have slow builds at engine scale; Rust's are worse as crates grow unless the code is
  split into many crates; C++'s are worse for whole-engine rebuilds (Unreal). Build time doesn't decide the language;
  the layout (many small crates or modules, a fast linker, dynamic linking in development) matters more.

## G4 · Mesa lavapipe conformance for headless image tests; Metal

- lavapipe on Mesa `main` (27.0.0-devel): `#define LVP_API_VERSION VK_MAKE_VERSION(1, 4, VK_HEADER_VERSION)` (LLVM ≥
  10); `conformanceVersion` 1.3.1.1; device extensions include `KHR_acceleration_structure`, `KHR_ray_query`,
  `KHR_ray_tracing_pipeline`; window-system code covers Wayland, Win32, XCB, Xlib and `EXT_metal_surface`; also
  `EXT_headless_surface` — https://gitlab.freedesktop.org/mesa/mesa/-/raw/main/src/gallium/frontends/lavapipe/lvp_device.c, source read.
- "The Khronos Group has now formally recognized Lavapipe as a Vulkan 1.3 implementation" (submission 696, Ryzen 7
  1800X, Mesa 22.1) — https://www.phoronix.com/news/Lavapipe-Vulkan-1.3-Official (2022-07-20), page read.
- Lavapipe was Vulkan 1.2 conformant in May 2022 and gained ray-tracing pipelines in Mesa 24.1 (April 2024; its
  author: useful "for testing, comparison, and demos") — phoronix.com, search snippet only.
- No Vulkan 1.4 conformance submission for lavapipe found — search snippet only (absence not proven; the Khronos
  list wasn't read).
- llvmpipe (Mesa's CPU OpenGL): "uses LLVM to do runtime code generation", up to 32 threads; builds as a Linux
  `libGL.so` drop-in or a Windows `opengl32.dll` replacement — https://docs.mesa3d.org/drivers/llvmpipe.html, page read.
  (The lavapipe doc page returns 404.)
- wgpu's CI GPU tests: Windows (WARP, DXC, Agility SDK, Mesa, Vulkan SDK), Linux (Mesa, Vulkan SDK), Mac aarch64 on
  `macos-14`; its Mesa action installs Mesa 26.1.3 and points the Vulkan loader at `libvulkan_lvp.so` (lavapipe) on
  Linux, with a Windows step too — https://github.com/gfx-rs/wgpu/blob/trunk/.github/workflows/ci.yml and
  `.github/actions/install-mesa/action.yml`, source read.
- Bevy: job `run-examples-macos-metal` on `runs-on: macos-14` saves screenshots and sends them to Pixel Eagle; the
  Linux job uses `mesa-vulkan-drivers` under `xvfb-run` —
  https://github.com/bevyengine/bevy/blob/main/.github/workflows/example-run.yml, source read.
- GitHub's M1 runners became available to all plans, including open source (runner-images issue #9254, closed
  2024-03-07) — GitHub API. GitHub's 2023 announcement of the M1 *larger* runner says "GPU hardware acceleration
  enabled by default" — github.blog, search snippet only.
- CircleCI's macOS executor "does not currently have any gpu/hardware acceleration due to being run in a VM"; "Metal
  appears to not have this fallback functionality" — https://support.circleci.com/hc/en-us/articles/360052160592 (2026-05-14), page read.
- Apple's ParavirtualizedGraphics framework gives macOS guests Metal through the host GPU (Parallels: Big Sur+,
  Metal only); a cited VM Metal score 102,282 vs host 110,960 — kb.parallels.com, eclecticlight.co (2026-04-29),
  search snippet only.
- Zed's GPUI has a "headless Metal platform for visual tests" that renders scenes to images without a window —
  git.secluded.site mirror of zed, search snippet only.
- Assessment: Linux and Windows golden-image tests can run on lavapipe (Vulkan 1.4 with ray tracing) and WARP
  (D3D12) on any CI machine. Metal has no CPU fallback; Metal goldens need an Apple-silicon runner (GitHub's
  `macos-14` works — Bevy and wgpu do it) and per-platform reference images.

## G5 · Ray tracing on Metal per library

- **Diligent:** platform table — Metal on macOS, iOS, tvOS, visionOS marked "² Available under commercial license";
  macOS Vulkan "requires a Vulkan portability implementation such as MoltenVK or gfx-portability" —
  https://github.com/DiligentGraphics/DiligentEngine README, source read.
- **MoltenVK:** PR #2771 "WIP: Add Metal ray query and ray tracing support" (open; created 2026-07-12, updated
  2026-10-26): implements `VK_KHR_acceleration_structure`, `ray_query`, `ray_tracing_pipeline`, `pipeline_library`;
  "remains disabled unless MVK_CONFIG_ENABLE_EXPERIMENTAL_RAY_TRACING=1"; needs SPIRV-Cross PR #2663; tested on an M5
  Pro. Issue #2384 (hardware ray tracing and mesh shading) open since 2024-10-20 — GitHub API.
- → Diligent on a Mac under the no-paid rule = MoltenVK = **no ray tracing today**; possibly later, as an
  experimental opt-in, if #2771 merges. Diligent stays "in, minus Metal and minus Mac ray tracing".
- **The Forge:** `Common_3/Graphics/Metal/MetalRaytracing.mm` (570 lines) builds `MTLAccelerationStructure` objects
  (triangle geometry, instance descriptors) — source read. README: "We switched to Ray Queries for the common Ray
  Tracing APIs on all the platforms we support", with a "Ray Queries on macOS" screenshot from an M2 Mac; supported
  platforms include "Windows(Vulkan/DX12), macOS/iOS"; a hybrid ray-traced-shadows test also runs on an M2 Mac —
  https://github.com/ConfettiFX/The-Forge README, source read.
- **Wicked Engine:** `wiGraphicsDevice_Metal.cpp` uses Metal 4 (`MTL4AccelerationStructure`), exits with "Metal 4
  graphics is not supported by your system"; sets `GraphicsDeviceCapability::RAYTRACING` when
  `device->supportsRaytracing()`; `CreateRaytracingPipelineState` and `DispatchRays` are `// TODO`; the repo ships
  `libmetalirconverter.dylib` (Apple's Metal shader converter, licence not checked) —
  https://github.com/turanszkij/WickedEngine/tree/master/WickedEngine, source read.
- Metal 4: "Mac with Apple silicon", "macOS Tahoe 26 or later" — https://support.apple.com/102894, page read.
- **wgpu:** `EXPERIMENTAL_RAY_QUERY` — "Supported platforms: Vulkan"; "native-only" — features.rs on trunk, source read.
- Filament, bgfx, Ogre-Next, Magnum: no ray tracing listed (round one, page read).
- Assessment: for ray tracing on Windows, Linux **and** macOS under the scope rules, The Forge is the only library
  with a working Metal ray-query path; Wicked has inline ray queries on Metal 4 (Apple silicon + macOS 26 only) and
  no ray-tracing pipelines there. Designing JustStage's ray-traced features around **ray queries** (not
  ray-tracing pipelines) keeps every backend open.

## G6 · Big apps using WebAssembly plugins, and what they learned

### Microsoft Flight Simulator

- "In order to provide both security and portability, it was decided to move away from add-ons distributed as DLLs";
  modules "are not interpreted but rather converted to native code ahead of time"; runs modules "on different
  threads" but "each module is still single threaded"; "C++ exceptions are not supported"; "C++ threads are not
  supported"; "The Windows API is not supported"; read-only access to the add-on package, read/write under `\work`
  — https://docs.flightsimulator.com/msfs2024/retail/programming-apis/wasm/webassembly/index.md (MSFS 2024 SDK), page read.
- MSFS 2020 docs: C/C++ compiled to `.wasm` by a Visual Studio platform toolset, `/clang:-O3`; debugging by
  attaching to the game; Edit and Continue partly supported; encrypted Marketplace packages block reading some files
  — https://docs.flightsimulator.com/html/Programming_Tools/WASM/WebAssembly.htm, page read.
- Developer complaints (2024-10-31 to 11-01): no multithreading (main limit); can't link any library or call Windows
  APIs; no C++ exceptions (hard to port Boost-style code); no reading files outside the package. Asobo staff:
  multithreading "has proven technically hard"; exceptions may come with a toolchain update; full drive access ruled
  out "for security reasons" — https://devsupport.flightsimulator.com/t/dll-vs-wasm-modules/10658, page read.

### Figma

- 2019-10-02: "vulnerabilities were recently discovered with the Realms shim" that could let plugin code escape; "We
  now use QuickJS, a JavaScript VM written in C and cross-compiled to WebAssembly"; "somewhat slower for certain
  plugins, but intrinsically more secure" — https://madebyevan.com/figma/an-update-on-plugin-security/ (copy on the
  co-founder's site), page read.
- The original design kept plugin UI in a null-origin iframe that talks to the document only through messages —
  figma.com blog "How to build a plugin system on the web and also sleep well at night", search snippet only.

### Zed (code editor)

- Extensions are Rust compiled to Wasm components; interfaces in WIT; host side `wasmtime::component::bindgen!`;
  Wasmtime with `async: true`; the API version is recorded in each extension's manifest and Zed picks matching
  bindings; extensions can add languages, language servers, themes, snippets, slash commands, but can't create UI
  panels or make arbitrary HTTP or file-system calls; Wasm "wasn't mature enough" until the component model became
  usable in early 2024 — https://zed.dev/blog/zed-decoded-extensions (2024-10-21), page read.

### Others

- Helm 4 (Kubernetes package manager): `go.mod` requires `github.com/extism/go-sdk v1.7.1` and
  `github.com/tetratelabs/wazero v1.12.0`; `internal/plugin` has both `runtime_extismv1.go` and
  `runtime_subprocess.go`; latest v4.3.1 (2026-10-15) — https://github.com/helm/helm, source read.
- Extism users named in a QCon London 2026 talk: Helm, Moonrepo, Reactables — qconlondon.com, search snippet only.
- Typst: plugins are Wasm modules isolated from the system (no printing or file reads); WASI imports aren't allowed
  (they must be stubbed); a purity requirement shapes the API — typst.app docs, search snippet only.
- VS Code: `wasm-wasi-core` runs WASI code inside extensions (2023); the component model with WIT and `wit2ts`
  (2024); Wasm in a worker so the extension host isn't blocked — code.visualstudio.com blogs 2023-06-05,
  2024-05-08, 2024-06-07, search snippet only.
- Audio: WCLAP = CLAP plugins compiled to Wasm; GUIs through a webview extension because "platform-native view
  handles can't be used inside the WASM sandbox" — github.com/WebCLAP, search snippet only.
- Envoy / Istio proxy-wasm: no detailed production post-mortem found; one field report (UiPath) traded higher memory
  for lower CPU — search snippet only.
- GPU access from Wasm: `wasi:webgpu` "Current Phase: Phase 2", portability "Linux, Windows, MacOS, Android, Web";
  last push 2026-07-02 — https://github.com/WebAssembly/wasi-gfx README, source read.
- No 3D content-creation app with Wasm plugins found in this pass either.
- Assessment: the lessons repeat — Wasm buys a real sandbox and one binary for every OS, at the cost of threads,
  exceptions, native libraries and direct GPU and UI access (MSFS, Zed). The apps that use it give Wasm plugins
  narrow, versioned interfaces (WIT) and keep a second, native or subprocess route for heavy work (Helm). For
  JustStage this fits importers, generators and rules as Wasm, while render, simulation and UI plugins need native
  code or Python.

## G7 · Unreal's Python scripting; Godot's C# hosting

- Unreal: "the Python environment is only available in the Unreal Editor"; "you cannot currently use it as a
  gameplay scripting language"; "The Python Editor Script Plugin contains an embedded version of Python 3.11.8" —
  https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python (UE 5.8), page read.
- Unreal MCP: "Experimental"; "Supports HTTP and Server-Sent Events only"; default `http://127.0.0.1:8000/mcp`;
  "There is no authentication layer; the plugin is not safe to expose beyond the local machine"; "executing Tool
  invocations on the game thread serially"; toolsets derive from `UToolsetDefinition` (C++) or
  `unreal.ToolsetDefinition` (Python); "Cooked and shipping game builds can host an MCP server" via
  `IModelContextProtocolModule::StartServer()`, but the Toolset Registry adapter is editor-only (tools added with
  `AddTool()`) — https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor?lang=en-US (5.8), page read.
- A UE 5.8 bug report: the MCP server "instantly drops connections" for some clients — forums.unrealengine.com, search snippet only.
- Godot C#: "Godot 4.5 requires .NET 8 or later, but exporting to Android requires .NET 9 or later"; "Godot bundles
  the parts of .NET needed to run already-compiled games"; "Projects written in C# using Godot 4 currently cannot be
  exported to the web platform"; Android and iOS experimental — https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/c_sharp_basics.html (4.7 docs), page read.
- Godot's .NET module loads the runtime through `hostfxr` (`hostfxr_initialize_for_runtime_config`,
  `hostfxr_get_runtime_delegate`) and also has a direct `coreclr_initialize` path —
  https://github.com/godotengine/godot/blob/master/modules/mono/mono_gd/gd_mono.cpp, source read.
- Assessment: Godot is the precedent for hosting .NET from a C++ engine with the standard hostfxr route (round one's
  MS Learn page). Unreal confirms "Python in the editor, C++ at runtime" as the big-engine pattern, and its MCP is
  editor-centred.

## G8 · Licence files GitHub marks NOASSERTION

One line each (all source read via GitHub's API, 2026-10-29):

- **ozz-animation** — MIT ("distributed under the MIT License", © 2020 Guillaume Blanc) — commercial use: yes — [LICENSE.md](https://github.com/guillaumeblanc/ozz-animation/blob/master/LICENSE.md)
- **assimp** — BSD-3-Clause (© 2006–2026 assimp team); files in `test/models-nonbsd` are under their creators'
  terms; bundled Poly2Tri etc. carry BSD-style notices — commercial use: yes — [LICENSE](https://github.com/assimp/assimp/blob/master/LICENSE)
- **CGAL** — each library file GPL-3.0-or-later or LGPL-3.0-or-later (stated per file); some Boost-derived files
  BSL; CORE and ImageIO LGPL; examples and files without a notice CC0; commercial licences from GeometryFactory —
  commercial use: conditional (GPL parts force GPL unless bought) — [Installation/LICENSE](https://github.com/CGAL/cgal/blob/main/Installation/LICENSE)
- **Magnum** — MIT (© 2010–2026 Vladimír Vondruš and contributors) — commercial use: yes — [COPYING](https://github.com/mosra/magnum/blob/master/COPYING)
- **Ogre-Next** — MIT ("OGRE … is made available under the MIT License") — commercial use: yes — [COPYING](https://github.com/OGRECave/ogre-next/blob/master/COPYING)
- **mitsuba3** — BSD-3-Clause text plus a clause: enhancements you choose to make public, or send to the author
  without a separate licence, are licensed to the author royalty-free — commercial use: yes — [LICENSE](https://github.com/mitsuba-renderer/mitsuba3/blob/master/LICENSE)
- **glm** — "The Happy Bunny License or MIT License" (choice) — commercial use: yes — [copying.txt](https://github.com/g-truc/glm/blob/master/copying.txt)

## G9 · Cascadeur and Marvelous Designer: toolkits and languages; effort figures

### Cascadeur

- Open beta 2020.1 changes: "GUI conversion to QML", "the revised core architecture to improve the general
  performance" — https://gameworldobserver.com/2020/07/29/nekki-launches-cascadeur-open-beta (2020-07-29), page read.
- A Nekki job ad for a "Qt QML C++ developer" on the Cascadeur team asked for strong C++ and Qt QML experience, with
  Conan, CMake and GitLab as pluses — nekki.com, search snippet only (the page returned 404 when fetched).
- "Eugene Dyabin started Cascadeur in 2006 as an internal animation tool for Nekki"; closed beta February 2019;
  Nekki founded 2002 — https://cascadeur.com/about, page read.
- "Cascadeur uses Python 3.8"; "Python scripting uses the csc module for accessing Cascadeur API"; console "intended
  primarily for running scripts, not for writing them" — https://cascadeur.com/help/tools/animation_tools/python_scripting_in_cascadeur, page read.
- Core language: C++ is stated only in the job ad (snippet). Assessment: C++ core + Qt QML UI + embedded Python 3.8 —
  the same shape as iClone.

### Marvelous Designer

- Python API on "Windows and Mac OS"; modules EXPORT_API, FABRIC_API, IMPORT_API, PATTERN_API, UTILITY_API —
  https://developer.marvelousdesigner.com/, page read.
- A GUI API is documented as "Coming soon" (not in 2026.1); Marvelous Designer "draws every window and widget in its
  own look and theme"; "No extra Python package is needed"; "Not in headless mode" — https://developer.marvelousdesigner.com/gui_api.html, page read.
- Changelog MD 2026.1: one function "works in headless mode only"; 2025.1.107 added built-in pip on Windows and `.py`
  plugins through the plugin manager; earliest entry MD 2024.2.189 — https://developer.marvelousdesigner.com/changelog.html, page read.
- Conflict: a support-forum reply said no headless session exists (undated) — support.marvelousdesigner.com, search
  snippet only. The 2026.1 changelog is newer.
- Qt: staff said MD uses "Qt version 5 … 5.14.2" and that Qt support (PythonQt) was removed from MD 10 scripting;
  a user says MD 12 ships Qt 5.15.2 DLLs — support.marvelousdesigner.com, search snippet only (pages return 403).
  "Marvelous Designer 10 Python Changes" news item dated 2020-12-02 — marvelousdesigner.com (title and date page
  read; body didn't load).
- Linux edition announced 2025-10-01: Rocky Linux 9+ / RHEL 9+; Python API included, but only on the Enterprise tier
  with floating licences ($2,300/year for Linux) — https://www.cgchannel.com/2025/10/marvelous-designer-is-now-available-for-linux/, page read.
- Core language: not found in public sources.

### Cinema 4D (re-check, round-one snippet)

- `GeDialog`: a dialog is "a window or a panel"; layouts built in `CreateLayout` or from resources
  (`LoadDialogResource` "the preferred method"); modal and async dialogs; async dialogs can be placed in the user's
  layout — https://developers.maxon.net/docs/py/2026_0_0/modules/c4d.gui/GeDialog/index.html (C4D 2026.0 SDK), page read.
- PySide in C4D 2024: Maxon SDK specialist ferdinand recommended an abstraction layer (QtPy) or a client-server design;
  users report PySide isn't bundled and PyPI wheels don't load — https://developers.maxon.net/forum/post/72746, page read.
- "Starting with Cinema 4D 2024.2 … possible to import PySide6", "the Maxon SDK team does not recommend using other
  third-party UI libraries" — written by a forum user ("As far as I know"), not Maxon staff —
  https://developers.maxon.net/forum/post/75688, page read.
- "Python API is a subset of the C++ API": not stated on the 2026.0 SDK index page — not confirmed.

### Effort figures

- **Blender:** Development Fund $326,118 a month; 7,611 individual and 46 corporate members —
  https://fund.blender.org/ (read 2026-10-29), page read. 2024 annual report published 2025-09-15 —
  https://www.blender.org/?p=95075, page read (the report PDFs return 403). 2024 income about €3.1M (2023: €2.55M);
  payments to developers €1.78M (2023) → €2.15M (2024); staff and developer grants 87% of spending —
  https://cgpress.org/archives/blender-foundation-reports-higher-donations-but-warns-of-low-reserves-in-2024-annual-report.html (2025-09-16), page read.
  Round one's GitHub figures stand (166,956 commits, 1,596 contributors; first source 1994).
- **Maya:** "Maya 1.0 was released in February 1998", built on Wavefront's The Advanced Visualizer, TDI Explore,
  Alias PowerAnimator and Alias Sketch!; "Qt-based user interface" since Maya 2011; written in C++ (plus MEL, Python,
  C#) — https://en.wikipedia.org/wiki/Autodesk_Maya, page read. "Over 26 million lines of code" at the 2001 Mac port
  — architosh.com, search snippet only (the page body didn't load). No team size found.
- **Houdini:** Side Effects Software founded 1987 by Kim Davidson and Greg Hermanovic, releasing PRISMS, which "would
  lay the groundwork for Houdini"; Epic Games became a minority investor in 2020 — https://www.sidefx.com/company/about-sidefx-old/, page read.
  PRISMS became Houdini in 1996 — ohiostate.pressbooks.pub, search snippet only. Company size 171–227 people per
  data aggregators (PitchBook, Built In) — search snippet only, low reliability.
- **Unreal's editor:** Unreal Engine 1 developed from 1995 by Tim Sweeney, with UnrealEd in the engine — Wikipedia /
  Giant Bomb, search snippet only. "Around 40 people" on UE4 in an old Sweeney interview — complex.com, search snippet
  only. Epic's headcount from aggregators conflicts (3,544 vs 11,834) — not used.
- Assessment: the only hard numbers are Blender's (about €2M a year of paid development on top of 30 years and
  ~1,600 contributors) and the years (Maya: 1993→1998 to 1.0 on top of older codebases; Houdini: from 1987).
  Round one's conclusion stands: every pro editor is decades of work; buy every layer that exists.

## G10 · Re-check of round one's snippet-only facts

| Fact (round one) | Now | Status |
|---|---|---|
| Cascadeur: Python 3.8, `csc` module | Confirmed | page read (cascadeur.com help) |
| Cascadeur: `call_action` by ID to be phased out | Not on the page read; remains | search snippet only |
| Marvelous Designer: Python API (v10+), Win + Mac | Win + Mac confirmed; "v10+" from support | page read / snippet |
| Marvelous Designer: no headless mode | **Conflict:** 2026.1 changelog mentions a headless mode | page read (changelog) vs snippet (support) |
| Marvelous Designer: API needs Qt 5.15.2 on the path | Staff: Qt 5 (5.14.2); a user: MD 12 ships 5.15.2 | search snippet only (403) |
| Marvelous Designer Linux 2025 | Announced 2025-10-01, Rocky/RHEL 9+ | page read (cgchannel) |
| Cinema 4D: Python API = subset of C++ API | Not stated on the SDK index | not confirmed |
| Cinema 4D: PySide6 importable since 2024.2, Maxon "does not recommend" | Said by a user, not staff; staff suggested QtPy or client-server | page read (two forum threads) |
| Unreal Slate: "custom", "platform agnostic", for editor and in-game UI | Confirmed: "a completely custom and platform agnostic user interface framework" | page read (UE 5.8 docs) |
| CC5 uses RLPy | Confirmed: tracker report on CC 5.11, "CC5.1 RLPy API", submitted 2026-07-15, "Released in 5.13" | page read ([tracker](https://reallusion.com/FeedBackTracker/Issue/Bug-Report-Hair-ccHair-cannot-be-applied-to-an-avatar-via-the-RLPy-API-generated-by-Claude)) |
| Unreal 5.8 MCP: HTTP/SSE, `127.0.0.1:8000/mcp`, no auth, serial on game thread | Confirmed; plus shipping builds can host a server | page read (Epic docs) |
| Multi-SWE-bench: Java above Rust and C++ | Confirmed: 1,632 instances, 7 languages; Claude 3.7 Sonnet Java 14.06/23.44/21.88 %, Rust 5.44/6.69/15.90 %, C++ 3.10/11.63/14.73 % (MagentLess / MSWE-agent / MopenHands); Python 44.6–52.2 % | page read ([arXiv HTML, Table 4](https://arxiv.org/html/2504.02605); v1 2025-04-03) |
| SWE-Sharp-Bench: ~40 % C# vs ~70 % Python | Confirmed: "150 instances from 17 repositories"; "70% of Python tasks in SWE-Bench Verified are solved, only 40% of our C# tasks"; v1 2025-11-04, v3 2025-11-18 | page read ([arXiv](https://arxiv.org/abs/2511.02352)) |
| PEP 779: ≤10 % slowdown, ≤15–20 % memory, Stable ABI in 3.15 | **Corrected:** Final, resolved 2025-06-16, Python 3.14; Phase II = "officially supported but still optional"; "15% as a hard performance target" (current penalty ~10 %, ~3 % on macOS); memory "target of 20%"; Stable ABI an open issue, no version named | page read ([PEP 779](https://peps.python.org/pep-0779/)) |
| WASI 0.3 released 2026-06-11, Wasmtime 46 default | Confirmed; Wasmtime 46.0.0 released 2026-06-22; `wasi:io` removed in 0.3; Wasmtime 43–45 implement an RC snapshot | page read (wasi.dev) + GitHub API + RELEASES.md source read |
| Avalonia 12 screen readers on Windows/macOS/Linux | Confirmed in source: `src/Avalonia.FreeDesktop.AtSpi` (Linux), `native/Avalonia.Native/src/OSX/automation.mm` (macOS), Win32 automation integration tests, `src/Android/Avalonia.Android/Automation`; 12.0.0 released 2026-04-07 | source read (GitHub API); docs page 404 |
| Slint wgpu underlay via `set_rendering_notifier()` | Confirmed; feature-gated `unstable-wgpu-29/30` | source read |
| Dear ImGui 1.92 (2025-06-25) dynamic fonts, `FontScaleDpi` | Confirmed: "added `style.FontScaleDpi` … changed on per-monitor/per-viewport basis, which `io.ConfigDpiScaleFonts` does automatically"; `io.ConfigDpiScaleViewports`; renderer backends need `ImGuiBackendFlags_RendererHasTextures` | source read ([v1.92.0 release notes](https://github.com/ocornut/imgui/releases/tag/v1.92.0)) |

---

## Couldn't verify / open

- **No controlled build-time comparison** of large Rust vs C++ codebases (or 3D engines) exists that I could find;
  the C++ side rests on forum snippets and a survey summary (JetBrains page 403, the isocpp PDF had no text layer,
  OpenBenchmarking 403).
- **No public team sizes** for Maya, Houdini or Unreal's editor; the Blender annual-report PDFs return 403, so
  Blender's headcount isn't stated (only money figures). Maya's "26 million lines" (2001) is a snippet; the page body
  didn't load.
- **Marvelous Designer's UI toolkit and core language** stay unconfirmed: support-forum pages return 403; the
  developer docs say only that MD draws its own widgets. Its headless mode needs the 2026.1 manual to settle the
  conflict.
- **Cascadeur's core language** rests on a job-ad snippet (the ad page now 404); `call_action` phase-out stays snippet-only.
- **Cinema 4D**: "Python API = subset of C++ API" not found on an official page.
- **lavapipe Vulkan 1.4 conformance**: the Khronos conformant-products list wasn't read; the source reports
  conformance version 1.3.1.1.
- **GitHub-hosted macOS runners' GPU** is shown by working CI jobs (Bevy, wgpu), not by a GitHub document.
- **Flutter desktop accessibility per OS** (which platform API it uses on Windows and Linux) is not stated in the docs read.
- **Apple's Metal shader converter** licence (shipped as `libmetalirconverter.dylib` in Wicked's repo) was not checked.
- **Wasm plugins in a 3D content-creation app**: none found; Envoy/Istio post-mortems with numbers not found.
- **Refused scripted access (not worked around):** blog.jetbrains.com, openbenchmarking.org, download.blender.org
  (annual-report PDFs), support.marvelousdesigner.com, archive.blender.org.
