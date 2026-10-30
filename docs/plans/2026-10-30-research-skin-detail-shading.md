# Skin that reads as a photo: fine detail, shading, light, upscaling, eyes (research, 2026-10-30)

Research agent's report for JustStage (Blender 5.3 extension). Asked for: what makes rendered skin read as a real photo.
The trigger: our render looks waxy. Pores and wrinkles come only from a bump map made from image brightness, which
turns painted shadows into dents. The shine is the same everywhere, and the eyes look pasted on.

**How to read this.** Options are **ranked by how good the method is**. Licence, memory (VRAM) and graphics-card
support are facts written beside each one. They were never used to drop or demote anything. Every method carries a
bucket:

- **(a)** needs no trained model;
- **(b)** runs on open weights that already exist (named, with their licence);
- **(c1)** needs a small LoRA or a tiny special-purpose model that fits the 8 GB card (the base model and the trainer's
  documented VRAM are given);
- **(c2)** needs real training we can't do. Each (c2) gets a training-free way to do the same job next to it.

Evidence labels: **measured** = run on this machine (Blender 5.3.0 Beta, `E:/blender-5.3.0-beta`, `--factory-startup`);
**API** = GitHub or Hugging Face API, or a licence or README file read raw; **page read** = the page itself was fetched
and read; **search snippet** = only a search result's summary was seen.

Plain words used below:
- **Normal map**: a picture whose colours say which way each tiny bit of surface faces. Light then shades bumps that
  aren't in the mesh.
- **Bump map**: a grey picture used the same way, by its slope.
- **Displacement**: a grey picture that really moves the surface in or out. Its silhouette and shadows change too.
- **Cavity map**: a grey picture that is dark in pores and creases. It is used to take the shine out of them.
- **SSS** (subsurface scattering): light goes into skin, spreads under it and comes out nearby. This is why skin glows
  red at its edges and in its shadows.
- **Specular / lobe**: the shine and the shape of its highlight.
- **Roughness**: how blurred that highlight is.
- **IOR**: how strongly a surface bends and reflects light.
- **HDRI**: a 360° photo of real light used to light a scene.

---

## Summary table

| # | Job | Best methods found, best first | Bucket | Code / weights licence | Runs on | Evidence |
|---|---|---|---|---|---|---|
| 1 | Take the lighting out of a painted or photographed face before anything else, so painted shadows stop becoming dents | 1 **OpenDelight** (SIGGRAPH 2026, face-specific). 2 **Marigold IID** (albedo / shading / roughness). 3 **StableDelight** (removes highlights) | (b) | OpenDelight GPL-3.0 code and dataset; Marigold IID weights openrail++; StableDelight weights apache-2.0 | PyTorch; VRAM not stated | API |
| 2 | Real relief (wrinkles, folds, lids, lips) from an image of a person | 1 **Sapiens2 normals** (human-only model, 1K, 4K variants). 2 **StableNormal**. 3 **Marigold normals v1.1** / **E2E-FT**. 4 **MoGe-2 normals** (official ONNX) | (b) | Sapiens2: custom licence, no non-commercial clause, bans deepfakes and biometric use. StableNormal apache-2.0. Marigold openrail++. E2E-FT apache-2.0. MoGe-2 MIT | All PyTorch; MoGe-2 also ONNX Runtime (any GPU) | API |
| 3 | Normal map → height map, and true displacement in the render | Normal integration (Frankot–Chellappa); Blender's **multires bake** to (vector) displacement + **adaptive subdivision** (no longer experimental since 5.0) | (a) | Blender GPL | Any | measured + release notes |
| 4 | Pores and micro-wrinkles | 1 **Graph-based micro-wrinkle synthesis** (Disney, SGP 2023). 2 **Example-based from scanned patches** (a CC-BY 3.0 scan exists). 3 **Tension-driven procedural wrinkles** (Blender Studio, *Charge*). 4 AI-made tiles from FLUX.2 klein | (a), (a), (a); klein (b) or (c1) | Disney: paper only. Scan: CC-BY 3.0. klein: apache-2.0 | Any; klein LoRA ~8 GB int8 (SimpleTuner) | snippet / page read / API |
| 5 | Wrinkles that come and go with expressions | Wrinkle maps blended by blendshape weights × region masks (the CC5 / MetaHuman way); tension maps (Unity *Heretic*, Blender Studio) | (a) | — | Any | page read / snippet |
| 6 | Skin shader | Cycles Principled **Random Walk (Skin)** + per-region roughness + a cavity map that takes shine out of pores + a second highlight lobe + a little sheen (fine facial hair) | (a) | Blender GPL | Cycles: any GPU | measured + manual |
| 7 | EEVEE skin | Thickness-based SSS approximation. **No Random Walk, IOR or anisotropy** in EEVEE (manual); EEVEE is the preview, Cycles the final render | (a) | — | Any | manual (API raw) |
| 8 | Light | AgX view (or Khronos PBR Neutral / ACES 2.0 — all present in 5.3); CC0 Poly Haven studio HDRI + one big soft key + a kicker; Cycles **MNEE shadow caustics** for the eyes | (a) | Poly Haven CC0 | Any | measured + API + manual |
| 9 | Upscaling textures to 4K–8K | 1 **SeedVR2** (one-step diffusion). 2 **SUPIR**. 3 DAT / HAT-class models (OpenModelDB, CC-BY / CC0). 4 **Real-ESRGAN / MoSR inside stable-diffusion.cpp** | (b) | SeedVR2 apache-2.0. SUPIR **non-commercial**. DAT-class CC-BY-4.0 / CC0. Real-ESRGAN BSD-3 | SeedVR2: "8GB or less" with GGUF Q4 + BlockSwap; sd.cpp: any GPU | API |
| 10 | Eyes | Shells: eye occlusion, tearline, eye blend (MIT topology in ICT-FaceKit). Cornea as real refraction (Cycles + MNEE, or a shadow-ray trick); EEVEE raytraced refraction; parallax eyes as the cheap path | (a) | ICT-FaceKit MIT | Any | API + manual |

**The cause of the waxy look, from our own code** (read 2026-10-30):
- `modules/skin/material.py` sets one roughness for the whole body (`ROUGHNESS = sqrt(0.35)` ≈ 0.59). It has no
  cavity map, no second lobe and no sheen.
- `modules/skin/detail.py` feeds an image's brightness to a Bump node (0.1 mm range). That is the shadows-become-dents
  path.
- The pro pipelines below never take pore height from colour brightness. Pores come from scanned or synthesised
  height, and colour is delit first.

---

## 1 · Relief from images: normals, displacement, cavity

### 1.0 The real fix comes first: take the light out (delighting)

A painted shadow becomes a dent because shading and colour arrive mixed in one picture. Every pro skin pipeline
separates them: light-stage scans capture colour under even, cross-polarised light (USC ICT, below). With AI pictures,
the separation has to be done by a model:

1. **OpenDelight** — "Learning a Delighting Prior for Facial Appearance Capture in the Wild", Han et al., SIGGRAPH
   2026 Journal ([arXiv 2605.05636](https://arxiv.org/abs/2605.05636), page read;
   [yxuhan/OpenDelight](https://github.com/yxuhan/OpenDelight), API).
   - **How it works:** a network trained to turn a lit face picture into the same face under even light. Training data:
     one-light-at-a-time (OLAT) light-stage data plus rendered light-stage scans. "Dataset Latent Modulation"
     (learnable tokens that say which source an image came from) lets it learn from both. In the paper it is a prior
     that steers a smartphone-video appearance capture.
   - **Quality:** the README says it beats "the best proprietary model, SwitchLight, with significantly fewer
     shadow-baking artifacts". This is the authors' claim; no independent test was found.
   - **Steps for us:** cut each painted view to the face; run delighting; project the delit colour (our
     `tools/face_test` projection already exists); keep the removed shading only as a hint for relief.
   - **Licence:** code GPL-3.0 (API). Dataset `yxuhan76/OpenDelight-Dataset` gpl-3.0 (HF API, 2026-05-05). The
     pretrained weights are a Google Drive link in `doc/TEST.md` with no separate licence stated. The dataset is built
     from Meta's Ava-256 (its own terms not read).
   - **Runs on:** PyTorch. Inference VRAM not stated. Retraining: "2 × NVIDIA RTX 3090 GPUs … 3–4 days" (README) —
     beyond us.
   - **Bucket:** (b) to use; (c2) to retrain. Last push 2026-05-08.
2. **Marigold IID** (prs-eth). Already in RESEARCH §10:
   - **How it works:** SD2's denoiser fine-tuned to output intrinsic layers instead of a picture: albedo, roughness and
     metallicity ("appearance"), or albedo, diffuse shading and residual ("lighting").
   - **Licence:** weights `prs-eth/marigold-iid-appearance-v1-1` and `-lighting-v1-1` openrail++ (HF API, 2025-05-20);
     code Apache-2.0 (last push 2026-09-06).
   - **Bucket:** (b).
   - **Note:** ArmorPaint published all Marigold v1.1 sets as GGUF (`armory3d/marigold-v1-1-gguf`: depth, IID
     appearance, IID lighting, normals, q4_0/q8_0; licence "openrail"; 2025-11-14, HF API). That suggests a ggml
     (stable-diffusion.cpp-style) runtime once ran them. Its pointer `github.com/armory3d/stable-diffusion.cpp`
     returns 404, so this is unverified.
3. **StableDelight** (Stable-X, [repo](https://github.com/Stable-X/StableDelight)) — removes specular highlights
   from a picture, so shine doesn't turn into bumps.
   - **Licence:** README badge Apache-2.0, but no LICENSE file (API). Weights `Stable-X/yoso-delight-v0-4-base`
     apache-2.0 (HF API).
   - **Bucket:** (b). Last push 2025-09-18.
4. Also found:
   - **MAGINet** ([arXiv 2512.16511](https://arxiv.org/abs/2512.16511), 2025-12): face intrinsics, 512² albedo
     refined to 1024². Code and licence not found.
   - **Careaga & Aksoy** intrinsic decomposition ([compphoto/Intrinsic](https://github.com/compphoto/Intrinsic)):
     "for academic use only", with a patent note (API).
   - SwitchLight (Beeble): proprietary.
- **Training-free fallback (a):** paint the views under flat, frontal, even light. That means a prompt plus a clay
  render lit by an even white world, which RESEARCH §10 already measured. Then do frequency separation: only the
  highest band, pore scale, is ever read as relief. This lessens the problem but cannot solve it: painted mid-scale
  shading (nasolabial shadows, under-eye) still leaks in.

### 1.1 Normals from a single picture, ranked

| Rank | Method | How it works (short) | Paper | Code licence, last push | Weights, licence | Bucket |
|---|---|---|---|---|---|---|
| 1 | **Sapiens2 normals** (Meta, ICLR 2026) | Vision transformer pretrained on 1 B human images (masked reconstruction + self-distilled contrastive). A dense head regresses camera-space unit normals. "native 1K resolution and hierarchical variants that support 4K". Sizes 0.4 / 0.8 / 1 / 5 B | [arXiv 2604.21681](https://arxiv.org/abs/2604.21681) (page read) | Sapiens2 License (custom), push 2026-05-24 | `facebook/sapiens2-normal-{0.4b,0.8b,1b,5b}`, "sapiens2-license", not gated (HF API, 2026-06-15); community ONNX ports exist (`WeReCooking/sapiens2-onnx`, 0 downloads — untested) | (b) |
| 2 | **StableNormal** (SIGGRAPH Asia 2024) | Reduces diffusion's randomness. A one-step "YOSO" coarse normal from an SD2-based model, then a refinement guided by semantic (DINO) features for sharp detail. A "turbo" variant is 10× faster | [arXiv 2406.16864](https://arxiv.org/abs/2406.16864) | Apache-2.0, 2025-08-02 | `Stable-X/stable-normal-v0-1` and `yoso-normal-v1-8-1` apache-2.0 (HF API); SD2 base is openrail++ | (b) |
| 3 | **Marigold normals v1.1** / **E2E-FT** | Marigold: SD2's denoiser fine-tuned to generate a normal latent conditioned on the image latent, 1–4 steps, ensembling. E2E-FT: the same model made single-step and deterministic and fine-tuned end-to-end — "200×" faster and better (authors) | [arXiv 2505.09358](https://arxiv.org/abs/2505.09358), [arXiv 2409.11355](https://arxiv.org/abs/2409.11355) | Marigold Apache-2.0, 2026-09-06; E2E-FT repo has no licence file, 2026-07-09 | `prs-eth/marigold-normals-v1-1` openrail++; `GonzaloMartinGarcia/stable-diffusion-e2e-ft-normals` apache-2.0 (HF API) | (b) |
| 4 | **MoGe-2** (Microsoft) | DINOv2 vision transformer predicting metric point map, depth and normals in one pass. Built for scenes and objects, so it resolves folds and lids, not pores | [arXiv 2507.02546](https://arxiv.org/abs/2507.02546) | MIT, 2026-10-24 | `Ruicheng/moge-2-vitl-normal` mit (HF API, 2026-09-02) + official `…-onnx` repos for vits / vitb / vitl | (b) — the only top option already in ONNX (the family's ONNX Runtime, any GPU) |
| 5 | **Lotus / Lotus-2** | Lotus: SD2 made to predict the answer directly (x0) in one step. Lotus-2: FLUX.1-dev-based, "at least 40GB" GPU (README) | [arXiv 2409.18124](https://arxiv.org/abs/2409.18124), [arXiv 2512.01030](https://arxiv.org/abs/2512.01030) | Apache-2.0 (both) | `jingheya/lotus-normal-g-v1-1` apache-2.0; `jingheya/Lotus-2` apache-2.0, but it needs FLUX.1-dev, whose licence is "flux-1-dev-non-commercial-license" (HF API) | (b) |
| 6 | **Image-editing models used as normal estimators** | Ask a general image editor to "output the surface normal map". A May 2026 study: FireRed-Image-Edit 17.69° mean angular error on NYUv2 (lower is better), Qwen-Image-Edit 20.51°, fine-tuned Marigold 20.86° | [arXiv 2605.04566](https://arxiv.org/abs/2605.04566) (abstract page read; per-model numbers search snippet) | — | Qwen-Image-Edit (-2511) apache-2.0; FireRed-Image-Edit-1.0 apache-2.0 (HF API). Qwen-Image-Edit runs in **stable-diffusion.cpp** (`docs/qwen_image_edit.md`, GGUF, `--offload-to-cpu`) | (b) — the one route on the family's own engine; untested for faces |
| 7 | DSINE (CVPR 2024) | Per-pixel ray direction as input + normals refined as iterative rotations | [arXiv 2403.00712](https://arxiv.org/abs/2403.00712) | Imperial College licence: "solely for non-commercial, internal or academic research" (API) | in repo | (b) non-commercial |
| — | Others seen | GeoWizard (no licence on code or weights); Metric3Dv2 (BSD-2); GenPercept (BSD-2); NormalCrafter (MIT code, apache-2.0 weights, built on Stable Video Diffusion, whose licence is "stable-video-diffusion-community"); Pixel3DMM (face UVs and normals, CC-BY-NC-4.0); NVIDIA DiffusionRenderer (Cosmos video model; inverse rendering gives normals, albedo, roughness, metallic; code Apache-2.0; weights page needs a login, not read); Sapiens v1 (CC-BY-NC-4.0) | | | | |

- **What none of them proves:** no benchmark was found at **pore scale on skin**. All are scored on scenes (NYUv2,
  ScanNet) or on humans at body scale. On a 1K face crop, a pore is about 1 px. Read them as the source of
  **mid-scale** relief: folds, lids, lip lines, nasolabial creases. Pores come from §2.
- **Bucket (c2) note:** training any of these from scratch is out. Training-free stand-ins: (a) shape-from-shading
  (classic photometric inversion; weak, because it needs known lighting) or (a) taking relief from our own mesh and
  sculpt rather than from the picture.
- **(c1) path:** a LoRA on FLUX.2 klein-base-4B (apache-2.0, HF API) to turn "skin photo → height map".
  - SimpleTuner's FLUX.2 page: klein-4b "~12GB" bf16 / "~8GB" int8, 32 GB+ system RAM (API, `documentation/quickstart/FLUX2.md`).
    8 GB is the edge, not a comfortable fit.
  - kohya's sd-scripts: SDXL LoRA "can be done with 8GB GPU memory (10GB recommended)" (`docs/train_SDXL-en.md`);
    FLUX.1 LoRA on 8 GB with `--blocks_to_swap 28` and fp8 T5 (`docs/flux_train_network.md`). FLUX.1-dev weights are
    non-commercial.
  - Training data is the blocker: CC0 / CC-BY pairs of skin photo + measured height. One exists (the Lee Perry-Smith
    scan, §2.3); ambientCG has CC0 pairs, but for materials, not skin.

### 1.2 Picture → height, and tools named in the brief

- **BumpMesh** = CNC Kitchen's browser tool for 3D-printing textures ([bumpmesh.com](https://bumpmesh.com), page
  read; [CNCKitchen/stlTexturizer](https://github.com/CNCKitchen/stlTexturizer), **AGPL-3.0**, last push 2026-10-25,
  API).
  - **How it works:** it pushes STL vertices by an image's grey value, "height images that push the mesh surface
    outward or inward". It projects triplanar, cubic, cylindrical or spherical, then re-meshes to a target edge length.
  - It uses no AI, and it is the same brightness-as-height idea we already use. Useful only as a reference for
    displacing a mesh in the browser. (a).
- **DeepBump** ([HugoTini/DeepBump](https://github.com/HugoTini/DeepBump), **GPL-3.0**, last push 2025-03-17, API):
  - It is a Blender add-on on **ONNX Runtime**: colour → normals (a small network), normals → height, normals →
    curvature.
  - "The training code is currently not available" (README). The weights ship with the add-on under the repo's GPL.
    Trained on materials, not skin.
  - Bucket: (b) for colour → normals; (a) for normals → height.
- **PBRify_Remix** ([Kim2091/PBRify_Remix](https://github.com/Kim2091/PBRify_Remix), **CC0-1.0**, last push
  2026-02-19, API):
  - Tiny SPAN-architecture models: `1x-PBRify-NormalV3`, `1x-PBRify-Height`, `1x-PBRify-RoughnessV2`, all CC0, plus
    the `4x-PBRify-UpscalerV4` upscaler (DAT, CC0, 2025-05-19) (OpenModelDB data, API).
  - "trained exclusively on high quality CC0 content from ambientCG". NVIDIA ships it in ComfyUI-RTX-Remix.
  - Bucket: (b) as-is (materials).
  - **(c1)** retraining on skin is plausible: SPAN has 2.6 M parameters and uses 0.65 GB at inference on a 480×640
    input (traiNNer-redux benchmark, RTX 4090). The trainer is `the-database/traiNNer-redux`, Apache-2.0. Its
    training VRAM is not documented. The skin data is again the blocker.
- **Normal → height integration (a):** Frankot–Chellappa (1988) solves for the height whose slopes best match the
  normal map, using FFT Poisson integration. It is a standard way to do this step; DeepBump's README doesn't name its
  own method. Steps:
  1. Turn normals into slopes p = −nx/nz and q = −ny/nz.
  2. Take their FFT.
  3. Compute H = −j(ωx·P + ωy·Q)/(ωx² + ωy²).
  4. Take the inverse FFT; remove the low frequencies.
- Materialize (Bounding Box Software): GPL-3.0, 2024 — a classic filter tool, (a).

### 1.3 Baking and rendering *true* displacement in Blender 5.3 (measured)

- **Multires bake** (`BakeSettings.use_multires`):
  - Measured: `BakeSettings.type` ∈ {`NORMALS`, `DISPLACEMENT`, `VECTOR_DISPLACEMENT`}; `displacement_space` ∈
    {`OBJECT`, `TANGENT`}.
  - The 5.0 release notes: "Support vector displacement baking from multires" (blender/blender!145014).
  - The manual (`render/cycles/baking.rst`, raw): it bakes "the difference between" the viewport (low) and render
    (high) multires levels.
- **Rendering:**
  - Measured: material `displacement_method` ∈ {`BUMP`, `DISPLACEMENT`, `BOTH`}. The Subdivision Surface modifier
    carries `use_adaptive_subdivision`, `adaptive_space`, `adaptive_pixel_size` and `adaptive_object_edge_length`.
    Cycles has no `feature_set` any more.
  - The 5.0 notes: "Adaptive subdivision is no longer an experimental feature, and always available in the Subdivision
    Surface modifier" (blender/blender!146723).
  - The 5.0 notes: with displacement, "the Normal Map node now uses the undisplaced normal and tangent … the right
    behavior using a matching normal and displacement map". 5.1 makes this a per-node choice.
- **The pro pipeline in Blender:**
  1. Base mesh → Multires (4–5 levels).
  2. Put mid-scale relief (from §1.1 or a sculpt) and pores (§2) onto the high level, with displacement layers or a
     sculpt.
  3. Bake **tangent-space displacement** at 4K–8K. Optionally also bake a normal map of the finest band only.
  4. Render with "Displacement and Bump" + adaptive subdivision, dicing rate about 1 px.
- **EEVEE:** it moves vertices with "Displacement and Bump" but has no adaptive dicing. Its manual warns
  "Displacement of flat shaded surfaces will split the mesh into triangles". It needs real subdivision levels; pores
  stay a normal map there.
- **Cavity (a):** bake Cycles `AO` (a listed bake type, measured) with a short distance, or compute it from the baked
  height by high-pass and clamp. The Ambient Occlusion and Bevel nodes exist in 5.3 (measured).

---

## 2 · Skin micro-detail: pores, fine lines, expression wrinkles

### 2.1 How the pros do it (evidence per line)

- **MetaHuman** ([materials and textures](https://dev.epicgames.com/documentation/metahuman/metahuman-materials-and-textures?lang=en-US), page read):
  - Baked face maps: Basecolor; **SRMF** (specular, roughness, metallic, **fuzz**) in one texture; Normal (base
    detail); Normal LOD 256²; Scatter 512².
  - **Animated delta maps**: Basecolor 512² and Normal 1K by default, storing "only … the difference between the base
    map and the associated animated map". These are the expression wrinkles.
  - "Micro skin detail normals" at LOD0 only. SSS is off at Medium and Low quality.
  - Scanned database: a "Face Texture Index … wrinkle density, stubble, freckles, and moles"
    ([skin material controls](https://dev.epicgames.com/documentation/metahuman/skin-material-controls), search snippet).
- **Unreal Digital Humans** (UE 4.26 showcase, search snippet; page itself 403):
  - A dual-lobe specular. A specular map that "boosts specularity where skin is stretched tighter, and dampens it in
    pore centres and within wrinkles".
  - The `SubsurfaceProfileStruct` constructor defaults are `roughness0=0.75`, `roughness1=1.3`, `lobe_mix=0.85`
    (UE Python API docs, search snippet). How these combine with the material roughness was not verified.
- **CC5 HD** ([HD Characters](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/CC5-HD-Characters.htm), search snippet):
  - "Cavity Maps for better pore and wrinkle detail, supports up to 8K textures, and works with SkinGen".
  - Pores and wrinkles stored "as displacement maps as well as normal maps" ([CGChannel](https://www.cgchannel.com/2025/08/reallusion-releases-character-creator-5/), search snippet).
  - Face Tool: "three embedded normal maps and the three displacement maps" make the expression bumps ([manual](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/Geenrating-Detailed-Exp-Wrinkles-with-Face-Tool.htm), search snippet).
  - "Expression wrinkles … are materialized with diffuse, normal, and roughness textures" ([manual](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/06-Wrinkle/Expression-Wrinkle-System.htm), page read — it says nothing more on counts or drivers).
- **Texturing.xyz workflow** (80.lv, Polycount, Substance magazine, Novedge; search snippets):
  - A scanned **multi-channel displacement**: R, G and B hold the broad, mid and fine levels. It is wrapped onto the
    head (R3DS Wrap) and projected in Mari as a multi-channel EXR.
  - Each level goes on its own ZBrush layer with its own strength, on top of the sculpted displacement.
  - ZBrush artists stack "one for overall pores, one for T-zone micro pores, and one for subtle noise breakup".
- **USC ICT:**
  - Face scans to "0.1 mm detail, with 6k maps (including displacement)" (Digital Human League, search snippet).
  - Graham et al. 2013, *Measurement-Based Synthesis of Facial Microgeometry*: small skin patches scanned at about
    10 µm per face region, synthesised over the whole face (paper not opened this session).
  - Nagano et al. 2015, [*Skin Microstructure Deformation with Displacement Map Convolution*](https://vgl.ict.usc.edu/Research/SkinStretch):
    micro-displacement blurred where skin stretches and sharpened where it compresses (search result; page not opened).

### 2.2 Methods ranked by quality, with the technique

1. **Graph-based synthesis for skin micro-wrinkles** — Weiss, Moulin, Chandran, Zoss, Gotardo, Bradley (Disney
   Research / ILM), SGP 2023, CGF 42(5) ([diglib](https://diglib.eg.org/handle/10.1111/cgf14904); search snippet, the
   diglib page 403).
   - **How:** pores are graph nodes and candidate wrinkles are edges. An optimisation "inspired by pedestrian trail
     formation" strengthens some edges into wrinkles. The graph is then drawn into a displacement map with shape
     functions in shaders, in real time.
   - **Steps:**
     1. Region maps: pore density, depth and preferred direction.
     2. Poisson-disk pore positions in UV space.
     3. Neighbour graph (Delaunay).
     4. Iterative trail reinforcement along the direction field.
     5. Rasterise a radial pore profile and a line-segment wrinkle profile into a height texture at texel size.
   - Follow-ups:
     - *Fast Dynamic Facial Wrinkles* (EG 2024) animates them under expressions.
     - *Stylize My Wrinkles* (EG 2024) transfers the look of scanned skin patches by style transfer.
   - Code: none found.
   - **Bucket (a)** (procedural). *Stylize My Wrinkles* needs a pretrained style network: (b) with any open VGG.
2. **Example-based from a real scan (a).**
   - Cut high-pass tiles of real pore displacement per region (nose, cheek, forehead, chin, lips) from a permissive
     scan. Synthesise them over the UVs, either with texture synthesis (Graham 2013) or with tiling and
     stochastic-tiling blending.
   - The only permissive real scan found: **"Infinite, 3D Head Scan by Lee Perry-Smith … Creative Commons Attribution
     3.0 Unported"**, "Based on a work at www.triplegangers.com".
     - Shipped in three.js `examples/models/gltf/LeePerrySmith/` with `Infinite-Level_02_Disp_NoSmoothUV-4096.jpg`
       (752,389 bytes), a tangent normal map, a colour map and a spec map. Licence file read, API; last change
       2018-08-30.
     - Limits: one man; the displacement is JPEG-compressed 4K, so the finest band is damaged; CC-BY needs credit.
3. **Tension-driven procedural micro-wrinkles** — Simon Thommes, Blender Studio, *Charge*, 2023-01-12
   ([Procedural Wrinkles](https://studio.blender.org/blog/procedural-wrinkles/), page read).
   - **How:** Geometry Nodes compares the posed mesh with its rest mesh.
     - A *compression map* 1 − 2^(−A_deformed/A_base): 0 is fully compressed, 0.5 unchanged, 1 infinitely stretched.
     - A *directional stretch map*: edge length changes, read as directions in UV space. Angles are doubled so
       opposite edges don't cancel; the mesh is triangulated two ways and averaged.
     - In the shader, Perlin noise is squashed along the tension direction per UV cell, on 4 offset grids blended
       together, and used as **bump for the finest band only**, "on top of manually sculpted displacement".
   - Limits: quad meshes only; costly on dense meshes. The example file's licence is not stated on the page.
   - **Bucket (a)**, native Blender.
4. **AI-made tiles** with FLUX.2 klein through stable-diffusion.cpp (apache-2.0).
   - RESEARCH §10 measured that "a flat patch of human skin on the inner forearm … gives real pores". It is still a
     picture of shading, so its relief needs §1.1 or 1.2 (StableNormal / DeepBump, then integration) rather than
     brightness.
   - Community "ultra-real" skin LoRAs for klein 9B exist (Civitai / Reddit, search snippet; licence unknown;
     commenters disagree that they help).
   - **(b)** as-is; **(c1)** a LoRA on klein-base-4B that outputs tileable height maps (~8 GB int8, SimpleTuner)
     would need skin height data we don't have.
5. **Procedural shader pores (a)** — the quick baseline.
   - Measured in 5.3: Voronoi features `F1`, `F2`, `SMOOTH_F1`, `DISTANCE_TO_EDGE`, `N_SPHERE_RADIUS`, and a **Gabor
     Texture** node (`ShaderNodeTexGabor`). Gabor noise suits the anisotropic crosshatch of skin lines.
   - Free example: Eugenio Pignataro's procedural pore shader ([80.lv](https://80.lv/articles/free-procedural-skin-shader-for-blender), search snippet).
   - It looks regular next to methods 1–3.

### 2.3 Expression wrinkles (the CC5 / MetaHuman feature)

- **Technique (a):** two or three wrinkle normal (or displacement) maps per face: "compressed" and "stretched". Region
  masks (brow, forehead, crow's feet, nose, nasolabial, chin), each masks weight multiplied by the matching blendshape
  weights, blend them over the base map.
  - Classic references: Oat 2007 *Animated Wrinkle Maps* (AMD, SIGGRAPH course) and Jimenez et al. 2011 *Practical
    and Realistic Facial Wrinkles Animation* (GPU Pro 2). Neither was opened this session.
  - Shipping versions: MetaHuman's animated delta maps; CC5's 3 normal + 3 displacement maps.
  - **Driver-free variant:** Unity's *Heretic* package "Added skin tension to apply wrinkle maps"
    ([Unity-Technologies/com.unity.demoteam.digital-human](https://github.com/Unity-Technologies/com.unity.demoteam.digital-human),
    README, API; Unity Companion License, "for Unity-dependent projects"). Blender Studio's tension maps (§2.2.3) do
    the same in Blender.
- **In Blender:** drivers from shape-key values → Mix nodes, or a tension attribute from Geometry Nodes → Mix factor.
  **CC Blender Tools** builds exactly this for CC characters: drivers from expression shape keys, flow maps, additive
  blending of competing maps, per-region strength (README, API). See §3.3 for its clean-room flag.
- The wrinkle maps themselves still have to be made. Ways to make them:
  - sculpt them on the multires at extreme expressions, then bake (a);
  - generate them with §2.2.1 under deformation (Disney's EG 2024 follow-up).

### 2.4 Open micro-detail sources (licence read)

| Source | What | Licence | Evidence |
|---|---|---|---|
| Lee Perry-Smith head scan (three.js examples) | 4K displacement JPG, normal, colour, spec of a real scan | CC-BY 3.0 | licence file, API |
| ICT-FaceKit | geometry, eye shells (no skin textures in the open model); the "full model" with "Albedo to displacement inference" is promised under "a different USC specific license" | MIT | README, API |
| MPFB2 / MakeHuman assets | base mesh, skins, node trees (`enhanced_skin.json`, `procedural_eyes.json`) | assets CC0 1.0, code GPL-3 | LICENSE.md, API |
| Poly Haven | 869 textures; none tagged skin, pore, human or flesh | CC0 ("Our assets are all licensed as CC0") | API + page read |
| ambientCG | "skin" query: only `Leather008` | CC0 | API |
| Texturing.xyz, 3D Scan Store, Triplegangers | scanned skin / heads | commercial terms, not read | — |

No verified free CC0 human-pore displacement set was found (search 7).

---

## 3 · Pro skin shading in Blender 5.x

### 3.1 What Blender 5.3 gives (measured + manual raw `render/shader_nodes/shader/principled.rst`)

- **Principled BSDF inputs (5.3 beta, measured):**
  - Base: Base Color, Metallic, Roughness, IOR 1.5, Alpha, Thin Wall, Normal, Weight, Diffuse Roughness.
  - Subsurface: Weight, Radius (1, 0.2, 0.1), Scale 0.005, **Subsurface IOR 1.4**, Subsurface Anisotropy.
  - Specular: IOR Level, Tint, Anisotropic, Anisotropic Rotation, Tangent.
  - Transmission: Weight, Dispersion Scale and Abbe.
  - Coat: Weight, Roughness 0.03, IOR 1.5, Tint, Normal.
  - Sheen: Weight, Roughness 0.5, Tint.
  - Emission Color and Strength; Thin Film Thickness and IOR.
- **Subsurface methods:** `BURLEY`, `RANDOM_WALK`, `RANDOM_WALK_SKIN`, `RANDOM_WALK_LEGACY`. Distributions: `GGX`,
  `MULTI_GGX` (measured).
  - **Random Walk (Skin)**, Cycles only: "The radius is automatically adjusted based on the color texture, and the
    subsurface entry direction uses a mix of diffuse and specular transmission with custom IOR. This tends to retain
    greater surface detail and color and matches measured skin more closely."
  - Subsurface IOR "may be set to a different value than the global IOR to simulate different layers of skin".
  - Anisotropy: "skin has been measured to have an anisotropy of 0.8".
  - Weight "Typically should be zero or one".
  - IOR Level: "0.5 means no adjustment, 0 removes all reflections, 1 doubles them".
- **Release notes** (raw `blender-developer-docs`):
  - 5.0: "More accurate random walk subsurface scattering with multiple bounces, reducing darkening artifacts at the
    cost of some render time"; thin film.
  - 5.2: Subsurface supports negative anisotropy; new Principled "Thin Wall" input.
- **EEVEE** (manual `render/eevee/limitations/nodes_support.rst`, raw):
  - "Subsurface Scattering: Random Walk sampling, IOR and Anisotropic are not supported."
  - Principled: "Anisotropy is not supported. The Sheen layer is a crude approximation."
  - EEVEE's SSS uses the material output's **Thickness** (Sphere or Slab mode, optional "From Shadow" refinement)
    (`material_settings.rst`).
  - 5.3's `scene.eevee` has no SSS settings left (measured property list).
  - 5.2: "EEVEE SubSurface Scattering now evaluates indirect light separately if light-path clamping or intensity are
    non-default".
  - Verdict: **Cycles is the final-render path for skin**; EEVEE is the fast preview and needs its own tuning. An older
    report (search snippet, Diffeomorphic tracker) says EEVEE ignores a *linked* Subsurface Radius socket; not checked
    on 5.x.

### 3.2 The pro recipe, piece by piece (a)

| Piece | What pros do | In Blender 5.3 | Source |
|---|---|---|---|
| Scattering | measured-skin profile; red goes deepest | Random Walk (Skin), radius per channel in mm with Scale 0.001 (ours already, from melanin and haemoglobin optics); Subsurface IOR ~1.4; anisotropy 0.8 | manual; our `skin_optics.py` |
| Shine varies by region | T-zone (forehead, nose, chin) shinier and smoother; cheeks rougher; lips wetter | a roughness map (or masks) instead of our single 0.59 | UE Digital Humans (snippet); Weyrich et al. 2006 *Analysis of Human Faces using a Measurement-Based Skin Reflectance Model* (measured per-region skin specular; paper not opened) |
| No shine in pores | specular killed in pore centres and wrinkle valleys, boosted where skin is stretched | the cavity map multiplies Specular IOR Level (and raises roughness) | UE Digital Humans (snippet); CC5 cavity maps; CC Blender Tools "Skin shaders updated to use cavity maps" |
| Two highlight lobes | a sharp lobe (oil film) + a broad lobe (skin) | (i) Coat as the sharp lobe: low weight, low roughness, white tint, Coat Normal = micro normal — **costs:** the coat dims the base; (ii) Mix Shader of two Principled at the lobe mix — **costs:** doubles shading; (iii) Add Shader of a Glossy — not energy-conserving | UE `lobe_mix` 0.85 (snippet); CC Blender Tools "Dual Specular skin shader (Eevee & Cycles) with specular micro details" (README); GPU Gems 3 ch. 14 (d'Eon & Luebke; search result) |
| Fine facial hair (peach fuzz) | MetaHuman bakes "fuzz" into SRMF | low Sheen Weight (crude in EEVEE) | MetaHuman (page read) |
| Micro-normal | a tiling pore normal on top of the baked normal, LOD0 | a second normal at UV × tile, combined with the baked normal (Normal Map → Bump chain) | MetaHuman (page read) |
| Colour | delit albedo; MetaHuman adds AO to base colour only at LOD2 "to help fake shadowing" | §1.0 | MetaHuman (page read) |

### 3.3 Free and paid Blender references

- **CC Blender Tools** ([soupday/cc_blender_tools](https://github.com/soupday/cc_blender_tools), **GPL-3.0**, last push
  2026-10-14, 524 ★, API). The most complete Blender reimplementation of a CC-class look:
  - Random Walk (Skin) "skin, eye and hair shaders";
  - cavity maps and dual specular;
  - wrinkle maps with drivers and flow maps;
  - "Tearline Plus" and "Eye Occlusion Plus";
  - refractive and parallax eyes;
  - EEVEE-Next fixes.
  - **Clean-room flag (decision for the user):** it imports Reallusion characters and ships Reallusion files
    (`textures/RL_WrinkleMask_Set*.png`, `RL_CC3_Plus_EyeTearlineNormal.TGA`, API tree). AGENTS.md allows only
    behaviour and public docs for reference apps. Whether its own GPL code may be read counts as such a reference is
    for the user to say.
- **MPFB2** ([makehumancommunity/mpfb2](https://github.com/makehumancommunity/mpfb2), code GPL-3, assets CC0, last push
  2026-10-24, API):
  - `enhanced_skin.json` (PBR + SSS; radius scaled per unit setting; an SSS texture);
  - `procedural_eyes.json`: one Principled + Voronoi, 18 node types, no refraction shell (API count).
- Paid or PWYW (behaviour only; search snippets):
  - UltimateSkin (Gumroad, pay-what-you-want, procedural, "updated to Blender 4.0");
  - VSHADE (US$44.99);
  - Procedural Skin Material – Detailed (US$3.90, lists 5.0–5.2);
  - Sporemind Procedural Skin Shader ("real displacement in Cycles … bump-based fallback in Eevee"; check pores in
    "soft raking light");
  - Pixelica's "Ultimate Guide To Hyper-Realistic Skin In Blender" course.
- A plain search for how-to guides (search 2) found mostly paid courses and pre-4.x posts; no 5.x-specific guide.

---

## 4 · Light for portrait realism

- **Colour management in 5.3 (measured):**
  - View transforms: `AgX`, `Filmic`, `Standard`, `Khronos PBR Neutral`, `ACES 1.3`, `ACES 2.0`, `False Color`.
  - AgX looks found: `AgX - Punchy`, `AgX - Base Contrast`, `AgX - Greyscale` (other names not tried).
  - Working spaces: `Linear Rec.709` (default), `Linear Rec.2020`, `ACEScg`.
  - Displays: sRGB, Display P3, Rec.1886, Rec.2020, Rec.2100-PQ, Rec.2100-HLG.
  - 5.0 notes: ACES 1.3 and 2.0 views, an "AgX HDR view", and per-file working spaces are new in 5.0.
- **HDRIs (API):** Poly Haven has 96 studio HDRIs, CC0. Most downloaded:
  - `brown_photostudio_02` (781,915);
  - `studio_small_09` (711,183 — the one in our `.dev/cache/hdri`, "medium contrast");
  - `studio_small_08` ("low contrast");
  - `studio_small_03`, `photo_studio_01`.
- **Portrait setups** (search snippets):
  - Classic patterns: Rembrandt, loop, butterfly, split, short, broad ("Light It Up" add-on, BlenderNation 2026-09-11).
  - Clamshell: a softbox above and below the face, plus kickers (DPReview's Blender head test).
  - HDR images on area lights for realistic reflections (Lightmap HDR Light Studio). Its rule: frame the camera first,
    because moving it moves the reflections.
  - Soft raking light shows pores (Sporemind manual).
- **The technique (a):**
  1. One large soft key (an area light about the size of a softbox) at 30–45°. It makes the broad sheen across the
     skin where pores and cavity read.
  2. A kicker or rim behind, which shows SSS at the ears and nostrils.
  3. Fill from a low-contrast studio HDRI.
  4. The key's shape must show as a catchlight in the cornea.
- **Eyes in Cycles — shadow caustics (MNEE)** (manual raw `render/cycles/object_settings/object_data.rst`,
  `light_settings.rst`; measured `is_caustics_caster` / `is_caustics_receiver` on objects and `is_caustics_light` on
  lights):
  - It lets light through a glass cornea onto the iris instead of a black shadow.
  - Limits, quoted: "Only refractive caustics in the shadows of objects work"; "Bump and normal maps are ignored";
    "only work if the caustic caster has smooth normals"; at most 6 caster surfaces.
  - The World can also be a Shadow Caustics light.

---

## 5 · Upscaling skin textures to 4K–8K

No benchmark on skin or UV textures was found (search 15 returned marketing pages). The ranking below is by the
methods' general restoration quality.

| Rank | Model | How it works | Paper | Code / weights licence | Runs on | Bucket |
|---|---|---|---|---|---|---|
| 1 | **SeedVR2** (ByteDance, ICLR 2026) | A video and image diffusion restorer turned into a **one-step** model by adversarial post-training; 3B and 7B | [arXiv 2506.05301](https://arxiv.org/abs/2506.05301) | code Apache-2.0 (push 2026-01-27); `ByteDance-Seed/SeedVR2-3B`/`-7B` apache-2.0 (HF API) | ComfyUI node (Apache-2.0): "Minimal VRAM (8GB or less): Use GGUF Q4_K_M models with BlockSwap and VAE tiling"; CUDA, ROCm, Apple MPS fixes in its changelog; a community ONNX port `Merserk/SeedVR2-3B-ONNX` (untested) | (b) |
| 2 | **SUPIR** | An SDXL-based restorer with a large adaptor + captions; strong on photos | [arXiv 2401.13627](https://arxiv.org/abs/2401.13627) | **non-commercial**: "the proprietary neural network weights … may only be used for non-commercial purposes" (LICENSE, API) | SDXL-class, CUDA | (b) NC |
| 3 | DAT / HAT / SwinIR-class transformers, community-trained (OpenModelDB data, API) | Transformer super-resolution trained on degraded / clean pairs | DAT [arXiv 2308.03364](https://arxiv.org/abs/2308.03364) | Arch code Apache-2.0. Models: `4x-RealWebPhoto-v4-dat2` CC-BY-4.0; `4x-FaceUpDAT` (faces) CC-BY-4.0; `4x-TextureDAT2-otf` CC-BY-4.0; `4x-PBRify-UpscalerV4` CC0 (2025-05-19); `4x-UltraSharpV2` CC-BY-NC-SA-4.0 (2025-05-23); skin-specific `1x-ITF-SkinDiffDetail-Lite-v1` CC-BY-NC-SA-4.0 (2022, "adds plausible high frequency detail") and `1x-SkinContrast-*` CC0 (2024) | PyTorch via spandrel (MIT) / chaiNNer (GPL-3) | (b) |
| 4 | **Real-ESRGAN** and **MoSR** inside **stable-diffusion.cpp** | ESRGAN generator trained on synthetic degradations | [arXiv 2107.10833](https://arxiv.org/abs/2107.10833) | Real-ESRGAN BSD-3-Clause (repo; OpenModelDB lists `4x-realesrgan-x4plus` BSD-3); ncnn-vulkan port MIT; `4x-Nomos2-hq-mosr` CC-BY-4.0 | sd.cpp `--upscale-model`: "MoSR models with the PixelShuffle upsampler … are also supported. The architecture is detected from the weights" (`docs/esrgan.md`, API) — the family's own engine, any GPU | (b) |

- **Job split for skin (proposal):**
  - Upscale **albedo only**.
  - Never photo-upscale normal, height or roughness maps: the models invent shading.
  - Fill the 4K–8K detail of relief from §2 instead (tiled micro-detail + synthesised pores).
- A diffusion "tile upscale" with the family image model (klein / Z-Image img2img in tiles at low strength,
  stable-diffusion.cpp VAE tiling) is a possible (b) path. It is untested on UV maps; seams across UV islands are the
  risk.
- GFPGAN / CodeFormer face restorers (CodeFormer "S-Lab License 1.0 … non-commercial") restore photos of faces, not
  unwrapped UV maps.
- **(c1):** small SR models (SPAN, Compact) trained with traiNNer-redux (Apache-2.0) on skin pairs. Inference is tiny
  (0.2–0.65 GB at 480×640, traiNNer benchmark); training VRAM is undocumented; skin data is the blocker.

---

## 6 · Eyes

### 6.1 How pro eyes are built (layers, top down)

1. **Eye occlusion shell**: "The topmost mesh layer … simulate the shadow cast from the eyelids to prevent
   over-exposure on the eyeballs" (CC5, RESEARCH §5, page read). A transparent dark gradient by UV, with blur, two
   shadows and a vertex offset (CC5's setting pages).
2. **Tearline / lacrimal fluid strip** along the lid margin: "moisture and the tear reflectivity on the eyeballs and
   the tear ducts" (CC5). Glossy + transparent, a tiling normal, an edge fade.
3. **Eye blend mesh** at the corners (ICT-FaceKit), for the caruncle transition.
4. **Cornea**: refractive and glossy over a **concave or recessed iris**. Sclera with light SSS.

- MetaHuman meshes: `eyeshell`, `eyeEdge` (RESEARCH §5).
- Unity *Heretic*: "Custom pass for cross-material normal buffer blur (tearline)", "Custom marker-driven occlusion for
  eyes and teeth" (README, API).
- **Free topology:** **ICT-FaceKit (MIT)** ships Lacrimal fluid L/R (204 vertices, 163 faces each), Eye blend L/R
  (24 / 15), Eye occlusion L/R (152 / 128), Sclera and Iris split meshes.
  - "Additional eye geometry including lacrimal fluid, blend meshes, and occlusion meshes adopts the style of Unreal
    Engine's Digital Human Project … plug and play with Unreal Engine's shaders" (README, API).
  - ICT-FaceKit is already in RESEARCH §5 as a head source.

### 6.2 Techniques in Blender (a)

- **Cycles, physical:**
  - The cornea is a smooth glass shell: Principled, Transmission 1, roughness about 0. The cornea's IOR is commonly
    quoted near 1.376 (not verified this session).
  - The iris is real geometry behind it, so the view refracts and the iris shifts with the viewing angle.
  - The glass blackens the iris in shadow. Two fixes:
    - (i) **MNEE shadow caustics**: cornea = caster, iris and sclera = receivers, key light = Shadow Caustics (§4;
      the cornea needs smooth normals);
    - (ii) the "fake caustics" trick: Light Path *Is Shadow Ray* → Transparent on the cornea (BlenderNation 2023 free
      node group; BlendSwap "Free Eyeballs + Fake Caustics", stated CC0 — search snippets).
- **EEVEE:**
  - The cornea material uses **Raytraced Transmission** (`use_raytrace_refraction`, measured) + Thickness.
  - Limits (manual raw): "Only one refraction event is correctly modeled"; "Only dithered materials *not* using
    Raytrace Refractions can be refracted". So the iris and sclera stay dithered and opaque, and only the cornea
    raytraces.
  - 5.3 notes: "Refraction no longer shows discontinuities at high roughness".
- **Parallax eyes** (the cheaper path, both engines): one surface; the iris UV is shifted by the view vector × an iris
  depth. CC Blender Tools offers both refractive and parallax eyes (README).
- Free assets, all behaviour references:
  - MPFB2 procedural eyes (CC0, simple);
  - BlendSwap CC0 eyeball (older Blender, needs a login);
  - Fab "Procedural Eye Generator" ("Free for personal + commercial use, no reselling/redistributing the plugin file" —
    so it cannot be bundled; search snippet).
- Eye-capture research for iris shape and cornea bulge: Bérard et al. 2014 *High-Quality Capture of Eyes* (Disney
  Research); Jimenez et al. GDC 2013 *Next-Generation Character Rendering* (Activision) — eye refraction and wetness.
  Neither was opened this session.

---

## 7 · Apps that do this and how they work

The leading ones the plain searches turned up — not a catalogue.

| App / project | Where its realism comes from | Pipeline in short | Evidence |
|---|---|---|---|
| **MetaHuman** (Epic) | A scanned face database + baked maps + engine shading | Pick from the scanned "Face Texture Index" → bake Basecolor / SRMF (incl. fuzz) / Normal / Scatter → animated delta maps (512 / 1K) for expressions → tiling micro-normal at LOD0 → dual-lobe specular + subsurface profile; eye meshes `eyeshell`, `eyeEdge` | page read + snippets |
| **Character Creator 5 HD + SkinGen** | HD base (+2 subdivision levels), 8K maps, displacement + cavity, layered SkinGen | Base skin + SkinGen layers → cavity and displacement for pores → expression wrinkles (diffuse, normal, roughness; Face Tool 3 normal + 3 displacement) → Digital Human Shader eyes (occlusion, tearline) | page read + snippets; RESEARCH §2 |
| **Daz Genesis 9** | Iray path tracing; skin artists' maps | Two skin systems, PBRSkin and Iray Uber; dual-lobe specular + top coat for shine and wetness | snippets only (thin) |
| **Texturing.xyz + R3DS Wrap + Mari + ZBrush** (film / VFX) | Scanned multi-channel skin displacement | Wrap the scan onto the head → project in Mari (multi-channel EXR, R/G/B = broad/mid/fine) → ZBrush layers with separate strengths over the sculpt → render displacement | snippets |
| **Substance 3D Designer / Painter** | Procedural pore generators; projection | Designer pore generator → ZBrush; Painter warp projection for pores; procedural skin materials; Texturing.xyz materials in Painter | snippets |
| **Unreal Digital Humans** (Epic) | Dual-lobe spec; stretch- and pore-aware specular map; eye shells | Specular map boosted where skin is stretched, damped in pores; `SubsurfaceProfile` lobes 0.75 / 1.3 / 0.85 (defaults) | snippets |
| **Unity *The Heretic* / *Enemies*** | Snappers face rig, tension-driven wrinkles, custom passes | Skin tension → wrinkle maps; tearline normal-blur pass; marker-driven eye and teeth occlusion | README (API) |
| **USC ICT / Digital Human League** | Light-stage scans | 0.1 mm scans, 6K maps with displacement; microgeometry synthesis from about 10 µm patches; displacement convolution under stretch | snippets |
| **Disney Research** | Procedural + example-based micro-wrinkles | Graph of pores → trail-formation wrinkles → displacement (SGP 2023); animated (EG 2024); styled from scans (EG 2024) | snippet |
| **Goodbye Kansas** (SIGGRAPH 2022 talk) | Procedural pores and wrinkles from animation | "generating pores and wrinkles procedurally from animation stretch and compression" | snippet |
| **Blender Studio *Charge*** | Sculpted displacement + rig-driven maps + procedural tension micro-wrinkles | §2.2.3 | page read |
| **CC Blender Tools** (Blender) | Rebuilds CC's look in Blender | Random Walk (Skin), cavity, dual spec, wrinkle maps with drivers and flow maps, tearline / occlusion shells, refractive and parallax eyes | README (API) |
| **ArmorPaint** (zlib source, paid binaries) | AI picture → PBR | Current `image_to_pbr_node.c` (last change 2026-09-11): Depth Anything 3 mono-large (`armory3d/DA3MONO-LARGE`, apache-2.0) via its own `iris` binary → height; shaders derive normal and AO from depth; roughness from a detail heuristic. Earlier, Marigold GGUF sets | source + HF API |
| **NVIDIA RTX Remix + PBRify** | Tiny CC0 models | Diffuse → upscale → normal / roughness / height (ambientCG-trained) | README (API) |
| **NVIDIA Omniverse digital humans** | MDL skin on `OmniSurfaceBase` | RESEARCH §8 | record |

---

## 8 · Leads for our pipeline — proposals for the user, not decisions

Each lead was attacked once; the attack and what it changed are on its line.

1. **Stop deriving relief from colour brightness.**
   - Instead: delit colour (§1.0) → mid-scale normals from a human model (§1.1) → pores from synthesis (§2.2) →
     multires → baked tangent displacement → Cycles adaptive subdivision (§1.3).
   - *Attack:* every top delighting and normal model is PyTorch (CUDA-first) and none runs in our engines. MoGe-2 is
     ONNX but scene-scale; Sapiens2 has untested community ONNX ports.
   - *Changed:* the first step that runs on every GPU is the (a) path: §2.2 pores plus mid-scale relief sculpted or
     taken from the mesh. The AI steps are optional.
2. **Shading:**
   - Swap the single roughness for region masks, a cavity map that takes shine out of pores, a second lobe via Coat,
     and a little sheen.
   - *Attack:* Coat dims the base layer, and the second lobe could double-count shine with Specular IOR Level.
   - *Changed:* tune it against reference photos in the quality gate; nothing to fix in advance.
3. **Eyes:**
   - Add occlusion, tearline and blend shells in ICT-FaceKit's layout (MIT), a refractive cornea over a recessed iris,
     and MNEE for the key light.
   - *Attack:* MNEE ignores normal maps and needs smooth normals; it does nothing under HDRI-only light unless the
     World is marked.
   - *Changed:* keep the shadow-ray trick as the fallback.
4. **Upscaling:**
   - Real-ESRGAN / MoSR inside stable-diffusion.cpp now (the family engine; BSD-3 / CC-BY); SeedVR2 as the quality
     option (apache-2.0, CUDA / ROCm / MPS).
   - *Attack:* SeedVR2 on 8 GB needs Q4 GGUF + BlockSwap and was not measured here.
   - *Changed:* nothing until measured.

---

## 9 · Search log (23 of 25 standard searches used)

| # | Query | What it returned |
|---|---|---|
| 1 | new AI tools for normal maps from photos 2026 | Vendor tools (3D AI Studio, NormalMap AI, Unity ArtEngine "Normal Gen", Magic Hour); Meshy's is a Sobel filter, not AI; nothing open |
| 2 | how to make realistic skin in Blender 2026 | Paid courses (Pixelica, FlippedNormals), 2018 and 2021 posts; no 5.x guide |
| 3 | BumpMesh image to displacement map | Nothing on BumpMesh; generic displacement docs (bumpmesh.com then fetched directly) |
| 4 | best surface normal estimation model 2026 state of the art single image | arXiv 2605.04566 (image editors as zero-shot normal estimators), a DSINE summary |
| 5 | MetaHuman skin material wrinkle maps animated micro normal cavity how it works | Epic docs: Face Texture Index, animated delta maps, LOD switches |
| 6 | Character Creator 5 HD skin displacement micro normal wrinkle system manual | CC5 manual pages (HD, Face Tool, Expression Wrinkles), CGChannel CC5 article, a 5.07 bug report |
| 7 | free skin pores micro detail displacement texture CC0 commercial use | General CC0 libraries, Gumroad packs with unclear licences, a paid ArtStation pack; no CC0 human pores |
| 8 | procedural skin pores shader Blender voronoi tutorial realistic | Paid shaders (Sporemind etc.), Pignataro's free pore shader, a stylised Voronoi breakdown |
| 9 | realistic eye Blender cornea refraction iris tearline eye occlusion shader free download | BlendSwap CC0 eyeball + fake caustics, BlenderNation caustics node group, Fab Procedural Eye Generator |
| 10 | Blender realistic portrait lighting setup character render HDRI area lights AgX skin | "Light It Up" portrait rigs, Lightmap HDR area lights, DPReview clamshell test, beginner AgX posts |
| 11 | Texturing XYZ multi-channel face displacement workflow Wrap Mari ZBrush skin pores breakdown | RGB = broad/mid/fine, Mari multi-channel EXR, ZBrush layer stacking |
| 12 | Substance 3D Painter Designer realistic skin pores generator tutorial 2025 | Designer pore-generator course, Painter warp projection, Substance procedural skin, Texturing.xyz in Painter |
| 13 | digital human skin rendering technical breakdown 2025 game studio SIGGRAPH pores wrinkles specular | UE 4.26 Digital Humans (dual lobe, spec map), GPU Gems 3 ch. 14, USC ICT 0.1 mm, Goodbye Kansas 2022, patents |
| 14 | Daz Genesis 9 PBR skin shader dual lobe specular Iray HD micro detail how it works | PBRSkin vs Iray Uber, dual lobe / top coat; product pages, no technical detail |
| 15 | best AI upscaler for game textures and skin textures 2026 open source | Marketing pages; Upscayl named; no skin benchmark |
| 16 | facial displacement map generation from photo high-frequency pores wrinkles diffusion 2025 2026 paper code | Disney SkinMicroWrinkles, *Stylize My Wrinkles*, Utrecht example-based wrinkles, patents; no diffusion code |
| 17 | free realistic skin shader node group Blender 4.x 5.x download dual specular cavity breakdown | UltimateSkin (PWYW), Pignataro; paid VSHADE, Procedural Skin Material |
| 18 | EEVEE Blender 5 subsurface scattering skin quality vs Cycles realistic character | Older sources: Cycles more realistic; EEVEE radius-socket report |
| 19 | Unreal subsurface profile dual specular "Roughness 0" "Roughness 1" "Lobe Mix" default values skin | UE Python API defaults 0.75 / 1.3 / 0.85; HDRP lobe-mix meaning |
| 20 | AI realistic skin texture detail pores LoRA 2026 Flux Klein Z-Image skin enhancer | Community klein-9B "ultra-real" LoRA, Reddit pushback, a 2025 FLUX skin LoRA guide |
| 21 | Blender tension map wrinkle maps geometry nodes shape keys drivers facial wrinkles | Blender Studio *Procedural Wrinkles*, the old wrinkle-modifier wiki, forum threads |
| 22 | "Graph-Based Synthesis for Skin Micro Wrinkles" Disney Research | Authors, SGP 2023, method summary, EG 2024 follow-ups |
| 23 | remove lighting from face photo get albedo texture open source model 2026 delighting intrinsic decomposition | OpenDelight (arXiv 2605.05636), MAGINet (2512.16511), HiFiAlbedo |

Licence, date and VRAM facts came from `gh api` and the Hugging Face API, which cost no searches.

---

## Couldn't verify

- **No method above was run** on our faces or on any skin picture. Their quality on skin, at pore scale, is unmeasured.
- **VRAM not stated** for Sapiens2, StableNormal, Marigold normals and IID, E2E-FT, MoGe-2, OpenDelight (inference),
  StableDelight, DeepBump, Qwen-Image-Edit or FireRed-Image-Edit on 8 GB. Not measured on the 2070 Super.
- **SeedVR2 on 8 GB** is the ComfyUI node's README claim (GGUF Q4 + BlockSwap); not run.
- **SimpleTuner's "~8GB int8" for klein-4b LoRA** is the doc's figure; LoRA training was not tried.
  Training VRAM for traiNNer-redux's tiny models is not documented.
- **Licences not fully read:**
  - the openrail++ text (Marigold) was not re-read this session;
  - OpenDelight's pretrained weights (Google Drive, no separate licence);
  - Meta's Ava-256 terms (OpenDelight's source data);
  - NVIDIA DiffusionRenderer weights (HF page needs a login);
  - the Blender Studio *Charge* example file;
  - the Fab Procedural Eye Generator and BlendSwap eyeball (snippets only);
  - Texturing.xyz, 3D Scan Store, Triplegangers terms.
- **ArmorPaint's sd.cpp fork** (`github.com/armory3d/stable-diffusion.cpp`) returns 404. How its Marigold GGUF files
  were run is unknown, and the source of its `iris` binary was not found.
- **Sapiens2 ONNX ports** (`WeReCooking/sapiens2-onnx`, `barakplasma/sapiens2-onnx`): 0 downloads, contents not
  checked.
- **Per-model normal errors** for Qwen-Image-Edit in arXiv 2605.04566 come from a search snippet. The abstract page
  read gives only FireRed's 17.69° and Marigold's 20.86°.
- **Unreal `SubsurfaceProfile` roughness0 / roughness1:** whether they multiply the material roughness was not
  verified. The UE 4.26 Digital Humans page itself returned 403; its content came from snippets.
- **Papers cited but not opened:** Graham et al. 2013; Weiss et al. 2023 (diglib 403); *Fast Dynamic Facial Wrinkles*
  and *Stylize My Wrinkles* (EG 2024); Weyrich et al. 2006; Oat 2007; Jimenez et al. 2011 and GDC 2013; Bérard et
  al. 2014; d'Eon & Luebke (GPU Gems 3 ch. 14).
- **Cornea IOR 1.376** is a commonly quoted value, not checked against a source here.
- **The EEVEE "linked Subsurface Radius ignored"** report is from the 4.x era; not checked on 5.3.
- **AgX look names** beyond Punchy, Base Contrast and Greyscale were not probed. The exact identifier of the "AgX HDR"
  view was not probed.
- **MetaHuman wrinkle-map count and drivers**, and CC5 wrinkle counts and drivers: not in the pages read.
- **Not checked at all:** Human Generator and other paid Blender human add-ons; Houdini skin tools; KeenTools.
- **For the session:** this agent was told to edit no file but this one. The RESEARCH.md entry for these facts (§7
  building blocks or §10) is still to be written.
