import os
import MusEEG
from MusEEG import eegData, classifier, client, cerebro
from MusEEG.music import chord
import numpy as np
import threading
import time

cerebro = cerebro()

client = client()
client.setup()
client.stream()

def mainProcessor():

    stopChunkGetter=False
    def getMoreChunks(chunk):
        while len(chunk) < eegData.chunkSize:
            chunk.extend(list(client.getChunk(chunkSize=eegData.smallchunkSize)))
            if stopChunkGetter:
                break

    while (True):
        try:
            checkpoint1 = time.time()
            activeGesture = False
            while not activeGesture:
                eeg = eegData()
                eeg.chunk = client.getChunk(chunkSize=eegData.smallchunkSize)

                fullchunk = list(eeg.chunk)
                chunkGetter = threading.Thread(target=getMoreChunks, args=(fullchunk,))
                chunkGetter.start()

                brainInput = eeg.process()
                brainOutput = cerebro.smallBrain.classify(brainInput.reshape(1, 350))
                if brainOutput == 0:
                    print('gesture found')
                    activeGesture = True
                    stopChunkGetter = False
                    chunkGetter.join()
                else:
                    print('no gesture found')
                    stopChunkGetter = True
                    chunkGetter.join()


            checkpoint2 = time.time()

            checkpoint3 = time.time()
            eeg = eegData()

            eeg.chunk = np.array(fullchunk)
            eeg.plotRawEEG()

            checkpoint4 = time.time()

            def processAndPlay(eeg):
                # print('performing wavelet transform')
                brainInput = eeg.process()

                # classify facial gesture in DNN
                brainOutput = cerebro.bigBrain.classify(brainInput.reshape(1, 350))
                # print('\nthe neural network has taken the brain signal and classified it.')
                gestureResult = cerebro.gestures[brainOutput]
                print('classification result: ' + gestureResult)

                resultingChord = cerebro.mididict[gestureResult]

                resultingChord.playchord()

            processor = threading.Thread(target=processAndPlay, args=(eeg,))
            processor.start()

            checkpoint5 = time.time()

            print('checkpoint2 =' + str(checkpoint2 - checkpoint1))
            print(checkpoint3 - checkpoint2)
            print(checkpoint4 - checkpoint3)
            print(checkpoint5 - checkpoint4)

        except KeyboardInterrupt:
            break



if __name__=="__main__":
    mainProcessor()