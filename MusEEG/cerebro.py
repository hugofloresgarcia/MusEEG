from .classifier import *
from .eegData import *
from .music import *

from MusEEG import parentDir, resetPort, closePort
import threading


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

    gestures = ['smile', 'bitelowerlip', 'eyebrows', 'hardblink', 'lookleft', 'lookright',
                'neutral', 'scrunch', 'tongue']

    """
    chord objects are defined here. the chord() class takes any set of notes as an input.
    """
    cmaj7sharp11add13 = chord(['C4', 'E4', 'G4', 'B4', 'D5', 'F#4', 'A5'], name='cmaj7sharp11add13')
    fminmaj7 = chord(['F4', 'Ab4', 'C5', 'E5'], name='fminmaj7')
    fmaj7 = chord(['F4', 'A4', 'C5', 'E5', 'G5'], name='fmaj7')
    ab69 = chord(['Ab4', 'C5', 'F5', 'Bb5', 'C6'], name='ab69')
    dmin7b5 = chord(['D4', 'F4', 'Ab4', 'C5', 'E5'], name='dmin7b5')
    g7b9 = chord(['G4', 'B4', 'D5', 'F5', 'Ab5'], name='g7b9')
    c5 = chord(['C3', 'G3'], name='c5')
    noChord = chord([], name='nochord')
    polychordcde = chord(
        ['C3', 'E3', 'G3', 'D4', 'F#4', 'A4', 'E5', 'G#5', 'B5'], name='E/D/C')  # todo: add a polychord(chord) method
    dbmaj7 = chord(['Db4', 'F4', 'Ab4', 'C5', 'Eb5'], name='dbmaj7')
    margaretsmagicchord = chord(['D4', 'F4', 'A#4'], name='margschord')

    defaultchordlist = [cmaj7sharp11add13.notelist, fminmaj7.notelist, fmaj7.notelist, ab69.notelist, dmin7b5.notelist,
                        c5.notelist, noChord.notelist,
                        polychordcde.notelist, dbmaj7.notelist]

    """
    this dictionary is where chords are referenced to facial gestures.
    """

    def __init__(self):
        #default mididict. it will be updated everytime the user presses the update chord button
        self.mididict = {'smile': self.cmaj7sharp11add13,
                         'bitelowerlip': self.fmaj7,
                         'hardblink': self.fminmaj7,
                         'eyebrows': self.ab69,
                         'lookleft': self.g7b9,
                         'lookright': self.c5,
                         'neutral': self.noChord,
                         'scrunch': self.polychordcde,
                         'tongue': self.dbmaj7}

        # open and reset midiport
        resetPort()

        # list of gestures to be used in classifier
        gestures = ['smile', 'bitelowerlip', 'eyebrows', 'hardblink', 'lookleft', 'lookright',
                    'neutral', 'scrunch', 'tongue']

        # load the DNN classifier (bigbrain for whole eeg chunks)
        self.brain = classifier()
        self.brain.loadmodel(os.path.join(parentDir, 'data', 'savedModels', 'bigBrain_v2'))

        # define chords and tempo to be used
        music.tempo = 60  # bpm
        music.midiChannel = 0  # add 1

    def updateChordList(self, chordlistlist):
        for c in chordlistlist:
            index = chordlistlist.index(c)
            gestureBeingDefined = self.gestures[index]
            self.mididict[gestureBeingDefined] = chord(notelist=chordlistlist[index], name=gestureBeingDefined)
            print(self.mididict)

    def loadFromDataSet(self, name):
        # subdirectory where sample chunks are located and load a random chunk from trianing dataset
        SUBDIR = os.path.join('bigChunks', 'hugo_facialgestures')
        self.eeg.loadChunkFromTraining(subdir=SUBDIR, filename=name + '_' + str(np.random.randint(0, 60)) + '.csv')

    def processAndPlay(self, arp, tempo, arpDurationFromGUI, noteDurationFromGUI):
        print('performing wavelet transform')
        brainInput = self.eeg.process()

        self.arpDurationFromGUI = arpDurationFromGUI
        self.noteDurationFromGUI = noteDurationFromGUI

        # classify facial gesture in DNN
        brainOutput = self.brain.classify(brainInput.reshape(1, 350))
        print('\nthe neural network has taken the brain signal and classified it.')
        self.gestureResult = self.gestures[brainOutput]
        print('classification result: ' + self.gestureResult)

        # refer classification to midi dictionary and refer chord object to musician
        musician = self.mididict[self.gestureResult]
        musician.set_tempo(tempo=tempo)

        #with threading
        musicianProcess = threading.Thread(target=self.perform, args=[musician, arp])
        musicianProcess.start()

    def perform(self, musician, arp):
        if arp == True:
            print('arpeggiate!')
            musician.arpeggiate(notelength=self.arpDurationFromGUI, vel=64, numTimes=8)

        else:
            musician.panic()
            musician.playchord(qtrnotes=self.noteDurationFromGUI)
