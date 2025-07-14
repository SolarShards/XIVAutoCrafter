from src.view import XIVAutoCrafterView
from src.controller import XIVAutoCrafterController
from src.model import XIVAutoCrafterModel
import customtkinter as ctk

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    model = XIVAutoCrafterModel()
    view = XIVAutoCrafterView()
    controller = XIVAutoCrafterController(model, view)
    view.mainloop()