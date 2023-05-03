import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import time
import math
import json, socket
import numpy as np
import gamePlayer
import select_frame
import automatic_frame
import manual_frame
import thankyou_frame
import swingAnimation
import scoresTable
import timer


class gamePlayer(tk.Tk):
    def __init__(self):
        ##Initliaize Tk properties using Tk.init() function
        tk.Tk.__init__(self)
        # Set fonts
        self.title_font = tkfont.Font(family='Helvetica', size=36, weight="bold", slant="italic")
        self.title_2_font = tkfont.Font(family='Helvetica', size=24, slant="italic")
        self.text_font_bold = tkfont.Font(family='Helvetica', size=18, weight="bold")
        self.text_font = tkfont.Font(family='Helvetica', size=18, slant="italic")
        self.timer_font = tkfont.Font(family='Helvetica', size=30, slant="italic")


        # initialize state variables
        self.lastState = "select"
        self.cancel = False
        self.x_des = 0  # Desired x position - set default to target location for actual thing
        self.y_des = 0  # desired y position - set default to target location for actual thing
        self.lastRunTime = 0  # time for previous run
        self.maxTheta = 0  # max theta variable
        self.state = "select"
        self.newState = "select"
        self.x_pos = 0
        self.y_pos = 0
        self.homed = True
        self.finished = False
        self.theta = 0

        # Initialize timer for runs
        self.runTimer = timer.timer()

        #Set up empty score array
        self.scoreArr = []
        self.lastMaxTheta = 1
        self.lastName = ""

        #Width and height of screen:
        self.width = int(768)
        self.height = int(1366)


        # Build container which acts as parent to all frames we will show
        # We just rasie the child frame we want at a given time to the top of the stack
        container = tk.Frame(self)
        container.master.maxsize(self.width, self.height)
        container.master.minsize(self.width, self.height)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Build dictionary of all frames we will want to show that this instance of the gamePlayer class
        # will use
        self.frames = {}
        for F in (select_frame.select_frame(parent=container, controller=self), manual_frame.manual_frame(parent=container, controller=self), automatic_frame.automatic_frame(parent=container, controller=self), thankyou_frame.thankyou_frame(parent=container, controller=self)):
            page_name = F.name
            frame = F ##.F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

    def getState(self):
        self.lastState = self.state;
        if self.state == "manual" and self.finished == True:
            self.state = "thankyou"
            return
        elif self.state == "automatic" and self.finished == True:
            self.state = "thankyou"
            return
        elif self.state == "thankyou" and self.homed == True:
            self.state = "select"
            return
        else:
            return

    def buttonState(self, buttonState):
        self.lastState = self.state
        self.state = buttonState

    def actions(self):
        #Show relevant frame for current state
        self.chooseFrame()
        #Perform underlying tasks
        if self.state == "select":
            if self.finished == True:
                self.finished = False
            self.x_des = (self.frames["select_frame"].xdesEntry.get())/1000
            #Tasks to run once when enter state:
            if self.state != self.lastState:
                if not self.cancel:
                    self.updateScoreArr(self.lastName, self.lastRunTime, self.lastMaxTheta) #Updtae score array
                else:
                    self.cancel = False
                self.maxTheta = 0 #reset max theta
        elif self.state == "manual":
            if self.homed == True:
                self.homed = False
            ##To happen every run:
            self.updateMaxTheta() #Check for maxTheta
            if self.state != self.lastState: #To happen once when enter state
                self.frames["manual_frame"].swingAnim.show() #show swing animation
                self.runTimer.startTimer() #start timer
                self.lastName = self.frames["select_frame"].nameEntry.get()
        elif self.state == "automatic":
            if self.homed == True:
                self.homed = False
            #To run every loop
            self.updateMaxTheta() #Update max theta
            if self.state != self.lastState: #To run once when enter state
                self.runTimer.startTimer() #start timer
                self.lastName = "Automatic"
        elif self.state == "thankyou":
            print("In thank you")
            print(self.lastState)
            print(self.state)
            if self.lastState == "manual":
                print("---------------------------------------------------------------- In last state condition")
                self.frames["manual_frame"].swingAnim.hide()  # Hide swing animation
            elif self.lastState == "automatic":
                A = 5  # TODO: self.frames["automatic_frame"].swingAnim.hide()
            if self.state != self.lastState: #To run once when enter state
                self.lastRunTime = self.runTimer.getTime() #Update time for score array
                self.lastMaxTheta = self.maxTheta #update max theta for score array
                self.runTimer.resetTimer() #Reset timer for next time

        return

    # helper function to update Frame based on state
    def chooseFrame(self):
        # The 'show_frame' function calls this update function as well, hence it is continually called
        # self.time = getTimeString()
        if self.state == "select":
            self.show_frame("select_frame")
        elif self.state == "manual":
            self.show_frame("manual_frame")
        elif self.state == "automatic":
            self.show_frame("automatic_frame")
        elif self.state == "thankyou":
            self.show_frame("thankyou_frame")
        else:
            print("Error: State != select|manual|automatic|thankyou")

    # Helper function to display frame
    def show_frame(self, page_name):
        # accesses frame from container dictionary
        frame = self.frames[page_name]
        # update frame with new time
        frame.update(self.runTimer.getTimeString())
        # Raise frame
        frame.tkraise()

    # helper function to update value of thetaMax
    def updateMaxTheta(self):
        if abs(self.theta) > self.maxTheta:
            self.maxTheta = abs(self.theta)
        return


    # Updates score array to include values from last run.
    def updateScoreArr(self, lastName, lastTime, lastMaxTheta):
        # Score calculated based on eqn: (CURRENT IS DUMMY:) 1/(time * max angle) * 1,000,000
        score = int(1 / (lastTime * lastMaxTheta) * 1000000)
        # Create new row in correct format
        newRow = (lastName, score, round(lastTime,2), lastMaxTheta)
        # Append new score to existing array and return it
        #print("ScoreArr: " + str(self.scoreArr))
        #print("new row+ " + str(newRow))
        self.scoreArr.append(newRow)

    def setCancelTrue(self):
        self.cancel = True

    def setCancelFalse(self):
        self.cancel = False

