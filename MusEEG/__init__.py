#todo: use emotions as upper harmonics of synthesized signal (affective computing)
#todo: clean up

import os
import sys
import numpy as np
import mido

"""MIDI Stuff: Open a port"""
port = mido.open_output()

def resetPort():
    port.reset()

def closePort():
    port.close()

np.set_printoptions(threshold=sys.maxsize)

##some global attributes
fileDir = os.path.dirname(os.path.abspath(__file__)) #should be the parent MusEEG directory
parentDir = os.path.dirname(fileDir)

#todo: make the plot windows non blocking and non stupid too


from .classifier import *
from .music import *
from .eegData import *
from .cerebro import *
from .client import *
