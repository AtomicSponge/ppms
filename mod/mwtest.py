#
#  Python Polyphonic MIDI Synthesizer
#
#  Filename:  mwtest.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#

from .parts import synthmod, mod_control

##  PPMS Synth Module for testing the mod wheel.
class mwtest_module(synthmod, mod_control):
    ## Test process, print mod wheel value if it's set
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def process(self, signal):
        if self.get_mod_value() > 0:
            print("Mod wheel: ", self.get_mod_value())
        return signal
