import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import time
import math
import json, socket
import numpy as np
import gamePlayer
import select_frame
import manual_frame
from PIL import ImageTk
from PIL import Image


class thankyou_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.name = "thankyou_frame"
        self.controller = controller
        self.label = tk.Label(self,
                         text="Thank you for playing! Please wait whilst the machine homes itself for the next run",
                         font=controller.title_font, wraplength=(controller.width*7/8), justify="center")
        self.label.pack(side="top", fill="x", pady=100)
        # self.button1 = tk.Button(self, text="Homed",
        #                     command=lambda: controller.buttonState("select"))
        # self.button1.pack()

        # Create an object of tkinter ImageTk
        self.img = ImageTk.PhotoImage(Image.open("prof.png"))

        # Create a Label Widget to display the text or Image
        self.imglabel = tk.Label(self, image=self.img)
        self.imglabel.pack()

    def update(self, time):
        ##self.controller.setCancelFalse()
        return
