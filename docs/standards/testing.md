# Testing standards for AI agents

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R16. Facts: RESEARCH §6
> (Blender headless, `gpu.init()` in 5.2, lavapipe, GitHub's macOS runner; Blender's own render tests), §8 pass 2
> (operator rules), §11 (PhotoCraft: "Every change comes with tests"). The family rule (memory): every app is built
> by AI agents and the human only does limited testing — so the tests are the eyes.

## 1 · The rules

1. **Every change comes with its test** (PhotoCraft's golden rule, §11). While building: only the change's own test;
   the full suites once at the end of a list (the user's rule, global CLAUDE.md).
2. **A command is tested through its schema**: each command has at least one test that runs it headless from JSON
   parameters and checks `returns` and the data it changed. No test drives the UI to do what a command can do.
3. **Tests run on the user's real app and real data shapes**: the sample characters in `tests/data/` are real
   JustStage packages (the gate head among them), not toys.
4. **Golden images decide looks**; a human decides the quality bar ([`quality-gate.md`](quality-gate.md)).
5. **Red, then green**: a test is written to fail first (the family's test-driven rule).

## 2 · Levels

| Level | What | How | Standard |
|---|---|---|---|
| **Unit** (pure Python, no Blender) | schema generation from `schema.usda`, migrations, wraps, retarget maps, the sidecar generator, the MCP tool generator | `pytest` on plain CPython with Pixar's `usd-core` wheel (PyPI, 26.11, TOST licence — read 2026-10-29); the `juststage` package keeps Blender-free modules importable without `bpy` | [pytest](https://docs.pytest.org/), [usd-core](https://pypi.org/project/usd-core/) |
| **Command** (headless Blender) | every command from JSON params; undo/redo after it; `poll` messages; the USD hook round trip (export → import → equal) | **one runner**: `blender -b --python tests/run.py` calls `pytest.main()` inside Blender's Python (pytest installed as a dev wheel); `gpu.init()` for GPU-needing commands (5.2) | [pytest](https://docs.pytest.org/) inside Blender's interpreter |
| **Golden image** | EEVEE and Cycles renders of the sample characters at fixed camera, light, resolution | Blender's `render_report.py` method: render, compare with `oiiotool` thresholds, an HTML report of diffs (§6); per-renderer and per-platform reference folders | Blender's own render tests |
| **Round trip** | every export preset into its target and back | Blender → Godot (glTF, Godot headless `--import`), → Blender (USD, FBX, glTF re-import), → Unreal (the plugin's Automation tests on a machine with Unreal — the user's at first), → Unity (when installed), diffs on vertex positions, weights, morph names, bone names, texture checksums | each target's own headless import |
| **API contract** | JSON-RPC and MCP: `server/discover`, `tools/list` deterministic, every tool's schema validates, permission groups refuse what they should, the Python tool stays off | the MCP SDK's test client over stdio; HTTP transport tests | MCP 2026-07-28 |
| **UI** | the template's workspaces open, panels draw, the menus exist | `blender --python` with `bpy.ops.screen.screenshot` compared as golden images; `bl_ui` class presence checks | Blender screenshots (R16) |
| **Migration** | one frozen sample file per `schema_version` loads and matches the current form | fixtures in `tests/data/versions/` | Blender's versioning tests pattern |
| **Scorecard** | the floor never drops | a test counts `done` rows against `scorecard.json`'s floor | PhotoCraft's parity scorecard |
| **Licence and provenance** | every shipped asset and model row carries a licence label; no asset without provenance reaches a library | a data check over `data/` and the sample packages | REUSE (§6 of [`README.md`](README.md)) |

## 3 · Platforms and CI

- CI: GitHub Actions, **manual runs only** (the user's rule: nothing builds by itself) — `workflow_dispatch`.
  Matrix: `ubuntu-latest` (Mesa lavapipe for Vulkan/EEVEE headless, Cycles CPU), `windows-latest` (lavapipe for
  Vulkan, WARP for D3D12 where used), `macos-14` (Metal; the runner GitHub provides — §6 pass 2). Blender is
  downloaded per run from blender.org (the version pinned in `pyproject.toml`).
- GPU-vendor coverage: the user's RTX 2070 Super is the measured machine (RESEARCH §1); AMD and Apple results come
  from CI's software rasterizers and the macOS runner until real hardware is at hand — stated on every golden folder.
- Unreal tests run where Unreal is installed (the user's machine, `E:\Dev\Unreal` projects — §1); CI marks them
  skipped, never green by omission.

## 4 · Fixtures and data

- `tests/data/packages/`: the gate head and body; one character per import source (a CC5 export the user makes,
  a Daz bridge export, a MetaHuman DCC export, a VRM) — **the user's own exports**, checked in only where their
  terms allow, otherwise referenced by path from a local folder the test reads (Daz's and Reallusion's terms bar
  redistribution — [`import-export.md`](import-export.md) §2).
- `tests/data/golden/<renderer>/<platform>/`: reference images with the command line that made them.
- `tests/data/versions/v<N>/`: frozen files per schema version.

## 5 · Tools and style

- Python: `ruff` (lint and format), type hints on the public API, `pyproject.toml` at the root; Blender's Python
  version is the extension's floor. Standard: [Ruff](https://docs.astral.sh/ruff/).
- Compiled parts (OpenRigLogic bindings, ufbx-write, later Jolt): CMake, shipped as **platform wheels** in the
  extension manifest (Blender's wheel mechanism — §8 pass 2); a wheel per `platforms` entry.
- Unreal plugin: Unreal's Automation framework for tests; `clang-format` with Epic's style.
- Commit messages name the command or schema they touch; a schema change without a migration test fails CI.

## 6 · What an agent runs

```
# the change's own test, red then green
blender -b --python tests/run.py -- -k body_set_slider
# once per list, the full suites
pytest tests/unit && blender -b --python tests/run.py && node tests/roundtrip/godot.js
# golden images (slow): only when a shader, generator or renderer setting changed
blender -b --python tests/golden/run.py -- --renderer eevee
```
