#
#  Python Polyphonic MIDI Synthesizer
#
#  Filename:  test.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#

##  PPMS Synth Module for testing the patchboard.
class test_module:
    ##  Store test_value
    __test_value = 0

    ## Test process.
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def process(self, signal):
        print("Test value:", self.__test_value)
        return signal

    ## Set control value
    #  @param self Object pointer
    #  @param val New value to set
    def set_control_value(self, val):
        self.__test_value = val
