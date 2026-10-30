$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
py -3.12 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el entorno. Instala Python 3.12." }
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias." }
if (-not (Test-Path config.local.json)) {
    Copy-Item config.example.json config.local.json
}
Write-Host "Entorno listo. Completa config.local.json y descarga tunnel-client.exe."
