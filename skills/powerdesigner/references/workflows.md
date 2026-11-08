# Operational workflows

Use the schemas provided by the active MCP client. **Never invent object IDs, diagram paths, coordinates or available collections.**

## Inspect a model — read only

1. Call `consultar_modelo_activo()` to identify the open file.
2. Call `listar_coleccion(coleccion="Packages")` or another collection supported by that model.
3. Use the returned `ruta` arrays to navigate objects. Use `leer_propiedades` to read supported scalar properties.
4. Report concrete findings and limitations. Do not edit.

## Inspect a class diagram — read only

1. Locate the target class diagram, including nested packages when needed, via `listar_coleccion`.
2. Call `inspeccionar_diagrama` with the exact returned `ruta_diagrama`.
3. Record symbol IDs, package coordinates and sizes, and dependency IDs and points.
4. Distinguish identically named elements using actual returned IDs.

## Move a package symbol

1. Inspect the diagram to obtain the exact package symbol ID and current x/y values.
2. Agree on new coordinates in **PowerDesigner internal units**, not screen pixels.
3. Preview: `mover_paquetes(ruta_diagrama=..., movimientos=[{"objeto_id":"<returned ID>","x":10000,"y":20000}])`. The numbers here are **illustrative placeholders**; replace them with user-approved coordinates.
4. Show the preview and request user approval.
5. Reissue the same call with `confirmar=True`, only if approved and write authorization is configured.
6. Reinspect and compare, then save only with separate approval.

## Straighten a dependency

1. Inspect to obtain the exact dependency ID and all its points.
2. Preview with `enderezar_flechas(ruta_diagrama=..., dependencias_ids=["<returned ID>"])`.
3. Clarify that intermediate points will be removed; semantic endpoints do not change.
4. After explicit approval, call with `confirmar=True`.
5. Reinspect; save only if approved.

## Insert a bend

1. Confirm the dependency has exactly two points.
2. Choose an intermediate x/y in PowerDesigner internal units, grounded in actual diagram inspection.
3. Preview with `insertar_codo_flecha(ruta_diagrama=..., dependencia_id="<returned ID>", x=10000, y=20000)`. Coordinates are placeholders.
4. Request approval; apply with `confirmar=True`.
5. Reinspect points; save if approved.

If a dependency has more than two points, do not attempt this tool directly; a separately approved straighten operation may be required.

## Create or attach a use case / actor

1. Discover the appropriate supported parent collection and route.
2. Get approval for a specific object name and code.
3. Call `crear_objeto` on `Actors` or `UseCases` with the intended `nombre`, `codigo` and `ruta_padre`.
4. Creating an object does not display it on a diagram. Use `mostrar_en_diagrama` only when explicitly requested and after identifying both routes.
5. Read back and save only with user approval.

## Errors and recovery

- `Edicion deshabilitada`: server-side write authorization blocked the operation; never circumvent it.
- Invalid `@index` routes: list again after objects/symbols change because indices may shift.
- COM errors or partial changes: reinspect state before recovery, warn about absence of transaction rollback.
- Backup copies the prior **saved file**, not unsaved memory. For significant edits recommend an independent backup and visual confirmation in PowerDesigner.
