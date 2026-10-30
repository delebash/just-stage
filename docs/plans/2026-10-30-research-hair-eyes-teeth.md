# Research — realistic hair, brows, lashes, beards, eyes and teeth (2026-10-30)

Scope: the 2025–2026 state of the art, AI and non-AI, for strand hair (scalp, brows, lashes, beard), eyes and the
mouth interior, for JustStage on Blender 5.3. Asked because today's MakeHuman CC0 grooms read as fake (thick strands,
odd colour), brows clump and the GNM eyes look pasted on. Read first: `docs/dev/RESEARCH.md` §5 (hair pack, eye
shells) and §7 (S10 character assets) — this file builds on them and repeats only what it re-checked.

How to read it:

- **Ranking is by quality and capability.** Licence, VRAM and platform are labels beside each option, never filters
  (the user, 2026-10-30). Non-commercial, CUDA-only and >8 GB options stay in, ranked where their quality puts them.
- **Every method says how it works** (paper link, the steps someone would implement), because JustStage is open
  source and can write its own implementation of a published method.
- **Bucket** (the user, 2026-10-30): **(a)** needs no trained model; **(b)** runs on open weights that already exist
  (named, with licence); **(c1)** needs a small LoRA on an open base, or a tiny special-purpose model, that fits the
  8 GB RTX 2070 Super (allowed); **(c2)** needs real training we can't do. Every (c2) gets a training-free alternative.
- **Evidence marks:** *page read* (page or raw repo file read), *API* (GitHub / Hugging Face API), *search snippet*
  (a search engine's summary only), *measured* (run today on this machine, Blender 5.3.0 beta `964900392c2a`),
  *inference* (my reasoning from the cited facts — a proposal, not a finding).

## Summary table

| Area | Rank | Option | How it works (one line) | Bucket | Code licence | Weights / data licence | GPU | Updated | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| **Why ours looks fake** | — | Our own hair, eye and teeth setup | Every strand the same pure-pheomelanin colour; Principled Hair is Cycles-only; EEVEE's default draws strands ~1 px wide; brows made by duplicating 44–79 guides into tufts; lashes a third to half of real; flat-colour iris; no occlusion or tearline shells | — | ours | MakeHuman CC0 | — | today | measured |
| Image → strands | 1 | **DiffLocks** (CVPR 2025) | Diffusion transformer paints a 256² scalp texture of 64-d strand codes from DINOv2 image features; ~100K strands decoded | (c2); weights exist | DiffLocks NC research licence | NC; 40K synthetic set NC | CUDA, custom kernels; 2.33 s on H100 | 2025-10-31 | API, page read |
| Image → strands | 2 | **Im2Haircut** (ICCV 2025) | Transformer hairstyle prior (synthetic + real) drives a Gaussian-splatting fit; strong back-of-head | (c2); checkpoints downloadable | none (no LICENSE) | not stated | CUDA 11.8, "tested on A100" | 2026-02-02 | API, page read |
| Image → strands | 3 | **TANGLED** (2025) | Latent diffusion conditioned on multi-view lineart; braid post-module; any style incl. anime and paintings | (c2) | no code | MultiHair 457 styles, not released | — | 2025-02-10 | page read |
| Image → strands | 4 | **Perm** (ICLR 2025) | Frequency-domain PCA strand basis; guide + residual textures, each with its own generator; fitted to images | (b) checkpoints released | MIT | trained on Hair20k (augmented USC-HairSalon, no licence) | CUDA ≥11.3 (StyleGAN ops) | 2026-07-11 | API, page read |
| Image → strands | 5 | HairStep (CVPR 2023) | Image → strand map + depth map → 3D orientation/occupancy → grown strands | (b) NC weights | CC BY-NC 4.0 | NC | CUDA 11.1 | 2026-03-30 | API |
| Multi-view / video | 1 | **Wispy to Voluminous** (2026-06) | Prior-free: Gaussians on a tracked head → traced strands → grounded curves; beards, brows, lashes | **(a)** per-scene optimisation | no code | — | — | 2026-06-06 | page read |
| Multi-view / video | 2 | **HairGS** | 3D Gaussian splatting → strand merging → photometric refinement, per scene | (a) per scene; uses FLAME head | MIT | FLAME is non-commercial | CUDA (Windows supported) | 2026-04-01 | API, page read |
| Multi-view / video | 3 | GaussianHaircut, NeuralHaircut, MonoHair, EfficientMonoHair, CGHair, Vid2Haircut, GeomHair | Video / multi-view → orientation fields or Gaussians → strands | (b) / (c2) | CC BY-NC-SA / CC BY-NC / CC BY-NC / none / none / none / NOASSERTION | NC or none | CUDA | 2023–2026 | API |
| Text → strands | 1 | **Digital Salon** (2025) | Text → CLIP retrieval over a captioned groom library → real-time CUDA sim + interactive cut/regrow → ControlNet render | **(b)** CLIP (MIT) | MIT | ships USC-HairSalon renders (no licence) | CUDA 11.6+ | 2025-07-14 | API, page read |
| Text → strands | 2 | HAAR (CVPR 2024) | Text-conditioned latent diffusion in a shared hairstyle UV space; captions from a VQA model | (c2) | CC BY-NC 4.0 | NC | A100 40 GB | 2024-10-09 | API, page read |
| Text → strands | 3 | StrandHead (ICCV 2025) | Text → head + strands by score distillation from SD 1.5 normal/depth models with hair priors | (b) with NC parts | MIT | FLAME (NC), NeuralHaircut prior (NC), HumanNorm SD 1.5 | A6000 | 2026-02-26 | API, page read |
| Procedural groom | 1 | **Blender's hair node groups, done right** (+ DiffLocks' own data recipe) | Guides → Interpolate (Poisson) to 100K+ → taper → multi-level clump + tip spread → frizz/noise; Cycles Principled Hair with per-strand melanin variance | **(a)** | GPL (Blender) | ours (CC0) | any | Blender 5.3 | page read, measured |
| Hair cards | 1 | CGHair (CVPR 2026) | Strands clustered into representative cards with shared texture codebooks | (c2) | no code | — | — | 2026-04-04 | page read |
| Hair cards | 2 | Unreal Hair Card Generator | Dataflow graph: clump strands → card strips (triangle budget) → shared texture atlas → per LOD | (a) | Unreal EULA, experimental | — | — | UE 5.8 | page read |
| Hair cards | 3 | **Our own card baker** (Hair Tool's documented design) | Cluster strands → ribbon per cluster → bake diffuse/depth/alpha/flow atlas → UVs | **(a)** | ours | ours | any | — | page read (design), inference |
| Groom library | 1 | MakeHuman hair-editor pack | 16 listed styles incl. brows, beards, lashes | (a) | — | **CC0** | — | 2026-10-24 | measured (§5) |
| Groom library | 2 | Blender demo "Hair Styles" (Daniel Bystedt), "Animal Fur Examples" (Blender Studio) | Geometry-nodes grooms | (a) | — | CC-BY-SA / CC0 | — | not stated | page read |
| Groom library | 3 | **Generate our own** (DiffLocks recipe) | 75 hand-made guide sets × 110 randomised node parameters → 40K styles | (a) | ours | ours | CPU / any | — | page read |
| Eyes | 1 | **Layered eye stack** (eyeball + cornea shell + occlusion + tearline + caruncle) with a deep iris | CC5 / MetaHuman / ICT-FaceKit layout; iris ~3.6 mm behind the cornea apex (Navarro optics) | (a) | ours | ICT geometry MIT; GNM Apache-2.0 | any | — | page read |
| Eyes | 2 | Iris texture, procedural (MPFB2-style radial noise + Voronoi) | Polar-coordinate fibres, collarette, crypts, limbal ring | (a) | MPFB2 GPL-3 (code), CC0 (assets) | — | any | 2026-10-24 | page read |
| Eyes | 3 | Iris texture from an image model, then a LoRA | Z-Image-Turbo / FLUX.2 klein 4B zero-shot; else an SDXL LoRA (kohya: 8 GB) | (b) → (c1) | sd.cpp MIT | Apache-2.0 / OpenRAIL++-M | SDXL LoRA fits 8 GB | 2026 | API, page read |
| Teeth | 1 | GNM teeth/tongue (current) + per-part shaders (enamel translucency by thickness, SSS gums/tongue, wet layer, mouth-cavity darkening) | Geometry reuse + shader build | (a) | Apache-2.0 | Apache-2.0 | any | — | page read, search snippet |
| Teeth | 2 | ICT-FaceKit teeth/gums/tongue; MakeHuman teeth/tongue | Alternative geometry | (a) | MIT | MIT / CC0 | — | 2020 / 2026 | API (§7) |

---

## 1 · Why our hair, eyes and teeth look fake — measured on this machine

Measured today in Blender 5.3 beta, headless (`--factory-startup --disable-autoexec`), on `hair.blend` from
MakeHuman's pack (SHA-256 per §5) and on JustStage's own code (`extension/juststage/modules/hair/*.py`,
`modules/head/part_materials.py`). Object scale is 1.0 and units are metres (the lash object is 0.091 m wide) —
*measured*.

### 1a · Strand counts and widths of the pack (evaluated, after its node-group modifiers)

| Groom | Curves in file | Strands after modifiers | Points / strand | Radius median (p95) |
|---|---|---|---|---|
| `short_hedgehog` | 42,504 | 42,504 | 8 | 0.050 mm (0.097) |
| `short_crown` | 19,907 | 19,907 | 8 | 0.053 mm (0.097) |
| `hair_to_shoulder` | 2,130 | 23,430 | 29 | 0.089 mm (0.145) |
| `straight_hair_to_shoulder` | 252 | 10,191 | 16 | 0.050 mm (0.095) |
| `short_ponnytail` | 1,654 | 1,654 | 57 | 0.075 mm (0.098) |
| `tail_base` / `back_pigtail` | 1,952 / 544 | same | 8 / 29 | 0.150 / 0.152 mm |
| `wild_eyebrow` / `wild_thick_eyebrow` (both brows) | 44 / 79 | 824 / 1,490 | 8 | 0.100 mm (0.194) |
| `wild_beard` / `wild_thick_beard` | 210 / 9,472 | 4,206 / 14,175 | 8 | 0.100 / 0.050 mm |
| `basic_lashes_upper` / `_lower` (both eyes) | 97 / 66 | 99 / 65 | 5 | 0.050 mm (0.100) |

*measured*. Comparison points:

- Real scalp: 175–300 terminal hairs per cm², average 223 ([BioNumbers 116431](https://bionumbers.hms.harvard.edu/bionumber.aspx?id=116431), *search snippet*);
  80,000–150,000 follicles per scalp (a clinic page citing StatPearls, *search snippet*, not confirmed at StatPearls).
- MetaHuman's real-time budget: hairstyle 50,000 strands at LOD0, 25,000 at LOD1; facial hair 10,000 / 5,000
  ([LOD specification](https://dev.epicgames.com/documentation/en-us/metahuman/platform-support-and-lod-specifications-for-metahumans), *search snippet*).
  So the pack's scalp grooms sit at a real-time count, not an offline one.
- Lashes: 90–160 on the upper lid in 5–6 rows, 75–80 on the lower lid in 3–4 rows, per eye
  ([StatPearls, Eyelash, NBK537278](https://www.ncbi.nlm.nih.gov/books/NBK537278/), *search snippet*). The pack has
  ~50 upper and ~33 lower per eye, at 5 points each — a third to a half of the count, with too few points to curl.
- Brows: `wild_eyebrow` turns each of its 44 guides into ~19 strands with *Duplicate Hair Curves*, then *Clump Hair
  Curves* pulls them back toward their guides (modifier stack *measured*). Blender's manual calls Duplicate "a
  lighter-weight alternative" to Interpolate ([interpolate_hair_curves.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/modeling/geometry_nodes/hair/generation/interpolate_hair_curves.rst), *page read*).
  *Inference:* ~19 near-copies around each guide make a visible tuft — the "clumping" the user sees. Real brow hairs
  grow one per follicle, so a brow needs individually placed hairs, not duplicated guides.
- Widths are not the main problem: 0.05 mm radius = 0.1 mm diameter for scalp hair is in the human range; brows at
  0.2 mm diameter are thick but brow hairs are coarse. No dermatology source for shaft diameter was found (search 16).
- The modifiers' own input values could not be read through Blender 5.3's Python (the NodesModifier rejected item
  access) — only the evaluated results above.

### 1b · Colour: every strand is pure pheomelanin, and all are identical

- JustStage's `groom.hair_material` replaces the pack's materials with a Principled Hair BSDF in melanin
  parametrisation, reading `melanin` and `redness` curve attributes; `hair_add.py` defaults are `melanin = 0.8`,
  `redness = 1.0` ("Blender's own Principled Hair BSDF defaults"), written as one constant for every strand
  (`_set_colour`, `np.full`) — *page read* (our code).
- Blender 5.3's Principled Hair BSDF defaults, read from a fresh node: model Chiang, Melanin 0.8, Melanin Redness 1.0,
  Roughness 0.3, Radial Roughness 0.3, Coat 0, IOR 1.55, Offset 0.035, **Random Color 0, Random Roughness 0** — *measured*.
- Blender's manual: "eumelanin = Melanin×(1.0−MelaninRedness), pheomelanin = Melanin×MelaninRedness", and at the top of
  the page: "Realistic hair should have a minimum of variance between each strand"
  ([hair_principled.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/render/shader_nodes/shader/hair_principled.rst), *page read*).
- *Inference:* Redness 1.0 makes eumelanin 0 — all red-yellow pigment — so every groom is a saturated red-brown
  ("odd colour"); with Random Color 0 and one value per groom every strand is the same, which reads as plastic.
  Fix (bucket a): per-strand melanin drawn from a distribution (the per-curve `melanin` attribute, plus Random Color),
  a realistic eumelanin/pheomelanin ratio per hair colour, Random Roughness, and root-to-tip change through
  *Curves Info → Intercept* ("1 at the tip and 0 at the root", [hair_info.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/render/shader_nodes/input/hair_info.rst), *page read*).
  Which ratios per colour is open — no measured table was found (Couldn't verify).

### 1c · Engine: Principled Hair is Cycles-only, and EEVEE draws strands a pixel wide

- Principled Hair BSDF and Hair BSDF are marked "Cycles Only"; EEVEE's node list: "Hair BSDF — Not supported",
  "Principled Hair BSDF — Not supported"; Principled BSDF in EEVEE: "Anisotropy is not supported"
  ([nodes_support.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/render/eevee/limitations/nodes_support.rst), *page read*).
  A Blender bug report: hair with this shader shows black in EEVEE; a developer: "not supported in EEVEE yet"
  ([#56207](https://projects.blender.org/blender/blender/issues/56207), *search snippet*). MakeHuman's pack works around
  it with "Hair shader EEVEE" groups that hold both a Principled Hair BSDF and a Principled BSDF + Translucent
  (*measured*); JustStage's material drops that fallback.
- EEVEE's *Curves* panel: **Strand** = "a thin strand roughly a pixel wide. Curve diameter parameters are ignored";
  **Strip** = "a flat ribbon with rounded normals" ([curves.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/render/eevee/render_settings/curves.rst), *page read*).
  Blender 5.3 factory settings and `hair.blend` both have `hair_type = STRAND`, `hair_subdiv = 0`; EEVEE render
  samples 64 — *measured*.
- Cycles: the default curve shape is `RIBBONS`, subdivisions 2 (*measured*); the manual: Rounded Ribbons "for fast
  rendering", **3D Curves** "for accurate results when viewing curves close up" ([hair.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/render/cycles/render_settings/hair.rst), *page read*).
- *Inference:* in EEVEE (the viewport's Material Preview and any EEVEE render) every 0.1 mm hair is drawn at least a
  pixel wide — at head-and-shoulders framing a hair is well under a pixel — so the groom reads thick and coarse, and its
  shading is wrong because the hair BSDF is unsupported. The face tests render in Cycles
  (`tools/face_test/test_face_project.py`: `scene.render.engine = "CYCLES"`), so in Cycles stills the causes are the
  colour (1b), the counts (1a) and the ribbon shape.

### 1d · Eyes and teeth: flat colours, no shells

- `part_materials.py`: one Principled BSDF per GNM region; iris a flat colour `(0.12, 0.06, 0.03)`, pupil near-black,
  sclera flat `(0.80, 0.76, 0.71)` with SSS 0.3, cornea Transmission 1.0 at IOR 1.376; teeth, gums and tongue flat
  colours with SSS. Its docstring: "starting values … the eye and mouth generators (R5) replace the colours with
  textures". `test_face_project.py` sets the iris to the photo's median colour × 1.6 — *page read* (our code).
- No eye-occlusion, tearline or caruncle mesh exists, and no mouth-cavity darkening: the parts are `eyeLeft`,
  `eyeRight`, `teeth` (`tests/blender/test_head.py`) — *page read*.
- *Inference:* a flat iris with no limbal ring or fibres, no eyelid shadow on the eyeball and no wet line where lid
  meets eye is exactly what CC5's Eye Occlusion exists to fix ("simulate the shadow cast from the eyelids to prevent
  over-exposure on the eyeballs", §5) — so the eyes look pasted on.

---

## 2 · Image or text → strand hair (AI), ranked by quality

### 2a · From one image (generation)

**1. DiffLocks** — Rosu, Wu, Feng, Zheng, Black; CVPR 2025; [arXiv 2505.06166](https://arxiv.org/abs/2505.06166), repo
[`Meshcapade/difflocks`](https://github.com/Meshcapade/difflocks) (push 2025-10-31, 195★, *API*).
- How it works (*page read*, arXiv HTML): (1) a strand VAE — 256 points per strand, a 1D-conv encoder to a 64-d code,
  a modulated SIREN decoder; (2) a 256×256×64 scalp texture of strand codes plus a 256×256 density map; (3) an
  Hourglass Diffusion Transformer (EDM) denoises texture + density, cross-attending to DINOv2-large features
  (55×55×1024 + CLS); (4) ~100K root positions sampled by density, codes decoded to strands, "no post-processing".
- Data recipe (useful on its own, §3): 75 hand-made base styles of ~50 guides each, interpolated to ~100K strands with
  geometry nodes (58 main + 349 auxiliary nodes, **110 randomised parameters**: clumping, curling, noise), Chiang BSDF,
  cloth sim, 255 Poly Haven HDRIs; 40K styles rendered at 768² in about a week on 4 H100s.
- Quality: 2.33 s per image on an H100; curly and detailed hair. Limits — no braids, ponytails, buns or accessories;
  "prioritizes local hair details over perfect image alignment" (*page read*).
- Licence: LICENSE "DiffLocks License (Non-Commercial Scientific Research Use Only)", granting use "for the sole
  purpose of performing non-commercial scientific research, non-commercial education, or non-commercial artistic
  projects" (*API*, LICENSE read); commercial use by contacting Meshcapade (project page, *search snippet*).
- Platform: custom CUDA kernels; exports `.blend` / Alembic through Blender 4.1.1 ("It will likely not work with other
  versions") — README *page read*. VRAM not stated.
- **Bucket (c2)** — the DiT trains ~400K iterations at batch 128 and the VAE 3M iterations (*page read*); NC weights
  exist. Training-free alternative: its own data recipe (procedural, §3) for a library, plus retrieval (2b).

**2. Im2Haircut** — Sklyarova, Zakharov, Prinzler, Becherini, Black, Thies; ICCV 2025; [arXiv 2509.01469](https://arxiv.org/abs/2509.01469),
[`Vanessik/Im2Haircut`](https://github.com/Vanessik/Im2Haircut) (push 2026-02-02, *API*).
- How it works (*page read*): a transformer hairstyle prior trained mostly on synthetic grooms (the inner structure),
  with real images added for the outer layer; the prior then drives a Gaussian-splatting reconstruction from one or
  more photos. Claims better orientation, silhouette and back-of-head consistency than earlier pipelines.
- Licence: **no LICENSE file** (GitHub `license: null`, *API*) — all rights reserved by default. Checkpoints come with
  its `install.sh`. CUDA 11.8; "Code was tested on NVIDIA A100 GPU" (*page read*). **Bucket (c2).**

**3. TANGLED** — Long, Zhao, Ouyang et al., ShanghaiTech + Deemos; [arXiv 2502.06392](https://arxiv.org/abs/2502.06392) (2025-02-10).
- How it works (*page read*): latent diffusion with cross-attention on **multi-view lineart** (keeps partings and
  density, drops photo noise); a parametric braid post-module; inputs of any style — photos, anime, oil paintings;
  MultiHair dataset, 457 styles × 74 attributes. No code found (search 1, GitHub). **Bucket (c2).**

**4. Perm** — He et al., ICLR 2025; [arXiv 2407.19451](https://arxiv.org/abs/2407.19451), [`c-he/perm`](https://github.com/c-he/perm) (MIT, push 2026-07-11, *API*).
- How it works (*page read*): a PCA strand basis in the frequency domain splits global shape from curl; a groom becomes
  **guide textures** (low frequency) + **residual textures** (high frequency), each with its own generative model,
  mirroring a groomer's guides-then-detail; used for single-view fitting, editing and hair-conditioned image generation.
- Released: pre-trained checkpoints, fitted parameters for all 343 USC-HairSalon styles, the Hair20k training set. Not
  released: the single-view pipeline "with a public license" (README checklist, *page read*). CUDA ≥11.3 for
  EG3D/StyleGAN3 ops; PCA fitting ~64 GB RAM (S10).
- **Bucket (b)** for its checkpoints (MIT repo; the training data, USC-HairSalon, has no licence — provenance open). The
  PCA strand basis alone is a **(c1) tiny model**: fit it on the CPU to our own procedural grooms (*inference*).

**5. HairStep** (CVPR 2023, [`GAP-LAB-CUHK-SZ/HairStep`](https://github.com/GAP-LAB-CUHK-SZ/HairStep)): image → "strand
map" (2D orientation) + depth map → 3D orientation and occupancy fields → strands grown from the scalp. LICENSE
"Attribution-NonCommercial 4.0 International" (*API*); CUDA 11.1. **Bucket (b), NC weights.**

Below these on quality or availability: StrandHead and HAAR (text, 2b); HairGPT (ShanghaiTech + Deemos, May 2026, no
code — S10); Hairflow (Columbia, 2024–25, image → 3D hair, *search snippet* only).

### 2b · From text

**1. Digital Salon** — He, Amador Herrera, Zhou et al. (Adobe, Yale, KAUST, MPI …); [arXiv 2507.07387](https://arxiv.org/abs/2507.07387),
[`digital-salon/Digital-Salon`](https://github.com/digital-salon/Digital-Salon) (**MIT**, push 2025-07-14, *API*).
- How it works (*page read*, project page + INSTALL): four stages — **text-guided retrieval** (a prompt returns "three
  distinct hairstyles with variations" from a library with **CLIP embeddings captioned for each hairstyle**),
  **real-time simulation** (CUDA, 10,000–80,000 strands; its log shows "200460 particles on GPU"), **interactive
  refinement** (select scalp triangles, generate, cut), and **hair-conditioned image generation** (SD 1.5 + ControlNet
  Canny).
- The release swapped Adobe's in-house grooms for USC-HairSalon renders (no licence) and needs a Pinscreen head mesh
  downloaded separately. CUDA 11.6+, Windows and Linux.
- **Bucket (b)**: CLIP (openai/CLIP, MIT, *API*). The strongest *training-free* text-to-groom design found: retrieval
  over a captioned library, then procedural edits — exactly what our own CC0 library (§3, §7) could feed.

**2. HAAR** — Sklyarova et al., CVPR 2024; [arXiv 2312.11666](https://arxiv.org/abs/2312.11666), [`Vanessik/HAAR`](https://github.com/Vanessik/HAAR).
- How it works (*page read*): latent diffusion conditioned on text in a common hairstyle UV space; the synthetic
  training grooms were auto-captioned with 2D VQA systems; output "production-ready" strands.
- LICENSE.txt "Attribution-NonCommercial 4.0 International" (*API* — S10 had only the README's "scientific research
  purposes"); "tested on an NVIDIA A100 40GB". **Bucket (c2).**

**3. StrandHead** — Sun et al., Nanjing University, ICCV 2025; [arXiv 2412.11586](https://arxiv.org/pdf/2412.11586),
[`XiaokunSun/StrandHead`](https://github.com/XiaokunSun/StrandHead) (MIT, push 2026-02-26, *API*).
- How it works (*page read*, README): bald head first, then strands, both optimised by score distillation from
  HumanNorm's SD 1.5 normal/depth-adapted models and ControlNet-normal, strands initialised from USC-HairSalon or HAAR
  styles and decoded by a NeuralHaircut strand checkpoint; scripts edit colour, curl, length and count, and transfer
  hairstyles.
- Code MIT, but it loads FLAME (non-commercial), the NeuralHaircut prior (CC BY-NC) and HumanNorm models; tested on an
  A6000, CUDA 11.7, Ubuntu. **Bucket (b), with NC pieces.**

**Training-free route for text → groom** (*inference*, a proposal): a llama.cpp model (the family's LLM runtime) maps
the prompt to hairstyle attributes, then (1) retrieves from our tagged CC0 library as Digital Salon does, and/or
(2) sets the procedural generator's parameters (§3). Microsoft's Hairmony taxonomy (SIGGRAPH Asia 2024) is a ready
attribute vocabulary — [`microsoft/hairmony`](https://github.com/microsoft/hairmony), data under the "Research Use of
Data Agreement v1.0" (*API*); whether that agreement covers using the attribute list itself is not stated (Couldn't
verify).

### 2c · From multi-view images, video or scans (capture)

Capture needs a real person and several views — not JustStage's main path, but the best route for beards, brows and
lashes, which no single-image model handles.

| Rank | Method | How it works | Bucket | Code licence | GPU | Updated |
|---|---|---|---|---|---|---|
| 1 | **Wispy to Voluminous** (Lee, Nam, Jarabo, Aliaga; [arXiv 2606.08041](https://arxiv.org/abs/2606.08041), 2026-06-06) | **Prior-free**: Gaussians constrained by a tracked head → strands traced through crossings → grounded to the skin with a physical prior → opacity-driven density → explicit curves for beard, moustache, lashes, brows | **(a)** | no code | — | 2026-06 |
| 2 | **HairGS** ([`yimin-pan/hair-gs`](https://github.com/yimin-pan/hair-gs)) | 3DGS geometry → strand merging → photometric refinement; COLMAP input; a new topology metric | (a) per scene — its README downloads no checkpoint (*inference*: no learned prior); FLAME head (NC) | **MIT** | CUDA 11/12; Windows (MSVC) | 2026-04-01 |
| 3 | GaussianHaircut (ECCV 2024, [`eth-ait/GaussianHaircut`](https://github.com/eth-ait/GaussianHaircut)) | strand-aligned 3D Gaussians fitted to monocular video, NeuralHaircut prior | (b) | CC BY-NC-SA 4.0 | CUDA 11.8 + Blender 3.6 | 2025-01-16 |
| 4 | NeuralHaircut (ICCV 2023, [`egorzakharov/NeuralHaircut`](https://github.com/egorzakharov/NeuralHaircut)) | stage 1: SDF + orientation field; stage 2: strand optimisation with a diffusion prior on a latent scalp texture | (b) | CC BY-NC 4.0 | CUDA | 2024-09-29 |
| 5 | MonoHair (CVPR 2024, [`KeyuWu-CS/MonoHair`](https://github.com/KeyuWu-CS/MonoHair)) | exterior from an Instant-NGP-style fit, interior inferred, strands grown; writes `.hair` | (b) | CC BY-NC 4.0 | tiny-cuda-nn | 2024-08-14 |
| 6 | EfficientMonoHair (CVPR 2026) | implicit networks + multi-view direction fusion, ~10× faster | — | repo is a project page only | — | 2026-05-14 |
| 7 | CGHair (CVPR 2026, [arXiv 2604.03716](https://arxiv.org/abs/2604.03716)) | Gaussian hair → cards (§4) | (c2) | repo is a project page only | — | 2026-05-26 |
| 8 | GeomHair ([arXiv 2505.05376](https://arxiv.org/abs/2505.05376)) | strands from colourless 3D scans (FLAME fit, orientation maps, CUDA UDF) | (b) | NOASSERTION | CUDA | 2026-06-02 |
| 9 | Vid2Haircut (EG 2026), DynHair (ECCV 2026; MIT, a 3 KB placeholder) | video → strands; dynamic hair avatars | — | none / MIT | — | 2026 |

All *API*; methods *page read* where an arXiv page is linked, else README or *search snippet*. CT2Hair (CT-scanned
wigs, CC BY-NC 4.0, *API*) is data, not a method.

---

## 3 · Procedural and artist grooming in Blender 5.x (bucket a)

**The standard:** Blender's own hair node groups (Essentials library) — Generation: Duplicate, Generate, Interpolate;
Guides: Braid, Clump, Create Guide Index Map, Curl; Deformation: Blend, Displace, Frizz, Hair Curves Noise, Roll,
Rotate, Shrinkwrap, Smooth, Straighten, Trim; Utility: Attach Hair Curves to Surface, Redistribute Curve Points,
Restore Curve Segment Length; Read: Curve Info / Root / Segment / Tip, Hair Attachment Info; Write: Set Hair Curve
Profile — the manual's [hair node pages](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/modeling/geometry_nodes/hair) (*API*, listed).

A recipe to replace the pack's look; each step from the manual (*page read*) unless marked:

1. **Guides, not duplicates.** A few hundred to a few thousand guides with enough points to curl. MetaHuman's groom
   tools warn above 3,000 guides, "the recommended upper limit", and flag curves over 255 points
   ([MH Groom tools](https://dev.epicgames.com/documentation/metahuman/mh-groom-tools?lang=en-US), *page read*).
2. **Interpolate Hair Curves** with *Poisson Disk* distribution ("maintain a minimum distance between root points"), a
   *Density* per unit area, several *Interpolation Guides*, *Part by Mesh Islands* for partings. Aim for ~100K+ scalp
   strands for stills (175–300 /cm², §1a) and ~50K for real time (MetaHuman LOD0). Duplicate is the lighter
   alternative and is what makes tufts (§1a).
3. **Set Hair Curve Profile**: thicker root, thin tip (*Factor Min* at the root, *Factor Max* at the tip).
4. **Clump Hair Curves** in levels: a small *Guide Distance* for many small clumps, *Tip Spread* > 0 "preventing perfect
   convergence", *Clump Offset*, *Distance Falloff*. MetaHuman's builder uses primary, secondary and tertiary clumps
   plus "Clump Tighter" (*page read*); the pack's grooms run one Clump.
5. **Frizz / Hair Curves Noise**, small, *Cumulative Offset* on; a sparse set of flyaways (MetaHuman: Scraggle,
   Spread). Houdini's equivalent stack: Set Guide Direction, Set Guide Length, Lift, Straighten, Smooth, Frizz, Bend,
   Clump, Part, Add White Hairs ([Houdini fur docs](https://www.sidefx.com/docs/houdini/fur/index.html), *page read*).
6. **Shade in Cycles** with Principled Hair BSDF: per-strand melanin with variance (Random Color, Random Roughness), a
   realistic redness, root-to-tip change through *Intercept*; the **Huang** model for elliptical hair, *Aspect Ratio*
   "0.8~1 for Asian hair, 0.65~0.9 for Caucasian hair, 0.5~0.65 for African hair", which needs curve normals from
   geometry nodes (*page read*). Render shape **3D Curves** for close-ups.
7. **EEVEE path:** shape **Strip** so the diameter counts; a Principled BSDF-based approximation (EEVEE has no hair
   BSDF and no anisotropy, §1c); more TAA samples for sub-pixel coverage (*inference*).
8. **Brows:** individual hairs on a painted density mask, flowing along the brow (Daz SBH and XGen brow time-lapses
   paint direction, *search snippet*). **Lashes:** 90–160 upper / 75–80 lower per eye in rows (§1a), 10+ points each
   for the curl. **Beard / stubble:** short interpolated curves on a density mask; stubble likely needs a skin texture
   layer under it too (*inference*). MetaHuman ships beard, moustache and "vellus" peach fuzz as separate grooms
   ([MetaHuman LODs](https://dev.epicgames.com/documentation/en-us/metahuman/controlling-metahuman-levels-of-detail-lods), *search snippet*).

**DiffLocks' data recipe** (§2a) is a published, working version of this recipe: 75 base guide sets, ~100K
interpolated strands, clumping / curling / noise, 110 randomised parameters, Chiang BSDF — the same building blocks
Blender ships. It is the training-free way to a large CC0 groom library of our own (*page read* for the recipe,
*inference* for our use of it).

Free and paid Blender tools (paid = reference only):

| Tool | What and how | Licence / price | Evidence |
|---|---|---|---|
| Blender hair node groups | above | GPL, built in | page read |
| Procedural Human Hair (creamtau) | geometry-nodes brows, lashes, hair; a changelog says its shaders use the Huang model | CC BY-SA, pay-what-you-want | search snippet (S10, search 4) |
| N_Hair_Nodes v2 | proxy nodes adding physics to curves hair | not checked | search snippet |
| Hair Tool 4 (Bartosz Styperek) | curves → hair cards: hair systems + deformers, guide by a grid mesh, "Glue Mesh — sculpt your hair rather than groom", bake diffuse / depth / alpha / flow, automatic UVs, convert to mesh, **Cards to Curves** | paid | page read ([docs repo](https://github.com/JoseConseco/HairTool_3_Documentation)) |
| RapidHair Cards | geometry-nodes card hair for Blender 5, needs a UV map; specular and "Random White Hair" controls | paid | search snippet |
| Curve-BStrands | bakes strand texture atlases for cards, Blender 5.1+ | paid | search snippet |
| EyeForge | §5b | GPL, $16.98 | page read |

---

## 4 · Hair cards for game LODs

| Rank | Option | How it works | Bucket | Licence | Evidence |
|---|---|---|---|---|---|
| 1 | CGHair (CVPR 2026; Luo, Sarkar, Mosella-Montoro, Vicente Carrasco, De la Torre) | multi-view → Gaussian strands (initialised by a generative prior) → strands clustered into "representative hair cards" sharing texture codebooks; 4× faster strand reconstruction, "over 200x lower memory footprint" than 3DGS hair | (c2) | no code | page read |
| 2 | Unreal Hair Card Generator | a Dataflow graph: GetGroomAsset → GroomAssetToCollection → **GenerateCardsClumps** ("Higher clump values increase the detail") → **GenerateCardsGeometry** (triangles by strand count and coverage; Num Clumps × 3 cards, Num Flyaways, Num Triangles) → **GenerateCardsTextures** (shared texture islands) → per LOD; card groups defined in the DCC and exported in Alembic; "Experimental" | (a) | Unreal EULA, Unreal only | page read ([doc](https://dev.epicgames.com/documentation/en-us/unreal-engine/hair-card-generator-for-grooms-in-unreal-engine)) |
| 3 | Hair Tool 4 | §3 | (a) | paid | page read |
| 4 | Houdini / SideFX Labs | the fur docs list "generating hair cards for games" | (a) | Houdini licence | page read (mention only) |
| 5 | Open code | `PurgatoryMP/Hair-Card-Generator` (GPL-3.0, 2★, push 2026-09-09), `mysticfall/hairball` (Blender curves → cards for GodotHair, "other", push 2026-10-23), `jamesrobinsonvfx/cards_to_curves` (Houdini HDA, no licence) | (a) | as listed | API |

**Our own card baker** (bucket a; *inference* from the documented designs above): (1) cluster strands by root position
and shape (k-means, or the groom's own clump / guide index); (2) one ribbon per cluster along its mean curve, width
from the cluster's spread, oriented by the scalp normal; (3) render each cluster orthographically in Blender into an
atlas — alpha, depth, root-to-tip gradient, strand ID, flow (Hair Tool's documented set); (4) UVs per card; (5) LODs
by merging clusters down MetaHuman's card-vertex budgets (30,000 → 1,500 over LOD0–4, search 18).

---

## 5 · Eyes

### 5a · Geometry and optics (bucket a)

- **The layer stack** CC5 and MetaHuman use: the eyeball; a tearline mesh "under the Eye Occlusion" that simulates
  "the moisture and the tear reflectivity on the eyeballs and the tear ducts"; the Eye Occlusion, "the topmost mesh
  layer", for "the shadow cast from the eyelids" — CC5 manual, *page read* (§5). MetaHuman's face has `eyeshell`,
  `eyeEdge` and `saliva` meshes (§5). An 80.lv UE4 character article: the occlusion mesh "provides fake eyelid shadow
  and occlusion shadow for eyes, this is the key to making the eyes look more natural"; the tear-line mesh "blends eye
  and eyelid more natural and it also provides the wet effect"; check the occlusion mesh's UVs to see how its shader
  works (*search snippet*, search 19). A Reallusion forum user: after editing in Blender the layers "move with the head
  but are otherwise static" — they must follow the lids and the eye (*search snippet*).
- **Open geometry to copy the structure of:** ICT-FaceKit (MIT, push 2020-12-01, *API*) — eyeballs (1,570 v each),
  lacrimal fluid (204 v), eye blend (24 v), eye occlusion (152 v), lash strips (S10, *page read*); GNM (Apache-2.0)
  eye interior and cornea (§5, what we use now); MakeHuman eyes (CC0 per MPFB2's LICENSE: "These assets have been
  released under CC0 1.0 Universal", *API*).
- **Optics for a deep iris** — Navarro's schematic eye ([`Smorodov/NavarroHumanEyeModel`](https://github.com/Smorodov/NavarroHumanEyeModel),
  MIT, `data/Navarro.dat`, *page read*): cornea front radius 7.72 mm, asphericity −0.26, thickness 0.55 mm, index 1.367;
  aqueous 3.05 mm deep, 1.3374; lens 4 mm, 1.42; vitreous 1.336; a 24 mm globe aperture. Our cornea's IOR 1.376 is the
  common Gullstrand value (our code comment). *Inference:* put the iris on a plane ~3.6 mm (0.55 + 3.05) behind the
  cornea apex, inside a sealed cornea shell, so Cycles' refraction gives the convex look; an eye add-on gives ~1.38 as
  "realistic" ([Auto Eye docs](https://superhivemarket.com/products/auto-eye/docs), *search snippet*).
- **Rendering:** Cycles refracts for real. EEVEE: Glass / Refraction "Only supports GGX … See Raytracing limitations"
  (*page read*), and a commercial eye shader says AO doesn't work through EEVEE's refraction and must be faked
  ([Real Eye docs](https://superhivemarket.com/products/real-eye-customizable-shaders/docs), *search snippet*).
  *Inference, unverified:* a transmissive cornea in Cycles can starve the iris of direct light (shadow rays blocked);
  community setups let shadow rays pass the cornea — to be tested before relying on it.

### 5b · Shaders

| Rank | Reference | What | Licence | Evidence |
|---|---|---|---|---|
| 1 | Unreal 5.8 Eye shading model + MetaHuman eye controls | Iris Mask, Iris Distance; 12 presets; iris, pupil, cornea, sclera controls; Epic calls it "highly technical" | Unreal EULA (study only) | S10, page read |
| 2 | Galacean digital-human eye (`galacean/engine-toolkit`) | sclera, iris, iris-normal, cornea-normal textures; mask R iris, G limbus, B pupil; pupil dilation; limbal ring; parallax | **MIT** (push 2026-08-03) | API, S10 |
| 3 | O3DE `Eye.materialtype` | refraction, iris, sclera, limbus | Apache-2.0 OR MIT | §6 |
| 4 | MPFB2 procedural eyes (`data/node_trees/procedural_eyes.json`) | Voronoi + math iris with bump; settings IrisMajorColor / IrisMinorColor, IrisRadialMult, IrisClockwiseMult, iris sections, PupilSize; outer layer Transmission 1.0, IOR 1.33, Clearcoat 0.4 | code GPL-3, data CC0 | page read |
| 5 | CC/iC Blender Tools (`soupday/cc_blender_tools`) | rebuilds CC's eye occlusion / tearline shaders in Blender | GPL-3.0 (push 2026-10-14) — **clean-room: do not read its shader code** (AGENTS.md) | API |

Paid Blender eye tools, for behaviour only: **EyeForge** — "Fully procedural shader", a Realistic style "using normal,
displacement, and specular maps", cornea bulge size and flat / round cornea, caruncle and tear line "imported as
separate objects", EEVEE needs ray tracing on, "Fake shadows", GPL, $16.98, Blender 4.0–5.2 (*page read*); Auto Eye,
Real Eye, Eyez, Eye Designer (*search snippet*, search 12).

### 5c · Iris textures, ranked

1. **Capture-quality research:** Bérard et al. 2014 (sclera, cornea and deforming iris captured separately); Khademi
   et al., WACV 2026, "Reconstructing Realistic and Relightable Eyes" — no code found (S10, search 12). (c2).
2. **Procedural (bucket a):** polar coordinates, radial fibres (noise stretched along the radius), a collarette ring,
   crypts (Voronoi), the pupillary ruff, limbal-ring darkening; MPFB2's node tree is a working example with CC0 data
   (*page read*). The colour model is open — no measured iris pigment model was found (Couldn't verify).
3. **Image model, zero-shot (bucket b):** prompt Z-Image-Turbo (Apache-2.0, HF *API* 2026-01-30) or FLUX.2 klein 4B
   (Apache-2.0, 2026-02-24) through stable-diffusion.cpp (MIT; supports both; LoRA "same as stable-diffusion-webui",
   README *page read*) for a flat, centred macro iris, then unwrap to polar. Not tested here.
4. **LoRA (bucket c1):** an existing one shows the idea works — "Airis eye texture" (CivitAI 87994; SD 1.5 and
   FLUX.1-dev versions; prompt a flat round iris with a centred pupil; prefers 512²) (*search snippet*); the Hugging
   Face mirror `Muapi/airis-eye-texture` labels it `openrail++` (*API*), but its base FLUX.1-dev is `other`
   (non-commercial, *API*), and the original CivitAI licence was not read. Our own LoRA would sit on:
   - **SDXL base 1.0** (OpenRAIL++-M, *API*): kohya sd-scripts — "The LoRA training can be done with 8GB GPU memory
     (10GB recommended)", with U-Net only, gradient checkpointing, cached text-encoder outputs, an 8-bit optimizer or
     Adafactor, "lower dim (4 to 8 for 8GB GPU)" ([train_SDXL-en.md](https://github.com/kohya-ss/sd-scripts/blob/main/docs/train_SDXL-en.md), *page read*) — **fits 8 GB, at the edge**.
   - **FLUX.2 klein 4B** (Apache-2.0): SimpleTuner — "~12GB" in bf16, "~8GB" in int8, "Recommended for klein-4b: Single
     16GB GPU" ([FLUX2.md](https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/FLUX2.md), *page read*) — **8 GB only in int8, borderline**.
   - **Z-Image**: SimpleTuner — "the absolute minimum is a single 3080 10G (with aggressive quantisation/offload)"
     ([ZIMAGE.md](https://github.com/bghira/SimpleTuner/blob/main/documentation/quickstart/ZIMAGE.md), *page read*) — **does not fit 8 GB**.
   - ai-toolkit (MIT) ships 24 GB example configs only (`train_lora_flux_24gb.yaml`, `train_lora_qwen_image_24gb.yaml`, *API*).
   - The training images are the open problem, not the GPU: no CC0 / CC-BY iris photo set was found (S10: iris sets
     are biometric).

---

## 6 · Teeth, gums, tongue

| Rank | Option | What / how | Bucket | Licence | Evidence |
|---|---|---|---|---|---|
| 1 | **Per-part shaders** on our GNM geometry | enamel refractive / translucent, its scattering driven by a baked **thickness map**; gums with SSS and low reflectivity "to avoid a metallic look"; tongue with SSS, rougher; a **transition mesh** between teeth and gums so screen-space scattering has no hard edge (80.lv Marmoset article); CC's teeth/gums use a scatter value for "translucency and moisture" and a gum mask; MetaHuman's teeth material has teeth, gum and plaque colours (S10) | (a) | ours | search snippet; S10 page read |
| 2 | A layered tooth model with measured optics | a Clemson thesis: an anatomically layered model with measured optical parameters; Velinov et al. 2018, in-vivo teeth appearance capture (no code) | (a) | papers | search snippet; S10 |
| 3 | Mouth-cavity darkening | *inference:* CC5 and MetaHuman darken teeth and tongue deeper in the mouth (AO / brightness controls); we have none (§1d) — an AO or vertex-colour gradient from the lips inward | (a) | ours | inference |
| Geometry | GNM teeth (80 identity components) + tongue (32 expressions) | what we use now | (a) | Apache-2.0 | §5 |
| Geometry | ICT-FaceKit teeth (4,412 v), gums and tongue | alternative | (a) | MIT | S10 |
| Geometry | MakeHuman teeth / tongue proxies | alternative | (a) | CC0 | API (MPFB2 LICENSE) |
| Geometry | BodyParts3D / Z-Anatomy | anatomical teeth, tongue, eyeball | (a) | **CC BY-SA 2.1 JP** / CC-BY-SA (share-alike) | API |
| Data | Teeth3DS(+) | 1,800 intra-oral scans; geometry only | — | **CC BY-NC-ND 4.0**; commercial use "requires a separate license" | API |
| Paid | 3D Scan Store teeth/tongue scans; Gumroad teeth node groups; "Ultra-Realistic Gum 8K" | reference | — | paid | search snippet |

---

## 7 · CC0 / CC-BY groom libraries beyond MakeHuman's

| Source | What | Licence | Commercial + redistribution | Evidence |
|---|---|---|---|---|
| MakeHuman hair-editor pack | 16 listed styles + other objects, brows, beards, lashes | CC0 | yes | measured, §5 |
| Blender demo **Hair Styles** (Daniel Bystedt) | geometry-nodes hairstyles | **CC-BY-SA** | yes, share-alike | page read ([demo files](https://www.blender.org/download/demo-files/)) |
| Blender demo **Animal Fur Examples** (Simon Thommes, Blender Studio) | fur grooms | **CC0** | yes | page read |
| Blender Studio open-movie characters | grooms inside character files | CC-BY (studio default) | not checked per file | Couldn't verify |
| Cem Yuksel HAIR models | 8 models, 10K–50K strands, `.hair` | free with a link back | unclear | S10 |
| Fab free MetaHuman groom sample | Alembic groom + head | Fab licence (not CC) | redistribution as a raw asset not checked | search snippet |
| USC-HairSalon / Hair20k | 343 / ~20K styles | **none found** | unknown | S10 |
| HairCS, DiffLocks 40K, CT2Hair, BEDLAM 2.0 | 53K / 40K / 10 / grooms | NC | no | S10, API |
| **Our own generator** (DiffLocks recipe, §3) | unlimited | ours (CC0) | yes | inference |

No CC0 / CC-BY library of realistic human grooms beyond MakeHuman's was found (search 15).

---

## 8 · Apps that do this and how they work

The leading tools the searches turned up — not an exhaustive catalogue. Studied for behaviour from public docs only.

| App | Hair: how it works | Eyes / teeth | Evidence |
|---|---|---|---|
| **MetaHuman** (Epic) | Hair, brows, lashes, beard, moustache and vellus "peach fuzz" are separate Groom Assets, each with strands, cards or meshes per LOD; LOD0 50,000 strands; Mac and mobile get cards only. Grooms are built in **Houdini** with the MH Groom tools: MH Groom Head (the standard head; Houdini 21 for custom heads), guide tools (Guide Fill, Braid, Bun, Cornrow, Guide to Tube, Cut Root, Rooter), **MH Groom Builder** (interpolation, density by attribute or texture, Number of Neighbors), **Clump Builder / Multi Clump** (primary, secondary, tertiary), Spread, Scraggle, Width, Framing, Cull, Mirror, Ambient Occlusion, Transfer RBF (moves guides between heads), **MH Groom Doctor** (checks), Alembic import/export to Unreal's groom spec; cards via Unreal's Hair Card Generator | `eyeshell`, `eyeEdge`, `saliva` meshes; 12 eye presets; teeth / plaque / gum colour controls | page read, search snippet |
| **Character Creator 5** (Reallusion) | Hair Builder: "20 pre-assembled hairstyles and 32 Hair Elements" with morphs, physics and material presets — assembled card parts, not generated (a long-time user: it "doesn't generate anything"); HD Eyes and an enhanced lash system with 3 thickness levels; Headshot (photo → head with mesh hair; v3.0 in April 2026 with a new image-to-head model) | Eye Occlusion (Blur, Shadow 1, Shadow 2, Vertex Offset) + Tear Line (moisture, Edge Fadeout); teeth / gums scatter + gum mask | page read (§5), search snippet |
| **Daz Studio** Strand-Based Hair (SBH) editor | free since 2019; tabs setup, paint, distribute, style, clump, tweak; guides spawn only at the hair cap's vertices; dForce simulates; block out at low density with large strands, finish at high density with small strands | — | search snippet |
| **Houdini** | Add Fur → **Guide Groom** (guides from skin, an internal SOP network) + **Hair Generate** (hair from skin + guides); **Guide Process** stacks Set Direction, Set Length, Lift, Straighten, Smooth, Frizz, Bend, Clump, Part, Add White Hairs, masked by ramps or painted skin attributes; Guide Deform / Simulate Guides; groom on the static mesh | — | page read |
| **XGen** (Maya) | built-in interactive grooming and instancing for hair, fur, feathers | — | search snippet |
| **Ornatrix** (Maya / Max) | a non-destructive operator stack; style, simulate, convert to XGen; renders in RenderMan, V-Ray, Redshift, Arnold | — | search snippet |
| **Yeti** (Maya) | a procedural node graph; grooms independent of topology and UVs; feathers; scripted customisation | — | search snippet |
| **Blender** | hair curves + the hair node groups (§3); Curves Sculpt brushes | — | page read |
| **Hair Tool 4** (Blender) | §3 | — | page read |
| **Digital Salon** | text → retrieval → sim → refine → AI render (§2b) | — | page read |
| **Generic AI 3D** (Meshy, Tripo, Rodin, CGTrader AI, Pixa) | text / image → mesh hair (not strands) | — | search snippet |
| **EyeForge** and other eye generators | — | §5b | page read / search snippet |
| GroomBear | **not found** (search 8 returned pet brushes; no GitHub repo) | — | — |

---

## 9 · Search log (for audit)

Searches 1–2 were narrow lookups made before the user's "plain broad searches first" note; from 3 on, each sub-topic
started broad. WebSearch calls: 19 of the 25 allowed.

| # | Tool | Query | What it returned |
|---|---|---|---|
| 1 | WebSearch | TANGLED generating 3D hair strands from images arbitrary styles github | TANGLED paper (arXiv 2502.06392, ShanghaiTech + Deemos), project page; no code link |
| 2 | WebSearch | 2026 arXiv single-image 3D strand hair generation diffusion code release | Only DiffLocks (CVPR 2025) and its project page |
| 3 | WebSearch | best AI hair generation for 3D characters 2026 | HAAR, Digital Salon (arXiv 2507.07387), Hairflow (Columbia), Reallusion Headshot, CGTrader / Pixa AI hair (mesh), vendor roundups |
| 4 | WebSearch | how to make realistic hair in Blender 5 geometry nodes groom tips | built-in hair assets, RapidHair Cards, a Blender Conference 2025 hair-sim talk, Procedural Human Hair, N_Hair_Nodes, Medusa Nodes |
| 5 | WebSearch | realistic eyebrows and eyelashes strands for 3D characters how many hairs thickness groom | MetaHuman marketplace brow grooms, an XGen brow time-lapse, Daz fibermesh brows, CC's 3 lash thickness levels; no counts |
| 6 | WebSearch | number of eyelashes upper eyelid lower eyelid eyebrow hairs count diameter anatomy StatPearls | StatPearls Eyelash: upper 90–160, lower 75–80; no brow count or diameter |
| 7 | WebSearch | Character Creator 5 Hair Builder strand hair cards how it works | Hair Builder store page (20 styles, 32 elements), forum posts, Curve-BStrands, Unreal Hair Card Generator doc |
| 8 | WebSearch | GroomBear grooming tool | nothing relevant |
| 9 | WebSearch | Daz Studio Strand-Based Hair editor how it works guides density | community SBH guides (six tabs, guides at hair-cap vertices, dForce) |
| 10 | WebSearch | Ornatrix vs Yeti vs XGen how they work guides operators node graph grooming comparison | forum and blog impressions only |
| 11 | WebSearch | CVPR 2026 hair strand reconstruction from images code github | CGHair, EfficientMonoHair, DynHair, CMU strand-accurate capture; no code links |
| 12 | WebSearch | realistic eyes Blender new techniques cornea refraction iris shader EEVEE Cycles 2026 | paid eye add-ons, BlenderArtists threads, a CC0 BlendSwap eyeball, the WACV 2026 eyes poster |
| 13 | WebSearch | AI generated iris texture for 3D eyes stable diffusion LoRA iris macro | Airis eye-texture LoRA (SD 1.5 + FLUX.1-dev), an SDXL "Eye Concept" LoRA |
| 14 | WebSearch | realistic teeth gums tongue shader Blender subsurface enamel translucency mouth interior | 80.lv Marmoset mouth article, CC4 / iClone teeth shader pages, a Blender Artists thread, a Clemson thesis, paid assets; SEO spam |
| 15 | WebSearch | free CC0 or CC-BY realistic hair groom download Blender hair curves alembic strands | Fab listings only (a free MetaHuman groom sample); no CC0 / CC-BY library |
| 16 | WebSearch | average number of hairs on human scalp and hair shaft diameter micrometres dermatology review | BioNumbers 175–300 /cm²; a clinic page 80k–150k; diameters only from low-quality pages |
| 17 | WebSearch | EEVEE realistic hair shader Principled Hair BSDF not supported workaround anisotropic strands | the EEVEE node list, Blender issue #56207; no workaround |
| 18 | WebSearch | MetaHuman groom strand count hair density LOD cards eyebrows eyelashes peach fuzz | Epic LOD spec: 50,000 / 25,000 hairstyle strands, 10,000 / 5,000 facial hair; card budgets |
| 19 | WebSearch | eye occlusion mesh and tearline in Blender realistic eyes shadow eyelid wet meniscus how to | CC3/4/5 occlusion + tearline pages, an 80.lv UE4 article, a Reallusion forum thread; no Blender tutorial |
| — | gh search repos | TANGLED hair; HairFormer hair; StrandHead; GaussianHair strand; strand-based hair; hairstyle 3D strands; hair modeling single view; groom blender; hair cards; haircards; hair card generator; procedural hair geometry nodes; eye shader blender; iris generator; realistic eye blender; Digital Salon; GroomGen; Hairmony; HairFormer; NeuralHDHair; CGHair; EfficientMonoHair; DynHair; Wispy to Voluminous; HairGPT; HairCS; GeomHair; Vid2Haircut; gaussian hair; groombear; hair tool blender; hairtool; Z-Anatomy; BodyParts3D; teeth 3d model; human eye model; Teeth3DS | StrandHead, Hairmony, GroomGen (unofficial), NeuralHDHair (no licence), CGHair and EfficientMonoHair (project pages), DynHair (placeholder), GaussianHair (HaiminLuo, no licence), Hair Tool docs, Z-Anatomy, BodyParts3D, the Navarro eye model, Teeth3DS mirrors; nothing for HairFormer, GroomBear, Wispy, HairCS |
| — | arXiv API, Semantic Scholar API | hair + strand papers 2025–2026 | arXiv 503 / "Rate exceeded"; Semantic Scholar 429 — unavailable this session |

Pages fetched directly (no search): the arXiv abs / HTML pages of DiffLocks, Digital Salon, HAAR, Perm, TANGLED,
Im2Haircut, CGHair, Wispy to Voluminous; digital-salon.github.io; MetaHuman MH Groom tools; Unreal Hair Card
Generator; Houdini fur docs; Blender demo files; the EyeForge listing; Blender manual rst (hair BSDFs, EEVEE curves and
node support, Cycles curves, hair node groups); READMEs and LICENSE files through the GitHub API; the Hugging Face model
API for SDXL, FLUX.2 klein 4B, Z-Image-Turbo, FLUX.1-dev, DINOv2, CLIP and the Airis mirror; trainer docs (kohya
sd-scripts, SimpleTuner, ai-toolkit).

---

## Couldn't verify

- **Real-hair shading numbers:** a measured table of melanin / redness per hair colour; scalp hair shaft diameter from
  a dermatology source (only low-quality pages, search 16); brow hair count and diameter; the 80k–150k scalp count at
  StatPearls itself.
- **Whether EEVEE "Strip" plus more samples fixes the thick look**, and the Cycles cornea shadow-ray issue — both are
  inferences; nothing was rendered (this task edited no file but this one).
- **The pack's modifier input values** (Blender 5.3's Python refused item access on the NodesModifier).
- **VRAM** of DiffLocks, Im2Haircut, HairGS, Digital Salon and StrandHead on 8 GB — none states it; none tested here.
- **DiffLocks' commercial terms** (Meshcapade contact only); **Im2Haircut's checkpoint terms** (no licence file);
  **the provenance of Perm's checkpoints** (USC-HairSalon has no licence).
- **Code release** of TANGLED, HairGPT, CGHair, EfficientMonoHair, Wispy to Voluminous, DynHair (placeholder),
  Hairflow, and Khademi et al. (WACV 2026) eyes.
- **Hairmony taxonomy:** whether the R-UDA covers using the attribute list (not the data).
- **The Airis LoRA's original CivitAI licence** (only a mirror's `openrail++` label was read).
- **Blender Studio character grooms** (CC-BY per file), **Microsoft Rocketbox hair cards**, the **Ten24 free head**'s
  licence, and Fab's terms for redistributing a free groom inside an open-source app.
- **GroomBear** — no trace under that name.
- **XGen, Ornatrix, Yeti** internals — forum and blog snippets only (search 10); official docs not read.
- **Blender 5.0–5.3 release notes on hair** — developer.blender.org returned 403 to the fetcher.
- **A pigment model for iris colour**, and any CC0 / CC-BY iris photo set for a LoRA.
