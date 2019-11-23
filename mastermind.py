import os
import MusEEG
from MusEEG import eegData, classifier, client, cerebro
from MusEEG.music import chord
import numpy as np
import threading

cerebro = cerebro()

client = client()
client.setup()
client.stream()

def mainProcessor():
    while (True):
        try:
            activeGesture = False
            while not activeGesture:
                eeg = eegData()
                eeg.chunk = client.getChunk(chunkSize=eegData.smallchunkSize)
                brainInput = eeg.process()
                brainOutput = cerebro.smallBrain.classify(brainInput.reshape(1, 350))
                if brainOutput is not 1:
                    chunk = list(eeg.chunk)
                    print('gesture found')
                    activeGesture = True

            while len(chunk) < eegData.chunkSize:
                chunk.extend(list(client.getChunk(chunkSize=eegData.smallchunkSize)))

            eeg = eegData()

            eeg.chunk = np.array(chunk)
            eeg.plotRawEEG()

            brainInput = eeg.process()

            # classify facial gesture in DNN
            brainOutput = cerebro.bigBrain.classify(brainInput.reshape(1, 350))
            gestureResult = cerebro.gestures[brainOutput]
            print('classification result: ' + gestureResult)

            # refer classification to midi dictionary and refer chord object to musician
            resultingChord = cerebro.mididict[gestureResult]

            musician = threading.Thread(target=resultingChord.playchord())
            musician.start()
        except KeyboardInterrupt:
            break



if __name__=="__main__":
    mainProcessor()