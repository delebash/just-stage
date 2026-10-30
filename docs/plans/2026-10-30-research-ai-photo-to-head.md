# Photo (or AI image) → a 3D head on our base mesh: research, 2026-10-30

*agent, 2026-10-30.* Scope: making a head that looks like the person in a photo and sits on OUR mesh (MakeHuman hm08 +
Google's GNM head wrapped on, 170 identity directions), the way CC5's Headshot 3 and Mesh-to-MetaHuman do it. The
options are ranked by how good the method is. Licence, graphics memory (VRAM) and platform are labels, not filters
(the user's correction).

**Source labels:** **page read** (this session read the page or file), **API** (GitHub or Hugging Face API fields),
**snippet** (a search-result summary only, page not opened), **code read** (this session read the source),
**inferred** (my reasoning, not measured: check before relying on it).

**Buckets** (the user's rule: we can't do full-model training): **(a)** needs no trained model · **(b)** runs on open
weights that exist now · **(c1)** needs only small training that fits 8 GB (a small LoRA, or a tiny special-purpose
network) · **(c2)** needs real training we can't do. Every (c2) item names a training-free way to do the same job.

**Plain words used below**
- *Face model (3DMM, "3D morphable model")*: an average head plus a few hundred "shape sliders" learned from 3D scans.
  FLAME and GNM are face models. *Identity* means the sliders for who someone is; *expression* means the sliders for
  smiles, blinks and so on.
- *Fitting*: searching for the slider values that make the model match a photo.
- *Landmarks*: named points found in a photo, such as eye corners or the tip of the nose. *Dense correspondence*: for
  EVERY face pixel, which point of the model's surface it shows (thousands of matches instead of 68 or 478).
- *Prior / regularisation*: a penalty that keeps the sliders near "a likely face", so the fit can't drift to an extreme one.
- *Gauss–Newton / Levenberg–Marquardt*: standard repeated least-squares solvers. Our failed fit used Gauss–Newton.
- *Chamfer distance (mm)*: the average gap between the reconstructed surface and the true scanned surface. Lower is better.
- *Gaussian splats*: a cloud of soft coloured blobs, renderable but **not a mesh**. It can't be rigged on our topology
  as it stands.
- *UV map / texture*: the flat image wrapped onto the mesh. *Wrap / NICP*: deforming one mesh onto another's surface
  (what `libs/wrap/gnm_to_hm08.py` already does).

---

## 0 · Summary table (ranked by quality within each group)

### 0.1 Fitting a face model to photos (gives the SHAPE)

Single-view accuracy comes from the NeRSemble single-view face-reconstruction (SVFR) leaderboard, Chamfer L1 in mm,
lower is better (**page read**, kaldir.vc.cit.tum.de/nersemble_benchmark/benchmark/svfr).

| # | Method | Output | Licence: code / weights | VRAM | Path without CUDA? | Last update | Bucket | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | **RealDenseFace** (arXiv 2608.09238, Zhejiang U.) — SVFR **1.610** | FLAME params + camera, single image / video / multi-view | **MIT / MIT on the HF card** (API, page read). The encoder is DINOv3 (DINOv3 License: derivatives allowed with "Built with DINOv3"). Trained on Ava-256 (**CC BY-NC 4.0**, README read) + NPHM + FaceScape | not stated | Network: plain ViT + DPT, so an ONNX export is likely (inferred, untested). Solver: CUDA-only, rewrite it in NumPy | repo 2026-10-27, weights 2026-10-29 (API) | **(b)** | **Best measured shape, open weights.** Top pick. |
| 2 | **Pixel3DMM** (ICLR 2026, TUM) — SVFR 1.659 | FLAME params from per-pixel UV + normal maps; single and multi-image | **CC BY-NC 4.0** (LICENSE page read) | not stated | No (CUDA 11.8, nvdiffrast) | 2026-01-12 (API) | (b) NC | Same idea as #1, slightly behind. Its multi-image recipe is a good reference. |
| 3 | PartFusionMI / PartFusion — 1.700 / 1.868 | ? | not found | ? | ? | ? | ? | On the leaderboard only. Couldn't find a paper or code. |
| 4 | FlowFace (CVPR 2024) — 1.973 | FLAME from dense 2D flow | not found (GitHub search empty) | ? | ? | ? | (c2) | Dense-flow idea; no release found. |
| 5 | SHeaP (ICCV 2025) — 2.083 | FLAME, self-supervised with 2D Gaussians | not found | ? | ? | ? | (c2) | No code found. |
| 6 | **Skullptor** (CVPR 2026, Ubisoft La Forge) — 2.260 | **free-form mesh** from a few views (multi-view normals + inverse rendering) | Ubisoft ML License, **research-only** (LICENSE page read). Its own model "trained on private data, we cannot redistribute it" | not stated | No (nvdiffrast) | 2026-05-07 (API) | (b) with the DAViD MIT backbone ("lower quality") | Good model for the "mesh, then wrap" route (§2.5). |
| 7 | SMIRK (CVPR 2024) — 2.276 | FLAME | MIT code; weights' licence unstated; trained on LRS3, MEAD, CelebA, FFHQ (README read) | not stated | No (PyTorch3D) | 2024-05-31 (API) | (b) | Superseded by #1 and #2. |
| 8 | DECA (2021) 2.385 · EMOCA (2022) 2.636 | FLAME | MPI **non-commercial** licence for code AND model (LICENSE page read) | small | No | 2023 / 2024 (API) | (b) NC | Old baselines. |
| — | **MICA** (ECCV 2022) — not on this board; NoW benchmark: 15% / 24% lower error than prior work (snippet) | FLAME identity in **real millimetres**, from a face-recognition embedding | MPI non-commercial; "prohibits … to train … networks … for commercial use" (LICENSE page read) | small | No | 2025-03-17 (API) | (b) NC; our own version would be (c2) | Unique idea: true scale. Pixel3DMM uses it as its prior. |
| — | **GNM's own fitting** (Google, tech report 2607.23687) | GNM identity + expression + pose + camera | GNM Apache-2.0. Its ~600-point dense landmark detector is **not released**; Google says it will "release publicly available the dense landmarks" (page read) | — | — | 2026-10-29 (API) | (c2) until released | The right recipe for OUR model (§1, §5). |
| — | MediaPipe Face Landmarker | 478 points + 52 blendshape scores | Apache-2.0 (API) | CPU fine | **Yes** | 2026-10-30 (API) | (b) | What we used. Fine for eyes and mouth, weak as the only shape signal (§1). |
| — | Microsoft DAViD (ICCV 2025) | per-pixel **surface normals**, depth, foreground matte of people | **MIT code + MIT ONNX models**; trained only on synthetic data (SynthHuman, CDLA-2.0) (README, model card page read) | not stated | **Yes (ONNX Runtime)** | 2026-07-10 (API) | (b) | Clean building block for a normal or silhouette term in our own fit. |

### 0.2 Feed-forward heads from one photo (gives shape + texture, or splats, in one pass)

| # | Method | Output | Licence: code / weights | VRAM | Path without CUDA? | Last update | Bucket | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | **MeshLAM** (CVPR 2026, Alibaba Tongyi) — "Feed-Forward One-Shot Animatable Textured Mesh Avatar Reconstruction" | **FLAME-topology mesh** (~5–8K verts) + **1024² UV texture**, 0.7 s | **No code or weights**: the project page's "Code" button goes to the LAM repo (page read) | not stated | — | arXiv 2026-04-23 | (c2) | The right KIND of output (mesh + UV). Unreleased. Training-free equivalent = our fit + projection pipeline. |
| 2 | FiCA (Meta, arXiv 2606.24232) | Gaussian codec avatar via a diffusion-completed mesh | no code (page read) | — | — | 2026-06 | (c2) | Research only. |
| 3 | **LAM** (SIGGRAPH 2025, Alibaba) | Gaussians bound to FLAME, 1.4 s, plays in WebGL | Apache-2.0 code; weights card front-matter apache-2.0 (HF API licence field empty); trained on **VFHQ + NeRSemble** (README read; their terms not read) | not stated (A100 timings) | Playback yes (WebGL); reconstruction CUDA | 2026-06-10 / weights 2025-04-03 (API) | (b) | Splats, not our mesh. The FLAME it estimates could seed a shape. |
| 4 | GAGAvatar (NeurIPS 2024) | Gaussians on FLAME | MIT code; weights licence not stated | not stated | No | 2026-09-16 (API) | (b) | Splats. |
| 5 | FaceLift (ICCV 2025, Adobe) | 360° Gaussian head (multi-view diffusion → GS-LRM), static | Apache-2.0 code; **weights Adobe Research License** (README page read) | not stated (trained on 8 GPUs) | No | 2026-03-25 (API) | (b) NC | Its multi-view step is the useful idea (§2.4). |
| 6 | CAP4D (CVPR 2025) | 4D Gaussian avatar from 1+ images, morphable multi-view diffusion | **CC BY-NC 4.0** (LICENSE page read) | not stated | No | 2026-03-24 (API) | (b) NC | Heavy. |
| 7 | Arc2Avatar (CVPR 2025) | Gaussians on FLAME, optimised per person with an identity-guided diffusion model (Arc2Face) | MIT code; Arc2Face MIT (API) | "tested on RTX 4090" (README read) | No | 2025-06-15 (API) | (b) | Per-person optimisation; splats. |
| — | HeadGAP (3DV 2025), PanoLAM, Avat3r | — | project pages only, no code (API search) | — | — | — | (c2) | — |

### 0.3 Building blocks for the views and textures

| Block | What | Licence | Runs on our engine? | Bucket |
|---|---|---|---|---|
| Qwen-Image-Edit-2511 + "Multiple-Angles" LoRA (`fal/Qwen-Image-Edit-2511-Multiple-Angles-LoRA`; `dx8152/Qwen-Edit-2509-Multiple-angles`) | turns one photo into the same person seen from other angles | base **apache-2.0**, both LoRAs **apache-2.0** (API) | stable-diffusion.cpp supports Qwen-Image-Edit / 2509 (README read; 2511 not stated) | (b) |
| FLUX.2 klein 4B LoRA training | our own LoRA, e.g. for front/side views of heads | Apache-2.0 base | BFL's training doc: **minimum "NVIDIA with 12GB VRAM"**, 32 GB RAM, AI-Toolkit "12GB+" (page read) → **8 GB does not fit by the docs** | (c1) on paper, not on our card |
| GNM `head_sparse_68.txt` | 68 landmarks as barycentric points on GNM's mesh (68 rows of 3 index/weight pairs) | Apache-2.0 (code read) | NumPy | (a) |
| GNM `fitting_utils/project_on_pca.py` | ridge-regularised least squares of a 3D mesh onto the identity basis, optional `num_components` | Apache-2.0 (code read) | NumPy | (a) |
| MediaPipe `canonical_face_model.obj` | the 468-vertex mesh whose vertices ARE MediaPipe's landmarks | Apache-2.0 (API: file in `mediapipe/modules/face_geometry/data`) | — | (a): wrap it onto GNM once, giving a fixed landmark→GNM map |

---

## 1 · Why our Gauss–Newton fit failed (diagnosis)

Read: `tools/face_test/test_face_fit.py` (**code read**); the result is in TASKS step 4 rounds 4–5: "16.1 → 14.3 px while
bending the identity 19.5 sd". Compared with how the published fitters work:

1. **Only identity was free.** Camera, head pose, scale and expression were fixed. GNM's own image fit solves "identity
   and expression coefficients, joint rotations, root translation, and camera intrinsics" (GNM report, page read). Any
   pose, focal or expression mismatch had to be absorbed by the 170 identity sliders, hence an extreme face that barely
   lowers the error. (inferred, but it matches the symptom)
2. **The targets were inconsistent.** The points came from the AI's repaintings, which TASKS measured drifting 5–15 px on
   head views and ~40 px (worst 182) on close views. Each repainted view is a slightly different face, so no single
   identity fits them all. Fit to real photos, or to views made consistent first (§2.4).
3. **The face-outline points slide.** MediaPipe's jaw and face-oval points follow the visible outline. From the side
   they land on different skin than from the front. The script gives each point ONE vertex by majority vote across
   views, so the outline points become wrong fixed matches. The published fixes: drop the outline points, or re-pick
   their vertex every iteration on the current silhouette. Pixel3DMM's README also calls landmark losses "usually not
   as reliable", stresses "landmark losses in the eye region", and turns mouth landmarks off on good images (page read).
4. **The prior was outweighed.** `PRIOR = 1.0` against residuals in units of 4 px. With ~470 points × 2 coordinates ×
   several views, thousands of data terms face 170 prior terms. The 4 px noise model assumes independent errors, but the
   AI drift is systematic (5–40 px, correlated per view), so the data was over-trusted. (inferred from the code and
   TASKS' numbers)
5. **Sparse points can't pin down depth.** Sparse 2D points from a few views barely constrain depth: the nose length and
   the depth of the eye sockets are almost free. The leaderboard's top three all add DENSE signals: UV correspondence
   per pixel plus relative depth (RealDenseFace); UV plus surface normals plus silhouette (Pixel3DMM).

---

## 2 · Fitting a face model from images: the techniques (part 1)

### 2.1 RealDenseFace: dense UV correspondence + relative depth → Gauss–Newton (rank 1)
- **How it works** (README, model card, configs read; arXiv 2608.09238 abstract page read). A frozen DINOv3 ViT encoder
  (`dino_frozen: true`, ViT-B or ViT-S+, 512² input) with a DPT decoder predicts two maps in the face model's UV space:
  "a correspondence map for UV-to-image alignment" (where each surface point lands in the image) and a relative-depth
  map. A "tailored Gauss-Newton solver" (Levenberg–Marquardt, Cholesky / PCG in `cuda_extensions/flame_solver/src`)
  then fits FLAME identity, expression and pose. The single-image config is: `correspondence_weight 1.0`,
  `relative_depth_weight 2.0`, `damping 0.001`, `pose_damping 0.1`, 20 registration iterations. Offline video mode
  "refines a shared identity from multiple frames"; a calibrated multi-view mode exists (NeRSemble v2 example).
- **Evidence:** best Chamfer L1 1.610 mm and L2 1.086 mm on NeRSemble SVFR (page read); "80+ FPS" online tracking
  (abstract).
- **Key steps to implement:** (1) crop the face (their FaceBox weights); (2) run the network → per-pixel UV and depth;
  (3) turn each confident pixel into a match: image point ↔ surface point given by its UV; (4) Gauss–Newton over
  {camera, pose, expression, identity}, with damping as the prior.
- **Bucket (b)**: weights `LinzhouLi/RealDenseFace` `vitb.pth` / `vits.pth`, card licence MIT (API). Also needs
  `flame2023.pkl` from the FLAME site (whether that is "FLAME 2023 Open" (CC-BY-4.0) or the academic FLAME 2023 is
  unverified). Training data: Ava-256 CC BY-NC 4.0; NPHM and FaceScape (FaceScape non-commercial per RESEARCH §7 S10).
- **How it fits our head:** the network predicts FLAME *UV coordinates*, a surface address, not FLAME sliders. Once we
  have a FLAME↔GNM surface map (§3), our own solver can fit **GNM's** 170 identity sliders straight to these dense
  matches (inferred). The other way: run their FLAME fit, then move the result to GNM (§3).

### 2.2 Pixel3DMM: per-pixel UV + normals + silhouette → FLAME optimisation (rank 2)
- **How it works** (arXiv 2505.00615 abstract and README read): DINO-based ViTs "predict per-pixel geometric cues" —
  surface normals and UV coordinates — and FLAME is optimised to match them, plus a silhouette term, plus landmarks
  mainly for the eyes. It was trained on three high-quality scan sets registered to FLAME ("over 1,000 identities and
  976K images"). The claim is ">15%" better geometry on posed expressions.
- **Multi-image recipe** (README read, worth copying as a pattern): `include_neck=False w_exp=0.1 use_mouth_lmk=False
  w_shape=0.01 w_shape_general=0.001 normal_super=2000.0 sil_super=1000.0 use_flame2023=True ignore_mica=True
  is_discontinuous=True`. That means one shared identity across separate photos, weak shape regularisers, strong
  normal and silhouette terms, and no neck.
- **Bucket (b) NC** (CC BY-NC 4.0). Retraining it is (c2). **Training-free stand-in:** DAViD's MIT normal model (ONNX)
  for the normal term, its matte for the silhouette, MediaPipe for the eyes. That is no UV-correspondence term, so it
  is weaker (inferred).

### 2.3 GNM's own recipe: ~600 dense landmarks + joint solve (the model's makers)
- **How it works** (GNM report HTML, page read): a dense landmark detector (Chandran et al. 2023/2024) predicts
  "approximately 600 landmarks"; re-projection error is the data term. The solve covers identity, expression, joint
  rotations, root translation and camera intrinsics, with "a simple L2 prior on the identity and expression
  coefficients" plus penalties on skin–eyeball and skin–mouth-cavity intersections.
- **Evidence:** single-view synthetic images, mean error **GNM 1.683 mm vs FLAME 2.172 mm**. Scan fitting: GNM 0.748
  vs FLAME 0.971 mm (Table 2/3, page read).
- **Bucket (c2)** until Google releases the landmarks (promised, no date). **Training-free stand-in:** MediaPipe 478 or
  a 68-point detector on GNM's shipped `head_sparse_68` points, solved the same way (§5).

### 2.4 Make the views consistent before fitting (CC5 does this with its AI)
- Headshot 3 generates or regenerates profile and front photos with AI. A Reallusion guide recommends regenerating a
  precise profile when the side photo shows the far eye (snippet: Reallusion Magazine 2026-09-24). FaceLift's first
  stage is a multi-view diffusion model making 6 consistent views (README read).
- Open route: Qwen-Image-Edit-2511 + Multiple-Angles LoRA (Apache-2.0, §0.3), run by stable-diffusion.cpp. **Bucket
  (b).** Caution: our own AI repaintings drifted 5–40 px, so AI views should get LOW weight next to the real photo, and
  each view gets its own expression variables (inferred).

### 2.5 Few-view mesh, then wrap (Skullptor; the "mesh mode" of the pro tools)
- **How it works** (Skullptor README read): a view-aware DPT predicts normals in each of a few views; "a custom inverse
  rendering pipeline" (continuous remeshing) turns them into a mesh "in seconds"; a landmark detector (facer) aligns the
  cameras. The released code can use Microsoft's DAViD normal model instead of its unreleased one, at "lower quality".
- **Then wrap it onto GNM / hm08:** the same NICP as `libs/wrap/gnm_to_hm08.py`, guided by landmarks. This is what
  Mesh-to-MetaHuman and Headshot's Mesh mode do (§4).
- **Bucket (b)** with the DAViD backbone (MIT ONNX). Skullptor's own code is research-only. Rebuilding its idea = (a)
  code on (b) weights.

### 2.6 True scale from identity features (MICA)
- **How it works** (snippet, arXiv 2204.06607): an ArcFace ResNet100 (pretrained on Glint360K, last 3 blocks
  fine-tuned) plus a small mapping network outputs FLAME shape, neutral and in millimetres. It was trained on paired
  photo↔scan data.
- **Bucket:** (b) NC as released. Our version needs photo↔scan pairs with commercial terms, which RESEARCH §7 S10 found
  don't exist → (c2). **Training-free stand-in:** set absolute scale from a known body measure. MediaPipe's iris model
  assumes a roughly constant iris diameter (from memory, not re-read). GNM's mean eyes sit at ±30.8 mm (RESEARCH §5,
  measured).

### 2.7 A tiny network from landmarks to GNM sliders (c1)
- We can sample unlimited GNM faces (Apache-2.0), project their landmarks through random cameras, add noise, and train a
  small network on CPU. **Bucket (c1).** Limit: it sees the same sparse points as a fit, so it gives a good starting
  value and a learned prior, not more accuracy (inferred). It's worth it only as the starting point for §5's solve.

---

## 3 · Moving a FLAME result onto our head (FLAME → GNM → hm08)

- Google built exactly this map: a "dense barycentric mapping between FLAME and GNM" from hand-marked sparse vertices,
  a rigid + scale alignment and a non-rigid deformation, average distance under 0.02 mm (GNM report, page read). It is
  **not in the repo** (the tree was listed through the API: only `head_sparse_68.txt` under `data/landmarks`).
- **Our route, bucket (a):** wrap the FLAME 2023 Open template (CC-BY-4.0, "including commercial use", licence page
  read) onto GNM's mean head ONCE with our existing NICP (it fit hm08 to 0.87 mm mean). For every photo: FLAME result →
  GNM-topology points through the stored map → `project_on_linear_vertex_basis(…, regularization=λ, num_components=k)`
  (GNM's own helper, code read). That gives 170 identity values → our existing MakeHuman targets on hm08.
- **Why this can't blow up the way §1 did:** it's a linear 3D-to-3D least-squares problem with no camera and no depth
  ambiguity, and λ plus a component cap bound the result (inferred from the maths). Whatever GNM can't express stays as
  an optional per-vertex offset.
- Same pattern for MediaPipe: wrap `canonical_face_model.obj` onto GNM once → a fixed MediaPipe-index → GNM-surface
  map. This replaces the per-view ray-cast vote in `test_face_fit.py` (inferred).

---

## 4 · Apps that do this and how they work (part 3)

The leading apps the searches turned up, beyond the user's examples. "How" comes from their own docs or tutorials
where those exist.

| App | What it does | How it works (steps) | Source |
|---|---|---|---|
| **CC5 Headshot 3** (Reallusion, $199) | **Image mode:** front photo (required), side photo and body photo (optional) → a head on the CC base mesh. **Mesh mode:** a scan or sculpt → a rigged CC head | Image: AI tidies the photo ("neutralize facial expressions, balance lighting, remove stray hairs", 4K upscale) → "Reallusion's proprietary AI" makes the head → align points: Auto Detect fills **24 points** (presets 24/32/35, more can be added) → refine: 58 presets, Bezier-spline face shaping, sculpt morphs, side-view refine → texture projected from the photo, "3D Lens Correction", **reprojection** of UVs after each shape change, de-light and redness tools, primary + secondary normal maps, hair from the image, body matched to the head. Mesh: Auto Detect → Align Points → Head Gen (effective area) → refine brushes → Attach to Body; bake options; SubD 0–2. Needs 8 GB+ VRAM and 32 GB RAM (RESEARCH plan 02) | reallusion.com photo-to-3d-head (page read); manual Front-Head / Source-Photo pages (page read); 3d-head-from-mesh (snippet) |
| ↳ user reports on Headshot 3 | Shape is the weak part: "consistently lower quality in recognizing and recreating facial and head shapes"; side refine gives "an “Alien-like” distorted head"; skin "too rough". Workaround: generate a bust in an image-to-3D tool (Tripo), then use Headshot's **Mesh-mode wrap**. Staff: the top forehead point belongs at the hairline | forum "Honest breakdown of Headshot 3" (page read) |
| **MetaHuman, From Mesh** (Epic, free under the UE EULA) | textured head mesh → MetaHuman | mesh needs a texture and visible sclera → camera FOV "20 degrees or less" (nearly flat projection) → promote a frontal frame (more frames only for missing markers) → "Track Markers" places curves along the facial features on that RENDER (editable, can auto-track) → **Identity Solve** "fits the Template Mesh vertices to the volume of the Neutral Pose Mesh" — "happens in the cloud" → Auto-Rig (DNA) → "Conform from Identity" in MetaHuman Creator (UE 5.6+). Tips: "Empty eye sockets are very likely to track poorly"; Unlit view for albedo-textured meshes | dev.epicgames.com …/metahuman/from-mesh (page read) |
| **MetaHuman, From Footage** | iPhone TrueDepth or stereo video → identity | TrueDepth: promote neutral, left, right and teeth frames; stereo: neutral + teeth → track → cloud Identity Solve → auto-rig. Uses **depth**, not one plain photo | …/metahuman/from-video-footage (page read) |
| **KeenTools FaceBuilder** (Blender / Nuke; subscription $15.99/mo–$699/yr) | several photos (any expression) → head with 51 ARKit shapes, LODs, export to CC4 and MetaHuman UVs | AI auto-align places a camera per photo and pins (red dots) → user drags pins → a shape model deforms under a "rigidity" setting (0 flexible … 10 rigid, default 1) → "Create Texture" blends the pinned views and bakes to a chosen UV layout. Photos are only references: "FaceBuilder uses camera settings and pin positions to change the shape". A cloud API takes 3–7 photos | keentools.io product page (page read); KeenTools guide and FAQ (snippet); cloud.keentools.io (snippet) |
| **R3DS / Faceform Wrap** (paid) | scan → clean base topology, texture transfer | node graph: SelectPointPairs (matching points on scan and base) → rigid alignment → **Wrapping** (non-rigid fit guided by the pairs) → **OpticalFlowWrapping** (refines the match from the textures; for neutral meshes and extreme expressions) → texture transfer or projection; Wrap4D for sequences | versluis.com tutorial, russian3dscanner tutorials index, toolfarm release notes (snippet; the docs site refused connection) |
| **Daz Face Transfer 2** | one photo → Genesis 9 (or 8) face shape + texture | AI transfer of shape and texture; higher-res maps; automatic facial-hair removal. Method undocumented | docs.daz3d.com, daz3d.com (snippet) |
| **FaceGen PhotoFit** (Singular Inversions) | 1–3 photos → statistical head | PCA "face space" from **273 scans**; 130 values in standard deviations (50 symmetric shape, 30 asymmetry, 50 colour). Markers "only approximate … a starting point" → fits the face model → whatever the model can't explain is saved as a **detail texture** (wrinkles, pores). "We have not published a paper" | facegen.com SDK manual and FAQ (snippet) |
| **Avatar SDK** (itSeez3D) | selfie → ~12k-vertex head with eyes, mouth, teeth; cloud or offline SDK | "deep learning" predicts geometry and texture (vendor wording) | 80.lv, gamedev.net (snippet) |
| **Avaturn** (in3D) · **Didimo** | selfies → avatar on a base model | AI onto a fixed base ("adapts a base model", Didimo); no technical docs found | aggregators, GamesBeat (snippet) |
| **Image-to-3D generators** (Tripo, Hyper3D Rodin / ChatAvatar, Meshy; open: TRELLIS.2, Hunyuan3D) | any image → a free-form mesh, no fixed topology | needs a wrap step (Headshot Mesh mode, Mesh-to-MetaHuman, Wrap) to become a riggable head. Likeness evidence is anecdotal (Tripo beat Headshot 3 on shape for one forum user) | vendor pages (snippet); forum (page read); RESEARCH §7 for the open ones |
| **Polywink** | not photo input: makes 161 blendshapes / rigs for a head mesh you already have | service on an uploaded OBJ/FBX | cgchannel, 80.lv (snippet) |

**The common pipeline the pros share** (synthesis of the rows above, inferred):
1. Clean the photo: neutral expression, even light, straight head, often with AI help.
2. Find landmarks and a camera (focal + pose).
3. Fit a statistical model, or a template mesh to a 3D surface, with user-editable pins or curves.
4. Project the texture from the photos, blended by view angle, then de-light; re-project after any shape edit.
5. The rig comes free because the topology is fixed.

MetaHuman and Headshot's Mesh mode both turn the hard problem (a photo) into an easier one (a 3D surface) first, then
fit the template to that **surface**, not to sparse 2D points.

---

## 5 · Landmark fitting that doesn't blow up: best practice (part 4)

1. **Solve everything at once**: camera focal length, head pose, expression and identity; GNM's own fit does
   (page read). Go in stages: pose and focal from stable inner points first, then identity on the first k sliders,
   then all of them. GNM's `num_components` supports this. RealDenseFace runs registration before tracking (config).
2. **Trust inner-face points, not the outline**: eye corners, nose base, mouth corners, brows. Drop jaw and face-oval
   points or re-match them to the silhouette each iteration (§1.3; Pixel3DMM README). Use GNM's shipped
   `head_sparse_68` barycentrics, or a once-built MediaPipe→GNM map (§3), never a per-view ray-cast vote.
3. **Weight each point by how reliable it is.** Microsoft's dense-landmark method predicts an uncertainty per point
   (from memory, ECCV 2022, project page not re-read). Use a robust loss such as Huber so a few bad points can't pull
   the face (standard practice, inferred).
4. **A prior that holds:** an L2 penalty on sliders in standard-deviation units (GNM), damping on the solver
   (RealDenseFace: 0.001, pose 0.1). Balance it against the number of data terms, or the data drowns it (§1.4). Cap
   |c| at about 3 sd as a hard guard (inferred).
5. **Add dense terms**: per-pixel UV correspondence (RealDenseFace, Pixel3DMM), normals (Pixel3DMM; DAViD as the open
   source), silhouette (Pixel3DMM `sil_super`), relative depth (RealDenseFace). They pin down the depth that sparse
   points leave free.
6. **Several photos: one identity shared, each photo with its own pose, expression and lighting** (Pixel3DMM
   `is_discontinuous`, RealDenseFace offline mode). Give AI-made views low weight (§2.4).
7. **Guards:** penalise skin passing through the eyeballs or mouth cavity (GNM). Set absolute scale from a known
   measure (§2.6).
8. **Check on views the fit didn't use**, plus a Chamfer number against a known head. NeRSemble aligns with
   Kabsch–Umeyama on 7 landmarks before measuring (snippet).

---

## 6 · Ranked routes for JustStage

1. **RealDenseFace dense matches → our own GNM solve (best, bucket b).** Run its network on the real photo (plus
   optional consistent AI side views, §2.4) → dense UV + depth → map FLAME-UV → GNM surface (§3) → our NumPy
   Gauss–Newton over camera, pose, expression and identity with §5's prior → hm08 targets → our existing texture
   projection.
   *Simpler first step:* use RealDenseFace's own FLAME fit, then the FLAME→GNM map, then GNM's ridge projection (§3).
   - *Attack:* the weights are MIT-labelled, but the training data includes Ava-256 (CC BY-NC) and other NC scan sets.
     It's shown and labelled, not filtered (the user's rule). The solver is CUDA-only, so we rewrite it (we have a
     Gauss–Newton already). The ONNX export is untested. It needs a FLAME file whose exact version is unverified.
     Still the best measured shape with weights out (1.610 mm).
   - *What the attack changed:* views made by AI get low weight, and the real photo drives the shape.
2. **Fix our own fitter, training-free (a + b):** everything in §5, with MediaPipe on the eyes and mouth plus DAViD
   normals and matte for the normal and silhouette terms. Weaker than route 1 with no UV term (inferred), but needs
   no new weights beyond MIT and Apache ones.
3. **Mesh, then wrap (the Mesh-mode / Mesh-to-MetaHuman pattern):** few-view mesh (Skullptor's idea on DAViD
   normals, or TRELLIS.2 via trellis.cpp) → render → landmarks → GNM fitted to the 3D surface with a prior → hm08.
   Most like the pros, and the most steps.
4. Feed-forward avatars (MeshLAM and the others) don't land on our topology. MeshLAM, the one with mesh + UV output,
   is unreleased. Watch it, don't build on it.

---

## 7 · Searches run (19 web searches; standard mode)

| # | Query | What it returned |
|---|---|---|
| 1 | best way to make a 3D head from a photo 2026 | Headshot photo guides, Trellis2 web tool, PanoHead listing, photogrammetry guides |
| 2 | new photo to 3D face model tools | FaceTo3D, Facial Studio (Di-o-matic), Novita "Face Transfer 2" blog — marketing |
| 3 | single image 3D face reconstruction state of the art 2026 github | FaceLift, Deep3DFaceReconstruction, NoW benchmark; no ranking |
| 4 | MeshLAM feed-forward one-shot animatable textured mesh avatar code release | arXiv 2604.22865, CVPR 2026 poster; no code found |
| 5 | CVPR 2026 monocular 3D face shape reconstruction FLAME NoW benchmark new method | **RealDenseFace**, NeRSemble SVFR board, Skullptor |
| 6 | dense facial landmarks 3D face fitting open source detector 2025 | Microsoft DenseLandmarks (ECCV 2022); no release confirmed |
| 7 | Headshot 3 manual Image Mode generate head Mesh Mode alignment points wrap bake texture (Reallusion domains) | Headshot pages, forum breakdown thread, magazine guides |
| 8 | MetaHuman Creator Unreal 5.7 conform from mesh identity solve tracking markers template mesh texture from images documentation | From Mesh doc, 5.7 notes, Python `MetaHumanIdentityFace` |
| 9 | KeenTools FaceBuilder for Blender documentation pin mode auto align rigidity texture bake from photos | KeenTools guide (403 on fetch), product page, rigidity and texture facts |
| 10 | Faceform R3DS Wrap documentation Wrapping node SelectPointPairs OpticalFlowWrapping texture projection | tutorials and release notes; official docs not found |
| 11 | Daz Face Transfer 2 how it works photo to Genesis 9 head texture | Daz docs and product pages; no method |
| 12 | Avaturn Didimo in3D photo to 3D avatar head how it works technology | aggregator and press summaries only |
| 13 | Polywink photo to 3D head service how it works blendshapes FACS | not photo-based; 161 blendshapes service |
| 14 | Avatar SDK itSeez3D FaceGen photo to 3D head how it works morphable model | Avatar SDK: deep learning, ~12k verts |
| 15 | Hyper3D Rodin Meshy Tripo realistic human head from photo likeness character mode | vendor pages, ChatAvatar; forum anecdote |
| 16 | FaceGen Modeller PhotoFit how it works statistical face model photos | FaceGen manual: 273-scan PCA, detail texture |
| 17 | LoRA training minimum VRAM 8GB FLUX.2 klein ai-toolkit OneTrainer musubi-tuner | BFL doc: 12 GB minimum for klein 4B |
| 18 | latest photo to 3D head avatar method 2026 high fidelity mesh texture | FiCA (Meta, 2026), KeenTools cloud API, ROME |
| 19 | MICA metrical face shape from ArcFace identity embedding how it works NoW metrical error | MICA design and NoW claims |

Non-search lookups (no search cost): GitHub API and READMEs/LICENSEs for DECA, EMOCA, SMIRK, MICA, Pixel3DMM, LAM,
GAGAvatar, FaceLift, CAP4D, RealDenseFace, Skullptor, DAViD, GNM, MediaPipe, Arc2Avatar, Arc2Face, Ava-256 and
stable-diffusion.cpp; the Hugging Face API for LAM-20K, RealDenseFace, DINOv3, Qwen-Image-Edit 2509/2511 and the
multi-angle LoRAs. WebFetch pages: the GNM report (arXiv 2607.23687 HTML), the MeshLAM abstract and alphaxiv summary,
meshlam.github.io, the RealDenseFace and Pixel3DMM abstracts, the NeRSemble SVFR board, the DINOv3 and FLAME licence
pages, the Headshot manual and product page, the Headshot forum thread, MetaHuman From Mesh and From Footage, the
KeenTools product page, BFL's klein training doc, and the FiCA abstract.

---

## 8 · Couldn't verify

- Whether RealDenseFace's `flame2023.pkl` is **FLAME 2023 Open** (CC-BY-4.0) or the academic FLAME 2023, and whether
  the two share the same UV layout and shape space.
- RealDenseFace on this machine: VRAM, speed, ONNX export; its NPHM and FaceScape terms (not read this session).
- The FLAME↔GNM surface map: Google's isn't released; ours is not built or measured.
- PartFusion / PartFusionMI, FlowFace and SHeaP: no papers or code found; the Skullptor normals score shows "inf".
- LAM's training-data terms (VFHQ, NeRSemble); GAGAvatar's and SMIRK's weight licences (unstated).
- Arc2Face's dependency on InsightFace's ArcFace weights (non-commercial in RESEARCH's earlier notes): not re-read.
- MeshLAM: whether code and weights will ever come out (only the LAM repo is linked).
- MetaHuman's texture handling on From Mesh, and any 5.7/5.8 photo-based identity (the release-notes page came back
  empty).
- R3DS/Faceform Wrap's official docs (connection refused) and KeenTools docs (certificate error; not bypassed). Their
  steps are from tutorials and snippets.
- Whether stable-diffusion.cpp runs Qwen-Image-Edit **2511** (its README names 2509), and whether the multi-angle
  LoRAs load in it.
- An 8 GB LoRA path for FLUX.2 klein: BFL documents 12 GB minimum; no trainer documents 8 GB.
- Headshot 3's Image-mode method (Reallusion doesn't say) and the methods behind Daz Face Transfer 2, Avaturn, Didimo
  and Avatar SDK (marketing only).
- From memory, not re-read: Microsoft dense landmarks' per-point uncertainty; outline-landmark re-matching
  ("landmark marching"); MediaPipe's constant-iris-size assumption.
