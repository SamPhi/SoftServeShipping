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

