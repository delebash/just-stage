# JustStage — instructions for any AI working in this repo

A free 3D app for characters, scenes and animation: what Reallusion's Character Creator 5 and iClone do,
with their plugins' features built in, plugins of its own, and an API users connect to. Planned — no code
yet. The research comes first, then the standards spec, then code (`docs/dev/TASKS.md`).

## Rules for this repo

- **Not the web family.** The web kit (`E:\Dev\Web\just-core`), its template, its family rules and
  `/new-just-app` don't apply here. The stack — languages, engine, editor — comes out of the research;
  nothing is assumed (C++, Rust, Python, .NET or other).
- **Clean-room.** CC5, iClone and every reference app are studied for behaviour and public docs only.
  Never copy their code, shaders, base meshes, morphs or content — we build it ourselves. The one
  exception, the user's word 2026-10-30: Reallusion's texture files may be used where they are free and
  open source (their own terms read first). Our names never use "Character Creator", "iClone" or
  "Reallusion".
- **Standards before code.** The data model, the command API, the plugin contract and the file format
  are specified and approved before any code is written.
- **A fork is brought up to date before we work on it.** Before any work on a fork this app keeps,
  merge its upstream into our branch, build it, and test the merged build in this app on its real data
  — then start the work. (The user, 2026-10-29, for every app's forks: "before we do any work on audio
  cpp nextime we should update the fork and test it in our app … this should be true for any forks for
  futre apps that we may use".)
- **Decisions and facts are written down as they happen.** A decision goes into `docs/dev/TASKS.md` as
  the exact text the user approved; a researched fact goes into `docs/dev/RESEARCH.md` in the same change.

## Docs

`docs/dev/README.md` is the start: the read order of `TASKS.md` (open work), `RESEARCH.md` (what is
known, with proof) and `IDEAS.md` (unscheduled ideas).
