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

class swingAnimation():
    def __init__(self,width):
        #Create stuff for finding lines to draw
        self.width = width
        self.arm_coords = (0,0,0,400) #initial arm coords as x0, x1, y0, y1

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


swingAnim = swingAnimation(width)

#Brain of animation:
line1,line2,line3,line4 = swingAnimation.create_ContainePoints(swingAnim.arm_coords,200,200)

line1Rot,line2Rot,line3Rot,line4Rot = swingAnimation.rotateDisplacePoint(line1,theta),swingAnimation.rotateDisplacePoint(line2,theta),swingAnimation.rotateDisplacePoint(line3,theta),swingAnimation.rotateDisplacePoint(line4,theta)

finalCoords = swingAnimation.rotateDisplacePoint(swingAnim.arm_coords,theta)


#GUI things:
root = tk.Tk()
root.geometry("768x1366")

swingAnimation = tk.Canvas(root,width=width,height=width,bg="white")
swingAnimation.pack()

print(finalCoords)

(500,500,-500,-500) #shows top left to bot right


swingAnimation.create_line(finalCoords,fill="red",width=35)
swingAnimation.create_line(line1Rot,fill="red",width=10)
swingAnimation.create_line(line2Rot,fill="red",width=10)
swingAnimation.create_line(line3Rot,fill="red",width=10)
swingAnimation.create_line(line4Rot,fill="red",width=10)

root.mainloop()


