from MusEEG import eegData, client, classifier, cerebro
from MusEEG import parentDir
import os
import matplotlib.pyplot as plt
import numpy as np
import threading
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
import time
import pandas as pd

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
            self.client.simulateStream('vid', subdir='testfiles', streamSpeed=1)
            # self.client.simulateStream('smile', subdir='trainbatch1', streamSpeed=1)
        else:
            self.client.setup()
            self.client.stream()

        # self.chunkFigure = plt.figure()
        self.streamPlotFigure = plt.figure()
        # self.PSDFigure = plt.figure()
        self.bandPowerFigure = plt.figure()

    def OSCstart(self, address="127.0.0.1", port=57120, clientName = "MusEEGosc"):
        self.clientNameOSC = clientName
        osc_startup()
        osc_udp_client(address, port, clientName)

    def OSCclose(self):
        osc_terminate()

    def defineOSCMessages(self):
        smileOSC = oscbuildparse.OSCMessage('/smile', None, ['true'])
        eyebrowsOSC = oscbuildparse.OSCMessage('/eyebrows', None, ['true'])
        hardblinkOSC = oscbuildparse.OSCMessage('/hardblink', None, ['true'])
        scrunchOSC = oscbuildparse.OSCMessage('/scrunch', None, ['true'])
        lookleftOSC = oscbuildparse.OSCMessage('/lookleft', None, ['true'])
        lookrightOSC = oscbuildparse.OSCMessage('/lookright', None, ['true'])
        neutralOSC = oscbuildparse.OSCMessage('/neutral', None, ['true'])

        self.discreteOSCdict = {'smile': smileOSC,
                           'eyebrows': eyebrowsOSC,
                           'hardblink': hardblinkOSC,
                           'scrunch': scrunchOSC,
                           'lookleft': lookleftOSC,
                           'lookright': lookrightOSC,
                           'neutral': neutralOSC}

    def sendOSCMessage(self, message):
        print(message)
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

    def bandPowerProcessorOld(self):
        buffer = self.client.getBuffer(bufferSize=128)
        freqBins = [0.5, 4, 8, 12, 30, 60]

        # compute delta, theta, alpha, beta, bands
        delta = eegData.bandPower(buffer=buffer, band=freqBins[0:2])
        theta = eegData.bandPower(buffer=buffer, band=freqBins[1:3])
        alpha = eegData.bandPower(buffer=buffer, band=freqBins[2:4])
        beta = eegData.bandPower(buffer=buffer, band=freqBins[3:5])
        gamma = eegData.bandPower(buffer=buffer, band=freqBins[4:6])

        deltaAvg = float(np.mean(delta))
        thetaAvg = float(np.mean(theta))
        alphaAvg = float(np.mean(alpha))
        betaAvg = float(np.mean(beta))
        gammaAvg = float(np.mean(gamma))

        bandPowerArray = np.array([delta, theta, alpha, beta, gamma])
        bandPowerStr = ['delta', 'theta', 'alpha', 'beta', 'gamma']
        # put these in a dataframe
        bandPowers = pd.DataFrame(bandPowerArray, index=bandPowerStr)
        bandPowers.columns = eegData.eegChannels
        #send OSC messages
        deltaOSC = oscbuildparse.OSCMessage('/delta', None, [0, deltaAvg])
        thetaOSC = oscbuildparse.OSCMessage('/theta', None, [0, thetaAvg])
        alphaOSC = oscbuildparse.OSCMessage('/alpha', None, [0, alphaAvg])
        betaOSC = oscbuildparse.OSCMessage('/beta', None, [0, betaAvg])
        gammaOSC = oscbuildparse.OSCMessage('/beta', None, [0, gammaAvg])

        OSCmsglist = [deltaOSC, thetaOSC, alphaOSC, betaOSC, gammaOSC]

        for message in OSCmsglist:
            osc_send(message, self.clientNameOSC)
            osc_process()

        # eegData.bandPowerHistogram(dfBandPower, figure=self.bandPowerFigure)

    def bandPowerProcessor(self):
        buffer = self.client.getBuffer(bufferSize=128)
        freqBins = {'delta': [0.5, 4],
                    'theta': [4, 8],
                    'alpha': [8, 12],
                    'beta': [12, 30],
                    'gamma': [30, 60]}
        bandPowerArray = []
        bandPowerAvg = []
        for key in freqBins:
            band = eegData.bandPower(buffer=buffer, band=freqBins[key])
            bandPowerArray.append(np.array(band))
            bandPowerAvg.append(float(np.mean(band)))

        fBinKeys = list(freqBins.keys())
        dfBandPower = pd.DataFrame(bandPowerArray, index=fBinKeys)
        dfBandPower.columns = eegData.eegChannels

        bandPowerDict = dict(zip(fBinKeys, bandPowerAvg))

        OSCmsglist = []
        for key in bandPowerDict:
            thing = bandPowerDict[key]
            tag = '/' + key
            msg = oscbuildparse.OSCMessage(tag, None, float(thing))
            OSCmsglist.append(msg)

        for message in OSCmsglist:
            osc_send(message, self.clientNameOSC)
            # osc_process()
            # print(message)

        #plot histogram
        eegData.bandPowerHistogram(dfBandPower, figure=self.bandPowerFigure)

    def bandPowerThread(self, asThread=True):
        def bandPowerLoop():
            while True:
                self.bandPowerProcessorOld()

        if asThread:
            thread = threading.Thread(target=bandPowerLoop)
            thread.start()
        else:
            bandPowerLoop()

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
                eeg.plotRawEEG(figure=self.streamPlotFigure)
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
                # eeg.plotRawEEG(figure=self.streamPlotFigure)
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
    processor = Processor(simulation=False)
    processor.OSCstart()
    processor.defineOSCMessages()
    processor.bandPowerThread(asThread=False)
    # processor.mainProcessorWithoutBackTrack()
    # processor.runProcessorThread(target=processor.mainProcessorWithBackTrack)
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