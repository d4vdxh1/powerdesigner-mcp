# Guía completa: de PowerDesigner a ChatGPT

## 1. Qué se crea y para qué sirve

No hay que desarrollar una API de OpenAI nueva. Se crean tres cosas distintas:

| Elemento | Dónde se crea | Para qué sirve |
|---|---|---|
| Servidor MCP | Esta carpeta en Windows | Publica herramientas que llaman a PowerDesigner mediante COM |
| Túnel y clave de API | OpenAI Platform | Permiten que el cliente local se autentique y transporte solicitudes |
| Complemento MCP | ChatGPT | Presenta las herramientas del servidor al chat |

El túnel no abre PowerDesigner ni ejecuta este servidor por sí solo. Deben estar funcionando PowerDesigner, el servidor y tunnel-client. VS Code es opcional: sirve para editar archivos.

## 2. Descargar el proyecto

En el repositorio, pulsá Code → Download ZIP y extraelo, por ejemplo en `C:\Users\TU_USUARIO\PowerDesignerMCP`. También podés usar Git:

```powershell
git clone https://github.com/d4vdxh1/powerdesigner-mcp.git
cd powerdesigner-mcp
```

Usá una carpeta normal con permisos de escritura. No copies la carpeta `.venv` de otra computadora: se genera nuevamente. Los ejemplos de PowerShell se ejecutan desde la raíz del proyecto.

## 3. Verificar Python e instalar dependencias

Abrí PowerShell y ejecutá:

```powershell
py -3.12 --version
```

La instalación original utilizó Python 3.12.10. Si el comando no existe, instalá Python 3.12 con su lanzador para Windows y reabrí PowerShell.

Para preparar todo:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\instalar.ps1
```

Equivale a crear un entorno con `py -3.12 -m venv .venv` e instalar `requirements.txt` con el Python de ese entorno. No hace falta activar `.venv` ni cambiar permanentemente la política de ejecución de Windows. Un aviso sobre una nueva versión de pip no implica que la instalación haya fallado.

## 4. Verificar PowerDesigner por COM

Abrí PowerDesigner y un modelo. Luego:

```powershell
.\.venv\Scripts\python.exe -c "import win32com.client; pd=win32com.client.Dispatch('PowerDesigner.Application'); print('Version:', pd.Version); m=pd.ActiveModel; print('Modelo:', m.Name if m is not None else 'Sin modelo activo')"
```

Debe mostrar la versión y el nombre del modelo que querés usar. Este paso consulta, no edita. La prueba de referencia funcionó con PowerDesigner 16.5.0.3982; otras versiones requieren comprobar su interfaz COM.

Si el modelo no coincide, revisá la instancia y el modelo activo en PowerDesigner. Si COM no conecta, resolvé ese problema antes de configurar ChatGPT.

## 5. Crear el túnel

1. Iniciá sesión en https://platform.openai.com/.
2. Abrí directamente https://platform.openai.com/settings/organization/tunnels si el menú no muestra Tunnels.
3. Comprobá que esté seleccionada la organización de Platform que vas a usar.
4. Pulsá Create tunnel y completá:
   - **Name:** PowerDesigner MCP.
   - **Description:** Conecta ChatGPT con PowerDesigner para consultar y editar modelos mediante las herramientas del servidor local.
   - **Organizations:** tu organización de Platform.
   - **ChatGPT workspaces:** el espacio de ChatGPT donde agregarás el complemento. A veces aparece como identificador en lugar de nombre.
   - **Restrict client network access:** en una instalación personal inicial puede permanecer desmarcado; en una organización respetá su política de redes.
5. Pulsá Create.
6. Copiá el ID completo que comienza por `tunnel_`. No copies la URL local en ese campo.

Crear o editar túneles requiere Tunnels Read + Manage. Ejecutarlos requiere Read + Use. El acceso a MCP personalizados en ChatGPT es independiente. Si falta acceso, revisá la organización y consultá con su propietario o administrador; no asumas que una suscripción de ChatGPT habilita automáticamente todos los permisos de Platform.

No es necesario crear otro túnel cada día.

## 6. Crear la clave de API

1. Abrí https://platform.openai.com/settings/organization/api-keys dentro de la misma organización.
2. Usá la opción para crear una nueva clave secreta de ejecución. Los nombres exactos de los controles pueden variar.
3. Poné un nombre identificable, por ejemplo `PowerDesigner MCP local`.
4. Seleccioná el proyecto y propietario que correspondan a tu cuenta.
5. Si el formulario permite restringir permisos, habilitá Tunnels Read + Use. El usuario o cuenta de servicio también debe tener autorización para el túnel; una clave no concede permisos que su propietario no tiene.
6. Copiá el secreto cuando se muestre y guardalo en un gestor de contraseñas. Si no podés recuperarlo después, generá una clave nueva y revocá la que ya no uses.

No uses una clave de administración para el cliente permanente. No pegues la clave en ChatGPT, GitHub, issues, capturas, README ni config.local.json. El ID `tunnel_…` no es la clave secreta.

Este proyecto no llama a modelos de la API ni configura facturación. El acceso, los límites y los posibles requisitos de la cuenta se consultan en Platform; esta guía no promete un servicio gratuito ni un acceso universal.

## 7. Descargar tunnel-client

Desde Platform seguí la descarga recomendada, o visitá https://github.com/openai/tunnel-client/releases/latest.

En Assets, elegí el paquete de Windows:

- Intel o AMD de 64 bits: `windows-amd64.zip`.
- Windows en procesador ARM: `windows-arm64.zip`.

`amd64` también corresponde a procesadores Intel x64. No elijas archivos de licencias, SBOM, código fuente, macOS o Linux como ejecutable de Windows. La instalación de referencia usó la versión v0.0.18; consultá la guía de la versión descargada si cambia el comportamiento.

Extraé el ZIP. Colocá `tunnel-client.exe` junto a `servidor.py`; conservá los acompañantes que la distribución requiera. No subas esos binarios al repositorio. Para comprobar que se puede ejecutar:

```powershell
.\tunnel-client.exe help quickstart
```

## 8. Completar la configuración local

El instalador crea `config.local.json`. Si no existe:

```powershell
Copy-Item config.example.json config.local.json
notepad config.local.json
```

Reemplazá el identificador del túnel y guardá un JSON válido. Por seguridad, las modificaciones están deshabilitadas inicialmente (`write_model` vacío):

```json
{
  "tunnel_id": "tunnel_TU_IDENTIFICADOR_COMPLETO",
  "write_model": ""
}
```

El iniciador conecta ese túnel a `http://127.0.0.1:8000/mcp`. No pegues esa URL en el campo ID del túnel de ChatGPT.

Para permitir modificaciones exclusivamente sobre **un modelo concreto**, escribí su ruta absoluta existente en `write_model`. En JSON las barras invertidas deben duplicarse, por ejemplo: `"write_model": "C:\\Modelos\\prueba.oom"`. Reiniciá el servidor para aplicar el cambio. El modelo original no queda autorizado solo por estar abierto en PowerDesigner.

## 9. Arranque normal con doble clic

1. Abrí PowerDesigner y guardá el modelo con Ctrl+S.
2. Hacé doble clic en `Iniciar-MCP.cmd`.
3. En el primer arranque, pegá la clave de API en el prompt oculto y presioná Enter. No ver caracteres mientras pegás es normal.
4. Se guarda `clave_tunel.xml` cifrado para el usuario de Windows. No es una clave portátil para distribuir entre equipos.
5. El servidor abre otra ventana. Buscá `Uvicorn running on http://127.0.0.1:8000`.
6. El cliente del túnel debe iniciar sin errores repetidos de autenticación. `tunnel-client started` indica que arrancó el proceso, no demuestra por sí solo que PowerDesigner responde.
7. Cuando el cliente use el puerto de salud predeterminado, abrí http://127.0.0.1:8080/ui para revisar su estado.

No ejecutes el iniciador varias veces: puede dejar clientes del túnel duplicados. **En esta rama el iniciador rechaza un puerto 8000 ya ocupado** y no reutiliza un proceso anterior. Primero cerrá el servidor previo. El chequeo del puerto no verifica la disponibilidad COM ni autentica solicitudes del puerto local.

Para crear un acceso de escritorio, hacé clic derecho sobre `Iniciar-MCP.cmd` → Mostrar más opciones → Enviar a → Escritorio (crear acceso directo), o creá un acceso directo desde el menú de Windows.

## 10. Registrar el complemento en ChatGPT

Con servidor y túnel activos:

1. Entrá en Complementos/Plugins y elegí agregar un servidor MCP personalizado.
2. Completá nombre y descripción.
3. En Conexión, seleccioná Túnel, elegí el existente o pegá el `tunnel_id` completo.
4. En autenticación, elegí Sin autenticación: este servidor no implementa OAuth. La clave que autentica tunnel-client con Platform sigue siendo necesaria.
5. Revisá el aviso de acceso y conectá el complemento.
6. Activá PowerDesigner MCP para el chat que lo utilizará.

Si no aparece el túnel, revisá su asociación con el espacio de ChatGPT y los permisos Read + Use. Si se alcanzó un límite de solicitudes, respetá el tiempo de reintento y verificá la salud del cliente antes de pulsar repetidamente Crear.

## 11. Prueba completa

Pedí primero:

> Consultá el modelo activo de PowerDesigner. Solo lectura.

El nombre debe coincidir con lo que tenés abierto. Luego:

> Listá UseCaseDiagrams del modelo activo y mostrame sus nombres. No modifiques nada.

Para un tipo de modelo distinto, la colección puede tener otro nombre. Poder consultar objetos no significa haber obtenido una imagen del diagrama. La comprobación visual requiere exportar una imagen o compartir una captura por separado; esta versión no incluye una herramienta de exportación gráfica.

Las rutas devueltas pueden usar ObjectID o un índice como `Symbols:@0`. No construyas rutas suponiendo que todos los símbolos tienen ObjectID, y volvé a listar después de cambios que alteren el orden.

## 12. Qué puede editar esta versión

El servidor publica **11 herramientas**: `consultar_modelo_activo`, `listar_coleccion`, `leer_propiedades`, `editar_propiedad`, `crear_objeto`, `mostrar_en_diagrama`, `guardar_modelo`, `inspeccionar_diagrama`, `mover_paquetes`, `enderezar_flechas` e `insertar_codo_flecha`.

Las funciones de geometría permiten consultar posiciones, mover **símbolos de paquetes**, enderezar dependencias y agregar un codo a una dependencia de dos puntos en **diagramas de clases**. No reordenan automáticamente todo el diagrama. La coordenadas son unidades internas de PowerDesigner y las operaciones de geometría previsualizan por defecto (`confirmar=False`): solo `confirmar=True` aplica cambios en memoria.

`editar_propiedad` admite únicamente Name, Code, Comment y Description. `crear_objeto` crea Actors o UseCases; `mostrar_en_diagrama` utiliza AttachObject. Las colecciones dependen del tipo de modelo. **No** se implementó edición de Expression, multiplicidades, tamaños, marcos opt ni ejecución arbitraria de Python.

**Seguridad:** el servidor es de solo lectura por defecto. Toda herramienta que escribe necesita `write_model` con la ruta absoluta del archivo activo autorizado; la autorización por ruta no reemplaza la autenticación ni la confianza en los clientes que usan el túnel. Revisá el nombre y la ruta antes de aplicar cambios.

Antes de la primera modificación de cada archivo durante un proceso, se respalda la versión guardada en disco. Si existen cambios sin guardar, la copia no los incluirá. Las ediciones quedan en memoria hasta ejecutar `guardar_modelo` o guardar manualmente. Hay intentos de restauración para algunas operaciones geométricas, pero **no hay rollback transaccional**: comprobá el diagrama y conservá el respaldo ante errores.

## 13. Uso posterior y apagado

Cada día: PowerDesigner con el modelo → doble clic en Iniciar-MCP.cmd → seleccionar el complemento en ChatGPT. No hay que recrear claves ni túneles.

Mantené Internet y evitá la suspensión. Para terminar, guardá los cambios que quieras conservar, presioná Ctrl+C en la ventana del túnel y en la del servidor, y cerralas.

Si editaste `servidor.py` o `write_model`, detené el proceso anterior antes de iniciar la nueva versión: el iniciador **no** reutiliza procesos que ya estén escuchando en 8000. Actualizá las herramientas del complemento si cambió su catálogo.

Si hay 401, revisá la clave y los permisos. Para reemplazar la clave almacenada, con el iniciador detenido:

```powershell
Remove-Item .\clave_tunel.xml
```

La próxima ejecución la pedirá de nuevo. Consultá SOLUCION_DE_PROBLEMAS.md para los otros errores.

## Fuentes

- OpenAI, Secure MCP Tunnel: https://developers.openai.com/api/docs/guides/secure-mcp-tunnels
- OpenAI, guía del cliente v0.0.18: https://github.com/openai/tunnel-client/blob/v0.0.18/docs/onboarding.md
- MCP Python SDK v1: https://py.sdk.modelcontextprotocol.io/v1/
- SAP/Sybase, OLE Automation en PowerDesigner 16.5: https://infocenter.sybase.com/help/topic/com.sybase.infocenter.dc38628.1653/doc/html/rad1232022697945.html
