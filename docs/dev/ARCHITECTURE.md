# JustStage — why it is built the way it is (ARCHITECTURE)

> **Status: DRAFT, 2026-10-29 — for the user's approval**, with [`PRD.md`](PRD.md) and the standards spec
> ([`../standards/README.md`](../standards/README.md)). Each reason names its evidence in [`RESEARCH.md`](RESEARCH.md)
> (§) and the approved rec (R). The standards are the contract; this page is the *why*.

## 1 · The route: an application on stock Blender, plus an open Unreal plugin (R1)

**What:** JustStage opens as its own application — a Blender application template (its own splash, startup layout,
workspaces, menus, panels, theme and keymaps, with Blender's panels replaced where they get in the way) — and its
features are Blender extensions (Python, with compiled wheels where speed needs it). A separate, MIT Unreal plugin is
the Auto Setup + Live Link equivalent.

**Why Blender (§6):** a character creator needs sculpting, modelling, UV, baking, hair curves, cloth, rigging, EEVEE,
Cycles and USD/glTF/Alembic/FBX — Blender 5.2 LTS has all of them, on every GPU vendor and all three OSes, and is the
easiest base for AI agents (`-b --python`, `gpu.init()` headless since 5.2, screenshots, an official MCP server).
Unreal's editor cannot ship inside a product (its EULA's Engine Tools clause, read at the source — §6) and its
sculpting is weak; Godot and our own engine leave the realistic human and nearly every tool to build; O3DE's macOS
editor is experimental; Unity's free tier is far smaller than Unreal's (out by the user's test).

**Why not a fork now (R1's attack):** the fork's reasons were GPU skinning and a timeline editor — iClone-side, out of
scope now; a template reworks most of the UI without a fork (checked at Blender's manual source and code — §6); a
fork returns only if the gate needs viewport C work or when an Animate workspace is built.

**Why an Unreal plugin:** Unreal reads files but cannot set up a character — skeleton reuse, the RigLogic face,
groom binding, materials, Live Link, an update that keeps animation. That is CC5's Auto Setup pattern (§2), and
MIT Unreal plugins are common practice (303 on GitHub — §6). It also lets Unreal stand in for iClone (R13).

**Licence (R2):** published Blender add-ons must be GPL-compatible (blender.org, read 2026-10-29), so the extension
is GPL-3.0-or-later; the schema tools, generators and the Unreal plugin don't link Blender and stay MIT; outside
programs that use the API may use any licence.

## 2 · The bar first: a measured gate (R3)

No source compares any open base, dataset or generator with CC5 or MetaHuman (§5, §7). The only honest test is our
own renders beside theirs, judged by the user. So the first step builds one head and renders it beside a CC5 HD
character and a MetaHuman in EEVEE, Cycles and Unreal, part by part — before any feature work. A failing base would
waste everything after it; the weeks are the cheapest insurance in the plan.

## 3 · The base human: an open quad base, two levels, scan-based shape spaces (R4)

hm08 is all-quad, made for subdivision, CC0, with 1,258 CC0 targets from infant to elder (§5). CC5 HD is CC3+'s
topology plus two subdivision levels with per-level maps (§2) — the same method. Realism comes from scan data, not
code (S10): MHR (7,110 body scans, Apache-2.0) and GNM (scan-based heads with eyes, teeth and tongue, Apache-2.0) are
wrapped onto the base through SOMA-X's existing bridge, as shape keys. The attack on hm08 alone ("artist-made forms
read stylised-realistic") is why the scan spaces are there, and the gate decides whether it worked.

## 4 · Assets: reuse where it meets the bar, build the rest (R5)

S10's part-by-part table: no permissively licensed skin generator, groom set or iris data meets the bar; the open
image models (Apache-2.0/MIT, run by stable-diffusion.cpp on every vendor) are the reusable AI; OpenRigLogic, GNM/ICT
mouth geometry, Dem Bones, complementary dynamics and Jolt are the reusable pieces. The large scan datasets are
non-commercial and mostly 1K — labelled, never trained on.

## 5 · One data model, three forms

The live character is Blender's data (meshes, shape keys, armatures, curves, materials) with JustStage's fields as
PropertyGroups generated from one USD schema file; the portable character is a USD package (UsdSkel, UsdShade,
BasisCurves) carrying JustStage's own data as **USD applied API schemas**, with one companion — the DNA face rig. Why
USD: it is the only open format with layers, composition, variants and skinned characters in one model, and Unreal
reads it (Beta) (§8). Why our own schemas: UsdSkel stores shapes but "does not aim to provide general rigging and
execution behaviours", so correctives' drivers, slider definitions, groom and garment settings have no industry schema,
and no app's USD carries them (S9); USD's own answer is the applied API schema (Epic's `GroomAPI` is one), and Blender's
own answer for writing them is its USD hook API. A JSON exists only as the sidecar FBX and glTF need (CC5's, Daz's and
MetaHuman's pattern). When AOUSD's character group delivers (not before 2027 — §8 pass 2), a converter maps our
families onto theirs. Versioning follows Blender (writer and minimum reader versions, ordered versioning code),
protobuf (unknown fields preserved) and USD (`_N` schema families). The first draft had the JSON as the record and USD
as a mirror; the standard-first pass of 2026-10-29 reversed it (standards README §6).

## 6 · Skeleton and face: where the industry converged (R18)

CC5 added ten bones to line up with UE5/MetaHuman and shares MetaHuman's facial controls (§2, §8); Daz's bridges map
Genesis onto the same skeleton (§8). So JustStage's skeleton **is** the UE5 skeleton, by its own names (measured from
the user's Unreal project: 80 deform bones), which Blender's mirror tools accept as they are — so Unreal needs no
renaming — with mapping tables to every other vocabulary (VRM/Unity/Godot — the converged open set; HumanIK and
Mixamo; Daz G8/G9; CC). The face is two layers: ARKit's 52 as the guaranteed, measurable
interchange set (public; iPhone and MediaPipe produce it), and a DNA + RigLogic rig underneath (the proven layered
design, open under MIT since June 2026 — §4). Correctives are the one thing no format carries — hence our schema.

## 7 · Everything is a command (R19)

Blender's own lesson, in its own words: operators without a context-free `execute()` "cannot be repeated from a
script or macro"; operators "use the context instead" of taking data — the scripting pain points (§8 pass 2). CC5
and iClone have an in-process Python API only, so a third party had to build an HTTP + MCP bridge (§2). PhotoCraft's
registry (id, label, schema, enabled, run; dispatched from the UI, CLI, JSON channel and MCP — §11) is the shape;
MCP 2026-07-28 is JSON-RPC 2.0 with JSON Schema 2020-12 tools and no sessions (§8 pass 2), so one schema per command
serves every door. Blender Lab's official MCP server (add-on + socket + stdio process) is the base; its "no guards"
Python tool is the reason permissions are first-class (Cinema 4D's model — §4).

## 8 · Plugins (R19, R2)

JustStage is **one** Blender extension with feature modules (Blender's manifest has no field for one extension
depending on another — read 2026-10-29 — so a family of extensions cannot be declared or installed), plus the
application template. Third-party plugins are their own extensions that import `juststage` and register in Python,
the way Blender add-ons talk to each other; the manifest stays stock. Outside programs use the MCP door. A sandboxed
WebAssembly tier was the right design for an own-engine route (§8) and the wrong one inside Blender (no GPU or mesh
access across the boundary); it is not built. The plugin API is proven on our own modules, which register through it.

## 9 · Import and export (R11, R12)

The reference apps converge on four steps — read, characterise, wrap, convert materials (S9) — so JustStage has four
commands and per-source profiles. Unreal reads more USD than any app checked, but its export is Beta and its morph
targets unverified (S9), so the plugin prefers the package and falls back to FBX, and the first test runs on the
user's own Unreal projects. CC5's and Daz's USD don't help (MDL materials; no Daz USD), so their FBX plus sidecars
stay the path. The keep-animation rule answers iClone users' loudest complaint (§3): re-import in place, by UUID,
with a shared skeleton asset and append-only names.

## 10 · AI engines through the family (R14)

The web kit already installs, starts, books memory for and runs jobs on stable-diffusion.cpp and llama.cpp
(`RuntimeService`), with one model cache for the family (§10). A second copy inside Blender would be a second cache
and no arbiter — the kit's own "never" column. The arbiter is per process and the card is 8 GB, so image jobs are
queued and JustStage lowers its own load while they run; the exact numbers come from the gate. One kit gap is named:
a generic HTTP route that runs an image feature as a job.

## 11 · Rendering and testing (R15, R16)

EEVEE in real time and Cycles offline are Blender's; Unreal through the plugin gives MetaHuman-level real time. Tests
are Blender's own methods — headless Python, golden images with oiiotool thresholds on lavapipe and the macOS runner —
because every family app is built by AI agents and the tests are the eyes (memory; PhotoCraft's "Every change comes
with tests").

## 12 · One app, workspaces; JustDirect beside it (R6, R20)

iClone users' worst seam is the CC↔iClone round trip (§3), so scenes and animation come later in the same app as
workspaces (Blender's own mechanism). JustDirect stays a separate app: a local video clip takes 7.3 GB of the 8 GB
card (§10) and the two stacks differ; it drives JustStage over the API and takes its USD/glTF scenes and render
passes.

## 13 · The order (R21)

0 the standards spec → 1 the gate with a first plugin → 2 base, head and the generators → 3 photo-to-head →
4 rig and expressions → 5 clothes fitting → 6 import/export and the full plugin → 7 sculpt extras → 8 patterns →
later: Animate, or staying on Unreal. The scorecard's floor only rises.

## 14 · What would change this architecture

| Trigger | Change |
|---|---|
| The gate fails on viewport work no extension can fix | a Blender fork (R1's trigger), the extension unchanged |
| AOUSD publishes character schemas | a converter maps JustStage's schema families onto theirs; ours stay for what AOUSD doesn't define |
| Unreal's USD export carries morph targets reliably | the FBX fallback in the plugin is retired |
| ufbx-write passes the round trips | it replaces Blender's FBX exporter for the MIT libraries |
| MetaHuman's terms read one way (the user's reading) | "Send to Unreal as a MetaHuman" and DNA import of MetaHuman assets are enabled or labelled accordingly |
| An Animate workspace is scheduled | iClone's inventory joins the scorecard; the animation data of the spec gets its editors |
