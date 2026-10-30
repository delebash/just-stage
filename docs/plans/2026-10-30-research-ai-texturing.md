# AI texturing of a given head/body mesh — research, 2026-10-30

The job: put photoreal, seamless skin onto an existing mesh (hm08: its shape, triangles and UV layout stay fixed), using
local AI. Our first try (`tools/face_test/`) painted ~10 camera views one by one with FLUX.2 klein 4B and projected them
back. Three problems: the AI moves facial features between views (drift up to ~180 px at 1024²), painted light and
shadow end up baked into the colour (and later read as bumps), and seams show where views meet.

**How facts are marked:** *[page]* = page read (README, LICENSE, model card, docs page, arXiv abstract); *[API]* =
GitHub or Hugging Face API (licence field, stars, dates, file lists); *[snippet]* = search-result text only;
*[measured]* = measured on this PC before (RESEARCH.md / just-core RESEARCH.md); *[not re-read]* = how a classic method
works, from background knowledge, its paper not opened this session.

**The user's corrections, applied (2026-10-30):** ranked by quality and capability first — licence, VRAM and platform
are labels beside each option, never filters; every method gets its technique (how it works, key steps, paper) and a
bucket — **(a)** needs no trained model, **(b)** runs on open weights that exist (named, with licence), **(c1)** a small
LoRA or tiny special-purpose model on an open base would do (small training is allowed if it fits 8 GB), **(c2)** needs
real training we can't do; for every (c) a training-free way to the same job is looked for; leading apps and how they
work (§6); every search query is listed (§7).

**Plain words used below**
- *UV map / UV texture* — the flat picture wrapped onto the mesh; every point of the mesh has a fixed spot in it.
- *Albedo* — skin colour with no light or shadow in it. *PBR maps* — the pictures a renderer needs: albedo, roughness
  (matte or shiny), metallic, and a normal map (fake small bumps).
- *Delighting / intrinsic decomposition* — splitting a picture into albedo and shading.
- *Back-projection* — copying each camera view's pixels onto the mesh through that camera. *Seam* — the line where two
  views' paint meet. *Bake* — Blender rendering surface data into a UV picture.
- *Multi-view diffusion* — one AI pass that paints several views together so they agree. *Geometry-conditioned* — the
  AI is shown the mesh's own depth, normal or position pictures for each view, so the paint stays on the mesh.
- *LoRA* — a small add-on file that adjusts a big image model; training one costs a fraction of training the model.
- *ONNX Runtime / ggml / MLX* — ways to run a model without PyTorch: ONNX Runtime (Microsoft, runs on many GPUs),
  ggml (the library under llama.cpp and stable-diffusion.cpp), MLX (Apple).

---

## 0 · Summary

### 0.1 Summary table (ranked inside each group by quality evidence, best first)

Quality evidence is almost all self-reported by each paper; no independent 2026 benchmark covers these methods
(searches 1, 3, 12, 15 — §7). "Without CUDA?" means: is there a documented way to run it on AMD / Intel / Apple.

| # | Method | What it does | Licence code / weights | VRAM (as documented) | Without CUDA? | Last update | Bucket | Verdict for JustStage |
|---|---|---|---|---|---|---|---|---|
| **Paint all views of a given mesh** |||||||||
| 1 | Hunyuan3D-Paint 2.1 (Tencent) | image + mesh → 6 views of albedo + metal/rough, back-projected to UV | Tencent Hunyuan 3D 2.1 Community (excludes EU, UK, S. Korea; >1M MAU needs a deal) / same | "21GB for texture generation"; `--low_vram_mode`; community claims an 8 GB floor, slow *[snippet]* | Apple: MLX conversions exist (`dgrauet/hunyuan3d-2.1-mlx`) *[API]*; its rasterizer is a compiled extension | 2025-10-17 | (b) | The reference method everyone compares to; licence excludes EU/UK/KR users; too big for 8 GB as shipped — use its technique |
| 2 | LumiTex (ICLR 2026) | image + mesh → albedo, metallic, roughness, lighting-aware attention + view-synthesis inpainting | Apache-2.0 badge, no LICENSE file / `FLUX-MV-Shaded` (no licence label), base FLUX.1-dev (non-commercial) | not stated | no port found | 2026-05-31 | (b) NC base; (c2) to rebuild | Strongest 2026 claim ("SOTA over open-source and commercial"); reference |
| 3 | NaTex (CVPR 2026, Tencent + CUHK) | paints colour directly on 3D points (no views, no UV seams) | repo 404 on 2026-10-30 / none found | not stated | — | — | (c2) | Seam-free by design; nothing to run yet |
| 4 | UniTEX (CVPR 2026) | FLUX LoRA multi-view + a "large texturing model" predicting colour as a 3D function | Apache-2.0 / FLUX LoRAs + LTM checkpoints (labels not read) | not stated | no port found | 2026-03-19 | (b); LoRA part (c1)-shaped | Its FLUX LoRA training code (texture + de-lighting) is public — a recipe to copy onto FLUX.2 klein 4B |
| 5 | TRELLIS.2 texture (Microsoft) | shape-conditioned PBR texture from a native 3D latent | MIT / MIT | "at least 24GB" | no | 2026-07-10 | (b) | Claims slightly above Hunyuan 2.1 *[snippet]*; 24 GB; keeping our UVs not verified |
| 6 | MatLat (CVPR 2026 highlight) | PBR texture in a material latent space | no licence / weights "CC BY-NC 4.0" | not stated | no | 2026-07-16 | (b) NC | Reference |
| 7 | MaterialMVP (ICCV 2025) = core of Paint 2.1 | multi-view PBR diffusion, illumination-invariant training | no licence / pro weights = Hunyuan3D-Paint 2.1 | as #1 | as #1 | 2025-07-26 | (b) | Technique of #1 |
| 8 | MVPainter (Alibaba AMAP) | image + mesh → multi-view, ControlNet geometry, PBR extraction | Apache-2.0 / apache-2.0 | not stated | no port found | 2025-07-14 | (b) | Fully Apache PBR painter; VRAM unknown — worth a measured test |
| 9 | Step1X-3D Texture | SDXL + MV-Adapter multi-view with a texture-sync module | Apache-2.0 / apache-2.0 | 27 GB for geometry + texture together | no | 2025-09-08 | (b) | Apache; texture-only VRAM unknown |
| 10 | SeqTex (SIGGRAPH Asia 2025) | Wan2.1 video model writes the UV map directly from the mesh's position/normal maps | no main LICENSE (nvdiffrast non-commercial) / no licence label | tested on A100 80 GB | no | 2025-12-12 | (b) unclear licence | Respects the given UV — good idea; far beyond 8 GB |
| 11 | MV-Adapter (ICCV 2025) | adapter making SD2.1/SDXL paint 6 geometry-conditioned views at once | Apache-2.0 / apache-2.0 (base SD2.1 / SDXL: OpenRAIL++) | SDXL ~14 GB; SD2.1 "<10G" | **yes: ONNX conversion of the SD2.1 image+geometry model** (CPU, CUDA, WebGPU providers) *[page]* | 2025-06-26 (ONNX 2026-10-29) | (b) | **Runs on our ONNX runtime today**; 512² per view — base colour only |
| 12 | FlexPainter | FLUX.1-dev grid of views + view sync + weighting | MIT / base FLUX.1-dev NC | not stated | no | 2025-12-09 | (b) NC base | Grid idea reusable training-free (§1.3) |
| 13 | MVPaint (CVPR 2025) | synced multi-view + 3D inpainting + UV refine | no licence | — | no | 2025-08-22 | (b) | Reference |
| 14 | SyncMVD (SIGGRAPH Asia 2024) | **training-free**: SD1.5 + ControlNet, views denoised together and averaged on the mesh each step | MIT / SD1.5 + ControlNet (open) | not stated | not ported; needs engine-level work | 2025-03-18 | (b) | Proven training-free consistency; needs a per-step hook sd.cpp doesn't document |
| 15 | Paint3D (CVPR 2024) | depth-ControlNet views, then UV inpaint with a UV-position ControlNet, "lighting-less" | Apache-2.0 / apache-2.0 | not stated | SD1.5 ControlNet → sd.cpp has SD1.5 ControlNet (not tried) | 2024-11-05 | (b) | UV inpaint part may run on our engine |
| 16 | TEXGen (SIGGRAPH Asia 2024) | diffusion directly in UV space with 3D point attention | no LICENSE / apache-2.0 | 24 GB for testing | no | 2024-12-18 | (b) | Reference |
| 17 | FlashTex (Roblox) | LightControlNet: paints under known light so light can be removed | Apache-2.0 / MIT | not stated | no | 2024-12-12 | (b) | Relightable idea |
| — | CaliTex, TEXTRIX, MV2UV (CVPR 2026), RomanTex (ICCV 2025), TOPOS (2026) | — | not released | — | — | — | (c2) | Watch |
| **Split colour from light (delighting, PBR from pictures)** |||||||||
| 1 | Marigold V2 albedo (Huawei, TOG / SIGGRAPH Asia 2026) | picture → linear albedo (also normals, depth) | Apache-2.0 / Apache-2.0 (LoRA on Qwen-Image-Edit-2509, apache-2.0) | "1024² needs about 17 GB" (4-bit DiT) | ComfyUI int8 repack (`Comfy-Org/marigold-v2-0`) *[API]*; sd.cpp runs Qwen-Image-Edit + LoRA (not tried with Marigold's VAE/embeddings) | 2026-09-13 | (b) | Newest, permissive; size is the problem — test on sd.cpp |
| 2 | IDArb | albedo/normal/material from **many views at once** | MIT / no licence label | tested on A100 | no | 2025-07-09 | (b) | Fits our multi-view case; weights' licence unknown |
| 3 | IntrinsicAnything (ECCV 2024) | albedo + specular from one picture | PRL v1.0 (free, incl. commercial, after registration) / apache-2.0 | not stated | no | 2026-09-15 | (b) | Usable after registration |
| 4 | RGB↔X (Adobe, SIGGRAPH 2024) | picture → albedo, normal, roughness, metallic, irradiance | Adobe Research License (noncommercial) / no label | "minimum of 12GB" | no | 2026-01-24 | (b) NC | Reference |
| 5 | Marigold IID v1.1 | albedo, roughness, metallicity; or albedo, shading, residual | Apache-2.0 / openrail++ | SD2-sized (not stated) | **ONNX conversion exists** (`ShaderError/luxtractor-marigold-iid`, no licence label) *[API]* | 2025-05-20 | (b) | Small, ONNX-ready fallback |
| 6 | V-RGBX (CVPR 2026), DiffusionRenderer (NVIDIA, CVPR 2025) | video inverse rendering | Apache code / CC BY-NC weights; NVIDIA non-commercial / Cosmos version weights not read | Cosmos: ≥16 GB | no | 2026-01 / 2025-10 | (b) NC | Reference |
| 7 | Flat-light LoRAs: Qwen-Image-Edit-2509 Light_restoration, QIE-2511 Studio-DeLight, Flux2-Klein-Delight (9B), Klein4B Albedo | relight a picture to flat, even light | apache-2.0; apache-2.0; "other" (9B base non-commercial); no licence label | as base (Qwen-Edit Q4 ran on this PC; klein 4B ~6 GB) | **yes — sd.cpp runs these bases + LoRA** | 2025-11 – 2026-05 | (b); (c1) to make our own | Flat light, not true albedo; cheap first step |
| 8 | StableDelight | removes shiny highlights only | Apache-2.0 badge / apache-2.0 | not stated | no | 2025-09-18 | (b) | Highlights only |
| 9 | Spherical-harmonic shading division (classic) | fit the light from the known mesh normals, divide it out | — | none | **yes (numpy)** | — | **(a)** | Uses what we have (the mesh); do first |
| **Fill holes in UV; face-specific UV generators** |||||||||
| 1 | TOPOS (2026 tech report) | one portrait → fixed-topology head + relightable UV maps | no code | — | — | 2026-05 | (c2) | Proves the target; nothing to run |
| 2 | OMGTex (CVPR 2026) | face picture → UV texture, gradient-guided alignment | MIT / Google-Drive checkpoints (licence unstated), base FLUX.1-dev (NC) | not stated | no | 2026-06-03 | (b) NC base; (c1)-shaped on FLUX.2 klein | Best open face-UV method found; its UV layout isn't hm08's |
| 3 | FreeUV (CVPR 2025) | face picture → UV albedo without ground truth | CC BY-NC-SA 4.0 | not stated | no | 2025-06-18 | (b) NC | Reference |
| 4 | UVAPM (Dai et al., 2026 journal) | coarse UV albedo model + VAE detail generator | MIT / Baidu checkpoints; uses BFM-based Deep3D | not stated | no | 2026-07-16 | (b) | BFM licence not read |
| 5 | Symmetry fill + LaMa | mirror the seen side; inpaint the rest | — / LaMa Apache-2.0, ONNX `Carve/LaMa-ONNX` apache-2.0 | small | **yes** | 2025-02 | (a) + (b) | Do it |
| 6 | Paint3D UV-position ControlNet | inpaint in UV space knowing each texel's 3D position | apache-2.0 | SD1.5-sized | sd.cpp has SD1.5 ControlNet (not tried) | 2024-04 | (b) | Try |

### 0.2 The face test's three problems and what fixes each

| Problem | Fixes without big training, best first | Bucket |
|---|---|---|
| **Drift** (features move between views) | (1) paint the views *together* with a geometry-conditioned multi-view model (MV-Adapter SD2.1 via ONNX now; Hunyuan3D-Paint 2.1's technique); (2) give each view the approved front view as a *reference* plus that view's depth: `refcontrol-FLUX.2-klein-4B-reference-depth-lora` (Apache-2.0); (3) sequential context — render what is already painted into the next camera and paint only what is new (StableGen "Generate Sequentially", TEXTure); (4) **non-rigid alignment before projection** — warp each new view onto the render of the already-painted texture where they overlap (ConsistenTex, ECCV 2024), by classical optical flow or by face landmarks (MediaPipe, Apache-2.0) | (b), (b), (a), (a)/(b) |
| **Baked light and shadow** | (1) divide out the light fitted from the known mesh normals, and a baked ambient-occlusion map; (2) Marigold V2 albedo or Marigold IID per view before projection; (3) a flat-light LoRA on the edit model; (4) paint under even light in the first place (white world, the face test's setting) | (a), (b), (b), (a) |
| **Seams** | (1) choose one view per mesh face with a graph cut (MRF), level colours across seams, then Poisson-blend (Waechter et al. 2014, `mvs-texturing`, BSD-3); (2) the 80-px edge fade we have; (3) seam-free methods (NaTex, UniTEX's 3D texture function, SeqTex) — not runnable | (a), (a), (c2) |

### 0.3 Rec for the user's decision (attacked)

**Rec:** keep FLUX.2 klein on stable-diffusion.cpp as the painter and add, in this order: (1) reference + depth
conditioning per view with the Apache `refcontrol` klein-4B LoRA, the approved front view as the reference; (2)
sequential context, painting only what's new; (3) optical-flow / landmark alignment of each view to the already-painted
texture before projecting; (4) graph-cut view choice + seam leveling + Poisson blend in UV; (5) spherical-harmonic +
ambient-occlusion shading division, with Marigold V2 albedo as the stronger option if it runs on sd.cpp within 8 GB;
(6) symmetry fill, then LaMa (ONNX) for the rest. Keep MV-Adapter SD2.1 (ONNX) as a second route for the low-frequency
base colour if (1)–(3) still drift.

**Attack:** (a) the `refcontrol` LoRA has 12 likes and is trained for klein *base* 4B, not the distilled klein 4B we run —
unproven on faces at 1024²; that is why (3) exists, which works whichever painter drifts. (b) Optical flow between an AI
view and a render of earlier paint can lock onto lighting differences; landmarks are the backstop for eyes, nose, lips.
(c) Spherical harmonics assume matte skin and soft light; creases keep some shadow — the baked AO division covers the
largest part, the rest is what Marigold would fix. (d) MV-Adapter is 512² per view, below the ~1,880 px the head gets at
4K *[measured]*, so it can only give base colour. (e) Hunyuan3D-Paint 2.1 is the best-evidenced painter, but its licence
excludes EU, UK and South Korea and it needs 21 GB as shipped — it stays a reference, not a dependency. (f) SD2.1's
OpenRAIL++ licence carries use restrictions; whether the family accepts OpenRAIL weights has not been decided — **ask the
user**. What the attack changed: added (3) and the landmark backstop; moved MV-Adapter from first to fallback.

---

## 1 · Painting all views of a given mesh

### 1.1 How the field does it now (2025–2026)

Every leading open painter follows one of three designs:
1. **Multi-view diffusion + back-projection** (Hunyuan3D-Paint 2.x, MaterialMVP, RomanTex, MV-Adapter, MVPainter,
   Step1X-3D, LumiTex, UniTEX stage 1, FlexPainter): an image model is extended so 6–9 views are generated *in one pass*;
   extra attention layers let each view look at the others and at a reference picture; each view also gets the mesh's
   normal and position pictures for that camera. The views are back-projected, blended by how squarely each camera sees
   the surface, holes are filled in UV or on the mesh, then upscaled.
2. **Synchronized denoising without training** (SyncMVD, MVPaint, TexPainter, GenesisTex, VCD-Texture): ordinary image
   models paint each view, but at every denoising step the views' partial results are projected to the mesh, averaged
   and projected back, so they can't drift apart.
3. **Native 3D or UV-space generation** (NaTex, TEXTRIX, TRELLIS.2, TEXGen, SeqTex, UniTEX stage 2): colour is predicted
   directly on 3D points or in the UV picture, so there are no view seams; these need large purpose-trained models.

Survey: *Advances in Neural 3D Mesh Texturing: A Survey* (Perla, Zhang, Mahdavi-Amiri; Eurographics STAR / CGF 45(2),
2026; arXiv 2606.00137) *[page]*; its method list (`sairajk/neural-mesh-texturing`, `data/papers.json`, 72 entries)
*[API]* supplied the 2026 names below.

### 1.2 Methods, best first

**1. Hunyuan3D-Paint 2.1 (Tencent, released 2025-06-13)** — https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1
- What: picture + mesh → PBR texture (albedo + metallic/roughness). Paper arXiv 2506.15442.
- Technique (MaterialMVP abstract, arXiv 2503.10289 *[page]*; MaterialMVP's README says its "Professional Version" *is*
  Hunyuan3D-Paint-v2-1 *[page]*): reference attention (the reference picture's features go into every view);
  dual-channel generation (albedo and metal/rough as two aligned branches with learnable material embeddings);
  multi-channel aligned attention (both branches stay pixel-aligned); consistency-regularized training (pairs under
  different light, so the output doesn't follow the input picture's light). RomanTex (ICCV 2025, same group) adds a
  3D-aware rotary position embedding — a pixel's attention position is its 3D surface point, so the same spot in two
  views is treated alike — and geometry-related guidance (abstract *[page]*; RomanTex code not released *[page]*).
- Key steps to implement: render normal + position maps for 6 cameras (`max_num_view=6, resolution=512` in the README
  example *[page]*; "768 and 512" per MaterialMVP *[page]*) → multi-view denoise with the reference → back-project to UV
  → inpaint unseen → upscale (RealESRGAN x4 is downloaded *[page]*).
- Evidence: README table — CLIP-FiD 24.78 vs Hunyuan3D-2.0 26.44, TexGen 28.24, SyncMVD-IPA 28.39; LPIPS 0.1211 *[page]*.
  Self-reported. TRELLIS.2's paper benchmarks itself against it *[snippet]*.
- Licence (LICENSE *[page]*): "THIS LICENSE AGREEMENT DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH
  KOREA"; "“Territory” shall mean the worldwide territory, excluding the territory of the European Union, United Kingdom
  and South Korea"; above 1 million monthly active users "You must request a license from Tencent". HF
  `tencent/Hunyuan3D-2.1`: other / tencent-hunyuan-community, 85,332 downloads *[API]*. Paint model 2B params *[page]*.
- VRAM: "10 GB VRAM for shape generation, 21GB for texture generation" *[page]*; `--low_vram_mode` flag *[page]*;
  community guides claim 8 GB works slowly; one user couldn't run paint locally at 20 GB+ *[snippet]*.
- Framework: PyTorch 2.5.1 + cu124 and a compiled `custom_rasterizer` *[page]*. Ports: `dgrauet/hunyuan3d-2.1-mlx` (MLX;
  includes `paint_unet`, `paint_vae`, `paint_dino`, `paint_clip`; 2026-08-31) and `zimengxiong/Hunyuan3D-2.1-Paint-MLX`
  *[API]*; whether the MLX code runs paint end to end not verified.
- Older sibling: Hunyuan3D-2.0 paint (RGB only) ships a separate `hunyuan3d-delight-v2-0` model *[API]*; "6 GB VRAM for
  shape generation and 16 GB for shape and texture generation in total" *[page]*; Hunyuan3D-2GP (deepbeepmeep) runs 2.0
  with memory profiles: "By default the memory profile assumes 9 GB of VRAM (profile 3). If you have less but at least
  6 GB of VRAM add --profile 4" *[page]*, last push 2025-03-29 *[API]*.
- Bucket **(b)**. Rebuilding it ourselves is (c2) — its multi-view model is trained on a "Private Dataset" *[page,
  MaterialMVP]*.

**2. LumiTex (ICLR 2026)** — https://github.com/LumiTexPBR/LumiTex, arXiv 2511.19437
- Technique (abstract *[page]*): a multi-branch generator separating albedo from metal/rough with shared lighting
  priors; lighting-aware material attention; geometry-guided inpainting with a large view-synthesis model to complete the
  UV texture. Claims state of the art over open-source and commercial methods (self-reported).
- Code: Apache-2.0 badge, GitHub licence field none *[API]*; README: "This project also uses third-party components with
  non-commercial license: FLUX model, Tencent Hunyuan3D-2.1 rendering code" *[page]*. Weights `Jingzhi03/FLUX-MV-Shaded`
  (no licence label, 2026-04-06) plus a LoRA trained on Step1X-3D data *[API/page]*. CUDA 12.8 *[page]*. VRAM not stated.
- Bucket (b) on a non-commercial base; (c2) to redo on an Apache base.

**3. NaTex (CVPR 2026, Tencent Hunyuan + CUHK)** — https://natex-ldm.github.io/, arXiv 2511.16317
- Technique *[page]*: colour predicted at 3D coordinates — a geometry-aware colour VAE over points (">80×" compression)
  and a multi-control colour diffusion transformer; inputs geometry + image (or a texture to refine); albedo-only
  benchmarks vs multi-view methods and commercial models on shared Hunyuan3D 2.5 geometry.
- Code: `Zeqiang-Lai/NaTex` returned 404 on 2026-10-30 *[API]*. Bucket (c2).

**4. UniTEX (CVPR 2026)** — https://github.com/YixunLiang/UniTEX, arXiv 2505.23253
- Technique *[page]*: stage 1 adapts a large diffusion transformer with LoRA for multi-view textures; stage 2 a transformer
  "Large Texturing Model" predicts *texture functions* (3D point → colour by surface proximity) from images + geometry,
  replacing UV inpainting. Filters drop points seen at grazing angles and high-frequency points that mismatch after
  super-resolution *[page]*.
- Code Apache-2.0 *[API]*; "flux lora checkpoints" and LTM checkpoints released; LoRA training code for "texture
  generation and de-lighting" in `lightillusions/UniTEX-FLUX` *[page]*. Last push 2026-03-19, 214 ★ *[API]*.
- Bucket (b); its LoRA stage is **(c1)-shaped**: the published recipe could be re-run on FLUX.2 klein 4B (§4.3), but it
  needs rendered multi-view training data.

**5. TRELLIS.2 texture (Microsoft, arXiv 2512.14692)** — https://github.com/microsoft/TRELLIS.2
- "Release shape-conditioned texture generation inference code" ✓ *[page]*; MIT code, `microsoft/TRELLIS.2-4B` MIT,
  2.75 M downloads *[API]*; "An NVIDIA GPU with at least 24GB of memory is necessary" *[page]*. Its paper's texture stage
  "reports slightly higher scores" than Hunyuan3D 2.1 *[snippet]*. Whether the output can be baked onto *our* UV layout
  not verified. StableGen's TRELLIS.2 "Native" texture mode uses nvdiffrast and nvdiffrec *[page]*.
- Bucket (b), 24 GB.

**6. MatLat (CVPR 2026 highlight, KAIST)** — https://github.com/KAIST-Visual-AI-Group/MatLat — MatVAE + MatDiff, a
material latent space; "The downloaded checkpoint weights are released under CC BY-NC 4.0" *[page]*; RealESRGAN and LaMa
in post-processing *[page]*. Bucket (b) NC.

**7. MVPainter (Alibaba AMAP)** — https://github.com/amap-cvlab/MV-Painter, arXiv 2505.12635
- Technique (abstract *[page]*): data filtering and augmentation; ControlNet-based geometric conditioning; PBR attributes
  extracted from the generated views (`infer_pbr.py` *[page]*).
- Licence: "all files in this repository are licensed under the Apache License, Version 2.0" *[page]*; weights
  `shaomq/MVPainter` apache-2.0 *[API]*. VRAM not stated. Last push 2025-07-14 *[API]*. Bucket (b).

**8. Step1X-3D Texture (StepFun)** — https://github.com/stepfun-ai/Step1X-3D
- "an SD-XL-based texture synthesis module"; training code adopted from MV-Adapter; "muti-view generation model with
  texture sync module" (2025-05-27); reuses Hunyuan3D 2.0's rasterizer *[page]*. "Step1X-3D is licensed under the Apache
  License 2.0" *[page]*; HF apache-2.0 *[API]*. GPU memory 27 G for geometry + texture, 152 s *[page]*; texture alone not
  stated. Bucket (b).

**9. SeqTex (SIGGRAPH Asia 2025, VAST)** — https://github.com/VAST-AI-Research/SeqTex, arXiv 2507.04285
- Technique *[page]*: a video model (Wan2.1) is fine-tuned to output the UV texture in a sequence with the mesh's position
  and normal maps — it writes the *given* UV map directly ("3 rows: position and normal map, and the final texture map").
  "tested with 1 × NVIDIA A100 80GB"; training "at least 8 GPUs with 80GB" *[page]*.
- No main LICENSE; its third-party file: nvdiffrast "Non-commercial use (research or evaluation purposes only)" *[page]*;
  weights `VAST-AI/SeqTex-Transformer` no licence *[API]*. Bucket (b), licence unclear; (c2).

**10. MV-Adapter (ICCV 2025)** — https://github.com/huanngzh/MV-Adapter, arXiv 2412.03632
- Technique (abstract *[page]*): duplicated self-attention layers in a parallel architecture beside the frozen base
  model (so the base's image quality stays) and a unified condition encoder for camera and geometry. Base SDXL at 768;
  SD2.1 variants since 2025-06-13 *[page]*.
- Steps (from the ONNX model card *[page]*): render the mesh's position and normal maps in 6 cameras → condition encoder
  (T2I-Adapter) → a reference pass on the input picture at t = 0 caching its attention states → 6-view denoise with
  multi-view row/column attention → decode → back-project.
- Licence Apache-2.0 code, `huanngzh/mv-adapter` apache-2.0 *[API]*. VRAM: image-to-multiview "about 14G GPU memory";
  "If your computational resources are limited (VRAM<10G), you can pass `--variant sd21`" *[page]*. Its texture pipeline
  needs NVIDIA's CV-CUDA *[page]*.
- **Port:** `creador/mv-adapter-sd21-onnx` (created 2026-10-29) — "image + geometry → 6 views" on SD2.1-base, fp16, UNet
  weights 1.93 GB; "The graphs need an onnxruntime with the `com.microsoft` contrib operators (the CPU, CUDA and WebGPU
  providers have them)"; licences: UNet/VAE "CreativeML Open RAIL++-M; its use restrictions apply", MV-Adapter
  Apache-2.0 *[page]*. Its conversion scripts are said to be in `puntorigen/waveslice3d`, which returned 404 *[API]*.
- Bucket (b). The one geometry-conditioned multi-view painter that runs on the family's ONNX runtime today; 512² per view.

**11. FlexPainter** (arXiv 2506.02620; MIT; FLUX.1-dev base *[page]*) — multi-view images on one grid, then view
synchronization and weighting before UV projection *[snippet]*. **12. MVPaint** (CVPR 2025; no licence *[API]*) —
synchronized multi-view generation, spatial-aware 3D inpainting, UV refinement *[snippet]*.

**13. SyncMVD (SIGGRAPH Asia 2024, training-free)** — https://github.com/LIU-Yuxin/SyncMVD, arXiv 2311.12891
- Technique *[not re-read]*: the views share one latent texture; at each denoising step each view's predicted clean
  picture is projected into the texture, averaged with the others by visibility, and re-rendered into each view.
- Uses `runwayml/stable-diffusion-v1-5` and `lllyasviel/control_v11p_sd15_normalbae` *[page]*; "The program licensed under
  MIT License" *[page]*; "developed and tested on Linux system with Nvidia GPU" *[page]*.
- Bucket (b), no training. On our engine it needs a hook between denoising steps that sd.cpp's documented CLI/server
  doesn't offer; on ONNX Runtime the UNet loop is ours to write (§4).

**14. TexPainter** (SIGGRAPH 2024; MIT) — training-free latent optimization; "at least have a NVIDIA GPU with 24 GB"
*[page]*. **15. Paint3D** (CVPR 2024; Apache-2.0 *[page]*) — coarse views by depth ControlNet, then a UV-position
ControlNet (`GeorgeQi/Paint3d_UVPos_Control`, apache-2.0 *[API]*) inpaints in UV space and a UVHD stage refines; "a no
lighting baked texture generative model" *[page]*. **16. TEXGen** (SIGGRAPH Asia 2024) — UV-space diffusion; "For testing
only, a GPU with 24GB VRAM will be fine" *[page]*; weights apache-2.0 *[API]*, code no LICENSE *[API]*. **17. FlashTex**
(Roblox) — Apache-2.0 *[page]*, LightControlNet weights MIT *[API]*: views painted under a known light so light can be
separated from colour. **18. TEXTure / Text2Tex** — the 2023 view-by-view baseline the face test resembles: paint a view,
project, mark texels keep / refine / generate, move on; TEXTure MIT; Text2Tex "Creative Commons
Attribution-NonCommercial-ShareAlike 3.0", needs "at least a NVIDIA GPU with 12 GB" *[page]*.

**19. ConsistenTex — "An Optimization Framework to Enforce Multi-View Consistency for Texturing 3D Meshes"** (ECCV 2024,
arXiv 2403.15559) *[page]*: (1) generate an over-complete set of views; (2) select a mutually consistent subset that still
covers the model (semi-definite programs); (3) **non-rigid alignment of the selected views over their overlaps**; (4) an
MRF assigns each mesh face to one view; (3)–(4) iterate, alignment focused near the cuts. No code. Steps 2–4 need no
trained model — bucket **(a)** applied to our FLUX.2 klein views. The direct answer to the drift.

Not released (watch): CaliTex (CVPR 2026, "Under internal review for public release" *[page]*), TEXTRIX (CVPR 2026, "Code
and model weights will be released soon" *[page]*), MV2UV (CVPR 2026, no code in the survey list *[API]*), PacTure
(2505.22394, "view packing" for higher per-view resolution *[snippet]*), TexSpot (2602.12157, point-latent texture
enhancement *[snippet]*), MeshGen (2505.04656, multi-view PBR decomposer + UV inpainter *[snippet]*).

### 1.3 Training-free consistency tricks usable with FLUX.2 klein on stable-diffusion.cpp

| Trick | How | Evidence | Bucket |
|---|---|---|---|
| Reference + depth per view | `refcontrol-FLUX.2-klein-4B-reference-depth-lora`: "fuses a **reference image** (left) with a **depth map** (right) … preserves **identity and style** from the reference while following the **pose and structure** from the depth map" | card *[page]*; apache-2.0, base `FLUX.2-klein-base-4B`, 2026-05-28, 12 likes *[API]* | (b) |
| Sequential context | render the texture so far into the next camera; give it as init/reference; regenerate only uncovered texels | StableGen: "Views are generated one at a time, and each view inpaints only areas earlier views did not cover, using a render of the current texture as context" *[page]*; TEXTure trimap | (a) |
| One canvas for several views | put 2×2 or 3×3 views on one picture so one generation sees them all | StableGen "Generate Using Grid … fast but has lower resolution per view" *[page]*; FlexPainter | (a) |
| Align before projecting | dense optical flow (classical, e.g. OpenCV) or face landmarks (MediaPipe, Apache-2.0 repo *[API]*) between the new view and the render of earlier paint; smooth warp | ConsistenTex step 3 *[page]* | (a)/(b) |
| Pick, don't average | one view per face by graph cut, then seam leveling + Poisson | Waechter et al. 2014 (`mvs-texturing` README *[page]*); ConsistenTex step 4; StableGen "Hard view segmentation with a high view weight exponent" *[page]* | (a) |
| Novel-view LoRA | `fal/Qwen-Image-Edit-2511-Multiple-Angles-LoRA` (apache-2.0, 1,605 likes) turns the camera around a picture | *[API]*; not geometry-locked → drift remains | (b) |

---

## 2 · PBR output and delighting

**1. Marigold V2 (Huawei Bayer Lab; ACM TOG 45(6), SIGGRAPH Asia 2026; arXiv 2609.08084)** —
https://github.com/huawei-bayerlab/marigold-v2
- What: depth, see-through depth, normals and **albedo** ("linear RGB albedo in [0, 1]") from one picture *[page]*.
- Technique *[page]*: all checkpoints "share the frozen Qwen-Image-Edit-2509 backbone and are stored as
  `trainables.safetensors` (LoRA adapters and, where trained, the VAE decoder)"; albedo: "L1 + DINOv3 spatial perceptual
  loss, VAE decoder fine-tuned, 30k steps"; precomputed prompt embeddings replace the 7B text encoder; "All released
  models were trained on a single 32 GB GPU with batch size 1" — LoRA-scale training.
- Evidence: Hypersim IID albedo PSNR 20.78, SSIM 0.811, LPIPS 0.195 *[page]* (self-reported).
- Licence: "Code and models are released under the Apache License, Version 2.0" *[page]*; HF apache-2.0, base
  `Qwen/Qwen-Image-Edit-2509` (apache-2.0) *[API]*.
- VRAM: "Inference at 1024² needs about 17 GB of GPU memory and 2048² about 29 GB; the DiT is quantized to 4 bit when it
  is first loaded"; "Linux, Python 3.10, a CUDA GPU" *[page]*.
- Ports: `Comfy-Org/marigold-v2-0` (apache-2.0: int8 Qwen-Image-Edit-2509 + Marigold LoRAs, VAEs, conditioning
  embeddings; 2026-09-23) and `fal/Marigold-v2-Qwen-Image-Edit-2509-NF4` *[API]*; a community roughness LoRA on it,
  `lefze/Marigold-V2-roughness-test` (apache-2.0, 2026-10-27) *[API]*. stable-diffusion.cpp runs Qwen-Image-Edit 2509 +
  LoRA *[page]*, and Qwen-Image-Edit 2511 Q4_K_M + a LoRA ran on this PC in 92 s *[measured]*; Marigold V2 also needs its
  own VAE decoder and conditioning embeddings — not tried.
- Bucket (b). It also gives normals — relief from pictures without painting it.

**2. IDArb** (arXiv 2412.12083) — https://github.com/Lizb6626/IDArb — "Intrinsic Decomposition for arbitrary number of
input views and illuminations" *[page]* — the multi-view case we have. MIT code *[API]*; weights `lizb6626/IDArb` no
licence label *[API]*; trained on Arb-Objaverse (68K curated models) *[page]*; "tested on CUDA 11.8 with A100" *[page]*. (b).

**3. IntrinsicAnything** (ECCV 2024, arXiv 2404.11593) — https://github.com/zju3dv/IntrinsicAnything — diffusion models
for albedo and specular shading *[page]*. Code: Project Registration License v1.0 — "Use of the Software by a company …
as part of any internal or external product … is permitted free of charge, provided that the Project Use is registered
before such use begins", "regardless of whether the project … is commercial or non-commercial" *[page]*. Weights
`LittleFrog/IntrinsicAnything` apache-2.0 *[API]*. Last push 2026-09-15 *[API]*. (b).

**4. RGB↔X** (Adobe, SIGGRAPH 2024) — https://github.com/zheng95z/rgbx — picture → albedo, normal, roughness, metallic,
irradiance, and back. "ADOBE RESEARCH LICENSE … for noncommercial research purposes only" *[page]*; "only compatible with
NVIDIA GPUs … a GPU with a minimum of 12GB" *[page]*. (b) NC.

**5. Marigold IID v1.1** (prs-eth, arXiv 2505.09358) — appearance (albedo, roughness, metallicity) and lighting (albedo,
diffuse shading, residual) models; code Apache-2.0, last push 2026-09-06 *[API]*; weights openrail++ (2025-05-20)
*[API]*; SD2-based *[RESEARCH]*. ONNX: `ShaderError/luxtractor-marigold-iid` (UNet/VAE ONNX, 2026-07-06, no licence label)
and `ShaderError/luxtractor-marigold-v1-1-onnx` *[API]*. (b).

**6. Video inverse rendering** — V-RGBX (CVPR 2026, arXiv 2512.11799): albedo, normal, material, irradiance; "Code
License Apache_2.0", "Model License CC BY-NC_4.0"; built on Wan2.1-T2V-1.3B *[page]*. DiffusionRenderer (NVIDIA, CVPR
2025 oral): academic version "only may be used or intended for use non-commercially … research or evaluation purposes
only" *[page]*; the Cosmos-Transfer1 version: code Apache-2.0 *[API]*, "at least 16GB VRAM, recommend to have >=48GB",
weights ~56 GB, their licence not read *[page]*. (b) NC / unread.

**7. Flat-light LoRAs on edit models (relighting, not physical albedo)** — all on stable-diffusion.cpp's bases:
- `dx8152/Qwen-Image-Edit-2509-Light_restoration` — apache-2.0, 250 likes *[API]*; fixed prompt "移除光影,使用柔和光线…"
  (remove light and shadow, relight softly); the author notes such LoRAs need paired lit/unlit pictures *[page]*.
- `prithivMLmods/QIE-2511-Studio-DeLight` — apache-2.0 *[API]*: "removes existing lighting and replaces it with soft,
  evenly diffused light while preserving the original identity" *[page]*.
- `linoyts/Flux2-Klein-Delight-LoRA` — base FLUX.2-klein-base-9B (non-commercial base), licence "other" *[API]*.
- `Aero-Ex/Klein4B-AlbedoLoRa` / `Aero-Ex/Klein9B-Albedo` — no model card, no licence label *[API]*.
- Bucket (b); making our own klein-4B one is (c1) (§4.3).

**8. StableDelight** — specular-highlight removal; Apache-2.0 badge *[page]*; `Stable-X/yoso-delight-v0-4-base`
apache-2.0 *[API]*. (b).

**9. (a) Shading division from the known mesh** *[not re-read]*: we rendered the cameras, so each painted pixel's surface
normal is known. Fit 9 spherical-harmonic light coefficients per view by least squares over skin pixels (brightness ≈
albedo × light(normal)), divide each pixel by the fitted shading, and divide by an ambient-occlusion map baked in Blender
(creases, nostrils, eye sockets). This is the standard light model of 3D face-model fitting (Ramamoorthi & Hanrahan
2001); the face test's "painted/clay ratio" is a cruder form. No model, no VRAM.

Commercial delighting: Substance 3D Sampler "Delight (AI Powered) … removes lighting information such as shadows and
highlights from the base color channel … no parameters" *[page]*; Headshot 3 "De-lighting produces a clean, consistent
albedo map" *[page]*; Meshy Retexture "lighting removal" (meshy-6, 2K/4K) *[page]*. Unity's Albedo Generation node is a
non-AI option *[snippet]*.

---

## 3 · UV-space completion and face UV generators

### 3.1 Filling texels no camera saw

1. **(a) Symmetry fill** *[not re-read]*: the head is near-symmetric; fill unseen texels from the mirrored vertex's texel,
   then blend. The face test's seven views cover 69% of the head's texels *[measured]*.
2. **(b) LaMa** — `advimman/lama` Apache-2.0, 10,349 ★, last push 2025-02-05 *[API]*; ONNX `Carve/LaMa-ONNX` apache-2.0
   *[API]*. Image-space inpainting; UV islands aren't continuous, so fill per island or on a re-rendered view.
3. **(b) Paint3D UV-position ControlNet** — SD1.5 ControlNet conditioned on each texel's 3D position *[page]*; sd.cpp has
   "Control Net support with SD 1.5" *[page]* — not tried. stable-diffusion.cpp also documents inpainting masks
   (`docs/image_preprocessing.md`: "`mask` | Inpainting mask") *[page]*, so FLUX.2 klein can inpaint a re-rendered view.
4. Research, not runnable: Meta 3D TextureGen (UV inpainting U-Net), Seed3D-UV (UV-coordinate DiT), Maggiordomo et al.
   2023 (patch-based texture inpainting for photogrammetry), MV2UV (2026) *[snippet]*.
5. Blender's bake margin pads islands so filtering doesn't bleed (manual source `render/cycles/baking.rst` *[page]*).

### 3.2 Face-specific UV generators, best first

- **TOPOS** (tech report, arXiv 2605.14594, 2026-05-14) *[page]*: one portrait → a head on one fixed studio topology
  (TOPOS-VAE + rectified-flow DiT) and "TOPOS-Texture", relightable UV maps from the same portrait by fine-tuning an
  unnamed multimodal image generator. No code or weights. The closest description of what JustStage wants. (c2).
- **OMGTex** (CVPR 2026, arXiv 2605.25778) — https://github.com/XZT24/OMGTex *[page]*: face picture → editable UV texture
  without geometry; an inference-time "gradient-guided refinement strategy" corrects UV misalignment (that module "has
  been disabled by default" in the preliminary release); CANVAS paired dataset; "uses **FLUX.1-dev** as the base
  diffusion model"; checkpoints on Google Drive; recommends AvatarTex or FFHQ-UV post-optimization. MIT code, 14 ★, last
  push 2026-06-03 *[API]*. Its UV layout isn't hm08's → a UV transfer (§5). (b) on a non-commercial base; its technique
  is a DiT fine-tune → (c1) on FLUX.2 klein 4B only if paired face→UV training data existed (none permissive found —
  RESEARCH §7, S10).
- **FreeUV** (CVPR 2025) — https://github.com/YangXingchao/FreeUV — ground-truth-free facial UV recovery; LICENSE
  "Attribution-NonCommercial-ShareAlike 4.0 International" *[page]*; CUDA 12.2 *[page]*. (b) NC.
- **UVAPM / Dai et al.** (Multimedia Systems 2026; arXiv 2506.13233) — https://github.com/wangalong-ahpu/UVAPM *[page]*:
  coarse UV albedo parametric model → VAE detail generator (wrinkles, whiskers, spots) → differentiable render; MIT code
  *[API]*; checkpoints on Baidu; depends on a `deep3d_model` and ArcFace (BFM-based; BFM licence not read). (b).
- **FFHQ-UV** (CVPR 2023) MIT code *[API]*; dataset licence labels conflict *[RESEARCH]*. **AvatarTex** (3DV 2026) MIT
  *[API]*. **HiFiAlbedo** (2406.13149, code promised), **HUST** (ICCV 2025, promised), **Relightify** (2023) *[snippet]*.

---

## 4 · Without CUDA, on 8 GB, and small training

### 4.1 What already runs without CUDA

| Runtime | Runs | Evidence |
|---|---|---|
| stable-diffusion.cpp (MIT, 7,829 ★, push 2026-10-29) — CPU, CUDA, Vulkan, Metal, OpenCL, SYCL | FLUX.2 klein + LoRA (refcontrol, delight/albedo LoRAs); Qwen-Image-Edit 2509/2511 + LoRA (delight LoRAs; Marigold V2 untested); SD1.5 ControlNet (Paint3D UVPos untested); IP-Adapter SD1.5/SDXL; inpaint masks; ESRGAN | README + docs *[page]*; klein 4B at 1024²: 9–13 s, peak 6,060 MiB *[measured]* |
| ONNX Runtime (the kit's `onnx` runtime, MIT, in-process *[RESEARCH]*) | MV-Adapter SD2.1 image+geometry → 6 views; Marigold IID / v1.1; LaMa | model cards *[page]* / *[API]*; MV-Adapter's graphs need `com.microsoft` contrib ops — CPU, CUDA, WebGPU named; DirectML not named |
| MLX (Apple) | Hunyuan3D-2.1 incl. paint weights | *[API]* |
| ComfyUI | MV-Adapter nodes (Apache-2.0, 474 ★), Hunyuan3DWrapper (1,048 ★), ComfyUI-3D-Pack (MIT, 3,896 ★), Marigold V2 templates | *[API]*; ComfyUI on AMD/Intel/Apple not checked this session |
| numpy / Blender | projection, SH shading division, symmetry fill, seam leveling, graph cut, bakes | face test *[measured]* |

### 4.2 8 GB feasibility (RTX 2070 Super)

| Fits as documented | Needs offload / quantization (unmeasured) | Doesn't fit |
|---|---|---|
| FLUX.2 klein 4B (6.1 GB peak *[measured]*); MV-Adapter SD2.1 (texture "<10G", text-to-multiview "smaller than 6G" *[page]*); Hunyuan3D-2.0 via 2GP profile 4 (≥6 GB *[page]*); LaMa; Marigold IID (SD2-sized) | Hunyuan3D-Paint 2.1 (`--low_vram_mode`; community 8 GB claims *[snippet]*); Marigold V2 (17 GB at 4-bit in PyTorch; Qwen-Edit Q4 ran here on sd.cpp *[measured]*); MV-Adapter SDXL (~14 GB) | TRELLIS.2 (24 GB), TEXGen (24 GB test), TexPainter (24 GB), SeqTex (A100 80 GB), DiffusionRenderer-Cosmos (≥16 GB), Step1X-3D (27 GB with geometry), RGB↔X (12 GB), Text2Tex (12 GB) |

### 4.3 Small training on 8 GB — bucket (c1)

| Base | Documented LoRA VRAM (trainer, source) | Fits 8 GB? |
|---|---|---|
| SDXL | "The LoRA training can be done with 8GB GPU memory (10GB recommended)… Use lower dim (4 to 8 for 8GB GPU)" — kohya `sd-scripts`, `docs/train_SDXL-en.md` *[page]* | yes, tight |
| FLUX.1 | "8GB VRAM \| Use `--blocks_to_swap 28`, recommend fp8 format for T5XXL" — kohya `docs/flux_train_network.md` *[page]* | yes, slow (block swap) |
| FLUX.2 klein 4B | SimpleTuner `documentation/quickstart/FLUX2.md`: "`klein-4b` \| ~12GB \| ~8GB \| 32GB+" (bf16 / int8 / system RAM); "Recommended for klein-4b: Single 16GB GPU" *[page]*. musubi-tuner supports klein base 4B with `--fp8_base --fp8_scaled`, `--blocks_to_swap`, gradient-checkpointing CPU offload *[page]*; its README: "12GB or more recommended for image training" *[page]* | borderline — needs a measured run |
| Qwen-Image-Edit | SimpleTuner `QWEN_EDIT.md`: "24 G minimum (with int8/nf4 quantisation)" *[page]* | no |

Trainers: kohya `sd-scripts` Apache-2.0 (push 2026-10-29), `musubi-tuner` (no licence field), SimpleTuner AGPL-3.0,
OneTrainer AGPL-3.0 (supports "Flux.2 Dev and Klein", SD 1.5/2.x, SDXL), ai-toolkit MIT (lists FLUX.2-klein-base-4B;
its FLUX example config is `train_lora_flux_24gb.yaml`) *[API/page]*. Turing caveat: musubi-tuner says its int8 kernels'
main benefit "is speed on GPUs without fp8 support (RTX 30 series and older)" *[page]* — the 2070 Super has no fp8.

(c1) jobs that would pay off: a flat-light / albedo LoRA on klein 4B (pairs rendered in Blender from permissively
licensed textured heads, lit vs unlit — which textures is the open question, RESEARCH S10); a "reference + normal map →
view" LoRA like refcontrol, trained on our own renders; a tiny landmark detector for UV textures (the job OMGTex's
disabled alignment module does).

---

## 5 · A professional pipeline with a Blender character

What the surveyed tools converge on (StableGen, Headshot 3, Meshy, Hunyuan3D): **render guidance from the mesh →
generate views with geometry + reference conditioning → project with angle weights → choose / blend views → delight →
fill unseen areas → bake to the fixed UV → add detail maps separately.** Blender 5.x pieces for each step:

1. Guidance renders: per-camera depth, normal, position and AO; the face test lights clay views with a white world
   Background at strength 1 *[measured]*.
2. Projection: our numpy rasterizer (36,046 triangles → 4,037,726 texels of a 4096² UV in 4 s *[measured]*); Blender's
   own routes are the UV Project modifier and Texture Paint's "Apply Camera Image" (manual pages not re-read).
3. Bake to the fixed UV: Cycles Render Baking — "Baking requires a mesh to have a UV map, and either a Color Attribute or
   an Image Texture node with an image to be baked to. The Active Image Texture node or Color Attribute is used as the
   baking target"; **Selected to Active**: "Bake shading on the surface of selected objects to the active object. The
   rays are cast from the low-poly object inwards towards the high-poly object", with Cage, Cage Extrusion and Max Ray
   Distance (manual source `render/cycles/baking.rst`, main branch) *[page]*. Selected to Active is also how a texture
   made on another topology (FFHQ-UV, OMGTex, a scan) moves onto hm08's UVs once the two heads are aligned.
4. AO for delighting: an AO bake from the same panel *[page]*.
5. Cleanup: stencil and clone painting on a separate layer (Headshot 3 fills gaps "on a separate corrective layer" with
   stencil and clone brushes *[page]*).
6. Detail: relief from the existing skin-detail module (`modules/skin/detail.py`), not from the colour views; Marigold V2
   normals as an option.

---

## 6 · Apps that do this and how they work

Found by searches 2, 6, 10, 12 (§7); internals only where a page states them.

| App | What it does | How it works (from its docs) | Open? |
|---|---|---|---|
| **Meshy — Retexture** | new textures for an existing model from a prompt, a reference image or 1–4 multi-view images (`meshy-7`) | async API; PBR maps (metallic, roughness, normal; emission with meshy-6); 2K/4K/8K; "lighting removal" (meshy-6, 2K/4K); `enable_original_uv` keeps the model's UVs, otherwise Meshy re-unwraps *[page: docs.meshy.ai]*; internals not documented | cloud, paid |
| **Reallusion Headshot 3 / 3.1** (CC5) | photo → head on CC's topology | AI enhancement (neutralize expression, balance light, remove stray hairs, upscale to 4K) → lens correction + morphs → reprojection of the photo onto the updated mesh → stencil/clone fill on a corrective layer → a skin-base preset by age and facial hair → Blend Masking merges face texture and skin base → de-light → primary + secondary normal maps *[page]*; 3.1 released mid-2026 *[snippet]* | paid, needs CC5 |
| **Adobe Substance 3D Sampler** | photo → tileable material | Image to Material (AI) includes the Delight (AI Powered) filter, which "removes lighting information such as shadows and highlights from the base color channel", no parameters *[page]* | paid |
| **KeenTools FaceBuilder** (Blender) | head from several photos | pin reference points to match the mesh to each photo; "One-click texturing" creates a "texture blended from different views"; $19.99/month *[page]*; its Cloud API blends angles "with automatic color correction" *[snippet]* | paid |
| **FaceGen** | head from front + side photos or one photo | *[snippet]* only | paid |
| **Tripo** | texture API | `pbr` flag; text, style or reference image *[snippet]*; internals not documented | cloud |
| **Hyper3D Rodin** | 3D generation with texture | Material PBR/Shaded, Condition Mode Concat/Fuse *[snippet]*; its research paper CLAY (SIGGRAPH 2024) is listed by the survey as synchronized multi-view PBR *[API]* | cloud |
| **Hunyuan3D Studio** (Tencent) | concept → game-ready asset | part-level generation, polygon generation, semantic UV, PBR textures (arXiv 2509.12815 abstract) *[page]* | service |
| **StableGen** (Blender add-on, GPL-3.0, 1,001 ★, push 2026-10-28) | textures meshes and scenes; TRELLIS.2 meshes; SkinTokens rigs | renders guidance per camera, ComfyUI generates; modes: Separately (shared prompt + depth ControlNet + optional IPAdapter), **Sequentially** (inpaint only uncovered areas, with a render of the current texture), Grid, Refine (img2img), Local/Masked Edit, UV Inpaint; Qwen Image Edit gets reference images per view; projections weighted "by visibility and viewing angle"; Marigold for PBR maps; "about 8 GB of VRAM for SDXL, and 16 GB or more for Qwen Image"; Blender 4.2–4.5, 5.1+ *[page: README, wiki]* | open (GPL) |
| **StableProjectorz** | free texturing tool | Unity 6 app, AGPL-3.0, 130 ★, push 2026-08-23 *[API/page]*; keeps the original UVs, mixes projections and removes seams, uses Automatic1111 *[snippet]* | open (AGPL) |
| **Dream Textures** (Blender) | Stable Diffusion inside Blender, with a project mode | GPL-3.0, 8,232 ★; PyTorch, "tested with CUDA and Apple Silicon GPUs" *[RESEARCH]* | open (GPL) |
| **Textures Diffusion** / **FTW3DForge Image Projector** (Blender) | per-view masks + projection + high-res bake / projection from reference images + bake | needs existing UVs; SD + ControlNet installed separately (~$24) / free, GPL *[snippet]* | paid / open |
| **ComfyUI workflows** | node graphs for the open methods | MV-Adapter, Hunyuan3DWrapper, 3D-Pack, Marigold V2 templates *[API]* | open |
| Vendor roundups (3D AI Studio, CGTrader, Polycam, TextureFast, Rodin image-to-PBR) | retexturing, PBR, UV unwrap | vendor claims, no independent tests *[snippet]* | cloud |

No commercial service documents its internal pipeline; the open ones (StableGen, Hunyuan3D, MV-Adapter) all use the
geometry-conditioned views → angle-weighted projection → bake design of §1.1 and §5.

---

## 7 · Search log (WebSearch, standard mode — 16 of the 25 allowed)

1. "new techniques for creating textures from a photo onto a 3D mesh 2026" — a 2026 survey (Perla, Zhang, Mahdavi-Amiri, CGF / arXiv 2606.00137), Mesh2Tex (2023), a variational multi-view patent; no single new method.
2. "best AI texture generator for 3D models" — vendor roundups (3D AI Studio, Tripo, CGTrader, Meshy, Rodin, Substance 3D, ArmorLab, Dream Textures); no independent tests.
3. "state of the art 3D mesh texture generation 2026 outperforms Hunyuan3D-2.1 multi-view PBR" — TRELLIS.2 paper (2512.14692, texture stage vs Hunyuan3D 2.1), Hunyuan3D 2.5 report (2506.16504), MuMA (2503.18461), PBR3DGen; no independent benchmark.
4. "AI skin texture for 3D head model UV map photoreal" — TOPOS (2605.14594), geometry-aware head texture with artist control (2505.04387), StyleUV, SemUV, Headshot 3, Pixa.
5. "remove lighting from photo to get albedo AI tool" — Substance 3D Sampler Delight (AI), a Qwen-Image-Edit-2509 remove-lighting LoRA (fal), Unity's Albedo Generation node, consumer shadow removers.
6. "best software to texture a 3D character head from photos AI 2026" — Headshot 3 / 3.1, FaceGen, KeenTools, Tripo's own guide.
7. "facial UV texture generation diffusion 2026 code released albedo" — OMGTex (2605.25778), Dai et al. coarse-to-fine UV albedo (2506.13233 = UVAPM), HUST (ICCV 2025), Relightify.
8. "intrinsic image decomposition diffusion 2026 albedo state of the art" — DANTE-W (2606.30677, albedo neural texturing distilled from diffusion renderers; no code), SAIL (2505.19751), Intrinsic Image Diffusion (CVPR 2024), Careaga & Aksoy (TOG 2024).
9. "fill missing areas of a UV texture map with AI inpainting 3D model" — Meta 3D TextureGen, Seed3D-UV, Maggiordomo et al. 2023, Vermandere CGVC 2024, MV2UV (2603.15436).
10. "how to project AI generated images onto a 3D character in Blender and bake to UV" — a Project-from-View devlog, a Blender Artists seam thread, FTW3DForge Image Projector, Textures Diffusion, StableProjectorz.
11. "Hunyuan3D-2.1 texture paint low VRAM 8GB GPU" — official 21 GB; `--low_vram_mode`; community guides claim an 8 GB floor (slow); one user couldn't run paint at 20 GB+.
12. "Tripo Rodin Meshy AI texture generation how it works multi-view diffusion PBR technical" — product docs only (Meshy v6, Rodin Material / Condition Mode, Tripo `pbr` flag), MuMA, PBR3DGen; no vendor internals.
13. "training-free multi-view consistent mesh texturing with image editing model FLUX Kontext Qwen-Image-Edit 2025" — ConsistenTex (ECCV 2024, 2403.15559: view selection, non-rigid alignment, MRF), Consistent Mesh Colors (2101.10734); nothing on edit models.
14. "face skin albedo de-lighting from photo diffusion 2025 code relightable texture" — HUST, HiFiAlbedo (code promised), portrait light diffusion (2305.04745), Relightify, AvatarMe++, DANTE-W.
15. "new 3D mesh texture generation paper arXiv September October 2026 PBR multi-view" — nothing from Sep–Oct 2026 surfaced; PBR3DGen, MeshGen (2505.04656), MaterialMVP, PacTure (2505.22394), TexPro.
16. "multi-view consistent 3D head texture generation diffusion fixed topology UV 2026" — no head-specific hit; MV2UV, TexSpot (2602.12157), FlexPainter, MVPaint, MD-ProjTex, TexGen.

Not searches (no budget used): the GitHub API for ~60 repos (licence, stars, push dates, READMEs, LICENSE files), the
Hugging Face API for ~60 models (licence, dates, files, cards) and its model search, the survey's `papers.json`, and
WebFetch of arXiv abstracts, docs.meshy.ai, Adobe Experience League, Reallusion, KeenTools, the StableGen wiki and
Blender's manual source (projects.blender.org).

---

## 8 · Couldn't verify

- Any independent quality comparison: every ranking above rests on the papers' own numbers; no side-by-side on a face.
- VRAM not stated anywhere for: MVPainter, LumiTex, UniTEX, MatLat, SyncMVD, Paint3D, IDArb, IntrinsicAnything, Marigold
  IID; Step1X-3D texture alone; Hunyuan3D-Paint 2.1 in `--low_vram_mode` (community claims only).
- Nothing measured on this PC this session: the refcontrol LoRA on distilled klein 4B; Marigold V2 on sd.cpp (its VAE +
  embeddings); MV-Adapter ONNX speed and VRAM, and whether ONNX Runtime's DirectML provider has the needed
  `com.microsoft` contrib operators; Paint3D's UVPos ControlNet on sd.cpp; klein-4B LoRA training in 8 GB; bf16 on Turing.
- Licences not read or unlabeled: SeqTex, IDArb, RGB↔X, `Klein4B-AlbedoLoRa`, `FLUX-MV-Shaded`, the `luxtractor` ONNX
  weights (no labels); UniTEX's LoRA/LTM checkpoints; Cosmos DiffusionRenderer weights; Hunyuan3D-2.0's licence text
  (only 2.1's read); OMGTex checkpoints; BFM (UVAPM); MediaPipe Face Landmarker's model card; LaMa's training-data terms.
- TRELLIS.2: whether its texture output can land on our UV layout.
- Code not found or not released: NaTex (`Zeqiang-Lai/NaTex` 404), `puntorigen/waveslice3d` (404), RomanTex (README
  only), CaliTex, TEXTRIX, MV2UV, TOPOS, ConsistenTex, DANTE-W, HiFiAlbedo, HUST, MeshGen (repo not found by name).
- Whether the MLX Hunyuan3D-2.1 port runs the paint stage end to end; ComfyUI's AMD / Intel / Apple support.
- How Meshy, Tripo, Rodin, 3D AI Studio and Hunyuan3D Studio texture internally (no docs say).
- Classic-method descriptions marked *[not re-read]* (SyncMVD's step, spherical-harmonic shading, symmetry fill): papers
  not opened this session; Waechter 2014 confirmed only through the `mvs-texturing` README (BSD-3, 1,111 ★, push
  2026-03-11 *[API]*).
- The professional scan pipeline (cross-polarized capture, wrapping a base mesh to a scan, Mari / texturing.xyz detail):
  not searched this session; left out rather than claimed.
- Hunyuan3D 2.5 / 3.x paint: no open weights on Hugging Face (`tencent` lists Hunyuan3D-2.1, -2, -2mini, -2mv, -Omni,
  -Part, -1) *[API]*; their texture method is described only as "extended from Hunyuan3D 2.0 Paint model" *[page]*.
