# Research 05, pass 2 — Open human bases: the gaps round one left open

Research notes for JustStage, 2026-10-29: the second pass on section S4 of
[`2026-10-29-research-second-pass.md`](2026-10-29-research-second-pass.md). It builds on round one,
[`2026-10-29-research-05-bases.md`](2026-10-29-research-05-bases.md), and feeds `docs/dev/RESEARCH.md` §5.
This agent did not edit RESEARCH.md. Round-one facts marked *page read* were not re-derived.

Method: `gh api` (signed in) for GitHub repos, trees, commits, issues and file contents; raw.githubusercontent.com
for raw files; the Hugging Face API and raw model cards; crates.io and the Godot Asset Library APIs; arXiv HTML
pages; WebFetch for project, vendor and docs pages; `pdftotext` for one thesis PDF. No meshes, models or datasets
were downloaded. Mesh counts come from small metadata, config and test files, from file sizes in GitHub's tree
listing, or from papers. Two small CharMorph YAML config files were read; no mesh or morph data was. About 40 of
the ~200 web searches were used.

Labels: *page read* means the primary page or file was opened. *Search snippet only* means it was seen only in a
search result. *Inference* is my own conclusion and is marked as such. Dates are the source's own dates; "read
2026-10-29" marks a live repo or API reading.

Refused or blocked to scripted access (not worked around): helpx.adobe.com (Mixamo FAQ, 403), vroid.com and
developer.vroid.com (403), unrealengine.com news (403), meshcapade.com (403), the meshcapade Notion page (renders
empty), the dev.epicgames.com Mutable page (renders empty), repositorio.upct.es (403). reddit.com is not reachable
by this search tool at all ("domains are not accessible to our user agent").

## Top findings

1. **SkinTokens (MIT) is no longer NVIDIA-only.** `localai-org/skin-tokens.cpp` (Apache-2.0, created 2026-08-28,
   232★) is a C++23/GGML port that rigs a mesh "on CPU or Vulkan", with a C API and published parity numbers. GGUF
   weights are at `LocalAI-io/SkinTokens-GGUF`. ONNX (QtMeshEditor) and Swift-MLX (Apple; "not ready for use")
   ports also exist. — [skin-tokens.cpp](https://github.com/localai-org/skin-tokens.cpp), [GGUF card](https://huggingface.co/LocalAI-io/SkinTokens-GGUF)
2. **UniRig's skeleton stage runs on any vendor through third-party ONNX ports.** One runs on ONNX Runtime; the
   other is an int8 build that runs "entirely inside a web browser on WebGPU" (1.44 GB → 455 MB). The skin-weight
   head does not port: "it depends on spconv/PTv3, which has no ONNX lowering". — [QtMeshEditor-unirig-onnx](https://huggingface.co/fernandotonon/QtMeshEditor-unirig-onnx), [unirig-skeleton-onnx-webgpu](https://huggingface.co/cgb/unirig-skeleton-onnx-webgpu)
3. **All the rigging checkpoints are permissive; their training data differs.** UniRig and SkinTokens weights are
   MIT. Puppeteer and MagicArticulate are Apache-2.0. Make-It-Animatable's weights are Apache-2.0 and its code MIT.
   Articulation-XL2.0 is CC-BY-4.0, "filtered from Objaverse-XL". Make-It-Animatable trains on 95 Mixamo characters
   and 2,453 Mixamo motions, kept in a gated HF dataset. A community Mixamo FAQ says Mixamo content can't be used for
   "training machine-learning models". — HF cards (below), [arXiv 2411.18197](https://arxiv.org/html/2411.18197)
4. **GNM Head's counts are now known.** It has 17,821 vertices (skin, teeth, tongue, eyeballs), stored as **both
   quads and triangles**. It has 253 identity components, 383 expression components, 4 joints, 7 UDIM tiles and a
   pose-corrective regressor. Its HF weights are Apache-2.0. On held-out scans it fits at 0.748 mm against FLAME's
   0.968 mm. — [GNM shape README](https://github.com/google/GNM/blob/main/gnm/shape/README.md), [arXiv 2607.23687](https://arxiv.org/html/2607.23687), [HF google/gnm-v3](https://huggingface.co/google/gnm-v3)
5. **MHR and SOMA-X evaluate as closed triangle meshes.** MHR LOD1 has 18,439 vertices and 36,874 faces. SOMA mid
   has 18,056 vertices and 36,108 triangles. SOMA-X documents LBS "candy-wrapper and volume-loss artifacts" past
   elbow 120° and shoulder abduction 90°. MHR's 72 expressions are artist-sculpted FACS shapes, not PCA. — [MHR test_server.py](https://github.com/facebookresearch/MHR/blob/main/web-viewer/tests/test_server.py), [SOMA-X data_assets.md](https://github.com/NVlabs/SOMA-X/blob/main/docs/data_assets.md), [EXPLAINABILITY.md](https://github.com/NVlabs/SOMA-X/blob/main/docs/EXPLAINABILITY.md)
6. **hm08 is an all-quad mesh made for subdivision.** It is triangle-free, poles have at most 5 edges, it has
   14,766 faces, and Manuel Bastioni remodelled it in 2013. The raw mesh has 19,158 vertices including helpers and
   125 joint cubes; the body group alone has 13,380. MPFB ships a Corrective Smooth operator for "volume loss at elbow
   and shoulder joints". — [MakeHuman topology doc](https://static.makehumancommunity.org/makehuman/docs/professional_mesh_topology.html), [hm08_config.json](https://github.com/makehumancommunity/mpfb2/blob/master/src/mpfb/data/mesh_metadata/hm08_config.json), [basemeshops.md](https://github.com/makehumancommunity/mpfb2/blob/master/docs/ui/operations/basemeshops.md)
7. **Realism against CC5 and MetaHuman is still unsourced for every open base.** The one perception survey found
   (Politecnico di Torino) covers MetaHuman, Daz, ZBrush and scans, not MakeHuman or CC. It says skin detail, eyes,
   hair and lighting drive the rating. A photoreal MakeHuman example needed a custom eyelid target, an SSS map, a pore
   bump map and eye-shader work. — [Polito thesis](https://webthesis.biblio.polito.it/24580/1/tesi.pdf)
8. **Humanizer's licence conflict is settled by its history.** The repo started under the Unlicense (2024-03), moved
   to CC0 on 2025-01-18, and moved to AGPL-3.0 on 2025-08-26 ("change LICENSE to match makehuman (AGPL)"). The Godot
   listing's "CC0" is the v2.2.0 release of 2025-02. — GitHub commits API, [Godot asset 3699](https://godotengine.org/asset-library/asset/3699)
9. **Rocketbox's bone count is settled at 53 body plus 28 facial bones.** That is my count of the bone keys in a
   Headbox data file, and it matches the paper's figure caption. The text's "56" probably counts helper or end
   nodes (inference). — [Headbox DeltaValues](https://github.com/openVRlab/Headbox/tree/main/Maya/DeltaValues), [Frontiers 2020](https://www.frontiersin.org/articles/10.3389/frvir.2020.561558/full)
10. **Unreal's Mutable is "production ready" with 5.8.** It merges and edits skeletal meshes, textures, morphs,
    cloth, physics, MetaHuman DNA and (experimentally) grooms, in the editor or at runtime. It ships no assets and
    works only in Unreal. — [Mutable wiki: What's New](https://github.com/anticto/Mutable-Documentation/wiki/What's-New)
11. **Strand hair: the only permissive groom set found is MakeHuman's CC0 hair-editor pack (7 styles).** The
    research hair datasets are non-commercial: DiffLocks (MPI licence; commercial use goes through Meshcapade) and
    CT2Hair (CC-BY-NC-4.0). — [MakeHuman asset packs](https://static.makehumancommunity.org/assets/assetpacks.html), [DiffLocks licence](https://difflocks.is.tue.mpg.de/license.html)
12. **Daz is free but closed, and its content can't be shipped.** Daz Studio and Genesis 9 Starter Essentials are
    free. The EULA bars distributing content without written consent. Use in an app needs a per-product
    Interactive License, and "AI engines" use is excluded. — [Daz EULA](https://www.daz3d.com/eula), [Interactive Licenses](https://www.daz3d.com/interactive-license-info)
13. **VRoid Studio's EULA (served through Steam):** output items "belong to the Users who created such works", and
    producing output items is an allowed use. The software itself stays the company's. — [Steam EULA](https://store.steampowered.com/eula/1486350_eula_0)
14. **The SMPL family's commercial use is paid through Meshcapade.** A Notion snippet gives €5,000 a year for its
    smallest tier. **ATLAS has no separate release:** it "has been integrated into MHR" (Apache-2.0). — [SMPL-X licence](https://smpl-x.is.tue.mpg.de/modellicense.html), [ATLAS page](https://jindapark.github.io/projects/atlas/)
15. **LHM is NVIDIA-only, and two of its inputs are non-commercial.** Its rasteriser and KNN are CUDA extensions,
    and the maintainer says it is "currently not supported on Mac". It uses the Sapiens-1B encoder (CC-BY-NC-4.0) and
    SMPL-X parameters, and outputs Gaussian points. — [LHM README](https://github.com/aigc3d/LHM), [LHM model card](https://github.com/aigc3d/LHM/blob/main/modelcard.md), [Sapiens LICENSE](https://github.com/facebookresearch/sapiens/blob/main/LICENSE)

## 1 · Realism against CC5 and MetaHuman

- Reallusion forum, user TRILEC, posted "4 Years Ago" (about 2022): CC rendering "about 85%" and MetaHuman "about
  95%" of photorealism. The thread never mentions MakeHuman, Daz-as-base or any open tool. —
  [forum.reallusion.com/503486](https://forum.reallusion.com/503486/Forum37.aspx), *page read* (round one had a snippet).
- Politecnico di Torino master's thesis "MetaHumans for Unreal (and other platforms)" (A. Esaulova, 2021–22). Its
  survey respondents had no CG experience and were shown renders from MetaHuman Creator, Daz3D and ZBrush beside real
  photos. Real photos were picked as photos 37.29% of the time, Daz renders 29.91%, MetaHuman 19.70% and ZBrush
  13.10%. — [tesi.pdf](https://webthesis.biblio.polito.it/24580/1/tesi.pdf), §3 p. 52, *page read* (PDF text).
- Same thesis: mean photorealism on a 1–5 scale was ZBrush 3.56, MetaHuman Creator 3.45, 3D scan 3.42 and Daz3D
  3.05. Respondents named lighting, skin texture, wrinkles, freckles and small imperfections, and gaze as what
  decided it. A Daz-made ad shown at half-body or from a distance scored 4.47. — same, pp. 52–55, *page read*.
- Same thesis, §1.6: a photoreal MakeHuman example by the artist "ecke101" needed raised and softened brows and
  lashes, a custom eyelid target, a skin subsurface map, a painted bump map for pores and lips, and a glossier
  cornea. The survey did not include MakeHuman. — same, p. 16, *page read*.
- JCU review (Briceno & Paul, IEA 2018, published 2019): the abstract says MakeHuman "creates realistic appearance 3D
  virtual human models" but gives no evidence, and says it is "rarely used in Ergonomic studies". —
  [researchonline.jcu.edu.au/59814](https://researchonline.jcu.edu.au/59814/), *page read* (abstract; the full text is
  restricted).
- GNM's report compares only with FLAME. Held-out scan-to-mesh error (15,000 scans) is 0.748 mm for GNM against
  0.968 mm (FLAME without jaw) and 0.971 mm (FLAME). Single-view synthetic fitting is 1.683 mm against 2.172 mm. There
  is no realism study. — [arXiv 2607.23687 HTML](https://arxiv.org/html/2607.23687), *page read*.
- MHR's paper compares only with SMPL and SMPL-X (vertex error on 3DBodyTex; "lower fitting error with fewer
  components"). There is no ATLAS or Anny comparison and no claim of use in games or film. —
  [arXiv 2511.15586](https://arxiv.org/html/2511.15586), *page read*.
- Utrecht student thesis (2024): MetaHuman avatars were rated "significantly more realistic and more unsettling" than
  Ready Player Me avatars (31 participants). — [studenttheses.uu.nl](https://studenttheses.uu.nl/handle/20.500.12932/48008),
  *search snippet only*.
- Digital Production's MPFB 2 article (Bela Beier, 2025-03-14) makes no realism or quality judgement. —
  [digitalproduction.com](https://digitalproduction.com/2025/03/14/mpfb-2-blenders-new-character-generation-sidekick/), *page read*.
- CharMorph 0.4 has press coverage (BlenderNation 2025-03-19, CG Channel 2025-03-24) but no independent hands-on
  review was found. The coverage says 0.4 ships non-AGPL models usable in commercial games. —
  [blendernation](https://www.blendernation.com/2025/03/19/charmorph-v0-4-0-character-creator-released/), *search snippet only*.
- Rocketbox: searches for perceived-realism ratings of Rocketbox avatars, or comparisons with CC or MetaHuman, found
  none. The library is described only as a research tool. — *search snippet only* (no study found).
- Showcases made by the authors exist: GNM's XR Blocks web demo ([README](https://github.com/google/GNM)) and MHR's
  local Three.js web viewer ([web-viewer README](https://github.com/facebookresearch/MHR/blob/main/web-viewer/README.md)).
  They are demos, not comparisons. — *page read*.

Assessment: no source rates MPFB2/MakeHuman, Anny, MHR, CharMorph, Rocketbox or GNM against CC5 or MetaHuman. The
evidence that exists (the Polito survey, the ecke101 example) puts perceived realism in skin detail, eyes, hair and
lighting rather than in the base mesh. That supports round one's rec: take realism from our own detail layers, not
from the choice of base.

## 2 · Mesh quality: topology, edge loops, subdivision, counts

### MakeHuman hm08
- The MakeHuman doc "Professional mesh topology" says: "The Homunculus08 remodelled from scratch by Manuel Bastioni
  in 2013"; "Light and optimized for subdivision surfaces modelling (14766 faces)"; "Quads only. The human mesh is
  completely triangles free"; "Max number of edges admitted for a pole: 5"; "Optimized for animation and sculpting
  (Zbrush, Mudbox)". It gives no vertex count or edge-loop layout. —
  [static.makehumancommunity.org](https://static.makehumancommunity.org/makehuman/docs/professional_mesh_topology.html), undated, *page read*.
- In `hm08_config.json` ("MakeHuman HM08 basemesh"), the `groups_by_range` field gives `body` as vertices 0–13,379
  (13,380). The helpers are tongue 226, eyes 72 each, eyelashes 125 each, teeth 68 each, genital 200, tights 2,674,
  skirt 720 and hair 428. This is my reading. —
  [hm08_config.json](https://github.com/makehumancommunity/mpfb2/blob/master/src/mpfb/data/mesh_metadata/hm08_config.json), read 2026-10-29, *page read*.
- `basemesh_vertex_groups.json` has 144 groups, 125 of them joint cubes. Its highest vertex index is 19,157, so the
  raw mesh including helpers and joint cubes has **19,158 vertices** (my count). —
  [basemesh_vertex_groups.json](https://github.com/makehumancommunity/mpfb2/blob/master/src/mpfb/data/mesh_metadata/basemesh_vertex_groups.json), read 2026-10-29, *page read*.
- MPFB's "Delete helpers" removes the `HelperGeometry` and `JointCubes` vertices. "Many clothing assets (.mhclo
  files) rely on the helper geometry's vertex indices", so deleting them stops most clothes fitting. —
  [basemeshops.md](https://github.com/makehumancommunity/mpfb2/blob/master/docs/ui/operations/basemeshops.md), *page read*.
- MPFB's "Add Corrective Smooth" places a Corrective Smooth modifier after the armature "so that it corrects
  deformation artefacts introduced by the armature (e.g. volume loss at elbow and shoulder joints)". — same, *page read*.
- MPFB's `MeshCrossRef` strips `MASK` and `SUBSURF` modifiers before building tables, so its arrays match the base
  mesh's vertex count. That is how MPFB handles subdivision: as a modifier on top of the base. —
  [meshcrossref.md](https://github.com/makehumancommunity/mpfb2/blob/master/docs/entities/meshcrossref.md), *page read*.

Assessment: hm08 is a deliberate all-quad, subdivision-ready base. Its LBS deformation needs help at elbows and
shoulders (MPFB's own fix is a smoothing modifier, not pose correctives), and no source documents its edge loops.
Anny's 13,718 is an edited figure; hm08's body group is 13,380 and the full raw mesh 19,158.

### MHR (Meta)
- The web viewer's tests assert LOD1 `vertices == 18439` and `faces == 36874`. Since 36,874 = 2 × 18,439 − 4, the
  model's LOD1 mesh is a closed, genus-0 triangle mesh (my arithmetic). —
  [web-viewer/tests/test_server.py](https://github.com/facebookresearch/MHR/blob/main/web-viewer/tests/test_server.py), read 2026-10-29, *page read*.
- The LOD conversion maps store "Triangle indices on the source mesh" with barycentric coordinates. —
  [mhr_LOD_conversion/README.md](https://github.com/facebookresearch/MHR/blob/main/tools/mhr_LOD_conversion/README.md), *page read*.
- The viewer's `build_lod_topology.py` reads the FBX "control-point topology" and fan-triangulates whatever polygons
  it finds. Whether the FBX polygons are quads is not stated. —
  [build_lod_topology.py](https://github.com/facebookresearch/MHR/blob/main/web-viewer/tools/build_lod_topology.py), *page read*.
- Paper: skinning weights are "artist-defined"; for LOD0 the authors "subdivide the LOD1 correctives to achieve a
  smoother result". It says nothing about edge loops or base-mesh authorship. —
  [arXiv 2511.15586](https://arxiv.org/html/2511.15586), *page read*.
- The 72 expressions are "artist-sculpted, sparse semantic facial blendshapes that follow" FACS, "not PCA
  components". They include unilateral controls, gaze, jaw direction and lip quadrants, and are identical across LODs
  0–6. They map to FBX shapes `shape_45` onward. —
  [docs/face-expressions.md](https://github.com/facebookresearch/MHR/blob/main/docs/face-expressions.md), *page read*.
- The viewer evaluates "the native TorchScript LOD 1 model on CPU". It exports OBJ, GLB and USD; the GLB and USD
  exports carry the armature and "four normalized skinning influences per vertex". —
  [web-viewer README](https://github.com/facebookresearch/MHR/blob/main/web-viewer/README.md), *page read*.

### SOMA-X (NVIDIA)
- The mid-LOD `triangles` array has T = 36,108 (18,056 vertices, so a closed triangle mesh by the same arithmetic).
  The low LOD has 9,006 triangles. The xlo LOD has 612 vertices and "is not a strict vertex-index subset of the mid
  mesh". — [docs/data_assets.md](https://github.com/NVlabs/SOMA-X/blob/main/docs/data_assets.md), read 2026-10-29, *page read*.
- "Standard LBS produces known candy-wrapper and volume-loss artifacts at joints under extreme flexion (e.g., elbow >
  120°, shoulder abduction > 90°). Mitigation: optional pose-dependent corrective MLP". The topology is fixed, and a
  new backend needs an offline wrap registration. —
  [docs/EXPLAINABILITY.md](https://github.com/NVlabs/SOMA-X/blob/main/docs/EXPLAINABILITY.md), *page read*.

### GNM Head (Google)
- "17 821 vertices (including the outer skin, teeth, tongue and eyeballs)". The kinematic chain has K = 4 joints,
  and skin weights and the chain "are designed manually by an artist". The teeth were procedurally generated from an
  artist-rigged template. Training data: about 5,000 individuals, ~150,000 samples. The report does not say quads or
  triangles and does not mention subdivision or edge loops. — [arXiv 2607.23687 HTML](https://arxiv.org/html/2607.23687), *page read*.
- The data schema carries both `quads` and `triangles`, `quad_uvs` and `triangle_uvs`, `skinning_weights`,
  `pose_correctives_regressor`, `mirror_indices` and `vertex_groups`. —
  [gnm_data_schema.py](https://github.com/google/GNM/blob/main/gnm/shape/gnm_data_schema.py), read 2026-10-29, *page read*.
- Identity has 253 components: 170 head, 3 eyeball and 80 teeth. Expression has 383: 100 left eye, 100 right eye,
  150 lower face, 32 tongue and 1 iris. Typical range is −3 to +3. The UV layout is UDIM tiles 1001–1007 (skin, left
  eye interior, left cornea, right eye interior, right cornea, teeth and gums, tongue), given "for both the quad
  topology and the triangulated topology". —
  [gnm/shape/README.md](https://github.com/google/GNM/blob/main/gnm/shape/README.md), *page read*.
- The model card names the joint controls as "kinematic rotation of the neck and bilateral eyeball gaze". —
  [HF google/gnm-v3](https://huggingface.co/google/gnm-v3), modified 2026-09-02, *page read*.

### MB-Lab (and its meshes inside CharMorph)
- Wikipedia: "The lab 1.5.0 provides about 470 morphs for each human character". It has two base meshes, male and
  female, and generated characters are AGPL-3. — [Wikipedia: MB-Lab](https://en.wikipedia.org/wiki/MB-Lab), *page read*.
- MB-Lab's README and CHANGELOG give no vertex or face counts. —
  [README](https://github.com/animate1978/MB-Lab), [CHANGELOG.md](https://github.com/animate1978/MB-Lab/blob/master/CHANGELOG.md), *page read*.
- CharMorph-db file sizes from the GitHub tree listing (no files downloaded): `mb_female/morphs/L1/*.npy` are
  218,648 bytes each and `mb_male/morphs/L1/*.npy` 216,080 bytes. The `faces.npy` files are 138,432 and 136,720
  bytes. — [CharMorph-db tree](https://github.com/Upliner/CharMorph-db/tree/master/characters), read 2026-10-29, *page read*.
- CharMorph's editor saves `faces.npy` as `uint16` polygon vertex lists, and L1 morphs as float32 or float64 xyz. —
  [cmedit/file_io.py](https://github.com/Upliner/CharMorph/blob/master/cmedit/file_io.py), *page read*.
- *Inference* from those two facts, assuming a 128-byte `.npy` header, float32 and uniform four-sided faces: MB-Lab
  female is about **18,210 vertices and 17,288 quads**, and male about **17,996 vertices and 17,074 quads**. The face
  and vertex counts agree with each other, as they should for a closed quad mesh. This is unverified.
- CharMorph's CC-BY base "Reom" has 111 L2 and 51 L3 morph files (tree listing). Antonia's morphs are packed into
  single L2 and L3 files, so they can't be counted this way. — same tree, *page read*.

## 3 · Licences of the AI rigging checkpoints, and Make-It-Animatable's Mixamo data

- **UniRig** (`VAST-AI/UniRig`): licence `mit`, dataset `Seed3D/Articulation-XL2.0`. The card says the repo holds
  "only the Skeleton&Skinning Prediction component … trained specifically on the Articulation-XL2.0 dataset". Files
  include `skeleton/articulation-xl_quantization_256`, `skeleton/rignet` and `skin/articulation-xl` checkpoints, plus
  Rig-XL data lists that include `mixamo_train/test` and `vroid_train/test`. Last modified 2025-08-01. —
  [HF card](https://huggingface.co/VAST-AI/UniRig), *page read*.
- **SkinTokens** (`VAST-AI/SkinTokens`): licence `mit`. It holds the FSQ-CVAE skin tokenizer and the TokenRig
  transformer ("Qwen3-0.6B architecture, GRPO-refined"), about 1.6 GB. "The training data … will be released
  separately". Last modified 2026-04-20. — [HF card](https://huggingface.co/VAST-AI/SkinTokens), *page read*.
  The embedded Qwen3-0.6B backbone weights are Apache-2.0 per a port's card —
  [mlx-community/SkinTokens-bf16](https://huggingface.co/mlx-community/SkinTokens-bf16), *page read*.
- **Puppeteer** (`Seed3D/Puppeteer`): `apache-2.0`, Articulation-XL2.0, with skeleton and skinning checkpoints
  released 2025-09-03. Last modified 2025-09-19. — [HF card](https://huggingface.co/Seed3D/Puppeteer), *page read*.
- **MagicArticulate** (`Seed3D/MagicArticulate`): `apache-2.0`, Articulation-XL2.0. The 2025-08-07 update fixed a
  "normalization bug causing mesh-skeleton misalignment". Last modified 2025-08-23. —
  [HF card](https://huggingface.co/Seed3D/MagicArticulate), *page read*.
- **Make-It-Animatable** (`jasongzy/Make-It-Animatable`): weights `apache-2.0`, dataset `jasongzy/Mixamo`, last
  modified 2026-09-08. The GitHub code is MIT ("Copyright (c) 2025 Zhiyang Guo"). So round one's "MIT" holds for
  the code, and the weights are Apache-2.0. — [HF card](https://huggingface.co/jasongzy/Make-It-Animatable),
  [LICENSE](https://github.com/jasongzy/Make-It-Animatable/blob/main/LICENSE), *page read*.
- **Articulation-XL2.0**: `cc-by-4.0`, "over 48K 3D models … filtered from Objaverse-XL". The metadata keeps each
  item's `source` and `fileIdentifier`. — [HF dataset](https://huggingface.co/datasets/Seed3D/Articulation-XL2.0), *page read*.
- **`jasongzy/Mixamo` dataset**: gated ("auto"). The file listing shows Mixamo FBX animations (`animation/*.fbx`) and
  a VRM add-on zip. Last modified 2025-03-05. Its card is behind the gate. —
  [HF API](https://huggingface.co/api/datasets/jasongzy/Mixamo), *page read* (listing only, nothing downloaded).
- **Make-It-Animatable paper**: training uses "95 high-quality characters and 2,453 diverse motion sequences"
  collected from Mixamo and normalised to a shared 52-bone skeleton. It trained on 8 NVIDIA A100s, inference takes
  "less than 1 second", and the paper says nothing about Mixamo's terms. —
  [arXiv 2411.18197 HTML](https://arxiv.org/html/2411.18197), *page read*.
- The Make-It-Animatable README adds 3DBiCar samples "rigged by Mixamo" to training and credits Adobe Mixamo. —
  [README](https://github.com/jasongzy/Make-It-Animatable), *page read*.
- **Mixamo's terms (official FAQ)**: helpx.adobe.com returned 403. The search snippet says Mixamo is free with an
  Adobe ID and needs no Creative Cloud subscription; Enterprise and Federated IDs and China are excluded. Characters
  and animations are royalty-free for personal, commercial and non-profit work including games and films, and the
  auto-rigger supports bipedal humanoids only. —
  [helpx mixamo-faq](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html), *search snippet only*.
- **Mixamo community FAQ** (user TylerG 3D, 2022-09-29; not labelled Adobe staff on the page): "really the only thing
  you can't do is distribute the raw character and animation files"; "The only research application Mixamo content
  can't be used in is training machine-learning models". It is framed as the "limited technology preview". —
  [community.adobe.com](https://community.adobe.com/questions-696/mixamo-faq-licensing-royalties-ownership-eula-and-tos-589400), *page read*.
- In 2021-07-19 the same user wrote that the only prohibited uses are "re-selling Mixamo assets" or "bulk downloading
  all Mixamo content … to use for machine learning applications". —
  [community.adobe.com](https://community.adobe.com/questions-696/mixamo-character-and-animation-use-590037), *page read*.

Licence lines:
- UniRig weights — MIT — commercial: yes — [HF](https://huggingface.co/VAST-AI/UniRig)
- SkinTokens weights — MIT (with the Qwen3-0.6B backbone under Apache-2.0) — commercial: yes — [HF](https://huggingface.co/VAST-AI/SkinTokens)
- Puppeteer weights — Apache-2.0 — commercial: yes — [HF](https://huggingface.co/Seed3D/Puppeteer)
- MagicArticulate weights — Apache-2.0 — commercial: yes — [HF](https://huggingface.co/Seed3D/MagicArticulate)
- Make-It-Animatable weights — Apache-2.0 (code MIT); trained on Mixamo content — commercial: unclear —
  [HF](https://huggingface.co/jasongzy/Make-It-Animatable)

Assessment: the weights themselves are all permissive. The open question is upstream data: Mixamo's
community-stated no-ML-training rule for Make-It-Animatable, and UniRig's Rig-XL lists, which name Mixamo and VRoid
splits even though the released checkpoint is the Articulation-XL2.0 one. These are labels, not reasons to drop any
of them.

## 4 · Free-but-closed terms

### VRoid Studio (pixiv)
- vroid.com, vroid.pixiv.help and developer.vroid.com (`/en/guidelines/conditions_of_use.html`) all returned 403. *Blocked*.
- On Steam it is "Free To Play", runs on Windows 10/11 and macOS 11+, was released 2020-12-23, and "Requires
  agreement to a 3rd-party EULA". — [Steam store](https://store.steampowered.com/app/1486350/VRoid_Studio/), *page read*.
- The EULA, served by Steam, is an English translation (the Japanese original prevails), in effect from 2018-07-31
  and revised 2020-03-30. Art. 9(2): output items "shall belong to the Users who created such works". Art. 9(1): the
  software "will belong to the Company". Art. 5(6) bars "commercial use or secondary application" of the software,
  with exceptions including "Use of Software with purpose of use or production of Output Items". Art. 5(7) bars
  transferring, lending or licensing the software. It says nothing about AI training or bundled presets. —
  [Steam EULA 1486350_eula_0](https://store.steampowered.com/eula/1486350_eula_0), *page read*.
- On the App Store (iPad) it is "Free · In‑App Purchases". VRoid Plus subscriptions are listed at $4.99, $24.99 and
  $13.49. It needs iPadOS 17 and an A12 chip. Version 2.16.0 was listed "10h ago" on 2026-10-29. VRM 1.0 has been the
  default export since 2.3.0. "You can set your own terms of use for the data of every model, texture, item, etc you
  create". — [App Store](https://apps.apple.com/us/app/-/id6449727674), *page read*.
- Licence line: VRoid Studio — proprietary freeware EULA; output belongs to its creator — commercial use of output:
  yes, subject to the terms of any third-party parts used — [Steam EULA](https://store.steampowered.com/eula/1486350_eula_0)

### Mixamo (Adobe)
- See §3 above. The official FAQ is blocked (403), so the official terms rest on a search snippet; the
  community-FAQ lines are *page read*.
- Licence line: Mixamo — Adobe Terms of Use plus FAQ — commercial use in projects: yes; redistributing raw files:
  no; ML training: no (community FAQ) — [helpx FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html)

### Daz Studio and Genesis 9 (Daz 3D)
- Daz Studio is a free download that comes with Daz Install Manager. The page also lists a "Daz Studio Premier"
  product and Premier, Plus and Base memberships, without prices. — [daz3d.com/get_studio](https://www.daz3d.com/get_studio), *page read*.
- Genesis 9 Starter Essentials (product 86958, released 2022-10-19) "is included for free with your Daz Studio
  download". It contains the Genesis 9 figure, base anatomy, clothing, hair and materials, a Genesis 9 Toon figure
  and six character presets. The resolved-issues list says "Updated Utility Scripts to work with Daz Studio 6". No
  product licence is stated. — [docs.daz3d.com 86958](https://docs.daz3d.com/public/read_me/index/86958/start), *page read*.
- The Daz EULA (undated, © 2026) says users may not "give, sell, rent, lease, sublicense, or otherwise transfer or
  distribute any Content" without Daz's written consent. It "expressly excludes the use, incorporation, or input of
  any Content" in AI engines that generate derivative or imitative material. 3D prints are personal and
  non-commercial only. Under the Interactive License Addendum, cloud distribution and post-install content updates
  are allowed only for entities under $1M a year in revenue. — [daz3d.com/eula](https://www.daz3d.com/eula), *page read*.
- "An Interactive License is required when using or distributing 3D content from the Daz 3D store" in apps and
  games. Each product's creator chooses whether to offer one, and the standard licence covers rendered images, video
  and HDRI/VR scenes. — [interactive-license-info](https://www.daz3d.com/interactive-license-info), *page read*.
- Genesis 9 has 25,182 vertices and 25,156 polygons according to third-party listings. A Daz tutorial listing says
  "The Base Genesis 9 Figure is Gender Neutral" with a simplified skeleton. —
  [renderhub listing](https://www.renderhub.com/den/lt-g9-heads-and-bodies-vol-1-base-male-wavefront-obj-fit), *search snippet only*.
- Daz's bridges: `daz3d/DazToUnreal` is Apache-2.0 (pushed 2026-01-01, 187★). `daz3d/DazToBlender` has licence
  NOASSERTION (pushed 2025-09-04, 281★). — GitHub API, read 2026-10-29, *page read*.
- Licence lines: Daz Studio — proprietary freeware — commercial use: yes for renders — [get_studio](https://www.daz3d.com/get_studio).
  Daz content, Genesis 9 included — Daz EULA — commercial use: renders yes; 3D content inside an app conditional on a
  per-product Interactive License; AI-engine use no — [EULA](https://www.daz3d.com/eula)

### Blender's Rigify page, from the manual's source repo
- Source: `projects.blender.org/blender/blender-manual`, `manual/addons/rigify/`, read through the Gitea API and raw
  files. The HTML commit view returned 403; the API worked. Last commit 2026-10-20, "Rigify: Simple UI Tweaks with
  added descriptions". — [manual source](https://projects.blender.org/blender/blender-manual/src/branch/main/manual/addons/rigify), *page read*.
- Rigify builds rigs "out of smaller rig parts"; "once a rig is created, that rig should no longer need Rigify"; it
  "does not attach the rig to a mesh, so you still have to do skinning etc. yourself". Re-generating keeps modifiers
  and constraints and, where possible, earlier features. — `introduction.rst`, `basics.rst`, *page read*.
- The meta-rigs are Basic Human (no face or fingers), Basic Quadruped, Human, Cat, Wolf, Horse and Shark. "Rigify
  assumes that 1 unit corresponds to 1 meter." Face bones "are almost useless if you plan to make facial animation
  through shape keys". — `basics.rst`, *page read*.
- The legacy `faces.super_face` "is being deprecated in favor of a new modular skin and face rigging system"
  (`face.skin_eye`, `face.skin_jaw`, `face.basic_tongue`, plus `skin.*` chains). An "Upgrade Face Rig" button converts
  old rigs, keeping skinning compatibility but not existing poses. — `rig_types/faces.rst`, `rig_types/face.rst`,
  `basics.rst`, *page read*.
- Third-party "Feature Sets" add meta-rigs and rig types and install from zip files. — `feature_sets.rst`, *page read*.

## 5 · Not researched in round one

### Unreal's Mutable (Customizable Object)
- "Mutable is a built-in Unreal Engine plugin for creating highly customizable characters and other modular assets.
  It generates Skeletal Meshes, Materials, and Textures dynamically in the editor or at runtime". —
  [Mutable wiki Home](https://github.com/anticto/Mutable-Documentation/wiki), *page read*.
- Features: clip, reshape, morph baking, transform, merge (to cut CPU, memory and replication cost), texture
  projection, layering and packing, skeleton merging, metadata for data-driven UIs, cloth and physics editing,
  MetaHuman DNA and grooms. — [Use Cases](https://github.com/anticto/Mutable-Documentation/wiki/Use-Cases), *page read*.
- "With 5.8 we are releasing the plugin as production ready". 5.8 also adds a Skeletal Mesh pin, parallel updates,
  Chaos Cloth, and real-time morphs and skin-weight profiles on the Skeletal Mesh Parameter node, and deprecates
  Mutable streaming and manual LODs. — [What's New](https://github.com/anticto/Mutable-Documentation/wiki/What's-New), *page read*.
- FAQ: it ships no assets; it has no predefined skeleton; it does not modify animations; the Populations crowd plugin
  was discontinued; grooms are experimental; changing height with morphs is discouraged because skinning breaks (use
  the Reshape node or bone transforms). — [FAQ](https://github.com/anticto/Mutable-Documentation/wiki/FAQ), *page read*.
- Epic's news post of 2026-10-27 says Mutable is production-ready in UE 5.8, with a MetaHuman sample on the Ada
  preset. — [unrealengine.com news](https://www.unrealengine.com/news/mutable-sample-for-runtime-character-customization-now-updated-for-ue-5-8),
  *search snippet only* (the page returned 403).
- Epic docs say it has shipped since UE 5.1 as an experimental plugin and has been beta since 5.5. —
  [dev.epicgames.com](https://dev.epicgames.com/documentation/unreal-engine/mutable-overview-in-unreal-engine), *search snippet only*.
- Assessment: it works only in Unreal, under the Unreal EULA; no separate licence was found. It is a design reference
  for runtime part-merging, and a route candidate only if Unreal is the engine.

### Bevy character creators
- Searches of crates.io (`bevy` with makehuman, humanoid, character-creator, avatar) and GitHub (bevy character
  creator, makehuman, avatar customization) found **no Bevy character creator**, as of 2026-10-29. — crates.io API, `gh search repos`.
- `bevy_vrm` (MIT OR Apache-2.0, 0.5.0, updated 2026-10-13, 20,442 downloads) and `bevy_vrm1` (MIT OR Apache-2.0,
  0.11.0, updated 2026-10-29, 7,483 downloads) load VRM avatars. — [crates.io bevy_vrm](https://crates.io/crates/bevy_vrm),
  [bevy_vrm1](https://crates.io/crates/bevy_vrm1), *page read* (API).
- `symbios-avatar` (MIT, 0.14.0, created 2026-08-16, 1★) builds "Parametric humanoid and creature bodies, generated
  entirely from code — no base mesh". It goes from skeleton capsules to a quad-dominant cage to Catmull-Clark
  subdivision. `bevy_symbios_avatar` binds it to Bevy. — [repo](https://github.com/TheJanusStream/symbios-avatar), *page read*.

### Open strand-hair groom assets
- The MakeHuman "Hair editor" pack holds "Fur and hair styles for the hair editor": "The assets are shared under
  CC0." The packs page also lists CC0 Hair 01 (mostly low-poly stylised mesh hair), CC-BY Hair 02/03 (mesh hair), CC0
  high-res eyebrows and eyelashes, and many CC0 clothes and skins. —
  [assetpacks.html](https://static.makehumancommunity.org/assets/assetpacks.html), *page read*.
- MPFB2's hair editor lists 7 styles plus an empty template: short hedgehog, hair to shoulder, crown, short cap,
  short ponytail, back pigtail, tail base. — [hair_assets.json](https://github.com/makehumancommunity/mpfb2/blob/master/src/mpfb/ui/haireditorpanel/properties/hair_assets.json), *page read*.
  It is geometry-nodes hair, "experimental", and needs the hair editor asset pack (2.0.11 notes). —
  [release_2011](https://static.makehumancommunity.org/mpfb/releases/release_2011.html), *search snippet only*.
- DiffLocks (MPI, CVPR 2025) is a dataset of 40K synthetic Blender hairstyles. Its licence is a "Software Copyright
  License for non-commercial scientific research purposes"; commercial licensing goes through Meshcapade; download
  needs registration. — [difflocks licence](https://difflocks.is.tue.mpg.de/license.html), © 2025, *page read*.
- CT2Hair (Meta, SIGGRAPH 2023) has 10 CT-scanned wig hairstyles plus code. Its LICENSE is "Attribution-NonCommercial
  4.0 International", and it was last pushed 2023-08-01. — [CT2Hair](https://github.com/facebookresearch/CT2Hair), *page read*.
- MetaHuman groom packs on Fab include a free sample ("MetaHuman Hairstyle Male 11 Groom", .mhpkg plus Alembic); its
  licence was not seen. — [fab.com](https://www.fab.com/listings/d92a0df0-61a8-4b3a-93ea-18bc62bb80a8), *search snippet only*.
- Blender Studio's Snow rig is CC-BY, but no groom is mentioned. —
  [studio.blender.org/characters/snow](https://studio.blender.org/characters/snow/), *search snippet only*.
- Assessment: MakeHuman's 7 CC0 hair-editor styles are the only permissive strand grooms found. Everything scan- or
  dataset-grade is non-commercial.

### Meshcapade's commercial SMPL terms
- SMPL-X model licence: "non-commercial scientific research, non-commercial education, or non-commercial artistic
  projects"; "The software/data is also available for commercial licensing through Meshcapade.com". It also bars
  training networks for commercial, military, surveillance or similar uses. —
  [smpl-x modellicense](https://smpl-x.is.tue.mpg.de/modellicense.html), © 2024, *page read*.
- The SMPL model licence is likewise "non-commercial scientific research" only, with commercial use through
  Meshcapade. — [smpl modellicense](https://smpl.is.tue.mpg.de/modellicense.html), © 2024, *page read*.
- Prices from a Meshcapade Notion page, which renders empty to scripted reads: separate commercial and R&D licences,
  tiered by company size. Micro: commercial €5,000 a year, R&D €1,500. SME: R&D €32,500, commercial on request.
  Enterprise on request. The R&D licence excludes product development, integration and redistribution. —
  [Notion page](https://meshcapade.notion.site/The-SMPL-Model-Licenses-2144560e54388085af5eff111fcdf266), *search snippet only*.
- Meshcapade's avatar-tech page (403) lists an add-on body-model commercial fee of €2,000 a year (Micro) and €10,000
  a year (SME). — [meshcapade.com](https://meshcapade.com/assets/avatar-tech), *search snippet only*.
- Licence line: SMPL / SMPL-X — MPI non-commercial research licence; commercial use only through a paid Meshcapade
  licence — commercial: no (paid licence needed) — [smpl-x](https://smpl-x.is.tue.mpg.de/modellicense.html)
- Assessment: commercial use is paid-only, so under the user's scope the SMPL family is no base option. It stays a
  labelled interop target, with users supplying their own licensed files, as SOMA-X already does.

### ATLAS (Meta / CMU)
- "ATLAS has been integrated into MHR, which is now released." The page's code link points to
  `facebookresearch/MHR`. ATLAS was "learned from 600k high-resolution scans captured using 240 synchronized cameras"
  and has non-linear pose correctives. — [ATLAS project page](https://jindapark.github.io/projects/atlas/), *page read*.
- Assessment: ATLAS has no code or licence of its own; it lives on as MHR (Apache-2.0).

## 6 · Conflicts settled

### Humanizer's licence (AGPL-3.0 file vs CC0 listing)
- The history of `LICENSE`: initial commit 2024-03-03 under the Unlicense ("free and unencumbered software released
  into the public domain"); 2025-01-18 "Create LICENSE", CC0 1.0 Universal; 2025-08-26 "change LICENSE to match
  makehuman (AGPL)", AGPL-3.0. — `gh api repos/NitroxNova/humanizer/commits?path=LICENSE` and contents at each SHA,
  read 2026-10-29, *page read*.
- The Godot Asset Library API for asset 3699 gives `"cost": "CC0"`, version 2.2.0, Godot 4.3, modified 2025-02-13. —
  [asset-library API](https://godotengine.org/asset-library/api/asset/3699), *page read*.
- Settled: the listing describes v2.2.0 from the CC0 period; the repo has been AGPL-3.0 since 2025-08-26.
  Licence line: Humanizer — v2.2.0 CC0 (commercial: yes); main since 2025-08-26 AGPL-3.0 (commercial: conditional) —
  [repo](https://github.com/NitroxNova/humanizer)

### Rocketbox's body-bone count (56 vs 53)
- The paper says both: Fig. 5's caption has "53 body bones and 28 facial bones", and §5's text has "56 body bones". —
  [Frontiers 2020](https://www.frontiersin.org/articles/10.3389/frvir.2020.561558/full), *page read*.
- Headbox's `Maya/DeltaValues/AK_01_BrowDownLeft.json` has keys for 82 distinct nodes: 28 facial bones, 53 body
  bones and the Biped helper "Bip01 Footsteps" (my count). The body set is Bip01, Pelvis, Spine, Spine1, Spine2, Neck
  and Head, plus per side Clavicle, UpperArm, Forearm, Hand, 15 finger bones (Finger0–4, three each), Thigh, Calf,
  Foot and Toe0. — [Headbox](https://github.com/openVRlab/Headbox), *page read* (one JSON file of bone deltas, no mesh).
- MoveBox's Kinect mapping uses the same `Bip01 …` naming. —
  [KinectMoCapRocketboxAvatar.cs](https://github.com/microsoft/MoveBox-for-Microsoft-Rocketbox), *page read*.
- Settled: **53 body + 28 facial bones**, matching the figure caption. *Inference, unverified:* the 56 probably adds
  Biped helper or end nodes (Footsteps, nubs).

## 7 · GPU vendors for SOMA-X, UniRig, SkinTokens and LHM

### SOMA-X
- The model card's hardware list is NVIDIA Ampere, Hopper, Ada, Turing and Volta, "Any NVIDIA GPU with CUDA support",
  and "CPU only (PyTorch fallback, no CUDA required)". The OS list is Linux and "Windows (via PyTorch CPU/GPU path)".
  No AMD, Intel or Apple GPU and no macOS appear. —
  [model_card.md](https://github.com/NVlabs/SOMA-X/blob/main/docs/model_card.md), *page read*.
- NVIDIA Warp ships wheels for Windows x86-64 and Linux (CPU and CUDA). Its macOS wheels "support CPU execution but
  not Metal acceleration". — [warp README](https://github.com/NVIDIA/warp), *page read*.
- The developer install uses the PyTorch `cu124` wheel index. —
  [installation.md](https://github.com/NVlabs/SOMA-X/blob/main/docs/installation.md), *page read*.
- No issues mention AMD, ROCm, Mac or MPS. — `gh search issues`, 2026-10-29.
- Label: GPU — NVIDIA (Warp/CUDA); CPU — any vendor; AMD, Intel and Apple GPUs — not documented.

### UniRig
- Upstream needs a "CUDA-enabled GPU with at least 8GB VRAM", plus `spconv`, `torch_scatter` and `torch_cluster` CUDA
  builds and `flash_attn`. — [README](https://github.com/VAST-AI-Research/UniRig), pushed 2026-06-04, *page read*.
- `fernandotonon/QtMeshEditor-unirig-onnx` (MIT, 2026-07-10) is an ONNX re-export of the skeleton stage only. It runs
  on ONNX Runtime inside QtMeshEditor; the skin head "depends on spconv/PTv3, which has no ONNX lowering". —
  [HF card](https://huggingface.co/fernandotonon/QtMeshEditor-unirig-onnx), *page read*.
- `cgb/unirig-skeleton-onnx-webgpu` (MIT, 2026-09-04) is the skeleton stage at int8, running "entirely inside a web
  browser on WebGPU". — [HF card](https://huggingface.co/cgb/unirig-skeleton-onnx-webgpu), *page read*.
- Label: upstream — NVIDIA only; skeleton stage — any vendor through third-party ONNX or WebGPU ports; skinning —
  NVIDIA only.

### SkinTokens / TokenRig
- Upstream: "An NVIDIA GPU with at least 14 GB of memory is required for inference"; CUDA ≥ 12.1; flash-attn. —
  [README](https://github.com/VAST-AI-Research/SkinTokens), pushed 2026-05-12, *page read*.
- `localai-org/skin-tokens.cpp` (Apache-2.0, created 2026-08-28, pushed 2026-10-19, 232★) does "automatic skeleton
  and skin-weight generation on CPU or Vulkan" with `--device vulkan|cpu|auto` and a C ABI. It reports parity with
  the reference, for example 7.1e-4 relative L2 on Vulkan. —
  [README](https://github.com/localai-org/skin-tokens.cpp), *page read*.
- The GGUF F16 weights for that port: mesh encoder 57.8 MB, TokenRig 948.6 MB, skin VAE 244.0 MB (MIT). —
  [LocalAI-io/SkinTokens-GGUF](https://huggingface.co/LocalAI-io/SkinTokens-GGUF), *page read*.
- `fernandotonon/QtMeshEditor-skintokens-onnx` (MIT) is QtMeshEditor's default skinner on ONNX Runtime. —
  [HF card](https://huggingface.co/fernandotonon/QtMeshEditor-skintokens-onnx), *page read*.
- `mlx-community/SkinTokens-bf16` (MIT) is a Swift-MLX port for Apple Silicon. Its runtime,
  `xocialize/mlx-engine-swift`, says "not ready for use". —
  [HF card](https://huggingface.co/mlx-community/SkinTokens-bf16), [repo](https://github.com/xocialize/mlx-engine-swift), *page read*.
- Label: upstream — NVIDIA only (14 GB+, above this machine's 8 GB); through skin-tokens.cpp — CPU plus Vulkan
  (NVIDIA, AMD, Intel); Apple — MLX port, not ready.

### LHM / LHM++
- Tested with "python3.10, CUDA 11.8 or CUDA 12.1". Install pulls in `diff-gaussian-rasterization` and `simple-knn`
  (CUDA extensions), `pytorch3d` and `xformers`. — [README](https://github.com/aigc3d/LHM), install scripts, *page read*.
- The model card says the service needs a 16–22 GB GPU (24 GB VRAM listed). The output is Gaussian points (20K for
  MINI, 40K otherwise), with Sapiens-1B and DINOv2 image encoders, trained on 2K2K, RP, THuman and 300K videos. —
  [modelcard.md](https://github.com/aigc3d/LHM/blob/main/modelcard.md), *page read*.
- Maintainer on 2025-03-21: "Our LHM is currently not supported on Mac systems". On 2025-05-16: Mac support will come
  in future. — [issue #11](https://github.com/aigc3d/LHM/issues/11), [issue #125](https://github.com/aigc3d/LHM/issues/125), *page read*.
- Sapiens' LICENSE is "Creative Commons Attribution-NonCommercial 4.0 International", and its HF checkpoints are
  tagged cc-by-nc-4.0. — [sapiens LICENSE](https://github.com/facebookresearch/sapiens), *page read*.
- LHM's HF weights are tagged apache-2.0 (LHM-MINI is untagged). Animation is driven by SMPL-X parameters, and
  `inference_mesh.sh` exports a mesh. — HF API, README, *page read*.
- Label: NVIDIA only. Licence note: the weights are Apache-2.0, but the pipeline needs Sapiens (CC-BY-NC-4.0) and
  SMPL-X (non-commercial).

### A side find for the lead (S6/S7, not S4)
- QtMeshEditor (MIT, pushed 2026-10-29, 64★) is a Qt 3D asset tool with a "MCP server — 57+ tools for AI agents" and
  an opt-in localhost REST API. It runs UniRig, SkinTokens and NVIDIA Audio2Face-3D locally through ONNX. —
  [README](https://github.com/fernandotonon/QtMeshEditor), *page read*.

## Couldn't verify / open

- **Realism against CC5 and MetaHuman:** not findable. I searched for comparisons of MPFB2/MakeHuman, CharMorph,
  Rocketbox, Anny, MHR and GNM against CC or MetaHuman, and for user studies, Blender Artists threads, reviews and
  showcases. reddit.com is unreachable by this tool. The one perception survey found covers no open base.
- **Deformation edge loops:** no source documents the edge-loop layout for hm08, MHR, SOMA-X or GNM. MakeHuman says
  only "optimized for animation".
- **Whether MHR's FBX polygons are quads:** not stated. The evaluated model is triangles.
- **Whether GNM's quad topology is all-quad:** not stated beyond the data having `quads` and `triangles` fields.
- **MB-Lab's exact vertex counts:** not in any doc. The ~18.2k / ~18.0k figures above are file-size inferences;
  morphs are "about 470" per character for v1.5.0 only.
- **Mixamo's official FAQ text:** helpx 403, so the official terms rest on a search snippet. The ML-training
  restriction rests on non-staff community posts (2021, 2022).
- **VRoid's Hub conditions and preset-asset terms:** developer.vroid.com 403. The Steam EULA covers the software and
  output only.
- **Meshcapade's prices:** snippet only; the two pages differ, and both refused scripted reads.
- **Mutable's licence:** no separate licence found (assumed to fall under the Unreal EULA). Epic's own pages were
  403 or rendered empty.
- **USC-HairSalon's terms:** not found.
- **SOMA-X's PyTorch GPU fallback on ROCm or MPS:** untested and undocumented.
- **Genesis 9's own counts:** third-party listings only. The Daz Studio 6 versus "Daz Studio 2025" naming is left to
  S3.
