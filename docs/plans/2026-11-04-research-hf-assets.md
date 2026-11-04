# Research — Hugging Face and Zenodo, shippable assets for every body part (2026-11-04)

> A research agent's deep pass (pagination past 100, licence / modality / task tag filters, Collections, authors
> followed, Zenodo full-text and title queries), on the user's word: "do a hugging face search deeper for all assets we
> could use". Marks: [API] HF or Zenodo API, [page] card / README / paper read, [meas] file measured, [seen] opened.
> Samples (223 MB) in `.dev/downloads/hf_samples/<name>/`; no code run from them.

## 1 · Shippable finds

**Ears**
- **HUTUBS head meshes** (`Emulated-Inc/hrtf-from-head-meshes`, a byte-for-byte mirror of TU Berlin DOI
  10.14279/depositonce-8487): "Released by its authors under … CC BY 4.0". `meshes.zip` 149 MB = 58 head PLYs, plus
  anthropometry and HRIRs. Sample pp2: 198,732 v / 397,460 f, metric 0.22 x 0.18 x 0.30 m; uniform grey vertex colour
  (no texture); clean ears (helix, antihelix, concha), a bald-capped head, a smoothed face. [page][meas][seen]
  **Checked at the original 2026-11-04:** TU Berlin's depositonce record (DOI 10.14279/depositonce-8487) shows "Creative
  Commons Attribution (CC BY)" linked to CC BY 4.0, no other restrictions; "3D head meshes.zip (142.09 MB)"; "3D head
  meshes, anthropometric features, and headphone transfer functions of 96 subjects" (authors Brinkmann, Dinakaran,
  Pelzer, Wohlgemuth, Seipel, Voss, Grosche, Weinzierl). [page]
- Viking HRTF v2 (Zenodo 4160401, CC BY 4.0): 20 pinna STLs moulded from museum figures, coarse (~10k v).
  [API][meas][seen]

**Teeth and mouth**
- **Poseidon3D** (Zenodo 15608906, CC BY 4.0): 200 cases, 400 intraoral STLs (maxilla, mandible) + 2,724 label files;
  sample 000122 maxilla 83,405 v, 67 x 61 x 20 mm, real crowns and gums, clean. [API][meas][seen]
- **MIO intraoral photos** (Zenodo 22047269, CC BY 4.0): healthy set 225 images (434 MB), gingivitis, periodontitis;
  sample 3932 x 1865 - enamel translucency, white spots, gum stippling. A shading reference. [API][meas][seen]
- ProsthoObjects3D (Zenodo 18488594, CC BY 4.0, 13.6 GB): ~650 full-arch intraoral STLs. [API][page]
- STS-3D-Tooth (`MedOtter`, CC BY 4.0): CBCT volumes with whole teeth including roots; the one ROI mask checked was
  binary, not the README's FDI instances. [page][meas]
- Intraoral caries images (Zenodo 14827784, CC BY 4.0): 6,313 photos incl. children's teeth. [API]

**Models (open weights)**
- **Paint3D UVPos ControlNet** (`GeorgeQi/Paint3d_UVPos_Control`; repo `OpenTexture/Paint3D`, Apache-2.0): an SD1.5
  ControlNet on UV position maps (1.45 GB) - paints in UV layout, fits 8 GB. [page][API]
- **TexDreamer** (`ggxxii/TexDreamer`, CC BY 4.0): SMPL-UV text- and image-to-texture weights (2.7 GB). [API]
- **yoso-delight-v0-4** (`Stable-X`, Apache-2.0): a delighting model. [API]
- `tlennon-ie/qwen-edit-skin`, `prithivMLmods/QIE-2511-Studio-DeLight` (Apache-2.0 LoRAs on Qwen-Image-Edit, ~20B
  parameters, need quantising for 8 GB); `paom/texture2albedo-v2` (tagged Apache-2.0; its FLUX.2-klein-9B base's
  licence not read).
- **HairDeck** (`hyz317/HairDeck`, Apache-2.0, 1.7 GB, 2026-10-30): one image -> stylised (VRoid-style) hair cards
  with per-card UVs and spring-bone chains; needs DINOv3 and SAM 3 (their own licences), Linux CUDA. Its method is
  relevant to cards; not realistic. [page][API]

**People**
- 3D-Pain (`SoroushMehraban/3D-Pain`, MIT, 93 GB): 2,500 FLAME heads "balanced by age, gender, and ethnicity",
  AI-textured (Hunyuan3D 2.1 from Kandinsky images) - not scans; its FLAME version and Hunyuan3D's licence (excludes the
  EU, UK, South Korea) need labels. Not sampled (smallest tar 10.5 GB). [page][API]
- Rocketbox mirror (`ENLYAS/pagesmith-assets`): 512² textures measured - the original repo is better. BoneHub Visible
  Human bones (CC BY 4.0): anatomy reference only.

**None shippable found:** eyes (DOOMGAN: 256² GAN periocular images; `synthetic-eyes-v1`: labels only), realistic
hair strands, UV skin textures, nails, lips, facial or body hair, children's 3D data - gaps in this search, not proof
none exist.

## 2 · Reference only (licence or provenance)

TopoRig (academic), DAD-3DHeads (NC-SA), Cafca (NC-SA), welsh-speech meshes (NC), DREAMS-Avatar (NC), show3d (NC),
HairCS (NC), StableMarkus hair (NC), SM-Tongue (NC), AxonData and UniDataPro children's faces (NC / ND). Tag conflicts:
Teeth3DS / 3DTeethSeg mirrors tagged MIT (the original is CC BY-NC-ND), `ThotaBhanu/3Dhumanmesh` (from HuMMan and
IDEA400), `navintiwari/atlas-large`, `Marcus-avatar-data` (FFHQ, CelebA), `Mesh2001/Dental_implant` (ToothFairy,
licence not read). Mixamo snapshots (Adobe terms); NVIDIA SDG-SynHuman (renders only). Placeholders or empty: UVMap-ID,
Rodney111/FFHQ-PBR. No licence: USC-IRIS/synhuman-v2, abcamiletto/textures. Not useful: WaifuAI/aurora (anime),
TripoSR heads, Civitai mirrors with unreliable tags, junk "cc0" repos, Zenodo 8027553 ("available upon request").

## 3 · Query log (the agent's, condensed; counts are results returned)

HF datasets by keyword (top 100 by downloads): human, avatar, mesh, scan, body, head, face, people, character,
multi-view, child, diverse (100 each, noise); textured mesh 1; photogrammetry 13 (drone); 3d face 9; digital human 4;
realitycapture 0; multiview human 11; kids 83; elderly 52; ethnicity 9; smpl 46; smplx 13; human 3d 5 (BoneHub); head
mesh 1 (HUTUBS); face mesh 2; 3d head 2; facial 59; light stage 4; olat 13 (ZJU_OLAT gated); metahuman 7; 4d human 4;
full body 15; renderpeople 4; thuman 3; textured 10; iris 100; sclera 1; eyes 63; ocular 7 (DOOMGAN); hairstyle 4;
groom 5; hair dataset 12; hair 96; curly 13; teeth 16; dental 98; intraoral 4; tooth 76 (STS-3D); tongue 51; mouth 20;
skin texture 1; albedo 22; normal map 5; pores 20; pbr 42; nail 44; fingernail 1; ear 100; lips 44; hrtf 3; pinna 16;
facial hair 1; eyebrow 1; infant 86 (statistics); baby 100; teen 63; aging 58; wrinkle 10; freckle 2. Zero for: face
reflectance, face uv, uv texture, human texture, clothed human, head avatar, gaussian avatar, human scans, body scans,
glb human, eye texture, periocular, hair strands, hairstyle 3d, 3d hair, hair cards, tooth mesh, face texture, pbr
texture, ear scan, eyelash, craniofacial, infant face, sonicom, chedar.
Tag crawls (every cursor page): modality:3d x licence cc-by-4.0 260, cc0 29, mit 257, apache 130, cc-by-sa 22,
openrail 3, odc-by 8, cc-by-3.0 7, bsd-3 5; task image-to-3d 529, text-to-3d 231; modality:3d 1,928 -> a union of 2,361
filtered to 86 hits. A crawl of 27,246 datasets filtered by part terms -> 128 hits.
HF models: uv texture 0, face texture 2, texture lora 97, skin texture 48, skin lora 95, eye texture 1, hair strand 0,
hairstyle 15, teeth 65, dental 100, pbr 76, albedo 100, delight 28, normal map 10, 3dmm 14, flame 100, texdreamer 1,
metahuman 3; a crawl of 30,908 models -> 441 hits; method names (difflocks, gaussianhair, hairstep, strandhead,
hairformer, hairgs, im2haircut, unihair, haircup, arc2avatar, hifi3dface, relightify, headgen, facescape: 0; monohair
1 NC; hairdeck 1; mosar 4; skingen 1).
Collections (17 queries): spaces and papers only. Authors followed: hyz317, Emulated-Inc, digitalrealitylab, MedOtter,
onethousand, Luffuly, ggxxii, SoroushMehraban, tfnn, csbhr, initialneil, mcbuehler, HairCS2027, ubisoft, nvidia.
Zenodo (a curl user agent; 403, 400 and 429 retried): full text "3D head scan", "head scans dataset", "3D face scan
dataset", "human body scan dataset", "3D scan human textured mesh", "photogrammetry human", "ear 3D scan", "pinna mesh",
"HRTF head mesh" (Viking); titles: viking hrtf 2, ear+mesh 19, pinna 2, head+scans 1, "3D facial" 2, children 3D 2,
intraoral 20 (MIO, caries), teeth+3D 21 (Poseidon3D), dental mesh/STL 4 (ProsthoObjects3D), hair 3D 7, skin
replica/topography 24, nail 31, facial texture 5; zero for sonicom, chedar, hutubs (title), face scans 3D, iris
visible, body/human "3D scans", face 3D dataset.

## 4 · Not verified

3D-Pain's FLAME version and texture licence; Face-Depth-3D's image source; DOOMGAN's training data; ToothFairy's
licence; STS masks beyond one file; ProsthoObjects3D and the caries photos unsampled; Poseidon3D's labels unparsed;
SONICOM and CHEDAR not found by title (may be hosted elsewhere); HF search matches ids, not card text.
