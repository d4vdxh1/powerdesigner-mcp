# Setup and distribution boundaries

This is a **skill-only package**, requiring a separately installed [PowerDesigner MCP server](https://github.com/d4vdxh1/powerdesigner-mcp).

## Prerequisites

- Windows and licensed SAP/Sybase PowerDesigner accessible via COM.
- Python 3.12, PowerShell, an open saved PowerDesigner model.
- A working MCP client connected to the separately installed server.

The project was verified on Windows 11 with PowerDesigner 16.5.0.3982; other versions and clean installations are **untested**.

## Server installation

Follow the [repository installation guide](https://github.com/d4vdxh1/powerdesigner-mcp/blob/main/docs/GUIA_PASO_A_PASO.md). From PowerShell:

~~~powershell
git clone https://github.com/d4vdxh1/powerdesigner-mcp.git
cd powerdesigner-mcp
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\instalar.ps1
~~~

With PowerDesigner open, start the **local server only** using:

~~~powershell
.\.venv\Scripts\python.exe servidor.py
~~~

It listens at `http://127.0.0.1:8000/mcp` via streamable HTTP and defaults to read-only.

## Connecting clients

- **ChatGPT:** the documented connection uses OpenAI Secure MCP Tunnel. Follow the repository guide to configure `config.local.json` and the separate official `tunnel-client.exe`.
- **Claude Code, Cursor, Codex:** the project has not verified the precise MCP setup and transport for these clients. Check the client's current documentation and test read-only before any write; do not claim prevalidated support.
- Installing this skill **does not** install the MCP server, establish a tunnel, or authenticate a client. The server must actually expose the tools.

## Allowing writes

The Windows tunnel launcher reads an optional single-file authorization:

~~~json
{
  "tunnel_id": "tunnel_YOUR_IDENTIFIER",
  "write_model": ""
}
~~~

An empty `write_model` keeps **all writes blocked**. Only the user can explicitly choose an **existing absolute model path** and restart the launcher. Direct server launches use `POWERDESIGNER_MCP_WRITE_MODEL` for authorization; do not set it automatically.

Localhost is not client authentication. Never bind the server to public interfaces without a proper security design.

## Distribution and validation

- The marketplace ZIP should contain the `SKILL.md` and `references/` documents only.
- Never include keys, `clave_tunel.xml`, `config.local.json`, models, backups, PowerDesigner executables or third-party tunnel binaries.
- The current skill is an **instruction package**, not a standalone application. Its actual capabilities depend on the user's installed software and active MCP connection.
- The repo has no chosen source-code license yet. Resolve licensing and third-party redistribution conditions before any commercial release.

For tested/untested status see [compatibility](compatibility.md). For the independent publication checklist see [Agensi readiness](https://github.com/d4vdxh1/powerdesigner-mcp/blob/main/docs/AGENSI_PUBLICACION.md).
- Refer to [troubleshooting](https://github.com/d4vdxh1/powerdesigner-mcp/blob/main/docs/SOLUCION_DE_PROBLEMAS.md).
