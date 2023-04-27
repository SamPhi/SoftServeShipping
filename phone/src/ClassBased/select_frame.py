import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import time
import math
import json, socket
import numpy as np
import gamePlayer
import scoresTable

# Select frame class: used to define and update
class select_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.name = "select_frame"
        self.controller = controller

        # Label for the welcome text:
        self.label = tk.Label(self,
                         text="Welcome to soft serve shipping!",
                         font=controller.title_font, wraplength=(controller.width*7/8), justify="center")
        self.label.pack(side="top", fill="x", pady=50)

        #Buttons for manual and auto mode:
        self.button1 = tk.Button(self, text="Manual Mode", height = 3, width = 20,font=controller.title_2_font,
                            command=lambda: controller.changeState("manual"))
        self.button2 = tk.Button(self, text="Automatic Mode", height = 3, width = 20, font=controller.title_2_font, command=lambda: controller.changeState("automatic"))

        self.button1.pack(pady=10)
        self.button2.pack(pady=10)

        #Table to show scores:
        self.table = scoresTable.ScoresTable(self)
        self.table.pack(fill=tk.BOTH, expand=True,pady=20)

    def update(self, time):
        self.table.update_scores(self.controller.scoreArr)
        return
