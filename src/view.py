"""
View module for the XIV Auto Crafter application.
Implements the main application window and coordinates UI components.
"""

import customtkinter as ctk
from CTkToolTip import *
from collections.abc import Iterable
from .ui.craft_tab import CraftTab
from .ui.actions_tab import ActionsTab
from src.common import *

class XIVAutoCrafterView(AutoCrafterViewInterface):
    """
    Main view class that manages the application window and tab system.
    Implements the view interface to coordinate with the controller.
    """

    def __init__(self) -> None:
        """
        Initialize the main application window and tab container.
        """
        super().__init__()

        self.title("XIV Auto Crafter")
        self.geometry("600x500")
        self.resizable(False, False)
        
        self._tabview = ctk.CTkTabview(self, width=600, height=500)
        self._tabview.pack(fill="both", expand=True)

    def set_controller(self, controller: AutoCrafterControllerInterface) -> None:
        """
        Set the controller reference and initialize the tab components.
        
        Args:
            controller: The controller instance to coordinate with
        """
        self._controller = controller
        self._tabview.add("Craft")
        self._craft_tab = CraftTab(self._tabview.tab("Craft"), controller)
        self._tabview.add("Actions")
        self._actions_tab = ActionsTab(self._tabview.tab("Actions"), controller)

    def set_progress(self, value: float) -> None:
        """
        Update the progress bar in the craft tab.
        
        Args:
            value: Progress value between 0.0 and 1.0
        """
        self._craft_tab.set_progress(value)

    def log(self, message: str, severity: LogSeverity = LogSeverity.INFO) -> None:
        """
        Add a log message to the craft tab's log display.
        
        Args:
            message: The message to log
            severity: The severity level of the message (defaults to INFO)
        """
        self._craft_tab.log(message, severity)

    def notify(self, notification_type: Notification, content: ControllerState | Iterable[str]) -> None:
        """
        Send notifications to all tab components.
        
        Args:
            notification_type: The type of notification to send
            content: The content or data associated with the notification
        """
        self._craft_tab.notify(notification_type, content)
        self._actions_tab.notify(notification_type, content)