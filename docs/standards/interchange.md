# Interchange — USD, glTF + VRM, FBX, Alembic, and the companion files

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R17, R11, R12. Facts:
> RESEARCH §8 (round one and S8), S9 and S10.

## 1 · Axes, units and the canonical convention

| Where | Up | Front | Handedness | Units | Source |
|---|---|---|---|---|---|
| **JustStage inside Blender** | Z | −Y | right | metres | Blender's own (§8 pass 2) |
| USD package (written) | Y (`upAxis = "Y"`) | +Z facing for characters | right | metres (`metersPerUnit = 1`) | the glTF/VRM/Godot convention (§8); Blender's USD I/O converts Z-up ↔ Y-up itself |
| glTF / VRM | +Y | +Z | right | metres | glTF 2.0 §coordinate system |
| Unreal preset | Z | +X | left | centimetres | Unreal 5.8 docs (§8) |
| Unity preset | Y | +Z | left | metres (1 unit) | Unity 6 docs (§8 pass 2) |
| Godot preset | Y | +Z | right | metres | Godot 4.7 docs (§8) |

Rule: one canonical internal convention, per-target **export presets** (CC5's Target Tool Preset pattern, §2); no
"manual orientation" options on import — the file states its axes (Blender's 4.5 ufbx importer dropped those options
for that reason, §8 pass 2).

## 2 · OpenUSD — the character package and scenes (R17)

Standard: [OpenUSD](https://openusd.org/release/index.html) (26.11; Tomorrow Open Source Technology License 1.0),
AOUSD Core Specification 1.0 for composition and the USDA/USDC/USDZ formats (§8).

### 2.1 Package layout

```
<Name>.juststage/                 a folder package (USDZ can't hold UDIM tiles — Blender's note, S9 §1.4)
  character.usda                  root layer: the prim tree, variants, references to the side layers
  geometry.usdc                   meshes, UVs, skin weights, blend shapes (binary)
  rig/skeleton.usdc               UsdSkelSkeleton (rest and bind transforms)
  rig/face.dna                    the face rig (OpenRigLogic DNA)
  grooms/<groom>.usdc             UsdGeomBasisCurves with GroomAPI (+ an Alembic twin on request, §4)
  textures/<channel>.<tile>.<ext> the master texture set
  character.juststage.json        the companion (schema `juststage-character`, version N)
  thumbnail.webp                  ≥ 256×256 (Blender's asset-preview rule, §8 pass 2)
```

### 2.2 Prim layout (root layer)

```
/Character (Xform, kind = component, customData: juststage:characterId, juststage:schemaVersion)
  /Character/Skel            UsdSkelRoot
    /Body, /Eye_L, /Eye_R, /Cornea_L, …, /Teeth_Upper, /Tongue      Mesh (level 0) + UsdSkelBindingAPI
    /Skeleton                UsdSkelSkeleton
    /Anim                    UsdSkelAnimation (rest; blendShapeWeights for the ARKit 52 and the slider state)
  /Character/Grooms/<groom>  BasisCurves, apiSchemas = [GroomAPI, JustStageGroomAPI_1]
  /Character/Garments/<garment>   Mesh + UsdSkelBindingAPI, apiSchemas = [JustStageGarmentAPI_1]
  /Character/Looks/<material>     UsdShade Material: UsdPreviewSurface + MaterialX OpenPBR (render contexts)
  variantSets: "lod" (0..3), "outfit" (named garment sets), "groom_lod" (strands | cards | mesh)
```

- Every level-0 mesh is a **subdivision surface** in USD (`subdivisionScheme = catmullClark`) so a reader can derive
  levels 1–2; the displacement channels carry the HD detail. Unreal's USD importer takes a `SubdivisionLevel` 0–6
  option (S9 §4).
- Blend shapes: one `UsdSkelBlendShape` per shape key, `offsets` + `pointIndices` sparse, `normalOffsets` when
  authored; in-betweens for non-linear sliders.
- **JustStage applied API schemas**, versioned by USD's family rule (`_1`, `_2` …; version 0 has no suffix — §8):
  `JustStageCharacterAPI_1` (ids, versions, provenance pointer), `JustStageSliderAPI_1` (slider state per shape),
  `JustStageGroomAPI_1`, `JustStageGarmentAPI_1`, `JustStageMaterialAPI_1` (the skin/eye/hair parameters). They hold
  what UsdSkel lacks and mirror the companion JSON for USD-native readers; the JSON stays the full record. Schemas are
  generated with USD's `usdGenSchema` from `schema.usda` in the repo. **NOT STANDARD** (own schemas; standard option:
  wait for AOUSD's character group — no normative schemas before 2027 at the earliest, §8 pass 2). Covered by the
  character-JSON mark in [`character-data-model.md`](character-data-model.md) §0.

### 2.3 Scenes (later)

A JustStage scene is a USD stage that **references** character packages, props and sets as components, with layers
for set dressing, animation and render settings (USD's composition is the standard for exactly this — §8). Unreal
reads it through its USD Stage (Beta) and Blender through its USD importer (no layers/references on Blender's import
side today — S9 §1.4; the scene workspace, when built, resolves composition itself). Defined now, built later
([`animation-and-later-features.md`](animation-and-later-features.md)).

### 2.4 What USD does not carry — the companions (R17)

| Data | Companion | Why |
|---|---|---|
| Face rig behaviour | `rig/face.dna` | UsdSkel has no rig behaviour (§8); DNA + OpenRigLogic is the proven open runtime |
| Body correctives, slider definitions, shape-space maps, wrinkle layers, groom settings, garment fit data, provenance, licence, extensions | `character.juststage.json` | no USD schema; one versioned JSON Schema (§0 of the data model) |

The companions are **always** written beside the USD; a package with the JSON missing imports as a plain UsdSkel
character with a warning naming what was lost.

## 3 · glTF 2.0 and VRM 1.0 — engines and avatars (R17)

Standard: [glTF 2.0](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html), [VRM 1.0](https://vrm.dev/en/vrm1/),
[glTF-Blender-IO](https://github.com/KhronosGroup/glTF-Blender-IO) (Apache-2.0, Blender's own exporter) and the
[VRM Add-on for Blender](https://github.com/saturday06/VRM-Addon-for-Blender) (MIT) as the writers.

Export rules (the glTF/VRM preset):

- Deform bones only; T-pose through the retarget pose; ≤ 4 joint influences per vertex set (glTF's guarantee; the
  Godot/Blender presets write one set — §8), weights normalised.
- Meshes at level 0 by default, or a baked level (1 or 2 with displacement applied) on request — glTF has no
  subdivision.
- Morph targets: the ARKit 52 and every slider the user ticks, names in `mesh.extras.targetNames`, sparse accessors;
  the exporter warns above 8 morphed attributes (the client guarantee — §8).
- Materials: PBR metallic-roughness + `KHR_materials_specular`, `KHR_materials_ior`, `KHR_materials_sheen`,
  `KHR_texture_transform`; textures baked per material at ≤ 4K (UDIM tiles merged per material — glTF has no UDIM).
- Hair: cards only (no curves extension exists — §8); a strand groom is baked to cards first.
- VRM adds `VRMC_vrm` (humanoid from the role map, `meta` from `provenance` and the licence fields, `expressions`
  presets derived from the 52 and the visemes, `lookAt` from the eye bones), `VRMC_springBone` for hair and
  garment secondary motion where the user asks, MToon only when the user picks it (our skin is PBR).
- Import: glTF/GLB/VRM through Blender's importers, then characterise ([`skeleton-and-face.md`](skeleton-and-face.md) §1.5);
  VRM's humanoid map seeds the role map; VRM `meta` lands in `provenance`.

## 4 · FBX and Alembic

- **FBX in:** Blender 5.x's C++ importer (ufbx-based, MIT or Unlicense) — `bpy.ops.wm.fbx_import` (the Python importer
  is legacy since 5.0, §8 pass 2). It reads skins, blend shapes, animation; axes and units from the file.
- **FBX out:** two writers exist; the choice is made by a test, not a preference. Default: Blender's own FBX exporter
  (`io_scene_fbx`, GPL, writes skins, blend shapes and shape-key normals since 5.1 — §8 pass 2) because it is the one
  that has shipped for years. `ufbx-write` (MIT or Unlicense, same author as ufbx, work in progress) is adopted for
  the MIT libraries when the round-trip suite passes on it (R17: Unreal, Unity, Maya, Blender). Both run behind the same
  preset and the same test suite ([`testing.md`](testing.md) §4). Export version FBX 7.5 (2016+), binary.
- **Unreal FBX rules** the preset satisfies (§8): triangulated, pivot at the root bone, one animation per file, morph
  targets named, cm, Z up, X forward; the Unreal plugin prefers the USD package and falls back to FBX for skeletal
  meshes with morph targets where Unreal's USD import is still Beta (S9 §4's attack).
- **Alembic:** grooms with the `groom_*` attributes at version 1.5 (Unreal's documented path, §8 pass 2); baked cloth
  and vertex animation out (Blender's Alembic exporter). Standard: [Alembic](https://github.com/alembic/alembic) (BSD-3).

## 5 · Formats by job (the one-way rule)

| Job | Format | Never |
|---|---|---|
| A character between JustStage installs, to JustDirect, to the Unreal plugin, to archives | the USD character package + companions | a `.blend` (Blender-only), a bare FBX |
| A character into Unity, Godot, Three.js, VRM apps | glTF/GLB (+ VRM when the user asks) | FBX first |
| A character into Unreal | the plugin reads the package; FBX fallback | hand FBX import without the plugin |
| A character into Maya, 3ds Max, MotionBuilder, Marvelous Designer, CC5 | FBX (+ companion JSON) | — |
| A character into Blender without JustStage | `.blend` (it is one) or the package through Blender's USD import | — |
| Grooms into Unreal | Alembic 1.5 attributes (reliable) or USD BasisCurves + GroomAPI | cards unless the target has no strands |
| Materials into USD readers | UsdPreviewSurface + MaterialX OpenPBR | MDL (CC's choice; Blender can't read it — S9) |
| Correctives and the face rig anywhere | DNA + the companion JSON | USD alone |
| Scenes (later) | USD stage referencing packages | one giant file |
