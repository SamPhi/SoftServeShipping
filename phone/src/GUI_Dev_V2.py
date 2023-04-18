import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import time
import math
import json, socket
import numpy as np

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
        self.runTimer = timer()

        #Set up empty score array
        self.scoreArr = []
        self.lastMaxTheta = 1

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
        for F in (select_frame, manual_frame, automatic_frame, thankyou_frame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

    def changeState(self, newState):
        self.newState = newState

    def updater(self, newState):
        # Updater acts as the state machine for the system

        # update maxTheta for score tracking
        self.updateMaxTheta()

        # update newState for non-button related events
        #If no non-button related events, returns newState unchanged
        if newState == self.state:
            newState = self.updateStateNonButton(newState)

        # The block below resets flags, updates the state, and calls this update functions again
        if newState != self.state:
            # update appropriate variables for change of state
            self.stateChanged(newState)
            # assign newState to state and update
            self.state = newState
            self.updater(newState)
            # raise approrpaite frame for the current state for GUI if previous and next state are same
        elif newState == self.state:
            self.chooseFrame(newState)
        else:
            print("Error: 'newState == self.state' & 'newState!=self.state' both false")

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

    # helper function to update Frame based on state
    def chooseFrame(self, newState):
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

    # helper function for change conditions/actions of state machine
    def stateChanged(self, newState):
        if newState == "manual":
            self.maxTheta = 0
            self.frames["manual_frame"].swingAnim.show()
            self.runTimer.startTimer()
        elif newState == "automatic":
            self.maxTheta = 0
            #self.frames["automatic_frame"].swingAnim.show()
            self.runTimer.startTimer()
        elif newState == "thankyou":
            if self.state == "manual":
                self.frames["manual_frame"].swingAnim.hide()
            #elif self.state == "automatic":
            #    self.frames["automatic_frame"].swingAnim.hide()
            self.lastRunTime = self.runTimer.getTime()
            self.lastMaxTheta = self.maxTheta
            self.runTimer.resetTimer()
        elif newState == "select":
            #Maybe acc do nothing
            self.updateScoreArr("Test Name", self.lastRunTime, self.lastMaxTheta)
        else:
            print("error in changeState: newState!= a valid state name")

    def updateStateNonButton(self,newState):
        #updates for the three non-button cases as per the state machine diagram
        if newState == "manual" and self.finished == True:
            return "thankyou"
        if newState == "automatic" and self.finished == True:
            return "thankyou"
        if newState == "thankyou" and self.homed == True:
            return "select"
        else:
            return newState

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



# Select frame class: used to define and update
class select_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
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
        self.table = ScoresTable(self)
        self.table.pack(fill=tk.BOTH, expand=True,pady=20)

    def update(self, time):
        self.table.update_scores(self.controller.scoreArr)
        return


class manual_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
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
                                 command=lambda: [controller.changeState("thankyou"), controller.setCancelTrue()])
        self.button1.pack(pady=20)

        #Create theta label
        self.thetaLabel = tk.Label(self, text="", font=controller.title_font, wraplength=(controller.width*7/8), justify="center")
        self.thetaLabel.pack(pady=(10,10))



        #Create Swing animation
        self.swingAnim = swingAnimation(controller.width)
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


class automatic_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
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
                            command=lambda: [controller.changeState("thankyou"),controller.setCancelTrue()])
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


class thankyou_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.label = tk.Label(self,
                         text="Thank you for playing! Please wait whilst the machine homes itself for the next run",
                         font=controller.title_font, wraplength=(controller.width*7/8), justify="center")
        self.label.pack(side="top", fill="x", pady=10)
        self.button1 = tk.Button(self, text="Homed",
                            command=lambda: controller.changeState("select"))
        self.button1.pack()

    def update(self, time):
        self.controller.setCancelFalse()
        return

#Swing animation class for creating swing animation in manual and auto modes
class swingAnimation(tk.Canvas):
    def __init__(self,width):
        tk.Canvas.__init__(self,width=width,height=width,bg="white")

        self.armLength = 400
        self.dx = 200
        self.dy = 200
        self.width = width

        #Create stuff for finding lines to draw
        self.arm_coords = (0,0,0,self.armLength) #initial arm coords as x0, x1, y0, y1
        self.line0 = None
        self.line1 = None
        self.line2 = None
        self.line3 = None
        self.line4 = None

    #Creates points for the initial corners of four containers based on the coordinates of arm_coords
    @classmethod
    def create_ContainePoints(self,points,dx,dy):
        x0 = points[0]
        x1 = points[1]
        y0 = points[2]
        y1 = points[3]
        line1 = (x1 - dx, x1 + dx, y1, y1)
        line2 = (x1 - dx, x1 + dx, y1 + dy, y1 + dy)
        line3 = (x1-dx,x1-dx,y1,y1+dy)
        line4 = (x1+dx,x1+dx,y1,y1+dy)
        return line1,line2,line3,line4

    #Takes rotates points by angle and then shifts them for display
    def rotateDisplacePoint(self,points,angle):
        width = self.width
        x0 = points[0]
        x1 = points[1]
        y0 = points[2]
        y1 = points[3]
        #Create R array
        c,s = np.cos(np.radians(angle)),np.sin(np.radians(angle))
        R = np.array(((c,-s),(s,c)))
        #Rotate line coordinates by theta
        initCoords = np.array([[x0,x1],[y0,y1]])
        RotCoords = np.matmul(R,initCoords)
        #Displace 'gantry' to top middle of frame
        RotDisCoords = RotCoords + np.array([[width/2,width/2],[0,0]])
        #Turn coords back into usable format (i.e. not numpy array
        finalCoords = (RotDisCoords[0,0],RotDisCoords[1,0],RotDisCoords[0,1],RotDisCoords[1,1])
        return finalCoords

    def getPoints(self,theta):
        line1, line2, line3, line4 = self.create_ContainePoints(self.arm_coords, self.dx, self.dy)
        line1Rot, line2Rot, line3Rot, line4Rot = self.rotateDisplacePoint(line1,theta), self.rotateDisplacePoint(line2, theta), self.rotateDisplacePoint(line3, theta), self.rotateDisplacePoint(line4,theta)
        return [line1Rot, line2Rot, line3Rot, line4Rot]

    def getFinalCoords(self,theta):
        return self.rotateDisplacePoint(self.arm_coords, theta)

    def drawContainer(self,theta):
        if not self.line0:
            self.line0 = self.create_line(self.getFinalCoords(theta), fill="red", width=35)
        if not self.line1:
            self.line1 = self.create_line(self.getPoints(theta)[0], fill="red", width=10)
        if not self.line2:
            self.line2 = self.create_line(self.getPoints(theta)[1], fill="red", width=10)
        if not self.line3:
            self.line3 = self.create_line(self.getPoints(theta)[2], fill="red", width=10)
        if not self.line4:
            self.line4 = self.create_line(self.getPoints(theta)[3], fill="red", width=10)
        self.coords(self.line0,self.getFinalCoords(theta))
        self.coords(self.line1, self.getPoints(theta)[0])
        self.coords(self.line2, self.getPoints(theta)[1])
        self.coords(self.line3, self.getPoints(theta)[2])
        self.coords(self.line4, self.getPoints(theta)[3])

    def show(self):
        self.pack()

    def hide(self):
        self.pack_forget()
        return

#Score table class - used by select screen to show scores so far
#Creates a tk.Frame() object which can be packed into the select frame
class ScoresTable(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.text_font_bold = tkfont.Font(family='Helvetica', size=18, weight="bold")
        self.text_font = tkfont.Font(family='Helvetica', size=18, slant="italic")

        style = ttk.Style(self)
        style.theme_use("clam")  # set theam to clam
        style.configure("Treeview", background="white",
                        fieldbackground="white", foreground="black", font = self.text_font)
        style.configure('Treeview.Heading', background="white", font = self.text_font_bold)


        # Create a scrollbar
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.colWidthUnit = int((768/2)/9) #TODO: Remove the div 2

        # Create a treeview with columns
        self.columns = ("Name", "Score", "Time", "Max Angle")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", yscrollcommand=self.scrollbar.set)
        self.tree.column("Name",width=(self.colWidthUnit)*3)
        self.tree.column("Score", width=(self.colWidthUnit)*2)
        self.tree.column("Time", width=(self.colWidthUnit)*2)
        self.tree.column("Max Angle", width=(self.colWidthUnit)*2)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Set the column headings
        for col in self.columns:
            self.tree.heading(col, text=col)

        # Configure the scrollbar to work with the treeview
        self.scrollbar.config(command=self.tree.yview)

    def update_scores(self, scores):
        # Delete all the old scores
        if not scores:
            return
        for child in self.tree.get_children():
            self.tree.delete(child)

        # Add the new scores
        for score in scores:
            self.tree.insert("", tk.END, values=score)



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

def start_server():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to a specific address and port
    server_address = ('127.0.0.1', 12345) #Should be:'192.168.43.1', 12345 for phone, '1
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)
    # Wait for a connection
    #print('waiting for a connection')
    connection, client_address = sock.accept()
    return connection

def send_data(sock, x_des, y_des, state, cancel):
    # Send data
    phoneDataArr = json.dumps({"x_des": x_des, "y_des": y_des, "state": state, "cancel": cancel})
    message = phoneDataArr.encode()
    #print('sending {!r}'.format(message))
    sock.sendall(message)

def receive_data(sock,game):
    # Receive data
    data = sock.recv(1024)
    if not data:
        return
    # If recieved multiple data packets since last check, return
    if "}{" in data.decode():
        return
    data = json.loads(data.decode())
    game.x_pos = data.get("x_pos")
    game.y_pos = data.get("y_pos")
    game.homed = data.get("homed")
    game.finished = data.get("finished")
    game.theta = data.get("theta")


if __name__ == "__main__":
    #Start an instance of gamePlayer() class
    game = gamePlayer()
    #start our server for ESP32 comms
    sock = start_server()
    while True:
        newState = game.newState
        game.updater(newState)
        game.update()
        #print("Starting send data")
        print(game.state)
        send_data(sock, game.x_des, game.y_des, game.state, game.cancel)
        #print("Finished send data")
        #print("Starting recieveing ESP32 data")
        receive_data(sock, game)
        #print("Finished recieveing ESP32 data. Recieved message:")
        #print(game.x_des, game.y_des, game.state, game.cancel)