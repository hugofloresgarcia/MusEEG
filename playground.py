"""
I'm just writing quick sketches here
"""

from MusEEG import eegData
import matplotlib.pyplot as plt

figure = plt.figure(figsize=(20,10))


eeg = eegData()
eeg.loadChunkFromTraining(subdir='trainbatch1_320samples/bigChunks', filename='smile_25.csv', labelcols=False)
eeg.wavelet()
eeg.plotRawEEG(figure=figure)
plt.pause(5)
figure.clear()
eeg.plotWavelets(channel=1, figure=figure)
plt.pause(5)
figure.clear()
eeg.cutChunk(newChunkSize=64)
eeg.plotRawEEG(figure=figure)
plt.pause(5)
figure.clear()