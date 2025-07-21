
"""
Controller module for the XIV Auto Crafter application.
Implements the business logic and coordinates between the model and view components.
"""

import threading
import time

from src.common import *
from src.model import XIVAutoCrafterModel, Recipe, Action

# Buff durations (in seconds)
FOOD_DURATION = 30 * 60  # 30 minutes
POTION_DURATION = 15 * 60  # 15 minutes

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
        self._food_time = None
        self._potion_time = None
        
        self._model.load_data()
        self._view.notify(Notification.RECIPE_LIST, self._model.recipes.keys())
        self._view.notify(Notification.ACTION_LIST, self._model.actions.keys())
        
        # Notify view about all fixed action shortcuts as a dictionary
        fixed_actions = {
            "confirm_action": self._model.confirm_action.shortcut,
            "cancel_action": self._model.cancel_action.shortcut,
            "food_action": self._model.food_action.shortcut,
            "potion_action": self._model.potion_action.shortcut,
            "recipe_book_action": self._model.recipe_book_action.shortcut,
            "up_action": self._model.up_action.shortcut,
            "down_action": self._model.down_action.shortcut,
            "left_action": self._model.left_action.shortcut,
            "right_action": self._model.right_action.shortcut
        }
        self._view.notify(Notification.FIXED_ACTIONS, fixed_actions)

    def add_recipe(self, name: str, action_names: list[str], use_food: bool = False, use_potion: bool = False, use_hq_ingredients: bool = False) -> bool:
        """
        Add a new recipe to the model.
        
        Args:
            name: Name of the recipe
            action_names: List of action names that make up the recipe
            use_food: Whether to use food buff for this recipe (defaults to False)
            use_potion: Whether to use potion buff for this recipe (defaults to False)
            use_hq_ingredients: Whether to use HQ ingredients for this recipe (defaults to False)
            
        Returns:
            True if recipe was added successfully, False if name already exists
        """
        if name in self._model.recipes:
            return False
        self._model.recipes[name] = Recipe(action_names, use_food, use_potion, use_hq_ingredients)
        self._model.save_data()
        self._view.notify(Notification.RECIPE_LIST, self._model.recipes.keys())
        return True
    
    def modify_recipe(self, current_name: str, new_name: str, action_names: list[str], use_food: bool = False, use_potion: bool = False, use_hq_ingredients: bool = False) -> bool:
        """
        Modify an existing recipe or rename it.
        
        Args:
            current_name: Current name of the recipe
            new_name: New name for the recipe
            action_names: Updated list of action names for the recipe
            use_food: Whether to use food buff for this recipe (defaults to False)
            use_potion: Whether to use potion buff for this recipe (defaults to False)
            use_hq_ingredients: Whether to use HQ ingredients for this recipe (defaults to False)
            
        Returns:
            True if recipe was modified successfully, False if operation failed
        """
        if current_name not in self._model.recipes:
            return False
        if new_name != current_name:
            if new_name in self._model.recipes:
                return False
            del self._model.recipes[current_name]
        self._model.recipes[new_name] = Recipe(action_names, use_food, use_potion, use_hq_ingredients)
        self._model.save_data()
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
        self._model.save_data()
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
        self._model.save_data()
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
        self._model.save_data()
        self._view.notify(Notification.ACTION_LIST, self._model.actions.keys())
        return True

    def remove_action(self, name: str) -> bool:
        """
        Remove an action from the model and replace it with "Deleted action" in all recipes that use it.
        
        Args:
            name: Name of the action to remove
            
        Returns:
            True if action was removed successfully, False if action not found
        """
        if name not in self._model.actions:
            return False
        action_to_delete = self._model.actions.pop(name, None)
        for recipe in self._model.recipes.values():
            recipe.action_names = [
                f"Deleted: {name}" if action_name == name else action_name 
                for action_name in recipe.action_names
            ]
        self._model.save_data()
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

    def start_crafting(self, quantity: int, recipe_name: str) -> None:
        """
        Start the crafting process for a specified quantity of items using the given recipe.
        
        Args:
            quantity: Number of items to craft
            recipe_name: Name of the recipe to use for crafting
        """
        if self._state == ControllerState.STOPPED:
            try:
                # Validate recipe exists
                if recipe_name not in self._model.recipes:
                    raise self.CraftingError(f"Recipe '{recipe_name}' not found.")
                
                self._quantity = int(quantity)
                self._selected_recipe = recipe_name  # Store for the crafting loop
                self._state = ControllerState.RUNNING
                self._pause_event.set()
                self._view.notify(Notification.CONTROLLER_STATE, self._state)

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
            self._view.notify(Notification.CONTROLLER_STATE, self._state)

    def pause_crafting(self) -> None:
        """
        Pause the current crafting process.
        """
        if self._state == ControllerState.RUNNING:
            self._state = ControllerState.PAUSED
            self._pause_event.clear()
            self._view.notify(Notification.CONTROLLER_STATE, self._state)

    def resume_crafting(self) -> None:
        """
        Resume a paused crafting process.
        """
        if self._state == ControllerState.PAUSED:
            self._state = ControllerState.RUNNING
            self._pause_event.set()
            self._view.notify(Notification.CONTROLLER_STATE, self._state)

    def _confirm(self) -> None:
        """
        Internal method to keep the comfirm action from stopping the crafting process.
        """
        if self._model.find_craft_window():
            self._model.confirm_action.execute()
        
    def _manage_buffs(self) -> bool:
        """
        Internal method to manage food and potion buffs during crafting.
        Checks if buffs are active and reapplies them if necessary.
        """
        if not self._model.food_action.shortcut:
            raise self.CraftingError("Food action not configured.")
        if not self._model.potion_action.shortcut:
            raise self.CraftingError("Potion action not configured.")
        
        must_eat = self._food_time is None or (time.time() - self._food_time) > FOOD_DURATION
        must_drink = self._potion_time is None or (time.time() - self._potion_time) > POTION_DURATION
        
        # Check food buff
        if must_eat or must_drink:
            if self._model.find_craft_window():
                self._model.recipe_book_action.execute()
                time.sleep(1)  # Allow time for the character to get up
            if must_eat:
                self._view.log("Using food (30 minute buff)...")
                self._food_time = time.time()
                self._model.food_action.execute()
            if must_drink:
                self._view.log("Using potion (15 minute buff)...")
                self._potion_time = time.time()
                self._model.potion_action.execute()
            self._model.recipe_book_action.execute()
            return True
        return False

    def _set_hq(self):
        """
        Inputs to set the all ingredients in HQ.
        """
        self._model.down_action.execute()
        self._model.down_action.execute()
        self._model.right_action.execute()
        self._model.down_action.execute()
        self._model.confirm_action.execute()
        self._model.up_action.execute()
        self._model.up_action.execute()
        self._model.up_action.execute()

    def _crafting_loop(self) -> None:
        """
        Internal method that runs the crafting loop in a separate thread.
        Executes the crafting process for the specified quantity with food/potion support.
        """
        if not self._selected_recipe or not (recipe := self._model.recipes.get(self._selected_recipe)):
            error_msg = "No recipe selected for crafting." if not self._selected_recipe else f"Recipe '{self._selected_recipe}' not found."
            self._view.log(error_msg, severity=LogSeverity.ERROR)
            self.stop_crafting()
            return
        
        if self._model.find_craft_window():
            self._model.recipe_book_action.execute()

        buffed = False

        # Main crafting loop
        for i in range(self._quantity):

            if self._state == ControllerState.STOPPED:
                break
            self._pause_event.wait()

            if not self._model.find_craft_window():
                self._view.log("Waiting for craft window to be ready...", severity=LogSeverity.INFO)
                while not self._model.find_craft_window():
                    if self._state == ControllerState.STOPPED:
                        break
                    self._pause_event.wait(1)
                    self._model.recipe_book_action.execute()

            if recipe.use_food or recipe.use_potion:
                buffed = self._manage_buffs()
            self._confirm()
            self._confirm()
            self._confirm()
            if recipe.use_hq_ingredients and (buffed or i == 0):
                self._set_hq()

            self._confirm()

            self._view.log(f"Crafting item {i+1}/{self._quantity}...")

            # Execute the recipe actions
            time.sleep(1)  # Allow time for the character to sit down
            recipe.execute(self._model.actions)

            self._view.set_progress((i+1)/self._quantity)

            from_scratch = False

        self.stop_crafting()

    def set_confirm_action(self, shortcut: str) -> None:
        """
        Set the confirm action shortcut in the model.
        
        Args:
            shortcut: The key combination for confirming actions
        """
        self._model.confirm_action.shortcut = shortcut
        self._model.save_data()

    def set_cancel_action(self, shortcut: str) -> None:
        """
        Set the cancel action shortcut in the model.
        
        Args:
            shortcut: The key combination for cancelling actions
        """
        self._model.cancel_action.shortcut = shortcut
        self._model.save_data()

    def set_food_action(self, shortcut: str) -> None:
        """
        Set the food action shortcut in the model.
        
        Args:
            shortcut: The key combination for consuming food
        """
        self._model.food_action.shortcut = shortcut
        self._model.save_data()

    def set_potion_action(self, shortcut: str) -> None:
        """
        Set the potion action shortcut in the model.
        
        Args:
            shortcut: The key combination for drinking a CP potion
        """
        self._model.potion_action.shortcut = shortcut
        self._model.save_data()

    def set_recipe_book_action(self, shortcut: str) -> None:
        """
        Set the recipe book action shortcut in the model.
        
        Args:
            shortcut: The key combination for opening/closing the recipe book
        """
        self._model.recipe_book_action.shortcut = shortcut
        self._model.save_data()

    def set_up_action(self, shortcut: str) -> None:
        """
        Set the up movement action shortcut in the model.
        
        Args:
            shortcut: The key combination for moving up
        """
        self._model.up_action.shortcut = shortcut
        self._model.save_data()

    def set_down_action(self, shortcut: str) -> None:
        """
        Set the down movement action shortcut in the model.
        
        Args:
            shortcut: The key combination for moving down
        """
        self._model.down_action.shortcut = shortcut
        self._model.save_data()

    def set_left_action(self, shortcut: str) -> None:
        """
        Set the left movement action shortcut in the model.
        
        Args:
            shortcut: The key combination for moving left
        """
        self._model.left_action.shortcut = shortcut
        self._model.save_data()

    def set_right_action(self, shortcut: str) -> None:
        """
        Set the right movement action shortcut in the model.
        
        Args:
            shortcut: The key combination for moving right
        """
        self._model.right_action.shortcut = shortcut
        self._model.save_data()
