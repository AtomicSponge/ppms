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

##  Generates samples of different waveforms
class oscillator:
    ##  Initialize and generate sample data.
    #  \param self Object pointer
    #  \param sample_rate Rate to create sample
    def __init__(self, sample_rate):
        ##  Store the phase data
        self.__sample_data = np.arange(sample_rate) / sample_rate

    ##  Use A440 to calculate the note frequency.
    #  \param self Object pointer
    #  \param note Note to calculate
    #  \return The calculated frequency
    def __calc_frequency(self, note):
        return math.pow(2, (note - 69) / 12) * 440

    ##  Return a sawtooth wave sample.
    #  \param self Object pointer
    #  \param note Note to play
    #  \return Sawtooth sample
    def sawtooth(self, note):
        return signal.sawtooth(2 * np.pi * self.__calc_frequency(note) * self.__sample_data)

    ##  Return a triangle wave sample.
    #  \param self Object pointer
    #  \param note Note to play
    #  \return Triangle sample
    def triangle(self, note):
        return signal.sawtooth(2 * np.pi * self.__calc_frequency(note) * self.__sample_data, 0.5)

    ##  Return a square wave sample.
    #  \param self Object pointer
    #  \param note Note to play
    #  \return Square sample
    def square(self, note):
        return signal.square(2 * np.pi * self.__calc_frequency(note) * self.__sample_data)

    ##  Return a sine wave sample.
    #  \param self Object pointer
    #  \param note Note to play
    #  \return Sine sample
    def sine(self, note):
        return np.sin(2 * np.pi * self.__calc_frequency(note) * self.__sample_data)
