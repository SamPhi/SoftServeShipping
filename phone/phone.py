import tkinter as tk
from tkinter import font as tkfont
import time
import math

class gamePlayer(tk.Tk):
    def __init__(self):
        ##Initliaize Tk properties using Tk.init() function
        tk.Tk.__init__(self)
        #Set a non-hideous font
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        #initialize state variables
        self.cancel = False
        self.x_des = 0 #Desired x position - set default to target location for actual thing
        self.y_des = 0 #desired y position - set default to target location for actual thing
        self.lastRunTime = 0 #time for previous run
        self.maxTheta = 0 #max theta variable
        self.state = "select"
        self.newState = "select"

        #Initialize timer for runs
        self.runTimer = timer()

        #Build container which acts as parent to all frames we will show
        #We just rasie the child frame we want at a given time to the top of the stack
        container = tk.Frame(self)
        container.master.maxsize(300,300)
        container.master.minsize(300,300)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #Build dictionary of all frames we will want to show that this instance of the gamePlayer class
        #will use
        self.frames = {}
        for F in (select_frame,manual_frame,automatic_frame,thankyou_frame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")



    def changeState(self, newState):
        self.newState = newState


    def updater(self,newState):
        #Update acts as the state machine for the system

        #read values from ESP32
        self.readESP32() # assigns [self.x_pos, self.y_pos, self.homed, self.finished,theta]

        #update maxTheta for score tracking
        self.updateMaxTheta()


        # The block below resets flags, updates the state, and calls this update functions again
        if newState!=self.state:
            # update appropriate variables for change of state
            self.stateChanged(newState)
            #assign newState to state and update 
            self.state = newState
            self.updater(newState)
            # raise approrpaite frame for the current state for GUI if previous and next state are same
        elif newState == self.state:
            self.chooseFrame(newState)
        else:
            print("Error: 'newState == self.state' & 'newState!=self.state' both false")


    #Helper function to display frame
    def show_frame(self,page_name):
        #accesses frame from container dictionary
        frame = self.frames[page_name]
        #update frame with new time
        frame.update(self.runTimer.getTimeString())
        #Raise frame
        frame.tkraise()

    #helper function to read ESP32
    def readESP32(self):
        #put stuff here
        # TODO: actually read from phone 
        self.x_pos = 0
        self.y_pos = 0
        self.homed = False
        self.finished = False
        self.theta = 0
        return

    #helper function to update value of thetaMax
    def updateMaxTheta(self):
        if self.theta > self.maxTheta:
            self.maxTheta = self.theta
        return

    #helper function to update Frame based on state
    def chooseFrame(self,newState):
        # If the old state is the same as the current state, it raises the corresponding frame for the current state
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

    #helper function for change conditions/actions of state machine
    def stateChanged(self,newState):
        if newState == "manual":
            self.runTimer.startTimer()
        elif newState == "automatic":
            self.runTimer.startTimer()
        elif newState == "thankyou":
            self.lastRunTime = self.runTimer.getTimeString()
            self.runTimer.resetTimer()
        elif newState == "select":
            # do nothing I guess?
            A = 1 #This state is superfluous rn but will have functionality later so stupid fix to indentation block expected error
        else:
            print("error in changeState: newState!= a valid state name")


#Select frame class: used to define and update
class select_frame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        #create text label
        label = tk.Label(self, text="Welcome to soft serve shipping! Please select automatic or manual mode using the buttons below", font=controller.title_font,wraplength=300, justify = "center")
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Manual",
                           command=lambda: controller.changeState("manual"))
        button2 = tk.Button(self, text = "Automatic", command = lambda: controller.changeState("automatic"))

        button1.pack()
        button2.pack()

    def update(self,time):
        return


class manual_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self,
                         text="Manual mode: Use the joystick to move the shipping container!",
                         font=controller.title_font,wraplength=300, justify = "center")
        label.pack(side="top", fill="x", pady=10)
        # create timer label
        self.timerLabel = tk.Label(self, text="", font=controller.title_font, wraplength=300, justify="center")
        self.timerLabel.pack(pady=20)

        button1 = tk.Button(self, text="Finished",
                            command=lambda: controller.changeState("thankyou"))
        button1.pack()

    def update(self, time):
        # update label with time. Time is a string in format M:SS
        if self.timerLabel is None:
            self.timerLabel = "error: timerlabel does not exist"
        self.timerLabel.config(text=time)
        return

class automatic_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self,
                         text="Automatic mode: Let the machine do its thing!",
                         font=controller.title_font,wraplength=300, justify = "center")
        label.pack(side="top", fill="x", pady=10)

        # create timer label
        self.timerLabel = tk.Label(self, text="", font=controller.title_font, wraplength=300, justify="center")
        self.timerLabel.pack(pady=20)

        button1 = tk.Button(self, text="Finished",
                            command=lambda: controller.changeState("thankyou"))
        button1.pack()

    def update(self, time):
        # update label with time. Time is a string in format M:SS
        if self.timerLabel is None:
            self.timerLabel = "error: timerlabel does not exist"
        self.timerLabel.config(text=time)
        return

class thankyou_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self,
                         text="Thank you for playing! Please wait whilst the machine homes itself for the next run",
                         font=controller.title_font,wraplength=300, justify = "center")
        label.pack(side="top", fill="x", pady=10)
        button1 = tk.Button(self, text="Homed",
                            command=lambda: controller.changeState("select"))
        button1.pack()

    def update(self, time):
        return

# Time class used to track runTime in gamePlayer class
class timer():
    def __init__(self):
        self.time = time.time(); #time in seconds
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
        minutes = math.floor(timeSec/60)
        seconds = math.floor(timeSec - minutes*60)
        timeString = str(minutes) + ":" + str(seconds)
        return timeString 

if __name__ == "__main__":
    game = gamePlayer()
    while True:
        newState = game.newState
        game.updater(newState)
        game.update()