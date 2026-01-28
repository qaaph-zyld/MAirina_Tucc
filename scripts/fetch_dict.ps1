# fetch_dict.ps1
# Downloads and extracts Serbian Hunspell dictionary

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $ProjectRoot "data"
$DictDir = Join-Path $DataDir "dict"
$ZipPath = Join-Path $DataDir "hunspell-sr-20130715.zip"
$Url = "https://devbase.net/dict-sr/hunspell-sr-20130715.zip"

Write-Host "RimerSR Dictionary Fetcher" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $DataDir)) {
    Write-Host "Creating data directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $DataDir | Out-Null
}

$HunspellDir = Join-Path $DictDir "hunspell-sr"
$LatinDicCheck = Join-Path $HunspellDir "sr-Latn.dic"

if (Test-Path $LatinDicCheck) {
    Write-Host "Dictionary already exists at: $HunspellDir" -ForegroundColor Green
    Write-Host "Skipping download." -ForegroundColor Green
    exit 0
}

Write-Host "Downloading dictionary from: $Url" -ForegroundColor Yellow

try {
    Invoke-WebRequest -Uri $Url -OutFile $ZipPath -UseBasicParsing
    Write-Host "Download complete!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to download dictionary" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "Extracting dictionary..." -ForegroundColor Yellow

try {
    if (-not (Test-Path $DictDir)) {
        New-Item -ItemType Directory -Path $DictDir | Out-Null
    }
    
    Expand-Archive -Path $ZipPath -DestinationPath $DictDir -Force
    Write-Host "Extraction complete!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to extract dictionary" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

$HunspellSubDir = Join-Path $DictDir "hunspell-sr"
$LatinDic = Join-Path $HunspellSubDir "sr-Latn.dic"
$CyrillicDic = Join-Path $HunspellSubDir "sr.dic"

if (Test-Path $LatinDic) {
    Write-Host ""
    Write-Host "Dictionary setup successful!" -ForegroundColor Green
    Write-Host "Latin dictionary: $LatinDic" -ForegroundColor Green
    
    if (Test-Path $CyrillicDic) {
        Write-Host "Cyrillic dictionary: $CyrillicDic" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "WARNING: sr-Latn.dic not found after extraction" -ForegroundColor Yellow
    Write-Host "Available files in ${DictDir}:" -ForegroundColor Yellow
    Get-ChildItem -Path $DictDir | ForEach-Object { Write-Host "  $_" }
}

Write-Host ""
Write-Host "You can now run the application!" -ForegroundColor Cyan
