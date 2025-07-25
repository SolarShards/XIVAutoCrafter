# XIVAutoCrafter - Build Instructions

XIVAutoCrafter uses OCR-based text detection for reliable game automation. This document covers building and packaging the application.

## Quick Start

### Option 1: Simple Executable Build
```powershell
.\build-executable.bat
```
- Creates: `dist\XIVAutoCrafter.exe`
- Portable executable with all files included
- No installation required

### Option 2: Complete Installer (Recommended)
```powershell
.\build-installer.bat
```
- Creates: `installer\XIVAutoCrafter-Setup-v1.0.0.exe`
- Professional Windows installer
- Installs to Program Files
- Creates desktop and Start Menu shortcuts
- Proper uninstall support

## Requirements

### For Building Executable
- Python 3.8+ (tested with 3.12)
- pip (Python package manager)
- Core dependencies (auto-installed):
  - `customtkinter (5.2.2)`: Modern UI framework
  - `CTkToolTip (0.8)`: Enhanced tooltips
  - `screen-ocr (0.5.0)`: OCR with WinRT support
  - `pywin32 (308)`: Windows API integration
  - `pywinauto (0.6.9)`: Windows automation

### For Creating Installer
- Everything above, plus:
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (free download)

## What Gets Included

Both build methods include:
- ✅ XIVAutoCrafter executable with OCR capabilities
- ✅ All Python libraries and dependencies
- ✅ Documentation files (README.md, LICENSE.txt)
- ✅ Multi-language OCR support (EN/FR/DE/JP)

**Note**: `data.json` configuration file will be created automatically in your AppData when you first configure the application.

## Installation Locations

### Using the Installer
- **Application**: `C:\Program Files\XIVAutoCrafter\`
- **User Data**: `%APPDATA%\XIVAutoCrafter\` (created automatically)
- **Shortcuts**: Desktop and Start Menu

### Manual/Portable
- Wherever you place the executable
- `data.json` will be created automatically when needed
- No additional files required (OCR detection is built-in)

## Troubleshooting

### Build Fails
1. Ensure Python 3.8+ is installed: `python --version`
2. Update pip: `python -m pip install --upgrade pip`
3. Install requirements: `pip install -r requirements.txt`

### Installer Creation Fails
1. Download and install [Inno Setup 6](https://jrsoftware.org/isdl.php)
2. Ensure it's installed to the default location
3. Run `build-installer.bat` again

### Runtime Issues
- Windows Defender may flag the executable initially (false positive)
- Add exclusion for the XIVAutoCrafter folder if needed
- Ensure FFXIV is running before starting the application
- OCR requires Windows 10/11 for optimal performance

## OCR Technology

### Screen-OCR Features
- **WinRT Integration**: Uses Windows Runtime OCR APIs for high accuracy
- **Multi-language Support**: Automatically detects EN/FR/DE/JP text
- **Smart Caching**: Remembers detected language for faster subsequent detection
