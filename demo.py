import os
import MusEEG
from MusEEG import eegData, chord, classifier
import numpy as np

#open and reset midiport
MusEEG.resetPort()

#list of gestures to be used in classifier
gestures = ['smile', 'bitelowerlip', 'eyebrows', 'hardblink', 'lookleft', 'lookright',
            'neutral', 'scrunch', 'tongue']

#load the DNN classifier (bigbrain for whole eeg chunks)
brain = classifier()
brain.loadmodel(os.path.join(MusEEG.parentDir, 'data', 'savedModels', 'bigBrain_v2'))

#define chords and tempo to be used
chord.tempo = 60 #bpm
chord.midiChannel = 0 #add 1

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
polychordcde = chord(['C3', 'E3', 'G3', 'D4', 'F#4', 'A4', 'E5', 'G#5', 'B5']) #todo: add a polychord(chord) method
dbmaj7 = chord(['Db4', 'F4', 'Ab4', 'C5', 'Eb5'])
margaretsmagicchord = chord(['D4', 'F4', 'A#4'])

#refer gestures to chords
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

def demoComponent():
    while (True):
        try:
            #prompt user what gesture they'd like to demo and load a random sample from the dataset to test
            eeg = eegData()
            print('\nHello! welcome to the MusEEG demo. This demo will send a pre-recorded brain signal, classify it into\n'
                  'a facial gesture using a deep learning algorithm, and the turn it into a set of pre-referenced\n'
                  ' chords. if you are familiar with music and prorgamming, feel free to edit the chord objects\n '
                  'and the chord-facial gesture dictionary in the cerebro.py file\n\n')
            print('NOTE: make sure to run this script BEFORE you open your DAW/virtual instrument due to MIDI port '
                  'reset purposes\n')
            print('available gestures: ' )
            print(gestures)
            name = input('\n\nwhat gesture would you like to send to the neural network? please enter one of the '
                         'gestures available above:  ')
            if name not in mididict:
                raise Exception('this gesture was not found.')
            length = input('how long would you like the note to last (in quarter notes)? the current tempo is: ' + str(chord.tempo) + ' ')

            #subdirectory where sample chunks are located
            SUBDIR = os.path.join('bigChunks', 'hugo_facialgestures')
            #load random sample from bigChunks subdirectory.
            eeg.loadChunkFromTraining(subdir=SUBDIR, filename=name+'_'+str(np.random.randint(0, 60))+'.csv')

            #plot raw eeg data
            eeg.plotRawEEG(title=eeg.filename)

            #process eegdata: wavelet transform, statistical extraction
            print('performing wavelet transform')
            brainInput = eeg.process()

            #plot wavelet transform of channel 2
            eeg.plotWavelets(channel=1)

            #classify facial gesture in DNN
            brainOutput = brain.classify(brainInput.reshape(1, 350))
            print('\nthe neural network has taken the brain signal and classified it.')
            gestureResult = gestures[brainOutput]
            print('classification result: ' + gestureResult)

            #refer classification to midi dictionary and refer chord object to musician
            musician = mididict[gestureResult]


            print('\nthe musician is about to play the chord object. It is sending a midi message through channel '
                  + str(chord.midiChannel+1)+ '. if you have a DAW/MIDI monitor installed, the message should have been'
                                              ' received.')
            musician.pause(4)

            #finally, play the chord for the length requested
            musician.play()
            musician.pause(int(length))
            musician.stop()
            print('\n\n\n')

            cont = input('would you like to try another eeg signal? (y/n)')
            if cont == 'y':
                continue
            elif cont == 'n':
                break
            else:
                print('invalid command. exiting anyway')
                break

        except KeyboardInterrupt:
            break

demoComponent()
MusEEG.closePort()
