#
#  Python Polyphonic MIDI Synthesizer
#
#  Filename:  reverb.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#

import numpy as np

##  PPMS Synth Module for reverb.  Shifts the signal and adds to original.
class reverberation:
    ##  Store reverb amount
    __reverb = 0
    ##  Max reverb value
    __reverb_max = 127

    ## Reverb process - Add a shifted array to the signal.
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def process(self, signal):
        signal += np.roll(signal, int(signal.size * (self.__reverb / self.__reverb_max)))
        #print(int(signal.size * (self.__reverb / self.__reverb_max)))
        return signal

    ##  Build an array of save data for the module.
    #  Bindings should have the format class_name.member_name.
    #  @param self Object pointer
    #  @return Module data to save
    def save_data(self):
        return [
            [ 'reverberation.set_reverb', self.__reverb ]
        ]

    ## Set reverb amount.
    #  @param self Object pointer
    #  @param val New value to set
    def set_reverb(self, val):
        self.__reverb = val
