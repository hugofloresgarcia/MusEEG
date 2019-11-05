import os
import MusEEG as MusEEG
from MusEEG import eegData, chord, classifier
import numpy as np

from tkinter import *

from tkinter import Tk, BOTH
from tkinter.ttk import Frame, Button, Style

gestures = ['smile', 'bitelowerlip', 'eyebrows', 'hardblink', 'lookleft', 'lookright',
            'neutral', 'scrunch', 'tongue']

class Window(Frame):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("Windows")
        self.pack(fill=BOTH, expand=True)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)

        lbl = Label(self, text="Windows")
        lbl.grid(sticky=W, pady=4, padx=5)

        area = Text(self)
        area.grid(row=1, column=0, columnspan=2, rowspan=4,
                  padx=5, sticky=E + W + S + N)

        abtn = Button(self, text="Activate")
        abtn.grid(row=1, column=3)

        cbtn = Button(self, text="Close")
        cbtn.grid(row=2, column=3, pady=4)

        hbtn = Button(self, text="Help")
        hbtn.grid(row=5, column=0, padx=5)

        obtn = Button(self, text="OK")
        obtn.grid(row=5, column=3)
        # Frame for preprocess and classify buttons
        buttonFrame = Frame(self, relief=RAISED, borderwidth=1)
        buttonFrame.pack(fill=BOTH, expand=True)

        self.pack(fill=BOTH, expand=True)

        processButton = Button(self, text='preprocess EEG')
        processButton.pack(side=RIGHT, padx=5, pady=5)
        classifyButton = Button(self, text='send to bigBrain')
        classifyButton.pack(side=RIGHT)

    def onSelect(self, val):
        sender = val.widget
        idx = sender.curselection()
        value = sender.get(idx)

        self.var.set(value)


def main():
    root = Tk()
    root.geometry("500x500+300+300")
    app = Window()
    root.mainloop()


if __name__ == '__main__':
    main()
