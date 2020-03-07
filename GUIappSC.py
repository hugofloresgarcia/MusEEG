import tkinter as tk
import MusEEG
from MusEEG import Processor
from tkinter import filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')

processor = Processor(device=None)
processor.OSCstart()
processor.defineOSCMessages()

style.use("ggplot")

class demoApp(tk.Frame):

    def __init__(self, master=None):
        self.plotFigure = Figure(figsize=(5,4), dpi=100)
        self.plotSubplot = self.plotFigure.add_subplot(111)
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
        loadModelBttn.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def buttonStartProcessor(self):
        def startProcessor():
            processor.startStream()
            processor.runProcessorThread(target=processor.mainProcessorWithSmallBrain)
            processor.bandPowerThread(asThread=True)
            global ani
            ani = animation.FuncAnimation(self.plotFigure, processor.client.animatePlot, interval=1000)


        startProcessorBttn = tk.Button(self, command=startProcessor)
        startProcessorBttn["text"] = "Start Processor"
        startProcessorBttn.grid(row=5, column=1, columnspan=2, padx=5, pady=5)


    def plotWindow(self):
        self.plotSubplot.set_ylim(-300, 400 * 20)
        self.plotSubplot.add_line(processor.client.plotLine)

        canvas = FigureCanvasTkAgg(self.plotFigure, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, rowspan=5, columnspan=4)
        
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