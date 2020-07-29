##################################################
#  Filename:  osc.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
##################################################

import math
import numpy as np
from scipy import signal

class oscillator:
    def __init__(self, sample_rate):
        self.__sample_data = np.arange(sample_rate) / sample_rate

    def __calc_frequency(self, note):
        return math.pow(2, (note - 69) / 12) * 440

    def sawtooth(self, note):
        return signal.sawtooth(2 * np.pi * self.__calc_frequency(note) * self.__sample_data)

    def triangle(self, note):
        return signal.sawtooth(2 * np.pi * self.__calc_frequency(note) * self.__sample_data, 0.5)

    def square(self, note):
        return signal.square(2 * np.pi * self.__calc_frequency(note) * self.__sample_data)

    def sine(self, note):
        return np.sin(2 * np.pi * self.__calc_frequency(note) * self.__sample_data)
