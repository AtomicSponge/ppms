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
from typing import Final
from scipy import signal
from abc import ABCMeta, abstractmethod

##  Algorithms for use by ppms.
#  Store some lambda expressions for use elsewhere.
class ppms_algs(object):
    #  Define the A440 algorithm
    A440 = lambda note: math.pow(2, (note - 69) / 12) * 440

##  Generates samples of different waveforms.
class oscillator(object):
    ##  Initialize and store sample rate.
    #  @param self Object pointer
    #  @param rate Sample rate
    def __init__(self, rate):
        ##  Store the sample rate
        self.__sample_rate: Final = rate

    ##  Calculate sample data.
    #  @param self Object pointer
    #  @param frame_size Amount to generate
    #  @param time_data Position in time
    #  @return Generated sample data
    def __calc_sample_data(self, frame_size, time_data):
        t = ((time_data + np.arange(frame_size)) / self.__sample_rate).reshape(-1, 1)
        return t.reshape(-1, 1)

    ##  Calculate pitch bend.
    #  @param self Object pointer
    #  @param note_freq Calculated note frequency
    #  @param pich_bend Calculated pitch bend amount
    #  @return The note frequency with pitch bend factored
    def __check_pitch_bend(self, note_freq, pitch_bend):
        if pitch_bend != 0: note_freq = note_freq * pitch_bend
        return note_freq

    ##  Calculate phase shift data for oscillator.
    #  This just cleans up the other function calls a bit.
    #  @param self Object pointer
    #  @param note Note to play
    #  @param pitch_bend Pitch bend data
    #  @param frame_size Amount of data to generate
    #  @param time_data Position in waveform
    #  @return Generated phase shift data
    def __OSCFUNC(self, note, pitch_bend, frame_size, time_data):
        return (2 * np.pi * self.__check_pitch_bend(ppms_algs.A440(note), pitch_bend)
            * self.__calc_sample_data(frame_size, time_data))

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

    ##  Set mod wheel value.
    #  @param self Object pointer
    #  @param value Mod value
    def set_mod_value(self, value):
        try:
            mod_control.set_mod_value(value)
        except:
            pass

##  Synth module base class.
class synthmod(metaclass=ABCMeta):
    ##  Flag to check if valid synth module
    IS_SYNTHMOD: Final = True
    ##  Midi min
    MIDI_MIN: Final = 0
    ##  Midi max
    MIDI_MAX: Final = 127

    ##  Synth module process member for modifying signal.
    #  Override this to implement a custom process method.
    #  Raises not implemented error if not overridden.
    #  @param self Object pointer
    #  @param note Note to be played
    #  @param signal Audio signal
    @abstractmethod
    def process(self, note, signal):
        raise NotImplementedError("Must override process method in synth module")

##  Mod wheel control part.
class mod_control(metaclass=ABCMeta):
    __MOD_VALUE = 0

    @classmethod
    def set_mod_value(cls, value):
        cls.__MOD_VALUE = value

    @classmethod
    def get_mod_value(cls):
        return cls.__MOD_VALUE
