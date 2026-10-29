# Research 07 pass 2 — building blocks (second pass, section S7)

Date: 2026-10-29. By the S7 research agent; not re-checked by the lead. For RESEARCH.md §7. Gap list:
`2026-10-29-research-second-pass.md` §S7. Round one: `2026-10-29-research-07-building-blocks.md`.

**Labels.** Every fact carries its source, the source's date, and one of:
- **[P] page read**: read at the primary page, the repo's own README, licence file, source file or issue (GitHub through
  `gh api`, read-only GETs), Hugging Face's API or model card, arXiv's API, or a docs source repo.
- **[S] search snippet only**: seen only in a search result; not confirmed at its page.

"Repo date" means the last push or the file's last commit as GitHub reported it on 2026-10-29. Star counts are from the same day.

**Method.** About 37 WebSearch calls (of the ~200 allowed); everything else through WebFetch, `gh api` (repo metadata, READMEs,
licence files, issues, code search), Hugging Face's model API, arXiv's export API and the Blender manual's source repo on
projects.blender.org. No installers, models, weights or datasets were downloaded. WebFetch saved two PDFs it was pointed at into the
session's tool-results folder on F: by itself: Adobe's 1-page Mixamo Additional Terms (16 KB, read) and the XPBD paper (1.9 MB, could
not be rendered — no text taken from it). Scratch files are in the session scratchpad on F:. One site refused with HTTP 429
(optitrack.com) and one has a certificate the fetcher rejects (mocap.cs.cmu.edu); neither was worked around.

Scope rules as in the second-pass file: paid-only out; one-GPU-vendor code out for the core (renderer, engine, physics, editor);
optional parts (AI models, mocap) labelled with vendors; Unreal in, Unity out; licences are labels.

## Top findings

1. **A cross-vendor GPU garment-cloth solver now exists: ZOZO's Contact Solver** (`st-tech/ppf-contact-solver`, Apache-2.0,
   4.6k stars). Since 2026-09-19 it runs on NVIDIA (CUDA), AMD (ROCm), Apple (Metal) and CPU (AVX2/NEON); it is Rust-first, barrier-based
   penetration-free FEM shells/solids/rods with seam **stitches**, a Blender add-on and an MCP server, and ships a dress-on-a-dancing-body
   example. Limits it states itself: offline (not real time), AMD "never run on real AMD hardware", CPU and Metal "slow", "not production
   ready (yet)", one maintainer. — [README](https://github.com/st-tech/ppf-contact-solver), 2026-10 [P]
2. **An open FBX writer now exists: `ufbx_write`** by the ufbx author — one C file, **MIT or public domain**, writes ASCII and binary
   FBX (version 7500) with nodes, meshes, materials, textures, cameras, lights, bones, bind poses, **skin clusters, blend shapes** and
   **animation stacks/layers/curves**. Marked "still a work-in-progress, … breaking changes are to be expected"; no release tags.
   — [ufbx/ufbx-write](https://github.com/ufbx/ufbx-write), last commit 2026-06-07 [P]
3. **Two open texture bakers found.** ArmorPaint's source (zlib) has 14 bake types — curvature, tangent and object normal, height,
   derivative, position, UV, material ID, object ID, vertex colour, AO, lightmap, bent normal, thickness — with normal/height/derivative
   "from high-poly mesh" and GPU ray-traced AO/bent-normal/thickness bakes (shader sources plus Metal versions). Unreal's Geometry
   Script lists 14 bake types (tangent/object/face/bent normal, position, curvature, AO, texture, multi-texture, vertex colour, material
   ID, UV shell, height). — [ArmorPaint enums.h](https://github.com/armory3d/armorpaint/blob/main/paint/sources/enums.h) 2026-10 [P];
   [UE Python 5.8 GeometryScriptBakeTypes](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/GeometryScriptBakeTypes) [P]
4. **Garment refitting has open research code and an Unreal feature, but still no MetaTailor-class open tool.** LoBoFit (SIGGRAPH 2026,
   **BSD-3**, PyTorch, CUDA or CPU) refits single- and multi-layer garments across avatars with different shapes, poses and topology —
   with a notice that parts "may be covered by a pending Chinese patent application". Unreal 5.6+ has an **Outfit Asset with
   resizing/refitting** (a 5.6 Chaos Cloth post on Epic's forum; the 5.8 Python API documents per-size body parts and resizing
   "interpolation points … distributed evenly across the entire body"). — [LoBoFit](https://github.com/MengZephyr/LoBoFit) 2026-07 [P];
   [Epic forum, 2025-06-13](https://forums.unrealengine.com/t/2555686) [P];
   [ChaosSizedOutfitSource](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ChaosSizedOutfitSource) [P]
5. **TRELLIS.2 runs cross-vendor through `trellis.cpp`** (MIT, GGML C++): prebuilt CUDA, **ROCm and Vulkan** binaries, Metal verified on
   Apple M5; the 1024 cascade fits a 16 GB card; on Apple silicon a 512 run peaked at 5.6 GB RSS. It serves as the `trellis`
   back-end of Lemonade.
   ComfyUI also added **native TRELLIS.2 and Pixal3D** (merged 2026-08-22) with all post-processing re-done in PyTorch/SciPy "to avoid
   any extra dependencies". — [trellis.cpp](https://github.com/pwilkin/trellis.cpp) 2026-10 [P];
   [ComfyUI PR #14718](https://github.com/Comfy-Org/ComfyUI/pull/14718) 2026-08-22 [P]
6. **Auto-rigging is no longer CUDA-only:** `skin-tokens.cpp` (Apache-2.0, C++/GGML) runs SkinTokens/TokenRig on **CPU or Vulkan**
   from F16 GGUF weights (~1.25 GB total); an MLX (Apple) conversion exists; UniRig's skeleton stage has ONNX exports, one int8 for
   in-browser **WebGPU** (455 MB). UniRig's skin-weight head has no ONNX port (spconv). — [skin-tokens.cpp](https://github.com/localai-org/skin-tokens.cpp) 2026-10 [P];
   [SkinTokens-GGUF card](https://huggingface.co/LocalAI-io/SkinTokens-GGUF) 2026-08-28 [P];
   [unirig-skeleton-onnx-webgpu](https://huggingface.co/cgb/unirig-skeleton-onnx-webgpu) 2026-09-04 [P]
7. **Audio2Face-3D's weights ship as ONNX** (`network.onnx` in the v3.0 repo) and a Swift-MLX port of v2.3 runs on Apple silicon; the
   official runtime is still TensorRT. So it is NVIDIA-first, not strictly NVIDIA-only. — [nvidia/Audio2Face-3D-v3.0 files](https://huggingface.co/nvidia/Audio2Face-3D-v3.0) [P];
   [MLX port card](https://huggingface.co/aufklarer/Audio2Face-3D-v2.3-Mark-MLX) [P]
8. **Cascadeur's free plan is "Only non-commercial use"**, exports `.casc` only ("`.fbx` and `.dae` are not available"), 300 frames and
   120 joints per scene. Ragdoll for Blender is free but recording to controls needs a paid licence [S]. Open physics-animation pieces:
   Balance Point (GPL-3 Blender add-on: centre of mass, ballistic ruler, angular-momentum-conserving bake), OpenSim Moco (Apache-2.0
   trajectory optimisation, `MocoTrack`/`MocoInverse`), MuJoCo MPC (Apache-2.0). — [cascadeur.com/plans](https://cascadeur.com/plans) undated [P];
   [Balance Point](https://github.com/rdat5/Balance-Point) 2026-07 [P]; [opensim-core](https://github.com/opensim-org/opensim-core) 4.6, 2026-07-09 [P]
9. **Sculpting: still no embeddable library**, but new open apps appeared: SculptForge (GPL-3, created 2026-10-21, v0.9.3 on
   2026-10-29: ZBrush-style brushes, SubTools, voxel remesh, quad remesh, sculpt layers as blend shapes), BrokkrSculpt (AGPL-3, Rust/wgpu
   voxel-SDF), Rooms (MIT, WebGPU SDF sculpting in VR, IEEE CG&A 2026), and a work-in-progress sculpt mode inside ArmorPaint (zlib).
   Blender's dynamic topology is confirmed (`sculpt_paint/mesh/sculpt_dyntopo.cc`). — repos below [P]
10. **Mixamo's Additional Terms (effective 2021-06-23) forbid using Mixamo "or any content, data, output … derived from" it to "create,
    train, test, or otherwise improve any machine learning algorithms or artificial intelligence systems".** —
    [Adobe PDF](https://wwwimages2.adobe.com/content/dam/cc/en/legal/servicetou/Mixamo-Addl-Terms-en_US-20210623.pdf) [P]
11. **Autodesk FBX SDK 2020 licence:** you may link the Library and distribute your product "free of charge or for a fee", sublicensed
    "as is"; you must show "This software contains Autodesk® FBX® code developed by Autodesk, Inc. Copyright 2019 Autodesk, Inc."; you may
    not redistribute the SDK itself, reverse engineer it, or let your use "cause the Software to be subject to any licensing terms other
    than those set forth in this Agreement" (its open-source clause names GPL and LGPL). — [copy hosted by SideFX](https://www.sidefx.com/docs/houdini/licenses/fbx.html) [P]
12. **VRAM, newly sourced:** SAM 3D Objects needs Linux and an NVIDIA GPU with ≥32 GB; Step1X-3D geometry+texture 27–29 GB; SAM 3D Body
    can exceed 24 GB on some inputs (a CPU-offload fork peaks ~6.5 GB); WHAM ~9 GB for a 20 s clip; GVHMR ~6 GB; NLF "a smaller GPU would
    also be enough" than 24 GB; Puppeteer's rigging fits 8 GB, its animation stage does not; ChatGarment ≥15 GB; Pixal3D 18–36 GB
    (low-VRAM mode merged; a community patch ~11 GB); BPT ~12 GB; MoMask runs on CPU. Details and sources in §2.
13. **Hi3D v1.0 (press release 2026-10-23 [S]; repo created 2026-10-16) does not run on the target machine:** it is geometry refinement only (needs a coarse mesh, by
    default from Hunyuan3D-2 mini), requires an NVIDIA GPU with compute capability ≥8.0 (the RTX 2070 Super is 7.5), no CPU path; its
    "Hi3D Open License 1.0" allows commercial use with a "Powered by Hi3D 1.0" display and a separate licence above 200,000 MAU or
    USD 1M monthly revenue. — [Hi3Dv1.0](https://github.com/hi3d-official/Hi3Dv1.0) 2026-10 [P]
14. **Licences resolved:** Rokoko's Blender plugin — the only licence file is LGPL-3.0 (added 2020); the MIT badge sits in the README
    rewritten in 2025 and links to that LGPL file. Rhubarb Lip Sync — MIT (all dependencies permissive). XR Animator — CC BY-NC-SA 4.0 for reuse of its code. lightmapper —
    public domain. MotionGPT3 — README says MIT, but no LICENSE file exists. CameraHMR, DressCode, Noitom MocapApi, VRM spec — no licence
    statement anywhere in the repo. KTX-Software — Apache-2.0 plus mixed permissive files, except an optional non-open Ericsson ETC decoder.
    CGAL — the kernel layer is LGPL; every mesh-processing package (PMP, booleans, remeshing, simplification, parameterisation, alpha
    wrap, Mesh_3) is GPL. Sources in §6.
15. **Platform facts:** Godot's IK modifiers (TwoBoneIK3D, FABRIK3D, CCDIK3D, JacobianIK3D, SplineIK3D, ChainIK3D) are in stable since
    **4.6 (2026-01-26)**; OIDN runs on NVIDIA (Turing+), AMD (RDNA2+), Intel (Xe+) and Apple (M1+) GPUs; PhysX's FEM soft bodies, PBD
    particles and SDF collision are **GPU-only** (CUDA, Pascal+); MoonRay's XPU mode is CUDA or Apple Metal (no AMD). Sources in §8.

---

## 1 · The jobs with no open option in round one

### 1a · Pattern-and-sew garment making (a Marvelous Designer equivalent)

- ZOZO's Contact Solver: Apache-2.0; shells (cloth), solids, rods, rigid bodies, sand; "100% Penetration-Free Upon Success"; fabric
  presets "match real measurements"; Blender add-on (simulate locally or on a remote GPU over SSH/Docker) and JupyterLab front-end; MCP
  server "so any LLM … can drive the whole pipeline". — [README](https://github.com/st-tech/ppf-contact-solver), 2026-10 [P]
- Its back-ends: NVIDIA CUDA 12.8+ (Linux, Windows), AMD ROCm gfx9–gfx12 (Linux, Windows), Apple Metal (M1/A14+), CPU x86_64/arm64.
  Recommended NVIDIA cards "RTX 4090 / 5090 for large scenes; 3090 / 4070 / 5070 for small to medium ones". — same README [P]
- Its stated limits: "Offline use: Not real time, though some examples reach interactive rates"; "Not the fastest"; "AMD GPUs untested";
  "CPU and Metal backends are slow"; "Not production ready (yet)"; "Maintained by Ryoichi Ando alone". — same README [P]
- Paper: "A Cubic Barrier with Elasticity-Inclusive Dynamic Stiffness", ACM TOG 43(6) (SIGGRAPH Asia 2024); main branch "will deviate
  from the paper". — same README [P]
- Sewing: the add-on's Snap/Merge records a **stitch** per source vertex within reach (2.5× the contact gap); "It is a spring, not a
  weld"; works for Shell/Solid/Rod pairs; mesh edits invalidate stitches. — [snap_merge.md](https://github.com/st-tech/ppf-contact-solver/blob/main/docs/blender_addon/workflow/constraints/snap_merge.md) 2026-10 [P]
- `examples/fitting.ipynb` loads a dress "with stitching information" and a dancing body (both from Codim-IPC's assets), adds the
  stitches, and simulates 240 frames. — [fitting.ipynb](https://github.com/st-tech/ppf-contact-solver/blob/main/examples/fitting.ipynb) 2026-10 [P]
- The Blender add-on needs Blender 5.0+ and spawns a `ppf-cts-server` Rust binary. — [digitalproduction](https://digitalproduction.com/2026/05/27/zozo-contact-solver-gets-blender-add-on/), 2026-05-27 [S]
- GarmentCode (MIT) has a GUI configurator (`gui.py`) that loads body and design parameters, shows the sewing pattern "and display[s]
  draped 3D models" (drapes fitted to a neutral body); command-line draping via its Warp simulator. GarmentCodeData was accepted to
  ECCV 2024; last news entry June 2025. — [Running_garmentcode.md](https://github.com/maria-korosteleva/GarmentCode/blob/main/docs/Running_garmentcode.md), [README](https://github.com/maria-korosteleva/GarmentCode) [P]
- NVIDIA Warp (under GarmentCode's sim and Newton) "can run on the CPU or GPU"; CUDA acceleration needs an NVIDIA Turing+ GPU; macOS
  wheels are CPU only. — [Warp README](https://github.com/NVIDIA/warp) 2026-10 [P]
- Valentina is still active on GitLab: last activity 2026-10-23, 70 stars, "cross-platform
  patternmaking program". — [GitLab API](https://gitlab.com/smart-pattern/valentina) [P]
- Blender's cloth has **sewing springs**: "virtual springs that pull vertices in one part of a cloth mesh toward vertices in another part",
  made from loose edges, with a Max Sewing Force. — [manual source, cloth/settings/shape.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/physics/cloth/settings/shape.rst) [P]
- prenda3d-lab (MIT): builds garments from real factory pattern pieces, sews them on a body and simulates in Blender 5.1 (CPU, headless);
  maintained by Parka Supply Co. — [README](https://github.com/parka-oss/prenda3d-lab) 2026-10 [P]
- EXO Sample 3D (GPL-3): "experimental platform for fashion CAD, 2D patterns, 3D garments, cloth simulation"; macOS beta of "ClothCraft
  Studio V2"; "fitting physics, avatar contact, stable live cloth behavior … [not yet]". — [README](https://github.com/mikristian/exo-sample-3d), updated 2026-10-19 [P]
- Blender "Seams to Sewing Pattern" add-on forks (GPL-2.0) turn UV seams into flat printable patterns. — [GitHub search](https://github.com/goatchurchprime/blender-seams-to-sewing-pattern) 2026-02 [P, metadata only]
- Unreal 5.6: "Beta Chaos Cloth Panel Editor … Experimental Unified Dataflow Editor", Outfit Asset with resizing/refitting, cloth-to-cloth
  constraints, simulation morph targets. — [Epic forum post by gozerKeymaster](https://forums.unrealengine.com/t/2555686), 2025-06-13 [P]
- Whether Chaos Cloth runs only on the CPU: Chaos uses Intel ISPC (a CPU SIMD compiler); no source found that says Chaos Cloth uses the GPU.
  — [Intel article](https://www.intel.com/content/www/us/en/developer/articles/technical/unreal-engines-new-chaos-physics-system-screams-with-in-depth-intel-cpu-optimizations.html) [S]
- Searches for an open, interactive pattern-to-3D app turned up only listings that pair Valentina/Seamly2D with Blender. —
  [AlternativeTo](https://alternativeto.net/software/marvelous-designer/) [S]

Assessment: the cloth-solver half of a Marvelous Designer equivalent now has an open, cross-vendor, stitch-capable candidate (ZOZO), but
it is offline. The interactive 2D-panel ↔ 3D-drape editor is still not available as open code; GarmentCode's data model and GUI,
Seamly2D/Valentina's drafting, and ZOZO's or Blender's sewing are the parts.

### 1b · Fitting any garment to any body (a MetaTailor equivalent)

- LoBoFit: "expresses garment geometry as a linear blend of its mappings into local bone coordinate frames", then refines localised
  residuals to resolve collisions; handles single- and multi-layer garments "across avatars with large shape and topological
  differences". — [arXiv 2605.07450](https://arxiv.org/abs/2605.07450), 2026-05-08 [P]
- LoBoFit code: official SIGGRAPH 2026 implementation, **BSD-3-Clause**, PyTorch, uses CUDA if available else CPU; sample data on Google
  Drive; "Parts of this work may be covered by a pending Chinese patent application. This code release does not grant any … patent
  rights." 7 stars. — [MengZephyr/LoBoFit](https://github.com/MengZephyr/LoBoFit) 2026-07-04 [P]
- Unreal Outfit Asset: `ChaosSizedOutfitSource` holds per-size `source_body_parts` (skeletal meshes), `source_asset`, `size_name`, and
  `num_resizing_interpolation_points` ("distributed evenly across the entire body"); the page is "Unreal Python 5.8 (Experimental)". —
  [API page](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/ChaosSizedOutfitSource) [P]
- An Epic staff reply says MetaHuman Creator's Dataflow graph "strips out the sim mesh", so a resized outfit loses its cloth simulation in
  that path. — [forum thread](https://forums.unrealengine.com/t/intended-workflow-for-resizing-a-chaos-outfit-asset-while-preserving-cloth-simulation/2762838) [S]
- MetaHuman 5.6 outfits "can be automatically sized to fit the character's body type". — [Gigazine](https://gigazine.net/gsc_news/en/20250604-unreal-engine-5-6-metahuman), 2025-06-04 [S]
- Elastic Clothing Fit (GPL-3 Blender add-on, Blender 3.2–5.x): "Fit any clothing mesh to any body in a few clicks"; proxy-based fit,
  UV preservation, preserve groups, proximity falloff, crease smoothing, hull fit, live preview. 14 stars. — [README](https://github.com/VRC-Staples/Elastic-Clothing-Fit) 2026-10-29 [P]
- cmt `meshretarget.py` (MIT, Maya): "Retarget meshes fit on a source mesh to a modified version of the source mesh" with RBFs, e.g.
  shirt and pants from `source_body` to `new_body`; derived from PyGeM's RBF. — [file](https://github.com/chadmv/cmt/blob/master/scripts/cmt/rig/meshretarget.py) [P]
- deformxfer: header-only C++ "Deformation Transfer for Triangle Meshes", BSD-3. — [repo](https://github.com/jerenchen/deformxfer) 2021-11 [P, metadata]
- Blender's Surface Deform modifier lets "an arbitrary mesh surface … control the deformation of another" (e.g. a cloth proxy). —
  [manual source](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/modeling/modifiers/deform/surface_deform.rst) [P]
- Pattern-level refitting papers without located code: Dress Anyone (Meta, 2024; differentiable sim adjusts 2D patterns per body),
  Bolt (NVIDIA, 2025; transfer, pattern adjust, drape, rig — reportedly in Warp), Digital Garment Alteration (2024), Pixar's Garment
  Refitting (de Goes 2020). — [arXiv 2405.19148](https://arxiv.org/pdf/2405.19148), [arXiv 2504.17614](https://arxiv.org/abs/2504.17614), [Pixar PDF](https://graphics.pixar.com/library/GarmentRefit/paper.pdf) [S]
- An unofficial implementation of Pixar's refitting exists (0 stars, no licence). — [panangam/garment-refitting](https://github.com/panangam/garment-refitting) 2026-08 [P, metadata]

Assessment: the parts now cover more of the job (LoBoFit for refit, ZOZO for layered settle, robust weight transfer from round one,
MHCLO offsets), but no open tool packages them with layer ordering and auto weights. Unreal's Outfit Asset is the nearest packaged
feature among in-scope options, under the UE EULA.

### 1c · Physics tools like Cascadeur's

- Cascadeur plans: Free $0 — "Only non-commercial use", "Export to .casc format only. .fbx and .dae are not available", "300 frames per
  scene", "120 joints per scene"; eligibility text also mentions revenue "less than US $100,000.00"; Indie $8/mo annual ($19 monthly)
  with FBX/DAE and <$100k revenue; Pro $33/mo annual ($49 monthly) "Commercial use with no limits". — [cascadeur.com/plans](https://cascadeur.com/plans), undated [P]
- Ragdoll for Blender: plugin open source but practical use needs the commercial Ragdoll Core; the free version stops "the ability to
  record" after a 30-day trial. — [CG Channel](https://www.cgchannel.com/2024/03/imbalance-releases-ragdoll-for-blender-1-0), 2024-03-01; [Blender Market](https://blendermarket.com/products/ragdoll-dynamics) [S]
- Balance Point (GPL-3, Blender add-on): centre-of-mass marker and motion path; a "Ballistic Ruler" arc from start point, time of flight,
  gravity and damping; baking "conserves angular momentum from posing" using the moment-of-inertia tensor. 7 stars. — [README](https://github.com/rdat5/Balance-Point) 2026-07-19 [P]
- OpenSim (Apache-2.0) includes Moco: `MocoTrack`, `MocoInverse`, `MocoStudy` (musculoskeletal optimal control; tracking a motion makes it
  dynamically consistent). — [OpenSim/Moco source](https://github.com/opensim-org/opensim-core/tree/main/OpenSim/Moco), v4.6 2026-07-09 [P]
- MuJoCo MPC (Apache-2.0): "real-time predictive control with MuJoCo" — iLQG, gradient descent, derivative-free planners. — [README](https://github.com/google-deepmind/mujoco_mpc) 2026-10-28 [P]
- Crocoddyl (BSD-3): optimal control "for robot control under contact sequence" (DDP-like solvers). — [repo](https://github.com/loco-3d/crocoddyl) 2026-10-26 [P, metadata]
- ProtoMotions3 (Apache-2.0) now has a MuJoCo CPU back-end alongside Isaac Gym, Isaac Lab and Newton; training at scale shown on A100s;
  bundles SMPL attribution notices. — [README](https://github.com/NVlabs/ProtoMotions) 2026-10 [P]
- Unreal's PhysicsControl plugin (Experimental folder): spring-damper "controls" drive a child body relative to a parent on static or
  skeletal meshes. — [plugin index](https://dev.epicgames.com/documentation/unreal-engine/API/PluginIndex/PhysicsControl) [S]
- Searches for an open Cascadeur alternative returned only Blender (general simulation) and paid DCCs. —
  [AlternativeTo](https://www.alternativeto.net/software/cascadeur/) [S]

Assessment: still no open animator-facing tool that makes a keyframed clip physically plausible. Building blocks: MuJoCo or Jolt for
dynamics, OpenSim Moco / MJPC / Crocoddyl-style trajectory optimisation, Balance Point's behaviours as a small reference.

### 1d · A ZBrush-class sculpt library

- SculptForge (GPL-3.0-or-later, C++): "The free, open-source alternative to ZBrush"; 14 named brushes, masking, polygroups, SubTools,
  polypaint, voxel remesh, QRemesh quad retopology with ProjectAll, sculpt layers as blend shapes, FBX/glTF/USD export; created
  2026-10-21, v0.9.3 on 2026-10-29, 12 stars; uses ufbx and xatlas. — [README](https://github.com/islandmed/SculptForge) [P]
- BrokkrSculpt (AGPL-3.0, Rust/wgpu): voxel/SDF "solid material" sculpting aimed at 3D printing; eight brushes. — [README](https://github.com/MakerViking/brokkrsculpt) created 2026-08-26 [P]
- Rooms (MIT, C++ on the MIT `wgpuEngine`): VR SDF sculpting with sparse SDF storage, layers, PBR paint, skeletal animation editing;
  paper in IEEE Computer Graphics and Applications (2026). — [README](https://github.com/upf-gti/rooms) 2026-09 [P]
- ArmorPaint has a sculpt tool type with draw, grab, inflate, flatten, clay, pinch, crease, cloth, twist, stretch, trim, plateau; the
  manual labels the sculpt workflow "work-in-progress". — [enums.h](https://github.com/armory3d/armorpaint/blob/main/paint/sources/enums.h) [P];
  [manual](https://armorpaint.org/manual) [P]
- Dilay (GPL-3) last pushed 2018-08. — [repo](https://github.com/abau/dilay) [P, metadata]
- Blender dynamic topology lives in `source/blender/editors/sculpt_paint/mesh/sculpt_dyntopo.cc`; the manual documents Detail Size,
  Refine Method (subdivide, collapse, both) and Relative/Constant/Brush/Manual detailing. — [code search](https://github.com/blender/blender/tree/main/source/blender/editors/sculpt_paint/mesh) [P];
  [dyntopo.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/sculpt_paint/sculpting/tool_settings/dyntopo.rst) [P]
- Searches for a 2026 open ZBrush alternative returned Blender, Dilay and SculptGL only. — [AlternativeTo](https://www.alternativeto.net/software/zbrush/) [S]

Assessment: no library to embed; SculptForge (GPL, eight days old) is a reference app, not a dependency. Our own sculpt core on OpenVDB plus a mesh kernel stays the route.

### 1e · A texture baker

- ArmorPaint bake types: curvature, normal, object normal, height, derivative, position, texcoord, material ID, object ID, vertex colour,
  occlusion, lightmap, bent normal, thickness. — [enums.h](https://github.com/armory3d/armorpaint/blob/main/paint/sources/enums.h) [P]
- ArmorPaint ray-traced bake shaders: `raytrace_bake_ao/bent/thick/light` in shader source and `.metal` versions; `make_bake.c` notes
  "Baked high-poly normals" and "Baked high-poly positions". — [code search, repo](https://github.com/armory3d/armorpaint/tree/main/base/shaders/raytrace) 2026-10 [P]
- ArmorPaint manual: AO, lightmap, bent normal and thickness need "raytracing GPUs"; normal, height and derivative bake "from high-poly
  mesh"; no documented cage. — [manual](https://armorpaint.org/manual) [P]
- ArmorPaint licence: zlib for the source; "Distributed binaries are paid". — [license.md](https://github.com/armory3d/armorpaint/blob/main/license.md), [readme](https://github.com/armory3d/armorpaint) [P]
- Unreal Geometry Script bake types (14, listed in Top finding 3). Whether these run in a packaged (non-editor) app was not checked. —
  [UE Python 5.8](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/GeometryScriptBakeTypes) [P]
- xNormal: free, version 3.19.3c, Windows 7–11 only, DirectX 10 GPU; licence for commercial use not stated on the site. — [xnormal.net](https://xnormal.net/) undated [P]
- Fornos: GPU bakers for height, normals, AO, bent normals, thickness; no licence file; last push 2018-12. — [repo](https://github.com/caosdoar/Fornos) [P]
- BakeForge: described by its author as a free, open-source GPU baker with cage projection; no repository found. — [LinkedIn](https://ru.linkedin.com/in/anton-murashkin) [S]
- Blender's Cycles baking (GPL app) remains the reference workflow with cage and extrusion. — [Blender manual](https://docs.blender.org/manual/ja/4.5/render/cycles/baking.html) [S]

Assessment: ArmorPaint's baker is the strongest open, permissively licensed code (zlib), but it is part of an app, has no documented
cage, and its ray-traced bakes need RT-capable GPUs.

### 1f · An FBX writer

- `ufbx_write`: creators for scene, node, mesh, material, texture, camera, light, bone, bind pose, skin deformer/cluster, blend
  deformer/channel/shape, anim stack/layer/curve, cache deformer; saves `UFBXW_SAVE_FORMAT_BINARY` (version 7500) or ASCII; no
  OS-specific code; optional C++11 threading. — [README](https://github.com/ufbx/ufbx-write), [ufbx_write.h](https://github.com/ufbx/ufbx-write/blob/main/ufbx_write.h) [P]
- `ufbx_write` licence: MIT or public domain (Unlicense), "choose whichever you prefer"; created 2025-06-22; 21 stars; no tags or releases. — same [P]
- Assimp's FBX exporter writes skin deformers ("Skin", "Cluster"), blend shapes ("BlendShape", "BlendShapeChannel") and AnimationStacks,
  with TODOs such as "this won't work if anything is not in the bind pose" and "Multilayer textures not supported". —
  [FBXExporter.cpp](https://github.com/assimp/assimp/blob/master/code/AssetLib/FBX/FBXExporter.cpp) master [P]
- Blender's FBX exporter (`io_scene_fbx`, v5.15.0) is Python under GPL-2.0-or-later and writes BlendShape/BlendShapeChannel deformers and
  AnimationStacks. — [addons_core/io_scene_fbx](https://github.com/blender/blender/tree/main/scripts/addons_core/io_scene_fbx) [P]
- fbxcel (Rust, Apache-2.0 per GitHub) has a low-level `writer` module; v0.9.0. — [repo](https://github.com/lo48576/fbxcel) 2026-04 [P]
- FbxWriter (.NET reader/writer) has no licence; last push 2022-10. — [repo](https://github.com/hamish-milne/FbxWriter) [P, metadata]

Assessment: the open writer gap is closed on paper by `ufbx_write` (same author and licence as the reader Blender uses), but it is
pre-release; a round-trip test against Maya/Unreal/Blender importers would be needed before relying on it.

### 1g · A cross-vendor GPU garment-cloth library

- ZOZO's Contact Solver — see 1a (CUDA, ROCm, Metal, CPU; offline). [P]
- Genesis: PBD cloth demo (`pbd_cloth.py`) and cloth-on-rigid coupling; its Quadrants compiler lowers Python kernels "to CUDA, AMD ROCm,
  Apple Metal, Vulkan, x86, and ARM64"; Genesis's IPC path uses libuipc (CUDA). — [README](https://github.com/Genesis-Embodied-AI/genesis-world) 2026-10 [P]
- Quadrants (Apache-2.0) was "forked from Taichi in June 2025. As the original Taichi is no longer being maintained…". Taichi's last
  release is v1.7.4 (2025-07-31). — [Quadrants README](https://github.com/Genesis-Embodied-AI/quadrants) [P]; [Taichi releases](https://github.com/taichi-dev/taichi/releases) [P]
- AVBD reference code (MIT): 2D (818 stars) and 3D (155) demos by the paper's first author; three-avbd (WebGPU, rigid bodies, "ragdolls
  on cloth, … a flag in the wind"); webphysics (WebGPU, "experimental"); Houdini-VBD (OpenCL port for Houdini). — [avbd-demo3d](https://github.com/savant117/avbd-demo3d), [three-avbd](https://github.com/sbobyn/three-avbd), [webphysics](https://github.com/jure/webphysics), [Houdini-VBD](https://github.com/MysteryPancake/Houdini-VBD) 2026 [P]
- XRTailor (OpenXRLab, Apache-2.0): GPU cloth engine with a real-time "Swift Mode"; "runs on Windows and Linux systems that support CUDA";
  SMPL/AMASS integration. — [README](https://github.com/openxrlab/xrtailor) 2025-11 [P]
- Jolt v5.6.0's GPU compute layer (DX12, Vulkan, Metal, CPU) is used for hair only; soft bodies (usable as cloth) remain CPU. —
  [ReleaseNotes.md](https://github.com/jrouwe/JoltPhysics/blob/master/Docs/ReleaseNotes.md) [P]
- Newton: "macOS (CPU only)"; CUDA needs an NVIDIA Turing+ GPU and driver R580+. — [README](https://github.com/newton-physics/newton) v1.7.0, 2026-10-14 [P]
- Small WebGPU/Vulkan XPBD cloth demos exist (e.g. steampower33/XPBD-Cloth, MIT, Vulkan compute; jspdown/cloth, MIT, WebGPU). — [GitHub search](https://github.com/steampower33/XPBD-Cloth) [P, metadata]

Assessment: one real candidate (ZOZO, offline); for real-time garment cloth across vendors, the route is still our own XPBD/AVBD on a
compute layer (Jolt's, wgpu, or Quadrants), with AVBD's MIT reference code as the starting point.

---

## 2 · VRAM needs

- **SAM 3D Body:** no official figure. A commenter who says he works with both models: "For most images, 24 GB might be sufficient. But I
  have seen certain inputs push memory usage above 24 GB." — [issue #136](https://github.com/facebookresearch/sam-3d-body/issues/136), 2026-08-05 [P]
- SAM 3D Body: a community CPU-offload fork reports peak VRAM "around 6.5 Gb" with a speed trade-off. — [issue #130](https://github.com/facebookresearch/sam-3d-body/issues/130), 2026-04-29 [P]
- **SAM 3D Objects:** "A linux 64-bits architecture" and "A NVIDIA GPU with at least 32 Gb of VRAM". — [doc/setup.md](https://github.com/facebookresearch/sam-3d-objects/blob/main/doc/setup.md) [P]
- **Stable3DGen (Hi3DGen):** OOM reported on RTX 4060 8 GB and 3060 12 GB; one user ran it on an RTX 2060 6 GB laptop with 64 GB RAM;
  a community script runs it on an 8 GB GTX 1070-class card by unloading to RAM ("approximately 26 GB required"); maintainers said in
  2025-04 they were "optimizing … to work with 12GB VRAM". — [#26](https://github.com/Stable-X/Stable3DGen/issues/26), [#55](https://github.com/Stable-X/Stable3DGen/issues/55), [#6](https://github.com/Stable-X/Stable3DGen/issues/6) [P]
- **Step1X-3D:** geometry+texture 27 GB (label variant 29 GB), 152 s for 50 steps. — [README](https://github.com/stepfun-ai/Step1X-3D) [P]
- **Puppeteer:** collaborator: rigging can be tested on a 3070 (8 GB) "but it may not be sufficient for running the animation part"; an
  open PR adds options for ≤12 GB cards (tested on a 4070 Ti). — [#7](https://github.com/Seed3D/Puppeteer/issues/7) 2025-09-22, [#26](https://github.com/Seed3D/Puppeteer/pull/26) 2026-07-23 [P]
- **MagicArticulate:** inference VRAM not stated; training on 8×A100 for ~2 days. — [README](https://github.com/Seed3D/MagicArticulate) [P]; [CVPR 2025 supplemental](https://openaccess.thecvf.com/content/CVPR2025/supplemental/Song_MagicArticulate_Make_Your_CVPR_2025_supplemental.pdf) [S]
- **Make-It-Animatable:** inference VRAM not stated; training settings "for training on A100 80G"; paper (CVPR 2025) claims under a
  second per character. — [README](https://github.com/jasongzy/Make-It-Animatable) [P]; [arXiv 2411.18197](https://arxiv.org/abs/2411.18197) [P]
- **WHAM:** owner: "I think it was 9GB to run 20 seconds demo". — [#93](https://github.com/yohanshin/WHAM/issues/93), 2024-06-04 [P]
- **GVHMR:** user report: "it requires 6gb vram". — [#13](https://github.com/zju3dv/GVHMR/issues/13), 2024-09-17 [P]
- **NLF:** owner used a 24 GB 3090, "but a smaller GPU would also be enough, depending on batch size". — [#13](https://github.com/isarandi/nlf/issues/13), 2025-03-28 [P]
- **GENMO / GEM:** not stated in README or issues (none filed); install uses cu124 wheels. — [README](https://github.com/NVlabs/GENMO) [P]
- **MoMask:** "The WebUI demo … is now running smoothly on a CPU. No GPU is required". — [README](https://github.com/EricGuo5513/momask-codes) 2024-08-02 [P]
- **MDM:** "CUDA capable GPU (one is enough)"; a user reports generation working on a MacBook via MPS. — [README](https://github.com/GuyTevet/motion-diffusion-model) [P]; [#213 title](https://github.com/GuyTevet/motion-diffusion-model/issues/213) [P]
- **T2M-GPT:** training "in a single GPU V100-32G"; inference VRAM not stated. — [README](https://github.com/Mael-zys/T2M-GPT) [P]
- **ChatGarment:** one reply: "至少15G" (at least 15 GB) for image-to-mesh inference. — [#25](https://github.com/biansy000/ChatGarment/issues/25), 2026-01-22 [P]
- **DiffLocks:** not stated (README needs custom CUDA kernels and NATTEN; no VRAM issue filed). — [README](https://github.com/Meshcapade/difflocks) [P]
- **Pixal3D:** "depending on settings 18-36 gb vram" (user); low-VRAM mode merged (default 1024 instead of 1536); a user patch peaks
  "around 11GB" at 1024 and ran on a 6 GB laptop GPU with system-memory fallback. — [#7](https://github.com/TencentARC/Pixal3D/issues/7), 2026-05 [P]; [README](https://github.com/TencentARC/Pixal3D) [P]
- **BPT:** "~12GB VRAM to run with fp16", ~2 min per mesh. — [README](https://github.com/Tencent-Hunyuan/bpt) [P]
- **SkinTokens (reference):** "An NVIDIA GPU with at least 14 GB of memory". — [README](https://github.com/VAST-AI-Research/SkinTokens) [P]
- **Hunyuan3D-2 Turbo on AMD:** ran end-to-end on a Radeon Pro W5500 with 8 GB (ROCm 7.2). — [#373](https://github.com/Tencent-Hunyuan/Hunyuan3D-2/issues/373), 2026-08-25 [P]

Assessment: on the 8 GB card, the newly sourced models that fit are GVHMR, Puppeteer's rigging stage, MoMask/MDM/T2M-GPT-class motion
models, SAM 3D Body only through community offload, and Stable3DGen/Pixal3D only with system-RAM offload. SAM 3D Objects, Step1X-3D,
ChatGarment and Hi3D do not fit.

## 3 · GPU vendors for the PyTorch models

- **TRELLIS.2 (reference):** a user lists hard CUDA-only blockers "(flash-attn, CuMesh, FlexGEMM, nvdiffrast)"; community ROCm ports
  (Strix Halo on ROCm 7.2; MI308X), a CUDA-free Triton sparse library, and MPS/MLX experiments ("produces scrambled output"). —
  [issue #74](https://github.com/microsoft/TRELLIS.2/issues/74), 2026-01 to 2026-04 [P]
- **TRELLIS.2 via trellis.cpp:** CUDA, ROCm, Vulkan, Metal, CPU fallback (see Top finding 5). On Strix Halo "Vulkan is the fastest
  backend"; 1024-res light input 6:09 on Strix Halo iGPU (Vulkan) vs 3:16 on an RTX 5060 Ti. — [README](https://github.com/pwilkin/trellis.cpp) [P]
- **TRELLIS.2 / Pixal3D via ComfyUI native:** pure-PyTorch sparse convolution (`flexgemm.py` imports only torch); runs wherever ComfyUI's
  PyTorch back-end runs — not verified on AMD or Apple by any source read. — [comfy/ldm/trellis2](https://github.com/Comfy-Org/ComfyUI/tree/master/comfy/ldm/trellis2) [P]
- **TRELLIS (v1):** open issues for an Apple Silicon MPS port reference (#359), AMD RX 480/580 (#98), DirectML (#244) and an SDPA back-end
  without flash-attn (#357). — [issues](https://github.com/microsoft/TRELLIS/issues) [P, titles]
- **TripoSG:** open PR to run on AMD (RX 6700 XT 12 GB) by making `diso` optional; open MPS PRs (#44, #66). — [#70](https://github.com/VAST-AI-Research/TripoSG/pull/70), 2026-10-17 [P]
- **PartCrafter:** "runs out of the box on ROCm — no patches" (RDNA4, ROCm 7.2.1); an earlier MPS attempt gave nonsense output (closed). —
  [#45](https://github.com/wgsxm/PartCrafter/issues/45), 2026-08-09; [#25](https://github.com/wgsxm/PartCrafter/issues/25) [P]
- **UniRig:** install needs CUDA builds of spconv, torch_scatter, torch_cluster. ONNX exports of the skeleton stage exist (QtMeshEditor,
  WebGPU int8). — [README](https://github.com/VAST-AI-Research/UniRig) [P]; [QtMeshEditor card](https://huggingface.co/fernandotonon/QtMeshEditor-unirig-onnx) 2026-07-10 [P]
- **SkinTokens:** reference needs NVIDIA ≥14 GB, CUDA ≥12.1, flash-attn; open PR for ROCm and CPU (#14); `skin-tokens.cpp` CPU/Vulkan;
  Swift-MLX port for Apple. — [README](https://github.com/VAST-AI-Research/SkinTokens), [#14](https://github.com/VAST-AI-Research/SkinTokens/pull/14) 2026-10-11, [MLX card](https://huggingface.co/mlx-community/SkinTokens-bf16) [P]
- **Audio2Face-3D:** model card: "Acceleration Engine: TensorRT", optimised for NVIDIA; the repo ships `network.onnx`, `trt_info.json`;
  MLX port of v2.3 (272 skin + 10 tongue blendshapes, 15 jaw and 4 eye controls per frame). — [card](https://huggingface.co/nvidia/Audio2Face-3D-v3.0), [MLX](https://huggingface.co/aufklarer/Audio2Face-3D-v2.3-Mark-MLX) [P]
- **Hunyuan3D-2:** README: "supports Macos, Windows, Linux"; AMD ROCm report on 8 GB (above); a Swift-MLX port claim (#367, title only). —
  [README](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) [P]
- **Stable Fast 3D:** MPS tested on M1 Max 64 GB; "We recommend running the CPU version if your system has less than 32GB of unified
  memory". — [README](https://github.com/Stability-AI/stable-fast-3d) [P]
- **TripoSR:** ONNX exports including WebGPU (`cgb/triposr-onnx-webgpu`, MIT); MPS PR open (#155). — [HF search](https://huggingface.co/models?search=triposr-onnx) [P]; [#155](https://github.com/VAST-AI-Research/TripoSR/pull/155) [P]
- **SAM 3D Body:** MHR TorchScript fails on MPS (#93); an MPS back-end PR is open (#125). — [issues](https://github.com/facebookresearch/sam-3d-body/issues) [P, titles]
- **Pixal3D:** MPS PR open (#35); otherwise follows TRELLIS.2's CUDA install. — [README](https://github.com/TencentARC/Pixal3D) [P]
- **Hi3D v1.0:** NVIDIA compute capability ≥8.0 and CUDA 12.0–12.5 only; "There is no CPU inference path"; flash-attn "has no fallback". — [README](https://github.com/hi3d-official/Hi3Dv1.0) [P]
- **Others stated in READMEs:** Step1X-3D checked on CUDA 12.4; Puppeteer CUDA 11.8; MagicArticulate cu118 wheels; Stable3DGen
  spconv-cu builds; GENMO cu124. [P]

Assessment: label TRELLIS.2, SkinTokens and UniRig's skeleton stage "NVIDIA; AMD/Intel/Apple via community C++/ONNX/MLX ports";
PartCrafter and Hunyuan3D-2 "NVIDIA; AMD reported working"; the rest "NVIDIA (CUDA)".

## 4 · CMU mocap terms; Blender's dynamic topology and hair-curve grooming

- mocap.cs.cmu.edu could not be read: "unable to verify the first certificate" (not worked around). — fetch attempt 2026-10-29
- The 2008 cgspeed BVH conversion README quotes the site: "This data is free for use in research and commercial projects worldwide",
  requests citation and the acknowledgment "The data used in this project was obtained from mocap.cs.cmu.edu. The database was created
  with funding from NSF EIA-0196217"; the converter adds "no additional restrictions". — [copy in Assimp's test data](https://github.com/assimp/assimp/blob/master/test/models/BVH/01_nn.bvh.source.txt), 2008-07-20 [P]
- A later wording quoted by other projects: "You may include this data in commercially-sold products, but you may not resell this data
  directly, even in converted form." — [tsseg data README](https://github.com/fchavelli/tsseg/blob/main/tsseg/data/README.md) [P, secondary copy];
  [QtMeshEditor THIRD_PARTY_AI_MODELS.md](https://github.com/fernandotonon/QtMeshEditor/blob/master/THIRD_PARTY_AI_MODELS.md) [P, secondary]
- Blender dynamic topology: see 1d. [P]
- Blender Curves Sculpt mode "is commonly used for hair grooming"; brushes: Add, Comb, Cut, Delete, Density, Grow/Shrink, Pinch, Puff,
  Slide, Smooth, Snake Hook, Selection Paint; curves attach to a surface mesh ("Snap to Deformed/Nearest Surface"). — [curves_sculpting/introduction.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/sculpt_paint/curves_sculpting/introduction.rst) [P]
- Blender's hair node groups: deformation (blend, displace, frizz, noise, roll, rotate, shrinkwrap, smooth, straighten, trim), generation
  (duplicate, generate, interpolate), guides (braid, clump, curl, guide index map), utility (attach to surface, redistribute points,
  restore segment length), read and write nodes. — [manual tree geometry_nodes/hair](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/modeling/geometry_nodes/hair) [P]

Assessment: CMU data is usable in a commercial app's built-in library by both wordings, but shipping the raw clips as a downloadable
pack could count as resale under the later wording; the primary page stays unread.

## 5 · Free-but-closed terms

- **Autodesk FBX SDK 2020:** see Top finding 11 (§1.1, 1.1.3, 1.1.5, 2.1.1(e)(i)(j), 2.1.5, 3; Exhibit A §21 defines Open Source to
  include GPL and LGPL). The agreement states no royalty for redistribution. — [SideFX copy](https://www.sidefx.com/docs/houdini/licenses/fbx.html) [P]; also hosted by [Unity](https://unity.com/legal/autodesk-fbx) [S]
- **Mixamo:** Additional Terms (see Top finding 10) are "incorporated into the Adobe General Terms of Use". The 2022 FAQ (round one) still
  describes royalty-free use and no redistribution of raw files. helpx.adobe.com's Mixamo FAQ returned HTTP 403. — [PDF](https://wwwimages2.adobe.com/content/dam/cc/en/legal/servicetou/Mixamo-Addl-Terms-en_US-20210623.pdf) [P]
- **Live Link Face (iOS):** free; seller Epic Games International S.à r.l.; v1.7.3 (Aug 26, year not shown); iOS/iPadOS 16+; MetaHuman
  Animator needs iPhone 12+ and a Windows PC; streams "ARKit animation data live to an Unreal Engine instance via Live Link over a
  network"; OSC remote control; the "License Agreement" link on the page points nowhere ("#"). — [App Store](https://apps.apple.com/us/app/live-link-face/id1495370836) [P]
- Live Link Face for Android: beta since June 2025; Snapdragon 8 Gen 1 or newer. — [Epic docs](https://dev.epicgames.com/documentation/metahuman/installing-live-link-face-on-android) [S]; [CG Channel](https://www.cgchannel.com/?p=167678) 2025-06-08 [S]
- Non-Unreal receivers exist: Blender add-ons decoding Live Link Face's stream (GPL-3, 89 stars; MIT, 21 stars). — [shun126/livelinkface_arkit_receiver](https://github.com/shun126/livelinkface_arkit_receiver), [nmfisher/blender_livelinkface](https://github.com/nmfisher/blender_livelinkface) [P, metadata]
- **Rokoko Studio Starter (free):** recording and FBX export with clean-up filters; 3 simultaneous actors; Rokoko Create: 30 s/month of
  video AI, unlimited text-to-motion clips; 1 day offline. Not in Starter: custom characters and retargeting to custom meshes, BVH export,
  **live streaming to third-party tools (Plus and up)**, face capture/CSV (Pro). Plus $20/mo annual, Pro $50/mo annual (the page's
  summary cards conflict). Commercial-use wording: none on the page. — [rokoko.com/pricing](https://www.rokoko.com/pricing), undated [P]
- **Cascadeur free:** see 1c. [P]

## 6 · Licences to resolve

- **Rokoko Studio Live for Blender:** `LICENSE.md` is "GNU LESSER GENERAL PUBLIC LICENSE Version 3", added 2020-01-23 and the only
  licence file; the current README (rewritten 2025-06-13 and 2025-06-17) shows an MIT badge that links to that same LICENSE. — [LICENSE.md](https://github.com/Rokoko/rokoko-studio-live-blender/blob/master/LICENSE.md), commit history [P]
  - Assessment: the licence file governs; the badge looks like an error. Label it LGPL-3.0, with the conflict noted.
- **Rhubarb Lip Sync:** "released under the MIT license. All its third-party dependencies … MIT …, BSD … or similar permissive"; output
  data "belongs to you alone". — [LICENSE.md](https://github.com/DanielSWolf/rhubarb-lip-sync/blob/master/LICENSE.md) [P]
- **XR Animator:** "License (CC BY-NC-SA 4.0) … applies if you are adapting XR Animator's source code"; it does not apply to content
  generated with it. — [readme.md](https://github.com/ButzYung/SystemAnimatorOnline) [P]
- **CameraHMR:** no licence file, no licence text in `ReadMe.md`. — [repo](https://github.com/pixelite1201/CameraHMR) 2025-11 [P]
- **DressCode:** no licence file; README gives SIGGRAPH 2024 (TOG) but no licence. — [repo](https://github.com/IHe-KaiI/DressCode) [P]
- **MotionGPT3:** README: "distributed under an [MIT LICENSE](LICENSE)", but `LICENSE` returns 404; depends on SMPL/SMPL-X. — [README](https://github.com/OpenMotionLab/MotionGPT3) [P]
- **Noitom MocapApi:** no licence file; README describes C/C++/C#/Python over Axis Studio's UDP/TCP stream; repo ships `bin`/`lib`. — [repo](https://github.com/pnmocap/MocapApi) 2026-07 [P]
- **lightmapper (ands):** "This software is in the public domain. Where that dedication is not recognized, you are granted a perpetual,
  irrevocable license to copy and modify this file however you want." — [lightmapper.h](https://github.com/ands/lightmapper/blob/master/lightmapper.h) [P]
- **VRM specification:** no licence file in the repo; neither the README nor `specification/VRMC_vrm-1.0/README.md` states one. — [repo](https://github.com/vrm-c/vrm-specification) 2026-10 [P]
- **CGAL 6.2.1:** foundation-layer packages LGPL (algebraic foundations, number types, kernels, 2D polygons, halfedge DS, combinatorial
  and generalized maps, linear cell complex, surface subdivision); Polygon Mesh Processing, booleans, remeshing, repair, Surface Mesh,
  simplification, parameterisation, alpha wrapping, 3D mesh generation, tetrahedral remeshing all GPL; commercial licences from
  GeometryFactory. — [license.html](https://doc.cgal.org/latest/Manual/license.html), [packages.html](https://doc.cgal.org/latest/Manual/packages.html) [P]
- **KTX-Software:** "Files unique to this repository generally fall under the Apache 2.0 license"; REUSE-compliant; exception
  `external/etcdec/etcdec.cxx` "is not open source" (Ericsson licence), omitted with `LIBKTX_FEATURE_ETC_UNPACK=NO`. — [LICENSE.md](https://github.com/KhronosGroup/KTX-Software/blob/main/LICENSE.md) [P]

## 7 · Algorithms and papers

- **VBD (Vertex Block Descent):** Chen, Liu, Yang, Yuksel, ACM TOG 43(4) (SIGGRAPH 2024): block coordinate descent on the variational
  form of implicit Euler, vertex-level Gauss-Seidel; "unconditional stability"; iteration count can be capped to a budget; code in Gaia.
  — [project page](https://graphics.cs.utah.edu/research/projects/vbd/) [P]
- Gaia (Apache-2.0, C++): standalone VBD and XPBD simulators; needs TBB, Eigen, Embree 3; tested on Windows/Visual Studio only. —
  [README](https://github.com/AnkaChan/Gaia) 2025-10 [P]
- **AVBD (Augmented VBD):** Giles, Diaz, Yuksel, ACM TOG 44(4) (SIGGRAPH 2025): augmented Lagrangian adds hard constraints "with
  infinite stiffness", high stiffness ratios, joints with limited DOF, stacking and friction; parallel GPU implementation, "millions of
  objects". — [project page](https://graphics.cs.utah.edu/research/projects/avbd/) [P]; open code in 1g [P]
- **XPBD:** Macklin, Müller, Chentanez, MIG 2016: removes PBD's dependence of stiffness on iteration count and time step; gives
  constraint-force estimates. — [DiffXPBD background, arXiv 2301.01396](https://arxiv.org/html/2301.01396v3) [S]; [IPSJ report](https://ipsj.ixsq.nii.ac.jp/record/183598/files/IPSJ-CG17167010.pdf) [S]
- XPBD is patented by NVIDIA (US11270041, inventors Macklin, Müller, Chentanez). — [Google Patents](https://patents.google.com/patent/US11270041) [S]
- Open XPBD code: PositionBasedDynamics (MIT) lists PBD & XPBD distance, bending and volume constraints plus Cosserat and stiff-rod
  solvers. — [README](https://github.com/InteractiveComputerGraphics/PositionBasedDynamics) [P]
- **Stable Cosserat Rods:** Hsu, Wang, Wu, Yuksel, SIGGRAPH 2025: hair, trees, yarn-level cloth; "orders of magnitude faster and more
  stable" than XPBD and discrete elastic rods; 1,464,704 hair vertices in 7 ms/frame on an RTX 3090. — [project page](https://graphics.cs.utah.edu/research/projects/stable-cosserat-rods/) [P]
- Its code: YarnBall (GPL-3, CUDA 12.8, tested on RTX 2080 with `sm_75`) and a CPU StableCosseratRods repo (MIT). — [YarnBall](https://github.com/jerry060599/YarnBall), [StableCosseratRods](https://github.com/jerry060599/StableCosseratRods) [P]
- Also from the same lab: "Real-Time Hair Rendering with Hair Meshes" (SIGGRAPH 2024), "Real-Time Physically Guided Hair Interpolation"
  (TOG 2024), "Game-Ready Hair in Minutes!" (SIGGRAPH 2026 Real-Time Live!). — [Yuksel research page](https://www.cemyuksel.com/research/) [P]
- **PSD / RBF correctives:** Lewis, Cordner, Fong, "Pose space deformation: a unified approach to shape interpolation and skeleton-driven
  deformation", SIGGRAPH 2000 — maps a pose space to displacements in local frames; Academy Technical Achievement Award 2013. —
  [PDF](https://www.scribblethink.org/Work/PSD/PSD.pdf) [S]; [SIGGRAPH history](https://history.siggraph.org/?p=118265) [S]
- Open RBF code: cmt `rbfNode` (MIT, Maya C++); weightDriver (Ingo Clemens) repo "discontinued", source now sold on Gumroad. —
  [cmt/src](https://github.com/chadmv/cmt/tree/master/src) [P]; [weightDriver](https://github.com/IngoClemens/weightDriver) [P]
- Houdini has a Pose Space Deform SOP (RBF). — [SideFX forum](https://www.sidefx.com/forum/topic/86079) [S]
- **Jimenez eye rendering:** "Separable Subsurface Scattering and Photorealistic Eyes Rendering" (SIGGRAPH 2012 Advances course, slides
  212.7 MB) and "Next Generation Character Rendering" (GDC 2013, slides 323.6 MB; eyes on slides 229–231 per a forum post). Slides not
  opened (size); topics (refraction, parallax, caustics) not confirmed. — [iryoku.com](https://www.iryoku.com/author/iryoku/) [P];
  [Unity forum](https://discussions.unity.com/t/eye-shader-physically-based-refraction-source-code/646027) [S]

Assessment, per item, for JustStage: VBD/AVBD → the cloth and soft-body solver core (MIT/Apache references, GPU-parallel, cross-vendor if
we write the kernels); XPBD → simplest fallback, patent noted; Stable Cosserat Rods → strand hair/yarn (GPL/MIT code, CUDA); PSD/RBF →
body correctives (technique, plus MIT RBF node as reference); Jimenez → eye shader reference (no code).

## 8 · Items not checked in round one

### Neural retopology
- DeepMesh (ICCV 2025): repo licence Apache-2.0 per GitHub, README badge MIT, HF weights tagged MIT; tested on A100/A800/A6000. — [repo](https://github.com/zhaorw02/DeepMesh) 2025-12 [P]
- BPT ("Scaling Mesh Generation via Compressive Tokenization", CVPR 2025, >8k faces): repo LICENSE is the **Tencent Hunyuan 3D 2.0
  Community License** ("DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA"); HF weights tagged MIT — conflict; ~12 GB. —
  [repo](https://github.com/Tencent-Hunyuan/bpt) 2025-07 [P]; [HF](https://huggingface.co/whaohan/bpt) [P]
- QuadGPT (native quad generation, ICLR 2026, HKUST/Tencent Hunyuan): no code or weights found. — [arXiv 2509.21420](https://arxiv.org/abs/2509.21420v2) [S]; GitHub search [P]
- Meshtron (NVIDIA): no official code; one unofficial MIT re-implementation (14 stars). — [repo](https://github.com/GauravPatil8/Nvidia-Meshtron-Pytorch) [P, metadata]
- Others: FastMesh (3DV 2026) — S-Lab License 1.0, non-commercial [P]; Mesh-RFT (NeurIPS 2025) — MIT [P]; MeshRipple (CVPR 2026) — no
  licence file [P]; Nautilus (ICCV 2025) — no licence, 3–4 min per 5,000-face mesh on an A100 [P]. — repos via GitHub API

### Hi3D v1.0
- See Top finding 13; trained on ~2M assets; 512/1024/1536 resolutions; geometry only, batch size one. — [README](https://github.com/hi3d-official/Hi3Dv1.0), [LICENSE](https://github.com/hi3d-official/Hi3Dv1.0/blob/main/LICENSE) [P]; [press](https://technode.global/?p=995995) 2026-10-23 [S]

### Sony mocopi and VMC
- mocopi app transfer formats seen: "mocopi (UDP)", default port 12351, IPv4 only, unencrypted; "VRChat (OSC)", default port 9000. —
  [tech spec](https://xyn.sony.net/en/developer/technical/mocopi/techspec) [P]; [help guide](https://helpguide.sony.net/mobile/qm-ss1/v1/en/contents/external-device-settings.html) [P]
- mocopi skeleton: joint table indices 0–26 (27 joints). — [tech spec](https://xyn.sony.net/en/developer/technical/mocopi/techspec) [P]
- Receiver plugins for Unity, MotionBuilder, Unreal, Maya and Blender; a Mobile SDK (Android/iOS, corporate); separate commercial licence
  page; the developer site "has been migrated to the XYN website". VMC output from the mocopi app: not found in Sony's pages. —
  [mocopi-dev](https://www.sony.co.jp/en/Products/mocopi-dev/en/) [P]
- The mocopi link iPhone app is slated for discontinuation in October 2026. — [search result](https://www.provideocoalition.com/sony-updates-mocopi-motion-capture-device-adds-app-for-pc/amp/) [S]

### OptiTrack NatNet and Vicon DataStream SDKs
- NatNet: free SDK; a developer forum thread asking about redistribution licence got no written answer; NaturalPoint staff said Linux was
  not directly supported. optitrack.com returned HTTP 429 (not retried around). — [forum](https://forums.naturalpoint.com/viewtopic.php?p=65496) [S]; [docs index](https://docs.optitrack.com/developer-tools/natnet-sdk) lists NatNet 4.5 [P]
- Vicon DataStream SDK: source "licensed under an MIT license agreement"; v1.13.0; Windows 64-bit, Linux, macOS 10.15+ (Apple Silicon);
  C++, .NET, Python, MATLAB, LabVIEW; Unity/Unreal plugins; requires a Vicon system (Tracker, Nexus, Shogun, Evoke) or the Vicon Virtual
  System; "free for existing customers". — [vicon.com](https://www.vicon.com/software/datastream-sdk/) [P]

### Live Link plugin terms
- Not read. Live Link is an Unreal Engine plugin; its terms are the UE EULA (§S5's subject). — no source read

### TressFX 5.0
- TressFX 5.0 for UE 5.4 (posted 2025-08-04): Lumen software/hardware RT, deep shadow approximation, continuous LOD; patch available only
  to "registered Unreal Engine developer[s]" via AMD's fork; UE 5.5+ "in a future update"; no standalone TressFX 5 SDK mentioned; the
  page states no licence (GPUOpen lists TressFX as MIT [S]). — [GPUOpen](https://gpuopen.com/learn/tressfx-5-0-unreal-engine-5-update/) [P]

### Godot IK in stable
- `TwoBoneIK3D`, `FABRIK3D`, `CCDIK3D`, `JacobianIK3D`, `SplineIK3D`, `IKModifier3D`, `ChainIK3D` class docs exist at tag 4.6-stable
  (released 2026-01-26), not at 4.5-stable; `LookAtModifier3D`, `RetargetModifier3D`, `SpringBoneSimulator3D` are already in 4.5-stable
  (2025-09-15). Current stable is 4.7.2 (2026-08-18). — [godot doc/classes at tags](https://github.com/godotengine/godot/tree/4.6-stable/doc/classes) [P]

### MoonRay GPU back-ends
- Build instructions: GPU/XPU support optional, CUDA libraries on Linux; "MoonRay now also builds on macOS Apple silicon systems and can
  leverage the unified memory architecture for XPU mode"; no AMD path found. — [general_build.md](https://github.com/OpenMoonRay/openmoonray/blob/main/building/general_build.md) [P]

### PhysX CPU/GPU split
- GPU simulation "supports the entire rigid body feature-set including articulations"; GPU-only: FEM soft bodies ("requires GPU
  acceleration"), PBD particles, SDF mesh collision (CPU falls back to triangle mesh); not on GPU: custom geometry, scene queries,
  contact modification, joint projection, CCD, triggers, non-D6 joint shaders; needs CUDA, "SM6.0 (Pascal) or later"; Linux and Windows. —
  [PhysX 5.4.1 GPU docs](https://nvidia-omniverse.github.io/PhysX/physx/5.4.1/docs/GPURigidBodies.html) [P]

### OIDN GPU vendors
- v2.5.1: CPUs (x86 SSE4.1+, ARM64), Intel Xe/Xe2/Xe3 GPUs, NVIDIA Turing through Blackwell, AMD RDNA 2/3/3.5/4, Apple silicon (M1+). —
  [README](https://github.com/RenderKit/oidn) [P]

### Kenney and ambientCG
- Kenney: game assets "public domain licensed (CC0)", "free to use them, even in commercial projects"; credit optional; Kenney logo
  reserved. — [kenney.nl/support](https://kenney.nl/support) [P]
- ambientCG: "All ambientCG assets are provided under the Creative Commons CC0 1.0 Universal License"; credit not required; no AI/ML
  clause. — [docs.ambientcg.com/license](https://docs.ambientcg.com/license/) [P]

### Quantised TRELLIS.2 at 6 GB
- GGUF quant files are 2.4 GB (Q4_K_M) to 4.3 GB (Q8_0) for the mesh stage plus ~2.3 GB shared files (download sizes, not VRAM). —
  [modly-trellis2-gguf-extension](https://github.com/lightningpixel/modly-trellis2-gguf-extension) [P]
- trellis.cpp: 1024 cascade on a 16 GB card; res-512 on Apple M5 peaked at 5.6 GB RSS (unified memory). — [README](https://github.com/pwilkin/trellis.cpp) [P]
- A 6 GB VRAM figure on a discrete GPU: not found.

### Pixal3D's VRAM
- See §2 (18–36 GB by settings; ~11 GB with a community patch at 1024; low-VRAM mode merged 2026-05-17). [P]

## 9 · Round-one snippet facts re-checked

- UniRig: "SIGGRAPH'25 (TOG)" — [README](https://github.com/VAST-AI-Research/UniRig) [P] (round one [S] confirmed)
- SkinTokens: arXiv 2602.04805 (2026-02-04), journal ref "ACM Transactions on Graphics 2026" — [arXiv API](https://arxiv.org/abs/2602.04805) [P]; the "+98–133%" accuracy figure not re-checked
- SAM 3D Body: arXiv 2602.15989 (2026-02-17); neither README nor arXiv metadata names CVPR 2026 — venue unconfirmed — [arXiv](https://arxiv.org/abs/2602.15989) [P]
- Pixal3D: "SIGGRAPH 2026", accepted April 2026; arXiv 2605.10922 — [README](https://github.com/TencentARC/Pixal3D) [P]
- DressCode: "SIGGRAPH 2024 (ACM Transactions on Graphics)" — [README](https://github.com/IHe-KaiI/DressCode) [P]
- Stable Fast 3D: "about 6GB VRAM for a single image" by default — [README](https://github.com/Stability-AI/stable-fast-3d) [P]
- Stability AI Community License: free under USD 1,000,000 annual revenue (with affiliates); above it the licence terminates unless a
  licence is granted; "Powered by Stability AI" display required; no use to build other foundation models; last updated 2024-07-05 —
  [stability.ai](https://stability.ai/community-license-agreement) [P]
- HY-Motion 1.0: arXiv 2512.23464, 2025-12-29 — [arXiv API](https://arxiv.org/abs/2512.23464) [P]
- Make-It-Animatable: "CVPR 2025" (arXiv comment) — [arXiv](https://arxiv.org/abs/2411.18197) [P]
- Strand-hair LOD (arXiv 2405.10565): 13 pages; the "EG 2025" venue is not in arXiv's metadata — unconfirmed [P]
- Software-raster hair (arXiv 2607.04230): published in Proc. ACM Comput. Graph. Interact. Tech. 9(4), Article 58, July 2026 [P]
- GarmentCodeData: ECCV 2024 (README) [P]; the 115k-garment count not re-checked
- TressFX 5.0, Cascadeur's free tier, Live Link Face's App Store page: now [P] (§8, §1c, §5)

---

## Couldn't verify / open

- **CMU mocap primary terms:** mocap.cs.cmu.edu fails certificate verification for the fetcher; only secondary copies of its wording
  (2008 and later) were read.
- **Mixamo FAQ (current):** helpx.adobe.com returned 403; Adobe General Terms not read.
- **OptiTrack NatNet licence text:** optitrack.com returned 429; the SDK's bundled licence file is not online in any page found.
- **Live Link plugin terms:** not read (UE EULA, §S5).
- **VRAM not found:** MagicArticulate, Make-It-Animatable, DiffLocks, GENMO (README, issues and one search each tried); T2M-GPT inference.
- **Non-NVIDIA runs not verified by any maintainer:** ComfyUI-native TRELLIS.2/Pixal3D on AMD/Apple; most AMD/MPS claims are open,
  unmerged community PRs or single user reports (labelled in §3).
- **ZOZO solver on AMD:** "never run on real AMD hardware" by its own README; real-time suitability for an editor viewport: no.
- **ufbx_write compatibility:** no published round-trip results with Maya/Unreal/Blender importers found.
- **Unreal Outfit Asset:** which bodies it accepts outside MetaHuman, and whether it works in a packaged app — Epic's conceptual docs
  page returned an empty shell to the fetcher; Unreal Geometry Script baking in a packaged app — not checked.
- **Chaos Cloth CPU-only:** no source states it outright (ISPC evidence only).
- **mocopi VMC output:** not documented by Sony; only mocopi (UDP) and VRChat (OSC) seen.
- **XPBD paper itself:** the PDF could not be rendered; facts from secondary sources only.
- **Jimenez eye slides:** 212–324 MB PowerPoints, not opened; eye topics unconfirmed.
- **BakeForge:** no repository found; LinkedIn claim only.
- **QuadGPT code:** none found.
- **VRM spec licence:** none stated in the repo; vrm.dev not checked.
- **Not re-checked from round one [S]:** AutoRemesher "final goes MIT" article, GarmentCodeData 115k, pygarment PyPI, SkinTokens
  accuracy figures, MetaTailor (digitalproduction), Quadify (paid), Xsens MVN streaming PDF, OnlineHMR (CVPR 2026), FaceDiffuser/SAiD,
  LHM++ 8 GB and other round-one items outside S7's list.
