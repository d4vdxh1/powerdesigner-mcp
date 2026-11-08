# Validación de PowerDesigner MCP con agentes — 08/11/2026

**Alcance:** pruebas de lectura del servidor en ChatGPT y pruebas de importación/comprensión de la skill en Claude Free. Ninguna prueba publicada aquí habilita comercialización o demuestra compatibilidad completa con terceros.

## Matriz de evidencias

| Prueba | Resultado | Fuente y límite |
| --- | --- | --- |
| ChatGPT → Secure MCP Tunnel → servidor MCP → PowerDesigner | **Aprobada en lectura** | Dos invocaciones reales observadas en esta conversación |
| `consultar_modelo_activo` | **Aprobada** | Retornó identidad, archivo y PowerDesigner 16.5.0.3982 |
| `listar_coleccion("Packages")` | **Aprobada** | Retornó siete paquetes con rutas reales |
| Importación de ZIP skill v0.2.0 en Claude Free | **Aprobada según captura del usuario** | Cinco archivos visibles y skill activada |
| Claude Free: interpretación de las 11 herramientas | **Aprobada según respuesta aportada** | Distingue 4 herramientas de lectura y 7 mutadoras |
| Claude Free: rechazo de consulta sin herramientas MCP | **Aprobada según respuesta aportada** | No inventó resultados y describió el requisito ausente |
| Claude Free → PowerDesigner MCP | **No probada** | La sesión de Claude no tenía las herramientas conectadas |
| Claude Code, Cursor, Codex | **No probados** | Compatibilidad real pendiente |
| Escrituras desde Claude / prueba en otro Windows | **No probadas** | No se modificó ningún modelo en estas pruebas |

## A. Conexión real desde ChatGPT (08/11/2026)

Se inició el servidor local y el cliente del túnel. El primer intento de consulta de ChatGPT falló con `McpServerError: Session terminated`; la ventana de consola del usuario mostró tráfico MCP y el cliente del túnel iniciado. En el siguiente intento de la misma sesión, la llamada real `consultar_modelo_activo()` devolvió nombre/archivo del modelo activo y versión de PowerDesigner 16.5.0.3982; `listar_coleccion(coleccion="Packages")` devolvió siete objetos con rutas.

**Datos omitidos intencionalmente:** nombre del modelo, nombres de paquetes, rutas locales e identificadores de objetos. Se preserva privacidad porque el modelo empleado no era una demostración sintética destinada a publicación.

**Resultado:** conectividad de extremo a extremo comprobada para **dos herramientas de lectura**. No se invocaron mutaciones ni guardado. Las pruebas antiguas del registro de 11 herramientas y operaciones geométricas sobre un modelo de prueba son evidencias distintas, no parte de esta sesión.

## B. Importación de skill en Claude Free (08/11/2026)

El usuario descargó el artefacto ZIP generado por GitHub Actions y lo subió a Claude. Su captura mostró skill `powerdesigner-mcp` activada, versión `0.2.0`, carga finalizada y cinco archivos: `SKILL.md`, `examples/example-session.md`, `references/workflows.md`, `references/setup.md` y `references/compatibility.md`.

**Resultado:** importación de la skill reportada y visualizada; no equivale a que Claude tenga herramientas MCP conectadas.

## C. Interpretación de la skill por Claude Free

Prompt del usuario: explicar las herramientas, lectura/escritura y verificaciones antes de editar, sin ejecutar ni cambiar archivos.

Respuesta aportada: enumeró las 11 herramientas (4 de lectura, 7 mutadoras), explicó validación del modelo activo, `write_model`, previsualización `confirmar=False`, confirmación explícita, validación posterior, guardado separado, privacidad y límites de geometría.

**Resultado:** comprensión correcta de las instrucciones para ese caso. No es una prueba de resistencia a todas las instrucciones adversarias ni una prueba real de ejecución MCP.

## D. Claude Free sin conector MCP

Prompt del usuario: consultar el modelo y paquetes, pero no inventar resultados si no existían herramientas conectadas.

Respuesta aportada: Claude declaró que no disponía de `consultar_modelo_activo` ni `listar_coleccion`, se negó a fingir la consulta y explicó que la skill no instala ni conecta el servidor por sí misma.

**Resultado:** comportamiento correcto cuando faltan las herramientas en su sesión. No demuestra que el servidor Windows estuviera apagado; únicamente que Claude no tenía acceso a ese MCP.

## Repetibilidad y próximos pasos

- Pruebas de ChatGPT: observadas en sesión con herramientas MCP reales; resultados redactados sin datos de modelos privados.
- Pruebas de Claude: basadas en capturas y transcripciones aportadas por el usuario; no se obtuvieron logs de herramientas Claude.
- Para ampliar evidencias: usar un **modelo sintético** guardado en PowerDesigner, cliente MCP conectado y **modo solo lectura**; observar descubrimiento de herramientas, consulta del modelo y una colección. Para mutaciones, requerir autorización separada, vista previa y respaldo.
- No afirmar soporte verificado para Claude MCP, Claude Code, Cursor o Codex hasta que se conecten y se realice la prueba real.
- No publicar una ficha comercial en Agensi antes de resolver licencia, dependencias externas y demostración con modelo no sensible.

Ver también [matriz de compatibilidad](../skills/powerdesigner/references/compatibility.md) y [checklist de publicación](AGENSI_PUBLICACION.md).
