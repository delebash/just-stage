# Import and export — CC5, Daz, MetaHuman, VRM, Unreal; the Unreal plugin's contract

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R11, R12, R13. Facts:
> RESEARCH §2, §4, §8 and the S9 note ("Pulling in assets from other programs"). The user's decision (TASKS):
> "it will be ok to import cc model if unreal can do it we can"; CC's base mesh is never JustStage's base (clean-room).

## 1 · The four import steps (every source)

The reference apps converge on four steps (S9 §2's assessment); each is a command, so every source is the same
pipeline with a per-source **profile** (`data/profiles/<source>.json`):

1. **Read** the file(s): `juststage.import.read` — FBX/OBJ (Blender's ufbx importer), glTF/GLB/VRM, USD, Alembic,
   BVH (our reader), plus the source's companion (CC's JSON, Daz's `.dtu` or `.duf`, MetaHuman's `.dna`).
2. **Characterise**: `juststage.import.characterise` — the rest pose and the role map from the profile, else a name
   and hierarchy guess (Godot `BoneMapper`'s keyword behaviour — S9 §3); the result is a **foreign character** that
   can be posed, animated and exported, with no wrap (CC's non-standard character, Unreal's IK Rig — the first
   deliverable, S9's "Changed" line).
3. **Wrap** (optional, "make it a JustStage character"): `juststage.import.wrap` — fit our base onto the source
   mesh (non-rigid ICP), transfer its shape as a slider, project its textures onto our UVs, transfer weights, rebuild
   clothes and hair as garments and grooms (CC5's Body Wrap and MetaHuman's From Custom Mesh behaviour — §2, S9).
4. **Convert materials**: `juststage.import.materials` — the source's parameters into our node groups
   (property-name maps: CC's JSON, Daz's Iray Uber names, MetaHuman's texture set; MaterialX translation graphs for
   OpenPBR/Standard Surface sources — S9 §3).

Every import writes `provenance` with the source program, file, date and licence label
([`character-data-model.md`](character-data-model.md) §6).

## 2 · Per source

| Source | Files in | Profile maps | Survives | Lost, and what we do | Terms (label) |
|---|---|---|---|---|---|
| **CC5 / CC4 / iClone** | FBX (Target Tool Preset "Blender" or "Unreal") + JSON sidecar; OBJ; GLB (5.2 import; export via API only) | `CC_Base_*` names or UE5 names → ours; the 52 ARKit shapes from the Standard profile; HD profile sliders by CC5's public slider names; UDIM tiles 1001–1006 → our tiles 1:1 | mesh, UVs, skeleton, weights, morphs as blend shapes, LODs, clothes and hair cards as separate meshes, textures; the JSON's material parameters (the GPL CC/iC Blender Tools' behaviour; reused as code only inside the GPL extension — R11) | wrinkle and physics data (sidecar read); `.fbxkey` (CC's own re-import key, ignored); joint correctives — CC has none; CC's USD is MDL (not used) | Reallusion content EULA: conditional — no character-generation systems, no AI training; the user decided importing is fine (TASKS) |
| **Daz Studio (G8, G8.1, G9)** | bridge export (FBX + `.dtu`, Apache-2.0 format) — preferred; plain FBX; native `.duf`/`.dsf` (DSON, public JSON) | the G8/G9 columns of [`skeleton-and-face.md`](skeleton-and-face.md) §1.4; `.dtu` `JointLinks` → our `correctives`; Iray Uber properties → our materials | mesh, morphs chosen by the export rules, weights, JCMs (from `.dtu`), subdivision level 0 | HD morphs (baked only); dForce settings; strand hair as strands (unverified) | Daz EULA: conditional — no redistribution of extractable content (so Daz-derived assets stay referenced, never packed into a shared library) |
| **MetaHuman** | the DCC export zip (`.dna` head + body, textures, JSON) or the Fab `.mhpkg` via Unreal; FBX via Unreal | DNA read with OpenRigLogic: joints, blend shapes, animated maps, controls; MetaHuman texture set → our channels | the full face rig (as a foreign DNA), body skeleton, textures | grooms (no exporter out of Unreal found — S9); vertex order in FBX (use DNA) | shown as a label (UE EULA 5.6+ "any engine"; the 2022 DNA Calibration licence names Unreal/Twinmotion); the user, 2026-10-29: "we do whatever to make it work not worry about license" — enabled |
| **VRM / VRoid** | `.vrm` (glTF + VRMC) through the VRM add-on | humanoid map → role map; `expressions` → the 52 subset; `meta` → provenance and licence label | everything VRM defines | PBR skin detail (MToon), strand hair | in-file `meta` fields decide; shown as the label |
| **Unreal (Fab, MetaHuman, own projects)** | USD (Unreal's exporter, Beta), FBX (`export_morph_targets`), glTF | UE5 names → ours; MetaHuman via DNA | meshes, skeleton, weights, animation, cameras, lights; morph targets via FBX | `.uasset` (re-export from Unreal); USD morph targets (unverified — test on `E:\Dev\Unreal` first, S9 §4's "Changed") | Fab licences per asset (CC-BY, Standard, NoAI); label from Fab's page |
| **MakeHuman / MPFB2** | `.mhm`, targets, `.mhclo`, MPFB2 `.blend` | the hm08 index map; targets → `makehuman.*` shape keys; MHCLO offsets → garment fit | all of it | — | CC0 |
| **Mixamo** | FBX | `mixamorig:` names → ours | rig, animation | — | Adobe terms: no AI training; label |
| **Any humanoid (sculpt, scan, AI mesh)** | OBJ, FBX, glTF, PLY | step 2 by guess, step 3 wrap | shape, textures (projected) | — | the user's own |
| **Motions** | BVH, FBX, VMC recordings | role map retarget | bone animation | — | per source |

## 3 · Export (R12, R17)

One command, `juststage.export.run`, with a **preset** (`data/presets/<target>.json`) that fixes the format, axes,
units, rest pose, bone names, texture bake sizes, material model, hair form and what goes in the companion:

| Preset | Format | Rules the preset enforces |
|---|---|---|
| `package` | the USD character package + companions | the full record, no bake, no loss |
| `unreal` | the package for the plugin; FBX fallback | UE5 names, cm, Z-up X-forward, IK helper bones, triangulated, one animation per file, morph targets named, Alembic grooms 1.5 (+ USD BasisCurves GroomAPI), textures ≤ 8K, DNA beside |
| `metahuman` | USD/FBX head mesh + our textures in MetaHuman's slots | the "Send to Unreal as a MetaHuman" path: the plugin runs Mesh to MetaHuman (Epic's cloud, Epic's terms — optional, user-run); textures re-baked into face base colour, normal, cavity, animated maps and body base colour, normal, cavity (MetaHuman's Texture Override slots — S10 §5) |
| `gltf`, `vrm` | glTF/GLB, VRM 1.0 | [`interchange.md`](interchange.md) §3 |
| `unity` | FBX (+ glTF on request) | T-pose, ≤ 4 weights, Y-up metres, blend-shape normals with smoothing groups, Unity's `HumanBodyBones` names in a companion map |
| `godot` | glTF | deform bones only, ≤ 4 weights, `extras.targetNames` |
| `blender`, `maya`, `max`, `motionbuilder` | FBX + companion; USD for Maya/Max/Houdini pipelines | HumanIK names on request |
| `cc5` | FBX with the ARKit 52 by CC Standard names, cards for hair, our six tiles as CC's UDIM 1001–1006, textures in folders; our sidecar beside it | CC imports a bone-skinned FBX through Characterization (§2); CC's own JSON sidecar is CC's export, whose structure is unpublished (S9) — not imitated |
| `marvelous` | FBX/OBJ avatar | avatar for garment making |

Rules: every preset has a **round-trip test** into its target where the target is free to run (Blender, Godot,
Unreal on the user's machine, Unity Personal when the user installs it; Maya and CC5 as the user's own checks); a
preset without a passing test is marked experimental in the UI.

## 4 · Unreal through the plugin (R12, R13) — why a plugin

Unreal reads USD (Beta) and FBX; what it cannot do from a file is set up a character: skeleton reuse, the RigLogic
face component, groom binding, skin/eye/hair materials, Live Link, and an update that keeps animation. That is CC5's
Auto Setup pattern (§2) and MetaHuman's own assembler (§4). The plugin is MIT (R2; 303 MIT Unreal plugins on GitHub —
§6), targets UE 5.8 at first, Windows, macOS and Linux editors; its own tests run in Unreal's Automation framework.

## 5 · The Unreal plugin's contract

### 5.1 In: `JustStage.ImportCharacter(package_path, options)`

- Reads the package (USD stage + companions). Builds: a `USkeletalMesh` per LOD variant from `geometry.usdc`
  (Unreal's USD importer when it round-trips morph targets, else the FBX fallback — decided by the gate's import
  test), a `USkeleton` named `SK_JustStage_<skeleton_version>` **shared by every JustStage character of that
  skeleton version** (so animations retarget nowhere), morph targets by our names, the DNA as a RigLogic-driven
  face (the MetaHuman runtime path), grooms from the Alembic twins with `UGroomBindingAsset`s, materials as instances
  of the plugin's master materials (skin, eye, cornea, occlusion, tearline, teeth, tongue, hair, cloth) fed by our
  texture channels and the `juststage` render-context parameters, body correctives as a Control Rig / Anim Blueprint set
  (the `_JCMAnim` pattern of Daz's bridge — S9), a Blueprint actor `BP_<Character>` that assembles the parts.
- Asset paths: `/Game/JustStage/<CharacterId>/…` (the UUID, not the display name), so renames never move assets.
- Every asset gets metadata tags `juststage:characterId`, `juststage:version`, `juststage:part`.

### 5.2 Out: `JustStage.ExportCharacter(actor, options)` and Live Link both ways

- Export the current state (poses, morph weights, edited materials) back as a package delta the Blender side merges.
- Live Link: the plugin is a Live Link **source** of JustStage's socket (poses and face controls from Blender into
  Unreal) and a **subject consumer** that streams Unreal's Sequencer/Control Rig/MetaHuman Animator poses back to
  Blender's socket for preview (Live Link's documented extension point — §8 pass 2). ARKit curves for the face.

### 5.3 The keep-animation rule (the complaint R12 answers)

iClone users' top complaint: an update "bakes keyframes and wipes lip-sync data" (§3). JustStage's rule:

> **Updating a character in Unreal keeps every animation, sequence, Control Rig and lip-sync that referenced it.**

The plugin guarantees it by **re-importing in place**: same asset paths (the UUID), the same `USkeleton` asset (bone
names and order are append-only between skeleton minor versions — [`project-files.md`](project-files.md) §3), the same
morph-target names, DNA control names and material slot names. An update that would break one of these (a skeleton
major bump, a removed morph a sequence keys, a renamed slot) is **refused by the plugin with the breaking item named**,
offering "import as a new character" instead. A test imports a character, animates it in a Level Sequence with a
face curve and lip-sync, re-imports an edited version, and asserts the sequence still plays unchanged.

### 5.4 "Send to Unreal as a MetaHuman" (optional, R12)

Runs Epic's Mesh to MetaHuman on our head (and body since 5.8) inside Unreal — Epic's cloud identity solve, Epic's
terms shown as a label — and returns a real MetaHuman that any MetaHuman tool accepts. It is a user-run button, never
automatic, and it ships enabled (the user, 2026-10-29: "we do whatever to make it work not worry about license").

## 6 · iClone's side, for now (R13)

Animation goes to Unreal (Sequencer, Control Rig, Live Link mocap, MetaHuman Animator — Windows-only, Epic's terms)
through the plugin, or stays in Blender's own tools (Actions, NLA, Graph Editor, Rigify controls). The data both need
is defined in [`animation-and-later-features.md`](animation-and-later-features.md) so an Animate workspace fits later
without a redesign.
