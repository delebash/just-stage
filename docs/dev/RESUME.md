# Resume — what to read before working (after every compaction, on "re-read docs", at every session start)

The user, 2026-11-05: "so every time i tell you to re read docs, what does that mean to you ... you should knoww the
doncs you need to re read"; "fix it keep things current do not really on compaction". A SessionStart hook
(`.claude/settings.json` → `tools/resume_hook.py`) puts this file into the session at every start, after a compaction
too. **Rule: before any tool call, read the "Always" list and every file listed for the active job — in full where
marked. A compaction summary is never a substitute: what it says is checked against these files.** This file is
updated in the same commit that starts, changes or ends a job, and its "Where it stands" after every step.

## THE ONE PRIORITY - read first, every time (the user, 2026-11-05; memory `one-priority`, TASKS "THE ONE PRIORITY")

**Prove CC5 (HD Aaron) quality on every body part, and that it holds for any custom character - or prove a part can't
and change the approach. Nothing else.** Every step must prove or disprove a part; library builds, credits, tooling
polish and side fixes only when a proof needs them. Proof = ours beside Aaron at the gate's views (`tools/gate/
parts_gate.py`), equal or above, measured; then the same method, no per-character tuning, on 4+ different characters.
Order, riskiest first: (1) face mid-scale relief (scan geometry -> normal maps) -> (2) body relief -> (3) scalp hair
(groom vs shading) -> (4) eyes -> (5) smile shapes -> (6) the rest -> (7) multi-character run + full gate. Report per
part: proved / not proved / disproved. **2026-11-06: entries (1), (1b), (4b), (4c) and the brows / lashes judgments
were measured on skins with painted hair (lashes, brows, stubble) and a pore tile that may carry stubble - VOID until
re-measured on clean inputs (RESEARCH "Painted hair in our inputs"; the active job above).** Proof log (`.dev/gate/parts/proof1/`, bands = fine / pore / fold, L* std,
`scratchpad bands.py` windows: forehead 0.02-0.25 x 0.3-0.75 of the eye view, cheek 0.25-0.6 of the cheek view):
- (1) face skin, one character (Average man, composed 632 = HSR0040 + LPS colour and relief): cheek 0.42/0.97/0.72 vs
  Aaron 0.45/0.96/0.79 = EQUAL; forehead 0.96/0.91/0.57 vs 1.73/1.74/0.92, by eye close (his glossier). Made by: pore
  relief 1.0 / 0.3 mm + per-pore shine, region factors (`tools/make_face_regions.py`: forehead pores x2, micro x5),
  the scans' geometry relief (`scan_bake.py NAME normal`, `skin_base._relief`). Scan colour alone = 0.40 pore band
  (Aaron without normals: 0.40) - pores are relief. NEXT: the same on 4 characters (scan relief bakes for hsr0027
  0028 0015 0042 0081 0102), then step (2) body relief. Seen: at face distance the gap is now shape (MakeHuman
  proportions, HSR0040's heavy bags), tone, hair - not texture.
- (1b) face skin on 6 characters (library men and women, light to dark, the six "Scan" skins with relief,
  `.dev/gate/parts/proof_chars/`): cheek pore band 0.97-2.18 (Aaron 0.96) - HOLDS for any character; forehead men
  55-70% of Aaron's, dark woman equal, young women lower (smoother, as real). Defect: a scar-like mark on Scan woman
  B's cheek (HSR0028's). NEW RISK found: face SHAPE - MakeHuman's faces read generic and puffy round the eyes beside
  Aaron's; testing a real face shape (a scan's fit in our topology) on the same skin next.
- (1c) face shape: HSR0040's real face (his fit in our topology as a shape key, `.dev/gate/parts/proof_shape/`) on the
  same skin reads no more like Aaron than MakeHuman's - shape is NOT the main gap. Tone is: melanin 0.07 overshoots
  (face L* 40 vs Aaron 48.5; a*/b* match), ~0.045 should match - a per-character choice. Sheen (roughness x0.8): no
  visible change. THE EYES are now the main face-distance gap (`.dev/gate/parts/proof_eyes/`): ours meet the eyeball
  at a sharp lid edge with no margin, no pink wet rim, lashes thin, white flat, pupil small; Aaron's lids have a thick
  wet pink margin wrapping the eyeball, lashes on it, a larger pupil, a lighter iris. Pupil 0.38 / white x0.85 /
  today's lashes: barely visible change (the pupil may be GNM's pupil-disc geometry - check). NEXT: the eye region
  (step 4 moved up): lid margin (geometry thickness + a wet pink rim by MPFB2's `mpfb_eyelids` mask?), tearline,
  pupil, iris; then the library characters rebuilt with today's lashes, brows, eyes open, scan skins.
- (4) eyes, measured (`.dev/gate/parts/proof_eyes/`, scratchpad `eye_exp3.py`): our white L* 80 vs Aaron's ~48-60 -
  his sits in the lids' shadow (CC5's occlusion); ours uniform. Our occlusion film (eyeshell) darkens nothing in EEVEE
  (hidden or not: same) - a fault to fix first. The pupil is GNM's 2.7 mm pupil-disc geometry (the shader's
  PupilSize 0.082 -> 0.15 changed nothing). Cornea reflection x0.3: no change. Lashes: radius 0.08 mm, 180 upper,
  melanin 1.0 give a visible lash line at face distance (adopt). Amber iris overshot to yellow.
  FOUND: the occlusion film (eyeshell, rendered solid red: `proof_eyes/eevee_eye_ours_shellred.png`) does not fit the
  opened eye - a lens in the middle of the opening, strips under the upper lid and above the lower one uncovered, so
  its lid-edge darkening lands inside the opening. FIXED in code: `eye_layers.refit` finds the lids again (test
  `test_they_follow_the_lids_when_the_eyes_open`).
- (4b) eyes on one character (Average man, Scan man A skin; scratchpad harness `eye_photo.py`, options per factor;
  `.dev/gate/parts/proof_eyes/`, crops beside Aaron's eye view; measures: white L* inside the opening found by a red
  film render, iris annulus Lab, a vertical L*a*b* profile under the iris). Each against Aaron:
  white x0.71 (warm R x1.05) L* 67.5 vs 68.3 = EQUAL; a polar-unwrapped iris PHOTO (`.dev/downloads/other_samples/
  commons_green_iris`, recoloured by its lightness to albedo 0.053/0.030/0.021, structure ^0.7) L* 24.6 C 14.8 vs
  27.2 / 11.3, detail bands 1.9/3.5/4.2 vs 1.1/2.6/3.9 = EQUAL (its light collarette ring is this photo's; brown photos
  are content); the iris' own specular 0 (the cornea shell glosses - at 0.5 a grey haze sat on the pupil); pupil 0.45
  of the iris vs his 0.49 (a parameter; the procedural eye's PupilSize did nothing); the lid MARGIN: our lower lid's
  edge stands up to 3.3 mm off the eyeball (a dark crevice, L* 21) - sealing the one vertex ring onto the eyeball left
  a 4-8 px band (MakeHuman's lid has no margin geometry); the TEARLINE strip (ICT's ring, eyeEdge) shaded as wet pink
  tissue (0.50/0.22/0.20, roughness 0.15, coat 0.6) gives a 32 px band L* 60-72 a* 12-18 vs his ~36 px L* 65-72 a*
  10-19 = EQUAL. Thick lashes (radius 0.08 mm, 180 upper, melanin 1.0) make the lash line. Not done: caruncle (a
  geometry mask at the inner corner barely shows), veins (invisible at face distance). Shape: MakeHuman's own sliders
  (bag -1, eyefold concave -0.7 / up 0.6, height1 +0.6) open the eye (9.7 -> 10.7 mm at the iris, iris covered 12.8 ->
  9.7 deg) - a per-character choice. Seen at face distance and NOT eye parts: our skin round the eyes reads rougher
  and far paler and less red than his (lid L* 80 a* 5 vs 60 a* 19) - recheck the skin proof (1) there.
- (4c) the same settings on four library characters (own skins, no tuning; `proof_eyes/*multiphotolashocctearpink*`):
  iris, white, pupil hold; the pink tearline strip DISPROVED as made - it outlines the whole opening (a drawn pink ring,
  worst on dark skin). Pink on the lower lid's part only, fading at the corners, the upper part the clear tear film
  (`*multi2*lowonly*`, five characters): a wet waterline on all five, no ring; darkened by the character's own melanin
  (x(1 - 0.7 min(m/0.25, 1)) toward 0.20/0.08/0.06 - conjunctival melanosis; `*multi3*`). The strip's inner end as the
  caruncle: hidden under the corner skin (failed). The caruncle as the corner skin painted wet pink (0.45/0.18/0.16,
  geometry mask past the inner corner, scratchpad `lid_margin_mask.py mode=caruncle`): shows, as on Aaron. Seen: our
  default opening shows white below the iris (scleral show - a stare), Aaron's lower lid meets the iris: shape, per
  character. Final run of every piece on five characters: `*final*`. EYES: equal by measure at face distance on one
  character, the pieces hold on five; at close-up still below (flat white without veins or soft shading; the photo is a
  hazel eye recoloured - a light collarette ring; brown photos are content). Adoption into code waits for the user's go
  (the list in the session report, 2026-11-05).
- (2) body, started (`.dev/gate/parts/proof_body/`; RESEARCH "Body relief and muscle definition"): MakeHuman's muscle
  gives bulk, not definition (Muscular man vs Aaron); a texture-tile seam across the chest and arms on two characters
  (to diagnose); no bare athletic torso among our downloads (HSRD bodies clothed but HSR0042-Body-045; deep3dstudio's
  athletic man in a tank top; Ten24 in a sweater). Triplegangers' free full-body sample (the user's link): athletic, in
  underwear, CC BY-NC-ND - a LOCAL test source only, behind a registration the user must do.
- (2b) the user's links, the user: "i want you to download all these ones i am giving you yes downloade dthem":
  Artec 3D "Body scan" DOWNLOADED (`.dev/downloads/artec_body_scan/`, 60.5 MB; its `license.txt`: CC BY 3.0 Unported,
  "Body scan by Artec 3D"; 765k triangles, 8K colour, no normal map; a lean athletic man, arms raised). Triplegangers
  needs the user's registration; Digital Reality Lab's form (name, email, company, use) mails the link to the user.
  Measured (scratchpad `scan_torso2.py`, the torso framed as Aaron's; bands fine/pore/fold/form at 1024 px, form =
  12-48 px = the muscles): ours 0.31/0.18/0.38/2.27, Muscular man 2.00/0.88/0.53/2.76, the Artec scan as scanned
  0.27/0.40/0.71/3.12, Aaron 0.86/0.67/1.23/4.34 - the scan carries real definition (72% of Aaron's form band; his
  is a sculpted glossier physique), its fine/pore come from our layers. The chest SEAM (`proof_body/*nonormal*`,
  `*flatcolour*`): COLOUR - the head tile's painted colour ends at the upper chest against the torso tile's, plus
  a dark line from the colour map's unpadded island edge; normals cut: no change. NEXT: fit the Artec torso to our
  body and bake its relief into our UVs (the face route on the torso), apply to two body types, measure; the seam
  fix (pad the islands, blend the head tile into the torso tile at the border).

## Always

- `AGENTS.md` and `CLAUDE.md` (loaded automatically), `docs/dev/README.md` (the doc map: TASKS, RESEARCH, IDEAS,
  PRD, ARCHITECTURE, `docs/standards/` — the standards govern; TASKS records the user's decisions verbatim).
- `docs/standards/README.md` §1 (which standard covers what) and §3 (one way per job): **a job's governing standard
  is read before its plan** (the user, 2026-11-05: "it was already part of the standard to match each part").
- Memory: the index (loaded automatically) and `search-mistakes` before any search, rec or plan.

## Active job (NOW, 2026-11-06, from ~13:00) — THE DEEP READ, THEN ONE PLAN (TASKS, the first entry - read it)

The user stopped app work to fix how I work: every doc read in full by job, the real gaps researched, one plan doc
(the final best method per part) worked from, RESEARCH made an index. **Read first:** TASKS "THE DEEP READ, THEN ONE
PLAN" (the approved rec, verbatim) and `.dev/audit/2026-11-06/CHECKLIST.md`. **State:** ten readers launched ~13:00
(G1-G8 every doc by topic, G9 / G10 second reads of skin+body and eyes+lids+lashes+brows+hair), reports to
`.dev/audit/2026-11-06/G<n>.md`. **Next:** check each report's coverage proof and tick the checklist; build the
coverage table (job -> methods, evidence, decisions, code follows?); re-read every cited source passage of each job's
final method myself; read each job's code modules whole; then gaps -> plan -> RESEARCH index. TASKS' reshaping waits
for the user. App work paused except run 11's check (`.dev/gate/parts/2026-11-06k`: hands, nails, feet from the
HSR0042 / Anny fit - not yet looked at).

## Previous job (2026-11-06 morning) — THE INPUTS FIRST: every input of the character audited against CC5's way, fixed, then re-measured

The user, 2026-11-06 (TASKS "THE INPUTS FIRST"): our skins carry painted hair (lashes, brows, stubble) and the proofs
were measured on them - "you a doing wrong things testing with wrong things ... check again if you are doing things
wrong like this"; "update the docs and fix all of this". Memory `audit-inputs-before-measuring`.
- **Read in full:** `docs/plans/2026-11-06-inputs-audit.md` (every input: source, CC5's way, checked how, verdict,
  fix) and RESEARCH "Painted hair in our inputs" (what is void, what stands).
- **Void until re-measured on clean inputs:** proof (1) face skin, (1b) six characters, the brows (rec 8) and lashes
  judgments, (4b)/(4c) the lower-lid wet margin and caruncle, the lid band of build step 1. **Stand:** iris, white,
  pupil; geometry (lid anatomy, the sweep, the recess); the gate's tooling; the live view's calibration.
- **Base v2's code, built 2026-11-06 (uncommitted at the time of writing, tests green):** `core/makehuman.py`
  (`skin_mask`, `Appended`, `extend_offsets`; `tests/unit/test_base_v2.py`), `modules/body/base.py` (`upgrade`: the
  cut after the UDIM layout, every key placed by its faces; `extend` in every target reader), `tools/make_base_v2.py`
  (`data/generated/base/v2.json`: rings 36 + 36, 128 vertices appended, 70 rows), `head/parts.py`
  `eyelid_contact` (rim 0.25 mm, lash line >= 1.0 mm, margin midway; 68 eye targets green),
  `tests/blender/test_base_v2.py` (4 green). Open in step 1: the upper lid's recess (measure ours by the scans'
  method first), the library migration with groom re-binding, the margin's tint in the skin material, the gate's band
  - on clean inputs.
- **Done 2026-11-06 (fix order 1-2 of the audit, each committed):** hair out of the skins (`tools/face_test/hair.py`:
  DullRazor strands + mirror fill; `skin_base.py`: the eye/brow band, strands in the eye zone and by the hairline,
  stubble found per texel, stubbled scans out of the beard, a faint shaved tint, holes filled with skin, smooth colour
  fill); the clean pore tile (Ten24's cheek relief, `pore_tile.py`, shared by every skin via `maps.pore_relief`); a
  stubble groom (`hair/stubble.py`, the library's "JustStage stubble", the gate's man wears it); the margin's tint in
  the skin (`maps._margin_layer`); the photo iris in code (`tools/make_iris.py`, `eyes.shade`); migrations
  (`juststage/migrations/`: v1 -> v2 on load and library add, grooms put back, our lashes re-made); defaults and the
  library's characters on the scan skins; the gate's man = Average man (Scan man A). The upper lid's move dropped
  (measured the scans' way: already real). ALSO DONE: the six scan skins rebuilt (`tools/rebuild_scan_skins.py`;
  stubble found per texel), the men with Artec's torso (`tools/body_scan.py`: wrapped, baked, hair out - rows 10/15);
  teeth and gums shaded from the MIO photo (row 13); lashes rooted on base v2's lash line; the library's hair and
  characters rebuilt on base v2 (backup `.dev/backup/library_2026-11-06/`).

- **Gate runs 1-10 on clean inputs (2026-11-06, `docs/gate/2026-11-06/report.md` - every finding, its measure and its
  fix, run by run; scratchpad `factors.py` renders one factor at a time, `show-<node>` a node's value as emission).**
  Fixed and committed: the head normals' false shading (Cycles' bake vs shape keys); the relief's size by UV density;
  the 3D border blend; relief holes flat; relief debris dropped; the neck is body skin (region map + `face_share.png` -
  never data in alpha); stubble as Aaron's (neckline, fine, dense, flowing); brows (grey only where a character greys);
  the lid margin capped at 2.6 mm; sclera veins (rec 12) where the white shows; an additive tear film; lips; the
  wet layers' coat; no pores on nails; the gate man's hair colour. Run 10 (`.dev/gate/parts/2026-11-06j`): face, front,
  neck, torso clean on all five characters.
- **NEXT (in order):** (1) hands and feet - flat beside HD Aaron's veins, tendons, knuckle creases (run 4's hand and
  foot views): extend `tools/body_scan.py` from the torso to tiles 1003 / 1004 from HSRD-100's HSR0042-Body-045
  (`.dev/downloads/hsrd100/`, bare but for trunks and cap, near A-pose, barefoot - arms ~20 deg out against our ~45:
  per-limb rigid alignment before the wrap; mask the trunks and cap; hair out). Built: `body_scan.py` takes a SOURCE
  (`hsr0042`); export done; legs place within 11-14 mm; arms failed twice (a turn at the shoulder: 8 cm off - our
  A-pose bends the forearm 19 cm forward, the scan's hangs straight); a joint-by-joint pose search is the third try -
  if the arms aren't within ~1 cm, switch to Anny (RESEARCH: NAVER's differentiable MakeHuman, torch is in venv-rdf)
  instead of tuning further (the user, 2026-11-06: "should look for another method?"); (2) rebuild the library's hair and
  characters (brows' grey) and re-run the gate with hand, nails, foot, ear views; (3) the eye: lower margin still a
  glossy roll, the tear film's band; (4) torso definition, face shape (step 4), hair style; (5) the full suites once
  at the end (known failing: test_ai_jobs' sd-server, test_body's face count and BASE_VERSION).

## Active job 0 (before the inputs audit) — the whole character redesigned, base mesh first

The user, 2026-11-05 late (TASKS "THE BASE MESH FIRST; THE WHOLE CHARACTER REDESIGNED"): rethink every piece - mesh,
parts, UVs, sliders, HD detail, face rig, expressions, skin, hair, materials, live view - against CC5 and MetaHuman
("better than both"), in adversarial passes, before Phase 2 builds anything; the append onto hm08 (NOT STANDARD) is
approved only if no better way is found.
- **Read in full:** `docs/plans/2026-11-05-base-mesh-first.md` (the plan: audit -> base -> sliders -> rig ->
  texturing; the best-of-both table), `docs/plans/2026-11-05-research-base-mesh.md` (Blender's CC0 realistic head models
  the lid margin and caruncle; MakeHuman's proxy system), `docs/standards/character-data-model.md` (whole - §1.1 already
  names Blender's CC0 base meshes as the FALLBACK BASE, sliders moved by wrapping, CharMorph's alternative-topology
  transfer as the code reference; topology frozen behind `baseVersion` + a vertex map), `skeleton-and-face.md` §2.
- **Measured so far:** hm08 lid edge one ring, up to 3.3 mm off the eyeball; CC5's HD Aaron (SubD 1 export, 56,412 body
  vertices) models a thick upper-lid margin and a lower-lid ledge (`.dev/gate/parts/audit/sheet_eye.png`,
  `sheet_mouth.png` - his wireframe didn't render yet); CC5 base 17,683 polygons at SubD 0; MetaHuman head LOD0 24,000
  vertices, 669 blend shapes, 713 joints; hm08 14,766 faces, head tile 4,986 vertices.
- **2026-11-05 late: DESIGN APPROVED ("your rec go on all", TASKS); build step 1, the lids, in progress** - the prototype (scratchpad `lid_proto.py`; measurements in `docs/plans/2026-11-05-research-base-mesh.md` §7): the lid-edge loop found (closed at threshold 0, a branch to trim), a loop cut each side (88 vertices appended, indices kept, 60 keys carried), shaped to lash line 2.0 / margin 1.1 / eyeball rim 0.25 mm; the blink's 2 mm gap is MakeHuman's blink shape (same on the original mesh) - step 3. DONE: on the library man (scratchpad `lidlib.py`, `lid_gate.py`) the margin band is in Aaron's range (28-50 px vs 26-63 px, a* 9-14 vs 12-14); tilting rejected; grooms re-made on the new topology. DONE also: the eye-slider sweep (20 of 66 targets clip the rim, 4 lift it -> the contact step runs on every refit, design changed) and the recess (real scans: the upper lid's front ~2.9 mm ahead of the cornea, ours 1.0 -> the upper lid ~2 mm forward in the base shape). NEXT: the production code - base v2 (appended loops with face-frame data in the target files), the refit contact key, the upper-lid recess, tests over all 66 eye targets, the vertex map, the library migration (backup first), groom re-binding (research file §7). Anny's README read (RESEARCH): its `makehuman` topology may be a differentiable copy of hm08 - check, then use it for scan fitting.
- **2026-11-05 late: the design is written and attacked in seven passes** - `docs/plans/2026-11-05-character-design.md` (base: hm08 kept + appended lid anatomy with face-frame transfer and a contact step; the lids measured as the one topology gap; parts, seam-continuous textures, sliders + mixer, scored expression sets, tension-driven wrinkles, SOMA-X correctives, hair live-view techniques; build order) and three audited research files (`2026-11-05-research-base-mesh-2.md`, `-face-animation.md`, `-mixing-hair.md`). WAITING for the user's approval of the design before build step 1.
- **Next:** the design document (`docs/plans/2026-11-05-character-design.md`): per piece CC5's way, MetaHuman's way,
  ours, the best, its standard, its attack; research only the verified gaps (rule 0 coverage map first); the audit
  sheets (eye, mouth, nose, ears, hands, feet, torso, joints, expressions) for ours / Aaron / Blender's CC0 / MetaHuman.

## Active job 1 — the quality bar: every body part at or above CC5's HD Aaron

- **The standard — read in full:** `docs/standards/quality-gate.md` (the gate: a CC5 HD character exported by the
  user; one JustStage head with every part; front, three-quarter, profile, eye and lip-corner close-ups; neutral +
  `jawOpen`, `mouthSmileLeft`+`Right`, `browInnerUp`; contact sheets part by part; "passes when no part is below";
  the report in `docs/gate/<date>/report.md`).
- **The bar — read:** `docs/plans/2026-11-04-realism-review-brief.md` §1 (the nine parts: skin of face, body, hands
  and feet; scalp hair; facial hair; brows and lashes; body hair; eyes; mouth - teeth, gums, tongue; nails, finger
  and toe; nipples, lips, ears) and the user's words 2026-11-05: "hd arron is the highest res cc5 character and that
  should be the bar"; "it has to be all parts of body meat quality bar not just skin"; "toe nails too, all body
  parts".
- **The plan and its order — read:** the same brief §6 (recs), §7 (order), §10 (adopted - it wins);
  `docs/plans/2026-11-04-realism.md` §5 (every part's rec list), §6a-6c (the gate's runs; 6c = HD Aaron in our
  stage), §7 (state).
- **The decisions — read in TASKS:** the entries from "THE BAR" (2026-11-04) to "FABIENNE & PERCY" (2026-11-05).
- **Standards it touches — read these sections:** `character-data-model.md` §1.4 (HD detail), §3 (materials and
  the texture set, the `micro_normal` channel), §4 (hair); `skeleton-and-face.md` §2.3 (the face controls the gate's
  expressions need); `parity-scorecard.md` "Head and face", "Skin and materials", "Eyes, teeth, tongue, hair".
- **Facts:** `docs/dev/RESEARCH.md` - the gaps entry (scans, nappy, Fabienne & Percy), the CC5 bridge, EEVEE.
- **Tools:** `tools/gate/parts_gate.py` (the gate part by part: ours and HD Aaron through the same anatomy-placed
  cameras), `tools/gate/cc5_bench.py` (`render --cc5-blend` puts a CC5 character in our stage; `--our-skin`),
  `tools/gate/blender_gate.py`, `eevee_settings.py`, `relief_tiles.py`; outputs in `.dev/gate/` (not in git).
- **CC5's side:** memory `cc5-control` (first call `check_cc5_connection`; `exec_python` off; the trial's dialogs are
  the user's to click). Limits measured: captures are 600 x 600 whatever is asked; the trial logo covers 27-73% of
  the width and 44-55% of the height - parts are framed above or below it; FBX / OBJ / ABC exports are counted (30 in
  the trial; 2 used: 10:41 mine, 12:06 the user's). HD Aaron's export (CC5's Blender Pipeline plugin, "Export FBX",
  Selected Models, SubD 1, every box off) and its CC Blender Tools import: `.dev/gate/cc5_aaron_blender/`
  (`aaron_cctools_eevee.blend`, `aaron_cctools_cycles.blend`). Hair on disk for the gate: `Classic Slick Back.rlHair`,
  `Stubble.rlHair`, HD brows (`F:\Reallusion Content\Reallusion Templates\Hair\Group\`).

### Where it stands (update after every step)

- **THE ONE PRIORITY (the user, 2026-11-05, TASKS "THE ONE PRIORITY"):** prove CC5 quality on every part, and that it
  holds for any custom character - or prove a part can't, and change the approach. Risk first: (1) face mid-scale
  relief by baking the HSRD scans' geometry into normal maps through the scan route's fit; (2) body relief; (3) scalp
  hair (groom vs shading); (4) eyes; (5) smile; (6) the rest; (7) four+ different characters through the same method.

- 2026-11-05: HD Aaron in our stage with CC5's maps comes close to CC5 (realism §6c) - the gap is our characters'
  content. **The standard is HD Aaron in Blender** (TASKS "THE GATE PART BY PART"): the user's hair export imported
  (`aaron_hair_{eevee,cycles}.blend`); `tools/gate/parts_gate.py` renders 21 views per character (`render --who
  ours|cc5 --engine eevee|cycles`, then `sheet`) into `.dev/gate/parts/2026-11-05/`; the report goes to
  `docs/gate/2026-11-05/report.md`. DONE (each committed, the report's "Done since the baseline"): the EEVEE and
  Cycles baselines (every part below); teeth ride the jaw; rec 18 microrelief; rec 14 v1 nails; rec 8 brows
  (`modules/hair/brows.py`, library "JustStage brows"); the eyes opened to an adult's 8.7 mm (`body_create.EYE_OPEN`,
  dressed and library humans); lashes sweep up (`lashes.py`); rec 11 v1 scalp groom (`modules/hair/scalp.py`, library
  "JustStage short combed", ~100k strands). IN PROGRESS - skin colour from scans, the likeness rule's way: HSRD-100
  through the scan route (done: hsr0015 0027 0028 0040 0042; 0081 0102 0112 0161 running; 0023 failed at the marks -
  its pose is a hand scan); `skin_base.py compose SEED '{"colour": "scans", "mid_from": {...}}'` then
  `tools/build_skins.py -- --composed SEED KEY LIB` makes a test skin; the gate's `--skin`, `--character`, `--scalp`.
  Composition 503 (hsr0040 + lps) natural but paler and softer than Aaron. NEXT: compose library skins by tone / sex /
  age from the HSRD people (fix the pale neck patch at the composite's coverage edge), rebuild the library's characters
  (skins backed up first), then a full gate re-run (EEVEE + Cycles) and the report; then body relief (rec 7 + 17: the
  torso is the largest measured gap), eyes (rec 12: sclera, wet margin), mouth (13), smile shapes, hair shading (rec
  1). The user's standing order: don't stop until every part meets the bar or it is measured impossible.

## Coordination

- **web-4c** holds the graphics card for its clips until I send "card free" - sent when CC5 is closed and my renders
  stop. Its limits are requests (memory `peer-limits-are-requests`).
- **"just-stage asset search"** fetches and searches assets; TASKS and RESEARCH are mine to record from what it sends
  (checked against its logs first).
- **Needs the user:** no emails, no purchases (the user, 2026-11-05).
