import tkinter as tk
import MusEEG
from MusEEG import Processor, eegData
from tkinter import filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation

processor = Processor(device=None)
processor.OSCstart()
processor.defineOSCMessages()

def get_data():
    x, y = processor.client.getPlotData()
    return x, y

class demoApp(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

        self.running = False
        self.ani = None

    def buttonLoadModel(self):
        def loadModel():
            path = filedialog.askdirectory(initialdir=MusEEG.parentDir+'/data/savedModels', title='load classifier')
            processor.bigBrain.loadmodel(filename=path, loadScaler=True)

        loadModelBttn = tk.Button(self, command=loadModel)
        loadModelBttn["text"] = "Load Model"
        loadModelBttn.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def buttonStartProcessor(self):

        self.startProcessorBttn = tk.Button(self, command=self.on_click)
        self.startProcessorBttn["text"] = "Start Processor"
        self.startProcessorBttn.grid(row=5, column=1, columnspan=2, padx=5, pady=5)

    def plotWindow(self):
        self.fig = plt.Figure()
        self.ax1 = self.fig.add_subplot(111)
        self.line, = self.ax1.plot([], [], lw=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=5, columnspan=4)

        self.ax1.set_ylim(0, 1500)
        self.ax1.set_xlim(0, processor.client.windowSize/eegData.sampleRate)

    def on_click(self):
        '''the button is a start, pause and unpause button all in one
        this method sorts out which of those actions to take'''
        if self.ani is None:
            processor.startStream()
            processor.runProcessorThread(target=processor.mainProcessorWithSmallBrain)
            processor.bandPowerThread(asThread=True)
            # animation is not running; start it
            return self.start()

        if self.running:
            # animation is running; pause it
            self.ani.event_source.stop()
            self.startProcessorBttn.config(text='Un-Pause')
        else:
            # animation is paused; unpause it
            self.ani.event_source.start()
            self.startProcessorBttn.config(text='Pause')
        self.running = not self.running

    def start(self):
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update_graph,
            interval=processor.client.windowSize/8/eegData.sampleRate*1000,
            repeat=False)
        self.running = True
        self.startProcessorBttn.config(text='Pause')
        self.ani._start()
        print('started animation')

    def update_graph(self, i):
        self.line.set_data(*get_data()) # update graph

        return self.line,
        
    def create_widgets(self):
        self.winfo_toplevel().title("MusEEG (SuperCollider)")
        self.buttonStartProcessor()
        self.buttonLoadModel()
        self.plotWindow()



root = tk.Tk()
app = demoApp(master=root)



#todo: the app isnt quitting properly and it ruins ur computer
while True:
    try:
        app.mainloop()
        break
    except UnicodeDecodeError:
        pass