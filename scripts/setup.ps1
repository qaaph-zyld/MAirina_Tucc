# setup.ps1
# Sets up the RimerSR development environment

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "RimerSR Setup Script" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path ".venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
    $response = Read-Host "Recreate it? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "Removing existing .venv..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force .venv
    } else {
        Write-Host "Using existing .venv" -ForegroundColor Green
        & ".venv\Scripts\Activate.ps1"
        Write-Host ""
        Write-Host "Installing/updating requirements..." -ForegroundColor Yellow
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        Write-Host ""
        Write-Host "Fetching dictionary..." -ForegroundColor Yellow
        & "scripts\fetch_dict.ps1"
        Write-Host ""
        Write-Host "Setup complete!" -ForegroundColor Green
        Write-Host "Run the app with: .\scripts\run.ps1" -ForegroundColor Cyan
        exit 0
    }
}

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv

if (-not (Test-Path ".venv")) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Fetching dictionary..." -ForegroundColor Yellow
& "scripts\fetch_dict.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To run the app:" -ForegroundColor Cyan
Write-Host "  .\scripts\run.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To use the CLI:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python cli.py word --syllables 2 --max 50" -ForegroundColor White
Write-Host ""
