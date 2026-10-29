# Animation data, defined now for later — and an extension point for every later feature

> **Status: APPROVED recs, written 2026-10-29** (the review's items 6, 22, 25, 26, 27 — TASKS; review file
> [`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md)). R13, R6, R21 "later". The
> user's rule (TASKS): FX "are things we can add later but we need to be able to add them in the original design".
> Facts: RESEARCH §3 (iClone's timeline and layers), §4 (Cascadeur, Unreal Sequencer), §8.

## 1 · Animation data (R13)

Defined now so an Animate workspace, or Unreal through the plugin, reads and writes the same things.

| Piece | Definition | Storage in `.blend` | Storage out | Standard |
|---|---|---|---|---|
| **Clip** | a named, time-ranged set of curves on one character: bone transforms (role-mapped), face controls (MetaHuman's names; the ARKit 52 always derivable), slider values, visemes, root-motion flag | a Blender **Action** with **slots** (one slot per data-block: armature, body shape keys, face) — "a single Action can animate multiple data-blocks at the same time" (Blender 4.4 notes) | USD `UsdSkelAnimation` (joints + `blendShapeWeights`, the rigs' results resolved); glTF animation (TRS + morph weights); FBX takes; to Unreal, face curves by the GUI control names | [Actions and slots](https://docs.blender.org/manual/en/5.3/animation/actions.html) |
| **Layer** | an additive or override layer over a clip or a stack of clips, per body-part mask (iClone's motion and per-part layers — §3) | **NLA** tracks and strips with blend modes and influence; part masks as bone collections | baked on export (USD and glTF have no layers) | [NLA](https://docs.blender.org/manual/en/5.3/editors/nla/index.html) |
| **Timeline** | one scene timeline: frame range, fps, markers, camera switches | scene frame range, timeline markers, the camera binding of markers | USD stage `startTimeCode`/`endTimeCode`/`timeCodesPerSecond` | Blender timeline; USD time codes |
| **Pose** | a clip of one frame | a pose asset (Action + asset mark) | USD `UsdSkelAnimation` at one time | Blender pose library (asset browser) |
| **Expression** | a one-frame clip of face controls | the same, on the face slot; MPFB2's expression JSON on import and export | the 52 as blend-shape weights | MPFB2 [`expression.md`](https://github.com/makehumancommunity/mpfb2/blob/master/docs/fileformats/expression.md) |
| **Lip-sync** | viseme weights over time + the text/phoneme alignment that produced them | a clip on the face slot + a `lipsync` PropertyGroup (phonemes, words, times, audio reference) | the 15 visemes baked as `blendShapeWeights`; the audio as a `UsdMediaSpatialAudio` prim, linked by `juststage:audio` (N1) | [`skeleton-and-face.md`](skeleton-and-face.md) §2.2; [UsdMedia](https://openusd.org/release/api/usd_media_page_front.html) |
| **Mocap take** | a raw recording (device, fps, calibration) kept separately from the cleaned clip | a clip tagged `take` + a `take` PropertyGroup | a `UsdSkelAnimation`; its audio by `juststage:audio` | [`skeleton-and-face.md`](skeleton-and-face.md) §4 |
| **Physics / secondary** | cloth, hair, jiggle settings per clip range | modifier settings + the garment's cloth settings and the groom's hair node inputs | the garment's `juststage:cloth:*`; Unreal Chaos settings mapped by the plugin | Blender cloth and hair simulation |
| **Camera** | lens, sensor, transform, clip planes, keyed | Blender camera + Action | USD `UsdGeomCamera`; glTF camera | USD |

**Starter motions** (item 28): Mesh2Motion's CC0 animations (over 170, for humans and its creature rigs) are the first
clips in the library — the creature ones play on creatures rigged from Mesh2Motion's rigs; the human ones are retargeted
onto the UE5 skeleton by `import.characterise` and checked by eye before they ship. Each carries its licence label
(Mesh2Motion's site says some human animations come from Quaternius; the repository says all its art is CC0).

Rules: a clip is addressed by `(character id, clip id)`; curves are named by the role map and the face control names,
never by a target engine's own names; everything in the table exports to Unreal through the plugin as Animation
Sequences, Control Rig poses and Level Sequences, and imports back the same way ([`import-export.md`](import-export.md)
§5.2). Time is frames at a stated fps (Blender) and time codes (USD); no tick unit of our own (iClone's 6,000 ticks a
second stays iClone's). Creatures' clips animate their own skeletons ([`character-data-model.md`](character-data-model.md) §1.0).

## 2 · Every later feature, and where it plugs in

The user's list (TASKS SCOPE, IDEAS) and R21's "later", with the extension point each one already has in this spec.
Every later feature is a built-in module or an outside plugin on the same plugin API ([`plugins.md`](plugins.md));
every AI part of one is a command that runs on the engine host ([`ai-engines.md`](ai-engines.md) §1).

| Later feature | Reference | Extension point now | What is reserved |
|---|---|---|---|
| **Animate workspace** (iClone's side) | iClone 8's timeline, layers, Motion Director, Curve Editor; Unreal Sequencer; Cascadeur's AutoPosing/AutoPhysics (§3, §4) | §1's data; `register_workspace("Animate")`; commands under `juststage.anim.*` | the `anim` command area |
| **Live capture in JustStage** (item 26) | Unreal's Live Link Face and MetaHuman Animator; BlendArMocap; VMC apps (§8) | `register_capture_source(kind, cls)`: MediaPipe webcam, the Live Link Face stream, VMC ([`skeleton-and-face.md`](skeleton-and-face.md) §4) | the `capture` area |
| **Scene workspace** (sets, props, lights, cameras, terrain, sky) | iClone's scene features (§3) | USD scene stages referencing packages ([`interchange.md`](interchange.md) §2.3); `register_workspace("Scene")`; `juststage.scene.*` | the `scene` area and the `scene:` attribute namespace |
| **FX** (particles, PopcornFX-type) | iClone's PopcornFX (§3) | Blender geometry-nodes simulation zones; `register_generator("fx", …)`; `juststage.fx.*` | the `fx` area and `fx:` namespace |
| **Making clothes from patterns** (Marvelous Designer, Z-Weave, MetaTailor) | §4; ZOZO's Contact Solver (R8) | `juststage.clothes.sew_*`; the garment's MHCLO fit stays the output | the `pattern:` namespace (2D pieces, seams, grading) |
| **Sculpt extras** (layers, morph brushes; ZBrush-level) | ZBrush, Nomad (§4) | Blender sculpt mode + "Save as slider" (R7, a `user` target); a fork trigger if C-level work is needed (R1) | the `sculpt` area |
| **Props** | CC5's props and accessories (§2) | attach point = a joint + offset, spring settings as `prop:` attributes on a Mesh prim; `Props` catalogue; `juststage.props.*` | the `prop:` namespace |
| **Texture painting and baking in app** (Substance-type) | CC5's SkinGen layers (§2) | the `makeup.<layer>` channels and the master-set bake; Blender's texture paint; `register_generator("texture", …)` | — |
| **Path-traced finals** | Cycles (R15); Unreal's path tracer through the plugin | render presets as commands `juststage.render.*` | the `render` area |
| **Crowds, Motion Director-type control, AI motion** | iClone 8.4 crowds, Motion Director (§3); text-to-motion models (§7) | clips + the engine host's job door ([`ai-engines.md`](ai-engines.md)) | — |
| **Describe a person, get the character** (IDEAS.md) | CC5's cloud AI 3D generator + Body Wrap (§2) | a text model on the host choosing slider values through the commands; image-to-3D + `import.wrap` | — |
| **JustDirect inside the system** / "AI makes the movie" | IDEAS; R20 | the API door; scene stages and render passes as JustDirect's inputs | — |
| **A Blender fork** | R1's trigger (viewport C work, GPU skinning, a timeline editor, the window title) | the application template already owns the UI; a fork replaces the host, not the extension | — |

## 3 · The mechanisms every extension point rests on

1. **Attribute namespaces** — a new feature's data is `<feature>:` attributes in USD and `extras.<feature>` in glTF,
   versioned with `juststage:formatVersion` or the plugin's own version; small records go in `customData` under a
   reverse-DNS key, preserved by every USD reader ([`character-data-model.md`](character-data-model.md) §6). No USD
   schemas of ours (item 6).
2. **The plugin API** — built-in modules and outside plugins register the same way (`register_plugin`, `needs`), and a
   plugin registers its own attributes (`register_attributes`) so its data travels in the package like ours
   ([`plugins.md`](plugins.md) §2–§3).
3. **Command areas** — a new feature is a new `juststage.<area>` with its commands, permission group and MCP tools
   (registered by the command registrar — [`commands-and-api.md`](commands-and-api.md) §2, §4).
4. **Registries** — generators, importers, exporters, materials, workspaces, capture sources, slider groups
   ([`plugins.md`](plugins.md) §3).
5. **Workspaces** — Blender's own; the template adds one per feature (R6: Body, Head & Face, Skin & Materials, Hair,
   Clothes, Rig & Expressions, Import / Export now; Scene and Animate later).
6. **The scorecard** — every later feature already has rows in [`parity-scorecard.md`](parity-scorecard.md) marked
   `later`, so the floor and the order are visible from day one.
