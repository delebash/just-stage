# Commands and the API — operators, one JSON Schema per command, the MCP server and its permissions

> **Status: DRAFT, 2026-10-29 — for the user's approval** (see [`README.md`](README.md)). R19, R20. Facts: RESEARCH §4
> (Cinema 4D's MCP, Houdini Engine), §6 (Blender Lab's MCP server), §8 (round one §4, S8.1 operator rules, S8.3 MCP
> 2026-07-28), §11 (PhotoCraft's command registry); Blender Lab's `blender_mcp` readme, read by this session
> 2026-10-29 (RESEARCH §6).

## 1 · The rule

**Every action JustStage can do is one command: a Blender operator with a context-free `execute()`, described by one
JSON Schema, reachable the same way from the UI, Python, the command line and the MCP server.** The user's words
(TASKS): "an api that user can connect to so we need to define standards for everything we do before we write code".

Standards: [Blender operators](https://docs.blender.org/api/current/bpy.types.Operator.html) (`bl_idname`, typed
properties as arguments, `poll`, `execute`, `REGISTER | UNDO`); [JSON Schema 2020-12](https://json-schema.org/draft/2020-12);
[MCP 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28); [JSON-RPC 2.0](https://www.jsonrpc.org/specification);
the registry shape of PhotoCraft (id, label, menu path, shortcut, params doc, enabled, run — §11).

## 2 · A command

```python
@command(
    id="juststage.body.set_slider",             # also the operator's bl_idname
    label="Set body slider",
    menu="Character > Body",                    # where the UI puts it (optional)
    schema="schemas/commands/body.set_slider.json",
    since="2026-11-01",
)
class BodySetSlider(bpy.types.Operator):
    bl_options = {"REGISTER", "UNDO"}
    # properties are GENERATED from the schema at registration (one source)
    @classmethod
    def poll(cls, context): ...                 # explains itself with poll_message_set
    def execute(self, context):                  # works from its properties alone — never from selection or the mouse
        ...
        return {"FINISHED"}
    def invoke(self, context, event):            # may only FILL properties from the UI, then call execute
```

Rules (Blender's own words behind them — §8 pass 2):

- `execute()` runs from explicit parameters, never from UI context. Blender: operators without `execute()` "cannot
  be repeated from a script or macro"; `invoke()` and modal tools only fill parameters. Objects are named by
  parameter (`character`, `garment`), never "the selection" — Blender's own gotcha list says operators "Can't pass
  data such as objects … (operators use the context instead)", which is what we avoid.
- `UNDO` on every command that changes data ("mandatory if the operator modifies Blender data"); `CANCELLED` means no
  change. Repeated drags use `UNDO_GROUPED`. Undo is Blender's one typed stack (memfile snapshots for general edits,
  sculpt steps for sculpt — §8 pass 2); JustStage adds no undo system of its own.
- `poll()` failures carry a message (`poll_message_set`) naming the missing condition.
- The **schema** (one file per command, JSON Schema 2020-12) is the source of truth: `title`, `description`,
  `properties` with `description`, `enum`, bounds and defaults, `required`, an `x-juststage` block (`since`,
  `deprecated`, `permission`, `undo`, `headless: true|false`, `returns` schema). From it the build generates the
  operator properties, the MCP tool, the CLI help and the reference docs. A command without a schema does not
  register (a test enforces it).
- Results: a command returns data through its `returns` schema (written to `context.scene.juststage.last_result` for
  Python and to the JSON-RPC response for remote callers), not through `report()` alone.
- Long commands (generation, baking, import) run as **jobs**: `juststage.jobs.start` returns a job id; `jobs.status`,
  `jobs.events`, `jobs.cancel` follow it; the UI shows Blender's progress cursor and a Jobs panel. Standard: Blender's
  modal timer for in-process work; `subprocess` for the engine host's HTTP jobs ([`ai-engines.md`](ai-engines.md)).

Namespaces: `juststage.<area>.<verb>_<object>`; areas: `base`, `body`, `head`, `skin`, `eyes`, `mouth`, `hair`,
`clothes`, `rig`, `face`, `pose`, `import`, `export`, `library`, `gate`, `jobs`, `api`. Plugins register under
`js_<plugin>.<area>.<verb>` ([`plugins.md`](plugins.md)).

## 3 · The four doors

| Door | How | Standard |
|---|---|---|
| UI | panels, menus and keymaps call the operator; the application template owns the layout (R1) | Blender |
| Python | `bpy.ops.juststage.body_set_slider(character="Eve", slider="nose-width", value=0.4)`; a thin `juststage.api` module wraps it with typed functions generated from the schemas | Blender `bpy.ops` |
| Command line | `blender -b file.blend --python-expr "import juststage; juststage.cli(['body.set_slider', '--character', 'Eve', …])"` and a `juststage` console script that wraps that line; `--json` input and output; exit codes | Blender `-b --python` (R16) |
| Remote (programs and agents alike) | **MCP** — over stdio for clients that launch it, over Streamable HTTP on loopback for programs such as JustDirect (§4). MCP is JSON-RPC 2.0, so there is no second remote protocol | MCP 2026-07-28 |

## 4 · The MCP server (R19)

**Base: Blender Lab's `blender_mcp`** (GPL-3.0-or-later, Blender 5.1+ — §6), reused as its readme describes it: "two
components that communicate over a TCP socket: A Blender add-on that runs inside Blender and executes requests. An
MCP server that runs as a separate process, launched by the MCP client"; data flow
`MCP Client ⇐ MCP/stdio ⇒ blender-mcp ⇐ TCP socket ⇒ Blender Add-on`; the add-on has preferences for host, port and
auto-start, polling intervals, client timeouts, and "background mode requires requests to complete synchronously".

JustStage's shape, built on it:

| Piece | JustStage | Note |
|---|---|---|
| In Blender | Blender Lab's add-on socket server, as it is, inside the JustStage extension's API module: its `{type, params}` wire stays **private** between the two JustStage processes (nothing else speaks it) | reusing Blender Lab's code unchanged, GPL inside GPL |
| Outside | `juststage-mcp`, Blender Lab's `blmcp` server process with JustStage's tool modules, started by the client over **stdio**, or started by JustStage with **Streamable HTTP** on loopback for programs such as JustDirect; MCP revision 2026-07-28: stateless, version and capabilities in `_meta`, `server/discover`, JSON Schema 2020-12 tool schemas, deterministic `tools/list` | the MCP spec's two transports; the only public protocol |
| Tools | **generated from the command schemas** — one MCP tool per command whose `x-juststage.headless` is true, `inputSchema` = the command schema, `outputSchema` = `returns`; grouped by area for the permission UI | one schema, four doors |
| State | an open file, a character, a selection are **explicit handles** in tool arguments (`character_id`), never session state — MCP 2026-07-28 removed sessions (§8 pass 2) | |
| Resources | read-only views: a character's schema data (as USDA text), the slider list, the scorecard, the gate's last report, the API reference | MCP resources |
| Port | the MCP HTTP transport on **17480** (loopback only; approved 2026-10-29), registered in the 3D family table ([`README.md`](README.md) §3); the private socket on the port Blender Lab's add-on preferences set; both configurable | — |

**Permissions** — the attack on Blender Lab's server (it runs model code "without any guards" — §6) and the model
Cinema 4D ships (off by default, local, an access token, the user picks the tool groups — §4):

| Rule | Detail |
|---|---|
| Off by default | the API starts when the user turns it on in preferences or passes `--juststage-api` headless |
| Loopback only | the socket and HTTP bind 127.0.0.1; a remote host needs an explicit preference and a token |
| Token | an access token generated by JustStage, shown in preferences, required on HTTP; stdio inherits the user's session |
| Tool groups | the user ticks areas (`read`, `body`, `head`, …, `import`, `export`, `files`) per client; a tool outside the ticked groups returns a JSON-RPC error naming the group |
| Python | `juststage.api.run_python` exists (Blender Lab's code-execution tool) but is **its own group, off by default, and asks in the UI on first use per session** (R19: "Python over MCP behind a permission"); headless it needs `--juststage-allow-python` |
| Files | import/export commands may read and write only inside folders the user listed (project, library, exchange); anything else is refused with the path named |
| Network | the engine host's address only ([`ai-engines.md`](ai-engines.md)); `bpy.app.online_access` respected |
| Log | every remote call is logged with its client, tool and arguments (secrets redacted) |

## 5 · What is not a command

Live streams (webcam, VMC, Live Link) feed poses and face controls continuously; they are turned on and off by
commands (`juststage.face.capture_start`) but their frames are not commands and leave no undo steps
([`skeleton-and-face.md`](skeleton-and-face.md) §4). Viewport drawing and gizmos are UI.

## 6 · The reference apps' lessons kept

- Blender: context-only operators and opaque `poll` failures are the scripting pain points — hence §2.
- blender-mcp and Unreal 5.8's MCP: arbitrary code, no authentication, loopback assumed — hence §4's permissions.
- CC5/iClone: an in-process Python API only, no outside door, so a third party built an HTTP + MCP bridge (§2) — hence
  the remote door is first-class.
- Houdini Engine: our tools inside other apps run through the API, in or out of process (§4) — JustDirect uses it
  (R20); an Unreal-side "JustStage panel" can later call the same API.
