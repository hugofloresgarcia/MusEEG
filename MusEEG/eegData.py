import os
import sys
import time

import pandas
import numpy as np
from pywt import wavedec

import pickle
from scipy.stats import kurtosis, skew

from tensorflow import keras
from keras import regularizers

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
plt.ion()
from matplotlib.figure import Figure

from MusEEG import parentDir

class eegData:
    threshold = 20
    sampleRate = 256
    chunkSize = int(256*1.5)
    smallchunkSize = int(chunkSize/6)
    backTrack = 35
    nchannels = 14
    emotivChannels = ["EEG.AF3", "EEG.F7", "EEG.F3", "EEG.FC5", "EEG.T7", "EEG.P7", "EEG.O1",
                           "EEG.O2", "EEG.P8", "EEG.T8", "EEG.FC6", "EEG.F4", "EEG.F8", "EEG.AF4"]

    def __init__(self):
        self.thresholdChannel = 'F7'
        self.trainingChunks = []

    def wavelet(self):
        """"
        wavelet transform (4-level) for a single eeg chunk
        input argument is a chunk
        creates a self.wavelets list which contains np arrays with the coefficients
        """
        self.nchannels = len(self.chunk[0, :])
        self.cA4 = []
        self.cD4 = []
        self.cD3 = []
        self.cD2 = []
        self.cD1 = []
        for i in range(0, self.nchannels):
            cA4, cD4, cD3, cD2, cD1 = wavedec(self.chunk[:, i], 'db2', level=4)
            self.cA4.append(cA4)
            self.cD4.append(cD4)
            self.cD3.append(cD3)
            self.cD2.append(cD2)
            self.cD1.append(cD1)

        self.wavelets = [np.asarray(self.cA4), np.asarray(self.cD4), np.asarray(self.cD3), np.asarray(self.cD2), np.asarray(self.cD1)]

    def extractStatsFromWavelets(self):
        """
        calculates mean, standard deviation, variance, kurtosis, and skewness from self.wavelets object.
        creates self.mean, self.std, self.kurtosis, self.skew which are numpy arrays with 14 rows (eeg channels)
        and 5 columns (per coefficients)
        """
        self.mean = np.ndarray((self.nchannels, 5))
        self.var = np.ndarray((self.nchannels, 5))
        self.std = np.ndarray((self.nchannels, 5))
        self.kurtosis = np.ndarray((self.nchannels, 5))
        self.skew = np.ndarray((self.nchannels, 5))
        ## ojo, dimensions are transposed here
        for i in range(0, self.nchannels):
            self.mean[i, :] = [np.mean(self.cA4[i]), np.mean(self.cD4[i]), np.mean(self.cD3[i]), np.mean(self.cD2[i]), np.mean(self.cD1[i])]
            self.var[i, :] = [np.var(self.cA4[i]), np.var(self.cD4[i]), np.var(self.cD3[i]), np.var(self.cD2[i]), np.var(self.cD1[i])]
            self.std[i, :] = [np.std(self.cA4[i]), np.std(self.cD4[i]), np.std(self.cD3[i]), np.std(self.cD2[i]), np.std(self.cD1[i])]
            self.kurtosis[i, :] = [kurtosis(self.cA4[i]), kurtosis(self.cD4[i]), kurtosis(self.cD3[i]), kurtosis(self.cD2[i]), kurtosis(self.cD1[i])]
            self.skew[i, :] = [skew(self.cA4[i]), skew(self.cD4[i]), skew(self.cD3[i]), skew(self.cD2[i]), skew(self.cD1[i])]

    def flattenIntoVector(self):
        """
        creates an input array for ANN, structured as:
            [mean, var, std, kurtosis, skew]
            each of these is 14 channels * 5 wavelet coefficients long = 70 floats
            vector is flattened, and for 5 stat features * 70 numbers = 350 numbers
        """
        mean = self.mean.flatten()
        var = self.var.flatten()
        std = self.std.flatten()
        kurtosis = self.kurtosis.flatten()
        skew = self.skew.flatten()

        self.inputVector = np.array([mean, var, std, kurtosis, skew])
        self.inputVector = self.inputVector.flatten()
        return self.inputVector

    def plotRawEEG(self, offset=200, title='eeg'):
        """
        :param title: title of the figure
        :param offset: DC offset between eeg channels
        :return: plot with all 14 eeg channels
        """
        # define time axis
        tAxis = np.arange(0, len(self.chunk))  # create time axis w same length as the data matrix
        tAxis = tAxis / self.sampleRate  # adjust time axis to 256 sample rate

        # use eeg matrix as y axis
        yAxis = self.chunk + offset * 13

        # add offset to display all channels
        for i in range(0, len(self.chunk[0, :])):
            yAxis[:, i] -= offset * i

        # plot figure
        plt.figure()
        plt.plot(tAxis, yAxis)
        plt.title(title)
        plt.ylim(-300, offset * 20)
        plt.legend(["EEG.AF3", "EEG.F7", "EEG.F3", "EEG.FC5", "EEG.T7", "EEG.P7", "EEG.O1",
                    "EEG.O2", "EEG.P8", "EEG.T8", "EEG.FC6", "EEG.F4", "EEG.F8", "EEG.AF4"],
                   loc='upper right')
        plt.xlabel('time')
        plt.show(block=True)
        # plt.pause(0.01)

    def plotRawEEGui(self, offset=200, plotTitle='eeg'):
        """
        this version spits out a figure window for use in the UI
        :param title: title of the figure
        :param offset: DC offset between eeg channels
        :return: plot with all 14 eeg channels
        """
        # define time axis
        tAxis = np.arange(0, len(self.chunk))  # create time axis w same length as the data matrix
        tAxis = tAxis / self.sampleRate  # adjust time axis to 256 sample rate

        # use eeg matrix as y axis
        yAxis = self.chunk + offset * 13

        # add offset to display all channels
        for i in range(0, len(self.chunk[0, :])):
            yAxis[:, i] -= offset * i

        # plot figure
        figure = Figure()
        ax = figure.add_subplot(111)
        ax.set_title(plotTitle)
        ax.set_ylim(-300, offset * 20)
        ax.legend(["EEG.AF3", "EEG.F7", "EEG.F3", "EEG.FC5", "EEG.T7", "EEG.P7", "EEG.O1",
                   "EEG.O2", "EEG.P8", "EEG.T8", "EEG.FC6", "EEG.F4", "EEG.F8", "EEG.AF4"])
        ax.set_xlabel('time')
        ax.plot(tAxis, yAxis)

        return figure

        # plt.pause(0.01)


    def plotWavelets(self, channel):
        """
        plots wavelet decomposition of a single channel self.chunk
        :param channel: (between 0 and 13) eeg channel to be plotted
        :return:
        """
        fig, axes = plt.subplots(3, 2)
        fig.suptitle('Wavelet Plot')
        axes[0, 0].plot(self.chunk[:, channel])
        axes[0, 0].set_title('Raw EEG')

        axes[0, 1].plot(self.cA4[:][channel])
        axes[0, 1].set_title('Approximation Coefficients')

        axes[1, 0].plot(self.cD4[:][channel])
        axes[1, 0].set_title('Level 4 Detail Coefficients')

        axes[1, 1].plot(self.cD3[:][channel])
        axes[1, 1].set_title('Level 3 Detail Coefficients')

        axes[2, 0].plot(self.cD2[:][channel])
        axes[2, 0].set_title('Level 2 Detail Coefficients')

        axes[2, 1].plot(self.cD1[:][channel])
        axes[2, 1].set_title('Level 1 Detail Coefficients')

        fig.show()
        plt.show(block=True)

    def loadChunkFromTraining(self, subdir, filename):
        """
        :param subdir: subdirectory where chunk is located from MusEEG/data/savedChunks
        :param filename: filename
        :return:
        """
        self.filename = filename
        self.chunk = pandas.read_csv(os.path.join(parentDir, 'data', 'savedChunks', subdir, filename), usecols=self.emotivChannels)
        self.chunk = self.chunk.values
        self.AF3 = self.chunk[:, 0]
        self.F7 = self.chunk[:, 1]
        self.F3 = self.chunk[:, 2]
        self.FC5 = self.chunk[:, 3]
        self.T7 = self.chunk[:, 4]
        self.P7 = self.chunk[:, 5]
        self.O1 = self.chunk[:, 6]
        self.O2 = self.chunk[:, 7]
        self.P8 = self.chunk[:, 8]
        self.T8 = self.chunk[:, 9]
        self.FC6 = self.chunk[:, 10]
        self.F4 = self.chunk[:, 11]
        self.F8 = self.chunk[:, 12]
        self.AF4 = self.chunk[:, 13]
        return self.chunk

    def cutChunk(self):
        """
        for smallBrain: cut chunk to smallchunkSize
        """
        self.chunk = self.chunk[0:(self.smallchunkSize-1), :]

    def process(self):
        self.wavelet()
        self.extractStatsFromWavelets()
        inputVector = self.flattenIntoVector()
        return inputVector



#todo: this has to work with relative paths
class TrainingDataMacro(eegData):
    """
    child eegData class meant for user to evaluate a long .csv file with multiple training samples in it
    reads rawdata and creates a long self.rawData object with ALL the data

    self.matrix contains only numbers w DC offset removed

    """
    def __init__(self):
        super().__init__()
        self.curatedChunk = []
        self.label = []

    def importCSV(self, subdir, filename, tag):
        """
        :param subdir: subdirectory under MusEEG/data/longRawTrainingSamples where the .csv files are located
        :param filename: filename of the .csv file
        :param tag: the label you would like to associate the file with. typically the same as filename.
        :return:
        """
        self.rawData = pandas.read_csv(os.path.join(parentDir, 'data', 'longRawTrainingSamples', subdir, filename), skiprows=1, dtype=float, header=0,
                                       usecols=self.emotivChannels)
        self.markers = pandas.read_csv(os.path.join(parentDir, 'data','longRawTrainingSamples', subdir, filename), skiprows=1, usecols=['EEG.MarkerHardware'])
        self.address = subdir
        self.filename = filename
        self.tag = tag
        self.matrix = np.array(self.rawData.values - 4100)
        self.AF3 = self.matrix[:, 0]
        self.F7 = self.matrix[:, 1]
        self.F3 = self.matrix[:, 2]
        self.FC5 = self.matrix[:, 3]
        self.T7 = self.matrix[:, 4]
        self.P7 = self.matrix[:, 5]
        self.O1 = self.matrix[:, 6]
        self.O2 = self.matrix[:, 7]
        self.P8 = self.matrix[:, 8]
        self.T8 = self.matrix[:, 9]
        self.FC6 = self.matrix[:, 10]
        self.F4 = self.matrix[:, 11]
        self.F8 = self.matrix[:, 12]
        self.AF4 = self.matrix[:, 13]

    def plotRawChannel(self, channel, start, stop):
        """
        plot raw channel for trainingdatamacro object
        :param channel: channel to be plotted
        :param start: (in seconds) where in the recording to start plotting
        :param stop: (in seconds) where in the recording to stop plotting
        :return:
        """
        channel = channel[start*self.sampleRate:stop*self.sampleRate]

        # define time axis
        tAxis = np.arange(0, len(channel))  # create time axis w same length as the data matrix
        tAxis = tAxis / self.sampleRate  # adjust time axis to 256 sample rate

        # use eeg matrix as y axis
        yAxis = channel

        # plot figure
        plt.figure()
        plt.plot(tAxis, yAxis)
        plt.ylim(-1000, 1000)
        plt.show(block=True)

    def createChunks(self):
        """
        creates chunks that meet the threshold and backtrack criteria. Basically, if a certain channel's voltage passes a
        certain threshold, a chunk of samples will be saved to self.trainingChunks
        :return:
        """
        self.nChunks = 0
        x, y = self.matrix.shape
        i = 0
        while i < len(self.F7):
            if ((abs(self.F7[i]) >= self.threshold) or (abs(self.AF3[i]) >= self.threshold) or (abs(self.T7[i]) >= self.threshold)) and (i > eegData.backTrack) and (i < (len(self.F7) - eegData.chunkSize)):
                chunkStart = i - eegData.backTrack
                chunkEnd = chunkStart + eegData.chunkSize
                # print(self.matrix[chunkStart:chunkEnd,:])
                # print(self.emotivChannels)
                self.trainingChunks.append(pandas.DataFrame(self.matrix[chunkStart:chunkEnd, :], columns=self.emotivChannels))
                self.nChunks = self.nChunks + 1
                i = chunkEnd + 1
            i += 1

    def plotChunk(self, num):
        """
        plots a single chunk from self.trainingChunks (not curated). to be used in evalChunk method
        """
        fig = plt.figure(num)
        plt.plot(self.trainingChunks[num].values)
        plt.xlabel('sample number ' + str(num) )
        plt.ylim(-1500, 1500)
        plt.pause(0.001)

        return fig

    def evalChunk(self):
        """
                evaluates chunks
                goes through self.matrix and picks out chunks for you to evaluate
                if you think the chunk is good, it will save it to self.curatedChunk list that contains all good chunks

                :return:
        """
        self.curatedChunkCount = 0
        for i in range(0, len(self.trainingChunks)):
            fig = self.plotChunk(i)
            prompt = input('would you like to use sample number ' + str(i) + '? ')
            if prompt == 'y':
                self.curatedChunk.append(self.trainingChunks[i])
                self.curatedChunkCount += 1

            plt.close(fig)

    def saveChunksToCSV(self, subdir='smallChunks'):
        """
        saves curated chunks to csv
        :param obj:
        :return:
        """
        for i in range(len(self.curatedChunk)):
            self.curatedChunk[i].to_csv(os.path.join(parentDir, 'data', 'savedChunks', subdir, self.tag + '_' + str(i) + '.csv'))

    def saveTrainingObject(self, filename, address=os.path.join(parentDir, 'data', 'savedTrainingObjects')):
        filehandle = open(os.path.join(address, filename), 'w')
        pickle.dump(self, filehandle)

    @staticmethod
    def loadFromTrainingObject(filename, address=os.path.join(parentDir, 'data', 'savedTrainingObjects')):
        file = open(os.path.join(address, filename), 'r')
        object = pickle.load(file)
        return object

    def plotRawEEG(self, matrix, offset=200):
        """
        note: the only difference between this and the parent method is that this one displays the title of the thing
        being plotted
        :param matrix:
        :param offset: DC offset between eeg channels
        :return: plot with all 14
        """
        # define time axis
        tAxis = np.arange(0, len(matrix))  # create time axis w same length as the data matrix
        tAxis = tAxis / self.sampleRate  # adjust time axis to 256 sample rate

        # use eeg matrix as y axis
        yAxis = matrix + offset * 13

        # add offset to display all channels
        for i in range(0, len(matrix[0, :])):
            yAxis[:, i] -= offset * i

        # plot figure
        plt.figure()
        plt.plot(tAxis, yAxis)
        plt.title(self.tag)
        plt.ylim(-300, offset * 20)
        plt.legend(["EEG.AF3", "EEG.F7", "EEG.F3", "EEG.FC5", "EEG.T7", "EEG.P7", "EEG.O1",
                    "EEG.O2", "EEG.P8", "EEG.T8", "EEG.FC6", "EEG.F4", "EEG.F8", "EEG.AF4"],
                   loc='upper right')
        plt.xlabel('time')
        plt.show(block=True)
        # plt.pause(0.01)

# todo: rebuild tensor flow with AVX2 FMA for faster performance