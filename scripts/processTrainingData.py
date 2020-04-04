# script meant to extract features from curated training data and put features into an input vector for ANN as well as create
# a target vector for labels

import os

import MusEEG
from MusEEG import eegData
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

numofSamples = 140

# create object lists, for easier handling
smile = [eegData() for i in range(0, numofSamples)]
eyebrows = [eegData() for i in range(0, numofSamples)]
lookLeft = [eegData() for i in range(0, numofSamples)]
lookRight = [eegData() for i in range(0, numofSamples)]
neutral = [eegData() for i in range(0, numofSamples)]
scrunch = [eegData() for i in range(0, numofSamples)]

# load chunks for each of the objects, 60 from trainbatch1 and 60 from trainbatch2
for i in range(0, 70):
    neutral[i].loadChunkFromTraining(subdir=os.path.join('trainbatch2_improved_320samples', 'bigChunks'),
                                     filename='neutral_' + str(i) + '.csv', labelcols=False)
for i in range(70, numofSamples):
    neutral[i].loadChunkFromTraining(subdir=os.path.join('trainbatch1_320samples', 'bigChunks'),
                                         filename='neutral_' + str(i-70) + '.csv', labelcols=False)
for i in range(0, 70):
    smile[i].loadChunkFromTraining(subdir=os.path.join('trainbatch2_improved_320samples', 'bigChunks'),
                                   filename='smile_' + str(i) + '.csv', labelcols=False)
    lookLeft[i].loadChunkFromTraining(subdir=os.path.join('trainbatch2_improved_320samples', 'bigChunks'),
                                      filename='lookleft_' + str(i) + '.csv', labelcols=False)
    lookRight[i].loadChunkFromTraining(subdir=os.path.join('trainbatch2_improved_320samples', 'bigChunks'),
                                       filename='lookright_' + str(i) + '.csv', labelcols=False)
    scrunch[i].loadChunkFromTraining(subdir=os.path.join('trainbatch2_improved_320samples', 'bigChunks'),
                                     filename='scrunch_' + str(i) + '.csv', labelcols=False)
    # tongue[i].loadChunkFromTraining(subdir=os.path.join('trainbatch2_improved_320samples', 'bigChunks'),
    #                                 filename='tongue_' + str(i) + '.csv', labelcols=False)
    eyebrows[i].loadChunkFromTraining(subdir=os.path.join('trainbatch2_improved_320samples', 'bigChunks'),
                                       filename='hardblink_' + str(i) + '.csv', labelcols=False)
for i in range(70, numofSamples):
    smile[i].loadChunkFromTraining(subdir=os.path.join('trainbatch1_320samples', 'bigChunks'),
                                   filename='smile_' + str(i-70) + '.csv', labelcols=False)
    lookLeft[i].loadChunkFromTraining(subdir=os.path.join('trainbatch1_320samples', 'bigChunks'),
                                      filename='lookleft_' + str(i-70) + '.csv', labelcols=False)
    lookRight[i].loadChunkFromTraining(subdir=os.path.join('trainbatch1_320samples', 'bigChunks'),
                                       filename='lookright_' + str(i-70) + '.csv', labelcols=False)
    scrunch[i].loadChunkFromTraining(subdir=os.path.join('trainbatch1_320samples', 'bigChunks'),
                                     filename='scrunch_' + str(i-70) + '.csv', labelcols=False)
    eyebrows[i].loadChunkFromTraining(subdir=os.path.join('trainbatch1_320samples', 'bigChunks'),
                                       filename='eyebrows_' + str(i-70) + '.csv', labelcols=False)

gestures = [smile, eyebrows, lookLeft, lookRight, neutral, scrunch]
targets = createTargetVector(gestures, 'smile', 'eyebrows', 'lookleft', 'lookright',
                             'neutral', 'scrunch')

inputs = np.ndarray([len(gestures)*numofSamples, 350])
inputindex = 0
for i in range(0, len(gestures)):
    for j in range(0, len(gestures[0])):
        print(j)
        gestures[i][j].wavelet()
        gestures[i][j].extractStatsFromWavelets()
        gestures[i][j].flattenIntoVector()
        inputs[inputindex][:] = gestures[i][j].inputVector
        inputindex = inputindex + 1

print(targets)

inputs = pandas.DataFrame(inputs)
targets = pandas.DataFrame(targets)

inputs.to_csv(os.path.join(MusEEG.parentDir, 'data', 'training', 'batch1_batch2_320samples', 'bigChunks', 'inputs.csv'))
targets.to_csv(os.path.join(MusEEG.parentDir, 'data', 'training', 'batch1_batch2_320samples', 'bigChunks', 'targets.csv'))