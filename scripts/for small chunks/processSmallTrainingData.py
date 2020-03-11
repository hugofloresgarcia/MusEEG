# script meant to extract features from curated training data and put features into an input vector for ANN as well as create
# a target vector for labels

import os
import sys

import MusEEG
from MusEEG import eegData
import pandas as pandas
import numpy as np

sizeYes = 160
sizeNo = 160

def createTargetVector(objarray, *argv):
    labels = []
    targets = [0 for row in range(0, sizeYes+sizeNo)]
    index = 0
    for i in range(0, len(objarray)):
        print(objarray[i][0].filename)
        for j in range(0, len(objarray[i])):
            labels.append(objarray[i][j].filename)
            for arg in argv:
                if arg in objarray[i][j].filename:
                    targets[index] = i
                    index = index + 1
    return targets


# create object lists.  They are lists, not arrays
nogesture = [eegData() for i in range(0, sizeNo)]
gesture = [eegData() for i in range(0, sizeYes)]



splitsies = int(len(gesture)/5)

# load chunks
for i in range(0, len(nogesture)):
    nogesture[i].loadChunkFromTraining(os.path.join('trainbatch1', 'smallChunks', 'hugo_facialgestures'), 'neutral_' + str(i) + '.csv')

for j in range(0, splitsies):
    for i in range(0, int(160 / 5)):
         gesture[j].loadChunkFromTraining(os.path.join('trainbatch1','bigChunks'), 'smile_' + str(i) + '.csv')

for j in range(2*splitsies, 3*splitsies):
    for i in range(0, int(160 / 5)):
         gesture[j].loadChunkFromTraining(os.path.join('trainbatch1','bigChunks'), 'lookleft_' + str(i) + '.csv')

for j in range(3 * splitsies, 4 * splitsies):
    for i in range(0, int(160 / 5)):
         gesture[j].loadChunkFromTraining(os.path.join('trainbatch1','bigChunks'), 'lookright_' + str(i) + '.csv')

for j in range(4 * splitsies, 5 * splitsies):
    for i in range(0, int(160 / 5)):
         gesture[j].loadChunkFromTraining(os.path.join('trainbatch1','bigChunks'), 'scrunch_' + str(i) + '.csv')

for j in range( splitsies, 2 * splitsies):
    for i in range(0, int(160 / 5)):
         gesture[j].loadChunkFromTraining(os.path.join('trainbatch1','bigChunks'), 'hardblink_' + str(i) + '.csv')




gestures = [nogesture, gesture]

for i in range(0, len(gestures)):
    for j in range(0, len(gestures[i])):
        if i == 1:
            gestures[i][j].filename = 'yesgesture'
        elif i == 0:
            gestures[i][j].filename = 'nogesture'

targets = createTargetVector(gestures, 'nogesture', 'yesgesture')

##for smallchunks only. smallchunks are 1/8 of bigChunks (comment if you're working with big chunks)
for i in range(0, len(gestures)):
    gesture[i].cutChunk(eegData.smallchunkSize)

inputs = np.ndarray([sizeYes + sizeNo, 350])
inputindex = 0
for i in range(0, len(gestures)):
    for j in range(0, len(gestures[i])):
        gestures[i][j].wavelet()
        gestures[i][j].extractStatsFromWavelets()
        gestures[i][j].flattenIntoVector()
        inputs[inputindex][:] = gestures[i][j].inputVector
        inputindex = inputindex + 1

print(targets)

inputs = pandas.DataFrame(inputs)
targets = pandas.DataFrame(targets)

inputs.to_csv(os.path.join(MusEEG.parentDir, 'data', 'training', 'smallChunks_v3', 'inputs.csv'))
targets.to_csv(os.path.join(MusEEG.parentDir, 'data', 'training', 'smallChunks_v3', 'targets.csv'))