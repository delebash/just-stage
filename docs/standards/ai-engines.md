# How the AI engines are reached

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R14, R5. Facts: RESEARCH §7
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

What JustStage uses the engines for (R5, R10): the skin, eye, lip, nail and hair-texture generators' image steps
(Z-Image-Turbo, Qwen-Image, FLUX.2 klein 4B, HiDream-O1 — Apache-2.0/MIT, all run by stable-diffusion.cpp on CPU,
CUDA, Vulkan, Metal — §7), photo-to-head's texture completion, and later motion and lip-sync models through the
same door. Everything geometric (wraps, fits, bakes, rigs) runs inside Blender.

## 2 · The exact service

**The engine host is a family server from the kit's template with the image runtime turned on:
`installLlm({ runtimes: ["sdcpp"], runtimeModels })` in its `server/src/app.js`, run headless by the kit's launcher
(`<app>-server serve`, `app-structure.md` §Q.3).** Concretely:

| When | Host | Why |
|---|---|---|
| From step 1 (the gate) | the kit's own template server, run from source (`npm run server` in `just-core/template`) with `sdcpp` enabled — the server the kit already tests | exists today; no new program; the template is the standard shape |
| When JustDirect exists (R20) | JustDirect's server (`just-direct-server serve`) — the family's 3D-side app, linked to JustStage by the API anyway | one engine host beside JustStage; JustDirect needs the same engines |

**For end users** the host must be a shipped family app: JustDirect. Until it ships, JustStage's generators run only
where a family server runs (the developer's machine); the family releases together (the family rule), so this costs
nothing at release time but must be said: no generator is promised to a user before JustDirect exists.

**Kit gap (being filled in the open `just-core` session — the user, 2026-10-29: "core already has open session which
it is working"):** the kit runs image features in-process (`llm/image_dispatch.js`
`runImageFeature`, used by just-house-paint's own routes) and exposes runtime management over HTTP
(`/v1/ai/runtimes`, `/v1/ai/runtimes/:id/engine/status`, `/v1/ai/runtimes/:id/models`), but **no generic HTTP route
runs an image feature as a job**. JustStage needs one: `POST /v1/ai/image/jobs` (feature key, request) → a kit
`JobRegistry` job (`/v1/jobs/:id`, `/v1/jobs/:id/events`, DELETE to cancel — the kit's standard long-job door,
§19), mounted by `installLlm` when an image runtime is on. This is web-kit work in another repo: a session the user
opens at `E:\Dev\Web\just-core` ([the user's rule: a kit gap is filled in the kit before the app is built on it]).
Until it lands, the gate's generator runs against the template server's existing in-process path by a short script
on that side — a stopgap named as such in TASKS.

## 3 · The client contract (JustStage's side, `juststage.engines`)

| Step | How | Source |
|---|---|---|
| Discovery | host `127.0.0.1`, port from preferences (default: the family registry's port for the host app — the template's `17490`; JustDirect's when registered), overridable headless with `--juststage-engine-host` | the kit's port registry (`app-structure.md` §1; `check-family.js` `APP_PORTS`) |
| Auth | none on loopback by default (the kit's `bearerAuth`: "an empty token list means no auth (the normal local-loopback case)"); a token from preferences when the host requires it | `platform/auth.js` |
| Readiness | `GET /v1/ai/runtimes` → the `sdcpp` row's engine status and models; `imageFeatureReadiness` semantics (engine installed, model present, fits) before a generator offers itself in the UI | `llm/runtimes_api.js`, `image_dispatch.js` |
| Install and models | the host app's own UI (the kit's `LuRuntimeTab`); JustStage links to it and never installs engines itself | §19 |
| Run | `POST /v1/ai/image/jobs` (§2's gap) with the feature key and request → `202` + job id; `GET /v1/jobs/:id/events` (server-sent events) for progress; `DELETE /v1/jobs/:id` to cancel | `platform/jobs_api.js` |
| Results | PNG/EXR bytes returned by the job, written into the character's `textures/` with a `provenance` record (generator, model id, seed, prompt, host version) | [`character-data-model.md`](character-data-model.md) §3.1 |
| Features | JustStage's image features are kit **feature-catalog** rows owned by the host app's seed (`installLlm` `featureCatalog` / `enginePresets` / `featurePresets`, §19): `juststage.skin_albedo`, `juststage.skin_detail`, `juststage.iris`, `juststage.hair_texture`, `juststage.photo_head_complete`; JustStage ships their prompt templates and preset params as data the host's seed includes | §19 "A feature's model and settings" |
| Failure | the kit's error envelope (`ApiError` codes: `engine-not-ready` 503, `provider-unreachable` 502); JustStage shows the host's words and a link to its AI page | `llm/prompts.js` `aiRunHttpError` |

## 4 · The 8 GB rule

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
3. Video (JustDirect's job) never runs while JustStage's viewport is live — the queue rule from §10.

## 5 · Models — labelled, never filtered

The family rule (memory, JustVoice's way): every model the host offers is shown with its licence label and the GPU
vendors it runs on; JustStage's generators pick a default (Apache-2.0 or MIT, every vendor) and let the user choose.
NVIDIA-only optional parts (Audio2Face-3D for lip-sync, UniRig's weight stage) are plugins the user installs, never
core ([`plugins.md`](plugins.md)).
