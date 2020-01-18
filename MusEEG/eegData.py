import os
import pandas
import numpy as np
from pywt import wavedec

import pickle
from scipy.stats import kurtosis, skew
from scipy.signal import welch
from scipy.integrate import simps


import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

plt.ion()
from matplotlib.figure import Figure
from matplotlib.pyplot import figure

from MusEEG import parentDir

from scipy import signal


class eegData:
    threshold = 350
    sampleRate = 256
    ####note: these used to be 384 samples and 64 samples.
    chunkSize = int(256 * 1.25)
    smallchunkSize = int(chunkSize / 4)
    backTrack = 50  ##backtrack used to be 35
    nchannels = 14
    emotivChannels = ["EEG.AF3", "EEG.F7", "EEG.F3", "EEG.FC5", "EEG.T7", "EEG.P7", "EEG.O1",
                      "EEG.O2", "EEG.P8", "EEG.T8", "EEG.FC6", "EEG.F4", "EEG.F8", "EEG.AF4"]
    eegChannels = [channel[4:] for channel in emotivChannels]
    thresholdChannels = ['F7', 'AF4', 'T7']

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

        self.wavelets = [np.asarray(self.cA4), np.asarray(self.cD4), np.asarray(self.cD3), np.asarray(self.cD2),
                         np.asarray(self.cD1)]

    @classmethod
    def bandPower(cls, buffer, band, window_sec=None):
        band = np.asarray(band)
        low, high = band

        if window_sec is not None:
            nperseg = window_sec*eegData.sampleRate
        else:
            nperseg = (2/low)*eegData.sampleRate

        freqs, psd = welch(buffer, eegData.sampleRate, nperseg=nperseg)

        freqRes = freqs[1] - freqs[0]
        idxBand = np.logical_and(freqs >= low, freqs <= high)

        bp = simps(psd[:, idxBand], dx=freqRes)
        return bp

    @classmethod
    def dbBandPower(cls, buffer, band, window_sec=None):
        bp = cls.bandPower(buffer, band, window_sec)
        bpdb = 10 * np.log10(bp)
        return bpdb

    @classmethod
    def bandPowerHistogram(cls, df, figure):
        figure.canvas.flush_events()
        ax = figure.add_subplot(111)
        ax.clear()
        ax.plot(df)
        ax.set_title('Band Power (dB)')
        ax.set_ylim([0, 80])
        figure.canvas.draw()
        plt.pause(0.001)


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
            self.mean[i, :] = [np.mean(self.cA4[i]), np.mean(self.cD4[i]), np.mean(self.cD3[i]), np.mean(self.cD2[i]),
                               np.mean(self.cD1[i])]
            self.var[i, :] = [np.var(self.cA4[i]), np.var(self.cD4[i]), np.var(self.cD3[i]), np.var(self.cD2[i]),
                              np.var(self.cD1[i])]
            self.std[i, :] = [np.std(self.cA4[i]), np.std(self.cD4[i]), np.std(self.cD3[i]), np.std(self.cD2[i]),
                              np.std(self.cD1[i])]
            self.kurtosis[i, :] = [kurtosis(self.cA4[i]), kurtosis(self.cD4[i]), kurtosis(self.cD3[i]),
                                   kurtosis(self.cD2[i]), kurtosis(self.cD1[i])]
            self.skew[i, :] = [skew(self.cA4[i]), skew(self.cD4[i]), skew(self.cD3[i]), skew(self.cD2[i]),
                               skew(self.cD1[i])]

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

    def plotRawEEG(self, figure=None, chunk=None, offset=200, plotTitle='eeg'):
        """
        this version spits out a figure window for use in the UI
        :param title: title of the figure
        :param offset: DC offset between eeg channels
        :return: plot with all 14 eeg channels
        """
        if chunk is None:
            chunk = self.chunk
        # define time axis
        tAxis = np.arange(0, len(chunk))  # create time axis w same length as the data matrix
        tAxis = tAxis / self.sampleRate  # adjust time axis to 256 sample rate

        # use eeg matrix as y axis
        yAxis = chunk + offset * 13

        # add offset to display all channels
        for i in range(0, len(chunk[0, :])):
            yAxis[:, i] -= offset * i

        # plot figure
        if figure is None:
            figure = Figure()

        figure.canvas.flush_events()
        ax = figure.add_subplot(111)
        ax.clear()
        ax.set_title(plotTitle)
        ax.set_ylim(-300, offset * 20)
        ax.legend(["EEG.AF3", "EEG.F7", "EEG.F3", "EEG.FC5", "EEG.T7", "EEG.P7", "EEG.O1",
                   "EEG.O2", "EEG.P8", "EEG.T8", "EEG.FC6", "EEG.F4", "EEG.F8", "EEG.AF4"])
        ax.set_xlabel('time')
        ax.plot(tAxis, yAxis)
        figure.canvas.draw()
        plt.pause(0.001)

        return figure

        # plt.pause(0.01)

    def plotWavelets(self, channel, figure=None):
        """
        plots wavelet decomposition of a single channel self.chunk
        :param channel: (between 0 and 13) eeg channel to be plotted
        :return: figure
        """
        if figure is None:
            fig = Figure()
        else:
            fig = figure
        # fig.suptitle('Wavelet Plot')
        ax = [0 for i in range(0, 6)]
        try:
            ax[0] = fig.add_subplot(611)
            ax[0].plot(self.chunk[:, channel])
            ax[0].set_title('Raw EEG', pad=1)

            ax[1] = fig.add_subplot(612)
            ax[1].plot(self.cA4[:][channel])
            ax[1].set_title('Approximation Coefficients', pad=1)

            ax[2] = fig.add_subplot(613)
            ax[2].plot(self.cD4[:][channel])
            ax[2].set_title('Level 4 Detail Coefficients', pad=1)

            ax[3] = fig.add_subplot(614)
            ax[3].plot(self.cD3[:][channel])
            ax[3].set_title('Level 3 Detail Coefficients', pad=1)

            ax[4] = fig.add_subplot(615)
            ax[4].plot(self.cD2[:][channel])
            ax[4].set_title('Level 2 Detail Coefficients', pad=1)

            ax[5] = fig.add_subplot(616)
            ax[5].plot(self.cD1[:][channel])
            ax[5].set_title('Level 1 Detail Coefficients', pad=1)
            fig.tight_layout(pad=0.75)
            fig.canvas.draw()
            plt.pause(0.001)
        except AttributeError:
            pass
        # todo: make this work with the UI
        return fig

    def loadChunkFromTraining(self, subdir, filename, labelcols=True):
        """
        :rtype: objectram subdir: subdirectory where chunk is located from MusEEG/data/savedChunks
        :param filename: filename with .csv at the end
        :param labelcols: do the .csv files have the EEG.CHANNEL headers in them?
        :return:
        """
        self.filename = filename
        if not labelcols:
            self.chunk = pandas.read_csv(os.path.join(parentDir, 'data', 'savedChunks', subdir, filename)).values
            # print(len(self.chunk[0,:]))
            if len(self.chunk[0, :]) == 15:
                self.chunk = self.chunk[:, 1:15]
                # print(self.chunk[:, 13])
            if len(self.chunk[0, :]) == 16:
                self.chunk = self.chunk[:, 2:16]


        else:
            self.chunk = pandas.read_csv(os.path.join(parentDir, 'data', 'savedChunks', subdir, filename),
                                     usecols=self.emotivChannels).values

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

    def cutChunk(self, newChunkSize):
        """
        for smallBrain: cut chunk to a new ChunkSize
        """
        self.chunk = self.chunk[0:(newChunkSize - 1), :]

    def process(self):
        self.wavelet()
        self.extractStatsFromWavelets()
        inputVector = self.flattenIntoVector()
        return inputVector

    @classmethod
    def checkThreshold(cls, packetdict):
        thresholdActive = False
        for channel in cls.thresholdChannels:
            if abs(packetdict[channel]) >= cls.threshold:
                thresholdActive = True
        return thresholdActive

    def saveChunkToCSV(self, subdir, gesturename):
        """
        saves self.chunk to csv
        :param subdir: sudirectory under /data/savedChunks
        :return:
        """
        workingDir = os.path.join(parentDir, 'data', 'savedChunks', subdir)
        idx = 0
        filesInFolder = [file for file in os.listdir(workingDir) if os.path.isfile(os.path.join(workingDir, file))]

        chunkFilename = gesturename + '_' + str(idx) + '.csv'
        while chunkFilename in filesInFolder:
            idx += 1
            chunkFilename = gesturename + '_' + str(idx) + '.csv'

        chunkDataFrame = pandas.DataFrame(self.chunk)
        chunkDataFrame.to_csv(os.path.join(parentDir, 'data', 'savedChunks', subdir, chunkFilename))


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
        self.trainingChunks = []
        self.curatedChunkCount = 0

    def importCSV(self, subdir, filename, tag):
        """
        :param subdir: subdirectory under MusEEG/data/longRawTrainingSamples where the .csv files are located
        :param filename: filename of the .csv file
        :param tag: the label you would like to associate the file with. typically the same as filename.
        :return:
        """
        self.rawData = pandas.read_csv(os.path.join(parentDir, 'data', 'longRawTrainingSamples', subdir, filename),
                                       skiprows=1, dtype=float, header=0,
                                       usecols=self.emotivChannels)
        self.markers = pandas.read_csv(os.path.join(parentDir, 'data', 'longRawTrainingSamples', subdir, filename),
                                       skiprows=1, usecols=['EEG.MarkerHardware'])
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
        channel = channel[start * self.sampleRate:stop * self.sampleRate]

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
            if ((abs(self.F7[i]) >= self.threshold) or (abs(self.AF3[i]) >= self.threshold) or (
                    abs(self.T7[i]) >= self.threshold)) and (i > eegData.backTrack) and (
                    i < (len(self.F7) - eegData.chunkSize)):
                chunkStart = i - eegData.backTrack
                chunkEnd = chunkStart + eegData.chunkSize
                # print(self.matrix[chunkStart:chunkEnd,:])
                # print(self.emotivChannels)
                self.trainingChunks.append(
                    pandas.DataFrame(self.matrix[chunkStart:chunkEnd, :], columns=self.emotivChannels))
                self.nChunks = self.nChunks + 1
                i = chunkEnd + 1
            i += 1

    def plotChunk(self, num):
        """
        plots a single chunk from self.trainingChunks (not curated). to be used in evalChunk method
        """
        fig = plt.figure(num)
        plt.plot(self.trainingChunks[num].values)
        plt.xlabel('sample number ' + str(num))
        plt.ylim(-1500, 1500)
        plt.pause(0.001)

        return fig

    def newChunkEvalMethod(self, chunkSubdir):
        """
                creates chunks that meet the threshold and backtrack criteria. Basically, if a certain channel's voltage passes a
                certain threshold, a chunk of samples will be saved to self.trainingChunks
                :return:
        """
        self.nChunks = 0
        i = 0
        fig = figure()
        i = input('enter starting sample: ')
        i = int(i)
        while i < len(self.F7):
            # see if it passes threshold
            if ((abs(self.F7[i]) >= self.threshold) or (abs(self.AF3[i]) >= self.threshold) or (
                    abs(self.T7[i]) >= self.threshold)) and (i > eegData.backTrack) and (
                    i < (len(self.F7) - eegData.chunkSize)):
                # make sure user evaluates whether threshold was right or not
                approvedByUser = False
                chunkStart = i - eegData.backTrack
                chunkEnd = chunkStart + eegData.chunkSize

                chunkUnderEvaluation = self.matrix[chunkStart:chunkEnd, :]
                while not approvedByUser:
                    shift = 0
                    self.chunk = chunkUnderEvaluation
                    self.plotRawEEG(fig)
                    print('current sample is ' + str(chunkStart))
                    keep = input('keep this? y/n')
                    if keep == 'n':
                        break
                    try:
                        shift = input('enter desired shift (in samples, negative numbers mean shift left) ')
                        shift = int(shift)
                    except (TypeError, ValueError):
                        print('uh thats not an integer, shift set to 0')
                        shift = 0

                    chunkStart = chunkStart + shift
                    chunkEnd = chunkEnd + shift

                    self.chunk = self.matrix[chunkStart:chunkEnd, :]
                    self.plotRawEEG(fig)
                    allgood = input('save this chunk? (y/n)')
                    print('\n')
                    if allgood == 'y':
                        approvedByUser = True
                        self.curatedChunk.append(self.chunk)
                        self.curatedChunkCount += 1
                        self.nChunks += 1
                        self.saveSingleChunkToCSV(chunk=self.chunk, subdir=chunkSubdir)

                i = chunkEnd + 1
            i += 1

    def saveSingleChunkToCSV(self, chunk, subdir):
        workingDir = os.path.join(parentDir, 'data', 'savedChunks', subdir)
        idx = 0
        filesInFolder = [file for file in os.listdir(workingDir) if os.path.isfile(os.path.join(workingDir, file))]

        chunkFilename = self.tag + '_' + str(idx) + '.csv'
        while chunkFilename in filesInFolder:
            idx += 1
            chunkFilename = self.tag + '_' + str(idx) + '.csv'

        chunkDataFrame = pandas.DataFrame(chunk)
        chunkDataFrame.to_csv(os.path.join(parentDir, 'data', 'savedChunks', subdir, chunkFilename))

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

    def saveChunksToCSV(self, subdir='smallChunks', append=True):
        """
        saves curated chunks to csv
        :param subdir: subdirectory where chunks will be stored
        :param append: append new chunks or overwrite old ones
        :return:
        """
        for i in range(len(self.curatedChunk)):
            self.curatedChunk[i].to_csv(
                os.path.join(parentDir, 'data', 'savedChunks', subdir, self.tag + '_' + str(i) + '.csv'))

    def plotRawCSV(self, offset=200):
        """
        plot the whole csv
        :param matrix:
        :param offset: DC offset between eeg channels
        :return: plot with all 14
        """
        # define time axis
        tAxis = np.arange(0, len(self.matrix))  # create time axis w same length as the data matrix
        tAxis = tAxis / self.sampleRate  # adjust time axis to 256 sample rate

        # use eeg self.matrix as y axis
        yAxis = self.matrix + offset * 13

        # add offset to display all channels
        for i in range(0, len(self.matrix[0, :])):
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
