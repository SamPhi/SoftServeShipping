import tkinter as tk
from tkinter import font as tkfont
import time

class gamePlayer(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        #initialize state variables
        self.cancel = False
        self.x_des = 0 #Desired x position - set default to target location for actual thing
        self.y_des = 0 #desired y position - set default to target location for actual thing
        self.time = 0 #time for displaying timer and measuring scores
        self.maxTheta = 0 #max theta variable

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

        #Start update loop:
        self.state = "select"
        self.update("select")

    def update(self,newState):

        #positional_data = readESP32()
        #self.theta = positional_data[1]
        #self.pos_x = positional_data[2]
        # etc. for all state variables

        #if theta> maxTheta
            #maxTheta= theta

        #self.time = getTime()
        if newState == self.state:
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
        elif newState!=self.state:
            #restart timer
            print("restart timer to be implemented")
            self.state = newState
            self.update(newState)
        else:
            print("Error: 'newState == self.state' & 'newState!=self.state' both false")

        self.state = newState
        #self.update(self.state)

    #Helper function to display frame
    def show_frame(self,page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.update(5)
        frame.tkraise()

#Select frame class: used to define and update
class select_frame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Welcome to soft serve shipping! Please select automatic or manual mode using the buttons below", font=controller.title_font,wraplength=300, justify = "center")
        label.pack(side="top", fill="x", pady=10)
        button1 = tk.Button(self, text="Manual",
                           command=lambda: controller.update("manual"))
        button2 = tk.Button(self, text = "Automatic", command = lambda: controller.update("automatic"))

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
        button1 = tk.Button(self, text="Finished",
                            command=lambda: controller.update("thankyou"))
        button1.pack()

    def update(self, time):
        return

class automatic_frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self,
                         text="Automatic mode: Let the machine do its thing!",
                         font=controller.title_font,wraplength=300, justify = "center")
        label.pack(side="top", fill="x", pady=10)
        button1 = tk.Button(self, text="Finished",
                            command=lambda: controller.update("thankyou"))
        button1.pack()

    def update(self, time):
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
                            command=lambda: controller.update("select"))
        button1.pack()

    def update(self, time):
        return

if __name__ == "__main__":
    game = gamePlayer()
    game.mainloop()