#
#  Python Polyphonic MIDI Synthesizer
#
#  Filename:  env.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#

import numpy as np
from .parts import synthmod

##  Envelope - ADSR
class envelope(synthmod):
    __attack = 0
    __decay = 0
    __sustain = 0
    __release = 0

    __envelope = np.zeros(shape=(10,1), dtype=np.float32)

    ##  Generate the envelope signal.
    #  This is called after a parameter is changed.
    #  @param self Object pointer
    def __generate_envelope(self):
        pass
        #self.__attack / self.MIDI_MAX
        #self.__decay / self.MIDI_MAX
        #self.__sustain / self.MIDI_MAX
        #self.__release / self.MIDI_MAX

    ## Process envelope.
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def process(self, note, signal):
        #print("note: ", note)
        #print("freq: ", self.calc_frequency(note))
        #print("period: ", 1 / self.calc_frequency(note))
        if self.__attack > 0 or \
        self.__decay > 0 or \
        self.__sustain > 0 or \
        self.__release > 0:
            return signal * self.__envelope
        return signal

    ##  Build an array of save data for the module.
    #  Bindings should have the format class_name.member_name.
    #  @param self Object pointer
    #  @return Module data to save
    def save_data(self):
        return [
            [ 'envelope.set_attack', self.__attack ],
            [ 'envelope.set_decay', self.__decay ],
            [ 'envelope.set_sustain', self.__sustain ],
            [ 'envelope.set_release', self.__release ]
        ]

    ## Set attack parameter.
    #  @param self Object pointer
    #  @param val New value to set
    def set_attack(self, val):
        self.__attack = val
        self.__generate_envelope(self)

    ## Set decay parameter.
    #  @param self Object pointer
    #  @param val New value to set
    def set_decay(self, val):
        self.__decay = val
        self.__generate_envelope(self)

    ## Set sustain parameter.
    #  @param self Object pointer
    #  @param val New value to set
    def set_sustain(self, val):
        self.__sustain = val
        self.__generate_envelope(self)

    ## Set release parameter.
    #  @param self Object pointer
    #  @param val New value to set
    def set_release(self, val):
        self.__release = val
        self.__generate_envelope(self)
