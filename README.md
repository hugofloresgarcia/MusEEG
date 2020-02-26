# MusEEG
website: [hugofloresgarcia/museeg](https://hugofloresgarcia.github.io/MusEEG/)

MusEEG is a python package designed to function as the software component for a music-oriented Brain-Computer Interface. The code is currently designed for the 14-Channel Emotiv EPOC+ (that's the only headset I have available at the moment), but it should be easily modifiable, provided that you have a means of obtaining a RAW EEG stream from your device. Although the main application is still in progres, the main MusEEG module is ready, and performs preprocessing and classification tasks on EEG data well. To view an example on how to use the MusEEG module, see the `demo.py` file. 

Disclaimer: I am still waiting on departmental funding to have access to a raw EEG stream, so this is a work in progress. The demo app provides a good example of its functionality but the main application is still in progress. 

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

## Demo App
The demo app provides a demo of MusEEG in action. It is able to load a random sample from the dataset, process w/ wavelet transform and classify using an ANN, and create a midi object off of it. 
To run the demo app: 

`python3 demoApp.py`

## Code Examples
the Processor.py module contains real-time processing methods. Running the Processor.py module with `python3 Processor.py` starts an EEG client and connects to a CyKit server (github.com/CymatiCorp/CyKit to run the EEG stream server), picks up raw EEG data, processes it, displays the classification result in the command line, and plays its respective MIDI event from the expression-MIDI dictionary. 

NOTE: because MusEEG creates a virtual MIDI port upon startup, `demoApp.py` and `example.py` must be run BEFORE the virtual instrument/DAW is opened for it to function properly. If not, MIDI drivers must be reset from the DAW prior to operation. 


## The MusEEG Module
Currently, the MusEEG package contains four main modules: 
- `music.py` (MIDI objects, chords, and melodies)
- `classifier.py` (build, train, save keras models easily)
- `eegData.py` (import, process, plot, save EEG data). 
- `cerebro.py` (methods to use music, classifier, and eegData together)
- `client.py` (TCP client to receive real-time raw EEG stream form [CyKit](https://github.com/CymatiCorp/CyKit))
- `processor.py` (real-time processing methods)

## Acknowledgments
Special thanks to Dr. Fernando Ríos and Dr. John Thompson for being awesome faculty mentors!
