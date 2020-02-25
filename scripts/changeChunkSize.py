from MusEEG import TrainingDataMacro, eegData
from MusEEG import parentDir
import os

oldsubdir = os.path.join('trainbatch1', 'bigChunks')
newsubdir = os.path.join('trainbatch1_320samples', 'bigChunks')
gestures = ['eyebrows']
gestureobjs = []

for gestItem in gestures:
    workingDir = os.path.join(parentDir, 'data', 'savedChunks', oldsubdir)
    idx = 0
    filesInFolder = [file for file in os.listdir(workingDir) if os.path.isfile(os.path.join(workingDir, file))]

    chunkFilename = gestItem + '_' + str(idx) + '.csv'
    while chunkFilename in filesInFolder:
        eeg = eegData()
        eeg.loadChunkFromTraining(subdir=oldsubdir, filename=chunkFilename)
        eeg.cutChunk(newChunkSize=320)
        eeg.saveChunkToCSV(subdir=newsubdir, gesturename=gestItem)
        idx += 1
        chunkFilename = gestItem + '_' + str(idx) + '.csv'
