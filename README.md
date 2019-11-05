# MusEEG

MusEEG is a python package designed to function as the software component for a music-oriented Brain-Computer Interface. The code is currently designed for the 14-Channel Emotiv EPOC+ (that's the only headset I have available at the moment), but it should be easily modifiable, provided that you have a means of obtaining a RAW EEG stream from your device. Although it is not yet fully functional (I am still waiting on my research lab to buy access to the RAW EEG stream of the EPOC+), the main MusEEG module is ready, and performs preprocessing and classification tasks on EEG data well. 

Disclaimer: This is a work in progress. The MusEEG module works well but an actual application is still in progress. 

# Motivation
The primary goal of MusEEG is to expand the creative capabilities of musicians past any bodily limitations by creating a direct interface between the human brain and a musical instrument. By cutting the medium between the brain and music, MusEEG results in an instrument that is highly accessible to people with motor disabilities. This interdisciplinary project consists of multiple technical and creative modules nested in the fields of computer science, electrical engineering, music performance and composition, concluding with the performance of a piece composed for guitar and EEG.

# Requirements
The MusEEG module uses the following libraries
- numpy
- tensorflow
- scipy
- pywt
- mido
- audiolazy
- matplotlib
- pandas

# Installation (Python 3.7)
install requirements.txt:

`pip install -r requirements.txt`

# Code Examples
Since I am still waiting on departmental funding to obtain a RAW EEG license to access RAW EEG data, there still isn't a way to implement MusEEG in real time. However, the demo.py file showcases how the eegData, classifier, and chord classes are used to create an eegData object, classify it using the classifier, and use it to trigger a MIDI event using chord. To run the file, simply run this command from terminal: 

`python demo.py`


# Acknowledgments
Special thanks to Dr. Fernando Ríos and Dr. John Thompson for being awesome faculty mentors!
