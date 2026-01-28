# run.ps1
# Runs the RimerSR Streamlit application

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path ".venv")) {
    Write-Host "ERROR: Virtual environment not found." -ForegroundColor Red
    Write-Host "Please run: .\scripts\setup.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting RimerSR..." -ForegroundColor Cyan

& ".venv\Scripts\Activate.ps1"

streamlit run app.py
