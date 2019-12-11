from MusEEG import eegData, classifier, client, cerebro
import numpy as np
import threading

cerebro = cerebro()

client = client()
# client.setup()
# client.stream()
client.simulateStream('scrunch')

def mainProcessor():

    stopChunkGetter=False
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
                    activeGesture=False
                    stopChunkGetter = True
                    chunkGetter.join()

            eeg = eegData()

            eeg.chunk = np.array(fullchunk)
            eeg.plotRawEEG()
            print(len(eeg.chunk))

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


        except KeyboardInterrupt:
            break

def mainProcessorBigChunks():
    while (True):
        try:
            eeg = eegData()

            eeg.chunk = client.getChunk(chunkSize=eeg.chunkSize)
            print(len(eeg.chunk))

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


        except KeyboardInterrupt:
            break


if __name__=="__main__":
    mainProcessor()