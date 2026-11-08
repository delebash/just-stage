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

## The active job: THE PLAN - read in full

- **`docs/plans/2026-11-06-the-plan.md`** - the final method per part, its status and its gate measure; §19 the
  decisions (19.1 taken under the user's go of 2026-11-07, 19.2 waiting for the user - nothing stops for them); §20
  the build order. Checked claim by claim by four independent readers 2026-11-07 (`.dev/audit/2026-11-07/CHECK-A.md`
  to `CHECK-D.md`).
- TASKS' first entry (THE DEEP READ, THEN ONE PLAN - with the user's words of 2026-11-07).
- RESEARCH.md §14 (the character, part by part: 14.N = the plan's §N) for the part being worked on.

### Where it stands (update after every step)

- **THE USER, 2026-11-08 (TASKS "UNTIL A VERDICT ON EVERY PART"): no stopping - after turns and compactions - until
  every part and the whole body has a verdict (meets HD Aaron or provably can't); then on to the app's other features.
  Decisions attacked to consensus and kept (changed only on a new measured fact, shown). After a compaction: read this
  file, the plan's §18a and §19.3 and `docs/gate/2026-11-07/report.md` first; keep a background job running.**
- **Wake-ups (session-only, set 2026-11-08 ~00:40, expire after 7 days or with the session - set them again with
  CronCreate):** every 20 min when idle, resume the verdict work from these docs; every 3 h, remind every peer session
  of the shared rules (the user: "they can help keep you on task").

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
