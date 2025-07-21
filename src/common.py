"""
Common module for the XIV Auto Crafter application.
Contains shared interfaces, enums, and abstract base classes used throughout the application.
"""

from abc import ABC, abstractmethod
import customtkinter as ctk
from enum import StrEnum, Enum

from src.model import Action, Recipe

class LogSeverity(StrEnum):
    """Enumeration for log message severity levels."""
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"

class ControllerState(Enum):
    """Enumeration for controller state values."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"

class Notification(Enum):
    """Enumeration for notification types sent between components."""
    CONTROLLER_STATE = "controller_state"
    RECIPE_LIST = "recipe_list"
    ACTION_LIST = "action_list"
    FIXED_ACTIONS = "fixed_actions"

class AutoCrafterControllerInterface(ABC):
    """
    Abstract base class defining the interface for controller implementations.
    Provides contract for recipe management, action management, and crafting operations.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the controller interface.
        Prevents direct instantiation of abstract class.
        """
        if type(self) is AutoCrafterControllerInterface:
            raise TypeError("AutoCrafterControllerInterface is an abstract class and cannot be instantiated directly.")
        super().__init__(*args, **kwargs)

    @abstractmethod
    def add_recipe(self, name: str, action_names: list[str], use_food: bool = False, use_potion: bool = False, use_hq_ingredients: bool = False) -> bool:
        """Add a new recipe to the system."""
        pass

    @abstractmethod
    def modify_recipe(self, current_name: str, new_name: str, action_names: list[str], use_food: bool = False, use_potion: bool = False, use_hq_ingredients: bool = False) -> bool:
        """Modify an existing recipe."""
        pass

    @abstractmethod
    def remove_recipe(self, name: str) -> bool:
        """Remove a recipe from the system."""
        pass

    @abstractmethod
    def get_recipes(self) -> dict[str, Recipe]:
        """Get all available recipes."""
        pass

    @abstractmethod
    def get_recipe(self, name: str) -> Recipe | None:
        """Get a specific recipe by name."""
        pass

    @abstractmethod
    def add_action(self, name: str, action: Action) -> bool:
        """Add a new action to the system."""
        pass

    @abstractmethod
    def modify_action(self, current_name: str, new_name: str, action: Action) -> bool:
        """Modify an existing action."""
        pass

    @abstractmethod
    def remove_action(self, name: str) -> bool:
        """Remove an action from the system."""
        pass
    
    @abstractmethod
    def get_actions(self) -> dict[str, Action]:
        """Get all available actions."""
        pass

    @abstractmethod
    def get_action(self, name: str) -> Action | None:
        """Get a specific action by name."""
        pass

    @abstractmethod
    def start_crafting(self, quantity: int, recipe_name: str) -> None:
        """Start the crafting process."""
        pass

    @abstractmethod
    def stop_crafting(self) -> None:
        """Stop the crafting process."""
        pass

    @abstractmethod
    def pause_crafting(self) -> None:
        """Pause the crafting process."""
        pass

    @abstractmethod
    def resume_crafting(self) -> None:
        """Resume the crafting process."""
        pass

    @abstractmethod
    def set_confirm_action(self, shortcut: str) -> None:
        """Set the confirm action shortcut."""
        pass

    @abstractmethod
    def set_cancel_action(self, shortcut: str) -> None:
        """Set the cancel action shortcut."""
        pass

    @abstractmethod
    def set_food_action(self, shortcut: str) -> None:
        """Set the food action shortcut."""
        pass

    @abstractmethod
    def set_potion_action(self, shortcut: str) -> None:
        """Set the potion action shortcut."""
        pass

    @abstractmethod
    def set_recipe_book_action(self, shortcut: str) -> None:
        """Set the recipe book action shortcut."""
        pass

    @abstractmethod
    def set_up_action(self, shortcut: str) -> None:
        """Set the up movement action shortcut."""
        pass

    @abstractmethod
    def set_down_action(self, shortcut: str) -> None:
        """Set the down movement action shortcut."""
        pass

    @abstractmethod
    def set_left_action(self, shortcut: str) -> None:
        """Set the left movement action shortcut."""
        pass

    @abstractmethod
    def set_right_action(self, shortcut: str) -> None:
        """Set the right movement action shortcut."""
        pass

class AutoCrafterViewInterface(ctk.CTk, ABC):
    """
    Abstract base class defining the interface for view implementations.
    Extends customtkinter's CTk class and provides contract for UI operations.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the view interface.
        Prevents direct instantiation of abstract class.
        """
        if type(self) is AutoCrafterViewInterface:
            raise TypeError("AutoCrafterViewInterface is an abstract class and cannot be instantiated directly.")
        super().__init__(*args, **kwargs)

    @abstractmethod
    def log(self, message: str, severity: LogSeverity = LogSeverity.INFO) -> None:
        """Display a log message with specified severity."""
        pass

    @abstractmethod
    def set_progress(self, value: float) -> None:
        """Update the progress display."""
        pass

    @abstractmethod
    def notify(self, notification_type: Notification, content: ControllerState | list[str] | dict[str, str]) -> None:
        """Handle notifications from the controller."""
        pass

    @abstractmethod
    def set_controller(self, controller: AutoCrafterControllerInterface) -> None:
        """Set the controller reference for the view."""
        pass
