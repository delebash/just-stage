# Research — latest techniques and tools for every JustStage function (2026-10-30)

One survey round over the seven JustStage functions plus Blender 5.0–5.3. It reports what is **new or changed** against
`docs/dev/RESEARCH.md` §5 and §7 (2026-10-29). Options are **ranked by quality and capability first**; licence, VRAM and
platform are labels beside each option, never filters (the user, 2026-10-30).

**How facts are marked**

- **[API]** — GitHub or Hugging Face API, read this session (stars, dates, `license` fields).
- **[page]** — a README, model card, release note or vendor page read this session.
- **[paper]** — the paper's abstract, read through the Hugging Face papers API this session.
- **[snippet]** — a web-search summary only; not opened.
- **[prior]** — carried from RESEARCH.md §5/§7 (2026-10-29), not re-checked.
- **[known]** — a published classic method named from general knowledge; its link was not re-read this round.

**Training buckets** (the user, 2026-10-30: no full training; a small LoRA on an open base or a tiny special-purpose model is
allowed)

- **(a)** needs no trained model.
- **(b)** runs on open weights that already exist (named, with their licence).
- **(c1)** a small LoRA on an open base, or a tiny special-purpose model, would do it on 8 GB.
- **(c2)** needs real training we can't do. Each (c2) item says what a training-free way to do the same job is.

**LoRA facts used for (c1)** (all [page]):

- Unsloth's requirements page gives QLoRA (4-bit) minimums of 3.5 GB for a 3B model, 5 GB for 7B, 6 GB for 8B, 7.5 GB for
  11B and 8.5 GB for 14B. It names NVIDIA "minimum CUDA Capability of 7.0 … RTX 20" as supported, and AMD and Intel as
  supported for training ([unsloth requirements](https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements)).
  So a VLM or LLM up to about 11B fits the RTX 2070 Super (8 GB) for QLoRA.
- SimpleTuner's quickstarts give image-model LoRA memory:
  - FLUX.2 klein-4B: "~12GB" in bf16 and "~8GB" in int8, with "32GB+" system RAM. 8 GB is borderline.
  - Z-Image: "~10–12G VRAM when quantising to NF4". That does not fit 8 GB.
  - Qwen-Image: "A 24GB GPU is the absolute minimum".
  - Sources: [FLUX2.md](https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/FLUX2.md),
    [ZIMAGE.md](https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/ZIMAGE.md),
    [QWEN_IMAGE.md](https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/QWEN_IMAGE.md).
- ai-toolkit's FLUX example config is named `train_lora_flux_24gb.yaml`
  ([README](https://github.com/ostris/ai-toolkit)).
- No common trainer (kohya_ss, OneTrainer, ai-toolkit, SimpleTuner, Unsloth) documents LoRA for 3D, rigging or motion
  models. For those, (c1) means "a tiny model trained from scratch", with no documented VRAM.

## Top findings (new since 2026-10-29)

1. **NVIDIA's SOMA motion stack now ships commercial-use weights, and all of it has CPU/Vulkan GGML ports.** It is built on
   SOMA, the body layer already in §5. RESEARCH §7 lists GENMO/GEM as non-commercial; GEM-X is a newer NVIDIA release under
   a commercial-use model licence.
   - **GEM-X** (NVlabs, 2026-10-21) does body, hands and world-space motion from video. Its code is Apache-2.0 with
     per-file exceptions, and its weights `nvidia/GEM-X` are under the NVIDIA Open Model License [API][page].
   - **Kimodo** (2026-03 to 2026-10) does text and keyframe constraints to motion. It is a 282M-parameter diffusion model
     trained on 700 h of optical mocap. The `Kimodo-SOMA-RP-v1.2` card says "This model is ready for commercial use"
     [page]. It needs "<3 GB" of VRAM with the text encoder on the CPU [page].
   - **MotionBricks** (SIGGRAPH 2026) does real-time motion from keyframes [page].
   - **SOMA Retargeter** (Apache-2.0) retargets SOMA motion [API].
   - The GGML ports by `localai-org`, all Apache-2.0 [API]: `kimodo.cpp` (942 stars), `gem-x.cpp`, `motion-bricks.cpp`.
2. **Text-to-motion for any skeleton arrived.**
   - **UniMate** (SIGGRAPH Asia 2026) is a 74M-parameter model covering animals, humanoids and rigged objects. Its code is
     MIT; its weights are CC-BY-NC-4.0 [API][page].
   - **TopX** (2026-10-25) is a 73M model that generates motion from the skeleton file alone; no code yet [paper].
   - **MoCapAnything V2** (SIGGRAPH Asia 2026) does video mocap onto arbitrary skeletons. Its HF weights are labelled MIT;
     the code repo says NOASSERTION [API][page].
3. **Rigging:** nothing beats SkinTokens/TokenRig among released models. What is new:
   - joint shape-plus-rig generators (Rigel3D, AniGen, Stroke3D) — papers, no code except Stroke3D;
   - an 82,633-mesh "animator-centric" skeleton dataset paper;
   - **Armature**, a free (under $100k revenue) AI-plus-geodesic-voxel rigging app that exports UsdSkel [page].
4. **Clothing:** **NGL-Prompter** (2026-02) is *training-free* sewing-pattern estimation from one image. A vision-language
   model describes the garment in a "Natural Garment Language" that maps onto GarmentCode [paper]. It is the first
   image-to-pattern route that needs no fine-tune. Its code was not found.
5. **Image-to-3D:**
   - **Pixal3D** (SIGGRAPH 2026, MIT, 2,549 stars) adds pixel-aligned generation on the TRELLIS.2 line [API][paper].
   - **SUPRA-Tex** (2026-10, MIT) does relightable PBR texturing from one reference image [API][paper].
   - **Meshy T2** (2026-07) generates native artist-topology meshes; its repo has no licence file [API][paper].
   - **Hunyuan3D 3.0/3.1** appear to be API-only; no open weights were found [snippet].
6. **Blender 5.3** (beta until 2026-11-04) has three relevant additions [page]:
   - EEVEE **Material Lighting nodes** (Light Accumulation, Shadow Raycast, …);
   - **3D Gaussian Splats** as a point-cloud type, with PLY/SPZ import, rendered in all engines;
   - Vulkan as the default back-end on Windows and Linux.

   Blender 5.2's **experimental XPBD Cloth and Hair Dynamics** (geometry-nodes assets) are confirmed in its physics notes
   [page].

---

## Search log

**WebSearch queries** (21 of the 30 allowed, all "standard"):

| # | Query | What it returned |
|---|---|---|
| 1 | latest AI auto rigging tools 2026 | Vendor listicles (Tripo ranks itself first); found **Armature** (cgchannel 2026-08), AccuRIG, AutoRig.online, Sorceress. |
| 2 | new techniques for 3D clothing from images 2026 | GarmentCrafter (CMU 2026-02 news), SyntheCloth-300K paper, pattern-coordinate reconstruction (SIGGRAPH 2025), Garment3DGen. |
| 3 | best open source image to 3D model generator 2026 | Blogs: TRELLIS.2 "quality leader", Hunyuan3D region limits, TripoSR, SPAR3D (<$1M revenue clause), SAM 3D. |
| 4 | best AI motion capture from video open source 2026 | Roundups: OpenPose, MediaPipe, FreeMoCap, "Open Mocap"; Rokoko Video. No research models. |
| 5 | best text to motion AI model 2026 | Only text-to-*video* roundups (Runway, Veo, Kling); useless for skeletal motion. |
| 6 | AI generate ARKit 52 blendshapes for any 3D head automatically | ARKitBlendshapeHelper (transfer of hand-sculpted shapes), Shape Key Gen (paid), KeenTools FaceBuilder claim; no true AI generator. |
| 7 | new parametric human body model 2026 open source | Anny, GNM, MHR, SOMA — all already in §5. |
| 8 | Hunyuan3D 3.0 open source weights release | 3.0 announced via Tencent Cloud API; last confirmed open release is 2.1. |
| 9 | MetaHuman 2026 update DNA RigLogic Blender export new features | MetaHuman 5.7 notes (Linux/macOS Creator, Python API); a 5.8 preview; a Spanish headline that Creator is discontinued in Nov 2026. |
| 10 | AI garment generation Marvelous Designer CLO Style3D AI features 2026 | Style3D AI (text/sketch/image to garment, GarmageNet), MD 2025.1 AI Pose Generator; nothing for CLO in 2026. |
| 11 | how AccuRIG Mixamo Meshy Tripo auto-rigging works joint markers skin weights comparison | Vendor blogs only; no internals; Mixamo humanoid-only, T/A pose. |
| 12 | Move AI Rokoko Vision Plask DeepMotion Radical markerless video motion capture how it works 2026 | Move AI single/multi-camera markerless; Rokoko Vision free webcam; DeepMotion AI and physics; nothing on Radical. |
| 13 | Audio2Face 3.0 AccuLips Faceware MetaHuman Animator how lip sync facial animation works | AccuLips internals (vendor page); Audio2Face general; nothing on Faceware or MetaHuman Animator. |
| 14 | Polywink Faceit automatic 52 ARKit blendshapes any head how it works | Polywink: 51 ARKit shapes from any static head, 24 h, $299 (2018 sources). |
| 15 | Cascadeur AutoPosing AutoPhysics neural network how it works 2026 update | Cascadeur 2026.1 (point constraints, quadruped AutoPosing) and 2026.2 (animation layers); no internals. |
| 16 | Meshy Tripo Rodin Hunyuan 3.0 image to 3D quality comparison 2026 topology PBR | A blind test (HackerNoon, Apr–May 2026): Tripo v3.1 > Rodin Gen-2.5 > Meshy 6 on geometry; Meshy best textured. |
| 17 | best open source webcam face capture ARKit blendshapes 2026 MediaPipe alternative | MediaPipe-based tools dominate; OpenSeeFace; mocap4face (free, not open); an ONNX export of MediaPipe's blendshape model. |
| 18 | wrinkle maps driven by blendshape weights shader Blender EEVEE MetaHuman animated wrinkle masks how | Unity *Blacksmith* wrinkle-map write-up; Blender Studio "procedural wrinkles" from tension. |
| 19 | best AI lip sync and facial animation for 3D characters 2026 | Listicles; consistent point: 3D needs blendshape-output tools (Audio2Face, AccuLips). |
| 20 | best cloth simulation for 3D characters 2026 open source | Blender only open option named; Marvelous Designer and Houdini lead commercial lists. |
| 21 | AI motion retargeting any skeleton tool 2026 | Uthana (bipeds, IK, under a second); Aberman et al. 2020 skeleton-aware networks. |

**Free API queries** (no search budget): Hugging Face papers search (`/api/papers/search?q=`). It was run for:

- rigging: auto rigging, skinning weights, skeleton generation 3D, rigging 3D characters, animatable 3D asset generation,
  rig motion generation arbitrary skeleton;
- face: blendshape generation, facial rig, face rigging, ARKit blendshapes, facial expression transfer mesh, wrinkle maps,
  3D face animation speech, facial performance capture monocular, face tracking blendshapes video;
- garments: sewing pattern generation, garment generation 3D, garment reconstruction single image, simulation-ready
  garment, cloth simulation GPU, garment draping, garment retargeting body;
- motion: world-grounded human motion video, human mesh recovery video, markerless motion capture monocular, text-to-motion
  generation, human motion generation diffusion, motion retargeting, hand pose estimation video 3D;
- image-to-3D: image-to-3D generation, 3D shape generation high resolution, textured mesh generation, part-aware 3D
  generation, PBR texture generation 3D mesh, native 3D generation sparse voxel, 3D generation open-source foundation
  model;
- named papers: GarmentCrafter, Design2GarmentCode, Garment3DGen, AIpparel, ChatGarment, GarmentDiffusion.

Each search was filtered to papers published from 2025-11 or 2026-01 on. 39 abstracts were read through
`/api/papers/<id>`.

Other free sources:

- GitHub API: about 70 repos, `search/repositories`, and the `localai-org` org listing.
- Hugging Face model API: 23 searches, and the model cards for Kimodo, UniMate, MoCapAnything V2 and the Kimodo GGML port.
- The Blender developer docs release notes, 5.0–5.3 (55 pages, raw markdown).
- arXiv's API answered once, then returned "Rate exceeded" (HTTP 429) on every retry. The Hugging Face papers index was
  used instead (see "Couldn't verify").

---

## 1 · Body shape and morph models

Nothing new at the model level since §5. What changed is that **SOMA became the skeleton of NVIDIA's whole motion stack**
(§5 of this file). That gives an MHR/Anny body a direct path to commercial-use mocap and text-to-motion.

| Rank | Tool | What | Licence code / weights | VRAM | No-CUDA path | Last update | New? | Bucket |
|---|---|---|---|---|---|---|---|---|
| 1 | **MHR** (Meta) | Scan-trained body: 7 LODs, 127 joints, 72 FACS expressions, neural pose correctives [prior] | Apache-2.0 / Apache-2.0 [API] | small [prior] | PyTorch CPU; Momentum C++ [prior] | push 2026-10-26, release v1.0.1 2025-11-19 [API] | no | b |
| 2 | **Anny** (NAVER) | MakeHuman-based body, infant to elder, WHO-calibrated phenotypes, ARKit-named face units [prior][paper] | Apache-2.0 code; CC0 data; SMPL-X topology non-commercial [prior] (API: NOASSERTION — mixed files) | small | PyTorch CPU | push 2026-10-26 [API] | no | a (artist blendshapes, no learned weights) |
| 3 | **SOMA-X** (NVIDIA) | One canonical mesh and a 77-joint rig over MHR, Anny, SMPL; closed-form skeleton fit [prior][paper] | Apache-2.0 [API] | small; Warp fast path NVIDIA-only [prior] | PyTorch CPU 12.1 ms/mesh [prior] | release v0.3.4 2026-10-09 [API] | changed: now the skeleton of GEM-X, Kimodo, MotionBricks [page] | a |
| 4 | **GNM Head** (Google) | Scan-based head with eyes, teeth, tongue; 253 identity and 383 expression parameters [prior] | Apache-2.0 / Apache-2.0 [prior][API] | small | NumPy | push 2026-10-29 [API] | no (body still roadmap [snippet]) | b |
| 5 | **MPFB2 / MakeHuman** | 1,258 targets, 234 slider groups, rigs, CC0 assets [prior] | GPLv3 code, CC0 assets [prior] | — | Blender | release v2.0.18 2026-10-11 [API] | no | a |
| — | SMPL / SMPL-X / STAR / SUPR / FLAME≤2023 | Research bodies | non-commercial (commercial via Meshcapade) [prior] | small | yes | — | no | b (NC) |

**Technique notes (top 3).**

- **MHR** ([arXiv 2511.15586](https://arxiv.org/abs/2511.15586)) [paper]: ATLAS's decoupled skeleton and shape (identity
  moves joints and surface separately), a Momentum-style rig, and non-linear pose correctives.
  - Steps: identity PCA, then joint regression from identity, then LBS, then neural correctives per joint group.
  - Needs trained weights: yes (shape space and correctives); open weights exist: Apache-2.0 model files.
- **Anny** ([arXiv 2511.03589](https://arxiv.org/abs/2511.03589)) [paper]: interpretable phenotype sliders (gender, age,
  height, weight …) blend MakeHuman's artist-made targets, calibrated against WHO population statistics.
  - Steps: macro-target interpolation (MakeHuman's own scheme), then skeleton refit from joint helpers, then LBS.
  - Needs trained weights: no; the data is MakeHuman's CC0 targets.
- **SOMA** ([arXiv 2603.16858](https://arxiv.org/abs/2603.16858)) [paper]: maps each source model onto a shared canonical
  mesh "in constant time per vertex".
  - It recovers identity-adapted joints "in a single closed-form pass, with no iterative optimization or per-model
    training".
  - Its pose layer inverts skinning to move poses between models.
  - Needs trained weights: no.

**Apps that do this and how they work.** CC5 and MetaHuman are in RESEARCH §2/§5 [prior]. MetaHuman 5.7 (Dec 2025) added
these, per the official release notes title and search summary [snippet]:

- Linux and macOS support for Creator;
- "pose agnostic body conform from template mesh";
- Python and Blueprint APIs.

---

## 2 · Auto-rigging and skinning

Ranked by quality (paper claims; no independent benchmark across all of them was found).

| Rank | Tool | What | Licence code / weights | VRAM | No-CUDA path | Last update | New? | Bucket |
|---|---|---|---|---|---|---|---|---|
| 1 | **SkinTokens / TokenRig** (VAST) | One autoregressive model for skeleton *and* skin weights; skin as learned discrete tokens; RL fine-tune [paper] | MIT / MIT (`VAST-AI/SkinTokens`) [API] | 14 GB CUDA [prior] | **skin-tokens.cpp** (GGML, CPU/Vulkan); MLX and GGUF re-hosts [API] | push 2026-05-12; .cpp 2026-10-19 [API] | no (but more ports: `mlx-community/SkinTokens-bf16`, several GGUF) | b |
| 2 | **UniRig** (VAST) | Autoregressive skeleton tokens, then skin and bone attributes; diverse skeletons (SIGGRAPH 2025) | MIT / MIT [API] | ≥ 8 GB [prior] | skeleton stage via ONNX/WebGPU ports; skin stage CUDA [prior] | push 2026-06-04 [API] | no | b |
| 3 | **Puppeteer** (Seed3D) | Rig *and* animate (NeurIPS 2025 spotlight) | Apache-2.0 / Apache-2.0 [API] | rigging fits 8 GB [prior] | CUDA 11.8 [prior] | push 2025-09-19 [API] | no | b |
| 4 | **Armature** (FabricatorStudio) | Standalone app: fits biped, quadruped or prop templates or modular creature skeletons, auto skin weights, manual refine; USD (UsdSkel) export; keeps skinning when the source mesh changes [page] | closed; free personal and indie (< $100k/yr), $149 perpetual [page] | AI skinning needs NVIDIA [page] | **geodesic voxel binding engine "runs on any system"** [page] | v2.1.3 at 2026-08-06 [page] | **yes** | (app) |
| 5 | **Rigel3D** (2026-05) / **AniGen** (2026-04) | Generate shape, skeleton and skinning *together* from an image (coupled latents / "S³ fields") [paper] | no code found | — | — | papers | **yes** | c2 |
| 6 | **Animator-centric skeleton generation** (2026-04) | Semantic bone-group tokenisation for complex models; 82,633-mesh dataset; control handles [paper] | no code found | — | — | paper | **yes** | c2 |
| 7 | MagicArticulate / RigAnything / Make-It-Animatable / HumanRig | Earlier learned riggers | Apache / NOASSERTION / MIT (Mixamo-trained) / MIT [API][prior] | various | CUDA | 2025-09 → 2026-09 [API] | no | b |
| 8 | **Make-It-Poseable** (SIGGRAPH Asia 2026) | Poses a character by editing its *latent* (no skin weights) [paper] | MIT code [API]; weights not checked | not stated | not stated | push 2026-09-02 [API] | **yes** | b? |
| 9 | **Stroke3D** (ICLR 2026) | 2D strokes to a rigged 3D model via latent diffusion [paper] | repo, no licence [API] | — | — | push 2026-09-04 [API] | **yes** | b? |

**Technique notes.**

- **TokenRig** ([arXiv 2602.04805](https://arxiv.org/abs/2602.04805)) [paper]:
  1. An FSQ-CVAE compresses each vertex's sparse skin-weight vector into a few discrete tokens.
  2. A transformer on mesh features emits one sequence: bones (parent, joint positions), then skin tokens.
  3. Decode the tokens back to weights.
  4. An RL step (reward on deformation quality) refines the result.

  Needs trained weights: yes; open weights exist: `VAST-AI/SkinTokens`, MIT.
- **Rigel3D / AniGen** ([2605.13129](https://arxiv.org/abs/2605.13129), [2604.08746](https://arxiv.org/abs/2604.08746))
  [paper]: generate the asset already rigged, avoiding a post-hoc rigger that misreads the shape. Bucket c2.
  - Training-free way to the same end: generate the mesh (§6), then rig it with SkinTokens (b) or the classic pipeline
    below (a).
- **Deep Feature Deformation Weights** ([2601.12527](https://arxiv.org/abs/2601.12527)) [paper]: distil a pretrained
  vision backbone's features onto the surface; weights come from feature proximity to handles, in real time, with automatic
  symmetry. Bucket b (a pretrained 2D backbone) — no code found.

**Training-free rigging (bucket a), the standard pipeline** [known]:

1. **Skeleton embedding** — Pinocchio (Baran & Popović, "Automatic Rigging and Animation of 3D Characters", SIGGRAPH 2007).
   It fits a template skeleton to the mesh's medial surface.
   - For humans, JustStage can skip this: fit the MakeHuman/MPFB2 base by wrap (non-rigid ICP) and keep its joints, which
     its joint-cube helpers place (§5) [prior].
2. **Skin weights.** Three options:
   - Blender's built-in "Automatic Weights" (bone heat, from the same paper);
   - **geodesic voxel binding** (Dionne & de Lasa, SCA 2013 — Maya's default; Armature's non-AI engine);
   - **bounded biharmonic weights** (Jacobson et al., SIGGRAPH 2011; libigl).
3. **Weight transfer** from a rigged template: "Robust Skin Weights Transfer via Weight Inpainting" (Abdrashitov et al.,
   SIGGRAPH Asia 2023). It copies weights where surfaces match closely and inpaints the rest.

**Apps that do this and how they work.**

- **AccuRIG** (Reallusion): free desktop tool; "identifies body parts, hands, and fingers with AI", feeds CC and ActorCore
  [snippet]. Its page could not be fetched (404).
- **Mixamo** (Adobe): free web service; humanoid bipeds only, expects a T or A pose [snippet]. The user places markers (chin,
  wrists, elbows, knees, groin) [known].
- **Meshy / Tripo**: rig their own generated models after generation; auto skeleton plus AI weights plus preset motions, FBX
  out [snippet, vendor blogs].
- **Armature**: see the table [page].
- **Cascadeur Quick Rigging**: it exists (the help index lists "Quick Rigging Tool"); the page content was not readable
  [page].
- **Mesh2Motion**: template skeletons per creature type (birds, dragons, spiders, horses …) placed on the mesh, then a
  motion library; MIT/CC0 [prior].
- **Rigify**: fit a metarig, then generate controls; GPL; human, quadruped and animal metarigs [prior].
- **Auto-Rig Pro**: paid; the user clicks reference points, the rig is generated [known]. Out as paid [prior].

---

## 3 · Facial expressions: ARKit-52 / FACS for any head, wrinkle maps, MetaHuman DNA

No released model turns an *arbitrary* head into a full ARKit-52 set in one step with commercial weights. Every search
agreed (search 6 [snippet], HF papers). The strongest route is template transfer (a).

| Rank | Tool / method | What | Licence code / weights | VRAM | No-CUDA path | Last update | New? | Bucket |
|---|---|---|---|---|---|---|---|---|
| 1 | **Deformation transfer from a CC0/MIT ARKit template** (Sumner & Popović, SIGGRAPH 2004) | Register a template that already has the 52 shapes (MPFB2 *Faceunits 01*, CC0; ICT-FaceKit, MIT) onto the new head, then transfer each shape's per-triangle deformation | method; template data CC0 / MIT [prior] | CPU | CPU (sparse solve) | — | method new to the docs | **a** |
| 2 | **NFR — Neural Face Rigging** (SIGGRAPH 2023) | Learns FACS-like codes that drive *any* face mesh, "even with different topology, without any labor for manual rigging" [page] | MIT code [API]; weights on Google Drive, licence unstated; trained on ICT-FaceKit and Multiface [page] | not stated | PyTorch | push 2026-08-03 [API] | **yes** | b (weights' terms unclear) |
| 3 | **RegHead** (2026-07) | Semantic blendshape sets for *non-humanoid* heads: a dataset grown from a small artist library by fine-tuned image editing, then feed-forward registration [paper] | no code found | — | — | paper | **yes** | c2 — training-free way: #1 with a creature template |
| 4 | **Example-based facial rigging** (Li, Weise & Pauly, SIGGRAPH 2010) | Given a few sculpted or scanned expressions of the target, optimise a full personalised blendshape set from a generic template | method [known] | CPU | CPU | — | method | **a** |
| 5 | **EmoteGPT** (2026-07) | Text to 3DMM expression parameters through an MLLM expression token [paper] | no code found | — | — | paper | **yes** | c2 — training-free way: an LLM picks ARKit weights from a prompt via the expression JSON format MPFB2 already has [prior] |
| — | KeenTools FaceBuilder | Builds a head from photos; reported to generate ARKit-compatible blendshapes [snippet, unconfirmed] | commercial | — | — | — | yes | (app) |

**Technique, #1 (the recommended path)** [known]:

1. Wrap the template head onto the target with landmarks plus non-rigid ICP (Amberg et al., "Optimal Step Nonrigid ICP",
   CVPR 2007).
2. For each template shape, compute the per-triangle deformation gradients from neutral to the shape.
3. Solve one sparse least-squares problem per shape, so the target's triangles take the same gradients (a pre-factored
   Cholesky solve reused for all 52).
4. Mask, and clean the eyelids and lips by hand-tuned vertex groups.

Needs trained weights: no.

**Wrinkle maps** (bucket a). Two methods:

- **Per-blendshape wrinkle layers** (Unity's *The Blacksmith*, 2015): each shape gets a wrinkle normal and occlusion map;
  maps are blended by shape weight in a pre-pass; only the 4 strongest shapes per frame are used, because of sampler limits
  [snippet].
  - In Blender: drive mix factors from the shape-key values (drivers), mix the normal maps, feed the Principled BSDF.
- **Tension-driven wrinkles** (Blender Studio "procedural wrinkles", for *Charge*, EEVEE): compare the deformed mesh with
  its rest mesh, pass the difference as an attribute, then a bump mask [snippet].
  - Blender 5.2's Capture Rest Geometry and geometry bundles [page] make the rest-versus-deformed comparison a standard
    node setup.

**MetaHuman DNA / OpenRigLogic news.**

- `EpicGames/MetaHuman-DNA-Calibration`: last push 2025-06-20 [API] — no 2026 change.
- The Blender DNA add-on moved to `poly-hammer/character-dna-addon` (GPL-3.0, 309 stars, pushed 2026-10-30) [API].
- MetaHuman 5.7 release-notes highlights [snippet]; the 5.8 release notes page exists [page] but was not read.
- A news headline says Epic discontinues the standalone MetaHuman Creator *app* in Nov 2026 [snippet, headline only].

**Apps that do this and how they work.**

- **Polywink**: an upload service — any static head (OBJ/FBX, "no restrictions on topology or UV layout"), back in 24 h:
  "51 facial shapes" for ARKit plus a Unity project; $299 per model (2018 figures) [snippet].
- **Shape Key Gen** (Superhive, paid): generates the 52 ARKit shapes for a rigged character; marker refinement [snippet].
- **ARKitBlendshapeHelper** (free): you sculpt the 52 poses on frames; it bakes and renames them [snippet].
- **Faceit** (Blender, paid): landmark placement, then a generated face rig, then ARKit shape keys [known; not re-read].
- **AccuLips** (iClone), lip-sync [snippet, vendor page]:
  - detects text and visemes from audio, or takes a script;
  - 8 lip-dental shapes, 7 tongue positions and mouth width, about 240 phoneme combinations, blended over time curves;
  - a 200,000-word dictionary.
- **NVIDIA Audio2Face-3D**: audio to face animation on any mesh; streams blendshapes to Unreal. SDK MIT, NVIDIA Open Model
  License weights, ONNX [prior]. Repos last pushed 2025-09 [API].
- **MetaHuman Animator, Faceware**: nothing found this round.

---

## 4 · Clothing: image or text to garment, cloth simulation

The 2026 trend: **sewing patterns as the target** (simulation-ready), produced by a VLM. NGL-Prompter shows the VLM need
not be fine-tuned.

| Rank | Tool | What | Licence code / weights | VRAM | No-CUDA path | Last update | New? | Bucket |
|---|---|---|---|---|---|---|---|---|
| 1 | **NGL-Prompter** (2026-02) | Training-free image to sewing pattern: VLM writes "Natural Garment Language", mapped to GarmentCode; multi-layer outfits; "generalize[s] to in-the-wild images" better than fine-tuned VLMs [paper] | no code found | the VLM's own (a quantised 7–8B VLM in llama.cpp should fit 8 GB [known, not measured]) | any (llama.cpp VLM) | paper | **yes** | **b** (open VLM, e.g. Qwen-VL class, plus GarmentCode MIT) |
| 2 | **PatternGSL** (2026-06) | Template-free pattern spec language (panels, parameterised seams, stitch topology) plus a VLM [paper] | no code found | — | — | paper | **yes** | c1 (QLoRA of a ≤ 11B VLM fits 8 GB [page]) or a with prompting |
| 3 | **SwiftTailor** (2026-03) | Small VLM "PatternMaker" plus "GarmentSewer" that predicts a geometry image directly; fixes 30–60 s GarmentCode inference [paper] | no code found | — | — | paper | **yes** | c2 |
| 4 | **Garment Particles** (2026-05) | 5D point cloud (2D pattern plus 3D drape); rectified flow; edit either side [paper] | no code found | — | — | paper | **yes** | c2 |
| 5 | **ChatGarment** (CVPR 2025) | LLaVA fine-tune: image or text to GarmentCode JSON | Apache-2.0 code [API] | ≥ 15 GB [prior] | — | push 2025-08-07 [API] | no | b; c1 to re-tune (7B QLoRA ≈ 5 GB [page]) |
| 6 | **GarmentCrafter** (CMU, arXiv 2503.08678; CMU news 2026-02) | Single image to editable 3D garment via progressive depth, warping and multi-view diffusion [snippet][paper title] | no code found | — | — | — | **yes** | c2 — training-free way: §6 image-to-3D, then Garment3DGen-style template fit |
| 7 | **Spatio-temporal garment reconstruction via pattern coordinates** (2026-02; extends SIGGRAPH 2025) | Pixels to UV-pattern coordinates to 3D, for images *and video* [paper] | no code found | — | — | paper | **yes** | c2 |
| 8 | AIpparel / DressCode / GarmentDiffusion / Design2GarmentCode | Earlier pattern generators | MIT / none / — / — [prior] | — | — | 2024–2025 | no | b / c2 |
| 9 | **Garment3DGen** (Meta) | Deform a base garment template to match an image-to-3D result; simulation-ready | NOASSERTION [API] | — | — | push 2024-07-09 [API] | no | b? |
| — | **GarmentCode** | Parametric pattern programs (the target language for most of the above) | MIT [API] | CPU | CPU | push 2025-06-29 [API] | no | **a** |

**Technique, NGL-Prompter** ([arXiv 2602.20700](https://arxiv.org/abs/2602.20700)) [paper]:

1. Define NGL, a natural-language re-structuring of GarmentCode's parameters (garment parts, lengths, fits).
2. Prompt an off-the-shelf VLM to describe the photo in NGL.
3. Map NGL to GarmentCode parameters deterministically.
4. GarmentCode builds the panels, then a simulator drapes them on the body.

Needs trained weights: an existing VLM only. Open weights exist: any local VLM run by the kit's llama.cpp (§10 of
RESEARCH). The exact VLM the paper used was not read.

**Cloth simulation (training-free).**

| Tool | What | Licence | No-CUDA path | Last update | New? |
|---|---|---|---|---|---|
| **Blender 5.2 Cloth Dynamics** (experimental) | Geometry-nodes asset on a built-in **XPBD Solver** node: pinning, stretch and bend, tearing; colliders, custom forces, custom effectors (closures), tag filters [page] | GPL (Blender) | CPU (Blender) | 5.2 LTS, 2026-07-14 [page] | detail new (§6 only named "XPBD node physics") |
| **ZOZO contact solver (ppf)** | Offline, penetration-free, seam stitching; Blender add-on | Apache-2.0 [API] | CPU, Apple, AMD (untested) [prior] | add-on release 2026-10-19 [API] | updated |
| **Newton** (NVIDIA Warp-based) | GPU physics engine (cloth, soft bodies) | Apache-2.0 [API] | Warp CPU only (Warp GPU = CUDA) [known] | v1.7.0, 2026-10-14 [API] | not in §7 |
| **Jolt** | Soft bodies, Cosserat rods, GPU hair (work in progress) | MIT [API] | DX12, Vulkan, Metal, CPU [prior] | v5.6.0, 2026-07-11 [API] | no |
| HyperBones / UNIC / PhySkin (2026) | *Neural* real-time garment sim trained per garment [paper] | no code found | — | papers | yes — c2; training-free way: XPBD above, baked |

**Apps that do this and how they work.**

- **Marvelous Designer / CLO** (the same company): 2D pattern pieces sewn and draped by a physics solver.
  - CLO is the "industry standard for 3D garment simulation, pattern automation" [snippet].
  - MD 2025.1 added an "AI Pose Generator" and drawing garment parts onto the avatar [snippet].
- **Style3D**: AI text-, sketch- and image-to-garment that output patterns plus simulation [snippet]. GarmageNet research
  reports a "91.41% simulation-initialisation success rate on 150 complex patterns" [snippet]; Studio V9.3 (May 2026)
  [snippet].
- **Meshy / Tripo**: whole-character meshes with clothes fused in, not separate garments [snippet].

---

## 5 · Motion: video to motion, face capture, text to motion, retargeting

### 5a · Video to body motion

| Rank | Tool | What | Licence code / weights | VRAM | No-CUDA path | Last update | New? | Bucket |
|---|---|---|---|---|---|---|---|---|
| 1 | **GEM-X** (NVIDIA) | Body pose, hand pose and temporal body motion, camera- and world-space, from image or video, on SOMA; fine-tuning supported [page] | Apache-2.0 plus per-file OpenMDW-1.1 exceptions / weights `nvidia/GEM-X` NVIDIA Open Model License [API][page] | not stated | **gem-x.cpp** (GGML, Vulkan or CPU) [page] | 2026-10-22 [API] | **yes** | b |
| 2 | **SAM 3D Body** (Meta) | Single image to MHR body, hands and feet | SAM License (conditional) [prior] | > 24 GB some inputs; 6.5 GB offload fork [prior] | GGUF re-host (LocalAI-io); **SAM3DBody-cpp-onnx** (MIT label) [API] | weights 2025-12 [API] | ports new | b |
| 3 | **GVHMR** | Gravity-view world-grounded motion | non-commercial [prior][API] | ~6 GB [prior] | CUDA | push 2026-09-15 [API] | no | b (NC) |
| 4 | **PromptHMR, GENMO, WHAM, TRAM** | Earlier world-grounded models | NC / NC / MIT + SMPL / MIT + SMPL [prior] | 6–9 GB [prior] | CUDA | — | no | b (NC) |
| 5 | **FlowHMR** (2026-10) | Video-conditioned flow-matching *generation* of motion, post-trained with GRPO for physical trackability [paper] | no code found | — | — | paper | **yes** | c2 |
| 6 | **MoCapAnything V2** (SIGGRAPH Asia 2026) | Video plus a one-frame reference pose to BVH rotations for *any* skeleton (animals too), end-to-end, no IK [page][paper] | repo NOASSERTION [API]; weights labelled MIT on HF, uploaded by `kehong` (an author's name) [page] | not stated | PyTorch; an MLX re-host exists [API] | 2026-09-04 [API] | **yes** | b |
| 7 | **TopoCap** (2026-06) | Video to motion on unseen topologies (bipeds to hexapods) via Graph CVAE plus flow matching [paper] | no code found | — | — | paper | **yes** | c2 |
| — | **World-space drift fix** (2026-10) | Closed-form rescaling of camera versus human scale; removes drift under fast camera motion, no retraining [paper] | code on GitHub (`chien90190/worldhmr-fastcam`) [paper] | — | — | 2026-10 | **yes** | **a** (add-on to any of the above) |

**Technique, GEM-X** [page]: an image Body Pose model and a Hand Pose model feed per-frame features to a temporal Motion
model. That model predicts camera-space and world-space SOMA motion; an optional contact and IK correction follows.

- Needs trained weights: yes; open weights exist: `nvidia/GEM-X` (NVIDIA Open Model License).
- The training data was not read.

### 5b · Face capture (webcam, iPhone)

| Rank | Tool | What | Licence | No-CUDA path | Last update | New? | Bucket |
|---|---|---|---|---|---|---|---|
| 1 | **MediaPipe Face Landmarker** | 478 landmarks plus 52 ARKit-style blendshape scores, real time [prior] | Apache-2.0 [API] | CPU, GPU, web | release v1.2.0, 2026-10-28 [API] | release new | b |
| 2 | **iPhone ARKit / Live Link Face** | 52 blendshapes from TrueDepth [prior] | free app | iPhone | — | no | (app) |
| 3 | **RealDenseFace** (2026-08) | Real-time 3DMM fit: dense UV correspondence and depth maps, then a few Gauss-Newton steps [paper] | no code found | — | paper | **yes** | c2; the Gauss-Newton fitting part is (a) |
| 4 | **Face Anything** (2026-04) | Feed-forward 4D face reconstruction from canonical facial-point prediction [paper] | no code found | — | paper | **yes** | c2 |
| — | OpenSeeFace / mocap4face | Webcam blendshapes; mocap4face is free but not open [snippet] | BSD (OpenSeeFace, [known]) / proprietary | CPU | — | no | b |

An ONNX export of MediaPipe's blendshape MLP-Mixer (`fernandotonon/QtMeshEditor-faceblendshapes-onnx`) runs it in ONNX
Runtime [snippet].

### 5c · Text (and keyframes) to motion

| Rank | Tool | What | Licence code / weights | VRAM | No-CUDA path | Last update | New? | Bucket |
|---|---|---|---|---|---|---|---|---|
| 1 | **Kimodo** (NVIDIA) | 282M two-stage transformer diffusion; text *plus* full-body keyframes, sparse joint positions and rotations, 2D waypoints and paths; ≤ 10 s at 30 fps; trained on 700 h of optical mocap [page][paper] | Apache-2.0 / **NVIDIA Open Model License, "ready for commercial use"** (SOMA-RP; the SMPLX-RP variant is R&D-only) [page] | "~17GB" on GPU; "<3 GB" with `TEXT_ENCODER_DEVICE=cpu` [page] | **kimodo.cpp** (GGML, CPU/Vulkan; 942 stars) [API] | v1.2, 2026-10-15 [page] | **yes** | **b** |
| 2 | **HY-Motion 1.0** (Tencent) | 1.0B / 0.46B DiT flow matching [prior] | Tencent community (excludes EU/UK/KR) [prior][API] | 24–26 GB [prior] | — | push 2026-07-18 [API]; distilled TACD-HY-Motion-Lite 2026-10 [API] | distil new | b |
| 3 | **MotionBricks** (NVIDIA, SIGGRAPH 2026) | Real-time modular latent model plus "smart primitives"; chains generations from the last 4 poses [page] | Apache-2.0 / NVIDIA Open Model Agreement (trained on Bones Rigplay 1) [page] | TensorRT, NVIDIA [page] | **motion-bricks.cpp** (GGML, CPU/Vulkan) [API] | 2026-10-26 [API] | **yes** | b |
| 4 | **UniMate** (SIGGRAPH Asia 2026) | Text to motion for any skeleton (5–70 joints): topology-aware attention, spectral RoPE on the graph Laplacian; 60 frames; flan-t5-base text encoder [page][paper] | MIT / **CC-BY-NC-4.0**; data UniML3D (Mixamo, Objaverse, Truebones) [page] | not stated | MLX re-host [API] | 2026-10-08 [API] | **yes** | b (NC); retraining the 74M model is "tiny" but the data's terms are the problem |
| 5 | **TopX** (2026-10-25) | 73M flow-matching transformer: motion for unseen skeletons from tree, rest pose and joint names [paper] | no code found | — | — | paper | **yes** | c2 |
| 6 | **VideoMDM** (2026-06) | Trains a 3D motion diffusion prior from **2D video poses only** (no AMASS); near-3D-supervised quality (FID 0.88 vs 0.54 on HumanML3D) [paper] | MIT code [API] | — | — | 2026-06-07 [API] | **yes** | c2 — but it is the route around AMASS's non-commercial terms |
| 7 | MoMask / ReMoMask-2 / MotionMaestro / MDM | HumanML3D/AMASS-trained | MIT/Apache code, data NC [prior] | small | PyTorch | 2026 | partly | b (NC data) |

**Technique, Kimodo** ([arXiv 2603.15546](https://arxiv.org/abs/2603.15546)) [paper][page]:

1. A text encoder (Llama-derived; GGML conversion `LocalAI-io/Llama-3-Kimodo-GGML`) [page].
2. A two-stage denoising transformer over a motion representation built for constraints.
3. Constraints enter as per-frame features: joint positions or rotations, root heading and path.

Needs trained weights: yes. Open weights exist: `nvidia/Kimodo-SOMA-RP-v1.2` (commercial) and `Kimodo-SOMA-SEED-v1.1`
(trained on the "open Bones-SEED dataset"; that dataset's licence is gated, "bones-seed-license" [API]).

### 5d · Retargeting

| Tool | What | Licence | New? | Bucket |
|---|---|---|---|---|
| **SOMA Retargeter** (NVIDIA, beta) | SOMA BVH to humanoid robot joints; Newton/Warp [page] | Apache-2.0 [API] | **yes** | a |
| Blender 5.3 world-space copy/paste and `convert_rotation_mode` | Copy world-space animation between bones and objects; convert rotation modes [page] | GPL | **yes** | a (building blocks) |
| Skeleton-aware networks (Aberman et al., SIGGRAPH 2020, `deep-motion-editing`) | Neural retargeting between homeomorphic skeletons [snippet] | not checked | no | b |
| UniMate / MoCapAnything V2 / TopoCap / TopX | Retargeting is implicit: generate or capture straight onto the target skeleton | see above | yes | b / c2 |

**Training-free retargeting (a)** [known]:

1. Map bones by role (the humanoid role table of §8).
2. Align rest poses: per-bone rest-orientation offsets.
3. Copy local rotations; scale the root translation by leg length.
4. Fix feet and hands with IK to contact targets.

This is what Uthana describes for bipeds ("proprietary IK retargeting … under a second", no bone mapping) [snippet].

**Apps that do this and how they work (motion).**

- **Move AI**: markerless, "a single camera or multiple cameras"; its "aim" computer vision extracts motion from video;
  real-time unclear [snippet].
- **Rokoko Vision**: free, webcam or phone video; Rokoko's CEO says it is less accurate than its suit [snippet].
- **DeepMotion**: ordinary video to 3D animation "using AI and physics simulation"; also renders [snippet].
- **Plask**: free browser capture [snippet].
- **Radical**: nothing found.
- **Cascadeur** [snippet]:
  - AutoPosing — move a few joints and the body follows; 2026.2 handles quadrupeds and environment contacts;
  - AutoPhysics — turns keyframes into a physically accurate version with "only four sliders"; 2026.1 point constraints;
  - 2026.2 adds animation layers.
- **Uthana**: bipedal IK retargeting, FBX/GLB, GraphQL API [snippet].
- **Meshy animation**: auto-rig plus 600+ presets [prior].

---

## 6 · Image to 3D for props and creatures

Quality evidence:

- A blind reviewer test (Apr–May 2026) of commercial tools: untextured geometry Tripo v3.1 > Rodin Gen-2.5 > Meshy 6;
  textured, Meshy beat Rodin 83.9% in single view; "face count did not predict quality" [snippet].
- Among open models, TRELLIS.2 is "the most consistently recommended" [snippet].

| Rank | Tool | What | Licence code / weights | VRAM | No-CUDA path | Last update | New? | Bucket |
|---|---|---|---|---|---|---|---|---|
| 1 | **TRELLIS.2** (Microsoft) | O-Voxel structured latents, 4B; non-watertight, PBR | MIT / MIT [API] | 24 GB native; 1024 cascade 16 GB via trellis.cpp [prior] | trellis.cpp (CUDA, ROCm, Vulkan, Metal); `localai-org/trellis2cpp` stage-1 (MIT) [API]; ComfyUI native [prior] | weights 2025-12, push 2026-07-10 [API] | ports new | b |
| 2 | **Pixal3D** (Tencent ARC, SIGGRAPH 2026) | Generates *pixel-aligned* 3D (in the input view, not canonical) via back-projection conditioning: better image fidelity [paper] | MIT / MIT (Comfy re-host "mit-and-dinov3" for quantised) [API] | 18–36 GB [prior] | ComfyUI native; Pixal3D.cpp GGUF [API] | 2026-09-01 [API] | detail new | b |
| 3 | **Hunyuan3D 2.1** (open) / **3.0–3.1** (API) | 2.1: shape plus PBR paint; 3.0: 1536³ geometry, 4K PBR, about 90 s [snippet] | 2.1 Tencent community (territory limit) [API]; 3.x no weights found [snippet] | 2.1: 10 GB shape, 21 GB paint [prior] | MLX ports of 2.1 [API]; ROCm report [prior] | 2.1 push 2025-10 [API] | 3.x status new | b (2.1) / app (3.x) |
| 4 | **SUPRA-Tex** (2026-10) | Texturing: an MLLM editor predicts lighting-separated PBR maps in the reference view, projects them onto the visible surface, a material generator completes the hidden side; relightable [paper] | MIT code [API]; weights not found on HF | not stated | — | push 2026-10-29 [API] | **yes** | b? |
| 5 | **Meshy T2** (2026-07) | Native *artist-topology* mesh generation: vertex-set mesh VAE plus a 2-stage flow cascade; interactive speed [paper] | repo with **no licence file** [API] | — | — | push 2026-08-11 [API] | **yes** | b? (terms unknown) |
| 6 | **KaiNinja** (2026-09) | Part-level TRELLIS.2: dual O-Voxel volumes so touching parts stay separate [paper] | repo, no licence [API] | — | — | 2026-10-22 [API] | **yes** | b? |
| 7 | **Seed3D 2.0** (ByteDance, 2026-04) | Coarse-to-fine geometry, unified MoE PBR, part decomposition, "training-free articulation" [paper] | no code found | — | — | paper | **yes** | (closed) |
| 8 | TripoSG / Step1X-3D / SAM 3D Objects / Direct3D-S2 | Earlier open models | MIT / Apache (texture re-host OpenRAIL++) / SAM / MIT [API][prior] | ≥ 8 / 27–29 / 32 / 10–24 GB [prior] | some ports | 2025 | no | b |
| 9 | **ActionMesh** (Meta, 2026-01) | Video or text to *animated* mesh: temporal 3D diffusion, then deformations of one reference mesh (consistent topology, rig-free) [paper] | NOASSERTION / "other" [API] | not stated | — | 2026-10-07 [API] | **yes** | b? |
| — | **AssetFurnace** (`Bingeljell/image-to-3dlab`) | Integrator: prompt or picture to textured, rigged, animated asset | Apache-2.0 [API] | — | — | 2026-10-29 [API] | **yes** | (pipeline) |

**Technique, Pixal3D** ([arXiv 2605.10922](https://arxiv.org/abs/2605.10922)) [paper]:

1. Estimate the camera of the input view.
2. Back-project image features into the 3D grid along camera rays (pixel back-projection conditioning).
3. Generate in that view-aligned frame instead of a canonical pose. Its install follows TRELLIS.2's [prior]; the stage
   design beyond the abstract was not read.

Needs trained weights: yes; open weights exist: MIT.

**Training-free option (a)** for props: multi-view photogrammetry (Meshroom/COLMAP), or Blender 5.3's Gaussian-splat import
[page] from a phone capture. Retopology is still manual.

**Apps that do this and how they work.**

- **Tripo v3.1**: "Smart Mesh" clean topology [snippet].
- **Meshy 6**: quad topology, "pose lock" [snippet].
- **Rodin Gen-2.5**: rated high-fidelity for characters [snippet].
- **Hunyuan 3D 3.0 Pro / 3.1**: Tencent Cloud API [snippet].

All are web services with credits; their internals are unpublished.

---

## 7 · Blender 5.0 → 5.3: what matters for JustStage

All [page] — the developer-docs raw release notes (`blender-developer-docs/docs/release_notes/5.X/*.md`).

- **Characters and rigging**
  - 5.0:
    - **Geometry Attribute constraint** (bones read matrix, vector or quaternion attributes from geometry);
    - per-pose-bone visibility and selection (instanced armatures);
    - a shape-key UI overhaul: multi-select, drag and drop, "Make Basis", flipped Join as Shapes;
    - Copy Global Transform built in.
  - 5.1:
    - **actions +125–146% and shape keys +130–304% faster** (1M-vertex test);
    - Gaussian Smooth F-curve modifier;
    - "Apply to Basis";
    - loop select in Weight Paint.
  - 5.2: Copy Constraints, Duplicate and Rename bones, in-betweens in object mode, loop modes.
  - 5.3:
    - **Copy/Paste World Space** animation;
    - **Convert Rotation Mode** operator plus `Object/PoseBone.convert_rotation_mode()` (Rigify's is deprecated);
    - pose paste with influence;
    - Rigify B-Bone segment count for spine and head;
    - Weight Paint defaults: Auto-Normalize, Multi-Paint and Mirror on; "Add Weight" brush.
- **Hair and physics**
  - 5.0: Curves drawing rewritten; the `resolution` attribute is now honoured ("15 times more geometry" by default — tune
    it down); a new **Cylinder** curve shape.
  - 5.2:
    - **experimental Cloth Dynamics and Hair Dynamics** geometry-nodes assets on a built-in **XPBD Solver** node;
    - **Capture Rest Geometry** modifier;
    - Collider, Custom Force and Custom Effector (closure) effectors;
    - updated *Empty Hair* operator.
  - 5.3: a **Cut Curves** hair-sculpt brush; Curve to Mesh "Miter Scale"; a **Construct Curves** node.
- **Geometry nodes**
  - 5.0: Bundles, Closures, volume grids (SDF ops), a UV Tangent node (MikkTSpace).
  - 5.1: a **Bone Info** node (read pose bones in GN), Matrix SVD, SLIM unwrap.
  - 5.2:
    - **Geometry Bundles** (data travels with geometry across objects);
    - **Lists**;
    - **Mesh Bevel** node;
    - Transfer Attributes;
    - Sample Sound Frequencies (audio-driven animation);
    - GN on Empties;
    - PCA nodes.
  - 5.3: Poisson Solver, Rasterize Points, Combine List, Geometry Materials.
- **Shading**
  - 5.0: Cycles **multi-bounce random-walk SSS**; metallic thin film; shader closures, bundles and repeat zones; adaptive
    subdivision out of experimental.
  - 5.1: EEVEE **Raycast** shader node; shader compile 2× faster (Vulkan cold 24.9 → 11.7 s); texture pool memory −40%;
    HIP RT on by default for AMD.
  - 5.2:
    - EEVEE screen-space raytracing overhaul and Fast GI fixes;
    - SSS negative anisotropy; Random Walk radius re-scaled to match other renderers (old files become "Legacy");
    - **Principled "Thin Wall"**;
    - Cycles **texture cache** (`.tx`);
    - the 8-object-attribute limit removed;
    - 2 GB shadow pool.
  - 5.3:
    - **EEVEE Material Lighting nodes** (Light Accumulation, Light Info, Light Evaluation, Shadow Raycast — per-light custom
      response, e.g. stylised or iridescent skin and eyes);
    - EEVEE panoramic cameras;
    - Principled dispersion; anisotropic glass roughness;
    - **DLSS viewport denoiser** (NVIDIA, driver 620+);
    - better texture baking for thin triangles;
    - **Vulkan default on Windows and Linux**;
    - hardware-raytraced Workbench shadows.
- **Texturing and baking**
  - 5.0: bake from Multires reworked (n-gons, exact subdivision) and **vector-displacement baking**.
  - 5.3: Multires shows textures and attributes in Sculpt; texture-paint undo optimised for UDIMs.
- **Sculpting**: 5.2 Scene Project brush; 5.3 automasking in Vertex and Weight Paint.
- **I/O, USD, MaterialX**
  - 5.0: the C++ FBX importer is default; Collada removed.
  - 5.1: FBX shape-key normals; USD indexed UVs; USD `get_prim_map` hook.
  - 5.2: glTF meshopt, iridescence and dispersion; USD colour spaces; Hydra 2.0 API; Alembic subdivision original
    coordinates.
  - 5.3:
    - a **Collection Importer** for USD;
    - USD Gaussian-splat schema import;
    - Matrix4d primvars;
    - glTF Gaussian splats and KTX2;
    - Alembic arbitrary attributes and subdivision parameters.
  - No MaterialX change in 5.0–5.3's pipeline notes (§8's MaterialX 1.39.4 / `open_pbr_surface` fact stands, [prior]).
- **3D Gaussian Splats** (5.3): a PointCloud `Type`, PLY/SPZ import, rendered by Workbench, EEVEE and Cycles; "rudimentary"
  relighting; no export.
- **Platform and API**
  - 5.0: Intel Macs dropped; sm_50 minimum.
  - 5.1: Python 3.13; macOS camera and mic access for add-ons.
  - 5.2: `gpu.init()` in background mode; GN modifier properties API changed.
  - 5.3:
    - **Projects** (`.blender_project`, per-project OCIO/ACES 2.0, project asset libraries);
    - `gpu.types.GPUStorageBuf`;
    - read-only undo stack;
    - bundled `OpenEXR` and `opentimelineio` Python modules;
    - asset-library extensions and access tokens.

---

## Couldn't verify

- **arXiv API**: one answer, then "Rate exceeded" (HTTP 429) on retries. Paper discovery relied on Hugging Face's papers
  index, which may miss papers HF doesn't list.
- **Hunyuan3D 3.0/3.1 weights**: no primary Tencent source read; "API-only" rests on search summaries.
- **MetaHuman**:
  - the 5.8 release-notes content was not read (only the "what's new" index);
  - the "Creator app discontinued Nov 2026" claim is a headline only;
  - MetaHuman Animator and Faceware internals: nothing found.
- **Vendor internals**: the AccuRIG page returned 404 and the ActorCore page was empty; Cascadeur's help page held only
  navigation; Mixamo marker steps are [known], not re-read; Radical — nothing found.
- **GEM-X**: VRAM and training data not stated or read; no independent comparison with GVHMR or SAM 3D Body.
- **Kimodo**: quality versus HY-Motion rests on NVIDIA's own report; the NVIDIA Open Model License text was not re-read
  this round (§7's "commercial use allowed" [prior], and the card's "ready for commercial use" [page]); the BONES-SEED
  licence is gated and unread.
- **MoCapAnything V2**: the HF weights say MIT while the code repo says NOASSERTION; its runtime pulls `briaai/RMBG-1.4`,
  whose licence was not read.
- **NFR**: the weights' licence is unstated; Multiface's licence was not re-read.
- **No code found** (each searched on HF papers and GitHub only): NGL-Prompter, PatternGSL, SwiftTailor, Garment Particles,
  GarmentCrafter, RegHead, EmoteGPT, Rigel3D, AniGen, the animator-centric skeleton paper, TopoCap, TopX, FlowHMR,
  RealDenseFace, Face Anything, Seed3D 2.0, HyperBones, UNIC.
- **Licence files missing**: Meshy T2, KaiNinja, Stroke3D, Tex-Zero; SUPRA-Tex weights not located; ActionMesh "other".
- **VRAM unstated**: GEM-X, MoCapAnything V2, UniMate, Make-It-Poseable, SUPRA-Tex, Meshy T2, NFR.
- **Classic methods** marked [known] (Pinocchio, geodesic voxel binding, bounded biharmonic weights, robust weight transfer,
  deformation transfer, example-based facial rigging, non-rigid ICP, the Faceit workflow): named from general knowledge;
  papers and links not re-read this round.
- **Commercial-tool rankings** (Tripo, Meshy, Rodin, lip-sync and cloth lists) are mostly vendor or affiliate content; only
  the HackerNoon blind test is independent, and only as a search summary.
- **Nothing was measured on this machine** this round: no model was installed or run, by the brief.
