@echo off
set VERSION=2.1
set APP_NAME=NimaStartUpSocial
set DIST_DIR=dist
set INSTALLER_DIR=installer_output
set ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe

echo ========================================
echo Building %APP_NAME% v%VERSION%
echo ========================================

:: Step 1: Clean previous builds
echo [1/3] Cleaning previous build artifacts...
if exist %DIST_DIR% rd /s /q %DIST_DIR%
if exist build rd /s /q build
if exist %INSTALLER_DIR% rd /s /q %INSTALLER_DIR%

:: Step 2: Build Executable with PyInstaller
echo [2/3] Building executable with PyInstaller...
python -m PyInstaller --clean %APP_NAME%.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed!
    exit /b 1
)

:: Step 3: Build Installer with Inno Setup
echo [3/3] Building setup installer with Inno Setup...
if exist "%ISCC_EXE%" (
    "%ISCC_EXE%" installer.iss
    if errorlevel 1 (
        echo [ERROR] Inno Setup compilation failed!
        exit /b 1
    )
) else (
    echo [WARNING] Inno Setup (ISCC.exe) not found at "%ISCC_EXE%". 
    echo Skipping installer build.
)

echo ========================================
echo Build Complete! 🚀
echo Executable: %DIST_DIR%\%APP_NAME%.exe
echo Installer: %INSTALLER_DIR%\Setup_%APP_NAME%.exe
echo ========================================
pause
