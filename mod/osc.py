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
    #  @param rate Sample rate
    def __init__(self, rate):
        ##  Store the sample rate
        self.__frequency = rate

    ##  Use A440 to calculate the note frequency.
    #  @param self Object pointer
    #  @param note Note to calculate
    #  @return The calculated frequency
    def __calc_frequency(self, note):
        return math.pow(2, (note - 69) / 12) * 440

    ##  Calculate period
    #  @param self Object pointer
    #  @param frame_size Amount to generate
    #  @param time_data Position in time
    #  @return Period data
    def __calc_period(self, frame_size, time_data):
        t = (time_data + np.arange(frame_size)) / self.__frequency
        return t.reshape(-1, 1)

    ##  Calculate pitch bend
    #  @param self Object pointer
    #  @param note_freq Calculated note frequency
    #  @param pich_bend Calculated pitch bend amount
    #  @return The note frequency with pitch bend factored
    def __check_pitch_bend(self, note_freq, pitch_bend):
        if pitch_bend != 0:
            note_freq = note_freq * pitch_bend
        return note_freq

    ##  Return a sawtooth wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param time_data
    #  @return Sawtooth sample
    def sawtooth(self, note, pitch_bend, frame_size, time_data):
        return signal.sawtooth(2 * np.pi * self.__check_pitch_bend(self.__calc_frequency(note), pitch_bend) * self.__calc_period(frame_size, time_data))

    ##  Return a triangle wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param time_data
    #  @return Triangle sample
    def triangle(self, note, pitch_bend, frame_size, time_data):
        return signal.sawtooth(2 * np.pi * self.__check_pitch_bend(self.__calc_frequency(note), pitch_bend) * self.__calc_period(frame_size, time_data), 0.5)

    ##  Return a square wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param time_data
    #  @return Square sample
    def square(self, note, pitch_bend, frame_size, time_data):
        return signal.square(2 * np.pi * self.__check_pitch_bend(self.__calc_frequency(note), pitch_bend) * self.__calc_period(frame_size, time_data))

    ##  Return a sine wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param time_data
    #  @return Sine sample
    def sine(self, note, pitch_bend, frame_size, time_data):
        return np.sin(2 * np.pi * self.__check_pitch_bend(self.__calc_frequency(note), pitch_bend) * self.__calc_period(frame_size, time_data))
