# Resume — what to read before working (after every compaction, on "re-read docs", at every session start)

The user, 2026-11-05: "so every time i tell you to re read docs, what does that mean to you ... you should knoww the
doncs you need to re read"; "fix it keep things current do not really on compaction". A SessionStart hook
(`.claude/settings.json` → `tools/resume_hook.py`) puts this file into the session at every start, after a compaction
too. **Rule: before any tool call, read the "Always" list and the active job's files - in full where marked. A
compaction summary is never a substitute.** This file stays short: it points to the plan; the plan holds the method,
RESEARCH the facts, TASKS the user's words. It is updated in the same commit that starts, changes or ends a job, and
"Where it stands" after every step. (Until 2026-11-07 this file also carried the proof log and the jobs' history -
moved to RESEARCH §14.2 and §14.1; git keeps the old text.)

## THE ONE PRIORITY (the user, 2026-11-05; TASKS "THE ONE PRIORITY"; memory `one-priority`)

**Prove CC5 (HD Aaron) quality on every body part, and that it holds for any custom character - or prove a part can't
and change the approach. Nothing else.** Order, riskiest first: face mid-scale relief -> body relief -> scalp hair
(groom or shading) -> eyes -> smile -> the rest -> four or more characters and the full gate. Per part: proved / not
proved / disproved. The gate: `docs/standards/quality-gate.md`.

## Always

- `AGENTS.md` and `CLAUDE.md` (loaded automatically), `docs/dev/README.md` (the doc map).
- `docs/standards/README.md` §1 and §3: a job's governing standard is read before its plan.
- Memory: the index (loaded automatically) and `search-mistakes` before any search, rec or plan.

## The active job: OUR ASSETS TO HD AARON (the own-content proof), under THE PLAN - read both in full

- **`docs/plans/2026-11-08-own-content-proof.md` - the working doc, read FIRST** (the user, 2026-11-08 ~09:55: "prove
  if we can meet quality that means with our texstures"; the plan approved ~10:40, TASKS "UNTIL A VERDICT ON EVERY
  PART" -> "OUR ASSETS TO HD AARON"): part by part, our own content against HD Aaron in EEVEE, fixing it; its status
  table, candidate fixes, rounds and run log. The transplant verdicts further down are diagnostics, not verdicts. Its
  batch scripts and logs live in the scratchpad of the session before the 2026-11-08 14:05 lock-up,
  `F:/ClaudeCode/tmp/claude/bff537e12af9b769/5a1c3314-77f3-4a60-8d1a-9d80b40bc2f8/scratchpad` ("scratchpad/" in the
  doc).
- **`docs/plans/2026-11-06-the-plan.md`** - the final method per part, its status and its gate measure; §19 the
  decisions (19.1 taken under the user's go of 2026-11-07, 19.2 waiting for the user - nothing stops for them); §20
  the build order. Checked claim by claim by four independent readers 2026-11-07 (`.dev/audit/2026-11-07/CHECK-A.md`
  to `CHECK-D.md`).
- TASKS' first entry (UNTIL A VERDICT ON EVERY PART, with OUR ASSETS TO HD AARON - the user's words of 2026-11-08)
  and THE DEEP READ, THEN ONE PLAN (the user's words of 2026-11-07).
- RESEARCH.md §14 (the character, part by part: 14.N = the plan's §N) for the part being worked on.

### Where it stands (update after every step)

- **THE USER, 2026-11-08 (TASKS "UNTIL A VERDICT ON EVERY PART"): no stopping - after turns and compactions - until
  every part and the whole body has a verdict (meets HD Aaron or provably can't); then on to the app's other features.
  Decisions attacked to consensus and kept (changed only on a new measured fact, shown). After a compaction: read this
  file, the plan's §18a and §19.3 and `docs/gate/2026-11-07/report.md` first; keep a background job running.**
- **Wake-ups (session-only, expire after 7 days or with the session - set them again with CronCreate; last set
  2026-11-08 14:25 after the lock-up):** every 20 min when idle, resume the own-content proof from its working doc;
  every 3 h, remind every peer session of the shared rules (the user: "they can help keep you on task").
- **2026-11-09 18:3x:** the verdict committed (51bc0ab: not CC5 quality with free assets - the face's mid-scale
  relief, the live-view hair). Then the face relief's "can't" REOPENED (the user: "never stop until you have proven or
  disproven"): HSR0040 (HSRD-100, CC BY 4.0, in our scan set) is 50 and his COLOUR carries deep forehead lines and
  crow's feet - only his mesh lost them. On trial (the working doc's 18:2x): Frangi line relief from his colour
  (`wrinkles*photo40`, `photo40b`) rendering (`scratchpad/batch_photo40.sh` in the old scratchpad); Sapiens2's normals
  of his colour in our head tile (`scratchpad/photorelief/sapiens_relief.py` -> `.dev/gate/wrinkles/sap40`) - they show
  every crease; its height conversion being fixed. His 112 photos with RealityCapture cameras (`.xmp`) unpacked in
  `.dev/downloads/hsrd100/HSR0040-Body-086/source/photos/` (a higher-resolution route if needed). Card: booked from
  just-voice and family-release (family-release wants the whole PC in ~1 h - it asks first).
  18:4x: **Sapiens2's relief of his colour at x2 makes the whole face read as real, older skin** (`row_sap40_*.png`) -
  the free route makes the mid-scale relief; tuning its cut and depth against HD Aaron. Queue on the card (old
  scratchpad): `batch_sap40f.sh` (the fine cut, eye area kept, pits out) -> `batch_vfbake.sh` (hair cards textured from
  our own strands, `factors vfbake*B4`, new) -> `batch_cc5photo.sh` (HD Aaron in the same run, then `measure.py`).
  19:0x: the colour relief INTO THE PRODUCT (my decision under the go, the working doc's 18:5x, NOT STANDARD):
  `tools/face_test/colour_relief.py` per scan -> `skin_base._colour_relief` (one scan a texel, `COLOUR_RELIEF` 1.0);
  running `batch_colourrelief.sh` (old scratchpad: the tool on 9 more scans, backups `*_2026-11-09cr`, the six skins
  composed and built, the library's characters, renders of six characters + HD Aaron in
  `.dev/gate/parts/2026-11-09colourrelief`, every suite). Don't edit skin_base.py / colour_relief.py / build tools
  while it runs. The baked hair cards (round 1) read as scales; round 2 next (clump cards, our hair shading).
  19:3x: the first rollout stopped (a seam where the relief's crop ended - fixed by `EDGE_FADE_MM`, the crop moved up);
  RERUN from 19:33 (the 19:21 backups `*_2026-11-09cr` are the true before - kept); then `batch_vfbake2.sh` (hair
  round 2: `factors vfbake2*B4*12*0.5` / `*18*0.5`, new).
  20:4x: **the face relief verified and committed (532cf98; unit 45, tools 60, Blender 209 passed) - the face's
  "can't" is disproven** (the working doc's verdict table). Running: hair round 2 (`batch_vfbake2.sh`). The face's
  next candidates (after the hair): the fine crease net - the dot filter at 1 mm2, the scans' own 16K colour.
  21:0x: **the hair - a free card groom reads as hair in the live view**: VincentFreelance's cut (CC BY) + Polytricity's
  4K strand strips (CC BY, `.dev/downloads/polytricity_hair_2026-11-09/`) + our hair model (`factors vfpoly*B4`);
  the cap's band being fixed (`batch_vfcap2.sh`).
  21:2x: **THE VERDICT REVISED: no part is blocked by a missing free asset - both "can't"s disproven** (the working
  doc's 21:2x). Not CC5 quality yet - work left: the hair's short sides (a strand-textured cap from Polytricity's strips,
  as HD Aaron's `Hair_Clap`), the face's fine crease net (dot filter 1 mm2; the scans' 16K colour). Waiting for the
  user: the hair's product route changes Q-HAIR-7 (theirs).
  21:3x: **family-release has the WHOLE PC (~60-75 min from ~21:30, its release test pass): nothing heavy of mine
  until its "PC free".** Then, in order: look at `row_vfcapbuzz_*` (the short layer rooted on the cap's footprint off
  the front - `factors vfpoly*B4*0.2*capbuzz`); the face's fine crease net (the dot filter at 1 mm2 in a scratch copy,
  then the scans' 16K colour).
  22:xx: family-release's "PC free" came (releases run on GitHub from here); running `batch_after_pc.sh` (old
  scratchpad: the hair's short layer on the cap footprint, then the face's fine crease net trial with HD Aaron measured).
  23:3x: verified and committed - the compositions put right by own sex (HSR0081 is a woman; `rebuild_scan_skins.
  own_sex_first`), all six skins and the library rebuilt (backups `*_2026-11-09sx`); unit 45, tools 62, Blender 209.
  The hair's short sides: the cut's cap shaded as clipped hair (`vfpoly*B4*0.2*strands`, a fade from behind). The eye's
  lid shape waits on Q-BASE-4 (the user's: the plan's head-topology fallback, design and spec disagree). Next work
  needing no decision: the face's fine crease net by our own generated microrelief.
  23:5x: the forehead's microrelief depth (x1 kept) and brow cards (not kept) tried; running THE FULL GATE
  (`batch_fullgate.sh` in the old scratchpad -> `.dev/gate/parts/2026-11-09gate`, ~60-90 min); then write
  `docs/gate/2026-11-09/report.md` from its sheets and table.
  2026-11-10 00:3x: **the full gate done - `docs/gate/2026-11-09/report.md`; every part has a verdict; no part is
  blocked by a missing free asset.** Waiting for the user: Q-HAIR-7 (the free card hair into the product) and
  Q-BASE-4 (the lid's head-topology fallback). Work left (mine): the hand's / foot's tone and sheen, the closed lid,
  the forehead's fine net (a better microrelief generator), the ear's concha, the tongue's light.
  01:0x: the closed lid into the product (a trial kept at 00:49: the working doc) - rolling out `batch_lidprod.sh`
  (old scratchpad; backups `*_2026-11-10lid`) - VERIFIED 01:3x (unit 45, tools 62, Blender 209; two chain-walking
  tests updated, test_skin_maps 25 passed). Next work (mine): the ear's concha - HUTUBS's ear targets (Q-EAR-1, plan
  build step 4; 57 heads zipped in `.dev/downloads/hf_samples/hutubs_meshes/meshes.zip`).
  01:5x: the ear's shallow concha is hm08's TOPOLOGY (a real HUTUBS ear wrapped on through the mixer keeps the dish;
  committed 7a9a552) - with the lid's ledge it joins Q-BASE-4 (the head alone on a new topology - the user's: the
  design and spec disagree on the fallback). The scan route now takes shape-only scans (PLY, clay views). Waiting for
  the user: Q-HAIR-7 (free card hair into the product), Q-BASE-4. Work left (mine): the forehead's fine net (a better
  microrelief generator), the tongue's light.
  03:40: Q-EAR-1 done - the 58 HUTUBS ears in the mixer (ears only, ATTRIBUTION row; tools 63, mixer 13 passed).
  04:4x: Q-BODY-3 - the women's torso relief from Blender Studio's CC0 female sculpt, in the three women's skins and
  the library (verified: unit 45, tools 63, Blender 212); its measure against HD Ariana waits for her export
  (Q-GATE-3, the user's). The gate's "aa" pairing fixed (jawOpen 0.8). Q-BASE-4's facts for the user (ICT-FaceKit's
  head has the lid fold and the ear's pit; Blender Studio's does not) - the working doc 03:5x, the gate report.
  05:2x: Q-BODY-3's limbs from HSR0015-Body-087 (CC BY 4.0): round 1's thighs streaked (the fit's leftover), fixed by
  `relief_hp_mm` 15; her sneakers and tucked hands left out (`body_scan` `leave_out`, new). Running `batch_hsr15c.sh`
  (old scratchpad: all three women's skins and the library rebuilt - backups `*_2026-11-10limbs`; renders `_lo`),
  then `batch_cavity.sh`: the forehead's fine net is HD Aaron's CAVITY map on his roughness (CC5's formula, RESEARCH
  14.10) - ours flat; trial `factors cavitynet*`. Uncommitted: body_scan.py, factors.py, the two tests, the docs.
  05:4x: the cavity trial NOT kept (the cheek's bands fell, the forehead softer). His forehead's look is pinpoint
  glints, and his coat lobe takes the bumped normal (ours unlinked) - `batch_coatnormal.sh` (`factors coatnormal`)
  starts by itself after `batch_limblayer.sh` (the women's thigh streaks: limb colour vs relief, one at a time; it
  restores and rebuilds the women after). The product change and its test are staged in this session's scratchpad
  (`test_coat_normal_snippet.py`); never edit `extension/` while a batch runs Blender.
  06:5x: found the LEGS' fault (every man's thighs: brown speckled patches with edges - HSR0042's colour; lumps -
  its relief at 40 mm) and the women's streaks (HSR0015's relief at 15 mm). Fixes: `no_colour` on hsr0042, per-tile
  cuts (`_relief_cut`, legs 6 mm), hsr0015 at 6 mm with her thigh dent marked out (`marks_out` per tile). Coat rounds
  1-2: the coat on the bumped normal + MICRO_DISTANCE x0.75 (cheek back in band, forehead strip 0.51 -> 0.62).
  Running: `batch_menlegs2.sh` (the men rebuilt) -> `apply_coat.py` -> `batch_end_1110.sh` (the women, the library,
  the full gate `.dev/gate/parts/2026-11-10gate`, every suite). Then: look at every sheet, write the gate report's
  changes, commit. Open: the forehead's granules (the micro tile's pattern), the cheek's pore band (1.11 with the coat
  - pores x0.9 if it stays over).
  07:5x: VERIFIED and committed (70fb51d; unit 45, tools 66, Blender 214): every character's legs one even tone, the
  women's limbs, the coat on the bumped normal; the gate report updated. Running `batch_pores09.sh` (pores x0.9 / x0.8,
  the cheek's pore band). Open (mine): the forehead's granules (box spent), the foot's smudges between the toe tendons,
  the slim woman's flank line. Waiting for the user: Q-HAIR-7, Q-BASE-4, Q-GATE-3.
- **2026-11-09 17:0x:** committed since 14:0x - lower lashes colour and thickness, lip creases (ff494f2), the nails'
  outline (fa83f03), the hands' tint (6f19979). The user, 16:4x: I had asked for two downloads for ~12 hours under a
  standing go - both fetched now: ISSA (`.dev/downloads/issa_2026-11-09/`) - read: the tone model matches measured
  dark skin within ~3 delta-E, no calibration job (RESEARCH 14.10 corrected); VincentFreelance's free cuts
  (`.dev/downloads/vincent_hair_2026-11-09/`, CC BY 4.0; male collection 01 split per bust into `m01_busts.blend`).
  Running: the cut fitted onto the gate's man (`scratchpad/batch_vfhair.sh`, `vfhair*B4[*tex]`). Global rule added:
  while a job runs, work the next piece; a blocking question goes first. The closed lid's streaks: blink-driven relief
  (pixel-equal open eye) not enough, the colour smoothing made a plastic sheet - removed, open.
- **2026-11-09 14:0x:** committed since 10:1x - the lips a soft sheen 0.4 / 0.2 (ab851d6), toenails a short plate on
  top of the toe (7eead78), the tear film faded out toward the lids (e1fd9f8), the lids' stretched margins smoothed
  (4758683); tried and removed: the closed lid's fold mask (the open lid went glossy - the working doc's 11:18).
  Running: the lower lashes at melanin 0.8 (`scratchpad/batch_lashprod.sh`, backup `library_2026-11-09q`). Open (the
  working doc): the closed lid's streaks (expression-driven detail), the lower lid's ledge width (shape), the lower
  lashes faint (thin), women's body relief (Q-BODY-3), dark skin's ear redness (chromophore maps); waiting for the
  user: ISSA + openpyxl, the hair cut.
- **2026-11-09 10:1x:** committed since 07:3x - the scans' darkened rims weighed out (0359462: no jaw smudges), the
  ears' redness by tone (4a24557), women's sparser brows live by the gender slider (dae067b), the brows thinning to
  their edges (060d447); the verdict table in the working doc updated. Running: a fresh side-by-side of every view
  (`scratchpad/batch_allviews.sh` -> `scratchpad/all/row_<view>.png`) to pick the next worst fault. Open: the scans'
  blood redness on dark skin (chromophore maps), the brows' fine-hair veil on dark skin (strand haze), the lower
  lashes, the ears' gloss; waiting for the user: ISSA + openpyxl, the hair cut.
- **2026-11-09 07:3x:** committed since 05:4x - the scans' edge faded (b978644: no neck / chest patch on any
  character), brown brows and the gate keeping a library character's own brows (afff11c). Running: the scans'
  darkened rims weighed out (`skin_base.rim_weight`; the women's jaw smudges) - `scratchpad/batch_rim.sh` (backups
  `compositions_2026-11-09c`, `skins_2026-11-09b`, `library_2026-11-09i`). Open (the working doc): women's sparser
  brows (a live density by sex), the brows' blocky shape, the lower lashes, the ears; waiting for the user: ISSA and
  openpyxl (the dark skin's calibration), the hair cut.
- **2026-11-09 05:4x:** kept and committed (6882eed) - the Heavy woman at melanin 0.1 (was 0.25, past measured skin:
  ashy); the gate's variants point the skin at their copy. Kept on trial, rolling out - the neck / chest patch: the
  composer cut its low layer where the scans end (`skin_base.faded_out`: carried past the edge, then OpenCV's
  multi-band blend; the pores' colour feathered) - `scratchpad/batch_cover_all.sh` (all six skins, library, six
  characters' renders, every suite; backups `.dev/backup/compositions_2026-11-09b`, `skins_2026-11-09`,
  `library_2026-11-09g`). Next: commit it, then the verdict table's open items (the working doc).
- **2026-11-09 04:3x:** kept - the lips matte (`maps.LIP_ROUGHNESS, LIP_COAT` 0.6 / 0.05) and the lining out of the
  mouth's corners (`make_mouth_mask.CORNER_FADE`; masks regenerated, backup `.dev/backup/mouthmasks_2026-11-09`);
  end run `scratchpad/batch_end3.sh` (unit 45, tools 51 passed; Blender running). Now: **dark skin reads ashy** - the
  tone model greys past NIST's darkest fitted skin (RESEARCH §14.10 "The model's dark end greys"); trial
  `batch_tone.sh` (the Heavy woman at melanin 0.14 / 0.1 / 0.065 against her preset 0.25) queued after the end run;
  asked of the user: the ISSA spreadsheet (CC BY 4.0, 9.3 MB) + openpyxl to calibrate the dark end, and the hair cut.
- **2026-11-09 03:5x (the working doc's entries from 22:3x on; its verdict table current; the end run green 03:51 -
  unit 45, tools 51, Blender 199):** kept and verified tonight
  - the feet (Thunk3D), the torso (debris fill: nipples, the sternum oval; the scanned man's scar out), the upper
  lashes smooth, the lips (seam band, soft patchy lines, the upper lip deeper red), the eyes' surround, the chin's pores
  x0.6, the border detail fade, the stubble in patches, women's pores finer (PORES_BY_SEX); ruled out with measures - the face/body colour gap (a bad mask
  of mine), the ears' depth, the eye rim's tint, the neck patch as beard shadow. Open, minor: the lower lashes' kinks,
  the New human's neck patch and cheek blotches (the composition's coverage), Amara's chest seam (her legacy skin), the
  ears' darkness. Waiting for the user: the hair cut's download
  (VincentFreelance, CC BY 4.0, glTF 18 MB - the standing go in TASKS noted; the per-download rule still asks), the
  face relief (a paid scan or an artist).
- **2026-11-08 22:3x: the feet work** - Thunk3D's CC BY scan as the "feet" part on UDIM 1003 + 1004 (most of our foot
  is on 1003; the first bake was 1004 only), the wrap smoothed, the debris limit 0.8: the foot's top shows real tendons
  and veins at x1 (working doc, "21:47-, the feet"). Into the product: `build_skins.BODY_PARTS` + "feet", ATTRIBUTION;
  `scratchpad/batch_feet_prod.sh` (library backup `.dev/backup/library_2026-11-08e`): rebuilt, the library man's foot
  shows them, **the end run green 22:53 (unit 45, tools 50, Blender 195)**. Running `scratchpad/batch_torso.sh`: the
  body relief's debris filled (the torso's oval by the sternum, the nipples' bumps), the lips' seam layer
  (`lipseam` renders), the eye rim's tint (`margintint`), then the tools and Blender suites. Waiting for the user: the
  hair cut's download (VincentFreelance, CC BY, glTF 18 MB).
  Next after it: the verdict table's open routes (torso definition slider from the CC0 MINDFRONT normal with its seams
  fixed; lips' colour to the seam; face colour), then the four characters.
- **2026-11-08 21:0x (read the working doc's "evening's verdicts" table and the entries above it):** the user's plan
  restated in my words at ~14:45 (TASKS) - the bar "a person can't tell at close-up", worst fault first, a time box per
  part, "can't, X missing" when the routes are spent. Kept today: forehead pores x1, stubble 100 a cm2, the scalp one
  ring, brows 1200/2000/0.92, the lips' lines in the shader. Verdicts: cheek and nose skin match; the face reads made -
  the layer diagnostic and the split put it in the live-view strand haze (cards, the approved rule) and the skin's
  mid-scale relief: **face skin relief - can't with free assets in hand** (three scans' relief, a made wrinkle layer);
  hair needs cards + an artist's free cut (the Chrome extension disconnected at 16:02); body definition from MakeHuman's
  CC0 normal works (a slider, seams to fix). Running 21:0x: the end run (`scratchpad/batch_end.sh`: the region map, the
  library rebuilt with a backup at `.dev/backup/library_2026-11-08d`, then every suite). The job's scratchpad:
  `F:/ClaudeCode/tmp/claude/bff537e12af9b769/5a1c3314-77f3-4a60-8d1a-9d80b40bc2f8/scratchpad`.
- **2026-11-08 14:05: the computer locked up and restarted.** Lost: nothing on disk - round 2a (face skin) had not
  started (it waited for just voice's card). 14:2x: found the forehead region-map variants also differed from the
  shipped map at region borders (the map is made on today's New human), so `regions*base` (today's map, unchanged) was
  added as their one-change baseline; round 2a running (`batch_r2a.sh`, log `batch_r2a.log`).

- **2026-11-08 ~02:00 (read the plan's §18a for each row's numbers):** block B ended; suites: unit 45 passed, tools
  33 passed, Blender ~143 passed / 1 failed (test_lashes: the ledge turn put one lash on the nose - fixed by
  `lashes.ROOT_REACH`, the three lash tests pass; the full Blender suite reruns at the end). Found and fixed on the CPU:
  the teeth transplant (new keys start at 1.0), the brows' sweep is placement (roots on the lid, median 8.5 mm above
  the eye against his 17.5), not binding. Built and dry-run: `aaronshape*upper` (his brow ridge and fold, depth-
  projected), `aaroncards*shaped`, `eyetrans`, `aaroneyes*own`, `nailmat`, `setkey*mouthClose*0.1` (closes the
  slit), `aaronwrinkles*smile`, the foot transplant (`aaron_foot.npz`), the body rig (`tools/gate/body_rig.py`,
  `parts_gate.POSES`, `test_body_rig.py`). **Block C** (`scratchpad/batch_C.sh`, log `batch_C` in batch_B.log) waits
  for the file `scratchpad/card_back` - the order (07:40 UTC): web-9e's takes, then web-4c's 20-25 min slot (send it "card yours" on web-9e's "card free"), web-4c's slot done 07:48; web-9e has the card (07:5x) for its translation and a ~10 min JustDirect window check, closing JustDirect after; create the file on web-9e's one "card free"; web-4c's ~50 min film run is agreed at the boundary after POSE-DONE - when web-4c says it's ready, make `scratchpad/card_back.after_pose` (or `card_back.lent` if POSE is already done); the log then prints PAUSED-FOR-PEER: send web-4c "card yours"; on its "card free" delete `card_back.lent`. **Found 08:15: the running block C reads its script's copy from before a `sed -i` at 07:4x (sed replaces the file; bash keeps the old one open) - the foot's 1003 fix and the PAUSED-FOR-PEER hook are not in it.** So: a watcher touches `card_back.lent` when the smoothed-rig step starts (the batch then holds before T24, after POSE-DONE) - on POSE-DONE send web-4c "card yours"; the full foot (1003+1004) reruns separately. Never `sed -i` a running script (Python's write in place reaches it); 08:45 the card went to web-4c (block C paused after POSE-DONE) - on its "card free" delete `scratchpad/card_back.lent` (block C resumes; a job then re-renders his posed views). Verdicts so far: rows 3, 4, 5, 5a, 10, 11, 12, 13, 15, 17 (bends) feasible (rendered); 16 feasible as modelling. 09:15 block C resumed; block C done 09:33 (B EXIT 0). 09:4x: card to web-4c (12 min), it passes to web-9e (20 min); on web-9e's "card free" create `scratchpad/card_back.cards_go` - the speed test with his card grooms starts (row 20's deciding test); CARDS-DONE (row 20 feasible: his cards 54 fps); web-4c has the card (~10 min planner); on its "card free" send web-9e "card free" (~10 min Live-tab check); on web-9e's "card free" create `scratchpad/card_back.suite_go` - the Blender suite runs (tools 33 / unit 45 already passed 09:4x), then the brow combinations' renders (build queue item 1). Verdicts: rows 1-19 all feasible (16 as modelling, 17 for bends); row 20 waits for the cards' measure; `card_back.lent` pauses it between
  steps for a peer. Then review every sheet against his and write each row's verdict.
- **2026-11-08 ~11:30: every §18a row has a verdict, none fails (the gate report's table). Building the plan's §19.4 queue: items 1-3 done and tested (rim brows, the lip seal, the blink's closing step) plus ICT's blink as our blink units; the library rebuilt with them (backup `.dev/backup/library_2026-11-08`). Item 4 (live-view cards) waits for the user (Q-HAIR-7's gap: MakeHuman's card meshes are other cuts). Item 5: the smaller eyeball alone not kept (the lids follow it in); the enamel ivory (done); the lip seal now fades with jawOpen (it closed the open mouth); the library needs a rebuild for the enamel (batch with the next change). Open for the user: item 4's card source (Q-HAIR-7's gap), the skin rule, HD Ariana, Thunk3D's foot.**
- **2026-11-08 afternoon: build queue item 8, the skeleton - its working doc `docs/plans/2026-11-08-skeleton.md`
  (read it first).** Built: the spec's 82 UE5 bones (`tools/make_skeleton.py` -> `data/generated/rigs/`), the Rig
  module (`juststage.rig.add_skeleton`, New human adds it, refit after shape changes), the gate on it plus
  `pose_twist`. Next: the suites, the posed renders (card), the library rebuild.
  from ~06:25 on the card (peers gave it; send web-4c "card free" when all end): batch D's full suite
  (`.dev/suite_2026-11-08s.log`), then E (`pose_twist` again; the eyeball 0.89 about its centre / cornea front ->
  `.dev/gate/parts/2026-11-08eye`), F (the smile on ICT's units -> `2026-11-08smile`; job doc
  `docs/plans/2026-11-08-smile-units.md`), G (item 7, the nail bed as shape: `nailshape` -> `2026-11-08nail`) - logs
  `scratchpad/batch_{D_skel,E,F,G}.log`. Item 5 found: the teeth's size is arch form, the tongue sits like his
  (RESEARCH 14.5). After: look at each sheet, the narrowed skeleton test run, the library rebuild (backup first).
- **2026-11-08 07:08: the skeleton job done (library rebuilt with it, backup `library_2026-11-08b`); the card given back.
  Active job: THE FACE RIG - working doc `docs/plans/2026-11-08-face-rig.md`: steps 1-3f done (the wheel; the
  reading; our `face.dna` - MetaHuman's names, our values, 69 channels incl. 28 split parts; the runtime; the jaw, eye
  and tongue joints with measured motions; the stand-in teeth keys removed); a clean full suite 08:14 (178 passed);
  next: wrinkles / correctives (Q-RIG-3 / Q-RIG-4 - research: Blender Studio's procedural wrinkles read, micro only;
  the expression folds' source still open, RESEARCH §14.7). Item 7 (nails) DONE in the product and the library (sheet
  `scratchpad/sheet_D24_nails_product.png`; skin tests 17 passed). Item 5's inner mouth: our mouth's own skin shadows
  the tongue, and both tongues see none of the stage's lights - his pink is bounce or material; `factors mouthlining`
  queued (batch R, waits for web-4c's "card yours" -> touch `scratchpad/card_back.R_go`, then send "card free"). Open from the queue: item 7's nail (displacement into the product, the lunula's white, the spike faces),
  item 5's tongue (our body's shadow in the mouth - narrow it to the mouth's inner skin; card), the full Blender suite
  for today's later changes (card).**
- **2026-11-08 ~08:45: the mixer job opened - `docs/plans/2026-11-08-mixer.md` (read it first); the face rig's
  wrinkles wait on research.** Built and tested by the afternoon: masks, identities (with the neck fill), the mix as
  `scans.<identity>.<region>.<features|proportions>` sliders (the data model's rule), MetaHuman's Blend Type read in its
  source, the helpers following the mixed skin (eyes, teeth, joints), the Mixer panel (`ui/mixer_panel.py`). Next: the
  panel seen in the real window (asked web-4c for the card), a gate render of a mix (seams at the neck and part
  borders), the per-band skin blend, user docs (none exist), then the full suite.
- **The user, 2026-11-08 ~09:50, seeing the Mixer window check: "the default character skin is plastic is this just
  because you havent transfter your fixs to the app or is this actaully the best quality you have proven?"** Checked:
  the default skin (`Scan man A skin`, the app's library, built 2026-11-07 18:59) has the face-skin fixes; the gate
  builds its stage with the app's own code (`parts_gate._stage` -> `startup.new_stage`: the same key, rim and image
  light), so the light isn't the difference; the window showed the live view of a fresh New human seconds after it
  appeared, the proofs are F12 EEVEE renders of the library's man; and "feasible" was proved by transplants (HD Aaron's
  content on our body) - our own content still measures above him (§18a row 1). Running: `scratchpad/batch_new.sh` -
  the New human through the gate (`parts_gate --character new`) beside the gate's man and HD Aaron
  (`.dev/gate/parts/2026-11-08new`); then find the factor if the New human is worse. Mistake made and caught: I first
  assumed the gate had its own CC5-matched lights - read the code before saying what a test used.
- **THE FEASIBILITY CHECKLIST (the plan's §18a) drives every step** - every part from the plan's rows and the gate's
  list; read it before choosing the next step, update its row the moment a result lands (the user, 2026-11-07 late:
  "why do you keep missing everything").

- **The plan's §0 governs (2026-11-07 evening): the bar is ours against HD Aaron in EEVEE only - never Aaron in Cycles;
  one loop per part (render both in EEVEE -> measure and look -> one change -> keep or undo) with the stop rule; no
  new tool, audit or decision list unless a measured gap needs it; no turn ends on a report.** Cycles numbers below are
  diagnostics of ours, not verdicts.
- 2026-11-07: the plan checked and corrected; RESEARCH an index by topic (§14.1-14.15); this file cut to a pointer.
- Gate tools (§20 step 1): `measure.py` (bands in mm, ridges, Lab, repeatability), `measure_table.py`, `dists.py`
  (DISTS against Aaron with his floor), `factors.py` (one factor at a time; trial settings; parts and colour edits in
  the shader - a UDIM image's `pixels` reads only its first tile), `parts_gate --lights world`; `quality-gate.md` to
  the bar. Report: `docs/gate/2026-11-07/report.md`; renders `.dev/gate/parts/2026-11-07a/b/c`.
- Proof (1) face relief: NOT PROVED. EEVEE cheek bands within Aaron's after pores x1.15 / microrelief x1.35 (folds 0.76
  below), forehead equal; but DISTS 0.188 against his 0.06 floor, the same with tone matched - the texture's structure
  (our soft bumps against his crisp network) is the gap; the microrelief generator is NOT STANDARD awaiting the user
  (§19.2 item 2). Cycles ~0.55 of his Cycles build - which build is the bar: §19.2 item 26.
- Face loop, 2026-11-07 evening (`.dev/gate/parts/2026-11-07d`, EEVEE only): (a) why ours reads soft - our pore tile
  is 4.6 px/mm (Ten24 Level_01; his head normal 3.9), so at the cheek view's 34 px/mm the crisp detail is the micro tile
  alone; his is a 388 px/mm micro normal of pillowed ~0.6-1 mm cells with finer cells inside, ours thin walls round flat
  cells (RESEARCH §14.9). (b) A layered tile (`make_microrelief.py --method layered`, `tools/gate/micro_compare.py`,
  `tests/tools/test_microrelief.py`): texture-space DISTS 0.385 -> 0.298 (his floor 0.156), the cheek render 0.188 ->
  0.173 (factor `microtile*s0+micro*1.97`, slope matched) - not yet the shipped tile. (c) Shine moves the bands most:
  roughness x0.75 -> micro 1.70 / pore 1.31 / fold 0.92 of his. (d) The forehead's microrelief factor is 5x the
  cheek's (`make_face_regions.py`, set on voided inputs 11-05) where his MicroNMask is ~1 everywhere - it reads as a
  crisp honeycomb against his soft forehead. (e) `tools/gate/shine_probe.py` reads each BSDF's roughness / specular as
  emission, his and ours. Factor trials now build once (`parts_gate.render` variants).
  (f) The texture measure corrected: `dists.py --patches` (24 patches, energy excess, permutation band +-0.003); the old
  0.06 floor was the same pixels moved. Excess cheek / forehead: today 0.047 / 0.107; tile t1 0.018 / 0.100; the
  forehead's levers roughness x1.38 (0.076) and microrelief x0.4 (0.074). His roughness 0.66 even, ours 0.37-0.48 flat.
  (g) Kept and shipped (commits 32a65c7, 98e3059): the layered tile t1 as the skin's microrelief (x2.686 depth: the same
  slope), the forehead at his mask's micro level (x5 -> x1) and roughness 0.50 - excess cheek 0.018, forehead 0.021;
  the library rebuilt (scan skins, characters; backup `.dev/backup/library_2026-11-07b`). Next: the baseline on the
  rebuilt library and the body trials (`scratchpad/batch_body.sh`, when JustVoice's "card free" comes); body excess
  this morning hand 0.085, torso 0.051, foot 0.107. Hair (RESEARCH §14.14): the groom is the gap (about half his
  stand-off on top and sides; 2% stray strands on the upper back).
- Later 2026-11-07 (all EEVEE against HD Aaron; RESEARCH §14.10-14.14 hold the numbers): body - hand 0.047 (arms'
  micro x2 shipped), torso 0.055 (the scan's red dots unreddened, `hair.spots` / `hair.unred`; re-measure queued),
  foot 0.10 (no scan relief - needs Thunk3D's foot, the user's download); his body shine (coat 0.10 at 0.35, specular
  0.40, base 0.72) read and tried - not the lever. Hair - the mask cut to the head (2% strays on the body, fixed,
  test); "short taper" on trial (stand-off within ~2 mm of his; a bare seam above the ear fixed by combing the sides
  back, re-render queued); contrast - his dark roots / light tips: `factors hairtip` queued. Eyes - iris and white
  close; margin shine, tint, tearline, occlusion change nothing: the lower roll is geometry - the eye-open sliders on
  trial (`factors eyebag*0 ... --alone`). New gate views nose and chin; `dists.py` nose patches (the chin is under
  stubble). The smile: CC5's Mouth_Corner_Pull carries his cheek raise and eye squint, our ARKit mouthSmile only the
  mouth - the expression sets' scoring (plan §19.2 item 9). The card: JustVoice (justvioce-0f) lets us use it
  whenever idle - send "card free" when done.
- Latest (2026-11-07 night): the nose 0.171 -> 0.0785 shipped (pores 0.6, micro 1; the 0.053 first written was a
  whole-skin trial, corrected late that night); torso
  0.049 with the spots unreddened; his body shine set is not the lever (relief is). Eyes: the lower roll survives the
  sliders and a 1.2-1.6 mm margin - the lid's own skin shape; next the plan's escalation (the head on a new topology)
  or a lid-shape fix - not started. Hair: strays and the island partings fixed (`Part by Mesh Islands` off; render
  check `.dev/gate/parts/2026-11-07e/*_taper4*`), the mask chosen in faces; contrast: shading trials can't darken the
  mean (L* 28-30 against his 20) - density on trial (`factors hairdensity`, 130 -> 220 / 300 a cm2). The library's
  scalp asset is short combed rebuilt with the fixes; "short taper" not yet the default.
- Night end (2026-11-07): the hair's bare lines were Blender's Clump Hair Curves (clump 0.25 / 0.35 -> 0.1); the scalp
  at its real density (2.2M a m2, 183,604 strands): back L* 27 -> 23 (his 20.4); "JustStage short taper" a library
  style and the gate's (the library rebuilt, backup `.dev/backup/library_2026-11-07g`). The gate report's night table
  (`docs/gate/2026-11-07/report.md`) holds every part's number. Open: the hair's highlights and style, the lower lid's
  shape, the smile (§19.2 item 9), the foot (its download).
- **Late 2026-11-07 (the user's "go, start as soon as the card frees": decide each part's feasibility within about a
  day).** Found, all in EEVEE against HD Aaron (RESEARCH §14.7, §14.9, §14.12, §14.14):
  - Smile: ICT-FaceKit's scanned smile carried onto our man (`smile_transfer.py`, `factors ictsmile`) moves the
    corners 0.91 of his, and the cheeks lift. His smile line and cheek mass are shape (his wrinkle maps off: only the
    crow's feet go). Depth trials queued.
  - Face skin: the remaining excess (cheek 0.018, forehead 0.021) sits at VGG stages 3-5, ~0.5-2 mm: pores' size
    and pattern (`dists.py --by-layer`). Pore size and depth trials queued (`.dev/gate/parts/2026-11-07k`).
  - Eyes: the lower lid's roll is its margin's tilt (a wall, the upper a ledge). `lidsmooth` failed; `factors
    lidledge` queued.
  - Hair: the procedural comb's outline is the gap (a helmet). HD Aaron's own cut as our strands
    (`groom_transfer.py cards`, `factors guidefile*aaron_cards`) is queued, to judge our render on his cut.
  - Suites: unit 45 and tools 30 passed; the Blender suite printed no summary, so it is rerun with its log kept
    (`.dev/suite_2026-11-07k.log`).
- **The user, 2026-11-07 late: "focus on can we meet quality 1st if anyone cant meet quality we stop"; "why is it
  taking so long".** The method changed to one deciding test per part: THE TRANSPLANT - HD Aaron's own content on our
  body, rendered our way (local tests only). Matches him -> our body and renderer carry CC5 there, the rest is content
  (feasible); can't match even with his content -> that part fails, stop. Built: skin (`factors aaronskin`), hair (his
  cut as our strands - done, outline right; `fieldcut`: our own generator along his measured cut).
- **Block B runs (from 2026-11-08 ~00:30, `scratchpad/batch_B.log`); when it ends send "card free" to ALL THREE:
  web-9e (a 6-min mocap take) first, then web-4c (its clips retry), then justvioce-e3 (JustVoice, hours of speech
  tests) - the order JustVoice agreed.**
- **Card order, 2026-11-07 late:** our block A (`scratchpad/batch_A.sh`: every transplant - ears, lips, mouth,
  teeth, brows / lashes / stubble cards, torso, hand, nails - and the quiff) runs now; then "card free" to web-4c for its
  clips (30-60 min); after its "card free", our block B (`scratchpad/batch_B.sh`: every part beside his, the other
  characters, the trials, the suites last).
- (Earlier:) **web-4c (JustDirect) had the card** after our first "card free": nothing of ours on it until it said
  it was done. Then run `scratchpad/batch_decide.sh` (the transplant, the field cut, every part's current renders and
  sheets in `.dev/gate/parts/2026-11-07all`, then `batch_after.sh`): the Blender suite (tonight's lid and detector changes are unverified
  until it), the tools and unit suites, the cheek's last factors (relief, colour mottling, scatter, microrelief), the
  forehead with Ten24's forehead tile. If the base v2 tests pass, rebuild the library's characters (backup first) so
  they carry the lower-lid ledge. The per-part table: `docs/gate/2026-11-07/report.md`, "Late night".
- Running (`scratchpad/batch_face.sh`, log `scratchpad/batch_face.log`):
  the trials above. Before it, `scratchpad/batch_next.sh` (done, log `batch_next.log`):
  `scratchpad/batch_next.sh`, log `scratchpad/batch_next.log`: the library's hair (the nape at the head joint, quiff
  0.8), `factors lidsmooth` on the lower lid, the full smile (`face_smile_full`: mouthSmile + cheekSquint), the hair
  with the library's style, the smile's feasibility (ICT-FaceKit's scanned smile carried onto the gate's man by
  `tools/gate/smile_transfer.py`, rendered with `factors ictsmile` beside HD Aaron's - CPU dry run good, RESEARCH
  §14.7), then the end-of-list run of every suite (the global tests rule; tonight's commits are
  unverified until it), then `factors hairgrey`. The user's 2026-11-07 global rules apply: NOT STANDARD under a go after
  attack passes (logged in the plan §19.3), gaps decided and logged as mine, faults fixed on sight, tests once at the end.
- Proof (2) body relief: hands - Ten24's relief in texture space (`body_scan.py texture ten24`, x1.5 + colour), skins
  and characters rebuilt (backup `.dev/backup/library_2026-11-07`): ridges x3 like for like (still below Aaron's veins);
  feet - no detailed donor until Thunk3D (§19.2 item 25); torso folds 0.53-0.85.
- Proof (3) scalp hair: the bound's gate FAILED for the hair's own reasons (front 0.77x, back 2.05x Cycles under the
  stage light; the image light fixed by ambient x0.45); by the approved rule cards take the live view - how: §19.2 item
  27 (cards baked from our own strands, after the face and body proofs).
- Full suites, 2026-11-07 end: Blender 140 passed, 1 failed, 1 deselected (the AI test); unit 45 passed; tools 18 passed.
  The failure, `test_migrations::test_a_v1_character_comes_in_as_v2_with_its_grooms_in_place`: the brows land 0.50 mm
  off after the v1 -> v2 upgrade against the test's 0.2 mm. Diagnosed 2026-11-07 evening: the migration put them back
  within 0.0005 mm (the log was right - not a unit slip, as I first wrote), then refitted the eyes, whose contact key
  reshapes the lids under the brows' lower hairs; fixed by putting the grooms back after the refit
  (`migrations/v2_base.py`).
- For the user to clean: `C:\.dev\gate\` - ten stray factor renders from my run (a relative path Blender resolved from
  C:\; the removal needs the user's approval).

## Tools and references

- The gate: `tools/gate/parts_gate.py` (render, sheet), `tools/gate/measure.py` (the measures), `tools/gate/
  cc5_bench.py`, `eevee_settings.py`, `relief_tiles.py`; outputs in `.dev/gate/` (not in git).
- HD Aaron: `.dev/gate/cc5_aaron_blender/` (`aaron_hair_{eevee,cycles}.blend`; his maps under `textures/`) - local
  only. CC5's side: memory `cc5-control` (limits in RESEARCH §14.1).

## Coordination

- **web-4c** shares the graphics card: message it before putting work on the card, and "card free" when done. Its
  limits are requests (memory `peer-limits-are-requests`). 2026-11-07: told it just-stage has the card for gate renders.
- **"just-stage asset search"** fetches and searches assets; TASKS and RESEARCH are mine to record from what it sends
  (checked against its logs first).
- **Needs the user:** no emails, no purchases (the user, 2026-11-05).
