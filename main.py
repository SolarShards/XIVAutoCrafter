"""
Main entry point for the XIV Auto Crafter application.
Sets up the MVC architecture and starts the application.
"""

from src.view import XIVAutoCrafterView
from src.controller import XIVAutoCrafterController
from src.model import XIVAutoCrafterModel
import customtkinter as ctk

if __name__ == "__main__":
    """
    Initialize and run the XIV Auto Crafter application.
    Creates the model, view, and controller instances and starts the main loop.
    """
    ctk.set_appearance_mode("dark")
    model = XIVAutoCrafterModel()
    view = XIVAutoCrafterView()
    controller = XIVAutoCrafterController(model, view)
    view.mainloop()