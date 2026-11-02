# Scan skin base — the working doc (read this FIRST after any compaction)

> Kept current at every step (the user, 2026-11-02: "you need to save a doc with what yo are doing so after each
> compact you dont get lost" … "this is already rule"). Sections: the job, the user's words, where things stand, the
> method picks with their sources, mistakes not to repeat, next steps. Research evidence lives in
> `2026-11-02-research-texture-source.md`; decisions verbatim in `../dev/TASKS.md` ("THE SKIN'S SOURCE", ~line 896).

## 1 · The job

Give every character a real-skin base for the whole head (scalp, neck, ears, under the face) built from several real
scans — never one scanned person copied. The face itself comes from the character's own painting (Headshot 3's
structure: one photo projected + a skin base, merged by masks). Per character: the scans' layers mixed, plus its own
tone, age, mottling, redness, freckles, moles, stubble.

## 2 · The user's words that govern it (verbatim, 2026-11-02)

- "your rec on all go" — on: (1) Headshot's structure, (2) the skin-base builder, (3) Nano Banana only if needed.
- The NOT STANDARD word for the builder: "you can do non stnadar if you cant get standard to work …"
- Variety: "we have to be able to make any human look real they cant keep looking like the same character or base, it
  has to be completelety adjustable like methuman … if all chracters looks the same but with is slightly differnt skin
  tone that is not acceptable".
- Scan hunt: "make sure you find the best sites to search, go".
- Then "stop", and: "you need to think on the best mthodes … be consistant, think adversirally … pick the right tools
  solluitions and save that info … make sure you chekc you exisitn research". NO GO for building since that stop.

## 3 · Where things stand (update at every step)

**2026-11-02 evening — STOPPED by the user; no building until the word "go".** Done since the stop: research gap F
(saved), the picks in §4 attacked (§4b), the rec list shown in chat. WAITING for the user's go on that list.

Done and kept:
- Scans downloaded (Sketchfab, CC Attribution, licences read from `/v3/models/{uid}`), each in
  `.dev/downloads/scans/<name>/` (zip + `x/` unpacked; nested RAR/ZIP unpacked to `x/src/` with 7-Zip).
- Checked at 1:1 (contact sheet + skin windows; scripts in the job tmp dir, not kept):
  KEEP — yaro13 (older man, 8K), rudavin (younger man, 8K), female_whynotmeebaby (woman, real pores, 4K), head03a (young
  woman, smooth, 3×4K), ammamma (elderly woman, 4K), portrait_3130 (woman, 8K), d3d_african_woman (dark skin, pores,
  8K body), d3d_african_man (dark skin, softer, 8K body), rp_carla (medium-olive, 8K body); plus scan02 and lps already
  in use. WEAK — d3d_bodysuit_woman (blurry), jared (beard, low-res). OUT — eddy, joan, red_lady, kitbash_self,
  leo_paul, asian_woman, john_cleaver, tony_hodges, rp_fabienne (reasons in the research file's table).
- Code from before the stop (committed 9d3ee4b): `tools/face_test/scan_base.py` (scan02 / lps / marcus: eyes or
  skull-breadth alignment, ICP, Amberg NICP, closest-point texel copy), `skin_base.py` (layer split + compose),
  `test_face_export_head.py`.
- Written after, NOT run, NOT committed: `tools/face_test/scan_convert.py` (Blender importers → arrays).

The research file now holds both download batches and the skin/hair research. Open, not this job: the approved
MediaPipe-vs-RealDenseFace painting-warp test (TASKS ~585) never ran.

## 4 · Method picks, job by job (recs — each waits for the user's go)

Coverage map: what our research already says, where, and whether our code followed it.

| Job | Our research says (file:line) | Our code did | Pick |
|---|---|---|---|
| A. Read FBX/OBJ/GLB | Blender is the platform | trimesh (no FBX) | Blender's importers (`scan_convert.py`) |
| B. Point pairs scan ↔ our head | Wrap: SelectPointPairs first; MetaHuman From Mesh: markers on a near-flat, unlit render of the textured mesh, frontal frame (`2026-10-30-research-ai-photo-to-head.md:211,214`); dense UV correspondence ranks first, MediaPipe "weak as the only shape signal" (same file §1 point 5, §2.1, §5); RealDenseFace measured here, reads our renders (`RESEARCH.md:1653,1696`); MediaPipe on clay "guesses" — brows 9-11 px (`TASKS.md:615`) | eyes (scan02) or skull breadth + crown — fails with hair | RealDenseFace's 5,023 FLAME points on an unlit near-flat render of the scan and of OUR TEXTURED head (both photo-like), inner-face masks only, weighted by its confidence; MediaPipe only to find which way the scan faces and the face box |
| C. Rigid + scale | Wrap: rigid from the pairs | ICP with scale | weighted similarity from the pairs (trimesh `registration.procrustes`, scale on), then the wrap |
| D. Non-rigid wrap | trimesh Amberg NICP = our standard (`libs/wrap/gnm_to_hm08.py:143`); Wrap's wrap is "guided by the pairs" | NICP without landmarks | `nricp_amberg` WITH the pairs (`source_landmarks` as triangle + barycentric on our head, `target_positions` on the scan); the scan cropped to the head; memory sized first (the Marcus run reached 38 GB) |
| E. Texture onto our UV | Blender Cycles bake "Selected to Active" — "how a texture made on another topology (… a scan) moves onto hm08's UVs once the two heads are aligned" (`2026-10-30-research-ai-texturing.md:437-442`, manual read) | hand-written closest-point copy (NOT STANDARD, unflagged) | the bake: scan selected, our fitted head active, emission of the scan's colour, cage / max ray distance; a white-emission bake gives the coverage |
| F. Skin vs hair, brows, beard, clothes | researched 2026-11-02 (`2026-11-02-research-texture-source.md`, "Telling skin from hair"): Pixels2Points does it on the scan mesh but has no code or weights; its training-free baseline is multi-view 2D parsing lifted onto the mesh; SegFace best measured (88.96 / 93.03 F1), code + weights MIT, trained on CelebAMask-HQ (NC data, label); full beards = hair there; the industry masks by hand | none | SegFace on unlit renders of the scan from the views where a face shows, labels voted onto the scan's vertices, baked into our UV with the colour → a skin mask; bald scans (scan02) keep their scalp by a per-scan flag, since a parser may call a bald crown "hair". NOT STANDARD (the voting is our code of a published baseline; the standard is a hand mask) |
| G. Layers + per-character mix | MetaHuman SELECTS its scanned HF maps from an index (`2026-10-30-research-comfyui-flame.md:177`); Texturing.xyz keeps broad/mid/fine as separate channels with separate strengths (`2026-10-30-research-skin-detail-shading.md:226-229`); a MetaHuman-albedo pipeline: low-pass → PCA basis (comfyui-flame:189) | `skin_base.compose` AVERAGES all scans' fine layers by random weights (pores of several people at one texel cancel ~1/√n) | fine layer SELECTED from one scan per character (MetaHuman's way), mid mixed from 2-3, tone from our skin colour model |
| H. Light baked in the scans | delight research (SH fit) | band split drops the low band | keep: the low band (> ~8 mm) is dropped, so broad light goes with it |
| I. Feature-level refine | Wrap's OpticalFlowWrapping (photo-to-head:214) | none | only if B-D leave the scan's features > ~2 mm off ours (measured) |

## 4b · The attack on each pick (what it changed)

- B, RealDenseFace pairs: consistent with `flame_fit.py`'s reasoning (the same network on both pictures, so its own
  leanings cancel). Attack: it was measured on clay and paintings, and MediaPipe/RealDenseFace guess worse on clay →
  CHANGED: our head's side is a render of our TEXTURED head (photo-like), not the clay. It needs a face box: MediaPipe on
  the render (its weak spot is fine points, not finding a face). Full-body scans: render only the top of the mesh so
  the face fills the picture. Unknown facing: 8 turns rendered, the frontal one kept. Licence: weights trained on
  Ava-256 (CC BY-NC) - a label; used offline to line scans up. Simpler options: hand-clicked pairs (Wrap) - not
  automatic for 11 scans; skull breadth - already failed on hair.
- C, `procrustes`: trimesh's own weighted similarity - nothing simpler.
- D, wrap with pairs: our standard (`gnm_to_hm08.py`) plus the pairs Wrap uses. Attack: hair can pull our scalp outward
  → the distance threshold kept to ~1 cm and hair masked out by F anyway. Memory: the scan cropped to the head and RAM
  watched on scan02 first (the Marcus run's 38 GB).
- E, Blender bake: heavier to set up than the numpy copy that already works (scan02 0.1% black), but it is the documented
  standard our research named, and it handles seams, filtering and margins the copy patches by hand. Kept; the coverage
  comes from a white-emission bake with the same ray distance (~5 mm).
- F, SegFace voting: attack - a parser may call a bald crown hair (scan02's scalp is our main scalp source) → CHANGED:
  per-scan bald flag; votes only from views where a face is found plus the back views for hair. Simpler: a skin-colour
  model seeded from the cheeks - fails on grey hair over light skin and brown hair over tan skin (yaro13, head03a).
- G, select the fine layer: attack - one scan's pores repeat across characters → 11 scans to choose from, mixed mid
  layers and each character's own marks; MetaHuman's index is also a finite set. Kept.
- I, optical-flow refine: only if measured misplacement > ~2 mm after D.

## 5 · Mistakes not to repeat

- Building before reading our own research for the job (B, E above were researched; I hand-rolled both).
- Switching tools between tries (MediaPipe → RealDenseFace) without writing why; every pick is written in §4 first.
- TaskStop leaves the child process: list processes after any stop (the Marcus fit grew to 38 GB, killed JustDirect's
  clip). Size heavy jobs first; tell web-4c / web-9e before card or heavy RAM use.
- Repo tests: always `-k`; the bare suite starts the Blender suite and an sd-server.
- Chrome blocks repeated downloads per site until "Always allow" (now allowed for sketchfab.com).

## 6 · Next steps (in order)

1. Research F (skin / hair masks) the user's way; log the queries in the research file.
2. Attack every pick in §4, then show one numbered rec list in chat; wait for "go".
3. On go: run `scan_convert.py` on scan02 first, rebuild the fit by §4, check it against the old fit (median 1.2 mm),
   then the keepers one by one; record each result here and in the research file.
