import customtkinter as ctk
from CTkToolTip import *
from collections.abc import Iterable
from .ui.craft_tab import CraftTab
from .ui.actions_tab import ActionsTab
from src.common import *

class XIVAutoCrafterView(AutoCrafterViewInterface):

    def __init__(self) -> None:
        super().__init__()

        self.title("XIV Auto Crafter")
        self.geometry("600x500")
        self.resizable(False, False)
        
        self._tabview = ctk.CTkTabview(self, width=600, height=500)
        self._tabview.pack(fill="both", expand=True)

    def set_controller(self, controller: AutoCrafterControllerInterface) -> None:
        self._controller = controller
        self._tabview.add("Craft")
        self._craft_tab = CraftTab(self._tabview.tab("Craft"), controller)
        self._tabview.add("Actions")
        self._actions_tab = ActionsTab(self._tabview.tab("Actions"), controller)

    def set_progress(self, value: float) -> None:
        self._craft_tab.set_progress(value)

    def log(self, message: str, severity: LogSeverity = LogSeverity.INFO) -> None:
        self._craft_tab.log(message, severity)

    def notify(self, notification_type: Notification, content: ControllerState | Iterable[str]) -> None:
        self._craft_tab.notify(notification_type, content)
        self._actions_tab.notify(notification_type, content)