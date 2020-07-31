#
#  Python Polyphonic MIDI Synthesizer
#
#  Filename:  osc.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#

import math
import numpy as np
from scipy import signal

##  Oscillator class
# ...
class oscillator:
    ##  Initialize and generate sample data
    def __init__(self, sample_rate):
        self.__sample_data = np.arange(sample_rate) / sample_rate

    ##  Use A440 to calculate the note frequency
    def __calc_frequency(self, note):
        return math.pow(2, (note - 69) / 12) * 440

    ##  Return a sawtooth wave sample
    def sawtooth(self, note):
        return signal.sawtooth(2 * np.pi * self.__calc_frequency(note) * self.__sample_data)

    ##  Return a triangle wave sample
    def triangle(self, note):
        return signal.sawtooth(2 * np.pi * self.__calc_frequency(note) * self.__sample_data, 0.5)

    ##  Return a square wave sample
    def square(self, note):
        return signal.square(2 * np.pi * self.__calc_frequency(note) * self.__sample_data)

    ##  Return a sine wave sample
    def sine(self, note):
        return np.sin(2 * np.pi * self.__calc_frequency(note) * self.__sample_data)
