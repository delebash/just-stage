# The plugin contract — Blender extensions in process, the API for outside programs

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R19, R2. Facts: RESEARCH §4,
> §6, §8 (round one §5, S8.1 manifest text).

## 1 · Two kinds of plugin, one registry

| Kind | What it is | How it reaches JustStage | Licence it must carry |
|---|---|---|---|
| **In-process plugin** | a Blender extension (a `.zip` with `blender_manifest.toml`) that imports `juststage` and registers commands, panels, workspaces, importers, exporters, generators or material node groups | Python inside Blender; the `juststage` package's public API (§3) | GPL-compatible — Blender's rule for published add-ons (R2, §6) |
| **Outside program** | any program (JustDirect, a web app, a pipeline script, an AI agent) | the API: JSON-RPC 2.0 over the socket, MCP over stdio or HTTP ([`commands-and-api.md`](commands-and-api.md) §3–§4) | any licence (it doesn't link Blender) |

Standards: [Blender extensions](https://docs.blender.org/manual/en/latest/advanced/extensions/index.html) (manifest,
platform wheels, permissions with reasons, extensions.blender.org); the MCP spec. JustStage's own features ship as
in-process plugins too (the user's requirement: "with plugin capability" and the web kit's lesson that the plugin API
is proven on our own features — §8): `juststage` (core: data model, commands, API), `juststage_body`,
`juststage_head`, `juststage_skin`, `juststage_hair`, `juststage_clothes`, `juststage_rig`, `juststage_io`,
`juststage_unreal_bridge`, each a separate extension that depends on the core, so a character-only user installs only
what they use.

## 2 · The manifest

Blender's `blender_manifest.toml` as is (schema 1.0.0; `id`, semver `version`, `name`, `tagline`, `maintainer`,
`type = "add-on"`, `blender_version_min`, `license` as SPDX, `platforms`, `wheels`, `permissions` each with a reason
≤ 64 characters — §8 pass 2) **plus** a `[juststage]` table JustStage reads:

```toml
[juststage]
api_min = "1.0"            # the juststage core API version this plugin needs (semver; §3)
api_max = "1"              # optional: refuse to load on a later major (Godot's compatibility_minimum/maximum pattern, §8)
namespace = "js_hairpro"   # command prefix: js_<plugin>.<area>.<verb>; also the extensions key org.<vendor>.<plugin>
provides = ["commands", "generator:hair", "importer:xyz", "exporter:xyz", "workspace", "material"]
data_schema_version = 1    # version of the plugin's own data in `extensions`
```

Blender's permissions are disclosure only (Blender's manual: it "cannot prevent third-party add-ons from violating"
the online rule — §8 pass 2); JustStage enforces what it can: a plugin's commands inherit the API permission groups,
and a plugin that lists `network` without a reason is not loaded by `juststage` (a check at register time, not a
sandbox). **Not a sandbox:** in-process Python has Blender's full power, as in Maya, Houdini and Blender itself. A
sandboxed tier (WebAssembly components) was the standards agent's design for an own-engine route; it does not apply
to a Blender extension (no GPU or mesh access across the boundary — §8 pass 2) and is not built.

## 3 · The in-process API (`juststage.api`)

A versioned Python package, semver, `juststage.api.VERSION`:

| Area | Functions (generated or written; all typed, all documented from the schemas) |
|---|---|
| Commands | `register_command(cls)` (the decorator of [`commands-and-api.md`](commands-and-api.md) §2), `run(command_id, **params)`, `commands()` |
| Data | `Character(id)` with typed access to the JSON record and the data-blocks (`character.body`, `.sliders`, `.grooms`, `.garments`, `.materials`, `.provenance`), `characters()`, `get_extension(namespace)`, `set_extension(namespace, data)` |
| Registries | `register_generator(kind, cls)` (skin, eye, hair, texture, morph), `register_importer(fmt, cls)`, `register_exporter(fmt, cls)`, `register_material(kind, node_group)`, `register_workspace(name, layout)`, `register_slider_group(path)` |
| Jobs | `start_job(fn, label)`, `Job.progress`, `.cancel()` |
| Engines | `engines.image(request)`, `engines.ready(feature)` — the family engine host ([`ai-engines.md`](ai-engines.md)) |
| Events | `on("character.changed" \| "slider.changed" \| "file.loaded", fn)` — Blender's `bpy.app.handlers` and `msgbus` underneath |

Rules: a plugin never writes Blender data of a character except through `Character` or a command (so undo, migrations
and provenance stay right); a plugin's own data lives in `extensions[namespace]` with its own version; breaking API
changes bump the major and ship a deprecation period of one Blender LTS cycle.

## 4 · Outside programs

They use the API door and nothing else. The contract is the command schemas (published as an OpenRPC-style document
generated from them, plus the MCP `tools/list`). JustDirect (R20): drives JustStage over MCP/JSON-RPC, pulls packages
and glTF, pushes render passes requests. Unreal: the JustStage plugin talks to Blender's socket for Live Link and
"update character" ([`import-export.md`](import-export.md) §5). A Houdini-Engine-style "JustStage inside another app"
is this door plus that app's own UI.

## 5 · Distribution

- JustStage's extensions: extensions.blender.org (the platform's review and GPL requirement), and a JustStage remote
  extension repository (Blender supports third-party repositories) for pre-release builds.
- Third-party plugins: the same two paths; the manifest's `[juststage]` table is what JustStage checks at load.
- The Unreal plugin: GitHub releases and Fab (free), MIT (R2, R12).
