# Research — licences read at their sources, the redo of the filtered search (2026-11-04)

> The user's go: "so redo the search and do it correctly your rec go", after my CC-only filter in four agent briefs
> (TASKS "SEARCH RULE"). This file holds the licence pages I read myself; the discovery agent's finds land in
> `2026-11-04-research-redo-sources.md`. Every verdict quotes its clause from the source's own page [page]; [API] an
> API record; nothing here rests on a snippet. Checked against the global CLAUDE.md research rule 7 (a-m).

## 1 · What "usable" means here (the routes)

Our case: a free, open-source app (code GPL/MIT) whose download and repository anyone can open; its characters are
edited and exported by users. Every source gets routes, never a yes/no filter:
- **SHIP** - we may include it, modified, in the app's download.
- **FETCH** - we may not include it, but each user may get it from the source (the app points or calls there).
- **IMPORT** - the user buys or downloads it under their own licence and our importer reads it.
- **TRAIN** - the licence allows machine-learning training (matters only if we pick a small LoRA; our texture work -
  delighting, tiling, projecting, building maps, running a model on one photo - is not training. The user: "your not
  really using it as ai traing like lora so i dont think that is a problem").
- **REFERENCE** - looking only.

## 2 · The licences

| Source | Clause, quoted from its own page | Routes |
|---|---|---|
| **Pexels** (Terms, updated 2026-10-20) | §5: "the right to download, use, copy, modify or adapt the Content for commercial or non-commercial purposes"; prohibited: "sell or distribute the Content ... on a Standalone basis", Standalone = "where no creative effort has been applied ... using the Content in its original form or solely using a filter, changing colors, resizing or cropping ... remains Standalone use"; §7B uploaders may not post generative-AI content (no guarantee); §8 "Data mining, extraction, scraping ... for machine learning purposes" and "Bulk, large-scale or systematic copying" prohibited; some items CC0 (marked) | SHIP (made into new textures, picked by hand); TRAIN no by bulk collection |
| **Unsplash** (Terms) | §5: "irrevocable, nonexclusive, worldwide copyright license to download, copy, modify, distribute, perform, and use images ... including for commercial purposes"; not "to compile images ... to replicate a similar or competing service"; recognisable people not covered; §8 no selling "without first significantly or meaningfully updating"; no bots "Except for use of the Unsplash API"; no use "in connection with any machine learning and/or artificial intelligence datasets (e.g., training ...)" | SHIP; TRAIN no |
| **Pixabay** (licence summary + Terms) | "Modify or adapt Content into new works"; "You cannot sell or distribute Content ... on a Standalone basis" (same definition as Pexels); §8 scraping "for machine learning purposes" and bulk copying prohibited | SHIP (new textures, by hand); TRAIN no by bulk |
| **BlenderKit** (docs/licenses) | Royalty Free "allows commercial use without mentioning the author but doesn't allow for re-sale of the asset in the same form (eg. a 3D model sold as a 3D model or part of assetpack or game level on a marketplace)"; "royalty free license doesn't allow to re-sell 3D models even if modified"; "Both allow you to sell higher-level-derivative works"; free giving-away not addressed; the terms-of-use page 404 | SHIP as a base for our own maps, labelled (decided 2026-11-04, the user: "your not reselling blender kit, its just part of an app so i tink its ok, it would be different if you where reselled the assets directly vers using thins as base"; the clause bars re-sale and allows "higher-level-derivative works") - never its raw files in our download; IMPORT; CC0 items SHIP. Downloads need a BlenderKit login (the user's) |
| **Superhive** (support article 49) | Standard Royalty-Free: "personal, educational, or commercial purposes"; reselling, redistributing or repackaging needs "explicit permission from the original author" | IMPORT; SHIP with the author's written permission; CC-BY items SHIP |
| **Fab** (EULA, 2024-10-01) | §6(a): may not combine Standard-License content with "GNU General Public License (GPL) ... or Creative Commons Attribution-ShareAlike"; §6(b)(iii): may not "make Content available in world- or level-editing tools or templates or other modeling tools that allow works to be exported"; §16(l): only "NoAI"-tagged content barred from AI training, and programs that "solely operate on the original content" are not Generative AI Programs; CC-BY listings follow CC | IMPORT; TRAIN (non-NoAI items); SHIP no (Standard); CC-BY listings SHIP |
| **CGTrader** (Terms §21A) | "strictly limited to Incorporated Product"; in software "you must take all commercially reasonable measures to prevent the end user from gaining access to the Product"; ML input allowed under the plain Royalty Free licence, not under "Royalty Free License, No AI" (subscribers always get No AI) | IMPORT; TRAIN (plain RF only); SHIP no |
| **Sketchfab Store** (licenses, Standard) | may not "make available the Licensed Material as a stand-alone file" or "in a way that allows third parties to use, download, extract or access" it; Editorial: no commercial use | IMPORT; SHIP no. Free Sketchfab CC listings follow CC |
| **HumanScanRepository** (licensing guide; free-models FAQ) | samples: "free for personal and commercial use with credit ... including ... the development of a commercial project like a game ... However, we do not allow resale or free distribution on other websites, either of the original or any derivatives from the model. Please let us know if you are still determining whether you can use our samples in your project"; paid Commercial: "Redistribution, resale, or sublicensing of the models outside the agreed commercial project is prohibited"; AI: "Yes, Commercial Use Licenses permit the use of models in AI and machine learning projects"; custom licences: "we are open to discussing" | IMPORT; TRAIN (paid commercial); SHIP of a sample-derived texture unclear - they invite the question (an email is the user's to send) |
| **Texturing.XYZ** (Terms & Licensing, updated 2026-08-29, `/pages/terms-of-service`) | §7 without written authorisation you may not "Release Materials or derivative products under an Open Source License", nor sell or distribute them "as part of a texture pack, material pack ... or comparable asset collection", nor use them "with artificial intelligence, machine-learning ... or comparable systems or software"; §8 no customer assets "for reuse by other parties"; price seen: Female 30s Multichannel Face #07, $19.90 sale ($39.90 regular), 8081 x 5089 TIF | IMPORT only (a user's own purchase); SHIP no; TRAIN no; even running a model on it needs their OK |
| **Renderpeople** (General Terms, 2024-12-13) | free data: "The same provisions apply ... as for paid 3D data"; §4.2(a) datasets and training need a separate licence ("ML / CV LICENSES"); §4.2(c) no "Implementation of the 3D data in applications ... if third parties are thereby allowed to use the 3D data. Computer and video games are not affected"; §4.3(b) no "making the 3D data available in a way that allows third parties to easily download, extract" | from their shop: IMPORT; TRAIN by separate licence. **But** their own Sketchfab uploads are CC BY 4.0 - "Mei Posed 001" by `renderpeople`, licence "CC Attribution" (by/4.0), downloadable [API] - so those files SHIP with credit |
| **Triplegangers** (Terms of Supply, 2025-05-05) | §8.1 commercial: derivative works "in video games, films, virtual reality ... or other digital or interactive products"; §8.3 not without written consent: "make available any of the Licensed Content or any derivative works ... on any online store, marketplace, or file-sharing platform of any kind"; no use "for training, validating, or otherwise creating machine-learning or artificial-intelligence models"; personal licence non-commercial | IMPORT; SHIP with written consent; TRAIN by separate licence |
| **Ten24 sample scan** (ten24.info/sample-scan) | "Feel free to use this scan as you wish for both commercial and personal projects. All we ask is that you provide us with a credit wherever it's used." Full body with an integrated head scan from their latest stage; 16K and 8K textures (PSD, JPG); ZTL and OBJ; RAW 15M-polygon OBJ; packages 1.3-2.5 GB; a light-skinned adult man in a sweater and jeans [seen]. Downloaded: OBJ package 1.97 GB [meas] - colour 16K / 8K (JPG, PSD), six normal-map levels (PSD), decimated OBJs 100k-2M, SubD levels 1-6 | SHIP with credit - the file's own grant governs it; the shop licence (next row) covers "the 3d models and Scans on the 3dscanStore website", which this free ten24.info file is not (the user, 2026-11-04: "no i dont wnat to ask ten24 i thought you said we dont need to?" - I had backed off on a guess at Ten24's intent, not on their text). The page as downloaded is kept at `.dev/downloads/ten24_sample/sample-scan-page-2026-11-04.html`. **Corrects** the "non-commercial" verdict (CG Channel, about 3D Scan Store's free heads) |
| **3D Scan Store** (Ten24 Media's shop; Terms & Conditions / Licensing, read in the user's tab) | every tier excludes "Integration of our scan data into any character maker programme whereby the results can be exported as 3d models in any 3d format. Including but not limited to Daz 3D, Reallusion character creator"; "It is NOT in any cases permitted to ... Release the 3D models or scans or derivative products under Open Source Licences"; "Sell or freely distribute character generators or digital humans created using AI training data derived from 3d scan store models"; "Use commercially or for profit a free download or giveaway product without expressed permission" | REFERENCE only - not even a user's own purchase may go into our app (a character maker that exports) |
| **Flickr licence 7** ("No known copyright restrictions", Flickr Commons usage page) | institutions have "reasonably concluded" no restrictions; "WITHOUT PROVIDING AN EXPRESSED OR IMPLIED WARRANTY"; per-institution rights statements | SHIP case by case, the institution's statement read per photo |

## 3 · What changed against earlier files

- Ten24: "non-commercial" (`2026-11-02-research-texture-source.md` 45-46, 305; `2026-10-29-research-10-character-assets.md`
  155-158) was about 3D Scan Store's free heads, read through CG Channel; Ten24's own sample scan is commercial-use
  with credit.
- Renderpeople: "bars making data available to third parties" (`texture-source.md` 306) is true of its shop; its
  own CC BY 4.0 Sketchfab uploads are a separate grant and ship.
- Texturing.XYZ: RESEARCH.md 211-215 said its licence was "not reached"; it is `/pages/terms-of-service`, read above.
  The brief's "comparable vendors forbid" was a guess that turned out right - now quoted.
- BlenderKit: "not shippable" (`2026-11-04-research-other-sites.md` 80-83) was too strong; its clause bars re-sale,
  not free inclusion - shippable as a base for our own maps (the user's call above), raw files never shipped.
- Pexels, Unsplash: usable (already corrected); Pixabay, never searched before, is usable on the same terms.

## 4 · Query log (mine)

WebSearch: "best sites for 3d scans of real people commercial use" (CG Channel posts on Renderbot, SnapTank, xoio,
3D People, 3D.sk, deep3dstudio); "where to get high quality human skin textures for 3d characters free or cheap"
(Gumroad free skins, CGTrader $8.99 skin pack, Superhive Premium Human Skin Pack, Fab Human Skin Material Pack,
Texturing.XYZ SKAP); "can I use royalty free 3d assets in an open source app" (polygoniq's GPL-code + royalty-free-asset
split; FORTEX's "part of a larger work such as an application"). Pages read: the table's sources; 404 or blocked:
blendkit.com/docs/terms-of-use, renderpeople.com/license, texturing.xyz/pages/license, triplegangers.com
terms-conditions-of-supply (the real path is terms-and-conditions-of-supply), 3dscanstore.com (403 by WebFetch; read in
the user's tab after they opened it), fab.com/eula by WebFetch (403; read in the browser).
