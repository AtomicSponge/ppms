#
#  Python Polyphonic MIDI Synthesizer
#
#  Filename:  bpass.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#

import numpy as np

##  Band-pass filter.  WIP
class band_pass:
    ##  Store high pass amount
    __high_pass = 0
    ##  Store low pass amount
    __low_pass = 0
    ##  Store filter max value
    __pass_max = 127

    ## Process low pass and high pass filters
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def process(self, signal):
        #print(np.amin(signal))
        #print(np.amax(signal))

        #  Do low pass
        if self.__low_pass > 0:
            amnt = self.__low_pass / self.__pass_max
            filter_amnt = np.amin(signal) - (np.amin(signal) * amnt)
            #print(filter_amnt)
            for x in np.nditer(np.where(signal < filter_amnt)):
                signal[x] = filter_amnt

        #  Do high pass
        if self.__high_pass > 0:
            amnt = self.__high_pass / self.__pass_max
            filter_amnt = np.amax(signal) - (np.amax(signal) * amnt)
            #print(filter_amnt)
            for x in np.nditer(np.where(signal > filter_amnt)):
                signal[x] = filter_amnt

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
