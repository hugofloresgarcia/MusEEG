"""
sortTrainingData
This is meant for u to look through each of the really long CSV files and cut the time series EEG data into chunks that contain the desired gesture
"""
import os
import MusEEG
from MusEEG import TrainingDataMacro

#this is where the your training data is stored
subdir = '10_15_training_samples'

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
smile.importCSV(subdir, "smile.csv", "smile")
biteLowerLip.importCSV(subdir, "bitelowerlip.csv", 'bitelowerlip')
hardBlink.importCSV(subdir, "hardblink.csv", 'hardblink')
lookLeft.importCSV(subdir, "lookLeft.csv", 'lookleft')
lookRight.importCSV(subdir, "lookRight.csv", 'lookright')
neutral.importCSV(subdir, "neutral.csv", 'neutral')
scrunch.importCSV(subdir, "scrunch.csv", 'scrunch')
tongue.importCSV(subdir, "tongue.csv", 'tongue')
eyebrows.importCSV(subdir, "eyebrows.csv", 'eyebrows')


# #sort through the data and cut chunks whenever it reaches the threshold
def evalAndPrep(obj):
    obj.plotRawEEG(obj.matrix, 400)
    obj.createChunks()
    obj.evalChunk()
    obj.saveChunksToCSV(subdir='smallChunks')


evalAndPrep(neutral)