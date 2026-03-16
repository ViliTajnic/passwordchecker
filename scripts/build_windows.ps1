$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $root ".build-venv"
$cache = Join-Path $root ".build-cache"
Set-Location $root

New-Item -ItemType Directory -Force -Path (Join-Path $cache "pip") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $cache "pyinstaller") | Out-Null
py -m venv $venv
$env:PIP_CACHE_DIR = Join-Path $cache "pip"
& "$venv\Scripts\python.exe" -m pip install --upgrade pip -r requirements-build.txt
$env:PYINSTALLER_CONFIG_DIR = Join-Path $cache "pyinstaller"
& "$venv\Scripts\pyinstaller.exe" --clean passwordchecker.spec

Write-Host ""
Write-Host "Build complete: $root\dist\passwordchecker.exe"
