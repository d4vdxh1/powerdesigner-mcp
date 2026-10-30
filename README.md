# PowerDesigner MCP para ChatGPT

Servidor MCP local que conecta PowerDesigner en Windows con ChatGPT mediante COM y Secure MCP Tunnel. Proyecto personal basado en una instalación de Sybase PowerDesigner 16.5.0.3982 y Python 3.12.10; no es un producto oficial de SAP ni de OpenAI.

**Empezá por la [guía completa paso a paso](docs/GUIA_PASO_A_PASO.md): instalación, creación de la clave de API y del túnel, conexión con ChatGPT, ejecución y resolución de errores.**

## Arquitectura

ChatGPT → Secure MCP Tunnel → tunnel-client en Windows → servidor MCP en `127.0.0.1:8000/mcp` → PowerDesigner mediante COM.

La computadora debe permanecer encendida, conectada a Internet y sin suspender mientras se utiliza el complemento.

## Qué contiene esta versión

Se tomó como base el `servidor.py` del comprimido entregado por el autor, no la versión de ejecución general de Python propuesta en la conversación.

| Herramienta | Función |
|---|---|
| `consultar_modelo_activo` | Consultar versión, nombre y archivo del modelo activo |
| `listar_coleccion` | Enumerar objetos y obtener sus rutas |
| `leer_propiedades` | Leer propiedades y extremos de relaciones |
| `editar_propiedad` | Cambiar únicamente Name, Code, Comment y Description |
| `crear_objeto` | Crear actores o casos de uso |
| `mostrar_en_diagrama` | Representar un objeto existente en un diagrama |
| `guardar_modelo` | Ejecutar Save sobre el modelo activo |

No incorpora `ejecutar_python_powerdesigner`, edición de multiplicidades, expresiones de decisiones ni posicionamiento de símbolos. No afirmar esas capacidades al usar esta versión.

Se añadió HTTP sin estado para evitar depender de sesiones conservadas entre reinicios. Las rutas de símbolos sin `ObjectID` usan índices de enumeración `@0`, `@1`, etc.; después de agregar o eliminar objetos hay que volver a listar la colección. Estas correcciones se verificaron con objetos simulados, no en una instalación real de PowerDesigner.

## Requisitos

- Windows con PowerShell y PowerDesigner instalado y registrado para COM.
- Python 3.12 con el comando `py` disponible.
- Una cuenta y un espacio de ChatGPT que permitan agregar MCP personalizados.
- Acceso a túneles en OpenAI Platform. Crear un túnel requiere Tunnels Read + Manage; ejecutarlo requiere Read + Use.
- Una clave de API de ejecución válida de la organización correspondiente y el identificador del túnel.
- Cliente oficial `tunnel-client` para Windows. La prueba original utilizó v0.0.18.

## 1. Instalar

Descargá o cloná el repositorio y abrí PowerShell en su carpeta:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\instalar.ps1
```

El instalador crea `.venv`, instala dependencias y genera `config.local.json` si no existe. No modifica PowerDesigner.

## 2. Probar COM

Abrí PowerDesigner con un modelo y ejecutá:

```powershell
.\.venv\Scripts\python.exe -c "import win32com.client; pd=win32com.client.Dispatch('PowerDesigner.Application'); print(pd.Version); m=pd.ActiveModel; print(m.Name if m is not None else 'Sin modelo activo')"
```

Si falla, resolvé primero el registro COM, la instalación o los permisos de la aplicación. Ejecutá PowerDesigner y el servidor con el mismo usuario y nivel de privilegios.

## 3. Crear el túnel y descargar su cliente

1. Abrí [Túneles de OpenAI Platform](https://platform.openai.com/settings/organization/tunnels).
2. Creá un túnel con nombre y descripción. Asociá la organización y el espacio de ChatGPT que lo usará.
3. Copiá el identificador completo `tunnel_…`.
4. Descargá el cliente desde Platform o las [releases oficiales](https://github.com/openai/tunnel-client/releases/latest). Para Windows Intel/AMD x64 elegí el ZIP `windows-amd64`; para Windows ARM, `windows-arm64`.
5. Extraé el paquete conservando los archivos acompañantes en una carpeta temporal y colocá `tunnel-client.exe` y cualquier archivo de ejecución requerido por esa distribución junto a `servidor.py`. Este repositorio no redistribuye esos binarios.
6. En [API keys de Platform](https://platform.openai.com/settings/organization/api-keys), generá una clave de ejecución con permisos para usar el túnel; no uses una clave de administración en el iniciador.

Abrí `config.local.json` y reemplazá el valor de ejemplo:

```json
{
  "tunnel_id": "tunnel_TU_IDENTIFICADOR_COMPLETO"
}
```

La clave secreta no se escribe en este JSON.

## 4. Iniciar con doble clic

1. Abrí y guardá el modelo en PowerDesigner con Ctrl+S.
2. Hacé doble clic en `Iniciar-MCP.cmd`. Podés crear un acceso directo en el escritorio.
3. La primera vez ingresá la clave de API cuando se solicite. PowerShell la guarda como SecureString cifrado para el usuario de Windows en `clave_tunel.xml`.
4. Dejá abiertas las ventanas del servidor y del cliente del túnel.

El iniciador reutiliza un proceso que esté escuchando en el puerto 8000; no verifica que sea este servidor. Si modificaste `servidor.py`, detené la ventana del servidor anterior antes de volver a iniciar. No abras varios clientes del mismo túnel.

## 5. Conectar ChatGPT

Con el túnel ejecutándose, agregá un servidor MCP personalizado desde Complementos/Plugins. Usá el nombre PowerDesigner MCP, seleccioná **Túnel** y pegá su identificador. Este servidor no implementa OAuth: elegí **Sin autenticación** en ese formulario. Eso no elimina la autenticación del cliente del túnel con Platform.

Conectá el complemento y probá: «Consultá el modelo activo de PowerDesigner». Después: «Listá la colección UseCaseDiagrams del modelo activo». El tipo de modelo determina qué colecciones existen.

Si cambian las herramientas del servidor, actualizalas desde ChatGPT o reconectá el complemento. No es un paso de uso diario obligatorio.

## Uso diario y guardado

Abrí PowerDesigner con el modelo y hacé doble clic en `Iniciar-MCP.cmd`. Al terminar, guardá lo que corresponda y presioná Ctrl+C en las dos ventanas.

Antes de la primera modificación de cada archivo durante una ejecución, el servidor copia la versión del archivo guardada en disco a un nombre con `_respaldo_` y fecha. No captura cambios previos que estén solamente en memoria. No hay rollback automático; una operación puede dejar cambios parciales. Las ediciones no se guardan hasta usar `guardar_modelo` o guardar manualmente.

## Seguridad y distribución

No subas tu carpeta de instalación completa. Excluí `clave_tunel.xml`, `config.local.json`, `.venv`, binarios, modelos, respaldos y registros. `.gitignore` ayuda para Git, pero no filtra archivos al cargarlos manualmente por la web. El servidor queda ligado a loopback; no lo expongas sin protección en la red.

Las claves cifradas no deben compartirse. Cada persona debe crear su configuración y sus credenciales. El proyecto se entrega sin licencia de redistribución propia elegida; los componentes de terceros conservan sus licencias originales y se descargan por separado.

## Problemas comunes

Consultá [docs/SOLUCION_DE_PROBLEMAS.md](docs/SOLUCION_DE_PROBLEMAS.md) y [docs/PUBLICAR_EN_GITHUB.md](docs/PUBLICAR_EN_GITHUB.md).

## Referencias oficiales

- [Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).
- [Cliente del túnel: guía v0.0.18](https://github.com/openai/tunnel-client/blob/v0.0.18/docs/onboarding.md).
- [MCP Python SDK v1](https://py.sdk.modelcontextprotocol.io/v1/).
- [PowerDesigner 16.5: OLE Automation](https://infocenter.sybase.com/help/topic/com.sybase.infocenter.dc38628.1653/doc/html/rad1232022697945.html).

## Validación de esta entrega

Compilación sintáctica de Python y pruebas simuladas de rutas con ObjectID y símbolos sin ObjectID. No se ejecutaron PowerShell, COM, PowerDesigner ni la conexión real desde este entorno Linux. Las dependencias usan un rango de versiones, no un lockfile reproducible.
