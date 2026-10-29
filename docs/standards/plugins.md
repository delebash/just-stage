# The plugin contract — one Blender extension with modules, third-party extensions in process, the API for outside programs

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R19, R2. Facts: RESEARCH §4,
> §6, §8 (round one §5, S8.1 manifest text); Blender's extension manifest page re-read 2026-10-29 (RESEARCH §8).
> Rewritten 2026-10-29: the first draft split JustStage into several inter-dependent extensions and added a custom
> table to the manifest — Blender's manifest has no dependency field and documents no custom tables, so both were
> NOT STANDARD and are gone.

## 1 · Shape

| Kind | What it is | How it reaches JustStage | Licence it must carry |
|---|---|---|---|
| **JustStage** | **one** Blender extension, `juststage` (a `.zip` with `blender_manifest.toml`), with feature **modules** the user turns on and off in its preferences (Body, Head & Face, Skin, Hair, Clothes, Rig, Import/Export, Unreal bridge, API) — Blender's own pattern for big add-ons (Rigify's feature sets, Node Wrangler's options) | — | GPL-3.0-or-later (Blender's rule for published add-ons, R2) |
| **The application template** | `juststage_app/` — splash, startup file, workspaces, theme, keymaps; it enables the extension | Blender application templates | GPL-compatible |
| **Third-party in-process plugin** | its own Blender extension that `import juststage` and registers commands, panels, generators, importers, exporters or material node groups in `register()` | the `juststage.api` Python package (§3) | GPL-compatible (it runs inside Blender) |
| **Outside program** | any program (JustDirect, a pipeline script, an AI agent) | the API door: MCP over stdio or Streamable HTTP ([`commands-and-api.md`](commands-and-api.md) §4) | any licence (it doesn't link Blender) |

Why one extension: Blender's manifest has no field for depending on another extension (its documented fields:
`schema_version`, `id`, `version`, `name`, `tagline`, `maintainer`, `type`, `blender_version_min`, `license`;
optional `blender_version_max`, `website`, `copyright`, `tags`, `platforms`, `wheels`; tables `[permissions]`,
`[build]`, `[asset_library]` — read 2026-10-29), so "extension B needs extension A" cannot be declared or installed
from extensions.blender.org. A character-only user gets the same lightness by disabling modules.

Standards: [Blender extensions](https://docs.blender.org/manual/en/latest/advanced/extensions/index.html),
[application templates](https://docs.blender.org/manual/en/latest/advanced/app_templates.html), the MCP spec.

## 2 · The manifest and registration

The manifest is **stock** `blender_manifest.toml` — nothing JustStage-specific in it. Compiled parts (OpenRigLogic's
Python bindings, later Jolt) ship as platform `wheels`, the manifest's own mechanism; `[permissions]` lists `files`
(the project and library folders), `network` (the family engine host on loopback) and `camera` (webcam capture), each
with its reason.

A third-party plugin declares itself to JustStage in Python, the way Blender add-ons talk to each other:

```python
import juststage

def register():
    juststage.api.register_plugin(
        id="js_hairpro",                 # command prefix js_hairpro.<area>.<verb>; customData key org.<vendor>.<plugin>
        api=">=1.0,<2",                  # the juststage.api version range it needs (semver)
        provides=["commands", "generator:hair"],
        schema="schema.usda",            # optional: its own USD applied API schemas (its data in the package)
    )
```

`register_plugin` refuses a plugin outside the API range with the versions named (Godot's compatibility-range
behaviour, §8). Blender's permissions are disclosure only (§8 pass 2); the plugin's commands inherit the API's
permission groups. **Not a sandbox:** in-process Python has Blender's full power, as in Maya, Houdini and Blender
itself. A sandboxed WebAssembly tier was the standards agent's design for an own-engine route; it does not apply to a
Blender extension (no GPU or mesh access across the boundary — §8 pass 2) and is not built.

## 3 · The in-process API (`juststage.api`)

A versioned Python package, semver, `juststage.api.VERSION`:

| Area | Functions (generated or written; all typed, all documented from the schemas) |
|---|---|
| Plugins | `register_plugin(...)` (§2) |
| Commands | `register_command(cls)` (the decorator of [`commands-and-api.md`](commands-and-api.md) §2), `run(command_id, **params)`, `commands()` |
| Data | `Character(id)` with typed access to the schema data and the data-blocks (`character.body`, `.sliders`, `.grooms`, `.garments`, `.materials`, `.provenance`), `characters()`, `custom_data(namespace)` |
| Registries | `register_generator(kind, cls)` (skin, eye, hair, texture, morph), `register_importer(fmt, cls)`, `register_exporter(fmt, cls)`, `register_material(kind, node_group)`, `register_workspace(name, layout)`, `register_slider_group(path)`, `register_capture_source(kind, cls)` |
| USD | `register_usd_schema(path)` — adds a plugin's `schema.usda` to the USD hook's writers and readers |
| Jobs | `start_job(fn, label)`, `Job.progress`, `.cancel()` |
| Engines | `engines.image(request)`, `engines.ready(feature)` — the family engine host ([`ai-engines.md`](ai-engines.md)) |
| Events | `on("character.changed" \| "slider.changed" \| "file.loaded", fn)` — Blender's `bpy.app.handlers` and `msgbus` underneath |

Rules: a plugin never writes a character's Blender data except through `Character` or a command (so undo, migrations
and provenance stay right); a plugin's own data lives in its applied schemas or in `customData` under its namespace,
with its own version; breaking API changes bump the major and ship a deprecation period of one Blender LTS cycle.

## 4 · Outside programs

They use the API door and nothing else. The contract is the command schemas (published as an OpenRPC-style document
generated from them, plus the MCP `tools/list`). JustDirect (R20): drives JustStage over MCP, pulls packages and glTF,
pushes render-pass requests. Unreal: the JustStage plugin talks to the MCP HTTP transport for "update character" and
to Live Link for streams ([`import-export.md`](import-export.md) §5). A Houdini-Engine-style "JustStage inside another
app" is this door plus that app's own UI.

## 5 · Distribution

- `juststage` and the application template: extensions.blender.org (the platform's review and GPL requirement), and a
  JustStage remote extension repository (Blender supports third-party repositories) for pre-release builds.
- Third-party plugins: the same two paths.
- The Unreal plugin: GitHub releases and Fab (free), MIT (R2, R12).
