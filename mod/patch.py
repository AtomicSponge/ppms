##################################################
#  Filename:  patch.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
##################################################

class patchboard:
    def __init__(self):
        self.__patches = list()

    def add_module(self, mod):
        self.__patches.append(mod)

    def patch(self, signal):
        for module in self.__patches:
            signal = module(signal)
        return signal
