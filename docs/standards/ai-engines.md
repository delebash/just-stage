# How the AI engines are reached

> **Status: APPROVED recs, written 2026-10-29** (the review's items 14, 15, 24, 25 — TASKS; review file
> [`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md)). R14, R5. Facts: RESEARCH §7
> (S10: the image models and stable-diffusion.cpp), §10 (the web kit's engines and the 8 GB card), and the kit's code
> read by this session 2026-10-29 (`just-core/packages/core/src/runner/`, `llm/runtimes_api.js`, `llm/image_dispatch.js`,
> `platform/auth.js`; `docs/app-structure.md` §Q.3 and §19).

## 1 · The rule (R14)

JustStage never starts an AI engine itself. It calls **the family's engines as a local service**: a family server
built on the web kit, whose `RuntimeService` installs, starts, books memory for and runs jobs on stable-diffusion.cpp
(`sdcpp`), llama.cpp (`llamacpp`), the ONNX runtime (`onnx`) and audio.cpp (`audiocpp`) — the kit's `RUNTIMES`
table (`runner/runtimes.js`), sharing the family's model cache (`runner/models.js`, the Hugging Face cache layout) and
its VRAM arbiter (`runner/arbiter.js`). Standard: our own existing code — the kit's one way to run another engine
(`app-structure.md` §19: "Another engine (sd.cpp, …) → `runner/runtimes.js` `RUNTIMES` + `runner/runtime_service.js`
`RuntimeService` … never an app's own engine code").

**One way to add an AI feature** (item 25; the user: "we are definitly adding lots of good ai features to this app like
cc5 and we will come of with more"): every AI feature is a **command** ([`commands-and-api.md`](commands-and-api.md))
that runs as a **job** on JustStage's engine host (§2), on an engine the family kit runs — llama.cpp (text),
stable-diffusion.cpp (images, video), ONNX Runtime (the kit's `onnx` runtime: kind "vision", `inProcess: true`, in the
host's own process), audio.cpp (speech both ways) (`runner/runtimes.js`, §10). A feature that needs a new engine program
— skin-tokens.cpp for auto-rigging, trellis.cpp for image-to-3D (§5, §7) — gets it added to the kit first, in the
just-core session on the user's word, so every family app can use it. Because every feature is a command, assistants
can call it too: describing a person and getting the character (IDEAS.md) is a text model choosing slider values
through those commands. **The one exception is live capture** (webcam face and body every frame): a stream, not a job,
so it runs inside Blender ([`skeleton-and-face.md`](skeleton-and-face.md) §4).

What JustStage uses the engines for first (R5, R10): the skin, eye, lip, nail and hair-texture generators' image steps
(Z-Image-Turbo, Qwen-Image, FLUX.2 klein 4B, HiDream-O1 — Apache-2.0/MIT, all run by stable-diffusion.cpp on CPU,
CUDA, Vulkan, Metal — §7) and photo-to-head's texture completion. Everything geometric (wraps, fits, bakes, rigs) runs
inside Blender.

## 2 · The exact service

**JustStage ships its own engine host** (item 14) — **JustStage's server**, `server/` in this repo, in the template's shape (the folder every family app's server has; the generator's names for JustStage — package `just-stage-server`, `JUST_STAGE_*` settings, product `JustStage`, one version with the app; the template's server tests, `biome.json` and root `server`/`test:server`/`lint` scripts as an npm workspace): the kit template's server copied by hand (the kit's generator places apps beside the kit only — `new-app.js` `repointKitPaths`), port 17481; started by `juststage.engines` when it isn't running. As written first: a server-only family package from the kit's template with the
runtimes its features need turned on — `installLlm({ runtimes: ["sdcpp", …], runtimeModels })` in its
`server/src/app.js`, run headless by the kit's launcher (`<app>-server serve`, `app-structure.md` §Q.3) — shipped in
JustStage's installer with its Node runtime ([`plugins.md`](plugins.md) §5) and started by the extension when a
generator first runs. **When JustDirect exists (R20), it uses the same host** instead of starting its own, so a machine
runs one host and one arbiter. Its port is registered in the kit's family registry when the package is created (the
kit's rule). (The stand-in first written here — the template's own server with `sdcpp` on — couldn't run: the template turns no engine on.)

**The image-job route — the kit gap, filled 2026-10-29** (item 15: requested of the `core` session; shipped on
just-core's main, `333ac9e3` "… an image feature over HTTP", read in `packages/core/src/llm/image_jobs_api.js`):
`makeImageJobsRouter(jobs, { resultDir })` from `@delebash/core/llm`, running on the app's `JobRegistry` beside
`makeJobsRouter`; the template mounts both, so a host built from the template has them (the core session's report).
No stopgap is needed.

## 3 · The client contract (JustStage's side, `juststage.engines`)

| Step | How | Source |
|---|---|---|
| Discovery | host `127.0.0.1`, port from preferences (default: the family registry's port for JustStage's host — the template's `17490` while the template stands in), overridable headless with `--juststage-engine-host` | the kit's port registry (`app-structure.md` §1; `check-family.js` `APP_PORTS`) |
| Auth | none on loopback by default (the kit's `bearerAuth`: "an empty token list means no auth (the normal local-loopback case)"); a token from preferences when the host requires it. The route runs under the kit's usual `/v1` checks: the CSRF check rejects only a request whose `Origin` header is present and not allowed, and resource isolation passes a request with no `Sec-Fetch-Site` — so Blender's Python client, which sends neither, passes | `platform/auth.js`, `platform/csrf.js` |
| Readiness | `GET /v1/ai/runtimes` → the `sdcpp` row's engine status and models before a generator offers itself in the UI; a feature that can't run yet is refused at submit with `409` problem+json naming its `need` — `engine-not-installed`, `model-not-downloaded`, `engine-cant-run-here`, `engine-not-on` or `model-unknown` — and nothing starts | `llm/runtimes_api.js`, `llm/image_jobs_api.js` |
| Install and models | the host's own AI page (the kit's `LuRuntimeTab`); JustStage opens it and never installs engines itself; models download on demand | §19 |
| Run | `POST /v1/ai/image/jobs` with `{feature, request: {prompt?, width?, height?, seed?, init?, mask?, refs?}}` (sizes 64–4096; pictures in as base64 PNG) → `202` with the job snapshot `{id, kind: "image", state, progress, …}`; `GET /v1/jobs/:id` or `GET /v1/jobs/:id/events` (server-sent events) for progress; `DELETE /v1/jobs/:id` to cancel | `llm/image_jobs_api.js`, `platform/jobs_api.js` |
| Results | `GET /v1/ai/image/jobs/:id/result` → the PNG (`image/png`), **once** — then the job is forgotten and its file deleted (a repeat gets `410`); `409 job-running` before it's done, `409 job-error` / `job-cancelled` for a failed or cancelled job; an unfetched picture goes with its job after 10 minutes. **PNG only** (`runImageFeature` returns PNG): a channel that needs float (`displacement`) is converted to EXR inside Blender, at the precision the model produced. Written into the character's `textures/` with a provenance record in the `juststage` `customData` (generator preset, model id, seed, prompt, host version) | `llm/image_jobs_api.js`; [`character-data-model.md`](character-data-model.md) §3.1 |
| Features | JustStage's image features are kit **feature-catalog** rows owned by the host app's seed (`installLlm` `featureCatalog` / `enginePresets` / `featurePresets`, §19): `juststage.skin_albedo`, `juststage.skin_detail`, `juststage.iris`, `juststage.hair_texture`, `juststage.photo_head_complete`; JustStage ships their prompt templates and preset params as data the host's seed includes | §19 "A feature's model and settings" |
| Failure | the kit's error envelope (`ApiError` codes: `engine-not-ready` 503, `provider-unreachable` 502); JustStage shows the host's words and a link to its AI page | `llm/prompts.js` `aiRunHttpError` |

## 4 · The 8 GB rule

Two apps sharing the card is the user's to manage, not the apps' (the user, 2026-10-29: "i dont care about two apps
managinemment memory that is uyser responsibliyt"); the rules below are JustStage's own load beside its own jobs.

The kit's arbiter is **in-process**: "each app process holds its OWN instance (cross-APP arbitration is out of scope,
design §7.2)" (`arbiter.js`). Blender's own VRAM (EEVEE, textures, Cycles) is not booked anywhere, and a local video
clip alone takes 7.3 GB of the card (§10). Rules:

1. Image jobs are **queued jobs**, never interactive; the UI says "generating on the family engine" with the host's
   progress.
2. Before a job, JustStage drops its own load: viewport texture limit to 2K (Blender's *Texture Limit* preference),
   Cycles previews paused; after the job, restored. Measured at the gate: the peak VRAM of Z-Image-Turbo under
   sd.cpp beside a JustStage head in EEVEE on the 2070 Super, recorded in RESEARCH §1 and in
   [`quality-gate.md`](quality-gate.md); if it doesn't fit, generation runs with the viewport in Solid mode (the
   measured fallback), and the spec is updated with the numbers.

## 5 · Models — labelled, never filtered

The family rule (memory, JustVoice's way): every model the host offers is shown with its licence label and the GPU
vendors it runs on; JustStage's generators pick a default (Apache-2.0 or MIT, every vendor) and let the user choose.
NVIDIA-only optional parts (Audio2Face-3D for lip-sync, UniRig's weight stage) are plugins the user installs, never
core ([`plugins.md`](plugins.md)).
