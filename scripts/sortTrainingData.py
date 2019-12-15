"""
sortTrainingData
This is meant for u to look through each of the really long CSV files and cut the time series EEG data into chunks that contain the desired gesture
"""
import os
from MusEEG import TrainingDataMacro

# #sort through the data and cut chunks whenever it reaches the threshold
def evalAndPrep(obj, chunksubdir=os.path.join('trainbatch2', 'bigChunks')):
    obj.plotRawEEG(obj.matrix, 400)
    obj.createChunks()
    obj.evalChunk()
    obj.saveChunksToCSV(subdir=chunksubdir)

#this is where the your training data is stored
subdir = 'trainbatch2'
gestures = ['smile', 'bitelowerlip', 'hardblink', 'lookleft', 'lookright', 'neutral', 'scrunch', 'tongue', 'eyebrows']

#create TrainingDataMacro objects for each of the gestures
gestureObjects = [TrainingDataMacro() for gestureItem in gestures]

# create importCSV from gesturedata, evaluate and create chunks from the csvs
for idx, gestureobj in enumerate(gestureObjects):
    gestureobj.importCSV(subdir=subdir, filename=gestures[idx]+'.csv',tag=gestures[idx])
    evalAndPrep(gestureobj)
