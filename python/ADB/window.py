#!/usr/bin/python
############################################################
# GUI for the ADB file
############################################################
import Tkinter

from Tkinter import *

class Application(Frame):
    def say_hi(self):
        print "hi there, everyone!"

    def query(self):
        print "query"

    def createWidgets(self):
        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

        self.hi_there = Button(self)
        self.hi_there["text"] = "Hello",
        self.hi_there["command"] = self.say_hi

        self.hi_there.pack({"side": "left"})

        self.item = Button(self)
        self.item["text"] = "my new button"
        self.item["command"] = self.query

        self.item.pack({"side":"left"})

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()
