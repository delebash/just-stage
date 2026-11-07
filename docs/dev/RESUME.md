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
