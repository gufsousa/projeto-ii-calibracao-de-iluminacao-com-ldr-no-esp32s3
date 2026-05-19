$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $PSScriptRoot ".venv-tf"

function Get-Python311Command {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @("py", "-3.11")
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        $version = (& python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')").Trim()
        if ($version -eq "3.11") {
            return @("python")
        }

        throw "Encontrei Python $version, mas o TensorFlow deste projeto precisa de Python 3.11."
    }

    throw "Nao encontrei um interpretador Python. Instale o Python 3.11 para usar o TensorFlow."
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Criando virtualenv em $venvPath"
    $pythonCmd = Get-Python311Command
    if ($pythonCmd.Length -gt 1) {
        & $pythonCmd[0] $pythonCmd[1] -m venv $venvPath
    } else {
        & $pythonCmd[0] -m venv $venvPath
    }
}

$python = Join-Path $venvPath "Scripts\python.exe"

Write-Host "Atualizando pip"
& $python -m pip install --upgrade pip

Write-Host "Instalando dependencias do treino"
& $python -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")

Write-Host "Ambiente pronto."
Write-Host "Ative com:"
Write-Host "  .\\training\\.venv-tf\\Scripts\\Activate.ps1"
