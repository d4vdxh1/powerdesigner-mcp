# PowerDesigner MCP — Agensi publication readiness

**Current status:** skill candidate, **not published** and **not a plug-and-play integration**.

## Product boundary

The deliverable is a **skill document package**. It guides an agent using the **independently installed PowerDesigner MCP server**. Installing this ZIP does not install licensed PowerDesigner, start a Windows service, establish a tunnel, grant agent tools, or authorize editing.

## Packaging scope

Inside the ZIP root:
- `SKILL.md` (frontmatter and agent instructions).
- `references/setup.md`, `references/workflows.md` and `references/compatibility.md`.
- `examples/example-session.md` — **fictional example**, not a live demo.

Do not bundle the repository root, Python environment, proprietary executables, private model files, API keys or encrypted credentials.

## Requirements for marketplace "Needs access to"

- Windows with a separately licensed and opened PowerDesigner instance (version 16.5.0.3982 tested only).
- Python 3.12 PowerDesigner MCP server from https://github.com/d4vdxh1/powerdesigner-mcp, installed and running separately.
- A compatible MCP client connected to the Windows server. A service at localhost is accessible only within the same machine/network namespace, unless the user configures an authorized transport.
- **OpenAI Secure MCP Tunnel is specific to the documented ChatGPT workflow**, not a requirement of all agents.
- Write authorization for a specific model remains intentionally disabled until separately configured.

## Suggested marketplace listing (draft, subject to current uploader requirements)

- **Title:** PowerDesigner MCP — Safe UML Model Assistant
- **Summary:** Inspect PowerDesigner models and guide controlled edits to use cases, package positions and dependency routing via a separately connected MCP server.
- **Audience:** UML modelers, systems analysts, software architects and PowerDesigner users.
- **Tags (suggested):** UML, MCP, Windows, PowerDesigner, Modeling.
- **Contents:** Instruction skill plus setup, workflows, compatibility matrix, and fictional example.
- **Limitations:** licensed Windows PowerDesigner required; user must install and connect MCP server; geometry editing limited to class diagrams; no server-side OAuth; no transactional rollback; client compatibility unverified.
- **Needs access to:** the user's local PowerDesigner MCP server; no hosted credentials supplied.
- **Price:** undecided; no commercial product tier has been defined.

## Release gates

- [x] Existing server implements 11 tools and default-deny editing, tested on a model copy.
- [x] Skill has explicit usage triggers, confirmation rules, workflows, requirements, and limitations.
- [ ] Validate Agensi's current accepted ZIP layout, optional frontmatter fields, listing and account rules using the actual submission UI.
- [ ] Select and verify licenses for the skill documents and the server source before redistribution or sale. Public source alone **does not grant an open-source license**.
- [ ] Validate the skill with **at least one real connected agent client** and capture actual tool calls, permission prompts and failures.
- [ ] Validate clean server installation on another Windows device or state clearly that this has not been done.
- [ ] Create and inspect a clean ZIP, rooted at `SKILL.md`, with no secrets or proprietary contents.
- [ ] Produce a **genuine** test-model demonstration (screenshots/video/logs), not only the fictional example.
- [ ] Confirm Agensi account/review/pricing/disclosures and marketplace policies.
- [ ] Obtain the author's explicit approval before submitting any public marketplace listing.

## Example ZIP command (PowerShell, only after approvals)

~~~powershell
Compress-Archive -Path .\skills\powerdesigner\* -DestinationPath .\powerdesigner-skill.zip -Force
~~~

Inspect the archive structure before submission. The ZIP should begin with `SKILL.md`, `references/` and `examples/`, never the entire repository.

**Release decision:** suitable as a development candidate; **not ready to publish publicly** until the unchecked gates are addressed.

## Empaquetado reproducible automatizado

El repositorio incluye una comprobación independiente de la integración de PowerDesigner:

~~~powershell
py -3.12 scripts/pack_skill.py --check
py -3.12 scripts/pack_skill.py
~~~

El validador verifica nombre y descripción del frontmatter, las once herramientas documentadas, referencias relativas, codificación UTF-8, tamaño y una lista cerrada de cinco archivos Markdown. Rechaza archivos inesperados, enlaces locales rotos y patrones evidentes de credenciales.

GitHub Actions ejecuta la validación y publica el ZIP como **artefacto de CI** en el workflow `Verificar y empaquetar skill Agensi`. Un artefacto CI **no es** una publicación en Agensi ni una validación en un cliente agente real.

**Estado:** el ZIP generado es candidato de distribución, sujeto a las verificaciones de licencias, cliente, demostración y revisión de la propia plataforma. No subir al marketplace sin aprobación específica.
