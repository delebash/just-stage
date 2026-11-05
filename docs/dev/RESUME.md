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
part: proved / not proved / disproved. Proved so far: skin fine detail only.

## Always

- `AGENTS.md` and `CLAUDE.md` (loaded automatically), `docs/dev/README.md` (the doc map: TASKS, RESEARCH, IDEAS,
  PRD, ARCHITECTURE, `docs/standards/` — the standards govern; TASKS records the user's decisions verbatim).
- `docs/standards/README.md` §1 (which standard covers what) and §3 (one way per job): **a job's governing standard
  is read before its plan** (the user, 2026-11-05: "it was already part of the standard to match each part").
- Memory: the index (loaded automatically) and `search-mistakes` before any search, rec or plan.

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
