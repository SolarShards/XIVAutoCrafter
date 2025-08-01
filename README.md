# XIVAutoCrafter

XIVAutoCrafter is a comprehensive automation tool for crafting in Final Fantasy XIV. It combines image recognition, window automation, and an intuitive UI to streamline complex crafting rotations.

## Future improvements
I reached a state where it works perfectly on my machine, therefore I'll just play with my new toy for now.
You can open an issue or branch/fork the repo if you have ideas of improvements.

## Features

### Core Functionality
- **Automated Crafting**: Execute multi-step crafting rotations with precise timing
- **OCR Text Detection**: Advanced screen-ocr technology for reliable craft window detection
- **Smart Buff Management**: Automatic food (30min) and potion (15min) buff reapplication
- **Multi-threaded Execution**: Non-blocking crafting with pause/resume capabilities
- **HQ Ingredients Support**: Optional high-quality ingredient usage per recipe
- **Directional Navigation**: Arrow key automation for interface navigation

### User Interface
- **Modern UI**: Built with CustomTkinter for a sleek, dark-mode interface
- **Recipe Management**: Create, edit, and organize complex crafting sequences
- **Action Library**: Manage custom keyboard shortcuts for crafting actions
- **Visual Feedback**: Progress tracking and real-time status updates
- **Deleted Action Handling**: Visual indicators for removed actions in recipes
- **Comprehensive Key Support**: Full pywinauto key mapping including function keys, numpad, and special characters

### Technical Features
- **MVC Architecture**: Clean separation of Model-View-Controller components
- **Data Persistence**: JSON-based configuration storage with graceful error handling
- **Window Automation**: Reliable FFXIV window targeting via pywinauto
- **Multi-language OCR Support**: Detects crafting log text in English, French, German, and Japanese
- **Advanced Key Handling**: Support for all keyboard combinations including F1-F24, numpad keys, and special characters

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows OS (required for game automation)
- Final Fantasy XIV installed and running

### Setup
1. Clone the repository:
   ```powershell
   git clone https://github.com/SolarShards/XIVAutoCrafter.git
   cd XIVAutoCrafter
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run the application:
   ```powershell
   python main.py
   ```

## Usage

### Quick Start
1. Run the application:
   ```powershell
   python main.py
   ```

2. Configure fixed actions (Actions tab):
   - Set keyboard shortcuts for all actions in the tab. Note that directions are controller inputs.
   - These are required for proper automation

3. Create custom actions (Actions tab):
   - Add keyboard shortcuts for your crafting skills (supports F1-F24, numpad keys, Ctrl/Alt/Shift combinations)
   - Set appropriate cooldown durations

4. Build recipes (Craft tab):
   - Create sequences of actions for complete crafting rotations
   - Configure food, potion, and HQ ingredients usage per recipe
   - Test with small quantities first

5. Prepare the craft (In-game):
   - Check your keyboard shortcuts
   - Make sure you have enough ingredients for the quantity you want to craft
   - Open the recipe book and select your recipe

6. Start the craft and go touch grass

### Advanced Features
- **Batch Crafting**: Set quantities up to 100 items
- **HQ Ingredients**: Toggle high-quality ingredient usage per recipe
- **Directional Controls**: Configure arrow key navigation for interface movement
- **Buff Integration**: Automatic food/potion management during long crafting sessions
- **State Management**: Pause and resume crafting operations safely

## Project Structure
```
XIVAutoCrafter/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies  
├── data.json                # User configuration and recipes (auto-created)
├── README.md                # This documentation
└── src/                     # Source code
    ├── common.py            # Shared interfaces and enums
    ├── model.py             # Data models and OCR-based game automation
    ├── controller.py        # Business logic and crafting operations
    ├── view.py              # Main UI coordinator
    └── ui/                  # User interface components
        ├── craft_tab.py     # Recipe management interface
        ├── actions_tab.py   # Action configuration interface
        └── custom_widgets.py # Custom UI components
```

## Dependencies

### Core Libraries
- **customtkinter** (5.2.2): Modern UI framework with dark mode support
- **CTkToolTip** (0.8): Enhanced tooltips for better user experience
- **screen-ocr** (0.5.0): Advanced OCR technology for text detection with WinRT support
- **pywin32** (308): Windows API integration
- **pywinauto** (0.6.9): Windows application automation and control

### Additional Runtime Dependencies
- **pyinstaller** (6.14.2): For building standalone executables
- **python** (3.8+): Required Python version

## Configuration

### Data Storage
The application stores all configuration in `data.json` (created automatically when you first save settings):
- **recipes**: User-created crafting sequences
- **actions**: Custom keyboard shortcuts and durations
- **fixed_actions**: Required system actions (confirm, cancel, food, potion, recipe book, directional controls)

### OCR Text Detection
The application uses advanced OCR to detect crafting windows automatically:
- **Multi-language Support**: Automatically detects crafting log text in English, French, German, and Japanese
- **Smart Caching**: Remembers the detected language for faster subsequent detection
- **Fallback Detection**: Uses multiple detection strategies for maximum reliability

## Safety Features
- **Window Validation**: Ensures FFXIV is running before automation
- **Error Recovery**: Graceful handling of missing actions or connection issues
- **User Control**: Easy pause/resume and stop functionality
- **Visual Feedback**: Clear status indicators and progress tracking

## Troubleshooting

### Common Issues
1. **"Could not find FFXIV window"**: Ensure FFXIV is running and visible
2. **OCR detection failing**: Check that the crafting log is visible and not obscured by other windows
3. **Actions not executing**: Verify keyboard shortcuts don't conflict with other applications
4. **Connection lost**: Application will attempt to reconnect automatically

### Performance Tips
- Close unnecessary applications to reduce system load
- Use appropriate cooldown durations for your connection speed
- Start with small quantities when testing new recipes

## Building and Distribution

### Creating an Executable
To create a standalone executable that can be distributed without Python:

1. **Quick Build** (executable only):
   ```powershell
   .\build-executable.bat
   ```
   This creates `dist\XIVAutoCrafter.exe` with all files bundled.

2. **Full Build with Installer** (recommended for distribution):
   ```powershell
   .\build-installer.bat
   ```
   This creates both the executable and a Windows installer.

### Prerequisites for Building
- Python 3.8+ with pip
- PyInstaller (automatically installed by build scripts)
- **For installer creation**: [Inno Setup 6](https://jrsoftware.org/isdl.php) (free)

### What the Installer Does
The Windows installer (`XIVAutoCrafter-Setup-v1.0.0.exe`) will:
- Install the application to `C:\Program Files\XIVAutoCrafter\`
- Include all required dependencies and configuration files
- Create a desktop shortcut (optional during installation)
- Add Start Menu shortcuts
- Register for proper Windows uninstall functionality
- Create user data directory if needed

### Manual Installation
If you prefer not to use the installer:
1. Build the executable using `build-executable.bat`
2. Copy `dist\XIVAutoCrafter.exe` to your desired location
3. `data.json` will be created automatically when you first configure the application

## Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License
XIVAutoCrafter is licensed under a Non-Commercial License. You are free to:
- ✅ Use the software for personal purposes
- ✅ Share it with friends and community
- ✅ Modify and improve the code
- ✅ Contribute to the project

**However, commercial use is prohibited:**
- ❌ Cannot sell the software or charge fees
- ❌ Cannot include in commercial products
- ❌ Cannot use for revenue generation

See [LICENSE.txt](LICENSE.txt) for full terms.

## Disclaimer
This tool is designed to assist with legitimate crafting activities in FFXIV. Users are responsible for ensuring their usage complies with the game's Terms of Service and any applicable automation policies.
