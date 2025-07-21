@echo off
REM XIVAutoCrafter - Simple Executable Build Script
REM 
REM ⚠️  IMPORTANT: XIVAutoCrafter is FREE SOFTWARE ⚠️
REM This software may NEVER be sold or charged for by anyone.

echo Building XIVAutoCrafter executable...
echo ====================================
echo ⚠️  This software is FREE and must remain FREE ⚠️
echo ====================================

REM Install PyInstaller if not available
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable
echo Building executable...
python -m PyInstaller build.spec

if %errorlevel% equ 0 (
    echo.
    echo Build completed successfully!
    echo Executable location: dist\XIVAutoCrafter.exe
    echo.
    echo The executable includes:
    echo - All image templates
    echo - All required libraries
    echo.
    echo Note: data.json will be created automatically next to the executable
    echo when you first configure the application.
) else (
    echo.
    echo Build failed! Check the output above for errors.
)

pause
