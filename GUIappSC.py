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

processor = Processor(device=None)
processor.OSCstart()
processor.defineOSCMessages()

def get_data_raw():
    x, y = processor.client.getPlotData()
    return x, y

global lastbandpwr
lastbandpwr = [[0, 1, 2, 3], processor.baselinedB]

def get_data_bp():
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

class demoApp(tk.Frame):

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
        loadModelBttn["text"] = "Load Model"
        loadModelBttn.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

    def buttonStartProcessor(self):
        self.startProcessorBttn = tk.Button(self, command=self.on_click)
        self.startProcessorBttn["text"] = "Start Processor"
        self.startProcessorBttn.grid(row=8, column=2, columnspan=2, padx=5, pady=5)

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
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=5, columnspan=4)

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
        self.bpcanvas.get_tk_widget().grid(row=5, column=3, rowspan=2, columnspan=2)

        self.bpax1.set_ylim(0, 40)
        self.bpax1.set_title('Band Power (dB)')
        self.bpax1.set_xlim(-1, 4)
        self.bpax1.set_xticklabels(['', 'theta', 'alpha', 'beta', 'gamma', ''])

    def on_click(self):
        '''the button is a start, pause and unpause button all in one
        this method sorts out which of those actions to take'''
        if self.ani is None:
            processor.startStream()
            processor.runProcessorThread(target=processor.mainProcessorWithSmallBrain)
            processor.bandPowerThread(asThread=True)
            # animation is not running; start it
            return self.start()

        # if self.running:
        #     # animation is running; pause it
        #     self.ani.event_source.stop()
        #     self.startProcessorBttn.config(text='Un-Pause')
        # else:
        #     # animation is paused; unpause it
        #     self.ani.event_source.start()
        #     self.startProcessorBttn.config(text='Pause')
        # self.running = not self.running

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
        self.running = True
        # self.startProcessorBttn.config(text='Pause')
        self.ani._start()
        self.bpani._start()
        print('started animation')

    def update_graph(self, i):
        x, y = get_data_raw()

        for idx, line in enumerate(self.lines):
            line.set_data(x, y[:,idx])

        return self.lines

    def update_graph_bp(self, i):
        x, y = get_data_bp()
        if y is not None:
            self.bpline.set_data(x, y)

        return self.bpline

    def commandWindow(self):
        self.cmd = ScrolledText(master=self, height=10, width=50, relief="solid")
        self.cmd.grid(row=5, column=0, rowspan=3,  columnspan=2, padx=5, pady=5)

        self.add_timestamp()

    def add_timestamp(self):
        self.cmd.see("end")
        self.after(1000, self.add_timestamp)


    def create_widgets(self):
        self.winfo_toplevel().title("MusEEG (OSC)")
        self.buttonStartProcessor()
        self.buttonLoadModel()
        self.plotWindow()
        self.commandWindow()
        self.bandPowerWindow()

        pl = PrintLogger(self.cmd)

        # replace sys.stdout with our object
        sys.stdout = pl

class PrintLogger(): # create file like object
    def __init__(self, textbox): # pass reference to text widget
        self.textbox = textbox # keep ref

    def write(self, text):
        self.textbox.insert(tk.END, text) # write text to textbox
            # could also scroll to end of textbox here to make sure always visible

    def flush(self): # needed for file like object
        pass

def quit_properly():
    processor.processorShutDown()
    del processor

root = tk.Tk()
root.lift()
root.iconbitmap(os.path.join(parentDir, 'museeg-logo.ico'))
root.protocol("WM_DELETE_WINDOW_", quit_properly)
app = demoApp(master=root)

#todo: the app isnt quitting properly
while True:
    try:
        print('hello! this is the MusEEG log')
        print('classification results are printed here\n\n')
        app.mainloop()
        break
    except UnicodeDecodeError:
        pass