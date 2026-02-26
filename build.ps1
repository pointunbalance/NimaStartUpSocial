$Version = "1.7"
$AppName = "NimaStartUpSocial"
$DistDir = "dist"
$InstallerDir = "installer_output"
$ISCC = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building $AppName v$Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Clean previous builds
Write-Host "[1/3] Cleaning previous build artifacts..." -ForegroundColor Yellow
if (Test-Path $DistDir) { Remove-Item -Path $DistDir -Recurse -Force }
if (Test-Path "build") { Remove-Item -Path "build" -Recurse -Force }
if (Test-Path $InstallerDir) { Remove-Item -Path $InstallerDir -Recurse -Force }

# Step 2: Build Executable with PyInstaller
Write-Host "[2/3] Building executable with PyInstaller..." -ForegroundColor Yellow
python -m PyInstaller --clean "$AppName.spec"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] PyInstaller build failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Build Installer with Inno Setup
Write-Host "[3/3] Building setup installer with Inno Setup..." -ForegroundColor Yellow
if (Test-Path $ISCC) {
    & $ISCC installer.iss
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Inno Setup compilation failed!" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "[WARNING] Inno Setup (ISCC.exe) not found at $ISCC." -ForegroundColor Magenta
    Write-Host "Skipping installer build." -ForegroundColor Magenta
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Complete! 🚀" -ForegroundColor Cyan
Write-Host "Executable: $DistDir\$AppName.exe" -ForegroundColor Cyan
Write-Host "Installer: $InstallerDir\Setup_$AppName.exe" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
