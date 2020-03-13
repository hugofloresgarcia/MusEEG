import tkinter as tk
import MusEEG
from MusEEG import cerebro, Processor
from tkinter import filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

buttonRow = 2

processor = Processor()
processor.OSCstart()
processor.defineOSCMessages()

class demoApp(tk.Frame):
    availableGestures = list(processor.cerebro.mididict.keys())
    defaultGesture = availableGestures[0]
    gestureButtonStartRow=0
    buttonRow=11

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def tempoBox(self):
        self.templbl = tk.Label(self, text='tempo (bpm)').grid(row=self.buttonRow+1, column=2)
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

    def buttonStartProcessor(self):
        def startProcessor():
            processor.startStream()
            processor.runProcessorThread(target=processor.mainProcessorWithoutBackTrack)
            processor.bandPowerThread(asThread=True)


        self.startProcessorBttn = tk.Button(self, command=startProcessor)
        self.startProcessorBttn["text"] = "Start Processor"
        self.startProcessorBttn.grid(row=self.buttonRow+3, column=0, columnspan=2, padx=5, pady=5)


    def plotWindow(self):
        self.canvas = FigureCanvasTkAgg(processor.cerebro.eeg.plotWavelets(1), self)
        self.canvas.draw()
        # self.canvas.get_tk_widget().pack(side="right", expand=True)
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=11, columnspan=3, padx=5, pady=5)

    def checkboxArpeggiate(self):
        self.arpVar = tk.BooleanVar()
        self.checkboxArp = tk.Checkbutton(self, text="arpeggiate?", variable=self.arpVar)
        self.checkboxArp.grid(row=self.buttonRow+2, column=2, padx=5, pady=5)

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

        self.chordlist = [chord.notelist for chord in processor.cerebro.mididict.values()]

        for gesture in processor.cerebro.gestures:
            index = processor.cerebro.gestures.index(gesture)

            #create entry box and set defaultchordlist as default
            self.chordEntrybx.append(tk.Entry(self))

            self.chordEntrybx[index].insert(0, listToString(self.chordlist[index]))
            self.chordEntrybx[index].grid(row=self.gestureButtonStartRow+index, column=1)

        #retrieve chords from list
        def defineChordList():
            for items in range(len(processor.cerebro.gestures)):
                self.chordlist[items] = stringToList(self.chordEntrybx[items].get())

            processor.cerebro.updateChordList(self.chordlist)

        #button to update chords
        self.updateChords = tk.Button(self, command=defineChordList)
        self.updateChords["text"] = "update MIDIdict"
        #place the button under all the entry boxes
        self.updateChords.grid(row=self.gestureButtonStartRow+len(self.chordlist)+2, column=0, columnspan=2)

        def saveChordDict():
            processor.cerebro.saveMIDIdict(addressPath=filedialog.asksaveasfilename(initialdir=MusEEG.parentDir+'/data/MIDIdicts', title='save MIDI dictionary')+'.pickle')

        # button to save chords
        self.saveChords = tk.Button(self, command=saveChordDict)
        self.saveChords["text"] = "save MIDIdict"
        # place the button under all the entry boxes
        self.saveChords.grid(row=self.gestureButtonStartRow + len(self.chordlist) + 1, column=0)

        def loadChordDict():
            processor.cerebro.loadMIDIdict(addressPath=filedialog.askopenfilename(initialdir=MusEEG.parentDir+'/data/MIDIdicts', title='load MIDI dictionary'))

            for gesture in processor.cerebro.gestures:
                index = processor.cerebro.gestures.index(gesture)
                self.chordEntrybx[index].delete(0, 'end')
                self.chordEntrybx[index].insert(0, listToString(processor.cerebro.mididict[gesture].notelist))

        # button to load chords
        self.loadChords = tk.Button(self, command=loadChordDict)
        self.loadChords["text"] = "load MIDIdict"
        # place the button under all the entry boxes
        self.loadChords.grid(row=self.gestureButtonStartRow + len(self.chordlist) + 1, column=1)

    def create_widgets(self):
        self.winfo_toplevel().title("MusEEG")

        self.tempoBox()
        self.arpeggioDuration()
        self.chordDuration()
        self.gestureButtons()

        self.checkboxArpeggiate()

        self.buttonStartProcessor()

        self.defineChordEntry()


processor.cerebro.loadFromDataSet(name=demoApp.defaultGesture)

root = tk.Tk()
app = demoApp(master=root)

#todo: the app isnt quitting properly and it ruins ur computer
while True:
    try:
        app.mainloop()
        break
    except UnicodeDecodeError:
        pass
