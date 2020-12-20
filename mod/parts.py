##################################################################
#
#  Python Polyphonic MIDI Synthesizer
#
##################################################################
#
#               ~~~~~~~[]=¤ԅ(ˊᗜˋ* )੭
#
#  Filename:  parts.py
#  By:  Matthew Evans
#       https://www.wtfsystems.net/
#
#  See LICENSE.md for copyright information.
#  See README.md for usage information.
#
##################################################################

import math
import numpy as np
from scipy import signal

##  Generates samples of different waveforms.
class oscillator(object):
    ##  Initialize and generate sample data.
    #  @param self Object pointer
    #  @param rate Sample rate
    def __init__(self, rate):
        ##  Store the sample rate
        self.__frequency = rate

    ##  Use A440 to calculate the note frequency.
    #  @param self Object pointer
    #  @param note Note to calculate
    #  @return The calculated frequency
    def __calc_frequency(self, note):
        return math.pow(2, (note - 69) / 12) * 440

    ##  Calculate period.
    #  @param self Object pointer
    #  @param frame_size Amount to generate
    #  @param time_data Position in time
    #  @return Period data
    def __calc_period(self, frame_size, time_data):
        t = (time_data + np.arange(frame_size)) / self.__frequency
        return t.reshape(-1, 1)

    ##  Calculate pitch bend.
    #  @param self Object pointer
    #  @param note_freq Calculated note frequency
    #  @param pich_bend Calculated pitch bend amount
    #  @return The note frequency with pitch bend factored
    def __check_pitch_bend(self, note_freq, pitch_bend):
        if pitch_bend != 0: note_freq = note_freq * pitch_bend
        return note_freq

    ##  Return data
    #  @param self Object pointer
    #  @param note Note to play
    #  @param pitch_bend Pitch bend data
    #  @param frame_size Amount of data to generate
    #  @param time_data Position in waveform
    #  @return data
    def __OSCFUNC(self, note, pitch_bend, frame_size, time_data):
        return (2 * np.pi * self.__check_pitch_bend(self.__calc_frequency(note), pitch_bend)
            * self.__calc_period(frame_size, time_data))

    ##  Return a sawtooth wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param pitch_bend Pitch bend data
    #  @param frame_size Amount of data to generate
    #  @param time_data Position in waveform
    #  @return Sawtooth sample
    def sawtooth(self, note, pitch_bend, frame_size, time_data):
        return signal.sawtooth(self.__OSCFUNC(note, pitch_bend, frame_size, time_data))

    ##  Return a triangle wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param pitch_bend Pitch bend data
    #  @param frame_size Amount of data to generate
    #  @param time_data Position in waveform
    #  @return Triangle sample
    def triangle(self, note, pitch_bend, frame_size, time_data):
        return signal.sawtooth(self.__OSCFUNC(note, pitch_bend, frame_size, time_data), 0.5)

    ##  Return a square wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param pitch_bend Pitch bend data
    #  @param frame_size Amount of data to generate
    #  @param time_data Position in waveform
    #  @return Square sample
    def square(self, note, pitch_bend, frame_size, time_data):
        return signal.square(self.__OSCFUNC(note, pitch_bend, frame_size, time_data))

    ##  Return a sine wave sample.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param pitch_bend Pitch bend data
    #  @param frame_size Amount of data to generate
    #  @param time_data Position in waveform
    #  @return Sine sample
    def sine(self, note, pitch_bend, frame_size, time_data):
        return np.sin(self.__OSCFUNC(note, pitch_bend, frame_size, time_data))

##  Creates "patches" of "synth modules" to process the signal.
class patchboard(object):
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
    #  @return Module object if found, else raise not found exception
    def get_module(self, name):
        for module in self.__patches:
            if(name == module.__name__): return module
        raise IndexError("Module not found")

    ##  Save all module data.
    #  @param self Object pointer
    #  @return List of all module save data
    def save_data(self):
        data = []
        for module in self.__patches:
            try:
                data += module.save_data(module)
            except:
                pass
        return data

    ##  Process modules in order.
    #  @param self Object pointer
    #  @param signal Signal data to modify
    #  @return Modified signal data
    def patch(self, signal):
        for module in self.__patches:
            #print(module)
            try:
                signal = module.process(module, signal)
            except:
                pass
        return signal

    ##  Set mod wheel value
    #  @param self Object pointer
    #  @param value Mod value
    def set_mod(self, value):
        for module in self.__patches:
            try:
                module.set_mod(module, value)
            except:
                pass

    ##  Send gate signal.
    #  @param self Object pointer
    #  @param gate Gate signal
    def send_gate(self, gate):
        for module in self.__patches:
            try:
                module.gate_signal(module, gate)
            except:
                pass

    ##  Update gates for all modules
    #  @param self Object pointer
    def update_gate(self):
        for module in self.__patches:
            try:
                module.gate_update(module)
            except:
                pass

##  Synth module base class.
class synthmod(object):
    ##  Flag to check if valid synth module
    IS_SYNTHMOD = "IS_SYNTHMOD"
    ##  Midi min
    MIDI_MIN = 0
    ##  Midi max
    MIDI_MAX = 127

    ##  Gate
    gate_map = dict()

    ##
    #  @param self Object pointer
    def process(self, signal):
        pass

    ## Process gate signal.
    #  @param self Object pointer
    #  @param gate Gate signal
    def gate_signal(self, gate):
        #print(gate)
        #  If signal on, create new item in gate
        if gate['status'] == "on":
            #gate_map.update({ signal['note']: 'on' })
            print("on")
        #  If signal off, set for removal
        if gate['status'] == "off":
            #gate_map.update({ signal['note']: 'idle' })
            print("off")

    ##
    #  @param self Object pointer
    #  @return True if idle, false if not
    def gate_update(self):
        pass

    ##  Return the gate status.
    #  .
    #  @param self Object pointer
    #  @param note Note to check status on
    def gate_status(self, note):
        try:
            return gate_map.get(note)
        except:
            return "idle"

##  Mod wheel control part.
class mod_control(object):
    MOD_VALUE = 0

    def set_mod(self, value):
        self.MOD_VALUE = value
