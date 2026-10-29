# Animation data, defined now for later — and an extension point for every later feature

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R13, R6, R21 "later". The
> user's rule (TASKS): FX "are things we can add later but we need to be able to add them in the original design".
> Facts: RESEARCH §3 (iClone's timeline and layers), §4 (Cascadeur, Unreal Sequencer), §8.

## 1 · Animation data (R13)

Defined now so an Animate workspace, or Unreal through the plugin, reads and writes the same things.

| Piece | Definition | Storage in `.blend` | Storage out | Standard |
|---|---|---|---|---|
| **Clip** | a named, time-ranged set of curves on one character: bone transforms (role-mapped), face controls (our vocabulary; the ARKit 52 always derivable), slider values, visemes, root motion flag | a Blender **Action** with **slots** (one slot per data-block: armature, body shape keys, face) | USD `UsdSkelAnimation` (joints + `blendShapeWeights`); glTF animation (TRS + weights); FBX takes; face controls beyond the 52 in the companion `clips[]` | [Actions and slots](https://docs.blender.org/manual/en/latest/animation/actions.html) (slotted Actions since Blender 4.4) |
| **Layer** | an additive or override layer over a clip or a stack of clips, per body part mask (iClone's motion and per-part layers — §3) | **NLA** tracks and strips with blend modes and influence; part masks as bone collections | baked on export (USD/glTF have no layers; a `layers[]` record keeps the recipe) | [NLA](https://docs.blender.org/manual/en/latest/editors/nla/index.html) |
| **Timeline** | one scene timeline: frame range, fps, markers, camera switches; later the Animate workspace's own editor over the same data | scene frame range, timeline markers, the camera binding of markers | USD stage `startTimeCode`/`endTimeCode`/`timeCodesPerSecond` | Blender timeline; USD time codes |
| **Pose** | a clip of one frame | a pose asset (Action + asset mark) | USD `UsdSkelAnimation` at one time | Blender pose library (asset browser) |
| **Expression** | a one-frame clip of face controls | the same, on the face slot | the 52 + companion | — |
| **Lip-sync** | viseme weights over time + the text/phoneme alignment that produced them | a clip on the face slot + `lipsync` record (phonemes, words, times, audio reference) | companion `lipsync[]`; the 15 visemes baked as curves | [`skeleton-and-face.md`](skeleton-and-face.md) §2.2 |
| **Mocap take** | a raw recording (device, fps, calibration) kept separately from the cleaned clip | a clip tagged `take` + a `takes[]` record | companion | VMC / Live Link ([`skeleton-and-face.md`](skeleton-and-face.md) §4) |
| **Physics / secondary** | cloth, hair, jiggle settings per clip range | modifier settings + `sim` records | companion; Unreal Chaos settings mapped by the plugin | Blender cloth/hair simulation |
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
| **Animate workspace** (iClone's side) | iClone 8's timeline, layers, Motion Director, Curve Editor; Unreal Sequencer; Cascadeur's AutoPosing/AutoPhysics (§3, §4) | §1's data; `register_workspace("Animate")`; commands under `juststage.anim.*` | the `anim` command area; `clips[]`, `layers[]`, `takes[]` in the JSON |
| **Scene workspace** (sets, props, lights, cameras, terrain, sky) | iClone's scene features (§3) | USD scene stages referencing packages ([`interchange.md`](interchange.md) §2.3); `register_workspace("Scene")`; `juststage.scene.*` | the `scene` area; `JustStageSceneAPI_1` family name |
| **FX** (particles, PopcornFX-type) | iClone's PopcornFX (§3) | Blender geometry-nodes simulation zones in the app; a `JustStageFxAPI_1` schema family and `extensions["org.juststage.fx"]`; `register_generator("fx", …)`; `juststage.fx.*` | names only, no schema yet |
| **Making clothes from patterns** (Marvelous Designer, Z-Weave, MetaTailor) | §4; ZOZO's Contact Solver (R8) | the garment record's reserved `pattern` field (2D pieces, seams, grading); `juststage.clothes.sew_*` | `pattern` in the garment schema |
| **Sculpt extras** (layers, morph brushes; ZBrush-level) | ZBrush, Nomad (§4) | Blender sculpt mode + "Save as slider" (R7); multires layers as sliders; a fork trigger if C-level work is needed (R1) | the `sculpt` area |
| **Props** | CC5's props and accessories (§2) | a `prop` record (mesh, pivot, attach point = a bone + offset, spring settings), `Props` catalogue; `juststage.props.*` | `props[]` in the JSON |
| **Texture painting and baking in app** (Substance-type) | CC5's SkinGen layers, Substance round trip (§2) | the `makeup.<layer>` channels and the master-set bake; Blender's texture paint; `register_generator("texture", …)` | — |
| **Path-traced finals** | Cycles (R15); Unreal's path tracer through the plugin | render presets as commands `juststage.render.*` | the `render` area |
| **Live mocap devices** (Rokoko, Xsens, mocopi, iPhone) | Motion LIVE (§3); VMC and OSC (§7) | `register_capture_source(kind, cls)` on the VMC/OSC and Live Link receivers | — |
| **Crowds, Motion Director-type control, AI motion** | iClone 8.4 crowds, Motion Director (§3); MoMask-type models (§7) | clips + the engine host's job door ([`ai-engines.md`](ai-engines.md)) | — |
| **JustDirect inside the system** / "AI makes the movie" | IDEAS; R20 | the API door; scene stages and render passes as JustDirect's inputs | — |
| **A Blender fork** | R1's trigger (viewport C work, GPU skinning, a timeline editor) | the application template already owns the UI; a fork replaces the host, not the extension | — |

## 3 · The mechanisms every extension point rests on

1. **Namespaced extensions in the data** — `extensions[<reverse-DNS>]` on the character JSON, each with its own
   version, preserved when unknown ([`character-data-model.md`](character-data-model.md) §6).
2. **Versioned USD schema families** — a new feature is a new `JustStage<Feature>API_1`, never a change to an
   existing family ([`interchange.md`](interchange.md) §2.2).
3. **Command areas** — a new feature is a new `juststage.<area>` with its own schemas, permission group and MCP tool
   group ([`commands-and-api.md`](commands-and-api.md) §2, §4).
4. **Registries** — generators, importers, exporters, materials, workspaces, capture sources, slider groups
   ([`plugins.md`](plugins.md) §3).
5. **Workspaces** — Blender's own; the template adds one per feature (R6: Body, Head & Face, Skin & Materials, Hair,
   Clothes, Rig & Expressions, Import / Export now; Scene and Animate later).
6. **The scorecard** — every later feature already has rows in [`parity-scorecard.md`](parity-scorecard.md) marked
   `later`, so the floor and the order are visible from day one.
