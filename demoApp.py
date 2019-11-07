import tkinter as tk
from MusEEG import cerebro

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class demoApp(tk.Frame):
    availableGestures = list(cerebro.mididict.keys())
    defaultGesture = availableGestures[6]

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

        
    def welcomeMessage(self):
        self.welcomemsg = tk.Message(self, text=cerebro.hellomsg)
        # self.welcomemsg.pack(side="left")
        self.welcomemsg.grid(row=0, column=0, padx=5, pady=5)

    def loadRandomSampleButton(self):
        def loadRandBttncommand():
            cerebro.loadFromDataSet(name=self.gestVar.get())

            self.canvas.flush_events()
            self.canvas = FigureCanvasTkAgg(cerebro.eeg.plotRawEEGui(), self)
            self.canvas.draw()
            self.say_hi()
            self.canvas.get_tk_widget().grid(row=0, column=2, padx=5, pady=5)

        self.loadRandBttn = tk.Button(self)
        self.loadRandBttn["text"] = "Load Random Sample"
        self.loadRandBttn["command"] = loadRandBttncommand
        self.loadRandBttn.grid(row=1, column=1, padx=5, pady=5)
        
    def dropDownGestures(self):
        self.gestVar = tk.StringVar(self)
        self.gestVar.set(self.defaultGesture)

        self.gestPopup = tk.OptionMenu(self, self.gestVar, *self.availableGestures)
        self.gestPopup.grid(row=1, column=0, padx=5, pady=5)

    def buttonProcessAndSend(self):
        self.processAndSendBttn = tk.Button(self, command=lambda: cerebro.processAndPlay(arp=self.arpVar.get()))
        self.processAndSendBttn["text"] = "Process and Send to Musician"
        self.processAndSendBttn.grid(row=2, column=2, padx=5, pady=5)


    def plotWindow(self):
        self.canvas = FigureCanvasTkAgg(cerebro.eeg.plotRawEEGui(), self)
        self.canvas.draw()
        # self.canvas.get_tk_widget().pack(side="right", expand=True)
        self.canvas.get_tk_widget().grid(row=0, column=2, padx=5, pady=5)

    def checkboxArpeggiate(self):
        self.arpVar = tk.BooleanVar()
        self.checkboxArp = tk.Checkbutton(self, text="arpeggiate?", variable=self.arpVar)
        self.checkboxArp.grid(row=1, column=2, padx=5, pady=5)

    def create_widgets(self):
        self.welcomeMessage()
        self.dropDownGestures()
        self.plotWindow()
        self.loadRandomSampleButton()
        self.checkboxArpeggiate()
        self.buttonProcessAndSend()


    def say_hi(self):
        print("hi there, everyone!")

#instantiate a cerebro object
cerebro = cerebro()
cerebro.loadFromDataSet(name=demoApp.defaultGesture)

root = tk.Tk()
app = demoApp(master=root)
app.mainloop()