#
#  Python Polyphonic MIDI Synthesizer
#
#  Filename:  patch.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#

##  Creates "patches" of "synth modules" to process the signal.
class patchboard:
    ##  Initialize patchboard.
    #  \param self Object pointer
    def __init__(self):
        self.__patches = list()

    ##  Add a module to the patchboard.
    #  These will be processed in order loaded.
    #  \param self Object pointer
    #  \mod Synth module to add
    def add_module(self, mod):
        self.__patches.append(mod)

    ##  Clear all loaded modules.
    #  \param self Object pointer
    def clear_modules(self):
        self.__patches.clear()

    ##  Process modules in order.
    #  \param self Object pointer
    #  \param signal Signal data to modify
    #  \return Modified signal data
    def patch(self, signal):
        for module in self.__patches:
            signal = module.process(signal)
        return signal
