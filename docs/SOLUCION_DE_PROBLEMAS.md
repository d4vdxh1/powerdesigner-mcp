# Solución de problemas

## 401 Unauthorized en el cliente del túnel

La autenticación con Platform fue rechazada. Revisá la clave, que no esté revocada, su organización y sus permisos. Detené el iniciador y eliminá la copia local para que la solicite nuevamente:

```powershell
Remove-Item .\clave_tunel.xml
```

Volvé a ejecutar `Iniciar-MCP.cmd` y pegá la clave válida en el prompt oculto. No la pegues en chats ni issues. No hace falta recrear el túnel por este error.

## Session terminated

Este servidor usa `stateless_http=True`. Detené el proceso anterior y reiniciá; después reconectá el complemento si mantiene una sesión vieja. Si sigue fallando, conservá los mensajes del servidor y del túnel sin secretos para diagnosticar la capa afectada. No es necesario actualizar las herramientas en cada encendido normal.

## Puerto 8000 ocupado

El iniciador no identifica el proceso que ocupa ese puerto. Comprobalo con:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

Identificá el proceso antes de cerrarlo. No termines procesos desconocidos. Si el proceso es un servidor anterior, detenelo con Ctrl+C y reiniciá.

## ObjectID en Symbols

Esta entrega admite rutas por índice cuando ObjectID no existe. Listá la colección nuevamente y utilizá la ruta devuelta. Los índices cambian al alterar la colección; no reutilices rutas viejas después de crear o eliminar símbolos.

## OAuth no encontrado / 404 en well-known

Este servidor no implementa OAuth. La configuración del complemento debe ser Sin autenticación mientras se conecta mediante el túnel autorizado. Una consulta a un endpoint OAuth inexistente puede producir 404; no implica por sí sola que las herramientas fallen.

## 400 o 406 al abrir /mcp en el navegador

No es una página web: requiere solicitudes MCP y encabezados concretos. Una prueba desde el navegador no valida el protocolo. Comprobá el cliente con `http://127.0.0.1:8080/ui` cuando use su puerto de salud predeterminado y hacé una consulta real desde ChatGPT.

## No hay modelo activo / no se puede respaldar

Abrí el modelo en la misma sesión de Windows y guardalo con Ctrl+S. El servidor requiere un archivo existente antes de editar. Conservá una copia manual adicional si hay cambios importantes.

## La herramienta no permite Expression, multiplicidades o posiciones

Es una limitación de esta versión, no un permiso de ChatGPT. El archivo aportado usa una lista explícita de propiedades editables. Esas operaciones requieren ampliar el servidor y comprobar el metamodelo concreto; no basta con modificar la descripción del complemento.

## La clave cifrada no abre en otra computadora

No copies `clave_tunel.xml`. Generá la configuración y guardá una clave válida desde el usuario de Windows que ejecutará el iniciador.
