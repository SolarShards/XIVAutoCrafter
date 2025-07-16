import customtkinter as ctk
from CTkToolTip import *
from enum import Enum
from collections.abc import Iterable
from src.common import AutoCrafterControllerInterface, LogSeverity, ControllerState, Notification
from src.model import Action, Recipe


# Dialog type enum (must be outside the class)
class RecipeDialogType(Enum):
    ADD = 0
    MODIFY = 1

class CraftTab(ctk.CTkFrame):

    def __init__(self, parent, controller : AutoCrafterControllerInterface):
        """
        Initialize the CraftTab frame with recipe management and crafting controls.
        
        Args:
            parent: Parent widget (usually the main application window)
            controller: Controller interface for managing recipes and crafting operations
        """
        super().__init__(parent)
        self._controller = controller
        self._controller_state = ControllerState.STOPPED
        self.pack(fill="both", expand=True)

        self._control_frame = ctk.CTkFrame(self)
        self._control_frame.pack(side="top", fill="x", expand=False, padx=(0, 0), pady=(10,0))
        ctk.CTkLabel(self._control_frame, text="Quantity:").pack(side="left", padx=5)
        self._quantity_var = ctk.IntVar(value=1)
        self._quantity_entry = ctk.CTkEntry(self._control_frame, width=60, textvariable=self._quantity_var)
        self._quantity_entry.pack(side="left", padx=5)
        self._quantity_entry.bind("<KeyPress>", self._validate_quantity_keypress)
        self._quantity_entry.bind("<MouseWheel>", self._on_quantity_mousewheel)
        self._start_button = ctk.CTkButton(self._control_frame, text="Start", command=self._start_button_callback, width=80, height=28)
        self._start_button.pack(side="left", padx=5)
        self._stop_button = ctk.CTkButton(self._control_frame, text="Stop", state="disabled", width=80, height=28)
        self._stop_button.pack(side="left", padx=5)
        self._stop_button.configure(command=self._stop_button_callback)
        self._progress = ctk.CTkProgressBar(self._control_frame, width=200)
        self._progress.set(0)
        self._progress.pack(side="left", fill="x", padx=10)

        self._recipe_frame = ctk.CTkFrame(self, width=170)
        self._recipe_frame.pack(side="left", fill="y", padx=10, pady=10)

        self._top_bar = ctk.CTkFrame(self._recipe_frame)
        self._top_bar.pack(fill="x", pady=(0, 5))
        self._add_recipe_btn = ctk.CTkButton(self._top_bar, text="+", width=28, height=24, command=lambda: self._open_recipe_dialog(RecipeDialogType.ADD))
        self._add_recipe_btn.pack(side="left", padx=2)
        CTkToolTip(self._add_recipe_btn, message="Add a new recipe")
        self._modify_recipe_btn = ctk.CTkButton(self._top_bar, text="✎", width=28, height=24, command=lambda: self._open_recipe_dialog(RecipeDialogType.MODIFY))
        self._modify_recipe_btn.pack(side="left", padx=2)
        CTkToolTip(self._modify_recipe_btn, message="Modify the selected recipe")
        self._delete_recipe_btn = ctk.CTkButton(self._top_bar, text="–", width=28, height=24, command=self._delete_recipe)
        self._delete_recipe_btn.pack(side="left", padx=2)
        CTkToolTip(self._delete_recipe_btn, message="Delete the selected recipe")

        self._recipe_list_frame = ctk.CTkFrame(self._recipe_frame)
        self._recipe_list_frame.pack(fill="both", expand=True)
        self._recipes = {}
        self._selected_recipe = None

        self._log_frame = ctk.CTkFrame(self)
        self._log_frame.pack(side="right", padx=10, pady=10, fill="both", expand=True)
        ctk.CTkLabel(self._log_frame, text="Status / Log:").pack(anchor="w")
        self._log_text = ctk.CTkTextbox(self._log_frame, height=150)
        self._log_text.configure(state="disabled")
        self._log_text.pack(fill="both", expand=True)

    def _open_recipe_dialog(self, dialog_type: RecipeDialogType):
        """
        Open the recipe dialog for adding or modifying recipes.
        
        Args:
            dialog_type: Type of dialog operation (ADD or MODIFY)
        """
        if dialog_type == RecipeDialogType.MODIFY and self._selected_recipe is None:
            self.log("No recipe selected to modify.", LogSeverity.WARNING)
            return
        RecipeDialog(
            self,
            dialog_type,
            self._on_confirm_recipe_dialog,
            self._controller.get_recipes(),
            self._controller.get_actions(),
            selected_recipe=self._selected_recipe
        )

    def _on_confirm_recipe_dialog(self, name: str, dialog_type: RecipeDialogType, actions: list[Action]):
        """
        Handle confirmation from the recipe dialog by adding or modifying recipes.
        
        Args:
            name: Name of the recipe
            dialog_type: Type of dialog operation (ADD or MODIFY)
            actions: List of Action objects that make up the recipe
        """
        if dialog_type == RecipeDialogType.ADD:
            if self._controller.add_recipe(name, actions):
                self.log(f"Added recipe: {name}")
        elif dialog_type == RecipeDialogType.MODIFY:
            previous_recipe_name = self._selected_recipe
            if self._controller.modify_recipe(self._selected_recipe, name, actions):
                self.log(f"Modified recipe: {previous_recipe_name} to {name}")
            else:
                self.log(f"Failed to modify recipe: {self._selected_recipe}. It may not exist.", LogSeverity.ERROR)

    def _select_recipe(self, name : str):
        """
        Select a recipe in the recipe list and update UI highlighting.
        
        Args:
            name: Name of the recipe to select
        """
        self._selected_recipe = name
        for k,v in self._recipes.items():
            v.configure(fg_color="#44aa77" if k == name else ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.log(f"Selected Recipe {name}")

    def _modify_recipe(self):
        """
        Open the modify recipe dialog for the currently selected recipe.
        """
        if self._selected_recipe is not None:
            self._open_recipe_dialog(RecipeDialogType.MODIFY)
        else:
            self.log("No recipe selected to modify.", LogSeverity.WARNING)

    def _delete_recipe(self):
        """
        Delete the currently selected recipe from the controller.
        """
        if self._selected_recipe is not None:
            name = self._selected_recipe
            self._controller.remove_recipe(name)
            self.log(f"Deleted Recipe {name}")
        else:
            self.log("No recipe selected to delete.", LogSeverity.WARNING)

    def _validate_quantity_keypress(self, event):
        """
        Validate key presses in the quantity entry to only allow digits and control keys.
        
        Args:
            event: Tkinter key press event
            
        Returns:
            None to allow the key press, "break" to block it
        """
        # Only allow digits, backspace, and delete
        if event.char.isdigit() or event.keysym in ("BackSpace", "Delete"):
            return None
        return "break"

    def _on_quantity_mousewheel(self, event):
        """
        Handle mouse wheel events on the quantity entry to increment/decrement values.
        
        Args:
            event: Tkinter mouse wheel event
            
        Returns:
            "break" to prevent default scroll behavior
        """
        # Mouse wheel up: increment, down: decrement
        delta = 1 if event.delta > 0 else -1
        current = self._quantity_var.get()
        new_value = max(1, current + delta)
        new_value = min(100, new_value)
        self._quantity_var.set(new_value)
        return "break"

    def set_progress(self, value: float) -> None:
        """
        Update the progress bar with the given value.
        
        Args:
            value: Progress value between 0.0 and 1.0
        """
        self._progress.set(value)

    def log(self, message: str, severity: LogSeverity = LogSeverity.INFO) -> None:
        """
        Add a log message to the log textbox with severity indicator.
        
        Args:
            message: Message text to log
            severity: Severity level of the message (defaults to INFO)
        """
        self._log_text.configure(state="normal")
        self._log_text.insert("end", f"[{severity}] {message}\n")
        self._log_text.see("end")
        self._log_text.configure(state="disabled")

    def _start_button_callback(self) -> None:
        """
        Handle start button clicks to start, pause, or resume crafting operations.
        Button behavior changes based on current controller state.
        """
        if not hasattr(self, '_controller') or self._controller is None:
            self.log("No controller is bound to the view.", LogSeverity.ERROR)
            return
        if self._controller_state == ControllerState.RUNNING:
            self._controller.pause_crafting()
        elif self._controller_state == ControllerState.PAUSED:
            self._controller.resume_crafting()
        else:
            self._controller.start_crafting(self._quantity_var.get())


    def _stop_button_callback(self) -> None:
        """
        Handle stop button clicks to stop crafting operations.
        """
        if not hasattr(self, '_controller') or self._controller is None:
            self.log("No controller is bound to the view.", LogSeverity.ERROR)
            return
        self._controller.stop_crafting()

    def notify(self, notification_type: Notification, content: ControllerState | Iterable[str]) -> None:
        """
        Handle notifications from the controller to update UI state.
        
        Args:
            notification_type: Type of notification received
            content: Notification content (ControllerState or list of recipe names)
        """
        if notification_type == Notification.CONTROLLER_STATE:
            if not isinstance(content, ControllerState):
                raise TypeError("Wrong notiofication type (expected ControllerState)")
            self._controller_state = content
            if content == ControllerState.STOPPED:
                self._stop_button.configure(state="disabled")
                self._start_button.configure(text="Start")
                self._progress.set(0)
                self.log("Crafting stopped.")
            elif content == ControllerState.RUNNING:
                self._start_button.configure(text="Pause")
                self._stop_button.configure(state="normal")
                self.log("Crafting in progress...")
            elif content == ControllerState.PAUSED:
                self._start_button.configure(text="Resume")
                self.log("Crafting paused.")
        
        if notification_type == Notification.RECIPE_LIST:
            if not isinstance(content, Iterable):
                raise TypeError("Wrong notification type (expected list of Recipe names)")
            # Update buttons
            for btn in self._recipes.values():
                btn.destroy()
            self._recipes.clear()
            for name in content:
                btn = ctk.CTkButton(self._recipe_list_frame, text=name, width=140, command=lambda n=name: self._select_recipe(n))
                btn.pack(pady=2, fill="x")
                self._recipes[name] = btn
            self._selected_recipe = None
            self.log("Recipe list updated.")

class RecipeDialog(ctk.CTkToplevel):
    def __init__(
        self,
        parent: CraftTab,
        dialog_type: RecipeDialogType,
        callback,
        recipes: dict[str, Recipe],
        actions: dict[str, Action],
        selected_recipe: str | None = None
    ):
        """
        Initialize the recipe dialog for adding or modifying recipes.
        
        Args:
            parent: Parent CraftTab widget
            dialog_type: Type of dialog operation (ADD or MODIFY)
            callback: Callback function to call when dialog is confirmed
            recipes: Dictionary of existing recipes for validation
            actions: Dictionary of available actions for recipe creation
            selected_recipe: Name of selected recipe for modification (optional)
        """
        super().__init__(parent)
        self._type = dialog_type
        self._callback = callback
        self._selected_recipe = selected_recipe
        self._recipes = recipes
        self._actions = actions
        # Build reverse mapping using action shortcut as key (since Action objects aren't reliably hashable)
        self._reversed_action_map = {action.shortcut: name for name, action in self._actions.items()}

        self._recipe_actions = self._recipes.get(selected_recipe).actions if selected_recipe else []

        self.title(("Add" if dialog_type == RecipeDialogType.ADD else "Modify") + " Recipe")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        parent.update_idletasks()
        x = parent.winfo_toplevel().winfo_x() + (parent.winfo_toplevel().winfo_width() // 2) - 250
        y = parent.winfo_toplevel().winfo_y() + (parent.winfo_toplevel().winfo_height() // 2) - 180
        self.geometry(f"500x500+{x}+{y}")

        label_text = "Enter recipe name:" if dialog_type == RecipeDialogType.ADD else "Edit recipe name:"
        default_text = "" if dialog_type == RecipeDialogType.ADD else selected_recipe

        ctk.CTkLabel(self, text=label_text).pack(pady=10)
        self._entry = ctk.CTkEntry(self, width=200)
        self._entry.pack(pady=5)
        self._entry.focus()
        if default_text:
            self._entry.insert(0, default_text)

        # Action selection frames
        action_frame = ctk.CTkFrame(self)
        action_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self._recipe_actions_frame = ctk.CTkFrame(action_frame)
        self._recipe_actions_frame.pack(side="left", fill="both", expand=True, padx=(0,10))
        ctk.CTkLabel(self._recipe_actions_frame, text="Recipe Actions").pack()
        self._recipe_actions_list = ctk.CTkScrollableFrame(self._recipe_actions_frame)
        self._recipe_actions_list.pack(fill="both", expand=True)

        self._available_actions_frame = ctk.CTkFrame(action_frame)
        self._available_actions_frame.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(self._available_actions_frame, text="Available Actions").pack()
        self._available_actions_list = ctk.CTkScrollableFrame(self._available_actions_frame)
        self._available_actions_list.pack(fill="both", expand=True)

        self._message_label = ctk.CTkLabel(self, text="", text_color="red")
        self._message_label.pack(pady=2)
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Confirm", command=self._confirm, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, width=80).pack(side="left", padx=5)

        # Populate recipe actions
        for idx, recipe_action in enumerate(self._recipe_actions):
            action_name = self._reversed_action_map.get(recipe_action.shortcut, None)
            btn = ctk.CTkButton(self._recipe_actions_list, text=action_name, width=160, command=lambda i=idx: self._remove_action_from_recipe(i))
            btn.pack(pady=2, fill="x")
        # Populate available actions
        for action_name, action in self._actions.items():
            btn = ctk.CTkButton(self._available_actions_list, text=action_name, width=160, command=lambda n=action_name, a=action: self._add_action_to_recipe(n,a))
            btn.pack(pady=2, fill="x")

    def _remove_action_from_recipe(self, idx):
        """
        Remove an action from the recipe at the specified index.
        
        Args:
            idx: Index of the action to remove from the recipe
        """
        self._recipe_actions_list.winfo_children()[idx].destroy()
        del self._recipe_actions[idx]
        for idx, button in enumerate(self._recipe_actions_list.winfo_children()[idx:]):
            button.configure(command=lambda i=idx: self._remove_action_from_recipe(i))

    def _add_action_to_recipe(self, action_name, action):
        """
        Add an action to the recipe and update the UI.
        
        Args:
            action_name: Display name of the action
            action: Action object to add to the recipe
        """
        btn = ctk.CTkButton(self._recipe_actions_list, text=action_name, width=160, command=lambda i=len(self._recipe_actions): self._remove_action_from_recipe(i))
        self._recipe_actions.append(action)
        btn.pack(pady=2, fill="x")

    def _confirm(self):
        """
        Validate and confirm the recipe dialog, creating or modifying the recipe.
        Performs validation on name uniqueness and calls the callback function if validation passes.
        """
        name = self._entry.get().strip()
        if not name:
            self._message_label.configure(text="Name cannot be empty.")
            return
        if name in self._recipes and name != self._selected_recipe:
            self._message_label.configure(text="A recipe with this name already exists.")
            return
        self._callback(name, self._type, self._recipe_actions)
        self.destroy()