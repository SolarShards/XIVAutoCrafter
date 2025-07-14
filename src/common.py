from abc import ABC, abstractmethod
import customtkinter as ctk
from enum import StrEnum, Enum

class LogSeverity(StrEnum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"

class ControllerState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"

class Notification(Enum):
    CONTROLLER_STATE = "controller_state"
    RECIPE_LIST = "recipe_list"
    ACTION_LIST = "action_list"

class AutoCrafterControllerInterface(ABC):
    def __init__(self, *args, **kwargs):
        if type(self) is AutoCrafterControllerInterface:
            raise TypeError("AutoCrafterControllerInterface is an abstract class and cannot be instantiated directly.")
        super().__init__(*args, **kwargs)

    @abstractmethod
    def add_recipe(self, name: str) -> bool:
        pass

    @abstractmethod
    def modify_recipe(self, current_name: str, new_name: str) -> bool:
        pass

    @abstractmethod
    def remove_recipe(self, name: str) -> bool:
        pass

    @abstractmethod
    def add_action(self, name: str) -> bool:
        pass

    @abstractmethod
    def modify_action(self, current_name: str, new_name: str) -> bool:
        pass

    @abstractmethod
    def remove_action(self, name: str) -> bool:
        pass

    @abstractmethod
    def start_crafting(self, quantity: int) -> None:
        pass

    @abstractmethod
    def stop_crafting(self) -> None:
        pass

    @abstractmethod
    def pause_crafting(self) -> None:
        pass

    @abstractmethod
    def resume_crafting(self) -> None:
        pass

class AutoCrafterViewInterface(ctk.CTk, ABC):
    def __init__(self, *args, **kwargs):
        if type(self) is AutoCrafterViewInterface:
            raise TypeError("AutoCrafterViewInterface is an abstract class and cannot be instantiated directly.")
        super().__init__(*args, **kwargs)

    @abstractmethod
    def log(self, message: str) -> None:
        pass

    @abstractmethod
    def set_progress(self, value: float) -> None:
        pass

    @abstractmethod
    def notify(self, obj: ControllerState | list[str]) -> None:
        pass

    @abstractmethod
    def set_controller(self, controller: AutoCrafterControllerInterface) -> None:
        pass
