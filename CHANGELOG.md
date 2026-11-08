# Cambios

## Licencia MIT para el proyecto público — 2026-11-08

- Licencia MIT añadida al código y documentación propios del repositorio. El ZIP incorpora una copia de `LICENSE` para preservar los avisos legales.
- No se alteran las licencias de terceros ni los requisitos de uso de SAP PowerDesigner. No se publica ni implementa ninguna funcionalidad PRO.

## Documentación y skill de preparación para Agensi — 2026-11-08

- Fusionado PR #1 con las 11 herramientas y protección de escritura por modelo autorizado.
- README profesional integrado por PR #2.
- Skill preliminar integrada por PR #3 bajo `skills/powerdesigner/`.
- PR #4 integrado: auditoría de seguridad documental, ejemplos, matriz de compatibilidad y checklist de publicación.
- PR #5 integrado: empaquetado ZIP de la skill y validación automatizada en GitHub Actions.
- 08/11/2026: conexión MCP real de solo lectura desde ChatGPT (dos herramientas), importación del ZIP v0.2.0 en Claude Free y evaluación de instrucciones sin conector MCP; ver [evidencias](docs/VALIDACION_AGENTES_2026-11-08.md). No hay release público en Agensi.


## Preparación para repositorio — 2026-10-30

- Base: servidor limitado e iniciador incluidos en el archivo aportado por el autor.
- Configuración del túnel separada en config.local.json, excluida de Git.
- Credenciales cifradas, dependencias, ejecutables y modelos excluidos de la distribución.
- Instalador de dependencias y lanzador CMD portátil.
- Servidor HTTP sin estado; lectura de símbolos sin ObjectID mediante índice.
- Guía de conexión, uso diario, errores y publicación.
- No incorpora la herramienta de ejecución arbitraria de Python propuesta anteriormente.
