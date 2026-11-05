@AGENTS.md

## For Claude

- `AGENTS.md` (imported above) holds this repo's instructions; this file adds only what is Claude
  Code's own. Keep both short: conventions and pointers, never tasks or status.
- Before researching anything, read the subject's section of `docs/dev/RESEARCH.md`; new facts land
  there in the same change.
- A decision goes into `docs/dev/TASKS.md` as the exact text the user approved.
- Sessions for this family open at `E:\Dev\3D`.
- After a compaction, on "re-read docs" and at every session start: read `docs/dev/RESUME.md` and every file it lists
  for the active job before any tool call (a SessionStart hook loads it); keep it current in the same commit as the work.
- `.claude/settings.local.json` is this machine's and never committed.
