from MusEEG import eegData, client, classifier, cerebro
from MusEEG import parentDir
import os
import matplotlib.pyplot as plt
import numpy as np
import threading
from osc4py3.as_allthreads import *
from osc4py3 import oscbuildparse
import time

class Processor:
    def __init__(self, simulation=True):
        """
        this is set up rn to simulate an eeg stream, instead of getting data from the client
        """
        self.cerebro = cerebro()
        self.bigBrain = classifier()
        self.bigBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'bigBrain_b1b2_norm'), loadScaler=True)

        self.client = client()

        if simulation:
            #### TEST TEST
            """
            lookright works fine
            hardblink and scrunch are wrong
            lookleft gets confused with smile sometimes
            """
            self.client.simulateStream('testrec_blink', subdir='testfiles', streamSpeed=8)
            # self.client.simulateStream('smile', subdir='trainbatch1', streamSpeed=8)
        else:
            self.client.setup()
            self.client.stream()

        # self.chunkFigure = plt.figure()
        self.streamPlotFigure = plt.figure()
        self.PSDFigure = plt.figure()

    def OSCstart(self, address="127.0.0.1", port=57120, clientName = "MusEEGosc"):
        self.clientNameOSC = clientName
        osc_startup()
        osc_udp_client(address, port, clientName)

    def OSCclose(self):
        osc_terminate()

    def defineOSCMessages(self):
        smileOSC = oscbuildparse.OSCMessage('/smile', None, [440, 0.1])
        eyebrowsOSC = oscbuildparse.OSCMessage('/eyebrows', None, [880, 0.1])
        hardblinkOSC = oscbuildparse.OSCMessage('/hardblink', None, [220, 0.1])
        scrunchOSC = oscbuildparse.OSCMessage('/scrunch', None, [110, 0.1])
        lookleftOSC = oscbuildparse.OSCMessage('/lookleft', None, [1760, 0.1])
        lookrightOSC = oscbuildparse.OSCMessage('/lookright', None, [660, 0.1])
        neutralOSC = oscbuildparse.OSCMessage('/neutral', None, [0, 0.1])

        self.discreteOSCdict = {'smile': smileOSC,
                           'eyebrows': eyebrowsOSC,
                           'hardblink': hardblinkOSC,
                           'scrunch': scrunchOSC,
                           'lookleft': lookleftOSC,
                           'lookright': lookrightOSC,
                           'neutral': neutralOSC}

    def sendOSCMessage(self, message):
        osc_send(message, self.clientNameOSC)
        osc_process()

    def processAndSendOSC(self, eeg):
        brainInput = eeg.process()
        brainOutput = self.bigBrain.classify(brainInput.reshape(1, 350))
        gestureResult = self.cerebro.gestures[brainOutput]

        print('classification result: ' + gestureResult)

        message = self.discreteOSCdict[gestureResult]
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
                        self.stopChunkGetter = False
                        chunkGetter.join()
                    else:
                        print('.')
                        activeGesture = False
                        self.stopChunkGetter = True
                        chunkGetter.join()

                eeg = eegData()

                eeg.chunk = np.array(fullchunk)
                # eeg.plotRawEEG(figure=self.streamPlotFigure)
                if len(eeg.chunk) != eeg.chunkSize:
                    raise RuntimeWarning('this chunk wasn\'t 384 samples. something went wrong')

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
                eeg.chunk = self.client.getChunkWithBackTrack()
                if len(eeg.chunk) != eeg.chunkSize:
                    raise RuntimeError('this chunk did not have the required number of samples. something went wrong')
                eeg.plotRawEEG(figure=self.streamPlotFigure)
                self.processAndSendOSC(eeg)

            except KeyboardInterrupt:
                break

    def runProcessorThread(self, target):
        """
        run the processor in a separate thread
        """
        processorThread = threading.Thread(target=target)
        processorThread.start()

    def processorShutDown(self):
        self.OSCclose()


if __name__ == "__main__":
    processor = Processor(simulation=True)
    processor.OSCstart()
    processor.defineOSCMessages()
    processor.client.initPSDThread()
    processor.client.plotPSD(figure=processor.PSDFigure)
    # processor.mainProcessorWithBackTrack()

    # while True:
    #     processor.sendOSCMessage(processor.discreteOSCdict['smile'])
    #     time.sleep(0.3)
    #     processor.sendOSCMessage(processor.discreteOSCdict['eyebrows'])
    #     time.sleep(0.3)
    #     processor.sendOSCMessage(processor.discreteOSCdict['lookleft'])
    #     time.sleep(0.3)
    #     processor.sendOSCMessage(processor.discreteOSCdict['scrunch'])
    #     print('sent')
    #     time.sleep(0.3)


    # processor.runProcessorThread(target=processor.mainProcessorWithoutBackTrack)
    # processor.client.plotClientStream(processor.streamPlotFigure, plotChunks=False)
    # processor.processorShutDown()