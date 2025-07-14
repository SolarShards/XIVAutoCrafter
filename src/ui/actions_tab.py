import customtkinter as ctk
from CTkToolTip import *
from enum import Enum
from collections.abc import Iterable
from src.common import AutoCrafterControllerInterface, ControllerState, Notification
from .custom_widgets import KeyComboWidget

class ActionsTab(ctk.CTkFrame):

    class ActionDialog(Enum):
        ADD = 0
        MODIFY = 1

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
        ctk.CTkButton(self._custom_actions_top_bar, text="+", width=28, height=24, command=lambda: self._open_custom_action_dialog(self.ActionDialog.ADD)).pack(side="left", padx=2)
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

    def _open_custom_action_dialog(self, dialog_type : ActionDialog):
        if dialog_type == self.ActionDialog.ADD:
            title = "Add Custom Action"
            label_text = "Enter action name:"
            default_text = ""
        elif dialog_type == self.ActionDialog.MODIFY:
            title = "Modify Custom Action"
            label_text = "Edit action name:"
            default_text = self._selected_custom_action

        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("300x160")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        self.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 150
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 80
        dialog.geometry(f"300x160+{x}+{y}")
        ctk.CTkLabel(dialog, text=label_text).pack(pady=10)
        entry = ctk.CTkEntry(dialog, width=200)
        entry.pack(pady=5)
        entry.focus()
        if default_text:
            entry.insert(0, default_text)
        message_label = ctk.CTkLabel(dialog, text="", text_color="red")
        message_label.pack(pady=2)
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=10)

        def confirm():
            name = entry.get().strip()
            if not name:
                message_label.configure(text="Name cannot be empty.")
                return
            if name in self._custom_actions:
                message_label.configure(text="An action with this name already exists.")
                return
            self._on_confirm_custom_action_dialog(name, dialog, dialog_type)
        ctk.CTkButton(btn_frame, text="Confirm", command=confirm, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy, width=80).pack(side="left", padx=5)

    def _on_confirm_custom_action_dialog(self, name : str, dialog : ctk.CTkToplevel, dialog_type : ActionDialog):
        if dialog_type == self.ActionDialog.ADD:
            if self._controller.add_action(name):
                dialog.destroy()
        elif dialog_type == self.ActionDialog.MODIFY:
            if self._controller.modify_action(self._selected_custom_action, name):
                dialog.destroy()

    def _select_custom_action(self, name):
        self._selected_custom_action = name
        for k, v in self._custom_actions.items():
            v.configure(fg_color="#44aa77" if k == name else ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def _modify_custom_action(self):
        if self._selected_custom_action is not None:
            self._open_custom_action_dialog(self.ActionDialog.MODIFY)

    def _delete_custom_action(self):
        if self._selected_custom_action is not None:
            self._controller.remove_action(self._selected_custom_action)

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