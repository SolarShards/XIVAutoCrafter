import win32gui
import win32ui
import win32con
import ctypes
import os
import time
from PIL import Image
from PIL.ImageFile import ImageFile
from typing import Optional
import pyautogui
import numpy as np
import cv2

WINDOW_TITLE = "FINAL FANTASY XIV"


class Action:
    def __init__(self, shortcut: str, duration: int = 3):
        """
        Represents an action in the crafting automation with a key combination and cooldown.
        :param key_combo: The key combination to send to the game (e.g., 'Ctrl+1', 'Alt+Q').
        :param cooldown: Cooldown in seconds after sending the key.
        """
        self._shortcut = shortcut
        self._duration = duration

    def execute(self):
        """
        Sends the key combination to the game using pyautogui, then waits for the cooldown.
        """
        keys = self._shortcut.split('+')
        modifiers = [k.lower() for k in keys if k.lower() in ('ctrl', 'alt', 'shift')]
        main_keys = [k for k in keys if k.lower() not in ('ctrl', 'alt', 'shift')]
        try:
            for mod in modifiers:
                pyautogui.keyDown(mod)
            for key in main_keys:
                pyautogui.press(key)
            for mod in reversed(modifiers):
                pyautogui.keyUp(mod)
            print(f"[INFO] Sent key combo: {self._shortcut}")
        except Exception as e:
            print(f"[ERROR] Failed to send key combo '{self._shortcut}': {e}")
        print(f"[INFO] Waiting for cooldown: {self._duration} seconds")
        time.sleep(self._duration)

class Recipe:
    def __init__(self):
        pass

class XIVAutoCrafterModel:
    def __init__(self, lang: str = "fr"):
        """
        Initialize the model with a language and preload image templates as attributes.
        """
        self.lang = lang
        self.recipes = dict[str, Recipe]()
        self.actions = dict[str, Action]()
        self.templates = dict[str, ImageFile]()
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
        Returns a PIL Image or None if the window is not found or capture fails.
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
        Returns the center (x, y) of the best match if above threshold, else None.
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
        Searches for craft_window.png in the FINAL FANTASY XIV window and returns True if found, else False.
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
        Searches for craft_button.png in the FINAL FANTASY XIV window and returns the center coordinates if found, else None.
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
        Double clicks with an interval of 0.3 seconds at the given coordinates in the game window.
        """
        try:
            pyautogui.moveTo(x, y)
            print(f"[INFO] Cursor moved to ({x}, {y})")
            pyautogui.click(clicks=2, interval=0.3)
            print(f"[INFO] Double click performed at ({x}, {y})")
        except Exception as e:
            print(f"[ERROR] Could not move mouse or click: {e}")
