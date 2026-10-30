# The plugin contract — built-in modules, outside plugins, the API for outside programs, distribution

> **Status: APPROVED recs, written 2026-10-29** (the review's items 24 and 27 — TASKS; review file
> [`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md)). R19, R2. Facts: RESEARCH §4,
> §6, §8; Blender facts on the installed 5.3 and its manual (`advanced/extensions/`).

## 1 · Shape

The user: "i agree our bundle of plugins for features should not be seperate donwloads"; "i like the modular design
idea".

| Kind | What it is | How it reaches JustStage | Licence |
|---|---|---|---|
| **JustStage** | **one** Blender add-on, `juststage` (a `.zip` with a stock `blender_manifest.toml`), installed by JustStage's installer into Blender's **System** extension repository (§5). Inside it: a small **core** that is always on (the character data, the commands, the API, the USD and glTF hooks) and the **built-in modules** | — | GPL-3.0-or-later (Blender's rule for add-ons, R2) |
| **Built-in module** | one feature — Body, Head & Face, Photo-to-head, Skin, Eyes, Hair, Clothes, Rig, Creature, Capture, Import/Export, Unreal bridge, AI — a separate package inside the add-on that registers through the **same public plugin API** outside plugins use (§3), so each is a plugin that ships in the box | `juststage.api.register_plugin` | as JustStage |
| **The application template** | `juststage` — splash, startup file, workspaces, theme, keymaps; it enables the add-on | Blender application templates, found through `BLENDER_SYSTEM_SCRIPTS` (§5) | GPL-compatible |
| **Outside plugin** | its own Blender extension that imports `bl_ext.system.juststage` and calls `register_plugin` in `register()` | the `juststage.api` package (§3) | GPL-compatible (it runs inside Blender) |
| **Outside program** | any program (JustDirect, a pipeline script, an AI agent) | the API door: MCP over stdio or Streamable HTTP ([`commands-and-api.md`](commands-and-api.md) §4) | any licence (it doesn't link Blender) |

Why one add-on for our own features: Blender's manual — "For add-ons to be bundled as extensions, they must be
self-contained"; "Bundle other add-ons together. This is recommended if an add-on depends on another add-on"
(`addons.rst`, 5.3) — and the manifest has no field for one extension depending on another, so separate extensions for
our own features would drift onto mismatched versions. Built-in modules update together, always.

Standards: Unreal's built-in plugins (shipped with the engine, each switchable, each listing the plugins it needs)
and Blender's bundled add-ons are the pattern; [Blender extensions](https://docs.blender.org/manual/en/5.3/advanced/extensions/index.html),
[application templates](https://docs.blender.org/manual/en/5.3/advanced/app_templates.html), the MCP spec.

## 2 · Registration, switching and finding JustStage

**Finding JustStage.** An extension's Python module is `bl_ext.{repository_module_name}.<id>` (manual `addons.rst`),
so a bare `import juststage` can't work. The installer always puts JustStage in Blender's System repository, whose
module is `system` (`BKE_preferences_extension_repo_add_default_system`: name "System", module "system" — Blender 5.3
source), so its module is always **`bl_ext.system.juststage`**:

```python
import importlib

def register():
    js = importlib.import_module("bl_ext.system.juststage")
    js.api.register_plugin(
        id="js_hairpro",                 # command prefix js_hairpro.<area>.<verb>; attribute namespace js_hairpro:
        api=">=1.0,<2",                  # the juststage.api version range it needs (semver)
        needs=["hair"],                  # the modules it needs
        provides=["commands", "generator:hair"],
    )
```

- `register_plugin` refuses a plugin outside the API range with the versions named (Godot's compatibility-range
  behaviour, §8), and one whose `needs` aren't on.
- **Built-in modules** call the same function from the core, with `needs` naming the modules they depend on
  (Photo-to-head needs Head & Face; Skin needs Body) — the way Unreal's plugin descriptors list theirs. Switching off a
  module that others need asks before switching those off too.
- **One Plugins page** in JustStage's preferences lists the built-in modules and the installed outside plugins, each
  with an on/off switch. For outside plugins the switch is Blender's own add-on switch (`addon_utils.enable` /
  `disable`), so Blender's add-on list and ours always agree. Switching a module or plugin off unregisters it fully:
  its panels, menus, commands and MCP tools go ([`commands-and-api.md`](commands-and-api.md) §4).
- The manifest is **stock**; compiled parts (OpenRigLogic's Python bindings built for Python 3.13, MediaPipe's wheels,
  later Jolt) ship as the manifest's `wheels`; `[permissions]` lists `files`, `network` (the engine host on loopback)
  and `camera` (webcam capture), each with its reason. Blender's permissions are disclosure only (§8).
- **Not a sandbox:** in-process Python has Blender's full power, as in Maya, Houdini and Blender itself. A sandboxed
  WebAssembly tier was a design for an own-engine route; it doesn't fit a Blender extension (no GPU or mesh access
  across the boundary — §8) and is not built.

## 3 · The in-process API (`juststage.api`)

A versioned Python package, semver, `juststage.api.VERSION`:

| Area | Functions (typed, documented) |
|---|---|
| Plugins | `register_plugin(...)` (§2), `plugins()` |
| Commands | `register_command(module)` (a module with `Params`, `Result`, `COMMAND`, `main` — [`commands-and-api.md`](commands-and-api.md) §2), `run(command_id, **params)`, `commands()` |
| Data | `Character(id)` with typed access to the data-blocks and fields (`character.body`, `.sliders`, `.grooms`, `.garments`, `.materials`, `.provenance`), `characters()` |
| Registries | `register_generator(kind, cls)` (skin, eye, hair, texture, morph), `register_importer(fmt, cls)`, `register_exporter(fmt, cls)`, `register_material(kind, node_group)`, `register_workspace(name, layout)`, `register_slider_group(path)`, `register_capture_source(kind, cls)` |
| USD and glTF | `register_attributes(namespace, fields)` — a plugin's own `<id>:` attributes, written and read by the core's USD and glTF hooks |
| Jobs | `start_job(fn, label)`, `Job.progress`, `.cancel()` |
| Engines | `engines.run(feature, request)`, `engines.ready(feature)` — the engine host ([`ai-engines.md`](ai-engines.md)) |
| Events | `on("character.changed" \| "slider.changed" \| "file.loaded", fn)` — Blender's `bpy.app.handlers` and `msgbus` underneath |

Rules: a plugin never writes a character's Blender data except through `Character` or a command (so undo, migrations
and provenance stay right); a plugin's own data lives in its own attribute namespace or in `customData` under its
reverse-DNS key, with its own version; breaking API changes bump the major and ship a deprecation period of one
Blender LTS cycle (two years — Blender's LTS span, §8).

## 4 · Outside programs

They use the API door and nothing else. The contract is the command list (the MCP `tools/list`, generated by the
registrar). JustDirect (R20): drives JustStage over MCP, pulls packages and glTF, pushes render-pass requests. Unreal:
the JustStage plugin talks to the MCP HTTP transport for "update character" and to Live Link for streams
([`import-export.md`](import-export.md) §5). A Houdini-Engine-style "JustStage inside another app" is this door plus that
app's own UI.

## 5 · Distribution — JustStage opens as its own app (item 24)

The user: "i want our app to look like a custom app so user donest have to load plugin it just laucnhe like an app we
built even thought it is using blender core features".

- **One installer per OS** holds: an **unmodified Blender** (the newest release, 5.3 now — R1 as changed, item 16), the
  `juststage` add-on, the application template, Blender Lab's MCP add-on and server ([`commands-and-api.md`](commands-and-api.md)
  §4), and JustStage's engine host with its Node runtime ([`ai-engines.md`](ai-engines.md)). Installed size about 1 GB
  (Blender 5.3 beta's folder is 956 MB).
- **A JustStage launcher** (our name and icon in the Start menu, Dock or app list) starts Blender with
  `--app-template juststage` and environment variables pointing at JustStage's own folders: `BLENDER_USER_RESOURCES`
  (its own preferences, user extensions and the template under `scripts/startup/bl_app_templates_user/` — apart from any
  Blender the user has) and `BLENDER_SYSTEM_EXTENSIONS` (whose `system` folder is the System repository — measured on
  5.3 — holding `juststage` and Blender Lab's add-on, pre-installed; system repositories "are managed outside of Blender
  and are considered read-only"). The template switches the add-on on itself, the way the manual describes ("You may
  enable add-ons associated with your template", defaults set "via handler": `load_factory_preferences_post`,
  `load_factory_startup_post`, plus `load_post`) — not from its `register()`, which runs before the extension system is
  up (measured). `BLENDER_SYSTEM_SCRIPTS` is **not** used: on 5.3, setting it stops Blender finding
  its own `bl_pkg` at start ("No module named 'bl_pkg'"), and extension add-ons are then not loaded (measured
  2026-10-29). Blender's own files are not touched.
- **What still says Blender:** the window title ends "— Blender 5.3" (built in C, `wm_window_title_text`; with a Blender
  project active it reads "<file> - <project> — Blender 5.3") and the running window has Blender's icon. Removing them
  is a change to Blender's code — a fork, R1's trigger — not done for a title bar.
- **Updates:** a new JustStage release ships a new installer; it moves to each new Blender release after the test
  suite passes on it ([`testing.md`](testing.md)).
- **Licences:** shipping Blender's binaries means offering its source (GPL); the add-on is GPL already (R2).
- **Outside plugins** install through Blender's own extension tools (Install from Disk, or a JustStage plugin
  repository — Blender supports third-party repositories) into JustStage's user repository.
- **The Unreal plugin:** GitHub releases and Fab (free), MIT (R2, R12).
- **Not used:** Blender as a Python module — it "runs without a user interface, like running regular Blender in
  background mode" (`WITH_PYTHON_MODULE`, Blender's CMake), so every editor would be lost.
