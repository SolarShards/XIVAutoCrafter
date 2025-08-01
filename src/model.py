"""
Model components for the XIV Auto Crafter application.
Contains data classes and business logic for actions, recipes, and game automation.
"""
import win32gui
from pywinauto import Application, findwindows
import screen_ocr
import sys
import os
import time
import json
from pathlib import Path

WINDOW_TITLE = "FINAL FANTASY XIV"
CRAFTING_LOG_TITLES = ["Crafting log", "Carnet d'artisanat", "HANDWERKER-NOTIZBUCH", "CRAFTING LOG"]

# Determine the correct location for data.json
# Store user data in AppData to persist across reinstalls
if getattr(sys, 'frozen', False):
    # Running as PyInstaller executable - use AppData for user data
    appdata_dir = Path(os.environ.get('APPDATA', '')) / "XIVAutoCrafter"
    appdata_dir.mkdir(exist_ok=True)  # Create directory if it doesn't exist
    SAVE_LOCATION = appdata_dir / "data.json"
else:
    # Running as script - use the parent directory of the script
    SAVE_LOCATION = Path(__file__).parent.parent / "data.json"

# Global Application instance for FFXIV window automation
_ffxiv_app = None

def get_ffxiv_app():
    """
    Get or create the global FFXIV Application instance.
    
    Returns:
        pywinauto Application instance connected to FFXIV, or None if not found
    """
    global _ffxiv_app
    
    try:
        # Check if we already have a valid connection
        if _ffxiv_app is not None:
            if _ffxiv_app.top_window().exists():
                return _ffxiv_app
            else:
                _ffxiv_app = None
        
        # Find and connect to FFXIV window
        windows = findwindows.find_windows(title_re=".*FINAL FANTASY XIV.*")
        if not windows:
            return None
        
        # Connect to the first FFXIV window found
        _ffxiv_app = Application().connect(handle=windows[0])
        return _ffxiv_app
        
    except Exception as e:
        _ffxiv_app = None
        return None

class Action:
    """
    Represents a single crafting action with a keyboard shortcut and execution duration.
    Used to automate individual crafting steps in FFXIV.
    """
    
    # Comprehensive key mapping for pywinauto
    # Special characters that need escaping
    SPECIAL_CHARS = {
        '+': '{+}',
        '^': '{^}',
        '%': '{%}',
        '~': '{~}',
        '(': '{(}',
        ')': '{)}',
        '[': '{[}',
        ']': '{]}',
        '{': '{{}',
        '}': '{}}',
        '"': '{"}',
        "'": "{'}",
        '\\': '{\\}',
        '!': '{!}',
        '@': '{@}',
        '#': '{#}',
        '$': '{$}',
        '&': '{&}',
        '*': '{*}',
        '_': '{_}',
        '=': '{=}',
        '-': '{-}',
        ';': '{;}',
        ':': '{:}',
        ',': '{,}',
        '.': '{.}',
        '/': '{/}',
        '?': '{?}',
        '|': '{|}',
        '`': '{`}',
        '<': '{<}',
        '>': '{>}',
    }
    
    # Function keys mapping
    FUNCTION_KEYS = {
        'f1': '{F1}', 'f2': '{F2}', 'f3': '{F3}', 'f4': '{F4}',
        'f5': '{F5}', 'f6': '{F6}', 'f7': '{F7}', 'f8': '{F8}',
        'f9': '{F9}', 'f10': '{F10}', 'f11': '{F11}', 'f12': '{F12}',
        'f13': '{F13}', 'f14': '{F14}', 'f15': '{F15}', 'f16': '{F16}',
        'f17': '{F17}', 'f18': '{F18}', 'f19': '{F19}', 'f20': '{F20}',
        'f21': '{F21}', 'f22': '{F22}', 'f23': '{F23}', 'f24': '{F24}'
    }
    
    # Special keys mapping
    SPECIAL_KEYS = {
        'enter': '{ENTER}',
        'return': '{ENTER}',
        'tab': '{TAB}',
        'escape': '{ESC}',
        'esc': '{ESC}',
        'space': '{SPACE}',
        'spacebar': '{SPACE}',
        'backspace': '{BACKSPACE}',
        'bs': '{BACKSPACE}',
        'delete': '{DELETE}',
        'del': '{DELETE}',
        'insert': '{INSERT}',
        'ins': '{INSERT}',
        'home': '{HOME}',
        'end': '{END}',
        'pageup': '{PGUP}',
        'pgup': '{PGUP}',
        'pagedown': '{PGDN}',
        'pgdn': '{PGDN}',
        'up': '{UP}',
        'down': '{DOWN}',
        'left': '{LEFT}',
        'right': '{RIGHT}',
        'capslock': '{CAPSLOCK}',
        'numlock': '{NUMLOCK}',
        'scrolllock': '{SCROLLLOCK}',
        'printscreen': '{PRTSC}',
        'prtsc': '{PRTSC}',
        'pause': '{PAUSE}',
        'break': '{BREAK}',
        'menu': '{APPS}',
        'apps': '{APPS}',
        'win': '{LWIN}',
        'windows': '{LWIN}',
        'lwin': '{LWIN}',
        'rwin': '{RWIN}'
    }
    
    # Numpad keys mapping
    NUMPAD_KEYS = {
        'numpad0': '{VK_NUMPAD0}', 'num0': '{VK_NUMPAD0}',
        'numpad1': '{VK_NUMPAD1}', 'num1': '{VK_NUMPAD1}',
        'numpad2': '{VK_NUMPAD2}', 'num2': '{VK_NUMPAD2}',
        'numpad3': '{VK_NUMPAD3}', 'num3': '{VK_NUMPAD3}',
        'numpad4': '{VK_NUMPAD4}', 'num4': '{VK_NUMPAD4}',
        'numpad5': '{VK_NUMPAD5}', 'num5': '{VK_NUMPAD5}',
        'numpad6': '{VK_NUMPAD6}', 'num6': '{VK_NUMPAD6}',
        'numpad7': '{VK_NUMPAD7}', 'num7': '{VK_NUMPAD7}',
        'numpad8': '{VK_NUMPAD8}', 'num8': '{VK_NUMPAD8}',
        'numpad9': '{VK_NUMPAD9}', 'num9': '{VK_NUMPAD9}',
        'numpadmultiply': '{VK_MULTIPLY}', 'num*': '{VK_MULTIPLY}',
        'numpadadd': '{VK_ADD}', 'num+': '{VK_ADD}',
        'numpadsubtract': '{VK_SUBTRACT}', 'num-': '{VK_SUBTRACT}',
        'numpaddecimal': '{VK_DECIMAL}', 'num.': '{VK_DECIMAL}',
        'numpaddivide': '{VK_DIVIDE}', 'num/': '{VK_DIVIDE}',
        'numpadenter': '{VK_RETURN}'
    }
    
    def __init__(self, shortcut: str, duration: int = 3):
        """
        Initialize an Action with a keyboard shortcut and duration.
        
        Args:
            shortcut: The key combination to send to the game (e.g., 'Ctrl+F1', 'Alt+Q')
            duration: Cooldown in seconds after sending the key (defaults to 3)
        """
        self.shortcut = shortcut
        self.duration = duration

    def _send_shortcut(self, key: str, shift: bool = False, alt: bool = False, ctrl: bool = False):
        """
        Send a single key with optional modifiers to the FFXIV window.
        
        Args:
            key: The key to send
            shift: Whether to hold Shift modifier
            alt: Whether to hold Alt modifier  
            ctrl: Whether to hold Ctrl modifier
        """
        key_lower = key.lower().strip()
        
        # Convert key to proper pywinauto format
        if key_lower in self.FUNCTION_KEYS:
            converted_key = self.FUNCTION_KEYS[key_lower]
        elif key_lower in self.SPECIAL_KEYS:
            converted_key = self.SPECIAL_KEYS[key_lower]
        elif key_lower in self.NUMPAD_KEYS:
            converted_key = self.NUMPAD_KEYS[key_lower]
        elif key.isdigit() and len(key) == 1:
            converted_key = f"{{VK_NUMPAD{key}}}"
        elif key in self.SPECIAL_CHARS:
            converted_key = self.SPECIAL_CHARS[key]
        else:
            converted_key = key
        
        # Apply modifiers
        if shift:
            converted_key = "+" + converted_key
        if alt:
            converted_key = "%" + converted_key
        if ctrl:
            converted_key = "^" + converted_key
        
        # Get the global FFXIV app and send keystrokes
        app = get_ffxiv_app()
        if app is None:
            raise RuntimeError("Could not connect to FFXIV window")
            
        try:
            window = app.window(handle=app.top_window().handle)
            window.send_keystrokes(converted_key)
        except Exception as e:
            raise RuntimeError(f"Failed to send keystroke '{converted_key}' to FFXIV window: {e}") from e

    def execute(self):
        """
        Execute the action by sending the key combination to the FFXIV game window and waiting for cooldown.
        Uses the global FFXIV Application instance for efficient window automation.
        """
        try:            
            # Parse the shortcut and send using _send_shortcut method
            
            # Split shortcut into components
            keys = [k.strip() for k in self.shortcut.split('+')]
            modifiers = [k.lower() for k in keys if k.lower() in ('ctrl', 'alt', 'shift')]
            main_keys = [k for k in keys if k.lower() not in ('ctrl', 'alt', 'shift')]
            
            # Validate that we have main keys to send
            if not main_keys:
                return
            
            # Send each main key with the appropriate modifiers
            for key in main_keys:
                try:
                    self._send_shortcut(
                        key=key,
                        shift='shift' in modifiers,
                        alt='alt' in modifiers,
                        ctrl='ctrl' in modifiers
                    )
                except Exception as e:
                    # Continue with other keys rather than failing completely
                    continue
            
        except Exception as e:
            pass
        
        # Always wait for cooldown, even if sending keys failed
        if self.duration > 0:
            time.sleep(self.duration)

    def to_dict(self) -> dict:
        """
        Convert Action to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the Action
        """
        return {
            "shortcut": self.shortcut,
            "duration": self.duration
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Action':
        """
        Create Action from dictionary loaded from JSON.
        
        Args:
            data: Dictionary containing action data
            
        Returns:
            Action object created from the data
        """
        return cls(data["shortcut"], data["duration"])

class Recipe:
    """
    Represents a crafting recipe consisting of a sequence of action names.
    Used to automate complete crafting rotations in FFXIV.
    """
    
    def __init__(self, action_names: list[str], use_food: bool = False, use_potion: bool = False, use_hq_ingredients: bool = False):
        """
        Initialize a Recipe with a list of action names to execute in sequence.
        
        Args:
            action_names: List of action names that make up the recipe
            use_food: Whether to execute food action before the recipe (defaults to False)
            use_potion: Whether to execute potion action before the recipe (defaults to False)
            use_hq_ingredients: Whether to use HQ ingredients for the recipe (defaults to False)
        """
        self.action_names = action_names
        self.use_food = use_food
        self.use_potion = use_potion
        self.use_hq_ingredients = use_hq_ingredients

    def execute(self, actions_dict: dict[str, Action]):
        """
        Execute all actions in the recipe sequentially.
        Each action will be executed with its specified cooldown before proceeding to the next.
        
        Args:
            actions_dict: Dictionary of available actions to execute by name
        """
        for action_name in self.action_names:
            if action_name == "Deleted action":
                continue
            elif action_name in actions_dict:
                actions_dict[action_name].execute()
            else:
                pass

    def to_dict(self) -> dict:
        """
        Convert Recipe to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the Recipe
        """
        return {
            "actions": self.action_names,
            "use_food": self.use_food,
            "use_potion": self.use_potion,
            "use_hq_ingredients": self.use_hq_ingredients
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Recipe':
        """
        Create Recipe from dictionary loaded from JSON.
        
        Args:
            data: Dictionary containing recipe data
            
        Returns:
            Recipe object created from the data
        """
        return cls(data["actions"], data.get("use_food", False), data.get("use_potion", False), data.get("use_hq_ingredients", False))

class XIVAutoCrafterModel:
    """
    Main model class for the XIV Auto Crafter application.
    Manages recipes, actions, templates, and provides game automation functionality.
    """
    
    def __init__(self):
        """
        Initialize the model with language settings and preload image templates.
        
        Args:
            lang: Language code for template images (defaults to "fr")
        """
        self.recipes = dict[str, Recipe]()
        self.actions = dict[str, Action]()
        
        # Fixed actions for crafting operations
        self.confirm_f_action = Action("", 0.5)
        self.cancel_f_action = Action("", 0.5)
        self.food_f_action = Action("", 2)
        self.potion_f_action = Action("", 2)
        self.recipe_book_f_action = Action("", 1)
        self.up_f_action = Action("", 0.5)
        self.down_f_action = Action("", 0.5)
        self.left_f_action = Action("", 0.5)
        self.right_f_action = Action("", 0.5)

        self._crafting_log_text = None

        self._ocr_reader = screen_ocr.Reader.create_quality_reader()

    def find_craft_window(self) -> bool:
        try:
            hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
            if not hwnd:
                return False
                
            window_rect = win32gui.GetWindowRect(hwnd)
            result = self._ocr_reader.read_screen(window_rect)

            if self._crafting_log_text is not None:
                matches = result.find_matching_words(self._crafting_log_text)
                if matches and len(matches) > 0:
                    return True
            else:
                for text in CRAFTING_LOG_TITLES:
                    matches = result.find_matching_words(text)
                    if matches and len(matches) > 0:
                        self._crafting_log_text = text
                        return True
            return False
        except Exception:
            return False
        

    def save_data(self) -> None:
        """
        Save recipes and actions to JSON file.
        """
        try:
            fixed_actions_vars = vars(self)
            # Prepare data structure
            data = {
                "recipes": {name: recipe.to_dict() for name, recipe in self.recipes.items()},
                "actions": {name: action.to_dict() for name, action in self.actions.items()},
                "fixed_actions": {name : {"shortcut": self.__getattribute__(name).shortcut} for name in fixed_actions_vars.keys() if "f_action" in name}
            }
            
            # Save to file
            with open(SAVE_LOCATION, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            pass

    def load_data(self) -> None:
        """
        Load recipes and actions from JSON file.
        Gracefully handles missing or corrupted files.
        """
        try:
            if not SAVE_LOCATION.exists():
                return
            
            with open(SAVE_LOCATION, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load actions first
            if "actions" in data:
                for name, action_data in data["actions"].items():
                    try:
                        self.actions[name] = Action.from_dict(action_data)
                    except Exception as e:
                        pass
            
            # Load recipes (after actions are loaded)
            if "recipes" in data:
                for name, recipe_data in data["recipes"].items():
                    try:
                        self.recipes[name] = Recipe.from_dict(recipe_data)
                    except Exception as e:
                        pass
            
            # Load fixed actions
            if "fixed_actions" in data:
                for name, action in data["fixed_actions"].items():
                    try:
                        self.__getattribute__(name).shortcut = action["shortcut"]
                    except Exception as e:
                        pass
            
        except Exception as e:
            pass
