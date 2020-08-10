#
#  Python Polyphonic MIDI Synthesizer
#
#  Filename:  env.py
#  By:  Matthew Evans
#  See LICENSE.md for copyright information.
#

##  Envelope - ADSR
class envelope:
    __attack = 0
    __decay = 0
    __sustain = 0
    __release = 0
    __gate = False

    ## Process envelope
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def process(self, signal):
        #print("A:", self.__attack)
        #print("D:", self.__decay)
        #print("S:", self.__sustain)
        #print("R:", self.__release)
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

    ## Set decay parameter.
    #  @param self Object pointer
    #  @param val New value to set
    def set_decay(self, val):
        self.__decay = val

    ## Set sustain parameter.
    #  @param self Object pointer
    #  @param val New value to set
    def set_sustain(self, val):
        self.__sustain = val

    ## Set release parameter.
    #  @param self Object pointer
    #  @param val New value to set
    def set_release(self, val):
        self.__release = val
