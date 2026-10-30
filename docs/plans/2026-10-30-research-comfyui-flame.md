# Existing methods first: ComfyUI nodes, FLAME-Universe, photo→head-texture apps, FLAME alternatives (research, 2026-10-30)

The user's question, verbatim: "https://github.com/TimoBolkart/FLAME-Universe   https://comfy.icu/node/BD_FlameFit  did we
reall check all confy ui stuff to see if somehwone doesnt already havea a really good working method alreayd?"
Added by the coordinator: question 4, "best alternatives to the FLAME head model for photoreal heads".

**Scope.** Our pipeline today: GNM identity on the hm08 mesh → 10 clay views → FLUX.2 klein repaints each view → MediaPipe
warp → NumPy projection onto hm08 UVs. Known gaps: lost mid-scale shape (eye bags, lids, lip shape), lost colour
variation, no real delighting, weak specular, no lashes. Methods already covered in the other `2026-10-30-research-*.md`
files (MV-Adapter, Hunyuan3D-Paint, Marigold IID/V2, StableNormal, Sapiens2, DAViD, MoGe-2, RealDenseFace, Pixel3DMM,
Skullptor, ICT-FaceKit, OpenDelight, SeedVR2, TRELLIS.2, FLUX.2 klein, Krea 2, StableGen, StableProjectorz, flat-light
LoRAs) are only cross-referenced here, not re-researched.

**Labels.** *[page]* = I read the page, README, LICENSE or code; *[API]* = GitHub / Hugging Face / ModelScope / Comfy
registry API; *[snippet]* = search-result text only; *[prior]* = from our earlier research files. Licence, VRAM and platform
are labels, never filters. "Fits 8 GB?" is judged against our RTX 2070 Super (8 GB, Turing, no bf16), 32 GB RAM, Windows.
Ranking inside every table is by result quality, best first, on the evidence found (almost all of it self-reported).

---

## 0 · The answer in short

1. **Yes, someone in ComfyUI already does what we do — and it is not better.** BrainDead's FaceWrap (the pack that holds
   `BD_FlameFit`) is our design: landmarks → fit → per-view projection bake → angle-weighted blend → AI fill → UV transfer
   to CC5/MetaHuman. Its FLAME fit is weaker than our GNM work (FLAME shape is re-fitted **separately per view** to 105
   sparse MediaPipe landmarks with a weak-perspective camera, "~3–4px landmark RMSE"), and it has no delighting, no normal
   or displacement maps, no lashes *[page: code + docs/face-wrap.md]*. It would not close any of our gaps.
2. **The one new, relevant ComfyUI method is UltraTex** (SIGGRAPH Asia 2026): a mesh + one reference image → 6 (or 10)
   geometry-conditioned views painted **together** at up to 2048², albedo then metal/rough, baked onto the mesh, optionally
   **keeping our UVs**; a GGUF low-VRAM build reports "6.8 GB VRAM at 1536 on an 8 GB laptop" *[page]*. It is an object
   texturer; no face results are shown.
3. **Not found in ComfyUI** (searches 1, 5, 6, 8, 10, 11, 14, 36, 38 plus registry/GitHub/HF keyword searches — a gap in
   the search, not proof of absence): a face-specific delighter that gives true albedo, a face pore/wrinkle displacement
   predictor, a face-UV generator for a given layout, a FLAME/3DMM *photometric* fitter.
4. **The commercial apps don't get realistic skin from the photo projection.** MetaHuman *synthesises* the albedo from a
   scan-trained model (driven by skin tone + a "high frequency" index) and *selects* normal and cavity maps from a library;
   Headshot 3 lays its reprojection over its own base skin (diffuse/normal/roughness) and adds AI DeLight plus two normal
   layers; pro Wrap users transfer scanned TexturingXYZ micro-detail (§3).
5. **FLAME alternatives:** no base shape space found is shown to beat GNM (GNM's own paper: 1.683 vs FLAME 2.172 mm
   single-view, 0.748 vs 0.971 mm scan fitting *[prior]*). What adds shape detail beyond any of them is a **displacement
   layer** on top: HeadCraft (FLAME + StyleGAN2 displacement), FaceScape's 4K displacement scans, DECA/EMOCA/HRN detail
   maps, NPHM's neural SDF (§4).

### 0.1 Most promising for our pipeline (6, each attacked)

| # | What | Why, and what it would replace in our pipeline | Attack (what fails, costs, or stays open) |
|---|---|---|---|
| 1 | **UltraTex, low-VRAM ComfyUI build** | Replaces our 10 independent klein repaints + MediaPipe warp with one jointly-denoised, normal-conditioned multi-view pass trained to output **albedo** (and metal/rough), baked to our hm08 UVs (`keep_existing`) | Trained on objects (G-buffer TexVerse), no faces shown → likeness and skin realism unproven; one reference image only; LoRA is MIT but runs on FLUX.2 klein **base 9B** = FLUX Non-Commercial *[API]*; needs Triton, untested on Turing; 5.5 GB model + 6.8 GB text encoder → offloading on 8 GB; paint-only — no displacement. What the attack changed: it is a test candidate against our current views, not a swap. |
| 2 | **Hunyuan3D-2 delight model** (ComfyUI `Hy3DDelightImage`) | Adds the missing per-view delight before projection; it is a Stable Diffusion InstructPix2Pix model *[API: model_index.json]*, so SD-sized and plausibly within 8 GB | No face results found (search 41); trained for objects; Tencent Hunyuan Community licence excludes EU/UK/KR *[prior]*; Marigold V2 albedo is the stronger model but 17 GB *[prior]*. Survives as the cheapest real delighter that fits; size not measured. |
| 3 | **Inverse rendering on our known mesh** — NextFace's per-texel stage, GTAvatar's UV-space version | Replaces "average the projected paintings" with a solve: fit light + per-texel diffuse albedo, specular, roughness (and a normal residual) so that rendering our mesh reproduces the 10 views. That is how NextFace (GPL-3.0) and GTAvatar (≥5 GB) separate light from colour; the methods are published, so we write our own | AI-painted views don't share one physical light → per-view light terms needed, and AI shading inconsistencies leak into albedo; mitigated by painting under a known even light. Needs a differentiable renderer (nvdiffrast is NVIDIA non-commercial *[prior]*; PyTorch3D BSD) — a new piece, not built. |
| 4 | **HeadCraft displacement** (3DV 2025) | Targets the lost **mid-scale shape** (eye bags, lids, lip shape): a StyleGAN2 space of scan-level displacements on a subdivided FLAME; its README fits the latent to a full or **partial** UV displacement map; we would estimate that from our views' normals/depth and move it to hm08 through the FLAME→GNM→hm08 surface map | Weights' licence unstated; trained on NPHM scans (dataset under a "much stricter" licence *[page]*) and needs FLAME files (NC unless FLAME 2023 Open suffices — unverified); the FLAME↔GNM map isn't built; a GAN prior can give plausible-but-not-this-person detail. |
| 5 | **FFHQ-UV (+ TRUST) as a colour prior** | 50K+ evenly lit, neutral 1024² face UV textures (HF dataset MIT *[API]*) with a FLAME conversion; build a PCA/statistics prior to fill unseen texels with real colour variation and to pull delighting toward a real albedo distribution — the low-frequency-model + high-frequency-from-photo split that arXiv 2401.16534 does with the MetaHuman albedo database *[snippet]* | Maps are StyleGAN-derived, 1024² (below our ~1,880 px head at 4K *[prior]*), HiFi3D++ topology → a map transfer; the source images are FFHQ (licence not re-read this session); TRUST is MPI non-commercial *[page]*. |
| 6 | **The pros' layering** (MetaHuman, Headshot 3) | Replaces "every channel from the projection" with: projected albedo for low/mid frequency only + a scanned micro-detail layer (normal + cavity) chosen per person, as MetaHuman's `SelectNormal`/`SelectCavity` and Headshot's base skin do | Needs open scanned micro-detail; the open sources and their licences are in the skin-detail file §2.4 *[prior]* — this search added no new source. |

---

## 1 · ComfyUI custom nodes and workflows (question 1)

Where I looked: comfy.icu node pages, the Comfy registry API (`api.comfy.org/nodes/search` for flame, face uv, face
texture, uv texture, delight, albedo, texture projection, mesh texture, face mesh, 3dmm, deca, head, skin, normal map,
intrinsic, relight, displacement, face reconstruction, facewrap, metahuman), GitHub repository search (comfyui + flame /
face texture / uv face / head texture / delight / 3dmm / face reconstruction / texturing mesh), Hugging Face model search
(face-uv, uv-texture, faceuv, head-texture, skin-texture, delight, albedo, uvmap), and web searches (§5). Civitai and
OpenArt pages never came back from the search tool, so workflows hosted only there are a **search gap**.

### 1a · A photoreal face/head UV texture for a given mesh, from one or many images

| # | Node pack / workflow | What it actually does | Model underneath | Licence code / weights | Last update · popularity | VRAM (stated) | Fits 8 GB? |
|---|---|---|---|---|---|---|---|
| 1 | **UltraTex** — `visualbruno/ComfyUI-UltraTex`, low-VRAM nodes `Mstafa-awad/UltraTex-ComfyUI-nodes`, Windows installer `pixelartistry/PixelArtistry-UltraTex` | Prep renders 6 canonical G-buffer views (world normals + masks) of the mesh and aligns the RGBA reference to the front; the sampler paints all views at 1024–2048² (a 10-view mode adds 4 cameras at 45°); albedo pass then metallic-roughness pass; Bake back-projects with "two-band fusion, exposure matching, mesh hole fill"; UVs: GPU unwrap, xatlas, or `keep_existing` *[page]* | FLUX.2 klein **base** 9B + UltraTex LoRA + foreground-aware VAE decoder; Qwen3-8B text encoder, empty prompt *[page]*. Paper: background-token dropping + block-sparse attention make 2K multi-view feasible *[page]* | code MIT; low-VRAM nodes GPL-3.0 *[API]*; LoRA + decoder MIT *[API ModelScope]*; base 9B FLUX Non-Commercial *[API]* (4B base is Apache-2.0 *[API]*, but "the 9B LoRA will not fit the 4B model" *[page]*; the training code supports 4B) | official repo 2026-10-07, 124★; visualbruno 2026-10-24, 48★; low-VRAM 2026-10-27, 17★ *[API]*; weights 5,688 downloads *[API]* | fp8: "~9 GB model alone, tested on 16 GB"; GGUF: Klein 5.5 GB + TE 6.8 GB loaded, "6.8 GB VRAM at 1536 on an 8 GB laptop (reported by MostAadTech)", "Runs on a 6 GB GPU at 1024" *[page]* | **reported yes** (GGUF + Triton); Turing untested |
| 2 | **Hunyuan3D-2.1 Paint wrappers** — `kijai/ComfyUI-Hunyuan3DWrapper`, `visualbruno/ComfyUI-Hunyuan3d-2-1` | mesh + image → 6 views of albedo + metal/rough → UV *[prior: ai-texturing §0.1 #1]* | Hunyuan3D-Paint 2.1 | wrappers NOASSERTION *[API]*; Tencent Hunyuan 3D 2.1 Community *[prior]* | kijai 2026-03-16, 1,048★; visualbruno 2026-09-08, 392★ *[API]* | "20 GB+" for Paint (a creator), 12 GB for the whole 2.0 process (docs.comfy.org) *[snippet]*; 21 GB official *[prior]* | no as shipped |
| 3 | **ComfyUI-Trellis2** `Mesh Texturing (Multi-View)` + experimental `Projection MultiView Texturing` | mesh + 1..n images → texture through TRELLIS.2's texture latent; projection nodes + example "Projection_Blender_Qwen_XViews" (Blender renders → Qwen edit repaints → project back) *[page: changelog]* | TRELLIS.2; Qwen-Image-Edit | MIT / MIT *[API]* | 2026-09-25, 876★ *[API]* | TRELLIS.2 "at least 24GB" *[prior]* | TRELLIS path no; the projection path is our own design |
| 4 | **BrainDead FaceWrap** — `BizaNator/ComfyUI-BrainDead` (`BD_FaceLandmarks` → `BD_FaceFit`/`BD_FlameFit` → `BD_FaceTextureBake` → `BD_UVConfidenceBlend` → Qwen inpaint → `BD_FaceWrapComposite` → `BD_UVTransfer`) | 4 photos → MediaPipe 478 landmarks → fit (MediaPipe canonical mesh = pure assembly; ICT-FaceKit = Procrustes of the **neutral** head; or FLAME) → nvdiffrast per-view UV bake, confidence = view cosine → blend with confidence^3 → Qwen Image Edit fills gaps → composite that keeps baked pixels byte-identical → UV→UV warp to CC5/MetaHuman via a one-time correspondence *[page: docs + code]*. No delight in the chain | MediaPipe, ICT-FaceKit, FLAME 2023, nvdiffrast, Qwen-Image-Edit | `pyproject.toml` says MIT; no LICENSE file *[API/page]*; bundled ICT mesh MIT, MediaPipe mesh Apache-2.0 *[page: NOTICE.md]* | 2026-09-24, 15★ *[API]* | small for fit + bake; Qwen edit as its own model | bake yes; Qwen fill only quantised |
| 5 | **GLB Face Retexture** — `KaletoAI/ComfyUI-GLB-Face-Retexture` | one face photo → landmark + semantic-mask registration onto the face region of an existing GLB; `light_balance`, `tone_match`, `skin_recolor`; geometry untouched; planar projection *[page]* | MediaPipe (CPU worker) | Apache-2.0 *[API]* | 2026-10-22, 1★ *[API]* | CPU | yes; "verified on Linux", Windows GUI not verified *[page]* |
| 6 | **ComfyUI-3D-Pack** | node suite wrapping Hunyuan3D-2, TRELLIS etc.; a "3D mesh + reference image → mesh with RGB texture" workflow *[snippet: wiki]* | per wrapped model | MIT / per model *[API]* | 2025-12-29, 3,897★ *[API]* | per model | per model |
| 7 | **StableGen** (Blender add-on driving ComfyUI) | sequential/grid/refine painting of a mesh *[prior]* | SDXL/FLUX + ControlNets | GPL-3.0 *[API]* | 2026-10-28, 1,017★ *[API]* | per model | per model |
| 8 | **Meshy / Tripo API nodes** (built into ComfyUI) | Meshy Texture Multi-View: 1–4 reference views texture an existing model, first = front *[snippet: docs.comfy.org]*; "lighting removal" *[prior]* | proprietary cloud | paid API | — | cloud | n/a |
| 9 | `A043-studios/comfyui-pixel3dmm` | claims Pixel3DMM reconstruction + UV prediction; README install steps use placeholder URLs ("your-repo") *[page]* — looks unfinished; the official Pixel3DMM is in the photo-to-head file | Pixel3DMM | MIT badge, NOASSERTION *[API]* | 2025-06-10, 10★ *[API]* | not stated | unknown |

### 1b · Delighting a face photo or texture

| # | Node | What it actually does | Model underneath | Licence code / weights | Last update · popularity | VRAM | Fits 8 GB? |
|---|---|---|---|---|---|---|---|
| 1 | `visualbruno/ComfyUI-Marigold-v2` | Marigold V2 albedo / normals / depth *[API description]* | Marigold V2 (LoRA on Qwen-Image-Edit-2509) *[prior]* | Apache-2.0 / Apache-2.0 *[API]* | 2026-09-16, 15★ | "1024² needs about 17 GB" *[prior]* | no as shipped (int8 repack `Comfy-Org/marigold-v2-0` *[prior]*) |
| 2 | `Hy3DDelightImage` + `DownloadAndLoadHy3DDelightModel` (kijai Hunyuan3DWrapper) | makes "a de-lit version of an input image"; `cfg_image` sets faithfulness to the input; "more useful for real photographs" *[snippet: comfy.icu]* | `hunyuan3d-delight-v2-0` = diffusers `StableDiffusionInstructPix2PixPipeline` (CLIP text encoder, UNet, VAE) *[API: model_index.json]* | wrapper NOASSERTION; weights Tencent Hunyuan Community (`tencent-hunyuan-community`) *[API]* | wrapper 2026-03-16; model repo 250,399 downloads *[API]* | not stated (SD-sized) | likely; not measured |
| 3 | Flat-light LoRAs loaded as ordinary LoRAs: `prithivMLmods/QIE-2511-Studio-DeLight` (6,234 dl), `linoyts/Flux2-Klein-Delight-LoRA` (3,700 dl) *[API]* | relight to flat even light *[prior]* | Qwen-Image-Edit-2511 / FLUX.2 klein 9B | *[prior]* | *[API]* | *[prior]* | *[prior]* |
| 4 | `kijai/ComfyUI-StableXWrapper` | StableDelight (highlights only) + StableNormal *[prior]* | StableDelight / StableNormal | *[prior]* | 2025-01-31, 69★ *[API]* | — | yes *[prior]* |
| 5 | IC-Light / LBM / ReLight nodes (`huagetai/ComfyUI-Gaffer`, `1038lab/ComfyUI-LBM` GPL-3.0, `EnragedAntelope/comfyui-relight`) | relighting; could relight to flat front light, does not output albedo; IC-Light V2 workflow asks ≥10 GB *[snippet]* | IC-Light, LBM | various *[API]* | 2025 *[API]* | ≥10 GB (IC-Light V2 + IPAdapter) | not with IPAdapter |
| 6 | `dreamrec/UniVidX_ComfyUI` | "intrinsic & alpha video decomposition" *[API description]* | UniVidX | GPL-3.0 code *[API]*; weights not read | 2026-05-11, 81★ | not read | unknown |
| 7 | `BD Even Light`, MKRShift `x1TextureDelight`, `ComfyUI-Seamless-Texture` High-Pass Delight / Remove Gradient | divide out a blurred luminance (BD: "a heavy mask-normalised blur of the luminance") or high-pass in LAB *[page/snippet]* | none | MIT / various | 2026 | none | yes — but not face-aware, flattens real shading |

### 1c · Normal / displacement / height maps from face photos (pore and wrinkle level)

| # | Node | What it actually does | Model underneath | Licence code / weights | Last update | VRAM | Fits 8 GB? |
|---|---|---|---|---|---|---|---|
| 1 | `BD Lotus-2 Model Loader / Predict` (BrainDead) | Lotus-2 depth or normal, "much higher quality than feedforward depth estimators" (pack's claim); CPU-offload toggle *[page]* | FLUX.1-dev + Lotus-2 LoRA + LCM bridge | Lotus-2 code Apache-2.0, weights apache-2.0 *[API]*; base FLUX.1-dev non-commercial *[prior]* | Lotus-2 2026-04-25, 309★ *[API]* | official: "at least 40GB" *[page]* | no as shipped; offload untested |
| 2 | Marigold V2 normals, StableNormal, Sapiens2, DAViD | covered *[prior]* | — | — | — | — | *[prior]* |
| 3 | DSINE / BAE / Metric3D normal preprocessors (`comfyui_controlnet_aux`) | general-scene normals *[snippet]* | various | various | — | small | yes |
| 4 | `NKD Normal Detail` (ComfyUI-NKD-Basic-Tools), `BD Detail Normal From Albedo` | keep a base normal, add the high-pass of the photo luminance as tangent-space detail (UDN blend), no model; the NKD page itself warns that photo brightness is not height *[snippet/page]* | none | — / MIT | 2026 | none | yes |
| 5 | `Normal Map (Simple)`, `ImageToDisplacementMap` (high-pass), `ComfyUI-TextureAlchemy` (height→normal, RNM/whiteout combine) | image filters *[snippet]* | none | NOASSERTION (TextureAlchemy) *[API]* | 2026-04-22 | none | yes |

Not found by searches 6, 14 and the registry/GitHub/HF keyword searches: any node or LoRA that predicts **face**
pore/wrinkle displacement from a photo. The research side of that job (DECA, HRN, FaceScape's pix2pixHD displacement,
HeadCraft) is in §2 and §4.

### 1d · FLAME fitting from images

| # | Node | What it actually does | Underneath | Licence | Last update | VRAM | Fits 8 GB? |
|---|---|---|---|---|---|---|---|
| 1 | **`BD_FlameFit`** (BrainDead) | Per view: staged Adam fit — camera + global pose, then + shape, then + expression + jaw/neck — with a closed-form scale/translation init; targets = 105 MediaPipe landmarks via the official `mediapipe_landmark_embedding.npz`; weak-perspective camera; defaults 100 shape / 50 expression coefficients, 300 iterations; **shape starts from zero for each view, so identity is not shared across views** (code read); "~3–4px landmark RMSE, ~2s/view on GPU"; output = FLAME head (5,023 verts) + per-view 2D vertex positions for the bake. No photometric term, no texture model, no detail *[page: code + docs]* | FLAME 2023 converted by `tools/convert_flame.py` (user supplies it; "NOT bundled — FLAME license") | pack MIT (pyproject) *[page]*; FLAME files under MPI terms | 2026-09-24 *[API]* | small | yes |
| 2 | `SMIRKFaceEstimator` (SMPLx Estimator pack) | SMIRK encoder on a 224² crop → **expression** coefficients for SMPL-X; no identity fit *[snippet]* | SMIRK | SMIRK MIT; drives FLAME (MPI non-commercial) *[snippet]* | — | small | yes |
| 3 | `cedarconnor/ComfyUI-GaussianAvatar` | trains a FLAME-rigged Gaussian head from **video** (MediaPipe or InsightFace tracking), PLY export *[page]* | GaussianAvatars-style 3DGS | no licence *[API]* | 2026-02-01, 3★ | "significant VRAM" *[page]* | unknown |
| 4 | `hype1356/ComfyUI-FLAME-face-map` | **not a fitter**: renders 512² normal / depth / mask from given or random FLAME parameters (for ControlNet); ships FLAME 2023 *[page]* | FLAME 2023, PyTorch3D | GPL-3.0 *[API]* | 2026-09-11, 1★ | small | yes |
| 5 | `comfyui-pixel3dmm` (A043-studios) | see 1a #9 | — | — | — | — | — |

Better fitters outside ComfyUI (Pixel3DMM, RealDenseFace, MICA) are ranked in the photo-to-head file *[prior]*.

### 1e · Multi-view consistent face painting on a mesh

| # | Method / node | Consistency mechanism | Notes |
|---|---|---|---|
| 1 | **UltraTex** (1a #1) | all views in one sequence, conditioned on the mesh's normal renders; 2K per view | object-trained; 8 GB GGUF build reported |
| 2 | Hunyuan3D-Paint 2.1 (1a #2) | multi-view attention + illumination-invariant training *[prior]* | 21 GB |
| 3 | MV-Adapter (`ComfyUI-MVAdapter`) | 6 geometry-conditioned views at once *[prior]* | 512² per view; ONNX route exists *[prior]* |
| 4 | StableGen "Sequentially" | inpaint only what earlier views didn't cover *[prior]* | training-free |
| 5 | Pixal3D multi-view texturing (`ComfyUI-Trellis2` "Mesh Texturing Pixal3D MultiView", `dreamrec/ComfyUI-Pixal3D` for Windows) | TRELLIS.2-based texture latent from multi-view images *[page: changelog; BrainDead README]* | ~10 GB weights *[page]*; licence NOASSERTION *[API]*; not read further |
| 6 | Qwen-Image-Edit-2511 Multiple-Angles LoRA + `ComfyUI-qwenmultiangle` viewport | 96 camera poses from one image *[snippet: HF card]* | **no mesh conditioning** → views won't match our geometry; RunComfy warns facial features drift *[snippet]* |

---

## 2 · FLAME-Universe (question 2)

I read the whole README (285 lines, raw file) *[page]*: sections FLAME, Code (48 repositories), Datasets (16, all in
FLAME topology), Publications (2019–2026). It has **no albedo/appearance section**; appearance work is scattered. Entries
relevant to a photoreal textured mesh: TRUST, DECA, EMOCA, `photometric_optimization` (the FLAME texture space), TF_FLAME,
GaussianAvatars, FateAvatar, MeGA, CAP4D, FLARE, SunStage, polarized-smartphone appearance capture, UltrAvatar, VGG-Tex,
ClipFace, "Towards Realistic Generative 3D Face Models" (AlbedoGAN), DiffusionRig, HeadCraft, SIDER, SurFhead, Next3D,
ReliTalk. The brief's AlbedoMM, HRN, FFHQ-UV and Relightify are **not** in the list (they are BFM / HiFi3D++ based); they
are included below. NextFace (BFM) came from search 39.

### 2.1 Ranked — the best 8 for (a) texture/albedo, (b) detail, (c) relightable appearance bakeable to a mesh

| # | Project | Job | Method (two lines) | Licence code / weights | Last update | GPU | Fits 8 GB? |
|---|---|---|---|---|---|---|---|
| 1 | **GTAvatar** (Eurographics 2026) | (c) | Monocular video → FLAME mesh + 2D Gaussians whose albedo, roughness and normals live in a **conventional UV texture**; relightable with environment maps, textures editable | Apache-2.0 code; Inria Gaussian renderer "non-commercial, research and evaluation"; FLAME geometry + texture space MPI non-commercial *[page]* | 2026-04-20, 19★ *[API]* | "requires at least 5 GB"; 1–3 h training *[page]* | yes (stated) |
| 2 | **HeadCraft** (3DV 2025) | (b) | Registers a highly subdivided FLAME to NPHM scans, bakes the residual as UV displacement, trains StyleGAN2 on those maps; can fit the latent to a full or partial displacement map | code MIT *[API]*; weights on Google Drive, licence unstated; needs FLAME files; trained on NPHM data (separate strict licence) *[page]* | 2025-02-05, 90★ *[API]* | not stated | likely (StyleGAN2); not stated |
| 3 | **FFHQ-UV** (CVPR 2023) | (a) | StyleGAN editing normalises FFHQ portraits to neutral expression and even light, then unwraps to 1024² UV; ships 50K+ maps, a texture decoder and a fitting pipeline; FLAME conversion provided | code MIT *[API]*; HF dataset MIT *[API]*; source images FFHQ (not re-read) | 2026-04-16 (HF mirror) *[page]* | TF 1.15 + PyTorch3D; not stated | not stated |
| 4 | **NextFace** (not FLAME; BFM) | (a)+(c) | Fits BFM 2017 + AlbedoMM priors, then minimises photo-consistency between a **ray-traced** render and the photo(s) to recover per-texel diffuse, specular, roughness UV maps (1024/2048 parametrisations); several photos share one reflectance | GPL-3.0 *[API]*; BFM 2017 (registration form) and AlbedoMM (academic only) priors *[page]* | 2023-10-18, 825★ *[API]* | CPU or CUDA; 4–5 min per optimisation *[page]* | yes |
| 5 | **HRN** (CVPR 2023) | (a)+(b) | Hierarchical representation: low-frequency 3DMM + mid-frequency deformation map + high-frequency displacement map, single or multi-view; texture map generation; head extension on ModelScope (2023-08) | Apache-2.0 *[API]* | 2024-07-12, 548★ *[API]* | "only tested under Ubuntu/CentOS with Nvidia GPUs" *[page]* | not stated |
| 6 | **TRUST** (ECCV 2022) | (a) | Estimates FLAME UV albedo while disambiguating skin tone from scene light (uses scene context); BalancedAlb albedo maps | MPI non-commercial (covers "albedo UV maps") *[page]* | 2023-07-21, 167★ *[API]* | not stated | not stated |
| 7 | **AlbedoGAN** ("Towards Realistic Generative 3D Face Models", WACV 2024) | (a) | StyleGAN2 albedo generator + FLAME shape (MICA/DECA-based) for a photo-realistic rendered face | X11 code *[page]*; modified weights on Google Drive (licence unstated); needs DECA and MICA weights (MPI terms) | 2024-07-30, 298★ *[API]* | not stated | not stated |
| 8 | **DECA / EMOCA v2** (SIGGRAPH 2021 / CVPR 2022) | (b) | Regressor → FLAME shape, expression, albedo, light + a detail code; decoder gives a 256² UV displacement map (person detail + expression wrinkles) | MPI "non-commercial scientific research" (both) *[page]* | DECA 2023-07-23, 2,533★; EMOCA 2024-12-06, 863★ *[API]* | not stated | not stated |

### 2.2 The rest of what was checked

| Project | Job | Status |
|---|---|---|
| FLAME texture space (`HavenFeng/photometric_optimization`) | (a) | PCA albedo in FLAME UV from photometric fits; code MIT, 597★, 2022-03-31 *[API]*; the texture space is under MPI's texture licence, non-commercial *[page: GTAvatar README]*; low frequency |
| AlbedoMM | (a) | diffuse **and specular** per-vertex PCA from 73 light-stage scans, in BFM and FLAME topology; "only for academic research purposes" *[page]*; 2020-06-19; the only open specular-albedo prior found |
| Relightify (ICCV 2023) | (a)(c) | diffusion prior on UV reflectance (diffuse, specular, normals) inpaints the partial UV from a 3DMM fit *[snippet]*; **no code found** (search 18, GitHub search) |
| UltrAvatar (CVPR 2024) | (a) | authenticity-guided diffusion albedo; `USRC-SEA/UltrAvatar` holds only a project page (no code) *[API: contents]* |
| VGG-Tex (2024), S3-Face (CVPR 2025: diffuse/specular/normals + hemoglobin/melanin maps *[page: chatpaper]*), SIDER (3DV 2021) | (a)(b) | no code found (searches 19, 21, GitHub search) — search gap |
| FLARE (SIGGRAPH Asia 2023) | (c) | relightable mesh avatar from monocular video; 149★, 2024-12-04; no LICENSE file read *[API]* |
| FATE (CVPR 2025) | (c) | full-head Gaussians with "neural baking" for UV-space texture editing; code MIT (3DGS licence dependency) *[page]*; 2025-09-07 |
| MeGA (CVPR 2025) | (c) | hybrid mesh (face) + Gaussians (hair); no licence *[API]* |
| CAP4D (CVPR 2025) | (c) | morphable multi-view diffusion → 4D Gaussian portrait; CC BY-NC 4.0 *[page]* |
| GaussianAvatars (CVPR 2024) | (c) | FLAME-rigged 3DGS from multi-view video; CC BY-NC-SA 4.0 *[page]* |
| Polarized smartphone capture (CVPR 2023), SunStage (CVPR 2023), LightHeadEd (2025, phone + polarisers → albedo/normal/specular UV maps *[snippet]*), URAvatar (Meta) | (c) | capture methods; code not found or not checked — see couldn't-verify |
| MARCUS-Avatar ("cascaded diffusion priors and UV-space differentiable shading", arXiv 2606.28144) | (c) | repo `Luh1124/MARCUS-Avatar`, 9★, NOASSERTION *[API]*; not read further |

---

## 3 · Apps that do photo → photoreal head texture today (question 3)

| App | Input → output | What is automated | What makes the skin look real (public docs) | Source |
|---|---|---|---|---|
| **MetaHuman Creator** (UE 5.6+, free under the UE EULA) | textured mesh or footage → MetaHuman | Mesh to MetaHuman tracks markers on a render of the textured mesh, solves the identity, then "Conform from Identity" in the Character editor (5.6 change) *[snippet: from-mesh docs]* | The skin textures are **not** the source photo: albedo is **synthesised** by `FMetaHumanFaceTextureSynthesizer` ("Texture Synthesis module feature set developed in titan") from a skin tone projected to a "Skin UV" value, optionally "using the input HF maps"; normal and cavity maps are **selected** ("Select a normal texture map based on the input parameters", `SelectCavity` "for this HF index"); the cloud service returns normal + cavity, albedo is synthesised locally; baked outputs Basecolor, SRMF (specular, roughness, metallic, fuzz), detail normal, up to 8K at "UE Cine" *[page: API docs; snippet: materials doc]*. "You can also provide your own textures" *[snippet]* | dev.epicgames.com API + docs |
| **Reallusion Headshot 3.0 / 3.1** (28 Apr / 7 Jul 2026; $199 + CC5 $299) | one photo (Image mode) or a mesh (Mesh mode) → CC5 head | "new proprietary AI model … trained on Reallusion's 'vast data set' of facial scans", fills unseen parts of the head; Generated Skin section is "all AI-powered": texture upscaling, DeLight, redness, normal refinement ("Source Normal and Correction Normal maps") *[page: cgchannel, manual]* | Final texture = reprojection + Headshot's **own skin maps** + blend masks (forum moderator); **Base Skin** diffuse/normal/roughness fills what the photo didn't see; **Primary** (macro: muscles, wrinkles) and **Secondary** (micro: pores) normal strengths *[page/snippet]* | cgchannel 2026-07; manual.reallusion.com |
| **KeenTools FaceBuilder** (Blender/Nuke) + Photo-to-3D-Head cloud API | several photos → head with ARKit shapes, MetaHuman/CC UV layouts | AI auto-align of pins; one-click "Create Texture" blends the pinned views into the chosen UV layout (since 2024.1); cloud API blends angles "with automatic color correction" from 3–7 photos *[snippet]* | photo colour only; **no delighting documented** (search 23); realism left to the user's shader | keentools.io, cgchannel 2024 |
| **R3DS / Faceform Wrap** (paid) | scan or sculpt + base mesh → base topology with transferred maps | point pairs → rigid → non-rigid wrap → optical-flow refine → texture transfer *[prior]* | realism comes from **scans**: photogrammetry albedo + TexturingXYZ VFace multi-channel micro-displacement, wrapped/projected and baked (often via xNormal) *[snippet: Daz blog, 3dscanstore]* | — |
| **FaceGen PhotoFit** | 1–3 photos → statistical head | fit a 273-scan PCA space; residual saved as a detail texture *[prior]* | the residual "detail texture" carries wrinkles/pores from the photo *[prior]* | — |
| **Avaturn** | selfies → rigged avatar | AI onto a base; "2048×2048 texture", Mixamo-compatible *[snippet]* | undocumented | aggregators |
| **Daz Face Transfer 2**, **Avatar SDK**, **Sparc3D 2.1 Portrait** (Scenario; "tuned for facial structure, skin texture and hair" — vendor claim) | photo → head | AI; methods undocumented *[snippet/prior]* | undocumented | — |
| **Polywink** | existing head mesh → blendshapes / rig | service; **no texture work** *[prior]* | — | — |

**Pattern** (inferred from the rows): photo colour is used for the low/mid frequencies; the "real" look comes from
(1) a delight step, (2) skin detail that came from **scans** (MetaHuman's selected normal/cavity maps, Headshot's base skin
and a head model trained on scans, TexturingXYZ), and (3) a full skin material (specular/roughness/SSS/fuzz). A
third-party pipeline that uses the MetaHuman albedo database does the same split explicitly: Gaussian low-pass → PCA basis
for the low frequencies, the high-frequency layer kept so "stubble, moles" survive (arXiv 2401.16534) *[snippet]*. An
Unreal forum post of 2026-10-16 describes a WIP "fully automated MetaHuman face texturing from reference images" with
trouble on "eyelids, nose, and ears", no code, and asks whether such a tool exists *[page]*.

---

## 4 · Best alternatives to the FLAME head model for photoreal heads (question 4)

Context: our head space is **GNM** (Google, Apache-2.0, 170 identity directions) on hm08; FLAME is only a bridge for
RealDenseFace *[prior]*. GNM's paper: 1.683 vs FLAME 2.172 mm single-view synthetic error, 0.748 vs 0.971 mm scan fitting
*[prior]*. "Mesh?" = gives a polygon mesh we can texture, rig and export. User's own search results (SMPL-X, NeRFlame /
NeRSemble / neural head avatars, 3DGS head avatars such as FlashAvatar and rigged 3DGS, HeadCraft, DECA, FaceScape) are
all rows below; searches 28–34 added the rest.

| # | Model | What it is | Mesh? | Detail level | Licence code / weights | Last update | GPU | Beats GNM for shape detail? |
|---|---|---|---|---|---|---|---|---|
| 1 | **FaceScape** (CVPR 2020 / PAMI 2023) | 16,940 topologically uniform scans (847 ids × 20 expressions) with **4K displacement + texture maps**; bilinear model; detailed riggable prediction (pix2pixHD displacement) *[page/snippet]* | yes | dataset: 4K displacement (pore/wrinkle); bilinear model "only for base shape" *[page]* | "only released for non-commercial research use"; bilinear v1.6 downloadable without a key; TU data needs a licence key *[page]* | 2026-01-27 *[page]* | n/a | base model: no evidence; its displacement data: yes, as a detail layer (NC) |
| 2 | **HeadCraft** (3DV 2025) | FLAME subdivided + StyleGAN2 UV displacement (§2.1 #2) | yes (FLAME topology + displacement map, animates with FLAME) | scan-level mid/fine shape | MIT code; weights unstated; NPHM data strict; FLAME *[page]* | 2025-02-05 | not stated | **yes, as a layer on top** — the most usable one (transferable through a FLAME↔GNM map) |
| 3 | **NPHM / MonoNPHM** (CVPR 2023 / 2024) | neural SDF heads from 5,200+ scans of 255 people, canonical SDF + deformation field *[snippet]* | **no** fixed topology — marching cubes, then wrap onto hm08 | fine detail *[snippet]* | code MIT; "NPHM dataset … much stricter license" *[page]* | 2024-06 / 2024-11 *[API]* | GPU, not stated | yes as a reconstruction; only a bake/wrap source for us |
| 4 | **FaceVerse v1–v4** (CVPR 2022) | PCA base (28,632 verts; 6,335 simplified) + conditional StyleGAN detail for geometry **and** texture; v2 fits Apple's 52 blendshapes; v3 full head *[page]* | yes | base + StyleGAN detail | BSD-2-Clause repo *[API]*; model-file terms not stated separately | 2024-12-19 *[API]* | not stated | detail module: plausibly; trained on "East Asian" data only *[page]* |
| 5 | **HRN** (CVPR 2023) | 3DMM + deformation map + displacement map (§2.1 #5) | yes | mid + fine | Apache-2.0 *[API]* | 2024-07-12 | not stated | as a detail layer: yes; topology not read |
| 6 | **DECA / EMOCA** | FLAME + 256² displacement (§2.1 #8) | yes | coarse wrinkles at 256² | MPI NC *[page]* | 2023 / 2024 | small | marginal (256²) |
| 7 | **Universal Head Model** (Ploumpis et al., CVPR 2019 / IJCV 2020) | LSFM face + LYHM cranium + ears, eyes, teeth, tongue *[page]* | yes | linear 3DMM, no displacement | "non-commercial research and education purposes only", form signed by academic staff *[page]* | 2026-05-03 *[API]* | n/a | no shared benchmark found |
| 8 | ICT-FaceKit | covered *[prior]* | yes | linear | MIT | 2020 | n/a | *[prior]* |
| 9 | **SMPL-X** | body model whose head **is** FLAME | yes | as FLAME | MPI "non-commercial scientific research" *[page]* | 2024-08-12 *[API]* | n/a | no — not an alternative |
| 10 | Implicit 3DMMs: i3DMM, PhoMoH, imGHUM | implicit heads; i3DMM claims better full-head than FLAME (FLAME ≈ equal on the face); PhoMoH claims the best appearance but FLAME the best Chamfer *[snippet]* | no (extraction only) | — | not read | — | — | reference only |
| 11 | Gaussian / NeRF heads: GaussianAvatars (CC BY-NC-SA), FlashAvatar (MIT code, 247★, 2024-04), Gaussian Head Avatar (custom licence), NeRSemble (no licence), NeRFlame, GTAvatar, FATE, SEGA, SVG-Head, 3DRealHead, OMEGA-Avatar *[page/API/snippet]* | radiance or Gaussian heads, most bound to FLAME | **no** — except GTAvatar/FATE/SVG-Head, which keep UV textures on the FLAME mesh (bake source) | photoreal renders | mostly NC | 2024–2026 | 5 GB+ (GTAvatar) | not a shape model; reference or bake source |
| 12 | Head360, "Towards Native Generative Model for 3D Head Avatar" (artist-designed topology) | parametric full head with neural texture *[snippet]* | yes (claimed) | — | code not found | — | — | unknown — search gap |

**Reading of the table.** No base shape space found has a published win over GNM on the same benchmark. Detail beyond GNM
comes from a displacement/detail layer on top of a base model: HeadCraft (FLAME base, learned from scans, fit to partial
maps), FaceScape-style displacement (data NC), HRN/DECA/EMOCA (regressed from one image, lower resolution), or a neural SDF
(NPHM) used as a bake source.

---

## 5 · Search log

WebSearch, standard mode — 41 queries.

| # | Query | What it returned (titles / URLs) |
|---|---|---|
| 1 | comfyui face texture uv map node from photo | runcomfy Avatar Graph UV Modifier; Hunyuan3D Model to UV; comfy.icu BD_UVConfidenceBlend, BD_FaceTextureBake; Hy3D21MeshUVWrap; Meshy Texture Model; superhivemarket Auto-PBR |
| 2 | comfyui flame fit head model node | comfy.icu BD_FlameFit; RunningHub / iAskAsk SoulX FlashHead (talking-head video, unrelated); docs.comfy.org manager |
| 3 | comfyui head texture from photo workflow 3d character | comfy.org image-to-3d use cases; Meshy 6 Image to Model (comfy.org, 5 languages); RunComfy Z-Image headswap |
| 4 | comfyui mesh texturing texture projection custom node multi-view | github visualbruno/ComfyUI-Trellis2; docs.comfy.org MeshyTextureMultiViewNode (en/ja/ko); runcomfy Tripo Multiview to Model; comfyai.run VisualBrunoToolsProjectionMultiViewTexturing; sourcepulse ComfyTextures |
| 5 | comfyui delight face photo remove lighting albedo node | OpenDelight HF space; comfyai.run ComfyUI-Seamless-Texture; comfy.icu DownloadAndLoadHy3DDelightModel, Hy3DDelightImage, x1TextureDelight; comfydeploy ComfyUI-Remover; Stability Replace Background and Relight |
| 6 | comfyui skin normal map displacement map from face photo pores | github ComfyUI-TextureAlchemy; comfy.icu NKDNormalDetail, NormalMapSimple; imperial.ac.uk spiral; runcomfy TextureViewer; instasd BAE normal preprocessor; comfyai.run ImageToDisplacementMap |
| 7 | StableProjectorz face texture photoreal head | superrendersfarm articles (ja/en/ko/fr/es + blog); cgpress Stable Projectorz |
| 8 | civitai workflow face UV texture map for 3D head comfyui | github A043-studios/comfyui-pixel3dmm; comfy.org workflows (Pixal3D; Hunyuan3D UV unwrap zh-TW/ko); Kirsten Zirngibl auto-texturing (artstation, 2023); comfyui.org HY 3D advanced features |
| 9 | openart comfyui workflow metahuman face texture generate | forums.unrealengine.com "(WIP) Fully automated metahuman face texturing from reference images"; paragraph.xyz avatar post; blenderartists PBR seamless; comfyui.org skin realism; trendshift ComfyTextures; polito thesis; comfyai.run Portrait Master |
| 10 | comfyui DECA EMOCA SMIRK 3D face reconstruction custom node | runcomfy SpectreImg2SMPL; comfyui-pixel3dmm; ComfyUI-Flowty-TripoSR; runcomfy node lists ×2; comfydeploy ComfyUI_FaceProcessor; comfy.icu SMIRKFaceEstimator |
| 11 | comfyui custom node 3D face reconstruction texture UV HRN FFHQ-UV | docs.comfy.org TencentModelTo3DUVNode; FFHQ-UV (Birmingham, deepai, arXiv 2211.13874, ar5iv); comfyui-pixel3dmm; Stable Fast 3D docs |
| 12 | comfyui 3D head avatar from single photo node textured mesh 2026 | ComfyUI-3D-Pack (wiki, repo, comfyonline ×2); docs.comfy.org MeshyImageToModelNode; instasd Hunyuan3D-2 workflow; developers.tripo3d.com ComfyUI nodes |
| 13 | comfyui hunyuan3d paint texture existing mesh low vram 8GB | 3D-Pack wiki; thinkdiffusion Hunyuan3D; docs.comfy.org Hunyuan3D-2 tutorial; patreon posts ×3; runcomfy Hy3DSetMeshPBRTextures |
| 14 | AI generate skin displacement map from face photo pores wrinkles tool 2026 | arXiv 2007.08364 (synthetic face framework); USPTO patents ×3; FaceScape arXiv 2003.13989; UU example-based wrinkle displacement maps; justia patent 20250118027; Disney SkinMicroWrinkles supplementary; NTU pdm paper |
| 15 | comfyui IC-Light delight flat lighting portrait albedo workflow texture | comfyui.org IC-Light V2 and portrait-lighting tutorials ×3; runcomfy IC-Light (de, zh-TW); gumroad IC-Light workflow |
| 16 | best way to make photoreal 3D head texture from photo 2026 | cgchannel Reallusion Headshot 3.0; Headshot 3 manual; KeenTools API/products; EG 2002 "Texturing Calibrated Head Model from Images"; grail realface; scitepress 2006; NWPU full head texture; reallusion headshot pages; EPO patent; creativeainews |
| 17 | single image face reflectance diffuse albedo specular normal maps open source code 2025 2026 | github brownvc/phaced; iris.unimore; bohrium probabilistic face; arXiv 1911.11999; USC single-shot reflectance ×2; papercopilot |
| 18 | Relightify relightable 3D faces from a single image diffusion github code | arXiv 2305.06077; HF papers; paperswithcode; CVF ICCV 2023 page/PDF; arxiv-vanity; mlanthology |
| 19 | facial reflectance reconstruction single image diffuse specular albedo normals CVPR 2025 code released FitMe AvatarMe | liner review (morphable reflectance from low-cost data); CVF Ren CVPR 2024; github limkokholefork/avatarme; Imperial spiral; USC HFFRGI; Waseda; chatpaper 155309 (S3-Face, CVPR 2025) |
| 20 | FLAME albedo texture model photoreal UV texture space high resolution 2025 | arXiv 2409.05396 (FacialFlowNet); TRUST 2205.03962; FLAME multi-view 2308.07551; 2506.13233 coarse-to-fine albedo (UVAPM); vortexstudio texture creation ×2; photometric_optimization mirror; LAM2/LAM render_uvmap |
| 21 | DECA detail displacement map alternative higher detail face wrinkles pores single image 2025 | DECA pages only (paperswithcode, deca.is.tue.mpg.de ×2, MPI publication, HF papers, ar5iv, sinoxiv) |
| 22 | MetaHuman Creator texture synthesis skin texture from mesh how it works albedo normal | dev.epicgames.com GenerateTextures, FMetaHumanFaceTextureSynthesizer ×2, metahuman-materials-and-textures ×2, skin-material-controls |
| 23 | KeenTools FaceBuilder texture from photos delighting blending how it works | superrendersfarm FaceBuilder 2024.1 (6 languages); keentools.io news 2024.1; medium FaceBuilder guide; blendernation 2020, 2022; 3dart.it; 80.lv ×2; cgchannel 2019, 2022, 2024; rebusfarm |
| 24 | MetaHuman 5.6 create texture from source mesh skin texture conform photo texture Unreal | dev.epicgames.com body texture utils 5.6; from-mesh docs ×3; medium MetaHumans 5.6/5.7 guide; metahuman.com 5.6 news; skin-material-tools |
| 25 | Wrap R3DS TexturingXYZ skin detail displacement transfer onto head workflow | pcper skin displacement; 3dscanstore "Making of Michael Clark Duncan"; Daz blog TexturingXYZ (×3 mirrors); carlosfcuervo artstation; ten_24 texture wrapping tutorial |
| 26 | Avaturn selfie to avatar face texture how it works photorealistic skin | dreamina realistic avatar; G2 Avaturn; topai.tools; startuphub; avatarsdk 2017 blog; AvatarizeMe (STAG 2023); hunted.space |
| 27 | Headshot 3 manual DeLight normal primary secondary texture reprojection skin base | manual Generated Skin, Base Skin, Theory for Skin Settings, Texture Adjustment, Pro; Reallusion feedback tracker ×5; forum threads; discussions "wrong skin tone in Headshot 3"; RealityCapture reprojection; rutube tutorial |
| 28 | best alternative to FLAME 3d head model | arXiv i3DMM 2011.14143; PhoMoH 2212.07275; 3dmd; papercopilot FLAME; MPI/ELLIS FLAME pages; FLAME supplementary |
| 29 | best 3d morphable face model 2026 | Egger et al. 3DMM survey (York, paperswithcode, HAL, FAU, ar5iv, MPI); HMC handbook chapter; CACM LSFM news; Imperial spiral; one spam result |
| 30 | high detail parametric head model with displacement | HeadCraft arXiv 2312.14140 (v1, v2, html, pdf, paperswithcode, iris.unina, arxiv-vanity); NPHM arXiv 2212.02761 |
| 31 | new parametric 3D head model 2025 2026 mesh topology identity expression released code weights better than FLAME | i3DMM; "Towards Native Generative Model for 3D Head Avatar" 2410.01226; Head360 2408.00296 (pdf, html); KaoLRM 2601.12736; GANHead; aifilms GNM Head blog; FLAME paper; ECCV 2024 07318; gdut course |
| 32 | FaceScape bilinear model displacement map 4K license download | github zhuhao-nju/facescape (+ forks deeptiu, jjandnn); v7labs FaceScape; nbviewer demo_bilinear_fit; artstation displacement packs (unrelated) |
| 33 | 3D gaussian head avatar bake to textured mesh UV texture export FLAME mesh 2025 | GTAvatar 2512.09162; OMEGA-Avatar 2602.11693; SEGA 2504.14373; 3DRealHead 2604.13171; SVG-Head 2508.09597 (pdf, html); HeadStudio |
| 34 | neural head avatar with mesh and UV texture photoreal relightable from phone video open source 2025 2026 | LightHeadEd 2504.09671 (abs, html, pdf); URAvatar 2410.24223 (pdf, export); GTAvatar 2512.09162v2; sinoxiv |
| 35 | comfyui qwen image edit multiple angles lora consistent head views for 3d texturing | HF 0k-t0/Qwen-Image-Edit-2511-Multiple-Angles-LoRA; runcomfy multiple-angles API + workflow ×2; comfy.org "1 click multiple character angles" template; dev.to guide; sourcepulse ComfyUI-qwenmultiangle |
| 36 | reddit comfyui realistic face texture onto 3D head model project photo workflow skin | runcomfy Tripo image/multiview to model; comfy.icu GLBFaceRetexture (node + extension); armory3d projection texturing; comfyui-pixel3dmm; comfy.icu BD_FaceTextureBake (no Reddit pages returned) |
| 37 | MetaHuman skin texture synthesis model trained on scans high frequency detail how Epic generates face textures | arXiv 2401.16534 "Democratizing the Creation of Animatable Facial Avatars"; arXiv 1612.00523; UE API FTextureSynthesisParams, THighFrequencyData ×2, FFaceTextureRequestCreateParams; EG 2001 skin rendering ×3; facegen tips page |
| 38 | lora face UV texture map metahuman layout flux civitai huggingface | HF santiblanko face LoRA; UE API GetValidFaceTextures ×2, FMetaHumanFaceTextureSynthesizer ×2; cgchannel FaceBuilder 2022.2; digitalproduction KeenTools 2022 |
| 39 | differentiable rendering face reconstruction recover diffuse specular roughness UV maps multi-view photos open source NextFace | github abdallahdib/NextFace, peterzs/nextface; arXiv 2101.05356; MARCUS arXiv 2606.28144; Polarized smartphone 2212.01160; EG "Two-shot Shape and SVBRDF Reconstruction of Human Faces"; deepai |
| 40 | best app photo to 3D head with realistic skin texture 2026 | reallusion photo-to-3d-head; KeenTools cloud (gaming, try-on, home), API; creativebloq; daz forum; 3daistudio avatar template; Headshot Pro mode manual; Scenario Sparc3D 2.1 Portrait; App Store image-to-3D apps; EG "3D-ize U!"; pixa skin generator |
| 41 | hunyuan3d delight model portrait face results remove shadows comfyui | comfy.icu Hy3DDelightImage; docs.comfy.org Hunyuan3D-2 tutorial; runcomfy Tencent 3D Texture Edit; comfyui-wiki Hunyuan3D-2 (es, fr ×2); comfyui.org Hunyuan update |

**Pages read (WebFetch / raw files):** comfy.icu/node/BD_FlameFit; FLAME-Universe README (raw, all 285 lines); BrainDead
README, `docs/face-wrap.md`, `nodes/facewrap/{flame_fit,texture_bake,uv_transfer,confidence_blend,__init__}.py`,
`lib/facewrap/NOTICE.md`, `pyproject.toml`; UltraTex README, project page, arXiv abstract; PixelArtistry-UltraTex and
visualbruno ComfyUI-UltraTex READMEs; UltraTex-Pinokio README; KaletoAI GLB-Face-Retexture README; comfyui-pixel3dmm README;
Character_Creator_Studio, ComfyUI-FLAME-face-map, ComfyUI-GaussianAvatar, facet READMEs; FFHQ-UV, HRN, FaceVerse, HeadCraft,
NPHM (+LICENSE), Universal_Head_3DMM, FaceScape, AlbedoMM, AlbedoGAN, NextFace, GTAvatar, FATE, Lotus-2 READMEs; LICENSE
heads of DECA, EMOCA, TRUST, DiffusionRig, CAP4D, AlbedoGAN, SMPL-X, Pixel3DMM, Gaussian-Head-Avatar, GaussianAvatars,
FaceVerse, FlashAvatar; cgchannel Headshot 3.0 article; Headshot 3 manual "Generated Skin"; UE API
`FMetaHumanFaceTextureSynthesizer`; Unreal forum WIP post; chatpaper S3-Face.

**APIs used:** GitHub repos API (≈60 repositories: stars, push date, licence); GitHub repository search (comfyui+flame,
comfyui+face+texture, comfyui+uv+face, comfyui+head+texture, comfyui+delight, comfyui+3dmm, comfyui+face+reconstruction,
comfyui+texturing+mesh, UltraTex, Relightify, UltrAvatar, VGG-Tex, HeadCraft, SIDER+face, AlbedoGAN, GTAvatar, SVG-Head,
LightHeadEd, 3DRealHead, URAvatar, S3-Face, Lotus-2, FitDiff, FitMe+face, AvatarMe, two-shot+svbrdf+face,
cascaded+diffusion+priors+uv-space+avatar; one query hit the rate limit and was dropped); Comfy registry search (keywords
in §1); Hugging Face model/dataset API (FFHQ-UV, tencent/Hunyuan3D-2, FLUX.2 klein base 9B / base 4B / 4B, Lotus-2;
searches face-uv, uv-texture, faceuv, head-texture, skin-texture, delight, albedo, uvmap); ModelScope API
(Yibo-Zhang/UltraTex).

---

## 6 · Couldn't verify

- **UltraTex on our card:** the low-VRAM nodes need Triton sparse attention; Turing (RTX 20xx, no bf16) is not mentioned
  anywhere; the 8 GB figure is "reported by MostAadTech", not measured by the installer's author. Face quality and how
  delit its albedo is on skin: no face results published.
- **Hunyuan3D delight model:** VRAM on 8 GB and quality on faces — no source (search 41).
- **BrainDead licence:** `pyproject.toml` says MIT; the repo has no LICENSE file.
- **FFHQ's own licence** (the FFHQ-UV source images) was not re-read this session.
- **HeadCraft weights licence** (Google Drive, unstated) and the **NPHM dataset licence text** (only "much stricter" read).
- **FLAME 2023 Open vs academic FLAME** for `BD_FlameFit` / HeadCraft / GTAvatar — which file each needs beyond
  "flame2023.pkl" / "FLAME2020.zip" was not checked.
- **FLARE, MeGA, NeRSemble** licences (no LICENSE file read); **UniVidX** and **Pixal3D** weight licences and VRAM.
- **Code for Relightify, UltrAvatar, VGG-Tex, S3-Face, SIDER, SVG-Head, LightHeadEd, URAvatar, Head360, SunStage,
  polarized-smartphone capture** — not found by the searches/GitHub search above; a gap in the search, not proof none exists.
- **Civitai and OpenArt** workflows — the search tool returned no pages from either site; not covered.
- **MetaHuman texture synthesis internals** ("titan") — undocumented; that its normal/cavity maps are scan-derived is
  inferred from the API's "select" wording and the HF index, not stated.
- **Headshot 3 normals** — whether "Source Normal" is AI-predicted from the photo is not stated in the manual page read.
- **KeenTools delighting**, **Avaturn / Daz Face Transfer 2 / Avatar SDK / Sparc3D internals** — undocumented.
- **HRN's mesh topology** (BFM or other) — not read.
- **Lotus-2 on 8 GB** with BrainDead's CPU offload — not stated.
- **FaceVerse model files' licence** separate from the BSD-2 repo — not stated.
- **comfyui-pixel3dmm** — whether it runs at all (placeholder README).
- **SMIRKFaceEstimator** pack name, licence and update date — snippet only.
