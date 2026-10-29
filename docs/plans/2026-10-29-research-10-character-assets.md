# Research 10 — making our own character realism: skin, eyes, lips, mouth, hair, nails, deformation (section S10)

Date: 2026-10-29. By the S10 research agent; not re-checked by the lead. For RESEARCH.md §2, §5, §7 and §8 (no
section of its own yet). Gap list: `2026-10-29-research-second-pass.md` §S10. No round-one file; this pass builds on
round one and pass 2 of CC5 (02), bases (05), building blocks (07) and standards (08), whose facts are not re-derived
here (pointers given where they matter).

**Scope.** The S10 list, widened by the user mid-pass (via the lead), verbatim: "not just mesh skin eys, i mean all
of the character realism hair the whole human" and "like teeth lips". So every part — skin; eyes (iris, sclera,
cornea, wetness, occlusion/tearline); lips; mouth interior (teeth, gums, tongue); hair of every kind (scalp, brows,
lashes, beard and stubble, body hair, vellus); nails; and how the whole human moves (face rig, wrinkle maps, body
correctives, skin deformation) — each judged against CC5 and MetaHuman with the user's order "reuse if it meets the
bar, otherwise build".

**Labels.** Every fact carries its source, the source's date ("undated" when the page shows none; for GitHub, the
repo's last push as the API reported it on 2026-10-29), and one of:
- **[P] page read**: read at the primary page, the repo's README / licence file / source file (GitHub through
  `gh api`, read-only GETs), a Hugging Face model or dataset card or API record, arXiv's export API, or a docs
  source repo (Blender's manual on projects.blender.org).
- **[S] search snippet only**: seen only in a search result; not confirmed at its page.

Lines starting "Assessment:" are my judgement, not facts. Licences are one-line labels; "NC" = non-commercial.

**Method.** About 75 WebSearch calls (of ~200 allowed); the rest through WebFetch, `gh api` (repo metadata,
READMEs, licence files, trees, code search), Hugging Face's public API and raw model/dataset cards, arXiv's export
API and Blender's manual source. No datasets, models, weights or installers were downloaded; scratch files only in
the session scratchpad on F:. Not worked around: gated Hugging Face repos (FLUX.3 Image Klein's licence file, Fibo
2.0), dataset request forms (NeRSemble, RenderMe-360, FaceScape, FaceVerse, DiffLocks). Several Epic docs pages
rendered empty to the fetcher (Alembic groom *specification* page, Material Overrides, Skin Material Controls);
sibling pages were used instead.

## Top findings

1. **The large datasets exist, but nearly all of them are research-only, and most are below the bar's
   resolution.** Face/skin: FFHQ-UV (50,000+ UV maps), FFHQ-UV-Intrinsics (10K subjects, 1K PBR maps, CC BY-NC-ND),
   FaceScape (16,940 models, 4K maps, NC), FaceVerse (2,688 scans, NC, "as training data for a commercial product"
   forbidden), Multiface (13 people, 65 TB, 1K textures, CC BY-NC), Ava-256 and Goliath (CC BY-NC), NeRSemble (220+
   heads, request form), RenderMe-360 (500 people, signed agreement), MERL/ETH skin reflectance (149 people,
   non-profit). Hair: HairCS (53,336 grooms, CC BY-NC 4.0, 2026-09), DiffLocks (40K, NC), Hair20k / USC-HairSalon
   (no clear licence). — sources in §1 [P]
2. **No free, commercially usable textured head-scan set at scale was found.** Free scans are single heads under NC
   terms (Ten24 / 3D Scan Store 8K female head; Digital Emily 2); the one permissive scan is Lee Perry-Smith's
   "Infinite" head (CC BY 3.0, shipped in three.js). Permissive skin material is tileable or low-res: MakeHuman Skins
   01–03 (CC0), TextureCan (site-wide CC0). Paid stores (Triplegangers 1,950+ people, Texturing XYZ, deep3dstudio
   "For non-AI use only", Meshcapade) are out. — §1 [P/S]
3. **No open UV-space face-texture generator with released weights and a permissive licence meets the bar.** FreeUV
   (CVPR 2025) is CC BY-NC-SA 4.0 (SD1.5-based); AvatarMe++ "has been commercialized and is not released publicly";
   MoSAR released only its dataset; UltrAvatar's repo has no licence; USC ICT's 2025 generator (44K faces → 4K
   albedo/specular/displacement) released nothing; UVAPM is MIT but albedo only. — §2 [P]
4. **General image models are the reusable AI layer, and the family's stable-diffusion.cpp runs them on every GPU
   vendor.** Artificial Analysis' open-weights board (human-preference Elo, read 2026-10-29): FLUX 3 Image Klein
   1043 (flux-kommunity licence, gated, unread), Qwen-Image-2.1 1042 (Qwen Research licence: non-commercial),
   HiDream-O1-Image-Dev (MIT), Z-Image Turbo 936 (Apache-2.0), Qwen-Image 903 (Apache-2.0), FLUX.2 klein 4B 837
   (Apache-2.0); Qwen-Image-Edit 2509/2511 Apache-2.0. stable-diffusion.cpp (MIT) runs all of these on CPU, CUDA,
   Vulkan, Metal, OpenCL and SYCL, and says Z-Image runs "on GPUs with 4GB of VRAM — or even less". — §2 [P]
5. **Every image-to-strand hair model found is non-commercial or unlicensed, CUDA-only and tested on A100s.**
   HAAR (research licence, A100 40 GB), HairStep (CC BY-NC 4.0), Im2Haircut (no licence, A100), GaussianHaircut and
   DiffLocks (NC); HairGPT (2026) has no code. Permissive: Perm (MIT, a parametric strand representation — needs
   CUDA and NVIDIA's StyleGAN ops) and HairGS (MIT, multi-view reconstruction). — §2 [P]
6. **Unreal imports strand grooms from USD as well as Alembic.** Epic: "Groom assets (static and baked animation)
   are imported from USD BasisCurves with the custom GroomAPI schema"; an Epic engineer (2026-08-18) says the schema
   tells the importer to read the `groom_*` attributes. The Alembic spec (UE 5.8) is groom schema 1.5:
   `groom_version_major/minor`, `groom_guide`, `groom_group_id`, `groom_root_uv`, `groom_id`, `groom_color`,
   `groom_closest_guides`, `groom_guide_weights`, `groom_width` (default 1 cm). — §5 [P]
7. **MetaHuman's texture set is now documented, and its Texture Override takes our maps.** Face: Basecolor Baked,
   SRMF Baked (specular, roughness, metallic, fuzz), Normal Baked, Normal LOD 256², Scatter 512², Basecolor
   Animated Delta 512², Normal Animated Delta 1K; texture sources 2K/4K/8K; UE Cine bakes "up to 8K". Texture
   Override accepts face base colour, normal, cavity and animated maps, and body base colour, normal and cavity. —
   §4–5 [P]
8. **Eyes: Unreal itself warns against building an eye shader, and open references exist.** Unreal 5.8's Eye
   shading model is "tightly coupled to the shader code, the Material, the geometry, and the UV layout". MIT
   references: Galacean's digital-human eye, hair and SSS shaders (`galacean/engine-toolkit`), O3DE's eye material
   (round one), and ICT-FaceKit's full eye stack of meshes (eyeballs, lacrimal fluid, eye blend, eye occlusion, lash
   strips). MetaHuman's eye controls are listed in full (12 presets; iris, pupil, cornea, sclera). — §3 [P]
9. **Teeth, gums and tongue have no open appearance model or data; geometry exists.** Velinov et al. 2018 (teeth
   appearance capture) released no code. GNM Head (Apache-2.0) has 80 teeth identity and 32 tongue expression
   components (pass-2 S4); ICT-FaceKit has teeth, gums and tongue meshes (MIT); OmniFaceRig (2026-06) procedurally
   fits teeth, gums and tongue but released no code. — §3 [P]
10. **Face rig generation from a neutral mesh is research with restrictive or missing code.** TopoRig (2026-09,
    from ICT's 53-control vocabulary) is under an "Academic Use License"; RigAnyFace (NeurIPS 2025) and
    OmniFaceRig (up to 155 blendshapes) have no code. OpenRigLogic's design doc confirms MetaHuman wrinkles are
    "animated mask multipliers" from RigLogic's conditional stage. — §3 [P]
11. **Wrinkle maps have a standard technique and recent open papers.** Mesh-tension blending of stretched and
    compressed maps (Oat; Jimenez; Raman et al. WACV 2023; Blender Studio's procedural wrinkles); Disney's
    graph-based micro-wrinkle synthesis (SGP 2023) runs at "real-time framerates". A patent on tension-map wrinkle
    blending (US 12062140) exists — a label, not analysed. — §3 [P/S]
12. **Physically based colour: hair has an open, published formula; skin does not.** Blender's manual gives the
    Principled Hair melanin and pheomelanin absorption coefficients (from d'Eon 2011 and Chiang 2016); MetaHuman's
    lash material uses the same Melanin and Redness controls. Skin chromophore models (Jimenez 2010, Donner 2008,
    Aliaga 2023) have papers but no open real-time code (SkinOptics, GPL-3.0, is offline colorimetry). — §3 [P]
13. **Body deformation: reusable open pieces exist; muscle and skin-sliding do not.** Dem Bones (BSD-3, EA),
    complementary dynamics (MIT), Jolt's skinned soft-body constraints (v5.0.0) and MIT jiggle add-ons; Ziva was
    discontinued 2024-04-02; no open muscle or skin-sliding library found. — §3 [P/S]
14. **No source compares any open asset, dataset or generator with CC5 or MetaHuman.** The closest is USC ICT's
    2025 user study (87 people, against DreamFace and Describe3D). MetaHuman appears in papers only as a framework or
    a foil ("limited preset assets"). — §4 [P]
15. **Upscaling to 8K: permissive upscalers exist, but both reference apps get pore detail from tiled micro-normal
    maps, not from upscaling.** Real-ESRGAN (BSD-3), SwinIR (Apache-2.0), SeedVR2 (Apache-2.0, H100-class),
    AuraSR-v2 (Apache-2.0); SUPIR and 4x-UltraSharp are NC. CC5's Micro Normal tiling default is 42 on body meshes;
    MetaHuman has "Micro Skin Detail normals". — §2, §4 [P]

## 1 · Datasets

### 1a · Face and head: scans, multi-view capture and UV textures

- **FFHQ-UV** (`csbhr/FFHQ-UV`, CVPR 2023): "over 50,000 high-quality texture UV-maps with even illuminations,
  neutral expressions", made from FFHQ through StyleGAN editing; about 1K extra samples added "to alleviate the data
  biases … (e.g., dark-skinned faces)". Repo MIT; the Hugging Face mirror (`csbhr/FFHQ-UV`, 2026-04-16) is tagged
  `license:mit`. Map resolution is not stated in the README or abstract. — [README](https://github.com/csbhr/FFHQ-UV),
  [dataset README](https://github.com/csbhr/FFHQ-UV/blob/main/README_dataset.md), [HF](https://huggingface.co/datasets/csbhr/FFHQ-UV),
  [arXiv 2211.13874](https://arxiv.org/abs/2211.13874), repo push 2026-04-16 [P]
  - Conflict to label, not settle: its source, FFHQ, says its image licences "allow free use, redistribution, and
    adaptation for non-commercial purposes" — [FFHQ README](https://github.com/NVlabs/ffhq-dataset), push 2022-11-18 [P]
- **FFHQ-UV-Intrinsics** (Ubisoft La Forge, `ubisoft/ubisoft-laforge-MoSAR`): "diffuse, specular, ambient occlusion,
  translucency and normal maps for 10K subjects" at 1K, made by running MoSAR at 512² and upscaling; registered to
  the HiFi3D topology. "Creative Commons Attribution-NonCommercial-NoDerivatives"; "can only be used for research
  purpose". — [README](https://github.com/ubisoft/ubisoft-laforge-MoSAR), created 2024-02-06, push 2024-03-25 [P]
- **FaceScape** (NJU): 16,940 topologically uniform models (847 identities × 20 expressions) "with displacement map
  and texture map", "4K dp/tex maps"; >400k multi-view images; "only released for non-commercial research use";
  licence key on request; site moved to nju-3dv.github.io/projects/FaceScape/ (2026-01-27). —
  [README](https://github.com/zhuhao-nju/facescape), push 2026-01-27 [P]
- **FaceVerse-Dataset** (Tsinghua): 2,688 head scans (21 expressions × 128 identities, East Asian) from a DSLR rig;
  per scan an .obj, a JPEG texture and a fitted .ply. Non-commercial research only, explicitly including "as
  training data for a commercial product"; the agreement must be signed by "a full-time academic staff member". —
  [README](https://github.com/LizhenWangT/FaceVerse-Dataset), push 2024-07-10 [P]
- **Multiface** (Meta, archived): 13 identities, 40–160 views, 2048 × 1334 images, tracked meshes, "unwrapped
  textures at 1024 × 1024", audio; 65 TB; "CC-BY-NC 4.0". — [README](https://github.com/facebookresearch/multiface), push 2023-08-01 [P]
- **Ava-256** (Meta): 256 paired dome and headset captures, 4–32 TB; "CC BY-NC 4.0". —
  [README](https://github.com/facebookresearch/ava-256), push 2025-06-17 [P]
- **Goliath** (Meta): per subject a relightable head, relightable hands, clothed and minimally clothed captures plus
  mobile versions; LICENSE "Attribution-NonCommercial 4.0"; "a pre-release". —
  [README / LICENSE](https://github.com/facebookresearch/goliath), push 2024-12-04 [P]
- **NeRSemble** (TUM): "more than 220 human heads", 16 cameras at 7.1 MP, "over 4700 … sequences" at 73 fps; access
  through a form; no licence stated on the page or in `nersemble-data`. —
  [project](https://tobias-kirschstein.github.io/nersemble/), undated; [nersemble-data](https://github.com/tobias-kirschstein/nersemble-data), push 2025-12-19 [P]
- **RenderMe-360**: 500 identities, 60 cameras at 2448 × 2048, 30 fps; scan mesh, UV map and 0.6M FLAME fits
  listed; to get data, "sign the downloaded License Agreement" and e-mail from an institution address with the
  research purpose. — [site](https://renderme-360.github.io/), [download](https://renderme-360.github.io/inner-download.html), undated;
  [repo](https://github.com/RenderMe-360/RenderMe-360), push 2024-06-18 [P]
- **ICT Face Model** (USC ICT): "Light" has 100 identity shape modes, **0 albedo modes**, 53 expressions; "Full" has
  200+ shape and 200+ albedo modes, an FBX rig, and albedo-to-specularity and albedo-to-displacement inference; the
  high-resolution 3DMM "for commercial use" is by contact. — [VGL page](https://vgl.ict.usc.edu/Data/ICTFaceModel/), © 2008–2019 [P]
  - ICT-FaceKit (the MIT Light release) ships geometry, not textures: face, mouth socket, eye sockets, gums and
    tongue (2,977 v), teeth (4,412 v), eyeballs (1,570 v each), lacrimal fluid (204 v), eye blend (24 v), eye
    occlusion (152 v), eyelash poly strips (684 v), and a UV layout. — [README](https://github.com/USC-ICT/ICT-FaceKit), push 2020-12-01 [P]
  - ICT's paid light-stage service delivers 6K diffuse albedo, specular albedo, normals, displacement and AO per
    expression — [VGL production](https://vgl.ict.usc.edu/production.php) [S]
- **RealFaceDB** (Imperial): 7,500 anonymised patches of diffuse albedo, diffuse normal, specular albedo, specular
  normal and shape; the licence must be signed by full-time academic staff. — [paperswithcode](https://www.paperswithcode.com/dataset/realfacedb) [S]
- **Morphable Face Albedo Model** (Smith et al., CVPR 2020): diffuse and specular albedo model from 50 light-stage
  scans plus 23 3DRFE scans, made to replace the Basel Face Model's texture model. — [arXiv 2004.02711](https://arxiv.org/abs/2004.02711) [S]
- **Digital Emily 2** (Wikihuman / USC ICT, 2015-05-29): Alembic model, EXR textures, OSL shader, a Maya/V-Ray scene;
  head and skin only ("eyes and hair data will be provided" later); free "for any non-commercial use". —
  [AWN](https://www.awn.com/news/digital-human-league-releases-first-batch-data-digital-emily-2) [P]
- **Ten24 / 3D Scan Store free female head** (2023-09-21): ZTL, OBJ, FBX; teeth, tongue, eyeballs, lenses, wet
  lines, lashes and brows as separate meshes; 8,192² albedo, normal, displacement (also 16-bit TIFF), roughness and
  specular; "isn't licensed for commercial use" (private, non-commercial, internal tests). —
  [CG Channel](https://www.cgchannel.com/2023/09/download-ten24s-free-hi-res-3d-scan-of-a-female-human-head/) [P]
- **Lee Perry-Smith "Infinite" head**: "licensed under a Creative Commons Attribution 3.0 Unported License. Based on
  a work at www.triplegangers.com"; three.js ships it with colour, specular, 4096 displacement and tangent-normal
  maps. — [three.js licence file](https://github.com/mrdoob/three.js/tree/dev/examples/models/gltf/LeePerrySmith), read 2026-10-29 [P]
- No CC BY / CC0 textured head-scan *dataset* found; free ones found are CC BY-ND (Second Chance Games head) or
  CC BY-NC-ND (Nexdata sample); Headspace (York) is "non-commercial, University-based research use only". —
  [CG Channel 2015](https://www.cgchannel.com/2015/06/download-a-high-resolution-3d-scan-of-a-female-head/), [Headspace](https://www-users.york.ac.uk/~np7/research/Headspace) [S]

### 1b · Close-up skin and reflectance

- **MERL/ETH Skin Reflectance Database** (Weyrich et al. 2006): measurements of 149 people varying in age, gender
  and race — [MERL TR2006-071](https://www.merl.com/publications/docs/TR2006-071.pdf) [S]. Now an archival mirror at
  UCL; use "for educational, research and non-profit purposes", commercial use needs MERL's permission; "may not be
  reposted". — [UCL mirror](https://reality.cs.ucl.ac.uk/projects/facescan/skin-reflectance-db/), undated [P]
- **PorePatch** (arXiv 2512.00381): about 10 million pore-scale patches from 257 identities, cut from NeRSemble — a
  matching benchmark, not displacement data. **MicroGlam** (arXiv 2401.05339): microscope patches of hand skin with
  and without cosmetics, 16 LED directions; the arXiv paper is CC BY-NC-ND 4.0 (dataset terms not checked). — [arXiv 2512.00381](https://arxiv.org/abs/2512.00381v1), [arXiv 2401.05339](https://arxiv.org/html/2401.05339v1) [S]
- No released skin *displacement* dataset found; ICT's skin-stretch and microgeometry pages mention no data release. —
  [ICT SkinStretch](https://vgl.ict.usc.edu/Research/SkinStretch) [S]
- Permissive skin material: MakeHuman "Skins 01 / 02 / 03" (natural female, natural male, non-natural), CC0, May 2023
  — [asset packs](https://static.makehumancommunity.org/assets/assetpacks.html) [S]; OpenGameArt CC0 derivatives at 2048²
  [S]; SMOKEWORKS Skins Vol.0/1 at 4K, CC BY 4.0 [S]; TextureCan's tileable "Human Face Skin Texture (Skin 0001)" under
  the site-wide "CC0 1.0" terms — [terms](https://texturecan.com/terms/) [S].

### 1c · Body textures

- **ATLAS** (TexDreamer, ECCV 2024): 50,000 SMPL-UV textures at 1024² with text descriptions — [arXiv 2403.12906](https://arxiv.org/abs/2403.12906) [P].
  Its Hugging Face card is tagged `cc-by-4.0` (2024-07-12) — [HF](https://huggingface.co/datasets/ggxxii/ATLAS) [P] —
  while the ECCV page says "available for research purposes" [S]: a conflict to label. Code `ggxxii/texdreamer` MIT
  (push 2025-02-15) [P].
- **SMPLitex**: SMPL texture dataset on its project page; repo has no licence file. — [repo](https://github.com/dancasas/SMPLitex), push 2024-02-07 [P]
- **BEDLAM** body textures: 7 ethnicities, 50 female + 50 male, minimal clothing; CC BY-NC 4.0, commercial via
  Meshcapade. BEDLAM 2.0's strand grooms are "for non-commercial use only". — [BEDLAM download](https://bedlam.is.tue.mpg.de/download.html),
  [BEDLAM2.0 arXiv 2511.14394](https://arxiv.org/pdf/2511.14394) [S]

### 1d · Large human-image sets (for training an own generator)

- **FFHQ**: 70,000 PNGs at 1024², Flickr images under CC BY 2.0, CC BY-NC 2.0, PDM, CC0 or US-Gov licences —
  "free use … for non-commercial purposes"; not for face recognition. — [README](https://github.com/NVlabs/ffhq-dataset), push 2022-11-18 [P]
- **Face Synthetics** (Microsoft): 100,000 synthetic faces at 512², landmarks and segmentation; "non-commercial
  research". — [README](https://github.com/microsoft/FaceSynthetics), push 2025-07-08 [P]
- **SynthHuman** (Microsoft, DAViD): about 300,000 synthetic renders (100K each of face, upper body, full body) with
  alpha, depth, normals and intrinsics; dataset **CDLA-2.0 (Permissive)**, code and models MIT. Rendered images
  only — the 548 strand hair models and face scans used to make it are not released. The paper credits synthetic
  data with "strong guarantees for data provenance, usage rights, and user consent". —
  [README](https://github.com/microsoft/DAViD), push 2026-07-10; [card](https://docs.voxel51.com/dataset_zoo/datasets_hf/synthhuman.html);
  [arXiv 2507.15365](https://arxiv.org/abs/2507.15365), 2025-07-21 [P]

### 1e · Hair

- **HairCS** (Utah, LIGHTSPEED, UCLA; arXiv 2609.16465, 2026-09-15): 53,336 strand grooms in 13 versions (base,
  curly profiles, blends; short, bob, shoulder, long), each 60,000 strands × 64 samples (float16), with previews,
  labels and a shared head/scalp OBJ; **CC BY-NC 4.0**. — [HF card](https://huggingface.co/datasets/HairCS2027/HairCS), 2026-09-14 [P]
- **DiffLocks**: 40K synthetic Blender hairstyles, NC licence, commercial via Meshcapade (pass-2 S4); repo push
  2025-10-31 [P].
- **USC-HairSalon**: 343 hairstyles, 10,000 strands each, 100 points per strand, "collected from online game
  communities"; no licence found — [Neural Haircut supp.](https://openaccess.thecvf.com/content/ICCV2023/supplemental/Sklyarova_Neural_Haircut_Prior-Guided_ICCV_2023_supplemental.pdf) [S].
  **Hair20k** (~20k, an augmented USC-HairSalon) is Perm's training set — [Perm README](https://github.com/c-he/perm), push 2026-07-11 [P].
- **Cem Yuksel's HAIR files**: 8 models (three at 50,000 strands, others 10,000–15,000); binary `.hair` format
  (128-byte header, segments, points, thickness, transparency, colour); "for your personal or research projects", with
  a link back. — [page](https://cemyuksel.com/research/hairmodels/), undated [P]
- **CT2Hair** (10 CT-scanned wigs, CC BY-NC) and **MakeHuman's CC0 hair-editor pack** (7 styles) — pass-2 S4, not
  re-derived. BEDLAM 2.0 grooms NC (above).

### 1f · Eyes, teeth, tongue

- No open eye-appearance dataset found; iris image sets are biometric (GAN survey). — [arXiv 2404.17105](https://arxiv.org/pdf/2404.17105) [S]
- **Teeth3DS(+)**: 1,800 intra-oral scans of 900 patients, 23,999 annotated teeth (geometry, no appearance); licence
  not confirmed. — [arXiv 2210.06094](https://arxiv.org/abs/2210.06094v3) [S]
- **G-OBIM**: an open finite-element tongue model of one male speaker from MRI, "freely available, along with the
  data". — [PMC12440228](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12440228/) [S]

### 1g · Paid only — out (one line each)

- Triplegangers: 1,950+ individuals × ~21 expressions, 40,000+ scans, sold with a commercial licence — [blog](https://triplegangers.com/blog) [S].
- Texturing XYZ: skin displacement and albedo maps, separate commercial and non-commercial licences — [3dvf](https://3dvf.com/actualite-24470-texturing-xyz-se-met-a-jour-avec-visages-pre-deplies-html/) [S].
- 3D Scan Store / Ten24 paid scans (free sample is NC, above); deep3dstudio scans, "For non-AI use only" — [CGTrader listings](https://www.cgtrader.com/3d-models/character/man/asian-male-30s-head-scan-037) [S].
- Meshcapade texture packs and SMPL commercial licences (Micro €1,500 a year) — [Meshcapade](https://meshcapade.com/assets/body-models) [S].

Assessment: the user's "i bet there are large datasets that exist" holds for size — tens of thousands of UV maps,
grooms and multi-view captures. Two things stand against reusing them as they are: (1) their resolution — the PBR
sets are 1K (FFHQ-UV-Intrinsics, Multiface), only FaceScape (4K) and single free heads (8K) approach CC5's and
MetaHuman's 8K; (2) their terms — almost all are non-commercial, several forbid training a commercial product, and
two carry conflicting labels (FFHQ-UV, ATLAS). Microsoft's DAViD shows the alternative the field uses when terms
matter: generate the training data procedurally.

## 2 · AI generators

### 2a · General image models (the "AI that generate human images with all sorts of options")

- Artificial Analysis open-weights text-to-image board (AA-Image-T2I v2.1, "Elo from pairwise human preference
  votes", page undated, read 2026-10-29): 1 FLUX 3 Image Klein 1043 (Oct 2026), 2 Qwen-Image-2.1 1042, 3 Fibo 2.0
  1039, 4 Ideogram 4.0 Quality 1026, 6 FLUX.2 [dev] 1000 (anchor), 9 Cosmos3-Super 993, 11 HunyuanImage 3.0 Instruct
  987; Z-Image Turbo 936 (rank 18–20); FLUX.2 klein 9B 929, 4B 837; Qwen-Image (Aug 2025) 903. Not a skin-specific
  test. — [leaderboard](https://artificialanalysis.ai/image/leaderboard/text-to-image/open-weights) [P]
- Licences from the Hugging Face API (2026-10-29) [P]:
  - Apache-2.0: Z-Image and Z-Image-Turbo (2026-01), Qwen-Image (2025-08), Qwen-Image-Edit, -2509, -2511 (to
    2025-12), FLUX.2-klein-4B (2026-02), FLUX.1-schnell, Chroma1-HD, AuraSR-v2.
  - MIT: HiDream-I1-Full; HiDream-O1-Image-Dev (~8.8B parameters, 2026-06).
  - OpenRAIL++: SDXL base.
  - Non-commercial: Qwen-Image-2.1 "Qwen Research License" ("FOR NON-COMMERCIAL PURPOSES ONLY" —
    [LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1/raw/main/LICENSE)); FLUX.1-Kontext-dev "non-commercial".
  - Not read (gated): FLUX 3 Image Klein (`flux-kommunity-license`, ~5.5B), Fibo-2.0-dev (`bria-fibo`), FLUX.2-dev
    and FLUX.2-klein-9B ("other"). Cosmos3-Super-Text2Image: `openmdw1.1` (~64.6B). HunyuanImage-3.0-Instruct
    "other" (~83B).
- **stable-diffusion.cpp** (MIT, 7,824 stars, push 2026-10-29): SD1.x–3.5, FLUX.1, FLUX.2, FLUX.3 Klein, Qwen Image
  (2.1), Z-Image, Chroma, HiDream-O1-Image and others; edit models (Kontext, Qwen Image Edit); PhotoMaker,
  IP-Adapter (SD1.5/SDXL), ControlNet (SD1.5 only), ESRGAN/MoSR upscaling; back-ends CPU, CUDA, Vulkan, Metal,
  OpenCL, SYCL. Z-Image: "GPUs with 4GB of VRAM — or even less"; PhotoMaker on ≤ 8 GB: use `--vae-on-cpu`. —
  [README](https://github.com/leejet/stable-diffusion.cpp), [docs/z_image.md](https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/z_image.md),
  [docs/photo_maker.md](https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/photo_maker.md) [P]
- Skin realism of Z-Image Turbo in reviews: "plastic skin mostly gone" and 16 GB in PyTorch; anecdotal, no
  controlled skin test found. — [Decrypt](https://decrypt.co/350572?amp=1), [getimg.ai](https://getimg.ai/blog/z-image-turbo-review-how-this-small-ai-model-delivers-big-results) [S]

### 2b · Face textures in UV space (albedo and PBR)

- **FreeUV** (CyberAgent / Tsukuba, CVPR 2025): photo → UV texture with Stable Diffusion 1.5 (`pipeline_sd15.py`)
  and a cross-assembly of appearance and structure networks; LICENSE.txt **CC BY-NC-SA 4.0**; checkpoints on Google
  Drive. — [repo](https://github.com/YangXingchao/FreeUV), push 2025-06-18; [arXiv 2503.17197](https://arxiv.org/abs/2503.17197) [P]
- **AvatarMe / AvatarMe++** (Imperial): up to 6K × 4K diffuse albedo, specular albedo, diffuse and specular normals;
  "This model has been commercialized and is not released publicly". — [repo](https://github.com/lattas/AvatarMe), push 2023-10-06 [P]
- **MoSAR** (Ubisoft): diffuse, specular, AO, translucency and normal maps from one portrait; only the dataset repo is
  public. — [arXiv 2312.13091](https://arxiv.org/abs/2312.13091), 2023-12-20; [repo](https://github.com/ubisoft/ubisoft-laforge-MoSAR) [P]
- **UltrAvatar** (2024-01): diffuse-colour extraction plus an "authenticity guided texture diffusion model" for PBR
  maps — [arXiv 2401.11078](https://arxiv.org/abs/2401.11078) [P]; repo `USRC-SEA/UltrAvatar` has no licence file, 8
  stars, push 2024-09-19 [P].
- **USC ICT 2025** ("Bringing Diversity from Diffusion Models to Semantic-Guided Face Asset Generation"): 44K
  albedo/geometry pairs made with a diffusion model and normalised to scan quality; a GAN generator outputs "4K
  geometry, albedo, specular and displacement maps in the UV space" (1K albedo → super-resolution); refinement adds
  eyeballs, teeth and gums; no code, weights or data release stated. — [arXiv 2504.15259 v2](https://arxiv.org/html/2504.15259v2), 2025-04-21 [P]
- **Geometry-aware texture generation with artist control** (arXiv 2505.04387, 2025-05-07): learns geometry–texture
  correlations by demographic; skin-tone change and wrinkle/facial-hair edits propagate across all maps; code not
  checked. — [arXiv](https://arxiv.org/abs/2505.04387) [P]
- **UVAPM** (2025): UV albedo parametric model plus a VAE detail generator (wrinkles, whiskers, spots); MIT. —
  [repo](https://github.com/wangalong-ahpu/UVAPM), push 2026-07-16 [P]
- **FFHQ-UV's pipeline** (MIT code) makes UV maps from single photos with StyleGAN2 editing and its own texture GAN —
  [README](https://github.com/csbhr/FFHQ-UV) [P]; it needs NVIDIA's StyleGAN2 FFHQ checkpoint (listed in the HF
  mirror's files) [P].
- **Relightify** (ICCV 2023): diffusion trained on UV reflectance (diffuse, specular, normals) inpaints from one
  photo — code not checked. — [paper](https://openaccess.thecvf.com/content/ICCV2023/papers/Papantoniou_Relightify_Relightable_3D_Faces_from_a_Single_Image_via_Diffusion_ICCV_2023_paper.pdf) [S]
- Photo-to-face fitting code with permissive code licences (models depend on BFM/FLAME data, see §5 of RESEARCH):
  HRN Apache-2.0, 3DDFA-V3 MIT, SMIRK MIT; MICA, EMOCA, DECA "NOASSERTION". — GitHub API, 2026-10-29 [P]

### 2c · Body textures

- **TexDreamer** (ECCV 2024): text or image → SMPL UV texture through a fine-tuned text-to-image model; code MIT;
  ATLAS data (§1c). — [arXiv 2403.12906](https://arxiv.org/abs/2403.12906), [repo](https://github.com/ggxxii/texdreamer) [P]
- **UVMap-ID** (ACM MM 2024): identity-personalised SMPL UV maps from a fine-tuned diffusion model; repo has no
  licence. — [arXiv 2404.14568](https://arxiv.org/pdf/2404.14568) [S], [repo](https://github.com/twowwj/UVMap-ID) [P]

### 2d · Material maps from images (de-lighting, normals, tileable PBR)

- Marigold IID appearance and lighting v1-1 and Marigold normals v1-1: OpenRAIL++ (2025-05-20). StableNormal v0-1:
  Apache-2.0. StableMaterials (tileable PBR): OpenRAIL. DreamMat (geometry-aware PBR for meshes, SIGGRAPH 2024): MIT.
  — HF API and GitHub API, 2026-10-29 [P]

### 2e · Upscaling toward 8K

- Real-ESRGAN BSD-3-Clause (push 2024-08-06); SwinIR Apache-2.0; AuraSR-v2 Apache-2.0; SeedVR / SeedVR2
  Apache-2.0 — "1 H100-80G can handle videos with 100x720x1280"; SUPIR: "Non-Commercial Use Only Declaration", low-VRAM
  mode 12 GB + 16 GB; 4x-UltraSharp CC BY-NC-SA 4.0. stable-diffusion.cpp runs ESRGAN and MoSR models. —
  [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN), [SeedVR](https://github.com/ByteDance-Seed/SeedVR), [SUPIR](https://github.com/Fanghua-Yu/SUPIR),
  [sd.cpp esrgan.md](https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/esrgan.md) [P]

### 2f · Image to strand hair

- **HAAR** (CVPR 2024, text → strands): "available for scientific research purposes"; tested on "an NVIDIA A100
  40GB". — [README](https://github.com/Vanessik/HAAR), push 2024-10-09 [P]
- **HairStep**: LICENSE "Attribution-NonCommercial 4.0"; its HiSa/HiDa data and checkpoints "non-commercial research
  purposes only"; CUDA 11.1. — [README](https://github.com/GAP-LAB-CUHK-SZ/HairStep), push 2026-03-30 [P]
- **Im2Haircut** (ICCV 2025, single view): no licence file; CUDA 11.8; "tested on NVIDIA A100". —
  [README](https://github.com/Vanessik/Im2Haircut), push 2026-02-02 [P]
- **Perm** (Yale/Adobe…, MIT): PCA-based parametric strand model; fitted parameters for all 343 USC-HairSalon styles;
  needs CUDA ≥ 11.3 for EG3D/StyleGAN3 ops; PCA fitting wants ~64 GB RAM; a re-implementation of its single-view
  pipeline "with a public license" is still unticked. — [README](https://github.com/c-he/perm), push 2026-07-11 [P]
- **HairGS** (MIT): strands from multi-view images (COLMAP), CUDA. — [repo](https://github.com/yimin-pan/hair-gs), push 2026-04-01 [P]
- GaussianHaircut (video, NOASSERTION; round one: CC BY-NC-SA) and DiffLocks (NC, custom CUDA kernels; pass-2 S7).
  GeomHair (strands from colourless scans, NOASSERTION), Vid2Haircut (EG 2026, no licence) — GitHub API [P].
- **HairGPT** (ShanghaiTech + Deemos, arXiv 2605.08824, May 2026): no code found. — [emergentmind](https://www.emergentmind.com/papers/2605.08824) [S]
- **HairCS** (cards → strands, arXiv 2609.16465): output "compatible with … common grooming modifiers (e.g.,
  clumping, curling, noise)"; dataset NC (§1e). — [arXiv](https://arxiv.org/abs/2609.16465) [P]
- **Wispy to Voluminous** (arXiv 2606.08041, 2026-06-06): beard, mustache, lashes and brows as strands from
  multi-view images, via 3D Gaussians → curves. — [arXiv](https://arxiv.org/abs/2606.08041) [P]

Assessment: the AI layer we can reuse under clear terms is general (image generation and editing, de-lighting,
normals, upscaling), not character-specific. Every model that writes UV-space PBR maps or strand grooms is
non-commercial, unlicensed or unreleased; and none is documented to run through stable-diffusion.cpp or off NVIDIA. A character
texture generator is therefore ours to build: an Apache/MIT image model (Z-Image, Qwen-Image, FLUX.2 klein 4B,
HiDream-O1) for identity and variety → our own projection into our UV layout → our own intrinsic split (Marigold-type,
or a model we train on procedurally rendered data) → procedural micro detail for 8K.

## 3 · Building blocks for our own generators

### 3a · Skin colour, pores and wrinkles

- **Jimenez et al. 2010**, "A Practical Appearance Model for Dynamic Facial Color" (TOG 29(5), SIGGRAPH Asia): "a
  real-time dynamic appearance model of skin built from in vivo measurements of melanin and hemoglobin
  concentrations", with a "skin appearance rig" coupled to the facial rig; "negligible overhead"; downloads are the
  PDF, slides and a movie — no code. — [iryoku.com/skincolor](https://www.iryoku.com/skincolor/) [P]
- **Aliaga, Hery, Xia 2022** (arXiv 2201.10695): Monte Carlo over a biophysical layered skin model, learning the
  inverse map from RGB albedo to skin properties; handles lips and imperfections; the albedo "can be robustly edited
  through meaningful biophysical properties". — [arXiv](https://arxiv.org/abs/2201.10695), 2022-01-26 [P]. Follow-up
  "A Hyperspectral Space of Skin Tones…" (CGF 42(4), EGSR 2023): melanin, haemoglobin, oxygenation,
  eumelanin/pheomelanin ratio, epidermal thickness — [EG diglib](https://diglib.eg.org/handle/10.1111/cgf14887) [S]
- **Donner et al. 2008**, layered heterogeneous spectral skin model with spatially varying melanin and haemoglobin
  maps — [Columbia](https://www.cs.columbia.edu/cg/hskin) [S]
- **SkinOptics** (GPL-3.0): Python tools for skin colour and optics, offline. — [repo](https://github.com/victorportog/skinoptics), push 2025-10-23 [P]
- **Separable SSS** (Jimenez & Gutierrez 2011): BSD-style licence text in the README ("Redistribution and use …
  are permitted provided that…"); two screen-space passes. —
  [repo](https://github.com/iryoku/separable-sss), push 2018-01-18 [P]
- **Graph-Based Synthesis for Skin Micro Wrinkles** (Weiss, Moulin, Chandran, Zoss, Gotardo, Bradley; SGP 2023):
  pores become graph nodes, edges become candidate wrinkles, an optimisation "inspired by pedestrian trail formation"
  carves them, shaders turn the graph into displacement; scales to "millions of wrinkles" at "real-time framerates";
  no code or data linked. — [Disney Research](https://studios.disneyresearch.com/?p=42514), 2023-07-03 [P]
- Graham et al. 2013 (exemplar microgeometry synthesis) and Nagano et al. 2015 (skin microstructure deformation by
  displacement-map convolution) — [ICT](https://vgl.ict.usc.edu/Research/Microgeometry/Measurement_Based_Synthesis_of_Facial_Microgeometry.pdf),
  [ICT SkinStretch](https://vgl.ict.usc.edu/Research/SkinStretch) [S]; EG 2024 style transfer of scanned micro detail —
  [cgf15048](https://diglib7.eg.org/bitstream/handle/10.1111/cgf15048/v43i2_38_15048.pdf) [S]
- **Wrinkle maps.** Raman et al. (Microsoft, WACV 2023): "we formalize the concept of mesh-tension and use it to
  aggregate possible wrinkles from high-quality expression scans into albedo and displacement texture maps", producing
  wrinkles "even for expressions not represented in the source scans". — [arXiv 2210.03529](https://arxiv.org/abs/2210.03529), 2022-10-05 [P].
  The lineage per the same paper: Oat's two bump maps (stretched, compressed), Jimenez's N maps with [0,1] weights;
  Disney's "Fast Dynamic Facial Wrinkles" adds per-angle stress bins; Blender Studio's *Charge* computes tension in
  Geometry Nodes (face-area ratio, 0.5 = no change). A patent on tension-map wrinkle blending: US 12062140 / 12555324.
  — [Disney PDF](https://studios.disneyresearch.com/app/uploads/2024/04/Fast-Dynamic-Facial-Wrinkles-Paper.pdf), [Blender Studio](https://studio.blender.org/blog/procedural-wrinkles/),
  [patent](https://patents.google.com/patent/US12062140) [S]

### 3b · Eyes

- **Unreal 5.8 shading models**: the Eye model takes Iris Mask and Iris Distance; it is "highly technical … tightly
  coupled to the shader code, the Material, the geometry, and the UV layout"; making one is "not recommended without
  extensive experience in shader development" — Epic suggests reusing the Digital Humans project's eye. Hair model:
  two specular highlights, inputs Scatter, Backlit, Tangent. Preintegrated Skin is "not physically perfect". Clear
  Coat can take a second normal. — [docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/shading-models-in-unreal-engine), UE 5.8, undated [P]
- **Galacean** (Ant Group; engine MIT, 5,914 stars, push 2026-10-29; docs v1.6): a digital-human Eye shader with
  sclera, iris, iris-normal and cornea-normal textures, a sclera mask (R iris, G limbus, B pupil), sclera colour,
  size, specular and roughness, pupil dilation (X/Y), limbal ring amount, iris colour and size, and a parallax layer;
  sibling Skin and Hair shaders. Source in `galacean/engine-toolkit` (MIT, push 2026-08-03) under
  `packages/custom-material/src/advanced-shader/{eye,hair,sss}`. —
  [eye docs](https://galacean.antgroup.com/engine/en/docs/graphics/material/builtinShaders/digitalHuman/eye), [toolkit](https://github.com/galacean/engine-toolkit) [P]
- **O3DE** Eye and Skin (with wrinkle maps) material types — round one C5/C6 (Apache-2.0 OR MIT), not re-derived.
- **Bérard et al. 2014**, "High-Quality Capture of Eyes" (Disney/ETH, SIGGRAPH Asia): sclera, cornea and a deforming
  iris reconstructed separately; 2016 follow-up "Lightweight eye capture using a parametric model". —
  [Disney](https://studios.disneyresearch.com/2014/11/19/high-quality-capture-of-eyes/) [S]
- Real-time eye papers: Animal Logic's "Real-time Refraction Shader for Animation" (SIGGRAPH 2024 talk, cornea
  refraction in Maya's viewport); Khademi et al., "Reconstructing Realistic and Relightable Eyes" (WACV 2026); the
  Animationsinstitut eye shader (multiple refractions, SSS, iris colour from pigmentation). —
  [SIGGRAPH history](https://history.siggraph.org/?p=160707), [WACV](https://openaccess.thecvf.com/content/WACV2026/papers/Khademi_Reconstructing_Realistic_and_Relightable_Eyes_WACV_2026_paper.pdf),
  [Animationsinstitut](https://animationsinstitut.de/en/research/tools/frapper/real-time-eye-shading) [S]
- No CC0 iris texture pack or open iris generator found — only paid Blender/Fab eye generators; a CC0 BlendSwap
  eyeball with fake caustics. — [BlendSwap 31370](https://www.blendswap.com/blend/31370) [S]
- Eye mesh stacks to copy the *structure* of (not the meshes, unless the licence allows): ICT-FaceKit's eyeballs,
  lacrimal fluid, eye blend, eye occlusion and lash strips (MIT, §1a); GNM's left/right eye interior and cornea UDIM
  tiles (Apache-2.0, pass-2 S4); CC5's Eye Occlusion and Tearline meshes (pass-2 S1).

### 3c · Lips

- Sticky lips: Barrielle et al. (CGF / EG 2019) simulate skin, lip contact and sticky lips in real time on the CPU
  from a blendshape model, driven from a webcam; Leach & Maddock model saliva with a FEM "breaking element" (2018,
  2019, thesis 2020). — [EG diglib cgf13450](https://diglib.eg.org:443/handle/10.1111/cgf13450), [Leach thesis](https://etheses.whiterose.ac.uk/28180/1/Matt_Leach_Thesis_Corrected.pdf) [S]
- Viseme set: Meta's 15 (sil, PP, FF, TH, DD, kk, CH, SS, nn, RR, aa, E, ih, oh, ou), "language independent"; the
  Oculus Lipsync plugin is end-of-life and the Movement SDK carries the same 15 through
  `XR_META_face_tracking_visemes`. — [Meta viseme reference](https://developers.meta.com/vr/documentation/unreal/audio-ovrlipsync-viseme-reference/) [S].
  CC5's 15 visemes (8 lip + 7 tongue pairs) and ARKit's 52 are in pass-2 S1 and §8.
- MetaHuman lip makeup: presets, colour, roughness ("matte or glossy"), opacity, metalness; plus foundation,
  concealer, blush and eye makeup. — [docs](https://dev.epicgames.com/documentation/metahuman/makeup-material-tools), undated [P]

### 3d · Mouth interior: teeth, gums, tongue

- **Velinov et al. 2018**, "Appearance Capture and Modeling of Human Teeth" (TOG 37(6)): in-vivo multi-camera,
  multi-light capture with intra-oral-scan geometry; derivative path tracing jointly fits optical properties and the
  inner dentin surface; output "can be directly used in conventional path tracing frameworks"; no code or data. —
  [project](https://www.jannovak.info/publications/TeethAppearance/index.html), undated [P]
- **OmniFaceRig** (arXiv 2606.08043, 2026-06-06): static mesh → FACS rig "with up to 155 blendshapes, procedurally
  fitted teeth, gums, and tongue, and re-packed UV/texture"; humans and animals; releases "Omni-Bench", 1,000 rigged
  biped characters with FACS blendshapes and inner-mouth geometry; the GitHub repo is a project page only. —
  [arXiv](https://arxiv.org/abs/2606.08043), [repo](https://github.com/omnifacerig/omnifacerig.github.io), push 2026-10-29 [P]
- MetaHuman teeth material: SRM (specular, roughness, metallic); controls teeth colour, gum colour, plaque colour and
  amount, a jaw-open preview. — [materials](https://dev.epicgames.com/documentation/metahuman/metahuman-materials-and-textures),
  [teeth & lashes](https://dev.epicgames.com/documentation/metahuman/teeth-and-eyelash-material-tools), undated [P]
- GNM teeth (80 identity components, procedurally generated from an artist-rigged template) and tongue (32
  expressions); ICT teeth, gums and tongue meshes; CC5's teeth/tongue bones — pass-2 S4 / S1 and §1a.

### 3e · Hair: grooming, shading and formats

- **Hair colour by melanin** (Blender manual source, Principled Hair BSDF): Melanin 0–1 mapped by
  `melanin_qty = -ln(max(1 - Melanin, 0.0001))`; Melanin Redness = pheomelanin share; absorption per unit eumelanin
  (0.506, 0.841, 1.653) and pheomelanin (0.343, 0.733, 1.924), "section 6.1 of [EFHLA11]" (d'Eon et al. 2011); colour
  → absorption from [CBTB16] (Chiang et al. 2016); Tint, Random Color, Random Roughness. —
  [hair_principled.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/render/shader_nodes/shader/hair_principled.rst), read 2026-10-29 [P]
- MetaHuman lashes use Dye Color, Melanin, Redness and Roughness — [teeth & lashes](https://dev.epicgames.com/documentation/metahuman/teeth-and-eyelash-material-tools) [P]
- Grooming: Blender's Curves Sculpt brushes and hair node groups (pass-2 S7). No standalone open grooming library
  found; Unreal's HairStrands interpolation (parametric, root-distance, vertex-index weights; nearest-neighbour to
  shape-matching quality) and Epic's Houdini "MH Groom Builder" (generation, guide interpolation, clumping) are
  engine-bound. — [UE Python API](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/HairInterpolationQuality),
  [MH Groom tools](https://dev.epicgames.com/documentation/metahuman/mh-groom-tools?lang=en-US) [S]
- **Real-Time Physically Guided Hair Interpolation** (Hsu, Wang, Pan, Gao, Yuksel, Wu; SIGGRAPH 2024): interpolate the
  guides' internal forces rather than positions; ~20% of linear interpolation's overhead; no code found. —
  [Utah](https://graphics.cs.utah.edu/research/projects/physically-guided-hair-interpolation/) [S]. "Game-Ready Hair in
  Minutes!" (SIGGRAPH 2026 Real-Time Live!, 2026-07-21): hair-mesh modelling with physics — [SIGGRAPH blog](https://blog.siggraph.org/2026/07/watch-it-work-real-time-live-2026-brings-emerging-technology-to-the-stage-in-la.html/) [S].
  `cemyuksel/cyCodeBase` (MIT, push 2026-07-08) [P] holds the `.hair` loader `cyHairFile` [S].
- Brows and lashes: free generator "Procedural Human Hair for Blender" (geometry nodes, CC BY-SA, pay-what-you-want);
  the rest are paid add-ons. — [itch.io](https://creamtau.itch.io/procedural-human-hair) [S]. MakeHuman's CC0 high-res
  brows and lashes (pass-2 S4).
- Cards: no maintained open card generator — `PurgatoryMP/Hair-Card-Generator` (GPL-3.0, 2 stars), a Houdini
  cards-to-curves HDA, `mysticfall/hairball` (Blender curves → cards for GodotHair); Unreal has a built-in card
  generator (Unreal-only). — GitHub API, 2026-10-29 [P]
- Rendering/sim (round one / pass-2 S7): TressFX 4.1 (MIT, push 2023-01-26), `vkhr` (MIT Vulkan hybrid), Jolt v5.6
  GPU hair (MIT, WIP), Stable Cosserat Rods.
- **Formats**: Unreal Alembic groom attributes (Top finding 6) — [Using Alembic for Grooms, UE 5.8](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-alembic-for-grooms-in-unreal-engine) [P];
  USD BasisCurves + `GroomAPI` (+ `GroomBindingAPI`), groom building editor-only, opt-in by
  `prepend apiSchemas = ["GroomAPI"]` — [UE forum thread](https://forums.unrealengine.com/t/how-does-the-usd-stage-need-to-be-structured-to-get-groom-assets-to-import/2794442), 2026-04-07 to 2026-08-18,
  quoting [Epic KB](https://dev.epicgames.com/community/learning/knowledge-base/jB8v/unreal-engine-usd-ue-format-support) [P].
  Blender imports `UsdGeomBasisCurves` as Curves; its USD export of particle hair is "limited to parent strands" with
  constant colour; Alembic export writes hair as "animated zero-width curves". —
  [usd.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/files/import_export/usd.rst),
  [alembic.rst](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/files/import_export/alembic.rst), read 2026-10-29 [P]

### 3f · Vellus, stubble, body hair, nails

- Vellus: LeGendre et al. 2017 model facial vellus hair from backlit silhouettes (offline); Unity's *Enemies* moved
  Skin Attachment to the GPU for peach fuzz; Daz sells a "Vellus Horizon" shader. — [ICT PeachFuzz](https://vgl.ict.usc.edu/Research/PeachFuzz/),
  [Unity blog](https://unity.com/blog/news/introducing-enemies-the-latest-evolution-in-high-fidelity-digital-humans-from-unity) [S].
  MetaHuman: a vellus (peach-fuzz) groom type and the "Fuzz" channel in SRMF (§4) [P].
- Stubble: MetaHuman's Face Texture Index filter covers "wrinkles, stubble, freckles, and moles" (texture, §4) [P];
  beard and mustache are grooms (§4) [P]. CC5's beards are cards with 1K textures and its SkinGen has a body-hair
  layer (round one 02).
- Nails: no nail appearance model found (only clinical notes — the lunula "appears white because of the way light
  is scattered"). CC5 gives nails their own UDIM tile (1005) and the Skin shader; MetaHuman has palm and nail colour
  controls. — [PMC4029263](https://pmc.ncbi.nlm.nih.gov/articles/PMC4029263/) [S]; [MetaHuman skin tools](https://dev.epicgames.com/documentation/metahuman/skin-material-tools) [P]

### 3g · Face rig generation

- **TopoRig** (arXiv 2609.15746, 2026-09-14): predicts "FACS-conditioned deformations directly on input mesh
  vertices while preserving the original topology", from the ICT FaceKit expression model; trained on 3,496 generated
  identities with "45 non-gaze expression controls from the 53-control ICT FaceKit vocabulary". Licence "TopoRig
  Academic Use License 1.0" (non-commercial academic); CUDA 12.8, Linux; weights on HF. —
  [arXiv](https://arxiv.org/abs/2609.15746), [repo](https://github.com/TaatiTeam/TopoRig), push 2026-09-20 [P]
- **RigAnyFace** (NeurIPS 2025): neutral mesh → FACS blendshape rig on diverse topologies, including disconnected
  parts; artist-rigged subset plus 2D supervision; no code found. — [arXiv 2511.18601](https://arxiv.org/abs/2511.18601), 2025-11-23 [P]
- No open tool generates ARKit's 52 shapes from a neutral mesh automatically: `digitalp/arkit-blendshape-tool` copies
  52 ARKit + 15 visemes from a reference avatar; FaceVerse's maintainer describes non-rigid ICP plus manual cleanup;
  KeenTools FaceBuilder generates them (commercial). — [tool](https://github.com/digitalp/arkit-blendshape-tool),
  [FaceVerse #7](https://github.com/LizhenWangT/FaceVerse/issues/7) [S]
- **OpenRigLogic design doc**: RigLogic outputs "joint transformations, blendshapes and animated mask multipliers";
  stages: PSD calculation (combined expressions), linear outputs (a sparse matrix of set-driven keys), conditional
  outputs (piecewise linear ranges; "less than 3%" of data, "usually … mask multipliers"); LODs laid out in one matrix
  with a Max-LOD. — [design.md](https://github.com/EpicGames/OpenRigLogic/blob/main/docs/design/design.md), read 2026-10-29 [P]
- Epic's DNA page: DNA "encodes all information necessary to assemble and configure a full MetaHuman head, body and
  its rigs"; geometry, skeleton and per-LOD skin weights at 8 LODs; expressions as joint animations; per-vertex
  displacement only at LOD0; wrinkles are "hooked to materials"; head and body are separate DNA files. —
  [MetaHuman DNA](https://dev.epicgames.com/documentation/metahuman/metahuman-dna-rig-definition-and-rig-operation), undated (5.6+) [P].
  MetaHuman body rigs use RBF solvers driving corrective bones (Poly Hammer's add-on, built on OpenRigLogic). —
  [Digital Production](https://digitalproduction.com/2026/04/02/metahuman-dna-add-on-for-rbf-editor/), 2026-04-02 [S]

### 3h · Body correctives and skin deformation

- **Dem Bones** (EA SEED): BSD 3-Clause (LICENSE "Copyright (c) 2025 Electronic Arts"); v1.2.1; turns an animated
  mesh sequence or blendshapes into linear blend skinning, or solves bone transforms; header-only C++ (Eigen, OpenMP);
  FBX/Alembic CLI. — [README](https://github.com/electronicarts/dem-bones), push 2025-01-17, 1,000 stars [P]
- **Complementary Dynamics**: `seungbaebang/complementary-dynamics-cpp` and `ErisZhang/complementary-dynamics`, MIT
  (2021) [P]. **Fast Complementary Dynamics** (SIGGRAPH 2023): reduced skinning-eigenmode solver for secondary motion
  "fully decoupled from the complexity of the mesh"; PyPI `fast-cd-pyb`. — [arXiv 2303.11886](https://arxiv.org/abs/2303.11886), 2023-03-21 [P]
- **Jolt v5.0.0**: "Added soft body skinning constraints", limiting soft-body vertices relative to a skinned mesh. —
  [ReleaseNotes.md](https://github.com/jrouwe/JoltPhysics/blob/master/Docs/ReleaseNotes.md), read 2026-10-29 [P]
- Jiggle: `naelstrof/JigglePhysics` MIT (Unity), `detomon/wigglebone` MIT (Godot `SkeletonModifier3D`),
  `xloveee/jiggle-physics` BSD-3 ("weight-painted regions + damped spring bone"). — GitHub API, 2026-10-29 [P]
- Direct Delta Mush (EA SEED, SIGGRAPH 2019; compression 2021): no official code found. — [EA SEED](https://www.ea.com/seed/news/siggraph2019-direct-delta-mush) [S]
- ML deformers: Unreal's Neural Morph Model (compressed morph targets from bone rotations, CPU inference, trained on a
  geometry cache; Unreal-only) — [UE API](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/NeuralMorphModel) [S];
  `EpicGames/MayaMLDeformer` MIT, push 2025-10-14 [P].
- Muscle: Ziva VFX, Real-Time and Face Trainer discontinued 2024-04-02 (DNEG holds an exclusive licence); AdonisFX 2.0
  (Maya/Houdini) is the commercial successor talked about; Houdini 21's Otis muscles and Skin Deform sliding are
  proprietary; no open muscle or skin-sliding library found. — [CG Channel 2024-04-03](https://www.cgchannel.com/2024/04/unity-discontinues-the-ziva-products/),
  [CG Channel 2026-03-04](https://www.cgchannel.com/2026/03/is-adonisfx-2-0-the-new-ziva-vfx/), [SideFX](https://www.sidefx.com/docs/houdini/muscles/overview.html) [S]
- PSD/RBF correctives, MHR's neural pose correctives (Apache-2.0) and SOMA-X's admitted candy-wrapper artefacts —
  pass-2 S7 / S4, not re-derived.

## 4 · Against the bar (CC5 and MetaHuman)

### 4a · What the bar is, part by part (new facts this pass; CC5's are in pass-2 S1)

- **MetaHuman textures**: preview at 512/1K; texture sources downloadable at 2K, 4K or 8K ("ERequestTextureResolution"
  2048/4096/8192); UE Cine bakes normal and specular "up to 8K", UE Optimized tops at 2K. Face: Basecolor Baked, SRMF
  Baked, Normal Baked, Normal LOD Baked 256², Scatter Baked 512², Basecolor Animated Delta 512², Normal Animated
  Delta 1K; body: the same set without animated maps; eyes: base colour and normal for sclera and iris; teeth: SRM;
  "Micro Skin Detail normals" (off at LOD1); SSS on at Epic/High, off at Medium/Low. —
  [materials and textures](https://dev.epicgames.com/documentation/metahuman/metahuman-materials-and-textures), undated (links to 5.5–5.6) [P];
  [materials tools](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-materials-tools) [P]
- **MetaHuman skin controls**: a 2D tone swatch with U and V sliders; Body Texture Index and Face Texture Index
  ("flipbook of discrete texture choices" for wrinkle density / age), a filter by wrinkles, stubble, freckles and
  moles; roughness; palm and nail colours; freckles (density, strength, saturation, tone shift); symmetric accents
  (redness, saturation, lightness — blush, sunburn, dark circles); Texture Override. —
  [skin material tools](https://dev.epicgames.com/documentation/metahuman/skin-material-tools), undated [P].
  Texture synthesis runs in Epic's cloud (pass-2 S3).
- **MetaHuman eyes**: 12 presets; iris pattern, rotation, primary/secondary colour, colour blend, Radial or Structural
  blending, shadow, limbal ring size/softness/colour, saturation, tint; pupil dilation and feather; cornea size (sets
  iris size), limbus softness and colour; sclera rotation, tint, transmission spread and colour, vascularity intensity
  and coverage; eyes edited together or apart. — [eye material tools](https://dev.epicgames.com/documentation/metahuman/eye-material-tools), undated [P]
- **MetaHuman grooms and LODs** (5.8 doc): up to 8 face/hair LODs, 4 body LODs; groom types hairstyle, eyebrows,
  eyelashes, beard, mustache and vellus (peach fuzz), each strands, cards or meshes per LOD; LOD 3 is "the
  highest-quality card-based LOD" in Epic's example; `r.HairStrands.UseCardsInsteadOfStrands 1`. —
  [LODs](https://dev.epicgames.com/documentation/metahuman/controlling-metahuman-levels-of-detail-lods-in-unreal-engine), undated [P]
- **CC5 micro normal**: "an additional normal map on top of the regular Normal map"; Micro Normal Tiling default
  42.000 on body, arm, leg and nail meshes. — [CC5 manual](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_Digital_Human_Shader/Skin/Micro_Normal.htm), undated [P].
  Face default 20 — [iClone/CC Head Micro Normal](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/41-Digital-Human-Shader/Head/Micro_Normal.htm) [S].
  CC5's 8K HD maps, five redness maps, cavity, EXR displacement, the Skin (5 textures) and Head (11 textures)
  shaders, card hair, multi-layer card lashes, eye occlusion and tearline: pass-2 S1 and round one 02.

### 4b · Comparisons found

- No paper, review or test found that compares an open dataset, open generator or open base with CC5 or MetaHuman
  output. Papers mention MetaHuman as a framework ("Democratizing the Creation of Animatable Facial Avatars", arXiv
  2401.16534) or a foil ("industrial systems like MetaHuman rely on limited preset assets", arXiv 2504.15259). —
  [arXiv 2504.15259](https://arxiv.org/html/2504.15259v2) [P]; [arXiv 2401.16534](https://arxiv.org/pdf/2401.16534) [S]
- USC ICT's 2025 generator ran an 87-person user study against DreamFace and Describe3D (description consistency and
  photorealism), not MetaHuman. — [arXiv 2504.15259](https://arxiv.org/html/2504.15259v2) [P]
- Perception studies with MetaHuman stimuli: arXiv 2509.17803 (photoreal vs semi-real MetaHumans with captured
  animation); a Utrecht thesis — MetaHumans rated "more realistic and more unsettling" than Ready Player Me in VR; a
  Brazilian age-perception study (112 participants) found 3D MetaHumans hardest to judge. —
  [arXiv 2509.17803](https://arxiv.org/pdf/2509.17803), [Utrecht](https://studenttheses.uu.nl/handle/20.500.12932/48008?show=full), [SBC](https://sol.sbc.org.br/index.php/semish/article/download/43534/43297/) [S].
  The Polito survey and the "CC 85% / MetaHuman 95%" forum post: pass-2 S4.

### 4c · Per part: reuse or build

Assessment (the user's order: reuse if it meets the bar, otherwise build; licences shown as labels only):

| Part | Bar (CC5 / MetaHuman) | Best reusable found | Meets the bar? | Assessment |
|---|---|---|---|---|
| Skin maps (albedo, spec/rough, normal, displacement, SSS, cavity) | 8K, displacement + cavity, redness / animated deltas; cloud synthesis + texture-index flipbooks (MH) | Data: FaceScape 4K (NC), FFHQ-UV-Intrinsics 1K PBR (CC BY-NC-ND), single 8K head (NC), Lee Perry-Smith (CC BY 3.0). Generators: FreeUV (NC), UVAPM albedo (MIT) | No — resolution or completeness short, and no released permissive PBR generator | **Build** the generator: Apache/MIT image model via sd.cpp → our UV projection → intrinsic split → procedural pores/micro-wrinkles (Weiss-type) + tiled micro normal for 8K. NC sets are usable only under their labels |
| Skin colour model | MH 2D tone + accents; CC SkinGen layers, redness maps | Papers only (Jimenez 2010, Aliaga 2022/23); no open real-time code | — | **Build** (melanin/haemoglobin maps as our parameters, from the papers) |
| Skin shading | Burley-type SSS, dual specular, micro normal | Separable SSS (BSD-style), O3DE skin (round one), Galacean SSS (MIT) | Technique yes | **Reuse technique**, write our shader |
| Wrinkle maps | MH animated maps via RigLogic mask multipliers; CC expression wrinkles | Mesh-tension papers; Blender Studio method; O3DE wrinkle maps | Technique yes | **Build** our tension-driven wrinkle system (patent noted) |
| Eyes (iris, sclera, cornea, wetness, occlusion, tearline) | MH 12 presets + full controls; CC HD eyes, occlusion, tearline | Galacean eye (MIT), O3DE eye; ICT eye stack layout (MIT); GNM eyeball/cornea (Apache) | Shader refs yes; no iris data | **Build** shader + procedural iris (or image-model iris), reusing ICT/GNM structure as reference |
| Lips | Part of skin + makeup (MH); MouthSticky shapes (CC) | Sticky-lips papers; viseme sets (Meta 15, CC 15, ARKit) | Technique only | **Build** (lip region in skin generator; sticky-lips as rig layer) |
| Teeth, gums, tongue | MH SRM teeth, plaque/gum colour; CC Teeth/Gums + Tongue shaders, HD teeth | GNM teeth (80 comps) + tongue (32) Apache; ICT meshes MIT; no appearance data | Geometry yes; appearance no | **Reuse geometry model** (GNM/ICT, under their licences), **build** shading |
| Scalp hair | MH strand grooms with card/mesh LODs; CC Smart Hair cards 2K | Data NC (HairCS, DiffLocks) or unlicensed (USC-HairSalon); Perm (MIT); renderers TressFX/vkhr (MIT); Jolt sim (MIT) | No permissive groom set at quality | **Build** a guide/interpolate/clump groom generator + card baker; reuse renderer/sim pieces |
| Brows, lashes, beard, stubble | MH grooms (strands→cards); CC conformed cards; MH stubble textures | MakeHuman CC0 brows/lashes; CC BY-SA Blender generator | Partial | **Build** procedural strand generators + stubble texture layer |
| Body hair, vellus | MH vellus groom + SRMF fuzz; CC SkinGen body-hair layer | LeGendre 2017 (paper) | — | **Build** (fuzz term in shader first; short-strand grooms later) |
| Nails | CC tile 1005 + Skin shader; MH nail colour | none | — | **Build** (small: texture + clear-coat) |
| Face rig | MH DNA/RigLogic (hundreds of controls, 8 LODs); CC 262 + 128 HD | OpenRigLogic MIT (runtime); ARKit names; TopoRig (academic licence) | Runtime yes; generation no | **Reuse** OpenRigLogic + ARKit naming; **build** shape generation |
| Body correctives, jiggle, muscle | MH body RBF corrective bones; CC (no JCMs, a complaint) | Dem Bones BSD-3; complementary dynamics MIT; Jolt skinned soft bodies; MHR correctives (Apache) | Pieces yes; muscle no | **Reuse pieces**, **build** the corrective system; muscle/skin-sliding later |

## 5 · Working with both

- **CC5**: six UDIM tiles 1001–1006 (head, body, arm, leg, nails, eyelash) in one `Std_Skin_Head` set; eyes, teeth
  and tongue separate — pass-2 S1, not re-derived. CC5 hair is cards only (round one 02), so a strand groom must be
  baked to cards to reach CC5.
- **MetaHuman textures in**: Texture Override takes face base colour, normal, cavity and animated maps, and body
  base colour, normal and cavity — [skin material tools](https://dev.epicgames.com/documentation/metahuman/skin-material-tools) [P].
  The eye, teeth and SRMF/Scatter maps are listed in §4a [P]. Head fitting picks up meshes named `eyeLeft`,
  `eyeRight` and teeth; "only teeth (mesh index 1), left eye (3), and right eye (4) are taken from the DNA"; material
  slots include `EyeShellSlotName`, `SalivaSlotName`, `TeethSlotName`. — [template tool](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-template-tool-in-unreal-engine?lang=en-US),
  [FMetaHumanCharacterSkinMaterials](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/MetaHumanCharacterEditor/FMetaHumanCharacterSkinMaterials) [S]
- **DNA**: OpenRigLogic (MIT) reads and writes DNA and evaluates the rig (pass-2 S3); wrinkle maps are its animated
  mask multipliers (§3g) [P].
- **ARKit names**: the 52 (§8 of RESEARCH); Meta's 15 visemes (§3c).
- **Grooms into Unreal**: Alembic with the groom 1.5 attributes, or USD BasisCurves with the `GroomAPI` schema and
  the same `groom_*` attributes; a `GroomBindingAPI` binds to a character (§3e) [P]. Blender reads BasisCurves as
  hair Curves [P].

Assessment: one internal groom record (strands with root UV, guide flags, group IDs, width, colour/melanin) written
as USD BasisCurves + `GroomAPI` and as Alembic covers Unreal and Blender; CC5 needs a card bake. For textures, one
master texture set per character, re-baked into CC5's six tiles and into MetaHuman's override slots, covers both —
both reference apps accept user textures through documented slots.

## Couldn't verify / open

- **Licences not read**: FLUX 3 Image Klein (`flux-kommunity-license`) and Fibo 2.0 — gated on Hugging Face, not
  worked around; FLUX.2-dev / klein-9B ("other"); USC-HairSalon (no licence found); Teeth3DS dataset; Omni-Bench;
  NeRSemble (form only); RenderMe-360's agreement text (download required).
- **Conflicting labels**: FFHQ-UV (MIT tag vs FFHQ's NC image licences); ATLAS (CC BY 4.0 tag vs "research purposes").
- **Not found**: any open dataset of skin displacement maps; any CC0/CC BY head-scan dataset at scale; an open iris
  texture set; any nail appearance model; an open muscle / skin-sliding library; a maintained open hair-card
  generator; code for Relightify, MoSAR, RigAnyFace, OmniFaceRig, HairGPT, physically guided hair interpolation, Weiss
  micro-wrinkles, Velinov teeth, Jimenez dynamic skin colour.
- **Search snippet only** (re-check at the page): MERL/ETH's 149 subjects; RealFaceDB; ICT's 6K service maps;
  BEDLAM textures; MakeHuman Skins 01–03 resolution; TextureCan; Aliaga 2023; Donner 2008; Graham 2013; Nagano 2015;
  Bérard 2014; sticky-lips papers; Meta's viseme list; mesh-tension lineage and the patent; LeGendre 2017; Unreal's
  Neural Morph Model; Direct Delta Mush; the Ziva and AdonisFX articles; the MetaHuman RBF article; CC's face
  micro-normal default (20); MetaHuman DNA mesh indices.
- **VRAM / GPU vendor not measured**: FreeUV (SD1.5, likely small), HiDream-O1-Image (~8.8B) and FLUX.2 klein 4B on
  8 GB through stable-diffusion.cpp; Marigold IID on non-NVIDIA; every hair model's VRAM below A100 class.
- **FFHQ-UV map resolution** is not stated in its README or abstract.
- **MetaHuman**: the number of animated (wrinkle) maps; whether its default lashes and brows are strands or cards at
  LOD0 (the materials page says "card-based eyelashes", the LOD page lists eyelashes as grooms); the Alembic groom
  *specification* page and Material Overrides page rendered empty to the fetcher.
- **No comparison against the bar exists** for any open part; judging "meets the bar" needs our own side-by-side
  renders against CC5 and MetaHuman (the user's machine runs both).
