# Research 07 — open building blocks for JustStage's character, animation and scene features

Date: 2026-10-29. By a research agent; not re-checked by the session. For RESEARCH.md §7.

**Labels.**
- **[P] page read.** Read from the primary page, the repo's own README or licence file (through GitHub's API), or GitHub's GraphQL data.
- **[S] search snippet only.**
- **Unlabelled text in a "does" or "quality evidence" cell** is a one-line statement of the project's purpose that was not re-read this pass. "Venue not checked" means the paper's conference was not confirmed.

**Health** is GitHub GraphQL data from 2026-10-29 [P]: stars · last push · latest release or tag.

**8 GB fit** refers to the RTX 2070 Super with 8 GB (§1). For libraries it says whether they need a GPU at all.

**Scope applied (coordinator, 2026-10-29).**
- **Paid-only is OUT.**
- **One-vendor GPU code is OUT for the core** (renderer, path tracer, physics, editor parts).
- **Optional parts** (AI models, mocap) keep a vendor label. "Vendors: unverified" means the README names no vendor; most of these are PyTorch repos that assume CUDA.
- **Free-but-proprietary options** keep normal rows, with their terms written out.
- **Licences are labels, not filters.**

**Method limits.** The session's shared web-search budget ran out partway through. After that, everything came from WebFetch on official pages and from GitHub's API. Anything still open is listed at the end.

## Top findings

1. **Jolt Physics v5.6.0 (2026-07-11, MIT) added GPU strand-hair simulation** [P].
   - It runs on a new compute layer with DX12, Vulkan, Metal and CPU back-ends, so it is not tied to one vendor.
   - Hair features: guide and render hairs, grid-based hair-to-hair collision, roots skinned to the scalp.
   - It is marked work in progress.
   - Jolt also has soft bodies (v5.4 added Cosserat rods), animated ragdolls, vehicles and deterministic simulation.
   - Source: [release notes](https://github.com/jrouwe/JoltPhysics/blob/master/Docs/ReleaseNotes.md), [README](https://github.com/jrouwe/JoltPhysics).
2. **Meta's Momentum Human Rig (MHR) is Apache-2.0** (v1.0.1, 2025-11) [P].
   - It is a body model with 45 identity parameters, 204 pose parameters, facial expression, and neural non-linear pose correctives.
   - It is the one permissive alternative to SMPL, whose licence is non-commercial with commercial terms through Meshcapade [P].
   - SAM 3D Body (SAM Licence) outputs MHR from a single image [P].
   - Momentum (MIT, C++/Python) adds forward and inverse kinematics plus body-tracking solvers [P].
   - Source: [MHR](https://github.com/facebookresearch/MHR), [SMPL licence](https://smpl.is.tue.mpg.de/modellicense.html), [sam-3d-body](https://github.com/facebookresearch/sam-3d-body).
3. **FLAME 2023 Open is CC-BY-4.0, so commercial use is allowed** [P]. FLAME 2017–2023 are non-commercial only. Many face trackers and lip-sync models need FLAME. Source: [FLAME licence](https://flame.is.tue.mpg.de/modellicense.html).
4. **MakeHuman/MPFB2 assets are CC0** [P]. The assets cover the base mesh, proxies, morph targets, textures, clothes in the MHCLO format, rigs, poses and expressions. The code is GPL-3. This gives an open base mesh, morph set and clothes-fitting format. Source: [MPFB2 LICENSE](https://github.com/makehumancommunity/mpfb2).
5. **FBX** [P]:
   - Blender 5.x's C++ FBX importer links ufbx (MIT or public domain).
   - ufbx is a single C file with no writer in the repo.
   - Writing FBX means Autodesk's FBX SDK 2020.3.11: free, closed C++, for Windows, macOS, iOS and Linux, with redistribution set by its EULA (not read). The other route is Assimp's exporter (BSD-3).
   - Source: [blender io/fbx](https://github.com/blender/blender/tree/main/source/blender/io/fbx), [ufbx](https://github.com/ufbx/ufbx), [Autodesk page](https://aps.autodesk.com/developer/overview/fbx-sdk).
6. **Cycles is the embeddable cross-vendor path tracer** [P]. It builds standalone or as a Hydra render delegate. Its device back-ends are CPU, CUDA, OptiX, HIP/HIP-RT, Metal and oneAPI. Apache-2.0, tag v5.2.0. Source: [blender/cycles](https://github.com/blender/cycles).
7. **Webcam face capture without vendor lock: MediaPipe Face Landmarker** (Apache-2.0) [P]. It outputs 52 blendshape scores, 478 3D landmarks and a transform matrix. Source: [docs](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker).
8. **Live mocap interchange: the VMC protocol** [P].
   - OSC over UDP, ports 39539/39540, with `/VMC/Ext/Bone/Pos`, `/Root/Pos` and `/Blend/Val` messages. The spec is MIT.
   - SlimeVR (open trackers), XR Animator (webcam), VSeeFace, Waidayo (iPhone) and others speak it.
   - Source: [protocol.vmc.info](https://protocol.vmc.info/english).
9. **Lip-sync: NVIDIA Audio2Face-3D is now open** [P].
   - Terms: the SDK and plugins are MIT; the models are under the NVIDIA Open Model License, "ready for commercial/non-commercial use".
   - Hardware: Turing GPUs are supported and 4 GB+ GPU memory is recommended.
   - Limits: it needs TensorRT/CUDA, so it is an optional part that runs on NVIDIA only. Its emotion model is restricted to use with Audio2Face.
   - Source: [hub](https://github.com/NVIDIA/Audio2Face-3D), [model card](https://huggingface.co/nvidia/Audio2Face-3D-v3.0).
10. **Image-to-3D on 8 GB** [P]:
    - Fits: Hunyuan3D-2 shape (6 GB, but its licence excludes the EU, UK and South Korea), TripoSR (6 GB, MIT), TripoSG and PartCrafter (at least 8 GB, MIT).
    - Does not fit: TRELLIS (16 GB), TRELLIS.2 (24 GB), Hunyuan3D-2.1 texturing (21 GB), Direct3D-S2 at 1024 (about 24 GB).
    - Source: the READMEs in table C14.
11. **Auto-rigging** [P]: UniRig (MIT) generates on at least 8 GB. Its 2026 successor SkinTokens/TokenRig (MIT, arXiv 2602.04805) needs 14 GB. Source: [UniRig](https://github.com/VAST-AI-Research/UniRig), [SkinTokens](https://github.com/VAST-AI-Research/SkinTokens).
12. **Text-to-motion** [P]:
    - The 2025 leader, HY-Motion 1.0 (1.0B and 0.46B), needs 24–26 GB. Its Tencent licence excludes the EU, UK and South Korea and requires a separate licence above 1M monthly active users.
    - Smaller models (MoMask, MDM, T2M-GPT) are MIT or Apache code, but they are trained on HumanML3D, which comes from AMASS. AMASS is non-commercial and forbids training models for commercial use.
    - Source: [HY-Motion](https://github.com/Tencent-Hunyuan/HY-Motion-1.0), [AMASS licence](https://amass.is.tue.mpg.de/license.html).
13. **Video mocap** [P]:
    - The strong monocular models either need SMPL (WHAM, TRAM, 4D-Humans) or are themselves non-commercial (GVHMR, PromptHMR, Multi-HMR, NVIDIA GENMO/GEM).
    - SAM 3D Body plus MHR is the one top model not tied to SMPL.
    - Multi-camera options: FreeMoCap (AGPL-3) and Pose2Sim (BSD-3).
    - Source: the repos in table A4.
14. **Clothing: no open equivalent of Marvelous Designer or MetaTailor exists.**
    - Open pieces: GarmentCode (MIT, parametric sewing patterns, simulated with NVIDIA Warp), Seamly2D (GPL-3, 2D drafting), ChatGarment (Apache-2.0, image or text to GarmentCode).
    - Fitting pieces: MPFB2's MHCLO fitting, and MIT-licensed robust skin-weight transfer.
    - The leading GPU cloth solvers (Newton: VBD, Style3D, XPBD) are NVIDIA-only and so out for the core.
    - Source: tables C9–C11.
15. **FX and content** [P]:
    - PopcornFX is out: its free plan is non-commercial only and shipping needs a paid plan. Effekseer (MIT, editor plus runtime, DX9 to DX12, Vulkan, Metal, OpenGL) is the open option.
    - Content usable commercially: 100STYLE (CC BY 4.0), Quaternius UAL (CC0, 60–70% free), Mesh2Motion (CC0), Poly Haven (CC0).
    - Non-commercial: LAFAN1, Bandai Namco, AMASS, Motion-X.
    - Mixamo is free but forbids ML training and redistributing raw files.
    - Source: [PopcornFX pricing](https://www.popcornfx.com/pricing/), table L1.

**Removed under the scope change.** These are not given as options:
- **Paid:** PopcornFX runtime for commercial shipping [P]; paid Blender add-ons such as Quadify [S].
- **NVIDIA-only GPU code in core roles:**
  - Newton (`newton/_src/solvers` holds vbd, style3d, xpbd, implicit_mpm, featherstone, mujoco) [P]
  - NVIDIA Warp; MuJoCo Warp
  - libuipc (CUDA IPC)
  - PhysX GPU features
  - OptiX as a standalone choice
  - Isaac Sim/Lab and anything built on Omniverse
  - The Audio2Face NIM container (NVIDIA software licence)
- **Their published algorithms stay usable as references:** VBD, XPBD, IPC.

---

## Character

### C1 · Sculpting (multiresolution, dynamic topology, voxel remesh)

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Blender sculpt mode | Full sculpt suite; multires and voxel-remesh sources present (`multires_*.cc`, `mesh_remesh_voxel.cc`) | Industry-wide use (not measured here) | GPU any vendor | C/C++ app; Python `bpy`; linking makes our app GPL — use as a separate process or for reference | 21.4k st · 2026-10 · tag v5.2.3 [P] | GPL (commercial yes, copyleft) — [LICENSE](https://github.com/blender/blender) | [repo tree](https://github.com/blender/blender/tree/main/source/blender/blenkernel/intern) [P] |
| SculptGL | Browser sculpting app (feature list not re-read) | — | WebGL | JavaScript | 1.5k st · **archived** 2026-01 [P] | MIT (commercial yes) | [repo](https://github.com/stephomi/sculptgl) [P] |
| OpenVDB | Sparse volumes; the basis for voxel remeshing and level-set booleans | ASWF project; VFX standard | CPU | C++ library | 3.4k st · 2026-10 · v13.2.0 (2026-10-27) [P] | Apache-2.0 (commercial yes) | [repo](https://github.com/AcademySoftwareFoundation/openvdb) [P] |
| ArmorPaint repo | Painting app; root holds `base` and `paint` only, with no sculpt module in this repo | — | GPU any vendor | C | 5.4k st · 2026-10 · 26.09 [P] | zlib for source; binaries sold (commercial yes) | [repo](https://github.com/armory3d/armorpaint) [P] |

**No good open option** exists as an embeddable sculpt engine at ZBrush level. Blender is the only complete open sculptor, and it is GPL and an app, not a library. ZBrush-class tools (millions of polygons, layers, ZRemesher-class retopology) would be our own code on OpenVDB plus a mesh kernel.

Assessment: Dynamic topology in Blender was not confirmed in this pass's source listing; the file-name search missed it.

### C2 · Retopology and remeshing

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| AutoRemesher | Automatic quad remesher with CLI; built on Geogram and libigl | "Final" release made MIT, 2026 [S]; v1.2.0 | CPU | C++ app/CLI; callable as a process | 3.6k st · 2026-10 · 1.2.0 (2026-08-23) [P] | MIT (commercial yes) | [repo](https://github.com/huxingyi/autoremesher) [P], [digitalproduction](https://digitalproduction.com/2026/07/28/autoremesher-final-goes-mit/) [S] |
| QuadWild-BiMDF | Field-aligned quad remeshing (successor to QuadWild) | Research (paper not fetched) | CPU | C/C++ | 143 st · 2026-08 · tag v0.0.2 [P] | GPL-3.0 (copyleft) | [repo](https://github.com/cgg-bern/quadwild-bimdf) [P] |
| QuadWild | Quad remeshing | Research | CPU | C++ | 435 st · 2022-09 [P] | GPL-3.0 | [repo](https://github.com/nicopietroni/quadwild) [P] |
| QuadriFlow | Quad remesher; bundled in Blender (`extern/quadriflow`) | Shipped in Blender [P] | CPU | C++ | 881 st · 2019-12 · v1.0 [P] | BSD-style (commercial yes) | [repo](https://github.com/hjwdzh/QuadriFlow) [P] |
| Instant Meshes | Field-aligned quad and triangle remeshing | Widely used since 2015 | CPU | C++ app/lib | 6.3k st · 2022-01 [P] | BSD-3-style (commercial yes) | [repo](https://github.com/wjakob/instant-meshes) [P] |
| MeshAnything V2 | AI "artist-created" low-poly mesh from dense mesh | Research | VRAM not stated | Python/PyTorch; vendors unverified | 1.0k st · 2025-04 [P] | S-Lab 1.0 — **non-commercial** | [repo](https://github.com/buaacyw/MeshAnythingV2) [P] |
| meshoptimizer | Simplification, LOD, vertex/index optimisation | Used widely in glTF tooling | CPU | C/C++ (+JS) | 8.7k st · 2026-10 · v1.3 (2026-09) [P] | MIT | [repo](https://github.com/zeux/meshoptimizer) [P] |
| geogram | Remeshing, parameterisation, Delaunay | Inria; under AutoRemesher | CPU | C++ | 2.6k st · 2026-10 · v1.10.1 [P] | BSD-3 | [repo](https://github.com/BrunoLevy/geogram) [P] |
| MeshLab / vcglib | Mesh processing toolbox (isotropic remesh, decimation) | Long-standing academic tool | CPU | C++ app/lib | 5.9k st · 2026-08 · 2025.07 [P] | GPL-3.0 | [repo](https://github.com/cnr-isti-vclab/meshlab) [P] |

Assessment: AutoRemesher is the best-licensed maintained quad remesher. No open neural retopology model with a commercial-friendly licence was found; DeepMesh, BPT and QuadGPT were not checked (see "open").

### C3 · UV unwrapping

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| xatlas | Automatic charting, parameterisation and packing | De facto open atlas library | CPU | C++ single lib | 2.6k st · last push 2024-06 [P] | MIT | [repo](https://github.com/jpcy/xatlas) [P] |
| UVAtlas (Microsoft) | Isochart UV atlas | DirectX toolkit lineage | CPU | C++ | 928 st · **archived** · oct2025 [P] | MIT | [repo](https://github.com/microsoft/UVAtlas) [P] |
| Boundary First Flattening | Conformal flattening with boundary control | Research paper (venue not checked) | CPU | C++ | 853 st · 2023-06 · v1.6 [P] | MIT | [repo](https://github.com/GeometryCollective/boundary-first-flattening) [P] |
| OptCuts | Joint seam and distortion optimisation | Research | CPU | C++ | 331 st · 2024-05 [P] | MIT | [repo](https://github.com/liminchen/OptCuts) [P] |
| PartUV | Part-based UV unwrapping (neural parts plus geometry) | Research, 2025–26 | VRAM not stated | C++/Python; vendors unverified | 264 st · 2026-07 [P] | Apache-2.0 (project licence) | [repo](https://github.com/EricWang12/PartUV) [P] |

Assessment: use xatlas for automatic atlases. Seam editing, pinning and packing UI are our own code; there is no open "RizomUV-class" library.

### C4 · Baking (normal, AO and other maps from high to low)

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Embree | CPU ray-tracing kernels; the basis of a baker | Intel; used by many renderers | CPU | C++ | 2.8k st · 2026-10 · v4.4.1 [P] | Apache-2.0 | [repo](https://github.com/RenderKit/embree) [P] |
| Open Image Denoise | Denoise baked or rendered maps | Used in Blender and others | CPU and GPUs (vendor list not re-checked) | C/C++ | 2.1k st · 2026-10 · v2.5.1 [P] | Apache-2.0 | [repo](https://github.com/RenderKit/oidn) [P] |
| Cycles (bake via Blender) | Cycles is embeddable (C13/S3); baking is driven from Blender's side | — | any vendor | C++ | see S3 | Apache-2.0 | [repo](https://github.com/blender/cycles) [P] |
| lightmapper (ands) | Lightmap baking (README not read) | single-header | GPU (OpenGL) | C header | 1.5k st · 2023-03 [P] | **no licence file found via API — unclear** | [repo](https://github.com/ands/lightmapper) [P] |

**No good open option** exists as a maintained standalone texture baker (cage, ray distance, curvature, thickness, ID). It would be built on Embree plus xatlas.

### C5 · Real-time skin rendering (subsurface)

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| O3DE Atom — Skin material | Skin material type with wrinkle maps (`Skin.materialtype`, `Skin_WrinkleMaps.lua`) | Production engine (Linux Foundation) | any vendor (Vulkan/DX12/Metal) | C++ engine; read as a reference implementation | 9.8k st · 2026-10 · 2605.0 [P] | Apache-2.0 OR MIT | [Materials/Types](https://github.com/o3de/o3de/tree/development/Gems/Atom/Feature/Common/Assets/Materials/Types) [P] |
| Separable SSS (Jimenez) | Screen-space separable subsurface scattering + transmittance | Jimenez et al. technique (venue not checked) | any GPU | C++/HLSL demo | 656 st · 2018 [P] | BSD-style custom (commercial yes, attribution) | [repo](https://github.com/iryoku/separable-sss) [P] |
| Filament | PBR renderer with a "subsurface" shading model (docs hit) | Google; Android, desktop and web | any vendor | C++ library | 20.7k st · 2026-10 · v1.79.0 [P] | Apache-2.0 | [repo](https://github.com/google/filament), code-search hit in `docs/Materials.md.html` [P] |
| Godot | Screen-space SSS material parameter (`subsurf_scatter` in `material.cpp`) | Large engine | any vendor | C++ engine | 119k st · 2026-10 · 4.7.2 [P] | MIT | [repo](https://github.com/godotengine/godot) [P] |
| Wicked Engine | Subsurface terms in BRDF and surface shaders | Hobby or indie engine with an active release cadence | DX12/Vulkan (macOS not checked) | C++ | 7.3k st · 2026-10 · v0.72.120 [P] | MIT | [repo](https://github.com/turanszkij/WickedEngine) [P] |
| Bevy | Only diffuse transmission (`transmission.wesl`); no dedicated SSS found | — | any vendor (wgpu) | Rust | 49.4k st · 2026-10 · v0.20.1 [P] | Apache-2.0 / MIT | code search [P] |

Assessment: there is no stand-alone skin-SSS library. The technique is screen-space separable or Burley-style diffusion plus transmission. O3DE is the most complete open reference with skin, eye and TressFX together.

### C6 · Eye and teeth shading

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| O3DE Atom — Eye material | Eye material type (`Eye.materialtype`, `Eye.azsli`) | Production engine | any vendor | C++/AZSL shaders; reference | as C5 [P] | Apache-2.0 OR MIT | [Materials/Types](https://github.com/o3de/o3de/tree/development/Gems/Atom/Feature/Common/Assets/Materials/Types) [P] |

**No good open option** exists as a library; teeth shading has none either. These are techniques (refraction, parallax iris, caustic and occlusion terms) for our own shaders.

### C7 · Strand hair rendering and grooming

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| AMD TressFX 4.1 | GPU strand hair rendering and simulation; DX12 and Vulkan sample; UE 4.22 patch | AMD GPUOpen library; TressFX 5.0 for UE reported [S] | any vendor | C++/HLSL | 847 st · 2023-01 · v4.1.0 (2020) [P] | MIT | [repo](https://github.com/GPUOpen-Effects/TressFX) [P], [gfxspeak](https://gfxspeak.com/featured/amd-all-tressed-up/) [S] |
| O3DE AtomTressFX gem | TressFX integrated in an open engine | Engine gem | any vendor | C++ | as C5 [P] | Apache-2.0 OR MIT | [Gems](https://github.com/o3de/o3de/tree/development/Gems) [P] |
| Wicked Engine hair | Hair via bundled Jolt hair module plus engine renderer | Code present (`WickedEngine/Jolt/Physics/Hair`) | DX12/Vulkan | C++ | as C5 [P] | MIT | code search [P] |
| Unity Hair (demoteam) | Strand hair system for Unity | Unity demo team | — | C# Unity package | 841 st · 2025-02 [P] | Unity Companion License — free, source visible, **only for Unity-dependent projects** | [repo](https://github.com/Unity-Technologies/com.unity.demoteam.hair) [P] |
| DiffLocks | Single image to 3D strands; trained on 40K synthetic Blender hairstyles | Research (MPI/Meshcapade) | not stated | C++/Python; vendors unverified | 193 st · 2025-10 [P] | **Non-commercial research** | [repo](https://github.com/Meshcapade/difflocks) [P], [site](https://difflocks.is.tue.mpg.de/) [S] |
| Perm | Parametric strand-hair representation (generative grooming) | Research | not stated | Python | 124 st · 2026-07 [P] | MIT | [repo](https://github.com/c-he/perm) [P] |
| GaussianHaircut | Strand reconstruction from video | Research | not stated | Python | 292 st · 2025-01 [P] | CC BY-NC-SA 4.0 — non-commercial | [repo](https://github.com/eth-ait/GaussianHaircut) [P] |
| HAAR | Text to strand hairstyle | Research | not stated | Python | 94 st · 2024-10 [P] | CC BY-NC 4.0 — non-commercial | [repo](https://github.com/Vanessik/HAAR) [P] |
| LOD strand rendering papers | Cluster-to-thick-strand LOD (EG 2025, up to 13× speedup); deferred software raster (arXiv 2607.04230, Jul 2026) | Peer-reviewed / preprint | — | techniques; no code link seen | — | — | [arXiv 2405.10565](https://arxiv.org/pdf/2405.10565), [arXiv 2607.04230](https://arxiv.org/abs/2607.04230) [S] |

**No good open option** exists as a grooming tool: open guides, clumping and noise brushes outside Blender's hair curves (not checked this pass). Rendering has TressFX (2020) and O3DE's gem only.

### C8 · Hair simulation

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Jolt Physics hair (v5.6.0) | GPU strand sim: guide and render hairs, long-range attachments, grid-averaged hair–hair collision, skinned roots; WIP | New in v5.6.0 (2026-07), marked WIP | any vendor (DX12/Vulkan/Metal/CPU compute) | C++ library | 11.8k st · 2026-10 · v5.6.0 (2026-07-11) [P] | MIT | [release notes](https://github.com/jrouwe/JoltPhysics/blob/master/Docs/ReleaseNotes.md) [P] |
| TressFX sim | GPU strand sim (shape constraints, wind, collision) | see C7 | any vendor | C++/HLSL | see C7 [P] | MIT | [repo](https://github.com/GPUOpen-Effects/TressFX) [P] |
| PositionBasedDynamics | PBD/XPBD library (rods and elastic models; rod details not re-read) | Academic library | CPU | C++ | 2.3k st · 2026-09 · 2.2.0 (2022) [P] | MIT | [repo](https://github.com/InteractiveComputerGraphics/PositionBasedDynamics) [P] |

Assessment: Jolt is the strongest fit (same library as rigid and soft bodies, cross-vendor GPU), but it is new and marked WIP.

### C9 · Garment making from 2D patterns with sewing simulation

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| GarmentCode / pygarment | Programmatic parametric sewing patterns (panels, edges, interfaces); body measurements; data generation simulated with NVIDIA Warp; old Maya+Qualoth path | ETH; GarmentCodeData 115k garments [S] | pattern code CPU; sim **NVIDIA (Warp)** | Python | 485 st · 2025-06 · v2.0.1 (2024) [P] | MIT | [repo](https://github.com/maria-korosteleva/GarmentCode) [P], [PyPI](https://pypi.org/project/pygarment) [S] |
| Seamly2D | 2D parametric pattern drafting; measurement tables | Long-running GPL project | CPU | C++/Qt app | 1.0k st · 2026-10 · v2026.10.26 [P] | GPL-3.0 | [repo](https://github.com/FashionFreedom/Seamly2D) [P] |
| FreeSewing | Parametric sewing patterns from measurements | — | CPU | JavaScript | 488 st · **archived** 2025-04 · tag v4.0.0 [P] | MIT | [repo](https://github.com/freesewing/freesewing) [P] |
| ChatGarment | Image or text to GarmentCode patterns (LLaVA fine-tune); sim via ContourCraft fork | Research | VRAM not stated (LLM) | Python; vendors unverified | 180 st · 2025-08 [P] | Apache-2.0 (code) | [repo](https://github.com/biansy000/ChatGarment) [P] |
| AIpparel | Multimodal sewing-pattern generation | Research | not stated | Python | 69 st · 2025-07 [P] | MIT | [repo](https://github.com/georgeNakayama/AIpparel-Code) [P] |
| DressCode | Text to sewing pattern (SewingGPT) | SIGGRAPH 2024 [S] | not stated | Python | 297 st · 2024-10 [P] | **no licence file — unclear** | [repo](https://github.com/IHe-KaiI/DressCode) [P] |
| ContourCraft / HOOD | Learned garment simulation (intersection-free); SMPL/SMPL-X bodies | Research | not stated | Python/PyTorch; vendors unverified | 101 st / 206 st · 2025 [P] | MIT code (SMPL needed — non-commercial) | [ContourCraft](https://github.com/Dolorousrtur/ContourCraft), [HOOD](https://github.com/Dolorousrtur/HOOD) [P] |
| Codim-IPC | Codimensional IPC cloth/shell sim (intersection-free, slow) | Research (2021–23) | CPU | C++ | 248 st · 2023-01 [P] | Apache-2.0 | [repo](https://github.com/ipc-sim/Codim-IPC) [P] |

**No good open option** exists as an interactive pattern-to-3D-garment app like Marvelous Designer. The open parts are a pattern model (GarmentCode), 2D drafting (Seamly2D) and offline sims.

Assessment: the core would be our own cloth solver (XPBD, VBD or IPC from papers) on a cross-vendor compute layer, with GarmentCode's data model as the pattern reference.

### C10 · Fitting clothes to any body (MetaTailor-type)

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| MPFB2 (MakeHuman) | Body generator with MHCLO clothes that follow body morphs and proxies | MakeHuman lineage; active | CPU | Python (Blender add-on) | 671 st · 2026-10 · v2.0.18 [P] | GPL-3 code; **CC0 assets** (base mesh, targets, clothes, rigs) | [LICENSE](https://github.com/makehumancommunity/mpfb2) [P] |
| CharMorph | Blender character morphing with asset fitting | Community add-on | CPU | Python | 576 st · 2025-05 · v0.4.0-3 [P] | GPL-3 code | [repo](https://github.com/Upliner/CharMorph) [P] |
| Robust Skin Weights Transfer | Weight transfer plus inpainting (body to garment) | Research paper (venue not checked) | CPU | C++ (libigl) | 144 st · 2024-07 [P] | MIT | [repo](https://github.com/rin-23/RobustSkinWeightsTransferCode) [P] |
| trimesh registration | Non-rigid ICP (`nricp_amberg`, `nricp_sumner`) for shape wrapping | Widely used Python lib | CPU | Python | 3.7k st · 2026-10 · 5.2.0 [P] | MIT | [registration.py](https://github.com/mikedh/trimesh/blob/main/trimesh/registration.py) [P] |
| DrapeNet | Learned draping of garments on bodies | Research (venue not checked) | not stated | Python | 127 st · 2023-09 [P] | GPL-3.0 | [repo](https://github.com/liren2515/DrapeNet) [P] |
| MetaTailor (reference only) | Proprietary adaptive fitting, skin weights, layer order | — | — | closed, Windows | — | commercial | [digitalproduction](https://digitalproduction.com/2026/02/05/metatailor-adds-engine-bridges-and-less-fbx-fatigue/) [S] |

**No good open option.** The parts exist (non-rigid wrap, weight transfer, MHCLO-style offsets, a cloth solver for settling and layering), but no open tool combines them.

### C11 · Cloth simulation libraries (core: cross-vendor only)

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Jolt soft bodies | Soft bodies usable as cloth (edge, bend and volume constraints, double-sided faces, Cosserat rods) | Shipped engine physics | CPU | C++ | see S1 [P] | MIT | [release notes](https://github.com/jrouwe/JoltPhysics/blob/master/Docs/ReleaseNotes.md) [P] |
| Genesis | Multi-physics (rigid, FEM, MPM, PBD/SPH, uipc); "Quadrants" compiles to CUDA, ROCm, Metal, Vulkan, x86, ARM64 | Large robotics project | any vendor (per README) | Python | 30.1k st · 2026-10 · v1.4.5 [P] | Apache-2.0 | [repo](https://github.com/Genesis-Embodied-AI/genesis-world) [P] |
| Taichi | GPU compute DSL (MPM, PBD examples) | Widely used research DSL | multi-backend (not re-checked) | Python/C++ | 28.4k st · 2026-10 · v1.7.4 (2025-07) [P] | Apache-2.0 | [repo](https://github.com/taichi-dev/taichi) [P] |
| PositionBasedDynamics | PBD/XPBD cloth | Academic | CPU | C++ | see C8 [P] | MIT | [repo](https://github.com/InteractiveComputerGraphics/PositionBasedDynamics) [P] |
| Bullet soft bodies | Soft body / cloth | Old; last release 2022 | CPU | C++ | 14.8k st · 2026-10 · 3.25 (2022) [P] | zlib | [repo](https://github.com/bulletphysics/bullet3) [P] |
| Codim-IPC | see C9 | | | | | | |

Removed for the core (NVIDIA-only GPU): Newton (VBD, Style3D, XPBD solvers [P]), Warp, libuipc, and PhysX GPU deformables.

Assessment: Garment-quality real-time cloth on a cross-vendor GPU has no ready library. Jolt (CPU soft bodies) or our own XPBD/VBD on Jolt's compute layer are the candidates.

### C12 · Blendshape and morph authoring, correctives, body models

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| MHR (Momentum Human Rig) | Body model: 45 identity, 204 pose params, facial expression, neural non-linear pose correctives | Used by SAM 3D Body (CVPR 2026 [S]) | small | Python package (+ Momentum C++) | 885 st · 2026-10 · v1.0.1 (2025-11) [P] | **Apache-2.0** | [repo](https://github.com/facebookresearch/MHR) [P] |
| Momentum | Kinematics, IK and body-tracking solvers (RGB, RGB-D) | Meta research, active | CPU | C++ with Python | 433 st · 2026-10 · v0.1.114 [P] | MIT | [repo](https://github.com/facebookresearch/momentum) [P] |
| MakeHuman targets (via MPFB2) | Morph-target library on an open base mesh | Long-running project | CPU | data (targets) | see C10 [P] | CC0 assets | [LICENSE](https://github.com/makehumancommunity/mpfb2) [P] |
| FLAME 2023 Open | Head model (shape, expression, pose) | Standard in face research | small | model data | — | CC-BY-4.0 (commercial yes); older FLAME non-commercial | [licence](https://flame.is.tue.mpg.de/modellicense.html) [P] |
| SMPL / SMPL-X | Body model used by most HMR and motion models | De facto research standard | small | model data | — | **non-commercial**; commercial via Meshcapade | [licence](https://smpl.is.tue.mpg.de/modellicense.html) [P] |
| Neural Blend Shapes | Learned skinning plus corrective blendshapes | Research (venue not checked) | not stated | Python | 704 st · 2021-08 [P] | BSD-2-style | [repo](https://github.com/PeizhuoLi/neural-blend-shapes) [P] |
| cmt (Chad Vernon) | Maya rigging tools (RBF etc.; feature list not re-read) | — | — | Python (Maya) | 280 st · 2020-10 [P] | MIT | [repo](https://github.com/chadmv/cmt) [P] |

Assessment: correctives (pose-space RBF) are a technique, not a library. MHR's neural correctives plus MakeHuman's CC0 targets are the best open data starting points.

### C13 · Auto-rigging and skin weights

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| UniRig | Autoregressive skeleton for any mesh plus skin-weight prediction | SIGGRAPH 2025 (arXiv 2504.12451) [S] | **≥8 GB** (generation) [P] | Python/PyTorch; CUDA per README | 1.9k st · 2026-06 [P] | MIT | [repo](https://github.com/VAST-AI-Research/UniRig) [P] |
| SkinTokens / TokenRig | Skin weights as discrete tokens; skeleton and skin in one sequence | arXiv 2602.04805 (Feb 2026); self-reported +98–133% skinning accuracy [S] | **14 GB — no** [P] | Python; NVIDIA per README | 553 st · 2026-05 [P] | MIT | [repo](https://github.com/VAST-AI-Research/SkinTokens), [arXiv](https://arxiv.org/abs/2602.04805v1) [S] |
| Puppeteer | Skeleton, skinning and animation of 3D objects | Research 2025 | not stated | Python | 439 st · 2025-09 [P] | Apache-2.0 | [repo](https://github.com/Seed3D/Puppeteer) [P] |
| MagicArticulate | Skeleton generation (weights fixed 2025-08) | Research 2025 (venue not checked) | not stated | Python | 418 st · 2025-09 [P] | Apache-2.0 | [repo](https://github.com/Seed3D/MagicArticulate) [P] |
| Make-It-Animatable | Fast humanoid rigging (joints, weights, pose) with Blender integration | Research (venue not checked) | not stated | Python | 468 st · 2026-09 [P] | MIT | [repo](https://github.com/jasongzy/Make-It-Animatable) [P] |
| RigNet | Learned skeleton and skinning | Research 2020 (venue not checked) | not stated | Python | 1.5k st · 2024-11 [P] | GPL-3.0 | [repo](https://github.com/zhan-xu/RigNet) [P] |
| Mesh2Motion | Web app: import model, auto-assign and export animations (GLB) — Mixamo-like | Active | browser | TypeScript web app | 3.6k st · 2026-10 [P] | CC0 for models, rigs and animations (code licence not read) | [repo](https://github.com/Mesh2Motion/mesh2motion-app) [P] |
| Robust Skin Weights Transfer | see C10 | | | | | MIT | |
| Mixamo (free, proprietary) | Online auto-rigger plus animation library | Widely used | web service | closed; Adobe | — | Free; royalty-free commercial use; **no redistribution of raw files; no ML training** (FAQ 2022) | [Adobe FAQ](https://community.adobe.com/t5/mixamo-discussions/mixamo-faq-licensing-royalties-ownership-eula-and-tos/m-p/13234775) [P] |

### C14 · Photo-to-head, photo-to-body and image-to-3D

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| SAM 3D Body | Single image to full-body mesh (body, feet, hands) in MHR | Claims SOTA; CVPR 2026 [S] | not stated | Python/PyTorch; vendors unverified | 3.7k st · 2026-02 [P] | SAM License (royalty-free use, modify, redistribute; custom terms) — commercial conditional | [repo](https://github.com/facebookresearch/sam-3d-body) [P] |
| LHM / LHM++ | Image(s) to animatable full-body human (Gaussians) | LHM++ (Mar 2026): 8-view input on 8 GB [P] | LHM++ 8 GB; LHM-500M Gradio 24 GB [P] | Python; vendors unverified | 2.7k st · 2026-03 [P] | Apache-2.0 | [repo](https://github.com/aigc3d/LHM) [P] |
| LAM | One-shot avatar model (README details not read) | — | not stated | Python | 1.1k st · 2026-06 [P] | Apache-2.0 | [repo](https://github.com/aigc3d/LAM) [P] |
| SMIRK | Photo to FLAME face parameters | Research (venue not checked) | small | Python; needs FLAME | 401 st · 2024-05 [P] | MIT code + FLAME terms | [repo](https://github.com/georgeretsi/smirk) [P] |
| DECA / MICA | Photo to FLAME head | Widely cited | small | Python | 2.5k / 661 st [P] | **non-commercial** | [DECA](https://github.com/yfeng95/DECA), [MICA](https://github.com/Zielon/MICA) [P] |
| VHAP | Head tracking to FLAME from video | Research | not stated | Python | 385 st · 2026-08 [P] | CC BY-NC-SA 4.0 | [repo](https://github.com/ShenhanQian/VHAP) [P] |
| Hunyuan3D-2 (incl. mini, turbo) | Image to mesh + texture | 15.2k st; widely used | **6 GB shape; 16 GB shape+texture**; `--low_vram_mode` [P] | Python; vendors unverified | 15.2k st · 2025-10 [P] | Tencent Hunyuan 3D 2.0 Community — **not valid in EU/UK/South Korea** | [repo](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) [P] |
| Hunyuan3D-2.1 | Image to mesh + PBR texture | June 2025 | 10 GB shape; 21 GB texture — **no** [P] | Python | 4.3k st · 2025-10 [P] | Tencent community (same territory limit) | [repo](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1) [P] |
| Hunyuan3D-Omni / -Part | Controllable generation / part split (Sep 2025) | — | not stated | Python | 653 / 554 st [P] | Tencent community (territory limit) | [Omni](https://github.com/Tencent-Hunyuan/Hunyuan3D-Omni), [Part](https://github.com/Tencent-Hunyuan/Hunyuan3D-Part) [P] |
| TRELLIS / TRELLIS.2 | Image to 3D (structured latents) | 14.1k / 12.5k st | **16 GB / 24 GB — no** [P]; quantised 6 GB claim [S] | Python; NVIDIA per README | 2026-10 / 2026-07 [P] | MIT | [TRELLIS](https://github.com/microsoft/TRELLIS), [TRELLIS.2](https://github.com/microsoft/TRELLIS.2) [P] |
| TripoSG | Image to high-fidelity mesh (geometry only [S]) | — | **≥8 GB** [P] | Python; CUDA per README | 1.9k st · 2025-04 [P] | MIT | [repo](https://github.com/VAST-AI-Research/TripoSG) [P] |
| TripoSR | Fast feed-forward image to mesh | Long-standing baseline | **~6 GB** [P] | Python | 7.3k st · 2026-06 [P] | MIT | [repo](https://github.com/VAST-AI-Research/TripoSR) [P] |
| PartCrafter | Image to part-separated meshes (on TripoSG) | — | **≥8 GB** [P] | Python; CUDA per README | 2.5k st · 2026-04 [P] | MIT | [repo](https://github.com/wgsxm/PartCrafter) [P] |
| Pixal3D | Pixel-aligned image to 3D; low-VRAM mode (1024 res) | SIGGRAPH 2026 [S] | low-VRAM ~10–12 GB per a third-party blog [S] — likely no | Python | 2.5k st · 2026-09 [P] | MIT | [repo](https://github.com/TencentARC/Pixal3D) [P] |
| Direct3D-S2 | Sparse SDF image to 3D | — | 10 GB @512; ~24 GB @1024 — **no** [P] | Python | 1.3k st · v1.1.0 [P] | MIT | [repo](https://github.com/DreamTechAI/Direct3D-S2) [P] |
| Step1X-3D | Geometry + texture (May 2025) | — | VRAM table in README (numbers not extracted) | Python | 898 st · 2025-09 [P] | Apache-2.0 | [repo](https://github.com/stepfun-ai/Step1X-3D) [P] |
| Stable3DGen (Hi3DGen) | Normal-bridged image to 3D | — | not stated | Python | 1.3k st · 2025-07 [P] | MIT | [repo](https://github.com/Stable-X/Stable3DGen) [P] |
| SAM 3D Objects | Image to object 3D | Meta, Nov 2025 | not stated | Python | 7.6k st · 2026-06 [P] | SAM License (conditional) | [repo](https://github.com/facebookresearch/sam-3d-objects) [P] |
| Stable Fast 3D / SPAR3D | Fast image to textured mesh | — | ~6 GB for SF3D [S] | Python | 1.9k / 1.1k st [P] | Stability AI Community (free under revenue cap [S]) — conditional | [SF3D](https://github.com/Stability-AI/stable-fast-3d) [P] |
| PartPacker | Part-level generation | NVIDIA research | not stated | Python | 827 st [P] | NVIDIA Source Code License — **non-commercial** | [repo](https://github.com/NVlabs/PartPacker) [P] |

**No good open option** exists for photo-to-head in a production topology like CC Headshot, meaning a textured head on our own base mesh. The open path is FLAME, SMIRK or MHR fitting, then wrapping onto our base mesh (C10 tools) and projecting the texture.

### C15 · Texture generation and layer-based painting

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| ArmorPaint | Layer-based 3D texture painting app | Long-running | any GPU | C | 5.4k st · 2026-10 · 26.09 [P] | zlib source; binaries paid ("Distributed binaries are paid") — building from source is free | [repo](https://github.com/armory3d/armorpaint) [P] |
| Ucupaint | Layer system for Blender texture painting | Active | — | Python (Blender add-on) | 2.3k st · 2026-10 · 3.0.0 [P] | GPL-3.0 | [repo](https://github.com/ucupumar/ucupaint) [P] |
| Material Maker | Node-based procedural materials (Godot app) | Active | any GPU | GDScript/Godot | 6.1k st · 2026-10 · 1.8 [P] | MIT | [repo](https://github.com/RodZill4/material-maker) [P] |
| MV-Adapter | Multi-view generation for texturing (incl. geometry-conditioned) | — | SD2.1 variant <6 GB; geometry adapters <10 GB; SDXL >12 GB [P] | Python (diffusers) | 1.3k st · 2025-06 [P] | Apache-2.0 | [repo](https://github.com/huanngzh/MV-Adapter) [P] |
| Hunyuan3D-2 / 2.1 Paint | Texture (2.1: PBR) for meshes | — | 2.0: within 16 GB total; 2.1: 21 GB — no [P] | Python | see C14 [P] | Tencent community (territory limit) | see C14 [P] |
| Step1X-3D texture | Geometry-aligned texture synthesis | — | not extracted | Python | see C14 | Apache-2.0 | see C14 [P] |
| MaterialAnything | PBR material generation for 3D objects | Research | not stated | Python | 369 st · 2025-12 [P] | MIT | [repo](https://github.com/3DTopia/MaterialAnything) [P] |
| Paint3D | Lighting-less texture generation | Research 2024 | not stated | Python | 810 st · 2024-11 [P] | Apache-2.0 | [repo](https://github.com/OpenTexture/Paint3D) [P] |
| StableGen | Blender add-on for AI texturing (README not read) | Active | depends on model | Python | 967 st · 2026-10 · v0.4.0 [P] | GPL-3.0 | [repo](https://github.com/sakalond/StableGen) [P] |

### C16 · Prop modelling: mesh-editing kernels and generators

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Manifold | Robust mesh booleans | — | CPU | C++ | 2.4k st · 2026-10 · v3.5.4 [P] | Apache-2.0 | [repo](https://github.com/elalish/manifold) [P] |
| PMP library | Halfedge mesh, smoothing, remeshing, decimation | Academic | CPU | C++ | 1.5k st · 2026-08 · 3.0.0 (2023) [P] | MIT | [repo](https://github.com/pmp-library/pmp-library) [P] |
| geometry-central | Halfedge mesh + geometry processing | Academic | CPU | C++ | 1.3k st · 2026-06 · v1.1.0 [P] | MIT | [repo](https://github.com/nmwsharp/geometry-central) [P] |
| libigl | Geometry processing (weights, deformation, winding numbers) | Widely cited | CPU | C++ header lib | 5.1k st · 2026-09 · v2.6.4 [P] | MPL-2.0 core + GPL-3 copyleft modules | [repo](https://github.com/libigl/libigl) [P] |
| CGAL | Computational geometry | Industry standard | CPU | C++ | 6.1k st · 2026-10 · v6.2.1 [P] | GPL/LGPL per package (heading read only) | [repo](https://github.com/CGAL/cgal) [P] |
| Open CASCADE (OCCT) | B-rep CAD kernel | — | CPU | C++ | 3.1k st · 2026-10 · V8.0.1 [P] | LGPL-2.1 | [repo](https://github.com/Open-Cascade-SAS/OCCT) [P] |
| truck | B-rep CAD kernel | Active | CPU (+wgpu) | Rust crates | 1.7k st · 2026-10 [P] | Apache-2.0 | [repo](https://github.com/ricosjp/truck) [P] |
| Fornjot | B-rep CAD kernel | — | CPU | Rust | **archived** · v0.49.0 (2024) [P] | 0BSD | [repo](https://github.com/hannobraun/fornjot) [P] |
| Open3D / trimesh | Mesh I/O and processing (Python first) | Widely used | CPU | C++/Python | 14.1k / 3.7k st · 2026 [P] | MIT | [Open3D](https://github.com/isl-org/Open3D), [trimesh](https://github.com/mikedh/trimesh) [P] |
| Dust3D | Quick modelling from sketched nodes | — | CPU | C++ app | 3.6k st · 2026-10 · 1.1.6 [P] | MIT | [repo](https://github.com/huxingyi/dust3d) [P] |
| Image- and text-to-3D | see C14 (text-to-3D in practice is text-to-image then image-to-3D) | | | | | | |

---

## Animation

### A1 · Retargeting

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Godot RetargetModifier3D (+ SkeletonProfile) | Engine-level retargeting between skeletons | Large engine | CPU | C++ (read as reference) | see C5 [P] | MIT | [scene/3d](https://github.com/godotengine/godot/tree/master/scene/3d) [P] |
| GMR (General Motion Retargeting) | Human motion to humanoid robots | Active 2026 | CPU | Python | 2.8k st · 2026-10 [P] | MIT | [repo](https://github.com/YanjieZe/GMR) [P] |
| Deep Motion Editing (skeleton-aware networks) | Learned retargeting across topologies | Research (venue not checked) | small | Python | 1.7k st · 2024-07 [P] | BSD-2 | [repo](https://github.com/DeepMotionEditing/deep-motion-editing) [P] |
| Rokoko Studio Live for Blender | Live stream in plus retargeting in Blender | Official plugin | — | Python | 511 st · 2026-10 · v1-4-3 [P] | **conflict:** GitHub detects LGPL-3.0; README badge says MIT | [repo](https://github.com/Rokoko/rokoko-studio-live-blender) [P] |

**No good open option** exists as a standalone retargeting library comparable to an IK-chain retargeter.

Assessment: build on Momentum/MHR or a standard humanoid bone list (VRM humanoid or Godot SkeletonProfile) with our own chain mapping.

### A2 · IK/FK and full-body IK

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Godot IK modifiers | TwoBoneIK3D, FABRIK3D, CCDIK3D, JacobianIK3D, SplineIK3D, ChainIK3D, LookAt, Aim, SpringBoneSimulator3D | Large engine | CPU | C++ (reference or embed via engine) | see C5 [P] | MIT | [scene/3d](https://github.com/godotengine/godot/tree/master/scene/3d) [P] |
| Momentum | FK/IK with interpretable parameters; body-tracking solvers | Meta | CPU | C++/Python | see C12 [P] | MIT | [repo](https://github.com/facebookresearch/momentum) [P] |
| Pinocchio | Rigid-body kinematics and dynamics (robotics) | Robotics standard | CPU | C++/Python | 3.8k st · 2026-10 · v4.1.0 [P] | BSD-2 | [repo](https://github.com/stack-of-tasks/pinocchio) [P] |
| Jolt ragdolls | Animated ragdolls; mapping between animation and ragdoll skeletons | see S1 | CPU | C++ | see S1 [P] | MIT | [README](https://github.com/jrouwe/JoltPhysics) [P] |

### A3 · Animation runtimes and compression

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| ozz-animation | Runtime playback (loading, sampling, blending), engine-agnostic; toolchain from glTF and FBX | Long-running | CPU | C++ | 3.0k st · 2026-08 · 0.17.0 (2026-08-01) [P] | MIT | [repo](https://github.com/guillaumeblanc/ozz-animation) [P] |
| ACL (Animation Compression Library) | Production animation compression; aims at "cinematographic quality" | — | CPU | C++ header lib | 1.6k st · 2025-11 · v2.1.0 (2023) [P] | MIT | [repo](https://github.com/nfrechette/acl) [P] |

### A4 · Video mocap (optional — vendor labels)

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| FreeMoCap | Multi-camera markerless mocap app | 10.6k st | CPU/GPU (vendors unverified) | TypeScript (primary per GitHub) app | 2026-10 · v2.0.0-alpha.25 [P] | AGPL-3.0 | [repo](https://github.com/freemocap/freemocap) [P] |
| Pose2Sim | Multi-camera markerless kinematics (OpenSim) | Academic, active | CPU/GPU | Python | 864 st · 2026-10 · v0.10.49 [P] | BSD-3 | [repo](https://github.com/perfanalytics/pose2sim) [P] |
| SAM 3D Body | Single image to MHR mesh (not SMPL) | Claims SOTA [P README] | not stated | Python; vendors unverified | see C14 [P] | SAM License (conditional); MHR Apache-2.0 | [repo](https://github.com/facebookresearch/sam-3d-body) [P] |
| WHAM | Video to world-grounded SMPL motion | Research (venue not checked) | not stated | Python | 1.2k st · 2024-04 [P] | MIT code; **SMPL non-commercial** | [repo](https://github.com/yohanshin/WHAM) [P] |
| TRAM | Video to world-space SMPL with camera | Research (venue not checked) | not stated | Python | 646 st · 2025-06 [P] | MIT code; SMPL | [repo](https://github.com/yufu-wang/tram) [P] |
| 4D-Humans (HMR 2.0) | Image or video to SMPL with tracking | Research (venue not checked) | not stated | Python | 1.7k st · 2026-02 [P] | MIT code; SMPL | [repo](https://github.com/shubham-goel/4D-Humans) [P] |
| NLF | Neural localizer fields (body model dependency not shown in README) | — | not stated | Python | 468 st · 2026-10 · v0.3.2 [P] | MIT | [repo](https://github.com/isarandi/nlf) [P] |
| GVHMR | Gravity-view world-grounded HMR | Research (venue not checked) | not stated | Python | 2.2k st · 2026-09 [P] | **non-commercial custom** (commercial by email) | [repo](https://github.com/zju3dv/GVHMR) [P] |
| PromptHMR | Promptable HMR | 2025 | not stated | Python | 507 st · 2026-01 [P] | **non-commercial** | [repo](https://github.com/yufu-wang/PromptHMR) [P] |
| Multi-HMR | Multi-person HMR | NAVER | not stated | Python | 424 st · 2026-03 [P] | **NAVER non-commercial** | [repo](https://github.com/naver/multi-hmr) [P] |
| GENMO / GEM-SMPL | Generalist model: video, text, audio or music to motion (Mar 2026 release) | NVIDIA research | not stated | Python | 540 st · 2026-06 [P] | NVIDIA OneWay **Noncommercial** | [repo](https://github.com/NVlabs/GENMO) [P] |
| CameraHMR | HMR with camera estimation | — | not stated | Python | 264 st · 2025-11 [P] | **no licence file — unclear** | [repo](https://github.com/pixelite1201/CameraHMR) [P] |
| EasyMocap | Multi-view mocap toolbox | ZJU | not stated | Python | 5.0k st · 2026-09 [P] | PRL v1.0 — free, **registration required before any use** | [repo](https://github.com/zju3dv/EasyMocap) [P] |
| MMPose (RTMPose etc.) | 2D/3D keypoint models | OpenMMLab | small | Python | 8.0k st · v1.3.2 (2024) [P] | Apache-2.0 | [repo](https://github.com/open-mmlab/mmpose) [P] |
| Sapiens | Human foundation models (pose, segmentation) | Meta | large | Python | 5.4k st [P] | CC BY-NC 4.0 | [repo](https://github.com/facebookresearch/sapiens) [P] |
| OnlineHMR | Streaming world-grounded HMR (on TRAM) | CVPR 2026 [S] | — | code not located | — | — | [CVF](https://openaccess.thecvf.com/content/CVPR2026/html/Zhao_OnlineHMR_Video-based_Online_World-Grounded_Human_Mesh_Recovery_CVPR_2026_paper.html) [S] |

Assessment: for commercial-clean use, the candidates are SAM 3D Body (SAM Licence) with MHR, or multi-camera Pose2Sim. Every SMPL-based model needs a Meshcapade licence for commercial use.

### A5 · Face capture (webcam, phone)

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| MediaPipe Face Landmarker | 52 blendshape scores, 478 3D landmarks, transform matrix | Google; very wide use | CPU/mobile GPU — all vendors | C++ core; Python, Web, Android (iOS page listed) | 37.5k st · 2026-10 · v1.2.0 [P] | Apache-2.0 | [docs](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker) [P] |
| OpenSeeFace | Webcam face tracking; ONNX CPU 30–60 fps; sends UDP | Basis of VSeeFace | CPU — all | Python + ONNX; C# receiver | 2.1k st · 2026-09 · v1.20.5 [P] | BSD-2 | [repo](https://github.com/emilianavt/OpenSeeFace) [P] |
| Live Link Face (Epic; free, proprietary) | iPhone ARKit face stream to UE Live Link; MetaHuman Animator capture (iPhone 12+); Android listed as beta | Epic | phone | closed iOS app; protocol undocumented publicly | App Store updates 2026 [S] | free app; closed | [App Store](https://apps.apple.com/DE/app/id1495370836) [S] |
| VMC performer apps (e.g. Waidayo, VSeeFace) | Phone or webcam to VMC blendshapes | listed by VMC spec | — | receive via VMC (A10) | — | per app | [VMC spec](https://protocol.vmc.info/english) [P] |
| SMIRK / VHAP (offline) | Video to FLAME expressions | see C14 | small | Python | see C14 | MIT + FLAME / CC BY-NC-SA | see C14 [P] |

### A6 · Lip-sync from audio or text

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| NVIDIA Audio2Face-3D (SDK + models v3.0) | Audio to facial motion (skin, tongue, jaw, eyeballs); emotion model | NVIDIA production model (2025-09-24) | **Yes: 4 GB+ GPU recommended; Turing supported** — **NVIDIA-only** (TensorRT/CUDA) | C++ SDK; Maya and UE5 plugins | 229 st SDK · 2025-08 [P] | SDK MIT; models NVIDIA Open Model (commercial yes); Audio2Emotion only with A2F; sample data evaluation only | [hub](https://github.com/NVIDIA/Audio2Face-3D), [card](https://huggingface.co/nvidia/Audio2Face-3D-v3.0) [P] |
| Rhubarb Lip Sync | Audio to mouth shapes (visemes); README not re-read | — | CPU — all | C++ CLI | 2.7k st · 2026-06 · v1.14.0 (2025-04) [P] | licence file has a summary plus third-party texts (not fully read) | [repo](https://github.com/DanielSWolf/rhubarb-lip-sync) [P] |
| uLipSync | Real-time lip-sync for Unity (README not re-read) | — | CPU | C# (Unity) | 1.7k st · 2026-01 · v3.1.4 [P] | MIT | [repo](https://github.com/hecomi/uLipSync) [P] |
| UniTalker | Unified audio to 3D face model | Research (venue not checked) | not stated | Python | 249 st · 2024-09 [P] | Apache-2.0 | [repo](https://github.com/X-niper/UniTalker) [P] |
| FaceFormer | Transformer audio to 3D face | Research (venue not checked) | small | Python | 919 st · 2023-08 [P] | MIT | [repo](https://github.com/EvelynFan/FaceFormer) [P] |
| ARTalk | Audio to FLAME head motion | — | not stated | Python; needs FLAME | 152 st · 2026-09 [P] | MIT + FLAME terms | [repo](https://github.com/xg-chu/ARTalk) [P] |
| Montreal Forced Aligner | Text + audio to phoneme timings (for text-driven lip-sync) | Widely used | CPU | Python | 1.9k st · v3.4.3 (2026-10) [P] | MIT | [repo](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner) [P] |
| WhisperX | ASR with word-level timestamps | 24.9k st | GPU/CPU | Python | v3.8.6 (2026-05) [P] | BSD-2 | [repo](https://github.com/m-bain/whisperX) [P] |
| FaceDiffuser / SAiD | Diffusion audio to ARKit blendshapes | Papers; a 2026 study retrains FaceDiffuser on 3DMEAD-ARKit | — | code not located | — | — | [FaceDiffuser](https://arxiv.org/pdf/2309.11306), [SAiD](https://arxiv.org/pdf/2401.08655), [2026 study](https://www.emergentmind.com/papers/2606.10753) [S] |

Assessment: Audio2Face-3D is the quality leader that fits 8 GB, but it is NVIDIA-only. A cross-vendor fallback is Rhubarb or MFA visemes driving ARKit-style shapes.

### A7 · Motion generation from text

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| HY-Motion 1.0 / Lite | DiT flow matching, 1.0B / 0.46B; 3,000+ h pretraining, 200+ categories | arXiv 2512.23464 [S] | **26 GB / 24 GB — no** [P] | Python | 2.6k st · 2026-07 [P] | Tencent HY-Motion Community — not in EU/UK/KR; >1M MAU needs a licence | [repo](https://github.com/Tencent-Hunyuan/HY-Motion-1.0) [P], [arXiv](https://arxiv.org/abs/2512.23464v1) [S] |
| MoMask | Masked residual-VQ text-to-motion | Research (venue not checked) | small (not stated) | Python | 1.3k st · 2024-09 [P] | MIT code; trained on HumanML3D (from AMASS — non-commercial) | [repo](https://github.com/EricGuo5513/momask-codes) [P] |
| MDM | Motion diffusion model | Research (venue not checked) | small (not stated) | Python | 4.1k st · 2025-10 [P] | MIT code; SMPL + HumanML3D | [repo](https://github.com/GuyTevet/motion-diffusion-model) [P] |
| T2M-GPT | VQ-VAE + GPT text-to-motion | Research (venue not checked) | small | Python | 781 st · 2024-09 [P] | Apache-2.0 code; HumanML3D | [repo](https://github.com/Mael-zys/T2M-GPT) [P] |
| MotionLCM (v2) | Real-time controllable latent consistency model | Research (venue not checked) | small | Python | 469 st · v2.0 (2025-01) [P] | **non-commercial** | [repo](https://github.com/Dai-Wenxun/MotionLCM) [P] |
| MotionGPT / MotionGPT3 | Language-model motion generation | — | not stated | Python | 2.0k / 245 st [P] | MIT / no licence file | [MotionGPT](https://github.com/OpenMotionLab/MotionGPT), [MotionGPT3](https://github.com/OpenMotionLab/MotionGPT3) [P] |
| MotionStreamer | Streaming text-to-motion | 2025 | not stated | Python | 304 st · 2026-09 [P] | PRL (registration required) | [repo](https://github.com/zju3dv/MotionStreamer) [P] |
| GEM / GENMO | see A4 | | | | | non-commercial | |

**No good open option** exists that is both commercial-clean and fits 8 GB. The weights that fit are trained on AMASS-derived data, which is non-commercial.

### A8 · Motion matching

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Motion-Matching (Holden) | Example motion matching and Learned Motion Matching demos | README links the Learned Motion Matching article | CPU | C++ (raylib) | 932 st · 2025-02 [P] | MIT | [repo](https://github.com/orangeduck/Motion-Matching) [P] |
| O3DE MotionMatching gem | Data-driven motion synthesis in an open engine | Engine gem | CPU | C++ | see C5 [P] | Apache-2.0 OR MIT | [gem README](https://github.com/o3de/o3de/tree/development/Gems/MotionMatching) [P] |

### A9 · Physics-based animation (Cascadeur-type)

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| MuJoCo | Articulated-body dynamics, contact; basis for trajectory optimisation and control | DeepMind; very wide use | CPU — all | C/C++ (+Python) | 16.0k st · 2026-10 · 3.17.0 [P] | Apache-2.0 | [repo](https://github.com/google-deepmind/mujoco) [P] |
| ProtoMotions (v3) | Physics-based character controllers learned from AMASS (MaskedMimic family) | NVIDIA; AMASS in ~12 h training | training: big GPUs; backends Isaac (NVIDIA), others not checked | Python | 2.5k st · 2026-10 · tag v3.2 [P] | Apache-2.0 code; SMPL/AMASS data terms | [repo](https://github.com/NVlabs/ProtoMotions) [P] |
| PHC | Perpetual humanoid control (SMPL) | Research (venue not checked) | not stated | Python | 1.3k st · 2025-08 [P] | BSD-3-Clause-Clear; SMPL | [repo](https://github.com/ZhengyiLuo/PHC) [P] |
| CLoSD | Diffusion plus physics control | Research (venue not checked) | not stated | Python | 503 st · 2025-05 [P] | MIT | [repo](https://github.com/GuyTevet/CLoSD) [P] |
| DeepMimic | RL imitation of mocap | Research (venue not checked) | CPU/GPU | C++/Python | 3.1k st · 2025-11 [P] | MIT | [repo](https://github.com/xbpeng/DeepMimic) [P] |
| Jolt animated ragdolls | Drive ragdolls from animation (motors) | see S1 | CPU | C++ | [P] | MIT | [README](https://github.com/jrouwe/JoltPhysics) [P] |
| Cascadeur (free tier, proprietary) | AutoPhysics, AutoPosing (reference app) | — | — | closed app | — | free tier for personal or hobby use [S]; paid Pro | [cascadeur.com](https://cascadeur.com/learn/physics/the_basics_of_physics_in_cascadeur) [S] |

**No good open option** exists for animator-facing physics tools: making a keyframed clip physically plausible, ballistic arcs, centre-of-mass and fulcrum editing. The building blocks are MuJoCo or Jolt plus trajectory optimisation (our code).

### A10 · Live mocap streams and devices

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| VMC protocol | OSC/UDP; bones (`/VMC/Ext/Bone/Pos`), root, blendshapes; ports 39539/39540 | Used by VSeeFace, VirtualMotionCapture, Waidayo, SlimeVR, XR Animator; receivers for Unity, UE, Blender, Godot | — | protocol | — | spec MIT | [spec](https://protocol.vmc.info/english) [P] |
| liblo / oscpack / rosc | OSC libraries | — | CPU | C / C++ / Rust | 0.36 (2026-06) / 2019 / v0.11.4 (2025) [P] | LGPL-2.1 / MIT-style / Apache-2.0 | [liblo](https://github.com/radarsat1/liblo), [oscpack](https://github.com/RossBencina/oscpack), [rosc](https://github.com/klingtnet/rosc) [P] |
| SlimeVR (server + open trackers) | IMU full-body trackers; OSC and VMC send/receive | Large hobby community | — | server app; ESP firmware | 1.0k st · 2026-10 · v21.1.0 [P] | Apache-2.0 (server) | [repo](https://github.com/SlimeVR/SlimeVR-Server) [P] |
| XR Animator | Single-webcam full-body tracking; VMC output (desktop build) | — | browser/Electron — all | JavaScript | 2.0k st · 2026-10 · v0.36.0 [P] | **no licence file — unclear** | [repo](https://github.com/ButzYung/SystemAnimatorOnline) [P] |
| VirtualMotionCapture | VR-tracker mocap app; VMC performer | — | — | C# | 827 st · v0.60f1 [P] | MIT | [repo](https://github.com/sh-akira/VirtualMotionCapture) [P] |
| Rokoko Studio + Live plugins | Studio (closed, free tier not verified) streams to plugins; hardware paid | Official | — | plugin Python | see A1 [P] | plugin LGPL-3/MIT conflict | [repo](https://github.com/Rokoko/rokoko-studio-live-blender) [P] |
| Xsens MVN network streamer | UDP/TCP; 23 segments' pose, velocity, acceleration; spec PDF public; hardware paid | Lab reports of frame loss | — | protocol | spec rev N (2018) | spec free | [PDF](https://www.xsens.com/hubfs/Downloads/Manuals/MVN_real-time_network_streaming_protocol_specification.pdf) [S] |
| Noitom MocapApi | Perception Neuron SDK | — | — | C# / C | 51 st · r1 (2022) [P] | **no licence file — unclear** | [repo](https://github.com/pnmocap/MocapApi) [P] |
| Live Link Face / ARKit | see A5 (free, proprietary) | | | | | | |

---

## Scene

### S1 · Physics engines (core: cross-vendor)

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Jolt Physics | Rigid bodies, deterministic sim, ragdolls (animated), vehicles, soft bodies, GPU hair (DX12/VK/Metal/CPU) | 11.8k stars | any vendor | C++ | 11.8k st · 2026-10 · v5.6.0 [P] | MIT | [repo](https://github.com/jrouwe/JoltPhysics) [P] |
| Rapier | Rigid bodies, joints, character controller | Rust ecosystem standard | CPU | Rust | 6.0k st · 2026-10 · tag v0.36.1 [P] | Apache-2.0 | [repo](https://github.com/dimforge/rapier) [P] |
| MuJoCo | Articulated dynamics (see A9) | | CPU | C/C++ | [P] | Apache-2.0 | [repo](https://github.com/google-deepmind/mujoco) [P] |
| PhysX 5 (CPU parts) | Rigid bodies, articulations; GPU features are CUDA (vendor split not re-checked) | NVIDIA; widely shipped | CPU — all; GPU parts out | C++ | 4.8k st · 2026-10 · tag 5.9.1 [P] | BSD-3 | [repo](https://github.com/NVIDIA-Omniverse/PhysX) [P] |
| Bullet | Rigid and soft bodies | Old; last release 2022 | CPU | C++ | 14.8k st · 3.25 (2022) [P] | zlib | [repo](https://github.com/bulletphysics/bullet3) [P] |
| Genesis | Multi-physics (see C11) | | any vendor | Python | [P] | Apache-2.0 | [repo](https://github.com/Genesis-Embodied-AI/genesis-world) [P] |

### S2 · Particles and FX

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Effekseer | Particle editor plus runtime; DX9/11/12, Metal, Vulkan, OpenGL; Unity, Godot and UE plugins | — | any vendor | C/C++ runtime; editor app | 1.8k st · 2026-10 · 1807 (2026-08) [P] | MIT | [repo](https://github.com/effekseer/Effekseer) [P] |
| bevy_hanabi | GPU particle system for Bevy | Rust ecosystem | any vendor (wgpu) | Rust | 1.4k st · 2026-10 · tag v0.19.0 [P] | Apache-2.0 (MIT dual per crate norm, not checked) | [repo](https://github.com/djeedai/bevy_hanabi) [P] |
| OpenVDB / NanoVDB | Volumes for smoke and fire caches | ASWF standard | CPU (+GPU NanoVDB) | C++ | see C1 [P] | Apache-2.0 | [repo](https://github.com/AcademySoftwareFoundation/openvdb) [P] |
| Mantaflow (in Blender `extern/`) | Smoke and fluid sim (offline) | Shipped in Blender | CPU | C++ | bundled [P] | not read | [extern](https://github.com/blender/blender/tree/main/extern) [P] |
| NVIDIA Flow (`flow/` in PhysX repo) | GPU fluid / smoke | — | vendor not checked | C++ | in PhysX repo [P] | BSD-3 (repo) | [repo](https://github.com/NVIDIA-Omniverse/PhysX) [P] |
| PopcornFX | **OUT (paid)**: PLE free plan is "exclusively for non-commercial and educational purposes"; Indie €25–30/month etc.; plugins free download but "A runtime licensing fee could be required for non-indy game studios" | | | | | commercial | [pricing](https://www.popcornfx.com/pricing/) [P] |

### S3 · Path tracer beside the real-time viewport (embeddable)

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Cycles standalone / Hydra | Production path tracer; devices CPU, CUDA, OptiX, HIP, HIP-RT, Metal, oneAPI | Blender's renderer | any vendor | C++ library or Hydra delegate | 662 st · 2026-10 · tag v5.2.0 [P] | Apache-2.0 | [repo](https://github.com/blender/cycles) [P] |
| MoonRay | Production path tracer (DreamWorks) | README: production renderer for animation and VFX | CPU — all; GPU mode vendor not checked | C++; Hydra delegate (not re-read) | 4.7k st · 2026-10 · v2026.29.1 [P] | Apache-2.0 | [repo](https://github.com/OpenMoonRay/openmoonray) [P] |
| OSPRay (+ Embree, OIDN) | CPU ray-tracing engine | Intel | CPU (+Intel GPU) | C/C++ | 1.1k st · v3.2.0 (2024) [P] | Apache-2.0 | [repo](https://github.com/RenderKit/ospray) [P] |
| LuxCoreRender | Unbiased path tracer | — | CPU/OpenCL/CUDA | C++ (+Python wheels) | 1.3k st · v2.11.2 (2026-09) [P] | Apache-2.0 | [repo](https://github.com/LuxCoreRender/LuxCore) [P] |
| Mitsuba 3 | Research differentiable renderer | Academic standard | CPU/CUDA | C++/Python | 3.0k st · v3.9.0 [P] | BSD-3 | [repo](https://github.com/mitsuba-renderer/mitsuba3) [P] |
| pbrt-v4 | Reference renderer (book) | Academic standard | CPU/GPU | C++ | 3.7k st · no releases [P] | Apache-2.0 | [repo](https://github.com/mmp/pbrt-v4) [P] |
| Radeon ProRender USD | Hydra delegate | AMD; last release 2024 | any vendor (not re-checked) | C++ | 242 st · v3.0.4 (2024) [P] | Apache-2.0 | [repo](https://github.com/GPUOpen-LibrariesAndSDKs/RadeonProRenderUSD) [P] |
| Bevy Solari | Ray-traced lighting crate in Bevy | New | wgpu (hardware RT; vendors not checked) | Rust | in Bevy [P] | MIT/Apache | [crate](https://github.com/bevyengine/bevy/tree/main/crates/bevy_solari) [P] |

Assessment: Cycles is the clear fit. It covers every GPU vendor, embeds as a library or a Hydra delegate, and Blender users already know its look.

### S4 · Terrain and sky

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| Hillaire sky/atmosphere | Sky and atmosphere technique demo (repo named for UE) | venue not checked | any GPU | C++/HLSL demo | 865 st · 2022-09 [P] | MIT | [repo](https://github.com/sebh/UnrealEngineSkyAtmosphere) [P] |
| Bruneton precomputed scattering | Precomputed atmospheric scattering | Widely cited | any GPU | C++/GLSL | 1.1k st · 2025-10 [P] | BSD-3 | [repo](https://github.com/ebruneton/precomputed_atmospheric_scattering) [P] |
| Terrain3D | Clipmap terrain editor and runtime for Godot | Active | any GPU | C++ GDExtension | 4.5k st · v1.0.2 (2026-05) [P] | MIT | [repo](https://github.com/TokisanGames/Terrain3D) [P] |
| HTerrain (Zylann) | Heightmap terrain for Godot | — | any GPU | GDScript | 2.3k st · 2026-07 [P] | MIT | [repo](https://github.com/Zylann/godot_heightmap_plugin) [P] |
| O3DE Terrain gem | Engine terrain | — | any GPU | C++ | [P] | Apache-2.0 OR MIT | [Gems](https://github.com/o3de/o3de/tree/development/Gems) [P] |
| TerraForge3D | Procedural terrain app (noise, erosion) | Last release 2022 | GPU | C++ | 1.3k st · v2.3 (2022) [P] | MIT | [repo](https://github.com/Jaysmito101/TerraForge3D) [P] |
| FastNoise2 | SIMD noise generation | — | CPU | C++ | 1.5k st · v1.1.1 (2026-02) [P] | MIT | [repo](https://github.com/Auburn/FastNoise2) [P] |

Assessment: no maintained open world-generator with erosion at Gaea or World Machine level; TerraForge3D's last release was 2022.

### S5 · Audio

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| miniaudio | Playback, capture, mixing, decoding | Single-file, widely used | CPU | C | 7.4k st · 0.11.25 (2026-03) [P] | choice of public domain or MIT-0 | [repo](https://github.com/mackron/miniaudio) [P] |
| Steam Audio | Spatial audio (HRTF, occlusion, reverb) | Valve | CPU | C/C++ (+plugins) | 3.0k st · v4.8.1 (2026-02) [P] | Apache-2.0 | [repo](https://github.com/ValveSoftware/steam-audio) [P] |
| OpenAL Soft | 3D audio API | Long-running | CPU | C/C++ | 2.8k st · 1.25.2 [P] | LGPL-2 | [repo](https://github.com/kcat/openal-soft) [P] |
| kira / cpal | Game audio / audio I/O | Rust ecosystem | CPU | Rust | v0.12.6 / v0.18.2 [P] | Apache-2.0 (per GitHub) | [kira](https://github.com/tesselode/kira), [cpal](https://github.com/RustAudio/cpal) [P] |
| SoLoud | Game audio engine | Stale (2020 release) | CPU | C++ | 2.2k st · 2024-08 [P] | zlib-style | [repo](https://github.com/jarikomppa/soloud) [P] |

---

## File I/O and core formats

### F1 · Formats and libraries

| option | does | quality evidence | 8 GB fit | language / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| ufbx | FBX reader (meshes, skinning, blend shapes, subdivision eval); no writer in repo | Used by Blender's new C++ importer (`bf::extern::ufbx`) | CPU | single C file | 1.4k st · 2026-10 · tag v0.23.1 [P] | dual: MIT or public domain | [repo](https://github.com/ufbx/ufbx), [Blender CMake](https://github.com/blender/blender/tree/main/source/blender/io/fbx) [P] |
| Autodesk FBX SDK 2020.3.11 (free, proprietary) | Official FBX read and **write** | Industry reference | CPU | closed C++ SDK; Windows, macOS, iOS, Linux | — | free under its EULA; redistribution terms not on page (EULA not read) | [page](https://aps.autodesk.com/developer/overview/fbx-sdk) [P] |
| Assimp | 40+ formats import; export incl. FBX | Widely used | CPU | C++ | 13.3k st · v6.0.5 (2026-04) [P] | BSD-3-style | [repo](https://github.com/assimp/assimp) [P] |
| OpenFBX | Lightweight FBX reader | — | CPU | C/C++ | 1.4k st · 2026-05 · tag v0.9 [P] | MIT | [repo](https://github.com/nem0/OpenFBX) [P] |
| OpenUSD | Scene description, composition, Hydra | Industry standard | CPU (+Hydra Storm GPU) | C++/Python | 7.6k st · v26.11.1 (2026-10-21) [P] | TOST 1.0 (Apache-2.0 with changed trademark clause) | [repo](https://github.com/PixarAnimationStudios/OpenUSD) [P] |
| LightUSD (was TinyUSDZ) | Dependency-light USD/USDZ reader/writer | Renamed 2025–26 | CPU | C++ | 733 st · tag v1.0.0-rc4 [P] | Apache-2.0 | [repo](https://github.com/lighttransport/LightUSD) [P] |
| Alembic | Baked geometry caches | VFX standard | CPU | C++ | 1.2k st · 1.8.12 (2026-07) [P] | BSD-3 | [repo](https://github.com/alembic/alembic) [P] |
| cgltf / tinygltf / fastgltf | glTF readers (and writers for cgltf, tinygltf) | Widely used | CPU | C / C++ / C++ | v1.15 / v3.0.1 / v0.9.1 [P] | MIT | [cgltf](https://github.com/jkuhlmann/cgltf), [tinygltf](https://github.com/syoyo/tinygltf), [fastgltf](https://github.com/spnda/fastgltf) [P] |
| gltf (Rust) | glTF crate | — | CPU | Rust | 645 st · 1.0.0 (2022), push 2026-05 [P] | Apache-2.0/MIT | [repo](https://github.com/gltf-rs/gltf) [P] |
| KTX-Software / Draco / meshoptimizer | GPU textures / mesh compression | Khronos / Google | CPU | C++ | v4.4.2 (v5.0.0-rc2) / 1.5.9 / v1.3 [P] | KTX licence file (Apache-2.0 per Khronos, not re-read) / Apache-2.0 / MIT | [KTX](https://github.com/KhronosGroup/KTX-Software), [Draco](https://github.com/google/draco) [P] |
| VRM specification | Humanoid avatar extension of glTF | VTuber standard | — | spec | 345 st · 2026-10 [P] | no licence file via API | [repo](https://github.com/vrm-c/vrm-specification) [P] |
| OpenImageIO | Image I/O and processing | ASWF | CPU | C++/Python | 2.4k st · v3.2.2.0 (2026-10) [P] | Apache-2.0 | [repo](https://github.com/AcademySoftwareFoundation/OpenImageIO) [P] |
| OpenEXR | HDR image format | ASWF | CPU | C/C++ | 1.9k st · v3.5.2 (2026-10) [P] | BSD-3 | [repo](https://github.com/AcademySoftwareFoundation/openexr) [P] |
| OpenColorIO | Colour management | ASWF | CPU/GPU | C++ | 2.1k st · v2.6.0 (2026-10) [P] | BSD-3 | [repo](https://github.com/AcademySoftwareFoundation/OpenColorIO) [P] |
| MaterialX + OpenPBR | Material graphs; OpenPBR surface | ASWF | CPU (codegen to GLSL/MSL/OSL) | C++/Python | v1.39.5 / OpenPBR v1.1.1 [P] | Apache-2.0 | [MaterialX](https://github.com/AcademySoftwareFoundation/MaterialX), [OpenPBR](https://github.com/AcademySoftwareFoundation/OpenPBR) [P] |
| OpenSubdiv | Subdivision surfaces (CPU/GPU eval) | Pixar standard | any vendor | C++ | 3.1k st · v3_8_0 (2026-10-23) [P] | TOST 1.0 | [repo](https://github.com/PixarAnimationStudios/OpenSubdiv) [P] |

**No good open option** exists for FBX writing. Only Autodesk's closed free SDK, or Assimp's exporter (quality not checked), can write FBX.

---

## Content libraries

### L1 · Motion and asset libraries

| option | holds | quality evidence | 8 GB fit | format / integration | health | licence | source |
|---|---|---|---|---|---|---|---|
| CMU Graphics Lab mocap | Large free mocap set | Classic | — | ASF/AMC (BVH conversions exist) | — | **not verified** (site certificate failed for the fetcher) | [mocap.cs.cmu.edu](http://mocap.cs.cmu.edu/) — unread |
| AMASS | Archive of mocap as SMPL surface shapes | Research standard | — | SMPL params | — | **non-commercial**; no redistribution; no training for commercial use | [licence](https://amass.is.tue.mpg.de/license.html) [P] |
| LAFAN1 (Ubisoft) | 5 subjects, 77 sequences, 496,672 frames @30 fps (~4.6 h) | Used in motion research | — | BVH | 1.6k st [P] | CC BY-NC-ND 4.0 | [repo](https://github.com/ubisoft/ubisoft-laforge-animation-dataset) [P] |
| Bandai Namco Research Motion | Two sets (36,673 and 384,931 frames), 3 professional actors | — | — | BVH | 3.4k st [P] | CC BY-NC 4.0 | [repo](https://github.com/BandaiNamcoResearchInc/Bandai-Namco-Research-Motiondataset) [P] |
| 100STYLE | 4M+ frames, 100 locomotion styles, 60 fps, 28-bone skeleton | Used in style research | — | BVH | — | **CC BY 4.0 (commercial yes, credit)** | [page](https://www.ianxmason.com/100style/) [P] |
| HumanML3D | Text-annotated motions derived from AMASS | Text-to-motion benchmark | — | features + text | 1.6k st [P] | MIT code; data inherits AMASS terms | [repo](https://github.com/EricGuo5513/HumanML3D) [P] |
| Motion-X | Whole-body motion with text | — | — | SMPL-X | 905 st [P] | **non-commercial** | [repo](https://github.com/IDEA-Research/Motion-X) [P] |
| Quaternius Universal Animation Library | 120+ animations on a universal humanoid rig | — | — | FBX, GLB, Blend | — | CC0; Standard tier ~60–70% free, Pro/Source paid | [page](https://quaternius.com/packs/universalanimationlibrary.html) [P] |
| Mesh2Motion | Models, rigs and animations for its web auto-animator | Active | — | GLB/Blend | 3.6k st [P] | CC0 (assets) | [repo](https://github.com/Mesh2Motion/mesh2motion-app) [P] |
| MakeHuman assets (via MPFB2) | Base mesh, targets, clothes, rigs, poses, expressions | Long-running | — | MakeHuman formats | [P] | CC0 | [LICENSE](https://github.com/makehumancommunity/mpfb2) [P] |
| Poly Haven | HDRIs, textures, 3D models | Widely used | — | EXR/HDR, PBR maps, glTF/Blend | — | CC0 (site ToS restricts scraping) | [licence](https://polyhaven.com/license) [P] |
| Mixamo (free, proprietary) | Characters and animations | Widely used | — | FBX | — | free, royalty-free commercial use; **no redistribution of raw files; no ML training** (FAQ 2022) | [FAQ](https://community.adobe.com/t5/mixamo-discussions/mixamo-faq-licensing-royalties-ownership-eula-and-tos/m-p/13234775) [P] |

Assessment: a built-in motion library that can ship in the app must come from CC0 or CC-BY sets: Quaternius free tier, Mesh2Motion, 100STYLE, and CMU if its terms are confirmed. LAFAN1, Bandai Namco, AMASS and Motion-X are research-only.

---

## Couldn't verify / open

- **Search budget.** The session's shared WebSearch budget ran out. Everything after that came from WebFetch on known official URLs and from GitHub's API.
- **CMU mocap terms:** the site's certificate failed for the fetcher, so the commercial-use and resale wording is unverified.
- **Blender's dynamic topology** was not found by file-name search in `editors/sculpt_paint` (Blender 5.x). Blender hair curves and grooming tools were not checked.
- **VRAM not stated** (needs a test run or model card):
  - SAM 3D Body and SAM 3D Objects
  - Stable3DGen, Step1X-3D (numbers not extracted from its table)
  - Puppeteer, MagicArticulate, Make-It-Animatable
  - WHAM, GVHMR, NLF, GENMO
  - MoMask, MDM, T2M-GPT
  - ChatGarment, DiffLocks
- **GPU vendor support for most PyTorch models** is unverified beyond the READMEs that state CUDA or NVIDIA (TRELLIS, TRELLIS.2, TripoSG, PartCrafter, UniRig, SkinTokens, Audio2Face).
- **Free-but-proprietary terms not read in full:**
  - Autodesk FBX SDK EULA, including redistribution of its libraries
  - Mixamo's current Terms of Use; the FAQ read is from 2022
  - Live Link Face (App Store snippets only)
  - Rokoko Studio's free tier
  - Cascadeur's free tier (search snippet only)
- **Licences not resolved:**
  - Rokoko Blender plugin: LGPL-3 per GitHub vs MIT per its README badge
  - Rhubarb Lip Sync: full licence text not read
  - No licence file found: XR Animator, CameraHMR, DressCode, MotionGPT3, Noitom MocapApi, lightmapper, VRM spec
  - CGAL: per-package terms not read
  - KTX-Software: licence file not read in full
- **Algorithms and papers not fetched:** VBD (Vertex Block Descent), XPBD, Stable Cosserat Rods, PSD/RBF correctives, Jimenez eye rendering. Newton (out for the core) contains VBD and Style3D solvers.
- **Not checked:**
  - Neural retopology models: DeepMesh, BPT, QuadGPT, Meshtron
  - Hi3D v1.0, an open image-to-3D model reported 2026-10 on X [S]; repo not located
  - Sony mocopi and its VMC support
  - OptiTrack NatNet and Vicon DataStream SDKs
  - Live Link (UE plugin) terms
  - TressFX 5.0's distribution and licence (snippet only)
  - Whether Godot's IK modifiers are in a stable release (seen in `master` source)
  - MoonRay's GPU back-end vendors
  - PhysX's CPU/GPU feature split
  - OIDN's GPU vendor list
- **Also open:**
  - Kenney and ambientCG (CC0 asset sites) not fetched
  - A quantised TRELLIS.2 at 6 GB is a snippet claim only
  - Pixal3D's 10–12 GB low-VRAM figure comes from a third-party blog
