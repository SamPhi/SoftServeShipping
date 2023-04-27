import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import time
import math
import json, socket
import numpy as np
import gamePlayer
import select_frame
import swingAnimation

class manual_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.name = "manual_frame"
        self.controller = controller
        self.label = tk.Label(self,
                         text="Manual mode",
                         font=controller.title_font, wraplength=(controller.width*7/8), justify="center")
        self.label.pack(side="top", fill="x", pady=(150,10))

        self.label2 = tk.Label(self,
                              text="Use the joystick to move the shipping container!",
                              font=controller.title_2_font, wraplength=(controller.width * 7 / 8), justify="center")
        self.label2.pack(side="top", fill="x", pady=(20,20))

        # create timer label
        self.timerLabel = tk.Label(self, text="", font=controller.timer_font, wraplength=(controller.width*7/8), justify="center")
        self.timerLabel.pack(pady=20)

        # Create cancel button
        self.button1 = tk.Button(self, text="I give up!", height=3, width=20, font=controller.title_2_font,
                                 command=lambda: [controller.buttonState("thankyou"), controller.setCancelTrue()])
        self.button1.pack(pady=20)

        #Create theta label
        self.thetaLabel = tk.Label(self, text="", font=controller.title_font, wraplength=(controller.width*7/8), justify="center")
        self.thetaLabel.pack(pady=(10,10))



        #Create Swing animation
        self.swingAnim = swingAnimation.swingAnimation(controller.width)
        self.swingAnim.pack(pady=(10,10))


    def update(self, time):
        # update label with time. Time is a string in format M:SS
        if self.timerLabel is None:
            self.timerLabel = "error: timerlabel does not exist"
        self.timerLabel.config(text=time)
        #Update theta value to reflect current theta
        #Update theta lable:
        self.thetaLabel.config(text = "θ: "+str('%.2f'%(self.controller.theta)))
        #Update swing animation
        self.swingAnim.drawContainer(self.controller.theta)
        return

