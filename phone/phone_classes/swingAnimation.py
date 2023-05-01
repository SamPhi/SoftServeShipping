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
import thankyou_frame
from PIL import ImageTk
from PIL import Image



#Swing animation class for creating swing animation in manual and auto modes
class swingAnimation(tk.Canvas):
    def __init__(self,parent, width):
        tk.Canvas.__init__(self,parent,width=width,height=width+200,bg="white")
        self.armLength = 350
        self.dx = 150
        self.dy = 150
        self.width = width

        #Create stuff for finding lines to draw
        self.arm_coords = (0,0,0,self.armLength) #initial arm coords as x0, x1, y0, y1
        self.line0 = None
        # self.line1 = None
        # self.line2 = None
        # self.line3 = None
        # self.line4 = None

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
        ##Draws container
        if not self.line0:
            self.line0 = self.create_line(self.getFinalCoords(theta), fill="silver", width=5)
        # if not self.line1:
        #     self.line1 = self.create_line(self.getPoints(theta)[0], fill="red", width=10)
        # if not self.line2:
        #     self.line2 = self.create_line(self.getPoints(theta)[1], fill="red", width=10)
        # if not self.line3:
        #     self.line3 = self.create_line(self.getPoints(theta)[2], fill="red", width=10)
        # if not self.line4:
        #     self.line4 = self.create_line(self.getPoints(theta)[3], fill="red", width=10)
        self.coords(self.line0,self.getFinalCoords(theta))
        # self.coords(self.line1, self.getPoints(theta)[0])
        # self.coords(self.line2, self.getPoints(theta)[1])
        # self.coords(self.line3, self.getPoints(theta)[2])
        # self.coords(self.line4, self.getPoints(theta)[3])

        #IMAGE STUFF
        # Load an image in the script
        self.img = ImageTk.PhotoImage(Image.open("container.png").resize((500,250)).rotate(-theta))

        # Add image to the Canvas Items
        self.image = self.create_image(10, 10, image=self.img)
        self.move(self.image,self.getFinalCoords(theta)[2],self.getFinalCoords(theta)[3])


    def show(self):
        self.pack(pady=(10,10))
        return

    def hide(self):
        self.pack_forget()
        return

