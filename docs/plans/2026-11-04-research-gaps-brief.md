# Brief - the asset search for the gaps (2026-11-04)

> For the session "just-stage asset search", sent by the main session (just-stage) on the user's word: "i opened
> another sessioj called just stage asset search please send it the search info and dont make the same search mistakes
> you have been making ... remember the mistakes you made before like limiting license to creative commons becuae
> others listed assets as free and for commercial use but didnt have anything about creative commons".
> Your results go in ONE new file: `docs/plans/2026-11-04-research-gaps.md`. Touch no other repo file, don't commit;
> message the session `just-stage` with the path when done (and if you hit a question only the user can answer).

## 1 · What JustStage is and how assets are used

A free, open-source (GPL) app for realistic human characters; **CC5 is the standard** (the user, 2026-11-04). The bar:
realism and variety for nine parts (skin by ethnicity and age; scalp hair; facial hair; brows and lashes; body hair;
eyes incl. sclera; mouth; nails; lips, ears, nipples). Assets are **inputs to our own maps**, not shipped as-is: scans
become skin bases (delit, wrapped, re-baked), photos become small patches and calibration targets, references are
looked at. A shipped character is never one scan's face (likeness rule).

**Licences are labels, never filters.** Report every real, high-quality source with its licence clause quoted from the
source's own page, and paid ones with the price. "Free for commercial use" site licences (Pexels-style: "use, copy,
modify ... for commercial or non-commercial purposes", no standalone resale) count exactly like Creative Commons - the
earlier briefs wrongly cut them. Label each find with routes (`2026-11-04-research-licences-redo.md` §1):
- **SHIP** - may be included, modified, in the app's open download;
- **FETCH** - may not be included, but each user may get it from the source;
- **IMPORT** - the user buys or downloads it and our importer reads it;
- **TRAIN** - the licence allows ML training (our texture work - delighting, tiling, projecting, building maps,
  running a model on one photo - is NOT training; the user: "your not really using it as ai traing like lora so i dont
  think that is a problem");
- **REFERENCE** - looking only.
The user's other licence calls: Pexels usable; BlenderKit royalty-free as a base ("your not reselling blender kit, its
just part of an app"); Ten24's sample ships with credit. Non-commercial and research-only sources are reported too
(REFERENCE / TRAIN labels), never dropped.

## 2 · The job - the gaps only (everything else is already searched - §3)

In priority order:

1. **Variety: the people we have no scan or sharp photo of.** Our 21 scans (§3) leave these holes: **older people of
   colour, 60+, men and women** - one older woman of colour (an elderly South Asian woman, a Sketchfab CC BY head),
   no older Black or Hispanic woman, and no Black person over 64 that we know of; **groups never searched
   by name** - Middle Eastern and North African, South Asian (one elderly woman; no man above 1K), Southeast Asian,
   Indigenous peoples (the Americas, Australia), Pacific Islander - any age. Wanted: textured 3D head or body scans,
   and sharp close-up photos of face and hand skin (pores, wrinkles, age spots, tone) at original resolution.
   **List each scan store's full catalogue by ethnicity and age from its own listing pages** (the pilot found
   deep3dstudio's "Middle East Female 20s Head Scan 033", which the last search's snippet-based list missed).
2. **Sclera veins.** Our method is procedural (the realism brief, rec 12: veins denser at the corners, redness,
   yellowing with age, melanosis), so the need is **sharp references to calibrate it** (DSLR macro sclera, by age and
   ethnicity), photographed sclera texture sets, and any method shown to beat procedural veins (with evidence).
3. **Nails, finger and toe.** Our method is a layered nail shader (rec 14: blood-coloured bed seen through a clear
   plate, lunula, white free edge, cuticle, ridges, yellowing with age), so the need is **sharp macro references across
   skin tones and ages** (incl. the pigment bands common on darker skin, ageing ridges and yellowing), scanned or
   photographed nail texture sets (paid ones with price), and how CC5 builds nails only if it goes beyond what's known
   (CC5: SkinGen nail layers, 29 + presets; a 2048 nail tile).
4. **Children and teens.** Our route is the generator (rec 4: shape from MPFB2's CC0 age targets, skin adapted from
   adult bases), so the need is **calibration data**: how child skin differs (pore size, smoothness, vellus hair, tone,
   eyes) from measured studies; how CC5 makes child characters (never researched); clothed face, hand and eye
   close-ups whose consent or model release is stated. **Nothing else involving minors - no nude or partly nude images,
   under any circumstances.** If a tool or site refuses a query, log it and move on.
5. **Licences never read** - read at the source, quote the clause: Daniel Bauer "Eye Textures @ 8K" (Gumroad),
   FlippedNormals Eye Kit, PixelHair (yelzkizi; 403 last time), Artec 3D's free ear / eye / hand scans (behind a download
   pop-up), the SP-6M dataset licence, Daz body-hair sets, Kaboompics (404 last time), Burst (Shopify), StockSnap - and
   every new site you find (nappy.co/license; CreateHER Stock; Jopwell Collection; the SBVPI and MOBIUS request forms).
6. **Better than what we have** (one or two plain queries per part, report only what beats ours, with the evidence):
   brows and lashes (MakeHuman `eyebrows01` CC0 masks; the Blender demo's brows / lashes, CC BY-SA), body hair
   (MakeHuman fur.blend, CC0), ears (nothing shippable; Another World Studios' $18 scanned set, IMPORT), lips (Commons
   CC BY-SA close-ups), iris (Commons macro photos, CC BY 4.0 - Lizapopova143, Thomas Tolkien, Kamil Saitov), straight
   and wavy scalp hair (the Blender "Hair Styles" demo, CC BY-SA). The last search already did this for older faces,
   coily hair, sclera, teeth, nails and children - don't repeat those.

## 3 · What is already searched - do not repeat (from the logs, passages read)

Files: `docs/dev/RESEARCH.md`; `docs/plans/2026-11-02-research-texture-source.md` §5;
`2026-11-04-research-hf-assets.md`; `2026-11-04-research-other-sites.md`; `2026-11-04-research-redo-sources.md`;
`2026-11-04-research-licences-redo.md`; `2026-11-04-realism-review-brief.md` §4. On disk: `.dev/downloads/` (hsrd100,
other_samples, redo_samples, ten24_sample, hf_samples, mh_skins02, scans). **Before saying "we have no X", grep those
files and `.dev/downloads/` for X.**

- **Our 21 scans:** HSRD-100's 10 people (CC BY 4.0, 16K: Black men 24 and 64 - the 64-year-old in a bucket hat in
  every pose - Black woman 22, Hispanic man 62 and woman 23, Asian man 25 and woman 21, white man 50, white women 60
  and 41) + 11 Sketchfab CC BY heads (mostly white, one elderly South Asian woman, two dark-skinned full bodies, one
  olive full body); Ten24's 2016 sample (light-skinned adult man, 16K, ship with credit).
- **Sketchfab:** ~60 API queries (people category; licences by / cc0 / by-sa; each ethnicity, age, body term).
- **Hugging Face + Zenodo:** keyword and licence-tag searches incl. `license:other`; kids 83, elderly 52, ethnicity 9
  were noise; children's face sets non-commercial.
- **Wikimedia Commons:** fingernail close-up 704, toenail 1,302, category Nails 105 (48 at 2000 px+), Lunula 7,
  "sclera blood vessels eye" 427 (none at 2000 px+ in the top 15), category sclera, close-up skin, children's eyes,
  iris categories (462 close-ups of one eye, 158 at size).
- **Flickr:** licences 4, 5, 9, 10 - fingernail macro 60, skin macro 2,933, eye macro 4,000; licences 7, 8 - no
  close-up texture sources.
- **Kaggle:** nail, fingernail, sclera, children face - ML sets of small phone photos.
- **Pexels:** page 1 only (first 7-9 per query; a crash cut lists short) for dark skin close up, old skin wrinkles,
  elderly hands, child skin close up, bloodshot eye macro, eye sclera close up, old man eye close up, fingernail close
  up, toenail close up, natural nails macro. Found: dark skin 7479965, 7480267; elderly 7544829, 7544832, 7544826,
  36730753 (hands); freckled child 8396129.
- **Unsplash:** the top 30 per query only, through an internal endpoint (a breach of its terms - never again): e.g.
  fingernail close up (1,816 results), bloodshot eye veins (3,664), wrinkled skin elderly (1,612), dark skin texture
  (8,829).
- **Pixabay:** three pages; afro hair, beard and teeth not loaded; fingernail by title only.
- **Stores read:** deep3dstudio (found: Asian F 60s/70s, Asian M 70s, European M/F 60s/70s, African M 20s, African F
  30s - the full catalogue NOT enumerated), 3D.sk (age 0-17 ... 71+ and ethnicity filters; paid), 3D Scan Store
  (reference only), Scan3Dmall kids (consent not stated), SP-6M, Human Alloy (2K diffuse), Bauer, FlippedNormals,
  Realistic Eye Pack (1K), Red Nebula, Lashko, Another World ears, Artec, Triplegangers samples (CC BY-NC-ND),
  Renderpeople (their Sketchfab uploads CC BY).
- **Also done:** GitHub (16 queries), Smithsonian, Europeana, OpenGameArt, itch.io, texture sites (TextureCan,
  cgbookcase, 3DTextures.me, FreePBR, ambientCG), Japanese, Chinese and Korean sites.

## 4 · My pilot queries today (rule d) and what they taught

1. "free stock photos of older black people close up faces" -> only paid stock (Getty, iStock, Adobe; one
   AI-generated, editorial). **So:** search the free sites' own search pages, and find niche sites by discovery.
2. "best free stock photo sites for black and brown people diverse" -> nappy.co, CreateHER Stock, UKBlackTech,
   Jopwell Collection, Disabled and Here, TONL (paid), round-up articles (goodgoodgood.co "13 sites"). nappy's licence
   is reported as CC0 by its own page but CC BY-NC by one third party [snip] - **read nappy.co/license yourself.**
3. "fingernail images dataset download license" -> Roboflow Universe nail sets listed CC BY 4.0 [snip], likely small
   phone photos like Kaggle's. **Measure one sample's resolution before reporting.**
4. "how to texture realistic fingernails 3d character" -> forum advice only (the bed's colour under the plate,
   subsurface, a separate mesh, more texel density) - our planned shader already does this; a paid CGTrader nail pack.
5. "sclera blood vessels image dataset high resolution" -> **SBVPI** (Univ. of Ljubljana): "1858 high-resolution RGB
   images of eyes from 55 subjects", DSLR with macro lens, "resized ... to 3000x1700"; access by a hand-signed form; no
   terms on the page [page] - **read the form's terms; never sign or send it.** MOBIUS: 16,717 phone images, 100
   subjects.
6. "realistic eye sclera veins texture free download" -> mostly AI-generated textures (aitextured.com). **Mark
   AI-generated content as such - it is not a photo reference.** Also: a free Substance Designer "Procedural Eye
   Generator" (CGTrader / Cubebrush), Andy Cuccaro's free Blender procedural eye (Gumroad).
7. "children skin vs adult skin differences pores texture measured study" -> studies on thickness, barrier, smoothness
   (e.g. PMC5606948; Chinese children 1-10; Japanese 10-14), none on pores. 8. "facial pore size by age study children
   adults measured" -> adult pore studies (PubMed 29393550: 434 polarised images, counts rise with age, nose and
   forehead above cheeks); a lead: a PMC7649423 table comparing cheek skin across children, youth, middle age, elderly.
9. "3d scanned head middle eastern man realistic texture" -> deep3dstudio "Middle East Female 20s Head Scan 033"
   (RenderHub), CGTrader "Middle East Man" / "Arabian man" (not stated as scans). **So:** enumerate catalogues.

## 5 · Where to look (find more by plain discovery searches first)

- **Free stock, past page 1, by plain queries per subject:** Pexels, Unsplash, Pixabay (their normal search pages - no
  internal endpoints, no scripts, no bulk fetching: their terms bar bots), nappy.co, CreateHER Stock, Jopwell,
  UKBlackTech, Kaboompics, Burst, StockSnap, rawpixel's public-domain set, Openverse (an aggregator), and the sites
  your discovery finds.
- **Where the people are:** regional stock and scan sites for Africa, the Middle East, South and Southeast Asia,
  Indigenous and Pacific communities, searched in their own languages where natural (e.g. Arabic, Hindi, Indonesian).
- **Scan stores and marketplaces** (full catalogues, price, licence): deep3dstudio (RenderHub / CGTrader / its own
  site), 3D.sk, Triplegangers, Renderpeople, 3D Scan Store, Scan3Dmall, Human Alloy, CGTrader, TurboSquid, Fab,
  ArtStation, RenderHub, Sketchfab Store, Superhive, BlenderKit.
- **Datasets and science:** biometric eye sets (SBVPI, MOBIUS, others), dermatology image sets (candidates from
  memory, unverified: ISIC archive, Fitzpatrick17k, DermNet - check each), medical image libraries (e.g. Wellcome
  Collection), multi-ethnic 3D face datasets, papers with measured child skin and pore data.

## 6 · How to work

- First queries the plain way a person types them: "where can I find free photos of elderly black women", "free stock
  photos middle eastern people", "realistic fingernail macro photo", "eye veins macro photo", "how does character
  creator 5 make kids", "is there anything better than <what we have>".
- Pilot two or three queries per venue and read the hits before running a list; narrow what returns noise, widen what
  returns nothing.
- **Every yes / no on a licence quotes its clause from the source's own page; anything else is marked UNREAD.** Mark
  every fact: [page] read at source, [API], [meas] measured, [seen] looked at, [snip] snippet only.
- Pages that block fetchers (403): read them in the user's Chrome (your own new tab, closed afterwards).
- **Never:** create accounts, log in, buy, sign or submit forms, or use the graphics card (it is shared). Samples only,
  to measure resolution and sharpness at 1:1, into a new folder `.dev/downloads/gaps_2026-11-04/<site>/`, at most
  ~500 MB in all; never run code from a download.
- Report resolution measured or stated (no silent size cut-offs); if you use a size threshold to triage, log it.
- Recognisable people: note model-release terms (Unsplash: recognisable people "not covered"). Images of Indigenous
  people: note any community or cultural terms the source states (e.g. on images of people who have died).
- Before each venue, check your queries against §8.

## 7 · Output - `docs/plans/2026-11-04-research-gaps.md`

Per gap (§2 items 1-6): each find - what, where (URL), resolution, licence clause quoted (or UNREAD), routes, price,
AI-generated or not, marks; then "what this changes" for that gap. Then: the licences read (item 5); a "not found"
list phrased as gaps in the search (what was searched), never "nothing exists"; and **the full query log with every
filter applied and its result count**. Message `just-stage` when done.

## 8 · Checked against my search mistakes (global CLAUDE.md research rule 7; memory `search-mistakes`)

- a. Licence as a filter -> no allowed-licence list; "free for commercial use" site licences count like CC; paid and
  non-commercial reported with labels.
- b. Verdicts from snippets -> every licence verdict quoted from the source's page, else UNREAD; marks on every fact.
- c. Too narrow -> six items covering variety, eyes, nails, children, licences and better-than for every other part;
  every kind of venue in §5 incl. regional and non-English sites and datasets.
- d. Too broad -> my nine pilots in §4 and what they changed; pilot per venue before a list.
- e. Not the plain way -> plain first queries in §6.
- f. Never asking if ours is still best -> item 6, and items 2-4 ask for methods that beat our planned ones.
- g. Briefs from headings, research repeated -> §3 built from the query logs' passages, with "do not repeat".
- h. A first search too small -> all gaps, their methods' calibration data and the unread licences in one brief.
- i. Launching when told to wait -> the user asked for this send.
- j. Hand-rolling before the standard -> "how does CC5 do X" for nails and children; methods only with evidence.
- k. Mechanical filters -> no licence codes, tag lists or "top N"; any size triage logged; no internal endpoints.
- l. Results used unread -> your query log and filters are required; I read them before using anything.
- m. Picks forgotten -> picks go into RESEARCH.md (by me) with why and the query that found them.
- n. Claiming we lack what we have -> §3's inventory and the grep rule before any "we have no X".
