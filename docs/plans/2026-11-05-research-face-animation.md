# Research — face animation sources: expression shapes, wrinkle maps, body correctives (2026-11-05)

Asked for: which open sources and methods give the most realistic ARKit-52 / FACS expression shapes, expression
wrinkles and body correctives for ANY character from sliders, and how CC5 and MetaHuman give every custom character
expressions and correctives. Design today: DNA + OpenRigLogic, ARKit 52 as plain shape keys (first set MakeHuman's CC0
Faceunits 01), wrinkles = the DNA's animated maps (source undecided), body correctives = the DNA's RBF and twist-swing
layers (shape source undecided) — `docs/standards/skeleton-and-face.md` §2–3.

Evidence marks: **[page]** read on the source's own page or file; **[snippet]** search-result text only; **[code]** read in
a repo or source file; **[measured]** checked on disk here; **[inferred]** my reasoning, not a source.

## 0 · What we already had (rule 0, read before searching) and the search-mistake check

| Job | Already covered where | Evidence | Built? |
|---|---|---|---|
| Faceunits 01 (CC0, hm08, Mika Suominen) | RESEARCH.md 2188–2191; 2184–2187 | zip sha256, licence fields [page]; on hm08 `mouthClose`=1 lifts lower lip and chin ~27 mm, `eyeBlinkLeft` 0.2 sinks the lid 0.7 mm into the eyeball [measured] | loaded as the first set |
| ICT-FaceKit (MIT) | RESEARCH.md 2195–2197, 2223–2226 | 57 OBJs, ARKit names, FACS map [page]; shells move with every expression [measured] | eye shells only |
| MHR 72 expressions, neural correctives | `2026-10-29-research-05-bases-pass2.md` 157–163 | "artist-sculpted … not PCA" [page] | no |
| GNM 383 expression components | same file 185–188; RESEARCH.md 2201–2203 | README [page]; zero expression = neutral on purpose [page] | wrap to hm08 measured (0.87 mm mean) |
| Transfer tools | RESEARCH.md 2198–2200 | Surface Deform; `vasiliskatr/deformation_transfer_ARkit_blendshapes` and example-based rigging (MIT) [page] | no |
| No released model makes ARKit-52 for any head | RESEARCH.md 1973–1974 | agent, 2026-10-30 | — |
| Wrinkle technique (Oat, Jimenez, Raman WACV 2023, Blender Studio tension, Disney SGP 2023 / EG 2024) | `2026-10-30-research-skin-detail-shading.md` §2.2–2.3; `2026-10-29-research-10-character-assets.md` finding 11, §3a | Blender Studio page read; others snippet; Oat/Jimenez "not opened" | no |
| MetaHuman wrinkles = "animated mask multipliers" from RigLogic | `…-10-character-assets.md` 81–82, 502–505 | OpenRigLogic design.md [page] | spec only |
| Body: Dem Bones BSD-3, PSD/RBF, MHR correctives, SOMA-X candy-wrapper | `…-10-character-assets.md` §3h; `…-07-building-blocks-pass2.md` 416–429 | READMEs [page] | no |
| D3DFACS registrations (FLAME, non-commercial, testing only) | RESEARCH.md 2077–2079 | downloaded, 47,384 frames | no |

So the gaps were real gaps, not unbuilt recs, except one: the wrinkle **technique** was researched; its **source content**
and **driver for any face** were not. Checked `.dev/downloads/` (rule n): neutral scans only (`scans/`, `hsrd100/`,
`ten24_sample/`); no expression scans or wrinkle maps on disk; `.dev/cache/ict/` holds only `generic_neutral_mesh.obj`.

Search-mistake check (memory `search-mistakes`):
a. licence a filter? — no; every source below carries its licence as a label, paid ones with prices. b. snippets as
verdicts? — each fact marked; snippet-only facts say so. c. too narrow? — covered papers, GitHub, Blender extensions,
Superhive, vendor manuals, scan stores, HF datasets, Epic's source on disk. d. too broad? — piloted three plain queries
first (§6, 1–3), then narrowed. e. plain way? — first queries were the brief's plain ones. f. "better than" ours? —
asked for ICT-FaceKit, MakeHuman face units and MHR (§6, 5, 33, 34). g. briefed from headings? — §0 from passages read.
h. whole job? — all four gaps in one pass. i. told to wait? — no gate in the brief. j. hand-rolling? — the standard
(DNA/RigLogic, PSD/RBF, Oat/Jimenez masks) named first. k. mechanical filters? — none; GitHub searches sorted by stars or
date only. l. agent results unread? — no agents used. m. picks forgotten? — this file. n. "we lack X"? — downloads
grepped above.

## 1 · Top findings

1. **FACSHuman: 133 FACS action-unit targets already on hm08, validated by FACS coders.** `montybot/FACSHuman` ships
   `.target` files for MakeHuman (upper and lower face AUs with L/R splits, lip parting and jaw, eye and head positions,
   emotions) — "All the FACSHuman target files were created with Blender and the MH tools for Blender" [code]; licence
   LGPL-3.0 (LICENSE file) [code]; last push 2026-04-18, 55 stars, a Python 3 port `FACSHuman-Py3-Enhanced` [code]. Its
   AU12 target's vertex indices run to 14,565, inside hm08's 19,158 [measured]. Paper (Behavior Research Methods 2021):
   two FACS coders rated 47 single AUs at 64% and 85% identification, 54 AU combinations at 68–82% [snippet — Springer
   behind a login]. Same topology as ours: no transfer. It is the only open FACS set on hm08 besides Faceunits 01.
   ([repo](https://github.com/montybot/FACSHuman))
2. **No source compares the realism of any open expression set** (Faceunits, ICT, MHR, GNM, FLAME) head to head; searched
   §6 5, 6, 7, 32 — a search gap, not proof. What each set is built from is known: MHR's 72 "were sculpted by an
   artist" [page, arXiv 2511.15586]; GNM's expression space is "an uncentered PCA" per region over ~150,000 static
   expression samples of ~5,000 people [page, arXiv 2607.23687]; ICT scanned 79 people × 26 FACS expressions plus 99
   Triplegangers heads × 20, and "We fit expressions using generic blendshapes and non-rigid ICP" — its README does not
   say whether the 53 released shapes are those generic shapes [page, arXiv 2004.03458 §3].
3. **MetaHuman picks its wrinkle maps from a library of 153 scanned characters; it does not generate them per face.**
   UE 5.8's local texture-synthesis model `TS-1.3-F_UE_res-1024_nchr-153/ts_params.json`: `"n_characters": 153`,
   per character `"albedo": 4, "normal": 4, "cavity": 1` [measured]; the map types are `Base, Animated0, Animated1,
   Animated2` (`MetaHumanFaceTextureSynthesizer.h`) [code]; the API: `SelectNormal` "Select a normal texture map based on
   the input parameters", `SelectCavity` per "HF index", `SynthesizeAlbedo` [page, UE API]. `texture_attributes.json`
   tags each character's "Face Wrinkles" Low/Medium/High [measured]. RigLogic drives the masks: the Texture Logic node
   "blends 3 color-map and 3 normal-map variants based on the current RigLogic evaluation" [page, Poly Hammer docs].
4. **CC5 does the same with presets:** wrinkle sets are library files per actor on CC's shared UV —
   `Expression Wrinkles/CC5 2K/HD Aaron 2K.rlWrinkle`, `HD Ariana`, `HD Gibro`, `HD Mila`, `HD Neutral F/M`, and CC4's
   `Camila`, `Kevin`, `Susan`, `Neutral` (2K and 4K) [measured, F:\Reallusion Content]. Each set has five source maps
   (AO, Crease, Flow Map, Normal, Redness), three sets, regions named per set ("Set 2_Nose_Crease.png"); the Flow Map
   "Controls the timing of the wrinkle patterns" [page, CC5 manual]; plus the Face Tool to sculpt new ones [page, earlier].
5. **Mesh tension can drive wrinkles for any deformation, and its code is MIT.** Raman et al. (Microsoft, WACV 2023)
   "express tension as a function of the mean change in the length of the edges connected to a vertex", blend expanded
   and compressed wrinkle maps by it, and graft wrinkles from scanned identities onto ones without scans [page,
   microsoft.github.io/DynamicWrinkles]. "Code for computing mesh tension is available as a Blender add-on":
   `chiragraman/mesh-tension`, MIT, v1.5.6 for Blender 2.93, last push 2021-09-08 [code].
6. **Disney's fast dynamic micro-wrinkles run in a shader:** wrinkles split into N = 4 orientation bins, each rendered
   for neutral, maximal compression and maximal stretch; a fragment shader blends them by the per-texel stretch tensor
   (Alg. 3) [page, Weiss et al. EG 2024, CC-BY paper]. No code found. Jimenez et al. 2011 (opened this time): wrinkle
   normal maps added to the base as partial-derivative normal maps, RGBA masks, per-blend-shape weights; shader 0.31 ms
   on a low-end GPU, 96 KB [page].
7. **SOMA-X has one corrective model for every body backend, distilled from MHR, Apache-2.0.** "Training data is
   distilled from MHR" — ~80,000 MHR posed meshes mapped to SOMA's topology; "a single unified correctives model that
   applies to all backends", shown on SOMA-Shape, MHR, SMPL, **Anny** and GarmentMeasurements; joint rotations (6D) →
   J × 24 activations → per-vertex displacements, masked by skinning weights and geodesic distance; "learned correctives
   mitigate but do not eliminate these" artefacts; no numbers against plain LBS [page, arXiv 2603.16858 §3.5.2]. Anny
   (MakeHuman's mesh) already ships a "soma" topology [page, Anny README] — a MakeHuman↔SOMA correspondence exists.
8. **MHR's correctives are trained on 26,000 scans and don't depend on body shape.** A per-joint MLP over the joint and
   its parent and child (6D), ReLU-gated geodesic masks, L1 sparsity; 13,000 body + 13,000 hand scans; "The facial
   expression and pose corrective blendshapes are independent from body shape in MHR"; shape conditioning is future work
   [page, arXiv 2511.15586 §3.4]. Shipped as `corrective_activation.npz` + `corrective_blendshapes_lod?.npz` [code].
9. **Both vendors solve per character differently.** MetaHuman: rigging is a cloud request (`FAutoRigServiceRequest`,
   texture requests beside it [snippet, UE API]); "A Full Rig includes joints and blendshapes … A Joints Only Rig omits
   blendshapes" [page]; conformed meshes must be "the MetaHuman Template mesh in terms of topology" [page]; how the
   cloud computes an identity's blend shapes is not published. CC5: HD profile "Facial Expression Morph Sliders: 262",
   "Corrective Expression Sliders: 128" that "correct the animation flaws by different combination of expression
   sliders" [page]; per character, users "adjust bone positions or edit the morph results of the Corrective Rule
   Sliders" in the Facial Profile Editor [page].
10. **Audio2Face's blend shapes can't ship, but its paper states the industry recipe**: ARKit is the schema, custom
    targets are built "by transferring ARKit poses to the subject's neutral mesh", some poses replaced by range-of-motion
    captures, artists refine [page, arXiv 2508.16401]. Its Claire dataset: "NVIDIA AUDIO2FACE SAMPLE DATA LICENSE" — use
    "only to train and evaluate models using the NVIDIA Audio2Face Project"; "for demonstration purposes and not for
    production usage" [page, HF].

## 2 · Gap 1 — the most realistic open expression shapes

| Source | What | Built from | Topology | Licence (quoted) | Evidence |
|---|---|---|---|---|---|
| MakeHuman Faceunits 01 | 52 ARKit-named targets | artist (Mika Suominen) | hm08 | metadata "license": "CC0" | [page]; faults [measured] RESEARCH 2185 |
| **FACSHuman** | 133 targets: AUs 1–64 with L/R, combos, emotions | artist in Blender, FACS-coder validated 64–85% | hm08 (MakeHuman 1.x) | LGPL-3.0 (repo LICENSE) | [code]; validation [snippet] |
| MHR (Meta) | 72 FACS-based, unilateral, lip quadrants, gaze, jaw | "sculpted by an artist" | MHR LOD0–6 (triangles), no eyeballs or mouth interior | "Apache Software License 2.0" | [page] |
| ICT-FaceKit | 53 ARKit-named (L/R split) + 100 identity PCA | "generic blendshapes" used to register light-stage scans; released shapes' origin unstated | ICT head | "released under the MIT license" | [page] |
| GNM (Google) | 382–383 PCA components by region (eyes, lower face, tongue, pupil) | ~150,000 static expressions of ~5,000 people | GNM head (quads + tris), wrapped to hm08 already | Apache-2.0 weights | [page] |
| FLAME 2023 Open | 100 expression PCA (from SUPR's head) | 4D scans | FLAME | CC-BY-4.0 | RESEARCH 2066–2071 |
| Headbox for Rocketbox (Microsoft) | 15 visemes, 48 FACS, 30 Vive, 52 ARKit (`AK_01`–`AK_52`) on 115 low-poly avatars | artist | Rocketbox | Rocketbox repo MIT; Headbox repo: "we can't provide any particular license" (OpenFace, Oculus Lipsync deps) | [snippet] + GitHub API (no licence on `openVRlab/Headbox`) |
| Meta Movement (Quest) | 70 FACS expressions (`XrFaceExpression2FB`) + 15 visemes, reference images | — | no meshes on the page | not stated | [page] |
| Audio2Face Claire / Mark / James | ARKit-style solve targets | transfer + ROM capture + artist | NVIDIA's heads | sample-data licence: A2F project only, not production | [page] |
| FaceKeys (Superhive) | generates 52 ARKit on any head: 478 MediaPipe points → in-memory helper rig → posed shapes | procedural rig | any | code GPL-3.0+; $21.75 Full | [page] |
| Faceit (Superhive) | landmarks → rig → 52 ARKit from a preset | procedural rig | any | $78 ARKit / $99 unlimited | [snippet] |
| Polywink | automatic 52 ARKit service | — | any | 2018: $299 a model (commercial) | [snippet, 2018 CG Channel] |
| 3D Scan Store / Triplegangers expression scans | real expression scans (10K maps, ZBrush) | scans | per scan | paid: £29.99 each, £199.99 for 15 (3DSS); $14.99 each (Triplegangers); licences not read | [snippet] |
| D3DFACS | real FACS AU scans, 10 people | 4D scans | FLAME | non-commercial (testing only, downloaded) | RESEARCH 2077 |
| Research generators | USC ICT 2020 (personalised blendshapes + dynamic textures from one scan, 4,000-scan database); Neural Face Skinning 2025 (FACS-supervised, any mesh); NFR (MIT code, weights' licence unstated); RigAnyFace, OmniFaceRig, TopoRig (no code / academic) | learned | any | code not found except NFR | [page] abstracts |

Newer open sets (2024–2026) searched (§6 6, 10, 15, 36): nothing beyond GNM (2026) and MHR (2025) found — a gap in
the search. Neural Face Skinning (arXiv 2505.22416) and Netease's BSGen (IEEE VR 2023) are methods without found code.

## 3 · Gap 2 — expression wrinkle maps

**(i) Scanned maps.** No open, ship-able wrinkle-map set was found (searched §6 27, 28). FaceScape: displacement maps
for 20 expressions per person, "free for non-commercial research" [snippet, paper]; paid expression scans (3D Scan
Store, Triplegangers, prices in §2) bake into wrinkle maps — their licences for a shipped library are unread.

**(ii) Procedural / tension.** Raman et al. WACV 2023 + MIT add-on (finding 5); Blender Studio's Geometry-Nodes tension
(compression 1 − 2^(−A_def/A_base), directional stretch; "bump for the finest band only", quads only — earlier read);
Disney EG 2024's 4-bin shader for micro-wrinkles (finding 6); a stress-driven wrinkle patent (US 8,217,955, surface
normals perturbed by rest-to-pose stress) [snippet]; Larboulette & Cani 2004 and Reis 2008 (older) [snippet]. Blender
tools: Auto Wrinkle Map (extensions.blender.org, "wrinkle maps driven from bones in one click", GPL-3.0+, v0.0.7,
2025-06-25, 9,882 downloads; the user supplies the maps) [page]; the old Wrinkle modifier wiki (shape-key based)
[snippet]; WrinkleMatic (paid Maya deformer) [snippet].

**(iii) How the vendors make theirs.** MetaHuman: selected from 153 scanned characters, 3 animated normal + 3 animated
albedo variants, delta-encoded ("only store the difference between the base map", basecolour delta 512², normal delta
1K; off at LOD2 and at Medium/Low quality) [page + measured, finding 3]. CC5: per-actor preset sets of 5 source maps × 3
sets, region masks, Flow Map timing, "Overall Influence" and per-region strength and speed; wrinkles "generated by
specific expression sliders in the Edit Facial panel" [page, finding 4]. Both: a **library on a shared UV, chosen per
character, blended by rig-driven region masks**.

**(iv) Open per-character generators.** None found that makes wrinkle normal maps for a new face (§6 29, 31, 36). USC
ICT 2020 does it from one scan but released nothing found.

## 4 · Gap 3 — body correctives for any body from sliders

| Option | What | Licence (quoted) | Shape-aware? | Evidence |
|---|---|---|---|---|
| SOMA-X correctives | one MLP for all backends, distilled from MHR; Anny included | Apache-2.0 | rest shape only (Eq. 7: V_h(β) + f_MLP(θ)) | [page] |
| MHR correctives | per-joint MLP, 26,000 scans | Apache-2.0 | "independent from body shape" | [page] |
| Anny | MakeHuman mesh in PyTorch | code Apache-2.0, data CC0 | no correctives (none in README) | [code] |
| SMPL | learned pose blend shapes | commercial via Max Planck Innovation ("MI will now directly take over the licensing"); Meshcapade's table read garbled (~€41,400/yr commercial?) | no | [snippet] |
| STAR | sparse, local pose correctives conditioned on shape | "non-commercial scientific research"; bars training "for commercial use" | yes | [code] LICENSE |
| Neural Blend Shapes (SIGGRAPH 2021) | predicts rig, skinning, pose blend shapes for a new character | BSD-style ("Redistribution and use … permitted") | per character | [code]; trained on Mixamo (Mixamo's terms bar ML training — earlier) |
| MetaHuman body | parametric body editor applies "RBF correctives, pose-driver shape controls" | Epic | per body state | [code] `BodyShapeEditor.h` |
| Blender Studio Pose Shape Keys | store pose → sculpt → push to shape keys; auto drivers | GPL-3.0+, v1.1.1, Blender 5.0+ | hand-made | [page] |
| RBF Drivers | RBF-interpolated drivers for shape keys from bone poses | not on docs page; sold on ArtStation | hand-made | [page]/[snippet] |
| SHAPES (brave rabbit) | sculpt correctives in pose; RBF via RBF Nodes | paid | hand-made | [snippet] |
| Dem Bones | example meshes → LBS / helper bones | BSD-3-Clause | — | [code] |
| Corrective Smooth (Blender) | volume-preserving smoothing (what MPFB2 adds) | Blender | training-free | earlier [page] |

Practice (forums): fix weights first, add helper bones, then pose-driven correctives for extremes [snippet, §6 3].

## 5 · Gap 4 — how CC5 and MetaHuman give every character expressions and correctives

- **MetaHuman:** one fixed topology for every face; a new or conformed identity is rigged by a cloud service per
  character — Full Rig (joints + blend shapes) or Joints Only [page]; the method is unpublished. Mesh to MetaHuman
  "solves a set of MetaHuman face parameters that approximate the source" and Creator rebuilds the head [snippet,
  forum]. A UE 5.8.3 user report: "PCA-driven joints" misplace on a joints-only rig after a body refit [snippet].
  Wrinkle maps: library selection (finding 3). Body: correctives evaluated with the parametric body state [code].
- **CC5:** one fixed topology (CC base); expression morphs (262 in HD) plus 128 combination correctives; per character,
  Adjust Bones and the Facial Profile Editor fix artefacts by hand ("the issue should be automatically fixed up" once
  the corrective sliders are on, otherwise edit the mesh) [page]. How CC5 adapts expression deltas to a morphed head is
  not documented (see "Couldn't verify"). Wrinkles: per-actor presets (finding 4).
- **The published per-character methods:** deformation transfer (Sumner & Popović 2004; MIT ARKit implementation
  already found), example-based facial rigging (Li, Weise, Pauly 2010; MIT and unlicensed implementations), Audio2Face's
  transfer + ROM capture + artist refinement (finding 10), USC ICT 2020's learned personalisation (no code).

## 6 · Queries run and what they returned (WebSearch, standard mode unless noted)

1. "best open source facial blendshapes ARKit 52 realistic" — Fiverr gigs, FaceKeys, `digitalp/arkit-blendshape-tool`; noise.
2. "how to make wrinkle maps for facial expressions" — Microsoft DynamicWrinkles, PGS 2014 wrinkle extraction/transfer, Disney EG 2024, CC5 Face Tool and source-map pages, Jimenez 2011, Oat 2007, patent US 12062140, Unity Blacksmith.
3. "best way to make corrective blend shapes elbow shoulder" — forums: weights first, helper bones, PSD; no tools.
4. "NVIDIA Audio2Face blendshape solve ARKit template character mesh license" — A2F-3D paper 2508.16401, NVIDIA forum (46-shape template), NGC.
5. "is there anything better than ICT-FaceKit for blendshapes" — NVIDIA Maxine 3DMM appendix (modified ICT), ICT page; no comparison.
6. "open 3D face expression blendshape model scanned FACS commercial use 2025" — OpenFACS (2019), Surrey dynamic FACS model, BU-3DFE; no licences.
7. "Meta MHR facial expression blendshapes FACS quality" — MHR paper, Meta's 70 FACS expressions page, REFA; no benchmark.
8. "Audio2Face-3D example dataset Claire blendshapes huggingface license" — Claire dataset, MLX ports of Mark/James.
9. "Microsoft Rocketbox Headbox facial blendshapes ARKit FACS license" — Headbox counts, conflicting licence notes.
10. "automatic ARKit blendshapes generation from neutral face mesh paper code 2025 2026" — arXiv 2601.08234 (unread), Netease BSGen 2023, A2F blendshape generation.
11. "FACSHuman MakeHuman plugin facial action units license" — FACSHuman repos, MakeHuman-Additions.
12. "FACSHuman Gilbert 2021 Behavior Research Methods validation FACS coders AU recognition results" — abstract figures (Springer PDF needs sign-in).
13. "Polywink 52 ARKit blendshapes automatic price per character" — 2018 prices, freelance rates (€140 a set).
14. "Faceit Blender addon ARKit expressions how it works landmarks transfer price" — Superhive listing $78 / $99.
15. "new open source face model expression blendshapes released 2026 Apache MIT ARKit" — nothing new; Polywink "CC BY 4.0" blendshapes claim (snippet).
16. "MetaHuman animated wrinkle maps how generated custom character Mesh to MetaHuman animated maps" — forum posts, MetaWrap/MetaSculpt, CC's MetaHuman page.
17. "dev.epicgames.com MetaHuman Creator auto-rig "blend shapes" joints only rig generation identity" — `EMetaHumanRigType`, creating-a-character, stylized tutorial, UE 5.8.3 forum bug.
18. "MetaHuman face material animated maps wrinkle mask RigLogic head_cm1 head_wm1 documentation" — forum `MF_AnimatedMaps`, Poly Hammer terminology.
19. "MetaHuman how facial rig expressions are generated for new identity database of scans 3Lateral Mesh to MetaHuman cloud autorig" — 80.lv shaman case, Road to VR, 3D Scan Store pipeline; secondary only.
20. "MetaHuman 5.6 conform template mesh "auto-rig" cloud service expressions generated from neutral head" — from-template-mesh doc, Gigazine, KeenTools.
21. ""auto-rigging and texture synthesis" MetaHuman cloud service" — UE API request classes, a region-timeout forum report.
22. "Character Creator 5 manual facial expressions custom head morph adapt facial profile expression correction" — CC5 manual pages (Refining Expressions, HD profile, Facial Profile Editor).
23. "Character Creator 5 Expression Wrinkle System manual regions wrinkle sets driven by expression morph" — CC5 wrinkle chapter pages.
24. "pose space deformation corrective shape keys Blender add-on RBF drivers" — Pose Shape Keys, RBF Drivers, SHAPES.
25. "learned pose corrective blendshapes any body shape small neural network open source 2025" — STAR, SMPL, Neural Blend Shapes.
26. "SMPL pose blend shapes commercial license price Meshcapade" — Meshcapade licence page (garbled table), SMPL FAQ, Epic acquisition.
27. "FACS expression 3D scans pack buy wrinkle maps price 3D Scan Store Triplegangers" — £29.99 / £199.99; $14.99.
28. "free facial expression scan dataset displacement maps wrinkles license FaceScape Multiface" — FaceScape (non-commercial); Multiface not returned.
29. "Blender addon wrinkle maps shape keys tension free generate expression wrinkles" — Auto Wrinkle Map, Wrinkle modifier wiki, Blender Studio.
30. "real-time facial wrinkles from mesh strain paper procedural no wrinkle maps 2024 2025" — patent 8,217,955, Larboulette 2004, Reis 2008, WrinkleMatic.
31. "MetaHuman texture synthesis face texture index scans animated wrinkle maps generated per character" — `FMetaHumanFaceTextureSynthesizer`, skin material docs.
32. "ICT-FaceKit vs FLAME expression blendshapes comparison realism evaluation" — Neural Face Skinning 2025, NFR; no head-to-head.
33. "is there anything better than MakeHuman MPFB face units ARKit shape keys free realistic" — FaceKeys, MPFB2 issue 362.
34. "better than Meta MHR body model pose correctives open source 2026 comparison SMPL-X Anny SOMA" — Anny paper, SOMA; no benchmark.
35. "Epic Games acquires Meshcapade SMPL licensing Max Planck takes over 2026" — mpg.de (2026-02-18).
36. "dynamic expression wrinkles any face 2025 2026 paper code neural wrinkle normal map generation from blendshape" — USC ICT 2020 single-scan rig, patents.

GitHub API: `repos/<name>` for FACSHuman (×2), Headbox, Rocketbox, ICT-FaceKit, Audio2Face-3D (+SDK), MHR, Anny, SOMA-X,
STAR, neural-blend-shapes, dem-bones, mesh-tension, MetaHuman-DNA-Calibration; `search/repositories` "arkit blendshapes
in:name,description,readme" sorted by update (noise — narrowed), "facial blendshapes topic:blendshapes", "face rig
blendshape dataset" (0 hits), "ARKit blendshapes mesh" (by stars) — found Example-Based Facial Rigging (no licence),
`swnolan/dna_2_obj` (MIT), `JRicardoSan/Blender-ARKit-compatible-heads` (MIT, 2023).

Pages read: listed per fact above (Meta move-ref-blendshapes; HF Claire card; arXiv 2508.16401, 2004.03458 PDF,
2511.15586, 2603.16858, 2607.23687, 2505.22416, 2010.00560; DynamicWrinkles; CC5 wrinkle and profile pages; MetaHuman
materials, creating-a-character, from-template-mesh; UE API texture synthesizer; Poly Hammer terminology; Pose Shape
Keys page and extension; RBF Drivers docs; Auto Wrinkle Map extension; Disney EG 2024 PDF; Jimenez 2011 PDF; FaceKeys
docs and listing). Local reads: UE 5.8 MetaHuman plugin (`ts_params.json`, `texture_attributes.json`, two headers,
`MetaHumanCreatorBodyAPI.cpp` comments) — Epic code read for facts only, nothing copied; `F:\Reallusion Content` wrinkle
preset listing; one FACSHuman target downloaded to the scratchpad.

## 7 · Couldn't verify

- Any head-to-head realism comparison of open expression sets — none found.
- How the 53 released ICT shapes were made (README silent; the paper's "generic blendshapes" may or may not be them).
- FACSHuman's paper text (Springer sign-in): validation numbers are from the abstract snippet; its targets' quality on
  our render not looked at.
- How MetaHuman's cloud auto-rig computes per-identity blend shapes and joints; whether the cloud texture model is
  higher resolution than the local 1024 one.
- How CC5 adapts expression morph deltas to a morphed head (no manual page says).
- Licences of 3D Scan Store and Triplegangers expression scans for baking a shipped wrinkle library; Polywink's current
  price; RBF Drivers' licence and price; FaceScape's licence on its own page; Headbox's asset licence.
- SOMA-X correctives' numbers against plain LBS (the paper gives none); how well Anny's SOMA registration holds at the
  elbow and shoulder.
- arXiv 2601.08234 (mesh animation to blendshapes, 2026) — not read.
- Disney's EG 2024 / SGP 2023 and USC ICT 2020: no code found.

## 8 · Assessment — MY READING, not a decision (each attacked; for the user to approve or change)

1. **Expression shapes — score per shape, don't pick a set.** Candidates on hm08: Faceunits 01 (now), FACSHuman (no
   transfer), MHR's 72 and ICT's 53 (wrapped onto hm08), GNM's space (projected); the realism oracle is D3DFACS's real
   AU scans (local test only, licence allows testing) plus CC5 HD Aaron's same expressions, through the existing gate.
   *Attack:* no source ranks the sets, so a pick now would be a guess; MHR has no mouth interior or eyeballs, so tongue
   and lid–eyeball contact come from elsewhere (GNM tongue, our eye clearance); mixing sources per shape risks combos
   that disagree — the DNA's corrective (PSD) layer is where combos get fixed. *What it changed:* from "MHR first" to
   "measure all, pick per shape".
2. **Wrinkles — keep RigLogic's animated maps (approved), 3 maps like MetaHuman, and compute the mask weights from mesh
   tension offline.** For each expression shape, the tension map on our mesh (Raman's edge-length measure, MIT code)
   says which region compresses and by how much — that fills the DNA's conditional table automatically instead of by
   hand. Map content: no open scanned library exists; first our own sculpted/baked folds per region, then (if their
   licence allows shipping) paid expression scans baked to our UV — the vendors' library route. Micro-wrinkles under
   stretch: Disney's 4-bin shader is a different job (pore-scale detail) and can sit in the skin shader.
   *Attack:* tension at runtime would be a second driver beside RigLogic ("one way per job") and wouldn't export to
   Unreal or glTF — so tension only authors the weights; a library of one or two wrinkle sets is far below MetaHuman's
   153 — the gap stays until a ship-able scan source is found. *What it changed:* tension moved from runtime driver to
   authoring tool.
3. **Body correctives — SOMA-X's distilled correctives, mapped to hm08 through Anny's SOMA correspondence, baked into
   the DNA's RBF layer (approved) by sampling poses per joint; Pose Shape Keys (GPL) for hand fixes only.** Measure first
   at the joints SOMA names (elbow > 120°, shoulder abduction > 90°) against plain LBS and HD Aaron in the same pose.
   *Attack:* the MLP's input is SOMA's 77-joint rig — our UE5-named rig needs a rotation map; an RBF bake approximates
   the MLP; correctives are shape-independent (MHR says so), so heavy or very muscular slider bodies get average folds —
   STAR's shape-conditioned method is published but its model is non-commercial, and we have no scans to train one;
   simpler Corrective Smooth keeps volume but adds no muscle bulge. *What it changed:* "measure before bake" added.
4. **Per-character adaptation — measure before building.** All our identities share hm08, so expression deltas carry
   over as CC5's do; apply them on extreme slider identities (thin/full lips, age 90, child) and check lip seal and lid
   contact; only if they fail, add deformation transfer from the average head per identity (MIT implementation exists).
   *Attack:* MetaHuman re-solves per identity in the cloud — a delta copy may be visibly worse on extremes; but no open
   per-identity solver with code exists beyond DT/example-based rigging, and DT on every slider change costs a solve.
   *What it changed:* nothing.
