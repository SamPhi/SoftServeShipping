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
import swingAnimation


class automatic_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.name = "automatic_frame"
        self.controller = controller
        self.label = tk.Label(self,
                         text="Automatic mode",
                         font=controller.title_font, wraplength=(controller.width*7/8), justify="center")
        self.label.pack(side="top", fill="x", pady=(150,10))

        self.label2 = tk.Label(self,
                               text="Let the machine do its thing!",
                               font=controller.title_2_font, wraplength=(controller.width * 7 / 8), justify="center")
        self.label2.pack(side="top", fill="x", pady=(20, 20))

        # create timer label
        self.timerLabel = tk.Label(self, text="", font=controller.timer_font, wraplength=(controller.width*7/8), justify="center")
        self.timerLabel.pack(pady=20)

        # Create theta label
        self.thetaLabel = tk.Label(self, text="", font=controller.title_font, wraplength=(controller.width*7/8), justify="center")
        self.thetaLabel.pack(pady=20)

        self.button1 = tk.Button(self, text="Cancel",
                            command=lambda: [controller.buttonState("thankyou"),controller.setCancelTrue()])
        self.button1.pack()

        #TODO Add input for x_des, y_des

    def update(self, time):
        # update label with time. Time is a string in format M:SS
        if self.timerLabel is None:
            self.timerLabel = "error: timerlabel does not exist"
        self.timerLabel.config(text=" Time: " + time)
        # Update theta value to reflect current theta
        self.thetaLabel.config(text="Theta = " + str(self.controller.theta))
        return

