from .classifier import *
from .eegData import *
from .music import *

from MusEEG import parentDir, resetPort, closePort
import threading


class cerebro:
    """
    hello message to display in UI
    """
    hellomsg = ('Hello! welcome to the MusEEG demo. \nThis demo will send a pre-recorded brain signal, classify it into '
            'a facial gesture using a deep learning algorithm, and the turn it into a set of pre-referenced '
            ' chords. If you are familiar with music and prorgamming, feel free to edit the chord objects '
            'and the chord-facial gesture dictionary in the cerebro.py file')
    eeg = eegData()

    gestures = ['smile', 'bitelowerlip', 'eyebrows', 'hardblink', 'lookleft', 'lookright',
                'neutral', 'scrunch', 'tongue']

    """
    chord objects are defined here. the chord() class takes any set of notes as an input.
    """
    cmaj7sharp11add13 = chord(['C4', 'E4', 'G4', 'B4', 'D5', 'F#4', 'A5'])
    fminmaj7 = chord(['F4', 'Ab4', 'C5', 'E5'])
    fmaj7 = chord(['F4', 'A4', 'C5', 'E5', 'G5'])
    ab69 = chord(['Ab4', 'C5', 'F5', 'Bb5', 'C6'])
    dmin7b5 = chord(['D4', 'F4', 'Ab4', 'C5', 'E5'])
    g7b9 = chord(['G4', 'B4', 'D5', 'F5', 'Ab5'])
    c5 = chord(['C3', 'G3'])
    noChord = chord([])
    polychordcde = chord(
        ['C3', 'E3', 'G3', 'D4', 'F#4', 'A4', 'E5', 'G#5', 'B5'])  # todo: add a polychord(chord) method
    dbmaj7 = chord(['Db4', 'F4', 'Ab4', 'C5', 'Eb5'])
    margaretsmagicchord = chord(['D4', 'F4', 'A#4'])

    # refer gestures to chords
    """
    this dictionary is where chords are referenced to facial gestures.
    """
    mididict = {'smile': cmaj7sharp11add13,
                'bitelowerlip': fmaj7,
                'hardblink': fminmaj7,
                'eyebrows': ab69,
                'lookleft': g7b9,
                'lookright': c5,
                'neutral': noChord,
                'scrunch': polychordcde,
                'tongue': dbmaj7}

    def __init__(self):
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

    def loadFromDataSet(self, name):
        # subdirectory where sample chunks are located and load a random chunk from trianing dataset
        SUBDIR = os.path.join('bigChunks', 'hugo_facialgestures')
        self.eeg.loadChunkFromTraining(subdir=SUBDIR, filename=name + '_' + str(np.random.randint(0, 60)) + '.csv')

    def processAndPlay(self, arp):
        print('performing wavelet transform')
        brainInput = self.eeg.process()

        # classify facial gesture in DNN
        brainOutput = self.brain.classify(brainInput.reshape(1, 350))
        print('\nthe neural network has taken the brain signal and classified it.')
        gestureResult = self.gestures[brainOutput]
        print('classification result: ' + gestureResult)

        # refer classification to midi dictionary and refer chord object to musician
        musician = self.mididict[gestureResult]

        t1 = threading.Thread(target=self.perform, args=[musician, arp])
        t1.start()

    def perform(self, musician, arp):
        if arp == True:
            print('arpeggiate!')
            musician.arpeggiate(0.125, vel=64, numTimes=10)

        else:
            musician.playchord(durationInTicks=40)