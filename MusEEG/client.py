from MusEEG import eegData
from MusEEG import TrainingDataMacro
import numpy as np
from numpy import array
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from collections import deque
from scipy import signal
from numpy.fft import fft
import numpy as np


import socket
import queue

class client:
    BUFFER_SIZE = eegData.chunkSize
    host = "127.0.0.1"
    port = 5555
    sampleRate = eegData.sampleRate
    streamIsSimulated = False
    done = False

    windowSize = eegData.chunkSize * 2
    line = deque([[0 for channels in range(0, eegData.nchannels)] for packets in range(0, windowSize)])

    # Named fields according to Warren doc !
    FIELDS = {"COUNTER": 0, "DATA-TYPE": 1, "AF3": 4, "F7": 5, "F3": 2, "FC5": 3, "T7": 6, "P7": 7, "O1": 8, "O2": 9,
              "P8": 10, "T8": 11, "FC6": 14, "F4": 15, "F8": 12, "AF4": 13, "DATALINE_1": 16, "DATALINE_2": 17}

    def getCounter(self, packet):
        counter = packet["COUNTER"]
        return counter

    def data2dic(self, data):
        field_list = data.split(b',')

        if len(field_list) > 17:
            return {field: float(field_list[index]) for field, index in self.FIELDS.items()}
        else:
            return -1

    def dict2list(self, data):
        list = [data["AF3"], data["F7"], data["F3"], data["FC5"], data["T7"], data["P7"], data["O1"],
                data["O2"], data["P8"], data["T8"], data["FC6"], data["F4"], data["F8"], data["AF4"]]
        return list

    def setup(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.s.send(b"\r\n")

        # To read the header msgs about cykit etc...
        self.s.recv(168, socket.MSG_WAITALL)

        # Local buffer to store parts of the messages
        self.buffer = b''

        # If when when split by \r, \r was the last character of the message, we know that we have to remove \n from
        # the begining of the next message
        self.remove_newline = False

    def stream(self):
        self.q = queue.LifoQueue()
        self.psdq = queue.LifoQueue()
        self.plotq = queue.LifoQueue()
        def workerjob():
            try:
                while True:
                    # -*- coding: utf8 -*-
                    #
                    # Cykit Example TCP - Client
                    # author: Icannos
                    # modified for MusEEG by: hugo flores garcia
                    import matplotlib
                    # We read a chunk
                    data = self.s.recv(self.BUFFER_SIZE)

                    # If we have to remove \n at the begining
                    if self.remove_newline:
                        data = data[1:]
                        self.remove_newline = False

                    # Splitting the chunk into the end of the previous message and the begining of the next message
                    msg_parts = data.split(b'\r')

                    # If the second part ends with nothing when splitted we will have to remove \n next time
                    if msg_parts[-1] == b'':
                        self.remove_newline = True
                        # Therefore the buffer for the next step is empty
                        self.n_buffer = b''
                    else:
                        # otherwise we store the begining of the next message as the next buffer
                        self.n_buffer = msg_parts[-1][1:]

                    # We interprete a whole message (begining from the previous step + the end
                    fields = self.data2dic(self.buffer + msg_parts[0])

                    # We setup the buffer for next step
                    self.buffer = self.n_buffer
                    self.plotq.put(fields, block=False)
                    self.psdq.put(fields,block=False)
                    # Print all channel
                    self.q.put(fields, block=False)
            except Exception:
                self.q.join()
                self.s.close()

        worker = threading.Thread(target=workerjob, args=())
        worker.setDaemon(True)
        worker.start()

    def getBuffer(self, bufferSize=eegData.chunkSize/1.25*4, highpass=True):
        buffer = []
        while len(buffer) < bufferSize:
            try:
                packet = self.psdq.get()
                buffer.append(self.dict2list(packet))
            except TypeError:
                pass

        buffer = np.array(buffer).transpose()
        if highpass:
            # highpass at 4Hz
            filter = signal.butter(10, 4, 'hp', fs=eegData.sampleRate, output='sos')
            buffer = signal.sosfilt(filter, buffer)
        return buffer

    def getChunk(self, chunkSize=eegData.chunkSize):
        bufferchunk = []
        chunk = []
        self.chunkq = queue.Queue()
        while len(chunk) < chunkSize:
            try:
                ## get packets until u find one that passes the threshold
                data = self.q.get()
                # print(data["COUNTER"])
                formattedData = self.dict2list(data)
                # self.plotClientStream(formattedData=formattedData, figure=self.figure)
                chunk.append(formattedData)

            except TypeError:
                pass

        self.chunkq.put(array(chunk))

        if self.streamIsSimulated:
            chunk = array(chunk) + 4100

        return array(chunk) - 4100

    def simulateStream(self, gesture, subdir='hugo_facialgestures', streamSpeed=1):
        self.streamIsSimulated = True
        eeg = TrainingDataMacro()
        eeg.importCSV(subdir=subdir, filename=gesture+'.csv', tag=gesture)
        self.q = queue.Queue()
        self.plotq = queue.Queue()
        self.psdq = queue.Queue()
        self.streamSpeed = streamSpeed
        def worker():
            for i in range(0,len(eeg.matrix)):
                packet = {eeg.eegChannels[j]: eeg.matrix[i][j] for j in range(len(eeg.emotivChannels))}
                packet["COUNTER"] = i
                self.q.put(item=packet)
                self.plotq.put(item=packet)
                self.psdq.put(item=packet)
                time.sleep(1/eegData.sampleRate/streamSpeed)

        simulationWorker = threading.Thread(target=worker)
        simulationWorker.setDaemon(True)
        simulationWorker.start()

    def getChunkWithBackTrack(self):
        bufferchunk = []
        chunk = []
        self.chunkq = queue.Queue()
        while len(chunk) < eegData.chunkSize:
            try:
                ## get packets until u find one that passes the threshold
                data = self.q.get()
                # print(data["COUNTER"])
                formattedData = self.dict2list(data)
                # self.plotClientStream(formattedData=formattedData, figure=self.figure)
                bufferchunk.append(formattedData)


                ## backtrack a couple samples to get all the transient info, then finish getting the chunk
                if eegData.checkThreshold(data):
                    chunk.extend(bufferchunk[(-1-eegData.backTrack):-1])
                    while len(chunk) <eegData.chunkSize:
                        data = self.q.get()
                        formattedData = self.dict2list(data)
                        chunk.append(formattedData)
            except TypeError:
                pass

        self.chunkq.put(array(chunk))

        if self.streamIsSimulated:
            chunk = array(chunk) + 4100

        return array(chunk) - 4100

    def plotClientStream(self, streamfigure=None, plotChunks=False,  chunkfigure=None, offset=400):
        if streamfigure is None:
            streamfigure = plt.Figure()
        while not self.plotq.empty():
            appendedChunk = []
            while len(appendedChunk) < self.windowSize/8:
                self.line.popleft()
                packet = self.plotq.get()
                self.line.append(self.dict2list(packet))
                appendedChunk.append(packet)

            # define time axis
            tAxis = np.arange(0, self.windowSize)  # create time axis w same length as the data matrix
            tAxis = tAxis / self.sampleRate  # adjust time axis to 256 sample rate

            plotBuffer = array(self.line) - 4100
            yAxis = plotBuffer + offset * 13

            # add offset to display all channels
            for i in range(0, len(plotBuffer[0, :])):
                yAxis[:, i] -= offset * i

            if plotChunks:
                if chunkfigure is None:
                    chunkfigure = plt.Figure()
                if not self.chunkq.empty():
                    eeg = eegData()
                    eeg.chunk = self.chunkq.get()
                    chunkfigure = eeg.plotRawEEG(chunkfigure)


            streamfigure.canvas.flush_events()
            ax = streamfigure.add_subplot(111)
            ax.clear()
            ax.set_ylim(-300, offset * 20)
            ax.legend(eegData.eegChannels)
            ax.set_xlabel('time')
            ax.plot(tAxis, yAxis)
            streamfigure.canvas.draw()
            plt.pause(0.001)

        return streamfigure, chunkfigure


