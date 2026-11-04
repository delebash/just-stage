# Research — the redo: sources the CC-only filter had cut, every body part (2026-11-04)

> A research agent on the user's "so redo the search and do it correctly your rec go" (TASKS "SEARCH RULE"), its
> brief checked against the global CLAUDE.md research rule 7 (a-n) and carrying the coverage map. The licences of the
> big sites were read by me (`2026-11-04-research-licences-redo.md`); this file is the agent's finds, checked by me
> against a-n before use. Marks: [page] read, [site-JSON] the site's own search data, [meas] measured, [seen] looked
> at, [snip] snippet only. Routes: SHIP / FETCH / IMPORT / TRAIN / REFERENCE (defined in the licences file).
> Samples: 6 photos, 26 MB, `.dev/downloads/redo_samples/{pexels,unsplash}/`; nothing run from them.

**Disclosed by the agent (rule l):** before my note on site rules reached it, it fetched Unsplash's internal `/napi`
search 16 times and Pexels' search pages ~41 times by a curl script - against Unsplash §8 (bots except the API) and
Pexels §8 (no automated collection). It stopped on the note and browsed normally after. It also used the user's tab for
~6 calls by mistake (the tab group was recreated); a typo address ("3dscantstore.com") appeared there - the tab was
checked afterwards: the user's own Google search, nothing open on that address. Its "TRAIN unclear" for Pexels and
Unsplash is wrong - both ban machine-learning collection (my reading of their terms).

## 1 · What the samples showed

Pexels and Unsplash strip EXIF on download (all six had none) [meas] - AI origin can't be ruled out from the file;
Pexels' §7B bars AI uploads, with no guarantee. One sharp texture source: Pexels 7479965 (Angela Roma, dark skin with
fine hairs, 4000 x 6000) - real micro-relief and follicles at 1:1, oily specular light [seen]. Soft or noisy at 1:1:
7544829 (elderly wrinkles), 36641345 (lips, moustache), 6319017 (ear, part sharp), Unsplash d3EhjfyLQYA (iris: real
crypts, heavy noise, colour cast). **Stock photos are mostly REFERENCE or small detail patches, not skin bases.**

## 2 · Finds by part

**1 · Skin**
- deep3dstudio head scans (RenderHub, CGTrader, TurboSquid, ArtStation): raw, 15M / 400K triangles, eyes open and
  closed, **16K cross-polarised + 16K parallel-polarised** 16-bit PNG, colour chart, 85-camera rig [page]; Asian F 60s
  and 70s, Asian M 70s, European M/F 60s and 70s, African M 20s, African F 30s (no African 60s-70s) [snip]; $12.99 sale
  ($19.99) on RenderHub. Licence: RenderHub Extended Use - §IV.2.a.iii "you may not redistribute, publish or make a
  Digital Asset available to any third party ... unless the Digital Asset becomes part of a larger Creation", "Share"
  = "the ability to access, download, edit or otherwise use" [page]; the listing: "For non-AI use only". Routes:
  IMPORT, REFERENCE; SHIP unclear (an open repo lets anyone access the files); no TRAIN. (Their free Sketchfab uploads
  are CC BY - two are in our skins.)
- 3D.sk: ~4,000 models, filters age 0-17 ... 71+, Arab / Asian / Black / Hispanic / Indian / White, Hairy, Bearded,
  Wrinkles, Birthmarks [page]; cross-polarised photo sets (e.g. "Matthew", 343 JPG at 4480 x 6840, age 15). Hobby
  EUR 17.90-24.90 a month; Commercial EUR 69.90-79.90; an A.I. plan (custom). Commercial terms: no "resale, license or
  other distribution, unless the original Content has been fundamentally modified ... nor is the Content capable of
  being downloaded, extracted or accessed by a third party as a stand-alone file"; pricing: the Commercial plan
  "doesn't cover A.I. usage ... and Avatar creation for next resale"; the A.I. agreement allows ML use [page]. Routes:
  REFERENCE, IMPORT, TRAIN (A.I. plan); SHIP of textures doubtful (open files are accessible).
- 3D Scan Store HD heads (16K albedo, normal, displacement; "Aged Senior" male 49) [snip] - its licence bars character
  makers: REFERENCE only.
- Ten24 SP-6M (sp-6m.com): 7,400+ people x 11 expressions, 16K textures, 5.8M raw photos, 501 retopologised faces;
  "licensed for responsible commercial use, including games, film, advertising, and AI research" [page]; its dataset
  licence page UNREAD; by contract. Routes: TRAIN, IMPORT (by contract).
- Human Alloy (HF, licence "other"): 180-DSLR rig, 6,000+ sessions, mostly Western European; **2K diffuse only**; the
  archviz licence "does not cover AI training" [page]. REFERENCE.
- Texturing.XYZ SKAP: an online 2K-8K -> 16K skin-map service, $1 a credit [snip]; its licence bars open source (see
  the licences file).
- Pexels skin [site-JSON]: dark skin 7479965, 7480267 (veins); elderly 7544829 / 7544832 / 7544826, 36730753 (hands);
  freckles 3064717, 3142446, 7479575, 7479603; moles 6568231, 6567944; palms 6642889, 4046563; a freckled child
  8396129; feet 7886226. Unsplash: 2mzUaunCeI4 (pores), k4ManxEQAnE (brown spots), oxqwdCMmUQM (elderly hands),
  RBzm131cMHk, 7m_jsxQRqoI (freckled arm). Routes: SHIP (derived), REFERENCE.
- Magnific (freepik.com now redirects there): §8.1(7) no "machine learning and/or artificial intelligence purposes",
  §8.1(3) not in "a database, archive or ... media/stock product", free use needs attribution [page]. REFERENCE.

**2 · Scalp hair**
- KhitrovArt coily / afro MetaHuman grooms on Fab (5+ styles, strands + 2 Alembic sources, no cards), $12.99-29.99,
  Fab Standard, "Allows usage with AI: No" [page] -> IMPORT only (Fab bars GPL and exporting tools).
- PixelHair (Yelzkizi): Blender particle hair, kinky / 4C, $45-170; an AI-training licence exists [snip]; licence
  UNREAD (403) -> IMPORT likely.
- hamza khaloui, 8 coily / afro / locs styles on Superhive, $18.99 each [page] -> IMPORT (redistribution needs the
  author's permission).
- CGTrader afro wig pack (6 styles, FBX + Alembic) [snip] -> IMPORT. 3D.sk groom scans and references -> REFERENCE.
- Photos (braids, twists, locs, afro, grey; e.g. Pexels 7951589, 11482130, 10283311; Unsplash kh4yDU33ZzQ grey,
  8256 x 10320) [site-JSON] -> REFERENCE.

**3 · Facial hair:** khaloui beard / brow / moustache packs ($19), Meta Studio cards ($15-255), PixelHair beards
[snip] -> IMPORT; photos (Pexels 36641345 coily moustache with grey, soft at 1:1; 7322313, 30178261) -> REFERENCE. No
open groom better than Blender's demo.

**4 · Brows and lashes:** no dedicated paid source; they come inside head packs [snip]; photos (Pexels 3373735,
36704138 Asian eye and lashes) -> REFERENCE.

**5 · Body hair:** 3D.sk "Hairy" references [page]; Daz body-hair sets (licence UNREAD); Fab and Superhive arm-hair
systems [snip]; photos (Pexels 18143970, 20047000, 8517480) -> REFERENCE.

**6 · Eyes**
- Daniel Bauer "Eye Textures @ 8K" (Gumroad): **photographed with a Phase One P65+**, 8K sclera, vessels, limbal ring,
  albedo, normal, height, roughness, vessel mask; no iris yet; $50 single user / $200 studio [page]; licence text
  UNREAD -> IMPORT likely.
- FlippedNormals Eye Kit: sculpted in ZBrush, not photographed; $49 [page]; licence UNREAD -> IMPORT.
- Realistic Eye Pack (Superhive): 54 irises at 1K [page] - low value.
- Photos: Unsplash d3EhjfyLQYA, MU9Zgo2QDfo; Pexels 33441257, 40113583, 10600332 (bloodshot) [site-JSON]; no sharp
  sclera-vein macro -> REFERENCE.

**7 · Mouth:** 3D Scan Store teeth (reference only, its licence); Red Nebula ($7.50+), Alex Lashko ($9-29) [snip] ->
IMPORT; TurboSquid dentition -> IMPORT only (§II.7(c) bars "a starter library within a Creation that allows users to
generally work with 3D models"; §II.6(d) no ML without authorisation) [page]. Nothing better than Poseidon3D + MIO.

**8 · Nails:** 3D Scan Store hands and feet (16K; reference only); a buyer's review of a 36-hand scan set: nails "not
expressed" (nails reconstruct poorly in scans) [snip]; Qlean "japanese-hands-nails" (HF, gated academic licence) ->
REFERENCE. **Still a gap.**

**9 · Nipples, lips, ears:** Another World Studios "Realistic Human Ears, Set of 10" (scanned), $18 [page] -> IMPORT;
Artec 3D free ear / eye / hand scans, "Creative Commons with attribution" [snip], licence behind a download pop-up,
UNREAD; lips: 3D Scan Store expression scans (reference only); nipples: only body scans (HSRD-100, on hand).

**Children and teens:** 3D.sk's age 0-17 filter (clothed photo references, e.g. age 15) -> REFERENCE / IMPORT;
Scan3Dmall "Asian kids collection" on CGTrader (10 clothed children) - consent not stated -> REFERENCE only. The
search tool refused one child-scan query. **No shippable child scan.**

**Better than what we have (rule f):** older faces - deep3dstudio's 60s-70s (16K, cross- and parallel-polarised) and
SP-6M beat HSRD-100 on resolution and polarisation, both paid or by contract (IMPORT / TRAIN, not SHIP); coily hair -
KhitrovArt and PixelHair beat the Blender demo for afro styles (IMPORT); sclera - Bauer's photographed set beats the
Commons photos (IMPORT). Teeth, nails, children: nothing better found.

## 3 · Sites and how they were found

deep3dstudio, Scan3Dmall ("best place to buy 3d head scans asian"); 3D.sk ("best skin texture packs ... cross
polarized 2026"); Human Alloy (HF `license:other` + scan); SP-6M ("3DCAP 3d scan people store head scans"; 3DCAP not
found); KhitrovArt, PixelHair ("artstation marketplace afro hair groom ..."); khaloui ("afro coily 4c hair groom
blender realistic buy"); Bauer, FlippedNormals ("realistic eye texture pack sclera veins iris 8k 3d buy"); Red Nebula,
Lashko ("realistic teeth gums tongue 3d model scanned texture buy"); Artec, Another World ("3d scan ears pack ...");
AI Hub (Korea: "AI Hub 한국인 얼굴 3D 스캔 데이터셋 이용 조건"); Magnific (freepik redirect); SizeGlobal (non-commercial),
Renderbot (2021, one-year royalty-free), SnapTank (2016-17, status unknown).

## 4 · Query log (the agent's; every filter it applied)

- **Pexels** (the site's search page, page 1; filter long side >= 3000 px, first 7-9 shown; a console-encoding crash
  cut several lists short): human eye iris macro, iris macro; dark skin close up, black skin texture macro, asian skin
  close up, old skin wrinkles close up, elderly hands close up, freckles close up, mole on skin, age spots, child skin
  close up, sole of foot close up, palm of hand close up, skin pores macro; afro hair close up, curly hair texture close
  up, grey hair close up, braids close up, dreadlocks close up, beard close up, stubble close up, grey beard close up,
  mustache close up, eyebrow close up, eyelashes macro, hairy arm close up, chest hair close up; bloodshot eye macro,
  eye sclera close up, old man eye close up, eyelid close up, teeth close up, crooked teeth, gums close up, tongue
  close up, fingernail close up, toenail close up, natural nails macro, lips macro, ear close up, nipple close up,
  areola (SafeSearch hides nudity).
- **Unsplash** (`/napi`, 30 a page - see the disclosure; filters: Unsplash+ items dropped, long side >= 3000 px): iris
  macro 337; dark skin texture close up 8,829; wrinkled skin elderly close up 1,612; freckles skin macro 3,381; afro
  hair texture 5,627; beard stubble close up 3,862; eyelashes eyebrow macro 1,824; hairy arm body hair 5,792; bloodshot
  eye veins 3,664; teeth close up 2,245; tongue close up 2,318; fingernail close up 1,816; lips macro texture 267; human
  ear close up 860; grey hair close up 784.
- **Pixabay** (photos only; filters: `isAiGenerated` dropped, long side >= 3000 px): iris macro eye 53,020; skin close
  up (2 of 106 AI); afro hair, beard, teeth close up - not loaded; fingernail close up (title only). Gap: three pages.
- **Flickr** (`license=7`, `8`, `7,8`, SafeSearch on): eye iris close up 0; eye (8) 210, military; teeth (8) 37;
  national eye institute (8) none; beard (7) 1,010 archive portraits; skin close up (7,8) 3; hair (7) 1,184 archive
  portraits. **Licences 7 and 8 hold no close-up texture sources.**
- **Hugging Face** (`filter=license:other`): datasets face 42, head 32, skin 15, hair 0, eye 7, iris 16, teeth 0,
  dental 3, nail 3, scan 30, 3d 89, human 134, avatar 4, portrait 5, beard 2, texture 9, albedo 1, mesh 19, body 12;
  models skin 36, skin-texture 2, texture 34, uv 23, albedo 1, pbr 3, hair 29, iris 29, eye 36, teeth 3, face-texture
  0, wrinkle 2, freckle 1, pores 0, macro 20. Cards read: humanalloy; qlean nails and full-body (gated, academic);
  inlineresearch/krea2-skin-lora ("other" a placeholder, provenance unknown); Purz/uv-unwrapped-head (Civitai licence,
  FLUX.1-dev base); a FLUX.3 klein skin LoRA (flux-kommunity); skin-lora-krea-2 (Krea 2 licence); KETI human3r,
  DH-FaceVid (gated). Nothing shippable.
- **Browser / pages:** 3D.sk terms, commercial terms, pricing, models; AI Hub (0 hits); ArtStation Marketplace EULA
  (§5(d) no making the Product "available to others to use, download or copy"; Standard: one Work, <= 2,000 sales /
  20,000 monthly views); Gumroad (Bauer); FlippedNormals; Fab KhitrovArt; Booth "リアル 肌 テクスチャ" (569 hits, all
  VRChat stylised materials); Artec ear; kaboompics licence (404); RenderHub agreement and AI policy; TurboSquid
  licence; Superhive coily, ears, eye pack; sp-6m.com; Magnific terms; data.go.kr 15146383 (a talking-face set, "no
  licence-scope restriction"). 403 / 404: deep3dstudio on ArtStation, 3d.sk by WebFetch, renderhub.com/licenses,
  sp-6m.com/licence, yelzkizi pages, CGTrader wig pack (empty).
- **Web searches** (three with `allowed_domains`: renderhub.com, flippednormals.com, 3dscanstore.com): best place to
  buy 3d head scans asian; where to buy 3d scans of black people head texture; deep3dstudio head scan african black
  male female 60s 70s; 3d scan store elderly old man head scan buy; 3D scan of child head buy commercial license
  photogrammetry kid; best sites to buy human 3d scans heads bodies list ten24 triplegangers alternatives; Infinite
  Realities scan store buy head scan dataset license; 3D Lab Kyoto head scan Japanese person buy license; Human Alloy
  3D scans price license ethnicity skin texture; xoio air 3d people scans license real-time redistribution; "3D People"
  posed people scanned 3d people license price real-time; SnapTank 3D scans human store; Renderbot free 3D scanned
  people commercial license; 3DCAP 3d scan people store head scans; Scan3Dmall asian 3d scan models cgtrader hong kong;
  3dscanstore HD head black female OR african male OR older 60 head scan price; a child-scan query (refused by the
  tool); best skin texture packs for 3d characters scanned cross polarized 2026; 3d.sk skin texture photo sets cross
  polarized price subscription license; Texturing XYZ SKAP skin scanning service price; realistic nail texture 3d
  fingernail toenail scan; 3d scanned hands and feet with nails 16k texture buy scan store; lip texture displacement
  map 3d scan lips close up pack; 3d scan ears pack realistic ear models scanned buy; realistic eye texture pack sclera
  veins iris 8k 3d buy; realistic teeth gums tongue 3d model scanned texture buy; free realistic beard groom blender;
  afro coily 4c hair groom blender realistic buy; artstation marketplace afro hair groom xgen alembic realistic 4c
  kinky; body hair groom blender chest arm legs realistic asset; best free stock photo sites like pexels unsplash
  pixabay 2026; renderhub "Extended Use License" terms redistribute; flippednormals marketplace license; yelzkizi
  pixelhair license terms commercial redistribution; Japanese: 3Dスキャン 人物 頭部 データ 販売 商用利用, 日本人 3Dスキャン
  頭部 モデル 販売, Booth 肌テクスチャ リアル 写真 素材 3DCG 商用可; Chinese: 人头扫描模型 购买 高精度 皮肤贴图 写实, 亚洲人
  头部扫描 数据 出售, cgmodel 中国人 扫描 人头 模型 8K 贴图; Korean: 3D 스캔 인물 얼굴 데이터 판매 한국인, AI Hub 한국인 얼굴
  3D 스캔 데이터셋 이용 조건, aihub.or.kr 한국인 3D 스캐닝 데이터, AI허브 데이터 이용정책.

## 5 · Not verified

Licence text UNREAD: Daniel Bauer, FlippedNormals, PixelHair, SP-6M's dataset licence, Artec 3D, Daz, AI Hub (and
its 500-person Korean scan set, known from news only), Kaboompics, Burst, StockSnap. No samples of deep3dstudio's paid
scans or KhitrovArt's grooms; 3D.sk's free samples need an account; Pexels / Unsplash AI origin (no EXIF); Pixabay past
three pages; whether a free open-source character app is a "larger Creation" (RenderHub) or a "Work" (ArtStation).

## 6 · What this changes

The cut sources are mostly **IMPORT** (a user's own purchase) or **TRAIN** (by contract), rarely **SHIP**: royalty-free
and store licences bar files that third parties can open, which an open-source download always allows. What ships
stays the CC BY scans (HSRD-100, Sketchfab incl. Renderpeople's own uploads), Ten24's sample, BlenderKit as a base,
and hand-picked stock photos as small patches. New SHIP finds: none at scan quality. New best-in-class but IMPORT-only:
deep3dstudio's 16K cross-polarised older heads ($12.99), KhitrovArt / PixelHair coily grooms, Bauer's photographed
sclera. Gaps that stay: children, nails, sharp sclera veins, older Black faces (70+).
