import customtkinter as ctk
from CTkToolTip import *

class KeyComboWidget(ctk.CTkFrame):
    def __init__(self, parent, label: str, hint: str):
        super().__init__(parent)

        self._label = ctk.CTkLabel(self, text=label + " key:", width=90, anchor="w")
        self._entry = ctk.CTkEntry(self, width=70)
        CTkToolTip(self._entry, message=hint)

        self._entry.bind("<KeyPress>", self._on_key)
        self._entry.bind("<Alt-KeyPress>", self._on_alt_key)
        self._entry.bind("<Control-KeyPress>", self._on_ctrl_key)
        self._entry.bind("<Shift-KeyPress>", self._on_shift_key)

    def _on_key(self, event):
        # Don't handle if any modifier keys are pressed - let the specific modifier handlers deal with it
        if event.state & (0x4 | 0x8 | 0x1):  # Ctrl, Alt, or Shift is pressed
            return "break"
        # Only handle plain keys (no modifiers)
        if event.keysym not in ("Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R") and event.keysym == event.char:
            self._entry.delete(0, "end")
            self._entry.insert(0, event.keysym.capitalize())
        return "break"
    
    def _on_alt_key(self, event):
        self._entry.delete(0, "end")
        self._entry.insert(0, "Alt+" + event.keysym.capitalize())
        return "break"
    
    def _on_ctrl_key(self, event):
        self._entry.delete(0, "end")
        self._entry.insert(0, "Ctrl+" + event.keysym.capitalize())
        return "break"
    
    def _on_shift_key(self, event):
        self._entry.delete(0, "end")
        self._entry.insert(0, "Shift+" + event.keysym.capitalize())
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