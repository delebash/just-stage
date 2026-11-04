# Where the head's skin should come from — research, 2026-11-02

The user, verbatim (after asking why CC5's mesh and textures would look right in our program and ours don't): "research
what you need think adversierly on your rec if you need deeper research then do so, let me know your resutls. 4 is your
ai just not good enough … if i need to pay for ai our you your self need to gen than we can do so, like if you need 100
ai gen photos from a frontier modle … i bet you claude can gen the or we can use nano bannaa … verify you have lookede
for any new techniques or latest best … dont duplicate and make sure you actually read the research we have already
done". Then: "tell me what kind of data you need and i will search for it"; "yes download it and finish the research"
(MakeHuman's Skins 02 pack).

Marks: *[page]* page read; *[snippet]* search-result text only; *[measured]* on this PC; *[file]* read from the file.

## 0 · What we already had (step 0: read before searching)

Read in full or by passage: `2026-10-30-research-image-models.md`, `2026-10-30-research-ai-texturing.md` (§0-§8),
`2026-10-30-research-ai-photo-to-head.md` (§0, §4, §6-§8), `2026-10-30-research-skin-detail-shading.md` (§2.1, §2.4, §7,
§8), RESEARCH.md S10 and the face-test notes.

| Job | Covered (where) | Evidence | Built? |
|---|---|---|---|
| Paint all views of a mesh | ai-texturing §0.1, §1 (Hunyuan3D-Paint 2.1, MV-Adapter ONNX, UniTEX, MVPainter, SyncMVD, StableGen) | pages, API | sequential painting + alignment + levelling built (rounds 49-73); multi-view-together models never tried |
| UV-space / face UV generators | ai-texturing §3.2 (OMGTex, FreeUV, UVAPM, TOPOS, TEXGen, SeqTex) | pages | none runs on hm08 in 8 GB |
| Delighting | ai-texturing §2, skin §1.0 | pages, measured | SH division built |
| How Headshot 3 textures | ai-texturing §6 *[page]*: "reprojection of the photo onto the updated mesh → stencil/clone fill on a corrective layer → **a skin-base preset by age and facial hair → Blend Masking merges face texture and skin base** → de-light → primary + secondary normal maps"; photo-to-head §4: front photo required, side photo optional | page read | **not followed** - we paint ten AI views instead |
| Open scanned skin | skin §2.4: Lee Perry-Smith scan CC-BY 3.0 (4K displacement, 1024² colour); MPFB2 assets CC0; Texturing.xyz / 3D Scan Store / Triplegangers terms not read; RESEARCH S10: "no free textured head-scan set that allows commercial use was found" | licence file, API | LPS displacement used for pores |
| Image models | image-models (FLUX 3 Image Klein measured, Krea 2) | measured | FLUX 3 klein is the painter |
| Frontier / paid image models | — | — | **gap** |
| MakeHuman's own CC0 skins | — | — | **gap** |
| Anything after 2026-10-30 | — | — | **gap** |

Attack on the need: the 73 rounds were spent on the multi-view method's side effects (drift, baked light, seams); the
pros' photo-to-head (Headshot) uses one photo for the face and a skin base for the rest - a researched fact we never
built. So the gaps worth closing: a skin base we may ship, whether a stronger (paid) painter changes the picture, and
anything newer.

## 1 · Findings

**MakeHuman's CC0 skins (downloaded 2026-11-02: `skins02_cc0.zip`, 76,112,708 bytes, files2.makehumancommunity.org,
to `.dev/downloads/mh_skins02/`)** *[measured]*: 13 male skins, every map 2048² for the whole body in MakeHuman's UV
layout (our mesh's), CC0 (`packs/skins02.json`; several "based on skin 'Old Caucasian Male'"). The head island is about
a quarter of the map: the face ~250 px across (our head tile gives ~6 texels a mm). Painted or photo-composited with
shading baked in (dark sockets, lit lips, the old skins' wrinkles). Game-asset grade - at most a low-detail tint for
scalp and neck. Skins 01 (female) and 03 (non-natural) not downloaded.

**Free scanned heads** *[snippet]*: Ten24's male and female scans (4K-16K maps) - "not licensed for commercial use"
(private, non-commercial, internal tests); Eisko's 2015 female scan - withdrawn; Digital Emily 2 (Digital Human League,
8K maps, EXR) - "free for everyone for non-commercial use only"; deep3dstudio's free Asian female scan (RenderHub,
"Extended Use License", terms not read). The Lee Perry-Smith "Infinite" scan stays the one CC-BY 3.0 head ("based on a
work at www.triplegangers.com"); its original diffuse resolution not found (three.js ships 1024²). No other open,
commercial head scan found.

**Frontier image models** *[snippet / page]*: Nano Banana Pro (Gemini 3 Pro Image) - character sheets and turnarounds
with strong but "not perfect" consistency (Artlist); up to 4K; Google's API ~$0.24 a 4K image, batch about half (several
pages; Google's own pricing page not read). Google's terms *[page, aistudio.google.com/docs/terms]*: "Google won't claim
ownership over that content"; you may not "use the Services to develop models that compete with the Services"; likeness
not addressed there. Nothing documents painting straight into a UV layout (one prompt-library "UV metaprompt" for
clothes). Skin realism rankings disagree (FLUX 2, Nano Banana Pro / 2, Imagen 4 Ultra, Recraft named; vendor blogs, no
method). **Claude itself makes no images** (text and code only).

**SkinGen (Reallusion)** *[snippet of the CC5 manual and product pages]*: a Skin Base at the bottom of a layer stack;
layers with Photoshop-like blend modes, each with a mask; normal and micro-normal strengths; region tools (lips: Base,
Heart, Contour, Highlight; redness by a shared face mask); layers merged onto the Skin Base into the material's maps.

**Building a base from swatches** *[snippet]*: histogram-preserving blending (Heitz & Neyret, HPG 2018) tiles a sample
without repetition or a colour shift; pores and wrinkles don't survive blending (random features), so they belong in a
separate high-frequency layer. AI skin-swatch generators exist (Morphic, Pixa, "AI Texture") - vendor claims only; the
outputs look like lit photos, not albedo.

**Newer methods** *[snippet]*: nothing dated after 2026-10-30 surfaced; GTAvatar (Eurographics 2026, arXiv 2512.09162:
a relightable Gaussian head from monocular video with UV albedo / roughness / specular maps) and LightHeadEd (2025,
smartphone + polarisers → albedo / normal / specular UV maps) - capture methods, not generators.

**The user's datasets** (Open Images, COCO, CelebA, Generated Photos, FFHQ, Kaggle profile photos): flat photos with
light baked in; FFHQ and CelebA are non-commercial as datasets; none is a head texture. They'd matter only for training
a model, which is not the bottleneck.

## 1b · Follow-ups the same day

**FLUX 3 Image Klein at 2048² on this card** *[measured, `.dev/tmp/r74/`]*: the close clay view (upscaled 2x) painted in
355 s, peak 7,540 MiB of 8,192 (`--offload-to-cpu --vae-tiling --diffusion-fa`); the cheek's fine detail (brightness
minus its 2-px blur, in 2K pixels) 6.96 against 2.92 for the 1024² painting upscaled - real pores, stubble, fine lines.
Its nose came out strongly red (the prompt's "slight redness on the nose" reads stronger at 2K). Step 1's local route
works; the face texture's density (6.0 texels a mm) is now the limit, not the painting.

**The user's pasted leads, checked**: "Human Male Head 3D Scan Sky" and "Marcus - Free 3D Head Sample" - the searches
missed both (wrongly called "not found" at first); the user's links, read through the Sketchfab API *[page]*:
`human-male-head-3d-scan-sky-0db5a34268d8498ea7acb7e3698f5cbd` by Sky Tesi - "Canon 5DSR and macro lens …
cross-polarization lighting", 4K diffuse and normal, 2K displacement and specular roughness, quads with UVs, of the
author himself; licence "Standard" (a paid Sketchfab Store item), `isDownloadable: false` - usable in a buyer's own
work, not redistributable, so not shippable in an open-source app. `marcus-free-3d-head-sample-model-scan-
1aef740047ba4214998f068355a5f034` by Digital Reality Lab - CC BY 4.0, downloadable, 498,162 faces, one texture
(size and lighting not stated), 2022-07-14 - the best open lead. "PolFace" = *High-Res Facial Appearance Capture from
Polarized Smartphone Images* (Azinović, Maury, Hery, Nießner, Thies; CVPR 2023) - real; a capture method (phone flash +
polarisers, cross- and parallel-polarised) - code and licence not found. 3D Scan Store's free scans - the Ten24 ones,
non-commercial. ShareTextures "Human Skin 5" *[page]* - CC0 ("CC0 Textures of human skin with several maps"): diffuse,
normal, height, smoothness, AO; body part and resolution not stated. **Corrected 2026-11-04:** ShareTextures' licence
page now says "Custom CC0 ... with specific restrictions", incl. "No asset redistribution on other websites, in
plugins, or as part of collections without our written permission" - not shippable (`2026-11-04-research-other-sites.md`).

**Sketchfab, searched through its API** (`api.sketchfab.com/v3/search?type=models&q=head%20scan&downloadable=true&license=by`
*[page]*): downloadable CC-BY head scans of real people exist - "Head scan 13 (photogrammetry)" by yaro.pro (CC BY 4.0;
"Shot on iPhone 12 Pro Max, edited in Luminar AI, processed in Photocatch"; a numbered series), "Head scan 02 (Optimized
PBR)" (a bald man, yaro.pro's scan re-baked by Cratera Games; CC BY 4.0; 12 textures), "Nils Head Scan" ("80 pictures
captured with a Canon EOS 550D"), "Jared Head Scan 3D", "Steven Novak's Head Scan", "Ammamma Head Scan Polycam", female
heads ("Female head scan", Nikitos & 3130's "Head 03 A", "HEAD 3 scan", "Lmdclub Nastya"), and "Head (Lee Perry
Smith)" - "Perry Smith head with all textures": lambert, high-res bump, normal, cavity, thickness, derivatives,
occlusion, proximity, translucency, curvature (resolutions not stated). Their texture sizes and lighting aren't in the
API; phone photogrammetry bakes the light in. Downloading needs a Sketchfab login. The CC0 search returned museum
objects only.

**More free scans (the user: "i think there are lots of free cc headscans out there you just did not look
correctly")** - right: one narrow API query had been run. The Sketchfab API with `q=face scan&downloadable=true&license=by`
*[page]* returns 19 more scans of real people under CC Attribution - Trnio app scans ("Face Scan example", "Face Scan #2",
"Scan - Stewart", "Face #1", "Andrew K. Face Scan"), Thunk3D scanner demos (0.6-6.7M faces), Scandy, an Artec scan
(CIMtech), an EinScan-Pro scan (Aniwaa), "Very detailed face" (Theworkings), "Harsha Face Scan" (Perspectiv); `q=head scan`
gave ~15 (above). Most are face-only phone or handheld scans with the room's light in the texture; texture sizes aren't
in the API. The user's ArtStation link (`artstation.com/artwork/GXJrLz`, read in Chrome): 3D Scan Store's "Free 3D Head
Scan" - a bald man, "ZBrush tool / OBJ / FBX / uncompressed TGA textures / Marmoset Toolbag scene / jacket included",
download through their blog (the browser may not read 3dscanstore.com); CG Channel on Ten24's 2019 free male head (this
one, by the description): "not licensed for commercial use … private or non-commercial … internal tests" *[snippet]*.
The blog post itself, read in Chrome on the user's word: "FREE HD HEAD" - "TGA / JPG (8192 x 8192 pixels) / Albedo,
Normal, displacement, Roughness, Specular", a 16-bit 8K displacement TIF, "Pore / fine wrinkle level detail with micro
map", head, teeth, tongue, eyes, lens, eye wet, lashes, brows; "License: Personal use only please contact us for
commercial use"; 1.9 GB - a reference for real skin, not shippable unless 3D Scan Store grants commercial use.
The high-end free scans (Ten24, Digital Emily 2, Eisko) are non-commercial, "Sky" is paid; the open ones are CC-BY
scans of uneven quality, to be judged by downloading (a Sketchfab login).

**Downloaded 2026-11-02 through the user's Sketchfab login** (original formats, saved to Chrome's folder and moved to
`.dev/downloads/scans/<name>/`, each unpacked in its own `x/`) *[measured]*:

| Scan (credit, CC BY) | Archive | Maps measured | What it shows |
|---|---|---|---|
| "Head scan 02 (Optimized PBR)" by Cratera Games, scan by yaro.pro - sketchfab.com/3d-models/2f1978b43032415c8fdf911c7acfb1a4 | 132 MB glTF | diffuse 4096², normal 4096², roughness 2048² | a bald man's whole head, scalp included, in clean panels; real scalp skin (fine mottling), real pores on the cheek, fairly even light (a gradient on one cheek) |
| "Head (Lee Perry Smith)" uploaded by Paul (Sketchfab); "Infinite, 3D Head Scan by Lee Perry-Smith", CC BY 3.0, based on a work at www.triplegangers.com | 96 MB OBJ | lambertian 4096², bump 6000², cavity 512² | evenly lit real skin with stubble, one wrapped head - the 4K original of three.js' 1024² copy |
| "Marcus - Free 3D Head Sample Model Scan" by Digital Reality Lab | 51 MB OBJ | one map 4096² | a black marker cap over the scalp; face and neck usable, neck tattoos |
| "Nils Head Scan" by Simsallabim | 69 MB FBX | diffuse 8192² | an automatic photogrammetry atlas of ~100 fragments, warm baked light - little use |
| "Very detailed face" by Theworkings | 118 MB OBJ | textures inside a nested archive (not opened yet) | face only |
| "Head scan 13 (photogrammetry)" by yaro.pro - sketchfab.com/3d-models/5e6d2804405449e6b3bd96cd12d8b1ab (383,563 faces; iPhone 12 Pro Max, Photocatch) | 140 MB FBX | baseColor 8192² | a mature man: real wrinkles, stubble, grey hair; a fragmented photogrammetry atlas with blurred fill between pieces - KEEP (older man) |
| "Rudavin Sergey 3d portrait" by rudavin - e1fe86107058409c9fb88b50f5ef80fd (194,614 faces) | 13 MB (OBJ in a RAR) | 8192² | a younger man: stubble, a mole, even light; a bust in a red jersey - KEEP (younger man) |
| "Female head scan" by whynotmeebaby - b157e28076484a3f9f4f41b5e0f70770 (1,326,812 faces) | 36 MB (OBJ in a RAR) | 4096² | a woman: real pores on cheek, nose and lips, sun spots - KEEP (the best woman's skin) |
| "Head 03 A" by Nikitos & 3130 (@vrcityphoto) - 04a94494d88d48d18c46b82c7ab7c7b8 (1,273,836 faces; "75 images not corrected") | 38 MB (OBJ in a RAR) | three maps 4096² | a young woman: smooth, soft skin, even light, green-screen spill at the hair - KEEP (young, smooth; weak pores) |
| "Ammamma Head Scan Polycam" by Krishna Prakash - 64fda4f6914d40b89bc07a9f5927357e (73,097 faces) | 23 MB GLB | 4096² | an elderly woman: wrinkles, red mottling, a few white flakes (marks to remove) - KEEP (old age) |
| "Jared Head Scan 3D" by ARmediaLab - 08f691ec9d2a43eea699638877df5674 | 9 MB OBJ | 4096×2048 | a front projection, a full beard over the lower face, ~2.8K across the face - weak |
| "Eddy's Bust made with 3DF Zephyr" by Eddy Adams - fd9ba129 | 53 MB FBX | 5536² | streaked, broken bake - out |
| "Joan", "Red Lady" by Veterock | 132 / 140 MB FBX | 4096² (+ a near-flat normal) | flat, smooth colour, no skin detail (game characters) - out |
| "Kitbash 3D Self potrait" by Krishna Prakash | 50 MB FBX | clothes 4096², a KeenTools FaceBuilder photo projection 2048² | not a scan's skin - out |
| "Scan - Léo-Paul" by Yannoid | 20 MB FBX | one grey map 4096² | no colour - out |
| "Asian Woman Photogrammetry" by daydev | 4 MB FBX | 2048² | the file name ("_refine") and the body read as an AI-made model, 2K - out |
| "John Cleaver" by toolsbyhollie | 40 MB OBJ | none in the archive | no texture - out |

Licences read from Sketchfab's API (`/v3/models/{uid}`, 2026-11-02): all of the above "CC Attribution". Measured
*[measured]*: each map's size; a contact sheet of the maps; the most detailed all-skin 384-px window per map at full
resolution and three typical ones (30th/60th/85th percentile of fine detail). Gap: no dark-skinned scan among them.

**Second batch - the dark-skin gap** (Sketchfab API, `downloadable=true&license=by&sort_by=-likeCount`; queries:
"african head scan", "black man head scan", "black woman head scan", "african american bust scan", "african man scan",
"dark skin face scan", "afro head scan", "man bust photogrammetry", "woman bust photogrammetry", "old man head scan",
"indian man head scan", "person scan photogrammetry", "portrait scan", "selfie scan", "renderpeople", "deep3dstudio
free download" - most hits museum objects; the people found: Renderpeople's and deep3dstudio's free full-body scans,
"portrait of model" by 3130). Texture sizes from the download endpoint (`/i/models/{uid}/download`, signed in). All
"CC Attribution":

| Scan (credit, CC BY) | Archive | Maps measured | What it shows |
|---|---|---|---|
| "FREE DOWNLOAD: Attractive African woman 236" by deep3dstudio - f2c29b6947f34237a0bfdc777120ef28 (100k faces, full body) | 89 MB OBJ | diffuse 8192², normal, specular | dark skin with visible pores and follicles - KEEP |
| "FREE DOWNLOAD Athletic African man walking 223" by deep3dstudio - f9a8e3b108f04e998815593f78f163b1 (full body) | 84 MB OBJ | diffuse 8192², normal, specular | dark skin, stubble, softer - KEEP (mid layer) |
| "Carla Rigged 001" by Renderpeople - acf520f450d14dd799f98a6fede3edf5 (full body) | 90 MB FBX | diffuse 8192², normal | medium-olive skin, clean - KEEP |
| "portrait of model 2.0" by 3130 - 6832a653f9c647aba01f77b5d774e9ba (bust) | 45 MB (OBJ in a RAR) | 8192² (UDIM 1001) | a light-skinned woman, fine detail, textured lips - KEEP |
| "FREE DOWNLOAD: Sexy woman in bodysuit posing 233" by deep3dstudio - 3fcc62089501452393dee0f7dc2c0613 | 56 MB OBJ | 8192² | blurry patches - weak |
| "Fabienne & Percy 001" by Renderpeople - 8c9bfd4fb8a444b3a42a4fc31935a2fb | 20 MB FBX | 8192² | the skin windows found only shoes and hair - out (face not checked) |
| "Tony "Mcfly" Hodges" by William Pedersen (conjurer) - 226ac4d5b5a94996b1e3373e60cbf651 | 14 MB OBJ | 4096² | a broken, blurred atlas - out |

**Telling skin from hair, brows, beard and clothes on a scan (2026-11-02; 7 of the 9 keepers have hair)** - our files
had only "CelebAMask-HQ 19-class parsers exist" (`2026-10-31-audit-eyes.md:323`). Queries (standard search): "best face
parsing model 2026 open source skin hair segmentation" -> LaPa leaderboard (a general facial-representation model 93.88,
SegFace 93.03, RTNet 92.5), yakhyo/face-parsing (BiSeNet), jonathandinu/face-parsing (SegFormer, non-commercial
licence), FPLNet (LaPa, ~2 years old); "latest techniques skin segmentation hair beard mask face texture 3D scan
cleanup" -> **Pixels2Points** (Eurographics 2025, arXiv 2504.19718; Chen, Bolkart, Beeler et al.): skin / non-skin
predicted per vertex ON the scan mesh from multi-view foundation-model features plus geometry, "8.89% and 14.3%" better
registration than pure 2D or pure 3D segmentation, trained on synthetic data - the abstract (page read) names hair,
beard and accessories as non-skin; no code, data or weights linked (arXiv page read; search "Pixels2Points ... github
code weights" found none) - its "pure 2D" baseline, multi-view 2D segmentation lifted onto the mesh, is the training-free
route; older patents (Canny texture + colour clustering for hair); "face parsing model with beard facial hair class
segmentation dataset" -> no dataset with a beard class; CelebAMask-HQ labels a full beard as hair (snippet: a SegFormer
project's notes); EasyPortrait counts a sparse beard as skin and a defined one as occlusion; "remove hair from head scan
texture photogrammetry skin only mask workflow" -> the industry does it by hand: sculpt or mask-by-smoothness the
geometry (3D Scan Store's ZBrush tutorial), paint out hair in Mari / Photoshop (Gnomon workshop), Headshot's Custom
Mask; HairFree (NeurIPS 2025) synthesises bald textures from skin masks + FLAME (research code); "SegFace ... github
weights license" and "EasyPortrait dataset license ..." -> the candidates' terms, read through GitHub's and Hugging
Face's APIs *[API]*:
- **SegFace** (AAAI 2025, `Kartik-3004/SegFace`): code MIT, pushed 2025-09-30, 112 stars; weights `kartiknarayan/SegFace`
  card MIT (ConvNeXt / EfficientNet / MobileNet / ResNet / Swin-B, CelebAMask-HQ 512 and Helen); mean F1 88.96 on
  CelebAMask-HQ, 93.03 on LaPa (arXiv listing). Trained on CelebAMask-HQ (non-commercial data) - a label, not a filter.
- **yakhyo/face-parsing** (BiSeNet): MIT, pushed 2026-10-26, 331 stars, ONNX weights - lighter, below SegFace.
- **EasyPortrait** (`hukenovs/easyportrait`): no licence file on the repo (API), data "a variant of" CC BY-SA 4.0; the
  only beard-aware rules found.

**The scan hunt (the user's go: "make sure you find the best sites to search, go")** - sites: Sketchfab (the
largest CC-BY set of real-person scans, searchable through its API); commercial-use free scans whose licences usually
don't allow redistributing the files - Renderbot (nine people, 8K, commercial use, "for a period of one year" per CG
Channel), xoio (15 people, 2K textures), Ten24's 2016 full-body male (commercial use with credit), 3DCAP (three people)
*[snippets]*; research sets behind institutional agreements (3DBodyTex.v2, ~3,000 scans); CC0 skin: "Human Materials
1" on Sketchfab (CC0, 2K skin materials: colour, AO, roughness, normal, displacement) *[snippet]*, ShareTextures' Human
Skin 5 (custom "CC0" with no redistribution in plugins - corrected 2026-11-04). Sketchfab API queries (`downloadable=true`, `license=by` or `cc0`, `sort_by=-likeCount`): "woman head
scan", "bust scan", "photogrammetry portrait", "head scan" (cc0: carvings only), "face scan", "head scan". Real-person
CC BY candidates (celebrities and public figures left out - likeness): "My bald father bust" (Coltranne, d281e5e1),
"Eddy's Bust made with 3DF Zephyr" (100 Canon 5D III photos, fd9ba129), "Asian Woman Photogrammetry" (daydev,
8c7bb1f3), "ESTHER" (videophage, 074e5680), "Rudavin Sergey 3d portrait" (e1fe8610), "Kitbash 3D Self potrait"
(Krishna Prakash, 42cf3aee), "Scan - Léo-Paul" (72199517), "Female head scan" (whynotmeebaby, b157e280), "Head 03 A"
(Nikitos & 3130, 04a94494), "Joan" and "Red Lady" (Veterock, d471e24a / 8dc6e53c, scanned heads, 0.8 / 2.9M faces),
"Female Head 3D Scan" (Konstantin Martens, Meshroom, 3ec26904), "Ammamma Head Scan Polycam" (64fda4f6), "Jared Head Scan
3D" (08f691ec), "Head scan 13" (yaro.pro, 5e6d2804), "John Cleaver" (Artec Eva Lite, 70c53edc), "Woman With Hair"
(Matter and Form, eb5895cd).

## 2 · The rec (attacked)

**Rec:** follow Headshot's structure, in measured steps.
1. **A sharper hero picture** (the one face painting everything is matched to): 2K-4K instead of 1024² - FLUX 3 Image
   Klein at 2K on this card if it fits (not measured), else SeedVR2's upscale (apache-2.0; RESEARCH skin §5), or Nano
   Banana Pro at 4K if the user chooses to pay (~$0.24 a picture, one per head; cloud). Pores and fine lines need
   ~10-20 px a mm; the 1024² hero gives ~5.
2. **The face from the hero, the rest from a skin base:** the hero projected as now (with the two 30-degree views as
   optional side sources - Headshot's optional side photo), blended by a mask into a skin base, instead of seven more
   AI views of scalp, neck and back.
3. **The skin base, SkinGen's way:** tone from our skin colour model matched to the hero; region layers with masks
   (scalp, redness, under-eye, lips); pores from the Lee Perry-Smith displacement (CC-BY 3.0, in use); colour variation
   tiled by histogram-preserving blending from skin swatches - AI-made (a flat close-up has no geometry, so no drift) or
   scanned ones if the user finds them. NOT STANDARD as code: SkinGen's layer model is documented, no library builds it
   for hm08 in Blender.

**Attack.**
- (a) Past decisions: retires seven of the ten views (rec 1's second half, 2026-10-30); the face's tuning (hero lead,
  eye and seam alignment) stays. The ears, jaw and scalp lose the paintings' specific detail and become the base's -
  Headshot does the same.
- (b) Cost: step 1 hours; steps 2-3 days (masks, layers, blend).
- (c) Could fail: a base can look procedural or repeat in the 40-degree and profile views; a visible line where the
  painted face meets the base; AI swatches carry baked light (delight them like the views).
- (d) Simpler or more standard: keep the ten views (round 73 works) - cheaper now, but every new character fights
  drift again and the app needs robustness; paid scans (Texturing.xyz, 3D Scan Store) can't ship in an open-source app.
- (e) Edges: other skin tones and ages - the base's tone and swatches follow the hero; the profile views see mostly
  base.
- What the attack changed: step 1 first (it helps whichever way the rest goes); the 30-degree views kept; the base
  tried on the 40-degree view before any view is retired.

## 3 · Search log (WebSearch, standard mode - 16)

1. "Nano Banana Pro consistent character same person multiple angles turnaround photorealistic" - invideo, letz.ai,
   Google's tips blog, Artlist, selfielabstudio guides: turnaround sheets, "not perfect" consistency.
2. "generate UV texture map for 3D head with AI image model Nano Banana GPT image" - a YouMind "UV metaprompt" (clothes),
   an itch.io projection devlog; nothing documented.
3. "free 3D head scan with textures commercial use CC-BY CC0 download" - Ten24 (non-commercial), Eisko (withdrawn),
   3dart.it, deep3dstudio.
4. "best AI image model photorealistic skin portraits 2026 comparison" - vendor rankings (FLUX 2, Nano Banana, Imagen 4
   Ultra, Recraft); no method.
5. "Digital Emily 2 Wikihuman head scan license commercial use textures" - non-commercial; 8K, EXR.
6. "Infinite Realities free head scan creative commons attribution license textures" - the LPS licence file (CC-BY 3.0).
7. "Nano Banana Pro API price per image 4K output commercial use rights" - ~$0.24 a 4K picture; rights not in results.
8. "latest AI head avatar texture generation method November 2026 relightable UV albedo" - GTAvatar, LightHeadEd.
9. "Lee Perry-Smith Infinite head scan original download diffuse texture resolution 4096 OBJ" - no resolution found.
10. "MakeHuman skin textures CC0 realistic resolution young asian male skin MPFB" - the CC0 skin packs, Toigo 2048².
11. "Character Creator SkinGen how it works layers base skin micro normal region mask appearance editor" - CC5 manual.
12. "seamless skin texture from small photo swatch for 3D character UV texture synthesis histogram preserving blending" -
    Heitz & Neyret 2018, Laplacian-pyramid synthesis.
13. "AI generated human skin texture close-up tileable pores for 3D character skin material workflow" - Morphic, Pixa,
    "AI Texture" (vendor pages).
14. "sketchfab human male head 3D scan downloadable CC attribution 4K diffuse normal photogrammetry" - Captured
    Dimensions full-body scans, a CC BY-NC body, Ten24.
15. "\"Marcus\" free 3D head scan sample Digital Reality Lab" - no such sample; Digital Reality Lab on TurboSquid.
16. "High-Res Facial Appearance Capture from Polarized Smartphone Images code release license" - the CVPR 2023 paper;
    no code found.

Fetched: aistudio.google.com/docs/terms; sharetextures.com human-skin-5; the Sketchfab API (two searches, three models); static.makehumancommunity.org/assets/assetpacks.html and
`assetpacks/skins02.html`; casual-effects.com/data (no content); opengameart.org Toigo skin (403).

## 4 · Couldn't verify

The original LPS diffuse resolution; Google's own price page; FLUX 3 Image Klein at 2K on 8 GB; SeedVR2 on this card;
any AI skin swatch generator's quality or licence; deep3dstudio's Extended Use terms; SkinGen's internals beyond the
manual's snippets.

## 5 · 2026-11-04: the gaps (East Asian, dark-skinned men, older people, children, bodies) - a research agent and checks

**HSRD-100** (Digital Reality Lab, `huggingface.co/datasets/digitalrealitylab/HSRD-100`) *[API + README read, one scan
downloaded and seen]*: CC BY 4.0 ("Commercial use allowed", "Distribution allowed", "All participants provided
informed consent"), not gated. 10 people x 10 poses, a 112-camera rig, RealityCapture: HSR0042 Black man 24, HSR0161
Black man 64 (bucket hat in all poses), HSR0102 Black woman 22 (hairband in all), HSR0023 Hispanic man 62, HSR0015
Hispanic woman 23, HSR0081 Asian man 25, HSR0028 Asian woman 21, HSR0040 White man 50, HSR0112 White woman 60, HSR0027
White woman 41. Per pose: the retopologised `-LOD0/1/2.zip` are 41-byte placeholders (`pose_meta.json`: "price_commercial":
"100", "license": "Commercial" - the lab's paid product); the raw scans are real: `-Scan-LOD0.zip` ~190 MB (an OBJ
~98 MB, one 16384² diffuse PNG), `-Scan.zip` ~480 MB, `-Photos.zip` ~1.2 GB, a RealityCapture project. Seen at 1:1
(HSR0042 pose 045, `hsr_chest_crop.png`, `hsr_face_crop.png`): real pores and hair follicles on the chest, a detailed
areola, fine lines on the lips, stubble; even, flat light (little baked shadow). The best open scan data we have.
Downloaded 2026-11-04 to `.dev/downloads/hsrd100/<pose>/` (Scan-LOD0): 042-045 and 042-018, 161-002, 102-052,
023-077, 015-035 and 015-087, 081-054 and 081-074, 028-093, 040-086, 112-074, 027-068.

**Sketchfab, CC Attribution, downloadable** (texture sizes from `sketchfab.com/i/models/{uid}/textures`; thumbnails
only, not downloaded): East Asian - Renderpeople "Mei Posed 001" (07f308b8, 8K, studio), 3D Selfie Scans "Shelley"
(0e6d9547, 8K) and "Matt Chua" (2f25dea0, 8K, bandana), OverseerThuror's two (caps), 3D Lab Kyoto "AYA2" (4K + normal,
roughness); Black men and women - 3D Selfie Scans "Malcolm" (9de3d339, 8K + maps; pores and stubble in the thumbnail),
"Bryan" (af5f7cbc, beanie), "Lamar", "Camille"; older and Latino - "Hector Navarro Bust" (910f9df8, 8K, older Latino
man), "Grandpa - RealityScan" (35316e96, 8K, phone, baked light), "Mohamed" (f2387a16, phone); bodies - Renderpeople
Eric, Nathan, Dennis, Sophia, Claudia (8K, mostly clothed), 3D Selfie Scans "Pete", "Ben". Children: no open
high-quality textured scan found (a swaddled baby phone scan; vertex-colour scans). No South Asian man above 1K.
Other sources' terms (snippet unless noted): Human Alloy - its own commercial licence; Triplegangers samples - CC
BY-NC-ND; Ten24 2016 full body - "licensed for use in commercial projects, providing you credit Ten24" (CG Channel, not
Ten24's page); Renderpeople's own site - bars making data available to third parties (their Sketchfab copies are CC
BY); AXYZ - a Distribution licence for software; Multiface - CC BY-NC; 3DBodyTex, Headspace - research-only; Polycam
Explore - "Savable" captures CC BY 4.0 (help page 403); Poly Haven, ambientCG - no human scans (API).
The agent's query log: ~60 Sketchfab API queries (people category, licences by / cc0 / by-sa, each ethnicity, age,
body term), Hugging Face dataset searches ("head scan", "human scan", "3d scan", "face scan", "photogrammetry human",
"body scan", "3d human"), and 20 web searches (`F:\ClaudeCode\tmp\claude\...\scratchpad\sf_details.jsonl` holds the
per-model records).
