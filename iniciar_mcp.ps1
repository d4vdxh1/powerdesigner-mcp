$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

try {
    $archivoClave = Join-Path $PSScriptRoot "clave_tunel.xml"

    if (-not (Test-Path $archivoClave)) {
        $clave = Read-Host "Pega tu clave de API de OpenAI" -AsSecureString
        $clave | Export-Clixml -Path $archivoClave
    }

    # Inicia el servidor en otra ventana si el puerto esta libre.
    $servidorActivo = Get-NetTCPConnection `
        -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue

    if (-not $servidorActivo) {
        Start-Process powershell.exe `
            -WorkingDirectory $PSScriptRoot `
            -ArgumentList @(
                "-NoProfile",
                "-NoExit",
                "-Command",
                "& '.\.venv\Scripts\python.exe' 'servidor.py'"
            )
        Start-Sleep -Seconds 3
    }

    $clave = Import-Clixml -Path $archivoClave
    $env:CONTROL_PLANE_API_KEY = (
        [System.Net.NetworkCredential]::new("", $clave)
    ).Password

    $archivoConfig = Join-Path $PSScriptRoot "config.local.json"
    if (-not (Test-Path $archivoConfig)) {
        throw "Copia config.example.json a config.local.json y completa tu tunnel_id."
    }
    $config = Get-Content $archivoConfig -Raw | ConvertFrom-Json
    if ($config.tunnel_id -notmatch '^tunnel_[a-z0-9_]+$' -or $config.tunnel_id -eq 'tunnel_REEMPLAZAR') {
        throw "Configura un tunnel_id valido en config.local.json."
    }
    $env:CONTROL_PLANE_TUNNEL_ID = $config.tunnel_id
    $env:MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"

    if (-not (Test-Path ".\tunnel-client.exe")) {
        throw "Descarga y extrae tunnel-client.exe en esta carpeta. Consulta README.md."
    }
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
