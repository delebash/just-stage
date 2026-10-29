# JustStage — why it is built the way it is (ARCHITECTURE)

> **Status: rewritten 2026-10-29 to the approved recs** — R1–R21 and the Opus review's 1–28 ([`TASKS.md`](TASKS.md);
> the review: [`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md), its items cited as
> "item N"). With [`PRD.md`](PRD.md) and the standards spec ([`../standards/README.md`](../standards/README.md)). Each
> reason names its evidence in [`RESEARCH.md`](RESEARCH.md) (§) and the rec (R). The standards are the contract; this
> page is the *why*.

## 1 · The route: its own app on an unmodified Blender, plus an open Unreal plugin (R1, items 16, 24)

**What:** JustStage installs and opens as its own app. Its installer holds an unmodified Blender (the newest release —
5.3 now, the version installed on this machine), the `juststage` add-on, a Blender application template (its own
splash, startup layout, workspaces, menus, panels, theme and keymaps, with Blender's panels replaced where they get in
the way), Blender Lab's MCP server and JustStage's engine host. A JustStage launcher starts Blender on that template
with JustStage's own settings folder. A separate, MIT Unreal plugin is the Auto Setup + Live Link equivalent.

**Why Blender (§6):** a character creator needs sculpting, modelling, UV, baking, hair curves, cloth, rigging, EEVEE,
Cycles and USD/glTF/Alembic/FBX — Blender has all of them, on every GPU vendor and all three OSes, and is the easiest
base for AI agents (`-b --python`, `gpu.init()` headless, screenshots, an official MCP server). Unreal's editor cannot
ship inside a product (its EULA's Engine Tools clause — §6) and its sculpting is weak; Godot and our own engine leave
the realistic human and nearly every tool to build; O3DE's macOS editor is experimental; Unity is out by the user's
word. Blender as a Python module "runs without a user interface", so it can't be embedded instead (§8).

**Why its own app, not an add-on users install** (item 24): the user wants it to launch "like an app we built". Blender
documents application templates for exactly this ("people can build their own *applications* on top of Blender that
can be easily distributed"), and its command-line flag and folder variables let a launcher start it on our template and
folders without touching Blender's files or the user's own Blender (§8). What still says Blender — the window title and
icon — is C code; removing them is a fork, not worth a title bar.

**Why 5.3 and every release after** (item 16): the user installed 5.3 for JustStage to be built and tested on, and it
brings online asset libraries with logins, Alembic export of hair attributes for Unreal, and Multires sculpting that
shows textures (§8). A normal release gets fixes only for severe bugs and is replaced in about four months, so the
installer moves to each new release after the test suite passes on it.

**Why not a fork now:** the fork's reasons were GPU skinning and a timeline editor — iClone-side, later; a template
reworks most of the UI without one; a fork returns only if the gate needs viewport C work, when an Animate workspace is
built, or if the branding must go.

**Why an Unreal plugin:** Unreal reads files but cannot set up a character — skeleton reuse, the RigLogic face and body,
groom binding, materials, Live Link, an update that keeps animation. That is CC5's Auto Setup pattern (§2), and MIT
Unreal plugins are common practice (§6). It also lets Unreal stand in for iClone (R13), mocap included.

**Licence (R2):** published Blender add-ons must be GPL-compatible, so the add-on is GPL-3.0-or-later; shipping
Blender's binaries means offering its source; the generators, the wrap code and the Unreal plugin don't link Blender and
stay MIT; outside programs that use the API may use any licence.

## 2 · The bar first: a measured gate (R3)

No source compares any open base, dataset or generator with CC5 or MetaHuman (§5, §7). The only honest test is our own
renders beside theirs, judged by the user. So the first step builds one realistic head — generated skin with pores
and fine wrinkles, eyes, lips, teeth, tongue, brows, lashes, strand hair, nails, three expressions — and renders it
beside a CC5 HD character and a MetaHuman in EEVEE, Cycles and Unreal, part by part, before any feature work. A failing
base would waste everything after it; the fallback base (item 23) is named in advance.

## 3 · The base human: MakeHuman's whole, two levels, scan-based shape spaces (R4, items 2, 3, 23)

hm08 is all-quad, made for subdivision, CC0, with 1,258 CC0 targets from infant to elder (§5). CC5 HD is CC3+'s
topology plus two subdivision levels with per-level maps (§2) — the same method. Realism comes from scan data: MHR
(7,110 body scans, Apache-2.0) and GNM (scan-based heads with eyes, teeth and tongue, Apache-2.0) are wrapped onto the
base through SOMA-X's bridge, as MakeHuman targets. **hm08 ships whole**: its helper geometry is what MakeHuman's
clothes fit to and its joint cubes are what every MPFB2 rig places joints from, so they are how joints and clothes
follow the body as sliders change it — MPFB2 masks them while editing and deletes them at export (item 2). **MakeHuman's
own formats** carry the data for this base — targets, `target.json`, `macro.json`, MHM, MHCLO, the rig and weights JSON,
the CC0 face-unit and viseme packs, expressions (item 3) — because a second format for the same data is the second way
the rules forbid. If the gate fails on topology, Blender Studio's CC0 base meshes take hm08's place with MakeHuman's
sliders wrapped on (item 23). Creatures are a second kind of character, with their own meshes and skeletons (item 22).

## 4 · Assets: reuse where it meets the bar, build the rest (R5, item 28)

S10's part-by-part table: no permissively licensed skin generator, groom set or iris data meets the bar; the open image
models (Apache-2.0/MIT, run by stable-diffusion.cpp on every vendor) are the reusable AI; OpenRigLogic, GNM/ICT mouth
geometry, Dem Bones, complementary dynamics and Jolt are the reusable pieces. Mesh2Motion's CC0 creature rigs and
animations and Blender Studio's CC0 base meshes start the library (item 28). The large scan datasets are
non-commercial and mostly 1K — labelled, never trained on.

## 5 · One data model, three forms — existing formats first (items 1–6, 11, 17)

The live character is Blender's data (meshes, shape keys, armatures, curves, materials) with JustStage's fields in
hand-written PropertyGroups; the portable character is a USD package; FBX gets a small sidecar. The first draft
invented a JSON record, then nine USD schema families; the review found that existing formats already do those jobs —
the DNA for correctives (its RBF and twist-swing layers, which MetaHuman's own body DNA uses), MakeHuman's formats for
sliders and clothes, MaterialX/OpenPBR (written by Blender's own exporter) for materials, Blender's hair node groups for
grooms, glTF's `extras` for application data. What is left with no standard home is a dozen plain `juststage:`
attributes (N1, approved), written by Blender's USD hook — readers that don't know them ignore them, as USD intends.
Name and index maps are JSON, as Daz's bridges and MPFB2 keep them (item 17). When AOUSD publishes character schemas, a
converter maps those attributes onto them.

## 6 · Skeleton and face: where the industry converged (R18, items 1, 9, 10)

CC5 added ten bones to line up with UE5/MetaHuman and shares MetaHuman's facial controls (§2, §8); Daz's bridges map
Genesis onto the same skeleton (§8). So JustStage's skeleton **is** the UE5 skeleton, by its own names (80 deform bones,
measured from the user's Unreal files), built on MPFB2's UE-named rig; Blender's mirror tools accept the names; name
tables reach every other vocabulary (VRM/Unity/Godot, HumanIK, Mixamo, Daz, CC — by humanoid role where a source has
fewer spine bones). In Unreal, compatible skeletons let Epic's animations play on ours (item 12). The face is two layers:
ARKit's 52 as the guaranteed interchange set (iPhone, MediaPipe and VMC produce it), and a DNA + RigLogic rig underneath
**by MetaHuman's control, joint and part names** (the user's exception to the clean-room rule, names only — item 10),
so MetaHuman Animator drives JustStage faces directly. Body correctives are a second DNA file beside it (item 1).

## 7 · Everything is a command (R19, items 7, 8)

Blender's own lesson: operators without a context-free `execute()` "cannot be repeated from a script or macro";
operators "use the context instead" of taking data (§8). CC5 and iClone have an in-process Python API only, so a third
party had to build an HTTP + MCP bridge (§2). So each command is declared once — `Params`, `Result` and `main`, the
convention of Blender Lab's own MCP tools — with an operator for the UI that a test keeps in step. Blender Lab's server
(add-on + socket + stdio process) is used as it is, on the MCP version it speaks (2025-11-25); one small module of ours
in its tools folder (N6, approved) registers every command — plugins' included — as MCP tools at runtime, because
Blender Lab's own hand-written wrappers can't follow plugins. Its "no guards" Python tool is why permissions are
first-class (Cinema 4D's model — §4).

## 8 · Plugins, built-in and outside (R19, R2, item 27)

JustStage is **one** add-on, because Blender's manual says add-ons that depend on each other should be bundled
together and the manifest can't declare a dependency. Inside it, each feature is a module that registers through the
**same public plugin API** outside plugins use, listing the modules it needs — Unreal's built-in plugins and Blender's
bundled add-ons are the pattern — so features switch on and off on one Plugins page and always update together.
Outside plugins are their own Blender extensions; they find JustStage at `bl_ext.system.juststage`, stable because the
installer always puts it in Blender's System repository. Outside programs use the MCP door. A sandboxed WebAssembly
tier was the right design for an own-engine route and the wrong one inside Blender; it is not built.

## 9 · Import and export (R11, R12, items 11, 12, 13)

The reference apps converge on four steps — read, characterise, wrap, convert materials (S9) — so JustStage has four
commands and per-source profiles. Unreal reads more USD than any app checked, but its export is Beta and its morph
targets unverified (S9), so the plugin prefers the package and falls back to FBX. FBX is written by Blender's own
exporter, which has shipped for years (R17 as changed). CC5's and Daz's USD don't help (MDL materials; no Daz USD), so
their FBX plus sidecars stay the path. The keep-animation rule answers iClone users' loudest complaint (§3): re-import
in place, by the character's id, with a shared skeleton asset and append-only names.

## 10 · AI features through the family's engines (R14, items 14, 15, 25)

The web kit already installs, starts, books memory for and runs jobs on stable-diffusion.cpp, llama.cpp, ONNX Runtime
and audio.cpp (`RuntimeService`), with one model cache for the family (§10). A second copy inside Blender would be a
second cache and no arbiter — the kit's own "never" column. So every AI feature is a command that runs as a job on
**JustStage's own engine host**, a server-only package from the kit's template shipped in the installer; JustDirect
reuses it later, so a machine runs one host. A new kind of engine goes into the kit first, so the whole family gets it.
Live capture is the one exception — a stream, not a job — and runs inside Blender. One kit gap (an HTTP route that runs
an image feature as a job) was requested of the just-core session. The arbiter is per process and the card is 8 GB, so
image jobs are queued and JustStage lowers its own load while they run; the numbers come from the gate.

## 11 · Rendering, capture and testing (R15, R16, item 26)

EEVEE in real time and Cycles offline are Blender's; Unreal through the plugin gives MetaHuman-level real time — and
Unreal's mocap now (Live Link Face, MetaHuman Animator with 5.8's one-camera capture, Live Link devices). JustStage's
own live capture (webcam, the Live Link Face stream, VMC) comes with the Animate workspace. Tests are Blender's own
methods — headless Python, golden images with oiiotool thresholds on lavapipe and the macOS runner — because every
family app is built by AI agents and the tests are the eyes; the whole suite runs on each new Blender release before
the installer moves to it.

## 12 · One app, workspaces; JustDirect beside it (R6, R20)

iClone users' worst seam is the CC↔iClone round trip (§3), so scenes and animation come later in the same app as
workspaces (Blender's own mechanism). JustDirect stays a separate app: a local video clip takes 7.3 GB of the 8 GB card
(§10) and the two stacks differ; it drives JustStage over the API, takes its USD/glTF scenes and render passes, and
shares its engine host.

## 13 · The order (R21 as changed)

0 the standards spec → 1 the gate with a first plugin → 2 base, head and the generators → 3 photo-to-head →
4 rig, expressions, auto-rig and creatures → 5 clothes fitting → 6 import/export and the full plugin → 7 sculpt extras
→ 8 patterns → later: Animate (with JustStage's own live capture), or staying on Unreal. The scorecard's floor only
rises.

## 14 · What would change this architecture

| Trigger | Change |
|---|---|
| The gate fails on viewport work no extension can fix, an Animate workspace needs C work, or the branding must go | a Blender fork (R1's trigger), the add-on unchanged |
| The gate fails on hm08's topology | Blender Studio's base meshes with MakeHuman's sliders wrapped on (item 23) |
| AOUSD publishes character schemas | a converter maps the `juststage:` attributes onto them |
| Unreal's USD export carries morph targets reliably | the FBX fallback in the plugin is retired |
| An MIT tool must write FBX outside Blender | ufbx-write, once its round trips pass |
| Blender Lab's server moves to MCP 2026-07-28 | JustStage moves with it |
| MetaHuman's terms read one way (the user's reading) | "Send to Unreal as a MetaHuman" and DNA import are enabled or labelled accordingly |
| An Animate workspace is scheduled | iClone's inventory joins the scorecard; the animation data of the spec gets its editors; live capture is built |
