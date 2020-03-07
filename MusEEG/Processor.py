from MusEEG import eegData, client, classifier, cerebro
from MusEEG import parentDir
import os
import numpy as np
import threading
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
import pandas as pd


class Processor:
    def __init__(self, device=None):
        self.cerebro = cerebro()
        self.bigBrain = classifier()

        self.client = client(device=device)

        if device is None:
            self.simulation = True
            self.bigBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'bigBrain_b1b2_norm'),
                                    loadScaler=True)

        elif device == 'emotiv':
            eegData.device = device
            eegData.sampleRate = 256
            eegData.chunkSize = 256*1.25
            eegData.nchannels = 14
            self.bigBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'bigBrain_b1b2_norm'),
                                    loadScaler=True)

        elif device == 'openBCI':
            eegData.device = device
            eegData.sampleRate = 125
            eegData.chunkSize = eegData.chunkSize/2
            eegData.nchannels = 16


        self.sendOSC = True #send OSC messages for facial expressions
        self.sendMIDI = True #send midi messages for facial expressions

        ##these are just some average bandpower values from the neutral track
        self.baseline = [78.72624375770606, 310.0973281373556, 99.40740830852117, 59.90541365434281, 31.977649759096565];
        self.baselinedB = np.log10(self.baseline)

    def startStream(self):
        if self.simulation:
            self.client.simulateStream('smile', subdir='trainbatch1', streamSpeed=4)
        else:
            self.client.setup()
            self.client.stream()

    def OSCstart(self, address="127.0.0.1", port=57120, clientName = "MusEEGosc"):
        self.clientNameOSC = clientName
        osc_startup()
        osc_udp_client(address, port, clientName)

        baselinemsg = oscbuildparse.OSCMessage('/baseline', None, self.baselinedB)
        osc_send(baselinemsg, self.clientNameOSC)
        osc_process()

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

    def processAndPlay(self, eeg):
        brainInput = eeg.process()
        brainOutput = self.bigBrain.classify(brainInput.reshape(1, 350))
        gestureResult = self.cerebro.gestures[brainOutput]

        print('classification result: ' + gestureResult)

        if self.sendOSC:
            message = self.discreteOSCdict[gestureResult]
            osc_send(message, self.clientNameOSC)
            osc_process()

        if self.sendMIDI:
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
        # delta = eegData.dbBandPower(buffer=buffer, band=freqBins[0:2])
        theta = eegData.dbBandPower(buffer=buffer, band=freqBins[1:3])
        alpha = eegData.dbBandPower(buffer=buffer, band=freqBins[2:4])
        beta = eegData.dbBandPower(buffer=buffer, band=freqBins[3:5])
        gamma = eegData.dbBandPower(buffer=buffer, band=freqBins[4:6])

        # deltaAvg = float(np.mean(delta))
        thetaAvg = float(np.mean(theta))
        alphaAvg = float(np.mean(alpha))
        betaAvg  = float(np.mean(beta))
        gammaAvg = float(np.mean(gamma))

        bandPowerArray = np.array([ theta, alpha, beta, gamma])
        print(bandPowerArray)

        bandPowerStr = ['theta', 'alpha', 'beta', 'gamma']
        # put these in a dataframe
        bandPowers = pd.DataFrame(bandPowerArray, index=bandPowerStr)
        bandPowers.columns = eegData.eegChannels
        #send OSC messages
        # deltaOSC = oscbuildparse.OSCMessage('/delta', None, [deltaAvg])
        thetaOSC = oscbuildparse.OSCMessage('/theta', None, [thetaAvg])
        alphaOSC = oscbuildparse.OSCMessage('/alpha', None, [alphaAvg])
        betaOSC = oscbuildparse.OSCMessage('/beta', None, [betaAvg])
        gammaOSC = oscbuildparse.OSCMessage('/gamma', None, [gammaAvg])

        OSCmsglist = [  thetaOSC, alphaOSC, betaOSC, gammaOSC]

        for message in OSCmsglist:
            osc_send(message, self.clientNameOSC)
            osc_process()

        # self.bandPowerFigure = Figure()
        # eegData.bandPowerHistogram(bandPowers, figure=self.bandPowerFigure)

    def bandPowerThread(self, asThread=True):
        def bandPowerLoop():
            while True:
                self.bandPowerProcessorOld()

        if asThread:
            thread = threading.Thread(target=bandPowerLoop)
            thread.start()
        else:
            bandPowerLoop()

    def mainProcessorWithSmallBrain(self):
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
                        print('facial expression found!')
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
                    raise RuntimeWarning('chunk size error')

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
                    raise RuntimeError('this chunk did not have the '
                                       'required number of samples. something went wrong')
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

    """
    old methods I'm not ready to let go of yet
    """
    # def sendOSCMessage(self, message):
    #     print(message)
    #     osc_send(message, self.clientNameOSC)
    #     osc_process()

    # def processAndSendOSC(self, eeg):
    #     brainInput = eeg.process()
    #     brainOutput = self.bigBrain.classify(brainInput.reshape(1, 350))
    #     gestureResult = self.cerebro.gestures[brainOutput]
    #
    #     print('classification result: ' + gestureResult)
    #
    #     message = self.discreteOSCdict[gestureResult]
    #     osc_send(message, self.clientNameOSC)
    #     osc_process()
    # def bandPowerProcessor(self):
    #     buffer = self.client.getBuffer(bufferSize=128)
    #     freqBins = {'delta': [0.5, 4],
    #                 'theta': [4, 8],
    #                 'alpha': [8, 12],
    #                 'beta': [12, 30],
    #                 'gamma': [30, 60]}
    #     bandPowerArray = []
    #     bandPowerAvg = []
    #     for key in freqBins:
    #         band = eegData.bandPower(buffer=buffer, band=freqBins[key])
    #         bandPowerArray.append(np.array(band))
    #         bandPowerAvg.append(float(np.mean(band)))
    #
    #     fBinKeys = list(freqBins.keys())
    #     dfBandPower = pd.DataFrame(bandPowerArray, index=fBinKeys)
    #     dfBandPower.columns = eegData.eegChannels
    #
    #     bandPowerDict = dict(zip(fBinKeys, bandPowerAvg))
    #
    #     OSCmsglist = []
    #     for key in bandPowerDict:
    #         thing = bandPowerDict[key]
    #         tag = '/' + key
    #         msg = oscbuildparse.OSCMessage(tag, None, float(thing))
    #         OSCmsglist.append(msg)
    #
    #     for message in OSCmsglist:
    #         osc_send(message, self.clientNameOSC)

    # plot histogram
    # eegData.bandPowerHistogram(dfBandPower, figure=self.bandPowerFigure)

if __name__ == "__main__":
    processor = Processor(device=None)
    processor.OSCstart()
    processor.defineOSCMessages()
    # processor.runProcessorThread(target=processor.mainProcessorWithSmallBrain)
    processor.startStream()
    processor.bandPowerThread(asThread=False)