from MusEEG import eegData, classifier, client, cerebro
from MusEEG import parentDir
import os
import matplotlib.pyplot as plt
import numpy as np
import threading


"""
this is set up rn to simulate an eeg stream, instead of getting data from the client
"""

cerebro = cerebro()
cerebro.bigBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'bigBrain_v3'))

client = client()
# client.setup()
# client.stream()
#### TEST TEST
"""
lookright works fine
eyebrows and scrunch are wrong
lookleft gets confused with lookright sometimes
"""
client.simulateStream('smile', subdir='trainbatch2', streamSpeed=1)

# figure = plt.figure()
chunkFigure = plt.figure()
streamPlotFigure = plt.figure()


def processAndPlay(eeg):
    brainInput = eeg.process()
    brainOutput = cerebro.bigBrain.classify(brainInput.reshape(1, 350))
    gestureResult = cerebro.gestures[brainOutput]

    print('classification result: ' + gestureResult)

    resultingChord = cerebro.mididict[gestureResult]
    resultingChord.playchord()

def mainProcessor():
    stopChunkGetter = False

    def getMoreChunks(chunk):
        while len(chunk) < eegData.chunkSize:
            chunk.extend(list(client.getChunk(chunkSize=eegData.smallchunkSize)))
            if stopChunkGetter:
                break

    while (True):
        try:
            activeGesture = False
            while not activeGesture:
                eeg = eegData()
                eeg.chunk = client.getChunk(chunkSize=eegData.smallchunkSize)

                eeg.plotRawEEG(figure=chunkFigure)

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
                    print('.')
                    activeGesture = False
                    stopChunkGetter = True
                    chunkGetter.join()

            eeg = eegData()

            eeg.chunk = np.array(fullchunk)
            eeg.plotRawEEG(figure=chunkFigure)

            # if len(eeg.chunk) != eeg.chunkSize:
            # raise RuntimeError('this chunk wasn\'t 384 samples. something went wrong')

            processor = threading.Thread(target=processAndPlay, args=(eeg,))
            processor.start()

        except KeyboardInterrupt:
            break


def mainProcessorWithBackTrack():
    while (True):
        try:
            if client.done:
                break
            eeg = eegData()
            # client.plotClientStream(figure)
            eeg.chunk = client.getChunkWithBackTrack()
            if len(eeg.chunk) != eeg.chunkSize:
                raise RuntimeError('this chunk wasn\'t 384 samples. something went wrong')

            processAndPlay(eeg)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    processorThread = threading.Thread(target=mainProcessorWithBackTrack).start()
    client.plotClientStream(streamPlotFigure, chunkFigure)