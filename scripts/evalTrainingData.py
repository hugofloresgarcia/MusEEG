"""
evalTrainingData
This is meant for u to look through each of the really long CSV files and cut the time series EEG data into chunks that
contain the desired gesture
ONLY WORKS ON EMOTIV
"""
import os
from MusEEG import TrainingDataMacro

# #sort through the data and cut chunks whenever it reaches the threshold
def evalAndPrep(obj, chunksubdir=os.path.join('trainbatch2_improved_320samples', 'bigChunks')):
    obj.plotRawCSV()
    obj.plotRawEEG(chunk=obj.matrix, offset=400)
    obj.newChunkEvalMethod(chunkSubdir=chunksubdir)
    # obj.saveChunksToCSV(subdir=chunksubdir, append=True)

#this is where the your training data is stored
subdir = 'trainbatch2'
gestures = ['scrunch']
# gestures = ['smile', 'bitelowerlip', 'hardblink', 'lookleft', 'lookright', 'neutral', 'scrunch', 'tongue', 'eyebrows']

#create TrainingDataMacro objects for each of the gestures
gestureObjects = [TrainingDataMacro() for gestureItem in gestures]

# create importCSV from gesturedata, evaluate and create chunks from the csvs
for idx, gestureobj in enumerate(gestureObjects):
    gestureobj.importCSV(subdir=subdir, filename=gestures[idx]+'.csv',tag=gestures[idx])
    evalAndPrep(gestureobj)
