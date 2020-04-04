import tkinter as tk
import MusEEG
from MusEEG import Processor, eegData, parentDir
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import sys
import os

import queue

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation

processor = Processor()
processor.OSCstart()
processor.defineOSCMessages()
processor.sendMIDI = False

lastbandpwr = [[0, 1, 2, 3], processor.baselinedB]

class MIDIOSCControl():

    def __init__(self, master=None, startRow=0, startColumn=0):
        self.master = master
        self.startRow = startRow
        self.startColumn = startColumn
        self.controlRow = startRow ##this gets overwritten if defineChordEntry() is on
        self.controlColumn = startColumn

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

        self.chordlist = [chord for chord in processor.mididict.values()]

        self.controlRow = self.startRow + len(self.chordlist) + 3

        for gesture in processor.cerebro.gestures:
            index = processor.cerebro.gestures.index(gesture)

            self.chordEntryLbl.append(tk.Label(self.master))
            self.chordEntryLbl[index]["text"] = gesture
            self.chordEntryLbl[index].grid(row=self.startRow+index, column=self.startColumn)

            # create entry box and set defaultchordlist as default
            self.chordEntrybx.append(tk.Entry(self.master))
            self.chordEntrybx[index].insert(0, listToString(self.chordlist[index]))
            self.chordEntrybx[index].grid(row=self.startRow + index, column=self.startColumn+1)

        # retrieve chords from list
        def defineChordList():
            for items in range(len(processor.cerebro.gestures)):
                self.chordlist[items] = stringToList(self.chordEntrybx[items].get())

            processor.updateMIDIdict(self.chordlist)

        # button to update chords
        self.updateChords = tk.Button(self.master, command=defineChordList)
        self.updateChords["text"] = "update MIDIdict"
        # place the button under all the entry boxes
        self.updateChords.grid(row=self.startRow + len(self.chordlist) + 2, column=self.startColumn, columnspan=2)

        def saveChordDict():
            processor.saveMIDIdict(
                addressPath=filedialog.asksaveasfilename(initialdir=MusEEG.parentDir + '/data/MIDIdicts',
                                                         title='save MIDI dictionary') + '.pickle')

        # button to save chords
        self.saveChords = tk.Button(self.master, command=saveChordDict)
        self.saveChords["text"] = "save MIDIdict"
        # place the button under all the entry boxes
        self.saveChords.grid(row=self.startRow + len(self.chordlist) + 1, column=self.startColumn)

        def loadChordDict():
            processor.loadMIDIdict(
                addressPath=filedialog.askopenfilename(initialdir=MusEEG.parentDir + '/data/MIDIdicts',
                                                       title='load MIDI dictionary'))

            for gesture in processor.cerebro.gestures:
                index = processor.cerebro.gestures.index(gesture)
                self.chordEntrybx[index].delete(0, 'end')
                self.chordEntrybx[index].insert(0, listToString(processor.mididict[gesture]))

        # button to load chords
        self.loadChords = tk.Button(self.master, command=loadChordDict)
        self.loadChords["text"] = "load MIDIdict"
        # place the button under all the entry boxes
        self.loadChords.grid(row=self.startRow + len(self.chordlist) + 1, column=self.startColumn+1)

    def checkboxArpeggiate(self):
        self.arpeggiateVar = tk.BooleanVar()
        self.checkboxArp = tk.Checkbutton(self.master, text="arpeggiate?", variable=self.arpeggiateVar)
        self.checkboxArp.grid(row=self.controlRow, column=self.startColumn, padx=5, pady=5)

    def checkboxScramble(self):
        self.scrambleVar = tk.BooleanVar()
        checkboxScramble = tk.Checkbutton(self.master, text="scramble?", variable=self.scrambleVar)
        checkboxScramble.grid(row=self.controlRow+1, column=self.startColumn, padx=5, pady=5)

    def chordDuration(self):
        self.sustainlbl = tk.Label(self.master, text='sustain duration (in qtr notes)').grid(row=self.controlRow+1, column=self.startColumn+1)
        self.sustainbx = tk.Entry(self.master)
        self.sustainbx.insert(10, '8')
        self.sustainbx.grid(row=self.controlRow, column=self.startColumn+1)

    def numRepeats(self):
        self.numRepeatsLabel = tk.Label(self.master, text='number of repeats (for arpeggios)').grid(row=self.controlRow+3, column=self.startColumn+1)
        self.numRepBx = tk.Entry(self.master)
        self.numRepBx.insert(0, '8')
        self.numRepBx.grid(row=self.controlRow+2, column=self.startColumn+1)

    def updateAllButton(self):
        def updateAll():
            processor.scrambleBool = self.scrambleVar.get()
            processor.arpBool = self.arpeggiateVar.get()
            processor.durVal = self.sustainbx.get()
            processor.numRepeats = self.numRepBx.get()

        self.updateAllBttn = tk.Button(self.master, command=updateAll)
        self.updateAllBttn["text"] = "update these ^^^^^"
        self.updateAllBttn.grid(row=self.controlRow+4, column=self.controlColumn, columnspan=2, padx=5, pady=5)

    def createWidgets(self):
        self.defineChordEntry()
        self.checkboxArpeggiate()
        self.checkboxScramble()
        self.chordDuration()
        self.numRepeats()
        self.updateAllButton()

class App(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def buttonLoadModel(self):
        def loadModel():
            path = filedialog.askdirectory(initialdir=MusEEG.parentDir+'/data/savedModels', title='load classifier')
            processor.bigBrain.loadmodel(filename=path, loadScaler=True)

        loadModelBttn = tk.Button(self, command=loadModel)
        loadModelBttn["text"] = "Load a bigBrain"
        loadModelBttn.grid(row=8, column=3, columnspan=1, padx=5, pady=5)

    def buttonLoadSmallModel(self):
        def loadModel():
            path = filedialog.askdirectory(initialdir=MusEEG.parentDir+'/data/savedModels', title='load classifier')
            processor.smallBrain.loadmodel(filename=path, loadScaler=True)

        loadModelBttn = tk.Button(self, command=loadModel)
        loadModelBttn["text"] = "Load a smallBrain"
        loadModelBttn.grid(row=8, column=4, columnspan=1, padx=5, pady=5)

    def buttonStartProcessor(self):
        self.startProcessorBttn = tk.Button(self, command=self.on_click)
        self.startProcessorBttn["text"] = "Start Processor"
        self.startProcessorBttn.grid(row=9, column=1, columnspan=1, padx=0, pady=0)

    def plotWindow(self):
        self.running = False
        self.ani = None

        self.fig = plt.Figure()
        self.ax1 = self.fig.add_subplot(111)

        self.lines = []
        for _ in range(0, eegData.nchannels):
            templine, = self.ax1.plot([], [], lw=2)
            self.lines.append(templine)

        # self.line, = self.ax1.plot([], [], lw=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, rowspan=4, columnspan=5)

        self.ax1.set_title('Raw EEG')
        self.ax1.set_ylim(-500, 6000)
        self.ax1.set_xlim(0, processor.client.windowSize/eegData.sampleRate)

    def bandPowerWindow(self):
        self.BPani = None

        self.bpfig = plt.Figure((3, 2))
        self.bpax1 = self.bpfig.add_subplot(111)


        self.bpline, = self.bpax1.plot([0, 1, 2, 3], processor.baselinedB, lw=2)

        # self.line, = self.ax1.plot([], [], lw=2)
        self.bpcanvas = FigureCanvasTkAgg(self.bpfig, master=self)
        self.bpcanvas.draw()
        self.bpcanvas.get_tk_widget().grid(row=1, column=6, rowspan=2, columnspan=2)

        self.bpax1.set_ylim(0, 40)
        self.bpax1.set_title('Band Power (dB)')
        self.bpax1.set_xlim(-1, 4)
        self.bpax1.set_xticklabels(['', 'theta', 'alpha', 'beta', 'gamma', ''])

    def smallBrainMonitor(self):
        self.sbani = None
        self.sbfig = plt.Figure((3, 2))
        self.sbax = self.sbfig.add_subplot(111)

        self.sblines = []
        for _ in range(0, eegData.nchannels):
            templine, = self.sbax.plot([], [], lw=2)
            self.sblines.append(templine)

        self.sbcanvas = FigureCanvasTkAgg(self.sbfig, master=self)
        self.sbcanvas.draw()
        self.sbcanvas.get_tk_widget().grid(row=5, column=6, rowspan=2, columnspan=2)

        self.sbax.set_ylim(-800, 800)
        # self.sbax.set_title('smallBrain monitor')
        self.sbax.set_xlim(-5, eegData.smallchunkSize+5)

    def bigBrainMonitor(self):
        self.bbani = None
        self.bbfig = plt.Figure((3, 2))
        self.bbax = self.bbfig.add_subplot(111)

        self.bblines = []
        for _ in range(0, eegData.nchannels):
            templine, = self.bbax.plot([], [], lw=2)
            self.bblines.append(templine)

        self.bbcanvas = FigureCanvasTkAgg(self.bbfig, master=self)
        self.bbcanvas.draw()
        self.bbcanvas.get_tk_widget().grid(row=3, column=6, rowspan=2, columnspan=2)

        self.bbax.set_ylim(-800, 800)
        self.bbax.set_title('bigBrain monitor')
        self.bbax.set_xlim(-5, eegData.chunkSize+5)

    def on_click(self):
        '''the button is a start, pause and unpause button all in one
        this method sorts out which of those actions to take'''
        if self.ani is None:
            processor.startStream()
            processor.runProcessorThread(target=processor.mainProcessorWithBackTrack)
            processor.bandPowerThread(asThread=True)
            # print('here on_click')
            # animation is not running; start it
            return self.start()

    def start(self):
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update_graph,
            interval=processor.client.windowSize/processor.client.refreshScale/eegData.sampleRate*1000,
            repeat=False)
        self.bpani = animation.FuncAnimation(
            self.bpfig,
            self.update_graph_bp,
            interval=500,
            repeat=False)
        self.sbani = animation.FuncAnimation(
            self.sbfig,
            self.update_graph_sb,
            interval=250,
            repeat=False)
        self.bbani = animation.FuncAnimation(
            self.bbfig,
            self.update_graph_bb,
            interval=250,
            repeat=False)
        self.running = True
        # self.startProcessorBttn.config(text='Pause')
        self.ani._start()
        self.bpani._start()
        self.sbani._start()
        self.bbani._start()
        print('started animation')

    def get_data_raw(self):
        x, y = processor.client.getPlotData()
        return x, y

    def get_data_bp(self):
        global lastbandpwr
        try:
            bandpwr = processor.bandPowerQueue.get(block=False)
            lastbandpwr = bandpwr

        except queue.Empty:
            bandpwr = lastbandpwr
        # x = bandpwr[0]
        x = [0, 1, 2, 3]
        y = bandpwr[1]
        return x, y

    def update_graph(self, i):
        x, y = self.get_data_raw()

        for idx, line in enumerate(self.lines):
            line.set_data(x, y[:, idx])

        return self.lines

    def update_graph_bp(self, i):
        x, y = self.get_data_bp()
        # print(y)
        if y is not None:
            self.bpline.set_data(x, y)

        return self.bpline

    def update_graph_sb(self, i):
        try:
           y = processor.smallBrainMonitorQueue.get(block=False)
           for idx, line in enumerate(self.sblines):
               line.set_data(range(0, eegData.smallchunkSize), y[:, idx])

        except queue.Empty:
            pass

        return self.sblines

    def update_graph_bb(self, i):
        try:
            y = processor.bigBrainMonitorQueue.get(block=False)
            for idx, line in enumerate(self.bblines):
                line.set_data(range(0, eegData.chunkSize), y[:, idx])
        except queue.Empty:
            pass

        return self.bblines

    def commandWindow(self):
        self.cmd = ScrolledText(master=self, height=15, width=50, relief="solid", bd =2)
        self.cmd.grid(row=5, column=0, rowspan=2,  columnspan=6, padx=5, pady=5)

        self.add_timestamp()

    def add_timestamp(self):
        self.cmd.see("end")
        self.after(1000, self.add_timestamp)

    def buttonConnect(self):
        def setup():
            device = self.deviceVar.get()
            if device == 'sim':
                processor.setDevice('sim')
                simPath = filedialog.askopenfilename(initialdir=MusEEG.parentDir+'/data/longRawTrainingSamples', title='choose a .csv file!')
                processor.simPath = simPath
                print('loaded ' + simPath + '!')

            else:
                processor.setDevice(device)
                processor.simulation = False

        self.connectBttn = tk.Button(self, command=setup)
        self.connectBttn["text"] = "setup"
        self.connectBttn.grid(row=8, column=1, columnspan=1, padx=5, pady=5)

    def deviceDropDown(self):
        self.deviceLabel = tk.Label(self, text='pick a device above ^^^')
        self.deviceLabel.grid(row=9, column=0, columnspan=1, padx=0, pady=0)
        self.deviceVar = tk.StringVar(self)
        self.deviceVar.set("sim")

        self.deviceMenu = tk.OptionMenu(self, self.deviceVar, *processor.deviceList).grid(row=8, column=0, columnspan=1, padx=5, pady=5)

    def quitButton(self):
        self.quitbttn = tk.Button(self, text="Shutdown", command=self.quitProcessor).grid(row=9, column=4, padx=5, pady=5)

    def quitProcessor(self):
        # global processor
        # processor.client.done = True
        # processor.processorShutDown()
        print('starting animation shutdown')
        if self.running:
            self.bbani._stop()
            self.bpani._stop()
            self.ani._stop()
            self.sbani._stop()
            print('starting processor shutdown')
            processor.processorShutDown()
            # del processor
            print('processor object deleted')
            print('shutdown! feel free to quit')
        self.master.destroy()

    def midiOSCCOntrolButton(self):
        def createMIDIWindow():
            if not self.MIDIWindowOpen:
                submaster = tk.Toplevel(self)
                submaster.wm_title('MusEEG MIDI')
                midiOSC = MIDIOSCControl(master=submaster, startRow=0, startColumn=0)
                midiOSC.createWidgets()
                processor.sendMIDI = True
                self.MIDIWindowOpen = True

        self.MIDIWindowOpen = False
        button = tk.Button(self, text="Show MIDI Menu", command=createMIDIWindow)
        button.grid(row=9, column=3)

    def create_widgets(self):
        self.winfo_toplevel().title("MusEEG (OSC)")
        self.buttonStartProcessor()
        self.buttonLoadModel()
        self.plotWindow()
        self.commandWindow()
        self.bandPowerWindow()
        self.deviceDropDown()
        self.buttonConnect()
        self.smallBrainMonitor()
        self.bigBrainMonitor()
        self.midiOSCCOntrolButton()
        # self.buttonLoadSmallModel()
        # self.quitButton()

        self.master.protocol("WM_DELETE_WINDOW", self.quitProcessor)
        # replace sys.stdout with our object
        sys.stdout = PrintLogger(self.cmd)
        #


class PrintLogger(): # createa file like object
    def __init__(self, textbox): # pass reference to text widget
        self.textbox = textbox # keep ref

    def write(self, text):
        self.textbox.insert(tk.END, text) # write text to textbox
            # could also scroll to end of textbox here to make sure always visible

    def flush(self): # needed for file like object
        pass


if __name__ == "__main__":
    root = tk.Tk()
    root.lift()
    root.iconbitmap(os.path.join(parentDir, 'museeg-logo.ico'))
    app = App(master=root)



    # todo: the app isnt quitting properly
    while True:
        try:
            print('hello! this is the MusEEG log')
            print('classification results are printed here\n\n')
            flower = [
                "/                   __     __                  /",
                "/                 .'  `...'  `.                /",
                "/               __|     |     |__              /",
                "/             .'    \   .   /    `.            /",
                "/             |      ./###\.      |            /",
                "/              >---- |#####| ----<             /",
                "/             |      `\###/'      |            /",
                "/             `.__ /    .    \ __.'            /",
                "/                 |     |     |                /",
                "/                 `.___.^.___.'                /"]

            for line in flower:
                print(line)

            app.mainloop()
            break
        except UnicodeDecodeError:
            pass
