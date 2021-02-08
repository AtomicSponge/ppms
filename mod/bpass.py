#
#  Python Polyphonic MIDI Synthesizer
#
#  Filename:  bpass.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#

from .parts import synthmod, gate_control
import numpy as np

##  Band-pass filter.
class band_pass(synthmod, gate_control):
    ##  Store high pass amount
    __high_pass = 0
    ##  Store low pass amount
    __low_pass = 0

    #__gate_list = list()

    ## Process low pass and high pass filters
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def process(self, signal):
        #  Do low pass
        if self.__low_pass > self.MIDI_MIN:
            filter_amnt = 1 - (self.__low_pass / self.MIDI_MAX)
            for x in np.nditer(np.where(signal > filter_amnt)):
                signal[x] = 0

        #  Do high pass
        if self.__high_pass > self.MIDI_MIN:
            filter_amnt = -1 + (self.__high_pass / self.MIDI_MAX)
            for x in np.nditer(np.where(signal < filter_amnt)):
                signal[x] = 0

        return signal

    ##  Build an array of save data for the module.
    #  Bindings should have the format class_name.member_name.
    #  @param self Object pointer
    #  @return Module data to save
    def save_data(self):
        return [
            [ 'band_pass.set_low_pass', self.__low_pass ],
            [ 'band_pass.set_high_pass', self.__high_pass ]
        ]

    ## Set high pass value.
    #  @param self Object pointer
    #  @param val New value to set
    def set_high_pass(self, val):
        self.__high_pass = val

    ## Set low pass value.
    #  @param self Object pointer
    #  @param val New value to set
    def set_low_pass(self, val):
        self.__low_pass = val
