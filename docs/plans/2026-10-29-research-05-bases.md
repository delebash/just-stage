# Research 05 — Existing bases to build on (open human models, creators, rigging tools)

Research notes for JustStage, 2026-10-29. Feeds `docs/dev/RESEARCH.md` §5 (not edited by this agent).
Scope changes applied (coordinator, from the user, 2026-10-29): candidates that **only come paid are OUT**
(one line each); free-but-proprietary candidates keep normal rows, with their terms labelled; research
models under non-commercial licences stay, labelled. The user also ruled Omniverse out because it only
runs on NVIDIA cards, so every NVIDIA/CUDA dependency below is labelled **NVIDIA-only**.

Method: GitHub's API through `gh api` (repo JSON, releases, commits, contributors, LICENSE and README
files, file trees), arXiv HTML pages, project pages. "page read" = the primary page or file was opened;
"search snippet only" = seen only in a search-result summary. All GitHub figures were read 2026-10-29
unless a date is given. RESEARCH.md §5 facts (MPFB2, MakeHuman, MB-Lab, CharMorph health; "web,
2026-10-29") were not re-derived. **The session's web-search budget ran out partway through**, so several
proprietary-terms checks and realism comparisons are still open (last section).

## Top findings

1. **MakeHuman's assets are CC0, and they are the only open, actively kept, morph-rich, all-ages
   body base with an ARKit-52 face set.** MPFB2 ships 1,258 target files (my count of
   `src/mpfb/data/targets`), 52 ARKit face units, 22 + 15 visemes and 8 standard rigs plus Rigify. Assets
   and output are CC0; the code is GPL-3. — [MPFB2 LICENSE.md](https://github.com/makehumancommunity/mpfb2/blob/master/LICENSE.md), [faceops doc](https://github.com/makehumancommunity/mpfb2/blob/master/docs/ui/operations/faceops.md), [cgchannel 2025-03-11](https://www.cgchannel.com/2025/03/check-out-open-source-blender-character-generation-plugin-mpfb-2)
2. **NAVER's Anny (Apache-2.0 code, CC0 data) proves the MakeHuman data runs outside Blender.** It is a
   PyTorch body model on the MakeHuman mesh (13,718 verts, 13,710 quads, eyes and tongue included). It
   has 163-bone and 104-bone rigs, up to 267 phenotype parameters, ages from infants to elders, and ARKit-named
   facial actions. Its latest version is v0.6.1 (2026-09-28). — [naver/anny README](https://github.com/naver/anny), [arXiv 2511.03589](https://arxiv.org/html/2511.03589v2), [CHANGELOG](https://github.com/naver/anny/blob/main/CHANGELOG.md)
3. **Meta's MHR (Apache-2.0) is the most production-like open scan-trained body.** It has 7 LODs
   (73,639 down to 595 verts), 127 joints, 72 FACS-based expressions, neural pose correctives and an FBX per LOD.
   It has no eyeballs, no mouth interior and no textures. Its identity space is small: 45 parameters.
   — [facebookresearch/MHR](https://github.com/facebookresearch/MHR), [arXiv 2511.15586](https://arxiv.org/html/2511.15586)
4. **NVIDIA's SOMA-X (Apache-2.0 code and assets, created 2026-03) puts MHR, Anny and SMPL on one
   77-joint UsdSkel rig.** Its mid LOD has 18,056 verts. The fast path is NVIDIA Warp (NVIDIA-only); a PyTorch
   CPU fallback exists (12.1 ms per mesh). — [NVlabs/SOMA-X](https://github.com/NVlabs/SOMA-X), [data_assets.md](https://github.com/NVlabs/SOMA-X/blob/main/docs/data_assets.md), [model_card.md](https://github.com/NVlabs/SOMA-X/blob/main/docs/model_card.md)
5. **Google's GNM Head (Apache-2.0, 2026) is a new open scan-based head model.** It covers eyeballs, teeth,
   tongue and neck, and samples identities by gender and ethnicity. Its repo was created 2026-03-23 and
   last pushed 2026-10-29 (1,612 stars). Body models are on its roadmap. — [google/GNM](https://github.com/google/GNM), [arXiv 2607.23687](https://arxiv.org/abs/2607.23687)
6. **ICT-FaceKit (MIT) gives a light-stage-scanned face with ARKit-named expressions.** It also has full eye,
   teeth, gum and eyelash geometry in the UE Digital Human style, but it has been unmaintained since 2020-12. — [USC-ICT/ICT-FaceKit](https://github.com/USC-ICT/ICT-FaceKit)
7. **FLAME 2023 Open (2025-11) is CC-BY-4.0.** Earlier FLAME versions, and SMPL-X, STAR and SUPR, are
   non-commercial research licences. — [flame.is.tue.mpg.de](https://flame.is.tue.mpg.de/), [vchoutas/smplx](https://github.com/vchoutas/smplx), [ahmedosman/STAR](https://github.com/ahmedosman/STAR)
8. **MB-Lab is archived and handed off to CharMorph, and both carry AGPL-3 mesh and morph data.** CharMorph
   also has CC-BY bases (Antonia, Reom), but its last release was 2025-03. — [MB-Lab license.txt](https://github.com/animate1978/MB-Lab/blob/master/license.txt), [CharMorph-db](https://github.com/Upliner/CharMorph-db)
9. **MakeHuman 2 (standalone Python, PySide6 + OpenGL; AGPL code, CC0 assets) is in alpha and active**
   (pushed 2026-10-07). It plans glTF, PBR, animation and more base meshes. — [makehumancommunity/makehuman2](https://github.com/makehumancommunity/makehuman2)
10. **Microsoft Rocketbox (MIT, archived 2022) has 115 rigged, textured, realistic but low-poly avatars.**
    Hipoly is 10k triangles. There are 28 face bones, and ARKit blendshapes were added in 2022. Clothes are
    baked into the mesh, so these are library content, not a creator base. — [Microsoft-Rocketbox](https://github.com/microsoft/Microsoft-Rocketbox), [Frontiers 2020](https://www.frontiersin.org/articles/10.3389/frvir.2020.561558/full)
11. **Blender Studio's Human Base Meshes (CC0) are clean quad realistic and stylised meshes with multires
    detail and UDIM UVs.** They have no morph system and no rig (none stated). — [cgchannel 2023-06-28](https://www.cgchannel.com/2023/06/download-blender-studios-free-human-base-meshes)
12. **Open auto-riggers exist, but most are NVIDIA-only (CUDA):** UniRig (MIT, at least 8 GB), its successor
    SkinTokens/TokenRig (MIT, at least 14 GB), Puppeteer and MagicArticulate (Apache-2.0) and Make-It-Animatable (MIT).
    Rigify (GPL-2.0+) is a core Blender add-on, last committed 2026-10-19. — repos linked below
13. **No source found compares any open base's realism with CC5 or MetaHuman.** The only lead is a forum
    opinion that rates CC at about 85% photoreal and MetaHuman at about 95% (search snippet only). — [forum.reallusion.com](https://forum.reallusion.com/503486/Forum37.aspx)
14. **OUT as paid only:** Human Generator ($68 personal / $128 commercial, no free version) and Auto-Rig Pro
    ($25 Lite / $50 Full, no free version). — [Superhive HG](https://superhivemarket.com/products/humgen3d), [Superhive ARP](https://superhivemarket.com/products/auto-rig-pro)
15. **Free but proprietary:** MetaHuman (free under the UE EULA below $1M revenue, usable in other
    engines, no AI training) and VRoid Studio (free, anime style, closed source). JustStage could never
    ship their assets; at most they are something a user imports. — [cgchannel 2025-06-04](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/), [MoguraVR 2026-06](https://www.moguravr.com/vroid-studio-v2-14-0-ipad-ads-vroid-plus-en/)

## Comparison table

Code and asset licences: "C" = commercial use, rated yes / conditional / no / unclear. NVIDIA-only = needs
CUDA or another NVIDIA path.

| Candidate | Covers | Morph count | Topology / verts | Rig + face rig | Realism | Tech | Health | Code licence | Asset licence | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| **MPFB2** (MakeHuman for Blender) | body, face, hands; clothes, hair (editor experimental, hair cards), eyes (procedural), teeth/tongue (hm08 groups); skin PBR+SSS | 1,258 target files; 257 labelled sliders in `target.json` (my counts); 31 asym sliders new in 2.0.18 | hm08 quads, ~13.7k verts (Anny figure) | 8 standard rigs (default, no-toes, game_engine, +breast, cmu_mb, mixamo, mixamo_unity, openpose) + Rigify; face: ARKit 52, MS visemes 22, Meta visemes 15 (shape keys) | stylised-realistic, artist-made; no scan detail found | Python, Blender add-on (bpy only) | v2.0.18 2026-10-11; push 2026-10-24; 671★ (RESEARCH §5) | GPL-3.0 (C: conditional) | CC0 1.0 (C: yes); output CC0 | [repo](https://github.com/makehumancommunity/mpfb2) |
| **Anny** (NAVER) | body, face, hands (part models); no clothes | up to 267 phenotype params; ARKit-named facial actions | MakeHuman quads 13,718 v / 13,710 f; default triangulated; alt. topologies smpl/smplx/soma | 104-bone `anny` rig or 163-bone MakeHuman rig; face = blendshapes (faceunits) | same mesh as MakeHuman; paper fits scans to 2.4 mm | Python/PyTorch library, host-free | v0.6.1 2026-09-28 (changelog, no GH releases); push 2026-10-26; 612★; 6 contributors | Apache-2.0 (C: yes) | CC0 (MakeHuman, faceunits); smplx topology non-commercial | [repo](https://github.com/naver/anny) |
| **MHR** (Meta) | body, face, hands; no eyes, no mouth interior, no clothes/hair | 45 identity + 72 expression + 204 pose/skeleton params | 7 LODs 73,639 → 595 v; face type not stated | 127 joints; 72 FACS-based expressions; neural pose correctives | scan-trained (7,110 body scans) | Python/PyTorch + pymomentum (C++); FBX/glTF export | v1.0.1 2025-11-19; last commit 2026-10-26; 885★; 9 contributors | Apache-2.0 (C: yes) | Apache-2.0 (README "MHR is licensed under Apache 2.0") | [repo](https://github.com/facebookresearch/MHR) |
| **SOMA-X** (NVIDIA) | body + hands; identity backends MHR/Anny/SOMA/SMPL | native PCA identity; hand 20 components | mid LOD 18,056 v, triangles; 3 LODs | 77 controllable joints (78 legacy) + procedural twists, UsdSkel | depends on backend | Python; Warp GPU path (NVIDIA-only), PyTorch CPU fallback | created 2026-03-03; push 2026-10-09; 847★ | Apache-2.0 (C: yes) | HF nvidia/SOMA-X apache-2.0 (C: yes) | [repo](https://github.com/NVlabs/SOMA-X) |
| **MakeHuman 1** | as MPFB2 (standalone) | as MPFB2 | hm08 | default rigs | as MPFB2 | Python standalone app | v1.3.0 2024-05-15; push 2024-08-19 (RESEARCH §5) | AGPL-3.0 (C: conditional) | CC0 (C: yes) | [repo](https://github.com/makehumancommunity/makehuman) |
| **MakeHuman 2** | as MakeHuman + planned PBR, animation, more base meshes | shares MPFB2 assets | hm08 kept compatible, "no longer identical" | — | — | Python + PySide6 + OpenGL standalone; glTF export | "Alpha III"; Alpha2 pre-release 2026-05-05; push 2026-10-07; 88★ | AGPL (C: conditional) | CC0 (C: yes) | [repo](https://github.com/makehumancommunity/makehuman2) |
| **MB-Lab** | body, face; Caucasian/Asian/African/Latin, anime, fantasy bases; hair; expressions; BVH poses | per-character morph files (not counted) | not found | own rig + face rig (`facial_rig.blend`, `facs_au.json`) | realistic-leaning (no evidence) | Python, Blender 4.0 add-on | **archived**; last 1_8_1 2024-06-08 (RESEARCH §5) | GPL-3.0 (C: conditional) | AGPL-3.0 data (C: conditional) | [repo](https://github.com/animate1978/MB-Lab) |
| **CharMorph** | body, face; hair; real-time asset fitting | not counted | per-character; "alternative topology" morph transfer | Rigify with full face rig (added at finalisation) | as MB-Lab | Python, Blender add-on | v0.4.0-3 2025-03-27; push 2025-05-29; db push 2024-07-23 | GPL-3.0 (C: conditional) | per character: MB-Lab AGPL-3; Antonia CC-BY 3.0; Reom CC-BY (C: conditional) | [repo](https://github.com/Upliner/CharMorph) |
| **Rocketbox** (Microsoft) | 115 full avatars, clothes baked in; 417 animations | blendshapes: 15 visemes, 48 FACS, 30 Vive, ARKit set (2022) | 10k / 5k / 2.5k / 500 tris | 53 or 56 body bones (paper conflicts) + 28 face bones | realistic, low-poly VR; 2048 px textures | FBX (3ds Max origin) + Unity/Unreal import tools | **archived** 2022-10-02; 654★ | MIT (C: yes) | MIT (C: yes) | [repo](https://github.com/microsoft/Microsoft-Rocketbox) |
| **ICT-FaceKit** (USC ICT) | head + neck, eyes, teeth, gums/tongue, eyelashes, eye occlusion | 100 identity PCA modes + ARKit-named expressions (L/R split) | face 9,409 v; full model ~26.7k v | blendshapes only | light-stage scans; UE digital-human-style eyes | Python toolkit | last commit 2020-12-01; 771★ | MIT (C: yes) | MIT (C: yes) | [repo](https://github.com/USC-ICT/ICT-FaceKit) |
| **GNM Head** (Google) | head, face, neck, eyeballs, teeth, tongue | identity + expression blendshapes (counts not found) | not found | neck + eye joints | scan-based ("SotA scan fitting", claim) | NumPy/JAX/PyTorch/TF; CI on Win/macOS/Linux | created 2026-03-23; push 2026-10-29; 1,612★ | Apache-2.0 (C: yes) | Apache-2.0 per README (C: yes) | [repo](https://github.com/google/GNM) |
| **FLAME** (MPI) | head + jaw, neck, eyeballs | 300 shape / 100 expression | not stated this session | jaw, neck, eye joints | scan-trained (3,800 scans) | Python | 2023 Open released 2025-11 | varies by repo | 2023 Open: CC-BY-4.0 (C: yes); older: non-commercial (C: no) | [site](https://flame.is.tue.mpg.de/) |
| **SMPL-X / STAR / SUPR** (MPI) | body, hands, face (SMPL-X) | PCA shape + expression | SMPL-X 10,475 v, 54 joints | joint-based; no artist face rig | scan-trained, research | Python | smplx last commit 2023-10-12, 2,748★; STAR push 2024-02; SUPR 2024-09 | non-commercial (C: no) | non-commercial (C: no) | [smplx](https://github.com/vchoutas/smplx) |
| **Blender Human Base Meshes** | 17 meshes: male/female bodies, heads, hands, feet, jaws, eyeballs; realistic + stylised | none | clean quads, closed, multires detail, UDIM UVs | none stated | realistic sculpt detail on realistic set | .blend asset library | v1.4.1 2025-01-20 (search snippet) | — | CC0 (C: yes) | [cgchannel](https://www.cgchannel.com/2023/06/download-blender-studios-free-human-base-meshes) |
| **Rigify** | rig generator (metarigs → control rigs) | — | — | human metarig, face rig (manual unreadable, 403) | — | Python, core Blender add-on | in Blender main; v0.6.10; last commit 2026-10-19 | GPL-2.0-or-later (C: conditional) | — | [blender repo](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/rigify) |
| **UniRig → SkinTokens** (VAST) | auto skeleton + skin weights for any mesh | — | — | predicted skeleton + weights | — | Python/PyTorch; NVIDIA-only (CUDA, spconv); ≥8 GB / ≥14 GB | UniRig push 2026-06-04, 1,908★; SkinTokens push 2026-05-12, 553★ | MIT (C: yes) | weights on HF (licence not checked) | [UniRig](https://github.com/VAST-AI-Research/UniRig) |
| **Puppeteer / MagicArticulate** (Seed3D) | auto rig + video-guided animation | — | — | predicted | — | Python/PyTorch (CUDA assumed, not checked) | push 2025-09; 439★ / 418★ | Apache-2.0 (C: yes) | checkpoints on HF (licence not checked) | [Puppeteer](https://github.com/Seed3D/Puppeteer) |
| **Make-It-Animatable** | humanoid auto-rig to Mixamo-style skeleton | — | — | Mixamo bones | — | Python/PyTorch; Hunyuan3D 2.1 ShapeVAE | push 2026-09-08; 468★; 1 contributor | MIT (C: yes) | trained on Mixamo data (terms not checked) | [repo](https://github.com/jasongzy/Make-It-Animatable) |
| **SAM 3D Body** (Meta) | image → MHR body mesh | — | MHR | MHR | — | Python/PyTorch | ~2025-11-19 licence date; push 2026-02-19; 3,658★ | SAM License (custom; royalty-free incl. derivatives; trade-control limits) (C: yes, conditional) | same | [repo](https://github.com/facebookresearch/sam-3d-body) |
| **LHM / LHM++** (Alibaba) | image → animatable human avatar | — | output form not verified | SMPL-family driven (not verified) | — | Python; NVIDIA-only GPU 14–24 GB (LHM++: 8 GB) | push 2026-03-17; 2,690★ | Apache-2.0 (C: yes) | data "license available" pending | [repo](https://github.com/aigc3d/LHM) |
| **VRM stack** (UniVRM, Blender add-on, three-vrm) | open avatar format + tools | VRM expressions | — | VRM humanoid | stylised | C# / Python / TS | UniVRM v0.131.4 2026-10-19; Blender add-on v4.10.3 2026-10-29; three-vrm push 2026-10-22 | MIT (C: yes) | n/a; CC0/CC-BY VRM avatars listed at opensourceavatars.com | [UniVRM](https://github.com/vrm-c/UniVRM) |
| **UMA** | Unity runtime character system (DNA, slots, atlasing) | DNA (count not found) | own meshes | Unity humanoid | not assessed | C#, Unity 6.3+ only | v3.1f3 2026-10-09; 870★; 35 contributors | MIT (C: yes) | MIT repo (bundled meshes' terms not checked) | [repo](https://github.com/umasteeringgroup/UMA) |
| **Humanizer** (Godot) | MakeHuman → Godot 4.3 creator | MakeHuman targets | hm08 | MakeHuman rigs | as MakeHuman | GDScript, Godot add-on | v2.2.0 2025-02-09; last commit 2025-11-07; 295★ | AGPL-3.0 (LICENSE file) (C: conditional); Godot listing says CC0 — conflict | MakeHuman CC0 | [repo](https://github.com/NitroxNova/humanizer) |
| **MetaHuman** (Epic) — free, proprietary | realistic body, face, hair, clothes | many (not counted) | — | full face rig | top-tier (CC is rated below it in the forum lead) | inside Unreal 5.6+ | web app shut down 2026-11-05 (snippet) | proprietary, UE EULA | free below $1M revenue; other engines OK; no AI training (C: conditional) | [cgchannel](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/) |
| **VRoid Studio** (pixiv) — free, proprietary | anime-style creator | — | — | VRM | stylised | closed app: Windows, macOS, iPad | v2.14.0 2026-06-29 (snippet) | proprietary | terms not verified (vroid.com refused, 403) | [MoguraVR](https://www.moguravr.com/vroid-studio-v2-14-0-ipad-ads-vroid-plus-en/) |
| ~~Human Generator~~ | **OUT: paid only** ($68 / $128) | | | | | | | | | [Superhive](https://superhivemarket.com/products/humgen3d) |
| ~~Auto-Rig Pro~~ | **OUT: paid only** ($25 / $50) | | | | | | | | | [Superhive](https://superhivemarket.com/products/auto-rig-pro) |

## Per-candidate facts

### MPFB2 (MakeHuman Plugin for Blender)
- RESEARCH.md §5 already holds its health (v2.0.18 2026-10-11, push 2026-10-24, 671★); not re-derived.
- The licence has two parts, "MPFB uses the same license setup as MakeHuman, but with GPLv3 as source code license". The assets file is CC0 1.0 and the code file is GPL-3.0 — [LICENSE.md, LICENSE.ASSETS.md, LICENSE.CODE.md](https://github.com/makehumancommunity/mpfb2) (repo files, read 2026-10-29), page read.
- Content made with it is CC0 and can be used commercially, including in closed-source games — [cgchannel, 2025-03-11](https://www.cgchannel.com/2025/03/check-out-open-source-blender-character-generation-plugin-mpfb-2), page read.
- `src/mpfb/data/targets` holds 1,258 `.target` files. By folder: macrodetails 348, breast 228, expression 102, eyes 68, asym 62, legs 58, arms 50, mouth 44, ears 44, nose 42, torso 34, feet 30, head 27, hands 22, neck 20, cheek 16, chin 15, hip 14, stomach 8, forehead 8, genitals 6, eyebrows 6, pelvis 4, buttocks 2 — my count from the [GitHub tree API](https://github.com/makehumancommunity/mpfb2/tree/master/src/mpfb/data/targets) (2026-10-29), page read.
- `targets/target.json` defines 23 groups with 257 labelled slider entries (my count); many entries are left/right pairs — [target.json](https://github.com/makehumancommunity/mpfb2/blob/master/src/mpfb/data/targets/target.json) (2026-10-29), page read.
- 2.0.18 exposes the 62 asym files as 31 sliders (−1 = full left, +1 = full right). The hair editor works on Blender 4.2–5.2, and hair renders in EEVEE on 5.x — [release notes 2.0.18, 2026-10-10](https://static.makehumancommunity.org/mpfb/releases/release_2018.html), page read.
- FaceService loads 22 Microsoft visemes, 15 Meta visemes and the 52 ARKit face units (`faceunits01` asset pack) as shape keys, and carries them over to clothes and proxies — [faceservice.md](https://github.com/makehumancommunity/mpfb2/blob/master/docs/services/faceservice.md), [faceops.md](https://github.com/makehumancommunity/mpfb2/blob/master/docs/ui/operations/faceops.md) (repo docs, 2026-10-29), page read.
- Shipped rigs: standard `default`, `default_no_toes`, `game_engine`, `game_engine_with_breast`, `cmu_mb`, `mixamo`, `mixamo_unity`, `openpose` (each with a weights file), plus Rigify `human` and `human_toes` — [data/rigs tree](https://github.com/makehumancommunity/mpfb2/tree/master/src/mpfb/data/rigs) (2026-10-29), page read.
- The skin is an "enhanced (PBR + subsurface scattering) skin shader" node group. A simpler MakeSkin material and a procedural-eyes node tree also ship — [enhancedskinmaterial.md](https://github.com/makehumancommunity/mpfb2/blob/master/docs/entities/material/enhancedskinmaterial.md), page read.
- Hair: the hair editor service is "experimental"; hair-card and hair-bake services exist in `src/mpfb/services` — [haireditorservice.md](https://github.com/makehumancommunity/mpfb2/blob/master/docs/services/haireditorservice.md), page read.
- Sliders cover age, build, gender and ethnicity; export goes to any Blender format (Alembic, glTF, USD, FBX…); 2.0.8 (2025-01) was the first stable release — [cgchannel, 2025-03-11](https://www.cgchannel.com/2025/03/check-out-open-source-blender-character-generation-plugin-mpfb-2), page read.
- Tech: the code is built on Blender's `bpy` throughout (services take `bpy.types.Object`), so it does not run outside Blender. Anny shows the data does — inference from [faceservice.md](https://github.com/makehumancommunity/mpfb2/blob/master/docs/services/faceservice.md).

### MakeHuman 1 and MakeHuman 2 (standalone)
- MakeHuman 1: code AGPL, assets CC0 — [LICENSE.CODE.md / LICENSE.ASSETS.md](https://github.com/makehumancommunity/makehuman) (2026-10-29), page read. Health is in RESEARCH §5.
- MakeHuman 2 is "in Alpha III state" and should succeed MakeHuman 1. Its plans are additional base meshes, animation, PBR shading and glTF export. It keeps hm08 compatible "but no longer identical", shares assets with MPFB2, and uses GLSL 3.3+ on Windows/Linux and GLSL 1.2 on macOS — [makehuman2 README](https://github.com/makehumancommunity/makehuman2) (2026-10-29), page read.
- MakeHuman 2's latest releases are pre-releases Alpha2 (2026-05-05) and Alpha1 (2026-04-30). The repo was created 2023-04-10, last pushed 2026-10-07, 88★ — GitHub API, 2026-10-29, page read.
- MakeHuman 2 licence: "source … released under AGPL"; assets "released under CC0 1.0 Universal" — [data/licenses/makehuman_license.txt](https://github.com/makehumancommunity/makehuman2/blob/main/data/licenses/makehuman_license.txt), page read.
- A CC0 community asset repo (`Makehuman-2/MH2_Asset_Repository_CCO`) was created 2026-08-26 and pushed 2026-10-28; it has 1★ — GitHub API, page read.

### Anny (NAVER LABS Europe)
- "A differentiable human body mesh model written in PyTorch … from infants to elders, using a common topology", based on MakeHuman. It ships full-body and hand/face part models — [README](https://github.com/naver/anny) (2026-10-29), page read.
- Default rig `anny`: 104 bones. `rig="makehuman"` gives the full 163-bone rig with face, tongue and eye bones. The default topology is triangulated MakeHuman-derived; `anny-quads` gives the original quads; alternative retopologies are smplx, smpl and soma — README, page read.
- Mesh: 13,718 vertices and 13,710 quad faces, "including tongue and eyes". A coarse mesh has 1,229 verts. Phenotypes are age, gender, weight, muscle, height and proportions plus local changes, 267 parameters in total — [arXiv 2511.03589v2](https://arxiv.org/html/2511.03589v2) (ECCV 2026), page read.
- Limits stated in the paper: phenotypes "encode by design stereotypes of MakeHuman artists"; ethnicity is not faithfully encoded; no clothes; scan fit error 2.4 mm against 1.8 mm for ATLAS; 49 ms runtime against 4 ms for SMPL-X. Pose correctives are not mentioned — same paper, page read.
- v0.6 (2026-08-06) added facial actions driven by the MakeHuman face units (e.g. `jawOpen`, `mouthSmileLeft`) and the new stable-orientation rig. v0.6.1 (2026-09-28) is the latest — [CHANGELOG.md](https://github.com/naver/anny/blob/main/CHANGELOG.md), page read.
- Licence: code Apache-2.0; `data/mpfb2` and `data/faceunits01` CC0; `data/soma` Apache-2.0; the smplx topology is downloadable "for non-commercial use only" — README, page read.
- Health: no GitHub releases (PyPI `anny`); last commit 2026-09-28; pushed 2026-10-26; 612★; 6 contributors — GitHub API, 2026-10-29, page read.

### MHR — Momentum Human Rig (Meta)
- 45 identity, 204 pose and 72 expression parameters; 7 LODs; non-linear (neural) pose correctives; PyTorch plus pymomentum — [README](https://github.com/facebookresearch/MHR) (2026-10-29), page read.
- The assets include `lod?.fbx` ("Rig with identity and expression blendshapes") and pose-corrective npz files. "MHR is licensed under the Apache Software License 2.0" — README, page read.
- Vertices per LOD: 73,639 / 18,439 / 10,661 / 4,899 / 2,461 / 971 / 595. It has 127 joints and 72 artist-sculpted expressions "based on FACS". Export goes to FBX and glTF — [arXiv 2511.15586v3, 2025-11-24](https://arxiv.org/html/2511.15586), page read.
- Training data: 7,110 body scans (from 13,664), about 3,000 hand subjects and 2,138 heads. The identity space does not change limb length or height; the skeleton parameters do — same, page read.
- Limits stated: no eyeball or mouth geometry ("future mouth system with teeth and tongue"); correctives and expressions do not depend on body shape; textures and topology type are not described — same, page read.
- Health: release v1.0.1 2025-11-19; last commit 2026-10-26; 885★; 9 contributors. Its solver library, `facebookresearch/momentum`, is MIT, v0.1.114 (2026-07-16), with 94 contributors and a last commit on 2026-10-29 — GitHub API, page read.
- ATLAS (Meta/CMU, ICCV 2025): 77-joint skeleton, 600k scans; it is MHR's predecessor. No licence or code repo was found — [arXiv 2508.15767](https://www.arxiv.org/abs/2508.15767), search snippet only.

### SOMA-X (NVIDIA)
- One canonical rig and topology across identity models: MHR (default), native SOMA, Anny, SMPL/SMPL-H/SMPL-X (user-supplied files), GarmentMeasurements; hands from SOMA, MANO or MHR. The package is `pip install py-soma-x` — [README](https://github.com/NVlabs/SOMA-X) (2026-10-29), page read.
- Mid-LOD body is 18,056 verts with 78 joints (legacy). The public pose input is 77 joints; the template rig adds procedural twist joints; the rig is UsdSkel (`SOMA_template_rig.usda`); the mesh is stored as triangles — [docs/data_assets.md](https://github.com/NVlabs/SOMA-X/blob/main/docs/data_assets.md), page read.
- Linear blend skinning runs on "NVIDIA Warp custom kernels", with a PyTorch CPU and GPU fallback: 2.1 ms GPU, 12.1 ms CPU (32 cores). "Designed and/or optimized to run on NVIDIA GPU-accelerated systems" — [docs/model_card.md](https://github.com/NVlabs/SOMA-X/blob/main/docs/model_card.md), page read. **NVIDIA-only fast path.**
- Licence: code Apache-2.0 (GitHub API); assets on [HF nvidia/SOMA-X](https://huggingface.co/nvidia/SOMA-X), card licence apache-2.0, last modified 2026-10-09 — HF API, page read.
- Health: created 2026-03-03, pushed 2026-10-09, 847★; technical report arXiv 2603.16858 — GitHub API, page read.

### MB-Lab
- "Final version of MB-Lab as development has moved onto Charmorph" (1.8.1). Known issues include buggy BVH import and old hair shaders — [README](https://github.com/animate1978/MB-Lab), page read. Archived (RESEARCH §5).
- Licence: Python GPL-3; "All data files … meshes … images … json files are released under GNU Affero General Public License 3" — [license.txt](https://github.com/animate1978/MB-Lab/blob/master/license.txt), page read.
- Characters in `data/characters_config.json`: human_female/male base, anime female/male, and variants `f/m_ca01, as01, af01, la01` (by their codes: Caucasian, Asian, African, Latin), plus `an0x` and `ft0x` sets. `data/` holds `face_rig/facial_rig.blend`, `facs_au.json`, per-character expressions, measures, phenotypes and poses — [data/](https://github.com/animate1978/MB-Lab/tree/master/data) (GitHub API, 2026-10-29), page read. The ethnicity reading of the codes is my inference.

### CharMorph
- It reimplements MB-Lab features without MB-Lab code: hairstyles, real-time asset fitting, "Rigify support with full face rig", and an "Alternative topology feature for applying morphs to models with different topology". The rig is added only at finalisation — [README](https://github.com/Upliner/CharMorph), page read.
- Licence: Python GPL-3; the database is per character — [license.txt](https://github.com/Upliner/CharMorph/blob/master/license.txt), page read. In [CharMorph-db](https://github.com/Upliner/CharMorph-db): `mb_female` and `mb_male` AGPL3, `antonia` "CC-BY 3.0" (Olaf Delgado-Friedrichs et al.), `reom` "CC-BY" (ComplexAce, Hope) — config.yaml files, page read.
- Latest release v0.4.0-3 (2025-03-27): "Fixes for Blender 4.4". CharMorph-db was last pushed 2024-07-23 — GitHub API, page read. No Blender 4.5/5.x mention found.

### Microsoft Rocketbox (+ Headbox, MoveBox)
- "115 characters and avatars fully rigged … relatively low-poly". Updates: 2/2022 blendshapes (15 visemes, 48 FACS, 30 Vive tracker); 6/2022 "ARkit compatible blendshapes"; 4/2022 417 animations; "Updated license to MIT" (12/2020) — [README](https://github.com/microsoft/Microsoft-Rocketbox), page read. Archived, last push 2022-10-02.
- LODs: 10,000 / 5,000 / 2,500 / 500 triangles. Textures usually 2048², with separate head and body maps. Clothing is part of the mesh. Body bones are given as 56 in the text and 53 (+28 facial) in a figure caption — the paper conflicts with itself. Face animation uses bones, not blendshapes (as of 2020) — [Frontiers in VR, 2020](https://www.frontiersin.org/articles/10.3389/frvir.2020.561558/full), page read (first 100k chars).
- The paper says "free for research and academic use"; this predates the README's Nov/Dec 2020 MIT change, and the README is the later source.
- Headbox (blendshape-transfer tool): no licence file, last push 2022-10-02, 54★ — [openVRlab/Headbox](https://github.com/openVRlab/Headbox), GitHub API, page read.

### ICT-FaceKit (USC ICT)
- Light version: base topology, landmarks, and "100 PCA modes of linear morph targets" from light-stage scans. Expressions follow ARKit naming with `_L`/`_R` and split `browInnerUp` and `cheekPuff` per side — [README](https://github.com/USC-ICT/ICT-FaceKit), page read.
- Geometry: face 9,409 v; head and neck 1,839; mouth socket 2,046; gums and tongue 2,977; teeth 4,412 (per tooth); eyeballs 1,570 each (sclera + iris); eye blend, occlusion and lashes. The extra eye meshes "adopt the style of Unreal Engine's Digital Human Project" — README, page read.
- MIT; last commit 2020-12-01; 771★; 5 contributors — GitHub API, page read.

### GNM Head (Google)
- An open "ecosystem … starting with GNM Head", Apache 2.0 "suitable for both non-commercial and commercial". The mesh covers skin, eyes, teeth and tongue; it has identity, expression and pose parameters; semantic samplers generate expressions ("happy", "surprise") and identities by gender and ethnicity; backends are NumPy, JAX, PyTorch and TensorFlow — [README](https://github.com/google/GNM), [gnm/shape/README.md](https://github.com/google/GNM/blob/main/gnm/shape/README.md), page read.
- Technical report: v1 2026-07-26, v3 2026-09-11, 32 authors; claims state-of-the-art scan fitting with no named baseline — [arXiv 2607.23687](https://arxiv.org/abs/2607.23687), page read.
- Weights are downloaded from a CDN on first run, so the asset licence is assumed from the README's ecosystem-wide Apache line; no separate asset licence file was checked — README, page read.

### FLAME, SMPL-X, STAR, SUPR (MPI-IS / Meshcapade family)
- FLAME 2023 Open (11/2025) is released "with the Open Source License (CC-BY-4.0)". Previous versions are "only available for non-commercial research purposes". The viewer shows 10 of 300 shape and 10 of 100 expression components; jaw, neck and eyeballs are articulated; 3,800 training scans — [flame.is.tue.mpg.de](https://flame.is.tue.mpg.de/), page read.
- SMPL-X has 10,475 vertices and 54 joints (neck, jaw, eyeballs, fingers), under a "Software Copyright License for non-commercial scientific research purposes". Last commit 2023-10-12; 2,748★ — [vchoutas/smplx](https://github.com/vchoutas/smplx), page read.
- STAR: non-commercial research licence; last push 2024-02-02; 727★. SUPR: last push 2024-09-30; 184★, licence NOASSERTION — [STAR](https://github.com/ahmedosman/STAR), [SUPR](https://github.com/ahmedosman/SUPR), page read (STAR README) / GitHub API (SUPR).

### Blender Studio Human Base Meshes
- 17 meshes: male and female figures, feet, hands, heads, jaws and eyeballs, in stylised and photorealistic versions. Closed volumes with "clean quad topology"; the realistic assets carry multiresolution detail; UV maps support UDIMs; CC0; Blender 3.2+; released with Blender 3.6 — [cgchannel, 2023-06-28](https://www.cgchannel.com/2023/06/download-blender-studios-free-human-base-meshes), page read.
- The current download is v1.4.1, 49 MB, updated 2025-01-20, for Blender 4.2 LTS+ — [blender.org demo files](https://www.blender.org/download/demo-files/), search snippet only.

### Rigify
- It is a core add-on in Blender's main branch (`scripts/addons_core/rigify`, next to io_scene_fbx and io_scene_gltf2). `__init__.py` reads `"version": (0, 6, 10)` and `SPDX-License-Identifier: GPL-2.0-or-later`. Last commit 2026-10-19 ("Fix: Rigify: Consistently use getattr…") — [projects.blender.org Gitea API](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/rigify), page read.
- The Blender manual page returned 403 to scripted access, so its feature list was not read.

### Auto-riggers and AI pipelines that make rigged humans
- UniRig: autoregressive skeleton prediction plus skinning. The released checkpoint is trained on Articulation-XL2.0; "Full UniRig model checkpoints … trained on Rig-XL/VRoid" are still planned. Generation needs a "CUDA-enabled GPU with at least 8GB VRAM"; spconv and torch_scatter are CUDA builds. MIT. SIGGRAPH 2025, arXiv 2504.12451 — [README](https://github.com/VAST-AI-Research/UniRig), page read. **NVIDIA-only.**
- SkinTokens/TokenRig: skeleton plus skin weights as one token sequence; "98%–133% improvement in skinning accuracy" (claim); inference needs an NVIDIA GPU with at least 14 GB; MIT; arXiv 2602.04805; created 2026-02-08 — [SkinTokens](https://github.com/VAST-AI-Research/SkinTokens), page read. **NVIDIA-only; above this machine's 8 GB.**
- Puppeteer: auto rig plus video-guided animation; checkpoints and the full Articulation-XL2.0 (59.4K rigged samples) released 2025-09-04; Apache-2.0; NeurIPS 2025 — [Puppeteer](https://github.com/Seed3D/Puppeteer), page read. MagicArticulate: Apache-2.0, CVPR 2025, push 2025-09-14 — GitHub API.
- Make-It-Animatable: CVPR 2025; moved to the Hunyuan3D 2.1 ShapeVAE backbone; uses Mixamo bones and animations as data; MIT; 1 contributor — [README](https://github.com/jasongzy/Make-It-Animatable), page read.
- SAM 3D Body: a single image to a full-body mesh "based on the Momentum Human Rig (MHR)". Under the SAM License (last updated 2025-11-19), Meta grants a "non-exclusive, worldwide, non-transferable and royalty-free limited license … to use, reproduce, distribute … create derivative works", with trade-control and military-use exclusions — [repo + LICENSE](https://github.com/facebookresearch/sam-3d-body), page read.
- LHM: "Large Animatable Human Reconstruction Model from a Single Image", ICCV 2025, Apache-2.0. Memory: 14 GB minimum, the Gradio app with motion 24 GB, and LHM++ (2026-03) runs 8-view input on 8 GB — [README](https://github.com/aigc3d/LHM), page read. Its output representation (mesh or Gaussians) was not confirmed this session.
- NVIDIA Audio2Face-3D (face animation, not a base): SDK MIT (C++/CUDA, NVIDIA-only), training framework Apache-2.0, released 2025-08/09 — GitHub API, page read. It belongs in RESEARCH §7.

### Engine-side character systems
- UMA: "free character creation and modification system", MIT. 3.1f1 (2026-09-28) and 3.1f3 (2026-10-09) support "Unity 6.3 and newer"; 35 contributors — [README + releases](https://github.com/umasteeringgroup/UMA), page read. Unity only, so it cannot be reused outside Unity.
- Humanizer: "3D Character Creator for Godot 4.3", MakeHuman-based. Its LICENSE file is GNU AGPL v3 and GitHub reports AGPL-3.0, but the Godot asset library listing says CC0 (search snippet). Release v2.2.0 2025-02-09; last commit 2025-11-07; 295★ — [repo](https://github.com/NitroxNova/humanizer), page read; [Godot asset library](https://godotengine.org/asset-library/asset/3699), search snippet only.
- A Godot forum thread asks for a "MetaHuman-like 'BetaHuman'" system, so there is no such open project yet — [forum.godotengine.org](https://forum.godotengine.org/t/would-godot-benefit-from-a-metahuman-like-betahuman-character-system/140827), search snippet only.
- No Bevy character creator was found; the search budget ran out before a Bevy-specific search.

### VRM stack (open format, stylised avatars)
- UniVRM: MIT, v0.131.4 2026-10-19, 87 contributors. VRM-Addon-for-Blender: MIT, v4.10.3 2026-10-29, "Blender 2.93 to 5.2". three-vrm: MIT, pushed 2026-10-22. vrm-specification: no licence detected by GitHub — GitHub API, page read.
- opensourceavatars.com (ToxSam) is a registry of VRM avatars "with clear licensing (CC0, CC-BY, etc.)", including the 100Avatars collection (CC0) — [README](https://github.com/ToxSam/open-source-avatars), page read.

### Free but proprietary
- MetaHuman: since UE 5.6 (2025-06) it falls under the Unreal EULA. It is free below $1M a year in revenue (seats $1,850 a year above that). Characters can be used in Unity or Godot and sold; they can be used in AI workflows "but not to train or enhance AI models" — [cgchannel, 2025-06-04](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/), page read. The MetaHuman Creator web app is to be discontinued on 2026-11-05 — [menorca.info, 2026-03-09](https://www.menorca.info/actualidad/tecnologia-videojuegos-1/2026/03/09/2585191/epic-games-descontinuara-aplicacion-para-crear-humanos-hiperrealistas-metahuman-creator-noviembre-2026.html), search snippet only.
- VRoid Studio: v2.14.0 on 2026-06-29 added iPad ads and the "VRoid Plus" subscription; it runs on Windows, macOS and iPad and is free software — [MoguraVR](https://www.moguravr.com/vroid-studio-v2-14-0-ipad-ads-vroid-plus-en/), search snippet only. vroid.com and vroid.pixiv.help returned 403, so the terms of use were not read.

### Out — paid only
- Human Generator: Personal $68, Commercial $128, no free version — [Superhive](https://superhivemarket.com/products/humgen3d), page read. Dropped as paid.
- Auto-Rig Pro: Lite $25, Full $50, no free version (only a free sample character) — [Superhive](https://superhivemarket.com/products/auto-rig-pro), page read. Dropped as paid.

## Ranked short-list of base-human options

Each option was argued against before ranking; the line "Attack" says what that changed.

1. **MakeHuman CC0 data (hm08 mesh, 1,258 targets, faceunits, rigs, weights), driven by our own
   host-free code with Anny as the reference.**
   Assessment: the only open base that is permissive (CC0 assets), morph-rich, covers infants to elders,
   has an ARKit-52 face set, ships game-engine and Mixamo rigs with weights, and is active in 2026 (MPFB2
   2026-10, Anny 2026-09, MakeHuman 2 2026-10). Anny (Apache-2.0) shows the data works outside Blender
   in a differentiable model, so JustStage need not inherit GPL or AGPL code. Weak points: artist-made,
   "stereotyped" phenotypes; a ~13.7k-vertex base that needs subdivision plus sculpted detail for close-ups;
   no pose correctives documented; no CC5-level skin, strand-hair or wrinkle system. No source rates its
   realism against CC5.
   Attack: "is it realistic enough?" survives only as a *starting* base — realism must come from our
   own detail layers (displacement, skin shading, correctives, hair). That changed the rec from "use MPFB"
   to "use the CC0 data with our own code".
2. **MHR (Apache-2.0) as the realism and scan-fitting backbone beside option 1, through SOMA-X's shared rig.**
   Assessment: scan-trained shape with 7 LODs up to 73k verts, 127 joints, 72 FACS expressions, neural
   pose correctives and FBX per LOD — closer to production deformation than MakeHuman. It is also the body
   that SAM 3D Body outputs from a photo. Weak points: 45 identity parameters (no age range, no children
   documented), no eyes, mouth interior or textures; pose correctives are an MLP JustStage would have to run;
   topology type not stated.
   Attack: two bases double the morph and clothing-fit work; SOMA-X answers part of that (one rig across
   MHR and Anny) but its fast path is NVIDIA Warp. Kept second, labelled: use SOMA-X's CPU path or
   reimplement its rig mapping (Apache-2.0) to avoid NVIDIA lock-in.
3. **Head and face layer: GNM Head (Apache-2.0) or ICT-FaceKit (MIT); FLAME 2023 Open (CC-BY-4.0) as a third.**
   Assessment: all three are scan-based; GNM and ICT include eyes, teeth and tongue, which MHR lacks;
   ICT's expressions are already ARKit-named. Weak points: head only; ICT is unmaintained since 2020;
   GNM's vertex and expression counts and topology were not found; joining a head model to a body mesh
   is our own work.
   Attack: "why not just MakeHuman's face?" — its faceunits are artist-made like the rest; a scanned
   head is the realism lever. Kept as a layer, not a base.
4. **Blender Human Base Meshes (CC0) as a topology and sculpt reference.**
   Assessment: clean quads, realistic multires detail, UDIMs, CC0. No morphs, no rig, so it is not a
   creator base.
   Attack: adopting its topology would orphan all of MakeHuman's morph data. Kept only as reference
   and sculpt detail.
5. **Rocketbox (MIT) as ready-made library characters and an animation set; not a base.** Low-poly, clothes baked
   in, archived.
6. **MB-Lab / CharMorph: AGPL-3 data; MB-Lab archived; CharMorph's last release was 2025-03.** Useful idea:
   CharMorph's "alternative topology" morph transfer. CharMorph's CC-BY bases (Antonia, Reom) are an
   option, but no evidence was found that they beat MakeHuman on morph coverage.
   Rigging tools beside any base: Rigify (GPL-2.0+) as the reference rig generator; UniRig, Puppeteer
   and Make-It-Animatable for rigging arbitrary meshes (all NVIDIA-only CUDA; SkinTokens needs more than
   this machine's 8 GB).

Non-commercial research models (SMPL-X, STAR, SUPR, older FLAME) stay labelled as comparison and
interop targets; Anny and SOMA-X already convert to and from them.

## Couldn't verify / open

- **Realism against CC5 and MetaHuman:** no render comparison or review was found for MPFB2, Anny, MHR,
  CharMorph or Rocketbox. The only lead is a forum opinion (CC ~85%, MetaHuman ~95% photoreal, search
  snippet). The web-search budget ran out before more searches.
- **Topology quality:** no source documents deformation edge loops or subdivision behaviour for hm08, MHR,
  SOMA or GNM. MHR's and GNM's face types (quads or triangles) and GNM's vertex and expression counts
  were not found.
- **MakeHuman base vertex count:** only Anny's edited figure (13,718) was found; hm08's raw count is not
  confirmed here. MB-Lab's vertex and morph counts were not found (counting meant downloading AGPL data
  files).
- **Asset licences of AI checkpoints:** UniRig, SkinTokens, Puppeteer and Make-It-Animatable weights on
  Hugging Face were not checked; Make-It-Animatable trains on Mixamo data (Adobe terms not read).
- **Proprietary terms not read (403 to scripted access):** VRoid Studio terms of use; Mixamo FAQ
  (helpx.adobe.com); Daz Studio / Genesis 9 (a free-tier proprietary candidate, not researched — daz3d.com
  returned 404/403); the Blender manual's Rigify page; Human Generator's licence FAQ (moot, paid).
- **Not researched for lack of search budget:** Unreal's Mutable (Customizable Object) plugin; Bevy
  character creators; open strand-hair groom assets; Meshcapade's commercial SMPL terms; ATLAS code and licence.
- **Conflicts noted:** the Humanizer licence (AGPL-3.0 file vs CC0 Godot listing); the Rocketbox body-bone count
  (56 vs 53 in the same paper); the MPFB 2.0.18 date (release notes 2026-10-10, GitHub 2026-10-11, likely a time
  zone).
- **NVIDIA dependence to confirm under the user's no-restrictions rule:** SOMA-X (Warp fast path, CPU
  fallback exists), UniRig, SkinTokens, LHM and Audio2Face SDK are NVIDIA-only or NVIDIA-first.
