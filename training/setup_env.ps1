$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $PSScriptRoot ".venv"

if (-not (Test-Path $venvPath)) {
    Write-Host "Criando virtualenv em $venvPath"
    & "C:\Espressif\tools\python\v6.0.1\venv\Scripts\python.exe" -m venv $venvPath
}

$python = Join-Path $venvPath "Scripts\python.exe"

Write-Host "Atualizando pip"
& $python -m pip install --upgrade pip

Write-Host "Instalando dependencias do treino"
& $python -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")

Write-Host "Ambiente pronto."
Write-Host "Ative com:"
Write-Host "  .\\training\\.venv\\Scripts\\Activate.ps1"
