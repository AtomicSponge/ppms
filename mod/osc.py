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
    #  @param self Object pointer
    #  @param sample_rate Rate to create sample
    def __init__(self):
        ##  Store the phase data
        #self.__sample_data = np.arange(sample_rate, dtype=np.float32) / sample_rate
        self.__blocksize = 0
        self.__samplerate = 0

    def config(self, size, rate):
        self.__blocksize = size
        self.__samplerate = rate

    ##  Use A440 to calculate the note frequency.
    #  @param self Object pointer
    #  @param note Note to calculate
    #  @return The calculated frequency
    def __calc_frequency(self, note):
        return math.pow(2, (note - 69) / 12) * 440

    ##  Calc
    #  @param self Object pointer
    #  @param time_data
    #  @return
    def __calc_timedata(self, time_data):
        t = (time_data + np.arange(self.__blocksize)) / self.__samplerate
        return t.reshape(-1, 1)

    ##  Return a sawtooth wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param time_data
    #  @return Sawtooth sample
    def sawtooth(self, note, time_data):
        return signal.sawtooth(2 * np.pi * self.__calc_frequency(note) * self.__calc_timedata(time_data))

    ##  Return a triangle wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param time_data
    #  @return Triangle sample
    def triangle(self, note, time_data):
        return signal.sawtooth(2 * np.pi * self.__calc_frequency(note) * self.__calc_timedata(time_data), 0.5)

    ##  Return a square wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param time_data
    #  @return Square sample
    def square(self, note, time_data):
        return signal.square(2 * np.pi * self.__calc_frequency(note) * self.__calc_timedata(time_data))

    ##  Return a sine wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param time_data
    #  @return Sine sample
    def sine(self, note, time_data):
        return np.sin(2 * np.pi * self.__calc_frequency(note) * self.__calc_timedata(time_data))
