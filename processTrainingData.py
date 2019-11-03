# script meant to extract features from curated training data and put features into an input vector for ANN as well as create
# a target vector for labels

import os
import sys

import MusEEG.MusEEG  as MusEEG
from MusEEG.MusEEG import eegData
import pandas as pandas
import numpy as np


def createTargetVector(objarray, *argv):
    labels = []
    targets = [0 for row in range(len(objarray[0][:]) * len(objarray))]
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
smile = [eegData() for i in range(0, 60)]
biteLowerLip = [eegData() for i in range(0, 60)]
eyebrows = [eegData() for i in range(0, 60)]
hardBlink = [eegData() for i in range(0, 60)]
lookLeft = [eegData() for i in range(0, 60)]
lookRight = [eegData() for i in range(0, 60)]
neutral = [eegData() for i in range(0, 60)]
scrunch = [eegData() for i in range(0, 60)]
tongue = [eegData() for i in range(0, 60)]

# load chunks
for i in range(0, 60):
    smile[i].loadChunkFromTraining('smile_' + str(i) + '.csv')
    biteLowerLip[i].loadChunkFromTraining('bitelowerlip_' + str(i) + '.csv')
    eyebrows[i].loadChunkFromTraining('eyebrows_' + str(i) + '.csv')
    lookLeft[i].loadChunkFromTraining('lookleft_' + str(i) + '.csv')
    lookRight[i].loadChunkFromTraining('lookright_' + str(i) + '.csv')
    neutral[i].loadChunkFromTraining('neutral_' + str(i) + '.csv')
    scrunch[i].loadChunkFromTraining('scrunch_' + str(i) + '.csv')
    tongue[i].loadChunkFromTraining('tongue_' + str(i) + '.csv')
    hardBlink[i].loadChunkFromTraining('hardblink_' + str(i) + '.csv')

# wavelet decomp for all samples
for i in range(0, 60):
    smile[i].wavelet()
    biteLowerLip[i].wavelet()
    eyebrows[i].wavelet()
    hardBlink[i].wavelet()
    lookLeft[i].wavelet()
    lookRight[i].wavelet()
    neutral[i].wavelet()
    scrunch[i].wavelet()
    tongue[i].wavelet()

gestures = [smile, biteLowerLip, eyebrows, hardBlink, lookLeft, lookRight, neutral, scrunch, tongue]
targets = createTargetVector(gestures, 'smile', 'bitelowerlip', 'eyebrows', 'hardblink', 'lookleft', 'lookright',
                             'neutral', 'scrunch', 'tongue')

smile[50].plotWavelets(1)

inputs = np.ndarray([540, 350])
inputindex = 0
for i in range(0, len(gestures)):
    for j in range(0, len(gestures[0])):
        gestures[i][j].extractStatsFromWavelets()
        gestures[i][j].flattenIntoVector()
        inputs[inputindex][:] = gestures[i][j].inputVector
        inputindex = inputindex + 1

print(targets)

inputs = pandas.DataFrame(inputs)
targets = pandas.DataFrame(targets)

inputs.to_csv(os.path.join(MusEEG.parentDir, 'data', 'training', 'inputs.csv'))
targets.to_csv(os.path.join(MusEEG.parentDir, 'data', 'training', 'targets.csv'))