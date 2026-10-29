# Research 08 — Standards, second pass (2026-10-29)

Second pass on section S8 of [`2026-10-29-research-second-pass.md`](2026-10-29-research-second-pass.md). Round one:
[`2026-10-29-research-08-standards.md`](2026-10-29-research-08-standards.md). Clean-room: public docs, specs and
behaviour only. Bone and field *names* are listed as interface facts. No code, meshes or assets were copied.

**How to read this.** Each fact carries its source URL, the source's date (or doc version), and **page read**
(I fetched the page or the doc/code source file and read the cited text) or **search snippet only**.
"Source file" means a raw file from the project's own docs or code repo, read as text. Facts are bullets.
**Assessment:** lines are my judgement, kept apart from the facts.

**Access this session.**
- Blender: I didn't use docs.blender.org. The manual's source (`projects.blender.org/blender/blender-manual`,
  raw files, branch `main`, which is the Blender 5.4 Alpha manual) and the developer docs' source
  (`projects.blender.org/blender/blender-developer-docs`) both served text (HTTP 200). Code came from
  `raw.githubusercontent.com/blender/blender/main`.
- GitHub API calls went through `gh api` (read-only) after the coordinator's note.
- Refused or login-walled, not worked around: helpx.adobe.com (403), fab.com/eula (403), unrealengine.com/eula/mhc
  (403), the unrealengine.com State of Unreal 2025 news page (403), metahuman.com (redirects to an Epic login),
  polyhammer.com (308), support.marvelousdesigner.com (403). The Mixamo, Fab and MetaHuman terms rest on other
  sources, named in each place.
- One PDF (the AOUSD CMI charter) was saved automatically by the fetch tool to the session's tool-results folder.
  I extracted its text locally with `pdftotext`. Nothing was downloaded on purpose.

Blender versions as of today: 5.2 LTS released 2026-07-14; 5.3 is in **Beta** until 2026-11-04; 5.4 is in
**Alpha** until 2027-02-03 — [5.2](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.2/index.md),
[5.3](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.3/index.md),
[5.4](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.4/index.md) —
page read (source files). Manual `main` describes some 5.3 features (marked below).

---

## Top findings

1. **MCP 2026-07-28 removed the `initialize` handshake: confirmed at the spec's own changelog.** Every request
   now carries its protocol version and client capabilities in `_meta`. Servers MUST implement `server/discover`.
   Protocol-level sessions (`Mcp-Session-Id`), `ping` and `logging/setLevel` are gone, and tasks moved to an
   official extension. [MCP changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
2. **No AOUSD character or skeleton spec exists yet, but the work has started.** AOUSD's Characters, Motion
   and Interactivity Interest Group was chartered 2026-03-02, with a review due March 2027. Its scope covers
   character motion and posing, pose-driven deformation and rig nodes. As an interest group it "cannot develop,
   propose or publish any normative documents (e.g., schemas)". A SIGGRAPH 2026 report says Meta announced a
   character-representation working group, with Pixar, Apple, Autodesk, Netflix, SideFX and Amazon taking part.
   [CMI charter](https://aousd.org/wp-content/uploads/sites/28/2026/03/26.03.02-AOUSD-Characters-Motion-and-Interactivity-Interest-Group-Charter-Approved-1.pdf),
   [3DVF 2026-07-21](https://3dvf.com/en/siggraph-2026-the-future-of-rigging-siggraph-asia-the-experience-hall-and-the-computer-animation-festival/)
3. **A USD cloth-and-hair physics schema is proposed, not shipped.** "Deformable Body Physics in USD" (OpenUSD
   proposals PR #111, opened 2026-06-23, open, from the AOUSD Physics WG) extends `UsdPhysics` to volumes,
   surfaces ("cloth, shells") and curves ("hair, rods"). Today's `UsdPhysics` covers rigid bodies only.
   [PR #111](https://github.com/PixarAnimationStudios/OpenUSD-proposals/pull/111),
   [UsdPhysics](https://openusd.org/release/api/usd_physics_page_front.html)
4. **OpenUSD is growing a rig-evaluation layer: OpenExec.** It had a preview in 25.08, and 26.08 added
   "invertible rigs" (`IrJointScope`, `IrFkController`, `IrSwitchController`), marked "not yet ready for
   production use". Pixar plans the execution system and parts of a rigging object model, with "no immediate
   plans" to open its deformer library.
   [OpenUSD CHANGELOG](https://raw.githubusercontent.com/PixarAnimationStudios/OpenUSD/release/CHANGELOG.md),
   [OpenExec proposal](https://raw.githubusercontent.com/PixarAnimationStudios/OpenUSD-proposals/main/proposals/openexec/README.md)
5. **UsdSkel blend shapes do carry normals.** `UsdSkelBlendShape` has `normalOffsets` next to `offsets` and
   `pointIndices`, and in-between shapes can carry optional normal offsets. Blender's USD importer reads offsets,
   point indices and weight animation. Its converter has no code for in-betweens or normal offsets, and the
   importer "does not yet handle" layers and references.
   [BlendShape](https://openusd.org/release/api/class_usd_skel_blend_shape.html),
   [InbetweenShape](https://openusd.org/release/api/class_usd_skel_inbetween_shape.html),
   [Blender usd_skel_convert.cc](https://raw.githubusercontent.com/blender/blender/main/source/blender/io/usd/intern/usd_skel_convert.cc)
6. **Open FBX writers exist, which changes round one's "FBX export needs Autodesk's SDK".**
   - **ufbx_write** (by ufbx's author, MIT or Unlicense) is a single-file C exporter: binary or ASCII, FBX 7500,
     with skin, blend-shape, animation and material elements. It is marked "work-in-progress".
   - **Assimp**'s FBX exporter (BSD-style licence, "experimental") writes FBX 7.5 in both forms.
   - Blender's own Python exporter (GPL) writes blend shapes.

   [ufbx-write](https://github.com/ufbx/ufbx-write),
   [Assimp formats](https://raw.githubusercontent.com/assimp/assimp/master/doc/Fileformats.md)
7. **Blender's default FBX importer is now C++ on top of ufbx**: experimental in 4.5, default since 5.0. It drops
   the Forward/Up axis and bone-orientation options, because "FBX file itself specifies the axes fairly clearly".
   The legacy Python importer keeps them.
   [4.5 notes](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/4.5/pipeline_assets_io.md),
   [5.0 notes](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.0/pipeline_io.md)
8. **Blender's undo, from its developer docs and code.**
   - One stack holds steps of different types (global/memfile, edit-mode, sculpt, paint, text). It is "fully
     relative": reaching a step means loading every step in between.
   - Global undo writes the database as an in-memory .blend. Chunks identical to the previous step are shared,
     not copied.
   - Operators push a step when they return `FINISHED` with the `UNDO` flag, which is "mandatory if the operator
     modifies Blender data".

   [undo.md](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/features/core/undo.md),
   [BLO_undofile.hh](https://raw.githubusercontent.com/blender/blender/main/source/blender/blenloader/BLO_undofile.hh),
   [rna_wm.cc](https://raw.githubusercontent.com/blender/blender/main/source/blender/makesrna/intern/rna_wm.cc)
9. **Blender's extension permissions are disclosure, confirmed in its manual.** "Blender cannot prevent
   third-party add-ons from violating" the online-access rule. The 5.3 asset-library extension's `scripts`
   permission is something "Blender doesn't enforce".
   [addons.rst](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/advanced/extensions/addons.rst),
   [asset_libraries.rst](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/advanced/extensions/asset_libraries.rst)
10. **"Blender does not have the concept of asset versions."** The remote listing gives each asset a Blender
    version range (`bl_versions` min/until) and each file a SHA256 hash. 5.3 (Beta) adds per-Blender-version
    replacement files named `asset@b5_3.blend`. Asset metadata fields are catalog_id, tags, author, description,
    license, copyright, preferred import method and custom properties.
    [remote_asset_libraries.rst](https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/files/asset_libraries/remote_asset_libraries.rst),
    [openapi.yaml](https://raw.githubusercontent.com/blender/blender/main/scripts/modules/_bpy_internal/assets/remote_library/blender_asset_library_openapi.yaml)
11. **Export targets' axes, now on pages.** Unity: "left-handed coordinate system: the positive x-axis points to
    the right, the positive y-axis points up, and the positive z-axis points forward", and 1 unit = 1 m for
    physics. Unreal 5.8: left-handed, Z up, X forward, Y right, centimetres. Blender: "Y Forward, Z Up".
    VRM 1.0 defines **no** bone local axes: only a T-pose by appearance and positive uniform scale.
    [Unity](https://docs.unity.com/en-us/engine/6000.5/manual/scripting/programming-math/unity-engine-math/class-quaternion),
    [Unreal](https://dev.epicgames.com/documentation/unreal-engine/coordinate-system-and-spaces-in-unreal-engine?lang=en-US),
    [VRM tpose.md](https://raw.githubusercontent.com/vrm-c/vrm-specification/master/specification/VRMC_vrm-1.0/tpose.md)
12. **Skeleton vocabularies, filled in.**
    - HumanIK: 15 required nodes, plus Spine1–9, Neck1–9, roll bones, fingers 1–4, an ExtraFinger and a
      Reference node.
    - Mixamo uses HumanIK names with a `mixamorig` prefix.
    - Rigify's human metarig has 159 bones: 67 body and 92 face.
    - MetaHuman head LOD0 has 713 joints and 669 blend shapes.
    - CC5 HD has 262 expression and 128 corrective sliders (390), plus 52 non-linear sliders.
    - The full UE5 Mannequin bone list is on no public page I could read (count 89 only).

    [HIK](https://help.autodesk.com/cloudhelp/2026/ENU/MotionBuilder-Character-Animation/files/Character-Animation/HIK-character-in-MotionBuilder/GUID-A900A0BA-A1A6-4707-A6AE-26FE8F49BEC6.html),
    [MetaHuman LODs](https://dev.epicgames.com/documentation/metahuman/platform-support-and-lod-specifications-for-metahumans),
    [CC5 HD](https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/HD-Facial-Profile-Intro.htm)
13. **MetaHuman terms, two readings with dates.**
    - Epic, 2025-06-03: "the EULA has been updated so that MetaHumans can be used in any engine". CG Channel,
      2025-06-04: free under $1M a year, but no training of AI models.
    - The MetaHuman DNA Calibration LICENSE: "may only be used in conjunction with Unreal Engine and Unreal
      Engine-based products". It was committed 2022-11-29 and never changed.

    [5.6 release](https://forums.unrealengine.com/t/metahuman-5-6-release/2539165),
    [DNA LICENSE](https://raw.githubusercontent.com/EpicGames/MetaHuman-DNA-Calibration/main/LICENSE)
14. **Unity now ships a first-party MCP server**: Unity MCP in the AI Assistant package 2.0.0-pre.1, stdio to a
    relay, then named pipes or Unix sockets to the Editor, with user approval for outside clients. This corrects
    round one's "no first-party MCP from Unity". I found none from Autodesk or SideFX.
    [Unity MCP](https://docs.unity3d.com/Packages/com.unity.ai.assistant@2.0/manual/unity-mcp-overview.html)
15. **No benchmark of WebAssembly copy cost on large meshes was findable.** The facts that bear on it:
    - The Component Model is "shared-nothing", so data crossing a component boundary is copied. Zero-copy memory
      mapping is an open design issue (#568, 2025-10-15).
    - Wasm 3.0 (2025-09-17) adds 64-bit memory (4 GB → 16 EB in theory; the web caps it at 16 GB).
    - A plain-module host (Wasmtime) can read guest memory in place.

    [CM #568](https://github.com/WebAssembly/component-model/issues/568),
    [Wasm 3.0](https://webassembly.org/news/2025-09-17-wasm-3.0),
    [Wasmtime Memory](https://docs.rs/wasmtime/latest/wasmtime/struct.Memory.html)

---

## S8.1 · Blender, from the manual's and the code's source

### Operator `poll` and `execute` rules

- `poll(context)` is "Test if the operator can be called or not", returns a boolean `visible`, and is optional (`FUNC_REGISTER_OPTIONAL`, `FUNC_NO_SELF`); `execute`, `invoke`, `modal`, `check`, `draw` and `cancel` are also optional callbacks. — https://raw.githubusercontent.com/blender/blender/main/source/blender/makesrna/intern/rna_wm_api.cc — main, 2026-10-29 — **page read (source file)**
- `bl_options` texts: `REGISTER` "Display in the info window and support the redo toolbar panel"; `UNDO` "Push an undo event when the operator returns `FINISHED` (needed for operator redo, mandatory if the operator modifies Blender data)"; `UNDO_GROUPED` "Push a single undo event for repeated instances of this operator"; also `BLOCKING`, `MACRO`, `GRAB_CURSOR(_X/_Y)`, `DEPENDS_ON_CURSOR`, `PRESET`, `INTERNAL` ("Removes the operator from search results"), `MODAL_PRIORITY`. — https://raw.githubusercontent.com/blender/blender/main/source/blender/makesrna/intern/rna_wm.cc — main — **page read (source file)**
- `execute` returns `{'FINISHED'}` or `{'CANCELLED'}`; `CANCELLED` means no change and no undo step. — https://raw.githubusercontent.com/blender/blender/main/doc/python_api/examples/bpy.types.Operator.0.py — main — **page read (source file)**
- Without `UNDO`, an operator that edits data "will at best corrupt the undo stack"; "In many cases, this can even lead to data corruption and crashes". If an error happens after data was changed, return `FINISHED` unless the change can be fully undone. — https://raw.githubusercontent.com/blender/blender/main/doc/python_api/examples/bpy.types.Operator.1.py — main — **page read (source file)**
- "Some operators don't have an execute() function, removing the ability to be repeated from a script or macro." `bpy.ops` calls `execute()` by default; buttons and menus follow `UILayout.operator_context` (usually `invoke()`); "Running an operator via a key shortcut always uses invoke(), and this behavior cannot be changed." Operator properties are registered as arguments and "saved for operator undo/redo". — https://raw.githubusercontent.com/blender/blender/main/doc/python_api/examples/bpy.types.Operator.2.py — main — **page read (source file)** (this re-checks round one's snippet)
- Modal operators run on each new event until they return `FINISHED` or `CANCELLED`; `invoke()` starts them by returning `RUNNING_MODAL`. — https://raw.githubusercontent.com/blender/blender/main/doc/python_api/examples/bpy.types.Operator.6.py — main — **page read (source file)**
- Blender's own list of operator limits for scripting: you "Can't pass data such as objects, meshes or materials to operate on (operators use the context instead)"; the return value is only success/cancel; and "poll function can fail where an API function would raise an exception giving details". `poll_message_set` exists to explain failures but "it's currently not used much". — https://raw.githubusercontent.com/blender/blender/main/doc/python_api/rst/info_gotchas_operators.rst — main — **page read (source file)**
- Some operators "are only intended for use in a specific context" (e.g. `bpy.ops.object.modifier_copy`, `bpy.ops.buttons.file_browse`). — same file — **page read (source file)**

Assessment: this supports round one's rule (every command runs from explicit parameters, never from UI context)
with Blender's own words: context-only operators, opaque `poll` failures and success-only results are the
scripting pain points it names.

### Undo system internals

- "Undo is organized as an 'undo stack' storing a list of 'undo steps'"; "Typically, only data is stored and managed in undo, UI changes are not." — https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/features/core/undo.md — dev docs main (marked "WIP" notes) — **page read (source file)**
- Steps are relative or absolute and stateful or differential; "Currently, Blender undo stack is fully relative", so reaching a step loads all steps in between; differential steps are applied or unapplied, and undoing step n processes step n+1. — same — **page read (source file)**
- "There is a single stack that gathers steps of different types (like global undo, edit modes undo, sculpt or paint undo, etc.)"; "skipped" steps hold intermediate states and never become active; undo push "is controlled by the operator management system". — same — **page read (source file)**
- Code layout: `ed_undo.cc` (operators, history), `undo_system.cc` (stack), and per-type `UndoType` implementations (`sculpt_undo.cc`, `memfile_undo.cc`, …); memfile undo uses the .blend read/write code. — same — **page read (source file)**
- Undo types declared in the kernel: IMAGE, MEMFILE, PAINTCURVE, PARTICLE, SCULPT, TEXT; each `UndoType` has `step_encode`/`step_decode` callbacks; the stack can be limited by step count and memory (`BKE_undosys_stack_limit_steps_and_memory`). — https://raw.githubusercontent.com/blender/blender/main/source/blender/blenkernel/BKE_undo_system.hh — main — **page read (source file)**
- A `MemFileChunk` with `is_identical` "doesn't own the memory, it's shared with a previous #MemFileChunk"; some data is not re-serialised because "the undo-step can take ownership of it without making a copy". — https://raw.githubusercontent.com/blender/blender/main/source/blender/blenloader/BLO_undofile.hh — main — **page read (source file)**
- Preferences: Undo Steps (range 0–256, "smaller values conserve memory"), Undo Memory Limit in MB (0 = unlimited), Global Undo (actions outside Edit Mode). — https://raw.githubusercontent.com/blender/blender/main/source/blender/makesrna/intern/rna_userdef.cc and https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/editors/preferences/system.rst — main — **page read (source files)**
- Scripts should "assume that undo and redo always invalidates all `bpy.types.ID` instances"; the "Modern undo/redo system does not systematically invalidate all pointers anymore" for unchanged data, with no guarantee. — https://raw.githubusercontent.com/blender/blender/main/doc/python_api/rst/info_gotchas_crashes.rst — main — **page read (source file)**
- "Adjust Last Operation" (F9) re-runs the last operator with changed parameters; Undo History lists recent actions. — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/interface/undo_redo.rst — manual main — **page read (source file)**

Assessment: Blender answers round one's open question ("global snapshot vs per-command") with **both**: one
history stack whose steps are typed. General edits use a deduplicated whole-database snapshot. Heavy modes
(edit mesh, sculpt) use their own step types. The redo panel works by undo plus re-running with new parameters.

### Extension manifest permissions text

- Permissions are *files*, *network*, *clipboard*, *camera*, *microphone*; "Each permission should be followed by an explanation (short single-sentence, up to 64 characters, with no end punctuation)." Comment text: files "for access of any filesystem operations", network "for internet access", clipboard "to read and/or write the system clipboard", camera "to capture photos and videos", microphone "to capture audio". — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/advanced/extensions/getting_started.rst — manual main — **page read (source file)** (re-checks round one's snippet)
- Required manifest fields: `schema_version` ("use 1.0.0"), `id`, `version` (semver), `name`, `tagline` (≤64 chars), `maintainer`, `type` ("add-on", "asset-library", "theme"), `blender_version_min` (≥ 4.2.0), `license` (SPDX); optional `blender_version_max`, `website`, `copyright`, `tags`, `platforms` (windows-x64, windows-arm64, macos-x64, macos-arm64, linux-x64), `wheels`, `permissions`, `[build]`. Empty values are not allowed. — same — **page read (source file)**
- Add-ons using the internet "must check for the (read-only) property `bpy.app.online_access`"; "Blender cannot prevent third-party add-ons from violating this rule." — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/advanced/extensions/addons.rst — manual main — **page read (source file)**
- Asset-library extensions (`type = "asset-library"`, needs `blender_version_min = "5.3.0"`) "only support the `scripts` permission … Blender doesn't enforce it"; the manifest holds only `[asset_library] remote_url`; optional `[asset_library.auth]` (TOKEN); "Assets can't be bundled with extensions". — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/advanced/extensions/asset_libraries.rst — manual main (5.3 feature) — **page read (source file)**

### Asset metadata fields (and the remote listing)

- Asset Details shows Name, Source (the .blend path), License, Copyright, Description, Author ("Not used by Blender itself" for the last four), Preview, Tags ("do not have any meaning to Blender") and Preferred import method. "Only metadata of assets contained in the current blend-file can be edited." — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/editors/asset_browser.rst — manual main — **page read (source file)**
- Catalogs: path + UUID + optional simple name; the UUID "is what is stored in the asset" and gives the catalog its identity; file `blender_assets.cats.txt` (backup `…~`), lines `{UUID}:{path}:{simple name}`, first line `VERSION 1`. — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/files/asset_libraries/catalogs.rst — manual main — **page read (source file)** (re-checks round one's snippet)
- Remote library rules: each .blend "should be **independent**" (pack textures); "Blender does not have the concept of **asset versions**" (only same/different); previews ≥256×256, WebP preferred or PNG; listing made by `blender -b -c asset_listing generate`; `_asset-library-meta.json` holds `api_versions.v1` (URL + SHA256 hash), name and contact. — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/files/asset_libraries/remote_asset_libraries.rst — manual main — **page read (source file)**
- Server requirements: "MUST" send `Content-Length` and ignore query strings; conditional requests (ETag / Last-Modified) "highly recommended"; access tokens are supported. — same — **page read (source file)**
- 5.3 (Beta): per-version replacement files named `my_asset@b5_3.blend`, asset-library extensions, access tokens. — https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.3/assets.md — 5.3 Beta notes — **page read (source file)**
- Listing schema (OpenAPI, GPL): `AssetV1` = name, id_type, files, thumbnail, meta, `bl_versions` {min, until}; `AssetMetadataV1` = catalog_id, preferred_import_method, tags, author, description, license, copyright, properties; `FileV1` = path, url, size_in_bytes, hash, blender_version; `CatalogV1` = path, simple_name, uuids; URLs are fetched as `GET {URL}?hash={HASH}` for cache-busting, SHA256 only. — https://raw.githubusercontent.com/blender/blender/main/scripts/modules/_bpy_internal/assets/remote_library/blender_asset_library_openapi.yaml — main (© 2026) — **page read (source file)**

Assessment: round one's asset-library rec holds (folder, self-contained file per asset, UUID catalogues, static
HTTP listing). Its "Changed" line, which added an explicit asset version, is still needed: Blender itself says
it has none. Blender's metadata gives the minimum field set (author, licence, copyright, description, tags).

### USD import of UsdSkel and blend shapes

- Import options: "Shape Keys — Imports USD blend shapes as Blender's Shape Keys"; "Armatures — Imports USD skeletons as Blender's Armatures"; "Apply Unit Conversion Scale" uses the stage's `metersPerUnit`. — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/files/import_export/usd.rst — manual main — **page read (source file)**
- "the importer does not yet handle certain USD composition concepts, such as layers and references"; USD prims become Blender objects. — same — **page read (source file)**
- Export: shape keys → USD blend shapes ("Absolute shape keys are not supported"); armatures → UsdSkel skeletons and skinned meshes ("Bendy bones are not supported"; other modifiers not applied); "Only Deform Bones" option; hair is "limited to parent strands". — same — **page read (source file)**
- Curves: `UsdGeomBasisCurves` import as Curves, `UsdGeomNurbsCurves` as meshes. — same — **page read (source file)**
- The skeleton converter reads blend-shape `offsets` and `pointIndices`, maps `blendShapeWeights` time samples to a shape-key action, reads joint indices/weights (vertex or constant interpolation only) and bind transforms. A search of the file finds no code for in-betweens or normal offsets. — https://raw.githubusercontent.com/blender/blender/main/source/blender/io/usd/intern/usd_skel_convert.cc — main — **page read (source file)**; the absence is from text search of that one file.

### FBX importer axis and bone options

- The default importer (`bpy.ops.wm.fbx_import`) has only Scale, Custom Properties, Enums As Strings, Custom Normals, Subdivision Data, Vertex Colors, Material Name Collision, Animation Offset and Ignore Leaf Bones; each FBX take becomes an Action with one slot per object. "To export FBX files use the FBX Add-on." — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/files/import_export/fbx.rst — manual main — **page read (source file)**
- The C++ importer, "based on ufbx", came in 4.5 as experimental: 3×–15× faster, reads ASCII and pre-7.1 binary. It left out Manual Orientation and Forward/Up Axis ("FBX file itself specifies the axes fairly clearly. USD/glTF/Alembic also do not have settings to override them"), Automatic Bone Orientation (it "often produces 'nonsensical bones'"), Force Connect Children, Primary/Secondary Bone Axis, Use Pre/Post Rotation and Apply Transform. — https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/4.5/pipeline_assets_io.md — 4.5 notes — **page read (source file)**
- Since 5.0 the C++ importer is the default and the Python importer is "legacy"; add-ons should move from `bpy.ops.import_scene.fbx` to `bpy.ops.wm.fbx_import`. — https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.0/pipeline_io.md — 5.0 notes — **page read (source file)**
- The C++ importer creates shape keys from FBX blend deformers (`import_blend_shapes`). — https://raw.githubusercontent.com/blender/blender/main/source/blender/io/fbx/importer/fbx_import_mesh.cc — main — **page read (source file)**
- Legacy add-on: "Blender uses Y Forward, Z Up (since the front view looks along the +Y direction)"; Y-up apps need "-Z Forward, Y Up"; "FBX bones seem to be -X aligned, Blender's are Y aligned"; options Primary/Secondary Bone Axis, Automatic Bone Orientation, Force Connect Children, Ignore Leaf Bones (most marked "todo" in the manual). — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/files/import_export/fbx_legacy.rst — manual main — **page read (source file)**
- The legacy manual still says the exporter does not write "Vertex shape keys". The exporter code writes `BlendShape` and `BlendShapeChannel` (`fbx_data_mesh_shapes_elements`, add-on 5.15.0), and the 5.1 notes say it "now also exports shapekey normals". **The manual is stale.** — https://raw.githubusercontent.com/blender/blender/main/scripts/addons_core/io_scene_fbx/export_fbx_bin.py, https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.1/pipeline_io.md — **page read (source files)**

### The Rigify bone list

- Rigify 0.6.10 is a core add-on bundled in Blender (`scripts/addons_core/rigify`), GPL-2.0-or-later; it "only automates the creation of the rig controls and bones" and "does not attach the rig to a mesh"; generated rigs work without Rigify. — https://raw.githubusercontent.com/blender/blender/main/scripts/addons_core/rigify/__init__.py, https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/addons/rigify/introduction.rst — **page read (source files)**
- The human metarig creates **159 bones**: 67 body + 92 face (counted from `edit_bones.new(...)` calls). Rig types on chain heads: 1 `spines.basic_spine`, 1 `spines.super_head`, 2 `limbs.arm`, 2 `limbs.leg`, 2 `limbs.super_palm`, 10 `limbs.super_finger`, 6 `basic.super_copy`, 1 `faces.super_face`. — https://raw.githubusercontent.com/blender/blender/main/scripts/addons_core/rigify/metarigs/human.py — main — **page read (source file)**; counting is mine.
- Body bone names: `spine`, `spine.001`–`spine.006`; `pelvis`, `thigh`, `shin`, `foot`, `toe`, `heel.02`, `shoulder`, `breast`, `upper_arm`, `forearm`, `hand`, `palm.01`–`palm.04` (each `.L`/`.R`); fingers `thumb`, `f_index`, `f_middle`, `f_ring`, `f_pinky` `.01`–`.03` `.L`/`.R`. Face bones include `face`, `jaw`, `chin`, `nose`, `lip.T/B`, `lid.T/B`, `brow.T/B`, `cheek.T/B`, `ear`, `forehead`, `temple`, `teeth.T/B`, `tongue` (with `.001`… segments). — same — **page read (source file)**
- The generated rig puts deforming bones in the *DEF* collection; legacy-face eye and teeth bones are not deforming; mechanism bones use `MCH-` (e.g. `MCH-spine.003`). — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/addons/rigify/basics.rst — **page read (source file)**

### Blender's own axes and units

- "Blender uses Y Forward, Z Up (since the front view looks along the +Y direction)." — usd.rst and fbx_legacy.rst (manual main) — **page read (source files)**
- Unit System None/Metric/Imperial; Unit Scale "only influences the values displayed in the user interface and not how things behave internally" (physics ignores it); Length unit Adaptive or fixed; Rotation degrees or radians. — https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/scene_layout/scene/properties.rst — **page read (source file)**
- That Blender's world is right-handed is stated only by third parties in what I found (Verge3D wiki, Wikibooks). — **search snippet only**

Assessment: Blender is Z up, Y forward and metres-by-convention. Its bones run along local +Y, the same as
Godot's profile ("+Y from parent to child"), so the round-one internal convention (Y up, +Y along each bone)
matches Blender bones and differs only in the world up axis.

---

## S8.2 · Not reached in round one

### gRPC as a remote protocol

- gRPC uses protocol buffers as its default IDL; four method kinds (unary, server streaming, client streaming, bidirectional streaming); client deadlines (`DEADLINE_EXCEEDED`); "Either the client or the server can cancel an RPC at any time", and changes made before a cancellation are not rolled back; per-call metadata key-value pairs. — https://grpc.io/docs/what-is-grpc/core-concepts/ — last modified 2026-05-11 — **page read**
- "gRPC largely follows HTTP semantics over HTTP/2 but we explicitly allow for full-duplex streaming"; "The gRPC-Web project is Generally Available"; "All implementations are licensed under Apache 2.0." — https://grpc.io/docs/what-is-grpc/faq/ — last modified 2025-03-17 — **page read**

Assessment: gRPC fits typed, streaming, cross-language control channels. MCP and our JSON channel are JSON-RPC
2.0, though, so gRPC would be a second way to do the same job. Keep it out unless a client needs it. Live
streams already have OSC/VMC.

### Live Link as a remote protocol

- Live Link is "a common interface for streaming animation data from external sources", "designed to be extensible through Unreal Plugins"; sources → subjects (name, static data such as a skeleton, frames); the page lists roles for Cameras, Lights, Characters, Transforms and a Basic role for generic data. — https://dev.epicgames.com/documentation/en-us/unreal-engine/live-link-in-unreal-engine — UE 5.8 docs — **page read**
- The built-in Message Bus Source runs on UDP Messaging; "UDP Messaging is not enabled by default in -game", and the shipping target is not supported. Third parties either write an Unreal plugin Source ("the recommended approach for anyone that already has their own streaming protocol") or embed a Message Bus endpoint (as the MotionBuilder plugin does). — same — **page read**
- Live Link Hub is "a stand-alone application for streaming real time animation data from Motion Capture software into Unreal Engine and UEFN", with recording and several editor clients on one network. — https://dev.epicgames.com/documentation/unreal-engine/live-link-hub-in-unreal-engine — UE 5.8 docs — **page read**. It can be downloaded from the Epic Games store to run without Unreal, and only plugins listing Live Link Hub as a supported program load in it. — **search snippet only**

Assessment: Live Link is Unreal's receive side, not a published wire spec. JustStage reaches it the way
Reallusion and MotionBuilder do, through a plugin on the Unreal side. That is an export integration, not a
JustStage protocol.

### Houdini `hou.undos`

- Functions: `areEnabled()`, `disabler()` (context manager: changes not added to the undo stack), `group(label, editor=None)` ("all changes … recorded as a single action"; no effect inside parameter callbacks, which "are already executed within an undo group"), `clear()`, `add(undo, label, tag=None)` (object with `undo()`/`redo()`), `removeUndos(tag)`, `memoryUsage()`, `memoryUsageLimit()`, `undoLabels()`, `redoLabels()`, `performUndo()`, `performRedo()`. — https://www.sidefx.com/docs/houdini/hom/hou/undos.html — Houdini 22.0 — **page read**

### Maya `MPxCommand` undo

- `doIt` sets up internal data and calls `redoIt`; `redoIt` does the work "based on the internal class data only"; `undoIt` reverses it "based on the internal class data only"; after a successful `doIt`, if `isUndoable` returns true "the instance … is retained and passed to Maya's undo manager" (default false); query mode should not be undoable; "Maya contains support for infinite levels of undo"; `setUndoable` "Deprecated in 2019.0". — https://help.autodesk.com/cloudhelp/2026/ENU/MAYA-API-REF/cpp_ref/class_m_px_command.html — Maya 2026 API ref — **page read**

Assessment: Maya, Houdini (`add` with undo/redo objects, `group`), Qt and Godot all store per-command undo
data on the command instance and group commands into one step. Blender is the exception, with snapshots for
general edits. Round one's rec (do and undo on one instance, groups, merge ids) matches the majority.

### HumanIK bone list

- 15 required nodes: Hips, LeftUpLeg, RightUpLeg, LeftLeg, RightLeg, LeftFoot, RightFoot, Spine, LeftArm, RightArm, LeftForeArm, RightForeArm, LeftHand, RightHand, Head ("At a minimum, you must characterize all fifteen nodes required by HIK"). — https://help.autodesk.com/cloudhelp/2026/ENU/MotionBuilder-Character-Animation/files/Character-Animation/HIK-character-in-MotionBuilder/GUID-A900A0BA-A1A6-4707-A6AE-26FE8F49BEC6.html — MotionBuilder 2026 help — **page read**
- Optional: Spine1–Spine9 and Neck, Neck1–Neck9 ("You cannot skip a number"); Left/RightShoulder and ShoulderExtra; roll bones on upper/lower arms and legs ("a maximum of five leaf roll bones per limb"); fingers Thumb, Index, Middle, Ring, Pinky, ExtraFinger with joints 1–4, InHand joints, FingerBase; toes on the same pattern; Reference and HipsTranslation. The page gives no total and no T-pose or axis rule. — same — **page read**

### Mixamo bone list

- three-vrm's example maps Mixamo names to VRM bones: `mixamorigHips`, `Spine`, `Spine1` (chest), `Spine2` (upperChest), `Neck`, `Head`, `Left/RightShoulder`, `Arm`, `ForeArm`, `Hand`, `HandThumb1–3` (Thumb1 → thumbMetacarpal), `HandIndex/Middle/Ring/Pinky1–3`, `UpLeg`, `Leg`, `Foot`, `ToeBase`. These are HumanIK names with a `mixamorig` prefix (the colon is dropped in three.js). — https://raw.githubusercontent.com/pixiv/three-vrm/dev/packages/three-vrm/examples/humanoidAnimation/mixamoVRMRigMap.js — dev branch, MIT — **page read (source file)**
- Mixamo's "standard 65-joint skeleton" and finger-chain behaviour come from community forum posts only. — community.adobe.com threads (2021) — **search snippet only**. Adobe's Mixamo help page returned 403.

### UE5 Mannequin bone list

- Bone counts: UE4 Mannequin 68, UE5 Mannequin 89, UEFN 88, MetaHuman 342, CC3+ 108; the page lists no bone names. — https://manual.reallusion.com/Live_Link_Plugin/ENU/Live_Link_Plugin/1.36/Skeleton-between-HD-and-UE-Characters.htm — undated — **page read**
- Epic's MetaHuman DNA page names 30 body joints that must match the body: `spine_04`, `spine_05`, `clavicle_pec_l/r`, `spine_04_latissimus_l/r`, `clavicle_l/r`, `clavicle_out_l/r`, `clavicle_scap_l/r`, `upperarm_l/r`, `upperarm_correctiveRoot_l/r`, `upperarm_out/fwd/in/bck_l/r`, `neck_01`, `neck_02`, `head`, plus `FACIAL_C_Neck1Root`, `FACIAL_C_Neck2Root`, `FACIAL_C_FacialRoot`. It also lists 70 facial "volume" joints (42 placed automatically, 28 not). — https://dev.epicgames.com/documentation/en-us/metahuman/metahuman-dna-rig-definition-and-rig-operation — undated — **page read**
- Epic's Mannequins listing says Manny and Quinn share a skeleton with MetaHumans. — https://docs.unrealengine.com/marketplace/en-US/product/mannequins-asset-pack — **search snippet only**
- Community bone lists show `pelvis`, `spine_01`–`spine_05`, `neck_01`–`neck_02`, twist bones (`upperarm_twist_01_r`, `thigh_twist_01_l`) and IK bones (`ik_foot_root`, `ik_foot_l/r`, `ik_hand_root`, `ik_hand_gun`, `ik_hand_l/r`). — forums.unrealengine.com listings, a Google Doc, a Reallusion tracker issue — **search snippet only**

### MetaHuman control counts

- Head LOD0–7 vertices 24000 / 12000 / 6000 / 2500 / 1300 / 560 / 270 / 130; joints 713 / 529 / 397 / 283 / 84 / 70 / 41 / 26; blend shapes 669 at LOD0 only; skin influences 12, 12, 12, 8, 8, 8, 4, 4; animated maps at LOD0–1. Body LOD0–3 vertices 30500 / 7600 / 3350 / 1507, correctives at LOD0–1, influences 8, 8, 8, 4. "This doesn't mean that each MetaHuman will use exactly these numbers." — https://dev.epicgames.com/documentation/metahuman/platform-support-and-lod-specifications-for-metahumans — undated — **page read**
- Standard MetaHumans have 8 head LODs and 4 body LODs ("two head LODs for each body LOD"). — https://dev.epicgames.com/documentation/metahuman/character-assembler-for-houdini — **page read**
- RigLogic takes "hundreds of semantically meaningful channels"; vertex displacement is used only at LOD0; the expression count is "set by the Rig Definition"; the Expression Editor works only with DNA from MetaHuman Creator in UE 5.6+. — https://dev.epicgames.com/documentation/en-us/metahuman/metahuman-dna-rig-definition-and-rig-operation — **page read**
- The neck has one RBF solver with three joints (neck_01, neck_02, head) and 37 poses driving 18 corrective expressions. — https://dev.epicgames.com/documentation/metahuman/updating-neck-rbf-setup-tool-drivers-for-expression-editor — **search snippet only**
- **GUI and raw control counts: not findable.** Tried: the Epic DNA, LOD and Houdini pages (no counts); metahuman.com's "tech behind face rigs" (login wall); three searches. Counting them would need a DNA file, which means a download.

### CC5's HD profile shape count

- "The HD Facial Profile increases morph sliders from 160 to 390": Facial Expression Morph Sliders 262; Corrective Expression Sliders 128 ("correct the animation flaws by different combination of expression sliders, especially the mouth"); plus "52 non-linear sliders". It is "fully compatible with Unreal Engine's facial expression system". — https://manual.reallusion.com/Character-Creator-5/Content/ENU/5.0/05-HD-Character/HD-Facial-Profile-Intro.htm — undated — **page read**
- Tiers: Standard "60+ morphs featured in iPhone ARKit"; Extended 140+; CC5 Extended+ 250+ with "Integrated expression correction morphs"; CC5 HD 390+, "Compatible with MetaHuman Animator". The Expression Profile Editor offers 300+ morphs. — https://www.reallusion.com/character-creator/facial-expression.html — undated — **page read**

Assessment: 262 + 128 = 390, so the 52 non-linear sliders seem to be counted outside that total. The manual
doesn't say.

### CC's Smart Gallery

- Smart Gallery: purchases in the Content Store or Marketplace sync to the app; Online/Offline mode with auto-sync; browse by Pack or Item; official tags plus custom tags; an update icon when installed content changed; Workgroup multi-seat sharing; for iClone 7+ and CC 3+. — https://www.reallusion.com/smartgallery/ — undated — **page read**
- Its successor, Smart Content Manager, is in iClone 8, CC 5/4 and Cartoon Animator 5: download free or bought content in-app, search "installed and custom created content by keywords and tags", spread content across drives, and share bought assets in a Workgroup through "a corporate server". — https://manual.reallusion.com/content-manager/2.0/00-welcome/welcome.htm — revision 2026-09-01 — **page read**
- Custom tags (right-click → Edit Tag), collections, and pack export that leaves out external files. — Reallusion manual and tips pages — **search snippet only**

### Fab

- Licences: CC-BY (free); Standard (free or paid, with Personal and Professional tiers; publishers must offer both); Reference Only (UEFN, Personal tier); UEFN Source; Legacy UE Marketplace (being phased out). Buyers above $100,000 gross revenue in the last 12 months must use Professional. A NoAI tag means "must not be used for generative AI data collection" and can't be combined with CC-BY. — https://dev.epicgames.com/documentation/fab/licenses-and-pricing-in-fab — undated — **page read**
- The Standard License covers use "in any engine or tool", and both tiers grant the same rights. — Fab licensing summary and launch coverage — **search snippet only**. fab.com/eula returned 403.

### The Reallusion content EULA (one line)

- Reallusion Content EULA, "Updated August 1st, 2025": the Standard License allows commercial renders and commercial games, AR/VR and interactive services. It bars redistribution, "online or in-software character generation" and "character generation APIs", and "machine learning, AI training, or AI-generated output". §6.3 requires 3D models in games to be "contained in proprietary formats". Commercial use: **conditional**. — https://www.reallusion.com/Content/EULA/EULA.htm — 2025-08-01 — **page read**

Assessment: for JustStage's CC importer, the clauses that matter are no character-generator systems and no
AI training on imported Reallusion content. Importing for a user's own projects is a different case. Legal
reading stays with the user.

---

## S8.3 · MCP: the removal of `initialize`, at the spec itself

- Changelog for 2026-07-28 (vs 2025-11-25), major change 2: "Make MCP stateless: remove the `initialize`/`notifications/initialized` handshake. Every request now carries its protocol version and client capabilities in `_meta` (`io.modelcontextprotocol/protocolVersion`, `io.modelcontextprotocol/clientCapabilities`)"; mismatches return `UnsupportedProtocolVersionError` (SEP-2575). — https://modelcontextprotocol.io/specification/2026-07-28/changelog — 2026-07-28 — **page read**
- Also major in 2026-07-28: sessions and `Mcp-Session-Id` removed (state goes in "explicit, server-minted handles passed as ordinary tool arguments"); `server/discover` is a MUST; `subscriptions/listen` replaces GET and `resources/subscribe`; `ping`, `logging/setLevel` and `notifications/roots/list_changed` removed; tasks became the `io.modelcontextprotocol/tasks` extension; Multi Round-Trip Requests (`resultType: "input_required"`) replace server-initiated requests; SSE resumability removed. — same — **page read**
- Minor: tools/list SHOULD come in a deterministic order; list results carry `ttlMs` and `cacheScope`; `inputSchema`/`outputSchema` may use any JSON Schema 2020-12 keywords; MCP error codes −32020…−32099. Deprecated: Roots, Sampling, Logging, the HTTP+SSE transport, and Dynamic Client Registration. — same — **page read**

Assessment: round one's rec (one JSON Schema per command, served over MCP) fits a stateless protocol well. Any
cross-call state (an open scene, a selection) must be an explicit handle in tool arguments, which suits
context-free commands.

---

## S8.4 · MetaHuman's terms: both readings (the user decides)

**Reading A: "any engine".**
- MetaHuman 5.6 release post: "the EULA has been updated so that MetaHumans can be used in any engine"; sale of MetaHumans on Fab is governed by the UE EULA. — https://forums.unrealengine.com/t/metahuman-5-6-release/2539165 — 2025-06-03 — **page read**
- CG Channel: the MetaHuman toolset is "now covered by the standard Unreal Engine EULA"; free under $1M a year; characters and clothing can be sold and used with other DCC apps or engines; usable in AI workflows but not to train or enhance AI models; tools are "enhanced by cloud services that deliver autorigging and texture synthesis". — https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/ — 2025-06-04 — **page read**
- The MetaHuman Creator EULA applies to users of UE 5.5 or earlier; for 5.6+ the UE EULA applies. — https://www.unrealengine.com/eula/mhc — **search snippet only** (403 on fetch)

**Reading B: "Unreal Engine and Twinmotion only".**
- MetaHuman DNA Calibration License §2: "MetaHuman Characters may only be used in conjunction with Unreal Engine and Unreal Engine-based products as designated by Epic, such as Twinmotion." — https://raw.githubusercontent.com/EpicGames/MetaHuman-DNA-Calibration/main/LICENSE — **page read**
- That LICENSE file has one commit, "initial commit", authored 2022-10-31 and committed 2022-11-29; the repo was last pushed 2025-06-20 and isn't archived. — GitHub API, `repos/EpicGames/MetaHuman-DNA-Calibration/commits?path=LICENSE` — **page read**

**Open between them.**
- A user asked whether the change covers pre-5.6 MetaHumans; the thread shows no staff answer. — https://forums.unrealengine.com/t/licensing-changes-to-metahumans/2547356 — 2025-06-08 — **page read**

Assessment: the restrictive text dates from 2022 and predates the June 2025 change, so it may be stale. It is
still the licence that ships with Epic's public DNA tools, which an importer would use. Fact only, no legal
reading; the user decides.

---

## S8.5 · UsdSkel and other USD domains

### Blend shapes and `normalOffsets`

- `UsdSkelBlendShape` attributes: `uniform vector3f[] offsets`, `uniform vector3f[] normalOffsets` ("Normal offsets which, when added to the base pose, provides the normals of the target shape"), `uniform int[] pointIndices` (length must match offsets). — https://openusd.org/release/api/class_usd_skel_blend_shape.html — generated 2026-10-20 — **page read**
- `UsdSkelInbetweenShape` has `Get/Set/CreateNormalOffsets(Attr)`; "Normal offsets are optional, and may be left unspecified." — https://openusd.org/release/api/class_usd_skel_inbetween_shape.html — 2026 docs — **page read**

### Any AOUSD plan for a character or skeleton domain spec

- CMI Interest Group charter, "Approved 03.02.2026", effective 2026-03-02, review/expiry 2027-03-02. Scope topics: "Digital character motion and posing … or as derived or retargeted from another character", "Deformation of a character's geometry as driven or derived by its pose", "Rig nodes and their role in character motion and interactivity, but not implementation details of rigging workflows", soft-body avatars and robots, and "experimental schemas … not normative deliverables". Out of scope: normative documents ("cannot develop, propose or publish any normative documents (e.g., schemas)") and implementing the algorithms. Planned output: recommendations for forming working groups; coordination with "Pixar, Autodesk, Nvidia, SideFX". Progress review "mid-to-late March 2027". — the charter PDF (link in Top findings) — 2026-03-02 — **page read** (text extracted locally)
- The AOUSD interest groups page lists CMI, Emerging Geometry, AECO, Industrial Digital Twin, Web, Build and DEI; no working group is named on that page. — https://aousd.org/community/interest-groups/ — updated 2026-08-13 — **page read**
- Linux Foundation release: CMI's focus is "standardizing skeletal animation, blend shapes, and interactive behaviors"; the Core Spec 1.1 roadmap draws on the Materials, Geometry and Physics groups and CMI; no timeline. — https://www.linuxfoundation.org/press/aousd_prmarch2026 — 2026-03-25 — **page read**
- At SIGGRAPH 2026 "Meta announced the creation of a new working group dedicated to character representation within the Alliance for OpenUSD"; "Pixar, Apple, Autodesk, Netflix, SideFX, Amazon, and Meta are already participating"; the aim is "not to define a universal rig". — https://3dvf.com/en/siggraph-2026-the-future-of-rigging-siggraph-asia-the-experience-hall-and-the-computer-animation-festival/ — 2026-07-21 — **page read** (secondary; no AOUSD charter for that working group found)
- Open OpenUSD proposal: `SkelInstancedAnimationSourcesAPI` (per-instance animation sources and time offsets for crowds of UsdSkel prototypes on a PointInstancer). — https://github.com/PixarAnimationStudios/OpenUSD-proposals/pull/120 — opened 2026-10-22, open — **page read**
- OpenExec: proposal version 2 (2025-06-21) aims to grow USD's computation "in the domain of rigging and posing of characters". "OpenExec by itself is not a rigging system": Pixar plans to ship the execution system and "many of the pieces" of a rigging object model, with "no immediate plans" for its deformer library. It is value-driven, not event-driven. — https://raw.githubusercontent.com/PixarAnimationStudios/OpenUSD-proposals/main/proposals/openexec/README.md — **page read (source file)**
- OpenExec preview in OpenUSD 25.08 (2025-07-31); 26.08 (2026-07-20) added invertible rigs with `IrJointScope`, `IrFkController` and `IrSwitchController` schemas, "limited in functionality, subject to change, and not yet ready for production use". — https://raw.githubusercontent.com/PixarAnimationStudios/OpenUSD/release/CHANGELOG.md — **page read (source file)**. The `release` branch CHANGELOG tops at 26.08, although round one recorded v26.11.1 (2026-10-21) from GitHub releases.

Assessment: JustStage's own schemas for face controls, correctives and rig behaviour (round one) are still
needed, since no standard will land before 2027 at the earliest. Two cheap hedges: keep them USD-shaped (applied
API schemas on UsdSkel prims, versioned `_N`), and follow CMI and OpenExec so we can move later.

### UsdPhysics for cloth

- UsdPhysics "enables the minimum set of common concepts required to represent rigid body physics": rigid bodies, mass, colliders, physics materials (friction, restitution, density), joints, articulations, filtering. The page doesn't mention soft bodies or cloth; "Future iterations and extensions will incrementally add capabilities". — https://openusd.org/release/api/usd_physics_page_front.html — Oct 2026 docs — **page read**
- "Deformable Body Physics in USD" (PR #111): extends `UsdPhysics` with "deformable body dynamics — the elastic deformation of volumes, surfaces (e.g. cloth, shells), and curves (e.g. hair, rods)". It adds a shared `UsdPhysicsBodyAPI`, deformable materials, simulation geometry and rest shape, collision and graphics geometry with bind poses, attachments, kinematic deformables and filtering. Out of scope: plastic deformation, per-element kinematics, rotational coupling, and varying materials. "Developed in the AOUSD Physics Working Group." — https://github.com/PixarAnimationStudios/OpenUSD-proposals/pull/111 — opened 2026-06-23 by `sschirm`, updated 2026-10-27, open — **page read**

### USD BasisCurves for strand hair, and Unreal's groom import format

- Unreal's groom import from Alembic is "an informal Alembic metadata schema" on `ICurves`. Required: `groom_version_major` = 1, `groom_version_minor` = 5. Optional: `groom_tool`, `groom_properties`, `groom_guide`, `groom_group_id`, `groom_root_uv`, `groom_id`, `groom_color`, `groom_closest_guides`, `groom_guide_weights`, `groom_width` (falls back to 1 cm). Names are lowercase with a `groom_` prefix. It supports rendering and simulation, not grooming. — https://dev.epicgames.com/documentation/en-us/unreal-engine/using-alembic-for-grooms-in-unreal-engine — UE 5.8 docs — **page read** (round one's "spec page empty" was a different URL)
- Unreal's USD format page, as quoted in a forum post: "Groom assets (static and baked animation) are imported from USD BasisCurves with the custom GroomAPI schema"; "GroomBindingAPI schema allows to set up a groom on a character". A staff reply says GroomAPI exists "so that we don't pull in non-hair related basis curves prims". Users report imports failing silently. — https://forums.unrealengine.com/t/how-does-the-usd-stage-need-to-be-structured-to-get-groom-assets-to-import/2794442 — 2026-04-07, staff reply 2026-08-18 — **page read**; the KB page itself (https://dev.epicgames.com/community/learning/knowledge-base/jB8v/unreal-engine-usd-ue-format-support) was not fetched.
- Unreal's USD Stage page lists no grooms or curves (supported: static and skeletal meshes, HISM, materials, lights, cameras, variants, animation, blend shapes); the feature is Beta. — https://dev.epicgames.com/documentation/en-us/unreal-engine/universal-scene-description-in-unreal-engine — UE 5.8 docs — **page read**
- Blender exports hair to USD as curves "limited to parent strands", without UVs or normals. — usd.rst (manual main) — **page read (source file)**

Assessment: for strand hair, export Alembic with `groom_*` attributes (documented, versioned 1.5) as Unreal's
reliable path. USD BasisCurves plus Epic's custom `GroomAPI` is a second path with reported failures. Inside
JustStage, BasisCurves remains the USD-shaped storage.

---

## S8.6 · Export-target facts

### Unity's coordinate system

- "Unity uses a left-handed coordinate system: the positive x-axis points to the right, the positive y-axis points up, and the positive z-axis points forward." — https://docs.unity.com/en-us/engine/6000.5/manual/scripting/programming-math/unity-engine-math/class-quaternion — Unity 6.5 docs — **page read**
- "Unity uses a Y-up, left-handed coordinate system, which differs from other engines." — https://docs.unity.com/en-us/engine/6000.7/manual/get-started/with-unity — Unity 6.7 Beta docs — **page read**
- Model import: "Unity's physics system expects 1 m in the game world to be 1 unit in the imported file" (Scale Factor); Convert Units; Bake Axis Conversion bakes the axis change into vertex and animation data, otherwise the root Transform compensates; "Importing blend shape normals requires smoothing groups in the FBX file"; Index Format Auto/16/32-bit. — https://docs.unity.com/en-us/engine/6000.7/manual/assets-and-media/asset-types/models/importing/fbximporter-model — Unity 6.7 docs — **page read** (re-checks round one's snippet)
- glTFast (`com.unity.cloud.gltfast`, latest 6.20): skins import and export with up to 4 joints and weights per vertex; morph targets supported; sparse accessors for "morph targets and vertex positions only"; Mecanim clips import but "won't be assigned and cannot be played back without further work"; Playables support was removed. — https://docs.unity3d.com/Packages/com.unity.cloud.gltfast@6.20/manual/features.html — 6.20 — **page read**

### VRM 1.0's bone local axes

- VRM 1.0's T-pose spec defines the pose by the mesh's appearance: facing +Z, symmetrical on X, grounded at Y = 0, arms and hands along X with palms toward −Y, finger nails toward +Y, thumbs at 45° between X and +Z. Its only numeric rule is "All node transforms must be in a positive uniform scale". It has no rule on bone local axes or rest rotations. — https://raw.githubusercontent.com/vrm-c/vrm-specification/master/specification/VRMC_vrm-1.0/tpose.md — last changed 2023-01-11 — **page read (source file)**
- `humanoid.md` and `README.md` contain no local-axis rule (text search); `lookAt.md` refers to the head's "rest rotation". — https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_vrm-1.0 — **page read (source files)**
- three-vrm keeps "raw" and "normalized" human bones; normalized bones have their own rest pose, and poses copy from normalized to raw on `update` (`autoUpdateHumanBones`, default true). — https://raw.githubusercontent.com/pixiv/three-vrm/dev/packages/three-vrm-core/src/humanoid/VRMHumanoid.ts — dev branch, MIT — **page read (source file)**. The library doc line "VRM1.0 allows for non-normalized bone orientations … identity orientation … in their rest pose" — **search snippet only**

Assessment: VRM's bones carry any local rotation, so a VRM exporter needs only the role map, T-pose appearance
and uniform scale. A runtime normalises on its side, as three-vrm does. Our internal "+Y along the bone" is not
required by VRM.

---

## S8.7 · Open FBX writers; WebAssembly copy cost

### Open FBX writers (any)

- **ufbx_write**: "Single source file FBX file exporter", © 2026 Samuli Raivio; ufbx's own LICENSE is © 2020 Samuli Raivio (same author). "still a work-in-progress, and issues/breaking changes are to be expected". MIT or Unlicense; repo created 2025-06-22, last pushed 2026-06-20. Its API saves binary or ASCII (example version 7500). Its element types include skin deformer and cluster, blend deformer, channel and shape, cache deformer, material, texture, and anim curve, layer and stack. — https://github.com/ufbx/ufbx-write and https://raw.githubusercontent.com/ufbx/ufbx-write/main/ufbx_write.h — **page read (source files)**; dates from `gh api repos/ufbx/ufbx-write`
- **Assimp**: exporters list "FBX ( experimental )"; `FBXExporter.cpp` writes version 7500 ("7.5 == 2016+"), ASCII and binary, skin deformers and blend shapes ("Blendshapes are considered Geometry"). Licence is a 3-clause BSD-style text (GitHub shows NOASSERTION). — https://raw.githubusercontent.com/assimp/assimp/master/doc/Fileformats.md, https://raw.githubusercontent.com/assimp/assimp/master/code/AssetLib/FBX/FBXExporter.cpp, https://raw.githubusercontent.com/assimp/assimp/master/LICENSE — master, pushed 2026-10-29 — **page read (source files)**
- **Blender's FBX exporter** (`io_scene_fbx`, Python, GPL-2.0-or-later, add-on 5.15.0) writes blend shapes and, since 5.1, shape-key normals. — see S8.1 — **page read (source files)**
- Smaller or older projects: hamish-milne/FbxWriter (.NET, no licence detected, last push 2022), jimmiebergmann/fbx-file (C++11, MIT, 2021), fbxcel (Rust reader/writer, per its deprecated predecessor's description), and three-js-fbx-exporter (MIT, 2026-06, 0 stars). — `gh api search/repositories` — **search snippet only** (repo descriptions, not code read)

Assessment: round one marked FBX export an open user decision because only Autodesk's SDK writes FBX. That
premise is wrong: two permissively licensed C/C++ writers exist. Both are young or experimental, so their output
needs proof by import tests into Unreal, Unity, Maya and Blender (not done here). Recommendation: glTF stays the
default; FBX export goes through ufbx_write (same author as our ufbx reader) behind an exporter test suite.
Assimp is the fallback.

### The copy cost of WebAssembly plugins on large meshes

- **Not findable**: no benchmark or paper measuring host↔guest copy cost for large meshes. Tried: three web searches ("component model canonical ABI copy overhead", "wasm plugin mesh processing overhead copy", plus related queries) and the component-model repo's issues. Related facts:
- The Component Model is shared-nothing. Its designer notes that copying a mappable memory reference "breaks the shared-nothing property", so memory mapping (from the core-wasm memory-control proposal) is still open design. — https://github.com/WebAssembly/component-model/issues/568 — 2025-10-15, open — **page read**
- Zero-copy proposals: a `flat<T>` data representation (issue #398, 2024-09-21, open) and caller-provided buffers (issue #369, 2024-06-19, open). — https://github.com/WebAssembly/component-model/issues/398, https://github.com/WebAssembly/component-model/issues/369 — **page read**
- Wasm 3.0 is the "live" standard (2025-09-17): 64-bit memories expand address space "from 4 gigabytes to (theoretically) 16 exabytes"; "on the web, a 64-bit memory is limited to 16 gigabytes"; one module may use several memories and copy between them. — https://webassembly.org/news/2025-09-17-wasm-3.0 — **page read**
- With plain wasm modules (not components), a Wasmtime host can view guest linear memory directly (`Memory::data`, `data_mut`, `data_ptr`); growth "may relocate the memory", which invalidates pointers. — https://docs.rs/wasmtime/latest/wasmtime/struct.Memory.html — wasmtime 50.0.0 — **page read**
- Compute (not copy) overhead: WebAssembly ran "slower by an average of 45% (Firefox) to 55% (Chrome)" than native on SPEC, peaks 2.08× and 2.5× (browsers, 2019). — https://www.usenix.org/conference/atc19/presentation/jangda — USENIX ATC 2019 — **page read**
- A vendor engineering note reports a 13× slowdown loading a 2D scene in wasm (geometry traversal 33×), blamed on access patterns and bounds checks rather than copies. — https://grida.co/docs/wg/feat-2d/wasm-load-scene-optimization — **search snippet only**

Assessment: this supports round one's two-tier "Changed" line. Mesh-heavy plugins (simulation, sculpt,
renderers) stay native built-ins. Sandboxed components get commands and small or streamed data. If a component
must touch big meshes, the host passes chunked `stream<T>` data or a handle-based API, not whole meshes per call.
A measurement on our own data would settle it; that is a prototype task, not a search.

---

## Re-checks of round one's snippet-only facts

| Round-one fact (snippet) | Result | Source (page read unless noted) |
|---|---|---|
| Blender operator `UNDO`/`REGISTER` texts; no-`execute` operators can't be repeated from scripts | **Confirmed**, exact texts above | rna_wm.cc; bpy.types.Operator.2.py |
| Blender manifest permissions (files, network, clipboard, camera, microphone; ≤64-char reason) | **Confirmed**; also `scripts` for 5.3 asset libraries | getting_started.rst; asset_libraries.rst |
| Blender stores SDNA in each file, writer and minimum-reader versions, unknown data ignored, defaults, versioning code | **Confirmed**; adds "Critical forward compatibility breakages are only allowed every two years" at major versions, the previous cycle's last LTS acts as converter, and files from major n open in n and n+1 | [compatibility_handling_for_blend_files.md](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/handbook/guidelines/compatibility_handling_for_blend_files.md), [dna.md](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/features/core/dna.md) |
| Blender 5.0 header change; only 4.5 LTS reads 5.0 files; 4.5 truncates long names | **Confirmed** | [5.0 core.md](https://projects.blender.org/blender/blender-developer-docs/raw/branch/main/docs/release_notes/5.0/core.md) |
| Remote listing `_asset-library-meta.json` → `_v1/asset-index.json`, OpenAPI in source | **Confirmed** | remote_asset_libraries.rst; openapi.yaml |
| Catalogue file format | **Confirmed** | catalogs.rst |
| USD schema versioning `_N`, family, helpers | **Confirmed** as design (white paper, ©2022); **shipped**: "Initial Schema Versioning support" in 23.02 (2023-01-24), "Completed initial support" in 23.05 (2023-04-18) | [wp_schema_versioning](https://openusd.org/release/wp_schema_versioning.html); OpenUSD CHANGELOG |
| Godot 4.1 broke GDExtension; later minors "should work" | **Confirmed**: "The GDExtension API completely breaks compatibility in 4.1"; godot-cpp: an extension for 4.3 "should work just fine in Godot 4.4, but one targeting Godot 4.4 won't work in Godot 4.3" | [upgrading_to_godot_4.1.rst](https://raw.githubusercontent.com/godotengine/godot-docs/master/tutorials/migrating/upgrading_to_godot_4.1.rst), [godot-cpp README](https://raw.githubusercontent.com/godotengine/godot-cpp/master/README.md) |
| Maya: no binary compatibility between releases | **Confirmed**: "Maya does not provide binary compatibility for plug-ins between releases. With each new release, the source must be recompiled." (2012 SDK page) | [Maya SDK 2012](https://download.autodesk.com/global/docs/Mayasdk2012/en_us/files/Setting_up_your_build_environment_Compiler_Requirements.htm) |
| Houdini asset naming `[namespace::]node_name[::version]` | **Confirmed**; old instances "will still work and use the old implementation" | [namespaces](https://www.sidefx.com/docs/houdini/assets/namespaces.html) (22.0) |
| Cinema 4D plugin IDs unique | **Confirmed**: the plugin "will otherwise not register when an ID collision occurs"; IDs issued via developers.maxon.net; adds "The Cinema 4D ABI will remain upwards compatible for one major version" | [C4D 2026.2 requirements](https://developers.maxon.net/docs/cpp/2026_2_0/page_requirements.html) |
| Unreal left-handed, Z up, X forward; cm | **Confirmed** (UE 5.8 pages); the units page sets the default distance unit to centimetres | [coordinate system](https://dev.epicgames.com/documentation/unreal-engine/coordinate-system-and-spaces-in-unreal-engine?lang=en-US), [units](https://dev.epicgames.com/documentation/en-us/unreal-engine/units-of-measurement-in-unreal-engine) |
| Unreal Remote Control ports 30010 / 30020 | **Confirmed**; binds 127.0.0.1 by default; "Do not attempt to open the hostname and port … to the open Internet" | [quick start](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-quick-start-for-unreal-engine), [WebSocket ref](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-api-websocket-reference-for-unreal-engine) |
| Unity FBX importer (scale, bake axis conversion, blend-shape normals) | **Confirmed** | Unity 6.7 Model tab page |
| MediaPipe "predicts 52 blendshape scores", 478 landmarks | **Confirmed** | [Face Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker) |
| blender-mcp: socket on localhost:9876, JSON `{type, params}`, arbitrary Python | **Confirmed**; the socket "has no authentication or encryption"; an optional `BLENDER_MCP_SAFE_MODE=1` screens scripts; MIT | [README](https://raw.githubusercontent.com/ahujasid/blender-mcp/main/README.md) |
| No first-party MCP from Unity, Autodesk, SideFX | **Corrected for Unity** (Unity MCP, AI Assistant 2.0.0-pre.1); none found for Autodesk or SideFX (one search) | [Unity MCP](https://docs.unity3d.com/Packages/com.unity.ai.assistant@2.0/manual/unity-mcp-overview.html) |
| MetaHuman 5.7 conform "between A-pose and T-pose" | **Not confirmed as worded**: the 5.7 notes say "support for varied poses" and "UV-space vertex correspondence"; UE 5.8 extends Mesh to MetaHuman to bodies (snippet) | [MetaHuman 5.7 released](https://forums.unrealengine.com/t/metahuman-5-7-released/2672724) (2025-11-12) |
| CC subdivision export "via FBX/USD format or Live Link" | **Confirmed**; each level "comes with its own set of normal and displacement maps" | [subdivision-export](https://www.reallusion.com/character-creator/subdivision-export.html) |
| CC5 forum ARKit → CC5 HD remap request | **Confirmed**: question 2025-11-26, no staff answer | [thread](https://discussions.reallusion.com/t/remap-retarget-asset-for-ue5-from-arkit-to-cc5-hd-facial-profile/15988) |
| AOUSD Core Spec 1.0 "landmark ratification" (LF, 2026-03-25) | **Confirmed**; no exact ratification date on that page | LF press |
| MetaHuman "any engine" (metahuman.com snippet) | **Confirmed elsewhere** (Epic forum release post; CG Channel); metahuman.com still behind login | S8.4 |
| Unreal 5.8 experimental MCP server | Not re-checked here; it's in S5's list | — |
| A Blender add-on imports MetaHuman DNA (superhivemarket) | Not verified: polyhammer.com redirected (308) and Marvelous Designer's DNA-importer page returned 403 | — |

---

## Licences, one line each (new in this pass)

- ufbx_write — MIT or Unlicense — commercial: yes — https://github.com/ufbx/ufbx-write
- Assimp — 3-clause BSD-style licence text (GitHub: NOASSERTION) — yes — https://github.com/assimp/assimp/blob/master/LICENSE
- Blender FBX add-on (`io_scene_fbx`) — GPL-2.0-or-later — yes (GPL terms) — https://github.com/blender/blender/tree/main/scripts/addons_core/io_scene_fbx
- Rigify — GPL-2.0-or-later — yes (GPL terms) — https://github.com/blender/blender/tree/main/scripts/addons_core/rigify
- Blender remote asset listing OpenAPI schema — GPL-2.0-or-later (file header; `info.license` says GPLv3) — yes — openapi.yaml above
- gRPC — Apache-2.0 — yes — https://grpc.io/docs/what-is-grpc/faq/
- three-vrm — MIT — yes — https://github.com/pixiv/three-vrm
- blender-mcp — MIT — yes — https://github.com/ahujasid/blender-mcp
- Live Link / Live Link Hub — part of Unreal Engine, UE EULA — conditional — https://dev.epicgames.com/documentation/en-us/unreal-engine/live-link-in-unreal-engine
- Unity MCP (AI Assistant package) — terms not stated on the page read — unclear — https://docs.unity3d.com/Packages/com.unity.ai.assistant@2.0/manual/unity-mcp-overview.html
- Fab Standard License — Personal/Professional by $100k revenue; full EULA refused (403) — conditional — https://dev.epicgames.com/documentation/fab/licenses-and-pricing-in-fab
- Reallusion Content EULA (2025-08-01) — no redistribution, no character generators, no AI training — conditional — https://www.reallusion.com/Content/EULA/EULA.htm
- MetaHuman (UE 5.6+) — UE EULA, free under $1M; "any engine" per Epic 2025-06-03; DNA Calibration licence says Unreal/Twinmotion only — conditional — S8.4
- AOUSD CMI charter contributions — Apache-2.0 for source code, W3C RF patent terms — n/a (process) — charter PDF
- OpenUSD proposals (PR #111, #120) — contributions under Pixar's supplemental terms; not checked further — unclear — https://github.com/PixarAnimationStudios/OpenUSD-proposals

---

## Couldn't verify / open

- **UE5 Mannequin full bone list**: no primary public page found; count 89 only (Reallusion page read); partial names from Epic's MetaHuman DNA page (30 body joints) and community lists (snippet). Tried: Epic IK Rig/retarget docs, Reallusion pages, four searches. The editor shows it; no download was made.
- **MetaHuman GUI and raw control counts**: not findable (see S8.2). LOD0 joints (713) and blend shapes (669) are known.
- **Mixamo**: Adobe's help page refused (403). The 65-joint standard skeleton is from forums only; the names come from three-vrm's map.
- **Fab EULA text**: fab.com/eula refused (403). "Any engine" for the Standard License is a snippet.
- **MetaHuman licence pages** (metahuman.com/license, ai-info, unrealengine.com/eula/mhc, the State of Unreal 2025 post) refused or need a login; the user reads them if needed.
- **Unreal's USD groom path**: the KB page (dev.epicgames.com/community/learning/knowledge-base/jB8v) was not fetched; GroomAPI comes from a forum quote. Which GroomAPI attributes exist is not known.
- **Blender's right-handedness**: no Blender manual or code page read states it (third-party snippets only). Z up and Y forward are page-read.
- **WebAssembly copy cost on large meshes**: no benchmark exists that I could find; it needs a measurement on our own data (prototype).
- **gRPC over local IPC** (Unix sockets, named pipes): not covered on the pages read.
- **The AOUSD character-representation working group** (Meta, SIGGRAPH 2026): known only from one press report; no charter found.
- **OpenUSD 26.11 changelog**: the `release` branch CHANGELOG tops at 26.08; whether 26.11 changed UsdSkel or OpenExec is not checked.
- **Open FBX writers' output quality**: ufbx_write is WIP and Assimp's exporter is experimental; neither was tested against Unreal, Unity or Maya import (that needs builds, not searches).
- **Fbxcel's writer status** (Rust): from a repo description only.
