from MusEEG import eegData, client, classifier, cerebro
from MusEEG import parentDir
import os
import matplotlib.pyplot as plt
import numpy as np
import threading
from osc4py3.as_allthreads import *
from osc4py3 import oscmethod as osm

class Processor:
    def __init__(self, simulation=True):
        """
        this is set up rn to simulate an eeg stream, instead of getting data from the client
        """
        self.cerebro = cerebro()
        self.bigBrain = classifier()
        self.bigBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'bigBrain_batch2_320samples'))

        self.client = client()

        if simulation:
            #### TEST TEST
            """
            lookright works fine
            eyebrows and scrunch are wrong
            lookleft gets confused with lookright sometimes
            """
            # self.client.simulateStream('smile', subdir='trainbatch2', streamSpeed=4)
            self.client.simulateStream('smile', subdir='trainbatch2', streamSpeed=1)
        else:
            self.client.setup()
            self.client.stream()

        self.chunkFigure = plt.figure()
        self.streamPlotFigure = plt.figure()

    def OSCstart(self, address="192.168.0.0", port=3721, clientName = "MusEEGosc"):
        self.clientNameOSC = clientName

        osc_startup()
        osc_udp_client(address, port, clientName)

    def OSCclose(self):
        osc_terminate()

    def processAndSendOSC(self, eeg, message):
        brainInput = eeg.process()
        brainOutput = self.bigBrain.classify(brainInput.reshape(1, 350))
        gestureResult = self.cerebro.gestures[brainOutput]

        print('classification result: ' + gestureResult)

        osc_send(message, self.clientNameOSC)
        osc_process()

    def processAndPlay(self, eeg):
        brainInput = eeg.process()
        brainOutput = self.bigBrain.classify(brainInput.reshape(1, 350))
        gestureResult = self.cerebro.gestures[brainOutput]

        print('classification result: ' + gestureResult)

        resultingChord = self.cerebro.mididict[gestureResult]
        resultingChord.playchord()


    def getMoreChunks(self, chunk):
        while len(chunk) < eegData.chunkSize:
            chunk.extend(list(self.client.getChunk(chunkSize=eegData.smallchunkSize)))
            if self.stopChunkGetter:
                break

    def mainProcessorWithoutBackTrack(self):
        self.stopChunkGetter = False
        while (True):
            try:
                activeGesture = False
                while not activeGesture:
                    eeg = eegData()
                    eeg.chunk = self.client.getChunk(chunkSize=eegData.smallchunkSize)

                    fullchunk = list(eeg.chunk)
                    chunkGetter = threading.Thread(target=self.getMoreChunks, args=(fullchunk,))
                    chunkGetter.start()

                    brainInput = eeg.process()
                    brainOutput = self.cerebro.smallBrain.classify(brainInput.reshape(1, 350))

                    if brainOutput == 0:
                        print('gesture found')
                        activeGesture = True
                        stopChunkGetter = False
                        chunkGetter.join()
                    else:
                        print('.')
                        activeGesture = False
                        stopChunkGetter = True
                        chunkGetter.join()

                eeg = eegData()

                eeg.chunk = np.array(fullchunk)

                # if len(eeg.chunk) != eeg.chunkSize:
                # raise RuntimeError('this chunk wasn\'t 384 samples. something went wrong')

                processor = threading.Thread(target=self.processAndPlay, args=(eeg,))
                processor.start()

            except KeyboardInterrupt:
                break


    def mainProcessorWithBackTrack(self):
        while (True):
            try:
                if self.client.done:
                    break
                eeg = eegData()
                # self.client.plotClientStream(figure)
                eeg.chunk = self.client.getChunkWithBackTrack()
                if len(eeg.chunk) != eeg.chunkSize:
                    raise RuntimeError('this chunk did not have the required number of samples. something went wrong')

                self.processAndPlay(eeg)

            except KeyboardInterrupt:
                break

    def runProcessorThread(self):
        """
        run the processor in a separate thread
        """
        processorThread = threading.Thread(target=self.mainProcessorWithoutBackTrack)
        processorThread.start()

    def processorShutDown(self):
        self.OSCclose()



if __name__ == "__main__":
    processor = Processor()
    processor.runProcessorThread()
    processor.client.plotClientStream(processor.streamPlotFigure, processor.chunkFigure)
    processor.processorShutDown()