"""
Model components for the XIV Auto Crafter application.
Contains data classes and business logic for actions, recipes, and game automation.
"""

import win32gui
import win32ui
import win32con
import ctypes
import os
import time
import json
from pathlib import Path
from PIL import Image
from PIL.ImageFile import ImageFile
from typing import Optional
import pyautogui
import numpy as np
import cv2
from pywinauto import Application, findwindows

WINDOW_TITLE = "FINAL FANTASY XIV"
SAVE_LOCATION = Path(__file__).parent.parent / "data.json"

class Action:
    """
    Represents a single crafting action with a keyboard shortcut and execution duration.
    Used to automate individual crafting steps in FFXIV.
    """
    
    def __init__(self, shortcut: str, duration: int = 3):
        """
        Initialize an Action with a keyboard shortcut and duration.
        
        Args:
            shortcut: The key combination to send to the game (e.g., 'Ctrl+1', 'Alt+Q')
            duration: Cooldown in seconds after sending the key (defaults to 3)
        """
        self.shortcut = shortcut
        self.duration = duration

    def execute(self):
        """
        Execute the action by sending the key combination to the FFXIV game window and waiting for cooldown.
        Uses pywinauto to find and send keys to the FFXIV window directly.
        """
        try:
            # Find all windows with FFXIV in the title
            windows = findwindows.find_windows(title_re=".*FINAL FANTASY XIV.*")
            if not windows:
                print(f"[ERROR] Could not find window containing 'FINAL FANTASY XIV'")
                return
            
            # Connect to the first FFXIV window found
            app = Application().connect(handle=windows[0])
            window = app.window(handle=windows[0])
            
            # Make sure the window is ready
            if not window.exists():
                print(f"[ERROR] FFXIV window is not accessible")
                return
            
            # Send the key combination directly using pywinauto
            print(f"[INFO] Sending key combo to FFXIV window: {self.shortcut}")
            window.send_keystrokes(self.shortcut)
            
            print(f"[INFO] Successfully sent key combo: {self.shortcut}")
            
        except Exception as e:
            print(f"[ERROR] Failed to send key combo '{self.shortcut}' to FFXIV window: {e}")
        
        print(f"[INFO] Waiting for cooldown: {self.duration} seconds")
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
    Represents a crafting recipe consisting of a sequence of actions.
    Used to automate complete crafting rotations in FFXIV.
    """
    
    def __init__(self, actions: list[Action], use_food: bool = False, use_potion: bool = False):
        """
        Initialize a Recipe with a list of actions to execute in sequence.
        
        Args:
            actions: List of Action objects that make up the recipe
            use_food: Whether to execute food action before the recipe (defaults to False)
            use_potion: Whether to execute potion action before the recipe (defaults to False)
        """
        self.actions = actions
        self.use_food = use_food
        self.use_potion = use_potion

    def execute(self):
        """
        Execute all actions in the recipe sequentially.
        Each action will be executed with its specified cooldown before proceeding to the next.
        """
        for action in self.actions:
            action.execute()

    def to_dict(self, actions_dict: dict[str, 'Action']) -> dict:
        """
        Convert Recipe to dictionary for JSON serialization.
        
        Args:
            actions_dict: Dictionary of available actions to find names by reference
        
        Returns:
            Dictionary representation of the Recipe
        """
        action_names = []
        for action in self.actions:
            # Find the action name by comparing object references
            action_name = None
            for name, dict_action in actions_dict.items():
                if dict_action is action:
                    action_name = name
                    break
            
            if action_name is not None:
                action_names.append(action_name)
            else:
                # Fallback to shortcut if name not found
                action_names.append(action.shortcut)
                print(f"[WARN] Action name not found for shortcut '{action.shortcut}', using shortcut")
        
        return {
            "actions": action_names,
            "use_food": self.use_food,
            "use_potion": self.use_potion
        }

    @classmethod
    def from_dict(cls, data: dict, actions_dict: dict[str, 'Action']) -> 'Recipe':
        """
        Create Recipe from dictionary loaded from JSON.
        
        Args:
            data: Dictionary containing recipe data
            actions_dict: Dictionary of available actions to reference by name
            
        Returns:
            Recipe object created from the data
        """
        actions = []
        for action_name in data["actions"]:
            if action_name in actions_dict:
                actions.append(actions_dict[action_name])
            else:
                print(f"[WARN] Action '{action_name}' not found, skipping")
        
        return cls(actions, data["use_food"], data["use_potion"])

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
        self.confirm_action = Action("", 1)
        self.cancel_action = Action("", 0.5)
        self.food_action = Action("", 2)
        self.potion_action = Action("", 2)
        self.recipe_book_action = Action("", 1)
        
        for name in ["craft_window.png", "craft_button.png"]:
            template_path = os.path.join('image_templates', lang, name)
            if os.path.exists(template_path):
                self.templates[name] = Image.open(template_path)
            else:
                self.templates[name] = None
                print(f"[WARN] Template not found: {template_path}")

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
            print(f"[ERROR] Template '{template_name}' not loaded.")
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
            print(f"[ERROR] Could not capture window '{WINDOW_TITLE}'.")
            return False
        window_center = self._find_template_in_image(img, "craft_window.png")
        if window_center:
            print(f"[INFO] 'craft_window.png' found at {window_center}")
            return True
        else:
            print("[INFO] 'craft_window.png' NOT found in the image.")
            return False

    def find_craft_button(self) -> Optional[tuple]:
        """
        Searches for craft_button.png in the FINAL FANTASY XIV window.
        
        Returns:
            Tuple of (x, y) center coordinates if craft button is found, None otherwise
        """
        img = self._capture_window(WINDOW_TITLE)
        if img is None:
            print(f"[ERROR] Could not capture window '{WINDOW_TITLE}'.")
            return None
        button_center = self._find_template_in_image(img, "craft_button.png")
        if button_center:
            print(f"[INFO] 'craft_button.png' found at {button_center}")
            return button_center
        else:
            print("[INFO] 'craft_button.png' NOT found in the image.")
            return None

    def click(self, x: int, y: int) -> None:
        """
        Performs a double click with 0.3 second interval at the specified coordinates.
        
        Args:
            x: X coordinate for the click
            y: Y coordinate for the click
        """
        try:
            pyautogui.moveTo(x, y)
            print(f"[INFO] Cursor moved to ({x}, {y})")
            pyautogui.click(clicks=2, interval=0.3)
            print(f"[INFO] Double click performed at ({x}, {y})")
        except Exception as e:
            print(f"[ERROR] Could not move mouse or click: {e}")

    def save_data(self) -> None:
        """
        Save recipes and actions to JSON file.
        """
        try:
            # Prepare data structure
            data = {
                "recipes": {name: recipe.to_dict(self.actions) for name, recipe in self.recipes.items()},
                "actions": {name: action.to_dict() for name, action in self.actions.items()},
                "fixed_actions": {
                    "confirm_action": {"shortcut": self.confirm_action.shortcut},
                    "cancel_action": {"shortcut": self.cancel_action.shortcut},
                    "food_action": {"shortcut": self.food_action.shortcut},
                    "potion_action": {"shortcut": self.potion_action.shortcut},
                    "recipe_book_action": {"shortcut": self.recipe_book_action.shortcut}
                }
            }
            
            # Save to file
            with open(SAVE_LOCATION, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"[INFO] Data saved to {SAVE_LOCATION}")
            
        except Exception as e:
            print(f"[ERROR] Failed to save data: {e}")

    def load_data(self) -> None:
        """
        Load recipes and actions from JSON file.
        Gracefully handles missing or corrupted files.
        """
        try:
            if not SAVE_LOCATION.exists():
                print(f"[INFO] No data file found at {SAVE_LOCATION}, starting with empty data")
                return
            
            with open(SAVE_LOCATION, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load actions first
            if "actions" in data:
                for name, action_data in data["actions"].items():
                    try:
                        self.actions[name] = Action.from_dict(action_data)
                    except Exception as e:
                        print(f"[WARN] Failed to load action '{name}': {e}")
            
            # Load recipes (after actions are loaded)
            if "recipes" in data:
                for name, recipe_data in data["recipes"].items():
                    try:
                        self.recipes[name] = Recipe.from_dict(recipe_data, self.actions)
                    except Exception as e:
                        print(f"[WARN] Failed to load recipe '{name}': {e}")
            
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
                except Exception as e:
                    print(f"[WARN] Failed to load some fixed actions: {e}")
            
            print(f"[INFO] Loaded {len(self.recipes)} recipes and {len(self.actions)} actions from {SAVE_LOCATION}")
            
        except Exception as e:
            print(f"[ERROR] Failed to load data: {e}")
            print("[INFO] Starting with empty data")
