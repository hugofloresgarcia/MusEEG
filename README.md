# MusEEG

MusEEG is a python package designed to function as the software component for a music-oriented Brain-Computer Interface. The code is currently designed for the 14-Channel Emotiv EPOC+ (that's the only headset I have available at the moment), but it should be easily modifiable, provided that you have a means of obtaining a RAW EEG stream from your device. Although it is not yet fully functional (I am still waiting on my research lab to buy access to the RAW EEG stream of the EPOC+), the main MusEEG module is ready, and performs preprocessing and classification tasks on EEG data well. 

Disclaimer: This is a work in progress. The MusEEG module works well but an actual application is still in progress. 

# Motivation
MusEEG is both my Honors thesis and senior design project for my undergraduate studies at Georgia Southern University. The primary goal of MusEEG is to provide a

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
