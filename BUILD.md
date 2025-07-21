# XIVAutoCrafter - Build Instructions

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
- Python 3.8+
- pip (Python package manager)
- All packages from requirements.txt (auto-installed)

### For Creating Installer
- Everything above, plus:
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (free download)

## What Gets Included

Both build methods include:
- ✅ XIVAutoCrafter executable
- ✅ All image templates (`image_templates/` folder)
- ✅ All Python libraries and dependencies
- ✅ Documentation files

**Note**: `data.json` configuration file will be created automatically next to the executable when you first configure the application.

## Installation Locations

### Using the Installer
- **Application**: `C:\Program Files\XIVAutoCrafter\`
- **User Data**: `%APPDATA%\XIVAutoCrafter\` (created automatically)
- **Shortcuts**: Desktop and Start Menu

### Manual/Portable
- Wherever you place the executable
- Keep `image_templates\` folder in the same directory
- `data.json` will be created automatically when needed

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
