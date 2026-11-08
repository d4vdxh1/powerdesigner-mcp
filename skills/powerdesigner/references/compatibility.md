# Compatibility and evidence matrix

Statuses below describe **verified testing** versus **not yet tested** environments.

| Component | Status | Evidence / remaining work |
| --- | --- | --- |
| Windows 11, Python 3.12, PowerDesigner 16.5.0.3982 | Tested on one development machine | COM link, model and class-diagram tools |
| MCP streamable HTTP on localhost | Tested locally | initialize, tools/list, denied write |
| 11 MCP tool registrations | Tested | Static inspection and tools/list |
| Class-diagram geometry changes | Tested with a copy | Inspected 22 symbols; package and dependency geometry changed, restored and saved |
| Deny write without allowed model | Tested | `guardar_modelo` returned `Edicion deshabilitada` |
| Updated ChatGPT tunnel installation | **Verified for two read-only calls** (2026-11-08) | `consultar_modelo_activo` and `listar_coleccion("Packages")` returned actual results through the tunnel; no writes tested |
| Claude Free, skill ZIP v0.2.0 | **Imported; instructions evaluated** (user-provided screenshots/transcripts, 2026-11-08) | Loaded five files; correctly classified 11 tools and declined to fabricate results without connected MCP tools |
| Claude Free → PowerDesigner MCP | **Not tested** | Claude lacked an MCP PowerDesigner connection; import of skill alone does not provide tools |
| Claude Code / Cursor / Codex | **Not tested** | Must configure each client and demonstrate real MCP calls |
| Other PowerDesigner versions | **Not tested** | Verify COM/metamodel behavior |
| Clean setup on different Windows machine | **Not tested** | Install from repository and reproduce the read-only checks |
| Agensi ZIP import and skill invocation | **Not tested** | Upload/package/permissions and client execution required |

## Acceptance steps per client

1. Use a non-sensitive, saved test model on Windows.
2. Install and launch the separate PowerDesigner MCP server in read-only mode.
3. Configure the target agent following the **current official documentation** for that client; do not invent transport settings.
4. Confirm tool discovery lists 11 names.
5. Invoke `consultar_modelo_activo` and validate the returned file.
6. Perform a read-only collection listing and geometry inspection if appropriate.
7. Confirm permission prompts before mutation. For a real write test, separately authorize **only the test model**, preview, apply a reversible change after approval, verify and restore.
8. Record tool outputs, software version, error messages and any differences.

A skill by itself cannot complete any of these MCP access checks.

Evidence and scope: [ChatGPT and Claude Free validation — 2026-11-08](../../../docs/VALIDACION_AGENTES_2026-11-08.md).
