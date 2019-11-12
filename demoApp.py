import tkinter as tk
from MusEEG import cerebro
import pprint

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

buttonRow = 2

#instantiate a cerebro object
cerebro = cerebro()

class demoApp(tk.Frame):
    availableGestures = list(cerebro.mididict.keys())
    defaultGesture = availableGestures[6]
    gestureButtonStartRow=0
    buttonRow=11

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        
    def welcomeMessage(self):
        self.welcomemsg = tk.Message(self, text=cerebro.demomsg, relief=tk.RIDGE)
        self.welcomemsg.anchor('nw')
        # self.welcomemsg.pack(side="left")
        self.welcomemsg.grid(row=11, column=0, rowspan=5, columnspan=2, padx=5, pady=5)

    def tempoBox(self):
        self.tempolbl = tk.Label(self, text='tempo').grid(row=buttonRow+1, column=2)
        self.tempobx = tk.Entry(self)
        self.tempobx.insert(10, '120')
        self.tempobx.grid(row=self.buttonRow, column=2)

    def arpeggioDuration(self):
        self.arpeglbl = tk.Label(self, text='arpeggio note duration (in qtr notes)').grid(row=self.buttonRow+1, column=3)
        self.arpegbx = tk.Entry(self)
        self.arpegbx.insert(10, '0.5')
        self.arpegbx.grid(row=self.buttonRow, column=3)

    def chordDuration(self):
        self.sustainlbl = tk.Label(self, text='sustain duration (in qtr notes)').grid(row=self.buttonRow + 3, column=3)
        self.sustainbx = tk.Entry(self)
        self.sustainbx.insert(10, '8')
        self.sustainbx.grid(row=self.buttonRow+2, column=3)

    def buttonProcessAndSend(self):
        def processFunction():
            cerebro.processAndPlay(arp=self.arpVar.get(), tempo=int(self.tempobx.get()),
                                   arpDurationFromGUI=float(self.arpegbx.get()),
                                   noteDurationFromGUI=float(self.sustainbx.get()))
            self.classificationResultVar.set(cerebro.gestureResult)

        self.processAndSendBttn = tk.Button(self, command=processFunction)
        self.processAndSendBttn["text"] = "Process and Send to Musician"
        self.processAndSendBttn.grid(row=self.buttonRow+2, column=2, padx=5, pady=5)

    def gestureButtons(self):
        def gestBttnCommand(gestureToLoad):
            #load from dataset
            cerebro.loadFromDataSet(name=gestureToLoad)

            #update plot window todo: make it not have to redefine entire plot window for faster processing
            self.canvas.flush_events()
            self.canvas = FigureCanvasTkAgg(cerebro.eeg.plotRawEEGui(), self)
            self.canvas.draw()
            self.say_hi()
            self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=11, columnspan=3,  padx=5, pady=5)

        self.gesturebttn = list()
        for GESTURES in cerebro.gestures:
            index = cerebro.gestures.index(GESTURES)
            self.gesturebttn.append(tk.Button(self, text=GESTURES, command=lambda GESTURES=GESTURES: gestBttnCommand(GESTURES)))
            self.gesturebttn[index].grid(row=self.gestureButtonStartRow+index, column=0)

    def plotWindow(self):
        self.canvas = FigureCanvasTkAgg(cerebro.eeg.plotRawEEGui(), self)
        self.canvas.draw()
        # self.canvas.get_tk_widget().pack(side="right", expand=True)
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=11, columnspan=3, padx=5, pady=5)

    def checkboxArpeggiate(self):
        self.arpVar = tk.BooleanVar()
        self.checkboxArp = tk.Checkbutton(self, text="arpeggiate?", variable=self.arpVar)
        self.checkboxArp.grid(row=self.buttonRow+1, column=2, padx=5, pady=5)

    def defineChordEntry(self):
        def listToString(s):
            # initialize an empty string
            str1 = " "
            # return string
            return (str1.join(s))

        def stringToList(s):
            return s.split()

        self.chordEntryLbl = list()
        self.chordEntrybx = list()

        self.chordlist = cerebro.defaultchordlist

        for gesture in cerebro.gestures:
            index = cerebro.gestures.index(gesture)
            # self.chordEntryLbl.append(tk.Label(self, text=gesture))
            # self.chordEntryLbl[index].grid(row=self.gestureButtonStartRow+index, column=0)

            #create entry box and set defaultchordlist as default
            self.chordEntrybx.append(tk.Entry(self))
            self.chordEntrybx[index].insert(0, listToString(cerebro.defaultchordlist[index]))
            self.chordEntrybx[index].grid(row=self.gestureButtonStartRow+index, column=1)



        #retrieve chords from list
        def defineChordList():
            for items in range(len(self.chordlist)):
                self.chordlist[items] = stringToList(self.chordEntrybx[items].get())

            cerebro.updateChordList(self.chordlist)

        #button to update chords
        self.updateChords = tk.Button(self, command=defineChordList)
        self.updateChords["text"] = "update chord dictionary"
        #place the button under all the entry boxes
        self.updateChords.grid(row=self.gestureButtonStartRow+len(self.chordlist)+1, column=1)



    def classificationResult(self):
        permanentText = 'classification result: '
        self.classificationResultVar = tk.StringVar(self)
        self.classificationResultVar.set('none')
        self.classPrint = tk.Label(self, text=permanentText+self.classificationResultVar.get())
        self.classPrint.grid(row=self.buttonRow+3, column=2)


    def create_widgets(self):
        self.winfo_toplevel().title("MusEEG")

        self.welcomeMessage()
        self.tempoBox()
        self.arpeggioDuration()
        self.chordDuration()
        self.gestureButtons()
        self.plotWindow()
        self.checkboxArpeggiate()
        self.classificationResult()
        self.buttonProcessAndSend()
        self.defineChordEntry()



    def say_hi(self):
        print("hi there, everyone!")


cerebro.loadFromDataSet(name=demoApp.defaultGesture)

root = tk.Tk()
app = demoApp(master=root)

#todo: the app isnt quitting properly and it ruins ur computer
while True:
    try:
        app.mainloop()
        break
    except UnicodeDecodeError:
        pass
