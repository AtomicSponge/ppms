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
#  This file implements the various parts used for ppms
#
##################################################################

import math
import numpy as np
from scipy import signal
from abc import ABCMeta, abstractmethod

#  Define the A440 algorithm as a lambda expression
A440 = lambda note: math.pow(2, (note - 69) / 12) * 440

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
    def __calc_frequency(self, note): return A440(note)

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

    ##  Calculate data for oscillator.
    #  This just cleans up the other function calls a bit.
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
    def patch(self, note, signal):
        for module in self.__patches:
            try:
                signal = module.process(module, note, signal)
            except:
                pass
        return signal

    ##  Set mod wheel value
    #  @param self Object pointer
    #  @param value Mod value
    def set_mod_value(self, value):
        try:
            mod_control.set_mod_value(value)
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
class synthmod(metaclass=ABCMeta):
    ##  Flag to check if valid synth module
    IS_SYNTHMOD = True
    ##  Midi min
    MIDI_MIN = 0
    ##  Midi max
    MIDI_MAX = 127

    ##  Synth module process member.
    #  Override this to implement a custom process method.
    #  Raises not implemented error if not overridden
    #  @param self Object pointer
    #  @param note Note to be played
    #  @param signal Audio signal
    @abstractmethod
    def process(self, note, signal):
        raise NotImplementedError("Must override process method in synth module")

    ##  Use A440 to calculate the note frequency.
    #  @param self Object pointer
    #  @param note Note to calculate
    #  @return The calculated frequency
    @classmethod
    def calc_frequency(self, note): return A440(note)

##  Mod wheel control part.
class mod_control(metaclass=ABCMeta):
    __MOD_VALUE = 0

    @classmethod
    def set_mod_value(cls, value):
        cls.__MOD_VALUE = value

    @classmethod
    def get_mod_value(cls):
        return cls.__MOD_VALUE
