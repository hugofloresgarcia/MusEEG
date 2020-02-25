"""
I'm just writing quick sketches here
"""
import MusEEG
from MusEEG import eegData, classifier, cerebro
import os
import pandas as pd
import matplotlib.pyplot as plt
import time

classifier = classifier()
classifier.loadmodel(os.path.join(MusEEG.parentDir, 'data', 'savedModels', 'bigBrain_b1b2_norm'), loadScaler=True)
howManyDoWeWannaCheck = 70

# figure1 = plt.figure()

expressionImChecking = 'smile'

eeg1 = [eegData() for i in range(0, howManyDoWeWannaCheck)]
stat1 = []
idx = 0
for eeg in eeg1:
	eeg.loadChunkFromTraining(subdir='trainbatch1_320samples/bigChunks', filename=expressionImChecking+'_' + str(idx) + '.csv', labelcols= False)
	eeg.wavelet()
	eeg.extractStatsFromWavelets()
	# eeg.plotWavelets(channel=1, figure=figure1)
	nnInput = eeg.flattenIntoVector()
	stat1.append(classifier.normalizeInput(nnInput.reshape(1, 350)))
	nnOutput = classifier.classify(nnInput.reshape(1, 350))
	print(cerebro.gestures[nnOutput])
	idx += 1

print('SPCSAKMNAPOSC')

eeg2 = [eegData() for i in range(0, howManyDoWeWannaCheck)]
stat2 = []
idx = 0
for eeg in eeg2:
	eeg.loadChunkFromTraining(subdir='trainbatch2_improved_320samples/bigChunks', filename=expressionImChecking+'_' + str(idx) + '.csv', labelcols=False)
	eeg.wavelet()
	eeg.extractStatsFromWavelets()
	# eeg.plotWavelets(channel=1, figure=figure2)
	nnInput = eeg.flattenIntoVector()
	stat2.append(classifier.normalizeInput(nnInput.reshape(1, 350)))
	nnOutput = classifier.classify(nnInput.reshape(1, 350))
	print(cerebro.gestures[nnOutput])
	idx += 1

for array in stat1:
	# plt.figure(1)
	plt.plot(array.reshape(350,1))

for array in stat2:
	plt.figure(2)
	plt.plot(array.reshape(350,1))

# time.sleep(7)
plt.show(block=True)




"""
plot figures for publications
"""

from MusEEG import eegData
import matplotlib.pyplot as plt
# figure = plt.figure(figsize=(20,10))
#
#
# eeg = eegData()
# eeg.loadChunkFromTraining(subdir='trainbatch1_320samples/bigChunks', filename='smile_25.csv', labelcols=False)
# eeg.wavelet()
# eeg.plotRawEEG(figure=figure)
# plt.pause(5)
# figure.clear()
# eeg.plotWavelets(channel=1, figure=figure)
# plt.pause(5)
# figure.clear()
# eeg.cutChunk(newChunkSize=64)
# eeg.plotRawEEG(figure=figure)
# plt.pause(5)
# figure.clear()