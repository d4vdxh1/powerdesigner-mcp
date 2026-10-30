# Publicar el proyecto

Nombre sugerido: `powerdesigner-mcp`. Descripción: «Conexión local entre PowerDesigner y ChatGPT mediante MCP, COM y Secure MCP Tunnel. Guía en español e iniciador para Windows».

## Crear el repositorio

Desde https://github.com/new, seleccioná tu cuenta y creá un repositorio vacío con ese nombre. Elegí la visibilidad deseada. Si vas a subirlo por Git, no lo inicialices con README, .gitignore ni licencia: esos archivos se gestionan desde el proyecto.

## Subir con Git

Extraé este proyecto en una carpeta nueva, distinta de la instalación que contiene claves y modelos. Abrí PowerShell allí:

```powershell
git init -b main
git add README.md requirements.txt servidor.py iniciar_mcp.ps1 instalar.ps1 Iniciar-MCP.cmd config.example.json .gitignore docs
git status --short
git diff --cached --stat
git commit -m "Documentar conexion de PowerDesigner con ChatGPT mediante MCP"
git remote add origin https://github.com/TU_USUARIO/powerdesigner-mcp.git
git push -u origin main
```

Reemplazá TU_USUARIO por tu cuenta. Revisá la lista antes del commit; no debe contener claves, modelos, binarios ni `.venv`. Si Git solicita identidad, configurá tu nombre y el correo que usás para commits (puede ser el noreply de GitHub). Autenticate mediante el método admitido por tu instalación de Git.

También podés pasar el enlace del repositorio ya creado a ChatGPT para que cargue los archivos mediante la conexión de GitHub, si el repositorio está incluido en los permisos de esa conexión.

## Subir desde la web

Usá Add file → Upload files y cargá los archivos extraídos, no el ZIP. Verificá que `.gitignore` también se incluya. El filtro de Git no se aplica a cargas manuales: nunca arrastres la carpeta de instalación original.

## Licencia

Elegí una licencia propia antes de presentar el proyecto como software de libre redistribución. No copies la licencia de tunnel-client como si licenciara automáticamente este código. Los ejecutables de terceros se obtienen desde sus fuentes oficiales.
