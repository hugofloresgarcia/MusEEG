import tkinter as tk
from MusEEG import eegData, classifier, client, cerebro, parentDir
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

def processAndPlay(eeg):
    brainInput = eeg.process()
    brainOutput = cerebro.bigBrain.classify(brainInput.reshape(1, 350))
    gestureResult = cerebro.gestures[brainOutput]

    print('classification result: ' + gestureResult)

    resultingChord = cerebro.mididict[gestureResult]
    resultingChord.playchord()

def mainProcessorWithBackTrack():
    while (True):
        try:
            if client.done:
                break
            eeg = eegData()
            # client.plotClientStream(figure)
            eeg.chunk = client.getChunkWithBackTrack()
            # eeg.plotRawEEG(figure=figure)
            # if len(eeg.chunk) != eeg.chunkSize:
            # raise RuntimeError('this chunk wasn\'t 384 samples. something went wrong')

            processAndPlay(eeg)

        except KeyboardInterrupt:
            break


class demoApp(tk.Frame):
    """
    mastermind inits
    """
    cerebro = cerebro()
    cerebro.bigBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'bigBrain_v3'))
    client = client()
    client.simulateStream('testrec_lookleft', subdir='testfiles', streamSpeed=1)
    streamPlotFigure = plt.figure()

    def __init__(self, master=None):
        super().__init__(master)

        self.master = master
        self.pack()
        self.create_widgets()

    def plotWindow(self):
        self.canvas = FigureCanvasTkAgg(client.plotClientStream(), self)
        self.canvas.draw()
        # self.canvas.get_tk_widget().pack(side="right", expand=True)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=11, columnspan=3, padx=5, pady=5)

    def create_widgets(self):
        self.winfo_toplevel().title("MusEEG")

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
