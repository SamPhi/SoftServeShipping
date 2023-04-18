import tkinter as tk
from tkinter import ttk


titleArray = [["Name","Score","Time (sec)","MaxTheta (deg)"]]

#Dummy last play values
lastName = "Sam"
lastTime = 78
lastMaxTheta = 12

scoreArr = [] #To be a self.scoreArr[()] in gamePlayer class

#Updates score array to include values from last run.
#To be used as a method in gamePlayer class
def updateScoreArr(scoreArr,lastName,lastTime,lastMaxTheta):
    #Score calculated based on eqn: (CURRENT IS DUMMY:) 1/(time * max angle) * 1,000,000
    score = 1/(lastTime * lastMaxTheta) * 1000000
    #Create new row in correct format
    newRow = (lastName,score,lastTime,lastMaxTheta)
    #Append new score to existing array and return it
    return scoreArr.append(newRow)


class ScoresTable(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Create a scrollbar
        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a treeview with columns
        columns = ("Name", "Score", "Max Angle", "Time")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Set the column headings
        for col in columns:
            self.tree.heading(col, text=col)

        # Configure the scrollbar to work with the treeview
        scrollbar.config(command=self.tree.yview)

    def update_scores(self, scores):
        # Delete all the old scores
        for child in self.tree.get_children():
            self.tree.delete(child)

        # Add the new scores
        for score in scores:
            self.tree.insert("", tk.END, values=score)


# Create the GUI
root = tk.Tk()
table = ScoresTable(root)
table.pack(fill=tk.BOTH, expand=True)

# Add some initial scores
scores = scoreArr
updateScoreArr(scoreArr,lastName,lastTime,lastMaxTheta)
updateScoreArr(scoreArr,lastName,lastTime,lastMaxTheta)
updateScoreArr(scoreArr,lastName,lastTime,lastMaxTheta)
table.update_scores(scores)


# Add a new score

# Start the main loop
root.mainloop()