#
#  Python Polyphonic MIDI Synthesizer
#
#  Filename:  bpass.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#

##  Band-pass filter.
class band_pass:
    ##  Store test_value
    __high_pass = 0
    __low_pass = 0

    ## Test process, simply print the test_value.
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def process(self, signal):
        return signal

    ##  Build an array of save data for the module.
    #  Bindings should have the format class_name.member_name.
    #  @param self Object pointer
    #  @return Module data to save
    def save_data(self):
        return [
            [ 'band_pass.set_high_pass', self.__high_pass ],
            [ 'band_pass.set_low_pass', self.__low_pass ]
        ]

    ## Set test value.
    #  @param self Object pointer
    #  @param val New value to set
    def set_high_pass(self, val):
        self.__high_pass = val

## Set test value.
    #  @param self Object pointer
    #  @param val New value to set
    def set_low_pass(self, val):
        self.__low_pass = val
