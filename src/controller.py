
import threading
import time
from src.common import *
from src.model import XIVAutoCrafterModel, Recipe, Action

class XIVAutoCrafterController(AutoCrafterControllerInterface):

    class CraftingError(Exception):
        pass

    def __init__(self, model : XIVAutoCrafterModel, view : AutoCrafterViewInterface) -> None:
        self._model = model
        self._view = view
        self._quantity = None
        self._view.set_controller(self)
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._thread = None
        self._state = ControllerState.STOPPED

    def add_recipe(self, name: str) -> bool:
        if name in self._model.recipes:
            return False
        self._model.recipes[name] = Recipe()
        self._view.notify(Notification.RECIPE_LIST, self._model.recipes.keys())
        return True
    
    def modify_recipe(self, current_name: str, new_name: str) -> bool:
        if new_name == current_name:
            return True
        if current_name not in self._model.recipes or new_name in self._model.recipes:
            return False
        self._model.recipes[new_name] = self._model.recipes[current_name]
        del self._model.recipes[current_name]
        self._view.notify(Notification.RECIPE_LIST, self._model.recipes.keys())
        return True

    def remove_recipe(self, name: str) -> bool:
        if name not in self._model.recipes:
            return False
        del self._model.recipes[name]
        self._view.notify(Notification.RECIPE_LIST, self._model.recipes.keys())
        return True

    def add_action(self, name: str, shortcut : str, duration : int) -> bool:
        if name in self._model.actions:
            return False
        self._model.actions[name] = Action(shortcut, duration)
        self._view.notify(Notification.ACTION_LIST, self._model.actions.keys())
        return True
    
    def modify_action(self, current_name: str, new_name: str, shortcut : str, duration : int) -> bool:
        if new_name == current_name:
            self._model.actions[current_name] = Action(shortcut, duration)
        if current_name not in self._model.actions or new_name in self._model.actions:
            return False
        self._model.actions[new_name] = Action(shortcut, duration)
        del self._model.actions[current_name]
        self._view.notify(Notification.ACTION_LIST, self._model.actions.keys())
        return True

    def remove_action(self, name: str) -> bool:
        if name not in self._model.actions:
            return False
        del self._model.actions[name]
        self._view.notify(Notification.ACTION_LIST, self._model.actions.keys())
        return True
    
    def get_action(self, name: str) -> tuple[str, int]:
        return self._model.actions[name]._shortcut, self._model.actions[name]._duration if name in self._model.actions else (None, None)

    def start_crafting(self, quantity: int) -> None:
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
        if self._state in (ControllerState.RUNNING, ControllerState.PAUSED):
            self._state = ControllerState.STOPPED
            self._pause_event.set()
            self._view.notify(Notification.CONTROLLER_STATE, ControllerState.STOPPED)

    def pause_crafting(self) -> None:
        if self._state == ControllerState.RUNNING:
            self._state = ControllerState.PAUSED
            self._pause_event.clear()
            self._view.notify(Notification.CONTROLLER_STATE, ControllerState.PAUSED)

    def resume_crafting(self) -> None:
        if self._state == ControllerState.PAUSED:
            self._state = ControllerState.RUNNING
            self._pause_event.set()
            self._view.notify(Notification.CONTROLLER_STATE, ControllerState.RUNNING)

    def _crafting_loop(self) -> None:
        for i in range(self._quantity):
            if self._state == ControllerState.STOPPED:
                break
            self._pause_event.wait()
            self._view.log(f"Crafting item {i+1}/{self._quantity}...")
            self._view.set_progress((i+1)/self._quantity)
            time.sleep(2)
        self.stop_crafting()
