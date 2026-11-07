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

- 2026-11-07: the plan checked and corrected; RESEARCH an index by topic (§14.1-14.15); this file cut to a pointer.
- Gate tools (§20 step 1): `tools/gate/measure.py` (standard measures, windows set by looking), `measure_table.py`,
  `factors.py` (one factor at a time, trial settings `pores*k+micro*k+relief*k`, `handspart*k` / `handspartc*k` in the
  shader); `quality-gate.md` brought to the bar. Baselines `.dev/gate/parts/2026-11-07a` (both engines), `-07b` (face
  after the fix). Report: `docs/gate/2026-11-07/report.md`.
- Proof (1) face relief: EEVEE cheek within HD Aaron's bands after pores x1.15 / microrelief x1.35 (`make_face_regions`)
  except the folds (0.76); forehead equal. Cycles ~0.55 of his Cycles build - the question of which build is the bar is
  the plan's §19.2 item 26. Next on the face: the microrelief's look (regular cells against his directional furrows -
  a direction field per region), the cheek's folds.
- Proof (2) body relief: Ten24's hands in texture space (`body_scan.py texture ten24`, x1.5 + colour) - back of the
  hand form 1.24 (equal), ridges 0.74-0.80 (below). Library backed up (`.dev/backup/library_2026-11-07`); the scan skins
  rebuilt (`rebuild_scan_skins.py build`) - next: the hand view rendered with the rebuilt skin (`parts_gate --skin`),
  then the characters (`build_library`). Feet: no detailed donor until Thunk3D's "Leg-foot" (§19.2 item 25).
- Fixes done: `test_body`; the oiliness link; no pores on lips / lining. Full suites not yet run (at the end).
- Clock: the hair bound (Q-HAIR-7) runs to 2026-11-08 09:37 - the scalp proof is third.

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
