import customtkinter as ctk
from CTkToolTip import *
from enum import StrEnum
from collections.abc import Iterable
from typing import Callable
from src.common import AutoCrafterControllerInterface, ControllerState, Notification
from .custom_widgets import KeyComboWidget
from src.model import Action

class ActionDialogType(StrEnum):
    ADD = "Add"
    MODIFY = "Modify"

class ActionsTab(ctk.CTkFrame):

    def __init__(self, parent, controller : AutoCrafterControllerInterface):
        super().__init__(parent)
        self._controller = controller
        self._controller_state = ControllerState.STOPPED
        self.pack(fill="both", expand=True)

        # Left frame: custom actions
        self._custom_actions_frame = ctk.CTkFrame(self, width=170)
        self._custom_actions_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Top bar for recipe actions
        self._custom_actions_top_bar = ctk.CTkFrame(self._custom_actions_frame)
        self._custom_actions_top_bar.pack(fill="x", pady=(0, 5))
        ctk.CTkButton(self._custom_actions_top_bar, text="+", width=28, height=24, command=self._create_custom_action).pack(side="left", padx=2)
        CTkToolTip(self._custom_actions_top_bar, message="Add a new custom action")
        ctk.CTkButton(self._custom_actions_top_bar, text="✎", width=28, height=24, command=self._modify_custom_action).pack(side="left", padx=2)
        CTkToolTip(self._custom_actions_top_bar, message="Modify the selected custom action")
        ctk.CTkButton(self._custom_actions_top_bar, text="–", width=28, height=24, command=self._delete_custom_action).pack(side="left", padx=2)
        CTkToolTip(self._custom_actions_top_bar, message="Delete the selected custom action")

        # Action list frame
        self._custom_actions_list_frame = ctk.CTkFrame(self._custom_actions_frame)
        self._custom_actions_list_frame.pack(fill="both", expand=True)
        self._custom_actions = {}
        self._selected_custom_action = None

        # Right frame: fixed actions inputs
        self._fixed_actions_frame = ctk.CTkFrame(self)
        self._fixed_actions_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self._confirm_key_input = KeyComboWidget(self._fixed_actions_frame, "Confirm", "Input the key combination for confirming actions as set in the game settings")
        self._confirm_key_input.pack(padx=20, pady=4)
        self._cancel_key_input = KeyComboWidget(self._fixed_actions_frame, "Cancel", "Input the key combination for cancelling actions as set in the game settings")
        self._cancel_key_input.pack(padx=20, pady=4)

    def _select_custom_action(self, name):
        self._selected_custom_action = name
        for k, v in self._custom_actions.items():
            v.configure(fg_color="#44aa77" if k == name else ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def _create_custom_action(self):
            CustomActionDialog(
                self, 
                ActionDialogType.ADD, 
                self._on_confirm_custom_action_dialog, 
                self._custom_actions.keys())
            return "break"

    def _modify_custom_action(self):
        if self._selected_custom_action is None:
            return
        action = self._controller.get_action(self._selected_custom_action)
        CustomActionDialog(
            self,
            ActionDialogType.MODIFY,
            self._on_confirm_custom_action_dialog,
            self._custom_actions.keys(),
            selected_action=self._selected_custom_action,
            action=action
        )
        return "break"

    def _delete_custom_action(self):
        if self._selected_custom_action is not None:
            self._controller.remove_action(self._selected_custom_action)

    def _on_confirm_custom_action_dialog(self, name: str, dialog_type: ActionDialogType, action: Action):
        if dialog_type == ActionDialogType.ADD:
            self._controller.add_action(name, action)
        elif dialog_type == ActionDialogType.MODIFY:
            self._controller.modify_action(self._selected_custom_action, name, action)

    def notify(self, notification_type: Notification, content: ControllerState | Iterable[str]) -> None:
        if notification_type == Notification.CONTROLLER_STATE:
            if not isinstance(content, ControllerState):
                raise TypeError("Wrong notiofication type (expected ControllerState)")
            self._controller_state = content
        
        if notification_type == Notification.ACTION_LIST:
            if not isinstance(content, Iterable):
                raise TypeError("Wrong notification type (expected list of Action names)")
            # Update buttons
            for btn in self._custom_actions.values():
                btn.destroy()
            self._custom_actions.clear()
            
            for name in content:
                btn = ctk.CTkButton(self._custom_actions_list_frame, text=name, width=140, command=lambda n=name: self._select_custom_action(n))
                btn.pack(pady=2, fill="x")
                self._custom_actions[name] = btn
            self._selected_custom_action = None

class CustomActionDialog(ctk.CTkToplevel):
    """
    Dialog for adding or modifying custom actions.
    This is a separate class to allow for easier testing and reuse.
    """
    def __init__(
        self,
        parent: ActionsTab,
        dialog_type: ActionDialogType,
        callback: Callable,
        action_list: Iterable[str],
        selected_action: str | None = None,
        action: Action = None
    ):
        self._parent = parent
        self._type = dialog_type
        self._callback = callback
        self._selected_custom_action = selected_action
        self._action_list = action_list
        self._action = action

        super().__init__(parent)
        self.title(dialog_type + " custom action")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        parent.update_idletasks()
        x = parent.winfo_toplevel().winfo_x() + (parent.winfo_toplevel().winfo_width() // 2) - 200
        y = parent.winfo_toplevel().winfo_y() + (parent.winfo_toplevel().winfo_height() // 2) - 350
        self.geometry(f"400x620+{x}+{y}")

        # Entry and label
        self._name_frame = ctk.CTkFrame(self)
        self._name_frame.pack(padx=10, pady=8, anchor="w")
        self._name_label = ctk.CTkLabel(self._name_frame, text="Action name:")
        self._name_label.pack(padx=5, side="left")
        self._name_entry = ctk.CTkEntry(self._name_frame, width=180)
        self._name_entry.pack(side="left", padx=(10,8))
        self._name_entry.focus()

        # KeyComboWidget for shortcut
        self._shortcut_frame = ctk.CTkFrame(self)
        self._shortcut_frame.pack(padx=10, pady=2, anchor="w")
        self._shortcut_input = KeyComboWidget(self._shortcut_frame, "Shortcut", "Input the key combination for this action")
        self._shortcut_input.pack(side="left")

        # Duration entry and label
        self._duration_frame = ctk.CTkFrame(self)
        self._duration_frame.pack(padx=10, pady=(10,2), anchor="w")
        self._duration_label = ctk.CTkLabel(self._duration_frame, text="Action duration (seconds):")
        self._duration_label.pack(padx=5, side="left")
        self._duration_var = ctk.StringVar()
        self._duration_entry = ctk.CTkEntry(self._duration_frame, width=80, textvariable=self._duration_var)
        self._duration_entry.configure(validate="key", validatecommand=(self.register(lambda P : P.isdigit() or P == ""), '%P'))
        self._duration_entry.pack(side="left", padx=(10,8))

        if dialog_type == ActionDialogType.MODIFY:
            if selected_action is not None:
                self._name_entry.insert(0, selected_action)
            if action is not None:
                self._shortcut_input.set_key_combo(action.shortcut)
                self._duration_var.set(str(action.duration))

        # Text input for macro
        self._macro_label = ctk.CTkLabel(self, text="FF XIV Macro:")
        self._macro_label.pack(pady=(10,2))
        self._macro_text = ctk.CTkTextbox(self, width=360, height=245)  # 15 lines, 20px per line
        self._macro_text.pack(pady=2)

        # Limit to 15 lines like FFXIV macros
        def limit_lines(event=None):
            content = self._macro_text.get("1.0", "end-1c")
            lines = content.splitlines()
            if len(lines) > 15:
                self._macro_text.delete("1.0", "end")
                self._macro_text.insert("1.0", "\n".join(lines[:15]))
        self._macro_text.bind("<KeyRelease>", limit_lines)

        self._message_label = ctk.CTkLabel(self, text="", text_color="red")
        self._message_label.pack(pady=2)
        self._btn_frame = ctk.CTkFrame(self)
        self._btn_frame.pack(pady=12)

        ctk.CTkButton(self._btn_frame, text="Confirm", command=self._confirm, width=80).pack(side="left", padx=5)
        ctk.CTkButton(self._btn_frame, text="Cancel", command=self.destroy, width=80).pack(side="left", padx=5)

    def _confirm(self):
        name = self._name_entry.get().strip()
        shortcut = self._shortcut_input.get_key_combo()
        duration = self._duration_var.get().strip()

        if not name:
            self._message_label.configure(text="Name cannot be empty.")
            return
        if name in self._action_list and name != self._selected_custom_action:
            self._message_label.configure(text="An action with this name already exists.")
            return
        if shortcut == "":
            self._message_label.configure(text="Shortcut cannot be empty.")
            return
        if not duration.isdigit():
            self._message_label.configure(text="Duration must be an integer.")
            return

        self._callback(name, self._type, Action(shortcut, int(duration)))
        self.destroy()
        