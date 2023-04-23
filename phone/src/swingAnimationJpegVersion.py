import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import time
import math
import json, socket
import numpy as np

#Setup for state machine variables
width = 768
theta= 12

class swingAnimation(tk.Canvas):
    def __init__(self,width):
        tk.Canvas.__init__(self,width=width,height=width,bg="white")

        #Create stuff for finding lines to draw
        self.arm_coords = (0,0,0,width/4) #initial arm coords as x0, x1, y0, y1

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
    @classmethod
    def rotateDisplacePoint(self,points,angle):
        x0 = points[0]
        x1 = points[1]
        y0 = points[2]
        y1 = points[3]
        #Create R array
        c,s = np.cos(np.radians(theta)),np.sin(np.radians(angle))
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
        line1, line2, line3, line4 = self.create_ContainePoints(self.arm_coords, 200, 200)
        line1Rot, line2Rot, line3Rot, line4Rot = self.rotateDisplacePoint(line1,theta), self.rotateDisplacePoint(line2, theta), swingAnimation.rotateDisplacePoint(line3, theta), swingAnimation.rotateDisplacePoint(line4,theta)
        return [line1Rot, line2Rot, line3Rot, line4Rot]

    def getFinalCoords(self,theta):
        return self.rotateDisplacePoint(self.arm_coords,theta)

    def drawContainer(self,theta):
        self.create_line(self.getFinalCoords(theta), fill="red", width=35)
        self.create_line(self.getPoints(theta)[0], fill="red", width=10)
        self.create_line(self.getPoints(theta)[1], fill="red", width=10)
        self.create_line(self.getPoints(theta)[2], fill="red", width=10)
        self.create_line(self.getPoints(theta)[3], fill="red", width=10)


#Create instance of class
swingAnim = swingAnimation(width)

#GUI things:
root = tk.Tk()
root.geometry("768x768")

swingAnim.pack()

swingAnim.drawContainer(theta)


root.mainloop()


