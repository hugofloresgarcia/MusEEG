"""
sortTrainingData
This is meant for u to look through each of the really long CSV files and cut the time series EEG data into chunks that contain the desired gesture
"""

import sys
sys.path.append("/Users/hugoffg/Documents/MusEEG/MusEEG")

from MusEEG.eegData import TrainingDataMacro

trainingAddress = "/Users/hugoffg/documents/MusEEG/data/10_15_training_samples/"
smile = TrainingDataMacro()
biteLowerLip = TrainingDataMacro()
hardBlink = TrainingDataMacro()
lookLeft = TrainingDataMacro()
lookRight = TrainingDataMacro()
neutral = TrainingDataMacro()
scrunch = TrainingDataMacro()
tongue = TrainingDataMacro()
eyebrows = TrainingDataMacro()

# create importCSV from gesturedata
smile.importCSV(trainingAddress, "smile.csv", "smile")
biteLowerLip.importCSV(trainingAddress, "bitelowerlip.csv", 'bitelowerlip')
hardBlink.importCSV(trainingAddress, "hardblink.csv", 'hardblink')
lookLeft.importCSV(trainingAddress, "lookLeft.csv", 'lookleft')
lookRight.importCSV(trainingAddress, "lookRight.csv", 'lookright')
neutral.importCSV(trainingAddress, "neutral.csv", 'neutral')
scrunch.importCSV(trainingAddress, "scrunch.csv", 'scrunch')
tongue.importCSV(trainingAddress, "tongue.csv", 'tongue')
eyebrows.importCSV(trainingAddress, "eyebrows.csv", 'eyebrows')


# #sort through the data and cut chunks whenever it reaches the threshold
# smile.plotRawChannel(smile.F7, 60, 240)


def evalAndPrep(obj):
    obj.plotRawEEG(obj.matrix, 400)
    obj.createChunks()
    obj.evalChunk()
    obj.saveChunksToCSV(obj.curatedChunk)


evalAndPrep(eyebrows)