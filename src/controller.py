
"""
Controller module for the XIV Auto Crafter application.
Implements the business logic and coordinates between the model and view components.
"""

import threading
import time
from src.common import *
from src.model import XIVAutoCrafterModel, Recipe, Action

class XIVAutoCrafterController(AutoCrafterControllerInterface):
    """
    Main controller class that manages crafting operations, recipes, and actions.
    Implements the controller interface to coordinate between model and view.
    """

    class CraftingError(Exception):
        """Exception raised when crafting operations encounter errors."""
        pass

    def __init__(self, model : XIVAutoCrafterModel, view : AutoCrafterViewInterface) -> None:
        """
        Initialize the controller with model and view references.
        
        Args:
            model: The model instance for data management
            view: The view instance for UI operations
        """
        self._model = model
        self._view = view
        self._quantity = None
        self._view.set_controller(self)
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._thread = None
        self._state = ControllerState.STOPPED

    def add_recipe(self, name: str, actions: list[Action]) -> bool:
        """
        Add a new recipe to the model.
        
        Args:
            name: Name of the recipe
            actions: List of actions that make up the recipe
            
        Returns:
            True if recipe was added successfully, False if name already exists
        """
        if name in self._model.recipes:
            return False
        self._model.recipes[name] = Recipe(actions)
        self._view.notify(Notification.RECIPE_LIST, self._model.recipes.keys())
        return True
    
    def modify_recipe(self, current_name: str, new_name: str, actions: list[Action]) -> bool:
        """
        Modify an existing recipe or rename it.
        
        Args:
            current_name: Current name of the recipe
            new_name: New name for the recipe
            actions: Updated list of actions for the recipe
            
        Returns:
            True if recipe was modified successfully, False if operation failed
        """
        if current_name not in self._model.recipes:
            return False
        if new_name != current_name:
            if new_name in self._model.recipes:
                return False
            del self._model.recipes[current_name]
        self._model.recipes[new_name] = Recipe(actions)
        self._view.notify(Notification.RECIPE_LIST, self._model.recipes.keys())
        return True

    def remove_recipe(self, name: str) -> bool:
        """
        Remove a recipe from the model.
        
        Args:
            name: Name of the recipe to remove
            
        Returns:
            True if recipe was removed successfully, False if recipe not found
        """
        if name not in self._model.recipes:
            return False
        del self._model.recipes[name]
        self._view.notify(Notification.RECIPE_LIST, self._model.recipes.keys())
        return True

    def get_recipes(self) -> dict[str, Recipe]:
        """
        Get all recipes from the model.
        
        Returns:
            Dictionary mapping recipe names to Recipe objects
        """
        return self._model.recipes

    def get_recipe(self, name: str) -> Recipe | None:
        """
        Get a specific recipe by name.
        
        Args:
            name: Name of the recipe to retrieve
            
        Returns:
            Recipe object if found, None otherwise
        """
        return self._model.recipes.get(name, None)

    def add_action(self, name: str, action: Action) -> bool:
        """
        Add a new action to the model.
        
        Args:
            name: Name of the action
            action: Action object to add
            
        Returns:
            True if action was added successfully, False if name already exists
        """
        if name in self._model.actions:
            return False
        self._model.actions[name] = action
        self._view.notify(Notification.ACTION_LIST, self._model.actions.keys())
        return True
    
    def modify_action(self, current_name: str, new_name: str, action: Action) -> bool:
        """
        Modify an existing action or rename it.
        
        Args:
            current_name: Current name of the action
            new_name: New name for the action
            action: Updated Action object
            
        Returns:
            True if action was modified successfully, False if operation failed
        """
        if current_name not in self._model.actions:
            return False
        if new_name != current_name:
            if new_name in self._model.actions:
                return False
            else:
                self._model.actions[new_name] = action
                del self._model.actions[current_name]            
        else:
            self._model.actions[current_name] = action
        self._view.notify(Notification.ACTION_LIST, self._model.actions.keys())
        return True

    def remove_action(self, name: str) -> bool:
        """
        Remove an action from the model and all recipes that use it.
        
        Args:
            name: Name of the action to remove
            
        Returns:
            True if action was removed successfully, False if action not found
        """
        if name not in self._model.actions:
            return False
        action_to_delete = self._model.actions.pop(name, None)
        for recipe in self._model.recipes.values():
            recipe.actions = [action for action in recipe.actions if action.shortcut != action_to_delete.shortcut]
        self._view.notify(Notification.ACTION_LIST, self._model.actions.keys())
        return True
    
    def get_actions(self) -> dict[str, Action]:
        """
        Get all actions from the model.
        
        Returns:
            Dictionary mapping action names to Action objects
        """
        return self._model.actions
    
    def get_action(self, name: str) -> Action | None:
        """
        Get a specific action by name.
        
        Args:
            name: Name of the action to retrieve
            
        Returns:
            Action object if found, None otherwise
        """
        return self._model.actions.get(name, None)

    def start_crafting(self, quantity: int) -> None:
        """
        Start the crafting process for a specified quantity of items.
        
        Args:
            quantity: Number of items to craft
        """
        if self._state == ControllerState.STOPPED:
            try:
                self._quantity = int(quantity)
                self._state = ControllerState.RUNNING
                self._pause_event.set()

                if not self._model.find_craft_window():
                    raise self.CraftingError("Craft window not found in the game.")
                
                button_center = self._model.find_craft_button()
                if button_center is None:
                    raise self.CraftingError("Craft button not found in the game.")
                
                self._model.click(*button_center)
                self._view.log("Crafting started in the game.")
                if self._model.find_craft_button():
                    raise self.CraftingError("Craft button not found in the game.")

                if not self._thread or not self._thread.is_alive():
                    self._thread = threading.Thread(target=self._crafting_loop, daemon=True)
                    self._thread.start()
                    self._view.log("Crafting started.")

            except ValueError:
                self._view.log("Invalid quantity.", severity=LogSeverity.ERROR)
            except self.CraftingError as e:
                self._view.log(f"{e}", severity=LogSeverity.ERROR)
                self.stop_crafting()

    def stop_crafting(self) -> None:
        """
        Stop the current crafting process and reset the controller state.
        """
        if self._state in (ControllerState.RUNNING, ControllerState.PAUSED):
            self._state = ControllerState.STOPPED
            self._pause_event.set()
            self._view.notify(Notification.CONTROLLER_STATE, ControllerState.STOPPED)

    def pause_crafting(self) -> None:
        """
        Pause the current crafting process.
        """
        if self._state == ControllerState.RUNNING:
            self._state = ControllerState.PAUSED
            self._pause_event.clear()
            self._view.notify(Notification.CONTROLLER_STATE, ControllerState.PAUSED)

    def resume_crafting(self) -> None:
        """
        Resume a paused crafting process.
        """
        if self._state == ControllerState.PAUSED:
            self._state = ControllerState.RUNNING
            self._pause_event.set()
            self._view.notify(Notification.CONTROLLER_STATE, ControllerState.RUNNING)

    def _crafting_loop(self) -> None:
        """
        Internal method that runs the crafting loop in a separate thread.
        Executes the crafting process for the specified quantity.
        """
        for i in range(self._quantity):
            if self._state == ControllerState.STOPPED:
                break
            self._pause_event.wait()
            self._view.log(f"Crafting item {i+1}/{self._quantity}...")
            self._view.set_progress((i+1)/self._quantity)
            time.sleep(2)
        self.stop_crafting()
