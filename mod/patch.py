##########################################################
#
#  Python Polyphonic MIDI Synthesizer
#
##########################################################
#
#  Filename:  patch.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#
##########################################################

#  Patchboard class
class patchboard:
    #  Initialize patchboard
    def __init__(self):
        self.__patches = list()

    #  Add a module to the patchboard
    #  These will be processed in order loaded
    def add_module(self, mod):
        self.__patches.append(mod)

    #  Clear all loaded modules
    def clear_modules(self):
        self.__patches.clear()

    #  Process modules in order
    def patch(self, signal):
        for module in self.__patches:
            signal = module.process(signal)
        return signal
