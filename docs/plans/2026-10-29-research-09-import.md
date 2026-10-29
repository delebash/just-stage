# Research 09 — Pulling in assets from other programs (second pass, S9)

Researched 2026-10-29 by the S9 research agent for RESEARCH.md §2, §7 and §8 (clean-room: public docs, public
repos and behaviour only; nothing copied). The user, 2026-10-29: "we need to be able to pull in assest from other
programs just like cc5 and unreal engine and daz studio", and "things like openusd help alot as unreal i think
already can export assets in this format".

**Labels.** **page read** = the page, README, manual source or repo file was fetched and read (GitHub through
`gh api`, Bitbucket through its public API, Blender's manual through its source repo on projects.blender.org).
**search snippet only** = seen only in a search-result summary. **round one** = a fact from round one's notes,
cited and not re-derived. **code read** = names of keys, classes or files read from a public repo to learn
behaviour (no code copied). Dates are the source's own; "undated" pages were read 2026-10-29.

**Access limits this session (not worked around):** fab.com (`/cla`, `/eula`) — HTTP 403; vroid.pixiv.help and
vroid.com — 403; support.marvelousdesigner.com — 403; helpx.adobe.com Substance format table — 403; metahuman.com
news and licence pages — redirect to an Epic login; Bitbucket's README page is script-rendered (its public API was
used instead). projects.blender.org served Blender's manual source this time (round one got 403).

**Scope applied:** Omniverse is out (Omniverse-only facts appear only where they decide what a USD file holds);
paid-only tools are out as options but kept as references; Unity is out; licences are one-line labels.

---

## Top findings

1. **OpenUSD carries meshes, skeletons, skin weights, blend shapes, PreviewSurface/MaterialX materials, curves,
   cameras, lights and animation between Unreal, Blender, Maya, Houdini and 3ds Max — not joint correctives, rig
   behaviour, wrinkle maps or cloth.** Each app's exporter writes UsdSkel skeletons and blend shapes; none writes a
   corrective or driver system. — [Blender usd.rst](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/files/import_export/usd.rst),
   [maya-usd commands](https://github.com/Autodesk/maya-usd/blob/dev/lib/mayaUsd/commands/Readme.md),
   [3ds Max USD export](https://help.autodesk.com/cloudhelp/2025/DEU/3dsMax-USD/files/USD-for-3ds-Max/Import-and-export-USD-data-in-Max/GUID-DC04C60D-07CD-4844-AB96-4FDE25CCAD8C.html) (page read).
2. **Unreal does export USD (Beta):** exporters for static meshes, skeletal meshes, animation sequences, geometry
   caches, materials, levels (sub-levels as sublayers) and level sequences; materials leave as baked
   **UsdPreviewSurface**. Whether skeletal-mesh morph targets are written as USD blend shapes is not documented.
   — [USDExporter API, UE 5.8](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/USDExporter),
   [FUsdMeshAssetOptions](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/USDExporter/FUsdMeshAssetOptions?lang=en-US) (page read).
3. **Unreal's USD import is the widest of any app checked:** skeletal animation (UsdSkelAnimQuery → AnimSequence),
   blend shapes with in-betweens, grooms (GroomAssets, GroomCaches, GroomBindings), MaterialX in USD, MDL,
   PreviewSurface, OpenVDB volumes and spatial audio. — [UUsdStageImportOptions](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/USDStageImporter/UUsdStageImportOptions?lang=en-US),
   [MaterialX import, UE 5.8](https://dev.epicgames.com/documentation/unreal-engine/importing-materialx-files-in-unreal-engine?lang=en-US) (page read).
4. **The two programs the user named first don't speak USD usefully.** Daz Studio has no USD exporter (its
   exporters are FBX, OBJ, Alembic, BVH, U3D, CR2; DS 6 retired Collada). CC/iClone export USD only for Omniverse,
   with materials in **MDL**, which Reallusion says Blender can't read. — [Daz object index](https://docs.daz3d.com/public/software/dazstudio/4/referenceguide/scripting/api_reference/object_index/start),
   [DS 6 highlights](https://delorean.daz3d.com/blog/daz-studio-6-technical-highlights),
   [Reallusion tracker 11048](https://www.reallusion.com/FeedBackTracker/Issue/USD-exports-not-working-in-other-DCCs-Houdini-and-Blender) (page read).
5. **Rich characters travel as "mesh file + JSON sidecar", and the receiving side rebuilds what FBX loses.** Daz's
   bridges write a `.dtu` JSON beside the FBX (raw Iray material properties, morph list, `JointLinks` that drive
   correctives from bone angles, subdivision, pose data); the Unreal side turns `JointLinks` into a `_JCMAnim`
   Anim Blueprint. CC writes a JSON material sidecar and an `.fbxkey`; MetaHuman's DCC export is DNA + JSON +
   PNG. — [DazBridgeUtils](https://github.com/daz3d/DazBridgeUtils), [DazToUnreal](https://github.com/daz3d/DazToUnreal) (code read),
   [CC fbxkey](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-Creating-Custom-Assets/About-fbxkey.htm),
   [MetaHuman export tool](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-export-tool-in-unreal-engine) (page read).
6. **Daz's bridges are open source (Apache-2.0) and ship humanoid bone maps** — Genesis 8/9 → MetaHuman, Mixamo,
   Unity and UE Manny (`g9_to_metahuman.json` and others). — [DazBridgeUtils tree](https://github.com/daz3d/DazBridgeUtils) (page read, pushed 2026-01-01).
7. **Daz's native files can be read without Daz Studio's exporter:** the Diffeomorphic DAZ Importer (GPL-2.0-or-
   later, v5.2.0 released 2026-08-10, now on GitHub) reads `.duf`/`.dsf` and handles JCM drivers (ERC links), Iray
   → Cycles/Eevee materials, dForce, HD data and hair. DSON is a published JSON spec (round one). — [GitHub repo](https://github.com/Diffeomorphic/import_daz) (page read).
8. **CC5's import paths, as a user sees them:** an FBX/OBJ becomes a prop, a humanoid (Characterization: T-pose
   and at least 15 mapped bones, or an auto-detected profile) or a creature; Daz Genesis 3/8/8.1/9/HD convert
   through Transformer (FBX in, base topology must be untouched); any humanoid mesh (skinned or not) wraps onto CC
   topology through Body Wrap; foreign clothing needs Transfer Skin Weights. — [CC5 manual](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Pipeline/Importing-Methods.htm) (page read).
9. **Mesh to MetaHuman is not local:** the source mesh may have any topology (FBX or OBJ), but the Identity Solve
   "happens in the cloud" and the rig comes back from the "MetaHuman Backend". — [From Mesh](https://dev.epicgames.com/documentation/en-us/metahuman/from-mesh) (page read).
10. **Unreal's auto-retarget only recognises UE4/UE5 Mannequins, MetaHumans and Stack O Bot**; other skeletons get
    chains by keyword and fuzzy name match. Godot's BoneMapper (MIT) is the open equivalent: keyword pick-lists,
    left/right detection and hierarchy search onto its humanoid profile. — [Auto Retargeting, UE 5.8](https://dev.epicgames.com/documentation/unreal-engine/auto-retargeting-in-unreal-engine?lang=en-US) (page read),
    [bone_map_editor_plugin.cpp](https://github.com/godotengine/godot/blob/master/editor/scene/3d/bone_map_editor_plugin.cpp) (code read).
11. **Open material converters exist for the hard cases:** NVIDIA's MDL SDK (BSD-3, 2026.0.2) "distils" MDL
    materials (Iray, CC's USD) to simpler models and bakes them, with a native-CPU back-end; MaterialX ships
    translation graphs (Standard Surface → glTF PBR / UsdPreviewSurface, OpenPBR ↔ Standard Surface) and texture
    bakers. — [MDL-SDK](https://github.com/NVIDIA/MDL-SDK), [MaterialX tree](https://github.com/AcademySoftwareFoundation/MaterialX) (page read).
12. **Strand hair has no common format:** Unreal takes grooms as Alembic (its own `groom_*` schema v1.5) or USD
    BasisCurves with Epic's GroomAPI; Blender's USD export writes only parent strands; CC hair is cards; Daz strand
    hair needs Diffeomorphic or a bridge. — [Alembic for grooms](https://dev.epicgames.com/documentation/unreal-engine/using-alembic-for-grooms-in-unreal-engine) (page read).
13. **Stores deliver different things:** Fab 3D models may come as FBX, GLB, glTF, OBJ, USD, USDZ or DCC files —
    or as Unreal-only `.uasset` packs; MetaHumans as `.mhpkg`. Sketchfab (sold by Epic to KitBash, announced
    2026-08-10) auto-converts downloads to glTF, GLB and USDZ. Poly Haven is CC0 in .blend, glTF, USD and FBX. —
    [Fab format rules](https://dev.epicgames.com/documentation/fab/asset-file-format-and-structure-requirements-in-fab?lang=en-US),
    [Digital Production 2026-08-12](https://digitalproduction.com/2026/08/12/kitbash-buys-artstation-and-sketchfab/),
    [Poly Haven API](https://api.polyhaven.com/files/wooden_table_02) (page read).
14. **Reallusion's licence allows export to "any other software" but not openable files.** The 2025-08-01 content
    policy: "The Standard License allows you to export 3D objects and characters to any other software"; round one's
    content EULA requires exported models to stay protected so they "cannot be opened or imported into a publicly
    available software application". — [content policy](https://www.reallusion.com/license/content.html) (page read),
    [content EULA](https://www.reallusion.com/Content/EULA/EULA.htm) (round one, page read).
15. **No open tool does what CC's Body Wrap or MetaHuman's From Custom Mesh does in one step;** the parts are open
    (deformation transfer in MIT and BSD-3 code, non-rigid ICP, robust skin-weight transfer), as round one found
    for garment fitting. — [deformation transfer (MIT)](https://github.com/mickare/Deformation-Transfer-for-Triangle-Meshes),
    [deformxfer (BSD-3)](https://github.com/jerenchen/deformxfer) (page read).

---

## 1 · Per source program — what it exports and what survives the trip

Notation in "survives": **yes** = carried in the file; **no** = lost; **sidecar** = carried only in a companion
file that a plugin must read; **?** = not verified this session.

### 1.1 CC5 / CC4 / iClone (Reallusion)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Character | FBX (Target Tool Preset per destination), OBJ (posed or morph targets), USD (Omniverse), iAvatar; GLB setting in the API only | Mesh, UVs, `CC_Base_` skeleton (or renamed to the UE skeleton), skin weights, expressions and morphs as blend shapes, LODs, UDIM (optional), clothes and hair cards as separate meshes; textures in categorised folders; subdivision detail as multi-level normal maps | Materials beyond textures → **sidecar** (JSON); CC editing state → **sidecar** (`.fbxkey`, needed to re-import into CC); joint correctives — CC has none to export (round one); wrinkle and physics data → **sidecar** (read by CC's Blender and Unreal tools) |
| Character via USD | USD | Skeleton joints (body + face), blend shapes, lights, motions, props | Materials as **MDL** — Blender can't read them (Reallusion's answer) |
| Motion | FBX, BVH, iMotion | Bone animation | Facial morph animation only in FBX (BVH carries no morphs) |
| Props / scenes (iClone) | FBX, OBJ (static), Alembic (baked), USD (Omniverse) | Mesh, hierarchy, vertex animation (Alembic) | — |
| Camera (iClone) | Real Camera data export | Lens, focal length, sensor, transform, clip planes | — |

Facts:
- CC5 FBX export: Target Tool Preset changes advanced settings per destination; options Mesh, Character, Motion,
  Character with Motion; writes a JSON file and a `Multi_Normal` folder; textures in categorised subfolders —
  [CC5 Export FBX](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/Export-FBX.htm) (round one, page read).
- FBX export options include bind pose, Epic UE4/UE5 skeleton, UE hand/foot IK, mouth-open as morph, skinned
  expressions → morphs, zero root, UDIM, LOD — [FBX Character section](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/17-Export/FBX-Advanced-Settings-Character.htm) (round one, page read).
- The `.fbxkey` holds "DRM base content information", bone scale per bone, body skin weight per vertex and clothing
  type; it is written only for a character-only round-trip FBX, not for Unity/Unreal exports; without it the
  character "cannot be imported back" — [About fbxkey](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08-Creating-Custom-Assets/About-fbxkey.htm) (undated, CC5 manual, page read).
- FBX exports carry a JSON sidecar of material parameters that the Blender tools use to rebuild materials —
  [CCiC Blender Pipeline README](https://github.com/reallusion/CCiC-Blender-Pipeline-Plugin) (round one, page read).
- CC's USD export (CC 3.41+) writes folders Lights ("keeps all lights and HDR image"), Materials ("includes all
  materials and textures"), Motions, Props (characters as props, with Meshes and Bones subfolders) and one main
  `.usd` — [Omniverse plug-in manual](https://manual.reallusion.com/Omniverse-Plug-in/Content/ENU/3.41/Sending-Character-in-USD-Format-to-Omniverse.htm) (undated, page read).
- Reallusion engineer, 2022-01-04: body and facial bones become USD skeleton joints; accessories get extra bones
  and skinning; morphs become USD blend shapes ("USD blend-shapes store positional offsets"); shaders were
  "rewritten from HLSL to MDL" (OmniPBR, OmniSurface, OmniHair) —
  [NVIDIA blog](https://developer.nvidia.com/blog/simplifying-realistic-character-creation-with-nvidia-omniverse-reallusion-connector) (page read).
- Tracker 11048 (CC 4.4, filed 2023-12-21, "Not a Bug"): materials and textures don't load in Blender or Houdini;
  admin reply 2024-02-23: "The Material of iClone USD is saved in MDL,but Blender does not support MDL" —
  [tracker](https://www.reallusion.com/FeedBackTracker/Issue/USD-exports-not-working-in-other-DCCs-Houdini-and-Blender) (page read).
- RLPy has export settings for FBX, GLB (`RExportGlbSetting`) and USD; GLB export in the UI not confirmed —
  [cc5-mcp-server RLPy reference](https://github.com/MorphoCore-Pty-Ltd/cc5-mcp-server) (round one, page read).
- iClone 8 imports OBJ/FBX props keeping the node hierarchy (or merging), and Alembic since 7.9 for vertex
  animation — [iClone manual: props](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/30-Set/Prop/Creating_Props_with_OBJ_FBX_Files.htm),
  [Alembic](https://manual.reallusion.com/iClone-8/Content/ENU/8.0/84-Alembic/Importing-Props-with-Vertex-Animation.htm) (search snippet only).
- iClone exports Alembic (range, sampling, split by material), USD for Omniverse (units cm/m since 8.7), static
  OBJ; imports BVH and FBX motion through a CC Characterization profile — round one iClone notes (page read).
- AccuRIG (free standalone) imports OBJ/FBX and exports FBX with presets for 3ds Max, Blender, Cinema 4D, Maya,
  MotionBuilder, Unity, Unreal, plus USD (Omniverse) and iAvatar —
  [CG Channel 2025-07-17](https://www.cgchannel.com/2025/07/rig-and-animate-3d-characters-for-free-with-accurig-2-0/) (search snippet only).

### 1.2 Daz Studio (Genesis 8 and 9)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Figure (character) | FBX, OBJ (static), Alembic (baked), bridges (FBX + `.dtu`) to Unreal, Unity, Blender, Maya, Cinema 4D, 3ds Max, Roblox, O3DE; native `.duf`/`.dsf` (DSON JSON) | Mesh, UVs, skeleton, skin weights; morphs chosen by Morph Export Rules (as plain blend shapes); with a bridge: JCMs rebuilt from `JointLinks`, Iray properties rebuilt as target shaders, subdivision baked or as level-0 subdivision surface | In plain FBX: JCM drivers (**sidecar** only), Iray material parameters (**sidecar** only), HD morphs (only baked); strand-based hair as strands (?) |
| Clothing / hair / props | Same formats; bridges send clothing and hair parented to the body | Separate meshes (structure as conforming figures not re-checked this session) | dForce cloth settings (? outside Diffeomorphic) |
| Pose / animation | FBX, BVH; bridge "Animation" mode (Timeline keys) | Bone animation; aniMate blocks must be baked to Timeline first | — |
| Scene | `.duf`; bridge "Environment" mode | Read by Diffeomorphic (its modules cover cameras and lights) | No USD, no glTF from Daz |

Facts:
- Daz Studio 4 script API exporters: DzAlembicExporter, DzBvhExporter, DzCr2Exporter, DzFbxExporter,
  DzObjExporter, DzU3DExporter (plus image and video); importers: DzBvhImporter, DzFbxImporter, DzObjImporter,
  DzPZ3Importer — [object index](https://docs.daz3d.com/public/software/dazstudio/4/referenceguide/scripting/api_reference/object_index/start) (undated, page read).
- Daz Studio 6 (Qt 6, Iray 2025.0.3) lists the Collada Exporter under "Retired Technologies"; no import/export
  format changes are described — [DS 6 technical highlights](https://delorean.daz3d.com/blog/daz-studio-6-technical-highlights) (undated, © 2026, page read).
- No native USD export in Daz Studio — [NVIDIA forum](https://forums.developer.nvidia.com/t/a-bridge-to-daz-studio-and-how-do-we-save-renders/227410) (search snippet only).
- FBX export of morphs: use FBX 2012 Binary, tick Morphs, and add an Export rule for "Not Used" morphs in Edit
  Morph Export Rules — [CC5 manual: Daz morph data](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09_Transformer/Importing-DAZ-Assets-with-Morph-Data.htm) (page read).
- Daz bridges (GitHub, `gh api` 2026-10-29): DazToUnreal Apache-2.0 (pushed 2026-01-01, 187 stars); DazBridgeUtils
  Apache-2.0 (2026-01-01); DazToUnity Apache-2.0 (2025-10-24); DazToBlender (LICENSE file: Apache-2.0; 2025-09-04,
  281 stars); DazToRoblox Apache-2.0; DazToC4D, DazToMaya, DazTo3dsMax (2021), DazToO3DE (GitHub: no SPDX);
  StudioFbxImporter Apache-2.0 (2022) — [daz3d org](https://github.com/daz3d) (page read).
- DazBridgeUtils: a C++ library and Daz Script framework for exporting assets, "Normal Map Generation, Texture
  Baking and Mesh Subdivision"; builds against the Daz Studio 4.5+ SDK, FBX SDK 2020.1, OpenSubdiv 3.4.4 and Qt
  4.8.1 — [README](https://github.com/daz3d/DazBridgeUtils) (page read).
- The `.dtu` JSON written by the bridge holds (key names): DTU Version, Asset Name/Type, FBX File, Base FBX File, HD
  FBX File, Materials (Material Name, Material Type, Properties with Name, Value, Data Type, Texture), Morphs,
  MorphLinks, JointLinks (Bone, Axis, Keys of Angle/Value, Scalar, Addend), Subdivisions, PoseData, SkeletonData,
  HeadTailData, JointOrientation, LimitData, LOD settings, Instances; it reads Daz's ERC links and has an automatic
  JCM export — [DzBridgeAction.cpp](https://github.com/daz3d/DazBridgeUtils/blob/HEAD/src/DzBridgeAction.cpp) (code read).
- DazToUnreal's Unreal plugin builds "`<Character>_JCMAnim`" (an Anim Blueprint with a Control Rig node) from the
  `JointLinks`, and maps Iray Uber property names (Diffuse Color, Metallic Weight, Dual Lobe Specular Ratio, SSS
  Color, Transmitted Color, Cutout Opacity) to Unreal materials —
  [DazToUnrealMorphs.cpp, DazToUnrealMaterials.cpp](https://github.com/daz3d/DazToUnreal/tree/HEAD/UnrealPlugin/DazToUnreal/Source/DazToUnreal/Private) (code read).
- DazToUnreal: File → Send To → Daz to Unreal; types Static Mesh, Skeletal Mesh, Animation, Environment; morphs and
  subdivision levels selectable — [README](https://github.com/daz3d/DazToUnreal) (page read).
- DazToBlender: Daz Studio 4.10+, Blender 2.83+ (4.2 LTS recommended); morph sliders in the add-on; subdivision is
  baked or sent as a level-0 Catmull-Clark surface; aniMate animation must be baked to Timeline keys —
  [README](https://github.com/daz3d/DazToBlender) (page read).
- DazBridgeUtils `Extras/` holds bone maps `g8_to_metahuman.json`, `g8_to_mixamo.json`, `g8_to_unity.json`,
  `g8_to_unreal.json`, `g9_to_metahuman.json`, `g9_to_mixamo.json`, `g9_to_unity.json`, `g9_to_unreal_manny.json`
  and rig files for Genesis 8.1 and 9 — [repo tree](https://github.com/daz3d/DazBridgeUtils/tree/HEAD/Extras) (page read).
- Daz's Iray Uber shader is MDL-based — [Daz forum](https://www.daz3d.com/forums/discussion/225361) (search snippet only).
- Genesis 9 is one unified figure (round one, [Introducing Genesis 9](https://free.downloads-cache.daz3d.com/introducing-genesis-9), page read).

### 1.3 Unreal Engine 5.8 (MetaHuman, Fab assets)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Static mesh | FBX, USD, glTF/GLB | Mesh, UVs, LODs (FBX, USD range); glTF one LOD, no collision | Materials only baked (USD: UsdPreviewSurface; glTF: Default Lit, Clear Coat, Unlit, others baked) |
| Skeletal mesh | FBX (morph targets option), USD, glTF | Skeleton, skin weights; FBX morph targets | glTF: no morph-target animation, no clothing assets; USD morph targets **?**; vertex order lost in FBX (matters for MetaHuman) |
| Animation | FBX, USD (AnimSequence exporter), glTF | Bone animation (glTF needs skin weights exported) | Level sequences in glTF: transforms only |
| Level / scene | USD (level exporter: sub-levels as sublayers, foliage, landscape baked), glTF (current level) | Actors, transforms, lights, cameras | Blueprint logic and effects (? not checked) |
| MetaHuman | DCC export zip (`.dna` head + body, `.png`, `.json`), DNA export, geometry export, materials export; `.mhpkg` on Fab | Rig behaviour (RigLogic) in DNA; textures | Grooms out of Unreal (**?** no exporter found) |
| Fab content | `.uasset` packs (Unreal-only) or exchange files (see §1.15) | — | `.uasset` is readable only by Unreal; leaving it means re-export from Unreal |

Facts:
- USDExporter (UE 5.8) classes: UAnimSequenceExporterUSD, UGeometryCacheExporterUSD, ULevelExporterUSD,
  ULevelSequenceExporterUsd, UMaterialExporterUsd, USkeletalMeshExporterUsd, UStaticMeshExporterUsd —
  [API index](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/USDExporter) (UE 5.8 docs, page read).
- FUsdMeshAssetOptions: `bBakeMaterials` — "bake the mesh's assigned material and export these as separate
  UsdPreviewSurface assets"; `bConvertSkeletalToNonSkeletal`; payload files; Lowest/Highest LOD —
  [API](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/USDExporter/FUsdMeshAssetOptions?lang=en-US) (page read).
- FLevelExporterUSDOptionsInner: `bSelectionOnly`, `bExportSublayers` ("export sub-levels as separate layers"),
  foliage layer, landscape LOD range and `LandscapeBakeResolution`, actor folders as empty prims, `RootPrimName`,
  metadata — [API](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/USDExporter/FLevelExporterUSDOptionsInner) (page read).
- The USD feature is "Beta … use caution when shipping with it" — [USD in Unreal](https://dev.epicgames.com/documentation/en-us/unreal-engine/universal-scene-description-in-unreal-engine) (UE 5.8 docs, page read).
- glTF exporter: "glTF does not support multiple levels of detail"; skeletal meshes: morph target animations and
  mesh clothing assets not supported; animation sequences "fully supported … as long as you also export vertex skin
  weights"; level sequences transform tracks only; materials Default Lit, Clear Coat, Unlit, others treated as
  Default Lit, complex inputs baked; lights via KHR_lights_punctual —
  [glTF exporter handling](https://dev.epicgames.com/documentation/en-us/unreal-engine/how-the-gltf-exporter-handles-unreal-engine-content) (UE 5.8, page read).
- glTF exporter extensions: KHR_lights_punctual, KHR_materials_unlit, KHR_materials_clearcoat,
  KHR_materials_variants, KHR_mesh_quantization, KHR_texture_transform —
  [glTF support](https://dev.epicgames.com/documentation/en-us/unreal-engine/gltf-file-format-support-in-unreal-engine) (page read).
- FBX export options include `export_morph_targets`, `map_skeletal_motion_to_root`, `level_of_detail`,
  `bake_material_inputs`; FBX compatibility default 2013 —
  [FbxExportOption Python API](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxExportOption) (search snippet only).
- MetaHuman Creator export tool: DCC Export (zip of `.dna`, `.png`, `.json`; required for MetaHuman for Maya and
  Houdini), Geometry Export (skeletal mesh assets), DNA Export, Materials Export —
  [export tool](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-export-tool-in-unreal-engine) (undated, page read).
- MetaHuman 5.6 conforming "relied on vertex ID data ordering, which is currently lost when exporting FBX from
  Unreal Engine"; 5.7 uses UV mapping to keep vertex IDs so meshes can be sculpted in Blender or ZBrush and
  re-imported — [MetaHuman 5.7 post](https://www.metahuman.com/news/metahuman-5-7-brings-major-improvements-to-body-conforming-with-more-to-come) (search snippet only; the page redirects to a login).
- Epic's "MH Groom Exporter" for Houdini writes groom curves to Alembic "specifically formatted for Unreal" —
  [Houdini groom exporter](https://dev.epicgames.com/documentation/metahuman/houdini-groom-exporter) (search snippet only).

### 1.4 Blender 5.x

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Character | FBX (Python add-on), glTF (Khronos add-on), USD, VRM (add-on) | Mesh, UVs, armature → skeleton, skin, shape keys → blend shapes (USD, glTF, FBX), actions | USD: bendy bones, modifiers other than Armature, absolute shape keys; glTF: 4 joints per set (round one) |
| Materials | USD (UsdPreviewSurface or MaterialX), glTF (PBR + KHR extensions) | Principled-based materials | USD Preview Surface "supports only a limited set of nodes"; MaterialX without displacement |
| Hair / curves | USD (BasisCurves), Alembic | Curves | USD hair: parent strands only, constant colour, no UVs or normals; Alembic: hair as zero-width curves |
| Animation caches | Alembic, USD | Vertex animation, transforms | Alembic: no materials (face-set names only), no armatures |
| Cameras / lights / scenes | USD, glTF, FBX | Perspective cameras (USD), lights (spot via UsdLuxShapingAPI), instancing (experimental) | USD: layers and variants not exported |

Facts (all from Blender's manual source, undated, page read):
- USD import: meshes, primitive shapes, NURBS curves, BasisCurves → curves, points, OpenVDB volumes; skeletons →
  armatures and blend shapes → shape keys (both optional); UsdPreviewSurface → Principled BSDF (lossy); MaterialX
  import not mentioned; cameras, lights (not cylinder/geometry lights), dome → world; Y-up rotated to Z-up,
  `metersPerUnit` honoured — [usd.rst](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/files/import_export/usd.rst).
- USD export: meshes, perspective cameras, curves, lights, hair, point clouds, volumes, armatures → skeletons and
  skinned meshes ("Bendy bones are not supported"); shape keys → blend shapes ("Absolute shape keys are not
  supported"); materials as USD Preview Surface or MaterialX; "requires software utilizing USD 24.03 or greater" for
  Unicode names; UDIMs can't go into USDZ — same page.
- FBX import (5.x): custom normals, subdivision data, vertex colours, each take → an Action, Ignore Leaf Bones; export
  is the FBX add-on — [fbx.rst](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/files/import_export/fbx.rst).
- Alembic: "Hair is exported as animated zero-width curves"; "Alembic has no support for Particle Systems, in the same
  way that it does not support armatures"; material data not exported — [alembic.rst](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/files/import_export/alembic.rst).
- VRM Add-on for Blender: MIT, 1,731 stars, pushed 2026-10-29, Blender 2.93–5.2 — [repo](https://github.com/saturday06/VRM-Addon-for-Blender) (page read).
- glTF-Blender-IO: Apache-2.0, pushed 2026-10-29 — [repo](https://github.com/KhronosGroup/glTF-Blender-IO) (page read).

### 1.5 Maya (Autodesk; reference — paid)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Character | FBX, USD (maya-usd), Alembic; MetaHuman for Maya (DNA) | USD: skeletons, skinClusters via UsdSkel, blend shapes, cameras, lights, NURBS curves, animation | USD correctives/HumanIK (none in UsdSkel) |
| Materials | USD | UsdPreviewSurface (default), MaterialX (incl. OpenPBR reader/writer) | Arnold networks only with Arnold installed |
| Grooms | Alembic (XGen) | Strands for Unreal's groom schema | — |

Facts:
- maya-usd v0.37.0 (2026-07-23), Apache-2.0 (`doc/LICENSE.md`), 915 stars — [repo](https://github.com/Autodesk/maya-usd) (page read).
- Export flags: `-exportSkels` (none/auto/explicit), `-exportSkin` ("export skinClusters via the UsdSkel schema"),
  `-exportBlendShapes`, `-convertMaterialsTo` (default UsdPreviewSurface; plug-ins add more); import `-shadingMode`
  (useRegistry, displayColor, pxrRis), `-readAnimData` — [commands Readme](https://github.com/Autodesk/maya-usd/blob/dev/lib/mayaUsd/commands/Readme.md) (page read).
- Translators in the repo: translatorSkel, translatorBlendShape, camera and light readers/writers, NURBS curve
  reader/writer, MaterialX readers/writers including `mtlxOpenPBRSurfaceReader/Writer` — [repo tree](https://github.com/Autodesk/maya-usd/tree/dev/lib) (page read).
- Unreal's groom Alembic spec names Maya XGen and Shave and a Haircut as sources — [Alembic for grooms](https://dev.epicgames.com/documentation/unreal-engine/using-alembic-for-grooms-in-unreal-engine) (page read).

### 1.6 3ds Max (Autodesk; reference — paid)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Character | FBX, USD (USD for 3ds Max), Alembic | USD: Skin → UsdSkel, Morpher → blend shapes (progressive → in-betweens), CAT/Biped bones (purpose `guide`) | USD import side **?** |
| Materials | USD | USD Preview Surface, Physical Material, MaterialX targets; Material Switcher → variant sets | — |
| Scenes | USD, Datasmith (export plugin 2016–2026) | Cameras, photometric lights, splines → BasisCurves or meshes, vertex and transform animation | — |

Facts:
- USD for 3ds Max export (2025 docs): `.usdc`/`.usda`/`.usdz`; Skin → USDSkel instead of vertex caches; Morpher →
  blend shapes, progressive morphers → in-betweens; Morpher/TurboSmooth must sit below Skin; materials USD Preview
  Surface + Physical Material, MaterialX targets; Z-up default — [Autodesk help](https://help.autodesk.com/cloudhelp/2025/DEU/3dsMax-USD/files/USD-for-3ds-Max/Import-and-export-USD-data-in-Max/GUID-DC04C60D-07CD-4844-AB96-4FDE25CCAD8C.html) (page read).
- Morpher and MaterialX arrived in USD for 3ds Max 0.5; "USD Skel does not support faceVarying Normals" —
  [CG Channel 2023-10-03](https://www.cgchannel.com/2023/10/autodesk-adds-materialx-support-to-usd-for-3ds-max-0-5) (search snippet only).
- Datasmith supports 3ds Max through an export plugin, 2016–2026 — [Datasmith formats](https://dev.epicgames.com/documentation/en-us/unreal-engine/datasmith-supported-software-and-file-types) (UE 5.8, page read).

### 1.7 Houdini (SideFX; reference — paid)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Character / scene | USD (Solaris is built on it), FBX, Alembic | UsdSkel skeleton, SkelAnimation, material bindings; H22 adds blend-shape channels to USD Animation Import and Agent import | — |
| Grooms | Alembic (Epic's MH Groom Exporter) | Strands + attributes for Unreal | — |

Facts:
- SOP Import UsdSkel Character LOP (since 19.0): imports rest geometry and skeleton, the `SkelAnimation` prim, and
  binds materials — [Houdini 22 docs](https://www.sidefx.com/docs/houdini/nodes/lop/kinefx--sopcharacterimport.html) (page read).
- Houdini 22: UsdSkel node renames; Agent SOP USD importer and USD Animation Import SOP "now include blendshape
  channels from skinned primitives with blendshapes" — [What's new: Solaris](https://www.sidefx.com/docs/houdini/news/22/solaris.html) (page read).

### 1.8 Marvelous Designer / CLO (reference — paid)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Garment | OBJ, FBX, Alembic, USD, USDZ, glTF/GLB and VRM (2026.0), caches `.mc`/`.pc2`/`.mdd` | Garment mesh, UVs; simulated animation as Alembic or caches; USD for clothing, trims and avatars | FBX joints only if the avatar came in by FBX; skin-deformed animation only as Alembic (2024.0); pattern data stays in MD |
| Avatar | FBX, USD | — | — |

Facts:
- MD 12.1: "Clothing, trims and character avatars can all be imported or exported as USD files" —
  [CG Channel 2023-05-25](https://www.cgchannel.com/2023/05/clo-virtual-fashion-releases-marvelous-designer-12-1) (page read).
- MD 2024.0: export to "Alembic, FBX or USD"; "animations with skin deformations can currently only be exported as
  Alembic caches"; EveryWear fits and rigs garments; 2024.0.173 adds USD export for UE 5.4 —
  [CG Channel 2024-04-29](https://www.cgchannel.com/2024/04/clo-virtual-fashion-releases-marvelous-designer-2024-0/) (page read).
- MD 2026.0: "new and expanded format support, including glTF and VRM" —
  [Digital Production 2026-04-15](https://digitalproduction.com/2026/04/15/marvelous-designer-2026-0-adds-3d-pencil-and-lacing/) (page read).
- Compatibility table: FBX holds mesh, material, joint, animation, camera ("only Joint that was imported as FBX …
  can be exported as FBX"); Alembic vertex + animation; USDZ export only —
  [MD support](https://support.marvelousdesigner.com/hc/en-us/articles/47358199862553-Compatible-File-Format) (search snippet only; page 403).
- MD converts Daz, Mixamo, CC and MetaHuman avatars "with compatible bone structures" — round one (04, snippet).

### 1.9 ZBrush (Maxon; reference — paid)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Sculpt / mesh | OBJ, FBX (plugin), USD, GoZ, `.ma`, X3D, STL, VRML | SubTools, polygroups, PolyPaint as vertex colour (FBX), "3D layers exported as Blendshapes" (FBX), texture/normal/displacement maps | Bones and skin weights (not listed); subdivision level choice (?) |

Facts:
- Formats: import OBJ, `.ma`, `.mesh`/`.meshb`, GoZ, STL, FBX (plugin), USD; export OBJ, `.ma`, X3D, GoZ, STL,
  VRML, FBX (plugin), USD — [Maxon supported formats](https://www.maxon.net/en/zbrush/features/supported-formats) (© 2026, page read).
- FBX ExportImport plugin: "Export of PolyPaint as vertex coloring", "3D layers exported as Blendshapes", polygroups,
  smooth or hard normals, maps embedded or separate, axis selection; FBX 2009–2014 —
  [Maxon help](https://help.maxon.net/zbr/en-us/Content/html/user-guide/zbrush-plugins/fbx-exportimport/fbx-exportimport.html) (undated, page read).

### 1.10 Mixamo (Adobe; free, closed)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Character | FBX Binary, FBX for Unity, DAE; "With Skin" | Auto-rigged skeleton, weights, mesh, textures | Bone names (`mixamorig`) not page-verified |
| Motion | Same; "Without Skin" (animation only); fps and keyframe reduction settings | Bone animation | — |

Facts:
- Download settings: FBX for Unity / FBX Binary / DAE; With Skin / Without Skin; frames per second; keyframe
  reduction — [Ready Player Me docs](https://docs.readyplayer.me/integration-guides/unity/loading-mixamo-animations),
  [SimLab blog](https://simlab-soft.com/blog/?p=1627) (search snippet only; Adobe's help returns 403, round one).

### 1.11 VRoid / VRM

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Avatar | VRM 0.0 or VRM 1.0 (dress-up only 1.0); XAvatar/XWear | Humanoid bone map, expressions (blend shapes), spring bones per hair chunk, MToon materials, licence metadata in the file | Which parts are separate meshes (?); reduce polygons/materials/bones options change topology |

Facts:
- Export VRM: choose VRM 0.0 or 1.0, optional reduce polygons / materials / bones; expressions from the Expression
  Editor are retained; the dress-up feature exports only VRM 1.0; hair bounce is converted to VRMSpringBone —
  [VRoid help: export](https://vroid.pixiv.help/hc/en-us/articles/38726063278233-How-do-I-export-a-model-as-VRM),
  [VRM 0.x](https://vroid.pixiv.help/hc/en-us/articles/39513600013721-Q-Can-I-export-in-VRM-0-x-format) (search snippet only; pages 403).
- VRM 1.0 carries humanoid, meta, firstPerson, expressions, lookAt, spring bones, node constraints, MToon; meta
  fields set the model's terms — round one (08, page read).
- Open VRM loaders: UniVRM MIT (3,415 stars), three-vrm MIT (2,244), VRM4U MIT (2,001; Unreal runtime), godot-vrm
  MIT (479), VRM Add-on for Blender MIT (1,731) — [GitHub](https://github.com/vrm-c/UniVRM), [VRM4U LICENSE](https://github.com/ruyo/VRM4U) (page read 2026-10-29).

### 1.12 MakeHuman / MPFB2 (open)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Character (MakeHuman 1) | Collada 1.4, FBX (2013 ASCII default), OBJ (+MTL, static), STL, Ogre3D, BVH | Mesh, UVs (OBJ); rig in DAE/FBX not stated on the page (?) | OBJ "not rigged"; exports are one-way (MakeHuman can't read them) |
| Character (MPFB2 in Blender) | Any Blender exporter (FBX, glTF, USD, Alembic) | Rigs `default`, `game_engine`, `cmu_mb`, `mixamo`, `mixamo_unity`, `openpose`, Rigify; 52 ARKit units and visemes as shape keys, carried to clothes; MHCLO clothes as separate meshes | — |

Facts:
- MakeHuman exports: Collada (y-up, decimetre default), FBX (2013 ASCII default; Blender needs binary), OBJ "not
  rigged but rather a static prop", STL, Ogre3D, BVH, light and UV maps —
  [MakeHuman docs](https://static.makehumancommunity.org/makehuman/docs/exports_and_file_formats.html) (undated, page read).
- MPFB2 rigs and face units: round one (05, page read) — [MPFB2 rigs](https://github.com/makehumancommunity/mpfb2/tree/master/src/mpfb/data/rigs).
- MakeHuman 2 (alpha) has glTF export — round one (05).

### 1.13 Substance 3D Painter (Adobe; reference — paid)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Textures / materials | Images via output templates (≈25 formats, 8/16/32-bit); USD asset export | Packed PBR maps per template; with "Export USD asset": texture folder + `.usda` pointing to it + optional `.usd` assembling materials on the mesh; OpenPBR naming (12.1) | Layer stack and smart-material logic stay in Painter; `.sbsar` needs Substance runtime (closed) |
| Mesh | USD (mesh-only export, 8.3+) | Mesh | — |

Facts:
- Painter 8.3+ USD: project creation with "scope and variants", subdivision levels and animation frames; export
  "materials and textures using the USD format"; USD mesh-only export —
  [Painter USD page](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/features/universal-scene-description-usd) (updated 2026-10-08, page read).
- "Export USD asset" output: texture folder, `.usda` pointing to it, optional `.usd` that "assembles materials with
  the original mesh file", optional mesh `.usd` — [export settings](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/export/export-window/export-settings) (2026-10-08, page read).
- 12.1 added OpenPBR naming on export and OpenPBR through USD — [release notes 12.1](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/release-notes/version-12-1) (search snippet only).

### 1.14 Mocap tools (BVH, FBX)

| Asset type | Formats out | Survives | Lost or unverified |
|---|---|---|---|
| Motion (BVH) | BVH | Joint hierarchy with offsets, per-frame channel values, frame time | No mesh, no weights, no rest rotation ("no rotational offset is defined"), no units, Euler order per file |
| Motion (FBX, USD) | Rokoko: FBX, BVH, CSV with HumanIK and Mixamo presets; Move One: FBX, USDC/USDZ, `.blend` | Skeleton + animation; FBX/USD can carry a mesh | Move Pro list (BVH, glTF, C3D) conflicts across help pages |

Facts:
- BVH: HIERARCHY of ROOT/JOINT with OFFSET and CHANNELS, End Site; MOTION with Frames, Frame Time, one line per
  frame; the format "lacks explicit information for how to draw the segments"; "no rotational offset is defined" —
  [BVH description (Wisconsin)](https://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/BVH.html) (1999, page read).
- Rokoko exports FBX (all plans), BVH and CSV, with "Human IK and Mixamo" skeleton presets — round one (04).
- Move One exports `.fbx`, `.usdc`, `.usdz`, `.blend` — [Move help](https://help.move.ai/en/articles/8851539-what-file-formats-are-available-for-exporting) (search snippet only; versions of the page disagree).

### 1.15 Stores (Fab, Sketchfab, Poly Haven, CGTrader-type)

| Store | Formats delivered | Survives | Notes |
|---|---|---|---|
| Fab (Epic) | 3D models: FBX, GLB, glTF, OBJ, USD, USDZ, or 3ds Max/Blender/C4D/Maya files; engine packs `.uasset` (Unreal), Unity, UEFN; MetaHuman `.mhpkg` | Per listing; humanoids should "rig to the MetaHuman skeleton" | Launcher exports exchange formats to UE5, Unity, Blender, Maya, 3ds Max, C4D; native DCC files not exported |
| Sketchfab (KitBash since 2026-08) | Auto-converted glTF, GLB (original/4k/1k textures), USDZ; original upload where offered | PBR materials; USDZ: one animation track, no morph animation | Download API gives glTF/GLB/USDZ only |
| Poly Haven | `.blend`, glTF, USD (usdc), FBX at 1k/2k/4k + PBR maps | Static props, textures, HDRIs | CC0 |
| CGTrader / TurboSquid | Whatever the seller uploads (FBX, OBJ, MAX, BLEND, glTF…) | Per listing | Royalty-free licences |

Facts:
- Fab requirements: most asset types as UEFN source, Unreal Engine or Unity; 3D models also FBX, GLB, GLTF, OBJ, USD,
  USDZ and 3ds Max/Blender/Cinema 4D/Maya; MetaHuman as MHPKG (UE 5.6+, ≤ 1.5 GB); humanoid characters "rig to the
  MetaHuman skeleton" — [Fab format rules](https://dev.epicgames.com/documentation/fab/asset-file-format-and-structure-requirements-in-fab?lang=en-US) (undated, page read).
- Fab Launcher integration: exchange formats `.fbx .gltf .glb .obj .usd .usdz` to UE5, Unity, Blender (3.6, 4.x),
  Maya 2024–26, 3ds Max 2024–26, Cinema 4D 2023–26; "Exporting `.gltf` and `.glb` files to Autodesk Maya is not
  supported" (same for 3ds Max); native DCC formats not supported; engine formats `.uasset/.uproject/.uplugin` via
  Add to Project — [Fab in Launcher](https://dev.epicgames.com/documentation/fab/setting-up-assets-for-fab-in-launcher?lang=en-US) (undated, page read).
- Fab launched 2024-10-22 as successor to the UE Marketplace and the Sketchfab Store —
  [Sketchfab blog](https://sketchfab.com/blogs/community/epics-unified-marketplace-fab-launches-today) (2024-10-22, page read).
- Sketchfab: "When possible, Sketchfab automatically converts every downloadable model to glTF and USDZ formats"; GLB
  in original, 4k and 1k textures; USDZ has "one animation track", "Morph animations are not supported" —
  [help: glTF, GLB and USDZ](https://help.sketchfab.com/en/articles/16152669-gltf-glb-and-usdz) (undated, page read).
- Epic sold ArtStation and Sketchfab to KitBash, announced 2026-08-10; Fab stays with Epic; the Download API offers
  glTF, GLB and USDZ, not source FBX/OBJ — [Digital Production](https://digitalproduction.com/2026/08/12/kitbash-buys-artstation-and-sketchfab/) (2026-08-12, page read).
- Poly Haven model files: blend, gltf, usd (usdc), fbx at 4k/2k/1k plus diffuse, normal (DX and GL), metal, rough,
  AO, ARM maps; no MaterialX — [API](https://api.polyhaven.com/files/wooden_table_02) (page read).

**Assessment:** a JustStage importer set that reads glTF/GLB, USD, FBX, OBJ, Alembic and BVH covers every store and
every free program above; DSON and the sidecars (Daz `.dtu`, CC JSON, MetaHuman DNA) are what lift a Daz, CC or
MetaHuman character from "mesh + skeleton" to "character with correctives and real materials". **Attack:** reading
sidecars ties us to undocumented, vendor-changeable formats (CC's JSON has no public spec; `.dtu` is defined only by
Apache-2.0 code). **Changed:** sidecar readers are optional per-source plugins, never part of the core importer, and
each one is pinned to the producer version it was tested on.

---

## 2 · How CC5, Unreal and Daz pull in foreign assets (and the Blender add-ons)

| App | Workflow | Input | What it does | Runs |
|---|---|---|---|---|
| CC5 | Import FBX/OBJ as prop | FBX, OBJ, iProp | Static prop, "regardless whether the model is bone-skinned rigged or animated"; split into sub-props or merge | Local |
| CC5 | Create Character → Humanoid (Characterization) | Bone-skinned FBX | Set T-pose (profile or by hand), map ≥ 15 basic bones (profile auto-maps known tools), optional facial/extra bones; saved profiles; auto-conversion when the bone structure "complies with the convention" (Maya, 3ds Max, Daz, Blender named) | Local |
| CC5 | Create Character → Creature | FBX | Non-humanoid character with motions; later convertible to humanoid | Local |
| CC5 | AccuRIG | Static humanoid OBJ/FBX | Auto-rig to CC skeleton (round one) | Local (standalone free) |
| CC5 | Transformer | Daz FBX (FBX 2012 Binary, T-pose, morph rules) | Daz G3/G8/G8.1/G9/HD → CC3+ or CC5 HD: shape, morphs (Actor Parts), textures (Basic/Advanced, bake), clothes, hair (often by hand), poses, animations | Local |
| CC5 | Body Wrap (5.2) | FBX (skinned or not), OBJ, iProp | Detect Joints → Align Points → Refine Mesh → Bake Textures; result is a standard CC5 character (SkinGen, clothing, Smart Hair work) | Local (not stated) |
| CC5 | Custom clothes / accessories / hair | FBX (+ `.fbxkey`), OBJ | Round trip through a 3D tool with the key, or new mesh + Transfer Skin Weights; accessory from OBJ/FBX; Smart Hair from card meshes | Local |
| CC5 | Material conversion | Imported "traditional" materials | Apply PBR_V1 substances, bake into 9 channels, shader set to PBR; Digital Human / SSS shader conversion | Local |
| CC5 | Motion import | FBX, BVH, Daz | Through a Characterization profile; batch conversion | Local |
| Unreal | Interchange import | FBX, glTF/GLB, OBJ, MaterialX, images (translators) | Static/skeletal meshes, morph targets, "Convert Statics with Morph Targets to Skeletals", animations + curves, materials or instances, UDIM | Local |
| Unreal | USD Stage / USD import | `.usd/.usda/.usdc/.usdz` | See §4 | Local (Beta) |
| Unreal | Alembic import | `.abc` | Static Mesh, Geometry Cache, or Skeletal Mesh (PCA morph bases); groom Alembic → Groom asset | Local |
| Unreal | Datasmith | 3ds Max, SketchUp, Revit, Rhino, C4D, CAD (STEP, IGES, IFC, JT…) | Whole architectural/CAD scenes; nothing for characters | Local |
| Unreal | IK Rig + IK Retargeter | Any skeletal mesh | Retarget chains (auto-created by keyword), fuzzy chain matching, pelvis, retarget pose with auto-align, op stack; Auto Retarget templates: UE4/UE5 Mannequins, MetaHumans, Stack O Bot | Local |
| Unreal | Mesh to MetaHuman / From Custom Mesh | FBX or OBJ, any topology (From Mesh); MetaHuman topology (From Template); DNA | Fits the MetaHuman template; returns a rigged skeletal mesh with DNA | Identity Solve in the cloud; rig from "MetaHuman Backend" |
| Unreal | Fab | Fab library | `.uasset` packs straight into a project; exchange files via the Launcher | Local after download |
| Daz Studio | OBJ / FBX import | OBJ (main path), FBX/DXF/3DS/DAE via the FBX SDK | Props, or meshes to rig | Local |
| Daz Studio | Transfer Utility | Source figure + target mesh | Copies rigging and weights from the figure (or a projection template), fits to a shape (Item Shape morph, Reverse Source Shape from Target), Auto-Follow morphs, smoothing modifier, rigidity map | Local |
| Daz Studio | Morph Loader Pro | OBJ with identical vertex count and order (base resolution) | New morph on the figure | Local |
| Daz Studio | Bridges | Daz scene | Send To Unreal / Unity / Blender / Maya / C4D / Roblox (FBX + `.dtu`) | Local |
| Blender | Diffeomorphic DAZ Importer | `.duf`/`.dsf` from the user's Daz library | Figures, morphs, JCM drivers (ERC), Iray → Cycles/Eevee, dForce, HD data, hair tools, Rigify/MHX rigs, cameras, lights | Local |
| Blender | CC/iC Blender Tools | CC3/4/5 and iClone 7/8 FBX/OBJ + JSON | Rebuilds skin, eye, teeth materials and expression wrinkles; physics and spring bones; Rigify control rig and retarget; round trip to CC and Unity; DataLink | Local |

Facts:
- CC5 import methods: OBJ drag → prop; FBX → Import FBX panel: Character (Humanoid or Creature) or Prop; Create menu
  and Modify panel buttons; props convert to creature/humanoid later via Characterization —
  [Importing Methods](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Pipeline/Importing-Methods.htm) (undated, page read).
- Humanoid characterization: T-pose from a prepared profile or by rotating bones; "manually map at least 15 basic
  bones"; optional facial and extended bones; the result takes iClone motions, facial animation, puppeteering and
  mocap — [Non-standard character](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Import-Humanoid/Importing-Model-to-Create-Non-Std-Character.htm) (page read).
- Bone-skinned FBX from Maya, 3ds Max, Daz 3D and Blender are "auto-converted into Humanoid characters" when "the
  bone structure of the model complies with the convention structure" —
  [Full Conversion page](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Import-Humanoid/Full-Conversion.htm) (page read).
- Standard characterization profiles cover Mixamo, Maya HIK, 3ds Max Biped, Blender Meta Rig, UE4 — round one (02,
  CC product page, page read).
- Transformer compatibility: CC5 HD & CC3+ base take G3, G8, G8.1, G9 and HD; G9 needs CC5; V3/M3/V4/M4/G1/G2,
  HiveWire and Poser need CC4; body, eyes and teeth "must retain the original base topology"; genitalia "not fully
  supported" — [Compatible Daz characters](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09_Transformer/Compatible-DAZ-Characters.htm) (page read).
- Transformer's manual set includes texture baking, material consolidation, an INI file for loading all Daz textures,
  poke-through fixing, Daz poses and animations, facial hair — [CC5 TOC data](https://manual.reallusion.com/Character-Creator-5/Data/Tocs/5_Chunk1.js) (TOC titles only).
- Body Wrap inputs: iProp (single or multi mesh), FBX ("skinned and non-skinned models"), OBJ ("static mesh
  models"); last step Bake Textures; the result "can then use the features and capabilities available to standard
  CC5 characters" — [Body Wrap quick guide](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.2/09-Body-Wrap/Quick-Guide.htm) (CC 5.2 manual, page read).
- Custom clothes: export FBX with its key, edit in a 3D tool ("editing without changing the topology or deleting
  faces is allowed" for cloth, gloves, shoes), re-import with the key; new garments use Transfer Skin Weights —
  [Creating Custom Clothes](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/08_Cloth/Creating_Custom_Clothes.htm) (page read).
- Static prop from FBX/OBJ "regardless whether the model is bone-skinned rigged or animated"; split into sub-props
  (nodes visible in CC and iClone) or merge — [Static prop](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/09-Import-Props/Importing-Model-to-Create-Static-3D-Prop.htm) (page read).
- PBR conversion: PBR_V1 substances in the Appearance Editor, baked "behind the scene" to "9 channels of the
  material", shader type set to PBR — [Converting to PBR](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/15_PBR_Substance/Converting_Traditional_Materials_to_PBR_Clothes.htm) (page read).
- Unreal Interchange Import Into Level works with FBX, glTF, GLB and MaterialX; skeletal import content Geometry and
  Skinning Weights / Geometry Only / Skinning Weights Only; "Import Morph Targets"; materials as materials or
  instances — [Interchange reference](https://dev.epicgames.com/documentation/en-us/unreal-engine/interchange-import-reference-in-unreal-engine) (UE 5.8, page read).
- Interchange translators (UE 5.8): DDS, Fbx, GLTF, IES, ImageWrapper, JPG, MaterialX, OBJ, PSD, UEJPEG —
  [InterchangeImport API](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/InterchangeImport?lang=en-US) (page read).
- Unreal Alembic import: Static Mesh, Geometry Cache, Skeletal Mesh ("PCA" morph bases, constant vertex count);
  materials from face sets; only tri/quad polygons; NURBS and SubD not supported —
  [Alembic importer](https://dev.epicgames.com/documentation/en-us/unreal-engine/alembic-file-importer-in-unreal-engine) (header UE 5.8, body UE4-era, page read).
- Groom Alembic schema v1.5: `groom_version_major/minor`, optional `groom_width` (default 1 cm), `groom_root_uv`,
  `groom_color`, `groom_guide`, `groom_group_id`, `groom_id`, `groom_closest_guides` / `groom_guide_weights`; names
  "must be lowercase … start with `groom_`" — [Alembic for grooms](https://dev.epicgames.com/documentation/unreal-engine/using-alembic-for-grooms-in-unreal-engine) (UE 5.8, page read).
- Datasmith (UE 5.8): export plugins for 3ds Max 2016–2026, Revit, SketchUp, Navisworks, Rhino, Archicad,
  SOLIDWORKS, VRED; direct import of Cinema 4D, CATIA, Creo, NX, Inventor, Alias and STEP/IGES/IFC/JT/Parasolid;
  "designed for whole scenes" — [Datasmith formats](https://dev.epicgames.com/documentation/en-us/unreal-engine/datasmith-supported-software-and-file-types) (page read).
- IK Retargeter: chains "similar to 'characterizing' a rig"; "Auto Create Retarget Chains" names chains from a
  keyword list with Left/Right by average X; chain mapping by "a fuzzy string match"; Set Pelvis; retarget poses
  imported from sequences or pose assets, Auto Align; op stack with custom C++ ops; Export Selected Animations —
  [IK Rig retargeting](https://dev.epicgames.com/documentation/en-us/unreal-engine/ik-rig-animation-retargeting-in-unreal-engine) (UE 5.8, page read).
- Auto Retargeting templates table: "Common Biped Skeletons — UE4 and UE5 Mannequins; MetaHumans; Stack O Bot";
  unmatched skeletons get a warning or "an error message" — [Auto Retargeting](https://dev.epicgames.com/documentation/unreal-engine/auto-retargeting-in-unreal-engine?lang=en-US) (UE 5.8, page read).
- MetaHuman Creator import tools: From Custom Mesh (biped static or skeletal mesh of non-MetaHuman topology —
  sculpts, scans, AI meshes), From Template (MetaHuman topology or UV layout), From DNA, From Identity —
  [import tools](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-import-tools-in-unreal-engine) (UE 5.7 era, page read).
- From Mesh: "can use any topology"; FBX or OBJ (OBJ above 200,000 vertices); eyes open with visible sclera; the
  Identity Solve "happens in the cloud"; the template mesh is submitted "to the MetaHuman Backend" —
  [From Mesh](https://dev.epicgames.com/documentation/en-us/metahuman/from-mesh) (UE 5.6 context, page read).
- DzFbxImporter imports FBX and, through the FBX SDK, DXF, 3DS and DAE; OBJ "has been intentionally excluded" (use
  DzObjImporter) — [DzFbxImporter](https://docs.daz3d.com/public/software/dazstudio/4/referenceguide/scripting/api_reference/object_index/fbximporter_dz) (page read).
- Transfer Utility (tutorial): source Genesis, target clothing, Source Item Shape → Morph; projection template
  gives "custom weight maps based on a simple example figure"; Auto-Follow; Add Smoothing Modifier; rigidity map for
  parts that "could move, but not change shape"; Reverse Source Shape from Target —
  [Modeling Against a Genesis Shape](https://docs.daz3d.com/public/software/dazstudio/4/userguide/creating_content/rigging/tutorials/modeling_against_a_genesis_shape/start) (undated, page read).
- Morph Loader Pro needs an OBJ with unchanged vertex count and order, exported at base resolution —
  [Daz forum](https://www.daz3d.com/forums/discussion/comment/907049) (search snippet only).
- Diffeomorphic: manifest "Importer for native DAZ files (.duf, .dsf)", Blender ≥ 4.2, GPL-2.0-or-later, maintainer
  Thomas Larsson; modules include `erc.py`, `formula.py`, `dforce.py`, `hd_data.py`, `dbzfile.py`, `hair_tools`,
  `material_tools`, `cycles.py`, `pbr.py`, `camera.py`, `light.py`, `rigify_tools`, `mhx_tools`, `facs_tools`,
  `to_daz_studio` — [Bitbucket API listing](https://api.bitbucket.org/2.0/repositories/Diffeomorphic/import_daz/src/master/) (repo updated 2026-04-08, page read).
- Diffeomorphic on GitHub: created 2026-04-03, 174 stars, pushed 2026-10-26, release `version_5_2_0` 2026-08-10;
  main branch manifest 5.3.0 — [repo](https://github.com/Diffeomorphic/import_daz) (page read).
- Diffeomorphic imports JCMs and applies drivers; Iray → Cycles/Eevee translation credited to Alessandro Padovani;
  Genesis 1/2 unsupported (TriAx); custom shaders unsupported; the user saves a scene and runs an export script for
  the file Blender reads — [Daz forum threads](https://forum.daz3d.com/forums/discussion/comment/6024242/) (search snippet only).
- CC/iC Blender Tools: GPL-3.0, 524 stars, v2.4.4 (2026-09-30), "importing and automatically setting up materials
  for Character Creator 3, 4 & 5 and iClone 7 & 8 character exports"; Rigify, physics, spring bones, expression
  wrinkles, Blender and Unity round trips — [repo](https://github.com/soupday/cc_blender_tools),
  [docs index](https://soupday.github.io/cc_blender_tools/index.html) (page read).

**Assessment:** the reference apps converge on four steps for a foreign character — (1) read the file, (2)
characterise: T-pose plus a bone map, by profile when the source is known and by name/hierarchy guess otherwise, (3)
for a full conversion, wrap the source onto the app's own topology and bake its textures onto the app's UVs, (4)
convert materials into the app's shaders. JustStage needs all four as commands, with per-source profiles (Daz G8/G9,
CC3+/CC5, MetaHuman, Mixamo, VRM, MPFB2, UE Mannequin) as data files. **Attack:** CC and MetaHuman get their best
results by wrapping onto *their* topology, which needs our base mesh decided first (S4's area); the cloud step in
MetaHuman shows the hard part (fitting a rig to arbitrary topology) is where vendors spend server time. **Changed:**
step 3 is specified against "our base mesh" as a parameter, and "characterise without wrapping" (CC's non-standard
character, Unreal's IK Rig) is the first deliverable, since it works with no base mesh at all.

---

## 3 · Open tools for each conversion

| Job | Tool | What it does | Licence | Health | Source |
|---|---|---|---|---|---|
| Read FBX | ufbx | FBX (and OBJ/MTL): meshes, skinning, blend shapes, lights, cameras, NURBS, geometry caches, constraints; "Unified PBR material from known vendor-specific materials" | MIT or public domain | 1,425★, v0.23.1, pushed 2026-10-01 | [repo](https://github.com/ufbx/ufbx) (page read) |
| Read many | Assimp | Imports BVH, DAE, FBX, glTF 1/2, OBJ, USD, X3D…; exports DAE, OBJ, glTF (partial), FBX (experimental) | BSD-3-style | v6.0.5 (round one) | [Fileformats.md](https://github.com/assimp/assimp/blob/master/doc/Fileformats.md) (page read) |
| Read/write USD | OpenUSD (UsdSkel, UsdShade, UsdMtlx) | Full USD | TOST 1.0 (modified Apache-2.0) | v26.11.1 (round one) | [repo](https://github.com/PixarAnimationStudios/OpenUSD) |
| Read glTF / VRM | cgltf, tinygltf, fastgltf; UniVRM, three-vrm, VRM4U, godot-vrm (behaviour refs) | glTF 2.0; VRM 0.x/1.0 | MIT | see round one; VRM loaders 479–3,415★ | [UniVRM](https://github.com/vrm-c/UniVRM) (page read) |
| Read Alembic | Alembic | Caches; Unreal groom schema rides on it | BSD-3 | 1.8.12 (round one) | [repo](https://github.com/alembic/alembic) |
| Read DSON (Daz) | Diffeomorphic DAZ Importer | Full `.duf`/`.dsf` import incl. JCM drivers, Iray materials, dForce, HD, hair | GPL-2.0-or-later | 5.2.0 (2026-08-10) | [repo](https://github.com/Diffeomorphic/import_daz) (page read) |
| Read DSON (Daz) | dufman | Python DSON loader; geometry, modifiers, nodes, UV sets; "extremely early state" | MIT | 7★, 2025-01-30 | [repo](https://github.com/MidnightArrowStudios/dufman) (page read) |
| Daz sidecar + bone maps | DazBridgeUtils / DazToUnreal | `.dtu` writer and reader; G8/G9 → MetaHuman, Mixamo, Unity, UE bone maps | Apache-2.0 | pushed 2026-01-01 | [repo](https://github.com/daz3d/DazBridgeUtils) (page read) |
| MDL → simple PBR | NVIDIA MDL SDK | Distilling ("mapping or simplifying compiled MDL materials to more limited material models"), texture baking; back-ends CUDA PTX, LLVM IR, HLSL, GLSL, native CPU | BSD-3-Clause | 537★, 2026.0.2 (2026-08-31) | [repo](https://github.com/NVIDIA/MDL-SDK) (page read) |
| Material graphs ↔ PBR | MaterialX | Translation graphs `standard_surface_to_gltf_pbr`, `standard_surface_to_usd`, `standard_surface_to_open_pbr`, `open_pbr_to_standard_surface`; TextureBaker (GLSL, MSL, Slang) and `baketextures.py` | Apache-2.0 | v1.39.5 (2026-05-22) | [repo tree](https://github.com/AcademySoftwareFoundation/MaterialX) (page read) |
| Iray/CC params → shaders | DazToUnreal materials; CC/iC Blender Tools; Diffeomorphic | Property-name maps from Iray Uber / CC JSON to target shaders | Apache-2.0 / GPL-3.0 / GPL-2.0+ | active | repos above (code/README read) |
| Auto bone mapping | Godot BoneMapper | Keyword pick-lists ("hip", "pelvis", "waist", "torso", "spine" … "foot", "ankle"), left/right segregation, parent/child search onto SkeletonProfileHumanoid | MIT | Godot master | [source](https://github.com/godotengine/godot/blob/master/editor/scene/3d/bone_map_editor_plugin.cpp) (code read) |
| Retarget (Blender) | BVH-Motion-Retargeter; Rokoko Studio Live; Expy Kit | BVH → Mixamo/UE5/VRM rigs; live retarget; rig conversion | MIT / LGPL-3.0 (GitHub) / no licence file | 74★ / 511★ / 440★ | [GitHub](https://github.com/BacteriaJun/BVH-Motion-Retargeter) (page read) |
| Auto-rig | UniRig, Mesh2Motion, SkinTokens… | See round one 07 (A-tables) | — | — | round one |
| Morph transfer | Deformation Transfer (Sumner & Popović) implementations | Moves a shape's deformation from one mesh to another of different topology | mickare: MIT (215★, 2021); deformxfer: BSD-3 C++ header-only (51★, 2021); Maya blendshape transfer: MIT | stale but small | [mickare](https://github.com/mickare/Deformation-Transfer-for-Triangle-Meshes), [deformxfer](https://github.com/jerenchen/deformxfer) (page read) |
| Mesh wrap | Optimal-step non-rigid ICP; trimesh `nricp_amberg` | Registers our base mesh onto a foreign mesh | MIT | 13★ / trimesh 3.7k★ (round one) | [golkir](https://github.com/golkir/optimal-step-nonrigid-icp) (page read) |
| Weight transfer | Robust Skin Weights Transfer (+ Maya impl.) | Body → garment weights with inpainting | MIT | 144★ / 56★ | [rin-23](https://github.com/rin-23/RobustSkinWeightsTransferCode) (page read) |
| Clothes follow body | Blender Surface Deform (behaviour reference); MPFB2 MHCLO; CharMorph | "allows an arbitrary mesh surface to control the deformation of another"; MHCLO offsets (round one) | GPL (Blender, CharMorph), GPL-3 code + CC0 assets (MPFB2) | — | [surface_deform.rst](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/modeling/modifiers/deform/surface_deform.rst) (page read) |

Facts not in the table:
- Surface Deform's target must not contain "edges with more than two faces" or "concave faces" — same page (page read).
- No open tool was found that combines wrap + weight transfer + morph transfer + texture re-projection the way CC's
  Body Wrap or MetaHuman's From Custom Mesh do; round one (07, C10) reached the same answer for garment fitting.

**Assessment:** build JustStage's import on ufbx (FBX/OBJ), OpenUSD, a glTF reader with VRM, Alembic, and our own
BVH reader; add MaterialX translation graphs as the material bridge and the MDL SDK distiller for MDL sources;
use Godot's BoneMapper behaviour (MIT, usable) as the model for auto-characterisation; own the wrap/morph-transfer
step from the papers. **Attack:** the MDL SDK's richest paths assume NVIDIA (CUDA PTX), which the scope bars from
core parts; Diffeomorphic is GPL, so its code can't enter an MIT JustStage. **Changed:** the MDL distiller is
named only with its native-CPU back-end and as an optional plugin; Diffeomorphic and the CC Blender tools are
behaviour references only, while dufman (MIT) and the Daz bridge code (Apache-2.0) are the licence-compatible
starting points — and whether reading Apache-licensed vendor bridge code fits AGENTS.md's clean-room rule is the
user's call.

---

## 4 · OpenUSD as the bridge

| App | Imports USD | Exports USD | Static mesh | Skinned mesh + skeleton | Blend shapes | Materials | Grooms / curves | Animation | Cameras / lights | Levels / scenes |
|---|---|---|---|---|---|---|---|---|---|---|
| Unreal 5.8 (Beta) | yes (Stage + import) | yes (exporters) | in/out | in/out | in (with in-betweens); out **?** | in: PreviewSurface, MaterialX (OpenPBR, Std Surface, PreviewSurface), MDL; out: baked UsdPreviewSurface | in: GroomAPI on BasisCurves + GroomBinding; out **?** | in: UsdSkel → AnimSequence, transforms; out: anim sequences, level sequences, geometry caches | in/out | in: Stage; out: levels with sub-levels as sublayers |
| CC5 / iClone | no (not found) | yes (Omniverse) | out | out (body + face joints) | out | out: **MDL** only | cards as meshes | out: motions | out: lights | out: one `.usd` + folders |
| Daz Studio | no | no | — | — | — | — | — | — | — | — |
| Blender 5.x | yes | yes | in/out | in/out | in/out (no absolute keys) | in: PreviewSurface; out: PreviewSurface or MaterialX | in: BasisCurves; out: parent strands only | in/out | in/out | no layers/variants out; layers/references not handled in |
| Maya (maya-usd) | yes | yes | in/out | in/out (UsdSkel) | in/out | PreviewSurface, MaterialX incl. OpenPBR | NURBS curves | in/out | in/out | ? |
| Houdini 22 | yes (native) | yes (native) | in/out | in/out (KineFX) | in/out (H22 channels) | material binding on import | Hair procedural LOP (BasisCurves not named) | in/out | ? | native (Solaris) |
| 3ds Max (USD for 3ds Max) | **?** | yes | out | out (Skin → UsdSkel) | out (in-betweens) | out: PreviewSurface, MaterialX | out: splines → BasisCurves | out | out | out (stages as references) |
| Marvelous Designer | yes | yes | garments, trims, avatars | avatars (skinning ?) | ? | ? | — | ? | — | — |
| ZBrush | yes | yes | in/out | — | — | — | — | — | — | — |
| Substance Painter | yes (project mesh) | yes (materials + textures, mesh-only) | in/out | — | — | out: USD material files (OpenPBR naming, 12.1) | — | animation frames in | — | — |
| Fab / Sketchfab / Poly Haven | — | delivered | USD/USDZ files where listed; Sketchfab USDZ "targeted mainly for viewing in AR QuickLook" | — | — | — | — | Sketchfab USDZ: one track, no morph animation | — | — |

Facts:
- UUsdStageImportOptions (UE 5.8): bImportActors, bImportGeometry, skeletal animations ("UAnimSequence skeletal
  animation assets for each encountered UsdSkelAnimQuery"), bImportLevelSequences, bImportMaterials,
  bImportGroomAssets ("Whether to import GroomAssets, GroomCaches and GroomBindings"), bImportSounds
  (UsdMediaSpatialAudio), bImportSparseVolumeTextures (OpenVDB), RenderContextToImport, MaterialPurpose,
  SubdivisionLevel 0–6, NaniteTriangleThreshold, RootMotionHandling —
  [API](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/USDStageImporter/UUsdStageImportOptions?lang=en-US) (page read).
- Unreal USD Stage prims: static and skeletal meshes, HISM, materials ("PreviewSurface and DisplayColor", NVIDIA MDL),
  lights, cameras, variants, animation, blend shapes; runtime loading via Set Root Layer — [USD in Unreal](https://dev.epicgames.com/documentation/en-us/unreal-engine/universal-scene-description-in-unreal-engine) (UE 5.8, page read).
- Unreal MaterialX import targets OpenPBR Surface, Standard Surface, Surface Unlit, USD Preview Surface; three paths:
  `.mtlx` directly, `.mtlx` referenced from USD, MaterialX embedded in a USD stage; Substrate projects convert
  OpenPBR/Standard Surface to Substrate — [MaterialX import](https://dev.epicgames.com/documentation/unreal-engine/importing-materialx-files-in-unreal-engine?lang=en-US) (UE 5.8, page read).
- In UE 5.1 MaterialX was "import-only, and only supports translation of materials using the `standard_surface`
  shading model" — [5.1 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5.1-release-notes?application_version=5.1&lang=en-US) (page read, first 100k characters).
- Unreal's USD blend shape struct holds name, deltas, LODs, in-betweens and an authored-tangents flag; USD blend
  shapes can't differ per LOD — [FUsdBlendShape](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/USDUtilities/FUsdBlendShape?lang=en-US) (search snippet only).
- Grooms from USD use a custom GroomAPI schema on BasisCurves and a GroomBindingAPI (UE 5.1); "native USD only
  supports vertex positions"; groom building is editor-only — [Unreal forum quoting Epic's page](https://forums.unrealengine.com/t/how-does-the-usd-stage-need-to-be-structured-to-get-groom-assets-to-import/2794442) (search snippet only).
- Control Rig on USD: the importer can "bake and directly manipulate skeletal animation from opened USD Stages";
  edits saved back to the USD file — [Control Rig with USD](https://dev.epicgames.com/documentation/unreal-engine/using-control-rig-with-usd-files-in-unreal-engine?lang=en-US) (UE 5.8, page read).
- Blender, Maya, Houdini, 3ds Max, CC, Painter, ZBrush and MD facts: §1 above.

**Assessment:** the user's read is right for Unreal — it exports USD today, and imports more USD than any other
app checked — and USD is a good bridge to Blender, Maya, Houdini and 3ds Max for meshes, skeletons, weights, blend
shapes, animation, cameras, lights and (with MaterialX/PreviewSurface) materials. It does not replace FBX and the
sidecars for CC and Daz: Daz has no USD at all, and CC's USD materials are MDL. Correctives (Daz JCMs, MetaHuman
RigLogic, CC HD correctives) and wrinkle maps cross no app's USD today, so JustStage's own schemas (S8) must define
them, and importers must fill them from sidecars. **Attack:** Unreal's USD is still Beta after several releases,
and its morph-target export is undocumented; a USD-first plan could fail on the one route the user expects most.
**Changed:** treat "Unreal → USD → JustStage" as a route to test on the user's own Unreal projects (`E:\Dev\Unreal`,
RESEARCH §1) before relying on it, with FBX (ufbx) as the fallback for skeletal meshes with morph targets.

---

## 5 · Terms, one line each (no analysis)

- **CC / iClone store content in other apps** — Reallusion Content Policy, "License Update (2025.8.1)": "The
  Standard License allows you to export 3D objects and characters to any other software"; iContent licence is
  Reallusion-only; Extended licence for mass character use in games/XR; AI training only under Enterprise —
  commercial: conditional — [content policy](https://www.reallusion.com/license/content.html) (page read). The content
  EULA (round one) adds that exported models must stay protected so they "cannot be opened or imported into a
  publicly available software application" — [EULA](https://www.reallusion.com/Content/EULA/EULA.htm) (round one, page read).
- **Daz content outside Daz Studio** — Daz EULA: 2D renders allowed; no redistribution; games need extra licences
  (round one, [EULA](https://www.daz3d.com/eula), page read); "An Interactive License is required when using or
  distributing 3D content from the Daz 3D store" in games and apps, offered per product at the creator's choice —
  commercial: conditional — [Interactive License](https://www.daz3d.com/interactive-license-info) (© 2026, page read).
- **MetaHuman outside Unreal** — two readings (S8 owns them): UE EULA "MetaHuman characters and animation to be used
  across all engines and creative software" as Non-Engine Products, no royalty in other engines (search snippet;
  metahuman.com needs a login) vs the DNA Calibration licence's Unreal/Twinmotion limit (round one, page read) —
  commercial: conditional / unclear — [metahuman.com/license](https://www.metahuman.com/license).
- **Fab Standard License** — "enables you to use the assets, including Megascans, in any game engine or tool you
  want"; Personal and Professional tiers; no standalone resale or redistribution (snippet) — commercial: yes —
  [Sketchfab launch post](https://sketchfab.com/blogs/community/epics-unified-marketplace-fab-launches-today) (page read);
  [fab.com/eula](https://www.fab.com/eula) refused (403) — the user reads it.
- **Mixamo** — free, royalty-free commercial use; no redistribution of raw files; no ML training (FAQ 2022) —
  commercial: yes, conditional on those limits — [Adobe FAQ](https://community.adobe.com/t5/mixamo-discussions/mixamo-faq-licensing-royalties-ownership-eula-and-tos/m-p/13234775) (round one, page read).
- **Sketchfab** — downloads carry the author's Creative Commons licence (CC BY, BY-SA, BY-ND, BY-NC and NC
  combinations, CC0; search snippet, [help](https://help.sketchfab.com/hc/en-us/articles/201368589)); store licences
  Standard (no standalone redistribution) and Editorial (no commercial use) — commercial: per model —
  [sketchfab.com/licenses](https://sketchfab.com/licenses) (© 2026 KitBash SF Operations LLC, page read).
- **Poly Haven** — CC0, "You can use our assets for any purpose", redistribution allowed; ToS bars scraping —
  commercial: yes — [licence](https://polyhaven.com/license) (page read).
- **VRM avatars** — the file's own meta fields (`commercialUsage`, `allowRedistribution`, `modification`…) —
  commercial: per file — round one (08).
- **CGTrader Royalty Free** — no resale or giving away "in the form it is downloaded"; only incorporated use —
  commercial: conditional — [CGTrader forum quote](https://cgtrader.com/forum/selling-buying-3d-models/royalty-free-licence) (search snippet only).
- **TurboSquid Standard** — royalty-free in any personal or business project; no redistribution in extractable form
  — commercial: conditional — [licence tiers](https://www.turbosquid.com/turbosquid-license-tiers) (search snippet only).

Assessment (no legal reading): every commercial source except Poly Haven, CC0 Sketchfab models and VRM files that
allow it restricts redistributing the asset in a form others can extract. A JustStage project that embeds an
imported CC, Daz, Fab or Mixamo asset in an open, readable file would be that form. Round one's rule — importers keep
a provenance and licence record per asset, and projects reference imported content rather than embed it (08 §9) —
covers this; the Reallusion "cannot be opened or imported into a publicly available software application" line
is for the user to read.

---

## Couldn't verify / open

- **Blocked, the user reads them:** fab.com `/eula` and `/cla` (403); metahuman.com licence and news (login);
  vroid.pixiv.help and vroid.com (403); support.marvelousdesigner.com format table (403); helpx.adobe.com
  Substance format table and Mixamo help (403).
- **Unreal:** whether the USD skeletal-mesh exporter writes morph targets as UsdSkel blend shapes (no doc found);
  whether any Unreal exporter writes grooms (none found); the glTF *import* feature list (page served only a title);
  the current text of the USD groom schema page (only a forum quote); Fab plugin version floor ("5.3 and above" is a
  machine-made video summary).
- **CC5:** whether CC 5.x USD export still uses MDL (the tracker answer is CC 4.4 / 2024); GLB export in the UI;
  whether Body Wrap runs locally; the CC JSON sidecar's structure (no public spec; known only through the Blender
  tools); whether CC imports USD (no manual topic found).
- **Daz:** how plain FBX export treats JCMs, strand-based hair and dForce (only bridge and Diffeomorphic behaviour
  read); the full Diffeomorphic feature list (blog not read; module names only); Daz Studio 6's export formats.
- **3ds Max USD import**, Blender MaterialX *import* through USD, iClone 8 USD import — not found.
- **Mixamo** bone names and current terms (S7 has the ToU item); **VRoid** mesh split (face/body/hair) — snippets
  only; **Move AI** export list — help pages disagree.
- **Morph transfer quality:** the open deformation-transfer code is small and stale (2021); no benchmark against
  CC Body Wrap or MetaHuman From Custom Mesh was found.
- Not searched (out of S9's list): Unity as a source; Cinema 4D's exporters; Cascadeur's export formats.
