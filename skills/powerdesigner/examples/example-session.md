# Example: inspect and adjust a dependency (illustrative only)

> This is a **fictional walkthrough**. The IDs and coordinates below are **placeholders**, not evidence of a real PowerDesigner run. Only use values actually returned by the connected MCP server.

## User request

"Inspect my class diagram and remove a bend from one dependency. Show me the change first."

## Agent sequence

1. **Identify.** Call `consultar_modelo_activo`; display the returned model name/path and confirm the target.
2. **Find diagram.** Use `listar_coleccion` on the correct model/package collection, then select the returned `ruta` for a class diagram.
3. **Inspect.** Call `inspeccionar_diagrama` and locate the actual dependency by returned `objeto_id`, endpoint names and `puntos_flecha`. If there are several matches, clarify.
4. **Preview.** Call `enderezar_flechas` with the real `ruta_diagrama`, one real dependency ID in `dependencias_ids`, and `confirmar=false`. Show `antes` and `despues` without claiming a change was applied.
5. **Get approval.** Ask "The preview changes this dependency from three points to two without changing its endpoints. Do you authorize that edit to this specific model?"
6. **Apply.** Only after explicit approval and existing write authorization, call `enderezar_flechas` with `confirmar=true`.
7. **Verify.** Call `inspeccionar_diagrama` again; compare observed points to the approved plan.
8. **Save separately.** Ask whether to save. Only then call `guardar_modelo`; explain backup and visual verification limitations.

## Failure handling

- `Edicion deshabilitada`: stop, explain missing file-specific authorization, never change permissions automatically.
- Invalid or missing ID: list/inspect again; never guess identifiers.
- Unexpected state after apply: stop and reinspect instead of blindly repeating writes.
- Tools missing: explain the requirement to connect a separate MCP server; loading the skill alone does not provide access.
