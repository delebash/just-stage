# Commands and the API — one declaration per command, four doors, the MCP server and its permissions

> **Status: APPROVED recs, written 2026-10-29** (the review's items 7 and 8, the command registrar approved by name —
> TASKS; review file [`../plans/2026-10-29-spec-review-opus.md`](../plans/2026-10-29-spec-review-opus.md)). R19 as
> changed, R20. Facts: RESEARCH §4 (Cinema 4D's MCP, Houdini Engine), §6 and §8 (Blender Lab's `blender_mcp`, the MCP
> Python SDK), §11 (PhotoCraft's command registry).

## 1 · The rule

**Every action JustStage can do is one command, declared once, reachable the same way from the UI, Python, the command
line and the MCP server.** The user's words (TASKS): "an api that user can connect to so we need to define standards
for everything we do before we write code".

Standards: [Blender operators](https://docs.blender.org/api/5.3/bpy.types.Operator.html) for the UI door; Blender Lab's
MCP server's own tool pattern for the declaration and the remote door (§4); the
[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) (FastMCP) for the tool schemas; the registry shape
of PhotoCraft (id, label, menu path, shortcut, params doc, enabled, run — §11).

## 2 · A command

Blender Lab's server declares each tool as a pair — a FastMCP function with typed arguments, and a `<tool>_toolcode.py`
with `Params` and `Result` `NamedTuple`s and a `main(params)` that runs inside Blender (`render_viewport_to_path`,
§8). JustStage follows that convention, with the declaration living in the extension so plugins can add commands:

```python
# juststage/commands/body/set_slider.py — inside the extension; pure Python at module level (bpy imported in main)
from typing import NamedTuple

class Params(NamedTuple):
    character: str          # the character's assetInfo identifier
    slider: str             # a slider id from target.json / macro.json
    value: float

class Result(NamedTuple):
    status: str
    value: float

COMMAND = dict(id="juststage.body.set_slider", label="Set body slider", menu="Character > Body",
               permission="body", undo=True, headless=True, since="2026-11-01")

def main(params: Params) -> Result: ...      # works from params alone — never from selection or the mouse
```

Rules:

- **One declaration** per command: its `Params`, `Result`, `COMMAND` record and `main`. `Params` fields use JSON types
  only (`str`, `int`, `float`, `bool`, `list[...]` of those, `Literal[...]` for choices), with defaults where optional.
- **The operator** for the UI and keymaps is a thin wrapper (`JUSTSTAGE_OT_body_set_slider`): its `bpy.props` mirror
  `Params` in Blender's own declaration style, its `execute()` builds `Params` from them and calls `main`. **One test per
  command** checks that the operator's properties match `Params` (names, types, defaults) — Blender's declaration stays
  standard, and the duplicate can't drift.
- `execute()` and `main` run from explicit parameters, never from UI context — Blender: operators without `execute()`
  "cannot be repeated from a script or macro"; operators "Can't pass data such as objects … (operators use the context
  instead)" (§8), which is what we avoid. Objects are named by parameter (`character`, `garment`), never "the selection".
- **Undo:** a data-changing command run through the operator gets Blender's `REGISTER | UNDO`; run through Python or
  MCP, `juststage.api.run` pushes one undo step after it (`bpy.ops.ed.undo_push`). Repeated drags use `UNDO_GROUPED`.
  JustStage adds no undo system of its own (§8).
- `poll` failures carry a message (`poll_message_set`) naming the missing condition.
- **Results** are `main`'s return value: Python callers get the `Result`; MCP callers get it as JSON over Blender Lab's
  socket, as Blender Lab's own tools return theirs. No scene property for results.
- **Long commands** (generation, baking, import) run as **jobs**: `juststage.jobs.start` returns a job id; `jobs.status`,
  `jobs.events`, `jobs.cancel` follow it; the UI shows a Jobs panel. Blender's modal timer for in-process work; the
  engine host's HTTP jobs for models ([`ai-engines.md`](ai-engines.md)).

Namespaces: `juststage.<area>.<verb>_<object>`; areas: `base`, `body`, `head`, `skin`, `eyes`, `mouth`, `hair`,
`clothes`, `rig`, `creature`, `face`, `capture`, `pose`, `import`, `export`, `library`, `gate`, `ai`, `jobs`, `api`.
Plugins — our built-in modules included — register under their module or plugin id ([`plugins.md`](plugins.md)).

## 3 · The four doors

| Door | How | Standard |
|---|---|---|
| UI | panels, menus and keymaps call the operator; the application template owns the layout | Blender |
| Python | `juststage.api.run("body.set_slider", character=…, slider="nose-width", value=0.4)` → `Result`; the module is `bl_ext.system.juststage.api` ([`plugins.md`](plugins.md) §2) | Blender extensions |
| Command line | `blender -b file.blend --python-expr "import bl_ext.system.juststage as js; js.cli([...])"` and a `juststage-cli` script the installer adds; `--json` input and output; exit codes | Blender `-b --python` (R16) |
| Remote (programs and agents alike) | **MCP** — stdio for clients that launch it, Streamable HTTP on loopback for programs such as JustDirect (§4). MCP is JSON-RPC 2.0, so there is no second remote protocol | MCP 2025-11-25 |

## 4 · The MCP server

**Base: Blender Lab's `blender_mcp`, as it is** (GPL-3.0-or-later; latest release v1.0.3, 2026-09-11; depends on
`mcp[cli]>=1.2.0,<2` — §8): "two components that communicate over a TCP socket: A Blender add-on that runs inside
Blender and executes requests. An MCP server that runs as a separate process, launched by the MCP client"; data flow
`MCP Client ⇐ MCP/stdio ⇒ blender-mcp ⇐ TCP socket ⇒ Blender Add-on`. The installer ships both
([`plugins.md`](plugins.md) §5).

| Piece | JustStage | Standard |
|---|---|---|
| Protocol version | **2025-11-25**, the version Blender Lab's server speaks through MCP SDK 1.x (`LATEST_PROTOCOL_VERSION`); clients on SDK 2.x speak it too (2.x knows 2026-07-28 "beside the handshake versions" — §8). JustStage moves when Blender Lab moves, and offers them the SDK-2 change upstream — **R19 as changed** (the user: "i agree with your recs"; item 8) | MCP 2025-11-25 |
| In Blender | Blender Lab's add-on and its socket, unchanged; its wire stays private between the two processes | reuse, GPL inside GPL |
| Outside | Blender Lab's `blmcp` server process, started by the client over stdio, or by JustStage with Streamable HTTP on loopback | the MCP spec's two transports |
| **JustStage's tools — the command registrar** | one module, `juststage_commands.py`, placed in Blender Lab's `blmcp/tools/` folder, which the server auto-discovers at startup (`pkgutil.iter_modules`, then each module's `register(mcp)`). Its `register` asks Blender over the socket for every command — ours and plugins' — with its `Params` fields, description and `COMMAND` record, builds a function with that signature (`__signature__`, which FastMCP reads with `inspect.signature`), and adds it with `FastMCP.add_tool`; the tool's JSON Schema is the one FastMCP derives. When plugins are switched on or off, it adds or removes tools (`add_tool` / `remove_tool`) and sends the SDK's tool-list-changed notice (`send_tool_list_changed()`, the SDK's "Dynamic Tools" example) | **NOT STANDARD — APPROVED 2026-10-29** ("your rec on all 1-6 … go", TASKS): our own small module on the SDK's documented calls. Standard option: Blender Lab's hand-written wrapper per tool — it can't follow plugins that come and go |
| State | an open file, a character, a selection are **explicit handles** in tool arguments (`character`), never session state | — |
| Resources | read-only views: a character's fields, the slider list, the scorecard, the gate's last report, the API reference | MCP resources |
| Port | the MCP HTTP transport on **17480** (loopback only; approved 2026-10-29), in the 3D family table ([`README.md`](README.md) §3); the private socket on the port Blender Lab's add-on preferences set | — |

**Permissions** — the attack on Blender Lab's server (its Python tool runs code "without any guards" — §6) and the
model Cinema 4D ships (off by default, local, an access token, the user picks the tool groups — §4):

| Rule | Detail |
|---|---|
| Off by default | the API starts when the user turns it on in JustStage's preferences, or with `--juststage-api` headless |
| Loopback only | the socket and HTTP bind 127.0.0.1; a remote host needs an explicit preference and a token |
| Token | an access token generated by JustStage, shown in preferences, required on HTTP; stdio inherits the user's session |
| Tool groups | the user ticks areas (`read`, `body`, `head`, …, `import`, `export`, `files`, `ai`) per client; the registrar adds only ticked groups' tools; a call outside them returns an error naming the group |
| Python | Blender Lab's `execute_blender_code` is **its own group, off by default** — the registrar removes it (`remove_tool`) unless the user turned it on, and JustStage asks in the UI on first use per session (R19: "Python over MCP behind a permission"); headless it needs `--juststage-allow-python` |
| Files | import/export commands may read and write only inside folders the user listed (project, library, exchange) |
| Network | the engine host's address only ([`ai-engines.md`](ai-engines.md)); `bpy.app.online_access` respected |
| Log | every remote call is logged with its client, tool and arguments (secrets redacted) |

## 5 · What is not a command

Live streams (webcam, phone face, VMC, Live Link) feed poses and the face continuously; they are turned on and off by
commands (`juststage.capture.start`) but their frames are not commands and leave no undo steps
([`skeleton-and-face.md`](skeleton-and-face.md) §4). Viewport drawing and gizmos are UI.

## 6 · The reference apps' lessons kept

- Blender: context-only operators and opaque `poll` failures are the scripting pain points — hence §2.
- blender-mcp and Unreal 5.8's MCP: arbitrary code, no authentication, loopback assumed — hence §4's permissions.
- CC5/iClone: an in-process Python API only, no outside door, so a third party built an HTTP + MCP bridge (§2) — hence
  the remote door is first-class.
- Houdini Engine: our tools inside other apps run through the API, in or out of process (§4) — JustDirect uses it
  (R20); an Unreal-side "JustStage panel" can later call the same API.
