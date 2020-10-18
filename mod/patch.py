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
    #  @param self Object pointer
    def __init__(self):
        self.__patches = list()

    ##  Add a module to the patchboard.
    #  These will be processed in order loaded.
    #  @param self Object pointer
    #  @param mod Synth module to add
    def add_module(self, mod):
        self.__patches.append(mod)

    ##  Clear all loaded modules.
    #  @param self Object pointer
    def clear_modules(self):
        self.__patches.clear()

    ##  Get a module by name.
    #  @param self Object pointer
    #  @param name Name of module to search for
    #  @return Module object if found, else None
    def get_module(self, name):
        for module in self.__patches:
            if(name == module.__name__):
                return module
        return None

    ##  Save all module data.
    #  @param self Object pointer
    #  @return List of all module save data
    def save_data(self):
        data = []
        for module in self.__patches:
            data += module.save_data(module)
        return data

    ##  Process modules in order.
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def patch(self, signal):
        for module in self.__patches:
            signal = module.process(module, signal)
        return signal

    ##  Send gate signal.
    #  @param self Object pointer
    #  @param signal Gate signal
    def send_gate(self, signal):
        for module in self.__patches:
            pass
            #if callable(module.gate_signal): #module.gate_signal(module, signal)
