# Attribution

Every asset JustStage fetches, bundles or ships — or builds a shipped asset from — with its source, author and
licence. A new asset gets its row **in the same change that adds it** (AGENTS.md). "Fetched" data lands under
`extension/juststage/data/fetched/` from `tools/fetch_data.py` at a pinned commit or hash; "library" assets are built
into the user's JustStage library by `tools/build_skins.py` / `tools/build_library.py`.

## Fetched data (shipped with the extension)

| What | Source | Author | Licence |
|---|---|---|---|
| hm08 base mesh, targets, mesh metadata, rigs, expressions, UV layers, node trees (incl. the procedural eye, `procedural_eyes.json`), region masks (`textures/mpfb_*.jpg`) | github.com/makehumancommunity/mpfb2 @ 6ff1eb35 (`src/mpfb/data/`) | MakeHuman / MPFB2 contributors | CC0-1.0 (MPFB2's LICENSE.md, part C) |
| Hair-editor pack (`hair/haireditor/hair.blend`) | files.makehumancommunity.org/functional/haireditor.zip | Tomáš Klecer (MakeHuman) | CC0-1.0 |
| Faceunits 01 (52 ARKit face units) | files.makehumancommunity.org/functional/faceunits01.zip | Mika Suominen (MakeHuman) | CC0-1.0 |
| ICT-FaceKit neutral mesh (eye occlusion and tearline strips) | github.com/USC-ICT/ICT-FaceKit @ da5f95a6 | USC Institute for Creative Technologies | MIT |
| GNM head model v3 | huggingface.co/google/gnm-v3 | Google | Apache-2.0 |
| Studio Small 09 HDRI (2K) | polyhaven.com/a/studio_small_09 | Poly Haven | CC0-1.0 |
| Haemoglobin molar extinction | omlc.org/spectra/hemoglobin | Scott Prahl, OMLC (1998) | no licence stated; cited |
| CIE 1931 2° colour-matching functions; CIE D65 | files.cie.co.at | CIE | no licence stated; cited |

## Tool inputs (not shipped; used to build shipped data)

| What | Source | Author | Licence |
|---|---|---|---|
| NIST skin reflectance (100 people) | opendata.nist.gov, doi:10.18434/M38597 | Cooksey, Allen & Tsai (NIST, 2017) | public domain |
| OpenRigLogic (DNA and RigLogic, built into a wheel) | github.com/EpicGames/OpenRigLogic @ ea253d5 | Epic Games | MIT |

## Library skins and characters (built by our tools from these)

The four mapped skins (Daniel, Amara, Walter, Mei) and the library characters wearing them mix layers from these
scans of real people (Sketchfab, "CC Attribution" - CC BY 4.0 - unless noted), under a face painted by an image model:

| Scan | Sketchfab id | Author | Licence |
|---|---|---|---|
| Head scan 13 (photogrammetry) | 5e6d2804405449e6b3bd96cd12d8b1ab | yaro.pro | CC BY 4.0 |
| Head scan 02 (Optimized PBR) | 2f1978b43032415c8fdf911c7acfb1a4 | Cratera Games, scan by yaro.pro | CC BY 4.0 |
| Rudavin Sergey 3d portrait | e1fe86107058409c9fb88b50f5ef80fd | rudavin | CC BY 4.0 |
| Female head scan | b157e28076484a3f9f4f41b5e0f70770 | whynotmeebaby | CC BY 4.0 |
| Head 03 A | 04a94494d88d48d18c46b82c7ab7c7b8 | Nikitos & 3130 (@vrcityphoto) | CC BY 4.0 |
| Ammamma Head Scan Polycam | 64fda4f6914d40b89bc07a9f5927357e | Krishna Prakash | CC BY 4.0 |
| portrait of model 2.0 | 6832a653f9c647aba01f77b5d774e9ba | 3130 | CC BY 4.0 |
| FREE DOWNLOAD: Attractive African woman 236 | f2c29b6947f34237a0bfdc777120ef28 | deep3dstudio | CC BY 4.0 |
| FREE DOWNLOAD Athletic African man walking 223 | f9a8e3b108f04e998815593f78f163b1 | deep3dstudio | CC BY 4.0 |
| Carla Rigged 001 | acf520f450d14dd799f98a6fede3edf5 | Renderpeople | CC BY 4.0 |
| Infinite, 3D Head Scan (pore tile) | three.js `examples/models/gltf/LeePerrySmith/` | Lee Perry-Smith ("based on a work at www.triplegangers.com") | CC BY 3.0 |

Painted faces: FLUX 3 Image Klein / FLUX.2 klein 4B (Black Forest Labs), run locally; the outputs are ours, the models'
licences (FLUX Kommunity licence / Apache-2.0) are labels.

## Downloaded for the next skin bases (not yet in a shipped asset)

| What | Source | Author | Licence |
|---|---|---|---|
| HSRD-100 raw scans (13 poses of 10 people) | huggingface.co/datasets/digitalrealitylab/HSRD-100 | Digital Reality Lab | CC BY 4.0 |
