from MusEEG import eegData, client, classifier, cerebro
from audiolazy.lazy_midi import str2midi
from MusEEG import parentDir
import os
import numpy as np
import threading
from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse
import pandas as pd
import queue
import pickle

import time

class Processor:
    def __init__(self):
        self.cerebro = cerebro()
        self.bigBrain = classifier()

        self.smallBrain = classifier()
        self.smallBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'smallBrain_v5_norm'), loadScaler=True)

        self.client = client()

        self.bandPowerQueue = queue.Queue()
        self.smallBrainMonitorQueue = queue.Queue()
        self.bigBrainMonitorQueue = queue.Queue()

        self.simPath = ''

        self.deviceList = ['sim', 'emotiv', 'OpenBCI']

        self.sendOSC = True #send OSC messages for facial expressions

        self.sendMIDI = True #send midi chords for facial expressions
        self.GUIcontrol = False #get arpeggio/scramble/duration messages from GUI
        self.arpBool = False
        self.scrambleBool = False
        self.durVal = 0.5
        self.numRepeats = 8

        self.mididict =dict(zip(self.cerebro.gestures, [["C4", "E4", "G4"] for i in range(0, len(self.cerebro.gestures))]))

        ##these are just some average bandpower values from the neutral track
        self.baseline = [310.0973281373556, 99.40740830852117, 59.90541365434281, 31.977649759096565]
        self.baselinedB = np.log10(self.baseline)

    def setDevice(self, device):
        self.device = device

        if self.device is None or 'sim':
            self.client.device = None
            self.simulation = True
            self.bigBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'bigBrain_v5_norm'),
                                    loadScaler=True)

        elif self.device == 'emotiv':
            eegData.device = self.device
            self.client.device = self.device
            eegData.sampleRate = 256
            eegData.chunkSize = 256*1.25
            eegData.nchannels = 14
            self.bigBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'bigBrain_v5_norm'),
                                    loadScaler=True)
            self.simulation = False

        elif self.device == 'openBCI':
            eegData.device = self.device
            self.client.device = self.device
            eegData.sampleRate = 125
            eegData.chunkSize = eegData.chunkSize/2
            eegData.nchannels = 16
            self.simulation = False

        self.client.setup(device)

    def startStream(self):
        if self.simulation:
            self.client.simulateStream(self.simPath, streamSpeed=1)
        else:
            self.client.setup(self.device)
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

    def sendChordSC(self, chord):
        midiChord = [str2midi(note) for note in chord]
        chordOSC = oscbuildparse.OSCMessage('/chord', None, midiChord)
        arpeggiateOSC = oscbuildparse.OSCMessage('/arpeggiate', None, [self.arpBool])
        durationOSC = oscbuildparse.OSCMessage('/duration', None, [self.durVal])
        scrambleOSC = oscbuildparse.OSCMessage('/scramble', None, [self.scrambleBool])
        numRepeatsOSC = oscbuildparse.OSCMessage('/numRepeats', None, [self.numRepeats])

        messages = [arpeggiateOSC, durationOSC, scrambleOSC, chordOSC, numRepeatsOSC]

        for msg in messages:
            osc_send(msg, self.clientNameOSC)
            osc_process()
            # print(msg)


    def updateMIDIdict(self, chordlistlist):
        for index, c in enumerate(chordlistlist):
            gestureBeingDefined = self.cerebro.gestures[index]
            self.mididict[gestureBeingDefined] = c
            print(self.mididict)

    def saveMIDIdict(self, addressPath):
        with open(os.path.join(addressPath), 'wb') as handle:
            pickle.dump(self.mididict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def loadMIDIdict(self, addressPath):
        with open(addressPath, 'rb') as handle:
            self.mididict = pickle.load(handle)
            return self.mididict

    def processAndPlay(self, eeg):
        TIMEstart = time.clock()
        brainInput = eeg.process()
        brainOutput = self.bigBrain.classify(brainInput.reshape(1, 350))
        gestureResult = self.cerebro.gestures[brainOutput]

        print('i found a ' + gestureResult + '!')

        if self.sendOSC:
            message = self.discreteOSCdict[gestureResult]
            osc_send(message, self.clientNameOSC)
            osc_process()

        if self.sendMIDI:
            resultingChord = self.mididict[gestureResult]
            self.sendChordSC(resultingChord)
            osc_process()

        TIMEend = time.clock()
        print('classification took ' + str(round(TIMEend-TIMEstart, 3)) + ' s')
        print('...')

    def getMoreChunks(self, chunk):
        while len(chunk) < eegData.chunkSize:
            chunk.extend(list(self.client.getChunk(chunkSize=eegData.smallchunkSize)))
            if self.stopChunkGetter:
                break

    def bandPowerProcessor(self):
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

        OSCmsglist = [thetaOSC, alphaOSC, betaOSC, gammaOSC]

        queueX = bandPowerStr
        queueY = [thetaAvg, alphaAvg, betaAvg, gammaAvg]
        self.bandPowerQueue.put([queueX, queueY])

        for message in OSCmsglist:
            osc_send(message, self.clientNameOSC)
            osc_process()

        # self.bandPowerFigure = Figure()
        # eegData.bandPowerHistogram(bandPowers, figure=self.bandPowerFigure)

    def bandPowerThread(self, asThread=True):
        def bandPowerLoop():
            while True:
                self.bandPowerProcessor()

        if asThread:
            thread = threading.Thread(target=bandPowerLoop)
            thread.start()
        else:
            bandPowerLoop()

    def mainProcessorWithSmallBrain(self):
        self.stopChunkGetter = False
        while not self.client.done:
            try:
                activeGesture = False
                while not activeGesture:
                    eeg = eegData()
                    eeg.chunk = self.client.getChunk(chunkSize=eegData.smallchunkSize)

                    fullchunk = list(eeg.chunk)
                    chunkGetter = threading.Thread(target=self.getMoreChunks, args=(fullchunk,))
                    chunkGetter.start()
                    eeg.chunk = np.array(eeg.chunk)
                    self.smallBrainMonitorQueue.put(eeg.chunk)
                    brainInput = eeg.process()
                    brainOutput = self.smallBrain.classify(brainInput.reshape(1, 350))

                    if brainOutput == 0:
                        activeGesture = True
                        self.stopChunkGetter = False
                        chunkGetter.join()
                    else:
                        print('...')
                        activeGesture = False
                        self.stopChunkGetter = True
                        chunkGetter.join()

                eeg = eegData()

                eeg.chunk = np.array(fullchunk)
                # eeg.plotRawEEG(figure=self.streamPlotFigure)
                if len(eeg.chunk) != eeg.chunkSize:
                    print('chunk size error')

                self.bigBrainMonitorQueue.put(eeg.chunk)
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
                eeg.chunk = np.array(self.client.getChunkWithBackTrack())

                self.bigBrainMonitorQueue.put(eeg.chunk)

                if len(eeg.chunk) != eeg.chunkSize:
                    raise RuntimeError('this chunk did not have the '
                                       'required number of samples. something went wrong')
                self.processAndPlay(eeg)
                time.sleep(20e-3) #try sleeping 20 ms to  debounce

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
        self.client.done


if __name__ == "__main__":
    processor = Processor(device=None)
    processor.OSCstart()
    processor.defineOSCMessages()
    processor.startStream()
    processor.runProcessorThread(target=processor.mainProcessorWithSmallBrain)
    processor.bandPowerThread(asThread=True)