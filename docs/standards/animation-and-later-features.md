# Animation data, defined now for later — and an extension point for every later feature

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R13, R6, R21 "later". The
> user's rule (TASKS): FX "are things we can add later but we need to be able to add them in the original design".
> Facts: RESEARCH §3 (iClone's timeline and layers), §4 (Cascadeur, Unreal Sequencer), §8.

## 1 · Animation data (R13)

Defined now so an Animate workspace, or Unreal through the plugin, reads and writes the same things.

| Piece | Definition | Storage in `.blend` | Storage out | Standard |
|---|---|---|---|---|
| **Clip** | a named, time-ranged set of curves on one character: bone transforms (role-mapped), face controls (our vocabulary; the ARKit 52 always derivable), slider values, visemes, root motion flag | a Blender **Action** with **slots** (one slot per data-block: armature, body shape keys, face) — "a single Action can animate multiple data-blocks at the same time" (Blender 4.4 release notes, read 2026-10-29) | USD `UsdSkelAnimation` (joints + `blendShapeWeights`); glTF animation (TRS + weights); FBX takes; face controls beyond the 52 as time-sampled attributes of `JustStageTakeAPI` on the animation prim | [Actions and slots](https://docs.blender.org/manual/en/latest/animation/actions.html) |
| **Layer** | an additive or override layer over a clip or a stack of clips, per body part mask (iClone's motion and per-part layers — §3) | **NLA** tracks and strips with blend modes and influence; part masks as bone collections | baked on export (USD/glTF have no layers); the recipe as `customData` on the animation prim | [NLA](https://docs.blender.org/manual/en/latest/editors/nla/index.html) |
| **Timeline** | one scene timeline: frame range, fps, markers, camera switches; later the Animate workspace's own editor over the same data | scene frame range, timeline markers, the camera binding of markers | USD stage `startTimeCode`/`endTimeCode`/`timeCodesPerSecond` | Blender timeline; USD time codes |
| **Pose** | a clip of one frame | a pose asset (Action + asset mark) | USD `UsdSkelAnimation` at one time | Blender pose library (asset browser) |
| **Expression** | a one-frame clip of face controls | the same, on the face slot | the 52 + companion | — |
| **Lip-sync** | viseme weights over time + the text/phoneme alignment that produced them | a clip on the face slot + a `lipsync` PropertyGroup (phonemes, words, times, audio reference) | `JustStageLipsyncAPI` on the animation prim; the 15 visemes baked as `blendShapeWeights` | [`skeleton-and-face.md`](skeleton-and-face.md) §2.2 |
| **Mocap take** | a raw recording (device, fps, calibration) kept separately from the cleaned clip | a clip tagged `take` + a `take` PropertyGroup | `JustStageTakeAPI` on the animation prim | VMC / Live Link ([`skeleton-and-face.md`](skeleton-and-face.md) §4) |
| **Physics / secondary** | cloth, hair, jiggle settings per clip range | modifier settings + the garment's and groom's `sim` attributes | `JustStageGarmentAPI` / `JustStageGroomAPI`; Unreal Chaos settings mapped by the plugin | Blender cloth/hair simulation |
| **Camera** | lens, sensor, transform, clip planes, keyed | Blender camera + Action | USD `UsdGeomCamera`; glTF camera | USD |

Rules: a clip is addressed by `(character_id, clip_id)`; curves are named by the role map and the face vocabulary,
never by a target engine's names; everything in the table exports to Unreal through the plugin as Animation
Sequences, Control Rig poses and Level Sequences, and imports back the same way (§5.2 of
[`import-export.md`](import-export.md)). Time is frames at a stated fps (Blender) and time codes (USD); no tick unit of
our own (iClone's 6,000 ticks a second — §3 — stays iClone's).

## 2 · Every later feature, and where it plugs in

The user's list (TASKS SCOPE, IDEAS) and R21's "later", with the extension point each one already has in this spec:

| Later feature | Reference | Extension point now | What is reserved |
|---|---|---|---|
| **Animate workspace** (iClone's side) | iClone 8's timeline, layers, Motion Director, Curve Editor; Unreal Sequencer; Cascadeur's AutoPosing/AutoPhysics (§3, §4) | §1's data; `register_workspace("Animate")`; commands under `juststage.anim.*` | the `anim` command area; `JustStageLipsyncAPI`, `JustStageTakeAPI` |
| **Scene workspace** (sets, props, lights, cameras, terrain, sky) | iClone's scene features (§3) | USD scene stages referencing packages ([`interchange.md`](interchange.md) §2.3); `register_workspace("Scene")`; `juststage.scene.*` | the `scene` area; the `JustStageSceneAPI` family name |
| **FX** (particles, PopcornFX-type) | iClone's PopcornFX (§3) | Blender geometry-nodes simulation zones in the app; a `JustStageFxAPI` schema family; `register_generator("fx", …)`; `juststage.fx.*` | the family name only, no schema yet |
| **Making clothes from patterns** (Marvelous Designer, Z-Weave, MetaTailor) | §4; ZOZO's Contact Solver (R8) | the reserved `JustStagePatternAPI` family (2D pieces, seams, grading); `juststage.clothes.sew_*` | the family name |
| **Sculpt extras** (layers, morph brushes; ZBrush-level) | ZBrush, Nomad (§4) | Blender sculpt mode + "Save as slider" (R7); multires layers as sliders; a fork trigger if C-level work is needed (R1) | the `sculpt` area |
| **Props** | CC5's props and accessories (§2) | a `JustStagePropAPI` (pivot, attach point = a joint + offset, spring settings) on a Mesh prim, `Props` catalogue; `juststage.props.*` | the family name |
| **Texture painting and baking in app** (Substance-type) | CC5's SkinGen layers, Substance round trip (§2) | the `makeup.<layer>` channels and the master-set bake; Blender's texture paint; `register_generator("texture", …)` | — |
| **Path-traced finals** | Cycles (R15); Unreal's path tracer through the plugin | render presets as commands `juststage.render.*` | the `render` area |
| **Live mocap devices** (Rokoko, Xsens, mocopi, iPhone) | Motion LIVE (§3); VMC and OSC (§7) | `register_capture_source(kind, cls)` on the VMC/OSC and Live Link receivers | — |
| **Crowds, Motion Director-type control, AI motion** | iClone 8.4 crowds, Motion Director (§3); MoMask-type models (§7) | clips + the engine host's job door ([`ai-engines.md`](ai-engines.md)) | — |
| **JustDirect inside the system** / "AI makes the movie" | IDEAS; R20 | the API door; scene stages and render passes as JustDirect's inputs | — |
| **A Blender fork** | R1's trigger (viewport C work, GPU skinning, a timeline editor) | the application template already owns the UI; a fork replaces the host, not the extension | — |

## 3 · The mechanisms every extension point rests on

1. **Versioned USD schema families** — a new feature is a new `JustStage<Feature>API_1`, never a change to an
   existing family ([`interchange.md`](interchange.md) §2.2); small records go in `customData` under a reverse-DNS key,
   preserved by every USD reader ([`character-data-model.md`](character-data-model.md) §6).
2. **Plugin schemas** — a plugin ships its own `schema.usda` and registers it (`juststage.api.register_usd_schema`),
   so its data travels in the package like ours ([`plugins.md`](plugins.md) §3).
3. **Command areas** — a new feature is a new `juststage.<area>` with its own schemas, permission group and MCP tool
   group ([`commands-and-api.md`](commands-and-api.md) §2, §4).
4. **Registries** — generators, importers, exporters, materials, workspaces, capture sources, slider groups
   ([`plugins.md`](plugins.md) §3).
5. **Workspaces** — Blender's own; the template adds one per feature (R6: Body, Head & Face, Skin & Materials, Hair,
   Clothes, Rig & Expressions, Import / Export now; Scene and Animate later).
6. **The scorecard** — every later feature already has rows in [`parity-scorecard.md`](parity-scorecard.md) marked
   `later`, so the floor and the order are visible from day one.
