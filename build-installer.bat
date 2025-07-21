@echo off
REM XIVAutoCrafter - Complete Build and Installer Script
REM This script builds the executable and creates a Windows installer
REM 
REM ⚠️  IMPORTANT: XIVAutoCrafter is FREE SOFTWARE ⚠️
REM This software may NEVER be sold or charged for by anyone.
REM It must remain free for all users forever.

echo ==========================================
echo XIVAutoCrafter - Build and Package Script
echo ==========================================
echo.
echo ⚠️  REMINDER: This software is FREE and must remain FREE ⚠️
echo    No one may sell this software or charge fees for it.
echo ==========================================

echo.
echo Checking prerequisites...
echo ========================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if PyInstaller is available
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

REM Install other required packages
echo Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages!
    pause
    exit /b 1
)

echo.
echo Step 1: Building executable...
echo ==============================

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build using the spec file
python -m PyInstaller build.spec

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to build executable!
    pause
    exit /b 1
)

echo Executable built successfully: dist\XIVAutoCrafter.exe

echo.
echo Step 2: Checking for Inno Setup...
echo ==================================

REM Check for Inno Setup in common locations
set "INNO_SETUP_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_SETUP_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set "INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 5\ISCC.exe" (
    set "INNO_SETUP_PATH=C:\Program Files\Inno Setup 5\ISCC.exe"
)

if "%INNO_SETUP_PATH%"=="" (
    echo.
    echo WARNING: Inno Setup not found!
    echo Please download and install Inno Setup from:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo You can still run the executable manually from: dist\XIVAutoCrafter.exe
    echo To create the installer later, run this script again after installing Inno Setup.
    pause
    exit /b 0
)

echo Found Inno Setup at: %INNO_SETUP_PATH%

REM Create installer directory
if not exist "installer" mkdir "installer"

echo.
echo Step 3: Creating Windows installer...
echo ====================================

REM Build the installer
"%INNO_SETUP_PATH%" XIVAutoCrafter.iss

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo SUCCESS: Build completed!
    echo ==========================================
    echo.
    echo Files created:
    echo - Executable: dist\XIVAutoCrafter.exe
    echo - Installer:  installer\XIVAutoCrafter-Setup-v1.0.0.exe
    echo.
    echo The installer will:
    echo - Install to: C:\Program Files\XIVAutoCrafter\
    echo - Include all image templates
    echo - Create desktop shortcut (optional during install)
    echo - Create Start Menu shortcuts
    echo - Provide proper uninstall functionality
    echo.
    echo Note: data.json will be created automatically next to the executable
    echo when you first configure the application.
    echo.
    echo You can now distribute the installer file!
) else (
    echo.
    echo ERROR: Failed to create installer!
    echo The executable is still available at: dist\XIVAutoCrafter.exe
)

echo.
pause
