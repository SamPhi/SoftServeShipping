import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import time
import math
import json, socket
import numpy as np
import gamePlayer

# Time class used to track runTime in gamePlayer class
class timer():
    def __init__(self):
        self.time = time.time();  # time in seconds
        self.startToSubtract = 0

    def startTimer(self):
        self.startToSubtract = time.time()

    def resetTimer(self):
        self.startToSubtract = 0

    def getTime(self):
        self.time = time.time() - self.startToSubtract
        return self.time

    def getTimeString(self):
        timeSec = self.getTime()
        minutes = math.floor(timeSec / 60)
        seconds = math.floor(timeSec - minutes * 60)
        timeString = f"{minutes:02d}" + ":" + f"{seconds:02d}"
        return timeString
