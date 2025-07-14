import customtkinter as ctk
from CTkToolTip import *
from enum import Enum
from collections.abc import Iterable
from src.common import AutoCrafterControllerInterface, LogSeverity, ControllerState, Notification


class CraftTab(ctk.CTkFrame):

    class RecipeDialog(Enum):
        ADD = 0
        MODIFY = 1

    def __init__(self, parent, controller : AutoCrafterControllerInterface):
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
        self._add_recipe_btn = ctk.CTkButton(self._top_bar, text="+", width=28, height=24, command=lambda: self._open_recipe_dialog(self.RecipeDialog.ADD))
        self._add_recipe_btn.pack(side="left", padx=2)
        CTkToolTip(self._add_recipe_btn, message="Add a new recipe")
        self._modify_recipe_btn = ctk.CTkButton(self._top_bar, text="✎", width=28, height=24, command=self._modify_recipe)
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

    def _open_recipe_dialog(self, dialog_type: RecipeDialog):

        if dialog_type == self.RecipeDialog.ADD:
            title = "Add Recipe"
            label_text = "Enter recipe name:"
            default_text = ""
        elif dialog_type == self.RecipeDialog.MODIFY:
            title = "Modify Recipe"
            label_text = "Edit recipe name:"
            default_text = self._selected_recipe

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
            # Check for duplicate name
            if name in self._recipes:
                message_label.configure(text="A recipe with this name already exists.")
                return
            self._on_confirm_recipe_dialog(name, dialog, dialog_type)
            
        ctk.CTkButton(btn_frame, text="Confirm", command=confirm, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy, width=80).pack(side="left", padx=5)

    def _on_confirm_recipe_dialog(self, name : str, dialog : ctk.CTkToplevel, dialog_type: RecipeDialog):
        if dialog_type == self.RecipeDialog.ADD:
            if self._controller.add_recipe(name):
                self.log(f"Added recipe: {name}")
                dialog.destroy()

        elif dialog_type == self.RecipeDialog.MODIFY:
            previous_recipe_name = self._selected_recipe
            if self._controller.modify_recipe(self._selected_recipe, name):
                self.log(f"Modified recipe: {previous_recipe_name} to {name}")
                dialog.destroy()
            else:
                self.log(f"Failed to modify recipe: {self._selected_recipe}. It may not exist.", LogSeverity.ERROR)

    def _select_recipe(self, name : str):
        self._selected_recipe = name
        for k,v in self._recipes.items():
            v.configure(fg_color="#44aa77" if k == name else ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.log(f"Selected Recipe {name}")

    def _modify_recipe(self):
        if self._selected_recipe is not None:
            self._open_recipe_dialog(self.RecipeDialog.MODIFY)
        else:
            self.log("No recipe selected to modify.", LogSeverity.WARNING)

    def _delete_recipe(self):
        if self._selected_recipe is not None:
            name = self._selected_recipe
            self._controller.remove_recipe(name)
            self.log(f"Deleted Recipe {name}")
        else:
            self.log("No recipe selected to delete.", LogSeverity.WARNING)

    def _validate_quantity_keypress(self, event):
        # Only allow digits, backspace, and delete
        if event.char.isdigit() or event.keysym in ("BackSpace", "Delete"):
            return None
        return "break"

    def _on_quantity_mousewheel(self, event):
        # Mouse wheel up: increment, down: decrement
        delta = 1 if event.delta > 0 else -1
        current = self._quantity_var.get()
        new_value = max(1, current + delta)
        new_value = min(100, new_value)
        self._quantity_var.set(new_value)
        return "break"

    def set_progress(self, value: float) -> None:
        self._progress.set(value)

    def log(self, message: str, severity: LogSeverity = LogSeverity.INFO) -> None:
        self._log_text.configure(state="normal")
        self._log_text.insert("end", f"[{severity}] {message}\n")
        self._log_text.see("end")
        self._log_text.configure(state="disabled")

    def _start_button_callback(self) -> None:
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
        if not hasattr(self, '_controller') or self._controller is None:
            self.log("No controller is bound to the view.", LogSeverity.ERROR)
            return
        self._controller.stop_crafting()

    def notify(self, notification_type: Notification, content: ControllerState | Iterable[str]) -> None:
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