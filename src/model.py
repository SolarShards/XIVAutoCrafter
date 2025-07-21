"""
Model components for the XIV Auto Crafter application.
Contains data classes and business logic for actions, recipes, and game automation.
"""

import win32gui
import win32ui
import ctypes
import os
import time
import json
from pathlib import Path
from PIL import Image
from PIL.ImageFile import ImageFile
from typing import Optional
import numpy as np
import cv2
from pywinauto import Application, findwindows

WINDOW_TITLE = "FINAL FANTASY XIV"
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
    
    def __init__(self, lang: str = "fr"):
        """
        Initialize the model with language settings and preload image templates.
        
        Args:
            lang: Language code for template images (defaults to "fr")
        """
        self.lang = lang
        self.recipes = dict[str, Recipe]()
        self.actions = dict[str, Action]()
        self.templates = dict[str, ImageFile]()
        
        # Fixed actions for crafting operations
        self.confirm_action = Action("", 0.5)
        self.cancel_action = Action("", 0.5)
        self.food_action = Action("", 2)
        self.potion_action = Action("", 2)
        self.recipe_book_action = Action("", 1)
        self.up_action = Action("", 0.5)
        self.down_action = Action("", 0.5)
        self.left_action = Action("", 0.5)
        self.right_action = Action("", 0.5)

        for name in ["craft_window.png", "craft_button.png"]:
            template_path = os.path.join('image_templates', lang, name)
            if os.path.exists(template_path):
                self.templates[name] = Image.open(template_path)
            else:
                self.templates[name] = None

    def _capture_window(self, window_title: str) -> Optional[Image.Image]:
        """
        Capture the contents of a window by its title, even if it is not in the foreground.
        
        Args:
            window_title: The title of the window to capture
            
        Returns:
            PIL Image of the window contents or None if window not found or capture fails
        """
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            return None
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        left, top = win32gui.ClientToScreen(hwnd, (left, top))
        right, bottom = win32gui.ClientToScreen(hwnd, (right, bottom))
        width = right - left
        height = bottom - top
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)
        # Use ctypes for PrintWindow
        result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        if result != 1:
            return None
        return img

    def _find_template_in_image(self, img: Image.Image, template_name: str, threshold: float = 0.8) -> Optional[tuple]:
        """
        Detects a preloaded template image inside another image using OpenCV template matching.
        
        Args:
            img: The source image to search within
            template_name: Name of the template image to search for
            threshold: Confidence threshold for template matching (defaults to 0.8)
            
        Returns:
            Tuple of (x, y) center coordinates of the best match if above threshold, else None
        """
        template = self.templates.get(template_name)
        if template is None:
            return None
        img_cv = np.array(img.convert('RGB'))
        template_cv = np.array(template.convert('RGB'))
        res = cv2.matchTemplate(img_cv, template_cv, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold:
            w, h = template.size
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)
        return None

    def find_craft_window(self) -> bool:
        """
        Searches for craft_window.png in the FINAL FANTASY XIV window.
        
        Returns:
            True if craft window template is found, False otherwise
        """
        img = self._capture_window(WINDOW_TITLE)
        if img is None:
            return False
        window_center = self._find_template_in_image(img, "craft_window.png")
        if window_center:
            return True
        else:
            return False

    def find_craft_button(self) -> Optional[tuple]:
        """
        Searches for craft_button.png in the FINAL FANTASY XIV window.
        
        Returns:
            Tuple of (x, y) center coordinates if craft button is found, None otherwise
        """
        img = self._capture_window(WINDOW_TITLE)
        if img is None:
            return None
        button_center = self._find_template_in_image(img, "craft_button.png")
        if button_center:
            return button_center
        else:
            return None

    def save_data(self) -> None:
        """
        Save recipes and actions to JSON file.
        """
        try:
            # Prepare data structure
            data = {
                "recipes": {name: recipe.to_dict() for name, recipe in self.recipes.items()},
                "actions": {name: action.to_dict() for name, action in self.actions.items()},
                "fixed_actions": {
                    "confirm_action": {"shortcut": self.confirm_action.shortcut},
                    "cancel_action": {"shortcut": self.cancel_action.shortcut},
                    "food_action": {"shortcut": self.food_action.shortcut},
                    "potion_action": {"shortcut": self.potion_action.shortcut},
                    "recipe_book_action": {"shortcut": self.recipe_book_action.shortcut},
                    "up_action": {"shortcut": self.up_action.shortcut},
                    "down_action": {"shortcut": self.down_action.shortcut},
                    "left_action": {"shortcut": self.left_action.shortcut},
                    "right_action": {"shortcut": self.right_action.shortcut}
                }
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
                fixed_actions = data["fixed_actions"]
                try:
                    if "confirm_action" in fixed_actions:
                        self.confirm_action.shortcut = fixed_actions["confirm_action"]["shortcut"]
                    if "cancel_action" in fixed_actions:
                        self.cancel_action.shortcut = fixed_actions["cancel_action"]["shortcut"]
                    if "food_action" in fixed_actions:
                        self.food_action.shortcut = fixed_actions["food_action"]["shortcut"]
                    if "potion_action" in fixed_actions:
                        self.potion_action.shortcut = fixed_actions["potion_action"]["shortcut"]
                    if "recipe_book_action" in fixed_actions:
                        self.recipe_book_action.shortcut = fixed_actions["recipe_book_action"]["shortcut"]
                    if "up_action" in fixed_actions:
                        self.up_action.shortcut = fixed_actions["up_action"]["shortcut"]
                    if "down_action" in fixed_actions:
                        self.down_action.shortcut = fixed_actions["down_action"]["shortcut"]
                    if "left_action" in fixed_actions:
                        self.left_action.shortcut = fixed_actions["left_action"]["shortcut"]
                    if "right_action" in fixed_actions:
                        self.right_action.shortcut = fixed_actions["right_action"]["shortcut"]
                except Exception as e:
                    pass
            
        except Exception as e:
            pass
