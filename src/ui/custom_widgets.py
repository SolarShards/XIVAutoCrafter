import customtkinter as ctk
from CTkToolTip import *

class KeyComboWidget(ctk.CTkFrame):
    # Class constant for symbol mapping
    SYMBOL_MAP = {
        "underscore": "_",
        "minus": "-",
        "equal": "=",
        "plus": "+",
        "bracketleft": "[",
        "bracketright": "]",
        "braceleft": "{",
        "braceright": "}",
        "semicolon": ";",
        "colon": ":",
        "apostrophe": "'",
        "quotedbl": '"',
        "comma": ",",
        "period": ".",
        "less": "<",
        "greater": ">",
        "slash": "/",
        "question": "?",
        "backslash": "\\",
        "bar": "|",
        "grave": "`",
        "asciitilde": "~",
        "exclam": "!",
        "at": "@",
        "numbersign": "#",
        "dollar": "$",
        "percent": "%",
        "asciicircum": "^",
        "ampersand": "&",
        "asterisk": "*",
        "parenleft": "(",
        "parenright": ")"
    }

    def __init__(self, parent, label: str, hint: str):
        super().__init__(parent)

        self._label = ctk.CTkLabel(self, text=label + " key:", width=90, anchor="w")
        self._entry = ctk.CTkEntry(self, width=70)
        CTkToolTip(self._entry, message=hint)
        
        # Flag to ignore the next key press after a alt combination
        self._ignore_next = False

        self._entry.bind("<KeyPress>", self._on_key)
        self._entry.bind("<Alt-KeyPress>", self._on_alt_key)
        self._entry.bind("<Control-KeyPress>", self._on_ctrl_key)
        self._entry.bind("<Shift-KeyPress>", self._on_shift_key)

    def _on_key(self, event):
        # Check if we should ignore this key press
        if self._ignore_next:
            self._ignore_next = False
            return "break"
            
        # Skip modifier keys themselves
        if event.keysym in ("Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"):
            return "break"
        
        # Use the actual character for printable keys, keysym for special keys
        self._entry.delete(0, "end")
        
        if event.char and event.char.isprintable():
            # Use the actual character for printable symbols and letters
            self._entry.insert(0, event.char)
        elif event.keysym.lower() in self.SYMBOL_MAP:
            # Use mapped symbol for common symbols
            self._entry.insert(0, self.SYMBOL_MAP[event.keysym.lower()])
        else:
            # Use keysym for non-printable keys like F1, Return, etc.
            self._entry.insert(0, event.keysym.capitalize())
        return "break"
    
    def _on_alt_key(self, event):
        self._entry.delete(0, "end")
        
        # Use symbol mapping for consistent display
        if event.keysym.lower() in self.SYMBOL_MAP:
            key_display = self.SYMBOL_MAP[event.keysym.lower()]
        else:
            key_display = event.keysym.capitalize()
            
        self._entry.insert(0, "Alt+" + key_display)
        self._ignore_next = True  # Ignore the next regular key press
        return "break"
    
    def _on_ctrl_key(self, event):
        self._entry.delete(0, "end")
        
        # Use symbol mapping for consistent display
        if event.keysym.lower() in self.SYMBOL_MAP:
            key_display = self.SYMBOL_MAP[event.keysym.lower()]
        else:
            key_display = event.keysym.capitalize()
            
        self._entry.insert(0, "Ctrl+" + key_display)
        self._ignore_next = True  # Ignore the next regular key press
        return "break"
    
    def _on_shift_key(self, event):
        self._entry.delete(0, "end")
        
        # Use symbol mapping for consistent display
        if event.keysym.lower() in self.SYMBOL_MAP:
            key_display = self.SYMBOL_MAP[event.keysym.lower()]
        else:
            key_display = event.keysym.capitalize()
            
        self._entry.insert(0, "Shift+" + key_display)
        self._ignore_next = True  # Ignore the next regular key press
        return "break"
    
    def pack(self, **kwargs):
        super().pack(**kwargs)
        self._label.pack(side="left", padx=5)
        self._entry.pack(side="left", padx=5)

    
    def get_key_combo(self) -> str:
        return self._entry.get().strip()
    
    def set_key_combo(self, key_combo: str) -> None:
        self._entry.delete(0, "end")
        self._entry.insert(0, key_combo)