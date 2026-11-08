$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

try {
    # Validar requisitos antes de solicitar credenciales o iniciar procesos.
    # Leer configuracion antes de iniciar el servidor: modo solo lectura por defecto.
    $archivoConfig = Join-Path $PSScriptRoot "config.local.json"
    if (-not (Test-Path $archivoConfig)) {
        throw "Copia config.example.json a config.local.json y completa tu tunnel_id."
    }
    $config = Get-Content $archivoConfig -Raw | ConvertFrom-Json
    $modeloEscritura = ""
    if ($null -ne $config.write_model) {
        $modeloEscritura = [string]$config.write_model
    }
    if ($modeloEscritura.Trim() -ne "") {
        if (-not [System.IO.Path]::IsPathRooted($modeloEscritura)) {
            throw "write_model debe ser una ruta absoluta."
        }
        if (-not (Test-Path -LiteralPath $modeloEscritura -PathType Leaf)) {
            throw "write_model no existe: $modeloEscritura"
        }
    }

    if ($config.tunnel_id -notmatch '^tunnel_[a-z0-9_]+$' -or $config.tunnel_id -eq 'tunnel_REEMPLAZAR') {
        throw "Configura un tunnel_id valido en config.local.json."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot "tunnel-client.exe") -PathType Leaf)) {
        throw "Descarga y extrae tunnel-client.exe en esta carpeta. Consulta README.md."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot ".venv\Scripts\python.exe") -PathType Leaf)) {
        throw "Falta el entorno Python. Ejecuta instalar.ps1 antes de iniciar."
    }

    # Inicia el servidor en otra ventana si el puerto esta libre.
    $servidorActivo = Get-NetTCPConnection `
        -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue

    if ($servidorActivo) {
        throw "El puerto 8000 ya esta ocupado. Detene la instancia anterior antes de iniciar este servidor protegido."
    }
    $archivoClave = Join-Path $PSScriptRoot "clave_tunel.xml"
    if (-not (Test-Path -LiteralPath $archivoClave -PathType Leaf)) {
        $clave = Read-Host "Pega tu clave de API de OpenAI" -AsSecureString
        $clave | Export-Clixml -Path $archivoClave
    }

    if (-not $servidorActivo) {
        # El proceso hijo hereda solo la ruta autorizada; no hereda claves API.
        $anterior = [Environment]::GetEnvironmentVariable("POWERDESIGNER_MCP_WRITE_MODEL", "Process")
        try {
            [Environment]::SetEnvironmentVariable("POWERDESIGNER_MCP_WRITE_MODEL", $modeloEscritura, "Process")
            Start-Process powershell.exe `
                -WorkingDirectory $PSScriptRoot `
                -ArgumentList @(
                    "-NoProfile",
                    "-NoExit",
                    "-Command",
                    "& '.\.venv\Scripts\python.exe' 'servidor.py'"
                )
        }
        finally {
            [Environment]::SetEnvironmentVariable("POWERDESIGNER_MCP_WRITE_MODEL", $anterior, "Process")
        }
        Start-Sleep -Seconds 3
    }

    $clave = Import-Clixml -Path $archivoClave
    $env:CONTROL_PLANE_API_KEY = (
        [System.Net.NetworkCredential]::new("", $clave)
    ).Password

    $env:CONTROL_PLANE_TUNNEL_ID = $config.tunnel_id
    $env:MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"

    & ".\tunnel-client.exe" run
    if ($LASTEXITCODE -ne 0) {
        throw "El cliente del tunel termino con codigo $LASTEXITCODE."
    }
}
catch {
    Write-Host "`nNo se pudo iniciar: $_" -ForegroundColor Red
}
finally {
    Remove-Item Env:CONTROL_PLANE_API_KEY -ErrorAction SilentlyContinue
    Read-Host "`nEl tunel se detuvo. Presiona Enter para cerrar"
}
