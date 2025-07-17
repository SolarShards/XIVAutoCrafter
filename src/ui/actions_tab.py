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

class FixedActionType(StrEnum):
    CONFIRM = "confirm"
    CANCEL = "cancel"
    FOOD = "food"
    POTION = "potion"

class ActionsTab(ctk.CTkFrame):

    def __init__(self, parent, controller : AutoCrafterControllerInterface):
        """
        Initialize the ActionsTab frame with action management UI.
        
        Args:
            parent: Parent widget (usually the main application window)
            controller: Controller interface for managing actions and application state
        """
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
        ctk.CTkButton(self._custom_actions_top_bar, text="+", width=28, height=24, command=lambda: self._open_action_dialog(ActionDialogType.ADD)).pack(side="left", padx=2)
        CTkToolTip(self._custom_actions_top_bar, message="Add a new custom action")
        ctk.CTkButton(self._custom_actions_top_bar, text="✎", width=28, height=24, command=lambda: self._open_action_dialog(ActionDialogType.MODIFY)).pack(side="left", padx=2)
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
        self._food_key_input = KeyComboWidget(self._fixed_actions_frame, "Food", "Input the key combination for consuming food as set in the game settings")
        self._food_key_input.pack(padx=20, pady=4)
        self._potion_key_input = KeyComboWidget(self._fixed_actions_frame, "Potion", "Input the key combination for drinking a CP potion as set in the game settings")
        self._potion_key_input.pack(padx=20, pady=4)

        # Bind events to detect when fixed action keys are entered
        self._confirm_key_input._entry.bind("<KeyRelease>", lambda e: self._on_fixed_action_changed(FixedActionType.CONFIRM))
        self._cancel_key_input._entry.bind("<KeyRelease>", lambda e: self._on_fixed_action_changed(FixedActionType.CANCEL))
        self._food_key_input._entry.bind("<KeyRelease>", lambda e: self._on_fixed_action_changed(FixedActionType.FOOD))
        self._potion_key_input._entry.bind("<KeyRelease>", lambda e: self._on_fixed_action_changed(FixedActionType.POTION))

    def _select_custom_action(self, name):
        """
        Select a custom action in the action list and update UI highlighting.
        
        Args:
            name: Name of the action to select
        """
        self._selected_custom_action = name
        for k, v in self._custom_actions.items():
            v.configure(fg_color="#44aa77" if k == name else ctk.ThemeManager.theme["CTkButton"]["fg_color"])
    
    def _open_action_dialog(self, dialog_type: ActionDialogType):
        """
        Open the custom action dialog for adding or modifying actions.
        
        Args:
            dialog_type: Type of dialog operation (ADD or MODIFY)
        """
        if dialog_type == ActionDialogType.MODIFY and self._selected_custom_action is None:
            return
        CustomActionDialog(
            self,
            dialog_type,
            self._on_confirm_custom_action_dialog,
            self._controller.get_actions(),
            selected_action=self._selected_custom_action
        )

    def _delete_custom_action(self):
        """
        Delete the currently selected custom action from the controller.
        """
        if self._selected_custom_action is not None:
            self._controller.remove_action(self._selected_custom_action)

    def _on_confirm_custom_action_dialog(self, name: str, dialog_type: ActionDialogType, action: Action):
        """
        Handle confirmation from the custom action dialog by adding or modifying actions.
        
        Args:
            name: Name of the action
            dialog_type: Type of dialog operation (ADD or MODIFY)
            action: Action object containing shortcut and duration
        """
        if dialog_type == ActionDialogType.ADD:
            self._controller.add_action(name, action)
        elif dialog_type == ActionDialogType.MODIFY:
            self._controller.modify_action(self._selected_custom_action, name, action)

    def notify(self, notification_type: Notification, content: ControllerState | Iterable[str]) -> None:
        """
        Handle notifications from the controller to update UI state.
        
        Args:
            notification_type: Type of notification received
            content: Notification content (ControllerState or list of action names)
        """
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

    def _on_fixed_action_changed(self, action_type: FixedActionType):
        """
        Handle changes to fixed action key combinations and update the controller.
        
        Args:
            action_type: Type of action that changed (FixedActionType enum value)
        """
        if action_type == FixedActionType.CONFIRM:
            shortcut = self._confirm_key_input.get_key_combo()
            if shortcut:
                self._controller.set_confirm_action(shortcut)
        elif action_type == FixedActionType.CANCEL:
            shortcut = self._cancel_key_input.get_key_combo()
            if shortcut:
                self._controller.set_cancel_action(shortcut)
        elif action_type == FixedActionType.FOOD:
            shortcut = self._food_key_input.get_key_combo()
            if shortcut:
                self._controller.set_food_action(shortcut)
        elif action_type == FixedActionType.POTION:
            shortcut = self._potion_key_input.get_key_combo()
            if shortcut:
                self._controller.set_potion_action(shortcut)

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
        action_list: dict[str, Action],
        selected_action: str | None = None
    ):
        """
        Initialize the custom action dialog for adding or modifying actions.
        
        Args:
            parent: Parent ActionsTab widget
            dialog_type: Type of dialog operation (ADD or MODIFY)
            callback: Callback function to call when dialog is confirmed
            action_list: Dictionary of existing actions for validation
            selected_action: Name of selected action for modification (optional)
        """
        self._parent = parent
        self._type = dialog_type
        self._callback = callback
        self._selected_custom_action = selected_action
        self._action_list = action_list
        
        # Build reverse mapping using action shortcut as key (since Action objects aren't reliably hashable)
        self._reversed_action_map = {action.shortcut : name for name, action in self._action_list.items()}

        super().__init__(parent)
        self.title(dialog_type + " custom action")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        parent.update_idletasks()
        x = parent.winfo_toplevel().winfo_x() + (parent.winfo_toplevel().winfo_width() // 2) - 200
        y = parent.winfo_toplevel().winfo_y() + (parent.winfo_toplevel().winfo_height() // 2) - 300
        self.geometry(f"400x500+{x}+{y}")

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
                self._shortcut_input.set_key_combo(action_list[selected_action].shortcut)
                self._duration_var.set(str(action_list[selected_action].duration))

        # Text input for macro
        self._macro_label_frame = ctk.CTkFrame(self)
        self._macro_label_frame.pack(pady=(10,2))
        self._macro_label = ctk.CTkLabel(self._macro_label_frame, text="FF XIV Macro")
        self._macro_label.pack(side="left")
        self._macro_info_button = ctk.CTkButton(self._macro_label_frame, text="ⓘ", width=20, height=20, 
                                               font=("Arial", 12), fg_color="transparent", 
                                               text_color="gray")
        self._macro_info_button.pack(side="left", padx=(5,0))
        CTkToolTip(self._macro_info_button, message="Paste your FFXIV macro here.\nDuration will be automatically calculated from <wait.n> tags.\nUse Backspace to clear all content.\nMax 15 lines (FFXIV limit).")
        
        self._macro_text = ctk.CTkTextbox(self, width=360, height=245)  # 15 lines, 20px per line
        self._macro_text.pack(pady=2)

        # Disable manual typing, only allow paste operations
        def on_key_press(event):
            """
            Handle key press events to control macro textbox input behavior.
            Allows paste operations, navigation, and clearing, but blocks manual typing.
            
            Args:
                event: Tkinter key press event
                
            Returns:
                None to allow the key press, "break" to block it
            """
            # Allow paste operations (Ctrl+V) and navigation keys
            if event.state & 0x4:  # Ctrl key is pressed
                if event.keysym.lower() in ['v', 'a', 'c', 'x']:  # Allow paste, select all, copy, cut
                    return None
            # Allow navigation keys
            if event.keysym in ['Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Page_Up', 'Page_Down']:
                return None
            # Clear all content on backspace or delete
            if event.keysym in ['BackSpace', 'Delete']:
                self._macro_text.delete("1.0", "end")
                self._duration_var.set("0")  # Reset duration when cleared
                return "break"
            # Block all other key presses
            return "break"
        
        self._macro_text.bind("<KeyPress>", on_key_press)

        # Limit to 15 lines like FFXIV macros and parse duration after paste
        def limit_lines_and_parse(event=None):
            """
            Limit macro content to 15 lines and parse duration from wait tags.
            Called when macro content changes via paste or other modifications.
            
            Args:
                event: Tkinter event (optional, defaults to None)
            """
            content = self._macro_text.get("1.0", "end-1c")
            lines = content.splitlines()
            if len(lines) > 15:
                self._macro_text.delete("1.0", "end")
                self._macro_text.insert("1.0", "\n".join(lines[:15]))
            # Parse duration after content change
            total_duration = self._calculate_macro_duration(self._macro_text.get("1.0", "end-1c"))
            self._duration_var.set(str(total_duration))
        
        # Bind to paste events and content changes
        self._macro_text.bind("<<Modified>>", limit_lines_and_parse)
        self._macro_text.bind("<Control-v>", lambda e: self.after(1, limit_lines_and_parse))

        self._message_label = ctk.CTkLabel(self, text="", text_color="red")
        self._message_label.pack(pady=2)
        self._btn_frame = ctk.CTkFrame(self)
        self._btn_frame.pack(pady=12)

        ctk.CTkButton(self._btn_frame, text="Confirm", command=self._confirm, width=80).pack(side="left", padx=5)
        ctk.CTkButton(self._btn_frame, text="Cancel", command=self.destroy, width=80).pack(side="left", padx=5)

    def _calculate_macro_duration(self, macro_content: str) -> int:
        """
        Parse FFXIV macro content for <wait.n> tags and calculate total duration.
        Searches each line for wait tags and sums up the wait times.
        
        Args:
            macro_content: Raw macro text content to parse
            
        Returns:
            Total duration in seconds as an integer
        """
        import re
        
        total_duration = 0
        lines = macro_content.splitlines()
        
        for line in lines:
            # Look for <wait.n> pattern where n is an integer
            wait_match = re.search(r'<wait\.(\d+)>', line.lower())
            if wait_match:
                wait_time = int(wait_match.group(1))
                total_duration += wait_time
        
        return total_duration

    def _confirm(self):
        """
        Validate and confirm the action dialog, creating or modifying the action.
        Performs validation on name uniqueness, shortcut uniqueness, and duration format.
        Calls the callback function if validation passes.
        """
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
        
        # Check for duplicate shortcuts            
        duplicate = self._reversed_action_map.get(shortcut)
        if duplicate is not None:
            self._message_label.configure(text=f"Shortcut '{shortcut}' is already used by action {duplicate}.")
            return
        
        if not duration.isdigit():
            self._message_label.configure(text="Duration must be an integer.")
            return

        self._callback(name, self._type, Action(shortcut, int(duration)))
        self.destroy()
        