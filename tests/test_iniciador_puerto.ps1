# Prueba aislada del iniciador ante el puerto 8000 ocupado.
# No inicia el servidor, no ejecuta tunnel-client y no requiere una API Key.
$ErrorActionPreference = "Stop"
$original = (Get-Location).Path
$temp = Join-Path ([System.IO.Path]::GetTempPath()) ("powerdesigner-mcp-prueba-" + [guid]::NewGuid().ToString("N"))

try {
    New-Item -ItemType Directory -Path (Join-Path $temp ".venv/Scripts") -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path (Split-Path $PSScriptRoot -Parent) "iniciar_mcp.ps1") -Destination $temp
    '{"tunnel_id":"tunnel_prueba123","write_model":""}' |
        Set-Content -LiteralPath (Join-Path $temp "config.local.json") -Encoding Ascii
    New-Item -ItemType File -Path (Join-Path $temp "tunnel-client.exe") | Out-Null
    New-Item -ItemType File -Path (Join-Path $temp ".venv/Scripts/python.exe") | Out-Null

    $script:consultasPuerto = 0
    $script:claveSolicitada = $false
    $script:inicioIntentado = $false

    # Mocks visibles al ejecutar el script con dot sourcing en este proceso.
    function Get-NetTCPConnection {
        [CmdletBinding()]
        param([int]$LocalPort, [string]$State)
        $script:consultasPuerto++
        if ($LocalPort -ne 8000 -or $State -ne "Listen") {
            throw "La comprobacion de puerto uso argumentos inesperados."
        }
        return [pscustomobject]@{ LocalPort = 8000; State = "Listen" }
    }

    function Read-Host {
        param([string]$Prompt, [switch]$AsSecureString)
        if ($Prompt -like "*API*") { $script:claveSolicitada = $true }
        return ""
    }

    function Start-Process {
        $script:inicioIntentado = $true
        throw "El iniciador intento crear un proceso."
    }

    $salida = . (Join-Path $temp "iniciar_mcp.ps1") 2>&1 6>&1 | Out-String

    if ($salida -notmatch "El puerto 8000 ya esta ocupado") {
        throw "No se observo el mensaje de rechazo esperado: $salida"
    }
    if ($script:consultasPuerto -ne 1) {
        throw "No se consulto el puerto 8000 correctamente."
    }
    if ($script:claveSolicitada) {
        throw "El iniciador solicito una API Key durante la prueba."
    }
    if ($script:inicioIntentado) {
        throw "El iniciador intento crear un proceso durante la prueba."
    }

    Write-Host "SEGURIDAD OK: puerto ocupado rechazado sin API Key ni procesos." -ForegroundColor Green
}
finally {
    Set-Location -LiteralPath $original
    if (Test-Path -LiteralPath $temp) {
        Remove-Item -LiteralPath $temp -Recurse -Force
    }
}
