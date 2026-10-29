# Brief for the standards-spec session (Fable 5.1)

Written 2026-10-29 by the research session, after the user approved the rec list, version 2 ("go your rec all").
The approved working method (TASKS, "Model"): "The synthesis and the standards spec run in a fresh session on Fable
that reads RESEARCH.md and TASKS.md." This session is that one.

## How to start it (the user)

Open a terminal at `E:\Dev\3D`, run `claude`, choose Fable (`/model`) at xhigh effort, and paste:

`go: write JustStage's synthesis and standards spec — read E:\Dev\3D\just-stage\docs\plans\2026-10-29-standards-spec-brief.md first`

## Read first, in this order

1. `just-stage/AGENTS.md`, `CLAUDE.md` and `docs/dev/README.md` — the repo's rules: clean-room, standards before code,
   decisions verbatim in TASKS, facts in RESEARCH with their proof.
2. `docs/dev/TASKS.md` — every decision in the user's exact words, the SCOPE and its requirements.
3. `docs/plans/2026-10-29-recs.md` — the approved rec list, version 2 (R1–R21). These are decided; don't re-open
   them. Version 1 is in git (`64f47a4`) for history only.
4. `docs/dev/RESEARCH.md` — the facts, by subject, each with how it was checked; the notes it links in `docs/plans/`
   (round one and the second pass) hold the detail. Don't re-derive what is there.

## What to write

- **The synthesis** — what JustStage is and why it is built this way, from the approved recs: the product (a character
  creator at CC5 / MetaHuman quality or better, in Blender as an extension and app template, with an open Unreal
  plugin), its scope now and later, and the reasons with their evidence. The repo's convention names `PRD.md` (what the
  app is for) and `ARCHITECTURE.md` (why it is built the way it is) as the docs that come after the research
  (`docs/dev/README.md`).
- **The standards spec** — specified and approved before any code (AGENTS.md). At least:
  - the character data model: the base (hm08 at subdivision 0, two levels, the wrapped shape spaces), morphs and
    sliders, materials and texture sets (CC5-compatible UDIM layout and MetaHuman's set), hair, clothes, rig and face
    rig, with versioning so older files keep loading;
  - the skeleton and face standards and every mapping table (R18);
  - interchange: USD, glTF + VRM, FBX in and out, and the companion files for correctives (R17);
  - the command and API layer: operators, one JSON Schema per command, the MCP server and its permissions (R19);
  - the plugin contract: Blender extensions in process, the API for outside programs (R19, R2);
  - the import and export rules for CC5, Daz, MetaHuman, VRM and Unreal (R11, R12), including the Unreal plugin's
    contract and its keep-animation rule;
  - animation data defined now for later (clips, layers, timeline, USD animation — R13), and an extension point for
    every later feature (FX and the rest — the user's rule);
  - how the AI engines are reached (R14) — name the exact service;
  - testing standards for AI agents (R16);
  - the quality gate's procedure (R3);
  - the parity scorecard against CC5's inventory (RESEARCH §2), with a floor that only rises;
  - the 3D family's "one way per job" table (the user's global rule: "In the 3D family (E:\Dev\3D) the table is the one
    JustStage's standards spec creates").
- Each piece names the standard it follows with its doc link, or is marked **NOT STANDARD** with the standard option
  and the trade-off — and a NOT STANDARD piece waits for the user's word on that piece by name.

## Rules that apply here (from the user's global instructions)

- Unsure, or the approved decision leaves a gap — a word, a label, a behaviour — stop and ask the user; never fill it
  with your own choice. Every rec is argued against before it is shown.
- The spec is shown to the user and approved before any code; the approval goes into TASKS verbatim.
- Save results as they arrive; commit as you go.
