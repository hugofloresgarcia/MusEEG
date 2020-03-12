from .classifier import *
from .eegData import *
from .music import *
from .client import *

from MusEEG import parentDir, resetPort

import pickle
import threading

"""
DEPRECATED
this is the processor used to run the demo app
"""


class cerebro:
    """
    hello message to display in UI
    """
    demomsg = (
        'Hello! welcome to the MusEEG demo. This demo will: \n'
        '- send a pre-recorded brain signal of your choice when you click on any of the gesture buttons\n'
        '- process it using a 4-level, db2 wavelet transform\n'
        '- extract the first four statistical moments of the wavelet decompositions (mean, variance, skewness, kurtosis)\n'
        '- classify it using a deep neural network\n'
        '- using the results from the DNN, play the chord that is referenced to the gesture using MIDI\n'
        '- to change a chord, press the "update chord dictionary" button after youve changed the notes\n')
    eeg = eegData()

    gestures = ['smile', 'eyebrows', 'lookleft', 'lookright',
                     'neutral', 'scrunch']

    def __init__(self):
        #default mididict. it will be updated everytime the user presses the update chord button
        self.mididict = self.loadMIDIdict(os.path.join(parentDir, 'data',  'MIDIdicts', 'simpleCmajor.pickle'))

        # open and reset midiport
        resetPort()

        # load the ANN classifier (bigbrain for whole eeg chunks, small brain for small chunks)
        self.bigBrain = classifier()
        self.bigBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'bigBrain_v2'))

        self.smallBrain = classifier()
        self.smallBrain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'smallBrain_v1'))

        # define chords and tempo to be used
        music.tempo = 60  # bpm
        music.midiChannel = 0  # add 1

    def setupClient(self):
        self.client = client()
        self.client.setup()

    def updateChordList(self, chordlistlist):
        for c in chordlistlist:
            index = chordlistlist.index(c)
            gestureBeingDefined = self.gestures[index]
            self.mididict[gestureBeingDefined] = chord(notelist=chordlistlist[index], name=gestureBeingDefined)
            print(self.mididict)

    def saveMIDIdict(self, addressPath):
        with open(os.path.join(addressPath), 'wb') as handle:
            pickle.dump(self.mididict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def loadMIDIdict(self, addressPath):
        with open(addressPath, 'rb') as handle:
            self.mididict = pickle.load(handle)
            return self.mididict

    def loadFromDataSet(self, name):
        # subdirectory where sample chunks are located and load a random chunk from trianing dataset
        SUBDIR = os.path.join('trainbatch1', 'bigChunks')
        self.eeg.loadChunkFromTraining(subdir=SUBDIR, filename=name + '_' + str(np.random.randint(0, 60)) + '.csv')

    def processAndPlay(self, arp, tempo, arpDurationFromGUI, noteDurationFromGUI):
        print('performing wavelet transform')
        brainInput = self.eeg.process()

        self.arpDurationFromGUI = arpDurationFromGUI
        self.noteDurationFromGUI = noteDurationFromGUI

        # classify facial gesture in DNN
        brainOutput = self.bigBrain.classify(brainInput.reshape(1, 350))
        print('the neural network has taken the brain signal and classified it.')
        self.gestureResult = self.gestures[brainOutput]
        print('classification result: ' + self.gestureResult)

        # refer classification to midi dictionary and refer chord object to musician
        musician = self.mididict[self.gestureResult]
        musician.set_tempo(tempo=tempo)

        #with threading
        musicianProcess = threading.Thread(target=self.perform, args=[musician, arp])
        musicianProcess.start()

    def perform(self, musician, arp):
        if arp:
            print('arpeggiate!')
            musician.arpeggiate(notelength=self.arpDurationFromGUI, vel=30, numTimes=8)

        else:
            musician.panic()
            musician.playchord(qtrnotes=self.noteDurationFromGUI, vel=30)
