# Interchange — USD, glTF + VRM, FBX, Alembic, and the companion files

> **Status: APPROVED recs, written 2026-10-29** (the review's items 1, 4, 5, 6, 11, 13, 21 — TASKS; review file
> [`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md)). R17 as changed, R11, R12.
> Facts: RESEARCH §8, S9, S10; Blender facts on the installed 5.3.

## 1 · Axes, units and the canonical convention

| Where | Up | Front | Handedness | Units | Source |
|---|---|---|---|---|---|
| **JustStage inside Blender** | Z | −Y | right | metres | Blender's own (§8) |
| USD package (written) | Y (`upAxis = "Y"`) | +Z facing for characters | right | metres (`metersPerUnit = 1`) | the glTF/VRM/Godot convention (§8); Blender's USD I/O converts Z-up ↔ Y-up itself |
| glTF / VRM | +Y | +Z | right | metres | glTF 2.0 §coordinate system |
| Unreal preset | Z | +X | left | centimetres | Unreal 5.8 docs (§8) |
| Unity preset | Y | +Z | left | metres (1 unit) | Unity 6 docs (§8) |
| Godot preset | Y | +Z | right | metres | Godot 4.7 docs (§8) |

Rule: one canonical internal convention, per-target **export presets** (CC5's Target Tool Preset pattern, §2); no
"manual orientation" options on import — the file states its axes (Blender's ufbx importer dropped those options, §8).

## 2 · OpenUSD — the character package and scenes (R17)

Standard: [OpenUSD](https://openusd.org/release/index.html) (Blender 5.3 builds USD 26.08 — §8), AOUSD Core
Specification 1.0 for composition and the USDA/USDC/USDZ formats (§8).

### 2.1 Package layout

```
<Name>.juststage/                 a folder package (USDZ can't hold UDIM tiles — Blender's note, S9)
  character.usda                  root layer: the prim tree, variants, references to the side layers
  geometry.usdc                   meshes, UVs, skin weights, blend shapes, GeomSubsets (binary)
  rig/skeleton.usdc               UsdSkelSkeleton (rest and bind transforms)
  rig/face.dna                    the face rig (Epic's DNA, MetaHuman's names — skeleton-and-face §2.3)
  rig/body.dna                    the body correctives (RBF and twist-swing layers — skeleton-and-face §3)
  grooms/<groom>.usdc             UsdGeomBasisCurves with Epic's GroomAPI (+ an Alembic twin, §4)
  garments/<garment>.mhclo        each garment's MakeHuman fit file
  textures/<channel>.<tile>.<ext> the master texture set, plus the baked HD displacement and normal maps
  thumbnail.webp                  ≥ 256×256 (Blender's asset-preview rule, §8)
```

Everything JustStage knows about the character is in USD's own parts — UsdSkel, UsdShade with MaterialX, BasisCurves,
GeomSubsets, `assetInfo`, `customData` and the dozen `juststage:` attributes of
[`character-data-model.md`](character-data-model.md) §0 (N1, approved) — plus the two DNA files and the MHCLO fit
files. **No JustStage applied schemas, no `schema.usda`, no `usdGenSchema`** (item 6). Blender's own USD exporter writes
the geometry, skeleton, blend shapes and materials; the USD hook API (`bpy.types.USDHook.on_export` / `on_import`)
adds and reads the `juststage:` attributes from the extension's `PropertyGroup`s.

### 2.2 Prim layout (root layer)

```
/Character (Xform, kind = component; assetInfo identifier/name/version; juststage:formatVersion, :kind,
            :baseVersion, :skeletonVersion, :sliderIds, :sliderValues, :faceRig, :bodyRig)
  /Character/Skel            UsdSkelRoot
    /Body, /eyeLeft, /eyeRight, /eyeshell, /eyeEdge, /eyelashes, /teeth, …   Mesh (level 0) + UsdSkelBindingAPI;
                             GeomSubsets family "juststage:hide" (body faces hidden under garments)
    /Skeleton                UsdSkelSkeleton (the UE5 names)
    /Anim                    UsdSkelAnimation (rest; blendShapeWeights for the ARKit 52 and the slider state)
  /Character/Grooms/<groom>  BasisCurves, apiSchemas = [GroomAPI]; groom_* primvars
  /Character/Garments/<garment>   Mesh + UsdSkelBindingAPI; juststage:layer, :tuckUnder (rel), :fit (asset), :cloth:*
  /Character/Looks/<material>     UsdShade Material: outputs:surface (UsdPreviewSurface) and the MaterialX network
                             (open_pbr_surface; chiang_hair_bsdf for hair), both written by Blender's exporter
  variantSets: "lod" (0..3), "outfit" (named garment sets), "groom_lod" (strands | cards | mesh)
```

- Every level-0 mesh is a **subdivision surface** in USD (`subdivisionScheme = catmullClark`) so a reader can derive
  levels 1–2; the baked displacement maps carry the HD detail. Unreal's USD importer takes a `SubdivisionLevel` 0–6
  option (S9).
- Blend shapes: one `UsdSkelBlendShape` per shape key, `offsets` + `pointIndices` sparse, `normalOffsets` when
  authored; in-betweens for non-linear sliders.
- The hm08 helper geometry and joint cubes are deleted at export (MPFB2's workflow — item 2).

### 2.3 Scenes (later)

A JustStage scene is a USD stage that **references** character packages, props and sets as components, with layers for
set dressing, animation and render settings (USD's composition — §8). Unreal reads it through its USD Stage (Beta) and
Blender through its USD importer (no layers or references on Blender's import side today — S9; the scene workspace,
when built, resolves composition itself). Defined now, built later ([`animation-and-later-features.md`](animation-and-later-features.md)).

### 2.4 What USD does not carry — the companions

| Data | Carrier | Why |
|---|---|---|
| Face rig behaviour | `rig/face.dna` beside the USD | UsdSkel "does not aim to provide general rigging and execution behaviours" (§8); OpenUSD 26.08's OpenExec rig schemas are experimental (§8); DNA + OpenRigLogic is the proven open runtime |
| Body correctives | `rig/body.dna` beside the USD | the DNA's RBF and twist-swing layers (item 1) |
| Garment fit | `garments/<garment>.mhclo` | MakeHuman's fit format (item 3) |
| Groom generator settings | not carried — the library `.blend` holds them | the baked curves are what other programs use (studios' practice, S10 — item 5) |
| Provenance and licence | `assetInfo` and the `juststage` `customData` inside the USD | USD's native metadata |

The DNA files are always written beside the USD; a package without them imports as a plain UsdSkel character with a
warning naming what was lost.

## 3 · glTF 2.0 and VRM 1.0 — engines and avatars

Standard: [glTF 2.0](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html), [VRM 1.0](https://vrm.dev/en/vrm1/),
[glTF-Blender-IO](https://github.com/KhronosGroup/glTF-Blender-IO) (Apache-2.0, Blender's own exporter) and the
[VRM Add-on for Blender](https://github.com/saturday06/VRM-Addon-for-Blender) (MIT) as the writers.

Export rules (the glTF/VRM preset):

- Deform bones only; T-pose through the retarget pose; ≤ 4 joint influences per vertex set, weights normalised.
- Meshes at level 0 by default, or a baked level (1 or 2 with displacement applied) on request — glTF has no
  subdivision.
- Morph targets: the ARKit 52 and every slider the user ticks, names in `mesh.extras.targetNames`, sparse accessors;
  the exporter warns above 8 morphed attributes (the client guarantee — §8). Rig results (the face DNA, the body
  correctives) are baked into morph-weight and joint animation.
- Materials: PBR metallic-roughness + `KHR_materials_specular`, `KHR_materials_ior`, `KHR_materials_sheen`,
  `KHR_texture_transform`; textures baked per material at ≤ 4K (UDIM tiles merged per material — glTF has no UDIM);
  HD detail as baked normal maps.
- Hair: cards only (no curves extension exists — §8); a strand groom is baked to cards first.
- **JustStage's own fields go in glTF's `extras`** (item 11) — "Application-specific data" (Khronos' `extras.schema.json`,
  "SHOULD be a JSON object") — under one `juststage` key on the node they describe, written by the glTF exporter's hook
  (`glTF2ExportUserExtension.gather_node_hook` — the glTF add-on's documented user-extension point, on disk in 5.3).
  Blender's glTF exporter writes custom properties to `extras` itself ("Unlike glTF extensions, custom properties
  (extras) have no defined namespace, and may be used for any user-specific or application-specific purposes" —
  manual), but JustStage's `PropertyGroup`s aren't custom properties since 5.0, hence the hook. No vendor extension and
  no Khronos prefix registration: an extension is for data other programs are meant to read; nobody but JustStage
  reads ours.
- VRM adds `VRMC_vrm` (humanoid from the role map, `meta` from provenance and the licence fields, `expressions`
  presets derived from the 52 and the visemes, `lookAt` from the eye joints), `VRMC_springBone` for hair and garment
  secondary motion where the user asks, MToon only when the user picks it (our skin is PBR).
- Import: glTF/GLB/VRM through Blender's importers, then characterise ([`skeleton-and-face.md`](skeleton-and-face.md)
  §1.5); VRM's humanoid map seeds the role map; VRM `meta` lands in provenance; `extras.juststage` is read back.

## 4 · FBX and Alembic

- **FBX in:** Blender's C++ importer (ufbx-based, MIT or Unlicense) — `bpy.ops.wm.fbx_import` (the Python importer is
  legacy since 5.0, §8). It reads skins, blend shapes, animation; axes and units from the file.
- **FBX out: Blender's own exporter** (`io_scene_fbx`, GPL; writes skins, blend shapes and, since 5.1, shape-key
  normals — §8) — **R17 as changed** (the user: "i agree with your recs"; item 13): it has shipped for years, while
  `ufbx-write` is "still a work-in-progress" (§7). FBX 7.5 binary. Rig results are baked; the DNA files are written
  beside the FBX.
- **The FBX sidecar** `<name>.juststage.json` holds the `juststage:` fields of the character (§0 of the data model) and
  names the DNA and MHCLO files — Blender's FBX exporter has no hook for our data (no hook code in `io_scene_fbx`, on
  disk in 5.3), and CC5, Daz and MetaHuman travel the same way (FBX + JSON + `.fbxkey`, FBX + `.dtu`, FBX + `.dna` — S9).
- **Unreal FBX rules** the preset satisfies (§8): triangulated, pivot at the root bone, one animation per file, morph
  targets named, cm, Z up, X forward; the Unreal plugin prefers the USD package and falls back to FBX for skeletal
  meshes with morph targets where Unreal's USD import is still Beta (S9).
- **Alembic:** grooms with the `groom_*` attributes at version 1.5 (Unreal's documented path, §8) — Blender 5.3 exports
  "Arbitrary attributes on meshes, curves, and pointclouds" and curve velocities to Alembic (§8), so no exporter of
  ours; baked cloth and vertex animation out. Standard: [Alembic](https://github.com/alembic/alembic) (BSD-3).

## 5 · Formats by job (the one-way rule)

| Job | Format | Never |
|---|---|---|
| A character between JustStage installs, to JustDirect, to the Unreal plugin, to archives | the USD character package + the DNA and MHCLO companions | a `.blend` (Blender-only), a bare FBX |
| A character into Unity, Godot, Three.js, VRM apps | glTF/GLB (+ VRM when the user asks), JustStage fields in `extras` | FBX first; a glTF sidecar |
| A character into Unreal | the plugin reads the package; FBX fallback | hand FBX import without the plugin |
| A character into Maya, 3ds Max, MotionBuilder, Marvelous Designer, CC5 | FBX + the sidecar, or USD where the app reads it (Maya, Max, Houdini, MD — S9) | — |
| A character into Blender without JustStage | `.blend` (it is one) or the package through Blender's USD import | — |
| Grooms into Unreal | Alembic 1.5 attributes (reliable) or USD BasisCurves + GroomAPI | cards unless the target has no strands |
| Materials into USD readers | UsdPreviewSurface + MaterialX OpenPBR, written by Blender's exporter | MDL (CC's choice; Blender can't read it — S9); a shader network of our own |
| Face rig and body correctives anywhere USD goes | the DNA files beside the USD | rig data inside the USD |
| JustStage's own fields | `juststage:` attributes in USD, `extras.juststage` in glTF, the sidecar beside FBX | a JSON beside USD or glTF |
| Scenes (later) | USD stage referencing packages | one giant file |
