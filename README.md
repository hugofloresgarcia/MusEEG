# MusEEG
website: [hugofloresgarcia/museeg](https://hugofloresgarcia.github.io/MusEEG/)

MusEEG is a python package designed to function as the software component for a music-oriented Brain-Computer Interface. The code is currently designed for the 14-Channel Emotiv EPOC+ (that's the only headset I have available at the moment), but it should be easily modifiable, provided that you have a means of obtaining a RAW EEG stream from your device. 

MusEEG is capable of sending OSC and MIDI messages, allowing for direct communication with a software instrument (MIDI) and for more customizable communication with music programming languages (SuperCollider/Max)

## Motivation
The primary goal of MusEEG is to expand the creative capabilities of musicians past any bodily limitations by creating a direct interface between the human brain and a musical instrument. By cutting the medium between the brain and music, MusEEG results in an instrument that is highly accessible to people with motor disabilities. This interdisciplinary project consists of multiple technical and creative modules nested in the fields of computer science, electrical engineering, music performance and composition, concluding with the performance of a piece composed for guitar and EEG.

## Requirements
The MusEEG module uses the following libraries
- numpy
- tensorflow
- scipy
- pywt
- mido
- python-rtmidi
- audiolazy
- matplotlib
- pandas
- osc4py3

see requirements.txt for the full list of dependencies

## Installation (Python 3.7)
[Install Python](https://realpython.com/installing-python/)

[Install pip](https://www.makeuseof.com/tag/install-pip-for-python/)

install requirements.txt:

`pip install -r requirements.txt`

## Using with SuperCollider 
MusEEG is capable of sending
- Discrete OSC messages for each facial expression (e.g. `/smile`)
- Continuous OSC messages for band power data (e.g. `/theta`)

which makes it easy to use with music programming languages (such as SuperCollider). Examples of usage with supercollider are in the /SuperCollider directory. 

## The MusEEG Module
Currently, the MusEEG package contains six main modules: 
- `music.py` (MIDI objects, chords, and melodies)
- `classifier.py` (build, train, save keras models easily)
- `eegData.py` (import, process, plot, save EEG data). 
- `cerebro.py` (methods to use music, classifier, and eegData together, store and load MIDI-facial expression dictionaries)
- `client.py` (TCP client to receive real-time raw EEG stream form [CyKit](https://github.com/CymatiCorp/CyKit))
- `processor.py` (real-time processing methods)

## Processor
the Processor.py module contains real-time processing methods. Running the Processor.py module with `python Processor.py` starts an EEG client and connects to a CyKit server (github.com/CymatiCorp/CyKit to run the EEG stream server), picks up raw EEG data, processes it, displays the classification result in the command line, and plays its respective MIDI event from the expression-MIDI dictionary. 

## Acknowledgments
Special thanks to Dr. Fernando Ríos and Dr. John Thompson for being awesome faculty mentors!
